"""Blender operators. No sidebar panel yet: a bare menu under Object > Parametric Ocarina."""
from __future__ import annotations

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, StringProperty

PRESET_ITEMS = [("P0", "P0 control egg", "Ellipsoid 2.2 : 1.5 : 1"), ("P1", "P1 teardrop", ""),
                ("P2", "P2 tailed gourd", ""), ("P3", "P3 traditional transverse", "")]
RATING_ITEMS = [("soft", "Soft", "Window length 8.89 mm"), ("medium", "Medium", "Window length 9.65 mm"),
                ("loud", "Loud", "Window length 10.41 mm")]


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
    export_dir: StringProperty(name="Export folder", subtype="DIR_PATH", default="",
                               description="Write the STL files and the check report here (empty: do not export)")
    stop_on_unexpected: BoolProperty(name="Stop on a failed check", default=False,
                                     description="Raise an error when a check fails that is not listed as expected")

    def execute(self, context):
        from . import api
        try:
            body = api.build_body(self.preset, self.v0_cm3, rating=self.rating,
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


class OCA_MT_menu(bpy.types.Menu):
    bl_idname = "OCA_MT_menu"
    bl_label = "Parametric Ocarina"

    def draw(self, context):
        self.layout.operator(OCA_OT_build_cavity.bl_idname)
        self.layout.operator(OCA_OT_build_body.bl_idname)


def _menu(self, context):
    self.layout.menu(OCA_MT_menu.bl_idname)


CLASSES = (OCA_OT_build_cavity, OCA_OT_build_body, OCA_MT_menu)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object.append(_menu)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(_menu)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
