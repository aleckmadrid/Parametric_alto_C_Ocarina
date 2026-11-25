# Stage 1 · Voicing stubs: generation report

Written by `ocarina_addon/headless.py -- stage1` on 2026-11-19. Every measured number comes from the STL file of the body, read back from disk. Run time 236 s for 7 bodies.

Result: **6 of 7 bodies have no unexpected failure**; UNEXPECTED FAILURES on V-a3.

- A stub is a small egg (25 cm³ of capped air, preset `S0`) with a generated voicing, the 4 mm wall and no holes. Its pitch at a known volume gives η_w·G_w for that voicing. A stub with the window of a body has the voicing hash of that body.
- The predicted pitch uses the prior η_w. It is a prediction, not a measurement.
- Every stub has the build of the bodies (the ellipse cut, the neck that stands off the body, the pipe lowered inside it, the pocket blend; owner decisions of 2026-11-18), except V-af and V-b. V-af is the same window as V-a with the plain build (fan cut, level windway, box stub). The build is part of the hash, so V-af has a hash that no body carries. V-a against V-af says what the build is worth and whether it speaks. V-b, the rounded rectangle, has the plain build too (the ellipse cut is made for the teardrop), so the shape pair is V-b against V-af.
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).
- Everything is pre-calibration: η_w prior 0.90, k_hole 0.8 for the first prints, 27 °C internal air. Nothing in this report was measured on a printed body.
- Statuses: `pass` (the docs say ok), `FAIL`, `NEEDS FEM` (cavity-mode desk check between its limits), `WARN` (a soft ergonomic check; never a failure), `info` (a reported number).

## Bodies

| Body | Preset | V0 | Voicing hash | Window | Windway exit | Capped air on the STL | First cavity mode (desk check) | Plastic; solid PLA mass | doc 04 mass | Failures | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V-a | S0 | 25.0 cm³ | `312011ec9f0e` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 25.002 cm³ (+0.009 %) | 3.12 × F6, pass | 30.2 cm³; 37 g | 50–54 g | none | – |
| V-af | S0 | 25.0 cm³ | `f661bfc7ca55` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 25.005 cm³ (+0.020 %) | 3.11 × F6, pass | 24.5 cm³; 30 g | 50–54 g | none | – |
| V-b | S0 | 25.0 cm³ | `d8753766fe77` | Rounded rectangle 9.65 × 6.60 mm, 62.8 mm² | 1.20 × 6.60 mm | 25.000 cm³ (+0.000 %) | 3.10 × F6, pass | 24.4 cm³; 30 g | 50–54 g | none | – |
| V-d | S0 | 25.0 cm³ | `8533277752bf` | Teardrop 9.65 × 6.96 mm, 46.5 mm² | 1.20 × 6.96 mm | 25.002 cm³ (+0.007 %) | 3.12 × F6, pass | 26.9 cm³; 33 g | 50–54 g | none | – |
| V-a0 | S0 | 25.0 cm³ | `0b46df739839` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 25.002 cm³ (+0.007 %) | 3.12 × F6, pass | 30.2 cm³; 37 g | 50–54 g | none | – |
| V-a35 | S0 | 25.0 cm³ | `41c6721c2f51` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 25.002 cm³ (+0.008 %) | 3.12 × F6, pass | 30.2 cm³; 37 g | 50–54 g | none | – |
| V-a3 | S0 | 25.0 cm³ | `db0ca1402d20` | Teardrop 9.65 × 7.93 mm, 54.4 mm² | 1.20 × 7.93 mm | 25.002 cm³ (+0.008 %) | 3.12 × F6, pass | 28.4 cm³; 35 g | 50–54 g | **voicing_keepouts (unexpected)** | – |

*Capped air* is compared with the target of the model: V0 for a round-1 body, the stub volume for a stub, and in Stage 3 V0 divided by the fitted volume factor, with the holes drawn at their CAD diameters. *First cavity mode* is the computed desk check with closed holes, which gives the verdict; the number in brackets is the kernel's c/(2L) estimate from the length of the chamber, the lowest estimate, shown for information (it is 30 to 44 % low for these shapes, docs/06 section 3.10). *Solid PLA mass* is the plastic volume of the STL at 1.24 g/cm³, with no supports, brim or infill saving; the doc 04 figure includes about 12 % for supports and a brim.

Total for the 7 bodies of this stage: 242 g of solid PLA, 271 g with 12 % for supports and a brim. The doc 04 budget for this stage is 200 g for the four stubs, about 100 g more for the optional V-a0 and V-a35, and about 50 g for the optional V-a3. The generated bodies are lighter than the budget; the doc 04 masses were estimates made before any body was built.

## Unexpected failures

