"""The blend between the neck and the body: a rolling-ball fillet on the joined outside (EXPERIMENT code of series 3).

Two halves in one file.

In Blender (install(body_mod)): body.build_body calls OUTER_MESH_HOOK with the outside of the body before anything is
cut out of it (the plain skin joined with the neck). A preset with neck_blend_mm gets a fillet: the outside is
written to a file, this same file is run by the system Python (which has scipy, trimesh and scikit-image; Blender's
Python has not), and the fillet it returns is joined to the outside. Every later step of the build is the add-on's:
the chamber, the holes and the voicing are cut out of the blended outside, and every check runs on the result.

In the system Python (python blend_fillet.py job.npz out.npz):
  1. the outside is voxelized (0.4 mm) around the root of the neck;
  2. a ball of radius r is rolled over it: grow the solid by r, then shrink it by r. That fills every hollow crease
     to the radius of the ball and leaves every convex surface where it was;
  3. the radius is not the same everywhere: near a tone hole the small radius is used, inside the keep-out of the
     window nothing is added;
  4. the added plastic is turned back into a mesh.

Preset keys (not hashed: the outside only)
    neck_blend_mm        radius of the ball, mm (no key = no blend)
    neck_blend_hole_mm   radius near a tone hole (default 2)
    neck_blend_bulb_mm   radius on the bulb side of the neck (default = neck_blend_mm); with neck_blend_mm on the
                         tail side this gives the lopsided root: a long sweep toward the tail, a tight one to the bulb
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
VOXEL_MM = 0.4
VOXEL_COARSE_MM = 0.6          # for a ball of more than 10 mm: the box is then nearly the whole body
LAST = {}


# ====================================================================== the Blender half

def install(body_mod, work_dir):
    from ocarina_addon import cavity_mode, holes_layout, meshutil

    def hook(envelope, ctx):
        preset = ctx["preset"]
        LAST.clear()
        if preset.get("neck_blend_mm") is None:
            return envelope
        fr = sys._getframe(1).f_locals                      # build_body: the sizing the layout will be made from (experiment code)
        lay = holes_layout.make_layout(ctx["cavity"].math, preset, body_mod.cut_rows(fr["sz"], fr["hole_key"]), slide_max_mm=fr["slide_max"])
        vs, v = ctx["voicing"], ctx["sizing"].voicing
        o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
        work = pathlib.Path(work_dir)
        work.mkdir(parents=True, exist_ok=True)
        job, out = work / f"blend_job_{os.getpid()}.npz", work / f"blend_out_{os.getpid()}.npz"    # two builds may run side by side
        params = dict(r=float(preset["neck_blend_mm"]), r_hole=float(preset.get("neck_blend_hole_mm", 2.0)),
                      r_bulb=float(preset.get("neck_blend_bulb_mm", preset["neck_blend_mm"])),
                      wall=float(v.wall_at_window_mm), L=float(v.window_length_mm),
                      h=VOXEL_MM if float(preset["neck_blend_mm"]) <= 10.0 else VOXEL_COARSE_MM,
                      tail_sign=float(np.sign(np.asarray(ctx["cavity"].V)[:, 0].mean() - o[0]) or 1.0))
        np.savez_compressed(job, V=np.asarray(envelope[0], float), F=np.asarray(envelope[1], np.int64),
                            frame=np.stack([o, fx, fy, fz]), outline=np.asarray(vs.outline, float)[:, :2],
                            holes=np.array([[*h.centre, *h.axis, h.d_mm] for h in lay.holes], float), params=json.dumps(params))
        exe = cavity_mode.find_python()[0]
        if not exe:
            raise meshutil.GeometryError("the blend needs a Python with scipy, trimesh and scikit-image; none was found")
        if out.exists():
            out.unlink()
        r = subprocess.run([exe, str(pathlib.Path(__file__).resolve()), str(job), str(out)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900, env=dict(cavity_mode._env(), PYTHONIOENCODING="utf-8"))
        if r.returncode != 0 or not out.exists():
            raise meshutil.GeometryError(f"the blend failed: {r.stderr[-600:]}")
        z = np.load(out)
        info = json.loads(str(z["info"]))
        if len(z["F"]) == 0:
            LAST.update(info, added_mm3=0.0)
            return envelope
        before = meshutil.volume(*envelope)
        a, b, _ = meshutil.boolean(envelope, (z["V"], z["F"]), "UNION")
        new = meshutil.cleanup(a, b, merge_mm=1e-3, no_self_intersection=True)
        rep = meshutil.manifold_report(*new)
        if not rep["manifold"] or rep["shells"] != 1:
            raise meshutil.GeometryError(f"the blended outside is not one closed shell ({rep['shells']} shells)")
        LAST.update(info, added_mm3=float(meshutil.volume(*new) - before), triangles=int(len(new[1])))
        print(f"[blend] ball {params['r']:g} mm (bulb side {params['r_bulb']:g}, near holes {params['r_hole']:g}): "
              f"{LAST['added_mm3'] / 1000:.2f} cm3 of plastic added", flush=True)
        return new

    body_mod.OUTER_MESH_HOOK = hook


# ====================================================================== the system-Python half

def _closing(s_out, h, r):
    """Signed field of the solid closed by a ball of radius r: below 0 inside. s_out is the distance outside the solid."""
    from scipy import ndimage as ndi
    grown = s_out <= r
    e = ndi.distance_transform_edt(grown) * h              # how deep inside the grown solid
    return np.where(grown, r - e, s_out)


def _smooth(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def worker(job_path, out_path):
    import trimesh
    from scipy import ndimage as ndi
    from skimage import measure
    sys.path.insert(0, str(HERE.parent / "ECAN3_experimental" / "tools"))
    import voxcav as vc

    z = np.load(job_path)
    P = json.loads(str(z["params"]))
    h, r, r_hole, r_bulb = P["h"], P["r"], P["r_hole"], P["r_bulb"]
    mesh = trimesh.Trimesh(z["V"], z["F"], process=False)
    o, fx, fy, fz = z["frame"]
    # only the region of the neck's root: a box around the window, grown by the largest ball
    reach = 30.0 + 2.0 * max(r, r_bulb)
    lo, hi = o - reach, o + reach
    solid, g = vc.voxelize_solid(mesh, h, pad=max(r, r_bulb) + 3.0)
    org = np.asarray(g.origin, float)                           # the centre of voxel (0, 0, 0)
    i0 = np.maximum(np.floor((lo - org) / h).astype(int), 0)
    i1 = np.minimum(np.ceil((hi - org) / h).astype(int), np.array(solid.shape))
    solid = solid[i0[0]:i1[0], i0[1]:i1[1], i0[2]:i1[2]]
    org = org + i0 * h
    s_out = (ndi.distance_transform_edt(~solid) * h).astype(np.float32)
    s = s_out - (ndi.distance_transform_edt(solid) * h).astype(np.float32)   # signed distance: below 0 in the plastic
    xs = (org[0] + np.arange(solid.shape[0]) * h).astype(np.float32)[:, None, None]
    ys = (org[1] + np.arange(solid.shape[1]) * h).astype(np.float32)[None, :, None]
    zs = (org[2] + np.arange(solid.shape[2]) * h).astype(np.float32)[None, None, :]

    def along(p0, d):                                           # (X - p0) . d, as a field
        return (xs - p0[0]) * d[0] + (ys - p0[1]) * d[1] + (zs - p0[2]) * d[2]

    # ---- the radius field: the tail side, the bulb side, and near the holes
    c_tail = _closing(s_out, h, r)
    c_bulb = c_tail if abs(r_bulb - r) < 1e-9 else _closing(s_out, h, r_bulb)
    c_hole = _closing(s_out, h, r_hole) if r_hole > 0 else s
    side = _smooth(0.5 + P["tail_sign"] * (xs - o[0]) / 16.0)   # 0 on the bulb side of the window, 1 on the tail side
    c = side * c_tail + (1.0 - side) * c_bulb
    near = np.full(solid.shape, 1e9, np.float32)
    for row in z["holes"]:
        cen, ax, d = row[:3], row[3:6], row[6]
        t = along(cen, ax)
        rho2 = (xs - cen[0] - t * ax[0]) ** 2 + (ys - cen[1] - t * ax[1]) ** 2 + (zs - cen[2] - t * ax[2]) ** 2
        near = np.minimum(near, np.where(t > -2.0, np.sqrt(rho2) - 0.5 * d, 1e9))
    w = _smooth((near - 2.5) / 7.0)                             # 0 within 2.5 mm of a hole's rim, 1 from 9.5 mm on
    c = w * c + (1.0 - w) * c_hole
    # and nothing at all on a hole's rim: plastic there makes the hole deeper than the kernel sized it (the build
    # refuses that: 'hole L_ring: the solid volume changed by -199, expected -160', first build of s3-b8). The blend
    # leaves a round dimple around such a hole.
    rim = _smooth((near - 1.2) / 2.5)
    c = rim * c + (1.0 - rim) * s
    # ---- the keep-out of the window: nothing is added inside the 45 deg flare from its rim (with 1.5 mm to spare)
    from matplotlib.path import Path
    from scipy.spatial import cKDTree
    u, vv, zl = along(o, fx) + P["L"], along(o, fy), along(o, fz)
    poly = z["outline"]
    zone = (np.abs(u) < 60) & (np.abs(vv) < 60) & (zl > P["wall"] - 3.0) & (zl < P["wall"] + 40.0)
    rho_w = np.full(u.shape, 1e9, np.float32)
    flat = np.stack([u[zone], vv[zone]], axis=1)
    inside = Path(poly).contains_points(flat)
    dense = np.concatenate([poly + (np.roll(poly, -1, axis=0) - poly) * t for t in np.linspace(0, 1, 6, endpoint=False)])
    dist, _ = cKDTree(dense).query(flat)
    rho_w[zone] = np.where(inside, 0.0, dist)
    free = _smooth(((rho_w - 1.5) - (zl - P["wall"])) / 1.5)    # 1 where plastic may be added
    c = free * c + (1.0 - free) * s
    # At the faces of the box the ball has nothing to roll back against (the solid goes on outside the box), so the
    # closing leaves a slab of plastic there (first picture of s3-b8: a flange on the far edge of the body).
    # Nothing is added within one ball of a face of the box; the root of the neck is well inside it.
    edge = int(np.ceil((max(r, r_bulb) + 1.0) / h))
    core = np.zeros(solid.shape, bool)
    core[edge:-edge, edge:-edge, edge:-edge] = True
    c = np.where(core, c, s)
    c = np.minimum(c, s)                                        # a closing only adds
    # ---- the blob: the added plastic, with its feather edge sunk under the surface so that the join is clean
    added = (c < 0) & (s > 0)
    info = dict(voxel_mm=h, added_voxel_cm3=float(added.sum() * h ** 3 / 1000.0), radius_mm=r, radius_bulb_mm=r_bulb, radius_hole_mm=r_hole)
    if added.sum() < 50:
        np.savez_compressed(out_path, V=np.zeros((0, 3)), F=np.zeros((0, 3), np.int64), info=json.dumps(info))
        return
    thick = s - c
    b = c + 0.25 * np.clip(1.0 - thick / 0.6, 0.0, 1.0)
    dF = ndi.distance_transform_edt(~added) * h
    b = np.maximum(b, dF - 3.0)
    b = ndi.gaussian_filter(b, 0.8)
    b[[0, -1], :, :] = b[:, [0, -1], :] = b[:, :, [0, -1]] = 1.0
    V, F, _, _ = measure.marching_cubes(b, level=0.0, spacing=(h, h, h))
    V = V + org
    m = trimesh.Trimesh(V, F, process=True)
    parts = [p for p in m.split(only_watertight=True) if abs(p.volume) > 1.0]
    m = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]
    if m.volume < 0:
        m.invert()
    info.update(blob_cm3=float(m.volume / 1000.0), blob_triangles=int(len(m.faces)), pieces=len(parts),
                thickest_mm=float(thick[added].max()))
    np.savez_compressed(out_path, V=np.asarray(m.vertices, float), F=np.asarray(m.faces, np.int64), info=json.dumps(info))


if __name__ == "__main__":
    worker(sys.argv[1], sys.argv[2])
