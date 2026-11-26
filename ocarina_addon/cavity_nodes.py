"""The cavity Geometry Nodes group, built from Python so that it is reproducible and versioned.

Two node groups are made:

    "OCA Surface Point"   a function: (theta, phi, 7 width stations, 7 height stations, section exponent,
                          bend) -> point on the unit cavity surface. The formula is the one in
                          cavity_math.py (which is the reference in double precision).
    "OCA Cavity"          the cavity mesh. A grid of (theta, phi) samples is moved onto the surface, the
                          seam and the poles are welded, the mesh is triangulated, translated so that the
                          voicing port is the origin, and scaled about the origin so that the MESH volume
                          equals the target volume (volume = sum over triangles of area * normal . centre / 3,
                          then a cube-root scale).

Because the port is the origin and the scale is about the origin, the voicing port never moves when
the target volume changes. The solved scale is stored on the mesh as the point attribute "oca_scale".

Units: the unit shape has a spine length of cavity_math.LREF (100). The output is in millimetres.
"""
from __future__ import annotations

import math

import bpy

from . import cavity_math

GROUP_NAME = "OCA Cavity"
POINT_GROUP_NAME = "OCA Surface Point"
NODES_VERSION = 1                 # bump when the node graph changes; stored on the group as "oca_version"
MERGE_DISTANCE = 1e-4             # weld distance for the seam and the poles, in unit-shape millimetres

N = cavity_math.N_STATIONS


class _G:
    """Small helper to write node maths as expressions. A value is a socket or a Python number."""

    def __init__(self, tree):
        self.tree = tree
        self._x = 0

    def _new(self, bl_idname):
        node = self.tree.nodes.new(bl_idname)
        self._x += 160
        node.location = (self._x, -120 * (len(self.tree.nodes) % 9))
        return node

    def _set(self, sock, value):
        if isinstance(value, bpy.types.NodeSocket):
            self.tree.links.new(value, sock)
        else:
            sock.default_value = value

    def math(self, op, a, b=None, c=None):
        node = self._new("ShaderNodeMath")
        node.operation = op
        for sock, value in zip(node.inputs, (a, b, c)):
            if value is not None:
                self._set(sock, value)
        return node.outputs[0]

    def add(self, a, b):
        return self.math("ADD", a, b)

    def sub(self, a, b):
        return self.math("SUBTRACT", a, b)

    def mul(self, a, b):
        return self.math("MULTIPLY", a, b)

    def div(self, a, b):
        return self.math("DIVIDE", a, b)

    def combine(self, x, y, z):
        node = self._new("ShaderNodeCombineXYZ")
        for sock, value in zip(node.inputs, (x, y, z)):
            self._set(sock, value)
        return node.outputs[0]

    def separate(self, v):
        node = self._new("ShaderNodeSeparateXYZ")
        self.tree.links.new(v, node.inputs[0])
        return node.outputs[0], node.outputs[1], node.outputs[2]

    def vsub(self, a, b):
        node = self._new("ShaderNodeVectorMath")
        node.operation = "SUBTRACT"
        self.tree.links.new(a, node.inputs[0])
        self.tree.links.new(b, node.inputs[1])
        return node.outputs[0]

    def vscale(self, v, s):
        node = self._new("ShaderNodeVectorMath")
        node.operation = "SCALE"
        self.tree.links.new(v, node.inputs[0])
        self._set(node.inputs["Scale"], s)
        return node.outputs[0]

    def vdot(self, a, b):
        node = self._new("ShaderNodeVectorMath")
        node.operation = "DOT_PRODUCT"
        self.tree.links.new(a, node.inputs[0])
        self.tree.links.new(b, node.inputs[1])
        return node.outputs["Value"]

    def index_switch(self, index, values):
        node = self._new("GeometryNodeIndexSwitch")
        node.data_type = "FLOAT"
        while len(node.index_switch_items) < len(values):
            node.index_switch_items.new()
        self._set(node.inputs[0], index)
        for sock, value in zip(list(node.inputs)[1:1 + len(values)], values):
            self._set(sock, value)
        return node.outputs[0]


