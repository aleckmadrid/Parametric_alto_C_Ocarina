"""First standing-wave (cavity) mode of a closed air mesh, by finite differences on a voxel grid.

This file is a stand-alone script for a Python that has numpy and scipy (system Python or the project
.venv). Blender's own Python has no scipy, so the add-on runs this file in a second process
(ocarina_addon/cavity_mode.py) and reads the JSON it writes. It imports nothing from the add-on.

    python ocarina_addon/cavity_mode_solver.py air_capped.stl --f-top 1396.91 --c 347.3 --json out.json

The method is that of tools/cavity_modes_fd.py, which imports the two functions below:

    voxelize(path, h_mm)       boolean mask of the cube centres inside a closed mesh
    modes_of_mask(mask, h_mm)  lowest cavity-mode frequencies of that mask

The chamber is a rigid, closed cavity: all holes and the window are closed. The script solves
-lap(p) = (2 pi f / c)^2 p with zero normal velocity at the walls. The first eigenvalue is zero (uniform
pressure: the lumped model's assumption); the next one is the first cavity mode. Self-test of the method:
a box is exact, a sphere is 1.0 % low (addon_checks/cavity_modes_fd.md).

It is a desk check, not a measurement. At F6 every hole is open, which moves the mode.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

C_27 = 347.3            # m/s at 27 degC, the project's design temperature


def modes_of_mask(mask: np.ndarray, h_mm: float, k: int = 4, c: float = C_27):
    """Lowest k cavity-mode frequencies (Hz, the zero mode left out) and their shapes, for a boolean air mask."""
    # Only the largest face-connected group of cells: a thin feature (the air of a rounded hole rim) can leave a few
    # cells joined to the rest only at an edge, and each such island is one more zero mode, read as "0 Hz".
    from scipy import ndimage
    lab, count = ndimage.label(mask)
    if count > 1:
        mask = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)
    idx = -np.ones(mask.shape, dtype=np.int64)
    n = int(mask.sum())
    idx[mask] = np.arange(n)
    rows, cols = [], []
    for ax in range(3):
        a = [slice(None)] * 3
        b = [slice(None)] * 3
        a[ax], b[ax] = slice(0, -1), slice(1, None)
        both = mask[tuple(a)] & mask[tuple(b)]
        i, j = idx[tuple(a)][both], idx[tuple(b)][both]
        rows += [i, j]
        cols += [j, i]
    rows, cols = np.concatenate(rows), np.concatenate(cols)
    A = sp.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n)).tocsr()
    lap = sp.diags(np.asarray(A.sum(axis=1)).ravel()) - A          # graph Laplacian = -h^2 lap with Neumann walls
    vals, vecs = spla.eigsh(lap.tocsc(), k=k + 1, sigma=-1e-3, which="LM")
    order = np.argsort(vals)
    vals, vecs = vals[order], vecs[:, order]
    f = c * np.sqrt(np.clip(vals[1:], 0, None)) / (h_mm * 1e-3) / (2 * math.pi)
    return f, vecs[:, 1:], idx


def read_triangles(path):
    """Triangles (n, 3, 3), bounds (lo, hi) and volume (mm3) of a mesh file. Uses trimesh when it is
    installed (any format); otherwise reads a binary STL with numpy."""
    try:
        import trimesh
    except ImportError:
        trimesh = None
    if trimesh is not None:
        mesh = trimesh.load(path, force="mesh")
        lo, hi = mesh.bounds
        return np.asarray(mesh.triangles), np.asarray(lo), np.asarray(hi), float(mesh.volume)
    dtype = np.dtype([("normal", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")])
    with open(path, "rb") as fh:
        fh.seek(80)
        n = int(np.frombuffer(fh.read(4), dtype="<u4")[0])
        tri = np.frombuffer(fh.read(n * dtype.itemsize), dtype=dtype, count=n)["v"].astype(np.float64)
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    vol = float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)
    pts = tri.reshape(-1, 3)
    return tri, pts.min(axis=0), pts.max(axis=0), vol


def voxelize(path, h_mm: float):
    """Boolean mask of the cube centres inside a closed mesh (column parity along z), the mesh volume
    and its bounding-box size."""
    tri, lo, hi, volume = read_triangles(path)
    xs = np.arange(lo[0] + 0.5 * h_mm, hi[0], h_mm)
    ys = np.arange(lo[1] + 0.5 * h_mm, hi[1], h_mm)
    zs = np.arange(lo[2] + 0.5 * h_mm, hi[2], h_mm)
    hits = [[[] for _ in ys] for _ in xs]
    for t in tri:
        (x0, y0), (x1, y1) = t[:, :2].min(axis=0), t[:, :2].max(axis=0)
        i0, i1 = np.searchsorted(xs, x0), np.searchsorted(xs, x1)
        j0, j1 = np.searchsorted(ys, y0), np.searchsorted(ys, y1)
        if i0 == i1 or j0 == j1:
            continue
        a, b, cc = t
        den = (b[1] - cc[1]) * (a[0] - cc[0]) + (cc[0] - b[0]) * (a[1] - cc[1])
        if abs(den) < 1e-12:
            continue
        for i in range(i0, i1):
            for j in range(j0, j1):
                px, py = xs[i], ys[j]
                w0 = ((b[1] - cc[1]) * (px - cc[0]) + (cc[0] - b[0]) * (py - cc[1])) / den
                w1 = ((cc[1] - a[1]) * (px - cc[0]) + (a[0] - cc[0]) * (py - cc[1])) / den
                w2 = 1.0 - w0 - w1
                if w0 >= 0 and w1 >= 0 and w2 >= 0:
                    hits[i][j].append(w0 * a[2] + w1 * b[2] + w2 * cc[2])
    mask = np.zeros((len(xs), len(ys), len(zs)), dtype=bool)
    for i in range(len(xs)):
        for j in range(len(ys)):
            hz = sorted(hits[i][j])
            hz = [z for n, z in enumerate(hz) if n == 0 or z - hz[n - 1] > 1e-6]      # shared edges hit twice
            for z0, z1 in zip(hz[0::2], hz[1::2]):
                mask[i, j, (zs > z0) & (zs < z1)] = True
    return mask, volume, (hi - lo)


def first_mode(path, c: float, grids=(1.5, 2.0)) -> dict:
    """The first cavity mode of the mesh at `path`. The first grid gives the result; the others show how
    much the result depends on the grid."""
    out = {"stl": str(path), "c_m_s": c, "grids": []}
    for h in grids:
        mask, volume, _ = voxelize(path, h)
        f, _, _ = modes_of_mask(mask, h, k=2, c=c)
        out["grids"].append({"grid_mm": h, "cells": int(mask.sum()), "voxel_cm3": float(mask.sum()) * h ** 3 / 1000.0,
                             "f1_hz": float(f[0]), "f2_hz": float(f[1])})
        out["mesh_cm3"] = volume / 1000.0
    out.update({k: out["grids"][0][k] for k in ("grid_mm", "cells", "voxel_cm3", "f1_hz", "f2_hz")})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="First cavity mode of a closed air mesh (finite differences).")
    ap.add_argument("stl", help="closed air mesh in millimetres")
    ap.add_argument("--f-top", type=float, default=1396.91, help="top note in Hz (F6)")
    ap.add_argument("--c", type=float, default=C_27, help="speed of sound in m/s")
    ap.add_argument("--grid", type=float, nargs="+", default=[1.5, 2.0], help="grid sizes in mm; the first gives the result")
    ap.add_argument("--json", help="write the result to this file")
    args = ap.parse_args(argv)
    t0 = time.time()
    res = first_mode(Path(args.stl), args.c, tuple(args.grid))
    res["f_top_hz"] = args.f_top
    res["ratio"] = res["f1_hz"] / args.f_top
    res["seconds"] = time.time() - t0
    res["solver"] = f"numpy {np.__version__}, scipy {__import__('scipy').__version__}, python {sys.version.split()[0]}"
    text = json.dumps(res, indent=1)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
