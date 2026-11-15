"""Measurement fitter (C2). Standard library only.

Input: BodyMeasurement records (measurements.py): measured V0, measured hole diameters, room
temperature, and the 13 pitches (mean of 3 takes). Output: FitResult.

Model (kernel docs, doc 03 section 2). Note j opens holes 0..j-1 in order, so

    G_tot_j = (2 pi f_j / c)^2 * V_j,       V_j = V0 - sum_{i<j} A_i t_i
    X_w     = G_tot_0                       (this is eta_w * G_w)
    G_i     = G_tot_{i+1} - G_tot_i         (the effective conductance of hole i, alone)

Each hole is then compared with the model of an isolated hole,

    G_i = psi_i * A_i / (t_i + k_hole * d_eq_i),

where A_i is the MEASURED area and t_i the chimney (wall + tube). psi_i is the position factor.

Convention for k and psi (read this before using k_hole). k_hole and an overall scale on psi cannot be
separated. A uniform psi of 1.1 looks almost like a different k. The fitter therefore fixes the scale
of psi: the (unweighted) geometric mean of psi over the holes of the REFERENCE SHAPE is 1. k_hole is
then the end correction seen by an average hole of that shape. The position factors of the other
shapes are measured on the same k, so a whole-scale offset of P1-P3 against P0 shows up in their psi.
If the true psi do not have a geometric mean of 1, the fitted k absorbs the difference. The tests show
the size of that bias.

Gate 2 numbers. With psi free, one body has 13 pitches and 13 unknowns, so its residual is zero.
The honest numbers are the pooled psi = 1 residuals: one eta_w per voicing hash, one k_hole, psi = 1,
fitted over all bodies together (`FitResult.pooled_psi1`).

Noise. Pitch noise enters G_i through a difference of two totals, so the small holes are the noisiest.
A hole whose conductance comes out at or below zero is reported `resolved = False` and stays out of the
fit. The per-hole relative error is estimated from the spread of the takes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import holes as holes_mod
import measurements as meas
import ocarina_kernel as ok

MM = 1e-3
CM3 = 1e-6

SIGMA_DEFAULT_CENTS = 5.0       # per-note uncertainty of the mean when there is a single take
SIGMA_FLOOR_CENTS = 1.0         # never trust a note better than this


# --------------------------------------------------------------------------
# Small numerical helpers
# --------------------------------------------------------------------------

def _golden(f, lo: float, hi: float, tol: float = 1e-9, max_iter: int = 200) -> float:
    """Minimum of a unimodal function on [lo, hi]."""
    g = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = lo, hi
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(max_iter):
        if abs(b - a) < tol:
            break
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = f(d)
    return 0.5 * (a + b)


def _bisect(f, lo: float, hi: float, tol: float = 1e-13, max_iter: int = 200) -> float:
    """Root of an increasing function. Raises ValueError if f(lo) and f(hi) have the same sign."""
    flo, fhi = f(lo), f(hi)
    if flo > 0 or fhi < 0:
        raise ValueError("root is outside the search range")
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------
# Result records
# --------------------------------------------------------------------------

@dataclass
class HoleFit:
    name: str
    opens: str
    chimney_mm: float
    d_design_mm: float
    d_measured_mm: float
    G_eff_mm: float | None         # effective conductance from the pitches; None when unresolved
    G_sigma_rel: float | None
    resolved: bool
    G_model_mm: float              # isolated-hole model at the fitted k, psi = 1, measured d
    psi_body: float | None         # this body's G_eff / G_model
    psi: float | None              # shared position factor used for the corrected diameter
    d_needed_mm: float | None      # diameter that puts this note on pitch (physical size, measured scale)
    ream_mm: float | None          # d_needed - d_measured: positive = ream open, negative = too big, cannot be fixed
    d_cad_needed_mm: float | None  # d_needed - hole offset: what to draw in CAD for a reprint
    flags: list = field(default_factory=list)


@dataclass
class BodyFit:
    id: str
    shape: str
    voicing_hash: str
    synthetic: bool
    v0_cm3: float
    internal_temp_c: float
    c_m_s: float
    X_w_mm: float                  # eta_w * G_w from the all-closed note
    eta_w: float                   # X_w / G_w(window, k_window)
    a4_error_cents: float          # observed all-closed note against its target. Holes cannot fix this.
    holes: list
    rms_shared_psi_cents: float | None = None   # shared psi, own eta_w: do bodies of one shape agree?
    residual_shared_psi_cents: list = field(default_factory=list)
    rms_pooled_psi1_cents: float | None = None  # one eta_w per hash, one k, psi = 1
    residual_pooled_psi1_cents: list = field(default_factory=list)
    volume_factor: float = 1.0                  # measured V0 / target V0
    hole_offset_mm: float | None = None         # mean(measured - design) of this body
    corrected_ok: bool = True
    corrected_message: str = ""


@dataclass
class PooledPsi1:
    k_hole: float
    eta_w_by_hash: dict
    rms_cents: float
    n_notes: int


@dataclass
class FitResult:
    k_hole: float
    k_hole_sigma: float | None
    reference_shape: str
    share: str
    psi: dict                      # shape -> {hole name -> psi}   (psi = 1 if share == "none")
    eta_w_by_hash: dict            # hash -> {eta_w, sigma, n, X_w_mm_mean, bodies}
    eta_w_fallback: float          # mean of the per-hash eta_w, for a voicing that was never printed
    hole_offset_mm: float | None
    hole_offset_sigma_mm: float | None
    volume_factor: float | None
    volume_factor_sigma: float | None
    breath: dict | None            # p0_pa, alpha
    bodies: list
    pooled_psi1: PooledPsi1 | None
    synthetic: bool
    internal_air: dict             # the temperature rule used
    messages: list = field(default_factory=list)


# --------------------------------------------------------------------------
# Step 1: effective conductances of one body
# --------------------------------------------------------------------------

def _areas(body):
    return [math.pi * h.d_measured_m ** 2 / 4.0 for h in body.holes]


def effective_conductances(body, c: float, sigma_default=SIGMA_DEFAULT_CENTS, sigma_floor=SIGMA_FLOOR_CENTS):
    """Return (X_w, G_list, sigma_rel_list, G_tot_list). Lengths in metres.

    sigma_rel is the relative uncertainty of each hole conductance, from the take spread of the two notes
    that bracket it.
    """
    n = len(body.holes)
    if len(body.notes) != n + 1:
        raise ValueError(f"{body.id}: {len(body.notes)} notes for {n} holes; need one more note than holes")
    K = ok.TWO_PI ** 2 / (c * c)
    A = _areas(body)
    V = body.v0_m3
    G_tot, sig = [], []
    for j, note in enumerate(body.notes):
        if j > 0:
            V -= A[j - 1] * body.holes[j - 1].chimney_m
        G_tot.append(K * note.f_hz ** 2 * V)
        sem = note.cents_sem
        s_c = max(sem if sem is not None else sigma_default, sigma_floor)
        sig.append(2.0 * s_c / ok.CENTS_PER_LN)           # sigma of ln G_tot
    X = G_tot[0]
    G, sig_rel = [], []
    for i in range(n):
        g = G_tot[i + 1] - G_tot[i]
        G.append(g)
        dg = math.hypot(G_tot[i + 1] * sig[i + 1], G_tot[i] * sig[i])
        sig_rel.append(dg / g if g > 0 else None)
    return X, G, sig_rel, G_tot


def _hole_model_G(area: float, t: float, k: float) -> float:
    return ok.conductance(area, t, k)


# --------------------------------------------------------------------------
# Step 2: global fit
# --------------------------------------------------------------------------

def _group_key(share: str, shape: str, name: str, regions):
    if share == "shape":
        return (shape, name)
    if share == "region":
        if not regions or name not in regions:
            raise ValueError("share='region' needs a regions dict that maps every hole name to a region")
        return (shape, regions[name])
    if share == "none":
        return ("*", "*")
    raise ValueError(f"unknown share mode {share!r}")


def fit_bodies(bodies, params: dict | None = None, *, share: str = "shape", reference_shape: str | None = None,
               regions: dict | None = None, k_bounds=(0.05, 5.0), sigma_default=SIGMA_DEFAULT_CENTS,
               sigma_floor=SIGMA_FLOOR_CENTS, pooled_k_bounds=(0.3, 2.5)) -> FitResult:
    """Fit one or several bodies together.

    share      "shape": one position factor per (shape, hole name), shared by all bodies of that shape.
               "region": one per (shape, region), regions given as a dict hole name -> region.
               "none": psi = 1 for every hole; only k_hole is fitted.
    reference_shape  the shape whose psi have a geometric mean of 1 (default: the shape with most bodies).
    """
    bodies = list(bodies)
    if not bodies:
        raise ValueError("no bodies to fit")
    temp = (params or {}).get("temperature", {"design_internal_c": 27.0, "reference_room_c": 22.0, "room_coupling": 0.31})
    messages = []
    for b in bodies:
        if any(h.d_measured_m is None for h in b.holes):
            raise meas.MeasurementIncomplete([f"{b.id}: hole diameters not measured"])

    # --- per body: effective conductances
    per = []
    for b in bodies:
        c = b.c_m_s(params)
        X, G, sig_rel, G_tot = effective_conductances(b, c, sigma_default, sigma_floor)
        if X <= 0:
            raise ValueError(f"{b.id}: non-positive all-closed conductance; check V0 and the first pitch")
        per.append(dict(body=b, c=c, X=X, G=G, sig=sig_rel, A=_areas(b)))
        for h, g in zip(b.holes, G):
            if g <= 0:
                messages.append(f"{b.id}: hole {h.name} is unresolved (conductance {g / MM:+.3f} mm from the pitches)")

    # --- instances for the k / psi fit
    inst = []     # dicts: body index, hole index, y, w, lnA, t, deq, group
    for bi, p in enumerate(per):
        b = p["body"]
        for hi, h in enumerate(b.holes):
            g, s = p["G"][hi], p["sig"][hi]
            if g <= 0 or s is None or s <= 0:
                continue
            area = p["A"][hi]
            inst.append(dict(bi=bi, hi=hi, y=math.log(g), w=1.0 / (s * s), area=area, t=h.chimney_m,
                             deq=ok.d_eq(area), group=_group_key(share, b.shape, h.name, regions)))
    if not inst:
        raise ValueError("no resolved hole in any body")

    shapes = [b.shape for b in bodies]
    if reference_shape is None:
        reference_shape = max(sorted(set(shapes)), key=shapes.count)
    groups = {}
    for ii, x in enumerate(inst):
        groups.setdefault(x["group"], []).append(ii)
    ref_groups = [g for g in groups if share == "none" or g[0] == reference_shape]
    if not ref_groups:
        raise ValueError(f"reference shape {reference_shape!r} has no resolved holes")

    def lnpsi_groups(k):
        out = {}
        for g, idx in groups.items():
            sw = sum(inst[i]["w"] for i in idx)
            sr = sum(inst[i]["w"] * (inst[i]["y"] - math.log(ok.conductance(inst[i]["area"], inst[i]["t"], k))) for i in idx)
            out[g] = sr / sw
        return out

    # Each distinct hole of the reference shape counts once in the geometric mean, whatever its group.
    ref_holes = sorted({(per[x["bi"]]["body"].holes[x["hi"]].name, x["group"])
                        for g in ref_groups for x in (inst[i] for i in groups[g])}, key=lambda t: (t[0], str(t[1])))

    def norm(k):
        lp = lnpsi_groups(k)
        if share == "none":
            return lp[("*", "*")]
        return sum(lp[grp] for _, grp in ref_holes) / len(ref_holes)

    k_fit = _bisect(norm, *k_bounds)
    lp = lnpsi_groups(k_fit)
    if share == "none":
        psi_g = {g: 1.0 for g in groups}
    else:
        psi_g = {g: math.exp(v) for g, v in lp.items()}

    # uncertainty of k from the weights (linearised)
    k_sigma = None
    if share != "none":
        n = len(ref_holes)
        var_N = sum(1.0 / sum(inst[i]["w"] for i in groups[grp]) for _, grp in ref_holes) / (n * n)
        dNdk = sum(sum(inst[i]["w"] * inst[i]["deq"] / (inst[i]["t"] + k_fit * inst[i]["deq"]) for i in groups[grp])
                   / sum(inst[i]["w"] for i in groups[grp]) for _, grp in ref_holes) / n
    else:
        sw = sum(x["w"] for x in inst)
        var_N = 1.0 / sw
        dNdk = sum(x["w"] * x["deq"] / (x["t"] + k_fit * x["deq"]) for x in inst) / sw
    if dNdk > 0:
        k_sigma = math.sqrt(var_N) / dNdk

    psi_table = {}
    for b in bodies:
        tbl = psi_table.setdefault(b.shape, {})
        for h in b.holes:
            g = _group_key(share, b.shape, h.name, regions)
            tbl[h.name] = psi_g.get(g)       # None when the hole was unresolved in every body of the shape

    # --- eta_w per hash
    eta_by_hash = {}
    for p in per:
        b = p["body"]
        eta = p["X"] / b.window_G_w()
        d = eta_by_hash.setdefault(b.voicing_hash, dict(values=[], X=[], bodies=[]))
        d["values"].append(eta)
        d["X"].append(p["X"] / MM)
        d["bodies"].append(b.id)
    eta_out = {}
    for h, d in eta_by_hash.items():
        vals = d["values"]
        m = sum(vals) / len(vals)
        sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else None
        eta_out[h] = dict(eta_w=m, sigma=sd, n=len(vals), X_w_mm_mean=sum(d["X"]) / len(d["X"]), bodies=d["bodies"],
                          values=vals)
    eta_fallback = sum(v["eta_w"] for v in eta_out.values()) / len(eta_out)

    # --- offsets, volume factor
    offs = [(h.d_measured_m - h.d_design_m) / MM for b in bodies for h in b.holes]
    off_mean = sum(offs) / len(offs)
    off_sd = math.sqrt(sum((x - off_mean) ** 2 for x in offs) / (len(offs) - 1)) if len(offs) > 1 else None
    vfs = [b.v0_cm3 / b.target_v0_cm3 for b in bodies if b.target_v0_cm3 > 0]
    vf_mean = sum(vfs) / len(vfs) if vfs else None
    vf_sd = math.sqrt(sum((x - vf_mean) ** 2 for x in vfs) / (len(vfs) - 1)) if len(vfs) > 1 else None

    # --- pooled psi = 1 fit (Gate 2)
    pooled = _fit_pooled_psi1(per, pooled_k_bounds)
    res_pooled = _pooled_residuals(per, pooled.k_hole, pooled.eta_w_by_hash)

    # --- per-body records
    body_fits = []
    for bi, p in enumerate(per):
        b = p["body"]
        c, X = p["c"], p["X"]
        psi_here = [psi_table[b.shape].get(h.name) for h in b.holes]
        psi_use = [x if x is not None else 1.0 for x in psi_here]
        chim = [h.chimney_m for h in b.holes]
        dmeas = [h.d_measured_m for h in b.holes]
        # residual of the shared-psi model with this body's own eta_w
        pred = holes_mod.predict_scale(X, b.v0_m3, dmeas, chim, k_fit, c, psi_use)
        res_shared = [ok.cents(pf, n.f_hz) for pf, n in zip(pred, b.notes)]
        rms_shared = math.sqrt(sum(x * x for x in res_shared) / len(res_shared))
        # corrected diameters
        f_targets = [n.target_hz for n in b.notes]
        try:
            d_need, _ = holes_mod.solve_scale(f_targets, X, b.v0_m3, chim, k_fit, c, psi_use)
            corrected_ok, cmsg = True, ""
        except ValueError as exc:
            d_need, corrected_ok, cmsg = [None] * len(b.holes), False, str(exc)
        off_body = sum(h.d_measured_m - h.d_design_m for h in b.holes) / len(b.holes) / MM
        hfits = []
        for hi, h in enumerate(b.holes):
            g, s = p["G"][hi], p["sig"][hi]
            resolved = g > 0 and s is not None
            G_model = _hole_model_G(p["A"][hi], h.chimney_m, k_fit)
            flags = []
            if not resolved:
                flags.append("unresolved")
            if psi_here[hi] is None:
                flags.append("psi_unresolved")
            dn = d_need[hi]
            ream = (dn - h.d_measured_m) / MM if dn is not None else None
            if ream is not None and ream < -0.02:
                flags.append("too_big_cannot_ream")
            if dn is not None:
                limit = _pad_limit(h, params)
                if limit is not None and dn / MM > limit:
                    flags.append("above_pad_limit")
            hfits.append(HoleFit(
                name=h.name, opens=h.opens, chimney_mm=h.chimney_m / MM, d_design_mm=h.d_design_m / MM,
                d_measured_mm=h.d_measured_m / MM, G_eff_mm=g / MM if resolved else None,
                G_sigma_rel=s if resolved else None, resolved=resolved, G_model_mm=G_model / MM,
                psi_body=g / G_model if resolved else None, psi=psi_here[hi],
                d_needed_mm=dn / MM if dn is not None else None, ream_mm=ream,
                d_cad_needed_mm=(dn / MM - off_mean) if dn is not None else None, flags=flags))
        body_fits.append(BodyFit(
            id=b.id, shape=b.shape, voicing_hash=b.voicing_hash, synthetic=b.synthetic, v0_cm3=b.v0_cm3,
            internal_temp_c=b.internal_temp_c(params), c_m_s=c, X_w_mm=X / MM, eta_w=X / b.window_G_w(),
            a4_error_cents=ok.cents(b.notes[0].f_hz, b.notes[0].target_hz), holes=hfits,
            rms_shared_psi_cents=rms_shared, residual_shared_psi_cents=res_shared,
            rms_pooled_psi1_cents=math.sqrt(sum(x * x for x in res_pooled[bi]) / len(res_pooled[bi])),
            residual_pooled_psi1_cents=res_pooled[bi],
            volume_factor=b.v0_cm3 / b.target_v0_cm3 if b.target_v0_cm3 > 0 else 1.0,
            hole_offset_mm=off_body, corrected_ok=corrected_ok, corrected_message=cmsg))

    return FitResult(
        k_hole=k_fit, k_hole_sigma=k_sigma, reference_shape=reference_shape, share=share, psi=psi_table,
        eta_w_by_hash=eta_out, eta_w_fallback=eta_fallback, hole_offset_mm=off_mean, hole_offset_sigma_mm=off_sd,
        volume_factor=vf_mean, volume_factor_sigma=vf_sd, breath=_fit_breath(bodies), bodies=body_fits,
        pooled_psi1=pooled, synthetic=any(b.synthetic for b in bodies),
        internal_air=dict(temp), messages=messages)


def fit_body(body, params: dict | None = None, **kw) -> FitResult:
    """Fit a single body. psi is then the residual of each hole against the k_hole of the mean hole."""
    return fit_bodies([body], params, **kw)


def _pad_limit(h, params):
    """Finger-pad limit in mm from the measurement's hole name, if params are given."""
    if not params:
        return None
    for spec in params.get("fingering", {}).get("holes", []):
        if spec["name"] == h.name:
            return float(spec["max_d_mm"])
    return None


