# Prompt: kernel and fitter (checkpoints C0–C2), Sonnet session

This prompt covers the first part of the add-on build: the plan, the kernel extensions, the measurement fitter and the measurement format. It is plain, standard-library Python work, which suits Sonnet and keeps the session small enough for the plan allowance. The Blender add-on itself (C3–C6) is built afterwards with Opus, using `prompts/fable-5.2-addon-implementation.md` and its resume line.

## How to run it

- **Model:** Sonnet 5.5 as the main model, with Fable 5.2 as the advisor. Type `/advisor` to check it shows Fable; if not, type `/advisor fable`.
- **Effort:** `high`.
- **Start:** open a new session in the repository root, on the branch `main`, and paste everything below the line.
- **If it stops before C2 is done** (a usage limit or a crash): start a new session, paste the same text again, and add this line:

  > Resume: read `prompts/addon-v1-notes.md` on the branch `addon-v1` and continue from the first checkpoint that is not marked done, up to C2.

- **If it fails C1 or C2 twice:** switch to Opus for that checkpoint with the same resume line.
- **When C2 is done:** check the status table and the handoff section in the notes file, push `addon-v1` if you want a backup, then start an Opus session with the full prompt and its resume line. It picks up at C3.

---

<context>
I'm building a 3D-printed, parametrically tuned 12-hole alto C ocarina (A4 to F6). The repository is `Parametric_alto_C_Ocarina`, on GitHub at `aleckmadrid/Parametric_alto_C_Ocarina`, and the `main` branch holds the design work. The physics is a lumped Helmholtz model: pitch depends on chamber volume and on the conductance of each opening (window and holes), not on chamber shape. That is what lets the outside of the instrument be shaped freely, while the acoustic parts are generated and solved.

The next step is a physical test campaign with plain, generated test bodies. The test plan is written and agreed, and none of it has been printed yet. Its purpose is to find out how far the chamber volume can grow above the proven 60–80 cm³ band, and whether cavity shape changes the calculations. To run it, I need a working generator: a Blender add-on, backed by the existing Python kernel, that produces the printable test bodies and later fits the measurements I record. This session builds the kernel side of that tool. The add-on comes later.

Read these before you design anything. They are the source of truth, and the decisions in them are settled:

- `docs/02-unified-plan.md`: architecture, parameter classes (LOCKED / LINKED / CALIBRATE / TARGET), phases and gates, mesh precision rules
- `docs/03-parametric-findings.md`: equations, identities, the chimney-volume fixed point, sweeps, design rules R1–R14
- `docs/04-testing-phase.md`: the test plan this build must serve. It lists decisions D1–D8, the shapes, the generated sizes at each step, the three stages, the gates and the filament budget.
- `Analizes_ocarinas/Miracle_M/Miracle_M.md`: the reference instrument, its hole layout coordinates (section 4.2), its voicing, and the thicker-wall volume re-assessment (section 6.4)
- `references/heuer-video2-alto-c-tolerances.md`: Chris Heuer's alto C voicing sizes and tolerance band
- `params/alto_c_12hole.toml` and `kernel/` (`ocarina_kernel.py`, `alto_c_study.py`, `test_kernel.py`): the parameter set and the standard-library acoustic kernel, with 9 passing tests

The full build prompt, with all checkpoints C0–C6, is `prompts/fable-5.2-addon-implementation.md`. Read it for the whole picture, but your scope is the one set in this prompt.

The ECAN3 analysis lives on the branch `ecan3-experimental` under `Analizes_ocarinas/ECAN3_experimental/`. Read its `ECAN3_experimental.md` for the evidence behind k ≈ 1.0, inward tubes on small holes, and the split-subhole placement. Use it as reference only; don't merge that branch.
</context>

<goal>
Build the standard-library kernel extensions, the measurement fitter and the measurement input format: checkpoints C0, C1 and C2 of the full build. A later session, run on a different model, builds the Blender add-on (C3–C6) on top of your work. So done means two things. First, C0–C2 pass their done conditions. Second, your code and notes are a clean base for that session: it should be able to call your kernel without reading your conversation.

