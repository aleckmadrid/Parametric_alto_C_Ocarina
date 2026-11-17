# 01 · Source review: what holds, what doesn't, what was added

This review covers the three input documents (copies are in [`references/`](../references/)) and the extra sources consulted to extend them. Each claim is marked:

- **Verified**: recomputed with [`kernel/`](../kernel/) or confirmed in a primary source
- **Consistent**: agrees with independent sources but is not proven
- **Unverified**: plausible, with no source available in this session
- **Wrong**: contradicted by arithmetic or by the source data

## Summary

| Source | Role | Reliability | Verdict |
| --- | --- | --- | --- |
| [Build plan](../references/build-plan-original.md) | Main document: architecture, math, roadmap | High | All formulas and worked numbers reproduce. Six issues need amending; see [§1.2](#12-issues-found-in-the-build-plan). |
| [Heuer Video #2: alto C tolerances](../references/heuer-video2-alto-c-tolerances.md) (Gemini summary) | Voicing dimensions for the #3 C (alto C) | High for the numbers, medium for the interpretations | The chart values match the build plan exactly. A few explanations were added by Gemini and are not on the chart. |
| [Heuer series overview](../references/heuer-series-overview.md) (Gemini summary) | Per-video topic list for videos #1 to #8 | Low | Only the video titles could be confirmed. The topic descriptions are unverified, and two statements are physically wrong. |

The voicing numbers are trustworthy because two independent routes give the same values: the user's own transcript (used by the build plan) and Gemini's summary. The per-video topic list should be treated as a set of hypotheses until someone watches the videos.

---

## 1. Build plan (main file)

### 1.1 Numbers recomputed

All of these came out of `kernel/alto_c_study.py`, section A ([generated output](generated/study-output.md)).

| Claim in the plan | Plan value | Recomputed | Status |
| --- | --- | --- | --- |
| Speed of sound at 27 °C, `331.3·sqrt(1+T/273.15)` | 347.3 m/s | 347.3 m/s (ideal-gas mixture model also gives 347.3) | Verified |
| Diameter inversion `d = (2/π)(Gk + sqrt(G²k² + πGt))` | — | Algebraically exact; round trip to 1e-12 m | Verified |
| Thin-plate end correction is the k = π/4 limit | 0.785 | Gives G = d, Rayleigh's conductivity for a circular hole | Verified |
| Appendix example: ηG_w, V, ΣG/ηG_w | 3.95 mm, 44.0 cm³, 5.35 | 3.94 mm, 44.0 cm³, 5.35 | Verified |
| Appendix hole diameters (9 holes) | 2.87 … 8.40 mm | Identical to two decimals | Verified |
| Alto table: 38 mm² window, 1.6 mm wall → V0, ΣG | 75 cm³, 43 mm | 75.3 cm³, 43.3 mm | Verified (all four rows) |
| Range ratio for A4..F6 / C5..F6 | 9.1 / 6.1 | 9.08 / 6.13 | Verified |
| 10-hole chamber relative to the 12-hole chamber (same window) | 0.71 | 0.707 | Verified |
| Sensitivity constant | 866 | 865.6 = 1200/(2 ln 2) | Verified |
| +1 % volume / +1 °C | −8.6 / +2.9 cents | −8.61 / +2.88 cents | Verified |
| Top hole 8.4 → 8.3 mm | −2.9 cents | −2.92 cents | Verified |
| 32-gon area deficit | 0.64 % | 0.64 % (64-gon: 0.16 %) | Verified |
| 12 chimneys of 0.2 cm³ in 150 cm³ | ≈14 cents | 13.96 cents | Verified |
| Half wavelength at E6 | 132 mm | 131.7 mm | Verified |
| Heuer window/exit ratios | 6.7 … 16.7 | Identical | Verified |
| Pure Ocarinas: 12-hole alto C sound hole 7–9 mm, 10-hole 8–10 mm | — | Page states "about 7 and 9 mm in diameter" | Verified (it is the author's experience, not a measurement) |
| Pure Ocarinas: 0.9 cents/°C measured | — | Page says so, with the caveat "to the extent that I have been able to measure it" | Verified |

### 1.2 Issues found in the build plan

1. **The prior for window efficiency η_w is too narrow and contradicts itself.** The plan first guesses 0.6–0.9, then a cross-check against maker data asks for 0.9–1.0. One external data point, the compressible LES ocarina study (Kobayashi et al. 2009), implies η_w ≈ 0.48 for a zero-thickness window and 0.63–0.78 if the window wall is 1.5–3 mm thick. That study does not state the wall thickness. The realistic prior is therefore **0.5–1.0**. Required chamber volume is proportional to η_w, so for the baseline design the volume ranges from **34 to 69 cm³**. A 10 % error in η_w moves every note by about 83 cents. This is the dominant design uncertainty, and the reason the calibration print comes before any sculpting. → [03 §6](03-parametric-findings.md#6-sweeps)
2. **The λ/3 validity rule flags most transverse alto C shapes.** At F6 the rule allows an internal length of only 82.9 mm. A typical transverse chamber of 3:1.6:1 proportions at the required volume is 87 mm long, and an elongated one is 96 mm. Egg-shaped chambers up to about 2.2:1.5:1 pass. The rule is not wrong, but the plan never says it **constrains chamber shape**. Phase 3 should use a compact egg, and the add-on should report `c/(2L) ÷ f_top` live. → [03 §8](03-parametric-findings.md#8-lumped-model-validity-chamber-shape)
3. **The window throat is booked in two places.** The plan counts the window wall thickness in the window's neck length (inside G_w), and also includes the window throat in V0. Open-hole chimneys are treated as neck, so the consistent rule is that **the window throat is neck and is excluded from V0**. The difference is small (about 0.11 cm³, roughly 1.5 cents), but calibration and design must use the same convention, or the error appears twice.
4. **The 3 mm minimum hole size conflicts with the subholes.** On a 3 mm uniform wall the solver gives 2.56 mm (sub 1), 1.86 mm (sub 2) and 2.64 mm (the F5 semitone hole). The plan's remedy is a longer chimney, but it gives no numbers. Sub 2 needs a **9.3 mm** chimney to reach 3 mm, which is only practical as an inward boss. This needs an explicit rule. → [03 §6.2](03-parametric-findings.md#62-chimney-height-and-the-subhole-problem)
5. **The chimney-volume correction matters more on a smaller chamber.** The plan's 14-cent example assumes 150 cm³. The baseline alto chamber is about 62 cm³, so ignoring chimney volume makes the top note **12.5 cents sharp**, even though its chimneys are smaller. Keep the correction in the solver; it is not optional.
6. **One cited cross-check is internally inconsistent.** The planning workbook (130 cm³, 9×5 mm window, 4 mm wall) cannot reach A4. Our model gives 320 Hz (−550 cents), and the workbook's own formula gives 406 Hz (−141 cents). Its end correction is labelled "flanged" but uses the unflanged coefficient 0.6. **Drop it as a reference point.**

The rest of the plan stands as written: the architecture, the locked/linked split, the safeguards and the validation tiers.

---

## 2. Heuer Video #2: alto C tolerances (Gemini summary)

| Item | Status | Note |
| --- | --- | --- |
| Airway exit 0.045 in = 1.14 mm | Verified | Matches the build plan's chart. |
| Window, fired 0.38 in = 9.65 mm; wet 0.428 in = 10.87 mm | Verified as written on the board; **the wet value is inconsistent** (see §5) | On the board the wet/fired ratio is **1.060 for six of the seven sizes** and 1.126 only for #3 C. "Add 12 %" generalises the one odd row. The fired 0.38 in agrees with the tolerance row, so the fired value is the one to use; printing is not affected. |
| Tolerance band 0.32 / 0.35 / 0.38 / 0.41 / 0.44 in | Verified | Identical to the build plan's table. |
| "Window size = airway exit to labium lip" | **Verified (transcript, §5.1)** | Heuer, reading the fired column: "the distance … from the airway exit to the labium lip will be less than a quarter of an inch … all the way up to a full inch on a big bass ocarina". Also consistent with the Miracle (10.0 mm on a 12-hole alto C). |
| Credit card 0.03 in = 0.76 mm | Verified | This is the ISO/IEC 7810 ID-1 card thickness. |
| 12-hole alto C, "up to 21 chromatic notes" | Verified | A4..F6 is 20 semitones, so 21 notes. Pure Ocarinas also confirms that two subholes extend a 10-hole down by three semitones. |
| "Keep the window at 9.65 mm" | Conflicts with the plan | The build plan starts at 8.89 mm (soft) as a safeguard for the high notes. The unified plan resolves this with voicing coupons at 8.9 / 9.3 / 9.65 mm. |
| "Too large: notes easily overblow or fail to sound" | **Not in the transcript** | Heuer says of both X limits only that the ocarina "is likely not to play very well or not be able to play at least one octave". The overblowing part is Gemini's. |
| `[cite: 1]` markers | Artefact | Gemini citation tokens with no content. |

**Added analysis** ([03 §3](03-parametric-findings.md#3-voicing-scaling-from-heuers-chart)): at a fixed Strouhal number, blowing pressure scales with W². Heuer's soft–loud band is ±0.76 mm (±7.9 %), which corresponds to **0.85×–1.16×** the medium pressure. The "X" limits sit at 0.71× and 1.34×. This gives a physical reading of his Soft/Medium/Loud labels.

---

## 3. Heuer series overview (Gemini summary)

**What could be checked.** YouTube oEmbed confirms that all eight video IDs exist, are uploaded by Chris Heuer (@ocarinaone), and carry titles of the form "Let's learn to make ocarinas Video #N". No description, transcript or chapter list could be retrieved. The topic given for each video is therefore **unverified**.

| Statement | Status | Why |
| --- | --- | --- |
| Video #1: pitch is set by "the ratio of internal volume to the total area of open fingerholes" | **Not in the transcript** (§5.2) | Video #1 explains the air reed and that a larger chamber gives a lower pitch; it does not mention finger holes. The physics: pitch goes as sqrt(conductance / volume), and conductance is area / (chimney + end correction), not area. |
| Video #2: chart for sizes #1 to #7, and a 0.03 in step moves Medium to Soft or Loud | Verified | Consistent with source 2 and the build plan. |
| "Proportional scaling": window, exit and labium scale down proportionally with volume | **Qualitative only** | Heuer does say it in Video #2 ("needs to be in proportion to the size of the chamber"), but loosely: his own chart shows W ∝ f^−0.75 (R² = 0.99), not f^−1. W/h rises from 6.7 to 16.7, and exit height moves in three steps. |
| Video #3: voicing tools and technique; "the labium angle must be precisely tuned" | **Partly** (§5.2) | The tools are right (needle tools, a #11 scalpel, airway sticks). No labium angle is given; what he sets precisely is where the lip sits relative to the airway. |
| Video #4: uneven wall thickness warps the voicing | Consistent | This is a clay-drying effect. For printing, the matching rule is a minimum wall for airtightness. |
| Video #5: a teardrop window keeps the 12-hole upper register stable | Consistent / unverified | Pure Ocarinas: teardrop holes are "very pure" and found on Asian ocarinas, and smaller sound holes help high notes. The video's content itself is unverified. |
| Video #7: larger chambers need wider exits and longer windows | Consistent | Matches the direction of Heuer's chart. The "to prevent overblowing" mechanism is unverified. |
| Video #8: small increases in hole diameter "exponentially shift pitch" | **Wrong** | G ∝ d² for long chimneys and G ∝ d for thin plates, and f ∝ sqrt(G_tot), so the effect is sub-quadratic and never exponential. The practical advice (ream gradually) is still right, because 0.1 mm moves a note by 2–11 cents ([03 §7](03-parametric-findings.md#7-sensitivities-and-tolerance-budget)). |
| "Scale wet clay up by 12 %" | **Not from Heuer** | The Video #2 transcript never mentions shrinkage, and the board uses ×1.06 for six of seven sizes (§5). This does not apply to printing. |

---

## 4. Extended research: what was added

| Source | What it contributes | Used in |
| --- | --- | --- |
| [Pure Ocarinas, How chamber shape affects range](https://pureocarinas.com/ocarina-chamber-shape-range-chamber-volume-bypassing) | A hole cannot usefully exceed the chamber's internal diameter. "Bypassing" (author's hypothesis) may help high notes in narrow chambers. | Constraint C5; open question Q6 |
| [Pure Ocarinas, Identifying playable ocarinas](https://pureocarinas.com/identifying-playable-ocarinas) | Alto C sound hole 7–9 mm (12-hole), 8–10 mm (10-hole). A good instrument overblows at least a semitone without screeching. Equal-size holes mean untuned. | Voicing check; Phase 3 gate |
| [Pure Ocarinas, Breath curves](https://pureocarinas.com/ocarina-breath-curves) | The natural breath curve is "approximately exponential"; its steepness depends on volume, sound hole, window length and hole count. | Breath model p ∝ f^α ([03 §4](03-parametric-findings.md#4-jet-strouhal-and-the-breath-curve)) |
| [Pure Ocarinas, How ocarinas work](https://pureocarinas.com/how-ocarinas-work) | Voicing neck (set-back sound hole) gives headroom on high notes. Soprano 12-hole reaches about 21 clean notes; bass about 18. | Safeguard 3 |
| [Pure Ocarinas, Warm or cold environments](https://pureocarinas.com/ocarina-tutorial/playing-ocarinas-in-warm-or-cold-environments) | About 0.9 cents/°C measured on room temperature. Humidity lowers pitch (author's claim). | Design-temperature choice |
| [Pure Ocarinas, 10- vs 12-hole](https://pureocarinas.com/differance-10-hole-12-hole-ocarina) and [timbre](https://pureocarinas.com/ocarina-playing-characteristics-timbre) | The 12-hole has a steep pressure curve with weak lows and airy highs. Only "a small voicing and steep pressure curve" covers the full range. Subhole fingering: C with neither subhole, B with the right one closed, A with both closed. | Fingering table; window-size choice |
| [Kobayashi et al. 2009, LES of an ocarina (arXiv:0911.3567)](https://arxiv.org/abs/0911.3567) | 9.4 cm³ cavity with a 5×5 mm window sounds at 880 Hz against a thin-aperture Helmholtz prediction of 1274 Hz. In 2D, pitch rises with jet speed. | η_w prior ([03 §10](03-parametric-findings.md#10-cross-checks-against-external-data)) |
| [Paley, Bridges 2015](https://archive.bridgesmathart.org/2015/bridges2015-559.pdf) | Hole position does not affect pitch; wind speed does. A second equal hole gives a flatter interval than the first (follows from the square root). The airduct is "remarkably sensitive". | Confirms the model |
| [Francis, UIUC Phys 406 (2012)](https://courses.physics.illinois.edu/phys406/sp2017/Student_Projects/Spring12/Gregory_Francis_P406_Project_Report_Sp12.pdf) | Clay shrinkage moved a whole scale from F to G. One fixed resonance near 1100 Hz appeared in a large ocarina regardless of fingering. | Scaling law f ∝ 1/s; cavity-mode check |
| [UNSW (J. Wolfe), Flute acoustics](https://newt.phys.unsw.edu.au/jw/fluteacoustics.html) and [air speed](https://newt.phys.unsw.edu.au/jw/air-speed.html) | Waves travel along the jet at about half the jet speed. P ≈ ½ρv². For flutes, pressure is roughly proportional to frequency (players also shorten the jet; an ocarina cannot). | Strouhal derivation |
| [Koop ocarina build packet](https://tonykoop.github.io/ocarina/README.md) | Workbook inputs. Found inconsistent (issue 6). | Rejected as a reference |

## 5. Second source review (2026-11-17): Heuer chart re-read, LES paper read in full

Inputs: a frame of Heuer's Video #2 board (supplied by the owner), full text of six Pure Ocarinas articles, the LES paper, the UNSW Helmholtz and flute pages, and web searches. The video's transcript and description could not be read: YouTube served a "confirm you're not a bot" page. The patent page and The Ocarina Network refused automated fetches.

**The board** (fired values unchanged from §2):

| Size | Exit in | Wet in | Fired in | Wet/fired |
| --- | --- | --- | --- | --- |
| #1 C | .03 | .212 | .20 | 1.060 |
| #2 G/F | .045 | .318 | .30 | 1.060 |
| **#3 C** | **.045** | **.428** | **.38** | **1.126** |
| #4 G/F | .045 | .477 | .45 | 1.060 |
| #5 C | .06 | .636 | .60 | 1.060 |
| #6 G/F | .06 | .848 | .80 | 1.060 |
| #7 C | .06 | 1.06 | 1.0 | 1.060 |

| Finding | Status | Consequence |
| --- | --- | --- |
| Heuer's chart uses **6 % shrinkage** (×1.06) for six sizes; only #3 C is ×1.126. 6 % fits earthenware (6–8 %), 12 % fits stoneware (11–13 %) ([Digitalfire](https://digitalfire.com/glossary/60), [Valentine Clays](https://valentineclays.co.uk/pages/shrinkage-rates)). | The #3 C wet value is either a board error (×1.06 gives .403 in wet) or a different clay. | None for printing. The fired .38 in is centred in his own tolerance row, so 9.65 mm stays the medium length. |
| A power law through the other six sizes (W ∝ f^−0.75) puts the #3 C fired window at **0.357–0.361 in (9.1–9.2 mm)**, between Soft and Medium. | Computed from the board. | Heuer's curve favours the soft end of his band for the alto. Doc 02's coupon sweep (8.9 / 9.3 / 9.65 mm) covers this; doc 04 Stage 1 tests only 9.65 mm. |
| **LES paper (Kobayashi et al. 2009), read in full.** The 880 Hz is not a measurement: it is the nominal lowest note (A5) of a commercial ocarina of "almost the same" size. The run lasted 5 ms at a fixed 10 m/s jet, and the authors say the oscillation "has not been grown sufficiently". No wall thickness is given. Its end-correction result (α ≈ 2.87) is from the 2D model. | Weak as a calibration point. | The η_w lower bound of 0.5 (A1, R11) rests mainly on this paper. Real instruments give 0.86 (V0N3), 0.89 (Eclipse) and about 0.9 (Miracle). A realistic prior is **0.85–0.95**, which narrows the baseline volume range from 34–69 cm³ to about 58–65 cm³. Calibration first still holds. |
| [Pure Ocarinas, playing characteristics](https://pureocarinas.com/ocarina-playing-characteristics-timbre): long narrow sound holes give a steep breath curve and a large range; wide short ones a flat curve and a smaller range; "only designs leaning towards a pure sound, with a small voicing and steep pressure curve can sound cleanly over the full range of a 12 hole". 12-holes are usually tuned with an "irregular pressure cut" on the lowest notes. | Maker's experience (opinion, consistent across articles). | Supports the 65–95 cm³ ladder, the 3 mm window wall at 95 cm³ (keeps the window longer than wide) and the medium-or-soft length, not loud. The pressure cut means the subhole notes (A4, B4) may want a lower pressure than the smooth curve of doc 03 §4. |
| [Pure Ocarinas, identifying playable ocarinas](https://pureocarinas.com/identifying-playable-ocarinas): 12-hole alto C sound hole "between about 7 and 9 mm in diameter"; the visual size changes with wall thickness. | Maker's rule of thumb; "diameter" is a visual size, not a defined dimension. | The generated windows have d_eq 7.7 mm (65 cm³) to 9.0 mm (80 cm³) at a 4 mm wall: inside the range. 95 cm³ is above it. |
| [Pure Ocarinas, how ocarinas work](https://pureocarinas.com/how-ocarinas-work): pitch rises with blowing pressure; the voicing neck is mostly needed on low ocarinas. [Airy high notes](https://pureocarinas.com/why-ocarina-airy-high-notes): a finger near an open hole flattens it ("shading"). | Maker's experience. | Neither is in the passive kernel. Both are absorbed by the round-1 fit when notes are played at the manometer pressure with fingers lifted clear. |
| [Pure Ocarinas, 3D-printed experiment](https://pureocarinas.com/playable-3d-printed-ocarina): a printed alto C (10-hole, SLS) played its full range; layer roughness in the windway made the tone harsh until polished; holes were printed undersize, reamed, measured and fed back into the model. | One maker's test. | Confirms the plan's method (k 0.8 print diameters, ream, fit). Windway surface finish is a risk; print the body so the windway walls are perimeters, as ECAN3 does (standing on the mouthpiece). |
| ECAN3 OOT (printables/makerworld page, seen only through a search summary): the designer **reduced the windway height from 1.2 to 1.0 mm** for a better breath curve and less airiness. | Second-hand; the page could not be opened. | Challenges the 1.20 mm exit height. 1.0 mm keeps W/h = 9.65 inside the 7–10 band. Worth a stub. |
| [UNSW, Helmholtz resonance](https://phys.unsw.edu.au/jw/Helmholtz.html): end correction about 0.6 r outside plus 1.0 r inside, 1.6 r = 0.8 d in total. | Textbook. | Matches k_window = 0.80. The ECAN3 fit of k_hole ≈ 1.0 on printed holes is plausible for holes in a curved, thick wall. |
| Recorder windways: W/h ≈ 4 ([Price, CU Boulder](https://spot.colorado.edu/~pricej/downloads/JPriceASAOct2014.pdf)); linear jet gain for St ≈ 0.07–0.29 ([arXiv:1502.02170](https://arxiv.org/pdf/1502.02170)). | Recorder data, not ocarina. | Ocarinas run longer windows (Heuer 6.7–16.7, alto 8.4). Keep Heuer's band for the ocarina; the recorder gain band brackets the St ≈ 0.25 design point of doc 03 §4. |

### 5.1 Video #2 transcript (supplied by the owner, 2026-11-17)

The video is a short talk in front of the board. What it settles:

| Topic | Heuer's words (excerpts) | Consequence |
| --- | --- | --- |
| Definition | "the distance … from the airway exit to the labium lip will be less than a quarter of an inch … all the way up to a full inch on a big bass ocarina" (reading the **fired** column) | The chart's window size is the window **length** along the jet, fired. The kernel's `rating_window_mm` uses it correctly. |
| Consistency within a pitch | "once you start looking at a number of different C-pitched ocarinas, let's say in alto … that distance from the airway exit … to the labium lip is very consistent in any … good playing ocarina" | Supports the kernel's rule: the window length is fixed by the pitch class, so extra window area at a larger volume comes from width. |
| Scaling between sizes | "the size of the window … and the distance from the airway exit to the labium lip needs to be in proportion to the size of the chamber … as that chamber gets smaller, the labium lip … and the airway and the window need to get smaller" | Qualitative. His chart is not linear (§3). |
| Soft / Medium / Loud | "if you're shooting for a nice **medium volume** on a C pitched ocarina, that's the number three … .38" ; ±.03 in "is going to affect the sound" | The labels are **loudness** choices; Medium 0.38 in is his stated target for an alto C. The pressure reading of doc 03 §3 (p ∝ W² at fixed St) is our interpretation, consistent with loudness rising with pressure. |
| X limits | "likely not to play very well or not be able to play at least one octave, which I think is a good goal for a beginning ocarina maker" | The X limits are a beginner's one-octave criterion, not a 12-hole criterion. Full 21-note 12-hole voicing is left to a later video. |
| Check on the bench | play the wet ocarina and "by blowing on the low note, test how hard you need to blow to blow that low note away … that'll give you a pretty good indication on whether you're in the range … on the size of the window" ; "whether it's C pitched or not … doesn't matter so much" | A direct voicing test: the pressure at which the **lowest note breaks** tells whether the window length suits the chamber. Not in doc 04 yet; it fits Stage 1 and the Stage 2 speaking-range measurement (record the A4 break pressure on the manometer). |
| Precision | a credit card is "about 3/100 of an inch"; the chart is "available as a PDF" by email | ±0.76 mm moves one loudness step. Printers hold ±0.1 mm, so window length is not the precision risk; the exit height and the labium are. Heuer's PDF could settle the #3 C wet value (0.428 vs 0.403). |
| Shrinkage | not mentioned | The "add 12 %" in the Gemini summary is not from Heuer. |

The transcript does not change the challenge to the η_w prior or the windway-height question (both §5). It weakens the soft-length argument: the power-law fit through the other sizes (9.1–9.2 mm) is only arithmetic, while Heuer names 0.38 in as the alto C medium. Soft stays a loudness and range option, not a correction.

### 5.2 Videos #1 and #3 (transcripts and two board frames, supplied by the owner)

Video #1 boards: "Parts of the Voicing" (airway entrance, airway, airway exit, labium lip, ramp, mouthpiece, mouth or window) and "Window/Mouth shapes" (rectangular/square, semicircular, teardrop, ovular, circular, triangular). Video #3 cuts a large rectangular voicing in clay to show the steps.

| Topic | Heuer's words (excerpts) | Kernel / add-on | Verdict |
| --- | --- | --- | --- |
| Labium height | "as I'm looking through that airway I'm looking for this lip … it's got to line up usually **below center down towards the bottom**" ; "dark on the bottom and light on top" | `labium_offset_mm` = 0.0 (edge mid-height on the windway centre line); coupons ±0.2 mm. Positive = toward the outside. | **Challenge.** Heuer's lip sits on the chamber side of the jet centre, i.e. a **negative** offset in our convention, somewhere between 0 and the floor (−0.6 mm at a 1.2 mm exit). |
| Airway exit depth | "on a normal-sized ocarina you want [the airway exit] about **a quarter of an inch below the top**" | The windway roof is the window wall minus 0.8 mm: 3.2 mm at 4 mm, 2.2 mm at 3 mm. | **Open.** If "the top" is the outer face at the window, his windway-side throat is about 6 mm deep, deeper than ours. It agrees with the Miracle (window wall inferred 4–5 mm) and the voicing-neck idea, and disagrees with the printed ECAN3 windows (2.1–2.4 mm, measured). The Stage 1 wall pair (3 vs 4 mm) is the test; a deeper stub could be added. |
| The drop below the exit | "this wall here, this drop … is either **straight up and down or tilted in** a little bit; you wouldn't want it tilted up … it would affect the sound" | The pocket's back face is vertical at the exit plane, 0.05 mm before it (`voicing_geo.POCKET_BACK_OVERLAP_MM`). | **Reaffirmed.** |
| Window over the chamber | "find this **back wall** … you want it to line up with that back wall … not too far, not too close" ; mark the wall seen through the airway to place the lip | The window opens through a flat pocket straight into the cavity at the voicing port, with 10 mm of free air behind the labium. | **Reaffirmed** (no number given). |
| Window size first | "always make it a little smaller than what you think it's going to need to be … easier to take away clay than add" | Holes are printed small (k 0.8) and reamed; the window comes from the stubs. | **Reaffirmed.** |
| Window shapes | six shapes; "the different sizes and shapes of the window are very important … adjusted depending on the size of the ocarina" ; rectangular "probably the easiest one to get started" | Teardrop at every volume (owner decision 1). | **Reaffirmed.** Pure Ocarinas: teardrop is the pure-timbre, wide-range shape. The orientation is not stated; on the shapes board the teardrop's point and the triangle's apex are both up, which matches the kernel (broad end at the windway, tip at the labium) only if the windway is at the bottom of the drawing. |
| Ramp | "this is called the ramp, so it kind of deflects the excess air up that way" | 20° labium wedge, ramp outward, fading toward the widest points. | No number from Heuer. Nothing to change. |
| Airway quality | "the quality of the airway stick is really going to affect the quality of this voicing" ; compress the airway walls and wiggle the stick out "to make that airway exit look really nice and clean" | Windway as a smooth tapered slot; surface finish depends on print orientation. | **Reaffirmed** as a risk; matches the Pure Ocarinas printed-ocarina finding (§5). |
| Mechanism | the jet is deflected out and in by the chamber pressure; "the larger the chamber … the lower the pitch" | Helmholtz kernel with an air-reed drive. | **Reaffirmed.** |

### Not verifiable in this session

- **Heuer video content.** Videos #1 to #3 are now covered by the owner's transcripts (§5.1, §5.2). For the other videos only the titles are known; YouTube asks for a sign-in from this environment. Videos #5 (teardrop windows) and #8 (tuning) are the ones still worth reading, for the teardrop orientation and the tuning practice.
- **Fletcher 1979 and Fletcher et al. 1980** (flue-jet theory). The PDFs are scanned images with no text layer. The "transit delay ≈ half a period" condition used in [03 §4](03-parametric-findings.md#4-jet-strouhal-and-the-breath-curve) is the textbook flue-pipe result (Fletcher & Rossing, *The Physics of Musical Instruments*, ch. 16) and is flagged there as not re-checked.
