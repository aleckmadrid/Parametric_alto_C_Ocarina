"""Second round of neck trials (2026-11-18): the top of the window cut, and a neck thrown back.

Run it with Blender 5.1 in background mode, from the repository root:

    blender -b --factory-startup --python Analizes_ocarinas/Neck_volume/throwback_trials.py -- [--only P1:tb-l,P4:sq]

Two bodies, each with five voicings: P1 (the teardrop, the nearest preset to the two bulb references) and P4 (the
seed), both at 80 cm3. Every trial is built as tools/geometry_check_variant.py builds a variant, and every check
runs on the STL read back from disk. It writes

    addon_checks/<P1|P4>-80-<trial>.md / .json and addon_renders/<...>/    the usual report and pictures
    Analizes_ocarinas/Neck_volume/images/<P1|P4>_<trial>_*.png             the pictures of the sheets
    Analizes_ocarinas/Neck_volume/throwback_trials.json                    the numbers and the section outlines

What changes from trial to trial
    shelf_angle_deg     40 (the rules) or 0: the wall over the windway exit is then cut square, as on both new
                        references, the NBN and the ECAN3 Eclipse; none of them has a leaning shelf
    port_angle_deg      45 (every preset) or 30: where the voicing sits around the body, from the bottom toward the
                        player. At 30 the window faces more nearly down and the neck points more nearly level
    windway_pitch_deg   +5 (the rules) or +8: the jet enters the chamber a little more steeply. 8 is the most that
                        leaves a roof of 1.7 mm over the exit under a 4 mm wall
    the neck            follows the pipe (trial nk-a of the first round), or lies LEVEL with the body: a straight
                        flank that points at the player, with the pipe lowered inside it
"""
from __future__ import annotations

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

from ocarina_addon import api, body as body_mod, cavity_math as cm, checks_geo, kernel_bridge, presets as presets_mod, render, report  # noqa: E402

IMG = HERE / "images"
V0 = 80.0
PRESETS = ("P1", "P4")
BODY_COLOR = (0.78, 0.74, 0.62, 1.0)
AIR_RGB = (0.35, 0.62, 1.0)
PORT_BACK, PITCH_BACK = 30.0, 8.0
# Rule version 2 (2026-11-18), named in full: these trials were built against it, and since rule version 3
# (2026-11-19) a value that a trial does not name would come from the new rule.
RULES_V2 = dict(stub_style="neck", stub_pitch_deg=15.0, windway_pitch_deg=5.0, shelf_angle_deg=40.0, port_angle_deg=45.0)


def face_above_level(pid: str, port_angle: float) -> float:
    """How far the window face rises above the body's level toward the player (= how far the window's normal is
    turned from straight down toward the player), in degrees."""
    cav = cm.Cavity.from_preset(dict(presets_mod.get_preset(pid), port_angle_deg=port_angle))
    _, _, z = cav.port_frame()
    return math.degrees(math.atan2(-z[1], -z[2]))


