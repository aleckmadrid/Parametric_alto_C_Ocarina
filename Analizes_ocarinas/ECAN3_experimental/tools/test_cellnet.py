"""Validation of the cell-network solver against closed-form cases.

    python -m unittest discover -s Analizes_ocarinas/ECAN3_experimental/tools -v
"""
import math
import unittest

import numpy as np

import cellnet as cn

C = 347.3e3   # mm/s, 27 C (kernel convention)
ATTACH = 7.0  # mm, geodesic attachment radius used by the analysis


def helmholtz(G, V):
    return C / (2 * math.pi) * math.sqrt(G / V)


def two_node(Gw, V1, Gp, V2, Gh=0.0):
    """Lowest mode of window-chamber V1, coupled by Gp to V2 that has hole Gh."""
    K = np.array([[Gw + Gp, -Gp], [-Gp, Gp + Gh]])
    M = np.diag([V1, V2])
    lam = np.linalg.eigvals(np.linalg.solve(M, K)).real
    return C / (2 * math.pi) * math.sqrt(min(lam))


def patch(mask, where):
    """Voxel indices of a small patch on the cavity surface (used as an opening)."""
    return np.argwhere(mask & where)


class TestCellNet(unittest.TestCase):
    h = 0.5

    def test_sphere_helmholtz(self):
        r = 25.0
        n = int(2 * r / self.h) + 5
        g = (np.indices((n, n, n)) - n // 2) * self.h
        cav = (g ** 2).sum(0) <= r * r
        net = cn.build_cells(cav, np.zeros(3), self.h, cell_mm=4.0)
        top = np.zeros_like(cav)
        top[n // 2 - 3:n // 2 + 4, n // 2 - 3:n // 2 + 4, :] = True
        top &= g[2] > r - 1.0
        side = np.zeros_like(cav)
        side[:, n // 2 - 3:n // 2 + 4, n // 2 - 3:n // 2 + 4] = True
        side &= g[0] > r - 1.0
        cn.attach_opening(net, "window", patch(cav, top), radius_mm=ATTACH)
        cn.attach_opening(net, "hole", patch(cav, side), radius_mm=ATTACH)
        V = net.V.sum()
        # one compact chamber must reproduce the single-volume kernel (de-embedded openings)
        for Gw, Gh in ((4.0, 0.0), (2.0, 8.0), (4.0, 9.0)):
            opn = {"window": cn.deembed(net, "window", Gw)}
            if Gh:
                opn["hole"] = cn.deembed(net, "hole", Gh)
            f = cn.solve(net, opn, C, n_modes=1)[0][0]
            self.assertLess(abs(f / helmholtz(Gw + Gh, V) - 1), 0.01, (Gw, Gh, f))

    def test_closed_tube_first_cavity_mode(self):
        L = 100.0
        cav = np.ones((int(L / self.h), 40, 40), bool)
        net = cn.build_cells(cav, np.zeros(3), self.h, cell_mm=4.0)
        end = np.zeros_like(cav)
        end[0, 18:22, 18:22] = True
        cn.attach_opening(net, "window", patch(cav, end))
        f = cn.solve(net, {"window": 1e-6}, C, n_modes=3)[0]
        self.assertLess(abs(f[1] / (C / (2 * L)) - 1), 0.01, f)

    def test_two_chambers_through_aperture(self):
        # chamber 1: 40 x 40 x 40 mm, chamber 2: 40 x 40 x 20 mm, 2 mm wall with a square aperture
        h = self.h
        nx, ny = int(40 / h), int(40 / h)
        nz1, nw, nz2 = int(40 / h), int(2 / h), int(20 / h)
        cav = np.zeros((nx, ny, nz1 + nw + nz2), bool)
        cav[:, :, :nz1] = True
        cav[:, :, nz1 + nw:] = True
        a = int(6 / h)                                  # 6 x 6 mm aperture
        cav[nx // 2 - a // 2:nx // 2 + a // 2, ny // 2 - a // 2:ny // 2 + a // 2, nz1:nz1 + nw] = True
        net = cn.build_cells(cav, np.zeros(3), h, cell_mm=3.0)
        w = np.zeros_like(cav)
        w[:4, ny // 2 - 4:ny // 2 + 4, nz1 // 2 - 4:nz1 // 2 + 4] = True
        hole = np.zeros_like(cav)
        hole[:4, ny // 2 - 4:ny // 2 + 4, -int(10 / h) - 4:-int(10 / h) + 4] = True
        cn.attach_opening(net, "window", patch(cav, w), radius_mm=ATTACH)
        cn.attach_opening(net, "hole", patch(cav, hole), radius_mm=ATTACH)
        A = (a * h) ** 2
        d = 2 * math.sqrt(A / math.pi)
        Gp = A / (2.0 + 0.8 * d)                       # kernel conductance of the aperture
        V1, V2 = 40 * 40 * 40.0, 40 * 40 * 20.0
        for Gw, Gh in ((3.0, 0.0), (3.0, 4.0), (3.0, 9.0)):
            opn = {"window": cn.deembed(net, "window", Gw)}
            if Gh:
                opn["hole"] = cn.deembed(net, "hole", Gh)
            f = cn.solve(net, opn, C, n_modes=1)[0][0]
            ref = two_node(Gw, V1, Gp, V2, Gh)
            # the aperture inertance is resolved by the cells, not by a formula: allow 6 %
            self.assertLess(abs(f / ref - 1), 0.06, (Gw, Gh, f, ref))


if __name__ == "__main__":
    unittest.main()
