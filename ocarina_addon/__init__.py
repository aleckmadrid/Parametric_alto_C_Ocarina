"""Parametric Ocarina: Blender 5.1 extension that generates printable ocarina test bodies.

The acoustic kernel (kernel/, standard-library Python) is the source of every number. This package
builds the geometry: the cavity (Geometry Nodes), the voicing, the holes, the wall and the checks.

Use it in three ways:
    operators        Object > Parametric Ocarina, or the Ocarina sidebar (build, calibrate, inspect)
    Python API       from ocarina_addon import api          (inside Blender)
    headless         blender -b --factory-startup --python ocarina_addon/headless.py -- <command> ...
"""

bl_info = {                     # read only by legacy add-on loading; the extension uses blender_manifest.toml
    "name": "Parametric Ocarina",
    "blender": (5, 1, 0),
    "category": "Object",
}

try:
    import bpy  # noqa: F401
    _IN_BLENDER = True
except ImportError:             # the pure-Python modules (cavity_math, presets, kernel_bridge) work without Blender
    _IN_BLENDER = False

if _IN_BLENDER:
    from . import operators

    def register():
        operators.register()

    def unregister():
        operators.unregister()
