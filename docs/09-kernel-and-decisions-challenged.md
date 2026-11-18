# 09 — The kernel, the suite and the decisions of 15–17 November, challenged

Written on 2026-11-18, after the two lines of work were joined on `main`. The owner asked for a full re-analysis that takes his four voicing decisions as given (a lowered windway, a neck, the ellipse cut, a smooth cavity inside), reviews the work of 16 November and the research of 17 November, and challenges the kernel and the test suite with three bases: the Heuer tutorial series, the reference library, and the two professional instruments (Spencer, Songbird).

**Nothing in the kernel, the add-on, the presets or the tests was changed.** One analysis script and its output were added: [kernel_vs_references.py](../Analizes_ocarinas/Kernel_challenge/kernel_vs_references.py), [kernel_vs_references.md](../Analizes_ocarinas/Kernel_challenge/kernel_vs_references.md). Every number below that is not quoted from another document comes from that output. Nothing was printed or played.

> **Applied later on 2026-11-18: item 1, the fingering order.** The owner's answer: switch to the Asian system, provided it is compatible with the split subholes (one per hand, decided on 2026-11-15). It is compatible. The source gives the same subhole order the kernel already had (the left subhole opens B4, the right one C5); both subhole fingers stay on their main holes from A4 to C5; and the left ring finger, which carries the left subhole, is the first left finger to lift (A5), after both subholes are open. `params/alto_c_12hole.toml` now follows the Asian order. The record of what was rebuilt is in the build notes ("Fingering order switched, 2026-11-18"). **The rest of this document is kept as it was written that morning: where it says "the parameter file", it means the file before the switch.** Items 2 to 4 and 6 to 9 are still open.

> **Answered later on 2026-11-18: item 5, what "lowered" means, and the smooth cavity.** The owner's words: "With lowered I mean tilted towards the body hidden by the neck volume, the pivot remains with the voicing alignment." So the mouth end of the windway tilts toward the body, the neck hides it, and the pivot stays at the lip, which keeps the lip's offset from the jet. **That is what the add-on builds** (a negative `windway_pitch_deg`, the neck not turning with the pipe). The second reading of section 3.1 is the right one, and the direction is settled. What section 3.1 leaves open is unchanged by the answer and is not a question for the owner: no model in the library shows how a jet that leaves the labium's inner face by a few degrees speaks, so the tilt belongs in the voicing hash and in one Stage 1 stub. The owner also confirmed the smooth cavity for now: **experimental internal cavities (the partitions and the solid tail of section 3.4 and doc 07 §3.9) are not being implemented yet.**

> **Decided and applied later on 2026-11-18: the left slide, the cut, the mouth end, the hash, the stubs and the stance of the neck** (section 8, items 4 to 6 and the slide of item 8). The owner saw a picture sheet and the measured effect of each option ([decisions.md](../Analizes_ocarinas/Decisions_2026-11-18/decisions.md)) and took: left subhole slide 10 mm; ellipse cut "P3"; 3 mm at the mouth end of the windway; the build in the hash, with stub V-a for the build and stub V-af for the plain build; and, against my recommendation, **a neck that stands 15° off the body**. These are now `[voicing_rules]`, rule version 2, and every stage was regenerated (build notes, "Owner decisions applied, 2026-11-18"). Two things follow that this document did not foresee. First, the pipe now lies 10° lower than the neck and reaches the lip heading **+5° into the chamber**, so the caution of section 3.1 about a jet that leaves the labium's inner face no longer applies; the 2.5° that the owner agreed for a level neck cannot be built inside a 15° neck without a much deeper mouth end, and the angle is the one open point. Second, the outside keep-out check now measures the 45° flare itself, because a standing neck rises behind the window; the limit did not change, and the neck stands 41° steep seen from the window rim.

## 1. Bottom line

In order of consequence. Items 1 and 5 need an answer before any print that has holes or a tilted windway.

