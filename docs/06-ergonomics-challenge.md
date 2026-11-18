# 06 — The ergonomics review, challenged

Written on 2026-11-15, after [05](05-ergonomics.md). Doc 05 proposed hand-layout rules from three references and listed ten research gaps (G1–G10). This pass works through those gaps with material that was already in the repository, tests each decision of doc 05 against it, and reports where the decision holds and where it does not.

Everything below is a finding or a proposal, with one exception: the owner accepted the P2 layout slide of section 3.11, so the P2 preset now has `layout_centre_from_port_mm = 23` and P2-80 was rebuilt. The add-on code, the kernel and the plan documents are unchanged.

The add-on numbers in sections 3.1–3.10 and 3.12 are those of the C4 bodies (commit 20b09ae). For P2 they describe the layout before the slide; section 3.11 has the numbers after it.

## 1. Bottom line

1. **The references were thinner than doc 05 says, and a better one was overlooked.** The shared photos are of a ceramic instrument with no scale. The repository already holds two 12-hole alto C designs with every hole centre in millimetres: the ECAN3 Ocarina of Time and Eclipse CAD models, analysed on the branch `ecan3-experimental`. Doc 05 did not use them. With them there are three layouts with a true scale (from two makers).
2. **The Miracle's "left subhole" is almost certainly a right-index subhole.** It sits 8.7 mm from the right index hole and 15.4 mm from the left index hole. That is the Japanese subhole layout (right index and right middle). The option "left subhole from L index, +15 mm" in question Q8 rests on a misreading and should be dropped.
3. **A subhole sits straight forward of its parent, perpendicular to that hand's line of holes, 7 to 10 mm away.** All six subholes with a scale obey this within 13°. The C4b plan slides along the body's Y axis, which is 14–16° off on P1 and P2, and its default of 11 mm for the left subhole is longer than any measured one.
4. **The two hand lines are parallel.** Within 1° on the Miracle and the Ocarina of Time, within 8° on the Eclipse. The proposed `ergo_hand_tilt` check tests each hand against the body and would pass a layout whose hands are 25° apart. The tilt against the body is a free choice (0° on the Ocarina of Time, 16° on the Miracle).
5. **The chamber-length conflict of doc 05 §5 mostly dissolves.** A finite-difference solve on the exported air meshes puts the first cavity mode at 1.63 × F6 for P1 and 1.40 × F6 for P2, against 1.13 and 0.99 by c/(2L). c/(2L) underestimates these shapes by 30–44 %. Both ECAN3 chambers are longer inside (127 and 136 mm) than the 124 mm hard stop proposed in A12.
6. **P2 can carry the hand layout as it is.** Sliding the layout 7 mm toward the tail gives 14–17 mm past both pinky centres with no new body. This is now the P2 preset, built and checked: the left thumb hole keeps 18.7 mm to the window (limit 10 mm) and no check changes status. The left pinky hole still leans 29° toward the end (section 3.11).
7. **Three of the proposed soft rules would warn on the reference designs themselves:** the tail rest space (20 mm), the hole tilt (30°) and the right thumb position. Section 5 gives revised limits.

## 2. Evidence used in this pass

