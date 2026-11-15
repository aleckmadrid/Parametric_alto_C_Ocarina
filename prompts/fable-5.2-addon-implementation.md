# Prompt: implement the parametric ocarina Blender add-on

## How to run it

- **Model:** Opus 5.5 as the main model, with Fable 5.2 as the advisor. The advisor is already set in your user settings (`"advisorModel": "fable"`); check with `/advisor` before you start, or set it with `/advisor fable`. This setup spends Fable only on advice: before an approach is chosen, when the work is stuck, and before a checkpoint is called done. Fable as main model also works, but it costs twice as much per token and can only use Fable as advisor.
- **Effort:** `high`. This is a long unattended build, and turns will run for many minutes.
- **Usage credits:** turn them on with a monthly cap before you start, so a long run does not stall at a usage limit.
- **First session:** paste everything below the line into a new session started in the repository root.
- **Later sessions** (after a usage limit, a crash or a fresh start): paste the same text again, followed by this one line:

  > Resume: read `prompts/addon-v1-notes.md` on the branch `addon-v1` and continue from the first checkpoint that is not marked done.

  A fresh session is cheaper than continuing a very long one, because it does not re-read the old conversation. Start one after each two or three checkpoints if the session context has grown large.

---

<context>
I'm building a 3D-printed, parametrically tuned 12-hole alto C ocarina (A4 to F6). The repository is `Parametric_alto_C_Ocarina`, on GitHub at `aleckmadrid/Parametric_alto_C_Ocarina`, and the `main` branch holds the design work. The physics is a lumped Helmholtz model: pitch depends on chamber volume and on the conductance of each opening (window and holes), not on chamber shape. That is what lets the outside of the instrument be shaped freely, while the acoustic parts are generated and solved.

The next step is a physical test campaign with plain, generated test bodies. The test plan is written and agreed, and none of it has been printed yet. Its purpose is to find out how far the chamber volume can grow above the proven 60–80 cm³ band, and whether cavity shape changes the calculations. To run it, I need a working generator: a Blender add-on, backed by the existing Python kernel, that produces the printable test bodies and later fits the measurements I record. The same tool will later carry sculpted exteriors, so build it as the real add-on, not a throwaway script.

Read these before you design anything. They are the source of truth, and the decisions in them are settled:

- `docs/02-unified-plan.md`: architecture, parameter classes (LOCKED / LINKED / CALIBRATE / TARGET), phases and gates, mesh precision rules
- `docs/03-parametric-findings.md`: equations, identities, the chimney-volume fixed point, sweeps, design rules R1–R14
- `docs/04-testing-phase.md`: the test plan this build must serve. It lists decisions D1–D8, the shapes, the generated sizes at each step, the three stages, the gates and the filament budget.
- `Analizes_ocarinas/Miracle_M/Miracle_M.md`: the reference instrument, its hole layout coordinates (section 4.2), its voicing, and the thicker-wall volume re-assessment (section 6.4)
- `references/heuer-video2-alto-c-tolerances.md`: Chris Heuer's alto C voicing sizes and tolerance band
- `params/alto_c_12hole.toml` and `kernel/` (`ocarina_kernel.py`, `alto_c_study.py`, `test_kernel.py`): the parameter set and the standard-library acoustic kernel, with 9 passing tests

The ECAN3 analysis lives on the branch `ecan3-experimental` under `Analizes_ocarinas/ECAN3_experimental/`. Read its `ECAN3_experimental.md` for the evidence behind k ≈ 1.0, inward tubes on small holes, and the split-subhole placement. Use it as reference only; don't merge that branch.
</context>

<goal>
Build the add-on and the kernel extensions it needs, working through the checkpoints below, so that I can generate, inspect and export every print in Stage 1 and Stage 2 of `docs/04-testing-phase.md`. I also need to load my recorded measurements and get the fitted constants and corrected hole sizes for Stage 3. Done means I can run one documented command per stage and get the STL files, plus a sizing report I can check against the doc.
</goal>

<design_decisions>
These are decided. Build to them, and don't reopen them:

