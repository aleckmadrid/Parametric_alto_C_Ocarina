# Stage 1 · Voicing stubs: generation report

Written by `ocarina_addon/headless.py -- stage1` on 2026-11-17. Every measured number comes from the STL file of the body, read back from disk. Run time 175 s for 6 bodies.

Result: **5 of 6 bodies have no unexpected failure**; UNEXPECTED FAILURES on V-a3.

- A stub is a small egg (25 cm³ of capped air, preset `S0`) with a generated voicing, the 4 mm wall and no holes. Its pitch at a known volume gives η_w·G_w for that voicing. A stub with the window of a body has the voicing hash of that body.
- The predicted pitch uses the prior η_w. It is a prediction, not a measurement.
- Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), sub2 = sub_R (right subhole, opens C5).
- Everything is pre-calibration: η_w prior 0.90, k_hole 0.8 for the first prints, 27 °C internal air. Nothing in this report was measured on a printed body.
- Statuses: `pass` (the docs say ok), `FAIL`, `NEEDS FEM` (cavity-mode desk check between its limits), `WARN` (a soft ergonomic check; never a failure), `info` (a reported number).

## Bodies

| Body | Preset | V0 | Voicing hash | Window | Windway exit | Capped air on the STL | First cavity mode (desk check) | Plastic; solid PLA mass | doc 04 mass | Failures | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V-a | S0 | 25.0 cm³ | `617b869f0b10` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 25.005 cm³ (+0.020 %) | 3.11 × F6, pass | 24.4 cm³; 30 g | 50–54 g | none | – |
| V-b | S0 | 25.0 cm³ | `c7b50fadd14b` | Rounded rectangle 9.65 × 6.60 mm, 62.8 mm² | 1.20 × 6.60 mm | 25.000 cm³ (+0.000 %) | 3.10 × F6, pass | 24.2 cm³; 30 g | 50–54 g | none | – |
| V-d | S0 | 25.0 cm³ | `2a71c31c2505` | Teardrop 9.65 × 6.96 mm, 46.5 mm² | 1.20 × 6.96 mm | 25.002 cm³ (+0.010 %) | 3.10 × F6, pass | 24.2 cm³; 30 g | 50–54 g | none | – |
| V-a0 | S0 | 25.0 cm³ | `d1b6418b1844` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 25.005 cm³ (+0.020 %) | 3.11 × F6, pass | 24.5 cm³; 30 g | 50–54 g | none | – |
| V-a35 | S0 | 25.0 cm³ | `7979d16c8d36` | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | 25.005 cm³ (+0.020 %) | 3.11 × F6, pass | 24.3 cm³; 30 g | 50–54 g | none | – |
| V-a3 | S0 | 25.0 cm³ | `36ebbc5bd520` | Teardrop 9.65 × 7.93 mm, 54.4 mm² | 1.20 × 7.93 mm | 25.003 cm³ (+0.013 %) | 3.10 × F6, pass | 23.8 cm³; 29 g | 50–54 g | **voicing_keepouts (unexpected)** | – |

*Capped air* is compared with the target of the model: V0 for a round-1 body, the stub volume for a stub, and in Stage 3 V0 divided by the fitted volume factor, with the holes drawn at their CAD diameters. *First cavity mode* is the computed desk check with closed holes, which gives the verdict; the number in brackets is the kernel's c/(2L) estimate from the length of the chamber, the lowest estimate, shown for information (it is 30 to 44 % low for these shapes, docs/06 section 3.10). *Solid PLA mass* is the plastic volume of the STL at 1.24 g/cm³, with no supports, brim or infill saving; the doc 04 figure includes about 12 % for supports and a brim.

Total for the 6 bodies of this stage: 180 g of solid PLA, 202 g with 12 % for supports and a brim. The doc 04 budget for this stage is 150 g for the three stubs, about 100 g more for the optional V-a0 and V-a35, and about 50 g for the optional V-a3. The generated bodies are lighter than the budget; the doc 04 masses were estimates made before any body was built.

## Unexpected failures

- **V-a3** `voicing_keepouts`: inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.3 mm; no tube inside the keep-out; outside: 243 vertices above the 45° flare

## Expected failures

Failures that the plan expects (the pad-limit checks: doc 04 prints these holes on purpose, "the real limit is unknown"). They do not stop a stage.

