# Bringing the rough sculpt into P4-bowl

Build an experimental 80 cm³ variant, provisionally named `P4-bowl-sculpt`, derived from the selected P4-bowl. The sculpt supplies the neck's outside, the thumb positions and the scoop's outline. The P4 body, the windway, the window and the labium stay as they are. The existing instrument design supplies the acoustic targets. A printed specimen supplies any future calibration.

Revised 2026-11-28 after measuring the sculpt mesh itself. The earlier draft worked from one projection; the numbers below replace its picks where they differ.

## What the sculpt is

Source: `ocarina oot rough stl.stl` (owner's Desktop, not in the repository; SHA-256 `a8b72a6c…3f366ab4`, 167,615 triangles). Gridded views of [the sculpt](../addon_renders/rough-sculpt-reference/sculpt-thumb-face-grid.png) and of [the baseline](../addon_renders/rough-sculpt-reference/baseline-thumb-face-grid.png) are saved with the [first picks](../addon_renders/rough-sculpt-reference/geometry-reference.toml) and the [annotated thumb face](../addon_renders/rough-sculpt-reference/thumb-face.png). Grid lines are 10 mm apart.

- It is a solid exterior with the holes cut in as pockets. It has no cavity, no windway and no labium, so it says nothing about wall thickness, duct or voicing edge.
- The mesh is one piece but not closed (166 open edges, about 130 edges shared by more than two faces). Measure it; do not boolean with it.
- At 1:1 in millimetres it encloses 115.4 cm³. The baseline's outside encloses about 149 cm³ (69.0 plastic + 80 air). The sculpt cannot hold 80 cm³ at baseline walls. It is longer and more pointed than P4 (about 148 mm bulb to tip against 140 mm) and thicker (53 mm against 40 mm, neck included).
- Twelve holes: ten on the finger deck, two thumbs. It also carries a hanging loop, which is out of scope.

**Owner's decision (2026-11-28):** the sculpt is a reference for proportions, not for 1:1 size. It is scaled before any dimension is taken from it.

**Scale, confirmed by the owner (2026-11-28): 1.089**, the factor that makes the sculpt enclose what the baseline's outside encloses, (149 / 115.4)^(1/3). This reads the sculpt as an 80 cm³ instrument of its own shape. The anchor matters, because the two bodies are shaped differently:

| Anchor | Scale |
|---|---:|
| Enclosed volume (used) | 1.089 |
| Aperture to mouth end | 1.055 |
| Span between the thumbs | 1.04 |
| Bulb to tip length | 0.95 |

A different anchor moves every sculpt number below by the ratio of the two scales, up to 5 % among the first three.

The neck does not use this scale. It is sized against the body's section at the neck, where P4 is 0.77 of the sculpt (step 2). The neck rows in the table below are kept for the record only.

## Measured differences

Frame: origin at the aperture center on the thumb face, first axis toward the mouth, second axis toward the tip-side thumb. Sculpt values are the mesh measurements times 1.089. Baseline values are from the print `addon_out/baseline-print-P4-bowl-80/P4-bowl-80.stl`.

| Item | Sculpt × 1.089 | Baseline | Note |
|---|---:|---:|---|
| Aperture to mouth end, projected | 63.6 mm | 61.6 mm | first draft said 54.8 unscaled, from a pick short of the end |
| Neck angle to the body's long axis | about 85–95° | 90° | not resolved; no change planned |
| Neck section 4.4 mm from the mouth | 18.2 × 13.6 mm | about 16.2 × 16.0 mm | width × depth |
| Neck section 25 mm from the mouth | 30.4 × 21.1 mm | about 19.8 × 19.7 mm | |
| Neck section 37 mm from the mouth | 38.2 × 25.7 mm | about 21.9 × 21.8 mm | |
| Neck section, upper half / lower half | equal | about 4.7 / 10.5 mm at the mouth | baseline computed from the rule, not measured |
| Neck axis to the mouth-center-to-aperture line | 13° | not comparable | the baseline's flank follows the pipe |
| Bulb-side thumb (`L_thumb`) | (−0.7, −29.7) | (−7.8, −25.6) | sculpt is the mean of two picks |
| Tip-side thumb (`R_thumb`) | (−13.0, +27.0) | (−12.8, +30.4) | |
| Thumb hole diameters | about 10–11 mm | 11.8 and 13.8 mm | kernel sizes stay |
| Scoop along the jet, rim to rim | 22.9 mm (7.6 neck side, 15.2 far side) | 24 mm (6.4 and 17.6) | |
| Scoop across the jet, rim to rim | 35.9 mm | 29.1 mm | |
| Scoop depth under the rim chord | about 3.3 mm | setting 2.2 mm, measured less | |
| Opening | round, about 7.6 mm | 8.89 × 9.05 mm | the baseline window stays |

The sculpt's neck sections were cut normal to the neck's own fitted axis. Away from the rounded end they are a straight cone. Scaled, the width is 15.6 + 0.61 s and the depth 12.0 + 0.37 s, with s the distance from the mouth in mm. Depth is 0.70 of width throughout. Baseline sections are computed from the build record (15.4 × 15.2 at the mouth, 25.4 × 25.4 at the exit, linear over 57 mm).

Two independent picks of each thumb center differ by 1.6 to 2.5 mm on the mesh. Treat ±2.7 mm as the scaled pick uncertainty until the centers are fitted to the pocket rims.

## 1. Register the sculpt to the baseline

Most of this is done above. What remains:

1. Copy the STL beside the reference TOML, or record its path and the checksum there, so the measurements can be repeated.
2. Fit each thumb center and the aperture center to its pocket rim instead of picking by eye, and replace the picks in the TOML. Record the residual. Keep the TOML in mesh units and record the scale beside them.
3. Read the baseline's thumb and aperture centers from the build record, not from a render. The baseline column above was picked from a render to within about 1 mm.
4. Confirm `L_thumb` is the bulb-side thumb. The −4 mm offset "toward the bulb" in the variant and the hole sizes (11.8 mm at the bulb side) both say so.

**Acceptance:** the TOML holds fitted centers with residuals under 1 mm, and the table above is regenerated from it.

## 2. Shape the neck

**Owner's correction (2026-11-28):** the neck is to match the sculpt's end-on view, looking down the neck from the mouth: its size against the body's silhouette and where it sits in it. It is not to be made strictly symmetric about the pipe, and it is not sized by the 1.089 volume scale. The first attempt did both and came out too wide and pushed toward the finger deck.

The neck is therefore sized against the body's section at the neck's station, measured across the neck. That section is 52.2 mm on the sculpt and 40.3 mm on P4, a ratio of 0.77. The two bodies differ in shape, so the volume scale and this one disagree; for the neck, this one governs.

Measured with `tools/neck_view_metrics.py`, which reports everything as a share of that section:

| Measure | Sculpt | Baseline | Kept build |
|---|---:|---:|---:|
| Neck axis passes this far from the body's long axis (+ toward the thumb-face side) | +4 % | −3 % | +4 % |
| Mouth end's distance from the long axis, in sections (the neck's height) | 1.35 | 1.72 | 1.58 |
| Neck width 0.2 / 0.4 / 0.6 sections from the mouth | 0.40 / 0.52 / 0.64 | 0.42 / 0.45 / 0.48 | 0.38 / 0.45 / 0.54 |
| Neck depth at the same places | 0.28 / 0.36 / 0.43 | 0.40 / 0.43 / 0.47 | 0.26 / 0.30 / 0.36 |
| Neck's station along the body, from the bulb end | 0.24 | 0.34 | 0.35 |
| Neck's lean along the body, mouth end toward the bulb | +8.6° | +2.7° | +1.6° |

