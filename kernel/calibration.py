"""Fitted-constants file (C2): what the Stage 3 generator reads.

Written by the fitter, read by sizing. One TOML file. Constants are stored per voicing hash
(eta_w) and per shape (position factors). A fit on synthetic input writes `synthetic = true`
and a banner; the reader keeps the flag, so synthetic constants cannot pass for real ones.

    [acoustics]        k_window (fixed), k_hole, k_hole_sigma, eta_w_fallback, hole_offset_mm, volume_factor,
                       and both estimates of k_hole: k_hole_source ("profile" or "convention"),
                       k_hole_profile with its interval, k_hole_convention (see fitter.py)
    [temperature]      the internal-air rule that the fit used. Sizing must use the same rule.
    [breath]           p0_pa, alpha
    [voicing."<hash>"] eta_w, sigma, n_bodies, window_area_mm2, wall_at_window_mm, bodies, and voicing_context when
                       every body of that hash named the same one (measurement files' [context])
    [position_factors.<shape>]   one number per hole name
    [layouts]          shape -> the layout signature its bodies shared (when they all named one)
    [model]            window_throat: the window's conductance with its wall as the throat ("wall", the only convention
                       the fitter has). A file without [model] or contexts is legacy: matched on the hash alone.
    [fit]              provenance: bodies, reference shape, pooled psi = 1 residual (the Gate 2 number)

Doc 04 "Outputs" maps to: eta_w per voicing hash, k_hole, hole_offset_mm, volume_factor, position
factors, and (in `size_body_from_calibration`) the largest volume that passes the round-hole verdict.
"""
from __future__ import annotations

import math
import pathlib
import tomllib
import dataclasses
from dataclasses import dataclass, field

import config
import measurements as meas
import ocarina_kernel as ok
import sizing
import voicing as voicing_mod

SCHEMA = "ocarina-calibration-v1"


def _unverified_context(value: str | None) -> bool:
    """Reserved signature prefix for edited shells whose actual geometry has not been identified.

    Kept in measurement and calibration files so neither side can silently regain an exact/legacy match.
    """
    return value is not None and value.startswith("unverified:")


def _hand_edited(value: str | None) -> bool:
    """A hand-edited shell: unidentified ("unverified:") or identified by its measured outside ("edited:", the add-on's
    shell_edit.calibration_identity). An identified edit matches an equal signature only, never a file that names none."""
    return value is not None and value.startswith(("unverified:", "edited:"))


@dataclass
class Calibration:
    synthetic: bool
    k_window: float
    k_hole: float
    k_hole_sigma: float | None
    eta_w_fallback: float
    hole_offset_mm: float
    volume_factor: float
    internal_air: dict
    breath: dict | None
    voicings: dict            # hash -> dict(eta_w, sigma, n_bodies, window_area_mm2, wall_at_window_mm, bodies)
    psi: dict                 # shape -> {hole name -> psi}
    fit: dict                 # provenance
    source: str = ""
    # Both estimates of k_hole (fitter.py). k_hole above is the one that drives psi and the diameters.
    k_hole_source: str = "convention"
    k_hole_profile: float | None = None
    k_hole_profile_lo: float | None = None
    k_hole_profile_hi: float | None = None
    k_hole_convention: float | None = None
    psi_geomean_reference: float | None = None
    layouts: dict = field(default_factory=dict)     # shape -> layout signature of the bodies its psi were fitted on
    model: dict = field(default_factory=dict)       # {"window_throat": "wall"}; {} in a legacy file (the wall, assumed)

    def eta_w_for(self, voicing_hash: str, voicing_context: str | None = None, allow_transfer: bool = False):
        """(eta_w, source) where source is "measured" for a hash that was printed (and, when both sides name one, in the
        same voicing context), else "fallback". See eta_w_match."""
        eta, match = self.eta_w_match(voicing_hash, voicing_context, allow_transfer)
        return eta, ("fallback" if match == "fallback" else "measured")

    def eta_w_match(self, voicing_hash: str, voicing_context: str | None = None, allow_transfer: bool = False):
        """(eta_w, match). match: "exact" (the hash and the voicing context both recorded and equal), "legacy" (the hash
        alone: the file or the caller names no context), "transfer" (measured in another context, taken only with
        allow_transfer: an experiment), "fallback" (never measured, or in another context).
        An unverified edited-shell context on either side requires transfer even if signatures are equal or absent; an
        identified edit ("edited:") matches exactly, but never as legacy."""
        v = self.voicings.get(voicing_hash)
        if v is None:
            return self.eta_w_fallback, "fallback"
        have = v.get("voicing_context")
        if _unverified_context(have) or _unverified_context(voicing_context):
            return (v["eta_w"], "transfer") if allow_transfer else (self.eta_w_fallback, "fallback")
        if have is None or voicing_context is None:
            if _hand_edited(have) or _hand_edited(voicing_context):
                return (v["eta_w"], "transfer") if allow_transfer else (self.eta_w_fallback, "fallback")
            return v["eta_w"], "legacy"
        if have == voicing_context:
            return v["eta_w"], "exact"
        return (v["eta_w"], "transfer") if allow_transfer else (self.eta_w_fallback, "fallback")

    def psi_match(self, shape: str, layout: str | None = None) -> str:
        """"exact", "legacy" (no layout recorded or none given), "unfitted" (no factors for the shape) or "other layout"
        (the shape's bodies had another hole layout: its factors do not apply). "unverified layout" means an edited
        shell's geometry is unidentified on either side, or an identified edit meets a side that names no layout; its
        factors do not apply, even with allow_transfer for eta_w."""
        if shape not in self.psi:
            return "unfitted"
        have = self.layouts.get(shape)
        if _unverified_context(have) or _unverified_context(layout):
            return "unverified layout"
        if have is None or layout is None:
            return "unverified layout" if _hand_edited(have) or _hand_edited(layout) else "legacy"
        return "exact" if have == layout else "other layout"

    def psi_list(self, shape: str, hole_names) -> list:
        """Position factors in the order of hole_names. Missing shape or hole: 1.0."""
        tbl = self.psi.get(shape, {})
        return [float(tbl.get(n, 1.0)) for n in hole_names]


