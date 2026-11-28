# Geometry check: P4-bowl-80-off26-s75-lt43m6

Written by `tools/geometry_check_variant.py -- P4-bowl 80 off26-s75-lt43m6 port_u=0.26 layout_centre_from_port_mm=22.97 thumb_offsets_mm={"L_thumb": [-4.3, -6.0], "R_thumb": [0.0, 0.0]} windway_length_mm=50 neck_side_wall_mm=2.5 neck_base_width_mm=38 neck_width_exponent=1.5 neck_cover_mm=3.3 neck_floor_mm=3.3 neck_base_depth_mm=26 neck_depth_exponent=1.5 neck_tilt_deg=0`: preset P4-bowl with port_u=0.26 layout_centre_from_port_mm=22.97 thumb_offsets_mm={"L_thumb": [-4.3, -6.0], "R_thumb": [0.0, 0.0]} windway_length_mm=50 neck_side_wall_mm=2.5 neck_base_width_mm=38 neck_width_exponent=1.5 neck_cover_mm=3.3 neck_floor_mm=3.3 neck_base_depth_mm=26 neck_depth_exponent=1.5 neck_tilt_deg=0. Every measured number comes from the STL file `addon_out/P4-bowl-80-off26-s75-lt43m6/P4-bowl-80-off26-s75-lt43m6.stl`, read back from disk (176414 triangles).

Result: **no unexpected failure**; expected by the notes: hole_limits[print] (fail), hole_limits[nominal] (fail); 6 warnings (soft checks, never failures): shell_hole_walls, ergo_finger_pitch, ergo_hand_span, ergo_rest_space, ergo_hole_lean_end, ergo_hole_lean_side. Build and check time 47 s.

