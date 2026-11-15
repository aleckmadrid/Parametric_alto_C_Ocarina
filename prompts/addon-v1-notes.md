# Add-on v1 build notes (branch `addon-v1`)

Working notes for the add-on build. This file is the hand-over between sessions. Read it first, then `git log` on `addon-v1`.

All constants in this file are **pre-calibration**. Nothing has been printed or measured. Every synthetic value in the repo is labelled synthetic.

## Status

| Checkpoint | Scope | Status |
| --- | --- | --- |
| C0 | Branch, notes, plan | done (commit `860946f`) |
| C1 | Kernel extensions and sizing CLI | done (commits `9eccda1`, `2f1bdbc`), see evidence below |
| C2 | Measurement fitter and input format | done, see evidence below |
| C3 | Cavity Geometry Nodes | not started, later session |
| C4 | Voicing geometry, holes, wall stack, Booleans | not started, later session |
| C5 | Stage commands | not started, later session |
| C6 | Headless tests, README, final pass | not started, later session |

## Kernel modules (all standard library, no Blender imports)

All modules sit flat in `kernel/` and import each other by plain module name (`import ocarina_kernel as ok`). The tests add `kernel/` to `sys.path`. The add-on must do the same.

| Module | Role | Status |
| --- | --- | --- |
| `ocarina_kernel.py` | Equations, air properties, conductance, fixed-point solver, Monte Carlo. Existing; gets only small additions (k constants). | existing |
| `voicing.py` | Voicing rules: window sizing (teardrop and rounded rectangle), windway numbers, W/h check, version hash. Numbers only, no geometry. | C1 |
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
3. **Teardrop limit.** `teardrop_area` needs width ≤ length. At width = length the shape is a circle, so the teardrop has a maximum area of π(W/2)². Above that area the window becomes a rounded rectangle.
4. **Voicing hash.** It hashes the numbers that define the voicing geometry (window shape and size, windway, labium, wall, offsets, rule version), rounded to 1 µm. It does not hash V0 directly. V0 enters through the solved window area. This way a stub that carries the 80 cm³ window has the same hash as the 80 cm³ body. That is the point of Stage 1.
5. **Inward tubes.** The floor applies to the printed (k 0.8) diameter. A tube is the shortest length, in 0.5 mm steps, that lifts the printed diameter to 3.0 mm. The tube length adds to the chimney. The report gives plain-wall diameters (the doc 04 numbers) and tubed diameters separately. The tube wall displaces a little air, and the report states it.
6. **Fitter.** One body gives η_w·G_w from the all-closed note, then one hole conductance per note pair. Across holes and bodies a single `k_hole` and per-hole position factors ψ are fitted. ψ is normalised to a geometric mean of 1, because k and a uniform ψ cannot be told apart. ψ is shared by hole name between bodies of the same shape.

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
| Switch from teardrop to rounded rectangle | "about 85 cm³" (doc 04) | 88.6 cm³ | The kernel is right for the rule as written. A teardrop at width = length is a circle of 9.65 mm; that circle has 73.1 mm², which needs 88.6 cm³. The doc number was a rough estimate. |
| Window area at 65 and 125 cm³ | 47 and 124 mm² | 46.5 and 123.5 mm² | The doc rounds the area from the rounded width (7.0 and 12.9 mm). The widths agree within 0.05 mm. No action. |
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

