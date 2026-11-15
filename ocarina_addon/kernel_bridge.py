"""The one place where the add-on reaches the acoustic kernel. Standard library only.

The kernel is the source of every number. The add-on never re-derives acoustics.

The kernel modules are flat files that import each other by plain name (`import config`, `import checks`,
`import holes`, ...). Those names are generic, and Blender's sys.path can hold other modules with the
same names. So this module puts the kernel folder FIRST on sys.path, imports the modules, and checks
that every one of them really came from the kernel folder.

Where the kernel is looked for, in this order:
    <add-on folder>/kernel        a copy packed into the extension (for an installed extension)
    <add-on folder>/../kernel     the repository layout (for development and the headless entry)
The parameter file is looked for in the same way: <add-on>/params/, then <repository>/params/.
The add-on always passes `params=` to the kernel and never relies on the kernel's default path.
"""
from __future__ import annotations

import importlib
import pathlib
import sys
import tomllib
import types

ADDON_DIR = pathlib.Path(__file__).resolve().parent
KERNEL_MODULES = ("ocarina_kernel", "config", "checks", "voicing", "holes", "sizing", "measurements", "fitter",
                  "calibration")
PARAMS_FILE = "alto_c_12hole.toml"

_cache: types.SimpleNamespace | None = None


def kernel_dir() -> pathlib.Path:
    for cand in (ADDON_DIR / "kernel", ADDON_DIR.parent / "kernel"):
        if (cand / "ocarina_kernel.py").is_file():
            return cand
    raise ImportError("the acoustic kernel was not found beside the add-on (looked for kernel/ocarina_kernel.py "
                      f"in {ADDON_DIR} and in {ADDON_DIR.parent})")


def params_path() -> pathlib.Path:
    for cand in (ADDON_DIR / "params" / PARAMS_FILE, ADDON_DIR.parent / "params" / PARAMS_FILE):
        if cand.is_file():
            return cand
    raise FileNotFoundError(f"parameter file {PARAMS_FILE} not found beside the add-on")


def load_params(path=None) -> dict:
    with open(path if path is not None else params_path(), "rb") as fh:
        return tomllib.load(fh)


def kernel() -> types.SimpleNamespace:
    """Import the kernel modules and return them as attributes of one object (k.sizing, k.voicing, ...)."""
    global _cache
    if _cache is not None:
        return _cache
    kdir = kernel_dir()
    kpath = str(kdir)
    if kpath in sys.path:
        sys.path.remove(kpath)
    sys.path.insert(0, kpath)
    # A module with one of these names that was imported from somewhere else must not be reused.
    for name in KERNEL_MODULES:
        mod = sys.modules.get(name)
        if mod is not None and pathlib.Path(getattr(mod, "__file__", "") or "").resolve().parent != kdir:
            del sys.modules[name]
    ns = types.SimpleNamespace()
    for name in KERNEL_MODULES:
        mod = importlib.import_module(name)
        origin = pathlib.Path(mod.__file__).resolve().parent
        if origin != kdir:
            raise ImportError(f"module {name!r} was imported from {origin}, not from the kernel folder {kdir}")
        setattr(ns, name, mod)
    ns.dir = kdir
    _cache = ns
    return ns
