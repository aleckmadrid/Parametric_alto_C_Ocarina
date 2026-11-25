"""Every through hole of the reference body, by rays through the two faces (the voxel pipeline missed a small one).

    python Analizes_ocarinas/Low_voicing/ref_oot_blend/find_holes.py
"""
import json
import pathlib

import numpy as np
import trimesh
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
d = np.load(HERE / "models" / "oot_blend_meshes.npz")
body = trimesh.Trimesh(d["Ocarina Body|eval|V"], d["Ocarina Body|eval|F"], process=True)
outer = np.load(HERE / "models" / "oot_blend_outer.npz")
skin = trimesh.Trimesh(outer["V"], outer["F"], process=True)
step = 0.4
res = []
for face, sgn in (("deck", 1.0), ("thumb", -1.0), ("far", None)):
    if sgn is None:                                   # from the side away from the player, looking toward +z
        xs, ys = np.arange(-92, 80, step), np.arange(-28, 27, step)
        G = np.array([(x, y, -60.0) for x in xs for y in ys])
        D = np.tile([0, 0, 1.0], (len(G), 1))
        ax = 2
    else:
        xs, zs = np.arange(-92, 80, step), np.arange(-31, 33, step)
        G = np.array([(x, -60.0 * sgn, z) for x in xs for z in zs])
        D = np.tile([0, sgn, 0.0], (len(G), 1))
        ax = 1
    n2 = len(G) // len(xs)
    first_body = np.full(len(G), np.nan)
    first_skin = np.full(len(G), np.nan)
    for mesh, arr in ((body, first_body), (skin, first_skin)):
        loc, ray, _ = mesh.ray.intersects_location(G, D, multiple_hits=True)
        dist = np.abs(loc[:, ax] - G[ray, ax])
        order = np.argsort(dist)[::-1]
        arr[ray[order]] = dist[order]                 # the nearest hit wins (written last)
    through = (first_body - first_skin) > 6.0         # the ray entered where the skin was cut away and went on into the chamber
    img = through.reshape(len(xs), n2)
    lab, n = ndi.label(img)
    for k in range(1, n + 1):
        m = lab == k
        area = m.sum() * step * step
        if area < 1.5:
            continue
        i, j = np.nonzero(m)
        pts = G.reshape(len(xs), n2, 3)[i, j]
        c = pts.mean(axis=0)
        depth = np.nanmedian(first_skin.reshape(len(xs), n2)[i, j])
        c[ax] = G[0, ax] + (1 if (sgn or 1) > 0 and ax == 1 or ax == 2 else -1) * depth
        res.append(dict(face=face, centre=[round(float(v), 2) for v in c], projected_area_mm2=round(float(area), 2),
                        d_projected_mm=round(float(2 * np.sqrt(area / np.pi)), 2),
                        extent_mm=[round(float(np.ptp(pts[:, a])), 1) for a in range(3)]))
res.sort(key=lambda r: r["centre"][0])
(HERE / "holes_by_rays.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
for r in res:
    print(r)
