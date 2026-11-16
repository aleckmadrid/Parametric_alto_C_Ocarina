"""Build and check one body with preset values overridden, without touching the preset file.

Run it with Blender 5.1 in background mode, from the repository root:

    blender -b --factory-startup --python tools/geometry_check_variant.py -- P2 80 c23 layout_centre_from_port_mm=23 [--renders]

    P2 80      preset and V0 in cm3
    c23        suffix of the body id: the body is P2-80-c23, so the files of the plain P2-80 stay as they are
    key=value  any number of preset overrides (numbers only)

It runs the same build and the same checks as `tools/geometry_check.py -- body`, on the STL read back from
disk, and writes addon_checks/<id>.md, addon_checks/<id>.json, addon_out/<id>/ and, with --renders,
addon_renders/<id>/. The report's first line names this script and the overrides.
"""
from __future__ import annotations

import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocarina_addon import body as body_mod, checks_geo, export, kernel_bridge, meshutil, presets as presets_mod  # noqa: E402
from tools import geometry_check_body as gcb  # noqa: E402


def main(argv) -> int:
    renders = "--renders" in argv
    args = [a for a in argv if not a.startswith("--")]
    pid, v0, suffix = args[0], float(args[1]), args[2]
    overrides = {k: float(v) for k, v in (a.split("=", 1) for a in args[3:])}
    preset = dict(presets_mod.get_preset(pid), **overrides)
    bid = f"{body_mod.default_body_id(pid, v0)}-{suffix}"
    t0 = time.time()
    P = kernel_bridge.load_params()
    out = gcb.OUT_DIR / bid
    body = body_mod.build_body(preset, v0, params=P, export_dir=str(out), run_checks=False, body_id=bid)
    V, F = export.read_stl(body.files["stl"])
    rep = meshutil.manifold_report(V, F)
    checks_geo.run_all(body, P, V, F)
    body.measurements["stl_file"] = dict(path=str(pathlib.Path(body.files["stl"]).relative_to(ROOT)), triangles=rep["triangles"],
                                         manifold=rep["manifold"], volume_cm3=meshutil.volume(V, F) / 1000.0,
                                         volume_in_memory_cm3=meshutil.volume(*body.solid) / 1000.0)
    for key in ("air_capped_stl", "air_fem_stl"):
        aV, aF = export.read_stl(body.files[key])
        r = meshutil.manifold_report(aV, aF)
        body.measurements[key] = dict(triangles=r["triangles"], manifold=r["manifold"], shells=r["shells"],
                                      volume_cm3=meshutil.volume(aV, aF) / 1000.0)
    body.measurements["preset_overrides"] = overrides
    body_mod.export_body(body, str(out))
    if renders:
        from ocarina_addon import render_body
        render_body.render_all(body)
    gcb.write_report(body, time.time() - t0)
    md = gcb.CHECK_DIR / f"{bid}.md"
    lines = md.read_text(encoding="utf-8").split("\n")
    lines[2] = (f"Written by `tools/geometry_check_variant.py -- {pid} {v0:g} {suffix} "
                + " ".join(f"{k}={v:g}" for k, v in overrides.items())
                + f"`: preset {pid} with " + ", ".join(f"`{k}` = {v:g}" for k, v in overrides.items())
                + ". " + lines[2].split(". ", 1)[1])
    md.write_text("\n".join(lines), encoding="utf-8")
    bad = checks_geo.unexpected_failures(body)
    for c in body.checks:
        print(f"[{bid}] {c['status'].upper()}{' (expected)' if c['expected'] else ''} {c['name']}: {c['message']}", flush=True)
    print(f"[{bid}] {'OK' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(c['name'] for c in bad)} in {time.time() - t0:.0f} s", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    sys.stdout.flush()
    os._exit(code) if code else None