- Preset P4-bowl, V0 80.00 cm³, voice rating soft, holes cut at the `print` diameters.
- Voicing hash `6d05b21b49e8`: teardrop window 8.89 × 9.05 mm, 62.84 mm², windway exit 1.20 × 9.05 mm, W/h 7.41.
- Build (in the hash): ellipse cut, 3 mm per side, opened into a round bowl 29.06 x 24.00 mm (xw -2 to 22), set 2.2 mm deep, shelf 0°; windway +4° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm. **Prototype settings that are not in the voicing hash:** neck_base_width_mm = 38, neck_base_depth_mm = 26, neck_side_wall_mm = 2.5, neck_cover_mm = 3.3, neck_depth_exponent = 1.5, neck_width_exponent = 1.5, neck_floor_mm = 3.3, neck_tilt_deg = 0, pocket_back_margin_mm = 0.05.
- **Round bowl (an option, not the rule; window_cut `bowl`, in the hash):** measured 1.32 mm deep, 4.27 mm of plastic under it, 2.09 mm over the windway's roof, the window's walls kept exactly to 2.52 mm; the hole at the bowl's floor xw 0.00 to 17.74, y -8.18 to +8.06 mm; cutter 2940.6 mm³.
- **The window's throat with the bowl** (kernel, pre-calibration, η_w prior): effective wall t_eff 2.398 mm to the rule's outer face, 2.428 mm to the bowl's rim (z 4.22 mm); the rule's ellipse cut alone 2.440 mm; the kernel takes the wall, 4 mm. The kernel's V0 for this window with each: 93.41, 93.12, 93.01 and 80.00 cm³.
- **Uneven wall (an option of the shell-edit build):** 3.00 mm on the finger deck to 6.00 mm on the thumb face (wall_front_less_mm 1, wall_back_more_mm 2, refined within 30, 24 mm of the window); shell 136.58 cm³ solid (130.62 cm³ with the rule's wall).
- **MOVED THUMB HOLE (an ergonomic change):** L_thumb moved -4.3 mm along the hand axis (+ toward the tail) and -6 mm across it (preset value `thumb_offsets_mm`).
- **MOVED THUMB HOLE (an ergonomic change):** R_thumb moved +0 mm along the hand axis (+ toward the tail) and +0 mm across it (preset value `thumb_offsets_mm`).
- Cavity spine length 131.94 mm (length behind the kernel's c/(2L) estimate: 131.94 mm, caller).
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).

## Checks

`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. `info` is a reported number that decides nothing.

| Check | Result | Message |
| --- | --- | --- |
| `range_ratio` | pass | sum(G_i) / (eta_w G_w) = 8.79; single-chamber ceiling 10.0 |
| `cavity_mode_c2L` | info | kernel estimate from the length of the chamber, reported only: c/(2L) = 0.94 x F6: the first cavity mode lies below the top note (the kernel's own status: fail). c/(2L) is the lowest estimate; the verdict is `cavity_mode_computed` |
| `wh_ratio` | pass | W/h = 7.41 (band 7..10) |
| `hole_limits[print]` | FAIL (expected) | R_thumb 13.76 mm above the 12 mm pad limit |
| `hole_limits[nominal]` | FAIL (expected) | L_thumb 13.03 mm above the 12 mm pad limit; R_thumb 15.25 mm above the 12 mm pad limit |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (P4-bowl-80-off26-s75-lt43m6_air_capped.stl; holes and window closed): 1899 Hz = 1.36 × F6 on a 1.5 mm grid of 23684 cells (2 mm grid: 1893 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 77.764 + voicing pocket 0.053) = 77.8170 cm³ against the kernel's 77.8170 cm³: -0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 79.7504 cm³ (-0.3120 %), air mesh 80.0156 cm³ (+0.0195 %), against V0 80.0000 cm³ (limit 0.5 %) |
| `booleans` | pass | 18 Booleans, all manifold, each volume change as expected (largest deviation 1.24 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13 (expected 13: 12 holes, the window and the windway) |
| `voicing_hash` | pass | hash 6d05b21b49e8; recomputed from the record: 6d05b21b49e8 |
| `voicing_dimensions` | pass | measured on the mesh: window 8.890 × 9.048 mm, 62.83 mm² (record 8.890 × 9.048, 62.84); windway exit 1.200 × 9.048 mm, inlet 3.000 × 9.048 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 9.048 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.42 mm from the exit, window 8.89 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 29.9 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 12° steep seen from the rim, 4.2 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 2.46 mm (at least 0.8 mm); windway roof 2.99 mm |
| `windway_mouth_end` | pass | the pipe is open at the mouth end of the neck |
| `hole_sizes_phase4_gate` | pass | 12 holes measured on the mesh against the kernel: largest diameter error +0.0000 mm (R_thumb), largest chimney error +0.0054 mm (sub1); limit 0.05 mm |
| `shell_hole_walls` | WARN | edited shell: wall at the holes from 3.04 mm (L_ring) to 6.02 mm (R_thumb); the rule's wall is 4 mm. Each hole is sized for its own wall; more than 1 mm from the rule's wall, which no test print has measured: L_thumb 5.93 mm, R_thumb 6.02 mm |
| `shell_hole_rims` | pass | edited shell: relief around the rim of a hole, against the plain skin: at most 0.28 mm (L_thumb); every rim is within 0.5 mm |
| `inward_tubes` | pass | sub2: length 4.000 mm (kernel 4.0), wall 1.198 mm, 23.6 mm to the opposite wall, 43.8 mm to the labium |
| `hole_axes` | pass | largest angle between a hole axis and the cavity mesh normal: 1.08° (L_thumb); limit 2.0° |
| `hole_spacing` | pass | smallest edge gap 4.40 mm (sub2 to R_middle); at least 3.4 mm |
| `hole_layout` | pass | record of moves: largest move from the layout position 0.00 mm (sub1; up to 2 mm allowed); layout 'template'; sub1 slides 10.00 mm from L_ring; sub2 slides 7.50 mm from R_middle; MOVED THUMB HOLE (an ergonomic change): L_thumb moved -4.3 mm along the hand axis (+ toward the tail) and -6 mm across it (preset value thumb_offsets_mm); MOVED THUMB HOLE (an ergonomic change): R_thumb moved +0 mm along the hand axis (+ toward the tail) and +0 mm across it (preset value thumb_offsets_mm); R_index: the sideways offset was limited from -12.1 to -9.5 mm (35 % of the half section there); L_index: the sideways offset was limited from +11.4 to +9.8 mm (35 % of the half section there); L_thumb: the sideways offset was limited from -9.3 to -8.1 mm (35 % of the half section there); the hole positions are those of the base; the diameters are sized for the wall measured at each hole of the edited shell; the finger pitch is never compressed: a deck that is too short shows in the ergo_* checks |
| `hole_to_voicing` | pass | nearest hole edge to the window: L_thumb, 13.2 mm (at least 10 mm); no hole touches the voicing block or the labium ramp; the most plastic of the neck beside a rim: 0.00 mm (R_index; counted from 0.3 mm) |
| `bowl_local_plastic` | pass | no plate thinner than its region allows; narrower than 0.4 mm (ledges, not printed as plates): windway_floor 0.18 mm² down to 0.15 mm, surround 0.48 mm² down to 0.15 mm (least plate / least edge / limit: windway_floor 0.15 / 0.15 / 0.80, windway_roof 1.44 / 1.44 / 1.32, windway_roof_in_window 2.48 / 0.00 / 0.40, labium – / 0.46 / 0.33, surround 0.15 / 0.01 / 0.40 mm along the inward normals, 90612 probes 0.25 mm apart; an edge, its far surface more than 15° from parallel, is reported only); the pocket is joined to the chamber (the capped air is one piece) |
| `hole_seal_surface` | pass | every hole keeps an uncut outside around its rim (least sub2 2.2 mm of 2.2 probed; at least 0.5 mm, a provisional limit: the margin a rim keeps from the voicing) |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 3.037 mm, median 4.045 mm (edited shell: at least 1.32 mm, three printed walls; the base has 4.0 mm; 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 1.75 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 3.1 to 5.1 mm beyond the flat part. Back corners beside the windway exit: none: the pocket's back edge follows the window (pocket_back_margin_mm) |
| `ergo_finger_pitch` | WARN | finger pitch out of range: L_middle to L_index 16.4 mm. Measured: left 17.1 / 17.7 / 16.4 mm, right 17.1 / 18.0 / 17.1 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.7 / 18.2 / 17.3, right 17.4 / 18.3 / 17.9 mm |
| `ergo_hand_span` | WARN | hand span out of range: left hand 49.7 mm. Measured: left 49.7 mm, right 50.7 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.4, right 51.9 mm |
| `ergo_arch` | pass | left ring +3.0, left middle +3.4, right ring +3.5, right middle +3.8 mm off the pinky to index line, + toward the fingertips; ok +0.5 to +7 mm |
| `ergo_hands_parallel` | pass | angle between the two hand lines +1.6° (+ = they open toward the tail); ok within ±10° |
| `ergo_hand_offset` | pass | the right-hand line is 19.5 mm nearer the player than the left-hand line; ok 18 to 28 mm. Tilt against the body axis, reported only: left line +14.7°, right line +13.1° (+ = the tail end of the line is farther from the player) |
| `ergo_index_meet` | pass | R index from L index: 19.5 mm across (toward the player), +0.5 mm along the hand axis (− = toward the bulb: the hands overlap); ok 18 to 28 mm across, -22 to +5 mm along |
| `ergo_subholes` | pass | sub1 from L_ring: 10.0 mm, -0° off the normal of the left-hand line (+9.7 mm forward, -0.0 mm toward the index); at the outer skin 11.6 mm; sub2 from R_middle: 7.5 mm, +0° off the normal of the right-hand line (+7.5 mm forward, +0.0 mm toward the index); at the outer skin 8.7 mm; ok 7 to 11 mm from the nearest finger hole, within 20° of the normal |
| `ergo_rest_space` | WARN | the bulb end is 3.3 mm too short: 6.7 mm past the L pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 6.7 mm (centre 10.7), tail 17.7 mm (centre 19.6); ok at least 10 mm |
| `ergo_hole_lean_end` | WARN | L_pinky leans 31° toward the bulb end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +31°, L_ring +7°, L_middle -0°, L_index -9°, R_pinky +16°, R_ring +12°, R_middle +8°, R_index -0°; ok up to 20° |
| `ergo_hole_lean_side` | WARN | R_pinky leans 7° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -1°, L_ring -3°, L_middle +5°, L_index +21°, R_pinky -7°, R_ring -3°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away |
| `ergo_thumbs` | pass | along the hand axis, + toward the tail: R thumb -7.4 mm from R middle (ok -8 to +3), L thumb +4.1 mm from L pinky (ok +4 to +10) |

## Warnings

Soft checks (the hand layout, and the edited shell) outside their range. They are measurements to judge, not failures.

- `shell_hole_walls`: edited shell: wall at the holes from 3.04 mm (L_ring) to 6.02 mm (R_thumb); the rule's wall is 4 mm. Each hole is sized for its own wall; more than 1 mm from the rule's wall, which no test print has measured: L_thumb 5.93 mm, R_thumb 6.02 mm
- `ergo_finger_pitch`: finger pitch out of range: L_middle to L_index 16.4 mm. Measured: left 17.1 / 17.7 / 16.4 mm, right 17.1 / 18.0 / 17.1 mm (pinky, ring, middle, index; straight 3D distance); ok 16.5 to 20.5 mm; at the outer skin: left 18.7 / 18.2 / 17.3, right 17.4 / 18.3 / 17.9 mm
- `ergo_hand_span`: hand span out of range: left hand 49.7 mm. Measured: left 49.7 mm, right 50.7 mm (pinky to index, plan view); ok 50 to 60 mm; at the outer skin: left 52.4, right 51.9 mm
- `ergo_rest_space`: the bulb end is 3.3 mm too short: 6.7 mm past the L pinky hole edge. Measured: land past the pinky holes, from the hole edge along the hand axis: bulb 6.7 mm (centre 10.7), tail 17.7 mm (centre 19.6); ok at least 10 mm
- `ergo_hole_lean_end`: L_pinky leans 31° toward the bulb end. Measured: lean along the hand axis toward the nearer end (− = toward the middle): L_pinky +31°, L_ring +7°, L_middle -0°, L_index -9°, R_pinky +16°, R_ring +12°, R_middle +8°, R_index -0°; ok up to 20°
- `ergo_hole_lean_side`: R_pinky leans 7° away from the hand that covers it. Measured: lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; − = away from it): L_pinky -1°, L_ring -3°, L_middle +5°, L_index +21°, R_pinky -7°, R_ring -3°, R_middle +7°, R_index +23°; ok up to 45° toward it and up to 5° away

## Hand layout

Measured in the frame of the hands (`ocarina_addon/ergonomics.py`, the metrics of docs/06). The `ergo_*` checks use the hole centres **on the cavity surface**, as docs/06 did for the add-on bodies. The column *at the outer skin* gives the same number 4 mm further out along each hole axis, where the fingers are; the hole axes spread outward, so it is larger. It decides nothing.

| Quantity | On the cavity surface (checked) | At the outer skin |
| --- | --- | --- |
| Left hand, pinky → ring → middle → index, straight 3D distance | 17.1 / 17.7 / 16.4 mm | 18.7 / 18.2 / 17.3 mm |
| Right hand, pinky → ring → middle → index, straight 3D distance | 17.1 / 18.0 / 17.1 mm | 17.4 / 18.3 / 17.9 mm |
| Hand span pinky to index, left / right (plan view) | 49.7 / 50.7 mm | 52.4 / 51.9 mm |
| Pinky to pinky (plan view) | 102.8 mm | 105.9 mm |
| Arch, ring and middle: left / right | 3.0, 3.4 / 3.5, 3.8 mm | 3.6, 4.0 / 3.9, 4.3 mm |
| Angle between the hand lines | 1.6° | 1.0° |
| Right-hand line nearer the player by | 19.5 mm | 22.5 mm |
| R index from L index: across / along the hand axis | 19.5 / 0.5 mm | 22.5 / -0.9 mm |
| sub1: nearest finger hole, distance, off the normal of that hand line | L_ring, 10.00 mm, -0° | L_ring, 11.63 mm, -4° |
| sub2: nearest finger hole, distance, off the normal of that hand line | R_middle, 7.50 mm, 0° | R_middle, 8.75 mm, -4° |
| L thumb from L pinky / R thumb from R middle, along the hand axis | 4.1 / -7.4 mm | 4.5 / -7.2 mm |
| Body end from the pinky hole centre, bulb / tail (plan view, along the hand axis) | 10.7 / 19.6 mm | – |
| The same from the hole edge (the rest space) | 6.7 / 17.7 mm | – |

Lean of each finger hole (angle of the hole axis against the normal of the finger face). *Toward the end*: along the hand axis toward the nearer end of the body. *Toward the hand*: across the hand axis toward the hand that covers the hole (left hand: the far side; right hand: the player).

| Hole | Total lean | Toward the end | Toward the hand | Mostly toward |
| --- | --- | --- | --- | --- |
| L_pinky | 31° | +31° | -1° | bulb |
| L_ring | 8° | +7° | -3° | bulb |
| L_middle | 5° | -0° | +5° | far |
| L_index | 23° | -9° | +21° | far |
| R_pinky | 18° | +16° | -7° | tail |
| R_ring | 13° | +12° | -3° | tail |
| R_middle | 10° | +8° | +7° | tail |
| R_index | 23° | -0° | +23° | player |

Layout record: kind `template`; sub1 slides 10.00 mm from L_ring (preset 10 mm); sub2 slides 7.50 mm from R_middle (preset 7.5 mm); smallest planned gaps sub2–R_middle 4.40, sub1–L_ring 5.16, L_ring–L_pinky 9.74, L_middle–L_index 9.77, L_ring–L_middle 10.43 mm.
- MOVED THUMB HOLE (an ergonomic change): L_thumb moved -4.3 mm along the hand axis (+ toward the tail) and -6 mm across it (preset value thumb_offsets_mm)
- MOVED THUMB HOLE (an ergonomic change): R_thumb moved +0 mm along the hand axis (+ toward the tail) and +0 mm across it (preset value thumb_offsets_mm)
- R_index: the sideways offset was limited from -12.1 to -9.5 mm (35 % of the half section there)
- L_index: the sideways offset was limited from +11.4 to +9.8 mm (35 % of the half section there)
- L_thumb: the sideways offset was limited from -9.3 to -8.1 mm (35 % of the half section there)
- the hole positions are those of the base; the diameters are sized for the wall measured at each hole of the edited shell

## Volumes

- Cavity mesh: loft 77.7637 cm³ + voicing pocket 0.0533 cm³ = 77.8170 cm³; kernel target 77.8170 cm³.
- Capped air: 79.7504 cm³ measured on the STL by column integration (0.25 mm grid), 80.0156 cm³ as the air mesh; target 80.0000 cm³ (kernel V0 80.0000 cm³, volume factor 1). Kernel bookkeeping: 2.247 cm³ of air in the holes, 0.064 cm³ of tube wall.
- Plastic volume of the body 64.99 cm³. Air with the window throat (FEM export) 80.2669 cm³.
- Exported air files: capped 80.0156 cm³ (manifold True, shells 1); with throat 80.2669 cm³ (manifold True).
- Cavity-mode desk check: first mode 1899 Hz, second 3168 Hz, top note 1396.9 Hz, speed of sound 347.3 m/s; voxel volume 79.93 cm³ on the 1.5 mm grid; numpy 2.5.5, scipy 1.18.1, python 3.12.16.

## Booleans

| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |
| --- | --- | --- | --- | --- |
| shell + neck | MANIFOLD | +10386.89 | between -0 and +26348 | yes |
| cavity + voicing pocket (air) | MANIFOLD | +53.26 | between +0 and +1285 | yes |
| envelope - cavity air | MANIFOLD | -77817.00 | -77817.00 | yes |
| tube sub2 | MANIFOLD | +92.56 | +93.72 | yes |
| hole sub1 | MANIFOLD | -22.32 | -22.29 | yes |
| hole sub2 | MANIFOLD | -51.93 | -52.04 | yes |
| hole R_pinky | MANIFOLD | -34.68 | -34.55 | yes |
| hole R_ring | MANIFOLD | -46.99 | -46.87 | yes |
| hole R_middle | MANIFOLD | -23.41 | -23.38 | yes |
| hole R_index | MANIFOLD | -76.31 | -76.11 | yes |
| hole L_ring | MANIFOLD | -105.20 | -104.89 | yes |
| hole L_middle | MANIFOLD | -147.64 | -147.09 | yes |
| hole L_index | MANIFOLD | -69.55 | -69.38 | yes |
| hole L_thumb | MANIFOLD | -653.23 | -647.37 | yes |
| hole R_thumb | MANIFOLD | -900.64 | -895.43 | yes |
| hole L_pinky | MANIFOLD | -159.25 | -157.48 | yes |
| window throat + labium ramp | MANIFOLD | -998.41 | -998.94 | yes |
| windway | MANIFOLD | -960.15 | -960.36 | yes |

## Voicing, measured on the mesh

| Quantity | Measured | Voicing record |
| --- | --- | --- |
| Window length (windway exit to labium) | 8.890 mm | 8.890 mm |
| Window width (broad end) | 9.048 mm | 9.048 mm |
| Window area | 62.83 mm² | 62.84 mm² |
| Widest point, from the windway exit | 4.419 mm | 4.419 mm |
| Windway exit height × width | 1.200 × 9.048 mm | 1.200 × 9.048 mm |
| Windway inlet height × width | 3.000 × 9.048 mm | 3.000 × 9.048 mm |
| Labium ramp angle | 20.00° | 20.00° |
| Labium edge thickness | 0.400 mm | 0.400 mm |
| Labium edge against the windway centre line | -0.200 mm | -0.200 mm |
| Windway roof thickness / floor lip at the exit | 2.99 / 2.46 mm | – |
| Free depth below the window (keep-out 10 mm) | 29.9 mm | – |
| Neck: mouth end width × depth; width × depth where it meets the body | 14.0 × 9.6 mm; 38.0 × 26.0 mm (at least 1.2 mm of plastic around the pipe) | – |
| Pocket blend: reach beyond the flat part until it meets the chamber wall | 3.1 to 5.1 mm (125 of 125 directions end on it) | radius 12 mm |
| Plastic above the outer face, seen from the window rim (keep-out flare 45°) | at most 11.6° steep, 4.2 mm high | at most 45° |

## Holes, measured on the mesh

Diameter: from the area of the bore in a slice at mid wall. Chimney: a ray along the hole axis through the wall before the hole is cut (doc 02, Phase 4 step 5). Bore wall: mean length of the cut bore wall in the final mesh (it is a little longer than the axis chimney on a curved wall). Axis: angle between the bore axis and the normal of the cavity mesh.

| Hole | Deck | d kernel | d measured | Error | Chimney kernel | Chimney measured | Error | Bore wall | Tube | Axis ° | Moved | Nearest gap | To window | To ramp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | top | 3.037 | 3.037 | +0.0000 | 3.08 | 3.077 | +0.0054 | 3.08 | – | 0.36 | 0.00 | 5.16 (L_ring) | 30.9 | 30.9 |
| sub2 | top | 3.066 | 3.066 | -0.0000 | 7.05 | 7.045 | +0.0000 | 7.02 | 4.00 mm, wall 1.20 | 0.16 | 0.00 | 4.40 (R_middle) | 51.0 | 45.6 |
| R_pinky | top | 3.795 | 3.795 | +0.0000 | 3.05 | 3.056 | +0.0017 | 3.07 | – | 0.76 | 0.00 | 13.01 (R_ring) | 76.3 | 68.8 |
| R_ring | top | 4.428 | 4.428 | +0.0000 | 3.04 | 3.047 | +0.0013 | 3.06 | – | 0.84 | 0.00 | 13.01 (R_pinky) | 62.4 | 55.8 |
| R_middle | top | 3.129 | 3.129 | -0.0000 | 3.04 | 3.042 | +0.0021 | 3.05 | – | 0.80 | 0.00 | 4.40 (sub2) | 50.2 | 45.4 |
| R_index | top | 5.634 | 5.634 | +0.0000 | 3.05 | 3.054 | +0.0030 | 3.07 | – | 1.01 | 0.00 | 12.74 (R_middle) | 37.7 | 36.0 |
| L_ring | top | 6.634 | 6.634 | -0.0000 | 3.03 | 3.038 | +0.0016 | 3.05 | – | 1.01 | 0.00 | 5.16 (sub1) | 34.2 | 33.3 |
| L_middle | top | 7.855 | 7.855 | +0.0000 | 3.04 | 3.039 | +0.0028 | 3.05 | – | 0.79 | 0.00 | 9.77 (L_index) | 35.8 | 36.1 |
| L_index | top | 5.375 | 5.375 | +0.0000 | 3.06 | 3.059 | +0.0027 | 3.07 | – | 1.01 | 0.00 | 9.77 (L_middle) | 41.8 | 38.7 |
| L_thumb | bottom | 11.791 | 11.791 | +0.0000 | 5.93 | 5.936 | +0.0040 | 6.03 | – | 1.08 | 0.00 | 12.47 (L_pinky) | 13.2 | 5.8 |
| R_thumb | bottom | 13.765 | 13.765 | +0.0000 | 6.02 | 6.003 | +0.0048 | 6.10 | – | 0.24 | 0.00 | 19.51 (sub2) | 24.6 | 15.1 |
| L_pinky | top | 8.041 | 8.041 | -0.0000 | 3.10 | 3.097 | +0.0043 | 3.18 | – | 0.96 | 0.00 | 9.74 (L_ring) | 36.3 | 32.0 |

All lengths in millimetres.

## Edited shell (shell-edit build, prototype)

The outer shell (90758 triangles, 136.58 cm³ solid) and the neck (4736 triangles) were edited after the add-on made them, and this body was cut out of them. The chamber, the voicing and the hole positions are the add-on's. The wall at each hole was measured on the edited shell and each hole was sized for it, in 3 sizing rounds; the chamber was solved again so that the capped air is still V0 (chamber 77.817 cm³; 78.113 cm³ on the base).

*Wall*: the rule's wall (4 mm) plus the mean of what the edit added over the hole. *On the axis*: the edited shell along the hole axis. *Rim relief*: how much the added plastic varies around the rim.

| Hole | Wall | Added by the edit | On the axis | Rim relief | d on the base | d cut | Change |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sub1 | 3.078 | -0.922 | 3.072 | 0.04 | 3.343 | 3.037 | -0.305 |
| sub2 | 3.049 | -0.951 | 3.045 | 0.01 | 3.057 | 3.066 | +0.009 |
| R_pinky | 3.056 | -0.944 | 3.055 | 0.02 | 4.161 | 3.795 | -0.365 |
| R_ring | 3.046 | -0.954 | 3.045 | 0.01 | 4.835 | 4.428 | -0.407 |
| R_middle | 3.042 | -0.958 | 3.040 | 0.00 | 3.452 | 3.129 | -0.323 |
| R_index | 3.055 | -0.945 | 3.050 | 0.04 | 6.094 | 5.634 | -0.460 |
| L_ring | 3.037 | -0.963 | 3.036 | 0.01 | 7.141 | 6.634 | -0.507 |
| L_middle | 3.037 | -0.963 | 3.036 | 0.01 | 8.395 | 7.855 | -0.540 |
| L_index | 3.060 | -0.940 | 3.056 | 0.04 | 5.805 | 5.375 | -0.430 |
| L_thumb | 5.929 | +1.929 | 5.932 | 0.28 | 10.758 | 11.791 | +1.033 |
| R_thumb | 6.018 | +2.018 | 5.999 | 0.05 | 12.715 | 13.765 | +1.050 |
| L_pinky | 3.103 | -0.897 | 3.093 | 0.15 | 8.563 | 8.041 | -0.522 |

All lengths in millimetres.

## Wall and topology

- Plain wall (cavity to outside along the normal, 2323 rays): minimum 3.037 mm, median 4.045 mm.
- Thinnest plastic of the finished body away from the voicing and the tubes (6000 rays): 1.75 mm at (-5.3, -34.1, 3.9).
- Topology of the STL: 176414 triangles, manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 13.

