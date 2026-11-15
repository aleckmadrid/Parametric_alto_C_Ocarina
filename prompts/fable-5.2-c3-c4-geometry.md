# Prompt: kernel corrections, cavity, voicing, holes and wall stack (checkpoints C2b–C4), Fable session

This prompt covers three checkpoints of the add-on build:
- **C2b:** two kernel corrections that the audit of C0–C2 asked for. The voicing stays a teardrop at every volume, and the fitter estimates `k_hole` from the ladder data.
- **C3:** the cavity Geometry Nodes group.
- **C4:** the voicing geometry, hole placement, inward tubes, wall stack, Booleans and pre-export checks.

C3 and C4 need the most spatial judgement, so this session runs on Fable 5.2 as the main model. C2b goes first, because the voicing geometry in C4 depends on the corrected window rule. The stage commands and the final pass (C5–C6) go back to the cheaper advisor setup afterwards.

## How to run it

- **Model:** Fable 5.2 as the main model. Type `/advisor` and switch the advisor off. A Fable main model can only use Fable itself as its advisor, so the review role moves to the tests (C2b) and to the geometry checks and renders that this prompt requires (see `<geometry_verification>`). If you want a second read anyway, set `/advisor fable`; each call re-reads the whole transcript, so it costs more as the session grows.
- **Effort:** `high`. Do not use `xhigh` or `max` unless a checkpoint fails on reasoning, not on tooling.
- **Usage credits:** turn them on with a monthly cap before you start. Fable costs about twice as much per token as Opus.
- **Start:** open a new session in the repository root, check out the branch `addon-v1`, and paste everything below the line.
- **If it stops before C4 is done** (a usage limit or a crash): start a new session, paste the same text again, and add this line:

  > Resume: read `prompts/addon-v1-notes.md` on the branch `addon-v1` and continue from the first checkpoint that is not marked done, up to C4.

- **When C4 is done:** check the status table, the C2b evidence, the geometry evidence and the renders in the notes file. Then start a session on Opus 5.5 (or Sonnet 5.5) with Fable as the advisor, paste `prompts/fable-5.2-addon-implementation.md`, and add its resume line. It picks up at C5. That older prompt still describes C0–C2 as work to do, says the kernel has 9 tests, and describes the rounded-rectangle window; the notes file overrides all three.

---

<context>
I'm building a 3D-printed, parametrically tuned 12-hole alto C ocarina (A4 to F6). The repository is `Parametric_alto_C_Ocarina`. The physics is a lumped Helmholtz model: pitch depends on chamber volume and on the conductance of each opening (window and holes), not on chamber shape. That is what lets the outside of the instrument be shaped freely, while the acoustic parts are generated and solved.

The next step is a physical test campaign with plain, generated test bodies (`docs/04-testing-phase.md`). To run it I need a Blender 5.1 add-on, backed by the existing Python kernel, that produces the printable bodies. The same tool will later carry sculpted exteriors, so build it as the real add-on, not a throwaway script.

**State of the work.** Checkpoints C0–C2 are done on the branch `addon-v1` and were audited: the standard-library kernel sizes the voicing and the holes, runs the checks and fits measurements. `python -m unittest discover -s kernel -v` passes 100 tests, and `python kernel/sizing.py --table` reproduces the doc 04 table. Nothing has been printed. Every constant is pre-calibration.

Read these first. The decisions in them are settled, except where `<design_decisions>` below changes them:

