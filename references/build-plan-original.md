# Ocarina acoustic core: architecture, math and build plan

Nov 15, 2026 · @Alex

## Bottom line

Build a small standalone Python acoustic kernel and put a thin Blender add-on in front of it. Treat the windway and labium as one frozen, pre-validated "voicing module" that is never sculpted. Use engineering CAD only to author that module once.

Three facts about ocarina physics make this the right split:

- **Pitch depends on chamber volume, not chamber shape.** An ocarina is a Helmholtz resonator, so the chamber can be any sculpted mesh as long as its measured volume hits a target. This is what makes your core + shell idea physically sound.
- **Pitch depends on the sum of open-hole conductances, not hole positions.** Holes can go wherever the sculpture and the fingers want them. Only diameter and chimney height matter to first order.
- **Chimney height is set by the shell, not the core.** The air column in each tone hole runs through the core wall and the shell. Any tool that does not know the local shell thickness cannot size the holes. This is why hole sizing has to run in the same environment as the shell.

A realistic accuracy target is within 10 to 15 cents on the second print, not zero tuning on the first. The lumped model has two or three constants that depend on your printer, material and voicing geometry. One cheap calibration print measures them. After that, new designs that reuse the same voicing module should land without hole filing.

Pitch also moves with breath pressure, typically by tens of cents across a comfortable blowing range. "In tune" therefore means in tune along a chosen breath curve, which you record on the calibration print.

The formulas here are standard resonator acoustics, written from memory rather than looked up. The numeric dimension ranges for voicing are typical maker practice and are labelled as starting values to replace with your own measurements.

## Architecture comparison

The Blender add-on wins on workflow and ties on the precision that matters, provided the acoustic math lives outside Blender in a testable library.

| Criterion | Parametric CAD | Blender add-on |
| --- | --- | --- |
| Chamber volume | Exact B-rep volume. Feeding measured volume back into hole sizes needs scripting (Fusion API, Onshape FeatureScript). OpenSCAD cannot query volume at all. | Exact for a closed manifold mesh via `bmesh` volume. Recomputed on every deformation. |
| Labium and windway control | Best. Exact fillets, chamfers, drafts and dimensions. | Good enough. The windway and labium ramp are planar faces, which a mesh represents exactly. A teardrop window outline and small fillets are faceted below printer resolution. |
| Chimney height awareness | Only if the shell is also modelled in CAD. | Direct. Ray-cast from each hole through the shell and measure. |
| Sculptural friction | High. Organic exteriors are painful in CAD, and importing sculpted meshes into B-rep is worse. | Low. Core, shell, solve and Boolean are in one scene. |
| Development effort | Lowest for one instrument. Poor reuse across sculpted designs. | Medium. Mostly Python glue around the kernel. |
| Main risk | Fights you on every non-primitive shape. | Mesh Boolean failures and Blender API changes between versions. |
| Best use here | Authoring the voicing module once, to exact dimensions. | Everything else: chamber, holes, shell, checks, export. |

### Recommended hybrid

1. **Acoustic kernel:** a pure Python package with no Blender imports. It holds the equations, the fingering-table solver and the calibration constants. It is unit-tested and runs from the command line, a notebook or the add-on.
2. **Voicing module:** one windway + window + labium solid, authored once in CAD or as exact mesh coordinates, validated by test print, then stored as a library asset. Keep a few scaled variants for different pitch ranges rather than a freely parametric one.
3. **Blender add-on:** places the voicing module, measures chamber volume, calls the kernel, builds chimney cutters at solved diameters, measures shell thickness at each hole, re-solves, and runs the Booleans.

Keep Geometry Nodes for live preview geometry only, such as hole cutters that follow empties on the surface. Do the solve in Python, because it is iterative and needs the calibration data.

### Mesh precision rules for the add-on