An earlier version of this table compared widths and depths at quarter points of each neck's own free length and showed a closer match. That free length was not well defined, and the build's neck is longer, so the comparison flattered it. At equal distances from the mouth the build's neck is still slimmer than the sculpt's toward the body.

The kept build is `P4-bowl-80-sculpt-neck`. Nothing is in `variants.toml` yet; the build is this command, and its [report](../addon_checks/P4-bowl-80-sculpt-neck.md), [views](../addon_renders/P4-bowl-80-sculpt-neck/sheet_views.png) and the [end-on comparison](../addon_renders/rough-sculpt-reference/end-on-sculpt-vs-neck-build.png) are saved. In the comparison the sculpt is drawn at 0.77 so the two body sections are the same size.

```bash
blender -b --factory-startup --python tools/geometry_check_variant.py -- P4-bowl 80 sculpt-neck windway_length_mm=50 neck_side_wall_mm=2.5 neck_base_width_mm=38 neck_width_exponent=1.5 neck_cover_mm=3.3 neck_floor_mm=3.3 neck_base_depth_mm=26 neck_depth_exponent=1.5 neck_tilt_deg=0 --renders
```

| Key | Baseline | Kept | Why |
|---|---:|---:|---|
| `windway_length_mm` | 57.0 | 50.0 | neck height from the owner's photo overlay; in the voicing hash |
| `neck_side_wall_mm` | 3.197 | 2.5 | mouth end 14.1 mm wide; the sculpt's share would be under the pipe's minimum |
| `neck_base_width_mm` | 25.4 | 38 | wider base, toward the sculpt's flared footprint |
| `neck_width_exponent`, `neck_depth_exponent` | 1.0, 1.0 | 1.5, 1.5 | slender near the mouth, flaring at the base, front and back |
| `neck_cover_mm`, `neck_floor_mm` | 2.2 (rule), 10.0 | 3.3, 3.3 | mouth end 9.6 mm deep with the pipe in its middle |
| `neck_base_depth_mm` | 25.4 | 26 | sets both the depth share and where the axis passes the body |
| `neck_tilt_deg` | 6.0 | 0 | owner's decision; the alignment comes from the root depth instead |

