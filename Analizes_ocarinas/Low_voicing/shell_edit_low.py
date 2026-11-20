"""The shell-edit build with the low voicing (2026-11-19): does the two-step build still work when the voicing sits
on the thumb face?

Run it with Blender 5.1 in background mode, from the root of the checkout:

    blender -b --factory-startup --python Analizes_ocarinas/Low_voicing/shell_edit_low.py -- [--port 10] [--only plain sculpt]

It runs trials of tools/shell_edit_trial.py (the same edits, made by the same programs) on the base of the seed P4 at
80 cm3 with the voicing of trial lv-<port>f: the port at <port> degrees and the foot of the neck 29 mm wide.

    plain     nothing is edited. The finished body must be the body that low_voicing_trials.py builds in one step
    sculpt    a longer tail, a boss over the R ring hole, a groove across the L middle hole, a relief pattern over the
              whole body, and a neck that is 20 % thicker
    remesh    the shell and the neck voxel-remeshed and pushed outward by a cloud texture, as modifiers

It writes addon_checks/P4-80-lv-<port>f-edit-<trial>.md / .json, addon_renders/<the same>/ and
Analizes_ocarinas/Low_voicing/shell_edit_low.json.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocarina_addon import presets as presets_mod, shell_edit  # noqa: E402
from tools import shell_edit_trial as st  # noqa: E402

V0, FOOT_MM = 80.0, 29.0


def main(argv):
    port = float(argv[argv.index("--port") + 1]) if "--port" in argv else 10.0
    names = [a for a in argv[argv.index("--only") + 1:] if not a.startswith("--")] if "--only" in argv else ["plain", "sculpt"]
    preset = dict(presets_mod.get_preset("P4"), port_angle_deg=port, neck_foot_width_mm=FOOT_MM)
    base_id = f"P4-{V0:g}-lv-{port:g}f"
    build_base = shell_edit.build_base

    def low_base(_preset, v0, **kwargs):               # the trials ask for the preset by name: give them the low voicing
        return build_base(preset, v0, body_id=base_id, **kwargs)

    st.shell_edit.build_base = low_base
    try:
        rows = [st.run_trial(name, "P4", V0, True, False) for name in names]
    finally:
        st.shell_edit.build_base = build_base
    path = HERE / "shell_edit_low.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for r in rows:
        r.pop("body", None)
        data[r["body_id"]] = {k: (list(v) if isinstance(v, tuple) else v) for k, v in r.items()}
    path.write_text(json.dumps(data, indent=1, default=float), encoding="utf-8")
    print(st.summary(rows, base_id, V0).encode("ascii", "replace").decode("ascii"), flush=True)
    return 0


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(args)
    sys.stdout.flush()
