"""Headless entry of the add-on. Run it with Blender 5.1 in background mode, from the repository root:

    blender -b --factory-startup --python ocarina_addon/headless.py -- cavity --preset P0 --volume 78.11 --out out/P0.stl
    blender -b --factory-startup --python ocarina_addon/headless.py -- body --preset P1 --v0 80 --out out/P1-80
    blender -b --factory-startup --python ocarina_addon/headless.py -- body --preset P0 --v0 95 --window-wall 3 --out out/P0-95-w3
    blender -b --factory-startup --python ocarina_addon/headless.py -- body --preset P4-bowl --v0 80 --calibration calibration/synthetic-fitted-constants.toml --out out/P4-bowl-80-cal

    blender -b --factory-startup --python ocarina_addon/headless.py -- stage1
    blender -b --factory-startup --python ocarina_addon/headless.py -- stage2
    blender -b --factory-startup --python ocarina_addon/headless.py -- stage3 --calibration calibration/synthetic-fitted-constants.toml

    cavity   the cavity mesh of a preset at a mesh volume (cm3), as an STL file
    body     a full test body (cavity, wall, voicing, holes): STL of the body, STL of the air domain,
             the check results as JSON, and a blank measurement template. Add --renders for the review pictures and
             --blend to save the scene; --calibration sizes it from a fitted-constants file (holes "fitted").
    stage1   the voicing stubs of docs/04 (V-a, V-b, V-d and the optional V-a0, V-a35)
    stage2   the round-1 bodies (P0 at 65, 80, 95 cm3; P1, P2, P4 at 80 cm3; P0-80-b and P0-80-c)
    stage3   the round-2 bodies, sized from a fitted-constants file, and P0 at 88 cm3 (the prediction body)

A stage writes, per body, the STL files, a blank measurement template and a check report, and one Markdown
report for the stage. Each body is checked on the STL read back from disk; the cavity-mode step is included
(it needs a Python with numpy and scipy: see ocarina_addon/cavity_mode.py). A stage builds every body even
when one fails. The exit code is 1 only when a body has an unexpected failure; expected failures and
warnings are listed in the report and leave the exit code at 0.

Where a stage writes (all can be changed with --out, --reports, --renders-dir):
    stage1, stage2   STL files and templates   addon_out/stage1/<id>/, addon_out/stage2/<id>/   (not in git)
                     reports                   addon_checks/stage1.md, addon_checks/stage2.md, addon_checks/<id>.md
                     pictures                  addon_renders/<id>/
    stage3           everything                addon_out/stage3-<calibration file name>/        (not in git)
                     stage report              addon_checks/stage3-<calibration file name>.md

The add-on does not have to be installed for this: the script imports the package from the repository.
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
    b.add_argument("--rating", default=None, choices=["soft", "medium", "loud"],
                   help="voice rating (default: the preset's own, e.g. soft for P4-bowl; else the rules' medium)")
    b.add_argument("--window-wall", type=float, default=None, choices=[3.0, 4.0],
                   help="wall at the window in mm: 4.0 (default) or 3.0 (narrower window at the same V0)")
    b.add_argument("--out", required=True, help="folder for the STL files and the check results")
    b.add_argument("--renders", action="store_true", help="also write the review pictures")
    b.add_argument("--blend", action="store_true", help="also save a .blend file with the procedural cavity")
    b.add_argument("--strict", action="store_true", help="exit with code 1 if a check fails that is not expected")
    b.add_argument("--calibration", default=None,
                   help="fitted-constants file: size the body from it for its resolved voicing (holes \"fitted\")")
    b.add_argument("--previous-inspection", default=None, help="with --specimen: an earlier <id>_inspection.json to compare with")
    b.add_argument("--specimen", action="store_true",
                   help="a specimen to print and measure: checks on the STL read back, the report, the annotated inspection, "
                        "the blank measurement template, the specimen record and PRINT-AND-MEASURE.md")
    for name, text in (("stage1", "build the Stage 1 voicing stubs"), ("stage2", "build the Stage 2 round-1 bodies"),
                       ("stage3", "build the Stage 3 round-2 bodies from a fitted-constants file")):
        s = sub.add_parser(name, help=text)
        s.add_argument("--out", help="folder for the STL files and measurement templates")
        s.add_argument("--reports", help="folder for the stage report and the per-body check reports")
        s.add_argument("--renders-dir", help="folder for the review pictures (one sub-folder per body)")
        s.add_argument("--no-renders", action="store_true", help="do not write the review pictures")
        s.add_argument("--only", nargs="+", metavar="ID", help="build only these body ids (for a quick try)")
        if name == "stage3":
            s.add_argument("--calibration", default=str(ROOT / "calibration" / "synthetic-fitted-constants.toml"),
                           help="fitted-constants file (default: the SYNTHETIC example)")
            s.add_argument("--renders", action="store_true", help="also write the review pictures (off by default for stage 3)")
            s.add_argument("--retarget-volume", action="store_true",
                           help="solve V0 again so that A4 is on pitch (default: keep the printed volume)")
    args = ap.parse_args(argv)

    if args.command.startswith("stage"):
        return run_stage(args)
    from ocarina_addon import api
    if args.command == "cavity":
        res = api.export_cavity(args.preset, args.volume, args.out)
        print(f"cavity {args.preset}: {res.volume_cm3:.4f} cm3, length {res.length_mm:.2f} mm, written to {args.out}")
        return 0
    from ocarina_addon import kernel_bridge
    k = kernel_bridge.kernel()
    cal = k.calibration.load_calibration(args.calibration) if args.calibration else None
    if args.specimen:
        body = api.export_specimen(args.preset, args.v0, args.out, rating=args.rating, wall_at_window_mm=args.window_wall,
                                   renders=args.renders, calibration=cal,
                                   previous_inspection=args.previous_inspection)
        print(api.format_summary(body))
        return 1 if (args.strict and [c for c in body.checks if c["status"] == "fail" and not c.get("expected")]) else 0
    body = api.build_body(args.preset, args.v0, rating=args.rating, wall_at_window_mm=args.window_wall,
                          export_dir=args.out, renders=args.renders,
                          save_blend=args.blend, calibration=cal)
    print(api.format_summary(body))
    if body.kind == "body":                 # the blank template names the voicing and the holes that were built
        from ocarina_addon import presets
        t = k.measurements.template_from_sizing(body.sizing, body.body_id, shape=body.preset_id, key="fitted" if cal else "print",
                                                context=presets.calibration_context(presets.get_preset(args.preset)))
        k.measurements.write_measurement_file(pathlib.Path(args.out) / f"{body.body_id}_measurement.toml", t, blank=True)
    bad = [c for c in body.checks if c["status"] == "fail" and not c.get("expected")]
    return 1 if (bad and args.strict) else 0


def run_stage(args) -> int:
    from ocarina_addon import stages
    shown = "ocarina_addon/headless.py -- " + " ".join(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [args.command])
    common = dict(root=ROOT, only=args.only, command=shown)
    if args.command == "stage3":
        tag = "stage3-" + pathlib.Path(args.calibration).stem
        out = pathlib.Path(args.out) if args.out else ROOT / "addon_out" / tag
        reports = pathlib.Path(args.reports) if args.reports else ROOT / "addon_checks"
        stage = stages.run_stage3(out, args.calibration, report_path=reports / f"{tag}.md", body_report_dir=None,
                                  render_root=args.renders_dir, renders=args.renders and not args.no_renders,
                                  retarget_volume=args.retarget_volume, **common)
        return stage.exit_code
    out = pathlib.Path(args.out) if args.out else ROOT / "addon_out" / args.command
    reports = pathlib.Path(args.reports) if args.reports else ROOT / "addon_checks"
    renders_dir = pathlib.Path(args.renders_dir) if args.renders_dir else ROOT / "addon_renders"
    run = stages.run_stage1 if args.command == "stage1" else stages.run_stage2
    stage = run(out, report_path=reports / f"{args.command}.md", body_report_dir=reports, render_root=renders_dir,
                renders=not args.no_renders, **common)
    return stage.exit_code


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    sys.stdout.flush()
    if code:
        os._exit(code)