- `python -m unittest discover -s kernel -v`: **94 tests, all pass** (9 old, 47 for C1, 38 for C2). Full verbose output was captured in the session; the last lines are `Ran 94 tests in 6.3s` and `OK`.
- Recovery of invented truth within 1 %, **through measurement files** (the test writes the synthetic TOML, loads it, then fits): nine bodies (P0 at 65, 80, 95, 125 cm³; two more P0-80; P1-P3 at 80 cm³), different room temperature per body, tubes at 65 cm³, measured diameters and V0 that differ from the design, per-hole position factors 0.83 to 1.13. On noise-free data eta_w, k_hole and all twelve position factors are recovered to better than 1e-5 relative error (`test_nine_bodies_clean_truth_is_exact`). With 0.04 mm hole scatter, 0.4 % volume scatter and 0.6 % window scatter added, k_hole is within 1 %, eta_w within 1 %, position factors within 3 % (`test_nine_bodies_with_awkward_truth`). A single body recovers everything to 1e-3 (`test_single_body_recovers_everything`).
- Corrected diameters: with the true physics, the diameters the fitter reports put every note above A4 on pitch within 0.02 cent (`test_corrected_diameters_put_every_note_on_pitch`). The Stage 3 loop is closed in the synthetic world: holes sized from fitted constants play within 0.1 cent (`test_stage3_corrected_body_hits_the_scale_in_the_synthetic_world`).
- Blank template: loads as valid TOML, and `load_measurement` raises `MeasurementIncomplete` with a list of 40 missing items.
- The constants file written from synthetic input has `synthetic = true` and a banner, and the reader keeps the flag (tests `test_synthetic_label_is_carried_to_the_file`, `test_repo_synthetic_files_are_labelled_and_load`).

### Noise study (SYNTHETIC data; `python kernel/noise_study.py --runs 30`)

Invented truth: eta_w 0.86, k_hole 1.07, position factors 0.83 to 1.13 with geometric mean 1. Noise is added **per take**, then the takes are averaged. Errors are relative to the truth, in percent. 30 runs per row, seed 11.

| Case | noise per take | takes | eta_w·G_w err % (med / p95) | k_hole err % (med / p95) | psi err % all holes (med / p95) | psi err % sub1, sub2, R_middle (med / p95) | unresolved holes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| one body | none | 3 | 0.000 / 0.000 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0 |
| one body | ±1 cents uniform | 3 | 0.024 / 0.058 | 0.06 / 0.17 | 0.23 / 0.72 | 0.24 / 0.95 | 0 |
| one body | ±2 cents uniform | 3 | 0.048 / 0.116 | 0.12 / 0.34 | 0.46 / 1.43 | 0.48 / 1.91 | 0 |
| one body | ±5 cents uniform | 3 | 0.120 / 0.290 | 0.30 / 0.81 | 1.13 / 3.57 | 1.20 / 4.78 | 0 |
| one body | ±5 cents uniform | 1 | 0.271 / 0.553 | 0.39 / 1.49 | 2.03 / 6.26 | 3.01 / 7.79 | 0 |
| one body | σ 5 cents | 3 | 0.273 / 0.554 | 0.50 / 1.40 | 1.86 / 6.83 | 2.46 / 8.03 | 0 |
| one body | ±10 cents uniform | 3 | 0.241 / 0.580 | 0.64 / 1.57 | 2.25 / 7.18 | 2.40 / 9.58 | 0 |
| nine bodies | none | 3 | 0.000 / 0.000 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0 |
| nine bodies | ±1 cents uniform | 3 | 0.012 / 0.029 | 0.03 / 0.07 | 0.09 / 0.32 | 0.13 / 0.41 | 0 |
| nine bodies | ±2 cents uniform | 3 | 0.024 / 0.058 | 0.05 / 0.15 | 0.19 / 0.63 | 0.26 / 0.83 | 0 |
| nine bodies | ±5 cents uniform | 3 | 0.060 / 0.146 | 0.24 / 0.56 | 0.61 / 1.90 | 0.84 / 2.44 | 0 |
| nine bodies | ±5 cents uniform | 1 | 0.112 / 0.236 | 0.32 / 0.66 | 0.85 / 2.75 | 1.00 / 3.58 | 0 |
| nine bodies | σ 5 cents | 3 | 0.114 / 0.247 | 0.42 / 0.83 | 0.86 / 3.15 | 1.02 / 3.67 | 0 |
| nine bodies | ±10 cents uniform | 3 | 0.120 / 0.291 | 0.58 / 1.40 | 1.41 / 4.45 | 1.82 / 5.95 | 0 |

