"""Reads the cavity presets (presets/cavity_presets.toml) and resolves a variant's voicing. Standard library only (the
kernel through kernel_bridge): calibration, sizing and tests use it without Blender."""
from __future__ import annotations

import dataclasses
import hashlib
import json
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


CONE_WIDEN_DEFAULT_MM = 2.5    # "cone" cut: how far each side of the window opens at the outer face

# The build of the voicing is part of the kernel's record since 2026-11-18 (kernel/voicing.py, BUILD_FIELDS), and of
# its hash. A preset key on the left overrides the record field on the right for one variant build; body.build_body
# puts the override INTO the record (kernel voicing.with_build), so the hash of a variant is the hash of what was built.
RECORD_KEYS = {"window_cut": "window_cut", "cone_widen_mm": "cut_widen_mm", "shelf_angle_deg": "shelf_angle_deg",
               "windway_pitch_deg": "windway_pitch_deg", "pocket_blend_radius_mm": "pocket_blend_radius_mm",
               "stub_style": "stub_style", "stub_pitch_deg": "stub_pitch_deg",
               **{k: k for k in ("bowl_half_length_mm", "bowl_centre_xw_mm", "bowl_half_width_mm", "bowl_depth_mm",
                                 "bowl_floor_exponent", "bowl_rim_exponent", "bowl_under_mm", "bowl_roof_mm", "bowl_smooth_mm",
                                 "bowl_flow_mm", "bowl_flow_floor_mm", "bowl_flow_out_mm", "bowl_flow_cap", "bowl_flow_smooth",
                                 "bowl_rim_round_mm", "bowl_rim_out_mm", "bowl_grid_mm")}}
# Voicing settings that are NOT in the record or in the hash (the old note "no preset uses them" no longer holds: the
# variant P4-bowl sets the neck's and pocket_back_margin_mm). They shape the air and plastic next to the window, so a
# fitted eta_w is matched on them too (calibration_context).
UNHASHED_KEYS = ("block_front_mm", "shelf_land_mm", "neck_base_width_mm", "neck_base_depth_mm", "neck_side_wall_mm",
                 "cone_flare_exponent", "neck_cover_mm", "neck_cover_exit_mm", "neck_depth_exponent", "neck_width_exponent",
                 "neck_floor_mm", "neck_corner_cover_mm", "neck_tilt_deg", "pocket_back_margin_mm")


def record_overrides(preset, v) -> dict:
    """The build fields of the record that a preset (a variant build) replaces: record field -> value.

    An override replaces the named field and nothing else, with two exceptions that keep a variant buildable:
    cone_widen_share (the sideways opening as a share of the window width) becomes cut_widen_mm and wins over
    cone_widen_mm; and a change of the cut to "fan" drops the shelf, to "cone" or "ellipse" on a plain record gives
    the default opening."""
    out = {}
    for key, name in RECORD_KEYS.items():
        if preset.get(key) is not None:
            out[name] = str(preset[key]) if name in ("window_cut", "stub_style") else float(preset[key])
    if preset.get("cone_widen_share") is not None:
        out["cut_widen_mm"] = float(preset["cone_widen_share"]) * v.window_width_mm
    cut = out.get("window_cut", v.window_cut)
    if cut == "fan" and "shelf_angle_deg" not in out:
        out["shelf_angle_deg"] = 0.0
    if cut != "fan" and "cut_widen_mm" not in out and v.window_cut == "fan":
        out["cut_widen_mm"] = CONE_WIDEN_DEFAULT_MM
    return {name: value for name, value in out.items() if getattr(v, name) != value}


def options_from(preset) -> dict:
    """The prototype settings of a variant build that are not in the voicing record (UNHASHED_KEYS)."""
    return {key: float(preset[key]) for key in UNHASHED_KEYS if preset.get(key) is not None}


SHELL_KEYS = ("wall_front_less_mm", "wall_back_more_mm", "wall_refine_mm")       # the shell around the window too
NOT_LAYOUT_KEYS = ("id", "name", "note", "base", "rating", "windway_length_mm", "window_throat_mm", "cone_widen_share")


def _signature(values: dict) -> str:
    return hashlib.sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]