def calibration_from_fit(fit, bodies, params: dict | None = None) -> Calibration:
    """Build the constants record from a fitter.FitResult and the BodyMeasurement list it was fitted on."""
    by_hash = {}
    for b in bodies:
        by_hash.setdefault(b.voicing_hash, b)
    voicings = {}
    for h, d in fit.eta_w_by_hash.items():
        b = by_hash[h]
        voicings[h] = dict(eta_w=d["eta_w"], sigma=d["sigma"], n_bodies=d["n"], window_area_mm2=b.window_area_mm2,
                           wall_at_window_mm=b.wall_at_window_mm, bodies=list(d["bodies"]))
    for h, entry in voicings.items():
        if (vc := _shared_context(bodies, "voicing_context", lambda b, h=h: b.voicing_hash == h, f"voicing {h}")) is not None:
            entry["voicing_context"] = vc
    layouts = {}
    for shape in fit.psi:
        if (lay := _shared_context(bodies, "layout", lambda b, s=shape: b.shape == s, f"shape {shape}")) is not None:
            layouts[shape] = lay
    psi = {shape: {n: (v if v is not None else 1.0) for n, v in tbl.items()} for shape, tbl in fit.psi.items()}
    unresolved = sorted(f"{shape}/{n}" for shape, tbl in fit.psi.items() for n, v in tbl.items() if v is None)
    pp = fit.pooled_psi1
    fitinfo = dict(bodies=[b.id for b in fit.bodies], reference_shape=fit.reference_shape, share=fit.share,
                   pooled_psi1_rms_cents=pp.rms_cents if pp else None, pooled_psi1_k_hole=pp.k_hole if pp else None,
                   n_notes=pp.n_notes if pp else None, sigma_mode="pooled",
                   psi_unresolved=unresolved or None)
    return Calibration(
        synthetic=fit.synthetic, k_window=ok.K_WINDOW, k_hole=fit.k_hole, k_hole_sigma=fit.k_hole_sigma,
        eta_w_fallback=fit.eta_w_fallback, hole_offset_mm=fit.hole_offset_mm or 0.0,
        volume_factor=fit.volume_factor or 1.0, internal_air=dict(fit.internal_air), breath=fit.breath,
        voicings=voicings, psi=psi, fit=fitinfo,
        k_hole_source=getattr(fit, "k_hole_source", "convention"),
        k_hole_profile=pr.k_hole if (pr := getattr(fit, "k_hole_profile", None)) is not None and pr.informative else None,
        k_hole_profile_lo=pr.lo if pr is not None and pr.informative else None,
        k_hole_profile_hi=pr.hi if pr is not None and pr.informative else None,
        k_hole_convention=getattr(fit, "k_hole_convention", None),
        psi_geomean_reference=getattr(fit, "psi_geomean_reference", None),
        layouts=layouts, model={"window_throat": "wall"})