def trials(pid: str) -> dict:
    level = round(face_above_level(pid, PORT_BACK), 2)                # a neck at this stance is level with the body
    thin = dict(neck_cover_mm=2.2, neck_cover_exit_mm=1.6)
    back = dict(thin, port_angle_deg=PORT_BACK, windway_pitch_deg=PITCH_BACK, stub_pitch_deg=PITCH_BACK, shelf_angle_deg=0.0)   # tb-f
    # the sections of the third round: the upper half of each section is only as high as leaves 1.3 mm of plastic
    # over the pipe's corners, so the neck can grow deep on the deck side without thinning the roof
    cone = dict(back, neck_depth_exponent=1.0, neck_corner_cover_mm=1.3)
    return {
        "now": ("rule version 2 (2026-11-18): neck 15° off the window face, pipe +5°, shelf 40°", {}),
        "nk-a": ("the neck follows the pipe (first round), shelf 40°", dict(neck_cover_mm=2.2, stub_pitch_deg=5.0)),
        "sq": ("as nk-a, the roof over the exit cut square (no shelf)", dict(neck_cover_mm=2.2, stub_pitch_deg=5.0, shelf_angle_deg=0.0)),
        "tb-f": (f"thrown back: port {PORT_BACK:g}°, pipe +{PITCH_BACK:g}°, the neck follows the pipe, square roof",
                 dict(thin, port_angle_deg=PORT_BACK, windway_pitch_deg=PITCH_BACK, stub_pitch_deg=PITCH_BACK, shelf_angle_deg=0.0)),
        "tb-l": (f"thrown back: port {PORT_BACK:g}°, pipe +{PITCH_BACK:g}°, the neck level with the body, square roof",
                 dict(thin, port_angle_deg=PORT_BACK, windway_pitch_deg=PITCH_BACK, stub_pitch_deg=level, shelf_angle_deg=0.0)),
        # Third round (2026-11-19): the owner chose tb-f with the square roof, and asked for the neck's volume to be
        # adjusted so that, seen along the body, it is closer to the section of the "Deluxe" model: the flank on the
        # deck side straight and fuller, not hollow as a bell. The pipe and the cut are those of tb-f.
        "tb-d1": ("tb-f with a straight flank on the deck side (the owner's sketch): depth grows evenly to 24.5 mm at the body",
                  dict(cone, neck_base_depth_mm=24.5)),
        "tb-d2": ("tb-f with the Deluxe's proportions: a cone, 27.5 mm deep at the body, 4 mm of plastic on the deck side of the pipe at the mouth end",
                  dict(cone, neck_width_exponent=1.0, neck_base_depth_mm=27.5, neck_floor_mm=4.0)),
    }


def crop(V, F, centre, radius):
    sel = np.linalg.norm(V - centre, axis=1) < radius
    keep = sel[F].all(axis=1)
    used = np.unique(F[keep])
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    return V[used], remap[F[keep]]


def pictures(body, tag):
    V, F = body.solid
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    L, Lw, wall = v.window_length_mm, v.windway_length_mm, v.wall_at_window_mm
    cV, cF = crop(V, F, o - fx * (L + 0.45 * Lw) + fz * 2.0, 46.0)
    X, Y, Z = np.eye(3)
    # name: (camera looks along, up, the part around the neck or the whole body)
    views = {"_outside": (tuple(-0.75 * fz + 0.50 * fx + 0.42 * fy), tuple(fz), True),    # three-quarter, from the mouth end, onto the window
             "_window": (tuple(-0.62 * fz - 0.70 * fx + 0.28 * fy), tuple(fz), True),     # from beyond the labium, back toward the neck
             "_end": (tuple(-X), tuple(Z), False),                                         # along the body: the player on the left, the deck up
             "_under": (tuple(0.62 * Y + 0.78 * Z + 0.10 * X), tuple(-0.78 * Y + 0.62 * Z), False)}   # from below and behind
    files = {}
    for key, (look, up, part) in views.items():
        render.VIEWS[key] = (look, up)
        p = render.render_views([(cV, cF, BODY_COLOR) if part else (V, F, BODY_COLOR)], str(IMG), prefix=tag, views=(key,), size_px=820)[0]
        target = str(IMG / f"{tag}{key}.png")
        os.replace(p, target)
        files[key[1:]] = target
    air = [(body.air_capped[0], body.air_capped[1], AIR_RGB)]
    # the body's own cross-section through the lip: the player on the left, the deck up
    files["bodysection"] = render.section_image(V, F, o, X, Y, Z, str(IMG / f"{tag}_bodysection.png"), mm_per_px=0.06,
                                                extent=(-58.0, 38.0, -30.0, 46.0), extra=air, marks=[((0.0, 0.0), (1.0, 0.1, 0.1))])[0]
    # close section through the pipe in the frame of the window (the jet runs left to right, outside is up)
    files["section"] = render.section_image(V, F, o, fy, fx, fz, str(IMG / f"{tag}_section.png"), mm_per_px=0.04,
                                            extent=(-L - 16.0, 14.0, -7.0, wall + 9.0), extra=air, marks=[((0.0, 0.0), (1.0, 0.1, 0.1))])[0]
    S = render.section_2d(V, F, o, X, Y, Z)
    keep = (np.abs(S[..., 0]).max(axis=1) < 70) & (np.abs(S[..., 1]).max(axis=1) < 60)
    return files, np.round(S[keep], 3).tolist()


