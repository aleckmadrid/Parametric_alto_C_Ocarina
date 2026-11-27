"""The shell-edit build (PROTOTYPE, branch shell-edit-prototype): the add-on makes the shell, the user edits it,
the add-on finishes the instrument.

The one-step build (body.build_body) makes the chamber, the wall, the neck, the holes and the voicing in one go,
so the user never touches a shape. Here the same build is cut in two, and the user works in between:

    1  build_base(preset, V0)     makes, as separate objects in one collection
           OCA_<id>_shell    the SOLID outer body: the chamber moved outward by the wall (4 mm), not hollowed yet
           OCA_<id>_neck     the SOLID neck (the voicing block of the rules: the cone neck)
           OCA_<id>_chamber  the chamber, as a wire mesh. For reference: it is solved again when the body is finished
           OCA_<id>_cuts     what will be cut: the pipe, the window and the 12 holes, as a wire mesh. For reference
    2  the user edits the shell and the neck: sculpt, add relief, lengthen the tail, thicken the neck. They are
       plain solids with no hole in them. Modifiers are applied when the body is finished; the objects may be moved.
    3  finish(shell object)       joins the shell and the neck, measures the wall the edited shell has at each hole,
                                  sizes each hole for its own wall, solves the chamber again so that the capped air
                                  is still V0, cuts the chamber, the holes, the window and the pipe, and runs every
                                  check. The base objects are hidden, not deleted: edit again and finish again.

What stays the add-on's: the chamber, the voicing (window, labium, pipe, with its hash), and where the holes are.
What the user may change: the outside. The checks say where an edit went too far:

    wall_thickness        less plastic over the chamber than body.SHELL_MIN_WALL_MM
    voicing_dimensions,   the window face, the labium or the flare around the window were changed
    voicing_keepouts
    windway_mouth_end     the neck was made longer than the pipe, which closes it
    shell_hole_walls      (soft) a hole whose wall is far from the rule's wall, or that its wall pushed above the pad limit
    shell_hole_rims       (soft) relief around the rim of a hole

A mesh that is not one closed solid, a neck that does not touch the shell and a chamber that comes through the
shell are refused before anything is cut, with the reason (body.checked_user_mesh, join_user_shell,
check_chamber_inside).

Not in the prototype, by the owner's decision of 2026-11-18 ("for the experiments afterwards"): moving the finger
holes, and a longer neck with a longer pipe. The pipe keeps the length of the voicing record, so the mouth end of
the neck must stay where it is.

The state that step 3 needs is stored on the shell object as the custom property `oca_base` (JSON): the preset
values, V0, the rating, the window wall, the hole set and the names of the other objects.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np

import bpy

from . import body as body_mod
from . import cavity as cavity_mod
from . import holes_layout, kernel_bridge, meshutil, presets as presets_mod

BASE_PROPERTY = "oca_base"
CUT_GUIDE_ABOVE_MM = 6.0       # the hole guides stand this far above the plain skin
EDIT_SUFFIX = "-edit"          # a finished body is <base id>-edit


@dataclass
class BaseResult:
    body_id: str
    preset_id: str
    v0_cm3: float
    sizing: object                       # kernel BodySizing of the base (the rule's wall at every hole)
    cavity: object                       # cavity.CavityResult
    voicing: object                      # voicing_geo.VoicingSolids
    layout: object                       # holes_layout.Layout
    shell: tuple                         # (V, F): the plain skin, solid
    neck: tuple                          # (V, F): the voicing block, solid
    cuts: tuple                          # (V, F): the pipe, the window and the hole cutters, for reference
    air: tuple                           # (V, F): the chamber joined with the voicing pocket
    state: dict = field(default_factory=dict)        # what finish() needs (stored on the shell object)
    object_names: dict = field(default_factory=dict)
    collection_name: str = ""


def _join(meshes) -> tuple:
    """Several meshes as one (V, F), side by side: nothing is merged. For a reference object only."""
    Vs, Fs, n = [], [], 0
    for V, F in meshes:
        Vs.append(np.asarray(V, float))
        Fs.append(np.asarray(F, np.int64) + n)
        n += len(V)
    return np.concatenate(Vs), np.concatenate(Fs)


def base_parts(preset, v0_cm3: float, *, rating: str | None = None, wall_at_window_mm: float | None = None,
               params: dict | None = None, hole_key: str = "print", body_id: str | None = None, verbose: bool = True,
               sizing_fn=None) -> BaseResult:
    """Step 1 as arrays: the sizing, the chamber, the plain shell, the neck and the cut guides. No scene objects.
    sizing_fn: as in body.build_body (the base of a calibrated build is sized as the body will be); default: the kernel's."""
    k = kernel_bridge.kernel()
    P = params if params is not None else kernel_bridge.load_params()
    if isinstance(preset, str):
        preset = presets_mod.get_preset(preset)
    preset = dict(preset)
    P = presets_mod.params_for(preset, P)
    rating = rating or preset.get("rating")
    pid = preset.get("id", "custom")
    if preset.get("layout") == "none":
        raise ValueError("a voicing stub has no shell to edit: the shell-edit build is for bodies with holes")
    body_id = body_id or body_mod.default_body_id(pid, v0_cm3, wall_at_window_mm, float(P["voicing_rules"]["default_wall_at_window_mm"]))
    log = (lambda *a: print(f"[{body_id} base]", *a, flush=True)) if verbose else (lambda *a: None)

    sz = presets_mod.resolve_sizing(preset, sizing_fn(None) if sizing_fn is not None else
                                    k.sizing.size_body(float(v0_cm3), rating, wall_at_window_mm, params=P, throat_mm=preset.get("window_throat_mm")))
    v = sz.voicing
    wall = float(P["hole_rules"]["wall_at_holes_mm"])
    segments = int(P["constraints"].get("mesh_hole_segments", body_mod.HOLE_SEGMENTS_DEFAULT))
    slide_max = float(P.get("ergonomics", {}).get("subhole_distance_mm", (0.0, holes_layout.SUBHOLE_SLIDE_MAX_MM))[1])
    solved = body_mod.solve_cavity(preset, v, sz.cavity_volume_for_mesh_cm3, log)
    cav, vs = solved.cav, solved.vs
    shell = body_mod.plain_skin(cav, wall)
    if meshutil.self_intersections(*shell) > 0:
        raise meshutil.GeometryError("the offset skin intersects itself")
    rows = body_mod.cut_rows(sz, hole_key)
    layout = holes_layout.make_layout(cav.math, preset, rows, slide_max_mm=slide_max)
    guides = [vs.windway, vs.window]
    for h in layout.holes:
        guides.append(meshutil.cylinder(h.centre, h.axis, 0.5 * h.d_mm, -max(h.tube_mm, 0.5), h.wall_mm + CUT_GUIDE_ABOVE_MM,
                                        segments, area_true=True))
    state = dict(version=1, body_id=body_id, preset=preset, v0_cm3=float(v0_cm3), rating=v.rating,
                 wall_at_window_mm=float(v.wall_at_window_mm), hole_key=hole_key, voicing_hash=v.version_hash,
                 wall_mm=wall)
    log(f"shell {meshutil.volume(*shell) / 1000.0:.2f} cm3 solid, neck {meshutil.volume(*vs.block) / 1000.0:.2f} cm3, "
        f"chamber {solved.air_mm3 / 1000.0:.2f} cm3, voicing {v.version_hash}")
    return BaseResult(body_id=body_id, preset_id=pid, v0_cm3=float(v0_cm3), sizing=sz, cavity=cav, voicing=vs, layout=layout,
                      shell=shell, neck=vs.block, cuts=_join(guides), air=solved.air, state=state)


