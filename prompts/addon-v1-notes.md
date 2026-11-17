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
| Ladder change | Ladder 65 / 80 / 95 cm³ with P0-88 as the prediction body; 125 cm³ and stub V-c dropped; 3 mm window wall option | done, see "Ladder change and window wall option" |
| C5 | Stage commands and Markdown sizing report | not started. Next session. See "Notes for C5 and C6" |
| C6 | Headless tests, README, packing of the extension, final pass | not started. Next session |

**Next concrete step (C5).** Add the stage commands to `ocarina_addon/headless.py`, starting with Stage 2 as a loop over `api.build_body` (it works today for all eight bodies that Stage 2 and the edge cases need). Then give `build_body` an argument for a ready `BodySizing`, for Stage 3. Then build the Stage 1 stubs. Read "Notes for C5 and C6" in the hand-over section first. Before any new work, check that the last checkpoint still passes: `python -m unittest discover -s kernel` (124 tests) and `tools/geometry_check.py -- body P1 80`.

## Add-on modules (`ocarina_addon/`, since C3 and C4)

| Module | Role | Needs Blender |
| --- | --- | --- |
| `blender_manifest.toml`, `__init__.py`, `operators.py` | The extension, its two operators and the bare menu. | yes |
| `headless.py`, `api.py` | Headless entry (`cavity`, `body`) and the Python API. | yes |
| `kernel_bridge.py` | The only place that imports the kernel; finds the parameter file. | no |
| `presets.py`, `presets/cavity_presets.toml` | Cavity presets P0–P3 as numbers. | no |
| `cavity_math.py` | The cavity surface as plain mathematics: points, normals, port frame, arc lengths. | no |
| `cavity_nodes.py`, `cavity.py` | The Geometry Nodes groups built from Python; the cavity object and its mesh. | yes |
| `holes_layout.py` | Hole positions: Miracle template by arc length, the P0 test layout, the edge-gap rule. | no |
| `voicing_geo.py` | Voicing solids from the `Voicing` record: block, pocket, window with labium ramp, windway. | numpy only |
| `body.py` | The build: wall stack, Booleans with assertions, capped air, export. | yes |
| `checks_geo.py` | Measurements on the mesh and the pre-export checks. | yes |
| `meshutil.py`, `export.py` | Mesh arrays, volume, topology, Booleans, column integration, cleanup; STL read and write. | yes (export.py: numpy only) |
| `render.py`, `render_body.py` | Workbench views and section drawings. | yes |

Outside the package: `tools/geometry_check.py` and `tools/geometry_check_body.py` (the check script), `addon_checks/` (its reports), `addon_renders/` (its pictures), `addon_out/` (STL files; ignored by git).

## Kernel modules (all standard library, no Blender imports)

All modules sit flat in `kernel/` and import each other by plain module name (`import ocarina_kernel as ok`). The tests add `kernel/` to `sys.path`. The add-on must do the same.

| Module | Role | Status |
| --- | --- | --- |
| `ocarina_kernel.py` | Equations, air properties, conductance, fixed-point solver, Monte Carlo. Existing; gets only small additions (k constants). | existing |
| `voicing.py` | Voicing rules: window sizing (a teardrop at every volume; a rounded rectangle only when forced), the window outline as a polygon, windway numbers, W/h check, version hash. Numbers only, no mesh. | C1, C2b |
| `holes.py` | Per-hole sizing with chimney-volume fixed point, position factors, inward tubes, k 0.8 and k 1.0 results. | C1 |
| `checks.py` | Range-ratio check and cavity-mode check, each returning a pass/fail result object. | C1 |
| `sizing.py` | Top level `size_body()` that joins voicing, holes and checks; command-line entry that prints the doc 04 table. | C1 |
| `measurements.py` | Reads and writes the hand-filled measurement TOML. Writes the blank template. | C2 |
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

