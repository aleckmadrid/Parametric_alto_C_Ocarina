"""Sections through the voicing (windway exit, window, labium) of two reference models and of the add-on's P4-80.

    python Analizes_ocarinas/Window_cutout/measure_windows.py

Every model gets the same three pictures, in its own window frame:

    origin   the middle of the windway exit
    c        from the exit to the labium tip (the chord of the window)
    a        across the window
    n        out of the body, square to c and a

    long section   the plane of c and n, on the centre line and at +- a quarter of the window width
    plan           planes square to n, at several depths (n = +1 mm is 1 mm outside the chord)
    cross          planes square to c: at the middle of the window and behind the labium tip

The frames were found by hand on trial sections (the numbers are in MODELS below). Reads the STL files named
there; a model whose file is missing is skipped. The outside was told from the cavity by a ray cast from the middle
of each window. Writes images/sections_<model>.png and frames.json. Needs numpy, trimesh, matplotlib.
"""
from __future__ import annotations

import math
import pathlib
import sys

import numpy as np
import trimesh
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def addon_frame(preset: str, v0: float = 80.0):
    """Window frame of an add-on body: the voicing frame of ocarina_addon/voicing_geo.py, turned to the convention here."""
    from ocarina_addon import cavity_math as cm, kernel_bridge, presets
    cav = cm.Cavity.from_preset(presets.get_preset(preset))
    x, y, z = (np.asarray(v, float) for v in cav.port_frame())
    v = kernel_bridge.kernel().sizing.size_body(v0, params=kernel_bridge.load_params()).voicing
    L = v.window_length_mm
    zc = 0.5 * v.labium_edge_thickness_mm - v.labium_offset_mm           # windway centre above the inner plane
    exit_pt = 0.05 * z - L * x + zc * z
    return dict(exit=exit_pt, c=x, a=y, n=z, length=L, width=v.window_width_mm)


def models():
    out = {}
    nbn = pathlib.Path(r"D:/Users/alexv/Downloads/ocarina-nbn-the-best20210930-25494-14sejhn/RodrigoSC/ocarina-nbn-the-best/NBN-with-holes.STL")
    local = HERE / "models" / "NBN-with-holes.STL"
    nbn = local if local.is_file() else nbn
    E, T = np.array([55.0, 32.5, 13.1]), np.array([55.0, 43.5, 10.45])
    c = unit(T - E)
    out["NBN"] = dict(path=nbn, exit=E, c=c, a=np.array([1.0, 0, 0]), n=unit(np.cross(c, [1.0, 0, 0])), length=float(np.linalg.norm(T - E)), width=9.5,
                      title="NBN (RodrigoSC)")
    ecl = ROOT / "Analizes_ocarinas" / "ECAN3_experimental" / "models" / "eclipse_12h_AC_assembly.stl"
    a = unit([1.0, 1.0, 0.0])
    v = np.array([0.7071, -0.7071, 0.0])
    E = np.array([83.8, 95.1, 0.0]) + 40.3 * np.array([0, 0, 1.0]) + 0.4 * v
    T = np.array([83.8, 95.1, 0.0]) + 49.65 * np.array([0, 0, 1.0]) - 3.3 * v
    c = unit(T - E)
    n = unit(np.cross(a, c))
    n = n if n @ v < 0 else -n
    out["Eclipse"] = dict(path=ecl, exit=E, c=c, a=a, n=n, length=float(np.linalg.norm(T - E)), width=7.0, title="ECAN3 Eclipse alto C")
    f = addon_frame("P4")
    out["P4-80"] = dict(path=ROOT / "addon_out" / "P4-80" / "P4-80.stl", title="Add-on P4-80 (current cut)", **f)
    for suffix, title in (("cone", "P4-80, cone cut, box as it is"), ("coneb", "P4-80, cone cut, box ends at the widest point"),
                          ("shelf", "P4-80, cone cut and top shelf 30°"), ("p10", "P4-80, shelf, windway and stub raised 10°"),
                          ("m4", "P4-80, shelf, windway and stub lowered 4°"), ("p10s7", "P4-80, shelf, windway raised 10°, stub 7°"),
                          ("neck", "P4-80, base neck, cone cut and shelf"), ("neck-m25", "P4-80, base neck, windway lowered 2.5° inside it")):
        out[f"P4-80-{suffix}"] = dict(path=ROOT / "addon_out" / f"P4-80-{suffix}" / f"P4-80-{suffix}.stl", title=title, **f)
    for folder in sorted((ROOT / "addon_out").glob("P4-80-dish-*")) + [ROOT / "addon_out" / "P4-80-neck-smooth"]:   # picture-only variations
        out[folder.name] = dict(path=folder / f"{folder.name}.stl", title=folder.name, **f)
    for folder in sorted((ROOT / "addon_out").glob("P4-80-ellipse-*")) + sorted((ROOT / "addon_out").glob("P4-80-el-*")):   # section 12: validated
        out[folder.name] = dict(path=folder / f"{folder.name}.stl", title=folder.name, **f)
    f125 = addon_frame("P0", 125.0)                                           # the widest window of the ladder: 18.6 x 9.65 mm
    for name in ("P0-125-el-p1", "P0-125-el-mm4"):
        out[name] = dict(path=ROOT / "addon_out" / name / f"{name}.stl", title=name, **f125)
    return out