# ------------------------------------------------------------------ the uneven wall (an option of this build, 2026-11-26)
# The low-voicing experiment's wall (Analizes_ocarinas/Low_voicing/uneven_wall.py and night_dish.night_skin; owner's
# request of 2026-11-24: "the volume shifted to the front so the face holes are less thick and there is more play on the
# back"). Preset keys, all off by default: wall_front_less_mm, wall_back_more_mm, wall_refine_mm. The chamber is not
# changed: the shell is the chamber moved outward by
#
#     wall(n) = wall_at_holes - wall_front_less_mm * s(n_z)   on the deck half    (n_z > 0)
#             = wall_at_holes + wall_back_more_mm * s(-n_z)   on the thumb half   (n_z < 0),      s(x) = x^2 (3 - 2 x)
#
# and body.build_body finishes it as an edited shell: the wall is measured at each hole and the hole sized for it.

def _edge_split(cV, cF, n, mark):
    """Split the edges of the marked triangles; close the others with 2-way splits (red-green: no T-junctions, the
    shell stays one closed solid). The new points get the mean of their edge's normals. Returns cV, cF, n."""
    e_all = np.sort(np.stack([cF[:, [0, 1]], cF[:, [1, 2]], cF[:, [2, 0]]], axis=1), axis=2)      # (T, 3, 2)
    ue, inv = np.unique(e_all.reshape(-1, 2), axis=0, return_inverse=True)
    inv = inv.reshape(-1, 3)
    split = np.zeros(len(ue), bool)
    split[inv[mark].ravel()] = True
    while True:                                   # a triangle with two split edges gets all three (closure)
        two = split[inv].sum(axis=1) == 2
        if not two.any():
            break
        split[inv[two].ravel()] = True
    idx = -np.ones(len(ue), np.int64)
    k = np.flatnonzero(split)
    idx[k] = len(cV) + np.arange(len(k))
    mn = n[ue[k, 0]] + n[ue[k, 1]]
    n = np.vstack([n, mn / np.linalg.norm(mn, axis=1)[:, None]])
    cV = np.vstack([cV, 0.5 * (cV[ue[k, 0]] + cV[ue[k, 1]])])
    cnt = split[inv].sum(axis=1)
    out = [cF[cnt == 0]]
    T3 = cF[cnt == 3]
    m3 = idx[inv[cnt == 3]]                                    # midpoints of edges 01, 12, 20
    a, b, c = T3.T
    out += [np.column_stack([a, m3[:, 0], m3[:, 2]]), np.column_stack([m3[:, 0], b, m3[:, 1]]),
            np.column_stack([m3[:, 2], m3[:, 1], c]), m3]
    T1, I1 = cF[cnt == 1], inv[cnt == 1]
    s1 = split[I1]
    for j in range(3):                                         # the split edge is edge j (vertices j, j+1)
        sel = s1[:, j]
        if not sel.any():
            continue
        t = T1[sel]
        m = idx[I1[sel, j]]
        p, q, r = t[:, j], t[:, (j + 1) % 3], t[:, (j + 2) % 3]
        out += [np.column_stack([p, m, r]), np.column_stack([m, q, r])]
    return cV, np.vstack(out), n


