# Parametric alto C ocarina

A 3D-printed, parametrically tuned 12-hole alto C ocarina (A4..F6). It is built around a frozen, pre-validated voicing module and a lumped Helmholtz acoustic kernel. The chamber and shell can be sculpted freely, because pitch depends only on chamber volume and opening conductances.

## Start here

1. [prompts/addon-v1-notes.md](prompts/addon-v1-notes.md): the hand-over between sessions. Status, next step, the kernel and add-on APIs, and the single list of pending owner decisions.
2. [docs/02-unified-plan.md](docs/02-unified-plan.md): scope, architecture, phases and gates.
3. [docs/03-parametric-findings.md](docs/03-parametric-findings.md): equations, derived identities, the computed baseline design, and design rules R1–R14.
4. [docs/04-testing-phase.md](docs/04-testing-phase.md): the test plan (volume ladder 65 / 80 / 95 cm³, shape test, voicing stubs) with the filament budget.
5. [docs/01-source-review.md](docs/01-source-review.md): how the sources were checked. §5–§6 hold the Heuer video review and the consolidated verdicts.
6. Reference instruments: [Miracle AO10-AC](Analizes_ocarinas/Miracle_M/Miracle_M.md) (photo analysis) and the [ECAN3 experimental track](Analizes_ocarinas/ECAN3_experimental/ECAN3_experimental.md) (three printed designs measured from their STLs).
7. [docs/05-ergonomics.md](docs/05-ergonomics.md): hand ergonomics of the hole layout and the body shape, soft rules, and how the add-on compares. Resources in [references/ocarina-making-resources.md](references/ocarina-making-resources.md).
8. [docs/06-ergonomics-challenge.md](docs/06-ergonomics-challenge.md): the review of doc 05 against two CAD references with a true scale. Where doc 05 and doc 06 differ, doc 06 holds; the add-on builds its rules.

9. [docs/09-kernel-and-decisions-challenged.md](docs/09-kernel-and-decisions-challenged.md): the re-analysis of 2026-11-18. It challenges the kernel, the test suite and the decisions of 15–17 November against the tutorial series and three made instruments. Its first finding was applied the same day: the holes now open in the Asian fingering order (left ring first on the left hand, then the thumbs, the left pinky last), with one subhole per hand as before. Its section 8 lists what was still to decide before the Stage 1 stubs; most of it was decided the same day (next item).
10. [Analizes_ocarinas/Decisions_2026-11-18/decisions.md](Analizes_ocarinas/Decisions_2026-11-18/decisions.md): six decisions of 2026-11-18, each with a picture sheet and the measured effect of its options, and what the owner chose: left subhole slide 10 mm, the ellipse window cut, a windway 3 mm high at the mouth end, the build of the voicing in its hash, and a neck that stands 15° off the body. One point is open: the angle of the pipe inside that neck.

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

## Add-on (Blender 5.1)

`ocarina_addon/` is a Blender 5.1 extension that generates the test bodies of [docs/04](docs/04-testing-phase.md): the cavity, a uniform 4 mm wall, the generated voicing and the 12 holes. The kernel is the source of every acoustic number; the add-on builds and checks the geometry. Every check is measured on the STL file read back from disk.

### What you need

