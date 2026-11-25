"""Mesh helpers: arrays, volume, manifold report, Booleans with assertions. Uses numpy and bpy.

All lengths are millimetres (1 Blender unit = 1 mm). A mesh here is a triangle mesh given as
(V, F): V is an (n, 3) float64 array of vertices and F an (m, 3) int array of triangles with outward
normals (counter-clockwise seen from outside).
"""
from __future__ import annotations

import math

import numpy as np

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


class GeometryError(RuntimeError):
    """A Boolean or a mesh check failed. The message says what was measured."""


# ------------------------------------------------------------------ arrays <-> Blender meshes

def arrays_from_mesh(mesh):
    """(V, F) of a Blender mesh. Polygons with more than 3 corners are triangulated by Blender's rule."""
    n = len(mesh.vertices)
    V = np.empty(n * 3, dtype=np.float64)
    mesh.vertices.foreach_get("co", V)
    V = V.reshape(n, 3)
    mesh.calc_loop_triangles()
    m = len(mesh.loop_triangles)
    F = np.empty(m * 3, dtype=np.int32)
    mesh.loop_triangles.foreach_get("vertices", F)
    return V, F.reshape(m, 3).astype(np.int64)


def mesh_from_arrays(name: str, V, F):
    mesh = bpy.data.meshes.new(name)
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int64)
    mesh.vertices.add(len(V))
    mesh.vertices.foreach_set("co", V.astype(np.float32).ravel())
    mesh.loops.add(F.size)
    mesh.loops.foreach_set("vertex_index", F.astype(np.int32).ravel())
    mesh.polygons.add(len(F))
    mesh.polygons.foreach_set("loop_start", np.arange(0, F.size, 3, dtype=np.int32))
    mesh.polygons.foreach_set("loop_total", np.full(len(F), 3, dtype=np.int32))
    mesh.update(calc_edges=True)
    mesh.validate(verbose=False)
    return mesh


def object_from_arrays(name: str, V, F, collection=None):
    obj = bpy.data.objects.new(name, mesh_from_arrays(name, V, F))
    (collection or bpy.context.scene.collection).objects.link(obj)
    return obj


def evaluated_arrays(obj):
    """(V, F) of an object with its modifiers applied, in world coordinates."""
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    ev = obj.evaluated_get(dg)
    mesh = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
    V, F = arrays_from_mesh(mesh)
    M = np.array(obj.matrix_world, dtype=np.float64)
    V = V @ M[:3, :3].T + M[:3, 3]
    attrs = {}
    for name in ("oca_scale",):
        a = mesh.attributes.get(name)
        if a is not None and len(a.data):
            attrs[name] = float(a.data[0].value)
    bpy.data.meshes.remove(mesh)
    return V, F, attrs


# ------------------------------------------------------------------ measures

def volume(V, F) -> float:
    """Signed volume (mm^3): sum of v0 . (v1 x v2) / 6. Positive for outward normals."""
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def area(V, F) -> float:
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    return float(np.linalg.norm(np.cross(b - a, c - a), axis=1).sum() / 2.0)


def face_normals(V, F):
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(b - a, c - a)
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    return n / ln[:, None]


