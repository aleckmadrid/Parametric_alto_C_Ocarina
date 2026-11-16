# Prompt: hand layout fix, stage commands and finish (checkpoints C4b–C6), long Fable session

This prompt covers the rest of the add-on build in one long unattended run (planned for 3–4 hours):

- **C4b:** the hand layout fix and the soft ergonomic checks, built to the rules of doc 06 that the owner accepted on 2026-11-15, plus a cavity-mode check from the computed first mode.
- **C5:** the stage commands (Stage 1 stubs, Stage 2 bodies, Stage 3 from a constants file) and the Markdown sizing reports.
- **C6:** the headless test suite, the packed extension, the README section and a final pass over the acceptance criteria.

C4b and C5 must be finished. C6 gets the time that is left.

## How to run it

- **Model:** Fable 5.2 as the main model. Switch the advisor off (`/advisor`, then off): a Fable main model accepts only Fable as its advisor, and each advisor call re-reads the whole transcript. The review role goes to the geometry checks, the renders and one fresh-context review per checkpoint (see `<verification>`).
- **Effort:** `high`. This is Anthropic's recommended level for long unattended agentic runs on Fable 5.2. Use `xhigh` only if a checkpoint fails on reasoning, not on tooling.
- **Before you leave it:** turn on usage credits with a monthly cap; turn on keep-awake in the desktop app; use auto mode or an allowlist for the Blender command, `python` and `git commit`, so that no permission prompt stalls the run.
- **Start:** new session in the repository root, branch `addon-v1`, paste everything below the line.
- **If it stops early** (a usage limit or a crash): new session, paste the same text, and add:

  > Resume: read `prompts/addon-v1-notes.md` on `addon-v1` and continue from the first checkpoint that is not marked done, up to C6.

- **When it ends:** read the status table and the evidence in the notes file, and look at the top views of P1-80, P2-80 and P3-80 with the hole names. Read `git diff` for `ocarina_addon/` and `params/` too, not only the summary: a model told that it owns the code sometimes changes behaviour nobody asked for and leaves small changes out of its recap. **Don't print Stage 2 until you have read the `ergo_*` warnings** and decided whether the hand template needs scaling: the layout is frozen at that print. Doc 02 Q10/Q11 (outer body, P4) wait for a hand check on a printed P2.

---

<context>
I'm building a 3D-printed, parametrically tuned 12-hole alto C ocarina (A4 to F6). The physics is a lumped Helmholtz model: pitch depends on the chamber volume and on the conductance of each opening, not on the chamber shape. The next step is a physical test campaign with generated test bodies (`docs/04-testing-phase.md`). A Blender 5.1 add-on backed by a standard-library Python kernel produces those bodies. The same add-on will later carry sculpted exteriors, so it is the real tool, not a throwaway script.

**State.** Checkpoints C0–C4 are done on `addon-v1`. The kernel passes 120 tests. The add-on builds eight bodies (P0 at 65, 80, 95, 110, 125 cm³; P1, P2, P3 at 80 cm³) as manifold STL files whose holes, chimneys, voicing and capped air match the kernel; the check script measures the STL read back from disk. After C4 the owner found the hand layout wrong. Doc 05 reviewed it, and doc 06 challenged doc 05 with better references (two CAD layouts with a true scale). Nothing has been printed, and every constant is pre-calibration. The hole layout must be frozen before Stage 2 is printed (doc 04 D10), because the fitted position factors belong to one layout. That is why C4b comes first.

Read these first:

