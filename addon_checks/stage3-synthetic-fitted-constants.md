# Stage 3 · Round 2 corrected bodies: generation report

> **SYNTHETIC CONSTANTS.** This stage was sized from a fitted-constants file that is marked synthetic: invented truth values, not measurements of printed bodies. The report shows that the Stage 3 generator works. Do not print these bodies.

Written by `ocarina_addon/headless.py -- stage3` on 2026-11-16. Every measured number comes from the STL file of the body, read back from disk. Run time 337 s for 8 bodies.

Result: **5 of 8 bodies have no unexpected failure**; UNEXPECTED FAILURES on P1-80-r2, P2-80-r2, P3-80-r2.

- Sized from the fitted-constants file `calibration/synthetic-fitted-constants.toml`: k_hole 1.1339 (profile estimate), hole offset -0.122 mm (printed minus designed), volume factor 0.9853 (printed / designed), η_w fallback 0.8602; η_w measured for the voicing hashes `6aa0038008cc` 0.8585, `d1b6418b1844` 0.8614, `622bdad5acb2` 0.8604, `f3803f8358b6` 0.8607.
- Bodies that were printed in round 1 keep their window, their volume, their inward tubes and their hole positions (doc 04 D10). Only the hole diameters change. The printed volume is kept (the default), so A4 errs by the amount the measured η_w says; the table gives it.
- Each hole is drawn at its CAD diameter (design diameter minus the hole offset), and the model holds V0 divided by the volume factor, so that the print holds V0.
- P0 at 110 cm³ was never printed: its window, tubes and holes come from the fitted model alone (the prediction test of Gate 3).
- The per-body check reports of this stage are written beside the STL files (not in git), and no pictures are made unless `--renders` is given: the result depends on the constants file.
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).
- The constants of this stage are those of the fitted-constants file named above, not the pre-calibration priors. This command measured nothing on a printed body: every measured number here comes from an STL file.
- Statuses: `pass` (the docs say ok), `FAIL`, `NEEDS FEM` (cavity-mode desk check between its limits), `WARN` (a soft ergonomic check; never a failure), `info` (a reported number).

## Bodies

| Body | Preset | V0 | Voicing hash | Window | Windway exit | Capped air on the STL | First cavity mode (desk check) | Plastic; solid PLA mass | doc 04 mass | Failures | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0-65-r2 | P0 | 65.0 cm³ | `6aa0038008cc` | Teardrop 9.65 × 6.96 mm, 46.5 mm² | 1.20 × 6.96 mm | 66.011 cm³ (+0.015 %) | 2.23 × F6, pass (c/(2L): 1.69) | 39.6 cm³; 49 g | 77 g | hole_limits[fitted] (expected) | 11 (taped test body) |
| P0-80-r2 | P0 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.238 cm³ (+0.017 %) | 2.08 × F6, pass (c/(2L): 1.57) | 44.3 cm³; 55 g | 84 g | hole_limits[fitted] (expected) | 11 (taped test body) |
| P0-95-r2 | P0 | 95.0 cm³ | `622bdad5acb2` | Teardrop 9.65 × 11.10 mm, 81.2 mm² | 1.20 × 11.10 mm | 96.467 cm³ (+0.022 %) | 1.97 × F6, pass (c/(2L): 1.49) | 48.6 cm³; 60 g | 91 g | hole_limits[fitted] (expected) | 11 (taped test body) |
| P0-125-r2 | P0 | 125.0 cm³ | `f3803f8358b6` | Teardrop 9.65 × 18.57 mm, 123.5 mm² | 1.20 × 18.57 mm | 126.927 cm³ (+0.034 %) | 1.80 × F6, pass (c/(2L): 1.36) | 56.6 cm³; 70 g | 108 g | hole_limits[fitted] (expected) | 11 (taped test body) |
| P1-80-r2 | P1 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.245 cm³ (+0.026 %) | 1.62 × F6, pass (c/(2L): 1.13) | 48.9 cm³; 61 g | 91 g | **hole_spacing (unexpected)**, hole_limits[fitted] (expected) | 4 |
| P2-80-r2 | P2 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.241 cm³ (+0.021 %) | 1.39 × F6, pass (c/(2L): 0.99) | 51.6 cm³; 64 g | 97 g | **hole_spacing (unexpected)**, hole_limits[fitted] (expected) | 5 |
| P3-80-r2 | P3 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.223 cm³ (-0.002 %) | 1.75 × F6, pass (c/(2L): 1.32) | 47.5 cm³; 59 g | 91 g | **hole_spacing (unexpected)**, hole_limits[fitted] (expected) | 6 |
| P0-110-r2 | P0 | 110.0 cm³ | `39c00d2765a6` | Teardrop 9.65 × 15.94 mm, 108.7 mm² | 1.20 × 15.94 mm | 111.698 cm³ (+0.030 %) | 1.88 × F6, pass (c/(2L): 1.42) | 52.9 cm³; 66 g | 102 g | hole_limits[fitted] (expected) | 11 (taped test body) |

*Capped air* is compared with the target of the model: V0 for a round-1 body, the stub volume for a stub, and in Stage 3 V0 divided by the fitted volume factor, with the holes drawn at their CAD diameters. *First cavity mode* is the computed desk check with closed holes, which gives the verdict; the number in brackets is the kernel's c/(2L) estimate from the length of the chamber, the lowest estimate, shown for information (it is 30 to 44 % low for these shapes, docs/06 section 3.10). *Solid PLA mass* is the plastic volume of the STL at 1.24 g/cm³, with no supports, brim or infill saving; the doc 04 figure includes about 12 % for supports and a brim.

Total for the 8 bodies of this stage: 484 g of solid PLA, 542 g with 12 % for supports and a brim. The doc 04 budget for this stage is 741 g. The generated bodies are lighter than the budget; the doc 04 masses were estimates made before any body was built.

## Unexpected failures

- **P1-80-r2** `hole_spacing`: smallest edge gap 2.80 mm (sub1 to L_ring); at least 3.4 mm
- **P2-80-r2** `hole_spacing`: smallest edge gap 2.56 mm (sub1 to L_ring); at least 3.4 mm
- **P3-80-r2** `hole_spacing`: smallest edge gap 2.70 mm (sub2 to L_index); at least 3.4 mm

**Why `hole_spacing` fails here.** The hole positions of a printed body are frozen at the round-1 layout (doc 04 D10), and the corrected holes are larger than the round-1 holes. A hole that was just clear of its neighbour in round 1 is then too close. The tightest pair of the hand layout is the left subhole and L_ring: the 9.5 mm slide leaves 3.63 mm between the hole edges at the round-1 (k_hole 0.8) diameters, and 3.05 mm at the k_hole 1.0 diameters, against the limit of 3.4 mm. The build is correct; the rules conflict. The owner has to choose before the layout is frozen: a longer slide in round 1, a smaller edge gap in round 2, or a subhole that may move in round 2 (see the build notes, "Questions for the owner").

