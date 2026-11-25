# Plan for series 3: the balance of the low voicing, necks, and blends into the body

**Updated 2026-11-19 with the owner's answers** (section 11): nothing is printed yet and the implementation is refined first; inner walls are now wanted; the inner pocket must blend; the raised neck is approved for testing; the lopsided root is to be explored. The changes are the new stage W (section 8), section 7.4, and the order of work in section 3a.

**Status, 2026-11-20:** step 0 and the first pass of stage W are done ([the record](Low_voicing.md), section 10). What they change in this plan:

- *Step 0.* The base is a new copy of the main checkout (`refs/snapshots/low-voicing-base-s3`). The 29 mm foot of series 1 was an effect of the old check: the rule's 42.3 mm foot passes at 10° on P4 and P1. The control is `s3-fwr`. `scipy` is there (system Python).
- *Stage W.* The walls are made by `inner_walls.py` beside the trials, not by a module inside `ocarina_addon/` as section 8.3 says: that keeps the add-on files equal to the copy. Trial names follow the height as a share of the section: `s3-w25`, `s3-w38`, `s3-w50` (20, 34 and 50 % blocked) stand for the `s3-w28`, `s3-w40`, `s3-w54` of section 8.4.
- *New work the results ask for* (not yet planned in detail): sizing the thumb holes for a wall in front of them; a finer cavity-mode solve for walled bodies; the owner's choice of height, of one wall or two, and of slab or ridge.
- *Still to do:* stages R (outside), A, B, C, the second pass of W, and D.

**Status, later on 2026-11-20** ([the record](Low_voicing.md), section 11): the owner sent a Blender reference and new notes, and the order of this plan changed.

- *Stage R* is replaced in part by the reference's own measurement (`ref_oot_blend/`) and a second reading of the clay photos.
- *Stage A (port bracket) and the raised neck of stage B* are answered: port 20° with the pipe at +4° and 57 mm puts the mouthpiece at mid-body (`s3-r20p`); 10°, 15° and 25° are on the same sheet; the raised neck is not needed.
- *Stage C (blends)* is done by the rolling ball (C2) on the outside hook instead of the shell-edit route; the lopsided root is `s3-ba`.
- *Stage W* has a second way, the ridge field, and the owner chose both low walls. The candidates are `s3-cA` and `s3-cB`.
- *Not done:* the other neck families of stage B, stage D (P0, P2, P3, the capped-air box, the print look), sizing the thumb holes for a wall, and the untried ways of the record's section 11.8.

**Status, end of 2026-11-20** ([the record](Low_voicing.md), section 12): the owner approved port 20°, the blend and the voicing cut, and dropped the ridge field. The voicing shoulder is built and tried on all five bodies; a Blender file and instructions for the owner's sculpt are in `sculpt/`. Open, in order: the owner's sculpt; the thick wall with short chimneys; one dish through that wall; port 25° with the shoulder (theirs to confirm); a shoulder height for each body; then stage D and the prints.

Written 2026-11-19 after a review of [the handover](../../Experimental_lower_voicing_handover.md), [the record](Low_voicing.md), the four Spencer pictures, the sheets of series 1 and 2, and the neck code (`ocarina_addon/voicing_geo.py`, `neck_solid`). Nothing in this plan is built yet. Nothing in it changes a rule, a preset or the main checkout.

## 1. Where the review leaves us

