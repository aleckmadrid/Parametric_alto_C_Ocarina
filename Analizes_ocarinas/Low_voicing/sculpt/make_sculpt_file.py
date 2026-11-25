"""Make the Blender file the owner sculpts in (series 3, 2026-11-20).

    blender -b --factory-startup --python Analizes_ocarinas/Low_voicing/sculpt/make_sculpt_file.py

The owner offered to sculpt a better reference for the outside of the low-voicing body, and asked for "a simple
blender file and instructions ... the file might include the no holes volume shell and internal and any other cutout
non applied geometries". This writes sculpt/OCA_sculpt_base.blend with two bases of the seed P4 at 80 cm3, each in
its own collection (what each object is for is in Sculpt_instructions.md, and in the text "README" inside the file):

    A  the approved stance: port 20 deg, pipe +4 deg and 57 mm, the plain body with its neck (trial s3-r20p)
    B  the same with my voicing shoulder (9 mm, port 25 deg, pipe 47 mm; trial s3-h9s), hidden when the file opens

Each base is what ocarina_addon.shell_edit.build_base makes (the solid shell, the solid neck, the chamber and the
cuts for reference), so finish_sculpt.py can finish an instrument from whatever the owner leaves. Added here:

    limit     the chamber moved outward by the least wall (1.32 mm): the sculpt must stay outside it
    keep-out  the 45 deg flare over the window: no plastic inside it
    mouth end a ring at the mouth end of the pipe: the neck must end exactly there
    cutters   the pipe, the window with its dish, the inner pocket and the twelve holes as separate objects
    PREVIEW   the shell and the neck with everything cut out, live (Boolean modifiers on a copy; hidden, slow)
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np

import bpy

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in (str(ROOT), str(HERE.parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

from ocarina_addon import body as body_mod, kernel_bridge, meshutil, presets as presets_mod, shell_edit  # noqa: E402
import voicing_shoulder  # noqa: E402

voicing_shoulder.install()

V0 = 80.0
REF_SCALE, REF_LIP = 0.75, (32.0, 18.24, 11.02)      # the owner's Blender reference (ref_oot_blend/): size factor, its lip
ROUND_TIP = dict(neck_floor_mm=8.6, neck_base_depth_mm=29.0)
BASES = {
    "A": dict(title="A - approved stance, plain body (sculpt this)", preset="P4",
              over=dict(port_angle_deg=20.0, windway_pitch_deg=4.0, stub_pitch_deg=4.0, **ROUND_TIP),
              params={"voicing_rules.windway_length_mm": 57.0}, hidden=False),
    "B": dict(title="B - the same with my voicing shoulder (compare, or sculpt this instead)", preset="P4",
              over=dict(port_angle_deg=25.0, windway_pitch_deg=4.0, stub_pitch_deg=4.0, voicing_shoulder_mm=9.0, **ROUND_TIP),
              params={"voicing_rules.windway_length_mm": 47.0}, hidden=True),
}
COLORS = dict(shell=(0.78, 0.74, 0.62, 1.0), neck=(0.70, 0.62, 0.50, 1.0), chamber=(0.25, 0.50, 1.0, 1.0), cuts=(0.9, 0.2, 0.2, 1.0),
              limit=(1.0, 0.55, 0.0, 1.0), keepout=(1.0, 0.0, 0.6, 1.0), mouth=(0.0, 0.7, 0.2, 1.0), preview=(0.85, 0.85, 0.85, 1.0))


def material(name, rgba):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = rgba
    return m


def add(name, mesh, col, role, color, wire=False, select=True, hide=False):
    ob = meshutil.object_from_arrays(name, np.asarray(mesh[0], float), np.asarray(mesh[1], np.int64), collection=col)
    ob.data.materials.append(material(f"OCA {color}", COLORS[color]))
    ob.color = COLORS[color]
    ob["oca_role"] = role
    if wire:
        ob.display_type = "WIRE"
    ob.hide_select = not select
    ob.hide_render = wire
    ob.hide_viewport = hide
    return ob


def params_with(P, par):
    import copy
    Q = copy.deepcopy(P)
    for key, value in par.items():
        table, field = key.split(".")
        Q[table][field] = value
    return Q


def flare(vs, v, height=14.0):
    """The keep-out over the window: the 45 deg flare from its rim at the outer face, as a solid."""
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    L, wall = v.window_length_mm, v.wall_at_window_mm
    out = np.asarray(vs.outline, float)
    rings = []
    for h in (0.0, height):
        xw = out[:, 0] + h * np.cos(out[:, 2])
        y = out[:, 1] + h * np.sin(out[:, 2])
        rings.append(o + np.outer(xw - L, fx) + np.outer(y, fy) + (wall + h) * fz)
    V, F = meshutil.prism_from_rings(rings)
    if meshutil.volume(V, F) < 0:
        F = F[:, ::-1]
    return V, F


def mouth_ring(vs, v, zc):
    do, dx, dy, dz = (np.asarray(a, float) for a in vs.windway_frame())
    c = do - (v.window_length_mm + v.windway_length_mm) * dx + zc * dz
    return meshutil.cylinder(c, -dx, 11.0, -0.15, 0.15, 48, area_true=True), c


def preview(name, shell_ob, neck_ob, chamber_ob, cutters_col, col):
    """The cut result, live: a copy of the shell's geometry (Geometry Nodes, Object Info) with Boolean modifiers."""
    tree = bpy.data.node_groups.new(f"{name} source", "GeometryNodeTree")
    tree.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    info = tree.nodes.new("GeometryNodeObjectInfo")
    info.transform_space = "RELATIVE"
    info.inputs["Object"].default_value = shell_ob
    out = tree.nodes.new("NodeGroupOutput")
    tree.links.new(info.outputs["Geometry"], out.inputs[0])
    ob = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    col.objects.link(ob)
    ob.data.materials.append(material("OCA preview", COLORS["preview"]))
    m = ob.modifiers.new("shell (live copy)", "NODES")
    m.node_group = tree
    for label, op, target in (("+ neck", "UNION", neck_ob), ("- chamber", "DIFFERENCE", chamber_ob)):
        b = ob.modifiers.new(label, "BOOLEAN")
        b.operation, b.object = op, target
        b.solver = "EXACT"
    b = ob.modifiers.new("- pipe, window, holes", "BOOLEAN")
    b.operation, b.operand_type, b.collection = "DIFFERENCE", "COLLECTION", cutters_col
    b.solver = "EXACT"
    ob.hide_viewport = True
    ob.hide_render = True
    ob.hide_select = True
    ob["oca_role"] = "preview"
    return ob