How the alignment works: the thumb-face flank follows the pipe and all the depth grows on the deck side, so a deeper root swings the neck's axis toward the deck. At 34 mm deep with straight flanks the axis passed 12 % to the deck side. A straight cone 31 by 23 mm at the base brought it to 3 % on the aperture side but left the base too slight. The kept build has a wider base (38 by 26 mm) with a flare of 1.5, at the owner's request, and the axis passes 4 % to the aperture side, which is the sculpt's position. Sections are still full ellipses and the pipe is centered at the mouth end.

Results of the kept build:

- **Neck height.** The owner's overlay of a ceramic reference (2026-11-28) shows its neck ending at about 0.86 of the build's free length, so the pipe went from 57 to 50 mm. That is a new voicing: hash `6d05b21b49e8`, where every build with the 57 mm pipe kept `bcdd90905c01`. Neither has an η_w.
- Topology, duct, wall and voicing checks pass. Warnings and expected failures are the baseline's own.
- No hole is touched by the neck (the first attempt reached `sub1`).
- The neck is slender for most of its length and flares where it meets the body, on the deck side and at both sides. The thumb-face flank still follows the pipe to the window.

### Neck base controls in the add-on

The panel has three new settings under the preset. They change the neck's outside only, so the pipe and the voicing hash stay the same. 0 keeps the preset's value.

| Setting | Effect |
|---|---|
| Neck base width (mm) | width where the neck meets the body |
| Neck base depth (mm) | depth there, front to back |
| Neck flare | 1 is a straight cone; larger is a tube near the mouth that flares at the base |

A base at or below the mouth end's size gives a tube: `neck_solid` now never lets the base be narrower than the mouth end. A body built with any of them set gets an id that names them (`P4-bowl-80-neck38x26f1.5`), so its files do not pass for the plain preset's. The mouth end's size, the cover and the tilt are still preset keys only.

