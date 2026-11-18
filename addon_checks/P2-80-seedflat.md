# Geometry check: P2-80-seedflat

Written by `tools/geometry_check_variant.py -- P2 80 seedflat width=0.511,0.3839,0.3314,0.2869,0.2345,0.1773,0.1028 height=0.3159,0.2448,0.212,0.183,0.1468,0.1058,0.0412 exponent=2 port_u=0.35 layout_centre_from_port_mm=20`: preset P2 with width=0.511,0.3839,0.3314,0.2869,0.2345,0.1773,0.1028 height=0.3159,0.2448,0.212,0.183,0.1468,0.1058,0.0412 exponent=2 port_u=0.35 layout_centre_from_port_mm=20. Every measured number comes from the STL file `addon_out/P2-80-seedflat/P2-80-seedflat.stl`, read back from disk (75832 triangles).

Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); needs a closer check: cavity_mode_computed; 2 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hole_lean_side. Build and check time 48 s.

- Preset P2, V0 80.00 cm³, voice rating medium, holes cut at the `print` diameters.
- Voicing hash `d1b6418b1844`: teardrop window 9.65 × 8.81 mm, 62.84 mm², windway exit 1.20 × 8.81 mm, W/h 8.04.
- Cavity spine length 139.95 mm (length behind the kernel's c/(2L) estimate: 139.95 mm, caller).
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).

## Checks

`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. `info` is a reported number that decides nothing.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.83; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.89 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_index 10.76 mm above the 10 mm pad limit; L_thumb 12.71 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_index 12.11 mm above the 10 mm pad limit; L_thumb 14.39 mm above the 12 mm pad limit |
| `cavity_mode_computed` | NEEDS FEM | first cavity mode of the capped air mesh (P2-80-seedflat_air_capped.stl; holes and window closed): 1799 Hz = 1.29 × F6 on a 1.5 mm grid of 23702 cells (2 mm grid: 1791 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.950 + voicing pocket 0.163) = 78.1127 cm³ against the kernel's 78.1125 cm³: +0.0002 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 79.9947 cm³ (-0.0066 %), air mesh 80.0070 cm³ (+0.0087 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.41 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset +0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 24.1 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 3.35 mm (at least 0.8 mm); windway roof 3.20 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (sub2), largest chimney error -0.0042 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 19.3 mm to the opposite wall, 41.9 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.78° (L_middle); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.63 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 9.50 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -9.0 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there); the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 18.4 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.99 mm |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.9 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.5 / 18.1 / 16.9, right 17.3 / 18.2 / 17.5 mm |
| `ergo_hand_span` | pass | left 50.2 mm, right 50.7 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.5, right 51.6 mm |
| `ergo_arch` | pass | left ring +3.0, left middle +3.2, right ring +3.4, right middle +3.5 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +1.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 18.8 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.2°, right line +12.6° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 18.8 mm across (toward the player), +0.9 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 9.5 mm, +0° off the normal of the left-hand line (+9.3 mm forward, +0.0 mm toward the index); at the outer skin 10.7 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.6 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | pass | land past the pinky holes, from the hole edge along the hand axis: bulb 17.8 mm (centre 21.4), tail 14.8 mm (centre 16.9); ok at least 10 mm |
| `ergo_hole_lean_end` | pass | lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +10°, L_ring +4°, L_middle -3°, L_index -9°, R_pinky +15°, R_ring +11°, R_middle +7°, R_index +2°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 6° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -4°, L_ring -2°, L_middle +3°, L_index +16°, R_pinky -6°, R_ring -3°, R_middle +6°, R_index +19°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.5 mm from R middle (ok -8 to +3), L thumb +9.8 mm from L pinky (ok +4 to +10) |

## Warnings

Soft ergonomic checks outside their range. They are measurements to judge, not failures.

- `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.9 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.5 / 18.1 / 16.9, right 17.3 / 18.2 / 17.5 mm
- `ergo_hole_lean_side`: R_pinky leans 6° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -4°, L_ring -2°, L_middle +3°, L_index +16°, R_pinky -6°, R_ring -3°, R_middle +6°, R_index +19°; ok up to 45° toward it and up to 5° away

## Hand layout

Measured in the frame of the hands (`ocarina_addon/ergonomics.py`, the metrics of docs/06). The `ergo_*` checks use the hole centres **on the cavity surface**, as docs/06 did for the add-on bodies. The column *at the outer skin* gives the same number 4 mm further out along each hole axis, where the fingers are; the hole axes spread outward, so it is larger. It decides nothing.