- Compensate polygon area. A 32-sided hole has 0.64% less area than its circle. Scale the cutter radius so polygon area equals target area, or use 64 segments.
- Run Booleans with the exact solver on clean manifold inputs, and assert that the result is manifold and that cavity volume changed by the expected amount.
- Never smooth, remesh or decimate the voicing module or the chimneys after the Boolean. Mask them out of any sculpt operation.

## Acoustic math

Every note is one Helmholtz resonance whose frequency squared is proportional to total open conductance divided by cavity volume. Sizing an ocarina is therefore linear algebra in conductances, followed by one quadratic per hole.

### Governing equation

```latex
f = \frac{c}{2\pi}\sqrt{\frac{G_{tot}}{V}}, \qquad G_{tot} = \eta_w G_w + \sum_{i \in \text{open}} G_i
```

- `c` is the speed of sound in the air inside the played instrument. Use c = 331.3 × sqrt(1 + T/273.15) m/s with T around 27 to 30 °C, because breath warms the air.
- `V` is the cavity volume for that fingering (see below).
- `G` is the acoustic conductance (Rayleigh conductivity) of an opening, with units of length.
- `η_w` is a calibration factor on the voicing window. The labium, the windway exit and the jet partly shroud the window, so its effective conductance is below the plain-aperture value. Expect roughly 0.6 to 0.9 and measure it.

### Conductance of a hole with chimney

```latex
G_i = \frac{A_i}{t_i + k\, d_{eq,i}}, \qquad d_{eq} = 2\sqrt{A/\pi}
```

- `A` is the cross-section area and `t` the chimney height: core wall plus shell along the hole axis.
- `k·d` is the combined inner and outer end correction. Theory bounds it between 0.785 d (hole in a thin plate, π/4 per diameter) and about 0.85 d (two flanged pipe ends). Start at 0.80 and fit it.
- For the rectangular window use its area, its wall thickness at the window and the equivalent diameter.

Inverting for a round hole gives the diameter directly:

```latex
d = \frac{2}{\pi}\left(Gk + \sqrt{G^2k^2 + \pi G t}\right)
```

### Volume bookkeeping

A closed hole's chimney is part of the cavity. An open hole's chimney is part of the neck. So:

```latex
V_j = V_0 - \sum_{i \in \text{open}_j} A_i t_i
```

`V_0` is the full air volume with every hole capped at its outer end, including the window throat up to the labium plane. Twelve chimneys of 0.2 cm³ in a 150 cm³ chamber shift pitch by about 14 cents if ignored.

### Sizing procedure

1. **Fix the voicing module.** Its window gives `G_w`, and calibration gives `η_w`.
2. **Solve the chamber volume from the lowest note** (all holes closed):

```latex
V_0 = \frac{\eta_w G_w\, c^2}{4\pi^2 f_0^2}
```

3. **Solve hole conductances.** For a linear fingering where hole k raises the pitch from note k−1 to note k:

```latex
G_k = \frac{4\pi^2 V}{c^2}\left(f_k^2 - f_{k-1}^2\right)
```

4. **Convert each `G_k` to a diameter** with the quadratic above, using the measured chimney height at that hole.
5. **Iterate.** Diameters change chimney volumes, and shell thickness changes `t`. Two or three passes converge.

For a full fingering chart with cross-fingerings, each fingering j gives one linear equation in the unknown conductances. Solve all of them together as a non-negative least-squares problem weighted in cents. This is how you tune accidentals without extra holes.

Volume is the design target, not a result. The sculpting constraint is "this chamber must enclose V\_0", and the add-on should show the live error in cents.

### Range limit

```latex
\left(\frac{f_{max}}{f_0}\right)^2 = 1 + \frac{\sum G_i}{\eta_w G_w}
```

An octave plus a minor sixth, the usual 12-hole range, needs total hole conductance about 9 times the window conductance. Past that, the top notes turn airy and unstable because one fixed window cannot voice the whole range. Treat a ratio of 9 to 10 as the single-chamber ceiling.

