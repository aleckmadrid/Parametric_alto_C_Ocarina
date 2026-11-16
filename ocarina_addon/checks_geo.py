"""Pre-export checks (docs/02, Phase 4 step 8) and the geometry measurements behind them.

Every number here is MEASURED on a mesh: slices, ray casts, areas and volumes of the final body. The
kernel record says what the number should be. `measure()` works on any (V, F), so the geometry check
script can run it on the STL file that was written to disk.

    run_all(body, params)            measure body.solid, fill body.measurements and body.checks
    measure(body, V, F)              the measurements alone, on the given mesh

A check is a dict: name, status, value, limit, message, expected. The status is one of

    "pass"       inside the rule (the docs say "ok")
    "needs_fem"  the cavity-mode desk check lies between the hard limit and the comfortable margin
    "fail"       outside a hard limit
    "warn"       a soft ergonomic check (ergo_*) is outside its range. A warning is never a failure:
                 unexpected_failures() ignores it, and so does --strict.
    "info"       a number that is reported and decides nothing

`expected` marks a failure that the notes list as expected (see expected_failure); it is not a bug.

Two groups of checks do not come from the mesh alone:
    ergo_*                 the hand layout, measured by ocarina_addon/ergonomics.py on the built hole centres
    cavity_mode_computed   the first cavity mode of the exported capped air mesh, computed in a second Python
                           process (ocarina_addon/cavity_mode.py). The kernel's c/(2L) result is shown as
                           cavity_mode_c2L with status "info".
"""
from __future__ import annotations

import math
import os
import shutil
import tempfile

import numpy as np

from . import body as body_mod
from . import cavity_math, cavity_mode, ergonomics, export, kernel_bridge, meshutil, render, voicing_geo

TOL_MM = 0.05                  # hole diameter, chimney, window sizes (the Phase 4 gate)
TOL_VOLUME = 0.005             # 0.5 %
TOL_AREA_REL = 0.002
TOL_ANGLE_DEG = 0.5
TOL_AXIS_DEG = 2.0             # hole axis against the local cavity normal (the mesh is faceted)
MIN_GAP_MM = 3.4
TUBE_CLEAR_WALL_MM = 5.0       # an inward tube must end this far from the opposite cavity wall
TUBE_CLEAR_TUBE_MM = 2.0
MIN_FLOOR_LIP_MM = 0.8         # plastic under the windway floor at the exit
WALL_TOL_MM = 0.03             # the offset skin is faceted: 4.00 mm measures as about 3.99


def expected_failure(preset_id: str, v0_cm3: float, name: str, status: str) -> bool:
    """Failures that the build notes list as expected (prompts/addon-v1-notes.md, "Expected failing checks")."""
    if name == "hole_limits[nominal]" and status == "fail":
        return v0_cm3 >= 65.0 - 1e-9
    if name == "hole_limits[print]" and status == "fail":
        return v0_cm3 >= 80.0 - 1e-9
    if name == "hole_limits[fitted]" and status == "fail":
        # Stage 3: holes sized with the fitted constants. A hole above the pad limit is the round-hole verdict
        # of doc 04 (Gate 2), which the stage report states in a block of its own. It is not a fault of the build.
        return True
    return False


def _check(name, ok, value, limit, message, status=None):
    return dict(name=name, status=status or ("pass" if ok else "fail"), value=value, limit=limit, message=message,
                expected=False)


# ====================================================================== measurements

def _loop_through(segs2d, seed_index):
    """Connected chain of 2-D segments that contains segment `seed_index` (end points matched by rounding)."""
    key = lambda p: (round(float(p[0]), 5), round(float(p[1]), 5))
    ends = {}
    for i, s in enumerate(segs2d):
        for p in s:
            ends.setdefault(key(p), []).append(i)
    seen, stack = {seed_index}, [seed_index]
    while stack:
        i = stack.pop()
        for p in segs2d[i]:
            for j in ends[key(p)]:
                if j not in seen:
                    seen.add(j)
                    stack.append(j)
    return segs2d[sorted(seen)]


def _loop_stats(loop, centre=(0.0, 0.0)):
    """Area (star-shaped about `centre`), perimeter, centroid and radius range of a loop of 2-D segments."""
    c = np.asarray(centre, float)
    a, b = loop[:, 0, :] - c, loop[:, 1, :] - c
    cross = np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])
    area = 0.5 * float(cross.sum())
    perim = float(np.linalg.norm(loop[:, 1, :] - loop[:, 0, :], axis=1).sum())
    w = cross / max(cross.sum(), 1e-30)
    centroid = ((loop[:, 0, :] + loop[:, 1, :] + c) / 3.0 * w[:, None]).sum(axis=0)
    r = np.linalg.norm(loop.reshape(-1, 2) - c, axis=1)
    return dict(area=area, perimeter=perim, centroid=centroid, r_min=float(r.min()), r_max=float(r.max()))


def _plane_basis(n):
    n = np.asarray(n, float) / np.linalg.norm(n)
    h = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(n, h)
    u /= np.linalg.norm(u)
    return u, np.cross(n, u), n


def _chords(loop, xs, y_limit=None):
    """Width of a loop (2-D segments in x, y) along each vertical line x = xs[i]: max y - min y."""
    out = np.zeros(len(xs))
    x0, y0, x1, y1 = loop[:, 0, 0], loop[:, 0, 1], loop[:, 1, 0], loop[:, 1, 1]
    for i, x in enumerate(xs):
        hit = ((x0 - x) * (x1 - x) <= 0) & (np.abs(x1 - x0) > 1e-12)
        if not hit.any():
            continue
        y = y0[hit] + (y1[hit] - y0[hit]) * (x - x0[hit]) / (x1[hit] - x0[hit])
        if y_limit is not None:
            y = y[np.abs(y) <= y_limit]
        if len(y) >= 2:
            out[i] = y.max() - y.min()
    return out


