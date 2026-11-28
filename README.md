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

The current work plan is [Visual voicing and add-on plan](docs/10-visual-voicing-and-addon-plan.md).

### Edited specimens and annotated inspection

In the 3D View, open the **Ocarina** sidebar (N), or use **Object > Parametric Ocarina**.

1. **Build Shell to Edit** creates the shell and neck. `P4-bowl` is available; **Preset default** preserves its soft voicing.
2. Edit the base shell, then **Finish Edited Shell**. Choose an export folder and optionally a fitted calibration TOML file. Leave **Create annotated inspection** enabled.
3. The export contains the body and air STLs, check reports, a blank `<id>_measurement.toml`, and `<id>_specimen.json` with the resolved design and geometry-derived calibration identity. The checks use the body STL read back from disk. A later build may replace the export while the measurement template is untouched. Once that file is changed, the folder is refused, preserving recorded measurements; use another folder.
4. Fill the measurement template after measuring a physical specimen. Fit it with `python kernel/fit_measurements.py <measurement files> --write-constants <constants.toml>`, then select those constants when finishing the same edited base. Calibration matches are shown in the report; synthetic constants are labelled synthetic.
5. Select the finished body and choose **Open Geometry Inspection**. The report shows the windway and bowl sections, projected jet guide, aperture and bowl boundary, local thickness map, thumb sealing bands and check results. It is a local HTML file with standalone SVG drawings and a JSON snapshot. For comparison, choose an earlier `<id>_inspection.json` in **Compare inspection JSON** before building. Current and previous geometry share a view scale and can be toggled separately.

The jet guide is geometric, not CFD. Thin edges and thin plates are labelled separately using the existing checks. Missing measurements remain unavailable; geometric validity does not establish physical tuning. With no export folder, inspection files are temporary; export a specimen to retain its evidence. Existing `--renders` builds also generate the annotated report beside their images.

An exported edited specimen is named by its edit: `<base>-edit-<8 hex digits>` (zeros when the edit left the window and the holes as the plain build has them), so two different edits of one base have different files. Every export also writes `PRINT-AND-MEASURE.md`: what to print, what to measure and the commands that follow.

### The panel (experimental, version 0.2.0)

The **Ocarina** sidebar holds the settings of one body (preset, volume, rating, window wall, calibration file); they are saved with the `.blend` file. A setting left at **Preset default** shows the value the preset resolves to. Changing a setting builds nothing. Three actions build:

| Action | What it does |
| --- | --- |
| **Preview** | The body without checks. Nothing is written. |
| **Validate** | The body with every check, the cavity-mode check included. Nothing is exported; the inspection goes to a temporary folder. |
| **Export** | The body checked as the STL read back from disk, with the report, the inspection, the blank measurement template, the specimen record and the checklist, into the export folder. |

The status line says `not built`, `not validated`, `validated` or `changed since validation` (a body setting was changed after the last Validate or Export). Export always checks what it writes, whatever the status.

The cavity-mode check runs in a separate Python with numpy and scipy. Set it in **Preferences > Add-ons > Parametric Ocarina > Python for the cavity-mode check**, or leave it empty to use `OCARINA_PYTHON`, a `.venv` beside the add-on, then `PATH`. **Test Solver** says which one is used. Without one the check fails and says so; it is never skipped.

**Open Tuning Evidence** writes a page for a filled measurement file (also `python -m ocarina_addon.evidence <file>`): the design targets, the measured takes and the geometry checks in separate sections, then each fingering's paired pressure and pitch readings with their status, the speaking limits that were seen and the kernel's descriptive fit. A synthetic file is marked SYNTHETIC in the title, in every figure and in the file name. No pressure fit is used in sizing.

`tools/check_inspection.py <folder>` compares an inspection with the check report beside it. `--specimen` on the headless `body` command writes the same bundle as **Export**.

### Elliptical apertures (geometry only)

`P4-bowl-e756`, `P4-bowl-e889` and `P4-bowl-e1022` are P4-bowl with the aperture a true ellipse of the same area, 7.56, 8.89 and 10.22 mm long along the jet (variant keys `window_shape = "ellipse"`, `window_length_mm`). The 8.89 and 10.22 mm ones build with no unexpected failure; the 7.56 mm one is refused, because its 10.58 mm windway leaves 1.18 mm of plastic around the pipe in the neck (least 1.2 mm). Each has its own voicing hash and no calibration. Equal area does not make them acoustically equal to the teardrop. Nothing was printed.