- `prompts/addon-v1-notes.md`: the build notes and the hand-over. It overrides every older prompt. Read "Status", "Open problems" (items 8, 13, 14), "Notes for C4b" and "Notes for C5 and C6".
- `docs/06-ergonomics-challenge.md` §3, §5 and §6: the rules C4b builds. Where doc 05 and doc 06 differ, doc 06 holds.
- `docs/05-ergonomics.md` §3–§6: the original review, for the parts doc 06 does not change.
- `Analizes_ocarinas/Ergonomic_reference_12hole/measure_cad_references.py` and its output `measure_cad_output.md`: the hand-frame metrics that become `ocarina_addon/ergonomics.py`.
- `tools/cavity_modes_fd.py` and `addon_checks/cavity_modes_fd.md`: the first cavity mode of an air mesh.
- `docs/04-testing-phase.md`: stages, bodies, stubs and gates. `docs/02-unified-plan.md`: amendments A11–A14, questions Q8–Q12, pre-export checks.

The ECAN3 data used by doc 06 sit on the branch `ecan3-experimental` (read with `git show`). The untracked folder `Analizes_ocarinas/ECAN3_experimental/` in this working copy holds third-party STL files and local voxel caches. Read them if useful, never copy their geometry, and never commit that folder.
</context>

<goal>
Finish the add-on so that the owner can print Stage 1 and Stage 2 from one command each, with a hand layout the owner accepted and a report that lists every check.

Done means:

- **C4b:** every built body places its subholes and hands by the rules below; the `ergo_*` checks report `ok` or `warn` and never fail; the cavity-mode check uses the computed first mode; all eight bodies build with no unexpected failure, and no acoustic number changed from C4.
- **C5:** `stage1` and `stage2` generate end to end (STL files, blank measurement templates, one Markdown report per stage whose sizes agree with doc 04), and `stage3` runs from `calibration/synthetic-fitted-constants.toml` with the round-1 tubes kept.
- **C6:** a headless Blender test suite and plain-Python tests run green; a pack script produces an extension zip that installs and builds a body in a clean Blender profile; the README says how to install, run the stages and run the tests; the final pass lists every acceptance criterion with the actual output.
</goal>

<owner_decisions>
Decided on 2026-11-15. Build to them; don't reopen them.

1. **C4b uses the rules of doc 06 §5 and §6.**
   - Subholes: sub1 (sub_L) from L ring, 9.5 mm; sub2 (sub_R) from R middle, 7.5 mm. Each slides along the normal of its own hand's pinky → index line, toward the fingertips. Parent and slide are preset parameters. An edge-gap relaxation may lengthen a slide up to 11 mm, never turn it around. The sideways clamp in `place()` (35 % of the half section) must not shorten a subhole slide without a message: give subholes their own limit or report the clamp.
   - The `ergo_*` checks and their `ok` ranges are the "Proposed" column of doc 06 §5, including the replacements (`ergo_hands_parallel` and `ergo_hand_offset` instead of `ergo_hand_tilt`; `ergo_hole_lean_end` and `ergo_hole_lean_side` instead of `ergo_hole_tilt`). The parent search looks at the holes of both hands. Every limit lives in a new `[ergonomics]` table of `params/alto_c_12hole.toml`.
   - A new status `warn`, beside the code's existing `pass`, `needs_fem`, `fail` and `info`. The docs say `ok` where the code says `pass`; keep the code's names. A warning is never a failure: `unexpected_failures` ignores it, `--strict` ignores it, and reports list warnings in their own block.
   - P0 keeps its relative test layout (doc 02 Q12). Its `ergo_*` checks report `warn` with the message "taped test body, not a hand layout", and its renders carry that caption.
   - Q8 is answered: the left subhole's parent is L ring. Drop the L index option.