def measure_voicing(body, V, F, tree) -> dict:
    """Window, windway and labium numbers measured on the mesh, in the voicing frame."""
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = vs.frame
    L, W, wall, e = v.window_length_mm, v.window_width_mm, v.wall_at_window_mm, v.labium_edge_thickness_mm
    Lw = v.windway_length_mm
    m = {}

    def to_body(xw, y, z):
        return o + fx * (xw - L) + fy * y + fz * z

    def slice_z(z):
        S = render.section_2d(V, F, to_body(0.0, 0.0, z), fz, fx, fy)        # u = xw, v = y
        return S

    # --- window: the labium half from the slice at the edge level, the windway half from a slice above the windway roof
    A = slice_z(0.5 * e)
    B = slice_z(0.6 * wall)
    selA = A[(np.abs(A[..., 1]).max(axis=1) <= 0.5 * W + 1.0) & (A[..., 0].min(axis=1) >= -1.0) & (A[..., 0].max(axis=1) <= L + 1.0)]
    selB = B[(np.abs(B[..., 1]).max(axis=1) <= 0.5 * W + 0.02) & (B[..., 0].min(axis=1) >= -1.0) & (B[..., 0].max(axis=1) <= L + 1.0)]
    ptsA = selA.reshape(-1, 2)
    m["window_width_mm"] = float(ptsA[:, 1].max() - ptsA[:, 1].min())
    wide = ptsA[np.abs(ptsA[:, 1]) >= 0.5 * m["window_width_mm"] - 2e-5]     # the mesh has a vertex at the widest point
    x_split = float(wide[:, 0].max())                                         # the widest point, measured
    m["widest_point_xw_mm"] = x_split
    tip_x = float(ptsA[:, 0].max())
    back_x = float(selB.reshape(-1, 2)[:, 0].min())
    m["window_tip_xw_mm"] = tip_x
    m["window_back_xw_mm"] = back_x
    m["window_length_mm"] = tip_x - back_x
    m["window_tip_y_mm"] = float(ptsA[np.argmax(ptsA[:, 0]), 1])
    xs_back = np.linspace(back_x, x_split, 600)
    xs_front = np.linspace(x_split, tip_x, 900)
    area = float(np.trapezoid(_chords(selB, xs_back, 0.5 * W + 0.02), xs_back) + np.trapezoid(_chords(selA, xs_front), xs_front))
    m["window_area_mm2"] = area
    m["broad_end_at_windway"] = bool(x_split - back_x <= 0.5 * (tip_x - back_x) + 0.02)

    # --- windway cross-sections just inside the exit and just inside the mouth end
    def duct_at(xw):
        S = render.section_2d(V, F, to_body(xw, 0.0, 0.0), fx, fy, fz)       # u = y, v = z
        zc = voicing_geo.windway_centre_z(v)
        S = S[(np.abs(S[..., 0]).max(axis=1) <= 0.5 * W + 0.5) & (np.abs(S[..., 1] - zc).max(axis=1) <= 1.5)]
        if len(S) == 0:
            return None
        mid = 0.5 * (S[:, 0, :] + S[:, 1, :])
        seed = int(np.argmin(np.hypot(mid[:, 0], mid[:, 1] - zc - 0.5 * v.windway_exit_height_mm)))
        loop = _loop_through(S, seed)
        p = loop.reshape(-1, 2)
        return dict(width=float(p[:, 0].max() - p[:, 0].min()), height=float(p[:, 1].max() - p[:, 1].min()),
                    centre_y=float(0.5 * (p[:, 0].max() + p[:, 0].min())), centre_z=float(0.5 * (p[:, 1].max() + p[:, 1].min())),
                    floor_z=float(p[:, 1].min()), roof_z=float(p[:, 1].max()))

    d_off = 0.3                     # slice a little inside each end, then extend the measured taper to the end
    ex, inl = duct_at(-d_off), duct_at(-Lw + d_off)
    if ex is None or inl is None:
        raise meshutil.GeometryError("the windway was not found in the mesh")
    slope = (inl["height"] - ex["height"]) / (Lw - 2 * d_off)
    m["windway_exit_height_mm"] = ex["height"] - slope * d_off
    m["windway_inlet_height_mm"] = inl["height"] + slope * d_off
    m["windway_exit_width_mm"] = ex["width"]
    m["windway_inlet_width_mm"] = inl["width"]
    m["windway_exit_centre_z_mm"] = ex["centre_z"]
    m["windway_exit_centre_y_mm"] = ex["centre_y"]
    m["windway_exit_floor_z_mm"] = ex["floor_z"]
    m["windway_roof_thickness_mm"] = wall - ex["roof_z"]

    # --- labium: top surface behind the edge (rays from outside), underside (rays from the cavity)
    def top_z(xw, y=0.0):
        hits = meshutil.ray_hits(tree, to_body(xw, y, 30.0), -fz, 60.0)
        return 30.0 - hits[0][0] if hits else None

    def under_z(xw, y=0.0):
        hits = meshutil.ray_hits(tree, to_body(xw, y, -4.0), fz, 30.0)
        return -4.0 + hits[0][0] if hits else None

    ss = np.array([0.5, 1.0, 1.5, 2.0, 3.0, 4.0])
    zt = np.array([top_z(tip_x + s) for s in ss], dtype=float)
    k = np.polyfit(ss, zt, 1)
    m["labium_angle_deg"] = math.degrees(math.atan(k[0]))
    m["labium_ramp_residual_mm"] = float(np.abs(np.polyval(k, ss) - zt).max())
    s0 = 0.02
    zt0, zb0 = top_z(tip_x + s0), under_z(tip_x + s0)
    m["labium_edge_thickness_mm"] = float(zt0 - zb0 - s0 * k[0])
    m["labium_edge_mid_z_mm"] = float(0.5 * (zt0 - s0 * k[0] + zb0))
    m["labium_offset_mm"] = m["labium_edge_mid_z_mm"] - ex["centre_z"]
    m["labium_underside_z_mm"] = float(zb0)

    # --- floor lip under the windway exit: plastic between the windway floor and the cavity, just behind the exit
    hits = meshutil.ray_hits(tree, to_body(-0.15, 0.0, ex["floor_z"] - 0.02), -fz, 30.0)
    m["windway_floor_lip_mm"] = float(hits[0][0] + 0.02) if hits else float("nan")

    # --- orientation
    # the windway runs toward +x and ends at the back of the window; the labium tip lies ahead of it on the centre line
    m["windway_exit_faces_labium"] = bool(tip_x > back_x and abs(back_x) < 0.05 and abs(ex["centre_y"]) < 0.05
                                          and abs(m["window_tip_y_mm"]) < 0.05 and ex["floor_z"] < m["labium_edge_mid_z_mm"] < ex["roof_z"])
    mid = to_body(x_split, 0.0, 0.5 * wall)
    out_hits = meshutil.ray_hits(tree, mid, fz, 400.0)
    in_hits = meshutil.ray_hits(tree, mid, -fz, 400.0)
    m["window_opens_outward"] = bool(len(out_hits) == 0)
    m["depth_below_window_mm"] = float(in_hits[0][0] - 0.5 * wall) if in_hits else float("inf")

    # --- keep-out outside: nothing above a 45 degree flare from the window rim at the outer face
    Pv = (V - o) @ np.stack([fx, fy, fz], axis=1)
    near = (np.abs(Pv[:, 0] + 0.5 * L) < 45.0) & (np.abs(Pv[:, 1]) < 45.0) & (Pv[:, 2] > wall + 1e-3)
    m["flare_violations"] = int(near.sum())
    m["max_height_above_outer_face_mm"] = float((Pv[near, 2] - wall).max()) if near.any() else 0.0
    return m


