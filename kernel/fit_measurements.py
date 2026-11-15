"""Command line for the fitter.

    python kernel/fit_measurements.py measurements/synthetic-round1/*.toml
    python kernel/fit_measurements.py a.toml b.toml --write-constants calibration/fitted-constants.toml
    python kernel/fit_measurements.py a.toml --share none      # psi = 1, fit k only

Prints the Markdown report. With --write-constants it also writes the constants file that the Stage 3
generator reads. Files with `synthetic = true` give a synthetic constants file.
"""
from __future__ import annotations

import argparse
import glob
import sys

import calibration
import config
import fitter
import measurements as meas


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Fit measurement files (docs/04, Stage 2 fit).")
    ap.add_argument("files", nargs="+", help="measurement TOML files, one per body")
    ap.add_argument("--share", default="shape", choices=["shape", "none"],
                    help="position factors shared by shape (default), or none (psi = 1, k only)")
    ap.add_argument("--reference-shape", default=None, help="shape whose psi have geometric mean 1 (default: most bodies)")
    ap.add_argument("--write-constants", default=None, help="write the fitted-constants TOML to this path")
    ap.add_argument("--params", default=None)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    P = config.load_params(args.params)
    files = []
    for pattern in args.files:                    # PowerShell and cmd do not expand wildcards
        found = sorted(glob.glob(pattern))
        files.extend(found if found else [pattern])
    try:
        bodies = [meas.load_measurement(f) for f in files]
    except meas.MeasurementIncomplete as exc:
        print(str(exc), file=sys.stderr)
        return 2
    fit = fitter.fit_bodies(bodies, P, share=args.share, reference_shape=args.reference_shape)
    print(fitter.format_report(fit))
    if args.write_constants:
        cal = calibration.calibration_from_fit(fit, bodies, params=P)
        calibration.write_calibration(args.write_constants, cal)
        print(f"\nConstants written to {args.write_constants}" + (" (SYNTHETIC)" if cal.synthetic else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