- **Blender 5.1.** The commands below use the Windows install path. Blender does not have to be on PATH, and the add-on does not have to be installed for the stage commands.
- **A Python with numpy and scipy outside Blender**, for the cavity-mode check (Blender's own Python has no scipy). The add-on looks for it in this order: the environment variable `OCARINA_PYTHON`, a `.venv` folder in the repository, then `python` on PATH. trimesh is used when it is present. Without such a Python the check `cavity_mode_computed` fails and says so; it never passes by default.

### Generate a stage

Run each command from the repository root. Each one builds every body of its stage, even when one body fails. The commands are written for the Windows command prompt and for Git Bash; in PowerShell put `& ` before the quoted Blender path.

Stage 1, the seven voicing stubs (V-a, V-af, V-b, V-d and the optional V-a0, V-a35, V-a3; about 3 minutes). V-af is V-a with the plain build (fan cut, level windway, box stub); the pair measures what the build of the bodies is worth:

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python ocarina_addon/headless.py -- stage1
```

Stage 2, the eight round-1 bodies (about 6 minutes):

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python ocarina_addon/headless.py -- stage2
```

Stage 3, the round-2 bodies and the P0-88 prediction body from a fitted-constants file (about 5 minutes). The file in the repository is **synthetic**: invented values that only show that the generator works.

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python ocarina_addon/headless.py -- stage3 --calibration calibration/synthetic-fitted-constants.toml
```

| Stage | STL files and blank measurement templates (not in git) | Reports | Pictures |
| --- | --- | --- | --- |
| 1 | `addon_out/stage1/<id>/` | `addon_checks/stage1.md`, `addon_checks/<id>.md` | `addon_renders/<id>/` |
| 2 | `addon_out/stage2/<id>/` | `addon_checks/stage2.md`, `addon_checks/<id>.md` | `addon_renders/<id>/` |
| 3 | `addon_out/stage3-<calibration file name>/<id>/` | `addon_checks/stage3-<calibration file name>.md`; per-body reports beside the STL | off (add `--renders`) |

Per body a stage writes `<id>.stl` (print this), `<id>_air_capped.stl` and `<id>_air_fem.stl` (the air), `<id>_measurement.toml` (fill it in after printing) and a check report. Options: `--out`, `--reports`, `--renders-dir`, `--no-renders`, `--only <id> ...`.

**Read the stage report before printing.** It has three separate blocks:

- *Unexpected failures.* A body with one must not be printed. Only these give the command a non-zero exit code.
- *Expected failures.* The pad-limit checks, which the plan expects (some holes are larger than a finger pad on purpose).
- *Warnings.* The soft hand-layout checks (`ergo_*`). They are measurements to judge and never failures. The P0 bodies warn on all of them: they are taped test bodies, not hand layouts.

After printing: fill the measurement files, then fit the bodies with `python kernel/fit_measurements.py <files> --write-constants <file>` and the stubs with `python tools/stub_eta_w.py <files>`.

### One body, or a variant

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python tools/geometry_check.py -- body P1 80 --renders
```

`tools/geometry_check_variant.py -- P3 80 ov6 hand_overlap_mm=6` builds a body with preset values overridden, under its own name. The presets are in `ocarina_addon/presets/cavity_presets.toml`; the limits of the hand-layout checks are in the `[ergonomics]` table of `params/alto_c_12hole.toml`.

### Install the extension in Blender

The stage commands run from the repository. To use the operators inside Blender (Object > Parametric Ocarina), pack and install the extension:

```bash
python tools/pack_extension.py --validate
```

This writes `dist/parametric_ocarina-<version>.zip` with the add-on, the kernel and the parameter file inside. In Blender: Edit > Preferences > Get Extensions > the arrow at the top right > Install from Disk, and choose the zip. Or from a command line:

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --command extension install-file -r user_default --enable dist/parametric_ocarina-0.1.0.zip
```

### Tests

All four suites with one command (about 5 minutes):

```bash
python tools/run_tests.py
```

Or one suite at a time:

```bash
python -m unittest discover -s kernel
```

```bash
python -m unittest discover -s tests
```

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python tests/run_blender_tests.py
```

```bash
python -m unittest discover -s tests/extension
```

| Suite | What it covers | Needs |
| --- | --- | --- |
| `kernel/` | The acoustic kernel, the fitter, the measurement files | Python 3.11+ |
| `tests/` | The add-on's modules that need no Blender: cavity maths, hole layout, presets, kernel bridge, ergonomics (it reproduces the reference rows of `measure_cad_output.md`), the cavity-mode solver, the committed stage reports against doc 04 | Python with numpy and scipy (tests that need a missing package are skipped) |
| `tests/blender/` | The geometry check as tests: the 25 cavities, P1-80 and P0-65 as bodies, a stub, the stage runner with a forced failure, one Stage 3 body | Blender 5.1 |
| `tests/extension/` | Packs the zip, installs it in a temporary Blender profile (`BLENDER_USER_RESOURCES`), builds a body with the installed copy, and checks that your own Blender profile did not change | Blender 5.1 |

## Status (2026-11-18)

The kernel, the measurement fitter and the add-on that generates the test bodies are in place (checkpoints C0 to C6 of the [build notes](prompts/addon-v1-notes.md)). **Nothing has been printed or measured.** Every absolute number is pre-calibration (window efficiency η_w = 0.9 assumed, k_hole 0.8 for the first prints). The next step is the test campaign of doc 04: print Stage 1 (V-a and V-af first), then Stage 2, measure, fit, and generate Stage 3 from the fitted constants. Before Stage 1 is printed the owner confirms the angle of the pipe inside the neck (it is hashed). Before Stage 2 is printed the owner reads the warnings of `addon_checks/stage2.md` and freezes the hole layout.

**Rules since 2026-11-17 (merged from `main`):** volume ladder 65 / 80 / 95 cm³ with an 88 cm³ prediction body (110 and 125 cm³ are no longer printed); labium offset −0.2 mm by default, with the coupons 0 and −0.35 mm; a 3 mm window wall as an option; η_w expected in 0.85–0.95; break pressure recorded per note and per stub. The stages were regenerated at these rules on 2026-11-17: Stage 1 has five of six stubs clean (the optional 3 mm wall stub V-a3 fails its outside keep-out, because the add-on does not yet build the 3 mm wall), Stage 2 has no unexpected failure on its eight bodies, and Stage 3 from the synthetic constants keeps its one known conflict (the edge gap of the left subhole on P1, P2 and P4). See "Merge with main and C5 rerun" in the build notes.

**Rules since 2026-11-18 (owner decisions of that day; `[voicing_rules]` version 2):** the holes open in the Asian fingering order; the left subhole slides 10 mm from L ring; the windway is 3.0 mm high at the mouth end and 1.20 mm at the exit; and the **build** of the voicing is part of the rule and of the voicing hash: the ellipse window cut (3 mm per side, shelf 40°), a neck that stands 15° off the body with the pipe 10° lower inside it (+5° against the body), and a blended pocket behind the labium. The window, the lip, the ramp and the windway exit did not change. The outside keep-out is still the 45° flare from the window rim; the check now measures the flare itself, and the neck stands 41.5° steep seen from the rim. The stages were regenerated: Stage 1 has six of seven stubs clean (the optional 3 mm wall stub V-a3 fails its outside keep-out by 2°), Stage 2 has no unexpected failure on its eight bodies, and Stage 3 from the synthetic constants has none on its seven, for the first time: the 10 mm slide keeps the edge gap with the round-2 diameters. See "Owner decisions applied" in the build notes.

## References

Chris Heuer, *Let's learn to make ocarinas* (YouTube, @ocarinaone), videos #1–#8 (transcripts reviewed; board frames in [references/heuer-frames/](references/heuer-frames/README.md)). Pure Ocarinas articles. Kobayashi et al. 2009 (arXiv:0911.3567). Full list in [docs/01-source-review.md](docs/01-source-review.md#4-extended-research-what-was-added).
