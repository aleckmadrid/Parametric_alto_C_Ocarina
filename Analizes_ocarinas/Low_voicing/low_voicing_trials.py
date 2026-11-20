"""Low-voicing trials (2026-11-19): the voicing placed lower in the body, on the thumb face.

Run it with Blender 5.1 in background mode, from the root of the checkout:

    blender -b --factory-startup --python Analizes_ocarinas/Low_voicing/low_voicing_trials.py -- [--only P4:lv-10,P1]

The owner asked (2026-11-19) to try the voicing "lower in the body like shown on the back/thumb face of the Spencer
and Songbird". On both ceramic instruments the window lies ON the thumb face, well inside the outline (Spencer: 16 to
20 mm in from the player-side edge of a 57 mm body), and the mouthpiece leaves the edge of the body in line with it.
The add-on puts the voicing port 30 deg around the section from the bottom toward the player (45 deg until
2026-11-19), so the window is on the lower player-side quadrant and the neck stands on that quadrant.

What changes from trial to trial
    port_angle_deg      30 (the rule), 20, 10, 0: where the voicing sits around the body, from the bottom toward the
                        player. 0 puts the middle of the window on the bottom line, between the two thumb holes.
    everything else     the rule of version 3: cone neck, pipe +8 deg into the chamber, roof cut square.
Variants on the seed are named in TRIALS below (a slimmer foot of the neck, a longer pipe).

Every trial is built as tools/geometry_check_variant.py builds a variant, and every check runs on the STL read back
from disk. It writes

    addon_checks/<P1|P4>-80-<trial>.md / .json and addon_renders/<...>/    the usual report and pictures
    Analizes_ocarinas/Low_voicing/images/<P1|P4>_<trial>_*.png             the pictures of the sheets
    Analizes_ocarinas/Low_voicing/trials/<P>_<trial>.json                  the numbers and the section outline of one trial
    Analizes_ocarinas/Low_voicing/low_voicing_trials.json                  all of them, merged
"""
from __future__ import annotations

import copy
import json
import math
import os
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocarina_addon import api, body as body_mod, checks_geo, kernel_bridge, meshutil, presets as presets_mod, render, report  # noqa: E402

IMG = HERE / "images"
TRIAL_DIR = HERE / "trials"
V0 = 80.0
PRESETS = ("P4", "P1")
BODY_COLOR = (0.78, 0.74, 0.62, 1.0)
AIR_RGB = (0.35, 0.62, 1.0)
DARK_COLOR = (0.10, 0.10, 0.12, 1.0)

# The foot of the neck where it meets the body, for the trials named ...f. The seed: 29 mm, which is the proportion of
# the Spencer and the Songbird Alto C (0.21 of the body length, docs/07 section 3.3; the seed's own value is 32 mm,
# found for port 30 on 2026-11-19). The teardrop: 34 mm (the rule gives it 4.8 x the window width, 42 mm).
FOOT_MM = {"P4": 29.0, "P1": 34.0}
FOOT = dict(neck_foot_width_mm="per body")
# A longer pipe (the owner parked "a neck longer than the pipe" for later experiments; it is here because a window that
# lies further inside the outline leaves less mouthpiece outside it). Heuer: 1 to 3 in; the references: 30 to 40 mm.
LONG = {"voicing_rules.windway_length_mm": 45.0}

