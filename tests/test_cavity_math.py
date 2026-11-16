"""Plain-Python tests of ocarina_addon/cavity_math.py (no Blender).

    python -m unittest discover -s tests
"""
import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ocarina_addon import cavity_math as cm, presets  # noqa: E402


def dist(a, b):
    return math.dist(a, b)


class TestSpline(unittest.TestCase):
    def test_passes_through_the_stations(self):
        vals = [0.46, 0.49, 0.47, 0.40, 0.33, 0.27, 0.22]
        for i, v in enumerate(vals):
            self.assertAlmostEqual(cm.catmull_rom(vals, i / 6.0), v, places=12)

    def test_constant_stations_give_a_constant(self):
        for t in (0.0, 0.123, 0.5, 0.77, 1.0):
            self.assertAlmostEqual(cm.catmull_rom([0.3] * 7, t), 0.3, places=12)

    def test_clamped_outside_0_1(self):
        vals = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        self.assertAlmostEqual(cm.catmull_rom(vals, -1.0), 1.0)
        self.assertAlmostEqual(cm.catmull_rom(vals, 2.0), 7.0)

    def test_superellipse_area_factor(self):
        self.assertAlmostEqual(cm.superellipse_area_factor(2.0), math.pi, places=12)
        self.assertGreater(cm.superellipse_area_factor(2.2), math.pi)          # boxier section, more area
        self.assertLess(cm.superellipse_area_factor(2.2), 4.0)


class TestEllipsoid(unittest.TestCase):
    """P0 has equal station values, so it is an exact ellipsoid 2.2 : 1.5 : 1."""

    def setUp(self):
        self.pre = presets.get_preset("P0")
        self.cav = cm.Cavity.from_preset(self.pre)

    def test_volume_is_the_ellipsoid_formula(self):
        L = cm.LREF
        W, H = L * self.pre["width"][0], L * self.pre["height"][0]
        self.assertAlmostEqual(self.cav.volume_mm3() / (math.pi / 6.0 * L * W * H), 1.0, places=5)
        self.assertAlmostEqual(W / H, 1.5, places=4)
        self.assertAlmostEqual(L / H, 2.2, places=4)

    def test_scale_for_volume(self):
        target = 78.11e3
        s = self.cav.scale_for_volume(target)
        scaled = cm.Cavity.from_preset(self.pre, scale=s)
        self.assertAlmostEqual(scaled.volume_mm3() / target, 1.0, places=9)
        self.assertAlmostEqual(scaled.length_mm, cm.LREF * s)
        self.assertAlmostEqual(scaled.length_mm, 78.4, delta=0.3)              # doc 04: 79 mm at 80 cm3 of cavity

    def test_width_and_height(self):
        w, h = self.cav.max_width_height_mm()
        self.assertAlmostEqual(w, cm.LREF * self.pre["width"][0], places=3)
        self.assertAlmostEqual(h, cm.LREF * self.pre["height"][0], places=3)

    def test_points_lie_on_the_ellipsoid(self):
        a, b, c = 50.0, 50.0 * self.pre["width"][0], 50.0 * self.pre["height"][0]
        o = self.cav._port_raw
        for theta in (0.4, 1.1, 1.9, 2.7):
            for phi in (0.3, 1.2, 2.5, 4.0, 5.5):
                x, y, z = (p + q for p, q in zip(self.cav.point(theta, phi), o))
                self.assertAlmostEqual((x / a) ** 2 + (y / b) ** 2 + (z / c) ** 2, 1.0, places=9)