## Expected failures

Failures that the plan expects (the pad-limit checks: doc 04 prints these holes on purpose, "the real limit is unknown"). They do not stop a stage.

- P0-65-r2 `hole_limits[fitted]` (fail): L_index 10.05 mm above the 10 mm pad limit; L_thumb 12.94 mm above the 12 mm pad limit
- P0-80-r2 `hole_limits[fitted]` (fail): L_index 11.83 mm above the 10 mm pad limit; L_thumb 15.29 mm above the 12 mm pad limit
- P0-95-r2 `hole_limits[fitted]` (fail): L_ring 10.61 mm above the 10 mm pad limit; L_index 13.58 mm above the 10 mm pad limit; L_thumb 17.59 mm above the 12 mm pad limit
- P0-125-r2 `hole_limits[fitted]` (fail): L_pinky 10.46 mm above the 10 mm pad limit; L_ring 13.22 mm above the 10 mm pad limit; L_index 17.00 mm above the 10 mm pad limit; L_thumb 22.06 mm above the 12 mm pad limit; R_thumb 13.21 mm above the 12 mm pad limit
- P1-80-r2 `hole_limits[fitted]` (fail): L_index 11.74 mm above the 10 mm pad limit; L_thumb 15.32 mm above the 12 mm pad limit
- P2-80-r2 `hole_limits[fitted]` (fail): L_index 12.36 mm above the 10 mm pad limit; L_thumb 15.86 mm above the 12 mm pad limit
- P3-80-r2 `hole_limits[fitted]` (fail): L_index 11.78 mm above the 10 mm pad limit; L_thumb 15.66 mm above the 12 mm pad limit
- P0-110-r2 `hole_limits[fitted]` (fail): L_ring 11.93 mm above the 10 mm pad limit; L_index 15.30 mm above the 10 mm pad limit; L_thumb 19.85 mm above the 12 mm pad limit

### Round-hole verdict (doc 04, Gate 2)

The rule of Gate 2, applied to the holes of this stage: a ladder step fails this verdict if a fitted hole needs more than 10 mm (finger) or 12 mm (thumb).

- P0-65-r2: L_index needs 10.05 mm (limit 10 mm)
- P0-65-r2: L_thumb needs 12.94 mm (limit 12 mm)
- P0-80-r2: L_index needs 11.83 mm (limit 10 mm)
- P0-80-r2: L_thumb needs 15.29 mm (limit 12 mm)
- P0-95-r2: L_ring needs 10.61 mm (limit 10 mm)
- P0-95-r2: L_index needs 13.58 mm (limit 10 mm)
- P0-95-r2: L_thumb needs 17.59 mm (limit 12 mm)
- P0-125-r2: L_pinky needs 10.46 mm (limit 10 mm)
- P0-125-r2: L_ring needs 13.22 mm (limit 10 mm)
- P0-125-r2: L_index needs 17.00 mm (limit 10 mm)
- P0-125-r2: L_thumb needs 22.06 mm (limit 12 mm)
- P0-125-r2: R_thumb needs 13.21 mm (limit 12 mm)
- P1-80-r2: L_index needs 11.74 mm (limit 10 mm)
- P1-80-r2: L_thumb needs 15.32 mm (limit 12 mm)
- P2-80-r2: L_index needs 12.36 mm (limit 10 mm)
- P2-80-r2: L_thumb needs 15.86 mm (limit 12 mm)
- P3-80-r2: L_index needs 11.78 mm (limit 10 mm)
- P3-80-r2: L_thumb needs 15.66 mm (limit 12 mm)
- P0-110-r2: L_ring needs 11.93 mm (limit 10 mm)
- P0-110-r2: L_index needs 15.30 mm (limit 10 mm)
- P0-110-r2: L_thumb needs 19.85 mm (limit 12 mm)

## Warnings

Soft ergonomic checks outside their range. They are measurements for the owner to judge. A warning is never a failure.