def uneven_skin(cav, wall: float, front_less: float, back_more: float, centre=None, refine=()) -> tuple:
    """The uneven shell (V, F) and the wall at each of its points. refine: radii in mm about `centre` (the window's
    centre); within each, every triangle is split in four once more (the bowl's rim showed the chamber's own grid)."""
    cV, cF = np.asarray(cav.V, float), np.asarray(cav.F, np.int64)
    n = meshutil.vertex_normals(cV, cF)
    for rad in refine:
        near = np.linalg.norm(cV - np.asarray(centre, float), axis=1) < float(rad)
        cV, cF, n = _edge_split(cV, cF, n, near[cF].any(axis=1))
    nz = np.clip(n[:, 2], -1.0, 1.0)

    def s3(x):
        return x * x * (3.0 - 2.0 * x)
    w = wall - front_less * s3(np.maximum(nz, 0.0)) + back_more * s3(np.maximum(-nz, 0.0))
    return cV + w[:, None] * n, cF.copy(), w


def uneven_outer(preset, v0_cm3: float, *, params: dict, **kwargs) -> tuple:
    """The outer shell and the neck of the uneven wall, as body.build_body(outer=...) takes them, and a record.
    kwargs go to base_parts."""
    base = base_parts(preset, v0_cm3, params=params, verbose=False, **kwargs)
    wall = float(params["hole_rules"]["wall_at_holes_mm"])
    f, b = float(preset.get("wall_front_less_mm") or 0.0), float(preset.get("wall_back_more_mm") or 0.0)
    if f < 0 or b < 0 or f >= wall:
        raise ValueError(f"wall_front_less_mm must be 0 to under the wall ({wall:g} mm) and wall_back_more_mm not negative")
    refine = [float(r) for r in (preset.get("wall_refine_mm") or ())]
    o, fx = np.asarray(base.voicing.frame[0], float), np.asarray(base.voicing.frame[1], float)
    centre = o - 0.5 * float(base.sizing.voicing.window_length_mm) * fx
    V, F, w = uneven_skin(base.cavity, wall, f, b, centre, refine)
    if meshutil.self_intersections(V, F) > 0:
        raise meshutil.GeometryError("the uneven skin intersects itself")
    info = dict(front_less_mm=f, back_more_mm=b, refine_mm=refine, wall_least_mm=float(w.min()), wall_most_mm=float(w.max()),
                shell_cm3=float(meshutil.volume(V, F) / 1000.0), plain_shell_cm3=float(meshutil.volume(*base.shell) / 1000.0),
                shell_triangles=int(len(F)))
    return ((V, F), base.neck), info


