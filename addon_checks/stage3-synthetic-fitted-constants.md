# Stage 3 · Round 2 corrected bodies: generation report

> **SYNTHETIC CONSTANTS.** This stage was sized from a fitted-constants file that is marked synthetic: invented truth values, not measurements of printed bodies. The report shows that the Stage 3 generator works. Do not print these bodies.

Written by `ocarina_addon/headless.py -- stage3 --calibration calibration/synthetic-fitted-constants.toml` on 2026-11-18. Every measured number comes from the STL file of the body, read back from disk. Run time 293 s for 7 bodies.

Result: **7 of 7 bodies have no unexpected failure**.

- Sized from the fitted-constants file `calibration/synthetic-fitted-constants.toml`: k_hole 1.1723 (profile estimate), hole offset -0.122 mm (printed minus designed), volume factor 0.9854 (printed / designed), η_w fallback 0.8601; η_w measured for the voicing hashes `16410d2e6a1b` 0.8585, `b4620fbf3d67` 0.8615, `7e2fd3e0bf07` 0.8604.
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
| P0-65-r2 | P0 | 65.0 cm³ | `16410d2e6a1b` | Teardrop 9.65 × 6.96 mm, 46.5 mm² | 1.20 × 6.96 mm | 66.008 cm³ (+0.014 %) | 2.23 × F6, pass (c/(2L): 1.69) | 43.0 cm³; 53 g | 77 g | none | 11 (taped test body) |
| P0-80-r2 | P0 | 80.0 cm³ | `b4620fbf3d67` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.235 cm³ (+0.017 %) | 2.08 × F6, pass (c/(2L): 1.57) | 49.5 cm³; 61 g | 84 g | hole_limits[fitted] (expected) | 11 (taped test body) |
| P0-95-r2 | P0 | 95.0 cm³ | `7e2fd3e0bf07` | Teardrop 9.65 × 11.10 mm, 81.2 mm² | 1.20 × 11.10 mm | 96.464 cm³ (+0.023 %) | 1.97 × F6, pass (c/(2L): 1.49) | 56.3 cm³; 70 g | 91 g | hole_limits[fitted] (expected) | 11 (taped test body) |
| P1-80-r2 | P1 | 80.0 cm³ | `b4620fbf3d67` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.241 cm³ (+0.024 %) | 1.62 × F6, pass (c/(2L): 1.13) | 54.2 cm³; 67 g | 91 g | hole_limits[fitted] (expected) | 4 |
| P2-80-r2 | P2 | 80.0 cm³ | `b4620fbf3d67` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.235 cm³ (+0.017 %) | 1.40 × F6, pass (c/(2L): 0.99) | 57.2 cm³; 71 g | 97 g | hole_limits[fitted] (expected) | 5 |
| P4-80-r2 | P4 | 80.0 cm³ | `b4620fbf3d67` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 81.218 cm³ (-0.003 %) | 1.36 × F6, pass (c/(2L): 0.94) | 57.4 cm³; 71 g | 99 g | hole_limits[fitted] (expected) | 2 |
| P0-88-r2 | P0 | 88.0 cm³ | `dfde809794fe` | Teardrop 9.65 × 10.44 mm, 77.4 mm² | 1.20 × 10.44 mm | 89.358 cm³ (+0.021 %) | 2.02 × F6, pass (c/(2L): 1.52) | 53.7 cm³; 67 g | 88 g | hole_limits[fitted] (expected) | 11 (taped test body) |

*Capped air* is compared with the target of the model: V0 for a round-1 body, the stub volume for a stub, and in Stage 3 V0 divided by the fitted volume factor, with the holes drawn at their CAD diameters. *First cavity mode* is the computed desk check with closed holes, which gives the verdict; the number in brackets is the kernel's c/(2L) estimate from the length of the chamber, the lowest estimate, shown for information (it is 30 to 44 % low for these shapes, docs/06 section 3.10). *Solid PLA mass* is the plastic volume of the STL at 1.24 g/cm³, with no supports, brim or infill saving; the doc 04 figure includes about 12 % for supports and a brim.

Total for the 7 bodies of this stage: 460 g of solid PLA, 516 g with 12 % for supports and a brim. The doc 04 budget for this stage is 627 g. The generated bodies are lighter than the budget; the doc 04 masses were estimates made before any body was built.

## Unexpected failures

None.

## Expected failures

Failures that the plan expects (the pad-limit checks: doc 04 prints these holes on purpose, "the real limit is unknown"). They do not stop a stage.

- P0-80-r2 `hole_limits[fitted]` (fail): L_thumb 13.00 mm above the 12 mm pad limit; R_thumb 14.15 mm above the 12 mm pad limit
- P0-95-r2 `hole_limits[fitted]` (fail): L_middle 11.05 mm above the 10 mm pad limit; L_thumb 14.95 mm above the 12 mm pad limit; R_thumb 16.27 mm above the 12 mm pad limit; L_pinky 10.27 mm above the 10 mm pad limit
- P1-80-r2 `hole_limits[fitted]` (fail): L_thumb 12.94 mm above the 12 mm pad limit; R_thumb 14.20 mm above the 12 mm pad limit
- P2-80-r2 `hole_limits[fitted]` (fail): L_thumb 13.38 mm above the 12 mm pad limit; R_thumb 14.74 mm above the 12 mm pad limit
- P4-80-r2 `hole_limits[fitted]` (fail): L_middle 10.20 mm above the 10 mm pad limit; L_thumb 13.30 mm above the 12 mm pad limit; R_thumb 15.85 mm above the 12 mm pad limit; L_pinky 10.30 mm above the 10 mm pad limit
- P0-88-r2 `hole_limits[fitted]` (fail): L_middle 10.40 mm above the 10 mm pad limit; L_thumb 14.05 mm above the 12 mm pad limit; R_thumb 15.29 mm above the 12 mm pad limit

### Round-hole verdict (doc 04, Gate 2)

The rule of Gate 2, applied to the holes of this stage: a ladder step fails this verdict if a fitted hole needs more than 10 mm (finger) or 12 mm (thumb).

