"""The neck's outside moved against the pipe (series 3, after the owner's draft of 2026-11-24).

The owner drew a slim straight cone on base A of the sculpt file (sculpt/OCA_sculpt_owner_draft_2026-11-24.blend):
25.4 mm across at the body, 15.2 mm at the mouth end, level, with the pipe running diagonally inside it, and a
flattened tube around the voicing. The owner's words: "angling the neck should also be posible without tilting the
internal cut to a small degree for ergonomics, also shifting slightly the postion of the neck ofset".

The add-on's cone neck already takes a width and a depth at the body, a wall beside the pipe and a floor under it at
the mouth end (settings that are not in the voicing hash). What it cannot do is turn its outside without the pipe,
except by stub_pitch_deg, which is in the hash. This file adds that from outside, with no change to an add-on file:
the rings of the add-on's neck are sheared about a line 3 mm before the windway's exit plane. The mouth end stays in its own plane, so
the pipe's cutter and the voicing hash do not change.

Preset keys (all optional; nothing is done when none is given):

    neck_tilt_deg     the outside turned toward the thumb face (the mouth end goes down as the player holds it);
                      negative: toward the finger deck
    neck_yaw_deg      the outside turned sideways; positive: the mouth end toward the tail
    neck_offset_mm    the outside moved sideways as a whole (positive: toward the tail), reached 15 mm from the exit plane
    neck_tail_mm      how far the neck runs on beyond the labium, under the skin (the add-on: 4 mm)

The plastic left around the pipe is measured ring by ring; under the add-on's least (1.2 mm) the build is refused,
with the number. LAST holds the measure of the neck built last.
"""
from __future__ import annotations

import math
import sys

import numpy as np

from ocarina_addon import voicing_geo

KEYS = ("neck_tilt_deg", "neck_yaw_deg", "neck_offset_mm", "neck_tail_mm")
OFFSET_REACH_MM = 15.0
HINGE_MM = 3.0
LAST: dict = {}
_NOW: dict = {}


def _smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


def _point_to_ring(p, ring):
    """Distance from the point p to the closed polygon ring (n, 2); negative when p is outside it."""
    a, b = ring, np.roll(ring, -1, axis=0)
    ab, ap = b - a, p - a
    t = np.clip((ap * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-18), 0.0, 1.0)
    d = float(np.sqrt((((a + t[:, None] * ab) - p) ** 2).sum(1)).min())
    cross = ab[:, 0] * ap[:, 1] - ab[:, 1] * ap[:, 0]
    inside = bool((cross >= 0).all() or (cross <= 0).all())           # the sections are convex
    return d if inside else -d


def install():
    plain_build, plain_neck = voicing_geo.build, voicing_geo.neck_solid

    def build(v, port_frame, *args, **kw):
        preset = sys._getframe(1).f_locals.get("preset") or {}
        _NOW.clear()
        LAST.clear()
        if any(preset.get(k) is not None for k in KEYS):
            _NOW.update({k: float(preset[k]) for k in KEYS if preset.get(k) is not None})
            _NOW["tail_sign"] = float(np.sign(np.asarray(port_frame[1], float)[0]) or 1.0)      # the across axis against the body's X
        try:
            return plain_build(v, port_frame, *args, **kw)
        finally:
            _NOW.clear()

    def neck_solid(v, wall, zc, xb, *args, **kw):
        if not _NOW:
            return plain_neck(v, wall, zc, xb, *args, **kw)
        keep = voicing_geo.NECK_TAIL_MM
        try:
            voicing_geo.NECK_TAIL_MM = _NOW.get("neck_tail_mm", keep)
            V, F, info = plain_neck(v, wall, zc, xb, *args, **kw)
        finally:
            voicing_geo.NECK_TAIL_MM = keep
        tilt, yaw = _NOW.get("neck_tilt_deg", 0.0), _NOW.get("neck_yaw_deg", 0.0)
        off, s = _NOW.get("neck_offset_mm", 0.0), _NOW["tail_sign"]
        V = np.array(V, float)
        # toward the mouth end, from a hinge HINGE_MM before the exit plane: a tilt hinged on the exit plane itself
        # left plastic inside the 45 deg flare at the window's back edge (trial s3-t6, first build)
        u = np.maximum(-V[:, 0] - HINGE_MM, 0.0)
        V[:, 2] += math.tan(math.radians(tilt)) * u
        V[:, 1] += s * (math.tan(math.radians(yaw)) * u + off * np.array([_smooth(x / OFFSET_REACH_MM) for x in u]))
        # the plastic around the pipe, ring by ring (the pipe is not lowered inside these necks)
        Lw, a = float(v.windway_length_mm), 0.5 * float(v.window_width_mm)
        n = voicing_geo.NECK_POINTS
        least, at = 1e9, None
        for k in range((len(V) - 2) // n):
            ring = V[k * n:(k + 1) * n]
            xw = float(ring[0, 0])
            if xw > 1e-9 or xw < -Lw - 1e-9:
                continue
            hh = voicing_geo.windway_half_height(v, xw)
            for y in (-a, 0.0, a):
                for z in (zc - hh, zc + hh):
                    d = _point_to_ring(np.array([y, z]), ring[:, 1:])
                    if d < least:
                        least, at = d, xw
        mouth = V[:n]
        LAST.update(tilt_deg=tilt, yaw_deg=yaw, offset_mm=off, tail_mm=float(_NOW.get("neck_tail_mm", keep)),
                    least_plastic_around_pipe_mm=float(least), least_at_mm_from_exit=float(-at),
                    mouth_end_moved_to_thumb_face_mm=float(math.tan(math.radians(tilt)) * (Lw - HINGE_MM)),
                    mouth_end_moved_to_tail_mm=float(math.tan(math.radians(yaw)) * (Lw - HINGE_MM) + off),
                    mouth_end_across_mm=float(np.ptp(mouth[:, 1])), mouth_end_deep_mm=float(np.ptp(mouth[:, 2])))
        info = dict(info, moved=dict(LAST))
        if (tilt or yaw or off) and least < voicing_geo.NECK_MIN_WALL_MM - 1e-6:
            raise ValueError(f"the neck's outside was moved too far for its thickness: {least:.2f} mm of plastic is left around the pipe "
                             f"{-at:.1f} mm from the exit (least {voicing_geo.NECK_MIN_WALL_MM:g} mm)")
        return V, F, info

    voicing_geo.build, voicing_geo.neck_solid = build, neck_solid
