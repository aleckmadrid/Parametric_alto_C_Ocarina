"""The round bowl around the window (window_cut = "bowl"; an OPTION since 2026-11-26, not the rule). numpy only.

The low-voicing experiment (Analizes_ocarinas/Low_voicing/, trial s3-yH7 of 2026-11-25, chosen by the owner: "s3-yH7
(xw 22)", "Keep yH7's flow", "Keep it level") cut the window through a thick thumb face into one shallow, round bowl.
This module is that cutter (night_dish.extend_window and _bowl_cut, with round_dish._quintic), ported with only the
options s3-yH7 uses. It takes the add-on's own "ellipse" window cutter and the finished outside, and returns the cutter
that replaces the window cutter:

    1  the rule's cut, unchanged, up to where the round-over starts (never below bowl_flow_floor_mm, 2.6 mm: the walls
       are kept exactly to about 2.5 mm; the throat, the lip, the 20 deg ramp and its 0.4 mm edge are the rule's);
    2  the cut's own flare, on the add-on's formula at 0.1 mm levels, up to the round-over's start;
    3  a quintic round-over (no jump of slope or curvature at either end) from the wall into the bowl, along the
       outward normals of the hole's edge, smoothed toward the ramp's tip, never more than bowl_flow_cap of the way
       to the outline;
    4  the bowl: one height field over the window face, B = S - D ((1 - rho^p)+)^q, with S the outside smoothed over
       bowl_smooth_mm and rho = 1 on the elliptic outline (bowl_half_length_mm, bowl_centre_xw_mm, bowl_half_width_mm,
       centred on the window and symmetric across it); floors: bowl_under_mm over the chamber and the pocket,
       bowl_roof_mm over the windway (made shallower smoothly there), and above the window's upper edge B held just
       under the outside;
    5  the rim: the depth under the outside falls to nothing along a quintic, from bowl_rim_round_mm inside the
       outline to bowl_rim_out_mm outside it, then the cutter rises clear of the outside.

The numbers are fields of the voicing record (kernel voicing.BOWL_BUILD), so they are in the voicing hash. The
sampling and the smoothing constants below are part of the cut, as the add-on's other cut constants are. Not ported
(experiment options s3-yH7 does not use): the ray cutter, the crest, the pad, keep_ramp, lip_z, fs_smooth, t2_du other
than its default, lip_cap_tip, the stadium rays, the contour hollow, the drop, the cubic rim.
"""
from __future__ import annotations

import warnings

import numpy as np

from . import meshutil, voicing_geo

FINE_MM = 0.1                  # the "ellipse" cut's own formula at levels this far apart (its 0.55 mm facets showed as rings)
FINE_EXTRA_MM = 3.0            # and carried on this far above the add-on's top ring
SUBDIVIDE_MM = 0.25            # ring edges longer than this at the outer face are split (the lip's flanks were one 4.2 mm facet)
GRID_X_MM, GRID_Y_MM = (-12.0, 36.0), (-30.0, 30.0)   # the height field over the window face (voicing frame, xw from the exit)
CAST_FROM_MM = 40.0            # rays from this far above the window's inner plane
UNDER_SOFT_MM = 0.4            # smooth maximum of the floors (k)
CHAMBER_MAX_MM, CHAMBER_SIG_MM = 0.6, 0.4    # the chamber taken at its highest within 0.6 mm, then softened 0.4 mm
ROOF_MARGIN_MM, ROOF_SIG_MM, ROOF_SOFT_MM = 0.15, 1.5, 0.3   # the bowl made shallower over the windway, smoothly
TOP_SIG_MM, TOP_GAP_MM, TOP_SOFT_MM, TOP_X0_MM, TOP_FADE_MM = 0.6, 0.05, 0.15, 4.4, 2.0   # above the upper edge: B under the outside
EDGE_LOW_MM = 1.2              # the bowl may not reach below this on the window's wall
FLOW_FACETS, BOWL_FACETS, FLARE_FACETS, RIM_FACETS = 48, 30, 8, 16   # rings of the round-over (even in arc), the bowl, the flare, the rim
NORMAL_SMOOTH = 6              # passes of smoothing of the hole edge's normals
WALL_DIRECTION_MM = 0.4        # the wall's direction at the round-over's start, over +-0.4 mm of arc
FLOW_HANDLE = 0.22             # the quintic's control points, as a share of its chord
BOWL_SLOPE_MM = 0.15           # the step of the bowl's slope where the round-over meets it
FLOW_SMOOTH_DEG = 60.0         # the round-over is smoothed along the ring within this angle of the jet
RIM_SIG_MM, RIM_RISE = 0.4, 0.03   # the outside under the rim smoothed 0.4 mm; beyond the rim the cutter rises 0.03 d^2
EPS_MM = 0.3                   # (the experiment's eps; the quintic rim does not use it)