2. **Cavity mode from the computed first mode (doc 02 Q9 / A12, as revised in doc 06 §3.10).** Add a check that computes the first mode of each body's exported capped air mesh (holes and window closed) with the method of `tools/cavity_modes_fd.py`: `pass` at 1.3 × F6 or more, `needs_fem` from 1.0 to 1.3 × F6, `fail` below 1.0 × F6. It needs scipy and trimesh, which Blender's Python lacks, so it runs in system Python (or the project `.venv`) on the exported STL; the design of that hand-off is yours. If the solver cannot run, the check must say so with a visible status; it must never pass by default. The kernel's c/(2L) check stays in the kernel unchanged and shows in the report with status `info`, so it no longer decides pass or fail for the add-on, and its entries in `checks_geo.expected_failure` go. The report calls the new result a desk check with closed holes: the 1.3 margin is a guess, and the Stage 2 spectra remain the real test. Acceptance: within 2 % of `addon_checks/cavity_modes_fd.md` on the same bodies (P1-80 1.63 × F6, P2-80 1.40 × F6).
3. **Short decks overlap the hands (doc 06 §3.5).** When the deck is too short for span plus rest space, the layout slides the two hands toward each other along their own lines and keeps the finger pitch. The amount is a preset parameter. The layout never compresses the finger pitch silently. The hard geometry checks (edge gaps between holes, hole to voicing, tube clearances) limit the overlap. A deck that is still too short gives `ergo_rest_space` = `warn` with the missing length in the message. P3-80 must then build with no unexpected failure; the old `hole_layout` check stays as the record of moves, and its compression part moves into the `ergo_*` checks.
4. **Scope:** C4b, then C5, then C6.

Still open with the owner. Build to the current rule, record what you see, and don't decide them: the separate outer body and the P4 body (Q10, Q11: decided after a hand check on a printed P2, so P4 is not in the Stage 2 list); the window tip radius and the wide-teardrop family; Stage 3 keeping the printed V0 (keep it as the default); the rewording of the "position factors within 1 % with ±5-cent noise" criterion; the licence.
</owner_decisions>

<checkpoint_notes>
The working detail is in "Notes for C4b" (rewritten to the decisions above) and "Notes for C5 and C6" in the notes file. This section holds the acceptance and what those notes lack.

**C4b.** `ocarina_addon/ergonomics.py` has no Blender imports and ports the hand-frame metrics of `measure_cad_references.py`; the analysis script then imports it, so the checks and the reference numbers come from one place. The top-view render gets the hole names beside the holes. Rebuild all eight bodies with `tools/geometry_check.py -- bodies --renders`.

Acceptance for C4b:
- sub_L 9–10.5 mm from L ring and sub_R 7–8.5 mm from R middle, each within 20° of its hand line's normal; smallest edge gap still at least 3.4 mm; every tube clearance check still passes.
- The `ergo_*` results are measurements to report, not targets to reach. The C4 layout already suggests warnings on P1-80 and P2-80 (left hand span 48.9 mm against 50–60, perhaps a finger pitch, the lean of the pinky holes toward the ends, rest space on P1): the wrapped template comes out a few percent smaller than the Miracle's. Don't tune the template, the presets or the limits to clear a warning. Report each warning with its number; whether to scale the template is my decision, and I must make it before Stage 2 is printed.
- The `ergonomics.py` metrics reproduce the reference rows of `measure_cad_output.md` (Miracle and both ECAN3 layouts).
- No acoustic number changes: diameters, chimneys, tubes, volumes and the voicing hash equal those of C4 (compare against the C4 reports in git); capped air within 0.5 %.
- No unexpected failure on any of the eight bodies.
- `python -m unittest discover -s kernel` passes (120 tests).

**C5.** Stage 2 is P0 at 65, 80, 95 and 125 cm³, P1, P2 and P3 at 80 cm³, and two copies of P0-80 (`P0-80-b`, `P0-80-c`). Stage 1 is the stubs of doc 04 (V-a, V-b, V-c, V-d, V-a±) built by the recipes in the notes; a stub has the voicing, the wall and no holes, and its own check that the capped volume equals the stub volume. V-b's forced rounded rectangle has only run as far as the solids, so test it through a full build. A stub measurement template (fields in open problem 4) may be added to `kernel/measurements.py` with tests. The reports name the subholes one way (`sub1`/`sub2` or `sub_L`/`sub_R`) and say which in the header. Each stage is one command for me, and that command includes the cavity-mode step. A stage builds every body even when one has an unexpected failure; it lists expected failures, unexpected failures and warnings in separate blocks of the report, and only an unexpected failure gives a non-zero exit code.

