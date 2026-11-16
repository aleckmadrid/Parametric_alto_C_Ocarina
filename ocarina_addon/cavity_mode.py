"""The cavity-mode desk check: the first standing-wave mode of a body's capped air mesh.

Standard library only. The solver (cavity_mode_solver.py) needs scipy, which Blender's Python does not
have. So this module finds a Python that has numpy and scipy, runs the solver there on the exported
`<id>_air_capped.stl`, and reads the JSON it writes beside the STL (`<id>_cavity_mode.json`).

Where a Python is looked for, in this order:
    the environment variable OCARINA_PYTHON
    the project's .venv   (<repository>/.venv)
    `python`, `python3` and the Windows launcher `py` on PATH
Each candidate is tested once (it must import numpy and scipy). Blender's own interpreter is skipped.

    run(stl_path, f_top_hz, c_m_s)    -> dict. "computed" is False with a "reason" when no solver could run.
    verdict(ratio, margin, fem_margin) -> "pass" / "needs_fem" / "fail"

The check never passes by default: when the solver did not run, the caller reports a failure that says so.
The same step can be run by hand:   python ocarina_addon/cavity_mode_solver.py <air.stl> --json <out.json>
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys

ADDON_DIR = pathlib.Path(__file__).resolve().parent
SOLVER = ADDON_DIR / "cavity_mode_solver.py"
GRIDS_MM = (1.5, 2.0)
TIMEOUT_S = 900
_python: tuple | None = None          # (executable or None, note)


def _env():
    env = dict(os.environ)
    for key in ("PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP"):          # Blender may set them for its own Python
        env.pop(key, None)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _candidates():
    seen = []
    explicit = os.environ.get("OCARINA_PYTHON")
    if explicit:
        seen.append(explicit)
    for root in (ADDON_DIR.parent, ADDON_DIR):
        for rel in (".venv/Scripts/python.exe", ".venv/bin/python"):
            p = root / rel
            if p.is_file():
                seen.append(str(p))
    for name in ("python", "python3", "py"):
        p = shutil.which(name)
        if p:
            seen.append(p)
    own = os.path.normcase(os.path.abspath(sys.executable or ""))
    out = []
    for p in seen:
        q = os.path.normcase(os.path.abspath(p))
        if q != own and q not in [os.path.normcase(os.path.abspath(x)) for x in out]:
            out.append(p)
    return out


def find_python(refresh: bool = False):
    """(executable, note): a Python that imports numpy and scipy, or (None, why none was found)."""
    global _python
    if _python is not None and not refresh:
        return _python
    tried = []
    for exe in _candidates():
        try:
            r = subprocess.run([exe, "-c", "import numpy, scipy.sparse.linalg; print('ok')"], capture_output=True, text=True,
                               timeout=120, env=_env())
        except (OSError, subprocess.SubprocessError) as exc:
            tried.append(f"{exe}: {exc}")
            continue
        if r.returncode == 0 and "ok" in r.stdout:
            _python = (exe, "")
            return _python
        tried.append(f"{exe}: numpy or scipy is missing")
    _python = (None, "no Python with numpy and scipy was found (" + ("; ".join(tried) if tried else "nothing on PATH")
               + "). Set OCARINA_PYTHON or create a .venv in the repository")
    return _python


def result_path(stl_path) -> pathlib.Path:
    p = pathlib.Path(stl_path)
    name = p.name[:-len("_air_capped.stl")] if p.name.endswith("_air_capped.stl") else p.stem
    return p.with_name(name + "_cavity_mode.json")


def run(stl_path, f_top_hz: float, c_m_s: float) -> dict:
    """Compute the first cavity mode of the air mesh at stl_path in a second Python process."""
    exe, note = find_python()
    if exe is None:
        return dict(computed=False, reason=note)
    out = result_path(stl_path)
    cmd = [exe, str(SOLVER), str(stl_path), "--f-top", repr(float(f_top_hz)), "--c", repr(float(c_m_s)),
           "--grid", *[repr(g) for g in GRIDS_MM], "--json", str(out)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S, env=_env())
    except (OSError, subprocess.SubprocessError) as exc:
        return dict(computed=False, reason=f"the solver did not finish: {exc}", python=exe)
    if r.returncode != 0:
        tail = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["no output"]
        return dict(computed=False, reason=f"the solver stopped with exit code {r.returncode}: {tail[0]}", python=exe)
    try:
        res = json.loads(out.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return dict(computed=False, reason=f"the solver result could not be read: {exc}", python=exe)
    res.update(computed=True, python=exe, result_file=str(out))
    return res


def verdict(ratio: float, margin: float = 1.0, fem_margin: float = 1.3) -> str:
    """pass at fem_margin x the top note or more, needs_fem from margin to fem_margin, fail below margin."""
    if ratio >= fem_margin:
        return "pass"
    return "needs_fem" if ratio >= margin else "fail"