How to read it. The error of eta_w·G_w stays under 0.3 % (95th percentile) at ±5 cents and under 0.6 % at ±10 cents, because the all-closed note has the whole window weight. The error of k_hole and of the position factors grows about linearly with the noise. At ±5 cents (the acceptance case), one body with 3 takes gives k_hole within 0.8 % (95th percentile) and position factors within 1.1 % (median) and 3.6 % (95th percentile). The three small holes (sub1, sub2, R_middle) are worse, up to 4.8 %. One take instead of three costs a factor of about 2 for the position factors. Nine bodies cut the position-factor errors by a factor of about 2 and the eta_w errors by about 2. They improve k_hole by only about 20 to 30 %. No hole was unresolved in any run. The noise is Gaussian with σ 5 cents in the "σ" rows and uniform ±5 cents in the others.

**k and psi convention (important).** k_hole and an overall scale of the position factors cannot be separated. The fitter fixes the scale: the geometric mean of the position factors over the holes of the reference shape (P0) is 1. The recovery numbers above hold when the truth obeys that rule. If it does not, k_hole absorbs the difference: a uniform 5 % error in psi gives a −7.9 % error in k_hole, and 10 % gives −15 % (a test, `test_k_absorbs_a_psi_scale_that_breaks_the_convention`, records this). eta_w is not affected. The ratios between position factors survive. For design use this is harmless, because k_hole and psi are applied together; but the number `k_hole` is "the end correction of an average hole", not a clean physical constant. Quote it that way.

