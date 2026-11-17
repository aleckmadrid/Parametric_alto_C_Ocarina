# 08 — The Stage 2 body library, body by body

Written on 2026-11-16, after [07](07-windway-and-body-shape.md). The owner wants the seed body of doc 07 in Stage 2 and asked for each present body to be assessed: keep, stash, modify or discard.

This document is an assessment with a recommendation. **Nothing in the presets, the stage lists or the tests was changed.** Section 6 lists what a decision would change.

**Owner, 2026-11-16: the recommendation of section 1 is saved as the Stage 2 plan for now.** That is set A with the round seed: P0 unchanged, the seed added, P2 and P1 kept as acoustic bodies, P3 stashed, the old P4 proposal dropped. It is provisional and may be revisited before the first print. **Built on 2026-11-17, on the owner's go-ahead:** the seed is preset `P4` ("P4 seed"), `P4-80` takes the place of `P3-80` in the Stage 2 and Stage 3 lists, and P3 stays as a preset that is in no stage list. `P4-80` is the test body `P2-80-seed` to the last digit (same 2 warnings, spine 132.05 mm, first cavity mode 1.36 × F6). The name `P4` was my choice, to keep the P-number scheme; say so if it should have its own name. P1's label was left as it is (section 7, item 4).

## 1. Recommendation

| Body | Verdict | In one line |
| --- | --- | --- |
| **P0** control egg, 65 / 80 / 95 / 125 cm³ and two copies of P0-80 | **Keep, unchanged** | It carries the volume ladder, the repeatability test and every fitted constant. Nothing else can replace it |
| **Seed** (new, the values of `P2-80-seed`) | **Add**, as the hand body and the long-chamber body | Smooth, slender, 2 warnings, first cavity mode 1.36 × F6. It takes the place doc 04 kept for P4 |
| **P2** tailed gourd | **Keep, unchanged, for acoustics only** | The waist the owner dislikes is what makes it worth printing: with the seed it forms a pair of equal length, with and without a waist |
| **P1** teardrop | **Keep for acoustics, or stash if prints are scarce** | The middle step between the egg and the seed. Its hand layout cannot pass: it is 20 mm too short |
| **P3** traditional transverse | **Stash** | The smallest step away from the control, proportions that match no reference, and doc 04 itself calls it provisional |
| **P4** as doc 04 describes it (flat, asymmetric, shaped outer body) | **Drop the proposal** | The seed does its two jobs with the cavity formula as it is |

*Stash* means: the preset stays in `cavity_presets.toml` and still builds, but it leaves the Stage 2 and Stage 3 lists.

The recommended Stage 2 is then **nine bodies, as now**: P0 at 65, 80, 95 and 125 cm³, two more P0-80, P1, P2 and the seed, all at 80 cm³ where not stated. Solid PLA 541 g against 534 g now.

## 2. What Stage 2 asks of its bodies

From [04](04-testing-phase.md), Gate 2:

| Job | What it needs | Bodies that can do it |
| --- | --- | --- |
| **Volume ladder and constants** | A compact body for which the lumped model holds, at four volumes | P0 only |
| **Repeatability** | Three identical prints | P0-80 and its two copies |
| **Shape verdict**: does the shape of the chamber move the notes by more than about 15 cents in a pattern? | Bodies at 80 cm³ with the same voicing as P0-80, that differ from the egg and from each other in a known way | P1, P2, P3, the seed |
| **Hand verdict**: is there one body on which every hole can be covered with straight wrists? | One body whose hand layout has a fair chance | the seed; P2 less so |
| **Long-chamber verdict**: does a cavity mode reach the top notes? | The longest chambers | the seed (132 mm), P2 (125 mm) |

A shape body earns its print by what it adds to the shape verdict. The variables in play are the length of the chamber, how narrow the tail is, a waist, the roundness of the section and a bend.

## 3. The bodies as built at 80 cm³

| | P0 | P3 | P1 | P2 | Seed |
| --- | --- | --- | --- | --- | --- |
| Cavity spine | 78 mm | 94 mm | 110 mm | 125 mm | 132 mm |
| Outer length × width × thickness | – | 102 × 58 × 39 | 118 × 57 × 42 | 133 × 59 × 42 | 140 × 49 × 39 |
| Outer width / length | – | 0.57 | 0.48 | 0.44 | 0.35 |
| Nearest references | – | none (all lie between 0.35 and 0.49) | Miracle 0.48, ECAN3 V0N3 0.46 | ECAN3 Ocarina of Time 0.40, V0N3 0.46 | Songbird 0.35, Spencer 0.35 |
| Outline | ellipsoid | ellipsoid, spine bent 20° | convex teardrop | bulb, waist, tail: 2.0 mm concave in plan, 1.2 mm on the deck | convex seed, pointed tail |
| First cavity mode (computed) | 2.10 × F6 | 1.76 | 1.63 | 1.40 | 1.36 |
| Warnings | taped test body | 6 | 4 | 5 | 2 |
| Land past the L / R pinky hole | – | 10.0 / 7.8 mm | 5.2 / 4.8 mm | 9.4 / 12.4 mm | 15.2 / 11.6 mm |
| Largest hole lean toward an end | – | 31° | 38° | 29° | 19° |
| Hands | taped | overlapped 12 mm each | template | template, centre 23 mm | template, centre 20 mm |
| Mouthpiece station | – | 0.35 | 0.37 | 0.31 | 0.36 |
| Solid PLA | 55 g | 59 g | 61 g | 65 g | 66 g |

