# Geometry check reports

Written by `tools/geometry_check.py` in Blender 5.1 during checkpoints C3 and C4.

**Stale since 2026-11-17.** These reports predate two changes: the ladder change (P0-88 and P0-95-w3 have no report; P0-110 and P0-125 are kept as range checks) and the labium default of −0.2 mm (the reports show offset 0.000 mm and the old voicing hashes, for example `d1b6418b1844` for the 80 cm³ window, now `617b869f0b10`). Rerun `blender -b --factory-startup --python tools/geometry_check.py -- bodies` and `-- cavities` to refresh them.
