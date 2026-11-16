"""Hole layouts with a true scale: the two ECAN3 12-hole alto C CAD models, the Miracle and the add-on bodies.

    python Analizes_ocarinas/Ergonomic_reference_12hole/measure_cad_references.py

Why a second script. `measure_reference.py` measures every layout against "the body axis". A photo has no
unique body axis, and the scale of the shared photos is borrowed from the Miracle. This script uses layouts
that have a scale of their own and measures them in a frame the hands define:

    hand axis a   the mean direction of the two hand lines (L pinky -> L index and R index -> R pinky)
    p             perpendicular to a, toward the player

Everything here is independent of how the body is turned in the picture or in the CAD file.

Reads
    the hole centres, axes and diameters of the ECAN3 Ocarina of Time v3 and Eclipse models. They are copied
    below from `Analizes_ocarinas/ECAN3_experimental/output/<model>/results.json` on the branch
    `ecan3-experimental` (commit fd041cb), so the layout metrics need no other file.
    Optional: `Analizes_ocarinas/ECAN3_experimental/output/<model>/stage1.npz` (the voxel cache of that
    analysis, not committed). With it the script also measures the outline: rest space past the pinkies,
    distance to the far edge, outer length and cavity length. Without it those cells show "–".
    The Miracle table and the add-on bodies come from `measure_reference.py`.
Writes
    measure_cad_output.md
    images/11_ecan3_oot_plan.png, images/12_ecan3_eclipse_plan.png   (only with the voxel cache)
Needs numpy; scipy and matplotlib for the outline part.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import measure_reference as mr  # noqa: E402

LEFT, RIGHT = mr.LEFT, mr.RIGHT
FINGERS = LEFT + RIGHT
C_27 = 347.3          # m/s, speed of sound at 27 degC (the project's design temperature)
F6 = 1396.9

# name: (centre [x, y, z] mm, axis, d_eq mm, chimney t mm) in the ECAN3 analysis frame:
# x along the body, y through the two playing faces, z up from the mouthpiece tip (the models stand on it).
ECAN3 = {
    "oot": {
        "L_pinky": ([-45.5, -10.5, 53.5], [-0.319, -0.941, 0.115], 5.08, 3.90),
        "L_ring": ([-29.2, -13.3, 61.2], [-0.217, -0.953, 0.21], 6.57, 2.41),
        "L_middle": ([-13.9, -13.4, 70.5], [-0.112, -0.965, 0.238], 6.26, 3.90),
        "L_index": ([0.1, -11.1, 81.8], [-0.165, -0.864, 0.476], 8.21, 2.41),
        "sub_L": ([-25.0, -14.4, 53.1], [-0.049, -0.989, -0.139], 2.94, 3.97),
        "R_index": ([7.9, -13.4, 64.1], [0.144, -0.974, -0.177], 5.89, 3.92),
        "R_middle": ([22.7, -12.6, 74.3], [0.163, -0.984, -0.071], 3.71, 3.96),
        "R_ring": ([38.1, -10.0, 83.6], [0.2, -0.98, 0.0], 4.79, 3.92),
        "R_pinky": ([54.2, -6.3, 91.7], [0.258, -0.966, 0.019], 3.19, 3.96),
        "sub_R": ([18.5, -13.2, 80.5], [0.072, -0.983, 0.171], 1.72, 3.99),
        "L_thumb": ([-35.9, 11.9, 51.5], [-0.364, 0.911, -0.194], 11.48, 8.44),
        "R_thumb": ([17.8, 11.9, 76.6], [0.122, 0.987, 0.105], 11.86, 2.42),
    },
    "eclipse": {
        "L_pinky": ([-88.3, 16.9, 65.5], [0.194, 0.979, 0.063], 6.10, 6.16),
        "L_ring": ([-104.2, 17.9, 76.0], [0.097, 0.989, 0.115], 8.30, 1.62),
        "L_middle": ([-118.8, 16.9, 87.8], [0.128, 0.941, 0.313], 7.27, 1.61),
        "L_index": ([-131.8, 12.1, 101.6], [0.23, 0.746, 0.625], 7.15, 1.61),
        "sub_L": ([-110.0, 18.4, 67.9], [-0.022, 0.994, -0.105], 4.25, 7.98),
        "R_index": ([-135.1, 14.0, 68.2], [-0.317, 0.775, -0.546], 7.80, 1.69),
        "R_middle": ([-146.6, 16.6, 84.5], [-0.197, 0.957, -0.215], 5.06, 7.90),
        "R_ring": ([-160.1, 15.4, 99.2], [-0.133, 0.991, 0.011], 6.84, 7.81),
        "R_pinky": ([-175.5, 12.8, 111.9], [-0.112, 0.987, 0.118], 5.05, 7.85),
        "sub_R": ([-139.7, 17.8, 89.4], [-0.04, 0.997, 0.065], 3.28, 7.96),
        "L_thumb": ([-96.6, -17.4, 63.2], [0.064, -0.992, -0.105], 9.37, 1.60),
        "R_thumb": ([-149.1, -16.1, 85.4], [-0.246, -0.955, -0.165], 8.77, 1.60),
    },
}
# sx: +1 if the bulb (left hand) is toward -x, -1 if it is toward +x. top: sign of y on the finger face.
# Player view of the finger face: X = sx * x (bulb left, tail right), Yp = -z (the mouthpiece points at the player).
ECAN3_FRAME = {"oot": dict(sx=+1.0, top=-1.0), "eclipse": dict(sx=-1.0, top=+1.0)}
ECAN3_TITLE = {"oot": "ECAN3 Ocarina of Time v3 (CAD)", "eclipse": "ECAN3 Eclipse (CAD)"}
# first closed-hole cavity mode of the cell network, Hz (results.json, network.closed_modes_hz[1])
ECAN3_MODE1 = {"oot": 1507.4, "eclipse": 1866.6}
LBL_SHELL, LBL_CAV, LBL_WALL = 1, 2, 3


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def hand_frame(P):
    """Hand axis a (bulb -> tail) and p (toward the player) from the eight finger holes. P: name -> (X, Yp)."""
    uL = unit(P["L_index"] - P["L_pinky"])
    uR = unit(P["R_pinky"] - P["R_index"])
    a = unit(uL + uR)
    p = np.array([-a[1], a[0]])
    if p[1] < 0:
        p = -p
    return a, p, uL, uR


def hand_metrics(P):
    """Frame-free layout metrics. P: name -> np.array (X along the body from the bulb side, Yp toward the player)."""
    P = {n: np.asarray(v, float)[:2] for n, v in P.items()}
    a, p, uL, uR = hand_frame(P)
    m = {"a": a, "p": p}
    # angle between the two hand lines: + = the lines open toward the tail (fan), 0 = parallel
    m["hands_angle"] = math.degrees(math.atan2(uL[0] * uR[1] - uL[1] * uR[0], uL @ uR))
    m["line_tilt"] = math.degrees(math.acos(max(-1.0, min(1.0, uL @ a))))          # each line against the hand axis
    mid = lambda names: sum(P[n] for n in names) / len(names)
    m["line_offset"] = float((mid(("R_pinky", "R_index")) - mid(("L_pinky", "L_index"))) @ p)   # + = right hand nearer the player
    m["pinky_span"] = float(np.linalg.norm(P["R_pinky"] - P["L_pinky"]))
    v = P["R_index"] - P["L_index"]
    m["index_across"], m["index_along"], m["index_dist"] = float(v @ p), float(v @ a), float(np.linalg.norm(v))
    for hand, names, ext in (("L", LEFT, +1.0), ("R", RIGHT, -1.0)):
        q = [P[n] for n in names]
        u = unit(q[3] - q[0])                       # pinky -> index
        nrm = np.array([-u[1], u[0]])
        if (nrm @ p) * ext < 0:                     # fingertip side: left hand toward the player, right hand away
            nrm = -nrm
        m[hand] = dict(pitches=[float(np.linalg.norm(q[i + 1] - q[i])) for i in range(3)],
                       span=float(np.linalg.norm(q[3] - q[0])),
                       arch=[float((q[i] - q[0]) @ nrm) for i in (1, 2)], u=u, nrm=nrm)
    # subholes: the nearest finger hole of EITHER hand is the parent; the slide is given in the parent's hand frame
    for sub in ("sub_L", "sub_R", "sub1", "sub2"):
        if sub not in P:
            continue
        parent = min(FINGERS, key=lambda n: np.linalg.norm(P[n] - P[sub]))
        hand = parent[0]
        v = P[sub] - P[parent]
        fwd, along = float(v @ m[hand]["nrm"]), float(v @ m[hand]["u"])
        same = min((LEFT if sub in ("sub_L", "sub1") else RIGHT), key=lambda n: np.linalg.norm(P[n] - P[sub]))
        m[sub] = dict(parent=parent, dist=float(np.linalg.norm(v)), forward=fwd, toward_index=along,
                      off_normal_deg=math.degrees(math.atan2(along, fwd)),
                      nearest_same_hand=same, dist_same_hand=float(np.linalg.norm(P[same] - P[sub])))
    # thumbs: position along the hand axis against the finger holes of that hand
    for th, names in (("L_thumb", LEFT), ("R_thumb", RIGHT)):
        if th not in P:
            continue
        s = float(P[th] @ a)
        rel = {n: s - float(P[n] @ a) for n in names}           # + = thumb toward the tail of that finger hole
        nearest = min(names, key=lambda n: abs(rel[n]))
        m[th] = dict(rel=rel, nearest=nearest, across={n: float((P[th] - P[n]) @ p) for n in names})
    return m


# ---------------------------------------------------------------- ECAN3 models

def ecan3_plan(model):
    fr = ECAN3_FRAME[model]
    P, tilt = {}, {}
    for n, (c, ax, d, t) in ECAN3[model].items():
        P[n] = np.array([fr["sx"] * c[0], -c[2]])
        face = fr["top"] if not n.endswith("thumb") else -fr["top"]
        cosang = max(-1.0, min(1.0, face * ax[1]))
        tilt[n] = (math.degrees(math.acos(cosang)), np.array([fr["sx"] * ax[0], -ax[2]]))    # angle, plan direction of the lean
    return P, tilt


def ecan3_outline(model):
    """Silhouette and cavity masks in the player plan (X, Yp), or None without the voxel cache."""
    f = ROOT / "Analizes_ocarinas" / "ECAN3_experimental" / "output" / model / "stage1.npz"
    if not f.exists():
        return None
    z = np.load(f)
    L, o, h = z["L"], z["origin"], float(z["h"])
    solid = ((L == LBL_SHELL) | (L == LBL_WALL) | (L == LBL_CAV)).any(axis=1)      # filled body, projected along y
    cav = (L == LBL_CAV).any(axis=1)
    thick = ((L == LBL_SHELL) | (L == LBL_WALL) | (L == LBL_CAV)).sum(axis=1) * h    # body thickness map (x, z)
    cav_thick = (L == LBL_CAV).sum(axis=1) * h
    sx = ECAN3_FRAME[model]["sx"]

    def native(Pxy):                                    # player plan -> voxel index (i, k)
        x, zc = sx * Pxy[0], -Pxy[1]
        return (x - o[0]) / h - 0.5, (zc - o[2]) / h - 0.5

    def inside(mask, Pxy):
        i, k = native(Pxy)
        i, k = int(round(i)), int(round(k))
        return 0 <= i < mask.shape[0] and 0 <= k < mask.shape[1] and bool(mask[i, k])

    def ray(mask, P0, d, step=0.1, far=400.0):
        """Distance from P0 along d to the last point inside the mask (the far edge along that ray)."""
        d = unit(d)
        s, last = 0.0, 0.0
        while s < far:
            if inside(mask, P0 + s * d):
                last = s
            elif s - last > 6.0:                         # allow a 6 mm gap (a hole mouth), then stop
                break
            s += step
        return last

    def extent(mask, d):
        """Length of the mask along direction d (player plan)."""
        ii, kk = np.nonzero(mask)
        X = sx * (o[0] + (ii + 0.5) * h)
        Y = -(o[2] + (kk + 0.5) * h)
        s = X * d[0] + Y * d[1]
        return float(s.max() - s.min()), float(s.min()), float(s.max())

    def value(arr, Pxy):
        i, k = native(Pxy)
        return float(arr[int(round(i)), int(round(k))])

    return dict(solid=solid, cav=cav, thick=thick, cav_thick=cav_thick, o=o, h=h, sx=sx, inside=inside, ray=ray,
                extent=extent, value=value)


def ecan3_outline_metrics(model, P, m, out):
    a, p = m["a"], m["p"]
    from scipy import ndimage as ndi
    edt = ndi.distance_transform_edt(out["solid"]) * out["h"]
    r = {}
    r["rest_bulb"] = out["ray"](out["solid"], P["L_pinky"], -a)
    r["rest_tail"] = out["ray"](out["solid"], P["R_pinky"], +a)
    r["rest_bulb_any"] = out["value"](edt, P["L_pinky"])           # nearest outline point, any direction
    r["rest_tail_any"] = out["value"](edt, P["R_pinky"])
    r["far_edge"] = {n: out["ray"](out["solid"], P[n], -p) for n in FINGERS}
    r["player_edge"] = {n: out["ray"](out["solid"], P[n], +p) for n in FINGERS}
    r["outer_len"] = out["extent"](out["solid"], a)[0]
    r["cav_len"], s0, s1 = out["extent"](out["cav"], a)
    r["cav_before_L_pinky"] = float(P["L_pinky"] @ a) - s0
    r["cav_after_R_pinky"] = s1 - float(P["R_pinky"] @ a)
    # longest straight line that fits the cavity projection (the standing-wave length is at most this)
    best = max((out["extent"](out["cav"], np.array([math.cos(t), math.sin(t)]))[0], t)
               for t in np.radians(np.arange(0, 180, 2)))
    r["cav_longest"] = best[0]
    r["cav_width"] = out["extent"](out["cav"], p)[0]
    r["cav_thick_max"] = float(out["cav_thick"].max())
    r["body_thick_max"] = float(out["thick"].max())
    r["cav_thick_at"] = {n: out["value"](out["cav_thick"], P[n]) for n in FINGERS}
    return r


def plot_plan(model, P, m, out, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    o, h, sx = out["o"], out["h"], out["sx"]
    nx, nz = out["solid"].shape
    xs = sx * (o[0] + (np.arange(nx) + 0.5) * h)
    ys = -(o[2] + (np.arange(nz) + 0.5) * h)
    fig, ax = plt.subplots(figsize=(9, 7), dpi=110)
    ax.contourf(xs, ys, out["solid"].T.astype(float), levels=[0.5, 1.5], colors=["#d9d2c0"])
    ax.contour(xs, ys, out["cav"].T.astype(float), levels=[0.5], colors=["#3b6ea5"], linewidths=1.0, linestyles="--")
    for n, (c, axv, d, t) in ECAN3[model].items():
        thumb = n.endswith("thumb")
        ax.add_patch(plt.Circle(P[n], d / 2, fc="none" if thumb else "#222", ec="#b00" if thumb else "#222", lw=1.2,
                                ls=":" if thumb else "-"))
        ax.annotate(n, P[n], xytext=(0, 9 if not thumb else -14), textcoords="offset points", ha="center", fontsize=7,
                    color="#b00" if thumb else "#000")
    for names in (LEFT, RIGHT):
        ax.plot(*zip(P[names[0]], P[names[3]]), color="#c60", lw=0.9)
    c0 = sum(P[n] for n in FINGERS) / 8
    ax.annotate("", c0 + 30 * m["a"], c0 - 30 * m["a"], arrowprops=dict(arrowstyle="->", color="#080", lw=1))
    ax.text(*(c0 + 32 * m["a"]), "hand axis", color="#080", fontsize=7)
    ax.set_aspect("equal")
    ax.invert_yaxis()                               # the player is at the bottom of the picture
    ax.invert_yaxis() if ax.get_ylim()[0] < ax.get_ylim()[1] else None
    ax.set_xlabel("mm, bulb (left hand) on the left")
    ax.set_ylabel("mm, toward the player (down)")
    ax.set_title(f"{ECAN3_TITLE[model]}: finger face, player view. Dashed blue: cavity. Dotted red: thumb holes (other face).")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def balance_of(com, r_thumb, tail):
    """Plan-view centre of mass against the line from the right thumb hole to the tail tip (uniform solid)."""
    u = unit(tail - r_thumb)
    n = np.array([-u[1], u[0]])
    if n[1] < 0:
        n = -n
    return float((com - r_thumb) @ u), float((com - r_thumb) @ n), float(np.linalg.norm(tail - r_thumb))


# ---------------------------------------------------------------- report

def f1(v, nd=1):
    return "–" if v is None or (isinstance(v, float) and v != v) else f"{v:.{nd}f}"


def sub_cell(m, key):
    s = m.get(key)
    if not s:
        return "–"
    return f"{s['parent']}, {f1(s['dist'])} mm ({f1(s['forward'])} forward, {f1(s['toward_index'])} toward the index; {f1(s['off_normal_deg'], 0)}° off the line's normal)"


def main():
    rows = []            # (label, P, metrics, outline metrics or None, tilt dict or None)
    mir = {n: np.array(v, float) for n, v in mr.MIRACLE.items()}
    rows.append(("Miracle AO10-AC (photo, catalogue scale)", mir, hand_metrics(mir), None, None))
    plots = []
    for model in ("oot", "eclipse"):
        P, tilt = ecan3_plan(model)
        m = hand_metrics(P)
        out = ecan3_outline(model)
        om = ecan3_outline_metrics(model, P, m, out) if out else None
        if out:
            name = {"oot": "11_ecan3_oot_plan.png", "eclipse": "12_ecan3_eclipse_plan.png"}[model]
            plot_plan(model, P, m, out, HERE / "images" / name)
            plots.append(name)
        rows.append((ECAN3_TITLE[model], P, m, om, tilt))
    land = [("Miracle AO10-AC (along the picture's long axis)", 13.0, 4.5, 32.8, 5.8)]
    for label, P, m, om, tilt in rows[1:]:
        if om:
            d = ECAN3["oot" if "Time" in label else "eclipse"]
            land.append((label + (" (decorative outer body)" if "Eclipse" in label else ""), om["rest_bulb"], d["L_pinky"][2],
                         om["rest_tail"], d["R_pinky"][2]))
    balance = []
    for body in ("P1-80", "P2-80", "P3-80"):
        lay, tl, Lout = mr.addon_layout(body)
        P = {n: np.array(v[:2], float) for n, v in lay.items()}
        H = {h["name"]: h for h in json.load(open(ROOT / "addon_checks" / f"{body}.json"))["measurements"]["holes"]}
        tilt = {}
        for n in FINGERS:                                # body coordinates: +Y is the far side, +Z the finger face
            ax = H[n]["axis"]
            tilt[n] = (math.degrees(math.acos(max(-1.0, min(1.0, ax[2])))), np.array([ax[0], -ax[1]]))
        m = hand_metrics(P)
        centre = mr.presets.get_preset(body.split("-")[0]).get("layout_centre_from_port_mm", 16.0)
        tag = f"built, layout centre {centre:g} mm"
        rows.append((f"Add-on {body} ({tag})", P, m, None, tilt))
        land.append((f"Add-on {body} ({tag}; along the body)", lay["L_pinky"][0], H["L_pinky"]["d_measured_mm"],
                     Lout - lay["R_pinky"][0], H["R_pinky"]["d_measured_mm"]))
        stl = ROOT / "addon_out" / body / f"{body}.stl"
        if stl.exists():
            import trimesh
            mesh = trimesh.load(stl, force="mesh")
            com, V = mesh.center_mass, mesh.vertices
            tail = V[np.argmax(V[:, 0])]
            rt = np.array(H["R_thumb"]["centre"])
            balance.append((f"Add-on {body}", *balance_of(np.array([com[0], -com[1]]), np.array([rt[0], -rt[1]]),
                                                          np.array([tail[0], -tail[1]])), mesh.volume / 1000.0))
    for model in ("oot", "eclipse"):
        f = ROOT / "Analizes_ocarinas" / "ECAN3_experimental" / "output" / model / "stage1.npz"
        if not f.exists():
            continue
        z = np.load(f)
        solid = (z["L"] == LBL_SHELL) | (z["L"] == LBL_WALL)
        o, h, sx = z["origin"], float(z["h"]), ECAN3_FRAME[model]["sx"]
        com = o + (np.argwhere(solid).mean(axis=0) + 0.5) * h
        P, _ = ecan3_plan(model)
        a = hand_metrics(P)["a"]
        ii, kk = np.nonzero(solid.any(axis=1))
        X, Y = sx * (o[0] + (ii + 0.5) * h), -(o[2] + (kk + 0.5) * h)
        j = int(np.argmax(X * a[0] + Y * a[1]))
        balance.append((ECAN3_TITLE[model], *balance_of(np.array([sx * com[0], -com[2]]), P["R_thumb"], np.array([X[j], Y[j]])),
                        float(solid.sum()) * h ** 3 / 1000.0))

    md = ["# Hole layouts with a true scale, in the frame of the hands (generated by measure_cad_references.py)", "",
          "All lengths in mm. Plan view of the finger face as the player sees it. The **hand axis** is the mean direction "
          "of the two hand lines (L pinky → L index, R index → R pinky); *across* means perpendicular to it, + toward the player. "
          "Nothing here depends on how the body is turned.", "",
          "## 1. The two hand lines", "",
          "| Layout | Angle between the hand lines | Each line against the hand axis | Right line nearer the player by | Pinky to pinky | L pitches P→R→M→I | R pitches P→R→M→I | L span | R span | L arch (ring, middle) | R arch (ring, middle) | Index holes: across / along / distance |",
          "|" + "---|" * 12]
    for label, P, m, om, tilt in rows:
        md.append(f"| {label} | {f1(m['hands_angle'])}° | ±{f1(m['line_tilt'])}° | {f1(m['line_offset'])} | {f1(m['pinky_span'])} "
                  f"| {' / '.join(f1(x) for x in m['L']['pitches'])} | {' / '.join(f1(x) for x in m['R']['pitches'])} "
                  f"| {f1(m['L']['span'])} | {f1(m['R']['span'])} | {', '.join(f1(x) for x in m['L']['arch'])} "
                  f"| {', '.join(f1(x) for x in m['R']['arch'])} | {f1(m['index_across'])} / {f1(m['index_along'])} / {f1(m['index_dist'])} |")
    md += ["", "## 2. Subholes", "",
           "The parent is the nearest finger hole of **either** hand. *Forward* is perpendicular to the parent hand's pinky → index line, "
           "on the side its fingertips point to (left hand: toward the player; right hand: away). The last column is what "
           "`measure_reference.py` reports instead: the nearest hole of the hand the subhole was assumed to belong to.", "",
           "| Layout | First subhole (opens B4) | Second subhole (opens C5) | Assumed-hand parent of the first / distance |", "|---|---|---|---|"]
    for label, P, m, om, tilt in rows:
        k1, k2 = ("sub_L", "sub_R") if "sub_L" in m else ("sub1", "sub2")
        s = m.get(k1)
        md.append(f"| {label} | {sub_cell(m, k1)} | {sub_cell(m, k2)} | {s['nearest_same_hand']} / {f1(s['dist_same_hand'])} |" if s
                  else f"| {label} | – | – | – |")
    md += ["", "## 3. Thumb holes", "",
           "Position of each thumb hole along the hand axis, measured from the finger holes of its hand (+ = toward the tail).", "",
           "| Layout | L thumb from L pinky / L ring | R thumb from R index / R middle / R ring | R thumb across from R index (+ = nearer the player) |",
           "|---|---|---|---|"]
    for label, P, m, om, tilt in rows:
        lt, rt = m.get("L_thumb"), m.get("R_thumb")
        if not lt:
            md.append(f"| {label} | – | – | – |")
            continue
        md.append(f"| {label} | {f1(lt['rel']['L_pinky'])} / {f1(lt['rel']['L_ring'])} | {f1(rt['rel']['R_index'])} / "
                  f"{f1(rt['rel']['R_middle'])} / {f1(rt['rel']['R_ring'])} | {f1(rt['across']['R_index'])} |")
    md += ["", "## 4. Outline, rest space and chamber (ECAN3 models; needs the voxel cache)", "",
           "| Layout | Outer length along the hand axis | Body thickness, max | Rest space bulb / tail along the hand axis | Nearest outline point from L pinky / R pinky | Finger holes to the far edge (min–max, without R index) | R index to the far edge / to the player edge | Cavity length along the hand axis | Longest line in the cavity plan | c/(2·longest) ÷ F6 | Network first mode ÷ F6 | Cavity past L pinky / past R pinky | Cavity width / max depth |",
           "|" + "---|" * 13]
    for label, P, m, om, tilt in rows:
        if not om:
            continue
        model = "oot" if "Time" in label else "eclipse"
        fe = [om["far_edge"][n] for n in FINGERS if n != "R_index"]
        md.append(f"| {label} | {f1(om['outer_len'])} | {f1(om['body_thick_max'])} | {f1(om['rest_bulb'])} / {f1(om['rest_tail'])} "
                  f"| {f1(om['rest_bulb_any'])} / {f1(om['rest_tail_any'])} | {f1(min(fe))}–{f1(max(fe))} "
                  f"| {f1(om['far_edge']['R_index'])} / {f1(om['player_edge']['R_index'])} | {f1(om['cav_len'])} | {f1(om['cav_longest'])} "
                  f"| {f1(C_27 / (2 * om['cav_longest'] * 1e-3) / F6, 2)} | {f1(ECAN3_MODE1[model] / F6, 2)} "
                  f"| {f1(om['cav_before_L_pinky'])} / {f1(om['cav_after_R_pinky'])} | {f1(om['cav_width'])} / {f1(om['cav_thick_max'])} |")
    md += ["", "## 5. Hole lean", "",
           "Angle between each finger hole's axis and the normal of the finger face, and which way the outer mouth leans: "
           "*far* / *player* (across the hand axis) and *bulb* / *tail* (along it).", "",
           "| Layout | " + " | ".join(FINGERS) + " |", "|" + "---|" * 9]
    for label, P, m, om, tilt in rows:
        if not tilt:
            continue
        cells = []
        for n in FINGERS:
            ang, d = tilt[n]
            ac, al = float(d @ m["p"]), float(d @ m["a"])
            way = ("player" if ac > 0 else "far") if abs(ac) >= abs(al) else ("tail" if al > 0 else "bulb")
            cells.append(f"{ang:.0f}° {way}")
        md.append(f"| {label} | " + " | ".join(cells) + " |")
    md += ["", "## 6. Land past the pinky holes", "",
           "From the pinky hole centre to the end of the body, and the same from the hole **edge** (centre distance minus the hole radius): "
           "the surface a resting finger actually has.", "",
           "| Layout | Bulb: centre / hole Ø / from the edge | Tail: centre / hole Ø / from the edge |", "|---|---|---|"]
    for label, cb, db, ct, dt in land:
        md.append(f"| {label} | {f1(cb)} / {f1(db)} / **{f1(cb - db / 2)}** | {f1(ct)} / {f1(dt)} / **{f1(ct - dt / 2)}** |")
    if balance:
        md += ["", "## 7. Balance (plan view, uniform solid)", "",
               "Centre of mass against the line from the right thumb hole to the tail tip. Negative *along* = toward the bulb from the thumb hole.", "",
               "| Body | Along the line from the R thumb | Off the line (+ = toward the player) | R thumb to tail tip | Plastic, cm³ |", "|---|---|---|---|---|"]
        for label, al, off, ln, vol in balance:
            md.append(f"| {label} | {f1(al)} | {f1(off)} | {f1(ln, 0)} | {f1(vol)} |")
    if plots:
        md += ["", "Plan views: " + ", ".join(f"[{p}](images/{p})" for p in plots)]
    text = "\n".join(md) + "\n"
    (HERE / "measure_cad_output.md").write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
