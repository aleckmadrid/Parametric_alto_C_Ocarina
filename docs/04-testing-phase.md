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
- **The holes grow too.** The largest top holes pass the finger-pad limit (about 10 mm for fingers, 12 mm for thumbs) on paper. Real instruments use top holes 20–40 % smaller than the lumped model predicts, so the real limit is unknown. *Since 2026-11-18 (Asian fingering order, [09 §6.1–6.2](09-kernel-and-decisions-challenged.md)) the two largest holes are the thumbs', as on every reference: at 80 cm³ the only hole over its limit at the print diameters is the right thumb's (12.7 mm against 12), and no finger hole is over 10 mm below 95 cm³. The earlier statement that the holes break at about 74 cm³ came from the old order, which gave the D6 hole to the left index finger.*
- **Longer chambers approach their first internal resonance.** That limits elongated shapes at large volume.

## Decisions this plan rests on

| # | Decision | Value |
| --- | --- | --- |
| D1 | Volume ladder | **65 / 80 / 95 cm³**. 88 cm³ is the prediction test (round 2 only); finer steps are an option. 110 and 125 cm³ were dropped (2026-11-17). |
| D2 | Shapes | Three presets (P1 teardrop, P2 tailed gourd, P4 seed), compared at equal volume. **Changed 2026-11-17 ([08](08-stage2-body-library.md), saved by the owner as the plan for now):** the seed takes the place of P3 traditional transverse, which is stashed (the preset stays and still builds). The volume ladder runs on a separate compact **P0 control egg**, so that volume and shape effects do not mix. |
| D3 | Wall default | **4 mm** at the window and at the finger deck. Test bodies use 4 mm everywhere. **Option:** 3 mm at the window only (`window_wall_options_mm`), for a narrower window at the same V0. |
| D4 | Voice rating | **Medium**, window length W = 9.65 mm (Heuer #3, fired) |
| D5 | Subholes | One per hand, as on the ECAN3 12-holes. **Decided 2026-11-15 ([06 §3.2 and §5](06-ergonomics-challenge.md#32-subholes-straight-forward-of-the-parent-710-mm)):** each subhole is a forward slide from its parent, along the normal of its own hand's pinky → index line, toward the fingertips. **sub_L from L_ring, 10 mm (toward the player); sub_R from R_middle, 7.5 mm (away from the player).** The left slide was 9.5 mm until 2026-11-18 (owner decision 1 of that day, [decisions](../Analizes_ocarinas/Decisions_2026-11-18/decisions.md) section 1): at 10 mm the edge gap to L_ring is 4.76 mm at the print diameters and 4.28 mm at k_hole 1.0, and it also holds with the round-2 diameters. Parent and slide are preset values. The edge-gap rule may lengthen a slide up to 11 mm and never turns it around. The parent of sub_L is settled (doc 02 Q8: L ring). *Superseded:* +11 mm and +7 mm along the body's Y axis ([05](05-ergonomics.md), earlier the same day), and the C4 rule, which put sub_L on the far side (the finger had to curl back) and sub_R on the R index–R middle line. |
| D6 | Holes | Round. Each hole has its own diameter, solved per note. Small holes get round inward tubes. |
| D7 | Voicing | **Generated** from a few inputs by rule, never free-form. Each setting has a version hash; calibration constants are stored per hash. Labium offset **−0.2 mm** by default (edge below the jet centre, Heuer Videos #3, #6, #8; 2026-11-17); coupons 0 and −0.35 mm; never positive. **Since 2026-11-18 (owner decisions 2 to 6, rule version 2):** the windway is 3.0 mm high at the mouth end (was 1.56 mm) and 1.20 mm at the exit, and the rule also fixes the **build** of the voicing, which is part of the hash: the ellipse window cut (3 mm per side, shelf 40°), a neck that stands 15° off the body with the pipe 10° lower inside it, and a blended pocket behind the labium. See "The build of the voicing" below. |
| D8 | End correction | Split in two. `k_window` = 0.80 stays fixed, because η_w = 0.9 is defined under it. `k_hole` has a prior of 1.0 (ECAN3 fit, 0.90–1.05) and is fitted from the test bodies. |
| D9 | Hand layout | Arch model with soft checks ([05 §3](05-ergonomics.md#3-soft-rules-proposed)): finger pitch, hand span, arch, hand tilt, index meeting point, subhole slides, rest space past the pinkies, hole tilt, thumbs. Warnings only. Defaults from the Miracle, which P1 and P2 already match in plan view. |
| D10 | Layout freeze | The hole layout of every shape is fixed before Stage 2 is printed. Stage 3 changes diameters only, never positions, because the fitted position factors belong to one layout. |

### Shapes

| Shape | Proportions | Length at 80 cm³ | Length at 95 cm³ | Role |
| --- | --- | --- | --- | --- |
| P0 control egg | 2.2 : 1.5 : 1 | 79 mm | 84 mm | Volume ladder. The lumped model is valid for it. |
| P1 teardrop | From proposed volume 1 | 111 mm | 118 mm | Shape test |
| P2 tailed gourd | From proposed volume 2 (Miracle-like) | 126 mm | 134 mm | Shape test; at 80 cm³ it is already at the cavity-mode limit (c/2L ≈ F6) |
| P3 traditional transverse | 3 : 1.6 : 1, bent spine (provisional until a traditional alto is measured) | 95 mm | 101 mm | Stashed since 2026-11-17 ([08](08-stage2-body-library.md)): not printed. Was: shape test |
| P4 seed ([08](08-stage2-body-library.md)) | Smooth, slender seed: the outline of a ceramic 12-hole alto C with a 4 mm wall taken off. Convex everywhere; cavity height / width 0.76; outside 140 × 49 × 39 mm at 80 cm³ | 133 mm | 141 mm | Shape test, hand comfort, and the high notes of a long chamber (first cavity mode 1.36 × F6 at 80 cm³). The older proposal for this slot (a flat, asymmetric body with an outer skin shaped for the hands, doc 02 Q11) was dropped on 2026-11-17 |

The P0 egg is too short for the Miracle hand span (about 104 mm pinky to pinky). It uses a compressed test layout and is played with tape over the holes; its renders and reports must say so (doc 02 Q12). Hand comfort is judged on P1–P4, which use the arch model. P3 at 80 cm³ is too short for the full span. Since the decision of 2026-11-15 its two hands overlap: each hand slides along its own line toward the other and the finger pitch is kept ([06 §3.5](06-ergonomics-challenge.md#35-shortening-a-layout-overlap-the-hands-do-not-squeeze-the-fingers)). The layout is no longer squeezed. P3 builds with no failure, and what is still missing shows as warnings (`ergo_rest_space` gives the missing length). P4, the seed, is the main hand test. P3 is stashed since 2026-11-17 and is not printed ([08](08-stage2-body-library.md)).

The C4 bodies (P1 118 mm, P2 133 mm, P3 102 mm outside) leave only 7–10 mm past the pinky holes at the ends of P1 and P3, and the pinky holes tilt up to 46°. The references leave 13–15 mm at the bulb and 23–33 mm at the tail ([05 §4](05-ergonomics.md#4-the-add-on-against-these-rules)).

## Generated sizes at each step

Defaults: P0 egg, medium window (W = 9.65 mm), 4 mm walls, η_w = 0.9, windway exit height 1.20 mm (W/h = 8.0 at every step), 3.0 mm at the mouth end. Holes are given at the k_hole = 1.0 nominal. They are **printed at their k_hole = 0.8 diameters** (see Stage 2).

| V0 | Window | Windway | sub_R | D6 thumb (L) | E6 thumb (R) | P0 length | Window area / V0^(2/3) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 65 cm³ | Teardrop 9.65 × 7.0 mm, 47 mm² | 1.2 × 7.0 mm | 2.2 mm | 10.3 mm | 12.2 mm | 74 mm | 0.029 |
| 80 cm³ | Teardrop 9.65 × 8.8 mm, 63 mm² | 1.2 × 8.8 mm | 2.6 mm | 12.1 mm | 14.4 mm | 79 mm | 0.034 |
| 88 cm³ (prediction) | Teardrop 9.65 × 9.6 mm, 72 mm² | 1.2 × 9.6 mm | 2.7 mm | 13.1 mm | 15.5 mm | 82 mm | 0.037 |
| 95 cm³ | Teardrop 9.65 × 11.1 mm, 81 mm² | 1.2 × 11.1 mm | 2.8 mm | 13.9 mm | 16.5 mm | 84 mm | 0.039 |

The two hole columns are the holes that open D6 and E6, the largest of the scale. Since 2026-11-18 they belong to the left and the right thumb (Asian fingering order, owner decision; [09 §6.1](09-kernel-and-decisions-challenged.md)); before, the same two diameters were listed as L_index and the E6 thumb. The numbers did not change.

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

### The build of the voicing (owner decisions of 2026-11-18 and 2026-11-19)

**Rule version 3 since 2026-11-19.** After two rounds of trial necks against his own sample and two bulb-shaped reference models, the owner chose trial `tb-d1` ([Neck_volume.md](../Analizes_ocarinas/Neck_volume/Neck_volume.md), sections 7 and 8): the wall over the windway exit is cut square, the voicing is turned toward the bottom of the body so that the mouthpiece points back at the player, and the neck is a cone with a thin roof over the pipe. The table below shows the values of today; the values of 2026-11-18 are in its third column.

The window, the lip, the ramp and the windway exit are the same numbers as before. What changed is how the window is opened to the outside and what the mouthpiece looks like. Pictures and measured effects of every option: [decisions.md](../Analizes_ocarinas/Decisions_2026-11-18/decisions.md).

| Build field (`[voicing_rules]`) | Value | On 2026-11-18 (rule version 2) | Plain build |
| --- | --- | --- | --- |
| `window_cut` | `ellipse`: one smooth dish from the window outline to an ellipse at the outer face | the same | `fan` |
| `cut_widen_mm`, `shelf_angle_deg` | 3 mm per side; 0°: the wall over the exit is cut square | 3 mm, shelf 40° ("P3") | – |
| `stub_style`, `stub_pitch_deg` | `cone`, 8°: the outer flank of the neck lies a thin roof over the pipe (2.2 mm at the mouth end, 1.7 mm at the exit) and its deck side is straight | `neck`, standing 15° | box, level |
| `windway_pitch_deg` | +8° against the window face, turned about the labium edge | +5°, 10° lower than the neck | 0° |
| `port_angle_deg` (a value of the body, in the cavity presets) | 30° around the body from the bottom toward the player; the stub S0 keeps 45° | 45° | – |
| `pocket_blend_radius_mm` | 12 mm: the pocket ceiling falls away behind the labium on this radius until it meets the chamber wall, instead of ending in a step. The reach depends on the chamber: 3 to 5 mm on a flat one, up to about 10 mm on a stub | the same | 0 |
| `windway_taper_ratio` | 2.5: 3.0 mm at the mouth end, 1.20 mm at the exit | the same | 1.3 (1.56 mm) |

- **The build is hashed** whenever it differs from the plain build, so a stub and a body share an η_w only when they share the build. A plain voicing keeps the hash it would have had before.
- **The outside keep-out is still the 45° flare.** The check now measures the flare itself: no plastic inside the cone that opens at 45° from the window rim at the outer face. Until 2026-11-18 it counted everything above the outer face, which was the same thing while the stub ended there. The neck of 2026-11-18 rose behind the window and stood 41° steep seen from the rim. The cone neck does not stand above the outer face at the back edge of the window at all; behind it the neck rises at about 11°.
- **Not measured, and why stub V-af exists:** the jet now reaches the edge heading 8° into the chamber (5° on 2026-11-18), the throat is a dish and no longer a 4 mm tube, and the wall over the exit is a thin roof cut square. Each of these can move η_w and the break pressure. V-a (this build) against V-af (the plain build, same window) measures the sum before eight bodies are printed with it.

### What the k_hole split means for the holes

At 80 cm³, moving k_hole from 0.8 to 1.0 grows each hole by +0.1 mm (subholes) up to +1.7 mm (E6 thumb). Holes sized with 0.8 that really behave like 1.0 play progressively flat: −16 cents at B4 down to −109 cents at F6. A flat note can be fixed by reaming and a sharp one cannot, so first prints use the smaller (k 0.8) diameters.

For the window, k and η_w are not separable: the voicing stub measures their product. Changing `k_window` would not change the volume target as long as η_w is refitted under the same convention, so it stays fixed at 0.80.

## Stage 1 · Voicing stubs (about 200 g)

A stub is a small chamber (about 25 cm³) with the generated voicing and no holes. Its pitch, at a known volume, gives η_w·G_w directly. It also shows whether the voicing speaks and overblows cleanly.

Record on every stub: the pitch (3 takes) at the manometer pressure, the room temperature, and the **break pressure**: blow harder until the note jumps or screeches and read the manometer just before. This is Heuer's window check ("blow that low note away … not too soft, not too hard", Videos #2, #4, #8). It compares the voicings (V-a against V-a0 / V-a35, V-a3, V-b) on one number. The stub measurement file (`ocarina-stub-measurement-v1`, written blank by the Stage 1 command) has the optional field `p_break_pa` for it.

| Stub | Window | Tests |
| --- | --- | --- |
| V-a | Teardrop 63 mm² (the 80 cm³ window), the build of the bodies | Baseline |
| V-af (since 2026-11-18) | The same window with the plain build: fan cut, level windway, box stub | What the ellipse cut, the tilt and the neck are worth, and whether they speak; pairs with V-a. Its hash is carried by no body |
| V-b | Rounded rectangle 63 mm², plain build | Window shape at equal area; pairs with V-af (the ellipse cut is made for the teardrop, so both stubs of this pair have the plain build) |
| V-d | Teardrop 47 mm² (the 65 cm³ window) | Proven-band reference |
| V-a0, V-a35 (optional, +100 g) | V-a with labium offset 0 and −0.35 mm (V-a itself uses the −0.2 mm default) | Labium height: Heuer puts the lip below the jet centre; brackets the default |
| V-a3 (optional, +50 g) | Teardrop 54 mm² (the 80 cm³ window at the 3 mm wall option) | η_w at the 3 mm wall, against V-a at 4 mm; needed before any 3 mm body |

**Gate 1:** each stub speaks cleanly across its range and overblows by at least a semitone without screeching. Stub V-c (the 125 cm³ window) was dropped with the 125 cm³ step.

## Stage 2 · Round 1 bodies (about 707 g)

| Bodies | Purpose |
| --- | --- |
| P0 at 65, 80, 95 cm³ | Volume ladder |
| P1, P2 and P4 (seed) at 80 cm³ | Shape test, with the same voicing (same hash) as P0-80. P4 is also the hand body and, with P2, the long-chamber body |
| P3 at 80 cm³ | Not printed: stashed since 2026-11-17 ([08](08-stage2-body-library.md)) |
| Two more copies of P0-80 | Repeatability: three identical prints, as amendment A7 requires |

Every body has the full 12 round holes, sized for its own volume and printed at the k_hole = 0.8 diameters. **Before printing:** the layout fix (D5, D9) is built and its warnings are read; the layouts are then frozen (D10).

### Measurements per body

| Item | Method | Gives |
| --- | --- | --- |
| Printed air volume | Tape every hole, fill with water, weigh within a minute, then dry | Volume factor, measured directly instead of fitted |
| Printed hole diameters | Drill-bit shanks as gauges | Hole offset (printed minus designed) |
| 13 notes, A4 (all closed) to F6 (all open) | 3 takes each, 1 minute of warm-up, room temperature recorded. Play each note at the breath-curve pressure p = p₀·2^(α·n/12) read on a water manometer (start p₀ = 150 Pa, α = 1.2; [doc 03 §4](03-parametric-findings.md#4-jet-strouhal-and-the-breath-curve)). | Pitch per fingering |
| Speaking range | Lowest and highest pressure at which each note still sounds cleanly. The highest is the **break pressure**, `p_break_pa` in the measurement file: optional per note, wanted at least for A4 | Strouhal bands, overblowing margin, Heuer's window check |
| Spectrum per fingering (P1, P2, P4) | The recorded takes, checked for a resonance that stays fixed across fingerings | Whether a cavity mode reaches the top notes of a long chamber (doc 02 A12) |
| Hand check (P1, P2, P4) | Play the scale untaped. Per hole: covered cleanly with a relaxed hand, yes or no; wrist straight, yes or no; free notes. Balance on the right thumb and the tail. | Hand-comfort verdict; which ergonomic warnings matter |

### The fit (no reaming needed)

- With V0 and the hole diameters measured, the all-closed note gives **η_w·G_w** for that voicing.
- In a linear fingering each later note opens exactly one more hole. So each note pair gives **that hole's effective conductance** on its own, with no reaming.
- Across all holes and bodies this gives the global **k_hole**, a **position factor per hole** (tail and bulb effects), and the **diameter each hole actually needs**.
- Reaming stays available as a rescue, but the plan does not depend on it.

### Gate 2

- One η_w per voicing and one k_hole explain all three P0 ladder bodies within 30 cents rms. (With three steps instead of four, the profile estimate of k_hole is less tight: about ±7.5 % on the synthetic round-1 files, against ±4.4 % when the ladder reached 125 cm³. The rule that lets it drive allows 15 %.)
- The three P0-80 copies agree within about ±8 cents (combined volume and window scatter ≤ 0.9 %, [doc 02](02-unified-plan.md#bottom-line)).
- **Shape verdict:** if P1, P2 or P4 differ from P0-80 by more than about 15 cents in a consistent pattern (whole-scale offset, top notes or tail holes), shape enters the calculations. The shapes are then retested at 95 cm³ (stretch option).
- **Round-hole verdict per ladder step:** a step fails if any fitted hole needs more than 10 mm (finger) or 12 mm (thumb).
- **Hand verdict (soft):** on at least one of P1, P2 and P4, every hole and subhole can be covered with straight wrists, and the instrument balances on the right thumb and the tail. That body's layout becomes the default for the design tools. A body that fails the hand check still counts for the acoustics.
- **Long-chamber verdict:** if P1, P2 or P4 shows a fixed resonance near E6/F6, or their top notes deviate from P0-80 in the "top notes" pattern, the A12 limit is tightened. Otherwise it stands.

## Stage 3 · Round 2 corrected prints (about 627 g)

| Bodies | Purpose |
| --- | --- |
| P0 at 65, 80, 95 cm³ and P1, P2 and P4 at 80 cm³, holes corrected from the round 1 fit, positions unchanged (D10) | Accuracy of the corrected design |
| **P0 at 88 cm³, sized from the fitted model only** | Prediction at a volume that was never printed (between two printed steps, just below the 88.6 cm³ where the 4 mm window turns into a circle) |

**Gate 3:** every note on the corrected bodies within ±15 cents with no reaming, and P0-88 within about ±20 cents. Passing validates the full chain: cavity generator, voicing generator, hole solver and calibration constants.

## Filament budget

Masses assume solid 4 mm walls plus about 12 % for supports and a brim. Slicer infill should bring real numbers lower.

| Print | Mass each |
| --- | --- |
| P0 at 65 / 80 / 88 / 95 cm³ | 77 / 84 / 88 / 91 g (88: interpolated) |
| P1 / P2 / P3 at 80 cm³ | 91 / 97 / 91 g |
| P1 / P2 / P3 at 95 cm³ | 100 / 106 / 99 g (interpolated between the 80 and 125 cm³ estimates) |
| P4 seed at 80 cm³ | about 99 g (estimate: P2's 97 g scaled by the generated plastic, 66 g against 65 g) |
| Voicing stub | 50–54 g |

| Stage | Mass |
| --- | --- |
| Stage 1 · voicing stubs (V-a, V-af, V-b, V-d) | 200 g (150 g before stub V-af, 2026-11-18) |
| Stage 2 · round 1 bodies | 707 g |
| Stage 3 · round 2 corrected + P0-88 | 627 g |
| **Core total** | **1,534 g** (was 1,768 g with the 125 cm³ step) |
| **With 10 % reserve** | **1,687 g** |
| Stretch: labium offsets, plus P1–P3 at 95 cm³ in both rounds | +710 g, about **2.4 kg** total with reserve |
| Option: stub V-a3 (+50 g) and P0-95-w3 in both rounds (+182 g) | about +230 g |

The stretch and the option together fit the 3 kg of filament on hand and stays under the 4 kg hard maximum.

**Since 2026-11-17 ([08](08-stage2-body-library.md)):** P4, the seed, takes P3's place in both rounds, which adds about 16 g; the totals above include it. The stretch line still lists P1–P3 at 95 cm³ and was not reworked for P4. The older P4 proposal (a flat body with solid rest areas, about 115 g) was dropped.

If failed prints use up the reserve, trim in this order:

1. Two P0-80 copies instead of three (−84 g).
2. No round 2 for a ladder step that failed the round-hole verdict.
3. Drop stub V-d (−50 g).

## Before printing

**Build items needed first** (status 2026-11-18; details in [`prompts/addon-v1-notes.md`](../prompts/addon-v1-notes.md)):

- Cavity presets P0–P4, scaled to a target volume and anchored at the voicing port. **Done** (C3, `351407c`; P4 seed since doc 08).
- The voicing generator (rules above, version hash per setting). **Done** (C1, C2b; labium default −0.2 mm since `0e9743a`).
- The hole solver and placer: kernel diameters, the Miracle-spaced template with ECAN3 subholes, round inward tubes for holes under 3 mm, and the compressed test layout for P0. **Done** (C1, C4 `20b09ae`).
- **The layout fix (checkpoint C4b of the add-on notes):** subhole slides (D5), the arch model and its soft checks (D9), rest space past the pinkies, labels on P0, hole names in the top-view renders; P4 and the separate outer body if doc 02 Q10 and Q11 are accepted
- A kernel fitter: per-hole effective conductance from successive notes, k_hole, position factors, volume factor and hole offset. **Done** (C2, C2b); the measurement file also takes the break pressure (`p_break_pa`).
- Split `k_end` into `k_window` and `k_hole` in [`params/alto_c_12hole.toml`](../params/alto_c_12hole.toml). **Done** (C1).
- Stage commands for Stages 1–3, the voicing stubs with their measurement file, the test suites and the extension package. **Done** (C5 `751d8fd`, C6 `6da438b`); regenerated at the current rules on 2026-11-17 after the merge with `main`.
- The owner's decisions of 2026-11-18 (slide 10 mm, ellipse cut, 3 mm mouth end, standing neck, the build in the hash, stub V-af). **Done**, and the stages were regenerated; the angle of the pipe inside the neck waited for the owner's confirmation. *(Superseded on 2026-11-19 by rule version 3: the cone neck, the pipe at +8°, the roof cut square and the port at 30°; the stages were regenerated again.)*
- **Still to do:** the 3 mm window wall is not built by the add-on yet (stub V-a3 fails its outside keep-out, by 2° since the neck stands; notes, open problem 22). The labium coupons are stubs V-a0 and V-a35; `build_body` has no labium-offset argument for a full body.

**Measuring kit:**

- Pitch recording: a Python script (`numpy` + `sounddevice`, FFT or autocorrelation), or a tuner app
- Water manometer: clear tubing, a ruler and a tee into a mouthpiece tube
- A drill-bit set to use as hole gauges
- A scale reading to 0.1 g for the water fill

## Outputs

- `eta_w` per voicing hash; `k_hole`; `hole_offset_mm`; `volume_factor`
- Position factors by region (bulb, centre, tail)
- The shape verdict: whether P1, P2 and P4 need their own constants
- The largest volume that passes the round-hole verdict, which sets the upper end of the volume range the design tools offer
- The hand verdict: which layout the design tools use by default, and which ergonomic warnings matter in practice
- The long-chamber verdict: whether amendment A12's limit stands
