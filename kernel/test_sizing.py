"""Tests for kernel/checks.py, holes.py and sizing.py, including the doc 04 table."""
import contextlib
import io
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import checks  # noqa: E402
import config  # noqa: E402
import holes as hl  # noqa: E402
import ocarina_kernel as ok  # noqa: E402
import sizing  # noqa: E402

MM = 1e-3
P = config.load_params()

# docs/04-testing-phase.md, "Generated sizes at each step" (holes at k_hole 1.0, plain 4 mm wall)
# V0 cm3: (shape, window width mm, windway width mm, sub_R, L_index, E6 thumb, P0 length mm, area/V0^(2/3))
DOC04 = {
    65.0: ("teardrop", 7.0, 7.0, 2.2, 10.3, 12.2, 74, 0.029),
    80.0: ("teardrop", 8.8, 8.8, 2.6, 12.1, 14.4, 79, 0.034),
    95.0: ("rounded_rectangle", 8.5, 8.5, 2.8, 13.9, 16.5, 84, 0.039),
    110.0: ("rounded_rectangle", 10.6, 10.6, 3.1, 15.6, 18.6, 88, 0.044),
    125.0: ("rounded_rectangle", 12.9, 12.9, 3.4, 17.3, 20.6, 92, 0.049),
}
DOC04_AREA = {65.0: 47, 80.0: 63, 95.0: 81, 110.0: 101, 125.0: 124}