# name: (what it is, preset overrides, parameter overrides as {"table.key": value}, the bodies it is built on)
TRIALS = {
    "lv-30": ("the rule: port 30 deg (the body of rule version 3)", dict(port_angle_deg=30.0), {}, PRESETS),
    "lv-20": ("port 20 deg", dict(port_angle_deg=20.0), {}, PRESETS),
    "lv-10": ("port 10 deg", dict(port_angle_deg=10.0), {}, PRESETS),
    "lv-0": ("port 0 deg: the window on the bottom line", dict(port_angle_deg=0.0), {}, PRESETS),
    "lv-20f": ("port 20 deg, a slimmer foot of the neck", dict(port_angle_deg=20.0, **FOOT), {}, PRESETS),
    "lv-10f": ("port 10 deg, a slimmer foot of the neck", dict(port_angle_deg=10.0, **FOOT), {}, PRESETS),
    "lv-0f": ("port 0 deg, a slimmer foot of the neck", dict(port_angle_deg=0.0, **FOOT), {}, PRESETS),
    "lv-20fw": ("port 20 deg, slimmer foot, pipe 45 mm long", dict(port_angle_deg=20.0, **FOOT), LONG, ("P4",)),
    "lv-10fw": ("port 10 deg, slimmer foot, pipe 45 mm long", dict(port_angle_deg=10.0, **FOOT), LONG, ("P4",)),
    # Series 2 (handover of 2026-11-19, section 5), after the owner's four Spencer pictures: a finer bracket around
    # 10 deg, and the three differences of look the pictures show (mouthpiece length, the dish, a fat round foot).
    "lv-15f": ("port 15 deg, slimmer foot", dict(port_angle_deg=15.0, **FOOT), {}, ("P4",)),
    "lv-5f": ("port 5 deg, slimmer foot", dict(port_angle_deg=5.0, **FOOT), {}, ("P4",)),
    "lv-5fw": ("port 5 deg, slimmer foot, pipe 45 mm long", dict(port_angle_deg=5.0, **FOOT), LONG, ("P4",)),
    # cone_widen_mm is the record's cut_widen_mm: it is hashed (a new voicing). It widens the dish on every side.
    "lv-10fd": ("port 10 deg, slimmer foot, the dish 8 mm beyond the window",
                dict(port_angle_deg=10.0, cone_widen_mm=8.0, **FOOT), {}, ("P4",)),
    # neck_base_depth_mm is not hashed (outside only); the rule gives 2.78 x the window width, 24.5 mm here.
    "lv-10fn": ("port 10 deg, slimmer foot, the neck 29 mm deep at the body",
                dict(port_angle_deg=10.0, neck_base_depth_mm=29.0, **FOOT), {}, ("P4",)),
    "lv-10fwdn": ("port 10 deg, slimmer foot, pipe 45 mm, dish 8 mm, neck 29 mm deep",
                  dict(port_angle_deg=10.0, cone_widen_mm=8.0, neck_base_depth_mm=29.0, **FOOT), LONG, PRESETS),
    # Added in the second session of series 2: the Spencer's mouthpiece tip is round (tray picture), ours is 13.8 x 7.6 mm.
    # neck_floor_mm (not hashed) is the plastic on the body side of the pipe at the mouth end (rule 2.4 mm); 8.6 mm makes
    # the tip as deep as it is wide. The pipe does not move: only the outside of the neck grows toward the body.
    "lv-10fwdnr": ("port 10 deg, slimmer foot, pipe 45 mm, dish 8 mm, neck 29 mm deep, round mouth end",
                   dict(port_angle_deg=10.0, cone_widen_mm=8.0, neck_base_depth_mm=29.0, neck_floor_mm=8.6, **FOOT), LONG, PRESETS),
}


def trial_spec(pid: str, name: str):
    what, over, par, bodies = TRIALS[name]
    over = dict(over)
    if "neck_foot_width_mm" in over:
        over["neck_foot_width_mm"] = FOOT_MM[pid]
    return what, over, dict(par), pid in bodies


def params_with(P: dict, par: dict) -> dict:
    if not par:
        return P
    Q = copy.deepcopy(P)
    for key, value in par.items():
        table, field = key.split(".")
        Q[table][field] = value
    return Q


def crop(V, F, centre, radius):
    sel = np.linalg.norm(V - centre, axis=1) < radius
    keep = sel[F].all(axis=1)
    used = np.unique(F[keep])
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    return V[used], remap[F[keep]]


