# Geometry check: P4-80-tb-l

Written by `Analizes_ocarinas/Neck_volume/throwback_trials.py` (trial P4:tb-l): preset P4 with stub_style=neck stub_pitch_deg=23.74 windway_pitch_deg=8 shelf_angle_deg=0 port_angle_deg=30 neck_cover_mm=2.2 neck_cover_exit_mm=1.6. Every measured number comes from the STL file `addon_out/P4-80-tb-l/P4-80-tb-l.stl`, read back from disk (82196 triangles).

Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 2 warnings (soft ergonomic checks, never failures): ergo_finger_pitch, ergo_hole_lean_side. Build and check time 53 s.

- Preset P4, V0 80.00 cm³, voice rating medium, holes cut at the `print` diameters.
- Voicing hash `5c3454b6ab15`: teardrop window 9.65 × 8.81 mm, 62.84 mm², windway exit 1.20 × 8.81 mm, W/h 8.04.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; neck standing 23.74° off the body, the pipe lowered 15.74° inside it; pocket blend 12 mm. **Prototype settings that are not in the voicing hash:** neck_cover_mm = 2.2, neck_cover_exit_mm = 1.6.
- Cavity spine length 132.04 mm (length behind the kernel's c/(2L) estimate: 132.04 mm, caller).
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).

## Checks

`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. `info` is a reported number that decides nothing.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.83; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.94 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | R_thumb 12.71 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_thumb 12.11 mm above the 12 mm pad limit; R_thumb 14.39 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P4-80-tb-l_air_capped.stl; holes and window closed): 1902 Hz = 1.36 × F6 on a 1.5 mm grid of 23733 cells (2 mm grid: 1892 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.932 + voicing pocket 0.181) = 78.1127 cm³ against the kernel's 78.1125 cm³: +0.0003 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 79.8909 cm³ (-0.1363 %), air mesh 80.0105 cm³ (+0.0131 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.76 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 5c3454b6ab15; recomputed from the record: 5c3454b6ab15 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 29.4 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 24° steep seen from the rim, 11.8 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 4.26 mm (at least 0.8 mm); windway roof 2.99 mm |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_thumb), largest chimney error -0.0044 mm (sub2); limit 0.05 mm |
| `inward_tubes` | pass | sub2: length 3.000 mm (kernel 3.0), wall 1.198 mm, 21.9 mm to the opposite wall, 41.7 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.18° (sub1); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.25 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 10.00 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -8.9 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there); the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 15.9 mm (at least 10 mm); no hole touches the voicing block or the labium ramp; the most plastic of the neck beside a rim: 0.00 mm (sub1; counted from 0.3 mm) |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 1.47 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 2.9 to 5.6 mm beyond the flat part. Back corners beside the windway exit: 8.7 mm, meets the wall; 8.5 mm, meets the wall |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.7 / 18.2 / 17.1, right 17.4 / 18.3 / 17.5 mm |
| `ergo_hand_span` | pass | left 50.1 mm, right 50.3 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.9, right 51.4 mm |
| `ergo_arch` | pass | left ring +3.0, left middle +3.2, right ring +3.3, right middle +3.5 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +1.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 18.5 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.1°, right line +12.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 18.5 mm across (toward the player), +0.9 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 10.0 mm, +0° off the normal of the left-hand line (+9.7 mm forward, +0.0 mm toward the index); at the outer skin 11.6 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.9 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | pass | land past the pinky holes, from the hole edge along the hand axis: bulb 14.5 mm (centre 18.8), tail 11.6 mm (centre 13.7); ok at least 10 mm |
| `ergo_hole_lean_end` | pass | lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +13°, L_ring +5°, L_middle -3°, L_index -12°, R_pinky +19°, R_ring +14°, R_middle +9°, R_index +3°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 10° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -5°, L_ring -3°, L_middle +4°, L_index +20°, R_pinky -10°, R_ring -4°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.4 mm from R middle (ok -8 to +3), L thumb +9.8 mm from L pinky (ok +4 to +10) |

## Warnings

Soft ergonomic checks outside their range. They are measurements to judge, not failures.

- `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.7 / 18.2 / 17.1, right 17.4 / 18.3 / 17.5 mm
- `ergo_hole_lean_side`: R_pinky leans 10° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -5°, L_ring -3°, L_middle +4°, L_index +20°, R_pinky -10°, R_ring -4°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away

