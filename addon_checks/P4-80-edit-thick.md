# Geometry check: P4-80-edit-thick

Written by `tools/shell_edit_trial.py` (trial `thick`): the shell-edit build, a PROTOTYPE. Edits made to the base P4-80 before it was finished: 2.5 mm more plastic over the finger deck. The numbers were measured on the mesh in memory.

Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 3 warnings (soft checks, never failures): shell_hole_walls, ergo_finger_pitch, ergo_hole_lean_side. Build and check time 48 s.

- Preset P4, V0 80.00 cm³, voice rating medium, holes cut at the `print` diameters.
- Voicing hash `b4620fbf3d67`: teardrop window 9.65 × 8.81 mm, 62.84 mm², windway exit 1.20 × 8.81 mm, W/h 8.04.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 40°; windway +5° against the body; neck standing 15° off the body, the pipe lowered 10° inside it; pocket blend 12 mm.
- Cavity spine length 131.25 mm (length behind the kernel's c/(2L) estimate: 131.25 mm, caller).
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).

## Checks

`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. `info` is a reported number that decides nothing.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.67; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.95 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | R_thumb 12.61 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_middle 10.43 mm above the 10 mm pad limit; R_thumb 14.25 mm above the 12 mm pad limit; L_pinky 10.41 mm above the 10 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P4-80-edit-thick_air_capped.stl; holes and window closed): 1897 Hz = 1.36 × F6 on a 1.5 mm grid of 23681 cells (2 mm grid: 1887 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 76.545 + voicing pocket 0.236) = 76.7807 cm³ against the kernel's 76.7805 cm³: +0.0002 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 80.0108 cm³ (+0.0135 %), air mesh 80.0178 cm³ (+0.0222 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 10.79 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash b4620fbf3d67; recomputed from the record: b4620fbf3d67 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window inf mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 41° steep seen from the rim, 10.1 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 4.48 mm (at least 0.8 mm); windway roof 2.99 mm |
| `windway_mouth_end` | pass | the pipe is open at the mouth end of the neck |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (sub1), largest chimney error +0.0066 mm (L_pinky); limit 0.05 mm |
| `shell_hole_walls` | WARN | edited shell: wall at the holes from 4.02 mm (L_thumb) to 6.72 mm (R_pinky); the rule's wall is 4 mm. Each hole is sized for its own wall; more than 1 mm from the rule's wall, which no test print has measured: sub1 6.62 mm, sub2 6.69 mm, R_pinky 6.72 mm, R_ring 6.69 mm, R_middle 6.66 mm, R_index 6.63 mm, L_ring 6.66 mm, L_middle 6.67 mm, L_index 6.69 mm, L_pinky 6.68 mm. A deeper hole must be wider: the edit pushed above the finger-pad limit, in the `nominal` set: L_middle 10.43 mm (limit 10), L_pinky 10.41 mm (limit 10) |
| `shell_hole_rims` | pass | edited shell: relief around the rim of a hole, against the plain skin: at most 0.07 mm (R_pinky); every rim is within 0.5 mm |
| `inward_tubes` | pass | sub2: length 0.500 mm (kernel 0.5), wall 1.198 mm, 24.2 mm to the opposite wall, 43.7 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.04° (L_index); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 3.84 mm (sub1 to L_ring); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 10.00 mm from L_ring; sub2 slides 7.50 mm from R_middle; R_index: the sideways offset was limited from -12.1 to -8.9 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there); the hole positions are those of the base; the diameters are sized for the wall measured at each hole of the edited shell; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 19.0 mm (at least 10 mm); no hole touches the voicing block or the labium ramp |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.377 mm (edited shell: at least 2 mm, a provisional limit; the base has 4.0 mm; 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 2.53 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 2.9 to 6.2 mm beyond the flat part. Back corners beside the windway exit: 9.6 mm, meets the wall; 9.5 mm, meets the wall |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.7 / 18.2 / 17.1, right 17.4 / 18.3 / 17.4 mm |
| `ergo_hand_span` | pass | left 50.1 mm, right 50.3 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 51.9, right 51.4 mm |
| `ergo_arch` | pass | left ring +3.0, left middle +3.1, right ring +3.3, right middle +3.4 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +1.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 18.4 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.0°, right line +12.4° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 18.4 mm across (toward the player), +1.0 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 10.0 mm, +0° off the normal of the left-hand line (+9.7 mm forward, +0.0 mm toward the index); at the outer skin 11.6 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.9 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | pass | land past the pinky holes, from the hole edge along the hand axis: bulb 15.3 mm (centre 20.1), tail 14.1 mm (centre 16.6); ok at least 10 mm |
| `ergo_hole_lean_end` | pass | lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +14°, L_ring +5°, L_middle -3°, L_index -12°, R_pinky +19°, R_ring +14°, R_middle +9°, R_index +3°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 11° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -5°, L_ring -3°, L_middle +4°, L_index +20°, R_pinky -11°, R_ring -4°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.4 mm from R middle (ok -8 to +3), L thumb +9.8 mm from L pinky (ok +4 to +10) |

## Warnings

Soft checks (the hand layout, and the edited shell) outside their range. They are measurements to judge, not failures.

- `shell_hole_walls`: edited shell: wall at the holes from 4.02 mm (L_thumb) to 6.72 mm (R_pinky); the rule's wall is 4 mm. Each hole is sized for its own wall; more than 1 mm from the rule's wall, which no test print has measured: sub1 6.62 mm, sub2 6.69 mm, R_pinky 6.72 mm, R_ring 6.69 mm, R_middle 6.66 mm, R_index 6.63 mm, L_ring 6.66 mm, L_middle 6.67 mm, L_index 6.69 mm, L_pinky 6.68 mm. A deeper hole must be wider: the edit pushed above the finger-pad limit, in the `nominal` set: L_middle 10.43 mm (limit 10), L_pinky 10.41 mm (limit 10)
- `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.2 mm. Measured: left 17.1 / 17.7 / 16.2 mm, right 17.1 / 18.0 / 16.8 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 17.7 / 18.2 / 17.1, right 17.4 / 18.3 / 17.4 mm
- `ergo_hole_lean_side`: R_pinky leans 11° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -5°, L_ring -3°, L_middle +4°, L_index +20°, R_pinky -11°, R_ring -4°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away

