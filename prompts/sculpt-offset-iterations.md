# Prompt: move the neck along the body, with the thumb holes and the voicing

Written 2026-11-28. Paste everything below the line into a session started in the repository root. Run it again for each round; the log at the end of this file carries the state between rounds.

---

<context>
I'm building a 3D-printed 12-hole alto C ocarina with a Blender add-on in this repository. The body is the variant `P4-bowl` at 80 cm³. I am reshaping its neck after a rough sculpt and a photo of a ceramic reference. Read `docs/11-rough-sculpt-integration.md` first: it has the measurements, the decisions taken so far and what is still open.

The neck's shape and height are settled for now. This is the build every iteration starts from:

```bash
blender -b --factory-startup --python tools/geometry_check_variant.py -- P4-bowl 80 <suffix> windway_length_mm=50 neck_side_wall_mm=2.5 neck_base_width_mm=38 neck_width_exponent=1.5 neck_cover_mm=3.3 neck_floor_mm=3.3 neck_base_depth_mm=26 neck_depth_exponent=1.5 neck_tilt_deg=0 --renders
```

Its voicing hash is `6d05b21b49e8` (the 50 mm pipe). No η_w is known for it, and nothing here is a tuning claim.
</context>

<goal>
Find where along the body the neck should sit, and where the two thumb holes go once it is there, so that the build looks like the references and still passes its checks.

On the sculpt and in the photo overlay the neck sits nearer the bulb than on P4. Measured with `tools/neck_view_metrics.py`:

| Measure | Sculpt | Photo overlay | Build now |
|---|---:|---:|---:|
| Station of the neck from the bulb end, share of the length | 0.24 | about 0.25 | 0.35 |
| Neck's lean along the body, mouth end toward the bulb | +8.6° | about +10° | +1.6° |

The target is a station of 0.24 to 0.26. The lean has no control yet; see step 5.
</goal>

<what_moves_what>
- `port_u` (now 0.35) moves the voicing, the window and the neck together along the spine. 0.01 is about 1.3 mm. It is not in the voicing hash.
- `layout_centre_from_port_mm` (now 20.0) sets where the hands sit, measured from the port toward the tail. If it stays the same, the hands follow the neck. Raising it by the distance the port moved keeps the hands where they were on the body.
- `thumb_offsets_mm` moves one thumb hole in deck coordinates: first number along the hand axis, positive toward the tail; second across it. The variant already has `L_thumb = [-4.0, 0.0]`. An override replaces the whole table, so always pass both thumbs.
- The scoop (`bowl_*`) stays the baseline's in this prompt. It has its own prompt, `prompts/sculpt-scoop-iterations.md`, which runs after this one is decided.
</what_moves_what>

<known_from_two_probes>
Both at `port_u=0.27`, which gives station 0.26:

- **Hands follow the neck** (`P4-bowl-80-off27-hands-follow`): no unexpected failure. New warnings: only 5.4 mm of land past the left pinky hole at the bulb end (10 mm wanted), the left pinky hole leans 35° toward the bulb end, and the left hand span is 49.5 mm (50 wanted).
- **Hands stay** (`P4-bowl-80-off27-hands-stay`, `layout_centre_from_port_mm=30.6`): three unexpected failures. `L_thumb` is 6.7 mm from the window (10 wanted) and touches the voicing block, the scoop cuts its sealing rim, and the capped air is 0.67 % under V0.

So the answer lies between the two: the hands follow part of the way, and `L_thumb` moves to clear the voicing.
</known_from_two_probes>

<iterations>
Change one thing per build. Give each build its own suffix (`off27-s50`, `off24-s50-lt6`, ...). After each build run the metrics tool on its STL and add one row to the log below.

1. **Station.** Build `port_u` = 0.31, 0.27, 0.24 with the hands following (layout centre 20.0). Record station, warnings and unexpected failures. Stop lowering `port_u` when a check fails that the split in step 2 cannot plausibly fix.
2. **How far the hands follow.** At the best station, build with the hands following 100 %, 75 %, 50 % and 25 % of the port's move: `layout_centre_from_port_mm = 20 + (1 − share) × (0.35 − port_u) × 132`. Keep the share with the most land past both pinky holes and no unexpected failure.
3. **The bulb-side thumb, `L_thumb`.** On the sculpt it sits level with the aperture and 27 to 30 mm from it toward the bulb. Move it with `thumb_offsets_mm` until it is at least 10 mm from the window, its sealing rim is uncut, and `ergo_thumbs` passes. Confirm the sign of the second offset number with one test build before trusting it.
4. **The tip-side thumb, `R_thumb`.** On the sculpt it is 25 to 27 mm from the aperture toward the tip and 12 to 13 mm behind it, away from the mouth. Move it only if step 2 left it outside `ergo_thumbs` or closer than 10 mm to the window.
5. **Lean.** If the station is right and the neck still looks too upright against the references, say so and stop. Leaning the neck along the body means turning the pipe, which is a new control and a new voicing. Do not add it in this prompt; describe what it would take.
6. **Recheck the neck.** Moving the port changes the body's section at the neck. Run the metrics tool and compare offset, mouth out, width and depth with the sculpt's values in the tool's header. Adjust `neck_base_width_mm` or `neck_base_depth_mm` only if a share is off by more than 0.05.
</iterations>