def one_base(key, spec, P0):
    preset = dict(presets_mod.get_preset(spec["preset"]), **spec["over"])
    P = params_with(P0, spec["params"])
    bid = f"{spec['preset']}-80-sculpt{key}"
    top = bpy.data.collections.new(spec["title"])
    bpy.context.scene.collection.children.link(top)
    base = shell_edit.build_base(preset, V0, collection=top, params=P, body_id=bid)
    names = base.object_names
    shell_ob, neck_ob = bpy.data.objects[names["shell"]], bpy.data.objects[names["neck"]]
    shell_ob["oca_param_overrides"] = json.dumps(spec["params"])
    for k, color in (("shell", "shell"), ("neck", "neck"), ("chamber", "chamber"), ("cuts", "cuts")):
        ob = bpy.data.objects[names[k]]
        ob.data.materials.append(material(f"OCA {color}", COLORS[color]))
        ob.color = COLORS[color]
    v, vs = base.sizing.voicing, base.voicing
    guides = bpy.data.collections.new(f"{key} guides (do not edit)")
    cutters = bpy.data.collections.new(f"{key} cutters (not applied)")
    top.children.link(guides)
    top.children.link(cutters)
    add(f"{key}_limit_least_wall_1.32mm", body_mod.plain_skin(base.cavity, body_mod.SHELL_MIN_WALL_MM), guides, "limit", "limit", wire=True, select=False)
    add(f"{key}_keepout_window_flare", flare(vs, v), guides, "keepout", "keepout", wire=True, select=False)
    ring, mouth = mouth_ring(vs, v, float(vs.info["windway_centre_z_mm"]))
    add(f"{key}_mouth_end_ring", ring, guides, "mouth_end", "mouth", select=False)
    add(f"{key}_cut_pipe", vs.windway, cutters, "cut", "cuts", wire=True, select=False)
    add(f"{key}_cut_window_and_dish", vs.window, cutters, "cut", "cuts", wire=True, select=False)
    segments = 48
    for h in base.layout.holes:
        cyl = meshutil.cylinder(h.centre, h.axis, 0.5 * h.d_mm, -max(h.tube_mm, 0.5) - 1.0, h.wall_mm + 12.0, segments, area_true=True)
        add(f"{key}_cut_hole_{h.name}", cyl, cutters, "cut", "cuts", wire=True, select=False)
    add(f"{key}_inner_pocket_of_the_voicing", vs.pocket, guides, "pocket", "chamber", wire=True, select=False)
    preview(f"{key}_PREVIEW_cut_result (slow)", shell_ob, neck_ob, bpy.data.objects[names["chamber"]], cutters, top)
    if spec["hidden"]:
        top.hide_viewport = True
    o = np.asarray(vs.frame[0], float)
    S = np.asarray(base.shell[0], float)
    return dict(key=key, body_id=bid, title=spec["title"], shell=names["shell"], neck=names["neck"], voicing_hash=v.version_hash,
                overrides=spec["over"], param_overrides=spec["params"], window_mm=[float(v.window_length_mm), float(v.window_width_mm)],
                wall_at_window_mm=float(v.wall_at_window_mm), pipe_mm=float(v.windway_length_mm), lip_xyz=[float(c) for c in o],
                mouth_end_xyz=[float(c) for c in mouth], shell_size_mm=[float(c) for c in (S.max(0) - S.min(0))],
                shell_cm3=float(meshutil.volume(*base.shell) / 1000.0), neck_cm3=float(meshutil.volume(*base.neck) / 1000.0),
                holes={h.name: dict(centre=[float(c) for c in h.centre], d_mm=float(h.d_mm)) for h in base.layout.holes})