class TestDoc04Table(unittest.TestCase):
    def test_every_listed_size_within_0p05_mm(self):
        for v0, (shape, w, wway, sub_r, l_idx, thumb, p0, ratio) in DOC04.items():
            b = sizing.size_body(v0)
            v = b.voicing
            self.assertEqual(v.shape, shape, v0)
            self.assertAlmostEqual(v.window_length_mm, 9.65, places=6)
            self.assertAlmostEqual(v.window_width_mm, w, delta=0.05, msg=f"window width at {v0}")
            self.assertAlmostEqual(v.windway_width_mm, wway, delta=0.05, msg=f"windway width at {v0}")
            self.assertAlmostEqual(v.windway_exit_height_mm, 1.2)
            self.assertAlmostEqual(v.wh_ratio, 8.0, delta=0.05)
            nom = {h.name: h for h in b.holes.solutions["nominal"]}
            self.assertAlmostEqual(nom["sub2"].d_plain_mm, sub_r, delta=0.05, msg=f"sub_R at {v0}")
            self.assertAlmostEqual(nom["L_index"].d_plain_mm, l_idx, delta=0.05, msg=f"L_index at {v0}")
            self.assertAlmostEqual(nom["L_thumb"].d_plain_mm, thumb, delta=0.05, msg=f"E6 thumb at {v0}")
            self.assertAlmostEqual(b.p0_length_mm, p0, delta=0.5, msg=f"P0 length at {v0}")
            self.assertAlmostEqual(b.window_area_over_v0_23, ratio, delta=0.0006)
            # doc 04 rounds the area from the rounded width; the exact area differs by under 1 mm2
            self.assertAlmostEqual(v.window_area_mm2, DOC04_AREA[v0], delta=1.0)

    def test_k_split_numbers_quoted_in_doc04(self):
        # At 80 cm3: moving k_hole 0.8 -> 1.0 grows holes by +0.1 mm (subholes) to +1.7 mm (E6 thumb);
        # holes sized at 0.8 that behave like 1.0 play -16 cents at B4 down to -109 cents at F6.
        b = sizing.size_body(80.0)
        c, V0, X = b.c_m_s, 80e-6, b.X_w_mm * MM
        specs = hl.hole_specs_from_params(P)
        plain = [s.wall_m for s in specs]
        d08, _ = hl.solve_scale(b.f_targets_hz, X, V0, plain, 0.8, c)
        d10, _ = hl.solve_scale(b.f_targets_hz, X, V0, plain, 1.0, c)
        growth = [(a - b_) / MM for a, b_ in zip(d10, d08)]
        self.assertAlmostEqual(growth[1], 0.1, delta=0.05)          # sub_R
        self.assertAlmostEqual(max(growth), 1.7, delta=0.05)        # E6 thumb
        pred = hl.predict_scale(X, V0, d08, plain, 1.0, c)
        err = [ok.cents(p, t) for p, t in zip(pred, b.f_targets_hz)]
        self.assertAlmostEqual(err[1], -16.0, delta=1.0)
        self.assertAlmostEqual(err[-1], -109.0, delta=1.0)

    def test_cli_prints_the_table(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(sizing.main(["--table"]), 0)
        out = buf.getvalue()
        for text in ("| 65 cm³ |", "| 125 cm³ |", "Rounded rectangle 9.65 × 12.9 mm", "Teardrop 9.65 × 8.8 mm", "| 92 mm |"):
            self.assertIn(text, out)

    def test_cli_other_volume_and_rating(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sizing.main(["--v0", "100", "--rating", "loud", "--holes"])
        out = buf.getvalue()
        self.assertIn("V0 = 100.0 cm³, loud window", out)
        self.assertIn("L_thumb", out)


class TestHoleSolver(unittest.TestCase):
    def setUp(self):
        self.b = sizing.size_body(80.0)
        self.c = self.b.c_m_s
        self.X = self.b.X_w_mm * MM
        self.specs = hl.hole_specs_from_params(P)
        self.f = self.b.f_targets_hz

    def test_matches_the_old_kernel_solver_without_tubes(self):
        holes = [ok.Hole(s.name, s.wall_m) for s in self.specs]
        des = ok.solve_linear_fingering(self.f, self.X, holes, k=0.8, c=self.c)
        ds, _ = hl.solve_scale(self.f, self.X, des.V0, [s.wall_m for s in self.specs], 0.8, self.c)
        for h, d in zip(des.holes, ds):
            self.assertAlmostEqual(h.d, d, delta=1e-12)

    def test_round_trip_with_tubes_and_position_factors(self):
        tubes = [3e-3, 0, 0, 0, 1.5e-3, 0, 0, 0, 0, 0, 0, 0]
        ch = [s.wall_m + t for s, t in zip(self.specs, tubes)]
        psi = [1.0, 0.9, 0.85, 0.9, 1.1, 1.0, 1.2, 1.0, 0.8, 1.0, 1.05, 0.95]
        for k in (0.8, 1.0, 1.13):
            ds, _ = hl.solve_scale(self.f, self.X, 80e-6, ch, k, self.c, psi)
            pred = hl.predict_scale(self.X, 80e-6, ds, ch, k, self.c, psi)
            for p, t in zip(pred, self.f):
                self.assertLess(abs(ok.cents(p, t)), 1e-6)

    def test_tubes_lift_print_diameters_to_the_floor(self):
        for v0 in (65, 80, 95, 110, 125):
            b = sizing.size_body(float(v0))
            for h in b.holes.solutions["print"]:
                self.assertGreaterEqual(h.d_mm, 3.0 - 1e-9, f"{h.name} at {v0}")
                self.assertFalse(h.below_floor)
            for t in b.holes.tubes_mm:
                self.assertAlmostEqual(t / 0.5, round(t / 0.5), places=9)
        small = sizing.size_body(65.0)
        self.assertGreater(small.holes.tubes_mm[1], 0.0)             # sub_R needs a tube at 65 cm3
        self.assertGreater(small.holes.tube_wall_displacement_cm3, 0.0)
        self.assertLess(small.holes.tube_wall_displacement_cm3, 0.2)  # doc 03: well under 1 cm3

    def test_holes_above_the_floor_get_no_tube(self):
        b = sizing.size_body(95.0)
        wall = {h.name: h for h in b.holes.solutions["print"]}
        for name in ("R_pinky", "R_ring", "R_index", "L_pinky", "L_ring", "L_middle", "L_index", "L_thumb", "R_thumb"):
            self.assertEqual(wall[name].tube_mm, 0.0, name)

    def test_same_chimneys_for_both_k(self):
        b = sizing.size_body(65.0)
        a, n = b.holes.solutions["print"], b.holes.solutions["nominal"]
        for p, q in zip(a, n):
            self.assertEqual(p.chimney_mm, q.chimney_mm)
            self.assertGreaterEqual(q.d_mm, p.d_mm)                  # larger k needs a larger bore

    def test_fixed_tubes_are_kept(self):
        b = sizing.size_body(80.0, tubes_mm=[0.0] * 12)
        self.assertEqual(b.holes.tubes_mm, [0.0] * 12)
        self.assertTrue(b.holes.solutions["print"][1].below_floor)   # sub_R without a tube is under the floor
        self.assertFalse(b.all_ok)

    def test_tube_cap_is_reported(self):
        tubes, capped = hl.plan_tubes(self.f, self.X, 80e-6, self.specs, 0.8, self.c, tube_max_m=1e-3)
        self.assertIn("sub2", capped)

    def test_unreachable_scale_raises(self):
        with self.assertRaises(ValueError):
            hl.solve_scale(self.f, self.X, 10e-6, [4e-3] * 12, 1.0, self.c)

    def test_tube_wall_displacement_formula(self):
        d, L, w = 3e-3, 5e-3, 1.2e-3
        expected = math.pi / 4 * ((d + 2 * w) ** 2 - d ** 2) * L
        self.assertAlmostEqual(hl.tube_wall_displacement_m3(d, L, w), expected, delta=1e-18)


class TestFixedVoicingMode(unittest.TestCase):
    def test_retarget_puts_a4_on_pitch(self):
        v = sizing.size_body(80.0).voicing
        b = sizing.size_body(voicing=v, eta_w=0.80)
        self.assertAlmostEqual(b.a4_error_cents, 0.0, delta=1e-9)
        self.assertLess(b.v0_cm3, 80.0)                               # lower eta_w needs less air
        self.assertEqual(b.voicing.version_hash, v.version_hash)

    def test_fixed_volume_reports_the_a4_error(self):
        v = sizing.size_body(80.0).voicing
        b = sizing.size_body(80.0, voicing=v, eta_w=0.80)
        self.assertLess(b.a4_error_cents, -50.0)                      # too much air for a weaker window: flat
        self.assertAlmostEqual(b.v0_cm3, 80.0)

    def test_calibration_scalars_change_mesh_volume_only(self):
        a = sizing.size_body(80.0)
        b = sizing.size_body(80.0, volume_factor=0.98)
        self.assertAlmostEqual(b.cavity_volume_for_mesh_cm3 - a.holes.tube_wall_displacement_cm3, 80.0 / 0.98, delta=1e-9)
        for p, q in zip(a.holes.solutions["print"], b.holes.solutions["print"]):
            self.assertEqual(p.d_mm, q.d_mm)

    def test_custom_k_set(self):
        b = sizing.size_body(80.0, ks={"fitted": 1.07})
        self.assertEqual(list(b.holes.solutions), ["fitted"])
        self.assertEqual(b.holes.floor_key, "fitted")


class TestChecks(unittest.TestCase):
    def test_range_ratio_identity_is_9p08(self):
        self.assertAlmostEqual(checks.range_ratio_identity(ok.midi_f(89), ok.midi_f(69)), 9.08, delta=0.005)

    def test_range_ratio_with_chimney_volume_is_8p9ish(self):
        b = sizing.size_body(80.0)
        self.assertAlmostEqual(b.range_ratio, 8.8, delta=0.2)
        self.assertEqual(checks.range_ratio_check(11.0, 1.0, 10.0).status, "fail")
        self.assertTrue(checks.range_ratio_check(9.0, 1.0, 10.0).ok)

    def test_cavity_mode_three_states(self):
        c, ftop = ok.c_air(27), ok.midi_f(89)
        self.assertEqual(checks.cavity_mode_check(79e-3, ftop, c).status, "pass")
        self.assertEqual(checks.cavity_mode_check(111e-3, ftop, c).status, "needs_fem")
        self.assertEqual(checks.cavity_mode_check(146e-3, ftop, c).status, "fail")
        # P2 tailed gourd at 80 cm3 (126 mm) sits right at the limit (doc 04): ratio 0.99, "fail" by the TOML margin
        r = checks.cavity_mode_check(126e-3, ftop, c)
        self.assertAlmostEqual(r.value, 0.99, delta=0.01)
        self.assertEqual(r.status, "fail")
        self.assertTrue(r.blocking)

    def test_cavity_mode_matches_doc03(self):
        # c/(2L) = F6 at 124.3 mm, 1.3 F6 at 95.6 mm
        c, ftop = ok.c_air(27), ok.midi_f(89)
        self.assertAlmostEqual(checks.cavity_mode_ratio(124.3e-3, ftop, c), 1.0, delta=0.002)
        self.assertAlmostEqual(checks.cavity_mode_ratio(95.6e-3, ftop, c), 1.3, delta=0.003)

    def test_p0_egg_lengths(self):
        for v0, L in ((65, 74), (80, 79), (95, 84), (110, 88), (125, 92)):
            self.assertAlmostEqual(checks.ellipsoid_length_m(v0 * 1e-6) / MM, L, delta=0.5)

    def test_pad_limits_flag_the_big_holes(self):
        b = sizing.size_body(65.0)
        flags = {h.name: h.above_pad_limit for h in b.holes.solutions["nominal"]}
        self.assertTrue(flags["L_index"])      # 10.3 mm > 10 mm
        self.assertTrue(flags["L_thumb"])      # 12.2 mm > 12 mm
        self.assertFalse(b.all_ok)

    def test_hole_limit_check_states(self):
        self.assertTrue(checks.hole_limit_check("x", 5e-3, 3e-3, 10e-3).ok)
        self.assertTrue(checks.hole_limit_check("x", 2e-3, 3e-3, 10e-3).blocking)
        self.assertTrue(checks.hole_limit_check("x", 11e-3, 3e-3, 10e-3).blocking)


class TestParams(unittest.TestCase):
    def test_k_split_in_the_toml(self):
        a = P["acoustics"]
        self.assertNotIn("k_end", a)
        self.assertEqual(a["k_window"], 0.80)
        self.assertEqual(a["k_hole_prior"], 1.00)
        self.assertEqual(a["k_hole_first_print"], 0.80)
        self.assertEqual(ok.K_WINDOW, a["k_window"])
        self.assertEqual(ok.K_HOLE_PRIOR, a["k_hole_prior"])

    def test_temperature_rule(self):
        self.assertAlmostEqual(ok.internal_air_temp_c(22.0), 27.0)
        self.assertAlmostEqual(ok.internal_air_temp_c(32.0), 27.0 + 3.1)


if __name__ == "__main__":
    unittest.main()
