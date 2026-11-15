# ECAN3 analysis: method and validation

This page explains how the numbers in [ECAN3_experimental.md](ECAN3_experimental.md) are produced and how far they can be trusted. The tools are separate from the main kernel/add-on on purpose: they are research tooling for testing chamber-shape ideas (open question Q6 in [docs/02](../../docs/02-unified-plan.md)) before anything moves into the parametric design.

## 1. Toolchain

| Tool | Version used | Role |
| --- | --- | --- |
| Python | 3.12 | |
| trimesh | 4.x/5.x (pip `trimesh`) | STL loading, body splitting, slicing, ray casts |
| manifold3d | pip | robust mesh booleans (installed for trimesh; not needed by the current pipeline) |
| scipy | 1.18 | Euclidean distance transforms, labelling, sparse eigen-solver, optimisation |
| scikit-image | 0.26 | polygon rasterising, watershed |
| numpy, matplotlib | numpy 2.5 | arrays, figures |

Install: `python -m pip install trimesh manifold3d scipy rtree networkx shapely scikit-image matplotlib`. No GUI program is needed. Blender's 3D-Print Toolbox gives the same solid volume (the mesh volume is exact for a watertight STL); it cannot by itself separate cavity air from exterior air, cap the tone holes, or measure walls, which is why the voxel pipeline exists.

## 2. Pipeline (`tools/voxcav.py`, `tools/analyze_model.py`)

1. **Load** the STL, keep the largest body. Every analysed model is a single watertight shell (genus 13 = 12 tunnels: the openings plus the windway).
2. **Voxelize** at 0.30 mm (Eclipse 0.33 mm). Each z-slice of the mesh is filled with the even-odd rule. Check: voxel solid volume vs exact mesh volume, e.g. 31,504.6 vs 31,499.3 mm³ (+0.017 %) for V0N3.
3. **Exterior** = the air a ball of radius R = 8 mm can reach from outside (morphological opening via distance transforms). The ball is wider than any tone hole, so it cannot enter the chamber.
4. **Cavity** = the remaining air. Channels thinner than 1.6 mm (the windway, about 1.2–1.5 mm high) are cut, the largest piece is kept, and corners are restored by a short geodesic dilation.
5. **Hole caps.** The ball dips into each hole by δ = R − √(R² − a²), so the cavity is capped slightly below the outer rim. The spherical-cap volume (`cap_correction`) is added back, giving **V0 capped at the outer rims**, the kernel's convention (closed chimneys belong to V0, the window throat is neck).
6. **Internal walls** = solid enclosed by cavity, closing(cavity, 2.5 mm) ∩ solid, keeping only solid deeper than one shell thickness (+0.4 mm) from the outside air. Without that depth filter, the shell ring around every hole's inner rim would count as "wall". The walls are split by connected component into three groups:
   - **voicing structure**: components that reach within 12 mm of the window;
   - **hole tubes and bosses**: components that touch a hole bore;
   - **free walls**: septa, fins and pocket covers.
   
   Only free walls are removed in the walls-removed counterfactual, so the holes and the voicing stay identical.