def _float_in(tree, name, default, lo=None, hi=None):
    s = tree.interface.new_socket(name=name, in_out="INPUT", socket_type="NodeSocketFloat")
    s.default_value = default
    if lo is not None:
        s.min_value = lo
    if hi is not None:
        s.max_value = hi
    return s


def station_socket_names():
    return [f"Width {k + 1}" for k in range(N)], [f"Height {k + 1}" for k in range(N)]


def _build_point_group():
    """(theta, phi, stations, exponent, bend) -> point on the unit surface. Mirrors cavity_math.Cavity.raw_point."""
    old = bpy.data.node_groups.get(POINT_GROUP_NAME)
    if old is not None:
        bpy.data.node_groups.remove(old)
    tree = bpy.data.node_groups.new(POINT_GROUP_NAME, "GeometryNodeTree")
    wn, hn = station_socket_names()
    _float_in(tree, "Theta", 1.0)
    _float_in(tree, "Phi", 0.0)
    for name in wn + hn:
        _float_in(tree, name, 0.5)
    _float_in(tree, "Section exponent", 2.0, 1.0, 8.0)
    _float_in(tree, "Bend (deg)", 0.0, -90.0, 90.0)
    tree.interface.new_socket(name="Point", in_out="OUTPUT", socket_type="NodeSocketVector")
    gin = tree.nodes.new("NodeGroupInput")
    gout = tree.nodes.new("NodeGroupOutput")
    gin.location, gout.location = (-300, 0), (9000, 0)
    I = gin.outputs
    g = _G(tree)

    theta, phi = I["Theta"], I["Phi"]
    t = g.mul(g.sub(1.0, g.math("COSINE", theta)), 0.5)
    env = g.math("SINE", theta)

    # uniform Catmull-Rom through the 7 stations: segment i = floor(6 t), local s
    x6 = g.mul(g.math("MINIMUM", g.math("MAXIMUM", t, 0.0), 1.0), float(N - 1))
    seg = g.math("MINIMUM", g.math("FLOOR", x6), float(N - 2))
    s = g.sub(x6, seg)
    s2 = g.mul(s, s)
    s3 = g.mul(s2, s)
    node = tree.nodes.new("ShaderNodeMath")          # the Index Switch wants an integer index
    node.operation = "ROUND"
    tree.links.new(seg, node.inputs[0])
    seg_i = node.outputs[0]

    def spline(names):
        v = [I[n] for n in names]
        lo = g.sub(g.mul(v[0], 2.0), v[1])                     # phantom points by linear extrapolation
        hi = g.sub(g.mul(v[N - 1], 2.0), v[N - 2])
        p0 = g.index_switch(seg_i, [lo] + v[:N - 2])
        p1 = g.index_switch(seg_i, v[:N - 1])
        p2 = g.index_switch(seg_i, v[1:])
        p3 = g.index_switch(seg_i, v[2:] + [hi])
        c1 = g.sub(p2, p0)
        c2 = g.sub(g.add(g.mul(p0, 2.0), g.mul(p2, 4.0)), g.add(g.mul(p1, 5.0), p3))
        c3 = g.sub(g.add(g.mul(p1, 3.0), p3), g.add(p0, g.mul(p2, 3.0)))
        return g.mul(0.5, g.add(g.add(g.mul(p1, 2.0), g.mul(c1, s)), g.add(g.mul(c2, s2), g.mul(c3, s3))))

    half = 0.5 * cavity_math.LREF
    a = g.mul(g.mul(spline(wn), env), half)
    b = g.mul(g.mul(spline(hn), env), half)

    e = g.div(2.0, I["Section exponent"])
    cos_p, sin_p = g.math("COSINE", phi), g.math("SINE", phi)
    yy = g.mul(g.mul(g.math("SIGN", cos_p), g.math("POWER", g.math("ABSOLUTE", cos_p), e)), a)
    zz = g.mul(g.mul(g.math("SIGN", sin_p), g.math("POWER", g.math("ABSOLUTE", sin_p), e)), b)

    # spine: circular arc of length LREF in the XY plane; a bend under 1e-6 rad counts as straight
    beta = g.math("RADIANS", I["Bend (deg)"])
    sign = g.sub(1.0, g.mul(2.0, g.math("LESS_THAN", beta, 0.0)))
    beta = g.mul(sign, g.math("MAXIMUM", g.math("ABSOLUTE", beta), 1e-6))
    rho = g.div(cavity_math.LREF, beta)
    psi = g.mul(beta, g.sub(t, 0.5))
    sin_s, cos_s = g.math("SINE", psi), g.math("COSINE", psi)
    cx = g.mul(rho, sin_s)
    cy = g.mul(rho, g.sub(1.0, cos_s))
    px = g.sub(cx, g.mul(yy, sin_s))                  # N = (-sin psi, cos psi, 0)
    py = g.add(cy, g.mul(yy, cos_s))
    tree.links.new(g.combine(px, py, zz), gout.inputs["Point"])
    return tree