- P0-80-r2: L_thumb needs 13.00 mm (limit 12 mm)
- P0-80-r2: R_thumb needs 14.15 mm (limit 12 mm)
- P0-95-r2: L_middle needs 11.05 mm (limit 10 mm)
- P0-95-r2: L_thumb needs 14.95 mm (limit 12 mm)
- P0-95-r2: R_thumb needs 16.27 mm (limit 12 mm)
- P0-95-r2: L_pinky needs 10.27 mm (limit 10 mm)
- P1-80-r2: L_thumb needs 12.94 mm (limit 12 mm)
- P1-80-r2: R_thumb needs 14.20 mm (limit 12 mm)
- P2-80-r2: L_thumb needs 13.38 mm (limit 12 mm)
- P2-80-r2: R_thumb needs 14.74 mm (limit 12 mm)
- P4-80-r2: L_middle needs 10.20 mm (limit 10 mm)
- P4-80-r2: L_thumb needs 13.30 mm (limit 12 mm)
- P4-80-r2: R_thumb needs 15.85 mm (limit 12 mm)
- P4-80-r2: L_pinky needs 10.30 mm (limit 10 mm)
- P0-88-r2: L_middle needs 10.40 mm (limit 10 mm)
- P0-88-r2: L_thumb needs 14.05 mm (limit 12 mm)
- P0-88-r2: R_thumb needs 15.29 mm (limit 12 mm)

## Warnings

Soft ergonomic checks outside their range. They are measurements for the owner to judge. A warning is never a failure.

- P0-65-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2.md`.
- P0-80-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2.md`.
- P0-95-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2.md`.
- P1-80-r2 `ergo_hand_span`: hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.2 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.3, right 51.9 mm
- P1-80-r2 `ergo_rest_space`: the bulb end is 5.7 mm too short: 4.3 mm past the L pinky hole edge; the tail end is 5.7 mm too short: 4.3 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 4.3 mm (centre 8.8), tail 4.3 mm (centre 7.0); ok at least 10 mm
- P1-80-r2 `ergo_hole_lean_end`: L_pinky leans 37° toward the bulb end; R_pinky leans 30° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +37°, L_ring +15°, L_middle -0°, L_index -14°, R_pinky +30°, R_ring +15°, R_middle +11°, R_index +5°; ok up to 20°
- P1-80-r2 `ergo_hole_lean_side`: R_pinky leans 12° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -0°, L_ring +0°, L_middle +4°, L_index +17°, R_pinky -12°, R_ring -3°, R_middle +7°, R_index +22°; ok up to 45° toward it and up to 5° away
- P2-80-r2 `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.5 mm. Measured: left 17.1 / 17.6 / 16.5 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.4 / 18.8 / 17.5, right 17.4 / 18.0 / 16.9 mm
- P2-80-r2 `ergo_hand_span`: hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.8 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.2, right 51.0 mm
- P2-80-r2 `ergo_rest_space`: the bulb end is 1.7 mm too short: 8.3 mm past the L pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 8.3 mm (centre 13.0), tail 11.7 mm (centre 14.5); ok at least 10 mm
- P2-80-r2 `ergo_hole_lean_end`: L_pinky leans 29° toward the bulb end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +29°, L_ring +11°, L_middle -6°, L_index -19°, R_pinky +12°, R_ring +8°, R_middle +8°, R_index +9°; ok up to 20°
- P2-80-r2 `ergo_hole_lean_side`: R_pinky leans 7° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +2°, L_ring +1°, L_middle +1°, L_index +12°, R_pinky -7°, R_ring -3°, R_middle +5°, R_index +19°; ok up to 45° toward it and up to 5° away
- P4-80-r2 `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.7 / 18.2 / 17.1, right 17.4 / 18.3 / 17.5 mm
- P4-80-r2 `ergo_hole_lean_side`: R_pinky leans 10° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -5°, L_ring -3°, L_middle +4°, L_index +20°, R_pinky -10°, R_ring -4°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away
- P0-88-r2: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2.md`.

## Per body