- **Kernel stays standard-library Python with no Blender imports.** It is unit-tested and runs from the command line. The add-on calls it.
- **Procedural cavity from Geometry Nodes.** One shared node group: a lofted spine with cross-sections, where width and height are given at 7 stations along the body and interpolated with a smooth spline, plus a superellipse section exponent, end caps and a voicing-port anchor. Shape inputs are ratios; size is solved. The cavity is scaled exactly to a target volume (mesh volume from face area × normal · position, then a cube-root scale) about the voicing port, so the voicing never moves. Presets: P0 control egg (2.2 : 1.5 : 1), P1 teardrop and P2 tailed gourd (loose proportions from the two reference volumes described in `docs/04`; build smooth, simple parametric versions, not copies of the meshes), and P3 traditional transverse (3 : 1.6 : 1 with a gently bent spine, provisional). Store station values as numbers that can be written from TOML, not in a curve widget.
- **Voicing is generated by rule, never free-form.** Inputs: target V0, voice rating (soft 8.89 / medium 9.65 / loud 10.41 mm window length; default medium), wall at window (default 4.0 mm), and coupon-only offsets (labium offset ±0.2 mm). Derived: window area solved through the kernel so that η_w·G_w reaches A4 at the target V0 (η_w = 0.90 prior; `k_window` = 0.80 fixed); a teardrop with its broad end at the windway and narrow end at the labium, switching to a rounded rectangle when the teardrop would need to be wider than long; windway exit height 1.20 mm, with W/h checked to stay within 7–10; windway width equal to the window's broad end; windway length 30 mm, inlet/exit taper 1.3; labium ramp 20°, edge 0.4 mm; keep-outs 10 mm inside and a 45° flare outside. Each generated voicing gets a version hash of its inputs. Calibration constants are stored per hash.
- **End correction is split.** `k_window` = 0.80 (the convention η_w is defined under). `k_hole` has a prior of 1.0 and is fitted from measurements. Update the TOML and kernel accordingly, and keep the existing tests passing.
- **Holes are round, and each has its own diameter**, solved per note with the chimney-volume fixed point. Holes under 3 mm get round inward tubes (ECAN3 style, counted as chimney). Layout: Miracle finger spacing (section 4.2 of the Miracle write-up) with one subhole per hand, ECAN3 style: sub_L between L_ring and L_middle, sub_R between R_index and R_middle, both off the finger line. Hole centres come from the hand template, and diameters from the kernel. A centre may move up to 2 mm along its row to keep edge gaps (about 3.4 mm minimum next to subholes). The template is wrapped onto the deck using the cavity's surface coordinates converted to arc length, and each hole axis follows the cavity normal. P0 is too short for the Miracle span, so it gets a compressed test layout; P1–P3 use the real template.
- **Wall stack.** The cavity is offset outward to form the skin. Finger-deck, thumb and voicing patches have a fixed thickness (deck 4.0 mm). An optional user outer mesh is merged inside a sculpt envelope (default 15 mm max). Test bodies have no outer mesh and a uniform 4 mm wall.
- **Booleans use Blender 5.1's Manifold solver, with Exact as fallback.** After every Boolean, assert that the result is manifold and that the cavity volume changed by the expected amount. Never remesh or smooth the voicing or the chimneys.
- **First-print holes are printed at their `k_hole` = 0.8 diameters** (so notes err flat, which reaming can fix), and the report also shows the k 1.0 nominal.
- **No sidebar panel or UI layout yet.** I'll design the panel after this works. Expose everything as Blender operators with properties, a Python API, and a headless command-line entry (`blender -b --python ...`). A bare-minimum menu entry to run the operators is fine.
</design_decisions>

