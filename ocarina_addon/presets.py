"""Reads the cavity presets (presets/cavity_presets.toml). Standard library only."""
from __future__ import annotations

import pathlib
import tomllib

SCHEMA = "ocarina-cavity-presets-v1"
DEFAULT_PATH = pathlib.Path(__file__).resolve().parent / "presets" / "cavity_presets.toml"
REQUIRED = ("width", "height", "exponent", "bend_deg", "port_u", "port_angle_deg", "layout")
VARIANTS_SCHEMA = "ocarina-preset-variants-v1"
VARIANTS_PATH = DEFAULT_PATH.parent / "variants.toml"
VARIANT_RULE_KEYS = ("windway_length_mm",)          # [voicing_rules] values a variant may replace for its own body


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


def load_variants(path=None, presets=None) -> dict:
    """Return {variant name: dict}: each a preset of cavity_presets.toml (its key `base`) with some values replaced
    (presets/variants.toml). A variant is an option for one body, not a rule; the six presets stay what they are."""
    path = pathlib.Path(path) if path is not None else VARIANTS_PATH
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    if data.get("schema") != VARIANTS_SCHEMA:
        raise ValueError(f"{path}: unknown schema {data.get('schema')!r}; expected {VARIANTS_SCHEMA!r}")
    presets = presets if presets is not None else load_presets()
    out = {}
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        if value.get("base") not in presets:
            raise ValueError(f"{path}: variant {key} needs `base`, one of {', '.join(sorted(presets))}")
        out[key] = dict(presets[value["base"]], **value, id=key)
    return out


def get_preset(name: str, path=None) -> dict:
    presets = load_presets(path)
    if name in presets:
        return presets[name]
    variants = load_variants(presets=presets) if path is None else {}
    if name not in variants:
        raise ValueError(f"unknown cavity preset {name!r}; known: {', '.join(sorted(presets) + sorted(variants))}")
    return variants[name]


def params_for(preset: dict, params: dict) -> dict:
    """The parameters with the rule values a variant sets replaced (VARIANT_RULE_KEYS); `params` itself when it sets
    none. Such a value is in the voicing hash, so the variant's hash names it."""
    over = {k: preset[k] for k in VARIANT_RULE_KEYS if preset.get(k) is not None}
    if not over:
        return params
    return dict(params, voicing_rules=dict(params["voicing_rules"], **{k: float(x) for k, x in over.items()}))