- P0-65-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2.md`.
- P0-80-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2.md`.
- P0-95-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2.md`.
- P0-125-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-125-r2/P0-125-r2.md`.
- P1-80-r2 `ergo_hand_span`: hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.2 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.3, right 51.8 mm
- P1-80-r2 `ergo_rest_space`: the bulb end is 4.9 mm too short: 5.1 mm past the L pinky hole edge; the tail end is 5.7 mm too short: 4.3 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 5.1 mm (centre 8.9), tail 4.3 mm (centre 7.0); ok at least 10 mm
- P1-80-r2 `ergo_hole_lean_end`: L_pinky leans 37° toward the bulb end; R_pinky leans 29° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +37°, L_ring +15°, L_middle -0°, L_index -14°, R_pinky +29°, R_ring +15°, R_middle +11°, R_index +5°; ok up to 20°
- P1-80-r2 `ergo_hole_lean_side`: R_pinky leans 12° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -0°, L_ring +0°, L_middle +4°, L_index +17°, R_pinky -12°, R_ring -3°, R_middle +7°, R_index +22°; ok up to 45° toward it and up to 5° away
- P2-80-r2 `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.5 mm. Measured: left 17.1 / 17.6 / 16.5 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.4 / 18.8 / 17.5, right 17.3 / 18.0 / 16.9 mm
- P2-80-r2 `ergo_hand_span`: hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.8 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.2, right 51.0 mm
- P2-80-r2 `ergo_rest_space`: the bulb end is 0.9 mm too short: 9.1 mm past the L pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 9.1 mm (centre 13.0), tail 11.8 mm (centre 14.5); ok at least 10 mm
- P2-80-r2 `ergo_hole_lean_end`: L_pinky leans 29° toward the bulb end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +29°, L_ring +11°, L_middle -6°, L_index -19°, R_pinky +12°, R_ring +8°, R_middle +8°, R_index +9°; ok up to 20°
- P2-80-r2 `ergo_hole_lean_side`: R_pinky leans 7° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +2°, L_ring +1°, L_middle +1°, L_index +12°, R_pinky -7°, R_ring -3°, R_middle +5°, R_index +19°; ok up to 45° toward it and up to 5° away
- P3-80-r2 `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.3 mm. Measured: left 17.0 / 17.4 / 16.3 mm, right 17.1 / 18.1 / 17.1 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.0 / 18.0 / 16.9, right 18.4 / 18.8 / 17.8 mm
- P3-80-r2 `ergo_hand_span`: hand span out of range: left hand 49.4 mm. Measured: left 49.4 mm, right 51.0 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.4, right 53.6 mm
- P3-80-r2 `ergo_hand_offset`: hand lines 17.6 mm apart across. Measured: the right-hand line is 17.6 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +9.5°, right line +14.8° (+ = the tail end of the line is farther from the player)
- P3-80-r2 `ergo_index_meet`: index holes 17.6 mm apart across; R index -23.2 mm along the hand axis from L index. Measured: R index from L index: 17.6 mm across (toward the player), -23.2 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along
- P3-80-r2 `ergo_rest_space`: the bulb end is 0.1 mm too short: 9.9 mm past the L pinky hole edge; the tail end is 2.6 mm too short: 7.4 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 9.9 mm (centre 13.6), tail 7.4 mm (centre 10.1); ok at least 10 mm
- P3-80-r2 `ergo_hole_lean_end`: L_pinky leans 23° toward the bulb end; R_pinky leans 31° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +23°, L_ring +9°, L_middle -0°, L_index -8°, R_pinky +31°, R_ring +11°, R_middle +2°, R_index -8°; ok up to 20°
- P0-110-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-110-r2/P0-110-r2.md`.

## Per body

### P0-65-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `6aa0038008cc`. Window: Teardrop 9.65 × 6.96 mm, 46.5 mm², wall 4.0 mm. Windway: exit 1.20 × 6.96 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 65.00 cm³ (capped air). Measured on the STL: 66.011 cm³ against the model target 66.002 cm³ (+0.015 %). Cavity mesh 64.21 cm³ (1.82 cm³ of air in the holes, 0.09 cm³ of tube wall). Cavity spine length 73.4 mm. Plastic 39.6 cm³.
- Fitted constants: η_w 0.8585 (measured), k_hole 1.1339, position factors of shape `P0`. A4 error with the kept volume: -40.9 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.079 | 0.5 (kept) | 4.5 | 3.56 | **3.68** | 3.08 | +0.48 | 3.679 | 10 | ok |
| sub2 | C5 | 1.004 | 5.0 (kept) | 9.0 | 3.17 | **3.29** | 3.03 | +0.14 | 3.291 | 10 | ok |
| R_pinky | D5 | 0.857 | 0.0 (kept) | 4.0 | 4.52 | **4.64** | 3.64 | +0.87 | 4.637 | 10 | ok |
| R_ring | E5 | 0.916 | 0.0 (kept) | 4.0 | 5.06 | **5.18** | 4.22 | +0.84 | 5.182 | 10 | ok |
| R_middle | F5 | 0.958 | 0.0 (kept) | 4.0 | 3.43 | **3.55** | 3.03 | +0.40 | 3.552 | 10 | ok |
| R_index | G5 | 1.072 | 0.0 (kept) | 4.0 | 5.78 | **5.90** | 5.29 | +0.49 | 5.902 | 10 | ok |
| L_pinky | A5 | 1.181 | 0.0 (kept) | 4.0 | 6.36 | **6.48** | 6.18 | +0.18 | 6.480 | 10 | ok |
| L_ring | B5 | 1.104 | 0.0 (kept) | 4.0 | 7.91 | **8.03** | 7.24 | +0.68 | 8.035 | 10 | ok |
| L_middle | C6 | 1.048 | 0.0 (kept) | 4.0 | 5.58 | **5.70** | 5.05 | +0.53 | 5.698 | 10 | ok |
| L_index | D6 | 1.133 | 0.0 (kept) | 4.0 | 10.05 | **10.17** | 9.22 | +0.82 | 10.167 | 10 | above the pad limit |
| L_thumb | E6 | 1.022 | 0.0 (kept) | 4.0 | 12.94 | **13.06** | 10.87 | +2.07 | 13.062 | 12 | above the pad limit |
| R_thumb | F6 | 1.115 | 0.0 (kept) | 4.0 | 8.00 | **8.12** | 7.39 | +0.61 | 8.119 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.26; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.69 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_index 10.05 mm above the 10 mm pad limit; L_thumb 12.94 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-65-r2_air_capped.stl; holes and window closed): 3111 Hz = 2.23 × F6 on a 1.5 mm grid of 19529 cells (2 mm grid: 3103 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 64.087 + voicing pocket 0.124) = 64.2112 cm³ against the kernel's 64.2111 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 66.0115 cm³ (+0.0146 %), air mesh 66.0095 cm³ (+0.0115 %), against the model target 66.0019 cm³ (V0 65.0000 cm³ in the print, volume factor 0.9853, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 19 Booleans, all manifold, each volume change as expected (largest deviation 12.43 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 6aa0038008cc; recomputed from the record: 6aa0038008cc |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 6.959 mm, 46.47 mm² (record 9.650 × 6.959, 46.47); windway exit 1.200 × 6.959 mm, inlet 1.560 × 6.959 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.48 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 29.5 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.47 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_pinky), largest chimney error -0.0058 mm (sub1); limit 0.05 mm |
| `inward_tubes` | pass | sub1: length 0.500 mm (kernel 0.5), wall 1.198 mm, 30.8 mm to the opposite wall, 30.8 mm to the labium, 23.9 mm to the nearest other tube; sub2: length 5.000 mm (kernel 5.0), wall 1.198 mm, 27.8 mm to the opposite wall, 29.8 mm to the labium, 23.9 mm to the nearest other tube |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.64 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 28.7 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2318 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.81 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 14.2 / 14.6 / 15.5 mm, right 11.1 / 10.7 / 14.0 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 16.0 / 16.0 / 17.2, right 12.6 / 11.8 / 15.3 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 27.2 mm, right 25.3 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 29.8, right 27.6 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -5.4, left middle +8.9, right ring -4.2, right middle +5.9 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 24.6 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 24.7 mm across (toward the player), +0.6 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 8.7 mm, -115° off the normal of the left-hand line (-3.5 mm forward, -7.7 mm toward the index); at the outer skin 9.3 mm; sub2 from R_middle: 7.1 mm, +38° off the normal of the right-hand line (+5.5 mm forward, +4.3 mm toward the index); at the outer skin 7.5 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.8 mm (centre 11.0), tail 8.5 mm (centre 10.9); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +6.7 mm from R middle (ok -8 to +3), L thumb +13.6 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2.md`.

