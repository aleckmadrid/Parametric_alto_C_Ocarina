"""Where the windway sits on the body, and how the body outline compares with the add-on presets.

    python Analizes_ocarinas/Windway_and_body_shape/measure_body_windway.py

One frame for every instrument: the plan view of the finger face. The body axis is the longest chord of the
body outline without the mouthpiece. s is the station along it, 0 at the bulb (left-hand) end and 1 at the
tail tip. "Across" is perpendicular to it, + toward the player (the mouthpiece side).

Reads
    ../Songbird_OoT_12h/measure_output.json, ../Spencer_OoT_12h/measure_output.json   (run those scripts first)
    ../ECAN3_experimental/output/<model>/stage1.npz   voxel caches of the three ECAN3 STL models (not committed);
                                                      without them the STL rows are left out
    the hole tables of ../Ergonomic_reference_12hole/measure_cad_references.py and measure_reference.py
    ../../addon_checks/P*-80.json and the cavity presets of the add-on
Writes
    measure_output.md, measure_output.json
    images/01_outlines.png, images/02_width_profiles.png, images/03_ecan3_windway.png
Needs numpy, scipy, Pillow and matplotlib.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import ConvexHull

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent / "Ergonomic_reference_12hole"))
import measure_cad_references as mcr  # noqa: E402
import measure_reference as mr  # noqa: E402
from ocarina_addon import cavity_math, ergonomics as ergo, presets  # noqa: E402

LEFT = ("L_pinky", "L_ring", "L_middle", "L_index")
WALL_ADDON_MM = 4.0
N_ST = 101
STATIONS = np.linspace(0.0, 1.0, N_ST)

# ECAN3 10-hole model: hole centres from output/v0n3/results.json on the branch ecan3-experimental
V0N3_HOLES = {"L_pinky": (-29.0, -18.2, 49.7), "L_ring": (-13.3, -16.0, 55.9), "L_middle": (1.8, -11.2, 64.4),
              "L_index": (15.4, -4.4, 74.5), "R_index": (14.2, -8.7, 49.2), "R_middle": (26.7, -4.8, 61.6),
              "R_ring": (39.7, 0.5, 73.0), "R_pinky": (53.3, 6.9, 83.3), "L_thumb": (-25.2, 7.7, 46.7),
              "R_thumb": (21.0, 15.9, 63.8)}
# window patch centres of the ECAN3 analysis (results.json, window.centre), model frame
ECAN3_WINDOW = {"oot": (-9.5, 12.0, 52.6), "eclipse": (-126.5, -11.2, 43.9), "v0n3": (0.0, 8.5, 31.1)}
ECAN3_NAME = {"oot": "ECAN3 Ocarina of Time v3 (STL)", "eclipse": "ECAN3 Eclipse (STL)", "v0n3": "ECAN3 V0N3 10-hole (STL)"}
ECAN3_SX = {"oot": +1.0, "eclipse": -1.0, "v0n3": +1.0}       # +1: the bulb is toward -x in the model frame

# Test bodies built with tools/geometry_check_variant.py: body id -> the preset values it overrides.
# P2-80-seed: the station values fitted to the Songbird outline (section 6 of the report), port at 0.35 of the spine.
VARIANTS = {
    "P2-80-seed": dict(width=[0.5110, 0.3839, 0.3314, 0.2869, 0.2345, 0.1773, 0.1028],
                       height=[0.3761, 0.2914, 0.2524, 0.2178, 0.1748, 0.1260, 0.0491],
                       exponent=2.0, port_u=0.35, layout_centre_from_port_mm=20.0),
}


# ---------------------------------------------------------------- outline tools (masks and profiles)

def feret_pts(pts):
    hp = pts[ConvexHull(pts).vertices]
    d = np.linalg.norm(hp[:, None, :] - hp[None, :, :], axis=2)
    i, j = np.unravel_index(np.argmax(d), d.shape)
    return hp[i], hp[j], float(d[i, j])


def concave_envelope(y):
    """Smallest concave function above y on the station grid (the profile of the convex hull)."""
    pts = np.column_stack([STATIONS, y])
    hull = [0]
    for i in range(1, len(pts)):
        while len(hull) >= 2:
            a, b = pts[hull[-2]], pts[hull[-1]]
            if (b[0] - a[0]) * (pts[i][1] - a[1]) - (b[1] - a[1]) * (pts[i][0] - a[0]) >= 0:
                hull.pop()
            else:
                break
        hull.append(i)
    return np.interp(STATIONS, pts[hull, 0], pts[hull, 1])


def profile_metrics(player, far, L):
    """Shape numbers of an outline given as half widths (mm) on the station grid."""
    player, far = np.asarray(player, float), np.asarray(far, float)
    width = player + far
    i = int(np.argmax(width))
    dep_p = concave_envelope(player) - player
    dep_f = concave_envelope(far) - far
    inner = slice(3, N_ST - 3)
    return dict(length=L, width_max=float(width.max()), s_width_max=float(STATIONS[i]), w_over_l=float(width.max() / L),
                w10=float(width[10] / width.max()), w80=float(width[80] / width.max()), w90=float(width[90] / width.max()),
                player_share=float(player[i] / width[i]),
                concave_player_mm=float(dep_p[inner].max()), s_concave_player=float(STATIONS[inner][int(np.argmax(dep_p[inner]))]),
                concave_far_mm=float(dep_f[inner].max()), s_concave_far=float(STATIONS[inner][int(np.argmax(dep_f[inner]))]),
                concave_pct=float(100.0 * max(dep_p[inner].max(), dep_f[inner].max()) / L))


def mask_frame(mask, h, origin, bulb_near, player_pt):
    """Body axis of a plan mask (index i -> first coordinate, k -> second). Returns the frame and the profile."""
    edge = mask ^ ndi.binary_erosion(mask)
    ii, kk = np.nonzero(edge)
    pts = np.column_stack([origin[0] + (ii + 0.5) * h, origin[1] + (kk + 0.5) * h])
    p, q, L = feret_pts(pts)
    bulb, tail = (p, q) if np.linalg.norm(p - bulb_near) < np.linalg.norm(q - bulb_near) else (q, p)
    e = (tail - bulb) / L
    nrm = np.array([-e[1], e[0]])
    if (np.asarray(player_pt, float) - bulb) @ nrm < 0:
        nrm = -nrm
    ii, kk = np.nonzero(mask)
    d = np.column_stack([origin[0] + (ii + 0.5) * h, origin[1] + (kk + 0.5) * h]) - bulb
    s_mm, n_mm = d @ e, d @ nrm
    player, far = np.zeros(N_ST), np.zeros(N_ST)
    for j, s in enumerate(STATIONS):
        sel = np.abs(s_mm - s * L) <= max(h, 0.004 * L)
        if sel.any():
            player[j], far[j] = n_mm[sel].max(), -n_mm[sel].min()
    hull_area = ConvexHull(pts).volume
    return dict(bulb=bulb, tail=tail, e=e, nrm=nrm, L=L, player=player, far=far,
                convexity=float(mask.sum() * h * h / hull_area))


def station(fr, pt):
    d = np.asarray(pt, float) - fr["bulb"]
    return float(d @ fr["e"]) / fr["L"], float(d @ fr["nrm"])


def cross_left_row(P, root, direction):
    """Where the mouthpiece axis (a line through `root` along `direction`, plan view) crosses the row of left-hand
    holes. Returns u (0 at L pinky, 1 at L index along the pinky -> index line) and the u of each left-hand hole."""
    a, b = np.array(P["L_pinky"], float), np.array(P["L_index"], float)
    v, d = b - a, np.asarray(direction, float)
    M = np.column_stack([v, -d])
    if abs(np.linalg.det(M)) < 1e-9:
        return None, {}
    u = float(np.linalg.solve(M, np.asarray(root, float) - a)[0])
    us = {n: float((np.array(P[n], float) - a) @ v / (v @ v)) for n in LEFT}
    return u, us


def describe_cross(u, us):
    if u is None:
        return "–"
    names = sorted(us, key=lambda n: us[n])
    for lo, hi in zip(names, names[1:]):
        if us[lo] <= u <= us[hi]:
            f = (u - us[lo]) / (us[hi] - us[lo])
            return f"between {lo} and {hi}, {100 * f:.0f} % of the way"
    return f"past {names[-1]} (toward the tail)" if u > us[names[-1]] else f"before {names[0]} (toward the bulb end)"


# ---------------------------------------------------------------- ECAN3 voxel models

def ecan3_holes(model):
    """Hole centres in the model frame (x, y, z)."""
    if model == "v0n3":
        return {n: np.array(c, float) for n, c in V0N3_HOLES.items()}
    return {n: np.array(v[0], float) for n, v in mcr.ECAN3[model].items()}


def ecan3(model):
    f = HERE.parent / "ECAN3_experimental" / "output" / model / "stage1.npz"
    if not f.exists():
        return None
    z = np.load(f)
    Lg, o, h = z["L"], z["origin"], float(z["h"])
    solid = (Lg == 1) | (Lg == 3)
    cav = Lg == 2
    filled3 = solid | cav
    holes = ecan3_holes(model)

    # windway: air enclosed by plastic in the horizontal slices of the mouthpiece (the models stand on it), followed
    # upward from the tip until it opens into the window
    track, prev = [], None
    for k in range(Lg.shape[2]):
        s = solid[:, :, k]
        if not s.any():
            continue
        encl = ndi.binary_fill_holes(s) & ~s & ~cav[:, :, k]
        lab, n = ndi.label(encl)
        if n == 0:
            if prev is not None:
                break
            continue
        cs = ndi.center_of_mass(encl, lab, range(1, n + 1))
        sizes = ndi.sum(encl, lab, range(1, n + 1))
        if prev is None:
            j = int(np.argmax(sizes))
        else:
            dist = [math.hypot(c[0] - prev[0], c[1] - prev[1]) for c in cs]
            j = int(np.argmin(dist))
            if dist[j] * h > 3.0:
                break
        if sizes[j] * h * h < 1.0:
            if prev is not None:
                break
            continue
        m = lab == j + 1
        ii, jj = np.nonzero(m)
        prev = cs[j]
        track.append((o[0] + (cs[j][0] + 0.5) * h, o[1] + (cs[j][1] + 0.5) * h, o[2] + (k + 0.5) * h,
                      (ii.max() - ii.min() + 1) * h, (jj.max() - jj.min() + 1) * h, sizes[j] * h * h))
    track = np.array(track)
    zt = track[:, 2]
    cx = np.polyfit(zt, track[:, 0], 1)                   # x = cx[0] z + cx[1]
    cy = np.polyfit(zt, track[:, 1], 1)
    tip3, exit3 = track[0, :3], track[-1, :3]

    # plan masks (project along y): the body is the cavity plan grown by the wall, inside the plastic outline
    solid_plan = filled3.any(axis=1)
    cav_plan = cav.any(axis=1)
    r = int(round(5.0 / h))
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    body = solid_plan & ndi.binary_dilation(cav_plan, structure=(xx * xx + yy * yy) <= r * r)
    body = ndi.binary_fill_holes(body)
    lab, n = ndi.label(body)
    body = lab == 1 + int(np.argmax(ndi.sum(body, lab, range(1, n + 1))))
    o2 = np.array([o[0], o[2]])
    lp = holes["L_pinky"]
    fr = mask_frame(body, h, o2, np.array([lp[0], lp[2]]), np.array([tip3[0], tip3[2]]))

    # neck root: where the windway line enters the body outline, coming from the tip
    root = None
    for zz in np.arange(tip3[2], o[2] + Lg.shape[2] * h, h / 2):
        x = np.polyval(cx, zz)
        i, k = int((x - o2[0]) / h), int((zz - o2[1]) / h)
        if 0 <= i < body.shape[0] and 0 <= k < body.shape[1] and body[i, k]:
            root = np.array([x, zz])
            break
    d_in = np.array([cx[0], 1.0]) / math.hypot(cx[0], 1.0)            # windway direction in plan, tip -> body
    ang = math.degrees(math.acos(float(-d_in @ fr["e"])))            # mouthpiece axis (root -> tip) against bulb -> tail
    win = np.array(ECAN3_WINDOW[model])
    # thickness through the two playing faces
    any_y = filled3.any(axis=1)
    first = np.argmax(filled3, axis=1)
    last = filled3.shape[1] - 1 - np.argmax(filled3[:, ::-1, :], axis=1)
    thick = np.where(any_y & body, (last - first + 1) * h, 0.0)
    cthick = np.where(body, cav.sum(axis=1) * h, 0.0)
    ii, kk = np.nonzero(body)
    dd = np.column_stack([o2[0] + (ii + 0.5) * h, o2[1] + (kk + 0.5) * h]) - fr["bulb"]
    s_mm = dd @ fr["e"]
    t_prof = np.array([thick[ii, kk][np.abs(s_mm - s * fr["L"]) <= h].max(initial=0.0) for s in STATIONS])
    ct_prof = np.array([cthick[ii, kk][np.abs(s_mm - s * fr["L"]) <= h].max(initial=0.0) for s in STATIONS])
    # cavity plan in the same frame
    ci, ck = np.nonzero(cav_plan)
    cd = np.column_stack([o2[0] + (ci + 0.5) * h, o2[1] + (ck + 0.5) * h]) - fr["bulb"]
    cs_mm, cn_mm = cd @ fr["e"], cd @ fr["nrm"]
    cav_player = np.array([cn_mm[np.abs(cs_mm - s * fr["L"]) <= h].max(initial=0.0) for s in STATIONS])
    cav_far = np.array([(-cn_mm[np.abs(cs_mm - s * fr["L"]) <= h]).max(initial=0.0) for s in STATIONS])

    # player-view hole plan for the hand frame: X = sx * x, Y = -z
    sx = ECAN3_SX[model]
    P = {n: (sx * c[0], -c[2]) for n, c in holes.items()}

    def pv(pt2):
        return np.array([sx * pt2[0], -pt2[1]])

    u, us = cross_left_row(P, pv(root), pv(d_in) - pv(np.zeros(2)))
    return dict(name=ECAN3_NAME[model], model=model, fr=fr, body=body, cav_plan=cav_plan, o2=o2, h=h, track=track,
                tip=np.array([tip3[0], tip3[2]]), exit=np.array([exit3[0], exit3[2]]), root=root, win=np.array([win[0], win[2]]),
                angle=ang, windway_len=float(np.linalg.norm(exit3 - tip3)), holes=holes, P=P, cross=(u, us),
                thick=t_prof, cav_thick=ct_prof, cav_player=cav_player, cav_far=cav_far,
                exit_y=float(exit3[1]), y_range=(float(o[1] + first[body].min() * h), float(o[1] + (last[body].max() + 1) * h)),
                tip_wh=(float(track[0, 3]), float(track[0, 4])), exit_wh=(float(track[-1, 3]), float(track[-1, 4])))


# ---------------------------------------------------------------- add-on presets

def addon(body_id, overrides=None):
    pid = body_id.split("-")[0]
    js = json.load(open(ROOT / "addon_checks" / f"{body_id}.json"))["measurements"]
    pre = dict(presets.get_preset(pid), **(overrides or {}))
    cav = cavity_math.Cavity.from_preset(pre, scale=js["cavity"]["scale"])
    n = 400
    up, dn = [], []
    for i in range(n + 1):
        th = math.pi * i / n
        up.append(cav.point(th, 0.0)[:2])                  # far side (+Y)
        dn.append(cav.point(th, math.pi)[:2])              # player side (-Y)
    poly = np.array(up + dn[::-1])
    h = 0.25
    pad = 12.0
    o2 = poly.min(axis=0) - pad
    size = np.ceil((poly.max(axis=0) + pad - o2) / h).astype(int)
    img = Image.new("1", (int(size[0]), int(size[1])), 0)
    ImageDraw.Draw(img).polygon([tuple(((p - o2) / h).tolist()) for p in poly], fill=1)
    cav_mask = np.asarray(img).T.astype(bool)             # [i (x), k (y)]
    r = int(round(WALL_ADDON_MM / h))
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    body = ndi.binary_dilation(cav_mask, structure=(xx * xx + yy * yy) <= r * r)
    H = {hh["name"]: hh for hh in js["holes"]}
    lp = np.array(H["L_pinky"]["centre"][:2])
    # plan coordinates here are (x, y) of the body frame: +y is the far side, so the player is toward -y
    fr = mask_frame(body, h, o2, lp, np.array([0.0, -200.0]))
    frc = mask_frame(cav_mask, h, o2, lp, np.array([0.0, -200.0]))
    P = {nm: (hh["centre"][0], -hh["centre"][1]) for nm, hh in H.items()}
    P = {("sub_L" if k == "sub1" else "sub_R" if k == "sub2" else k): v for k, v in P.items()}
    xf, yf, zf = cav.port_frame()                         # xf = jet direction; the windway runs along -xf
    d_plan = np.array([-xf[0], -xf[1]])
    d_plan = d_plan / np.linalg.norm(d_plan)              # port -> mouth, plan view, body frame
    ang = math.degrees(math.acos(float(d_plan @ fr["e"])))
    u, us = cross_left_row(P, (0.0, 0.0), (d_plan[0], -d_plan[1]))
    # the side view (heights) for the smoothness of the deck
    top = np.array([cav.point(math.pi * i / n, math.pi / 2)[2] for i in range(n + 1)])
    bot = np.array([cav.point(math.pi * i / n, 3 * math.pi / 2)[2] for i in range(n + 1)])
    xs = np.array([cav.point(math.pi * i / n, math.pi / 2)[0] for i in range(n + 1)])
    s_side = (xs - xs.min()) / (xs.max() - xs.min())
    order = np.argsort(s_side)
    half_h = np.interp(STATIONS, s_side[order], ((top - bot) / 2.0)[order])
    dep_h = concave_envelope(half_h) - half_h
    return dict(name=f"Add-on {body_id}", fr=fr, frc=frc, body=body, cav_mask=cav_mask, o2=o2, h=h, P=P, angle=ang,
                cross=(u, us), port_u=pre["port_u"], cav_len=js["cavity"]["length_mm"], half_h=half_h,
                deck_concave_mm=float(dep_h[3:-3].max()), width_st=pre["width"], height_st=pre["height"],
                exponent=pre.get("exponent", 2.0))


# ---------------------------------------------------------------- station fit (the preset model)

def catmull_basis(t, n=7):
    """Row of weights w with Catmull-Rom(values, t) = w @ values (the spline is linear in its station values)."""
    return np.array([cavity_math.catmull_rom([1.0 if j == i else 0.0 for j in range(n)], t) for i in range(n)])


def fit_stations(width_frac, t_grid):
    """Least-squares station values S_k so that width / length = S(t) * sqrt(4 t (1 - t)) follows the profile."""
    A, b = [], []
    for t, w in zip(t_grid, width_frac):
        env = math.sqrt(max(4.0 * t * (1.0 - t), 0.0))
        if env < 0.2:
            continue
        A.append(catmull_basis(t) * env)
        b.append(w)
    sol, *_ = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)
    fit = np.array([cavity_math.catmull_rom(list(sol), t) * math.sqrt(max(4 * t * (1 - t), 0.0)) for t in t_grid])
    return sol, fit


def cavity_from_outer(width_frac, tw_ratio, wall, target_mm3, exponent=2.0):
    """Scale an outer outline (width / outer length on the station grid) so that the cavity, the outline moved inward
    by `wall`, holds `target_mm3`. Sections are ellipses, thickness = tw_ratio * width. Returns the outer length, the
    cavity length and the cavity width and height over the cavity length on a t grid."""
    k_area = cavity_math.superellipse_area_factor(exponent)

    def cavity(Lo):
        a = np.clip(width_frac * Lo / 2.0 - wall, 0.0, None)
        b = np.clip(tw_ratio * width_frac * Lo / 2.0 - wall, 0.0, None)
        x = STATIONS * Lo
        inside = (a > 0) & (b > 0)
        vol = float(np.trapezoid(k_area * a * b, x))
        return a, b, x, inside, vol

    lo, hi = 60.0, 400.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if cavity(mid)[4] < target_mm3:
            lo = mid
        else:
            hi = mid
    Lo = 0.5 * (lo + hi)
    a, b, x, inside, vol = cavity(Lo)
    x0 = max(wall, x[inside].min() - (x[1] - x[0]))
    x1 = min(Lo - wall, x[inside].max() + (x[1] - x[0]))
    Lc = x1 - x0
    t = np.linspace(0.0, 1.0, N_ST)
    xa = x0 + t * Lc
    return Lo, Lc, t, np.interp(xa, x, 2 * a) / Lc, np.interp(xa, x, 2 * b) / Lc


# ---------------------------------------------------------------- report

def f1(v, nd=1):
    return "–" if v is None or (isinstance(v, float) and v != v) else f"{v:.{nd}f}"


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    (HERE / "images").mkdir(exist_ok=True)

    rows = []          # one dict per instrument: name, L, player, far, mouthpiece numbers ...
    out = {}

    # --- photos
    for folder, key in (("Songbird_OoT_12h", "songbird"), ("Spencer_OoT_12h", "spencer")):
        f = HERE.parent / folder / "measure_output.json"
        if not f.exists():
            continue
        j = json.load(open(f))
        P = {k: (v["X"], v["Y"]) for k, v in j["holes"].items()}
        mp = j["mouthpiece"]
        L = j["length_mm"]
        root = (mp["root_station"] * L, mp["root_across_mm"])
        ang = math.radians(mp["angle_to_body_axis_deg"])
        u, us = cross_left_row(P, root, (math.cos(ang), math.sin(ang)))
        hm = ergo.hand_metrics(P)
        a = np.array(hm["a"])
        rel = {k: float((np.array(root) - np.array(P[k])) @ a) for k in LEFT}
        hs = {k: v["s"] for k, v in j["holes"].items()}
        for nm, f in j.get("thumb_face", {}).get("feats", {}).items():
            if nm.endswith("thumb"):
                hs[nm] = f["s"]                      # rough: corrected station of an oblique frame
        rows.append(dict(key=key, name=j["name"], kind="photo", hs=hs, L=L, player=np.array(j["player_half_mm"]),
                         far=np.array(j["far_half_mm"]), convexity=j["convexity"], s_root=mp["root_station"],
                         s_window=None, angle=mp["angle_to_body_axis_deg"], cross=(u, us), rel=rel,
                         pitch=j["mean_finger_pitch_mm"], thick=None, P=P, tenor=j.get("tenor_a"),
                         length_note=("estimated" if j.get("length_is_estimate") else "maker"),
                         root_range=mp.get("root_station_by_photo")))

    # --- Miracle (numbers of Miracle_M.md: stub axis x = 46 mm, window centre x = 48.3 mm, length 150 mm)
    Pm = {k: tuple(v) for k, v in mr.MIRACLE.items()}
    Pm_c = {k: (v[0], v[1] - 38.0) for k, v in Pm.items()}        # y from the far edge -> across, about the mid line
    u, us = cross_left_row(Pm_c, (46.0, 30.0), (0.0, 1.0))
    hm = ergo.hand_metrics(Pm_c)
    a = np.array(hm["a"])
    rel = {k: float((np.array([46.0, Pm_c[k][1]]) - np.array(Pm_c[k])) @ a) for k in LEFT}
    xs = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150], float)
    top = np.array([26, 7.1, 2.3, 0.3, 0.8, 1.3, 2.6, 3.2, 3.9, 4.2, 4.5, 4.8, 4.8, 4.8, 4.8, 13.8])
    bot = np.array([26, 45.7, 64.3, 67.5, 70.5, 72.5, 74.0, 56.0, 48.6, 43.7, 39.6, 35.4, 31.2, 26.7, 22.8, 13.8])
    axis_y = 26.0 - 12.2 * STATIONS                               # bulb end (0, 26) -> tail tip (150, 13.8), y from the far edge
    m_player = np.clip(np.interp(STATIONS * 150.0, xs, bot) - axis_y, 0.0, None)
    m_far = np.clip(axis_y - np.interp(STATIONS * 150.0, xs, top), 0.0, None)
    rows.append(dict(key="miracle", name="Miracle AO10-AC (photo, catalogue scale; outline from its table)", kind="photo",
                     hs={k: v[0] / 150.0 for k, v in Pm.items()},
                     L=150.0, player=m_player, far=m_far, convexity=None, s_root=46.0 / 150.0, s_window=48.3 / 150.0,
                     angle=90.0, cross=(u, us), rel=rel, pitch=float(np.mean(hm["L"]["pitches"] + hm["R"]["pitches"])),
                     thick=None, P=Pm_c, table_outline=True))

    # --- ECAN3 STL models
    ec = {}
    for model in ("oot", "eclipse", "v0n3"):
        r = ecan3(model)
        if r is None:
            continue
        ec[model] = r
        fr = r["fr"]
        hm = ergo.hand_metrics({k: v for k, v in r["P"].items() if not k.endswith("thumb")})
        a = np.array(hm["a"])
        sx = ECAN3_SX[model]
        exit_pv = np.array([sx * r["exit"][0], -r["exit"][1]])
        rel = {k: float((exit_pv - np.array(r["P"][k])) @ a) for k in LEFT}
        rows.append(dict(key=model, name=r["name"], kind="stl", hs={n: station(fr, (c[0], c[2]))[0] for n, c in r["holes"].items()}, L=fr["L"], player=fr["player"], far=fr["far"],
                         convexity=fr["convexity"], s_root=station(fr, r["root"])[0], s_exit=station(fr, r["exit"])[0],
                         s_window=station(fr, r["win"])[0], s_tip=station(fr, r["tip"])[0], angle=r["angle"], cross=r["cross"],
                         rel=rel, pitch=float(np.mean(hm["L"]["pitches"] + hm["R"]["pitches"])), thick=r["thick"],
                         cav_thick=r["cav_thick"], cav_player=r["cav_player"], cav_far=r["cav_far"], P=r["P"],
                         windway_len=r["windway_len"], exit_inboard=station(fr, r["exit"])[1], root_across=station(fr, r["root"])[1],
                         win_across=station(fr, r["win"])[1], decorative=(model == "eclipse")))

    # --- add-on
    ad = {}
    for body_id in ("P1-80", "P2-80", "P3-80") + tuple(VARIANTS):
        if not (ROOT / "addon_checks" / f"{body_id}.json").exists():
            continue
        r = addon(body_id, VARIANTS.get(body_id))
        ad[body_id] = r
        fr = r["fr"]
        s_port, n_port = station(fr, (0.0, 0.0))
        hm = ergo.hand_metrics({k: v for k, v in r["P"].items() if not k.endswith("thumb")})
        a = np.array(hm["a"])
        rel = {k: float((np.zeros(2) - np.array(r["P"][k])) @ a) for k in LEFT}
        rows.append(dict(key=body_id, name=r["name"] + " (cavity + 4 mm wall)", kind="addon",
                         hs={n: station(fr, (v[0], -v[1]))[0] for n, v in r["P"].items()}, L=fr["L"], player=fr["player"],
                         far=fr["far"], convexity=fr["convexity"], s_root=s_port, s_window=s_port, angle=r["angle"],
                         cross=r["cross"], rel=rel, pitch=float(np.mean(hm["L"]["pitches"] + hm["R"]["pitches"])),
                         thick=2 * r["half_h"] + 2 * WALL_ADDON_MM, P=r["P"], port_u=r["port_u"], port_across=n_port,
                         cav=r["frc"], deck_concave_mm=r["deck_concave_mm"]))

    for r in rows:
        r["shape"] = profile_metrics(r["player"], r["far"], r["L"])

    # ------------------------------------------------------------ tables
    md = ["# Windway position and body outline: references against the add-on presets", "",
          "Generated by `measure_body_windway.py`. Plan view of the finger face. The body axis is the longest chord of the "
          "body outline without the mouthpiece; s = station along it, 0 at the bulb (left-hand) end, 1 at the tail tip.", "",
          "## 1. Where the mouthpiece and the windway sit along the body", "",
          "*Neck root*: where the mouthpiece axis meets the body outline on the player side. *Windway exit*: the end of the closed "
          "windway channel (STL models). *Window*: the window centre (the ECAN3 value is the centre of the whole opening patch, "
          "which includes the labium ramp). *Angle*: mouthpiece axis (root → tip) against the body axis (bulb → tail); 90° = square, "
          "below 90° the tip leans toward the tail.", "",
          "| Instrument | Body length mm | Neck root s | Windway exit s | Window s | Angle | Mouthpiece axis crosses the left-hand row |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        rr = r.get("root_range")
        root_txt = f"**{r['s_root']:.3f}**" + (f" ({min(rr.values()):.2f}–{max(rr.values()):.2f} on {len(rr)} photos)" if rr else "")
        md.append(f"| {r['name']} | {f1(r['L'])} | {root_txt} | {f1(r.get('s_exit'), 3)} | {f1(r.get('s_window'), 3)} | "
                  f"{f1(r['angle'], 0)}° | {describe_cross(*r['cross'])} |")
    md += ["", "For the add-on rows the neck root, the windway exit and the window are one point: the voicing port (the origin of the body). "
           "The preset value `port_u` is measured along the cavity spine: " +
           ", ".join(f"{k} {ad[k]['port_u']:.2f}" for k in ad) + ".", "",
           "## 2. The mouthpiece against the holes, along the body axis", "",
           "Stations of the hole centres on the same axis. *Mouthpiece − L middle* is the distance from the L middle hole to the "
           "neck root along the body axis (+ = the mouthpiece is toward the tail). *Layout centre* is the point halfway between the "
           "two index holes.", "",
           "| Instrument | L pinky | L ring | L middle | L index | R index | R pinky | Mouthpiece (neck root) | Mouthpiece − L middle, mm / % of length | Layout centre − mouthpiece, mm / % of length | L thumb | R thumb |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        hs = r["hs"]
        dm = (r["s_root"] - hs["L_middle"])
        dc = (0.5 * (hs["L_index"] + hs["R_index"]) - r["s_root"])
        md.append(f"| {r['name']} | {hs['L_pinky']:.3f} | {hs['L_ring']:.3f} | {hs['L_middle']:.3f} | {hs['L_index']:.3f} | {hs['R_index']:.3f} | "
                  f"{hs['R_pinky']:.3f} | **{r['s_root']:.3f}** | {dm * r['L']:+.1f} / {100 * dm:+.1f} | {dc * r['L']:+.1f} / {100 * dc:+.1f} | "
                  f"{f1(hs.get('L_thumb'), 3)} | {f1(hs.get('R_thumb'), 3)} |")
    md += ["", "The Spencer hole stations carry about ±0.03 (parallax between the deck and the outline; photo 03 lies midway between "
           "the two oblique photos, see its own report). The Songbird thumb stations come from one oblique video frame, after a "
           "projective correction: about ±0.05. The Songbird millimetres are for an estimated body length."]
    if ec:
        md += ["", "## 3. The windway inside the STL models", "",
               "| Model | Windway length, tip to exit | Channel at the tip (wide × high) | Channel at the exit | Exit: distance inboard of the body axis (+ = player side) | Neck root: same | Window patch centre: same | Exit through the thickness (y) / body y range |",
               "|---|---|---|---|---|---|---|---|"]
        for model, r in ec.items():
            row = next(x for x in rows if x["key"] == model)
            md.append(f"| {r['name']} | {f1(r['windway_len'])} mm | {f1(r['tip_wh'][0])} × {f1(r['tip_wh'][1])} mm | "
                      f"{f1(r['exit_wh'][0])} × {f1(r['exit_wh'][1])} mm | {row['exit_inboard']:+.1f} mm | {row['root_across']:+.1f} mm | "
                      f"{row['win_across']:+.1f} mm | {f1(r['exit_y'])} / {f1(r['y_range'][0])} … {f1(r['y_range'][1])} mm |")
    md += ["", "## 4. Outline shape", "",
           "*Concave depth*: the largest gap between one edge of the outline and its convex hull (0 = that edge is convex everywhere). "
           "*Player share*: the part of the largest width that lies on the player side of the body axis. "
           "Widths at s = 0.1, 0.8 and 0.9 are fractions of the largest width.", "",
           "| Instrument | Length | Largest width | Width / length | s of largest width | Player share | Width at 0.1 / 0.8 / 0.9 | Area / hull area | Concave depth player / far (mm) | Largest, % of length |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        sh = r["shape"]
        note = " (table)" if r.get("table_outline") else ""
        md.append(f"| {r['name']}{note} | {f1(sh['length'])} | {f1(sh['width_max'])} | {sh['w_over_l']:.3f} | {sh['s_width_max']:.2f} | "
                  f"{sh['player_share']:.2f} | {sh['w10']:.2f} / {sh['w80']:.2f} / {sh['w90']:.2f} | {f1(r['convexity'], 3)} | "
                  f"{sh['concave_player_mm']:.1f} at {sh['s_concave_player']:.2f} / {sh['concave_far_mm']:.1f} at {sh['s_concave_far']:.2f} | {sh['concave_pct']:.1f} |")
    md += ["", "The cavity alone (what the holes are cut into), add-on presets and STL models:", "",
           "| Body | Cavity plan: concave depth player / far (mm) | Deck (side view): concave depth (mm) | Cavity thickness / cavity width, at the largest width |",
           "|---|---|---|---|"]
    for k, r in ad.items():
        shc = profile_metrics(r["frc"]["player"], r["frc"]["far"], r["frc"]["L"])
        i = int(np.argmax(r["frc"]["player"] + r["frc"]["far"]))
        md.append(f"| {r['name']} | {shc['concave_player_mm']:.1f} at {shc['s_concave_player']:.2f} / {shc['concave_far_mm']:.1f} at {shc['s_concave_far']:.2f} | "
                  f"{r['deck_concave_mm']:.1f} | {2 * r['half_h'].max() / (r['frc']['player'] + r['frc']['far'])[i]:.2f} |")
    for model, r in ec.items():
        shc = profile_metrics(r["cav_player"], r["cav_far"], r["fr"]["L"])
        i = int(np.argmax(r["cav_player"] + r["cav_far"]))
        md.append(f"| {r['name']} | {shc['concave_player_mm']:.1f} at {shc['s_concave_player']:.2f} / {shc['concave_far_mm']:.1f} at {shc['s_concave_far']:.2f} | "
                  f"– | {r['cav_thick'].max() / (r['cav_player'] + r['cav_far'])[i]:.2f} |")

    # --- depth
    md += ["", "## 5. Depth (thickness through the two playing faces)", "",
           "| Instrument | Largest thickness mm | Largest width mm | Thickness / width | Source |", "|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] == "stl" and not r.get("decorative"):
            md.append(f"| {r['name']} | {r['thick'].max():.1f} | {r['shape']['width_max']:.1f} | {r['thick'].max() / r['shape']['width_max']:.2f} | voxel model |")
        if r["kind"] == "addon":
            md.append(f"| {r['name']} | {np.max(r['thick']):.1f} | {r['shape']['width_max']:.1f} | {np.max(r['thick']) / r['shape']['width_max']:.2f} | preset |")
    sb = next((r for r in rows if r["key"] == "songbird"), None)
    sp = next((r for r in rows if r["key"] == "spencer"), None)
    depth = {}
    if sb is not None and sb.get("tenor"):
        ten = sb["tenor"]
        depth["songbird_tw"] = ten["tw_with_measured_width"]
        depth["songbird_tw_maker"] = ten["tw_maker"]
        md.append(f"| {ten['name']} | {ten['thickness_maker_mm']:.1f} | {ten['thickness_maker_mm'] / ten['tw_with_measured_width']:.1f} (outline scaled to 203.2 mm) | "
                  f"{ten['tw_with_measured_width']:.2f} | maker's thickness (2.25 in) over the width of the scaled outline |")
        md.append(f"| {ten['name']} | {ten['thickness_maker_mm']:.1f} | {ten['width_maker_mm']:.1f} (maker: 3 in) | {ten['tw_maker']:.2f} | the maker's own two numbers, both rounded |")
    if sp is not None:
        # mass balance: plastic = (mass - mouthpiece) / density; outer volume = plastic + air; sections taken as ellipses
        w = sp["player"] + sp["far"]
        int_w2 = float(np.trapezoid(w * w, STATIONS * sp["L"]))
        cases = []
        for air, rho, m_mouth in ((70.0, 2.3, 35.0), (60.0, 2.4, 45.0), (80.0, 2.1, 25.0)):
            outer = air * 1000.0 + (330.0 - m_mouth) / rho * 1000.0
            cases.append(outer / (math.pi / 4.0 * int_w2))
        depth["spencer_tw"] = cases
        md.append(f"| {sp['name']} | {cases[0] * sp['shape']['width_max']:.0f} ({cases[1] * sp['shape']['width_max']:.0f}–{cases[2] * sp['shape']['width_max']:.0f}) | "
                  f"{sp['shape']['width_max']:.1f} (apparent) | {cases[0]:.2f} ({cases[1]:.2f}–{cases[2]:.2f}) | mass balance: 330 g, fired clay 2.1–2.4 g/cm³, 60–80 cm³ of air, elliptical sections |")
    md += ["", "The photos give no direct thickness. The grip photos show the far edge of both ceramic bodies as a deep, round flank, "
           "which agrees with a thickness of about 0.8 of the width; they have no usable scale."]

    # --- station fit
    md += ["", "## 6. The reference outlines in the preset model", "",
           "The add-on describes a cavity by 7 width stations and 7 height stations (`cavity_presets.toml`). Each reference outline "
           "is taken as the outer body of a printed part with a 4 mm wall, scaled until the cavity inside holds 78.1 cm³ (the cavity mesh of an "
           "80 cm³ body), and the station values are fitted to that cavity by least squares. Sections are ellipses. "
           "Thickness / width: 0.80 for the Songbird outline (the Tenor A value of section 5; the Alto C is taken to have the same section); 0.80 assumed for the Spencer; the measured thickness profile for the STL model.", "",
           "| Outline | Outer length mm | Cavity spine mm | Cavity width × height mm | Width stations | Height stations | Fit error, rms / max (mm) |",
           "|---|---|---|---|---|---|---|"]
    fits = {}
    target = 78110.0
    for key, tw in (("songbird", depth.get("songbird_tw", 0.8)), ("spencer", 0.80), ("oot", None)):
        r = next((x for x in rows if x["key"] == key), None)
        if r is None:
            continue
        wfrac = (r["player"] + r["far"]) / r["L"]
        if tw is None:
            ratio = float(r["thick"].max() / (r["player"] + r["far"]).max())
            tfrac = r["thick"] / r["L"]
        else:
            ratio, tfrac = tw, None
        Lo, Lc, t, wc, hc = cavity_from_outer(wfrac, ratio, WALL_ADDON_MM, target)
        if tfrac is not None:                       # use the real thickness profile for the heights
            xa = np.interp(t, [0, 1], [WALL_ADDON_MM, Lo - WALL_ADDON_MM])
            hc = np.clip(np.interp(xa, STATIONS * Lo, tfrac * Lo) - 2 * WALL_ADDON_MM, 0, None) / Lc
        sw, fw = fit_stations(wc, t)
        sh_, fh = fit_stations(hc, t)
        err = np.r_[(fw - wc) * Lc]
        inner = slice(8, N_ST - 8)
        fits[key] = dict(outer_length_mm=Lo, cavity_length_mm=Lc, width=[round(float(v), 4) for v in sw],
                         height=[round(float(v), 4) for v in sh_], tw_ratio=ratio,
                         cav_w=float(wc.max() * Lc), cav_h=float(hc.max() * Lc), s_root=r["s_root"],
                         port_u=float((r["s_root"] * Lo - WALL_ADDON_MM) / Lc))
        md.append(f"| {r['name']} | {Lo:.1f} | {Lc:.1f} | {wc.max() * Lc:.1f} × {hc.max() * Lc:.1f} | "
                  f"{', '.join(f'{v:.4f}' for v in sw)} | {', '.join(f'{v:.4f}' for v in sh_)} | "
                  f"{float(np.sqrt(np.mean(err[inner] ** 2))):.2f} / {float(np.abs(err[inner]).max()):.2f} |")
    md += ["", "Present presets, for comparison (width stations; the spine length is that of the 80 cm³ body):", "",
           "| Preset | Cavity spine mm | Width stations | Height stations | port_u |", "|---|---|---|---|---|"]
    for k, r in ad.items():
        md.append(f"| {k} | {r['cav_len']:.1f} | {', '.join(f'{v:.4f}' for v in r['width_st'])} | {', '.join(f'{v:.4f}' for v in r['height_st'])} | {r['port_u']:.2f} |")
    if fits:
        md += ["", "The mouthpiece station of each reference, as the `port_u` of its fitted cavity (station of the neck root, measured along the cavity spine):", "",
               "| Outline | Neck root s (outer) | Same as port_u |", "|---|---|---|"]
        for key, ft in fits.items():
            md.append(f"| {key} | {ft['s_root']:.3f} | {ft['port_u']:.3f} |")

    # ------------------------------------------------------------ figures
    order = ["songbird", "spencer", "oot", "miracle", "v0n3", "eclipse", "P1-80", "P2-80", "P3-80"]
    order += [k for k in VARIANTS if any(x["key"] == k for x in rows)]
    nrow = math.ceil(len(order) / 3)
    fig, axs = plt.subplots(nrow, 3, figsize=(15, 3.2 * nrow), dpi=110)
    for ax in axs.ravel()[len(order):]:
        ax.axis("off")
    for ax, key in zip(axs.ravel(), order):
        r = next((x for x in rows if x["key"] == key), None)
        ax.set_aspect("equal")
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.33, 0.33)
        ax.axhline(0, color="#bbb", lw=0.6)
        ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        if r is None:
            ax.set_title(key + " (no data)", fontsize=9)
            continue
        L = r["L"]
        col = {"photo": "#1f5fa8", "stl": "#2a7f3f", "addon": "#b3541e"}[r["kind"]]
        ax.fill_between(STATIONS, -r["far"] / L, r["player"] / L, color=col, alpha=0.18, lw=0)
        ax.plot(STATIONS, r["player"] / L, color=col, lw=1.4)
        ax.plot(STATIONS, -r["far"] / L, color=col, lw=1.4)
        ax.plot(STATIONS, concave_envelope(r["player"]) / L, color="#888", lw=0.7, ls=":")
        ax.plot(STATIONS, -concave_envelope(r["far"]) / L, color="#888", lw=0.7, ls=":")
        ax.axvline(r["s_root"], color="#c00", lw=1.2)
        ax.text(r["s_root"] + 0.01, 0.27, f"mouthpiece {r['s_root']:.2f}", color="#c00", fontsize=8)
        # holes in the body-axis frame, where available
        ax.set_title(r["name"].split(" (")[0] + f"   W/L {r['shape']['w_over_l']:.2f}", fontsize=9)
    axs[nrow - 1, 0].set_xlabel("station s along the body axis (0 = bulb end, 1 = tail tip); + across = player side. "
                         "Dotted: convex hull of each edge. Red: mouthpiece / port station.")
    fig.suptitle("Body outlines in units of body length (blue: photos, green: STL models, orange: add-on presets with a 4 mm wall)", fontsize=11)
    fig.tight_layout()
    fig.savefig(HERE / "images" / "01_outlines.png")
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(14, 5), dpi=110)
    style = {"songbird": ("#1f5fa8", "-"), "spencer": ("#1f5fa8", "--"), "oot": ("#2a7f3f", "-"), "miracle": ("#777", ":"),
             "P1-80": ("#b3541e", "--"), "P2-80": ("#b3541e", "-"), "P3-80": ("#b3541e", ":"), "P2-80-seed": ("#c0007a", "-")}
    for r in rows:
        if r["key"] not in style:
            continue
        c, ls = style[r["key"]]
        w = (r["player"] + r["far"])
        ax[0].plot(STATIONS, w / w.max(), color=c, ls=ls, lw=1.6, label=r["name"].split(" (")[0])
        ax[0].plot([r["s_root"]], [1.03], marker="v", color=c, ms=7)
        ax[1].plot(STATIONS, w / r["L"], color=c, ls=ls, lw=1.6, label=r["name"].split(" (")[0])
    ax[0].set_title("Width along the body, as a fraction of the largest width (triangles: mouthpiece station)")
    ax[1].set_title("Width / body length")
    for a_ in ax:
        a_.set_xlabel("station s (0 = bulb end, 1 = tail tip)")
        a_.grid(alpha=0.3)
    ax[0].legend(fontsize=8, loc="lower center")
    fig.tight_layout()
    fig.savefig(HERE / "images" / "02_width_profiles.png")
    plt.close(fig)

    if ec:
        fig, axs = plt.subplots(1, len(ec), figsize=(6.2 * len(ec), 5.6), dpi=110)
        axs = np.atleast_1d(axs)
        for ax, (model, r) in zip(axs, ec.items()):
            o2, h = r["o2"], r["h"]
            nx, nz = r["body"].shape
            xs_ = o2[0] + (np.arange(nx) + 0.5) * h
            zs_ = o2[1] + (np.arange(nz) + 0.5) * h
            ax.contourf(xs_, zs_, r["body"].T.astype(float), levels=[0.5, 1.5], colors=["#d9d2c0"])
            ax.contour(xs_, zs_, r["cav_plan"].T.astype(float), levels=[0.5], colors=["#3b6ea5"], linewidths=0.9, linestyles="--")
            fr = r["fr"]
            ax.plot(*zip(fr["bulb"], fr["tail"]), color="#e08a00", lw=1.2)
            ax.plot(r["track"][:, 0], r["track"][:, 2], color="#c00", lw=2.2)
            ax.plot(*r["root"], "o", mfc="none", mec="#c00", ms=9)
            ax.plot(*r["win"], "x", color="#000", ms=8)
            for n, c in r["holes"].items():
                thumb = n.endswith("thumb")
                ax.plot(c[0], c[2], "o", ms=5, mfc="none" if thumb else "#222", mec="#b00" if thumb else "#222")
                ax.annotate(n.replace("_", " "), (c[0], c[2]), xytext=(3, 4), textcoords="offset points", fontsize=6)
            ax.set_aspect("equal")
            row = next(x for x in rows if x["key"] == model)
            ax.set_title(f"{r['name']}\nneck root s = {row['s_root']:.2f}, windway exit s = {row['s_exit']:.2f}, angle {r['angle']:.0f}°", fontsize=9)
            ax.set_xlabel("model x, mm (the model stands on its mouthpiece; z up)")
        fig.suptitle("Red: windway channel. Ring: neck root. Cross: window patch centre. Orange: body axis. Dashed: cavity.", fontsize=10)
        fig.tight_layout()
        fig.savefig(HERE / "images" / "03_ecan3_windway.png")
        plt.close(fig)

    out["rows"] = [dict(key=r["key"], name=r["name"], length_mm=r["L"], s_root=r["s_root"], s_exit=r.get("s_exit"),
                        s_window=r.get("s_window"), angle_deg=r["angle"], cross_u=r["cross"][0], rel=r["rel"],
                        pitch=r["pitch"], shape=r["shape"], convexity=r["convexity"]) for r in rows]
    out["fits"] = fits
    out["depth"] = depth
    (HERE / "measure_output.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    text = "\n".join(md) + "\n"
    (HERE / "measure_output.md").write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
