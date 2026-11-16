"""First standing-wave (cavity) modes of a closed chamber, by finite differences on a voxel grid.

    python tools/cavity_modes_fd.py                      # self-test, ECAN3 caches, add-on air meshes
    python tools/cavity_modes_fd.py path/to/air.stl ...  # any closed air mesh (mm)

What it is. The chamber is taken as a rigid, closed cavity (all holes and the window closed). The script
solves -lap(p) = (2 pi f / c)^2 p with zero normal velocity at the walls, on a regular grid of cubes cut
from the air mesh. The first eigenvalue is zero (uniform pressure: the lumped model's assumption). The next
one is the first cavity mode: the frequency at which the pressure is no longer uniform along the chamber.

What it is for. The project's cavity-mode rule (doc 03 section 8, R9) uses c/(2L), which is exact only for
a straight pipe. This gives the number for the real shape, so the rule can be checked on the exported air
meshes without an FEM package. It is a desk check, not a measurement.

What it is not. The window and the open holes are closed here. An open window or hole releases pressure,
which moves the mode (the ECAN3 cell network, which keeps the window open, is listed beside this result where
both exist). Walls are rigid and lossless.

Needs numpy, scipy and trimesh (system Python; not Blender).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

ROOT = Path(__file__).resolve().parents[1]
C_27 = 347.3            # m/s at 27 degC, the project's design temperature
F6 = 1396.9


def modes_of_mask(mask: np.ndarray, h_mm: float, k: int = 4, c: float = C_27):
    """Lowest k cavity-mode frequencies (Hz, the zero mode left out) and their shapes, for a boolean air mask."""
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


def voxelize(path: Path, h_mm: float):
    """Boolean mask of the cube centres inside a closed mesh (column parity along z), and the mesh volume."""
    import trimesh
    mesh = trimesh.load(path, force="mesh")
    lo, hi = mesh.bounds
    xs = np.arange(lo[0] + 0.5 * h_mm, hi[0], h_mm)
    ys = np.arange(lo[1] + 0.5 * h_mm, hi[1], h_mm)
    zs = np.arange(lo[2] + 0.5 * h_mm, hi[2], h_mm)
    tri = mesh.triangles                                           # (n, 3, 3)
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
    return mask, float(mesh.volume), (hi - lo)


def longest_line(mask, h_mm):
    """Largest extent of the mask over a set of directions (mm): the L of c/(2L)."""
    pts = np.argwhere(mask) * h_mm
    pts = pts[np.random.default_rng(0).choice(len(pts), min(len(pts), 20000), replace=False)]
    best = 0.0
    for th in np.radians(np.arange(0, 180, 6)):
        for ph in np.radians(np.arange(0, 180, 6)):
            d = np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)])
            s = pts @ d
            best = max(best, float(s.max() - s.min()) + h_mm)
    return best


def self_test():
    """Box and sphere against the exact answers."""
    out = []
    h = 1.0
    box = np.ones((100, 40, 30), dtype=bool)
    f, _, _ = modes_of_mask(box, h, k=2)
    out.append(("box 100 x 40 x 30 mm", f[0], C_27 / (2 * 0.100)))
    r = 25.0
    g = np.arange(-r + 0.5 * h, r, h)
    X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
    f, _, _ = modes_of_mask(X * X + Y * Y + Z * Z < r * r, h, k=2)
    out.append(("sphere, radius 25 mm", f[0], 2.0816 * C_27 / (2 * math.pi * r * 1e-3)))
    return out


def ecan3_mask(model: str, factor: int = 5):
    f = ROOT / "Analizes_ocarinas" / "ECAN3_experimental" / "output" / model / "stage1.npz"
    if not f.exists():
        return None
    z = np.load(f)
    cav = z["L"] == 2
    h = float(z["h"])
    s = [n - n % factor for n in cav.shape]
    c = cav[:s[0], :s[1], :s[2]].reshape(s[0] // factor, factor, s[1] // factor, factor, s[2] // factor, factor)
    return c.mean(axis=(1, 3, 5)) >= 0.5, h * factor, float(cav.sum()) * h ** 3


def row(label, f, L, vol_cm3, note=""):
    cl = C_27 / (2 * L * 1e-3)
    return (f"| {label} | {vol_cm3:.1f} | {L:.0f} | {cl:.0f} | {cl / F6:.2f} | {f[0]:.0f} | **{f[0] / F6:.2f}** | {f[0] / cl:.2f} "
            f"| {f[1]:.0f} | {note} |")


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    lines = ["# Cavity modes of closed chambers (generated by tools/cavity_modes_fd.py)", "",
             "Rigid closed cavity, all holes and the window closed, air at 27 °C (c = 347.3 m/s). F6 = 1396.9 Hz. "
             "L is the longest straight line that fits in the air. c/(2L) is the project's present estimate (doc 03 §8).", "",
             "## Self-test", "", "| Case | This script, Hz | Exact, Hz | Error |", "|---|---|---|---|"]
    for name, got, exact in self_test():
        lines.append(f"| {name} | {got:.0f} | {exact:.0f} | {100 * (got / exact - 1):+.1f} % |")
    hdr = ["", "| Chamber | Air, cm³ | L, mm | c/(2L), Hz | c/(2L) ÷ F6 | First cavity mode, Hz | First mode ÷ F6 | First mode ÷ c/(2L) | Second mode, Hz | Note |",
           "|" + "---|" * 10]
    if not argv:
        lines += ["", "## Reference chambers (ECAN3 voxel caches)"] + hdr
        net = {"oot": 1507.4, "eclipse": 1866.6}
        for model, title in (("oot", "ECAN3 Ocarina of Time v3"), ("eclipse", "ECAN3 Eclipse")):
            r = ecan3_mask(model)
            if r is None:
                lines.append(f"| {title} | – | – | – | – | – | – | – | – | voxel cache not found |")
                continue
            mask, h, vol = r
            f, _, _ = modes_of_mask(mask, h)
            lines.append(row(title, f, longest_line(mask, h), vol / 1000,
                             f"internal walls kept; grid {h:.2f} mm; ECAN3 cell network with the window open: {net[model]:.0f} Hz = {net[model] / F6:.2f} × F6"))
        lines += ["", "## Add-on bodies (exported `*_air_capped.stl`)"] + hdr
        for body in ("P0-80", "P3-80", "P1-80", "P2-80", "P0-125"):
            p = ROOT / "addon_out" / body / f"{body}_air_capped.stl"
            if not p.exists():
                lines.append(f"| {body} | – | – | – | – | – | – | – | – | air mesh not found (run the add-on build) |")
                continue
            res = {}
            for h in (2.0, 1.5):
                mask, vol, ext = voxelize(p, h)
                f, _, _ = modes_of_mask(mask, h)
                res[h] = (f, longest_line(mask, h), mask.sum() * h ** 3 / 1000)
            chk = json.load(open(ROOT / "addon_checks" / f"{body}.json"))
            st = [c for c in chk["checks"] if c["name"] == "cavity_mode"][0]
            f, L, v = res[1.5]
            lines.append(row(body, f, L, v, f"grid 1.5 mm (2.0 mm grid: {res[2.0][0][0]:.0f} Hz); present check: `{st['status']}` at {st['value']:.2f}"))
    else:
        lines += ["", "## Meshes"] + hdr
        for a in argv:
            p = Path(a)
            mask, vol, ext = voxelize(p, 1.5)
            f, _, _ = modes_of_mask(mask, 1.5)
            lines.append(row(p.name, f, longest_line(mask, 1.5), mask.sum() * 1.5 ** 3 / 1000, "grid 1.5 mm"))
    text = "\n".join(lines) + "\n"
    if not argv:
        (ROOT / "addon_checks" / "cavity_modes_fd.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