def cutter(vs, v, envelope, air) -> tuple:
    """The window and bowl cutter: (V, F) in body coordinates, a record dict, and the ring stack in the voicing frame
    (xw from the windway exit), for the throat's areas (throat_areas).

    vs, v       the voicing solids (their window is the "ellipse" cut) and the record (window_cut "bowl")
    envelope    the finished outside (V, F): the skin joined with the neck
    air         the chamber joined with the voicing pocket (V, F): the plastic under the bowl is measured to it
    """
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    R = np.stack([fx, fy, fz], axis=1)
    L, wall = float(v.window_length_mm), float(v.wall_at_window_mm)
    WV, _ = vs.window
    n = len(vs.outline)
    P = (np.asarray(WV, float) - o) @ R
    P[:, 0] += L                                                    # xw: 0 at the exit, L at the lip
    nr = (len(P) - 2) // n
    rings = P[:nr * n].reshape(nr, n, 3)
    z = rings[:, :, 2].mean(axis=1)
    if np.abs(rings[:, :, 2] - z[:, None]).max() > 1e-6 or not np.all(np.diff(z) > 0):
        raise meshutil.GeometryError("bowl cut: the add-on's window cutter is not a stack of level rings")
    rings, fine = _fine_rings(vs, v, rings, FINE_MM)
    z = rings[:, :, 2].mean(axis=1)
    rings = _subdivide(rings, int(np.argmin(np.abs(z - wall))), SUBDIVIDE_MM)
    V, F, rec, allr = _bowl(vs, v, rings, (o, fx, fy, fz), L, wall, float(np.sign(fy[0]) or 1.0), envelope, air)
    rec["fine_rings"] = fine
    return V, F, rec, allr


def throat_areas(allr, z_levels) -> np.ndarray:
    """Area (mm^2) of the cutter's section at each height z of z_levels (voicing frame): along each ray of the ring
    stack, the point where the cutter's wall first reaches z; the section is the polygon of those points. Up to the
    hole's edge that is the window's own opening; above it the opening runs out into the bowl."""
    A = np.stack([np.asarray(r, float) for r in allr[:-1]])        # the last ring is the cap
    out = []
    for zz in z_levels:
        pts = []
        for i in range(A.shape[1]):
            zi = A[:, i, 2]
            k = np.flatnonzero(zi >= zz)
            if not len(k):
                return np.asarray(out + [np.inf] * (len(z_levels) - len(out)))
            k = int(k[0])
            if k == 0:
                pts.append(A[0, i, :2])
                continue
            t = (zz - zi[k - 1]) / max(zi[k] - zi[k - 1], 1e-12)
            pts.append(A[k - 1, i, :2] + t * (A[k, i, :2] - A[k - 1, i, :2]))
        p = np.asarray(pts)
        out.append(0.5 * abs(float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]))))
    return np.asarray(out)


# ------------------------------------------------------------------ helpers (night_dish.py, unchanged)

