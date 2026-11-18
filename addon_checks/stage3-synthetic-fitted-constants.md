# Stage 3 · Round 2 corrected bodies: generation report

> **SYNTHETIC CONSTANTS.** This stage was sized from a fitted-constants file that is marked synthetic: invented truth values, not measurements of printed bodies. The report shows that the Stage 3 generator works. Do not print these bodies.

Written by `ocarina_addon/headless.py -- stage3 --calibration calibration/synthetic-fitted-constants.toml` on 2026-11-17. Every measured number comes from the STL file of the body, read back from disk. Run time 276 s for 7 bodies.

Result: **4 of 7 bodies have no unexpected failure**; UNEXPECTED FAILURES on P1-80-r2, P2-80-r2, P4-80-r2.

- Sized from the fitted-constants file `calibration/synthetic-fitted-constants.toml`: k_hole 1.1804 (profile estimate), hole offset -0.122 mm (printed minus designed), volume factor 0.9854 (printed / designed), η_w fallback 0.8601; η_w measured for the voicing hashes `2a71c31c2505` 0.8585, `617b869f0b10` 0.8615, `7b411d5079d7` 0.8604.
- Bodies that were printed in round 1 keep their window, their volume, their inward tubes and their hole positions (doc 04 D10). Only the hole diameters change. The printed volume is kept (the default), so A4 errs by the amount the measured η_w says; the table gives it.
- Each hole is drawn at its CAD diameter (design diameter minus the hole offset), and the model holds V0 divided by the volume factor, so that the print holds V0.
- P0 at 88 cm³ was never printed: its window, tubes and holes come from the fitted model alone (the prediction test of Gate 3).
- The per-body check reports of this stage are written beside the STL files (not in git), and no pictures are made unless `--renders` is given: the result depends on the constants file.
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).
- The constants of this stage are those of the fitted-constants file named above, not the pre-calibration priors. This command measured nothing on a printed body: every measured number here comes from an STL file.
- Statuses: `pass` (the docs say ok), `FAIL`, `NEEDS FEM` (cavity-mode desk check between its limits), `WARN` (a soft ergonomic check; never a failure), `info` (a reported number).

## Bodies

| Body | Preset | V0 | Voicing hash | Window | Windway exit | Capped air on the STL | First cavity mode (desk check) | Plastic; solid PLA mass | doc 04 mass | Failures | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0-65-r2 | P0 | 65.0 cm³ | `2a71c31c2505` | Teardrop 9.65 × 6.96 mm, 46.5 mm² | 1.20 × 6.96 mm | 66.009 cm³ (+0.015 %) | 2.23 × F6, pass (c/(2L): 1.69) | 39.5 cm³; 49 g | 77 g | hole_limits[fitted] (expected) | 11 (taped test body) |
| P0-80-r2 | P0 | 80.0 cm³ | `617b869f0b10` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.235 cm³ (+0.017 %) | 2.08 × F6, pass (c/(2L): 1.57) | 44.2 cm³; 55 g | 84 g | hole_limits[fitted] (expected) | 11 (taped test body) |
| P0-95-r2 | P0 | 95.0 cm³ | `7b411d5079d7` | Teardrop 9.65 × 11.10 mm, 81.2 mm² | 1.20 × 11.10 mm | 96.463 cm³ (+0.023 %) | 1.97 × F6, pass (c/(2L): 1.49) | 48.5 cm³; 60 g | 91 g | hole_limits[fitted] (expected) | 11 (taped test body) |
| P1-80-r2 | P1 | 80.0 cm³ | `617b869f0b10` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.242 cm³ (+0.026 %) | 1.62 × F6, pass (c/(2L): 1.13) | 48.8 cm³; 61 g | 91 g | **hole_spacing (unexpected)**, hole_limits[fitted] (expected) | 4 |
| P2-80-r2 | P2 | 80.0 cm³ | `617b869f0b10` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.238 cm³ (+0.021 %) | 1.39 × F6, pass (c/(2L): 0.99) | 51.5 cm³; 64 g | 97 g | **hole_spacing (unexpected)**, hole_limits[fitted] (expected) | 5 |
| P4-80-r2 | P4 | 80.0 cm³ | `617b869f0b10` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.214 cm³ (-0.007 %) | 1.36 × F6, pass (c/(2L): 0.94) | 52.0 cm³; 64 g | 99 g | **hole_spacing (unexpected)**, hole_limits[fitted] (expected) | 2 |
| P0-88-r2 | P0 | 88.0 cm³ | `cd934d015aea` | Teardrop 9.65 × 10.44 mm, 77.4 mm² | 1.20 × 10.44 mm | 89.357 cm³ (+0.021 %) | 2.02 × F6, pass (c/(2L): 1.52) | 46.6 cm³; 58 g | 88 g | hole_limits[fitted] (expected) | 11 (taped test body) |