def manifold_report(V, F, zero_edge_mm: float = 1e-6) -> dict:
    """Topology facts of a triangle mesh.

    manifold            every edge is used by exactly two triangles, in opposite directions
    boundary_edges      edges used by one triangle (holes in the surface)
    nonmanifold_edges   edges used by three or more triangles
    inconsistent_edges  edges whose two triangles run the same way (flipped normals)
    zero_length_edges   edges shorter than zero_edge_mm
    degenerate_faces    triangles with (almost) no area
    shells              number of connected surfaces
    """
    e = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    lo, hi = np.minimum(e[:, 0], e[:, 1]), np.maximum(e[:, 0], e[:, 1])
    key = lo * (int(V.shape[0]) + 1) + hi
    direction = np.where(e[:, 0] < e[:, 1], 1, -1)
    order = np.argsort(key, kind="stable")
    key_s, dir_s = key[order], direction[order]
    uniq, start, count = np.unique(key_s, return_index=True, return_counts=True)
    dsum = np.add.reduceat(dir_s, start)
    boundary = int((count == 1).sum())
    nonman = int((count > 2).sum())
    incons = int(((count == 2) & (dsum != 0)).sum())
    elen = np.linalg.norm(V[e[:, 0]] - V[e[:, 1]], axis=1)
    zero = int((elen < zero_edge_mm).sum() // 2)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    dbl = np.linalg.norm(np.cross(b - a, c - a), axis=1)
    degenerate = int((dbl < 1e-10).sum())
    # shells: union-find over vertices
    parent = np.arange(V.shape[0])

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a_, b_ in zip(lo[order][start], hi[order][start]):
        ra, rb = find(int(a_)), find(int(b_))
        if ra != rb:
            parent[ra] = rb
    used = np.unique(F)
    shells = len({find(int(i)) for i in used})
    return dict(vertices=int(V.shape[0]), triangles=int(F.shape[0]), boundary_edges=boundary,
                nonmanifold_edges=nonman, inconsistent_edges=incons, zero_length_edges=zero,
                degenerate_faces=degenerate, shells=shells, unused_vertices=int(V.shape[0] - len(used)),
                manifold=(boundary == 0 and nonman == 0 and incons == 0))


def shell_volumes(V, F) -> list:
    """Signed volume of each connected surface, largest magnitude first."""
    parent = np.arange(V.shape[0])

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for tri in F:
        r0 = find(int(tri[0]))
        for j in (1, 2):
            r = find(int(tri[j]))
            if r != r0:
                parent[r] = r0
    roots = np.array([find(int(t[0])) for t in F])
    out = []
    for r in np.unique(roots):
        out.append(volume(V, F[roots == r]))
    return sorted(out, key=lambda x: -abs(x))


def self_intersections(V, F, eps: float = 1e-7) -> int:
    """Number of triangle pairs that overlap and share no vertex (BVH overlap of the mesh with itself)."""
    tree = BVHTree.FromPolygons([Vector(v) for v in V], [tuple(int(i) for i in f) for f in F], epsilon=0.0)
    count = 0
    for i, j in tree.overlap(tree):
        if i >= j:
            continue
        if set(F[i]) & set(F[j]):
            continue
        if _tri_tri_intersect(V[F[i]], V[F[j]], eps):
            count += 1
    return count


def _tri_tri_intersect(t1, t2, eps):
    """True if two triangles (3x3 arrays) properly intersect (an edge of one crosses the inside of the other)."""
    for a, b in ((t1, t2), (t2, t1)):
        n = np.cross(b[1] - b[0], b[2] - b[0])
        ln = np.linalg.norm(n)
        if ln < 1e-14:
            continue
        n = n / ln
        for k in range(3):
            p, q = a[k], a[(k + 1) % 3]
            dp, dq = np.dot(p - b[0], n), np.dot(q - b[0], n)
            if (dp > eps and dq > eps) or (dp < -eps and dq < -eps) or abs(dp - dq) < 1e-14:
                continue
            if abs(dp) <= eps or abs(dq) <= eps:
                continue                      # an end point lies in the plane: touching, not crossing
            x = p + (q - p) * (dp / (dp - dq))
            inside = True
            for m in range(3):
                e0, e1 = b[m], b[(m + 1) % 3]
                if np.dot(np.cross(e1 - e0, x - e0), n) < eps:
                    inside = False
                    break
            if inside:
                return True
    return False


def bvh(V, F):
    return BVHTree.FromPolygons([Vector(v) for v in V], [tuple(int(i) for i in f) for f in F], epsilon=0.0)



# ------------------------------------------------------------------ rays, vertex normals, column integration

def vertex_normals(V, F):
    """Area-weighted unit normals at the vertices."""
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    fn = np.cross(b - a, c - a)
    n = np.zeros_like(V)
    for k in range(3):
        np.add.at(n, F[:, k], fn)
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    return n / ln[:, None]


def ray_hits(tree, origin, direction, max_dist: float = 1e3, eps: float = 1e-3, limit: int = 64):
    """All hits of a ray with a BVH tree, as sorted (distance from `origin`, hit normal, triangle index).

    Blender's BVH works in single precision, so keep the origin within a few hundred millimetres of the
    mesh. After each hit the ray is restarted `eps` further on; a second hit on the same triangle within
    2 * eps is dropped.
    """
    o = Vector(origin)
    d = Vector(direction).normalized()
    out = []
    travelled = 0.0
    last = -1
    for _ in range(limit):
        loc, nrm, idx, dist = tree.ray_cast(o, d, max_dist - travelled)
        if loc is None:
            break
        travelled += dist
        if not (idx == last and dist < 2.0 * eps):
            out.append((travelled, tuple(nrm), idx))
        last = idx
        o = loc + d * eps
        travelled += eps
    return out


def inside(tree, point, direction=(0.371, 0.557, 0.743)) -> bool:
    """True if the point is inside the closed mesh of the BVH tree (odd number of crossings)."""
    return len(ray_hits(tree, point, direction)) % 2 == 1


def column_hits(V, F, origin, x, y, z, bbox, nx: int, ny: int):
    """Exact crossings of a grid of columns (lines parallel to `z`) with a triangle mesh, in double precision.

    Returns a dict {(i, j): [(height, sign), ...]} for the columns that are crossed. sign is +1 where the
    column ENTERS the solid going up (the face normal points down) and -1 where it leaves. The column
    positions are shifted by irrational fractions of a cell, so that a column never runs through a mesh
    edge of geometry that was built at round coordinates.
    """
    o = np.asarray(origin, float)
    R = np.stack([np.asarray(x, float), np.asarray(y, float), np.asarray(z, float)], axis=1)
    P = (np.asarray(V, float) - o) @ R                      # coordinates in the frame
    x0, x1, y0, y1 = bbox
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    fx, fy = 0.371390676, 0.618033989
    T = P[F]                                               # (m, 3, 3)
    tmin, tmax = T[:, :, :2].min(axis=1), T[:, :, :2].max(axis=1)
    sel = np.nonzero((tmax[:, 0] >= x0) & (tmin[:, 0] <= x1) & (tmax[:, 1] >= y0) & (tmin[:, 1] <= y1))[0]
    hits = {}
    for t in sel:
        a, b, c = T[t]
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-14:
            continue                                       # the triangle is parallel to the columns
        sign = -1.0 if den > 0 else 1.0                    # den > 0: counter-clockwise from above = normal up = leaving
        i0 = max(0, int(math.floor((tmin[t, 0] - x0) / dx - fx)))
        i1 = min(nx - 1, int(math.ceil((tmax[t, 0] - x0) / dx - fx)))
        j0 = max(0, int(math.floor((tmin[t, 1] - y0) / dy - fy)))
        j1 = min(ny - 1, int(math.ceil((tmax[t, 1] - y0) / dy - fy)))
        for i in range(i0, i1 + 1):
            px = x0 + (i + fx) * dx
            for j in range(j0, j1 + 1):
                py = y0 + (j + fy) * dy
                w0 = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) / den
                w1 = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / den
                w2 = 1.0 - w0 - w1
                if w0 < 0.0 or w1 < 0.0 or w2 < 0.0:
                    continue
                hits.setdefault((i, j), []).append((w0 * a[2] + w1 * b[2] + w2 * c[2], sign))
    return hits, dx, dy


