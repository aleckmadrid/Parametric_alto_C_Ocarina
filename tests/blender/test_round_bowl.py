"""Headless Blender tests of the round bowl and its options (an OPTION since 2026-11-26, not the rule).

    blender -b --factory-startup --python tests/run_blender_tests.py -- TestRoundBowl TestOptionsOff      (about 2 minutes)
    blender -b --factory-startup --python tests/run_blender_tests.py -- TestCalibratedBowl                 (the bowl from fitted constants)
    blender -b --factory-startup --python tests/run_blender_tests.py -- TestThinFloorPlate TestBowlOverhang (the local checks)

TestRoundBowl builds the variant P4-bowl (ocarina_addon/presets/variants.toml: the low-voicing experiment's s3-yH7) at
80 cm3 as it is, with the left thumb hole moved 4 mm toward the bulb by the variant itself (s3-zB4, the owner's pick of
2026-11-26), and measures it on the STL read back from disk,
beside its bare reference: the same body with the rule's ellipse cut (the experiment's s3-zR4), which tells where the
bowl changed the outside. The rule's own plastic over the windway's exit corners, under the flare of the ellipse cut, is
thinner than 1.32 mm (0.8 mm on the bare reference, 0.35 mm on the plain P4-80 of rule version 3); there the test asks
that the bowl takes nothing more from it.
TestOptionsOff builds P4 at 80 cm3 with every new option set to off and compares it with the committed plain body.
The cavity-mode step is switched off (it has its own tests), so `cavity_mode_computed` is left out of the failures.
"""
import json
import math
import pathlib
import shutil
import sys
import tempfile
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocarina_addon import api, body as body_mod, bowl_cut, checks_geo, export, kernel_bridge, meshutil, presets, report, voicing_geo  # noqa: E402

K = kernel_bridge.kernel()
P = kernel_bridge.load_params()
PAD_LIMITS = {"hole_limits[print]", "hole_limits[nominal]"}


def unexpected(body) -> list:
    return [c["name"] for c in checks_geo.unexpected_failures(body) if c["name"] != "cavity_mode_computed"]


