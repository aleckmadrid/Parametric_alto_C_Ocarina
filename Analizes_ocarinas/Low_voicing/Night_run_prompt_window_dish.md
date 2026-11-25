# Night run: a smooth window and dish for the low voicing

A prompt for an Opus session that runs unattended for 3 to 4 hours. Written 2026-11-25 by the session that built series 3. Start the session in the worktree `D:\Users\alexv\Documents\GitHub\Parametric_alto_C_Ocarina\.claude\worktrees\low-voicing` (branch `low-voicing-experiment`) and paste everything below the line.

---

You are continuing an experiment on a parametric 12-hole alto C ocarina (a Blender add-on). The owner is asleep. You have 3 to 4 hours and nobody to ask. Your job tonight is to produce a wide range of built, checked and pictured experiments on one narrow problem, so that the owner can pick a direction in the morning. Breadth and honest records matter more than one polished result.

## The problem

The voicing (the window and labium) sits on the thumb face of the body, in a wall that is thicker than usual there (5 to 6 mm on the thumb face, 3 mm on the finger deck). The owner wants the window to sit in a smooth oval dish in that thick wall, as on two reference pictures:

- `Analizes_ocarinas/Low_voicing/reference_photos/night_run_targets/target_1_game_render_oval_dish.png`: **the main target.** An oval dish with one clear rim and a smooth floor, long along the body, the window hole inside it, close to the foot of the neck. No second edge inside the dish.
- `.../target_2_blue_ceramic.png`: a deeper scoop on a ceramic instrument. Secondary.
- `.../owner_markup_cut_above_window.png`: the owner's markup of what looked wrong earlier (a cut reaching the body above the window and around the neck).

Look at these three pictures first. They are third-party images kept on this disk only: do not commit them, and do not copy them elsewhere.

**Every attempt so far failed on the look.** The owner's words, in order:

- "the round cut goes above the voicing height and leaves an uneven finish"
- "the dish should not cut above the upper of the voicing window, that is what is causing the bad finish"
- "drop the dish just work on the window ramp shape to mirror this or the spencer"
- "the s3-v2 is getting there however the scoop is giving really inconsistent results, aim for the mre oval window of the first image rather than the spencers"
- "none of them work the scoop leaves a non smoth surface, another aproach that comes to mind is the window and the dish being separate, allowing to different windows with smothing applied"
- "this experiments fails"

So the bar is the surface: one smooth form around the window, read by eye from the pictures. A body that passes every check but shows facets, steps, a second ring or a seam has failed.

## What has been tried (do not repeat these as they are)

Read section 14 (14 to 14.5) of `Analizes_ocarinas/Low_voicing/Low_voicing.md` and the block "Handover of 2026-11-25" at the end of `Experimental_lower_voicing_handover.md` before you build anything. In short:

| Trials | Way | Why it failed on the look |
| --- | --- | --- |
| `s3-u1`, `s3-u6` | round dish drawn into the wall thickness | cut into the body above the window and around the neck |
| `s3-v1` to `s3-v3` | oval "ramp scoop", wall rising evenly from the middle | no floor, no rim: an uneven slope |
| `s3-w1` to `s3-w3`, `s3-w6` | oval with a level floor and a rim | faceted rim; the add-on's round window cone showed as a second edge inside |
| `s3-w4`, `s3-w5` | an ellipsoid cut out of the shell by a Boolean | fails the check `voicing_keepouts` |
| `s3-d1` to `s3-d4` | the dish as its own shape, finer mesh, kink-free rim; two window cuts | the dish is smooth, but the window's own cut still shows inside it (a cone, or the ramp as a wedge) |

What I believe is the root cause, for you to test and not to take on trust: **the dish and the window cut are two shapes made by two different pieces of code, and where they meet there is always a visible edge.** The add-on cuts the window with a cutter that flares 2.5 mm to each side and reaches 1 mm above the window's outer face; the dish is drawn into the shell before that. Smoothness probably needs one of: a window cut designed to end exactly on the dish floor; a dish floor designed to follow the window cutter's own surface; or a smoothing pass over the finished surface that leaves the acoustic parts alone.

