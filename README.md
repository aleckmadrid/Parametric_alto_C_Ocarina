# Parametric alto C ocarina

A 3D-printed, parametrically tuned 12-hole alto C ocarina (A4..F6). It is built around a frozen, pre-validated voicing module and a lumped Helmholtz acoustic kernel. The chamber and shell can be sculpted freely, because pitch depends only on chamber volume and opening conductances.

## Start here

1. [prompts/addon-v1-notes.md](prompts/addon-v1-notes.md): the hand-over between sessions. Status, next step, the kernel and add-on APIs, and the single list of pending owner decisions.
2. [docs/02-unified-plan.md](docs/02-unified-plan.md): scope, architecture, phases and gates.
3. [docs/03-parametric-findings.md](docs/03-parametric-findings.md): equations, derived identities, the computed baseline design, and design rules R1–R14.
4. [docs/04-testing-phase.md](docs/04-testing-phase.md): the test plan (volume ladder 65 / 80 / 95 cm³, shape test, voicing stubs) with the filament budget.
5. [docs/01-source-review.md](docs/01-source-review.md): how the sources were checked. §5–§6 hold the Heuer video review and the consolidated verdicts.
6. Reference instruments: [Miracle AO10-AC](Analizes_ocarinas/Miracle_M/Miracle_M.md) (photo analysis) and the [ECAN3 experimental track](Analizes_ocarinas/ECAN3_experimental/ECAN3_experimental.md) (three printed designs measured from their STLs).

## Kernel

Standard-library Python 3.11+ (uses `tomllib`):

```bash
python -m unittest discover -s kernel -v
```

```bash
python kernel/sizing.py --table
```

```bash
python kernel/alto_c_study.py
```

- `kernel/sizing.py` sizes the test bodies (window, windway, every hole, checks); `--holes` prints the full tables, `--wall 3` uses the 3 mm window wall.
- `kernel/fit_measurements.py` fits filled-in measurement files (`measurements/`) and writes the constants file (`calibration/`).
- `kernel/alto_c_study.py` reproduces every table in doc 03 and writes `docs/generated/study-output.md`.

## Blender add-on

`ocarina_addon/` is a Blender 5.1 extension that builds printable test bodies from the kernel. It runs headless from the repository root:

```bash
blender -b --factory-startup --python ocarina_addon/headless.py -- body --preset P0 --v0 80 --out addon_out/P0-80
```

```bash
blender -b --factory-startup --python tools/geometry_check.py -- bodies
```

The check script measures the exported STL files and writes `addon_checks/`.

## Status (2026-11-18)

- **Kernel:** sizing, voicing rules, hole solver with inward tubes, checks, measurement format, fitter and calibration constants are done; 125 tests pass.
- **Add-on:** checkpoints C0–C4 are done (cavity presets P0–P3, voicing, holes, wall, Booleans, checks, STL export). C5 (stage commands, stubs) and C6 (tests, packaging) are next. The reports in `addon_checks/` are stale until the Blender checks are rerun.
- **Design decisions since C4:** volume ladder 65 / 80 / 95 cm³ with an 88 cm³ prediction body; 3 mm window wall as an option; labium offset −0.2 mm (edge below the jet centre); teardrop tip radius 1.0 mm; break pressure recorded per note.
- **Branches:** all work is on `main`; `addon-v1` and `ecan3-experimental` point to the same commit.
- **Nothing has been printed.** Every absolute number is pre-calibration (window efficiency η_w = 0.9 assumed, expected 0.85–0.95). The voicing stubs and round-1 bodies of doc 04 replace the assumed constants with measured ones.

## Next steps

1. Owner decisions that change geometry (window wall for the ladder, the 95 cm³ window shape, P3 layout, P2 waiver).
2. Rerun the Blender geometry checks at the current rules (refreshes `addon_checks/`).
3. Add-on C5: labium-offset and Stage 3 inputs for `build_body`, the Stage 1 voicing stubs, stage commands and reports.
4. Add-on C6: tests and packaging.
5. Print the voicing stubs, then the round-1 bodies; fit and correct (doc 04, Gates 1–3).

Details, owner decisions and the API are in [prompts/addon-v1-notes.md](prompts/addon-v1-notes.md) ("Next steps", "Pending owner decisions").

## References

Chris Heuer, *Let's learn to make ocarinas* (YouTube, @ocarinaone), videos #1–#8 (transcripts reviewed; board frames in [references/heuer-frames/](references/heuer-frames/README.md)). Pure Ocarinas articles. Kobayashi et al. 2009 (arXiv:0911.3567). Full list in [docs/01-source-review.md](docs/01-source-review.md#4-extended-research-what-was-added).
