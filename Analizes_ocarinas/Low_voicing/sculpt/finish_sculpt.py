"""Finish an instrument from the owner's sculpt, and measure what the sculpt changed (series 3).

    blender -b --factory-startup --disable-autoexec <the owner's .blend> --python Analizes_ocarinas/Low_voicing/sculpt/finish_sculpt.py -- [--base A] [--tag v1]

The .blend is a copy of sculpt/OCA_sculpt_base.blend that the owner sculpted in and saved under a new name. This
takes the shell (and the neck, if it is still a separate object) of base A or B as they were left, with their
modifiers, and lets ocarina_addon.shell_edit.finish do the rest: the wall is measured at every hole, the holes are
sized for it, the chamber is solved again for 80 cm3, the chamber, the holes, the window and the pipe are cut, and
every check runs on the STL read back from disk.

It writes
    addon_out/<id>/, addon_checks/<id>.md / .json, addon_renders/<id>/     the usual output (<id> = P4-80-sculpt<base>-<tag>)
    Analizes_ocarinas/Low_voicing/sculpt/result_<tag>.json                 the checks, and the sculpt against its base
    Analizes_ocarinas/Low_voicing/sculpt/images/<tag>_*.png                the pictures of the sheets
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

import bpy

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in (str(ROOT), str(HERE.parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

import series3_trials as s3  # noqa: E402  (installs the hooks: the shoulder, the blend, the inner walls)
from ocarina_addon import body as body_mod, checks_geo, kernel_bridge, meshutil, report, shell_edit  # noqa: E402


def against_base(user, base_shell, base_neck):
    """Where the sculpt added plastic to its base and where it took some away: distances from the sculpt's surface
    to the base's (the plain shell joined with the plain neck), outside positive."""
    V = np.asarray(user[0], float)
    trees = [meshutil.bvh(*m) for m in (base_shell, base_neck) if m is not None]
    step = max(1, len(V) // 20000)
    out = []
    for p in V[::step]:
        d = min(float(t.find_nearest(tuple(p))[3]) for t in trees)
        inside = any(meshutil.inside(t, p) for t in trees)
        out.append(-d if inside else d)
    out = np.array(out)
    P = V[::step]
    far = P[int(np.argmax(out))]
    deep = P[int(np.argmin(out))]
    return dict(samples=int(len(out)), added_max_mm=float(out.max()), added_max_at=[float(c) for c in far],
                removed_max_mm=float(-out.min()), removed_max_at=[float(c) for c in deep],
                percentiles_5_25_50_75_95_mm=[float(v) for v in np.percentile(out, [5, 25, 50, 75, 95])],
                share_of_surface_moved_out_more_than_0p5mm=float((out > 0.5).mean()),
                share_of_surface_moved_in_more_than_0p5mm=float((out < -0.5).mean()))


def main(argv):
    key = argv[argv.index("--base") + 1] if "--base" in argv else "A"
    tag = argv[argv.index("--tag") + 1] if "--tag" in argv else "check"
    shell_ob = next((o for o in bpy.data.objects if o.get(shell_edit.BASE_PROPERTY) and f"sculpt{key}" in o.name), None)
    if shell_ob is None:
        raise SystemExit(f"no shell of base {key} in this file (an object with the property {shell_edit.BASE_PROPERTY!r})")
    state = shell_edit.base_state(shell_ob)
    par = json.loads(shell_ob.get("oca_param_overrides", "{}"))
    P = s3.lv.params_with(kernel_bridge.load_params(), par)
    for col in bpy.data.collections:                        # a hidden collection is not evaluated
        col.hide_viewport = False
    bid = f"{state['body_id']}-{tag}"
    t0 = time.time()
    user = shell_edit.user_meshes(shell_ob)
    # the base as it was made: built again from the stored preset (the owner may have changed the objects in place)
    base = shell_edit.base_parts(state["preset"], state["v0_cm3"], params=P, body_id=state["body_id"], verbose=False)
    body = shell_edit.finish(shell_ob, export_dir=str(ROOT / "addon_out" / bid), body_id=bid, params=P, renders=True, keep_objects=False)
    report.write_body_report(body, ROOT / "addon_checks", time.time() - t0,
                             f"Written by `Analizes_ocarinas/Low_voicing/sculpt/finish_sculpt.py` from `{pathlib.Path(bpy.data.filepath).name}` "
                             f"(base {key}).", json_default=body_mod._json_default)
    s3.lv.IMG = HERE / "images"
    s3.lv.IMG.mkdir(exist_ok=True)
    files, _ = s3.pictures(body, tag)
    bad = checks_geo.unexpected_failures(body)
    joined = user[0] if user[1] is None else None
    res = dict(file=pathlib.Path(bpy.data.filepath).name, base=key, body_id=bid, voicing_hash=body.voicing_hash,
               neck_is_separate=user[1] is not None,
               unexpected={c["name"]: c["message"] for c in bad}, warnings={c["name"]: c["message"] for c in checks_geo.warnings(body)},
               checks={c["name"]: dict(status=c["status"], message=c["message"]) for c in body.checks},
               plastic_cm3=body.measurements["volume"]["body_plastic_cm3"], capped_air_cm3=body.measurements["volume"]["capped_air_measured_cm3"],
               cavity_mode=body.measurements.get("cavity_mode"), shell_edit=body.info.get("shell_edit"),
               user_shell_cm3=float(meshutil.volume(*user[0]) / 1000.0), base_shell_cm3=float(meshutil.volume(*base.shell) / 1000.0),
               user_neck_cm3=None if user[1] is None else float(meshutil.volume(*user[1]) / 1000.0),
               base_neck_cm3=float(meshutil.volume(*base.neck) / 1000.0),
               shell_against_base=against_base(user[0], base.shell, base.neck if joined is not None else None),
               neck_against_base=None if user[1] is None else against_base(user[1], None, base.neck),
               files={k: pathlib.Path(p).name for k, p in files.items()}, seconds=round(time.time() - t0, 1))
    (HERE / f"result_{tag}.json").write_text(json.dumps(res, indent=1, default=body_mod._json_default), encoding="utf-8")
    print(f"[{bid}] {'OK' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(res['unexpected'])}; {len(res['warnings'])} warnings", flush=True)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    sys.stdout.flush()
