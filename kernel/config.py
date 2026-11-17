"""Loads params/alto_c_12hole.toml (standard library only).

Every kernel module that needs a rule or a constant takes a params dict, so the
Blender add-on can pass its own copy of the file. With no argument the repository
file is read.
"""
from __future__ import annotations

import pathlib
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_PARAMS_PATH = ROOT / "params" / "alto_c_12hole.toml"


def load_params(path=None) -> dict:
    """Return the parameter file as a nested dict. Units are as written in the file (mm, Hz, Pa)."""
    path = pathlib.Path(path) if path is not None else DEFAULT_PARAMS_PATH
    with open(path, "rb") as fh:
        return tomllib.load(fh)
