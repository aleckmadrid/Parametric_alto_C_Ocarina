"""Neck volume trials (2026-11-18): the same body with the neck shaped in several ways.

Run it with Blender 5.1 in background mode, from the repository root:

    blender -b --factory-startup --python Analizes_ocarinas/Neck_volume/neck_trials.py -- [--only nk-a,nk-p10]

Every trial is the seed body P4 at 80 cm3 with preset values overridden, as tools/geometry_check_variant.py does it:
the body is built, its STL is read back from disk and every check runs on that file. It writes

    addon_checks/P4-80-<trial>.md / .json     the usual report
    addon_renders/P4-80-<trial>/              the usual pictures
    Analizes_ocarinas/Neck_volume/images/<trial>_outside.png, _side.png, _mouth.png, _section.png
    Analizes_ocarinas/Neck_volume/neck_trials.json    the numbers of every trial and its section outline

The trial "now" is the body of the rules (no override). sheet_neck.py makes the sheets from these files.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocarina_addon import api, body as body_mod, checks_geo, kernel_bridge, presets as presets_mod, render, report  # noqa: E402

IMG = HERE / "images"
PRESET, V0 = "P4", 80.0
# Rule version 2 (2026-11-18), named in full: these trials were built against it, and since rule version 3
# (2026-11-19) a value that a trial does not name would come from the new rule.
RULES_V2 = dict(stub_style="neck", stub_pitch_deg=15.0, windway_pitch_deg=5.0, shelf_angle_deg=40.0, port_angle_deg=45.0)
FOLLOW = dict(neck_cover_mm=2.2)                       # the top line of the neck follows the pipe, 2.2 mm over its roof (the sample)
TRIALS = {
    # name: (what it is, overrides)
    "now": ("rule version 2 (2026-11-18): top line of the neck 15° off the body, pipe +5°", {}),
    "nk-a": ("top line follows the pipe; pipe +5° as now; bell as now", dict(FOLLOW, stub_pitch_deg=5.0)),
    "nk-slim": ("as nk-a, slimmer bell (32 × 16 mm at the body)", dict(FOLLOW, stub_pitch_deg=5.0, neck_base_width_mm=32.0, neck_base_depth_mm=16.0)),
    "nk-full": ("as nk-a, the sample's bell (48.5 × 24.5 mm at the body)", dict(FOLLOW, stub_pitch_deg=5.0, neck_base_width_mm=48.5, neck_base_depth_mm=24.5)),
    "nk-p0": ("top line follows the pipe; pipe level (0°)", dict(FOLLOW, stub_pitch_deg=0.0, windway_pitch_deg=0.0)),
    "nk-p10": ("top line follows the pipe; pipe +10°", dict(FOLLOW, stub_pitch_deg=10.0, windway_pitch_deg=10.0)),
    "nk-p17": ("top line follows the pipe; pipe +17.65° (the sample's angle)", dict(FOLLOW, stub_pitch_deg=17.65, windway_pitch_deg=17.65)),
}
BODY_COLOR = (0.78, 0.74, 0.62, 1.0)
AIR_RGB = (0.35, 0.62, 1.0)


def crop(V, F, centre, radius):
    sel = np.linalg.norm(V - centre, axis=1) < radius
    keep = sel[F].all(axis=1)
    used = np.unique(F[keep])
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    return V[used], remap[F[keep]]


def pictures(body, name):
    V, F = body.solid
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    L, Lw, wall = v.window_length_mm, v.windway_length_mm, v.wall_at_window_mm
    mid = o - fx * (L + 0.45 * Lw) + fz * 2.0                       # about the middle of the neck
    cV, cF = crop(V, F, mid, 46.0)
    # name: (camera looks along, up, the whole body or the part around the neck)
    views = {"_outside": (tuple(-0.75 * fz + 0.50 * fx + 0.42 * fy), tuple(fz), True),    # three-quarter, from the mouth end, onto the window
             "_window": (tuple(-0.62 * fz - 0.70 * fx + 0.28 * fy), tuple(fz), True),     # from beyond the labium, back toward the neck
             "_side": (tuple(fy), tuple(fz), False),                                      # profile: the jet runs left to right, outside is up
             "_mouth": (tuple(fx - 0.25 * fz), tuple(fz), False)}                         # from the mouth end
    files = {}
    for key, (look, up, part) in views.items():
        render.VIEWS[key] = (look, up)
        mesh = (cV, cF, BODY_COLOR) if part else (V, F, BODY_COLOR)
        p = render.render_views([mesh], str(IMG), prefix=f"{name}", views=(key,), size_px=820)[0]
        target = str(IMG / f"{name}{key}.png")
        os.replace(p, target)
        files[key[1:]] = target
    extent = (-L - Lw - 4.0, 18.0, -24.0, wall + 13.0)
    files["section"] = render.section_image(V, F, o, fy, fx, fz, str(IMG / f"{name}_section.png"), mm_per_px=0.05, extent=extent,
                                            extra=[(body.air_capped[0], body.air_capped[1], AIR_RGB)], marks=[((0.0, 0.0), (1.0, 0.1, 0.1))])[0]
    S = render.section_2d(V, F, o, fy, fx, fz)
    keep = (S[..., 0].min(axis=1) > extent[0] - 2) & (S[..., 0].max(axis=1) < extent[1] + 2) & (S[..., 1].min(axis=1) > -26) & (S[..., 1].max(axis=1) < 22)
    return files, np.round(S[keep], 3).tolist()


def one(name, P):
    what, over = TRIALS[name]
    over = dict(RULES_V2, **over)
    t0 = time.time()
    bid = body_mod.default_body_id(PRESET, V0) + (f"-{name}" if name.startswith("nk-") else f"-nk-{name}")   # never the files of P4-80 itself
    preset = dict(presets_mod.get_preset(PRESET), **over)
    body = api.build_checked_body(preset, V0, str(ROOT / "addon_out" / bid), params=P, renders=True, root=ROOT, body_id=bid)
    shown = " ".join(f"{k}={v:g}" if isinstance(v, float) else f"{k}={v}" for k, v in over.items())
    written = (f"Written by `Analizes_ocarinas/Neck_volume/neck_trials.py` (trial {name}): preset {PRESET} with {shown}." if over else
               f"Written by `Analizes_ocarinas/Neck_volume/neck_trials.py` (trial {name}): the body of the rules.")
    report.write_body_report(body, ROOT / "addon_checks", time.time() - t0, written, json_default=body_mod._json_default)
    files, outline = pictures(body, name)
    bad = checks_geo.unexpected_failures(body)
    m = body.measurements
    g = m["voicing"]
    C = {c["name"]: c for c in body.checks}
    cut = {b["name"]: -b["delta_mm3"] for b in body.booleans}
    row = dict(trial=name, body_id=bid, what=what, overrides=over, voicing_hash=body.sizing.voicing.version_hash,
               unexpected=[c["name"] for c in bad], warnings=[c["name"] for c in checks_geo.warnings(body)],
               neck=g.get("neck"), flare_steepest_deg=g.get("flare_steepest_deg"), above_outer_face_mm=g.get("max_height_above_outer_face_mm"),
               window_area_mm2=g.get("window_area_mm2"), labium_angle_deg=g.get("labium_angle_deg"), labium_edge_mm=g.get("labium_edge_thickness_mm"),
               windway_roof_mm=g.get("windway_roof_thickness_mm"), windway_floor_lip_mm=g.get("windway_floor_lip_mm"),
               capped_air_cm3=m["volume"]["capped_air_measured_cm3"], plastic_cm3=m["volume"]["body_plastic_cm3"],
               window_cut_removes_mm3=cut.get("window throat + labium ramp"), windway_removes_mm3=cut.get("windway"),
               wall_thinnest=C.get("wall_thickness", {}).get("message"),
               keepouts=C.get("voicing_keepouts", {}).get("message"), files={k: pathlib.Path(p).name for k, p in files.items()},
               outline=outline, seconds=round(time.time() - t0, 1))
    print(f"[{bid}] {'OK' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(row['unexpected'])}; {len(row['warnings'])} warnings; "
          f"{row['seconds']} s", flush=True)
    return row


def main(argv):
    only = None
    if "--only" in argv:
        only = argv[argv.index("--only") + 1].split(",")
    IMG.mkdir(parents=True, exist_ok=True)
    P = kernel_bridge.load_params()
    path = HERE / "neck_trials.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for name in TRIALS:
        if only and name not in only:
            continue
        try:
            data[name] = one(name, P)
        except Exception as exc:                 # noqa: BLE001 - one trial must not hide the others
            import traceback
            traceback.print_exc()
            data[name] = dict(trial=name, what=TRIALS[name][0], overrides=TRIALS[name][1], build_failed=str(exc))
            print(f"[{name}] BUILD FAILED: {exc}", flush=True)
        path.write_text(json.dumps(data, indent=1, default=body_mod._json_default), encoding="utf-8")
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(argv)
    sys.stdout.flush()
