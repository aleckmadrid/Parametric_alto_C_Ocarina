# Add-on v1 build notes (branch `addon-v1`)

Working notes for the add-on build. This file is the hand-over between sessions. Read it first, then `git log` on `addon-v1`.

All constants in this file are **pre-calibration**. Nothing has been printed or measured. Every synthetic value in the repo is labelled synthetic.

## Status

| Checkpoint | Scope | Status |
| --- | --- | --- |
| C0 | Branch, notes, plan | in progress |
| C1 | Kernel extensions and sizing CLI | not started |
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

## Open problems and decisions log

(Filled in as the work goes.)

## Handoff for the C3 session

(Written at the end of C2.)
