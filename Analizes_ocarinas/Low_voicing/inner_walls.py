"""Inner walls (partial partitions) between the window and the thumb holes: EXPERIMENT code of series 3.

The owner, 2026-11-19: "implement the inner wall due to the closenes to the thumb holes". Read as the partial walls
of the Spencer half-shell picture and of patent US 7,799,980 (Analizes_ocarinas/Patent_US7799980/).

This module is not part of the add-on. It lives beside the trials and hooks into the build from outside
(install()), so that no add-on file of this checkout differs from the snapshot of the main checkout.

How a wall is made
    A wall is a slab across the body (its faces are planes x = const in body coordinates, X runs along the body),
    standing on the thumb-face side of the chamber up to a level top edge. The top edge is a half round. Where the
    slab meets the chamber wall (and the skirt of the voicing pocket, if it stands there) a fillet strip follows the
    meeting line, so there is no sharp inside corner.
    The slab and its strip are SUBTRACTED FROM THE AIR before the air is cut out of the shell. Nothing else of the
    build changes: the outside, the voicing solids and the holes are made as before.
    The walls take air, so the chamber is solved again, a little larger, until the walled air holds the target.

A second way, after the owner's notes of 2026-11-20 on the clay internals (Spencer mould and half-shell pictures,
and the Blender reference with its thick shell): the RIDGE FIELD. The thumb-face wall of the chamber is made thicker
by a smooth field of plastic, and pockets are left in it: a funnel around each thumb hole and the pocket of the
voicing. What stands between the pockets is a broad ridge with a round top and no sharp edge anywhere. It is one
height field over the plan of the body: thickness = height x (pocket masks) x (how far the wall faces the deck).

Preset keys (all optional; without inner_wall_x_mm there is no wall and the build is the add-on's own)
    inner_wall_x_mm          {"L": x, "R": x}: the middle plane of each wall, mm along the body from the lip
    inner_wall_height        top edge, as a share of the height of the air section at the wall (0.5 = the mid-line)
    inner_wall_thickness_mm  default 2.4
    inner_wall_fillet_mm     radius of the fillet at the foot, default 2.0 (0 = none); or {"L": [r toward -x, r toward +x]}
                             when a thumb hole is so near that the fillet on its side must be small
    inner_ridge_height_mm    the ridge field: plastic added on the thumb-face wall, mm (no key = no ridge field)
    (the funnels are placed on the thumb holes of the body as it is being built: the holes move when the chamber grows)
    inner_ridge_width_mm     the width over which a pocket's side rises to the full height (default 3)
    inner_ridge_land_mm      flat land around a thumb hole's rim before its funnel starts to rise (default 1.0)
    inner_ridge_window_half_mm   half width, along the body, of the zone around the window that is kept free. Default: the
                             whole pocket of the voicing with its skirt (about 14 mm), so the field never stands on it
    inner_ridge_tail         True: the thick wall runs on to the tail (the Spencer's solid tail); False: only between
                             the two thumb holes
"""
from __future__ import annotations

import math
import types

import numpy as np

from ocarina_addon import meshutil

THICKNESS_DEFAULT_MM = 2.4
FILLET_DEFAULT_MM = 2.0
HEIGHT_DEFAULT = 0.5
FILLET_MIN_MM = 0.4            # the strip thins out to this radius at its two ends, under the top edge
FILLET_TAPER_MM = 4.0          # ... over this length of the meeting line
FILLET_INTO_SLAB_MM = 0.03     # the strip's arc ends this far inside the slab's face, so the two cross cleanly
FILLET_UNDER_WALL_MM = 0.05    # ... and this far under the chamber wall, for the same reason (a tangent meeting leaves slivers)
STRIP_STEP_MM = 1.0            # distance between the sections of the fillet strip along the meeting line
ARC_POINTS = 8
TOP_POINTS = 12
BIG = 200.0
VOLUME_TOL = 2e-6              # the walled air against its target (relative)
ROUNDS = 8
CRUMBS_MAX_MM3 = 5.0           # air cut off as loose crumbs by the ridge field: more than this is an error

LAST = {}                      # what the last build made: specs, solids, numbers (read by the trial script)


# ------------------------------------------------------------------ the section of a mesh at x = x0

