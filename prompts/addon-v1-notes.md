# Add-on v1 build notes (branch `addon-v1`)

Working notes for the add-on build. This file is the hand-over between sessions. Read it first, then `git log` on `addon-v1`.

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
| C5 | Stage commands and Markdown sizing report | done (commit `751d8fd`), see "C5 evidence". Stage 1 and Stage 2 generate with no unexpected failure. Stage 3 runs from the synthetic constants and reports one real conflict (open problem 19) |
| C6 | Headless tests, README, packing of the extension, final pass | done (commit `6da438b`), see "C6 evidence and final pass" |

**Owner decisions of 2026-11-15 (after doc 06).** (1) C4b builds the rules of doc 06 §5–6: subholes 9.5 mm from L ring and 7.5 mm from R middle along each hand line's normal, the revised `ergo_*` checks, parent search over both hands; Q8 answered (L ring), Q12 answered (P0 keeps the taped layout, labelled). (2) Q9/A12: the add-on's cavity-mode verdict comes from the computed first mode of the capped air mesh (`tools/cavity_modes_fd.py` method): ok ≥ 1.3 × F6, needs_fem 1.0–1.3, fail < 1.0; the kernel's c/(2L) check stays unchanged as a reported number. (3) Short decks (P3) overlap the hands along their lines and keep the finger pitch (doc 06 §3.5); open problem 8 then becomes warnings. (4) The next run does C4b, C5 and C6 in that order. Still open: Q10/Q11 (outer body, P4) after a hand check on a printed P2.

**Next concrete step (for the owner, then the next session).** All checkpoints C0 to C6 are done. Nothing has been printed. Before Stage 2 is printed the owner answers the questions under "Questions for the owner" (items 1 and 2 change the hole layout, which is frozen by the first print). Stage 1 can be printed now: it has no holes. A next session starts with `python tools/run_tests.py` (all four suites) and then acts on the answers.

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
| `voicing_geo.py` | Voicing solids from the `Voicing` record: block, pocket, window with labium ramp, windway. | numpy only |
| `body.py` | The build: wall stack, Booleans with assertions, capped air, export. | yes |
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

### Windway width at the top of the ladder (owner decision pending; recorded, not changed)

| P0 body | Window and windway width | Mouthpiece stub width | Body width | Nearest hole edge to the labium ramp | Nearest hole edge to the voicing block | Plastic under the windway floor at the exit | Free depth below the window |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 95 cm³ | 11.10 mm | 19.1 mm | 56.6 mm | 22.7 mm | 21.4 mm | 2.02 mm | 35.0 mm |
| 110 cm³ | 14.66 mm | 22.7 mm | 59.3 mm | 23.4 mm | 21.4 mm | 1.86 mm | 36.6 mm |
| 125 cm³ | 18.57 mm | 26.6 mm | 61.9 mm | 23.9 mm | 21.3 mm | 1.75 mm | 38.1 mm |

The widest teardrop windways fit the P0 body and both keep-outs at 110 and 125 cm³. No sample point within 10 mm of the labium is plastic, and nothing stands above the 45° flare. The mouthpiece stub at 125 cm³ is 26.6 mm wide, which is wide for the lips; that is a comfort question for the owner, not a geometry failure. Renders: `addon_renders/P0-110/` and `addon_renders/P0-125/` (`voicing.png`, `section_window_plan.png`).

## Decisions made in C4

- **Voicing frame.** The voicing is built in its own frame and placed at the port. The origin is the labium point (the far end of the window on the centre line) in the inner plane. x runs along the jet, y across, z outward. The inner plane sits 0.05 mm outside the cavity surface at the port, so the flat plane and the curved cavity never touch.
- **Voicing pocket.** The cavity is curved and the voicing needs a flat inner face, so that the window throat is exactly 4.0 mm deep on every body with the same hash. A flat-topped air pocket fills the gap between the inner plane and the curved cavity under the window and 3 mm around its labium half. It adds 0.13 to 0.24 cm³ of air. The loft is made smaller by that amount, so that loft plus pocket equals `cavity_volume_for_mesh_cm3`. The kernel's "cavity mesh" is therefore the loft joined with the pocket.
- **Windway.** A tapered slot, 30 mm long, as wide as the broad end of the window. The taper is symmetric about the centre line. The floor ends at the exit plane (a straight edge, 0.05 mm before it). The roof ends on the rounded broad end of the window, so the slot runs on under the roof to the widest point of the window. The windway and the window sit in a block with a flat outer face (the voicing patch, 4.0 mm). The block is also the mouthpiece stub: 4 mm of plastic beside the windway, 3.2 mm above, 2.4 mm below at the mouth end.
- **Labium.** The edge is a 0.4 mm land at the inner plane. Above it the wall is cut back at 20° from the outline, outward, around the labium half of the window. The ramp has its full angle where the outline normal is within 60° of the jet and fades to nothing at the widest points. **Labium offset convention:** the mid-height of the edge is `labium_offset_mm` above the windway centre line. The owner can flip the sign in `voicing_geo.windway_centre_z`.
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