<deliverables>
1. **Kernel extensions** (standard library, tested): `k_window` / `k_hole` split; window sizing for teardrop and rounded rectangle; voicing rules and version hash; hole sizing with inward tubes; the cavity-mode and range-ratio checks already planned in doc 02; and a **measurement fitter**. Given the measured V0, measured hole diameters and the 13 recorded pitches of one body, it returns η_w·G_w, each hole's effective conductance, the global `k_hole`, per-hole position factors and the corrected diameters. It also fits across several bodies. The fitter must recover synthetic constants within 1 % on generated data.
2. **The add-on** as a Blender 5.1 extension (`blender_manifest.toml`), in its own folder in the repo. It contains: the cavity Geometry Nodes group built from Python, so it is reproducible and versioned; the voicing generator; the hole solver and placer; the wall stack; the Booleans; the pre-export checks from doc 02 (volume within 0.5 %, voicing hash intact, hole floor and pad limits, spacing, wall thickness, range ratio, cavity length ratio); and STL export, plus the air domain for later FEM.
3. **Test-body generation per stage.** One command per stage writes the STL files and a Markdown sizing report: per body, the volume, window, windway, every hole diameter at k 0.8 and k 1.0, chimney and tube lengths, check results and the voicing hash. Stage 1: voicing stubs V-a to V-d, plus the optional V-a± pair. Stage 2: P0 at 65 / 80 / 95 / 125 cm³, P1–P3 at 80 cm³, and the P0-80 repeat copies. Stage 3: corrected bodies from a fitted-constants file, plus P0 at 110 cm³ predicted from the model only.
4. **A measurement input format** (CSV or TOML) I can fill in by hand, for each body: water-fill mass, measured hole diameters, room temperature, and pitch and pressure per fingering, 3 takes each. Include a template file and one synthetic example.
5. **Tests**: kernel unit tests (`python -m unittest discover -s kernel -v` stays green), and headless Blender tests run with Blender 5.1 in background mode.
6. **A short README section** on how to install the extension, run each stage, and run the tests.
</deliverables>

<acceptance_criteria>
- Generated sizes match the table in `docs/04-testing-phase.md` (window shape and size, windway, the listed hole diameters at k 1.0) within 0.05 mm, or you explain any difference and which side is right.
- Every exported body is manifold, and its cavity volume is within 0.5 % of target.
- Doc 02's Phase 4 gate: from the same inputs, the add-on reproduces the kernel's hole sizes within 0.05 mm.
- The voicing hash is stable for the same inputs and changes when any voicing input changes.
- The fitter recovers synthetic η_w·G_w, `k_hole` and position factors within 1 %, including with ±5-cent noise on the pitches (report how the error grows).
- All kernel tests and headless Blender tests pass. Report the actual output.
</acceptance_criteria>

