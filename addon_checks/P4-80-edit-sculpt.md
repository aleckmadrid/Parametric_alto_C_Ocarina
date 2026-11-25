# Geometry check: P4-80-edit-sculpt

Written by `tools/shell_edit_trial.py` (trial `sculpt`): the shell-edit build, a PROTOTYPE. Edits made to the base P4-80 before it was finished: tail 25 mm longer (the last 10 mm of the body stretched); boss +1.5 mm high, 8 mm radius, over R_ring; groove 0.9 mm deep, 4 mm wide, across the rim of L_middle; relief up to 0.6 mm, 7 mm pattern, none within 16 mm of the window; neck 20 % thicker toward the mouth end (roof line and mouth end plane kept). The numbers were measured on the mesh in memory.

Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 4 warnings (soft checks, never failures): shell_hole_walls, shell_hole_rims, ergo_finger_pitch, ergo_hole_lean_side. Build and check time 54 s.

- Preset P4, V0 80.00 cm³, voice rating medium, holes cut at the `print` diameters.
- Voicing hash `312011ec9f0e`: teardrop window 9.65 × 8.81 mm, 62.84 mm², windway exit 1.20 × 8.81 mm, W/h 8.04.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm.
- Cavity spine length 131.90 mm (length behind the kernel's c/(2L) estimate: 131.90 mm, caller).
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).

## Checks

