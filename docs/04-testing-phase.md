# 04 · Testing phase: volume ladder and shape test

This plan tests the chamber volume of a 12-hole alto C from 65 to 95 cm³, just past the proven band, and whether the cavity shape changes any of the parametric calculations. It uses plain generated test bodies only: a procedural cavity, a uniform wall, a generated voicing and generated round holes, with no styled exterior. It builds on the [unified plan](02-unified-plan.md), the [parametric findings](03-parametric-findings.md) and the [Miracle AO10-AC analysis](../Analizes_ocarinas/Miracle_M/Miracle_M.md).

**Budget:** about 1.47 kg of PLA for the core plan, 1.61 kg with a 10 % reserve for failed prints, against a target of 2 kg and a hard maximum of 4 kg. A stretch option brings it to about 2.4 kg.

> **Ladder change (2026-11-17).** The ladder was 65 / 80 / 95 / 125 cm³ with a 110 cm³ prediction body. It is now **65 / 80 / 95 cm³ with an 88 cm³ prediction body**. The 125 cm³ step came from the drawn size of the two proposed reference shapes (119 and 124 cm³), not from any analysed instrument. At 125 cm³ the generated window is 9.65 × 18.6 mm (nearly twice as wide as long), the windway slot is 15.5 : 1, the mouthpiece stub is 26.6 mm wide, and L_index and L_thumb print at 15.1 and 18.0 mm, far past the pad limits. The kernel already shows where the design breaks (holes at about 74 cm³ on 4 mm walls, window shape at 88.6 cm³ on a 4 mm window wall), so printing 125 cm³ adds cost but little information. Stub V-c (the 125 cm³ voicing) is dropped with it. A large exterior can come from solid outer mass instead of air, as the ECAN3 Eclipse does (77 cm³ of air in 125 cm³ of plastic). A **3 mm window wall** is now an option (see "Window wall option").

## Why test volumes above 80 cm³

Every alto C analysed so far holds **60–80 cm³** of air:

