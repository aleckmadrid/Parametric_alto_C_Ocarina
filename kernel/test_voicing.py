"""Tests for kernel/voicing.py: window sizing, rules, version hash."""
import copy
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import config  # noqa: E402
import ocarina_kernel as ok  # noqa: E402
import voicing as vo  # noqa: E402

MM = 1e-3
P = config.load_params()


class TestWindowMaths(unittest.TestCase):
    def test_area_for_conductance_round_trip(self):
        for A in (20e-6, 47e-6, 124e-6):
            for t in (3e-3, 4e-3):
                G = ok.conductance(A, t, ok.K_WINDOW)
                self.assertAlmostEqual(vo.window_area_for_conductance(G, t) / A, 1.0, delta=1e-12)

    def test_teardrop_width_round_trip(self):
        L, r = 9.65e-3, 1.0e-3
        for w in (3e-3, 7e-3, 8.8e-3, 9.6e-3):
            area = ok.teardrop_area(L, w, r)
            self.assertAlmostEqual(vo.teardrop_width_for_area(L, area, r), w, delta=1e-9)

    def test_teardrop_limit_is_a_circle(self):
        L = 9.65e-3
        self.assertAlmostEqual(vo.teardrop_max_area(L), ok.teardrop_area(L, L - 1e-12, 1e-3), delta=1e-9 * L * L)
        with self.assertRaises(ValueError):
            vo.teardrop_width_for_area(L, vo.teardrop_max_area(L) * 1.001, 1e-3)

    def test_rounded_rectangle_round_trip(self):
        L, rc = 9.65e-3, 1e-3
        for w in (6e-3, 8.5e-3, 12.9e-3):
            a = vo.rounded_rectangle_area(L, w, rc)
            self.assertAlmostEqual(vo.rounded_rectangle_width_for_area(L, a, rc), w, delta=1e-12)


class TestRules(unittest.TestCase):
    def test_a4_lands_on_pitch_at_target_volume(self):
        for v0 in (40, 65, 80, 125):
            v = vo.make_voicing(v0)
            c = ok.c_air(27)
            X = 0.9 * v.G_w()
            self.assertAlmostEqual(ok.cents(ok.freq(X, v0 * 1e-6, c), 440.0), 0.0, delta=1e-6)

    def test_defaults_are_medium_and_4mm(self):
        v = vo.make_voicing(80)
        self.assertEqual(v.rating, "medium")
        self.assertAlmostEqual(v.window_length_mm, 9.65)
        self.assertAlmostEqual(v.wall_at_window_mm, 4.0)
        self.assertAlmostEqual(v.windway_exit_height_mm, 1.20)
        self.assertAlmostEqual(v.windway_length_mm, 30.0)
        self.assertAlmostEqual(v.windway_inlet_height_mm / v.windway_exit_height_mm, 1.3)
        self.assertAlmostEqual(v.windway_width_mm, v.window_width_mm)

    def test_ratings(self):
        for name, W in (("soft", 8.89), ("medium", 9.65), ("loud", 10.41)):
            v = vo.make_voicing(80, name)
            self.assertAlmostEqual(v.window_length_mm, W)
            self.assertTrue(v.wh_ok, f"W/h {v.wh_ratio} outside 7..10 for {name}")
        with self.assertRaises(ValueError):
            vo.make_voicing(80, "extra loud")

    def test_labium_offset_only_from_the_coupon_set(self):
        for off in (-0.2, 0.0, 0.2):
            self.assertAlmostEqual(vo.make_voicing(80, labium_offset_mm=off).labium_offset_mm, off)
        with self.assertRaises(ValueError):
            vo.make_voicing(80, labium_offset_mm=0.3)

    def test_shape_switch(self):
        v_switch = vo.teardrop_to_rectangle_v0_cm3()
        self.assertAlmostEqual(v_switch, 88.6, delta=0.1)       # doc 04 says "about 85"; see notes
        self.assertEqual(vo.make_voicing(v_switch - 0.5).shape, "teardrop")
        self.assertEqual(vo.make_voicing(v_switch + 0.5).shape, "rounded_rectangle")
        # a teardrop is never wider than long
        t = vo.make_voicing(v_switch - 0.01)
        self.assertLessEqual(t.window_width_mm, t.window_length_mm)

    def test_shape_override_keeps_the_area(self):
        a = vo.make_voicing(80)
        b = vo.make_voicing(80, shape="rounded_rectangle")       # stub V-b
        self.assertEqual(b.shape, "rounded_rectangle")
        self.assertAlmostEqual(a.window_area_mm2, b.window_area_mm2, delta=1e-9)
        self.assertNotEqual(a.version_hash, b.version_hash)
        with self.assertRaises(ValueError):
            vo.make_voicing(125, shape="teardrop")

    def test_fixed_area_mode_reproduces_a_voicing(self):
        a = vo.make_voicing(80)
        b = vo.make_voicing(window_area_mm2=a.window_area_mm2)
        self.assertEqual(a.version_hash, b.version_hash)

    def test_window_grows_with_volume(self):
        areas = [vo.make_voicing(v).window_area_mm2 for v in (65, 80, 95, 110, 125)]
        self.assertEqual(areas, sorted(areas))