<rules>
- Every build must keep voicing hash `6d05b21b49e8`. If it changes, a hashed key was touched by mistake: undo it.
- A candidate is acceptable only with no unexpected failed check. The two `hole_limits` failures are expected and stay.
- Thumb positions are hand dimensions. Judge them by the `ergo_*` checks and the 10 mm clearance, and use the sculpt's positions as a guide of ±3 mm, not as a tolerance.
- Do not edit `variants.toml`, the presets, or any add-on code. Everything here is an override on the command line.
- Do not touch `addon_out/baseline-print-P4-bowl-80/`.
- At most eight builds per round. Then stop and report.
</rules>

<report>
End each round with:

1. The log table, updated in this file.
2. The best candidate's command in full, its check summary, and its row from the metrics tool.
3. A top view and a thumb-face view of the best candidate, from `addon_renders/<id>/`, for me to lay over the references.
4. What you would try next and why, or the decision you need from me.
</report>

## Log

| Build suffix | `port_u` | Layout centre | Thumb offsets | Station | Unexpected failures | New warnings against the neck-only build |
|---|---:|---:|---|---:|---|---|
| `sculpt-neck` | 0.35 | 20.0 | L [-4, 0] | 0.35 | none | none |
| `off27-hands-follow` | 0.27 | 20.0 | L [-4, 0] | 0.26 | none | bulb rest land 5.4 mm; L_pinky lean 35°; left span 49.5 mm |
| `off27-hands-stay` | 0.27 | 30.6 | L [-4, 0] | 0.26 | `hole_to_voicing`, `hole_seal_surface`, `volume_capped_air` | none |
| `off31-s100` | 0.31 | 20.0 | L [-4, 0] | 0.30 | none | bulb rest land 9.2 mm; L_pinky lean 24°; left span 50.0 mm (just under) |
| `off24-s100` | 0.24 | 20.0 | L [-4, 0] | 0.23 | none | bulb rest land 2.2 mm; L_pinky lean 52°; left span 48.5 mm; L_pinky rim relief 0.57 mm |
| `off26-s75` | 0.26 | 22.97 | L [-4, 0] | 0.25 | none | bulb rest land 6.7 mm; L_pinky lean 31°; left span 49.7 mm |
| `off26-s50` | 0.26 | 25.94 | L [-4, 0] | 0.25 | `hole_seal_surface` (scoop cuts L_thumb rim), `volume_capped_air` (−0.55 %) | bulb rest land 9.3 mm; L_pinky lean 23°; left span 50.0 mm (just under) |
| `off26-s25` | 0.26 | 28.91 | L [-4, 0] | 0.25 | `hole_to_voicing` (L_thumb 8.2 mm, touches the ramp), `hole_seal_surface`, `volume_capped_air` (−0.65 %) | none (bulb land 12.0 mm) |
| `off26-s75-ltmouth` | 0.26 | 22.97 | L [-5.2, -6], R [0, 0] | 0.25 | none | as `off26-s75`, plus `ergo_thumbs`: L thumb +3.3 mm from L pinky |
| `off26-s50-ltbulb` | 0.26 | 25.94 | L [-5.4, 0], R [0, 0] | 0.25 | none (capped air −0.46 %, limit 0.5) | as `off26-s50`; bulb land reads −4.0 mm, a measuring artifact (see round 1) |
| **`off26-s75-lt43m6`** | 0.26 | 22.97 | L [-4.3, -6], R [0, 0] | 0.25 | none | bulb rest land 6.7 mm; L_pinky lean 31°; left span 49.7 mm |
| `off26-s50-lt49m3` | 0.26 | 25.94 | L [-4.9, -3], R [0, 0] | 0.25 | `volume_capped_air` (−0.51 %) | as `off26-s50` |
| `off26-s50-lt44m6` | 0.26 | 25.94 | L [-4.4, -6], R [0, 0] | 0.25 | `volume_capped_air` (−0.52 %), `hole_to_voicing` (L_thumb 10.0 mm, just under) | as `off26-s50` |

### Round 1 (2026-11-28): what the eight builds showed

