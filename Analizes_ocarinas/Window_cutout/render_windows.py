"""Outside views of the windows listed in frames.json (written by measure_windows.py). Run with Blender:

    blender -b --factory-startup --python Analizes_ocarinas/Window_cutout/render_windows.py

Two pictures per model, both orthographic and 44 mm across: straight into the window (the jet runs upward in
the picture) and from three quarters, looking with the jet. Writes images/outside_<model>_<view>.png.
"""
import json
import pathlib
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from ocarina_addon import meshutil, render  # noqa: E402

HALF = 22.0


def read_stl(path):
    dtype = np.dtype([("normal", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")])
    with open(path, "rb") as fh:
        fh.seek(80)
        n = int(np.frombuffer(fh.read(4), dtype="<u4")[0])
        return np.frombuffer(fh.read(n * dtype.itemsize), dtype=dtype, count=n)["v"].astype(np.float64)


def main():
    frames = json.loads((HERE / "frames.json").read_text(encoding="utf-8"))
    scene = render._reset_scene()
    cam = render._camera(scene)
    for o in list(scene.objects):
        if o is not cam:
            o.hide_render = True
    scene.render.resolution_x = scene.render.resolution_y = 900
    cam.data.ortho_scale = 2 * HALF
    only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for name, m in frames.items():
        if only and not any(name.startswith(o) for o in only):
            continue
        if not pathlib.Path(m["path"]).is_file():
            print("skipped", name)
            continue
        E, c, a, n = (np.array(m[k], float) for k in ("exit", "c", "a", "n"))
        centre = E + 0.6 * m["length"] * c
        tri = read_stl(m["path"])
        keep = np.linalg.norm(tri.mean(axis=1) - centre, axis=1) < 70.0
        tri = tri[keep]
        V = tri.reshape(-1, 3)
        F = np.arange(len(V)).reshape(-1, 3)
        ob = meshutil.object_from_arrays(f"_win_{name}", V, F)
        ob.data.shade_flat()
        ob.color = (0.78, 0.76, 0.70, 1.0)
        for view, look, up in (("front", -n, c), ("oblique", -n * 0.75 + c * 0.55 + a * 0.35, n)):
            render._aim(cam, tuple(look), tuple(up), tuple(centre), HALF, HALF)
            scene.render.filepath = str(HERE / "images" / f"outside_{name}_{view}.png")
            bpy.ops.render.render(write_still=True)
        mesh = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.meshes.remove(mesh)
        print("rendered", name)


main()
