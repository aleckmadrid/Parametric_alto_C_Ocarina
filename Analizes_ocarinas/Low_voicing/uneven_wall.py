"""An uneven wall: thin on the finger deck, thick on the thumb face (series 3, owner's request of 2026-11-24).

The owner's words: "consider having uneven thickness in a test with the volume shifted to the front so the face holes
are less thick and there is more play on the back". The chamber is not changed: the outside is drawn at a distance
from it that depends on which way the surface faces,

    wall(n) = wall_at_holes - wall_front_less_mm * s(n_z)   on the deck half   (n_z > 0)
            = wall_at_holes + wall_back_more_mm * s(-n_z)   on the thumb half  (n_z < 0),      s(x) = x^2 (3 - 2 x)

so the sides keep the rule's wall and the change is smooth. The body is then finished by the add-on's shell-edit
build (body.build_body with `outer`), which measures the wall at every hole and sizes each hole for the chimney it
really has. The window keeps the wall of the voicing rule: its cutter makes the dish through whatever plastic stands
above it. No add-on file is changed; build_body is wrapped from outside.

Around the window the extra thickness of the back fades to nothing as a smooth dish (9 mm of land, then a run of
2.5 times the extra thickness), so the window sits in a hollow of the thick wall as on the ceramic instruments.

Preset keys: wall_front_less_mm, wall_back_more_mm, wall_ramp_oval_mm ([length, width] of the oval ramp scoop, or a dict
with len, wid, shift, floor for the oval with a rim and a level floor; see skin()), wall_ramp_ellipsoid_mm (cut_ellipsoid()),
wall_back_no_dish (no hollow at all: the add-on's own window cut goes through the thicker wall; the owner's choice of 2026-11-25),
and formerly wall_back_no_dish (the first build, kept to show why the dish is there).
"""
from __future__ import annotations

import numpy as np

from ocarina_addon import body as body_mod, kernel_bridge, meshutil, shell_edit

LAST: dict = {}


DISH_LAND_MM = 9.0        # around the window's middle the wall keeps the rule's thickness this far out
CHANNEL_LAND_MM = 7.5     # half the width of the channel's floor toward the player (the neck's foot is 12.7 mm half wide)
DISH_RUN_PLAYER = 2.0     # the same on the player's side (steepest slope about 37 deg)
DISH_RUN = 2.5            # and reaches the thick wall over this many times the extra thickness (steepest slope about 31 deg)


