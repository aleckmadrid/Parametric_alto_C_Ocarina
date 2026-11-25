# The owner's low-voicing reference: "Ocarina of time Blender.blend"

Sent by the owner on 2026-11-20 from their Downloads folder, with its STL export (`ocarina-of-time.stl`). The owner's words: "this one achieves a slightly simillar shape to the one we want with the lower voicing without the intenral geometry", "playable", "a good voicing cut approach, a similar windway tilt and neck blend and position to what we are aiming for and using a thicker internal geometry to achieve this result smothly".

What was found is written up in [Low_voicing.md](../Low_voicing.md), section 11. This folder holds the tools and their output.

## The files (third-party, not in git)

| File here | Original | SHA-256 |
| --- | --- | --- |
| `models/oot_blend_body.stl` | `ocarina-of-time.stl` (194 922 triangles, no header text) | `7602dad236f9ff30613773ee3051c011e27d1189ce4f5d6ebaab7995ca3751e4` |
| `models/oot_blend_meshes.npz`, `models/oot_blend_outer.npz` | the three objects of `Ocarina of time Blender.blend` (`68f63ced…0393aa`), exported by Blender 5.1 with its scripts switched off | made here |

The blend file holds three objects: `Ocarina Body` (1 033 vertices, a subdivision surface of level 3, with two Boolean differences), `Ocarina Body Cavity` (the chamber, with a stub for every hole) and `Pipe Boolean` (the windway). The STL is exactly the evaluated body. Its source and licence are not known to me: it is not committed, and it should not be published with the repository.

**It is not the ECAN3 Ocarina of Time** of `Analizes_ocarinas/ECAN3_experimental/` (another file, another shape: this one has no walls inside).

## Frame of the file

x = body length (the bulb at +x, the tail at −x), y = thickness (the thumb face at +y, the finger deck at −y), z = toward the player (the mouthpiece points to +z). Hands: the tail is the right hand, the bulb the left.

## Tools

| Script | What it does | Output |
| --- | --- | --- |
| `run_analysis.py` | The ECAN3 voxel pipeline (`../../ECAN3_experimental/tools/analyze_model.py`) with this folder as its root: air volume, every opening, the kernel and cell-network back-fit | `output/ootb/report.md`, `results.json` |
| `find_holes.py` | Every through hole by rays through the faces (the pipeline finds the small left subhole but measures its neighbour twice) | `holes_by_rays.json` |
| `measure_ref.py`, `measure_details.py` | Volumes, sections, the windway ring by ring, shell thickness, the dish, the mouthpiece | `measure_ref.json`, `images/ref_section_*.png` |
| `lip_scan.py` | The window and the lip, cut by cut across the window | `lip_scan.json` |
| `tune_test.py` | The kernel's scale with nothing fitted to a note, against two tuned ECAN3 instruments | `tune_test.md`, `tune_test.json` |
| `any_order.py` | The least any order of opening the twelve holes could leave | `any_order.json` |

Rebuild `models/` from the owner's two files: copy the STL in, and export the meshes with Blender (`--factory-startup --disable-autoexec`), as `oot_blend_meshes.npz` (each object raw and evaluated) and `oot_blend_outer.npz` (the body with its Booleans switched off).