def _inside_intervals(col):
    """Height intervals where a column is inside the solid, from its crossings (a depth counter)."""
    out, depth, start = [], 0, 0.0
    for h, sg in sorted(col):
        if sg > 0:
            if depth == 0:
                start = h
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append((start, h))
            depth = max(depth, 0)
    return out


def column_volume(include, exclude, origin, x, y, z, bbox, step: float = 0.25) -> float:
    """Volume of the set (inside every mesh of `include`) and (outside every mesh of `exclude`), by column
    integration over bbox = (x0, x1, y0, y1) in the frame. No Boolean is used, so meshes that share
    surfaces are not a problem. This is how the capped air is measured from the final body mesh."""
    x0, x1, y0, y1 = bbox
    nx, ny = max(1, int(round((x1 - x0) / step))), max(1, int(round((y1 - y0) / step)))
    inc = [column_hits(*m, origin, x, y, z, bbox, nx, ny) for m in include]
    exc = [column_hits(*m, origin, x, y, z, bbox, nx, ny)[0] for m in exclude]
    dx, dy = inc[0][1], inc[0][2]
    total = 0.0
    for key, col in inc[0][0].items():
        segs = _inside_intervals(col)
        for other, _, _ in inc[1:]:
            oi = _inside_intervals(other.get(key, []))
            segs = [(max(a0, b0), min(a1, b1)) for a0, a1 in segs for b0, b1 in oi if min(a1, b1) > max(a0, b0)]
        for ex in exc:
            for b0, b1 in _inside_intervals(ex.get(key, [])):
                nxt = []
                for a0, a1 in segs:
                    if b1 <= a0 or b0 >= a1:
                        nxt.append((a0, a1))
                    else:
                        if b0 > a0:
                            nxt.append((a0, b0))
                        if b1 < a1:
                            nxt.append((b1, a1))
                segs = nxt
        total += sum(a1 - a0 for a0, a1 in segs)
    return total * dx * dy


