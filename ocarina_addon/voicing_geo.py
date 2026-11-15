"""Voicing geometry, built only from the kernel's Voicing record. Nothing here is free-form.

The voicing is rigid: the same record gives the same solids on every body. It is built in its own
frame and then placed at the voicing port.

Voicing frame (millimetres)
    origin   the labium point: the far end of the window on the centre line, in the INNER PLANE
    x        along the jet, from the windway toward the labium. The window runs from x = -L (windway
             exit) to x = 0 (labium), L = window length. "xw" below is x + L (0 at the exit).
    y        across the jet (the window width and the windway width are along y)
    z        outward. z = 0 is the inner plane: the flat cavity-side face around the window.
             z = wall is the outer face of the voicing block.
The frame sits on the cavity at the voicing port: z is the cavity normal there, and the origin is
POCKET_CLEARANCE_MM outside the cavity surface, so the inner plane never touches the curved cavity.

Solids (all closed meshes)
    block      the voicing block and mouthpiece stub: a box that holds the windway and gives the window a
               flat outer face at z = wall. It is joined to the skin.
    pocket     air: a flat-topped prism from below the cavity surface up to the inner plane, under the
               window and a margin around it. It is joined to the cavity, so the window opens from a flat
               ceiling and its throat is exactly `wall` deep. Its windway side ends at the exit plane
               xw = 0, where the windway floor ends.
    window     air cutter: the window outline through the wall (the throat), with the labium ramp:
               on the labium side the outline is flared outward above the edge at the ramp angle. The
               flare fades to zero toward the widest points of the outline.
    windway    air cutter: the tapered windway, from the mouth end to the exit, and on into the broad
               end of the window so that the full width opens.

Conventions that the record does not fix (recorded in the notes; change them here if the owner decides)
    labium offset  the mid-height of the labium edge is `labium_offset_mm` above the windway centre line
    windway taper  symmetric about the centre line (floor and roof both move)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from . import meshutil

POCKET_CLEARANCE_MM = 0.05     # the inner plane sits this far outside the cavity surface at the port
POCKET_MARGIN_MM = 3.0         # flat ceiling around the labium half of the window
POCKET_BACK_OVERLAP_MM = 0.05  # the pocket starts this far before the exit plane, so that the window cutter
                               # crosses the pocket ceiling cleanly and does not touch the pocket's back wall
POCKET_DEPTH_MM = 7.0          # the pocket prism reaches this far below the inner plane (into the cavity air)
STUB_SIDE_WALL_MM = 4.0        # plastic beside the windway
STUB_FLOOR_MM = 2.4            # plastic under the windway floor at the mouth end
BLOCK_FRONT_MM = 4.0           # the block reaches this far beyond the labium point
RAMP_FULL_DEG = 60.0           # the ramp has its full angle for outline normals within this angle of the jet
CUT_ABOVE_MM = 1.0             # cutters reach this far above the outer face
CUT_BELOW_MM = 0.5             # the window cutter reaches this far below the inner plane (into the pocket air)
WINDWAY_OVERSHOOT_MM = 1.0     # the windway cutter starts this far outside the mouth end of the stub
OUTLINE_STEP_DEG = 1.5


@dataclass
class VoicingSolids:
    frame: tuple                   # (origin, x, y, z) in body coordinates
    block: tuple                   # (V, F) each, body coordinates
    pocket: tuple
    window: tuple
    windway: tuple
    outline: np.ndarray            # window outline polygon in the voicing frame: (n, 3) = xw, y, normal angle
    footprint: np.ndarray          # pocket footprint polygon (n, 2) in xw, y
    info: dict                     # numbers used to build the solids (for the checks)


def _to_frame(pts_xw_y_z, L, frame):
    origin, x, y, z = frame
    P = np.asarray(pts_xw_y_z, dtype=np.float64).copy()
    P[:, 0] -= L                                  # xw -> x
    return meshutil.frame_points(P, origin, x, y, z)


def ramp_reach_factor(theta_abs: float) -> float:
    """1 where the ramp has its full angle; falls smoothly to 0 at the widest points of the outline."""
    full = math.radians(RAMP_FULL_DEG)
    if theta_abs <= full:
        return 1.0
    if theta_abs >= 0.5 * math.pi:
        return 0.0
    return math.cos(0.5 * math.pi * (theta_abs - full) / (0.5 * math.pi - full)) ** 2


def voicing_frame(port_frame):
    """Voicing frame from the cavity's port frame (x jet, y, z normal; the port is the body origin)."""
    x, y, z = (np.asarray(v, dtype=np.float64) for v in port_frame)
    origin = POCKET_CLEARANCE_MM * z
    return origin, x, y, z