### Voicing ratios

These are starting values for an alto-sized instrument. Replace them with numbers from your reverse-engineered references.

| Parameter | Starting value | Linked to |
| --- | --- | --- |
| Windway exit height h | 1.0 to 1.5 mm | Printer resolution, breath resistance |
| Windway width | Equal to window width | Window |
| Window length W (windway exit to labium edge) | 7 to 10 × h at alto size (see the alto C section) | Jet transit time |
| Windway length | 20 to 40 mm, converging toward the exit | Jet stability |
| Labium ramp angle | 15° to 25° | Tone colour, printability |
| Labium edge thickness | 0.3 to 0.5 mm blunt | Printer minimum feature |
| Edge offset from windway centreline | Within the jet thickness; sweep it | Low versus high note balance |
| Window conductance G\_w | 4π² V\_0 f\_0² / (η\_w c²) | Chamber volume and lowest note |

Jet timing gives one diagnostic. With jet speed U = sqrt(2p/ρ) at blowing pressure p, the Strouhal number is St = f × W / U. For the alto C window lengths below, St comes out near 0.2 to 0.3 on the low note at 150 to 300 Pa and 0.3 to 0.4 on the top note at 600 to 1000 Pa. Those pressures are assumptions. Measure St on your printed references and keep a new design inside the range they show, rather than treating any band as fixed.

### Sensitivities

```latex
\Delta\text{cents} \approx 866\left(\frac{\Delta G_{tot}}{G_{tot}} - \frac{\Delta V}{V}\right)
```

| Error source | Effect |
| --- | --- |
| +1% cavity volume | −8.6 cents on every note |
| +1 °C internal air temperature (theory; about 0.9 cents measured per °C of room temperature) | +2.9 cents on every note |
| Top hole printed 0.1 mm undersize (8.4 mm nominal) | −2.9 cents on the top note |
| Breath pressure | Tens of cents; set by the player and the voicing |

Volume and window errors dominate, since they shift the whole scale. Individual hole errors are small. That is why calibration targets `η_w`, volume shrinkage and `k`, in that order.

### Where the lumped model stops

The model assumes the cavity is small compared with the wavelength. At E6 the half wavelength is 132 mm. Keep the longest internal dimension under about a third of the top note's wavelength. Beyond that, hole position starts to matter and you need the FEM check in the validation section.

Also keep a flat land of about 1.5 hole diameters around each hole exit, and at least one diameter between hole edges. Deep countersinks, ridges and close neighbours all change the outer end correction.

## Alto C targets and high-note safeguards

Start the alto C voicing module with an 8.9 mm window length and a 1.14 mm windway exit, the quiet end of Chris Heuer's playable band. A window that is too large for the chamber is the most common documented cause of airy or missing high notes, so size it small first and enlarge only if the low note is too weak.

### Heuer's voicing chart, converted