**Gate 2 numbers.** With psi free, one body has 13 pitches and 13 unknowns, so its residual is zero. The honest numbers are `FitResult.pooled_psi1` (one eta_w per voicing hash, one k_hole, psi = 1, all bodies together) and `BodyFit.rms_shared_psi_cents` (shared psi, the body's own eta_w: shows whether bodies of one shape agree). On the synthetic set the pooled psi = 1 residual is 21.9 cents rms, which comes from the invented position factors (±15 %). The Gate 2 limit of 30 cents rms would pass on this synthetic set.

## Decisions made in C2

- **File format: TOML**, one file per body. A TOML file is easy to fill by hand and `tomllib` reads it with no extra package. The generator writes the template with design numbers filled in (hash, window area, chimney and design diameter per hole, target pitch per note). The person types only the measured values: `water_net_mass_g`, `water_temp_c`, `room_temp_c`, `d_measured_mm` per hole, `hz` (or `cents`) and `p_pa` per note, three takes each.
- **Water fill.** The input is net mass and water temperature. The loader converts it to V0 with the density of water (Tanaka formula). The kernel's V0 holds every hole chimney but not the window throat and not the windway. Two yes/no lines in `[fill]` say whether water also filled them; the loader then subtracts their volume (the file carries the window throat volume; the windway volume is typed in).
- **Hole offset** is one number, the mean of (measured − design) over all holes and bodies. `d_cad_needed_mm` = needed physical size − offset.
- **Corrected diameters** are physical sizes for the body as built, using the body's own eta_w·G_w and measured V0, and the shared position factors. A positive `ream_mm` means ream open. A negative value means the hole is already too big and cannot be fixed (flag `too_big_cannot_ream`). A flag `above_pad_limit` marks a needed size over 10 mm (finger) or 12 mm (thumb). The all-closed note (A4) is reported separately as `a4_error_cents`; holes cannot fix it.
- **Position factors are shared by shape.** Bodies of one shape share one psi per hole name. The reference shape (default: the shape with most bodies) fixes the scale. A whole-scale offset of P1-P3 against P0 shows as a difference in eta_w among bodies with the same voicing hash, and as a pattern in their psi.
- **Weights.** The relative error of each hole conductance comes from the spread of the takes (standard error of the mean, floor 1 cent, 5 cents when there is a single take). The ln-conductance of each hole is weighted by its inverse variance. The correlation between neighbouring holes is ignored.
- **Unresolved holes.** If the conductance of a hole comes out at or below zero, the hole is flagged `unresolved` and left out of the fit. The fit does not fail.
- **Temperature.** The fitter and the sizing use one rule: `ocarina_kernel.internal_air_temp_c(room_c)`. The constants file records the rule. A wrong room temperature moves eta_w: 10 °C of room error is about 1 %.
- **Breath curve.** p0 and alpha come from a least-squares line of ln p against semitones. The pitch is not corrected for blowing pressure.
- **Stage 1 stubs.** A stub has no holes. `voicing.stub_pitch_hz()` predicts its pitch, and `fitter.eta_w_from_stub()` returns eta_w from one measured pitch. No file format for stubs exists yet (open question 4).

## Open problems and decisions log

1. Doc 04 says the switch is at about 85 cm³. The kernel gives 88.6. Nobody has to act, but doc 04 could be corrected by its owner.
2. Pad-limit failures at the largest ladder steps are expected by the plan (doc 04: "the real limit is unknown"). The check reports them; the generator in C5 must not refuse to build because of them.
3. The 1.0 mm tip radius and 1.0 mm corner radius were found by fitting doc 04's table, not from a source. They are in the TOML. If the window geometry in C4 looks wrong, check these first.
4. No measurement format exists for Stage 1 stubs. Add one when the stub is printed (fields: stub id, hash, water-fill mass, room temperature, 3 pitches). `eta_w_from_stub()` is ready.
5. Hole offset is one global number. FDM probably shrinks small holes more than large ones. The data from Stage 2 will show it; a size-dependent offset is a later change.
6. The convention for k_hole and psi (see the C2 evidence) makes k_hole the end correction of an average hole. A later session may prefer to fit k_hole from a single reference hole with a known psi, for example with a coupon.


## Handoff for the C3 session

Read this section first. Everything is standard-library Python 3.12 in `kernel/`, tested with `python -m unittest discover -s kernel -v` (94 tests). Put `kernel/` on `sys.path`, then import by plain module name. No Blender imports exist or are needed.

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
Numbers only, in mm and degrees: `shape` ("teardrop" or "rounded_rectangle"), `window_length_mm` (9.65 medium), `window_width_mm` (broad end of the teardrop, or full width of the rectangle), `window_area_mm2`, `tip_radius_mm` (1.0, teardrop) or `corner_radius_mm` (1.0, rectangle), `wall_at_window_mm`, windway (`windway_exit_height_mm` 1.2, `windway_inlet_height_mm` 1.56, `windway_width_mm` = window broad end, `windway_length_mm` 30), `labium_ramp_angle_deg` 20, `labium_edge_thickness_mm` 0.4, `labium_offset_mm`, `keepout_inside_mm` 10, `keepout_outside_flare_deg` 45, `wh_ratio`, `version_hash`. Teardrop: broad end at the windway, narrow end (tip radius) at the labium. Rectangle: corners rounded with `corner_radius_mm`.
`shape="rounded_rectangle"` forces a rectangle of the same area (stub V-b). `window_area_mm2=` fixes the area instead of solving it from V0.
Stub recipes (Stage 1): V-a = `make_voicing(80)`; V-b = `make_voicing(80, shape="rounded_rectangle")`; V-c = `make_voicing(125)`; V-d = `make_voicing(65)`; V-a± = `make_voicing(80, labium_offset_mm=±0.2)`. `voicing.stub_pitch_hz(v, stub_volume_cm3)` predicts the stub pitch.
`voicing.voicing_hash(values)` hashes the geometry numbers (1 µm), so the same window gives the same hash on any chamber.

**Holes (lower level):** `holes.size_holes(f_targets, X_w, V0, specs, ks, c, ...)`, `holes.solve_scale`, `holes.predict_scale`, `holes.plan_tubes`, `holes.hole_specs_from_params(params)`. SI units (m, m³, Hz).
**Checks:** `checks.range_ratio_check(sum_G, G_w_eff, limit)`, `checks.cavity_mode_check(L_int_m, f_top, c)`, `checks.ellipsoid_length_m(v_m3, r_length, r_width)`, `checks.hole_limit_check`, `checks.wh_ratio_check`.
**Measurements:** `measurements.template_from_sizing(body_sizing, body_id, shape)` then `measurements.write_measurement_file(path, m, blank=True)` writes the template for a generated body with the design numbers pre-filled. `measurements.load_measurement(path)` reads a filled file.
**Fitter:** `fitter.fit_bodies(bodies, params, share="shape", reference_shape=None)`, `fitter.fit_body(body, params)`, `fitter.format_report(fit)`, `fitter.eta_w_from_stub(...)`.
**Constants:** `calibration.calibration_from_fit(fit, bodies, params)`, `calibration.write_calibration(path, cal)`, `calibration.load_calibration(path)`, `calibration.size_body_from_calibration(cal, v0_cm3, rating, ..., shape="P0", retarget_volume=False)` which returns `(BodySizing, info)`. For a voicing hash that was printed, the window is kept and eta_w is the measured value. For an unknown hash (P0 at 110 cm³) the window is solved with `eta_w_fallback`.

### What C3 to C6 must do with it

- Call `size_body(v0, rating)` with the V0 of the step. Build the cavity mesh to `cavity_volume_for_mesh_cm3`, not to `v0_cm3`. Cut each hole at `holes.solutions["print"][i].d_mm` (first print) and add an inward tube of `tube_mm` where it is above 0. Tube wall: `[hole_rules] tube_wall_mm`.
- For P1 to P3, pass `L_int_mm` (the real internal length) to `size_body`. The default is the P0 egg length, and the result records it in `L_int_source`.
- The pre-export checks in doc 02 map to: `checks` (range ratio, cavity mode, W/h, hole limits), the mesh volume against `cavity_volume_for_mesh_cm3` (0.5 %), and `voicing.version_hash`.
- Expected failing checks, not bugs: `hole_limits[nominal]` at 65 cm³ and above (L_index and E6 thumb exceed 10 and 12 mm at k 1.0); `hole_limits[print]` from 80 cm³ up (the print diameters of L_index and the thumbs exceed the pad limits); `cavity_mode` for P2 at 80 cm³ (0.987 × F6, status fail) and P1 at 125 cm³; `needs_fem` for P1 at 80 cm³ (1.12 × F6). Do not stop the build on these; print them in the sizing report.

### Known limits

- Everything is pre-calibration: eta_w 0.90, k_hole prior 1.0, uniform 4 mm walls, 27 °C internal air.
- The lumped model has no position effect, no finger shading and no pressure-dependent pitch. The fitter measures position as a factor per hole name and shape.
- k_hole is the end correction of an average hole (see the C2 evidence).
- Hole offset is a single mean. The hole-air and tube-plastic volume terms use the printed (k 0.8) diameters.
- The tube rule lifts the printed bore to the 3 mm floor in 0.5 mm steps, up to 15 mm. It does not check that tubes collide with each other or with the voicing keep-out. That is geometry work for C4.
- The window throat is neck and excluded from V0; a window-throat correction exists for the water fill but no other effect of the 4 mm throat is modelled.
- The cavity-mode check uses c/(2L), the conservative estimate.

### Open questions for the owner

1. **Stage 3 for a known voicing:** keep the printed volume (and accept an A4 error equal to what the measured eta_w says) or retarget V0 so that A4 is on pitch? The code supports both (`retarget_volume`). Round 2 reuses the printed window, so the default is to keep V0.
2. **Doc 04 says the teardrop runs out at about 85 cm³; the kernel gives 88.6 cm³.** The kernel is right for the stated rule. Does the owner want a stricter rule (for example a teardrop never wider than 0.9 × its length)?
3. **Window tip and corner radius (1.0 mm each)** were fitted to doc 04. Confirm them against the Miracle reference or a drawing.
4. **Cavity-mode failure of P2 at 80 cm³** is by plan. Does the generator print a waiver note, or does C5 need a `--waive` flag?
5. **Stub measurement format** (open problem 4).