- `prompts/addon-v1-notes.md`: the build notes and the hand-over. Read its "Handoff for the C3 session" section before anything else. It gives the kernel API with units, the volume bookkeeping, the checks that are expected to fail, and the module-name and `sys.path` cautions for Blender.
- `docs/04-testing-phase.md`: the test plan this build serves (shapes, sizes per step, stages, gates).
- `docs/02-unified-plan.md`: architecture, parameter classes, the Phase 4 build order and gate, the pre-export checks, the mesh precision and print-practice rules.
- `docs/03-parametric-findings.md`: equations and design rules R1–R14.
- `Analizes_ocarinas/Miracle_M/Miracle_M.md`: the reference instrument. Section 4.2 holds the hole layout coordinates; section 5 the voicing (a teardrop, broad end at the windway).
- `references/heuer-video2-alto-c-tolerances.md` and `references/heuer-series-overview.md`: Chris Heuer's window length band (soft 8.89 / medium 9.65 / loud 10.41 mm) and his teardrop window for 12-hole range (video #5).
- `prompts/fable-5.2-addon-implementation.md`: the full build prompt (C0–C6). Read it for the whole picture. Its design decisions apply here, except the rounded-rectangle window; its scope is wider than this session's.

The ECAN3 analysis is on the branch `ecan3-experimental` under `Analizes_ocarinas/ECAN3_experimental/` (read `ECAN3_experimental.md` and `METHOD.md` with `git show`). It is the evidence behind inward tubes on small holes and the split-subhole placement. Use it as reference only; don't merge that branch. Untracked STL files of the analysed instruments may sit in the working copy under `Analizes_ocarinas/ECAN3_experimental/models/`; you may load them to compare proportions, but never copy their geometry.
</context>

<goal>
Build checkpoints C2b, C3 and C4, so that the next session only has to wire the stage commands and reports (C5) and finish the test suite (C6).

Done means:
- **C2b:** the window rule produces a teardrop at every volume (no rounded-rectangle switch); the fitter reports a `k_hole` estimated from the data next to the convention value; the kernel tests pass, old and new; the doc 04 table and the notes carry the new window and windway sizes.
- **C3:** headless Blender 5.1 produces every cavity preset (P0–P3) at every Stage 2 volume, each within 0.5 % of its target, and the voicing port does not move when the cavity is scaled.
- **C4:** a full P1 body at 80 cm³ exports as a manifold STL, passes every pre-export check (or fails only the checks that the notes list as expected), and its hole sizes and chimney lengths measured from the mesh match the kernel within 0.05 mm (the Phase 4 gate). A P0 body at 80 cm³ and a P0 body at 65 cm³ (the one with an inward tube) also export and pass the same checks, and the P0 body at 125 cm³ shows the widest teardrop voicing building cleanly.

**Scope limit:** stop after C4. Don't write the stage commands, the Markdown sizing report or the headless test suite of C5–C6, even if you finish early. Time left goes into the geometry checks, edge cases (P2 and P3 at 80 cm³, P0 at 95 and 125 cm³) and the notes for C5.
</goal>

<design_decisions>
These are decided. Build to them and don't reopen them. The full wording is in `prompts/fable-5.2-addon-implementation.md`; this is the part that matters for C2b–C4, including two owner decisions made after the audit.

**Owner decision 1: the window and windway stay a teardrop at every volume.** Chris Heuer's window length table assumes a teardrop window, so the voicing keeps that shape across the whole volume ladder. The window length stays at the rating length (medium 9.65 mm, from the windway exit to the labium edge). Above the volume where today's teardrop family runs out (about 88.6 cm³, where the broad end reaches a circle as wide as the window is long), the teardrop grows wider than it is long. The windway width stays equal to the broad end, so it grows steadily with volume and never steps down. Rules for the shape family:
- broad end at the windway, narrow end (1.0 mm tip radius) at the labium;
- the window length never changes with volume;
- the area grows steadily with the width, and the outline stays smooth and printable;
- below the old limit, keep today's teardrops exactly, so the 65 and 80 cm³ windows and stubs V-a and V-d don't change. If you find a geometric reason this cannot hold, record it in the notes and say what changed;
- remove the automatic switch to a rounded rectangle. Keep `shape="rounded_rectangle"` as a forced option only, because stub V-b compares window shapes at equal area (63 mm²).

