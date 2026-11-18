"""Run every test suite of the project, one after the other, and print one summary (plain Python).

    python tools/run_tests.py                 # all four suites, about 5 minutes
    python tools/run_tests.py kernel plain    # only the suites named: kernel, plain, blender, extension

    kernel      python -m unittest discover -s kernel                 the acoustic kernel (standard library)
    plain       python -m unittest discover -s tests                  the add-on's modules that need no Blender
    blender     blender -b --factory-startup --python tests/run_blender_tests.py     cavities, bodies, stub, stages
    extension   python -m unittest discover -s tests/extension        pack the zip, install it in a temporary
                                                                      Blender profile, build a body with it

The Blender program is taken from the environment variable BLENDER, or from the default install path.
The exit code is 0 when every suite that ran is green.
"""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")
SUITES = {
    "kernel": [sys.executable, "-m", "unittest", "discover", "-s", "kernel"],
    "plain": [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
    "blender": [BLENDER, "-b", "--factory-startup", "--python", "tests/run_blender_tests.py"],
    "extension": [sys.executable, "-m", "unittest", "discover", "-s", "tests/extension"],
}


def main(argv) -> int:
    names = argv or list(SUITES)
    unknown = [n for n in names if n not in SUITES]
    if unknown:
        print(f"unknown suite: {', '.join(unknown)}; known: {', '.join(SUITES)}")
        return 2
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    rows, code = [], 0
    for name in names:
        t0 = time.time()
        print(f"=== {name}: {' '.join(SUITES[name])}", flush=True)
        r = subprocess.run(SUITES[name], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        text = (r.stdout or "") + (r.stderr or "")
        ran = re.findall(r"Ran (\d+) tests? in", text)
        last = [ln for ln in text.splitlines() if ln.strip()][-12:]
        if r.returncode != 0:
            code = 1
            print("\n".join(last).encode("ascii", "replace").decode("ascii"))
        skipped = re.findall(r"skipped[= ](\d+)", text)
        rows.append((name, ran[-1] if ran else "?", "OK" if r.returncode == 0 else f"FAILED (exit code {r.returncode})",
                     skipped[-1] if skipped else "0", time.time() - t0))
        print(f"    {rows[-1][2]}: {rows[-1][1]} tests, {rows[-1][3]} skipped, {rows[-1][4]:.0f} s", flush=True)
    print("\n| Suite | Tests | Skipped | Result | Time |\n| --- | --- | --- | --- | --- |")
    for name, ran, result, skipped, seconds in rows:
        print(f"| {name} | {ran} | {skipped} | {result} | {seconds:.0f} s |")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
