"""Tests for kernel/voicing.py: window sizing, rules, version hash."""
import ast
import contextlib
import copy
import io
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import config  # noqa: E402
import ocarina_kernel as ok  # noqa: E402
import voicing as vo  # noqa: E402
import sizing  # noqa: E402

MM = 1e-3
P = config.load_params()
ROOT = pathlib.Path(__file__).resolve().parent.parent


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
        self.assertAlmostEqual(vo.teardrop_circle_limit_area(L), ok.teardrop_area(L, L - 1e-12, 1e-3), delta=1e-9 * L * L)
        self.assertAlmostEqual(vo.teardrop_area(L, L, 1e-3), math.pi * L * L / 4, delta=1e-15)
        # C2b: above the circle the family goes on (wider than long). It ends only at the widest teardrop.
        w = vo.teardrop_width_for_area(L, vo.teardrop_circle_limit_area(L) * 1.001, 1e-3)
        self.assertGreater(w, L)
        self.assertLess(w, L * 1.01)
        w_max = vo.teardrop_max_width(L, 1e-3)
        with self.assertRaises(ValueError):
            vo.teardrop_width_for_area(L, vo.teardrop_area(L, w_max, 1e-3) * 1.001, 1e-3)
        with self.assertRaises(ValueError):
            vo.teardrop_width_for_area(L, vo.teardrop_min_area(L, 1e-3) * 0.99, 1e-3)

    def test_wide_teardrop_round_trip_and_units(self):
        L, r = 9.65e-3, 1.0e-3
        for w in (9.7e-3, 11.1e-3, 14.7e-3, 18.6e-3, 24e-3):
            area = vo.teardrop_area(L, w, r)
            self.assertAlmostEqual(vo.teardrop_width_for_area(L, area, r), w, delta=1e-9)
            # the maths is unit-free: the same shape in millimetres has 1e6 times the area
            self.assertAlmostEqual(vo.teardrop_area(L * 1e3, w * 1e3, r * 1e3) / (area * 1e6), 1.0, delta=1e-9)

    def test_family_is_continuous_and_grows_at_the_circle(self):
        L, r = 9.65, 1.0
        below, at, above = (vo.teardrop_area(L, L * f, r) for f in (1 - 1e-6, 1.0, 1 + 1e-6))
        self.assertLess(below, at)
        self.assertLess(at, above)
        self.assertLess(above - below, 5e-4)             # 2e-5 mm of width: no step in the area
        # area grows with width over the whole family, in steps of 0.05 mm
        w_max = vo.teardrop_max_width(L, r)
        prev = 0.0
        w = 2.0 * r
        while w <= w_max:
            a = vo.teardrop_area(L, w, r)
            self.assertGreater(a, prev, f"area does not grow at width {w:.2f}")
            prev = a
            w += 0.05

    def test_wide_teardrop_is_never_sharper_than_the_tip(self):
        L, r = 9.65, 1.0
        w_max = vo.teardrop_max_width(L, r)
        b = vo.teardrop_broad_half_length(L, w_max)
        self.assertAlmostEqual(b * b / (w_max / 2), r, delta=1e-9)
        for w in (11.1, 14.7, 18.6):                     # the ladder steps above the circle
            b = vo.teardrop_broad_half_length(L, w)
            self.assertGreater(b * b / (w / 2), r)
            self.assertLess(2 * b, L)                    # the broad end stops short of the labium: the tip is the narrow end

    def test_outline_matches_the_numbers(self):
        for v0 in (65, 80, 95, 110, 125):
            v = vo.make_voicing(v0)
            pts = v.outline_mm()
            self.assertAlmostEqual(vo.polygon_area(pts) / v.window_area_mm2, 1.0, delta=3e-4, msg=str(v0))
            self.assertLess(vo.polygon_area(pts), v.window_area_mm2)             # inscribed polygon
            xs, ys = [q[0] for q in pts], [q[1] for q in pts]
            self.assertAlmostEqual(min(xs), 0.0, delta=1e-9)                       # windway exit
            self.assertAlmostEqual(max(xs), v.window_length_mm, delta=1e-9)        # labium
            self.assertAlmostEqual(max(ys), v.window_width_mm / 2, delta=1e-9)
            self.assertAlmostEqual(min(ys), -v.window_width_mm / 2, delta=1e-9)
            # broad end at the windway: the widest point lies in the windway half of the window
            x_widest = xs[ys.index(max(ys))]
            self.assertLess(x_widest, v.window_length_mm / 2 + 1e-9, str(v0))
            self.assertAlmostEqual(x_widest, v.broad_end_length_mm / 2, delta=1e-9)
            # narrow end at the labium: near x = length the outline is the tip circle
            near_tip = [q for q in pts if abs(q[2]) < 0.2]
            self.assertTrue(near_tip)
            for x, y, _ in near_tip:
                self.assertAlmostEqual(math.hypot(x - (v.window_length_mm - v.tip_radius_mm), y), v.tip_radius_mm, delta=1e-9)
            # convex and counter-clockwise
            n = len(pts)
            for i in range(n):
                (x0, y0, _), (x1, y1, _), (x2, y2, _) = pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
                self.assertGreater((x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1), -1e-9)

    def test_rectangle_outline(self):
        v = vo.make_voicing(80, shape="rounded_rectangle")
        pts = v.outline_mm()
        self.assertAlmostEqual(vo.polygon_area(pts) / v.window_area_mm2, 1.0, delta=3e-4)
        self.assertAlmostEqual(max(q[0] for q in pts), v.window_length_mm, delta=1e-9)
        self.assertAlmostEqual(max(q[1] for q in pts), v.window_width_mm / 2, delta=1e-9)

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
        for off in (-0.35, -0.2, 0.0):
            self.assertAlmostEqual(vo.make_voicing(80, labium_offset_mm=off).labium_offset_mm, off)
        for bad in (0.2, 0.3, -0.4, -0.6):                       # never positive (Heuer: "below the halfway mark")
            with self.assertRaises(ValueError):
                vo.make_voicing(80, labium_offset_mm=bad)

    def test_labium_default_is_below_the_jet_centre(self):
        # Owner decision 2026-11-17: default -0.2 mm, resolved from [voicing_rules] wherever None is passed.
        self.assertAlmostEqual(vo.make_voicing(80).labium_offset_mm, -0.2)
        self.assertAlmostEqual(sizing.size_body(80.0).voicing.labium_offset_mm, -0.2)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sizing.main(["--v0", "80", "--holes"])
        self.assertIn("offset -0.2 mm", buf.getvalue())
        P2 = copy.deepcopy(P)
        P2["voicing_rules"]["default_labium_offset_mm"] = 0.0
        self.assertAlmostEqual(vo.make_voicing(80, params=P2).labium_offset_mm, 0.0)

    def _windway_centre_z(self):
        src = (ROOT / "ocarina_addon" / "voicing_geo.py").read_text(encoding="utf-8")
        fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "windway_centre_z")
        ns = {}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), "voicing_geo.py", "exec"), ns)
        return ns["windway_centre_z"]

    def test_every_labium_option_keeps_the_floor_clear(self):
        # Past the exit the windway floor is at windway_centre_z - h/2. It must stay at least 0.05 mm below the
        # pocket ceiling (z = 0, the inner plane), the add-on's own clearance; at -0.4 mm it would be coplanar.
        centre = self._windway_centre_z()
        for off in P["voicing_rules"]["labium_offset_options_mm"]:
            v = vo.make_voicing(80, labium_offset_mm=off)
            floor = centre(v) - 0.5 * v.windway_exit_height_mm
            self.assertLessEqual(floor, -0.05 + 1e-9, f"offset {off}: floor at {floor:+.3f} mm")
            self.assertGreater(0.5 * v.labium_edge_thickness_mm, floor)      # the lip stays visible above the floor

    def test_labium_sign_matches_the_addon_geometry(self):
        # The add-on places the windway with voicing_geo.windway_centre_z (z outward, the edge spans z = 0 .. e at
        # the inner plane). Heuer's "lip below centre" means the edge mid-height lies on the chamber side (-z) of the
        # jet centre. voicing_geo imports bpy through meshutil, so the one-line function is read from the source.
        v = vo.make_voicing(80)
        edge_mid = 0.5 * v.labium_edge_thickness_mm
        jet_centre = self._windway_centre_z()(v)
        self.assertGreater(jet_centre, edge_mid)                  # edge below (inward of) the jet centre
        self.assertAlmostEqual(edge_mid - jet_centre, v.labium_offset_mm, delta=1e-12)
        floor = jet_centre - 0.5 * v.windway_exit_height_mm
        self.assertLess(floor, 0.0 + 1e-12)                       # the edge (z = 0 .. e) stays above the floor
        self.assertGreater(edge_mid, floor)

    def test_teardrop_at_every_volume(self):
        # C2b, owner decision 1: no automatic rounded rectangle at any volume.
        for v0 in (40, 65, 80, 88, 89, 95, 110, 125, 140):
            v = vo.make_voicing(v0)
            self.assertEqual(v.shape, "teardrop", v0)
            self.assertAlmostEqual(v.window_length_mm, 9.65, places=9)         # the window length never changes
            self.assertAlmostEqual(v.tip_radius_mm, 1.0)
            self.assertAlmostEqual(v.windway_width_mm, v.window_width_mm)      # windway width = broad end
            self.assertAlmostEqual(v.wh_ratio, 9.65 / 1.2)
        for rating, W in (("soft", 8.89), ("loud", 10.41)):
            for v0 in (65, 125):
                v = vo.make_voicing(v0, rating)
                self.assertEqual(v.shape, "teardrop")
                self.assertAlmostEqual(v.window_length_mm, W)

    def test_circle_limit_volume(self):
        v_limit = vo.teardrop_circle_limit_v0_cm3()
        self.assertAlmostEqual(v_limit, 88.6, delta=0.1)       # doc 04 said "about 85"; see the notes
        below, above = vo.make_voicing(v_limit - 0.5), vo.make_voicing(v_limit + 0.5)
        self.assertLessEqual(below.window_width_mm, below.window_length_mm)
        self.assertFalse(below.is_wide_teardrop)
        self.assertGreater(above.window_width_mm, above.window_length_mm)
        self.assertTrue(above.is_wide_teardrop)
        self.assertLess(above.window_width_mm - below.window_width_mm, 0.25)   # no step at the limit
        self.assertAlmostEqual(below.broad_end_length_mm, below.window_width_mm)
        self.assertLess(above.broad_end_length_mm, above.window_length_mm)

    def test_old_teardrops_are_unchanged(self):
        # The 65 and 80 cm3 windows (stubs V-d and V-a) keep their pre-C2b numbers and hashes at the old
        # labium offset (0.0): the hash function and the window rule have not drifted.
        for v0, width, hash_before_c2b in ((65, 6.9594, "6aa0038008cc"), (80, 8.8060, "d1b6418b1844")):
            v = vo.make_voicing(v0, labium_offset_mm=0.0)
            self.assertAlmostEqual(v.window_width_mm, width, delta=5e-5)
            self.assertAlmostEqual(ok.teardrop_area(9.65, v.window_width_mm, 1.0), v.window_area_mm2, delta=1e-9)
            self.assertEqual(v.version_hash, hash_before_c2b)
        # With the -0.2 mm default (2026-11-17) only the offset changes: same window, new pinned hashes.
        for v0, hash_now in ((65, "2a71c31c2505"), (80, "617b869f0b10"), (95, "7b411d5079d7")):
            v, v_old = vo.make_voicing(v0), vo.make_voicing(v0, labium_offset_mm=0.0)
            self.assertEqual(v.version_hash, hash_now)
            self.assertAlmostEqual(v.window_width_mm, v_old.window_width_mm, delta=1e-12)
            self.assertAlmostEqual(v.window_area_mm2, v_old.window_area_mm2, delta=1e-12)

    def test_width_and_area_grow_together_with_volume(self):
        prev = None
        for v0 in [60 + 2.5 * i for i in range(33)]:            # 60 .. 140 cm3, across the circle limit
            v = vo.make_voicing(v0)
            if prev is not None:
                self.assertGreater(v.window_area_mm2, prev.window_area_mm2, v0)
                self.assertGreater(v.window_width_mm, prev.window_width_mm, v0)
                self.assertGreater(v.windway_width_mm, prev.windway_width_mm, v0)   # the windway never steps down
                self.assertLess(v.window_width_mm - prev.window_width_mm, 0.9, v0)  # and never jumps
            prev = v

    def test_ladder_sizes(self):
        # broad end = windway width at each ladder step (the doc 04 table after C2b)
        for v0, width, area in ((65, 7.0, 46.5), (80, 8.8, 62.8), (95, 11.1, 81.2), (110, 14.7, 101.4), (125, 18.6, 123.5)):
            v = vo.make_voicing(v0)
            self.assertAlmostEqual(v.window_width_mm, width, delta=0.05, msg=str(v0))
            self.assertAlmostEqual(v.window_area_mm2, area, delta=0.06, msg=str(v0))

    def test_family_has_an_upper_end(self):
        v_max = vo.teardrop_max_v0_cm3()
        self.assertGreater(v_max, 125.0)                        # the whole ladder is inside the family
        self.assertEqual(vo.make_voicing(v_max - 0.5).shape, "teardrop")
        with self.assertRaises(ValueError):
            vo.make_voicing(v_max + 1.0)

    def test_shape_override_keeps_the_area(self):
        a = vo.make_voicing(80)
        b = vo.make_voicing(80, shape="rounded_rectangle")       # stub V-b: forced, 63 mm2
        self.assertEqual(b.shape, "rounded_rectangle")
        self.assertAlmostEqual(a.window_area_mm2, b.window_area_mm2, delta=1e-9)
        self.assertAlmostEqual(b.window_area_mm2, 63.0, delta=0.5)
        self.assertAlmostEqual(b.corner_radius_mm, 1.0)
        self.assertEqual(b.tip_radius_mm, 0.0)
        self.assertAlmostEqual(b.windway_width_mm, b.window_width_mm)
        self.assertNotEqual(a.version_hash, b.version_hash)
        # the forced rectangle also works above the circle limit, and "teardrop" is the rule itself
        self.assertEqual(vo.make_voicing(125, shape="rounded_rectangle").shape, "rounded_rectangle")
        self.assertEqual(vo.make_voicing(125, shape="teardrop").version_hash, vo.make_voicing(125).version_hash)
        # the 125 cm3 teardrop (top of the old ladder, old stub V-c), 124 mm2: still inside the family
        self.assertAlmostEqual(vo.make_voicing(125).window_area_mm2, 124.0, delta=1.0)

    def test_fixed_area_mode_reproduces_a_voicing(self):
        a = vo.make_voicing(80)
        b = vo.make_voicing(window_area_mm2=a.window_area_mm2)
        self.assertEqual(a.version_hash, b.version_hash)

    def test_window_grows_with_volume(self):
        areas = [vo.make_voicing(v).window_area_mm2 for v in (65, 80, 95, 110, 125)]
        self.assertEqual(areas, sorted(areas))
        widths = [vo.make_voicing(v).window_width_mm for v in (65, 80, 95, 110, 125)]
        self.assertEqual(widths, sorted(widths))


