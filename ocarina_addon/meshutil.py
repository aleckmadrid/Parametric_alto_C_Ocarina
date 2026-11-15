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
