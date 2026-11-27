"""Plain-Python tests of the cavity-mode desk check: ocarina_addon/cavity_mode.py (standard library) and
ocarina_addon/cavity_mode_solver.py (numpy and scipy; those tests are skipped when scipy is missing).
"""
import json
import math
import pathlib
import struct
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ocarina_addon import cavity_mode  # noqa: E402

try:
    import numpy as np
    sys.path.insert(0, str(ROOT / "ocarina_addon"))
    import cavity_mode_solver as solver                 # a stand-alone file: imported as a plain module
except Exception:                                       # noqa: BLE001
    solver = None

C = 347.3
F6 = 1396.91


def write_box_stl(path, lx, ly, lz):
    """A closed box as a binary STL (12 triangles, outward normals)."""
    v = [(x, y, z) for x in (0.0, lx) for y in (0.0, ly) for z in (0.0, lz)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    tris = [(q[0], q[1], q[2]) for q in quads] + [(q[0], q[2], q[3]) for q in quads]
    with open(path, "wb") as fh:
        fh.write(b"test box".ljust(80, b" "))
        fh.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            fh.write(struct.pack("<12fH", 0.0, 0.0, 0.0, *v[a], *v[b], *v[c], 0))


class TestVerdict(unittest.TestCase):
    def test_limits(self):
        self.assertEqual(cavity_mode.verdict(1.63), "pass")
        self.assertEqual(cavity_mode.verdict(1.30), "pass")
        self.assertEqual(cavity_mode.verdict(1.2999), "needs_fem")
        self.assertEqual(cavity_mode.verdict(1.00), "needs_fem")
        self.assertEqual(cavity_mode.verdict(0.9999), "fail")
        self.assertEqual(cavity_mode.verdict(1.2, margin=1.0, fem_margin=1.1), "pass")

    def test_result_file_name(self):
        self.assertEqual(cavity_mode.result_path("out/P1-80/P1-80_air_capped.stl").name, "P1-80_cavity_mode.json")
        self.assertEqual(cavity_mode.result_path("some/air.stl").name, "air_cavity_mode.json")

    def test_no_solver_is_reported_and_never_a_pass(self):
        saved, saved_candidates = cavity_mode._python, cavity_mode._candidates
        try:
            cavity_mode._python = None
            cavity_mode._candidates = lambda: []
            res = cavity_mode.run("nothing.stl", F6, C)
            self.assertIs(res["computed"], False)
            self.assertIn("no Python with numpy and scipy", res["reason"])
            self.assertNotIn("ratio", res)
            cavity_mode._python = None
            cavity_mode._candidates = lambda: [str(ROOT / "no_such_python.exe")]
            self.assertIs(cavity_mode.run("nothing.stl", F6, C)["computed"], False)
        finally:
            cavity_mode._python, cavity_mode._candidates = saved, saved_candidates

    def test_the_interpreter_that_runs_this_test_is_not_a_candidate(self):
        import os
        own = os.path.normcase(os.path.abspath(sys.executable))
        self.assertNotIn(own, [os.path.normcase(os.path.abspath(p)) for p in cavity_mode._candidates()])


@unittest.skipIf(solver is None, "numpy or scipy is missing")
class TestSolver(unittest.TestCase):
    def test_box_is_exact(self):
        f, _, _ = solver.modes_of_mask(np.ones((60, 24, 18), dtype=bool), 1.0, k=2, c=C)
        self.assertAlmostEqual(f[0] / (C / (2 * 0.060)), 1.0, delta=5e-4)           # first mode of a 60 mm box: c / (2 L)
        self.assertAlmostEqual(f[1] / (C / 0.060), 1.0, delta=2e-3)                 # second: the next mode along the length

    def test_a_cell_joined_only_at_an_edge_is_left_out(self):
        # a rounded hole rim left such cells on a 1.5 mm grid, and each one read as a second zero mode ("0 Hz")
        m = np.zeros((62, 24, 18), dtype=bool)
        m[:60] = True
        m[61, 0, 0] = True                               # touches the box at an edge only, not at a face
        f, _, _ = solver.modes_of_mask(m, 1.0, k=2, c=C)
        self.assertAlmostEqual(f[0] / (C / (2 * 0.060)), 1.0, delta=5e-4)

    def test_sphere_is_one_percent_low(self):
        r, h = 20.0, 1.0                                 # the tool's self-test uses 25 mm and finds -1.0 %
        g = np.arange(-r + 0.5 * h, r, h)
        X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
        f, _, _ = solver.modes_of_mask(X * X + Y * Y + Z * Z < r * r, h, k=2, c=C)
        exact = 2.0816 * C / (2 * math.pi * r * 1e-3)
        self.assertLess(f[0] / exact, 1.0)               # a staircase wall makes the cavity a little "longer"
        self.assertGreater(f[0] / exact, 0.975)

    def test_voxelize_a_box_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "box.stl"
            write_box_stl(p, 90.0, 30.0, 21.0)
            mask, volume, size = solver.voxelize(p, 1.5)
            self.assertAlmostEqual(volume, 90.0 * 30.0 * 21.0, delta=1e-3)
            self.assertEqual(mask.shape, (60, 20, 14))
            self.assertTrue(mask.all())
            res = solver.first_mode(p, C, grids=(1.5, 3.0))
            self.assertAlmostEqual(res["f1_hz"] / (C / (2 * 0.090)), 1.0, delta=1e-3)
            self.assertEqual([g["grid_mm"] for g in res["grids"]], [1.5, 3.0])
            self.assertAlmostEqual(res["voxel_cm3"], 56.7, delta=1e-6)

    def test_the_tool_uses_the_same_functions(self):
        """tools/cavity_modes_fd.py must import the method from the add-on's solver file, not carry a copy."""
        text = (ROOT / "tools" / "cavity_modes_fd.py").read_text(encoding="utf-8")
        self.assertIn("from cavity_mode_solver import modes_of_mask, voxelize", text)
        self.assertNotIn("def modes_of_mask", text)
        self.assertNotIn("def voxelize", text)


class TestRunInASecondProcess(unittest.TestCase):
    def test_run_on_a_box(self):
        exe, note = cavity_mode.find_python(refresh=True)
        if exe is None:
            self.skipTest(note)
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "box_air_capped.stl"
            write_box_stl(p, 120.0, 30.0, 24.0)
            res = cavity_mode.run(p, F6, C)
            self.assertIs(res["computed"], True, res)
            self.assertAlmostEqual(res["f1_hz"] / (C / (2 * 0.120)), 1.0, delta=1e-3)
            self.assertAlmostEqual(res["ratio"], res["f1_hz"] / F6, places=9)
            self.assertEqual(cavity_mode.verdict(res["ratio"]), "needs_fem")          # a 120 mm box: 1.04 x F6
            saved = json.loads((pathlib.Path(tmp) / "box_cavity_mode.json").read_text(encoding="utf-8"))
            self.assertAlmostEqual(saved["f1_hz"], res["f1_hz"])
            self.assertEqual(res["grid_mm"], cavity_mode.GRIDS_MM[0])

    def test_a_broken_file_is_reported(self):
        exe, note = cavity_mode.find_python()
        if exe is None:
            self.skipTest(note)
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "broken_air_capped.stl"
            p.write_bytes(b"not an stl")
            res = cavity_mode.run(p, F6, C)
            self.assertIs(res["computed"], False)
            self.assertIn("the solver stopped", res["reason"])


class TestReferenceTable(unittest.TestCase):
    def test_the_committed_reports_agree_with_the_reference_table(self):
        """Acceptance of C4b: the add-on's check is within 2 % of addon_checks/cavity_modes_fd.md (P1-80 1.63, P2-80 1.40)."""
        table = (ROOT / "addon_checks" / "cavity_modes_fd.md").read_text(encoding="utf-8")
        for body, expected in (("P1-80", 1.63), ("P2-80", 1.40)):
            row = [ln for ln in table.splitlines() if ln.startswith(f"| {body} |")][0]
            in_table = float(row.split("**")[1])
            self.assertAlmostEqual(in_table, expected, delta=0.005)
            report = json.loads((ROOT / "addon_checks" / f"{body}.json").read_text(encoding="utf-8"))
            check = [c for c in report["checks"] if c["name"] == "cavity_mode_computed"][0]
            self.assertEqual(check["status"], "pass")
            self.assertAlmostEqual(check["value"] / expected, 1.0, delta=0.02)
            kernel = [c for c in report["checks"] if c["name"] == "cavity_mode_c2L"][0]
            self.assertEqual(kernel["status"], "info")           # the kernel's c/(2L) decides nothing


if __name__ == "__main__":
    unittest.main()