Not matched, and why:

- **Neck height against the sculpt.** The mouth end is 1.58 sections from the long axis; the sculpt's is 1.35 and the photo overlay about 1.56. The build follows the photo. Matching the sculpt would take a pipe of about 41 mm.
- **Root fillet.** The sculpt flares smoothly into the body, so its footprint on the body is larger (about 0.94 by 0.65 sections). The flare of 1.5 goes part of the way; the root still meets the body in a crease. There is no blend control.
- **Mouth end.** The sculpt's is about 0.25 by 0.19 sections, which on P4 is 10 by 8 mm. The 9.05 mm pipe needs at least 11.5 mm of width. The build's is 14.1 by 9.6 mm.
- **Station and lean.** The sculpt's neck sits nearer the bulb and leans along the body. The station is `port_u`, and moving it moves the voicing and the hands with it; that work is set out in `prompts/sculpt-offset-iterations.md`, with two probe builds already logged. The lean has no control.

## 3. Shape the exterior scoop

**Superseded as a work order by `prompts/sculpt-scoop-iterations.md`**, which sizes the scoop against the body's section and runs after the neck's position is decided. The numbers below are the earlier volume-scaled reading, kept for the record.

Add the scoop to the accepted neck. Every `bowl_*` value is in the voicing hash, so this step makes a new voicing with no η_w. That is the same standing as the baseline, which is also unprinted.

Start from the existing controls. Extend `bowl_math.py` and `bowl_cut.py` only if these cannot reach the targets.

| Key | Now | Trial | From |
|---|---:|---:|---|
| `bowl_half_length_mm` | 12.0 | 11.4 | 22.9 mm rim to rim along the jet |
| `bowl_half_width_mm` | 14.53 | 18.0 | 35.9 mm across the jet |
| `bowl_centre_xw_mm` | 10.0 | about 8.2 | center 3.8 mm beyond the window's center |
| `bowl_depth_mm` | 2.2 | raise until the measured depth is 3.3 mm | depth under the rim chord |

The window, the windway exit height and the labium edge do not change. The sculpt's round opening is not adopted: the window is the kernel's.

**Roadblock:** the scoop gets deeper and its center moves toward the exit while the neck's root gets wider, so the least plastic over the windway's roof and under the windway's exit corners is at risk. The baseline already leaves 0.18 to 0.42 mm there. Compare centerline and off-center sections, run the local thickness probes, and if clearance worsens, reduce the depth before the outline.

**Acceptance:** built rim-to-rim length, width and measured depth are within 1 mm, 1 mm and 0.3 mm of the targets. The STL read-back confirms the unchanged aperture and edge dimensions within the existing check tolerances, with zero wide thin-plate probes. The plate under the exit corners is no thinner than the baseline's. The new voicing hash is recorded, and calibration matching reports no constants for it.

## 4. Move the thumb holes

**Superseded as a work order by `prompts/sculpt-offset-iterations.md`**, which moves the thumbs together with the neck's station. The numbers below are the earlier volume-scaled reading, kept for the record.

The sculpt asks for two moves, in the aperture frame:

- `L_thumb`: about 7 mm toward the mouth side and 4 mm toward the bulb.
- `R_thumb`: about 3.4 mm toward the aperture (toward the bulb), with no real change toward the mouth.

The `L_thumb` move is well beyond the pick uncertainty. The `R_thumb` move is only just beyond it and depends on the scale anchor: at 1.04 it would be about 4.6 mm. Fit the centers (step 1) before committing it.

Express both as `thumb_offsets_mm` in the variant. No new code is needed. The baseline's `L_thumb = [-4.0, 0.0]` is included in the baseline column above, so the new offset is that value plus the move, counted once. The first axis of the offset is the hand axis, positive toward the tail. The sign of the second axis has to be confirmed with one test build before the values are trusted. The offsets are in deck coordinates on a curved face, so iterate once on the built centers.