**Scope limit:** stop after C2. Don't write Blender code, Geometry Nodes, `bpy` imports, a `blender_manifest.toml` or anything else from C3 onward, even if you finish early. If you have time left, spend it on test coverage, edge cases and the handoff notes for C3.
</goal>

<design_decisions>
These are decided. Build to them, and don't reopen them:

- **Kernel stays standard-library Python with no Blender imports.** It is unit-tested and runs from the command line. The add-on will call it.
- **End correction is split.** `k_window` = 0.80 is fixed: it is the convention η_w is defined under, and η_w and k cannot be separated for the window. `k_hole` has a prior of 1.0 and is fitted from measurements. Update `params/alto_c_12hole.toml` and the kernel accordingly, and keep the existing tests passing.
- **Voicing is generated by rule, never free-form.** Inputs: target V0, voice rating (soft 8.89 / medium 9.65 / loud 10.41 mm window length; default medium), wall at window (default 4.0 mm), and coupon-only offsets (labium offset ±0.2 mm). Derived: the window area is solved so that η_w·G_w reaches A4 at the target V0 (η_w = 0.90 prior); the window is a teardrop with its broad end at the windway and narrow end at the labium, and switches to a rounded rectangle when the teardrop would need to be wider than long (the existing `teardrop_area` requires width < length); windway exit height 1.20 mm, with W/h checked to stay within 7–10; windway width equal to the window's broad end; windway length 30 mm, inlet/exit taper 1.3; labium ramp 20°, edge 0.4 mm; keep-outs 10 mm inside and a 45° flare outside. In the kernel, the voicing is a set of numbers, not geometry. Each voicing gets a version hash of its inputs, and calibration constants are stored per hash.
- **Holes are round, and each has its own diameter**, solved per note with the chimney-volume fixed point. Holes under 3 mm get round inward tubes (ECAN3 style), whose length counts as chimney. Hole placement on the body is C4 work; the kernel only sizes the holes and reports chimney and tube lengths.
- **First-print holes are printed at their `k_hole` = 0.8 diameters** (so notes err flat, which reaming can fix). Sizing output must give both the k 0.8 print diameter and the k 1.0 nominal.
- **Checks.** Add the cavity-mode check (first internal resonance c/2L against F6) and the range-ratio check already planned in doc 02, as kernel functions with clear pass/fail results.
</design_decisions>

<deliverables>
1. **C0: plan and notes.** Create the branch `addon-v1` from `main`. Write `prompts/addon-v1-notes.md`: the kernel modules and data flow, your build order for C1–C2, and a status table for C0–C6 (C3–C6 marked "not started, later session").
2. **C1: kernel extensions.** The `k_window` / `k_hole` split; window sizing for teardrop and rounded rectangle; voicing rules and version hash; hole sizing with inward tubes; cavity-mode and range-ratio checks. Add a command-line entry that prints the sizing for any V0 and voice rating, so the doc 04 table can be regenerated.
3. **C2: measurement fitter and input format.** Given one body's measured V0, measured hole diameters, room temperature and the 13 recorded pitches, the fitter returns η_w·G_w, each hole's effective conductance, the global `k_hole`, per-hole position factors and the corrected diameters. It also fits across several bodies at once. The measurement format (CSV or TOML) is filled in by hand: for each body, water-fill mass, measured hole diameters, room temperature, and pitch and pressure per fingering, 3 takes each. Include a blank template, one synthetic example labelled synthetic, and a synthetic fitted-constants file in the format the Stage 3 generator will read later.
4. **Handoff section** at the end of the notes file, for the C3 session: the public kernel API the add-on should call (function names, inputs, outputs, units), where the parameters live, the command that regenerates the sizing table, known limits and open questions.
</deliverables>

<acceptance_criteria>
- Generated sizes match the table in `docs/04-testing-phase.md` (window shape and size, windway, the listed hole diameters at k 1.0) within 0.05 mm, or you explain any difference and which side is right.
- The voicing hash is stable for the same inputs and changes when any voicing input changes.
- The fitter recovers synthetic η_w·G_w, `k_hole` and position factors within 1 % on noise-free data. Also run it with ±5-cent noise on the pitches and report how the error grows.
- `python -m unittest discover -s kernel -v` passes, old tests and new. Report the actual output.
</acceptance_criteria>