## Questions for the owner (state after C6)

Before Stage 2 is printed (the first print freezes the layout, doc 04 D10):

1. **Scale the hand template, and on which surface do the hand checks measure?** (Open problem 15.) On the cavity surface the left hand span is 48.9 mm on P1 and P2 and 49.4 mm on P3 (ok range 50–60); at the outer skin, where the fingers are, it is 52.3, 52.2 and 51.5 mm. The checks use the cavity surface, as doc 06 did. Assumption made: nothing was scaled and nothing was tuned.
2. **The left subhole slide and round 2.** (Open problem 19.) 9.5 mm gives a 3.63 mm edge gap now and 3.05 mm at the k_hole 1.0 diameters. Lengthen the slide in round 1 (about 9.9 mm), accept a smaller gap in round 2, or let the subhole move in round 2? Assumption made: 9.5 mm as decided; Stage 3 reports the failure.
3. **P3 hand overlap: 12 mm (built) or 6 mm?** (Open problem 16.) Both reports are in `addon_checks/`.
4. **The 35 % sideways limit** pulls the index holes toward the deck line and shortens the middle-to-index distance (P2 16.4 mm, P3 16.3 mm). Keep it? (Open problem 17.) Assumption made: kept, as in C4.
5. **`hole_lean_side_away_max_deg = 5`** is my number; doc 06 gives none. (Open problem 18.)

After a hand check on a printed P2, or later:

6. The separate outer body and the P4 body (doc 02 Q10, Q11). Not built; P4 is not in Stage 2.
7. Which finger closes the left subhole (doc 02 Q8, the part that needs a print).
8. The window tip radius (1.0 mm) and the wide-teardrop family (open problems 3 and 11).
9. Stage 3 keeps the printed V0 by default (`--retarget-volume` is the other choice). With the synthetic constants this gives an A4 error of −38 to −41 cents.
10. The wording of the criterion "position factors within 1 % with ±5-cent noise".
11. The licence. The manifest says GPL-3.0-or-later; the repository has no licence file. None was added.

Things I did not do because they need a go-ahead:

12. **Pushing to GitHub and merging `addon-v1` into another branch.** Everything is committed locally on `addon-v1`.
13. **Edits in `docs/` beyond the approved ones.** These places still state a superseded rule or an old number: doc 03 §8 (the "Under review" paragraph about the 124 mm stop); doc 04's shape table (P2 "at the cavity-mode limit (c/2L ≈ F6)") and its D9 row and "Before printing" list (they name the doc 05 checks); doc 02 Phase 4 step 9 (`hand tilt`, `hole tilt`) and its repository map (no doc 06, no add-on, no tests); doc 04's filament masses (the generated bodies are about a quarter lighter, open problem 20); doc 06 §5 gives no number for "leans away".

## Open problems and decisions log