def measure_keepout_inside(body, tree, n: int = 3000, seed: int = 1) -> dict:
    """Keep-out inside: within keepout_inside_mm of the labium, on the cavity side, there must be no plastic
    where the cavity air (loft joined with the pocket) should be. Sampled with a fixed seed."""
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = vs.frame
    r = v.keepout_inside_mm
    rng = np.random.default_rng(seed)
    air_tree = meshutil.bvh(*body.voicing_air)
    bad = tested = 0
    while tested < n:
        p = rng.uniform(-r, r, 3)
        if p[2] > -0.2 or np.linalg.norm(p) > r:
            continue
        q = o + fx * p[0] + fy * p[1] + fz * p[2]
        if not meshutil.inside(air_tree, q):
            continue                               # in the wall beside the pocket: the wall that carries the labium
        tested += 1
        if meshutil.inside(tree, q):
            # a point within 0.05 mm of a surface is not an intrusion: all six neighbours must be plastic too
            d = 0.05
            if all(meshutil.inside(tree, q + s * d * ax) for ax in (fx, fy, fz) for s in (-1.0, 1.0)):
                bad += 1
    return dict(points_tested=tested, points_in_plastic=bad)


def measure_holes(body, V, F, tree) -> list:
    """Per hole: diameter from a slice at mid wall, chimney from an axis ray on the body before the cuts,
    bore wall length, axis against the cavity normal, tube numbers."""
    pre_tree = meshutil.bvh(*body.precut)
    cav_tree = meshutil.bvh(body.cavity.V, body.cavity.F)
    cav_normals = meshutil.face_normals(body.cavity.V, body.cavity.F)
    FN = meshutil.face_normals(V, F)
    FC = V[F].mean(axis=1)
    a_, b_, c_ = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    FA = 0.5 * np.linalg.norm(np.cross(b_ - a_, c_ - a_), axis=1)
    tube_wall = body.params["tube_wall_mm"]
    out = []
    for h in body.layout.holes:
        p, n = np.asarray(h.centre, float), np.asarray(h.axis, float)
        u, w, _ = _plane_basis(n)
        row = dict(name=h.name, deck=h.deck, d_kernel_mm=h.d_mm, chimney_kernel_mm=h.chimney_mm, tube_kernel_mm=h.tube_mm,
                   moved_mm=h.moved_mm, tilt_deg=h.tilt_deg, centre=[float(x) for x in p], axis=[float(x) for x in n])

        def loops_at(depth):
            S = render.section_2d(V, F, p + n * depth, n, u, w)
            if len(S) == 0:
                return []
            mid = 0.5 * (S[:, 0, :] + S[:, 1, :])
            rad = np.hypot(mid[:, 0], mid[:, 1])
            near = S[rad < 0.5 * h.d_mm + tube_wall + 3.0]
            found = []
            remaining = near
            for _ in range(3):
                if len(remaining) == 0:
                    break
                mid = 0.5 * (remaining[:, 0, :] + remaining[:, 1, :])
                seed = int(np.argmin(np.hypot(mid[:, 0], mid[:, 1])))
                loop = _loop_through(remaining, seed)
                found.append(_loop_stats(loop))
                key = {tuple(np.round(s.ravel(), 5)) for s in loop}
                remaining = np.array([s for s in remaining if tuple(np.round(s.ravel(), 5)) not in key]).reshape(-1, 2, 2)
            return found

        loops = loops_at(0.5 * h.wall_mm)
        if not loops:
            raise meshutil.GeometryError(f"hole {h.name}: no bore found in the mesh")
        bore = loops[0]
        row["d_measured_mm"] = 2.0 * math.sqrt(bore["area"] / math.pi)
        row["d_error_mm"] = row["d_measured_mm"] - h.d_mm
        row["bore_r_min_mm"], row["bore_r_max_mm"] = bore["r_min"], bore["r_max"]
        row["centre_offset_mm"] = float(np.linalg.norm(bore["centroid"]))

        # chimney: axis ray on the body BEFORE the hole cut (doc 02, Phase 4 step 5: "chimney ray-cast")
        hits = meshutil.ray_hits(pre_tree, p + n * 40.0, -n, 120.0)
        row["chimney_measured_mm"] = float(hits[1][0] - hits[0][0]) if len(hits) >= 2 else float("nan")
        row["chimney_error_mm"] = row["chimney_measured_mm"] - h.chimney_mm

        # bore wall of the final mesh: faces on the cylinder, normals toward the axis
        rel = FC - p
        ax = rel @ n
        radial = rel - np.outer(ax, n)
        rho = np.linalg.norm(radial, axis=1)
        inward = -(np.einsum("ij,ij->i", FN, radial)) / np.maximum(rho, 1e-9)
        r_c = 0.5 * row["d_measured_mm"]
        sel = (np.abs(rho - r_c) < 0.06 * r_c + 0.02) & (inward > 0.9) & (ax > -(h.tube_mm + 1.0)) & (ax < h.wall_mm + 2.5)
        if sel.sum() >= 8:
            row["bore_wall_mean_length_mm"] = float(FA[sel].sum() / bore["perimeter"])
            _, _, vt = np.linalg.svd(FN[sel], full_matrices=False)
            axis_m = vt[-1]
            axis_m = axis_m if axis_m @ n > 0 else -axis_m
            loc, nrm, idx, dist = cav_tree.find_nearest(tuple(p))
            row["axis_vs_cavity_normal_deg"] = math.degrees(math.acos(min(1.0, abs(float(axis_m @ cav_normals[idx])))))
            row["axis_vs_formula_deg"] = math.degrees(math.acos(min(1.0, abs(float(axis_m @ n)))))
            vsel = V[np.unique(F[sel])]
            row["bore_inner_end_mm"] = float(((vsel - p) @ n).min())
        else:
            row["bore_wall_mean_length_mm"] = float("nan")
            row["axis_vs_cavity_normal_deg"] = float("nan")

        if h.tube_mm > 0:
            tl = loops_at(-0.5 * h.tube_mm)
            row["tube_length_measured_mm"] = -row.get("bore_inner_end_mm", float("nan"))
            if len(tl) >= 2:
                r_in, r_out = math.sqrt(tl[0]["area"] / math.pi), math.sqrt(tl[1]["area"] / math.pi)
                row["tube_wall_measured_mm"] = r_out - r_in
                row["tube_bore_d_measured_mm"] = 2.0 * r_in
            end = p - n * h.tube_mm
            # against the cavity loft, not the finished body: the ray may point at a hole in the opposite wall
            hits = meshutil.ray_hits(cav_tree, end - n * 0.05, -n, 300.0)
            row["tube_to_opposite_wall_mm"] = float(hits[0][0] + 0.05) if hits else float("inf")
            lab = np.asarray(body.voicing.frame[0], float)
            t = np.clip((lab - p) @ (-n), 0.0, h.tube_mm)
            row["tube_to_labium_mm"] = float(np.linalg.norm(lab - (p - n * t)) - (0.5 * h.d_mm + tube_wall))
        out.append(row)
    # edge gaps from the measured bores (at the cavity surface: the axes spread outward, so this is the smallest)
    for i, a in enumerate(out):
        a["nearest_gap_mm"], a["nearest_hole"] = float("inf"), ""
    for i, a in enumerate(out):
        for b in out[i + 1:]:
            gap = float(np.linalg.norm(np.array(a["centre"]) - np.array(b["centre"])) - 0.5 * (a["d_measured_mm"] + b["d_measured_mm"]))
            if gap < a["nearest_gap_mm"]:
                a["nearest_gap_mm"], a["nearest_hole"] = gap, b["name"]
            if gap < b["nearest_gap_mm"]:
                b["nearest_gap_mm"], b["nearest_hole"] = gap, a["name"]
    # tube to tube
    tubes = [r for r in out if r["tube_kernel_mm"] > 0]
    for i, a in enumerate(tubes):
        a["tube_to_tube_mm"] = float("inf")
        for b in tubes:
            if a is b:
                continue
            d = _segment_distance(np.array(a["centre"]), np.array(a["centre"]) - np.array(a["axis"]) * a["tube_kernel_mm"],
                                  np.array(b["centre"]), np.array(b["centre"]) - np.array(b["axis"]) * b["tube_kernel_mm"])
            a["tube_to_tube_mm"] = min(a["tube_to_tube_mm"], d - 0.5 * (a["d_kernel_mm"] + b["d_kernel_mm"]) - 2 * tube_wall)
    return out