### P0-65-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `16410d2e6a1b`. Window: Teardrop 9.65 × 6.96 mm, 46.5 mm², wall 4.0 mm. Windway: exit 1.20 × 6.96 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 40°; windway +5° against the body; neck standing 15° off the body, the pipe lowered 10° inside it; pocket blend 12 mm.
- Volume: V0 65.00 cm³ (capped air). Measured on the STL: 66.008 cm³ against the model target 65.999 cm³ (+0.014 %). Cavity mesh 64.22 cm³ (1.81 cm³ of air in the holes, 0.09 cm³ of tube wall). Cavity spine length 73.3 mm. Plastic 43.0 cm³.
- Fitted constants: η_w 0.8585 (measured), k_hole 1.1723, position factors of shape `P0`. A4 error with the kept volume: -40.9 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.098 | 0.5 (kept) | 4.5 | 3.56 | **3.68** | 3.08 | +0.48 | 3.677 | 10 | ok |
| sub2 | C5 | 1.012 | 5.0 (kept) | 9.0 | 3.17 | **3.29** | 3.03 | +0.15 | 3.293 | 10 | ok |
| R_pinky | D5 | 0.871 | 0.0 (kept) | 4.0 | 4.52 | **4.64** | 3.64 | +0.88 | 4.645 | 10 | ok |
| R_ring | E5 | 0.933 | 0.0 (kept) | 4.0 | 5.06 | **5.18** | 4.22 | +0.84 | 5.184 | 10 | ok |
| R_middle | F5 | 0.972 | 0.0 (kept) | 4.0 | 3.43 | **3.56** | 3.03 | +0.40 | 3.557 | 10 | ok |
| R_index | G5 | 1.096 | 0.0 (kept) | 4.0 | 5.77 | **5.89** | 5.29 | +0.48 | 5.894 | 10 | ok |
| L_ring | A5 | 1.133 | 0.0 (kept) | 4.0 | 6.66 | **6.78** | 6.18 | +0.48 | 6.783 | 10 | ok |
| L_middle | B5 | 1.075 | 0.0 (kept) | 4.0 | 8.21 | **8.33** | 7.24 | +0.98 | 8.335 | 10 | ok |
| L_index | C6 | 1.155 | 0.0 (kept) | 4.0 | 5.28 | **5.40** | 5.05 | +0.23 | 5.401 | 10 | ok |
| L_thumb | D6 | 1.031 | 0.0 (kept) | 4.0 | 11.01 | **11.13** | 9.22 | +1.79 | 11.135 | 12 | ok |
| R_thumb | E6 | 1.158 | 0.0 (kept) | 4.0 | 11.98 | **12.10** | 10.87 | +1.11 | 12.100 | 12 | ok |
| L_pinky | F6 | 1.202 | 0.0 (kept) | 4.0 | 7.70 | **7.82** | 7.39 | +0.30 | 7.818 | 10 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.26; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.69 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | pass | all holes inside floor and pad limits |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-65-r2_air_capped.stl; holes and window closed): 3109 Hz = 2.23 × F6 on a 1.5 mm grid of 19537 cells (2 mm grid: 3099 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 64.003 + voicing pocket 0.215) = 64.2177 cm³ against the kernel's 64.2172 cm³: +0.0007 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 66.0084 cm³ (+0.0136 %), air mesh 66.0072 cm³ (+0.0118 %), against the model target 65.9995 cm³ (V0 65.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 19 Booleans, all manifold, each volume change as expected (largest deviation 12.43 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 16410d2e6a1b; recomputed from the record: 16410d2e6a1b |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 6.959 mm, 46.47 mm² (record 9.650 × 6.959, 46.47); windway exit 1.200 × 6.959 mm, inlet 3.000 × 6.959 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 6.959 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.48 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 29.4 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 41° steep seen from the rim, 10.1 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 3.80 mm (at least 0.8 mm); windway roof 2.99 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (sub2), largest chimney error -0.0058 mm (sub1); limit 0.05 mm |
| `inward_tubes` | pass | sub1: length 0.500 mm (kernel 0.5), wall 1.198 mm, 30.8 mm to the opposite wall, 30.8 mm to the labium, 23.8 mm to the nearest other tube; sub2: length 5.000 mm (kernel 5.0), wall 1.198 mm, 27.8 mm to the opposite wall, 29.8 mm to the labium, 23.8 mm to the nearest other tube |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.63 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: R_thumb, 29.1 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2320 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 2.45 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 3.5 to 7.5 mm beyond the flat part. Back corners beside the windway exit: 10.4 mm, meets the wall; 10.4 mm, meets the wall |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 27.6 / 14.2 / 14.6 mm, right 11.1 / 10.7 / 14.0 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 30.2 / 16.0 / 15.9, right 12.5 / 11.8 / 15.2 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 15.5 mm, right 25.3 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 17.2, right 27.6 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring +15.6, left middle +12.6, right ring -4.2, right middle +5.9 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines -136.0° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is -12.2 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line -107.5°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: -7.6 mm across (toward the player), +17.9 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_index: 8.7 mm, +30° off the normal of the left-hand line (+7.3 mm forward, +4.3 mm toward the index); at the outer skin 9.3 mm; sub2 from R_middle: 7.1 mm, +38° off the normal of the right-hand line (+5.5 mm forward, +4.3 mm toward the index); at the outer skin 7.5 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 16.8 mm (centre 20.7), tail 10.9 mm (centre 13.2); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +16°, L_ring +16°, L_middle +22°, L_index +3°, R_pinky +22°, R_ring +23°, R_middle +8°, R_index +14°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +11°, L_ring -29°, L_middle -3°, L_index -10°, R_pinky -27°, R_ring -5°, R_middle -10°, R_index +8°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +0.0 mm from R middle (ok -8 to +3), L thumb -8.2 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-65-r2/P0-65-r2.md`.

### P0-80-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `b4620fbf3d67`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 40°; windway +5° against the body; neck standing 15° off the body, the pipe lowered 10° inside it; pocket blend 12 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.235 cm³ against the model target 81.221 cm³ (+0.017 %). Cavity mesh 78.72 cm³ (2.48 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 78.5 mm. Plastic 49.5 cm³.
- Fitted constants: η_w 0.8615 (measured), k_hole 1.1723, position factors of shape `P0`. A4 error with the kept volume: -37.8 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.098 | 0.0 (kept) | 4.0 | 3.90 | **4.02** | 3.34 | +0.56 | 4.024 | 10 | ok |
| sub2 | C5 | 1.012 | 3.0 (kept) | 7.0 | 3.25 | **3.37** | 3.06 | +0.19 | 3.371 | 10 | ok |
| R_pinky | D5 | 0.871 | 0.0 (kept) | 4.0 | 5.24 | **5.36** | 4.16 | +1.08 | 5.361 | 10 | ok |
| R_ring | E5 | 0.933 | 0.0 (kept) | 4.0 | 5.88 | **6.00** | 4.83 | +1.04 | 6.002 | 10 | ok |
| R_middle | F5 | 0.972 | 0.0 (kept) | 4.0 | 3.95 | **4.07** | 3.45 | +0.50 | 4.073 | 10 | ok |
| R_index | G5 | 1.096 | 0.0 (kept) | 4.0 | 6.73 | **6.85** | 6.09 | +0.63 | 6.848 | 10 | ok |
| L_ring | A5 | 1.133 | 0.0 (kept) | 4.0 | 7.79 | **7.91** | 7.14 | +0.65 | 7.910 | 10 | ok |
| L_middle | B5 | 1.075 | 0.0 (kept) | 4.0 | 9.65 | **9.77** | 8.39 | +1.25 | 9.768 | 10 | ok |
| L_index | C6 | 1.155 | 0.0 (kept) | 4.0 | 6.13 | **6.25** | 5.80 | +0.33 | 6.254 | 10 | ok |
| L_thumb | D6 | 1.031 | 0.0 (kept) | 4.0 | 13.00 | **13.12** | 10.76 | +2.24 | 13.125 | 12 | above the pad limit |
| R_thumb | E6 | 1.158 | 0.0 (kept) | 4.0 | 14.15 | **14.27** | 12.71 | +1.44 | 14.272 | 12 | above the pad limit |
| L_pinky | F6 | 1.202 | 0.0 (kept) | 4.0 | 9.00 | **9.12** | 8.56 | +0.44 | 9.121 | 10 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.20; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.57 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_thumb 13.00 mm above the 12 mm pad limit; R_thumb 14.15 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-80-r2_air_capped.stl; holes and window closed): 2907 Hz = 2.08 × F6 on a 1.5 mm grid of 24091 cells (2 mm grid: 2901 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.494 + voicing pocket 0.226) = 78.7208 cm³ against the kernel's 78.7205 cm³: +0.0005 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2348 cm³ (+0.0166 %), air mesh 81.2335 cm³ (+0.0150 %), against the model target 81.2213 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.50 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash b4620fbf3d67; recomputed from the record: b4620fbf3d67 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 32.8 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 41° steep seen from the rim, 10.1 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 3.48 mm (at least 0.8 mm); windway roof 2.99 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_index), largest chimney error -0.0021 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 32.1 mm to the opposite wall, 34.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.83 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: R_thumb, 30.2 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 2.73 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 3.7 to 7.0 mm beyond the flat part. Back corners beside the windway exit: 10.1 mm, meets the wall; 10.1 mm, meets the wall |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 29.6 / 15.2 / 15.6 mm, right 11.9 / 11.5 / 14.9 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 32.2 / 17.0 / 17.0, right 13.3 / 12.6 / 16.2 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 16.6 mm, right 27.1 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 18.3, right 29.3 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring +16.6, left middle +13.5, right ring -4.5, right middle +6.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines -136.0° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is -13.0 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line -107.5°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: -8.1 mm across (toward the player), +19.2 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_index: 9.3 mm, +30° off the normal of the left-hand line (+7.8 mm forward, +4.6 mm toward the index); at the outer skin 9.9 mm; sub2 from R_middle: 7.6 mm, +38° off the normal of the right-hand line (+5.9 mm forward, +4.6 mm toward the index); at the outer skin 8.0 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 17.3 mm (centre 21.9), tail 11.1 mm (centre 13.8); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +16°, L_ring +16°, L_middle +22°, L_index +3°, R_pinky +22°, R_ring +23°, R_middle +8°, R_index +14°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +11°, L_ring -29°, L_middle -3°, L_index -10°, R_pinky -27°, R_ring -5°, R_middle -10°, R_index +8°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +0.0 mm from R middle (ok -8 to +3), L thumb -8.8 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-80-r2/P0-80-r2.md`.