Keep the kernel's hole sizes and remeasure the finished chimney lengths.

**Roadblock:** `L_thumb` lands at the wide neck's root. Its 11.8 mm hole may be drilled through neck plastic, which lengthens the chimney and changes the kernel's size for that hole. `R_thumb` at 13.8 mm moves toward a scoop that is 7 mm wider. Check both sealing bands, spacing to the scoop and to adjacent holes, drill axes, chimney geometry and hand reach. The baseline already has two expected pad-limit failures; compare their values and flag any worsening. Confirm grip and reach on a physical mock-up before freezing the layout.

**Acceptance:** built centers are within 1.5 mm of the fitted, scaled sculpt centers in the aperture frame. Chimney lengths and the hole-to-voicing distances are tabulated against the baseline's (16.7 mm and 21.7 mm to the window). The report marks both moves as ergonomic changes.

## 5. Integrate and verify

Save comparable builds for baseline, neck only, neck plus scoop, and all three changes. Expected identities:

| Build | Voicing hash | Layout |
|---|---|---|
| Baseline | `bcdd90905c01` | baseline |
| Neck only | `bcdd90905c01` | baseline |
| Neck plus scoop | new | baseline |
| All three | same new hash | new |

For the final variant, export the STL, run the geometry and cavity-mode checks, and produce matched thumb-face, side, aperture, windway-section and thickness views. Compare dimensions and check outcomes across the four builds to identify which change caused any regression.

Exercise preview, validate, checked export and edited-shell finish. Verify the table above, and that the original 80 cm³ baseline still resolves to `bcdd90905c01`. Export into a fresh specimen folder to protect existing measurements. Run the kernel, plain Python, Blender and installed-extension suites.

The geometry milestone is a reviewed variant with documented reference deviations and no new unexpected check failures. The physical milestone is a grip and seal trial followed by measured volume, pitch and breath-pressure readings from the printed variant. Only those observations can support a tuning claim.

## Which body the sculpt resembles

Outside profiles, each measured the same way: thickness and width at stations along the length, divided by the length and by the ellipse envelope the presets use. Widths near the neck are left out because the neck inflates them.

| Body | Thickness at 1/6, 1/2, 5/6 | Width at 1/2, 2/3, 5/6 | Width : thickness |
|---|---:|---:|---:|
| Sculpt | 0.39, 0.30, 0.22 | 0.35, 0.30, 0.24 | 1.1 to 1.2 |
| P4 seed | 0.36, 0.27, 0.20 | 0.33, 0.28, 0.24 | 1.2 |
| P1 teardrop | 0.40, 0.34, 0.26 | 0.47, 0.38, 0.33 | 1.3 to 1.4 |
| P2 tailed gourd | 0.37, 0.25, 0.20 | 0.35, 0.27, 0.26 | 1.3 to 1.4 |

P4 seed is the closest of the existing bodies. Its taper matches the sculpt's, its width is within 5 %, and it is about 11 % thinner along the whole length. The P1 teardrop is a worse match: about a third too wide for its length, flatter in section, and blunter at the tail.

A closer body would be P4 with its `height` stations raised about 11 % and `port_u` moved from 0.35 toward 0.25. That is a new body, not a variant of the neck: the solved length, every hole position and the cavity mode change with it. It is not part of this plan.

## Open questions for the owner

1. Steps 3 and 4 still use the 1.089 volume scale. The neck showed that scale does not suit P4's slimmer section. Should the scoop also be sized against the body's section (0.77), and the thumbs left at hand size?
2. Is the 57 mm pipe to stay, leaving the neck longer than the sculpt's proportion, or is a shorter pipe (a new voicing) worth an experiment?
3. Is a thicker P4 (about 11 % more height, port nearer the bulb) wanted as a later body?
