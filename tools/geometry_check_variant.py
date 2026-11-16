"""Build and check one body with preset values overridden, without touching the preset file.

Run it with Blender 5.1 in background mode, from the repository root:

    blender -b --factory-startup --python tools/geometry_check_variant.py -- P3 80 ov12 hand_overlap_mm=12 [--renders]

    P3 80      preset and V0 in cm3
    ov12       suffix of the body id: the body is P3-80-ov12, so the files of the plain P3-80 stay as they are
    key=value  any number of preset overrides (numbers, or a hole name for sub1_parent / sub2_parent)

It runs the same build and the same checks as `tools/geometry_check.py -- body`, on the STL read back from
disk, and writes addon_checks/<id>.md, addon_checks/<id>.json, addon_out/<id>/ and, with --renders,
addon_renders/<id>/. The report's first line names this script and the overrides.
"""
from __future__ import annotations

import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocarina_addon import body as body_mod, presets as presets_mod  # noqa: E402
from tools import geometry_check_body as gcb  # noqa: E402


def _value(text: str):
    try:
        return float(text)
    except ValueError:
        return text


def main(argv) -> int:
    renders = "--renders" in argv
    args = [a for a in argv if not a.startswith("--")]
    pid, v0, suffix = args[0], float(args[1]), args[2]
    overrides = {k: _value(v) for k, v in (a.split("=", 1) for a in args[3:])}
    preset = dict(presets_mod.get_preset(pid), **overrides)
    bid = f"{body_mod.default_body_id(pid, v0)}-{suffix}"
    shown = " ".join(f"{k}={v:g}" if isinstance(v, float) else f"{k}={v}" for k, v in overrides.items())
    return gcb.check_body(preset, v0, renders, body_id=bid,
                          written_by=f"Written by `tools/geometry_check_variant.py -- {pid} {v0:g} {suffix} {shown}`: preset {pid} "
                                     f"with {shown}.")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    sys.stdout.flush()
    os._exit(code) if code else None