**What is settled (the owner's words, 2026-11-19):** port 10° (built 11.2°), the low mouthpiece accepted, the 45 mm pipe, thumb holes on the template.

**What changed with this plan.** Earlier the same day the owner said "no" to partitions as an add-on feature. In answer to this plan they wrote: "implement the inner wall due to the closenes to the thumb holes". I read "the inner wall" as the partial walls inside the chamber between the window and each thumb hole, as in the Spencer half-shell picture and patent US 7,799,980. That reopens the earlier "no", for this experiment. If something else was meant (for example a thicker wall around the thumb holes), stage W changes; the reading is asked once more in section 11.

**What the pictures show that our bodies do not have yet:**

| On the Spencer | On our nearest body (`lv-10fwdnr`) | Gap |
| --- | --- | --- |
| The mouthpiece grows out of the body. Seen on the thumb face it is a "T" with wide hollow curves on both sides, and no line where it meets the body | The neck is a cone pushed into the body. The join is a sharp crease all around (the build is a plain union; nothing is smoothed) | **The blend. Not explored at all so far** |
| A round cone, about 35 mm long, tip a little under half its foot | Round tip 13.8 mm, foot 29 × 29 mm, 34.2 mm beyond the edge | Close. The taper and the foot can still move |
| Seen edge-on (tray picture) the cone stands near the middle of the body's thickness | The tip's middle is 12.0 mm below the body's middle | Accepted by the owner, but the outside of the neck can still hide part of it |
| Window 30 to 33 % of the width inside the edge | 31 % | None |
| A dish about 28 × 20 mm | 19.5 × 14.8 mm | Open question 2 of the handover; not part of this plan |

**What "balance" has to weigh.** Every earlier series moved one thing at a time. The low voicing pulls four things against each other:

1. The window far around the body (the Spencer look) against the mouthpiece height (15 mm below mid-body at 10°, 10 mm at 20°).
2. A full neck and a wide blend (the Spencer look, a comfortable mouth end) against the left thumb hole, which is 12.7 mm from the window on the seed P4.
3. A round, thick mouth end against plastic and print time (60.0 cm³ against 54.2).
4. The outside shape against the voicing hash: anything that changes the hash needs its own Stage 1 stub.

**One thing I found in the review that must be checked first.** This checkout is a frozen copy of 2026-11-19, about 01:15. Its `checks_geo.py` differs from the main checkout's in 76 lines, and the main checkout no longer has `neck_foot_width_mm` at all. My notes say the `hole_to_voicing` check was a bounding box at that time and now measures the plastic at each rim. If so, the series 1 finding "below 30° the rule's foot touches the left thumb hole, so the foot must be 29 mm" may be an effect of the old check. The foot width is the main limit on every neck and blend in this plan, so step 0 settles it before anything else is built.

## 2. Ground rules for series 3

- All work stays in this checkout (`.claude/worktrees/low-voicing`). No rule change and no edit in the main checkout. Commits only when the owner asks (on 2026-11-20 they asked to commit the experiment's new files, this plan among them, on `low-voicing-experiment`).
- **Stages A to C change nothing that is in the voicing hash.** The window, lip, ramp, pipe (45 mm, hash `40688a48d1c7`), dish and pocket blend stay as they are, so the stubs V-a / V-aw stay valid. Only the outside of the neck and the join move.
- **Stage W (inner walls) does not change the voicing hash either, but it changes the body's acoustics** in a way the kernel does not model. It is kept as its own stage so that every other result can be read without it.
- **No print until the implementation is refined** (the owner, 2026-11-19). The prints of the handover (V-a / V-aw, a 10° body beside a 30° one) come after stage D.
- The owner's standing rules apply: the outer neck hides the pipe and does not have to follow it; at least 1.2 mm of plastic over the pipe; the roof over the exit cut square; no plastic inside the 45° flare from the window rim; the window cut must look smooth from outside.
- Not reopened: a bent pipe, moved thumb holes, a mid-body mouthpiece.
- Every body is checked on the STL read back from disk, as in series 1 and 2, and shown with outside renders and sections before it is called done.
- Before a rebuild, compare the outputs on disk with the scripts (the rewind trap of the handover, section 7).

## 3. Step 0: a sound base (about half a day)

1. Look for another running session in the main checkout; note the modification times of its add-on files.
2. **Settle the thumb-hole check.** Read the main checkout's `hole_to_voicing` and this copy's. Run the main checkout's version of the check (copied into the scratchpad, not into this checkout) on the stored STLs of `P4:lv-10`, `P4:lv-10f`, `P1:lv-10`, `P1:lv-10f`. Result: the real plastic between the foot of the neck and each thumb hole rim, and the widest foot that passes on P4 and P1 at 10°. This number is the budget for stage B and C.
3. **Decide the base.** Two ways:
   - *Stay on the frozen copy* (comparable with series 1 and 2 digit for digit), and carry only the corrected check into the trial script.
   - *Take a new snapshot of the main checkout* (rule 3 finished, flank fix `FLANK_UNDER_FACE_MM`) and rebuild the control bodies.
   I recommend the second if the main checkout is quiet: series 3 is about the neck, and the neck code is what changed. The cost is rebuilding four controls (about 5 minutes).
4. **Controls.** Build `P1:lv-10fw` (the decided values on P1; it was never built) and rebuild `P4:lv-10fw`. Add a trial with the decided values and the round tip but without the 8 mm dish (`lv-10fwr`, P4 and P1): the handover does not recommend the dish, so the dish must not sit in every body of series 3.
5. Check that `scipy` is available to the system Python or Blender's Python (needed for one blend method in stage C).

**Done when:** the foot budget is a measured number, the base is chosen and written into the record, and the control `lv-10fwr` passes on P4 and P1.

## 3a. Order of work

1. Step 0 (base, the thumb-hole check).
2. Stage R (references), now also the inside: the half-shell picture and the patent figures.
3. **Stage W, first pass** (section 8): the inner walls and the pocket on the control body. It comes early because the owner put it first, and because it decides how much room the window has between the thumb holes, which the necks and blends then live with.
4. Stages A, B, C (port bracket, necks, outside blends).
5. Stage W, second pass: the walls on the shortlisted outsides. Then stage D on every body.
6. Only then the prints.

## 4. Stage R: read the references for neck and blend (about half a day)

The earlier readings measured the window and the pipe. This stage measures the outside of the mouthpiece.

| Source | What to read | How |
| --- | --- | --- |
| Spencer thumb-face picture (`spencer_02`) | Width of the mouthpiece root against the body width; radius of the hollow curve on each side of the "T"; where the curve ends along the body (toward each thumb hole); taper of the cone | Gridded copy, `photo_grid.py`; a silhouette traced by threshold |
| Spencer tray picture (`spencer_01`) | Cone length against foot, tip against foot, where the cone meets the body across its thickness, the hollow curve on the deck side and on the thumb side | The same; several bodies, so a spread can be given |
| Songbird report (`Analizes_ocarinas/Songbird_OoT_12h/`) | The same proportions where the report already has them | Read, no new measuring |
| Spencer half-shell picture (`spencer_04`) and the patent record (`Analizes_ocarinas/Patent_US7799980/`) | For stage W: where each inner wall stands between the window and its thumb hole, its height, its thickness, how its top edge and its foot are rounded, the pocket under the window and how it runs into the walls | The record already has stations and heights (left wall at 0.18 to 0.21 of the length, right at 0.42 to 0.44, height to about the mid-line); add thickness and rounding from the gridded picture |
| Ocarina 12 and Deluxe STLs (the owner's Downloads) | A real fillet radius and root section, measured on the mesh: section along the body and across it | Sections by script. Visual reference only, as agreed: neck and window position, tuning not vouched for |

All picture readings are rough (oblique, low resolution); each number gets a range.

**Done when:** one table "root width, blend radius by side, cone taper, tip" with ranges, and a silhouette of the Spencer thumb face scaled to the P4 width for overlays.

## 5. Stage A: the port bracket with the final pipe (about 1 hour)

The owner chose 10° from bodies with a 30 mm pipe and a flat tip. The balance should be seen once with the decided pipe and the round tip, on the mesh steps around 10°:

| Trial | Port asked → built | Why |
| --- | --- | --- |
| `s3-p08` | 8° → 8.4° | The other end of the Spencer's 30 to 33 %; never built |
| `s3-p11` (= `lv-10fwr`) | 10° → 11.2° | The anchor |
| `s3-p14` | 15° → 14.1° | One step up |
| `s3-p17` | 17° → 16.9° | Between 10° and 20°: how much mouthpiece height each step buys |
| `s3-p20` | 20° → 19.7° | Series 1 had it only with the flat tip |

Seed P4 first; P1 for the two best. Output: one curve sheet (window % in, tip's middle below mid-body, mouth end beyond the edge, neck below the body, thumb hole distances, against the port) so the trade is one picture. **10° stays the anchor for stages B and C unless the owner moves it after seeing this sheet.**

## 6. Stage B: neck families at the anchor (about half a day)

All at port 10°, pipe 45 mm, on P4, then the best two on P1. All use settings that exist in `neck_solid` and are outside the hash. The foot width is bounded by step 0.

| Trial | Family | Settings | The question it answers |
| --- | --- | --- | --- |
| `s3-n0` | The rule's cone, flat tip (control) | as `lv-10fw` | – |
| `s3-n1` | Round cone (the Spencer's) | `neck_floor_mm = 8.6`, foot depth 29 | The control with the round tip (= `lv-10fwr`) |
| `s3-n2` | Round cone, slimmer taper | tip 13.8, foot about 24 × 24 mm | Does a slimmer neck free the thumb hole and still look like the reference? |
| `s3-n3` | Round cone, fuller foot | foot at the budget of step 0, depth 32 | The Spencer's tip-to-foot ratio (a little under half) |
| `s3-n4` | Bell | `neck_depth_exponent = 1.4`, `neck_width_exponent = 1.7`, round tip | The hollow profile as a blend "for free": the bell already curves into the body |
| `s3-n5` | Strong bell | exponents about 2.0 / 2.2, slim at the mouth, wide at the foot | The same, pushed toward the Spencer's "T" |
| `s3-n6` | Deluxe proportions | the settings of trial `tb-d2` (Neck_volume, section 8) at port 10° | The owner liked the Deluxe section at 30°; how does it read at 10°? |
| `s3-n7a`, `s3-n7b`, `s3-n7c` | Neck raised over the pipe (**approved for further testing by the owner, 2026-11-19**) | neck stance 4°, 8° and 12° above the pipe, cover growing toward the mouth end, round tip; the roof at the exit stays thin and square | How far can the outside alone lift the mouthpiece toward mid-body, and where does it start to read as the wedge the owner rejected at port 30°? (Series 2: the round tip alone gave 3 mm.) Measured for each: the tip's middle below mid-body, plastic over the pipe at the mouth end, and the look of the window cut from outside |
| `s3-n8` | Wider mouth end | `neck_side_wall_mm` 3.5 to 4, round tip about 16 mm | Lip comfort against bulk |

For each: mouth end size, foot size, middle line against the body, tip's middle below mid-body, least plastic over the pipe and its corners, plastic between foot and each thumb hole, keep-out, plastic volume, all checks.

**Done when:** a sheet like `sheet_series2.png` with the Spencer pictures in the first column, and a shortlist of two or three necks.

## 7. Stage C: blends between the neck and the body (1 to 1.5 days)

This is the new part. Today the join is a plain union with a sharp crease.

### 7.1 Three ways to make a blend

| Way | How | For | Against |
| --- | --- | --- | --- |
| **C1. Flared foot in the loft** | The last 8 to 12 mm of `neck_solid` widen faster (the bell of stage B, or a new unhashed setting for a flare at the foot only) | No new mesh method; exact; stays parametric | The sections are ellipses, so the neck cannot meet the body tangent all around; a crease stays, only shallower |
| **C2. Rolling-ball fillet on the envelope** (recommended) | Join shell and neck, then close the crease as a ball of radius r rolled along it would: a distance field on a 0.25 mm grid, grown by r and shrunk by r. This adds plastic only in hollow creases and leaves every convex surface where it was. The blended envelope then goes through the **shell-edit build** (`outer=`), which already cuts the chamber, holes and voicing out of a user's shell and runs every check. `shell_edit_low.py` shows that route works at 10° | A true fillet of a known radius; no change to the add-on; it is exactly the owner's own workflow (the user edits the shell, the add-on cuts) | A grid step in the surface (0.25 mm, below a print layer); it needs `scipy` or Blender's volume tools (step 0) |
| **C3. Hand sculpt in Blender** | Smooth the join by hand on the shell-edit base | The owner can do it themselves | Not repeatable; not a trial series |

The plan uses C1 inside stage B (the bells) and C2 for the series below. C3 is what the shell-edit build is for and needs no trial.

### 7.2 The limits of a blend

- **The window face.** No plastic may enter the 45° flare from the window rim, and the face around the window must stay (the shell-edit build measures there). The fillet is masked off inside that zone.
- **The thumb holes.** The crease runs within 12.7 mm (left) and 21.4 mm (right) of the window on P4. A fillet that reaches a hole makes its chimney longer and changes its tuning. The fillet radius is therefore set **by side**: small toward the thumb holes, free on the deck side and toward the bottom.
- **The mouth end** must stay as built (lip shape, and the shell-edit build measures it).
- **The chamber does not move.** The air is the cavity preset; a blend only adds plastic outside, so pitch and volume do not change. Expect 1 to 4 cm³ more plastic.

### 7.3 The trials (on the best neck of stage B, then on the second)

| Trial | Blend | The question |
| --- | --- | --- |
| `s3-b0` | none (control, through the shell-edit route) | Does the route give the same body as the one-step build? |
| `s3-b3` | r = 3 mm all around | The least that removes the crease |
| `s3-b6` | r = 6 mm all around | |
| `s3-b10` | r = 10 mm all around | The Spencer's "T" as read in stage R; does it reach the left thumb hole? |
| `s3-ba` | by side: the stage R radius on the deck side and toward the bottom, 3 mm or less toward the thumb holes | The balance candidate |
| `s3-bs1`, `s3-bs2`, `s3-bs3` | **the lopsided root** (the owner, 2026-11-19: "i believe this has not been explores"; it has not): the foot and the fillet fuller on the right-thumb side (21.4 mm of room) than on the left (12.7 mm), in three steps: fillet only, foot shifted 3 mm, foot shifted 6 mm | The Spencer root is wider than deep. How lopsided can it be before it looks wrong, and how much plastic does it win back beside the left thumb hole? |
| `s3-bm` | the mirror of `s3-bs2` (fuller toward the left thumb) | A control: it should fail or come close at the left thumb hole, which shows the limit is real |

For each, beside the usual checks: plastic added, the chimney length of each thumb hole before and after, the steepest plastic seen from the window rim, the least wall, and an overlay of the thumb-face silhouette on the Spencer's.

### 7.4 "Among the chamber and neck": the inside

The owner, 2026-11-19: "yes the inner pocked must blend".

**A correction to the first version of this plan.** I wrote that the pocket blend would need its own stub. It does not: the blend is already in the rule. `pocket_blend_radius_mm = 12` is in `[voicing_rules]` and in the hash, so V-a and V-aw already carry it. On `P4:lv-30` the check reads: the pocket ceiling falls away behind the lip on a 12 mm radius and meets the chamber wall in 125 of 125 directions, reaching 3.6 to 6.3 mm beyond the flat part, 8.2 and 7.8 mm at the back corners beside the windway exit.

What is still to do for the inside:

1. **Show it at 10°.** No sheet of series 1 or 2 shows the pocket from inside. Add an inside view (the thumb-face half seen from the chamber) and sections along and across the jet for the control body, and the `pocket_blend` numbers of every series 3 body to the tables.
2. **The pocket against the thumb holes.** At 10° the pocket's skirt runs toward the inner rims of both thumb holes. Measure the plastic and the distance between the end of the blend and each thumb hole's inner rim. No check does this today (`hole_to_voicing` looks at the outside).
3. **The pocket against the inner walls** (stage W): the walls must run into the pocket's skirt and the chamber wall with a fillet, with no step and no thin fin.
4. **The sides of the pocket beside the windway exit.** The blend is made around the lip half of the window. Check on the inside view whether the two back corners and the sides read as blended; if a step shows, extending the blend there changes the hash and needs a stub, so it is reported to the owner first and not built silently.
5. **Not in this plan:** a chamber that follows into the root of the neck (the air changes; the cavity must be solved again).

**Done when:** a sheet of the blend trials with the Spencer pictures, the by-side candidate passes on P4 and P1, and the control `s3-b0` equals the one-step body.

## 8. Stage W: the inner walls (1.5 to 2 days; new code)

**Why.** At port 10° the window sits 12.7 mm from the left thumb hole and 21.4 mm from the right one on the seed P4. Heuer says to keep holes away from the voicing; the Spencer has its holes 35 to 40 mm away *and* inner walls; the patent by its maker claims the walls for exactly this. The owner keeps the holes on the template, so the wall is the remaining lever.

### 8.1 What exists

- The record [US7799980_partitions.md](../Patent_US7799980/US7799980_partitions.md) and a desk check, `partition_check.py`. On its model body, two walls to the mid-line block 54 % of the section, leave 90 % of the thumb holes' conductance, and lower the first cavity mode with all holes closed from 1.48 to 1.24 × F6.
- The add-on has no inner wall. The chamber is smooth.

### 8.2 The cost to watch from the start

- **The first cavity mode.** The seed P4 stands at 1.361 × F6; the add-on's comfortable margin is 1.3 and the hard limit 1.0. If the model's drop of 0.24 carries over, walls to the mid-line put P4 near 1.12: inside the band where the add-on asks for the FEM solve. So every wall trial runs the cavity-mode solve, and wall height is the main dial.
- **The air.** A wall takes air out of the chamber. The chamber must be grown back to 80 cm³, or the body plays sharp.
- **The thumb holes' effect.** The model expects the thumb-open notes a little flat (conductance 90 to 97 %). The kernel does not model walls, so the hole sizes it solves are for a smooth chamber. This is the reason the patent record said "after Stages 2 and 3". The owner's choice puts the walls first; the plan therefore reports the predicted shift for each wall and keeps a wall-less twin of every candidate.
- **Room.** On P4 the left wall must fit into 12.7 mm between the window's edge and the thumb hole's edge, together with the pocket's skirt and the thumb hole's own inner rim. This may not fit at full thickness; the first task is to measure it.
- **Printing.** A wall standing inside a closed chamber must print without supports in the body's print orientation.

### 8.3 The implementation (in this checkout only)

- A new module, `ocarina_addon/inner_walls.py`, and optional preset keys (all absent = today's smooth chamber, so no existing body changes):
  `inner_wall_left_station`, `inner_wall_right_station` (place along the body, as a share of the distance from the window's edge to the thumb hole's edge), `inner_wall_height` (share of the chamber section blocked, or mm from the thumb-face wall), `inner_wall_thickness_mm`, `inner_wall_top_radius_mm`, `inner_wall_foot_fillet_mm`.
- Each wall is a solid rib across the thumb-face half of the chamber, following the chamber wall, with a rounded top edge and a filleted foot. It is **subtracted from the air** before the air is cut out of the shell, so the outside, the voicing solid and the holes are untouched.
- The chamber is then resized so the capped air is back on target (the cavity sizing already does this for other changes; confirm it sees the walls).
- New checks: wall thickness and height as built; plastic and clearance to the pocket's skirt, to each thumb hole's inner rim and to the windway's pocket; least fillet; overhang for printing; the blocked share of the section. The cavity-mode check runs on the walled air.
- Reported, not checked: the desk model's predicted loss of thumb-hole conductance and of the cavity mode, from `partition_check.py` fed with the built sizes.
- The inner walls are outside the voicing hash. They get their own line in the body record so that a walled and a smooth body can never be mistaken for one another.

### 8.4 The trials, first pass (control body `lv-10fwr`, P4, then P1)

| Trial | Walls | The question |
| --- | --- | --- |
| `s3-w0` | none (control) | – |
| `s3-w28` | both, blocking about 28 % (half the depth of the thumb-face half) | The mildest wall of the record |
| `s3-w40` | both, about 40 % | |
| `s3-w54` | both, to the mid-line (the Spencer / patent height) | Does the cavity mode stay above the limit? |
| `s3-wL`, `s3-wR` | the left only, the right only, at the best height | The left hole is the close one (12.7 mm); is one wall enough? |
| `s3-wn`, `s3-wf` | the wall nearer the thumb hole (as the patent and the photos have it) and nearer the window | Room against the pocket's skirt |
| `s3-wt` | thickness 2.4 and 4 mm at the best height | Print strength against lost air |
| `s3-w30` | the best wall on the rule's port 30° | Is the wall a low-voicing feature or a general one? |

For each: capped air before and after resizing, the body's growth, the first cavity mode, the predicted thumb-hole conductance, the clearances of 8.3, the print overhang, and inside views.

**Second pass,** after stage C: the chosen wall inside the shortlisted outsides, on P4 and P1.

**Done when:** a walled body passes every existing and new check on P4 and P1, its smooth twin is beside it, the cavity mode and the predicted thumb-hole shift are in the table, and inside-view sheets show wall, pocket and thumb holes together.

## 8a. Stage D: the shortlist on every body (about half a day)

1. Two or three candidates (port × neck × blend) from stages A to C.
2. Build each on P4 and P1, then on **P0, P2 and P3** (never built at 10°; each needs its own foot width, found as in step 0).
3. The capped-air check: narrow its box to the window cut ([capped_air_cap_box.py](capped_air_cap_box.py)) so a blended body is not read low for the wrong reason.
4. A print look, by script: overhang of the neck and the blend in the print orientation the add-on assumes, and the print mass.
5. The Stage 1 stub: the outside of the neck is not hashed, so V-aw stays the stub. Build one V-aw with the chosen neck outside only to confirm it passes; no new measurement is needed.

## 9. The balance sheet (what the owner gets to choose from)

One table and one picture sheet. Each candidate is a row; no single score, the weighing is the owner's.

| Measure | Reference or limit |
| --- | --- |
| Window inside the player-side edge | Spencer 30 to 33 % |
| Mouthpiece direction against the body's level | Spencer: about level |
| Tip's middle below the middle of the body | smaller is closer to the tray picture; 12.0 mm today |
| Mouth end beyond the body's edge | Spencer about 35 mm |
| Neck below the body's lowest point | 0 |
| Tip size; tip against foot | Spencer: round, a little under half the foot |
| Blend radius by side against stage R | Spencer reading, with its range |
| Plastic from the foot or blend to each thumb hole rim; chimney length change | check limit; 0 change wanted |
| Thumb hole edge to the window | 10 mm limit; Heuer and the patent say "further is safer" |
| Steepest plastic seen from the window rim | 45° keep-out |
| Least plastic over the pipe | 1.2 mm |
| Plastic volume and print mass | 54.2 cm³ for the plain body |
| Pocket blend: directions that meet the chamber wall; distance from its skirt to each thumb hole's inner rim | all directions meet; no thin fin |
| Inner walls: height (share blocked), thickness, clearances | as built |
| First cavity mode ÷ F6, smooth and walled | 1.3 comfortable, 1.0 hard limit; 1.361 smooth on P4 |
| Predicted thumb-hole conductance left (desk model) | 100 % smooth; 90 % at the mid-line wall |
| Voicing hash | must stay `40688a48d1c7` in every stage |
| Checks | no unexpected failure |

Pictures per candidate, in the Spencer's own views: straight at the thumb face with the silhouette overlay, along the body, edge-on as in the tray, from the player, the section through the lip, and a close view of the join.

## 10. What comes after, and what this plan does not do

- **The record.** Series 3 becomes section 10 of [Low_voicing.md](Low_voicing.md); the handover is updated; new trials go into `TRIALS` and into `ORDER` of `table_low_voicing.py`. The blend series gets its own script beside `shell_edit_low.py`.
- **Printing comes after the refinement** (the owner, 2026-11-19) and is still the only answer to the acoustic risks: the V-a / V-aw pair, then a 10° body beside a 30° one. With stage W there is now a third pair worth printing: the chosen 10° body with and without its inner walls. Only that pair shows whether the walls help the top notes and what they cost the thumb-open notes.
- **Not in this plan:** a rule change, a longer dish, a chamber that follows the neck, moved thumb holes, anything in the main checkout. If the inner walls are to become an add-on feature for real, that is a merge into the main checkout with its own tests, and it is the owner's to order.

Rough size: about 75 to 90 bodies at about 65 s each (walled bodies longer, because each runs the cavity-mode solve), five to six working sessions with the new module, the reading, scripts, sheets and record.

## 11. The owner's answers, and what is still open

**Answered 2026-11-19 (the owner's words):** "no printed tests on this experiment yet first we need to refine the implementation and implement the inner wall due to the closenes to the thumb holes, 3. yes the inner pocked must blend, 4. aprove this for further testing, 5. i believe this has not been explores".

| # | Question | Answer | In the plan |
| --- | --- | --- | --- |
| 1 | Was anything printed? | No. Refine the implementation first | Prints after stage D (section 10) |
| – | (added by the owner) | Implement the inner wall, because of the closeness to the thumb holes | Stage W (section 8). Reopens the "no" to partitions of the same day, for this experiment |
| 2 | Is the port open again? | Not answered | The default stands: 10° is the anchor, the bracket of stage A is information |
| 3 | Does the blend include the inside? | Yes, the inner pocket must blend | Section 7.4. The 12 mm pocket blend is already in the rule; the plan shows it, measures it against the thumb holes and joins it to the inner walls |
| 4 | May the neck's outside rise above the pipe? | Approved for further testing | `s3-n7a` to `s3-n7c` (section 6) |
| 5 | A root fuller on one side? | Not explored yet | `s3-bs1` to `s3-bs3` and the control `s3-bm` (section 7.3) |

**Still open.** Work starts without these; the defaults are what I will do.

1. **"The inner wall":** I read it as the partial walls between the window and each thumb hole (the patent, the half-shell picture). *Default: that reading.*
2. **One wall or two?** The left thumb hole is the close one. *Default: both are built, and each alone (`s3-wL`, `s3-wR`), so it can be chosen from results.*
3. **If the pocket's sides beside the windway exit show a step** (section 7.4, point 4), extending the blend there changes the voicing hash and needs a new stub. *Default: report it with a picture and ask before building.*
4. **The port** (question 2 above). *Default: 10°.*
