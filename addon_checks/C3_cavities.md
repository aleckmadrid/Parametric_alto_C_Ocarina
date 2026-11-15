# C3 geometry check: cavity presets

Written by `tools/geometry_check.py -- cavities`. Every number is measured on the evaluated mesh.

Result: **all cavities pass** (20 cavities, 33 s).

- Target: `BodySizing.cavity_volume_for_mesh_cm3` of the kernel for the P0 hole set at that V0 (plain cavity, before the voicing pocket of C4).
- Port before / after: distance from the origin to the nearest mesh vertex, for the preset at 40 cm³ (before) and at the target (after). The port is the origin by construction, so both must be zero.
- Normal change: angle between the mesh normals at the port before and after scaling.
- Mesh vs formula: largest distance between the cavity formula (`cavity_math.py`) and the mesh, on a grid of samples.
- Stage 2 marks the volumes that the test plan prints for that shape.

| Preset | V0 cm³ | Stage 2 | Target cm³ | Measured cm³ | Error % | Length mm | Width × height mm | Port before mm | Port after mm | Normal change ° | Mesh vs formula mm | Manifold | Shells | Zero edges | Self-intersections | c/(2L) ÷ F6 | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | 65 | yes | 63.640 | 63.6402 | -0.00002 | 73.21 | 49.9 × 33.3 | 5.3e-06 | 6.2e-06 | 0.0000 | 1.1e-05 | yes | 1 | 0 | 0 | 1.698 | pass |
| P0 | 80 | yes | 78.113 | 78.1125 | -0.00002 | 78.39 | 53.4 × 35.6 | 5.3e-06 | 6.7e-06 | 0.0000 | 1.2e-05 | yes | 1 | 0 | 0 | 1.586 | pass |
| P0 | 95 | yes | 92.545 | 92.5445 | -0.00001 | 82.94 | 56.6 × 37.7 | 5.3e-06 | 7.1e-06 | 0.0000 | 1.4e-05 | yes | 1 | 0 | 0 | 1.499 | pass |
| P0 | 110 |  | 106.932 | 106.9319 | -0.00002 | 87.04 | 59.3 × 39.6 | 5.3e-06 | 7.4e-06 | 0.0000 | 1.4e-05 | yes | 1 | 0 | 0 | 1.428 | pass |
| P0 | 125 | yes | 121.275 | 121.2747 | -0.00003 | 90.77 | 61.9 × 41.3 | 5.3e-06 | 7.7e-06 | 0.0000 | 1.5e-05 | yes | 1 | 0 | 0 | 1.370 | pass |
| P1 | 65 |  | 63.640 | 63.6402 | +0.00000 | 102.87 | 45.4 × 31.8 | 3.8e-06 | 4.4e-06 | 0.0000 | 1.3e-05 | yes | 1 | 0 | 0 | 1.208 | pass |
| P1 | 80 | yes | 78.113 | 78.1125 | -0.00002 | 110.14 | 48.7 × 34.1 | 3.8e-06 | 4.7e-06 | 0.0000 | 1.3e-05 | yes | 1 | 0 | 0 | 1.129 | pass |
| P1 | 95 |  | 92.545 | 92.5445 | -0.00001 | 116.55 | 51.5 × 36.0 | 3.8e-06 | 5.0e-06 | 0.0000 | 1.6e-05 | yes | 1 | 0 | 0 | 1.067 | pass |
| P1 | 110 |  | 106.932 | 106.9319 | -0.00001 | 122.30 | 54.0 × 37.8 | 3.8e-06 | 5.2e-06 | 0.0000 | 1.5e-05 | yes | 1 | 0 | 0 | 1.016 | pass |
| P1 | 125 |  | 121.275 | 121.2747 | -0.00002 | 127.54 | 56.3 × 39.4 | 3.8e-06 | 5.4e-06 | 0.0000 | 1.9e-05 | yes | 1 | 0 | 0 | 0.975 | pass |
| P2 | 65 |  | 63.640 | 63.6402 | +0.00001 | 116.77 | 47.5 × 31.4 | 4.0e-06 | 4.7e-06 | 0.0000 | 1.3e-05 | yes | 1 | 0 | 0 | 1.065 | pass |
| P2 | 80 | yes | 78.113 | 78.1125 | -0.00001 | 125.02 | 50.9 × 33.6 | 4.0e-06 | 5.1e-06 | 0.0000 | 1.7e-05 | yes | 1 | 0 | 0 | 0.994 | pass |
| P2 | 95 |  | 92.545 | 92.5445 | -0.00000 | 132.29 | 53.8 × 35.5 | 4.0e-06 | 5.4e-06 | 0.0000 | 1.5e-05 | yes | 1 | 0 | 0 | 0.940 | pass |
| P2 | 110 |  | 106.932 | 106.9319 | -0.00001 | 138.82 | 56.5 × 37.3 | 4.0e-06 | 5.6e-06 | 0.0000 | 1.8e-05 | yes | 1 | 0 | 0 | 0.895 | pass |
| P2 | 125 |  | 121.275 | 121.2747 | +0.00001 | 144.77 | 58.9 × 38.9 | 4.0e-06 | 5.9e-06 | 0.0000 | 1.9e-05 | yes | 1 | 0 | 0 | 0.859 | pass |
| P3 | 65 |  | 63.640 | 63.6402 | +0.00002 | 88.11 | 47.0 × 29.4 | 5.6e-06 | 6.6e-06 | 0.0000 | 1.6e-05 | yes | 1 | 0 | 0 | 1.411 | pass |
| P3 | 80 | yes | 78.113 | 78.1125 | +0.00001 | 94.34 | 50.3 × 31.4 | 5.6e-06 | 7.0e-06 | 0.0000 | 1.7e-05 | yes | 1 | 0 | 0 | 1.318 | pass |
| P3 | 95 |  | 92.545 | 92.5446 | +0.00002 | 99.82 | 53.2 × 33.3 | 5.6e-06 | 7.4e-06 | 0.0000 | 1.8e-05 | yes | 1 | 0 | 0 | 1.245 | pass |
| P3 | 110 |  | 106.932 | 106.9319 | +0.00003 | 104.75 | 55.9 × 34.9 | 5.6e-06 | 7.8e-06 | 0.0000 | 1.9e-05 | yes | 1 | 0 | 0 | 1.187 | pass |
| P3 | 125 |  | 121.275 | 121.2747 | +0.00003 | 109.24 | 58.3 × 36.4 | 5.6e-06 | 8.1e-06 | 0.0000 | 2.0e-05 | yes | 1 | 0 | 0 | 1.138 | pass |
