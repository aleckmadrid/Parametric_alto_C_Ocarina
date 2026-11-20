"""Stage 1 stub for the 45 mm pipe of the low-voicing approach (owner, 2026-11-19: "Yes, un-park it").

Run it with Blender 5.1 in background mode, from the root of the checkout:

    blender -b --factory-startup --python Analizes_ocarinas/Low_voicing/stub_long_pipe.py

It builds stubs exactly as `ocarina_addon/headless.py -- stage1` builds V-a (preset S0, 25 cm3 of capped air, the
80 cm3 window, the build of the rules, no holes), through the same calls of ocarina_addon/stages.run_stage1:

    V-a     the rule's 30 mm pipe, built again in this checkout to check that it is the V-a of the main checkout
            (voicing hash 312011ec9f0e); its report goes beside this file, so the tracked addon_checks/V-a.md is untouched
    V-aw    the same with [voicing_rules] windway_length_mm = 45: the voicing of the trials named ...fw (40688a48d1c7)

A stub has no port angle, so V-aw serves every port angle of the approach. The round tip of lv-10fwdnr is outside the
hash (neck_floor_mm) and is left out: the stub measures the voicing.

Writes
    addon_out/lv-stubs/<id>/                         STL files and the blank measurement file of the stub
    addon_checks/V-aw.md / .json, addon_renders/V-aw/   the report and pictures of V-aw
    Analizes_ocarinas/Low_voicing/stubs/V-a.md / .json  the report of the rebuilt V-a; its pictures in stubs/renders/V-a/
    Analizes_ocarinas/Low_voicing/stubs/stubs.json      the numbers of both
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocarina_addon import api, body as body_mod, checks_geo, kernel_bridge, presets as presets_mod, report, stub  # noqa: E402

OUT = ROOT / "addon_out" / "lv-stubs"
STUBS_DIR = HERE / "stubs"
# id: (pipe length in mm or None for the rule, where the report goes, where the pictures go or None)
BUILDS = {
    "V-a": (None, STUBS_DIR, STUBS_DIR / "renders" / "V-a"),
    "V-aw": (45.0, ROOT / "addon_checks", ROOT / "addon_renders" / "V-aw"),
}


def params_for(P, pipe_mm):
    if pipe_mm is None:
        return P
    Q = copy.deepcopy(P)
    Q["voicing_rules"]["windway_length_mm"] = float(pipe_mm)
    return Q


def one(sid, P0):
    k = kernel_bridge.kernel()
    pipe_mm, report_dir, render_dir = BUILDS[sid]
    P = params_for(P0, pipe_mm)
    preset = presets_mod.get_preset(stub.STUB_PRESET)
    volume = float(preset["stub_volume_cm3"])
    t0 = time.time()
    out = OUT / sid
    b = api.build_checked_body(preset, volume, str(out), params=P, renders=render_dir is not None,
                               render_dir=str(render_dir) if render_dir else None, root=ROOT, body_id=sid, kind="stub",
                               sizing_fn=lambda L: stub.stub_sizing("V-a", P, volume), info=dict(stage=1))
    sz = b.sizing
    t = k.measurements.stub_template(sz.voicing, sid, sz.v0_cm3, predicted_hz=sz.predicted_pitch_hz)
    k.measurements.write_stub_file(out / f"{sid}_measurement.toml", t, blank=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    pipe_text = f"[voicing_rules] windway_length_mm = {pipe_mm:g}" if pipe_mm else "the rule's pipe"
    md = report.write_body_report(b, report_dir, time.time() - t0,
                                  f"Written by `Analizes_ocarinas/Low_voicing/stub_long_pipe.py`: Stage 1 stub V-a with {pipe_text}.",
                                  json_default=body_mod._json_default)
    m, v = b.measurements, sz.voicing
    g = m["voicing"]
    bad = checks_geo.unexpected_failures(b)
    row = dict(stub=sid, pipe_mm=v.windway_length_mm, voicing_hash=v.version_hash, v0_cm3=sz.v0_cm3,
               predicted_pitch_hz=sz.predicted_pitch_hz, eta_w_prior=sz.eta_w,
               window_area_mm2=g.get("window_area_mm2"), labium_edge_mm=g.get("labium_edge_thickness_mm"),
               labium_angle_deg=g.get("labium_angle_deg"), windway_roof_mm=g.get("windway_roof_thickness_mm"),
               flare_steepest_deg=g.get("flare_steepest_deg"), above_outer_face_mm=g.get("max_height_above_outer_face_mm"),
               neck=g.get("neck") or {}, capped_air_cm3=m["volume"]["capped_air_measured_cm3"],
               plastic_cm3=m["volume"]["body_plastic_cm3"], cavity_mode=m.get("cavity_mode"),
               unexpected=[c["name"] for c in bad], unexpected_messages={c["name"]: c["message"] for c in bad},
               warnings=[c["name"] for c in checks_geo.warnings(b)],
               checks={c["name"]: dict(status=c["status"], message=c["message"]) for c in b.checks},
               report=str(pathlib.Path(md).relative_to(ROOT)).replace("\\", "/"), seconds=round(time.time() - t0, 1))
    print(f"[{sid}] {'OK' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(row['unexpected'])}; hash {v.version_hash}; "
          f"pipe {v.windway_length_mm:g} mm; predicted {sz.predicted_pitch_hz:.1f} Hz; {row['seconds']} s", flush=True)
    return row


def main(argv):
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else list(BUILDS)
    STUBS_DIR.mkdir(parents=True, exist_ok=True)
    P = kernel_bridge.load_params()
    path = STUBS_DIR / "stubs.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for sid in only:
        data[sid] = one(sid, P)
        path.write_text(json.dumps(data, indent=1, default=body_mod._json_default), encoding="utf-8")
    return 0


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(args)
    sys.stdout.flush()
