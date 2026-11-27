"""Plain-Python test of tools/exit_corner_plastic.py: the known thickness on a small made-up mesh (no Blender)."""
import math
import pathlib
import re
import sys
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import exit_corner_plastic as ecp  # noqa: E402


def box(x0, x1, y0, y1, z0, z1):
    """A closed box, its triangles facing out."""
    V = np.array([[x, y, z] for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)], float)
    quads = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    return V, np.array([t for a, b, c, d in quads for t in ((a, b, c), (a, c, d))])


class TestExitCornerPlastic(unittest.TestCase):
    def test_the_known_thickness_of_a_made_up_windway(self):
        # in the voicing frame: a roof plate 0.35 mm thick over a windway 1.2 mm high, a floor plate 0.7 mm thick under it
        L, half, gap = 9.65, 4.4, 1.2
        roof, floor = box(-2.0, 6.0, -6.0, 6.0, 2.2, 2.55), box(-2.0, 6.0, -6.0, 6.0, 0.3, 1.0)
        Q = np.vstack([roof[0], floor[0]])
        F = np.vstack([roof[1], floor[1] + len(roof[0])])
        # placed in a body by a turned frame, as the voicing sits on a cavity
        a, b = math.radians(25.0), math.radians(-40.0)
        Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
        Rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
        fx, fy, fz = (Rz @ Rx).T
        o = np.array([12.0, -30.0, 5.0])
        V = o + (Q[:, :1] - L) * fx + Q[:, 1:2] * fy + Q[:, 2:] * fz
        r = ecp.measure(V, F, (o, fx, fy, fz), L, half, gap)
        self.assertEqual(r["odd_lines"], 0)
        self.assertAlmostEqual(r["roof"]["thinnest_mm"], 0.35, delta=1e-6)
        self.assertAlmostEqual(r["roof"]["along_z_least_mm"], 0.35, delta=1e-6)
        self.assertAlmostEqual(r["roof"]["at"][2], 2.2, delta=1e-6)
        self.assertEqual(r["roof"]["edge_exits"], 0)
        self.assertAlmostEqual(r["floor"]["thinnest_mm"], 0.7, delta=1e-6)
        self.assertGreater(r["roof"]["points"], 10000)
        # the frame's constants are the add-on's (cavity.py and voicing_geo.py need Blender to import)
        src = (ROOT / "ocarina_addon" / "cavity.py").read_text(encoding="utf-8")
        self.assertEqual((ecp.RES_U, ecp.RES_V), tuple(int(re.search(rf"^{k} = (\d+)", src, re.M).group(1)) for k in ("RES_U", "RES_V")))
        src = (ROOT / "ocarina_addon" / "voicing_geo.py").read_text(encoding="utf-8")
        self.assertEqual(ecp.CLEARANCE_MM, float(re.search(r"^POCKET_CLEARANCE_MM = ([\d.]+)", src, re.M).group(1)))


if __name__ == "__main__":
    unittest.main()