def _smooth5(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


def quintic(g0, d0, c0, t):
    """Quintic on t in [0, 1] with value g0, slope d0, curvature c0 at 0 and value, slope and curvature 0 at 1."""
    t2, t3, t4, t5 = t * t, t ** 3, t ** 4, t ** 5
    h0 = 1 - 10 * t3 + 15 * t4 - 6 * t5
    h1 = t - 6 * t3 + 8 * t4 - 3 * t5
    h2 = 0.5 * t2 - 1.5 * t3 + 1.5 * t4 - 0.5 * t5
    return g0 * h0 + d0 * h1 + c0 * h2


def _subdivide(rings, top, max_len):
    """Insert points along every ring's own edges where ring `top` has an edge longer than max_len, at the same parameters in
    every ring. The new points lie on the add-on's ring edges, so the rule's surface is kept."""
    nr, n, _ = rings.shape
    seg = np.linalg.norm(np.roll(rings[top, :, :2], -1, axis=0) - rings[top, :, :2], axis=1)
    cols = []
    for i in range(n):
        j = (i + 1) % n
        cols.append(rings[:, i:i + 1, :])
        m = int(np.ceil(seg[i] / max_len)) - 1
        if m > 0:
            t = (np.arange(1, m + 1) / (m + 1))[None, :, None]
            cols.append(rings[:, i:i + 1, :] * (1.0 - t) + rings[:, j:j + 1, :] * t)
    return np.concatenate(cols, axis=1)


def _fine_rings(vs, v, rings, step, extra=FINE_EXTRA_MM):
    """The add-on's "ellipse" window cut from its own formula (voicing_geo.build) at levels `step` mm apart and at its own
    levels, checked against the add-on's rings to 1e-5 mm: the same surface without its 0.55 mm facets."""
    cone = vs.info.get("cone") or {}
    if cone.get("style") != "ellipse":
        raise meshutil.GeometryError("bowl cut: it needs the 'ellipse' window cut under it")
    out = np.asarray(vs.outline, float)
    n0 = len(out)
    e, wall = float(v.labium_edge_thickness_mm), float(v.wall_at_window_mm)
    p_ = float(cone["flare_exponent"])
    ex_c, ex_a, ex_b = float(cone["ellipse_centre_xw_mm"]), 0.5 * float(cone["ellipse_length_mm"]), 0.5 * float(cone["ellipse_width_mm"])
    zl = rings[:, 0, 2]
    roof = float(vs.info["windway_roof_at_exit_plane_z_mm"])
    z_shelf = float(zl[np.argmin(np.abs(zl - min(max(roof + voicing_geo.SHELF_LAND_DEFAULT_MM, e + 0.2), wall - 0.2)))])
    nx, ny = np.cos(out[:, 2]), np.sin(out[:, 2])
    xb = float(out[np.argmax(out[:, 1]), 0])
    psi = np.arctan2(out[:, 1], out[:, 0] - xb)
    qx, qy = ex_c + ex_a * np.cos(psi), ex_b * np.sin(psi)
    uu = np.clip((np.degrees(np.abs(psi)) - 90.0) / voicing_geo.ELLIPSE_START_BLEND_DEG, 0.0, 1.0)
    z0 = e + (z_shelf - e) * (uu * uu * (3.0 - 2.0 * uu))
    dx, dy = qx - out[:, 0], qy - out[:, 1]

    def ring_at(zz):
        t = np.clip((zz - z0) / (wall - z0), 0.0, None)
        sx, sy = dx * t, dy * t ** p_
        sn = np.minimum(sx * nx + sy * ny, 0.0) if voicing_geo.ELLIPSE_NO_OVERHANG else np.zeros(n0)
        return np.column_stack([out[:, 0] + sx - sn * nx, out[:, 1] + sy - sn * ny, np.full(n0, zz)])

    err = max(float(np.abs(ring_at(float(zl[k])) - rings[k]).max()) for k in range(len(zl)) if zl[k] > e + 1e-9)
    if err > 1e-5:
        raise meshutil.GeometryError(f"bowl cut: the window cut's formula differs from the add-on's rings by {err:.2e} mm")
    lev = list(zl[zl > e + 1e-9])
    for zz in np.arange(e + step, float(zl.max()) + extra + 1e-9, step):
        if np.abs(np.asarray(lev) - zz).min() > 0.3 * step:
            lev.append(float(zz))
    rec = dict(step_mm=step, levels=len(lev), formula_vs_addon_max_mm=err, z_shelf_mm=z_shelf)
    return np.stack([rings[k] for k in range(len(zl)) if zl[k] <= e + 1e-9] + [ring_at(zz) for zz in sorted(lev)]), rec


def _bezier5(P, s):
    s = s[:, None, None]
    c = [1, 5, 10, 10, 5, 1]
    return sum(c[k] * s ** k * (1 - s) ** (5 - k) * P[k][None] for k in range(6))


def _cast_grid(meshes, frame, L, xs, ys):
    """Height (voicing frame z) of the topmost of the meshes over a grid of (xw, y), rays from outside along -z. NaN = miss."""
    o, fx, fy, fz = frame
    trees = [meshutil.bvh(np.asarray(V, float), np.asarray(F)) for V, F in meshes]
    Z = np.full((len(ys), len(xs)), np.nan)
    for j, y in enumerate(ys):
        b0 = o + float(y) * fy + CAST_FROM_MM * fz - L * fx
        for i, xw in enumerate(xs):
            p = b0 + float(xw) * fx
            best = np.nan
            for tree in trees:
                hits = meshutil.ray_hits(tree, p, -fz, 90.0, limit=1)
                if hits:
                    zz = CAST_FROM_MM - hits[0][0]
                    if not best >= zz:
                        best = zz
            Z[j, i] = best
    return Z


def _gauss(Z, sigma, h):
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


def _fill(Z):
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


def _interp(Z, xs, ys, x, y):
    h = xs[1] - xs[0]
    gx = np.clip((np.asarray(x) - xs[0]) / h, 0.0, len(xs) - 1.000001)
    gy = np.clip((np.asarray(y) - ys[0]) / h, 0.0, len(ys) - 1.000001)
    i0, j0 = np.floor(gx).astype(int), np.floor(gy).astype(int)
    tx, ty = gx - i0, gy - j0
    return ((1 - ty) * ((1 - tx) * Z[j0, i0] + tx * Z[j0, i0 + 1]) + ty * ((1 - tx) * Z[j0 + 1, i0] + tx * Z[j0 + 1, i0 + 1]))


def _smax(a, b, k):
    """Smooth maximum: never below max(a, b), at most k / 2 above it where a = b."""
    return 0.5 * (a + b + np.sqrt((a - b) ** 2 + k * k)) if k > 0 else np.maximum(a, b)


def _inside(poly, x, y):
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


def _ellipse_reach(P0, u, a, xc, b):
    """Distance from each P0 along u to the elliptic outline (0 where P0 is outside it)."""
    def f(p):
        return np.sqrt(((p[:, 0] - xc) / a) ** 2 + (p[:, 1] / b) ** 2)

    inside = f(P0) < 1.0
    lo, hi = np.zeros(len(P0)), np.full(len(P0), 2.0 * max(a, b))
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        ok = f(P0 + mid[:, None] * u) < 1.0
        lo, hi = np.where(ok, mid, lo), np.where(ok, hi, mid)
    return np.where(inside, lo, 0.0)


# ------------------------------------------------------------------ the cutter (night_dish._bowl_cut, s3-yH7's options)

def _bowl(vs, v, rings, frame, L, wall, ts, envelope, air):
    o, fx, fy, fz = frame
    nr, n, _ = rings.shape
    h = float(v.bowl_grid_mm)
    xs = np.round(np.arange(GRID_X_MM[0], GRID_X_MM[1] + 1e-9, h), 4)
    ys = np.round(np.arange(GRID_Y_MM[0], GRID_Y_MM[1] + 1e-9, h), 4)
    S = _fill(_cast_grid([envelope], frame, L, xs, ys))
    C = _fill(_cast_grid([air], frame, L, xs, ys))
    Ss = _gauss(S, float(v.bowl_smooth_mm), h)
    X, Y = np.meshgrid(xs, ys)
    D, p_, q_ = float(v.bowl_depth_mm), float(v.bowl_floor_exponent), float(v.bowl_rim_exponent)
    a_, b_, xc = float(v.bowl_half_length_mm), float(v.bowl_half_width_mm), float(v.bowl_centre_xw_mm)
    rho = np.sqrt(((X - xc) / a_) ** 2 + (Y / b_) ** 2)
    d = D * np.clip(1.0 - rho ** p_, 0.0, None) ** q_
    # over the windway (above the window's upper edge) the bowl is made shallower smoothly, so that it keeps the roof's plastic
    info_ = vs.info
    roof = float(v.bowl_roof_mm)
    zr0 = float(info_.get("windway_roof_at_exit_plane_z_mm", 1.67)) + np.maximum(-X, 0.0) * np.tan(np.radians(float(info_.get("windway_pitch_deg", 0.0))))
    hw0 = 0.5 * float(getattr(v, "windway_width_mm", v.window_width_mm)) + 1.5
    st0 = _smooth5((hw0 + 3.0 - np.abs(Y)) / 3.0) * _smooth5((2.5 - X) / 2.5)
    d_lim = np.maximum(Ss - (zr0 + roof + ROOF_MARGIN_MM), 0.0) + 10.0 * (1.0 - st0)
    d_lim = _gauss(d_lim, ROOF_SIG_MM, h)
    d = 0.5 * (d + d_lim - np.sqrt((d - d_lim) ** 2 + ROOF_SOFT_MM * ROOF_SOFT_MM))          # smooth minimum
    d = np.maximum(d, 0.0)
    out = np.asarray(vs.outline, float)[:, :2]
    B = Ss - d
    k_s = UNDER_SOFT_MM
    # the chamber's height taken at its highest within 0.6 mm (no smoothing below the true surface), then softened
    Cd = C.copy()
    rr = max(int(round(CHAMBER_MAX_MM / h)), 1)
    for dj in range(-rr, rr + 1):
        for di in range(-rr, rr + 1):
            Cd = np.maximum(Cd, np.roll(np.roll(C, dj, axis=0), di, axis=1))
    B = _smax(B, _gauss(Cd, CHAMBER_SIG_MM, h) + float(v.bowl_under_mm), k_s)
    # the windway roof under the bowl above the window's upper edge
    z_roof_exit = float(info_.get("windway_roof_at_exit_plane_z_mm", 1.67))
    pitch = np.radians(float(info_.get("windway_pitch_deg", 0.0)))
    half_w = 0.5 * float(getattr(v, "windway_width_mm", v.window_width_mm)) + 1.5
    zr = z_roof_exit + np.maximum(-X, 0.0) * np.tan(pitch)
    strip = _smooth5((half_w + 2.5 - np.abs(Y)) / 2.5) * _smooth5((2.0 - X) / 2.0)
    B = np.where(strip > 0, _smax(B, zr + roof - 10.0 * (1.0 - strip), k_s), B)
    # above the window's upper edge the outside has a valley where the neck's flank meets the skin; smoothed it is
    # filled, so B is held at most TOP_GAP_MM under the outside there (s3-yB4), and the roof's floor applied again
    tgt = _gauss(S, TOP_SIG_MM, h) - TOP_GAP_MM
    Bm = 0.5 * (B + tgt - np.sqrt((B - tgt) ** 2 + TOP_SOFT_MM * TOP_SOFT_MM))
    Wt = _smooth5((TOP_X0_MM - X) / TOP_FADE_MM)
    B = B + Wt * np.minimum(Bm - B, 0.0)
    B = np.where(strip > 0, _smax(B, zr + roof - 10.0 * (1.0 - strip), k_s), B)

    def Bf(x, y):
        return _interp(B, xs, ys, x, y)

    # the add-on's flare, point by point, carried on beyond its top ring
    Fp = np.concatenate([rings, np.stack([rings[-1] + m * (rings[-1] - rings[-2]) for m in (1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0)])], axis=0)
    Kp = len(Fp)
    fval = Fp[:, :, 2] - Bf(Fp[:, :, 0], Fp[:, :, 1])
    k_lo = int(np.flatnonzero(rings[:, 0, 2] >= EDGE_LOW_MM)[0])
    if (fval[k_lo] >= 0).any():
        raise meshutil.GeometryError(f"bowl cut: the bowl lies below {EDGE_LOW_MM:g} mm at {int((fval[k_lo] >= 0).sum())} points of the "
                                     "window's wall (too deep at the window)")
    above = fval >= 0
    above[:k_lo] = False
    if not above.any(axis=0).all():
        raise meshutil.GeometryError("bowl cut: the window's wall never meets the bowl at some points")
    kk = np.argmax(above, axis=0) - 1                                   # segment kk -> kk + 1 crosses
    idx = np.arange(n)
    A0, A1 = Fp[kk, idx], Fp[kk + 1, idx]
    lo, hi = np.zeros(n), np.ones(n)
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        Pm = A0 + mid[:, None] * (A1 - A0)
        up = Pm[:, 2] - Bf(Pm[:, 0], Pm[:, 1]) >= 0
        lo, hi = np.where(up, lo, mid), np.where(up, mid, hi)
    tE = 0.5 * (lo + hi)
    E = A0 + tE[:, None] * (A1 - A0)
    # arc length along each flare line; the round-over's start lip mm below the edge, never below the floor
    seg = np.linalg.norm(np.diff(Fp, axis=0), axis=2)
    cum = np.vstack([np.zeros(n), np.cumsum(seg, axis=0)])
    sE = cum[kk, idx] + tE * seg[kk, idx]
    lip = max(float(v.bowl_flow_mm), 0.05)
    lip_out = max(float(v.bowl_flow_out_mm), 0.05)
    lip_floor = float(v.bowl_flow_floor_mm)

    def at_s(s):
        k = np.clip(np.array([np.searchsorted(cum[:, i], s[i]) - 1 for i in range(n)]), 0, Kp - 2)
        t = np.clip((s - cum[k, idx]) / np.maximum(seg[k, idx], 1e-12), 0.0, 1.0)
        P_ = Fp[k, idx] + t[:, None] * (Fp[k + 1, idx] - Fp[k, idx])
        T_ = Fp[k + 1, idx] - Fp[k, idx]
        return P_, T_ / np.maximum(np.linalg.norm(T_, axis=1), 1e-12)[:, None]

    s_floor = np.array([np.interp(lip_floor, Fp[:, i, 2], cum[:, i]) for i in range(n)])
    sF = np.maximum(sE - lip, np.minimum(s_floor, sE - 0.05))
    Fs, _ = at_s(sF)
    # the wall's direction at the round-over's start as a central difference over +-WALL_DIRECTION_MM of arc (one 0.1 mm
    # segment's direction jumps from point to point where the flare bends: streaks along the flow)
    Pa_, _ = at_s(sF + WALL_DIRECTION_MM)
    Pb_, _ = at_s(np.maximum(sF - WALL_DIRECTION_MM, 0.0))
    T1 = Pa_ - Pb_
    T1 /= np.maximum(np.linalg.norm(T1, axis=1), 1e-12)[:, None]
    z_keep = min(float(Fs[:, 2].min()) - 0.08, wall)
    if z_keep < EDGE_LOW_MM - 0.3:
        raise meshutil.GeometryError(f"bowl cut: the round-over would start at {z_keep:.2f} mm, below the window's walls kept")
    zr_ = rings[:, 0, 2]
    Jk = int(np.flatnonzero(zr_ < z_keep).max())
    kz = (z_keep - zr_[Jk]) / (zr_[Jk + 1] - zr_[Jk])
    Rk = rings[Jk] + kz * (rings[Jk + 1] - rings[Jk])
    sK = cum[Jk, idx] + kz * seg[Jk, idx]
    flare = [at_s(sK + (sF - sK) * j / FLARE_FACETS)[0] for j in range(1, FLARE_FACETS + 1)]
    Exy = E[:, :2]
    # outward normals of the hole's edge, in plan, smoothed along it
    t2 = np.roll(Exy, -1, axis=0) - np.roll(Exy, 1, axis=0)
    u = np.column_stack([t2[:, 1], -t2[:, 0]])
    u /= np.maximum(np.linalg.norm(u, axis=1), 1e-12)[:, None]
    if (u * (Exy - Exy.mean(axis=0))).sum() < 0:
        u = -u
    for _ in range(NORMAL_SMOOTH):
        u = (np.roll(u, 1, axis=0) + 2.0 * u + np.roll(u, -1, axis=0)) / 4.0
        u /= np.maximum(np.linalg.norm(u, axis=1), 1e-12)[:, None]
    reach = _ellipse_reach(Exy, u, a_, xc, b_)
    cap_ = float(v.bowl_flow_cap)
    lip_out = np.minimum(lip_out, cap_ * reach)
    for _ in range(8):
        lip_out = np.minimum((np.roll(lip_out, 1) + 2.0 * lip_out + np.roll(lip_out, -1)) / 4.0, cap_ * reach)
    lip_out = np.maximum(lip_out, 0.05)
    if (reach < lip_out + 0.6).any():
        k_ = int(np.argmin(reach - lip_out))
        raise meshutil.GeometryError(f"bowl cut: the hole's edge comes within {float(reach.min()):.2f} mm of the bowl's outline "
                                     f"(points {int((reach < lip_out + 0.6).sum())}; worst at xw {Exy[k_, 0]:.2f}, y {Exy[k_, 1]:.2f}); "
                                     "make the bowl larger")

    def slope_u(P2, du=BOWL_SLOPE_MM):
        return (Bf(P2[:, 0] + du * u[:, 0], P2[:, 1] + du * u[:, 1]) - Bf(P2[:, 0] - du * u[:, 0], P2[:, 1] - du * u[:, 1])) / (2 * du)

    Be_xy = Exy + lip_out[:, None] * u
    Be = np.column_stack([Be_xy, Bf(Be_xy[:, 0], Be_xy[:, 1])])
    T2 = np.column_stack([u, slope_u(Be_xy)])
    T2 /= np.linalg.norm(T2, axis=1)[:, None]
    ch = np.linalg.norm(Be - Fs, axis=1)
    m_l = FLOW_FACETS
    sl = np.arange(1, m_l + 1) / m_l
    # quintic with three control points in line at each end: no curvature where it leaves the wall or meets the bowl;
    # its points evenly along the curve
    c_ = FLOW_HANDLE * ch[:, None]
    Pq = [Fs, Fs + c_ * T1, Fs + 2 * c_ * T1, Be - 2 * c_ * T2, Be - c_ * T2, Be]
    fine = _bezier5(Pq, np.linspace(0.0, 1.0, 241))
    sl_ = np.vstack([np.zeros((1, n)), np.cumsum(np.linalg.norm(np.diff(fine, axis=0), axis=2), axis=0)])
    tgt = sl[:, None] * sl_[-1][None, :]
    lipr = []
    for k in range(m_l):
        j = np.clip(np.array([np.searchsorted(sl_[:, i], tgt[k, i]) for i in range(n)]), 1, 240)
        w_ = ((tgt[k] - sl_[j - 1, idx]) / np.maximum(sl_[j, idx] - sl_[j - 1, idx], 1e-12))[:, None]
        lipr.append(fine[j - 1, idx] + w_ * (fine[j, idx] - fine[j - 1, idx]))
    # the round-over's inner rings smoothed along the ring toward the ramp's tip, strongest half-way along the curve
    ang_ = np.degrees(np.abs(np.arctan2(u[:, 1], u[:, 0])))
    wdir = _smooth5((FLOW_SMOOTH_DEG - ang_) / 20.0)
    for k in range(m_l - 1):
        wk = (np.sin(np.pi * sl[k]) ** 2) * wdir
        P_ = lipr[k].copy()
        for _ in range(int(v.bowl_flow_smooth)):
            P_ = P_ + wk[:, None] * (0.25 * (np.roll(P_, 1, axis=0) + 2.0 * P_ + np.roll(P_, -1, axis=0)) - P_)
        lipr[k] = P_
    # the bowl along the normal, then the rim
    w_r = float(v.bowl_rim_round_mm)
    r_end = np.maximum(reach - w_r, lip_out + 0.3) if w_r > 0 else reach
    sb = 0.5 - 0.5 * np.cos(np.pi * np.arange(1, BOWL_FACETS + 1) / BOWL_FACETS)
    bowl = []
    for s_ in sb:
        r = lip_out + s_ * (r_end - lip_out)
        xy = Exy + r[:, None] * u
        bowl.append(np.column_stack([xy, Bf(xy[:, 0], xy[:, 1])]))
    # the rolled rim: the depth under the outside (smoothed RIM_SIG_MM) falls from the bowl's to nothing along a quintic
    # (no jump of slope or curvature), reaching 0 at bowl_rim_out_mm beyond the outline; beyond, the cutter rises
    # RIM_RISE d^2 over the outside for 3 mm, so it never crosses the skin at an angle
    Sx_r = _gauss(S, RIM_SIG_MM, h)
    dlt = Sx_r - B

    def Df(xy_):
        return _interp(dlt, xs, ys, xy_[:, 0], xy_[:, 1])

    r0, r1 = r_end, reach + float(v.bowl_rim_out_mm)
    r1 = np.maximum(r1, r0 + 0.5)
    Ln = r1 - r0
    du_ = 0.3
    xy0 = Exy + r0[:, None] * u
    d0 = Df(xy0)
    dp = (Df(xy0 + du_ * u) - Df(xy0 - du_ * u)) / (2 * du_)
    dpp = (Df(xy0 + du_ * u) - 2.0 * d0 + Df(xy0 - du_ * u)) / (du_ * du_)
    rim = []
    for s_ in np.arange(1, RIM_FACETS + 1) / RIM_FACETS:
        r = r0 + s_ * Ln
        xy = Exy + r[:, None] * u
        rim.append(np.column_stack([xy, _interp(Sx_r, xs, ys, xy[:, 0], xy[:, 1]) - quintic(d0, dp * Ln, dpp * Ln * Ln, s_)]))
    for dd in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        xy = Exy + (r1 + dd)[:, None] * u
        rim.append(np.column_stack([xy, _interp(Sx_r, xs, ys, xy[:, 0], xy[:, 1]) + RIM_RISE * dd * dd]))
    endr = rim[-1]
    z_cap = max(float(vs.info["z_top_mm"]), float(np.max([r_[:, 2].max() for r_ in bowl + rim])) + 0.6)
    flat = np.column_stack([endr[:, :2] + 0.3 * u, endr[:, 2]])
    cap = flat.copy()
    cap[:, 2] = z_cap
    allr = [rings[k] for k in range(Jk + 1)] + [Rk] + flare + lipr + bowl + rim + [flat, cap]
    V, F = meshutil.prism_from_rings(allr)
    V[:, 0] -= L
    V = meshutil.frame_points(V, o, fx, fy, fz)
    if meshutil.volume(V, F) < 0:
        F = F[:, ::-1]
    bad = meshutil.self_intersections(V, F)
    if bad:
        raise meshutil.GeometryError(f"bowl cut: the window and bowl cutter intersects itself ({bad} pairs)")
    # measures for the record
    inb = (rho < 1.0) & ~_inside(Exy, X, Y)
    xb = float(out[np.argmax(out[:, 1]), 0])
    side = np.abs(np.abs(E[:, 1]) - np.abs(E[:, 1]).max()) < 0.3
    backm = (E[:, 0] < 0.3) & (np.abs(E[:, 1]) < 3.0)
    tip = int(np.argmax(E[:, 0]))
    roof_left = B - zr
    roof_zone = (strip > 0.99) & (rho < 1.0) & (X < -0.05)
    r_fin = np.maximum(reach + float(v.bowl_rim_out_mm), r_end + 0.5)
    i_back = int(np.argmin(np.where(E[:, 0] < 0.3, np.abs(E[:, 1]), np.inf)))
    i_tail, i_bulb = int(np.argmax(E[:, 1] * ts)), int(np.argmin(E[:, 1] * ts))
    flow = {k: dict(xw=float(E[i, 0]), y=float(E[i, 1]), reach_mm=float(reach[i]), flow_out_mm=float(lip_out[i]),
                    rim_from_mm=float(r_end[i]), rim_to_mm=float(r_fin[i]))
            for k, i in dict(tip=tip, back=i_back, tail=i_tail, bulb=i_bulb).items()}
    flow.update(flow_out_least_mm=float(lip_out.min()), flow_out_most_mm=float(lip_out.max()))
    rec = dict(mode="bowl", ring_points=int(n), z_kept_exactly_mm=float(z_keep), z_cap_mm=z_cap,
               edge_z_mm=dict(least=float(E[:, 2].min()), most=float(E[:, 2].max()), sides=float(E[side, 2].mean()),
                              back=float(E[backm, 2].mean()) if backm.any() else None, tip=float(E[tip, 2])),
               wall_at_window_rule_mm=wall,
               roundover_start_z_mm=dict(least=float(Fs[:, 2].min()), most=float(Fs[:, 2].max()), tip=float(Fs[tip, 2])),
               ramp_rule_kept_mm=float(Fs[tip, 0] - L), ramp_kept_mm=float(E[tip, 0] - L),
               ramp_rule_mm=float((wall - float(v.labium_edge_thickness_mm)) / np.tan(np.radians(float(v.labium_ramp_angle_deg)))),
               hole_extent_xw_mm=[float(E[:, 0].min()), float(E[:, 0].max())], hole_extent_y_mm=[float(E[:, 1].min()), float(E[:, 1].max())],
               bowl_depth_most_mm=float(np.nanmax(np.where(inb, S - B, np.nan))),
               plastic_under_bowl_least_mm=float(np.nanmin(np.where(inb, B - C, np.nan))),
               roof_plastic_least_mm=float(np.nanmin(np.where(roof_zone, roof_left, np.nan))) if roof_zone.any() else None,
               rim_extent_xw_mm=[float(xc - a_), float(xc + a_)], rim_extent_y_mm=[float(-b_), float(b_)],
               rim_height_mean_mm=float(np.mean(_interp(S, xs, ys, Exy[:, 0] + reach * u[:, 0], Exy[:, 1] + reach * u[:, 1]))),
               widest_xw_mm=xb, cutter_triangles=int(len(F)), cutter_volume_mm3=float(meshutil.volume(V, F)), flow=flow)
    return V, F, rec, allr
