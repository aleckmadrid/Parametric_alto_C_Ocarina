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
    result.update(
        body_id=body.body_id, voicing_hash=body.voicing_hash,
        unexpected=[c["name"] for c in checks_geo.unexpected_failures(body)],
        statuses={c["name"]: c["status"] for c in body.checks},
        capped_air_cm3=body.measurements["volume"]["capped_air_measured_cm3"],
        cavity_mode=body.measurements["cavity_mode"].get("ratio"),
        files=sorted(p.name for p in (out / "P0-65").iterdir()),
        triangles=body.measurements["stl_file"]["triangles"], manifold=body.measurements["stl_file"]["manifold"])
    result["ok"] = True
except Exception:                                   # noqa: BLE001 - the test reads the text
    result["error"] = traceback.format_exc()
(out / "result.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
print("[installed extension]", "OK" if result["ok"] else "FAILED", flush=True)
