"""Builds the cavity object from a preset and a target volume (Geometry Nodes, see cavity_nodes.py)."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

import bpy

from . import cavity_math, cavity_nodes, meshutil, presets as presets_mod

RES_U = 129            # rings along the body (theta = 0 .. pi)
RES_V = 128            # segments around the section


@dataclass
class CavityResult:
    preset_id: str
    preset: dict
    target_volume_cm3: float       # volume the mesh was scaled to
    V: np.ndarray                  # vertices, body coordinates (mm); the voicing port is the origin
    F: np.ndarray                  # triangles, outward normals
    volume_cm3: float              # measured mesh volume
    scale: float                   # solved scale (mm per unit-shape mm)
    length_mm: float               # internal length along the spine = cavity_math.LREF * scale
    math: cavity_math.Cavity       # the same surface as plain mathematics, at this scale
    object_name: str = ""
    report: dict = field(default_factory=dict)


def preset_inputs(preset: dict, cav: cavity_math.Cavity, target_volume_cm3: float, res_u: int, res_v: int) -> dict:
    wn, hn = cavity_nodes.station_socket_names()
    values = {n: v for n, v in zip(wn, preset["width"])}
    values.update({n: v for n, v in zip(hn, preset["height"])})
    values.update({"Section exponent": preset["exponent"], "Bend (deg)": preset["bend_deg"],
                   "Port U": cav.port_u, "Port angle (deg)": cav.port_angle_deg,
                   "Target volume (cm3)": target_volume_cm3, "Resolution U": res_u, "Resolution V": res_v})
    return values


def build_cavity(preset, target_volume_cm3: float, *, res_u: int = RES_U, res_v: int = RES_V,
                 name: str | None = None, keep_object: bool = True, collection=None) -> CavityResult:
    """Make the cavity mesh of `preset` (a name or a preset dict) with the given mesh volume.

    The port is snapped to a vertex of the grid, so the origin is a vertex of the mesh. The object keeps
    its Geometry Nodes modifier, so the cavity stays procedural in the .blend file.
    """
    if isinstance(preset, str):
        preset = presets_mod.get_preset(preset)
    pid = preset.get("id", "custom")
    cav = cavity_math.Cavity.from_preset(preset)
    cav.snap_port_to_grid(res_u, res_v)

    tree = cavity_nodes.ensure_cavity_group()
    name = name or f"OCA_cavity_{pid}_{target_volume_cm3:g}"
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    (collection or bpy.context.scene.collection).objects.link(obj)
    mod = obj.modifiers.new("OCA Cavity", "NODES")
    mod.node_group = tree
    cavity_nodes.set_modifier_inputs(mod, preset_inputs(preset, cav, target_volume_cm3, res_u, res_v))
    obj["oca_preset"] = pid
    obj["oca_target_volume_cm3"] = float(target_volume_cm3)

    V, F, attrs = meshutil.evaluated_arrays(obj)
    if len(F) == 0:
        raise meshutil.GeometryError("the cavity node group produced no geometry")
    vol = meshutil.volume(V, F)
    if vol < 0:
        raise meshutil.GeometryError("the cavity mesh has inward normals")
    scale = attrs.get("oca_scale")
    if scale is None:
        raise meshutil.GeometryError("the cavity mesh does not carry the 'oca_scale' attribute")
    cav.scale = scale
    result = CavityResult(preset_id=pid, preset=preset, target_volume_cm3=float(target_volume_cm3), V=V, F=F,
                          volume_cm3=vol / 1000.0, scale=scale, length_mm=cavity_math.LREF * scale, math=cav,
                          object_name=obj.name)
    if not keep_object:
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(mesh)
        result.object_name = ""
    return result