def build_cavity_group():
    """Create (or rebuild) the node groups and return "OCA Cavity"."""
    point_tree = _build_point_group()
    old = bpy.data.node_groups.get(GROUP_NAME)
    if old is not None:
        bpy.data.node_groups.remove(old)
    tree = bpy.data.node_groups.new(GROUP_NAME, "GeometryNodeTree")
    tree["oca_version"] = NODES_VERSION
    if hasattr(tree, "is_modifier"):
        tree.is_modifier = True
    wn, hn = station_socket_names()
    tree.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    for name in wn:
        _float_in(tree, name, 1.5 / 2.2, 0.01, 3.0)
    for name in hn:
        _float_in(tree, name, 1.0 / 2.2, 0.01, 3.0)
    _float_in(tree, "Section exponent", 2.0, 1.0, 8.0)
    _float_in(tree, "Bend (deg)", 0.0, -90.0, 90.0)
    _float_in(tree, "Port U", 0.5, 0.02, 0.98)
    _float_in(tree, "Port angle (deg)", 45.0, -180.0, 180.0)
    _float_in(tree, "Target volume (cm3)", 80.0, 0.001, 100000.0)
    for name, default in (("Resolution U", 129), ("Resolution V", 128)):
        s = tree.interface.new_socket(name=name, in_out="INPUT", socket_type="NodeSocketInt")
        s.default_value, s.min_value, s.max_value = default, 8, 1024

    gin = tree.nodes.new("NodeGroupInput")
    gout = tree.nodes.new("NodeGroupOutput")
    gin.location, gout.location = (-300, 0), (6000, 0)
    I = gin.outputs
    g = _G(tree)

    # grid of (theta, phi): X runs 0..pi over "Resolution U" rings, Y runs 0..2 pi over "Resolution V" + 1 columns
    grid = tree.nodes.new("GeometryNodeMeshGrid")
    grid.inputs["Size X"].default_value = 1.0
    grid.inputs["Size Y"].default_value = 1.0
    tree.links.new(I["Resolution U"], grid.inputs["Vertices X"])
    node = tree.nodes.new("FunctionNodeIntegerMath")
    node.operation = "ADD"
    tree.links.new(I["Resolution V"], node.inputs[0])
    node.inputs[1].default_value = 1
    tree.links.new(node.outputs[0], grid.inputs["Vertices Y"])
    pos = tree.nodes.new("GeometryNodeInputPosition")
    gx, gy, _ = g.separate(pos.outputs[0])
    theta = g.mul(g.add(gx, 0.5), math.pi)
    phi = g.mul(g.add(gy, 0.5), 2.0 * math.pi)

    def surface_point(th, ph):
        node = tree.nodes.new("GeometryNodeGroup")
        node.node_tree = point_tree
        g._set(node.inputs["Theta"], th)
        g._set(node.inputs["Phi"], ph)
        for name in wn + hn + ["Section exponent", "Bend (deg)"]:
            tree.links.new(I[name], node.inputs[name])
        return node.outputs["Point"]

    port_theta = g.math("ARCCOSINE", g.sub(1.0, g.mul(2.0, I["Port U"])))
    port_phi = g.math("RADIANS", g.sub(270.0, I["Port angle (deg)"]))
    moved = g.vsub(surface_point(theta, phi), surface_point(port_theta, port_phi))   # the port is the origin

    setpos = tree.nodes.new("GeometryNodeSetPosition")
    tree.links.new(grid.outputs["Mesh"], setpos.inputs["Geometry"])
    tree.links.new(moved, setpos.inputs["Position"])

    merge = tree.nodes.new("GeometryNodeMergeByDistance")
    tree.links.new(setpos.outputs[0], merge.inputs["Geometry"])
    merge.inputs["Distance"].default_value = MERGE_DISTANCE

    flip = tree.nodes.new("GeometryNodeFlipFaces")              # the grid faces point inward after the mapping
    tree.links.new(merge.outputs[0], flip.inputs["Mesh"])

    tri = tree.nodes.new("GeometryNodeTriangulate")
    tree.links.new(flip.outputs[0], tri.inputs["Mesh"])
    try:
        tri.inputs["Quad Method"].default_value = "Fixed"
    except Exception:                                           # older builds: a node property
        if hasattr(tri, "quad_method"):
            tri.quad_method = "FIXED"

    # mesh volume of the unit shape: sum over triangles of area * (normal . centre) / 3
    pos2 = tree.nodes.new("GeometryNodeInputPosition")
    nrm = tree.nodes.new("GeometryNodeInputNormal")
    area = tree.nodes.new("GeometryNodeInputMeshFaceArea")
    contrib = g.div(g.mul(g.vdot(pos2.outputs[0], nrm.outputs[0]), area.outputs[0]), 3.0)
    stat = tree.nodes.new("GeometryNodeAttributeStatistic")
    stat.data_type = "FLOAT"
    stat.domain = "FACE"
    tree.links.new(tri.outputs[0], stat.inputs["Geometry"])
    tree.links.new(contrib, stat.inputs["Attribute"])
    unit_volume = stat.outputs["Sum"]

    target_mm3 = g.mul(I["Target volume (cm3)"], 1000.0)
    scale = g.math("POWER", g.div(target_mm3, unit_volume), 1.0 / 3.0)

    pos3 = tree.nodes.new("GeometryNodeInputPosition")
    scaled = tree.nodes.new("GeometryNodeSetPosition")          # scale about the origin = about the port
    tree.links.new(tri.outputs[0], scaled.inputs["Geometry"])
    tree.links.new(g.vscale(pos3.outputs[0], scale), scaled.inputs["Position"])

    store = tree.nodes.new("GeometryNodeStoreNamedAttribute")
    store.data_type = "FLOAT"
    store.domain = "POINT"
    tree.links.new(scaled.outputs[0], store.inputs["Geometry"])
    store.inputs["Name"].default_value = "oca_scale"
    tree.links.new(scale, store.inputs["Value"])

    tree.links.new(store.outputs[0], gout.inputs["Geometry"])
    return tree


def ensure_cavity_group():
    tree = bpy.data.node_groups.get(GROUP_NAME)
    if tree is None or tree.get("oca_version") != NODES_VERSION or bpy.data.node_groups.get(POINT_GROUP_NAME) is None:
        tree = build_cavity_group()
    return tree


def set_modifier_inputs(modifier, values: dict) -> None:
    """Set node-group inputs of a Geometry Nodes modifier by socket name (Blender 5.1 and 5.2)."""
    tree = modifier.node_group
    by_name = {item.name: item for item in tree.interface.items_tree
               if getattr(item, "item_type", "") == "SOCKET" and item.in_out == "INPUT"}
    for name, value in values.items():
        item = by_name[name]
        value = int(value) if item.socket_type == "NodeSocketInt" else float(value)
        try:
            modifier[item.identifier] = value
        except TypeError:                   # Blender 5.2: "id properties not supported for this type"
            getattr(modifier.properties.inputs, item.identifier).value = value