### P0-80-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.238 cm³ against the model target 81.224 cm³ (+0.017 %). Cavity mesh 78.72 cm³ (2.49 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 78.5 mm. Plastic 44.3 cm³.
- Fitted constants: η_w 0.8614 (measured), k_hole 1.1339, position factors of shape `P0`. A4 error with the kept volume: -38.0 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.079 | 0.0 (kept) | 4.0 | 3.90 | **4.02** | 3.34 | +0.56 | 4.023 | 10 | ok |
| sub2 | C5 | 1.004 | 3.0 (kept) | 7.0 | 3.24 | **3.36** | 3.06 | +0.19 | 3.365 | 10 | ok |
| R_pinky | D5 | 0.857 | 0.0 (kept) | 4.0 | 5.23 | **5.35** | 4.16 | +1.06 | 5.348 | 10 | ok |
| R_ring | E5 | 0.916 | 0.0 (kept) | 4.0 | 5.87 | **5.99** | 4.83 | +1.04 | 5.995 | 10 | ok |
| R_middle | F5 | 0.958 | 0.0 (kept) | 4.0 | 3.94 | **4.07** | 3.45 | +0.49 | 4.065 | 10 | ok |
| R_index | G5 | 1.072 | 0.0 (kept) | 4.0 | 6.73 | **6.85** | 6.09 | +0.64 | 6.851 | 10 | ok |
| L_pinky | A5 | 1.181 | 0.0 (kept) | 4.0 | 7.42 | **7.54** | 7.14 | +0.28 | 7.541 | 10 | ok |
| L_ring | B5 | 1.104 | 0.0 (kept) | 4.0 | 9.28 | **9.40** | 8.39 | +0.88 | 9.401 | 10 | ok |
| L_middle | C6 | 1.048 | 0.0 (kept) | 4.0 | 6.48 | **6.60** | 5.80 | +0.68 | 6.602 | 10 | ok |
| L_index | D6 | 1.133 | 0.0 (kept) | 4.0 | 11.83 | **11.95** | 10.76 | +1.08 | 11.955 | 10 | above the pad limit |
| L_thumb | E6 | 1.022 | 0.0 (kept) | 4.0 | 15.29 | **15.42** | 12.71 | +2.58 | 15.416 | 12 | above the pad limit |
| R_thumb | F6 | 1.115 | 0.0 (kept) | 4.0 | 9.35 | **9.47** | 8.56 | +0.79 | 9.473 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.20; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.57 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_index 11.83 mm above the 10 mm pad limit; L_thumb 15.29 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-80-r2_air_capped.stl; holes and window closed): 2909 Hz = 2.08 × F6 on a 1.5 mm grid of 24073 cells (2 mm grid: 2907 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.578 + voicing pocket 0.138) = 78.7153 cm³ against the kernel's 78.7152 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2377 cm³ (+0.0166 %), air mesh 81.2364 cm³ (+0.0151 %), against the model target 81.2242 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9853, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.50 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 32.8 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.20 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_index), largest chimney error -0.0021 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 32.1 mm to the opposite wall, 34.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.84 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 29.7 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 15.2 / 15.6 / 16.6 mm, right 11.9 / 11.5 / 14.9 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.0 / 17.0 / 18.3, right 13.3 / 12.6 / 16.2 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 29.2 mm, right 27.1 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 31.7, right 29.4 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -5.7, left middle +9.5, right ring -4.5, right middle +6.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 26.3 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 26.4 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 9.3 mm, -115° off the normal of the left-hand line (-3.8 mm forward, -8.2 mm toward the index); at the outer skin 9.9 mm; sub2 from R_middle: 7.6 mm, +38° off the normal of the right-hand line (+5.9 mm forward, +4.6 mm toward the index); at the outer skin 8.0 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.8 mm (centre 11.5), tail 8.7 mm (centre 11.3); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.1 mm from R middle (ok -8 to +3), L thumb +14.5 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2.md`.

### P0-95-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `622bdad5acb2`. Window: Teardrop 9.65 × 11.10 mm, 81.2 mm², wall 4.0 mm. Windway: exit 1.20 × 11.10 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 95.00 cm³ (capped air). Measured on the STL: 96.467 cm³ against the model target 96.445 cm³ (+0.022 %). Cavity mesh 93.15 cm³ (3.25 cm³ of air in the holes, 0.03 cm³ of tube wall). Cavity spine length 83.1 mm. Plastic 48.6 cm³.
- Fitted constants: η_w 0.8604 (measured), k_hole 1.1339, position factors of shape `P0`. A4 error with the kept volume: -39.0 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.079 | 0.0 (kept) | 4.0 | 4.40 | **4.52** | 3.72 | +0.67 | 4.520 | 10 | ok |
| sub2 | C5 | 1.004 | 1.5 (kept) | 5.5 | 3.29 | **3.41** | 3.06 | +0.23 | 3.411 | 10 | ok |
| R_pinky | D5 | 0.857 | 0.0 (kept) | 4.0 | 5.91 | **6.04** | 4.65 | +1.26 | 6.035 | 10 | ok |
| R_ring | E5 | 0.916 | 0.0 (kept) | 4.0 | 6.66 | **6.78** | 5.42 | +1.24 | 6.783 | 10 | ok |
| R_middle | F5 | 0.958 | 0.0 (kept) | 4.0 | 4.44 | **4.56** | 3.85 | +0.59 | 4.557 | 10 | ok |
| R_index | G5 | 1.072 | 0.0 (kept) | 4.0 | 7.65 | **7.78** | 6.87 | +0.79 | 7.775 | 10 | ok |
| L_pinky | A5 | 1.181 | 0.0 (kept) | 4.0 | 8.45 | **8.57** | 8.07 | +0.38 | 8.574 | 10 | ok |
| L_ring | B5 | 1.104 | 0.0 (kept) | 4.0 | 10.61 | **10.74** | 9.52 | +1.10 | 10.737 | 10 | above the pad limit |
| L_middle | C6 | 1.048 | 0.0 (kept) | 4.0 | 7.36 | **7.48** | 6.53 | +0.83 | 7.479 | 10 | ok |
| L_index | D6 | 1.133 | 0.0 (kept) | 4.0 | 13.58 | **13.70** | 12.25 | +1.33 | 13.704 | 10 | above the pad limit |
| L_thumb | E6 | 1.022 | 0.0 (kept) | 4.0 | 17.59 | **17.71** | 14.51 | +3.08 | 17.714 | 12 | above the pad limit |
| R_thumb | F6 | 1.115 | 0.0 (kept) | 4.0 | 10.67 | **10.79** | 9.69 | +0.97 | 10.788 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.18; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.49 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_ring 10.61 mm above the 10 mm pad limit; L_index 13.58 mm above the 10 mm pad limit; L_thumb 17.59 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-95-r2_air_capped.stl; holes and window closed): 2750 Hz = 1.97 × F6 on a 1.5 mm grid of 28580 cells (2 mm grid: 2747 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 92.989 + voicing pocket 0.157) = 93.1457 cm³ against the kernel's 93.1456 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 96.4669 cm³ (+0.0224 %), air mesh 96.4652 cm³ (+0.0206 %), against the model target 96.4453 cm³ (V0 95.0000 cm³ in the print, volume factor 0.9853, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 2.91 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 622bdad5acb2; recomputed from the record: 622bdad5acb2 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 11.102 mm, 81.14 mm² (record 9.650 × 11.102, 81.15); windway exit 1.200 × 11.102 mm, inlet 1.560 × 11.102 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.60 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 35.1 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.01 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_thumb), largest chimney error -0.0023 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 1.500 mm (kernel 1.5), wall 1.198 mm, 35.7 mm to the opposite wall, 37.5 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.86 mm (sub1 to L_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 29.9 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2320 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 16.1 / 16.5 / 17.6 mm, right 12.6 / 12.1 / 15.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.9 / 17.9 / 19.3, right 14.0 / 13.2 / 17.1 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 30.8 mm, right 28.7 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 33.4, right 30.9 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -6.1, left middle +10.0, right ring -4.7, right middle +6.6 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 27.8 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 27.9 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 9.9 mm, -115° off the normal of the left-hand line (-4.0 mm forward, -8.7 mm toward the index); at the outer skin 10.5 mm; sub2 from R_middle: 8.0 mm, +38° off the normal of the right-hand line (+6.2 mm forward, +4.9 mm toward the index); at the outer skin 8.5 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.7 mm (centre 12.0), tail 8.7 mm (centre 11.8); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.6 mm from R middle (ok -8 to +3), L thumb +15.4 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2.md`.

