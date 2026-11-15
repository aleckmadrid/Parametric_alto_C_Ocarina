"""Unit tests for the kernel seed.  Run:  python -m unittest discover -s kernel -v"""
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ocarina_kernel as ok  # noqa: E402

MM = 1e-3


class TestAcoustics(unittest.TestCase):
    def test_diameter_inversion_round_trip(self):
        for d in (1.5e-3, 3e-3, 6e-3, 10e-3):
            for t in (1e-3, 3e-3, 6e-3):
                G = ok.conductance(math.pi * d * d / 4, t)
                self.assertAlmostEqual(ok.hole_diameter(G, t), d, delta=1e-12)

    def test_thin_plate_limit_is_rayleigh(self):
        # k = pi/4 and t = 0 gives the Rayleigh conductivity of a circular hole, G = d
        d = 5e-3
        self.assertAlmostEqual(ok.conductance(math.pi * d * d / 4, 0.0, math.pi / 4), d, delta=1e-15)

    def test_teardrop_limits(self):
        R = 3e-3
        stadium = ok.teardrop_area(10e-3, 2 * R, R)
        self.assertAlmostEqual(stadium, math.pi * R * R + 2 * R * (10e-3 - 2 * R), delta=1e-15)

    def test_polygon_compensation(self):
        r = 4e-3
        Rc = ok.polygon_circumradius_for_area(r, 32)
        self.assertAlmostEqual(16 * Rc * Rc * math.sin(2 * math.pi / 32), math.pi * r * r, delta=1e-15)

    def test_speed_of_sound_models_agree_for_dry_air(self):
        for T in (0.0, 20.0, 27.0, 35.0):
            self.assertAlmostEqual(ok.c_mixture(T, ok.DRY_AIR) / ok.c_air(T), 1.0, delta=1e-3)

    def test_plan_appendix_example(self):
        c = ok.c_air(27)
        Gw = 0.75 * ok.conductance(9e-3 * 5e-3, 2.5e-3)
        f = [ok.midi_f(m) for m in (72, 74, 76, 77, 79, 81, 83, 84, 86, 88)]
        V = ok.volume_for(Gw, f[0], c)
        self.assertAlmostEqual(V * 1e6, 44.0, delta=0.05)
        G9 = 4 * math.pi ** 2 * V / c ** 2 * (f[9] ** 2 - f[8] ** 2)
        self.assertAlmostEqual(ok.hole_diameter(G9, 4e-3) / MM, 8.40, delta=0.005)


class TestSolver(unittest.TestCase):
    def _design(self, chimney_volume=True):
        notes = [69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89]
        targets = [ok.midi_f(m) for m in notes]
        holes = [ok.Hole(f"h{i}", (3.0 + 0.25 * i) * MM) for i in range(12)]
        Gw = 0.9 * ok.conductance(ok.teardrop_area(8.9e-3, 6e-3, 1e-3), 3e-3)
        des = ok.solve_linear_fingering(targets, Gw, holes, c=ok.c_air(27), chimney_volume=chimney_volume)
        return des, targets

    def test_round_trip_under_0p1_cent(self):
        """Phase 0 gate: size holes, predict every fingering back, error < 0.1 cent."""
        des, targets = self._design()
        for j, ft in enumerate(targets):
            self.assertLess(abs(ok.cents(des.predict(range(j)), ft)), 0.1)

    def test_range_ratio_identity(self):
        # Without chimney volume, sum G / G_w = (f_top/f_0)^2 - 1 exactly
        des, targets = self._design(chimney_volume=False)
        ratio = sum(des.G(i) for i in range(12)) / des.G_w_eff
        self.assertAlmostEqual(ratio, (targets[-1] / targets[0]) ** 2 - 1, delta=1e-9)

    def test_uniform_scaling_law(self):
        # Scaling every length by s scales G by s and V by s^3, so f scales by 1/s
        des, targets = self._design()
        s = 1.01
        G = des.G_w_eff * s + sum(des.G(i) for i in range(5)) * s
        V = (des.V0 - sum(h.area * h.t for h in des.holes[:5])) * s ** 3
        f_scaled = ok.freq(G, V, des.c)
        self.assertAlmostEqual(f_scaled * s, des.predict(range(5)), delta=1e-9)


if __name__ == "__main__":
    unittest.main()