7. **Openings** = patches where the cavity touches the ball-reachable exterior. Each is measured on the mesh (`measure_hole`). The axis is the weakest eigenvector of the bore-wall normals. A_min is the narrowest closed section ring around the axis. t is the median chimney length from 36 rays parallel to the axis just outside the bore. If that fails (thin, oblique or lens-shaped holes), the axis falls back to the patch normal, then to the local surface normal.
8. **Sub-volumes** = parts of the cavity joined only through gaps narrower than 2 r_neck (5 mm and 8 mm reported). These are seeds where the inscribed radius exceeds r_neck, followed by a watershed on the distance map. Interface areas are the neck areas.
9. **Placement metrics** per hole: local chamber diameter (largest inscribed ball within 10 mm), the hole/chamber ratio (Pure Ocarinas' bypass condition), distance to the nearest internal wall, and the window-to-hole path length through the air vs the straight-line distance.

## 3. Acoustic models

**Single-volume kernel** (repo `kernel/ocarina_kernel.py`): f = c/2π √((G_w + ΣG_open)/(V0 − ΣA t_open)), with G = A/(t + k d_eq).

**Cell network** (`tools/cellnet.py`). The cavity is cut into about 4 mm cells: a geodesic Voronoi of lattice seeds, so no cell crosses a wall. Each pair of neighbouring cells is joined by the inertance of their shared face (G_ab = A_ab/|x_a − x_b|). Each open hole and the window is the kernel conductance from its cells to p = 0:

    (Lap(G_ab) + diag(G_open)) p = (ω/c)² diag(V) p

**Bores are neck, not cells.** Each hole's chimney, including any inward tube, is carved out of the cell cavity (a cylinder of radius d/2 + 0.6 mm from the inner end of the chimney to the rim). The hole is attached at the cells next to the bore's inner end, so its full chimney is counted once, in the kernel conductance. While a hole is closed, its chimney volume A·t is added back to those cells, matching the kernel's V0 convention. Without the carving, an 8 mm inward tube was counted twice (once resolved by cells, once in t), and the Eclipse notes on tube holes came out 50–85 cents flat.

The lowest eigenpair is the played Helmholtz mode. Its shape gives three numbers:

- **participation ratio** (Σ V p)² / (V Σ V p²): 1 means uniform pressure, the kernel's assumption.
- **V_eff = Σ V p / p_bulk**, the air the mode drives relative to the bulk pressure (the volume-weighted median of |p|). Below V0 means part of the air lags behind (is bypassed).
- **bypassed share** = air with |p| below half the bulk pressure.

The bulk is the reference rather than the window cells, because a window opening into a recess (OOT) otherwise inflates every ratio.

Higher eigenvalues are the cavity (standing-wave) modes, used for the lumped-model validity check of doc 03 §8.

**De-embedding.** The kernel's end correction k already contains the inner (cavity-side) end correction. Attaching a hole to a few cells would add the near-hole converging flow a second time. Two things prevent that:

- each opening is spread over the cells within a 7 mm geodesic radius (never across a wall);
- the half-space spreading conductance S = 2π R_eff of that region is removed: 1/G_net = 1/G − 1/S.

**Fitting.** The window conductance is always fitted so the all-closed note is exact; the window geometry of these printed voicings is not reliable enough to predict it. The end-correction coefficient k is then fitted per model (and separately for each acoustic model) to minimise the RMS cents of the whole scale. With the window fitted and k fitted, the only remaining freedom is the geometry, so the residual pattern is what each model fails to explain.

## 4. Validation (`tools/test_cellnet.py`, all passing)

| Case | Reference | Result |
| --- | --- | --- |
| Sphere r = 25 mm, window + one hole, G 4–13 mm | single-volume Helmholtz | within ±1 % (±0.4 % in the attachment study) |
| Closed box 100 mm long | first cavity mode c/2L | within 1 % |
| Two boxes joined by a 6 × 6 mm aperture in a 2 mm wall, hole on the far box | two-node coupled Helmholtz with the kernel aperture conductance | within 6 % |

**Attachment-radius study** (sphere, before de-embedding): attaching an opening to only the cells it touches made the network 8 % flat at G = 4 mm. The error behaved as a series conductance S ≈ 2π × attachment radius, which is exactly the half-space spreading term the kernel's k already contains; de-embedding removes it.

**Cell-size sensitivity** (`tools/convergence.py`, cells 3/4/5 mm × attachment 5/7/9 mm, k fixed, window refitted, final bore-carved setup). Max−min spread across the nine settings:

| Model | Lowest note | Low to C6 | Top three notes |
| --- | --- | --- | --- |
| V0N3 | 0 cents (C5) | 4–7 cents | 15–20 cents |
| OOT | 0 cents (A4) | 2–6 cents | 5–10 cents |

Network effects smaller than about 10 cents (OOT) to 20 cents (V0N3) at the top of the scale are therefore not resolved.

## 5. Known limitations

- **No finger shading, no hole–hole interaction, no jet.** A finger hovering over an open hole lowers its conductance, and so do neighbouring open holes sharing their external flow field. The sounding pitch also drifts with blowing pressure. All of these are absorbed, on average, by the fitted k. Their note-to-note pattern is not modelled.
- **CAD, not prints.** The STLs are design intent. FDM prints holes about 0.1–0.4 mm undersize and shells slightly thick. ECAN3 tuned the designs on real prints, so the CAD hole sizes already contain his printer's offsets.
- **Fingering assumption.** Hole names come from position and the standard 12-hole (and 10-hole) chart: subholes first, then the right hand from the pinky, the left hand from the pinky, the left thumb, then the right thumb. Swapping the two thumbs changes the V0N3 fit only slightly (RMS 28 → 24 cents with the kernel).
- **Window.** The voicing notch is not a bore, so its measured area is only indicative. The window conductance is always fitted.
- **Temperature.** 27 °C (kernel convention). The fitted window absorbs any uniform offset.