def windway_centre_z(v) -> float:
    return 0.5 * v.labium_edge_thickness_mm - v.labium_offset_mm


def windway_half_height(v, xw: float) -> float:
    """Half of the windway height at xw (xw <= 0 inside the windway; constant beyond the exit)."""
    he, hi, Lw = v.windway_exit_height_mm, v.windway_inlet_height_mm, v.windway_length_mm
    if xw >= 0.0:
        return 0.5 * he
    return 0.5 * (he + (hi - he) * (-xw / Lw))


def build(v, port_frame) -> VoicingSolids:
    """All voicing solids for the Voicing record `v`, placed at the port frame."""
    frame = voicing_frame(port_frame)
    L, W, wall = v.window_length_mm, v.window_width_mm, v.wall_at_window_mm
    e = v.labium_edge_thickness_mm
    Lw = v.windway_length_mm
    a = 0.5 * W
    out = np.array(v.outline_mm(OUTLINE_STEP_DEG), dtype=np.float64)        # (n, 3): xw, y, normal angle
    n = len(out)
    nx, ny = np.cos(out[:, 2]), np.sin(out[:, 2])
    xb = float(out[np.argmax(out[:, 1]), 0])                                # xw of the widest point

    # ---------------- window cutter: throat + labium ramp, one closed mesh
    z_top = wall + CUT_ABOVE_MM
    reach = (z_top - e) / math.tan(math.radians(v.labium_ramp_angle_deg))
    if v.shape == "teardrop":
        f = np.array([ramp_reach_factor(abs(t)) for t in out[:, 2]])
    else:
        # forced rounded rectangle: the labium is the straight far edge; ramp on normals within 45 deg of the jet
        f = np.array([1.0 if abs(t) < math.radians(45.0) else 0.0 for t in out[:, 2]])
    ring_lo = np.column_stack([out[:, 0], out[:, 1], np.full(n, -CUT_BELOW_MM)])
    ring_edge = np.column_stack([out[:, 0], out[:, 1], np.full(n, e)])
    ring_top = np.column_stack([out[:, 0] + f * reach * nx, out[:, 1] + f * reach * ny, np.full(n, z_top)])
    wV, wF = meshutil.prism_from_rings([ring_lo, ring_edge, ring_top])
    window = (_to_frame(wV, L, frame), wF)

    # ---------------- pocket footprint: straight back edge at the exit plane, margin around the labium half
    m = POCKET_MARGIN_MM
    front = [(x + m * cx, y + m * sy) for (x, y, t), cx, sy in zip(out, nx, ny) if abs(t) <= 0.5 * math.pi + 1e-9]
    front.sort(key=lambda p: math.atan2(p[1], p[0] - xb))                    # from -90 deg round to +90 deg
    xk = -POCKET_BACK_OVERLAP_MM
    foot = [(xk, -(a + m))] + [p for p in front] + [(xk, a + m)]
    foot = _dedupe(foot)
    foot = np.array(foot, dtype=np.float64)
    r0 = np.column_stack([foot, np.full(len(foot), -POCKET_DEPTH_MM)])
    r1 = np.column_stack([foot, np.zeros(len(foot))])
    pV, pF = meshutil.prism_from_rings([r0, r1])
    pocket = (_to_frame(pV, L, frame), pF)

    # ---------------- windway cutter: tapered duct, then on into the broad end of the window
    zc = windway_centre_z(v)
    x0 = -Lw - WINDWAY_OVERSHOOT_MM
    c = min(0.5, 0.3 * xb)                                                   # the nose starts this far before the widest point
    x_nose = xb + 1.0
    y_nose = 0.6 * _half_width_at(out, x_nose)
    stations = [(x0, a), (0.0, a), (xb - c, a), (x_nose, y_nose)]
    rings = []
    for xs, hw in stations:
        hh = windway_half_height(v, xs)
        rings.append(np.array([[xs, -hw, zc - hh], [xs, hw, zc - hh], [xs, hw, zc + hh], [xs, -hw, zc + hh]]))
    dV, dF = meshutil.prism_from_rings(rings)
    if meshutil.volume(dV, dF) < 0:
        dF = dF[:, ::-1]
    windway = (_to_frame(dV, L, frame), dF)

    # ---------------- block: voicing block and mouthpiece stub
    z_bot = zc - 0.5 * v.windway_inlet_height_mm - STUB_FLOOR_MM
    half_w = a + STUB_SIDE_WALL_MM
    bV, bF = meshutil.box_local(-Lw, L + BLOCK_FRONT_MM, -half_w, half_w, z_bot, wall)
    block = (_to_frame(bV, L, frame), bF)

    outline_area = float(abs(_poly_area(out[:, :2])))
    corner_area = W * (xb - c) - _area_left_of(out, xb - c)       # windway footprint outside the outline, xw in [0, xb - c]
    info = dict(
        window_length_mm=L, window_width_mm=W, wall_mm=wall, edge_mm=e, ramp_deg=v.labium_ramp_angle_deg,
        ramp_reach_mm=reach, widest_xw_mm=xb, windway_centre_z_mm=zc, windway_floor_exit_z_mm=zc - 0.5 * v.windway_exit_height_mm,
        windway_roof_exit_z_mm=zc + 0.5 * v.windway_exit_height_mm, block_z_bottom_mm=z_bot, block_half_width_mm=half_w,
        outline_polygon_area_mm2=outline_area, outline_points=n, pocket_margin_mm=m, pocket_clearance_mm=POCKET_CLEARANCE_MM,
        throat_volume_mm3=outline_area * wall,
        windway_volume_mm3=W * Lw * 0.5 * (v.windway_exit_height_mm + v.windway_inlet_height_mm),
        windway_corner_area_mm2=corner_area, windway_nose=(xb - c, x_nose, y_nose),
        z_top_mm=z_top)
    return VoicingSolids(frame=frame, block=block, pocket=pocket, window=window, windway=windway, outline=out,
                         footprint=foot, info=info)


