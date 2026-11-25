"""Series 3 of the low-voicing experiment (2026-11-20): the balance, necks, blends and inner walls.

Plan: Analizes_ocarinas/Low_voicing/Plan_series3_balance_necks_blends.md. Run with Blender 5.1 from the root of the
checkout:

    blender -b --factory-startup --python Analizes_ocarinas/Low_voicing/series3_trials.py -- [--only P4:s3-c42,P1] [--group base]

The base of series 3 is the main checkout as it stood on 2026-11-20 01:02 (refs/snapshots/low-voicing-base-s3): rule
version 3 finished, hole_to_voicing measures the plastic at each rim, and the preset key neck_foot_width_mm is gone.
The foot of the neck is therefore given with the prototype setting neck_base_width_mm (not hashed).

It reuses the build, the numbers and the pictures of low_voicing_trials.py, and writes beside series 1 and 2 without
touching them:

    addon_checks/<P>-80-<trial>.md / .json, addon_renders/<...>/       the usual report and pictures
    Analizes_ocarinas/Low_voicing/images_s3/<P>_<trial>_*.png           the pictures of the sheets
    Analizes_ocarinas/Low_voicing/trials_s3/<P>_<trial>.json            one trial
    Analizes_ocarinas/Low_voicing/series3_trials.json                   all of them, merged
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (str(ROOT), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import blend_fillet  # noqa: E402
import inner_walls  # noqa: E402
import low_voicing_trials as lv  # noqa: E402
import tandem_neck  # noqa: E402
import uneven_wall  # noqa: E402
import voicing_shoulder  # noqa: E402
from ocarina_addon import body as body_mod, kernel_bridge  # noqa: E402

lv.IMG = HERE / "images_s3"
lv.TRIAL_DIR = HERE / "trials_s3"
MERGED = HERE / "series3_trials.json"

LONG = {"voicing_rules.windway_length_mm": 45.0}
P4, P1, BOTH = ("P4",), ("P1",), ("P4", "P1")
ALL = ("P4", "P1", "P0", "P2", "P3")
PORT = dict(port_angle_deg=10.0)
ROUND = dict(neck_floor_mm=8.6, neck_base_depth_mm=29.0)        # the round 13.8 mm mouth end and the 29 mm deep foot of lv-10fwdnr


def foot(mm):
    return dict(neck_base_width_mm=mm)


# name: (group, what it is, preset overrides (a value may be {"P4": .., "P1": ..}), parameter overrides, bodies)
TRIALS = {
    # ---- step 0: the base. How wide may the foot of the neck be at port 10 deg, by the corrected check?
    "s3-c42": ("base", "port 10 deg, pipe 45 mm, the rule's foot (4.8 x the window width)", dict(PORT), LONG, BOTH),
    "s3-c38": ("base", "port 10 deg, pipe 45 mm, foot 38 mm", dict(PORT, **foot(38.0)), LONG, BOTH),
    "s3-c34": ("base", "port 10 deg, pipe 45 mm, foot 34 mm", dict(PORT, **foot(34.0)), LONG, BOTH),
    "s3-c32": ("base", "port 10 deg, pipe 45 mm, foot 32 mm", dict(PORT, **foot(32.0)), LONG, P4),
    # the decided values (the handover's lv-10fw) and the control of series 3: the same with the round tip, no 8 mm dish
    "s3-fw": ("base", "the decided values: port 10 deg, pipe 45 mm, foot 29 mm (P4) / 34 mm (P1)",
              dict(PORT, **foot({"P4": 29.0, "P1": 34.0})), LONG, BOTH),
    "s3-fwr": ("base", "the control of series 3: the decided values and the round mouth end, foot 29 mm deep",
               dict(PORT, **foot({"P4": 29.0, "P1": 34.0}), **ROUND), LONG, BOTH),
}

# ---- stage W, first pass: the inner walls on the control s3-fwr (plan, section 8).
# The room, measured on the control (row "room" of s3-fwr; x along the body from the lip, mm):
#   P4: the pocket's skirt ends at about -12.5 / +12.5; thumb hole rims at -15.8 (left) and +23.1 (right)
#   P1: skirt -12.6 / +12.5; rims at -19.3 and +19.0
# A wall stands "near the thumb hole" (the patent): its face 2.5 mm from the rim, or 0.8 mm where there is no room
# (P4 left: 3.3 mm between the rim and the skirt). The fillet on the hole's side is kept off the rim.
SKIRT = {"P4": (-12.5, 12.5), "P1": (-12.6, 12.5)}
RIMS = {"P4": (-15.79, 23.09), "P1": (-19.27, 19.01)}


def walls(sides="LR", height=0.5, t=2.4, rf=2.0, near="hole", gap=2.5):
    """Preset overrides for inner walls on P4 and P1 (per body: the place depends on the body's holes)."""
    xs, fil = {}, {}
    for pid in ("P4", "P1"):
        xs[pid], fil[pid] = {}, {}
        for side, sign in (("L", -1.0), ("R", 1.0)):
            if side not in sides:
                continue
            rim, skirt = abs(RIMS[pid][0 if side == "L" else 1]), abs(SKIRT[pid][0 if side == "L" else 1])
            if near == "hole":
                g = max(0.8, min(gap, rim - skirt - t))            # as far from the rim as the room allows, at least 0.8 mm
                x = rim - g - 0.5 * t
            else:                                                  # near the window: the face 1 mm outside the skirt
                x = skirt + 1.0 + 0.5 * t
                g = rim - x - 0.5 * t
            r_hole, r_win = max(0.0, min(rf, g - 0.3)), rf
            xs[pid][side] = round(sign * x, 2)
            fil[pid][side] = [r_hole, r_win] if side == "L" else [r_win, r_hole]
    return dict(inner_wall_x_mm=xs, inner_wall_height=height, inner_wall_thickness_mm=t, inner_wall_fillet_mm=fil)


CONTROL = dict(PORT, **foot({"P4": 29.0, "P1": 34.0}), **ROUND)
TRIALS.update({
    "s3-w25": ("walls", "inner walls, both, top edge at 0.25 of the section height", dict(CONTROL, **walls(height=0.25)), LONG, BOTH),
    "s3-w38": ("walls", "inner walls, both, top edge at 0.375 of the section height", dict(CONTROL, **walls(height=0.375)), LONG, BOTH),
    "s3-w50": ("walls", "inner walls, both, top edge at the mid-line (the patent's height)", dict(CONTROL, **walls(height=0.5)), LONG, BOTH),
    "s3-wL": ("walls", "the left wall only, to the mid-line", dict(CONTROL, **walls("L", 0.5)), LONG, BOTH),
    "s3-wR": ("walls", "the right wall only, to the mid-line", dict(CONTROL, **walls("R", 0.5)), LONG, BOTH),
    "s3-wf": ("walls", "both, to the mid-line, each wall near the window instead of near its thumb hole",
              dict(CONTROL, **walls(height=0.5, near="window")), LONG, P4),
    "s3-wt16": ("walls", "both, to the mid-line, 1.6 mm thick", dict(CONTROL, **walls(height=0.5, t=1.6, rf=1.5)), LONG, P4),
    "s3-wt40": ("walls", "both, to the mid-line, 4 mm thick, fillet 4 mm (nearer the ridges of the Spencer half shell)",
                dict(CONTROL, **walls(height=0.5, t=4.0, rf=4.0)), LONG, P4),
    "s3-fwr30": ("walls", "the smooth twin of s3-w30: the control's neck on the rule's port 30 deg", dict(CONTROL, port_angle_deg=30.0), LONG, P4),
    "s3-w30": ("walls", "the walls of s3-w50 on the rule's port 30 deg", dict(CONTROL, **walls(height=0.5), port_angle_deg=30.0), LONG, P4),
})

# ---- stage "ref": the stance of the owner's reference of 2026-11-20 (ref_oot_blend/), with settings that exist.
# The reference at the size where it sounds A4 (x 0.75): window faces about 23 deg from straight down, the pipe is
# 55 mm long, runs 4 deg into the chamber against the chamber wall, and its mouth end stands at mid thickness.
LONG57 = {"voicing_rules.windway_length_mm": 57.0}
RTIP = dict(neck_floor_mm=8.6, neck_base_depth_mm=29.0)


def ref(port, pitch, raise_deg, **more):
    return dict(port_angle_deg=port, windway_pitch_deg=pitch, stub_pitch_deg=pitch + raise_deg, **RTIP, **more)


TRIALS.update({
    "s3-r20": ("ref", "port 20 deg, the rule's pipe angle (+8), pipe 45 mm, round tip", dict(port_angle_deg=20.0, **RTIP), LONG, BOTH),
    "s3-r20p": ("ref", "port 20 deg, pipe +4 deg and 57 mm long, round tip", ref(20.0, 4.0, 0.0), LONG57, BOTH),
    "s3-r20pn": ("ref", "the same, the neck's outside raised 8 deg over the pipe", ref(20.0, 4.0, 8.0), LONG57, BOTH),
    "s3-r15pn": ("ref", "port 15 deg, pipe +4 deg and 57 mm, neck raised 8 deg", ref(15.0, 4.0, 8.0), LONG57, P4),
    "s3-r10pn": ("ref", "port 10 deg, pipe +4 deg and 57 mm, neck raised 8 deg", ref(10.0, 4.0, 8.0), LONG57, P4),
    "s3-r25pn": ("ref", "port 25 deg, pipe +4 deg and 57 mm, neck raised 8 deg", ref(25.0, 4.0, 8.0), LONG57, P4),
})

# ---- stage W, second way: the ridge field (inner_walls.py): a thick thumb-face wall with pockets left in it.
def ridge(h=7.5, W=3.0, tail=False, **more):
    return dict(inner_ridge_height_mm=h, inner_ridge_width_mm=W, inner_ridge_tail=tail, **more)


TRIALS.update({
    "s3-k1": ("ridge", "ridge field 7.5 mm between the thumb holes, pockets rising over 3 mm", dict(CONTROL, **ridge()), LONG, BOTH),
    "s3-k2": ("ridge", "the same, running on to the tail (the Spencer's thick tail)", dict(CONTROL, **ridge(tail=True)), LONG, BOTH),
    "s3-k3": ("ridge", "ridge field 5 mm, to the tail", dict(CONTROL, **ridge(h=5.0, tail=True)), LONG, P4),
    "s3-k4": ("ridge", "ridge field 7.5 mm to the tail, pockets rising over 5 mm (gentler sides)", dict(CONTROL, **ridge(W=5.0, tail=True)), LONG, P4),
    "s3-k5": ("ridge", "ridge field 10 mm, to the tail", dict(CONTROL, **ridge(h=10.0, tail=True)), LONG, P4),
    "s3-k6": ("ridge", "ridge field 7.5 mm to the tail, allowed onto the outer skirt of the voicing's pocket (zone 10 mm half wide)",
              dict(CONTROL, **ridge(tail=True, inner_ridge_window_half_mm=10.0)), LONG, P4),
    "s3-k7": ("ridge", "ridge field 7.5 mm to the tail, and the slab wall on the left where the field has no room",
              dict(CONTROL, **ridge(tail=True), **walls("L", 0.25)), LONG, P4),
})

# ---- stage C: the blend between the neck and the body (blend_fillet.py), on the stance of the reference (s3-r20p)
REF = ref(20.0, 4.0, 0.0)
TRIALS.update({
    "s3-b8": ("blend", "the stance of s3-r20p, the neck blended into the body with an 8 mm ball", dict(REF, neck_blend_mm=8.0), LONG57, P4),
    "s3-b16": ("blend", "the same with a 16 mm ball", dict(REF, neck_blend_mm=16.0), LONG57, P4),
    "s3-b24": ("blend", "the same with a 24 mm ball", dict(REF, neck_blend_mm=24.0), LONG57, P4),
    "s3-ba": ("blend", "lopsided, as on the reference: a 24 mm ball toward the tail, 10 mm toward the bulb",
              dict(REF, neck_blend_mm=24.0, neck_blend_bulb_mm=10.0), LONG57, ALL),
    "s3-bw": ("blend", "a wider foot of the neck (50 x 32 mm) and a 16 mm ball",
              dict(REF, neck_base_width_mm=50.0, neck_base_depth_mm=32.0, neck_blend_mm=16.0), LONG57, P4),
    # ---- the candidates: the stance of the reference, the lopsided blend, and the inside either way
    "s3-cA": ("cand", "candidate A: stance of s3-r20p, lopsided blend, the two low slab walls the owner chose (s3-w25)",
              dict(REF, neck_blend_mm=24.0, neck_blend_bulb_mm=10.0, **walls(height=0.25)), LONG57, BOTH),
    "s3-cB": ("cand", "candidate B: the same outside, the ridge field 7.5 mm to the tail instead of the slab walls",
              dict(REF, neck_blend_mm=24.0, neck_blend_bulb_mm=10.0, **ridge(tail=True)), LONG57, BOTH),
    "s3-c0": ("cand", "the smooth twin of the candidates: the same outside, nothing inside",
              dict(REF, neck_blend_mm=24.0, neck_blend_bulb_mm=10.0), LONG57, P1),
})

# ---- the voicing shoulder (voicing_shoulder.py): extra volume of the body around the voicing, chamber and wall together.
# The owner approved port 20 deg on 2026-11-20; the stance and the lopsided blend are those of s3-ba.
BLEND = dict(neck_blend_mm=24.0, neck_blend_bulb_mm=10.0)


def shoulder(h, port=20.0, **more):
    return dict(ref(port, 4.0, 0.0), voicing_shoulder_mm=h, **BLEND, **more)


TRIALS.update({
    "s3-h6": ("shoulder", "shoulder 6 mm, port 20 deg", shoulder(6.0), LONG57, P4),
    "s3-h9": ("shoulder", "shoulder 9 mm, port 20 deg", shoulder(9.0), LONG57, BOTH),
    "s3-h9p25": ("shoulder", "shoulder 9 mm, port 25 deg", shoulder(9.0, 25.0), LONG57, ALL),
    "s3-h9p30": ("shoulder", "shoulder 9 mm, port 30 deg", shoulder(9.0, 30.0), LONG57, P4),
    "s3-h12p25": ("shoulder", "shoulder 12 mm, port 25 deg", shoulder(12.0, 25.0), LONG57, P4),
    "s3-h9n": ("shoulder", "shoulder 9 mm, port 25 deg, no blend (to tell the shoulder from the blend)",
               dict(ref(25.0, 4.0, 0.0), voicing_shoulder_mm=9.0), LONG57, BOTH),
    "s3-h5p25": ("shoulder", "shoulder 5 mm, port 25 deg", shoulder(5.0, 25.0), LONG57, P1),
    "s3-h7p25": ("shoulder", "shoulder 7 mm, port 25 deg", shoulder(7.0, 25.0), LONG57, P1),
    "s3-h9e": ("shoulder", "shoulder 9 mm as an egg (power 1), port 25 deg", shoulder(9.0, 25.0, voicing_shoulder_power=1.0), LONG57, P4),
    "s3-h9s": ("shoulder", "shoulder 9 mm, port 25 deg, pipe 47 mm (the neck starts further out, so it can be shorter)",
               shoulder(9.0, 25.0), {"voicing_rules.windway_length_mm": 47.0}, BOTH),
})


# ---- the owner's draft of 2026-11-24 (sculpt/OCA_sculpt_owner_draft_2026-11-24.blend): a slim straight cone on the plain
# body, 25.4 mm across at the body and 15.2 mm at the mouth end, level, the pipe diagonal inside it. tandem_neck.py turns
# and moves the outside of the neck; the pipe and the voicing hash stay those of s3-r20p.
HALF_WINDOW, INLET, COVER = 4.403, 3.0, 2.2


def cone(tip=15.2, root=25.4, tilt=0.0, yaw=0.0, off=0.0, across=None, port=20.0, **more):
    """A straight cone neck: round, `tip` mm at the mouth end (`across` mm wide there if given) and `root` mm at the body."""
    d = dict(port_angle_deg=port, windway_pitch_deg=4.0, stub_pitch_deg=4.0, neck_base_width_mm=root, neck_base_depth_mm=root,
             neck_width_exponent=1.0, neck_side_wall_mm=0.5 * (across or tip) - HALF_WINDOW, neck_floor_mm=tip - INLET - COVER)
    d.update({k: v for k, v in (("neck_tilt_deg", tilt), ("neck_yaw_deg", yaw), ("neck_offset_mm", off)) if v})
    d.update(more)
    return d


TRIALS.update({
    "s3-t0": ("tandem", "the draft's cone (25.4 mm at the body, 15.2 mm at the mouth end) along the pipe", cone(neck_tail_mm=4.0), LONG57, P4),
    "s3-t4": ("tandem", "the cone, its outside tilted 4 deg toward the thumb face", cone(tilt=4.0), LONG57, P4),
    "s3-t6": ("tandem", "the cone, tilted 6 deg", cone(tilt=6.0), LONG57, ALL),
    "s3-t10": ("tandem", "the cone tilted 10 deg as drawn; the mouth end must be 19.2 mm for it", cone(tip=19.2, tilt=10.0), LONG57, P4),
    "s3-t6b": ("tandem", "tilted 6 deg, an 8 mm ball in the crease", cone(tilt=6.0, neck_blend_mm=8.0), LONG57, P4),
    "s3-t6l": ("tandem", "tilted 6 deg, the lopsided blend of s3-ba (24 mm toward the tail, 10 mm toward the bulb)", cone(tilt=6.0, **BLEND), LONG57, P4),
    "s3-t6yt": ("tandem", "tilted 6 deg and turned 3 deg toward the tail (mouth end 20 mm across)", cone(tilt=6.0, yaw=3.0, across=20.0), LONG57, P4),
    "s3-t6yb": ("tandem", "tilted 6 deg and turned 3 deg toward the bulb (mouth end 20 mm across)", cone(tilt=6.0, yaw=-3.0, across=20.0), LONG57, P4),
    "s3-t6o": ("tandem", "tilted 6 deg, the outside moved 2.5 mm toward the tail (mouth end 19 mm across)", cone(tilt=6.0, off=2.5, across=19.0), LONG57, P4),
    "s3-t6h": ("tandem", "tilted 6 deg, the neck running on 8.5 mm beyond the labium as the draft's flat tube", cone(tilt=6.0, neck_tail_mm=8.5), LONG57, P4),
    "s3-t6s": ("tandem", "tilted 6 deg with a 5 mm voicing shoulder of the chamber, port 25 deg",
               cone(tilt=6.0, port=25.0, voicing_shoulder_mm=5.0), LONG57, P4),
})


# ---- the owner chose the cone tilted 6 deg with the slim tip (2026-11-24) and asked which approach works best at this
# voicing height, on the seed only, with a test of an uneven wall: thin on the deck, thick on the thumb face (uneven_wall.py).
T6 = cone(tilt=6.0)


def uneven(front, back, **more):
    return dict(T6, wall_front_less_mm=front, wall_back_more_mm=back, **more)


TRIALS.update({
    "s3-u0": ("uneven", "control: the cone tilted 6 deg, the even 4 mm wall, built by the shell-edit way (0.01 mm more on the back)", uneven(0.0, 0.01), LONG57, P4),
    "s3-u1": ("uneven", "wall 3 mm on the deck, 5 mm on the thumb face", uneven(1.0, 1.0), LONG57, P4),
    "s3-u2": ("uneven", "wall 2.5 mm on the deck, 6 mm on the thumb face", uneven(1.5, 2.0), LONG57, P4),
    "s3-u3": ("uneven", "wall 2 mm on the deck, 7 mm on the thumb face", uneven(2.0, 3.0), LONG57, P4),
    "s3-u6": ("uneven", "wall 3 mm on the deck, 6 mm on the thumb face", uneven(1.0, 2.0), LONG57, P4),
    "s3-u7": ("uneven", "wall 3 mm on the deck, 7 mm on the thumb face", uneven(1.0, 3.0), LONG57, P4),
    "s3-u2n": ("uneven", "wall 2.5 / 6 mm without the dish around the window (the first build)", uneven(1.5, 2.0, wall_back_no_dish=True), LONG57, P4),
    "s3-v0": ("uneven", "wall 3 / 5 mm, no dish: only the add-on's own window cut through the thicker wall", uneven(1.0, 1.0, wall_back_no_dish=True), LONG57, P4),
    "s3-v1": ("uneven", "wall 3 / 5 mm, the ramp run on as an oval scoop 22 x 17 mm from the window's upper edge", uneven(1.0, 1.0, wall_ramp_oval_mm=[22.0, 17.0]), LONG57, P4),
    "s3-v2": ("uneven", "wall 3 / 6 mm, the same oval scoop (2 mm deep)", uneven(1.0, 2.0, wall_ramp_oval_mm=[22.0, 17.0]), LONG57, P4),
    "s3-v3": ("uneven", "wall 3 / 5 mm, a longer oval scoop 28 x 18 mm", uneven(1.0, 1.0, wall_ramp_oval_mm=[28.0, 18.0]), LONG57, P4),
    # the owner, 2026-11-25: s3-v2 "is getting there however the scoop is giving really inconsistent results, aim for the mre
    # oval window of the first image" (the game render: an oval with a clear rim, long along the body). Wall 3 / 6 mm.
    "s3-w1": ("oval", "oval 22 mm along the jet x 17 mm, a level floor and a clear rim", uneven(1.0, 2.0, wall_ramp_oval_mm=dict(len=22.0, wid=17.0)), LONG57, P4),
    "s3-w2": ("oval", "oval long along the body: 15 mm along the jet x 26 mm, level floor, clear rim", uneven(1.0, 2.0, wall_ramp_oval_mm=dict(len=15.0, wid=26.0)), LONG57, P4),
    "s3-w3": ("oval", "the same 15 x 28 mm, its middle 4 mm toward the bulb (the window near its tail end)",
              uneven(1.0, 2.0, wall_ramp_oval_mm=dict(len=15.0, wid=28.0, shift=-4.0)), LONG57, P4),
    "s3-w4": ("oval", "an ellipsoid cut out of the shell: 18 mm along the jet x 30 mm along the body, 7 mm vertical half axis",
              uneven(1.0, 2.0, wall_back_no_dish=True, wall_ramp_ellipsoid_mm=dict(len=18.0, wid=30.0, deep=7.0)), LONG57, P4),
    "s3-w5": ("oval", "an ellipsoid 20 x 26 mm, 5 mm vertical half axis (flatter floor), 3 mm toward the bulb",
              uneven(1.0, 2.0, wall_back_no_dish=True, wall_ramp_ellipsoid_mm=dict(len=20.0, wid=26.0, deep=5.0, shift=-3.0)), LONG57, P4),
    "s3-w6": ("oval", "the oval of s3-w2 on the 3 / 5 mm wall", uneven(1.0, 1.0, wall_ramp_oval_mm=dict(len=15.0, wid=26.0)), LONG57, P4),
    # the owner, 2026-11-25: "none of them work the scoop leaves a non smoth surface, another aproach that comes to mind is the
    # window and the dish being separate, allowing to different windows with smothing applied". The dish as its own shape
    # (level floor, a rim 2.5 mm wide, the mesh split twice), with the rule's window and with a window that opens less.
    "s3-d1": ("dish", "separate dish 18 mm along the jet x 26 mm, level floor, rim 2.5 mm, from the window's upper edge; the rule's window",
              uneven(1.0, 2.0, wall_ramp_oval_mm=dict(len=18.0, wid=26.0, rim=2.5, splits=2)), LONG57, P4),
    "s3-d2": ("dish", "the same dish; a window that opens 0.6 mm to each side instead of 2.5 mm (another voicing hash)",
              uneven(1.0, 2.0, wall_ramp_oval_mm=dict(len=18.0, wid=26.0, rim=2.5, splits=2), cone_widen_mm=0.6), LONG57, P4),
    "s3-d3": ("dish", "the dish 21 x 26 mm begun 3 mm above the window's upper edge, so its floor is level round the whole window; the rule's window",
              uneven(1.0, 2.0, wall_ramp_oval_mm=dict(len=21.0, wid=26.0, rim=2.5, splits=2, start=-3.0)), LONG57, P4),
    "s3-d4": ("dish", "the dish of s3-d3 with the window that opens 0.6 mm (another voicing hash)",
              uneven(1.0, 2.0, wall_ramp_oval_mm=dict(len=21.0, wid=26.0, rim=2.5, splits=2, start=-3.0), cone_widen_mm=0.6), LONG57, P4),
    "s3-u4": ("uneven", "wall 4 mm on the deck, 6 mm on the thumb face (thick back only)", uneven(0.0, 2.0), LONG57, P4),
    "s3-u5": ("uneven", "wall 2.5 mm on the deck, 4 mm on the thumb face (thin deck only)", uneven(1.5, 0.0), LONG57, P4),
    "s3-u6s": ("uneven", "wall 3 / 6 mm with a 5 mm voicing shoulder of the chamber, port 25 deg",
               uneven(1.0, 2.0, port_angle_deg=25.0, voicing_shoulder_mm=5.0), LONG57, P4),
    "s3-u6w": ("uneven", "wall 3 / 6 mm with the two low slab walls inside (s3-w25)", uneven(1.0, 2.0, **walls(height=0.25)), LONG57, P4),
    "s3-t6w": ("uneven", "even wall, the cone tilted 6 deg, the two low slab walls inside", dict(T6, **walls(height=0.25)), LONG57, P4),
})


def trial_spec(pid: str, name: str):
    group, what, over, par, bodies = TRIALS[name]
    per_body = lambda v: isinstance(v, dict) and set(v) <= {"P0", "P1", "P2", "P3", "P4"}      # noqa: E731
    over = {k: (v[pid] if per_body(v) else v) for k, v in over.items() if not per_body(v) or pid in v}
    return what, over, dict(par), pid in bodies


lv.trial_spec = trial_spec
lv.TRIALS = {k: v[1:] for k, v in TRIALS.items()}

# ---- the inner walls hook into the build from outside (inner_walls.py says why), and every body of series 3 gets
#      pictures of its inside: the thumb-face half seen from the chamber, and two sections along the body.
inner_walls.install(body_mod)
blend_fillet.install(body_mod, ROOT / "addon_out" / "_blend_work")
voicing_shoulder.install()
tandem_neck.install()
uneven_wall.install()
CURRENT = {}
ROOM = ("s3-fwr",)                      # bodies whose room for a wall is measured (no wall in them)
_plain_pictures = lv.pictures


def pictures(body, tag):
    files, outline = _plain_pictures(body, tag)
    CURRENT["body"] = body
    V, F = body.solid
    o = np.asarray(body.voicing.frame[0], float)
    X, Y, Z = np.eye(3)
    S = body_mod.plain_skin(body.cavity, float(body.params["wall_mm"]))[0]
    z_mid = 0.5 * (S[:, 2].min() + S[:, 2].max())
    keep = (V[:, 2] < z_mid)[F].all(axis=1)                     # the thumb-face half, opened at the middle of the body
    used = np.unique(F[keep])
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    lv.render.VIEWS["_inside"] = (tuple(-Z), tuple(-Y))          # from the finger deck down into the half; the player at the top
    p = lv.render.render_views([(V[used], remap[F[keep]], lv.BODY_COLOR)], str(lv.IMG), prefix=tag, views=("_inside",), size_px=1000)[0]
    target = str(lv.IMG / f"{tag}_inside.png")
    os.replace(p, target)
    files["inside"] = target
    air = [(body.air_capped[0], body.air_capped[1], lv.AIR_RGB)]
    thumbs = {h.name: np.asarray(h.centre, float) for h in body.layout.holes if "thumb" in h.name}
    y_holes = float(np.mean([c[1] for c in thumbs.values()])) if thumbs else float(o[1])
    for key, y in (("alongwindow", float(o[1] - 0.5 * body.sizing.voicing.window_length_mm * body.voicing.frame[1][1])), ("alongthumbs", y_holes)):
        files[key] = lv.render.section_image(V, F, np.array([o[0], y, 0.0]), Y, X, Z, str(lv.IMG / f"{tag}_{key}.png"), mm_per_px=0.06,
                                             extent=(-45.0, 50.0, S[:, 2].min() - 6.0, S[:, 2].max() + 6.0), extra=air)[0]
    return files, outline


lv.pictures = pictures


def merge() -> dict:
    data = {}
    for f in sorted(lv.TRIAL_DIR.glob("*.json")):
        row = json.loads(f.read_text(encoding="utf-8"))
        data[f"{row['preset']}:{row['trial']}"] = row
    MERGED.write_text(json.dumps(data, indent=1), encoding="utf-8")
    return data


def main(argv):
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else None
    group = argv[argv.index("--group") + 1] if "--group" in argv else None
    lv.IMG.mkdir(parents=True, exist_ok=True)
    lv.TRIAL_DIR.mkdir(parents=True, exist_ok=True)
    P = kernel_bridge.load_params()
    for pid in ("P4", "P1", "P0", "P2", "P3"):
        for name, spec in TRIALS.items():
            key = f"{pid}:{name}"
            if (only and key not in only and pid not in only) or (group and spec[0] != group) or not trial_spec(pid, name)[3]:
                continue
            try:
                row = lv.one(pid, name, P)
                row["group"] = spec[0]
                body = CURRENT.pop("body", None)
                if body is not None:
                    row["blend"] = dict(blend_fillet.LAST)
                    row["shoulder"] = dict(voicing_shoulder.LAST) if body.cavity.preset.get("voicing_shoulder_mm") is not None else {}
                    row["inner_walls"] = inner_walls.measure(body)
                    row["uneven"] = dict(uneven_wall.LAST)
                    row["shell_edit"] = body.info.get("shell_edit")
                    row["holes"] = {h.name: dict(d_mm=float(h.d_mm), wall_mm=float(h.wall_mm), tube_mm=float(h.tube_mm)) for h in body.layout.holes}
                    if name in ROOM:
                        row["room"] = inner_walls.room(body)
            except Exception as exc:                 # noqa: BLE001 - one trial must not hide the others
                import traceback
                traceback.print_exc()
                what, over, par, _ = trial_spec(pid, name)
                row = dict(trial=name, preset=pid, group=spec[0], what=what, overrides=over, param_overrides=par, build_failed=str(exc))
                print(f"[{key}] BUILD FAILED: {exc}", flush=True)
            (lv.TRIAL_DIR / f"{pid}_{name}.json").write_text(json.dumps(row, indent=1, default=body_mod._json_default), encoding="utf-8")
            merge()
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(argv)
    sys.stdout.flush()