def build_base(preset, v0_cm3: float, *, collection=None, **kwargs) -> BaseResult:
    """Step 1: make the base objects in the scene (see the module text). kwargs go to base_parts."""
    base = base_parts(preset, v0_cm3, **kwargs)
    bid = base.body_id
    col = collection or bpy.data.collections.new(f"OCA {bid}")
    if collection is None:
        bpy.context.scene.collection.children.link(col)
    names = {}
    for key, (V, F) in (("shell", base.shell), ("neck", base.neck), ("chamber", base.air), ("cuts", base.cuts)):
        ob = meshutil.object_from_arrays(f"OCA_{bid}_{key}", V, F, collection=col)
        names[key] = ob.name
        if key in ("chamber", "cuts"):                      # reference objects: seen through the shell, not selectable
            ob.display_type = "WIRE"
            ob.hide_select = True
            ob.hide_render = True
        ob["oca_role"] = key
        ob["oca_body_id"] = bid
    state = dict(base.state, neck=names["neck"], chamber=names["chamber"], cuts=names["cuts"], collection=col.name)
    shell_ob = bpy.data.objects[names["shell"]]
    shell_ob[BASE_PROPERTY] = json.dumps(state)
    bpy.data.objects[names["neck"]]["oca_shell"] = shell_ob.name
    base.state, base.object_names, base.collection_name = state, names, col.name
    return base


def base_state(shell_ob) -> dict:
    """The record that build_base stored on the shell object. Raises ValueError when the object is not a base shell."""
    raw = shell_ob.get(BASE_PROPERTY) if shell_ob is not None else None
    if not raw:
        raise ValueError("this object is not the shell of a base: run 'Ocarina: Build Base' first and select its shell")
    return json.loads(raw)


def find_shell(obj):
    """The shell object of the base that `obj` belongs to (the shell itself, or its neck)."""
    if obj is None:
        return None
    if obj.get(BASE_PROPERTY):
        return obj
    other = obj.get("oca_shell")
    return bpy.data.objects.get(other) if other else None


def user_meshes(shell_ob, neck_ob=None) -> tuple:
    """(shell (V, F), neck (V, F) or None) as the user left them: modifiers applied, in world coordinates. The neck
    is the object that build_base made, unless another is given; a base whose neck object was deleted or joined into
    the shell has none."""
    state = base_state(shell_ob)
    if neck_ob is None:
        neck_ob = bpy.data.objects.get(state.get("neck", ""))
    for ob in (shell_ob, neck_ob):                          # an object that is switched off is not evaluated: its
        if ob is not None and ob.hide_viewport:             # modifiers would be left out (finish() hides the base)
            ob.hide_viewport = False
    sV, sF, _ = meshutil.evaluated_arrays(shell_ob)
    neck = None
    if neck_ob is not None and neck_ob.type == "MESH" and len(neck_ob.data.polygons):
        nV, nF, _ = meshutil.evaluated_arrays(neck_ob)
        neck = (nV, nF)
    return (sV, sF), neck


def finish(shell_ob, neck_ob=None, *, export_dir: str | None = None, body_id: str | None = None, keep_objects: bool = True,
           hide_base: bool = True, params: dict | None = None, **kwargs):
    """Step 3: finish the body from the edited shell (and neck). Returns the body.BodyResult. kwargs go to
    body.build_body (renders, render_dir, run_checks, cavity_mode_step, verbose ...)."""
    state = base_state(shell_ob)
    outer = user_meshes(shell_ob, neck_ob)
    bid = body_id or state["body_id"] + EDIT_SUFFIX
    for name in (f"OCA_{bid}", f"OCA_{bid}_air", f"OCA_{bid}_cavity"):          # the result of an earlier finish
        old = bpy.data.objects.get(name)
        if old is not None:
            mesh = old.data
            bpy.data.objects.remove(old, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
    # calibration=... (kwargs) sizes the holes from fitted constants ("fitted"); the voicing must still be the base's (below)
    result = body_mod.build_body(state["preset"], state["v0_cm3"], rating=state["rating"],
                                 wall_at_window_mm=state["wall_at_window_mm"], hole_key=state["hole_key"], params=params,
                                 body_id=bid, outer=outer, export_dir=export_dir, keep_objects=keep_objects,
                                 info=dict(base_id=state["body_id"]), **kwargs)
    if result.voicing_hash != state["voicing_hash"]:
        raise meshutil.GeometryError(f"the finished body has the voicing {result.voicing_hash}, the base had {state['voicing_hash']}: "
                                     "the rules changed since the base was built. Build the base again")
    if keep_objects and hide_base:
        for name in (shell_ob.name, state.get("neck"), state.get("chamber"), state.get("cuts")):
            ob = bpy.data.objects.get(name or "")
            if ob is not None:
                ob.hide_viewport = True
    return result
