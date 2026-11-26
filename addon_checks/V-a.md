# Geometry check: V-a

Written by `ocarina_addon/headless.py -- stage1`. Every measured number comes from the STL file `addon_out/stage1/V-a/V-a.stl`, read back from disk (72814 triangles).

Result: **no unexpected failure**; 0 warnings. Build and check time 17 s.

- Preset S0, V0 25.00 cm³, voice rating medium, no holes (a voicing stub).
- Voicing hash `312011ec9f0e`: teardrop window 9.65 × 8.81 mm, 62.84 mm², windway exit 1.20 × 8.81 mm, W/h 8.04.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm.
- Cavity spine length 53.34 mm.
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).

## Checks

`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. `info` is a reported number that decides nothing.

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-a_air_capped.stl; holes and window closed): 4364 Hz = 3.12 × F6 on a 1.5 mm grid of 7422 cells (2 mm grid: 4338 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.612 + voicing pocket 0.388) = 25.0000 cm³ against the kernel's 25.0000 cm³: -0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0022 cm³ (+0.0086 %), air mesh 25.0000 cm³ (-0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0022 cm³ against the stub volume 25.0000 cm³ (+0.0086 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 787.1 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.11 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash 312011ec9f0e; recomputed from the record: 312011ec9f0e |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.7 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 11° steep seen from the rim, 5.6 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 21.53 mm (at least 0.8 mm); windway roof 2.99 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 1.24 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 4.6 to 9.9 mm beyond the flat part. Back corners beside the windway exit: 2.5 mm, ends at the chamber's side wall; 2.5 mm, ends at the chamber's side wall |

## Warnings

None.

## Volumes

- Cavity mesh: loft 24.6118 cm³ + voicing pocket 0.3882 cm³ = 25.0000 cm³; kernel target 25.0000 cm³.
- Capped air: 25.0022 cm³ measured on the STL by column integration (0.25 mm grid), 25.0000 cm³ as the air mesh; target 25.0000 cm³ (kernel V0 25.0000 cm³, volume factor 1). Kernel bookkeeping: 0.000 cm³ of air in the holes, 0.000 cm³ of tube wall.
- Plastic volume of the body 30.20 cm³. Air with the window throat (FEM export) 25.2513 cm³.
- Exported air files: capped 25.0000 cm³ (manifold True, shells 1); with throat 25.2513 cm³ (manifold True).
- Cavity-mode desk check: first mode 4364 Hz, second 6022 Hz, top note 1396.9 Hz, speed of sound 347.3 m/s; voxel volume 25.05 cm³ on the 1.5 mm grid; numpy 2.5.5, scipy 1.18.1, python 3.12.16.

## Booleans

| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |
| --- | --- | --- | --- | --- |
| cavity + voicing pocket (air) | MANIFOLD | +388.24 | between +0 and +2251 | yes |
| skin + voicing block | MANIFOLD | +9630.86 | between +0 and +21227 | yes |
| envelope - cavity air | MANIFOLD | -25000.00 | -25000.00 | yes |
| window throat + labium ramp | MANIFOLD | -413.70 | -413.73 | yes |
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
| Windway roof thickness / floor lip at the exit | 2.99 / 21.53 mm | – |
| Free depth below the window (keep-out 10 mm) | 20.7 mm | – |
| Neck: mouth end width × depth; width × depth where it meets the body | 13.8 × 7.6 mm; 42.3 × 24.5 mm (at least 1.2 mm of plastic around the pipe) | – |
| Pocket blend: reach beyond the flat part until it meets the chamber wall | 4.6 to 9.9 mm (125 of 125 directions end on it) | radius 12 mm |
| Plastic above the outer face, seen from the window rim (keep-out flare 45°) | at most 10.9° steep, 5.6 mm high | at most 45° |

## Wall and topology

- Plain wall (cavity to outside along the normal, 2323 rays): minimum 4.000 mm, median 4.000 mm.
- Thinnest plastic of the finished body away from the voicing and the tubes (6000 rays): 1.24 mm at (-4.8, -30.4, 11.4).
- Topology of the STL: 72814 triangles, manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1.

