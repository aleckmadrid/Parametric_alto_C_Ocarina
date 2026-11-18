# Geometry check: V-c

Written by `ocarina_addon/headless.py -- stage1`. Every measured number comes from the STL file `addon_out/stage1/V-c/V-c.stl`, read back from disk (66796 triangles).

Result: **no unexpected failure**; 0 warnings. Build and check time 32 s.

- Preset S0, V0 25.00 cm³, voice rating medium, no holes (a voicing stub).
- Voicing hash `f3803f8358b6`: teardrop window 9.65 × 18.57 mm, 123.50 mm², windway exit 1.20 × 18.57 mm, W/h 8.04.
- Cavity spine length 53.27 mm.
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).

## Checks

`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. `info` is a reported number that decides nothing.

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-c_air_capped.stl; holes and window closed): 4371 Hz = 3.13 × F6 on a 1.5 mm grid of 7426 cells (2 mm grid: 4351 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.509 + voicing pocket 0.491) = 25.0001 cm³ against the kernel's 25.0000 cm³: +0.0002 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0018 cm³ (+0.0072 %), air mesh 25.0001 cm³ (+0.0002 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0018 cm³ against the stub volume 25.0000 cm³ (+0.0072 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 983.9 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.18 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash f3803f8358b6; recomputed from the record: f3803f8358b6 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 18.568 mm, 123.48 mm² (record 9.650 × 18.568, 123.50); windway exit 1.200 × 18.568 mm, inlet 1.560 × 18.568 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.88 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.1 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 4.95 mm (at least 0.8 mm); windway roof 3.20 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 2.95 mm |

## Warnings

None.

## Volumes

- Cavity mesh: loft 24.5095 cm³ + voicing pocket 0.4906 cm³ = 25.0001 cm³; kernel target 25.0000 cm³.
- Capped air: 25.0018 cm³ measured on the STL by column integration (0.25 mm grid), 25.0001 cm³ as the air mesh; target 25.0000 cm³ (kernel V0 25.0000 cm³, volume factor 1). Kernel bookkeeping: 0.000 cm³ of air in the holes, 0.000 cm³ of tube wall.
- Plastic volume of the body 25.60 cm³. Air with the window throat (FEM export) 25.4940 cm³.
- Exported air files: capped 25.0001 cm³ (manifold True, shells 1); with throat 25.4940 cm³ (manifold True).
- Cavity-mode desk check: first mode 4371 Hz, second 5990 Hz, top note 1396.9 Hz, speed of sound 347.3 m/s; voxel volume 25.06 cm³ on the 1.5 mm grid; numpy 2.5.4, scipy 1.18.1, python 3.12.10.

## Booleans

| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |
| --- | --- | --- | --- | --- |
| cavity + voicing pocket (air) | MANIFOLD | +490.58 | between +0 and +1719 | yes |
| skin + voicing block | MANIFOLD | +5928.77 | between +0 and +8096 | yes |
| envelope - cavity air | MANIFOLD | -25000.06 | -25000.06 | yes |
| window throat + labium ramp | MANIFOLD | -937.47 | -939.15 | yes |
| windway | MANIFOLD | -780.70 | -781.89 | yes |

## Voicing, measured on the mesh

| Quantity | Measured | Voicing record |
| --- | --- | --- |
| Window length (windway exit to labium) | 9.650 mm | 9.650 mm |
| Window width (broad end) | 18.568 mm | 18.568 mm |
| Window area | 123.48 mm² | 123.50 mm² |
| Widest point, from the windway exit | 3.882 mm | 3.879 mm |
| Windway exit height × width | 1.200 × 18.568 mm | 1.200 × 18.568 mm |
| Windway inlet height × width | 1.560 × 18.568 mm | 1.560 × 18.568 mm |
| Labium ramp angle | 20.00° | 20.00° |
| Labium edge thickness | 0.400 mm | 0.400 mm |
| Labium edge against the windway centre line | -0.000 mm | +0.000 mm |
| Windway roof thickness / floor lip at the exit | 3.20 / 4.95 mm | – |
| Free depth below the window (keep-out 10 mm) | 20.1 mm | – |

## Wall and topology

- Plain wall (cavity to outside along the normal, 2323 rays): minimum 4.000 mm, median 4.000 mm.
- Thinnest plastic of the finished body away from the voicing and the tubes (6000 rays): 2.95 mm at (-12.4, -6.9, 12.1).
- Topology of the STL: 66796 triangles, manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1.