def slice_x(V, F, x0: float):
    """The cut of a closed mesh with the plane x = x0: a list of closed loops, each an (n, 2) array of (y, z),
    counter-clockwise (the inside on the left)."""
    V = np.asarray(V, float)
    d = V[:, 0] - x0
    d[np.abs(d) < 1e-9] = 1e-9
    segs = []
    F = np.asarray(F)
    pos = d[F] > 0
    for f in F[pos.any(axis=1) & ~pos.all(axis=1)]:
        s = d[f]
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if (s[a] > 0) != (s[b] > 0):
                t = s[a] / (s[a] - s[b])
                pts.append(V[f[a]] + t * (V[f[b]] - V[f[a]]))
        if len(pts) == 2:
            segs.append((pts[0][1:], pts[1][1:]))
    if not segs:
        return []
    key = lambda p: (round(float(p[0]), 5), round(float(p[1]), 5))      # noqa: E731
    nxt = {}
    for a, b in segs:
        nxt.setdefault(key(a), []).append((key(b), b))
        nxt.setdefault(key(b), []).append((key(a), a))
    loops, seen = [], set()
    for start in list(nxt):
        if start in seen:
            continue
        loop, cur, prev = [], start, None
        while cur not in seen:
            seen.add(cur)
            loop.append(cur)
            step = [k for k, _ in nxt[cur] if k != prev and k not in seen]
            if not step:
                break
            prev, cur = cur, step[0]
        if len(loop) >= 8:
            P = np.array(loop, float)
            if _area(P) < 0:
                P = P[::-1]
            loops.append(P)
    return sorted(loops, key=lambda P: -_area(P))


def _area(P) -> float:
    return 0.5 * float(np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]))


def _area_below(P, z_top: float) -> float:
    """Area of the part of the polygon below z = z_top (Sutherland-Hodgman against one half plane)."""
    out = []
    n = len(P)
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        ia, ib = a[1] <= z_top, b[1] <= z_top
        if ia:
            out.append(a)
        if ia != ib:
            t = (z_top - a[1]) / (b[1] - a[1])
            out.append(a + t * (b - a))
    return _area(np.array(out)) if len(out) >= 3 else 0.0


def _resample(P, step: float):
    """Points at even distances along a polyline. The cut of a mesh has points that lie almost on each other (two
    edges of one triangle fan); normals taken from those swing wildly, and a strip lofted along them folds."""
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    n = max(int(round(s[-1] / step)), 8)
    t = np.linspace(0.0, s[-1], n + 1)
    return np.column_stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])])


# ------------------------------------------------------------------ the solids of one wall

def slab(x0: float, t: float, z_top: float):
    """The slab: faces at x0 -+ t/2, a half-round top edge whose highest line is z_top, endless downward and sideways."""
    r = 0.5 * t
    ang = np.linspace(0.0, math.pi, TOP_POINTS)
    prof = [(x0 - r, -BIG), (x0 + r, -BIG)] + [(x0 + r * math.cos(a), z_top - r + r * math.sin(a)) for a in ang]
    rings = [np.array([(x, y, z) for x, z in prof]) for y in (-BIG, BIG)]
    V, F = meshutil.prism_from_rings(rings)
    if meshutil.volume(V, F) < 0:
        F = F[:, ::-1]
    return V, F


def _profile(t: float, rL: float, rR: float, bL: float, bR: float):
    """The section of the fillet strip in (x, d): x across the wall from its middle plane, d from the chamber wall
    into the air. The chamber wall is the line d = b * |x| on each side (it need not stand square to the slab)."""
    ht = 0.5 * t - FILLET_INTO_SLAB_MM
    side = {}
    for name, b, rf in (("L", bL, rL), ("R", bR, rR)):
        s = math.sqrt(1.0 + b * b)
        xc = ht + rf
        dc = b * xc + rf * s - FILLET_UNDER_WALL_MM
        a1 = math.atan2(-1.0, b) + 2.0 * math.pi                  # from the centre toward the chamber wall
        arc = [(xc + rf * math.cos(a), dc + rf * math.sin(a)) for a in np.linspace(math.pi, a1, ARC_POINTS)]
        side[name] = (arc, dc)                                    # arc[0] on the slab's face, arc[-1] on the chamber wall
    arcR, dcR = side["R"]
    arcL, dcL = side["L"]
    low = min(arcR[-1][1], arcL[-1][1], 0.0) - 1.5                # into the plastic: only the part in the air counts
    pts = [(-arcL[-1][0], low), (arcR[-1][0], low)]
    pts += list(reversed(arcR))                                   # up the right fillet to the slab's face
    pts += [(ht - 0.25, dcR + 0.5), (-ht + 0.25, dcL + 0.5)]      # across, inside the slab
    pts += [(-x, d) for x, d in arcL]                             # down the left fillet
    return np.array(pts, float)


