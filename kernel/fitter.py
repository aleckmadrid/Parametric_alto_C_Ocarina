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

Two estimates of k_hole (read this before using k_hole). Both are always reported.

  PROFILE estimate (C2b, owner decision 2). Bodies of one shape share one psi per hole name. When such
  bodies have different hole diameters (the P0 volume ladder), the same hole name is seen at several
  sizes, and only one k makes the model fit all of them with one psi. The fitter compares candidate
  values of k against the measurements: for each k it removes the best psi of every group and sums the
  weighted squares of what is left of ln G. The k with the smallest sum is the profile estimate. Its
  interval is the range of k where the sum stays within 1 of the minimum (the weights are 1 / sigma^2,
  so this is a one-sigma likelihood interval), widened by the reduced chi-square when the model does
  not fit to within the pitch noise. This estimate does not assume anything about the size of psi.

  CONVENTION estimate (the only estimate before C2b). k is chosen so that the (unweighted) geometric
  mean of psi over the holes of the REFERENCE SHAPE is 1. It always exists, and its noise is small.
  But it is right only if the position factors really average 1. If they do not, k absorbs the
  difference: a uniform psi of 1.2 gives k 0.78 for a true 1.07. One body alone, or bodies with equal
  holes, cannot tell k from a common scale of psi, so they have only this estimate.

  Which one drives psi and the corrected diameters (`FitResult.k_hole`, `k_hole_source`): the profile
  estimate, when its interval lies inside the search range and its half-width is at most
  K_PROFILE_MAX_REL_HALFWIDTH (15 %) of its value. Otherwise the convention estimate. A message is
  written whenever the convention value falls outside the profile interval. With the profile estimate
  the position factors are no longer scaled to a geometric mean of 1: their mean is a result
  (`FitResult.psi_geomean_reference`).

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

# The profile estimate of k_hole drives the fit when the half-width of its interval is at most this
# fraction of its value. Reason for 15 %: in the synthetic world a k error of 28 % moves the P0-110 (the old prediction body)
# prediction by about 10 cents (Gate 3 allows 20), so 15 % costs about 5 cents. The convention estimate
# is exact only if the position factors average 1; doc 04 expects them to be 20-40 % off for top holes.
K_PROFILE_MAX_REL_HALFWIDTH = 0.15
K_PROFILE_GRID = 48             # points of the first scan over k_bounds (log-spaced)


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
class KProfile:
    """Profile estimate of k_hole: psi profiled out per group, weighted sum of squares of ln G."""
    k_hole: float                  # k with the smallest sum of squares
    lo: float                      # interval: sum of squares within `delta` of the minimum
    hi: float
    sigma: float                   # (hi - lo) / 2
    chi2_min: float                # sum of squares at the minimum (weights 1 / sigma^2)
    dof: int                       # instances in shared groups - shared groups - 1
    delta: float                   # max(1, chi2_min / dof): the level that defines the interval
    informative: bool              # the interval lies inside k_bounds (the data constrain k)
    rel_halfwidth: float           # sigma / k_hole


@dataclass
class FitResult:
    k_hole: float                  # the value that drives psi and the corrected diameters
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
    # Both estimates of k_hole (see the module docstring).
    k_hole_source: str = "convention"            # "profile" | "convention": which estimate k_hole is
    k_hole_convention: float | None = None       # geometric mean of the reference psi = 1
    k_hole_convention_sigma: float | None = None
    k_hole_profile: KProfile | None = None       # None when share == "none"
    k_hole_rule: str = ""                        # one sentence: why this estimate drives
    psi_geomean_reference: float | None = None   # geometric mean of the reference-shape psi at k_hole


# --------------------------------------------------------------------------
# Step 1: effective conductances of one body
# --------------------------------------------------------------------------

def _areas(body):
    return [math.pi * h.d_measured_m ** 2 / 4.0 for h in body.holes]