| Quantity | On the cavity surface (checked) | At the outer skin |
| --- | --- | --- |
| Left hand, pinky → ring → middle → index, straight 3D distance | 17.1 / 17.7 / 16.2 mm | 17.5 / 18.1 / 16.9 mm |
| Right hand, pinky → ring → middle → index, straight 3D distance | 17.1 / 18.0 / 16.9 mm | 17.3 / 18.2 / 17.5 mm |
| Hand span pinky to index, left / right (plan view) | 50.2 / 50.7 mm | 51.5 / 51.6 mm |
| Pinky to pinky (plan view) | 103.5 mm | 105.1 mm |
| Arch, ring and middle: left / right | 3.0, 3.2 / 3.4, 3.5 mm | 3.4, 3.7 / 3.7, 3.9 mm |
| Angle between the hand lines | 1.6° | 1.2° |
| Right-hand line nearer the player by | 18.8 mm | 21.1 mm |
| R index from L index: across / along the hand axis | 18.8 / 0.9 mm | 21.1 / -0.2 mm |
| sub1: nearest finger hole, distance, off the normal of that hand line | L_ring, 9.50 mm, 0° | L_ring, 10.68 mm, -3° |
| sub2: nearest finger hole, distance, off the normal of that hand line | R_middle, 7.50 mm, 0° | R_middle, 8.58 mm, -4° |
| L thumb from L pinky / R thumb from R middle, along the hand axis | 9.8 / -7.5 mm | 10.0 / -7.3 mm |
| Body end from the pinky hole centre, bulb / tail (plan view, along the hand axis) | 21.4 / 16.9 mm | – |
| The same from the hole edge (the rest space) | 17.8 / 14.8 mm | – |

Lean of each finger hole (angle of the hole axis against the normal of the finger face). *Toward the end*: along the hand axis toward the nearer end of the body. *Toward the hand*: across the hand axis toward the hand that covers the hole (left hand: the far side; right hand: the player).

| Hole | Total lean | Toward the end | Toward the hand | Mostly toward |
| --- | --- | --- | --- | --- |
| L_pinky | 10° | +10° | -4° | bulb |
| L_ring | 5° | +4° | -2° | bulb |
| L_middle | 4° | -3° | +3° | far |
| L_index | 18° | -9° | +16° | far |
| R_pinky | 16° | +15° | -6° | tail |
| R_ring | 11° | +11° | -3° | tail |
| R_middle | 9° | +7° | +6° | tail |
| R_index | 19° | +2° | +19° | player |

Layout record: kind `template`; sub1 slides 9.50 mm from L_ring (preset 9.5 mm); sub2 slides 7.50 mm from R_middle (preset 7.5 mm); smallest planned gaps sub1–L_ring 3.63, sub2–R_middle 4.25, L_middle–L_index 7.93, L_pinky–L_ring 9.38, R_index–L_index 10.35 mm.
- R_index: the sideways offset was limited from -12.1 to -9.0 mm (35 % of the half section there)
- L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there)

## Volumes

- Cavity mesh: loft 77.9499 cm³ + voicing pocket 0.1628 cm³ = 78.1127 cm³; kernel target 78.1125 cm³.
- Capped air: 79.9947 cm³ measured on the STL by column integration (0.25 mm grid), 80.0070 cm³ as the air mesh; target 80.0000 cm³ (kernel V0 80.0000 cm³, volume factor 1). Kernel bookkeeping: 1.936 cm³ of air in the holes, 0.048 cm³ of tube wall.
- Plastic volume of the body 55.52 cm³. Air with the window throat (FEM export) 80.2583 cm³.
- Exported air files: capped 80.0070 cm³ (manifold True, shells 1); with throat 80.2583 cm³ (manifold True).
- Cavity-mode desk check: first mode 1799 Hz, second 3014 Hz, top note 1396.9 Hz, speed of sound 347.3 m/s; voxel volume 79.99 cm³ on the 1.5 mm grid; numpy 2.5.4, scipy 1.18.1, python 3.12.10.

## Booleans

| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |
| --- | --- | --- | --- | --- |
| cavity + voicing pocket (air) | MANIFOLD | +162.81 | between +0 and +1093 | yes |
| skin + voicing block | MANIFOLD | +3483.12 | between +0 and +5121 | yes |
| envelope - cavity air | MANIFOLD | -78112.67 | -78112.67 | yes |
| tube sub2 | MANIFOLD | +69.07 | +70.06 | yes |
| hole sub1 | MANIFOLD | -35.12 | -35.10 | yes |
| hole sub2 | MANIFOLD | -51.29 | -51.39 | yes |
| hole R_pinky | MANIFOLD | -54.53 | -54.39 | yes |
| hole R_ring | MANIFOLD | -73.54 | -73.43 | yes |
| hole R_middle | MANIFOLD | -37.45 | -37.43 | yes |
| hole R_index | MANIFOLD | -116.85 | -116.67 | yes |
| hole L_pinky | MANIFOLD | -160.49 | -160.21 | yes |
| hole L_ring | MANIFOLD | -221.79 | -221.40 | yes |
| hole L_middle | MANIFOLD | -105.93 | -105.85 | yes |
| hole L_index | MANIFOLD | -365.25 | -363.56 | yes |
| hole L_thumb | MANIFOLD | -510.23 | -507.88 | yes |
| hole R_thumb | MANIFOLD | -230.88 | -230.35 | yes |
| window throat + labium ramp | MANIFOLD | -560.20 | -561.18 | yes |
| windway | MANIFOLD | -371.04 | -371.55 | yes |