def _shared_context(bodies, key: str, belongs, what: str):
    """The context value `key` that every body for which belongs(b) names; None when one of them names none (legacy).
    Bodies that name different ones were not built alike: pooling them would be wrong, so that raises ValueError."""
    seen = [getattr(b, "context", {}).get(key) for b in bodies if belongs(b)]
    known = set(seen) - {None}
    if len(known) > 1:
        raise ValueError(f"{what}: the bodies were built in different contexts ({key} {', '.join(sorted(known))}): fit them apart")
    # A legacy input must not erase the mark of a hand-edited shell.
    return known.pop() if known and (None not in seen or any(_hand_edited(v) for v in known)) else None


def _opt(d: dict, key, value):
    if value is not None:
        d[key] = value


def write_calibration(path, cal: Calibration) -> str:
    tv = meas.toml_value
    out = []
    if cal.synthetic:
        out += ["# SYNTHETIC CONSTANTS. Fitted from synthetic (invented) measurement files.",
                "# Nothing here describes a real printed body. Use only to test the Stage 3 generator.", ""]
    out += [f"schema = {tv(SCHEMA)}", f"synthetic = {tv(cal.synthetic)}", ""]
    out += ["[acoustics]", f"k_window = {tv(cal.k_window)}   # fixed", f"k_hole = {tv(cal.k_hole)}"]
    if cal.k_hole_sigma is not None:
        out.append(f"k_hole_sigma = {tv(cal.k_hole_sigma)}")
    out.append(f"k_hole_source = {tv(cal.k_hole_source)}   # which estimate k_hole is: profile (k compared against the data) or convention (mean psi = 1)")
    if cal.k_hole_profile is not None:
        out.append(f"k_hole_profile = {tv(cal.k_hole_profile)}")
        out.append(f"k_hole_profile_interval = {tv([cal.k_hole_profile_lo, cal.k_hole_profile_hi])}")
    if cal.k_hole_convention is not None:
        out.append(f"k_hole_convention = {tv(cal.k_hole_convention)}")
    if cal.psi_geomean_reference is not None:
        out.append(f"psi_geomean_reference = {tv(cal.psi_geomean_reference)}   # geometric mean of the reference-shape psi at k_hole")
    out += [f"eta_w_fallback = {tv(cal.eta_w_fallback)}   # for a voicing hash that was never printed",
            f"hole_offset_mm = {tv(cal.hole_offset_mm)}   # printed minus designed diameter",
            f"volume_factor = {tv(cal.volume_factor)}   # printed / designed capped volume", ""]
    out += ["[temperature]   # internal-air rule used by the fit; sizing must use the same rule"]
    for k, v in cal.internal_air.items():
        out.append(f"{meas.toml_key(k)} = {tv(float(v))}")
    out.append("")
    if cal.breath:
        out += ["[breath]", f"p0_pa = {tv(cal.breath['p0_pa'])}", f"alpha = {tv(cal.breath['alpha'])}", ""]
    for h, v in cal.voicings.items():
        out += [f"[voicing.{meas.toml_key(h)}]", f"eta_w = {tv(v['eta_w'])}"]
        if v.get("sigma") is not None:
            out.append(f"sigma = {tv(v['sigma'])}")
        out += [f"n_bodies = {tv(v['n_bodies'])}", f"window_area_mm2 = {tv(v['window_area_mm2'])}",
                f"wall_at_window_mm = {tv(v['wall_at_window_mm'])}", f"bodies = {tv(v['bodies'])}"]
        if v.get("voicing_context") is not None:
            out.append(f"voicing_context = {tv(v['voicing_context'])}")
        out.append("")
    for shape, tbl in cal.psi.items():
        out.append(f"[position_factors.{meas.toml_key(shape)}]")
        for n, v in tbl.items():
            out.append(f"{meas.toml_key(n)} = {tv(v)}")
        out.append("")
    if cal.layouts:
        out.append("[layouts]   # the hole layout (signature) that each shape's position factors were fitted on")
        out += [f"{meas.toml_key(s)} = {tv(sig)}" for s, sig in cal.layouts.items()] + [""]
    if cal.model:
        out += ["[model]   # the conventions the constants were fitted under"]
        out += [f"{meas.toml_key(k)} = {tv(v)}" for k, v in cal.model.items()] + [""]
    out.append("[fit]")
    for k, v in cal.fit.items():
        if v is not None:
            out.append(f"{meas.toml_key(k)} = {tv(v)}")
    out.append("")
    text = "\n".join(out)
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(text, encoding="utf-8")
    return text