def note_sigmas_cents(body, sigma_default=SIGMA_DEFAULT_CENTS, sigma_floor=SIGMA_FLOOR_CENTS, mode="pooled"):
    """Uncertainty of the mean pitch of each note, in cents.

    mode "pooled": one sigma for the whole body, the root-mean-square of the notes' standard errors (a standard
    error from 3 takes is itself very noisy, and weights that follow it by chance hurt the fit).
    mode "sem": each note uses its own standard error.
    A single take has no spread: sigma_default is used.
    """
    sems = [n.cents_sem for n in body.notes]
    known = [x for x in sems if x is not None]
    if mode == "pooled" and known:
        pooled = max(math.sqrt(sum(x * x for x in known) / len(known)), sigma_floor)
        return [pooled if x is not None else max(sigma_default, sigma_floor) for x in sems]
    return [max(x if x is not None else sigma_default, sigma_floor) for x in sems]


def effective_conductances(body, c: float, sigma_default=SIGMA_DEFAULT_CENTS, sigma_floor=SIGMA_FLOOR_CENTS,
                           sigma_mode="pooled"):
    """Return (X_w, G_list, sigma_rel_list, G_tot_list). Lengths in metres.

    sigma_rel is the relative uncertainty of each hole conductance, from the pitch uncertainty of the two
    notes that bracket it (see note_sigmas_cents).
    """
    n = len(body.holes)
    if len(body.notes) != n + 1:
        raise ValueError(f"{body.id}: {len(body.notes)} notes for {n} holes; need one more note than holes")
    K = ok.TWO_PI ** 2 / (c * c)
    A = _areas(body)
    V = body.v0_m3
    G_tot, sig = [], []
    s_cents = note_sigmas_cents(body, sigma_default, sigma_floor, sigma_mode)
    for j, note in enumerate(body.notes):
        if j > 0:
            V -= A[j - 1] * body.holes[j - 1].chimney_m
        G_tot.append(K * note.f_hz ** 2 * V)
        sig.append(2.0 * s_cents[j] / ok.CENTS_PER_LN)           # sigma of ln G_tot
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
               sigma_floor=SIGMA_FLOOR_CENTS, pooled_k_bounds=(0.3, 2.5), sigma_mode="pooled",
               k_source: str = "auto", k_profile_max_rel_halfwidth: float = K_PROFILE_MAX_REL_HALFWIDTH) -> FitResult:
    """Fit one or several bodies together.

    share      "shape": one position factor per (shape, hole name), shared by all bodies of that shape.
               "region": one per (shape, region), regions given as a dict hole name -> region.
               "none": psi = 1 for every hole; only k_hole is fitted.
    reference_shape  the shape of the convention estimate: its psi have a geometric mean of 1 at the
               convention k (default: the shape with most bodies).
    sigma_mode "pooled" (default): one pitch uncertainty per body for all its notes. "sem": per note.
    k_source   "auto" (default): the profile estimate of k_hole drives when its interval is narrow
               enough, otherwise the convention estimate (see the module docstring).
               "profile" or "convention" forces one of them. Both are always reported.
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
        X, G, sig_rel, G_tot = effective_conductances(b, c, sigma_default, sigma_floor, sigma_mode)
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

    # --- convention estimate: geometric mean of the reference psi = 1
    try:
        k_conv = _bisect(norm, *k_bounds)
    except ValueError:
        k_conv = None                # the root lies outside k_bounds: psi are far from an average of 1

    k_conv_sigma = None              # from the weights (linearised)
    if k_conv is not None:
        if share != "none":
            n = len(ref_holes)
            var_N = sum(1.0 / sum(inst[i]["w"] for i in groups[grp]) for _, grp in ref_holes) / (n * n)
            dNdk = sum(sum(inst[i]["w"] * inst[i]["deq"] / (inst[i]["t"] + k_conv * inst[i]["deq"]) for i in groups[grp])
                       / sum(inst[i]["w"] for i in groups[grp]) for _, grp in ref_holes) / n
        else:
            sw = sum(x["w"] for x in inst)
            var_N = 1.0 / sw
            dNdk = sum(x["w"] * x["deq"] / (x["t"] + k_conv * x["deq"]) for x in inst) / sw
        if dNdk > 0:
            k_conv_sigma = math.sqrt(var_N) / dNdk

    # --- profile estimate: compare candidate k against the data, psi profiled out per group
    prof = _profile_k(inst, groups, k_bounds) if share != "none" else None

    # --- which estimate drives
    if k_source not in ("auto", "profile", "convention"):
        raise ValueError(f"unknown k_source {k_source!r}")
    narrow = prof is not None and prof.informative and prof.rel_halfwidth <= k_profile_max_rel_halfwidth
    if k_source == "profile":
        if prof is None or not prof.informative:
            raise ValueError("k_source='profile': the data do not constrain k_hole (one body, bodies with equal "
                             "holes, or share='none')")
        use_profile, why = True, "the profile estimate was forced (k_source='profile')"
    elif k_source == "convention":
        use_profile, why = False, "the convention estimate was forced (k_source='convention')"
    elif share == "none":
        use_profile, why = False, "share='none': psi = 1, so k_hole is the value that makes the mean residual zero"
    elif narrow:
        use_profile = True
        why = (f"the profile estimate drives: its interval is +-{100 * prof.rel_halfwidth:.1f} % "
               f"(limit {100 * k_profile_max_rel_halfwidth:.0f} %)")
    elif prof.informative:
        use_profile = False
        why = (f"the convention estimate drives: the profile interval is +-{100 * prof.rel_halfwidth:.1f} %, "
               f"wider than the limit of {100 * k_profile_max_rel_halfwidth:.0f} %")
    else:
        use_profile = False
        why = ("the convention estimate drives: the data do not constrain k_hole on their own (one body, or bodies "
               "of one shape with equal holes)")
    if not use_profile and k_conv is None:
        if prof is not None and prof.informative:
            use_profile = True
            why = "the profile estimate drives: the convention estimate has no solution inside k_bounds"
        else:
            raise ValueError("root is outside the search range")
    k_fit = prof.k_hole if use_profile else k_conv
    k_sigma = prof.sigma if use_profile else k_conv_sigma
    if prof is not None and prof.informative and k_conv is not None and not (prof.lo <= k_conv <= prof.hi):
        messages.append(
            f"k_hole: the convention value {k_conv:.3f} lies outside the profile interval "
            f"[{prof.lo:.3f}, {prof.hi:.3f}] around {prof.k_hole:.3f}. The position factors of the {reference_shape} "
            f"holes do not average 1. " + ("The profile value is used." if use_profile else
                                           "The convention value is used all the same; read k_hole and psi with care."))
    if k_conv is None:
        messages.append("k_hole: the convention estimate has no solution inside k_bounds")

    lp = lnpsi_groups(k_fit)
    if share == "none":
        psi_g = {g: 1.0 for g in groups}
        psi_gm = 1.0
    else:
        psi_g = {g: math.exp(v) for g, v in lp.items()}
        psi_gm = math.exp(sum(lp[grp] for _, grp in ref_holes) / len(ref_holes))

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
        internal_air=dict(temp), messages=messages,
        k_hole_source="profile" if use_profile else "convention", k_hole_convention=k_conv,
        k_hole_convention_sigma=k_conv_sigma, k_hole_profile=prof, k_hole_rule=why, psi_geomean_reference=psi_gm)


def _profile_k(inst, groups, k_bounds) -> KProfile:
    """Profile estimate of k_hole over all bodies (see the module docstring).

    S(k) = sum over groups of sum_i w_i (r_i(k) - mean_g(k))^2, with r_i = ln G_i - ln G_model(A_i, t_i, k)
    and mean_g the weighted mean in the group (this is ln psi of the group, profiled out). A group with
    one instance adds nothing. The minimum is found by a scan over k_bounds and a golden-section search.
    The interval is where S <= S_min + delta, delta = max(1, S_min / dof).
    """
    multi = [idx for idx in groups.values() if len(idx) > 1]
    cols = [[(inst[i]["y"], inst[i]["w"], inst[i]["area"], inst[i]["t"]) for i in idx] for idx in multi]

    def S(k):
        total = 0.0
        for col in cols:
            r = [y - math.log(ok.conductance(a, t, k)) for y, _, a, t in col]
            sw = sum(w for _, w, _, _ in col)
            m = sum(w * ri for (_, w, _, _), ri in zip(col, r)) / sw
            total += sum(w * (ri - m) ** 2 for (_, w, _, _), ri in zip(col, r))
        return total

    lo_b, hi_b = k_bounds
    n = K_PROFILE_GRID
    grid = [lo_b * (hi_b / lo_b) ** (i / (n - 1)) for i in range(n)]
    vals = [S(k) for k in grid]
    j = min(range(n), key=vals.__getitem__)
    k_hat = _golden(S, grid[max(j - 1, 0)], grid[min(j + 1, n - 1)], tol=1e-10)
    s_min = S(k_hat)
    dof = sum(len(c) for c in cols) - len(cols) - 1
    delta = max(1.0, s_min / dof) if dof > 0 else 1.0

    def edge(bound):
        if not cols or S(bound) - s_min <= delta:
            return bound, False                       # the sum never rises by delta: open on this side
        a, b = k_hat, bound
        for _ in range(100):
            mid = 0.5 * (a + b)
            if S(mid) - s_min <= delta:
                a = mid
            else:
                b = mid
        return 0.5 * (a + b), True

    lo, lo_closed = edge(lo_b)
    hi, hi_closed = edge(hi_b)
    sigma = 0.5 * (hi - lo)
    return KProfile(k_hole=k_hat, lo=lo, hi=hi, sigma=sigma, chi2_min=s_min, dof=dof, delta=delta,
                    informative=bool(cols) and dof > 0 and lo_closed and hi_closed, rel_halfwidth=sigma / k_hat)


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
    out.append(f"- k_hole = **{fit.k_hole:.4f}**{ks} ({fit.k_hole_source} estimate; {fit.k_hole_rule})")
    pr = fit.k_hole_profile
    if pr is None:
        out.append("  - profile estimate (candidate k compared against the data): not made (psi is not fitted)")
    elif pr.informative:
        out.append(f"  - profile estimate (candidate k compared against the data): {pr.k_hole:.4f}, interval "
                   f"[{pr.lo:.4f}, {pr.hi:.4f}] (±{100 * pr.rel_halfwidth:.1f} %), chi² {pr.chi2_min:.1f} on {pr.dof} degrees of freedom")
    else:
        out.append("  - profile estimate (candidate k compared against the data): not available. These bodies do not "
                   "constrain k_hole on their own (one body, or equal holes in every body of a shape).")
    if fit.k_hole_convention is not None:
        cs = f" ± {fit.k_hole_convention_sigma:.3f}" if fit.k_hole_convention_sigma is not None else ""
        out.append(f"  - convention estimate (geometric mean of psi over the {fit.reference_shape} holes = 1): "
                   f"{fit.k_hole_convention:.4f}{cs}")
    else:
        out.append("  - convention estimate: no solution inside the search range")
    if fit.psi_geomean_reference is not None:
        out.append(f"  - geometric mean of psi over the {fit.reference_shape} holes at the k_hole in use: {fit.psi_geomean_reference:.4f}")
    out.append(f"- eta_w fallback (for a voicing never printed) = {fit.eta_w_fallback:.4f}")
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
        out.append(f"- **Gate 2 number for the bodies in this fit** ({len(fit.bodies)} bodies; doc 04's gate is the three P0 ladder bodies, so fit those alone): "
                   f"one eta_w per voicing, one k_hole = {pp.k_hole:.3f}, psi = 1: rms {pp.rms_cents:.1f} cents over {pp.n_notes} notes")
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
