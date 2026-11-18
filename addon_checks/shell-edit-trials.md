# Shell-edit build: trials

Written by `tools/shell_edit_trial.py` for the base P4-80. The shell-edit build is a PROTOTYPE (`ocarina_addon/shell_edit.py`): the add-on makes the solid shell and the solid neck, they are edited, and the add-on then cuts the chamber, the holes and the voicing. In these trials a program made the edits a user could make.

*Scale with the base's holes* is what the edit would have done if the holes had kept the sizes of the base: the kernel's model with the walls measured on the edited shell. It is a prediction, not a measurement. *Finished body* is what the add-on built after it sized every hole for its own wall; its numbers are measured on the STL file.

| Trial | Edits | Shell triangles | Wall at the holes | Scale with the base's holes: A4, worst note | Largest hole change | Sizing rounds | Chamber | Capped air (target) | Length | Plastic | Largest hole / chimney error | Result | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | none | 32512 | 4.00 to 4.00 mm | -0, -0 cents | +0.00 mm (sub1) | 1 | 78.11 cm³ (base 78.11) | 80.00 cm³ (80.00) | 140 mm | 58.3 cm³ | 0.000 / 0.007 mm | no unexpected failure | 61 s |
| `tail` | tail 25 mm longer (the last 10 mm of the body stretched) | 32512 | 4.00 to 4.00 mm | -0, +0 cents | +0.00 mm (sub1) | 1 | 78.11 cm³ (base 78.11) | 80.00 cm³ (80.00) | 165 mm | 60.4 cm³ | 0.000 / 0.007 mm | no unexpected failure | 59 s |
| `sculpt` | tail 25 mm longer (the last 10 mm of the body stretched); boss +1.5 mm high, 8 mm radius, over R_ring; groove 0.9 mm deep, 4 mm wide, across the rim of L_middle; relief up to 0.6 mm, 7 mm pattern, none within 16 mm of the window; neck 20 % thicker toward the mouth end (roof line and mouth end plane kept) | 32512 | 3.96 to 5.78 mm | -2, -50 cents | +0.65 mm (R_ring) | 3 | 77.85 cm³ (base 78.11) | 80.00 cm³ (80.00) | 166 mm | 66.5 cm³ | 0.000 / 0.007 mm | no unexpected failure; warnings: shell_hole_walls, shell_hole_rims | 56 s |
| `remesh` | voxel remesh at 0.6 mm on the shell and the neck, cloud displacement up to 0.5 mm on the shell (modifiers) | 119120 | 4.20 to 4.37 mm | -1, -22 cents | +0.15 mm (L_pinky) | 3 | 77.93 cm³ (base 78.11) | 80.00 cm³ (80.00) | 140 mm | 61.8 cm³ | 0.000 / 0.007 mm | no unexpected failure | 100 s |
| `thick` | 2.5 mm more plastic over the finger deck | 32512 | 4.02 to 6.72 mm | -8, -186 cents | +1.19 mm (L_middle) | 3 | 76.78 cm³ (base 78.11) | 80.01 cm³ (80.00) | 143 mm | 76.2 cm³ | 0.000 / 0.007 mm | no unexpected failure; warnings: shell_hole_walls | 63 s |

The check report of each finished body is `addon_checks/<id>.md`, with <id> = `P4-80-edit-<trial>`.
