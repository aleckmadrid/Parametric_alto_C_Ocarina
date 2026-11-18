"""Partial partitions in an ocarina chamber (US 7,799,980 B1): what the add-on's tools can and cannot say about them.

    python Analizes_ocarinas/Patent_US7799980/partition_check.py

The patent puts a partial partition between the sound hole (the window) and each thumb hole, rising from the
thumb-hole side of the chamber to a little above the mid-line. This script takes the Spencer body model of
../Spencer_OoT_12h/internal_cavity_check.py (70 cm3 of air, solid tail), adds two partitions of several heights
at the stations read on the maker's mould photo, and computes on a voxel grid:

  closed            the first standing-wave mode with every hole closed (the add-on's desk check)
  one thumb open    the lowest resonance with the right thumb hole open and nothing else (window closed)
  both thumbs open  the same with both thumb holes open

An open hole is a column of air through the wall whose outer end is held at zero pressure. That leaves out the
end correction outside the hole and the window, so the frequencies are not notes of the instrument. They are
compared between chambers only: (f / f0)^2 x (V / V0) is how much of the hole's conductance is left.

Nothing here tests the patent's claim, which is about tone in the high register. It is a model of the geometry.
Reads ../Spencer_OoT_12h/measure_output.json. Writes partition_check.md. Needs numpy and scipy.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "Spencer_OoT_12h"))
import internal_cavity_check as icc  # noqa: E402

H = icc.H
C = 347.3
F6 = icc.F6
PARTITIONS = ((0.18, 0.21), (0.42, 0.44))      # stations of the two walls between the pockets (mould photo)
THUMB_R, THUMB_L = 0.54, 0.11                  # stations of the thumb holes (centres of their pockets)
HOLE_D = 12.0
HEIGHTS = (("none", None), ("half the depth of the thumb-face half", -0.5), ("to the mid-line", 0.0),
           ("4 mm above the mid-line", 4.0), ("8 mm above the mid-line", 8.0))


def modes(mask, dirichlet=None, k=3):
    """Lowest k frequencies (Hz). With `dirichlet` (cells held at zero pressure) the first one is the
    Helmholtz resonance through the open holes; without, the uniform mode (0 Hz) is dropped."""
    free = mask if dirichlet is None else mask & ~dirichlet
    idx = -np.ones(mask.shape, dtype=np.int64)
    n = int(free.sum())
    idx[free] = np.arange(n)
    deg = np.zeros(n)
    rows, cols = [], []
    for ax in range(3):
        a = [slice(None)] * 3
        b = [slice(None)] * 3
        a[ax], b[ax] = slice(0, -1), slice(1, None)
        a, b = tuple(a), tuple(b)
        both = mask[a] & mask[b]
        fa, fb = free[a] & both, free[b] & both
        np.add.at(deg, idx[a][fa], 1.0)
        np.add.at(deg, idx[b][fb], 1.0)
        ff = fa & fb
        i, j = idx[a][ff], idx[b][ff]
        rows += [i, j]
        cols += [j, i]
    rows, cols = np.concatenate(rows), np.concatenate(cols)
    A = sp.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n)).tocsr()
    lap = (sp.diags(deg) - A).tocsc()
    kk = k + (1 if dirichlet is None else 0)
    vals = np.sort(spla.eigsh(lap, k=kk, sigma=-1e-3, which="LM")[0])
    if dirichlet is None:
        vals = vals[1:]
    return C * np.sqrt(np.clip(vals, 0, None)) / (H * 1e-3) / (2 * math.pi)


def main():
    j = json.load(open(HERE.parent / "Spencer_OoT_12h" / "measure_output.json"))
    outer, X, Y, Z, L = icc.build_outer(j)
    g = icc.fit(outer, X, Z, L, "solid tail", icc.AIR_TARGET)
    base = icc.biggest(icc.chamber(outer, X, Z, L, "solid tail", scale=g))
    s = X / L
    depth = np.where(base & (Z < 0), -Z, 0.0).max(axis=2, keepdims=True)          # depth of the thumb-face half, per column

    def hole(station):
        r = np.hypot(X - station * L, Y) <= HOLE_D / 2
        col = outer & r & (Z < 0) & ~base
        col &= Z <= Z[base & r].min()                                               # only below the pocket floor
        below = np.zeros_like(outer)
        below[:, :, 1:] = outer[:, :, :-1]
        return col, col & ~below                                                    # the outer end: cells with nothing under them

    hr, er = hole(THUMB_R)
    hl, el = hole(THUMB_L)

    rows = []
    for name, top in HEIGHTS:
        air = base.copy()
        blocked = 0.0
        if top is not None:
            for lo, hi in PARTITIONS:
                slab = (s >= lo) & (s <= hi)
                zt = (-depth * abs(top)) if top < 0 else top
                air &= ~(slab & (Z <= zt))
                mid = np.argmin(np.abs(X[:, 0, 0] / L - 0.5 * (lo + hi)))
                blocked = max(blocked, 1.0 - air[mid].sum() / base[mid].sum())
        air = icc.biggest(air)
        v = air.sum() * H ** 3 / 1000.0
        f_closed = modes(air)[0]
        f_r = modes(air | hr, er)
        f_b = modes(air | hr | hl, er | el)
        rows.append(dict(name=name, v=v, blocked=blocked, f_closed=f_closed, f_r=f_r, f_b=f_b))

    r0 = rows[0]
    md = ["# Partial partitions (US 7,799,980 B1) on the Spencer body model (generated by partition_check.py)", "",
          f"Body model of the Spencer report §7.3: {icc.T_MM:.0f} mm thick, about {icc.AIR_TARGET:.0f} cm³ of air, the thumb-face half solid in the tail. "
          f"Two partitions at {PARTITIONS[0][0]:.2f}–{PARTITIONS[0][1]:.2f} and {PARTITIONS[1][0]:.2f}–{PARTITIONS[1][1]:.2f} of the body length from the bulb end, "
          f"rising from the thumb face. Thumb holes {HOLE_D:.0f} mm, at {THUMB_L:.2f} and {THUMB_R:.2f}. Grid {H} mm.", "",
          "*Blocked* is the share of the chamber's cross-section the larger partition closes. *Conductance left* is "
          "(f / f0)² × (V / V0) against the chamber without partitions: what remains of the open holes' effect on the pitch. "
          "The open-hole frequencies leave out the window and the outer end correction; they only serve the comparison.", "",
          "| Partitions | Air cm³ | Blocked | Closed: first cavity mode ÷ F6 | Right thumb open: lowest resonance, Hz | Conductance left | Both thumbs open: Hz | Conductance left | Both thumbs open: next mode ÷ F6 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        gr = (r["f_r"][0] / r0["f_r"][0]) ** 2 * r["v"] / r0["v"]
        gb = (r["f_b"][0] / r0["f_b"][0]) ** 2 * r["v"] / r0["v"]
        md.append(f"| {r['name']} | {r['v']:.0f} | {r['blocked'] * 100:.0f} % | **{r['f_closed'] / F6:.2f}** | {r['f_r'][0]:.0f} | {gr * 100:.0f} % | "
                  f"{r['f_b'][0]:.0f} | {gb * 100:.0f} % | {r['f_b'][1] / F6:.2f} |")
    text = "\n".join(md) + "\n"
    (HERE / "partition_check.md").write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