## Hand layout

Measured in the frame of the hands (`ocarina_addon/ergonomics.py`, the metrics of docs/06). The `ergo_*` checks use the hole centres **on the cavity surface**, as docs/06 did for the add-on bodies. The column *at the outer skin* gives the same number 4 mm further out along each hole axis, where the fingers are; the hole axes spread outward, so it is larger. It decides nothing.

| Quantity | On the cavity surface (checked) | At the outer skin |
| --- | --- | --- |
| Left hand, pinky → ring → middle → index, straight 3D distance | 17.1 / 17.7 / 16.2 mm | 17.7 / 18.2 / 17.1 mm |
| Right hand, pinky → ring → middle → index, straight 3D distance | 17.1 / 18.0 / 16.8 mm | 17.4 / 18.3 / 17.4 mm |
| Hand span pinky to index, left / right (plan view) | 50.1 / 50.3 mm | 51.9 / 51.4 mm |
| Pinky to pinky (plan view) | 103.1 mm | 105.0 mm |
| Arch, ring and middle: left / right | 3.0, 3.1 / 3.3, 3.4 mm | 3.4, 3.7 / 3.6, 3.7 mm |
| Angle between the hand lines | 1.6° | 0.8° |
| Right-hand line nearer the player by | 18.4 mm | 21.4 mm |
| R index from L index: across / along the hand axis | 18.4 / 1.0 mm | 21.4 / -0.4 mm |
| sub1: nearest finger hole, distance, off the normal of that hand line | L_ring, 10.00 mm, 0° | L_ring, 11.57 mm, -4° |
| sub2: nearest finger hole, distance, off the normal of that hand line | R_middle, 7.50 mm, 0° | R_middle, 8.90 mm, -5° |
| L thumb from L pinky / R thumb from R middle, along the hand axis | 9.8 / -7.4 mm | 10.1 / -7.2 mm |
| Body end from the pinky hole centre, bulb / tail (plan view, along the hand axis) | 20.1 / 16.6 mm | – |
| The same from the hole edge (the rest space) | 15.3 / 14.1 mm | – |

Lean of each finger hole (angle of the hole axis against the normal of the finger face). *Toward the end*: along the hand axis toward the nearer end of the body. *Toward the hand*: across the hand axis toward the hand that covers the hole (left hand: the far side; right hand: the player).

| Hole | Total lean | Toward the end | Toward the hand | Mostly toward |
| --- | --- | --- | --- | --- |
| L_pinky | 14° | +14° | -5° | bulb |
| L_ring | 6° | +5° | -3° | bulb |
| L_middle | 5° | -3° | +4° | far |
| L_index | 23° | -12° | +20° | far |
| R_pinky | 21° | +19° | -11° | tail |
| R_ring | 14° | +14° | -4° | tail |
| R_middle | 12° | +9° | +7° | tail |
| R_index | 23° | +3° | +23° | player |

