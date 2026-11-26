"""The thinnest plastic between the window cut and the windway's roof over the windway's exit corners (plain Python).

    python tools/exit_corner_plastic.py addon_out/stage2/P4-80/P4-80.stl [more STL files] [--preset P4]

Where the windway's rectangle runs on past the round broad end of the window (xw 0 to about 3.2 mm), the window's
cut stands on the windway's roof. The wall check measures "away from the voicing" and does not see the plastic there.
This script measures it on the STL read back from disk (trimesh reads the file; the rest is numpy):

1. Lines along the window's normal (z of the voicing frame) on a 0.02 mm grid over xw 0 to 3.5 mm and across the
   windway's width. Along a line the mesh is crossed an even number of times; plastic lies between the 1st and 2nd
   crossing from the top, the 3rd and 4th, and so on. The windway is the gap between two such stretches whose height
   is the windway's exit height (within 0.3 mm, from the record); the stretch above it ends on the windway's roof,
   the stretch below it on the windway's floor.
2. "Along z" is the shortest stretch above the roof on those lines (the measure of the H7 run). Next to a wall that
   stands on the roof it shrinks with the grid, so it is not a thickness.
3. "Thinnest" is the add-on's own measure of thin plastic (checks_geo.measure_wall): from each point of the roof a ray
   along the inward normal of its triangle, through the plastic; it counts only when it leaves through a face that
   looks away from the roof (normals at more than 120 deg). Next to an edge a ray leaves through the neighbouring face
   after a very short way; that is not a thin wall, so it is left out. The same is done from the floor, downward.

The voicing frame comes from the preset's cavity maths (cavity_math; the port is the body's origin); the window's
length and the windway's exit width and height come from the check record beside the STL (<id>_checks.json). The
preset is the body id up to its volume (P4-80 -> P4, P4-bowl-80-zb4 -> P4-bowl) unless --preset is given.
It changes nothing and adds no check.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP_MM = 0.02           # the grid of the lines
XW_RANGE_MM = (0.0, 3.5)
GAP_TOL_MM = 0.3         # the windway: a gap of the exit height within this
OPPOSITE = -0.5          # a ray counts when the face it leaves by has n . n_start below this (checks_geo.measure_wall)
START_MM = 0.02          # rays start this far inside the plastic (checks_geo.measure_wall)
RES_U, RES_V = 129, 128  # cavity.RES_U, cavity.RES_V: the port is snapped to this grid (cavity.py needs bpy)
CLEARANCE_MM = 0.05      # voicing_geo.POCKET_CLEARANCE_MM: the frame's origin sits this far out along z


def frame_of(preset: dict):
    """(origin, x, y, z) of the voicing frame in body coordinates, as voicing_geo.voicing_frame makes it."""
    from ocarina_addon import cavity_math
    cav = cavity_math.Cavity.from_preset(preset)
    cav.snap_port_to_grid(RES_U, RES_V)
    x, y, z = (np.asarray(v, float) for v in cav.port_frame())
    return CLEARANCE_MM * z, x, y, z


def crossings(Q, F, xs, ys) -> dict:
    """Where the lines (xs[i], ys[j]) along z cross the triangles F of the points Q (xw, y, z):
    {(i, j): [(z, triangle), ...] highest first}."""
    T = Q[F]
    lo, hi = T[:, :, :2].min(1), T[:, :, :2].max(1)
    out: dict = {}
    for f, (t, a, b) in enumerate(zip(T, lo, hi)):
        i0, i1 = max(math.ceil((a[0] - xs[0]) / STEP_MM), 0), min(math.floor((b[0] - xs[0]) / STEP_MM), len(xs) - 1)
        j0, j1 = max(math.ceil((a[1] - ys[0]) / STEP_MM), 0), min(math.floor((b[1] - ys[0]) / STEP_MM), len(ys) - 1)
        if i1 < i0 or j1 < j0:
            continue
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
        det = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(det) < 1e-14:                                # seen edge-on along z
            continue
        X, Y = np.meshgrid(xs[i0:i1 + 1], ys[j0:j1 + 1], indexing="ij")
        u = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / det
        v = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / det
        w = 1.0 - u - v
        for ii, jj in zip(*np.nonzero((u >= 0) & (v >= 0) & (w >= 0))):
            out.setdefault((i0 + ii, j0 + jj), []).append((u[ii, jj] * az + v[ii, jj] * bz + w[ii, jj] * cz, f))
    return {k: sorted(v, reverse=True) for k, v in out.items()}


def first_hit(p, d, T, N):
    """Distance along the unit direction d from p to the nearest triangle of T (Moller-Trumbore), and its normal."""
    e1, e2 = T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
    h = np.cross(d, e2)
    a = (e1 * h).sum(1)
    ok = np.abs(a) > 1e-12
    with np.errstate(divide="ignore", invalid="ignore"):
        f = 1.0 / a
        s = p - T[:, 0]
        u = f * (s * h).sum(1)
        q = np.cross(s, e1)
        v = f * (q @ d)
        t = f * (e2 * q).sum(1)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-9)
    if not hit.any():
        return math.inf, None
    k = np.nonzero(hit)[0][np.argmin(t[hit])]
    return float(t[k]), N[k]


def measure(V, F, frame, L: float, half_width: float, gap_mm: float) -> dict:
    """The plastic over (and under) the windway's exit corners, xw 0 to 3.5 mm; V, F in body coordinates."""
    o, fx, fy, fz = (np.asarray(a, float) for a in frame)
    D = np.asarray(V, float) - o
    Q = np.column_stack([D @ fx + L, D @ fy, D @ fz])                         # xw, y, z
    F = np.asarray(F)
    T = Q[F]
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-300)
    xs = np.arange(XW_RANGE_MM[0], XW_RANGE_MM[1] + 1e-9, STEP_MM) + 1.3e-5    # off the mesh's own round numbers
    ys = np.arange(-half_width, half_width + 1e-9, STEP_MM) + 0.7e-5
    lo, hi = T[:, :, :2].min(1), T[:, :, :2].max(1)
    near = np.nonzero((hi[:, 0] >= xs[0]) & (lo[:, 0] <= xs[-1]) & (hi[:, 1] >= ys[0]) & (lo[:, 1] <= ys[-1]))[0]
    lines = crossings(Q, F[near], xs, ys)
    odd, sides = 0, {"roof": [], "floor": []}
    for (i, j), zs in lines.items():
        if len(zs) % 2:                                     # a line through an edge or along a face: left out
            odd += 1
            continue
        if abs(ys[j]) >= half_width:
            continue
        st = list(zip(zs[0::2], zs[1::2]))                  # stretches of plastic, (top, bottom), from the top down
        for (top, bottom), (top2, _) in zip(st, st[1:]):
            if abs((bottom[0] - top2[0]) - gap_mm) <= GAP_TOL_MM and bottom[0] > 0.5:
                sides["roof"].append((xs[i], ys[j], bottom[0], near[bottom[1]], top[0] - bottom[0]))
                sides["floor"].append((xs[i], ys[j], top2[0], near[top2[1]], math.nan))
                break
    out = dict(lines=len(lines), odd_lines=odd)
    reach = 3.0
    zone = np.nonzero((T[:, :, 0].max(1) > xs[0] - reach) & (T[:, :, 0].min(1) < xs[-1] + reach) &
                      (T[:, :, 1].max(1) > ys[0] - reach) & (T[:, :, 1].min(1) < ys[-1] + reach))[0]
    Tz, Nz = T[zone], N[zone]
    for side, pts in sides.items():
        if not pts:
            out[side] = None
            continue
        best, edge_exits = (math.inf, None), 0
        for x, y, z, f, _ in pts:
            p, n = np.array([x, y, z]), N[f]
            d, nh = first_hit(p - START_MM * n, -n, Tz, Nz)
            if nh is None:
                continue
            if float(n @ nh) >= OPPOSITE:
                edge_exits += 1
                continue
            if d + START_MM < best[0]:
                best = (d + START_MM, (x, y, z))
        r = dict(points=len(pts), edge_exits=edge_exits, thinnest_mm=best[0], at=best[1])
        if side == "roof":
            a = np.array([q[4] for q in pts])
            k = int(np.argmin(a))
            r.update(along_z_least_mm=float(a[k]), along_z_at=pts[k][:3])
        out[side] = r
    return out