Sources: `addon_checks/*.json`, [addon_checks/stage2.md](../addon_checks/stage2.md), [07 §3.4–3.6](07-windway-and-body-shape.md). The limits are 10 mm of land and 20° of lean.

## 4. Body by body

### P0 control egg: keep

- **Role.** The volume ladder (65 to 125 cm³), the three repeatability prints, and the prediction body of Stage 3 (110 cm³). η_w·G_w, k_hole, the volume factor and the hole offset all come from it.
- **What doc 07 changes.** Nothing. It is played with tape over the holes and was never a hand body. Its mouthpiece station does not matter for the same reason.
- **Verdict: keep, unchanged.** Six of the nine prints are P0, and none can be saved without weakening a gate.

### Seed: add

- **What it is.** The 7-station model fitted to the outline of the Songbird Alto C (the Spencer outline gives the same body within 3 mm), with a 4 mm wall, 80 cm³, port at 0.35 of the spine, layout centre 20 mm from the port. It uses the cavity formula, the hole template and the limits as they are.
- **What it does better than every present body.** No waist. Land past both pinky holes. No hole leans more than 19° toward an end. The left hand span is inside its range. Two warnings, both shared with P2.
- **What it costs.**
  - The first cavity mode is 1.36 × F6, the lowest of the set and 0.06 above the pass line. The stretch option of doc 04 (shapes at 125 cm³) would put it near 1.17.
  - The tail is narrow: 12.4 × 8.2 mm of cavity at the R pinky hole (P2: 14.0 × 9.2 mm). Holes there will need more area than the lumped model gives. That is what the position factors are for, and it is the pattern the Miracle analysis found.
  - Its hole layout is the Miracle template, not the layout of the instruments its outline comes from. Those have their two rows 36–42 mm apart (07 §3.7). One variable at a time: the shape first.
- **Round or flatter.** Both were built:

| | Seed (round) | Seed, flatter |
| --- | --- | --- |
| Cavity height / width | 0.76 | 0.64 |
| Outer length × width × thickness | 140 × 49 × 39 mm | 148 × 52 × 36 mm |
| First cavity mode | **1.36 × F6, pass** | **1.29 × F6, needs_fem** |
| Warnings | 2 | 2 (the same two) |
| Land past the L / R pinky hole | 15.2 / 11.6 mm | 17.8 / 14.8 mm |
| Largest lean toward an end | 19° | 15° |
| Cavity at the R pinky hole | 12.4 × 8.2 mm | 15.7 × 9.1 mm |
| Solid PLA | 66 g | 69 g |

  At equal volume a flatter body is a longer body. The flatter one is a little kinder to the hands and falls just under the cavity-mode line. Reports: [P2-80-seed](../addon_checks/P2-80-seed.md), [P2-80-seedflat](../addon_checks/P2-80-seedflat.md).
- **Verdict: add the round one.** It is the shape of both ceramic references, and it keeps the cavity mode on the passing side.

### P2 tailed gourd: keep, for acoustics

- **Role until now.** The Miracle-like shape, and since doc 06 the best hand body of the set.
- **What doc 07 found.** A waist on both sides of the plan and a dip along the deck, between the two hands; no ceramic reference has either. The L pinky hole still leans 29°. The seed is better on every hand measure.
- **Why it still earns a print.** P2 and the seed are nearly the same length (125 and 132 mm) and share the voicing. They differ in one thing: a bulb with a waist against a smooth taper. If the shape of the chamber enters the calculations at all, this pair shows whether the waist is the cause. P2 is also the only body whose reference instrument has a full hole analysis (Miracle §6.3: tail holes 1.2 to 2.1 times too big for the lumped model). Its fitted position factors can be read against that.
- **Why not modify it.** Smoothing the waist gives a shorter seed. The contrast would be gone, and the Miracle link with it.
- **Verdict: keep, unchanged. The hand verdict moves to the seed.** If one shape body has to go beyond P3, see P1.

### P1 teardrop: keep for acoustics, or stash