def one(pid, name, P):
    what, over = trials(pid)[name]
    over = dict(RULES_V2, **over)
    t0 = time.time()
    bid = f"{body_mod.default_body_id(pid, V0)}-{name if name.startswith(('nk-', 'tb-')) else 'tb-' + name}"   # never the files of the stage body
    preset = dict(presets_mod.get_preset(pid), **over)
    body = api.build_checked_body(preset, V0, str(ROOT / "addon_out" / bid), params=P, renders=True, root=ROOT, body_id=bid)
    shown = " ".join(f"{k}={v:g}" if isinstance(v, float) else f"{k}={v}" for k, v in over.items())
    written = (f"Written by `Analizes_ocarinas/Neck_volume/throwback_trials.py` (trial {pid}:{name}): preset {pid} with {shown}." if over else
               f"Written by `Analizes_ocarinas/Neck_volume/throwback_trials.py` (trial {pid}:{name}): the body of the rules.")
    report.write_body_report(body, ROOT / "addon_checks", time.time() - t0, written, json_default=body_mod._json_default)
    files, outline = pictures(body, f"{pid}_{name}")
    bad = checks_geo.unexpected_failures(body)
    m, v = body.measurements, body.sizing.voicing
    g = m["voicing"]
    C = {c["name"]: c for c in body.checks}
    cut = {b["name"]: -b["delta_mm3"] for b in body.booleans}
    face = face_above_level(pid, float(over.get("port_angle_deg", presets_mod.get_preset(pid)["port_angle_deg"])))
    nk = g.get("neck") or {}
    top = v.stub_pitch_deg if abs(v.stub_pitch_deg - v.windway_pitch_deg) > 1e-9 or nk.get("cover_mm") is None else v.windway_pitch_deg + 1.7
    row = dict(trial=name, preset=pid, body_id=bid, what=what, overrides=over, voicing_hash=v.version_hash,
               unexpected=[c["name"] for c in bad], unexpected_messages={c["name"]: c["message"] for c in bad},
               warnings=[c["name"] for c in checks_geo.warnings(body)], neck=nk,
               window_faces_from_down_deg=face, pipe_above_level_deg=face - v.windway_pitch_deg, neck_top_above_level_deg=face - top,
               neck_middle_above_level_deg=face - nk.get("middle_line_deg_against_body", float("nan")),
               shelf_angle_deg=v.shelf_angle_deg, flare_steepest_deg=g.get("flare_steepest_deg"), above_outer_face_mm=g.get("max_height_above_outer_face_mm"),
               window_area_mm2=g.get("window_area_mm2"), labium_angle_deg=g.get("labium_angle_deg"), labium_edge_mm=g.get("labium_edge_thickness_mm"),
               windway_roof_mm=g.get("windway_roof_thickness_mm"), windway_floor_lip_mm=g.get("windway_floor_lip_mm"),
               capped_air_cm3=m["volume"]["capped_air_measured_cm3"], plastic_cm3=m["volume"]["body_plastic_cm3"],
               window_cut_removes_mm3=cut.get("window throat + labium ramp"),
               hole_to_voicing=C.get("hole_to_voicing", {}).get("message"), wall_thinnest=C.get("wall_thickness", {}).get("message"),
               files={k: pathlib.Path(p).name for k, p in files.items()}, outline_body=outline, seconds=round(time.time() - t0, 1))
    print(f"[{bid}] {'OK' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(row['unexpected'])}; {len(row['warnings'])} warnings; "
          f"{row['seconds']} s", flush=True)
    return row


def main(argv):
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else None
    IMG.mkdir(parents=True, exist_ok=True)
    P = kernel_bridge.load_params()
    path = HERE / "throwback_trials.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for pid in PRESETS:
        for name in trials(pid):
            key = f"{pid}:{name}"
            if only and key not in only:
                continue
            try:
                data[key] = one(pid, name, P)
            except Exception as exc:                 # noqa: BLE001 - one trial must not hide the others
                import traceback
                traceback.print_exc()
                data[key] = dict(trial=name, preset=pid, what=trials(pid)[name][0], overrides=trials(pid)[name][1], build_failed=str(exc))
                print(f"[{key}] BUILD FAILED: {exc}", flush=True)
            path.write_text(json.dumps(data, indent=1, default=body_mod._json_default), encoding="utf-8")
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(argv)
    sys.stdout.flush()