<environment_and_permissions>
- Windows 11. System Python is 3.12 with no packages installed. Blender is not needed for this work.
- **Approved without asking:** create the branch `addon-v1` from `main` and commit to it as you go; create a project virtual environment (`.venv`, add it to `.gitignore`) and install test or analysis packages into it (for example `pytest`, `numpy`), as long as the kernel itself stays standard library; write files inside the repository; restructure the kernel internals as the design needs, as long as its public behaviour and tests stay correct.
- **Ask first:** pushing to GitHub, merging into `main`, installing anything outside the project folder, editing the files under `docs/` or `references/` beyond adding cross-links, and deleting files you did not create.
</environment_and_permissions>

<checkpoints>
At the end of each checkpoint (C0, C1, C2):
1. Run the checks for that checkpoint and the full kernel test suite.
2. Commit to `addon-v1` with a message that starts with the checkpoint, for example `C1: k split, voicing rules and hole sizing`.
3. Update the notes file: mark the checkpoint done with the evidence (test counts, measured values), list decisions and open problems, and write the next concrete step.
4. If an advisor is available in this session, consult it before you mark the checkpoint done.

A checkpoint is not a stop: finish it, record it, and go on to the next one, up to the end of C2. If a checkpoint fails its done condition and you cannot fix it, record why in the notes and mark it blocked.

When you resume, read the notes file and `git log` on `addon-v1` first, check that the last checkpoint marked done still passes its tests, then continue from the first checkpoint that is not done. Don't redo finished work.
</checkpoints>

<working_approach>
You own the kernel extensions and the fitter, and their design is up to you within the decisions above. Keep `prompts/addon-v1-notes.md` as your working notes as you go: decisions you made and why, problems found, and what remains.

Establish a way to check your own work early, and run it as you build: compare generated sizes against the doc 04 table, and run the test suite after each change. Where the kernel's equations and a doc disagree, the docs record decisions and the kernel records the maths; flag the conflict in your notes, pick the reading that matches the decisions, and keep going.

Physical testing has not happened yet. Every constant is pre-calibration. Never invent measured values; synthetic data must be labelled as synthetic everywhere it appears.

Before you start, say in a line what you're about to do. Brief updates while you work help me follow along.
</working_approach>

# Finishing work

Please avoid stopping while you still owe work I asked for. Be persistent and do not stop unless needed. While status notes are welcome, as is clarifying with me on open decisions, carry on with work that does not depend on my answer without unnecessary stops. If you notice yourself inviting me to redirect you or offering to wait, instead proceed on the next part of the task. You may meet ordinary obstacles like errors, timeouts, locked files, empty results or failing tools. Diagnose them first, and when they are not real blockers, work through them with the access you have (wait and retry, fix the request, use another tool or source) rather than stopping unnecessarily. If someone clearly decided something is a hard blocker, such as a file marked not to be touched, access that was intentionally withheld, or a safety guardrail, leave it alone, say plainly what you found, and look for another safe way to finish the task. Stopping before the task is complete is very rarely merited - as in when the task can't move forward without user input, or where the blocker is deliberate and should not be worked past. This does not override the need for confirmation on the actions listed under "Ask first".

Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.

# Communicating clearly

Write for an intelligent but low-context reader. The person reading has not seen your tool calls, your reasoning or the files you opened, and may be switching in from other work. Messages should generally be self-contained: the reader should understand what you mean without having to dig for other context. Put the key points in the first few sentences. Practice progressive disclosure in your sentence order, and do not use undefined references and ideas in line 1 that won't make sense until the reader reaches line 12. Use plain words, and write in clear, understandable full sentences. Do not use a term or abbreviation that you made up during the work - say what the thing is in a way any reader would understand. Write mostly in the style of ASD-STE100 Simplified Technical English: short sentences, one idea per sentence, active voice, and consistently using the same word for the same thing. Use a paragraph of flowing prose where ideas connect, and keep bullets for lists of separate items. Leave out unnecessary details unless the reader asks and practice concision, but do ensure that your messages have the key context. Aim to make your user-facing text as human-readable and clear as possible.

Close with a short recap that stands on its own: which checkpoints are done and how each was verified, which acceptance criteria pass or fail, what is left for the C3 session, and the exact command that regenerates the sizing table.