Expect wide windows at the top of the ladder. A rough estimate gives a broad end of about 11–12 mm at 95 cm³, 13–15 mm at 110 cm³ and 16–19 mm at 125 cm³, against 8.5 / 10.6 / 12.9 mm for the old rectangle. Report the real numbers, and the windway width and W/h at each step. Stub V-c becomes a 124 mm² teardrop.

**Owner decision 2: the fitter estimates `k_hole` from the data.** Today `fit_bodies` in `kernel/fitter.py` (around lines 295–313) solves k by bisection so that the geometric mean of the P0 position factors (psi) is 1. It never compares candidate values of k against the measurements. The four P0 ladder bodies share one psi per hole name and have different diameters, so they do constrain k. An audit check on noise-free synthetic data (truth built with `synthetic.make_truth(psi=..., normalise=False)`, P0 bodies of `synthetic.round1_set`) found:
- the weighted sum of squares of the ln G residuals, with psi profiled out per hole group, is smallest at the true k (1.070) every time;
- the fitter returned 0.985 or 1.164 when psi was scaled by ±5 %, 0.775 or 0.566 at +20 % or +40 %, and 1.517 at −20 %;
- P0-110, sized from those fitted constants and played with the true physics, was off by up to about 10 cents at +20 % or +40 %, and 27 cents at −20 % (Gate 3 allows ±20 cents). Doc 04 notes that real top holes run 20–40 % smaller than the model predicts, so offsets of this size are realistic;
- with ±5 cents of noise per take (3 takes, 4 P0 bodies, 12 seeds), the profile estimate had no bias but was noisy (median error 4.4 %, worst 13 %), while the convention estimate was biased by about 8 %.

Add a profile-likelihood estimate of k across all bodies (shared psi per group, the existing weights and `k_bounds`), with an uncertainty from the curvature or a likelihood interval. Keep the convention estimate and report both in `FitResult` and `format_report`. Choose by a documented rule which value drives psi and the corrected diameters: for example, the profile estimate when its interval is narrow enough, otherwise the convention, with a message whenever the convention value falls outside the profile interval. A single body has a flat profile, so it keeps today's behaviour.

**Unchanged decisions:**
- **Add-on form.** A Blender 5.1 extension (`blender_manifest.toml`) in its own folder in the repo, with operators that have properties, a Python API and a headless entry (`blender -b --python ...`). No sidebar panel yet; a bare menu entry is fine.
- **Kernel is the source of every number.** The add-on calls the kernel and never re-derives acoustics. Put `kernel/` first on `sys.path` (the module names `config`, `checks` and `holes` are generic) and pass `params=` explicitly. The kernel stays standard-library Python with no Blender imports. Outside C2b, kernel changes are allowed only for real bugs, each with a test.
- **Procedural cavity from Geometry Nodes**, built from Python so it is reproducible and versioned. One shared node group: a lofted spine with cross-sections, width and height given at 7 stations and interpolated with a smooth spline, a superellipse section exponent, end caps and a voicing-port anchor. Shape inputs are ratios; size is solved. Scale exactly to a target volume about the voicing port. Station values are numbers that can be written from TOML. Presets: P0 control egg (2.2 : 1.5 : 1), P1 teardrop and P2 tailed gourd (smooth, simple parametric shapes whose internal lengths match doc 04: P1 111 mm and P2 126 mm at 80 cm³), P3 traditional transverse (3 : 1.6 : 1, gently bent spine, provisional).
- **Cavity target volume.** Build the cavity mesh to `BodySizing.cavity_volume_for_mesh_cm3`, not to `v0_cm3`. The invariant after the Booleans is that the capped air equals `v0_cm3`. Cap each hole at the outer skin surface (the hole air through the wall counts in V0) and cap the window at the inner cavity surface (the window throat is neck and is excluded). The throat is about 0.3 % of V0 at 80 cm³ and grows with the wider teardrops, which matters against a 0.5 % tolerance. For P1–P3, pass the real internal length as `L_int_mm` to `size_body`.
- **Voicing geometry comes from the `Voicing` record**, never free-form: the teardrop above, windway exit height 1.20 mm, inlet/exit taper 1.3, length 30 mm, width equal to the window's broad end, labium ramp 20°, edge 0.4 mm, keep-outs 10 mm inside and a 45° flare outside, wall at window 4.0 mm. Store `voicing.version_hash` on the object and check that it is intact before export. Never remesh or smooth the voicing or the chimneys.
- **Holes.** Round, one diameter per hole from the kernel: first prints cut at `holes.solutions["print"][i].d_mm` (k_hole 0.8). Inward tube of `tube_mm` where it is above 0, tube wall from `[hole_rules] tube_wall_mm`. Layout: Miracle finger spacing (Miracle §4.2) with one subhole per hand: sub_L (kernel name `sub1`) between L_ring and L_middle, sub_R (kernel name `sub2`) between R_index and R_middle, both off the finger line. A centre may move up to 2 mm along its row to keep edge gaps (about 3.4 mm minimum next to subholes). Wrap the template onto the deck through the cavity's surface coordinates converted to arc length; each hole axis follows the cavity normal. P0 is too short for the Miracle span, so it gets a compressed test layout; P1–P3 use the real template.
- **Wall stack.** Offset the cavity outward to form the skin: a uniform 4 mm wall for test bodies, with finger-deck, thumb and voicing patches at fixed thickness (deck 4.0 mm). The optional user outer mesh (sculpt envelope, default 15 mm) is a later feature: leave a clean hook for it, but don't build it.
- **Booleans** use the Manifold solver, with Exact as the fallback. After every Boolean, assert that the result is manifold and that the air volume changed by the expected amount.
- **Expected failing checks are not bugs.** Hole pad limits from 65 cm³ (nominal) and 80 cm³ (print), the cavity-mode failure of P2 at 80 cm³ (0.987 × F6) and of P1 at 125 cm³, and `needs_fem` for P1 at 80 cm³. Build these bodies anyway and report the results.
</design_decisions>

