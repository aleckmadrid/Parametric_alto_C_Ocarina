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
    """The 20 cavities of the C3 check: P0-P3 at the mesh volumes of the 65, 80, 95, 110 and 125 cm3 bodies."""

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.failures, _ = geometry_check.measure_cavities(renders=False)

    def test_twenty_cavities_all_pass(self):
        self.assertEqual(len(self.rows), 20)
        self.assertEqual(sorted({r["preset"] for r in self.rows}), ["P0", "P1", "P2", "P3"])
        self.assertEqual(sorted({r["v0_cm3"] for r in self.rows}), [65.0, 80.0, 95.0, 110.0, 125.0])
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
        for name, doc in (("P0", 79.0), ("P1", 111.0), ("P2", 126.0), ("P3", 95.0)):
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
        self.assertAlmostEqual(e["sub1"]["dist_3d"], 9.5, delta=0.01)
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
        self.assertEqual(self.body.voicing_hash, "d1b6418b1844")
        self.assertEqual({c["name"] for c in self.body.checks if c["status"] == "fail"}, PAD_LIMITS)

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
        self.assertEqual(self.body.voicing_hash, "6aa0038008cc")
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
                         ["P0-65", "P0-80", "P0-95", "P0-125", "P1-80", "P2-80", "P3-80", "P0-80-b", "P0-80-c"])
        self.assertNotIn("P4", [b[0] for b in stages.STAGE2_BODIES])            # waits for the owner (doc 02 Q10, Q11)
        self.assertEqual(stages.STAGE1_STUBS, ["V-a", "V-b", "V-c", "V-d", "V-a-plus", "V-a-minus"])
        self.assertEqual([(p, v) for p, v, printed in stages.STAGE3_BODIES if not printed], [("P0", 110.0)])
        self.assertEqual(len(stages.STAGE3_BODIES), 8)

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
        self.assertEqual(b.measurements["holes"], [])
        self.assertEqual(b.measurements["topology"]["genus"], 1)             # the window and the windway, no holes
        self.assertFalse([x for x in b.checks if x["name"].startswith("ergo_")])
        # the same window area as V-a, another shape, another hash
        va = stub.stub_sizing("V-a", P, 25.0).voicing
        self.assertAlmostEqual(b.sizing.voicing.window_area_mm2, va.window_area_mm2, places=6)
        self.assertNotEqual(b.sizing.voicing.version_hash, va.version_hash)
        self.assertEqual(va.version_hash, K.sizing.size_body(80.0, params=P).voicing.version_hash)
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


if __name__ == "__main__":
    unittest.main()