Layout record: kind `template`; sub1 slides 10.00 mm from L_ring (preset 10 mm); sub2 slides 7.50 mm from R_middle (preset 7.5 mm); smallest planned gaps sub1–L_ring 3.84, sub2–R_middle 3.87, L_middle–L_index 8.03, L_ring–L_pinky 8.19, L_ring–L_middle 8.74 mm.
- R_index: the sideways offset was limited from -12.1 to -8.9 mm (35 % of the half section there)
- L_index: the sideways offset was limited from +11.4 to +9.3 mm (35 % of the half section there)
- the hole positions are those of the base; the diameters are sized for the wall measured at each hole of the edited shell

## Volumes

- Cavity mesh: loft 76.5449 cm³ + voicing pocket 0.2358 cm³ = 76.7807 cm³; kernel target 76.7805 cm³.
- Capped air: 80.0108 cm³ measured on the STL by column integration (0.25 mm grid), 80.0178 cm³ as the air mesh; target 80.0000 cm³ (kernel V0 80.0000 cm³, volume factor 1). Kernel bookkeeping: 3.228 cm³ of air in the holes, 0.008 cm³ of tube wall.
- Plastic volume of the body 76.23 cm³. Air with the window throat (FEM export) 80.2691 cm³.
- Cavity-mode desk check: first mode 1897 Hz, second 3165 Hz, top note 1396.9 Hz, speed of sound 347.3 m/s; voxel volume 79.92 cm³ on the 1.5 mm grid; numpy 2.5.4, scipy 1.18.1, python 3.12.10.

## Booleans

| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |
| --- | --- | --- | --- | --- |
| shell + neck | MANIFOLD | +8816.55 | between -0 and +20000 | yes |
| cavity + voicing pocket (air) | MANIFOLD | +235.83 | between +0 and +1918 | yes |
| envelope - cavity air | MANIFOLD | -76780.70 | -76780.70 | yes |
| tube sub2 | MANIFOLD | +10.54 | +11.81 | yes |
| hole sub1 | MANIFOLD | -85.55 | -85.41 | yes |
| hole sub2 | MANIFOLD | -53.73 | -53.76 | yes |
| hole R_pinky | MANIFOLD | -134.02 | -132.74 | yes |
| hole R_ring | MANIFOLD | -175.37 | -174.62 | yes |
| hole R_middle | MANIFOLD | -91.33 | -91.12 | yes |
| hole R_index | MANIFOLD | -266.00 | -265.14 | yes |
| hole L_ring | MANIFOLD | -358.20 | -357.04 | yes |
| hole L_middle | MANIFOLD | -482.62 | -480.77 | yes |
| hole L_index | MANIFOLD | -241.54 | -240.68 | yes |
| hole L_thumb | MANIFOLD | -361.37 | -359.41 | yes |
| hole R_thumb | MANIFOLD | -509.38 | -504.73 | yes |
| hole L_pinky | MANIFOLD | -488.49 | -485.87 | yes |
| window throat + labium ramp | MANIFOLD | -679.28 | -679.06 | yes |
| windway | MANIFOLD | -580.64 | -580.77 | yes |

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
| Windway roof thickness / floor lip at the exit | 2.99 / 4.48 mm | – |
| Free depth below the window (keep-out 10 mm) | inf mm | – |
| Neck: mouth end width × depth; width × depth where it meets the body | 13.8 × 15.0 mm; 42.3 × 21.1 mm (at least 1.2 mm of plastic around the pipe) | – |
| Pocket blend: reach beyond the flat part until it meets the chamber wall | 2.9 to 6.2 mm (125 of 125 directions end on it) | radius 12 mm |
| Plastic above the outer face, seen from the window rim (keep-out flare 45°) | at most 41.5° steep, 10.1 mm high | at most 45° |

## Holes, measured on the mesh

Diameter: from the area of the bore in a slice at mid wall. Chimney: a ray along the hole axis through the wall before the hole is cut (doc 02, Phase 4 step 5). Bore wall: mean length of the cut bore wall in the final mesh (it is a little longer than the axis chimney on a curved wall). Axis: angle between the bore axis and the normal of the cavity mesh.

