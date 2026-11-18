"""Spencer OoT alto C: what the pocketed chamber of the workshop photos does to the first cavity mode.

    python Analizes_ocarinas/Spencer_OoT_12h/internal_cavity_check.py

The workshop photos (images/11 and images/12) show thick walls and a thumb-face half that is hollow only in three
pockets: one under each thumb hole and one under the window. The tail third of that half is solid clay.
This script builds a voxel model of the body from the measured outline and compares the first standing-wave
mode of several chambers, with the add-on's own solver (ocarina_addon/cavity_mode_solver.py, all holes closed):

  uniform        one shell of even thickness, with the same air volume as the pocketed chamber
  solid tail     the same, but the thumb-face half is solid past the last pocket
  pockets, low   three pockets, the walls between them half as high as the half is deep
  pockets, full  three pockets, the walls between them reach the joint plane (as images/12 shows)

It is a model of what the photos show, not a measurement of the instrument. Assumed, not measured: the depth of
the pockets, the wall at the two playing faces, elliptical sections, a thickness of 45 mm.
Reads measure_output.json. Writes internal_cavity_check.md and images/13_cavity_model.png.
Needs numpy, scipy and matplotlib.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "ocarina_addon"))
import cavity_mode_solver as cms  # noqa: E402

H = 1.25                      # grid, mm
AIR_TARGET = 70.0             # cm3, the working value of ceramic_volume_check.md section 1
F6 = 1396.91
T_MM = 45.0                   # body thickness: the working value of ceramic_volume_check.md section 1
# Read on images/12 (thumb-face mould), as fractions of the body length from the bulb end:
POCKETS = ((0.04, 0.18), (0.21, 0.42), (0.44, 0.65))      # under the left thumb, under the window, under the right thumb
# Read on images/11 and images/12, fired sizes for a 165 mm body:
WALL_SIDE = 7.0               # wall at the joint plane (the scored band): 6-8 mm, up to 12 mm at the tail
WALL_FACE = 5.0               # wall at the finger face: assumed
WALL_FLOOR = 4.0              # wall at the floor of a pocket: about 3 mm at the thumb holes
RHO = (1.9, 2.3)              # fired clay, g/cm3
MOUTHPIECE_G = 45.0


def build_outer(j):
    L = j["length_mm"]
    st = np.array(j["stations"]) * L
    ap, af = np.array(j["player_half_mm"]), np.array(j["far_half_mm"])
    tw = T_MM / float((ap + af).max())
    xs = np.arange(0.5 * H, L, H)
    ymax = float(max(ap.max(), af.max())) + H
    ys = np.arange(-ymax + 0.5 * H, ymax, H)
    zs = np.arange(-T_MM / 2 - H + 0.5 * H, T_MM / 2 + H, H)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    a_p, a_f = np.interp(X, st, ap), np.interp(X, st, af)
    a = np.where(Y < 0, a_p, a_f)
    b = tw * (a_p + a_f) / 2.0
    with np.errstate(divide="ignore", invalid="ignore"):
        outer = (Y / a) ** 2 + (Z / b) ** 2 < 1.0
    return outer, X, Y, Z, L


def chamber(outer, X, Z, L, kind, wall_uniform=None, scale=1.0):
    """Air mask of one chamber. `scale` multiplies the three walls of the pocketed kinds."""
    pad = np.pad(outer, 1)
    d3 = ndi.distance_transform_edt(pad)[1:-1, 1:-1, 1:-1] * H                    # distance to the outside
    if kind == "uniform":
        return d3 >= wall_uniform
    plan = np.pad(outer.any(axis=2), 1)
    d2 = (ndi.distance_transform_edt(plan)[1:-1, 1:-1] * H)[:, :, None]          # distance to the outline, in plan
    finger = (Z >= 0) & (d3 >= WALL_FACE * scale) & (d2 >= WALL_SIDE * scale)
    thumb = (Z < 0) & (d3 >= WALL_FLOOR * scale) & (d2 >= WALL_SIDE * scale)
    s = X / L
    if kind == "solid tail":
        return finger | (thumb & (s >= POCKETS[0][0]) & (s <= POCKETS[-1][1]))
    in_pocket = np.zeros_like(outer)
    for lo, hi in POCKETS:
        in_pocket |= (s >= lo) & (s <= hi)
    span = (s >= POCKETS[0][0]) & (s <= POCKETS[-1][1])
    if kind == "pockets, full":
        return finger | (thumb & in_pocket)
    if kind == "pockets, low":                                                      # dividing walls reach half the depth
        depth = np.where(thumb, -Z, 0.0)
        half = depth.max(axis=2, keepdims=True) / 2.0
        return finger | (thumb & in_pocket) | (thumb & span & (-Z <= half))
    raise ValueError(kind)


def biggest(mask):
    lab, n = ndi.label(mask)
    if n <= 1:
        return mask
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    return lab == (1 + int(np.argmax(sizes)))


def stats(air, outer, L):
    air = biggest(air)
    f, _, _ = cms.modes_of_mask(air, H, k=2)
    xs = np.where(air.any(axis=(1, 2)))[0]
    v_air = air.sum() * H ** 3 / 1000.0
    v_out = outer.sum() * H ** 3 / 1000.0
    return dict(air=air, v_air=v_air, v_out=v_out, f1=float(f[0]), length=(xs.max() - xs.min() + 1) * H,
                mass=[(v_out - v_air) * r + MOUTHPIECE_G for r in RHO])


def fit(outer, X, Z, L, kind, target):
    """The chamber of this kind whose air volume is nearest the target: the walls are scaled (the wall itself for a uniform shell)."""
    best = None
    grid = np.arange(4.0, 16.01, 0.25) if kind == "uniform" else np.arange(1.0, 3.01, 0.05)
    for g in grid:
        air = biggest(chamber(outer, X, Z, L, kind, wall_uniform=g, scale=g))
        v = air.sum() * H ** 3 / 1000.0
        if best is None or abs(v - target) < abs(best[1] - target):
            best = (g, v)
    return best[0]


def figure(rows, L, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(len(rows), 2, figsize=(11, 2.6 * len(rows)))
    for (name, r), ax in zip(rows, axs):
        air = r["air"]
        nz = air.shape[2]
        below = air[:, :, : nz // 2].any(axis=2)                                    # thumb-face half, seen in plan
        side = air.any(axis=1)                                                       # seen from the player
        ax[0].imshow(below.T, origin="lower", cmap="Blues", extent=(0, L, -1, 1), aspect="auto")
        ax[0].set_title(f"{name}: air in the thumb-face half (plan)", fontsize=9)
        ax[1].imshow(side.T, origin="lower", cmap="Blues", extent=(0, L, -T_MM / 2, T_MM / 2), aspect="auto")
        ax[1].set_title(f"side view; {r['v_air']:.0f} cm³, first mode {r['f1'] / F6:.2f} × F6", fontsize=9)
        for a_ in ax:
            a_.set_yticks([])
            a_.set_xlabel("mm from the bulb end", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def main():
    j = json.load(open(HERE / "measure_output.json"))
    outer, X, Y, Z, L = build_outer(j)
    kinds = ("uniform", "solid tail", "pockets, low", "pockets, full")
    head = ["| Chamber | Walls: joint / finger face / pocket floor, mm | Air cm³ | Chamber length mm | First cavity mode, Hz | ÷ F6 | Mass at 1.9 / 2.3 g/cm³, g |",
            "|---|---|---|---|---|---|---|"]

    def row(name, walls, r):
        return (f"| {name} | {walls} | {r['v_air']:.0f} | {r['length']:.0f} | {r['f1']:.0f} | **{r['f1'] / F6:.2f}** | "
                f"{r['mass'][0]:.0f} / {r['mass'][1]:.0f} |")

    md = ["# Spencer OoT alto C: the pocketed chamber and the first cavity mode (generated by internal_cavity_check.py)", "",
          f"A voxel model ({H} mm grid) of a body with the measured outline, {T_MM:.0f} mm thick, elliptical sections; outer volume "
          f"{outer.sum() * H ** 3 / 1000.0:.0f} cm³. Pockets of the thumb-face half, as fractions of the body length from the bulb end: "
          + ", ".join(f"{a:.2f}–{b:.2f}" for a, b in POCKETS) + ". All holes and the window are closed. "
          f"The pass line of the add-on's desk check is 1.3 × F6. The mass includes a mouthpiece of {MOUTHPIECE_G:.0f} g; the maker states 330 g.", "",
          "## 1. With the walls as read on the photos", "", *head]
    as_read = [("uniform", "6.0 everywhere", stats(chamber(outer, X, Z, L, "uniform", 6.0), outer, L))]
    for kind in kinds[1:]:
        as_read.append((kind, f"{WALL_SIDE:.0f} / {WALL_FACE:.0f} / {WALL_FLOOR:.0f}", stats(chamber(outer, X, Z, L, kind), outer, L)))
    md += [row(*r) for r in as_read]
    md += ["", "These chambers hold about 105 cm³ and the body would weigh about 250 g. Both miss the instrument (about 70 cm³, 330 g): "
           "the real walls are thicker than the band at the joint suggests, or the pockets are shallower than assumed.", "",
           f"## 2. With the walls scaled so that the air is {AIR_TARGET:.0f} cm³", "", *head]
    rows = []
    for kind in kinds:
        g = fit(outer, X, Z, L, kind, AIR_TARGET)
        r = stats(chamber(outer, X, Z, L, kind, wall_uniform=g, scale=g), outer, L)
        walls = f"{g:.2f} everywhere" if kind == "uniform" else f"{WALL_SIDE * g:.1f} / {WALL_FACE * g:.1f} / {WALL_FLOOR * g:.1f}"
        rows.append((kind, walls, r))
        md.append(row(kind, walls, r))
    md += ["", "![model](images/13_cavity_model.png)"]
    text = "\n".join(md) + "\n"
    (HERE / "internal_cavity_check.md").write_text(text, encoding="utf-8")
    figure([(n, r) for n, _, r in rows], L, HERE / "images" / "13_cavity_model.png")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
