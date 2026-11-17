"""Fitted-constants file (C2): what the Stage 3 generator reads.

Written by the fitter, read by sizing. One TOML file. Constants are stored per voicing hash
(eta_w) and per shape (position factors). A fit on synthetic input writes `synthetic = true`
and a banner; the reader keeps the flag, so synthetic constants cannot pass for real ones.

    [acoustics]        k_window (fixed), k_hole, k_hole_sigma, eta_w_fallback, hole_offset_mm, volume_factor,
                       and both estimates of k_hole: k_hole_source ("profile" or "convention"),
                       k_hole_profile with its interval, k_hole_convention (see fitter.py)
    [temperature]      the internal-air rule that the fit used. Sizing must use the same rule.
    [breath]           p0_pa, alpha
    [voicing."<hash>"] eta_w, sigma, n_bodies, window_area_mm2, wall_at_window_mm, bodies
    [position_factors.<shape>]   one number per hole name
    [fit]              provenance: bodies, reference shape, pooled psi = 1 residual (the Gate 2 number)

Doc 04 "Outputs" maps to: eta_w per voicing hash, k_hole, hole_offset_mm, volume_factor, position
factors, and (in `size_body_from_calibration`) the largest volume that passes the round-hole verdict.
"""
from __future__ import annotations

import math
import pathlib
import tomllib
from dataclasses import dataclass, field

import config
import measurements as meas
import ocarina_kernel as ok
import sizing
import voicing as voicing_mod

SCHEMA = "ocarina-calibration-v1"


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

    def eta_w_for(self, voicing_hash: str):
        """(eta_w, source) where source is "measured" for a hash that was printed, else "fallback"."""
        v = self.voicings.get(voicing_hash)
        if v is not None:
            return v["eta_w"], "measured"
        return self.eta_w_fallback, "fallback"

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
        psi_geomean_reference=getattr(fit, "psi_geomean_reference", None))


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
                f"wall_at_window_mm = {tv(v['wall_at_window_mm'])}", f"bodies = {tv(v['bodies'])}", ""]
    for shape, tbl in cal.psi.items():
        out.append(f"[position_factors.{meas.toml_key(shape)}]")
        for n, v in tbl.items():
            out.append(f"{meas.toml_key(n)} = {tv(v)}")
        out.append("")
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
        k_hole_convention=a.get("k_hole_convention"), psi_geomean_reference=a.get("psi_geomean_reference"))


# --------------------------------------------------------------------------
# Stage 3: size a body from fitted constants
# --------------------------------------------------------------------------

def size_body_from_calibration(cal: Calibration, v0_cm3: float, rating: str | None = None,
                               wall_at_window_mm: float | None = None, labium_offset_mm: float | None = None, *,
                               shape: str = "P0", retarget_volume: bool = False, voicing_v0_cm3: float | None = None,
                               L_int_mm: float | None = None, params: dict | None = None, **kw):
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
    """
    P = params if params is not None else config.load_params()
    vo0 = voicing_mod.make_voicing(voicing_v0_cm3 if voicing_v0_cm3 is not None else v0_cm3, rating,
                                   wall_at_window_mm, labium_offset_mm, params=P)
    eta, source = cal.eta_w_for(vo0.version_hash)
    names = [h["name"] for h in P["fingering"]["holes"]]
    common = dict(params=P, ks={"fitted": cal.k_hole}, psi=cal.psi_list(shape, names), volume_factor=cal.volume_factor,
                  hole_offset_mm=cal.hole_offset_mm, L_int_mm=L_int_mm, **kw)
    if source == "measured":
        body = sizing.size_body(None if retarget_volume else v0_cm3, voicing=vo0, eta_w=eta, **common)
    else:
        vo = voicing_mod.make_voicing(v0_cm3, rating, wall_at_window_mm, labium_offset_mm, eta_w=eta, params=P)
        body = sizing.size_body(v0_cm3, voicing=vo, eta_w=eta, **common)
    unresolved = set(cal.fit.get("psi_unresolved", []) or [])
    missing = [n for n in names if n not in cal.psi.get(shape, {}) or f"{shape}/{n}" in unresolved]
    info = dict(eta_w=eta, eta_w_source=source, voicing_hash=body.voicing.version_hash, synthetic=cal.synthetic,
                k_hole=cal.k_hole, shape=shape, shape_known=shape in cal.psi, psi_defaulted_to_1=missing,
                warnings=([f"shape {shape!r} has no fitted position factors: psi = 1 for every hole"] if shape not in cal.psi else [])
                + ([f"psi = 1 (not fitted) for: {', '.join(missing)}"] if missing and shape in cal.psi else [])
                + ([] if source == "measured" else ["voicing hash was never measured: eta_w_fallback used"]))
    return body, info