## Hand layout

Measured in the frame of the hands (`ocarina_addon/ergonomics.py`, the metrics of docs/06). The `ergo_*` checks use the hole centres **on the cavity surface**, as docs/06 did for the add-on bodies. The column *at the outer skin* gives the same number 4 mm further out along each hole axis, where the fingers are; the hole axes spread outward, so it is larger. It decides nothing.

| Quantity | On the cavity surface (checked) | At the outer skin |
| --- | --- | --- |
| Left hand, pinky → ring → middle → index, straight 3D distance | 17.1 / 17.7 / 16.2 mm | 17.7 / 18.2 / 17.1 mm |
| Right hand, pinky → ring → middle → index, straight 3D distance | 17.1 / 18.0 / 16.8 mm | 17.4 / 18.3 / 17.5 mm |
| Hand span pinky to index, left / right (plan view) | 50.1 / 50.3 mm | 51.9 / 51.4 mm |
| Pinky to pinky (plan view) | 103.1 mm | 105.0 mm |
| Arch, ring and middle: left / right | 3.0, 3.2 / 3.3, 3.5 mm | 3.4, 3.7 / 3.6, 3.8 mm |
| Angle between the hand lines | 1.6° | 0.9° |
| Right-hand line nearer the player by | 18.5 mm | 21.5 mm |
| R index from L index: across / along the hand axis | 18.5 / 0.9 mm | 21.5 / -0.5 mm |
| sub1: nearest finger hole, distance, off the normal of that hand line | L_ring, 10.00 mm, 0° | L_ring, 11.56 mm, -4° |
| sub2: nearest finger hole, distance, off the normal of that hand line | R_middle, 7.50 mm, 0° | R_middle, 8.89 mm, -4° |
| L thumb from L pinky / R thumb from R middle, along the hand axis | 9.8 / -7.4 mm | 10.1 / -7.2 mm |
| Body end from the pinky hole centre, bulb / tail (plan view, along the hand axis) | 18.8 / 13.7 mm | – |
| The same from the hole edge (the rest space) | 14.5 / 11.6 mm | – |

Lean of each finger hole (angle of the hole axis against the normal of the finger face). *Toward the end*: along the hand axis toward the nearer end of the body. *Toward the hand*: across the hand axis toward the hand that covers the hole (left hand: the far side; right hand: the player).

| Hole | Total lean | Toward the end | Toward the hand | Mostly toward |
| --- | --- | --- | --- | --- |
| L_pinky | 14° | +13° | -5° | bulb |
| L_ring | 6° | +5° | -3° | bulb |
| L_middle | 5° | -3° | +4° | far |
| L_index | 23° | -12° | +20° | far |
| R_pinky | 21° | +19° | -10° | tail |
| R_ring | 14° | +14° | -4° | tail |
| R_middle | 12° | +9° | +7° | tail |
| R_index | 23° | +3° | +23° | player |

Layout record: kind `template`; sub1 slides 10.00 mm from L_ring (preset 10 mm); sub2 slides 7.50 mm from R_middle (preset 7.5 mm); smallest planned gaps sub2–R_middle 4.25, sub1–L_ring 4.76, L_middle–L_index 9.14, L_ring–L_pinky 9.30, L_ring–L_middle 9.90 mm.
- R_index: the sideways offset was limited from -12.1 to -8.9 mm (35 % of the half section there)
- L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there)