<owner_decisions_pending>
These are open with the owner. Build to the current rule and record what you see; don't change the rule.

- **Window tip radius, 1.0 mm,** was fitted to the doc 04 table, not taken from a source. If the window looks wrong in the renders, check it first and say so.
- **P1 and P2 proportions** are loose by design. Record the station values you chose and why.
- **Windway width at the top of the ladder.** Record whether the widest teardrop windways (110 and 125 cm³) still fit the voicing keep-outs and the P0 body at those volumes, with renders. Don't narrow them.
</owner_decisions_pending>

<kernel_verification>
C2b is kernel work, and its evidence is tests and numbers:
- `python -m unittest discover -s kernel -v` passes: the 100 existing tests plus new ones. Tests whose expected values follow from the old window rule (the doc 04 rows at 95, 110 and 125 cm³, and the switch volume) are updated to the new rule, with the reason in the commit message. Tests of the 65 and 80 cm³ rows keep their values.
- New window tests: no automatic rectangle at any ladder volume; window length constant; width and area increase together with V0; the forced rectangle still works for V-b; the hash is stable for the same inputs and changes with every voicing input.
- New fitter tests: noise-free recovery of a truth that breaks the convention (psi scaled 1.2 and 0.8); single-body behaviour unchanged; a noise case with a tolerance you justify. Update `test_k_absorbs_a_psi_scale_that_breaks_the_convention` to the new behaviour.
- Extend `kernel/noise_study.py` with a row for psi offsets, and regenerate the synthetic files with `python kernel/synthetic.py --write-examples` (hashes and window sizes change above 88.6 cm³).
- Regenerate the table with `python kernel/sizing.py --table` and put the new window and windway columns into doc 04.
</kernel_verification>

<geometry_verification>
Spatial mistakes don't show up in unit tests or in a log that only prints "done". Build a geometry check script early in C3, run it after every change, and treat its output as the evidence for C3 and C4. These checks take the place of an advisor's review, so make them measure the mesh, not restate the inputs.