**Result: 7 of 8 bodies have no unexpected failure. P3-80 fails one check that the notes did not expect (`hole_layout`, see open problem 8).**

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
- **Windway.** A tapered slot, 30 mm long, as wide as the broad end of the window. The taper is symmetric about the centre line. The floor ends at the exit plane (a straight edge, 0.05 mm before it). The roof ends on the rounded broad end of the window, so the slot runs on under the roof to the widest point of the window. The windway and the window sit in a block with a flat outer face (the voicing patch, 4.0 mm). The block is also the mouthpiece stub: 4 mm of plastic beside the windway, 3.2 mm above (3.0 mm at the −0.2 mm labium default since 2026-11-17), 2.4 mm below at the mouth end.
- **Labium.** The edge is a 0.4 mm land at the inner plane. Above it the wall is cut back at 20° from the outline, outward, around the labium half of the window. The ramp has its full angle where the outline normal is within 60° of the jet and fades to nothing at the widest points. **Labium offset convention:** the mid-height of the edge is `labium_offset_mm` above (outward of) the windway centre line. **Decided 2026-11-17:** default −0.2 mm (edge below the jet centre, as Heuer sets it), coupons 0 and −0.4 mm, never positive. The test `test_labium_sign_matches_the_addon_geometry` reads `voicing_geo.windway_centre_z` and fails if the sign is flipped. At the default the windway sits 0.2 mm further out: the roof is the window wall minus 1.0 mm at the exit (3.0 mm at 4 mm, 2.0 mm at 3 mm); the thinnest case, 3 mm wall with the −0.4 coupon, leaves 1.8 mm at the exit and 1.62 mm at the inlet, just above the 3-perimeter minimum.
- **Holes.** A 64-sided cutter whose area equals the area of the circle (`mesh_hole_segments`, the kernel's `polygon_circumradius_for_area`). The axis is the cavity normal at the hole centre. An inward tube is a 64-sided cylinder of radius d/2 + 1.2 mm from 2 mm inside the wall to the tube length inside the cavity; the hole is then cut through wall and tube.
- **Hole layout** (`ocarina_addon/holes_layout.py`). P1–P3: the Miracle positions in millimetres (section 4.2), wrapped by arc length along the top or bottom line of the body from the layout centre (16 mm toward the tail from the port station, as on the Miracle) and then around the section. sub1 (sub_L) sits between L_ring and L_middle and sub2 (sub_R) between R_index and R_middle, both 6 mm off the finger line on the far side. P0: a compressed test layout given as fractions of the spine length (`P0_RELATIVE`), so every P0 body has its holes at the same relative places. The smallest edge gap is 4.0 mm or more on every P0 body from 65 to 125 cm³. No centre had to move on any body that was built.
- **Wall stack.** Skin = cavity moved outward by 4.0 mm along the vertex normals. Envelope = skin joined with the voicing block. Body = envelope minus (cavity joined with pocket), plus tubes, minus holes, minus window, minus windway. The finger deck and the thumb area have no separate patch yet: with a uniform 4 mm wall they would be the same surface. `body.OUTER_MESH_HOOK` is the place where a user outer mesh will be joined to the envelope (not built).
- **Capped air.** Two results. (1) An air mesh built beside the body: cavity plus pocket, minus the tubes, plus every hole up to the outer skin. It is exported as `<id>_air_capped.stl`, and with the window throat added as `<id>_air_fem.stl`. (2) A measurement on the final body mesh without any Boolean: the volume that is inside the envelope, outside the plastic and on the cavity side of the window and windway caps, integrated along columns of 0.25 mm (`body.measure_capped_air_cm3`). A Boolean of the envelope with the body fails, because the two share most of their surface; the column method does not mind.
- **Cleanup.** After the last cut, points closer than 1 µm are merged and zero-area triangles are dissolved (up to 10 µm when needed). Nothing is remeshed or smoothed. The result is accepted only if it is manifold and the volume moved by less than 0.05 mm³.
- **Port stations of P2 and P3 moved in C4** (P2 0.28 → 0.30, P3 0.42 → 0.34 of the spine), so that the hand template has about the same usable deck on both sides of the layout centre. The C3 cavity check was run again with the new presets (all 20 cavities pass); the C3 pictures and report in the repository are the new ones.
- **Expected failures** are coded in `checks_geo.expected_failure`: `hole_limits[nominal]` from 65 cm³, `hole_limits[print]` from 80 cm³, `cavity_mode` fail for P2 from 80 cm³ and P1 from 125 cm³, `cavity_mode` needs FEM for P1 from 80 cm³. Everything else counts as unexpected.

## Open problems and decisions log

1. Closed in C2b. Doc 04 now says 88.6 cm³ and describes the teardrop that is wider than long.
2. Pad-limit failures at the largest ladder steps are expected by the plan (doc 04: "the real limit is unknown"). The check reports them; the generator in C5 must not refuse to build because of them.
3. The 1.0 mm tip radius was found by fitting doc 04's table, not from a source (owner decision pending). The Miracle window is much blunter at its narrow end: 4.8 mm wide at 1.5 mm from the tip, where a 1.0 mm tip radius gives about 2.5 mm. The 1.0 mm corner radius of the forced rectangle has the same origin. Both are in the TOML. If the window geometry in C4 looks wrong, check these first.
4. No measurement format exists for Stage 1 stubs. Add one when the stub is printed (fields: stub id, hash, water-fill mass, room temperature, 3 pitches, **break pressure**). `eta_w_from_stub()` is ready. Body files have the optional per-note `p_break_pa` since 2026-11-17 (the fit report prints the lowest note's value).
5. Hole offset is one global number. FDM probably shrinks small holes more than large ones. The data from Stage 2 will show it; a size-dependent offset is a later change.
6. Changed in C2b: the profile estimate of k_hole does not need the convention. It needs bodies of one shape with different hole diameters, and it assumes that one psi per hole name holds over the whole P0 ladder. If psi changes with volume, the profile estimate absorbs that change. The data can show it: the reduced chi-square of the profile (`chi2_min / dof`) is then well above 1 and the interval widens.
8. **P3 at 80 cm³ is too short for the Miracle hand span.** Its deck is usable for 48 to 51 mm on each side of the layout centre, and the template needs 56 mm. The layout compresses the template to 90 % (left hand) and 86 % (right hand), so the finger pitch is about 15 mm instead of 17 mm. The check `hole_layout` fails for it, and this failure is not in the list of expected failures. The owner should decide: accept a compressed template on P3, make P3 longer and slimmer, or judge hand comfort on P1 and P2 only. P2 fits the template without compression, and P1 too.
9. **The bore wall is a little longer than the axis chimney on a curved wall.** The kernel's chimney is the wall along the hole axis (4.000 mm, measured). The mean length of the cut bore wall is up to 0.09 mm longer (P1-80, large holes near the ends), because both wall surfaces curve away from the hole. The reports list both numbers. The fitter measures the effective conductance, so this goes into the position factors.
10. **No flat land around the hole exits.** `hole_flat_land_d` (doc 02, "hole land") is not built and not checked. The test bodies are taped, not fingered. A later session can add a flat patch per hole.
11. **Window tip radius (owner decision pending).** The renders show the 1.0 mm tip as a narrow nose at 65 and 80 cm³ and as a small nose on a wide oval at 95 to 125 cm³ (`addon_renders/P0-*/voicing.png`, `section_window_plan.png`). The Miracle window is much blunter at its narrow end. Nothing was changed. **Evidence added 2026-11-17:** Heuer's Video #8 teaching model has a narrow tip close to the 1.0 mm tip and puts the broad end at the windway (docs/01-source-review.md §5.5). Still the owner's decision.
12. **The mouthpiece stub is a plain box**, 7 mm thick and (window width + 8 mm) wide, with square edges. It points toward the player and 34° up from the plane of the body. Shaping it for the lips is later work.
7. The interval of the profile estimate knows the pitch noise only. Errors in the measured hole diameters (gauge steps of 0.05 mm are 1.7 % of a 3 mm hole) are not in the weights. On the repository's synthetic set the profile estimate is 6 % off with a stated interval of ±4.4 %. A later session can add the diameter uncertainty to the weights of the small holes.

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
Stub recipes (Stage 1): V-a = `make_voicing(80)`; V-b = `make_voicing(80, shape="rounded_rectangle")`; V-c = `make_voicing(125)` (since C2b a teardrop, 123.5 mm², 18.6 mm wide); V-d = `make_voicing(65)`; coupons V-a0 / V-a4 = `make_voicing(80, labium_offset_mm=0.0)` / `(..., -0.4)` (V-a uses the −0.2 default). `voicing.stub_pitch_hz(v, stub_volume_cm3)` predicts the stub pitch.
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
- Expected failing checks, not bugs: `hole_limits[nominal]` at 65 cm³ and above (L_index and E6 thumb exceed 10 and 12 mm at k 1.0); `hole_limits[print]` from 80 cm³ up (the print diameters of L_index and the thumbs exceed the pad limits); `cavity_mode` for P2 at 80 cm³ (0.987 × F6, status fail) and P1 at 125 cm³; `needs_fem` for P1 at 80 cm³ (1.12 × F6). Do not stop the build on these; print them in the sizing report.

### Notes for C5 (Stage 3) and for the report

- **Tubes in Stage 3.** `size_body_from_calibration` plans the inward tubes again at the fitted k. A round-1 tube can then change length or disappear, and its fitted position factor belonged to the old chimney. Pass the round-1 `tubes_mm` (`size_body_from_calibration(..., tubes_mm=round1.holes.tubes_mm)`) to keep them. `info["warnings"]` lists every silent default: a shape without fitted position factors (psi = 1), a hole whose psi was unresolved, and a voicing hash that was never measured (fallback eta_w).
- **Volume invariant after the Booleans.** The invariant is that the capped air equals `v0_cm3` (printed: `v0_cm3 × volume_factor`). `cavity_volume_for_mesh_cm3` is only the target of the cavity mesh before the holes are cut and the tubes added. Measure the air volume after the Booleans, and compare that with `v0_cm3`.
- **Gate 2 uses the four P0 ladder bodies.** `FitResult.pooled_psi1` covers every body in the fit. To get doc 04's Gate 2 number, fit the four P0 ladder bodies alone.
- **Shape verdict.** `eta_w_by_hash` averages all bodies with one voicing hash, including P1 to P3 that share the P0-80 hash. For the shape verdict, compare the per-body values (`BodyFit.eta_w`, and `eta_w_by_hash[h]["values"]`), and compare the position factors of P1 to P3 against P0.
- **Module names.** `config`, `checks` and `holes` are generic names. If Blender's `sys.path` holds other modules with these names, the import breaks. Put `kernel/` first on `sys.path` for the add-on, or rename on import. `config.ROOT` points at the repository; it breaks if the `kernel/` folder is copied away. In the add-on, pass `params=` explicitly (read from the add-on's own copy of the TOML) and do not rely on the default path.
- **Console.** The command-line tools switch stdout to UTF-8. All files are written as UTF-8. They were tested on the Windows console and in PowerShell, with wildcards expanded by `fit_measurements.py` itself.

### Notes for C5 and C6 (written at the end of C4)

What exists. `ocarina_addon/api.py`: `build_body(preset, v0_cm3, rating=None, export_dir=None, renders=False, save_blend=False, hole_key="print", body_id=None)` returns a `BodyResult` with `sizing` (the kernel `BodySizing`), `checks` (list of dicts: name, status, value, limit, message, expected), `measurements`, `booleans`, `files`, and the meshes `solid`, `air_capped`, `air_fem`. `export_cavity(preset, volume_cm3, path)`. `format_summary(body)`. The headless entry is `ocarina_addon/headless.py` with the commands `cavity` and `body`. The operators are `oca.build_cavity` and `oca.build_body` (menu Object > Parametric Ocarina).

What C5 has to add.

1. **Stage commands** in `ocarina_addon/headless.py`: `stage1`, `stage2`, `stage3`. Stage 2 is a loop over `build_body`: P0 at 65, 80 and 95 cm³ (ladder change: no 125 cm³), P1, P2 and P3 at 80 cm³, and two more copies of P0-80 (same geometry; give them `body_id` P0-80-b and P0-80-c). Stage 3 reads a constants file with `k.calibration.size_body_from_calibration`. `build_body` sizes with `k.sizing.size_body` itself today, so it needs a new argument that takes a ready `BodySizing` (and the round-1 `tubes_mm`, see the notes above about tubes in Stage 3). The cut diameters must then come from `cad_diameters_mm` (design diameter minus the hole offset), and the cavity mesh target already includes the volume factor.
2. **Stage 1 stubs** are not built. A stub is a small chamber (about 25 cm³) with the voicing and no holes. `voicing_geo.build(v, port_frame)` already gives the voicing solids for any `Voicing` record, including the forced rounded rectangle of V-b (its ramp is the straight far edge; this path has run only as far as the solids, never through a full build). The stub needs a cavity preset (a short egg works: P0 at 25 cm³; the widest stub window is now V-a, 8.8 mm, since V-c was dropped), the same wall stack without holes, and its own check that the capped volume equals the stub volume. `k.voicing.stub_pitch_hz` predicts the pitch.
3. **The Markdown sizing report** per stage: per body the volume, window, windway, every hole at k 0.8 and k 1.0, chimney and tube lengths, check results and the hash. `tools/geometry_check_body.write_report` already writes most of this per body from the measurements; `k.sizing.format_body` gives the kernel table with both k values. Join the two.
4. **Names in reports.** The reports of the kernel CLI print `sub_L` and `sub_R`. The kernel records, the measurement files, the add-on and the check reports use `sub1` and `sub2`. Pick one in the stage reports and say so in the header (`sizing.LABELS` holds the mapping).
5. **Expected failures.** `checks_geo.expected_failure` holds the rule. The stage commands must not stop on an expected failure and must list it in the report. `headless.py body --strict` exits with code 1 only on an unexpected failure.
6. **P3-80 fails `hole_layout`** (open problem 8). Stage 2 will show this failure until the owner decides.
7. **Blank measurement templates.** `k.measurements.template_from_sizing(body.sizing, body_id, shape)` and `write_measurement_file(path, m, blank=True)` write the template for each generated body. Stage 2 should write one per body next to the STL.

What C6 has to add.

1. **Headless Blender tests.** `tools/geometry_check.py` is the measuring script, not a test suite. C6 should wrap it: a cavity test (the 20 cavities), a body test (at least P1-80 and P0-65), and plain-Python tests for `cavity_math.py`, `holes_layout.py`, `presets.py` and `kernel_bridge.py`, which run without Blender.
2. **Packing the extension.** `kernel_bridge.py` already looks for `ocarina_addon/kernel/` and `ocarina_addon/params/` first. A pack script must copy the kernel modules (not the tests) and `alto_c_12hole.toml` there and zip the folder. `config.ROOT` then points at the wrong place, which does not matter because the add-on always passes `params=`. Installing the zip in Blender 5.1 has not been tried.
3. **README section** on installing, the stage commands and the tests.
4. **The acceptance criterion "position factors within 1 % with ±5-cent noise" of the full prompt cannot pass as written.** The noise study gives 2.5 to 3.6 % at the 95th percentile (1.0 to 1.1 % median). The noise-free 1 % criterion passes. The owner should reword it before C6.
5. **The full prompt still describes the rounded-rectangle window** ("switching to a rounded rectangle when the teardrop would need to be wider than long"). The teardrop-only rule of C2b replaces it, Stub V-c was dropped with the 125 cm³ step (ladder change).
6. The manifest names the licence GPL-3.0-or-later, because Blender add-ons that use `bpy` are distributed under the GPL. The repository has no licence file. The owner should confirm.

### Known limits

- Everything is pre-calibration: eta_w 0.90, k_hole prior 1.0, uniform 4 mm walls, 27 °C internal air.
- The lumped model has no position effect, no finger shading and no pressure-dependent pitch. The fitter measures position as a factor per hole name and shape.
- k_hole has two estimates since C2b (see "k_hole: two estimates"). A single body still gives only the convention value: the end correction of an average hole.
- Hole offset is a single mean. The hole-air and tube-plastic volume terms use the printed (k 0.8) diameters.
- The tube rule lifts the printed bore to the 3 mm floor in 0.5 mm steps, up to 15 mm. It does not check that tubes collide with each other or with the voicing keep-out. That is geometry work for C4.
- The window throat is neck and excluded from V0; a window-throat correction exists for the water fill but no other effect of the 4 mm throat is modelled.
- The cavity-mode check uses c/(2L), the conservative estimate.

### Open questions for the owner

1. **Stage 3 for a known voicing:** keep the printed volume (and accept an A4 error equal to what the measured eta_w says) or retarget V0 so that A4 is on pitch? The code supports both (`retarget_volume`). Round 2 reuses the printed window, so the default is to keep V0.
2. Answered by owner decision 1 (C2b): the window stays a teardrop at every volume and grows wider than long above 88.6 cm³. New question: **is the wide-teardrop family (broad ellipse plus 1.0 mm tip, exponent 1/3) the shape the owner wants?** The renders of P0 at 95, 110 and 125 cm³ show it. A full-length ellipse would be narrower (16.3 mm at 125 cm³) but has no narrow end.
3. **Window tip and corner radius (1.0 mm each)** were fitted to doc 04. Confirm them against the Miracle reference or a drawing.
4. **Cavity-mode failure of P2 at 80 cm³** is by plan. Does the generator print a waiver note, or does C5 need a `--waive` flag?
5. **Stub measurement format** (open problem 4).