<environment_and_permissions>
- Windows 11. Blender 5.1 is installed at `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe` (not on PATH; Blender 4.1 is also installed and is not a target). Blender 5.1 bundles Python 3.13 and numpy. System Python is 3.12 with no packages installed.
- **Approved without asking:** create a branch from `main` named `addon-v1` and commit to it as you go; create a project virtual environment (`.venv`, add it to `.gitignore`) and install Python packages into it (for example `pytest`, `numpy`, `trimesh`, `manifold3d`, `gmsh`, `scikit-fem`, `meshio`, `fake-bpy-module`); run Blender headless; write files inside the repository; restructure code you write, and the kernel internals, as the design needs, as long as the kernel's public behaviour and tests stay correct.
- **Ask first:** pushing to GitHub, merging into `main`, installing anything outside the project folder (system software or Blender's bundled Python), editing the files under `docs/` or `references/` beyond adding cross-links, and deleting files you did not create.
- Package installs into Blender's own Python would need admin rights. Avoid them: keep the add-on on Blender's bundled numpy, or vendor what it needs.
</environment_and_permissions>

<checkpoints>
Build in these checkpoints, in order. They exist so that the work survives a usage limit or a new session: at every checkpoint the branch and the notes file must be enough for a fresh session to pick up without this conversation. A checkpoint is not a stop. Finish it, record it, and go straight on to the next one.

- **C0 Plan.** Read the files in `<context>`. Create the branch `addon-v1`. Write `prompts/addon-v1-notes.md` with the modules, the data flow, your build order inside the checkpoints below, and a status table of C0–C6.
- **C1 Kernel.** The kernel extensions from deliverable 1, except the fitter: the `k_window` / `k_hole` split, window sizing, voicing rules and hash, hole sizing with inward tubes, cavity-mode and range-ratio checks. Done when the sizes match the doc 04 table and all kernel tests pass.
- **C2 Fitter and measurement format.** The measurement fitter, the measurement input format, the template and the labelled synthetic example (deliverables 1 and 4). Done when the synthetic recovery criteria pass, with the noise result recorded.
- **C3 Cavity.** The add-on skeleton (`blender_manifest.toml`, headless entry), the cavity Geometry Nodes group built from Python, the presets P0–P3 and the exact volume scaling about the voicing port. Done when headless Blender produces every preset at every Stage 2 volume within 0.5 % and the voicing port does not move.
- **C4 Voicing, holes and wall stack.** The voicing geometry, the hole placement on the deck, the inward tubes, the wall stack, the Booleans and the pre-export checks. Done when a full P1 body at 80 cm³ exports manifold, passes every check, and its hole sizes match the kernel within 0.05 mm (the Phase 4 gate).
- **C5 Stage commands.** One command per stage with STL files and the Markdown sizing report (deliverable 3). Done when Stage 1 and Stage 2 generate end to end and the reports agree with doc 04, and Stage 3 runs from the synthetic fitted-constants file.
- **C6 Finish.** The headless Blender test suite, the README section, and a final pass over every acceptance criterion with the actual test output.

At the end of each checkpoint:
1. Run the checks for that checkpoint and the full kernel test suite.
2. Commit to `addon-v1` with a message that starts with the checkpoint, for example `C3: cavity Geometry Nodes group and volume scaling`.
3. Update the notes file: mark the checkpoint done with the evidence (test counts, measured values), list decisions and open problems, and write the next concrete step.
4. If an advisor is available in this session, consult it before you mark the checkpoint done.

If a checkpoint fails its done condition and you cannot fix it, record why in the notes, mark it blocked, and continue with the next checkpoint that does not depend on it.

When you resume, read the notes file and `git log` on `addon-v1` first, check that the last checkpoint marked done still passes its tests, then continue from the first checkpoint that is not done. Don't redo finished work.
</checkpoints>

<working_approach>
You are the owner and long-term maintainer of the add-on code and the kernel extensions, and their design is up to you within the decisions above. Keep `prompts/addon-v1-notes.md` as your working notes as you go: decisions you made and why, problems found, and what remains.

Establish a way to check your own work early, and run it as you build: compare generated sizes against the doc 04 table, check manifold and volume on every export, and run the test suites. Where the kernel's equations and a doc disagree, the docs record decisions and the kernel records the maths; flag the conflict in your notes, pick the reading that matches the decisions, and keep going.

Physical testing has not happened yet. Every constant is pre-calibration. Never invent measured values; synthetic data must be labelled as synthetic everywhere it appears.

Before you start, say in a line what you're about to do. Brief updates while you work help me follow along.
</working_approach>

# Finishing work

Please avoid stopping while you still owe work I asked for. Be persistent and do not stop unless needed. While status notes are welcome, as is clarifying with me on open decisions, carry on with work that does not depend on my answer without unnecessary stops. If you notice yourself inviting me to redirect you or offering to wait, instead proceed on the next part of the task. You may meet ordinary obstacles like errors, timeouts, locked files, empty results or failing tools. Diagnose them first, and when they are not real blockers, work through them with the access you have (wait and retry, fix the request, use another tool or source) rather than stopping unnecessarily. If someone clearly decided something is a hard blocker, such as a file marked not to be touched, access that was intentionally withheld, or a safety guardrail, leave it alone, say plainly what you found, and look for another safe way to finish the task. Stopping before the task is complete is very rarely merited - as in when the task can't move forward without user input, or where the blocker is deliberate and should not be worked past. This does not override the need for confirmation on the actions listed under "Ask first".

Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.

# Communicating clearly

Write for an intelligent but low-context reader. The person reading has not seen your tool calls, your reasoning or the files you opened, and may be switching in from other work. Messages should generally be self-contained: the reader should understand what you mean without having to dig for other context. Put the key points in the first few sentences. Practice progressive disclosure in your sentence order, and do not use undefined references and ideas in line 1 that won't make sense until the reader reaches line 12. Use plain words, and write in clear, understandable full sentences. Do not use a term or abbreviation that you made up during the work - say what the thing is in a way any reader would understand. Write mostly in the style of ASD-STE100 Simplified Technical English: short sentences, one idea per sentence, active voice, and consistently using the same word for the same thing. Use a paragraph of flowing prose where ideas connect, and keep bullets for lists of separate items. Leave out unnecessary details unless the reader asks and practice concision, but do ensure that your messages have the key context. Aim to make your user-facing text as human-readable and clear as possible.

Close with a short recap that stands on its own: which checkpoints are done and how each was verified, which acceptance criteria pass or fail, what is left, and the exact commands to generate the Stage 1 and Stage 2 prints.