class TestPortAndFrames(unittest.TestCase):
    def test_the_port_is_the_origin_at_every_scale(self):
        for name in ("P0", "P1", "P2", "P3", "S0"):
            for scale in (0.4, 0.78, 1.3):
                cav = cm.Cavity.from_preset(presets.get_preset(name), scale=scale)
                self.assertLess(dist(cav.point(cav.port_theta, cav.port_phi), (0, 0, 0)), 1e-12, name)

    def test_the_port_is_on_the_lower_player_side(self):
        for name in ("P0", "P1", "P2", "P3"):
            cav = cm.Cavity.from_preset(presets.get_preset(name))
            n = cav.normal(cav.port_theta, cav.port_phi)
            self.assertLess(n[1], 0.0, name)        # toward the player (-Y)
            self.assertLess(n[2], 0.0, name)        # toward the thumb side (-Z)

    def test_snap_port_to_grid(self):
        cav = cm.Cavity.from_preset(presets.get_preset("P1"))
        cav.snap_port_to_grid(129, 128)
        self.assertAlmostEqual(cav.port_theta / math.pi * 128, round(cav.port_theta / math.pi * 128), places=9)
        self.assertAlmostEqual(cav.port_phi / (2 * math.pi) * 128, round(cav.port_phi / (2 * math.pi) * 128), places=9)
        self.assertLess(dist(cav.point(cav.port_theta, cav.port_phi), (0, 0, 0)), 1e-12)
        self.assertAlmostEqual(cav.port_u, 0.36, delta=0.01)

    def test_normals_are_unit_and_outward(self):
        for name in ("P0", "P1", "P2", "P3"):
            cav = cm.Cavity.from_preset(presets.get_preset(name), scale=0.9)
            for theta in (0.5, 1.4, 2.4):
                for phi in (0.2, 1.57, 3.3, 4.7):
                    n = cav.normal(theta, phi)
                    self.assertAlmostEqual(math.sqrt(sum(c * c for c in n)), 1.0, places=9)
                    p = cav.point(theta, phi)
                    spine = cav.to_body(cav.spine_raw((1 - math.cos(theta)) / 2)[0])
                    self.assertGreater(sum(nc * (pc - sc) for nc, pc, sc in zip(n, p, spine)), 0.0)
        top = cm.Cavity.from_preset(presets.get_preset("P0")).normal(0.5 * math.pi, 0.5 * math.pi)
        self.assertAlmostEqual(top[2], 1.0, places=6)        # the top of the egg looks straight up

    def test_port_frame_is_orthonormal_and_the_jet_runs_toward_the_bottom(self):
        cav = cm.Cavity.from_preset(presets.get_preset("P2"), scale=0.8)
        x, y, z = cav.port_frame()
        dot = lambda a, b: sum(p * q for p, q in zip(a, b))
        for v in (x, y, z):
            self.assertAlmostEqual(dot(v, v), 1.0, places=9)
        self.assertAlmostEqual(dot(x, y), 0.0, places=9)
        self.assertAlmostEqual(dot(x, z), 0.0, places=9)
        self.assertAlmostEqual(dot(y, z), 0.0, places=9)
        n = cav.normal(cav.port_theta, cav.port_phi)
        self.assertAlmostEqual(dot(z, n), 1.0, places=9)
        self.assertGreater(x[1], 0.0)        # the jet leaves the player's side (toward +Y, away from the player)
        self.assertLess(x[2], 0.0)           # and runs toward the bottom of the body

    def test_bent_spine_moves_both_ends_away_from_the_player(self):
        cav = cm.Cavity.from_preset(presets.get_preset("P3"))
        mid = cav.spine_raw(0.5)[0]
        self.assertGreater(cav.spine_raw(0.0)[0][1], mid[1])
        self.assertGreater(cav.spine_raw(1.0)[0][1], mid[1])
        straight = cm.Cavity.from_preset(presets.get_preset("P1"))
        self.assertEqual(straight.spine_raw(0.0)[0][1], 0.0)


class TestArcLengths(unittest.TestCase):
    def setUp(self):
        self.cav = cm.Cavity.from_preset(presets.get_preset("P1"), scale=1.1)

    def test_meridian_arc_and_its_inverse(self):
        top = 0.5 * math.pi
        t0 = 1.2
        for s in (-30.0, -5.0, 12.0, 40.0):
            t1 = self.cav.theta_at_meridian_arc(t0, s, top)
            self.assertAlmostEqual(self.cav.meridian_arc(t0, t1, top), s, delta=1e-3)
            self.assertEqual(t1 > t0, s > 0)

    def test_section_arc_and_its_inverse(self):
        theta, top = 1.3, 0.5 * math.pi
        for w in (-12.0, -3.0, 4.0, 15.0):
            phi = self.cav.phi_at_section_arc(theta, top, w)
            self.assertAlmostEqual(self.cav.section_arc(theta, top, phi), w, delta=1e-3)

    def test_too_long_an_arc_is_an_error(self):
        with self.assertRaises(ValueError):
            self.cav.theta_at_meridian_arc(1.2, 500.0, 0.5 * math.pi)
        with self.assertRaises(ValueError):
            self.cav.phi_at_section_arc(1.3, 0.5 * math.pi, 500.0)

    def test_circle_section_arc(self):
        ball = cm.Cavity([1.0] * 7, [1.0] * 7, 2.0, 0.0, 0.5, 45.0, 1.0)        # width = length: a sphere of radius 50
        self.assertAlmostEqual(ball.section_arc(0.5 * math.pi, 0.0, math.pi), math.pi * 50.0, delta=2e-3)
        self.assertAlmostEqual(ball.meridian_arc(0.5 * math.pi, 0.5 * math.pi + 0.4, 0.5 * math.pi), 0.4 * 50.0, delta=2e-3)

    def test_wrong_station_count(self):
        with self.assertRaises(ValueError):
            cm.Cavity([0.5] * 6, [0.5] * 7)


if __name__ == "__main__":
    unittest.main()