| Source | What it gives | Where |
| --- | --- | --- |
| ECAN3 Ocarina of Time v3, ECAN3 Eclipse (CAD, maker-tuned, A4–F6) | Hole centres, axes and diameters in mm; thumb holes; outline; cavity shape | Hole data from `output/<model>/results.json` on `ecan3-experimental` (commit fd041cb); outline from the local voxel caches `output/<model>/stage1.npz` (not committed) |
| Miracle AO10-AC | Hole centres in mm from a product photo with a catalogue scale | [Miracle_M.md](../Analizes_ocarinas/Miracle_M/Miracle_M.md) §4.2 |
| Add-on bodies P1, P2, P3 at 80 cm³ | Built hole centres and axes; exported solids and air meshes | `addon_checks/*.json`, `addon_out/` |
| New script, layouts in the frame of the hands | Sections 3.1–3.9 | [measure_cad_references.py](../Analizes_ocarinas/Ergonomic_reference_12hole/measure_cad_references.py), output [measure_cad_output.md](../Analizes_ocarinas/Ergonomic_reference_12hole/measure_cad_output.md), plan views [Ocarina of Time](../Analizes_ocarinas/Ergonomic_reference_12hole/images/11_ecan3_oot_plan.png), [Eclipse](../Analizes_ocarinas/Ergonomic_reference_12hole/images/12_ecan3_eclipse_plan.png) |
| New script, cavity modes | Section 3.10 | [tools/cavity_modes_fd.py](../tools/cavity_modes_fd.py), output [addon_checks/cavity_modes_fd.md](../addon_checks/cavity_modes_fd.md) |
| Web check of the subhole conventions | Section 3.1 | [Pure Ocarinas, fingering system](https://pureocarinas.com/ocarina-fingering-system) |

**The frame of the hands.** Doc 05 measures tilt and stagger against "the body axis". A photo or a CAD file has no unique body axis: the Ocarina of Time model stands on its mouthpiece with the body turned 31°. The new script uses the mean direction of the two hand lines (L pinky → L index, R index → R pinky) as its axis. Every number in section 3 is independent of how the body is turned.

**About the photos.** The shared pictures show glossy blue and matte yellow ceramic bodies. They are not the ECAN3 print, although the outline is similar. In the hand frame they agree with the scaled references in kind: hand lines within 11° of parallel, both subholes forward of L ring and R middle. Their millimetre values are borrowed from the Miracle's span, so they should not set limits.

## 3. Findings

### 3.1 The Miracle's first subhole belongs to the right index finger

| | Distance to the first subhole | Direction |
| --- | --- | --- |
| R index | **8.7 mm** | straight forward of the right-hand line (1° off its normal) |
| L index | 15.4 mm | forward of the left-hand line |
| For comparison, second subhole from R middle | 7.3 mm | forward (13° off) |

`measure_reference.py` looks for a subhole's parent only among the holes of the hand it was assumed to belong to, so it reported "L index, +15.2 mm". Pure Ocarinas describes two layouts: one subhole per hand (Taiwanese), or both on the right hand at the index and middle fingers (Japanese). The Miracle matches the second. A 15 mm slide would also be half as long again as any other subhole measured here.

**Consequences.** Doc 05 §2 lists the left subhole as "+9 to +15 mm"; the 15 is this hole. Question Q8 ("L ring or L index") offers an option no reference supports. The real choice is one subhole per hand (both ECAN3 designs, the photographed ceramic) or both on the right hand (the Miracle). Decision D5 already picked one per hand, so its default stands.

**Still open.** By distance the left subhole's parent is the **ring** finger hole on both ECAN3 models (9.1 and 10.0 mm, against 21 mm from the middle hole) and on the photos. The usual description of the Taiwanese layout says "middle fingers". Either these designs differ from that description or the description is loose. The geometry rule does not depend on the answer, but the hand check on the first print should confirm which finger closes it.

### 3.2 Subholes: straight forward of the parent, 7–10 mm

| Layout | Left-hand or first subhole | Right-hand or second subhole |
| --- | --- | --- |
| Miracle | from R index: 8.7 mm, 1° off the normal | from R middle: 7.3 mm, 13° |
| ECAN3 Ocarina of Time | from L ring: 9.1 mm, −4° | from R middle: 7.5 mm, 3° |
| ECAN3 Eclipse | from L ring: 10.0 mm, −4° | from R middle: 8.5 mm, 7° |
| Add-on P1-80 (C4) | from L middle: 9.4 mm, **−131°** (behind the finger) | from R middle: 7.6 mm, **70°** (sideways) |

"Normal" is the perpendicular to that hand's pinky → index line, on the side the fingertips point to.

- **Direction.** The C4b notes place the subhole along the body's ±Y. On P1 and P2 the hand lines are tilted 14–16° against the body, so ±Y is that far off the measured direction: 2.5 mm sideways on a 10 mm slide. Use the normal of the hand line.
- **Length.** The default of 11 mm for sub_L (D5) comes from the photo scaled to the Miracle. The CAD values are 9.1 and 10.0 mm. With the add-on's own hole sizes (L ring 8.4 mm, sub1 3.3 mm) the shortest slide that keeps the 3.4 mm edge gap is 9.3 mm. **Proposed default: 9.5 mm.** For sub_R the shortest is 6.7 mm and the references give 7.3–8.5; **proposed default 7.5 mm** (D5 says 7).
- **Range.** `ergo_subholes` allows 6–16 mm. The upper end exists only because of the misread Miracle hole. Proposed `ok` range: 7–11 mm, within 20° of the normal.

### 3.3 The two hand lines are parallel

| Layout | Angle between the hand lines | Right line nearer the player by |
| --- | --- | --- |
| Miracle | 0.6° | 24.0 mm |
| ECAN3 Ocarina of Time | 1.0° | 19.2 mm |
| ECAN3 Eclipse | −7.6° | 26.4 mm |
| Add-on P1-80 / P2-80 | 2.1° / 2.9° | 21.1 / 21.0 mm |
| Add-on P3-80 | −8.6° | 22.7 mm |

Doc 05 describes "two arcs that meet in the middle", each tilted 4–23° against the body, and proposes `ergo_hand_tilt` = 0–25° per hand. The frame-free reading is simpler: **two parallel lines of holes, 19–26 mm apart across the hands.** The 16° of the Miracle is how its maker turned the hands against the body; the Ocarina of Time has 0°.

The proposed check misses this. A layout with the left hand at 0° and the right at 25° passes it and matches no reference. **Proposed:** replace it with `ergo_hands_parallel` (angle between the two lines, `ok` within ±10°) and `ergo_hand_offset` (`ok` 18–28 mm). Report the tilt against the body as a number without a limit.

### 3.4 Finger pitch: the lower limit came from the photos

Pitches with a scale: Miracle 17.1–18.6 mm, Ocarina of Time 17.9–18.0 mm (a constant 18 mm), Eclipse 18.8–20.0 mm. The rule's lower limit of 14 mm comes only from the perspective photos. One study found by a quick search gives mean index-finger joint widths of 13.8 and 15.4 mm for two groups ([table](https://pmc.ncbi.nlm.nih.gov/articles/PMC5702813/table/tbl_001); gap G9, not followed up), so at a 14 mm pitch neighbouring fingers would touch, which Pure Ocarinas names as a fault.

The add-on's 15.2–15.6 mm between L pinky and L ring on P1 and P2 is a plan-view number. On the surface the distance is 17.1 mm; the hole sits on the steep end, so the plan view shortens it. **Proposed:** measure the pitch as the straight distance between centres in 3D, `ok` 16.5–20.5 mm.

### 3.5 Shortening a layout: overlap the hands, do not squeeze the fingers

The Eclipse has the shortest pinky-to-pinky distance (98.8 mm) and the largest finger pitch (19–20 mm). It gets there by overlap: its right index hole sits 20.6 mm toward the bulb from the left index hole, and the hands are further apart across (26.4 mm). The add-on shortens P3 by compressing the pitch to 12.9–16.6 mm instead.

**Proposed for C4b step 3:** the "squeeze" parameter slides the two hands along their own lines toward each other and keeps the finger pitch. `ergo_index_meet` should then allow it: across 18–28 mm, along −22 to +5 mm in the hand frame (references: −1.6, −2.5, −20.6). Doc 05's "within ±10 mm along" would warn on the Eclipse.

### 3.6 Rest space: measure from the hole edge; 20 mm at the tail is too strict

| Layout | Bulb, from the hole edge | Tail, from the hole edge |
| --- | --- | --- |
| Miracle | 10.8 mm | 29.9 mm |
| ECAN3 Ocarina of Time | 15.5 mm | 13.2 mm |
| Add-on P1-80 | 6.4 mm | 5.2 mm |
| Add-on P2-80 | 4.8 mm | 21.6 mm |
| Add-on P3-80 | 3.4 mm | 5.3 mm |

The Eclipse is left out: its chamber sits in a decorative crescent with 45 mm of solid past both pinkies.

- The Ocarina of Time has 14.8 mm from the pinky centre to the tail. The proposed limit of 20 mm would warn on it.
- The add-on's kernel makes the left pinky hole 7.1 mm wide; the references use 4.5–6.1 mm. A limit from the hole centre hides this. The finger rests on what is left past the edge.
- **Proposed:** `ergo_rest_space` = at least 10 mm from the hole edge at both ends. More at the tail is a preference, shown as a number.
- The verdict of doc 05 on the add-on bodies stands and gets clearer: P1 and P3 have about half the land of the tightest reference at both ends.

### 3.7 Hole tilt: the direction matters more than the angle

| Layout | L pinky | L ring | L middle | L index | R pinky | R ring | R middle | R index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ECAN3 Ocarina of Time | 20° far | 18° far | 15° far | 30° far | 15° tail | 11° tail | 10° player | 13° player |
| ECAN3 Eclipse | 12° far | 9° far | 20° far | **42° far** | 9° tail | 8° tail | 17° player | **39° player** |
| Add-on P1-80 | **38° bulb** | 15° bulb | 4° far | 22° far | **32° tail** | 16° tail | 13° tail | 22° player |
| Add-on P3-80 | **41° bulb** | 15° bulb | 7° far | 17° far | **46° tail** | 17° tail | 8° tail | 17° player |

The proposed `ergo_hole_tilt` (ok to 25°, warn above 30°) has no source (gap G4), and both ECAN3 designs would warn at their index holes. The pattern in the references is consistent:

- **Across the hand, toward the hand that covers the hole:** up to 42°. Left-hand holes lean to the far side, where the left fingers come from. The right index and middle lean to the player. A finger meets such a hole square on.
- **Along the body, toward an end:** never more than 15°.

The add-on's fault is of the second kind: its pinky holes lean 32–46° toward the ends, so the finger slides off the end of the body. Its index holes at 22° are well inside what the references do.

**Proposed:** two checks. `ergo_hole_lean_end` (lean along the hand axis toward the nearer end): `ok` to 20°. `ergo_hole_lean_side` (lean across): `ok` to 45° toward the covering hand, warn if it leans away from it. The coupon of gap G4 is still worth printing, but with this split.

### 3.8 Thumb holes

Along the hand axis, + toward the tail:

| Layout | L thumb from L pinky | R thumb from R index | R thumb from R middle |
| --- | --- | --- | --- |
| Miracle | +9.7 mm | +10.5 | −7.3 |
| ECAN3 Ocarina of Time | +7.2 | +15.0 | −3.0 |
| ECAN3 Eclipse | +4.4 | +22.0 | +2.4 |
| Add-on P1-80 | +8.6 | +9.6 | −7.2 |

`ergo_thumbs` says "right thumb between R index and R middle". The Eclipse puts it 2.4 mm past R middle and would warn. **Proposed:** right thumb within −8 to +3 mm of the R middle hole; left thumb 4–10 mm tailward of L pinky. The add-on is in range on both.

### 3.9 Balance (gap G5)

Centre of mass of the solid in plan view, against the line from the right thumb hole to the tail tip:

| Body | Toward the bulb from the R thumb | Off the line |
| --- | --- | --- |
| Add-on P1-80 / P2-80 / P3-80 | 15.4 / 10.1 / 9.7 mm | 3.2–3.8 mm |
| ECAN3 Ocarina of Time | 30.7 mm | 14.0 mm |
| ECAN3 Eclipse | 24.6 mm | 7.4 mm |

The add-on bodies are closer to the line than both references. Nothing here argues for moving the thumbs. Solid rest areas at the tail would move the centre of mass toward the thumb, which is the helpful direction. This gap can be closed for the C4 shapes; repeat the number when an outer body exists.

### 3.10 Chamber length and the cavity mode (gap G1)

`tools/cavity_modes_fd.py` solves the standing-wave modes of a closed, rigid cavity on a grid of 1.5 mm cubes cut from the air mesh. Self-test: a box is exact, a sphere is 1.0 % low.

| Chamber | Longest line inside, L | c/(2L) ÷ F6 | First cavity mode ÷ F6 | Mode ÷ c/(2L) | Present check |
| --- | --- | --- | --- | --- | --- |
| P0-80 | 79 mm | 1.58 | 2.10 | 1.32 | pass |
| P3-80 | 96 mm | 1.29 | 1.75 | 1.36 | pass |
| P1-80 | 110 mm | 1.13 | **1.63** | 1.44 | needs_fem |
| P2-80 | 124 mm | 1.00 | **1.40** | 1.40 | **fail** (0.99 from the spine length) |
| ECAN3 Eclipse | 127 mm | 0.98 | 1.27 | 1.30 | – |
| ECAN3 Ocarina of Time | 136 mm | 0.92 | 1.19 | 1.30 | – |

- **c/(2L) is 30–44 % low for these shapes.** Doc 03 §8 says it is the lowest estimate; this is by how much. The tapered presets gain the most.
- **P1 and P2 clear the 1.3 margin.** P2 at 80 cm³ fails today's check by plan; by this measure it passes.
- **Both ECAN3 chambers are longer than the A12 hard stop (124 mm)** and are published as tuned to F6. Their own cell network, with the window open, gives 1.34 (Eclipse) and 1.08 (Ocarina of Time) × F6; the two methods differ by 5–10 %.
- **The chamber needs more than "span plus a little".** Doc 05 §5 asks for 115–120 mm inside. The references keep 10–17 mm of chamber past each pinky hole (the add-on's P1: 3–6 mm). For a 105 mm span that is 125–135 mm, which the numbers above allow.

**Proposed for A12 and R9:** replace the length rule with the computed first mode. Keep the margin at 1.3 × F6 as the `ok` line and drop the hard stop on length. A mode between 1.0 and 1.3 × F6 gives `needs_fem`, which now means "measure it in Stage 2".

**Limits.** All holes and the window are closed. At F6 every hole is open, which moves the mode. The 1.3 margin is itself a guess. The Stage 2 spectra (a resonance that stays fixed across fingerings) remain the real test.

### 3.11 P2 may already be the ergonomic body

P2-80 is 133 mm long outside and its cavity mode is fine (3.10). Its fault is where the layout sits: 8.4 mm past the left pinky, 23.6 mm past the right. Sliding the layout centre toward the tail (preset value `layout_centre_from_port_mm`, now 16):

| Layout centre from the port | Bulb / tail, pinky centre to the end | L pinky tilt | R pinky tilt | Squeeze |
| --- | --- | --- | --- | --- |
| 16 mm (C4) | 8.3 / 23.7 mm | 40° | 11° | none |
| 23 mm | 14.2 / 16.7 mm | 29° | 14° | none |
| 26 mm | 16.9 / 13.8 mm | 26° | 16° | none |

At 23–26 mm P2 matches the Ocarina of Time's rest space with no outer body and no new preset. P1 cannot do this: it is about 20 mm too short, and the slide only moves the squeeze to the other hand.

**Built and checked at 23 mm, then adopted.** The slide was first built as a variant with `tools/geometry_check_variant.py`, which overrides a preset value without touching the preset file. The owner then accepted it: the P2 preset now says 23, and the plain P2-80 was rebuilt ([check report](../addon_checks/P2-80.md), [top view](../addon_renders/P2-80/top.png)). The rebuilt body is identical to the variant. Every geometry check has the same status as before the slide: no unexpected failure, and the same three expected ones (`cavity_mode` by c/(2L), and the two pad-limit checks for L index and L thumb).

| Measured on the built body | P2-80 in C4 (16 mm) | P2-80 now (23 mm) | Reference or limit |
| --- | --- | --- | --- |
| `hole_to_voicing`: nearest hole edge to the window | L thumb, 23.4 mm | L thumb, **18.7 mm** | at least 10 mm |
| L thumb edge to the voicing block | 14.2 mm | 9.4 mm | must not touch (0.5 mm) |
| `voicing_keepouts` (inside, 10 mm of the labium) | pass | pass | – |
| Land past the L pinky, from the hole edge | 4.8 mm | **10.7 mm** | references 10.8–15.5 mm |
| Land past the R pinky, from the hole edge | 21.6 mm | **14.7 mm** | references 13.2–29.9 mm |
| L pinky lean toward the bulb end | 40° | **29°** | references at most 15° toward an end |
| L ring lean toward the bulb end | 19° | 11° | – |
| R pinky lean toward the tail | 11° | 14° | – |
| Smallest edge gap between holes | 4.55 mm | 4.55 mm | at least 3.4 mm |
| Thinnest plastic away from the voicing | 3.43 mm | 3.99 mm | – |
| Hand lines apart, across | 21.0 mm | 18.7 mm | references 19.2–26.4 mm |
| Centre of mass, toward the bulb from the R thumb hole | 10.1 mm | 17.2 mm | references 24.6–30.7 mm |

What it shows:

- **The voicing is not in the way.** The left thumb hole keeps 18.7 mm to the window, almost twice the limit. A 26 mm centre would cost about 3 mm more and should still pass; it was not built.
- **The rest space now matches the tightest reference at both ends**, with no outer body.
- **The left pinky hole still leans 29° toward the end.** The slide takes 11° off, but the bulb of P2 is round there. This is what is left for a flatter deck or an outer body (A13) to fix.
- **A side effect to watch:** the hand lines come 2.3 mm closer across (18.7 mm, just under the references). The index holes now sit where the body is narrower, and `place()` limits the sideways offset to 35 % of the half section. The same clamp will matter for the subhole slide in C4b.
- The subholes are still in their C4 places; the slide does not touch that rule.
- The right thumb hole moved 7 mm toward the tail with the layout, so the centre of mass sits further from it. It is still closer than on both references (3.9).
- The acoustic numbers are unchanged, as they should be: same cavity, same volumes (capped air 80.008 cm³), same hole sizes and voicing hash. The cavity-mode result of 3.10 is the same (1.40 × F6).

**Consequence for Q10 and Q11.** With the slide in the preset, the separate outer body and a new P4 are needed for one thing only: the lean of the left pinky hole. Whether that is worth a print is the owner's call; the hand check on a printed P2 would answer it.

### 3.12 Hole sizes

Doc 05 §4 says the add-on's diameters "run from 3.1 to 12.7 mm" against the Miracle's 2.6–7.1 mm. The 12.7 is the left thumb. On the finger face the add-on has 3.1–10.8 mm; the references have 1.7–8.3 mm there and thumbs up to 11.9 mm. Only the left index hole (10.8 mm) is outside what the references use. The left pinky (7.1 mm) is at the top of their range and costs rest space (3.6).

## 4. The research gaps after this pass

| # | Gap | Status | What moved | What is left |
| --- | --- | --- | --- | --- |
| G1 | Cavity mode of a long chamber | **Mostly closed on paper** | First mode computed for P0–P3 and both ECAN3 chambers (3.10) | Open holes; the Stage 2 spectra |
| G2 | Reference layouts with a scale | **Half closed** | Two CAD layouts added; three with a scale now | Both new ones are by one designer. The ECAN3 data sit on another branch. Calipers on one or two ceramic instruments would still help |
| G3 | Hole position and pitch | Open | The ECAN3 track already has a cell network that resolves position; it cut the Ocarina of Time's error from 32 to 20 cents | Not run on the add-on bodies. It would give a first estimate of ψ before any print |
| G4 | Hole tilt and lands | **Reframed** | Direction split with reference numbers (3.7) | The coupon, with lean toward the end and toward the hand as separate cases |
| G5 | Thumbs and balance | **Closed for C4 shapes** | Thumb ranges (3.8), centre of mass (3.9) | Repeat with an outer body; hand check |
| G6 | Subhole convention | **Mostly closed** | Miracle is the Japanese layout; rule in 3.2 | Which finger closes the left subhole (3.1) |
| G7 | Pressure against pitch | Open | – | Needs Stage 2 data |
| G8 | Mouthpiece angle | Small step | The Ocarina of Time's mouthpiece stands roughly 60° to the hand axis, not square (read off the plan view, not measured) | Clearance check on a print |
| G9 | Hand-size range | Open | One indicative figure (3.4) | The US Army hand survey (Greiner 1992) has the tables; not read |
| G10 | The book's chapters | Open | – | Owner's call |

## 5. The soft rules, revised

Still warnings only. Limits are the range of the references with a scale, widened a little.

| Check | Doc 05 | Proposed | Why |
| --- | --- | --- | --- |
| `ergo_finger_pitch` | 14–20 mm, plan view | **16.5–20.5 mm, straight 3D distance** | 3.4 |
| `ergo_hand_span` | 44–60 mm | 50–60 mm | References: 50.9–59.5 |
| `ergo_arch` | +1 to +7 mm | **+0.5 to +7 mm**, warn if negative | The Ocarina of Time's right hand is at +1.2 |
| `ergo_hand_tilt` | 0–25° per hand against the body | **Replace:** `ergo_hands_parallel` within ±10°, `ergo_hand_offset` 18–28 mm; tilt against the body reported only | 3.3 |
| `ergo_index_meet` | 18–32 mm across, ±10 mm along (body frame) | 18–28 mm across, **−22 to +5 mm along, hand frame** | 3.5 |
| `ergo_subholes` | +5 to +16 mm along Y; 6–16 mm | **7–11 mm, within 20° of the hand line's normal**, parent = nearest finger hole | 3.1, 3.2 |
| `ergo_rest_space` | 12 mm bulb, 20 mm tail, from the centre | **10 mm from the hole edge, both ends** | 3.6 |
| `ergo_hole_tilt` | 25° ok, warn above 30° | **Split:** toward an end ≤ 20°; across ≤ 45° toward the covering hand | 3.7 |
| `ergo_thumbs` | R thumb between R index and R middle | **R thumb −8 to +3 mm from R middle; L thumb 4–10 mm tailward of L pinky** | 3.8 |

## 6. What this changes in the plan (proposals)

| Item | Now | Proposed |
| --- | --- | --- |
| D5, R16 | sub_L from L ring +11 mm, sub_R from R middle +7 mm, along Y | 9.5 mm and 7.5 mm, along the normal of each hand line |
| Q8 | L ring or L index | Drop the L index option. Remaining question: confirm on a print which finger closes the left subhole |
| C4b step 1 | Port the metrics of `measure_reference.py` | Port the hand-frame metrics of `measure_cad_references.py` instead; the parent search must look at both hands |
| C4b step 3 | Squeeze becomes a parameter | The squeeze overlaps the hands (3.5). Add a slide of the layout along the body, and try P2 at 23–26 mm (3.11) |
| C4b step 4 | Nine `ergo_*` checks | The table in section 5 |
| C4b acceptance | sub_L +9 to +13 mm from L ring | 9–10.5 mm |
| A12, R9, Q9 | Hard stop at 124 mm; FEM between 75 and 124 mm | First mode from `cavity_modes_fd.py`; `ok` at 1.3 × F6; no length stop (3.10) |
| P2 preset | `layout_centre_from_port_mm = 16` | **Done:** 23, P2-80 rebuilt (3.11) |
| A13, Q10, Q11 | Separate outer body; add P4 | Their remaining job is the lean of the left pinky hole (29° on the slid P2). Decide after a hand check on a printed P2 |
| Doc 05 §2 | "Three references" | Miracle, two ECAN3 CAD models; the photos as a qualitative check |
| Doc 04 P4 row | Chamber 115–120 mm inside | 125–135 mm if it is built: the references keep 10–17 mm of chamber past each pinky |

## 7. Limits of this pass

- Three layouts with a scale, two of them by one designer. The limits in section 5 are their range, not a population.
- The Miracle's millimetres come from a product photo; its rest space is along the picture's long axis, not the hand axis.
- "Well rated" is hearsay for all of them. Nobody on this project has played any of these instruments.
- The ECAN3 hole axes are those of the ECAN3 analysis; the add-on's are cavity-surface normals. They are comparable, not identical.
- The cavity-mode solve is a desk check with closed holes (3.10).
- The ECAN3 numbers in the new script are copied from another branch, and its outline tables need two local files that are not in git. Without them the script still produces sections 1–3 and 5.
- One body was rebuilt: P2-80 with the layout centre at 23 mm (3.11). The 26 mm row of that section's first table was computed with the layout module alone.
- Doc 05 §4 and the C4 evidence in the add-on notes still show P2 before the slide. `measure_output.md` and `measure_cad_output.md` were regenerated and show it after.