Measure from the exported or evaluated mesh:
- **Volume:** cavity mesh against `cavity_volume_for_mesh_cm3`, and capped air after the Booleans against `v0_cm3` with the cap convention above, both within 0.5 %. Also the air volume change of each Boolean against what it should be.
- **Anchor:** voicing-port position before and after volume scaling, for every preset and volume.
- **Topology:** manifold, no non-manifold or zero-length edges, no self-intersections, one closed shell plus the expected openings.
- **Voicing:** window length, width and area, windway exit and inlet height and width, labium angle and edge thickness, measured on the mesh and compared with the `Voicing` record; the hash intact.
- **Orientation:** the windway exit faces the labium edge, the teardrop's broad end is at the windway, the window opens outward, and nothing intrudes into the keep-outs (10 mm inside, 45° flare outside).
- **Holes:** each diameter and chimney length (ray-cast from the cut) against the kernel within 0.05 mm, the angle between each hole axis and the local cavity normal, the edge gaps between holes, how far each centre moved from the template, and the clearance of every inward tube to the other tubes, the opposite cavity wall and the voicing keep-out.
- **Wall:** minimum wall thickness over the body, against 4.0 mm.

Look at the result as well:
- Render headless to PNG (Workbench is enough): three orthographic views, one isometric view, a section along the windway centreline, and a section through each hole row. Save them under `addon_renders/<body>/` and open each image yourself before you call a checkpoint done. Check that what you see agrees with the numbers. A wrong-way labium or a hole on the wrong face is easier to see than to measure.
- Commit the renders for the C3 presets and the C4 bodies, so that the owner and the next session can review them.
</geometry_verification>

