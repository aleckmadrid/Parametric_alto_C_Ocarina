# Parametric alto C ocarina

A 3D-printed, parametrically tuned 12-hole alto C ocarina (A4..F6). It is built around a frozen, pre-validated voicing module and a lumped Helmholtz acoustic kernel. The chamber and shell can be sculpted freely, because pitch depends only on chamber volume and opening conductances.

## Start here

1. [docs/02-unified-plan.md](docs/02-unified-plan.md): scope, architecture, phases and gates, open questions.
2. [docs/03-parametric-findings.md](docs/03-parametric-findings.md): equations, derived identities, the computed baseline design, and design rules R1–R14.
3. [docs/01-source-review.md](docs/01-source-review.md): how the three input documents were checked, what was corrected, and the extra sources.
4. [docs/04-testing-phase.md](docs/04-testing-phase.md): the test plan for larger chamber volumes and the three cavity shapes, with the filament budget.

## Kernel

Standard-library Python 3.11+ (uses `tomllib`):

```bash
python kernel/alto_c_study.py
```

```bash
python -m unittest discover -s kernel -v
```

The study script reads `params/alto_c_12hole.toml`, prints every table in doc 03 and writes `docs/generated/study-output.md`.

## Status

Phase 0 (kernel) has started: the solver, checks and tests are in place. Every absolute number is **pre-calibration** (window efficiency η_w = 0.9 assumed). Phase 2's calibration print replaces the assumed constants with measured ones.

## References

Chris Heuer, *Let's learn to make ocarinas* (YouTube, @ocarinaone), videos #1–#8. Pure Ocarinas articles. Kobayashi et al. 2009 (arXiv:0911.3567). Full list in [docs/01-source-review.md](docs/01-source-review.md#4-extended-research-what-was-added).