def load_calibration(path) -> Calibration:
    path = pathlib.Path(path)
    with open(path, "rb") as fh:
        d = tomllib.load(fh)
    if d.get("schema") != SCHEMA:
        raise ValueError(f"unknown schema {d.get('schema')!r}; expected {SCHEMA!r}")
    a = d["acoustics"]
    return Calibration(
        synthetic=bool(d.get("synthetic", False)), k_window=a["k_window"], k_hole=a["k_hole"],
        k_hole_sigma=a.get("k_hole_sigma"), eta_w_fallback=a["eta_w_fallback"], hole_offset_mm=a["hole_offset_mm"],
        volume_factor=a["volume_factor"], internal_air=dict(d.get("temperature", {})), breath=d.get("breath"),
        voicings={h: dict(v) for h, v in d.get("voicing", {}).items()},
        psi={s: dict(t) for s, t in d.get("position_factors", {}).items()}, fit=dict(d.get("fit", {})), source=str(path),
        k_hole_source=a.get("k_hole_source", "convention"), k_hole_profile=a.get("k_hole_profile"),
        k_hole_profile_lo=(a.get("k_hole_profile_interval") or [None, None])[0],
        k_hole_profile_hi=(a.get("k_hole_profile_interval") or [None, None])[1],
        k_hole_convention=a.get("k_hole_convention"), psi_geomean_reference=a.get("psi_geomean_reference"),
        layouts=dict(d.get("layouts", {})), model=dict(d.get("model", {})))


# --------------------------------------------------------------------------
# Stage 3: size a body from fitted constants
# --------------------------------------------------------------------------