# ------------------------------------------------------------------ small 2-D helpers

def _dedupe(pts, tol=1e-9):
    out = []
    for p in pts:
        if not out or abs(p[0] - out[-1][0]) > tol or abs(p[1] - out[-1][1]) > tol:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < tol and abs(out[0][1] - out[-1][1]) < tol:
        out.pop()
    return out


def _poly_area(xy):
    x, y = xy[:, 0], xy[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def _half_width_at(out, xw: float) -> float:
    """Half-width of the (convex, symmetric) outline at xw: the largest y of the polygon on the line x = xw."""
    best = 0.0
    n = len(out)
    for i in range(n):
        x0, y0 = out[i, 0], out[i, 1]
        x1, y1 = out[(i + 1) % n, 0], out[(i + 1) % n, 1]
        if (x0 - xw) * (x1 - xw) <= 0 and abs(x1 - x0) > 1e-12:
            best = max(best, y0 + (y1 - y0) * (xw - x0) / (x1 - x0))
    return best


def _area_left_of(out, x_cut: float, n: int = 400) -> float:
    """Area of the outline with xw <= x_cut (numerical, from the half-width)."""
    xs = np.linspace(0.0, x_cut, n + 1)
    hw = np.array([_half_width_at(out, float(x)) for x in xs])
    return float(2.0 * np.trapezoid(hw, xs))
