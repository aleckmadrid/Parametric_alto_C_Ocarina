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
    checks_geo.run_all(body, P, V, F, cavity_mode_step=cavity_mode_step)
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
