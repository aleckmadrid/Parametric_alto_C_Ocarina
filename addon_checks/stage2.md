# Stage 2 · Round 1 bodies: generation report

Written by `ocarina_addon/headless.py -- stage2` on 2026-11-16. Every measured number comes from the STL file of the body, read back from disk. Run time 444 s for 9 bodies.

Result: **9 of 9 bodies have no unexpected failure**.

- Every body has the full 12 round holes, sized for its own volume and cut at the k_hole = 0.8 (`print`) diameters. P0 bodies carry the taped test layout; P1, P2 and P3 carry the hand layout.
- **Read the warnings before printing.** The hole layout of every shape is frozen once Stage 2 is printed (doc 04 D10), because the fitted position factors belong to one layout.
- P4 is not in this list: it waits for a hand check on a printed P2 (doc 02 Q10, Q11).
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).
- Everything is pre-calibration: η_w prior 0.90, k_hole 0.8 for the first prints, 27 °C internal air. Nothing in this report was measured on a printed body.
- Statuses: `pass` (the docs say ok), `FAIL`, `NEEDS FEM` (cavity-mode desk check between its limits), `WARN` (a soft ergonomic check; never a failure), `info` (a reported number).

## Bodies

| Body | Preset | V0 | Voicing hash | Window | Windway exit | Capped air on the STL | First cavity mode (desk check) | Plastic; solid PLA mass | doc 04 mass | Failures | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0-65 | P0 | 65.0 cm³ | `6aa0038008cc` | Teardrop 9.65 × 6.96 mm, 46.5 mm² | 1.20 × 6.96 mm | 65.008 cm³ (+0.012 %) | 2.24 × F6, pass (c/(2L): 1.69) | 39.8 cm³; 49 g | 77 g | hole_limits[nominal] (expected) | 11 (taped test body) |
| P0-80 | P0 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 80.009 cm³ (+0.011 %) | 2.10 × F6, pass (c/(2L): 1.57) | 44.7 cm³; 55 g | 84 g | hole_limits[print] (expected), hole_limits[nominal] (expected) | 11 (taped test body) |
| P0-95 | P0 | 95.0 cm³ | `622bdad5acb2` | Teardrop 9.65 × 11.10 mm, 81.2 mm² | 1.20 × 11.10 mm | 95.013 cm³ (+0.013 %) | 1.98 × F6, pass (c/(2L): 1.49) | 49.3 cm³; 61 g | 91 g | hole_limits[print] (expected), hole_limits[nominal] (expected) | 11 (taped test body) |
| P0-125 | P0 | 125.0 cm³ | `f3803f8358b6` | Teardrop 9.65 × 18.57 mm, 123.5 mm² | 1.20 × 18.57 mm | 125.025 cm³ (+0.020 %) | 1.81 × F6, pass (c/(2L): 1.36) | 57.9 cm³; 72 g | 108 g | hole_limits[print] (expected), hole_limits[nominal] (expected) | 11 (taped test body) |
| P1-80 | P1 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 80.011 cm³ (+0.013 %) | 1.63 × F6, pass (c/(2L): 1.13) | 49.3 cm³; 61 g | 91 g | hole_limits[print] (expected), hole_limits[nominal] (expected) | 4 |
| P2-80 | P2 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 80.008 cm³ (+0.010 %) | 1.40 × F6, pass (c/(2L): 0.99) | 52.2 cm³; 65 g | 97 g | hole_limits[print] (expected), hole_limits[nominal] (expected) | 5 |
| P3-80 | P3 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 80.006 cm³ (+0.007 %) | 1.76 × F6, pass (c/(2L): 1.32) | 47.9 cm³; 59 g | 91 g | hole_limits[print] (expected), hole_limits[nominal] (expected) | 6 |
| P0-80-b | P0 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 80.009 cm³ (+0.011 %) | 2.10 × F6, pass (c/(2L): 1.57) | 44.7 cm³; 55 g | 84 g | hole_limits[print] (expected), hole_limits[nominal] (expected) | 11 (taped test body) |
| P0-80-c | P0 | 80.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 80.009 cm³ (+0.011 %) | 2.10 × F6, pass (c/(2L): 1.57) | 44.7 cm³; 55 g | 84 g | hole_limits[print] (expected), hole_limits[nominal] (expected) | 11 (taped test body) |

*Capped air* is compared with the target of the model: V0 for a round-1 body, the stub volume for a stub, and in Stage 3 V0 divided by the fitted volume factor, with the holes drawn at their CAD diameters. *First cavity mode* is the computed desk check with closed holes, which gives the verdict; the number in brackets is the kernel's c/(2L) estimate from the length of the chamber, the lowest estimate, shown for information (it is 30 to 44 % low for these shapes, docs/06 section 3.10). *Solid PLA mass* is the plastic volume of the STL at 1.24 g/cm³, with no supports, brim or infill saving; the doc 04 figure includes about 12 % for supports and a brim.

Total for the 9 bodies of this stage: 534 g of solid PLA, 598 g with 12 % for supports and a brim. The doc 04 budget for this stage is 807 g. The generated bodies are lighter than the budget; the doc 04 masses were estimates made before any body was built.

Repeatability copies: `P0-80-b` has the same triangles as `P0-80`; `P0-80-c` has the same triangles as `P0-80`. A copy has its own STL file, measurement template and check report, and no pictures.

## Unexpected failures

None.

## Expected failures

Failures that the plan expects (the pad-limit checks: doc 04 prints these holes on purpose, "the real limit is unknown"). They do not stop a stage.

- P0-65 `hole_limits[nominal]` (fail): L_index 10.31 mm above the 10 mm pad limit; L_thumb 12.22 mm above the 12 mm pad limit
- P0-80 `hole_limits[print]` (fail): L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit
- P0-80 `hole_limits[nominal]` (fail): L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit
- P0-95 `hole_limits[print]` (fail): L_index 12.25 mm above the 10 mm pad limit; L_thumb 14.51 mm above the 12 mm pad limit
- P0-95 `hole_limits[nominal]` (fail): L_ring 10.67 mm above the 10 mm pad limit; L_index 13.87 mm above the 10 mm pad limit; L_thumb 16.52 mm above the 12 mm pad limit
- P0-125 `hole_limits[print]` (fail): L_ring 11.69 mm above the 10 mm pad limit; L_index 15.14 mm above the 10 mm pad limit; L_thumb 18.00 mm above the 12 mm pad limit
- P0-125 `hole_limits[nominal]` (fail): L_pinky 11.09 mm above the 10 mm pad limit; L_ring 13.24 mm above the 10 mm pad limit; L_index 17.31 mm above the 10 mm pad limit; L_thumb 20.64 mm above the 12 mm pad limit; R_thumb 13.34 mm above the 12 mm pad limit
- P1-80 `hole_limits[print]` (fail): L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit
- P1-80 `hole_limits[nominal]` (fail): L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit
- P2-80 `hole_limits[print]` (fail): L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit
- P2-80 `hole_limits[nominal]` (fail): L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit
- P3-80 `hole_limits[print]` (fail): L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit
- P3-80 `hole_limits[nominal]` (fail): L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit
- P0-80-b `hole_limits[print]` (fail): L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit
- P0-80-b `hole_limits[nominal]` (fail): L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit
- P0-80-c `hole_limits[print]` (fail): L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit
- P0-80-c `hole_limits[nominal]` (fail): L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit

## Warnings

Soft ergonomic checks outside their range. They are measurements for the owner to judge. A warning is never a failure.

- P0-65: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_checks/P0-65.md`.
- P0-80: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_checks/P0-80.md`.
- P0-95: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_checks/P0-95.md`.
- P0-125: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_checks/P0-125.md`.
- P1-80 `ergo_hand_span`: hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.2 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.3, right 51.9 mm
- P1-80 `ergo_rest_space`: the bulb end is 4.8 mm too short: 5.2 mm past the L pinky hole edge; the tail end is 5.2 mm too short: 4.8 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 5.2 mm (centre 8.8), tail 4.8 mm (centre 6.8); ok at least 10 mm
- P1-80 `ergo_hole_lean_end`: L_pinky leans 38° toward the bulb end; R_pinky leans 30° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +38°, L_ring +15°, L_middle -0°, L_index -14°, R_pinky +30°, R_ring +15°, R_middle +11°, R_index +5°; ok up to 20°
- P1-80 `ergo_hole_lean_side`: R_pinky leans 13° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -0°, L_ring +0°, L_middle +4°, L_index +17°, R_pinky -13°, R_ring -3°, R_middle +7°, R_index +22°; ok up to 45° toward it and up to 5° away
- P2-80 `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.4 mm. Measured: left 17.1 / 17.6 / 16.4 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.4 / 18.8 / 17.5, right 17.4 / 18.0 / 16.9 mm
- P2-80 `ergo_hand_span`: hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.8 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.2, right 51.0 mm
- P2-80 `ergo_rest_space`: the bulb end is 0.6 mm too short: 9.4 mm past the L pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 9.4 mm (centre 13.0), tail 12.4 mm (centre 14.4); ok at least 10 mm
- P2-80 `ergo_hole_lean_end`: L_pinky leans 29° toward the bulb end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +29°, L_ring +11°, L_middle -6°, L_index -19°, R_pinky +12°, R_ring +8°, R_middle +8°, R_index +9°; ok up to 20°
- P2-80 `ergo_hole_lean_side`: R_pinky leans 7° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +2°, L_ring +1°, L_middle +1°, L_index +12°, R_pinky -7°, R_ring -3°, R_middle +5°, R_index +19°; ok up to 45° toward it and up to 5° away
- P3-80 `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.3 mm. Measured: left 17.0 / 17.4 / 16.3 mm, right 17.1 / 18.1 / 17.1 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.0 / 18.0 / 17.0, right 18.4 / 18.8 / 17.8 mm
- P3-80 `ergo_hand_span`: hand span out of range: left hand 49.4 mm. Measured: left 49.4 mm, right 51.0 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.5, right 53.6 mm
- P3-80 `ergo_hand_offset`: hand lines 17.5 mm apart across. Measured: the right-hand line is 17.5 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +9.5°, right line +14.8° (+ = the tail end of the line is farther from the player)
- P3-80 `ergo_index_meet`: index holes 17.6 mm apart across; R index -23.3 mm along the hand axis from L index. Measured: R index from L index: 17.6 mm across (toward the player), -23.3 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along
- P3-80 `ergo_rest_space`: the bulb end is 0.0 mm too short: 10.0 mm past the L pinky hole edge; the tail end is 2.2 mm too short: 7.8 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 10.0 mm (centre 13.6), tail 7.8 mm (centre 9.9); ok at least 10 mm
- P3-80 `ergo_hole_lean_end`: L_pinky leans 23° toward the bulb end; R_pinky leans 31° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +23°, L_ring +9°, L_middle -0°, L_index -8°, R_pinky +31°, R_ring +12°, R_middle +2°, R_index -8°; ok up to 20°
- P0-80-b: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_checks/P0-80-b.md`.
- P0-80-c: all 11 `ergo_*` checks warn: taped test body, not a hand layout. The measured numbers are in `addon_checks/P0-80-c.md`.

## Sizes against doc 04

The table "Generated sizes at each step" of [docs/04](../docs/04-testing-phase.md), regenerated by the kernel from the bodies of this stage (P0 ladder; holes at the k_hole = 1.0 nominal on a plain 4 mm wall, as in doc 04). The bodies are **printed at the k_hole = 0.8 diameters**, which the per-body tables give. Doc 04 also has a 110 cm³ row; that body belongs to Stage 3. *P0 length* is the length of the egg that holds V0, as in doc 04; the cavity mesh of a built body holds V0 minus the air in the holes, so its spine is about 1 % shorter (the per-body sections give it).

| V0 | Window | Windway | sub2 (sub_R) | L_index | E6 thumb (L_thumb) | P0 length | Window area / V0^(2/3) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 65 cm³ | Teardrop 9.65 × 7.0 mm, 46 mm² | 1.2 × 7.0 mm | 2.2 mm | 10.3 mm | 12.2 mm | 74 mm | 0.029 |
| 80 cm³ | Teardrop 9.65 × 8.8 mm, 63 mm² | 1.2 × 8.8 mm | 2.6 mm | 12.1 mm | 14.4 mm | 79 mm | 0.034 |
| 95 cm³ | Teardrop 9.65 × 11.1 mm, 81 mm² | 1.2 × 11.1 mm | 2.8 mm | 13.9 mm | 16.5 mm | 84 mm | 0.039 |
| 125 cm³ | Teardrop 9.65 × 18.6 mm, 123 mm² | 1.2 × 18.6 mm | 3.4 mm | 17.3 mm | 20.6 mm | 92 mm | 0.049 |

## Per body

### P0-65

- Result: **no unexpected failure**; expected by the notes: hole_limits[nominal] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `6aa0038008cc`. Window: Teardrop 9.65 × 6.96 mm, 46.5 mm², wall 4.0 mm. Windway: exit 1.20 × 6.96 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 65.00 cm³ (capped air). Measured on the STL: 65.008 cm³ against the model target 65.000 cm³ (+0.012 %). Cavity mesh 63.64 cm³ (1.45 cm³ of air in the holes, 0.09 cm³ of tube wall). Cavity spine length 73.2 mm. Plastic 39.8 cm³.

| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 3.11 | 0.5 | 4.5 | **3.08** | 3.24 | 3.077 | 4.494 | 10 | ok |
| sub2 | C5 | 2.24 | 5.0 | 9.0 | **3.03** | 3.11 | 3.025 | 8.998 | 10 | ok |
| R_pinky | D5 | 3.89 | 0.0 | 4.0 | **3.64** | 3.89 | 3.642 | 4.000 | 10 | ok |
| R_ring | E5 | 4.54 | 0.0 | 4.0 | **4.22** | 4.54 | 4.219 | 4.000 | 10 | ok |
| R_middle | F5 | 3.21 | 0.0 | 4.0 | **3.03** | 3.21 | 3.033 | 4.000 | 10 | ok |
| R_index | G5 | 5.76 | 0.0 | 4.0 | **5.29** | 5.75 | 5.291 | 4.000 | 10 | ok |
| L_pinky | A5 | 6.78 | 0.0 | 4.0 | **6.18** | 6.77 | 6.178 | 3.999 | 10 | ok |
| L_ring | B5 | 8.00 | 0.0 | 4.0 | **7.24** | 8.00 | 7.237 | 3.999 | 10 | ok |
| L_middle | C6 | 5.47 | 0.0 | 4.0 | **5.05** | 5.47 | 5.048 | 4.000 | 10 | ok |
| L_index | D6 | 10.31 | 0.0 | 4.0 | **9.22** | 10.31 | 9.224 | 3.999 | 10 | k 1.0 above the pad limit |
| L_thumb | E6 | 12.23 | 0.0 | 4.0 | **10.87** | 12.22 | 10.869 | 4.000 | 12 | k 1.0 above the pad limit |
| R_thumb | F6 | 8.14 | 0.0 | 4.0 | **7.39** | 8.14 | 7.391 | 4.000 | 12 | ok |

All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.85; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.69 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | pass | all holes inside floor and pad limits |
| `hole_limits[nominal]` | FAIL (expected) | L_index 10.31 mm above the 10 mm pad limit; L_thumb 12.22 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-65_air_capped.stl; holes and window closed): 3133 Hz = 2.24 × F6 on a 1.5 mm grid of 19250 cells (2 mm grid: 3122 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 63.516 + voicing pocket 0.125) = 63.6403 cm³ against the kernel's 63.6402 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 65.0078 cm³ (+0.0119 %), air mesh 65.0062 cm³ (+0.0096 %), against V0 65.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 19 Booleans, all manifold, each volume change as expected (largest deviation 10.25 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 6aa0038008cc; recomputed from the record: 6aa0038008cc |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 6.959 mm, 46.47 mm² (record 9.650 × 6.959, 46.47); windway exit 1.200 × 6.959 mm, inlet 1.560 × 6.959 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.48 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 29.4 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.48 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (sub1), largest chimney error -0.0058 mm (sub1); limit 0.05 mm |
| `inward_tubes` | pass | sub1: length 0.500 mm (kernel 0.5), wall 1.198 mm, 30.7 mm to the opposite wall, 31.0 mm to the labium, 24.2 mm to the nearest other tube; sub2: length 5.000 mm (kernel 5.0), wall 1.198 mm, 27.7 mm to the opposite wall, 29.8 mm to the labium, 24.2 mm to the nearest other tube |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.01 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 29.7 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 14.2 / 14.5 / 15.5 mm, right 11.1 / 10.7 / 13.9 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 16.0 / 15.9 / 17.2, right 12.5 / 11.8 / 15.2 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 27.2 mm, right 25.3 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 29.7, right 27.5 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -5.3, left middle +8.8, right ring -4.2, right middle +5.9 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 24.5 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 24.6 mm across (toward the player), +0.6 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 8.7 mm, -115° off the normal of the left-hand line (-3.5 mm forward, -7.7 mm toward the index); at the outer skin 9.3 mm; sub2 from R_middle: 7.0 mm, +38° off the normal of the right-hand line (+5.5 mm forward, +4.3 mm toward the index); at the outer skin 7.5 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.9 mm (centre 11.0), tail 9.0 mm (centre 10.8); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +6.7 mm from R middle (ok -8 to +3), L thumb +13.5 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage2/P0-65/P0-65.stl`, air_capped_stl: `addon_out/stage2/P0-65/P0-65_air_capped.stl`, air_fem_stl: `addon_out/stage2/P0-65/P0-65_air_fem.stl`, renders: `addon_renders/P0-65/`, measurement_template: `addon_out/stage2/P0-65/P0-65_measurement.toml`, check_report: `addon_checks/P0-65.md`.

