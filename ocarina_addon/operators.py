"""Blender operators. No sidebar panel yet: a bare menu under Object > Parametric Ocarina."""
from __future__ import annotations

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, StringProperty

PRESET_ITEMS = [("P0", "P0 control egg", "Ellipsoid 2.2 : 1.5 : 1"), ("P1", "P1 teardrop", ""),
                ("P2", "P2 tailed gourd", ""), ("P3", "P3 traditional transverse", "Stashed: in no stage list"),
                ("P4", "P4 seed", "Smooth, slender seed (docs/08)")]
RATING_ITEMS = [("soft", "Soft", "Window length 8.89 mm"), ("medium", "Medium", "Window length 9.65 mm"),
                ("loud", "Loud", "Window length 10.41 mm")]
WINDOW_WALL_ITEMS = [("4.0", "4 mm", "Default wall at the window"),
                     ("3.0", "3 mm", "Narrower window at the same V0: a teardrop up to 96.9 cm³ (medium)")]


class OCA_OT_build_cavity(bpy.types.Operator):
    """Make the procedural cavity of a preset, scaled to a mesh volume about the voicing port"""
    bl_idname = "oca.build_cavity"
    bl_label = "Ocarina: Build Cavity"
    bl_options = {"REGISTER", "UNDO"}

    preset: EnumProperty(name="Preset", items=PRESET_ITEMS, default="P0")
    volume_cm3: FloatProperty(name="Mesh volume (cm³)", default=80.0, min=5.0, max=500.0)

    def execute(self, context):
        from . import cavity
        res = cavity.build_cavity(self.preset, self.volume_cm3)
        self.report({"INFO"}, f"{res.object_name}: {res.volume_cm3:.3f} cm³, length {res.length_mm:.1f} mm")
        return {"FINISHED"}


class OCA_OT_build_body(bpy.types.Operator):
    """Build a complete test body: cavity, wall, voicing and holes, with the pre-export checks"""
    bl_idname = "oca.build_body"
    bl_label = "Ocarina: Build Test Body"
    bl_options = {"REGISTER", "UNDO"}

    preset: EnumProperty(name="Preset", items=PRESET_ITEMS, default="P1")
    v0_cm3: FloatProperty(name="Air volume V0 (cm³)", default=80.0, min=20.0, max=146.0,
                          description="Capped air volume with all holes closed (the acoustic target)")
    rating: EnumProperty(name="Voice rating", items=RATING_ITEMS, default="medium")
    window_wall: EnumProperty(name="Wall at the window", items=WINDOW_WALL_ITEMS, default="4.0")
    export_dir: StringProperty(name="Export folder", subtype="DIR_PATH", default="",
                               description="Write the STL files and the check report here (empty: do not export)")
    stop_on_unexpected: BoolProperty(name="Stop on a failed check", default=False,
                                     description="Raise an error when a check fails that is not listed as expected")

    def execute(self, context):
        from . import api
        try:
            body = api.build_body(self.preset, self.v0_cm3, rating=self.rating,
                                  wall_at_window_mm=float(self.window_wall),
                                  export_dir=self.export_dir or None, keep_objects=True)
        except Exception as exc:                 # noqa: BLE001 - show the reason in the UI
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        bad = [c for c in body.checks if c["status"] == "fail" and not c.get("expected")]
        if bad and self.stop_on_unexpected:
            self.report({"ERROR"}, "; ".join(f"{c['name']}: {c['message']}" for c in bad))
            return {"CANCELLED"}
        self.report({"WARNING"} if bad else {"INFO"},
                    f"{body.body_id}: V0 {body.air_capped_cm3:.2f} cm³, {len(bad)} unexpected failed check(s)")
        return {"FINISHED"}