| Instrument | Air volume V0 | Source |
| --- | --- | --- |
| Repo baseline (37 mm² window) | 61.9 cm³ | [doc 03 §5](03-parametric-findings.md#5-baseline-design-12-hole-alto-c) |
| ECAN3 OOT (12-hole) | 63.8 cm³ | ECAN3 track (branch `ecan3-experimental`) |
| ECAN3 V0N3 (10-hole) | 67.9 cm³ | ECAN3 track |
| Miracle AO10-AC (12-hole) | about 65–75 cm³ | [Miracle §6.4](../Analizes_ocarinas/Miracle_M/Miracle_M.md#64-re-assessment-with-thicker-walls) |
| ECAN3 Eclipse (12-hole) | 77.0 cm³ | ECAN3 track |

The two reference cavity proportions proposed for the shape library hold 119 and 124 cm³ at their drawn size; the tests scale them to 80 cm³. Nothing above 80 cm³ is proven, and the kernel flags three problems as volume grows:

- **The window has to grow with volume.** η_w·G_w is proportional to V0 at a fixed lowest note. The window *length* is set by the jet and the pitch range (Heuer's #3 band), so the extra area has to come from width. With a medium window and a 4 mm wall, the broad end of the teardrop becomes a circle as wide as the window is long at about 88.6 cm³ (96.9 cm³ with the 3 mm window wall option). Above that the window stays a teardrop and grows wider than it is long (the broad end becomes an ellipse), and the windway widens with it.
- **The holes grow too.** The largest top holes pass the finger-pad limit (about 10 mm for fingers, 12 mm for thumbs) on paper. Real instruments use top holes 20–40 % smaller than the lumped model predicts, so the real limit is unknown.
- **Longer chambers approach their first internal resonance.** That limits elongated shapes at large volume.

## Decisions this plan rests on

| # | Decision | Value |
| --- | --- | --- |
| D1 | Volume ladder | **65 / 80 / 95 cm³**. 88 cm³ is the prediction test (round 2 only); finer steps are an option. 110 and 125 cm³ were dropped (2026-11-17). |
| D2 | Shapes | Three presets (P1 teardrop, P2 tailed gourd, P3 traditional transverse), compared at equal volume. The volume ladder runs on a separate compact **P0 control egg**, so that volume and shape effects do not mix. |
| D3 | Wall default | **4 mm** at the window and at the finger deck. Test bodies use 4 mm everywhere. **Option:** 3 mm at the window only (`window_wall_options_mm`), for a narrower window at the same V0. |
| D4 | Voice rating | **Medium**, window length W = 9.65 mm (Heuer #3, fired) |
| D5 | Subholes | One per hand, as on the ECAN3 12-holes: **sub_L between L_ring and L_middle, sub_R between R_index and R_middle** |
| D6 | Holes | Round. Each hole has its own diameter, solved per note. Small holes get round inward tubes. |
| D7 | Voicing | **Generated** from a few inputs by rule, never free-form. Each setting has a version hash; calibration constants are stored per hash. Labium offset **−0.2 mm** by default (edge below the jet centre, Heuer Videos #3, #6, #8; 2026-11-17); coupons 0 and −0.4 mm; never positive. |
| D8 | End correction | Split in two. `k_window` = 0.80 stays fixed, because η_w = 0.9 is defined under it. `k_hole` has a prior of 1.0 (ECAN3 fit, 0.90–1.05) and is fitted from the test bodies. |

### Shapes

| Shape | Proportions | Length at 80 cm³ | Length at 95 cm³ | Role |
| --- | --- | --- | --- | --- |
| P0 control egg | 2.2 : 1.5 : 1 | 79 mm | 84 mm | Volume ladder. The lumped model is valid for it. |
| P1 teardrop | From proposed volume 1 | 111 mm | 118 mm | Shape test |
| P2 tailed gourd | From proposed volume 2 (Miracle-like) | 126 mm | 134 mm | Shape test; at 80 cm³ it is already at the cavity-mode limit (c/2L ≈ F6) |
| P3 traditional transverse | 3 : 1.6 : 1, bent spine (provisional until a traditional alto is measured) | 95 mm | 101 mm | Shape test |

The P0 egg is too short for the Miracle hand span (about 104 mm pinky to pinky). It uses a compressed test layout and is played with tape over the holes. Hand comfort is judged on P1–P3, which use the real layout template.

## Generated sizes at each step

Defaults: P0 egg, medium window (W = 9.65 mm), 4 mm walls, η_w = 0.9, windway exit height 1.20 mm (W/h = 8.0 at every step). Holes are given at the k_hole = 1.0 nominal. They are **printed at their k_hole = 0.8 diameters** (see Stage 2).

| V0 | Window | Windway | sub_R | L_index | E6 thumb | P0 length | Window area / V0^(2/3) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 65 cm³ | Teardrop 9.65 × 7.0 mm, 47 mm² | 1.2 × 7.0 mm | 2.2 mm | 10.3 mm | 12.2 mm | 74 mm | 0.029 |
| 80 cm³ | Teardrop 9.65 × 8.8 mm, 63 mm² | 1.2 × 8.8 mm | 2.6 mm | 12.1 mm | 14.4 mm | 79 mm | 0.034 |
| 88 cm³ (prediction) | Teardrop 9.65 × 9.6 mm, 72 mm² | 1.2 × 9.6 mm | 2.7 mm | 13.1 mm | 15.5 mm | 82 mm | 0.037 |
| 95 cm³ | Teardrop 9.65 × 11.1 mm, 81 mm² | 1.2 × 11.1 mm | 2.8 mm | 13.9 mm | 16.5 mm | 84 mm | 0.039 |

Every step is inside the 0.024–0.041 range of window area / V0^(2/3) that the analysed instruments span. With the default 4 mm window wall, the 95 cm³ window is the only one wider than long (11.1 mm on a 9.65 mm length).

Lengths at 95 cm³ in the shape table scale from the 80 cm³ lengths as V0^(1/3).

### Window wall option (3 mm)

The window area is solved from V0 through η_w·G_w, and G_w = A / (t + k·d_eq). A thinner wall gives more conductance per mm², so the same V0 needs a smaller window. The holes do not change: they depend on η_w·G_w, which V0 and A4 fix.

| V0 | Window, 4 mm wall (default) | Window, 3 mm wall (option) | Window area / V0^(2/3), 3 mm |
| --- | --- | --- | --- |
| 65 cm³ | 9.65 × 7.0 mm, 46 mm² | 9.65 × 6.0 mm, 40 mm² | 0.025 |
| 80 cm³ | 9.65 × 8.8 mm, 63 mm² | 9.65 × 7.9 mm, 54 mm² | 0.029 |
| 88 cm³ | 9.65 × 9.6 mm, 72 mm² | 9.65 × 8.8 mm, 63 mm² | 0.032 |
| 95 cm³ | 9.65 × **11.1** mm, 81 mm² (wider than long) | 9.65 × **9.5** mm, 71 mm² (a normal teardrop) | 0.034 |
| Teardrop turns wider than long at | 88.6 cm³ | 96.9 cm³ | |

How to use it:

- The wall is a voicing input, so a 3 mm window has its own hash and its own η_w. The fitter handles that already (one η_w per hash).
- η_w may depend on the window wall, and no data separates the two yet. The measured ECAN3 windows (2.1–2.4 mm) give 0.86–0.89, and the Miracle fits 0.9 if its window wall is about 4 mm. (The LES study's 0.48 / 0.63 / 0.78 are one measurement read under three assumed walls, 0 / 1.5 / 3 mm, because the study does not state its wall; they are not a trend.) So do not mix walls inside the P0 ladder: the P0-88 prediction would then rest on an unknown η_w(wall). Build the whole ladder at one wall, or add the 3 mm body as an extra (P0-95-w3).
- Before a 3 mm body, print the optional stub V-a3 (Stage 1): it measures η_w at 3 mm directly.
- Commands: `python kernel/sizing.py --wall 3`; add-on `headless.py -- body --preset P0 --v0 95 --window-wall 3 --out ...` (body id `P0-95-w3`), or "Wall at the window" in the Build Test Body operator.

### What the k_hole split means for the holes

At 80 cm³, moving k_hole from 0.8 to 1.0 grows each hole by +0.1 mm (subholes) up to +1.7 mm (E6 thumb). Holes sized with 0.8 that really behave like 1.0 play progressively flat: −16 cents at B4 down to −109 cents at F6. A flat note can be fixed by reaming and a sharp one cannot, so first prints use the smaller (k 0.8) diameters.

For the window, k and η_w are not separable: the voicing stub measures their product. Changing `k_window` would not change the volume target as long as η_w is refitted under the same convention, so it stays fixed at 0.80.

## Stage 1 · Voicing stubs (about 150 g)

A stub is a small chamber (about 25 cm³) with the generated voicing and no holes. Its pitch, at a known volume, gives η_w·G_w directly. It also shows whether the voicing speaks and overblows cleanly.

| Stub | Window | Tests |
| --- | --- | --- |
| V-a | Teardrop 63 mm² (the 80 cm³ window) | Baseline |
| V-b | Rounded rectangle 63 mm² | Window shape at equal area; pairs with V-a |
| V-d | Teardrop 47 mm² (the 65 cm³ window) | Proven-band reference |
| V-a0, V-a4 (optional, +100 g) | V-a with labium offset 0 and −0.4 mm (V-a itself uses the −0.2 mm default) | Labium height: Heuer puts the lip below the jet centre; brackets the default |
| V-a3 (optional, +50 g) | Teardrop 54 mm² (the 80 cm³ window at the 3 mm wall option) | η_w at the 3 mm wall, against V-a at 4 mm; needed before any 3 mm body |

**Gate 1:** each stub speaks cleanly across its range and overblows by at least a semitone without screeching. Stub V-c (the 125 cm³ window) was dropped with the 125 cm³ step.

## Stage 2 · Round 1 bodies (about 699 g)

| Bodies | Purpose |
| --- | --- |
| P0 at 65, 80, 95 cm³ | Volume ladder |
| P1, P2, P3 at 80 cm³ | Shape test, with the same voicing (same hash) as P0-80 |
| Two more copies of P0-80 | Repeatability: three identical prints, as amendment A7 requires |

Every body has the full 12 round holes, sized for its own volume and printed at the k_hole = 0.8 diameters.

### Measurements per body

| Item | Method | Gives |
| --- | --- | --- |
| Printed air volume | Tape every hole, fill with water, weigh within a minute, then dry | Volume factor, measured directly instead of fitted |
| Printed hole diameters | Drill-bit shanks as gauges | Hole offset (printed minus designed) |
| 13 notes, A4 (all closed) to F6 (all open) | 3 takes each, 1 minute of warm-up, room temperature recorded. Play each note at the breath-curve pressure p = p₀·2^(α·n/12) read on a water manometer (start p₀ = 150 Pa, α = 1.2; [doc 03 §4](03-parametric-findings.md#4-jet-strouhal-and-the-breath-curve)). | Pitch per fingering |
| Speaking range | Lowest and highest pressure at which each note still sounds cleanly | Strouhal bands, overblowing margin |

### The fit (no reaming needed)

- With V0 and the hole diameters measured, the all-closed note gives **η_w·G_w** for that voicing.
- In a linear fingering each later note opens exactly one more hole. So each note pair gives **that hole's effective conductance** on its own, with no reaming.
- Across all holes and bodies this gives the global **k_hole**, a **position factor per hole** (tail and bulb effects), and the **diameter each hole actually needs**.
- Reaming stays available as a rescue, but the plan does not depend on it.

### Gate 2

- One η_w per voicing and one k_hole explain all three P0 ladder bodies within 30 cents rms. (With three steps instead of four, the profile estimate of k_hole is less tight: about ±7.5 % on the synthetic round-1 files, against ±4.4 % when the ladder reached 125 cm³. The rule that lets it drive allows 15 %.)
- The three P0-80 copies agree within about ±8 cents (combined volume and window scatter ≤ 0.9 %, [doc 02](02-unified-plan.md#bottom-line)).
- **Shape verdict:** if P1–P3 differ from P0-80 by more than about 15 cents in a consistent pattern (whole-scale offset, top notes or tail holes), shape enters the calculations. The shapes are then retested at 95 cm³ (stretch option).
- **Round-hole verdict per ladder step:** a step fails if any fitted hole needs more than 10 mm (finger) or 12 mm (thumb).

## Stage 3 · Round 2 corrected prints (about 619 g)

| Bodies | Purpose |
| --- | --- |
| P0 at 65, 80, 95 cm³ and P1–P3 at 80 cm³, holes corrected from the round 1 fit | Accuracy of the corrected design |
| **P0 at 88 cm³, sized from the fitted model only** | Prediction at a volume that was never printed (between two printed steps, just below the 88.6 cm³ where the 4 mm window turns into a circle) |

**Gate 3:** every note on the corrected bodies within ±15 cents with no reaming, and P0-88 within about ±20 cents. Passing validates the full chain: cavity generator, voicing generator, hole solver and calibration constants.

## Filament budget

Masses assume solid 4 mm walls plus about 12 % for supports and a brim. Slicer infill should bring real numbers lower.

| Print | Mass each |
| --- | --- |
| P0 at 65 / 80 / 88 / 95 cm³ | 77 / 84 / 88 / 91 g (88: interpolated) |
| P1 / P2 / P3 at 80 cm³ | 91 / 97 / 91 g |
| P1 / P2 / P3 at 95 cm³ | 100 / 106 / 99 g (interpolated between the 80 and 125 cm³ estimates) |
| Voicing stub | 50–54 g |

| Stage | Mass |
| --- | --- |
| Stage 1 · voicing stubs (V-a, V-b, V-d) | 150 g |
| Stage 2 · round 1 bodies | 699 g |
| Stage 3 · round 2 corrected + P0-88 | 619 g |
| **Core total** | **1,468 g** (was 1,752 g with the 125 cm³ step) |
| **With 10 % reserve** | **1,615 g** |
| Stretch: labium offsets, plus P1–P3 at 95 cm³ in both rounds | +710 g, about **2.4 kg** total with reserve |
| Option: stub V-a3 (+50 g) and P0-95-w3 in both rounds (+182 g) | about +230 g |

The stretch and the option together fit the 3 kg of filament on hand and stays under the 4 kg hard maximum.

If failed prints use up the reserve, trim in this order:

1. Two P0-80 copies instead of three (−84 g).
2. No round 2 for a ladder step that failed the round-hole verdict.
3. Drop stub V-d (−50 g).

## Before printing

**Build items needed first:**

- Cavity presets P0–P3, scaled to a target volume and anchored at the voicing port
- The voicing generator (rules above, version hash per setting)
- The hole solver and placer: kernel diameters, the Miracle-spaced template with ECAN3 subholes, round inward tubes for holes under 3 mm, and the compressed test layout for P0
- A kernel fitter: per-hole effective conductance from successive notes, k_hole, position factors, volume factor and hole offset. This extends the Phase 0 fingerprint fitter.
- Split `k_end` into `k_window` and `k_hole` in [`params/alto_c_12hole.toml`](../params/alto_c_12hole.toml)

**Measuring kit:**

- Pitch recording: a Python script (`numpy` + `sounddevice`, FFT or autocorrelation), or a tuner app
- Water manometer: clear tubing, a ruler and a tee into a mouthpiece tube
- A drill-bit set to use as hole gauges
- A scale reading to 0.1 g for the water fill

## Outputs

- `eta_w` per voicing hash; `k_hole`; `hole_offset_mm`; `volume_factor`
- Position factors by region (bulb, centre, tail)
- The shape verdict: whether P1–P3 need their own constants
- The largest volume that passes the round-hole verdict, which sets the upper end of the volume range the design tools offer