def intersection_volume_columns(mesh_a, mesh_b, origin, x, y, z, bbox, step: float = 0.2) -> float:
    """Volume of (A intersect B) by integrating along columns: an estimate that does not use a Boolean.

    A grid of columns parallel to `z` covers bbox = (x0, x1, y0, y1) in the frame (origin, x, y, z). On each
    column the lengths that are inside both meshes are added up. It is used to say what a cut should remove,
    so the Boolean is checked against an independent number.
    """
    x0, x1, y0, y1 = bbox
    nx, ny = max(1, int(round((x1 - x0) / step))), max(1, int(round((y1 - y0) / step)))
    hb, dx, dy = column_hits(*mesh_b, origin, x, y, z, bbox, nx, ny)
    ha, _, _ = column_hits(*mesh_a, origin, x, y, z, bbox, nx, ny)
    total = 0.0
    for key, colb in hb.items():
        cola = ha.get(key)
        if not cola:
            continue
        ia = _inside_intervals(cola)
        for b0, b1 in _inside_intervals(colb):
            for a0, a1 in ia:
                lo, hi = max(a0, b0), min(a1, b1)
                if hi > lo:
                    total += hi - lo
    return total * dx * dy


# ------------------------------------------------------------------ primitives (closed, outward normals)

def prism_from_rings(rings):
    """Closed mesh from a stack of rings. Each ring is an (n, 3) array of points, counter-clockwise seen
    from the side the LAST ring faces. Side walls are quads split into triangles; both ends are closed
    with a fan from the ring centre. Returns (V, F)."""
    rings = [np.asarray(r, dtype=np.float64) for r in rings]
    n = rings[0].shape[0]
    if any(r.shape[0] != n for r in rings):
        raise ValueError("all rings need the same number of points")
    V = [r for r in rings]
    F = []
    for k in range(len(rings) - 1):
        a0, b0 = k * n, (k + 1) * n
        for i in range(n):
            j = (i + 1) % n
            F.append((a0 + i, a0 + j, b0 + j))
            F.append((a0 + i, b0 + j, b0 + i))
    base = len(rings) * n
    V.append(rings[0].mean(axis=0)[None, :])          # centre of the first ring
    V.append(rings[-1].mean(axis=0)[None, :])         # centre of the last ring
    c0, c1 = base, base + 1
    last = (len(rings) - 1) * n
    for i in range(n):
        j = (i + 1) % n
        F.append((c0, j, i))                          # first cap faces away from the stack
        F.append((c1, last + i, last + j))
    return np.concatenate(V), np.array(F, dtype=np.int64)


def frame_points(points_local, origin, x, y, z):
    """Local (x, y, z) coordinates -> body coordinates, for an orthonormal frame."""
    P = np.asarray(points_local, dtype=np.float64)
    R = np.stack([np.asarray(x, float), np.asarray(y, float), np.asarray(z, float)], axis=1)   # columns
    return P @ R.T + np.asarray(origin, dtype=np.float64)


