"""The voicing shoulder: extra volume of the body around the voicing (EXPERIMENT code of series 3).

The owner, 2026-11-20: "both the third party 3d model and the spencer have a shell that accommodates the voicing
within the shell and from there extends the windway an neck, seems that it has some extra volume around the voicing
area, explore ways to heave this be readly added to the volumes we have when selecting to work with the lowered
voicing".

What the two references have (ref_oot_blend/, cut across the pipe; the Spencer tray and half-shell pictures): at the
station of the mouthpiece the BODY ITSELF reaches further toward the player, chamber and wall together. The section
there is an egg with its narrow end toward the player. The window lies on the thumb-face flank of that egg, well
inside the body's outline, and the pipe and the neck leave from its crown. Our bodies have the same section from end
to end, and everything toward the player is a neck stuck onto it.

What this does: the chamber of any preset gets a shoulder. Around the station of the port, the player-side half of
every section is made wider by up to `height` mm; the wall and the outside follow, because they are the chamber moved
outward. It is one more term in the formula of the surface (cavity_math.Cavity.raw_point), so the port, the frame of
the voicing, the hole layout and every check see the new body, and the chamber is still scaled to its volume.

It is not part of the add-on: it hooks in from outside (install()). A preset without voicing_shoulder_mm is built
by the add-on's own node group, exactly as before. With the key, the node group still makes the mesh, and every
vertex of it is then moved to where the formula with the shoulder puts it (the node group would need the same term
to draw it by itself). The faces are the add-on's own: a mesh of the same points with other diagonals gave a wall
0.3 mm thicker near the tail of P1, because the outside is the chamber moved along its vertex normals.

Preset keys (the body, not the voicing: none of this is hashed)
    voicing_shoulder_mm        how far the player-side edge of the chamber moves out at the port's station (no key = none)
    voicing_shoulder_tail_mm   how far the shoulder runs along the body toward the tail (default 30)
    voicing_shoulder_bulb_mm   ... toward the bulb end (default 20): the reference's root is lopsided this way
    voicing_shoulder_power     1 = the half section is stretched (an egg); above 1 the flanks stay straighter and the
                               crown narrower (a pear). Default 1.3
"""
from __future__ import annotations

import math

import numpy as np

from ocarina_addon import cavity as cavity_mod
from ocarina_addon import cavity_math, meshutil

TAIL_DEFAULT_MM, BULB_DEFAULT_MM, POWER_DEFAULT = 30.0, 20.0, 1.3
LAST = {}


class ShoulderCavity(cavity_math.Cavity):
    """A cavity with a shoulder toward the player around the port's station."""

    shoulder = None                # dict(h, tail, bulb, power), mm; set before the port is placed

    def _bump(self, t: float) -> float:
        sh = self.shoulder
        s_mm = cavity_math.LREF * (t - self._shoulder_t) * self.scale        # along the spine from the port, + toward the tail
        L = sh["tail"] if s_mm >= 0 else sh["bulb"]
        u = abs(s_mm) / L
        return 0.0 if u >= 1.0 else math.cos(0.5 * math.pi * u) ** 2

    def raw_point(self, theta: float, phi: float):
        if not self.shoulder:
            return super().raw_point(theta, phi)
        t = (1.0 - math.cos(theta)) / 2.0
        a, b = self.half_axes_raw(theta)
        e = 2.0 / self.exponent
        yy = cavity_math._spow(math.cos(phi), e) * a
        zz = cavity_math._spow(math.sin(phi), e) * b
        if yy < 0.0 and a > 1e-12:                       # the player-side half (-Y)
            g = self._bump(t)
            if g > 0.0:
                yy -= (self.shoulder["h"] / self.scale) * g * (-yy / a) ** self.shoulder["power"]
        c, _, n = self.spine_raw(t)
        return (c[0] + yy * n[0], c[1] + yy * n[1], c[2] + zz)