## Volumes

- Cavity mesh: loft 77.9320 cm³ + voicing pocket 0.1807 cm³ = 78.1127 cm³; kernel target 78.1125 cm³.
- Capped air: 79.8909 cm³ measured on the STL by column integration (0.25 mm grid), 80.0105 cm³ as the air mesh; target 80.0000 cm³ (kernel V0 80.0000 cm³, volume factor 1). Kernel bookkeeping: 1.936 cm³ of air in the holes, 0.048 cm³ of tube wall.
- Plastic volume of the body 58.06 cm³. Air with the window throat (FEM export) 80.2618 cm³.
- Exported air files: capped 80.0105 cm³ (manifold True, shells 1); with throat 80.2618 cm³ (manifold True).
- Cavity-mode desk check: first mode 1902 Hz, second 3188 Hz, top note 1396.9 Hz, speed of sound 347.3 m/s; voxel volume 80.10 cm³ on the 1.5 mm grid; numpy 2.5.4, scipy 1.18.1, python 3.12.10.

## Booleans

| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |
| --- | --- | --- | --- | --- |
| cavity + voicing pocket (air) | MANIFOLD | +180.69 | between +0 and +1831 | yes |
| skin + voicing block | MANIFOLD | +8663.87 | between +0 and +19994 | yes |
| envelope - cavity air | MANIFOLD | -78112.72 | -78112.72 | yes |
| tube sub2 | MANIFOLD | +68.83 | +70.06 | yes |
| hole sub1 | MANIFOLD | -35.12 | -35.10 | yes |
| hole sub2 | MANIFOLD | -51.27 | -51.39 | yes |
| hole R_pinky | MANIFOLD | -54.68 | -54.39 | yes |
| hole R_ring | MANIFOLD | -73.61 | -73.43 | yes |
| hole R_middle | MANIFOLD | -37.46 | -37.43 | yes |
| hole R_index | MANIFOLD | -116.92 | -116.67 | yes |
| hole L_ring | MANIFOLD | -160.52 | -160.21 | yes |
| hole L_middle | MANIFOLD | -221.99 | -221.40 | yes |
| hole L_index | MANIFOLD | -106.04 | -105.85 | yes |
| hole L_thumb | MANIFOLD | -365.41 | -363.56 | yes |
| hole R_thumb | MANIFOLD | -512.22 | -507.88 | yes |
| hole L_pinky | MANIFOLD | -231.36 | -230.35 | yes |
| window throat + labium ramp | MANIFOLD | -433.41 | -433.55 | yes |
| windway | MANIFOLD | -605.28 | -605.36 | yes |

## Voicing, measured on the mesh

| Quantity | Measured | Voicing record |
| --- | --- | --- |
| Window length (windway exit to labium) | 9.650 mm | 9.650 mm |
| Window width (broad end) | 8.806 mm | 8.806 mm |
| Window area | 62.83 mm² | 62.84 mm² |
| Widest point, from the windway exit | 4.403 mm | 4.403 mm |
| Windway exit height × width | 1.200 × 8.806 mm | 1.200 × 8.806 mm |
| Windway inlet height × width | 3.000 × 8.806 mm | 3.000 × 8.806 mm |
| Labium ramp angle | 20.00° | 20.00° |
| Labium edge thickness | 0.400 mm | 0.400 mm |
| Labium edge against the windway centre line | -0.200 mm | -0.200 mm |
| Windway roof thickness / floor lip at the exit | 2.99 / 4.26 mm | – |
| Free depth below the window (keep-out 10 mm) | 29.4 mm | – |
| Neck: mouth end width × depth; width × depth where it meets the body | 13.8 × 15.0 mm; 42.3 × 21.1 mm (at least 1.2 mm of plastic around the pipe) | – |
| Pocket blend: reach beyond the flat part until it meets the chamber wall | 2.9 to 5.6 mm (125 of 125 directions end on it) | radius 12 mm |
| Plastic above the outer face, seen from the window rim (keep-out flare 45°) | at most 23.6° steep, 11.8 mm high | at most 45° |