### P0-125-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `f3803f8358b6`. Window: Teardrop 9.65 × 18.57 mm, 123.5 mm², wall 4.0 mm. Windway: exit 1.20 × 18.57 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 125.00 cm³ (capped air). Measured on the STL: 126.927 cm³ against the model target 126.884 cm³ (+0.034 %). Cavity mesh 121.78 cm³ (5.01 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 90.8 mm. Plastic 56.6 cm³.
- Fitted constants: η_w 0.8607 (measured), k_hole 1.1339, position factors of shape `P0`. A4 error with the kept volume: -38.6 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.079 | 0.0 (kept) | 4.0 | 5.33 | **5.45** | 4.45 | +0.88 | 5.451 | 10 | ok |
| sub2 | C5 | 1.004 | 0.0 (kept) | 4.0 | 3.51 | **3.63** | 3.19 | +0.32 | 3.633 | 10 | ok |
| R_pinky | D5 | 0.857 | 0.0 (kept) | 4.0 | 7.24 | **7.36** | 5.59 | +1.65 | 7.364 | 10 | ok |
| R_ring | E5 | 0.916 | 0.0 (kept) | 4.0 | 8.19 | **8.31** | 6.55 | +1.64 | 8.311 | 10 | ok |
| R_middle | F5 | 0.958 | 0.0 (kept) | 4.0 | 5.38 | **5.50** | 4.60 | +0.78 | 5.500 | 10 | ok |
| R_index | G5 | 1.072 | 0.0 (kept) | 4.0 | 9.45 | **9.57** | 8.35 | +1.10 | 9.571 | 10 | ok |
| L_pinky | A5 | 1.181 | 0.0 (kept) | 4.0 | 10.46 | **10.59** | 9.86 | +0.60 | 10.587 | 10 | above the pad limit |
| L_ring | B5 | 1.104 | 0.0 (kept) | 4.0 | 13.22 | **13.34** | 11.69 | +1.53 | 13.343 | 10 | above the pad limit |
| L_middle | C6 | 1.048 | 0.0 (kept) | 4.0 | 9.05 | **9.17** | 7.92 | +1.13 | 9.175 | 10 | ok |
| L_index | D6 | 1.133 | 0.0 (kept) | 4.0 | 17.00 | **17.12** | 15.14 | +1.85 | 17.117 | 10 | above the pad limit |
| L_thumb | E6 | 1.022 | 0.0 (kept) | 4.0 | 22.06 | **22.18** | 18.00 | +4.06 | 22.179 | 12 | above the pad limit |
| R_thumb | F6 | 1.115 | 0.0 (kept) | 4.0 | 13.21 | **13.33** | 11.87 | +1.34 | 13.330 | 12 | above the pad limit |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.12; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.36 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_pinky 10.46 mm above the 10 mm pad limit; L_ring 13.22 mm above the 10 mm pad limit; L_index 17.00 mm above the 10 mm pad limit; L_thumb 22.06 mm above the 12 mm pad limit; R_thumb 13.21 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-125-r2_air_capped.stl; holes and window closed): 2515 Hz = 1.80 × F6 on a 1.5 mm grid of 37600 cells (2 mm grid: 2506 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 121.544 + voicing pocket 0.235) = 121.7790 cm³ against the kernel's 121.7788 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 126.9274 cm³ (+0.0344 %), air mesh 126.9249 cm³ (+0.0324 %), against the model target 126.8838 cm³ (V0 125.0000 cm³ in the print, volume factor 0.9853, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 17 Booleans, all manifold, each volume change as expected (largest deviation 1.59 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash f3803f8358b6; recomputed from the record: f3803f8358b6 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 18.568 mm, 123.48 mm² (record 9.650 × 18.568, 123.50); windway exit 1.200 × 18.568 mm, inlet 1.560 × 18.568 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.88 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 38.1 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 1.74 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (L_pinky), largest chimney error -0.0007 mm (L_index); limit 0.05 mm |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.47 mm (sub1 to L_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 30.5 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.71 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 17.6 / 18.0 / 19.2 mm, right 13.8 / 13.3 / 17.3 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 19.4 / 19.4 / 20.9, right 15.2 / 14.4 / 18.6 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 33.7 mm, right 31.3 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 36.3, right 33.6 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -6.6, left middle +11.0, right ring -5.2, right middle +7.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 30.4 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 30.5 mm across (toward the player), +0.8 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 10.8 mm, -115° off the normal of the left-hand line (-4.4 mm forward, -9.5 mm toward the index); at the outer skin 11.4 mm; sub2 from R_middle: 8.7 mm, +38° off the normal of the right-hand line (+6.8 mm forward, +5.4 mm toward the index); at the outer skin 9.2 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.4 mm (centre 12.7), tail 8.8 mm (centre 12.5); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +8.3 mm from R middle (ok -8 to +3), L thumb +16.8 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-125-r2/P0-125-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-125-r2/P0-125-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-125-r2/P0-125-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-125-r2/P0-125-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-125-r2/P0-125-r2.md`.

### P1-80-r2

*Round 2 of a printed body.*

