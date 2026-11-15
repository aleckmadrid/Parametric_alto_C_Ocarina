"""Noise study for the fitter, on SYNTHETIC data (C2 acceptance: "report how the error grows").

    python kernel/noise_study.py                 # prints the Markdown table
    python kernel/noise_study.py --runs 40

For each noise level it builds the synthetic round-1 set (9 bodies) or one body, adds pitch noise per take,
fits, and compares with the invented truth. Truth psi has geometric mean 1 (the fitter's convention).
Errors are relative, in percent: |fit - truth| / truth.
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


def run_case(noise_cents, noise, n_takes, runs, seed, single=False, truth=None, params=None, sigma_mode="pooled"):
    P = params or config.load_params()
    truth = truth or sy.make_truth()
    err_eta, err_k, err_psi, err_psi_small, n_unres = [], [], [], [], 0
    for r in range(runs):
        rng_seed = seed * 1000 + r
        if single:
            rng = random.Random(rng_seed)
            bodies = [sy.synth_body("one", "P0", 80.0, truth, noise_cents=noise_cents, noise=noise, n_takes=n_takes, rng=rng)]
        else:
            bodies = sy.round1_set(seed=rng_seed, noise_cents=noise_cents, truth=truth, noise=noise, n_takes=n_takes)
        fit = fitter.fit_bodies(bodies, P, sigma_mode=sigma_mode)
        h = bodies[-1 if single else 1].voicing_hash
        err_eta.append(abs(fit.eta_w_by_hash[h]["eta_w"] / truth["eta_w"] - 1) * 100)
        err_k.append(abs(fit.k_hole / truth["k_hole"] - 1) * 100)
        tbl = fit.psi["P0"]
        for name, v in tbl.items():
            if v is None:
                continue
            e = abs(v / truth["psi"][name] - 1) * 100
            err_psi.append(e)
            if name in ("sub1", "sub2", "R_middle"):
                err_psi_small.append(e)
        n_unres += sum(1 for b in fit.bodies for hf in b.holes if not hf.resolved)
    return dict(noise=noise_cents, kind=noise, n_takes=n_takes, single=single, runs=runs,
                eta_med=statistics.median(err_eta), eta_p95=_pct(err_eta, 0.95),
                k_med=statistics.median(err_k), k_p95=_pct(err_k, 0.95),
                psi_med=statistics.median(err_psi), psi_p95=_pct(err_psi, 0.95),
                psi_small_med=statistics.median(err_psi_small), psi_small_p95=_pct(err_psi_small, 0.95),
                unresolved=n_unres)


def table(rows) -> str:
    head = ["Case", "noise per take", "takes", "eta_w·G_w err % (med / p95)", "k_hole err % (med / p95)",
            "psi err % all holes (med / p95)", "psi err % sub1, sub2, R_middle (med / p95)", "unresolved holes"]
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    for r in rows:
        case = "one body" if r["single"] else "nine bodies"
        noise = "none" if r["noise"] == 0 else (f"±{r['noise']:g} cents uniform" if r["kind"] == "uniform" else f"σ {r['noise']:g} cents")
        out.append("| " + " | ".join([case, noise, str(r["n_takes"]),
                                      f"{r['eta_med']:.3f} / {r['eta_p95']:.3f}", f"{r['k_med']:.2f} / {r['k_p95']:.2f}",
                                      f"{r['psi_med']:.2f} / {r['psi_p95']:.2f}",
                                      f"{r['psi_small_med']:.2f} / {r['psi_small_p95']:.2f}", str(r["unresolved"])]) + " |")
    return "\n".join(out)


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
        for noise, kind, takes in ((1.0, "uniform", 3), (2.0, "uniform", 3), (5.0, "uniform", 3), (5.0, "uniform", 1),
                                   (5.0, "gauss", 3), (10.0, "uniform", 3)):
            rows.append(run_case(noise, kind, takes, args.runs, args.seed, single))
    print("SYNTHETIC data. Invented truth: eta_w 0.86, k_hole 1.07, position factors 0.83..1.13 (geometric mean 1).")
    print(f"{args.runs} runs per row, seed {args.seed}. Errors are relative to the invented truth.")
    print()
    print(table(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