*Capped air* is compared with the target of the model: V0 for a round-1 body, the stub volume for a stub, and in Stage 3 V0 divided by the fitted volume factor, with the holes drawn at their CAD diameters. *First cavity mode* is the computed desk check with closed holes, which gives the verdict; the number in brackets is the kernel's c/(2L) estimate from the length of the chamber, the lowest estimate, shown for information (it is 30 to 44 % low for these shapes, docs/06 section 3.10). *Solid PLA mass* is the plastic volume of the STL at 1.24 g/cm³, with no supports, brim or infill saving; the doc 04 figure includes about 12 % for supports and a brim.

Total for the 7 bodies of this stage: 411 g of solid PLA, 460 g with 12 % for supports and a brim. The doc 04 budget for this stage is 627 g. The generated bodies are lighter than the budget; the doc 04 masses were estimates made before any body was built.

## Unexpected failures

- **P1-80-r2** `hole_spacing`: smallest edge gap 2.81 mm (sub1 to L_ring); at least 3.4 mm
- **P2-80-r2** `hole_spacing`: smallest edge gap 2.54 mm (sub1 to L_ring); at least 3.4 mm
- **P4-80-r2** `hole_spacing`: smallest edge gap 2.17 mm (sub1 to L_ring); at least 3.4 mm

**Why `hole_spacing` fails here.** The hole positions of a printed body are frozen at the round-1 layout (doc 04 D10), and the corrected holes are larger than the round-1 holes. A hole that was just clear of its neighbour in round 1 is then too close. The tightest pair of the hand layout is the left subhole and L_ring: the 9.5 mm slide leaves 3.63 mm between the hole edges at the round-1 (k_hole 0.8) diameters, and 3.05 mm at the k_hole 1.0 diameters, against the limit of 3.4 mm. The build is correct; the rules conflict. The owner has to choose before the layout is frozen: a longer slide in round 1, a smaller edge gap in round 2, or a subhole that may move in round 2 (see the build notes, "Questions for the owner").

## Expected failures

Failures that the plan expects (the pad-limit checks: doc 04 prints these holes on purpose, "the real limit is unknown"). They do not stop a stage.

- P0-65-r2 `hole_limits[fitted]` (fail): L_index 10.06 mm above the 10 mm pad limit; L_thumb 12.94 mm above the 12 mm pad limit
- P0-80-r2 `hole_limits[fitted]` (fail): L_index 11.86 mm above the 10 mm pad limit; L_thumb 15.30 mm above the 12 mm pad limit
- P0-95-r2 `hole_limits[fitted]` (fail): L_ring 10.64 mm above the 10 mm pad limit; L_index 13.62 mm above the 10 mm pad limit; L_thumb 17.61 mm above the 12 mm pad limit
- P1-80-r2 `hole_limits[fitted]` (fail): L_index 11.80 mm above the 10 mm pad limit; L_thumb 15.38 mm above the 12 mm pad limit
- P2-80-r2 `hole_limits[fitted]` (fail): L_index 12.21 mm above the 10 mm pad limit; L_thumb 15.94 mm above the 12 mm pad limit
- P4-80-r2 `hole_limits[fitted]` (fail): L_ring 10.24 mm above the 10 mm pad limit; L_index 13.36 mm above the 10 mm pad limit; L_thumb 15.92 mm above the 12 mm pad limit
- P0-88-r2 `hole_limits[fitted]` (fail): L_ring 10.02 mm above the 10 mm pad limit; L_index 12.80 mm above the 10 mm pad limit; L_thumb 16.54 mm above the 12 mm pad limit

### Round-hole verdict (doc 04, Gate 2)

The rule of Gate 2, applied to the holes of this stage: a ladder step fails this verdict if a fitted hole needs more than 10 mm (finger) or 12 mm (thumb).

- P0-65-r2: L_index needs 10.06 mm (limit 10 mm)
- P0-65-r2: L_thumb needs 12.94 mm (limit 12 mm)
- P0-80-r2: L_index needs 11.86 mm (limit 10 mm)
- P0-80-r2: L_thumb needs 15.30 mm (limit 12 mm)
- P0-95-r2: L_ring needs 10.64 mm (limit 10 mm)
- P0-95-r2: L_index needs 13.62 mm (limit 10 mm)
- P0-95-r2: L_thumb needs 17.61 mm (limit 12 mm)
- P1-80-r2: L_index needs 11.80 mm (limit 10 mm)
- P1-80-r2: L_thumb needs 15.38 mm (limit 12 mm)
- P2-80-r2: L_index needs 12.21 mm (limit 10 mm)
- P2-80-r2: L_thumb needs 15.94 mm (limit 12 mm)
- P4-80-r2: L_ring needs 10.24 mm (limit 10 mm)
- P4-80-r2: L_index needs 13.36 mm (limit 10 mm)
- P4-80-r2: L_thumb needs 15.92 mm (limit 12 mm)
- P0-88-r2: L_ring needs 10.02 mm (limit 10 mm)
- P0-88-r2: L_index needs 12.80 mm (limit 10 mm)
- P0-88-r2: L_thumb needs 16.54 mm (limit 12 mm)

## Warnings

Soft ergonomic checks outside their range. They are measurements for the owner to judge. A warning is never a failure.

