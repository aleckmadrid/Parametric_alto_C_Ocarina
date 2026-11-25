# Add-on v1 build notes

Working notes for the add-on build. This file is the hand-over between sessions. Read it first, then `git log` on the working branch.

**Branches (2026-11-17).** **`main` is the current line.** On 2026-11-17 the ECAN3 track (`ecan3-experimental`, PR #1) and then the working branch `claude/optimistic-edison-iibsy5` (all of `addon-v1` C0–C4, the ladder change, the source review and the labium default) were merged into `main`, by owner decision: the rebuilt logic and assumptions replace the earlier, incomplete analysis. `addon-v1` and `ecan3-experimental` are historical; do not start new work from them. Start new work from `main`. The old session prompts in `prompts/` still say `addon-v1`.

**Correction, later on 2026-11-17.** The paragraph above was written on `main` without the local state of the owner's machine. The local `addon-v1` was not historical: it held eight commits that were never pushed (the ergonomics docs 05 and 06, C4b, C5, C6) and uncommitted work (docs 07 and 08, the P4 seed, the ellipse window cut). `origin/main` was merged into the local `addon-v1` (merge commit `583adde`; the branch before the merge is kept as `backup/addon-v1-pre-merge-2026-11-17`). **Until `addon-v1` is pushed and merged, it is the line that holds everything; `main` lacks C4b, C5 and C6.** The η_w amendment that `main` numbered A11 is A15 here, because A11–A14 were already the ergonomics amendments. See "Merge with main and C5 rerun (2026-11-17)".

**Shell-edit prototype (2026-11-18, branch `shell-edit-prototype`).** By owner decision the add-on gets a second way to build: it makes the solid shell and the solid neck, the user edits them, and the add-on cuts the instrument out of them. It is a prototype on its own branch; the stage builds are unchanged. See "Shell-edit build (prototype, 2026-11-18)". Later the same day the owner set the least wall of an edited shell (three printed walls, 1.32 mm) and found the neck of the rules wrong; two rounds of trial necks were built (seven on P4, then ten on P1 and P4 after two bulb models he supplied) and **the choice is open**: see "Owner notes, neck volume trials and next steps".

All constants in this file are **pre-calibration**. Nothing has been printed or measured. Every synthetic value in the repo is labelled synthetic.

## Status

| Checkpoint | Scope | Status |
| --- | --- | --- |
| C0 | Branch, notes, plan | done (commit `860946f`) |
| C1 | Kernel extensions and sizing CLI | done (commits `9eccda1`, `2f1bdbc`), see evidence below |
| C2 | Measurement fitter and input format | done (commits `5ef484f`, `8f10de3`), see evidence below |
| C2b | Kernel corrections: teardrop window at every volume, `k_hole` estimated from the data | done (commit `3f217d3`), see "C2b evidence" |
| C3 | Add-on skeleton, cavity Geometry Nodes, presets P0–P3, volume scaling about the voicing port | done (commit `351407c`), see "C3 evidence" |
| C4 | Voicing geometry, holes, wall stack, Booleans, pre-export checks, STL and air export | done (commit `20b09ae`), see "C4 evidence" |
| C4b | Hand layout fix, soft ergonomic checks, cavity mode from the computed first mode (rules of [docs/06](../docs/06-ergonomics-challenge.md) §5–6, owner decisions of 2026-11-15) | done (commit `0d08e05`), see "C4b evidence". **The owner must read the warnings and decide on the template scale before Stage 2 is printed** (doc 04 D10; "Questions for the owner") |
| Ladder change | Ladder 65 / 80 / 95 cm³ with P0-88 as the prediction body; 125 cm³ and stub V-c dropped; 3 mm window wall option | done, see "Ladder change and window wall option" |
| Source review step 1 | Labium offset default −0.2 mm (coupons 0 / −0.35, never positive); optional `p_break_pa`; η_w planning band 0.85–0.95 (A15); tip radius closed at 1.0 mm | done (commits `0e9743a`, `f3b669d`, `60d20f6`, `8d61969`, plus the −0.35 coupon fix); 125 kernel tests. Blender reports in `addon_checks/` are stale until rerun. See docs/01-source-review.md §6 |
| C5 | Stage commands and Markdown sizing report | done (commit `751d8fd`), see "C5 evidence". **Rerun at the rules of `main` on 2026-11-17** (not committed yet), see "Merge with main and C5 rerun". The sentences that follow describe the first run. Stage 1 and Stage 2 generate with no unexpected failure. Stage 3 runs from the synthetic constants and reports one real conflict (open problem 19) |
| C6 | Headless tests, README, packing of the extension, final pass | done (commit `6da438b`), see "C6 evidence and final pass" |

**Owner decisions of 2026-11-15 (after doc 06).** (1) C4b builds the rules of doc 06 §5–6: subholes 9.5 mm from L ring and 7.5 mm from R middle along each hand line's normal, the revised `ergo_*` checks, parent search over both hands; Q8 answered (L ring), Q12 answered (P0 keeps the taped layout, labelled). (2) Q9/A12: the add-on's cavity-mode verdict comes from the computed first mode of the capped air mesh (`tools/cavity_modes_fd.py` method): ok ≥ 1.3 × F6, needs_fem 1.0–1.3, fail < 1.0; the kernel's c/(2L) check stays unchanged as a reported number. (3) Short decks (P3) overlap the hands along their lines and keep the finger pitch (doc 06 §3.5); open problem 8 then becomes warnings. (4) The next run does C4b, C5 and C6 in that order. Still open: Q10/Q11 (outer body, P4) after a hand check on a printed P2.

**After C6: windway position, body shape and the body library (2026-11-16, [docs/07](../docs/07-windway-and-body-shape.md), [docs/08](../docs/08-stage2-body-library.md)).** The owner supplied photos of two ceramic designs: the Songbird Ocarina of Time 12-hole (sold as an Alto C and as a larger, lower "Tenor A") and the Spencer OoT alto C. Findings: the mouthpiece meets the body at 0.36 of the body length from the bulb end on both, and the presets (0.31–0.37) are inside the range of all references, so `port_u` stays; P2's cavity has a waist (2.0 mm in the plan, 1.2 mm on the deck) that neither ceramic body has; the ceramic bodies are slimmer (width / length 0.35) and rounder (thickness / width about 0.8) than every preset. Two test bodies were built with `tools/geometry_check_variant.py` (which now takes comma-separated lists): `P2-80-seed`, the fitted Songbird outline (no unexpected failure, 2 warnings against P2's 5, first cavity mode 1.36 × F6), and the flatter `P2-80-seedflat` (1.29 × F6, needs_fem). **The owner decided on 2026-11-16 that the seed joins Stage 2.** Doc 08 assesses every present body and recommends: keep P0, add the seed, keep P2 and P1 as acoustic bodies, stash P3, drop the old P4 proposal. **The owner saved that recommendation as the Stage 2 plan "for now" on 2026-11-16 (set A, round seed); it is provisional.** **Nothing was changed in the presets, the stage lists, the layout rules or the limits: the changes of doc 08 §6 are not made yet** (items 14 to 17 under "Questions for the owner"). Not committed. A correction made the same day: the first pass read the measured Songbird photo as the Tenor A (8 in); it is the Alto C, whose length the maker does not state (estimated 170 mm, 152–181 mm allowed). Fractions of the body length and the seed body did not change. Later the same day the owner added an edge view of the Spencer and three workshop pictures from the maker (doc 07 §3.9, the Spencer report §7). Readings: the Spencer is about 45 mm thick (thickness / width 0.79) and holds about 70 cm³ of air (65–80); about two thirds of the body is clay; the thumb-face half is hollow only in three pockets and solid in the tail; the chamber is about 131–136 mm long in a body of 165 mm. A model solved with the add-on's cavity-mode solver (`Analizes_ocarinas/Spencer_OoT_12h/internal_cavity_check.py`): first mode 1.34 × F6 for an even shell of 70 cm³, 1.48 with the solid tail, 1.39 with low ridges between the pockets, 1.21 with walls up to the joint plane. The seed's chamber (132 mm, 1.36 × F6) is about the Spencer's. No add-on code changed. **Built on 2026-11-17 on the owner's go-ahead:** preset `P4` ("P4 seed", the values of `P2-80-seed`), `P4-80` in place of `P3-80` in `STAGE2_BODIES` and `STAGE3_BODIES`, P3 kept as a preset in no stage list, the tests, doc 04 (shapes, stage tables, budget: Stage 2 815 g, Stage 3 749 g) and doc 02 Q11. The cavity check, `P4-80`, Stage 2 and Stage 3 were rebuilt. The kernel was not touched: its synthetic test set still labels its third shape P3.

**Next concrete step (2026-11-17, after the merge and the C5 rerun).** (1) The owner reviews the working tree and says what to commit: the merge is committed, the rerun and the geometry experiments are not. (2) The owner decides how the 3 mm window wall is built (open problem 22) or drops stub V-a3 and P0-95-w3. (3) Then push `addon-v1` and merge it into `main`. The questions under "Questions for the owner" still stand; Stage 1 (V-a, V-b, V-d, V-a0, V-a35) can be printed now.

