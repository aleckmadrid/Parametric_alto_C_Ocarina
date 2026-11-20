"""Desk model of the inner walls on the bodies of series 3: what a voxel grid can say about them.

    python Analizes_ocarinas/Low_voicing/walls_desk_model.py [--grid 1.0 1.5] [--only P4]

The method is that of Analizes_ocarinas/Patent_US7799980/partition_check.py, here on the air of each BUILT body
(addon_out/<id>/<id>_air_capped.stl: the chamber, the pocket and every hole up to the outer skin):

  closed            the first standing-wave mode with every hole closed, against the top note F6 (the add-on's own
                    desk check does the same on a 1.5 mm grid; a 2.4 mm wall is thin for that grid, so it is solved
                    again here on 1.0 mm)
  one thumb open    the lowest resonance with one thumb hole open and nothing else (the window closed)
  both thumbs open  the same with both

An open hole is its column of air with the outer end held at zero pressure. That leaves out the end correction
outside the hole and the window, so the frequencies are not notes of the instrument. They are compared between a
walled body and its smooth twin only: (f / f0)^2 x (V / V0) is how much of the hole's conductance is left.

Nothing here tests what the walls are FOR (the tone of the top notes with the large holes open). It sizes their cost.
Writes walls_desk_model.json and walls_desk_model.md. Needs numpy and scipy.
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
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "ocarina_addon"))
import cavity_mode_solver as cms  # noqa: E402

C = cms.C_27
# body: its smooth twin
PAIRS = {"s3-fwr": None, "s3-w25": "s3-fwr", "s3-w38": "s3-fwr", "s3-w50": "s3-fwr", "s3-wL": "s3-fwr", "s3-wR": "s3-fwr",
         "s3-wf": "s3-fwr", "s3-wt16": "s3-fwr", "s3-wt40": "s3-fwr", "s3-fwr30": None, "s3-w30": "s3-fwr30"}


def lowest(mask, h, dirichlet=None, k=2):
    """Lowest frequencies (Hz). With `dirichlet` (cells held at zero pressure) the first is the resonance through
    the open holes; without, the uniform mode (0 Hz) is dropped."""
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
    return C * np.sqrt(np.clip(vals, 0, None)) / (h * 1e-3) / (2 * math.pi)


def biggest(mask):
    """The largest face-connected part (a thin sliver of voxels may hang loose at a hole's edge)."""
    from scipy import ndimage
    lab, n = ndimage.label(mask)
    if n <= 1:
        return mask
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    return lab == (1 + int(np.argmax(sizes)))


def one(pid, trial, h):
    bid = f"{pid}-80-{trial}"
    stl = ROOT / "addon_out" / bid / f"{bid}_air_capped.stl"
    chk = ROOT / "addon_out" / bid / f"{bid}_checks.json"
    if not stl.exists() or not chk.exists():
        return None
    meas = json.loads(chk.read_text(encoding="utf-8"))["measurements"]
    mask, vol, _ = cms.voxelize(str(stl), h)
    mask = biggest(mask)
    _, lo, hi, _ = cms.read_triangles(str(stl))
    gx, gy, gz = (np.arange(lo[k] + 0.5 * h, hi[k], h) for k in range(3))
    P = np.stack(np.meshgrid(gx, gy, gz, indexing="ij"), axis=-1)
    ends = {}
    for r in meas["holes"]:
        if "thumb" not in r["name"]:
            continue
        c, ax = np.asarray(r["centre"], float), np.asarray(r["axis"], float)
        rel = P - c
        t = rel @ ax
        rad = np.linalg.norm(rel - t[..., None] * ax, axis=-1)
        col = mask & (rad <= 0.5 * r["d_measured_mm"]) & (t > 0.5)
        ends[r["name"]] = col & (t > t[col].max() - 1.2 * h)
    f6 = float(meas["cavity_mode"]["f_top_hz"])
    out = dict(body=bid, grid_mm=h, voxel_cm3=float(mask.sum()) * h ** 3 / 1000.0, mesh_cm3=vol / 1000.0, f6_hz=f6,
               f_closed_hz=float(lowest(mask, h)[0]), addon_ratio=float(meas["cavity_mode"]["ratio"]))
    out["closed_ratio"] = out["f_closed_hz"] / f6
    for name, d in (("L", ends["L_thumb"]), ("R", ends["R_thumb"]), ("LR", ends["L_thumb"] | ends["R_thumb"])):
        f = lowest(mask, h, d)
        out[f"f_{name}_open_hz"] = float(f[0])
        out[f"next_{name}_open_ratio"] = float(f[1]) / f6
    return out


def main(argv):
    grids = [float(a) for a in argv[argv.index("--grid") + 1:argv.index("--grid") + 3]] if "--grid" in argv else [1.0]
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else ["P4", "P1"]
    out_json = HERE / "walls_desk_model.json"
    res = json.loads(out_json.read_text(encoding="utf-8")) if out_json.exists() and "--fresh" not in argv else {}
    for pid in only:
        for trial in PAIRS:
            for h in grids:
                r = one(pid, trial, h)
                if r is None:
                    continue
                res[f"{pid}:{trial}@{h:g}"] = r
                print(f"{pid}:{trial} grid {h:g}: closed {r['closed_ratio']:.3f} x F6 (add-on {r['addon_ratio']:.3f}); "
                      f"L {r['f_L_open_hz']:.0f} Hz, R {r['f_R_open_hz']:.0f} Hz, both {r['f_LR_open_hz']:.0f} Hz", flush=True)
    for key, r in res.items():
        pid, rest = key.split(":")
        trial, h = rest.split("@")
        twin = PAIRS[trial]
        r0 = res.get(f"{pid}:{twin}@{h}") if twin else None
        if r0:
            for name in ("L", "R", "LR"):
                r[f"conductance_left_{name}"] = (r[f"f_{name}_open_hz"] / r0[f"f_{name}_open_hz"]) ** 2 * r["voxel_cm3"] / r0["voxel_cm3"]
            r["closed_ratio_twin"] = r0["closed_ratio"]
    if out_json.exists() and "--fresh" not in argv:           # another run may have written meanwhile (one run per body family)
        res = dict(json.loads(out_json.read_text(encoding="utf-8")), **res)
    res = dict(sorted(res.items()))
    out_json.write_text(json.dumps(res, indent=1), encoding="utf-8")
    md = ["# Inner walls on the bodies of series 3: desk model (generated by walls_desk_model.py)", "",
          "Closed: the first standing-wave mode of the built air with every hole closed, against the top note F6 "
          "(1.3 is the add-on's comfortable margin, 1.0 its hard limit). Conductance left: how much of a thumb hole's "
          "effect remains against the smooth twin, with the window closed and no end corrections; a model of the "
          "geometry, not a note. Next mode: the first standing wave with those holes open, against F6.", "",
          "| Body | Grid | Closed ÷ F6 | Smooth twin | Left thumb: conductance left | Right thumb | Both | Both open: next mode ÷ F6 |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for key, r in res.items():
        pc = lambda k: f"{100 * r[k]:.0f} %" if k in r else "–"      # noqa: E731
        md.append(f"| `{key.split('@')[0]}` | {r['grid_mm']:g} mm | {r['closed_ratio']:.2f} | "
                  f"{r.get('closed_ratio_twin', float('nan')):.2f} | {pc('conductance_left_L')} | {pc('conductance_left_R')} | "
                  f"{pc('conductance_left_LR')} | {r['next_LR_open_ratio']:.2f} |")
    (HERE / "walls_desk_model.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
