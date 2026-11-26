"""The round bowl's maths on grids and rings (numpy only, no Blender): the height field of the bowl and its floors, the
flow's length and its cap, the rim's quintic, and the throat's section areas. bowl_cut.py builds the cutter with these.
The numbers come from the voicing record (kernel voicing.BOWL_BUILD); the constants below are part of the cut.
"""
from __future__ import annotations

import warnings

import numpy as np

UNDER_SOFT_MM = 0.4            # smooth maximum of the floors (k)
CHAMBER_MAX_MM, CHAMBER_SIG_MM = 0.6, 0.4    # the chamber taken at its highest within 0.6 mm, then softened 0.4 mm
ROOF_MARGIN_MM, ROOF_SIG_MM, ROOF_SOFT_MM = 0.15, 1.5, 0.3   # the bowl made shallower over the windway, smoothly
TOP_SIG_MM, TOP_GAP_MM, TOP_SOFT_MM, TOP_X0_MM, TOP_FADE_MM = 0.6, 0.05, 0.15, 4.4, 2.0   # above the upper edge: B under the outside
FLOW_SMOOTH_PASSES = 8         # the flow's length smoothed along the ring, under its cap


def smooth5(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


def quintic(g0, d0, c0, t):
    """Quintic on t in [0, 1] with value g0, slope d0, curvature c0 at 0 and value, slope and curvature 0 at 1."""
    t2, t3, t4, t5 = t * t, t ** 3, t ** 4, t ** 5
    h0 = 1 - 10 * t3 + 15 * t4 - 6 * t5
    h1 = t - 6 * t3 + 8 * t4 - 3 * t5
    h2 = 0.5 * t2 - 1.5 * t3 + 1.5 * t4 - 0.5 * t5
    return g0 * h0 + d0 * h1 + c0 * h2


def gauss(Z, sigma, h):
    """Gaussian smoothing of a grid with holes (normalised convolution); the holes stay holes."""
    if sigma <= 0:
        return Z.copy()
    r = int(np.ceil(3.0 * sigma / h))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) * h / sigma) ** 2)
    k /= k.sum()
    m = np.isfinite(Z).astype(float)
    A = np.where(np.isfinite(Z), Z, 0.0)

    def conv(M):
        M = np.apply_along_axis(lambda row: np.convolve(row, k, mode="same"), 1, M)
        return np.apply_along_axis(lambda col: np.convolve(col, k, mode="same"), 0, M)

    out = conv(A) / np.maximum(conv(m), 1e-9)
    return np.where(np.isfinite(Z), out, np.nan)