Values are from the chart in [Chris Heuer's](https://www.youtube.com/@ocarinaone) tolerances video for teardrop voicings. "Window" is the distance from the windway exit to the labium edge. Use the fired column for printing, since a print does not shrink like clay. I read "airway exit" as the exit height (his reference is one credit card, 0.03 in); confirm that against his voicing video.

| Size | Windway exit (in) | Windway exit (mm) | Window, fired (in) | Window, fired (mm) | Window ÷ exit |
| --- | --- | --- | --- | --- | --- |
| #1 C (smallest) | 0.03 | 0.76 | 0.20 | 5.1 | 6.7 |
| #2 G/F | 0.045 | 1.14 | 0.30 | 7.6 | 6.7 |
| #3 C (alto) | 0.045 | 1.14 | 0.38 | 9.7 | 8.4 |
| #4 G/F | 0.045 | 1.14 | 0.45 | 11.4 | 10.0 |
| #5 C | 0.06 | 1.52 | 0.60 | 15.2 | 10.0 |
| #6 G/F | 0.06 | 1.52 | 0.80 | 20.3 | 13.3 |
| #7 C (bass) | 0.06 | 1.52 | 1.00 | 25.4 | 16.7 |

His tolerance band for the alto #3 C:

| Window (in) | Window (mm) | Result |
| --- | --- | --- |
| 0.32 | 8.1 | Too small; unlikely to play a full octave |
| 0.35 | 8.9 | Soft |
| 0.38 | 9.7 | Medium |
| 0.41 | 10.4 | Loud |
| 0.44 | 11.2 | Too large; unlikely to play a full octave |

The playable band is about ±0.75 mm around the medium value. A printer holds ±0.1 to 0.2 mm, so window length is not your precision risk. Windway height and the labium edge are: 1.14 mm is only six to ten FDM layers, so set it to a whole number of layers.

### Cross-checks from other makers

- Pure Ocarinas puts the sound hole of a 12-hole alto C at about 7 to 9 mm, and 8 to 10 mm for a 10-hole. Heuer's soft value sits at the top of that range and his medium value just above it.
- One maker on r/Ocarina reports 70 to 80 cm³ of chamber with a teardrop window of 35 to 40 mm² for alto C. The lumped model reproduces that with a thin wall and `η_w` near 0.9 to 1.0, higher than my first guess of 0.6 to 0.9.
- Other figures in circulation are 100 cm³ with a 10 × 10 mm window, and a planning workbook using 130 cm³ with a 9 × 5 mm window in a 4 mm wall. These are forum-level numbers. The spread is the reason for a calibration print.

### What the model says an alto C needs

Computed with the kernel for a 12-hole range of A4 to F6, at 27 °C with `η_w` = 0.9 and `k` = 0.8. The 38 mm² area assumes a teardrop about 9 mm long and 6 mm wide; measure the real outline on your reference.

| Window area (mm²) | Wall at window (mm) | Chamber volume (cm³) | Total hole conductance (mm) | Average hole diameter, 3 mm chimney (mm) | Same, 5 mm chimney (mm) |
| --- | --- | --- | --- | --- | --- |
| 38 | 1.6 | 75 | 43 | 6.0 | 7.0 |
| 38 | 3.0 | 63 | 36 | 5.3 | 6.2 |
| 50 | 3.0 | 76 | 44 | 6.0 | 7.0 |
| 64 | 3.0 | 89 | 51 | 6.8 | 7.8 |

A4 to F6 needs total hole conductance 9.1 times the window's. A 10-hole C5 to F6 needs 6.1 times, and a chamber about 0.71 times the volume for the same window.

### Safeguards against high notes dropping out

1. **Keep the window small for the chamber.** Stay at 8.5 to 9 mm length for the first module. A larger window is louder but makes the high end airy.
2. **Design to a rising breath curve.** High notes need more pressure than low notes, and each has a narrow band between airy and screeching. Record the curve on a good reference and solve hole sizes at those pressures, not at one uniform pressure.
3. **Thicken the wall at the window rather than enlarging the chamber.** A deeper window throat acts as a voicing neck: it reaches the same low note with less volume, which leaves more headroom at the top and keeps holes smaller. In a printed core this is one parameter.
4. **Thin the chimneys of the highest holes.** The table shows chimney height adding about 1 mm to hole diameter. Where the shell is thick over the top-note holes, counterbore it so those holes stay coverable.
5. **Keep each hole smaller than the chamber's internal width at that point.** Past that, the chamber itself limits the flow and the pitch stops rising. Watch this where sculpting narrows the chamber.
6. **Build the 10-hole first.** More holes make the top notes airier, and sub-hole notes are the weakest on the instrument. Prove C5 to F6, then add the two sub-holes and the larger chamber they need.
7. **Do not push the labium closer to gain response.** A wide window with a close labium flattens the breath curve but shortens the range.
8. **Keep the windway smooth and the body airtight.** Layer ridges across the jet and porous walls both show up first as airy top notes.

The first three set the voicing module, so they are fixed before any sculpting. Items 4 and 5 become solver constraints in the add-on.

## Global parameters

Lock everything that shapes the air jet, and link everything that enters the Helmholtz equation. The chamber surface and the shell exterior are the only free geometry.

### Locked: the voicing module moves as one rigid body

| Parameter | Why it is locked |
| --- | --- |
| Windway exit height, width, length and taper | Sets jet speed profile and breath resistance |
| Window length W and width | Sets jet transit time and G\_w |
| Labium ramp angle, edge thickness, edge offset | Sets which notes speak and how cleanly |
| Wall thickness at the window | Part of the window's effective length |
| Chamfers at the windway exit | Small changes here alter attack and noise |
| Keep-out zone inside the chamber, about 10 mm behind and below the labium | A wall close to the edge disturbs the jet and adds to the window's end correction |
| Keep-out zone outside the window, flared at 45° or more through the shell | A shell lip over the window lengthens it and shields the jet |

A change to any of these creates a new voicing module that needs its own calibration print.

### Dynamically linked: re-solved on every change

| Parameter | Driven by | Drives |
| --- | --- | --- |
| V\_0, capped cavity volume | Chamber mesh, measured | Lowest note; all hole conductances |
| Target V\_0 | Lowest note, G\_w, η\_w, c | Chamber scale or offset to hit volume |
| Chimney height t\_i per hole | Core wall + shell thickness along the hole axis, measured | Hole diameter |
| Hole diameter d\_i | G\_i, t\_i, k | Chimney volume, so V\_j |
| Fingering table and target frequencies | Your scale, reference pitch, temperament | All G\_i |
| Design air temperature, so c | Playing conditions | Everything |

### Calibration constants: stored per printer, material and voicing module

- `η_w`, window efficiency.
- `k`, hole end-correction coefficient.
- Hole diameter offset, printed minus designed. FDM holes usually print undersize.
- Volume scale factor, printed cavity minus designed, from shrinkage and inner-wall roughness.
- Breath-pressure curve: the pressure at which each note was tuned.

### Constraints the solver enforces

- Hole diameter between a voicing minimum of about 3 mm and the finger pad limit, about 9 to 10 mm for fingers and 12 mm for thumbs. If a solved hole is too large, shorten its chimney or split it into a hole and sub-hole.
- Minimum wall thickness for airtightness. On FDM use at least three perimeters, since porous walls leak, lower the pitch and dull the tone.
- Hole edge spacing of at least one diameter, and holes at least 10 mm from the window.
- Total hole conductance below 9 to 10 times the window conductance.
- Longest internal dimension below a third of the top note's wavelength, or the design is flagged for FEM.

## Reverse-engineering working STLs

Extract the air volume from each reference as its own mesh, measure the same handful of quantities on every one, and trust only references you have printed and recorded yourself.

### Extracting the air domain

An ocarina STL is one solid whose cavity connects to the outside through the holes, so the cavity has no separate shell to measure. Two methods work:

1. **Manual capping.** In Blender, fill each tone hole at its outer rim, the window at the labium plane and the windway at its mouth end. Separate the inner surface and compute its volume. Slow, but exact and good for the first reference.
2. **Voxel flood fill.** With `trimesh`, voxelise at 0.2 mm. Flood-fill the outside air using a probe larger than the biggest hole, so it cannot enter. Everything that is neither solid nor outside is cavity, chimneys and windway. This scripts well for a batch of references.

### What to measure

| Quantity | How | Used for |
| --- | --- | --- |
| V\_0 | Volume of the capped air mesh | Checks the lowest note |
| Window length, width, wall thickness | Section plane through the windway axis | G\_w |
| Windway height at exit and inlet, length | Same section | Voicing module |
| Labium angle, edge thickness, edge offset | Same section | Voicing module |
| Each hole's area and chimney height | Cross-section at mid-chimney; rim-to-rim distance | G\_i |
| Longest internal dimension | Bounding box of the air mesh | Lumped-model validity |

### Ratios to carry forward

Absolute dimensions do not transfer between sizes. Dimensionless groups do:

- Implied `η_w`: the value that makes the lumped model match the reference's lowest note.
- Implied `k`: the value that best fits the rest of its scale.
- W / h, window width / W, and windway length / h.
- Total hole conductance / G\_w, which shows how far that design pushes its range.
- Window area / V\_0^(2/3), a size-independent measure of how large the voicing is for the chamber.
- St at the lowest and highest notes, once you have measured blowing pressure.

If implied `η_w` and `k` agree across three or four good references, the model is trustworthy and those values are your priors. If they scatter, the scatter is your real uncertainty.

### Ground truth

Print each reference unmodified on your own printer. Record every fingering with a phone or USB microphone and extract the fundamental by FFT peak or autocorrelation in Python. Tee a water manometer or a cheap pressure sensor into a mouthpiece tube to log blowing pressure per note. Use the designer's stated tuning only as a cross-check, since it was measured on their printer at their breath.

Check each model's licence before reusing its voicing geometry in work you distribute.

## Validation before printing

Use the lumped model on every edit, an FEM eigenmode check before each print, and no CFD. Pitch is predictable in software. Voicing is not, at hobby cost, so voicing is validated once physically and then frozen.

| Tier | Method | Tools | Predicts | Cost | Verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | Lumped Helmholtz | The kernel in the appendix | Pitch of every fingering, after calibration | Milliseconds | Run live in the add-on |
| 1 | Per-hole Laplace solve | gmsh + scikit-fem or FEniCSx | Exact conductance of an odd-shaped, recessed or oval hole, replacing the `k` approximation | Seconds per hole | Use when a hole sits in sculpted relief |
| 2 | Helmholtz eigenmodes of the air domain | gmsh + scikit-fem, FEniCSx or Elmer | Passive resonance per fingering, including chamber shape and hole position effects | Minutes per fingering | Run before every print |
| 3 | Compressible CFD of the jet | OpenFOAM or a lattice-Boltzmann code | Voicing, attack, breath curve | Days per note, and hard to trust | Skip |

### Tier 2 setup

1. Export the air domain, not the solid: cavity, chimneys of the open holes, window throat.
2. Add a hemisphere of outside air over each open hole and over the window, radius 3 to 5 opening diameters.
3. Mesh with gmsh, refined to about 0.5 mm in the chimneys and window.
4. Solve −∇²p = (2πf/c)² p with rigid walls and p = 0 on the hemisphere surfaces. The lowest eigenvalue is the note.
5. Compare with tier 0. Agreement within 10 cents confirms the lumped model for that shape. A larger gap on the top notes means the chamber is too long, and the FEM value is the one to trust.

This gives the passive resonance. The sounding pitch sits near it and rises with blowing pressure. The offset comes from the calibration print and is carried as part of `η_w`.

Bore-instrument design tools based on transfer matrices, such as those for flutes and whistles, do not apply. They model a tube with side holes, and an ocarina has no tube.

### Geometry checks the add-on runs before export

- Air mesh is manifold and its volume is within 0.5% of target.
- Voicing module vertices are unchanged against the library asset, by hash.
- Every hole has its flat land, spacing and diameter within limits.
- Minimum wall thickness everywhere, by ray-cast sampling.
- Predicted pitch table in cents, tier 0 beside tier 2.

### Physical checks that cannot be skipped

- **Calibration print**, once per printer, material and voicing module. A plain box or egg chamber with the voicing module and four to six holes of known size. Fit `η_w`, `k`, hole offset and volume factor from its recorded notes.
- **Voicing coupons**, only when designing a new voicing module. Print just the mouthpiece and window on a short stub chamber, in a small sweep of window length and edge offset. Pick the one that speaks cleanly at both ends of the range.

## Phased roadmap

Six phases take you from verified math to a first sculpted instrument, with three physical prints before the first stylised shell: one reference, one calibration body, one plain instrument. Each phase has a gate, and you do not start the next until it passes.

| Phase | Work | Gate |
| --- | --- | --- |
| 0. Kernel | Package the appendix script: conductance, diameter inversion, volume bookkeeping, fingering-table least squares, cents report. Add unit tests, including round-trip checks (size holes, then predict the notes back). | Round-trip error under 0.1 cent |
| 1. References | Pick three or four well-reviewed ocarina STLs in your target range. Extract air domains and measure the table in the reverse-engineering section. Print each, record every fingering and blowing pressure. | Lumped model fits each reference within 30 cents using one `η_w` and one `k` per instrument |
| 2. Voicing module and calibration | Author your own voicing module from the best reference's ratios. Print voicing coupons if you change anything. Then print the calibration body and fit `η_w`, `k`, hole offset and volume factor. Set up the tier 2 FEM script and check it against the same print. | Calibrated model predicts every calibration-body note within 10 cents; FEM within 10 cents of that |
| 3. Plain instrument | Design a full-scale instrument with a simple egg chamber and uniform walls, entirely from the kernel and constants. Print, record, compare. Re-fit constants with the new data. | All notes within 15 cents at the recorded breath curve, with no filing |
| 4. Blender add-on | Build in this order: voicing module asset with locked vertices; chamber volume readout and scale-to-target; hole empties that snap to the surface; shell thickness ray-cast; solve and cutter generation; Booleans; pre-export checks; FEM export. | Add-on reproduces the phase 3 instrument's hole sizes within 0.05 mm from the same inputs |
| 5. First stylised shell | Sculpt a non-trivial chamber and shell around the voicing module. Let the add-on hold volume and re-solve holes as you work. Run tier 2, print, record. | All notes within 15 cents on the first print, or within 10 after one constant re-fit and reprint |

### Print practice that protects the acoustics

- Orient so the labium edge and windway floor print without supports touching them. On FDM, run the windway along the layer plane to avoid stair-stepping across the jet.
- Print the mouthpiece as a separate glued insert if that is the only way to get a clean windway. It also lets you reuse one validated insert across shells.
- On SLA, tone holes double as drain holes, but check that no resin is cured inside the windway.
- Seal FDM prints if the calibration body shows leakage: a weak low note and flat pitch that improves when the body is coated.
- Log printer, material, layer height and the fitted constants with every print. The constants table is the asset that removes trial and error over time.

### After the first instrument

Second chambers for extended range and the other sizes on the voicing chart are extensions of the same solver. Neither should start before phase 5 passes.

## Appendix: kernel and worked example

This script is the seed of the phase 0 kernel. I ran it to produce the table below, and the predicted frequencies round-trip to the targets.

```python
import math

def c_air(T_c=27.0):                      # speed of sound, breath-warmed air
    return 331.3 * math.sqrt(1 + T_c / 273.15)

def conductance(area, t, k=0.80):         # hole or window with chimney height t
    d_eq = 2 * math.sqrt(area / math.pi)
    return area / (t + k * d_eq)

def hole_diameter(G, t, k=0.80):          # invert G = (pi d^2/4) / (t + k d)
    return (2 / math.pi) * (G * k + math.sqrt(G * G * k * k + math.pi * G * t))

def freq(G_total, V, c):
    return c / (2 * math.pi) * math.sqrt(G_total / V)

def midi_f(m, a4=440.0):
    return a4 * 2 ** ((m - 69) / 12)

c = c_air(27)
win_w, win_l, t_w, eta_w = 9e-3, 5e-3, 2.5e-3, 0.75   # placeholder voicing module
G_w = eta_w * conductance(win_w * win_l, t_w)
midi = [72, 74, 76, 77, 79, 81, 83, 84, 86, 88]       # C5 .. E6
f = [midi_f(m) for m in midi]
V = G_w * c**2 / (4 * math.pi**2 * f[0]**2)            # chamber volume from tonic
t_ch, k = 4e-3, 0.80
for i in range(1, len(f)):
    G = 4 * math.pi**2 * V / c**2 * (f[i]**2 - f[i-1]**2)
    print(i, round(hole_diameter(G, t_ch, k) * 1e3, 2), "mm")
```

### Inputs

C major from C5 to E6 with linear fingering. Window 9 × 5 mm in a 2.5 mm wall, `η_w` = 0.75, 4 mm chimneys, `k` = 0.80, 27 °C. The `η_w` and `k` values are placeholders until calibrated. Chimney volume correction is left out to keep the example short. This example shows the method on a generic window; the alto C numbers are in their own section.

### Outputs

Speed of sound 347.3 m/s, effective window conductance 3.95 mm, target chamber volume 44.0 cm³. Total hole conductance is 5.35 times the window's, comfortably under the ceiling.

| Hole | Opens | Target (Hz) | Conductance (mm) | Diameter (mm) |
| --- | --- | --- | --- | --- |
| 1 | D5 | 587.3 | 1.03 | 2.87 |
| 2 | E5 | 659.3 | 1.29 | 3.31 |
| 3 | F5 | 698.5 | 0.77 | 2.41 |
| 4 | G5 | 784.0 | 1.83 | 4.12 |
| 5 | A5 | 880.0 | 2.30 | 4.79 |
| 6 | B5 | 987.8 | 2.90 | 5.59 |
| 7 | C6 | 1046.5 | 1.72 | 3.96 |
| 8 | D6 | 1174.7 | 4.10 | 7.11 |
| 9 | E6 | 1318.5 | 5.17 | 8.40 |

Holes 1 and 3 come out under the 3 mm minimum. This is the solver's constraint handling at work: a longer chimney at those two holes raises the diameter for the same conductance, so the add-on would ask for a locally thicker shell there. The semitone steps (holes 3 and 7) are always the small ones.

At an assumed 400 Pa blowing pressure the jet speed is 26 m/s and St runs from 0.10 at C5 to 0.25 at E6. The pressure is an assumption to replace with your manometer readings.

## Sources

- [Chris Heuer, Ocarina One channel](https://www.youtube.com/@ocarinaone): voicing chart and tolerance band, from the transcript and image you supplied.
- [Pure Ocarinas: Identifying playable ocarinas](https://pureocarinas.com/identifying-playable-ocarinas): alto C sound hole sizes; oversize sound hole and airy high notes.
- [Pure Ocarinas: How ocarinas work](https://pureocarinas.com/how-ocarinas-work): voicing neck, range versus chamber volume.
- [Pure Ocarinas: Playing characteristics and timbre](https://pureocarinas.com/ocarina-playing-characteristics-timbre): sound hole size, aspect ratio and breath curve.
- [Pure Ocarinas: Why does my ocarina have airy high notes?](https://pureocarinas.com/why-ocarina-airy-high-notes): pressure, hole count.
- [Pure Ocarinas: How chamber shape affects range](https://pureocarinas.com/ocarina-chamber-shape-range-chamber-volume-bypassing): hole size versus chamber width.
- [Pure Ocarinas: Warm or cold environments](https://pureocarinas.com/ocarina-tutorial/playing-ocarinas-in-warm-or-cold-environments): measured pitch change per °C.
- [r/Ocarina weekly thread, November 2024 (mirror)](https://axebps-redlib.hf.space/r/Ocarina/comments/1grps3f/no_stupid_questions_open_conversation_weekly): makers' alto C volumes and window sizes.
- [Tony Koop, ocarina build packet](https://tonykoop.github.io/ocarina/design.md): planning workbook inputs for an alto C.

I worked from search excerpts of these pages rather than reading each in full, so check the originals before fixing a dimension.