- Result: **UNEXPECTED FAILURES: hole_spacing**; expected by the notes: hole_limits[fitted] (fail); 4 warnings (soft ergonomic checks, never failures): ergo_hand_span, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.245 cm³ against the model target 81.224 cm³ (+0.026 %). Cavity mesh 78.71 cm³ (2.49 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 110.4 mm. Plastic 48.9 cm³.
- Fitted constants: η_w 0.8614 (measured), k_hole 1.1339, position factors of shape `P1`. A4 error with the kept volume: -38.0 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.080 | 0.0 (kept) | 4.0 | 3.90 | **4.02** | 3.34 | +0.56 | 4.022 | 10 | ok |
| sub2 | C5 | 0.994 | 3.0 (kept) | 7.0 | 3.26 | **3.38** | 3.06 | +0.21 | 3.385 | 10 | ok |
| R_pinky | D5 | 0.849 | 0.0 (kept) | 4.0 | 5.26 | **5.38** | 4.16 | +1.10 | 5.381 | 10 | ok |
| R_ring | E5 | 0.931 | 0.0 (kept) | 4.0 | 5.80 | **5.92** | 4.83 | +0.97 | 5.924 | 10 | ok |
| R_middle | F5 | 0.947 | 0.0 (kept) | 4.0 | 3.97 | **4.10** | 3.45 | +0.52 | 4.095 | 10 | ok |
| R_index | G5 | 1.067 | 0.0 (kept) | 4.0 | 6.75 | **6.87** | 6.09 | +0.66 | 6.874 | 10 | ok |
| L_pinky | A5 | 1.194 | 0.0 (kept) | 4.0 | 7.36 | **7.48** | 7.14 | +0.22 | 7.481 | 10 | ok |
| L_ring | B5 | 1.109 | 0.0 (kept) | 4.0 | 9.25 | **9.37** | 8.39 | +0.85 | 9.369 | 10 | ok |
| L_middle | C6 | 1.007 | 0.0 (kept) | 4.0 | 6.67 | **6.79** | 5.80 | +0.86 | 6.789 | 10 | ok |
| L_index | D6 | 1.145 | 0.0 (kept) | 4.0 | 11.74 | **11.86** | 10.76 | +0.98 | 11.863 | 10 | above the pad limit |
| L_thumb | E6 | 1.019 | 0.0 (kept) | 4.0 | 15.32 | **15.45** | 12.71 | +2.61 | 15.445 | 12 | above the pad limit |
| R_thumb | F6 | 1.108 | 0.0 (kept) | 4.0 | 9.39 | **9.51** | 8.56 | +0.83 | 9.514 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.20; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.13 x F6: below 1.3, so a FEM check of the top fingerings is required (the kernel's own status: needs_fem). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_index 11.74 mm above the 10 mm pad limit; L_thumb 15.32 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P1-80-r2_air_capped.stl; holes and window closed): 2259 Hz = 1.62 × F6 on a 1.5 mm grid of 24084 cells (2 mm grid: 2249 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.560 + voicing pocket 0.154) = 78.7133 cm³ against the kernel's 78.7132 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2453 cm³ (+0.0258 %), air mesh 81.2438 cm³ (+0.0241 %), against the model target 81.2243 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9853, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 4.80 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset +0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 31.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.47 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_pinky), largest chimney error -0.0039 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 24.0 mm to the opposite wall, 40.8 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.79° (L_middle); limit 2.0° |
| `hole_spacing` | FAIL | smallest edge gap 2.80 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -10.2 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +10.7 mm (35 % of the half section there); the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); edge gap sub1 to L_ring is 2.80 mm, under 3.4 mm, with the new diameters at the round-1 positions; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 21.2 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 2.70 mm |
| `ergo_finger_pitch` | pass | left 17.2 / 17.6 / 16.9 mm, right 17.2 / 18.0 / 17.3 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.7 / 18.7 / 18.0, right 18.0 / 18.3 / 18.0 mm |
| `ergo_hand_span` | WARN | hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.2 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.3, right 51.8 mm |
| `ergo_arch` | pass | left ring +3.2, left middle +4.0, right ring +3.7, right middle +4.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +2.1° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 21.2 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +16.1°, right line +14.0° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 21.2 mm across (toward the player), -0.4 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 9.5 mm, +0° off the normal of the left-hand line (+9.4 mm forward, +0.0 mm toward the index); at the outer skin 10.7 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.6 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | the bulb end is 4.9 mm too short: 5.1 mm past the L pinky hole edge; the tail end is 5.7 mm too short: 4.3 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 5.1 mm (centre 8.9), tail 4.3 mm (centre 7.0); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | L_pinky leans 37° toward the bulb end; R_pinky leans 29° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +37°, L_ring +15°, L_middle -0°, L_index -14°, R_pinky +29°, R_ring +15°, R_middle +11°, R_index +5°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 12° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -0°, L_ring +0°, L_middle +4°, L_index +17°, R_pinky -12°, R_ring -3°, R_middle +7°, R_index +22°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.2 mm from R middle (ok -8 to +3), L thumb +8.6 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2.md`.

### P2-80-r2

*Round 2 of a printed body.*

- Result: **UNEXPECTED FAILURES: hole_spacing**; expected by the notes: hole_limits[fitted] (fail); 5 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.241 cm³ against the model target 81.224 cm³ (+0.021 %). Cavity mesh 78.52 cm³ (2.69 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 125.1 mm. Plastic 51.6 cm³.
- Fitted constants: η_w 0.8614 (measured), k_hole 1.1339, position factors of shape `P2`. A4 error with the kept volume: -38.0 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.040 | 0.0 (kept) | 4.0 | 4.00 | **4.12** | 3.34 | +0.66 | 4.122 | 10 | ok |
| sub2 | C5 | 0.941 | 3.0 (kept) | 7.0 | 3.37 | **3.49** | 3.06 | +0.31 | 3.492 | 10 | ok |
| R_pinky | D5 | 0.804 | 0.0 (kept) | 4.0 | 5.47 | **5.59** | 4.16 | +1.31 | 5.588 | 10 | ok |
| R_ring | E5 | 0.884 | 0.0 (kept) | 4.0 | 6.02 | **6.14** | 4.83 | +1.19 | 6.144 | 10 | ok |
| R_middle | F5 | 0.909 | 0.0 (kept) | 4.0 | 4.09 | **4.21** | 3.45 | +0.63 | 4.207 | 10 | ok |
| R_index | G5 | 1.023 | 0.0 (kept) | 4.0 | 6.96 | **7.09** | 6.09 | +0.87 | 7.086 | 10 | ok |
| L_pinky | A5 | 1.124 | 0.0 (kept) | 4.0 | 7.70 | **7.82** | 7.14 | +0.56 | 7.819 | 10 | ok |
| L_ring | B5 | 1.051 | 0.0 (kept) | 4.0 | 9.63 | **9.75** | 8.39 | +1.23 | 9.749 | 10 | ok |
| L_middle | C6 | 0.999 | 0.0 (kept) | 4.0 | 6.71 | **6.83** | 5.80 | +0.90 | 6.827 | 10 | ok |
| L_index | D6 | 1.071 | 0.0 (kept) | 4.0 | 12.36 | **12.48** | 10.76 | +1.60 | 12.483 | 10 | above the pad limit |
| L_thumb | E6 | 0.974 | 0.0 (kept) | 4.0 | 15.86 | **15.98** | 12.71 | +3.15 | 15.985 | 12 | above the pad limit |
| R_thumb | F6 | 1.052 | 0.0 (kept) | 4.0 | 9.75 | **9.87** | 8.56 | +1.18 | 9.868 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.17; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.99 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_index 12.36 mm above the 10 mm pad limit; L_thumb 15.86 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P2-80-r2_air_capped.stl; holes and window closed): 1946 Hz = 1.39 × F6 on a 1.5 mm grid of 24099 cells (2 mm grid: 1936 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.342 + voicing pocket 0.177) = 78.5187 cm³ against the kernel's 78.5186 cm³: +0.0002 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2406 cm³ (+0.0205 %), air mesh 81.2369 cm³ (+0.0160 %), against the model target 81.2239 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9853, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.75 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset +0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 31.0 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.97 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (L_index), largest chimney error -0.0008 mm (sub1); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 17.3 mm to the opposite wall, 45.7 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.10° (R_index); limit 2.0° |
| `hole_spacing` | FAIL | smallest edge gap 2.56 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -8.7 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.6 mm (35 % of the half section there); the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); edge gap sub1 to L_ring is 2.56 mm, under 3.4 mm, with the new diameters at the round-1 positions; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 17.1 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 2.95 mm |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.5 mm. Measured: left 17.1 / 17.6 / 16.5 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.4 / 18.8 / 17.5, right 17.3 / 18.0 / 16.9 mm |
| `ergo_hand_span` | WARN | hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.8 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.2, right 51.0 mm |
| `ergo_arch` | pass | left ring +2.9, left middle +3.4, right ring +3.3, right middle +3.4 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +2.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 18.7 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.9°, right line +12.3° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 18.7 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 9.5 mm, +0° off the normal of the left-hand line (+9.5 mm forward, +0.0 mm toward the index); at the outer skin 10.5 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.5 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | the bulb end is 0.9 mm too short: 9.1 mm past the L pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 9.1 mm (centre 13.0), tail 11.8 mm (centre 14.5); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | L_pinky leans 29° toward the bulb end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +29°, L_ring +11°, L_middle -6°, L_index -19°, R_pinky +12°, R_ring +8°, R_middle +8°, R_index +9°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 7° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +2°, L_ring +1°, L_middle +1°, L_index +12°, R_pinky -7°, R_ring -3°, R_middle +5°, R_index +19°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.4 mm from R middle (ok -8 to +3), L thumb +9.0 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2.md`.