def _segment_distance(p1, q1, p2, q2, n: int = 40):
    t = np.linspace(0.0, 1.0, n)
    A = p1[None, :] + (q1 - p1)[None, :] * t[:, None]
    B = p2[None, :] + (q2 - p2)[None, :] * t[:, None]
    return float(np.linalg.norm(A[:, None, :] - B[None, :, :], axis=2).min())


def measure_hole_to_voicing(body, holes) -> dict:
    """3-D distance from each hole edge (at the outer skin) to the window outline, to the rim of the labium
    ramp and to the voicing block with its mouthpiece stub."""
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = vs.frame
    L, wall = v.window_length_mm, v.wall_at_window_mm
    out2 = vs.outline[:, :2]
    reach = (wall - v.labium_edge_thickness_mm) / math.tan(math.radians(v.labium_ramp_angle_deg))
    nx, ny = np.cos(vs.outline[:, 2]), np.sin(vs.outline[:, 2])
    if v.shape == "teardrop":
        f = np.array([voicing_geo.ramp_reach_factor(abs(t)) for t in vs.outline[:, 2]])
    else:
        f = np.array([1.0 if abs(t) < math.radians(45.0) else 0.0 for t in vs.outline[:, 2]])
    scoop = out2 + (f * reach)[:, None] * np.column_stack([nx, ny])           # rim of the ramp at the outer face
    half_w = vs.info["block_half_width_mm"]
    lo = np.array([-v.windway_length_mm, -half_w, vs.info["block_z_bottom_mm"]])
    hi = np.array([L + voicing_geo.BLOCK_FRONT_MM, half_w, wall])
    res = {}
    for r in holes:
        p = np.asarray(r["centre"], float) + np.asarray(r["axis"], float) * body.params["wall_mm"]     # at the outer skin
        q = (p - o) @ np.stack([fx, fy, fz], axis=1)
        q[0] += L                                                             # xw, y, z
        rad = 0.5 * r["d_measured_mm"]
        d_win = float(np.sqrt((out2[:, 0] - q[0]) ** 2 + (out2[:, 1] - q[1]) ** 2 + (wall - q[2]) ** 2).min() - rad)
        d_scoop = float(np.sqrt((scoop[:, 0] - q[0]) ** 2 + (scoop[:, 1] - q[1]) ** 2 + (wall - q[2]) ** 2).min() - rad)
        d_block = float(np.linalg.norm(q - np.clip(q, lo, hi)) - rad)
        res[r["name"]] = dict(to_window_mm=d_win, to_ramp_mm=d_scoop, to_block_mm=d_block)
    return res


def measure_wall(body, V, F, tree) -> dict:
    """Wall thickness. (1) Cavity to envelope along the cavity normals (the plain wall, before any cut).
    (2) Thinnest plastic in the final mesh away from the voicing and the tubes, by rays through the plastic."""
    cav = body.cavity
    env_tree = meshutil.bvh(*body.envelope)
    N = meshutil.vertex_normals(cav.V, cav.F)
    idx = np.arange(0, len(cav.V), 7)
    t = []
    for i in idx:
        hits = meshutil.ray_hits(env_tree, cav.V[i] + N[i] * 1e-3, N[i], 60.0)
        if hits:
            t.append(hits[0][0] + 1e-3)
    t = np.array(t)
    out = dict(shell_min_mm=float(t.min()), shell_median_mm=float(np.median(t)), shell_samples=int(len(t)))

    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = vs.frame
    L, W = v.window_length_mm, v.window_width_mm
    reach = vs.info["ramp_reach_mm"]
    FN = meshutil.face_normals(V, F)
    FC = V[F].mean(axis=1)
    Pv = (FC - o) @ np.stack([fx, fy, fz], axis=1)
    in_voicing = ((Pv[:, 0] > -L - v.windway_length_mm - 1.0) & (Pv[:, 0] < reach + 2.0)
                  & (np.abs(Pv[:, 1]) < 0.5 * W + reach + 2.0) & (Pv[:, 2] > -6.0) & (Pv[:, 2] < v.wall_at_window_mm + 1.0))
    near_tube = np.zeros(len(FC), dtype=bool)
    tw = body.params["tube_wall_mm"]
    for h in body.layout.holes:
        if h.tube_mm <= 0:
            continue
        rel = FC - np.asarray(h.centre)
        ax = rel @ np.asarray(h.axis)
        rho = np.linalg.norm(rel - np.outer(ax, h.axis), axis=1)
        near_tube |= (rho < 0.5 * h.d_mm + tw + 0.3) & (ax < 0.5) & (ax > -h.tube_mm - 0.5)
    a_, b_, c_ = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    big = 0.5 * np.linalg.norm(np.cross(b_ - a_, c_ - a_), axis=1) > 2e-3      # skip sliver triangles: their normals are noise
    cand = np.nonzero(~in_voicing & ~near_tube & big)[0]
    rng = np.random.default_rng(3)
    pick = cand if len(cand) <= 6000 else rng.choice(cand, 6000, replace=False)
    thin, where = float("inf"), None
    for i in pick:
        hits = meshutil.ray_hits(tree, FC[i] - FN[i] * 0.02, -FN[i], 80.0)
        # A wall has two faces that look away from each other. Next to an edge (a hole rim) a ray leaves
        # through the neighbouring face after a very short way; that is not a thin wall, so it is skipped.
        if hits and float(np.dot(FN[i], hits[0][1])) < -0.5 and hits[0][0] + 0.02 < thin:
            thin, where = hits[0][0] + 0.02, FC[i]
    out["final_min_thickness_mm"] = float(thin)
    out["final_min_thickness_at"] = [float(x) for x in where] if where is not None else None
    out["final_samples"] = int(len(pick))
    return out