class TestHash(unittest.TestCase):
    def test_stable_for_same_inputs(self):
        for v0 in (65, 80, 95, 110, 125):
            self.assertEqual(vo.make_voicing(v0).version_hash, vo.make_voicing(float(v0)).version_hash)
        self.assertEqual(len({vo.make_voicing(v0).version_hash for v0 in (65, 80, 95, 110, 125)}), 5)
        self.assertEqual(len(vo.make_voicing(80).version_hash), 12)
        v = vo.make_voicing(80)
        self.assertEqual(vo.voicing_hash_of(v), v.version_hash)

    def test_changes_when_any_input_changes(self):
        for v0 in (80, 125):                      # an old teardrop and a teardrop wider than long
            base = vo.make_voicing(v0).version_hash
            variants = {
                "v0": vo.make_voicing(v0 + 1),
                "rating": vo.make_voicing(v0, "loud"),
                "rating soft": vo.make_voicing(v0, "soft"),
                "wall": vo.make_voicing(v0, wall_at_window_mm=3.0),
                "labium 0": vo.make_voicing(v0, labium_offset_mm=0.0),
                "labium -0.35": vo.make_voicing(v0, labium_offset_mm=-0.35),
                "eta_w": vo.make_voicing(v0, eta_w=0.8),
                "shape": vo.make_voicing(v0, shape="rounded_rectangle"),
            }
            seen = {base}
            for name, v in variants.items():
                self.assertNotIn(v.version_hash, seen, f"{name} at {v0}")
                seen.add(v.version_hash)

    def test_changes_when_a_rule_constant_changes(self):
        rules = {"windway_length_mm": 31.0, "teardrop_tip_radius_mm": 1.2, "windway_exit_height_mm": 1.25,
                 "windway_taper_ratio": 1.4, "labium_ramp_angle_deg": 22.0, "labium_edge_thickness_mm": 0.5,
                 "keepout_inside_mm": 12.0, "keepout_outside_flare_deg": 40.0, "rule_version": 2}
        for v0 in (80, 125):
            base = vo.make_voicing(v0).version_hash
            for key, value in rules.items():
                P2 = copy.deepcopy(P)
                P2["voicing_rules"][key] = value
                self.assertNotEqual(vo.make_voicing(v0, params=P2).version_hash, base, f"{key} at {v0}")
        P2 = copy.deepcopy(P)
        P2["voicing_rules"]["rect_corner_radius_mm"] = 1.5
        self.assertNotEqual(vo.make_voicing(80, shape="rounded_rectangle", params=P2).version_hash,
                            vo.make_voicing(80, shape="rounded_rectangle").version_hash)

    def test_wide_teardrop_rule_is_in_the_hash_only_above_the_circle(self):
        P2 = copy.deepcopy(P)
        P2["voicing_rules"]["teardrop_wide_exponent"] = 0.5
        self.assertEqual(vo.make_voicing(80, params=P2).version_hash, vo.make_voicing(80).version_hash)
        self.assertNotEqual(vo.make_voicing(125, params=P2).version_hash, vo.make_voicing(125).version_hash)
        # the hash of a record always equals the hash of its own numbers
        for v0 in (65, 80, 95, 110, 125):
            v = vo.make_voicing(v0)
            self.assertEqual(vo.voicing_hash_of(v), v.version_hash)
            self.assertEqual(vo.voicing_hash(v.to_dict()), v.version_hash)
        # a wide teardrop with a changed broad-end length is a different voicing
        d = vo.make_voicing(125).to_dict()
        d["broad_end_length_mm"] += 0.01
        self.assertNotEqual(vo.voicing_hash(d), vo.make_voicing(125).version_hash)

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