def geometry_numbers(body) -> dict:
    """Where the voicing and the mouthpiece lie against the body, in the frame of the body (X along the body, +Y away
    from the player, +Z the finger deck). The body's outline is that of the plain skin (the chamber moved out by the
    wall), so the neck does not count as body."""
    V, _ = body.solid
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    do, dx, dy, dz = (np.asarray(a, float) for a in vs.windway_frame())
    L, Lw, wall = v.window_length_mm, v.windway_length_mm, v.wall_at_window_mm
    zc = float(vs.info["windway_centre_z_mm"])
    S = body_mod.plain_skin(body.cavity, float(body.params["wall_mm"]))[0]
    win = o - 0.5 * L * fx + wall * fz                       # middle of the window at its outer face
    lip = o + wall * fz
    exit_ = o - L * fx + wall * fz
    band = S[np.abs(S[:, 0] - win[0]) < 1.2]                 # the body's own section at the station of the window
    edge_y, far_y, bottom_z, top_z = band[:, 1].min(), band[:, 1].max(), band[:, 2].min(), band[:, 2].max()
    mouth = do - (L + Lw) * dx + zc * dz                     # middle of the mouth end of the pipe
    back = -dx                                               # from the exit toward the mouth end
    math_cav = body.cavity.math
    # Heuer's "drop" and "body too flat" (docs/01 section 5.4): the free air under the window, along its normal, from
    # the lip and from the middle of the window to the chamber wall opposite; and how far the chamber wall has fallen
    # away from the window's inner plane at the windway exit (the height of the upright wall under the exit).
    tree = meshutil.bvh(body.cavity.V, body.cavity.F)

    def depth(xw):
        hits = meshutil.ray_hits(tree, o + fx * (xw - L) - fz * 0.5, -fz, 120.0)
        return float(hits[-1][0] + 0.5) if hits else float("nan")

    def wall_below_inner_plane(xw):
        hits = meshutil.ray_hits(tree, o + fx * (xw - L) + fz * 20.0, -fz, 80.0, limit=1)
        return float(hits[0][0] - 20.0) if hits else float("nan")

    out = dict(
        free_depth_under_lip_mm=depth(L), free_depth_under_window_middle_mm=depth(0.5 * L),
        drop_height_at_exit_mm=wall_below_inner_plane(0.0),
        body_width_at_window_mm=float(far_y - edge_y), body_thickness_at_window_mm=float(top_z - bottom_z),
        window_in_from_player_edge_mm=float(win[1] - edge_y), window_in_share_of_width=float((win[1] - edge_y) / (far_y - edge_y)),
        exit_in_from_player_edge_mm=float(exit_[1] - edge_y), lip_in_from_player_edge_mm=float(lip[1] - edge_y),
        window_above_bottom_line_mm=float(win[2] - bottom_z),
        window_faces_from_down_deg=float(math.degrees(math.atan2(-fz[1], -fz[2]))),
        pipe_above_level_deg=float(math.degrees(math.atan2(back[2], math.hypot(back[0], back[1])))),
        mouth_end_beyond_player_edge_mm=float(edge_y - mouth[1]),
        mouth_end_below_mid_plane_mm=float(0.5 * (bottom_z + top_z) - mouth[2]),
        mouth_end_below_bottom_line_mm=float(bottom_z - mouth[2]),
        body_hangs_below_plain_skin_mm=float(S[:, 2].min() - V[:, 2].min()),
        body_reaches_beyond_player_edge_mm=float(S[:, 1].min() - V[:, 1].min()),
        chamber_radius_along_jet_mm=float(math_cav.curvature_radius_along(math_cav.port_theta, math_cav.port_phi, tuple(fx))),
        chamber_radius_across_jet_mm=float(math_cav.curvature_radius_along(math_cav.port_theta, math_cav.port_phi, tuple(fy))),
        mouth_xyz=[float(c) for c in mouth], window_xyz=[float(c) for c in win])
    return out


def pictures(body, tag):
    V, F = body.solid
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    L, Lw, wall = v.window_length_mm, v.windway_length_mm, v.wall_at_window_mm
    cV, cF = crop(V, F, o - fx * (L + 0.45 * Lw) + fz * 2.0, 46.0)
    X, Y, Z = np.eye(3)
    # name: (camera looks along, up, the part around the neck or the whole body)
    views = {"_thumbface": (tuple(Z), tuple(-Y), False),                                   # straight at the thumb face; the player is at the top of the picture
             "_end": (tuple(-X), tuple(Z), False),                                         # along the body: the player on the left, the deck up
             "_under": (tuple(0.62 * Y + 0.78 * Z + 0.10 * X), tuple(-0.78 * Y + 0.62 * Z), False),   # from below, from the player's side
             "_back34": (tuple(-0.55 * Y + 0.70 * Z - 0.45 * X), tuple(0.55 * Y + 0.70 * Z), False),  # as the two ceramic thumb-face photos: from below and beyond, tail toward the camera
             "_player": (tuple(Y), tuple(Z), False),                                       # from the player
             "_window": (tuple(-0.62 * fz - 0.70 * fx + 0.28 * fy), tuple(fz), True)}      # the window, from beyond the labium, back toward the neck
    files = {}
    # the chamber, dark, inside the body: a hole or the window then reads as an opening and not as a raised disc
    dark = (np.asarray(body.cavity.V, float), np.asarray(body.cavity.F), DARK_COLOR)
    for key, (look, up, part) in views.items():
        render.VIEWS[key] = (look, up)
        p = render.render_views([(cV, cF, BODY_COLOR) if part else (V, F, BODY_COLOR), dark], str(IMG), prefix=tag, views=(key,), size_px=820)[0]
        target = str(IMG / f"{tag}{key}.png")
        os.replace(p, target)
        files[key[1:]] = target
    air = [(body.air_capped[0], body.air_capped[1], AIR_RGB)]
    # the body's own cross-section through the lip: the player on the left, the deck up
    files["bodysection"] = render.section_image(V, F, o, X, Y, Z, str(IMG / f"{tag}_bodysection.png"), mm_per_px=0.06,
                                                extent=(-62.0, 44.0, -34.0, 44.0), extra=air, marks=[((0.0, 0.0), (1.0, 0.1, 0.1))])[0]
    # close section through the pipe in the frame of the window (the jet runs left to right, outside is up)
    files["section"] = render.section_image(V, F, o, fy, fx, fz, str(IMG / f"{tag}_section.png"), mm_per_px=0.04,
                                            extent=(-L - 16.0, 14.0, -7.0, wall + 9.0), extra=air, marks=[((0.0, 0.0), (1.0, 0.1, 0.1))])[0]
    S = render.section_2d(V, F, o, X, Y, Z)
    keep = (np.abs(S[..., 0]).max(axis=1) < 80) & (np.abs(S[..., 1]).max(axis=1) < 60)
    return files, np.round(S[keep], 3).tolist()