def _reach(S, sign: float, gap_mm: float = 1.0) -> float:
    """How far the solid reaches from u = 0 in the direction `sign` along the u axis of a section (segments
    S in plane coordinates). The segments of a closed section cover its whole extent, so the reach is the end
    of the run of covered u that starts at 0; a break longer than gap_mm ends the run."""
    u = np.sort(S[..., 0] * sign, axis=1)
    order = np.argsort(u[:, 0])
    reach = 0.0
    for lo, hi in u[order]:
        if hi < 0.0:
            continue
        if lo > reach + gap_mm:
            break
        reach = max(reach, hi)
    return float(reach)


def measure_ergonomics(body, V, F, holes) -> dict:
    """The hand layout in the frame of the hands (ocarina_addon/ergonomics.py).

    inner   metrics from the hole centres on the cavity surface. They decide the ergo_* checks: this is the
            convention of docs/06 and of measure_cad_references.py for the add-on bodies.
    outer   the same from the hole centres at the outer skin (centre + wall x axis), where the fingers are.
            The hole axes spread outward, so these distances are larger. Reported beside the others.
    rest    from each pinky hole centre to the end of the body, along the hand axis in the plan view, measured
            on the mesh: the body is cut by the vertical plane through the hole centre along the hand axis.
    """
    if not holes:
        return {}
    wall = body.params["wall_mm"]
    inner, outer = {}, {}
    for r in holes:
        c, ax = np.asarray(r["centre"], float), np.asarray(r["axis"], float)
        inner[r["name"]] = dict(centre=ergonomics.body_to_player(c), axis=ergonomics.body_to_player(ax), d_mm=r["d_measured_mm"])
        outer[r["name"]] = dict(centre=ergonomics.body_to_player(c + wall * ax), axis=ergonomics.body_to_player(ax), d_mm=r["d_measured_mm"])
    m_in, m_out = ergonomics.layout_metrics(inner), ergonomics.layout_metrics(outer)
    a = m_in["a"]
    a3 = np.array([a[0], -a[1], 0.0])                       # the hand axis in body coordinates (player Y = -body Y)
    z3 = np.array([0.0, 0.0, 1.0])
    by = {r["name"]: r for r in holes}
    rest = {}
    for end, name, sign in (("bulb", "L_pinky", -1.0), ("tail", "R_pinky", 1.0)):
        S = render.section_2d(V, F, np.asarray(by[name]["centre"], float), np.cross(z3, a3), a3, z3)
        rest[end] = _reach(S, sign)
    return dict(inner=m_in, outer=m_out, rest=rest, taped=body.layout.kind == "relative")


def measure_cavity_mode(body) -> dict:
    """First cavity mode of the capped air mesh, computed outside Blender on the exported STL file. When the
    body was not exported, the air mesh is written to a temporary file for the solver."""
    sz = body.sizing
    path = body.files.get("air_capped_stl")
    tmp = None
    if not path or not os.path.isfile(path):
        tmp = tempfile.mkdtemp(prefix="oca_mode_")
        path = export.write_stl(os.path.join(tmp, f"{body.body_id}_air_capped.stl"), *body.air_capped)
    try:
        res = cavity_mode.run(path, float(sz.f_targets_hz[-1]), float(sz.c_m_s))
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    res["source"] = "a temporary export of the air mesh" if tmp else os.path.basename(path)
    if tmp:
        res.pop("result_file", None)
        res.pop("stl", None)
    return res


def measure(body, V=None, F=None, capped_step_mm: float = 0.25) -> dict:
    """All measurements on the mesh (default: the body's final mesh)."""
    if V is None:
        V, F = body.solid
    tree = meshutil.bvh(V, F)
    rep = meshutil.manifold_report(V, F)
    rep["self_intersections"] = meshutil.self_intersections(V, F)
    n_v, n_f = rep["vertices"] - rep["unused_vertices"], rep["triangles"]
    n_e = 3 * n_f // 2
    rep["euler_characteristic"] = n_v - n_e + n_f
    rep["genus"] = (2 * rep["shells"] - rep["euler_characteristic"]) // 2
    sz = body.sizing
    m = dict(topology=rep)
    m["volume"] = dict(
        cavity_mesh_target_cm3=sz.cavity_volume_for_mesh_cm3, cavity_mesh_cm3=body.cavity_air_cm3,
        loft_cm3=body.cavity.volume_cm3, pocket_cm3=body.pocket_cm3,
        v0_target_cm3=body.params.get("capped_target_cm3", sz.v0_cm3), v0_kernel_cm3=sz.v0_cm3,
        volume_factor=sz.volume_factor, capped_air_built_cm3=body.air_capped_cm3,
        capped_air_measured_cm3=body_mod.measure_capped_air_cm3(body.envelope, (V, F), body.voicing, sz.voicing, capped_step_mm),
        capped_air_measure_step_mm=capped_step_mm, body_plastic_cm3=meshutil.volume(V, F) / 1000.0,
        air_fem_cm3=meshutil.volume(*body.air_fem) / 1000.0)
    m["voicing"] = measure_voicing(body, V, F, tree)
    m["keepout_inside"] = measure_keepout_inside(body, tree)
    m["holes"] = measure_holes(body, V, F, tree)
    m["hole_to_voicing"] = measure_hole_to_voicing(body, m["holes"])
    m["wall"] = measure_wall(body, V, F, tree)
    m["ergonomics"] = measure_ergonomics(body, V, F, m["holes"])
    m["layout"] = dict(kind=body.layout.kind, hand_overlap_mm=body.layout.overlap_mm, subholes=body.layout.subholes,
                       sideways_limits=[(n, float(a), float(u)) for n, a, u in body.layout.clamps],
                       messages=body.layout.messages,
                       smallest_gaps=[(a, b, float(g)) for a, b, g in body.layout.gaps[:5]])
    m["cavity"] = dict(length_mm=body.cavity.length_mm, scale=body.cavity.scale,
                       port_vertex_distance_mm=float(np.linalg.norm(body.cavity.V, axis=1).min()))
    return m


