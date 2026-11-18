# Geometry check: P0-95-el-p1-m4-lab02

Written by `tools/geometry_check_variant.py -- P0 95 el-p1-m4-lab02 stub_style=neck window_cut=ellipse pocket_blend_radius_mm=12 cone_widen_share=0.45 shelf_angle_deg=50 windway_pitch_deg=-4`: preset P0 with stub_style=neck window_cut=ellipse pocket_blend_radius_mm=12 cone_widen_share=0.45 shelf_angle_deg=50 windway_pitch_deg=-4. Every measured number comes from the STL file `addon_out/P0-95-el-p1-m4-lab02/P0-95-el-p1-m4-lab02.stl`, read back from disk (81496 triangles).

Result: **UNEXPECTED FAILURES: windway_floor_lip**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 11 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hand_span, ergo_arch, ergo_hands_parallel, ergo_hand_offset, ergo_index_meet, ergo_subholes, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side, ergo_thumbs. Build and check time 43 s.

- Preset P0, V0 95.00 cm³, voice rating medium, holes cut at the `print` diameters.
- Voicing hash `7b411d5079d7`: teardrop window 9.65 × 11.10 mm, 81.15 mm², windway exit 1.20 × 11.10 mm, W/h 8.04.
- Cavity spine length 82.86 mm (length behind the kernel's c/(2L) estimate: 83.66 mm, P0 egg).
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).

## Checks

