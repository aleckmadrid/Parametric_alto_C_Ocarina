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

Window cut styles (the record's `window_cut`; since 2026-11-18 the rule is "ellipse", and "fan" is the plain build)
    "fan"    every outline point on the labium side is pushed outward along its own normal. The ramp has its full
             angle within RAMP_FULL_DEG of the jet, so on a round window it also opens far to the sides.
    "cone"   EXPERIMENTAL (Analizes_ocarinas/Window_cutout/Window_cutout.md, owner's idea of 2026-11-17). First the
             sharp outline goes straight through the wall; then a second surface smooths the labium side. It passes
             through the outline at the top of the labium edge and runs along the jet at the ramp angle (a cone with
             its apex far upstream). So the edge keeps its thickness along the whole labium and the ramp has the
             record's angle. Sideways it opens by `cone_widen_mm` at the outer face, gently near the lip and faster
             near the surface, so the cut reads as a dish. The two halves meet in a fold at the widest points of
             the window; the owner found the sides rough in every variation (2026-11-17). Kept for comparison.
    "ellipse" EXPERIMENTAL, the owner's choice of 2026-11-17 among the prototypes (Window_cutout.md sections 11, 12).
             One surface, lofted from the window outline to an ellipse at the outer face, so there is no fold. The
             labium half starts at the top of the edge: the edge keeps its thickness, and the ramp has the record's
             angle at the tip. The windway half starts at the shelf level. The ellipse reaches from the back edge of
             the shelf to the end of the ramp, and `cone_widen_mm` beyond the window on each side. No point of the
             surface moves inward across its own normal, so nothing leans in over the window (ELLIPSE_NO_OVERHANG).
             Its window area is measured as the free opening seen straight in (checks_geo.measure_voicing).

The build settings (prototypes of 2026-11-17; since the owner's decisions of 2026-11-18 they are fields of the
kernel's voicing record, [voicing_rules] gives their values, and they are hashed: see RECORD_KEYS. No preset sets them)
    shelf_angle_deg     "cone" and "ellipse" cuts: the wall of the window above the windway exit is cut back at this angle from
                        the normal, starting shelf_land_mm above the windway roof ("the top shelf"). 0 = vertical.
    windway_pitch_deg   the windway cutter is turned about the across axis through the labium edge, so the jet still
                        aims at the edge. Positive: the mouth end is raised away from the body and the jet reaches the
                        edge heading inward. Negative: the mouth end is lowered and the jet heads outward, along the ramp.
    stub_pitch_deg      the same turn for the outer stub (the plastic around the windway). It follows the windway
                        unless it is given, so the outer shape and the pipe can be set apart.
    A turn sideways is not an option of the windway: it would be a turn of the whole voicing about its normal.
    stub_style          "box" (default): the plain box. "neck": a base neck after the owner's sample
                        (Analizes_ocarinas/Window_cutout/Window_cutout.md section 10): ellipses lofted along the
                        windway, slim at the mouth end and flaring like a bell into the body. Its roof-side line is
                        straight and level with the outer face at the window; past the widest point of the window it
                        dives under the skin. THE NECK HIDES THE TILT (owner, 2026-11-17): it does not follow a lowered
                        windway. The pipe turns inside it, and the mouth end of the neck is made just deep enough to
                        leave NECK_MIN_WALL_MM of plastic around the pipe. A raised windway cannot be hidden under a
                        level roof line, so the neck follows that one unless stub_pitch_deg says otherwise.
                        "cone": THE NECK OF THE RULES since 2026-11-19 (rule version 3, the owner's choice of trial
                        tb-d1; Analizes_ocarinas/Neck_volume/Neck_volume.md). Its outer flank lies a thin roof over the
                        pipe (CONE_COVER_MM at the mouth end, about 1.7 mm at the exit), it never stands above the
                        window's outer face at the exit, and its deck side is straight. See neck_solid and CONE_*.
    History: on 2026-11-18 the rule was the "neck" standing 15 deg off the window face with the pipe 10 deg lower inside
    it (+5 deg). That put a wedge of plastic over the pipe and over the window, and the owner rejected it. Since rule
    version 3 the pipe is at +8 deg, the flank follows it, and the voicing as a whole is turned toward the bottom of
    the body by the port angle of the cavity presets (30 deg), which is what points the neck back at the player.
    pocket_blend_radius_mm   0 = the pocket as it is: a flat ceiling with a 3 mm margin that ends in a small step
                        (0.2 to 0.3 mm behind the lip) where the curved chamber wall has dropped away. A radius (for
                        example 12) keeps the ceiling flat for POCKET_BLEND_FLAT_MM beyond the labium and then lets it
                        fall away on a circle of that radius until it meets the chamber wall, so it meets it at a few
                        degrees instead of a step. The skirt ends where it meets the wall, in every direction (see the
                        pocket code below): its reach is a few millimetres on a flat chamber and up to about 11 mm on a stub.
    cone_flare_exponent   shape of the dish: how fast the sides open toward the surface.
    cone_widen_share    the sideways opening as a share of the window width (per side), instead of cone_widen_mm, so
                        that the dish follows the window from one volume to the next. It wins over cone_widen_mm.

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
POCKET_BLEND_FLAT_MM = 1.5     # with pocket_blend_radius_mm: the ceiling stays flat this far beyond the labium
POCKET_BLEND_UNDER_MM = 0.2    # the skirt of the blend ends this far below the chamber wall
POCKET_BLEND_STEP_MM = 0.5     # the meeting point is looked for in steps of this size, then refined
POCKET_BLEND_REACH_MAX = 0.98  # the skirt reaches at most this share of its radius (at 1 it would be vertical)
POCKET_BLEND_REACH_NO_CHAMBER_MM = 11.0   # reach of the skirt in a direct call that gives no chamber
POCKET_BLEND_SIDE_INSET_MM = 0.3   # where the chamber's wall turns upright first, the skirt stops this far before it
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
    duct_frame: tuple = None       # (origin, x, y, z) of the windway: the frame turned by the windway pitch (None = frame)

    def windway_frame(self) -> tuple:
        return self.frame if self.duct_frame is None else self.duct_frame


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


def pitched_frame(frame, zc: float, pitch_deg: float) -> tuple:
    """The voicing frame turned by pitch_deg about the across axis through the labium edge (x = 0, z = zc).
    Coordinates in the turned frame are those of the voicing frame at the pivot. Positive raises the mouth end."""
    o, x, y, z = frame
    t = math.radians(pitch_deg)
    xd = math.cos(t) * x - math.sin(t) * z
    zd = math.sin(t) * x + math.cos(t) * z
    pivot = o + zc * z
    return pivot - zc * zd, xd, y, zd


def windway_centre_z(v) -> float:
    return 0.5 * v.labium_edge_thickness_mm - v.labium_offset_mm


def windway_half_height(v, xw: float) -> float:
    """Half of the windway height at xw (xw <= 0 inside the windway; constant beyond the exit)."""
    he, hi, Lw = v.windway_exit_height_mm, v.windway_inlet_height_mm, v.windway_length_mm
    if xw >= 0.0:
        return 0.5 * he
    return 0.5 * (he + (hi - he) * (-xw / Lw))


CUT_STYLES = ("fan", "cone", "ellipse", "bowl")      # "bowl": the "ellipse" cut here; body.build_body replaces it by bowl_cut.py
from .presets import CONE_WIDEN_DEFAULT_MM  # noqa: E402  (the "cone" cut: how far each side opens at the outer face)
ELLIPSE_START_BLEND_DEG = 50.0  # "ellipse" cut: the start height of the flare rises from the lip level to the shelf level over this arc
ELLIPSE_NO_OVERHANG = True     # "ellipse" cut: no point moves inward across its own normal (False only to test the window check)
CONE_FLARE_EXPONENT = 1.6      # the sideways opening grows as (height above the lip) ** exponent: a dish, not a tube


# The preset keys that replace build fields of the record (RECORD_KEYS, record_overrides) and the voicing settings that
# are not in it (UNHASHED_KEYS, options_from) live in presets.py, which imports without Blender: calibration and
# sizing resolve a variant's voicing there before they look anything up (presets.resolve_voicing).
from .presets import RECORD_KEYS, UNHASHED_KEYS, options_from, record_overrides  # noqa: E402,F401


STUB_STYLES = ("box", "neck", "cone")
# The "cone" neck, rule version 3 (owner's choice of trial tb-d1, 2026-11-19; Analizes_ocarinas/Neck_volume/Neck_volume.md
# section 8). It is the neck of neck_solid with these values; a setting of the same name still replaces one for a trial.
FLANK_UNDER_FACE_MM = 0.05           # at the exit plane the flank of a neck with a cover is this far under the window's outer face
CONE_COVER_MM = 2.2                  # plastic over the pipe's roof at the mouth end, on the centre line
CONE_COVER_EXIT_MM = 1.6             # the same at the windway exit; the outer face of the window caps it (1.7 mm at +8 deg)
CONE_DEPTH_EXPONENT = 1.0            # the deck side is straight in profile
CONE_CORNER_COVER_MM = 1.3           # plastic kept over the upper corners of the pipe (the sections are two half ellipses)
CONE_BASE_DEPTH_FACTOR = 2.78        # depth where it meets the body / window width (24.5 mm at the 80 cm3 window)
NECK_SIDE_WALL_DEFAULT_MM = 2.5      # plastic beside the windway at the mouth end (the owner's sample: 2.5 mm)
NECK_BASE_WIDTH_FACTOR = 4.8         # width of the neck where it meets the body / window width (sample: 48.5 / 10)
NECK_BASE_DEPTH_FACTOR = 2.4         # depth there / window width (sample: 24.5 / 10)
NECK_WIDTH_EXPONENT = 1.7            # the bell: width and depth grow as (distance from the mouth end) ** exponent
NECK_DEPTH_EXPONENT = 1.4
NECK_TAIL_MM = 4.0                   # the neck ends this far beyond the labium, under the skin
NECK_DIVE_MM = 3.0                   # and its roof-side line has dropped this far by then
NECK_MIN_WALL_MM = 1.2               # least plastic between the pipe and the surface of the neck (owner, 2026-11-17)
NECK_STATIONS, NECK_POINTS = 28, 64


def neck_solid(v, wall: float, zc: float, xb: float, side_wall: float, base_width: float, base_depth: float,
               pipe_lowered_deg: float = 0.0, cover: float | None = None, stance_deg: float = 0.0,
               cover_exit: float | None = None, depth_exponent: float | None = None, width_exponent: float | None = None,
               floor: float | None = None, corner_cover: float | None = None, tilt_deg: float = 0.0):
    """The base neck in windway coordinates (xw, y, z): a closed mesh (V, F) and a dict of its sizes.

    tilt_deg (setting neck_tilt_deg, not in the hash): the outside turned toward the thumb face, the mouth end down as
    the player holds it, about a line NECK_TILT_HINGE_MM before the exit plane. The pipe does not move, so the hash
    does not change; a tilt that leaves less than NECK_MIN_WALL_MM of plastic around the pipe is refused.

    Each station is an ellipse across the windway. Its outer extreme stays on the line z = wall from the mouth end
    to the widest point of the window (xw = xb), so the roof over the windway keeps its thickness; from there it
    dives under the skin.

    cover (PROTOTYPE of 2026-11-18, setting neck_cover_mm): the top line of the neck is set by the PIPE instead: it
    passes cover_exit (setting neck_cover_exit_mm, default = cover) over the pipe's roof at the windway exit, and it
    never goes below the outer face of the voicing. The bell hangs on the body side of the pipe. Two cases:
      stance = the windway pitch (pipe_lowered_deg = 0)   the top line follows the pipe to the mouth end, where the
                                                           plastic over the roof is `cover`. The owner's sample and
                                                           the "Deluxe" reference are made like this.
      stance > the windway pitch                           the top line is straight at the neck's own angle, as on a
                                                           tube. The pipe dives under it toward the mouth end, so the
                                                           plastic over it grows from cover_exit. The "Ocarina 12"
                                                           reference is made like this (2.2 mm at the exit, 12.5 deg).
    In both the roof over the exit is thin, so the window cut meets little plastic there
    (Analizes_ocarinas/Neck_volume/Neck_volume.md).

    The shape of the body side of the neck (PROTOTYPE settings neck_depth_exponent, neck_width_exponent,
    neck_floor_mm): the depth and the width grow from the mouth end to the body as (distance) ** exponent. The
    defaults (1.4 and 1.7) give a bell, which is hollow in profile; 1 gives a cone with a straight flank, as on the
    "Deluxe" reference. floor is the plastic under the pipe at the mouth end (default STUB_FLOOR_MM).
    corner_cover (setting neck_corner_cover_mm): each section is then two half ellipses that share their width. The
    upper one is as high as it can be while this much plastic stays over the pipe's upper corners, and never more
    than half the depth; the lower one takes the rest. A full ellipse grows rounder over the pipe as the neck grows
    deep, and a deep straight flank would leave less than NECK_MIN_WALL_MM over the corners. Near the body, where
    the section is wide, the two halves are equal again and the section is the plain ellipse."""
    L, Lw = v.window_length_mm, v.windway_length_mm
    a = 0.5 * v.window_width_mm
    A0 = a + side_wall
    t_st = math.radians(stance_deg)
    if cover is not None and cover_exit is None:
        cover_exit = cover
    # The pipe inside the neck, lowered by pipe_lowered_deg about the labium edge: its floor and roof at station xw, and
    # how deep the ellipse must be there to keep NECK_MIN_WALL_MM under the corners of the pipe.
    tan_p = math.tan(math.radians(pipe_lowered_deg))
    cos_p = math.cos(math.radians(pipe_lowered_deg))

    def pipe_floor(xw):
        return zc - (L - xw) * tan_p - windway_half_height(v, xw) / cos_p

    def pipe_roof(xw):
        return zc - (L - xw) * tan_p + windway_half_height(v, xw) / cos_p

    def face(xw):                # the outer face of the voicing (z = wall in the voicing frame), seen in the turned frame of the neck
        return zc + (wall - zc + (xw - L) * math.sin(t_st)) / math.cos(t_st)

    if cover is not None:
        # The flank may not stand above the outer face where the window begins: a window that is cut square (no
        # shelf) would leave that plastic as a step at its back edge, inside the outside keep-out. A flank at the
        # neck's angle that passes through the outer face exactly at the exit plane has this height in the neck's frame:
        at_face = zc + (wall - zc - L * math.tan(t_st)) * math.cos(t_st)
        # Where the pipe is too steep for the wall (+8 deg under a 3 mm window wall) that would leave less than
        # NECK_MIN_WALL_MM of roof. The roof then keeps that minimum and stands above the outer face, and the outside
        # keep-out check says so (the former stub V-a3): a body is built and fails a named check, it is not refused.
        # The flank is kept FLANK_UNDER_FACE_MM below that height, so that it meets the outer face a little before the
        # exit plane and not exactly on it: on the mesh an exact meeting leaves a step of a few hundredths of a
        # millimetre at the rim (stub V-a35, whose pipe sits 0.15 mm higher, failed the keep-out with 0.021 mm).
        cover_exit = max(min(cover_exit, at_face - pipe_roof(0.0) - FLANK_UNDER_FACE_MM), min(cover_exit, NECK_MIN_WALL_MM))

    def flank(xw):
        if abs(pipe_lowered_deg) > 1e-9:                       # a straight flank at the neck's own angle
            return pipe_roof(0.0) + cover_exit
        return pipe_roof(min(xw, 0.0)) + cover_exit + (cover - cover_exit) * min(max(-xw / Lw, 0.0), 1.0)   # it follows the pipe

    def top_line(xw):
        return wall if cover is None else max(flank(xw), face(xw))

    floor = STUB_FLOOR_MM if floor is None else float(floor)
    p_depth = NECK_DEPTH_EXPONENT if depth_exponent is None else float(depth_exponent)
    p_width = NECK_WIDTH_EXPONENT if width_exponent is None else float(width_exponent)
    D0 = top_line(-Lw) - (pipe_floor(-Lw) - floor) if cover is not None else wall - (zc - 0.5 * v.windway_inlet_height_mm - floor)
    A1, D1 = 0.5 * base_width, base_depth

    def upper_cap(xw, A):
        """The most the upper half of the section at xw may be high (None: no limit, the section is a full ellipse)."""
        if corner_cover is None or xw > 0.0:
            return None
        k = math.sqrt(max(1.0 - (a / A) ** 2, 1e-6))
        return max(top_line(xw) - pipe_roof(xw) - float(corner_cover), 0.0) / max(1.0 - k, 1e-6)

    def depth_needed(xw, A):
        k = math.sqrt(max(1.0 - (a / A) ** 2, 1e-6))                        # ellipse half-depth at the pipe's corner / at the centre
        full = 2.0 * (top_line(xw) - pipe_floor(xw) + NECK_MIN_WALL_MM) / (1.0 + k)
        cap = upper_cap(xw, A)
        if cap is None or cap >= 0.5 * full:
            return full
        return cap + (top_line(xw) - cap - pipe_floor(xw) + NECK_MIN_WALL_MM) / k

    D0 = max(D0, depth_needed(-Lw, A0))
    D1 = max(D1, D0)
    end = L + NECK_TAIL_MM
    xs = list(np.linspace(-Lw, 0.0, NECK_STATIONS)) + list(np.linspace(0.0, end, 9)[1:])
    if cover is not None:
        # a station where the flank meets the outer face (the exit plane), so that the mesh has its bend exactly there
        lo, hi = -Lw, end
        if flank(lo) > face(lo) and flank(hi) < face(hi):
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                lo, hi = (mid, hi) if flank(mid) > face(mid) else (lo, mid)
            if min(abs(hi - x) for x in xs) > 1e-3:
                xs = sorted(xs + [hi])
    phi = np.linspace(0.0, 2.0 * math.pi, NECK_POINTS, endpoint=False)
    rings = []
    over_corners, centres = [], {}
    for xw in xs:
        t = min(1.0, (xw + Lw) / Lw)
        A = A0 + (A1 - A0) * t ** p_width
        D = D0 + (D1 - D0) * t ** p_depth
        if xw <= 0.0:
            D = max(D, depth_needed(xw, A))
        top = top_line(xw) if xw <= xb else top_line(xw) - NECK_DIVE_MM * ((xw - xb) / (end - xb)) ** 2
        cap = upper_cap(xw, A)
        up = 0.5 * D if cap is None else min(cap, 0.5 * D)                 # height of the upper half of the section
        if xw <= 0.0:                # plastic over the upper corners of the pipe: the ellipse is lower there than on the centre line
            k = math.sqrt(max(1.0 - (a / A) ** 2, 1e-6))
            over_corners.append(top - up * (1.0 - k) - pipe_roof(xw))
            centres[float(xw)] = top - 0.5 * D
        sn = np.sin(phi)
        rings.append(np.column_stack([np.full(NECK_POINTS, xw), A * np.cos(phi), top - up + np.where(sn >= 0.0, up, D - up) * sn]))
    if cover is not None and min(over_corners) < NECK_MIN_WALL_MM - 1e-6:
        raise ValueError(f"neck_cover_mm = {cover:g}: only {min(over_corners):.2f} mm of plastic is left over the corners of the pipe "
                         f"(least {NECK_MIN_WALL_MM:g} mm); give more cover or a wider mouth end (neck_side_wall_mm)")
    V, F = meshutil.prism_from_rings(rings)
    if meshutil.volume(V, F) < 0:
        F = F[:, ::-1]
    # the middle line of the neck from the mouth end to the exit, against the body: what the eye reads as its stance
    axis = stance_deg + math.degrees(math.atan2(centres[float(xs[0])] - centres[min(centres, key=abs)], Lw))
    moved = _tilt_neck(v, V, zc, float(tilt_deg)) if tilt_deg else None
    if moved:                    # the tilt lifts each section by this much over the pipe, which stays: the sizes below are the tilted neck's
        def lift(xw):
            return math.tan(math.radians(float(tilt_deg))) * max(-xw - NECK_TILT_HINGE_MM, 0.0)
        over_corners = [oc + lift(xw) for oc, xw in zip(over_corners, [x for x in xs if x <= 0.0])]
    else:
        def lift(xw):
            return 0.0
    return V, F, dict(**({"moved": moved} if moved else {}), mouth_width_mm=2 * A0, mouth_depth_mm=D0, base_width_mm=2 * A1, base_depth_mm=D1, length_mm=Lw + end,
                      pipe_lowered_deg=pipe_lowered_deg, min_wall_mm=NECK_MIN_WALL_MM,
                      pipe_floor_at_mouth_z_mm=pipe_floor(-Lw), cover_mm=cover, cover_exit_mm=cover_exit, over_pipe_corners_min_mm=float(min(over_corners)),
                      top_above_outer_face_at_exit_mm=float(top_line(0.0) - face(0.0)),
                      over_pipe_roof_at_exit_mm=float(top_line(0.0) - pipe_roof(0.0)),
                      over_pipe_roof_at_mouth_mm=float(top_line(-Lw) - pipe_roof(-Lw) + lift(-Lw)),
                      middle_line_deg_against_body=float(axis))


NECK_TILT_HINGE_MM = 3.0             # a tilted neck turns about a line this far before the exit plane (a hinge on the
                                     # plane itself left plastic inside the 45 deg flare at the window's back edge)


def _tilt_neck(v, V, zc: float, tilt_deg: float) -> dict:
    """Turn the neck's outside (V, windway coordinates, changed in place) toward the thumb face by tilt_deg, and
    measure the plastic left around the pipe ring by ring (low-voicing experiment, tandem_neck.py, 2026-11-24)."""
    t = math.tan(math.radians(tilt_deg))
    V[:, 2] += t * np.maximum(-V[:, 0] - NECK_TILT_HINGE_MM, 0.0)
    Lw, a, n = float(v.windway_length_mm), 0.5 * float(v.window_width_mm), NECK_POINTS
    least, at = 1e9, 0.0
    for k in range((len(V) - 2) // n):
        ring = V[k * n:(k + 1) * n]
        xw = float(ring[0, 0])
        if xw > 1e-9 or xw < -Lw - 1e-9:
            continue
        hh = windway_half_height(v, xw)
        for y in (-a, 0.0, a):
            for z in (zc - hh, zc + hh):
                d = _point_to_section(np.array([y, z]), ring[:, 1:])
                if d < least:
                    least, at = d, xw
    if least < NECK_MIN_WALL_MM - 1e-6:
        raise ValueError(f"neck_tilt_deg = {tilt_deg:g}: only {least:.2f} mm of plastic is left around the pipe {-at:.1f} mm from the exit "
                         f"(least {NECK_MIN_WALL_MM:g} mm)")
    return dict(tilt_deg=tilt_deg, hinge_mm_before_exit=NECK_TILT_HINGE_MM, least_plastic_around_pipe_mm=float(least),
                least_at_mm_from_exit=float(-at), mouth_end_moved_to_thumb_face_mm=float(t * (Lw - NECK_TILT_HINGE_MM)))


def _point_to_section(p, ring):
    """Distance from the point p to the closed convex polygon ring (n, 2); negative when p is outside it."""
    a, b = ring, np.roll(ring, -1, axis=0)
    ab, ap = b - a, p - a
    t = np.clip((ap * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-18), 0.0, 1.0)
    d = float(np.sqrt((((a + t[:, None] * ab) - p) ** 2).sum(1)).min())
    cross = ab[:, 0] * ap[:, 1] - ab[:, 1] * ap[:, 0]
    return d if bool((cross >= 0).all() or (cross <= 0).all()) else -d


SHELF_LAND_DEFAULT_MM = 0.8    # plastic left above the windway roof at the exit before the shelf cut starts


def build(v, port_frame, cut_style: str | None = None, cone_widen_mm: float | None = None,
          block_front_mm: float | None = None, shelf_angle_deg: float | None = None, shelf_land_mm: float = SHELF_LAND_DEFAULT_MM,
          windway_pitch_deg: float | None = None, stub_pitch_deg: float | None = None, stub_style: str | None = None,
          neck_base_width_mm: float | None = None, neck_base_depth_mm: float | None = None,
          neck_side_wall_mm: float = NECK_SIDE_WALL_DEFAULT_MM, pocket_blend_radius_mm: float | None = None,
          cone_flare_exponent: float | None = None, cone_widen_share: float | None = None,
          cavity_height=None, neck_cover_mm: float | None = None, neck_cover_exit_mm: float | None = None,
          neck_depth_exponent: float | None = None, neck_width_exponent: float | None = None,
          neck_floor_mm: float | None = None, neck_corner_cover_mm: float | None = None,
          neck_tilt_deg: float | None = None, pocket_back_margin_mm: float | None = None) -> VoicingSolids:
    """All voicing solids for the Voicing record `v`, placed at the port frame.

    The cut, its opening, the shelf, the two pitches, the stub style and the pocket blend come from the record
    (its build fields). The arguments of the same names replace them for a direct call (tests, prototypes); a body
    is always built from the record alone, so that its hash names what was built.

    block_front_mm: how far the block reaches beyond the labium point (default BLOCK_FRONT_MM). A negative value
    ends the block before the labium; -window length ends it at the windway exit.
    cavity_height: a function (xw, y) -> z of the chamber wall in the voicing frame, or None where the line along the
    normal misses the chamber. The pocket blend needs it to end where it meets the chamber wall; body.build_body
    gives it. Without it the blend has one fixed reach."""
    direct_pitch = windway_pitch_deg is not None
    cut_style = getattr(v, "window_cut", "fan") if cut_style is None else cut_style
    stub_style = getattr(v, "stub_style", "box") if stub_style is None else stub_style
    if cone_widen_mm is None:
        cone_widen_mm = getattr(v, "cut_widen_mm", 0.0) or CONE_WIDEN_DEFAULT_MM
    if shelf_angle_deg is None:
        shelf_angle_deg = getattr(v, "shelf_angle_deg", 0.0) if cut_style != "fan" else 0.0
    if pocket_blend_radius_mm is None:
        pocket_blend_radius_mm = getattr(v, "pocket_blend_radius_mm", 0.0)
    if cut_style not in CUT_STYLES:
        raise ValueError(f"unknown window cut {cut_style!r}; known: {', '.join(CUT_STYLES)}")
    if cut_style != "fan" and v.shape != "teardrop":
        raise ValueError(f"the {cut_style} window cut is made for the teardrop window; a {v.shape.replace('_', ' ')} needs the plain build "
                         "(window_cut = fan)")
    block_front = BLOCK_FRONT_MM if block_front_mm is None else float(block_front_mm)
    pitch = float(windway_pitch_deg) if direct_pitch else float(getattr(v, "windway_pitch_deg", 0.0))
    if stub_pitch_deg is not None:
        stub_pitch = float(stub_pitch_deg)
    elif not direct_pitch:
        stub_pitch = float(getattr(v, "stub_pitch_deg", 0.0))
    elif stub_style in ("neck", "cone"):
        stub_pitch = max(pitch, 0.0)                     # a direct call: the neck hides a lowered windway and follows a raised one
    else:
        stub_pitch = pitch
    shelf = float(shelf_angle_deg)
    if shelf and cut_style == "fan":
        raise ValueError("shelf_angle_deg needs window_cut = cone or ellipse")
    if stub_style not in STUB_STYLES:
        raise ValueError(f"unknown stub style {stub_style!r}; known: {', '.join(STUB_STYLES)}")
    experimental = bool(pitch or stub_pitch or shelf or stub_style != "box" or cut_style != "fan")
    base_cut = "ellipse" if cut_style == "bowl" else cut_style          # the bowl is cut later, through the finished outside
    frame = voicing_frame(port_frame)
    L, W, wall = v.window_length_mm, v.window_width_mm, v.wall_at_window_mm
    e = v.labium_edge_thickness_mm
    Lw = v.windway_length_mm
    a = 0.5 * W
    if cone_widen_share is not None:
        cone_widen_mm = float(cone_widen_share) * W
    out = np.array(v.outline_mm(OUTLINE_STEP_DEG), dtype=np.float64)        # (n, 3): xw, y, normal angle
    n = len(out)
    nx, ny = np.cos(out[:, 2]), np.sin(out[:, 2])
    xb = float(out[np.argmax(out[:, 1]), 0])                                # xw of the widest point

    # ---------------- window cutter: throat + labium ramp, one closed mesh
    z_top = wall + CUT_ABOVE_MM
    if stub_pitch > 0:                                                       # a raised stub stands above the outer face at the exit
        z_top += (wall + L) * math.sin(math.radians(stub_pitch)) + 0.5
    reach = (z_top - e) / math.tan(math.radians(v.labium_ramp_angle_deg))
    zc0 = windway_centre_z(v)
    # the windway roof where it meets the window (the exit plane), in the voicing frame
    roof_at_exit = zc0 + L * math.sin(math.radians(pitch)) + 0.5 * v.windway_exit_height_mm / math.cos(math.radians(pitch))
    z_shelf = min(max(roof_at_exit + float(shelf_land_mm), e + 0.2), wall - 0.2)
    # where the checks slice the windway half of the window: above the windway roof and below the shelf cut
    z_slice = min(roof_at_exit + 0.5 * float(shelf_land_mm), wall - 0.3)
    if v.shape == "teardrop":
        f = np.array([ramp_reach_factor(abs(t)) for t in out[:, 2]])
    else:
        # forced rounded rectangle: the labium is the straight far edge; ramp on normals within 45 deg of the jet
        f = np.array([1.0 if abs(t) < math.radians(45.0) else 0.0 for t in out[:, 2]])
    ring_lo = np.column_stack([out[:, 0], out[:, 1], np.full(n, -CUT_BELOW_MM)])
    ring_edge = np.column_stack([out[:, 0], out[:, 1], np.full(n, e)])
    cone = None
    if base_cut == "cone":
        # The labium half of the outline is pushed along the jet by (z - e) / tan(ramp): a slanted cylinder, which is
        # a cone with its apex far upstream. So the surface passes through the outline at the top of the edge (the lip
        # keeps its thickness) and the ramp has the record's angle everywhere. Sideways the cut opens by
        # cone_widen_mm at the outer face, and faster near the surface than near the lip (CONE_FLARE_EXPONENT), so it
        # meets the skin at a shallow angle: a dish, not a tube (owner, 2026-11-17, after the Songbird's window).
        # The windway half stays vertical up to z_shelf. Above it, it opens sideways in the same way, and leans back
        # along its own normal by the shelf angle (full within RAMP_FULL_DEG of upstream, nothing at the widest points).
        tan_r = math.tan(math.radians(v.labium_ramp_angle_deg))
        tan_s = math.tan(math.radians(shelf))
        widen = max(float(cone_widen_mm), 0.0) / a
        flare_p = CONE_FLARE_EXPONENT if cone_flare_exponent is None else float(cone_flare_exponent)
        labium = out[:, 0] > xb + 1e-9
        g = np.array([ramp_reach_factor(math.pi - abs(t)) for t in out[:, 2]])
        g[labium] = 0.0

        def ring_at(z):
            x, y = out[:, 0].copy(), out[:, 1].copy()
            x[labium] += (z - e) / tan_r
            y[labium] *= 1.0 + widen * ((z - e) / (wall - e)) ** flare_p
            if z > z_shelf:
                up = ~labium
                y[up] *= 1.0 + widen * ((z - z_shelf) / (wall - z_shelf)) ** flare_p
                back = g * (z - z_shelf) * tan_s
                x[up] += (back * nx)[up]
                y[up] += (back * ny)[up]
            return np.column_stack([x, y, np.full(n, z)])

        levels = [z for z in np.linspace(e, z_top, 10)[1:] if abs(z - z_shelf) > 0.15] + [z_shelf]
        rings_w = [ring_lo, ring_edge] + [ring_at(float(z)) for z in sorted(levels)]
        cone = dict(widen_mm=float(cone_widen_mm), flare_exponent=flare_p, opening_width_at_outer_face_mm=W + 2.0 * float(cone_widen_mm),
                    rim_length_beyond_tip_mm=(wall - e) / tan_r)
    elif base_cut == "ellipse":
        # One surface, lofted from the window outline to an ellipse at the outer face, so the two halves of the
        # "cone" cut do not meet in a crease (the owner's choice among the prototypes, 2026-11-17). The ellipse reaches from the shelf's back edge to the
        # end of the ramp along the jet, and cone_widen_mm beyond the window on each side. Each outline point goes to
        # the ellipse point at the same angle about the centre. The labium half starts at the top of the edge (the lip
        # keeps its thickness; at the tip the ramp has the record's angle). The windway half starts at z_shelf, and
        # the start height changes smoothly between the two over ELLIPSE_START_BLEND_DEG of the outline.
        tan_r = math.tan(math.radians(v.labium_ramp_angle_deg))
        flare_p = CONE_FLARE_EXPONENT if cone_flare_exponent is None else float(cone_flare_exponent)
        back = (wall - z_shelf) * math.tan(math.radians(shelf))
        x_far = L + (wall - e) / tan_r
        ex_c, ex_a, ex_b = 0.5 * (x_far - back), 0.5 * (x_far + back), a + max(float(cone_widen_mm), 0.0)
        psi = np.arctan2(out[:, 1], out[:, 0] - xb)                        # angle about the middle of the widest chord
        qx, qy = ex_c + ex_a * np.cos(psi), ex_b * np.sin(psi)
        u = np.clip((np.degrees(np.abs(psi)) - 90.0) / ELLIPSE_START_BLEND_DEG, 0.0, 1.0)
        z0 = e + (z_shelf - e) * (u * u * (3.0 - 2.0 * u))

        dx, dy = qx - out[:, 0], qy - out[:, 1]
        inward = [0.0]

        def ring_at(z):
            # Along the jet the move is linear in height (on the labium that is the ramp, at the shelf it is the
            # shelf angle); sideways it grows as a power, so the dish opens gently near the lip.
            t = np.clip((z - z0) / (wall - z0), 0.0, None)
            sx, sy = dx * t, dy * t ** flare_p
            # NO OVERHANG: a point never moves inward across its own normal. Next to the widest points, on the
            # windway side, the slide along the jet points a little into the window; low down it can outweigh the
            # sideways opening (most on a window that is much wider than long). There the wall stays upright.
            sn = np.minimum(sx * nx + sy * ny, 0.0) if ELLIPSE_NO_OVERHANG else np.zeros(n)
            inward[0] = max(inward[0], float(-sn.min()))
            return np.column_stack([out[:, 0] + sx - sn * nx, out[:, 1] + sy - sn * ny, np.full(n, z)])

        levels = [z for z in np.linspace(e, z_top, 12)[1:] if abs(z - z_shelf) > 0.12] + [z_shelf]
        rings_w = [ring_lo, ring_edge] + [ring_at(float(z)) for z in sorted(levels)]
        cone = dict(style="ellipse", widen_mm=float(cone_widen_mm), flare_exponent=flare_p, ellipse_length_mm=2 * ex_a, ellipse_width_mm=2 * ex_b,
                    ellipse_centre_xw_mm=ex_c, shelf_back_mm=back, rim_length_beyond_tip_mm=(wall - e) / tan_r,
                    inward_move_removed_max_mm=inward[0])
    else:
        ring_top = np.column_stack([out[:, 0] + f * reach * nx, out[:, 1] + f * reach * ny, np.full(n, z_top)])
        rings_w = [ring_lo, ring_edge, ring_top]
    wV, wF = meshutil.prism_from_rings(rings_w)
    window = (_to_frame(wV, L, frame), wF)

    # ---------------- pocket footprint: straight back edge at the exit plane, margin around the labium half
    m = POCKET_MARGIN_MM
    front = [(x + m * cx, y + m * sy) for (x, y, t), cx, sy in zip(out, nx, ny) if abs(t) <= 0.5 * math.pi + 1e-9]
    front.sort(key=lambda p: math.atan2(p[1], p[0] - xb))                    # from -90 deg round to +90 deg
    xk = -POCKET_BACK_OVERLAP_MM
    foot = [(xk, -(a + m))] + [p for p in front] + [(xk, a + m)]
    foot = _dedupe(foot)
    foot = np.array(foot, dtype=np.float64)
    blend = None
    if pocket_blend_radius_mm > 0:
        # A flat ceiling for POCKET_BLEND_FLAT_MM beyond the labium, then a skirt that falls away on a circle of the
        # given radius UNTIL IT MEETS THE CHAMBER WALL. How far that is depends on the chamber: a flat wall is met after
        # a few millimetres, a strongly curved one (a stub, the bulb of P2) falls away under the skirt and is met later.
        # So the reach is found per direction on the cavity itself (cavity_height), and the skirt ends
        # POCKET_BLEND_UNDER_MM below the chamber wall there: no step is left at its rim, and nothing is cut beyond the
        # meeting line. (Until 2026-11-18 the skirt was a parabola with a fixed reach of 12.5 mm. On a curved chamber
        # it never met the wall: it cut a step into it, thinned it, and on P2-80 left a 0.06 mm sliver.)
        # Every ring is the labium half of the outline pushed out along its normals, in one fixed order.
        Rp = float(pocket_blend_radius_mm)
        idx = [i for i in range(n) if abs(out[i, 2]) <= 0.5 * math.pi + 1e-9]
        idx.sort(key=lambda i: math.atan2(out[i, 1], out[i, 0] - xb))
        base = [(xk, -a, 0.0, -1.0)] + [(out[i, 0], out[i, 1], nx[i], ny[i]) for i in idx] + [(xk, a, 0.0, 1.0)]   # point, push direction
        # pocket_back_margin_mm (an option, 2026-11-26; not in the hash): the pocket's back edge follows the exit half of
        # the window outline at this margin, as an upright wall, instead of running straight across at the exit plane.
        # The flat ceiling then no longer lies under the windway's exit corners, where the windway's floor runs on beside
        # the window: with a low pipe that floor was a plate 0.18 mm thick over the ceiling (P4-bowl, pipe +4 deg). The
        # chamber's own wall stays under it.
        back = []
        if pocket_back_margin_mm is not None:
            mb = float(pocket_back_margin_mm)
            back = [i for i in range(n) if abs(out[i, 2]) > 0.5 * math.pi + 1e-9]
            back.sort(key=lambda i: math.atan2(out[i, 1], out[i, 0] - xb) % (2.0 * math.pi))        # from +90 deg round to -90 deg
            base = base[1:-1] + [(out[i, 0] + mb * nx[i], out[i, 1] + mb * ny[i], 0.0, 0.0) for i in back]

        def arc(d):
            return -(Rp - math.sqrt(max(Rp * Rp - d * d, 0.0)))

        d_max = POCKET_BLEND_REACH_MAX * Rp

        def find_reach(bx, by, ux, uy):
            """How far the skirt goes in one direction, and how it ends there:
            "met"         it meets the chamber wall (it ends POCKET_BLEND_UNDER_MM below it)
            "side wall"   the chamber ends first: its wall has turned upright (beside the windway exit of a small
                          chamber). The skirt stops POCKET_BLEND_SIDE_INSET_MM before that wall; no ledge is left
            "full reach"  neither happened within the largest reach: the skirt is a steep wall there, and the
                          returned step is what is left between its lower end and the chamber wall"""
            def gap(d):
                mm = POCKET_BLEND_FLAT_MM + d
                h = cavity_height(bx + mm * ux, by + mm * uy)
                return None if h is None else arc(d) - (h - POCKET_BLEND_UNDER_MM)

            lo, d = 0.0, POCKET_BLEND_STEP_MM
            while d <= d_max + 1e-9:
                g = gap(d)
                if g is None:                              # the line along the normal misses the chamber from here on
                    hi = d
                    for _ in range(10):
                        mid = 0.5 * (lo + hi)
                        lo, hi = (mid, hi) if gap(mid) is not None else (lo, mid)
                    return max(lo - POCKET_BLEND_SIDE_INSET_MM, 0.5 * POCKET_BLEND_STEP_MM), "side wall", 0.0
                if g <= 0.0:
                    hi = d
                    for _ in range(14):
                        mid = 0.5 * (lo + hi)
                        g = gap(mid)
                        lo, hi = (mid, hi) if (g is not None and g > 0.0) else (lo, mid)
                    return hi, "met", 0.0
                lo, d = d, d + POCKET_BLEND_STEP_MM
            return lo, "full reach", max((gap(lo) or 0.0) - POCKET_BLEND_UNDER_MM, 0.0)

        pushed = base[:len(base) - len(back)]             # the points that carry a skirt (all of them without the option)
        if cavity_height is None:                          # a direct call without a chamber: one fixed reach
            found = [(min(POCKET_BLEND_REACH_NO_CHAMBER_MM, d_max), "fixed", 0.0)] * len(pushed)
        else:
            found = [find_reach(*point) for point in pushed]
        found += [(min(f[0] for f in found), "back", 0.0)] * len(back)    # the back wall is upright, as deep as the least skirt
        skirt = [f[0] for f in found]
        fractions = (0.0, 0.08, 0.18, 0.32, 0.50, 0.72, 1.0)
        rings_p = [np.array([(bx + (POCKET_BLEND_FLAT_MM + s * r) * ux, by + (POCKET_BLEND_FLAT_MM + s * r) * uy, arc(s * r))
                             for (bx, by, ux, uy), r in zip(base, skirt)], dtype=np.float64) for s in fractions]
        far = rings_p[-1].copy()
        far[:, 2] = min(-POCKET_DEPTH_MM, float(far[:, 2].min()) - 2.0)
        foot = rings_p[0][:, :2].copy()
        m = POCKET_BLEND_FLAT_MM
        pV, pF = meshutil.prism_from_rings([far] + rings_p[::-1])
        # The first and the last direction are the two back corners, beside the windway exit. The others are the labium
        # half of the window outline: the part the jet and the chamber air meet. The check reads those.
        labium, corners = (found[:len(pushed)], ()) if back else (found[1:-1], (found[0], found[-1]))
        blend = dict(radius_mm=Rp, on_the_chamber=cavity_height is not None, directions=len(labium),
                     met_directions=sum(1 for f in labium if f[1] == "met"),
                     side_wall_directions=sum(1 for f in labium if f[1] == "side wall"),
                     full_reach_directions=sum(1 for f in labium if f[1] == "full reach"),
                     step_left_mm=float(max(f[2] for f in labium)),
                     reach_min_mm=float(min(f[0] for f in labium)), reach_max_mm=float(max(f[0] for f in labium)),
                     corners=[dict(reach_mm=float(f[0]), ends=f[1], step_left_mm=float(f[2])) for f in corners],
                     depth_mm=float(-far[0, 2]), under_mm=POCKET_BLEND_UNDER_MM)
    else:
        if pocket_back_margin_mm is not None:
            raise ValueError("pocket_back_margin_mm needs the pocket blend (pocket_blend_radius_mm)")
        r0 = np.column_stack([foot, np.full(len(foot), -POCKET_DEPTH_MM)])
        r1 = np.column_stack([foot, np.zeros(len(foot))])
        pV, pF = meshutil.prism_from_rings([r0, r1])
    pocket = (_to_frame(pV, L, frame), pF)

    # ---------------- windway cutter: tapered duct, then on into the broad end of the window
    zc = windway_centre_z(v)
    # The cutter must come out of the mouth end of the stub. When the pipe is turned inside the stub (a neck that
    # stands while the pipe lies lower), its start face meets the end face of the stub at an angle, so it starts
    # further out: far enough that the whole start face is 0.1 mm beyond the end plane of the stub.
    rel = math.radians(abs(stub_pitch - pitch))
    hh_in = 0.5 * v.windway_inlet_height_mm
    x0 = -Lw - max(WINDWAY_OVERSHOOT_MM, (L + Lw + 0.1 + hh_in * math.sin(rel)) / math.cos(rel) - (L + Lw))
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
    duct = pitched_frame(frame, zc, pitch) if pitch else None
    windway = (_to_frame(dV, L, duct or frame), dF)

    # ---------------- block: voicing block and mouthpiece stub
    z_bot = zc - 0.5 * v.windway_inlet_height_mm - STUB_FLOOR_MM
    half_w = a + STUB_SIDE_WALL_MM
    neck = None
    if stub_style in ("neck", "cone"):
        if pitch > stub_pitch + 1e-9:
            raise ValueError("the windway is raised above the roof line of the neck: give stub_pitch_deg at least the windway pitch")
        cone_neck = stub_style == "cone"

        def given(value, cone_value):                    # a setting that was given, else the cone's value, else the bell's default
            return float(value) if value is not None else (cone_value if cone_neck else None)

        nV, nF, neck = neck_solid(v, wall, zc, xb, float(neck_side_wall_mm),
                                  NECK_BASE_WIDTH_FACTOR * W if neck_base_width_mm is None else float(neck_base_width_mm),
                                  (CONE_BASE_DEPTH_FACTOR if cone_neck else NECK_BASE_DEPTH_FACTOR) * W if neck_base_depth_mm is None
                                  else float(neck_base_depth_mm),
                                  pipe_lowered_deg=stub_pitch - pitch, stance_deg=stub_pitch,
                                  cover=given(neck_cover_mm, CONE_COVER_MM), cover_exit=given(neck_cover_exit_mm, CONE_COVER_EXIT_MM),
                                  depth_exponent=given(neck_depth_exponent, CONE_DEPTH_EXPONENT), width_exponent=neck_width_exponent,
                                  floor=neck_floor_mm, corner_cover=given(neck_corner_cover_mm, CONE_CORNER_COVER_MM),
                                  tilt_deg=float(neck_tilt_deg or 0.0))
        block = (_to_frame(nV, L, pitched_frame(frame, zc, stub_pitch) if stub_pitch else frame), nF)
        half_w = max(half_w, 0.5 * neck["base_width_mm"])
    elif not stub_pitch:
        bV, bF = meshutil.box_local(-Lw, L + block_front, -half_w, half_w, z_bot, wall)
        block = (_to_frame(bV, L, frame), bF)
    else:
        # The outer stub is its own solid, turned by its own pitch about the labium edge and cut off at the exit
        # plane. The flat pad around the window stays in the voicing frame.
        sV, sF = meshutil.box_local(-Lw, 3.0, -half_w, half_w, z_bot, wall)
        stub = (_to_frame(sV, L, pitched_frame(frame, zc, stub_pitch)), sF)
        hV, hF = meshutil.box_local(-Lw - 80.0, 0.0, -80.0, 80.0, -80.0, 80.0)
        bV, bF, _ = meshutil.boolean(stub, (_to_frame(hV, L, frame), hF), "INTERSECT")
        block = (bV, bF)
        if L + block_front > 0.6:
            pV, pF = meshutil.box_local(-0.5, L + block_front, -half_w - 0.02, half_w + 0.02, z_bot - 0.02, wall)   # no face shared with the stub
            bV, bF, _ = meshutil.boolean(block, (_to_frame(pV, L, frame), pF), "UNION")
            block = (bV, bF)

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
        z_top_mm=z_top, cut_style=cut_style, cone=cone, block_front_mm=block_front, pocket_blend_radius_mm=float(pocket_blend_radius_mm),
        pocket_blend=blend,
        windway_pitch_deg=pitch, stub_pitch_deg=stub_pitch, stub_style=stub_style, neck=neck, shelf_angle_deg=shelf, shelf_start_z_mm=z_shelf if shelf else None,
        shelf_reach_mm=(z_top - z_shelf) * math.tan(math.radians(shelf)) if shelf else 0.0,   # how far the shelf cut leans back at the top of the cutter
        windway_roof_at_exit_plane_z_mm=roof_at_exit,
        window_slice_z_mm=(z_slice if experimental else None),
        # The ellipse cut opens next to the widest points below every level at which the windway half could be
        # sliced, so its window is measured as the free opening seen straight in (checks_geo.measure_voicing).
        window_area_by_projection=(base_cut == "ellipse"))
    return VoicingSolids(frame=frame, block=block, pocket=pocket, window=window, windway=windway, outline=out,
                         footprint=foot, info=info, duct_frame=duct)


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
