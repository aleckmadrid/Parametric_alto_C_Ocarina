"""Headless entry of the add-on. Run it with Blender 5.1 in background mode, from the repository root:

    blender -b --factory-startup --python ocarina_addon/headless.py -- cavity --preset P0 --volume 78.11 --out out/P0.stl
    blender -b --factory-startup --python ocarina_addon/headless.py -- body --preset P1 --v0 80 --out out/P1-80

    cavity   the cavity mesh of a preset at a mesh volume (cm3), as an STL file
    body     a full test body (cavity, wall, voicing, holes): STL of the body, STL of the air domain,
             the check results as JSON. Add --renders for the review pictures and --blend to save the scene.

The add-on does not have to be installed for this: the script imports the package from the repository.
The one-command-per-stage generators and the Markdown sizing report are checkpoint C5.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="ocarina_addon/headless.py", description="Parametric ocarina generator (headless).")
    sub = ap.add_subparsers(dest="command", required=True)
    c = sub.add_parser("cavity", help="export the cavity mesh of a preset")
    c.add_argument("--preset", default="P0")
    c.add_argument("--volume", type=float, required=True, help="mesh volume in cm3")
    c.add_argument("--out", required=True, help="STL file to write")
    b = sub.add_parser("body", help="build and export a full test body")
    b.add_argument("--preset", default="P1")
    b.add_argument("--v0", type=float, default=80.0, help="capped air volume V0 in cm3 (the acoustic target)")
    b.add_argument("--rating", default="medium", choices=["soft", "medium", "loud"])
    b.add_argument("--out", required=True, help="folder for the STL files and the check results")
    b.add_argument("--renders", action="store_true", help="also write the review pictures")
    b.add_argument("--blend", action="store_true", help="also save a .blend file with the procedural cavity")
    b.add_argument("--strict", action="store_true", help="exit with code 1 if a check fails that is not expected")
    args = ap.parse_args(argv)

    from ocarina_addon import api
    if args.command == "cavity":
        res = api.export_cavity(args.preset, args.volume, args.out)
        print(f"cavity {args.preset}: {res.volume_cm3:.4f} cm3, length {res.length_mm:.2f} mm, written to {args.out}")
        return 0
    body = api.build_body(args.preset, args.v0, rating=args.rating, export_dir=args.out, renders=args.renders,
                          save_blend=args.blend)
    print(api.format_summary(body))
    bad = [c for c in body.checks if c["status"] == "fail" and not c.get("expected")]
    return 1 if (bad and args.strict) else 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    sys.stdout.flush()
    if code:
        os._exit(code)