`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. `info` is a reported number that decides nothing.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.80; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.94 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | R_thumb 12.87 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_thumb 12.21 mm above the 12 mm pad limit; R_thumb 14.51 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P4-80-edit-sculpt_air_capped.stl; holes and window closed): 1898 Hz = 1.36 × F6 on a 1.5 mm grid of 23699 cells (2 mm grid: 1891 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.681 + voicing pocket 0.181) = 77.8618 cm³ against the kernel's 77.8618 cm³: +0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 79.8818 cm³ (-0.1478 %), air mesh 80.0118 cm³ (+0.0147 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 2.08 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 312011ec9f0e; recomputed from the record: 312011ec9f0e |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 29.4 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 11° steep seen from the rim, 5.6 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 4.26 mm (at least 0.8 mm); windway roof 2.99 mm |
| `windway_mouth_end` | pass | the pipe is open at the mouth end of the neck |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error -0.0000 mm (R_pinky), largest chimney error +0.0068 mm (L_pinky); limit 0.05 mm |
| `shell_hole_walls` | WARN | edited shell: wall at the holes from 3.99 mm (L_middle) to 5.75 mm (R_ring); the rule's wall is 4 mm. Each hole is sized for its own wall; more than 1 mm from the rule's wall, which no test print has measured: R_ring 5.75 mm |
| `shell_hole_rims` | WARN | edited shell: relief around the rim of a hole, against the plain skin: at most 0.97 mm (L_middle); above 0.5 mm, where a finger pad may not seal the hole: L_middle 0.97 mm |
| `inward_tubes` | pass | sub2: length 2.500 mm (kernel 2.5), wall 1.198 mm, 22.4 mm to the opposite wall, 42.1 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.14° (sub1); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.22 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 10.00 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -8.9 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there); the hole positions are those of the base; the diameters are sized for the wall measured at each hole of the edited shell; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 15.8 mm (at least 10 mm); no hole touches the voicing block or the labium ramp; the most plastic of the neck beside a rim: 0.00 mm (L_pinky; counted from 0.3 mm) |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 3.220 mm, median 4.360 mm (edited shell: at least 1.32 mm, three printed walls; the base has 4.0 mm; 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 1.31 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 2.9 to 5.6 mm beyond the flat part. Back corners beside the windway exit: 8.7 mm, meets the wall; 8.5 mm, meets the wall |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.7 / 18.2 / 17.1, right 17.4 / 18.3 / 17.5 mm |
| `ergo_hand_span` | pass | left 50.1 mm, right 50.3 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.9, right 51.4 mm |
| `ergo_arch` | pass | left ring +3.0, left middle +3.2, right ring +3.3, right middle +3.4 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +1.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 18.5 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.1°, right line +12.5° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 18.5 mm across (toward the player), +0.9 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 10.0 mm, +0° off the normal of the left-hand line (+9.7 mm forward, +0.0 mm toward the index); at the outer skin 11.6 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.9 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | pass | land past the pinky holes, from the hole edge along the hand axis: bulb 14.8 mm (centre 19.2), tail 17.3 mm (centre 19.4); ok at least 10 mm |
| `ergo_hole_lean_end` | pass | lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +13°, L_ring +5°, L_middle -3°, L_index -12°, R_pinky +19°, R_ring +14°, R_middle +9°, R_index +3°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 10° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -5°, L_ring -3°, L_middle +4°, L_index +20°, R_pinky -10°, R_ring -4°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.4 mm from R middle (ok -8 to +3), L thumb +9.8 mm from L pinky (ok +4 to +10) |

## Warnings

Soft checks (the hand layout, and the edited shell) outside their range. They are measurements to judge, not failures.

- `shell_hole_walls`: edited shell: wall at the holes from 3.99 mm (L_middle) to 5.75 mm (R_ring); the rule's wall is 4 mm. Each hole is sized for its own wall; more than 1 mm from the rule's wall, which no test print has measured: R_ring 5.75 mm
- `shell_hole_rims`: edited shell: relief around the rim of a hole, against the plain skin: at most 0.97 mm (L_middle); above 0.5 mm, where a finger pad may not seal the hole: L_middle 0.97 mm
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
| Arch, ring and middle: left / right | 3.0, 3.2 / 3.3, 3.4 mm | 3.4, 3.7 / 3.6, 3.8 mm |
| Angle between the hand lines | 1.6° | 0.8° |
| Right-hand line nearer the player by | 18.5 mm | 21.5 mm |
| R index from L index: across / along the hand axis | 18.5 / 0.9 mm | 21.5 / -0.5 mm |
| sub1: nearest finger hole, distance, off the normal of that hand line | L_ring, 10.00 mm, 0° | L_ring, 11.56 mm, -4° |
| sub2: nearest finger hole, distance, off the normal of that hand line | R_middle, 7.50 mm, 0° | R_middle, 8.89 mm, -4° |
| L thumb from L pinky / R thumb from R middle, along the hand axis | 9.8 / -7.4 mm | 10.1 / -7.2 mm |
| Body end from the pinky hole centre, bulb / tail (plan view, along the hand axis) | 19.2 / 19.4 mm | – |
| The same from the hole edge (the rest space) | 14.8 / 17.3 mm | – |

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

Layout record: kind `template`; sub1 slides 10.00 mm from L_ring (preset 10 mm); sub2 slides 7.50 mm from R_middle (preset 7.5 mm); smallest planned gaps sub2–R_middle 4.22, sub1–L_ring 4.62, L_middle–L_index 9.08, L_ring–L_pinky 9.14, L_ring–L_middle 9.83 mm.
- R_index: the sideways offset was limited from -12.1 to -8.9 mm (35 % of the half section there)
- L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there)
- the hole positions are those of the base; the diameters are sized for the wall measured at each hole of the edited shell

## Volumes

- Cavity mesh: loft 77.6808 cm³ + voicing pocket 0.1810 cm³ = 77.8618 cm³; kernel target 77.8618 cm³.
- Capped air: 79.8818 cm³ measured on the STL by column integration (0.25 mm grid), 80.0118 cm³ as the air mesh; target 80.0000 cm³ (kernel V0 80.0000 cm³, volume factor 1). Kernel bookkeeping: 2.178 cm³ of air in the holes, 0.040 cm³ of tube wall.
- Plastic volume of the body 63.69 cm³. Air with the window throat (FEM export) 80.2631 cm³.
- Cavity-mode desk check: first mode 1898 Hz, second 3186 Hz, top note 1396.9 Hz, speed of sound 347.3 m/s; voxel volume 79.98 cm³ on the 1.5 mm grid; numpy 2.5.4, scipy 1.18.1, python 3.12.10.

## Booleans

| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |
| --- | --- | --- | --- | --- |
| shell + neck | MANIFOLD | +7472.78 | between -0 and +22482 | yes |
| cavity + voicing pocket (air) | MANIFOLD | +180.98 | between +0 and +1831 | yes |
| envelope - cavity air | MANIFOLD | -77861.77 | -77861.77 | yes |
| tube sub2 | MANIFOLD | +56.10 | +57.30 | yes |
| hole sub1 | MANIFOLD | -41.83 | -41.78 | yes |
| hole sub2 | MANIFOLD | -47.63 | -47.73 | yes |
| hole R_pinky | MANIFOLD | -61.35 | -60.99 | yes |
| hole R_ring | MANIFOLD | -135.69 | -135.34 | yes |
| hole R_middle | MANIFOLD | -43.03 | -42.99 | yes |
| hole R_index | MANIFOLD | -132.85 | -132.56 | yes |
| hole L_ring | MANIFOLD | -181.69 | -181.37 | yes |
| hole L_middle | MANIFOLD | -220.26 | -219.60 | yes |
| hole L_index | MANIFOLD | -119.96 | -119.65 | yes |
| hole L_thumb | MANIFOLD | -396.27 | -394.39 | yes |
| hole R_thumb | MANIFOLD | -565.40 | -560.07 | yes |
| hole L_pinky | MANIFOLD | -260.17 | -259.15 | yes |
| window throat + labium ramp | MANIFOLD | -429.64 | -429.67 | yes |
| windway | MANIFOLD | -563.81 | -564.41 | yes |

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
| Neck: mouth end width × depth; width × depth where it meets the body | 13.8 × 7.6 mm; 42.3 × 24.5 mm (at least 1.2 mm of plastic around the pipe) | – |
| Pocket blend: reach beyond the flat part until it meets the chamber wall | 2.9 to 5.6 mm (125 of 125 directions end on it) | radius 12 mm |
| Plastic above the outer face, seen from the window rim (keep-out flare 45°) | at most 10.9° steep, 5.6 mm high | at most 45° |

## Holes, measured on the mesh

Diameter: from the area of the bore in a slice at mid wall. Chimney: a ray along the hole axis through the wall before the hole is cut (doc 02, Phase 4 step 5). Bore wall: mean length of the cut bore wall in the final mesh (it is a little longer than the axis chimney on a curved wall). Axis: angle between the bore axis and the normal of the cavity mesh.

| Hole | Deck | d kernel | d measured | Error | Chimney kernel | Chimney measured | Error | Bore wall | Tube | Axis ° | Moved | Nearest gap | To window | To ramp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | top | 3.470 | 3.470 | -0.0000 | 4.42 | 4.594 | +0.0010 | 4.34 | – | 1.14 | 0.00 | 4.62 (L_ring) | 30.4 | 30.4 |
| sub2 | top | 3.006 | 3.006 | -0.0000 | 6.72 | 6.680 | +0.0000 | 6.75 | 2.50 mm, wall 1.20 | 0.44 | 0.00 | 4.22 (R_middle) | 48.2 | 42.4 |
| R_pinky | top | 4.260 | 4.260 | -0.0000 | 4.28 | 4.189 | +0.0012 | 4.40 | – | 0.31 | 0.00 | 12.27 (R_ring) | 72.3 | 64.4 |
| R_ring | top | 5.475 | 5.475 | +0.0000 | 5.75 | 5.835 | +0.0033 | 5.70 | – | 0.02 | 0.00 | 12.27 (R_pinky) | 58.3 | 51.2 |
| R_middle | top | 3.554 | 3.554 | +0.0000 | 4.33 | 4.334 | +0.0039 | 4.34 | – | 0.23 | 0.00 | 4.22 (sub2) | 46.0 | 40.8 |
| R_index | top | 6.241 | 6.241 | +0.0000 | 4.33 | 4.199 | +0.0014 | 4.39 | – | 1.03 | 0.00 | 11.92 (R_middle) | 33.3 | 31.4 |
| L_ring | top | 7.299 | 7.299 | +0.0000 | 4.33 | 4.332 | +0.0023 | 4.34 | – | 0.92 | 0.00 | 4.62 (sub1) | 35.1 | 34.3 |
| L_middle | top | 8.378 | 8.378 | -0.0000 | 3.98 | 3.951 | +0.0035 | 4.09 | – | 0.66 | 0.00 | 9.08 (L_index) | 35.1 | 35.2 |
| L_index | top | 5.937 | 5.937 | +0.0000 | 4.32 | 4.367 | +0.0019 | 4.34 | – | 1.05 | 0.00 | 9.08 (L_middle) | 40.4 | 37.4 |
| L_thumb | bottom | 10.882 | 10.882 | -0.0000 | 4.24 | 4.271 | +0.0051 | 4.28 | – | 0.11 | 0.00 | 19.60 (L_pinky) | 15.8 | 6.1 |
| R_thumb | bottom | 12.871 | 12.871 | -0.0000 | 4.30 | 4.414 | +0.0049 | 4.40 | – | 0.10 | 0.00 | 17.28 (sub2) | 24.5 | 14.8 |
| L_pinky | top | 8.717 | 8.717 | -0.0000 | 4.34 | 4.226 | +0.0068 | 4.36 | – | 0.19 | 0.00 | 9.14 (L_ring) | 40.1 | 36.4 |

All lengths in millimetres.

## Edited shell (shell-edit build, prototype)

The outer shell (32512 triangles, 137.22 cm³ solid) and the neck (4736 triangles) were edited after the add-on made them, and this body was cut out of them. The chamber, the voicing and the hole positions are the add-on's. The wall at each hole was measured on the edited shell and each hole was sized for it, in 3 sizing rounds; the chamber was solved again so that the capped air is still V0 (chamber 77.862 cm³; 78.113 cm³ on the base).

*Wall*: the rule's wall (4 mm) plus the mean of what the edit added over the hole. *On the axis*: the edited shell along the hole axis. *Rim relief*: how much the added plastic varies around the rim.

| Hole | Wall | Added by the edit | On the axis | Rim relief | d on the base | d cut | Change |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | 4.420 | +0.420 | 4.593 | 0.26 | 3.343 | 3.470 | +0.127 |
| sub2 | 4.226 | +0.226 | 4.180 | 0.26 | 3.057 | 3.006 | -0.051 |
| R_pinky | 4.281 | +0.281 | 4.188 | 0.38 | 4.161 | 4.260 | +0.099 |
| R_ring | 5.751 | +1.751 | 5.831 | 0.43 | 4.835 | 5.475 | +0.640 |
| R_middle | 4.336 | +0.336 | 4.330 | 0.44 | 3.452 | 3.554 | +0.102 |
| R_index | 4.335 | +0.335 | 4.198 | 0.43 | 6.094 | 6.241 | +0.147 |
| L_ring | 4.336 | +0.336 | 4.330 | 0.36 | 7.141 | 7.299 | +0.158 |
| L_middle | 3.986 | -0.014 | 3.947 | 0.97 | 8.395 | 8.378 | -0.017 |
| L_index | 4.324 | +0.324 | 4.365 | 0.44 | 5.805 | 5.937 | +0.133 |
| L_thumb | 4.240 | +0.240 | 4.266 | 0.49 | 10.758 | 10.882 | +0.125 |
| R_thumb | 4.305 | +0.305 | 4.409 | 0.32 | 12.715 | 12.871 | +0.157 |
| L_pinky | 4.344 | +0.344 | 4.219 | 0.43 | 8.563 | 8.717 | +0.155 |

All lengths in millimetres.

## Wall and topology

- Plain wall (cavity to outside along the normal, 2323 rays): minimum 3.220 mm, median 4.360 mm.
- Thinnest plastic of the finished body away from the voicing and the tubes (6000 rays): 1.31 mm at (-4.6, -31.9, 6.2).
- Topology of the STL: 82638 triangles, manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13.

