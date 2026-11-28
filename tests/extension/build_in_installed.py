"""Runs INSIDE Blender, in a profile where the extension zip was installed (see test_install.py).

    blender -b --python tests/extension/build_in_installed.py -- <output folder>

It imports the INSTALLED extension (not the repository), builds one body through its API and writes
result.json to the output folder. It must not import anything from the repository.
"""
import importlib
import json
import pathlib
import sys
import traceback

out = pathlib.Path(sys.argv[sys.argv.index("--") + 1])
out.mkdir(parents=True, exist_ok=True)
result = {"ok": False}
try:
    import bpy
    import addon_utils

    name = "bl_ext.user_default.parametric_ocarina"
    mod = importlib.import_module(name)
    result["module_file"] = str(pathlib.Path(mod.__file__).resolve())
    result["user_resources"] = bpy.utils.resource_path("USER")
    result["enabled"] = bool(addon_utils.check(name)[1])
    result["operators"] = [op for op in ("build_cavity", "build_body") if hasattr(bpy.ops.oca, op) and
                           getattr(bpy.ops.oca, op).get_rna_type() is not None]
    bridge = importlib.import_module(name + ".kernel_bridge")
    result["kernel_dir"] = str(bridge.kernel_dir())
    result["params_path"] = str(bridge.params_path())
    result["repository_on_sys_path"] = [p for p in sys.path if p and (pathlib.Path(p) / "ocarina_addon").is_dir()]
    api = importlib.import_module(name + ".api")
    checks_geo = importlib.import_module(name + ".checks_geo")
    body = api.build_checked_body("P0", 65.0, str(out / "P0-65"), root=out)
    inspection = importlib.import_module(name + ".inspection")
    specimen = importlib.import_module(name + ".specimen")
    presets = importlib.import_module(name + ".presets")
    inspection.write_inspection(body, out / "P0-65")
    specimen.write_bundle(body, presets.get_preset("P0"), out / "P0-65")
    result["inspection_created"] = pathlib.Path(body.files["inspection"]).is_file()
    result["measurement_created"] = pathlib.Path(body.files["measurement"]).is_file()
    result["calibration_picker"] = "calibration_path" in bpy.ops.oca.finish_body.get_rna_type().properties
    result.update(
        body_id=body.body_id, voicing_hash=body.voicing_hash,
        unexpected=[c["name"] for c in checks_geo.unexpected_failures(body)],
        statuses={c["name"]: c["status"] for c in body.checks},
        capped_air_cm3=body.measurements["volume"]["capped_air_measured_cm3"],
        cavity_mode=body.measurements["cavity_mode"].get("ratio"),
        files=sorted(p.name for p in (out / "P0-65").iterdir()),
        triangles=body.measurements["stl_file"]["triangles"], manifold=body.measurements["stl_file"]["manifold"])
    # The panel's workflow with the installed copy only: preview, validate and export of the bowl, then an edited shell.
    import numpy as np
    s = bpy.context.scene.oca
    s.preset, s.v0_cm3, s.export_dir, s.inspection = "P4-bowl", 80.0, str(out / "bowl"), True
    operators = importlib.import_module(name + ".operators")
    states = []
    for action in ("PREVIEW", "VALIDATE", "EXPORT"):
        bpy.ops.oca.run(action=action)
        states.append(operators.validation_state(bpy.context.scene))
    result["panel_states"] = states
    result["bowl_files"] = sorted(p.name for p in (out / "bowl").iterdir() if not p.name.startswith("."))
    shell_edit = importlib.import_module(name + ".shell_edit")
    base = shell_edit.build_base("P4", 80.0, verbose=False)
    shell = bpy.data.objects[base.object_names["shell"]]
    co = np.empty(3 * len(shell.data.vertices))
    shell.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    far = int(np.argmax(np.linalg.norm(co - co.mean(axis=0), axis=1)))
    shell.data.vertices[far].co = (co[far] + 0.3 * (co[far] - co.mean(axis=0)) / np.linalg.norm(co[far] - co.mean(axis=0))).tolist()
    bpy.context.view_layer.objects.active = shell
    bpy.ops.oca.finish_body("EXEC_DEFAULT", export_dir=str(out / "edit"))
    result["edit_files"] = sorted(p.name for p in (out / "edit").iterdir() if not p.name.startswith("."))
    repo = pathlib.Path(__file__).resolve().parents[2]
    sources = [repo / d for d in ("ocarina_addon", "kernel", "tools")]          # the test profile itself may lie in the repository
    result["modules_from_repository"] = sorted(n for n, m in sys.modules.items() if getattr(m, "__file__", None)
                                               and any(pathlib.Path(m.__file__).resolve().is_relative_to(d) for d in sources))
    result["ok"] = True
except Exception:                                   # noqa: BLE001 - the test reads the text
    result["error"] = traceback.format_exc()
(out / "result.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
print("[installed extension]", "OK" if result["ok"] else "FAILED", flush=True)
