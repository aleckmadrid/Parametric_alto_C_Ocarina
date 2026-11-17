"""Finite-volume acoustic network ("cell network") for vessel-flute cavities.

The single-volume Helmholtz model of kernel/ocarina_kernel.py assumes the
pressure is uniform in the chamber. Internal walls, slits, pockets and long
side passages break that assumption. Here the voxel cavity is cut into compact
cells (geodesic Voronoi of a lattice of seeds, so no cell crosses a wall);
neighbouring cells are joined by the inertance of their shared face, and every
open hole (and the window) is a lumped radiation conductance from its cell(s)
to the outside (p = 0):

    (Lap(G_ab) + diag(G_open)) p = (omega / c)^2 diag(V) p

    G_ab   = A_ab / |x_a - x_b|      shared face area / centroid distance (mm)
    G_open = A / (t + k d_eq)        kernel conductance of a hole or window (mm)
    V      = cell air volume (mm^3)

A single compact cell reproduces f = c/(2 pi) sqrt(G_tot / V) exactly. The
lowest eigenpair is the played Helmholtz-like mode. Its shape shows how much
of the air actually takes part ("participation"), which is the measurable form
of Pure Ocarinas' volume-bypassing idea. The next eigenvalues are the cavity
(standing-wave) modes, used for the lumped-model validity check.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy import ndimage as ndi
from scipy.optimize import brentq
from skimage.segmentation import watershed

TWO_PI = 2.0 * math.pi


@dataclass
class CellNet:
    labels: np.ndarray          # cell id per voxel (0 = not cavity), cropped to `offset`
    offset: np.ndarray          # voxel index of labels[0,0,0] in the full grid
    h: float
    V: np.ndarray               # (n,) cell volume mm^3
    X: np.ndarray               # (n,3) cell centroid, world mm
    edges: np.ndarray           # (m,2) cell index pairs
    A: np.ndarray               # (m,) shared face area mm^2
    G: np.ndarray               # (m,) face conductance mm
    openings: dict = field(default_factory=dict)   # name -> (cells, weights)

    @property
    def n(self):
        return len(self.V)

    def laplacian(self):
        i, j = self.edges[:, 0], self.edges[:, 1]
        W = sp.coo_matrix((np.r_[self.G, self.G], (np.r_[i, j], np.r_[j, i])), shape=(self.n, self.n)).tocsr()
        d = np.asarray(W.sum(axis=1)).ravel()
        return sp.diags(d) - W


def build_cells(cav, grid_origin, h, cell_mm=4.0):
    """Cut a boolean cavity into connected cells about cell_mm across."""
    nz = np.argwhere(cav)
    lo = nz.min(0)
    hi = nz.max(0) + 1
    sl = tuple(slice(a, b) for a, b in zip(lo, hi))
    c = cav[sl]
    # keep the largest face-connected piece: islands that touch it only along an edge or
    # corner would carry no flow and make the stiffness matrix singular
    comp0, n0 = ndi.label(c)
    if n0 > 1:
        sizes0 = np.bincount(comp0.ravel())[1:]
        c = comp0 == (1 + int(np.argmax(sizes0)))
    step = max(1, int(round(cell_mm / h)))
    markers = np.zeros(c.shape, np.int32)
    # stagger the lattice to half-step offsets so thin layers still get seeds
    off = step // 2
    pts = np.argwhere(c[off::step, off::step, off::step]) * step + off
    markers[tuple(pts.T)] = np.arange(1, len(pts) + 1, dtype=np.int32)
    # any connected piece of the cavity without a seed gets one
    comp, nc = ndi.label(c)
    seeded = np.unique(comp[markers > 0])
    for k in range(1, nc + 1):
        if k not in seeded:
            q = np.argwhere(comp == k)[0]
            markers[tuple(q)] = markers.max() + 1
    lab = watershed(np.zeros(c.shape, np.uint8), markers, mask=c)
    # relabel consecutively 1..n
    ids, inv = np.unique(lab, return_inverse=True)
    lab = inv.reshape(lab.shape).astype(np.int32)    # 0 stays 0 because ids[0] == 0
    n = len(ids) - 1
    flat = lab.ravel()
    V = np.bincount(flat, minlength=n + 1)[1:] * h ** 3
    X = np.zeros((n, 3))
    grids = np.indices(c.shape, sparse=True)
    for ax in range(3):
        coord = np.broadcast_to(grids[ax], c.shape).ravel()
        X[:, ax] = np.bincount(flat, weights=coord, minlength=n + 1)[1:] / np.maximum(
            np.bincount(flat, minlength=n + 1)[1:], 1)
    X = grid_origin + (X + lo) * h
    pair_counts = {}
    codes_all = []
    for ax in range(3):
        a = np.moveaxis(lab, ax, 0)
        u, v = a[:-1].ravel(), a[1:].ravel()
        m = (u > 0) & (v > 0) & (u != v)
        u, v = u[m] - 1, v[m] - 1
        lo_, hi_ = np.minimum(u, v), np.maximum(u, v)
        codes_all.append(lo_.astype(np.int64) * n + hi_)
    codes = np.concatenate(codes_all)
    uc, cnt = np.unique(codes, return_counts=True)
    edges = np.column_stack([uc // n, uc % n]).astype(np.int64)
    A = cnt * h ** 2
    dist = np.linalg.norm(X[edges[:, 0]] - X[edges[:, 1]], axis=1)
    G = A / np.maximum(dist, h)
    return CellNet(labels=lab, offset=lo, h=h, V=V, X=X, edges=edges, A=A, G=G)


def attach_opening(net: CellNet, name, voxel_idx, radius_mm=None):
    """Attach an opening to the cells that own the given full-grid voxel indices.

    radius_mm: also attach every cell within this *geodesic* distance (through
    the cell graph, so never across a wall) of the owning cells, weighted by
    volume. The kernel conductance A/(t + k d) already contains the inner end
    correction; spreading the attachment over about one hole diameter (and at
    least 1.5 cells) stops the network from adding the near-hole spreading
    inertance a second time. Validated in test_cellnet.py.
    """
    from scipy.sparse.csgraph import dijkstra
    q = np.asarray(voxel_idx) - net.offset
    ok = np.all((q >= 0) & (q < np.array(net.labels.shape)), axis=1)
    q = q[ok]
    cells = net.labels[tuple(q.T)]
    cells = cells[cells > 0] - 1
    if len(cells) == 0:
        raise ValueError(f"opening {name} touches no cell")
    own = np.unique(cells)
    if radius_mm:
        dist = np.linalg.norm(net.X[net.edges[:, 0]] - net.X[net.edges[:, 1]], axis=1)
        i, j = net.edges[:, 0], net.edges[:, 1]
        Gr = sp.coo_matrix((np.r_[dist, dist], (np.r_[i, j], np.r_[j, i])), shape=(net.n, net.n)).tocsr()
        D = dijkstra(Gr, directed=False, indices=own, limit=radius_mm, min_only=True)
        sel = np.nonzero(np.isfinite(D))[0]
        w = net.V[sel]
        net.openings[name] = (sel, w / w.sum())
    else:
        u, w = np.unique(cells, return_counts=True)
        net.openings[name] = (u, w / w.sum())


def deembed(net: CellNet, name, G_kernel):
    """Network-side conductance for an opening whose kernel conductance is G_kernel.

    The cells outside the attachment region carry the converging flow toward
    the hole, which the kernel's inner end correction already counts. For a
    hole in a wall that is the half-space spreading conductance from the
    attachment region to infinity, S = 2 pi R_eff, with R_eff the radius of the
    hemisphere that has the attachment region's volume. Returns
    1 / (1/G_kernel - 1/S), capped at 20 * G_kernel.
    """
    cells, _ = net.openings[name]
    R_eff = (3.0 * net.V[cells].sum() / (2.0 * math.pi)) ** (1.0 / 3.0)
    S = 2.0 * math.pi * R_eff
    inv = 1.0 / G_kernel - 1.0 / S
    return G_kernel * 20.0 if inv <= 0.05 / G_kernel else 1.0 / inv


def solve(net: CellNet, G_open: dict, c_mm_s: float, n_modes=3, dV_open: dict | None = None,
          dV_closed: dict | None = None):
    """Lowest modes for the given open set. G_open: name -> conductance (mm) of the open ones.

    dV_open: name -> chimney volume (mm^3) removed from the cavity when that hole is open.
    dV_closed: name -> chimney volume (mm^3) added to the hole's cells while it is closed
               (used when the bores are carved out of the cell cavity).
    Returns (freqs Hz, modes (n, n_modes) normalised so the window cell average = 1).
    """
    K = net.laplacian().tolil()
    V = net.V.copy()
    for name, G in G_open.items():
        cells, w = net.openings[name]
        for ci, wi in zip(cells, w):
            K[ci, ci] += G * wi
        if dV_open and name in dV_open:
            V[cells] = np.maximum(V[cells] - dV_open[name] * w, 0.1 * V[cells])
    if dV_closed:
        for name, dv in dV_closed.items():
            cells, w = net.openings[name]
            V[cells] = V[cells] + dv * w
    K = K.tocsc()
    M = sp.diags(V).tocsc()
    k = min(n_modes, net.n - 2)
    vals, vecs = spla.eigsh(K, k=k, M=M, sigma=0.0, which="LM")
    order = np.argsort(vals)
    vals, vecs = vals[order], vecs[:, order]
    f = c_mm_s / TWO_PI * np.sqrt(np.maximum(vals, 0.0))
    if "window" in net.openings:
        wc, ww = net.openings["window"]
        for m in range(vecs.shape[1]):
            ref = float(np.dot(vecs[wc, m], ww))
            if abs(ref) > 1e-30:
                vecs[:, m] /= ref
    return f, vecs


def participation(net: CellNet, mode, V=None):
    """How much of the air takes part in a mode.

    Returns (v_eff, bypass, pr):
      v_eff  = sum(V p) / p_bulk, with p_bulk the volume-weighted median of |p|
               (the pressure of the main body of air), mm^3
      bypass = share of the volume with |p| < 0.5 p_bulk (air that barely takes part)
      pr     = participation ratio (sum V p)^2 / (V_tot sum V p^2); 1 = uniform pressure
    The bulk reference (not the window cells) keeps the numbers meaningful when the
    window opens into a recess or behind a constriction.
    """
    V = net.V if V is None else V
    a = np.abs(mode)
    order = np.argsort(a)
    cum = np.cumsum(V[order])
    p_bulk = float(a[order][np.searchsorted(cum, 0.5 * cum[-1])])
    sgn = np.sign(np.dot(V, mode)) or 1.0
    v_eff = float(sgn * np.dot(V, mode) / p_bulk)
    bypass = float(V[a < 0.5 * p_bulk].sum() / V.sum())
    pr = float(np.dot(V, mode) ** 2 / (V.sum() * np.dot(V, mode * mode)))
    return v_eff, bypass, pr


def fit_window(net: CellNet, f0, c_mm_s, G_lo=0.05, G_hi=200.0):
    """Window conductance (mm) that puts the all-closed note at f0."""
    def err(G):
        return solve(net, {"window": G}, c_mm_s, n_modes=1)[0][0] - f0
    return brentq(err, G_lo, G_hi, xtol=1e-6)