def preset_of(body_id: str) -> str:
    m = re.match(r"^(.*?)-\d+(?:\.\d+)?(?:-|$)", body_id)
    if not m:
        raise ValueError(f"cannot tell the preset of {body_id!r}; give --preset")
    return m.group(1)


def measure_file(stl, preset_id: str | None = None) -> dict:
    import trimesh
    from ocarina_addon import presets
    path = pathlib.Path(stl)
    g = json.loads(path.with_name(path.stem + "_checks.json").read_text(encoding="utf-8"))["measurements"]["voicing"]
    mesh = trimesh.load(str(path), force="mesh", process=False)
    pid = preset_id or preset_of(path.stem)
    r = measure(mesh.vertices, mesh.faces, frame_of(presets.get_preset(pid)), g["window_length_mm"],
                0.5 * g["windway_exit_width_mm"], g["windway_exit_height_mm"])
    return dict(r, body=path.stem, preset=pid)


def main(argv) -> int:
    pid = None
    if "--preset" in argv:
        i = argv.index("--preset")
        pid, argv = argv[i + 1], argv[:i] + argv[i + 2:]
    xy = lambda c: f"xw {c[0]:.2f}, y {c[1]:+.2f}, z {c[2]:.2f}"  # noqa: E731
    print("| Body | Over the roof: thinnest | where (on the roof) | along z, least (the H7 measure) | where | "
          "Under the floor: thinnest | where (on the floor) | rays left out at an edge | lines left out |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for stl in argv:
        r = measure_file(stl, pid)
        ro, fl = r["roof"], r["floor"]
        if ro is None:
            print(f"| {r['body']} | no windway found under plastic | | | | | | | {r['odd_lines']} of {r['lines']} |")
            continue
        print(f"| {r['body']} | {ro['thinnest_mm']:.2f} mm | {xy(ro['at'])} | {ro['along_z_least_mm']:.2f} mm | {xy(ro['along_z_at'])} | "
              f"{fl['thinnest_mm']:.2f} mm | {xy(fl['at'])} | {ro['edge_exits']} of {ro['points']}, {fl['edge_exits']} of {fl['points']} | "
              f"{r['odd_lines']} of {r['lines']} |", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