def fillet_strip(air, tree, loop, x0: float, t: float, rf, z_top: float):
    """The fillet along the line where the slab meets the air's wall. `loop` is the air section at x0.
    rf = (radius on the side toward -x, radius on the side toward +x)."""
    rf_side = {"L": float(rf[0]), "R": float(rf[1])}
    n = len(loop)
    low = loop[:, 1] <= z_top - 0.5 * t - 0.3
    if low.sum() < 6 or low.all():
        return None
    start = next(i for i in range(n) if low[i] and not low[i - 1])
    run = []
    i = start
    while low[i % n]:
        run.append(i % n)
        i += 1
    P = _resample(loop[run], STRIP_STEP_MM)
    tang = np.gradient(P, axis=0)
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    m = np.column_stack([-tang[:, 1], tang[:, 0]])                # inward normal in the section plane (loop is ccw)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    X = np.array([1.0, 0.0, 0.0])
    rings = []
    for k in range(len(P)):
        c = np.array([x0, P[k, 0], P[k, 1]])
        m3 = np.array([0.0, m[k, 0], m[k, 1]])
        slope = {}
        for name, sign in (("L", -1.0), ("R", 1.0)):              # how the air's wall runs along the body, each side
            xe = 0.5 * t + rf_side[name]
            hits = meshutil.ray_hits(tree, c + sign * xe * X + 6.0 * m3, -m3, 12.0, limit=1)
            e = (6.0 - hits[0][0]) if hits else 0.0               # > 0: the wall has come inward at that station
            slope[name] = max(-0.8, min(0.8, e / xe))
        ends = min(s[k], s[-1] - s[k])
        w = min(1.0, ends / FILLET_TAPER_MM)
        ease = 3 * w * w - 2 * w * w * w
        r_k = {n_: FILLET_MIN_MM + (max(r_, FILLET_MIN_MM) - FILLET_MIN_MM) * ease for n_, r_ in rf_side.items()}
        prof = _profile(t, r_k["L"], r_k["R"], slope["L"], slope["R"])
        rings.append(np.array([c + x * X + d * m3 for x, d in prof]))
    V, F = meshutil.prism_from_rings(rings)
    if meshutil.volume(V, F) < 0:
        F = F[:, ::-1]
    return V, F


# ------------------------------------------------------------------ the ridge field

RIDGE_STEP_MM = 0.5
RIDGE_POCKET_MARGIN_MM = 0.8    # the field keeps this far from the pocket of the voicing and its skirt
RIDGE_UNDER_MM = 0.15           # where the field is zero its top lies this far under the wall (no tangent meeting)
RIDGE_FACE_NZ = (0.50, 0.82)    # the field fades out where the wall turns from facing the deck (nz 0.82) to 60 deg off it
RIDGE_FADE_HEIGHTS = (11.0, 18.0)   # mm of chamber height: no field below the first, the full field above the second
RIDGE_HEIGHT_SHARE_MAX = 0.45   # never more than this share of the chamber's own height at that place (the tail)