# ====================================================================== checks

def evaluate(body, m, params) -> list:
    k = kernel_bridge.kernel()
    sz, v = body.sizing, body.sizing.voicing
    C = []

    # ---- kernel checks (range ratio, cavity length ratio, W/h, hole floor and pad limits)
    for c in sz.checks:
        d = dict(c.to_dict(), expected=False)
        if d["name"] == "cavity_mode":
            # The kernel's c/(2L) estimate stays in the kernel unchanged. Here it is a reported number only
            # (owner decision of 2026-11-15, doc 02 Q9 / A12): the verdict is cavity_mode_computed below.
            d = dict(name="cavity_mode_c2L", status="info", value=d["value"], limit=d["limit"], expected=False,
                     message=f"kernel estimate from the length of the chamber, reported only: {d['message']} "
                             f"(the kernel's own status: {d['status']}). c/(2L) is the lowest estimate; the verdict is "
                             f"`cavity_mode_computed`")
        C.append(d)
    C.append(_cavity_mode_check(m.get("cavity_mode"), params))

    # ---- volume
    vol = m["volume"]
    e1 = vol["cavity_mesh_cm3"] / vol["cavity_mesh_target_cm3"] - 1.0
    C.append(_check("volume_cavity_mesh", abs(e1) <= TOL_VOLUME, 100 * e1, 100 * TOL_VOLUME,
                    f"cavity mesh (loft {vol['loft_cm3']:.3f} + voicing pocket {vol['pocket_cm3']:.3f}) = {vol['cavity_mesh_cm3']:.4f} cm³ "
                    f"against the kernel's {vol['cavity_mesh_target_cm3']:.4f} cm³: {100 * e1:+.4f} % (limit 0.5 %)"))
    e2 = vol["capped_air_measured_cm3"] / vol["v0_target_cm3"] - 1.0
    e3 = vol["capped_air_built_cm3"] / vol["v0_target_cm3"] - 1.0
    C.append(_check("volume_capped_air", abs(e2) <= TOL_VOLUME and abs(e3) <= TOL_VOLUME, 100 * e2, 100 * TOL_VOLUME,
                    f"capped air measured on the final mesh {vol['capped_air_measured_cm3']:.4f} cm³ ({100 * e2:+.4f} %), "
                    f"air mesh {vol['capped_air_built_cm3']:.4f} cm³ ({100 * e3:+.4f} %), against "
                    + (f"V0 {vol['v0_target_cm3']:.4f} cm³" if abs(vol["v0_target_cm3"] - vol["v0_kernel_cm3"]) < 1e-6 else
                       f"the model target {vol['v0_target_cm3']:.4f} cm³ (V0 {vol['v0_kernel_cm3']:.4f} cm³ in the print, volume factor "
                       f"{vol['volume_factor']:.4f}, holes drawn with the hole offset)") + " (limit 0.5 %)"))
    if body.kind == "stub":
        C.append(_check("stub_volume", abs(e2) <= TOL_VOLUME, vol["capped_air_measured_cm3"], vol["v0_target_cm3"],
                        f"voicing stub: capped air measured on the final mesh {vol['capped_air_measured_cm3']:.4f} cm³ against the stub volume "
                        f"{vol['v0_target_cm3']:.4f} cm³ ({100 * e2:+.4f} %, limit 0.5 %). The window is capped at its inner plane, as on a body"))
        pitch = getattr(sz, "predicted_pitch_hz", None)
        if pitch:
            C.append(_check("stub_pitch_predicted", None, pitch, 0.0,
                            f"predicted pitch of the stub, not measured: {pitch:.1f} Hz with the prior eta_w {sz.eta_w:.2f} at "
                            f"{sz.internal_temp_c:.0f} °C internal air. The measured pitch gives eta_w · G_w for this voicing", status="info"))
    bad = [s["name"] for s in body.booleans if not (s["ok"] and s["manifold"])]
    worst = max((abs(s["delta_mm3"] - s["expected_mm3"]) / max(abs(s["expected_mm3"]), 1.0)
                 for s in body.booleans if s.get("expected_mm3") is not None), default=0.0)
    C.append(_check("booleans", not bad, len(body.booleans), 0,
                    f"{len(body.booleans)} Booleans, all manifold, each volume change as expected "
                    f"(largest deviation {100 * worst:.2f} % of the expected change)" if not bad else "failed: " + ", ".join(bad)))

    # ---- topology
    t = m["topology"]
    n_open = len(body.layout.holes) + 2                       # holes, window, windway mouth
    ok = (t["manifold"] and t["shells"] == 1 and t["zero_length_edges"] == 0 and t["degenerate_faces"] == 0
          and t["self_intersections"] == 0 and t["genus"] == n_open - 1)
    C.append(_check("topology", ok, t["genus"], n_open - 1,
                    f"manifold {t['manifold']}, shells {t['shells']}, boundary edges {t['boundary_edges']}, non-manifold edges "
                    f"{t['nonmanifold_edges']}, zero-length edges {t['zero_length_edges']}, degenerate triangles {t['degenerate_faces']}, "
                    f"self-intersections {t['self_intersections']}, genus {t['genus']} (expected {n_open - 1}: {len(body.layout.holes)} holes, "
                    f"the window and the windway)"))

    # ---- voicing hash and voicing numbers
    again = k.voicing.voicing_hash_of(v)
    stored = body.voicing_hash
    C.append(_check("voicing_hash", again == v.version_hash == stored, 0, 0,
                    f"hash {stored}; recomputed from the record: {again}"))
    g = m["voicing"]
    rows = [("window length", g["window_length_mm"], v.window_length_mm, TOL_MM),
            ("window width", g["window_width_mm"], v.window_width_mm, TOL_MM),
            ("windway exit height", g["windway_exit_height_mm"], v.windway_exit_height_mm, TOL_MM),
            ("windway exit width", g["windway_exit_width_mm"], v.windway_width_mm, TOL_MM),
            ("windway inlet height", g["windway_inlet_height_mm"], v.windway_inlet_height_mm, TOL_MM),
            ("windway inlet width", g["windway_inlet_width_mm"], v.windway_width_mm, TOL_MM),
            ("labium edge thickness", g["labium_edge_thickness_mm"], v.labium_edge_thickness_mm, TOL_MM),
            ("labium offset", g["labium_offset_mm"], v.labium_offset_mm, TOL_MM)]
    bad = [f"{n} {a:.3f} against {b:.3f} mm" for n, a, b, tol in rows if abs(a - b) > tol]
    a_err = g["window_area_mm2"] / v.window_area_mm2 - 1.0
    if abs(a_err) > TOL_AREA_REL:
        bad.append(f"window area {g['window_area_mm2']:.2f} against {v.window_area_mm2:.2f} mm²")
    if abs(g["labium_angle_deg"] - v.labium_ramp_angle_deg) > TOL_ANGLE_DEG:
        bad.append(f"labium angle {g['labium_angle_deg']:.2f} against {v.labium_ramp_angle_deg:.2f}°")
    C.append(_check("voicing_dimensions", not bad, max(abs(a - b) for _, a, b, _ in rows), TOL_MM,
                    ("measured on the mesh: window " f"{g['window_length_mm']:.3f} × {g['window_width_mm']:.3f} mm, {g['window_area_mm2']:.2f} mm² "
                     f"(record {v.window_length_mm:.3f} × {v.window_width_mm:.3f}, {v.window_area_mm2:.2f}); windway exit "
                     f"{g['windway_exit_height_mm']:.3f} × {g['windway_exit_width_mm']:.3f} mm, inlet {g['windway_inlet_height_mm']:.3f} × "
                     f"{g['windway_inlet_width_mm']:.3f} mm; labium {g['labium_angle_deg']:.2f}°, edge {g['labium_edge_thickness_mm']:.3f} mm, "
                     f"offset {g['labium_offset_mm']:+.3f} mm") if not bad else "; ".join(bad)))
    # A teardrop has its broad end at the windway. A rounded rectangle (forced shape, stub V-b only) has the same
    # width from end to end, so that part of the check does not apply to it.
    teardrop = v.shape == "teardrop"
    ok = g["windway_exit_faces_labium"] and (g["broad_end_at_windway"] or not teardrop) and g["window_opens_outward"]
    C.append(_check("voicing_orientation", ok, 0, 0,
                    f"windway exit faces the labium: {g['windway_exit_faces_labium']}; "
                    + (f"broad end at the windway: {g['broad_end_at_windway']} (widest point {g['widest_point_xw_mm']:.2f} mm from the exit, "
                       f"window {g['window_length_mm']:.2f} mm long); " if teardrop else
                       f"broad end: not applicable to a {v.shape.replace('_', ' ')}, which has one width (full width from "
                       f"{v.corner_radius_mm:.1f} mm to {g['widest_point_xw_mm']:.2f} mm of the {g['window_length_mm']:.2f} mm length); ")
                    + f"window opens outward: {g['window_opens_outward']}"))
    kin = m["keepout_inside"]
    tubes_near = [r for r in m["holes"] if r.get("tube_to_labium_mm", 1e9) < v.keepout_inside_mm]
    ok = (kin["points_in_plastic"] == 0 and g["depth_below_window_mm"] >= v.keepout_inside_mm and not tubes_near
          and g["flare_violations"] == 0)
    C.append(_check("voicing_keepouts", ok, g["depth_below_window_mm"], v.keepout_inside_mm,
                    f"inside: {kin['points_in_plastic']} of {kin['points_tested']} sample points within {v.keepout_inside_mm:.0f} mm of the labium "
                    f"are plastic; free depth below the window {g['depth_below_window_mm']:.1f} mm; "
                    + ("tubes inside the keep-out: " + ", ".join(r["name"] for r in tubes_near) + "; " if tubes_near else "no tube inside the keep-out; ")
                    + f"outside: {g['flare_violations']} vertices above the {v.keepout_outside_flare_deg:.0f}° flare"))
    C.append(_check("windway_floor_lip", g["windway_floor_lip_mm"] >= MIN_FLOOR_LIP_MM, g["windway_floor_lip_mm"], MIN_FLOOR_LIP_MM,
                    f"plastic under the windway floor at the exit: {g['windway_floor_lip_mm']:.2f} mm (at least {MIN_FLOOR_LIP_MM} mm); "
                    f"windway roof {g['windway_roof_thickness_mm']:.2f} mm"))

    # ---- holes: the Phase 4 gate
    H = m["holes"]
    if H:
        C.extend(_hole_checks(body, m, params, H, v))

    # ---- wall
    w = m["wall"]
    wall = body.params["wall_mm"]
    C.append(_check("wall_thickness", w["shell_min_mm"] >= wall - WALL_TOL_MM, w["shell_min_mm"], wall,
                    f"plain wall, cavity to outside along the normal: minimum {w['shell_min_mm']:.3f} mm, median {w['shell_median_mm']:.3f} mm "
                    f"(target {wall:.1f} mm, {w['shell_samples']} rays). Thinnest plastic of the finished body away from the voicing and the "
                    f"tubes: {w['final_min_thickness_mm']:.2f} mm"))

    # ---- hand layout: soft checks, "pass" or "warn"
    e = m.get("ergonomics") or {}
    if e:
        for c in ergonomics.evaluate(e["inner"], params.get("ergonomics"), rest=e["rest"], taped=e["taped"], outer=e["outer"]):
            C.append(dict(c, expected=False))

    for c in C:
        c["expected"] = bool(c["status"] in ("fail", "needs_fem") and expected_failure(body.preset_id, body.v0_cm3, c["name"], c["status"]))
    return C


