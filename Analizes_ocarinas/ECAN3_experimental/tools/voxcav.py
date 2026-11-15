"""Voxel cavity extraction for 3D-printed vessel flutes (ocarinas).

Pipeline (all lengths in mm):
  1. voxelize_solid   - even-odd scanline fill of z-slices of a watertight mesh
  2. exterior_opening - air reachable from outside by a ball of radius R
                        (R larger than the biggest tone-hole radius, so the
                        ball cannot pass through a hole into the chamber)
  3. extract_cavity   - residual air (not reachable by the ball); channels
                        thinner than 2*cut_radius (the windway) are severed,
                        the largest component is kept, corners are restored
  4. internal_walls   - solid enclosed by the cavity (fins, partitions,
                        bosses), via a morphological closing of the cavity
  5. find_openings    - each hole / the window = a patch where the cavity
                        touches the ball-reachable exterior

The ball dips into each hole by delta = R - sqrt(R^2 - a^2), so the cavity is
capped slightly *below* the outer rim; cap_correction() gives that volume.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import trimesh
from scipy import ndimage as ndi
from skimage.draw import polygon as fill_polygon


@dataclass
class Grid:
    origin: np.ndarray      # (3,) world coordinate of the centre of voxel (0,0,0)
    h: float                # voxel edge, mm
    shape: tuple

    def world(self, idx):
        return self.origin + np.asarray(idx, float) * self.h

    def index(self, xyz):
        return np.round((np.asarray(xyz, float) - self.origin) / self.h).astype(int)

    @property
    def voxel_volume(self):
        return self.h ** 3


def load_main_body(path, rotate_z_deg=0.0, body_index=0):
    """Load an STL and keep the body_index-th largest body; optionally rotate about +z."""
    m = trimesh.load(path, force="mesh")
    bodies = sorted(m.split(only_watertight=False), key=lambda b: -abs(b.volume))
    body = bodies[body_index].copy()
    if rotate_z_deg:
        R = trimesh.transformations.rotation_matrix(math.radians(rotate_z_deg), [0, 0, 1])
        body.apply_transform(R)
    if body.volume < 0:
        body.invert()
    return body, bodies


def voxelize_solid(mesh: trimesh.Trimesh, h: float, pad: float):
    """Occupancy (True = solid) on a grid padded by `pad` mm of air on every side."""
    lo = mesh.bounds[0] - pad
    hi = mesh.bounds[1] + pad
    shape = tuple(int(math.ceil((hi[i] - lo[i]) / h)) + 1 for i in range(3))
    grid = Grid(origin=lo.copy(), h=h, shape=shape)
    solid = np.zeros(shape, dtype=bool)
    zs = lo[2] + np.arange(shape[2]) * h
    zmin, zmax = mesh.bounds[0][2], mesh.bounds[1][2]
    k_in = np.nonzero((zs > zmin) & (zs < zmax))[0]
    heights = zs[k_in] - zmin + 1e-6          # tiny offset: never slice exactly through vertices
    sections = mesh.section_multiplane(plane_origin=[0, 0, zmin], plane_normal=[0, 0, 1],
                                       heights=heights)
    plane = np.zeros(shape[:2], dtype=bool)
    for k, sec in zip(k_in, sections):
        if sec is None:
            continue
        T = sec.metadata.get("to_3D")
        plane[:] = False
        for ring in sec.discrete:
            if len(ring) < 3:
                continue
            pts = trimesh.transform_points(np.column_stack([ring, np.zeros(len(ring))]), T)[:, :2]
            r = (pts[:, 0] - lo[0]) / h
            c = (pts[:, 1] - lo[1]) / h
            rr, cc = fill_polygon(r, c, shape=shape[:2])
            plane[rr, cc] ^= True                  # even-odd rule
        solid[:, :, k] = plane
    return solid, grid


def edt_mm(mask, h):
    """Euclidean distance (mm) from every True voxel to the nearest False voxel."""
    return ndi.distance_transform_edt(mask, sampling=h).astype(np.float32)


def exterior_opening(solid, grid, R):
    """Air voxels covered by balls of radius R that fit in the air and connect to the outside."""
    air = ~solid
    D = edt_mm(air, grid.h)
    centres = D >= R
    del D
    lab, n = ndi.label(centres)
    faces = [lab[0], lab[-1], lab[:, 0], lab[:, -1], lab[:, :, 0], lab[:, :, -1]]
    border = np.unique(np.concatenate([f.ravel() for f in faces]))
    border = border[border > 0]
    outside_centres = np.isin(lab, border)
    del lab, centres
    Dc = edt_mm(~outside_centres, grid.h)
    return (Dc <= R + 1e-6) & air


def extract_cavity(solid, grid, ext, cut_radius=0.8):
    """Cavity = residual air of the main chamber, with sub-2*cut_radius channels severed.

    Channels thinner than 2*cut_radius (the windway, ~1.2 mm) are cut before
    the largest component is chosen. Corners lost to that small opening are
    restored by a geodesic dilation of cut_radius + h inside the residual air.
    """
    air = ~solid
    resid = air & ~ext
    D = edt_mm(resid, grid.h)
    core = D > cut_radius
    del D
    lab, n = ndi.label(core)
    if n == 0:
        raise RuntimeError("no cavity found")
    sizes = ndi.sum(core, lab, index=np.arange(1, n + 1))
    main = lab == (1 + int(np.argmax(sizes)))
    del lab, core
    Dm = edt_mm(~main, grid.h)
    cav = (Dm <= cut_radius + 1e-6) & resid
    del Dm
    steps = int(math.ceil(cut_radius / grid.h)) + 1
    st = ndi.generate_binary_structure(3, 1)
    for _ in range(steps):
        cav = ndi.binary_dilation(cav, st) & resid
    srt = np.sort(sizes)
    info = {"n_core_components": int(n),
            "main_core_mm3": float(srt[-1] * grid.voxel_volume),
            "second_core_mm3": float(srt[-2] * grid.voxel_volume) if n > 1 else 0.0}
    return cav, resid, info


def internal_walls(solid, cav, grid, r_close=2.5):
    """Solid enclosed by cavity (fins, partitions, bosses) = closing(cavity) minus cavity, in solid."""
    Dout = edt_mm(~cav, grid.h)
    dil = Dout <= r_close
    del Dout
    Din = edt_mm(dil, grid.h)
    closed = Din > r_close
    del Din, dil
    return closed & solid


@dataclass
class Opening:
    label: int
    n_vox: int
    centroid: np.ndarray
    normal: np.ndarray       # unit vector, cavity -> exterior
    area_mm2: float          # contact-patch area (curved ball cap; an upper bound of the hole area)
    info: dict = field(default_factory=dict)


def find_openings(cav, ext, grid, min_area=1.0):
    """Patches where the cavity touches the ball-reachable exterior (tone holes, window)."""
    st = ndi.generate_binary_structure(3, 1)
    touch = cav & ndi.binary_dilation(ext, st)
    lab, n = ndi.label(touch, structure=np.ones((3, 3, 3), bool))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        if sl is None:
            continue
        idx = np.argwhere(lab[sl] == i) + np.array([s.start for s in sl])
        area = len(idx) * grid.h ** 2
        if area < min_area:
            continue
        c = grid.world(idx).mean(0)
        lo = np.maximum(idx.min(0) - 8, 0)
        hi = np.minimum(idx.max(0) + 9, np.array(cav.shape))
        win = tuple(slice(a, b) for a, b in zip(lo, hi))
        e = np.argwhere(ext[win]) + lo
        cv = np.argwhere(cav[win]) + lo
        nrm = grid.world(e).mean(0) - grid.world(cv).mean(0) if len(e) and len(cv) else np.zeros(3)
        nn = np.linalg.norm(nrm)
        out.append(Opening(label=i, n_vox=len(idx), centroid=c,
                           normal=nrm / nn if nn > 0 else nrm, area_mm2=area))
    return out, lab


def _ring_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _point_in_ring(pt, p):
    from matplotlib.path import Path as MPath
    return MPath(p).contains_point(pt)


def measure_hole(mesh, centre, normal, crop=18.0, span=(-9.0, 9.0), dz=0.2, grow=1.6, refine=True):
    """Measure a tone hole (or the window) by slicing the mesh perpendicular to its axis.

    1. Crop the mesh to a sphere around the opening.
    2. Refine the axis: the bore wall normals all lie perpendicular to the
       axis, so the axis is the weakest eigenvector of their covariance.
    3. Slice every dz along the axis; at each offset take the smallest closed
       section ring that contains the axis point (the bore). The chimney is the
       contiguous run around the narrowest slice where area < grow * A_min.

    Returns dict: axis, centre, A_min (mm^2), d_eq (mm), t (mm, rim-to-rim
    along the axis), z_in/z_out (offsets of the inner/outer rim from `centre`),
    profile [(offset, area)], G_profile (mm) = 1 / integral(dz / A) over the run.
    """
    c = np.asarray(centre, float)
    axis = np.asarray(normal, float)
    axis /= np.linalg.norm(axis)
    vmask = np.linalg.norm(mesh.vertices - c, axis=1) < crop
    fmask = vmask[mesh.faces].any(axis=1)
    sub = mesh.submesh([np.nonzero(fmask)[0]], append=True)
    tc, fn, fa = sub.triangles_center, sub.face_normals, sub.area_faces

    def profile(ax, cc):
        rows = []
        for off in np.arange(span[0], span[1] + 1e-9, dz):
            o = cc + off * ax
            sec = sub.section(plane_origin=o, plane_normal=ax)
            if sec is None:
                rows.append((off, np.nan, None))
                continue
            planar, to3d = sec.to_2D() if hasattr(sec, "to_2D") else sec.to_planar()
            p2 = trimesh.transform_points(o[None, :], np.linalg.inv(to3d))[0, :2]
            best, best_ring = np.nan, None
            near, near_ring, near_d = np.nan, None, np.inf
            for ent in planar.entities:
                if not ent.closed:
                    continue
                ring = planar.vertices[ent.points]
                if len(ring) < 4:
                    continue
                a = _ring_area(ring)
                if (np.isnan(best) or a < best) and _point_in_ring(p2, ring):
                    best, best_ring = a, ring
                # fallback: a small ring whose centre is close to the axis point
                dc = np.linalg.norm(ring.mean(0) - p2)
                if a < 250.0 and dc < math.sqrt(a / math.pi) + 3.0 and dc < near_d:
                    near, near_ring, near_d = a, ring, dc
            rows.append((off, best, best_ring))
        return rows

    # axis refinement (3 passes), radius guess from a first coarse profile
    r_guess = 6.0
    for _ in range(3 if refine else 0):
        v = tc - c
        z = v @ axis
        rad = np.linalg.norm(v - np.outer(z, axis), axis=1)
        sel = (np.abs(z) < 6.0) & (rad < r_guess + 1.5) & (np.abs(fn @ axis) < 0.6)
        if sel.sum() < 12:
            break
        N = fn[sel]
        w = fa[sel]
        cov = (N * w[:, None]).T @ N
        evals, evecs = np.linalg.eigh(cov)
        a = evecs[:, 0]
        if a @ axis < 0:
            a = -a
        axis = a
        rows = profile(axis, c)
        areas = np.array([r[1] for r in rows])
        if np.all(np.isnan(areas)):
            break
        r_guess = math.sqrt(np.nanmin(areas) / math.pi)
        # recentre on the bore centroid at the narrowest slice
        k = int(np.nanargmin(areas))
        ring = rows[k][2]
        off = rows[k][0]
        o = c + off * axis
        sec = sub.section(plane_origin=o, plane_normal=axis)
        planar, to3d = sec.to_2D() if hasattr(sec, "to_2D") else sec.to_planar()
        cen2 = ring.mean(0)
        cen3 = trimesh.transform_points(np.array([[cen2[0], cen2[1], 0.0]]), to3d)[0]
        c = cen3 - off * axis          # keep offsets referenced to the same plane family

    rows = profile(axis, c)
    offs = np.array([r[0] for r in rows])
    areas = np.array([r[1] for r in rows])
    if np.all(np.isnan(areas)):
        return {"ok": False}
    k = int(np.nanargmin(areas))
    amin = areas[k]
    lo = hi = k
    while lo - 1 >= 0 and not np.isnan(areas[lo - 1]) and areas[lo - 1] < grow * amin:
        lo -= 1
    while hi + 1 < len(areas) and not np.isnan(areas[hi + 1]) and areas[hi + 1] < grow * amin:
        hi += 1
    run = areas[lo:hi + 1]
    t_closed = (hi - lo + 1) * dz
    d_eq = 2 * math.sqrt(amin / math.pi)
    # mean chimney length: rays parallel to the axis on a circle just outside the bore
    ring = rows[k][2]
    u = np.cross(axis, [0.0, 0.0, 1.0] if abs(axis[2]) < 0.9 else [1.0, 0.0, 0.0])
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    r_probe = d_eq / 2 + 0.35
    zmid = 0.5 * (offs[lo] + offs[hi])
    lengths, zin_l, zout_l = [], [], []
    for th in np.linspace(0, 2 * math.pi, 36, endpoint=False):
        o = c + r_probe * (math.cos(th) * u + math.sin(th) * v) + (zmid - 12.0) * axis
        locs, _, _ = sub.ray.intersects_location([o], [axis], multiple_hits=True)
        if len(locs) < 2:
            continue
        s = np.sort((locs - o) @ axis) + (zmid - 12.0)
        # pair hits into solid segments; keep the one that contains zmid
        for a_, b_ in zip(s[0::2], s[1::2]):
            if a_ - 0.05 <= zmid <= b_ + 0.05:
                lengths.append(b_ - a_)
                zin_l.append(a_)
                zout_l.append(b_)
                break
    t_mean = float(np.median(lengths)) if lengths else float("nan")
    return {"ok": True, "axis": axis, "centre": c, "A_min": float(amin), "d_eq": float(d_eq),
            "A_mean_closed": float(run.mean()), "t_closed": float(t_closed),
            "t": t_mean, "t_min": float(np.min(lengths)) if lengths else float("nan"),
            "t_max": float(np.max(lengths)) if lengths else float("nan"), "n_rays": len(lengths),
            "z_in": float(np.median(zin_l)) if zin_l else float(offs[lo]),
            "z_out": float(np.median(zout_l)) if zout_l else float(offs[hi]),
            "profile": [(float(o), float(a)) for o, a in zip(offs, areas)]}


def surface_axis(mesh, centre, n0, radius=8.0):
    """Local outer-surface normal around an opening (area-weighted face normals facing like n0)."""
    c = np.asarray(centre, float)
    n0 = np.asarray(n0, float) / np.linalg.norm(n0)
    tc = mesh.triangles_center
    sel = np.linalg.norm(tc - c, axis=1) < radius
    fn = mesh.face_normals[sel]
    fa = mesh.area_faces[sel]
    keep = fn @ n0 > 0.3
    if keep.sum() < 5:
        return n0
    a = (fn[keep] * fa[keep, None]).sum(0)
    return a / np.linalg.norm(a)


def measure_opening(mesh, centre, normal, is_window=False):
    """measure_hole with fallbacks: refined axis -> patch normal -> local surface normal."""
    tries = [dict(normal=normal, refine=not is_window), dict(normal=normal, refine=False),
             dict(normal=surface_axis(mesh, centre, normal), refine=False),
             dict(normal=surface_axis(mesh, centre, normal), refine=True)]
    last = {"ok": False}
    for i, kw in enumerate(tries):
        r = measure_hole(mesh, centre, kw["normal"], refine=kw["refine"])
        if r.get("ok") and not math.isnan(r.get("t", float("nan"))) and r.get("n_rays", 0) >= 6:
            r["method"] = ["refined", "patch normal", "surface normal", "surface normal refined"][i]
            return r
        if r.get("ok"):
            last = r
            last["method"] = "partial"
    return last


def cap_correction(R, d):
    """Volume (mm^3) of the spherical cap that a ball of radius R dips into a hole of diameter d."""
    a = d / 2.0
    if a >= R:
        return float("nan")
    delta = R - math.sqrt(R * R - a * a)
    return math.pi * delta * delta * (3 * R - delta) / 3.0
