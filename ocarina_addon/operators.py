"""Build, export and inspect ocarina specimens from Blender."""

import functools
import json

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, PointerProperty, StringProperty

PRESET_ITEMS = [("P0", "P0 control egg", "Ellipsoid 2.2 : 1.5 : 1"), ("P1", "P1 teardrop", ""),
                ("P2", "P2 tailed gourd", ""), ("P3", "P3 traditional transverse", "Stashed: in no stage list"),
                ("P4", "P4 seed", "Smooth, slender seed (docs/08)"),
                ("P4-bowl", "P4 low voicing bowl", "Soft voicing, uneven wall, selected thumb offset"),
                ("P4-bowl-e889", "P4 bowl, ellipse 8.89 mm", "Elliptical aperture of the same area and length; geometry only"),
                ("P4-bowl-e1022", "P4 bowl, ellipse 10.22 mm", "Elliptical aperture of the same area, 15 % longer; geometry only")]
RATING_ITEMS = [("preset", "Preset default", "Use the preset’s voice rating"), ("soft", "Soft", "Window length 8.89 mm"), ("medium", "Medium", "Window length 9.65 mm"),
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
    rating: EnumProperty(name="Voice rating", items=RATING_ITEMS, default="preset")
    window_wall: EnumProperty(name="Wall at the window", items=WINDOW_WALL_ITEMS, default="4.0")
    export_dir: StringProperty(name="Export folder", subtype="DIR_PATH", default="",
                               description="Write the STL files and the check report here (empty: do not export)")
    stop_on_unexpected: BoolProperty(name="Stop on a failed check", default=False,
                                     description="Raise an error when a check fails that is not listed as expected")

    calibration_path: StringProperty(name="Calibration file", subtype="FILE_PATH", default="",
                                     description="Fitted TOML constants; empty uses uncalibrated design values")
    inspection: BoolProperty(name="Create annotated inspection", default=True)
    previous_inspection: StringProperty(name="Compare inspection JSON", subtype="FILE_PATH", default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    def execute(self, context):
        from . import api, inspection, kernel_bridge
        try:
            cal = kernel_bridge.kernel().calibration.load_calibration(bpy.path.abspath(self.calibration_path)) if self.calibration_path else None
            previous = bpy.path.abspath(self.previous_inspection) if self.previous_inspection else None
            if previous:
                inspection.load_snapshot(previous)
            out = bpy.path.abspath(self.export_dir) if self.export_dir else None
            options = dict(rating=None if self.rating == "preset" else self.rating,
                           wall_at_window_mm=float(self.window_wall), calibration=cal, keep_objects=True)
            if out:
                body = api.export_specimen(self.preset, self.v0_cm3, out, inspection=self.inspection,
                                           previous_inspection=previous, **options)
            else:
                body = api.build_body(self.preset, self.v0_cm3, **options)
                if self.inspection:
                    inspection.write_inspection(body, None, previous_path=previous)
            _select_result(context, body)
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
    rating: EnumProperty(name="Voice rating", items=RATING_ITEMS, default="preset")
    window_wall: EnumProperty(name="Wall at the window", items=WINDOW_WALL_ITEMS, default="4.0")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    def execute(self, context):
        from . import shell_edit
        try:
            base = shell_edit.build_base(self.preset, self.v0_cm3, rating=None if self.rating == "preset" else self.rating, wall_at_window_mm=float(self.window_wall))
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

    calibration_path: StringProperty(name="Calibration file", subtype="FILE_PATH", default="",
                                     description="Fitted TOML constants for this edited geometry")
    inspection: BoolProperty(name="Create annotated inspection", default=True)
    previous_inspection: StringProperty(name="Compare inspection JSON", subtype="FILE_PATH", default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    @classmethod
    def poll(cls, context):
        from . import shell_edit
        return shell_edit.find_shell(context.active_object) is not None

    def execute(self, context):
        from . import inspection, kernel_bridge, shell_edit
        shell = shell_edit.find_shell(context.active_object)
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")          # a sculpt or edit session keeps its changes until it is left
        try:
            cal = kernel_bridge.kernel().calibration.load_calibration(bpy.path.abspath(self.calibration_path)) if self.calibration_path else None
            previous = bpy.path.abspath(self.previous_inspection) if self.previous_inspection else None
            if previous:
                inspection.load_snapshot(previous)
            body = shell_edit.finish(shell, export_dir=bpy.path.abspath(self.export_dir) if self.export_dir else None,
                                     calibration=cal, inspection=self.inspection, previous_inspection=previous)
            _select_result(context, body)
        except Exception as exc:                 # noqa: BLE001 - show the reason in the UI
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        bad = [c for c in body.checks if c["status"] == "fail" and not c.get("expected")]
        warn = [c for c in body.checks if c["status"] == "warn" and c["name"].startswith("shell_")]
        text = f"{body.body_id}: V0 {body.air_capped_cm3:.2f} cm³, {len(bad)} unexpected failed check(s)"
        if bad:
            text += ": " + "; ".join(f"{c['name']}: {c['message']}" for c in bad)
        if warn:
            text += ". " + "; ".join(c["message"] for c in warn)
        self.report({"WARNING"} if bad or warn else {"INFO"}, text)
        return {"FINISHED"}


def _select_result(context, body):
    obj = bpy.data.objects[body.object_names["body"]]
    if body.files.get("inspection"):
        obj["oca_inspection"] = body.files["inspection"]
    for other in context.selected_objects:
        other.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


class OCA_OT_open_inspection(bpy.types.Operator):
    """Open the selected body's saved geometry report in the browser"""
    bl_idname = "oca.open_inspection"
    bl_label = "Open Geometry Inspection"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and bool(context.active_object.get("oca_inspection"))

    def execute(self, context):
        from pathlib import Path
        path = Path(context.active_object["oca_inspection"])
        if not path.is_file():
            self.report({"ERROR"}, "The inspection file is missing. Rebuild with inspection enabled.")
            return {"CANCELLED"}
        bpy.ops.wm.url_open(url=path.resolve().as_uri())
        return {"FINISHED"}


class OcaSettings(bpy.types.PropertyGroup):
    """scene.oca: what the panel builds, saved with the .blend file. No property has an update function: changing
    one costs nothing, and the panel compares the settings with the validated ones when it is drawn."""
    preset: EnumProperty(name="Preset", items=PRESET_ITEMS, default="P4-bowl")
    v0_cm3: FloatProperty(name="Air volume V0 (cm³)", default=80.0, min=20.0, max=146.0,
                          description="Capped air volume with all holes closed (the acoustic target)")
    rating: EnumProperty(name="Voice rating", items=RATING_ITEMS, default="preset")
    window_wall: EnumProperty(name="Wall at the window", items=WINDOW_WALL_ITEMS, default="4.0")
    export_dir: StringProperty(name="Export folder", subtype="DIR_PATH", default="")
    calibration_path: StringProperty(name="Calibration file", subtype="FILE_PATH", default="",
                                     description="Fitted TOML constants; empty uses uncalibrated design values")
    inspection: BoolProperty(name="Create annotated inspection", default=True)
    previous_inspection: StringProperty(name="Compare inspection JSON", subtype="FILE_PATH", default="")
    measurement_path: StringProperty(name="Measurement file", subtype="FILE_PATH", default="",
                                     description="A filled measurement TOML, for the tuning evidence page")
    # The neck's base, where it meets the body. 0 keeps the preset's value. The outside only: the pipe and the voicing
    # hash do not change. A preset without a neck ignores them.
    neck_base_width_mm: FloatProperty(name="Neck base width (mm)", default=0.0, min=0.0, max=80.0,
                                      description="Width of the neck where it meets the body. 0: the preset's. At or below "
                                                  "the mouth end's width the neck is a tube; larger makes a cone")
    neck_base_depth_mm: FloatProperty(name="Neck base depth (mm)", default=0.0, min=0.0, max=60.0,
                                      description="Depth of the neck, front to back, where it meets the body. 0: the preset's. "
                                                  "At or below the mouth end's depth the neck is a tube; larger makes a cone")
    neck_flare: FloatProperty(name="Neck flare", default=0.0, min=0.0, max=4.0,
                              description="How the neck grows toward the body. 0: the preset's. 1: a straight cone. "
                                          "Larger: a tube near the mouth that flares at the base")
    last_body: StringProperty(options={"HIDDEN"})


def panel_preset(s):
    """(preset, body id) of the panel's settings: the preset's name and None, or, with a neck value set, the preset
    as a dict with the neck's keys replaced and an id that names them, so its files do not pass for the plain body's."""
    w, d, f = round(s.neck_base_width_mm, 2), round(s.neck_base_depth_mm, 2), round(s.neck_flare, 2)
    over = dict(**({"neck_base_width_mm": w} if w else {}), **({"neck_base_depth_mm": d} if d else {}),
                **({"neck_width_exponent": f, "neck_depth_exponent": f} if f else {}))
    if not over:
        return s.preset, None
    from . import body, presets
    return (dict(presets.get_preset(s.preset), **over),
            f"{body.default_body_id(s.preset, s.v0_cm3, float(s.window_wall))}-neck{w:g}x{d:g}f{f:g}")


def settings_signature(s) -> str:
    """What a validation is a validation of. The export folder and the review options do not change the body."""
    return json.dumps([s.preset, round(s.v0_cm3, 6), s.rating, s.window_wall, s.calibration_path,
                       round(s.neck_base_width_mm, 2), round(s.neck_base_depth_mm, 2), round(s.neck_flare, 2)])


def validation_state(scene) -> str:
    """"not built", "not validated", "validated" or "changed since validation": a comparison of strings, no geometry."""
    obj = bpy.data.objects.get(scene.oca.last_body) if scene.oca.last_body else None
    if obj is None:
        return "not built"
    if not obj.get("oca_validated"):
        return "not validated"
    return "validated" if obj["oca_validated"] == settings_signature(scene.oca) else "changed since validation"


@functools.lru_cache(maxsize=None)
def _preset_rating(preset_id: str) -> str:
    from . import kernel_bridge, presets
    return presets.get_preset(preset_id).get("rating") or kernel_bridge.load_params()["voicing_rules"]["default_rating"]


class OCA_OT_run(bpy.types.Operator):
    """Build the body of the panel's settings. Preview: no checks. Validate: all checks, nothing exported. Export: the STL files, checked as read back from disk, with the report, the inspection and the measurement template"""
    bl_idname = "oca.run"
    bl_label = "Ocarina: Preview, Validate or Export"
    bl_options = {"REGISTER", "UNDO"}

    action: EnumProperty(items=[("PREVIEW", "Preview", ""), ("VALIDATE", "Validate", ""), ("EXPORT", "Export", "")], default="PREVIEW")

    def execute(self, context):
        from . import api, inspection, kernel_bridge
        s = context.scene.oca
        try:
            if self.action == "EXPORT" and not s.export_dir:
                raise ValueError("Choose an export folder first.")
            cal = kernel_bridge.kernel().calibration.load_calibration(bpy.path.abspath(s.calibration_path)) if s.calibration_path else None
            previous = bpy.path.abspath(s.previous_inspection) if s.previous_inspection else None
            options = dict(rating=None if s.rating == "preset" else s.rating, wall_at_window_mm=float(s.window_wall),
                           calibration=cal, keep_objects=True)
            preset, body_id = panel_preset(s)
            if body_id:
                options["body_id"] = body_id
            if self.action == "EXPORT":
                body = api.export_specimen(preset, s.v0_cm3, bpy.path.abspath(s.export_dir), inspection=s.inspection,
                                           previous_inspection=previous, **options)
            else:
                body = api.build_body(preset, s.v0_cm3, run_checks=self.action == "VALIDATE", **options)
                if self.action == "VALIDATE" and s.inspection:
                    inspection.write_inspection(body, None, previous_path=previous)
            _select_result(context, body)
        except Exception as exc:                 # noqa: BLE001 - show the reason in the UI
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        obj = bpy.data.objects[body.object_names["body"]]
        s.last_body = obj.name
        if self.action == "PREVIEW":
            obj.pop("oca_validated", None)
            self.report({"INFO"}, f"{body.body_id}: preview, not checked")
            return {"FINISHED"}
        obj["oca_validated"] = settings_signature(s)
        bad = [c for c in body.checks if c["status"] == "fail" and not c.get("expected")]
        self.report({"WARNING"} if bad else {"INFO"},
                    f"{body.body_id}: {len(bad)} unexpected failed check(s)" + (": " + ", ".join(c["name"] for c in bad[:4]) if bad else ""))
        return {"FINISHED"}


class OCA_OT_test_solver(bpy.types.Operator):
    """Look for the Python with numpy and scipy that the cavity-mode check runs in"""
    bl_idname = "oca.test_solver"
    bl_label = "Test Solver"

    def execute(self, context):
        from . import cavity_mode
        exe, why = cavity_mode.find_python(refresh=True)
        self.report({"INFO"} if exe else {"ERROR"}, f"Cavity-mode solver: {exe}" if exe else why)
        return {"FINISHED"}


class OCA_OT_open_evidence(bpy.types.Operator):
    """Write the tuning evidence page of the panel's measurement file and open it in the browser"""
    bl_idname = "oca.open_evidence"
    bl_label = "Open Tuning Evidence"

    @classmethod
    def poll(cls, context):
        return bool(context.scene.oca.measurement_path)

    def execute(self, context):
        from . import evidence
        try:
            page = evidence.write_evidence(bpy.path.abspath(context.scene.oca.measurement_path))
        except Exception as exc:                 # noqa: BLE001 - an unfilled or wrong file says what it lacks
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        bpy.ops.wm.url_open(url=page.resolve().as_uri())
        return {"FINISHED"}


class OCA_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    python_path: StringProperty(name="Python for the cavity-mode check", subtype="FILE_PATH", default="",
                                description="A Python with numpy and scipy. Empty: OCARINA_PYTHON, a .venv beside the add-on, then PATH")

    def draw(self, context):
        self.layout.prop(self, "python_path")
        self.layout.operator(OCA_OT_test_solver.bl_idname)


class OCA_PT_review(bpy.types.Panel):
    bl_label = "Ocarina Build and Review"
    bl_idname = "OCA_PT_review"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Ocarina"

    def draw(self, context):
        from . import cavity_mode
        s = context.scene.oca
        col = self.layout.column(align=True)
        for name in ("preset", "v0_cm3", "rating", "window_wall", "calibration_path"):
            col.prop(s, name)
        if s.rating == "preset":
            col.label(text=f"Rating of the preset: {_preset_rating(s.preset)}")
        for name in ("neck_base_width_mm", "neck_base_depth_mm", "neck_flare"):
            col.prop(s, name)
        col.separator()
        row = col.row(align=True)
        for action in ("PREVIEW", "VALIDATE", "EXPORT"):
            row.operator(OCA_OT_run.bl_idname, text=action.capitalize()).action = action
        state = validation_state(context.scene)
        col.label(text=f"Status: {state}", icon="CHECKMARK" if state == "validated" else "ERROR" if state.startswith("changed") else "DOT")
        for name in ("export_dir", "inspection", "previous_inspection"):
            col.prop(s, name)
        col.separator()
        col.operator("oca.build_base", text="Build Shell to Edit")
        col.operator("oca.finish_body", text="Finish Edited Shell")
        col.separator()
        col.operator("oca.open_inspection", icon="URL")
        col.prop(s, "measurement_path")
        col.operator(OCA_OT_open_evidence.bl_idname, icon="URL")
        col.separator()
        found = cavity_mode._python                           # what the last look found; the panel never starts one
        col.label(text="Cavity-mode check: " + ("not looked for yet" if found is None else "available" if found[0] else "not available"))
        col.operator(OCA_OT_test_solver.bl_idname)
        col.label(text="Geometry checks do not establish tuning.", icon="INFO")


class OCA_MT_menu(bpy.types.Menu):
    bl_idname = "OCA_MT_menu"
    bl_label = "Parametric Ocarina"

    def draw(self, context):
        self.layout.operator(OCA_OT_build_cavity.bl_idname)
        self.layout.operator(OCA_OT_build_body.bl_idname)
        self.layout.separator()
        self.layout.operator(OCA_OT_build_base.bl_idname)
        self.layout.operator(OCA_OT_finish_body.bl_idname)
        self.layout.operator(OCA_OT_open_inspection.bl_idname)


def _menu(self, context):
    self.layout.menu(OCA_MT_menu.bl_idname)


CLASSES = (OcaSettings, OCA_Preferences, OCA_OT_build_cavity, OCA_OT_build_body, OCA_OT_build_base, OCA_OT_finish_body,
           OCA_OT_run, OCA_OT_test_solver, OCA_OT_open_inspection, OCA_OT_open_evidence, OCA_MT_menu, OCA_PT_review)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.oca = PointerProperty(type=OcaSettings)
    bpy.types.VIEW3D_MT_object.append(_menu)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(_menu)
    del bpy.types.Scene.oca
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