def cylinder(origin, axis, radius: float, z0: float, z1: float, segments: int = 64, area_true: bool = True):
    """Closed cylinder along `axis` through `origin`, from z0 to z1 (z1 > z0) on the axis.

    area_true: the polygon has the same AREA as the circle (the circumradius is made a little larger),
    so that a cut made with it has the conductance of the round hole. See ocarina_kernel.polygon_circumradius_for_area.
    """
    axis = np.asarray(axis, dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    helper = np.array([1.0, 0.0, 0.0]) if abs(axis[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(axis, helper)
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    r = radius * math.sqrt(2.0 * math.pi / (segments * math.sin(2.0 * math.pi / segments))) if area_true else radius
    ang = np.arange(segments) * (2.0 * math.pi / segments)
    circle = r * (np.cos(ang)[:, None] * u + np.sin(ang)[:, None] * v)
    o = np.asarray(origin, dtype=np.float64)
    return prism_from_rings([o + axis * z0 + circle, o + axis * z1 + circle])


def box_local(x0, x1, y0, y1, z0, z1):
    """Closed box in local coordinates. Returns (V, F)."""
    lo = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=np.float64)
    r0 = np.column_stack([lo, np.full(4, z0)])
    r1 = np.column_stack([lo, np.full(4, z1)])
    return prism_from_rings([r0, r1])


# ------------------------------------------------------------------ Booleans

_SOLVERS = ("MANIFOLD", "EXACT")


def boolean(a, b, operation: str, solver: str | None = None):
    """Boolean of two closed meshes given as (V, F). operation: "UNION", "DIFFERENCE" or "INTERSECT".

    Uses Blender's Manifold solver; if the result is not manifold (or Blender rejects the input), the
    Exact solver is tried. Returns (V, F, solver used). Raises GeometryError if no solver gives a
    manifold result.
    """
    last = None
    for s in ((solver,) if solver else _SOLVERS):
        try:
            V, F = _boolean_once(a, b, operation, s)
        except Exception as exc:                 # noqa: BLE001 - Blender raises RuntimeError variants
            last = f"{s}: {exc}"
            continue
        if len(F) == 0:
            if operation == "INTERSECT":
                return V, F, s
            last = f"{s}: empty result"
            continue
        rep = manifold_report(V, F)
        if rep["manifold"]:
            return V, F, s
        last = (f"{s}: result not manifold ({rep['boundary_edges']} boundary, {rep['nonmanifold_edges']} non-manifold, "
                f"{rep['inconsistent_edges']} inconsistent edges)")
    raise GeometryError(f"Boolean {operation} failed. {last}")


def _boolean_once(a, b, operation, solver):
    oa = object_from_arrays("_oca_bool_a", *a)
    ob = object_from_arrays("_oca_bool_b", *b)
    try:
        mod = oa.modifiers.new("bool", "BOOLEAN")
        mod.operation = operation
        mod.solver = solver
        mod.object = ob
        if solver == "EXACT":
            mod.use_self = False
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        mesh = bpy.data.meshes.new_from_object(oa.evaluated_get(dg), depsgraph=dg)
        V, F = arrays_from_mesh(mesh)
        bpy.data.meshes.remove(mesh)
        V, F = _weld(V, F)
        return V, F
    finally:
        for o in (oa, ob):
            m = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.meshes.remove(m)


def _weld(V, F, tol: float = 1e-7):
    """Merge vertices that coincide within tol and drop triangles that collapse. Booleans can leave such pairs."""
    if len(V) == 0:
        return V, F
    q = np.round(V / tol).astype(np.int64)
    _, first, inverse = np.unique(q, axis=0, return_index=True, return_inverse=True)
    inverse = inverse.reshape(-1)
    if len(first) == len(V):
        return V, F
    F2 = inverse[F]
    keep = (F2[:, 0] != F2[:, 1]) & (F2[:, 1] != F2[:, 2]) & (F2[:, 0] != F2[:, 2])
    return V[first], F2[keep]


class BooleanLog:
    """Runs Booleans on a working solid and records the volume change of each one against an expected value."""

    def __init__(self):
        self.steps = []

    def apply(self, name: str, solid, tool, operation: str, expected_delta_mm3: float | None = None,
              tol_rel: float = 0.02, tol_abs_mm3: float = 1.0, bounds=None):
        """Apply `tool` to `solid`. The volume change of the SOLID is compared with expected_delta_mm3
        (negative for a cut) within tol_rel * |expected| + tol_abs. `bounds` = (lo, hi) is used instead when
        no exact expectation exists. Raises GeometryError when the result is not manifold or the change is
        outside the tolerance."""
        v0 = volume(*solid)
        V, F, solver = boolean(solid, tool, operation)
        v1 = volume(V, F)
        delta = v1 - v0
        rep = manifold_report(V, F)
        ok = True
        why = ""
        if expected_delta_mm3 is not None:
            tol = tol_rel * abs(expected_delta_mm3) + tol_abs_mm3
            ok = abs(delta - expected_delta_mm3) <= tol
            why = f"expected {expected_delta_mm3:+.2f} ± {tol:.2f} mm³"
        elif bounds is not None:
            ok = bounds[0] <= delta <= bounds[1]
            why = f"expected between {bounds[0]:+.2f} and {bounds[1]:+.2f} mm³"
        step = dict(name=name, operation=operation, solver=solver, volume_before_mm3=v0, volume_after_mm3=v1,
                    delta_mm3=delta, expected_mm3=expected_delta_mm3, bounds=bounds, ok=bool(ok),
                    manifold=rep["manifold"], shells=rep["shells"], triangles=rep["triangles"])
        self.steps.append(step)
        if not rep["manifold"]:
            raise GeometryError(f"Boolean '{name}': the result is not manifold")
        if not ok:
            raise GeometryError(f"Boolean '{name}': the solid volume changed by {delta:+.2f} mm³; {why}")
        return V, F


# ------------------------------------------------------------------ cleanup after Booleans

def _cleanup_once(V, F, merge_mm: float, degenerate_mm: float, needle_rounds: int = 3, needle_height_mm: float = 0.0):
    mesh = mesh_from_arrays("_oca_clean", V, F)
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=merge_mm)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=degenerate_mm)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        # A needle triangle (three points almost on one line, with long edges) is not removed by the steps
        # above. Its longest edge is flipped: the needle and its neighbour become two proper triangles.
        for _ in range(needle_rounds):
            needles = [f for f in bm.faces if f.calc_area() < 1e-9 or
                       (needle_height_mm and 2.0 * f.calc_area() < needle_height_mm * max(ed.calc_length() for ed in f.edges))]
            if not needles:
                break
            edges = []
            for f in needles:
                e = max(f.edges, key=lambda ed: ed.calc_length())
                # flip only against a proper neighbour: two needles on one line would only swap places
                if e.is_manifold and e not in edges and all(g is f or g.calc_area() > 1e-6 for g in e.link_faces):
                    edges.append(e)
            if not edges:
                break
            bmesh.ops.rotate_edges(bm, edges=edges, use_ccw=False)
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        bm.to_mesh(mesh)
        return arrays_from_mesh(mesh)
    finally:
        bm.free()
        bpy.data.meshes.remove(mesh)