### P0-95-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `7e2fd3e0bf07`. Window: Teardrop 9.65 × 11.10 mm, 81.2 mm², wall 4.0 mm. Windway: exit 1.20 × 11.10 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 40°; windway +5° against the body; neck standing 15° off the body, the pipe lowered 10° inside it; pocket blend 12 mm.
- Volume: V0 95.00 cm³ (capped air). Measured on the STL: 96.464 cm³ against the model target 96.442 cm³ (+0.023 %). Cavity mesh 93.15 cm³ (3.24 cm³ of air in the holes, 0.03 cm³ of tube wall). Cavity spine length 83.0 mm. Plastic 56.3 cm³.
- Fitted constants: η_w 0.8604 (measured), k_hole 1.1723, position factors of shape `P0`. A4 error with the kept volume: -39.0 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.098 | 0.0 (kept) | 4.0 | 4.40 | **4.53** | 3.72 | +0.68 | 4.526 | 10 | ok |
| sub2 | C5 | 1.012 | 1.5 (kept) | 5.5 | 3.30 | **3.42** | 3.06 | +0.24 | 3.422 | 10 | ok |
| R_pinky | D5 | 0.871 | 0.0 (kept) | 4.0 | 5.93 | **6.05** | 4.65 | +1.28 | 6.055 | 10 | ok |
| R_ring | E5 | 0.933 | 0.0 (kept) | 4.0 | 6.67 | **6.80** | 5.42 | +1.25 | 6.796 | 10 | ok |
| R_middle | F5 | 0.972 | 0.0 (kept) | 4.0 | 4.45 | **4.57** | 3.85 | +0.60 | 4.570 | 10 | ok |
| R_index | G5 | 1.096 | 0.0 (kept) | 4.0 | 7.65 | **7.78** | 6.87 | +0.79 | 7.776 | 10 | ok |
| L_ring | A5 | 1.133 | 0.0 (kept) | 4.0 | 8.89 | **9.01** | 8.07 | +0.82 | 9.009 | 10 | ok |
| L_middle | B5 | 1.075 | 0.0 (kept) | 4.0 | 11.05 | **11.17** | 9.52 | +1.53 | 11.170 | 10 | above the pad limit |
| L_index | C6 | 1.155 | 0.0 (kept) | 4.0 | 6.96 | **7.08** | 6.53 | +0.43 | 7.080 | 10 | ok |
| L_thumb | D6 | 1.031 | 0.0 (kept) | 4.0 | 14.95 | **15.07** | 12.25 | +2.70 | 15.072 | 12 | above the pad limit |
| R_thumb | E6 | 1.158 | 0.0 (kept) | 4.0 | 16.27 | **16.39** | 14.51 | +1.76 | 16.394 | 12 | above the pad limit |
| L_pinky | F6 | 1.202 | 0.0 (kept) | 4.0 | 10.27 | **10.39** | 9.69 | +0.57 | 10.387 | 10 | above the pad limit |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.18; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.49 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_middle 11.05 mm above the 10 mm pad limit; L_thumb 14.95 mm above the 12 mm pad limit; R_thumb 16.27 mm above the 12 mm pad limit; L_pinky 10.27 mm above the 10 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-95-r2_air_capped.stl; holes and window closed): 2745 Hz = 1.97 × F6 on a 1.5 mm grid of 28560 cells (2 mm grid: 2742 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 92.897 + voicing pocket 0.252) = 93.1491 cm³ against the kernel's 93.1488 cm³: +0.0004 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 96.4638 cm³ (+0.0228 %), air mesh 96.4616 cm³ (+0.0205 %), against the model target 96.4418 cm³ (V0 95.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 2.92 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 7e2fd3e0bf07; recomputed from the record: 7e2fd3e0bf07 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 11.102 mm, 81.14 mm² (record 9.650 × 11.102, 81.15); windway exit 1.200 × 11.102 mm, inlet 3.000 × 11.102 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 11.102 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.60 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 35.1 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 41° steep seen from the rim, 10.1 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 3.25 mm (at least 0.8 mm); windway roof 2.99 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (R_middle), largest chimney error -0.0023 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 1.500 mm (kernel 1.5), wall 1.198 mm, 35.6 mm to the opposite wall, 37.5 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.83 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: R_thumb, 30.5 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.32 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 4.0 to 7.1 mm beyond the flat part. Back corners beside the windway exit: 10.1 mm, meets the wall; 10.1 mm, meets the wall |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 31.3 / 16.1 / 16.5 mm, right 12.6 / 12.1 / 15.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 33.9 / 17.9 / 17.9, right 14.0 / 13.2 / 17.1 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 17.5 mm, right 28.7 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 19.2, right 30.9 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring +17.6, left middle +14.3, right ring -4.7, right middle +6.6 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines -136.0° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is -13.8 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line -107.5°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: -8.6 mm across (toward the player), +20.3 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_index: 9.9 mm, +30° off the normal of the left-hand line (+8.3 mm forward, +4.8 mm toward the index); at the outer skin 10.5 mm; sub2 from R_middle: 8.0 mm, +38° off the normal of the right-hand line (+6.2 mm forward, +4.9 mm toward the index); at the outer skin 8.4 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 17.7 mm (centre 22.9), tail 11.3 mm (centre 14.4); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +16°, L_ring +16°, L_middle +22°, L_index +3°, R_pinky +22°, R_ring +23°, R_middle +8°, R_index +14°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +11°, L_ring -29°, L_middle -3°, L_index -10°, R_pinky -27°, R_ring -5°, R_middle -10°, R_index +8°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +0.0 mm from R middle (ok -8 to +3), L thumb -9.3 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-95-r2/P0-95-r2.md`.