def _cavity_mode_check(cm, params) -> dict:
    """The cavity-mode verdict from the computed first mode (doc 02 Q9 / A12 as revised in docs/06 section 3.10)."""
    margin = float(params["constraints"].get("cavity_mode_margin", 1.0))
    fem = float(params["constraints"].get("cavity_mode_fem_margin", 1.3))
    rule = (f"Rule: pass at {fem:g} × F6 or more, needs_fem from {margin:g} to {fem:g}, fail below {margin:g}. This is a desk check "
            f"with closed holes: the {fem:g} margin is a guess, and the Stage 2 spectra remain the real test")
    if not cm or not cm.get("computed"):
        why = (cm or {}).get("reason", "the cavity-mode step did not run")
        return _check("cavity_mode_computed", False, float("nan"), fem,
                      f"NOT COMPUTED: {why}. The check does not pass by default. To run it by hand: "
                      f"python ocarina_addon/cavity_mode_solver.py <body>_air_capped.stl. {rule}")
    ratio = float(cm["ratio"])
    other = "; ".join(f"{g['grid_mm']:g} mm grid: {g['f1_hz']:.0f} Hz" for g in cm.get("grids", [])[1:])
    return _check("cavity_mode_computed", None, ratio, fem,
                  f"first cavity mode of the capped air mesh ({cm.get('source', 'air mesh')}; holes and window closed): "
                  f"{cm['f1_hz']:.0f} Hz = {ratio:.2f} × F6 on a {cm['grid_mm']:g} mm grid of {cm['cells']} cells"
                  + (f" ({other})" if other else "") + f". {rule}", status=cavity_mode.verdict(ratio, margin, fem))