class OCA_OT_build_base(bpy.types.Operator):
    """Shell-edit build, step 1 (prototype): make the solid shell and the solid neck to edit. No hole is cut yet"""
    bl_idname = "oca.build_base"
    bl_label = "Ocarina: Build Base (shell to edit)"
    bl_options = {"REGISTER", "UNDO"}

    preset: EnumProperty(name="Preset", items=[it for it in PRESET_ITEMS if it[0] != "P0"], default="P4")
    v0_cm3: FloatProperty(name="Air volume V0 (cm³)", default=80.0, min=20.0, max=146.0,
                          description="Capped air volume with all holes closed (the acoustic target)")
    rating: EnumProperty(name="Voice rating", items=RATING_ITEMS, default="medium")
    window_wall: EnumProperty(name="Wall at the window", items=WINDOW_WALL_ITEMS, default="4.0")

    def execute(self, context):
        from . import shell_edit
        try:
            base = shell_edit.build_base(self.preset, self.v0_cm3, rating=self.rating, wall_at_window_mm=float(self.window_wall))
        except Exception as exc:                 # noqa: BLE001 - show the reason in the UI
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        shell = bpy.data.objects[base.object_names["shell"]]
        for ob in context.selected_objects:
            ob.select_set(False)
        shell.select_set(True)
        context.view_layer.objects.active = shell
        self.report({"INFO"}, f"{base.body_id}: edit {base.object_names['shell']} and {base.object_names['neck']}, "
                              "then run 'Ocarina: Finish Body' with the shell selected")
        return {"FINISHED"}


class OCA_OT_finish_body(bpy.types.Operator):
    """Shell-edit build, step 3 (prototype): cut the chamber, the holes and the voicing out of the edited shell and neck"""
    bl_idname = "oca.finish_body"
    bl_label = "Ocarina: Finish Body (from the edited shell)"
    bl_options = {"REGISTER", "UNDO"}

    export_dir: StringProperty(name="Export folder", subtype="DIR_PATH", default="",
                               description="Write the STL files and the check report here (empty: do not export)")

    @classmethod
    def poll(cls, context):
        from . import shell_edit
        return shell_edit.find_shell(context.active_object) is not None

    def execute(self, context):
        from . import body as body_mod, report, shell_edit
        shell = shell_edit.find_shell(context.active_object)
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")          # a sculpt or edit session keeps its changes until it is left
        try:
            body = shell_edit.finish(shell, export_dir=self.export_dir or None)
        except Exception as exc:                 # noqa: BLE001 - show the reason in the UI
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        if self.export_dir:
            report.write_body_report(body, self.export_dir, written_by="Written by the operator 'Ocarina: Finish Body'.",
                                     json_default=body_mod._json_default)
        bad = [c for c in body.checks if c["status"] == "fail" and not c.get("expected")]
        warn = [c for c in body.checks if c["status"] == "warn" and c["name"].startswith("shell_")]
        text = f"{body.body_id}: V0 {body.air_capped_cm3:.2f} cm³, {len(bad)} unexpected failed check(s)"
        if bad:
            text += ": " + "; ".join(f"{c['name']}: {c['message']}" for c in bad)
        if warn:
            text += ". " + "; ".join(c["message"] for c in warn)
        self.report({"WARNING"} if bad or warn else {"INFO"}, text)
        return {"FINISHED"}


class OCA_MT_menu(bpy.types.Menu):
    bl_idname = "OCA_MT_menu"
    bl_label = "Parametric Ocarina"

    def draw(self, context):
        self.layout.operator(OCA_OT_build_cavity.bl_idname)
        self.layout.operator(OCA_OT_build_body.bl_idname)
        self.layout.separator()
        self.layout.operator(OCA_OT_build_base.bl_idname)
        self.layout.operator(OCA_OT_finish_body.bl_idname)


def _menu(self, context):
    self.layout.menu(OCA_MT_menu.bl_idname)


CLASSES = (OCA_OT_build_cavity, OCA_OT_build_body, OCA_OT_build_base, OCA_OT_finish_body, OCA_MT_menu)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object.append(_menu)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(_menu)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