**Next concrete step (2026-11-18, after the owner's decisions were applied).** (1) The owner confirms the angle of the pipe inside the standing neck (built: 10° under the neck, +5° against the body; see "Owner decisions applied"). (2) The owner says what to commit: everything since pull request 3 is uncommitted on `addon-v1`. (3) Stage 1 can then be printed: V-a and V-af first, then V-b, V-d, V-a0, V-a35. The other items of doc 09 section 8 (the prior of the position factors, a prediction body above the ladder, the row limit for round bodies) and open problem 22 (the 3 mm wall) still wait.

**Re-analysis of 2026-11-18 ([docs/09](../docs/09-kernel-and-decisions-challenged.md)); nothing was changed in the kernel, the add-on, the presets or the tests.** `addon-v1` was pushed and merged into `main` on 2026-11-18 (pull request 3), so steps (1) and (3) above are done. Doc 09 challenges the kernel, the suite and the decisions of 15–17 November against the Heuer series, the reference library and the Spencer and Songbird instruments. New script: `Analizes_ocarinas/Kernel_challenge/kernel_vs_references.py`. Its findings wait for the owner (doc 09 section 8) and are open problems here:

- **27. Closed 2026-11-18: the fingering order is the Asian system** (owner decision, on the condition that it stays compatible with one subhole per hand; it does). See "Fingering order switched (2026-11-18)" below.
- **28. Three made instruments cut the top of the scale smaller than the kernel and the right hand larger** (thumbs 0.77–0.83, L pinky 0.47–0.75, right hand 1.07–1.21 of the kernel's diameters). The prior of 1 for every position factor is what the first prints rest on. "The design breaks at about 74 cm³" (doc 04) does not hold.
- **29. Answered 2026-11-18: what "lowered" means.** *(Later the same day the neck became a standing one, and "lowered" is now the pipe 10° under the neck, +5° against the body: see "Owner decisions applied". The stub is V-a against V-af.)* The owner: "With lowered I mean tilted towards the body hidden by the neck volume, the pivot remains with the voicing alignment." That is what the add-on builds (negative `windway_pitch_deg`; the neck does not turn; the pivot is the lip edge). The direction is settled. Still to do, and not a question for the owner: the tilt is in no hash, and no reference shows how such a jet speaks, so it needs a Stage 1 stub of its own (doc 09 section 3.1). The owner also confirmed the smooth cavity for now: experimental internal cavities (partitions, solid tail; item 19 of the questions list) are not being implemented yet.
- **30. Closed 2026-11-18 (owner decision 4): the windway is 3.0 mm high at the mouth end.** It was 1.56 mm; every reference has 2.5–4.5 mm.
- **31. The proven volume band reaches about 100 cm³** (Songbird Alto C, an estimate). Doc 04's table of analysed instruments lacks the Spencer and the Songbird.

Open problem 24 (the cut is not hashed) has an estimate now: the ellipse cuts read 23–29 cents flat of the fan cut on a duct model. The tilt, the shelf and the pocket blend are not hashed either.

*Before the merge this paragraph said:* All checkpoints C0 to C6 are done. Nothing has been printed. Before Stage 2 is printed the owner answers the questions under "Questions for the owner" (items 1 and 2 change the hole layout, which is frozen by the first print). Stage 1 can be printed now: it has no holes. A next session starts with `python tools/run_tests.py` (all four suites) and then acts on the answers.

## Add-on modules (`ocarina_addon/`, since C3 and C4)

| Module | Role | Needs Blender |
| --- | --- | --- |
| `blender_manifest.toml`, `__init__.py`, `operators.py` | The extension, its two operators and the bare menu. | yes |
| `headless.py`, `api.py` | Headless entry (`cavity`, `body`, `stage1`, `stage2`, `stage3`) and the Python API. `api.build_checked_body` builds a body, reads the STL back from disk and runs every check on that file. | yes |
| `kernel_bridge.py` | The only place that imports the kernel; finds the parameter file. | no |
| `presets.py`, `presets/cavity_presets.toml` | Cavity presets P0–P3 as numbers. | no |
| `cavity_math.py` | The cavity surface as plain mathematics: points, normals, port frame, arc lengths. | no |
| `cavity_nodes.py`, `cavity.py` | The Geometry Nodes groups built from Python; the cavity object and its mesh. | yes |
| `holes_layout.py` | Hole positions: Miracle template by arc length, subhole slides along the hand-line normal, hand overlap for short decks, the P0 test layout, the edge-gap rule. | no |
| `ergonomics.py` | Hand-frame metrics of a layout and the soft `ergo_*` checks (docs/06 §5). Standard library only; `measure_cad_references.py` imports it. | no |
| `cavity_mode.py`, `cavity_mode_solver.py` | The cavity-mode desk check. `cavity_mode.py` finds a Python with scipy and runs `cavity_mode_solver.py` there on the exported air mesh. The solver file is stand-alone (numpy, scipy). | no (the solver needs scipy) |
| `report.py` | The Markdown check report of a body (checks, warnings block, hand-layout tables, volumes, Booleans, voicing, holes) and the report of a stage (summary table, three blocks, sizes against doc 04, the kernel sizing of every body). | no |
| `stub.py` | The Stage 1 voicing stubs: the recipes of doc 04 and the sizing record of a body without holes. | no |
| `stages.py` | `run_stage1`, `run_stage2`, `run_stage3`: build every body of a stage, write the files and the stage report. | yes |
| `voicing_geo.py` | Voicing solids from the `Voicing` record: block, pocket, window with labium ramp, windway. | yes (imports `meshutil`, which imports `bpy`; the kernel test of the labium sign reads `windway_centre_z` from the source instead) |
| `body.py` | The build: wall stack, Booleans with assertions, capped air, export. Since the shell-edit prototype also `build_body(outer=...)`: the build from a shell and a neck that the user edited. | yes |
| `shell_edit.py` | The shell-edit build (prototype, branch `shell-edit-prototype`): `build_base` makes the solid shell and neck to edit, `finish` builds the body from them. See "Shell-edit build (prototype, 2026-11-18)". | yes |
| `checks_geo.py` | Measurements on the mesh and the pre-export checks, the `ergo_*` checks and the cavity-mode verdict. Statuses: `pass`, `needs_fem`, `fail`, `warn`, `info`. | yes |
| `meshutil.py`, `export.py` | Mesh arrays, volume, topology, Booleans, column integration, cleanup; STL read and write. | yes (export.py: numpy only) |
| `render.py`, `render_body.py` | Workbench views and section drawings. | yes |

Tests: `tests/` (plain Python), `tests/blender/` (inside Blender, started by `tests/run_blender_tests.py`), `tests/extension/` (the install test), `tools/run_tests.py` (all suites with one command). Packing: `tools/pack_extension.py` writes `dist/parametric_ocarina-<version>.zip` (`dist/` is not in git).

Outside the package: `tools/geometry_check.py` and `tools/geometry_check_body.py` (the check script), `tools/geometry_check_variant.py` (one body with preset values overridden), `tools/cavity_modes_fd.py` (the cavity-mode table for reference chambers; it imports the solver of the add-on), `tools/stub_eta_w.py` (η_w from filled stub measurement files), `addon_checks/` (reports), `addon_renders/` (pictures), `addon_out/` (STL files; ignored by git).

## Kernel modules (all standard library, no Blender imports)

All modules sit flat in `kernel/` and import each other by plain module name (`import ocarina_kernel as ok`). The tests add `kernel/` to `sys.path`. The add-on must do the same.

| Module | Role | Status |
| --- | --- | --- |
| `ocarina_kernel.py` | Equations, air properties, conductance, fixed-point solver, Monte Carlo. Existing; gets only small additions (k constants). | existing |
| `voicing.py` | Voicing rules: window sizing (a teardrop at every volume; a rounded rectangle only when forced), the window outline as a polygon, windway numbers, W/h check, version hash. Numbers only, no mesh. | C1, C2b |
| `holes.py` | Per-hole sizing with chimney-volume fixed point, position factors, inward tubes, k 0.8 and k 1.0 results. | C1 |
| `checks.py` | Range-ratio check and cavity-mode check, each returning a pass/fail result object. | C1 |
| `sizing.py` | Top level `size_body()` that joins voicing, holes and checks; command-line entry that prints the doc 04 table. | C1 |
| `measurements.py` | Reads and writes the hand-filled measurement TOML. Writes the blank template. Since C5 also the stub file (`stub_template`, `write_stub_file`, `load_stub`). | C2, C5 |
| `fitter.py` | Fits one body or many bodies. Returns η_w·G_w, per-hole conductance, k_hole, position factors, corrected diameters. | C2 |
| `calibration.py` | Reads and writes the fitted-constants TOML that Stage 3 reads. `size_body_from_calibration()` sizes a body with fitted constants. | C2 |
| `config.py` | `load_params()` reads `params/alto_c_12hole.toml`. | C1 |
| `synthetic.py` | SYNTHETIC data generator for tests and examples. Writes `measurements/` and `calibration/` examples. | C2 |
| `fit_measurements.py` | Command line: fit measurement files, print the report, write the constants file. | C2 |
| `noise_study.py` | Noise study of the fitter on synthetic data. | C2 |

## Data flow

```
params/alto_c_12hole.toml ──► voicing.py ──► window + windway numbers + hash
                                   │
         target V0, rating ────────┤
                                   ▼
                              sizing.py ──► holes.py ──► diameters (k 0.8 print, k 1.0 nominal), tubes
                                   │
                                   └──► checks.py ──► range ratio, cavity mode

printed body ──► measurement TOML ──► measurements.py ──► fitter.py ──► calibration TOML
                                                                            │
                                                  sizing.py (Stage 3) ◄─────┘
```

## Design decisions (this session)

These refine, and do not reopen, the decisions in the task prompt.

1. **k split.** `k_window = 0.80` (fixed). `k_hole`: prior 1.0, first-print value 0.8. TOML key `k_end` is replaced by three keys. `alto_c_study.py` keeps its doc 03 numbers by using `k_window` for the window and the first-print k (0.8) for the holes.
2. **doc 04 table reverse-engineered.** The table reproduces exactly with a uniform 4 mm chimney (wall only, no tubes), k_hole = 1.0, a 1.0 mm teardrop tip radius, and a rounded rectangle with 1.0 mm corner radius. The sizing code uses these as rules, so the table regenerates.
3. **Teardrop limit (changed in C2b).** At width = length the two-circle teardrop is a circle of area π(W/2)². Before C2b the window became a rounded rectangle above that area. Since C2b it stays a teardrop and grows wider than long (see "Decisions made in C2b").
4. **Voicing hash.** It hashes the numbers that define the voicing geometry (window shape and size, windway, labium, wall, offsets, rule version), rounded to 1 µm. It does not hash V0 directly. V0 enters through the solved window area. This way a stub that carries the 80 cm³ window has the same hash as the 80 cm³ body. That is the point of Stage 1.
5. **Inward tubes.** The floor applies to the printed (k 0.8) diameter. A tube is the shortest length, in 0.5 mm steps, that lifts the printed diameter to 3.0 mm. The tube length adds to the chimney. The report gives plain-wall diameters (the doc 04 numbers) and tubed diameters separately. The tube wall displaces a little air, and the report states it.
6. **Fitter.** One body gives η_w·G_w from the all-closed note, then one hole conductance per note pair. Across holes and bodies a single `k_hole` and per-hole position factors ψ are fitted. ψ is shared by hole name between bodies of the same shape. Since C2b the fitter makes two estimates of `k_hole` and reports both (see "k_hole: two estimates").

## Build order

1. C0: branch, this file.
2. C1a: k split in the TOML and kernel constants; `alto_c_study.py` still reproduces `docs/generated/study-output.md`.
3. C1b: `voicing.py` and its tests.
4. C1c: `holes.py`, `checks.py`, `sizing.py` and the CLI; compare against the doc 04 table.
5. C2a: `measurements.py`, the template, the synthetic example.
6. C2b: `fitter.py`; synthetic recovery tests; noise study.
7. C2c: `calibration.py`, the synthetic constants file; handoff section.

## C1 evidence

- `python -m unittest discover -s kernel -v`: 56 tests, all pass (9 old, 47 new in `test_voicing.py` and `test_sizing.py`).
- `python kernel/alto_c_study.py` regenerates `docs/generated/study-output.md` byte-identical after the k split (`git diff docs/` is empty).
- Doc 04 table: every window width, windway width, sub_R, L_index and E6 thumb diameter (k 1.0, plain 4 mm wall) is within 0.05 mm of the doc. P0 lengths are within 0.5 mm. Window area / V0^(2/3) is within 0.0006. Test: `TestDoc04Table.test_every_listed_size_within_0p05_mm`.
- Doc 04 quotes for the k split reproduce: at 80 cm³ the holes grow by +0.12 mm (sub_R) up to +1.68 mm (E6 thumb) from k 0.8 to 1.0, and holes sized at k 0.8 that behave like k 1.0 play −16 cents at B4 and −109 cents at F6. Test: `test_k_split_numbers_quoted_in_doc04`.
- Round trip: holes sized with tubes and position factors predict every note back within 1e-6 cent at three different k.

## Differences from docs, and which side is right

| Item | Doc | Kernel | Reading |
| --- | --- | --- | --- |
| Volume where the teardrop becomes wider than long | 88.6 cm³ (doc 04, corrected in C2b; it said "about 85 cm³" and named a switch to a rounded rectangle) | 88.6 cm³ | Agree since C2b. A teardrop at width = length is a circle of 9.65 mm; that circle has 73.1 mm², which needs 88.6 cm³. There is no switch any more: the window stays a teardrop. |
| Window and windway width at 95, 110 and 125 cm³ | 11.1 / 14.7 / 18.6 mm teardrops (doc 04, rewritten in C2b; before: rounded rectangles 8.5 / 10.6 / 12.9 mm) | 11.10 / 14.66 / 18.57 mm | Agree since C2b. The window areas (81.2 / 101.4 / 123.5 mm²) and every hole size did not change. |
| Window area at 65 cm³ | 47 mm² | 46.5 mm² | The doc rounded the area from the rounded width (7.0 mm). The widths agree within 0.05 mm. No action. The 125 cm³ row now reads 123 mm² (the CLI prints 123.5 as 123) and stub V-c reads 123.5 mm². |
| Hole diameters in doc 04's table | plain wall, no tubes | table printed plain; tubes reported beside it | The table lists the sub_R at 2.2 mm (65 cm³). With the 3 mm floor rule that hole gets a 5 mm inward tube and its bore becomes 3.03 mm (print) and 3.11 mm (k 1.0). The CLI prints both. |
| P2 tailed gourd at 80 cm³ | "already at the cavity-mode limit" | c/(2·126 mm) = 0.987 × F6, status `fail` | Matches the doc's words. The plan prints it on purpose. The check reports the maths and has no waiver. The C5 session must treat this one result as expected. |
| P1 at 80 cm³ (111 mm) | not stated | 1.12 × F6, status `needs_fem` | Within the plan's FEM-first band. |

## Decisions made in C1

- **Unknowns the docs did not state, taken from the table:** teardrop tip radius 1.0 mm, rounded rectangle corner radius 1.0 mm, chimney 4.0 mm everywhere for the plain wall. All three are in `params/alto_c_12hole.toml` under `[voicing_rules]` and `[hole_rules]`.
- **Tube rule.** The floor (3.0 mm) applies to the printed diameter (k 0.8). The tube is the shortest, in 0.5 mm steps, that lifts that bore to the floor. The same chimney length is used for the k 0.8 and the k 1.0 solution, so a tubed hole has one geometry and two diameters. Stage 3 can pass `tubes_mm` to keep the tubes fixed.
- **Volume bookkeeping.** V0 is the capped air with every chimney inside (doc 03 section 1). So V0 = V_cavity_mesh − tube plastic + Σ A_i·wall_i, and `cavity_volume_for_mesh_cm3` = (V0 + tube plastic − Σ A_i·wall_i) / volume_factor. At 80 cm³ the holes hold about 1.9 cm³ of air, so the mesh is smaller than V0. The tube plastic is 0.05 to 0.09 cm³. `wall_chimney_air_cm3` and `tube_plastic_cm3` are separate fields. The areas are those of the floor-key (printed) diameters. A first version of this field forgot the hole air; the advisor caught it, and a test now checks the identity.
- **Hash.** It hashes the voicing geometry numbers (rounded to 1 µm, negative zero removed) and the rule version. `rating` and V0 are not in it. Stubs are built with `make_voicing(V0, shape=...)`, so a stub that carries the 80 cm³ window has the 80 cm³ hash.
- **Fixed-voicing mode.** `size_body(voicing=v, eta_w=fitted)` keeps a printed window and re-solves the holes. With no `v0_cm3` it retargets V0 so that A4 is on pitch. With `v0_cm3` it keeps the volume and reports the A4 error in cents.
- **Temperature.** `ocarina_kernel.internal_air_temp_c(room_c)` is the one rule for sizing and the fitter: 27 °C at a 22 °C room, plus 0.31 °C per °C of room (params `[temperature]`). The constants file will record it.
- **Flat module layout.** Modules import each other by plain name, because the tests use `sys.path` on `kernel/`. The add-on must put `kernel/` on `sys.path` (or vendor the folder).
- **`k` defaults.** `conductance`, `hole_diameter` and `solve_linear_fingering` still default to k 0.80. New code always passes k explicitly.

## C2 evidence

- `python -m unittest discover -s kernel -v`: **100 tests, all pass** (9 old, 47 for C1, 44 for C2); the verbose run ends with `Ran 100 tests` and `OK`.
- Recovery of invented truth within 1 %, **through measurement files** (the test writes the synthetic TOML, loads it, then fits): nine bodies (P0 at 65, 80, 95, 125 cm³; two more P0-80; P1-P3 at 80 cm³), different room temperature per body, tubes at 65 cm³, measured diameters and V0 that differ from the design, per-hole position factors 0.83 to 1.13. On noise-free data eta_w, k_hole and all twelve position factors are recovered to better than 1e-5 relative error (`test_nine_bodies_clean_truth_is_exact`). With 0.04 mm hole scatter, 0.4 % volume scatter and 0.6 % window scatter added, k_hole is within 1 %, eta_w within 1 %, position factors within 3 % (`test_nine_bodies_with_awkward_truth`). A single body recovers everything to 1e-3 (`test_single_body_recovers_everything`).
- Corrected diameters: with the true physics, the diameters the fitter reports put every note above A4 on pitch within 0.02 cent (`test_corrected_diameters_put_every_note_on_pitch`). The Stage 3 loop is closed in the synthetic world: holes sized from fitted constants play within 0.1 cent (`test_stage3_corrected_body_hits_the_scale_in_the_synthetic_world`).
- Blank template: loads as valid TOML, and `load_measurement` raises `MeasurementIncomplete` with a list of 40 missing items.
- The constants file written from synthetic input has `synthetic = true` and a banner, and the reader keeps the flag (tests `test_synthetic_label_is_carried_to_the_file`, `test_repo_synthetic_files_are_labelled_and_load`).

### Noise study (SYNTHETIC data; `python kernel/noise_study.py --runs 30`; table regenerated in C2b)

Invented truth: eta_w 0.86, k_hole 1.07, position factors 0.83 to 1.13 with geometric mean 1, multiplied by the "psi scale" of the row. Noise is added **per take**, then the takes are averaged. Errors are relative to the truth, in percent. 30 runs per row, seed 11. "k_hole in use" is the estimate that drives the position factors and the corrected diameters (see "k_hole: two estimates" below).

| Case | psi scale | noise per take | takes | eta_w·G_w err % (med / p95) | k_hole in use err % (med / p95) | profile drives (runs) | k_hole profile err % (med / p95) | k_hole convention err % (med / p95) | psi err % all holes (med / p95) | psi err % sub1, sub2, R_middle (med / p95) | unresolved holes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| one body | 1 | none | 3 | 0.000 / 0.000 | 0.00 / 0.00 | 0 of 1 | – | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0 |
| one body | 1 | ±1 cents uniform | 3 | 0.024 / 0.058 | 0.06 / 0.17 | 0 of 30 | – | 0.06 / 0.17 | 0.23 / 0.72 | 0.24 / 0.95 | 0 |
| one body | 1 | ±2 cents uniform | 3 | 0.048 / 0.116 | 0.12 / 0.34 | 0 of 30 | – | 0.12 / 0.34 | 0.46 / 1.43 | 0.48 / 1.91 | 0 |
| one body | 1 | ±5 cents uniform | 3 | 0.120 / 0.290 | 0.30 / 0.81 | 0 of 30 | – | 0.30 / 0.81 | 1.13 / 3.57 | 1.20 / 4.78 | 0 |
| one body | 1 | ±5 cents uniform | 1 | 0.271 / 0.553 | 0.39 / 1.49 | 0 of 30 | – | 0.39 / 1.49 | 2.03 / 6.26 | 3.01 / 7.79 | 0 |
| one body | 1 | σ 5 cents | 3 | 0.273 / 0.554 | 0.50 / 1.40 | 0 of 30 | – | 0.50 / 1.40 | 1.86 / 6.83 | 2.46 / 8.03 | 0 |
| one body | 1 | ±10 cents uniform | 3 | 0.241 / 0.580 | 0.64 / 1.57 | 0 of 30 | – | 0.64 / 1.57 | 2.25 / 7.18 | 2.40 / 9.58 | 0 |
| nine bodies | 1 | none | 3 | 0.000 / 0.000 | 0.00 / 0.00 | 1 of 1 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0 |
| nine bodies | 1 | ±1 cents uniform | 3 | 0.012 / 0.029 | 0.22 / 0.62 | 30 of 30 | 0.22 / 0.62 | 0.03 / 0.07 | 0.19 / 0.53 | 0.21 / 0.51 | 0 |
| nine bodies | 1 | ±2 cents uniform | 3 | 0.024 / 0.058 | 0.44 / 1.25 | 30 of 30 | 0.44 / 1.25 | 0.05 / 0.15 | 0.37 / 1.06 | 0.42 / 1.02 | 0 |
| nine bodies | 1 | ±5 cents uniform | 3 | 0.060 / 0.146 | 1.16 / 3.19 | 30 of 30 | 1.16 / 3.19 | 0.16 / 0.39 | 1.01 / 2.63 | 1.05 / 2.54 | 0 |
| nine bodies | 1 | ±5 cents uniform | 1 | 0.112 / 0.236 | 0.32 / 0.66 | 0 of 30 | 3.01 / 6.59 | 0.32 / 0.66 | 0.85 / 2.75 | 1.00 / 3.58 | 0 |
| nine bodies | 1 | σ 5 cents | 3 | 0.114 / 0.247 | 3.07 / 7.21 | 30 of 30 | 3.07 / 7.21 | 0.26 / 0.58 | 1.84 / 5.45 | 1.53 / 3.86 | 0 |
| nine bodies | 1 | ±10 cents uniform | 3 | 0.120 / 0.291 | 2.39 / 6.75 | 30 of 30 | 2.39 / 6.75 | 0.40 / 0.79 | 2.09 / 5.31 | 2.03 / 5.35 | 0 |
| one body | 1.2 | none | 3 | 0.000 / 0.000 | 28.10 / 28.10 | 0 of 1 | – | 28.10 / 28.10 | 17.12 / 20.79 | 13.01 / 13.24 | 0 |
| one body | 1.2 | ±5 cents uniform | 3 | 0.120 / 0.290 | 28.06 / 28.72 | 0 of 30 | – | 28.06 / 28.72 | 17.02 / 21.87 | 12.33 / 15.63 | 0 |
| nine bodies | 1.2 | none | 3 | 0.000 / 0.000 | 0.00 / 0.00 | 1 of 1 | 0.00 / 0.00 | 27.58 / 27.58 | 0.00 / 0.00 | 0.00 / 0.00 | 0 |
| nine bodies | 1.2 | ±2 cents uniform | 3 | 0.024 / 0.058 | 0.40 / 1.24 | 30 of 30 | 0.40 / 1.24 | 27.59 / 27.67 | 0.35 / 0.98 | 0.36 / 0.92 | 0 |
| nine bodies | 1.2 | ±5 cents uniform | 3 | 0.060 / 0.146 | 1.14 / 3.13 | 30 of 30 | 1.14 / 3.13 | 27.57 / 27.96 | 0.95 / 2.51 | 0.98 / 2.35 | 0 |
| nine bodies | 1.2 | ±10 cents uniform | 3 | 0.120 / 0.291 | 2.22 / 6.56 | 30 of 30 | 2.22 / 6.56 | 27.73 / 28.25 | 1.92 / 4.97 | 1.90 / 4.78 | 0 |
| one body | 0.8 | none | 3 | 0.000 / 0.000 | 42.54 / 42.54 | 0 of 1 | – | 42.54 / 42.54 | 25.92 / 31.48 | 19.70 / 20.05 | 0 |
| one body | 0.8 | ±5 cents uniform | 3 | 0.120 / 0.290 | 42.62 / 43.35 | 0 of 30 | – | 42.62 / 43.35 | 26.03 / 34.00 | 18.36 / 23.82 | 0 |
| nine bodies | 0.8 | none | 3 | 0.000 / 0.000 | 0.00 / 0.00 | 1 of 1 | 0.00 / 0.00 | 41.76 / 41.76 | 0.00 / 0.00 | 0.00 / 0.00 | 0 |
| nine bodies | 0.8 | ±2 cents uniform | 3 | 0.024 / 0.058 | 0.46 / 1.28 | 30 of 30 | 0.46 / 1.28 | 41.73 / 41.93 | 0.40 / 1.12 | 0.46 / 1.16 | 0 |
| nine bodies | 0.8 | ±5 cents uniform | 3 | 0.060 / 0.146 | 1.34 / 3.32 | 30 of 30 | 1.34 / 3.32 | 41.65 / 42.19 | 1.14 / 2.84 | 1.18 / 3.00 | 0 |
| nine bodies | 0.8 | ±10 cents uniform | 3 | 0.120 / 0.291 | 2.82 / 7.01 | 30 of 30 | 2.82 / 7.01 | 41.25 / 42.34 | 2.31 / 5.71 | 2.35 / 6.09 | 0 |

How to read it.

- **eta_w·G_w** does not depend on the k_hole estimate. Its error stays under 0.3 % (95th percentile) at ±5 cents and under 0.6 % at ±10 cents, because the all-closed note has the whole window weight.
- **One body** has only the convention estimate. If the position factors really average 1 (psi scale 1), k_hole is within 0.8 % at ±5 cents (95th percentile) and the position factors within 1.1 % (median) and 3.6 % (95th percentile). If they average 1.2 or 0.8, one body gives a k_hole that is 28 % or 43 % off and position factors that are 17 % or 26 % off (median), with or without noise. One body cannot see this.
- **Nine bodies, convention holds (psi scale 1).** The profile estimate drives. It is noisier than the convention estimate: at ±5 cents and 3 takes, 1.2 % (median) and 3.2 % (95th percentile) against 0.16 % and 0.39 %. The position factors follow: 1.0 % and 2.6 % against 0.49 % and 1.62 % before C2b. This is the price of not assuming that the position factors average 1.
- **Nine bodies, convention broken (psi scale 1.2 or 0.8).** The profile estimate keeps the same error (1.1 to 1.3 % median, 3.1 to 3.3 % at the 95th percentile, ±5 cents). The convention estimate is 28 % or 42 % off at every noise level. The position factors are recovered with their true scale (1.0 to 1.1 % median).
- **One take per note.** With a single take the fitter has no spread and uses a pitch uncertainty of 5 cents. The profile interval is then wider than the 15 % limit, and the convention estimate drives (row "±5 cents uniform, 1 take": 0 of 30). Three takes are needed for the profile estimate to drive.
- The weights use one pitch uncertainty per body (the root-mean-square of the notes' standard errors, `sigma_mode="pooled"`). The noise is Gaussian with σ 5 cents in the "σ" rows and uniform ±5 cents in the others. No hole was unresolved in any run.
- **The full prompt's criterion "position factors within 1 % with ±5-cent noise" cannot pass as written:** the 95th percentile is 2.5 to 3.6 %. The noise-free 1 % criterion passes (errors below 1e-4).

### k_hole: two estimates (C2b, owner decision 2; replaces the old "k and psi convention" paragraph)

k_hole and a common scale of the position factors cannot be separated in one body. The fitter therefore makes two estimates and reports both, in `FitResult`, in `format_report` and in the constants file.

- **Profile estimate** (`FitResult.k_hole_profile`: `k_hole`, `lo`, `hi`, `sigma`, `chi2_min`, `dof`, `informative`). Bodies of one shape share one psi per hole name. The P0 ladder bodies have the same hole names at different diameters, so only one k lets a single psi per hole fit all of them. For each candidate k the fitter removes the best psi of every group and sums the weighted squares of what is left of ln G (weights as before, `k_bounds` as before). The k with the smallest sum is the estimate. The interval is where the sum stays within 1 of the minimum (a one-sigma likelihood interval), widened by the reduced chi-square when the fit is worse than the pitch noise. This estimate assumes nothing about the size of psi.
- **Convention estimate** (`FitResult.k_hole_convention`). The value that makes the geometric mean of the P0 position factors equal to 1. It was the only estimate before C2b. It always exists and has little noise, but it is right only if the position factors really average 1.
- **Rule for which one drives** (`FitResult.k_hole`, `k_hole_source`, `k_hole_rule`). The profile estimate drives when its interval lies inside `k_bounds` and its half-width is at most 15 % of its value (`fitter.K_PROFILE_MAX_REL_HALFWIDTH`). Otherwise the convention estimate drives. Reason for 15 %: in the synthetic world a k error of 28 % moves the P0-110 prediction by about 10 cents (Gate 3 allows about 20), so 15 % costs about 5 cents. `fit_bodies(..., k_source="profile" | "convention")` forces one of them.
- **Message.** Whenever the convention value lies outside the profile interval, `FitResult.messages` says so, and the report prints it.
- **One body, or bodies with equal holes** (the three P0-80 copies alone) have a flat profile. The profile estimate is then marked `informative = False`, and the convention estimate drives, as before C2b.
- **Position factors.** With the profile estimate the position factors are no longer scaled to a geometric mean of 1. Their mean is a result: `FitResult.psi_geomean_reference`.

Audit numbers reproduced in C2b (noise-free synthetic data, nine bodies): with psi scaled by 1.05 / 1.2 / 1.4 / 0.8 the convention estimate returns 0.985 / 0.775 / 0.566 / 1.517 for a true 1.070; the profile estimate returns 1.0700 every time. P0-110, sized from the fitted constants and played with the true physics, is off by 3.9 / 10.2 / 9.4 / 26.6 cents (worst note) with the convention estimate and by 0.00 cents with the profile estimate. With ±5 cents of noise (3 takes, 12 seeds) the P0-110 error with the profile estimate is 1.5 to 2.5 cents (median) and at most 3.7 cents.

On the repository's synthetic round-1 files (`measurements/synthetic-round1/`, Gaussian noise of 2 cents per take, diameters rounded to 0.05 mm, pitches to 0.1 Hz, mass to 0.1 g; invented truth k_hole 1.07 with position factors that obey the convention): **profile 1.134, interval 1.086 to 1.185 (±4.4 %); convention 1.069 ± 0.003**. The profile estimate drives. It is 6 % above the truth and 1.3 interval half-widths away. The interval knows the pitch noise only; the 0.05 mm rounding of the measured diameters is not in it. This is a known limit: see open problem 7.

**Gate 2 numbers.** With psi free, one body has 13 pitches and 13 unknowns, so its residual is zero. The honest numbers are `FitResult.pooled_psi1` (one eta_w per voicing hash, one k_hole, psi = 1, all bodies together) and `BodyFit.rms_shared_psi_cents` (shared psi, the body's own eta_w: shows whether bodies of one shape agree). On the synthetic set the pooled psi = 1 residual is 21.9 cents rms, which comes from the invented position factors (±15 %). The Gate 2 limit of 30 cents rms would pass on this synthetic set.

## Decisions made in C2

- **File format: TOML**, one file per body. A TOML file is easy to fill by hand and `tomllib` reads it with no extra package. The generator writes the template with design numbers filled in (hash, window area, chimney and design diameter per hole, target pitch per note). The person types only the measured values: `water_net_mass_g`, `water_temp_c`, `room_temp_c`, `d_measured_mm` per hole, `hz` (or `cents`) and `p_pa` per note, three takes each.
- **Water fill.** The input is net mass and water temperature. The loader converts it to V0 with the density of water (Tanaka formula). The kernel's V0 holds every hole chimney but not the window throat and not the windway. Two yes/no lines in `[fill]` say whether water also filled them; the loader then subtracts their volume. The template pre-fills both volumes from the voicing numbers. Setting `windway_in_fill = true` with no windway volume is rejected.
- **Hole offset** is one number, the mean of (measured − design) over all holes and bodies. `d_cad_needed_mm` = needed physical size − offset.
- **Corrected diameters** are physical sizes for the body as built, using the body's own eta_w·G_w and measured V0, and the shared position factors. A positive `ream_mm` means ream open. A negative value means the hole is already too big and cannot be fixed (flag `too_big_cannot_ream`). A flag `above_pad_limit` marks a needed size over 10 mm (finger) or 12 mm (thumb). The all-closed note (A4) is reported separately as `a4_error_cents`; holes cannot fix it.
- **Position factors are shared by shape.** Bodies of one shape share one psi per hole name. The reference shape (default: the shape with most bodies) fixes the scale. A whole-scale offset of P1-P3 against P0 shows as a difference in eta_w among bodies with the same voicing hash, and as a pattern in their psi.
- **Weights.** The relative error of each hole conductance comes from the pitch uncertainty of the two notes that bracket it. That uncertainty is one value per body: the root-mean-square of the notes' standard errors (floor 1 cent; 5 cents when there is a single take). The ln-conductance of each hole is weighted by its inverse variance. The correlation between neighbouring holes is ignored.
- **Unresolved holes.** If the conductance of a hole comes out at or below zero, the hole is flagged `unresolved` and left out of the fit. The fit does not fail.
- **Temperature.** The fitter and the sizing use one rule: `ocarina_kernel.internal_air_temp_c(room_c)`. The constants file records the rule. A wrong room temperature moves eta_w: 10 °C of room error is about 1 %.
- **Breath curve.** p0 and alpha come from a least-squares line of ln p against semitones. The pitch is not corrected for blowing pressure.
- **Stage 1 stubs.** A stub has no holes. `voicing.stub_pitch_hz()` predicts its pitch, and `fitter.eta_w_from_stub()` returns eta_w from one measured pitch. No file format for stubs exists yet (open question 4).

## C2b evidence

- `python -m unittest discover -s kernel -v`: **120 tests, all pass** (100 before C2b; 5 of them were rewritten for the new rules, 20 are new).
- Window: the 65 and 80 cm³ windows keep their numbers and their hashes (`6aa0038008cc`, `d1b6418b1844`; test `test_old_teardrops_are_unchanged`). No rounded rectangle is chosen at any volume from 40 to 140 cm³ and for all three ratings. The window length is constant. Width, windway width and area grow together with V0 in a sweep from 60 to 140 cm³, with no step at 88.6 cm³. The forced rectangle still works (V-b, 62.8 mm²). The hash is stable and changes with every voicing input, for an old teardrop and for a wide one.
- New sizes (`python kernel/sizing.py --table`, also in doc 04):

| V0 | Window (length × broad end) | Area | Windway exit (height × width) | Broad end length along the jet | W/h | Hash |
| --- | --- | --- | --- | --- | --- | --- |
| 65 cm³ | 9.65 × 6.96 mm | 46.5 mm² | 1.20 × 6.96 mm | 6.96 mm (circle) | 8.04 | `6aa0038008cc` (unchanged) |
| 80 cm³ | 9.65 × 8.81 mm | 62.8 mm² | 1.20 × 8.81 mm | 8.81 mm (circle) | 8.04 | `d1b6418b1844` (unchanged) |
| 95 cm³ | 9.65 × 11.10 mm | 81.2 mm² | 1.20 × 11.10 mm | 9.21 mm (ellipse) | 8.04 | `622bdad5acb2` |
| 110 cm³ | 9.65 × 14.66 mm | 101.4 mm² | 1.20 × 14.66 mm | 8.40 mm (ellipse) | 8.04 | `a01cb7f7f544` |
| 125 cm³ | 9.65 × 18.57 mm | 123.5 mm² | 1.20 × 18.57 mm | 7.76 mm (ellipse) | 8.04 | `f3803f8358b6` |

  W/h is the window length over the exit height, so it is 8.04 at every step. The exit slot itself goes from 5.8 : 1 (65 cm³) to 15.5 : 1 (125 cm³) in width over height.
- Fitter: noise-free recovery with psi scaled by 1.2 and by 0.8 (k_hole and all position factors within 1e-4, through measurement files; P0-110 on pitch within 0.1 cent): `test_noise_free_recovery_when_the_convention_is_broken`. Single body unchanged: `test_single_body_keeps_the_convention`. Noise case: `test_with_noise_the_profile_stays_near_the_truth` (±5 cents, 3 takes, 6 seeds, k within 15 % = 3 interval half-widths, P0-110 within 6 cents).
- `python kernel/synthetic.py --write-examples` regenerated the synthetic files. Only `P0-95`, `P0-125` (new hash and window width) and the constants file changed.
- `python kernel/alto_c_study.py` still regenerates `docs/generated/study-output.md` byte-identical.

## Decisions made in C2b

- **Shape family for a teardrop wider than long.** The outline is the convex hull of a broad end and the tip circle (radius 1.0 mm, far point at the labium). The broad end is an ellipse with its back vertex at the windway exit: half-width a = width / 2 across the jet, half-length b along the jet. Up to width = length, b = a (a circle): this is the old two-circle teardrop, unchanged. Above it, b = (length / 2) · (length / width)^(1/3). At width = length both give the same circle, so there is no step. The exponent is `[voicing_rules] teardrop_wide_exponent`.
- **Why this family.** The rules ask for a broad end at the windway, a 1.0 mm tip at the labium, a constant length, an area that grows with the width and a smooth outline. An ellipse of full length (b = length / 2) would be the simplest choice and gives the narrowest windows (10.7 / 13.4 / 16.3 mm), but it swallows the tip: the window would be an oval, not a teardrop. Letting the broad end become shorter along the jet as it becomes wider keeps the tip as a separate narrow end. With the exponent 1/3 the widths (11.1 / 14.7 / 18.6 mm) stay inside the owner's rough estimate (11–12 / 13–15 / 16–19 mm), and the sides of the ellipse stay rounder than the tip (side radius 3.8 / 2.4 / 1.6 mm). An exponent of 1/2 gives 11.3 / 15.3 / 19.5 mm and a side radius of 1.2 mm at 125 cm³.
- **Geometric reason the shape near the limit is not teardrop-like.** At the old limit the old family is already a circle: the tip circle lies inside the broad circle. Any continuous family passes through that circle. So between about 85 and 95 cm³ the window is a near-circle with a small nose. No ladder step is in that range. The 65 and 80 cm³ windows did not change.
- **Upper end of the family.** The family ends where the sides of the ellipse would be sharper than the tip (b²/a = tip radius): width 24.8 mm, 158 mm², 146.4 cm³ (medium window). `make_voicing` raises `ValueError` above it. `voicing.teardrop_max_v0_cm3()` gives the number.
- **Hash.** `rule_version` stays 1, and the hashed fields of the old teardrops are unchanged, so their hashes are unchanged. A teardrop wider than long also hashes `broad_end_length_mm` and `wide_exponent`.
- **Outline.** `Voicing.outline_mm()` returns the window outline as a closed polygon of (x, y, outward normal angle), with x = 0 at the windway exit and x = length at the labium. The add-on must use it, so that the shape rule lives in one place. The polygon is inscribed: its area is about 0.01 % under the record's area.
- **Renamed.** `voicing.teardrop_to_rectangle_v0_cm3` is now `voicing.teardrop_circle_limit_v0_cm3`. `voicing.teardrop_max_area` is now `voicing.teardrop_circle_limit_area`.

## C3 evidence

Command (from the repository root; Blender 5.1.2):

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python tools/geometry_check.py -- cavities --renders
```

- Report: `addon_checks/C3_cavities.md` (table) and `addon_checks/C3_cavities.json`. Pictures: `addon_renders/C3_cavities/P0` … `P3` (six views, three sections, and `sheet.png` with all of them).
- **All 20 cavities pass** (P0–P3, each at the mesh volume of the 65, 80, 95, 110 and 125 cm³ bodies; this includes every Stage 2 volume).
- Volume: the measured mesh volume is within 0.00004 % of `cavity_volume_for_mesh_cm3` in every case (limit 0.5 %). The node group scales the mesh to the target itself.
- Voicing port: the port is the origin. The nearest mesh vertex is 4 to 9 millionths of a millimetre from the origin at 40 cm³ ("before") and at the target ("after"). The mesh normal at the port does not turn (0.0000°).
- Topology: every mesh is one closed shell, manifold, with no zero-length edge, no degenerate triangle and no self-intersection (32,512 triangles each).
- Mesh against formula: the mesh and the Python copy of the formula agree within 0.00002 mm.
- Measured spine lengths at the 80 cm³ body (mesh volume 78.11 cm³): P0 78.39 mm, P1 110.14 mm, P2 125.02 mm, P3 94.34 mm. Doc 04 gives 79, 111, 126 and 95 mm for 80 cm³ of cavity. The mesh is smaller by the air in the holes (about 1.9 cm³), so the lengths are 0.8 % shorter. The presets are calibrated to the doc lengths at exactly 80 cm³.
- I looked at the four sheets. They agree with the numbers: P0 is the 2.2 : 1.5 : 1 egg, P1 a teardrop with the bulb at the left-hand end, P2 a large bulb with a long narrow tail, P3 a slimmer egg on a bent spine. The port marker sits on the lower player-side quadrant, with the jet arrow pointing away from the player.
- `python -m unittest discover -s kernel -v`: 120 tests pass (unchanged by C3).

## Decisions made in C3

- **Folder layout.** `ocarina_addon/` is the extension (`blender_manifest.toml`, id `parametric_ocarina`). `tools/geometry_check.py` is the check script. `addon_checks/` holds its reports and `addon_renders/` its pictures.
- **Kernel access.** `ocarina_addon/kernel_bridge.py` is the only place that imports the kernel. It puts the kernel folder first on `sys.path`, drops any foreign module called `config`, `checks`, `holes`, … from `sys.modules`, and checks that every kernel module came from the kernel folder. It looks for `<add-on>/kernel` first (a packed copy, for an installed extension) and then for `<repository>/kernel`. The parameter file is found the same way, and the add-on always passes `params=`. **Packing the kernel and the TOML into the extension zip is not done yet (C6).**
- **Units and axes.** 1 Blender unit = 1 mm. X runs along the body from the left-hand end to the right-hand end, +Y points away from the player, +Z is the finger deck. Thumbs and voicing are on the −Z side. **The voicing port is the origin of every body.**
- **Cavity formula** (`ocarina_addon/cavity_math.py`, mirrored by the node group in `cavity_nodes.py`). The body is sampled by an angle θ along the spine (t = (1 − cos θ) / 2) and an angle φ around the section. Half-width = L/2 · S_w(t) · sin θ, and the same for the height, where S is a Catmull-Rom spline through the 7 station values. sin θ is the envelope of an ellipse, so equal station values give an exact ellipsoid and the station value is then width / length. The section is a superellipse. The spine is a circular arc in the XY plane.
- **Node group.** "OCA Cavity" has the 14 station values, the section exponent, the bend, the port position, the target volume and the resolution as inputs. It welds the seam and the poles, triangulates, moves the port to the origin, measures the mesh volume (sum of area × normal · centre / 3) and scales by the cube root about the origin. It stores the solved scale as the attribute `oca_scale`. The port is snapped to a grid vertex in Python before the inputs are set, so the origin is a mesh vertex.
- **Presets** (`ocarina_addon/presets/cavity_presets.toml`; station values are full width or height over spine length):

| Preset | Width stations | Height stations | Exponent | Bend | Port (along spine, angle) | Why |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | 0.6818 × 7 | 0.4545 × 7 | 2.0 | 0° | 0.50, 45° | The exact 2.2 : 1.5 : 1 ellipsoid of doc 04. |
| P1 | 0.4584, 0.4859, 0.4676, 0.4034, 0.3301, 0.2659, 0.2200 | 0.70 × width | 2.0 | 0° | 0.36, 45° | A plain teardrop: widest at about 1/3 of the length, even taper to a tail about half as wide in shape factor. One multiplier on all stations sets the length to 111 mm at 80 cm³. At 80 cm³ the bulb is 49 × 34 mm. |
| P2 | 0.4056, 0.4720, 0.4277, 0.2950, 0.2212, 0.1917, 0.1770 | 0.66 × width | 2.2 | 0° | 0.30, 45° | A large bulb (51 × 34 mm at 80 cm³) and a long tail that narrows from about 30 to 13 mm, after the Miracle planform. One multiplier sets the length to 126 mm at 80 cm³. The slightly boxier section is a guess. |
| P3 | 0.5333 × 7 | 0.3333 × 7 | 2.0 | 20° | 0.34, 45° | The 3 : 1.6 : 1 ellipsoid of doc 04 on a gently bent spine. The bend moves both ends away from the player. Provisional, as in doc 04. |

- **Port position.** The port is on the lower player-side quadrant of the section (45° from the bottom toward the player), on the bulb. There the section has a radius of 20 to 25 mm along the jet. The jet runs along the section, away from the player. The windway then leaves the body tangentially toward the player and upward, which gives room for the mouthpiece.
- **Renders.** Workbench renders are posterised to 40 grey levels, which makes the PNG files three times smaller. Section pictures are not renders: they are drawn from the plane-mesh intersection (solid dark, air white, 10 mm grid).

## C4 evidence

Commands (from the repository root; Blender 5.1.2). The first builds one body, the second runs the geometry check on it, the third runs the check on the whole C4 set:

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python ocarina_addon/headless.py -- body --preset P1 --v0 80 --out addon_out/P1-80
```

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python tools/geometry_check.py -- body P1 80 --renders
```

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python tools/geometry_check.py -- bodies --renders
```

The check script builds each body, writes the STL files to `addon_out/<body>/` (not committed), **reads the body STL back from disk** and measures that file. Reports: `addon_checks/<body>.md` and `.json`. Pictures: `addon_renders/<body>/` (six views, a close view of the window, sections along the windway, across and through the window, through the finger rows and the thumbs, and along every inward tube; `sheet_views.png` and `sheet_sections.png` hold them side by side). One body takes about 45 s.

**Result at C4: 7 of 8 bodies had no unexpected failure. P3-80 failed one check that the notes did not expect (`hole_layout`).** This section is the record of C4 (commit `20b09ae`). C4b changed three things in it, and "C4b evidence" has the present state: P3-80 now builds with no unexpected failure; the kernel's `cavity_mode` result is shown as `cavity_mode_c2L` with status `info` and is no longer a failure of P1 or P2; the subholes and the P2 and P3 layouts moved, so the "smallest hole gap" column is the C4 value. The acoustic numbers in the table (capped air, diameters, chimneys, windows) are unchanged.

| Body | Capped air, measured on the STL | Largest hole diameter error | Largest chimney error | Window measured (length × width, area) | Smallest hole gap | Failed checks |
| --- | --- | --- | --- | --- | --- | --- |
| P1-80 | 80.010 cm³ (+0.013 %) | 0.0000 mm | −0.0010 mm | 9.650 × 8.806 mm, 62.83 mm² | 4.55 mm | `cavity_mode` needs FEM (expected), `hole_limits[print]`, `hole_limits[nominal]` (expected) |
| P0-80 | 80.009 cm³ (+0.011 %) | 0.0000 mm | −0.0021 mm | 9.650 × 8.806 mm, 62.83 mm² | 4.28 mm | `hole_limits[print]`, `hole_limits[nominal]` (expected) |
| P0-65 | 65.008 cm³ (+0.012 %) | 0.0000 mm | −0.0058 mm | 9.650 × 6.959 mm, 46.47 mm² | 4.01 mm | `hole_limits[nominal]` (expected) |
| P0-95 | 95.013 cm³ (+0.013 %) | 0.0000 mm | −0.0023 mm | 9.650 × 11.102 mm, 81.14 mm² | 4.52 mm | `hole_limits[print]`, `hole_limits[nominal]` (expected) |
| P0-110 | 110.017 cm³ (+0.016 %) | 0.0000 mm | −0.0024 mm | 9.650 × 14.658 mm, 101.37 mm² | 4.56 mm | `hole_limits[print]`, `hole_limits[nominal]` (expected) |
| P0-125 | 125.025 cm³ (+0.020 %) | 0.0000 mm | −0.0007 mm | 9.650 × 18.568 mm, 123.48 mm² | 4.42 mm | `hole_limits[print]`, `hole_limits[nominal]` (expected) |
| P2-80 | 80.009 cm³ (+0.011 %) | 0.0000 mm | −0.0016 mm | 9.650 × 8.806 mm, 62.83 mm² | 4.55 mm | `cavity_mode` fail, 0.99 × F6 (expected), `hole_limits[print]`, `hole_limits[nominal]` (expected) |
| P3-80 | 80.009 cm³ (+0.011 %) | 0.0000 mm | −0.0041 mm | 9.650 × 8.806 mm, 62.83 mm² | 3.52 mm | `hole_limits[print]`, `hole_limits[nominal]` (expected); **`hole_layout` (not expected)** |

What holds for every body in the table:

- **Phase 4 gate.** All 12 hole diameters (area of the bore in a slice at mid wall) match the kernel within 0.0001 mm, and all chimney lengths (a ray along the hole axis through the wall before the hole is cut) within 0.006 mm. The limit is 0.05 mm.
- **Volume.** The cavity mesh (loft joined with the voicing pocket) is within 0.0002 % of `cavity_volume_for_mesh_cm3`. The capped air, measured on the STL by column integration, is within 0.020 % of `v0_cm3`. The limit is 0.5 %. The air mesh that is exported gives the same volume within 0.005 %.
- **Booleans.** 17 to 19 Booleans per body, all with the Manifold solver (the Exact fallback was never needed). Every result is manifold, and every volume change matches its expected value: holes within 1.2 % of area × chimney, tubes of 1.5 mm or more within 2.7 % of their cylinder (a 0.5 mm tube within 1 mm³), the window and windway cuts within 0.3 % of an independent column integration.
- **Topology of the STL.** One closed manifold shell, no boundary edge, no zero-length edge, no zero-area triangle, no self-intersection, genus 13 (12 holes, the window and the windway).
- **Voicing.** Window length, width and area, windway exit and inlet height and width, labium angle (20.00°), edge thickness (0.400 mm) and labium offset (0.000 mm) measured on the mesh agree with the `Voicing` record within 0.001 mm and 0.02 % of the area. The hash is intact. The windway exit faces the labium, the broad end is at the windway, the window opens outward, and nothing intrudes into the keep-outs.
- **Wall.** The plain wall measures 4.000 mm (minimum over 2,300 rays from the cavity to the outside). Away from the voicing and the tubes, the thinnest plastic of the finished bodies is 3.07 mm (between holes, P1-80).
- **Inward tubes.** P0-65 has two (sub1 0.5 mm, sub2 5.0 mm), P0-80, P1-80, P2-80 and P3-80 one (sub2 3.0 mm), P0-95 one (1.5 mm), P0-110 one (0.5 mm), P0-125 none. Measured tube lengths match the kernel within 0.001 mm and the tube wall is 1.198 mm (1.2 mm asked). Every tube ends at least 22 mm from the opposite wall and 29 mm from the labium.
- I looked at the view sheet or the section sheet of every one of the eight bodies (`sheet_views.png`, `sheet_sections.png`), and at the window close views of P1-80 and P0-125. They agree with the numbers: the windway comes from the player side, its floor ends at the exit, the window opens outward through a 4 mm throat, the 0.4 mm labium edge with the 20° ramp is on the far side, the holes are on the deck with the thumbs and the voicing underneath, and the 5 mm tube of P0-65 shows its 1.2 mm walls. On the P0 bodies the "row" sections cut almost along the wall, because the test layout is staggered and not in rows; they show the bores as circles with the gaps between them.
- **A picture fault that was fixed.** Early pictures showed a small cube in the window. It was Blender's default 2 mm cube at the scene origin, which is where the voicing port is. It was never part of a body or of an STL file. The renderer now hides every object that it did not create, and all pictures in the repository were made after that fix.
- `python -m unittest discover -s kernel -v`: 120 tests pass (C4 did not change the kernel).

**A fault that the checks found and that was fixed.** The first build left a thin lip of plastic across part of the inner rim of the large thumb hole. The hole cutter stopped 0.6 mm inside the cavity at the hole centre, but on a curved wall the cavity surface at the rim of a 12.7 mm hole lies 1.1 mm deeper. The "thinnest plastic" measurement read 0.02 mm there. The cutter now reaches below the deepest point of the wall under each hole (`body.rim_depth`).

### Windway width at the top of the ladder (recorded in C4; partly moot since the ladder change)

Since 2026-11-17 only the 95 cm³ row is printed (110 and 125 cm³ are range checks). The question still applies there: on a 4 mm window wall the 95 cm³ windway is 11.1 mm wide and the mouthpiece stub 19.1 mm; the 3 mm wall option gives a 9.5 mm window (see "Pending owner decisions").

| P0 body | Window and windway width | Mouthpiece stub width | Body width | Nearest hole edge to the labium ramp | Nearest hole edge to the voicing block | Plastic under the windway floor at the exit | Free depth below the window |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 95 cm³ | 11.10 mm | 19.1 mm | 56.6 mm | 22.7 mm | 21.4 mm | 2.02 mm | 35.0 mm |
| 110 cm³ | 14.66 mm | 22.7 mm | 59.3 mm | 23.4 mm | 21.4 mm | 1.86 mm | 36.6 mm |
| 125 cm³ | 18.57 mm | 26.6 mm | 61.9 mm | 23.9 mm | 21.3 mm | 1.75 mm | 38.1 mm |

The widest teardrop windways fit the P0 body and both keep-outs at 110 and 125 cm³. No sample point within 10 mm of the labium is plastic, and nothing stands above the 45° flare. The mouthpiece stub at 125 cm³ is 26.6 mm wide, which is wide for the lips; that is a comfort question for the owner, not a geometry failure. Renders: `addon_renders/P0-110/` and `addon_renders/P0-125/` (`voicing.png`, `section_window_plan.png`).

## Decisions made in C4

- **Voicing frame.** The voicing is built in its own frame and placed at the port. The origin is the labium point (the far end of the window on the centre line) in the inner plane. x runs along the jet, y across, z outward. The inner plane sits 0.05 mm outside the cavity surface at the port, so the flat plane and the curved cavity never touch.
- **Voicing pocket.** The cavity is curved and the voicing needs a flat inner face, so that the window throat is exactly 4.0 mm deep on every body with the same hash. A flat-topped air pocket fills the gap between the inner plane and the curved cavity under the window and 3 mm around its labium half. It adds 0.13 to 0.24 cm³ of air. The loft is made smaller by that amount, so that loft plus pocket equals `cavity_volume_for_mesh_cm3`. The kernel's "cavity mesh" is therefore the loft joined with the pocket.
- **Windway.** A tapered slot, 30 mm long, as wide as the broad end of the window. The taper is symmetric about the centre line. The floor ends at the exit plane (a straight edge, 0.05 mm before it). The roof ends on the rounded broad end of the window, so the slot runs on under the roof to the widest point of the window. The windway and the window sit in a block with a flat outer face (the voicing patch, 4.0 mm). The block is also the mouthpiece stub: 4 mm of plastic beside the windway, 3.2 mm above (3.0 mm at the −0.2 mm labium default since 2026-11-17), 2.4 mm below at the mouth end.
- **Labium.** The edge is a 0.4 mm land at the inner plane. Above it the wall is cut back at 20° from the outline, outward, around the labium half of the window. The ramp has its full angle where the outline normal is within 60° of the jet and fades to nothing at the widest points. **Labium offset convention:** the mid-height of the edge is `labium_offset_mm` above (outward of) the windway centre line. **Decided 2026-11-17:** default −0.2 mm (edge below the jet centre, as Heuer sets it), coupons 0 and −0.35 mm, never positive. The far coupon is −0.35, not −0.4: at −0.4 the windway floor past the exit would lie exactly on the pocket ceiling (z = 0), a coplanar Boolean case (`test_every_labium_option_keeps_the_floor_clear`). The test `test_labium_sign_matches_the_addon_geometry` reads `voicing_geo.windway_centre_z` and fails if the sign is flipped. At the default the windway sits 0.2 mm further out: the roof is the window wall minus 1.0 mm at the exit (3.0 mm at 4 mm, 2.0 mm at 3 mm); the thinnest case, 3 mm wall with the −0.35 coupon, leaves 1.85 mm at the exit and 1.67 mm at the inlet, above the 3-perimeter minimum (about 1.35 mm). A 2.5 mm window wall would leave 1.32 mm at the inlet at the default, below that minimum: with this voicing block the usable window walls are 3.0 mm and up (the options are 3.0 and 4.0).
- **Holes.** A 64-sided cutter whose area equals the area of the circle (`mesh_hole_segments`, the kernel's `polygon_circumradius_for_area`). The axis is the cavity normal at the hole centre. An inward tube is a 64-sided cylinder of radius d/2 + 1.2 mm from 2 mm inside the wall to the tube length inside the cavity; the hole is then cut through wall and tube.
- **Hole layout** (`ocarina_addon/holes_layout.py`). P1–P3: the Miracle positions in millimetres (section 4.2), wrapped by arc length along the top or bottom line of the body from the layout centre (16 mm toward the tail from the port station, as on the Miracle; P2 23 mm since the slide) and then around the section. The subhole rule of C4 (both subholes 6 mm off the finger line on the far side) was replaced in C4b: see "Decisions made in C4b". P0: a compressed test layout given as fractions of the spine length (`P0_RELATIVE`), so every P0 body has its holes at the same relative places. The smallest edge gap is 4.0 mm or more on every P0 body from 65 to 125 cm³. No centre had to move on any body that was built.
- **Wall stack.** Skin = cavity moved outward by 4.0 mm along the vertex normals. Envelope = skin joined with the voicing block. Body = envelope minus (cavity joined with pocket), plus tubes, minus holes, minus window, minus windway. The finger deck and the thumb area have no separate patch yet: with a uniform 4 mm wall they would be the same surface. `body.OUTER_MESH_HOOK` is the place where a user outer mesh will be joined to the envelope (not built).
- **Capped air.** Two results. (1) An air mesh built beside the body: cavity plus pocket, minus the tubes, plus every hole up to the outer skin. It is exported as `<id>_air_capped.stl`, and with the window throat added as `<id>_air_fem.stl`. (2) A measurement on the final body mesh without any Boolean: the volume that is inside the envelope, outside the plastic and on the cavity side of the window and windway caps, integrated along columns of 0.25 mm (`body.measure_capped_air_cm3`). A Boolean of the envelope with the body fails, because the two share most of their surface; the column method does not mind.
- **Cleanup.** After the last cut, points closer than 1 µm are merged and zero-area triangles are dissolved (up to 10 µm when needed). Nothing is remeshed or smoothed. The result is accepted only if it is manifold and the volume moved by less than 0.05 mm³.
- **Port stations of P2 and P3 moved in C4** (P2 0.28 → 0.30, P3 0.42 → 0.34 of the spine), so that the hand template has about the same usable deck on both sides of the layout centre. The C3 cavity check was run again with the new presets (all 20 cavities pass); the C3 pictures and report in the repository are the new ones.
- **Expected failures** are coded in `checks_geo.expected_failure`. Since C4b the list is: `hole_limits[nominal]` from 65 cm³ and `hole_limits[print]` from 80 cm³. Everything else counts as unexpected. (At C4 the list also held the kernel's `cavity_mode` results for P1 and P2; C4b removed them, because that result is now reported with status `info`.)

## C4b evidence

Commands (from the repository root; Blender 5.1.2). The first rebuilds and checks all eight bodies with pictures, the second builds the P3 comparison with 6 mm of hand overlap:

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python tools/geometry_check.py -- bodies --renders
```

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python tools/geometry_check_variant.py -- P3 80 ov6 hand_overlap_mm=6 --renders
```

Reports: `addon_checks/<body>.md` and `.json` (each has a "Warnings" block and a "Hand layout" section). Pictures: `addon_renders/<body>/` (the top view has the hole names; the bottom view names the thumb holes; every P0 picture has the caption "taped test body, not a hand layout"). One body takes about 50 s, of which the cavity-mode step takes 5 s.

**Result: all eight bodies build with no unexpected failure.** The only failed checks are the two pad-limit checks that the plan expects (`hole_limits[print]`, `hole_limits[nominal]`). Every `ergo_*` check is `pass` or `warn`.

| Body | First cavity mode (computed) | c/(2L), kernel, `info` | Smallest edge gap | Warnings |
| --- | --- | --- | --- | --- |
| P1-80 | 2277 Hz = 1.63 × F6, pass | 1.13 | 3.63 mm (sub1–L_ring) | `ergo_hand_span`, `ergo_rest_space`, `ergo_hole_lean_end`, `ergo_hole_lean_side` |
| P2-80 | 1959 Hz = 1.40 × F6, pass | 0.99 | 3.63 mm (sub1–L_ring) | `ergo_finger_pitch`, `ergo_hand_span`, `ergo_rest_space`, `ergo_hole_lean_end`, `ergo_hole_lean_side` |
| P3-80 | 2452 Hz = 1.76 × F6, pass | 1.32 | 3.41 mm (sub2–L_index) | `ergo_finger_pitch`, `ergo_hand_span`, `ergo_hand_offset`, `ergo_index_meet`, `ergo_rest_space`, `ergo_hole_lean_end` |
| P0-65 | 3133 Hz = 2.24 × F6, pass | 1.69 | 4.01 mm | all 11 `ergo_*`: taped test body |
| P0-80 | 2927 Hz = 2.10 × F6, pass | 1.57 | 4.28 mm | all 11 `ergo_*`: taped test body |
| P0-95 | 2772 Hz = 1.98 × F6, pass | 1.49 | 4.52 mm | all 11 `ergo_*`: taped test body |
| P0-110 | 2637 Hz = 1.89 × F6, pass | 1.42 | 4.56 mm | all 11 `ergo_*`: taped test body |
| P0-125 | 2533 Hz = 1.81 × F6, pass | 1.36 | 4.42 mm | all 11 `ergo_*`: taped test body |

The hand layout of the three hand bodies. "Cavity" is measured between hole centres on the cavity surface (this decides the checks); "skin" is the same at the outer skin (open problem 15).

| Quantity (ok range) | P1-80 | P2-80 | P3-80 |
| --- | --- | --- | --- |
| sub1 from L_ring, cavity / skin (7–11 mm) | 9.50 / 10.7 mm, 0° off the normal | 9.50 / 10.5 mm, 0° | 9.50 / 10.5 mm, 0° |
| sub2 from R_middle, cavity / skin (7–11 mm) | 7.50 / 8.6 mm, 0° | 7.50 / 8.5 mm, 0° | 7.50 / 8.2 mm, 0° |
| Hand span left / right, cavity (50–60 mm) | **48.9** / 50.2 mm | **48.9** / 50.8 mm | **49.4** / 51.0 mm |
| The same at the skin | 52.3 / 51.9 mm | 52.2 / 51.0 mm | 51.5 / 53.6 mm |
| Finger pitch, left, pinky→index, cavity (16.5–20.5 mm) | 17.2 / 17.6 / 16.9 | 17.1 / 17.6 / **16.4** | 17.0 / 17.4 / **16.3** |
| Finger pitch, right, cavity | 17.2 / 18.0 / 17.3 | 17.1 / 18.0 / 16.8 | 17.1 / 18.1 / 17.1 |
| Finger pitch at the skin, left; right | 18.7 / 18.7 / 18.0; 18.0 / 18.3 / 18.0 | 18.4 / 18.8 / 17.5; 17.4 / 18.0 / 16.9 | 18.0 / 18.0 / 17.0; 18.4 / 18.8 / 17.8 |
| Land past the pinky holes from the hole edge, bulb / tail (≥ 10 mm) | **5.2 / 4.8** mm | **9.4** / 12.4 mm | 10.0 / **7.8** mm |
| Pinky lean toward the end, L / R (≤ 20°) | **38° / 30°** | **29°** / 12° | **23° / 31°** |
| Lean away from the covering hand (≤ 5°) | R pinky **13°** | R pinky **7°** | – |
| Hand lines: angle (±10°), apart across (18–28 mm) | 2.1°, 21.1 mm | 2.6°, 18.7 mm | −5.3°, **17.5** mm |
| R index from L index, across / along (18–28; −22 to +5 mm) | 21.1 / −0.4 | 18.7 / +0.7 | **17.6 / −23.3** |

Bold = outside the ok range, so the check warns. The arch and thumb checks pass on all three. **These are measurements, not targets: nothing was tuned to clear a warning.** The wrapped template is a few percent smaller than the Miracle's on the cavity surface (left span 48.9 mm against 50.9 mm). Whether to scale the template, and on which surface to measure, is the owner's decision before Stage 2 is printed.

Acceptance list of C4b, with the output:

- **Subholes.** sub1 is 9.50 mm from L_ring and sub2 7.50 mm from R_middle on P1-80, P2-80 and P3-80, each 0° off the normal of its own hand line, on the fingertip side (limits: 9–10.5 mm, 7–8.5 mm, 20°). Seen in the top views: sub1 lies toward the player from L_ring, sub2 away from the player from R_middle.
- **Edge gap.** Smallest 3.41 mm (P3-80, sub2 to L_index); limit 3.4 mm. Every `inward_tubes` check passes (sub2 has a 3 mm tube on the 80 cm³ bodies: 17 to 28 mm to the opposite wall, 34 to 46 mm to the labium).
- **`ergo_*`** report `pass` or `warn` only. On P0 all eleven report `warn` with "taped test body, not a hand layout".
- **Reference rows.** `ergonomics.hand_metrics` gives the same numbers as the old code of `measure_cad_references.py` for the Miracle and both ECAN3 layouts (compared key by key to 1e-9 before the old code was removed). The regenerated `measure_cad_output.md` has no changed line in the Miracle and ECAN3 rows. All three references pass every check with the limits of doc 06 §5.
- **No acoustic number changed** against the C4 reports in git (commit `20b09ae`), for all eight bodies: kernel diameters, chimneys and tubes equal; measured diameters within 1e-6 mm, measured chimneys within 0.003 mm; cavity mesh target and V0 target equal; voicing hashes equal (`d1b6418b1844` at 80 cm³, `6aa0038008cc`, `622bdad5acb2`, `a01cb7f7f544`, `f3803f8358b6`). Capped air within +0.007 % to +0.020 % of V0 (limit 0.5 %) and within 0.004 % of the C4 value. The finger and thumb holes of P1 and of every P0 body did not move at all.
- **Cavity mode.** P1-80 1.630 × F6 and P2-80 1.402 × F6 (`addon_checks/cavity_modes_fd.md`: 1.63 and 1.40).
- `python -m unittest discover -s kernel`: 120 tests pass.
- I looked at `top.png` of P1-80, P2-80, P3-80, P3-80-ov6 and P0-80, and at `sheet_views.png` of P0-80. They agree with the numbers. On P3-80 the two hands overlap: R_index sits under L_middle, and sub2 sits close to the large L_index hole (the 3.41 mm gap).

- **Independent review.** A fresh-context reviewer (Sonnet 5.5) checked the eight reports, the JSON files and the top views against this list. It recomputed the subhole distances from the hole centres (9.500 and 7.500 mm, 0.0° off the normal on P1, P2 and P3), diffed all eight bodies against commit `20b09ae` (no acoustic number changed), and found all seven items to pass. Its remarks: the 3.41 mm gap on P3-80 passes by 0.01 mm; `measure_cad_output.md` gave plan-view pitches without saying so (a sentence was added to that file); the `voicing.png` close view has a jagged outline because it shows only the triangles near the window (unchanged since C4).

## Decisions made in C4b

- **Subhole rule** (`holes_layout._slide_point`). The eight finger holes are placed first. The hand line is the line from the pinky hole to the index hole of the parent's hand, in the plan view, between the hole centres on the cavity surface. The subhole lies on the normal of that line through the parent, on the fingertip side (left hand: toward the player; right hand: away). Its distance is the straight 3-D distance between the two centres. The point is found on the deck by Newton steps (`_surface_over`). Presets carry `sub1_parent`, `sub1_slide_mm`, `sub2_parent`, `sub2_slide_mm`.
- **Subholes have no sideways limit.** The 35 % limit of the finger holes does not apply to them. Their own limit is that the deck must not lean more than 60° where they sit; a breach is a layout message and never shortens the slide. A slide that leaves the deck is an error with a clear text.
- **Edge-gap relaxation.** For a pair with one subhole: when a longer slide moves the subhole away from the other hole, the slide grows (up to 11 mm = the upper limit of `ergo_subholes`, read from `[ergonomics] subhole_distance_mm`). Otherwise the other hole moves along its row (up to 2 mm), unless it is the parent. A slide never turns around. Finger and thumb holes behave as in C4.
- **Hand overlap** (`hand_overlap_mm` in the preset). Each hand moves by that distance along its own pinky → index line of the template toward the other hand; its thumb hole moves with it. Distances inside a hand do not change. The old compression is gone: a hole that does not fit raises an error that names the two preset values to change. P1 and P2 have 0, P3 has 12 (open problem 16).
- **Eleven soft checks** (`ergonomics.evaluate`): `ergo_finger_pitch`, `ergo_hand_span`, `ergo_arch`, `ergo_hands_parallel`, `ergo_hand_offset`, `ergo_index_meet`, `ergo_subholes`, `ergo_rest_space`, `ergo_hole_lean_end`, `ergo_hole_lean_side`, `ergo_thumbs`. Limits in `[ergonomics]` of `params/alto_c_12hole.toml`. The tilt of each hand line against the body is in the message of `ergo_hand_offset`, without a limit.
- **Rest space is measured on the mesh, along the hand axis**: the body is cut by the vertical plane through the pinky hole centre along the hand axis, and the land is the distance to the end of that cut minus the hole radius. This is the method used for the ECAN3 rows. It gives less than the "along the body" numbers of doc 06 (P1 5.2 / 4.8 mm against 6.4 / 5.2; P2 9.4 / 12.4 against 10.7 / 14.7), because the pinky holes are off the middle line, where the body ends sooner.
- **Status `warn`.** `checks_geo.unexpected_failures` and `--strict` look only at `fail`. `report.check_blocks` gives the three blocks (unexpected, expected, warnings).
- **Cavity mode hand-off.** `body.build_body` writes the STL files before the checks. `checks_geo.measure_cavity_mode` passes the exported `<id>_air_capped.stl` to `cavity_mode.run`, which starts `cavity_mode_solver.py` in a Python that has numpy and scipy: the environment variable `OCARINA_PYTHON`, then the project `.venv`, then `python`, `python3`, `py` on PATH. The solver writes `<id>_cavity_mode.json` beside the STL. The result is the 1.5 mm grid; the 2.0 mm grid is shown beside it. trimesh is used when present; without it the solver reads the binary STL itself. When no solver can run, `cavity_mode_computed` is `fail` with a message that starts "NOT COMPUTED": it shows as an unexpected failure, so it cannot pass by default. A body that is not exported gets a temporary export for the solver.
- **Check names.** `cavity_mode_c2L` (the kernel's result, status `info`) and `cavity_mode_computed` (the verdict; limits `cavity_mode_margin` 1.0 and `cavity_mode_fem_margin` 1.3 of the parameter file).
- **Renders.** Names are text objects that float between the body and the camera (built-in font); `render.place_labels` picks the free side of each hole. The caption is a text object rendered once and pasted under each picture.
- **`tools/cavity_modes_fd.py` and `measure_cad_references.py` import the add-on's code** (`cavity_mode_solver.py`, `ergonomics.py`), so each method exists once.
- **Docs.** The decisions are recorded in doc 02 (A12, Q8, Q9, Q12), doc 04 (D5, the P3 sentence), doc 03 (R9, R16) and the banner of doc 05. Nothing else in `docs/` changed. Doc 03 §8 still has its "Under review" paragraph about the 124 mm stop, and doc 04's shape table still says P2 is "at the cavity-mode limit (c/2L ≈ F6)"; both are outside the edits the owner approved. Doc 02's Phase 4 list (step 9) and doc 04 D9 still name the doc 05 checks (`hand tilt`, `hole tilt`).

## C5 evidence

The three commands (from the repository root; Blender 5.1.2). Each builds every body of its stage, even when one fails:

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python ocarina_addon/headless.py -- stage1
```

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python ocarina_addon/headless.py -- stage2
```

```bash
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python ocarina_addon/headless.py -- stage3 --calibration calibration/synthetic-fitted-constants.toml
```

| Stage | Bodies | Result | Exit code | Time | Report | Files (not in git) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | V-a, V-b, V-c, V-d, V-a-plus, V-a-minus | 6 of 6 with no unexpected failure, no expected failure, no warning | 0 | about 3 min | `addon_checks/stage1.md` | `addon_out/stage1/<id>/` |
| 2 | P0-65, P0-80, P0-95, P0-125, P1-80, P2-80, P3-80, P0-80-b, P0-80-c | 9 of 9 with no unexpected failure; expected: the pad-limit checks; warnings: the `ergo_*` checks of "C4b evidence" | 0 | about 7.5 min | `addon_checks/stage2.md` | `addon_out/stage2/<id>/` |
| 3 (SYNTHETIC constants) | the seven printed bodies as `<id>-r2`, and P0-110-r2 | 5 of 8 with no unexpected failure; `hole_spacing` fails on P1-80-r2 (2.80 mm), P2-80-r2 (2.56 mm) and P3-80-r2 (2.70 mm): open problem 19 | 1 | about 5.5 min | `addon_checks/stage3-synthetic-fitted-constants.md` | `addon_out/stage3-synthetic-fitted-constants/<id>/` |

Per body a stage writes `<id>.stl`, `<id>_air_capped.stl`, `<id>_air_fem.stl`, `<id>_cavity_mode.json`, `<id>_checks.json`, a blank `<id>_measurement.toml`, and a check report. Stage 1 and Stage 2 write the check reports to `addon_checks/<id>.md` and the pictures to `addon_renders/<id>/`; Stage 3 writes them beside the STL files, because its result depends on the constants file.

Acceptance list of C5, with the output:

- **Stage 2 list.** Exactly the nine bodies of the task; no P4. `P0-80-b` and `P0-80-c` have the same triangles as `P0-80` (the files differ only in the 80-byte header that carries the id). Every body has the acoustic numbers of C4b (the stage uses the same build).
- **Stage 1 stubs.** Built by the recipes: V-a = `make_voicing(80)`, V-b = `make_voicing(80, shape="rounded_rectangle")`, V-c = `make_voicing(125)`, V-d = `make_voicing(65)`, V-a-plus and V-a-minus = `make_voicing(80, labium_offset_mm=±0.2)`. A stub is the egg preset `S0` at 25 cm³ of capped air with the voicing, the 4 mm wall and no holes (genus 1). Its own check `stub_volume` passes on all six: 25.000 to 25.005 cm³ (at most +0.021 %, limit 0.5 %). V-a has the hash of the 80 cm³ bodies (`d1b6418b1844`), V-c that of P0-125 (`f3803f8358b6`), V-d that of P0-65 (`6aa0038008cc`). Predicted pitches with the prior η_w (predictions, not measurements): 787 Hz (V-a, V-b, V-a±), 984 Hz (V-c), 709 Hz (V-d).
- **V-b through a full build.** The forced rounded rectangle (9.65 × 6.60 mm, 62.8 mm², corner radius 1.0 mm) builds and passes every check. The first run failed `voicing_orientation`, because that check asked for a broad end at the windway, which a rectangle does not have; the check now applies that part to teardrops only and says so.
- **Sizes agree with doc 04.** The table "Sizes against doc 04" of `stage2.md` equals the table "Generated sizes at each step" of doc 04 for 65, 80, 95 and 125 cm³ in every cell, except the known rounding of the 65 cm³ window area (46 against 47 mm²; the value is 46.47). `tests/test_stage_reports.py` compares the two tables cell by cell, and the print diameters, tubes and chimneys of the per-body tables with the kernel.
- **Stage 3.** Runs from `calibration/synthetic-fitted-constants.toml` and marks its report SYNTHETIC. The round-1 tubes are kept on all 84 holes of the seven printed bodies (none changed); the windows and the volumes are kept (A4 error −38 to −41 cents with the synthetic η_w 0.86: the owner's open question about keeping V0); the holes stay at their round-1 positions; P0-110 is sized from the fitted model only (new hash `39c00d2765a6`, η_w fallback). Capped air +0.015 to +0.030 % of the model target (V0 / volume factor 0.9853).
- **Report blocks and exit code.** Each stage report has "Unexpected failures", "Expected failures" and "Warnings" as separate blocks. A build error of one body is recorded and the other bodies are still built (tested with a forced failure in `tests/blender/test_geometry.py`). Only an unexpected failure gives exit code 1.
- **Names.** The reports use `sub1` and `sub2` and say so in the header (sub1 = sub_L, sub2 = sub_R).
- **Cavity-mode step.** Runs inside each stage command for every body (stubs 3.10 to 3.13 × F6; Stage 2 as in "C4b evidence").
- `python -m unittest discover -s kernel`: 123 tests pass (120 before; 3 new for the stub file).
- I looked at `sheet_views.png` of V-a, `voicing.png` of V-b and `sheet_views.png` and `sheet_sections.png` of V-c. They agree with the numbers: no finger holes; V-a has the teardrop with its broad end at the windway; V-b has a rounded rectangle; V-c has the 18.6 mm wide window with its 4 mm throat on a flat inner plane.
- **Independent review.** A fresh-context reviewer (Sonnet 5.5) checked the three stage reports against doc 04, the per-body reports, the generated folders and the pictures. Stage 1 and Stage 2 passed every item (it compared all nine hole tables with the per-body reports by script: no difference; the totals add up). For Stage 3 it confirmed the 84 kept tubes and found wording faults, which are fixed: the report now explains the `hole_spacing` failures in plain words, no longer claims pre-calibration constants, gives the right target for the capped air, shows "–" as the round-1 diameter of the never-printed P0-110, and shows the kernel's c/(2L) beside the computed cavity mode.

## Decisions made in C5

- **Where a stage writes.** Defaults of `headless.py`: STL files and templates under `addon_out/<stage>/` (not in git); the stage report and, for Stage 1 and 2, the per-body reports under `addon_checks/`; pictures under `addon_renders/<id>/`. All can be changed (`--out`, `--reports`, `--renders-dir`, `--no-renders`, `--only`). The blank measurement templates are not committed: fill in a copy.
- **`body.build_body` takes `sizing_fn` and `layout_rows`.** `sizing_fn(L_int_mm)` replaces the kernel's `size_body` call (Stage 3: `calibration.size_body_from_calibration`; stubs: `stub.stub_sizing`). `layout_rows` are the rows that decide the hole positions; Stage 3 passes the round-1 rows, and `holes_layout.with_rows` then puts the corrected diameters on the same positions and computes the gaps again.
- **Cut diameters are the CAD diameters** (`body.cut_rows`: the kernel's `cad_diameters_mm`, design minus hole offset). In round 1 the offset is 0 and they equal the design diameters.
- **The volume target of a model** (`body.capped_target_cm3`) is the cavity mesh target minus the tube walls plus the air of the holes as drawn. In round 1 this is V0 exactly. With fitted constants it is V0 / volume factor. Before C5 the check compared with V0 × volume factor, which is wrong for a factor other than 1; no body had been built with one.
- **`hole_limits[fitted]` is an expected failure** (Stage 3). It is the round-hole verdict of doc 04; the stage report states it in a block of its own.
- **Stubs.** Preset `S0` (P0 proportions, port at the middle, `layout = "none"`, `stub_volume_cm3 = 25`). `stub.StubSizing` carries what the build and the checks read from a sizing record. A stub has the checks of a body without the hole checks, plus `stub_volume` and `stub_pitch_predicted` (status `info`). The cavity-mode step compares the stub's first mode with F6, the top note of the instrument the voicing is for.
- **Stage 3 keeps the printed V0** (`retarget_volume=False`; option `--retarget-volume`). This is one of the questions still open with the owner; the report gives the A4 error that follows.
- **Stage 3 ids end in `-r2`.** Its per-body reports and templates stay beside the STL files.
- **The stage report** joins the kernel's sizing (every hole at k 0.8 and k 1.0, plain-wall diameter, tube, chimney, pad limit) with the numbers measured on the STL. It also gives the plastic volume and the solid PLA mass against the doc 04 budget.

## C6 evidence and final pass

One command runs all four suites (about 5 minutes on this machine):

```bash
python tools/run_tests.py
```

| Suite | Command | Result |
| --- | --- | --- |
| Kernel | `python -m unittest discover -s kernel` | 123 tests, all pass |
| Plain Python | `python -m unittest discover -s tests` | 99 tests, all pass |
| Headless Blender | `blender -b --factory-startup --python tests/run_blender_tests.py` | 30 tests, all pass (one more entry is the empty base class, skipped) |
| Extension install | `python -m unittest discover -s tests/extension` | 4 tests, all pass |

What the suites cover:

- `tests/test_cavity_math.py`, `test_holes_layout.py`, `test_presets_and_bridge.py`, `test_ergonomics.py`, `test_cavity_mode.py`, `test_report.py`, `test_stage_reports.py`: no Blender. The ergonomics test reproduces the Miracle and both ECAN3 rows of `measure_cad_output.md` (sections 1, 2, 3 and 5) from the reference hole data, and checks that all three references pass every `ergo_*` check. The layout test states the subhole rule (9.5 and 7.5 mm, 0° off the normal, toward the fingertips), the overlap rule (every distance inside a hand is unchanged), the P3 error without overlap, the lengthening of a slide up to 11 mm, and the 3.05 mm gap of open problem 19. The stage-report test compares the committed `stage2.md` with doc 04 cell by cell.
- `tests/blender/test_geometry.py`: the 20 cavities; P1-80 and P0-65 as bodies, built into a temporary folder and measured on the STL read back from disk (Phase 4 gate, volumes, voicing, the eleven soft checks, the cavity mode, equal acoustic numbers and hole positions against the committed reports, pictures); stub V-b; the stage runner with one stub made to fail (the other is still built, the stage exits with 1); one Stage 3 body (tubes, window, volume and positions kept).
- `tests/extension/test_install.py`: packs the zip, installs it with `blender --command extension install-file -r user_default --enable` into a temporary profile (`BLENDER_USER_RESOURCES`), builds P0-65 with the INSTALLED copy (module, kernel and parameter file all inside the temporary profile; nothing of the repository on `sys.path`), and compares a full listing of the owner's real Blender 5.1 profile before and after: no file changed.

**The pack script found a real fault.** `python tools/pack_extension.py --validate` runs Blender's own check of the zip. The manifest's `[permissions] files` text was 69 characters; Blender allows 64 and refuses the package. The text is now 58 characters. Installing the extension had never been tried before C6.

### Final pass: every acceptance criterion with the output

C4b:

| Criterion | Output |
| --- | --- |
| sub_L 9–10.5 mm from L ring, sub_R 7–8.5 mm from R middle, within 20° of the hand line's normal | 9.50 mm and 7.50 mm, 0° off the normal, on P1-80, P2-80 and P3-80 (recomputed by the reviewer from the hole centres) |
| Smallest edge gap at least 3.4 mm | 3.63 mm (P1, P2), 3.41 mm (P3), 4.01 mm or more (P0) |
| Every tube clearance check passes | `inward_tubes` pass on every body that has a tube |
| `ergo_*` report ok or warn, never fail | 11 checks per body, statuses `pass` or `warn` only; P0: all `warn` with "taped test body, not a hand layout" |
| `ergonomics.py` reproduces the reference rows | identical to the old code to 1e-9; `tests/test_ergonomics.py` checks the rows of `measure_cad_output.md` |
| No acoustic number changed from C4 | all eight bodies: diameters, chimneys, tubes, volume targets and hashes equal; capped air +0.007 to +0.020 % of V0 |
| Cavity mode from the computed first mode, within 2 % of the table | P1-80 1.630 × F6 (table 1.63), P2-80 1.402 × F6 (table 1.40); pass on all eight bodies |
| No unexpected failure on the eight bodies | none |
| Kernel suite | 120 tests passed at C4b; 123 now (3 new tests for the stub file) |

C5:

| Criterion | Output |
| --- | --- |
| `stage1` generates end to end | six stubs, 6 of 6 with no unexpected failure, exit code 0; STL files, blank stub templates, `addon_checks/stage1.md` |
| `stage2` generates end to end | nine bodies, 9 of 9 with no unexpected failure, exit code 0; STL files, blank templates, `addon_checks/stage2.md` |
| Report sizes agree with doc 04 | every cell of the ladder table for 65, 80, 95, 125 cm³ (one known rounding: 46 against 47 mm²); stub windows 62.8, 62.8, 123.5 and 46.5 mm² |
| `stage3` runs from the synthetic constants with the round-1 tubes kept | eight bodies generated, 84 of 84 tubes kept, report marked SYNTHETIC. **Exit code 1:** `hole_spacing` fails on P1-80-r2, P2-80-r2 and P3-80-r2 (open problem 19: a conflict between two rules, not a build fault) |
| A stub has its own volume check | `stub_volume` passes on all six (at most +0.021 %) |
| V-b through a full build | builds and passes every check |
| Stub measurement template in the kernel, with tests | `measurements.stub_template`, `write_stub_file`, `load_stub`; 3 tests |
| Reports name the subholes one way | `sub1` / `sub2`, stated in every header |
| A stage builds every body even when one fails; three blocks; exit code only for unexpected failures | tested with a forced failure (`tests/blender/test_geometry.py`); Stage 2 exits with 0 although it has 17 expected failures and 81 warnings |
| The stage command includes the cavity-mode step | yes, for every body and stub |

C6:

| Criterion | Output |
| --- | --- |
| Headless Blender test suite runs green | 30 tests, all pass (one more entry is the empty base class, skipped) |
| Plain-Python tests run green | 99 tests pass (kernel: 123) |
| Pack script produces a zip that installs and builds a body in a clean Blender profile | `dist/parametric_ocarina-0.1.0.zip` (35 files); Blender validates it; installed into a temporary profile, P0-65 built with no unexpected failure and cavity mode 2.24 × F6; the owner's profile unchanged |
| README says how to install, run the stages and run the tests | section "Add-on (Blender 5.1)" of `README.md` |
| Final pass | this section |

Not met, blocked or expected to fail:

- **Stage 3 with the synthetic constants ends with exit code 1** (three `hole_spacing` failures, open problem 19). It needs an owner decision, not a code fix.
- **Expected failures** on every Stage 2 body but P0-65's print set: the pad-limit checks `hole_limits[print]` and `hole_limits[nominal]` (L_index and L_thumb are larger than a finger pad by the plan).
- **Warnings** on P1-80 (4), P2-80 (5) and P3-80 (6): see "C4b evidence".
- The criterion "position factors within 1 % with ±5-cent noise" of the first prompt still cannot pass as written (2.5 to 3.6 % at the 95th percentile). The owner has to reword it.
- Nothing was printed. Every constant is pre-calibration.

## Merge with main and C5 rerun (2026-11-17)

`origin/main` (27 commits: ladder change, 3 mm window wall option, labium default −0.2 mm, break pressure, η_w band, Heuer source review, ECAN3 merge) was merged into the local `addon-v1` (C4b, C5, C6 and the uncommitted work of 2026-11-16/17). Merge commit `583adde`. **Everything below the merge commit is uncommitted.**

What was changed to bring C5 to the rules of `main`:

- `stub.RECIPES`: V-a, V-b, V-d and the optional V-a0 (offset 0), V-a35 (offset −0.35 mm) and V-a3 (3 mm window wall). V-c, V-a-plus and V-a-minus are gone (the offset is never positive). A recipe has a sixth field, the wall at the window.
- `stages.py`: Stage 2 is P0 at 65, 80, 95, then P1, P2, P4 at 80 and the two copies (8 bodies). Stage 3 is the six printed bodies and P0-88 (`PREDICTION_V0_CM3`). Budgets 150 / 707 / 627 g (doc 04, with P4 in P3's place).
- `body.build_body`, `api`, `tools/geometry_check_body.py`: the argument `wall_at_window_mm` of `main` is threaded through the C5 structure (`sizing_fn`).
- `kernel/measurements.py`: the stub file has the optional `p_break_pa` under `[pitch]` (doc 04 asks for the break pressure on every stub).
- `meshutil.cleanup` ends with `repair_collinear_rows`. With the labium at −0.2 mm the windway floor lies 0.2 mm below the pocket ceiling, and the Booleans leave a row of needle triangles (heights near 1e-7 mm) on the line where the window side wall meets that ceiling. They are clean in double precision and one of them becomes a zero-area triangle in the STL file (V-b and V-d failed `topology` with "degenerate triangles 1"). The repair deletes the needles of a row and splits the proper triangles beside it; no vertex moves. A mesh without such a row is returned unchanged.
- `checks_geo.measure_voicing`: `window_tip_y_mm` is the middle of the far end of the window. On the rounded rectangle (V-b) the far end is a straight edge, and the old "point with the largest x" could be any point of it (−1.27 mm at the new offset), which failed `voicing_orientation` for no geometric reason.
- `report.py`: the labium offset is printed with two decimals when it needs them (−0.35).
- Tests: the stage lists, the stub set, the voicing hashes (65 cm³ `2a71c31c2505`, 80 cm³ `617b869f0b10`; the old 80 cm³ hash `d1b6418b1844` is now the hash of coupon V-a0), 30 cavities (P0–P4 at 65, 80, 88, 95, 110, 125).

Results (all on the STL files read back from disk):

| Run | Result |
| --- | --- |
| `headless.py -- stage1` | 5 of 6: V-a, V-b, V-d, V-a0, V-a35 have no failure. **V-a3 fails `voicing_keepouts`** (243 vertices above the outer face; open problem 22) |
| `headless.py -- stage2` | 8 of 8 with no unexpected failure. Warnings: P0 bodies 11 each (taped layout), P1-80 4, P2-80 5, P4-80 2 |
| `headless.py -- stage3 --calibration calibration/synthetic-fitted-constants.toml` | 4 of 7: the P0 bodies and P0-88-r2 are clean. P1-80-r2, P2-80-r2 and P4-80-r2 fail `hole_spacing` (sub1 to L_ring 2.81 / 2.54 / 2.17 mm against 3.4 mm). This is open problem 19, unchanged by the merge |
| `python tools/run_tests.py` | kernel 128, plain 99, Blender 36 (1 skipped), extension 4: all pass |

Not done, and stale: the reports `addon_checks/V-c.md`, `V-a-plus.md`, `V-a-minus.md`, `P0-125.*`, `P0-110.*` and `P3-80*.md` are from the old stage lists; `tools/geometry_check.py -- bodies` (which includes P0-95 with the 3 mm wall) and `-- cavities` were not rerun as report writers (the Blender test suite ran the 30 cavities). The synthetic round-1 files of `main` and the calibration file were used as merged.

## Re-evaluation against the source review (2026-11-17)

The work that `main` did not have (ergonomics docs 05 and 06, the cavity-mode tool, C4b, and the uncommitted ellipse window cut, windway tilt and neck) was read against docs/01 §5–6 (Heuer Videos #1–#8, Pure Ocarinas, the consolidated verdicts). All of it is on `addon-v1` since the merge; none of it is on `main` yet.

| Item | Against the source review | Verdict |
| --- | --- | --- |
| Ergonomics review (docs 05, 06; A11–A14) | Heuer #7: holes go "where it's comfortable", marked with the hand in place. Doc 01 §6 row 6: positions are free. | **Agrees.** No change. The layout freeze (A14) is this branch's own caution and is not contradicted |
| C4b hand layout | Heuer #4, #8: no hole near the voicing. Rebuilt 2026-11-17: nearest hole edge to the window 22.6 mm (P1-80), 18.7 mm (P2-80), 18.1 mm (P4-80), 29.7 mm (P0-65), against 10 mm | **Agrees.** |
| C4b soft checks and the expected pad-limit failures | Doc 01 §6 challenge B (inner bevel under a hole, Heuer #4) is the maker's answer to holes larger than a finger pad. It is on hold | **Open, unchanged.** The `hole_limits` failures on P1, P2 and P4 stay "expected" until B is decided |
| Subholes and Stage 3 edge gaps (open problem 19) | Pure Ocarinas: a finger near an open hole flattens it ("shading") | **Supports keeping the 3.4 mm gap rule** and deciding problem 19 before the layout freeze |
| Cavity-mode tool (`tools/cavity_modes_fd.py`, check `cavity_mode_computed`) | Self-test: box 0.0 %, sphere −1.0 %. Table regenerated for the present bodies: P0-65 2.24, P0-80 2.10, P0-95 1.98, P1-80 1.63, P2-80 1.40, P4-80 1.36 × F6. The labium offset does not move these | **Sound as a desk check, with one caution** (open problem 25) |
| Body shapes | Heuer #8: "you don't want it too long and skinny … generally kind of a roundish type shape". ECAN3 X7: chambers at 1.08–1.18 × F6 are sold as playing to F6 | **Tension, already a test item.** P0 is the roundish body. P2 and the P4 seed (133 mm at 80 cm³, the longest) are long and slim in Heuer's terms; the seed follows two ceramic 12-holes. The Stage 2 spectra decide |
| Ellipse window cut (`window_cut=ellipse`, P1 and P3 settings) | Heuer #8 model: the window "sits in a recessed dish that opens around it". #8: airway width equals window width; exit "no overhangs … not too flared out" | **Agrees in form.** Rebuilt at the −0.2 mm labium offset on P4-80, P0-65 and P0-95: no unexpected failure; window area, exit size, labium angle, edge and offset as recorded; the windway is not touched by the cut. Two cautions: open problems 24 and 26 |
| Windway tilt (`windway_pitch_deg`, lowered only) | Heuer #3, #8: the drop under the exit is "straight up and down or tilted in"; "you wouldn't want it tilted up". The lip must be seen through the airway, below the middle | **Agrees for a lowered windway, and Heuer gives the reason for the owner's rule.** The pivot is the lip edge, so the lip stays at −0.2 mm from the jet centre. Seen from the jet, a lowered windway leaves the drop tilted back by the pitch angle; a raised one would tilt it up. One caution: open problem 26 |
| Neck (`stub_style=neck`) | Outside plastic only. Outside keep-out: 0 vertices above the 45° flare on every rebuilt body. Pure Ocarinas: print standing on the mouthpiece so the windway walls are perimeters | **No clash.** Two print notes: 1.2 mm is the least wall around the pipe (three 0.4 mm perimeters), and the slim mouth end is the print base, so it needs a brim. The "voicing neck" of Pure Ocarinas is a deep window throat, not this mouthpiece neck |

Rebuilt for this table with `tools/geometry_check_variant.py` (reports in `addon_checks/`, ids ending in `-lab02`): `P4-80-el-p1-m25-lab02`, `P4-80-el-p3-m25-lab02`, `P0-65-el-p3-lab02`, `P0-95-el-p1-lab02`, and `P0-95-el-p1-m4-lab02`, which fails. The owner's earlier experiment reports (`*-el-*`, `P4-80-neck*`, `P4-80-dish-*`, `P4-80-cone*`) were built at labium offset 0 and are kept as they were.

## Fingering order switched (2026-11-18)

Owner decision, after doc 09: "Switch it as long as it's compatible with the split sub hole decision, one on each hand." It is compatible: the source gives the subhole order the kernel already had (the left subhole opens B4, the right one C5), both subhole fingers stay on their main holes from A4 to C5, and L ring, which carries the left subhole, is the first left finger to lift (A5), after both subholes are open.

What changed:

- `params/alto_c_12hole.toml`, `[fingering]`: after R index the holes open L ring (A5), L middle (B5), L index (C6), L thumb (D6), R thumb (E6), L pinky (F6). Before: L pinky, L ring, L middle, L index, L thumb, R thumb. The steps, conductances and diameters are the same numbers; the finger that owns each one changed.
- `kernel/sizing.py`, `ocarina_addon/report.py`: the doc 04 table shows the two largest holes by the note they open (D6, E6). Its numbers did not change; its columns are now "D6 thumb (L)" and "E6 thumb (R)".
- `kernel/alto_c_study.py`: the chimney table names its columns from the fingering table. `docs/generated/study-output.md`, the synthetic round-1 files, the example file, the blank template and `calibration/synthetic-fitted-constants.toml` were regenerated.
- `ocarina_addon/holes_layout.py`, `P0_RELATIVE`: the taped P0 layout kept its places and the names moved, so that each top-deck place holds a hole of the diameter it had before or a smaller one (L ring has the end place, L middle and L index the next two, L pinky the place of the old D6 hole). A first attempt that only moved the left subhole built the ladder but not P0-125, where the F6 hole at the bulb end failed its Boolean check. No hand layout (P1, P2, P4) was touched.
- Tests: `test_fingering_order_is_the_asian_system` and `test_the_two_largest_holes_are_under_the_thumbs` are new (the first carries the source). Updated: the doc 04 table test, the pad-limit test (at 65 cm³ only R thumb is over its limit), the report needle of the convention estimate, and three layout tests that had assumed the larger L ring hole.
- Docs: 02 (Q3 answered), 03 (the baseline table and two more), 04 (the table header and the hole paragraph), the Miracle report (a dated correction), 09 (status blocks).

Results, all on the STL files read back from disk:

| Run | Result |
| --- | --- |
| `headless.py -- stage2` | 8 of 8 with no unexpected failure. Warnings as before: P0 bodies 11 each, P1-80 4, P2-80 5, P4-80 2. At the print diameters the only hole over a pad limit at 80 cm³ is R thumb (12.71 mm against 12). Smallest edge gap: P0 4.01 / 4.28 / 4.52 mm at 65 / 80 / 95 cm³; P1, P2, P4 4.25 mm (sub2 to R middle). Nearest hole edge to the window: L thumb, 19.0–23.6 mm on the hand bodies |
| `headless.py -- stage3 --calibration calibration/synthetic-fitted-constants.toml` | 5 of 7 (was 4 of 7). The P0 bodies, P0-88-r2 and **P1-80-r2 are clean**. P2-80-r2 and P4-80-r2 still fail `hole_spacing` on the left subhole and L ring: 3.34 and 3.02 mm against 3.4 (they were 2.54 and 2.17) |
| `python tools/run_tests.py`, run as its four parts | kernel 130, plain 99, Blender 36 (1 skipped), extension 4: all pass |

**Open problem 19 is smaller, not closed.** At the k_hole 1.0 diameters the 9.5 mm slide now leaves 3.78 mm (it left 3.05). With the synthetic constants (k_hole 1.17, invented) P2 and P4 are still under 3.4 mm. A left slide of 10.0 mm would clear both (3.84 and 3.52 mm), and the two professional alto C instruments have 10.3–10.6 mm there (doc 09 section 4). The 9.5 mm is the owner's number of 2026-11-15, so it was not changed.

Stale after this change: the per-body reports and pictures of bodies that are in no stage list (`P3-80*`, `P0-110`, `P0-125`, the `*-el-*`, `-neck*`, `-dish-*`, `-cone*` experiment bodies) were built in the old order. `tools/geometry_check.py -- bodies` was not rerun as a report writer.

## Owner decisions applied (2026-11-18): slide, cut, mouth end, hash, stubs, standing neck

The owner was shown one picture sheet and the measured effect per option for six open decisions ([decisions.md](../Analizes_ocarinas/Decisions_2026-11-18/decisions.md)). The answer: "I agree with the decisions, just the 6. Swap it to standing 15 degree." So recommendations 1 to 5 were taken, and for decision 6 the owner chose the neck that stands off the body, against my recommendation.

| # | Decision | Where it lives now |
| --- | --- | --- |
| 1 | Left subhole slide 10 mm (was 9.5) | `sub1_slide_mm = 10.0` in P1 to P4 of `cavity_presets.toml`; `holes_layout.SUBHOLE_DEFAULTS` |
| 2 | Window cut: ellipse "P3" | `[voicing_rules]` `window_cut = "ellipse"`, `cut_widen_mm = 3.0`, `shelf_angle_deg = 40.0` |
| 3 | Tilt 2.5°, agreed for a neck along the body | **Not as worded: see "The one open point".** `windway_pitch_deg = 5.0` |
| 4 | Windway 3.0 mm high at the mouth end (was 1.56) | `windway_taper_ratio = 2.5` |
| 5 | The build in the hash; one stub with the build, one with the plain build | kernel `BUILD_FIELDS`; stubs V-a and V-af |
| 6 | The neck stands 15° off the body | `stub_style = "neck"`, `stub_pitch_deg = 15.0`; with it `pocket_blend_radius_mm = 12.0`, the blend every option body had |

`[voicing_rules]` is rule version 2. Every hash changed: 65 / 80 / 88 / 95 cm³ are `16410d2e6a1b` / `b4620fbf3d67` / `ecfc6c2a0620` / `7e2fd3e0bf07` (plain build at the same rules: `e090f35105ee` / `36b60ed8c18d` / `60ace4fc1eaf` / `bc4c1aae5286`).

### The one open point: the angle of the pipe

Decisions 3 and 6 cannot both hold as worded. The 2.5° was agreed for a neck that lies along the body, where the pipe is lowered 2.5° inside it. With a neck that stands 15°, a pipe at −2.5° against the body lies 17.5° lower than the neck. The test body `P4-80-st15-m25` showed what that means: the windway never reached the mouth end (genus 12 against 13), and once the cutter was made to reach it (see below) the mouth end of the neck has to be 21.3 mm deep to keep 1.2 mm around the pipe, against 15.0 mm at the rule. What was built is the body the owner chose from the picture (`P4-80-el-d-p3-stand`): **the pipe 10° lower than the neck, +5° against the body**. It is "lowered" in the owner's sense of 2026-11-18 (tilted toward the body, hidden by the neck, the pivot at the lip). The jet now reaches the lip heading 5° into the chamber, so the caution of doc 09 section 3.1 about a jet that leaves the labium's inner face no longer applies. The owner was asked to confirm the angle. It is one number in `[voicing_rules]`; a change means the stages are regenerated (about 15 minutes) and four pinned hashes move.

### What changed in the code

- **Kernel, `voicing.py`.** The record has seven build fields (`BUILD_FIELDS`: `window_cut`, `cut_widen_mm`, `shelf_angle_deg`, `windway_pitch_deg`, `pocket_blend_radius_mm`, `stub_style`, `stub_pitch_deg`). `PLAIN_BUILD` is what every body had until now. The hash takes the build as a whole and only when it differs from the plain build, so a plain voicing keeps its hash: with the rules of version 1 (taper 1.3, no build fields) `make_voicing` still gives `617b869f0b10` at 80 cm³ and the pre-C2b hashes at offset 0 (`test_old_teardrops_are_unchanged`). New: `make_voicing(..., build=None | "plain" | dict)`, `resolve_build`, `check_build` (refuses a shelf on the fan cut, an unknown cut or stub style, a neck whose pipe is raised above its roof line), `with_build(v, **fields)`.
- **Add-on, `voicing_geo.py`.** `build()` takes the cut, the pitches, the stub style and the blend from the record. A variant build still overrides them through preset keys (`RECORD_KEYS`; `cone_widen_mm` is the record's `cut_widen_mm`), and `body.build_body` now puts the override **into the record** before anything is built, so the hash of a variant is the hash of what was built. Six prototype keys stay outside the record (`UNHASHED_KEYS`: `block_front_mm`, `shelf_land_mm`, the three `neck_*` sizes, `cone_flare_exponent`); a report of a body that uses one says so in its header. An override replaces the field it names and nothing else: `windway_pitch_deg=-2.5` alone no longer lays the neck along the body.
- **The windway cutter** starts further outside the mouth end when the pipe is turned far inside the stub, so that its whole start face clears the end plane of the stub. Up to 10° between pipe and stub this is the 1.0 mm it always was; the rule bodies are unchanged by it.
- **The ellipse cut is refused on a window that is not a teardrop** (a clear `ValueError`). Stub V-b, the forced rounded rectangle, failed its window Boolean with it (−3442 mm³ against −520).
- **Outside keep-out, `checks_geo.measure_keepout_outside`.** The record's rule is a 45° flare. The check counted every vertex above the outer face, which was the same thing while the stub ended there. A standing neck rises behind the window, so the check now measures the flare: a point h above the outer face is inside when its distance from the window outline, in the outer face, is less than h · tan 45°. It tests vertices, edge midpoints and face centres. The limit is unchanged. The neck is 41.5° steep seen from the rim on every 4 mm body (the point where the shelf meets the roof of the neck, 4.4 mm behind the exit and 3.9 mm up), so the margin is about 3.5°.
- **The pocket blend ends where it meets the chamber wall** (`voicing_geo.build(..., cavity_height=)`, `body.cavity_height_fn`). The blend was prototyped on P4-80 with a fixed reach of 12.5 mm and a parabola. The first regeneration with the blend on every body showed what that does on a curved chamber: the skirt never met the wall, cut a step of about 2 mm into it at its rim, thinned the wall, and on P2-80 left **0.06 mm of plastic** between the pocket and the chamber (stubs: 1.4 to 3.5 mm). Every check passed, because `wall_thickness` judged the plain wall only. Now the skirt is a circle of the rule's radius, its reach is found per direction on the cavity mesh, and it ends 0.2 mm under the chamber wall; beside the windway exit of a small chamber, where the chamber's own wall turns upright first, it ends 0.3 mm before that wall. Reach on the stage bodies: 2.9 to 7.6 mm around the labium half of the window on P0, P1 and P4, up to 9.0 mm on P2 and 10.3 mm on the stubs; all 125 directions meet the wall on every body. At the two back corners beside the windway exit the skirt meets the wall after 9.4 to 10.8 mm, ends at the chamber's upright side wall on the stubs, and on P2-80 is a steep wall with 1.0 mm left at its full reach (reported in the check message). Two checks follow: `pocket_blend` (new: every direction around the labium half of the window must end on the chamber wall with no ledge) and `wall_thickness`, which now also fails when the thinnest plastic of the finished body is under 0.4 mm, one extrusion line (`MIN_PLASTIC_MM`). Thinnest plastic after the fix: 2.45 to 2.65 mm on the stubs, 2.81 to 4.00 mm on the Stage 2 bodies (P2-80: 2.94 mm).
- **Stubs, `stub.py`.** New stub **V-af**: the window of V-a with the plain build. **V-b has the plain build too**, so the shape pair is V-b against V-af at one build. The stub table of the Stage 1 report has a Build column.
- **Reports.** Every body report and every stage section has a "Build" line.

### Results (STL files read back from disk)

| Run | Result |
| --- | --- |
| `headless.py -- stage1` | 6 of 7 with no unexpected failure: V-a, V-af, V-b, V-d and the two labium coupons are clean. The optional V-a3 (3 mm window wall) fails `voicing_keepouts` as before, now by 2° (150 points inside the flare; the neck is 47° steep seen from the rim). Solid PLA: V-a 39 g, V-af 30 g; 248 g for the seven |
| `headless.py -- stage2` | 8 of 8 with no unexpected failure. Warnings as before: P0 bodies 11 each, P1-80 4, P2-80 5, P4-80 2. Smallest edge gap: P0 4.01 / 4.28 / 4.52 mm at 65 / 80 / 95 cm³; P1, P2, P4 4.25 mm (the right subhole to R middle; the left subhole now has 4.76 mm). Plastic under the windway at the exit 3.25 to 4.44 mm. 522 g of solid PLA for the eight (468 g before: the neck) |
| `headless.py -- stage3 --calibration calibration/synthetic-fitted-constants.toml` | **7 of 7 with no unexpected failure, for the first time** (5 of 7 before). Smallest edge gap with the synthetic constants (k_hole 1.17, invented): 3.63 / 3.83 / 3.83 mm on the P0 ladder, 3.78 (P1), 3.64 (P2), 3.52 mm (P4), 4.04 mm (P0-88) |
| `python tools/run_tests.py`, run as its four parts | kernel 132, plain 102, Blender 43 (1 skipped), extension 4: all pass |

Measured on P4-80 (Stage 2), against the body of 2026-11-17: plastic under the windway at the exit 4.44 mm (3.21); windway 3.00 → 1.20 mm (1.56 → 1.20); plastic of the body 58.3 cm³ (52.9); window area measured 62.83 mm² (record 62.84). Stub masses as solid PLA: V-a 39 g with the neck, V-af 30 g.

### What I chose myself (the owner can overrule each)

1. **The style and the stance of the neck are in the hash** (the owner agreed to the cut, the shelf, the tilt and the blend). A neck that stands behind the window is a baffle next to it; a stub with another neck should not lend its η_w.
2. **Rule version 2.** `[voicing_rules]` says a change is a new version.
3. **V-b carries the plain build** and pairs with V-af. The alternative is an ellipse cut for the rectangle, which does not exist.
4. **The flare is measured from the window outline at the outer face.** The dish of the cut lies inside the wall, below the face, and is not part of this check (the fan cut is not either).
5. **The pocket blend and the neck are part of the rule**, because every option body of the decision sheets had them (the owner's "smooth cavity" and "neck volume").
6. **0.4 mm as the least plastic that counts as buildable** (`MIN_PLASTIC_MM`, one extrusion line, the thickness of the labium edge). It is a build-error line, not a strength limit: the owner's 1.2 mm around the pipe is kept by the neck itself.

### What the standing neck costs, for the record

- The mouth end of the neck is 13.8 × 15.0 mm at 80 cm³ (width × depth), deeper than wide: the roof line of the neck is straight at 15° while the pipe lies 10° lower, so the slot comes out at the bottom of the end face. With the neck along the body it was 13.8 × 9.1 mm. Shaping the mouth end (a roof line that curves down toward the lips) is not done.
- The neck is about 41° steep seen from the window rim, 4° inside the flare limit. A steeper neck, a shallower shelf or a thinner window wall (stub V-a3: 47°) goes over it.
- Plastic: the neck adds about 5 cm³ to a body.

### Not done, stale, or still open

- Not printed, not played. Whether this build speaks is the question stub V-a answers against V-af.
- Stub V-a3 still fails `voicing_keepouts` (now 47° against 45°). Open problem 22 stands.
- **The bell of the neck scales with the window** (4.8 window widths wide, 2.4 deep). On the stage bodies that is 33 × 17 mm (65 cm³) to 53 × 27 mm (95 cm³). At 125 cm³, which is no stage body, it is 89 mm wide and, standing 15°, reaches the hole sub1 of the taped layout: the build stops on that hole's Boolean check, as it should. The Blender test that uses P0-125 for the wide window now builds it with the box stub. The neck needs its own width before a window wider than the 95 cm³ one gets a neck (doc 09 section 8, item 8).
- The two bodies built to show the other pipe angles (`P4-80-st15-lvl`, pipe level with the body; `P4-80-st15-m25`, pipe −2.5°) pass every check, but their thinnest plastic is 0.95 and 0.92 mm, under the owner's 1.2 mm: the neck keeps 1.2 mm under the pipe at its stations, not everywhere, once the pipe lies more than about 12° under the neck. If the owner picks one of them, the neck has to be fixed first.
- The option bodies of the decision sheets (`P4-80-el-d-*`, `P0-*-el-d-*`) and the two test bodies `P4-80-st15-*` are from before the rule; their reports and pictures stay as records. Their commands no longer rebuild the same bodies.
- `Analizes_ocarinas/Window_cutout/` (`measure_windows.py`, `render_windows.py`) was not rerun.
- `tools/geometry_check.py -- bodies` was not rerun as a report writer; the reports of bodies in no stage list are older still.

## Shell-edit build (prototype, 2026-11-18)

Branch `shell-edit-prototype`, cut from `addon-v1` at `a7a0e98`. Nothing of the stage builds changed: a body built in one step is the body it was.

**What the owner asked for (2026-11-18).** A user should be able to shape the instrument. Two ways were compared. (a) The user sculpts any volume and the add-on hollows it: set aside, because the chamber would be new every time and nothing the test prints measure would carry over. (b) **The add-on gives the shell and the user edits it: chosen.** The owner's decisions: the body and the neck are two separate objects ("the volume as one shape and the neck as another"), fused when the body is finished; no broad movements are intended; moving the finger holes and a neck longer than the pipe are "for the experiments afterwards". The owner's view on a longer pipe, for that later experiment: it "should not throw the ocarina much out of tune, but it does affect the pressure consistency and adds a little bit of volume in theory".

**How it works** (`ocarina_addon/shell_edit.py`, `body.build_body(outer=...)`).

1. `shell_edit.build_base(preset, V0)` (operator *Ocarina: Build Base*) runs steps 1 to 3 of the build and stops: sizing, chamber, plain skin. It makes four objects in one collection: `OCA_<id>_shell` (the chamber moved outward by 4 mm, **solid**), `OCA_<id>_neck` (the voicing block of the rules, solid), and two wire objects that cannot be selected, `OCA_<id>_chamber` and `OCA_<id>_cuts` (the pipe, the window and the 12 hole cutters). What step 3 needs is stored on the shell object as JSON (custom property `oca_base`: the preset values, V0, rating, window wall, hole set, voicing hash, object names).
2. The user edits the shell and the neck. Modifiers and object transforms are read when the body is finished (`meshutil.evaluated_arrays`).
3. `shell_edit.finish(shell object)` (operator *Ocarina: Finish Body*) reads both meshes, checks that each is one closed solid, joins them, and calls `build_body` with them as the envelope. The base objects are hidden, not deleted, so the user can edit on and finish again.

**The wall at the holes.** In the kernel's model 1 mm more plastic over every hole makes most notes 60 to 70 cents flat (0.5 mm: about 30), so the holes cannot keep the sizes of the base. `body.shell_over_holes` sends rays along each hole axis over the hole's disc (4 rings of equal area, 16 spokes, and a ring on the rim) at the edited shell and at the plain skin of the same chamber. The wall of a hole is the rule's 4 mm plus the mean difference. On a shell that nobody edited the difference is zero, so the body is exactly the one-step body. The kernel takes a wall per hole (`sizing.size_body(wall_at_holes_mm=<dict or list>)`, new; `holes.hole_specs_from_params`). Deeper holes hold more air, and V0 counts the air in the holes, so the chamber is solved again for a smaller mesh volume; that moves the walls a little, so sizing, chamber and measurement repeat until the wall measured at every hole is within 0.02 mm of the wall it was sized for (3 rounds in every trial that changed a wall, 1 where none changed). The hole positions are those of the base (the Stage 3 mechanism, `holes_layout.with_rows`). The hole cutters start above the highest point of the shell over each hole.

**What guards an edit.** Refused with the reason: a mesh that is not one closed solid, faces pointing inward, a mesh that passes through itself, a neck that does not touch the shell, a chamber that comes through the shell. Failing checks: `wall_thickness` (less plastic over the chamber than the least wall), `windway_mouth_end` (new: a neck longer than the pipe closes it), and the voicing checks that existed (window, labium, flare around the window). Soft checks, `warn` only: `shell_hole_walls` (a hole whose wall is more than 1 mm from the rule's wall, or a hole that the thicker wall pushed above the finger-pad limit) and `shell_hole_rims` (relief around a rim above 0.5 mm, where a finger may not seal).

**Trials** (`tools/shell_edit_trial.py`; a program makes the edits a user could make; the table is `addon_checks/shell-edit-trials.md`, the reports `addon_checks/P4-80-edit-<trial>.md`, the pictures `addon_renders/P4-80-edit-<trial>/` with `base.png` for the edited solids). On P4-80:

| Trial | Edit | With the base's holes (kernel model) | Finished body |
| --- | --- | --- | --- |
| `plain` | none | on pitch | the one-step body: same diameters, plastic volume equal to 4 decimals of a cm³ |
| `tail` | tail 25 mm longer, solid | on pitch (no hole is touched) | 165 mm long instead of 140; chamber unchanged |
| `sculpt` | longer tail, 1.5 mm boss over R ring, groove across L middle, 0.6 mm relief everywhere, neck 20 % thicker | up to 50 cents flat | walls 3.96 to 5.78 mm; R ring hole +0.65 mm; capped air 80.00 cm³; both soft checks warn |
| `remesh` | voxel remesh at 0.6 mm and a cloud displacement, as modifiers (119,000 triangles, another mesh altogether) | up to 22 cents flat | walls 4.20 to 4.37 mm; no warning |
| `thick` | 2.5 mm more plastic over the whole finger deck | up to 186 cents flat | walls up to 6.72 mm; holes up to +1.19 mm; **L middle and L pinky go above the 10 mm pad limit in the `nominal` set** |

Every trial finishes with no unexpected failure, measured on the STL read back from disk. The "with the base's holes" column is the kernel's model, not a measurement. Edits that go too far behave as listed under "What guards an edit" (`tests/blender/test_shell_edit.py`, class `TestShellEditTooFar`).

The `sculpt` and `remesh` trials were also run on P2-80 (the waisted gourd) and P1-80 (the short teardrop), with `--preset`; their reports were not kept. All four finish with no unexpected failure, in 3 sizing rounds, with the capped air at 80.01 cm³. With the base's holes the sculpted P2 would be up to 51 cents flat and the sculpted P1 up to 67. P1 shows one thing the seed does not: its body ends less than 6 mm past the R pinky hole, so a longer tail there is plastic over that hole too (wall 5.43 mm, rim relief 1.44 mm, both warned). On a short body the tail cannot be lengthened without touching the last hole.

**Tests (2026-11-18, `python tools/run_tests.py`).** kernel 133 (one new: a wall per hole), plain 102, Blender 63 with 1 skipped (20 new in `tests/blender/test_shell_edit.py`), extension 4: all pass. The Blender suite now takes about 10 minutes. The operators were run in a background Blender (register, *Build Base*, an edit, *Finish Body* with the neck as the active object, export); they were not clicked in the interface.

**What this does not show.** Nothing was printed. A hole deeper than 4 mm is a prediction of the kernel's chimney model: every Stage 2 body has 4 mm walls, so no test print measures it (the reason for the `shell_hole_walls` warning). Nobody sculpted by hand: the trials cover a remeshed mesh and modifiers, not a real session with its accidents. The relief, the boss and the groove are smooth; sharp or undercut detail was not tried.

**What I chose myself (the owner can overrule each).**

- *(No longer my choice: decided by the owner on 2026-11-18.)* **Holes under added material are sized again for whatever wall the add-on finds, with a warning past a limit.** The owner: "we should resize the holes for whatever thickness it finds past the limit. I think that your recommendation is really sound." The other way, a protected 4 mm land around each hole, is not built. Where the limit lies is still my number (next item).
- *(No longer my choice: decided by the owner later on 2026-11-18.)* **The least wall of an edited shell is three printed walls, 1.32 mm** (`SHELL_MIN_WALL_MM`; it was my 2.0 mm). See "Owner notes, neck volume trials and next steps".
- **Two limits** in `body.py`: `shell_hole_walls` warns beyond 1 mm from the rule's wall, `shell_hole_rims` warns above 0.5 mm.
- **The neck's length is fixed** (owner: parked). The pipe keeps the length of the voicing record; a neck that is longer fails `windway_mouth_end`.
- The id of a finished body is `<base id>-edit`.

**Not built.** Hole markers that the user can move (parked by the owner; their intent, noted later on 2026-11-18: the markers change in spacing and curvature as a group, not hole by hole, and the sizes stay automatic). A stretching pipe (parked). A sidebar panel: the two operators are in the bare menu. Stage 3 constants together with an edited shell (`build_body` refuses `sizing_fn` with `outer`). A quad mesh for the shell: the base shell is the triangle mesh of the skin, about 1 mm edges; a user will want to remesh it before sculpting. Enforced keep-out zones: the window face, the flare and the mouth end are checked after the edit, not masked during it.

## Owner notes, neck volume trials and next steps (2026-11-18, after the shell-edit prototype)

**Owner notes (their words in quotes).**

- **Hole markers, still parked.** "my intent is not to have a user move each fingering hole independently, but allow them to have the markers change in spacing and curvature, the size would be dynamic beyond the user control (take note, keep parked)". So the future control is a hand line per hand (its spacing and its curve), not twelve loose markers, and the kernel sizes the holes. Nothing was built.
- **Least wall of an edited shell: three printed walls.** "the least wall thickness would be 3 walls which in standard FDM 0.2 is like 1.32 adjust if this is not the exact value for standard profiles". Applied: `SHELL_MIN_WALL_MM = 1.32` in `body.py` (it was my provisional 2.0). I did not adjust the figure: 1.32 mm is 0.42 mm (outer wall) + 2 × 0.45 mm (inner walls), the line widths of the standard 0.20 mm profiles of Bambu Studio and OrcaSlicer for a 0.4 mm nozzle. PrusaSlicer's 0.20 mm profiles use 0.45 mm for every wall, which gives 1.35 mm, the figure this file uses for the voicing block. The message of `wall_thickness` now says "three printed walls", and the test that carves a shell carves 3.1 mm instead of 2.5 mm, so that it still goes under the limit. Not changed, because they are older and separate numbers: 1.2 mm around the pipe (owner, 2026-11-17), the 1.2 mm wall of an inward tube, and the 0.4 mm sliver limit.
- **The neck of the rules is wrong.** "the current one cuts too much of the upper neck like it trying to voice upwards and the neck is tilted with the windway which goes against my decisions of using it to hide the tilt, review again the example stl, run experiments on that and provide the renders".

**The neck: what was found** (record, pictures and scripts: [Analizes_ocarinas/Neck_volume/Neck_volume.md](../Analizes_ocarinas/Neck_volume/Neck_volume.md)). The sample was measured again in the frame of its own window. Its pipe stands 17.65° off the window face; the **top line of its neck is parallel to the pipe** (20.1°), with 2.1 to 2.5 mm of plastic over the pipe from end to end, and it runs into the outer face of the body before the window. The neck's volume is under the pipe, and the neck's middle line stands 35°. On 2026-11-18 I had applied "the pipe lies 10° lower than the neck" between the pipe and the neck's top line. That put a wedge of plastic over the pipe (4.7 mm at the exit, 9.1 mm at the mouth end) which stands 10.1 mm above the window, and the window cut digs a funnel through it (679 mm³ against 446 mm³ on a level neck). Both of the owner's points come from that.

**The trials.** `Analizes_ocarinas/Neck_volume/neck_trials.py` builds seven bodies `P4-80-nk-*` (reports in `addon_checks/`, pictures in `addon_renders/` and in the analysis folder). A prototype setting, `neck_cover_mm` (in `voicing_geo.UNHASHED_KEYS`, used by no preset), makes the top line of the neck follow the pipe with that much plastic over it. With 2.2 mm and the pipe at the rules' +5° (`P4-80-nk-a`): 2.2 mm over the pipe everywhere, 3.5 mm above the outer face at 9°, the cut removes 435 mm³, the neck's middle line stands 19° (15° with a slimmer foot), window, lip, ramp and capped air as the record says, no unexpected failure. Pipe angles 0°, +5° and +10° pass; the sample's 17.65° fails four checks on a 4 mm wall (the sample's wall is 5.3 mm). The add-on's cut was also made in the sample itself (`sample_cut.py`), as a picture.

**Nothing was decided and no rule changed.** `[voicing_rules]`, the presets, the stage bodies and the base of the shell-edit build are as committed in `45b3486`. The body of the rules still has the neck the owner objected to.

**Second round, later the same day** (record: the same file, section 7). The owner was not yet on board: "I am still not all on board with the neck and voicing current cutout specifically the upper shelf cut of the voicing", and "the neck for bulb shaped ocarinas is thrown backward further, however also the cuttout, use as a reference of the top portion the top part of the ECAN3 or NBN". He gave two STL models of bulb-shaped 12-hole ocarinas ("Ocarina 12" and "Deluxe", in his Downloads folder) with the condition that they stay out of the analysis: they play, but he does not vouch for their tuning. **They are used for shape and position only.**

- *Measured in the frame of the body* (`refs_position.py`): on both models the roof over the windway exit is a thin plate (2.2 and 1.4 mm) cut square; neither has a shelf, and neither have the NBN (1.2 mm plate) or the ECAN3 (a taller upright wall). Both models stand 11° to 18° more level than the add-on's bodies: their window faces 13° and 19° from straight down toward the player and their pipe climbs 12° and 19° toward the deck, against 30° to 32° for both on P1 and P4. The cause is in the presets: the port is 45° around the body on every one of them, and the pipe lies along the body's surface there.
- *Prototype* (`voicing_geo.neck_solid`): with `neck_cover_mm` and a `stub_pitch_deg` above the windway pitch the neck now has a straight flank at its own angle with the pipe lowered inside it (until now the flank could only follow the pipe); `neck_cover_exit_mm` sets the roof at the exit; the flank never stands above the window's outer face at the exit plane, because a square cut would leave that plastic as a step inside the outside keep-out. All of it is off unless a trial names it; the default build is unchanged.
- *Trials* (`throwback_trials.py`, ten bodies `P1-80-*` and `P4-80-*`): `sq`, the following neck with the roof cut square (`shelf_angle_deg=0`), passes on both bodies. `tb-l` (port 30°, pipe +8°, neck level with the body, square roof) passes on P1 and is close to "Ocarina 12" in section. `tb-f` (the same with a neck that follows the pipe, close to "Deluxe") fails `topology` on P1 with one pair of triangles that pass through each other; not looked into. On P4 both thrown-back trials failed `hole_to_voicing`; that was an error of the check, corrected below ("Rule version 3 applied").
- Not built: the ECAN3's rounded top edge, the NBN's roof below the body's surface, a shorter window (the models have about 7 mm against 9.65 mm), a jet steeper than +8°.

**Third round, 2026-11-19: the owner chose** (record: the same file, section 8). "tb-F but adjust the neck volume a little so in its along the body view its closer to the deluxe cross section. so technically the neck wouldn't follow the pipe also go with the roof cut square". So: the voicing thrown back as in `tb-f` (port 30° on the teardrop, pipe +8°), the roof over the exit cut square, and a neck whose deck side is straight and fuller. Built: `tb-d1` (the straight flank the owner drew; 24.5 mm deep at the body) and `tb-d2` (the Deluxe's proportions; 27.5 mm deep, a cone in plan too). Both pass every check on P1-80. On P4-80 I reported that the foot of the neck met the left thumb hole; that was an error of the check, corrected below. New prototype settings in `voicing_geo.UNHASHED_KEYS`: `neck_depth_exponent`, `neck_width_exponent`, `neck_floor_mm`, `neck_corner_cover_mm` (sections of two half ellipses, so that a deep neck keeps 1.3 mm over the pipe's corners). **A mesh fault was fixed on the way**: a needle a few millionths of a millimetre high at the mouth end of the neck made `topology` fail on two trials; `meshutil.cleanup` now repeats its needle repair at the spacing of single-precision numbers, only on a mesh that would otherwise fail. No rule had changed at that point.

**Rule version 3 applied, 2026-11-19** (record: the same file, section 9). The owner picked `tb-d1`. It is now the rule:

- `[voicing_rules]` in `params/alto_c_12hole.toml`: `rule_version = 3`, `shelf_angle_deg = 0`, `stub_style = "cone"`, `stub_pitch_deg = 8`, `windway_pitch_deg = 8`. `kernel/voicing.py` knows the style `cone`. Every voicing hash changed (65 / 80 / 88 / 95 cm³: `8533277752bf`, `312011ec9f0e`, `fa2a2dd2e3f6`, `237c069dec0d`).
- `ocarina_addon/presets/cavity_presets.toml`: `port_angle_deg = 30` on P0 to P4 (the stub preset S0 keeps 45).
- `ocarina_addon/voicing_geo.py`: the cone neck is the build of the style `cone` (roof 2.2 mm at the mouth end, 1.7 mm at the exit, 1.3 mm over the pipe's corners, the deck side straight, 2.78 window widths deep at the body). The prototype settings of the trials stay in `UNHASHED_KEYS` and no preset uses them.
- **Two values came with the picture and were not confirmed one by one:** the pipe at +8°, and the port at 30° on P0, P2 and P3 (the trials built P1 and P4).
- **A correction.** The second and third round said that on the seed P4 the foot of the neck touched the left thumb hole. That was wrong: `hole_to_voicing` measured against a box as wide as the neck's foot. The check now measures, on the built body, the plastic that stands on the skin beside each rim (`checks_geo.plastic_on_skin_at_rim`; a touch from 0.3 mm). P4 has the same neck as every other body. On an edited shell the comparison is the user's shell with and without the user's neck, so that a boss or a thicker deck is not taken for the neck; a shell that comes in one piece with its neck is not measured, and the check says so.
- **Stages:** Stage 1 six of seven clean (the optional V-a3 fails `voicing_keepouts`, as before), Stage 2 eight of eight, Stage 3 seven of seven. On P4 the capped air measured on the final mesh reads 79.91 cm³ (−0.12 %, inside the 0.5 % limit): the measurement leaves out a box around the window and part of the left thumb hole's chimney lies in it. The built air is 80.01 cm³.
- **The synthetic examples were rewritten** (`python kernel/synthetic.py --write-examples`): the invented round-1 measurements and `calibration/synthetic-fitted-constants.toml` are keyed by voicing hash, and with the hashes of rule version 2 in them Stage 3 did not recognise its printed bodies and gave them a new window without saying so. My first Stage 3 run under rule version 3 had that fault; the run reported here is the one after the rewrite. Only the hashes changed in those files.
- **Shell-edit trials:** all five (`plain`, `tail`, `sculpt`, `remesh`, `thick`) have no unexpected failure.
- **Thinnest plastic.** The stage reports now read 1.18 to 1.32 mm as the thinnest plastic of a body (it was 2.0 mm and more): that is the roof of the cone neck over the pipe, 1.2 mm by the owner's rule of 2026-11-17. The report tests ask for 1.15 mm.
- **Tests:** `python tools/run_tests.py` on 2026-11-19: kernel 133, plain 102, Blender 63 (1 skipped), extension 4, all pass.

**Next steps, in order.**

1. **The owner confirms the two values that came with the picture**: the pipe at +8°, and the port at 30° on P0, P2 and P3. A separate experiment (branch `low-voicing-experiment`) tries the voicing further around the body; if the owner picks an angle there, it replaces the 30° before anything is printed.
2. **The owner edits one base by hand** in Blender. The two operators were run in a background Blender only; nobody has sculpted a base yet.
3. **The two limits that are still mine**: `shell_hole_walls` warns beyond 1 mm from the rule's wall, `shell_hole_rims` above 0.5 mm.
4. **The parked experiments, when the owner opens them:** the hand-line markers (spacing and curvature, sizes by the kernel), then a neck and pipe longer than the rule.
5. **Prints.** Nothing was printed. The Stage 1 stubs can be printed once step 1 is settled, because the pipe angle and the neck are in the voicing hash.

## Questions for the owner (state after C6)

Before Stage 2 is printed (the first print freezes the layout, doc 04 D10):

1. **Scale the hand template, and on which surface do the hand checks measure?** (Open problem 15.) On the cavity surface the left hand span is 48.9 mm on P1 and P2 and 49.4 mm on P3 (ok range 50–60); at the outer skin, where the fingers are, it is 52.3, 52.2 and 51.5 mm. The checks use the cavity surface, as doc 06 did. Assumption made: nothing was scaled and nothing was tuned.
2. *(Answered 2026-11-18: the slide is 10 mm; open problem 19 is closed.)* **The left subhole slide and round 2.** (Open problem 19.) 9.5 mm gives a 3.63 mm edge gap now and 3.05 mm at the k_hole 1.0 diameters. Lengthen the slide in round 1 (about 9.9 mm), accept a smaller gap in round 2, or let the subhole move in round 2? Assumption made: 9.5 mm as decided; Stage 3 reports the failure.
3. **P3 hand overlap: 12 mm (built) or 6 mm?** (Open problem 16.) Both reports are in `addon_checks/`.
4. **The 35 % sideways limit** pulls the index holes toward the deck line and shortens the middle-to-index distance (P2 16.4 mm, P3 16.3 mm). Keep it? (Open problem 17.) Assumption made: kept, as in C4.
5. **`hole_lean_side_away_max_deg = 5`** is my number; doc 06 gives none. (Open problem 18.)

After a hand check on a printed P2, or later:

6. The separate outer body and the P4 body (doc 02 Q10, Q11). Not built; P4 is not in Stage 2. *Update 2026-11-17: P4 is now the seed body and is in Stage 2 (item 14 of the list from docs/07); the flat P4 with a shaped outer body was dropped. The separate outer body is still open.*
7. Which finger closes the left subhole (doc 02 Q8, the part that needs a print).
8. The window tip radius (1.0 mm) and the wide-teardrop family (open problems 3 and 11).
9. Stage 3 keeps the printed V0 by default (`--retarget-volume` is the other choice). With the synthetic constants this gives an A4 error of −38 to −41 cents.
10. The wording of the criterion "position factors within 1 % with ±5-cent noise".
11. The licence. The manifest says GPL-3.0-or-later; the repository has no licence file. None was added.

Things I did not do because they need a go-ahead:

12. **Pushing to GitHub and merging `addon-v1` into another branch.** Everything is committed locally on `addon-v1`.
13. **Edits in `docs/` beyond the approved ones.** These places still state a superseded rule or an old number: doc 03 §8 (the "Under review" paragraph about the 124 mm stop); doc 04's shape table (P2 "at the cavity-mode limit (c/2L ≈ F6)") and its D9 row and "Before printing" list (they name the doc 05 checks); doc 02 Phase 4 step 9 (`hand tilt`, `hole tilt`) and its repository map (no doc 06, no add-on, no tests); doc 04's filament masses (the generated bodies are about a quarter lighter, open problem 20); doc 06 §5 gives no number for "leans away".

From the windway and body-shape study (docs/07, 2026-11-16); items 14 and 15 belong before Stage 2 is printed:

14. **Stage 2 bodies: built on 2026-11-17 (set A, provisional).** P0 unchanged; `P4` is the seed; P2 and P1 kept; P3 stashed (preset kept, in no stage list); the old P4 proposal dropped. Still the owner's to say: whether `P4` is the right name for the seed (my choice) and whether P1 is marked an acoustic body in the reports (left as it is). The layout of P4 (port 0.35, centre 20 mm) freezes with the first Stage 2 print (doc 04 D10).
15. **Round or flatter seed: round, saved for now (2026-11-16).** Both were built at 80 cm³: round (cavity height / width 0.76) has its first cavity mode at 1.36 × F6; flatter (0.64) at 1.29 × F6, under the pass line.
16. **The two Songbird sizes.** The Alto C length is an estimate (170 mm); the Tenor A's size fits a lowest note of about F♯4. A ruler on an Alto C or a tuner on a Tenor A would settle them. No number the add-on uses depends on either. The Songbird report §8 holds the owner's notes on a longer, lower body; the scope stays the 12-hole alto C.
17. **`ergo_hand_offset` on round bodies.** Both ceramic alto C references have their two rows of holes 36–42 mm apart across (limit 18–28 mm). No change was made.
18. **A solid tail as a lever (idea, 2026-11-16).** The Spencer's thumb-face half is solid in its tail third. In the model of the Spencer report §7.3 that raises the first cavity mode by 0.14 × F6 at equal air volume. The add-on has no such option. Nothing was built; the owner has not asked for it.
19. **Internal partitions: experimental, parked (owner, 2026-11-16).** The walls inside the Spencer chamber are the partial partitions of US 7,799,980 B1 (Norman Spencer Register; Google Patents lists it as expired, lapsed 2014-09-21). The owner wants them kept as an experiment for later, before advanced builds are explored. Summary, the patent's drawings and a model: [US7799980_partitions.md](../Analizes_ocarinas/Patent_US7799980/US7799980_partitions.md). The model: a partition a little above the mid-line weakens the thumb hole behind it by 10–15 % and lowers the closed-hole cavity mode from 1.48 to 1.10–1.24 × F6 on the Spencer body model; the patent's claim (tone of the top notes) is outside what the add-on computes. Not part of Stage 2 or Stage 3. Nothing was built.
20. *(Decided and built 2026-11-18: the ellipse cut "P3" is the rule; see "Owner decisions applied".)* **The window cut-out: proposal, not built (2026-11-17).** The owner named the window section as the part with the most room for improvement: visible from outside, it must be smooth and functional. Two models were reviewed (NBN by RodrigoSC, ECAN3 Eclipse): [Window_cutout.md](../Analizes_ocarinas/Window_cutout/Window_cutout.md). Both cut the labium from the body wall with a scoop wider than the window, flare the sides of the window above a short lip, and add no block; the add-on has a box around the window, vertical 4 mm walls and a ramp that ends in a crest. Proposal A: a 1.5 mm land then a dish, a trough ramp cut from the skin, no block downstream of the exit, rounded rings, and the land height as a value of the voicing record. **It changes the throat, so it must be settled before the Stage 1 stubs are printed.** *Later the same day:* the owner found proposal A too wide and suggested a cone as a second pass. Built as an experimental option: `voicing_geo.build(..., cut_style="cone")`, set by the preset values `window_cut`, `cone_widen_mm`, `block_front_mm` (default: the fan cut; no preset uses them). The cone goes through the window outline at the top of the lip, so the lip stays 0.4 mm and the ramp 20°, and the opening is 10.8 mm across instead of about 25 mm. Test bodies `P4-80-cone` and `P4-80-coneb` (box ends at the widest point; the cleaner one) pass every check. Open: whether it becomes the default, the rounding pass, and the mouthpiece neck (Window_cutout.md §8). *After the owner's review of the cone tests:* three more experimental settings, all off by default: `shelf_angle_deg` (the wall above the exit cut back, with `shelf_land_mm` of roof kept), `windway_pitch_deg` (the windway turned about the lip edge; positive raises the mouth end) and `stub_pitch_deg` (the outer stub turned on its own). Checks and capped air follow the turned windway (`VoicingSolids.duct_frame`). Test bodies `P4-80-shelf` (passes), `-p10` and `-p10s7` (only the outside 45° keep-out fails), `-m4` (0.49 mm under the windway floor at the exit; the limit of lowering is about 3° on this body). Not built: a shaped neck, a sideways turn of the whole voicing, a windway that turns only at its exit, rounding (Window_cutout.md §9). *After the owner's sample STL (body, neck, wind cut):* `stub_style=neck` builds a base neck (bell of ellipses along the windway). **Owner's rules:** only a lowered windway is used in practice; the neck hides the tilt (it does not turn with the pipe); 1.2 mm between the pipe and the other surface is acceptable; the window keeps some sideways flare (the cone cut is now a dish, `cone_widen_mm` 2.5); a user may bring their own outer shell and neck, out of which the add-on cuts chamber, holes and voicing (not built; `OUTER_MESH_HOOK` is the place). Test bodies `P4-80-neck` and `P4-80-neck-m25` pass every check. On P4-80 the windway can be lowered about 2.7° before less than 1.2 mm is left under it at the exit; the chamber is the limit, not the neck (Window_cutout.md §10). *Then:* the owner put the own-shell path on hold, pointed at the step under the lip (the end of the pocket's flat margin) and asked for dish variations as pictures only. New options, all off by default: `pocket_blend_radius_mm` (the pocket ceiling falls away as a curve; `P4-80-neck-smooth` passes every check), `cone_flare_exponent`, `cone_shoulder_blend_deg` (made a seam; I would drop it) and a third cut style `window_cut=ellipse` (one surface lofted from the outline to an ellipse: no fold; my proposal). `voicing_dimensions` fails on the ellipse cut because the check measures the windway half where that cut has already opened. Variations `P4-80-dish-b` to `-h` and `-p1` to `-p3` are picture bodies, not validated. Waiting for the owner's choice of cut and widths (Window_cutout.md §11). *Owner's choice (2026-11-17):* the ellipse loft; the two-part dish was rough at the sides in all of A to H; P1 (+4 mm, shelf 50°) and P3 (+3 mm, 40°) look best. Validated (Window_cutout.md §12): for this cut the window area is measured as the free opening seen along the normal (`window_area_by_projection`); the cutter got a no-overhang rule after the loft was found to lean in over the wide 125 cm³ window (120.2 against 123.5 mm²); `meshutil.cleanup` got a fallback for needle triangles left by a lowered windway (reached only by a mesh that is not clean otherwise) and counts overlapping triangles for the body solid. `cone_shoulder_blend_deg` removed; `cone_widen_share` added and then advised against (a fixed 3 to 4 mm suits the 4 mm wall at every volume). Twelve bodies pass every check: P4-80 with P1 and P3, level and lowered 2.5° and 2.7°; P1-80, P2-80; P0-65 and P0-125. New test class `TestEllipseWindowCut`. Still experimental and off by default. **Open:** P1 or P3 as default; whether the cut, neck and blended pocket go into the stage bodies before the Stage 1 stubs are printed; the "cone" names of the settings; the wide window at 125 cm³, where the loft is not smooth.

## Open problems and decisions log

1. Closed in C2b. Doc 04 now says 88.6 cm³ and describes the teardrop that is wider than long.
2. Pad-limit failures at the largest ladder steps are expected by the plan (doc 04: "the real limit is unknown"). The check reports them; the generator in C5 must not refuse to build because of them.
3. **Closed 2026-11-17 (owner decision): the teardrop tip radius stays 1.0 mm.** Evidence: Heuer's Video #8 teaching model has a narrow tip close to it (docs/01-source-review.md §5.5). Background: the 1.0 mm tip radius was first found by fitting doc 04's table, not from a source. The Miracle window is much blunter at its narrow end: 4.8 mm wide at 1.5 mm from the tip, where a 1.0 mm tip radius gives about 2.5 mm. The 1.0 mm corner radius of the forced rectangle has the same origin and is **still open** (it only affects stub V-b). Both are in the TOML.
4. Closed in C5. The stub measurement file exists (`measurements.stub_template`, `write_stub_file`, `load_stub`; schema `ocarina-stub-measurement-v1`): stub id, hash, water fill, room temperature, three takes of the pitch, and the two yes/no answers of Gate 1. Stage 1 writes a blank one per stub. `tools/stub_eta_w.py` prints η_w from filled files.
5. Hole offset is one global number. FDM probably shrinks small holes more than large ones. The data from Stage 2 will show it; a size-dependent offset is a later change.
6. Changed in C2b: the profile estimate of k_hole does not need the convention. It needs bodies of one shape with different hole diameters, and it assumes that one psi per hole name holds over the whole P0 ladder. If psi changes with volume, the profile estimate absorbs that change. The data can show it: the reduced chi-square of the profile (`chi2_min / dof`) is then well above 1 and the interval widens.
8. Closed in C4b. P3 at 80 cm³ is too short for the Miracle hand span. Its two hands now overlap by 12 mm each along their own lines (preset value `hand_overlap_mm`), the finger pitch is not compressed, and P3-80 builds with no unexpected failure. What is still missing shows as warnings (see "C4b evidence" and open problem 16).
9. **The bore wall is a little longer than the axis chimney on a curved wall.** The kernel's chimney is the wall along the hole axis (4.000 mm, measured). The mean length of the cut bore wall is up to 0.09 mm longer (P1-80, large holes near the ends), because both wall surfaces curve away from the hole. The reports list both numbers. The fitter measures the effective conductance, so this goes into the position factors.
10. **No flat land around the hole exits.** `hole_flat_land_d` (doc 02, "hole land") is not built and not checked. The test bodies are taped, not fingered. A later session can add a flat patch per hole.
11. **Window tip radius: closed 2026-11-17, stays 1.0 mm (see item 3).** The renders show the 1.0 mm tip as a narrow nose at 65 and 80 cm³ and as a small nose on a wide oval at 95 to 125 cm³ (`addon_renders/P0-*/voicing.png`, `section_window_plan.png`). The Miracle window is much blunter at its narrow end. Nothing was changed. **Evidence added 2026-11-17:** Heuer's Video #8 teaching model has a narrow tip close to the 1.0 mm tip and puts the broad end at the windway (docs/01-source-review.md §5.5). Still the owner's decision.
12. *(Changed 2026-11-18: the stage bodies have the neck, which flares into the body and stands 15° off it. The box is the plain build, on stubs V-af and V-b only. Shaping the mouth end for the lips is still later work.)* **The mouthpiece stub is a plain box**, 7 mm thick and (window width + 8 mm) wide, with square edges. It points toward the player and 34° up from the plane of the body. Shaping it for the lips is later work.
13. Closed in C4b (was: the hand-ergonomics review of [docs/05](../docs/05-ergonomics.md)). The subholes sit a forward slide from L ring and R middle, the soft `ergo_*` checks exist, and P0 is labelled. What the checks still report on P1–P3 is in "C4b evidence". Open with the owner: the separate outer body and the P4 body (doc 02 Q10, Q11), after a hand check on a printed P2.
14. Closed in C4b (was: the P2 layout slide and [docs/06](../docs/06-ergonomics-challenge.md)). The P2 preset has `layout_centre_from_port_mm = 23`. The rules of doc 06 §5–6 are built.
15. **Which surface do the hand checks measure? (owner question, C4b.)** The `ergo_*` checks use the hole centres on the cavity surface, as doc 06 did for the add-on bodies. The fingers touch the outer skin, 4 mm further out along each hole axis, and the axes spread outward. There the same holes are further apart: the left hand span is 52.3 mm on P1-80 (48.9 mm on the cavity surface), the subholes are 10.5–10.7 mm and 8.2–8.6 mm from their parents (9.5 and 7.5 mm), and no finger pitch is under 16.5 mm on P1 and P2. The Miracle template was wrapped onto the cavity surface, but its millimetres were measured on the outside of that instrument. Every report gives both numbers. If the owner chooses the outer skin, the span warnings of P1 and P2 go away without a scaled template, and the subhole slides should then be set at the outer skin too (9.5 mm there needs about 8.5 mm on the cavity surface, which is under the 3.4 mm edge gap; the gap rule would then also have to move to the outer skin, where the Miracle's 3.4 mm was measured).
16. **P3 hand overlap: 12 mm or 6 mm (C4b; the preset has 12).** With no overlap the right pinky hole does not fit on the deck. From 8 to 11 mm the right subhole and the L index hole (10.8 mm) are closer than the 3.4 mm edge gap after the allowed moves. 6 mm and 12 mm pass every hard check. 12 mm gives 10.0 / 7.8 mm of land past the pinky holes and pinky leans of 23° / 31°, and costs two more warnings by small amounts (`ergo_hand_offset` 17.5 mm against 18; `ergo_index_meet` −23.3 mm along against −22). 6 mm gives 4.7 / 3.4 mm of land and leans of 35° / 52°. Reports: `addon_checks/P3-80.md` (12 mm) and `addon_checks/P3-80-ov6.md`; pictures in `addon_renders/P3-80/` and `addon_renders/P3-80-ov6/`. At 12 mm the L index hole moved 1.31 mm along its row to keep the gap to sub2 (3.41 mm).
17. **The sideways limit shortens one finger pitch (C4b; reported, not changed).** `holes_layout` keeps a finger hole within 35 % of the half section from the deck line. On narrow sections this pulls the index holes toward the deck line: P1 R index −12.1 → −10.2 mm and L index +11.4 → +10.7; P2 −12.1 → −8.7 and +11.4 → +9.5; P3 −15.4 → −11.2 and +14.8 → +11.0. The middle-to-index distance then drops (P2 16.4 mm, P3 16.3 mm on the cavity surface: `ergo_finger_pitch` warns), and the two hand lines come closer (P2 18.7 mm, P3 17.5 mm). The limit existed in C4; since C4b each use is in the layout messages and in `hole_layout`. Raising the limit would move the index holes onto steeper deck; that is a layout change for the owner to decide before Stage 2.
18. **`hole_lean_side_away_max_deg = 5` is the session's number, not the owner's.** Doc 06 §5 says "warn if it leans away" from the covering hand and gives no tolerance. The references lean away by 0.5° at most. With 5°, `ergo_hole_lean_side` warns on the R pinky of P1 (13° away) and P2 (7° away). The value is in `[ergonomics]` of the parameter file.
19. **Closed 2026-11-18 (owner decision 1: the left slide is 10 mm).** At 10 mm the edge gap between the left subhole and L ring is 4.76 mm at the print diameters and 4.28 mm at k_hole 1.0, and Stage 3 from the synthetic constants (k_hole 1.17) has no `hole_spacing` failure: the smallest gap there is 3.52 mm (P4-80-r2). *The record:* **Round 2 at frozen positions breaks the 3.4 mm edge gap (C5; owner decision needed before the layout freeze).** Doc 04 D10 freezes the hole positions after round 1. The left subhole slides 9.5 mm from L_ring (D5). At the round-1 (k_hole 0.8) diameters the edge gap is 3.63 mm. At the k_hole 1.0 diameters it is 3.05 mm (L_ring 8.39 → 9.35 mm, sub1 3.34 → 3.56 mm), under the 3.4 mm limit. So any round-2 correction toward k_hole 1.0 fails `hole_spacing` on P1, P2 and P3. With the synthetic constants (k_hole 1.13) Stage 3 reports 2.80 mm (P1), 2.56 mm (P2) and 2.70 mm (P3, sub2 to L_index). The build is correct; the rules conflict. Choices: (a) size the round-1 slide for the k_hole 1.0 diameters (about 9.9 mm on P1 and P2; still inside the 9–10.5 mm acceptance and the 11 mm limit), (b) accept a smaller edge gap in round 2, (c) let a subhole move in round 2 (against D10). The P0 bodies are not affected (their smallest gap is 4.0 mm or more). `holes_layout.with_rows` is the code that keeps the positions; `tests/test_holes_layout.py` has a test that states the 3.05 mm number.
20. **The generated bodies are lighter than the doc 04 budget (C5; a finding, nothing to fix).** Solid PLA at 1.24 g/cm³ from the STL volumes, with 12 % added for supports: Stage 1 205 g for six stubs (doc 04: 204 g for four, about 100 g more for the two optional ones), Stage 2 598 g (doc 04: 807 g), Stage 3 542 g (doc 04: 741 g). A stub is 30 to 32 g (doc 04: 50 to 54 g), P0-80 is 55 g (84 g). The doc 04 masses were estimates made before any body was built. Doc 04 was not changed.
21. *(Moot since 2026-11-17: stub V-c was dropped with the 125 cm³ step.)* **Stub V-c has 2.95 mm of plastic at its thinnest place** away from the voicing (the other stubs 4.00 mm). The 26.6 mm wide voicing block of the 18.6 mm window meets the small egg at a shallow angle there. The wall check passes (it measures the plain wall, 4.000 mm). Seen in `addon_checks/V-c.md`; not changed.
7. The interval of the profile estimate knows the pitch noise only. Errors in the measured hole diameters (gauge steps of 0.05 mm are 1.7 % of a 3 mm hole) are not in the weights. On the repository's synthetic set the profile estimate is 6 % off with a stated interval of ±4.4 %. A later session can add the diameter uncertainty to the weights of the small holes.

22. **The 3 mm window wall is not built by the add-on (found 2026-11-17 in the C5 rerun; owner decision needed).** *Update 2026-11-18: with the standing neck and the flare measured as a flare, V-a3 fails by 2° (the neck is 47° steep seen from the rim of the lower outer face; 150 points). The question is unchanged.* `main` added `wall_at_window_mm` to the kernel and passed it to `build_body`, but the geometry was never run. The voicing block is built 3 mm high while the skin stays 4 mm (`wall_at_holes_mm`), so the window sits in a 1 mm recess and the skin stands above the outer face: `voicing_keepouts` fails on stub V-a3 (243 vertices above the 45° flare). The window, windway and labium measure correctly. To decide: a flat land of 3 mm blended into the 4 mm skin (how wide, what slope), or a 3 mm skin everywhere on that body, or drop the option. Until then V-a3 and P0-95-w3 must not be printed.
23. **Closed 2026-11-17: needle rows on the window side wall at the −0.2 mm labium offset** (`meshutil.repair_collinear_rows`; see "Merge with main and C5 rerun").
24. **Closed 2026-11-18 (owner decision 5): the build is in the voicing record and in its hash.** *The record:* **The window cut style is not part of the voicing hash (found 2026-11-17; decide before any print uses a cut other than "fan").** Doc 04 says each window wall has its own hash and its own η_w, because the throat changes the window's conductance. The cut style changes the throat as well: the window Boolean removes 548 mm³ on P1-80 with the "fan" cut, 474 mm³ with ellipse P1 and 458 mm³ with ellipse P3 (the plain prism is 251 mm³), and the ellipse cut also cuts back the wall above the windway exit (the shelf), which the fan cut leaves upright. The stubs are built with "fan". A body with the ellipse cut would carry the same hash as stub V-a and take its η_w, which was measured on a different throat. Proposal: put the cut style and its numbers (widen share, shelf angle and land, windway pitch) into the hashed values, or give Stage 1 one stub per cut. The shelf also bears on the open question of doc 01 §5.2 (throat depth on the windway side: Heuer's exit is about 6 mm below the top, the ECAN3 windows are 2.1–2.4 mm): it makes that side shallower.
25. **`cavity_mode_computed` is a closed-box number; the window moves it by up to about 10 % (2026-11-17).** On the two ECAN3 references the cell network with the window open gives 1.08 × F6 (OOT) and 1.34 (Eclipse), against 1.19 and 1.27 from this tool with everything closed: −9 % and +5 %. P2-80 (1.40) and P4-80 (1.36) pass the 1.3 line by less than that. Treat both as "measure in Stage 2", which doc 04 already asks for (spectrum per fingering on P1, P2, P4). The check itself is unchanged.
26. *(Moot since 2026-11-18: with the neck standing 15° and the pipe at +5° the plastic under the exit is 4.44 mm. It comes back if the pipe goes below the plane of the body.)* **A lowered windway uses up the wall under the windway exit (the drop of Heuer #3 and #8).** Plastic under the windway floor at the exit, at the −0.2 mm offset: P4-80 3.21 mm with the box stub and no tilt, 1.48 mm with the neck, the pocket blend and −2.5°; P0-95 2.22 mm with no tilt, **0.49 mm at −4° (fails `windway_floor_lip`, limit 0.8 mm)**. The 0.8 mm limit is a print-strength number. Heuer asks for "a certain amount of distance" at the drop and gives no number. Keep the tilt at −2.5° or less until a stub says more, and check `windway_floor_lip` at every volume before a tilt becomes a preset value.
13. **Ladder change (2026-11-17, owner decision).** Ladder 65 / 80 / 95 cm³, P0-88 is the Stage 3 prediction body, 110 and 125 cm³ are no longer printed, stub V-c is dropped. A 3 mm window wall is an option. See the next section.

## Ladder change and window wall option

What changed and why: docs/04-testing-phase.md, "Ladder change" and "Window wall option".

- **Kernel.** `sizing.DOC04_STEPS` is (65, 80, 88, 95). `synthetic.round1_set` has eight bodies (no P0-125); the synthetic round-1 files and `calibration/synthetic-fitted-constants.toml` were regenerated (`python kernel/synthetic.py --write-examples`), and `measurements/synthetic-round1/P0-125.synthetic.toml` was removed.
- **Window wall option.** `[voicing_rules] window_wall_options_mm = [3.0, 4.0]`; `make_voicing` refuses any other wall. The wall is hashed, so a 3 mm voicing has its own hash and η_w. The holes do not change with the window wall (test `test_window_wall_option_3mm`). Windows at 3 mm: 6.0 / 7.9 / 8.8 / 9.5 mm wide at 65 / 80 / 88 / 95 cm³; the teardrop turns wider than long at 96.9 cm³ (88.6 at 4 mm).
- **Add-on.** `build_body(..., wall_at_window_mm=None)`; the default body id gains `-w3` for a 3 mm window (P0-95-w3). `headless.py body --window-wall 3`. The operator has "Wall at the window" (4 mm / 3 mm). `tools/geometry_check_body.py`: the `bodies` set is the printed set plus P0-88 and P0-95-w3; `bodies range` adds P0-110 and P0-125 as generator range checks; `body P0 95 3` builds one body with the 3 mm wall. `tools/geometry_check.py -- cavities` adds 88 cm³ and keeps 110 and 125 as a range check (Stage 2 marks only 65 / 80 / 95).
- **Not run here.** No Blender in this session, so the add-on changes are compiled (`py_compile`) but not built. The C4 reports in `addon_checks/` (including P0-110 and P0-125) are from C4. P0-88 and P0-95-w3 have no report yet: run `tools/geometry_check.py -- bodies` in Blender 5.1.
- **Fitter consequences.** With three ladder steps the profile estimate of k_hole is less tight: on the synthetic round-1 files 1.180, interval 1.096–1.273 (±7.5 %), convention 1.069 (before: 1.134, ±4.4 %). The profile still drives (limit 15 %). Noise-free, the interval is 5.1 % (psi × 1.2) and 6.2 % (psi × 0.8); the test bound moved from 5 % to 8 %. A wrong k costs less at P0-88 than at P0-110 because 88 cm³ lies inside the ladder: with the convention estimate the prediction body is 5 and 22 cents off (P0-110: 10 and 27).

## Handoff for the C3 session

Read this section first. Everything is standard-library Python 3.12 in `kernel/`, tested with `python -m unittest discover -s kernel -v` (120 tests since C2b). Put `kernel/` on `sys.path`, then import by plain module name. No Blender imports exist or are needed.

### Where things live

| What | Where |
| --- | --- |
| All parameters and rules | `params/alto_c_12hole.toml`. New sections: `[acoustics]` (k split), `[voicing_rules]`, `[hole_rules]`, `[temperature]`. The older `[voicing]` and `chimney_mm` values are the doc 03 baseline. Do not use them for the test bodies. |
| Read the parameters | `config.load_params(path=None) -> dict` |
| Measurement template, synthetic example, synthetic round-1 set | `measurements/` |
| Synthetic fitted-constants file (format Stage 3 reads) | `calibration/synthetic-fitted-constants.toml` |
| Regenerate the synthetic files | `python kernel/synthetic.py --write-examples` |

### Command that regenerates the sizing table

```bash
python kernel/sizing.py --table
```

Other forms: `--v0 80 --holes` (every hole with k 0.8 and k 1.0, tubes, checks), `--v0 100 --rating loud`, `--json`.
The fit command is `python kernel/fit_measurements.py measurements/synthetic-round1/*.toml --write-constants out.toml`.

### Public API (all lengths in the records are millimetres unless the name ends in `_m`; inside the acoustic functions they are metres)

**`sizing.size_body(v0_cm3=None, rating=None, wall_at_window_mm=None, labium_offset_mm=None, *, params, voicing, eta_w, shape, ks, floor_key, psi, tubes_mm, volume_factor, hole_offset_mm, L_int_mm, internal_temp_c, wall_at_holes_mm) -> BodySizing`**
The one call the add-on needs. Defaults give the plain P0 test body (medium window, 4 mm walls, prior eta_w 0.90, `ks = {"print": 0.8, "nominal": 1.0}`).
Main outputs:
- `voicing` (a `Voicing`, below) and `voicing.version_hash`
- `holes.solutions["print"]` and `["nominal"]`: lists of `HoleResult` in opening order, with `name, opens, kind, d_mm, tube_mm, chimney_mm, wall_mm, G_mm, psi, d_plain_mm, below_floor, above_pad_limit`. `d_plain_mm` is the diameter without a tube (the number in doc 04's table).
- `holes.tubes_mm`: inward tube length per hole (0 for none). The tube bore equals the hole diameter. Tube wall is 1.2 mm (`[hole_rules] tube_wall_mm`).
- `cad_diameters_mm[key]`: diameter to draw in CAD = d − hole offset.
- `cavity_volume_for_mesh_cm3`: volume of the cavity mesh **before** tubes are added and holes are cut. V0 = mesh − tube plastic + hole air, so this is smaller than V0 by about 2 cm³. `wall_chimney_air_cm3` and `tube_plastic_cm3` are given separately.
- `v0_cm3` (the capped air target the acoustics assume), `p0_length_mm` (P0 egg internal length), `f_targets_hz`, `notes`, `c_m_s`
- `checks`: list of `CheckResult(name, status, value, limit, message)`. Status is `pass`, `needs_fem` or `fail`. `all_ok` is true when every check passes.
- `to_dict()` for JSON.

**`voicing.make_voicing(v0_cm3=None, rating=None, wall_at_window_mm=None, labium_offset_mm=None, *, eta_w, shape, window_area_mm2, params, ...) -> Voicing`**
`labium_offset_mm=None` resolves from `[voicing_rules] default_labium_offset_mm` (−0.2 mm since 2026-11-17); the allowed values are `labium_offset_options_mm` (−0.35, −0.2, 0). Numbers only, in mm and degrees: `shape` ("teardrop" by rule at every volume; "rounded_rectangle" only when forced), `window_length_mm` (9.65 medium), `window_width_mm` (broad end of the teardrop, or full width of the rectangle), `window_area_mm2`, `broad_end_length_mm` (length of the broad end along the jet: equal to the width while it is a circle, shorter when the teardrop is wider than long), `tip_radius_mm` (1.0, teardrop) or `corner_radius_mm` (1.0, rectangle), `wall_at_window_mm`, windway (`windway_exit_height_mm` 1.2, `windway_inlet_height_mm` 1.56, `windway_width_mm` = window broad end, `windway_length_mm` 30), `labium_ramp_angle_deg` 20, `labium_edge_thickness_mm` 0.4, `labium_offset_mm`, `keepout_inside_mm` 10, `keepout_outside_flare_deg` 45, `wh_ratio`, `version_hash`. Teardrop: broad end at the windway, narrow end (tip radius) at the labium. Rectangle: corners rounded with `corner_radius_mm`.
`shape="rounded_rectangle"` forces a rectangle of the same area (stub V-b only; the rule never picks it). `window_area_mm2=` fixes the area instead of solving it from V0. `Voicing.outline_mm()` returns the window outline as a polygon (x from the windway exit to the labium, y across, outward normal angle).
Stub recipes (Stage 1): V-a = `make_voicing(80)`; V-b = `make_voicing(80, shape="rounded_rectangle")`; V-d = `make_voicing(65)`; V-a3 = `make_voicing(80, wall_at_window_mm=3.0)` (optional); V-c (125 cm³) was dropped with the ladder change; coupons V-a0 / V-a35 = `make_voicing(80, labium_offset_mm=0.0)` / `(..., -0.35)` (V-a uses the −0.2 default). `build_body` has no labium-offset argument yet: add a pass-through like `wall_at_window_mm` when C5 builds the stubs. `voicing.stub_pitch_hz(v, stub_volume_cm3)` predicts the stub pitch.
`voicing.voicing_hash(values)` hashes the geometry numbers (1 µm), so the same window gives the same hash on any chamber.

**Holes (lower level):** `holes.size_holes(f_targets, X_w, V0, specs, ks, c, ...)`, `holes.solve_scale`, `holes.predict_scale`, `holes.plan_tubes`, `holes.hole_specs_from_params(params)`. SI units (m, m³, Hz).
**Checks:** `checks.range_ratio_check(sum_G, G_w_eff, limit)`, `checks.cavity_mode_check(L_int_m, f_top, c)`, `checks.ellipsoid_length_m(v_m3, r_length, r_width)`, `checks.hole_limit_check`, `checks.wh_ratio_check`.
**Measurements:** `measurements.template_from_sizing(body_sizing, body_id, shape)` then `measurements.write_measurement_file(path, m, blank=True)` writes the template for a generated body with the design numbers pre-filled. `measurements.load_measurement(path)` reads a filled file.
**Fitter:** `fitter.fit_bodies(bodies, params, share="shape", reference_shape=None, k_source="auto")`, `fitter.fit_body(body, params)`, `fitter.format_report(fit)`, `fitter.eta_w_from_stub(...)`. `FitResult.k_hole` is the value in use; `k_hole_source` says which estimate it is; `k_hole_profile` and `k_hole_convention` hold both (see "k_hole: two estimates"). The constants file carries `k_hole_source`, `k_hole_profile`, `k_hole_profile_interval`, `k_hole_convention` and `psi_geomean_reference` in `[acoustics]`.
**Constants:** `calibration.calibration_from_fit(fit, bodies, params)`, `calibration.write_calibration(path, cal)`, `calibration.load_calibration(path)`, `calibration.size_body_from_calibration(cal, v0_cm3, rating, ..., shape="P0", retarget_volume=False)` which returns `(BodySizing, info)`. For a voicing hash that was printed, the window is kept and eta_w is the measured value. For an unknown hash (P0 at 88 cm³, the prediction body) the window is solved with `eta_w_fallback`.

### What C3 to C6 must do with it

- Call `size_body(v0, rating)` with the V0 of the step. Build the cavity mesh to `cavity_volume_for_mesh_cm3`, not to `v0_cm3`. Cut each hole at `holes.solutions["print"][i].d_mm` (first print) and add an inward tube of `tube_mm` where it is above 0. Tube wall: `[hole_rules] tube_wall_mm`.
- For P1 to P3, pass `L_int_mm` (the real internal length) to `size_body`. The default is the P0 egg length, and the result records it in `L_int_source`.
- The pre-export checks in doc 02 map to: `checks` (range ratio, cavity mode, W/h, hole limits), the mesh volume against `cavity_volume_for_mesh_cm3` (0.5 %), and `voicing.version_hash`.
- Expected failing checks, not bugs: `hole_limits[nominal]` at 65 cm³ and above (L_index and E6 thumb exceed 10 and 12 mm at k 1.0); `hole_limits[print]` from 80 cm³ up (the print diameters of L_index and the thumbs exceed the pad limits). Do not stop the build on these; print them in the sizing report. The kernel's own `cavity_mode` check still returns `fail` for P2 at 80 cm³ (0.987 × F6) and `needs_fem` for P1 at 80 cm³ (1.12 × F6); since C4b the add-on reports those as `cavity_mode_c2L` with status `info`, so they are not failures of a build.

### Notes on Stage 3 and the report (written in C2; C5 built to them)

- **Tubes in Stage 3.** `size_body_from_calibration` plans the inward tubes again at the fitted k. A round-1 tube can then change length or disappear, and its fitted position factor belonged to the old chimney. Pass the round-1 `tubes_mm` (`size_body_from_calibration(..., tubes_mm=round1.holes.tubes_mm)`) to keep them. `info["warnings"]` lists every silent default: a shape without fitted position factors (psi = 1), a hole whose psi was unresolved, and a voicing hash that was never measured (fallback eta_w).
- **Volume invariant after the Booleans.** The invariant is that the capped air equals `v0_cm3` (printed: `v0_cm3 × volume_factor`). `cavity_volume_for_mesh_cm3` is only the target of the cavity mesh before the holes are cut and the tubes added. Measure the air volume after the Booleans, and compare that with `v0_cm3`.
- **Gate 2 uses the four P0 ladder bodies.** `FitResult.pooled_psi1` covers every body in the fit. To get doc 04's Gate 2 number, fit the four P0 ladder bodies alone.
- **Shape verdict.** `eta_w_by_hash` averages all bodies with one voicing hash, including P1 to P3 that share the P0-80 hash. For the shape verdict, compare the per-body values (`BodyFit.eta_w`, and `eta_w_by_hash[h]["values"]`), and compare the position factors of P1 to P3 against P0.
- **Module names.** `config`, `checks` and `holes` are generic names. If Blender's `sys.path` holds other modules with these names, the import breaks. Put `kernel/` first on `sys.path` for the add-on, or rename on import. `config.ROOT` points at the repository; it breaks if the `kernel/` folder is copied away. In the add-on, pass `params=` explicitly (read from the add-on's own copy of the TOML) and do not rely on the default path.
- **Console.** The command-line tools switch stdout to UTF-8. All files are written as UTF-8. They were tested on the Windows console and in PowerShell, with wildcards expanded by `fit_measurements.py` itself.

### C4b: where the detail is

"Notes for C4b" was the work list. It is done: the record is "C4b evidence" and "Decisions made in C4b" below "Decisions made in C4". Not in C4b, each waiting for the owner: the separate outer body (Q10, through `body.OUTER_MESH_HOOK`), the P4 preset (Q11), a scaled hand template.

### Known limits

- Everything is pre-calibration: eta_w 0.90, k_hole prior 1.0, uniform 4 mm walls, 27 °C internal air.
- The lumped model has no position effect, no finger shading and no pressure-dependent pitch. The fitter measures position as a factor per hole name and shape.
- k_hole has two estimates since C2b (see "k_hole: two estimates"). A single body still gives only the convention value: the end correction of an average hole.
- Hole offset is a single mean. The hole-air and tube-plastic volume terms use the printed (k 0.8) diameters.
- The cavity-mode verdict of the add-on is a desk check with closed holes and a rigid wall (`cavity_mode_computed`). The 1.3 margin is a guess. The Stage 2 spectra are the real test.
- The tube rule lifts the printed bore to the 3 mm floor in 0.5 mm steps, up to 15 mm. It does not check that tubes collide with each other or with the voicing keep-out. That is geometry work for C4.
- The window throat is neck and excluded from V0; a window-throat correction exists for the water fill but no other effect of the 4 mm throat is modelled.
- The kernel's own cavity-mode check uses c/(2L), the lowest estimate. The add-on shows it as `cavity_mode_c2L` (status `info`) and decides with the computed first mode.

### Pending owner decisions (the single list; doc 02 Q1–Q7 and doc 01 §6 point here)

Decided on 2026-11-17 and no longer pending: the ladder (65 / 80 / 95 cm³, P0-88 prediction), the 3 mm window wall as an option, the labium offset default (−0.2 mm, coupons 0 / −0.35), the teardrop tip radius (1.0 mm), the teardrop orientation (broad end at the windway), and holding proposal B.

The current list is the section "Questions for the owner (state after C6)" above. The questions of C2 are answered or carried there (keeping V0 in Stage 3: question 9; the wide-teardrop family and the tip radius: question 8; the cavity mode of P2 and the stub format: answered).

1. **Stage 3 for a known voicing:** keep the printed volume (and accept an A4 error equal to what the measured eta_w says) or retarget V0 so that A4 is on pitch? The code supports both (`retarget_volume`). Round 2 reuses the printed window, so the default is to keep V0.
2. **Wide-teardrop family** (broad ellipse plus 1.0 mm tip, exponent 1/3, owner decision 1 of C2b): is it the shape wanted where the window is wider than long? Since the ladder change this matters only for 95 cm³ on a 4 mm wall (11.1 × 9.65 mm).
3. **Window wall for the ladder:** keep 4 mm everywhere, or build the whole ladder at 3 mm (95 cm³ then stays a teardrop longer than wide)? Do not mix walls inside the ladder (doc 04, "Window wall option").
4. **Rectangle corner radius** (1.0 mm, stub V-b only): fitted to doc 04, never confirmed. (The teardrop tip radius was closed at 1.0 mm.)
5. **Cavity-mode failure of P2 at 80 cm³** is by plan. Does the generator print a waiver note, or does C5 need a `--waive` flag?
6. **P3-80 hole layout** (open problem 8): accept a compressed template, make P3 longer and slimmer, or judge hand comfort on P1 and P2 only.
7. **Stub measurement format** (open problem 4), including the break pressure.
8. **Proposal B, hole undercut** (inner bevel per hole to stay under the pad limits; docs/01 §5.3): **on hold**.
9. **Window throat depth:** add a 5–6 mm window-wall stub to test Heuer's deeper throat, or rely on the 3 / 4 mm pair (docs/01 §5.2).
10. **Windway exit 1.0 mm stub** (optional; Heuer recommends 1.14 mm as the start, the ECAN3 OOT designer moved to 1.0 mm).
11. **Heuer's chart PDF** (he offers it by email): would settle the #3 C wet value (0.428 against 0.403 in). Clay only; printing is not affected.
12. ~~Merging~~: done 2026-11-17 (PR #1 and the working branch merged into `main`).