`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. `info` is a reported number that decides nothing.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.82; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 1.49 x F6 (rule: at least 1.3) (the kernel's own status: pass). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | L_index 12.25 mm above the 10 mm pad limit; L_thumb 14.51 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_ring 10.67 mm above the 10 mm pad limit; L_index 13.87 mm above the 10 mm pad limit; L_thumb 16.52 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P0-95-el-p1-m4-lab02_air_capped.stl; holes and window closed): 2774 Hz = 1.99 × F6 on a 1.5 mm grid of 28139 cells (2 mm grid: 2764 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 92.278 + voicing pocket 0.267) = 92.5450 cm³ against the kernel's 92.5445 cm³: +0.0005 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 95.0135 cm³ (+0.0142 %), air mesh 95.0114 cm³ (+0.0120 %), against V0 95.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 2.61 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 7b411d5079d7; recomputed from the record: 7b411d5079d7 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 11.102 mm, 81.19 mm² (record 9.650 × 11.102, 81.15); windway exit 1.200 × 11.102 mm, inlet 1.560 × 11.102 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 11.102 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.60 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 35.0 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | FAIL | plastic under the windway floor at the exit: 0.49 mm (at least 0.8 mm); windway roof 3.00 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (L_pinky), largest chimney error -0.0022 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 1.500 mm (kernel 1.5), wall 1.198 mm, 35.6 mm to the opposite wall, 37.6 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 0.89° (sub2); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.52 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'relative'; taped test body, not a hand layout |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 31.4 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 3.78 mm |
| `ergo_finger_pitch` | WARN | taped test body, not a hand layout. Measured: left 16.0 / 16.5 / 17.5 mm, right 12.6 / 12.1 / 15.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.9 / 17.8 / 19.2, right 14.0 / 13.2 / 17.1 mm |
| `ergo_hand_span` | WARN | taped test body, not a hand layout. Measured: left 30.8 mm, right 28.6 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 33.3, right 30.8 mm |
| `ergo_arch` | WARN | taped test body, not a hand layout. Measured: left ring -6.0, left middle +10.0, right ring -4.7, right middle +6.6 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | WARN | taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | WARN | taped test body, not a hand layout. Measured: the right-hand line is 27.8 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | WARN | taped test body, not a hand layout. Measured: R index from L index: 27.9 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | WARN | taped test body, not a hand layout. Measured: sub1 from L_middle: 9.8 mm, -115° off the normal of the left-hand line (-4.0 mm forward, -8.7 mm toward the index); at the outer skin 10.4 mm; sub2 from R_middle: 8.0 mm, +38° off the normal of the right-hand line (+6.2 mm forward, +4.9 mm toward the index); at the outer skin 8.4 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.9 mm (centre 11.9), tail 9.4 mm (centre 11.7); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | WARN | taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.5 mm from R middle (ok -8 to +3), L thumb +15.3 mm from L pinky (ok +4 to +10) |

## Warnings

Soft ergonomic checks outside their range. They are measurements to judge, not failures.

- `ergo_finger_pitch`: taped test body, not a hand layout. Measured: left 16.0 / 16.5 / 17.5 mm, right 12.6 / 12.1 / 15.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.9 / 17.8 / 19.2, right 14.0 / 13.2 / 17.1 mm
- `ergo_hand_span`: taped test body, not a hand layout. Measured: left 30.8 mm, right 28.6 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 33.3, right 30.8 mm
- `ergo_arch`: taped test body, not a hand layout. Measured: left ring -6.0, left middle +10.0, right ring -4.7, right middle +6.6 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm
- `ergo_hands_parallel`: taped test body, not a hand layout. Measured: angle between the two hand lines +9.2° (+ = they open toward the tail); ok within ±10°
- `ergo_hand_offset`: taped test body, not a hand layout. Measured: the right-hand line is 27.8 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +37.6°, right line +28.5° (+ = the tail end of the line is farther from the player)
- `ergo_index_meet`: taped test body, not a hand layout. Measured: R index from L index: 27.9 mm across (toward the player), +0.7 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along
- `ergo_subholes`: taped test body, not a hand layout. Measured: sub1 from L_middle: 9.8 mm, -115° off the normal of the left-hand line (-4.0 mm forward, -8.7 mm toward the index); at the outer skin 10.4 mm; sub2 from R_middle: 8.0 mm, +38° off the normal of the right-hand line (+6.2 mm forward, +4.9 mm toward the index); at the outer skin 8.4 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal
- `ergo_rest_space`: taped test body, not a hand layout. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 7.9 mm (centre 11.9), tail 9.4 mm (centre 11.7); ok at least 10 mm
- `ergo_hole_lean_end`: taped test body, not a hand layout. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +32°, L_ring +9°, L_middle +10°, L_index -6°, R_pinky +31°, R_ring +12°, R_middle +12°, R_index -4°; ok up to 20°
- `ergo_hole_lean_side`: taped test body, not a hand layout. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky +6°, L_ring +20°, L_middle -0°, L_index +18°, R_pinky +14°, R_ring +21°, R_middle +4°, R_index +16°; ok up to 45° toward it and up to 5° away
- `ergo_thumbs`: taped test body, not a hand layout. Measured: along the hand axis, + toward the tail: R thumb +7.5 mm from R middle (ok -8 to +3), L thumb +15.3 mm from L pinky (ok +4 to +10)

## Hand layout

Measured in the frame of the hands (`ocarina_addon/ergonomics.py`, the metrics of docs/06). The `ergo_*` checks use the hole centres **on the cavity surface**, as docs/06 did for the add-on bodies. The column *at the outer skin* gives the same number 4 mm further out along each hole axis, where the fingers are; the hole axes spread outward, so it is larger. It decides nothing. **This body is a taped test body, not a hand layout.**

| Quantity | On the cavity surface (checked) | At the outer skin |
| --- | --- | --- |
| Left hand, pinky → ring → middle → index, straight 3D distance | 16.0 / 16.5 / 17.5 mm | 17.9 / 17.8 / 19.2 mm |
| Right hand, pinky → ring → middle → index, straight 3D distance | 12.6 / 12.1 / 15.8 mm | 14.0 / 13.2 / 17.1 mm |
| Hand span pinky to index, left / right (plan view) | 30.8 / 28.6 mm | 33.3 / 30.8 mm |
| Pinky to pinky (plan view) | 66.0 mm | 70.2 mm |
| Arch, ring and middle: left / right | -6.0, 10.0 / -4.7, 6.6 mm | -6.6, 10.9 / -5.2, 7.3 mm |
| Angle between the hand lines | 9.2° | 9.5° |
| Right-hand line nearer the player by | 27.8 mm | 30.1 mm |
| R index from L index: across / along the hand axis | 27.9 / 0.7 mm | 30.2 / -0.4 mm |
| sub1: nearest finger hole, distance, off the normal of that hand line | L_middle, 9.83 mm, -115° | L_middle, 10.44 mm, -115° |
| sub2: nearest finger hole, distance, off the normal of that hand line | R_middle, 7.97 mm, 38° | R_middle, 8.43 mm, 36° |
| L thumb from L pinky / R thumb from R middle, along the hand axis | 15.3 / 7.5 mm | 17.1 / 8.3 mm |
| Body end from the pinky hole centre, bulb / tail (plan view, along the hand axis) | 11.9 / 11.7 mm | – |
| The same from the hole edge (the rest space) | 7.9 / 9.4 mm | – |

Lean of each finger hole (angle of the hole axis against the normal of the finger face). *Toward the end*: along the hand axis toward the nearer end of the body. *Toward the hand*: across the hand axis toward the hand that covers the hole (left hand: the far side; right hand: the player).

| Hole | Total lean | Toward the end | Toward the hand | Mostly toward |
| --- | --- | --- | --- | --- |
| L_pinky | 32° | +32° | +6° | bulb |
| L_ring | 22° | +9° | +20° | far |
| L_middle | 10° | +10° | -0° | bulb |
| L_index | 19° | -6° | +18° | far |
| R_pinky | 33° | +31° | +14° | tail |
| R_ring | 23° | +12° | +21° | player |
| R_middle | 13° | +12° | +4° | tail |
| R_index | 16° | -4° | +16° | player |

Layout record: kind `relative`; smallest planned gaps sub2–R_middle 4.52, sub1–L_pinky 4.67, sub1–L_middle 4.71, L_ring–L_index 6.58, sub1–L_ring 7.21 mm.

## Volumes

- Cavity mesh: loft 92.2783 cm³ + voicing pocket 0.2667 cm³ = 92.5450 cm³; kernel target 92.5445 cm³.
- Capped air: 95.0135 cm³ measured on the STL by column integration (0.25 mm grid), 95.0114 cm³ as the air mesh; target 95.0000 cm³ (kernel V0 95.0000 cm³, volume factor 1). Kernel bookkeeping: 2.480 cm³ of air in the holes, 0.024 cm³ of tube wall.
- Plastic volume of the body 52.73 cm³. Air with the window throat (FEM export) 95.3359 cm³.
- Exported air files: capped 95.0114 cm³ (manifold True, shells 1); with throat 95.3359 cm³ (manifold True).
- Cavity-mode desk check: first mode 2774 Hz, second 3982 Hz, top note 1396.9 Hz, speed of sound 347.3 m/s; voxel volume 94.97 cm³ on the 1.5 mm grid; numpy 2.5.4, scipy 1.18.1, python 3.12.10.

## Booleans

| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |
| --- | --- | --- | --- | --- |
| cavity + voicing pocket (air) | MANIFOLD | +266.72 | between +0 and +3563 | yes |
| skin + voicing block | MANIFOLD | +7355.31 | between +0 and +28306 | yes |
| envelope - cavity air | MANIFOLD | -92545.00 | -92545.00 | yes |
| tube sub2 | MANIFOLD | +34.14 | +35.05 | yes |
| hole sub1 | MANIFOLD | -43.60 | -43.59 | yes |
| hole sub2 | MANIFOLD | -40.31 | -40.42 | yes |
| hole R_pinky | MANIFOLD | -68.16 | -68.07 | yes |
| hole R_ring | MANIFOLD | -92.50 | -92.41 | yes |
| hole R_middle | MANIFOLD | -46.54 | -46.53 | yes |
| hole R_index | MANIFOLD | -148.30 | -148.14 | yes |
| hole L_pinky | MANIFOLD | -205.46 | -204.67 | yes |
| hole L_ring | MANIFOLD | -285.47 | -284.58 | yes |
| hole L_middle | MANIFOLD | -134.09 | -133.98 | yes |
| hole L_index | MANIFOLD | -473.30 | -471.37 | yes |
| hole L_thumb | MANIFOLD | -666.57 | -661.58 | yes |
| hole R_thumb | MANIFOLD | -296.17 | -295.23 | yes |
| window throat + labium ramp | MANIFOLD | -611.61 | -611.46 | yes |
| windway | MANIFOLD | -464.86 | -464.95 | yes |

## Voicing, measured on the mesh

| Quantity | Measured | Voicing record |
| --- | --- | --- |
| Window length (windway exit to labium) | 9.650 mm | 9.650 mm |
| Window width (broad end) | 11.102 mm | 11.102 mm |
| Window area | 81.19 mm² | 81.15 mm² |
| Widest point, from the windway exit | 4.605 mm | 4.605 mm |
| Windway exit height × width | 1.200 × 11.102 mm | 1.200 × 11.102 mm |
| Windway inlet height × width | 1.560 × 11.102 mm | 1.560 × 11.102 mm |
| Labium ramp angle | 20.00° | 20.00° |
| Labium edge thickness | 0.400 mm | 0.400 mm |
| Labium edge against the windway centre line | -0.200 mm | -0.200 mm |
| Windway roof thickness / floor lip at the exit | 3.00 / 0.49 mm | – |
| Free depth below the window (keep-out 10 mm) | 35.0 mm | – |

## Holes, measured on the mesh

Diameter: from the area of the bore in a slice at mid wall. Chimney: a ray along the hole axis through the wall before the hole is cut (doc 02, Phase 4 step 5). Bore wall: mean length of the cut bore wall in the final mesh (it is a little longer than the axis chimney on a curved wall). Axis: angle between the bore axis and the normal of the cavity mesh.

| Hole | Deck | d kernel | d measured | Error | Chimney kernel | Chimney measured | Error | Bore wall | Tube | Axis ° | Moved | Nearest gap | To window | To ramp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | top | 3.725 | 3.725 | -0.0000 | 4.00 | 3.999 | -0.0006 | 4.00 | – | 0.22 | 0.00 | 4.67 (L_pinky) | 40.3 | 38.3 |
| sub2 | top | 3.059 | 3.059 | -0.0000 | 5.50 | 5.498 | -0.0022 | 5.48 | 1.50 mm, wall 1.20 | 0.89 | 0.00 | 4.52 (R_middle) | 46.7 | 46.1 |
| R_pinky | top | 4.655 | 4.655 | -0.0000 | 4.00 | 4.000 | -0.0004 | 4.01 | – | 0.64 | 0.00 | 7.54 (R_ring) | 48.5 | 43.4 |
| R_ring | top | 5.424 | 5.424 | +0.0000 | 4.00 | 4.000 | -0.0002 | 4.01 | – | 0.85 | 0.00 | 7.46 (R_middle) | 40.3 | 37.4 |
| R_middle | top | 3.849 | 3.849 | +0.0000 | 4.00 | 4.000 | -0.0005 | 4.00 | – | 0.48 | 0.00 | 4.52 (sub2) | 45.0 | 43.2 |
| R_index | top | 6.867 | 6.867 | +0.0000 | 4.00 | 4.000 | -0.0002 | 4.01 | – | 0.86 | 0.00 | 10.40 (R_middle) | 34.3 | 34.3 |
| L_pinky | top | 8.071 | 8.071 | -0.0000 | 4.00 | 3.999 | -0.0005 | 4.03 | – | 0.46 | 0.00 | 4.67 (sub1) | 40.5 | 36.3 |
| L_ring | top | 9.518 | 9.518 | +0.0000 | 4.00 | 3.999 | -0.0006 | 4.03 | – | 0.38 | 0.00 | 6.58 (L_index) | 46.2 | 42.8 |
| L_middle | top | 6.530 | 6.530 | +0.0000 | 4.00 | 4.000 | -0.0004 | 4.01 | – | 0.56 | 0.00 | 4.71 (sub1) | 39.1 | 38.7 |
| L_index | top | 12.249 | 12.249 | +0.0000 | 4.00 | 3.999 | -0.0008 | 4.03 | – | 0.16 | 0.00 | 6.58 (L_ring) | 45.9 | 44.7 |
| L_thumb | bottom | 14.512 | 14.512 | +0.0000 | 4.00 | 4.000 | -0.0005 | 4.06 | – | 0.56 | 0.00 | 17.30 (L_ring) | 31.4 | 22.6 |
| R_thumb | bottom | 9.694 | 9.694 | +0.0000 | 4.00 | 4.000 | -0.0005 | 4.03 | – | 0.55 | 0.00 | 20.96 (R_pinky) | 33.8 | 25.0 |

All lengths in millimetres.

## Wall and topology

- Plain wall (cavity to outside along the normal, 2321 rays): minimum 4.000 mm, median 4.000 mm.
- Thinnest plastic of the finished body away from the voicing and the tubes (6000 rays): 3.78 mm at (-3.8, -26.2, 24.8).
- Topology of the STL: 81496 triangles, manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13.