### P1-80-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 4 warnings (soft ergonomic checks, never failures): ergo_hand_span, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side.
- Voicing hash `b4620fbf3d67`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 40°; windway +5° against the body; neck standing 15° off the body, the pipe lowered 10° inside it; pocket blend 12 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.241 cm³ against the model target 81.221 cm³ (+0.024 %). Cavity mesh 78.73 cm³ (2.48 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 110.3 mm. Plastic 54.2 cm³.
- Fitted constants: η_w 0.8615 (measured), k_hole 1.1723, position factors of shape `P1`. A4 error with the kept volume: -37.8 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.108 | 0.0 (kept) | 4.0 | 3.88 | **4.00** | 3.34 | +0.53 | 3.999 | 10 | ok |
| sub2 | C5 | 1.004 | 3.0 (kept) | 7.0 | 3.27 | **3.39** | 3.06 | +0.21 | 3.388 | 10 | ok |
| R_pinky | D5 | 0.869 | 0.0 (kept) | 4.0 | 5.25 | **5.37** | 4.16 | +1.09 | 5.371 | 10 | ok |
| R_ring | E5 | 0.938 | 0.0 (kept) | 4.0 | 5.86 | **5.98** | 4.83 | +1.03 | 5.983 | 10 | ok |
| R_middle | F5 | 0.978 | 0.0 (kept) | 4.0 | 3.93 | **4.06** | 3.45 | +0.48 | 4.056 | 10 | ok |
| R_index | G5 | 1.089 | 0.0 (kept) | 4.0 | 6.76 | **6.88** | 6.09 | +0.66 | 6.880 | 10 | ok |
| L_ring | A5 | 1.133 | 0.0 (kept) | 4.0 | 7.79 | **7.91** | 7.14 | +0.64 | 7.908 | 10 | ok |
| L_middle | B5 | 1.081 | 0.0 (kept) | 4.0 | 9.60 | **9.73** | 8.39 | +1.21 | 9.727 | 10 | ok |
| L_index | C6 | 1.144 | 0.0 (kept) | 4.0 | 6.17 | **6.30** | 5.80 | +0.37 | 6.296 | 10 | ok |
| L_thumb | D6 | 1.037 | 0.0 (kept) | 4.0 | 12.94 | **13.06** | 10.76 | +2.18 | 13.065 | 12 | above the pad limit |
| R_thumb | E6 | 1.152 | 0.0 (kept) | 4.0 | 14.20 | **14.33** | 12.71 | +1.49 | 14.327 | 12 | above the pad limit |
| L_pinky | F6 | 1.223 | 0.0 (kept) | 4.0 | 8.88 | **9.00** | 8.56 | +0.32 | 9.005 | 10 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.20; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.13 x F6: below 1.3, so a FEM check of the top fingerings is required (the kernel's own status: needs_fem). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_thumb 12.94 mm above the 12 mm pad limit; R_thumb 14.20 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P1-80-r2_air_capped.stl; holes and window closed): 2264 Hz = 1.62 × F6 on a 1.5 mm grid of 24099 cells (2 mm grid: 2253 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.464 + voicing pocket 0.265) = 78.7285 cm³ against the kernel's 78.7280 cm³: +0.0006 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2411 cm³ (+0.0244 %), air mesh 81.2398 cm³ (+0.0229 %), against the model target 81.2213 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 4.89 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash b4620fbf3d67; recomputed from the record: b4620fbf3d67 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 31.7 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 41° steep seen from the rim, 10.1 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 3.80 mm (at least 0.8 mm); windway roof 2.99 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (R_ring), largest chimney error -0.0039 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 24.0 mm to the opposite wall, 40.8 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.93° (sub1); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.78 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 10.00 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -10.2 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +10.7 mm (35 % of the half section there); the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 22.4 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 2.70 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 4.0 to 7.6 mm beyond the flat part. Back corners beside the windway exit: 10.8 mm, meets the wall; 10.2 mm, meets the wall |
| `ergo_finger_pitch` | pass | left 17.2 / 17.6 / 16.9 mm, right 17.2 / 18.0 / 17.3 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.7 / 18.7 / 18.0, right 18.0 / 18.3 / 18.0 mm |
| `ergo_hand_span` | WARN | hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.2 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.3, right 51.9 mm |
| `ergo_arch` | pass | left ring +3.2, left middle +4.0, right ring +3.7, right middle +4.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +2.1° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 21.2 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +16.1°, right line +14.0° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 21.2 mm across (toward the player), -0.4 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 10.0 mm, +0° off the normal of the left-hand line (+9.9 mm forward, +0.0 mm toward the index); at the outer skin 11.3 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.6 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | the bulb end is 5.7 mm too short: 4.3 mm past the L pinky hole edge; the tail end is 5.7 mm too short: 4.3 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 4.3 mm (centre 8.8), tail 4.3 mm (centre 7.0); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | L_pinky leans 37° toward the bulb end; R_pinky leans 30° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +37°, L_ring +15°, L_middle -0°, L_index -14°, R_pinky +30°, R_ring +15°, R_middle +11°, R_index +5°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 12° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -0°, L_ring +0°, L_middle +4°, L_index +17°, R_pinky -12°, R_ring -3°, R_middle +7°, R_index +22°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.2 mm from R middle (ok -8 to +3), L thumb +8.6 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P1-80-r2/P1-80-r2.md`.

### P2-80-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 5 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side.
- Voicing hash `b4620fbf3d67`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 40°; windway +5° against the body; neck standing 15° off the body, the pipe lowered 10° inside it; pocket blend 12 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.235 cm³ against the model target 81.221 cm³ (+0.017 %). Cavity mesh 78.53 cm³ (2.67 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 125.1 mm. Plastic 57.2 cm³.
- Fitted constants: η_w 0.8615 (measured), k_hole 1.1723, position factors of shape `P2`. A4 error with the kept volume: -37.8 cents.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.039 | 0.0 (kept) | 4.0 | 4.05 | **4.17** | 3.34 | +0.71 | 4.173 | 10 | ok |
| sub2 | C5 | 0.955 | 3.0 (kept) | 7.0 | 3.36 | **3.49** | 3.06 | +0.31 | 3.487 | 10 | ok |
| R_pinky | D5 | 0.822 | 0.0 (kept) | 4.0 | 5.46 | **5.58** | 4.16 | +1.30 | 5.581 | 10 | ok |
| R_ring | E5 | 0.901 | 0.0 (kept) | 4.0 | 6.03 | **6.15** | 4.83 | +1.20 | 6.152 | 10 | ok |
| R_middle | F5 | 0.914 | 0.0 (kept) | 4.0 | 4.12 | **4.24** | 3.45 | +0.67 | 4.242 | 10 | ok |
| R_index | G5 | 1.035 | 0.0 (kept) | 4.0 | 7.02 | **7.14** | 6.09 | +0.92 | 7.140 | 10 | ok |
| L_ring | A5 | 1.089 | 0.0 (kept) | 4.0 | 8.02 | **8.14** | 7.14 | +0.88 | 8.144 | 10 | ok |
| L_middle | B5 | 1.027 | 0.0 (kept) | 4.0 | 9.99 | **10.11** | 8.39 | +1.59 | 10.111 | 10 | ok |
| L_index | C6 | 1.057 | 0.0 (kept) | 4.0 | 6.53 | **6.66** | 5.80 | +0.73 | 6.657 | 10 | ok |
| L_thumb | D6 | 0.992 | 0.0 (kept) | 4.0 | 13.38 | **13.50** | 10.76 | +2.62 | 13.504 | 12 | above the pad limit |
| R_thumb | E6 | 1.097 | 0.0 (kept) | 4.0 | 14.74 | **14.87** | 12.71 | +2.03 | 14.866 | 12 | above the pad limit |
| L_pinky | F6 | 1.140 | 0.0 (kept) | 4.0 | 9.35 | **9.47** | 8.56 | +0.78 | 9.469 | 10 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.17; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.99 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_thumb 13.38 mm above the 12 mm pad limit; R_thumb 14.74 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P2-80-r2_air_capped.stl; holes and window closed): 1949 Hz = 1.40 × F6 on a 1.5 mm grid of 24091 cells (2 mm grid: 1937 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.165 + voicing pocket 0.365) = 78.5301 cm³ against the kernel's 78.5288 cm³: +0.0017 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2346 cm³ (+0.0166 %), air mesh 81.2337 cm³ (+0.0156 %), against the model target 81.2211 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.75 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash b4620fbf3d67; recomputed from the record: b4620fbf3d67 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 31.0 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 41° steep seen from the rim, 10.1 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 4.39 mm (at least 0.8 mm); windway roof 2.99 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_pinky), largest chimney error -0.0007 mm (sub1); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 17.2 mm to the opposite wall, 45.7 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.11° (R_index); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.64 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 10.00 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -8.7 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.5 mm (35 % of the half section there); the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 18.4 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.33 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 4.3 to 9.0 mm beyond the flat part. Back corners beside the windway exit: 11.5 mm, a steep wall with 0.95 mm left to the chamber wall; 11.5 mm, a steep wall with 1.05 mm left to the chamber wall |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.5 mm. Measured: left 17.1 / 17.6 / 16.5 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.4 / 18.8 / 17.5, right 17.4 / 18.0 / 16.9 mm |
| `ergo_hand_span` | WARN | hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.8 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.2, right 51.0 mm |
| `ergo_arch` | pass | left ring +2.9, left middle +3.4, right ring +3.3, right middle +3.4 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +2.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 18.7 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.8°, right line +12.3° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 18.7 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 10.0 mm, +0° off the normal of the left-hand line (+9.9 mm forward, +0.0 mm toward the index); at the outer skin 11.0 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.5 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | the bulb end is 1.7 mm too short: 8.3 mm past the L pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 8.3 mm (centre 13.0), tail 11.7 mm (centre 14.5); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | L_pinky leans 29° toward the bulb end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +29°, L_ring +11°, L_middle -6°, L_index -19°, R_pinky +12°, R_ring +8°, R_middle +8°, R_index +9°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 7° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +2°, L_ring +1°, L_middle +1°, L_index +12°, R_pinky -7°, R_ring -3°, R_middle +5°, R_index +19°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.4 mm from R middle (ok -8 to +3), L thumb +9.0 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P2-80-r2/P2-80-r2.md`.

### P4-80-r2

*Round 2 of a printed body.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 2 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hole_lean_side.
- Voicing hash `b4620fbf3d67`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 40°; windway +5° against the body; neck standing 15° off the body, the pipe lowered 10° inside it; pocket blend 12 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 81.218 cm³ against the model target 81.220 cm³ (-0.003 %). Cavity mesh 78.35 cm³ (2.85 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 132.1 mm. Plastic 57.4 cm³.
- Fitted constants: η_w 0.8615 (measured), k_hole 1.1723, position factors of shape `P4` (not fitted: every factor is 1). A4 error with the kept volume: -37.8 cents. **Note:** shape 'P4' has no fitted position factors: psi = 1 for every hole.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.000 | 0.0 (kept) | 4.0 | 4.16 | **4.28** | 3.34 | +0.82 | 4.280 | 10 | ok |
| sub2 | C5 | 1.000 | 3.0 (kept) | 7.0 | 3.27 | **3.40** | 3.06 | +0.22 | 3.395 | 10 | ok |
| R_pinky | D5 | 1.000 | 0.0 (kept) | 4.0 | 4.75 | **4.87** | 4.16 | +0.59 | 4.874 | 10 | ok |
| R_ring | E5 | 1.000 | 0.0 (kept) | 4.0 | 5.60 | **5.72** | 4.83 | +0.76 | 5.717 | 10 | ok |
| R_middle | F5 | 1.000 | 0.0 (kept) | 4.0 | 3.88 | **4.00** | 3.45 | +0.42 | 3.999 | 10 | ok |
| R_index | G5 | 1.000 | 0.0 (kept) | 4.0 | 7.20 | **7.32** | 6.09 | +1.11 | 7.324 | 10 | ok |
| L_ring | A5 | 1.000 | 0.0 (kept) | 4.0 | 8.56 | **8.68** | 7.14 | +1.42 | 8.680 | 10 | ok |
| L_middle | B5 | 1.000 | 0.0 (kept) | 4.0 | 10.20 | **10.32** | 8.39 | +1.80 | 10.319 | 10 | above the pad limit |
| L_index | C6 | 1.000 | 0.0 (kept) | 4.0 | 6.80 | **6.93** | 5.80 | +1.00 | 6.926 | 10 | ok |
| L_thumb | D6 | 1.000 | 0.0 (kept) | 4.0 | 13.30 | **13.42** | 10.76 | +2.54 | 13.423 | 12 | above the pad limit |
| R_thumb | E6 | 1.000 | 0.0 (kept) | 4.0 | 15.85 | **15.97** | 12.71 | +3.13 | 15.971 | 12 | above the pad limit |
| L_pinky | F6 | 1.000 | 0.0 (kept) | 4.0 | 10.30 | **10.42** | 8.56 | +1.74 | 10.425 | 10 | above the pad limit |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 9.15; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.94 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_middle 10.20 mm above the 10 mm pad limit; L_thumb 13.30 mm above the 12 mm pad limit; R_thumb 15.85 mm above the 12 mm pad limit; L_pinky 10.30 mm above the 10 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P4-80-r2_air_capped.stl; holes and window closed): 1896 Hz = 1.36 × F6 on a 1.5 mm grid of 24075 cells (2 mm grid: 1888 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 78.117 + voicing pocket 0.233) = 78.3503 cm³ against the kernel's 78.3499 cm³: +0.0005 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 81.2177 cm³ (-0.0026 %), air mesh 81.2424 cm³ (+0.0278 %), against the model target 81.2198 cm³ (V0 80.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.98 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash b4620fbf3d67; recomputed from the record: b4620fbf3d67 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window inf mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 41° steep seen from the rim, 10.1 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 4.43 mm (at least 0.8 mm); windway roof 2.99 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (sub2), largest chimney error -0.0044 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 22.0 mm to the opposite wall, 42.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.19° (sub1); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.52 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 10.00 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -9.0 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there); the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10); the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 17.7 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.02 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 2.9 to 6.2 mm beyond the flat part. Back corners beside the windway exit: 9.5 mm, meets the wall; 9.4 mm, meets the wall |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.7 / 18.2 / 17.1, right 17.4 / 18.3 / 17.5 mm |
| `ergo_hand_span` | pass | left 50.1 mm, right 50.4 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.9, right 51.4 mm |
| `ergo_arch` | pass | left ring +3.0, left middle +3.2, right ring +3.3, right middle +3.5 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +1.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 18.6 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.1°, right line +12.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 18.6 mm across (toward the player), +0.9 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 10.0 mm, +0° off the normal of the left-hand line (+9.7 mm forward, +0.0 mm toward the index); at the outer skin 11.6 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.9 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | pass | land past the pinky holes, from the hole edge along the hand axis: bulb 13.6 mm (centre 18.8), tail 11.3 mm (centre 13.7); ok at least 10 mm |
| `ergo_hole_lean_end` | pass | lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +13°, L_ring +5°, L_middle -3°, L_index -12°, R_pinky +19°, R_ring +14°, R_middle +9°, R_index +3°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 10° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -5°, L_ring -3°, L_middle +4°, L_index +20°, R_pinky -10°, R_ring -4°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.4 mm from R middle (ok -8 to +3), L thumb +9.8 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P4-80-r2/P4-80-r2.md`.

### P0-88-r2

*Never printed: sized from the fitted model only.*

- Result: **no unexpected failure**; expected by the notes: hole_limits[fitted] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `dfde809794fe`. Window: Teardrop 9.65 × 10.44 mm, 77.4 mm², wall 4.0 mm. Windway: exit 1.20 × 10.44 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 40°; windway +5° against the body; neck standing 15° off the body, the pipe lowered 10° inside it; pocket blend 12 mm.
- Volume: V0 88.00 cm³ (capped air). Measured on the STL: 89.358 cm³ against the model target 89.338 cm³ (+0.021 %). Cavity mesh 86.42 cm³ (2.86 cm³ of air in the holes, 0.02 cm³ of tube wall). Cavity spine length 81.0 mm. Plastic 53.7 cm³.
- Fitted constants: η_w 0.8601 (fallback), k_hole 1.1723, position factors of shape `P0`. A4 error with the kept volume: +0.0 cents. **Note:** voicing hash was never measured: eta_w_fallback used.

| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 1.098 | 0.0 | 4.0 | 3.75 | **3.88** | – | – | 3.876 | 10 | ok |
| sub2 | C5 | 1.012 | 1.0 | 5.0 | 3.04 | **3.16** | – | – | 3.159 | 10 | ok |
| R_pinky | D5 | 0.871 | 0.0 | 4.0 | 5.61 | **5.73** | – | – | 5.735 | 10 | ok |
| R_ring | E5 | 0.933 | 0.0 | 4.0 | 6.31 | **6.43** | – | – | 6.429 | 10 | ok |
| R_middle | F5 | 0.972 | 0.0 | 4.0 | 4.22 | **4.34** | – | – | 4.341 | 10 | ok |
| R_index | G5 | 1.096 | 0.0 | 4.0 | 7.22 | **7.35** | – | – | 7.347 | 10 | ok |
| L_ring | A5 | 1.133 | 0.0 | 4.0 | 8.38 | **8.50** | – | – | 8.501 | 10 | ok |
| L_middle | B5 | 1.075 | 0.0 | 4.0 | 10.40 | **10.52** | – | – | 10.522 | 10 | above the pad limit |
| L_index | C6 | 1.155 | 0.0 | 4.0 | 6.58 | **6.70** | – | – | 6.699 | 10 | ok |
| L_thumb | D6 | 1.031 | 0.0 | 4.0 | 14.05 | **14.17** | – | – | 14.171 | 12 | above the pad limit |
| R_thumb | E6 | 1.158 | 0.0 | 4.0 | 15.29 | **15.41** | – | – | 15.413 | 12 | above the pad limit |
| L_pinky | F6 | 1.202 | 0.0 | 4.0 | 9.68 | **9.80** | – | – | 9.803 | 10 | ok |

All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.75; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.52 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[fitted]` | FAIL (expected) | L_middle 10.40 mm above the 10 mm pad limit; L_thumb 14.05 mm above the 12 mm pad limit; R_thumb 15.29 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-88-r2_air_capped.stl; holes and window closed): 2818 Hz = 2.02 × F6 on a 1.5 mm grid of 26494 cells (2 mm grid: 2811 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 86.170 + voicing pocket 0.250) = 86.4194 cm³ against the kernel's 86.4190 cm³: +0.0005 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 89.3575 cm³ (+0.0213 %), air mesh 89.3549 cm³ (+0.0183 %), against the model target 89.3385 cm³ (V0 88.0000 cm³ in the print, volume factor 0.9854, holes drawn with the hole offset) (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 4.11 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash dfde809794fe; recomputed from the record: dfde809794fe |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 10.440 mm, 77.43 mm² (record 9.650 × 10.440, 77.44); windway exit 1.200 × 10.440 mm, inlet 3.000 × 10.440 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 10.440 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.70 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 34.2 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 41° steep seen from the rim, 10.1 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 3.34 mm (at least 0.8 mm); windway roof 2.99 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (sub2), largest chimney error -0.0022 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 1.000 mm (kernel 1.0), wall 1.198 mm, 35.2 mm to the opposite wall, 37.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.90° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.04 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: R_thumb, 30.1 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.30 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 4.1 to 7.0 mm beyond the flat part. Back corners beside the windway exit: 10.1 mm, meets the wall; 10.1 mm, meets the wall |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 30.5 / 15.7 / 16.1 mm, right 12.3 / 11.8 / 15.4 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 33.1 / 17.5 / 17.5, right 13.7 / 12.9 / 16.7 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 17.1 mm, right 28.0 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 18.8, right 30.2 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring +17.2, left middle +13.9, right ring -4.6, right middle +6.5 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines -136.0° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is -13.4 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line -107.5°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: -8.4 mm across (toward the player), +19.8 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_index: 9.6 mm, +30° off the normal of the left-hand line (+8.1 mm forward, +4.7 mm toward the index); at the outer skin 10.2 mm; sub2 from R_middle: 7.8 mm, +38° off the normal of the right-hand line (+6.1 mm forward, +4.8 mm toward the index); at the outer skin 8.3 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 17.5 mm (centre 22.4), tail 11.3 mm (centre 14.1); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +16°, L_ring +16°, L_middle +22°, L_index +3°, R_pinky +22°, R_ring +23°, R_middle +8°, R_index +14°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +11°, L_ring -29°, L_middle -3°, L_index -10°, R_pinky -27°, R_ring -5°, R_middle -10°, R_index +8°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +0.0 mm from R middle (ok -8 to +3), L thumb -9.1 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2.stl`, air_capped_stl: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2_air_capped.stl`, air_fem_stl: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2_air_fem.stl`, measurement_template: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2_measurement.toml`, check_report: `addon_out/stage3-synthetic-fitted-constants/P0-88-r2/P0-88-r2.md`.