def _smooth(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def ridge_from(preset):
    if preset.get("inner_ridge_height_mm") is None:
        return None
    return dict(h=float(preset["inner_ridge_height_mm"]), W=float(preset.get("inner_ridge_width_mm", 3.0)),
                land=float(preset.get("inner_ridge_land_mm", 1.0)),
                win_half=None if preset.get("inner_ridge_window_half_mm") is None else float(preset["inner_ridge_window_half_mm"]),
                tail=bool(preset.get("inner_ridge_tail", False)), thumbs={})


def ridge_solid(air, vs, L_window: float, sp):
    """The ridge field as a closed solid: a height field over the plan of the body (x along it, y across), standing on
    the thumb-face wall of the air. Returns ((V, F), numbers)."""
    V, F = air
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    X, Y, Z = np.eye(3)
    x0, x1 = float(V[:, 0].min()) - 1.0, float(V[:, 0].max()) + 1.0
    y0, y1 = float(V[:, 1].min()) - 1.0, float(V[:, 1].max()) + 1.0
    nx, ny = int(round((x1 - x0) / RIDGE_STEP_MM)), int(round((y1 - y0) / RIDGE_STEP_MM))
    hits, dx, dy = meshutil.column_hits(V, F, (0.0, 0.0, 0.0), X, Y, Z, (x0, x1, y0, y1), nx, ny)
    zw = np.full((nx, ny), np.nan)
    zt = np.full((nx, ny), np.nan)
    for (i, j), lst in hits.items():
        hs = [h for h, _ in lst]
        zw[i, j], zt[i, j] = min(hs), max(hs)
    xs = x0 + (np.arange(nx) + 0.371390676) * dx
    ys = y0 + (np.arange(ny) + 0.618033989) * dy
    valid = ~np.isnan(zw)
    # outside the plan of the chamber: the nearest wall height of the same row (only so that the solid closes)
    for i in range(nx):
        row = valid[i]
        if row.any():
            jj = np.nonzero(row)[0]
            zw[i, ~row] = np.interp(np.nonzero(~row)[0], jj, zw[i, jj])
            zt[i, ~row] = np.interp(np.nonzero(~row)[0], jj, zw[i, jj])
    rows = valid.any(axis=1)
    ii = np.nonzero(rows)[0]
    for j in range(ny):
        zw[~rows, j] = np.interp(np.nonzero(~rows)[0], ii, zw[ii, j])
        zt[~rows, j] = np.interp(np.nonzero(~rows)[0], ii, zw[ii, j])
    gx, gy = np.gradient(zw, dx, dy)
    nz = 1.0 / np.sqrt(1.0 + gx * gx + gy * gy)
    # At the rim of the plan the slope is not known (there is no wall beyond it to difference against), and the wall
    # is upright there anyway: no field within 2 mm of the rim. Without this a fin of plastic hung on the side wall
    # of the tail (second build of s3-k2: 0.02 mm thick).
    inner = valid.copy()
    for _ in range(int(round(2.0 / RIDGE_STEP_MM))):
        e = inner.copy()
        e[1:, :] &= inner[:-1, :]
        e[:-1, :] &= inner[1:, :]
        e[:, 1:] &= inner[:, :-1]
        e[:, :-1] &= inner[:, 1:]
        e[0, :] = e[-1, :] = False
        e[:, 0] = e[:, -1] = False
        inner = e
    lat = _smooth((nz - RIDGE_FACE_NZ[0]) / (RIDGE_FACE_NZ[1] - RIDGE_FACE_NZ[0])) * inner
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    M = lat.copy()
    W = sp["W"]
    cx = {}
    for name, (tx, ty, td) in sp["thumbs"].items():
        cx[name] = tx
        rho = np.hypot(XX - cx[name], YY - ty)
        M *= _smooth((rho - (0.5 * td + sp["land"])) / W)
    # the voicing's pocket: a rounded box in the plane of the window, from behind the windway exit to beyond the lip
    Pw = np.stack([XX - o[0], YY - o[1], zw - o[2]], axis=-1)
    u, v = Pw @ fx, Pw @ fy
    Q = (np.asarray(vs.pocket[0], float) - o)                    # the pocket of the voicing with its skirt, as built
    pu, pv = Q @ fx, Q @ fy
    u_lo, u_hi = float(pu.min()) - RIDGE_POCKET_MARGIN_MM, float(pu.max()) + RIDGE_POCKET_MARGIN_MM
    half = float(np.abs(pv).max()) + RIDGE_POCKET_MARGIN_MM if sp["win_half"] is None else sp["win_half"]
    du = np.maximum(np.maximum(u_lo - u, u - u_hi), 0.0)
    dv = np.maximum(np.abs(v) - half, 0.0)
    M *= _smooth(np.hypot(du, dv) / W)
    lo, hi = min(cx.values()), max(cx.values())
    band = _smooth((XX - lo + W) / W)
    if not sp["tail"]:
        band = band * _smooth((hi + W - XX) / W)
    M *= band
    # toward the tip of the tail the chamber is too low for a thick wall: the field fades out where the chamber is
    # between RIDGE_FADE_HEIGHTS high (at the very tip it left sliver faces, third build of s3-k2)
    M *= _smooth((np.maximum(zt - zw, 0.0) - RIDGE_FADE_HEIGHTS[0]) / (RIDGE_FADE_HEIGHTS[1] - RIDGE_FADE_HEIGHTS[0]))
    t = np.minimum(sp["h"] * M, RIDGE_HEIGHT_SHARE_MAX * np.maximum(zt - zw, 0.0)) - RIDGE_UNDER_MM
    # The solid stands only where the field does (and one ring of cells around it, where its top is just under the
    # wall). A sheet under the whole plan would cross the air wherever the wall has a step: at the back and the sides
    # of the voicing's pocket it cut a fin of plastic into the edge of the window (first build of s3-k2).
    node = (t > -RIDGE_UNDER_MM + 0.02) & valid
    if not node.any():
        raise meshutil.GeometryError("the ridge field is empty: the pockets leave no room for it")
    cell = node[:-1, :-1] | node[1:, :-1] | node[1:, 1:] | node[:-1, 1:]
    cell &= valid[:-1, :-1] & valid[1:, :-1] & valid[1:, 1:] & valid[:-1, 1:]
    for _ in range(50):                                   # no two cells may meet at a corner only (the solid would pinch there)
        d1 = cell[:-1, :-1] & cell[1:, 1:] & ~cell[1:, :-1] & ~cell[:-1, 1:]
        d2 = cell[1:, :-1] & cell[:-1, 1:] & ~cell[:-1, :-1] & ~cell[1:, 1:]
        if not (d1.any() or d2.any()):
            break
        fill = d1 | d2
        cell[:-1, :-1] |= fill
        cell[1:, 1:] |= fill
        cell[1:, :-1] |= fill
        cell[:-1, 1:] |= fill
    ci, cj = np.nonzero(cell)
    used = np.zeros((nx, ny), bool)
    for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
        used[ci + di, cj + dj] = True
    idx = -np.ones((nx, ny), np.int64)
    idx[used] = np.arange(int(used.sum()))
    nb = int(used.sum())
    Vt = np.stack([XX[used], YY[used], (zw + t)[used]], axis=-1)
    Vb = np.stack([XX[used], YY[used], (zw - 1.0)[used]], axis=-1)
    a, b, c, d = idx[ci, cj], idx[ci + 1, cj], idx[ci + 1, cj + 1], idx[ci, cj + 1]
    faces = [np.stack([a, b, c], 1), np.stack([a, c, d], 1),                              # top, normal up
             np.stack([a + nb, c + nb, b + nb], 1), np.stack([a + nb, d + nb, c + nb], 1)]   # bottom, normal down
    pad = np.zeros((nx + 1, ny + 1), bool)
    pad[1:-1, 1:-1] = cell
    for (pa, pb), (oi, oj) in (((a, b), (0, -1)), ((b, c), (1, 0)), ((c, d), (0, 1)), ((d, a), (-1, 0))):
        open_edge = ~pad[ci + 1 + oi, cj + 1 + oj]                                      # no cell on that side: a wall of the solid
        e0, e1 = pa[open_edge], pb[open_edge]
        faces += [np.stack([e0, e0 + nb, e1 + nb], 1), np.stack([e0, e1 + nb, e1], 1)]
    Vr, Fr = np.concatenate([Vt, Vb]), np.concatenate(faces)
    if meshutil.volume(Vr, Fr) < 0:
        Fr = Fr[:, ::-1]
    crest = np.stack([XX, YY, zw + t], axis=-1)[(t > 0.3) & valid]                       # the field where it really stands
    tt = np.where(valid, t, -1.0)

    def saddle(name):                     # the highest point of the field on the straight line from a thumb hole to the lip
        tx, ty, _ = sp["thumbs"][name]
        best = -1.0
        for w in np.linspace(0.0, 1.0, 80):
            px, py = tx + w * (o[0] - tx), ty + w * (o[1] - ty)
            i, j = int(np.clip(round((px - x0) / dx - 0.371), 0, nx - 1)), int(np.clip(round((py - y0) / dy - 0.618), 0, ny - 1))
            best = max(best, float(tt[i, j]))
        return best + RIDGE_UNDER_MM

    info = dict(height_mm=sp["h"], width_mm=W, land_mm=sp["land"], window_half_mm=half, window_zone_along_jet_mm=[u_lo, u_hi], tail=sp["tail"],
                thumbs={k: [round(float(c), 2) for c in v] for k, v in sp["thumbs"].items()},
                highest_mm=float(tt.max() + RIDGE_UNDER_MM), plan_area_cm2=float((tt > 0.5).sum() * dx * dy / 100.0),
                between_thumb_and_window_mm={name: saddle(name) for name in sp["thumbs"]})
    return (Vr, Fr), dict(info, crest=crest)


# ------------------------------------------------------------------ the walls of one body

def specs_from(preset) -> list:
    xs = preset.get("inner_wall_x_mm") or {}
    out = []
    for name, x in sorted(xs.items()):
        rf = preset.get("inner_wall_fillet_mm", FILLET_DEFAULT_MM)
        rf = rf.get(name, FILLET_DEFAULT_MM) if isinstance(rf, dict) else rf
        rf = [float(rf), float(rf)] if isinstance(rf, (int, float)) else [float(rf[0]), float(rf[1])]
        out.append(dict(name=name, x=float(x), height=float(preset.get("inner_wall_height", HEIGHT_DEFAULT)),
                        t=float(preset.get("inner_wall_thickness_mm", THICKNESS_DEFAULT_MM)), rf=rf))
    return out


def cut_walls(air, specs, origin_x: float = 0.0, log=lambda *a: None, ridge=None, vs=None, L_window: float = 0.0):
    """air minus the walls and the ridge field. Returns (the new air, wall records with their solids, its topology)."""
    V, F = air
    tree = meshutil.bvh(V, F)
    walls = []
    out = (V, F)
    if ridge is not None:
        solid, info = ridge_solid(air, vs, L_window, ridge)
        before = meshutil.volume(*out)
        a, b, _ = meshutil.boolean(out, solid, "DIFFERENCE")
        out = meshutil.cleanup(a, b, merge_mm=1e-3, no_self_intersection=True)
        info["air_taken_mm3"] = float(before - meshutil.volume(*out))
        log(f"ridge field: {info['height_mm']:g} mm high, takes {info['air_taken_mm3'] / 1000:.3f} cm3 of air; between each thumb hole and "
            f"the window it reaches " + ", ".join(f"{k} {v:.1f} mm" for k, v in info["between_thumb_and_window_mm"].items()))
        LAST["ridge_now"] = dict(info, solid=solid)
        info.pop("crest", None)
    for sp in specs:
        x0 = origin_x + sp["x"]
        loops = slice_x(V, F, x0)
        if not loops:
            raise meshutil.GeometryError(f"inner wall {sp['name']}: the plane x = {x0:.1f} mm does not cut the chamber")
        loop = loops[0]
        z0, z1 = float(loop[:, 1].min()), float(loop[:, 1].max())
        z_top = z0 + sp["height"] * (z1 - z0)
        parts = [slab(x0, sp["t"], z_top)]
        if max(sp["rf"]) > 0:
            strip = fillet_strip(air, tree, loop, x0, sp["t"], sp["rf"], z_top)
            if strip is not None:
                parts.append(strip)
        before = meshutil.volume(*out)
        if len(parts) > 1:                                  # one solid per wall: the slab joined with its fillet strip
            a, b, _ = meshutil.boolean(parts[0], parts[1], "UNION")
            parts = [(a, b)]
        a, b, _ = meshutil.boolean(out, parts[0], "DIFFERENCE")
        out = meshutil.cleanup(a, b, merge_mm=1e-3, no_self_intersection=True)
        taken = before - meshutil.volume(*out)
        rec = dict(sp, x_body=x0, z_bottom=z0, z_top=z_top, section_height_mm=z1 - z0,
                   section_area_mm2=_area(loop), blocked_share=_area_below(loop, z_top) / _area(loop),
                   air_taken_mm3=float(taken), parts=parts, loop=loop)
        log(f"inner wall {sp['name']}: x {x0:+.1f} mm, top edge {z_top - z0:.1f} mm above the thumb-face wall "
            f"({100 * rec['blocked_share']:.0f} % of the section), takes {taken / 1000:.3f} cm3 of air")
        walls.append(rec)
    rep = meshutil.manifold_report(*out)
    if rep["manifold"] and rep["shells"] > 1:
        # crumbs of air cut off under the ridge field (where its foot meets the wall): drop them if they are crumbs
        from ocarina_addon import body as body_mod
        vols = sorted((abs(v) for v in meshutil.shell_volumes(*out)), reverse=True)
        if sum(vols[1:]) > CRUMBS_MAX_MM3:
            raise meshutil.GeometryError(f"the walls cut the air into {len(vols)} parts; the smaller ones hold {sum(vols[1:]):.1f} mm3")
        log(f"{len(vols) - 1} crumbs of air under the ridge field dropped ({sum(vols[1:]):.2f} mm3 in all)")
        out = meshutil.cleanup(*body_mod.largest_shell(*out), merge_mm=1e-3)
        rep = meshutil.manifold_report(*out)
    if not rep["manifold"] or rep["shells"] != 1:
        raise meshutil.GeometryError(f"the walled air is not one closed shell ({rep['shells']} shells, manifold {rep['manifold']})")
    return out, walls, rep


def install(body_mod):
    """Hook the walls into body.build_body from outside: solve_cavity then returns the walled air, with the chamber
    grown until that air holds the target. A preset without inner_wall_x_mm is built exactly as before."""
    if getattr(body_mod.solve_cavity, "_inner_walls", False):
        return
    plain = body_mod.solve_cavity

    def solve_cavity(preset, v, target_cm3, log=lambda *a: None, pocket_guess_mm3: float = 0.0):
        specs = specs_from(preset)
        ridge = ridge_from(preset)
        LAST.clear()
        if not specs and ridge is None:
            return plain(preset, v, target_cm3, log, pocket_guess_mm3)
        extra_mm3, guess, last = 0.0, pocket_guess_mm3, None
        for rnd in range(ROUNDS):
            s = plain(preset, v, target_cm3 + extra_mm3 / 1000.0, log, guess)
            o = np.asarray(s.vs.frame[0], float)
            if ridge is not None:
                # the thumb holes of the body AS IT IS NOW: the layout is made after this step in build_body, from the
                # sizing of the caller. Experiment code: the sizing is read from the caller's frame.
                import sys as _sys
                from ocarina_addon import holes_layout
                fr = _sys._getframe(1).f_locals
                lay = holes_layout.make_layout(s.cav.math, preset, body_mod.cut_rows(fr["sz"], fr["hole_key"]), slide_max_mm=fr["slide_max"])
                ridge["thumbs"] = {h.name: [float(h.centre[0]), float(h.centre[1]), float(h.d_mm)] for h in lay.holes if "thumb" in h.name}
            air, walls, rep = cut_walls(s.air, specs, float(o[0]), log, ridge, s.vs, v.window_length_mm)
            vol = meshutil.volume(*air)
            err = vol / (target_cm3 * 1000.0) - 1.0
            log(f"inner walls, round {rnd}: walled air {vol / 1000:.4f} cm3 ({100 * err:+.5f} %)")
            if abs(err) < VOLUME_TOL:
                break
            # secant step: the walls and the ridge field grow with the chamber, so a plain "add what is missing" creeps
            step = target_cm3 * 1000.0 - vol
            if last is not None and abs(vol - last[1]) > 1e-9:
                step *= (extra_mm3 - last[0]) / (vol - last[1])
            last = (extra_mm3, vol)
            extra_mm3 += step
            guess = s.pocket_mm3
        else:
            raise meshutil.GeometryError("the chamber with inner walls did not reach its volume")
        LAST.update(walls=walls, ridge=LAST.pop("ridge_now", None), plain_air=s.air, plain_air_mm3=float(s.air_mm3), chamber_grown_mm3=float(extra_mm3),
                    walled_air_mm3=float(vol), rounds=rnd + 1)
        return types.SimpleNamespace(cav=s.cav, vs=s.vs, air=air, air_mm3=vol, pocket_mm3=s.pocket_mm3, solver=s.solver,
                                     triangles=rep["triangles"])

    solve_cavity._inner_walls = True
    body_mod.solve_cavity = solve_cavity


# ------------------------------------------------------------------ what was built, measured

def _wall_tree(rec):
    """One BVH per part of the wall, clipped to nothing: distances are taken to the slab and the strip as built."""
    return [meshutil.bvh(*p) for p in rec["parts"]]


def _dist(trees, p) -> float:
    """Distance from a point to the wall (0 or less: the point is in it)."""
    best = 1e9
    for tree in trees:
        if meshutil.inside(tree, p):
            return 0.0
        hit = tree.find_nearest(tuple(float(c) for c in p))
        if hit[0] is not None:
            best = min(best, float(hit[3]))
    return best


def measure(body) -> dict:
    """The walls of the last build against the thumb holes, the window and the pocket."""
    if not LAST.get("walls") and not LAST.get("ridge"):
        return {}
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    L = v.window_length_mm
    win = np.array([o + fx * (q[0] - L) + fy * q[1] for q in vs.outline])            # window outline at the inner plane
    foot = np.array([o + fx * (q[0] - L) + fy * q[1] for q in vs.footprint])         # the pocket's flat footprint
    cav_tree = meshutil.bvh(body.cavity.V, body.cavity.F)
    out = dict(chamber_grown_cm3=LAST["chamber_grown_mm3"] / 1000.0, rounds=LAST["rounds"],
               walled_air_cm3=LAST["walled_air_mm3"] / 1000.0, walls={})
    if LAST.get("ridge"):
        rg = LAST["ridge"]
        crest = rg["crest"]                                           # points of the field where it stands 0.3 mm or more
        near = lambda p: float(np.linalg.norm(crest - np.asarray(p, float), axis=1).min())      # noqa: E731
        out["ridge"] = {k: v for k, v in rg.items() if k not in ("solid", "crest")}
        out["ridge"]["air_taken_cm3"] = rg["air_taken_mm3"] / 1000.0
        out["ridge"]["window_to_ridge_mm"] = min(near(p) for p in win)
        out["ridge"]["pocket_flat_to_ridge_mm"] = min(near(p) for p in foot)
        rims = {}
        for h in body.layout.holes:
            if "thumb" not in h.name:
                continue
            c, ax = np.asarray(h.centre, float), np.asarray(h.axis, float)
            u = np.cross(ax, [1.0, 0.0, 0.0])
            u /= np.linalg.norm(u)
            w = np.cross(ax, u)
            rims[h.name] = min(near(c + 0.5 * h.d_mm * (math.cos(a) * u + math.sin(a) * w))
                               for a in np.linspace(0, 2 * math.pi, 48, endpoint=False))
        out["ridge"]["thumb_rim_to_ridge_mm"] = rims
    for rec in LAST["walls"]:
        trees = _wall_tree(rec)
        holes = {}
        for h in body.layout.holes:
            if "thumb" not in h.name:
                continue
            c, ax = np.asarray(h.centre, float), np.asarray(h.axis, float)
            u = np.cross(ax, [1.0, 0.0, 0.0])
            u /= np.linalg.norm(u)
            w = np.cross(ax, u)
            rim = [c + 0.5 * h.d_mm * (math.cos(a) * u + math.sin(a) * w) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
            # the rim at the chamber wall: the hole's centre lies on the chamber surface, its axis points outward
            holes[h.name] = dict(rim_to_wall_mm=min(_dist(trees, p - 0.3 * ax) for p in rim),
                                 rim_x_range_mm=[float(min(p[0] for p in rim) - o[0]), float(max(p[0] for p in rim) - o[0])])
        # how much of the wall stands in the pocket's own air (the pocket solid outside the loft)
        in_pocket = 0.0
        for part in rec["parts"]:
            try:
                a, b, _ = meshutil.boolean(part, vs.pocket, "INTERSECT")
                c, d, _ = meshutil.boolean((a, b), (body.cavity.V, body.cavity.F), "DIFFERENCE")
                in_pocket += max(meshutil.volume(c, d), 0.0) if len(d) else 0.0
            except Exception:                                    # noqa: BLE001 - no overlap gives an empty mesh
                pass
        out["walls"][rec["name"]] = dict(
            x_mm=rec["x"], thickness_mm=rec["t"], fillet_mm=rec["rf"], height_share=rec["height"],
            top_above_thumb_wall_mm=rec["z_top"] - rec["z_bottom"], section_height_mm=rec["section_height_mm"],
            section_area_mm2=rec["section_area_mm2"], blocked_share=rec["blocked_share"],
            air_taken_cm3=rec["air_taken_mm3"] / 1000.0, has_fillet=max(rec["rf"]) > 0,
            footprint_x_mm=[rec["x"] - 0.5 * rec["t"] - rec["rf"][0], rec["x"] + 0.5 * rec["t"] + rec["rf"][1]],
            window_to_wall_mm=min(_dist(trees, p) for p in win),
            pocket_flat_to_wall_mm=min(_dist(trees, p) for p in foot),
            in_pocket_air_mm3=in_pocket, thumb_holes=holes)
    del cav_tree
    return out


def room(body) -> dict:
    """Where a wall could stand on a body WITHOUT walls: the window, the pocket and the thumb holes along the body
    (x from the lip, mm), and the air section at a few stations."""
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    L = v.window_length_mm

    def xs(poly):
        P = np.array([o + fx * (q[0] - L) + fy * q[1] for q in poly])
        return [float(P[:, 0].min() - o[0]), float(P[:, 0].max() - o[0])]

    pV = np.asarray(vs.pocket[0], float)
    out = dict(lip_x_body=float(o[0]), jet_direction=[float(c) for c in fx], window_x_mm=xs(vs.outline), pocket_flat_x_mm=xs(vs.footprint),
               pocket_solid_x_mm=[float(pV[:, 0].min() - o[0]), float(pV[:, 0].max() - o[0])],
               pocket_blend=vs.info.get("pocket_blend"), holes={}, sections={})
    # the skirt of the pocket as built: where the walled-free air differs from the loft, along the body
    air = body.voicing_air
    for h in body.layout.holes:
        if "thumb" in h.name:
            c = np.asarray(h.centre, float)
            out["holes"][h.name] = dict(centre_mm=[float(c[0] - o[0]), float(c[1]), float(c[2])], d_mm=float(h.d_mm),
                                        x_range_mm=[float(c[0] - o[0] - 0.5 * h.d_mm), float(c[0] - o[0] + 0.5 * h.d_mm)])
    cav = (np.asarray(body.cavity.V, float), np.asarray(body.cavity.F))
    for x in np.arange(-24.0, 30.1, 1.0):
        la, lc = slice_x(*air, o[0] + x), slice_x(*cav, o[0] + x)
        if not la or not lc:
            continue
        A, C = la[0], lc[0]
        out["sections"][f"{x:+.0f}"] = dict(air_mm2=_area(A), loft_mm2=_area(C), pocket_adds_mm2=_area(A) - _area(C),
                                           height_mm=float(A[:, 1].max() - A[:, 1].min()), width_mm=float(A[:, 0].max() - A[:, 0].min()))
    return out