<environment_and_permissions>
- Windows 11. Blender 5.1 is at `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe` (not on PATH; Blender 4.1 is also installed and is not a target). Blender 5.1 bundles Python 3.13 and numpy. System Python is 3.12.
- **Approved without asking:** commit to `addon-v1` as you go; run Blender headless as often as needed; create a project `.venv` (already in `.gitignore`) and install packages into it for offline checking (for example `trimesh`, `manifold3d`, `numpy`, `fake-bpy-module`); write files inside the repository; restructure the add-on code you write; retry a failing Blender run after fixing its cause. **For C2b:** change the window rule in `kernel/voicing.py` and `params/alto_c_12hole.toml`, change the fitter, update the kernel tests whose expected values follow from the old rule, regenerate the synthetic files, and edit `docs/04-testing-phase.md` where the window rule shows: the "teardrop runs out at about 85 cm³" sentence, the window and windway columns of the sizes table for 95, 110 and 125 cm³, and the V-c stub row. The owner approved these edits.
- **Ask first:** pushing to GitHub, merging into `main` or `ecan3-experimental`, installing anything outside the project folder (system software or Blender's bundled Python, which would need admin rights), any other edit under `docs/` or `references/`, other changes to the kernel's public behaviour, and deleting files you did not create.
</environment_and_permissions>

<checkpoints>
- **C2b Kernel corrections.** The teardrop-only window rule and the `k_hole` profile estimate (owner decisions 1 and 2), with the checks in `<kernel_verification>`.
- **C3 Cavity.** The add-on skeleton (`blender_manifest.toml`, headless entry), the cavity Geometry Nodes group built from Python, presets P0–P3, and exact volume scaling about the voicing port.
- **C4 Voicing, holes and wall stack.** Voicing geometry, hole placement on the deck, inward tubes, the wall stack, the Booleans, the pre-export checks from doc 02 (volume, voicing hash, hole floor and pad limits, spacing, wall thickness, range ratio, cavity length ratio), STL export, and the air domain exported for later FEM.

Add a C2b row to the status table in the notes file. At the end of each checkpoint:
1. Run its checks: the kernel suite for C2b; the geometry check script on every body the checkpoint covers, the renders and the kernel suite for C3 and C4.
2. Commit to `addon-v1` with a message that starts with the checkpoint, for example `C2b: teardrop window at every volume, profile fit of k_hole`.
3. Update `prompts/addon-v1-notes.md`: mark the checkpoint done with the evidence (test counts, check output, the render folder, measured values), list decisions and open problems, and write the next concrete step. For C2b, also replace the notes' "k and psi convention" paragraph, the noise table and the doc-differences rows that the new rule changes.

A checkpoint is not a stop: record it and go straight on, up to the end of C4. If a checkpoint fails its done condition and you cannot fix it, record why, mark it blocked, and continue with work that does not depend on it.

When you resume, read the notes file and `git log` on `addon-v1` first, check that the last checkpoint marked done still passes its checks, then continue from the first checkpoint that is not done. Don't redo finished work.
</checkpoints>

<notes_for_c5_c6>
Add these to the notes file for the next session, with anything new you find:
- The full prompt's criterion "position factors within 1 % with ±5-cent noise" cannot pass as written: the noise study gives 2–4 % at the 95th percentile. The noise-free 1 % criterion passes. The owner should reword it before C6.
- The full prompt still describes the rounded-rectangle window. The teardrop-only rule from C2b replaces it, and Stage 1 stub V-c is a teardrop.
- The reports print `sub_L` and `sub_R`; the kernel and the measurement files use `sub1` and `sub2`.
</notes_for_c5_c6>

<working_approach>
You are the owner and long-term maintainer of the add-on code and the kernel, and their design is up to you within the decisions above. Keep `prompts/addon-v1-notes.md` as your working notes: the decisions you made and why, problems found, and what remains.

Where the kernel's equations and a doc disagree, the docs record decisions and the kernel records the maths: flag the conflict in the notes, pick the reading that matches the decisions, and keep going. Never invent measured values; synthetic data stays labelled synthetic.

Before you start, say in a line what you're about to do. Brief updates while you work help me follow along.
</working_approach>

# Finishing work

Please avoid stopping while you still owe work I asked for. Be persistent and do not stop unless needed. While status notes are welcome, as is clarifying with me on open decisions, carry on with work that does not depend on my answer without unnecessary stops. If you notice yourself inviting me to redirect you or offering to wait, instead proceed on the next part of the task. You may meet ordinary obstacles like errors, timeouts, locked files, empty results or failing tools. Diagnose them first, and when they are not real blockers, work through them with the access you have (wait and retry, fix the request, use another tool or source) rather than stopping unnecessarily. If someone clearly decided something is a hard blocker, such as a file marked not to be touched, access that was intentionally withheld, or a safety guardrail, leave it alone, say plainly what you found, and look for another safe way to finish the task. Stopping before the task is complete is very rarely merited - as in when the task can't move forward without user input, or where the blocker is deliberate and should not be worked past. This does not override the need for confirmation on the actions listed under "Ask first".

Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if a check fails, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.

# Communicating clearly

Write for an intelligent but low-context reader. The person reading has not seen your tool calls, your reasoning or the files you opened, and may be switching in from other work. Messages should generally be self-contained: the reader should understand what you mean without having to dig for other context. Put the key points in the first few sentences. Practice progressive disclosure in your sentence order, and do not use undefined references and ideas in line 1 that won't make sense until the reader reaches line 12. Use plain words, and write in clear, understandable full sentences. Do not use a term or abbreviation that you made up during the work - say what the thing is in a way any reader would understand. Write mostly in the style of ASD-STE100 Simplified Technical English: short sentences, one idea per sentence, active voice, and consistently using the same word for the same thing. Use a paragraph of flowing prose where ideas connect, and keep bullets for lists of separate items. Leave out unnecessary details unless the reader asks and practice concision, but do ensure that your messages have the key context. Aim to make your user-facing text as human-readable and clear as possible.

Close with a short recap that stands on its own: which checkpoints are done and how each was verified (tests for C2b, check script output and renders for C3 and C4), the new window and windway sizes at each ladder step, the `k_hole` values from both estimates on the synthetic set, what failed or is expected to fail, where the renders are, and the exact headless command that builds the P1 body at 80 cm³.