class TestRoundBowl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="oca_bowl_"))
        cls.preset = presets.get_preset("P4-bowl")                          # the variant carries the move (s3-zB4)
        cls.body = api.build_checked_body(cls.preset, 80.0, str(cls.tmp / "P4-bowl-80-L4"), params=P, cavity_mode_step=False,
                                          body_id="P4-bowl-80-L4", root=cls.tmp)
        cls.checks = {c["name"]: c for c in cls.body.checks}
        cls.bare = api.build_checked_body(dict(cls.preset, window_cut="ellipse"), 80.0, str(cls.tmp / "bare"), params=P,
                                          cavity_mode_step=False, body_id="P4-bowl-80-L4-bare", root=cls.tmp)
        trees = []
        for b in (cls.body, cls.bare):                                   # every measure below is on the files read back
            V, F = export.read_stl(b.files["stl"])
            trees.append(meshutil.bvh(np.asarray(V, float), np.asarray(F)))
        cls.tree, cls.bare_tree = trees
        cls.o, cls.fx, cls.fy, cls.fz = (np.asarray(a, float) for a in cls.body.voicing.frame)
        cls.v = cls.body.sizing.voicing
        cls.L = float(cls.v.window_length_mm)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def at(self, xw, y, z):
        """A point given in the voicing frame (xw from the windway exit, y across, z out from the window's inner plane)."""
        return self.o + (xw - self.L) * self.fx + y * self.fy + z * self.fz

    def down(self, tree, xw, y, n=2):
        """The heights z of the first n surfaces met by a ray from z = 40 down along -z."""
        return [40.0 - h[0] for h in meshutil.ray_hits(tree, self.at(xw, y, 40.0), -self.fz, 90.0, limit=n)]

    def test_no_unexpected_failure_and_the_expected_ones_exactly(self):
        self.assertEqual(unexpected(self.body), [])
        self.assertEqual({c["name"] for c in self.body.checks if c["status"] == "fail"} - {"cavity_mode_computed"}, PAD_LIMITS)
        self.assertEqual({c["name"] for c in checks_geo.warnings(self.body)}, {"shell_hole_walls", "ergo_finger_pitch", "ergo_hole_lean_side"})

    def test_its_voicing_hash(self):
        self.assertEqual(self.body.voicing_hash, "bcdd90905c01")
        self.assertEqual(self.checks["voicing_hash"]["status"], "pass")
        self.assertEqual((self.v.window_cut, self.v.rating, self.v.windway_length_mm), ("bowl", "soft", 57.0))
        self.assertEqual({k: getattr(self.v, k) for k in K.voicing.BOWL_FIELDS}, K.voicing.BOWL_BUILD)
        # the bowl in the hash: the same body with the rule's cut is the experiment's bare body (s3-oS1, 5f3adc096c76)
        self.assertEqual(K.voicing.with_build(self.v, window_cut="ellipse").version_hash, "5f3adc096c76")

    def test_the_plastic_on_the_stl_around_the_bowl(self):
        bc = self.body.info["bowl_cut"]
        a, b, xc = self.v.bowl_half_length_mm, self.v.bowl_half_width_mm, self.v.bowl_centre_xw_mm
        half = 0.5 * self.v.windway_width_mm
        xb = float(np.asarray(self.body.voicing.outline)[np.argmax(np.asarray(self.body.voicing.outline)[:, 1]), 0])
        rows, deep = [], []
        for xw in np.arange(xc - a + 0.1, xc + a, 0.4):                  # off the windway's exit plane (xw = 0)
            for y in np.arange(-b + 0.1, b, 0.4):
                if ((xw - xc) / a) ** 2 + (y / b) ** 2 >= 1.0:
                    continue
                z, zb = self.down(self.tree, xw, y), self.down(self.bare_tree, xw, y)
                if not z or z[0] < 2.0:                                  # inside the window, down its walls, the ramp's foot
                    deep.append((xw, y))
                elif len(z) == 2 and len(zb) == 2 and zb[0] - z[0] > 0.03:      # where the bowl changed the outside
                    rows.append((xw, y, z[0] - z[1], zb[0] - zb[1]))
        r, deep = np.array(rows), np.array(deep)
        dist = np.array([np.min(np.hypot(deep[:, 0] - x, deep[:, 1] - y)) for x, y in r[:, :2]])
        x, y, t, t_bare = r.T
        self.assertGreater(len(t), 1500)
        corners = (x >= -0.3) & (x < xb) & (np.abs(y) < half + 1.0)      # over the windway's exit corners
        over_windway = (x < -0.3) & (np.abs(y) < half)
        rest = ~corners & ~over_windway
        self.assertGreaterEqual(float(t[rest].min()), body_mod.SHELL_MIN_WALL_MM)                    # never thinner than 1.32 mm
        self.assertGreaterEqual(float((t - np.minimum(body_mod.SHELL_MIN_WALL_MM, t_bare))[corners].min()), -checks_geo.TOL_MM)
        self.assertGreaterEqual(float(t[over_windway].min()), self.v.bowl_roof_mm - checks_geo.TOL_MM)     # 1.6 mm over the windway
        floor = rest & (x > 0.5) & (dist > bc["flow"]["flow_out_most_mm"] + 2.5)                    # the bowl's floor, past the flow
        self.assertGreater(int(floor.sum()), 500)
        self.assertGreaterEqual(float(t[floor].min()), self.v.bowl_under_mm - checks_geo.TOL_MM)          # 4 mm under the bowl
        self.assertGreaterEqual(bc["plastic_under_bowl_least_mm"], self.v.bowl_under_mm)

    def test_the_local_plastic_by_region(self):
        # handover phase D, on the STL read back: no plate thinner than its region allows; the labium is an edge and valid;
        # the roof over the pipe is probed (its long faces too); the pocket is joined; every hole keeps an uncut rim; and a
        # probe spacing half as wide finds the same least values
        self.assertEqual(self.checks["bowl_local_plastic"]["status"], "pass", self.checks["bowl_local_plastic"]["message"])
        self.assertEqual(self.checks["hole_seal_surface"]["status"], "pass", self.checks["hole_seal_surface"]["message"])
        bl = self.body.measurements["bowl_local"]
        reg = bl["regions"]
        self.assertEqual(sum(r["wide_thin_plate_probes"] for r in reg.values()), 0)
        # the generated uneven wall is the plain variant, not an edited shell
        self.assertEqual(self.body.info["calibration_context"], presets.calibration_context(self.preset))
        samples = self.body.measurements["bowl_local"]["map_samples"]
        self.assertTrue(samples)
        self.assertFalse(any(s["category"] == "wide_thin_plate" for s in samples))
        self.assertGreaterEqual(reg["labium"]["least_mm"], reg["labium"]["limit_mm"])
        self.assertIsNone(reg["labium"]["least_plate_mm"])
        self.assertGreater(reg["windway_roof"]["probes"], 100)
        self.assertGreaterEqual(reg["windway_roof"]["least_plate_mm"], body_mod.SHELL_MIN_WALL_MM)
        self.assertEqual(bl["air_shells"], 1)
        V, F = export.read_stl(self.body.files["stl"])
        fine = checks_geo.measure_bowl_local(self.body, np.asarray(V, float), np.asarray(F), self.tree, self.body.measurements["voicing"],
                                             step=0.12)
        for n, r in reg.items():
            f = fine["regions"][n]
            self.assertEqual(f["wide_thin_plate_probes"], 0, n)                               # the verdict holds when finer
            if r["least_plate_mm"] is not None and f["least_plate_mm"] is not None:
                self.assertAlmostEqual(f["least_plate_mm"], r["least_plate_mm"], delta=checks_geo.TOL_MM, msg=n)
        # an edge's least value moves toward its tip with finer probes (the labium: 0.46 mm at 0.25, its 0.40 mm edge at 0.12);
        # the labium's stays over its limit
        self.assertGreaterEqual(fine["regions"]["labium"]["least_mm"], reg["labium"]["limit_mm"])

    def test_the_window_walls_and_the_ramp_are_the_rules(self):
        # the ramp on the middle line: 20 deg and a 0.4 mm edge, straight as far as the rule's cut is kept
        g = self.body.measurements["voicing"]
        self.assertAlmostEqual(g["labium_angle_deg"], 20.0, delta=checks_geo.TOL_ANGLE_DEG)
        self.assertAlmostEqual(g["labium_edge_thickness_mm"], 0.4, delta=checks_geo.TOL_MM)
        s = np.array([0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        self.assertLess(s.max(), self.body.info["bowl_cut"]["ramp_rule_kept_mm"])
        z = np.array([self.down(self.tree, self.L + x, 0.0, 1)[0] for x in s])
        k = np.polyfit(s, z, 1)
        self.assertAlmostEqual(math.degrees(math.atan(k[0])), 20.0, delta=0.05)
        self.assertLess(float(np.abs(np.polyval(k, s) - z).max()), 0.01)
        # the window's walls up to 2.52 mm are the rule's ellipse cut: rays across the opening at the widest point, and to
        # the back wall above the windway's roof, against the rule's own cutter
        bc = self.body.info["bowl_cut"]
        self.assertGreaterEqual(bc["z_kept_exactly_mm"], 2.5)
        rule = voicing_geo.build(K.voicing.with_build(self.v, window_cut="ellipse"), self.body.cavity.math.port_frame(),
                                 **voicing_geo.options_from(self.preset))
        rings = bowl_cut._rings_of(rule, self.v)
        xb = float(np.asarray(rule.outline)[np.argmax(np.asarray(rule.outline)[:, 1]), 0])
        roof = float(rule.info["windway_roof_at_exit_plane_z_mm"])

        def rule_reach(zz, d):
            zr = rings[:, 0, 2]
            k = int(np.searchsorted(zr, zz))
            ring = rings[k - 1] + (zz - zr[k - 1]) / (zr[k] - zr[k - 1]) * (rings[k] - rings[k - 1])
            p0, best = np.array([xb, 0.0]), None
            for i in range(len(ring)):                                   # the ray from (xb, 0) along d against the ring's edges
                a_, b_ = ring[i, :2], ring[(i + 1) % len(ring), :2]
                M = np.column_stack([d, a_ - b_])
                if abs(np.linalg.det(M)) < 1e-12:
                    continue
                tt, uu = np.linalg.solve(M, a_ - p0)
                if tt > 0 and 0 <= uu <= 1 and (best is None or tt < best):
                    best = tt
            return best

        for zz, dirs in ((1.0, ((0, 1), (0, -1))), (2.0, ((0, 1), (0, -1), (-1, 0))), (2.45, ((0, 1), (0, -1), (-1, 0)))):
            for d in dirs:
                if d == (-1, 0) and zz <= roof + 0.2:
                    continue
                dvec = d[0] * self.fx + d[1] * self.fy
                got = meshutil.ray_hits(self.tree, self.at(xb, 0.0, zz), dvec, 30.0, limit=1)
                self.assertTrue(got, (zz, d))
                self.assertAlmostEqual(got[0][0], rule_reach(zz, np.array(d, float)), delta=0.02, msg=f"z {zz}, direction {d}")

    def test_both_thumb_hole_gaps_at_least_1_mm(self):
        # as the experiment measured them (round_hole_gap.py): the dish is where the outside departs from the bare
        # reference's by more than 0.03 mm, the hole where a ray goes through the thumb face of the bare reference
        wall = float(self.v.wall_at_window_mm)
        holes = {h.name: h for h in self.body.layout.holes if h.name in ("L_thumb", "R_thumb")}
        R = np.stack([self.fx, self.fy, self.fz], axis=1)
        gaps = {}
        for name, h in holes.items():
            c = (np.asarray(h.centre, float) - self.o) @ R
            cx, cy = float(c[0]) + self.L, float(c[1])
            step = 0.25
            xs, ys = np.arange(cx - 22.0, cx + 22.0 + 1e-9, step), np.arange(cy - 22.0, cy + 22.0 + 1e-9, step)
            Zt = np.full((len(ys), len(xs)), np.nan)
            Ze = np.full((len(ys), len(xs)), np.nan)
            for j, y in enumerate(ys):
                for i, x in enumerate(xs):
                    zt, ze = self.down(self.tree, x, y, 1), self.down(self.bare_tree, x, y, 1)
                    Zt[j, i] = zt[0] if zt else np.nan
                    Ze[j, i] = ze[0] if ze else np.nan
            YY, XX = np.meshgrid(ys, xs, indexing="ij")
            on = np.isfinite(Ze) & (Ze > wall - 6.0)
            Ze = np.where(np.isfinite(Ze), Ze, -99.0)                    # a ray through the hole meets the far wall or nothing
            deep = np.isfinite(Ze) & (Ze < wall - 6.0) & (np.hypot(XX - cx, YY - cy) < 0.5 * h.d_mm + 4.0)
            edge = deep & ~(np.roll(deep, 1, 0) & np.roll(deep, -1, 0) & np.roll(deep, 1, 1) & np.roll(deep, -1, 1))
            changed = on & np.isfinite(Zt) & (Zt > wall - 6.0) & (np.abs(Ze - Zt) > 0.03)
            self.assertTrue(edge.any(), name)
            p = np.column_stack([XX[changed], YY[changed]])
            e = np.column_stack([XX[edge], YY[edge]])
            gaps[name] = float(min(np.min(np.hypot(p[:, 0] - x, p[:, 1] - y)) for x, y in e)) if len(p) else math.inf
        for name, g in gaps.items():
            self.assertGreaterEqual(g, 1.0, name)
        self.assertAlmostEqual(gaps["L_thumb"], 5.49, delta=0.25)            # s3-zB4: 5.49 mm (0.2 mm grid, bare reference)

    def test_a_moved_thumb_hole_is_marked_in_the_report(self):
        text = report.body_report(self.body)
        self.assertIn("**MOVED THUMB HOLE (an ergonomic change):** L_thumb moved -4 mm along the hand axis", text)
        self.assertIn("MOVED THUMB HOLE (an ergonomic change): L_thumb moved -4 mm", self.checks["hole_layout"]["message"])
        self.assertIn("**Round bowl (an option, not the rule", text)
        self.assertIn("**Uneven wall (an option of the shell-edit build):**", text)
        self.assertIn("ergo_thumbs", self.checks)
        self.assertIn("L thumb +5.9 mm from L pinky", self.checks["ergo_thumbs"]["message"])

    def test_the_records_of_the_options(self):
        bc, uw = self.body.info["bowl_cut"], self.body.info["uneven_wall"]
        self.assertAlmostEqual(uw["wall_least_mm"], 3.0, delta=1e-6)
        self.assertAlmostEqual(uw["wall_most_mm"], 6.0, delta=1e-6)
        moved = self.body.voicing.info["neck"]["moved"]
        self.assertEqual(moved["tilt_deg"], 6.0)
        self.assertGreaterEqual(moved["least_plastic_around_pipe_mm"], voicing_geo.NECK_MIN_WALL_MM)
        # the pocket's back edge follows the window: no flat ceiling under the windway's exit corners (a 0.18 mm plate there)
        foot = np.asarray(self.body.voicing.footprint, float)
        self.assertFalse(bool(bowl_cut.bm.inside(foot, 1.0, 4.0)) or bool(bowl_cut.bm.inside(foot, 1.0, -4.0)))
        self.assertTrue(bool(bowl_cut.bm.inside(foot, 0.5 * self.v.window_length_mm, 0.0)))
        self.assertEqual(self.body.info["unhashed_voicing_options"]["pocket_back_margin_mm"], 0.05)
        neck = self.body.voicing.info["neck"]                     # the roof at the mouth end is the tilted neck's: the cone's cover and the lift
        self.assertAlmostEqual(neck["over_pipe_roof_at_mouth_mm"], neck["cover_mm"] + moved["mouth_end_moved_to_thumb_face_mm"], delta=0.01)
        t = bc["throat"]
        self.assertLess(t["t_eff_outer_face_mm"], self.v.wall_at_window_mm)
        self.assertLessEqual(t["t_eff_outer_face_mm"], t["t_eff_rim_mm"])
        self.assertAlmostEqual(t["v0_for_wall_cm3"], 80.0, delta=1e-9)
        self.assertGreater(t["v0_for_t_eff_outer_face_cm3"], 80.0)


class TestThinFloorPlate(unittest.TestCase):
    """P4-bowl without pocket_back_margin_mm: the pocket's flat ceiling under the windway's exit corners leaves the thin
    plate that the margin was set to remove (prompts/addon-v1-notes.md). The local plastic check must fail it, and only it."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="oca_plate_"))
        preset = {k: x for k, x in presets.get_preset("P4-bowl").items() if k != "pocket_back_margin_mm"}
        cls.body = api.build_checked_body(preset, 80.0, str(cls.tmp / "P4-bowl-80-plate"), params=P, cavity_mode_step=False,
                                          body_id="P4-bowl-80-plate", root=cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_plate_fails_and_nothing_else(self):
        self.assertEqual(unexpected(self.body), ["bowl_local_plastic"])
        reg = self.body.measurements["bowl_local"]["regions"]
        r = reg["windway_floor"]
        self.assertGreater(r["wide_thin_plate_probes"], 0)
        self.assertLess(r["least_wide_plate_mm"], checks_geo.MIN_FLOOR_LIP_MM)
        self.assertGreater(r["thin_plate_mm2"], 1.0)
        samples = self.body.measurements["bowl_local"]["map_samples"]
        self.assertTrue(any(s["category"] == "wide_thin_plate" and s["region"] == "windway_floor" for s in samples))
        xw, y, _ = r["at_wide_plate_xw_y_z"]
        self.assertTrue(0.0 <= xw <= self.body.measurements["voicing"]["widest_point_xw_mm"] and abs(y) > 3.0, (xw, y))   # an exit corner
        self.assertGreaterEqual(reg["labium"]["least_mm"], reg["labium"]["limit_mm"])          # the designed edge stays valid


class TestBowlOverhang(unittest.TestCase):
    def test_an_outside_that_overhangs_is_found(self):
        frame = (np.zeros(3), np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0]))
        xs = ys = np.round(np.arange(-2.0, 2.0 + 1e-9, 0.5), 4)
        C, everywhere = np.zeros((len(ys), len(xs))), np.ones((len(ys), len(xs)), dtype=bool)
        plain = meshutil.box_local(-5.0, 5.0, -5.0, 5.0, -10.0, 6.0)
        self.assertEqual(bowl_cut.overhangs(plain, frame, 0.0, xs, ys, C, everywhere), 0)
        shelf = meshutil.box_local(-0.75, 5.0, -5.0, 5.0, 8.0, 9.0)          # over the columns xw >= -0.5: an overhang there
        both = (np.vstack([plain[0], shelf[0]]), np.vstack([plain[1], np.asarray(shelf[1]) + len(plain[0])]))
        self.assertEqual(bowl_cut.overhangs(both, frame, 0.0, xs, ys, C, everywhere), int((xs >= -0.5).sum()) * len(ys))


class TestCalibratedBowl(unittest.TestCase):
    """P4-bowl at 80 cm3 sized from fitted constants: the SYNTHETIC example file with an invented eta_w for the bowl's hash
    (nothing here is a measured body). The uneven wall's loop sizes the holes for the wall measured at each one."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="oca_bowl_cal_"))
        cls.preset = presets.get_preset("P4-bowl")
        cls.cal = K.calibration.load_calibration(ROOT / "calibration" / "synthetic-fitted-constants.toml")
        cls.cal.voicings = {"bcdd90905c01": {"eta_w": 0.88}}   # 0.77 fails range_ratio (10.3 > 10): a true verdict
        cls.body = api.build_checked_body(cls.preset, 80.0, str(cls.tmp / "P4-bowl-80-cal"), params=P, cavity_mode_step=False,
                                          body_id="P4-bowl-80-cal", root=cls.tmp, calibration=cls.cal)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_bowls_constants_and_its_window(self):
        info = self.body.info["calibration_info"]
        self.assertEqual((self.body.voicing_hash, info["eta_w"], info["eta_w_source"]), ("bcdd90905c01", 0.88, "measured"))
        self.assertTrue(self.body.info["synthetic"])
        self.assertEqual(self.body.params["hole_key"], "fitted")
        designed = presets.resolve_voicing(self.preset, 80.0, P)          # a measured window is kept, not solved again
        self.assertEqual(self.body.sizing.voicing.window_area_mm2, designed.window_area_mm2)
        self.assertEqual(self.body.sizing.volume_factor, self.cal.volume_factor)
        self.assertTrue(any("psi = 1" in w for w in info["warnings"]))  # no position factors for the moved thumb's layout

    def test_it_builds_with_only_the_round_hole_verdict_failing(self):
        self.assertEqual(unexpected(self.body), [])
        self.assertLessEqual({c["name"] for c in self.body.checks if c["status"] == "fail"} - {"cavity_mode_computed"},
                             {"hole_limits[fitted]"})

    def test_each_hole_is_sized_for_its_measured_wall(self):
        over = self.body.info["shell_edit"]["holes"]
        rows = {r.name: r for r in self.body.sizing.holes.solutions["fitted"]}
        for name, r in rows.items():
            self.assertAlmostEqual(r.wall_mm, over[name]["wall_sized_mm"], delta=body_mod.SHELL_DEPTH_TOL_MM, msg=name)
        self.assertGreater(min(rows[n].wall_mm for n in ("L_thumb", "R_thumb")), 5.0)      # the 6 mm thumb face, not 4 mm
        self.assertLess(rows["L_index"].wall_mm, 3.5)                                      # the 3 mm finger deck

    def test_the_template_names_what_was_built(self):
        t = K.measurements.template_from_sizing(self.body.sizing, self.body.body_id, shape="P4-bowl", key="fitted")
        self.assertEqual(t.voicing_hash, "bcdd90905c01")
        drawn = {h.name: h.d_mm for h in self.body.layout.holes}
        for h in t.holes:
            self.assertAlmostEqual(h.d_design_m * 1000.0, drawn[h.name], delta=1e-9, msg=h.name)


class TestOptionsOff(unittest.TestCase):
    """P4 at 80 cm3 with every new option set to off is the plain body of rule version 3 (addon_checks/P4-80.json)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="oca_off_"))
        preset = dict(presets.get_preset("P4"), wall_front_less_mm=0.0, wall_back_more_mm=0.0, neck_tilt_deg=0.0, thumb_offsets_mm={})
        cls.body = api.build_checked_body(preset, 80.0, str(cls.tmp / "P4-80"), params=P, cavity_mode_step=False, root=cls.tmp)
        cls.committed = json.loads((ROOT / "addon_checks" / "P4-80.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_same_body(self):
        self.assertEqual(self.body.voicing_hash, "312011ec9f0e")
        self.assertFalse(any(k in self.body.info for k in ("bowl_cut", "uneven_wall", "thumb_offsets_mm", "shell_edit")))
        old, new = self.committed["measurements"]["volume"], self.body.measurements["volume"]
        for key in ("body_plastic_cm3", "capped_air_built_cm3", "cavity_mesh_cm3"):
            self.assertAlmostEqual(new[key], old[key], delta=5e-4, msg=key)
        was = {c["name"]: c["status"] for c in self.committed["checks"] if c["name"] != "cavity_mode_computed"}
        now = {c["name"]: c["status"] for c in self.body.checks if c["name"] != "cavity_mode_computed"}
        self.assertEqual(now, was)
        old_h = {h["name"]: h for h in self.committed["measurements"]["holes"]}
        for r in self.body.measurements["holes"]:
            self.assertEqual(r["d_kernel_mm"], old_h[r["name"]]["d_kernel_mm"], r["name"])
            for a, b in zip(r["centre"], old_h[r["name"]]["centre"]):
                self.assertAlmostEqual(a, b, places=3, msg=r["name"])


class TestEllipseAperture(unittest.TestCase):
    """P4-bowl with a true elliptical aperture (docs/10, step 3): the cut window is the kernel's outline. Geometry only."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="oca-ellipse-"))
        cls.body = api.build_checked_body("P4-bowl-e1022", 80.0, str(cls.tmp), params=P, cavity_mode_step=False, verbose=False)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_cut_window_is_the_ellipse_of_the_record(self):
        v, g = self.body.sizing.voicing, self.body.measurements["voicing"]
        self.assertEqual((v.shape, v.window_length_mm), ("ellipse", 10.22))
        self.assertAlmostEqual(g["window_length_mm"], v.window_length_mm, delta=checks_geo.TOL_MM)
        self.assertAlmostEqual(g["window_width_mm"], 4.0 * v.window_area_mm2 / (math.pi * v.window_length_mm), delta=checks_geo.TOL_MM)
        self.assertAlmostEqual(g["window_area_mm2"] / (math.pi * 10.22 * v.window_width_mm / 4.0), 1.0, delta=checks_geo.TOL_AREA_REL)
        self.assertAlmostEqual(g["windway_exit_width_mm"], v.window_width_mm, delta=checks_geo.TOL_MM)   # the windway follows the window

    def test_it_builds_like_the_bowl_it_came_from(self):
        skip = ("cavity_mode_computed",)                       # not run here
        self.assertEqual([c["name"] for c in checks_geo.unexpected_failures(self.body) if c["name"] not in skip], [])
        self.assertEqual(sum(r["wide_thin_plate_probes"] for r in self.body.measurements["bowl_local"]["regions"].values()), 0)
        self.assertNotEqual(self.body.voicing_hash, "bcdd90905c01")