## Holes, measured on the mesh

Diameter: from the area of the bore in a slice at mid wall. Chimney: a ray along the hole axis through the wall before the hole is cut (doc 02, Phase 4 step 5). Bore wall: mean length of the cut bore wall in the final mesh (it is a little longer than the axis chimney on a curved wall). Axis: angle between the bore axis and the normal of the cavity mesh.

| Hole | Deck | d kernel | d measured | Error | Chimney kernel | Chimney measured | Error | Bore wall | Tube | Axis ° | Moved | Nearest gap | To window | To ramp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | top | 3.343 | 3.343 | -0.0000 | 4.00 | 4.000 | -0.0001 | 4.00 | – | 1.18 | 0.00 | 4.76 (L_ring) | 30.5 | 30.5 |
| sub2 | top | 3.057 | 3.057 | -0.0000 | 7.00 | 6.996 | -0.0044 | 6.97 | 3.00 mm, wall 1.20 | 0.39 | 0.00 | 4.25 (R_middle) | 48.2 | 42.4 |
| R_pinky | top | 4.161 | 4.161 | -0.0000 | 4.00 | 3.999 | -0.0007 | 4.04 | – | 0.24 | 0.00 | 12.64 (R_ring) | 72.4 | 64.4 |
| R_ring | top | 4.835 | 4.835 | -0.0000 | 4.00 | 3.999 | -0.0007 | 4.02 | – | 0.03 | 0.00 | 12.64 (R_pinky) | 58.7 | 51.5 |
| R_middle | top | 3.452 | 3.452 | -0.0000 | 4.00 | 3.999 | -0.0006 | 4.01 | – | 0.24 | 0.00 | 4.25 (sub2) | 46.1 | 40.9 |
| R_index | top | 6.094 | 6.094 | +0.0000 | 4.00 | 4.000 | -0.0002 | 4.02 | – | 1.04 | 0.00 | 12.05 (R_middle) | 33.4 | 31.5 |
| L_ring | top | 7.141 | 7.141 | -0.0000 | 4.00 | 4.000 | -0.0002 | 4.02 | – | 0.91 | 0.00 | 4.76 (sub1) | 35.2 | 34.4 |
| L_middle | top | 8.395 | 8.395 | -0.0000 | 4.00 | 4.000 | -0.0005 | 4.02 | – | 0.67 | 0.00 | 9.14 (L_index) | 35.1 | 35.2 |
| L_index | top | 5.805 | 5.805 | +0.0000 | 4.00 | 4.000 | -0.0002 | 4.01 | – | 1.05 | 0.00 | 9.14 (L_middle) | 40.6 | 37.5 |
| L_thumb | bottom | 10.758 | 10.758 | -0.0000 | 4.00 | 3.999 | -0.0007 | 4.04 | – | 0.11 | 0.00 | 19.78 (L_pinky) | 15.9 | 6.2 |
| R_thumb | bottom | 12.715 | 12.715 | +0.0000 | 4.00 | 3.999 | -0.0007 | 4.07 | – | 0.10 | 0.00 | 17.37 (sub2) | 24.6 | 14.9 |
| L_pinky | top | 8.563 | 8.563 | -0.0000 | 4.00 | 3.999 | -0.0009 | 4.04 | – | 0.20 | 0.00 | 9.30 (L_ring) | 40.2 | 36.5 |

All lengths in millimetres.

## Wall and topology

- Plain wall (cavity to outside along the normal, 2322 rays): minimum 4.000 mm, median 4.000 mm.
- Thinnest plastic of the finished body away from the voicing and the tubes (6000 rays): 1.47 mm at (5.7, -39.2, 12.8).
- Topology of the STL: 82196 triangles, manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13.

