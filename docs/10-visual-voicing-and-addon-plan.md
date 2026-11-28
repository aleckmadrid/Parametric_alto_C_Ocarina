# Visual voicing and add-on plan

The next milestone is a visual voicing workbench with a complete measurement and calibration workflow. The selected P4-bowl geometry remains the baseline: 80 cm³, the 4 mm throat convention, the existing bowl and left-thumb offset. Geometry checks establish build validity; physical measurements establish tuning.

The work is split in two phases. **Phase A** is everything that can run unattended: no owner answer, no print, no listening test. Where a decision is pending, Phase A uses the stated default and builds so that the other answer costs little. **Phase B** is everything blocked by a decision, a review or a physical test. The steps of the original plan (1 to 5, and 2a) are kept at the end as the reference; each phase item names the step it serves.

| Step | Phase A | Phase B |
|---|---|---|
| 1 Edited shell measurements | done; A2 closes the open ID point | B1 review |
| 2 Annotated inspection | done; A3 regenerates the examples | B1 review |
| 2a Baseline print | A4 print package | B2 print, measure, fit |
| 3 Elliptical aperture | A7 family and geometry-only specimens | D1, then B4 prints |
| 4 Tuning evidence | A5 report tool on synthetic fixtures | B3 real data, D8 |
| 5 Add-on release | A6 settings, actions, solver, package | B5 UI review, B6 release |

## Phase A: unattended run

### Rules of the run

- No commit, push, pull request or publication. No file outside the repository is changed, except a `.venv` inside it (A1).
- The baseline's voicing hash (`bcdd90905c01`) and its sizing must not change. A test asserts it before and after every package. If it changes, undo the package and record why.
- Nothing in `params/` or `presets/variants.toml` that changes an existing body. New presets and new keys with a default that reproduces today's result are allowed.
- Every output states what it is: geometry check, synthetic fixture or prediction. Nothing produced in Phase A is tuning evidence.
- A package that fails its acceptance is recorded in the implementation record with the failing output, and the run goes on to the next package. Packages are independent unless "needs" says otherwise.
- After each package: the plain suite, the specimen tests and the package's own tests. After the last one: all four suites.
- Order: A1, A2, A3, A4, A5, A6, A7, A8. A7 is last of the build work because decision D1 may drop it.

### A1. Environment that runs every test

Why: on 2026-11-26 the extension test `test_the_installed_extension_builds_a_body` failed here because no Python with numpy and scipy was found, and the plain suite needs a Python of 3.11 or later with numpy.

1. Create `.venv` in the repository root with numpy and scipy. `cavity_mode._candidates` already looks there first after `OCARINA_PYTHON`. Check that `.venv` is in `.gitignore`; add it if not.
2. Run the plain suite with that Python: `.venv/bin/python -m unittest discover -s tests`, and the kernel tests in `kernel/`.
3. Run the extension tests with `BLENDER=/Applications/Blender.app/Contents/MacOS/Blender`.
4. Remove the macOS sidecar files `.git/objects/pack/._*` (they cause the "non-monotonic index" lines on every git command; they are not git objects). Check `git fsck` before and after.
5. Write the exact commands and the versions (Python, numpy, scipy, Blender) under "How to run the tests" in the README.

Acceptance: kernel, plain, Blender and all 4 extension tests pass, with the cavity-mode step computed, not skipped. `git status` prints no index error.

### A2. One ID per edited specimen (step 1, open point)

Today every finish of one base is `<base>-edit`. Two different edits differ only by folder and calibration context.