def skin(cav, wall, front_less, back_more, window=None, oval=None):
    """window: (centre, jet direction, normal) of the window. The extra thickness of the back fades to nothing toward it, as a
    smooth dish: the first build (s3-u2) left the thick wall standing inside the 45 deg flare of the window."""
    cV, cF = np.asarray(cav.V, float), np.asarray(cav.F, np.int64)
    n = meshutil.vertex_normals(cV, cF)
    splits = 0 if window is None or back_more <= 0.0 else int(oval.get("splits", 1)) if isinstance(oval, dict) else 1
    for _ in range(splits):
        # every triangle split in four: on the chamber's own grid the walls of the dish came out in steps
        e = np.sort(np.concatenate([cF[:, [0, 1]], cF[:, [1, 2]], cF[:, [2, 0]]]), axis=1)
        ue, inv = np.unique(e, axis=0, return_inverse=True)
        mid = len(cV) + inv.reshape(3, -1).T                              # per triangle: the new points on edges 01, 12, 20
        mn = n[ue[:, 0]] + n[ue[:, 1]]
        n = np.vstack([n, mn / np.linalg.norm(mn, axis=1)[:, None]])
        cV = np.vstack([cV, 0.5 * (cV[ue[:, 0]] + cV[ue[:, 1]])])
        a, b, c = cF.T
        cF = np.vstack([np.column_stack([a, mid[:, 0], mid[:, 2]]), np.column_stack([mid[:, 0], b, mid[:, 1]]),
                        np.column_stack([mid[:, 2], mid[:, 1], c]), mid])
    nz = np.clip(n[:, 2], -1.0, 1.0)
    s = lambda x: x * x * (3.0 - 2.0 * x)          # noqa: E731
    more = back_more * s(np.maximum(-nz, 0.0))
    if window is not None and back_more > 0.0:
        # A round dish cut into the body above the voicing and around the foot of the neck, and a channel under the
        # neck did the same (the owner, 2026-11-25: "the dish should not cut above the upper of the voicing window,
        # that is what is causing the bad finish"). So the dish ends at the window's edge on the player's side: there
        # its land is half the window's length and 0.5 mm, and the wall is full again 2 mm per mm of extra further on.
        # Toward the labium it keeps its 9 mm of land; in between the land and the run change with the direction.
        c, fx, fz, half = window
        c, fx, fz = (np.asarray(a, float) for a in (c, fx, fz))
        d = cV - c
        along = d @ fx                                  # positive toward the labium, negative toward the player
        across = np.linalg.norm(d - np.outer(along, fx) - np.outer(d @ fz, fz), axis=1)
        if oval is not None:
            # The owner dropped the dish (2026-11-25: "drop the dish just work on the window ramp shape to mirror this
            # or the spencer"). On the references the window stands at the neck's end of one long oval scoop that
            # runs on from the labium ramp. So: an oval that begins on the line of the window's upper edge, `oval[0]`
            # long toward the labium and `oval[1]` wide, in which the extra wall rises smoothly from nothing at its
            # middle line to all of it at its rim. Nothing is taken above the window's upper edge.
            if isinstance(oval, dict):
                # The second form (the owner, 2026-11-25: "the scoop is giving really inconsistent results, aim for the
                # mre oval window of the first image"): the game render shows an oval with a clear rim and a level
                # floor, long along the body. len: along the jet, wid: along the body, shift: its middle moved along
                # the body (+ toward the tail), floor: the share of its radius that is level floor.
                a, b = 0.5 * float(oval["len"]), 0.5 * float(oval["wid"])
                fy = np.cross(fz, fx)
                fy = fy * (np.sign(fy[0]) or 1.0)                       # toward the tail
                side = d @ fy - float(oval.get("shift", 0.0))
                x = along + half - a - float(oval.get("start", 0.0))       # start: the oval's player end against the window's upper edge
                rho = np.sqrt((x / a) ** 2 + (side / b) ** 2)
                if oval.get("rim") is not None:
                    # The dish as its own shape (the owner, 2026-11-25: "the window and the dish being separate, allowing
                    # to different windows with smothing applied"): a level floor everywhere inside, and a rim of a set
                    # width in millimetres all round, its profile with no kink at either end (a quintic step).
                    grad = np.sqrt((x / a ** 2) ** 2 + (side / b ** 2) ** 2) / np.maximum(rho, 1e-9)
                    dist = (rho - 1.0) / np.maximum(grad, 1e-9)            # about the distance to the oval's edge, inside negative
                    u = np.clip(1.0 + dist / float(oval["rim"]), 0.0, 1.0)
                    rise = u * u * u * (u * (6.0 * u - 15.0) + 10.0)
                else:
                    f0 = float(oval.get("floor", 0.55))
                    rise = s(np.clip((rho - f0) / (1.0 - f0), 0.0, 1.0))
            else:
                a, b = 0.5 * float(oval[0]), 0.5 * float(oval[1])
                rise = s(np.clip(((along + half - a) / a) ** 2 + (across / b) ** 2, 0.0, 1.0))
            w = wall - front_less * s(np.maximum(nz, 0.0)) + more * rise
            return cV + w[:, None] * n, cF.copy(), w
        r = np.hypot(along, across)
        t = (0.5 * (1.0 - along / np.maximum(r, 1e-9))) ** 2          # 0 toward the labium, 1 toward the player
        land = DISH_LAND_MM + (half + 0.5 - DISH_LAND_MM) * t
        run = (DISH_RUN + (DISH_RUN_PLAYER - DISH_RUN) * t) * back_more
        hollow = 1.0 - s(np.clip((r - land) / run, 0.0, 1.0))
        # and strictly: no hollow above the line of the window's upper edge; it begins there and is whole
        # DISH_RUN_PLAYER times the extra thickness further toward the labium
        hollow = hollow * s(np.clip((along + half) / (DISH_RUN_PLAYER * back_more), 0.0, 1.0))
        more = more * (1.0 - hollow)
    w = wall - front_less * s(np.maximum(nz, 0.0)) + more
    return cV + w[:, None] * n, cF.copy(), w


