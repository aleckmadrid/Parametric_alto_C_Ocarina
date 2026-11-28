# Prompt: shape the scoop around the window after the neck is decided

Written 2026-11-28. Do not run this before the neck's position is decided with `prompts/sculpt-offset-iterations.md`. Paste everything below the line into a session started in the repository root. The log at the end of this file carries the state between rounds.

---

<context>
I'm building a 3D-printed 12-hole alto C ocarina with a Blender add-on in this repository. The body is the variant `P4-bowl` at 80 cm³, with its neck reshaped and moved after a rough sculpt. Read `docs/11-rough-sculpt-integration.md` first, then the log at the end of `prompts/sculpt-offset-iterations.md`. The last accepted row of that log is the build this prompt starts from. Copy its full command here before the first build:

```bash
# START BUILD: paste the accepted command from the offset prompt's report
```

If that log has no accepted candidate, stop and tell me.
</context>

<goal>
Reshape the shallow scoop on the thumb face around the window so it reads like the sculpt's, without thinning the plastic around the windway and without touching the window itself.

The sculpt's scoop, measured on its mesh, as shares of the body's section at the neck (52.2 mm on the sculpt, about 40 mm on P4):

| Measure | Sculpt, share of section | On P4 | Baseline now |
|---|---:|---:|---:|
| Length along the jet, rim to rim | 0.40 | 16.2 mm | 24 mm |
| Of that, on the neck side of the window's center | 0.13 | 5.4 mm | 6.4 mm |
| Of that, on the far side | 0.27 | 10.8 mm | 17.6 mm |
| Width across the jet, rim to rim | 0.63 | 25.5 mm | 29.1 mm |
| Depth under the rim chord | 0.057 | 2.3 mm | setting 2.2 mm, measured less |

Sized this way the sculpt's scoop is smaller than the baseline's, mostly on the far side. An earlier draft scaled it by volume (1.089) and got a larger scoop; that scale was dropped for the neck and is not used here. The first thing to settle is whether the shares above are the right reading, so step 1 is a look, not a build.
</goal>

<what_moves_what>
Every `bowl_*` key is in the voicing hash. Each scoop that differs is a new voicing with no η_w, the same standing as the start build.

- `bowl_half_length_mm` (12.0): half the length along the jet.
- `bowl_centre_xw_mm` (10.0): the center along the jet, measured from the windway exit. The window's center is about 4.4 mm from the exit.
- `bowl_half_width_mm` (14.53): half the width across the jet.
- `bowl_depth_mm` (2.2): a setting; the depth measured on the mesh comes out smaller.
- `bowl_floor_exponent` (2.0) and `bowl_rim_exponent` (1.5): how flat the floor is and how soft the rim.

The window, the windway exit and the labium do not change. The sculpt's small round opening is not adopted.
</what_moves_what>

<iterations>
Change one thing per build. Give each build its own suffix (`scoop-l8`, `scoop-l8-w13`, ...). Add one row to the log after each.

1. **Look first.** Render the start build's thumb face and lay it beside `addon_renders/rough-sculpt-reference/sculpt-thumb-face-grid.png`. Tell me whether the baseline scoop already reads like the sculpt's before changing anything. If it does, stop here.
2. **Length and center.** Trial: `bowl_half_length_mm=8.1`, `bowl_centre_xw_mm=7.1`. Then step toward the baseline's 12.0 and 10.0 if the checks below fail.
3. **Width.** Trial: `bowl_half_width_mm=12.8`.
4. **Depth.** Raise `bowl_depth_mm` in steps of 0.3 until the measured depth is 2.3 mm, or until a plastic check stops it.
5. **Rim and floor.** Only if the profile still looks wrong in section: one build each for `bowl_rim_exponent` 1.2 and 2.0.
6. **Thumb clearance.** After the outline is settled, confirm both thumb holes keep an uncut sealing rim and 10 mm to the window. If the scoop now reaches one, shrink the scoop on that side before moving the thumb.
</iterations>

<rules>
- The window must read back unchanged: 8.89 × 9.05 mm, exit 1.20 mm high, labium 20°. `voicing_dimensions` reports it.
- `bowl_local_plastic` must pass with zero wide thin-plate probes, and the plate under the windway's exit corners must be no thinner than the start build's. Compare the numbers, not only the status.
- `windway_floor_lip`, `voicing_keepouts` and `pocket_blend` must pass.
- A candidate is acceptable only with no unexpected failed check.
- Extend `bowl_math.py` or `bowl_cut.py` only if the existing keys cannot give the sculpt's uneven slopes, and only after showing me the section that proves it.
- Do not edit `variants.toml` or the presets, and do not touch `addon_out/baseline-print-P4-bowl-80/`.
- Record every build's voicing hash. Two builds with the same scoop must have the same hash.
- At most eight builds per round. Then stop and report.
</rules>

<report>
End each round with:

1. The log table, updated in this file.
2. The best candidate's command in full, its voicing hash and its check summary.
3. Thumb-face, window-along and window-across views of the best candidate from `addon_renders/<id>/`.
4. The plastic numbers under the exit corners, start build against candidate.
5. What you would try next and why, or the decision you need from me.
</report>

## Log

| Build suffix | Half length | Center | Half width | Depth setting | Measured depth | Voicing hash | Unexpected failures | Least plate under the exit corners |
|---|---:|---:|---:|---:|---:|---|---|---:|
| start build | 12.0 | 10.0 | 14.53 | 2.2 | | | | |
