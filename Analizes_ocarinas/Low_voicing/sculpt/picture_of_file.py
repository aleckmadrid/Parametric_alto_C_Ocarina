"""Pictures of what is in the sculpt file (for the instructions).

    blender -b --factory-startup --disable-autoexec sculpt/OCA_sculpt_base.blend --python sculpt/picture_of_file.py
"""
import pathlib
import sys

import numpy as np

import bpy

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from ocarina_addon import meshutil, render  # noqa: E402

COL = dict(shell=(0.78, 0.74, 0.62, 1.0), neck=(0.62, 0.50, 0.36, 1.0), cut=(0.85, 0.15, 0.15, 1.0), keepout=(1.0, 0.1, 0.65, 1.0),
           mouth_end=(0.0, 0.7, 0.2, 1.0), limit=(1.0, 0.55, 0.0, 1.0), chamber=(0.25, 0.5, 1.0, 1.0))
X, Y, Z = np.eye(3)
VIEWS = {"_thumb": (tuple(Z), tuple(-Y)), "_three": (tuple(0.62 * Y + 0.70 * Z + 0.35 * X), tuple(-0.70 * Y + 0.62 * Z)),
         "_end": (tuple(-X), tuple(Z)), "_deck": (tuple(-Z), tuple(-Y))}
for col in bpy.data.collections:
    col.hide_viewport = False
(HERE / "images").mkdir(exist_ok=True)
for key in ("A", "B"):
    solids, inside = [], []
    for ob in bpy.data.objects:
        role = ob.get("oca_role")
        if ob.type != "MESH" or role is None or f"sculpt{key}" not in ob.name and not ob.name.startswith(f"{key}_"):
            continue
        if role in ("preview", "cuts", "pocket"):
            continue
        ob.hide_viewport = False
        V, F, _ = meshutil.evaluated_arrays(ob)
        (inside if role in ("chamber", "limit") else solids).append((V, F, COL.get(role, (0.5, 0.5, 0.5, 1.0))))
    for name, meshes in (("outside", solids), ("inside", [m for m in inside] + [m for m in solids if m[2] in (COL["cut"], COL["keepout"], COL["mouth_end"])])):
        for v, look in VIEWS.items():
            render.VIEWS[v] = look
            p = render.render_views(meshes, str(HERE / "images"), prefix=f"file_{key}_{name}", views=(v,), size_px=900)[0]
            print("PICTURE", p, flush=True)
