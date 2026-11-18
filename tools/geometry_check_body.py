"""Body part of the geometry check (see tools/geometry_check.py for how to run it).

For each body it builds the body, writes the STL files, READS THE BODY STL BACK from disk and runs every
measurement of ocarina_addon/checks_geo.py on the file that was written (ocarina_addon.api.build_checked_body).
The cavity-mode step runs in a second Python process on the exported air mesh. It then writes

    addon_checks/<body>.md      every check, the warnings, the hand layout, the per-hole table, the Boolean log
    addon_checks/<body>.json    the same as data
    addon_renders/<body>/       the review pictures (with --renders)
    addon_out/<body>/           the STL files (not committed)
"""
from __future__ import annotations

import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

from ocarina_addon import api, body as body_mod, checks_geo, kernel_bridge, report  # noqa: E402

CHECK_DIR = ROOT / "addon_checks"
OUT_DIR = ROOT / "addon_out"
# The printed set: P0 ladder 65 / 80 / 95, P0-88 (Stage 3 prediction body), P1-P4 at 80; and P0-95 with the 3 mm window wall.
# P0-110 and P0-125 (the old ladder top) are kept as generator range checks; their reports in addon_checks/ are from C4.
C4_SET = [("P1", 80.0), ("P0", 80.0), ("P0", 65.0), ("P2", 80.0), ("P3", 80.0), ("P4", 80.0), ("P0", 95.0), ("P0", 88.0)]
WALL3_SET = [("P0", 95.0)]
RANGE_SET = [("P0", 110.0), ("P0", 125.0)]


def check_body(preset, v0: float, renders: bool, body_id: str | None = None, written_by: str | None = None,
               wall_at_window_mm: float | None = None) -> int:
    """Build, check and report one body. `preset` is a preset name or a preset dict (a variant)."""
    t0 = time.time()
    P = kernel_bridge.load_params()
    pid = preset if isinstance(preset, str) else preset.get("id", "custom")
    bid = body_id or body_mod.default_body_id(pid, v0, wall_at_window_mm,
                                              float(P["voicing_rules"]["default_wall_at_window_mm"]))
    body = api.build_checked_body(preset, v0, str(OUT_DIR / bid), params=P, renders=renders, root=ROOT, body_id=bid,
                                  wall_at_window_mm=wall_at_window_mm)
    wall_arg = "" if wall_at_window_mm is None else f" {wall_at_window_mm:g}"
    written_by = written_by or f"Written by `tools/geometry_check.py -- body {pid} {v0:g}{wall_arg}`."
    report.write_body_report(body, CHECK_DIR, time.time() - t0, written_by, json_default=body_mod._json_default)
    bad = checks_geo.unexpected_failures(body)
    for c in body.checks:
        print(f"[{bid}] {body_mod.STATUS_MARKS.get(c['status'], c['status'])}{' (expected)' if c['expected'] else ''} "
              f"{c['name']}: {c['message']}", flush=True)
    print(f"[{bid}] {'OK' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(c['name'] for c in bad)}; "
          f"{len(checks_geo.warnings(body))} warnings; {time.time() - t0:.0f} s", flush=True)
    return 1 if bad else 0


def main(args, renders: bool) -> int:
    if args[0] == "body":
        # body <preset> <v0> [<window wall mm>]
        return check_body(args[1], float(args[2]), renders, wall_at_window_mm=float(args[3]) if len(args) > 3 else None)
    code = 0
    todo = [(p_, v_, None) for p_, v_ in C4_SET] + [(p_, v_, 3.0) for p_, v_ in WALL3_SET]
    if len(args) > 1 and args[1] == "range":
        todo += [(p_, v_, None) for p_, v_ in RANGE_SET]
    for preset, v0, wall in todo:
        try:
            code |= check_body(preset, v0, renders, wall_at_window_mm=wall)
        except Exception as exc:                 # noqa: BLE001 - one body must not hide the others
            import traceback
            traceback.print_exc()
            print(f"[{preset}-{v0:g}] BUILD FAILED: {exc}", flush=True)
            code |= 1
    return code