def one(pid, name, P0):
    what, over, par, _ = trial_spec(pid, name)
    t0 = time.time()
    bid = f"{body_mod.default_body_id(pid, V0)}-{name}"
    P = params_with(P0, par)
    preset = dict(presets_mod.get_preset(pid), **over)
    body = api.build_checked_body(preset, V0, str(ROOT / "addon_out" / bid), params=P, renders=True, root=ROOT, body_id=bid)
    shown = " ".join(f"{k}={v:g}" if isinstance(v, (int, float)) else f"{k}={v}" for k, v in {**over, **par}.items())
    report.write_body_report(body, ROOT / "addon_checks", time.time() - t0,
                             f"Written by `Analizes_ocarinas/Low_voicing/low_voicing_trials.py` (trial {pid}:{name}): preset {pid} with {shown}.",
                             json_default=body_mod._json_default)
    files, outline = pictures(body, f"{pid}_{name}")
    bad = checks_geo.unexpected_failures(body)
    m, v = body.measurements, body.sizing.voicing
    g = m["voicing"]
    C = {c["name"]: c for c in body.checks}
    cut = {b["name"]: -b["delta_mm3"] for b in body.booleans}
    hv = m.get("hole_to_voicing", {})
    row = dict(trial=name, preset=pid, body_id=bid, what=what, overrides=over, param_overrides=par, voicing_hash=v.version_hash,
               unexpected=[c["name"] for c in bad], unexpected_messages={c["name"]: c["message"] for c in bad},
               expected=[c["name"] for c in checks_geo.expected_failures(body)],
               warnings=[c["name"] for c in checks_geo.warnings(body)],
               warning_messages={c["name"]: c["message"] for c in checks_geo.warnings(body)},
               checks={c["name"]: dict(status=c["status"], message=c["message"]) for c in body.checks},
               neck=g.get("neck") or {}, geometry=geometry_numbers(body),
               thumbs={k: hv.get(k) for k in ("L_thumb", "R_thumb")},
               flare_steepest_deg=g.get("flare_steepest_deg"), above_outer_face_mm=g.get("max_height_above_outer_face_mm"),
               window_area_mm2=g.get("window_area_mm2"), labium_angle_deg=g.get("labium_angle_deg"), labium_edge_mm=g.get("labium_edge_thickness_mm"),
               windway_roof_mm=g.get("windway_roof_thickness_mm"),
               capped_air_cm3=m["volume"]["capped_air_measured_cm3"], plastic_cm3=m["volume"]["body_plastic_cm3"],
               pocket_cm3=float(body.pocket_cm3), cavity_mode=m.get("cavity_mode"), keepout_inside=m.get("keepout_inside"),
               pocket_blend=body.voicing.info.get("pocket_blend"),
               window_cut_removes_mm3=cut.get("window throat + labium ramp"),
               windway_length_mm=v.windway_length_mm,
               files={k: pathlib.Path(p).name for k, p in files.items()}, outline_body=outline, seconds=round(time.time() - t0, 1))
    print(f"[{bid}] {'OK' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(row['unexpected'])}; {len(row['warnings'])} warnings; "
          f"{row['seconds']} s", flush=True)
    return row


def merge() -> dict:
    """low_voicing_trials.json from the files of the single trials (two runs may build at the same time)."""
    data = {}
    for f in sorted(TRIAL_DIR.glob("*.json")):
        row = json.loads(f.read_text(encoding="utf-8"))
        data[f"{row['preset']}:{row['trial']}"] = row
    (HERE / "low_voicing_trials.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
    return data


def main(argv):
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else None
    IMG.mkdir(parents=True, exist_ok=True)
    TRIAL_DIR.mkdir(parents=True, exist_ok=True)
    P = kernel_bridge.load_params()
    for pid in PRESETS:
        for name in TRIALS:
            key = f"{pid}:{name}"
            if (only and key not in only and pid not in only) or not trial_spec(pid, name)[3]:
                continue
            try:
                row = one(pid, name, P)
            except Exception as exc:                 # noqa: BLE001 - one trial must not hide the others
                import traceback
                traceback.print_exc()
                what, over, par, _ = trial_spec(pid, name)
                row = dict(trial=name, preset=pid, what=what, overrides=over, param_overrides=par, build_failed=str(exc))
                print(f"[{key}] BUILD FAILED: {exc}", flush=True)
            (TRIAL_DIR / f"{pid}_{name}.json").write_text(json.dumps(row, indent=1, default=body_mod._json_default), encoding="utf-8")
            merge()
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(argv)
    sys.stdout.flush()