1. **The kernel opens the six upper holes in an order no fingering chart uses.** The parameter file opens the left pinky for A5 and the two thumbs for E6 and F6. The Asian system, the common one on 12-hole instruments, opens left ring, left middle, left index, then the left thumb (D6), the right thumb (E6) and the left pinky last (F6). The kernel sizes a hole for the note it opens, so six holes carry the wrong diameter for the finger that covers them. All three measured instruments fit the kernel better in the Asian order (section 6.1).
2. **With the order put right, most of the "expected" pad-limit failures go away, and so does open problem 19 at 80 cm³.** The left index hole drops from 12.1 to 6.3 mm at 80 cm³; the two largest holes move under the thumbs, where every reference has them; the edge gap between the left subhole and L ring at the 9.5 mm slide becomes 3.78 mm (limit 3.4) where the notes record 3.05 mm.
3. **Makers cut the top of the scale smaller than the passive model and the right hand larger, on all three instruments.** Measured against the kernel's own holes: right hand 1.07–1.21, thumbs 0.77–0.83, left pinky 0.47–0.75. The kernel has no pressure-dependent pitch (it says so), and this is what that omission looks like. Two statements built on the kernel's raw diameters do not hold: that "the design breaks at about 74 cm³" because of the holes, and that the pad limits will fail on purpose.
4. **The proven volume band is wider than doc 04 says.** Doc 04 lists 62–77 cm³. The Spencer adds about 70–77 cm³. The Songbird Alto C fits 101 cm³ here and 92–116 cm³ by the two routes of 16 November; it is 77 cm³ or more at any length the evidence allows. The 95 cm³ step is inside the band of made instruments, not past it.
5. **The lowered windway points the jet the other way from the owner's own sample.** In the sample, and on the NBN model, the jet meets the labium heading into the chamber at 16° to the labium's inner face. The add-on starts level with that face (0°) and lowers the mouth end, so its jet leaves that face heading outward by the tilt angle. "Lowered" is true of both, measured against two different things. This needs the owner's word before the tilt goes any further (section 3.1).
6. **The cut is an acoustic part, not a finish.** The wall at the window is 36 % of the window's effective length in the kernel. Half a millimetre of effective throat is about 40 cents on A4. A duct estimate puts the two ellipse cuts 23–29 cents flat of the fan cut that the Stage 1 stubs are built with. The cut, the shelf and the tilt are in no hash.
7. **The windway rule is outside every reference at the mouth end.** The kernel's slot is 1.56 mm high at the mouth end. The Miracle has 2.5–3 mm, the owner's sample 3.0 mm, the Eclipse 3.7 mm, the NBN 4.5 mm; the two CAD models also narrow in width. The slot's dimensions are hashed, so this must be settled before the stubs.
8. **The research of 17 November holds on its main points** (labium below the jet centre, the teardrop and its orientation, the window length, the break pressure, dropping 125 cm³). Three of its statements are stronger than their evidence, and it missed the fingering chart, which three documents had listed as "to confirm" (section 5).
9. **The test suite checks the kernel against itself.** No test compares it with a made instrument, none ties the fingering to a source, and the fitter is tested only on data generated by the model it fits (section 7).

## 2. What was read, and what is new here