- **Role.** A plain teardrop of medium length.
- **Hands.** Land of 5.2 and 4.8 mm past the pinky holes, half of the tightest reference, and pinky holes that lean 38° and 30°. Doc 06 §3.11 already found that it is about 20 mm too short and that sliding the layout does not help. It will not pass the hand check, and nothing short of lengthening it would change that.
- **Acoustics.** With the egg and the seed it makes a series of three smooth shapes: 78, 110 and 132 mm of spine. That series says whether the effect of length is gradual. Without P1 the same question has two points.
- **Why not modify it.** A longer, slimmer P1 is the seed.
- **Verdict: keep as an acoustic body, with no hand check expected of it.** It is the first to stash if prints run short: the egg, P2 and the seed still answer the shape verdict without it.

### P3 traditional transverse: stash

- **Role.** A 3 : 1.6 : 1 ellipsoid on a spine bent by 20°.
- **Against the references.** Its outer width / length is 0.57. Every measured instrument lies between 0.35 and 0.49. Doc 04 marks it "provisional until a traditional alto is measured", and none has been.
- **Hands.** Six warnings with the hands overlapped by 12 mm each, more than any other body. The overlap itself is past its limit (−23.3 mm along, limit −22).
- **Acoustics.** It is the smallest step away from the control: an ellipsoid of 94 mm beside an ellipsoid of 78 mm. Its own variable is the bend, and 20° on a body this fat moves the ends very little.
- **Verdict: stash.** Keep the preset. Bring it back when a traditional alto has been measured and the preset can be fitted to it, as the seed was fitted to the Songbird. Its second build, `P3-80-ov6`, goes with it.

### P4 as proposed in doc 04: drop the proposal

Doc 04 sketched P4 as a flat, asymmetric teardrop about 145 mm long with an outer body shaped for the hands, to test hand comfort and the high notes of a long chamber. It was never built. The seed tests both, at 140 mm, with no new geometry code. What P4 had and the seed has not: a flat section (about 0.5), a straight far edge, and solid rest areas. The flatter seed above is the first of these, and it costs cavity-mode margin. The other two need an outer body, which stays an open question (doc 02 Q10).

## 5. Three possible sets

| Set | Shape bodies at 80 cm³ | Bodies in Stage 2 | Solid PLA, Stage 2 | With 12 % for supports and a brim |
| --- | --- | --- | --- | --- |
| Now | P1, P2, P3 | 9 | 534 g | 598 g |
| **A, recommended** | P1, P2, seed | 9 | 541 g | 606 g |
| B, lean | P2, seed | 8 | 480 g | 538 g |
| C, everything | P1, P2, P3, seed | 10 | 600 g | 672 g |

The doc 04 budget for Stage 2 is 807 g, so all three fit. Stage 3 prints the same shape bodies once more, corrected.

## 6. What a decision would change

**Done on 2026-11-17** for set A:

| Where | Change |
| --- | --- |
| `ocarina_addon/presets/cavity_presets.toml` | A new preset block `[P4]` with the seed values. P3 stays |
| `ocarina_addon/stages.py`, `tools/geometry_check.py`, `tools/geometry_check_body.py`, the operator's preset menu | `STAGE2_BODIES` and the Stage 3 list: P3 out, P4 in; the doc 04 masses |
| `tests/test_stage_reports.py` and any other test that names the bodies | The expected body lists |
| [04](04-testing-phase.md), [02](02-unified-plan.md) Q11 | The shapes table, the Stage 2 and Stage 3 tables, the P4 row, the filament budget (Stage 2 815 g, Stage 3 749 g by doc 04's method) |
| `prompts/addon-v1-notes.md`, README | Status, and questions 14 and 15 closed |
| Rebuild | `tools/geometry_check.py -- cavities` and `-- body P4 80 --renders`, the two stage commands, `tools/run_tests.py`. The kernel's synthetic test set still calls its third shape P3; it is a label there and was left alone |

The layout of every shape is frozen by the first Stage 2 print (doc 04 D10). The seed's layout values (port 0.35, centre 20 mm) are part of that freeze.

## 7. Open choices for the owner

1. **The set:** A, B or C, or another mix. *Saved for now, 2026-11-16: set A.*
2. **The name of the seed:** `P4`, which reuses the slot doc 04 kept open, or a name of its own. *Built as `P4` on 2026-11-17; not chosen by the owner.*
3. **Round or flatter.** The recommendation is round. *Saved for now, 2026-11-16: round.*
4. **P1's label.** If it stays: keep its hand layout and expect the warnings, or mark it an acoustic body in the reports, as P0 is marked a taped body.

## 8. Limits

- Every number is a desk check on a generated body. Nothing was printed.
- The cavity mode is computed with all holes closed; the pass line at 1.3 × F6 is a guess (doc 06 §3.10). The seed's margin of 0.06 is inside what a real measurement could move.
- "What a body adds to the shape verdict" is my reading of how the bodies differ. No acoustic model in the repository predicts the size of a shape effect; Stage 2 exists to measure it.
- The seed comes from two ceramic instruments measured on photos (doc 07 §7).