# --------------------------------------------------------------------------
# Pooled psi = 1 fit: one eta_w per hash, one k_hole
# --------------------------------------------------------------------------

def _pooled_residuals(per, k, eta_by_hash):
    out = []
    for p in per:
        b = p["body"]
        eta = eta_by_hash[b.voicing_hash]
        out.append(_residuals_psi1(p, k, eta * b.window_G_w()))
    return out


def _residuals_psi1(p, k, X):
    b = p["body"]
    chim = [h.chimney_m for h in b.holes]
    pred = holes_mod.predict_scale(X, b.v0_m3, [h.d_measured_m for h in b.holes], chim, k, p["c"])
    return [ok.cents(pf, n.f_hz) for pf, n in zip(pred, b.notes)]


def _fit_pooled_psi1(per, k_bounds) -> PooledPsi1:
    hashes = sorted({p["body"].voicing_hash for p in per})
    by_hash = {h: [p for p in per if p["body"].voicing_hash == h] for h in hashes}

    def sse_eta(h, k, eta):
        return sum(sum(r * r for r in _residuals_psi1(p, k, eta * p["body"].window_G_w())) for p in by_hash[h])

    def best_eta(h, k):
        return _golden(lambda e: sse_eta(h, k, e), 0.2, 2.0, tol=1e-10)

    def total(k):
        return sum(sse_eta(h, k, best_eta(h, k)) for h in hashes)

    k = _golden(total, *k_bounds, tol=1e-9)
    etas = {h: best_eta(h, k) for h in hashes}
    n = sum(len(p["body"].notes) for p in per)
    return PooledPsi1(k_hole=k, eta_w_by_hash=etas, rms_cents=math.sqrt(total(k) / n), n_notes=n)