## The working body (fixed tonight)

Seed P4 at 80 cm³ only. Do not build other bodies. Settings, as in trial `s3-v2` / `s3-d1` of `Analizes_ocarinas/Low_voicing/series3_trials.py`:

- port 20°, pipe +4° into the chamber, 57 mm long;
- cone neck 25.4 mm at the body, 15.2 mm at the mouth end, its outside tilted 6° (`cone(tilt=6.0)` in the runner);
- wall 3 mm on the deck, 6 mm on the thumb face (`uneven(1.0, 2.0, ...)`). You may also try 5 mm and 7 mm on the thumb face where depth matters; 7 mm fails the check `volume_capped_air` on its own, so note that when it happens.

## How to build and look

All experiment code is outside the add-on and hooks in from `series3_trials.py`. Read `uneven_wall.py` (the wall and the dish), `tandem_neck.py`, `blend_fillet.py` (a rolling-ball smoothing on a voxel field, run in the system Python), `sheet_series3.py` and the trial table in `series3_trials.py`.

One build, from the root of the worktree (Git Bash; set the encoding, the console is cp932):

    PYTHONIOENCODING=utf-8 "/c/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b --factory-startup --python Analizes_ocarinas/Low_voicing/series3_trials.py -- --only P4:s3-d1 > some.log 2>&1

