"""Sections of the owner's sample (body, neck, wind cut). Run with python -I after sample.py."""
import site
import sys

site.addsitedir(site.getusersitepackages())
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

out = sys.argv[1]
parts = {n: trimesh.load(f"{out}/sample_part{k}.stl", force="mesh") for n, k in (("body", 0), ("neck", 1), ("wind", 2), ("tip", 3))}
col = {"body": "#111111", "neck": "#2e86ab", "wind": "#d1495b", "tip": "#d1495b"}


def cut(mesh, origin, normal, u, v):
    segs = trimesh.intersections.mesh_plane(mesh, np.array(normal, float), np.array(origin, float))
    if len(segs) == 0:
        return np.zeros((0, 2, 2))
    rel = segs - np.array(origin, float)
    return np.stack([rel @ np.array(u, float), rel @ np.array(v, float)], axis=-1)


fig, axs = plt.subplots(1, 3, figsize=(24, 9))
ax = axs[0]                                                   # long section through the wind cut: y right, z up
for n, m in parts.items():
    for p, q in cut(m, (27.92, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)):
        ax.plot([p[0], q[0]], [p[1], q[1]], "-", color=col[n], lw=1.0)
ax.set_title("x = 27.92 (through the wind cut): y →, z ↑")
ax.set_xlim(-8, 46); ax.set_ylim(8, 72)
ax = axs[1]                                                   # front: section at y through the neck middle: x right, z up
for yy, ls in ((22.0, "-"), (28.0, "--")):
    for n, m in parts.items():
        for p, q in cut(m, (0, yy, 0), (0, 1, 0), (1, 0, 0), (0, 0, 1)):
            ax.plot([p[0], q[0]], [p[1], q[1]], ls, color=col[n], lw=0.9)
ax.set_title("y = 22 (solid) and y = 28 (dashed): x →, z ↑")
ax.set_xlim(-30, 70); ax.set_ylim(0, 72)
ax = axs[2]                                                   # neck cross-sections at several heights: x right, y up
for zz, c in ((36, "#111111"), (42, "#d1495b"), (50, "#2e86ab"), (58, "#3a7d44"), (64, "#b07d00")):
    for n in ("neck", "wind", "body"):
        S = cut(parts[n], (0, 0, zz), (0, 0, 1), (1, 0, 0), (0, 1, 0))
        for k, (p, q) in enumerate(S):
            ax.plot([p[0], q[0]], [p[1], q[1]], "-" if n != "body" else ":", color=c, lw=1.0, label=f"z = {zz}" if (k == 0 and n == "neck") else None)
ax.set_title("sections at z = 36 … 64: x →, y ↑ (body dotted)")
ax.set_xlim(-12, 62); ax.set_ylim(0, 44)
ax.legend(fontsize=8)
for ax in axs:
    ax.set_aspect("equal"); ax.grid(True, lw=0.3); ax.minorticks_on(); ax.grid(True, which="minor", lw=0.12)
fig.tight_layout()
fig.savefig(f"{out}/sample_sections.png", dpi=80)
print("ok")