class TestHash(unittest.TestCase):
    def test_stable_for_same_inputs(self):
        self.assertEqual(vo.make_voicing(80).version_hash, vo.make_voicing(80).version_hash)
        self.assertEqual(len(vo.make_voicing(80).version_hash), 12)
        v = vo.make_voicing(80)
        self.assertEqual(vo.voicing_hash_of(v), v.version_hash)

    def test_changes_when_any_input_changes(self):
        base = vo.make_voicing(80).version_hash
        variants = {
            "v0": vo.make_voicing(81),
            "rating": vo.make_voicing(80, "loud"),
            "wall": vo.make_voicing(80, wall_at_window_mm=3.0),
            "labium +": vo.make_voicing(80, labium_offset_mm=0.2),
            "labium -": vo.make_voicing(80, labium_offset_mm=-0.2),
            "eta_w": vo.make_voicing(80, eta_w=0.8),
            "shape": vo.make_voicing(80, shape="rounded_rectangle"),
        }
        seen = {base}
        for name, v in variants.items():
            self.assertNotIn(v.version_hash, seen, name)
            seen.add(v.version_hash)

    def test_changes_when_a_rule_constant_changes(self):
        P2 = copy.deepcopy(P)
        P2["voicing_rules"]["windway_length_mm"] = 31.0
        self.assertNotEqual(vo.make_voicing(80, params=P2).version_hash, vo.make_voicing(80).version_hash)
        P3 = copy.deepcopy(P)
        P3["voicing_rules"]["teardrop_tip_radius_mm"] = 1.2
        self.assertNotEqual(vo.make_voicing(80, params=P3).version_hash, vo.make_voicing(80).version_hash)

    def test_negative_zero_does_not_change_the_hash(self):
        v = vo.make_voicing(80)
        d = vo.asdict(v) if hasattr(vo, "asdict") else v.to_dict()
        d["labium_offset_mm"] = -0.0
        h1 = vo.voicing_hash(d)
        d["labium_offset_mm"] = 0.0
        self.assertEqual(h1, vo.voicing_hash(d))

    def test_below_micrometre_noise_is_ignored(self):
        d = vo.make_voicing(80).to_dict()
        h1 = vo.voicing_hash(d)
        d["window_width_mm"] += 1e-7
        self.assertEqual(h1, vo.voicing_hash(d))

    def test_equal_window_equal_hash_for_stub_and_body(self):
        # Stage 1 stub V-a carries the 80 cm3 window: same numbers, same hash, whatever the chamber.
        body = vo.make_voicing(80)
        self.assertEqual(vo.make_voicing(80, shape="teardrop").version_hash, body.version_hash)
        self.assertEqual(vo.make_voicing(window_area_mm2=body.window_area_mm2, rating="medium").version_hash,
                         body.version_hash)
        # V-b: same area, other shape: different hash
        self.assertNotEqual(vo.make_voicing(80, shape="rounded_rectangle").version_hash, body.version_hash)


if __name__ == "__main__":
    unittest.main()