- A build takes 2 minutes with the mesh split once and 5 minutes split twice. Run **three at a time** in the background, never more, and work on the next idea while they run.
- The result of a trial is `Analizes_ocarinas/Low_voicing/trials_s3/P4_<trial>.json` (checks, hole sizes, voicing hash, plastic) and pictures in `Analizes_ocarinas/Low_voicing/images_s3/P4_<trial>_*.png`. **Open the pictures** `_thumbface`, `_window`, `_back34` and `_section` for every trial and judge the surface yourself against target 1. The checks do not judge the look.
- A line `[P4-80-<trial>] OK` or `UNEXPECTED FAILURES: ...` ends each log.
- If a row fails only `cavity_mode_computed` with "no Python with numpy and scipy was found", the run was disturbed: build it again.
- Write new scripts with the Write tool. A Bash heredoc that contains triple quotes fails in this shell.
- Add closer pictures of the dish if the standard ones are not enough (the runner's `pictures()` function shows how views are added). A raking-light or section view across the dish is worth having: facets and seams hide in a flat-lit top view.

## What to explore

Use your own judgement and go wide. Give every family a letter and number its trials (`s3-nA1`, `s3-nA2`, ...; group `night`). At least these families, and others you think of:

- **A. A window cut made for the dish.** Vary the add-on's hashed cut settings through preset keys (`window_cut` = `fan` / `cone` / `ellipse`, `cone_widen_mm`, `cone_flare_exponent`, `shelf_angle_deg`): find the cut that leaves no second edge on a level dish floor. Each such change is a new voicing hash; record it.
- **B. A dish floor that follows the window cutter.** Shape the floor so it meets the add-on's cutter surface tangentially (the cutter's top is 1 mm above the window's outer face; its flare is in `ocarina_addon/voicing_geo.py`, read only).
- **C. Dish shape and place.** Length, width, rim width, where it starts against the window's upper edge (the owner dislikes any cut above that edge; show both sides of that line and say which is which), shift along the body, a dish that is deeper toward the labium, a superellipse instead of an ellipse.
- **D. Smoothing as a last pass.** A rolling-ball or Laplacian smoothing of the thumb-face surface around the window after the dish is drawn and before the add-on cuts the window, or a voxel closing/opening as in `blend_fillet.py`, limited to a region so the window, the labium and the holes are not touched.
- **E. One shape for both.** Build the dish and the outer part of the window flare as a single lofted cutter (rings from the window outline at the outer face up to the oval rim at the shell's surface) and subtract it from the shell before the add-on cuts the window proper. The earlier ellipsoid failed because it left plastic standing at the window's upper edge; a loft from the window's own outline does not have that fault.
- **F. Mesh.** Refine only around the dish instead of everywhere, so that a fine rim does not cost 5 minutes a build. Mind T-junctions: the shell must stay one closed solid.
- **G. Wall depth.** The same best shapes at 5, 6 and 7 mm on the thumb face.

Work in rounds. In each round: decide 3 to 6 trials, build them three at a time, open the pictures, write down what you see, and let that choose the next round. When a family clearly cannot give a smooth surface, say why in the log and move on; when one looks promising, vary it further. Aim for 40 or more built trials by the end. **Do not stop after a few trials, and do not stop because one looks good:** keep going until the time is used, then finish the write-up. If something blocks one family (an error you cannot fix in 15 minutes), record it and continue with another.

## Hard rules

- **Do not edit, commit or merge any add-on file**: `ocarina_addon/`, `kernel/`, `params/`, `tests/`, `tools/`, `docs/`, `calibration/`, `measurements/`. They are an uncommitted copy of a snapshot and show as modified in `git status`; leave them exactly as they are. Change behaviour only from outside, the way `uneven_wall.py` and `tandem_neck.py` do (wrapping functions at run time). Reading them is fine.
- **Do not commit and do not push.** Leave everything in the working tree for the owner.
- **Seed P4 only.** No prints, no rule changes, no preset changes.
- **The acoustic parts stay sound.** The window area (62.8 mm² for the rule's cut), the labium edge and the pipe must not be changed by the dish or the smoothing. A trial may use a different window cut (family A); then it has a new voicing hash, which no test print has checked. Mark every such trial plainly.
- **Never thinner than 1.32 mm of wall anywhere, and never thinner than the rule's 4 mm under the dish** unless a trial is named as testing exactly that.
- **Every check must be reported as it came out.** Do not loosen a check, do not skip one, do not describe a failing body as passing. A good-looking body that fails a check is still worth recording, with the failure named.
- Keep the earlier trials and their files. Add; do not rewrite `s3-u*`, `s3-v*`, `s3-w*`, `s3-d*`.
- Third-party material stays out of git: `ref_oot_blend/models/`, `ref_oot_blend/images/`, `reference_photos/night_run_targets/`.
- Write records in plain, direct English, with the owner's words quoted where you rely on them.

## What to leave behind

1. **`Analizes_ocarinas/Low_voicing/Night_run_log.md`**, written as you go (append after every round, so a crash loses nothing): for each trial its name, family, what it changed in one line, the voicing hash if it differs, the checks that failed, and two or three sentences on what the surface looks like against target 1. Give each trial a look grade of your own: A (one smooth form), B (smooth with one visible seam), C (rough).
2. **Sheets** made with `sheet_series3.py` (add calls; each sheet takes 5 to 7 trials): one per family, and one last sheet `sheet_s3_night_best.png` with the best six overall beside `s3-d4`.
3. **Section 15 of `Low_voicing.md`**: what was tried by family, a table of the best ten (settings, hash, checks, grade), what you now think the cause of the roughness is and what evidence supports it, which families are dead ends and why, and the two or three directions you would take next.
4. **A short block at the end of `Experimental_lower_voicing_handover.md`** ("Night run of 2026-11-25/26") with the count of trials, the best three by name, anything that needs the owner's decision (for example a new voicing hash, or a dish that starts above the window's upper edge), and how to rebuild the best one.
5. Your final message: the same in a few lines, leading with whether any trial reaches the target and which pictures to open first.

Start now: read the record, look at the three target pictures and at `sheet_s3_dish_P4.png`, then begin round one.