def shoulder_from(preset):
    if preset.get("voicing_shoulder_mm") is None:
        return None
    return dict(h=float(preset["voicing_shoulder_mm"]), tail=float(preset.get("voicing_shoulder_tail_mm", TAIL_DEFAULT_MM)),
                bulb=float(preset.get("voicing_shoulder_bulb_mm", BULB_DEFAULT_MM)), power=float(preset.get("voicing_shoulder_power", POWER_DEFAULT)))


def _grid_of(mesh_V, cav, n_u: int, n_v: int):
    """(theta, phi) of every vertex of the add-on's chamber mesh: the grid node of the plain formula nearest to it."""
    nodes, params = [cav.point(0.0, 0.0)], [(0.0, 0.0)]
    for i in range(1, n_u - 1):
        th = math.pi * i / (n_u - 1)
        for j in range(n_v):
            ph = 2.0 * math.pi * j / n_v
            nodes.append(cav.point(th, ph))
            params.append((th, ph))
    nodes.append(cav.point(math.pi, 0.0))
    params.append((math.pi, 0.0))
    nodes = np.array(nodes, float)
    V = np.asarray(mesh_V, float)
    out = np.empty(len(V), np.int64)
    worst = 0.0
    for a in range(0, len(V), 400):
        d = np.linalg.norm(V[a:a + 400, None, :] - nodes[None, :, :], axis=2)
        k = d.argmin(axis=1)
        out[a:a + 400] = k
        worst = max(worst, float(d[np.arange(len(k)), k].max()))
    if worst > 1e-2:
        raise meshutil.GeometryError(f"the chamber mesh does not lie on the grid of the formula (off by {worst:.3f} mm)")
    return [params[k] for k in out]


def install():
    """Hook the shoulder into cavity.build_cavity from outside."""
    if getattr(cavity_mod.build_cavity, "_shoulder", False):
        return
    plain = cavity_mod.build_cavity

    def build_cavity(preset, target_volume_cm3: float, *, res_u: int = cavity_mod.RES_U, res_v: int = cavity_mod.RES_V,
                     name=None, keep_object: bool = True, collection=None):
        from ocarina_addon import presets as presets_mod
        if isinstance(preset, str):
            preset = presets_mod.get_preset(preset)
        sh = shoulder_from(preset)
        if sh is None:
            return plain(preset, target_volume_cm3, res_u=res_u, res_v=res_v, name=name, keep_object=keep_object, collection=collection)
        base = plain(preset, target_volume_cm3, res_u=res_u, res_v=res_v, name=name, keep_object=False, collection=collection)
        grid = _grid_of(base.V, base.math, res_u, res_v)    # the add-on's mesh: its faces are kept, its points are moved
        F = np.asarray(base.F)
        cav = ShoulderCavity.from_preset(preset)
        cav.shoulder = None
        cav.snap_port_to_grid(res_u, res_v)                 # the port's station, on the plain surface
        cav._shoulder_t = (1.0 - math.cos(cav.port_theta)) / 2.0
        plain_cav = cavity_math.Cavity.from_preset(preset)
        scale = base.scale
        for _ in range(8):                                  # the shoulder is given in mm: the scale is found by iteration
            cav.scale = scale
            cav.shoulder = sh
            cav._port_raw = cav.raw_point(cav.port_theta, cav.port_phi)
            V = np.array([cav.point(th, ph) for th, ph in grid], float)
            vol = meshutil.volume(V, F) / 1000.0
            if abs(vol / target_volume_cm3 - 1.0) < 1e-9:
                break
            scale *= (target_volume_cm3 / vol) ** (1.0 / 3.0)
        pid = preset.get("id", "custom")
        plain_cav.scale = scale
        LAST.update(shoulder=dict(sh), scale=float(scale), scale_without=float(base.scale),
                    shoulder_volume_cm3=float(vol - base.volume_cm3 * (scale / base.scale) ** 3))
        return cavity_mod.CavityResult(preset_id=pid, preset=preset, target_volume_cm3=float(target_volume_cm3), V=V, F=F,
                                       volume_cm3=vol, scale=scale, length_mm=cavity_math.LREF * scale, math=cav, object_name="")

    build_cavity._shoulder = True
    cavity_mod.build_cavity = build_cavity
