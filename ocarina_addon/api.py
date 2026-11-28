"""Python API of the add-on (use inside Blender, or through headless.py).

    from ocarina_addon import api
    res  = api.export_cavity("P0", 78.11, "out/P0-cavity.stl")
    body = api.build_body("P1", 80.0, export_dir="out/P1-80", renders=True)
    print(api.format_summary(body))
"""
from __future__ import annotations

from . import cavity as cavity_mod
from . import export as export_mod


def export_cavity(preset, volume_cm3: float, path: str):
    """Build the cavity of `preset` at a mesh volume and write it as STL. Returns the CavityResult."""
    res = cavity_mod.build_cavity(preset, volume_cm3, keep_object=False)
    export_mod.write_stl(path, res.V, res.F, header=f"ocarina cavity {res.preset_id} {volume_cm3:g} cm3, mm")
    return res


def build_body(preset, v0_cm3: float, **kwargs):
    """Build a full test body. See body.build_body for the arguments."""
    from . import body as body_mod
    return body_mod.build_body(preset, v0_cm3, **kwargs)


def format_summary(body) -> str:
    from . import body as body_mod
    return body_mod.format_summary(body)


def build_base(preset, v0_cm3: float, **kwargs):
    """Shell-edit build, step 1 (prototype): the solid shell and the solid neck as objects to edit. See shell_edit.py."""
    from . import shell_edit
    return shell_edit.build_base(preset, v0_cm3, **kwargs)


def finish_body(shell_object, neck_object=None, **kwargs):
    """Shell-edit build, step 3 (prototype): finish the body from the edited shell and neck. See shell_edit.finish."""
    from . import shell_edit
    return shell_edit.finish(shell_object, neck_object, **kwargs)


def build_checked_body(preset, v0_cm3: float, out_dir: str, *, params=None, renders: bool = False, render_dir=None,
                       root=None, **kwargs):
    """Build a body, write its STL files to out_dir, READ THE BODY STL BACK from disk and run every check on
    the file that was written (the cavity-mode step reads the exported air mesh). Then write <id>_checks.json
    and, with renders=True, the review pictures. This is what the geometry check and the stage commands use.

    root: paths in the measurements are given relative to this folder when they lie inside it.
    kwargs go to body.build_body (body_id, rating, hole_key, sizing, ...).
    """
    import pathlib

    from . import body as body_mod
    from . import checks_geo, export, kernel_bridge, meshutil

    P = params if params is not None else kernel_bridge.load_params()
    cavity_mode_step = kwargs.pop("cavity_mode_step", True)
    body = body_mod.build_body(preset, v0_cm3, params=P, export_dir=str(out_dir), run_checks=False, **kwargs)
    V, F = export.read_stl(body.files["stl"])
    file_report = meshutil.manifold_report(V, F)
    from . import presets
    P_body = presets.params_for(presets.get_preset(preset) if isinstance(preset, str) else preset, P)
    checks_geo.run_all(body, P_body, V, F, cavity_mode_step=cavity_mode_step)
    path = pathlib.Path(body.files["stl"]).resolve()
    try:
        shown = path.relative_to(pathlib.Path(root).resolve()).as_posix() if root is not None else str(path)
    except ValueError:
        shown = str(path)
    body.measurements["stl_file"] = dict(path=shown, triangles=file_report["triangles"], manifold=file_report["manifold"],
                                         volume_cm3=meshutil.volume(V, F) / 1000.0,
                                         volume_in_memory_cm3=meshutil.volume(*body.solid) / 1000.0)
    for key in ("air_capped_stl", "air_fem_stl"):
        aV, aF = export.read_stl(body.files[key])
        rep = meshutil.manifold_report(aV, aF)
        body.measurements[key] = dict(triangles=rep["triangles"], manifold=rep["manifold"], shells=rep["shells"],
                                      volume_cm3=meshutil.volume(aV, aF) / 1000.0)
    body_mod.write_checks_json(body, str(out_dir))
    if renders:
        from . import render_body
        render_body.render_all(body, render_dir)
    return body


def export_specimen(preset, v0_cm3: float, out_dir, *, inspection: bool = True, previous_inspection=None, **kwargs):
    """A body as a specimen to print and measure: build_checked_body, then the check report, the annotated inspection
    (with previous_inspection, an earlier <id>_inspection.json, as its comparison), the blank measurement template and
    the specimen record. Refused when out_dir holds a measurement record of this ID (specimen.require_new_export).
    kwargs go to build_checked_body."""
    from . import body as body_mod
    from . import inspection as review
    from . import presets, report, specimen

    if isinstance(preset, str):
        preset = presets.get_preset(preset)
    bid = kwargs.get("body_id") or body_mod.default_body_id(preset.get("id", "custom"), v0_cm3, kwargs.get("wall_at_window_mm"))
    specimen.require_new_export(out_dir, bid)
    if previous_inspection:
        review.load_snapshot(previous_inspection)          # a wrong file fails before the build, not after it
    body = build_checked_body(preset, v0_cm3, str(out_dir), **kwargs)
    body.files["report"] = str(report.write_body_report(body, str(out_dir), json_default=body_mod._json_default))
    if inspection:
        review.write_inspection(body, out_dir, previous_path=previous_inspection)
    specimen.write_bundle(body, preset, out_dir)
    return body