## Voicing, measured on the mesh

| Quantity | Measured | Voicing record |
| --- | --- | --- |
| Window length (windway exit to labium) | 9.650 mm | 9.650 mm |
| Window width (broad end) | 8.806 mm | 8.806 mm |
| Window area | 62.83 mm² | 62.84 mm² |
| Widest point, from the windway exit | 4.403 mm | 4.403 mm |
| Windway exit height × width | 1.200 × 8.806 mm | 1.200 × 8.806 mm |
| Windway inlet height × width | 1.560 × 8.806 mm | 1.560 × 8.806 mm |
| Labium ramp angle | 20.00° | 20.00° |
| Labium edge thickness | 0.400 mm | 0.400 mm |
| Labium edge against the windway centre line | +0.000 mm | +0.000 mm |
| Windway roof thickness / floor lip at the exit | 3.20 / 3.35 mm | – |
| Free depth below the window (keep-out 10 mm) | 24.1 mm | – |

## Holes, measured on the mesh

Diameter: from the area of the bore in a slice at mid wall. Chimney: a ray along the hole axis through the wall before the hole is cut (doc 02, Phase 4 step 5). Bore wall: mean length of the cut bore wall in the final mesh (it is a little longer than the axis chimney on a curved wall). Axis: angle between the bore axis and the normal of the cavity mesh.

| Hole | Deck | d kernel | d measured | Error | Chimney kernel | Chimney measured | Error | Bore wall | Tube | Axis ° | Moved | Nearest gap | To window | To ramp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | top | 3.343 | 3.343 | +0.0000 | 4.00 | 4.000 | -0.0004 | 4.00 | – | 0.73 | 0.00 | 3.63 (L_ring) | 27.1 | 27.1 |
| sub2 | top | 3.057 | 3.057 | -0.0000 | 7.00 | 6.996 | -0.0042 | 6.98 | 3.00 mm, wall 1.20 | 0.34 | 0.00 | 4.25 (R_middle) | 47.8 | 41.8 |
| R_pinky | top | 4.161 | 4.161 | +0.0000 | 4.00 | 4.000 | -0.0001 | 4.02 | – | 0.72 | 0.00 | 12.62 (R_ring) | 73.0 | 64.8 |
| R_ring | top | 4.835 | 4.835 | -0.0000 | 4.00 | 4.000 | -0.0001 | 4.01 | – | 0.72 | 0.00 | 12.62 (R_pinky) | 58.5 | 51.1 |
| R_middle | top | 3.452 | 3.452 | -0.0000 | 4.00 | 4.000 | -0.0003 | 4.00 | – | 0.55 | 0.00 | 4.25 (sub2) | 44.8 | 39.1 |
| R_index | top | 6.094 | 6.094 | -0.0000 | 4.00 | 3.999 | -0.0006 | 4.01 | – | 0.08 | 0.00 | 10.35 (L_index) | 30.5 | 27.9 |
| L_pinky | top | 7.141 | 7.141 | +0.0000 | 4.00 | 4.000 | -0.0005 | 4.01 | – | 0.44 | 0.00 | 9.38 (L_ring) | 38.9 | 34.6 |
| L_ring | top | 8.395 | 8.395 | +0.0000 | 4.00 | 4.000 | -0.0003 | 4.01 | – | 0.58 | 0.00 | 3.63 (sub1) | 31.8 | 30.7 |
| L_middle | top | 5.805 | 5.805 | -0.0000 | 4.00 | 4.000 | -0.0001 | 4.01 | – | 0.78 | 0.00 | 7.93 (L_index) | 34.0 | 34.3 |
| L_index | top | 10.758 | 10.758 | +0.0000 | 4.00 | 3.999 | -0.0007 | 4.04 | – | 0.11 | 0.00 | 7.93 (L_middle) | 37.6 | 34.4 |
| L_thumb | bottom | 12.715 | 12.715 | +0.0000 | 4.00 | 4.000 | -0.0004 | 4.04 | – | 0.45 | 0.00 | 17.07 (L_ring) | 18.4 | 8.8 |
| R_thumb | bottom | 8.563 | 8.563 | -0.0000 | 4.00 | 4.000 | -0.0005 | 4.02 | – | 0.13 | 0.00 | 17.57 (sub2) | 29.8 | 20.2 |

All lengths in millimetres.

## Wall and topology

- Plain wall (cavity to outside along the normal, 2321 rays): minimum 4.000 mm, median 4.000 mm.
- Thinnest plastic of the finished body away from the voicing and the tubes (6000 rays): 3.99 mm at (93.1, 12.5, 8.6).
- Topology of the STL: 75832 triangles, manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13.