def cut_ellipsoid(shell, base, ell):
    """Another way to the oval: a real ellipsoid cut out of the thick shell. ell = dict(len, wid, deep, shift): its
    length along the jet, its width along the body, its vertical half axis, and its middle moved along the body
    (+ toward the tail). Its lowest point touches the plane of the window's outer face, so the wall under it is never
    less than the window's own; toward the player it reaches that plane no nearer than the window's upper edge."""
    v = base.sizing.voicing
    o, fx, fy, fz = (np.asarray(a, float) for a in base.voicing.frame)
    fy = fy * (np.sign(fy[0]) or 1.0)
    L, ww = float(v.window_length_mm), float(v.wall_at_window_mm)
    b, a, rz = 0.5 * float(ell["len"]), 0.5 * float(ell["wid"]), float(ell["deep"])
    c = o + (b - L) * fx + float(ell.get("shift", 0.0)) * fy + (ww + rz) * fz
    nu, nv = 96, 48
    th = np.linspace(0.0, np.pi, nv + 1)[1:-1]
    ph = np.linspace(0.0, 2.0 * np.pi, nu, endpoint=False)
    T, Ph = np.meshgrid(th, ph, indexing="ij")
    P = np.concatenate([np.stack([np.sin(T) * np.cos(Ph), np.sin(T) * np.sin(Ph), np.cos(T)], -1).reshape(-1, 3), [[0, 0, 1.0], [0, 0, -1.0]]])
    eV = c + np.outer(P[:, 0] * b, fx) + np.outer(P[:, 1] * a, fy) + np.outer(P[:, 2] * rz, fz)
    F = []
    for i in range(nv - 2):
        for j in range(nu):
            p, q, r, t = i * nu + j, i * nu + (j + 1) % nu, (i + 1) * nu + (j + 1) % nu, (i + 1) * nu + j
            F += [(p, t, r), (p, r, q)]
    top, bot, last = len(P) - 2, len(P) - 1, (nv - 2) * nu
    for j in range(nu):
        F += [(top, j, (j + 1) % nu), (bot, last + (j + 1) % nu, last + j)]
    eF = np.array(F, np.int64)
    if meshutil.volume(eV, eF) < 0:
        eF = eF[:, ::-1]
    before = meshutil.volume(*shell)
    V, F, _ = meshutil.boolean(shell, (eV, eF), "DIFFERENCE")
    V, F = meshutil.cleanup(V, F, merge_mm=1e-3, no_self_intersection=True)
    rep = meshutil.manifold_report(V, F)
    if not rep["manifold"] or rep["shells"] != 1:
        raise meshutil.GeometryError("the shell with the ellipsoid cut out is not one closed solid")
    LAST["ellipsoid_removed_mm3"] = float(before - meshutil.volume(V, F))
    return V, F


def install():
    plain = body_mod.build_body

    def build_body(preset, v0_cm3, *args, **kw):
        LAST.clear()
        if isinstance(preset, dict) and kw.get("outer") is None and (preset.get("wall_front_less_mm") or preset.get("wall_back_more_mm")):
            P = kw.get("params") if kw.get("params") is not None else kernel_bridge.load_params()
            base = shell_edit.base_parts(preset, v0_cm3, rating=kw.get("rating"), wall_at_window_mm=kw.get("wall_at_window_mm"), params=P,
                                         hole_key=kw.get("hole_key", "print"), body_id=kw.get("body_id"), verbose=False)
            wall = float(P["hole_rules"]["wall_at_holes_mm"])
            f, b = float(preset.get("wall_front_less_mm") or 0.0), float(preset.get("wall_back_more_mm") or 0.0)
            o, fx, fy, fz = (np.asarray(a, float) for a in base.voicing.frame)
            centre = o - 0.5 * float(base.sizing.voicing.window_length_mm) * fx
            V, F, w = skin(base.cavity, wall, f, b, None if preset.get("wall_back_no_dish") else (centre, fx, fz, 0.5 * float(base.sizing.voicing.window_length_mm)),
                           oval=preset.get("wall_ramp_oval_mm"))
            if meshutil.self_intersections(V, F) > 0:
                raise meshutil.GeometryError("the uneven skin intersects itself")
            ell = preset.get("wall_ramp_ellipsoid_mm")
            if ell:
                V, F = cut_ellipsoid((V, F), base, ell)
            LAST.update(front_less_mm=f, back_more_mm=b, wall_least_mm=float(w.min()), wall_most_mm=float(w.max()),
                        shell_cm3=float(meshutil.volume(V, F) / 1000.0), plain_shell_cm3=float(meshutil.volume(*base.shell) / 1000.0))
            kw["outer"] = ((V, F), base.neck)
        return plain(preset, v0_cm3, *args, **kw)

    body_mod.build_body = build_body
