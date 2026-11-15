# Add-on v1 build notes (branch `addon-v1`)

Working notes for the add-on build. This file is the hand-over between sessions. Read it first, then `git log` on `addon-v1`.

All constants in this file are **pre-calibration**. Nothing has been printed or measured. Every synthetic value in the repo is labelled synthetic.

## Status

| Checkpoint | Scope | Status |
| --- | --- | --- |
| C0 | Branch, notes, plan | done (commit `860946f`) |
| C1 | Kernel extensions and sizing CLI | done, see evidence below |
| C2 | Measurement fitter and input format | not started |
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
| `calibration.py` | Reads and writes the fitted-constants TOML that Stage 3 will read. | C2 |

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

## Open problems and decisions log

1. Doc 04 says the switch is at about 85 cm³. The kernel gives 88.6. Nobody has to act, but doc 04 could be corrected by its owner.
2. Pad-limit failures at the largest ladder steps are expected by the plan (doc 04: "the real limit is unknown"). The check reports them; the generator in C5 must not refuse to build because of them.

## Handoff for the C3 session

(Written at the end of C2.)