README = """OCARINA SCULPT BASE (series 3, low voicing) - made by sculpt/make_sculpt_file.py
Units are millimetres. Read Analizes_ocarinas/Low_voicing/sculpt/Sculpt_instructions.md first.

Collection A (visible): the approved stance, a plain body with its neck. Collection B (hidden): the same with a voicing
shoulder already added by formula. Sculpt the SHELL and the NECK of ONE collection (or join them and sculpt one mesh).

  ..._shell          SCULPT. The solid outside of the body, no holes.
  ..._neck           SCULPT. The solid neck. May be joined into the shell (Ctrl+J) - then sculpt the join freely.
  ..._chamber        blue wire. The air. Not editable; it is solved again when the body is finished.
  ..._limit...       orange wire. The chamber plus the least wall (1.32 mm). Stay OUTSIDE it everywhere.
  ..._keepout...     pink wire. The 45 degree flare over the window. NO plastic inside it.
  ..._mouth_end_ring green. The neck must still end here, and the pipe's opening must stay in the end face.
  ..._cut_...        red wire. What will be cut: pipe, window with its dish, the 12 holes. Not applied.
  ..._PREVIEW...     hidden. Switch it on in the outliner (screen icon) to see the body with everything cut. Slow.

  REFERENCE_goes_here  an empty. To see your own reference model in place at alto size: File > Append its
                     "Ocarina Body", select it, then shift-select this empty, Ctrl+P > Object (Without Inverse).

Save under a NEW name in the same folder (File > Save As), e.g. OCA_sculpt_v1.blend. Do not apply the cutters.
"""


def main():
    for ob in list(bpy.data.objects):                       # the default cube sits where the window is
        bpy.data.objects.remove(ob, do_unlink=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    scene.unit_settings.length_unit = "MILLIMETERS"
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.clip_start, space.clip_end = 0.5, 5000.0
                        space.overlay.grid_scale = 0.001
                        space.shading.color_type = "MATERIAL"
    P0 = kernel_bridge.load_params()
    info = {k: one_base(k, spec, P0) for k, spec in BASES.items()}
    # Where the owner's own reference model goes (the file is theirs and is not put in here): an empty that carries the
    # turn, the size and the place. The model's frame is x = length (bulb at +x), y = thickness (thumb face +y),
    # z = toward the player; ours is X = length (tail at +X), Y = away from the player, Z = the finger deck. At 0.75
    # of its size it has our air, and its lip (32.0, 18.2, 11.0 in its own millimetres) is put on our lip, the origin.
    import mathutils
    R = mathutils.Matrix(((-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, -1.0, 0.0)))
    M = (R * REF_SCALE).to_4x4()
    M.translation = -(R @ mathutils.Vector(REF_LIP)) * REF_SCALE
    em = bpy.data.objects.new("REFERENCE_goes_here (parent your model to me, Without Inverse)", None)
    em.empty_display_type = "ARROWS"
    em.empty_display_size = 20.0
    em.matrix_world = M
    scene.collection.objects.link(em)
    txt = bpy.data.texts.new("README")
    txt.write(README)
    out = HERE / "OCA_sculpt_base.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out), check_existing=False)
    (HERE / "sculpt_base.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print("SCULPT FILE", out, {k: (v["shell_size_mm"], v["voicing_hash"]) for k, v in info.items()}, flush=True)


if __name__ == "__main__":
    main()