def _hole_checks(body, m, params, H, v) -> list:
    C = []
    worst_d = max(H, key=lambda r: abs(r["d_error_mm"]))
    worst_c = max(H, key=lambda r: abs(r["chimney_error_mm"]))
    ok = abs(worst_d["d_error_mm"]) <= TOL_MM and abs(worst_c["chimney_error_mm"]) <= TOL_MM
    C.append(_check("hole_sizes_phase4_gate", ok, max(abs(worst_d["d_error_mm"]), abs(worst_c["chimney_error_mm"])), TOL_MM,
                    f"12 holes measured on the mesh against the kernel: largest diameter error {worst_d['d_error_mm']:+.4f} mm ({worst_d['name']}), "
                    f"largest chimney error {worst_c['chimney_error_mm']:+.4f} mm ({worst_c['name']}); limit {TOL_MM} mm"))
    tubed = [r for r in H if r["tube_kernel_mm"] > 0]
    if tubed:
        bad = []
        for r in tubed:
            if abs(r.get("tube_length_measured_mm", float("nan")) - r["tube_kernel_mm"]) > TOL_MM:
                bad.append(f"{r['name']} tube length {r.get('tube_length_measured_mm')}")
            if abs(r.get("tube_wall_measured_mm", float("nan")) - body.params["tube_wall_mm"]) > TOL_MM:
                bad.append(f"{r['name']} tube wall {r.get('tube_wall_measured_mm')}")
            if r["tube_to_opposite_wall_mm"] < TUBE_CLEAR_WALL_MM:
                bad.append(f"{r['name']} ends {r['tube_to_opposite_wall_mm']:.1f} mm from the opposite wall")
            if r.get("tube_to_tube_mm", float("inf")) < TUBE_CLEAR_TUBE_MM:
                bad.append(f"{r['name']} is {r['tube_to_tube_mm']:.1f} mm from another tube")
            if r["tube_to_labium_mm"] < v.keepout_inside_mm:
                bad.append(f"{r['name']} is {r['tube_to_labium_mm']:.1f} mm from the labium")
        C.append(_check("inward_tubes", not bad, len(tubed), 0,
                        "; ".join(f"{r['name']}: length {r.get('tube_length_measured_mm', float('nan')):.3f} mm (kernel {r['tube_kernel_mm']:.1f}), wall "
                                  f"{r.get('tube_wall_measured_mm', float('nan')):.3f} mm, {r['tube_to_opposite_wall_mm']:.1f} mm to the opposite wall, "
                                  f"{r['tube_to_labium_mm']:.1f} mm to the labium"
                                  + (f", {r['tube_to_tube_mm']:.1f} mm to the nearest other tube" if r.get("tube_to_tube_mm", float("inf")) < 1e9 else "")
                                  for r in tubed) if not bad else "; ".join(bad)))
    worst_a = max(H, key=lambda r: r["axis_vs_cavity_normal_deg"] if r["axis_vs_cavity_normal_deg"] == r["axis_vs_cavity_normal_deg"] else 999)
    C.append(_check("hole_axes", worst_a["axis_vs_cavity_normal_deg"] <= TOL_AXIS_DEG, worst_a["axis_vs_cavity_normal_deg"], TOL_AXIS_DEG,
                    f"largest angle between a hole axis and the cavity mesh normal: {worst_a['axis_vs_cavity_normal_deg']:.2f}° ({worst_a['name']}); "
                    f"limit {TOL_AXIS_DEG}°"))
    gmin = min(H, key=lambda r: r["nearest_gap_mm"])
    C.append(_check("hole_spacing", gmin["nearest_gap_mm"] >= MIN_GAP_MM - 1e-6, gmin["nearest_gap_mm"], MIN_GAP_MM,
                    f"smallest edge gap {gmin['nearest_gap_mm']:.2f} mm ({gmin['name']} to {gmin['nearest_hole']}); at least {MIN_GAP_MM} mm"))
    moved = max(H, key=lambda r: r["moved_mm"])
    lay = body.layout
    C.append(_check("hole_layout", moved["moved_mm"] <= 2.0 + 1e-6, moved["moved_mm"], 2.0,
                    f"record of moves: largest move from the layout position {moved['moved_mm']:.2f} mm ({moved['name']}; up to 2 mm "
                    f"allowed); layout '{lay.kind}'"
                    + ("".join(f"; {s} slides {r['slide_mm']:.2f} mm from {r['parent']}" for s, r in lay.subholes.items()))
                    + ("; " + "; ".join(lay.messages) if lay.messages else "")
                    + ("; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks"
                       if lay.kind == "template" else f"; {ergonomics.TAPED_MESSAGE}")))
    hv = m["hole_to_voicing"]
    lim = float(params["constraints"]["hole_to_window_min_mm"])
    nearest = min(hv.items(), key=lambda kv: kv[1]["to_window_mm"])
    cut = [n for n, d in hv.items() if d["to_block_mm"] < 0.5 or d["to_ramp_mm"] < 0.5]
    C.append(_check("hole_to_voicing", nearest[1]["to_window_mm"] >= lim and not cut, nearest[1]["to_window_mm"], lim,
                    f"nearest hole edge to the window: {nearest[0]}, {nearest[1]['to_window_mm']:.1f} mm (at least {lim:.0f} mm)"
                    + ("; holes that touch the voicing block or the labium ramp: " + ", ".join(cut) if cut else
                       "; no hole touches the voicing block or the labium ramp")))
    return C


def run_all(body, params=None, V=None, F=None, cavity_mode_step: bool = True) -> None:
    """Measure the mesh (default: the body's final mesh) and evaluate every check. The cavity-mode step runs a
    second Python process on the exported air mesh; with cavity_mode_step=False the check reports that it
    was not computed (a failure, never a pass)."""
    params = params if params is not None else kernel_bridge.load_params()
    body.measurements = measure(body, V, F)
    body.measurements["cavity_mode"] = (measure_cavity_mode(body) if cavity_mode_step else
                                        dict(computed=False, reason="the cavity-mode step was switched off for this run"))
    body.checks = evaluate(body, body.measurements, params)


def unexpected_failures(body) -> list:
    """Failed checks that the notes do not list as expected. Warnings (status "warn") are never failures."""
    return [c for c in body.checks if c["status"] == "fail" and not c["expected"]]


def expected_failures(body) -> list:
    return [c for c in body.checks if c["status"] in ("fail", "needs_fem") and c["expected"]]


def warnings(body) -> list:
    return [c for c in body.checks if c["status"] == "warn"]