- P0-65-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2.md`.
- P0-80-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2.md`.
- P0-95-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2.md`.
- P1-80-r2 `ergo_hand_span`: hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.2 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.3, right 51.8 mm
- P1-80-r2 `ergo_rest_space`: the bulb end is 4.9 mm too short: 5.1 mm past the L pinky hole edge; the tail end is 5.7 mm too short: 4.3 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 5.1 mm (centre 8.9), tail 4.3 mm (centre 7.0); ok at least 10 mm
- P1-80-r2 `ergo_hole_lean_end`: L_pinky leans 37° toward the bulb end; R_pinky leans 29° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +37°, L_ring +15°, L_middle -0°, L_index -14°, R_pinky +29°, R_ring +15°, R_middle +11°, R_index +5°; ok up to 20°
- P1-80-r2 `ergo_hole_lean_side`: R_pinky leans 12° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -0°, L_ring +0°, L_middle +4°, L_index +17°, R_pinky -12°, R_ring -3°, R_middle +7°, R_index +22°; ok up to 45° toward it and up to 5° away
- P2-80-r2 `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.5 mm. Measured: left 17.1 / 17.6 / 16.5 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.4 / 18.8 / 17.5, right 17.3 / 18.0 / 16.9 mm
- P2-80-r2 `ergo_hand_span`: hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.8 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.2, right 51.0 mm
- P2-80-r2 `ergo_rest_space`: the bulb end is 0.9 mm too short: 9.1 mm past the L pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 9.1 mm (centre 13.0), tail 11.8 mm (centre 14.5); ok at least 10 mm
- P2-80-r2 `ergo_hole_lean_end`: L_pinky leans 29° toward the bulb end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +29°, L_ring +11°, L_middle -6°, L_index -19°, R_pinky +12°, R_ring +8°, R_middle +8°, R_index +9°; ok up to 20°
- P2-80-r2 `ergo_hole_lean_side`: R_pinky leans 7° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +2°, L_ring +1°, L_middle +1°, L_index +12°, R_pinky -7°, R_ring -3°, R_middle +5°, R_index +19°; ok up to 45° toward it and up to 5° away
- P4-80-r2 `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.7 / 18.2 / 17.1, right 17.4 / 18.3 / 17.5 mm
- P4-80-r2 `ergo_hole_lean_side`: R_pinky leans 10° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -5°, L_ring -3°, L_middle +4°, L_index +20°, R_pinky -10°, R_ring -4°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away
- P0-88-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2.md`.

## Per body

