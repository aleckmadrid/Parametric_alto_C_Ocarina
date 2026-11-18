"""Headless Blender tests: the geometry check as a test suite.

Run with Blender 5.1 from the repository root (about 5 minutes):

    blender -b --factory-startup --python tests/run_blender_tests.py

Every body is built once, written to a temporary folder, read back from disk and measured there
(ocarina_addon.api.build_checked_body, the path the stage commands use). Nothing in the repository is
written.
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

from ocarina_addon import api, checks_geo, export, kernel_bridge, meshutil, presets, report, stages, stub  # noqa: E402
from tools import geometry_check  # noqa: E402

K = kernel_bridge.kernel()
P = kernel_bridge.load_params()
TMP = None
PAD_LIMITS = {"hole_limits[print]", "hole_limits[nominal]"}


def setUpModule():
    global TMP
    TMP = pathlib.Path(tempfile.mkdtemp(prefix="oca_test_"))


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


def checks_of(body) -> dict:
    return {c["name"]: c for c in body.checks}


class TestCavities(unittest.TestCase):
    """The 30 cavities of the C3 check: P0-P4 at the mesh volumes of the 65, 80, 88, 95, 110 and 125 cm3 bodies
    (110 and 125 are a range check of the generator; they are not printed since the ladder change)."""

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.failures, _ = geometry_check.measure_cavities(renders=False)

    def test_all_cavities_pass(self):
        self.assertEqual(len(self.rows), 30)
        self.assertEqual(sorted({r["preset"] for r in self.rows}), ["P0", "P1", "P2", "P3", "P4"])
        self.assertEqual(sorted({r["v0_cm3"] for r in self.rows}), [65.0, 80.0, 88.0, 95.0, 110.0, 125.0])
        self.assertEqual(self.failures, [])
        self.assertTrue(all(r["ok"] for r in self.rows))

    def test_volume_port_and_topology(self):
        for r in self.rows:
            tag = f"{r['preset']} at {r['v0_cm3']:g} cm3"
            self.assertLess(abs(r["volume_error_pct"]), 0.5, tag)                 # the plan's limit
            self.assertLess(abs(r["volume_error_pct"]), 1e-3, tag)                # what the node group reaches
            self.assertLess(r["port_distance_before_mm"], 1e-3, tag)             # the voicing port is the origin
            self.assertLess(r["port_distance_after_mm"], 1e-3, tag)
            self.assertLess(r["port_normal_change_deg"], 0.05, tag)
            self.assertLess(r["mesh_vs_formula_mm"], 1e-3, tag)
            self.assertTrue(r["manifold"] and r["shells"] == 1, tag)
            self.assertEqual((r["zero_length_edges"], r["degenerate_faces"], r["self_intersections"]), (0, 0, 0), tag)

    def test_lengths_of_doc_04(self):
        at80 = {r["preset"]: r["length_mm"] for r in self.rows if r["v0_cm3"] == 80.0}
        for name, doc in (("P0", 79.0), ("P1", 111.0), ("P2", 126.0), ("P3", 95.0), ("P4", 133.0)):
            self.assertAlmostEqual(at80[name] / doc, 1.0, delta=0.012, msg=name)     # the mesh holds 78.1 cm3, so 0.8 % shorter


class BodyCase(unittest.TestCase):
    PRESET, V0 = "P1", 80.0

    @classmethod
    def setUpClass(cls):
        if cls is BodyCase:
            raise unittest.SkipTest("base class")
        cls.bid = f"{cls.PRESET}-{cls.V0:g}"
        cls.out = TMP / cls.bid
        cls.body = api.build_checked_body(cls.PRESET, cls.V0, str(cls.out), params=P, renders=True,
                                          render_dir=str(cls.out / "renders"), root=TMP)
        cls.checks = checks_of(cls.body)
        cls.m = cls.body.measurements

    def test_files_are_written_and_the_stl_was_read_back(self):
        for name in (f"{self.bid}.stl", f"{self.bid}_air_capped.stl", f"{self.bid}_air_fem.stl", f"{self.bid}_checks.json",
                     f"{self.bid}_cavity_mode.json"):
            self.assertTrue((self.out / name).is_file(), name)
        V, F = export.read_stl(str(self.out / f"{self.bid}.stl"))
        self.assertEqual(len(F), self.m["stl_file"]["triangles"])
        self.assertTrue(meshutil.manifold_report(V, F)["manifold"])
        self.assertAlmostEqual(meshutil.volume(V, F) / 1000.0, self.m["volume"]["body_plastic_cm3"], places=6)
        saved = json.loads((self.out / f"{self.bid}_checks.json").read_text(encoding="utf-8"))
        self.assertEqual([c["name"] for c in saved["checks"]], [c["name"] for c in self.body.checks])

    def test_no_unexpected_failure(self):
        self.assertEqual([c["name"] for c in checks_geo.unexpected_failures(self.body)], [])
        failed = {c["name"] for c in self.body.checks if c["status"] == "fail"}
        self.assertTrue(failed <= PAD_LIMITS, failed)
        self.assertTrue(all(c["expected"] for c in self.body.checks if c["status"] == "fail"))
        self.assertTrue(all(c["status"] in ("pass", "fail", "needs_fem", "warn", "info") for c in self.body.checks))

    def test_phase_4_gate_hole_sizes(self):
        self.assertEqual(len(self.m["holes"]), 12)
        for r in self.m["holes"]:
            self.assertLess(abs(r["d_error_mm"]), 0.05, r["name"])
            self.assertLess(abs(r["chimney_error_mm"]), 0.05, r["name"])
        self.assertEqual(self.checks["hole_sizes_phase4_gate"]["status"], "pass")
        self.assertGreaterEqual(min(r["nearest_gap_mm"] for r in self.m["holes"]), 3.4 - 1e-6)
        if "inward_tubes" in self.checks:
            self.assertEqual(self.checks["inward_tubes"]["status"], "pass")

    def test_volumes_and_voicing(self):
        vol = self.m["volume"]
        self.assertLess(abs(vol["capped_air_measured_cm3"] / self.V0 - 1.0), 0.005)
        self.assertLess(abs(vol["cavity_mesh_cm3"] / vol["cavity_mesh_target_cm3"] - 1.0), 0.005)
        v = self.body.sizing.voicing
        self.assertEqual(self.body.voicing_hash, K.sizing.size_body(self.V0, params=P).voicing.version_hash)
        g = self.m["voicing"]
        self.assertAlmostEqual(g["window_length_mm"], v.window_length_mm, delta=0.05)
        self.assertAlmostEqual(g["window_width_mm"], v.window_width_mm, delta=0.05)
        self.assertAlmostEqual(g["window_area_mm2"] / v.window_area_mm2, 1.0, delta=0.002)
        self.assertAlmostEqual(g["labium_angle_deg"], 20.0, delta=0.5)
        for name in ("topology", "booleans", "voicing_hash", "voicing_dimensions", "voicing_orientation", "voicing_keepouts",
                     "wall_thickness", "volume_capped_air", "hole_axes", "hole_to_voicing", "hole_layout"):
            self.assertEqual(self.checks[name]["status"], "pass", name)

    def test_ergonomic_checks_are_soft(self):
        ergo = [c for c in self.body.checks if c["name"].startswith("ergo_")]
        self.assertEqual(len(ergo), 11)
        self.assertTrue(all(c["status"] in ("pass", "warn") for c in ergo))
        self.assertEqual([c["name"] for c in checks_geo.warnings(self.body)], [c["name"] for c in ergo if c["status"] == "warn"])

    def test_cavity_mode(self):
        self.assertTrue(self.m["cavity_mode"]["computed"], self.m["cavity_mode"])
        self.assertEqual(self.checks["cavity_mode_computed"]["status"], "pass")
        self.assertEqual(self.checks["cavity_mode_c2L"]["status"], "info")
        self.assertNotIn("cavity_mode", self.checks)                    # the kernel's result is shown under its own name

    def test_acoustic_numbers_equal_the_committed_report(self):
        committed = json.loads((ROOT / "addon_checks" / f"{self.bid}.json").read_text(encoding="utf-8"))
        old = {h["name"]: h for h in committed["measurements"]["holes"]}
        for r in self.m["holes"]:
            self.assertEqual(r["d_kernel_mm"], old[r["name"]]["d_kernel_mm"], r["name"])
            self.assertEqual(r["chimney_kernel_mm"], old[r["name"]]["chimney_kernel_mm"], r["name"])
            for a, b in zip(r["centre"], old[r["name"]]["centre"]):
                self.assertAlmostEqual(a, b, places=3, msg=f"{r['name']}: the hole moved against the committed layout")

    def test_pictures(self):
        for name in ("top.png", "bottom.png", "sheet_views.png", "sheet_sections.png", "voicing.png"):
            self.assertGreater((self.out / "renders" / name).stat().st_size, 2000, name)

    def test_report_text(self):
        text = report.body_report(self.body, 1.0, "Written by a test.")
        self.assertIn("## Warnings", text)
        self.assertIn("## Hand layout", text)
        self.assertIn("sub1 = sub_L", text)
        self.assertIn("no unexpected failure", text)


class TestBodyP1(BodyCase):
    PRESET, V0 = "P1", 80.0

    def test_subholes_follow_the_owner_decision(self):
        e = self.m["ergonomics"]["inner"]
        self.assertEqual((e["sub1"]["parent"], e["sub2"]["parent"]), ("L_ring", "R_middle"))
        self.assertAlmostEqual(e["sub1"]["dist_3d"], 10.0, delta=0.01)             # 10 mm since 2026-11-18 (owner decision 1)
        self.assertAlmostEqual(e["sub2"]["dist_3d"], 7.5, delta=0.01)
        self.assertLess(abs(e["sub1"]["off_normal_deg"]), 1.0)
        self.assertLess(abs(e["sub2"]["off_normal_deg"]), 1.0)
        by = {r["name"]: r for r in self.m["holes"]}
        self.assertLess(by["sub1"]["centre"][1], by["L_ring"]["centre"][1])           # toward the player (-Y)
        self.assertGreater(by["sub2"]["centre"][1], by["R_middle"]["centre"][1])      # away from the player
        self.assertEqual(self.checks["ergo_subholes"]["status"], "pass")
        self.assertFalse(self.m["ergonomics"]["taped"])

    def test_cavity_mode_value(self):
        self.assertAlmostEqual(self.checks["cavity_mode_computed"]["value"] / 1.63, 1.0, delta=0.02)
        self.assertEqual(self.body.voicing_hash, "b4620fbf3d67")                      # rules of version 2 (2026-11-18)
        self.assertEqual({c["name"] for c in self.body.checks if c["status"] == "fail"}, PAD_LIMITS)

    def test_the_build_of_the_rules_is_built(self):
        """Owner decisions 2 to 6 of 2026-11-18: the ellipse cut, the neck that stands 15 degrees, the pipe lowered
        10 degrees inside it, the 3 mm mouth end and the pocket blend are the build of every stage body."""
        v, info, g = self.body.sizing.voicing, self.body.voicing.info, self.m["voicing"]
        self.assertEqual((v.window_cut, v.cut_widen_mm, v.shelf_angle_deg), ("ellipse", 3.0, 40.0))
        self.assertEqual((v.stub_style, v.stub_pitch_deg, v.windway_pitch_deg, v.pocket_blend_radius_mm), ("neck", 15.0, 5.0, 12.0))
        self.assertEqual((info["cut_style"], info["stub_style"], info["stub_pitch_deg"], info["windway_pitch_deg"]),
                         ("ellipse", "neck", 15.0, 5.0))
        self.assertEqual((info["cone"]["widen_mm"], info["shelf_angle_deg"], info["pocket_blend_radius_mm"]), (3.0, 40.0, 12.0))
        self.assertAlmostEqual(info["neck"]["pipe_lowered_deg"], 10.0)
        self.assertEqual(info["neck"]["min_wall_mm"], 1.2)                            # the owner's minimum around the pipe
        self.assertAlmostEqual(g["windway_inlet_height_mm"], 3.0, delta=0.01)
        self.assertAlmostEqual(g["windway_exit_height_mm"], 1.2, delta=0.01)
        self.assertGreater(g["windway_floor_lip_mm"], 1.2)
        self.assertEqual(self.body.info.get("unhashed_voicing_options"), None)
        self.assertIn("Build (in the hash): ellipse cut, 3 mm per side, shelf 40°; windway +5° against the body; neck standing 15° off "
                      "the body, the pipe lowered 10° inside it; pocket blend 12 mm.", report.body_report(self.body, 1.0, ""))

    def test_the_pocket_blend_ends_on_the_chamber_wall(self):
        """The pocket ceiling falls away behind the labium until it meets the chamber wall, in every direction, and no
        further. A blend with a fixed reach cut into the wall of a curved chamber (0.06 mm of plastic left on P2-80)."""
        pb = self.m["voicing"]["pocket_blend"]
        self.assertEqual(pb["radius_mm"], 12.0)
        self.assertTrue(pb["on_the_chamber"])
        self.assertGreater(pb["directions"], 100)
        self.assertEqual(pb["full_reach_directions"], 0)
        self.assertEqual(pb["met_directions"] + pb["side_wall_directions"], pb["directions"])
        self.assertEqual(pb["step_left_mm"], 0.0)
        self.assertLess(pb["reach_max_mm"], 0.98 * 12.0)
        self.assertEqual(self.checks["pocket_blend"]["status"], "pass")
        self.assertGreaterEqual(self.m["wall"]["final_min_thickness_mm"], checks_geo.MIN_PLASTIC_MM)
        self.assertEqual(self.checks["wall_thickness"]["status"], "pass")

    def test_a_sliver_fails_the_wall_check(self):
        """Plastic thinner than one extrusion line is a build error, even where the plain wall is 4 mm."""
        m = dict(self.m, wall=dict(self.m["wall"], final_min_thickness_mm=0.06))
        checks = {c["name"]: c for c in checks_geo.evaluate(self.body, m, P)}
        self.assertEqual(checks["wall_thickness"]["status"], "fail")
        self.assertEqual(self.checks["wall_thickness"]["status"], "pass")
        self.assertEqual(checks_geo.MIN_PLASTIC_MM, 0.4)

    def test_the_standing_neck_stays_outside_the_flare(self):
        """The neck stands above the outer face behind the window. The outside keep-out is the 45 degree flare from the
        window rim; the neck must stay under it."""
        g = self.m["voicing"]
        self.assertGreater(g["points_above_outer_face"], 1000)
        self.assertGreater(g["max_height_above_outer_face_mm"], 5.0)
        self.assertEqual(g["flare_violations"], 0)
        self.assertLess(g["flare_steepest_deg"], g["flare_limit_deg"])
        self.assertEqual(g["flare_limit_deg"], 45.0)
        self.assertIn("0 points of the surface inside the 45° flare", self.checks["voicing_keepouts"]["message"])

    def test_a_missing_solver_fails_the_check_and_never_passes(self):
        for cm in (None, dict(computed=False, reason="no Python with numpy and scipy was found")):
            c = checks_geo._cavity_mode_check(cm, P)
            self.assertEqual(c["status"], "fail")
            self.assertTrue(c["message"].startswith("NOT COMPUTED"))
        self.assertEqual(checks_geo._cavity_mode_check(dict(self.m["cavity_mode"], ratio=1.2), P)["status"], "needs_fem")
        self.assertEqual(checks_geo._cavity_mode_check(dict(self.m["cavity_mode"], ratio=0.9), P)["status"], "fail")

    def test_a_warning_is_never_a_failure(self):
        self.assertGreater(len(checks_geo.warnings(self.body)), 0)
        self.assertEqual(checks_geo.unexpected_failures(self.body), [])
        blocks = report.check_blocks(self.body.checks)
        self.assertEqual(blocks["unexpected"], [])
        self.assertEqual({c["name"] for c in blocks["expected"]}, PAD_LIMITS)
        self.assertTrue(all(c["name"].startswith("ergo_") for c in blocks["warnings"]))


class TestBodyP0(BodyCase):
    PRESET, V0 = "P0", 65.0

    def test_taped_test_body(self):
        self.assertTrue(self.m["ergonomics"]["taped"])
        ergo = [c for c in self.body.checks if c["name"].startswith("ergo_")]
        for c in ergo:
            self.assertEqual(c["status"], "warn", c["name"])
            self.assertTrue(c["message"].startswith("taped test body, not a hand layout"), c["name"])
        self.assertEqual(self.body.layout.kind, "relative")
        self.assertEqual(self.body.voicing_hash, "16410d2e6a1b")
        self.assertEqual({c["name"] for c in self.body.checks if c["status"] == "fail"}, {"hole_limits[nominal]"})

    def test_two_inward_tubes(self):
        tubes = {r["name"]: r for r in self.m["holes"] if r["tube_kernel_mm"] > 0}
        self.assertEqual(sorted(tubes), ["sub1", "sub2"])
        self.assertAlmostEqual(tubes["sub1"]["tube_length_measured_mm"], 0.5, delta=0.05)
        self.assertAlmostEqual(tubes["sub2"]["tube_length_measured_mm"], 5.0, delta=0.05)
        self.assertAlmostEqual(tubes["sub2"]["tube_wall_measured_mm"], 1.2, delta=0.05)


class TestStages(unittest.TestCase):
    def test_stage_lists_of_the_plan(self):
        self.assertEqual([b[2] for b in stages.STAGE2_BODIES],
                         ["P0-65", "P0-80", "P0-95", "P1-80", "P2-80", "P4-80", "P0-80-b", "P0-80-c"])
        self.assertNotIn("P3", [b[0] for b in stages.STAGE2_BODIES])            # stashed since 2026-11-17 (docs/08)
        self.assertNotIn("P3", [b[0] for b in stages.STAGE3_BODIES])
        self.assertEqual(stages.STAGE1_STUBS, ["V-a", "V-af", "V-b", "V-d", "V-a0", "V-a35", "V-a3"])
        self.assertEqual([s for s in stages.STAGE1_STUBS if stub.RECIPES[s][6] == "plain"], ["V-af", "V-b"])   # the plain builds
        self.assertEqual([(p, v) for p, v, printed in stages.STAGE3_BODIES if not printed], [("P0", 88.0)])
        self.assertEqual(len(stages.STAGE3_BODIES), 7)

    def test_stage1_builds_every_stub_even_when_one_fails(self):
        """V-a is made to fail; V-b (the forced rounded rectangle) must still be built, and the stage must fail."""
        real = api.build_checked_body

        def flaky(preset, v0, out_dir, **kwargs):
            if kwargs.get("body_id") == "V-a":
                raise RuntimeError("made to fail by the test")
            return real(preset, v0, out_dir, **kwargs)

        out = TMP / "stage1"
        api.build_checked_body = flaky
        try:
            st = stages.run_stage1(out, renders=False, params=P, root=TMP, only=["V-a", "V-b"])
        finally:
            api.build_checked_body = real
        by = {it.body_id: it for it in st.items}
        self.assertEqual(sorted(by), ["V-a", "V-b"])
        self.assertIsNone(by["V-a"].body)
        self.assertIn("made to fail", by["V-a"].error)
        self.assertEqual((st.ok, st.exit_code), (False, 1))
        b = by["V-b"].body
        self.assertEqual(checks_geo.unexpected_failures(b), [])
        self.assertFalse(by["V-b"].failed)
        c = checks_of(b)
        self.assertEqual(b.kind, "stub")
        self.assertEqual(b.sizing.voicing.shape, "rounded_rectangle")
        self.assertEqual(c["stub_volume"]["status"], "pass")
        self.assertLess(abs(b.measurements["volume"]["capped_air_measured_cm3"] / 25.0 - 1.0), 0.005)
        self.assertEqual(c["voicing_orientation"]["status"], "pass")
        self.assertEqual(c["stub_pitch_predicted"]["status"], "info")
        self.assertNotIn("pocket_blend", c)                                 # the plain build has no pocket blend
        self.assertEqual(b.measurements["holes"], [])
        self.assertEqual(b.measurements["topology"]["genus"], 1)             # the window and the windway, no holes
        self.assertFalse([x for x in b.checks if x["name"].startswith("ergo_")])
        # the same window area as V-a, another shape, another hash
        va = stub.stub_sizing("V-a", P, 25.0).voicing
        self.assertAlmostEqual(b.sizing.voicing.window_area_mm2, va.window_area_mm2, places=6)
        self.assertNotEqual(b.sizing.voicing.version_hash, va.version_hash)
        self.assertEqual(va.version_hash, K.sizing.size_body(80.0, params=P).voicing.version_hash)
        self.assertTrue(b.sizing.voicing.is_plain_build)                      # V-b has the plain build: the ellipse cut is made for the teardrop
        # V-af: the same window with the plain build, so another hash, which no body carries
        vaf = stub.stub_sizing("V-af", P, 25.0).voicing
        self.assertTrue(vaf.is_plain_build)
        self.assertAlmostEqual(vaf.window_area_mm2, va.window_area_mm2, places=9)
        self.assertEqual(vaf.version_hash, K.voicing.with_build(va, **K.voicing.PLAIN_BUILD).version_hash)
        self.assertNotIn(vaf.version_hash, report.stub_body_hashes(P))
        # the blank measurement template of the stub
        template = out / "V-b" / "V-b_measurement.toml"
        m = K.measurements.load_stub(template, allow_incomplete=True)
        self.assertEqual((m.id, m.voicing_hash, m.target_volume_cm3), ("V-b", b.voicing_hash, 25.0))
        with self.assertRaises(K.measurements.MeasurementIncomplete):
            K.measurements.load_stub(template)
        text = st.report_path.read_text(encoding="utf-8")
        for needle in ("# Stage 1", "## Unexpected failures", "## Expected failures", "## Warnings", "V-a: the build failed", "made to fail"):
            self.assertIn(needle, text)

    def test_stage3_keeps_the_round_1_tubes_and_positions(self):
        cal_path = ROOT / "calibration" / "synthetic-fitted-constants.toml"
        st = stages.run_stage3(TMP / "stage3", cal_path, renders=False, params=P, root=TMP, only=["P0-65-r2"])
        self.assertEqual(len(st.items), 1)
        it = st.items[0]
        self.assertIsNotNone(it.body, it.error)
        self.assertTrue(st.synthetic)
        b, round1 = it.body, K.sizing.size_body(65.0, params=P)
        cal = K.calibration.load_calibration(cal_path)
        self.assertEqual(list(b.sizing.holes.tubes_mm), list(round1.holes.tubes_mm))          # sub1 0.5 mm, sub2 5.0 mm, kept
        self.assertEqual(b.voicing_hash, round1.voicing.version_hash)                         # the printed window is kept
        self.assertAlmostEqual(b.sizing.v0_cm3, 65.0, places=9)                               # the printed volume is kept (default)
        fitted = {h.name: h.d_mm for h in b.sizing.holes.solutions["fitted"]}
        first = {h.name: h.d_mm for h in round1.holes.solutions["print"]}
        self.assertTrue(all(abs(fitted[n] - first[n]) > 0.01 for n in fitted))                # the diameters did change
        for r in b.measurements["holes"]:                                                     # drawn at design minus the hole offset
            self.assertAlmostEqual(r["d_kernel_mm"], fitted[r["name"]] - cal.hole_offset_mm, places=9)
            self.assertLess(abs(r["d_error_mm"]), 0.05)
        vol = b.measurements["volume"]
        self.assertAlmostEqual(vol["v0_target_cm3"] / (65.0 / cal.volume_factor), 1.0, delta=0.003)   # the model is scaled for the print
        self.assertEqual(checks_of(b)["volume_capped_air"]["status"], "pass")
        # the positions are those of the round-1 layout (doc 04 D10): same place on the surface, in units of the body length
        first_build = json.loads((ROOT / "addon_checks" / "P0-65.json").read_text(encoding="utf-8"))
        scale = b.cavity.scale / first_build["measurements"]["cavity"]["scale"]
        old = {h["name"]: h["centre"] for h in first_build["measurements"]["holes"]}
        for r in b.measurements["holes"]:
            self.assertLess(math.dist(r["centre"], [c * scale for c in old[r["name"]]]), 0.02, r["name"])
        text = st.report_path.read_text(encoding="utf-8")
        self.assertIn("SYNTHETIC CONSTANTS", text)
        self.assertIn("(kept)", text)
        self.assertNotIn("(CHANGED)", text)
        self.assertIn("Round-hole verdict", text)
        m = K.measurements.load_measurement(TMP / "stage3" / "P0-65-r2" / "P0-65-r2_measurement.toml", allow_incomplete=True)
        self.assertEqual(m.voicing_hash, b.voicing_hash)


class TestEllipseWindowCut(unittest.TestCase):
    """The "ellipse" window cut (the owner's choice among the prototypes, 2026-11-17; the rule since 2026-11-18): one
    surface from the window outline to an ellipse at the outer face. It changes how the window looks from outside. It
    must not change the window, the lip and the ramp. One body, P4-80, as a VARIANT of the rule: the wider setting
    "P1" of Analizes_ocarinas/Window_cutout/Window_cutout.md section 12 (the rule is "P3": 3 mm, shelf 40 degrees)."""
    OPTIONS = dict(window_cut="ellipse", cone_widen_mm=4.0, shelf_angle_deg=50.0, stub_style="neck",       # "P1" of the note
                   pocket_blend_radius_mm=12.0)

    @classmethod
    def setUpClass(cls):
        cls.bid = "P4-80-ellipse"
        cls.out = TMP / cls.bid
        cls.body = api.build_checked_body(dict(presets.get_preset("P4"), **cls.OPTIONS), 80.0, str(cls.out), params=P,
                                          root=TMP, body_id=cls.bid)
        cls.checks = checks_of(cls.body)
        cls.m = cls.body.measurements
        cls.v = cls.body.sizing.voicing
        cls.info = cls.body.voicing.info

    def test_no_unexpected_failure(self):
        self.assertEqual([c["name"] for c in checks_geo.unexpected_failures(self.body)], [])
        self.assertTrue({c["name"] for c in self.body.checks if c["status"] == "fail"} <= PAD_LIMITS)
        for name in ("topology", "booleans", "voicing_dimensions", "voicing_orientation", "voicing_keepouts", "windway_floor_lip",
                     "wall_thickness", "volume_capped_air", "hole_to_voicing"):
            self.assertEqual(self.checks[name]["status"], "pass", name)

    def test_the_window_the_lip_and_the_ramp_equal_the_record(self):
        v, g = self.v, self.m["voicing"]
        # A variant of the build has its own hash: the record that is hashed is the one that was built.
        standard = K.sizing.size_body(80.0, params=P).voicing
        self.assertEqual((v.window_cut, v.cut_widen_mm, v.shelf_angle_deg), ("ellipse", 4.0, 50.0))
        self.assertEqual((v.stub_style, v.stub_pitch_deg, v.windway_pitch_deg), ("neck", 15.0, 5.0))      # not overridden: the rule
        self.assertNotEqual(self.body.voicing_hash, standard.version_hash)
        self.assertEqual(self.body.voicing_hash, K.voicing.with_build(standard, cut_widen_mm=4.0, shelf_angle_deg=50.0).version_hash)
        self.assertEqual(self.checks["voicing_hash"]["status"], "pass")
        self.assertAlmostEqual(g["window_length_mm"], v.window_length_mm, delta=0.01)
        self.assertAlmostEqual(g["window_width_mm"], v.window_width_mm, delta=0.01)
        self.assertAlmostEqual(g["window_area_mm2"] / v.window_area_mm2, 1.0, delta=0.002)
        self.assertAlmostEqual(g["labium_angle_deg"], v.labium_ramp_angle_deg, delta=0.5)
        self.assertAlmostEqual(g["labium_edge_thickness_mm"], v.labium_edge_thickness_mm, delta=0.02)
        self.assertAlmostEqual(g["labium_offset_mm"], v.labium_offset_mm, delta=0.02)
        self.assertAlmostEqual(g["windway_exit_height_mm"], v.windway_exit_height_mm, delta=0.01)
        # This cut opens next to the widest points below any level where the windway half could be sliced, so the
        # area is the free opening seen straight in: the narrowest opening at every point.
        self.assertEqual(g["window_area_method"], "free opening seen along the normal")
        self.assertAlmostEqual(g["window_width_free_mm"], v.window_width_mm, delta=0.01)
        self.assertEqual(g["window_cut"]["style"], "ellipse")

    def test_the_lip_keeps_its_thickness_along_the_labium(self):
        v, vs = self.v, self.body.voicing
        o, fx, fy, fz = vs.frame
        V, F = export.read_stl(self.body.files["stl"])
        tree = meshutil.bvh(V, F)
        e, L, step = v.labium_edge_thickness_mm, v.window_length_mm, 0.03
        seen = 0
        for xw, y, t in vs.outline:
            if abs(t) > math.radians(60.0):                                   # the labium within 60 degrees of the jet
                continue
            p = o + fx * (xw + step * math.cos(t) - L) + fy * (y + step * math.sin(t))
            top = meshutil.ray_hits(tree, p + 30.0 * fz, -fz, 60.0)
            under = meshutil.ray_hits(tree, p - 4.0 * fz, fz, 30.0)
            self.assertTrue(top and under, f"no plastic just behind the lip at {math.degrees(t):.0f} degrees")
            thickness = (30.0 - top[0][0]) - (-4.0 + under[0][0])
            self.assertGreater(thickness, e - 0.02, f"{math.degrees(t):.0f} degrees")
            self.assertLess(thickness, e + 0.08, f"{math.degrees(t):.0f} degrees")
            seen += 1
        self.assertGreater(seen, 40)

    def test_the_ellipse_at_the_outer_face(self):
        c, W = self.info["cone"], self.v.window_width_mm
        self.assertEqual((self.info["cut_style"], c["style"]), ("ellipse", "ellipse"))
        self.assertEqual(c["widen_mm"], 4.0)
        self.assertAlmostEqual(c["ellipse_width_mm"], W + 8.0, places=9)
        self.assertLess(c["inward_move_removed_max_mm"], 0.02)                  # on this window the no-overhang rule barely acts
        self.assertGreater(c["ellipse_length_mm"], self.v.window_length_mm)
        self.assertEqual(self.info["pocket_blend_radius_mm"], 12.0)

    def test_the_window_check_notices_a_wall_that_leans_in(self):
        """On a window much wider than long (P0-125: 18.6 x 9.65 mm) the loft would lean in over the window next to
        the widest points. The cutter removes that part of the move. With the rule switched off, the window check
        must fail: the free opening is then smaller than the record."""
        from ocarina_addon import voicing_geo
        # The plain box stub, level: this test is about the window cut. (With the neck of the rules the build stops, as
        # it should: the bell of the neck is 4.8 window widths wide, 89 mm on this window, and standing 15 degrees it
        # reaches the hole sub1, whose Boolean check then fails. 125 cm3 is no stage body; the neck needs its own width
        # before a window this wide gets one.)
        preset = dict(presets.get_preset("P0"), **dict(self.OPTIONS, cone_widen_share=0.34, shelf_angle_deg=40.0,   # the share wins over the mm
                                                       stub_style="box", stub_pitch_deg=0.0, windway_pitch_deg=0.0))
        record = K.sizing.size_body(125.0, params=P).voicing.window_area_mm2
        v125 = K.sizing.size_body(125.0, params=P).voicing
        self.assertAlmostEqual(voicing_geo.record_overrides(preset, v125)["cut_widen_mm"], 0.34 * v125.window_width_mm)
        seen = {}
        for rule in (True, False):
            voicing_geo.ELLIPSE_NO_OVERHANG = rule
            try:
                b = api.build_checked_body(preset, 125.0, str(TMP / f"P0-125-ellipse-{rule}"), params=P, root=TMP,
                                           body_id=f"P0-125-ellipse-{rule}", cavity_mode_step=False)
            finally:
                voicing_geo.ELLIPSE_NO_OVERHANG = True
            seen[rule] = (checks_of(b)["voicing_dimensions"]["status"], b.measurements["voicing"]["window_area_mm2"],
                          b.measurements["voicing"]["window_cut"]["inward_move_removed_max_mm"], checks_of(b)["topology"]["status"])
        self.assertEqual((seen[True][0], seen[True][3]), ("pass", "pass"))
        self.assertAlmostEqual(seen[True][1] / record, 1.0, delta=0.002)
        self.assertGreater(seen[True][2], 0.05)                                 # the rule did act on this window
        self.assertEqual(seen[False][0], "fail")
        self.assertLess(seen[False][1] / record, 0.99)

    def test_no_preset_uses_an_experimental_setting(self):
        from ocarina_addon import voicing_geo
        for name, preset in presets.load_presets().items():
            self.assertEqual(voicing_geo.options_from(preset), {}, name)        # so every stage body has the build of the rules
            self.assertEqual(voicing_geo.record_overrides(preset, self.v), {}, name)
        # a prototype setting that is not in the hash is separate from the build fields, and a report names it
        self.assertEqual(voicing_geo.options_from(dict(shelf_land_mm=1.0, window_cut="fan")), {"shelf_land_mm": 1.0})
        self.assertEqual(voicing_geo.record_overrides(dict(window_cut="fan"), self.v), {"window_cut": "fan", "shelf_angle_deg": 0.0})
        self.assertNotIn("not in the voicing hash", report.body_report(self.body, 1.0, ""))
        frame = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
        with self.assertRaises(ValueError):
            voicing_geo.build(self.v, frame, cut_style="scoop")
        with self.assertRaises(ValueError):                                     # the ellipse cut is made for the teardrop
            voicing_geo.build(K.voicing.make_voicing(80.0, shape="rounded_rectangle", params=P), frame)
        with self.assertRaises(ValueError):
            voicing_geo.build(self.v, frame, cut_style="fan", shelf_angle_deg=30.0)   # a shelf needs the cone or the ellipse cut
        with self.assertRaises(ValueError):
            voicing_geo.build(self.v, frame, stub_style="horn")


class TestOutsideKeepout(unittest.TestCase):
    """The outside keep-out of the voicing record (45 degrees): no plastic inside the flare that opens from the window
    rim at the outer face. Until 2026-11-18 the check counted everything above the outer face."""

    @classmethod
    def setUpClass(cls):
        import types
        cls.v = K.sizing.size_body(80.0, params=P).voicing
        frame = (np.zeros(3), np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0]))
        cls.vs = types.SimpleNamespace(frame=frame, outline=np.array(cls.v.outline_mm(1.5)))

    def wedge(self, rise_deg, start_behind_exit_mm=0.5, length_mm=20.0):
        """A ramp behind the windway exit that rises at rise_deg from the outer face, in the voicing frame."""
        L, wall = self.v.window_length_mm, self.v.wall_at_window_mm
        x0 = -L - start_behind_exit_mm                       # voicing x: the exit is at -L
        x1, h = x0 - length_mm, length_mm * math.tan(math.radians(rise_deg))
        V = np.array([[x0, -6, wall], [x0, 6, wall], [x1, -6, wall], [x1, 6, wall], [x1, -6, wall + h], [x1, 6, wall + h]], float)
        F = np.array([[0, 1, 3], [0, 3, 2], [2, 3, 5], [2, 5, 4], [0, 4, 5], [0, 5, 1], [0, 2, 4], [1, 5, 3]])
        return V, F

    def test_a_shallow_rise_is_outside_the_flare_and_a_steep_one_is_inside(self):
        shallow = checks_geo.measure_keepout_outside(*self.wedge(30.0), self.vs, self.v)
        self.assertGreater(shallow["points_above_outer_face"], 0)
        self.assertEqual(shallow["flare_violations"], 0)
        self.assertAlmostEqual(shallow["flare_steepest_deg"], 30.0, delta=1.0)
        steep = checks_geo.measure_keepout_outside(*self.wedge(60.0), self.vs, self.v)
        self.assertGreater(steep["flare_violations"], 0)
        self.assertGreater(steep["flare_steepest_deg"], 45.0)
        self.assertEqual(steep["flare_limit_deg"], 45.0)

    def test_plastic_over_the_window_is_always_inside(self):
        L, wall = self.v.window_length_mm, self.v.wall_at_window_mm
        V = np.array([[-0.5 * L, 0.0, wall + 0.5], [-0.5 * L + 1, 0.0, wall + 0.5], [-0.5 * L, 1.0, wall + 0.5]])
        m = checks_geo.measure_keepout_outside(V, np.array([[0, 1, 2]]), self.vs, self.v)
        self.assertEqual(m["flare_violations"], m["points_above_outer_face"])
        self.assertAlmostEqual(m["flare_steepest_deg"], 90.0, delta=0.01)

    def test_nothing_above_the_outer_face(self):
        V, F = self.wedge(30.0)
        V[:, 2] -= 30.0
        m = checks_geo.measure_keepout_outside(V, F, self.vs, self.v)
        self.assertEqual((m["points_above_outer_face"], m["flare_violations"], m["flare_steepest_deg"]), (0, 0, 0.0))


if __name__ == "__main__":
    unittest.main()
