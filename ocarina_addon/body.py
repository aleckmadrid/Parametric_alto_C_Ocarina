"""Builds one full test body: cavity, wall, voicing, holes. Every number comes from the kernel.

Order of work (the "wall stack" and the Booleans)

    1  sizing            kernel: voicing record, hole diameters (first prints: the "print" set, k_hole 0.8),
                         tubes, the target volume of the cavity mesh
    2  cavity            Geometry Nodes loft, scaled about the voicing port. The scale is solved so that
                         (loft joined with the voicing pocket) has the kernel's cavity_volume_for_mesh_cm3
    3  skin              the cavity surface moved outward by the wall thickness (uniform 4 mm)
    4  envelope          skin joined with the voicing block (mouthpiece stub and flat window face)
                         [hook: a user outer mesh would be joined here, see OUTER_MESH_HOOK]
    5  shell             envelope minus (cavity joined with the pocket)
    6  tubes             each inward tube is joined (a cylinder from the wall into the cavity)
    7  holes             each hole is cut along the cavity normal, through wall and tube
    8  window, windway   the window throat with the labium ramp is cut, then the windway

After every Boolean the result must be manifold, and the volume of the solid must change by the
expected amount (meshutil.BooleanLog). The invariant at the end is that the CAPPED AIR equals the
kernel's V0: every hole capped at the outer skin, the window capped at the inner plane.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

import numpy as np

from . import cavity as cavity_mod
from . import cavity_math, export, holes_layout, kernel_bridge, meshutil, presets as presets_mod, voicing_geo

HOLE_SEGMENTS_DEFAULT = 64
TUBE_ROOT_MM = 2.0             # an inward tube starts this far inside the wall, so that it joins the wall cleanly
HOLE_CUT_OUTSIDE_MM = 3.0      # hole cutters reach this far outside the skin
HOLE_CUT_INSIDE_MM = 0.6       # and this far beyond the deepest point of the cavity wall under the hole
VOLUME_SOLVE_TOL = 2e-5        # relative error of the cavity-plus-pocket volume after the scale solve
CAP_EPS_MM = 0.02              # the caps of the window and the windway sit this far from the cap planes
CLEAN_MERGE_MM = 1e-3          # after the last cut, points closer than 1 micrometre are merged (Boolean slivers)

# Hook for the later feature "user outer mesh inside a sculpt envelope" (not built in this version).
# A function (envelope (V, F), body context) -> (V, F) may be set here; it runs after step 4.
OUTER_MESH_HOOK = None


@dataclass
class BodyResult:
    body_id: str
    preset_id: str
    v0_cm3: float
    rating: str
    sizing: object                       # kernel BodySizing
    voicing_hash: str
    cavity: object                       # cavity.CavityResult (the loft)
    voicing: object                      # voicing_geo.VoicingSolids
    layout: object                       # holes_layout.Layout
    solid: tuple                         # (V, F) final body
    envelope: tuple                      # (V, F) skin joined with the block, before any cut
    precut: tuple                        # (V, F) body with tubes, before the holes and the voicing cuts
    air_capped: tuple                    # (V, F) capped air (the V0 convention)
    air_fem: tuple                       # (V, F) capped air plus the window throat (for FEM)
    voicing_air: tuple                   # (V, F) the loft joined with the voicing pocket (the kernel's "cavity mesh")
    air_capped_cm3: float
    cavity_air_cm3: float                # loft joined with the pocket (the kernel's "cavity mesh")
    pocket_cm3: float
    booleans: list                       # one dict per Boolean
    measurements: dict = field(default_factory=dict)
    checks: list = field(default_factory=list)       # dicts: name, status, value, limit, message, expected
    files: dict = field(default_factory=dict)
    object_names: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)


def default_body_id(preset_id: str, v0_cm3: float) -> str:
    return f"{preset_id}-{v0_cm3:g}"


def build_body(preset, v0_cm3: float, *, rating: str | None = None, params: dict | None = None,
               body_id: str | None = None, hole_key: str = "print", export_dir: str | None = None,
               renders: bool = False, render_dir: str | None = None, save_blend: bool = False,
               keep_objects: bool = False, run_checks: bool = True, cavity_mode_step: bool = True,
               verbose: bool = True) -> BodyResult:
    """Build a test body. `preset` is a preset name or dict; v0_cm3 is the capped air volume (the acoustic target).

    hole_key     which kernel hole set is cut: "print" (k_hole 0.8, the first prints) or "nominal" (k_hole 1.0).
    export_dir   write <id>.stl (the body), <id>_air_capped.stl, <id>_air_fem.stl and <id>_checks.json there.
    renders      write the review pictures to render_dir (default addon_renders/<id>/ in the repository).
    cavity_mode_step   run the cavity-mode desk check (a second Python process with scipy, see cavity_mode.py).
                 When it is off, or no such Python is found, the check `cavity_mode_computed` fails and says so.
    """
    k = kernel_bridge.kernel()
    P = params if params is not None else kernel_bridge.load_params()
    if isinstance(preset, str):
        preset = presets_mod.get_preset(preset)
    pid = preset.get("id", "custom")
    body_id = body_id or default_body_id(pid, v0_cm3)
    log = (lambda *a: print(f"[{body_id}]", *a, flush=True)) if verbose else (lambda *a: None)

    # ---- 1 sizing (hole sizes do not depend on the cavity length; the checks do, see below)
    sz = k.sizing.size_body(float(v0_cm3), rating, params=P)
    v = sz.voicing
    target_cm3 = sz.cavity_volume_for_mesh_cm3
    wall = float(P["hole_rules"]["wall_at_holes_mm"])
    tube_wall = float(P["hole_rules"]["tube_wall_mm"])
    segments = int(P["constraints"].get("mesh_hole_segments", HOLE_SEGMENTS_DEFAULT))
    log(f"sizing: V0 {sz.v0_cm3:.2f} cm3, cavity mesh target {target_cm3:.3f} cm3, voicing {v.version_hash} "
        f"({v.shape} {v.window_length_mm:.2f} x {v.window_width_mm:.2f} mm)")

    # ---- 2 cavity: solve the loft volume so that loft + pocket = target
    blog = meshutil.BooleanLog()
    loft_target = target_cm3
    cav = vs = air = None
    pocket_mm3 = 0.0
    for it in range(5):
        cav = cavity_mod.build_cavity(preset, loft_target, keep_object=False)
        vs = voicing_geo.build(v, cav.math.port_frame())
        aV, aF, solver = meshutil.boolean((cav.V, cav.F), vs.pocket, "UNION")
        air = (aV, aF)
        air_mm3 = meshutil.volume(aV, aF)
        pocket_mm3 = air_mm3 - cav.volume_cm3 * 1000.0
        err = air_mm3 / (target_cm3 * 1000.0) - 1.0
        log(f"volume solve {it}: loft {cav.volume_cm3:.4f} cm3 + pocket {pocket_mm3 / 1000:.4f} cm3 = {air_mm3 / 1000:.4f} cm3 "
            f"({100 * err:+.5f} %)")
        if abs(err) < VOLUME_SOLVE_TOL:
            break
        loft_target = target_cm3 - pocket_mm3 / 1000.0
    else:
        raise meshutil.GeometryError("the cavity volume solve did not converge")
    rep = meshutil.manifold_report(*air)
    if not rep["manifold"] or rep["shells"] != 1:
        raise meshutil.GeometryError("cavity joined with the pocket is not one closed shell")
    if pocket_mm3 <= 0:
        raise meshutil.GeometryError("the voicing pocket added no air: the inner plane is inside the cavity")
    blog.steps.append(dict(name="cavity + voicing pocket (air)", operation="UNION", solver=solver,
                           volume_before_mm3=cav.volume_cm3 * 1000.0, volume_after_mm3=air_mm3, delta_mm3=pocket_mm3,
                           expected_mm3=None, bounds=(0.0, float(meshutil.volume(*vs.pocket))), ok=True, manifold=True,
                           shells=1, triangles=rep["triangles"]))

    # the checks need the real internal length for P1-P3; the P0 egg keeps the kernel's own length
    L_int = None if pid == "P0" else cav.length_mm
    sz = k.sizing.size_body(float(v0_cm3), rating, params=P, L_int_mm=L_int)

    # ---- 3 skin, 4 envelope
    normals = meshutil.vertex_normals(cav.V, cav.F)
    skin = (cav.V + wall * normals, cav.F.copy())
    if meshutil.self_intersections(*skin) > 0:
        raise meshutil.GeometryError("the offset skin intersects itself")
    block_mm3 = meshutil.volume(*vs.block)
    envelope = blog.apply("skin + voicing block", skin, vs.block, "UNION", bounds=(0.0, block_mm3 + 1.0))
    if OUTER_MESH_HOOK is not None:
        envelope = OUTER_MESH_HOOK(envelope, dict(preset=preset, sizing=sz, cavity=cav, voicing=vs))

    # ---- 5 shell
    solid = blog.apply("envelope - cavity air", envelope, air, "DIFFERENCE", expected_delta_mm3=-air_mm3,
                       tol_rel=1e-4, tol_abs_mm3=0.5)

    # ---- hole placement
    rows = sz.holes.solutions[hole_key]
    slide_max = float(P.get("ergonomics", {}).get("subhole_distance_mm", (0.0, holes_layout.SUBHOLE_SLIDE_MAX_MM))[1])
    layout = holes_layout.make_layout(cav.math, preset, rows, slide_max_mm=slide_max)
    for m in layout.messages:
        log("layout: " + m)

    # ---- 6 tubes
    for h in layout.holes:
        if h.tube_mm <= 0:
            continue
        r_out = 0.5 * h.d_mm + tube_wall
        tube = meshutil.cylinder(h.centre, h.axis, r_out, -h.tube_mm, TUBE_ROOT_MM, segments, area_true=False)
        poly = 0.5 * segments * r_out * r_out * math.sin(2 * math.pi / segments)
        solid = blog.apply(f"tube {h.name}", solid, tube, "UNION", expected_delta_mm3=poly * h.tube_mm,
                           tol_rel=0.08, tol_abs_mm3=2.0)
    precut = solid

    # ---- 7 holes. The air mesh is built beside the body: cavity air, minus the tubes, plus each hole up to the skin.
    air_mesh = air
    for h in layout.holes:
        if h.tube_mm > 0:
            tube = meshutil.cylinder(h.centre, h.axis, 0.5 * h.d_mm + tube_wall, -h.tube_mm, TUBE_ROOT_MM, segments, area_true=False)
            V, F, _ = meshutil.boolean(air_mesh, tube, "DIFFERENCE")
            air_mesh = (V, F)
    for h in layout.holes:
        inner = max(h.tube_mm, rim_depth(cav, h)) + HOLE_CUT_INSIDE_MM
        cutter = meshutil.cylinder(h.centre, h.axis, 0.5 * h.d_mm, -inner,
                                   h.wall_mm + HOLE_CUT_OUTSIDE_MM, segments, area_true=True)
        expected = -math.pi * h.d_mm ** 2 / 4.0 * (h.wall_mm + h.tube_mm)
        solid = blog.apply(f"hole {h.name}", solid, cutter, "DIFFERENCE", expected_delta_mm3=expected,
                           tol_rel=0.04, tol_abs_mm3=1.0)
        V, F, _ = meshutil.boolean(cutter, envelope, "INTERSECT")       # the hole, capped at the outer skin
        V, F, _ = meshutil.boolean(air_mesh, (V, F), "UNION")
        air_mesh = (V, F)

    # ---- 8 window (throat + labium ramp), then the windway. Expected volumes come from column integration,
    #        which does not use a Boolean.
    o, fx, fy, fz = vs.frame
    L, W = v.window_length_mm, v.window_width_mm
    reach = vs.info["ramp_reach_mm"]
    bbox = (-L - 1.0, reach + 1.0, -(0.5 * W + reach + 1.0), 0.5 * W + reach + 1.0)
    exp_window = meshutil.intersection_volume_columns(solid, vs.window, o, fx, fy, fz, bbox, step=0.25)
    solid = blog.apply("window throat + labium ramp", solid, vs.window, "DIFFERENCE", expected_delta_mm3=-exp_window,
                       tol_rel=0.03, tol_abs_mm3=3.0)
    bbox = (-L - v.windway_length_mm - 2.0, 2.0, -(0.5 * W + 0.5), 0.5 * W + 0.5)
    exp_windway = meshutil.intersection_volume_columns(solid, vs.windway, o, fx, fy, fz, bbox, step=0.2)
    solid = blog.apply("windway", solid, vs.windway, "DIFFERENCE", expected_delta_mm3=-exp_windway,
                       tol_rel=0.04, tol_abs_mm3=3.0)

    # ---- cleanup: merge the points that the Booleans left closer than a micrometre. Nothing is remeshed or smoothed.
    solid = meshutil.cleanup(*solid, merge_mm=CLEAN_MERGE_MM)
    if not meshutil.manifold_report(*solid)["manifold"]:
        raise meshutil.GeometryError("the final mesh is not manifold")

    # ---- capped air (the V0 convention): the mesh built beside the body, and the air with the window throat for FEM
    capped = meshutil.cleanup(*largest_shell(*air_mesh), merge_mm=CLEAN_MERGE_MM)
    air_fem = meshutil.cleanup(*air_with_throat(capped, vs, v), merge_mm=CLEAN_MERGE_MM)
    capped_cm3 = meshutil.volume(*capped) / 1000.0
    log(f"capped air (built) {capped_cm3:.4f} cm3 against V0 {sz.v0_cm3 * sz.volume_factor:.4f} cm3 "
        f"({100 * (capped_cm3 / (sz.v0_cm3 * sz.volume_factor) - 1):+.4f} %)")

    body = BodyResult(body_id=body_id, preset_id=pid, v0_cm3=float(v0_cm3), rating=v.rating, sizing=sz,
                      voicing_hash=v.version_hash, cavity=cav, voicing=vs, layout=layout, solid=solid, envelope=envelope,
                      precut=precut, air_capped=capped, air_fem=air_fem, voicing_air=air, air_capped_cm3=capped_cm3,
                      cavity_air_cm3=air_mm3 / 1000.0, pocket_cm3=pocket_mm3 / 1000.0, booleans=blog.steps,
                      params=dict(wall_mm=wall, tube_wall_mm=tube_wall, hole_segments=segments, hole_key=hole_key))

    # The STL files are written before the checks: the cavity-mode step reads the exported air mesh.
    if export_dir:
        export_meshes(body, export_dir)
    if run_checks:
        from . import checks_geo
        checks_geo.run_all(body, P, cavity_mode_step=cavity_mode_step)
    if export_dir:
        write_checks_json(body, export_dir)
    if renders:
        from . import render_body
        render_body.render_all(body, render_dir)
    if keep_objects or save_blend:
        make_objects(body, preset)
    if save_blend and export_dir:
        import bpy
        path = os.path.join(export_dir, f"{body_id}.blend")
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(path))
        body.files["blend"] = path
    return body


def rim_depth(cav, h) -> float:
    """How far the cavity wall under a hole lies below the hole centre, measured along the hole axis.

    On a curved wall the cavity surface at the rim of a hole is deeper than at its centre (by about
    radius^2 / (2 * curvature radius): more than 1 mm for a 13 mm hole near the end of a body). The hole
    cutter must reach below that, or a thin lip of plastic stays across the inner rim of the hole.
    """
    p, n = np.asarray(h.centre, float), np.asarray(h.axis, float)
    rel = cav.V - p
    ax = rel @ n
    rho = np.linalg.norm(rel - np.outer(ax, n), axis=1)
    near = (rho <= 0.5 * h.d_mm + 1.0) & (np.abs(ax) < 0.5 * h.d_mm + 4.0)
    return float(max(0.0, -ax[near].min())) if near.any() else 0.0


def cap_boxes(vs, v):
    """The two boxes that close the voicing side under the V0 convention, in body coordinates.

    k1  everything above the inner plane around the window: the throat, the ramp scoop, the windway roof side
    k2  the windway behind the exit plane, below the inner plane
    Both stop CAP_EPS_MM short of the cap planes, so they never share a face with the body.
    """
    L, W, wall = v.window_length_mm, v.window_width_mm, v.wall_at_window_mm
    reach = vs.info["ramp_reach_mm"]
    e = CAP_EPS_MM
    k1 = meshutil.box_local(-L - v.windway_length_mm - 3.0, reach + 3.0, -(0.5 * W + reach + 3.0), 0.5 * W + reach + 3.0,
                            e, wall + 4.0)
    zc = voicing_geo.windway_centre_z(v)
    k2 = meshutil.box_local(-L - v.windway_length_mm - 3.0, -L - voicing_geo.POCKET_BACK_OVERLAP_MM - e,
                            -(0.5 * W + 0.6), 0.5 * W + 0.6, zc - 0.5 * v.windway_inlet_height_mm - 0.2, 2 * e)
    return [(meshutil.frame_points(b[0], *vs.frame), b[1]) for b in (k1, k2)]


def measure_capped_air_cm3(envelope, solid, vs, v, step: float = 0.25) -> float:
    """Capped air measured from the FINAL body mesh, without a Boolean.

    A point is capped air when it is inside the envelope (the skin joined with the voicing block, which
    closes every hole at the outer skin), outside the body's plastic, and not on the voicing side of the
    caps (cap_boxes). The volume of that set is integrated along columns parallel to the body's Z axis.
    """
    V = envelope[0]
    lo, hi = V.min(axis=0) - 1.0, V.max(axis=0) + 1.0
    I = np.eye(3)
    vol = meshutil.column_volume([envelope], [solid] + cap_boxes(vs, v), (0.0, 0.0, 0.0), I[0], I[1], I[2],
                                 (lo[0], hi[0], lo[1], hi[1]), step)
    return vol / 1000.0


def air_with_throat(capped, vs, v):
    """FEM air domain: the capped air joined with the window throat (the neck of the window), up to the outer face."""
    out = vs.outline
    L, wall = v.window_length_mm, v.wall_at_window_mm
    r0 = np.column_stack([out[:, 0], out[:, 1], np.full(len(out), -0.5)])
    r1 = np.column_stack([out[:, 0], out[:, 1], np.full(len(out), wall)])
    tV, tF = meshutil.prism_from_rings([r0, r1])
    tV[:, 0] -= L
    throat = (meshutil.frame_points(tV, *vs.frame), tF)
    fV, fF, _ = meshutil.boolean(capped, throat, "UNION")
    return fV, fF


def largest_shell(V, F):
    """Keep the connected surface with the largest volume; raise if another shell holds real volume."""
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
    best, best_vol, others = None, -1.0, 0.0
    for r in np.unique(roots):
        vol = abs(meshutil.volume(V, F[roots == r]))
        if vol > best_vol:
            others += max(best_vol, 0.0)
            best, best_vol = r, vol
        else:
            others += vol
    if others > 5.0:
        raise meshutil.GeometryError(f"the capped air has loose pieces with {others:.1f} mm3 in total")
    Fk = F[roots == best]
    used = np.unique(Fk)
    remap = -np.ones(V.shape[0], dtype=np.int64)
    remap[used] = np.arange(len(used))
    return V[used], remap[Fk]


# ------------------------------------------------------------------ export, objects, summary

def export_body(body: BodyResult, export_dir: str) -> dict:
    """Write the STL files and the check results. A body whose voicing hash is not intact is never exported."""
    export_meshes(body, export_dir)
    write_checks_json(body, export_dir)
    return body.files


def export_meshes(body: BodyResult, export_dir: str) -> dict:
    """Write <id>.stl, <id>_air_capped.stl and <id>_air_fem.stl."""
    k = kernel_bridge.kernel()
    v = body.sizing.voicing
    if not (k.voicing.voicing_hash_of(v) == v.version_hash == body.voicing_hash):
        raise meshutil.GeometryError(f"{body.body_id}: the voicing hash is not intact; the body is not exported")
    os.makedirs(export_dir, exist_ok=True)
    bid = body.body_id
    files = {
        "stl": export.write_stl(os.path.join(export_dir, f"{bid}.stl"), *body.solid, header=f"ocarina {bid} body, mm"),
        "air_capped_stl": export.write_stl(os.path.join(export_dir, f"{bid}_air_capped.stl"), *body.air_capped,
                                           header=f"ocarina {bid} capped air (V0), mm"),
        "air_fem_stl": export.write_stl(os.path.join(export_dir, f"{bid}_air_fem.stl"), *body.air_fem,
                                        header=f"ocarina {bid} air with window throat, mm"),
    }
    body.files.update(files)
    return files


def write_checks_json(body: BodyResult, export_dir: str) -> str:
    """Write <id>_checks.json: the checks, the measurements and the Boolean log."""
    os.makedirs(export_dir, exist_ok=True)
    bid = body.body_id
    path = os.path.join(export_dir, f"{bid}_checks.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(dict(body_id=bid, preset=body.preset_id, v0_cm3=body.v0_cm3, voicing_hash=body.voicing_hash,
                       checks=body.checks, measurements=body.measurements, booleans=body.booleans), fh, indent=1,
                  default=_json_default)
    body.files["checks_json"] = path
    return path


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, tuple):
        return list(o)
    return str(o)


def make_objects(body: BodyResult, preset: dict) -> dict:
    """Put the result into the scene: the body mesh (with the voicing hash as a custom property), the air
    domain, and the procedural cavity object with its Geometry Nodes modifier."""
    import bpy
    names = {}
    ob = meshutil.object_from_arrays(f"OCA_{body.body_id}", *body.solid)
    ob["oca_body_id"] = body.body_id
    ob["oca_voicing_hash"] = body.voicing_hash          # voicing.version_hash, stored on the object
    ob["oca_voicing"] = json.dumps(body.sizing.voicing.to_dict())
    ob["oca_v0_cm3"] = body.v0_cm3
    ob["oca_preset"] = body.preset_id
    names["body"] = ob.name
    air = meshutil.object_from_arrays(f"OCA_{body.body_id}_air", *body.air_capped)
    air.display_type = "WIRE"
    names["air"] = air.name
    cav = cavity_mod.build_cavity(preset, body.cavity.target_volume_cm3, name=f"OCA_{body.body_id}_cavity", keep_object=True)
    bpy.data.objects[cav.object_name].display_type = "WIRE"
    names["cavity"] = cav.object_name
    body.object_names.update(names)
    return names


STATUS_MARKS = {"pass": "PASS", "needs_fem": "NEEDS FEM", "fail": "FAIL", "info": "INFO", "warn": "WARN"}


def format_summary(body: BodyResult) -> str:
    sz, v = body.sizing, body.sizing.voicing
    out = [f"{body.body_id}: {body.preset_id}, V0 {sz.v0_cm3:.2f} cm3, voicing {v.version_hash}",
           f"  window {v.shape} {v.window_length_mm:.2f} x {v.window_width_mm:.2f} mm, {v.window_area_mm2:.1f} mm2; "
           f"windway exit {v.windway_exit_height_mm:.2f} x {v.windway_width_mm:.2f} mm",
           f"  cavity length {body.cavity.length_mm:.2f} mm; cavity air (loft + pocket) {body.cavity_air_cm3:.4f} cm3 "
           f"(target {sz.cavity_volume_for_mesh_cm3:.4f}); capped air {body.air_capped_cm3:.4f} cm3 (V0 {sz.v0_cm3:.4f})"]
    for c in body.checks:
        mark = STATUS_MARKS.get(c["status"], c["status"])
        exp = " (expected)" if c.get("expected") else ""
        out.append(f"  {mark}{exp} {c['name']}: {c['message']}")
    for name, path in body.files.items():
        out.append(f"  file {name}: {path}")
    return "\n".join(out)