### P0-80

- Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 80.009 cm³ against the model target 80.000 cm³ (+0.011 %). Cavity mesh 78.11 cm³ (1.94 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 78.3 mm. Plastic 44.7 cm³.

| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 3.56 | 0.0 | 4.0 | **3.34** | 3.56 | 3.343 | 3.999 | 10 | ok |
| sub2 | C5 | 2.55 | 3.0 | 7.0 | **3.06** | 3.17 | 3.057 | 6.998 | 10 | ok |
| R_pinky | D5 | 4.47 | 0.0 | 4.0 | **4.16** | 4.47 | 4.161 | 4.000 | 10 | ok |
| R_ring | E5 | 5.24 | 0.0 | 4.0 | **4.83** | 5.24 | 4.835 | 4.000 | 10 | ok |
| R_middle | F5 | 3.68 | 0.0 | 4.0 | **3.45** | 3.68 | 3.452 | 4.000 | 10 | ok |
| R_index | G5 | 6.68 | 0.0 | 4.0 | **6.09** | 6.68 | 6.094 | 4.000 | 10 | ok |
| L_pinky | A5 | 7.89 | 0.0 | 4.0 | **7.14** | 7.89 | 7.141 | 3.999 | 10 | ok |
| L_ring | B5 | 9.35 | 0.0 | 4.0 | **8.39** | 9.35 | 8.395 | 3.999 | 10 | ok |
| L_middle | C6 | 6.34 | 0.0 | 4.0 | **5.80** | 6.33 | 5.805 | 4.000 | 10 | ok |
| L_index | D6 | 12.12 | 0.0 | 4.0 | **10.76** | 12.11 | 10.758 | 3.999 | 10 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| L_thumb | E6 | 14.40 | 0.0 | 4.0 | **12.71** | 14.39 | 12.715 | 4.000 | 12 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| R_thumb | F6 | 9.50 | 0.0 | 4.0 | **8.56** | 9.49 | 8.563 | 4.000 | 12 | ok |

All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.83; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.57 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-80_air_capped.stl; holes and window closed): 2927 Hz = 2.10 × F6 on a 1.5 mm grid of 23759 cells (2 mm grid: 2920 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.975 + voicing pocket 0.138) = 78.1126 cm³ against the kernel's 78.1125 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 80.0092 cm³ (+0.0115 %), air mesh 80.0076 cm³ (+0.0095 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.36 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 32.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.21 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (sub1), largest chimney error -0.0021 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 32.0 mm to the opposite wall, 34.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.90° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.28 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 30.9 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 15.2 / 15.6 / 16.6 mm, right 11.9 / 11.4 / 14.9 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.0 / 16.9 / 18.3, right 13.3 / 12.5 / 16.2 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 29.1 mm, right 27.0 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 31.6, right 29.3 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -5.7, left middle +9.4, right ring -4.5, right middle +6.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 26.3 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 26.3 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 9.3 mm, -115° off the normal of the left-hand line (-3.8 mm forward, -8.2 mm toward the index); at the outer skin 9.9 mm; sub2 from R_middle: 7.5 mm, +38° off the normal of the right-hand line (+5.9 mm forward, +4.6 mm toward the index); at the outer skin 8.0 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.9 mm (centre 11.5), tail 9.2 mm (centre 11.3); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.1 mm from R middle (ok -8 to +3), L thumb +14.5 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage2/P0-80/P0-80.stl`, air_capped_stl: `addon_out/stage2/P0-80/P0-80_air_capped.stl`, air_fem_stl: `addon_out/stage2/P0-80/P0-80_air_fem.stl`, renders: `addon_renders/P0-80/`, measurement_template: `addon_out/stage2/P0-80/P0-80_measurement.toml`, check_report: `addon_checks/P0-80.md`.