- **Station:** it tracks `port_u` almost one for one (0.31 → 0.298, 0.27 → 0.263, 0.24 → 0.230). `port_u` = 0.26 gives 0.252, the middle of the target. No build failed a check from the station alone; the cost is bulb-end land and L_pinky's lean.
- **Hands:** in thumb-place terms, the `layout_centre_from_port_mm` increase from the 100 % to the 25 % share moves every hand hole about 9 mm toward the tail against the aperture. Bulb land grows about 0.9 mm per mm, and L_thumb comes about 0.97 mm per mm nearer the window. Every failure at 50 % and 25 % is L_thumb's: the scoop cuts its rim, it comes near the window, and capped air falls as it approaches (−0.15 % at 27 mm from the aperture, −0.34 % at 24, −0.55 % at 20).
- **`ergo_thumbs` ties L_thumb to the hand:** at the variant's −4 it sits +5.5 to +5.8 mm from L_pinky (range +4 to +10), so it can go only about 1.5 mm further toward the bulb. A sideways move also shifts it along the hand axis: −6 across cost 1.0 mm.
- **Sign:** the second number of `thumb_offsets_mm` is positive away from the mouth. −6 moved L_thumb 5.7 mm toward the mouth.
- **The trade:** the sculpt's thumbs (L 29.7 mm toward the bulb from the aperture, R 27.0 toward the tip) fit the hands following 100 %, where bulb land is only about 4 mm. More land puts the thumbs nearer the aperture than the sculpt. 75 % with L_thumb level with the aperture is the closest look that passes. 50 % gives 9.3 mm of land, but L_thumb then sits 6 mm off the sculpt's line, with capped air 0.04 % from its limit.
- **Artifact in `off26-s50-ltbulb`:** `ergo_rest_space` cuts the body through the L_pinky centre along the hand axis. The moved L_thumb bore crosses that plane within 1.5 mm of the centre, so the run of plastic breaks at 0 and the land reads −4.0 mm. The hands did not move from `off26-s50`; the real land is 9.3 mm.
- **R_thumb:** not moved (step 4). It passes `ergo_thumbs` (−7.4 mm from R middle, range −8 to +3) and is 24.6 mm from the window. It sits 6 mm further toward the tip than the sculpt, and only 0.6 mm of the `ergo_thumbs` range lies in that direction.
- **Neck recheck:** at station 0.25: offset +2 %, mouth out 1.59, width 0.39 / 0.45 / 0.54, depth 0.27 / 0.31 / 0.37, lean +3.6 to +4.0°. The move changed every share by 0.01 or less. Width at 0.4 and 0.6 sections is 0.07 and 0.10 under the sculpt, as on the kept `sculpt-neck` build. Closing that with `neck_base_width_mm` alone would need about 55 mm against a 39.5 mm section: the gap is in the flare, not the base. Not adjusted.
- **Lean:** +4.0° against the sculpt's +8.6° and the photo's +10°: still too upright. See step 5; nothing was added.

### Round 2 (2026-11-28): both shares, compared

The owner asked to carry both shares and compare them. On 75 %, L_thumb is already where the sculpt has it across the body, and `ergo_thumbs` stops it moving further toward the bulb, so it was not rebuilt. On 50 %, two builds moved L_thumb toward the mouth, 3 and 6 mm (rows `off26-s50-lt49m3`, `off26-s50-lt44m6`). Both fail capped air, because the thumb comes nearer the window. On 50 % L_thumb cannot leave the line it has in `off26-s50-ltbulb`.

[Thumb-face comparison](../addon_renders/rough-sculpt-reference/offset-75-vs-50-thumb-face.png): both builds at one scale, 10 mm grid about the aperture, with the sculpt's thumb centres and the 3 mm guide.

| | 75 %: `off26-s75-lt43m6` | 50 %: `off26-s50-ltbulb` |
|---|---|---|
| `layout_centre_from_port_mm`, thumb offsets | 22.97, L [-4.3, -6] | 25.94, L [-5.4, 0] |
| Unexpected failures | none | none |
| Land past the pinky holes, bulb / tail | 6.7 / 17.7 mm | 9.3 / 16.0 mm (bulb reads −4.0, the artifact of round 1) |
| L_pinky lean toward the bulb | 31° | 23° |
| Left hand span | 49.7 mm | 50.0 mm (just under) |
| L_thumb, (toward the mouth, toward the tip) | (−1.1, −24.0): 5.7 mm from the sculpt's centre | (−7.0, −21.9): 10.0 mm from it |
| R_thumb | (−12.7, +33.2): 6.2 mm from the sculpt's centre | (−12.7, +36.3): 9.3 mm from it |
| L_thumb to the window; seal band uncut | 13.2 mm; 3.0 of 3.0 mm | 12.4 mm; 1.3 of 3.0 mm |
| Capped air (limit −0.5 %) | −0.31 % | −0.46 % |
| `ergo_thumbs`, L thumb from L pinky (+4 to +10) | +4.1 mm | +4.4 mm |
| Warnings | the same six | the same six |

Reading: 75 % is nearer the references for both thumbs, and it keeps margin for the scoop prompt. The L_thumb rim has 3 mm of uncut band and capped air 0.19 % to spare. 50 % has 1.3 mm and 0.04 %, so almost any wider scoop would fail it. 50 % gives 2.6 mm more land at the bulb and 8° less L_pinky lean, but both are still warnings. Only a grip mock-up can say whether that land matters more than the look.
