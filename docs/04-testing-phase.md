# 04 · Testing phase: volume ladder and shape test

This plan tests how far the chamber volume of a 12-hole alto C can grow, and whether the cavity shape changes any of the parametric calculations. It uses plain generated test bodies only: a procedural cavity, a uniform wall, a generated voicing and generated round holes, with no styled exterior. It builds on the [unified plan](02-unified-plan.md), the [parametric findings](03-parametric-findings.md) and the [Miracle AO10-AC analysis](../Analizes_ocarinas/Miracle_M/Miracle_M.md).

**Budget:** about 1.75 kg of PLA for the core plan, 1.93 kg with a 10 % reserve for failed prints, against a target of 2 kg and a hard maximum of 4 kg. A stretch option brings it to about 2.8 kg.

## Why test larger volumes

Every alto C analysed so far holds **60–80 cm³** of air:

| Instrument | Air volume V0 | Source |
| --- | --- | --- |
| Repo baseline (37 mm² window) | 61.9 cm³ | [doc 03 §5](03-parametric-findings.md#5-baseline-design-12-hole-alto-c) |
| ECAN3 OOT (12-hole) | 63.8 cm³ | ECAN3 track (branch `ecan3-experimental`) |
| ECAN3 V0N3 (10-hole) | 67.9 cm³ | ECAN3 track |
| Miracle AO10-AC (12-hole) | about 65–75 cm³ | [Miracle §6.4](../Analizes_ocarinas/Miracle_M/Miracle_M.md#64-re-assessment-with-thicker-walls) |
| ECAN3 Eclipse (12-hole) | 77.0 cm³ | ECAN3 track |

The two reference cavity proportions proposed for the shape library hold 119 and 124 cm³ at their drawn size. Nothing above 80 cm³ is proven, and the kernel flags three problems as volume grows:

- **The window has to grow with volume.** η_w·G_w is proportional to V0 at a fixed lowest note. The window *length* is set by the jet and the pitch range (Heuer's #3 band), so the extra area has to come from width. With a medium window and a 4 mm wall, the broad end of the teardrop becomes a circle as wide as the window is long at about 88.6 cm³. Above that the window stays a teardrop and grows wider than it is long (the broad end becomes an ellipse), and the windway widens with it.
- **The holes grow too.** The largest top holes pass the finger-pad limit (about 10 mm for fingers, 12 mm for thumbs) on paper. Real instruments use top holes 20–40 % smaller than the lumped model predicts, so the real limit is unknown.
- **Longer chambers approach their first internal resonance.** That limits elongated shapes at large volume.

## Decisions this plan rests on

| # | Decision | Value |
| --- | --- | --- |
| D1 | Volume ladder | **65 / 80 / 95 / 125 cm³**. 110 cm³ is used as a prediction test; finer steps are an option. |
| D2 | Shapes | Three presets (P1 teardrop, P2 tailed gourd, P3 traditional transverse), compared at equal volume. The volume ladder runs on a separate compact **P0 control egg**, so that volume and shape effects do not mix. |
| D3 | Wall default | **4 mm** at the window and at the finger deck. Test bodies use 4 mm everywhere. |
| D4 | Voice rating | **Medium**, window length W = 9.65 mm (Heuer #3, fired) |
| D5 | Subholes | One per hand, as on the ECAN3 12-holes. **Decided 2026-11-15 ([06 §3.2 and §5](06-ergonomics-challenge.md#32-subholes-straight-forward-of-the-parent-710-mm)):** each subhole is a forward slide from its parent, along the normal of its own hand's pinky → index line, toward the fingertips. **sub_L from L_ring, 9.5 mm (toward the player); sub_R from R_middle, 7.5 mm (away from the player).** Parent and slide are preset values. The edge-gap rule may lengthen a slide up to 11 mm and never turns it around. The parent of sub_L is settled (doc 02 Q8: L ring). *Superseded:* +11 mm and +7 mm along the body's Y axis ([05](05-ergonomics.md), earlier the same day), and the C4 rule, which put sub_L on the far side (the finger had to curl back) and sub_R on the R index–R middle line. |
| D6 | Holes | Round. Each hole has its own diameter, solved per note. Small holes get round inward tubes. |
| D7 | Voicing | **Generated** from a few inputs by rule, never free-form. Each setting has a version hash; calibration constants are stored per hash. |
| D8 | End correction | Split in two. `k_window` = 0.80 stays fixed, because η_w = 0.9 is defined under it. `k_hole` has a prior of 1.0 (ECAN3 fit, 0.90–1.05) and is fitted from the test bodies. |
| D9 | Hand layout | Arch model with soft checks ([05 §3](05-ergonomics.md#3-soft-rules-proposed)): finger pitch, hand span, arch, hand tilt, index meeting point, subhole slides, rest space past the pinkies, hole tilt, thumbs. Warnings only. Defaults from the Miracle, which P1 and P2 already match in plan view. |
| D10 | Layout freeze | The hole layout of every shape is fixed before Stage 2 is printed. Stage 3 changes diameters only, never positions, because the fitted position factors belong to one layout. |

### Shapes

| Shape | Proportions | Length at 80 cm³ | Length at 125 cm³ | Role |
| --- | --- | --- | --- | --- |
| P0 control egg | 2.2 : 1.5 : 1 | 79 mm | 92 mm | Volume ladder. The lumped model is valid for it. |
| P1 teardrop | From proposed volume 1 | 111 mm | 129 mm | Shape test |
| P2 tailed gourd | From proposed volume 2 (Miracle-like) | 126 mm | 146 mm | Shape test; at 80 cm³ it is already at the cavity-mode limit (c/2L ≈ F6) |
| P3 traditional transverse | 3 : 1.6 : 1, bent spine (provisional until a traditional alto is measured) | 95 mm | 110 mm | Shape test |
| P4 ergonomic (proposed, doc 02 Q11) | Flat, asymmetric teardrop: fairly straight far edge, bulb and mouthpiece on the player's side, height about 0.5 of the width. Outer body shaped for the hands (doc 02 A13), about 145 mm long | about 115–120 mm (inside) | not planned | Hand comfort and long-chamber high notes on one print |

The P0 egg is too short for the Miracle hand span (about 104 mm pinky to pinky). It uses a compressed test layout and is played with tape over the holes; its renders and reports must say so (doc 02 Q12). Hand comfort is judged on P1–P4, which use the arch model. P3 at 80 cm³ is too short for the full span. Since the decision of 2026-11-15 its two hands overlap: each hand slides along its own line toward the other and the finger pitch is kept ([06 §3.5](06-ergonomics-challenge.md#35-shortening-a-layout-overlap-the-hands-do-not-squeeze-the-fingers)). The layout is no longer squeezed. P3 builds with no failure, and what is still missing shows as warnings (`ergo_rest_space` gives the missing length). P4 is the main hand test.

The C4 bodies (P1 118 mm, P2 133 mm, P3 102 mm outside) leave only 7–10 mm past the pinky holes at the ends of P1 and P3, and the pinky holes tilt up to 46°. The references leave 13–15 mm at the bulb and 23–33 mm at the tail ([05 §4](05-ergonomics.md#4-the-add-on-against-these-rules)).

## Generated sizes at each step

Defaults: P0 egg, medium window (W = 9.65 mm), 4 mm walls, η_w = 0.9, windway exit height 1.20 mm (W/h = 8.0 at every step). Holes are given at the k_hole = 1.0 nominal. They are **printed at their k_hole = 0.8 diameters** (see Stage 2).

| V0 | Window | Windway | sub_R | L_index | E6 thumb | P0 length | Window area / V0^(2/3) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 65 cm³ | Teardrop 9.65 × 7.0 mm, 47 mm² | 1.2 × 7.0 mm | 2.2 mm | 10.3 mm | 12.2 mm | 74 mm | 0.029 |
| 80 cm³ | Teardrop 9.65 × 8.8 mm, 63 mm² | 1.2 × 8.8 mm | 2.6 mm | 12.1 mm | 14.4 mm | 79 mm | 0.034 |
| 95 cm³ | Teardrop 9.65 × 11.1 mm, 81 mm² | 1.2 × 11.1 mm | 2.8 mm | 13.9 mm | 16.5 mm | 84 mm | 0.039 |
| 110 cm³ | Teardrop 9.65 × 14.7 mm, 101 mm² | 1.2 × 14.7 mm | 3.1 mm | 15.6 mm | 18.6 mm | 88 mm | 0.044 |
| 125 cm³ | Teardrop 9.65 × 18.6 mm, 123 mm² | 1.2 × 18.6 mm | 3.4 mm | 17.3 mm | 20.6 mm | 92 mm | 0.049 |

The analysed instruments span 0.024–0.041 in window area / V0^(2/3). The 110 and 125 cm³ steps are outside that range.

### What the k_hole split means for the holes

At 80 cm³, moving k_hole from 0.8 to 1.0 grows each hole by +0.1 mm (subholes) up to +1.7 mm (E6 thumb). Holes sized with 0.8 that really behave like 1.0 play progressively flat: −16 cents at B4 down to −109 cents at F6. A flat note can be fixed by reaming and a sharp one cannot, so first prints use the smaller (k 0.8) diameters.

For the window, k and η_w are not separable: the voicing stub measures their product. Changing `k_window` would not change the volume target as long as η_w is refitted under the same convention, so it stays fixed at 0.80.

## Stage 1 · Voicing stubs (about 204 g)

A stub is a small chamber (about 25 cm³) with the generated voicing and no holes. Its pitch, at a known volume, gives η_w·G_w directly. It also shows whether the voicing speaks and overblows cleanly.

| Stub | Window | Tests |
| --- | --- | --- |
| V-a | Teardrop 63 mm² (the 80 cm³ window) | Baseline |
| V-b | Rounded rectangle 63 mm² | Window shape at equal area; pairs with V-a |
| V-c | Teardrop 123.5 mm² (the 125 cm³ window), 18.6 mm windway | Whether the 125 cm³ voicing speaks at all (highest risk) |
| V-d | Teardrop 47 mm² (the 65 cm³ window) | Proven-band reference |
| V-a± (optional, +100 g) | V-a with labium offset ±0.2 mm | Low/high note balance |

**Gate 1:** each stub speaks cleanly across its range and overblows by at least a semitone without screeching. If V-c fails, the 125 cm³ body is skipped and its voicing is reworked first.

## Stage 2 · Round 1 bodies (about 807 g)

| Bodies | Purpose |
| --- | --- |
| P0 at 65, 80, 95, 125 cm³ | Volume ladder |
| P1, P2, P3 at 80 cm³ | Shape test, with the same voicing (same hash) as P0-80 |
| P4 at 80 cm³ (proposed, doc 02 Q11) | Hand comfort with the arch layout and rest areas; high notes of a 115–120 mm chamber. Same voicing hash. |
| Two more copies of P0-80 | Repeatability: three identical prints, as amendment A7 requires |

Every body has the full 12 round holes, sized for its own volume and printed at the k_hole = 0.8 diameters. **Before printing:** the layout fix (D5, D9) is built and its warnings are read; the layouts are then frozen (D10).

### Measurements per body

| Item | Method | Gives |
| --- | --- | --- |
| Printed air volume | Tape every hole, fill with water, weigh within a minute, then dry | Volume factor, measured directly instead of fitted |
| Printed hole diameters | Drill-bit shanks as gauges | Hole offset (printed minus designed) |
| 13 notes, A4 (all closed) to F6 (all open) | 3 takes each, 1 minute of warm-up, room temperature recorded. Play each note at the breath-curve pressure p = p₀·2^(α·n/12) read on a water manometer (start p₀ = 150 Pa, α = 1.2; [doc 03 §4](03-parametric-findings.md#4-jet-strouhal-and-the-breath-curve)). | Pitch per fingering |
| Speaking range | Lowest and highest pressure at which each note still sounds cleanly | Strouhal bands, overblowing margin |
| Spectrum per fingering (P1, P2, P4) | The recorded takes, checked for a resonance that stays fixed across fingerings | Whether a cavity mode reaches the top notes of a long chamber (doc 02 A12) |
| Hand check (P1–P4) | Play the scale untaped. Per hole: covered cleanly with a relaxed hand, yes or no; wrist straight, yes or no; free notes. Balance on the right thumb and the tail. | Hand-comfort verdict; which ergonomic warnings matter |

### The fit (no reaming needed)

- With V0 and the hole diameters measured, the all-closed note gives **η_w·G_w** for that voicing.
- In a linear fingering each later note opens exactly one more hole. So each note pair gives **that hole's effective conductance** on its own, with no reaming.
- Across all holes and bodies this gives the global **k_hole**, a **position factor per hole** (tail and bulb effects), and the **diameter each hole actually needs**.
- Reaming stays available as a rescue, but the plan does not depend on it.

### Gate 2

- One η_w per voicing and one k_hole explain all four P0 bodies within 30 cents rms.
- The three P0-80 copies agree within about ±8 cents (combined volume and window scatter ≤ 0.9 %, [doc 02](02-unified-plan.md#bottom-line)).
- **Shape verdict:** if P1–P3 differ from P0-80 by more than about 15 cents in a consistent pattern (whole-scale offset, top notes or tail holes), shape enters the calculations. The shapes are then retested at 125 cm³ (stretch option).
- **Round-hole verdict per ladder step:** a step fails if any fitted hole needs more than 10 mm (finger) or 12 mm (thumb).
- **Hand verdict (soft):** on at least one of P1–P4, every hole and subhole can be covered with straight wrists, and the instrument balances on the right thumb and the tail. That body's layout becomes the default for the design tools. A body that fails the hand check still counts for the acoustics.
- **Long-chamber verdict:** if P1, P2 or P4 shows a fixed resonance near E6/F6, or their top notes deviate from P0-80 in the "top notes" pattern, the A12 limit is tightened. Otherwise it stands.

## Stage 3 · Round 2 corrected prints (about 741 g)

| Bodies | Purpose |
| --- | --- |
| P0 at 65, 80, 95, 125 cm³ and P1–P3 at 80 cm³ (and P4 if printed), holes corrected from the round 1 fit, positions unchanged (D10) | Accuracy of the corrected design |
| **P0 at 110 cm³, sized from the fitted model only** | Prediction at a volume that was never printed |

**Gate 3:** every note on the corrected bodies within ±15 cents with no reaming, and P0-110 within about ±20 cents. Passing validates the full chain: cavity generator, voicing generator, hole solver and calibration constants.

## Filament budget

Masses assume solid 4 mm walls plus about 12 % for supports and a brim. Slicer infill should bring real numbers lower.

| Print | Mass each |
| --- | --- |
| P0 at 65 / 80 / 95 / 110 / 125 cm³ | 77 / 84 / 91 / 102 / 108 g |
| P1 / P2 / P3 at 80 cm³ | 91 / 97 / 91 g |
| P1 / P2 / P3 at 125 cm³ | 117 / 125 / 116 g |
| P4 at 80 cm³ (proposed) | about 115 g (estimate: a flatter chamber has more wall, plus solid rest areas; not built yet) |
| Voicing stub | 50–54 g |

| Stage | Mass |
| --- | --- |
| Stage 1 · voicing stubs | 204 g |
| Stage 2 · round 1 bodies | 807 g |
| Stage 3 · round 2 corrected + P0-110 | 741 g |
| **Core total** | **1,752 g** |
| **With 10 % reserve** | **1,927 g** |
| Stretch: labium offsets, plus P1–P3 at 125 cm³ in both rounds | +816 g, about **2.8 kg** total with reserve |

The stretch fits the 3 kg of filament on hand and stays under the 4 kg hard maximum.

**With P4 (doc 02 Q11):** P4 in both rounds adds about 230 g: core 1,982 g, **2,180 g with the reserve**, over the 2 kg target and under the 4 kg maximum. Replacing P3 with P4 instead costs about +48 g over both rounds: core 1,800 g, 1,980 g with the reserve, just under the 2 kg target.

If failed prints use up the reserve, trim in this order:

1. Two P0-80 copies instead of three (−84 g).
2. No round 2 for a ladder step that failed the round-hole verdict.
3. Drop stub V-d (−50 g).

## Before printing

**Build items needed first:**

- Cavity presets P0–P3, scaled to a target volume and anchored at the voicing port
- The voicing generator (rules above, version hash per setting)
- The hole solver and placer: kernel diameters, the Miracle-spaced template with ECAN3 subholes, round inward tubes for holes under 3 mm, and the compressed test layout for P0
- **The layout fix (checkpoint C4b of the add-on notes):** subhole slides (D5), the arch model and its soft checks (D9), rest space past the pinkies, labels on P0, hole names in the top-view renders; P4 and the separate outer body if doc 02 Q10 and Q11 are accepted
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
- The hand verdict: which layout the design tools use by default, and which ergonomic warnings matter in practice
- The long-chamber verdict: whether amendment A12's limit stands