### P0-65-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `2a71c31c2505`. Window: Teardrop 9.65 × 6.96 mm, 46.5 mm², wall 4.0 mm. Windway: exit 1.20 × 6.96 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 65.00 cm³ (capped air). Measured on the STL: 66.009 cm³ against the model target 65.999 cm³ (+0.015 %). Cavity mesh 64.21 cm³ (1.82 cm³ of air in the holes, 0.09 cm³ of tube wall). Cavity spine length 73.4 mm. Plastic 39.5 cm³.
- Fitted constants: η_w 0.8585 (measured), k_hole 1.1804, position factors of shape `P0`. A4 error with the kept volume: -40.9 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.101 | 0.5 (kept) | 4.5 | 3.56 | **3.68** | 3.08 | +0.48 | 3.677 | 10 | ok |
| sub2 | C5 | 1.015 | 5.0 (kept) | 9.0 | 3.17 | **3.29** | 3.03 | +0.14 | 3.293 | 10 | ok |
| R_pinky | D5 | 0.874 | 0.0 (kept) | 4.0 | 4.52 | **4.65** | 3.64 | +0.88 | 4.645 | 10 | ok |
| R_ring | E5 | 0.937 | 0.0 (kept) | 4.0 | 5.06 | **5.18** | 4.22 | +0.84 | 5.184 | 10 | ok |
| R_middle | F5 | 0.975 | 0.0 (kept) | 4.0 | 3.43 | **3.56** | 3.03 | +0.40 | 3.557 | 10 | ok |
| R_index | G5 | 1.101 | 0.0 (kept) | 4.0 | 5.77 | **5.89** | 5.29 | +0.48 | 5.894 | 10 | ok |
| L_pinky | A5 | 1.214 | 0.0 (kept) | 4.0 | 6.35 | **6.48** | 6.18 | +0.18 | 6.476 | 10 | ok |
| L_ring | B5 | 1.135 | 0.0 (kept) | 4.0 | 7.92 | **8.04** | 7.24 | +0.68 | 8.039 | 10 | ok |
| L_middle | C6 | 1.075 | 0.0 (kept) | 4.0 | 5.57 | **5.70** | 5.05 | +0.53 | 5.696 | 10 | ok |
| L_index | D6 | 1.166 | 0.0 (kept) | 4.0 | 10.06 | **10.18** | 9.22 | +0.83 | 10.178 | 10 | above the pad limit |
| L_thumb | E6 | 1.055 | 0.0 (kept) | 4.0 | 12.94 | **13.06** | 10.87 | +2.07 | 13.059 | 12 | above the pad limit |
| R_thumb | F6 | 1.143 | 0.0 (kept) | 4.0 | 8.01 | **8.14** | 7.39 | +0.62 | 8.135 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.26; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.69 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_index 10.06 mm above the 10 mm pad limit; L_thumb 12.94 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-65-r2_air_capped.stl; holes and window closed): 3111 Hz = 2.23 × F6 on a 1.5 mm grid of 19527 cells (2 mm grid: 3103 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 64.083 + voicing pocket 0.124) = 64.2073 cm³ against the kernel's 64.2072 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 66.0089 cm³ (+0.0146 %), air mesh 66.0069 cm³ (+0.0115 %), against the model target 65.9993 cm³ (V0 65.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 19 Booleans, all manifold, each volume change as expected (largest deviation 12.43 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 2a71c31c2505; recomputed from the record: 2a71c31c2505 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 6.959 mm, 46.47 mm² (record 9.650 × 6.959, 46.47); windway exit 1.200 × 6.959 mm, inlet 1.560 × 6.959 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.48 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 29.5 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.67 mm (at least 0.8 mm); windway roof 3.00 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (L_thumb), largest chimney error -0.0058 mm (sub1); limit 0.05 mm |
| `inward_tubes` | pass | sub1: length 0.500 mm (kernel 0.5), wall 1.198 mm, 30.8 mm to the opposite wall, 30.8 mm to the labium, 23.9 mm to the nearest other tube; sub2: length 5.000 mm (kernel 5.0), wall 1.198 mm, 27.8 mm to the opposite wall, 29.8 mm to the labium, 23.9 mm to the nearest other tube |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.64 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 28.7 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.81 mm |
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
- Voicing hash `617b869f0b10`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.235 cm³ against the model target 81.221 cm³ (+0.017 %). Cavity mesh 78.71 cm³ (2.50 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 78.5 mm. Plastic 44.2 cm³.
- Fitted constants: η_w 0.8615 (measured), k_hole 1.1804, position factors of shape `P0`. A4 error with the kept volume: -37.8 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.101 | 0.0 (kept) | 4.0 | 3.90 | **4.02** | 3.34 | +0.56 | 4.025 | 10 | ok |
| sub2 | C5 | 1.015 | 3.0 (kept) | 7.0 | 3.25 | **3.37** | 3.06 | +0.19 | 3.371 | 10 | ok |
| R_pinky | D5 | 0.874 | 0.0 (kept) | 4.0 | 5.24 | **5.36** | 4.16 | +1.08 | 5.363 | 10 | ok |
| R_ring | E5 | 0.937 | 0.0 (kept) | 4.0 | 5.88 | **6.00** | 4.83 | +1.05 | 6.003 | 10 | ok |
| R_middle | F5 | 0.975 | 0.0 (kept) | 4.0 | 3.95 | **4.07** | 3.45 | +0.50 | 4.074 | 10 | ok |
| R_index | G5 | 1.101 | 0.0 (kept) | 4.0 | 6.73 | **6.85** | 6.09 | +0.63 | 6.849 | 10 | ok |
| L_pinky | A5 | 1.214 | 0.0 (kept) | 4.0 | 7.42 | **7.54** | 7.14 | +0.28 | 7.543 | 10 | ok |
| L_ring | B5 | 1.135 | 0.0 (kept) | 4.0 | 9.29 | **9.42** | 8.39 | +0.90 | 9.415 | 10 | ok |
| L_middle | C6 | 1.075 | 0.0 (kept) | 4.0 | 6.48 | **6.61** | 5.80 | +0.68 | 6.606 | 10 | ok |
| L_index | D6 | 1.166 | 0.0 (kept) | 4.0 | 11.86 | **11.98** | 10.76 | +1.10 | 11.978 | 10 | above the pad limit |
| L_thumb | E6 | 1.055 | 0.0 (kept) | 4.0 | 15.30 | **15.42** | 12.71 | +2.59 | 15.424 | 12 | above the pad limit |
| R_thumb | F6 | 1.143 | 0.0 (kept) | 4.0 | 9.38 | **9.50** | 8.56 | +0.82 | 9.502 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.20; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.57 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_index 11.86 mm above the 10 mm pad limit; L_thumb 15.30 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-80-r2_air_capped.stl; holes and window closed): 2909 Hz = 2.08 × F6 on a 1.5 mm grid of 24073 cells (2 mm grid: 2907 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.568 + voicing pocket 0.138) = 78.7057 cm³ against the kernel's 78.7056 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2347 cm³ (+0.0168 %), air mesh 81.2333 cm³ (+0.0151 %), against the model target 81.2211 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.50 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 617b869f0b10; recomputed from the record: 617b869f0b10 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 32.8 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.40 mm (at least 0.8 mm); windway roof 3.00 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (L_pinky), largest chimney error -0.0021 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 32.1 mm to the opposite wall, 34.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.90° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.83 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 29.7 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
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
- Voicing hash `7b411d5079d7`. Window: Teardrop 9.65 × 11.10 mm, 81.2 mm², wall 4.0 mm. Windway: exit 1.20 × 11.10 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 95.00 cm³ (capped air). Measured on the STL: 96.463 cm³ against the model target 96.442 cm³ (+0.023 %). Cavity mesh 93.13 cm³ (3.26 cm³ of air in the holes, 0.03 cm³ of tube wall). Cavity spine length 83.1 mm. Plastic 48.5 cm³.
- Fitted constants: η_w 0.8604 (measured), k_hole 1.1804, position factors of shape `P0`. A4 error with the kept volume: -39.0 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.101 | 0.0 (kept) | 4.0 | 4.41 | **4.53** | 3.72 | +0.68 | 4.528 | 10 | ok |
| sub2 | C5 | 1.015 | 1.5 (kept) | 5.5 | 3.30 | **3.42** | 3.06 | +0.24 | 3.423 | 10 | ok |
| R_pinky | D5 | 0.874 | 0.0 (kept) | 4.0 | 5.94 | **6.06** | 4.65 | +1.28 | 6.058 | 10 | ok |
| R_ring | E5 | 0.937 | 0.0 (kept) | 4.0 | 6.68 | **6.80** | 5.42 | +1.25 | 6.799 | 10 | ok |
| R_middle | F5 | 0.975 | 0.0 (kept) | 4.0 | 4.45 | **4.57** | 3.85 | +0.60 | 4.571 | 10 | ok |
| R_index | G5 | 1.101 | 0.0 (kept) | 4.0 | 7.66 | **7.78** | 6.87 | +0.79 | 7.779 | 10 | ok |
| L_pinky | A5 | 1.214 | 0.0 (kept) | 4.0 | 8.46 | **8.58** | 8.07 | +0.39 | 8.584 | 10 | ok |
| L_ring | B5 | 1.135 | 0.0 (kept) | 4.0 | 10.64 | **10.76** | 9.52 | +1.12 | 10.761 | 10 | above the pad limit |
| L_middle | C6 | 1.075 | 0.0 (kept) | 4.0 | 7.37 | **7.49** | 6.53 | +0.84 | 7.488 | 10 | ok |
| L_index | D6 | 1.166 | 0.0 (kept) | 4.0 | 13.62 | **13.74** | 12.25 | +1.37 | 13.741 | 10 | above the pad limit |
| L_thumb | E6 | 1.055 | 0.0 (kept) | 4.0 | 17.61 | **17.73** | 14.51 | +3.10 | 17.734 | 12 | above the pad limit |
| R_thumb | F6 | 1.143 | 0.0 (kept) | 4.0 | 10.71 | **10.83** | 9.69 | +1.01 | 10.829 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.18; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.49 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_ring 10.64 mm above the 10 mm pad limit; L_index 13.62 mm above the 10 mm pad limit; L_thumb 17.61 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-95-r2_air_capped.stl; holes and window closed): 2750 Hz = 1.97 × F6 on a 1.5 mm grid of 28579 cells (2 mm grid: 2747 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 92.972 + voicing pocket 0.157) = 93.1286 cm³ against the kernel's 93.1285 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 96.4633 cm³ (+0.0226 %), air mesh 96.4616 cm³ (+0.0208 %), against the model target 96.4416 cm³ (V0 95.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 2.92 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 7b411d5079d7; recomputed from the record: 7b411d5079d7 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 11.102 mm, 81.14 mm² (record 9.650 × 11.102, 81.15); windway exit 1.200 × 11.102 mm, inlet 1.560 × 11.102 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.60 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 35.1 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.21 mm (at least 0.8 mm); windway roof 3.00 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (R_middle), largest chimney error -0.0023 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 1.500 mm (kernel 1.5), wall 1.198 mm, 35.7 mm to the opposite wall, 37.5 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.85 mm (sub1 to L_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 29.8 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
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
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.6 mm from R middle (ok -8 to +3), L thumb +15.3 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2.md`.

### P1-80-r2

*Round 2 of a printed body.*

- Result: **UNEXPECTED FAILURES: hole_spacing**; expected by the notes: hole_limits[fitted] (fail); 4 warnings (soft ergonomic checks, never failures): ergo_hand_span, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side.
- Voicing hash `617b869f0b10`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.242 cm³ against the model target 81.221 cm³ (+0.026 %). Cavity mesh 78.71 cm³ (2.49 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 110.3 mm. Plastic 48.8 cm³.
- Fitted constants: η_w 0.8615 (measured), k_hole 1.1804, position factors of shape `P1`. A4 error with the kept volume: -37.8 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.112 | 0.0 (kept) | 4.0 | 3.88 | **4.00** | 3.34 | +0.54 | 4.000 | 10 | ok |
| sub2 | C5 | 1.006 | 3.0 (kept) | 7.0 | 3.27 | **3.39** | 3.06 | +0.21 | 3.388 | 10 | ok |
| R_pinky | D5 | 0.872 | 0.0 (kept) | 4.0 | 5.25 | **5.37** | 4.16 | +1.09 | 5.372 | 10 | ok |
| R_ring | E5 | 0.941 | 0.0 (kept) | 4.0 | 5.86 | **5.98** | 4.83 | +1.03 | 5.984 | 10 | ok |
| R_middle | F5 | 0.982 | 0.0 (kept) | 4.0 | 3.93 | **4.06** | 3.45 | +0.48 | 4.057 | 10 | ok |
| R_index | G5 | 1.094 | 0.0 (kept) | 4.0 | 6.76 | **6.88** | 6.09 | +0.66 | 6.881 | 10 | ok |
| L_pinky | A5 | 1.214 | 0.0 (kept) | 4.0 | 7.42 | **7.54** | 7.14 | +0.28 | 7.541 | 10 | ok |
| L_ring | B5 | 1.141 | 0.0 (kept) | 4.0 | 9.25 | **9.37** | 8.39 | +0.86 | 9.374 | 10 | ok |
| L_middle | C6 | 1.063 | 0.0 (kept) | 4.0 | 6.54 | **6.66** | 5.80 | +0.73 | 6.659 | 10 | ok |
| L_index | D6 | 1.173 | 0.0 (kept) | 4.0 | 11.80 | **11.92** | 10.76 | +1.05 | 11.925 | 10 | above the pad limit |
| L_thumb | E6 | 1.049 | 0.0 (kept) | 4.0 | 15.38 | **15.50** | 12.71 | +2.66 | 15.499 | 12 | above the pad limit |
| R_thumb | F6 | 1.165 | 0.0 (kept) | 4.0 | 9.25 | **9.37** | 8.56 | +0.69 | 9.371 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.20; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.13 x F6: below 1.3, so a FEM check of the top fingerings is required (the kernel's own status: needs_fem). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_index 11.80 mm above the 10 mm pad limit; L_thumb 15.38 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P1-80-r2_air_capped.stl; holes and window closed): 2260 Hz = 1.62 × F6 on a 1.5 mm grid of 24084 cells (2 mm grid: 2249 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.557 + voicing pocket 0.154) = 78.7105 cm³ against the kernel's 78.7104 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2418 cm³ (+0.0255 %), air mesh 81.2407 cm³ (+0.0242 %), against the model target 81.2210 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 4.78 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 617b869f0b10; recomputed from the record: 617b869f0b10 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 31.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.67 mm (at least 0.8 mm); windway roof 3.00 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_index), largest chimney error -0.0039 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 24.0 mm to the opposite wall, 40.8 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.79° (L_middle); limit 2.0° |
| `hole_spacing` | FAIL | smallest edge gap 2.81 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -10.2 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +10.7 mm (35 % of the half section there); the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); edge gap sub1 to L_ring is 2.81 mm, under 3.4 mm, with the new diameters at the round-1 positions; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 21.2 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 2.71 mm |
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
- Voicing hash `617b869f0b10`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.238 cm³ against the model target 81.221 cm³ (+0.021 %). Cavity mesh 78.51 cm³ (2.69 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 125.1 mm. Plastic 51.5 cm³.
- Fitted constants: η_w 0.8615 (measured), k_hole 1.1804, position factors of shape `P2`. A4 error with the kept volume: -37.8 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.042 | 0.0 (kept) | 4.0 | 4.05 | **4.17** | 3.34 | +0.71 | 4.174 | 10 | ok |
| sub2 | C5 | 0.957 | 3.0 (kept) | 7.0 | 3.37 | **3.49** | 3.06 | +0.31 | 3.488 | 10 | ok |
| R_pinky | D5 | 0.825 | 0.0 (kept) | 4.0 | 5.46 | **5.58** | 4.16 | +1.30 | 5.583 | 10 | ok |
| R_ring | E5 | 0.905 | 0.0 (kept) | 4.0 | 6.03 | **6.15** | 4.83 | +1.20 | 6.154 | 10 | ok |
| R_middle | F5 | 0.917 | 0.0 (kept) | 4.0 | 4.12 | **4.24** | 3.45 | +0.67 | 4.243 | 10 | ok |
| R_index | G5 | 1.039 | 0.0 (kept) | 4.0 | 7.02 | **7.14** | 6.09 | +0.92 | 7.141 | 10 | ok |
| L_pinky | A5 | 1.166 | 0.0 (kept) | 4.0 | 7.65 | **7.77** | 7.14 | +0.50 | 7.768 | 10 | ok |
| L_ring | B5 | 1.084 | 0.0 (kept) | 4.0 | 9.62 | **9.74** | 8.39 | +1.23 | 9.745 | 10 | ok |
| L_middle | C6 | 0.980 | 0.0 (kept) | 4.0 | 6.93 | **7.05** | 5.80 | +1.13 | 7.055 | 10 | ok |
| L_index | D6 | 1.121 | 0.0 (kept) | 4.0 | 12.21 | **12.34** | 10.76 | +1.46 | 12.337 | 10 | above the pad limit |
| L_thumb | E6 | 1.000 | 0.0 (kept) | 4.0 | 15.94 | **16.07** | 12.71 | +3.23 | 16.067 | 12 | above the pad limit |
| R_thumb | F6 | 1.083 | 0.0 (kept) | 4.0 | 9.75 | **9.87** | 8.56 | +1.19 | 9.871 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.17; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.99 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_index 12.21 mm above the 10 mm pad limit; L_thumb 15.94 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P2-80-r2_air_capped.stl; holes and window closed): 1947 Hz = 1.39 × F6 on a 1.5 mm grid of 24095 cells (2 mm grid: 1936 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.330 + voicing pocket 0.177) = 78.5065 cm³ against the kernel's 78.5063 cm³: +0.0002 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2381 cm³ (+0.0213 %), air mesh 81.2338 cm³ (+0.0160 %), against the model target 81.2208 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.75 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 617b869f0b10; recomputed from the record: 617b869f0b10 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 31.0 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 3.17 mm (at least 0.8 mm); windway roof 3.00 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (R_pinky), largest chimney error -0.0008 mm (sub1); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 17.3 mm to the opposite wall, 45.7 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.10° (R_index); limit 2.0° |
| `hole_spacing` | FAIL | smallest edge gap 2.54 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -8.7 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.6 mm (35 % of the half section there); the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); edge gap sub1 to L_ring is 2.54 mm, under 3.4 mm, with the new diameters at the round-1 positions; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 17.1 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 2.95 mm |
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

### P4-80-r2

*Round 2 of a printed body.*

- Result: **UNEXPECTED FAILURES: hole_spacing**; expected by the notes: hole_limits[fitted] (fail); 2 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hole_lean_side.
- Voicing hash `617b869f0b10`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.214 cm³ against the model target 81.220 cm³ (-0.007 %). Cavity mesh 78.33 cm³ (2.87 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 132.2 mm. Plastic 52.0 cm³.
- Fitted constants: η_w 0.8615 (measured), k_hole 1.1804, position factors of shape `P4` (not fitted: every factor is 1). A4 error with the kept volume: -37.8 cents. **Note:** shape 'P4' has no fitted position factors: psi = 1 for every hole.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.000 | 0.0 (kept) | 4.0 | 4.17 | **4.29** | 3.34 | +0.83 | 4.291 | 10 | ok |
| sub2 | C5 | 1.000 | 3.0 (kept) | 7.0 | 3.28 | **3.40** | 3.06 | +0.22 | 3.400 | 10 | ok |
| R_pinky | D5 | 1.000 | 0.0 (kept) | 4.0 | 4.76 | **4.89** | 4.16 | +0.60 | 4.887 | 10 | ok |
| R_ring | E5 | 1.000 | 0.0 (kept) | 4.0 | 5.61 | **5.73** | 4.83 | +0.78 | 5.735 | 10 | ok |
| R_middle | F5 | 1.000 | 0.0 (kept) | 4.0 | 3.89 | **4.01** | 3.45 | +0.43 | 4.008 | 10 | ok |
| R_index | G5 | 1.000 | 0.0 (kept) | 4.0 | 7.23 | **7.35** | 6.09 | +1.13 | 7.349 | 10 | ok |
| L_pinky | A5 | 1.000 | 0.0 (kept) | 4.0 | 8.59 | **8.71** | 7.14 | +1.45 | 8.713 | 10 | ok |
| L_ring | B5 | 1.000 | 0.0 (kept) | 4.0 | 10.24 | **10.36** | 8.39 | +1.84 | 10.360 | 10 | above the pad limit |
| L_middle | C6 | 1.000 | 0.0 (kept) | 4.0 | 6.83 | **6.95** | 5.80 | +1.02 | 6.948 | 10 | ok |
| L_index | D6 | 1.000 | 0.0 (kept) | 4.0 | 13.36 | **13.48** | 10.76 | +2.60 | 13.479 | 10 | above the pad limit |
| L_thumb | E6 | 1.000 | 0.0 (kept) | 4.0 | 15.92 | **16.04** | 12.71 | +3.20 | 16.039 | 12 | above the pad limit |
| R_thumb | F6 | 1.000 | 0.0 (kept) | 4.0 | 10.34 | **10.46** | 8.56 | +1.78 | 10.463 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.15; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.94 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_ring 10.24 mm above the 10 mm pad limit; L_index 13.36 mm above the 10 mm pad limit; L_thumb 15.92 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P4-80-r2_air_capped.stl; holes and window closed): 1893 Hz = 1.36 × F6 on a 1.5 mm grid of 24075 cells (2 mm grid: 1887 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.170 + voicing pocket 0.158) = 78.3277 cm³ against the kernel's 78.3275 cm³: +0.0002 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2144 cm³ (-0.0066 %), air mesh 81.2421 cm³ (+0.0274 %), against the model target 81.2198 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.98 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 617b869f0b10; recomputed from the record: 617b869f0b10 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 29.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 3.20 mm (at least 0.8 mm); windway roof 3.00 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (sub1), largest chimney error -0.0044 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 22.0 mm to the opposite wall, 42.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.05° (L_index); limit 2.0° |
| `hole_spacing` | FAIL | smallest edge gap 2.17 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -9.0 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there); the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); edge gap sub1 to L_ring is 2.17 mm, under 3.4 mm, with the new diameters at the round-1 positions; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 16.4 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.30 mm |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.7 / 18.2 / 17.1, right 17.4 / 18.3 / 17.5 mm |
| `ergo_hand_span` | pass | left 50.1 mm, right 50.4 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.9, right 51.4 mm |
| `ergo_arch` | pass | left ring +3.0, left middle +3.2, right ring +3.3, right middle +3.5 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +1.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 18.6 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.1°, right line +12.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 18.6 mm across (toward the player), +0.9 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 9.5 mm, +0° off the normal of the left-hand line (+9.2 mm forward, +0.0 mm toward the index); at the outer skin 11.0 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.9 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | pass | land past the pinky holes, from the hole edge along the hand axis: bulb 14.4 mm (centre 18.8), tail 11.3 mm (centre 13.8); ok at least 10 mm |
| `ergo_hole_lean_end` | pass | lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +13°, L_ring +5°, L_middle -3°, L_index -12°, R_pinky +19°, R_ring +14°, R_middle +9°, R_index +3°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 10° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -5°, L_ring -3°, L_middle +4°, L_index +20°, R_pinky -10°, R_ring -4°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.4 mm from R middle (ok -8 to +3), L thumb +9.8 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2.md`.