NEEDLE_HEIGHT_MM = 1e-6        # a triangle lower than this over its longest edge is a needle (a nanometre)
SINGLE_PRECISION_STEP_MM = 2e-5    # just above the spacing of single-precision numbers at the size of a body (1.5e-5 mm at 150 mm)


def repair_collinear_rows(V, F, height_mm: float = NEEDLE_HEIGHT_MM, line_tol_mm: float = 1e-5):
    """Remove rows of needle triangles: several points on one straight line, joined by triangles of (almost) no area.

    Such a row is clean in double precision and collapses to zero-area triangles once the STL file stores single
    precision (seen 2026-11-17 on the line where the side wall of the window meets the ceiling of the pocket, with
    the windway floor 0.2 mm below that ceiling). An edge flip cannot remove it: the neighbours across the long
    edges are needles too.

    The needles of one row are deleted. Every proper triangle that borders the row has one edge on the line; that
    edge is split at each point of the row that lies inside it (a fan from the opposite corner). No vertex moves,
    so the surface and the volume do not change. A row that is not a simple line (points off the line, or a
    proper triangle that touches it with two edges) is left alone. Returns (V, F, number of needles removed).
    """
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int64)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    dbl = np.linalg.norm(np.cross(b - a, c - a), axis=1)
    longest = np.maximum.reduce([np.linalg.norm(b - a, axis=1), np.linalg.norm(c - b, axis=1), np.linalg.norm(a - c, axis=1)])
    needle = dbl < height_mm * np.maximum(longest, 1e-12)
    ids = np.where(needle)[0]
    if len(ids) == 0:
        return V, F, 0
    edge_faces = {}
    for fi, tri in enumerate(F):
        for j in range(3):
            edge_faces.setdefault(tuple(sorted((int(tri[j]), int(tri[(j + 1) % 3])))), []).append(fi)
    parent = {int(i): int(i) for i in ids}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for fi in ids:
        tri = F[fi]
        for j in range(3):
            for other in edge_faces[tuple(sorted((int(tri[j]), int(tri[(j + 1) % 3]))))]:
                if other != fi and needle[other]:
                    parent[find(int(fi))] = find(int(other))
    rows = {}
    for fi in ids:
        rows.setdefault(find(int(fi)), []).append(int(fi))

    drop, replace = set(), {}
    for members in rows.values():
        verts = sorted({int(x) for fi in members for x in F[fi]})
        P = V[verts]
        i0 = int(np.argmax(np.linalg.norm(P - P[0], axis=1)))
        i1 = int(np.argmax(np.linalg.norm(P - P[i0], axis=1)))
        d = P[i1] - P[i0]
        length = float(np.linalg.norm(d))
        if length < 1e-9:
            continue
        d /= length
        t = (P - P[i0]) @ d
        if float(np.linalg.norm((P - P[i0]) - np.outer(t, d), axis=1).max()) > line_tol_mm:
            continue                                   # not a straight row
        tv = dict(zip(verts, t.tolist()))
        plan, ok, seen = {}, True, set()
        for fi in members:
            tri = F[fi]
            for j in range(3):
                va, vb = int(tri[j]), int(tri[(j + 1) % 3])
                others = [g for g in edge_faces[tuple(sorted((va, vb)))] if g != fi]
                if len(others) != 1:
                    ok = False
                    continue
                g = others[0]
                if needle[g]:
                    continue                           # an inner edge of the row
                if g in seen or g in replace:
                    ok = False                         # a proper triangle with two edges on the row
                    continue
                seen.add(g)
                lo, hi = sorted((tv[va], tv[vb]))
                between = [v for v in verts if lo + 1e-12 < tv[v] < hi - 1e-12]
                if not between:
                    continue
                gt = [int(x) for x in F[g]]
                k = next(k for k in range(3) if {gt[k], gt[(k + 1) % 3]} == {va, vb})
                p, q, apex = gt[k], gt[(k + 1) % 3], gt[(k + 2) % 3]
                chain = [p] + sorted(between, key=lambda v: tv[v], reverse=tv[p] > tv[q]) + [q]
                plan[g] = [(chain[n], chain[n + 1], apex) for n in range(len(chain) - 1)]
        if not ok:
            continue
        drop.update(members)
        replace.update(plan)
    if not drop:
        return V, F, 0
    keep = [tri for fi, tri in enumerate(F.tolist()) if fi not in drop and fi not in replace]
    for fan in replace.values():
        keep.extend(fan)
    F2 = np.asarray(keep, dtype=np.int64)
    used = np.unique(F2)
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    return V[used], remap[F2], len(drop)


