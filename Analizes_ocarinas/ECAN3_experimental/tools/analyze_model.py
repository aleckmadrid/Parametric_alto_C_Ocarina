"""Volume, wall, hole and bypass analysis of one ocarina STL.

    python Analizes_ocarinas/ECAN3_experimental/tools/analyze_model.py v0n3
    python Analizes_ocarinas/ECAN3_experimental/tools/analyze_model.py oot --stage1-only

Stage 1 (cached in output/<model>/stage1.npz): voxelize, extract the cavity,
internal walls and openings, measure every opening on the mesh.
Stage 2: name the holes (config map), volumes, sub-volumes, the single-volume
kernel back-fit, the cell-network back-fit, the "walls removed"
counterfactual, figures and output/<model>/results.json + report.md.

Needs numpy, scipy, trimesh, scikit-image, matplotlib (see README).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
import tomllib
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT.parents[1] / "kernel"))
import cellnet as cn            # noqa: E402
import ocarina_kernel as ok     # noqa: E402
import voxcav as vc             # noqa: E402

LBL_EXT, LBL_SHELL, LBL_CAV, LBL_WALL, LBL_RESID = 0, 1, 2, 3, 4


def midi_of(name):
    base = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    rest, acc = name[1:], 0
    if rest[0] in "#b":
        acc = 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + base[name[0]] + acc


def load_cfg(model):
    cfg = tomllib.loads((ROOT / "config" / "models.toml").read_text(encoding="utf-8"))
    m = dict(cfg["defaults"])
    m.update(cfg["models"][model])
    return m


def auto_rotation(mesh):
    """Angle about z (deg) that minimises the y extent (puts the thickness on y)."""
    v = mesh.convex_hull.vertices[:, :2]
    best = min(range(0, 180), key=lambda a: np.ptp(v @ np.array([math.sin(math.radians(a)),
                                                                 math.cos(math.radians(a))])))
    # refine to 0.1 deg
    angs = np.arange(best - 1, best + 1, 0.1)
    ext = [np.ptp(v @ np.array([math.sin(math.radians(a)), math.cos(math.radians(a))])) for a in angs]
    return float(angs[int(np.argmin(ext))])


# --------------------------------------------------------------------------- stage 1

def stage1(model, cfg, outdir):
    t0 = time.time()
    rot = cfg.get("rotate_z_deg", 0.0)
    if rot == "auto":
        body0, _ = vc.load_main_body(ROOT / cfg["file"])
        rot = auto_rotation(body0)
    body, bodies = vc.load_main_body(ROOT / cfg["file"], rotate_z_deg=rot)
    h, R = cfg["voxel_mm"], cfg["ball_R_mm"]
    solid, g = vc.voxelize_solid(body, h, pad=R + 3.0)
    print(f"[{model}] grid {g.shape} ({time.time()-t0:.0f}s)")
    ext = vc.exterior_opening(solid, g, R)
    cav, resid, cinfo = vc.extract_cavity(solid, g, ext, cut_radius=cfg["cut_radius_mm"])
    walls = vc.internal_walls(solid, cav, g, r_close=cfg["wall_close_mm"])
    ops, oplab = vc.find_openings(cav, ext, g)
    print(f"[{model}] cavity + walls + {len(ops)} openings ({time.time()-t0:.0f}s)")
    L = np.zeros(g.shape, np.uint8)
    L[solid] = LBL_SHELL
    L[walls] = LBL_WALL
    L[cav] = LBL_CAV
    L[resid & ~cav] = LBL_RESID
    # window = opening nearest the configured hint, else the lowest one (nearest the mouthpiece)
    if "window" in cfg:
        wi = int(np.argmin([np.linalg.norm(o.centroid - np.array(cfg["window"])) for o in ops]))
    else:
        wi = int(np.argmin([o.centroid[2] for o in ops]))
    recs, patches = [], {}
    for i, o in enumerate(ops):
        is_w = i == wi
        r = vc.measure_opening(body, o.centroid, o.normal, is_window=is_w)
        rec = {"id": int(o.label), "is_window": is_w, "patch_centroid": o.centroid.tolist(),
               "patch_normal": o.normal.tolist(), "patch_area_mm2": o.area_mm2, "measured": r.get("ok", False)}
        if r.get("ok"):
            rec.update({k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in r.items()
                        if k not in ("profile",)})
        recs.append(rec)
        patches[f"p{o.label}"] = np.argwhere(oplab == o.label).astype(np.int32)
    np.savez_compressed(outdir / "stage1.npz", L=L, origin=g.origin, h=g.h, **patches)
    meta = {"model": model, "rotate_z_deg": rot, "grid_shape": list(g.shape), "voxel_mm": h,
            "ball_R_mm": R, "mesh_volume_mm3": float(body.volume), "mesh_faces": int(len(body.faces)),
            "mesh_extents_mm": body.extents.tolist(), "mesh_bounds_mm": body.bounds.tolist(),
            "mesh_watertight": bool(body.is_watertight), "mesh_genus": int((2 - body.euler_number) // 2),
            "n_bodies_in_file": len(bodies),
            "other_bodies": [{"volume_mm3": float(b.volume), "extents_mm": b.extents.tolist()} for b in bodies[1:]],
            "cavity_info": cinfo, "openings": recs, "stage1_seconds": time.time() - t0}
    (outdir / "stage1.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    with open(outdir / "openings.txt", "w", encoding="utf-8") as f:
        for r in sorted(recs, key=lambda r: r["patch_centroid"][0]):
            c = r.get("centre", r["patch_centroid"])
            f.write(f"id {r['id']:2d} {'WINDOW ' if r['is_window'] else ''}centre {np.round(c, 1).tolist()} "
                    f"axis {np.round(r.get('axis', r['patch_normal']), 2).tolist()} d_eq {r.get('d_eq', float('nan')):.2f} "
                    f"t {r.get('t', float('nan')):.2f} patch {r['patch_area_mm2']:.1f}\n")
    print((outdir / "openings.txt").read_text(encoding="utf-8"))
    return body


# --------------------------------------------------------------------------- stage 2 helpers

def compute_bores(cav, g, holes):
    """Cavity voxels inside each hole's chimney (incl. inward tubes): radius d/2 + 0.6 mm,
    from 0.6 mm below the inner end (z_in) to 3 mm beyond the rim (z_out)."""
    bores = np.zeros_like(cav)
    bore_idx = {}
    for n, hh in holes.items():
        cen, ax = np.array(hh["centre"]), np.array(hh["axis"])
        z_in, z_out = hh["z_in"], hh["z_out"]
        rad = hh["d_eq"] / 2 + 0.6
        reach = max(abs(z_in), abs(z_out)) + rad + 3
        lo_ = np.maximum(g.index(cen - reach), 0)
        hi_ = np.minimum(g.index(cen + reach) + 1, np.array(cav.shape))
        sl_ = tuple(slice(a, b) for a, b in zip(lo_, hi_))
        ii = np.indices(tuple(hi_ - lo_)).reshape(3, -1).T + lo_
        v = g.world(ii) - cen
        zz = v @ ax
        rr = np.linalg.norm(v - np.outer(zz, ax), axis=1)
        m_ = (zz >= z_in - 0.6) & (zz <= z_out + 3.0) & (rr <= rad)
        sub_ = np.zeros(tuple(hi_ - lo_), bool)
        sub_.reshape(-1)[m_] = True
        sub_ &= cav[sl_]
        bores[sl_] |= sub_
        bore_idx[n] = np.argwhere(sub_) + lo_
    return bores, bore_idx


def segment_subvolumes(cav, h, r_neck, min_core_mm3=40.0):
    """Sub-volumes = parts of the cavity joined only through gaps narrower than 2 r_neck."""
    from skimage.segmentation import watershed
    nz = np.argwhere(cav)
    lo, hi = nz.min(0), nz.max(0) + 1
    sl = tuple(slice(a, b) for a, b in zip(lo, hi))
    c = cav[sl]
    D = vc.edt_mm(c, h)
    lab, n = ndi.label(D > r_neck)
    sizes = ndi.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1)) * h ** 3
    keep = np.nonzero(sizes >= min_core_mm3)[0] + 1
    markers = np.zeros_like(lab)
    for new, old in enumerate(keep, start=1):
        markers[lab == old] = new
    seg = watershed(-D, markers, mask=c)
    full = np.zeros(cav.shape, np.int32)
    full[sl] = seg
    # interfaces (neck areas)
    necks = {}
    for ax in range(3):
        a = np.moveaxis(seg, ax, 0)
        u, v = a[:-1].ravel(), a[1:].ravel()
        m = (u > 0) & (v > 0) & (u != v)
        for p, q in zip(np.minimum(u[m], v[m]), np.maximum(u[m], v[m])):
            necks[(int(p), int(q))] = necks.get((int(p), int(q)), 0) + 1
    necks = {k: cnt * h * h for k, cnt in necks.items()}
    vols = np.bincount(seg.ravel(), minlength=len(keep) + 1)[1:] * h ** 3
    return full, vols, necks


def kernel_predict(V0, Gw, holes, order, c):
    """Single-volume kernel: frequencies of the cumulative fingering."""
    f = []
    for j in range(len(order) + 1):
        op = order[:j]
        G = Gw + sum(holes[n]["G"] for n in op)
        V = V0 - sum(holes[n]["A"] * holes[n]["t"] for n in op)
        f.append(ok.freq(G, V, c))
    return f


def kernel_required_G(V0, Gw, holes, order, targets, c):
    """Hole conductances the single-volume kernel needs to hit every target note."""
    req, Gsum, Vsum = {}, Gw, V0
    for j, n in enumerate(order):
        Vj = Vsum - holes[n]["A"] * holes[n]["t"]
        Gneed = ok.volume_for(1.0, targets[j + 1], c)   # = c^2/(4 pi^2 f^2) per unit G
        Gk = Vj / Gneed - Gsum
        req[n] = Gk
        Gsum += Gk
        Vsum = Vj
    return req


def network_predict(net, Gw_net, holes, order, c, dV=True):
    f, veff, byp, prs = [], [], [], []
    for j in range(len(order) + 1):
        op = {"window": Gw_net}
        for n in order[:j]:
            op[n] = holes[n]["G_net"]
        dvc = {n: holes[n]["A"] * holes[n]["t"] for n in order[j:]} if dV else None
        fr, modes = cn.solve(net, op, c, n_modes=1, dV_closed=dvc)
        f.append(float(fr[0]))
        v_eff, b, pr = cn.participation(net, modes[:, 0])
        prs.append(pr)
        veff.append(v_eff)
        byp.append(b)
    return f, veff, byp, prs


def fit_network_window(net, f0, c, dV_closed=None):
    """Window conductance (kernel-equivalent, mm) that puts the all-closed note at f0."""
    from scipy.optimize import brentq

    def err(Gk):
        Gn = cn.deembed(net, "window", Gk)
        return cn.solve(net, {"window": Gn}, c, n_modes=1, dV_closed=dV_closed)[0][0] - f0
    return brentq(err, 0.2, 60.0, xtol=1e-6)


# --------------------------------------------------------------------------- figures

def fig_faces(L, g, holes, window, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    solid = (L == LBL_SHELL) | (L == LBL_WALL)
    ny = solid.shape[1]
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    ext = [g.origin[0], g.origin[0] + L.shape[0] * g.h, g.origin[2], g.origin[2] + L.shape[2] * g.h]
    for ax, sgn, name in ((axes[0], -1, "face at -y (viewed from -y)"), (axes[1], +1, "face at +y (viewed from +y, mirrored)")):
        s = solid if sgn < 0 else solid[:, ::-1, :]
        hit = s.any(1)
        depth = np.where(hit, s.argmax(1), ny).astype(float) * g.h
        img = np.where(hit, depth, np.nan)
        if sgn > 0:
            img = img[::-1, :]
        ax.imshow(img.T, origin="lower", cmap="gray_r", extent=ext if sgn < 0 else [ext[1], ext[0], ext[2], ext[3]],
                  interpolation="nearest")
        for n, hrec in holes.items():
            c = np.array(hrec["centre"])
            if np.sign(hrec["axis"][1]) != sgn:
                continue
            ax.plot(c[0], c[2], "o", mfc="none", mec="tab:red", ms=hrec["d_eq"] * 2.2)
            ax.annotate(f"{n}\n{hrec['d_eq']:.2f}", (c[0], c[2]), xytext=(6, 6), textcoords="offset points",
                        color="tab:red", fontsize=8)
        if window is not None and np.sign(window["axis"][1]) == sgn:
            c = np.array(window["centre"])
            ax.plot(c[0], c[2], "s", mfc="none", mec="tab:blue", ms=12)
            ax.annotate("window", (c[0], c[2]), xytext=(6, -12), textcoords="offset points", color="tab:blue", fontsize=8)
        ax.set_title(name)
        ax.set_xlabel("x mm")
        ax.set_ylabel("z mm")
    fig.suptitle(f"{title}: depth view (darker = deeper), hole names and d_eq (mm)")
    fig.tight_layout()
    fig.savefig(path, dpi=90)
    plt.close(fig)


def fig_labels(L, g, path, title, seg=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(["white", "0.6", "#8ecae6", "#e76f51", "#ffb703"])
    nz = np.argwhere(L == LBL_CAV)
    lo, hi = nz.min(0), nz.max(0)
    fig, axes = plt.subplots(2, 4, figsize=(22, 11))
    for k, ax in enumerate(axes[0]):
        j = int(lo[1] + (k + 1) * (hi[1] - lo[1]) / 5)
        sl = L[:, j, :]
        e = [g.origin[0], g.origin[0] + L.shape[0] * g.h, g.origin[2], g.origin[2] + L.shape[2] * g.h]
        if seg is None:
            ax.imshow(sl.T, origin="lower", cmap=cmap, vmin=0, vmax=4, extent=e, interpolation="nearest")
        else:
            ax.imshow((sl == LBL_SHELL).T | (sl == LBL_WALL).T, origin="lower", cmap="Greys", alpha=0.6, extent=e)
            s = np.ma.masked_equal(seg[:, j, :], 0)
            ax.imshow(s.T, origin="lower", cmap="tab20", extent=e, interpolation="nearest", alpha=0.85)
        ax.set_title(f"y = {g.origin[1] + j * g.h:.1f}")
    for k, ax in enumerate(axes[1]):
        i = int(lo[0] + (k + 1) * (hi[0] - lo[0]) / 5)
        sl = L[i, :, :]
        e = [g.origin[1], g.origin[1] + L.shape[1] * g.h, g.origin[2], g.origin[2] + L.shape[2] * g.h]
        if seg is None:
            ax.imshow(sl.T, origin="lower", cmap=cmap, vmin=0, vmax=4, extent=e, interpolation="nearest")
        else:
            ax.imshow((sl == LBL_SHELL).T | (sl == LBL_WALL).T, origin="lower", cmap="Greys", alpha=0.6, extent=e)
            s = np.ma.masked_equal(seg[i, :, :], 0)
            ax.imshow(s.T, origin="lower", cmap="tab20", extent=e, interpolation="nearest", alpha=0.85)
        ax.set_title(f"x = {g.origin[0] + i * g.h:.1f}")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=75)
    plt.close(fig)


def fig_modes(net, L, g, mode_list, path, title):
    """Pressure amplitude p/p_window painted on cells, mid-thickness slice, for several fingerings."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    lab = net.labels
    off = net.offset
    j_mid = int(np.argmax((lab > 0).sum(axis=(0, 2))))
    fig, axes = plt.subplots(1, len(mode_list), figsize=(6 * len(mode_list), 6))
    for ax, (label, mode) in zip(np.atleast_1d(axes), mode_list):
        val = np.r_[np.nan, mode][lab[:, j_mid, :]]
        e = [g.origin[0] + off[0] * g.h, g.origin[0] + (off[0] + lab.shape[0]) * g.h,
             g.origin[2] + off[2] * g.h, g.origin[2] + (off[2] + lab.shape[2]) * g.h]
        im = ax.imshow(val.T, origin="lower", cmap="RdYlBu_r", vmin=0, vmax=1.2, extent=e, interpolation="nearest")
        ax.set_title(label)
    fig.colorbar(im, ax=axes, shrink=0.7, label="p / p_window")
    fig.suptitle(title + f" (slice y = {g.origin[1] + (off[1] + j_mid) * g.h:.1f})")
    fig.savefig(path, dpi=80)
    plt.close(fig)


