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