def cleanup(V, F, merge_mm: float = 1e-3, volume_tol_mm3: float = 0.05, no_self_intersection: bool = False):
    """_cleanup_core (see there), then repair_collinear_rows on the single-precision result. The repair is kept
    only if the mesh is still manifold, its volume did not move and it has fewer needles than before; a mesh
    without a needle row comes back exactly as _cleanup_core made it."""
    V1, F1 = _cleanup_core(V, F, merge_mm, volume_tol_mm3, no_self_intersection)
    V32 = np.asarray(V1, dtype=np.float32).astype(np.float64)
    for _ in range(4):
        V2, F2, removed = repair_collinear_rows(V32, F1)
        if not removed:
            break
        rep = manifold_report(V2, F2)
        if not rep["manifold"] or abs(volume(V2, F2) - volume(V32, F1)) > volume_tol_mm3:
            break
        if no_self_intersection and self_intersections(V2, F2) > self_intersections(V32, F1):
            break
        V1, V32, F1 = V2, V2, F2
    if no_self_intersection and self_intersections(V32, F1) > 0:
        # Still a pair of triangles that count as crossing. One cause is a needle a little HIGHER than NEEDLE_HEIGHT_MM:
        # a point on the edge of a large triangle, off it by a few millionths of a millimetre, which is the spacing
        # of single-precision numbers at these sizes (4e-6 mm at 40 mm, 1.5e-5 mm at 150 mm). The neighbours of such a
        # needle touch along the line and the crossing test tells them apart only by rounding (seen 2026-11-19 at the
        # mouth end of the neck, where the pipe's roof meets the end face). The same repair, with the needle height
        # set to that spacing, removes it. It is kept only if it leaves fewer crossings; this path is reached only by
        # a mesh that would otherwise fail the topology check.
        before = self_intersections(V32, F1)
        for _ in range(4):
            V2, F2, removed = repair_collinear_rows(V32, F1, height_mm=SINGLE_PRECISION_STEP_MM, line_tol_mm=SINGLE_PRECISION_STEP_MM)
            if not removed:
                break
            rep = manifold_report(V2, F2)
            after = self_intersections(V2, F2)
            if not rep["manifold"] or abs(volume(V2, F2) - volume(V32, F1)) > volume_tol_mm3 or after >= before:
                break
            V1, V32, F1, before = V2, V2, F2, after
            if after == 0:
                break
    return V1, F1


