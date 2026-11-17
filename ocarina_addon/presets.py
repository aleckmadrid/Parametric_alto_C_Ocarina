"""Reads the cavity presets (presets/cavity_presets.toml). Standard library only."""
from __future__ import annotations

import pathlib
import tomllib

SCHEMA = "ocarina-cavity-presets-v1"
DEFAULT_PATH = pathlib.Path(__file__).resolve().parent / "presets" / "cavity_presets.toml"
REQUIRED = ("width", "height", "exponent", "bend_deg", "port_u", "port_angle_deg", "layout")


def load_presets(path=None) -> dict:
    """Return {preset name: dict}. Raises ValueError for a wrong schema or a missing key."""
    path = pathlib.Path(path) if path is not None else DEFAULT_PATH
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    if data.get("schema") != SCHEMA:
        raise ValueError(f"{path}: unknown schema {data.get('schema')!r}; expected {SCHEMA!r}")
    out = {}
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        missing = [k for k in REQUIRED if k not in value]
        if missing:
            raise ValueError(f"{path}: preset {key} lacks {', '.join(missing)}")
        if len(value["width"]) != 7 or len(value["height"]) != 7:
            raise ValueError(f"{path}: preset {key} needs 7 width and 7 height stations")
        out[key] = dict(value, id=key)
    return out


def get_preset(name: str, path=None) -> dict:
    presets = load_presets(path)
    if name not in presets:
        raise ValueError(f"unknown cavity preset {name!r}; known: {', '.join(sorted(presets))}")
    return presets[name]
