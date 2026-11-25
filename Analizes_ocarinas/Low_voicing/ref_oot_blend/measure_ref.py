"""Measure the owner's low-voicing reference ("Ocarina of time Blender.blend", 2026-11-20) on its own meshes.

    python Analizes_ocarinas/Low_voicing/ref_oot_blend/measure_ref.py

Reads models/oot_blend_meshes.npz (the three objects of the blend file, exported as they are and evaluated) and
models/oot_blend_outer.npz (the body with its subdivision but before the two Boolean cuts). Both are made from the
blend file by Blender and are not in git (third-party model). Writes measure_ref.json and images/ref_*.png.

Frame of the file: x = body length (bulb at -x, tail at +x), y = thickness (thumb face at +y, finger deck at -y),
z = toward the player (the mouthpiece points to +z). Needs numpy, trimesh (with manifold3d), matplotlib.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import trimesh

HERE = pathlib.Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
IMG = HERE / "images"


def load():
    d = np.load(HERE / "models" / "oot_blend_meshes.npz")
    o = np.load(HERE / "models" / "oot_blend_outer.npz")
    mk = lambda V, F: trimesh.Trimesh(np.asarray(V, float), np.asarray(F), process=True)      # noqa: E731
    return dict(body=mk(d["Ocarina Body|eval|V"], d["Ocarina Body|eval|F"]),
                cavity=mk(d["Ocarina Body Cavity|eval|V"], d["Ocarina Body Cavity|eval|F"]),
                pipe=mk(d["Pipe Boolean|eval|V"], d["Pipe Boolean|eval|F"]), outer=mk(o["V"], o["F"]))


def segments(mesh, origin, normal, u, v):
    """The cut of a mesh with a plane, as (n, 2, 2) segments in the plane's (u, v) coordinates."""
    V = mesh.vertices
    d = (V - origin) @ normal
    d[np.abs(d) < 1e-9] = 1e-9
    F = mesh.faces
    pos = d[F] > 0
    out = []
    for f in F[pos.any(axis=1) & ~pos.all(axis=1)]:
        s = d[f]
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if (s[a] > 0) != (s[b] > 0):
                t = s[a] / (s[a] - s[b])
                p = V[f[a]] + t * (V[f[b]] - V[f[a]]) - origin
                pts.append((p @ u, p @ v))
        if len(pts) == 2:
            out.append(pts)
    return np.array(out, float)


def section_plot(M, origin, normal, u, v, path, title, extent=None, extra=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    fig, ax = plt.subplots(figsize=(12, 8))
    for key, col, lw in (("outer", "#bbbbbb", 0.8), ("body", "#222222", 1.4), ("cavity", "#2f6fd0", 1.0), ("pipe", "#d0602f", 1.2)):
        S = segments(M[key], origin, normal, u, v)
        if len(S):
            ax.add_collection(LineCollection(S, colors=col, linewidths=lw, label=key))
    for pts, col, lab in (extra or []):
        P = np.asarray(pts)
        ax.plot(P[:, 0], P[:, 1], "o-", color=col, ms=3, lw=1, label=lab)
    ax.set_aspect("equal")
    if extent:
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
    else:
        ax.autoscale()
    ax.grid(True, lw=0.3)
    ax.legend(loc="best", fontsize=8)
    ax.set_title(title, fontsize=10)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def main():
    IMG.mkdir(exist_ok=True)
    M = load()
    X, Y, Z = np.eye(3)
    res = {}
    for k, m in M.items():
        res[k] = dict(watertight=bool(m.is_watertight), volume_mm3=float(m.volume), bounds=[m.bounds[0].round(3).tolist(), m.bounds[1].round(3).tolist()])
    for name, pair in (("air_capped_at_outer_skin_mm3", ("cavity", "outer")), ("windway_in_body_mm3", ("pipe", "outer"))):
        try:                                   # the cavity mesh of the file is not a closed volume for every tool
            res[name] = float(trimesh.boolean.intersection([M[pair[0]], M[pair[1]]], engine="manifold").volume)
        except ValueError as exc:
            res[name] = None
            res[name + "_note"] = f"no Boolean: {exc}; the air is measured on the voxel grid instead (run_analysis.py)"
    res["plastic_mm3"] = float(M["body"].volume)
    pc = M["pipe"].vertices.mean(axis=0)
    res["pipe_centroid"] = pc.round(3).tolist()
    # ---- sections
    px = float(0.5 * (M["pipe"].bounds[0][0] + M["pipe"].bounds[1][0]))
    section_plot(M, np.array([px, 0, 0.0]), X, Y, Z, IMG / "ref_section_across_pipe.png",
                 f"Cut across the body through the middle of the pipe (x = {px:.1f}): y = thickness (thumb face right), z = toward the player")
    section_plot(M, np.array([px, 0, 0.0]), X, Y, Z, IMG / "ref_section_across_pipe_close.png",
                 "The same, close on the voicing", extent=(0, 32, -5, 45))
    for zc in (0.0, 10.0, 20.0):
        section_plot(M, np.array([0, 0, zc]), Z, X, Y, IMG / f"ref_section_plan_z{zc:+.0f}.png",
                     f"Cut at z = {zc:+.0f} (seen from the player): x = length, y = thickness (thumb face up)")
    section_plot(M, np.array([0, 0, 0.0]), Y, X, Z, IMG / "ref_section_mid_thickness.png",
                 "Cut at mid thickness (y = 0): x = length, z = toward the player")
    import measure_details
    res.update(measure_details.details(M))
    (HERE / "measure_ref.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