# --------------------------------------------------------------------------- stage 2

def stage2(model, cfg, outdir, imgdir):
    t0 = time.time()
    meta = json.loads((outdir / "stage1.json").read_text(encoding="utf-8"))
    z = np.load(outdir / "stage1.npz")
    L = z["L"]
    g = vc.Grid(origin=z["origin"], h=float(z["h"]), shape=L.shape)
    vv = g.voxel_volume
    c = ok.c_air(cfg["temp_c"]) * 1000.0      # mm/s
    k = cfg["k_end"]
    recs = meta["openings"]
    win = next(r for r in recs if r["is_window"])
    if "holes" not in cfg:
        print(f"[{model}] no hole map in config; stage 2 skipped")
        return None
    # ---- name the holes
    cand = [r for r in recs if not r["is_window"] and r.get("measured")]
    recs_by_id = {r["id"]: r for r in recs}
    holes, used = {}, set()
    for name, pos in cfg["holes"].items():
        dists = [np.linalg.norm(np.array(r["patch_centroid"]) - np.array(pos)) for r in cand]
        i = int(np.argmin(dists))
        if dists[i] > 6.0 or cand[i]["id"] in used:
            raise SystemExit(f"[{model}] cannot map hole {name} (nearest {dists[i]:.1f} mm, id {cand[i]['id']})")
        used.add(cand[i]["id"])
        r = cand[i]
        A, t, d = r["A_min"], r["t"], r["d_eq"]
        holes[name] = {"id": r["id"], "centre": r["centre"], "axis": r["axis"], "d_eq": d, "A": A, "t": t,
                       "t_range": [r["t_min"], r["t_max"]], "G": ok.conductance(A, t, k),
                       "patch_area": r["patch_area_mm2"], "cap_mm3": vc.cap_correction(cfg["ball_R_mm"], d)}
    unmapped = [r["id"] for r in cand if r["id"] not in used]
    order, notes = cfg["order"], cfg["notes"]
    targets = [ok.midi_f(midi_of(n)) for n in notes]
    # ---- volumes
    cav = L == LBL_CAV
    wc = np.array(win["centre"] if win.get("measured") else win["patch_centroid"])
    # bores: cavity voxels inside each hole's chimney (incl. inward tubes), from the inner end to the rim
    for n, hh in holes.items():
        hh["z_in"] = recs_by_id[hh["id"]].get("z_in", -hh["t"])
        hh["z_out"] = recs_by_id[hh["id"]].get("z_out", 0.0)
    bores, bore_idx = compute_bores(cav, g, holes)
    # internal walls = enclosed solid that is deeper than one shell thickness from the outside air
    shell_t = float(np.median([hh["t"] for hh in holes.values() if hh["t"] < 5.0] or [2.0]))
    D_ext = vc.edt_mm((L != LBL_EXT) & (L != LBL_RESID), g.h)
    walls_all = (L == LBL_WALL) & (D_ext > shell_t + 0.4)
    del D_ext
    wlab, nwl = ndi.label(walls_all, structure=np.ones((3, 3, 3), bool))
    idx = np.argwhere(walls_all)
    # voicing structure: wall components reaching within 12 mm of the window
    near_w = np.linalg.norm(g.world(idx) - wc, axis=1) < 12.0
    vlabels = np.unique(wlab[tuple(idx[near_w].T)])
    voicing = np.isin(wlab, vlabels[vlabels > 0])
    # hole tubes / bosses: wall components touching a bore (within 1.5 mm)
    near_b = ndi.binary_dilation(bores, iterations=max(1, int(round(1.5 / g.h))))
    tlabels = np.unique(wlab[near_b & walls_all])
    tubes = np.isin(wlab, tlabels[tlabels > 0]) & ~voicing
    del wlab, near_b
    walls = walls_all & ~voicing & ~tubes            # free walls: septa, fins, pocket covers
    V_air = cav.sum() * vv
    V_walls = float((walls | tubes).sum() * vv)
    V_free, V_tubes = float(walls.sum() * vv), float(tubes.sum() * vv)
    V_voicing = voicing.sum() * vv
    caps = sum(hh["cap_mm3"] for hh in holes.values())
    chim = sum(hh["A"] * hh["t"] for hh in holes.values())
    V0 = V_air + caps                         # capped at the outer rims (kernel V0)
    vols = {"mesh_solid_mm3": meta["mesh_volume_mm3"], "voxel_solid_mm3": float(((L == LBL_SHELL) | (L == LBL_WALL)).sum() * vv),
            "cavity_air_ball_capped_mm3": V_air, "hole_cap_correction_mm3": caps,
            "V0_air_capped_at_outer_rims_mm3": V0, "closed_chimneys_in_V0_mm3": chim,
            "internal_walls_mm3": V_walls, "free_walls_septa_fins_covers_mm3": V_free,
            "hole_tube_and_boss_walls_mm3": V_tubes, "voicing_structure_walls_mm3": V_voicing,
            "shell_thickness_used_mm": shell_t, "bore_air_carved_for_network_mm3": float(bores.sum() * vv),
            "gross_chamber_air_plus_walls_mm3": V0 + V_walls,
            "wall_displacement_pct_of_gross": 100 * V_walls / (V0 + V_walls)}
    # ---- sub-volumes
    seg, svols, necks = segment_subvolumes(cav, g.h, cfg["neck_radius_mm"])
    patches = {r["id"]: z[f"p{r['id']}"] for r in recs}
    def subvol_of(pid):
        p = patches[pid]
        s = seg[tuple(p.T)]
        s = s[s > 0]
        return int(np.bincount(s).argmax()) if len(s) else 0
    for n, hh in holes.items():
        hh["subvolume"] = subvol_of(hh["id"])
    win_sub = subvol_of(win["id"])
    sub = {"neck_radius_mm": cfg["neck_radius_mm"], "volumes_mm3": svols.tolist(),
           "necks_mm2": {f"{a}-{b}": v for (a, b), v in sorted(necks.items())}, "window_in": win_sub,
           "holes_in": {s + 1: [n for n, hh in holes.items() if hh["subvolume"] == s + 1] for s in range(len(svols))}}
    # second, coarser segmentation (gaps < 2 x 4 mm)
    seg4, svols4, necks4 = segment_subvolumes(cav, g.h, 4.0)
    sub4 = {"neck_radius_mm": 4.0, "volumes_mm3": svols4.tolist(),
            "necks_mm2": {f"{a}-{b}": v for (a, b), v in sorted(necks4.items())}}
    for n, hh in holes.items():
        p = patches[hh["id"]]
        s = seg4[tuple(p.T)]
        s = s[s > 0]
        hh["subvolume_8mm"] = int(np.bincount(s).argmax()) if len(s) else 0
    sub4["holes_in"] = {s + 1: [n for n, hh in holes.items() if hh["subvolume_8mm"] == s + 1] for s in range(len(svols4))}
    # ---- placement metrics: local chamber width at the hole, distance to the nearest internal wall
    Dcav = vc.edt_mm(cav, g.h)                              # inscribed radius field of the cavity
    Dwall = vc.edt_mm(~walls, g.h) if walls.any() else None
    for n, hh in holes.items():
        p = patches[hh["id"]]
        cen = g.index(hh["centre"])
        r = int(round(10.0 / g.h))
        lo_ = np.maximum(cen - r, 0)
        hi_ = np.minimum(cen + r + 1, np.array(L.shape))
        win_ = tuple(slice(a, b) for a, b in zip(lo_, hi_))
        hh["local_chamber_diameter"] = float(2.0 * Dcav[win_].max())    # largest ball within 10 mm of the hole
        hh["hole_over_chamber"] = hh["d_eq"] / hh["local_chamber_diameter"]
        hh["dist_to_internal_wall"] = float(Dwall[tuple(p.T)].min()) if Dwall is not None else float("nan")
    del Dcav, Dwall
    # ---- single-volume kernel back-fit
    Gw_k = V0 / ok.volume_for(1.0, targets[0], c)
    f_k = kernel_predict(V0, Gw_k, holes, order, c)
    req = kernel_required_G(V0, Gw_k, holes, order, targets, c)
    # ---- cell network
    cav_net = cav & ~bores                      # chimneys/tubes are neck (kernel G), not network cells
    st6 = ndi.generate_binary_structure(3, 1)

    def attach_voxels(cv, n):
        b = np.zeros_like(cv)
        b[tuple(bore_idx[n].T)] = True
        a = np.argwhere(ndi.binary_dilation(b, st6, iterations=2) & cv)
        return a if len(a) else patches[holes[n]["id"]]

    att = {n: attach_voxels(cav_net, n) for n in holes}
    net = cn.build_cells(cav_net, g.origin, g.h, cell_mm=cfg["cell_mm"])
    cn.attach_opening(net, "window", patches[win["id"]], radius_mm=cfg["attach_mm"])
    for n, hh in holes.items():
        cn.attach_opening(net, n, att[n], radius_mm=cfg["attach_mm"])
        hh["G_net"] = cn.deembed(net, n, hh["G"])
    dvc_all = {n: hh["A"] * hh["t"] for n, hh in holes.items()}
    Gw_n_kernel = fit_network_window(net, targets[0], c, dvc_all)
    Gw_n = cn.deembed(net, "window", Gw_n_kernel)
    f_n, veff, byp, _ = network_predict(net, Gw_n, holes, order, c)
    # geodesic distance window -> each hole through the cavity (cell graph)
    from scipy.sparse.csgraph import dijkstra
    import scipy.sparse as sps
    dd = np.linalg.norm(net.X[net.edges[:, 0]] - net.X[net.edges[:, 1]], axis=1)
    Gr = sps.coo_matrix((np.r_[dd, dd], (np.r_[net.edges[:, 0], net.edges[:, 1]], np.r_[net.edges[:, 1], net.edges[:, 0]])),
                        shape=(net.n, net.n)).tocsr()
    Dw = dijkstra(Gr, directed=False, indices=net.openings["window"][0], min_only=True)
    for n, hh in holes.items():
        cells_h = net.openings[n][0]
        hh["path_from_window_mm"] = float(Dw[cells_h].min())
        hh["straight_from_window_mm"] = float(np.linalg.norm(np.array(hh["centre"]) - np.array(
            win.get("centre", win["patch_centroid"]))))

    # ---- end-correction fit: each model gets the k that minimises the RMS cents (window refitted)
    def holes_at(kk, net_=None):
        out = {}
        for n, hh in holes.items():
            G = ok.conductance(hh["A"], hh["t"], kk)
            out[n] = dict(hh, G=G, G_net=cn.deembed(net_ or net, n, G))
        return out

    def kernel_rms(kk):
        hk = holes_at(kk)
        f = kernel_predict(V0, Gw_k, hk, order, c)
        return float(np.sqrt(np.mean([ok.cents(a, b) ** 2 for a, b in zip(f, targets)])))

    def network_scale(kk, net_=None, Gwk=None):
        net_ = net_ or net
        hk = holes_at(kk, net_)
        Gwk = Gwk if Gwk is not None else fit_network_window(net_, targets[0], c, dvc_all)
        return network_predict(net_, cn.deembed(net_, "window", Gwk), hk, order, c), Gwk

    def network_rms(kk):
        (f, _, _, _), _ = network_scale(kk)
        return float(np.sqrt(np.mean([ok.cents(a, b) ** 2 for a, b in zip(f, targets)])))

    from scipy.optimize import minimize_scalar
    kfit_k = minimize_scalar(kernel_rms, bounds=(0.3, 4.0), method="bounded", options={"xatol": 1e-3}).x
    kfit_n = minimize_scalar(network_rms, bounds=(0.3, 4.0), method="bounded", options={"xatol": 1e-3}).x
    f_k_fit = kernel_predict(V0, Gw_k, holes_at(kfit_k), order, c)
    (f_n_fit, veff_fit, byp_fit, pr_fit), Gw_n_fit = network_scale(kfit_n)
    holes_kfit = holes_at(kfit_n)
    for n in holes:
        holes[n]["G_at_kfit_network"] = holes_kfit[n]["G"]
    # cavity modes, all holes closed, window open
    fr_closed, modes_closed = cn.solve(net, {"window": Gw_n}, c, n_modes=4, dV_closed=dvc_all)
    # mode shapes for figures
    mode_list = []
    for j in (0, len(order) // 2, len(order) - 1, len(order)):
        op = {"window": Gw_n}
        for n in order[:j]:
            op[n] = holes[n]["G_net"]
        fr, md = cn.solve(net, op, c, n_modes=1, dV_closed={n: dvc_all[n] for n in order[j:]})
        mode_list.append((f"{notes[j]}: {fr[0]:.0f} Hz", md[:, 0]))
    # ---- walls-removed counterfactual (same holes, same window conductance)
    cav_nw = cav_net | walls                    # free walls turned into air; tubes and voicing kept
    net_nw = cn.build_cells(cav_nw, g.origin, g.h, cell_mm=cfg["cell_mm"])
    cn.attach_opening(net_nw, "window", patches[win["id"]], radius_mm=cfg["attach_mm"])
    for n, hh in holes.items():
        cn.attach_opening(net_nw, n, attach_voxels(cav_nw, n), radius_mm=cfg["attach_mm"])
    # walls effect evaluated at the network's fitted k, same window conductance in both bodies
    (f_wk, _, _, _), _ = network_scale(kfit_n, net, Gw_n_fit)
    (f_nw, veff_nw, byp_nw, _), _ = network_scale(kfit_n, net_nw, Gw_n_fit)
    hk_fit = holes_at(kfit_k)
    f_k_w = kernel_predict(V0, Gw_k, hk_fit, order, c)
    f_k_nw = kernel_predict(V0 + V_free, Gw_k, hk_fit, order, c)
    # ---- tables
    rows = []
    for j, nname in enumerate(notes):
        rows.append({"note": nname, "target_hz": targets[j], "opened": order[j - 1] if j else "-",
                     "kernel_hz": f_k[j], "kernel_cents": ok.cents(f_k[j], targets[j]),
                     "network_hz": f_n[j], "network_cents": ok.cents(f_n[j], targets[j]),
                     "kernel_kfit_cents": ok.cents(f_k_fit[j], targets[j]),
                     "network_kfit_cents": ok.cents(f_n_fit[j], targets[j]),
                     "V_eff_mm3": veff_fit[j], "V_eff_over_V0": veff_fit[j] / net.V.sum(), "bypassed_share": byp_fit[j],
                     "participation_ratio": pr_fit[j],
                     "nowalls_network_cents": ok.cents(f_nw[j], targets[j]),
                     "walls_effect_network_cents": ok.cents(f_wk[j], f_nw[j]),
                     "walls_effect_kernel_cents": ok.cents(f_k_w[j], f_k_nw[j])})
    rms = lambda key: float(np.sqrt(np.mean([r[key] ** 2 for r in rows])))
    Aw, tw, dw = win.get("A_min"), win.get("t"), win.get("d_eq")
    Gw_geom = ok.conductance(Aw, tw, k) if Aw and tw and not math.isnan(tw) else float("nan")
    res = {"model": model, "title": cfg["title"], "frame_rotation_deg": meta["rotate_z_deg"],
           "mesh": {k_: meta[k_] for k_ in ("mesh_volume_mm3", "mesh_faces", "mesh_extents_mm", "mesh_watertight",
                                            "mesh_genus", "n_bodies_in_file", "other_bodies")},
           "volumes": vols, "unmapped_openings": unmapped,
           "window": {"id": win["id"], "centre": win.get("centre", win["patch_centroid"]),
                      "axis": win.get("axis", win["patch_normal"]), "A_outer_mm2": Aw, "d_eq": dw, "t": tw,
                      "G_geom_kernel": Gw_geom, "G_fit_kernel": Gw_k, "G_fit_network_kernel_equiv": Gw_n_kernel,
                      "eta_w_implied_kernel": Gw_k / Gw_geom if Gw_geom == Gw_geom else None},
           "holes": {n: {k_: v for k_, v in hh.items()} for n, hh in holes.items()},
           "kernel_required_G": req, "subvolumes": sub, "subvolumes_8mm": sub4,
           "network": {"cells": int(net.n), "cell_mm": cfg["cell_mm"], "V_cells_mm3": float(net.V.sum()),
                       "closed_modes_hz": fr_closed.tolist(),
                       "first_cavity_mode_over_top_note": float(fr_closed[1] / targets[-1])},
           "k_fit": {"kernel": float(kfit_k), "network": float(kfit_n), "network_window_G_at_kfit": float(Gw_n_fit)},
           "scale": rows, "rms_cents": {"kernel": rms("kernel_cents"), "network": rms("network_cents"),
                                        "kernel_kfit": rms("kernel_kfit_cents"), "network_kfit": rms("network_kfit_cents")},
           "range_ratio_measured": sum(hh["G"] for hh in holes.values()) / Gw_k,
           "seconds": time.time() - t0}
    (outdir / "results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    # ---- figures
    window_rec = {"centre": res["window"]["centre"], "axis": res["window"]["axis"]}
    fig_faces(L, g, holes, window_rec, imgdir / f"{model}_faces.png", cfg["title"])
    fig_labels(L, g, imgdir / f"{model}_labels.png",
               f"{cfg['title']}: grey shell | blue cavity air | red internal walls | yellow air outside the cavity")
    fig_labels(L, g, imgdir / f"{model}_subvolumes.png",
               f"{cfg['title']}: sub-volumes joined through gaps < {2*cfg['neck_radius_mm']:.0f} mm", seg=seg)
    fig_modes(net, L, g, mode_list, imgdir / f"{model}_modes.png", f"{cfg['title']}: Helmholtz mode shape")
    write_report(res, outdir / "report.md")
    print((outdir / "report.md").read_text(encoding="utf-8"))
    return res


def write_report(res, path):
    v = res["volumes"]
    L = [f"# {res['title']}", "",
         f"Generated by `tools/analyze_model.py {res['model']}`. Lengths mm, volumes mm³, conductances mm.", "",
         "## Volumes", "", "| Quantity | mm³ |", "| --- | --- |"]
    for k_, val in v.items():
        L.append(f"| {k_} | {val:,.1f} |")
    w = res["window"]
    L += ["", "## Window", "",
          f"outer aperture {w['A_outer_mm2'] or float('nan'):.1f} mm², d_eq {w['d_eq'] or float('nan'):.2f}, t {w['t'] or float('nan'):.2f}; "
          f"G_geom {w['G_geom_kernel']:.3f}; G fitted (kernel) {w['G_fit_kernel']:.3f}; G fitted (network) {w['G_fit_network_kernel_equiv']:.3f}", "",
          "## Holes", "",
          "| Hole | sub-vol (5 / 8 mm) | x | y | z | d_eq | t | local chamber Ø | d/chamber | to wall | path / straight from window | G (k 0.8) | G required (single volume) | ratio |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for n, hh in res["holes"].items():
        req = res["kernel_required_G"].get(n, float("nan"))
        cx, cy, cz = hh["centre"]
        L.append(f"| {n} | {hh['subvolume']} / {hh['subvolume_8mm']} | {cx:.1f} | {cy:.1f} | {cz:.1f} | {hh['d_eq']:.2f} | {hh['t']:.2f} | "
                 f"{hh['local_chamber_diameter']:.1f} | {hh['hole_over_chamber']:.2f} | {hh['dist_to_internal_wall']:.1f} | "
                 f"{hh['path_from_window_mm']:.0f} / {hh['straight_from_window_mm']:.0f} | "
                 f"{hh['G']:.3f} | {req:.3f} | {hh['G']/req:.2f} |")
    for key in ("subvolumes", "subvolumes_8mm"):
        s = res[key]
        L += ["", f"## Sub-volumes (gaps < {2*s['neck_radius_mm']:.0f} mm separate them)", "",
              "| # | mm³ | holes |", "| --- | --- | --- |"]
        for i, vol in enumerate(s["volumes_mm3"], start=1):
            hl = s["holes_in"].get(i, s["holes_in"].get(str(i), []))
            L.append(f"| {i} | {vol:,.0f} | {', '.join(hl)} |")
        L += ["", "Neck (interface) areas mm²: " + (", ".join(f"{k_}: {a:.0f}" for k_, a in s["necks_mm2"].items()) or "none")]
    kf = res["k_fit"]
    L += ["", "## Scale: single-volume kernel vs cell network (window fitted to the lowest note)", "",
          f"Columns at the prior k = 0.80, then at each model's own best-fit k (kernel {kf['kernel']:.2f}, network {kf['network']:.2f}). "
          "Participation ratio (1 = uniform pressure), V_eff/V (driven air relative to the bulk pressure), bypassed share (air below half the bulk pressure) and the walls effect are at the network's fitted k.", "",
          "| Note | opened | target Hz | kernel k0.8 | network k0.8 | kernel k_fit | network k_fit | participation | V_eff/V | bypassed | walls effect, network | walls effect, kernel |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in res["scale"]:
        L.append(f"| {r['note']} | {r['opened']} | {r['target_hz']:.1f} | {r['kernel_cents']:+.1f} | {r['network_cents']:+.1f} | "
                 f"{r['kernel_kfit_cents']:+.1f} | {r['network_kfit_cents']:+.1f} | "
                 f"{r['participation_ratio']:.3f} | {r['V_eff_over_V0']:.3f} | {100*r['bypassed_share']:.1f} % | {r['walls_effect_network_cents']:+.1f} | {r['walls_effect_kernel_cents']:+.1f} |")
    n = res["network"]
    rc = res["rms_cents"]
    L += ["", f"RMS cents: kernel {rc['kernel']:.1f} / network {rc['network']:.1f} at k 0.8; "
          f"kernel {rc['kernel_kfit']:.1f} / network {rc['network_kfit']:.1f} at fitted k. "
          f"Range ratio ΣG/G_w (measured holes, k 0.8, kernel window) {res['range_ratio_measured']:.2f}.",
          f"Network: {n['cells']} cells of {n['cell_mm']} mm. Closed-hole modes (Hz): "
          + ", ".join(f"{x:.0f}" for x in n["closed_modes_hz"])
          + f"; first cavity mode / top note = {n['first_cavity_mode_over_top_note']:.2f}."]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--stage1-only", action="store_true")
    ap.add_argument("--redo-stage1", action="store_true")
    a = ap.parse_args()
    cfg = load_cfg(a.model)
    outdir = ROOT / "output" / a.model
    imgdir = ROOT / "images"
    outdir.mkdir(parents=True, exist_ok=True)
    imgdir.mkdir(exist_ok=True)
    if a.redo_stage1 or not (outdir / "stage1.npz").exists():
        stage1(a.model, cfg, outdir)
    if not a.stage1_only:
        stage2(a.model, cfg, outdir, imgdir)


if __name__ == "__main__":
    main()