def calibration_context(preset: dict, edited_shell: bool = False, identity: dict | None = None) -> dict:
    """What a fitted constant depends on beyond the voicing hash, as signatures of the preset (written to the measurement
    template, kept by the fitter, compared by kernel calibration.size_body_from_calibration):

    voicing_context  the voicing settings that are not hashed (options_from: the neck, the pocket's back margin ...), the
                     shell's walls around the window (SHELL_KEYS) and whether the shell was edited by hand. A measured
                     eta_w is matched on it as well as on the voicing hash.
    layout           every other preset value (cavity stations, port, hole layout, thumb offsets, walls, hole rims) and the
                     edited flag: the position factors of a shape are matched on it.
    window_throat    the model's convention for the window: "wall" (the rule) or "effective" (window_throat_mm).

    An edited shell (edited_shell) is identified by `identity` (shell_edit.calibration_identity: per region, None where
    its outside is the plain build's, else a fingerprint of the edited outside there). A region left as the plain build
    has the plain signature, so its constants match exactly; an edited one has "edited:" + a signature that includes the
    fingerprint, which matches only the same edit. Without an identity both carry the reserved "unverified:" prefix:
    calibration never treats them as exact or as a context-free legacy match."""
    voicing = dict(options_from(preset), **{k: preset[k] for k in SHELL_KEYS if preset.get(k)})
    layout = {k: v for k, v in preset.items() if k not in NOT_LAYOUT_KEYS and k not in RECORD_KEYS and k not in UNHASHED_KEYS}

    def sign(values, region):
        if not edited_shell:
            return _signature(dict(values, edited_shell=False))
        if identity is None:
            return "unverified:" + _signature(dict(values, edited_shell=True))
        if identity[region] is None:
            return _signature(dict(values, edited_shell=False))
        return "edited:" + _signature(dict(values, edited_shell=True, outside=identity[region]))
    return dict(voicing_context=sign(voicing, "voicing"), layout=sign(layout, "layout"),
                window_throat="wall" if preset.get("window_throat_mm") is None else "effective")


def resolve_voicing(preset: dict, v0_cm3: float, params: dict, rating: str | None = None,
                    wall_at_window_mm: float | None = None):
    """The voicing record that body.build_body builds for `preset` at v0_cm3, with the eta_w prior: the variant's rule
    values (params_for), its rating unless `rating` is given, and its build fields (record_overrides). Fitted constants
    are looked up under this record's hash, so a calibrated sizing starts from it (calibrated_sizing_fn)."""
    from . import kernel_bridge
    k = kernel_bridge.kernel()
    v = k.voicing.make_voicing(float(v0_cm3), rating or preset.get("rating"), wall_at_window_mm, params=params_for(preset, params))
    over = record_overrides(preset, v)
    return k.voicing.with_build(v, **over) if over else v


def resolve_sizing(preset: dict, sz):
    """The sizing record `sz` with the variant's build fields put into its voicing (record_overrides). A record sized
    from fitted constants must carry them already: the constants were looked up under its voicing's hash, and changing
    that voicing afterwards would build a window they were not looked up for. Such a record raises ValueError."""
    over = record_overrides(preset, sz.voicing)
    if not over:
        return sz
    if getattr(sz, "eta_w_source", "prior") != "prior":
        raise ValueError(f"the sizing used fitted constants looked up for voicing {sz.voicing.version_hash}, but the variant "
                         f"replaces {', '.join(sorted(over))}: size it from the resolved voicing (presets.resolve_voicing)")
    from . import kernel_bridge
    return dataclasses.replace(sz, voicing=kernel_bridge.kernel().voicing.with_build(sz.voicing, **over))


def calibrated_sizing_fn(cal, preset: dict, v0_cm3: float, params: dict, *, rating: str | None = None,
                         wall_at_window_mm: float | None = None, edited_shell: bool = False, identity: dict | None = None,
                         info: dict | None = None, **kw):
    """A body.build_body sizing_fn(L_int_mm, walls=None) that sizes `preset` from fitted constants `cal`.

    The voicing is resolved once (resolve_voicing) and handed to the kernel (calibration.size_body_from_calibration,
    voicing=...): its own hash is looked up, and its window is kept whether eta_w is measured or the fallback. `walls`
    (hole name -> mm, the walls measured at the holes of an uneven or edited shell) go to the hole sizing on every call.
    The position factors are those of the preset's own id: a variant whose thumb hole moved does not take its base's.
    The build's calibration_context goes with every lookup (edited_shell: the shell was edited by hand; identity: what
    shell_edit.calibration_identity measured on it), and so does the
    preset's window_throat_mm, which the kernel refuses for constants fitted with the wall as the throat.
    `info`, a dict, receives the kernel's calibration info; kw go to size_body_from_calibration."""
    from . import kernel_bridge
    k = kernel_bridge.kernel()
    P = params_for(preset, params)
    v = resolve_voicing(preset, v0_cm3, P, rating, wall_at_window_mm)
    context = calibration_context(preset, edited_shell, identity)

    def sizing_fn(L_int_mm, walls=None):
        sz, i = k.calibration.size_body_from_calibration(cal, float(v0_cm3), voicing=v, shape=preset.get("id", "custom"),
                                                         L_int_mm=L_int_mm, params=P, wall_at_holes_mm=walls, context=context,
                                                         throat_mm=preset.get("window_throat_mm"), **kw)
        if info is not None:
            info.update(i)
        return sz
    return sizing_fn