None.

## Warnings

Soft ergonomic checks outside their range. They are measurements for the owner to judge. A warning is never a failure.

None.

## Sizes against doc 04

The stub table of [docs/04](../docs/04-testing-phase.md), Stage 1, with the generated numbers.

| Stub | Window (generated) | Windway exit | Labium offset | Voicing hash | Same hash as | Stub volume on the STL | Predicted pitch | Tests |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V-a | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | -0.2 mm | `617b869f0b10` | the 80 cm³ bodies | 25.005 cm³ | 787 Hz | Baseline: the 80 cm³ window |
| V-b | Rounded rectangle 9.65 × 6.60 mm, 62.8 mm² | 1.20 × 6.60 mm | -0.2 mm | `c7b50fadd14b` | no body | 25.000 cm³ | 787 Hz | Window shape at equal area; pairs with V-a |
| V-d | Teardrop 9.65 × 6.96 mm, 46.5 mm² | 1.20 × 6.96 mm | -0.2 mm | `2a71c31c2505` | the 65 cm³ bodies | 25.002 cm³ | 709 Hz | Proven-band reference: the 65 cm³ window |
| V-a0 | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | +0.0 mm | `d1b6418b1844` | no body | 25.005 cm³ | 787 Hz | V-a with the labium offset 0 mm (labium height: brackets the −0.2 mm default) |
| V-a35 | Teardrop 9.65 × 8.81 mm, 62.8 mm² | 1.20 × 8.81 mm | -0.35 mm | `7979d16c8d36` | no body | 25.005 cm³ | 787 Hz | V-a with the labium offset −0.35 mm (labium height: brackets the −0.2 mm default) |
| V-a3 | Teardrop 9.65 × 7.93 mm, 54.4 mm² | 1.20 × 7.93 mm | -0.2 mm | `36ebbc5bd520` | no body | 25.003 cm³ | 787 Hz | The 80 cm³ window at the 3 mm window wall: η_w at 3 mm, against V-a at 4 mm |

## Per body

### V-a