def size_body_from_calibration(cal: Calibration, v0_cm3: float, rating: str | None = None,
                               wall_at_window_mm: float | None = None, labium_offset_mm: float | None = None, *,
                               shape: str = "P0", retarget_volume: bool = False, voicing_v0_cm3: float | None = None,
                               L_int_mm: float | None = None, params: dict | None = None,
                               voicing: voicing_mod.Voicing | None = None, context: dict | None = None,
                               allow_transfer: bool = False, **kw):
    """Size a body with fitted constants. Returns (BodySizing, info).

    The voicing is built from (voicing_v0_cm3 or v0_cm3, rating, wall, labium offset) with the prior eta_w,
    exactly as in round 1. Two cases follow.

    Known hash (that voicing was printed and measured): the window is KEPT. eta_w is the measured value.
      retarget_volume=False keeps v0_cm3 (A4 then errs by the amount the measured eta_w says: see
      `BodySizing.a4_error_cents`). retarget_volume=True solves V0 so that A4 is on pitch.
    Unknown hash (for example P0 at 88 cm3, the prediction body, never printed): the window is re-solved with eta_w_fallback,
      so A4 is on pitch at v0_cm3 by construction.

    Holes use k_hole, the position factors of `shape`, and the hole offset; the cavity mesh volume uses the
    volume factor. Inward tubes are planned again at the fitted k. A round-1 tube can then change length or
    disappear, and the fitted position factor belonged to the old chimney. To keep the printed tubes, pass the
    round-1 `tubes_mm` (it goes to size_body). `info["warnings"]` lists every silent default (psi = 1, fallback eta_w). Open question for the owner: retarget or keep V0 for a known hash (see notes).

    voicing   an already resolved record (a variant build: its bowl, pitch and other build fields; the add-on's
              presets.resolve_voicing), instead of the record that (voicing_v0_cm3 or v0_cm3, rating, wall, offset) make.
              Its own hash is looked up, and its window is kept in both cases: a measured eta_w or the fallback changes
              the A4 error (or V0, with retarget_volume), never the window that was designed. Give it or those
              arguments, not both. The legacy path above (no voicing) keeps re-solving an unknown window.
    context   the build's calibration context (the add-on's presets.calibration_context: voicing_context, layout). eta_w
              is taken only from an entry of the same voicing context ("exact"), or of none named ("legacy"); measured in
              another context it is the fallback, unless allow_transfer (an experiment: "transfer"). Position factors
              fitted on another or unverified layout are not used (psi = 1). Unidentified edited shells require explicit
              transfer for eta_w even with matching signatures or legacy constants; an identified edit ("edited:") matches
              an equal signature, never legacy constants. info["eta_w_match"] and info["psi_match"] say which.
    throat_mm (in kw, for size_body) is refused: the fitter's eta_w belongs to the window's wall as its throat.
    """
    P = params if params is not None else config.load_params()
    if voicing is not None:
        if any(x is not None for x in (rating, wall_at_window_mm, labium_offset_mm, voicing_v0_cm3)):
            raise ValueError("give the resolved voicing or the arguments that make one (rating, walls, offset, voicing V0), not both")
        vo0 = voicing
    else:
        vo0 = voicing_mod.make_voicing(voicing_v0_cm3 if voicing_v0_cm3 is not None else v0_cm3, rating,
                                       wall_at_window_mm, labium_offset_mm, params=P)
    ctx = dict(context or {})
    if kw.get("throat_mm") is not None and cal.model.get("window_throat", "wall") != "effective":
        raise ValueError("these constants were fitted with the window's wall as its throat (window_throat = wall): "
                         "refit them before sizing with an effective throat (window_throat_mm)")
    eta, eta_match = cal.eta_w_match(vo0.version_hash, ctx.get("voicing_context"), allow_transfer)
    source = "fallback" if eta_match == "fallback" else "measured"
    names = [h["name"] for h in P["fingering"]["holes"]]
    psi_match = cal.psi_match(shape, ctx.get("layout"))
    psi = cal.psi_list(shape, names) if psi_match in ("exact", "legacy") else [1.0] * len(names)
    common = dict(params=P, ks={"fitted": cal.k_hole}, psi=psi, volume_factor=cal.volume_factor,
                  hole_offset_mm=cal.hole_offset_mm, L_int_mm=L_int_mm, **kw)
    if source == "measured" or voicing is not None:
        body = sizing.size_body(None if retarget_volume else v0_cm3, voicing=vo0, eta_w=eta, **common)
    else:
        vo = voicing_mod.make_voicing(v0_cm3, rating, wall_at_window_mm, labium_offset_mm, eta_w=eta, params=P)
        body = sizing.size_body(v0_cm3, voicing=vo, eta_w=eta, **common)
    unresolved = set(cal.fit.get("psi_unresolved", []) or [])
    known = psi_match in ("exact", "legacy")
    missing = [n for n in names if not known or n not in cal.psi[shape] or f"{shape}/{n}" in unresolved]
    measured_elsewhere = eta_match == "fallback" and vo0.version_hash in cal.voicings
    unverified_voicing = any(_hand_edited(v) for v in
                             (ctx.get("voicing_context"), cal.voicings.get(vo0.version_hash, {}).get("voicing_context")))
    body = dataclasses.replace(body, eta_w_source=source)
    info = dict(eta_w=eta, eta_w_source=source, eta_w_match=eta_match, psi_match=psi_match, context=ctx,
                model=dict(cal.model), voicing_hash=body.voicing.version_hash, synthetic=cal.synthetic,
                k_hole=cal.k_hole, shape=shape, shape_known=known, psi_defaulted_to_1=missing,
                warnings=([f"shape {shape!r} has no fitted position factors: psi = 1 for every hole"] if psi_match == "unfitted" else [])
                + ([f"the position factors of shape {shape!r} were fitted on another hole layout: psi = 1 for every hole"]
                   if psi_match == "other layout" else [])
                + (["hand-edited shell: its layout is unidentified or the constants name none; psi = 1 for every hole"]
                   if psi_match == "unverified layout" else [])
                + ([f"psi = 1 (not fitted) for: {', '.join(missing)}"] if missing and known else [])
                + (["voicing hash was never measured: eta_w_fallback used"] if eta_match == "fallback" and not measured_elsewhere else [])
                + (["voicing context differs or is unverified: eta_w_fallback used"
                    if unverified_voicing
                    else "voicing measured in another voicing context: eta_w_fallback used"] if measured_elsewhere else [])
                + (["eta_w taken from another or unverified voicing context (allow_transfer: an experiment, not a match)"] if eta_match == "transfer" else []))
    return body, info