def fill(Z):
    """Holes of a grid filled from their neighbours (a few rings outward), the rest with the lowest value."""
    Z = Z.copy()
    for _ in range(40):
        bad = ~np.isfinite(Z)
        if not bad.any():
            break
        P = np.pad(Z, 1, constant_values=np.nan)
        nb = np.stack([P[:-2, 1:-1], P[2:, 1:-1], P[1:-1, :-2], P[1:-1, 2:]])
        with np.errstate(invalid="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)              # a point with no finite neighbour yet
            avg = np.nanmean(np.where(np.isfinite(nb), nb, np.nan), axis=0)
        Z = np.where(bad & np.isfinite(avg), avg, Z)
    return np.where(np.isfinite(Z), Z, np.nanmin(Z))


def interp(Z, xs, ys, x, y):
    """Bilinear value of the grid Z (rows y, columns x, square cells) at (x, y)."""
    h = xs[1] - xs[0]
    gx = np.clip((np.asarray(x) - xs[0]) / h, 0.0, len(xs) - 1.000001)
    gy = np.clip((np.asarray(y) - ys[0]) / h, 0.0, len(ys) - 1.000001)
    i0, j0 = np.floor(gx).astype(int), np.floor(gy).astype(int)
    tx, ty = gx - i0, gy - j0
    return ((1 - ty) * ((1 - tx) * Z[j0, i0] + tx * Z[j0, i0 + 1]) + ty * ((1 - tx) * Z[j0 + 1, i0] + tx * Z[j0 + 1, i0 + 1]))


def smax(a, b, k):
    """Smooth maximum: never below max(a, b), at most k / 2 above it where a = b."""
    return 0.5 * (a + b + np.sqrt((a - b) ** 2 + k * k)) if k > 0 else np.maximum(a, b)


def inside(poly, x, y):
    """Points (x, y) inside the closed polygon poly (n, 2): even-odd rule."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ins = np.zeros(x.shape, bool)
    px, py = poly[:, 0], poly[:, 1]
    qx, qy = np.roll(px, -1), np.roll(py, -1)
    for a, b, c, d in zip(px, py, qx, qy):
        cond = (b > y) != (d > y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xc = a + (y - b) * (c - a) / (d - b)
        ins ^= cond & (x < xc)
    return ins


def ellipse_reach(P0, u, a, xc, b):
    """Distance from each point P0 (n, 2) along the unit direction u to the ellipse (centre (xc, 0), half axes a, b);
    0 where P0 is outside it."""
    def f(p):
        return np.sqrt(((p[:, 0] - xc) / a) ** 2 + (p[:, 1] / b) ** 2)

    ins = f(P0) < 1.0
    lo, hi = np.zeros(len(P0)), np.full(len(P0), 2.0 * max(a, b))
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        ok = f(P0 + mid[:, None] * u) < 1.0
        lo, hi = np.where(ok, mid, lo), np.where(ok, hi, mid)
    return np.where(ins, lo, 0.0)


def bowl_field(S, C, xs, ys, v, roof_exit_z: float, windway_pitch_deg: float, windway_width_mm: float):
    """The bowl's surface B over the grid (rows ys, columns xs; voicing frame, xw from the windway exit, z from the
    window's inner plane): B = S smoothed - D ((1 - rho^p)+)^q, made shallower over the windway, then never under
    bowl_under_mm over the chamber C (taken at its highest within CHAMBER_MAX_MM) nor bowl_roof_mm over the windway's
    roof, and above the window's upper edge held just under the outside S. S and C have no holes (fill). v: the
    voicing record (its bowl fields). Returns B, rho (1 on the outline), the windway roof's height zr and its strip."""
    h = float(v.bowl_grid_mm)
    X, Y = np.meshgrid(xs, ys)
    Ss = gauss(S, float(v.bowl_smooth_mm), h)
    D, p_, q_ = float(v.bowl_depth_mm), float(v.bowl_floor_exponent), float(v.bowl_rim_exponent)
    a_, b_, xc = float(v.bowl_half_length_mm), float(v.bowl_half_width_mm), float(v.bowl_centre_xw_mm)
    rho = np.sqrt(((X - xc) / a_) ** 2 + (Y / b_) ** 2)
    d = D * np.clip(1.0 - rho ** p_, 0.0, None) ** q_
    roof = float(v.bowl_roof_mm)
    tan_p = np.tan(np.radians(float(windway_pitch_deg)))
    zr0 = float(roof_exit_z) + np.maximum(-X, 0.0) * tan_p
    hw0 = 0.5 * float(windway_width_mm) + 1.5
    st0 = smooth5((hw0 + 3.0 - np.abs(Y)) / 3.0) * smooth5((2.5 - X) / 2.5)
    d_lim = np.maximum(Ss - (zr0 + roof + ROOF_MARGIN_MM), 0.0) + 10.0 * (1.0 - st0)
    d_lim = gauss(d_lim, ROOF_SIG_MM, h)
    d = 0.5 * (d + d_lim - np.sqrt((d - d_lim) ** 2 + ROOF_SOFT_MM * ROOF_SOFT_MM))          # smooth minimum
    d = np.maximum(d, 0.0)
    B = Ss - d
    Cd = C.copy()
    rr = max(int(round(CHAMBER_MAX_MM / h)), 1)
    for dj in range(-rr, rr + 1):
        for di in range(-rr, rr + 1):
            Cd = np.maximum(Cd, np.roll(np.roll(C, dj, axis=0), di, axis=1))
    B = smax(B, gauss(Cd, CHAMBER_SIG_MM, h) + float(v.bowl_under_mm), UNDER_SOFT_MM)
    zr = float(roof_exit_z) + np.maximum(-X, 0.0) * tan_p
    strip = smooth5((hw0 + 2.5 - np.abs(Y)) / 2.5) * smooth5((2.0 - X) / 2.0)
    B = np.where(strip > 0, smax(B, zr + roof - 10.0 * (1.0 - strip), UNDER_SOFT_MM), B)
    tgt = gauss(S, TOP_SIG_MM, h) - TOP_GAP_MM
    Bm = 0.5 * (B + tgt - np.sqrt((B - tgt) ** 2 + TOP_SOFT_MM * TOP_SOFT_MM))
    Wt = smooth5((TOP_X0_MM - X) / TOP_FADE_MM)
    B = B + Wt * np.minimum(Bm - B, 0.0)
    B = np.where(strip > 0, smax(B, zr + roof - 10.0 * (1.0 - strip), UNDER_SOFT_MM), B)
    return B, rho, zr, strip


def flow_out(reach, flow_out_mm: float, cap: float):
    """The round-over's length out over the bowl at each point of the hole's edge: flow_out_mm, but never more than the
    share `cap` of the way to the outline (`reach`), smoothed along the ring under that cap."""
    out = np.minimum(max(float(flow_out_mm), 0.05), cap * reach)
    for _ in range(FLOW_SMOOTH_PASSES):
        out = np.minimum((np.roll(out, 1) + 2.0 * out + np.roll(out, -1)) / 4.0, cap * reach)
    return np.maximum(out, 0.05)


def throat_areas(rings, z_levels) -> np.ndarray:
    """Area (mm^2) of the opening at each height of z_levels, from a stack of rings (each (n, 3), the same n; voicing
    frame): along each column of the stack, the point where it first reaches the height (the last ring's point if it
    never does); the section is the polygon of those points. Up to the hole's edge that is the window's own opening;
    above it the opening runs out into the bowl."""
    A = np.stack([np.asarray(r, float) for r in rings])
    out = []
    for zz in z_levels:
        pts = []
        for i in range(A.shape[1]):
            zi = A[:, i, 2]
            k = np.flatnonzero(zi >= zz)
            if not len(k):
                pts.append(A[-1, i, :2])
            elif k[0] == 0:
                pts.append(A[0, i, :2])
            else:
                k = int(k[0])
                t = (zz - zi[k - 1]) / max(zi[k] - zi[k - 1], 1e-12)
                pts.append(A[k - 1, i, :2] + t * (A[k, i, :2] - A[k - 1, i, :2]))
        p = np.asarray(pts)
        out.append(0.5 * abs(float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]))))
    return np.asarray(out)