def _cleanup_core(V, F, merge_mm: float = 1e-3, volume_tol_mm3: float = 0.05, no_self_intersection: bool = False):
    """Weld vertices closer than merge_mm and dissolve degenerate triangles (bmesh), then triangulate.

    Booleans can leave slivers: edges of almost no length and triangles of almost no area. They are far
    below anything a printer or a slicer sees, but they break the "no zero-length edge" rule and can count
    as self-intersections. The voicing and the chimneys are not smoothed or remeshed: only coincident
    points are merged. The result holds single-precision coordinates, exactly as an STL file stores them.

    Several merge distances are tried, from the given one (1 micrometre) up to ten times that. A result is
    accepted only if it is manifold and its volume did not move. The first accepted result without any
    zero-length edge or zero-area triangle wins; if none is that clean, the cleanest accepted result is
    returned (the topology check then reports it).

    no_self_intersection: a result with overlapping triangles is not counted as clean either (the body solid).
    """
    v0 = volume(V, F)
    best, best_score = None, None

    def score_of(cand, rep):
        n = rep["zero_length_edges"] + rep["degenerate_faces"]
        return n + self_intersections(*cand) if no_self_intersection and n == 0 else n
    for scale in (1.0, 2.0, 5.0, 10.0, 0.3, 0.1):
        m = merge_mm * scale
        cand = _cleanup_once(V, F, m, 0.1 * m)
        cand = _cleanup_once(*cand, m, 0.1 * m)              # a second pass removes what the first pass exposed
        rep = manifold_report(*cand)
        if not rep["manifold"] or abs(volume(*cand) - v0) > volume_tol_mm3:
            continue
        score = score_of(cand, rep)
        if score == 0:
            return cand
        if best is None or score < best_score:
            best, best_score = cand, score
    if best is not None:
        # Not clean at any merge distance. A row of needles on one line needs more rounds of edge flips than the
        # three above, and a needle of 1e-9 to 1e-8 mm2 is missed by the area rule; such needles sit on the line
        # where the side wall of a lowered windway meets the ceiling under the window (seen 2026-11-17). Here a
        # needle is any triangle lower than a nanometre over its longest edge. This path is reached only by a mesh
        # that would otherwise fail the topology check, so the meshes that were clean before are not touched.
        for scale in (1.0, 2.0, 5.0):
            m = merge_mm * scale
            cand = _cleanup_once(*best, m, 0.1 * m, needle_rounds=12, needle_height_mm=1e-6)
            rep = manifold_report(*cand)
            if not rep["manifold"] or abs(volume(*cand) - v0) > volume_tol_mm3:
                continue
            score = score_of(cand, rep)
            if score < best_score:
                best, best_score = cand, score
            if best_score == 0:
                break
        return best
    return _weld(np.asarray(V, dtype=np.float32).astype(np.float64), F)