| Hole | Deck | d kernel | d measured | Error | Chimney kernel | Chimney measured | Error | Bore wall | Tube | Axis ° | Moved | Nearest gap | To window | To ramp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | top | 4.056 | 4.056 | +0.0000 | 6.61 | 6.616 | +0.0023 | 6.63 | – | 0.97 | 0.00 | 3.84 (L_ring) | 27.0 | 27.0 |
| sub2 | top | 3.088 | 3.088 | -0.0000 | 7.18 | 7.184 | +0.0000 | 7.16 | 0.50 mm, wall 1.20 | 0.30 | 0.00 | 3.87 (R_middle) | 48.1 | 42.6 |
| R_pinky | top | 5.019 | 5.019 | +0.0000 | 6.71 | 6.710 | +0.0007 | 6.81 | – | 0.63 | 0.00 | 11.74 (R_ring) | 72.1 | 64.2 |
| R_ring | top | 5.770 | 5.770 | +0.0000 | 6.68 | 6.684 | +0.0031 | 6.73 | – | 0.13 | 0.00 | 11.74 (R_pinky) | 58.0 | 51.0 |
| R_middle | top | 4.177 | 4.177 | -0.0000 | 6.65 | 6.658 | +0.0037 | 6.67 | – | 0.20 | 0.00 | 3.87 (sub2) | 44.8 | 39.7 |
| R_index | top | 7.139 | 7.139 | -0.0000 | 6.62 | 6.627 | +0.0017 | 6.67 | – | 1.03 | 0.00 | 11.14 (R_middle) | 30.6 | 28.7 |
| L_ring | top | 8.271 | 8.271 | -0.0000 | 6.65 | 6.652 | +0.0021 | 6.68 | – | 0.94 | 0.00 | 3.84 (sub1) | 33.0 | 32.5 |
| L_middle | top | 9.590 | 9.590 | -0.0000 | 6.66 | 6.660 | +0.0036 | 6.71 | – | 0.64 | 0.00 | 8.03 (L_index) | 33.6 | 33.6 |
| L_index | top | 6.773 | 6.773 | +0.0000 | 6.68 | 6.689 | +0.0015 | 6.72 | – | 1.04 | 0.00 | 8.03 (L_middle) | 40.3 | 37.6 |
| L_thumb | bottom | 10.666 | 10.666 | +0.0000 | 4.02 | 4.023 | +0.0048 | 4.07 | – | 0.13 | 0.00 | 19.08 (L_pinky) | 19.0 | 9.5 |
| R_thumb | bottom | 12.612 | 12.612 | -0.0000 | 4.04 | 4.041 | +0.0049 | 4.12 | – | 0.12 | 0.00 | 17.20 (sub2) | 27.4 | 17.9 |
| L_pinky | top | 9.635 | 9.635 | -0.0000 | 6.66 | 6.662 | +0.0066 | 6.74 | – | 0.26 | 0.00 | 8.19 (L_ring) | 38.4 | 34.8 |

All lengths in millimetres.

## Edited shell (shell-edit build, prototype)

The outer shell (32512 triangles, 148.69 cm³ solid) and the neck (4608 triangles) were edited after the add-on made them, and this body was cut out of them. The chamber, the voicing and the hole positions are the add-on's. The wall at each hole was measured on the edited shell and each hole was sized for it, in 3 sizing rounds; the chamber was solved again so that the capped air is still V0 (chamber 76.781 cm³; 78.113 cm³ on the base).

*Wall*: the rule's wall (4 mm) plus the mean of what the edit added over the hole. *On the axis*: the edited shell along the hole axis. *Rim relief*: how much the added plastic varies around the rim.

| Hole | Wall | Added by the edit | On the axis | Rim relief | d on the base | d cut | Change |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | 6.619 | +2.619 | 6.614 | 0.01 | 3.343 | 4.056 | +0.713 |
| sub2 | 6.689 | +2.689 | 6.684 | 0.01 | 3.057 | 3.088 | +0.031 |
| R_pinky | 6.724 | +2.724 | 6.709 | 0.07 | 4.161 | 5.019 | +0.859 |
| R_ring | 6.692 | +2.692 | 6.681 | 0.04 | 4.835 | 5.770 | +0.935 |
| R_middle | 6.661 | +2.661 | 6.654 | 0.01 | 3.452 | 4.177 | +0.725 |
| R_index | 6.634 | +2.634 | 6.625 | 0.04 | 6.094 | 7.139 | +1.045 |
| L_ring | 6.657 | +2.657 | 6.650 | 0.03 | 7.141 | 8.271 | +1.130 |
| L_middle | 6.668 | +2.668 | 6.657 | 0.05 | 8.395 | 9.590 | +1.195 |
| L_index | 6.693 | +2.693 | 6.687 | 0.04 | 5.805 | 6.773 | +0.969 |
| L_thumb | 4.024 | +0.024 | 4.018 | 0.03 | 10.758 | 10.666 | -0.092 |
| R_thumb | 4.043 | +0.043 | 4.037 | 0.05 | 12.715 | 12.612 | -0.103 |
| L_pinky | 6.676 | +2.676 | 6.656 | 0.05 | 8.563 | 9.635 | +1.072 |

All lengths in millimetres.

## Wall and topology

- Plain wall (cavity to outside along the normal, 2323 rays): minimum 4.000 mm, median 4.377 mm.
- Thinnest plastic of the finished body away from the voicing and the tubes (6000 rays): 2.53 mm at (3.1, -32.5, 24.5).
- Topology of the STL: 82774 triangles, manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13.