**C6.** Wrap `tools/geometry_check.py` in tests (the 20 cavities; at least P1-80 and P0-65 as bodies), and add plain-Python tests for `cavity_math.py`, `holes_layout.py`, `presets.py`, `kernel_bridge.py` and `ergonomics.py`. The ergonomics test reproduces the Miracle and ECAN3 rows of `measure_cad_output.md`. Test the extension install with a temporary Blender user folder (for example `BLENDER_USER_RESOURCES` pointing into the scratch area), so the owner's Blender profile stays untouched.
</checkpoint_notes>

<verification>
Spatial mistakes don't show up in unit tests or in a log that prints "done". The evidence for each checkpoint is measured on the mesh and seen in the renders:

- Run the geometry check on every body the checkpoint touches. It measures the STL read back from disk. Its output is the evidence.
- Open the renders yourself before you call a checkpoint done: at least the top view with hole names of P1-80, P2-80, P3-80 and P0-80, and one Stage 1 stub per window shape. Check that what you see agrees with the numbers. A subhole on the wrong side of a hand line is easier to see than to measure.
- At the end of C4b and of C5, start one fresh-context subagent on a cheaper model (Sonnet 5.5 is enough) with the acceptance list and the paths of the reports and renders, and ask it to check them against each other. A fresh reader catches what self-review misses. Keep delegation to these reviews: the build itself depends on context that a subagent would have to rebuild.
- Commit the reports and renders, so that the owner and the next session can review them.
</verification>

<environment_and_permissions>
- Windows 11. Blender 5.1.2 is at `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe` (not on PATH; Blender 4.1 is also installed and is not a target). Its Python is 3.13 with numpy and nothing else. System Python 3.12 has numpy, scipy, trimesh, matplotlib and Pillow. Its console is cp932: set `PYTHONIOENCODING=utf-8` when a script prints non-ASCII text.
- In the Bash tool, a heredoc that contains Python triple quotes fails. Write multi-line scripts to a file and run the file.
- With `--factory-startup`, Blender's default cube sits at the origin, which is the voicing port. The renderer already hides objects it did not create; keep it that way.

**Approved without asking:**
- Before anything else, if `git status` still shows it, commit the work already in the working tree as one commit, "Ergonomics challenge: doc 06, P2 layout slide, cavity-mode and CAD reference scripts". It is the owner-accepted P2 slide and its rebuilt reports and renders, the doc 05 banner, doc 06, `tools/cavity_modes_fd.py`, `tools/geometry_check_variant.py`, `measure_cad_references.py` and its outputs and images, this prompt, and the notes (item 14, the owner decisions, the rewritten "Notes for C4b"). Leave out `Analizes_ocarinas/ECAN3_experimental/` and `New Text Document.txt`.
- Commit to `addon-v1` as you go. Run Blender headless as often as needed. Write files inside the repository. Restructure the add-on code. Create or use a project `.venv` (it is in `.gitignore`) and install packages into it. Retry a failing build or check after fixing its cause, and retry a tool call that failed for a passing reason.
- Edit `params/alto_c_12hole.toml` for the `[ergonomics]` table and the new layout parameters, and the cavity presets for layout parameters.
- In the docs, record the decisions above where the docs state the question or the superseded rule: Q8, Q9 and Q12 in doc 02 (and the A12 row), D5 and the P3 sentence in doc 04, R9 and R16 in doc 03, the banner of doc 05. Change nothing else in `docs/`.
- Add the stub measurement template to the kernel, with tests.

**Ask first** (put the question in the notes and in your final report, and carry on with the rest): pushing to GitHub; merging into another branch; installing anything outside the project folder, including into Blender's bundled Python or the owner's Blender profile; any other change to the kernel's public behaviour; any other edit under `docs/` or `references/`; adding a licence file; deleting files you did not create.
</environment_and_permissions>