- **V-a3** `voicing_keepouts`: inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.2 mm; no tube inside the keep-out; outside: 179 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 90° steep seen from the rim, 6.6 mm high; allowed up to 45°)

## Expected failures

Failures that the plan expects (the pad-limit checks: doc 04 prints these holes on purpose, "the real limit is unknown"). They do not stop a stage.

None.

## Warnings

Soft ergonomic checks outside their range. They are measurements for the owner to judge. A warning is never a failure.

None.

## Sizes against doc 04

The stub table of [docs/04](../docs/04-testing-phase.md), Stage 1, with the generated numbers.

| Stub | Window (generated) | Windway exit | Labium offset | Voicing hash | Same hash as | Stub volume on the STL | Predicted pitch | Tests | Build |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V-a | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | -0.2 mm | `312011ec9f0e` | the 80 cm³ bodies | 25.002 cm³ | 787 Hz | Baseline: the 80 cm³ window with the build of the bodies | of the rules |
| V-af | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | -0.2 mm | `f661bfc7ca55` | no body | 25.005 cm³ | 787 Hz | V-a with the plain build (fan cut, level windway, box stub): what the ellipse cut, the tilt and the neck are worth | plain |
| V-b | Rounded rectangle 9.65 × 6.60 mm, 62.8 mm² | 1.20 × 6.60 mm | -0.2 mm | `d8753766fe77` | no body | 25.000 cm³ | 787 Hz | Window shape at equal area; pairs with V-af (both have the plain build) | plain |
| V-d | Teardrop 9.65 × 6.96 mm, 46.5 mm² | 1.20 × 6.96 mm | -0.2 mm | `8533277752bf` | the 65 cm³ bodies | 25.002 cm³ | 709 Hz | Proven-band reference: the 65 cm³ window | of the rules |
| V-a0 | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | +0.0 mm | `0b46df739839` | no body | 25.002 cm³ | 787 Hz | V-a with the labium offset 0 mm (labium height: brackets the −0.2 mm default) | of the rules |
| V-a35 | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | -0.35 mm | `41c6721c2f51` | no body | 25.002 cm³ | 787 Hz | V-a with the labium offset −0.35 mm (labium height: brackets the −0.2 mm default) | of the rules |
| V-a3 | Teardrop 9.65 × 7.93 mm, 54.4 mm² | 1.20 × 7.93 mm | -0.2 mm | `db0ca1402d20` | no body | 25.002 cm³ | 787 Hz | The 80 cm³ window at the 3 mm window wall: η_w at 3 mm, against V-a at 4 mm | of the rules |

## Per body

### V-a