1. Closed in C2b. Doc 04 now says 88.6 cm³ and describes the teardrop that is wider than long.
2. Pad-limit failures at the largest ladder steps are expected by the plan (doc 04: "the real limit is unknown"). The check reports them; the generator in C5 must not refuse to build because of them.
3. The 1.0 mm tip radius was found by fitting doc 04's table, not from a source (owner decision pending). The Miracle window is much blunter at its narrow end: 4.8 mm wide at 1.5 mm from the tip, where a 1.0 mm tip radius gives about 2.5 mm. The 1.0 mm corner radius of the forced rectangle has the same origin. Both are in the TOML. If the window geometry in C4 looks wrong, check these first.
4. Closed in C5. The stub measurement file exists (`measurements.stub_template`, `write_stub_file`, `load_stub`; schema `ocarina-stub-measurement-v1`): stub id, hash, water fill, room temperature, three takes of the pitch, and the two yes/no answers of Gate 1. Stage 1 writes a blank one per stub. `tools/stub_eta_w.py` prints η_w from filled files.
5. Hole offset is one global number. FDM probably shrinks small holes more than large ones. The data from Stage 2 will show it; a size-dependent offset is a later change.
6. Changed in C2b: the profile estimate of k_hole does not need the convention. It needs bodies of one shape with different hole diameters, and it assumes that one psi per hole name holds over the whole P0 ladder. If psi changes with volume, the profile estimate absorbs that change. The data can show it: the reduced chi-square of the profile (`chi2_min / dof`) is then well above 1 and the interval widens.
8. Closed in C4b. P3 at 80 cm³ is too short for the Miracle hand span. Its two hands now overlap by 12 mm each along their own lines (preset value `hand_overlap_mm`), the finger pitch is not compressed, and P3-80 builds with no unexpected failure. What is still missing shows as warnings (see "C4b evidence" and open problem 16).
9. **The bore wall is a little longer than the axis chimney on a curved wall.** The kernel's chimney is the wall along the hole axis (4.000 mm, measured). The mean length of the cut bore wall is up to 0.09 mm longer (P1-80, large holes near the ends), because both wall surfaces curve away from the hole. The reports list both numbers. The fitter measures the effective conductance, so this goes into the position factors.
10. **No flat land around the hole exits.** `hole_flat_land_d` (doc 02, "hole land") is not built and not checked. The test bodies are taped, not fingered. A later session can add a flat patch per hole.
11. **Window tip radius (owner decision pending).** The renders show the 1.0 mm tip as a narrow nose at 65 and 80 cm³ and as a small nose on a wide oval at 95 to 125 cm³ (`addon_renders/P0-*/voicing.png`, `section_window_plan.png`). The Miracle window is much blunter at its narrow end. Nothing was changed.
12. **The mouthpiece stub is a plain box**, 7 mm thick and (window width + 8 mm) wide, with square edges. It points toward the player and 34° up from the plane of the body. Shaping it for the lips is later work.
13. Closed in C4b (was: the hand-ergonomics review of [docs/05](../docs/05-ergonomics.md)). The subholes sit a forward slide from L ring and R middle, the soft `ergo_*` checks exist, and P0 is labelled. What the checks still report on P1–P3 is in "C4b evidence". Open with the owner: the separate outer body and the P4 body (doc 02 Q10, Q11), after a hand check on a printed P2.
14. Closed in C4b (was: the P2 layout slide and [docs/06](../docs/06-ergonomics-challenge.md)). The P2 preset has `layout_centre_from_port_mm = 23`. The rules of doc 06 §5–6 are built.
15. **Which surface do the hand checks measure? (owner question, C4b.)** The `ergo_*` checks use the hole centres on the cavity surface, as doc 06 did for the add-on bodies. The fingers touch the outer skin, 4 mm further out along each hole axis, and the axes spread outward. There the same holes are further apart: the left hand span is 52.3 mm on P1-80 (48.9 mm on the cavity surface), the subholes are 10.5–10.7 mm and 8.2–8.6 mm from their parents (9.5 and 7.5 mm), and no finger pitch is under 16.5 mm on P1 and P2. The Miracle template was wrapped onto the cavity surface, but its millimetres were measured on the outside of that instrument. Every report gives both numbers. If the owner chooses the outer skin, the span warnings of P1 and P2 go away without a scaled template, and the subhole slides should then be set at the outer skin too (9.5 mm there needs about 8.5 mm on the cavity surface, which is under the 3.4 mm edge gap; the gap rule would then also have to move to the outer skin, where the Miracle's 3.4 mm was measured).
16. **P3 hand overlap: 12 mm or 6 mm (C4b; the preset has 12).** With no overlap the right pinky hole does not fit on the deck. From 8 to 11 mm the right subhole and the L index hole (10.8 mm) are closer than the 3.4 mm edge gap after the allowed moves. 6 mm and 12 mm pass every hard check. 12 mm gives 10.0 / 7.8 mm of land past the pinky holes and pinky leans of 23° / 31°, and costs two more warnings by small amounts (`ergo_hand_offset` 17.5 mm against 18; `ergo_index_meet` −23.3 mm along against −22). 6 mm gives 4.7 / 3.4 mm of land and leans of 35° / 52°. Reports: `addon_checks/P3-80.md` (12 mm) and `addon_checks/P3-80-ov6.md`; pictures in `addon_renders/P3-80/` and `addon_renders/P3-80-ov6/`. At 12 mm the L index hole moved 1.31 mm along its row to keep the gap to sub2 (3.41 mm).
17. **The sideways limit shortens one finger pitch (C4b; reported, not changed).** `holes_layout` keeps a finger hole within 35 % of the half section from the deck line. On narrow sections this pulls the index holes toward the deck line: P1 R index −12.1 → −10.2 mm and L index +11.4 → +10.7; P2 −12.1 → −8.7 and +11.4 → +9.5; P3 −15.4 → −11.2 and +14.8 → +11.0. The middle-to-index distance then drops (P2 16.4 mm, P3 16.3 mm on the cavity surface: `ergo_finger_pitch` warns), and the two hand lines come closer (P2 18.7 mm, P3 17.5 mm). The limit existed in C4; since C4b each use is in the layout messages and in `hole_layout`. Raising the limit would move the index holes onto steeper deck; that is a layout change for the owner to decide before Stage 2.
18. **`hole_lean_side_away_max_deg = 5` is the session's number, not the owner's.** Doc 06 §5 says "warn if it leans away" from the covering hand and gives no tolerance. The references lean away by 0.5° at most. With 5°, `ergo_hole_lean_side` warns on the R pinky of P1 (13° away) and P2 (7° away). The value is in `[ergonomics]` of the parameter file.
19. **Round 2 at frozen positions breaks the 3.4 mm edge gap (C5; owner decision needed before the layout freeze).** Doc 04 D10 freezes the hole positions after round 1. The left subhole slides 9.5 mm from L_ring (D5). At the round-1 (k_hole 0.8) diameters the edge gap is 3.63 mm. At the k_hole 1.0 diameters it is 3.05 mm (L_ring 8.39 → 9.35 mm, sub1 3.34 → 3.56 mm), under the 3.4 mm limit. So any round-2 correction toward k_hole 1.0 fails `hole_spacing` on P1, P2 and P3. With the synthetic constants (k_hole 1.13) Stage 3 reports 2.80 mm (P1), 2.56 mm (P2) and 2.70 mm (P3, sub2 to L_index). The build is correct; the rules conflict. Choices: (a) size the round-1 slide for the k_hole 1.0 diameters (about 9.9 mm on P1 and P2; still inside the 9–10.5 mm acceptance and the 11 mm limit), (b) accept a smaller edge gap in round 2, (c) let a subhole move in round 2 (against D10). The P0 bodies are not affected (their smallest gap is 4.0 mm or more). `holes_layout.with_rows` is the code that keeps the positions; `tests/test_holes_layout.py` has a test that states the 3.05 mm number.
20. **The generated bodies are lighter than the doc 04 budget (C5; a finding, nothing to fix).** Solid PLA at 1.24 g/cm³ from the STL volumes, with 12 % added for supports: Stage 1 205 g for six stubs (doc 04: 204 g for four, about 100 g more for the two optional ones), Stage 2 598 g (doc 04: 807 g), Stage 3 542 g (doc 04: 741 g). A stub is 30 to 32 g (doc 04: 50 to 54 g), P0-80 is 55 g (84 g). The doc 04 masses were estimates made before any body was built. Doc 04 was not changed.
21. **Stub V-c has 2.95 mm of plastic at its thinnest place** away from the voicing (the other stubs 4.00 mm). The 26.6 mm wide voicing block of the 18.6 mm window meets the small egg at a shallow angle there. The wall check passes (it measures the plain wall, 4.000 mm). Seen in `addon_checks/V-c.md`; not changed.
7. The interval of the profile estimate knows the pitch noise only. Errors in the measured hole diameters (gauge steps of 0.05 mm are 1.7 % of a 3 mm hole) are not in the weights. On the repository's synthetic set the profile estimate is 6 % off with a stated interval of ±4.4 %. A later session can add the diameter uncertainty to the weights of the small holes.


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

**`sizing.size_body(v0_cm3=None, rating=None, wall_at_window_mm=None, labium_offset_mm=0.0, *, params, voicing, eta_w, shape, ks, floor_key, psi, tubes_mm, volume_factor, hole_offset_mm, L_int_mm, internal_temp_c, wall_at_holes_mm) -> BodySizing`**
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

**`voicing.make_voicing(v0_cm3=None, rating=None, wall_at_window_mm=None, labium_offset_mm=0.0, *, eta_w, shape, window_area_mm2, params, ...) -> Voicing`**
Numbers only, in mm and degrees: `shape` ("teardrop" by rule at every volume; "rounded_rectangle" only when forced), `window_length_mm` (9.65 medium), `window_width_mm` (broad end of the teardrop, or full width of the rectangle), `window_area_mm2`, `broad_end_length_mm` (length of the broad end along the jet: equal to the width while it is a circle, shorter when the teardrop is wider than long), `tip_radius_mm` (1.0, teardrop) or `corner_radius_mm` (1.0, rectangle), `wall_at_window_mm`, windway (`windway_exit_height_mm` 1.2, `windway_inlet_height_mm` 1.56, `windway_width_mm` = window broad end, `windway_length_mm` 30), `labium_ramp_angle_deg` 20, `labium_edge_thickness_mm` 0.4, `labium_offset_mm`, `keepout_inside_mm` 10, `keepout_outside_flare_deg` 45, `wh_ratio`, `version_hash`. Teardrop: broad end at the windway, narrow end (tip radius) at the labium. Rectangle: corners rounded with `corner_radius_mm`.
`shape="rounded_rectangle"` forces a rectangle of the same area (stub V-b only; the rule never picks it). `window_area_mm2=` fixes the area instead of solving it from V0. `Voicing.outline_mm()` returns the window outline as a polygon (x from the windway exit to the labium, y across, outward normal angle).
Stub recipes (Stage 1): V-a = `make_voicing(80)`; V-b = `make_voicing(80, shape="rounded_rectangle")`; V-c = `make_voicing(125)` (since C2b a teardrop, 123.5 mm², 18.6 mm wide); V-d = `make_voicing(65)`; V-a± = `make_voicing(80, labium_offset_mm=±0.2)`. `voicing.stub_pitch_hz(v, stub_volume_cm3)` predicts the stub pitch.
`voicing.voicing_hash(values)` hashes the geometry numbers (1 µm), so the same window gives the same hash on any chamber.

**Holes (lower level):** `holes.size_holes(f_targets, X_w, V0, specs, ks, c, ...)`, `holes.solve_scale`, `holes.predict_scale`, `holes.plan_tubes`, `holes.hole_specs_from_params(params)`. SI units (m, m³, Hz).
**Checks:** `checks.range_ratio_check(sum_G, G_w_eff, limit)`, `checks.cavity_mode_check(L_int_m, f_top, c)`, `checks.ellipsoid_length_m(v_m3, r_length, r_width)`, `checks.hole_limit_check`, `checks.wh_ratio_check`.
**Measurements:** `measurements.template_from_sizing(body_sizing, body_id, shape)` then `measurements.write_measurement_file(path, m, blank=True)` writes the template for a generated body with the design numbers pre-filled. `measurements.load_measurement(path)` reads a filled file.
**Fitter:** `fitter.fit_bodies(bodies, params, share="shape", reference_shape=None, k_source="auto")`, `fitter.fit_body(body, params)`, `fitter.format_report(fit)`, `fitter.eta_w_from_stub(...)`. `FitResult.k_hole` is the value in use; `k_hole_source` says which estimate it is; `k_hole_profile` and `k_hole_convention` hold both (see "k_hole: two estimates"). The constants file carries `k_hole_source`, `k_hole_profile`, `k_hole_profile_interval`, `k_hole_convention` and `psi_geomean_reference` in `[acoustics]`.
**Constants:** `calibration.calibration_from_fit(fit, bodies, params)`, `calibration.write_calibration(path, cal)`, `calibration.load_calibration(path)`, `calibration.size_body_from_calibration(cal, v0_cm3, rating, ..., shape="P0", retarget_volume=False)` which returns `(BodySizing, info)`. For a voicing hash that was printed, the window is kept and eta_w is the measured value. For an unknown hash (P0 at 110 cm³) the window is solved with `eta_w_fallback`.

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

### Open questions for the owner

The current list is the section "Questions for the owner (state after C6)" above. The questions of C2 are answered or carried there (keeping V0 in Stage 3: question 9; the wide-teardrop family and the tip radius: question 8; the cavity mode of P2 and the stub format: answered).
