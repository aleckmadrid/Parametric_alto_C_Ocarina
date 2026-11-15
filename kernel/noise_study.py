"""Noise study for the fitter, on SYNTHETIC data (C2 acceptance: "report how the error grows").

    python kernel/noise_study.py                 # prints the Markdown table
    python kernel/noise_study.py --runs 40

For each noise level it builds the synthetic round-1 set (9 bodies) or one body, adds pitch noise per take,
fits, and compares with the invented truth. Errors are relative, in percent: |fit - truth| / truth.

The fitter makes two estimates of k_hole (see fitter.py): the profile estimate (candidate k compared
against the data) and the convention estimate (geometric mean of the P0 position factors = 1). The table
gives the error of both, and of the one that drives the fit. In the first rows the invented position
factors have a geometric mean of 1, so the convention holds. The "psi x 1.2" and "psi x 0.8" rows (C2b)
scale every position factor, so the convention is broken by 20 %. Doc 04 expects offsets of this size.
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
import sys

import config
import fitter
import synthetic as sy


def _pct(x, q):
    s = sorted(x)
    return s[min(len(s) - 1, int(round(q * (len(s) - 1))))]


def scaled_truth(psi_scale: float = 1.0, truth=None) -> dict:
    """Invented truth with every position factor multiplied by psi_scale (geometric mean = psi_scale)."""
    base = truth or sy.make_truth()
    if psi_scale == 1.0:
        return base
    return sy.make_truth(**{**{k: v for k, v in base.items() if k != "psi"},
                            "psi": {k: v * psi_scale for k, v in base["psi"].items()}, "normalise": False})


def run_case(noise_cents, noise, n_takes, runs, seed, single=False, truth=None, params=None, sigma_mode="pooled",
             psi_scale: float = 1.0, k_source: str = "auto"):
    P = params or config.load_params()
    truth = scaled_truth(psi_scale, truth)
    err_eta, err_k, err_kc, err_kp, err_psi, err_psi_small, n_unres, n_profile = [], [], [], [], [], [], 0, 0
    for r in range(runs):
        rng_seed = seed * 1000 + r
        if single:
            rng = random.Random(rng_seed)
            bodies = [sy.synth_body("one", "P0", 80.0, truth, noise_cents=noise_cents, noise=noise, n_takes=n_takes, rng=rng)]
        else:
            bodies = sy.round1_set(seed=rng_seed, noise_cents=noise_cents, truth=truth, noise=noise, n_takes=n_takes)
        fit = fitter.fit_bodies(bodies, P, sigma_mode=sigma_mode, k_source=k_source)
        h = bodies[-1 if single else 1].voicing_hash
        err_eta.append(abs(fit.eta_w_by_hash[h]["eta_w"] / truth["eta_w"] - 1) * 100)
        err_k.append(abs(fit.k_hole / truth["k_hole"] - 1) * 100)
        if fit.k_hole_convention is not None:
            err_kc.append(abs(fit.k_hole_convention / truth["k_hole"] - 1) * 100)
        pr = fit.k_hole_profile
        if pr is not None and pr.informative:
            err_kp.append(abs(pr.k_hole / truth["k_hole"] - 1) * 100)
        n_profile += fit.k_hole_source == "profile"
        tbl = fit.psi["P0"]
        for name, v in tbl.items():
            if v is None:
                continue
            e = abs(v / truth["psi"][name] - 1) * 100
            err_psi.append(e)
            if name in ("sub1", "sub2", "R_middle"):
                err_psi_small.append(e)
        n_unres += sum(1 for b in fit.bodies for hf in b.holes if not hf.resolved)
    med = lambda x: statistics.median(x) if x else None
    p95 = lambda x: _pct(x, 0.95) if x else None
    return dict(noise=noise_cents, kind=noise, n_takes=n_takes, single=single, runs=runs, psi_scale=psi_scale,
                eta_med=statistics.median(err_eta), eta_p95=_pct(err_eta, 0.95),
                k_med=statistics.median(err_k), k_p95=_pct(err_k, 0.95),
                kc_med=med(err_kc), kc_p95=p95(err_kc), kp_med=med(err_kp), kp_p95=p95(err_kp),
                profile_runs=n_profile,
                psi_med=statistics.median(err_psi), psi_p95=_pct(err_psi, 0.95),
                psi_small_med=statistics.median(err_psi_small), psi_small_p95=_pct(err_psi_small, 0.95),
                unresolved=n_unres)


def _pair(a, b, nd=2):
    return "–" if a is None else f"{a:.{nd}f} / {b:.{nd}f}"


def table(rows) -> str:
    head = ["Case", "psi scale", "noise per take", "takes", "eta_w·G_w err % (med / p95)",
            "k_hole in use err % (med / p95)", "profile drives (runs)", "k_hole profile err % (med / p95)",
            "k_hole convention err % (med / p95)", "psi err % all holes (med / p95)",
            "psi err % sub1, sub2, R_middle (med / p95)", "unresolved holes"]
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    for r in rows:
        case = "one body" if r["single"] else "nine bodies"
        noise = "none" if r["noise"] == 0 else (f"±{r['noise']:g} cents uniform" if r["kind"] == "uniform" else f"σ {r['noise']:g} cents")
        out.append("| " + " | ".join([
            case, f"{r['psi_scale']:g}", noise, str(r["n_takes"]),
            _pair(r["eta_med"], r["eta_p95"], 3), _pair(r["k_med"], r["k_p95"]),
            f"{r['profile_runs']} of {r['runs']}", _pair(r["kp_med"], r["kp_p95"]), _pair(r["kc_med"], r["kc_p95"]),
            _pair(r["psi_med"], r["psi_p95"]), _pair(r["psi_small_med"], r["psi_small_p95"]), str(r["unresolved"])]) + " |")
    return "\n".join(out)


NOISE_CASES = ((1.0, "uniform", 3), (2.0, "uniform", 3), (5.0, "uniform", 3), (5.0, "uniform", 1),
               (5.0, "gauss", 3), (10.0, "uniform", 3))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Noise study of the fitter on SYNTHETIC data.")
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for single in (True, False):
        rows.append(run_case(0.0, "gauss", 3, 1, args.seed, single))
        for noise, kind, takes in NOISE_CASES:
            rows.append(run_case(noise, kind, takes, args.runs, args.seed, single))
    # C2b: position factors that break the convention (geometric mean 1.2 and 0.8)
    for scale in (1.2, 0.8):
        rows.append(run_case(0.0, "gauss", 3, 1, args.seed, True, psi_scale=scale))
        rows.append(run_case(5.0, "uniform", 3, args.runs, args.seed, True, psi_scale=scale))
        rows.append(run_case(0.0, "gauss", 3, 1, args.seed, False, psi_scale=scale))
        for noise, kind, takes in ((2.0, "uniform", 3), (5.0, "uniform", 3), (10.0, "uniform", 3)):
            rows.append(run_case(noise, kind, takes, args.runs, args.seed, False, psi_scale=scale))
    print("SYNTHETIC data. Invented truth: eta_w 0.86, k_hole 1.07, position factors 0.83..1.13 (geometric mean 1),")
    print("multiplied by the psi scale of the row.")
    print(f"{args.runs} runs per row, seed {args.seed}. Errors are relative to the invented truth.")
    print()
    print(table(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