*Baseline: the 80 cm³ window with the build of the bodies.*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `312011ec9f0e`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.002 cm³ against the model target 25.000 cm³ (+0.009 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.3 mm. Plastic 30.2 cm³.
- Stub: window sized for the 80 cm³ body. Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

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

Files: stl: `addon_out/stage1/V-a/V-a.stl`, air_capped_stl: `addon_out/stage1/V-a/V-a_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-a/V-a_air_fem.stl`, renders: `addon_renders/V-a/`, measurement_template: `addon_out/stage1/V-a/V-a_measurement.toml`, check_report: `addon_checks/V-a.md`.

### V-af

*V-a with the plain build (fan cut, level windway, box stub): what the ellipse cut, the tilt and the neck are worth.*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `f661bfc7ca55`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build: plain (fan cut, level windway, box stub, no pocket blend). The build is not in this hash.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.005 cm³ against the model target 25.000 cm³ (+0.020 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.4 mm. Plastic 24.5 cm³.
- Stub: window sized for the 80 cm³ body. Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-af_air_capped.stl; holes and window closed): 4343 Hz = 3.11 × F6 on a 1.5 mm grid of 7423 cells (2 mm grid: 4330 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.765 + voicing pocket 0.235) = 25.0000 cm³ against the kernel's 25.0000 cm³: +0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0051 cm³ (+0.0202 %), air mesh 25.0000 cm³ (+0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0051 cm³ against the stub volume 25.0000 cm³ (+0.0202 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 787.1 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.21 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash f661bfc7ca55; recomputed from the record: f661bfc7ca55 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.7 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (nothing stands above the outer face) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 5.08 mm (at least 0.8 mm); windway roof 2.99 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm (it must be at least 0.4 mm, one extrusion line) |

Files: stl: `addon_out/stage1/V-af/V-af.stl`, air_capped_stl: `addon_out/stage1/V-af/V-af_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-af/V-af_air_fem.stl`, renders: `addon_renders/V-af/`, measurement_template: `addon_out/stage1/V-af/V-af_measurement.toml`, check_report: `addon_checks/V-af.md`.

### V-b

*Window shape at equal area; pairs with V-af (both have the plain build).*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `d8753766fe77`. Window: Rounded rectangle 9.65 × 6.60 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 6.60 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build: plain (fan cut, level windway, box stub, no pocket blend). The build is not in this hash.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.000 cm³ against the model target 25.000 cm³ (+0.000 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.5 mm. Plastic 24.4 cm³.
- Stub: window sized for the 80 cm³ body, forced to a rounded rectangle of the same area (no body carries this window). Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-b_air_capped.stl; holes and window closed): 4336 Hz = 3.10 × F6 on a 1.5 mm grid of 7421 cells (2 mm grid: 4322 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.801 + voicing pocket 0.199) = 25.0000 cm³ against the kernel's 25.0000 cm³: -0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0001 cm³ (+0.0004 %), air mesh 25.0000 cm³ (-0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0001 cm³ against the stub volume 25.0000 cm³ (+0.0004 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 787.1 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.66 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash d8753766fe77; recomputed from the record: d8753766fe77 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 6.601 mm, 62.80 mm² (record 9.650 × 6.601, 62.84); windway exit 1.200 × 6.601 mm, inlet 3.000 × 6.601 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end: not applicable to a rounded rectangle, which has one width (full width from 1.0 mm to 8.65 mm of the 9.65 mm length); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 24.3 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (nothing stands above the outer face) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 5.08 mm (at least 0.8 mm); windway roof 2.99 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm (it must be at least 0.4 mm, one extrusion line) |

Files: stl: `addon_out/stage1/V-b/V-b.stl`, air_capped_stl: `addon_out/stage1/V-b/V-b_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-b/V-b_air_fem.stl`, renders: `addon_renders/V-b/`, measurement_template: `addon_out/stage1/V-b/V-b_measurement.toml`, check_report: `addon_checks/V-b.md`.

### V-d

*Proven-band reference: the 65 cm³ window.*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `8533277752bf`. Window: Teardrop 9.65 × 6.96 mm, 46.5 mm², wall 4.0 mm. Windway: exit 1.20 × 6.96 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.002 cm³ against the model target 25.000 cm³ (+0.007 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.4 mm. Plastic 26.9 cm³.
- Stub: window sized for the 65 cm³ body. Predicted pitch 709.5 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-d_air_capped.stl; holes and window closed): 4357 Hz = 3.12 × F6 on a 1.5 mm grid of 7432 cells (2 mm grid: 4339 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.646 + voicing pocket 0.354) = 24.9999 cm³ against the kernel's 25.0000 cm³: -0.0005 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0016 cm³ (+0.0066 %), air mesh 24.9999 cm³ (-0.0005 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0016 cm³ against the stub volume 25.0000 cm³ (+0.0066 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 709.5 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.19 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash 8533277752bf; recomputed from the record: 8533277752bf |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 6.959 mm, 46.46 mm² (record 9.650 × 6.959, 46.47); windway exit 1.200 × 6.959 mm, inlet 3.000 × 6.959 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 6.959 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.48 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 19.7 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 11° steep seen from the rim, 5.6 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 18.89 mm (at least 0.8 mm); windway roof 2.99 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 1.25 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 4.1 to 10.3 mm beyond the flat part. Back corners beside the windway exit: 3.5 mm, ends at the chamber's side wall; 3.5 mm, ends at the chamber's side wall |

Files: stl: `addon_out/stage1/V-d/V-d.stl`, air_capped_stl: `addon_out/stage1/V-d/V-d_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-d/V-d_air_fem.stl`, renders: `addon_renders/V-d/`, measurement_template: `addon_out/stage1/V-d/V-d_measurement.toml`, check_report: `addon_checks/V-d.md`.

### V-a0

*V-a with the labium offset 0 mm (labium height: brackets the −0.2 mm default) (optional stub of doc 04).*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `0b46df739839`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.002 cm³ against the model target 25.000 cm³ (+0.007 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.3 mm. Plastic 30.2 cm³.
- Stub: window sized for the 80 cm³ body. Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-a0_air_capped.stl; holes and window closed): 4364 Hz = 3.12 × F6 on a 1.5 mm grid of 7422 cells (2 mm grid: 4338 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.612 + voicing pocket 0.388) = 25.0000 cm³ against the kernel's 25.0000 cm³: -0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0017 cm³ (+0.0067 %), air mesh 25.0000 cm³ (-0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0017 cm³ against the stub volume 25.0000 cm³ (+0.0067 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 787.1 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.11 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash 0b46df739839; recomputed from the record: 0b46df739839 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.000 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.7 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 10° steep seen from the rim, 5.4 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 21.33 mm (at least 0.8 mm); windway roof 3.19 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 1.18 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 4.6 to 9.9 mm beyond the flat part. Back corners beside the windway exit: 2.5 mm, ends at the chamber's side wall; 2.5 mm, ends at the chamber's side wall |

Files: stl: `addon_out/stage1/V-a0/V-a0.stl`, air_capped_stl: `addon_out/stage1/V-a0/V-a0_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-a0/V-a0_air_fem.stl`, renders: `addon_renders/V-a0/`, measurement_template: `addon_out/stage1/V-a0/V-a0_measurement.toml`, check_report: `addon_checks/V-a0.md`.

### V-a35

*V-a with the labium offset −0.35 mm (labium height: brackets the −0.2 mm default) (optional stub of doc 04).*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `41c6721c2f51`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.35 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.002 cm³ against the model target 25.000 cm³ (+0.008 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.3 mm. Plastic 30.2 cm³.
- Stub: window sized for the 80 cm³ body. Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-a35_air_capped.stl; holes and window closed): 4364 Hz = 3.12 × F6 on a 1.5 mm grid of 7422 cells (2 mm grid: 4338 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.612 + voicing pocket 0.388) = 25.0000 cm³ against the kernel's 25.0000 cm³: -0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0020 cm³ (+0.0078 %), air mesh 25.0000 cm³ (-0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0020 cm³ against the stub volume 25.0000 cm³ (+0.0078 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 787.1 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.11 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash 41c6721c2f51; recomputed from the record: 41c6721c2f51 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 3.000 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.350 mm; the window area is the free opening seen along the normal (widest there: 8.806 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.7 mm; no tube inside the keep-out; outside: 0 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 11° steep seen from the rim, 5.7 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 21.68 mm (at least 0.8 mm); windway roof 2.84 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 1.32 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 4.6 to 9.9 mm beyond the flat part. Back corners beside the windway exit: 2.5 mm, ends at the chamber's side wall; 2.5 mm, ends at the chamber's side wall |

Files: stl: `addon_out/stage1/V-a35/V-a35.stl`, air_capped_stl: `addon_out/stage1/V-a35/V-a35_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-a35/V-a35_air_fem.stl`, renders: `addon_renders/V-a35/`, measurement_template: `addon_out/stage1/V-a35/V-a35_measurement.toml`, check_report: `addon_checks/V-a35.md`.

### V-a3

*The 80 cm³ window at the 3 mm window wall: η_w at 3 mm, against V-a at 4 mm (optional stub of doc 04).*

- Result: **UNEXPECTED FAILURES: voicing_keepouts**; 0 warnings.
- Voicing hash `db0ca1402d20`. Window: Teardrop 9.65 × 7.93 mm, 54.4 mm², wall 3.0 mm. Windway: exit 1.20 × 7.93 mm, inlet height 3.00 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.002 cm³ against the model target 25.000 cm³ (+0.008 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.4 mm. Plastic 28.4 cm³.
- Stub: window sized for the 80 cm³ body. Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-a3_air_capped.stl; holes and window closed): 4359 Hz = 3.12 × F6 on a 1.5 mm grid of 7432 cells (2 mm grid: 4339 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.629 + voicing pocket 0.371) = 25.0000 cm³ against the kernel's 25.0000 cm³: +0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0020 cm³ (+0.0080 %), air mesh 25.0000 cm³ (+0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0020 cm³ against the stub volume 25.0000 cm³ (+0.0080 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 787.1 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.21 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash db0ca1402d20; recomputed from the record: db0ca1402d20 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 7.935 mm, 54.40 mm² (record 9.650 × 7.935, 54.40); windway exit 1.200 × 7.935 mm, inlet 3.000 × 7.935 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm; the window area is the free opening seen along the normal (widest there: 7.935 mm) |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.97 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | FAIL | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.2 mm; no tube inside the keep-out; outside: 179 points of the surface inside the 45° flare from the window rim (the plastic above the outer face stands at most 90° steep seen from the rim, 6.6 mm high; allowed up to 45°) |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 19.57 mm (at least 0.8 mm); windway roof 1.99 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 1.27 mm (it must be at least 0.4 mm, one extrusion line) |
| `pocket_blend` | pass | the pocket ceiling falls away behind the labium on a 12 mm radius until it meets the chamber wall: 125 of 125 directions around the labium half of the window meet it; reach 4.4 to 10.1 mm beyond the flat part. Back corners beside the windway exit: 3.0 mm, ends at the chamber's side wall; 3.0 mm, ends at the chamber's side wall |

Files: stl: `addon_out/stage1/V-a3/V-a3.stl`, air_capped_stl: `addon_out/stage1/V-a3/V-a3_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-a3/V-a3_air_fem.stl`, renders: `addon_renders/V-a3/`, measurement_template: `addon_out/stage1/V-a3/V-a3_measurement.toml`, check_report: `addon_checks/V-a3.md`.

