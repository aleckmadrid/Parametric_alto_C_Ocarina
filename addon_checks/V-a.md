# Geometry check: V-a

Written by `ocarina_addon/headless.py -- stage1`. Every measured number comes from the STL file `addon_out/stage1/V-a/V-a.stl`, read back from disk (67762 triangles).

Result: **no unexpected failure**; 0 warnings. Build and check time 33 s.

- Preset S0, V0 25.00 cm³, voice rating medium, no holes (a voicing stub).
- Voicing hash `d1b6418b1844`: teardrop window 9.65 × 8.81 mm, 62.84 mm², windway exit 1.20 × 8.81 mm, W/h 8.04.
- Cavity spine length 53.45 mm.
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).

## Checks

`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. `info` is a reported number that decides nothing.

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-a_air_capped.stl; holes and window closed): 4343 Hz = 3.11 × F6 on a 1.5 mm grid of 7423 cells (2 mm grid: 4330 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.765 + voicing pocket 0.235) = 25.0000 cm³ against the kernel's 25.0000 cm³: +0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0051 cm³ (+0.0202 %), air mesh 25.0000 cm³ (+0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0051 cm³ against the stub volume 25.0000 cm³ (+0.0202 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 787.1 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.21 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash d1b6418b1844; recomputed from the record: d1b6418b1844 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 4.89 mm (at least 0.8 mm); windway roof 3.20 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |

## Warnings

None.

## Volumes

- Cavity mesh: loft 24.7651 cm³ + voicing pocket 0.2349 cm³ = 25.0000 cm³; kernel target 25.0000 cm³.
- Capped air: 25.0051 cm³ measured on the STL by column integration (0.25 mm grid), 25.0000 cm³ as the air mesh; target 25.0000 cm³ (kernel V0 25.0000 cm³, volume factor 1). Kernel bookkeeping: 0.000 cm³ of air in the holes, 0.000 cm³ of tube wall.
- Plastic volume of the body 24.50 cm³. Air with the window throat (FEM export) 25.2513 cm³.
- Exported air files: capped 25.0000 cm³ (manifold True, shells 1); with throat 25.2513 cm³ (manifold True).
- Cavity-mode desk check: first mode 4343 Hz, second 6065 Hz, top note 1396.9 Hz, speed of sound 347.3 m/s; voxel volume 25.05 cm³ on the 1.5 mm grid; numpy 2.5.4, scipy 1.18.1, python 3.12.10.

## Booleans

| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |
| --- | --- | --- | --- | --- |
| cavity + voicing pocket (air) | MANIFOLD | +234.88 | between +0 and +1093 | yes |
| skin + voicing block | MANIFOLD | +3631.79 | between +0 and +5121 | yes |
| envelope - cavity air | MANIFOLD | -25000.00 | -25000.00 | yes |
| window throat + labium ramp | MANIFOLD | -541.67 | -542.82 | yes |
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
| Labium edge against the windway centre line | -0.000 mm | +0.000 mm |
| Windway roof thickness / floor lip at the exit | 3.20 / 4.89 mm | – |
| Free depth below the window (keep-out 10 mm) | 20.7 mm | – |

## Wall and topology

- Plain wall (cavity to outside along the normal, 2322 rays): minimum 4.000 mm, median 4.000 mm.
- Thinnest plastic of the finished body away from the voicing and the tubes (6000 rays): 4.00 mm at (-0.9, 31.1, 8.8).
- Topology of the STL: 67762 triangles, manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1.