1. Read `kernel/fitter.py` and `kernel/calibration.py`: find every place that keys on `BodyMeasurement.id`. Write the finding in the record.
2. Default (D4): the scene objects keep `OCA_<base>-edit` (so a second finish still replaces the first). The exported files and the `[body] id` of the template become `<base>-edit-<8 hex>`, the hex taken from the calibration identity (`0`×8 when both regions are the plain build's). Implement it in `shell_edit.finish` as the export stem only; `body_id=` given by the caller still wins.
3. `specimen.require_new_export` then guards the new stem. Update `OCA_OT_finish_body`, the README and the two specimen test files.
4. Tests: the same edit finished twice has the same stem; a rim edit and a window edit have different stems; the untouched base has the zero stem; a fit of two edited files of one base keeps them apart.

Acceptance: those tests, and the synthetic export, fit and exact-match cycle still passes.

### A3. Regenerate the examples of steps 1 and 2

The files in `addon_out/visual-review-step12/` predate the review fixes.

1. Rebuild `current` (P4-bowl, 80 cm³, one-step build, cavity-mode step on) and `prior` (the thin-floor regression, as it was made: the preset without `pocket_back_margin_mm`), `current` with `prior` as its previous inspection.
2. Render the HTML report and the five SVG views to PNG previews with the built-in browser or Blender's image API; whichever is used, record the command.
3. Self-check script `tools/check_inspection.py` (new, small): read `<id>_inspection.json` and `<id>_checks.json`, assert that every value in `measured` equals the check report's, that each differs from the design value by less than the check's tolerance (`TOL_MM` in `checks_geo`), and that `jet_to_edge.off_axis_mm` equals labium offset × cos(pitch). Exit code 1 on a difference. Run it on both examples and add it to the Blender specimen test.
4. Look at each preview once and record in the notes what is seen: labels that overlap, a marker off the mesh, a clipped section. Fix what is a defect of the drawing; list what is a matter of taste under B1.

Acceptance: the self-check passes on both; `current` has no unexpected failure and its two expected pad-limit failures; `prior` shows its wide thin-plate probes and `current` shows none.

### A4. Baseline print package (prepares step 2a)

Everything the owner needs to print and measure without opening Blender.

1. Export the baseline to `addon_out/baseline-print-P4-bowl-80/` through `api.build_checked_body` and `specimen.write_bundle`, cavity-mode step on, renders on.
2. Write `PRINT-AND-MEASURE.md` beside it (generated by a small function in `specimen.py`, so every export can have one): the file to print; orientation, layer height, material and supports as doc 04 states them for Stage 2 bodies (quote the section; where doc 04 gives no value, say "not specified" and list it under D5); the water fill with every hole taped; room temperature; one minute of playing before recording; three takes for each of the 13 fingerings; the paired pressure and pitch observations and the onset and break pressures; which lines of `<id>_measurement.toml` to fill; the command `python kernel/fit_measurements.py <file> --write-constants <constants.toml>`; and the sentence that the file must not be marked synthetic.
3. Add to the checklist what the loader rejects (`MeasurementIncomplete`), taken from the loader itself, so the list cannot go stale. `p_pa` is required for every note today; that is D5.
4. A dry run with a SYNTHETIC copy of the template in a temporary folder proves the commands of the checklist work as written. Nothing synthetic is written into the package.

Acceptance: the package holds the body and air STL files, the check report, the inspection, the blank template, the specimen record and the checklist; the dry run fits and a finish from its constants reports an exact match.

### A5. Tuning evidence report (step 4, tooling only)

A report that needs no Blender: `kernel/` stays standard-library Python, so the tool is `tools/tuning_evidence.py` and writes HTML with inline SVG, as `ocarina_addon/inspection.py` does. No plotting package.

1. Inputs: one or more measurement files, optionally the constants file and the specimen record of each.
2. Section "Predicted": the design pitch of each fingering from the sizing, labelled prediction. Section "Measured": mean and spread of the takes in cents, each take a mark. Section "Geometry": the check summary from the specimen record. The three never share an axis or a table column.
3. Per fingering, pressure against cents: every `[[observation]]` as a point with its status (clean, airy, unstable, absent), the takes of `[[note]]`, the onset and break pressures of `[[speaking_range]]` as limits, and a gap where no stable note was seen. Nothing is interpolated across a gap.
4. A4 and B4 (the subhole notes) in their own group, C5 to F6 in another.
5. The pressure fit of `kernel` (see `kernel/test_pressure_response.py` for what exists) is drawn as a description of this body, with its residuals, and is never fed to sizing. The report says so.
6. A file marked synthetic puts SYNTHETIC in the title, in every figure and in the file name.
7. Tests in `tests/test_tuning_evidence.py` on the repository's synthetic files: the three sections exist and are separate; an unstable observation is drawn and not averaged; a missing onset is "not seen"; A4/B4 are grouped apart; the banner is present; a non-finite value fails with the note's name.
8. Add **Open Tuning Evidence** to the sidebar only if a measurement file is selected; the operator calls the tool and opens the page.

Acceptance: the tests; the report of the synthetic example opens from a file URL with no network request.

### A6. Experimental add-on (step 5)

Built on `ocarina_addon/operators.py`, `blender_manifest.toml`, `tools/pack_extension.py` and `tests/extension/`.

1. **Persistent settings.** A `PropertyGroup` on the scene (`scene.oca`): preset, volume, rating, window wall, export folder, calibration file, previous inspection, inspection on or off. The operators read it; their own properties stay for scripts and for the redo panel. Saved with the `.blend`.
2. **Presets with inherited defaults.** Each setting has "preset default" as its unset state, as `rating` has now. The panel shows the resolved value beside it (from `presets.get_preset` and the kernel record), so the owner sees what will be built. No new preset format.
3. **Three explicit actions** in the panel, replacing the single build dialog:
   - *Preview*: `build_body(run_checks=False)`, no export, no cavity-mode step.
   - *Validate*: the checks on the mesh in memory, with the cavity-mode step; writes nothing but a temporary inspection.
   - *Export*: `api.build_checked_body` and `specimen.write_bundle` (for an edited shell: `shell_edit.finish`), into the export folder.
4. **Changed since validation.** Validate stores on the body object a signature of the resolved settings, the voicing hash and, for an edited shell, the calibration identity. The panel compares it on draw (a dictionary compare, no geometry) and shows "validated", "changed since validation" or "not validated". Export of a changed body asks to validate first.
5. **Solver dependency.** An add-on preference `python_path`, put first in `cavity_mode._candidates`. A button "Test solver" runs the existing import probe and shows the result and the Python used. The panel says "cavity-mode check not available" when none is found; the check keeps failing as it does today, it is never skipped silently. Default (D7): an external Python, nothing bundled.
6. **Nothing expensive on a slider.** Property `update` functions only mark the state as changed. A test sets each property and asserts that no mesh was created and that it returned in under 50 ms.
7. **Tests independent of the repository.** Extend `tests/extension/build_in_installed.py`: in the clean profile, with the installed copy only, run preview, validate and export of P4-bowl, then build a base, apply the test boss, finish and export, and check the bundle. Assert that no module was imported from the repository path.
8. **Package.** Version `0.2.0` in the manifest (D9); `tools/pack_extension.py`; `blender --command extension validate` on the ZIP; record the file list and the size.
9. **Stage reports.** Regenerate them with the commands in the notes ("Command that regenerates the sizing table" and the stage commands of `headless.py`), and compare with the committed ones: every difference is listed in the record with its cause. A difference without a known cause stops the release item, not the run.
10. **README.** Installation from the ZIP, the three actions, the solver preference, what "experimental" means here.

Acceptance: the four suites; the clean-profile workflow; the ZIP validates; the stage comparison is listed. Left for B5: whether the panel is pleasant to use.

### A7. Elliptical aperture family (step 3, geometry only)

Skip this package if D1 is answered "drop" before the run starts. Otherwise the default is the three variants below.

1. **Desk table first** (`tools/ellipse_table.py`, kernel only): for the baseline area 62.84 mm², the lengths 7.56, 8.89 and 10.22 mm (−15 %, 0, +15 %), the width W = 4A/(πL) (10.59, 9.00, 7.83 mm), the windway width each needs under the present rule, the kernel's G_w, and whether the bowl and its rim still fit (`bowl_half_length_mm`, `bowl_half_width_mm`). Written to `docs/` as a table. A variant that does not fit is listed as not buildable and is not built.
2. **Kernel.** `"ellipse"` in `voicing.SHAPES`; one outline function returning the polygon and the area, used by sizing, by the add-on's cutter (`voicing_geo`), by the measurement of the window in `checks_geo` and by the hash. `shape` and the two axes enter the hash; the teardrop's hash is unchanged (asserted for every committed preset).
3. **Presets.** Three variants of `P4-bowl` in `variants.toml`, named by their length. The aperture is distinct from the surrounding oval recess: the recess keys are not touched.
4. **Checks.** The measured aperture area and axes against the outline, within the existing tolerance; the bowl local checks; the cavity-mode step.
5. **Comparison.** One inspection per variant with the baseline as previous, in `addon_out/ellipse-step3/`. The report states: equal area does not establish acoustic equivalence, and each variant needs its own calibration.
6. **Tests.** Area of the outline against π·L·W/4; the cut window measured on the mesh; the hash differs from the baseline's and between variants; a calibration fitted for the baseline is a fallback, not an exact match, for each variant.

Acceptance: the tests; the buildable variants have no unexpected failure; the table and the comparisons exist. No print is implied.

### A8. Close the run

1. All four suites; the numbers go into the implementation record with the date and the versions.
2. The implementation record lists, per package: done, skipped (with the reason) or failed (with the output).
3. A list for Phase B: every default that was assumed (D1, D4, D5, D7, D9), every matter of taste found in A3, every stage-report difference from A6.
4. `git status` and a summary of the changed files, for the owner's commit decision (D10). Nothing is committed.

## Phase B: blocked by a decision, a review or a physical test

| Item | What | Blocked by |
|---|---|---|
| B1 | The owner looks at the regenerated inspection (A3): does it show what a maker needs, is anything misleading, which of the matters of taste to change. | review |
| B2 | Print the baseline from the package (A4), measure it, fill the template, fit, finish the same geometry with an exact match (step 2a). The first print freezes the hole layout (doc 04 D10). | D2, D3, D5; a printer, a tuner, a scale, a manometer |
| B3 | The tuning evidence report (A5) on the real file. Read the pressure progression between notes against Hickman's breath curve. | B2 |
| B4 | Print the ellipse variants that D1 keeps, one calibration each, compared with the baseline by ear and in B3's report. | D1, B2 |
| B5 | The owner uses the add-on (A6) from a clean install: preview, validate, export, an edit. What is awkward. | review |
| B6 | Release of the experimental package: where, under which licence, with which minimum Blender. | D6, D9, B5 |
| B7 | Pressure-driven hole sizing. Not started until D8 is answered from data. | B3, D8 |
| B8 | Commit, push and pull request of the work of both phases. | D10 |

## Decisions pending

| # | Decision | Default assumed in Phase A | Blocks |
|---|---|---|---|
| D1 | Step 3: drop it, or which lengths to compare. At the baseline the ellipse differs from the teardrop by 0.05 mm of width. | Keep; −15 %, 0 and +15 % of the length at equal area, geometry only. | A7, B4 |
| D2 | Print the baseline with its two expected pad-limit failures as they are? | Not assumed; the package lists them. | B2 |
| D3 | The questions the notes mark "before Stage 2 is printed" that are still open (`prompts/addon-v1-notes.md`, "Questions for the owner", items 1, 3, 4, 5): the surface of the hand checks, the sideways limit, the lean tolerance. Do they apply to the P4-bowl print, or is the layout accepted as built? | Not assumed. | B2 |
| D4 | Exported ID of an edited specimen. | `<base>-edit-<8 hex of the identity>`; scene names unchanged. | A2 |
| D5 | Measuring kit and protocol: is a manometer available? The template requires a pressure for every note; without one the file cannot be loaded. Also the print settings doc 04 leaves open. | Pressure stays required. | B2 |
| D6 | Licence: the manifest says GPL-3.0-or-later, the repository has no licence file. | Nothing added. | B6 |
| D7 | Cavity-mode solver: an external Python with numpy and scipy (today), or wheels bundled in the extension. | External, set in a preference. | A6, B6 |
| D8 | When may a pressure fit enter sizing: how many bodies, how many repeated sessions, which residual. Step 4 says "repeated physical measurements" without a number. | Never in Phase A. | B7 |
| D9 | Version and minimum Blender of the experimental package. The manifest says 5.1.0; the README says 5.1; every run of this plan was on 5.2.0 LTS. | 0.2.0; minimum left at 5.1.0 and marked "tested on 5.2.0 only". | B6 |
| D10 | Commit and pull request: steps 1 and 2 and their review are uncommitted on `claude/edited-shell-calibration-identity`. One commit per phase item, or one for all? Target `ecan3-experimental`? | Nothing committed. | B8 |

## The steps (reference)

### 1. Edited shell measurements

Compute the geometry-derived calibration identity before exporting an uncalibrated edited shell. Export its STL, resolved settings, blank measurement template and geometry report together. Include the identity and model convention in the template, and expose calibration-file selection in Blender.

Acceptance: export an edited shell, fill and fit its measurements, then finish the same edit with an exact calibration match. A changed window surround invalidates voicing reuse; a changed hole surround invalidates layout reuse. Synthetic fixtures remain labelled synthetic. A measurement file that was touched since its export, a comment included, must not be overwritten by a later build; an untouched blank template may be exported again, so that visual iteration does not need a new folder each time.

### 2. Annotated visual inspection

Generate inspection drawings from the finished mesh and existing check measurements. Show:

- Windway section: exit height, projected jet centreline, labium offset and jet-to-edge distance. The centreline is a geometric guide, not simulated airflow.
- Bowl section and plan: aperture and recess outlines, nominal blend boundary, measured local thickness minima and the distinction between thin plates and intentional edges.
- Thumb face: sealing surfaces and hole clearances, with measured values distinguished from design dimensions.
- Before/after comparison: shared view framing, changed settings and calibration status.

Keep the constrained bowl construction. These views support visual refinement without smoothing away the labium or changing the acoustic model. Provide an inspection report accessible from Blender; full live parameter editing belongs to step 5.

Acceptance: the drawings show what the checks measured beside the design value, and the two agree within the check's tolerance; a value the checks did not measure is shown as not measured, never replaced by the design value. A previous inspection snapshot can be compared at the same scale. Inspection does not alter scene geometry or the voicing hash.

### 2a. Baseline print and measurement

Every calibration so far is synthetic. Before another voicing family is added, print the selected P4-bowl baseline, fill its measurement template and fit it. Steps 3 and 4 depend on it: step 4 plots this data, and step 3 would otherwise compare one uncalibrated voicing with another.

Acceptance: one physical, non-synthetic measurement file of the baseline, fitted, and a finish of the same geometry with an exact calibration match.

### 3. True elliptical aperture

At the baseline the comparison below is too small to measure: the teardrop is 9.05 × 8.89 mm at 62.84 mm², and the equal-area, equal-length ellipse is 9.00 × 8.89 mm. A width change of 0.05 mm is below print resolution. The first comparison therefore needs a different aspect ratio (a longer or shorter L at the same area), or this step is dropped.

Add an explicit ellipse aperture family, distinct from the surrounding oval recess. Share the outline definition across sizing, cutters, measurement and hashing. Begin with equal-area, equal-along-jet-length comparisons, deriving width as W = 4A/(πL), and record any windway-width change. Equal area does not establish acoustic equivalence. Each new voicing requires its own calibration.

### 4. Tuning evidence

Show predicted pitch separately from measured pitch and geometry checks. Plot paired pressure and cents observations per fingering, preserving takes, unstable gaps and onset/break limits. Distinguish A4/B4 from C5–F6. Keep pressure fitting descriptive until repeated physical measurements justify its use in sizing.

Maker guidance connects tuning to the progression of breath pressure between notes: [Robert Hickman, measuring the breath curve](https://pureocarinas.com/measure-ocarina-breath-curve). The coupled jet and resonator require more than the passive resonance model: [Okada et al., ISMA 2019](https://pub.dega-akustik.de/ISMA2019/data/articles/000010.pdf).

### 5. Experimental add-on release

Build on the existing manifest, ZIP packer and installation tests. Add persistent Blender settings, presets with inherited defaults, explicit preview/validate/export actions, changed-since-validation status, and solver dependency configuration. Keep expensive geometry and cavity-mode work off slider callbacks. Test clean installation and the bowl/edit workflow independently of the repository, and regenerate stage reports before release.

## Implementation record

Steps 1 and 2 are implemented as specimen export and portable annotated inspection reports. The Ocarina sidebar exposes build, finish and review actions; the build dialogs accept calibration files and previous inspection snapshots. Export refuses to overwrite a specimen whose measurement file was changed. The full interactive parameter editor remains in step 5.

The thickness maps use the existing normal-probe checks, retaining the thinnest sample in each class per 0.5 mm plan cell for display. Verdicts still use every probe. Before and after thickness maps are separate, with shared framing, so a previous defect is not presented as a current failure. Other sections support toggled overlays.

The selected P4-bowl example and its prior thin-floor regression are exported locally under `addon_out/visual-review-step12/`. The current example retains its two expected pad-limit failures and has no unexpected geometry failure. The test of the measurement-to-calibration cycle uses explicitly synthetic observations; no physical tuning is established.

Step 2a remains planned; the unattended parts of steps 3 to 5 were built in the Phase A run below. Physical calibration, printed elliptical apertures and pressure-driven hole sizing are not part of this implementation.

### Review of steps 1 and 2 (2026-11-26)

- The windway drawing and a table now show the checks' measurements (exit height, labium offset, edge thickness) beside the design values, and the labium edge against the projected jet axis: the distance along it and off it. Without checks they read "not measured".
- An edited shell is exported through the same read-back build as every other body (`api.build_checked_body`), so its report has the air-file measurements. That build now gives the checks the variant's parameters, as the in-memory build does.
- Export is refused only when the measurement file differs from the blank template recorded in the specimen JSON (`blank_template_sha256`).
- The measurement context is the one the build matched constants on (`body.info["calibration_context"]`); it is no longer computed a second time.
- Section coordinates are rounded to a micrometre; the thickness map rings the least sample of each region.
- Open at the review, closed by A2: every finish of one base had the same ID (`<base>-edit`).
- The previews under `addon_out/visual-review-step12/` predated these changes; A3 regenerated them.

### Phase A run (2026-11-26)

Nothing was committed. The baseline's voicing hash is `bcdd90905c01` before and after (asserted in `tests/test_calibrated_variant.py`). Nothing below is tuning evidence.

| Package | Result |
|---|---|
| A1 | Done. `.venv` (Python 3.12.16, numpy 2.5.5, scipy 1.18.1) holds numpy and scipy; the extension tests need `OCARINA_PYTHON`, because the installed copy does not see the repository's `.venv`. The eight sidecar files in `.git/objects/pack/` were removed; `git fsck` still names three `._` sidecars among the loose objects, which were left. Commands are in the README. |
| A2 | Done, with one difference from the plan. The fitter and the calibration use a body's ID as a label only, never as a key, so two files of one ID were never merged. An exported edited specimen is now `<base>-edit-<8 hex>`; the scene objects carry the same name (not the plain `<base>-edit` the plan named), and a finish removes every earlier finish of that base from the scene. A finish without export keeps `<base>-edit`. |
| A3 | Done. `tools/visual_review_examples.py` rebuilds `addon_out/visual-review-step12/` (the earlier files are in `visual-review-step12.before-review/`). `tools/check_inspection.py` agrees on both. `current`: no unexpected failure, the two expected pad-limit failures, 0 wide thin-plate probes. `prior`: `bowl_local_plastic` fails, 312 probes. Two defects of the drawing were fixed: the windway note ran off the page, and a comparison drew the previous aperture in the current one's blue. Previews: `qlmanage -t -s 1400 -o . *.svg`. |
| A4 | Done. `addon_out/baseline-print-P4-bowl-80/`, made with `headless.py -- body --preset P4-bowl --v0 80 --specimen --renders --strict`; first cavity mode 1.36 × F6. Every export now writes `PRINT-AND-MEASURE.md`. A SYNTHETIC copy in a temporary folder was fitted with the checklist's command and rebuilt: voicing and layout matched exactly. |
| A5 | Done. `ocarina_addon/evidence.py` (also `python -m ocarina_addon.evidence`), not `tools/`: it has to be in the packed extension for the panel. 7 tests. The "prediction" shown is the design target of each fingering; a prediction from fitted constants is not drawn. Example: `addon_out/tuning-evidence-example/`. |
| A6 | Done. `scene.oca` settings, Preview / Validate / Export, the status line, the solver preference and Test Solver, Open Tuning Evidence, version 0.2.0. The clean-profile test runs the three actions on P4-bowl and finishes an edited P4 shell with the installed copy only. `dist/parametric_ocarina-0.2.0.zip` (42 files, 251 kB) passes Blender's validation. Not done as planned: Export does not ask to validate first, because it always checks what it writes; presets keep the one "preset default" (the rating), since volume and wall are not preset values. |
| A6 stages | Stages 1, 2 and 3 were regenerated into a scratch folder with Blender 5.2.0 and compared with the committed reports (made with 5.1): no check changed its status in any of the 30 reports. The differences are the command line, the build time, the numpy and Python versions, and last-digit noise (thinnest plastic of P0-80 1.20 → 1.28 mm at a neighbouring ray, seal bands ±0.01 mm, the sign of a zero). The committed reports were not replaced. |
| A7 | Done for two of three variants. `ellipse` is a window shape of the kernel (one outline for sizing, cutter, measurement and hash); a variant sets `window_shape` and `window_length_mm`. See the table below. `tools/ellipse_table.py` was not written: the table has three rows and the variants reproduce it. |
| A8 | Suites below. |

Ellipse variants of P4-bowl at 80 cm³, area 62.84 mm², G_w 5.633 mm (the model's conductance is the same for all three, since it sees the area and the wall only):

| Variant | Length × width mm | Voicing | Windway width mm | Result |
|---|---|---|---|---|
| baseline (teardrop) | 8.89 × 9.05 | `bcdd90905c01` | 9.05 | no unexpected failure |
| `P4-bowl-e756` | 7.56 × 10.58 | `fc17584c9f68` | 10.58 | not buildable: 1.18 mm of plastic around the pipe in the neck (least 1.2 mm) |
| `P4-bowl-e889` | 8.89 × 9.00 | `e02568f6a99c` | 9.00 | no unexpected failure; cut window 8.890 × 9.000 mm, 62.83 mm² |
| `P4-bowl-e1022` | 10.22 × 7.83 | `05bc7c2af5cd` | 7.83 | no unexpected failure; cut window 10.220 × 7.829 mm, 62.83 mm² |

The bowl is P4-bowl's and is placed from the windway exit, so in the 10.22 mm variant the labium sits 1.33 mm further into it. Comparisons with the baseline are in `addon_out/ellipse-step3/`.

For Phase B:

- Defaults that were assumed: D1 (three lengths; one is not buildable), D4 (the ID, as built in A2), D5 (pressure stays required), D7 (external Python), D9 (0.2.0, minimum Blender left at 5.1.0, run on 5.2.0 only).
- Matters of taste in the drawings, for B1: the thumb view shows the window's outline through the body; the thumb labels sit on the sealing rings; the bowl's boundary is drawn for the previous build in the same purple as the current one.
- The 7.56 mm ellipse needs a wider neck or a thinner pipe wall to exist. That is a change to P4-bowl's neck, so it was not made.

Suites after the run (Blender 5.2.0 LTS): kernel 166; plain 147 (2 skipped); extension 4; Blender 88 (1 skipped).

### Validation on 2026-11-26 (before the review and Phase A)

Blender 5.2.0 LTS: the full run passed 164 kernel tests, the 140-test plain-Python suite (2 skipped), the 85-test Blender suite (1 skipped), and 4 clean-profile extension installation tests. The four focused specimen tests also passed after the final provenance changes. These exercise blank export identity, measured chimney dimensions, synthetic file/fit/calibration round trips, exact reuse, invalidation of changed contexts, Blender property registration, and inspection without geometry mutation.

The current and prior bowl thickness maps were rendered and visually checked. The current build has zero wide thin-plate probes; the prior regression has 312. SVG sections and HTML comparisons use a shared coordinate transform. The package `dist/parametric_ocarina-0.1.0.zip` passes Blender's extension validation and includes the new modules. This is an experimental package, with the existing external Python/numpy/scipy requirement for cavity-mode checks.