<checkpoints>
At the end of each checkpoint:
1. Run its checks: the geometry check and renders for C4b and C5, the kernel suite always, the new test suites for C6.
2. Commit to `addon-v1` with a message that starts with the checkpoint, for example `C4b: subholes along the hand-line normal, ergo checks, cavity mode from the first mode`.
3. Update `prompts/addon-v1-notes.md`: mark the checkpoint done with its evidence (test counts, check output, render folders, measured values), record decisions and open problems, and write the next concrete step. The notes file is the memory between sessions: it must describe the true state after every commit. When new work makes a note untrue (the lists of expected failing checks, the C4 numbers of P2 from before the slide, a caution whose reason is gone), correct or delete that note; don't stack a caveat on top of it. Evidence of finished checkpoints stays as the record.

A checkpoint is not a stop: record it and go straight on. If a checkpoint fails its done condition and you cannot fix it, record why, mark it blocked, and continue with work that does not depend on it.

When you resume, read the notes file and `git log` first, check that the last checkpoint marked done still passes, and continue from the first checkpoint that is not done. Don't redo finished work.
</checkpoints>

<working_approach>
You are the owner and long-term maintainer of the add-on code, and its design is up to you within the decisions above. The kernel is the source of every acoustic number: the add-on calls it and never re-derives acoustics, and kernel changes beyond the stub template are allowed only for real bugs, each with a test.

Where a doc and the kernel disagree, the docs record decisions and the kernel records the maths: flag the conflict in the notes, pick the reading that matches the decisions, and keep going. Never invent measured values; synthetic data stays labelled synthetic.

If you find a pre-existing bug or a behaviour the task does not mention, fix it only if the requested work cannot succeed without the fix; otherwise record it as an open problem. Scratch scripts and quick checks need not be kept. C6 asks for tests, so commit those; elsewhere, don't turn scratch checks into permanent test files.

Before you start, say in a line what you're about to do. Brief updates while you work help me follow along when I look in.
</working_approach>

# Finishing work

Please avoid stopping while you still owe work I asked for. Be persistent and do not stop unless needed. I am not watching in real time and cannot answer questions mid-task, so a question in the middle of the run blocks the work: put it in the notes and in the final report, state the assumption you made, and carry on with everything that does not depend on it. If you notice yourself inviting me to redirect you or offering to wait, instead proceed on the next part of the task. You may meet ordinary obstacles like errors, timeouts, locked files, empty results or failing tools. Diagnose them first, and when they are not real blockers, work through them with the access you have (wait and retry, fix the request, use another tool or source) rather than stopping unnecessarily. If someone clearly decided something is a hard blocker, such as the "Ask first" list above, leave it alone, say plainly what you found, and look for another safe way to finish the task. Before ending your turn, check your last paragraph: if it is a plan or a promise about work you have not done, do that work now. Stopping before the task is complete is very rarely merited. This does not override the "Ask first" list: those actions still wait for my go-ahead.

Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if a check fails, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.

# Communicating clearly

Write for an intelligent but low-context reader. The person reading has not seen your tool calls, your reasoning or the files you opened, and may be switching in from other work. Messages should generally be self-contained. Put the key points in the first few sentences. Use plain words and full sentences. Do not use a term or abbreviation that you made up during the work; say what the thing is. Write mostly in the style of ASD-STE100 Simplified Technical English: short sentences, one idea per sentence, active voice, the same word for the same thing. Use a paragraph of flowing prose where ideas connect, and keep bullets for lists of separate items.

Close with a short recap that stands on its own: which checkpoints are done and how each was verified; where sub_L and sub_R landed on P1-80, P2-80 and P3-80, and which `ergo_*` warnings each body shows, with the measured hand span and finger pitch beside the reference range; the computed first cavity mode of each Stage 2 body against F6; what failed, was blocked or is expected to fail; the questions waiting for me; and the exact commands that generate Stage 1 and Stage 2.