### P0-95

- Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `622bdad5acb2`. Window: Teardrop 9.65 × 11.10 mm, 81.2 mm², wall 4.0 mm. Windway: exit 1.20 × 11.10 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 95.00 cm³ (capped air). Measured on the STL: 95.013 cm³ against the model target 95.000 cm³ (+0.013 %). Cavity mesh 92.54 cm³ (2.48 cm³ of air in the holes, 0.02 cm³ of tube wall). Cavity spine length 82.9 mm. Plastic 49.3 cm³.

| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 3.98 | 0.0 | 4.0 | **3.72** | 3.98 | 3.725 | 3.999 | 10 | ok |
| sub2 | C5 | 2.84 | 1.5 | 5.5 | **3.06** | 3.20 | 3.059 | 5.498 | 10 | ok |
| R_pinky | D5 | 5.03 | 0.0 | 4.0 | **4.65** | 5.03 | 4.655 | 4.000 | 10 | ok |
| R_ring | E5 | 5.91 | 0.0 | 4.0 | **5.42** | 5.91 | 5.424 | 4.000 | 10 | ok |
| R_middle | F5 | 4.12 | 0.0 | 4.0 | **3.85** | 4.12 | 3.849 | 4.000 | 10 | ok |
| R_index | G5 | 7.58 | 0.0 | 4.0 | **6.87** | 7.57 | 6.867 | 4.000 | 10 | ok |
| L_pinky | A5 | 8.98 | 0.0 | 4.0 | **8.07** | 8.98 | 8.071 | 3.999 | 10 | ok |
| L_ring | B5 | 10.67 | 0.0 | 4.0 | **9.52** | 10.67 | 9.518 | 3.999 | 10 | k 1.0 above the pad limit |
| L_middle | C6 | 7.17 | 0.0 | 4.0 | **6.53** | 7.17 | 6.530 | 4.000 | 10 | ok |
| L_index | D6 | 13.88 | 0.0 | 4.0 | **12.25** | 13.87 | 12.249 | 3.999 | 10 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| L_thumb | E6 | 16.52 | 0.0 | 4.0 | **14.51** | 16.52 | 14.512 | 4.000 | 12 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| R_thumb | F6 | 10.81 | 0.0 | 4.0 | **9.69** | 10.81 | 9.694 | 4.000 | 12 | ok |

All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.82; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.49 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_index 12.25 mm above the 10 mm pad limit; L_thumb 14.51 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_ring 10.67 mm above the 10 mm pad limit; L_index 13.87 mm above the 10 mm pad limit; L_thumb 16.52 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-95_air_capped.stl; holes and window closed): 2772 Hz = 1.98 × F6 on a 1.5 mm grid of 28142 cells (2 mm grid: 2761 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 92.387 + voicing pocket 0.157) = 92.5446 cm³ against the kernel's 92.5445 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 95.0126 cm³ (+0.0133 %), air mesh 95.0110 cm³ (+0.0115 %), against V0 95.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 2.61 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 622bdad5acb2; recomputed from the record: 622bdad5acb2 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 11.102 mm, 81.14 mm² (record 9.650 × 11.102, 81.15); windway exit 1.200 × 11.102 mm, inlet 1.560 × 11.102 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.60 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 35.0 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.02 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (R_pinky), largest chimney error -0.0023 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 1.500 mm (kernel 1.5), wall 1.198 mm, 35.6 mm to the opposite wall, 37.6 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.52 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 31.4 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 16.0 / 16.5 / 17.5 mm, right 12.6 / 12.1 / 15.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.9 / 17.8 / 19.2, right 14.0 / 13.2 / 17.1 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 30.8 mm, right 28.6 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 33.3, right 30.9 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -6.0, left middle +10.0, right ring -4.7, right middle +6.6 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 27.8 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 27.9 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 9.8 mm, -115° off the normal of the left-hand line (-4.0 mm forward, -8.7 mm toward the index); at the outer skin 10.4 mm; sub2 from R_middle: 8.0 mm, +38° off the normal of the right-hand line (+6.2 mm forward, +4.9 mm toward the index); at the outer skin 8.4 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.9 mm (centre 11.9), tail 9.4 mm (centre 11.7); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.5 mm from R middle (ok -8 to +3), L thumb +15.3 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage2/P0-95/P0-95.stl`, air_capped_stl: `addon_out/stage2/P0-95/P0-95_air_capped.stl`, air_fem_stl: `addon_out/stage2/P0-95/P0-95_air_fem.stl`, renders: `addon_renders/P0-95/`, measurement_template: `addon_out/stage2/P0-95/P0-95_measurement.toml`, check_report: `addon_checks/P0-95.md`.

### P0-125

- Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `f3803f8358b6`. Window: Teardrop 9.65 × 18.57 mm, 123.5 mm², wall 4.0 mm. Windway: exit 1.20 × 18.57 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 125.00 cm³ (capped air). Measured on the STL: 125.025 cm³ against the model target 125.000 cm³ (+0.020 %). Cavity mesh 121.27 cm³ (3.73 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 90.7 mm. Plastic 57.9 cm³.

| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 4.79 | 0.0 | 4.0 | **4.45** | 4.79 | 4.445 | 3.999 | 10 | ok |
| sub2 | C5 | 3.38 | 0.0 | 4.0 | **3.19** | 3.38 | 3.188 | 4.000 | 10 | ok |
| R_pinky | D5 | 6.10 | 0.0 | 4.0 | **5.59** | 6.10 | 5.592 | 4.000 | 10 | ok |
| R_ring | E5 | 7.21 | 0.0 | 4.0 | **6.55** | 7.21 | 6.546 | 4.000 | 10 | ok |
| R_middle | F5 | 4.96 | 0.0 | 4.0 | **4.60** | 4.96 | 4.596 | 4.000 | 10 | ok |
| R_index | G5 | 9.31 | 0.0 | 4.0 | **8.35** | 9.31 | 8.350 | 4.000 | 10 | ok |
| L_pinky | A5 | 11.09 | 0.0 | 4.0 | **9.86** | 11.09 | 9.865 | 3.999 | 10 | k 1.0 above the pad limit |
| L_ring | B5 | 13.24 | 0.0 | 4.0 | **11.69** | 13.24 | 11.690 | 3.999 | 10 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| L_middle | C6 | 8.78 | 0.0 | 4.0 | **7.92** | 8.78 | 7.919 | 4.000 | 10 | ok |
| L_index | D6 | 17.31 | 0.0 | 4.0 | **15.14** | 17.31 | 15.144 | 3.999 | 10 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| L_thumb | E6 | 20.64 | 0.0 | 4.0 | **18.00** | 20.64 | 17.999 | 4.000 | 12 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| R_thumb | F6 | 13.34 | 0.0 | 4.0 | **11.87** | 13.34 | 11.870 | 4.000 | 12 | k 1.0 above the pad limit |

All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.78; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.36 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_ring 11.69 mm above the 10 mm pad limit; L_index 15.14 mm above the 10 mm pad limit; L_thumb 18.00 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_pinky 11.09 mm above the 10 mm pad limit; L_ring 13.24 mm above the 10 mm pad limit; L_index 17.31 mm above the 10 mm pad limit; L_thumb 20.64 mm above the 12 mm pad limit; R_thumb 13.34 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-125_air_capped.stl; holes and window closed): 2533 Hz = 1.81 × F6 on a 1.5 mm grid of 37052 cells (2 mm grid: 2523 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 121.040 + voicing pocket 0.235) = 121.2749 cm³ against the kernel's 121.2747 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 125.0252 cm³ (+0.0202 %), air mesh 125.0201 cm³ (+0.0161 %), against V0 125.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 17 Booleans, all manifold, each volume change as expected (largest deviation 1.00 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash f3803f8358b6; recomputed from the record: f3803f8358b6 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 18.568 mm, 123.48 mm² (record 9.650 × 18.568, 123.50); windway exit 1.200 × 18.568 mm, inlet 1.560 × 18.568 mm; labium 20.00°, edge 0.400 mm, offset +0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.88 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 38.1 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 1.75 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (R_pinky), largest chimney error -0.0007 mm (L_index); limit 0.05 mm |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.42 mm (sub1 to L_pinky); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 32.6 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 17.5 / 18.0 / 19.2 mm, right 13.8 / 13.2 / 17.3 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 19.4 / 19.4 / 20.9, right 15.2 / 14.3 / 18.5 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 33.7 mm, right 31.3 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 36.2, right 33.6 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -6.6, left middle +10.9, right ring -5.2, right middle +7.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 30.4 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 30.5 mm across (toward the player), +0.8 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 10.8 mm, -115° off the normal of the left-hand line (-4.4 mm forward, -9.5 mm toward the index); at the outer skin 11.4 mm; sub2 from R_middle: 8.7 mm, +38° off the normal of the right-hand line (+6.8 mm forward, +5.4 mm toward the index); at the outer skin 9.2 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.8 mm (centre 12.7), tail 9.7 mm (centre 12.5); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +8.3 mm from R middle (ok -8 to +3), L thumb +16.8 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage2/P0-125/P0-125.stl`, air_capped_stl: `addon_out/stage2/P0-125/P0-125_air_capped.stl`, air_fem_stl: `addon_out/stage2/P0-125/P0-125_air_fem.stl`, renders: `addon_renders/P0-125/`, measurement_template: `addon_out/stage2/P0-125/P0-125_measurement.toml`, check_report: `addon_checks/P0-125.md`.

### P1-80

- Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 4 warnings (soft ergonomic checks, never failures): ergo_hand_span, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 80.011 cm³ against the model target 80.000 cm³ (+0.013 %). Cavity mesh 78.11 cm³ (1.94 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 110.1 mm. Plastic 49.3 cm³.

| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 3.56 | 0.0 | 4.0 | **3.34** | 3.56 | 3.343 | 3.999 | 10 | ok |
| sub2 | C5 | 2.55 | 3.0 | 7.0 | **3.06** | 3.17 | 3.057 | 6.996 | 10 | ok |
| R_pinky | D5 | 4.47 | 0.0 | 4.0 | **4.16** | 4.47 | 4.161 | 3.999 | 10 | ok |
| R_ring | E5 | 5.24 | 0.0 | 4.0 | **4.83** | 5.24 | 4.835 | 3.999 | 10 | ok |
| R_middle | F5 | 3.68 | 0.0 | 4.0 | **3.45** | 3.68 | 3.452 | 4.000 | 10 | ok |
| R_index | G5 | 6.68 | 0.0 | 4.0 | **6.09** | 6.68 | 6.094 | 3.999 | 10 | ok |
| L_pinky | A5 | 7.89 | 0.0 | 4.0 | **7.14** | 7.89 | 7.141 | 3.999 | 10 | ok |
| L_ring | B5 | 9.35 | 0.0 | 4.0 | **8.39** | 9.35 | 8.395 | 4.000 | 10 | ok |
| L_middle | C6 | 6.34 | 0.0 | 4.0 | **5.80** | 6.33 | 5.805 | 4.000 | 10 | ok |
| L_index | D6 | 12.12 | 0.0 | 4.0 | **10.76** | 12.11 | 10.758 | 3.999 | 10 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| L_thumb | E6 | 14.40 | 0.0 | 4.0 | **12.71** | 14.39 | 12.715 | 4.000 | 12 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| R_thumb | F6 | 9.50 | 0.0 | 4.0 | **8.56** | 9.49 | 8.563 | 3.999 | 12 | ok |

All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.83; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.13 x F6: below 1.3, so a FEM check of the top fingerings is required (the kernel's own status: needs_fem). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P1-80_air_capped.stl; holes and window closed): 2277 Hz = 1.63 × F6 on a 1.5 mm grid of 23694 cells (2 mm grid: 2264 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.959 + voicing pocket 0.154) = 78.1126 cm³ against the kernel's 78.1125 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 80.0105 cm³ (+0.0132 %), air mesh 80.0099 cm³ (+0.0124 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.40 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset +0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 31.6 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.48 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_ring), largest chimney error -0.0040 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 23.9 mm to the opposite wall, 41.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.81° (L_middle); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.63 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -10.2 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +10.7 mm (35 % of the half section there); the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 22.6 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.77 mm |
| `ergo_finger_pitch` | pass | left 17.2 / 17.6 / 16.9 mm, right 17.2 / 18.0 / 17.3 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.7 / 18.7 / 18.0, right 18.0 / 18.3 / 18.0 mm |
| `ergo_hand_span` | WARN | hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.2 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.3, right 51.9 mm |
| `ergo_arch` | pass | left ring +3.2, left middle +4.0, right ring +3.7, right middle +4.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +2.1° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 21.1 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +16.1°, right line +14.0° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 21.1 mm across (toward the player), -0.4 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 9.5 mm, +0° off the normal of the left-hand line (+9.4 mm forward, +0.0 mm toward the index); at the outer skin 10.7 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.6 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | the bulb end is 4.8 mm too short: 5.2 mm past the L pinky hole edge; the tail end is 5.2 mm too short: 4.8 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 5.2 mm (centre 8.8), tail 4.8 mm (centre 6.8); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | L_pinky leans 38° toward the bulb end; R_pinky leans 30° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +38°, L_ring +15°, L_middle -0°, L_index -14°, R_pinky +30°, R_ring +15°, R_middle +11°, R_index +5°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 13° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -0°, L_ring +0°, L_middle +4°, L_index +17°, R_pinky -13°, R_ring -3°, R_middle +7°, R_index +22°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.2 mm from R middle (ok -8 to +3), L thumb +8.6 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage2/P1-80/P1-80.stl`, air_capped_stl: `addon_out/stage2/P1-80/P1-80_air_capped.stl`, air_fem_stl: `addon_out/stage2/P1-80/P1-80_air_fem.stl`, renders: `addon_renders/P1-80/`, measurement_template: `addon_out/stage2/P1-80/P1-80_measurement.toml`, check_report: `addon_checks/P1-80.md`.

### P2-80

- Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 5 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 80.008 cm³ against the model target 80.000 cm³ (+0.010 %). Cavity mesh 78.11 cm³ (1.94 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 124.9 mm. Plastic 52.2 cm³.

| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 3.56 | 0.0 | 4.0 | **3.34** | 3.56 | 3.343 | 3.999 | 10 | ok |
| sub2 | C5 | 2.55 | 3.0 | 7.0 | **3.06** | 3.17 | 3.057 | 6.999 | 10 | ok |
| R_pinky | D5 | 4.47 | 0.0 | 4.0 | **4.16** | 4.47 | 4.161 | 4.000 | 10 | ok |
| R_ring | E5 | 5.24 | 0.0 | 4.0 | **4.83** | 5.24 | 4.835 | 4.000 | 10 | ok |
| R_middle | F5 | 3.68 | 0.0 | 4.0 | **3.45** | 3.68 | 3.452 | 4.000 | 10 | ok |
| R_index | G5 | 6.68 | 0.0 | 4.0 | **6.09** | 6.68 | 6.094 | 4.000 | 10 | ok |
| L_pinky | A5 | 7.89 | 0.0 | 4.0 | **7.14** | 7.89 | 7.141 | 4.000 | 10 | ok |
| L_ring | B5 | 9.35 | 0.0 | 4.0 | **8.39** | 9.35 | 8.395 | 3.999 | 10 | ok |
| L_middle | C6 | 6.34 | 0.0 | 4.0 | **5.80** | 6.33 | 5.805 | 3.999 | 10 | ok |
| L_index | D6 | 12.12 | 0.0 | 4.0 | **10.76** | 12.11 | 10.758 | 4.000 | 10 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| L_thumb | E6 | 14.40 | 0.0 | 4.0 | **12.71** | 14.39 | 12.715 | 3.999 | 12 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| R_thumb | F6 | 9.50 | 0.0 | 4.0 | **8.56** | 9.49 | 8.563 | 4.000 | 12 | ok |

All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.83; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.99 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P2-80_air_capped.stl; holes and window closed): 1959 Hz = 1.40 × F6 on a 1.5 mm grid of 23718 cells (2 mm grid: 1948 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.936 + voicing pocket 0.177) = 78.1127 cm³ against the kernel's 78.1125 cm³: +0.0002 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 80.0078 cm³ (+0.0098 %), air mesh 80.0071 cm³ (+0.0089 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.51 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset +0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 31.0 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.98 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (L_ring), largest chimney error -0.0008 mm (sub1); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 17.2 mm to the opposite wall, 45.9 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.12° (R_index); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.63 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -8.7 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.5 mm (35 % of the half section there); the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 18.7 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.80 mm |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.4 mm. Measured: left 17.1 / 17.6 / 16.4 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.4 / 18.8 / 17.5, right 17.4 / 18.0 / 16.9 mm |
| `ergo_hand_span` | WARN | hand span out of range: left hand 48.9 mm. Measured: left 48.9 mm, right 50.8 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.2, right 51.0 mm |
| `ergo_arch` | pass | left ring +2.9, left middle +3.4, right ring +3.3, right middle +3.4 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +2.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 18.7 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.8°, right line +12.2° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 18.7 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 9.5 mm, +0° off the normal of the left-hand line (+9.5 mm forward, +0.0 mm toward the index); at the outer skin 10.5 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.5 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | the bulb end is 0.6 mm too short: 9.4 mm past the L pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 9.4 mm (centre 13.0), tail 12.4 mm (centre 14.4); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | L_pinky leans 29° toward the bulb end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +29°, L_ring +11°, L_middle -6°, L_index -19°, R_pinky +12°, R_ring +8°, R_middle +8°, R_index +9°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 7° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +2°, L_ring +1°, L_middle +1°, L_index +12°, R_pinky -7°, R_ring -3°, R_middle +5°, R_index +19°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.4 mm from R middle (ok -8 to +3), L thumb +9.0 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage2/P2-80/P2-80.stl`, air_capped_stl: `addon_out/stage2/P2-80/P2-80_air_capped.stl`, air_fem_stl: `addon_out/stage2/P2-80/P2-80_air_fem.stl`, renders: `addon_renders/P2-80/`, measurement_template: `addon_out/stage2/P2-80/P2-80_measurement.toml`, check_report: `addon_checks/P2-80.md`.

### P3-80

- Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 6 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_hand_offset, ergo_index_meet, ergo_rest_space, ergo_hole_lean_end.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 80.006 cm³ against the model target 80.000 cm³ (+0.007 %). Cavity mesh 78.11 cm³ (1.94 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 94.3 mm. Plastic 47.9 cm³.

| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 3.56 | 0.0 | 4.0 | **3.34** | 3.56 | 3.343 | 4.000 | 10 | ok |
| sub2 | C5 | 2.55 | 3.0 | 7.0 | **3.06** | 3.17 | 3.057 | 6.996 | 10 | ok |
| R_pinky | D5 | 4.47 | 0.0 | 4.0 | **4.16** | 4.47 | 4.161 | 3.999 | 10 | ok |
| R_ring | E5 | 5.24 | 0.0 | 4.0 | **4.83** | 5.24 | 4.835 | 4.000 | 10 | ok |
| R_middle | F5 | 3.68 | 0.0 | 4.0 | **3.45** | 3.68 | 3.452 | 4.000 | 10 | ok |
| R_index | G5 | 6.68 | 0.0 | 4.0 | **6.09** | 6.68 | 6.094 | 3.999 | 10 | ok |
| L_pinky | A5 | 7.89 | 0.0 | 4.0 | **7.14** | 7.89 | 7.141 | 4.000 | 10 | ok |
| L_ring | B5 | 9.35 | 0.0 | 4.0 | **8.39** | 9.35 | 8.395 | 3.999 | 10 | ok |
| L_middle | C6 | 6.34 | 0.0 | 4.0 | **5.80** | 6.33 | 5.805 | 4.000 | 10 | ok |
| L_index | D6 | 12.12 | 0.0 | 4.0 | **10.76** | 12.11 | 10.758 | 3.999 | 10 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| L_thumb | E6 | 14.40 | 0.0 | 4.0 | **12.71** | 14.39 | 12.715 | 4.000 | 12 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| R_thumb | F6 | 9.50 | 0.0 | 4.0 | **8.56** | 9.49 | 8.563 | 4.000 | 12 | ok |

All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.83; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.32 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P3-80_air_capped.stl; holes and window closed): 2452 Hz = 1.76 × F6 on a 1.5 mm grid of 23710 cells (2 mm grid: 2443 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.958 + voicing pocket 0.155) = 78.1127 cm³ against the kernel's 78.1125 cm³: +0.0002 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 80.0058 cm³ (+0.0073 %), air mesh 80.0062 cm³ (+0.0077 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.13 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 26.5 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.80 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (sub2), largest chimney error -0.0039 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 28.2 mm to the opposite wall, 33.9 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.91° (sub1); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.41 mm (sub2 to L_index); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 1.31 mm (L_index; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; each hand was slid 12 mm along its own line toward the other hand (preset value hand_overlap_mm); the finger pitch is unchanged; R_index: the sideways offset was limited from -15.4 to -11.2 mm (35 % of the half section there); L_index: the sideways offset was limited from +14.8 to +11.0 mm (35 % of the half section there); the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 17.6 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.90 mm |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.3 mm. Measured: left 17.0 / 17.4 / 16.3 mm, right 17.1 / 18.1 / 17.1 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.0 / 18.0 / 17.0, right 18.4 / 18.8 / 17.8 mm |
| `ergo_hand_span` | WARN | hand span out of range: left hand 49.4 mm. Measured: left 49.4 mm, right 51.0 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.5, right 53.6 mm |
| `ergo_arch` | pass | left ring +3.3, left middle +2.9, right ring +1.9, right middle +1.7 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines -5.3° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | hand lines 17.5 mm apart across. Measured: the right-hand line is 17.5 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +9.5°, right line +14.8° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | index holes 17.6 mm apart across; R index -23.3 mm along the hand axis from L index. Measured: R index from L index: 17.6 mm across (toward the player), -23.3 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 9.5 mm, +0° off the normal of the left-hand line (+9.5 mm forward, +0.0 mm toward the index); at the outer skin 10.5 mm; sub2 from R_middle: 7.5 mm, -0° off the normal of the right-hand line (+7.5 mm forward, -0.0 mm toward the index); at the outer skin 8.2 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | the bulb end is 0.0 mm too short: 10.0 mm past the L pinky hole edge; the tail end is 2.2 mm too short: 7.8 mm past the R pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 10.0 mm (centre 13.6), tail 7.8 mm (centre 9.9); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | L_pinky leans 23° toward the bulb end; R_pinky leans 31° toward the tail end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +23°, L_ring +9°, L_middle -0°, L_index -8°, R_pinky +31°, R_ring +12°, R_middle +2°, R_index -8°; ok up to 20° |
| `ergo_hole_lean_side` | pass | lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +10°, L_ring +5°, L_middle +8°, L_index +16°, R_pinky +5°, R_ring +4°, R_middle +8°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.8 mm from R middle (ok -8 to +3), L thumb +9.0 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage2/P3-80/P3-80.stl`, air_capped_stl: `addon_out/stage2/P3-80/P3-80_air_capped.stl`, air_fem_stl: `addon_out/stage2/P3-80/P3-80_air_fem.stl`, renders: `addon_renders/P3-80/`, measurement_template: `addon_out/stage2/P3-80/P3-80_measurement.toml`, check_report: `addon_checks/P3-80.md`.

### P0-80-b

*Repeatability copy of P0-80: the same geometry (doc 02 A7).*

- Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 80.009 cm³ against the model target 80.000 cm³ (+0.011 %). Cavity mesh 78.11 cm³ (1.94 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 78.3 mm. Plastic 44.7 cm³.

| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 3.56 | 0.0 | 4.0 | **3.34** | 3.56 | 3.343 | 3.999 | 10 | ok |
| sub2 | C5 | 2.55 | 3.0 | 7.0 | **3.06** | 3.17 | 3.057 | 6.998 | 10 | ok |
| R_pinky | D5 | 4.47 | 0.0 | 4.0 | **4.16** | 4.47 | 4.161 | 4.000 | 10 | ok |
| R_ring | E5 | 5.24 | 0.0 | 4.0 | **4.83** | 5.24 | 4.835 | 4.000 | 10 | ok |
| R_middle | F5 | 3.68 | 0.0 | 4.0 | **3.45** | 3.68 | 3.452 | 4.000 | 10 | ok |
| R_index | G5 | 6.68 | 0.0 | 4.0 | **6.09** | 6.68 | 6.094 | 4.000 | 10 | ok |
| L_pinky | A5 | 7.89 | 0.0 | 4.0 | **7.14** | 7.89 | 7.141 | 3.999 | 10 | ok |
| L_ring | B5 | 9.35 | 0.0 | 4.0 | **8.39** | 9.35 | 8.395 | 3.999 | 10 | ok |
| L_middle | C6 | 6.34 | 0.0 | 4.0 | **5.80** | 6.33 | 5.805 | 4.000 | 10 | ok |
| L_index | D6 | 12.12 | 0.0 | 4.0 | **10.76** | 12.11 | 10.758 | 3.999 | 10 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| L_thumb | E6 | 14.40 | 0.0 | 4.0 | **12.71** | 14.39 | 12.715 | 4.000 | 12 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| R_thumb | F6 | 9.50 | 0.0 | 4.0 | **8.56** | 9.49 | 8.563 | 4.000 | 12 | ok |

All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.83; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.57 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-80-b_air_capped.stl; holes and window closed): 2927 Hz = 2.10 × F6 on a 1.5 mm grid of 23759 cells (2 mm grid: 2920 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.975 + voicing pocket 0.138) = 78.1126 cm³ against the kernel's 78.1125 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 80.0092 cm³ (+0.0115 %), air mesh 80.0076 cm³ (+0.0095 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.36 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 32.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.21 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (sub1), largest chimney error -0.0021 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 32.0 mm to the opposite wall, 34.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.90° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.28 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 30.9 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 15.2 / 15.6 / 16.6 mm, right 11.9 / 11.4 / 14.9 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.0 / 16.9 / 18.3, right 13.3 / 12.5 / 16.2 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 29.1 mm, right 27.0 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 31.6, right 29.3 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -5.7, left middle +9.4, right ring -4.5, right middle +6.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 26.3 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 26.3 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 9.3 mm, -115° off the normal of the left-hand line (-3.8 mm forward, -8.2 mm toward the index); at the outer skin 9.9 mm; sub2 from R_middle: 7.5 mm, +38° off the normal of the right-hand line (+5.9 mm forward, +4.6 mm toward the index); at the outer skin 8.0 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.9 mm (centre 11.5), tail 9.2 mm (centre 11.3); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.1 mm from R middle (ok -8 to +3), L thumb +14.5 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage2/P0-80-b/P0-80-b.stl`, air_capped_stl: `addon_out/stage2/P0-80-b/P0-80-b_air_capped.stl`, air_fem_stl: `addon_out/stage2/P0-80-b/P0-80-b_air_fem.stl`, measurement_template: `addon_out/stage2/P0-80-b/P0-80-b_measurement.toml`, check_report: `addon_checks/P0-80-b.md`.

### P0-80-c

*Repeatability copy of P0-80: the same geometry (doc 02 A7).*

- Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 80.00 cm³ (capped air). Measured on the STL: 80.009 cm³ against the model target 80.000 cm³ (+0.011 %). Cavity mesh 78.11 cm³ (1.94 cm³ of air in the holes, 0.05 cm³ of tube wall). Cavity spine length 78.3 mm. Plastic 44.7 cm³.

| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | B4 | 3.56 | 0.0 | 4.0 | **3.34** | 3.56 | 3.343 | 3.999 | 10 | ok |
| sub2 | C5 | 2.55 | 3.0 | 7.0 | **3.06** | 3.17 | 3.057 | 6.998 | 10 | ok |
| R_pinky | D5 | 4.47 | 0.0 | 4.0 | **4.16** | 4.47 | 4.161 | 4.000 | 10 | ok |
| R_ring | E5 | 5.24 | 0.0 | 4.0 | **4.83** | 5.24 | 4.835 | 4.000 | 10 | ok |
| R_middle | F5 | 3.68 | 0.0 | 4.0 | **3.45** | 3.68 | 3.452 | 4.000 | 10 | ok |
| R_index | G5 | 6.68 | 0.0 | 4.0 | **6.09** | 6.68 | 6.094 | 4.000 | 10 | ok |
| L_pinky | A5 | 7.89 | 0.0 | 4.0 | **7.14** | 7.89 | 7.141 | 3.999 | 10 | ok |
| L_ring | B5 | 9.35 | 0.0 | 4.0 | **8.39** | 9.35 | 8.395 | 3.999 | 10 | ok |
| L_middle | C6 | 6.34 | 0.0 | 4.0 | **5.80** | 6.33 | 5.805 | 4.000 | 10 | ok |
| L_index | D6 | 12.12 | 0.0 | 4.0 | **10.76** | 12.11 | 10.758 | 3.999 | 10 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| L_thumb | E6 | 14.40 | 0.0 | 4.0 | **12.71** | 14.39 | 12.715 | 4.000 | 12 | k 1.0 above the pad limit, k 0.8 above the pad limit |
| R_thumb | F6 | 9.50 | 0.0 | 4.0 | **8.56** | 9.49 | 8.563 | 4.000 | 12 | ok |

All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.83; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.57 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-80-c_air_capped.stl; holes and window closed): 2927 Hz = 2.10 × F6 on a 1.5 mm grid of 23759 cells (2 mm grid: 2920 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.975 + voicing pocket 0.138) = 78.1126 cm³ against the kernel's 78.1125 cm³: +0.0001 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 80.0092 cm³ (+0.0115 %), air mesh 80.0076 cm³ (+0.0095 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.36 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 32.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.21 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (sub1), largest chimney error -0.0021 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 32.0 mm to the opposite wall, 34.0 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.90° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.28 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 30.9 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 15.2 / 15.6 / 16.6 mm, right 11.9 / 11.4 / 14.9 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.0 / 16.9 / 18.3, right 13.3 / 12.5 / 16.2 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 29.1 mm, right 27.0 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 31.6, right 29.3 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -5.7, left middle +9.4, right ring -4.5, right middle +6.3 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 26.3 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 26.3 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 9.3 mm, -115° off the normal of the left-hand line (-3.8 mm forward, -8.2 mm toward the index); at the outer skin 9.9 mm; sub2 from R_middle: 7.5 mm, +38° off the normal of the right-hand line (+5.9 mm forward, +4.6 mm toward the index); at the outer skin 8.0 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.9 mm (centre 11.5), tail 9.2 mm (centre 11.3); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.1 mm from R middle (ok -8 to +3), L thumb +14.5 mm from L pinky (ok +4 to +10) |

Files: stl: `addon_out/stage2/P0-80-c/P0-80-c.stl`, air_capped_stl: `addon_out/stage2/P0-80-c/P0-80-c_air_capped.stl`, air_fem_stl: `addon_out/stage2/P0-80-c/P0-80-c_air_fem.stl`, measurement_template: `addon_out/stage2/P0-80-c/P0-80-c_measurement.toml`, check_report: `addon_checks/P0-80-c.md`.