### P3-80-r2

*Round 2 of a printed body.*

- Result: **UNEXPECTED FAILURES: hole_spacing**; expected by the notes: hole_limits[fitted] (fail); 6 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_hand_offset, ergo_index_meet, ergo_rest_space, ergo_hole_lean_end.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.223 cm³ against the model target 81.224 cm³ (-0.002 %). Cavity mesh 78.70 cm³ (2.51 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 94.5 mm. Plastic 47.5 cm³.
- Fitted constants: η_w 0.8614 (measured), k_hole 1.1339, position factors of shape `P3`. A4 error with the kept volume: -38.0 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.091 | 0.0 (kept) | 4.0 | 3.87 | **3.99** | 3.34 | +0.53 | 3.995 | 10 | ok |
| sub2 | C5 | 1.010 | 3.0 (kept) | 7.0 | 3.23 | **3.35** | 3.06 | +0.17 | 3.353 | 10 | ok |
| R_pinky | D5 | 0.846 | 0.0 (kept) | 4.0 | 5.27 | **5.39** | 4.16 | +1.11 | 5.393 | 10 | ok |
| R_ring | E5 | 0.917 | 0.0 (kept) | 4.0 | 5.87 | **5.99** | 4.83 | +1.03 | 5.987 | 10 | ok |
| R_middle | F5 | 0.965 | 0.0 (kept) | 4.0 | 3.92 | **4.04** | 3.45 | +0.47 | 4.045 | 10 | ok |
| R_index | G5 | 1.072 | 0.0 (kept) | 4.0 | 6.73 | **6.85** | 6.09 | +0.64 | 6.852 | 10 | ok |
| L_pinky | A5 | 1.177 | 0.0 (kept) | 4.0 | 7.44 | **7.56** | 7.14 | +0.30 | 7.561 | 10 | ok |
| L_ring | B5 | 1.108 | 0.0 (kept) | 4.0 | 9.25 | **9.37** | 8.39 | +0.85 | 9.371 | 10 | ok |
| L_middle | C6 | 1.056 | 0.0 (kept) | 4.0 | 6.44 | **6.56** | 5.80 | +0.64 | 6.563 | 10 | ok |
| L_index | D6 | 1.140 | 0.0 (kept) | 4.0 | 11.78 | **11.90** | 10.76 | +1.02 | 11.898 | 10 | above the pad limit |
| L_thumb | E6 | 0.992 | 0.0 (kept) | 4.0 | 15.66 | **15.78** | 12.71 | +2.94 | 15.779 | 12 | above the pad limit |
| R_thumb | F6 | 1.149 | 0.0 (kept) | 4.0 | 9.14 | **9.26** | 8.56 | +0.58 | 9.261 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.20; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.32 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_index 11.78 mm above the 10 mm pad limit; L_thumb 15.66 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P3-80-r2_air_capped.stl; holes and window closed): 2438 Hz = 1.75 × F6 on a 1.5 mm grid of 24088 cells (2 mm grid: 2427 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.544 + voicing pocket 0.155) = 78.6988 cm³ against the kernel's 78.6986 cm³: +0.0002 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2227 cm³ (-0.0016 %), air mesh 81.2341 cm³ (+0.0124 %), against the model target 81.2240 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9853, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.24 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset +0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 26.6 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.79 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_ring), largest chimney error -0.0039 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 28.3 mm to the opposite wall, 33.9 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.88° (sub1); limit 2.0° |
| `hole_spacing` | FAIL | smallest edge gap 2.70 mm (sub2 to L_index); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 1.25 mm (L_index; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; each hand was slid 12 mm along its own line toward the other hand (preset value hand_overlap_mm); the finger pitch is unchanged; R_index: the sideways offset was limited from -15.4 to -11.3 mm (35 % of the half section there); L_index: the sideways offset was limited from +14.8 to +11.1 mm (35 % of the half section there); the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); edge gap sub2 to L_index is 2.70 mm, under 3.4 mm, with the new diameters at the round-1 positions; edge gap sub1 to L_ring is 2.82 mm, under 3.4 mm, with the new diameters at the round-1 positions; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 16.1 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.11 mm |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.3 mm. Measured: left 17.0 / 17.4 / 16.3 mm, right 17.1 / 18.1 / 17.1 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.0 / 18.0 / 16.9, right 18.4 / 18.8 / 17.8 mm |
| `ergo_hand_span` | WARN | hand span out of range: left hand 49.4 mm. Measured: left 49.4 mm, right 51.0 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.4, right 53.6 mm |
| `ergo_arch` | pass | left ring +3.3, left middle +2.9, right ring +1.9, right middle +1.7 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines -5.3° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | hand lines 17.6 mm apart across. Measured: the right-hand line is 17.6 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +9.5°, right line +14.8° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | index holes 17.6 mm apart across; R index -23.2 mm along the hand axis from L index. Measured: R index from L index: 17.6 mm across (toward the player), -23.2 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 9.5 mm, +0° off the normal of the left-hand line (+9.5 mm forward, +0.0 mm toward the index); at the outer skin 10.5 mm; sub2 from R_middle: 7.5 mm, -0° off the normal of the right-hand line (+7.5 mm forward, -0.0 mm toward the index); at the outer skin 8.2 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | the bulb end is 0.1 mm too short: 9.9 mm past the L pinky hole edge; the tail end is 2.6 mm too short: 7.4 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 9.9 mm (centre 13.6), tail 7.4 mm (centre 10.1); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | L_pinky leans 23° toward the bulb end; R_pinky leans 31° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +23°, L_ring +9°, L_middle -0°, L_index -8°, R_pinky +31°, R_ring +11°, R_middle +2°, R_index -8°; ok up to 20° |
| `ergo_hole_lean_side` | pass | lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +10°, L_ring +5°, L_middle +8°, L_index +16°, R_pinky +5°, R_ring +4°, R_middle +8°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.8 mm from R middle (ok -8 to +3), L thumb +9.1 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P3-80-r2/P3-80-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P3-80-r2/P3-80-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P3-80-r2/P3-80-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P3-80-r2/P3-80-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P3-80-r2/P3-80-r2.md`.

### P0-110-r2

*Never printed: sized from the fitted model only.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `39c00d2765a6`. Window: Teardrop 9.65 × 15.94 mm, 108.7 mm², wall 4.0 mm. Windway: exit 1.20 × 15.94 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 110.00 cm³ (capped air). Measured on the STL: 111.698 cm³ against the model target 111.665 cm³ (+0.030 %). Cavity mesh 107.51 cm³ (4.07 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 87.1 mm. Plastic 52.9 cm³.
- Fitted constants: η_w 0.8602 (fallback), k_hole 1.1339, position factors of shape `P0`. A4 error with the kept volume: +0.0 cents. **Note:** voicing hash was never measured: eta_w_fallback used.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.079 | 0.0 | 4.0 | 4.37 | **4.49** | – | – | 4.490 | 10 | ok |
| sub2 | C5 | 1.004 | 0.0 | 4.0 | 3.23 | **3.35** | – | – | 3.349 | 10 | ok |
| R_pinky | D5 | 0.857 | 0.0 | 4.0 | 6.59 | **6.71** | – | – | 6.707 | 10 | ok |
| R_ring | E5 | 0.916 | 0.0 | 4.0 | 7.43 | **7.55** | – | – | 7.555 | 10 | ok |
| R_middle | F5 | 0.958 | 0.0 | 4.0 | 4.91 | **5.04** | – | – | 5.035 | 10 | ok |
| R_index | G5 | 1.072 | 0.0 | 4.0 | 8.56 | **8.68** | – | – | 8.681 | 10 | ok |
| L_pinky | A5 | 1.181 | 0.0 | 4.0 | 9.47 | **9.59** | – | – | 9.590 | 10 | ok |
| L_ring | B5 | 1.104 | 0.0 | 4.0 | 11.93 | **12.05** | – | – | 12.051 | 10 | above the pad limit |
| L_middle | C6 | 1.048 | 0.0 | 4.0 | 8.21 | **8.34** | – | – | 8.336 | 10 | ok |
| L_index | D6 | 1.133 | 0.0 | 4.0 | 15.30 | **15.43** | – | – | 15.425 | 10 | above the pad limit |
| L_thumb | E6 | 1.022 | 0.0 | 4.0 | 19.85 | **19.97** | – | – | 19.970 | 12 | above the pad limit |
| R_thumb | F6 | 1.115 | 0.0 | 4.0 | 11.95 | **12.07** | – | – | 12.074 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.71; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.42 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_ring 11.93 mm above the 10 mm pad limit; L_index 15.30 mm above the 10 mm pad limit; L_thumb 19.85 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-110-r2_air_capped.stl; holes and window closed): 2623 Hz = 1.88 × F6 on a 1.5 mm grid of 33075 cells (2 mm grid: 2618 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 107.299 + voicing pocket 0.208) = 107.5074 cm³ against the kernel's 107.5073 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 111.6985 cm³ (+0.0302 %), air mesh 111.6938 cm³ (+0.0260 %), against the model target 111.6648 cm³ (V0 110.0000 cm³ in the print, volume factor 0.9853, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 17 Booleans, all manifold, each volume change as expected (largest deviation 1.37 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 39c00d2765a6; recomputed from the record: 39c00d2765a6 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 15.942 mm, 108.65 mm² (record 9.650 × 15.942, 108.66); windway exit 1.200 × 15.942 mm, inlet 1.560 × 15.942 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.08 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 36.6 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 1.86 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (R_index), largest chimney error -0.0007 mm (L_index); limit 0.05 mm |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.93 mm (sub1 to L_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 30.3 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 16.9 / 17.3 / 18.4 mm, right 13.2 / 12.7 / 16.6 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.7 / 18.7 / 20.1, right 14.6 / 13.8 / 17.9 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 32.3 mm, right 30.1 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 34.9, right 32.3 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -6.4, left middle +10.5, right ring -5.0, right middle +7.0 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 29.2 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 29.3 mm across (toward the player), +0.8 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 10.3 mm, -115° off the normal of the left-hand line (-4.2 mm forward, -9.1 mm toward the index); at the outer skin 10.9 mm; sub2 from R_middle: 8.4 mm, +38° off the normal of the right-hand line (+6.5 mm forward, +5.2 mm toward the index); at the outer skin 8.8 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.6 mm (centre 12.3), tail 8.8 mm (centre 12.1); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.9 mm from R middle (ok -8 to +3), L thumb +16.1 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-110-r2/P0-110-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-110-r2/P0-110-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-110-r2/P0-110-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-110-r2/P0-110-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-110-r2/P0-110-r2.md`.