*Baseline: the 80 cm³ window.*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `617b869f0b10`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.005 cm³ against the model target 25.000 cm³ (+0.020 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.4 mm. Plastic 24.4 cm³.
- Stub: window sized for the 80 cm³ body. Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

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
| `voicing_hash` | pass | hash 617b869f0b10; recomputed from the record: 617b869f0b10 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 5.09 mm (at least 0.8 mm); windway roof 3.00 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |

Files: stl: `addon_out/stage1/V-a/V-a.stl`, air_capped_stl: `addon_out/stage1/V-a/V-a_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-a/V-a_air_fem.stl`, renders: `addon_renders/V-a/`, measurement_template: `addon_out/stage1/V-a/V-a_measurement.toml`, check_report: `addon_checks/V-a.md`.

### V-b

*Window shape at equal area; pairs with V-a.*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `c7b50fadd14b`. Window: Rounded rectangle 9.65 × 6.60 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 6.60 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.000 cm³ against the model target 25.000 cm³ (+0.000 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.5 mm. Plastic 24.2 cm³.
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
| `voicing_hash` | pass | hash c7b50fadd14b; recomputed from the record: c7b50fadd14b |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 6.601 mm, 62.80 mm² (record 9.650 × 6.601, 62.84); windway exit 1.200 × 6.601 mm, inlet 1.560 × 6.601 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end: not applicable to a rounded rectangle, which has one width (full width from 1.0 mm to 8.65 mm of the 9.65 mm length); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 24.3 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 5.08 mm (at least 0.8 mm); windway roof 3.00 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2321 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |

Files: stl: `addon_out/stage1/V-b/V-b.stl`, air_capped_stl: `addon_out/stage1/V-b/V-b_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-b/V-b_air_fem.stl`, renders: `addon_renders/V-b/`, measurement_template: `addon_out/stage1/V-b/V-b_measurement.toml`, check_report: `addon_checks/V-b.md`.

### V-d

*Proven-band reference: the 65 cm³ window.*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `2a71c31c2505`. Window: Teardrop 9.65 × 6.96 mm, 46.5 mm², wall 4.0 mm. Windway: exit 1.20 × 6.96 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.002 cm³ against the model target 25.000 cm³ (+0.010 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.5 mm. Plastic 24.2 cm³.
- Stub: window sized for the 65 cm³ body. Predicted pitch 709.5 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-d_air_capped.stl; holes and window closed): 4335 Hz = 3.10 × F6 on a 1.5 mm grid of 7420 cells (2 mm grid: 4320 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.805 + voicing pocket 0.195) = 25.0000 cm³ against the kernel's 25.0000 cm³: +0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0024 cm³ (+0.0095 %), air mesh 25.0000 cm³ (+0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0024 cm³ against the stub volume 25.0000 cm³ (+0.0095 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 709.5 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.24 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash 2a71c31c2505; recomputed from the record: 2a71c31c2505 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 6.959 mm, 46.47 mm² (record 9.650 × 6.959, 46.47); windway exit 1.200 × 6.959 mm, inlet 1.560 × 6.959 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.48 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 19.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 5.08 mm (at least 0.8 mm); windway roof 3.00 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2323 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |

Files: stl: `addon_out/stage1/V-d/V-d.stl`, air_capped_stl: `addon_out/stage1/V-d/V-d_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-d/V-d_air_fem.stl`, renders: `addon_renders/V-d/`, measurement_template: `addon_out/stage1/V-d/V-d_measurement.toml`, check_report: `addon_checks/V-d.md`.

### V-a0

*V-a with the labium offset 0 mm (labium height: brackets the −0.2 mm default) (optional stub of doc 04).*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `d1b6418b1844`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset +0.0 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.005 cm³ against the model target 25.000 cm³ (+0.020 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.4 mm. Plastic 24.5 cm³.
- Stub: window sized for the 80 cm³ body. Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-a0_air_capped.stl; holes and window closed): 4343 Hz = 3.11 × F6 on a 1.5 mm grid of 7423 cells (2 mm grid: 4330 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
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

Files: stl: `addon_out/stage1/V-a0/V-a0.stl`, air_capped_stl: `addon_out/stage1/V-a0/V-a0_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-a0/V-a0_air_fem.stl`, renders: `addon_renders/V-a0/`, measurement_template: `addon_out/stage1/V-a0/V-a0_measurement.toml`, check_report: `addon_checks/V-a0.md`.

### V-a35

*V-a with the labium offset −0.35 mm (labium height: brackets the −0.2 mm default) (optional stub of doc 04).*

- Result: **no unexpected failure**; 0 warnings.
- Voicing hash `7979d16c8d36`. Window: Teardrop 9.65 × 8.81 mm, 62.8 mm², wall 4.0 mm. Windway: exit 1.20 × 8.81 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.35 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.005 cm³ against the model target 25.000 cm³ (+0.020 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.4 mm. Plastic 24.3 cm³.
- Stub: window sized for the 80 cm³ body. Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-a35_air_capped.stl; holes and window closed): 4343 Hz = 3.11 × F6 on a 1.5 mm grid of 7423 cells (2 mm grid: 4330 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.765 + voicing pocket 0.235) = 25.0000 cm³ against the kernel's 25.0000 cm³: +0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0050 cm³ (+0.0199 %), air mesh 25.0000 cm³ (+0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0050 cm³ against the stub volume 25.0000 cm³ (+0.0199 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 787.1 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.21 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash 7979d16c8d36; recomputed from the record: 7979d16c8d36 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 8.806 mm, 62.83 mm² (record 9.650 × 8.806, 62.84); windway exit 1.200 × 8.806 mm, inlet 1.560 × 8.806 mm; labium 20.00°, edge 0.400 mm, offset -0.350 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 4.40 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | pass | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.7 mm; no tube inside the keep-out; outside: 0 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 5.24 mm (at least 0.8 mm); windway roof 2.85 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2322 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |

Files: stl: `addon_out/stage1/V-a35/V-a35.stl`, air_capped_stl: `addon_out/stage1/V-a35/V-a35_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-a35/V-a35_air_fem.stl`, renders: `addon_renders/V-a35/`, measurement_template: `addon_out/stage1/V-a35/V-a35_measurement.toml`, check_report: `addon_checks/V-a35.md`.

### V-a3

*The 80 cm³ window at the 3 mm window wall: η_w at 3 mm, against V-a at 4 mm (optional stub of doc 04).*

- Result: **UNEXPECTED FAILURES: voicing_keepouts**; 0 warnings.
- Voicing hash `36ebbc5bd520`. Window: Teardrop 9.65 × 7.93 mm, 54.4 mm², wall 3.0 mm. Windway: exit 1.20 × 7.93 mm, inlet height 1.56 mm, length 30 mm; W/h 8.04. Labium 20°, edge 0.4 mm, offset -0.2 mm.
- Volume: V0 25.00 cm³ (capped air). Measured on the STL: 25.003 cm³ against the model target 25.000 cm³ (+0.013 %). Cavity mesh 25.00 cm³ (0.00 cm³ of air in the holes, 0.00 cm³ of tube wall). Cavity spine length 53.5 mm. Plastic 23.8 cm³.
- Stub: window sized for the 80 cm³ body. Predicted pitch 787.1 Hz with the prior η_w 0.90 (a prediction, not a measurement).

| Check | Result | Message |
| --- | --- | --- |
| `wh_ratio` | pass | W/h = 8.04 (band 7..10) |
| `cavity_mode_computed` | pass | first cavity mode of the capped air mesh (V-a3_air_capped.stl; holes and window closed): 4337 Hz = 3.10 × F6 on a 1.5 mm grid of 7424 cells (2 mm grid: 4326 Hz). Rule: pass at 1.3 × F6 or more, needs_fem from 1 to 1.3, fail below 1. This is a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test |
| `volume_cavity_mesh` | pass | cavity mesh (loft 24.785 + voicing pocket 0.215) = 25.0000 cm³ against the kernel's 25.0000 cm³: +0.0000 % (limit 0.5 %) |
| `volume_capped_air` | pass | capped air measured on the final mesh 25.0033 cm³ (+0.0131 %), air mesh 25.0000 cm³ (+0.0000 %), against V0 25.0000 cm³ (limit 0.5 %) |
| `stub_volume` | pass | voicing stub: capped air measured on the final mesh 25.0033 cm³ against the stub volume 25.0000 cm³ (+0.0131 %, limit 0.5 %). The window is capped at its inner plane, as on a body |
| `stub_pitch_predicted` | info | predicted pitch of the stub, not measured: 787.1 Hz with the prior eta_w 0.90 at 27 °C internal air. The measured pitch gives eta_w · G_w for this voicing |
| `booleans` | pass | 5 Booleans, all manifold, each volume change as expected (largest deviation 0.25 % of the expected change) |
| `topology` | pass | manifold True, shells 1, boundary edges 0, non-manifold edges 0, zero-length edges 0, degenerate triangles 0, self-intersections 0, genus 1 (expected 1: 0 holes, the window and the windway) |
| `voicing_hash` | pass | hash 36ebbc5bd520; recomputed from the record: 36ebbc5bd520 |
| `voicing_dimensions` | pass | measured on the mesh: window 9.650 × 7.935 mm, 54.40 mm² (record 9.650 × 7.935, 54.40); windway exit 1.200 × 7.935 mm, inlet 1.560 × 7.935 mm; labium 20.00°, edge 0.400 mm, offset -0.200 mm |
| `voicing_orientation` | pass | windway exit faces the labium: True; broad end at the windway: True (widest point 3.97 mm from the exit, window 9.65 mm long); window opens outward: True |
| `voicing_keepouts` | FAIL | inside: 0 of 3000 sample points within 10 mm of the labium are plastic; free depth below the window 20.3 mm; no tube inside the keep-out; outside: 243 vertices above the 45° flare |
| `windway_floor_lip` | pass | plastic under the windway floor at the exit: 5.09 mm (at least 0.8 mm); windway roof 2.00 mm |
| `wall_thickness` | pass | plain wall, cavity to outside along the normal: minimum 4.000 mm, median 4.000 mm (target 4.0 mm, 2319 rays). Thinnest plastic of the finished body away from the voicing and the tubes: 4.00 mm |

Files: stl: `addon_out/stage1/V-a3/V-a3.stl`, air_capped_stl: `addon_out/stage1/V-a3/V-a3_air_capped.stl`, air_fem_stl: `addon_out/stage1/V-a3/V-a3_air_fem.stl`, renders: `addon_renders/V-a3/`, measurement_template: `addon_out/stage1/V-a3/V-a3_measurement.toml`, check_report: `addon_checks/V-a3.md`.