| Base | Read | Used for |
| --- | --- | --- |
| The tutorial series | [01](01-source-review.md) §5–6 (the excerpts of Heuer's Videos #1–#8) and the eight frames in `references/heuer-frames/`. The full transcripts are not in the repository | Sections 3 and 5 |
| The professional instruments | The [Spencer](../Analizes_ocarinas/Spencer_OoT_12h/Spencer_OoT_12h.md) and [Songbird](../Analizes_ocarinas/Songbird_OoT_12h/Songbird_OoT_12h.md) reports, [ceramic_volume_check.md](../Analizes_ocarinas/Windway_and_body_shape/ceramic_volume_check.md), [07](07-windway-and-body-shape.md), [08](08-stage2-body-library.md) | Sections 4 and 6 |
| The reference library | [Miracle](../Analizes_ocarinas/Miracle_M/Miracle_M.md), the ECAN3 track, the NBN and Eclipse sections and the owner's sample in [Window_cutout.md](../Analizes_ocarinas/Window_cutout/Window_cutout.md) | Sections 3 and 6 |
| The kernel and the suite | `kernel/voicing.py`, `holes.py`, `sizing.py`, `params/alto_c_12hole.toml`, the test classes of `kernel/` and `tests/` | Sections 6 and 7 |
| A source that was not in the repository | Pure Ocarinas, [The ocarina's fingering system](https://pureocarinas.com/ocarina-fingering-system), opened on 2026-11-18 | Section 6.1 |

New in this document: the measured holes of the Spencer and the Songbird put through the kernel's scale model note by note (the reports of 16 November used them only for the air volume); the test of the fingering order; the throat and slot estimates; and the reading of the windway's direction on the sample and the two CAD models.

## 3. The owner's four voicing decisions

### 3.1 The lowered windway

**What the references show.** The angle that matters is the one between the jet and the inner face of the labium.

| Body | Jet against the labium's inner face | Source |
| --- | --- | --- |
| Owner's sample | **16° into the chamber.** The neck stands about 27° off that face; the pipe is lowered 10.6° inside it | Window_cutout.md §10.1 |
| NBN | **16° into the chamber** | Window_cutout.md §2 |
| ECAN3 Eclipse | The windway comes down toward the labium and turns the last 3 mm by 20°; the labium is a blade, symmetric about the jet | Window_cutout.md §2 |
| Add-on, level | 0°: the jet runs along the flat ceiling of the pocket | `voicing_geo.py` |
| Add-on, lowered 2.5° | **2.5° away from the chamber** | [sheet_neck.png](../Analizes_ocarinas/Window_cutout/images/sheet_neck.png), lower section |

**The challenge.** The owner's rule is "in practice only a lowered windway is used", and it came with the sample. In the sample the pipe is lowered *inside a neck that stands 27° off the body*, and the jet still arrives heading inward. The add-on's neck lies along the windway, level with the labium's inner face, so lowering from there carries the jet past parallel to the other side. No reference in the repository has a jet that heads outward. The session that built it flagged its own reading of "lowered" as an interpretation, not the owner's words.

Two readings are possible, and only the owner can say which he meant:

- *Lowered against the neck.* Then the add-on should build a neck that stands off the body and a pipe that is lowered inside it, with the jet still entering at something like 10–16°. In the add-on's settings that is a positive `windway_pitch_deg` with a larger `stub_pitch_deg`. The bodies `P4-80-p10` and `P4-80-p10s7` were steps in that direction; they failed only the outside 45° keep-out.
- *Lowered against the labium.* Then the present −2.5° is what was asked, and it is an untested geometry with no reference behind it.

**What does hold.**

- Heuer puts the airway exit "about a quarter of an inch below the top" (#3, #5), and lowering the exit goes that way.
- The pivot at the lip edge keeps the lip at its −0.2 mm offset from the jet's centre line at any angle.

**What does not hold as argued.** The notes read Heuer's "the drop is straight up and down or tilted in, never tilted up" as a reason for the direction of the tilt. That sentence is about the shape of the wall under the exit. It does not say which way the jet points.

**The tilt and the offset add up.** A lip below the jet centre sends more of the jet outside. A jet that heads outward does the same. The two labium coupons (0 and −0.35 mm) are level stubs, so they do not say where the lip should sit under a tilted jet.

**The room for it.** The exit moves 0.42 mm toward the chamber at 2.5° and the mouth end 1.73 mm. The plastic under the windway falls much faster than the exit moves: 3.01 → 1.48 mm on P4-80, because the pipe closes on the curved chamber wall just behind the exit. The working range on P4-80 is 0 to about 2.7°; P0-95 has 2.22 mm at 0° and fails at 4°. The sample reaches 10.6° with a 5.5 mm wall and a flat face inside. The Spencer's walls are 4–12 mm. So the uniform 4 mm wall (doc 04 D3) is what limits this decision, not the neck.

**Proposals.** (a) Ask the owner for the frame of "lowered", with the two section drawings side by side. (b) Whatever the answer, put the tilt in the voicing hash and give Stage 1 one stub with it. (c) If more than about 2.5° is wanted, thicken the wall locally around the voicing; with the ellipse cut the throat no longer follows the wall (section 3.3), so the two can be set apart.

### 3.2 The neck

- **Acoustically it is outside plastic.** It adds 2.1 cm³ of plastic to P4-80 (52.9 → 55.1 cm³) and no air: the capped air, the window and the windway measure the same with and without it. The air inside the windway is about 0.36 cm³ and is not part of V0.
- **Its size against the references.** The add-on's neck is 4.8 × the window width where it meets the body: about 42 mm on the 80 cm³ window. The Spencer and the Songbird Alto C have 36 mm, the owner's sample 48.5 mm. Its length is the windway's, 30 mm. The Songbird's mouthpiece stands 48 mm beyond the body edge, the sample's neck is 32 mm high, and the reference windways are 30–40 mm long. The add-on is at the short end, and inside the range.
- **It scales with the window, and the references do not.** At 65 cm³ the neck would be 33 mm wide and at 95 cm³ 53 mm. A neck is held by the lips; it should be a size of its own.
- **The slim mouth end is the print base** (the notes already say it needs a brim), and the 1.2 mm of plastic around the pipe is the owner's accepted minimum. With a taller mouth end (section 6.5) the neck's mouth end grows by the same amount.

**Verdict:** no conflict with any source. Two proposals: make the neck width a number in millimetres, and decide the windway slot (section 6.5) before the neck is frozen, because the slot sets the neck's mouth end.

### 3.3 The ellipse cut

**What the references show.** Every window in the library sits in a dish that is wider than the window: Heuer's teaching model, the Songbird (a round recess about 28 mm across), the Spencer (a scoop about 30 × 20 mm), the Eclipse (a heart-shaped dish about 16 × 25 mm), the NBN (a scoop 14–15 mm wide). The ellipse cut is 14.8 × 21.6 mm (P3) and 16.8 × 22.4 mm (P1).

- **The owner's choice is in the family, at the narrow end.** Per side, P3 and P1 open 3 and 4 mm over a 4 mm wall, a flare of 37–45°. The Songbird's recess opens about 10 mm per side if its window is about 8 mm wide (the opening itself is in shadow on the photo), over a wall of perhaps 8 mm: about 50°. The two ellipse settings are in proportion to their wall. There is no evidence that they are too narrow.
- **Heuer's model has a dish that is wider across than along the jet.** The ellipse is longer along the jet. The model is a hand-made prop, so this is a hint.
- **Heuer on the exit: "no overhangs … not too flared out"** (#8). The cutter's no-overhang rule answers the first. The shelf above the exit is a flare on the windway side; the Eclipse keeps 6 mm of steep wall there and the NBN 1.2 mm, so the references do not settle it.

**The challenge is acoustic.** The kernel models the window as a prism through the wall, G_w = A / (t + k·d_eq). For the 80 cm³ window:

| Effective throat depth | G_w against 4 mm | A4, same window and volume | Volume the same window tunes to A4 |
| --- | --- | --- | --- |
| 2.5 mm | +15.5 % | +125 cents | 92 cm³ |
| 3.0 mm | +9.8 % | +81 cents | 88 cm³ |
| 3.5 mm | +4.7 % | +40 cents | 84 cm³ |
| 4.0 mm | 0 | 0 | 80 cm³ |
| 5.0 mm | −8.2 % | −74 cents | 73 cm³ |

No cut in the add-on is a prism. From the volume each cut removes (notes, open problem 24), taken as a duct whose area grows evenly to the outer face:

| Cut | Volume removed | Duct-equivalent depth | A4 against the fan cut |
| --- | --- | --- | --- |
| Plain prism, the kernel's model | 251 mm³ | 4.00 mm | −166 cents |
| Fan, the default and the Stage 1 stubs | 548 mm³ | 2.05 mm | 0 |
| Ellipse P1 | 474 mm³ | 2.30 mm | −23 cents |
| Ellipse P3 | 458 mm³ | 2.37 mm | −29 cents |

The estimate counts the ramp side as duct, so the absolute numbers are too large. The difference between the cuts is the point: it is of the size of Gate 3's whole tolerance (±15 cents), and of the −38 cents that a 4.4 % change of η_w gives in the synthetic Stage 3.

What follows:

1. **An ellipse body must not take η_w from a fan stub.** Put the cut style and its numbers (opening per side, shelf angle and land, flare exponent) into the hashed values. This is open problem 24; the estimate above is the reason it cannot wait.
2. **Stage 1 needs a stub with the cut the bodies will carry**, and it is worth keeping the fan stub beside it: the pair measures what a cut is worth, which nothing in the repository can compute.
3. **`wall_at_window_mm` is no longer the throat.** With a dish, the throat is the lip land plus the flare. The 3 mm wall option of 17 November was a way to shorten the throat; the cut now does that by another route. The two should not be stacked without a stub.
4. **This is also why large chambers are possible.** A window of 63 mm² with a 2.5 mm effective throat tunes 92 cm³. A deep dish on a thick wall is how a maker drives a chamber of 100 cm³ with a window of ordinary proportions (section 6.3).

**Verdict:** the choice of the ellipse loft stands, and P3 or P1 is a matter of looks. The condition is the hash and a stub of its own.

### 3.4 The smooth cavity inside

- **Supported at the voicing.** Heuer bevels the inside of the window and wants "no extra material in this area", with the lip "nicely beveled underneath" (#6, #8). The pocket blend removes the 0.3 mm step behind the lip. It is the same direction.
- **The blend shortens the flat under the lip from 3 mm to 1.5 mm.** Past that the ceiling curves toward the chamber. On the NBN and the sample the labium's inner face falls away from the jet at 16°; in the add-on it runs with the jet and then bends into its path. A level or outward jet meets that. This is the same question as section 3.1 seen from the wall's side.
- **The blend changes the throat a little and is in no hash.** Hash it with the cut.
- **The seed body's cavity is convex everywhere**, as both ceramic outlines are. That part of "smooth" is well supported (doc 07 §3.4).
- **A professional chamber is not smooth everywhere.** The Spencer's thumb-face half has three pockets with walls between them, thin lips at the thumb holes and a solid tail. So smoothness is a rule for the voicing and the outline. It is not a rule the references follow for the whole inside, and the solid tail is a lever the add-on does not have (doc 07 §3.9).

**Verdict:** keep it. It needs no new stub of its own if it is hashed and built into the ellipse stub.

## 4. The work of 15–16 November, challenged

| Item | Verdict | Challenge |
| --- | --- | --- |
| The seed body as P4 (docs 07, 08) | **Holds.** Two ceramic outlines give the same body within 3 mm, and its chamber (132 mm) is the Spencer's (131–136 mm) | The fit takes a ceramic *outer* outline as the skin of a 4 mm print, so the printed cavity is fuller than the ceramic one. Doc 07 says so. The seed carries the Miracle's hole layout, not the layout of the instruments it is shaped on |
| The seed at 80 cm³ | **Open.** | The Spencer is about 70–77 cm³ and the Songbird about 100 cm³. 80 cm³ is between them, so it is a fair middle. The claim that 80 cm³ is "the top of the proven band" is withdrawn (section 6.3) |
| Rows of holes 18–28 mm apart (`ergo_hand_offset`) | **Does not hold for round bodies.** | Both professional alto C instruments have 36–42 mm and would warn. The limit came from flat bodies. On a body whose thickness is 0.8 of its width the rows sit on the flanks. Measure the distance along the surface, or set the limit by the roundness of the body |
| "The kernel makes the left pinky hole 7.1 mm; the references use 4.5–6.1" (doc 06 §3.6) | **Explained.** | The kernel sizes that hole for A5. On an instrument it is the F6 hole. The mismatch was the fingering order (section 6.1), not the hand |
| Subhole slides 9.5 and 7.5 mm | **Holds.** | The two alto C instruments have 10.3–10.6 and 7.5–8.3 mm. A left slide of 10 mm would sit nearer both. Open problem 19 clears at 80 cm³ in the Asian order without touching the slide |
| Cavity-mode pass line at 1.3 × F6 | **A guess, as its documents say.** | Two instruments that are sold as playing to F6 sit under it (1.19 and 1.27), and the Spencer model spans 1.21–1.48 with the reading of one photo. `needs_fem` on the flatter seed (1.29) is not evidence against it. Keep the number as a report; do not choose bodies by it |
| P3 stashed, old P4 dropped | **Holds.** | None |
| P0 as the control egg | **Holds.** Heuer: "generally kind of a roundish type shape" | None |

One correction to the record. The Miracle report says its order of opening "is the standard Asian 12-hole linear fingering, the same one the repo uses", and that a search over all orders "cannot pick a clearly better order". The order the repository uses is not the Asian one, and the Asian one ranks 37th of 720 on the Miracle's holes against 629th for the repository's.

## 5. The research of 17 November, challenged

| Decision or finding | Verdict | Evidence beyond the review itself, and challenge |
| --- | --- | --- |
| Labium −0.2 mm, coupons 0 and −0.35 mm, never positive | **Holds.** | Three videos; the board's end-on drawing; the Eclipse section, where the lip sits a little under the middle of a 1.0 mm exit. Under a tilted jet the coupons do not apply (section 3.1) |
| Teardrop, broad end at the windway | **Holds by majority.** | Heuer's model, the Miracle, V0N3, the Eclipse. The NBN is the other way round (a U with its round end at the labium), so "resolved" is too strong a word |
| Window length 9.65 mm | **Holds.** | Miracle 10.0, Eclipse 9.4, NBN 11.3 mm |
| Exit height 1.20 mm | **Holds as a middle value.** | Heuer's chart 1.14, his own builds 0.8–1.0, Eclipse 1.0, NBN 2.35 mm |
| Break pressure recorded | **Holds.** | The manometer reads the jet's pressure plus the loss in the slot, which is about 36 % of the jet's on the low notes with the kernel's slot (section 6.5). Compare break pressures only between stubs with the same slot |
| η_w band 0.85–0.95 "measured on real instruments" | **Overstated.** | The ECAN3 values assume the CAD plays in tune; the Miracle value has ±0.08. And η_w depends on the cut (section 3.3), so one band cannot describe the fan, the ellipse and the references' dishes at once |
| "Heuer's throat is about 6 mm deep" | **Overstated.** | The quarter inch is from the top of the body to the exit. His model's dish thins the wall around the window itself |
| Ladder 65 / 80 / 95 cm³, 125 dropped | **The drop holds; two of its three reasons do not.** | No reference is above about 116 cm³, and a print costs filament: that holds. "The holes break at about 74 cm³" is an artefact of the fingering order and of the passive model (section 6.2). "The window turns wider than long at 88.6 cm³" assumes a 4 mm prism; a dish moves that point (section 3.3) |
| P0-88 as the prediction body | **Weaker test than the one it replaced.** | 88 cm³ lies between two ladder steps. The notes say a wrong k_hole costs 5–22 cents there against 10–27 at 110 cm³. Gate 3 is easier to pass and proves less. A prediction above the ladder (105–110 cm³) is the stronger test, and the Songbird says such a body is real |
| 3 mm window wall option | **Partly overtaken.** | It shortens the throat; the cut does the same (section 3.3). Stub V-a3 can be a stub with 3 mm everywhere, since a stub has no holes |
| Hole undercut (proposal B) on hold | **Reaffirmed, for a new reason.** | In the Asian order, and at the makers' ratios, no hole is over its pad limit at 80 cm³ (section 6.2). The undercut is not needed to get there |
| "Hole positions are free" | **Holds for comfort; not shown for pitch.** | The makers' pattern (section 6.2) could be position, pressure or undercut. Stage 2 is the measurement |

**What the review missed.** (1) The fingering chart. Doc 02 Q3, doc 05 G6, the Miracle report and the ECAN3 report each list "confirm the fingering chart" as open; six Pure Ocarinas articles were read in full on 17 November, and the one on fingering was not among them. (2) The two professional volumes were never added to doc 04's table of analysed instruments, so "every alto C holds 60–80 cm³" stayed in the plan a day after the Songbird was measured.

## 6. The kernel, challenged

### 6.1 The order in which the holes open

| Note | Parameter file | Asian system | Italian system |
| --- | --- | --- | --- |
| B4, C5 | left subhole, right subhole | the same | the same |
| D5–G5 | R pinky, R ring, R middle, R index | the same | the same |
| A5 | **L pinky** | L ring | L ring |
| B5 | **L ring** | L middle | L middle |
| C6 | **L middle** | L index | L index |
| D6 | **L index** | L thumb | L thumb |
| E6 | **L thumb** | R thumb | L pinky |
| F6 | **R thumb** | L pinky | R thumb |

The source says of the left hand: "the first finger to lift is the ring finger, not the pinky! The pinky finger stays down to support the instrument", and gives the top of the scale as left thumb, right thumb, left pinky. The subhole order of the parameter file agrees with it.

The measured holes of each instrument, in the kernel's scale model under each order (A4 exact, volume fitted, k_hole 1.0):

| Instrument | Parameter file: rms, rank of 720 | Asian: rms, rank | Italian: rms, rank |
| --- | --- | --- | --- |
| Miracle | 108 cents, 629 | **90 cents, 37** | 103 cents, 453 |
| Spencer | 59 cents, 115 | **57 cents, 55** | 63 cents, 263 |
| Songbird Alto C | 54 cents, 167 | **47 cents, 11** | 59 cents, 323 |

The gain in rms is small, because the photo diameters are rough and the model leaves a tilt (6.2). The rank is the stronger sign: the same order moves to the top few per cent on three instruments from three makers.

What the kernel cuts at 80 cm³ (print at k_hole 0.8 / nominal at 1.0, mm):

| Order | L pinky | L ring | L middle | L index | L thumb | R thumb | Over the pad limit, nominal | Edge gap, left subhole to L ring |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Parameter file | 7.1 / 7.9 | 8.4 / 9.3 | 5.8 / 6.3 | 10.8 / 12.1 | 12.7 / 14.4 | 8.6 / 9.5 | L index, L thumb | 3.63 / 3.05 mm |
| Asian | 8.6 / 9.5 | 7.1 / 7.9 | 8.4 / 9.3 | 5.8 / 6.3 | 10.8 / 12.1 | 12.7 / 14.4 | L thumb (by 0.1 mm), R thumb | 4.26 / 3.78 mm |

**What it touches.** Six diameters on every body with holes; the tube plan; the edge gaps and with them open problem 19; every `ergo_*` number that depends on a diameter (rest space past the left pinky, leans); the P0 taped layout; the Stage 2 and Stage 3 reports; the synthetic measurement files and the constants file; the measurement template, which lists the notes in the order they are played. The physics does not change: the lumped model does not care which hole opens. A body built in the present order would play in tune only with a fingering nobody uses.

**What it does not touch.** Stage 1. The stubs have no holes.

**The owner's choice.** Asian, Italian, or keep the present order on purpose. The Italian system gives the pinky the E6 hole, which the source calls "a lot bigger". I recommend Asian: it is what the Spencer, the Songbird and the Miracle are built for.

### 6.2 The size of the holes against three makers

The measured hole over the kernel's hole for the same note, at each instrument's fitted volume, Asian order, k_hole 1.0:

| Instrument | Fitted V0 | Subholes | Right hand, D5–G5 | L ring, middle, index, A5–C6 | Thumbs, D6–E6 | L pinky, F6 |
| --- | --- | --- | --- | --- | --- | --- |
| Miracle | 80 cm³ | 1.00 | 1.21 | 0.88 | 0.77 | 0.47 |
| Spencer | 77 cm³ | 0.85 | 1.13 | 1.02 | 0.83 | 0.75 |
| Songbird Alto C | 101 cm³ | 1.04 | 1.07 | 1.05 | 0.79 | 0.58 |

- **The ratio falls as the scale rises, on all three.** With A4 on pitch and the measured holes, the passive model reads the middle of the scale about 60–150 cents sharp and F6 about 80–160 cents flat. A player raises the breath pressure up the scale, and the pitch of an ocarina rises with pressure; the makers tune for that. The kernel's "Known limits" name the omission. This is its size.
- **The position factors will carry it.** The fitter estimates one factor per hole name and shape, so Stage 2 measures this pattern. The prior of 1 for every hole is what is wrong, and the prior decides the first prints.
- **The first-print rule cuts the wrong way at the top.** Holes are printed at k_hole 0.8 "so that notes err flat and reaming can fix them". The kernel's left pinky hole at 80 cm³ is 8.6 mm at k 0.8; the makers' ratio puts it near 4.5–7 mm. That note will be sharp, and a reamer cannot make a hole smaller. Stage 3 reprints the bodies, so nothing is lost but the stated reason.
- **The pad limits.** At the makers' ratios the Asian order gives, at 80 cm³, thumbs of about 9.7 and 11.5 mm and no finger hole over 10 mm. The two ceramic instruments confirm it from the other side: rims of 12 ± 2 mm (Spencer) and about 14 mm (Songbird) under the thumbs, and finger rims up to 9.8 and 11.6 mm. The stage reports' block of "expected failures" describes the kernel's prior, not an instrument.
- **Two holes go against the trend on all three**: L middle is smaller than the kernel's (0.65–0.81) and L index larger (1.12–1.34). The kernel gives B5 a whole-tone hole and C6 a semitone hole; the makers even them out. I have no explanation; a cross-fingering or the position of the two holes are candidates.

**Proposals.** (a) Give the position factors a prior from the three instruments for the first print of the bodies with a hand layout, and keep P0 at a prior of 1 as the control; or (b) keep 1 everywhere and state in the Stage 2 report that the top notes are expected sharp. Either way, remove "the design breaks at about 74 cm³" from doc 04.

### 6.3 The volume band

| Instrument | V0 | How |
| --- | --- | --- |
| Doc 04's table (baseline, ECAN3 OOT, V0N3, Miracle, Eclipse) | 62–77 cm³ | STL, photo |
| Miracle, holes in the Asian order | 80 cm³ | this document; its own report gives 65–75 and 82 |
| Spencer | 70 cm³ (65–80); 77 cm³ by the holes here | mass, thickness, holes |
| Songbird Alto C | 92–116 cm³ at 170 mm; 101 cm³ by the holes here; 77 cm³ or more at any allowed length | holes, outline |

The Songbird's length is an estimate, and one of its four supports uses the kernel's own range identity. The support that does not (the Tenor A divided by three semitones, 171 mm) agrees. So a professional alto C at about 100 cm³ is likely, not certain. It is enough to say that 95 cm³ is not an excursion, and that a prediction body above the ladder would be a body that exists.

### 6.4 The window

Covered in section 3.3. In the kernel's terms: G_w = A / (t + k·d_eq) with t the wall is a model of a prism that no cut builds; η_w is the constant that absorbs the difference, and it is a property of the cut. The honest form is one η_w per hashed voicing, with the cut in the hash. The rule that the window's *length* is fixed and its *width* grows with volume (Heuer #2) is unaffected.

One check does nothing: `wh_ratio` is the window length over the exit height. Both are fixed by the rating, so it is 8.0 at every volume and can never fail. The ratio that changes with volume is the slot's width over its height, 5.8 at 65 cm³ and 9.3 at 95 cm³.

### 6.5 The windway slot

| | Height, mouth end → exit | Width, mouth end → exit | Length |
| --- | --- | --- | --- |
| Kernel rule | 1.56 → 1.20 mm (taper 1.3) | constant, the window's width | 30 mm |
| Owner's sample | 3.0 → 1.3 mm | 10 mm, constant | 36 mm |
| Miracle | 2.5–3 mm at the entrance | about 9 mm | 30–32 mm |
| ECAN3 Eclipse | 3.7 → 1.0 mm | 10 → 7 mm | 40 mm |
| NBN | 4.5 → 2.35 mm | 12.6 → 9.5 mm | 33 mm |

- The taper of 1.3 is a "starting value" in the parameter file. Heuer says "taper it down just a little bit" (#8), which fits it; his airway is a stick pressed into clay. Every measured slot in the library is two to three times taller at the mouth end.
- Laminar loss in the slot, entrance losses left out: 47 Pa at a 15 m/s jet with the kernel's slot, 36 % of the jet's own pressure; 14–22 Pa (11–17 %) with the sample's or the Miracle's. A thin slot costs breath on the low notes, and it holds condensation; the second point is my own engineering judgement, not a source's.
- Both CAD models narrow the slot in width as well. The kernel does not.
- `windway_inlet_height_mm`, the width and the length are hashed. Changing them after Stage 1 means new stubs.

**Proposal:** a mouth-end height of about 3 mm (a taper near 2.5), decided before the stubs. It also gives the tilt more to work with inside the neck.

### 6.6 What holds

The Helmholtz core and the split of the end correction; the teardrop rule and the fixed window length; the labium default; the hash as the key of the calibration; the hole solver itself (it is the order and the prior that are challenged, not the mathematics); the volume and topology checks of the add-on, which measure the exported file.

## 7. The test suite, challenged

| What the suite does | What it does not do |
| --- | --- |
| `TestDoc04Table`, `test_stage_reports`: the kernel reproduces the tables of doc 04, and the committed reports reproduce the kernel | Compare the kernel with any made instrument. The numbers of doc 04 come from the kernel, so these tests close a circle |
| `TestRecoveryNoiseFree`, `TestKHoleProfile`, `TestNoise`: the fitter recovers the constants of synthetic bodies | Test the fitter on data that the model cannot produce. The synthetic truth is the kernel's own model with factors per hole; a pitch that rises with pressure is not in it |
| `TestHash`: the hash changes with the wall, the offset and the window | Change the hash with the cut, the shelf, the tilt or the pocket blend, because they are not hashed |
| `TestEllipseWindowCut`: the cut has the window, lip and ramp of the record | Say anything about its conductance (it cannot; a stub must) |
| `TestReferenceRows` (ergonomics): reproduces the Miracle and ECAN3 rows | The same for the Spencer and the Songbird, which contradict one limit |
| Nothing | Tie the fingering order to a source |

Tests worth adding, each small:

1. **The fingering order equals a named chart**, with the source in the test's docstring, and the left pinky opens last.
2. **A reference regression**: the three instruments of `kernel_vs_references.py` with wide bounds (rank of the adopted order in the top 10 %; thumbs between 0.7 and 0.9 of the kernel's). It records what the passive model misses, so a later change that makes it worse is seen.
3. **The hash changes** when the cut style, any cut number, the tilt, the pocket blend or the slot changes; and a stage refuses to take η_w from a hash whose cut differs.
4. **`windway_floor_lip` on every stage body** whenever a tilt is set, not on P4-80 alone.
5. **The fitter against a tilted truth**: synthetic bodies whose pitch rises with pressure, to see where the tilt goes. The profile estimate of k_hole assumes one factor per hole name over the ladder; a tilt may land in k_hole instead.
6. **`wh_ratio` replaced** by a check that can fail (the slot's width over its height).

## 8. Decisions for the owner

Before any body with holes is built again:

1. **The fingering system**: Asian (recommended), Italian, or the present order on purpose. Scope: six lines of `params/alto_c_12hole.toml`, then the stage reports, the synthetic files, the hole-layout tests and docs 03–04 are regenerated. **Answered and done on 2026-11-18: Asian, with the split subholes kept.**
2. **The prior of the position factors** for the first prints: 1 everywhere, or the makers' pattern on the hand bodies (section 6.2).

Before the Stage 1 stubs are printed:

3. **What "lowered" is measured against**: the neck, or the labium's inner face (section 3.1). This decides the sign of the tilt.
4. **The windway slot**: the mouth-end height (I propose about 3 mm), and whether the width narrows. **Decided and done on 2026-11-18: 3.0 mm at the mouth end. The width does not narrow.**
5. **The hash**: the cut, the shelf, the tilt and the pocket blend go in (recommended). **Decided and done on 2026-11-18; the style and the stance of the neck are hashed too.**
6. **The stub set**: the fan stub and one stub with the full chosen voicing (ellipse P3 or P1, neck, blend, the tilt as answered in 3). Stub V-a3 as a 3 mm stub if the wall option is kept. **Decided and done on 2026-11-18: V-a carries the build (ellipse P3, standing neck, blend), V-af the plain build. V-a3 still fails its outside keep-out, now by 2° (47° against 45°).**

Can wait:

7. A prediction body above the ladder (105–110 cm³) in place of, or beside, P0-88.
8. The row limit for round bodies; a left slide of 10 mm; the neck width as its own number. **The slide: decided and done on 2026-11-18, 10 mm.**
9. Local wall thickness around the voicing, if more than about 2.5° of tilt is wanted.

## 9. Limits

- **Photo measurements.** The Miracle's holes are dark openings at ±0.3 mm. The ceramic rims are ±15 %, taken 1 mm smaller as bores; the Spencer's thumb holes are 12 ± 2 mm and were set to 12; the wall at the ceramic holes is assumed 5 mm. The patterns of section 6.2 are read across three instruments for that reason. No single ratio is reliable.
- **The fingering source is one maker's site**, read through a fetch on 2026-11-18. It describes the Asian and Italian systems for single-chamber instruments; it is consistent with the hole sizes of all three references. The charts shipped with the Spencer, the Songbird or the Miracle were not seen.
- **The throat and slot estimates are duct formulas.** They are not models of a jet or of a labium, and the throat estimate overstates the effect of a cut. They show which quantities are large enough to need a stub.
- **The direction of the jet** on the sample and the NBN is taken from the measurements of Window_cutout.md, which I did not repeat; the Eclipse and the add-on were read on the section pictures.
- **The Heuer series was read as excerpts.** A sentence that looks decisive in a table may have a context that the excerpt does not show.
- Nothing here was printed, played or measured with a tuner. Every challenge ends in a stub or a Stage 2 body, not in a correction.