### P0-88-r2

*Never printed: sized from the fitted model only.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `cd934d015aea`. Window: Teardrop 9.65 × 10.44 mm, 77.4 mm², wall 4.0 mm. Windway: exit 1.20 × 10.44 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 88.00 cm³ (capped air). Measured on the STL: 89.357 cm³ against the model target 89.338 cm³ (+0.021 %). Cavity mesh 86.40 cm³ (2.88 cm³ of air in the holes, 0.02 cm³ of tube wall). Cavity spine length 81.0 mm. Plastic 46.6 cm³.
- Fitted constants: η_w 0.8601 (fallback), k_hole 1.1804, position factors of shape `P0`. A4 error with the kept volume: +0.0 cents. **Note:** voicing hash was never measured: eta_w_fallback used.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.101 | 0.0 | 4.0 | 3.75 | **3.88** | – | – | 3.877 | 10 | ok |
| sub2 | C5 | 1.015 | 1.0 | 5.0 | 3.04 | **3.16** | – | – | 3.160 | 10 | ok |
| R_pinky | D5 | 0.874 | 0.0 | 4.0 | 5.61 | **5.74** | – | – | 5.737 | 10 | ok |
| R_ring | E5 | 0.937 | 0.0 | 4.0 | 6.31 | **6.43** | – | – | 6.432 | 10 | ok |
| R_middle | F5 | 0.975 | 0.0 | 4.0 | 4.22 | **4.34** | – | – | 4.342 | 10 | ok |
| R_index | G5 | 1.101 | 0.0 | 4.0 | 7.23 | **7.35** | – | – | 7.349 | 10 | ok |
| L_pinky | A5 | 1.214 | 0.0 | 4.0 | 7.98 | **8.10** | – | – | 8.103 | 10 | ok |
| L_ring | B5 | 1.135 | 0.0 | 4.0 | 10.02 | **10.14** | – | – | 10.138 | 10 | above the pad limit |
| L_middle | C6 | 1.075 | 0.0 | 4.0 | 6.96 | **7.08** | – | – | 7.081 | 10 | ok |
| L_index | D6 | 1.166 | 0.0 | 4.0 | 12.80 | **12.93** | – | – | 12.925 | 10 | above the pad limit |
| L_thumb | E6 | 1.055 | 0.0 | 4.0 | 16.54 | **16.67** | – | – | 16.666 | 12 | above the pad limit |
| R_thumb | F6 | 1.143 | 0.0 | 4.0 | 10.09 | **10.22** | – | – | 10.216 | 12 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.75; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.52 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_ring 10.02 mm above the 10 mm pad limit; L_index 12.80 mm above the 10 mm pad limit; L_thumb 16.54 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-88-r2_air_capped.stl; holes and window closed): 2821 Hz = 2.02 × F6 on a 1.5 mm grid of 26482 cells (2 mm grid: 2812 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 86.248 + voicing pocket 0.154) = 86.4014 cm³ against the kernel's 86.4014 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 89.3571 cm³ (+0.0211 %), air mesh 89.3548 cm³ (+0.0185 %), against the model target 89.3382 cm³ (V0 88.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 4.11 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash cd934d015aea; recomputed from the record: cd934d015aea |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 10.440 mm, 77.43 mm² (record 9.650 × 10.440, 77.44); windway exit 1.200 × 10.440 mm, inlet 1.560 × 10.440 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.70 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 34.2 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.29 mm (at least 0.8 mm); windway roof 3.00 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (L_pinky), largest chimney error -0.0022 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 1.000 mm (kernel 1.0), wall 1.198 mm, 35.2 mm to the opposite wall, 37.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.92° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.04 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 29.5 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 15.7 / 16.1 / 17.1 mm, right 12.3 / 11.8 / 15.4 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.5 / 17.5 / 18.8, right 13.7 / 12.9 / 16.7 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 30.1 mm, right 28.0 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 32.6, right 30.2 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -5.9, left middle +9.8, right ring -4.6, right middle +6.5 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 27.2 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 27.2 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 9.6 mm, -115° off the normal of the left-hand line (-3.9 mm forward, -8.5 mm toward the index); at the outer skin 10.2 mm; sub2 from R_middle: 7.8 mm, +38° off the normal of the right-hand line (+6.1 mm forward, +4.8 mm toward the index); at the outer skin 8.3 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.7 mm (centre 11.8), tail 8.7 mm (centre 11.6); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.4 mm from R middle (ok -8 to +3), L thumb +15.0 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2.md`.