def cut(mesh, origin, normal, u, v):
    segs = trimesh.intersections.mesh_plane(mesh, normal, origin)
    if len(segs) == 0:
        return np.zeros((0, 2, 2))
    rel = segs - origin
    return np.stack([rel @ u, rel @ v], axis=-1)


def draw(ax, S, color, lw=1.0, label=None):
    for k, (p, q) in enumerate(S):
        ax.plot([p[0], q[0]], [p[1], q[1]], "-", color=color, lw=lw, label=label if k == 0 else None)


def figure(name, m):
    mesh = trimesh.load(m["path"], force="mesh")
    cen = mesh.triangles_center
    keep = np.linalg.norm(cen - (m["exit"] + 0.5 * m["length"] * m["c"]), axis=1) < 45.0
    mesh = mesh.submesh([np.where(keep)[0]], append=True, repair=False)
    E, c, a, n, L, W = m["exit"], unit(m["c"]), unit(m["a"]), unit(m["n"]), m["length"], m["width"]
    fig, axs = plt.subplots(1, 3, figsize=(21, 7.4))
    cols = ["#111111", "#d1495b", "#2e86ab", "#3a7d44", "#b07d00"]

    ax = axs[0]
    for k, off in enumerate((0.0, 0.25 * W, -0.25 * W)):
        draw(ax, cut(mesh, E + off * a, a, c, n), cols[k], 1.3 if k == 0 else 0.7, f"a = {off:+.1f} mm")
    ax.set_xlim(-22, 30); ax.set_ylim(-16, 14)
    ax.set_title(f"{m['title']}: long section (c →, n ↑ = outside)", fontsize=10)

    ax = axs[1]
    for k, d in enumerate((2.0, 1.0, 0.0, -1.0, -2.5)):
        draw(ax, cut(mesh, E + d * n, n, a, c), cols[k], 1.0, f"n = {d:+.1f} mm")
    ax.set_xlim(-14, 14); ax.set_ylim(-12, 26)
    ax.set_title("plan sections (a →, c ↑)", fontsize=10)

    ax = axs[2]
    for k, s in enumerate((0.5 * L, L + 1.5, L + 5.0, L + 10.0)):
        draw(ax, cut(mesh, E + s * c, c, a, n), cols[k], 1.0, f"c = {s:.1f} mm")
    ax.set_xlim(-16, 16); ax.set_ylim(-16, 12)
    ax.set_title("cross sections (a →, n ↑ = outside)", fontsize=10)

    for ax in axs:
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3)
        ax.minorticks_on()
        ax.grid(True, which="minor", lw=0.12)
        ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    (HERE / "images").mkdir(exist_ok=True)
    fig.savefig(HERE / "images" / f"sections_{name}.png", dpi=100)
    plt.close(fig)
    print("written", name)


def main():
    import json
    frames = {k: {q: (np.asarray(v).tolist() if isinstance(v, np.ndarray) else str(v) if isinstance(v, pathlib.Path) else v)
                  for q, v in m.items()} for k, m in models().items()}
    (HERE / "frames.json").write_text(json.dumps(frames, indent=1), encoding="utf-8")       # read by render_windows.py (Blender)
    only = sys.argv[1:]
    for name, m in models().items():
        if only and not any(name.startswith(o) for o in only):
            continue
        if not pathlib.Path(m["path"]).is_file():
            print("skipped (file missing):", name, m["path"])
            continue
        figure(name, m)


if __name__ == "__main__":
    main()
