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
C4_SET = [("P1", 80.0), ("P0", 80.0), ("P0", 65.0), ("P0", 125.0), ("P2", 80.0), ("P3", 80.0), ("P0", 95.0), ("P0", 110.0)]


def check_body(preset, v0: float, renders: bool, body_id: str | None = None, written_by: str | None = None) -> int:
    """Build, check and report one body. `preset` is a preset name or a preset dict (a variant)."""
    t0 = time.time()
    P = kernel_bridge.load_params()
    pid = preset if isinstance(preset, str) else preset.get("id", "custom")
    bid = body_id or body_mod.default_body_id(pid, v0)
    body = api.build_checked_body(preset, v0, str(OUT_DIR / bid), params=P, renders=renders, root=ROOT, body_id=bid)
    written_by = written_by or f"Written by `tools/geometry_check.py -- body {pid} {v0:g}`."
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
        return check_body(args[1], float(args[2]), renders)
    code = 0
    for preset, v0 in C4_SET:
        try:
            code |= check_body(preset, v0, renders)
        except Exception as exc:                 # noqa: BLE001 - one body must not hide the others
            import traceback
            traceback.print_exc()
            print(f"[{preset}-{v0:g}] BUILD FAILED: {exc}", flush=True)
            code |= 1
    return code