# --------------------------------------------------------------------------
# Breath curve: ln p = ln p0 + alpha * ln 2 * n / 12
# --------------------------------------------------------------------------

def _fit_breath(bodies):
    xs, ys = [], []
    for b in bodies:
        if not b.notes:
            continue
        m0 = meas.note_midi(b.notes[0].name)
        for n in b.notes:
            for p in n.pressures_pa:
                if p > 0:
                    xs.append((meas.note_midi(n.name) - m0) * math.log(2.0) / 12.0)
                    ys.append(math.log(p))
    if len(xs) < 3 or max(xs) == min(xs):
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    alpha = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return {"p0_pa": math.exp(my - alpha * mx), "alpha": alpha}


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def format_report(fit: FitResult) -> str:
    out = []
    if fit.synthetic:
        out += ["> **SYNTHETIC DATA.** At least one body in this fit is synthetic. Nothing here was measured.", ""]
    out += [f"## Fit of {len(fit.bodies)} body(ies)", ""]
    ks = f" ± {fit.k_hole_sigma:.3f}" if fit.k_hole_sigma is not None else ""
    out += [f"- k_hole = **{fit.k_hole:.4f}**{ks} (psi scale fixed: geometric mean of psi over the {fit.reference_shape} holes = 1)",
            f"- eta_w fallback (for a voicing never printed) = {fit.eta_w_fallback:.4f}"]
    for h, d in fit.eta_w_by_hash.items():
        sd = f" ± {d['sigma']:.4f}" if d["sigma"] is not None else ""
        out.append(f"- voicing `{h}`: eta_w = {d['eta_w']:.4f}{sd} from {d['n']} body(ies) ({', '.join(d['bodies'])}); eta_w·G_w = {d['X_w_mm_mean']:.4f} mm")
    if fit.hole_offset_mm is not None:
        sd = f" ± {fit.hole_offset_sigma_mm:.3f}" if fit.hole_offset_sigma_mm is not None else ""
        out.append(f"- hole offset (measured − design) = {fit.hole_offset_mm:+.3f}{sd} mm")
    if fit.volume_factor is not None:
        sd = f" ± {fit.volume_factor_sigma:.4f}" if fit.volume_factor_sigma is not None else ""
        out.append(f"- volume factor (measured / target V0) = {fit.volume_factor:.4f}{sd}")
    if fit.breath:
        out.append(f"- breath curve: p0 = {fit.breath['p0_pa']:.0f} Pa, alpha = {fit.breath['alpha']:.2f}")
    if fit.pooled_psi1:
        pp = fit.pooled_psi1
        out.append(f"- **Gate 2 number**: one eta_w per voicing, one k_hole = {pp.k_hole:.3f}, psi = 1: rms {pp.rms_cents:.1f} cents over {pp.n_notes} notes")
    out.append("")
    for b in fit.bodies:
        out += [f"### {b.id} ({b.shape}, V0 {b.v0_cm3:.2f} cm³, hash `{b.voicing_hash}`)", "",
                f"eta_w·G_w = {b.X_w_mm:.4f} mm, eta_w = {b.eta_w:.4f}. All-closed note is {b.a4_error_cents:+.1f} cents off target (holes cannot fix this). "
                f"Residual with shared psi: {b.rms_shared_psi_cents:.2f} cents rms; with psi = 1 (pooled constants): {b.rms_pooled_psi1_cents:.1f} cents rms.", "",
                "| Hole | Opens | d measured | G_eff mm | psi (body) | psi (shared) | d needed mm | ream mm | Flags |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for h in b.holes:
            f = lambda x, n=3: "–" if x is None else f"{x:.{n}f}"
            out.append(f"| {h.name} | {h.opens} | {h.d_measured_mm:.2f} | {f(h.G_eff_mm)} | {f(h.psi_body)} | {f(h.psi)} | "
                       f"{f(h.d_needed_mm, 2)} | {f(h.ream_mm, 2)} | {', '.join(h.flags) or 'ok'} |")
        if not b.corrected_ok:
            out.append(f"\nCorrected diameters not available: {b.corrected_message}")
        out.append("")
    for m in fit.messages:
        out.append(f"- note: {m}")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Stage 1: voicing stub (no holes)
# --------------------------------------------------------------------------

def eta_w_from_stub(f_hz: float, v0_cm3: float, window_area_mm2: float, wall_at_window_mm: float,
                    room_temp_c: float, params: dict | None = None) -> dict:
    """eta_w from one stub pitch. A stub has the voicing and a known volume and no holes, so its pitch gives
    eta_w * G_w directly:  eta_w * G_w = (2 pi f / c)^2 * V0.  Returns {"X_w_mm", "eta_w", "G_w_mm", "c_m_s"}.
    The stub volume must be the capped volume under the same convention as a body (measure it by water fill).
    """
    t = (params or {}).get("temperature", {"design_internal_c": 27.0, "reference_room_c": 22.0, "room_coupling": 0.31})
    c = ok.c_air(ok.internal_air_temp_c(room_temp_c, t["design_internal_c"], t["reference_room_c"], t["room_coupling"]))
    X = (ok.TWO_PI * f_hz / c) ** 2 * v0_cm3 * CM3
    G_w = ok.conductance(window_area_mm2 * MM * MM, wall_at_window_mm * MM, ok.K_WINDOW)
    return {"X_w_mm": X / MM, "eta_w": X / G_w, "G_w_mm": G_w / MM, "c_m_s": c}
