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

import inner_walls  # noqa: E402
import low_voicing_trials as lv  # noqa: E402
from ocarina_addon import body as body_mod, kernel_bridge  # noqa: E402

lv.IMG = HERE / "images_s3"
lv.TRIAL_DIR = HERE / "trials_s3"
MERGED = HERE / "series3_trials.json"

LONG = {"voicing_rules.windway_length_mm": 45.0}
P4, P1, BOTH = ("P4",), ("P1",), ("P4", "P1")
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
                    row["inner_walls"] = inner_walls.measure(body)
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