The P4-bowl edit base still has the prototype's even wall, so finishing that base is a distinct geometry from the one-step uneven-wall P4-bowl build; its calibration identity records this difference.

`ocarina_addon/` is a Blender 5.1 extension that generates the test bodies of [docs/04](docs/04-testing-phase.md): the cavity, a uniform 4 mm wall, the generated voicing and the 12 holes. The kernel is the source of every acoustic number; the add-on builds and checks the geometry. Every check is measured on the STL file read back from disk.

### What you need

- **Blender 5.1.** The commands below use the Windows install path. Blender does not have to be on PATH, and the add-on does not have to be installed for the stage commands. **Blender 5.2 builds too** since 2026-11-26: `cavity_nodes.set_modifier_inputs` sets the Geometry Nodes inputs the 5.2 way when 5.2 refuses the 5.1 way. The committed records are from 5.1.2. On 5.2.0 the blender and extension test suites pass with the same counts as on 5.1.2 (none differs), and P4-80 and P4-bowl-80-zb4 give every check the same status as their 5.1.2 records; plastic, built capped air and every Boolean volume agree within 3e-7 cm³, the capped air measured on the mesh within 1.7e-6 cm³; the STL files differ in float noise.
- **A Python with numpy and scipy outside Blender**, for the cavity-mode check (Blender's own Python has no scipy). The add-on looks for it in this order: the environment variable `OCARINA_PYTHON`, a `.venv` folder in the repository, then `python` on PATH. trimesh is used when it is present. Without such a Python the check `cavity_mode_computed` fails and says so; it never passes by default.

### Generate a stage

Run each command from the repository root. Each one builds every body of its stage, even when one body fails. The commands are written for the Windows command prompt and for Git Bash; in PowerShell put `& ` before the quoted Blender path.

Stage 1, the six voicing stubs (V-a, V-af, V-b, V-d and the optional V-a0, V-a35; about 3 minutes; the 3 mm wall stub V-a3 was dropped on 2026-11-26). V-af is V-a with the plain build (fan cut, level windway, box stub); the pair measures what the build of the bodies is worth:

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

### The shell-edit build (prototype, branch `shell-edit-prototype`)

The add-on makes the solid outer shell and the solid neck, you edit them, and the add-on cuts the instrument out of them. In Blender, with the extension installed:

1. Object > Parametric Ocarina > **Ocarina: Build Base (shell to edit)**. It makes `OCA_<id>_shell` and `OCA_<id>_neck` (two solids, nothing cut yet), and two wire objects for reference: the chamber, and what will be cut (the pipe, the window, the 12 holes).
2. Edit the shell and the neck: sculpt, add relief, lengthen the tail, thicken the neck. Modifiers may stay on the objects.
3. Select the shell and run **Ocarina: Finish Body (from the edited shell)**. The add-on measures the wall your shell has at each hole, sizes each hole for it, solves the chamber again so that the air volume stays the target, cuts everything and runs the checks. The base is hidden, not deleted: edit again and finish again.

What stays the add-on's: the chamber, the window and the pipe, and where the holes are. The mouth end of the neck and the face around the window must stay where the base has them; the checks say so when they did not. Trials that edit the base by program and finish it:

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python tools/shell_edit_trial.py -- --renders
```

They write `addon_checks/shell-edit-trials.md`. The method, the limits that are still provisional and what is not built are in the [build notes](prompts/addon-v1-notes.md#shell-edit-build-prototype-2026-11-18). An edited shell must keep at least 1.32 mm of plastic over the chamber (three printed walls, owner decision of 2026-11-18).

**The neck and the turn of the voicing are rule version 3 since 2026-11-19** (see "Rules since 2026-11-19" below). The trials that led there, the owner's sample and the two bulb models he supplied for shape and position are in [Analizes_ocarinas/Neck_volume/Neck_volume.md](Analizes_ocarinas/Neck_volume/Neck_volume.md).

### Low voicing with the round bowl (an option, not a rule)

The variant `P4-bowl` (`ocarina_addon/presets/variants.toml`) is the body the owner chose from the low-voicing experiment on 2026-11-25 (trial `s3-yH7`, `Analizes_ocarinas/Low_voicing/` on branch `claude/ocarina-low-voicing-dish-009b14`): P4 at 80 cm³ with the round window (the soft length, 8.89 × 9.05 mm), the pipe at +4° and 57 mm long, the cone neck turned 6° toward the thumb face, an uneven wall (3 mm on the finger deck, 6 mm on the thumb face), the window opened into one shallow round bowl (`window_cut = "bowl"`, its numbers in the voicing hash) and, since the owner's pick of 2026-11-26 (trial `s3-zB4`), the left thumb hole moved 4 mm toward the bulb (`thumb_offsets_mm`: an ergonomic change, marked in the report). Each of these is an option that is off by default; the presets, the rule tables and the stages are unchanged.

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python tools/geometry_check_variant.py -- P4-bowl 80 zb4 --renders
```

Add `thumb_offsets_mm='{}'` to build it with the left thumb hole where the template has it (`s3-yH7`, the record `P4-bowl-80-yh7`), or `window_throat_mm=2.403` to size the window with the kernel's effective throat of the rounded walls instead of the 4 mm wall (the records `-teff4`, `-teffrim`). The reports of these builds are `addon_checks/P4-bowl-80-*.md`.

Decided by the owner on 2026-11-26: the left thumb hole moves 4 mm toward the bulb with the bowl unchanged ("s3-zB4"), the window keeps the 4 mm wall as its throat at V0 80 cm³ ("Keep 4.0 mm wall"), and the bowl stays this variant rather than a rule ("Keep as option"). What is left is a print and its η_w: the build has a voicing hash of its own (`bcdd90905c01` at 80 cm³) that no stub carries, so its η_w is unknown until a stub of the same build is measured (doc 04). Nothing was printed, and no print is proposed here. Under the windway's exit corners this variant leaves a plate of 0.18 to 0.42 mm between the windway's floor and the voicing pocket (decision 18 of the build notes; measured, not changed). How it was ported and tested: [build notes](prompts/addon-v1-notes.md#low-voicing-with-the-round-bowl-into-the-add-on-2026-11-26-branch-clauderound-bowl-addon).

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

All four suites with one command (about 12 minutes on the branch `shell-edit-prototype`, where the Blender suite also covers the shell-edit build; about 5 minutes without it):

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

On macOS, with the repository's `.venv` (Python 3.12 with numpy and scipy; `python3 -m venv .venv`, then `.venv/bin/pip install numpy scipy`):

```bash
(cd kernel && ../.venv/bin/python -m unittest discover -s .)
```

```bash
.venv/bin/python -m unittest discover -s tests
```

```bash
OCARINA_PYTHON=$PWD/.venv/bin/python blender -b --factory-startup --python tests/run_blender_tests.py
```

```bash
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender .venv/bin/python -m unittest discover -s tests/extension
```

The installed copy in the test profile does not see the repository's `.venv`, so the extension tests pass it on as `OCARINA_PYTHON` unless that is already set. Last run: Python 3.12.16, numpy 2.5.5, scipy 1.18.1, Blender 5.2.0 LTS.

| Suite | What it covers | Needs |
| --- | --- | --- |
| `kernel/` | The acoustic kernel, the fitter, the measurement files | Python 3.11+ |
| `tests/` | The add-on's modules that need no Blender: cavity maths, hole layout, presets, kernel bridge, ergonomics (it reproduces the reference rows of `measure_cad_output.md`), the cavity-mode solver, the committed stage reports against doc 04; the round bowl's maths, the thumb offset and the variant (`test_round_bowl.py`); the measure of the plastic at the windway's exit corners, `tools/exit_corner_plastic.py` (`test_exit_corner_plastic.py`) | Python with numpy and scipy (tests that need a missing package are skipped) |
| `tests/blender/` | The geometry check as tests: the 25 cavities, P1-80 and P0-65 as bodies, a stub, the stage runner with a forced failure, one Stage 3 body; the shell-edit build (`test_shell_edit.py`); the round-bowl variant and P4-80 with every new option off (`test_round_bowl.py`) | Blender 5.1 |
| `tests/extension/` | Packs the zip, installs it in a temporary Blender profile (`BLENDER_USER_RESOURCES`), builds a body with the installed copy, and checks that your own Blender profile did not change | Blender 5.1 |

## Status (2026-11-18)

The kernel, the measurement fitter and the add-on that generates the test bodies are in place (checkpoints C0 to C6 of the [build notes](prompts/addon-v1-notes.md)). **Nothing has been printed or measured.** Every absolute number is pre-calibration (window efficiency η_w = 0.9 assumed, k_hole 0.8 for the first prints). The next step is the test campaign of doc 04: print Stage 1 (V-a and V-af first), then Stage 2, measure, fit, and generate Stage 3 from the fitted constants. Before Stage 1 is printed the owner confirms the angle of the pipe inside the neck (it is hashed). Before Stage 2 is printed the owner reads the warnings of `addon_checks/stage2.md` and freezes the hole layout.

**Rules since 2026-11-17 (merged from `main`):** volume ladder 65 / 80 / 95 cm³ with an 88 cm³ prediction body (110 and 125 cm³ are no longer printed); labium offset −0.2 mm by default, with the coupons 0 and −0.35 mm; a 3 mm window wall as an option; η_w expected in 0.85–0.95; break pressure recorded per note and per stub. The stages were regenerated at these rules on 2026-11-17: Stage 1 has five of six stubs clean (the optional 3 mm wall stub V-a3 fails its outside keep-out, because the add-on does not yet build the 3 mm wall), Stage 2 has no unexpected failure on its eight bodies, and Stage 3 from the synthetic constants keeps its one known conflict (the edge gap of the left subhole on P1, P2 and P4). See "Merge with main and C5 rerun" in the build notes.

**Rules since 2026-11-18 (owner decisions of that day; `[voicing_rules]` version 2):** the holes open in the Asian fingering order; the left subhole slides 10 mm from L ring; the windway is 3.0 mm high at the mouth end and 1.20 mm at the exit; and the **build** of the voicing is part of the rule and of the voicing hash: the ellipse window cut (3 mm per side, shelf 40°), a neck that stands 15° off the body with the pipe 10° lower inside it (+5° against the body), and a blended pocket behind the labium. The window, the lip, the ramp and the windway exit did not change. The outside keep-out is still the 45° flare from the window rim; the check now measures the flare itself, and the neck stands 41.5° steep seen from the rim. The stages were regenerated: Stage 1 has six of seven stubs clean (the optional 3 mm wall stub V-a3 fails its outside keep-out by 2°), Stage 2 has no unexpected failure on its eight bodies, and Stage 3 from the synthetic constants has none on its seven, for the first time: the 10 mm slide keeps the edge gap with the round-2 diameters. See "Owner decisions applied" in the build notes.

**Rules since 2026-11-19 (the owner's choice of trial `tb-d1`; `[voicing_rules]` version 3):** the roof over the windway exit is cut square (the 40° shelf is gone; the ellipse cut, 3 mm per side, stays); the pipe climbs 8° against the body; the neck is a cone with a thin roof over the pipe (2.2 mm at the mouth end, 1.7 mm at the exit) and a straight, fuller side toward the finger deck; and the voicing sits 30° around the body from the bottom on presets P0 to P4 (it was 45°), so that the mouthpiece points more level at the player. The window, the lip, the ramp and the windway exit did not change; every voicing hash did (80 cm³: `312011ec9f0e`). This replaces the shelf, the +5° and the standing 15° neck of 2026-11-18. The pipe at +8° and the 30° on P0, P2 and P3 came with the picture the owner chose and were not confirmed one by one. The stages were regenerated: Stage 1 has six of seven stubs clean (the optional 3 mm wall stub V-a3 fails its outside keep-out), Stage 2 has no unexpected failure on its eight bodies, Stage 3 none on its seven. The check `hole_to_voicing` now measures the plastic of the neck beside each hole's rim on the built body; it used a box around the mouthpiece, which reported a touch that was not there. See "Rule version 3 applied" in the build notes.

## References

Chris Heuer, *Let's learn to make ocarinas* (YouTube, @ocarinaone), videos #1–#8 (transcripts reviewed; board frames in [references/heuer-frames/](references/heuer-frames/README.md)). Pure Ocarinas articles. Kobayashi et al. 2009 (arXiv:0911.3567). Full list in [docs/01-source-review.md](docs/01-source-review.md#4-extended-research-what-was-added).
