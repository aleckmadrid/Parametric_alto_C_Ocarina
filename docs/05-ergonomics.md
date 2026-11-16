# 05 — Hand ergonomics of the 12-hole alto C: hole layout and body shape

Written on 2026-11-15, after the C4 renders showed odd hole placement and odd chamber shapes.

> **Challenged the same day in [06](06-ergonomics-challenge.md).** Read it before acting on sections 2, 3, 5 and 7 below. In short: the Miracle's "left subhole" is a right-index subhole, two CAD references with a true scale were not used here, several limits of section 3 would warn on the references themselves, and the chamber-length conflict of section 5 is smaller than stated. The P2 column of section 4 shows the C4 layout; the P2 preset has since moved 7 mm toward the tail (06 §3.11).

The owner's guidelines for this review:

- No absolutes. A design choice that is called unergonomic (a straight, inline mouthpiece, for example) can still be a valid aesthetic choice. The rules below are **soft**: they produce warnings and scores, never a refused build.
- The scope is the **12-hole alto C**. The holes should follow the arch of the fingers with reasonable spacing.
- An alto suits most adult hands, so finger size is not a design input. The pad limits that exist stay as they are; no per-finger hole-size limits are added.

Sources: [references/ocarina-making-resources.md](../references/ocarina-making-resources.md) (Pure Ocarinas articles, the book site, a maker's comment on the limits of the model). Measurements: [Analizes_ocarinas/Ergonomic_reference_12hole](../Analizes_ocarinas/Ergonomic_reference_12hole/Ergonomic_reference_12hole.md) (the shared photos) and [Analizes_ocarinas/Miracle_M](../Analizes_ocarinas/Miracle_M/Miracle_M.md). The comparison script measures the Miracle, the photos and the add-on bodies in one frame: [measure_output.md](../Analizes_ocarinas/Ergonomic_reference_12hole/measure_output.md).

## 1. What the sources say

No free source gives hole spacing in millimetres. The guidance is qualitative, and the numbers have to come from instruments that play well.

- **How the hands hold a transverse ocarina** (Pure Ocarinas). The right palm faces away from the player, so the right fingers reach over from the player's side and their tips point to the far side. The left palm faces the player, so the left fingers reach over from the far side and their tips point toward the player. Wrists straight, fingers gently curved, fingers not touching each other.
- **Subholes** are closed by straightening the finger and sliding the tip forward. So a subhole sits **in the direction its finger points**, beyond its parent hole.
- **Rest areas.** Leave room past the outermost holes. On high notes the right pinky rests on the tail beside its hole, and the left index on the bump near the mouthpiece. Holes pushed against the ends, and very round bodies, are named signs of a poor design.
- **Flat areas** around the holes keep the fingers from sliding off a curved surface.
- **Balance** comes first: the instrument should balance on the line from the right thumb hole to the tail.
- **Position hardly affects pitch** (Pure Ocarinas, the book site), so the holes can go where the hands want them. A maker's comment adds a caution: the distance from the voicing and the chamber shape *do* move the pitch somewhat. In this project that effect goes into the fitted position factor ψ per hole name. **ψ belongs to one layout, so the layout must be fixed before the Stage 2 bodies are printed.**

## 2. What well-played instruments share

Three references were measured in one frame (player's view; x along the body from the bulb, y toward the player): the Miracle AO10-AC (measured in mm) and two photo sets of a well-rated design (scaled to the Miracle's pinky-to-pinky span, because the photos have no scale).

| Feature | Range over the references | Miracle |
| --- | --- | --- |
| Neighbouring finger holes, centre to centre | 14–20 mm | 17–19 mm |
| One hand, pinky to index | 48–60 mm | 51–52 mm |
| Tilt of each hand's pinky → index line against the body | 4°–23° | 16° |
| Ring and middle holes off that line, toward the fingertips (the arch) | +1.4 to +5.7 mm | +3.7 to +5.7 mm |
| The two index holes: across the body / along it | 23–31 mm / −6 to +10 mm | 23.5 / 5.2 mm |
| Left subhole: parent; offset along the left fingertips | L ring (photos) or L index (Miracle); +9 to +15 mm | L index, +15 mm |
| Right subhole: parent; offset along the right fingertips | R middle on all; +6 to +9 mm | R middle, +6 mm |
| Pinky hole to the end of the body, bulb / tail | 13–15 / 23–33 mm | 13 / 33 mm |
| Finger holes from the far edge (all but the right index) | 10–16 mm | 11–26 mm |

In words: each hand's holes lie on a gentle arc that bulges the way the fingertips point. The two arcs meet in the middle, with the left index near the far edge and the right index near the player. Each subhole sits a short slide forward from its parent. There is room past both pinkies, more at the tail.

## 3. Soft rules (proposed)

Each rule gives a status `ok` or `warn`, never `fail`. The defaults come from section 2. Every limit is a parameter, so a body made for looks can be built anyway, with the warning shown.

| Check | Measure | `ok` range (default) | Why |
| --- | --- | --- | --- |
| `ergo_finger_pitch` | centre distance of neighbouring finger holes of one hand | 14–20 mm | References; fingers do not touch |
| `ergo_hand_span` | pinky → index of one hand | 44–60 mm | References |
| `ergo_arch` | ring and middle offset from the pinky → index line, toward the fingertips | +1 to +7 mm (warn if negative: a zigzag) | The arch of the fingers |
| `ergo_hand_tilt` | angle of each hand's pinky → index line | 0°–25°, left index end to the far side, right index end to the player | References; Pure Ocarinas (hand slightly angled) |
| `ergo_index_meet` | index holes across / along the body | 18–32 mm across, within ±10 mm along | References |
| `ergo_subholes` | subhole offset from its parent, along that hand's fingertips | +5 to +16 mm along, centre distance 6–16 mm | Closed by straightening and sliding forward |
| `ergo_rest_space` | pinky hole centre to the outer end of the body | at least 12 mm at the bulb, 20 mm at the tail | Pinky rest on high notes; holes not against the ends |
| `ergo_hole_tilt` | angle between a finger hole's axis and the deck's vertical | up to 25° ok, warn above 30° | Flat areas so the fingers do not slide off (our limit; no source gives a number) |
| `ergo_thumbs` | thumb holes along the body | right thumb between R index and R middle, left thumb under the left hand | Balance on the line right thumb → tail; Miracle |

Not proposed as checks: per-finger hole sizes (owner: not relevant at alto size), the mouthpiece angle (an aesthetic choice; the report states it), and timbre or feel (not measurable here).

## 4. The add-on against these rules

Measured on the built bodies at 80 cm³ (`measure_output.md`).

| Item | P1-80 | P2-80 | P3-80 | P0-80 | Verdict |
| --- | --- | --- | --- | --- | --- |
| Finger pitch | 15.6–17.5 mm | 15.2–17.8 | 12.9–16.6 | 11.1–16.5 | P1 and P2 ok. P3 is squeezed (open problem 8). P0 is too tight for fingers. |
| Arch (ring, middle) | +3.2…+4.3 mm | +3.2…+4.2 | +3.0…+5.2 | −5.7…+9.4 | P1–P3 follow the arch. **P0 zigzags** (negative = against the fingers). |
| Hand tilt (L / R) | 16° / −14° | 16.5° / −14° | 14° / −23° | 38° / −28° | P1–P3 ok; P0 out of range. |
| Index holes across | 20.5 mm | 20.4 | 22.4 | 21.7 | Ok, at the low end. |
| **Left subhole** along the fingers | **−3.9 mm** (from L middle) | −3.9 | −4.4 | +2.0 | **Wrong side.** The rule puts it toward the far side, so the left finger must curl back to close it. The references put it 9–15 mm toward the player. |
| **Right subhole** along the fingers | **+0.8 mm** (from R middle) | +0.8 | +0.5 | +3.0 | On the line between R index and R middle, not a slide forward from R middle. The references: +6 to +9 mm. |
| **Rest space**, bulb / tail | **10.0 / 7.2 mm** | 8.4 / 23.6 | 6.9 / 7.3 | 13.2 / 11.4 | **The pinky holes sit at the ends** of P1 and P3. References: 13–15 / 23–33 mm. |
| **Hole tilt**, worst finger hole | **L pinky 38°**, R pinky 32° | L pinky 40° | **R pinky 46°**, L pinky 41° | L pinky 32° | The pinky holes slide down the curved ends. |
| Outer length | 118 mm | 133 mm | 102 mm | 86 mm | References: about 143–150 mm. |

So in plan view the Miracle template is already reproduced well on P1 and P2: pitch, tilt, arch and the index stagger are all in range. What makes the renders look wrong:

1. **The subholes are on the wrong side.** `holes_layout._template_nominal` puts both subholes 6 mm off the finger line on the far side. That is right for the right hand (only it is too close to the R index–R middle line) and wrong for the left hand.
2. **The bodies are too short for the hand span.** The Miracle span is wrapped by arc length onto 102–133 mm bodies, so the pinky holes land on the steep ends, with no rest space.
3. **The bodies are round where the fingers go.** The cavity sections are 0.66–0.70 as high as they are wide, and the 4 mm wall copies the cavity. The deck under the holes curves away, so even the index holes tilt 17–23°.
4. **P0 is not laid out for hands at all.** Its compressed test layout zigzags so the 78 mm egg keeps its gaps. That was intended (P0 is played with tape over the holes), but it reads as a hand layout on the renders.
5. **Hole sizes look random.** Diameters run from 3.1 to 12.7 mm. The Miracle's top holes run from 2.6 to 7.1 mm. This is acoustics, not layout: the lumped model asks for larger top holes than real instruments use (Miracle analysis §6.3), and Stage 2 will measure it.

## 5. The body shape: where ergonomics and acoustics pull apart

The hands need a deck about 140–150 mm long: a 104 mm pinky span plus 13 mm at the bulb and 25 mm or more at the tail. The holes must open into the chamber, so the chamber must reach from just before the left pinky hole to just past the right pinky hole: **about 115–120 mm inside**. The rest areas past the pinkies need not be chamber.

The project's cavity-mode rule (doc 03 §8) says: no chamber longer than c/(2L) = 1.3 × F6 (95 mm inside) without an FEM check, and never beyond 124 mm. Every reference instrument is longer than 95 mm, and the Miracle (150 mm outside) plays to F6. The rule uses c/(2L), which doc 03 itself calls the lowest estimate: a tapered chamber's first mode is higher. So the rule is stricter than real instruments need. It is right that a long chamber needs a check, but a 115–125 mm teardrop is the normal case for a 12-hole alto C, not an exception.

Proposed direction:

1. **Separate the outer body from the chamber.** The chamber is sized for the acoustics, about 115–125 mm long, flatter in section (height about 0.45–0.55 of the width) so 80 cm³ fits. The outer body is shaped for the hands: about 140–150 mm long, solid rest areas past the pinky holes, a flatter deck under the hole band, flat lands around the holes (open problem 10). The add-on already has a place for this: `body.OUTER_MESH_HOOK`. A thicker wall makes the chimney longer under some holes; the kernel takes the chimney per hole, so the sizing must read it from the geometry.
2. **An asymmetric planform** as an option for the chamber presets, as on the Miracle and the photos: a fairly straight far edge, the bulb and the mouthpiece on the player's side, the tail tapering. The holes then sit in a band 10–16 mm from the far edge, where the surface is nearly flat.
3. **The cavity-mode check stays**, but for the chambers in this range its result becomes `needs_fem` (FEM on the exported air mesh, or a measurement in Stage 2) instead of `fail`. P1 at 80 cm³ (111 mm) is already `needs_fem`.
4. **Add one ergonomic body to Stage 2** (for example "P4": the flat, asymmetric chamber in a 145 mm outer body with the corrected layout). It tests hand comfort and the long-chamber high notes on one print. It also gives ψ for the layout the project will actually use.

## 6. Proposed changes to the add-on (a checkpoint before C5)

These are now in the plan: amendments A11–A14 and questions Q8–Q12 in [doc 02](02-unified-plan.md#amendments-to-the-original-plan), decisions D5 (revised), D9 and D10 and the P4 body in [doc 04](04-testing-phase.md#decisions-this-plan-rests-on), rules R15 and R16 in [doc 03](03-parametric-findings.md#11-design-rules), and checkpoint **C4b** in the [add-on notes](../prompts/addon-v1-notes.md) (items 1–6 below, with acceptance criteria).

1. **Subhole rule.** Place each subhole from a named parent along that hand's fingertip direction: left toward the player, right toward the far side. Defaults: sub_L from L ring, +11 mm; sub_R from R middle, +7 mm. Both are parameters. This keeps doc 04 D5's intent (one subhole per hand, at the ring/middle fingers) and fixes the direction.
2. **Layout as an arch model, not a wrapped photo.** Per hand: finger pitch, tilt, arch offset. Across hands: the index stagger. Plus rest space at both ends. The Miracle numbers stay the defaults, so P1 and P2 hardly move.
3. **The layout sets the deck length.** If the deck is shorter than span + rest space, the build warns and says how much is missing. It does not squeeze the hand any more; the squeeze moves to a parameter.
4. **The soft checks of section 3**, with status `warn`, listed in the check report and in the stage reports. `--strict` keeps exiting only on unexpected failures.
5. **P0:** either keep the taped test layout and label its renders and reports "taped test body, not a hand layout", or give P0 the arch model with a smaller pitch. The ladder only needs every P0 body to share one layout.
6. **Renders:** hole names next to the holes in the top view, so the layout can be judged at a glance.

## 7. Questions for the owner

Questions 1–4 are doc 02 Q8, Q10, Q11 and Q12; the A12 cavity-mode change is Q9. Each has a default until answered.

1. Left subhole parent: L ring (the photos, close to doc 04 D5) or L index (the Miracle)? *Default: L ring.*
2. Body: separate outer body and chamber (section 5, point 1), or a longer, flatter chamber with the wall as it is? *Default: separate outer body.*
3. Add the ergonomic body "P4" to Stage 2, or replace P3 with it? *Default: add it.*
4. P0: keep the taped layout with a label, or use the arch model? *Default: keep it, with a label.*
5. The index stagger: keep the left index near the far edge and the right index near the player, as on every reference? *Default: yes.*

## 8. Where more research is needed

The rules above rest on three instruments, only one of them with a scale, and on qualitative maker guidance. These are the gaps, ordered by what they block.

| # | Gap | Why it matters | What we know now | How to close it | Blocks | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| G1 | **Cavity mode of a long teardrop chamber** (115–125 mm inside) | Decides the body length (A12) and therefore whether the hand layout fits at all | c/(2L) says 95–124 mm is risky; doc 03 says tapered chambers resonate higher; the Miracle (150 mm outside) plays to F6; Pure Ocarinas suggests narrow chambers can help high notes (Q6) | Tier 2 FEM on the exported air meshes of P1, P2 and P4 (first mode against F6); literature on modes of tapered and ellipsoidal cavities; Stage 2 spectra (a fixed resonance across fingerings) | Q9, P4 shape, Phase 3 chamber | **High** |
| G2 | **More reference layouts with a scale** | Every range in §2–3 comes from three instruments; the photos have no scale | Miracle with a catalogue scale; one photographed design without one | Calipers on 2–3 more 12-hole alto Cs (hole centres, deck curvature, rest space, thumb holes, outer and chamber length), run through `measure_reference.py`; or ask makers or owners for drawings | Confidence in the ranges; D9 defaults | **High** |
| G3 | **How much hole position moves the pitch** (the maker's point 4: distance from the voicing, chamber shape) | If position matters, a layout change after calibration costs cents (A14), and P4's position factors will differ from P1–P3 | The lumped model has no position term; ψ per hole name absorbs it; makers disagree on how large it is | Literature on Helmholtz resonators with several necks and on neck position; design Stage 2 so ψ can be read against the distance from the window (the P0 ladder keeps one layout; P1–P4 move holes) | Layout freeze (D10); whether ψ transfers between shapes | **High** |
| G4 | **Hole tilt and flat lands** | `ergo_hole_tilt` (25°/30°) has no source; the land size (doc 02 "hole land", open problem 10) has no number anywhere | Pure Ocarinas: flat areas help, curved surfaces make fingers slide; nothing quantitative | A small coupon (about 20 g): holes of 6 and 10 mm at 0°, 15°, 30° and 45°, each with and without a flat land of 1.5 × d; cover each with a relaxed finger and blow a test note through a stub, or test the seal by suction | `ergo_hole_tilt` limit; the outer-body design (A13) | Medium |
| G5 | **Thumb holes and balance** | Pure Ocarinas puts balance first (right thumb to tail); the thumb positions come from one instrument; solid rest areas and a flatter body move the centre of mass | Miracle: left thumb under the left pinky/ring region, right thumb under the right index/middle | Compute the centre of mass of each built body in Blender and check it against the line from the right thumb hole to the tail; measure thumb positions on the G2 instruments; hand check in Stage 2 | `ergo_thumbs`; outer-body mass distribution | Medium |
| G6 | **Subhole convention and fingering chart** | The left subhole's parent differs between references (L ring on the photos, L index on the Miracle; the Japanese layout uses the right index and middle) | doc 02 Q3 default: the common 12-hole layout | Settle the fingering chart the owner plays; confirm on the P4 print by the hand check | Q8 | Medium |
| G7 | **Pressure against pitch** (the maker's point 2) | Tuning holds only along the recorded breath curve; the pitch is not corrected for pressure | Breath curve p0, α fitted; speaking range recorded per note in Stage 2 | From the Stage 2 data, fit cents per pascal per note; compare with the Pure Ocarinas figures and with the jet model in doc 03 §4 | Stage 3 accuracy at off-curve pressures | Medium |
| G8 | **Mouthpiece angle and face clearance** | Pure Ocarinas: a slightly angled mouthpiece leaves room between the right hand and the face; the add-on's stub is a plain box at 34° | Qualitative only | Check the right hand's clearance on the P4 hand check; look at the mouthpiece angles of the G2 instruments | Mouthpiece shaping (open problem 12) | Low |
| G9 | **Hand-size range** | The owner set finger size aside for the alto; the 14–20 mm pitch range should still suit most adult hands | Three references, all near 15–19 mm | Published adult hand anthropometry (hand length, finger spread, 5th–95th percentile) against the arch model's ranges | Only the width of the `ok` bands | Low |
| G10 | **The book's ergonomics chapters** | "Designing ocarinas with good ergonomics", "Dealing with weak high notes in 12 hole ocarinas" and "Avoiding problem areas" may hold maker numbers that no free source gives | Only the table of contents is free | Buy the e-book (£17.99 on ocarinamaking.com); owner's call | Could replace guesses in G4 and G5 | Low–medium |

Out of scope for now: timbre and "feel" (the maker's point 5), and jet CFD (point 6). The project measures their effects through calibration instead of modelling them.
