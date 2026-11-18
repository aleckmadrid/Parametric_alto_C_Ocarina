"""Photo measurement of the Songbird "Ocarina of Time" 12-hole ocarinas (Alto C and Tenor A).

    python Analizes_ocarinas/Songbird_OoT_12h/measure_songbird.py

The maker sells one design in two sizes. The photos were sorted by the owner on 2026-11-16:

    altoC_*    the Alto C (A4-F6). altoC_01 is the main picture of the maker's Alto C page.
    tenorA_*   the Tenor A (larger and lower): frames of the review video. Not measured here.
    unsorted_* model not known. Not used.

Reads   images/altoC_01_top_face_product.png   finger face, near-orthographic cut-out, mouthpiece up, tail to the left
        images/altoC_05_video_thumb_face.png   thumb face, oblique video frame (rough)
Writes  images/altoC_08_annotated_top_face.png, images/altoC_09_annotated_thumb_face.png
        measure_output.md, measure_output.json (read by ../Windway_and_body_shape/measure_body_windway.py)

Scale. The maker gives no size for the Alto C. Everything is measured as a fraction of the body length
(the longest chord of the body outline). Millimetres are given for two lengths:
    170 mm    the Alto C, an ESTIMATE (see the write-up; the evidence allows 152 to 181 mm)
    203.2 mm  the Tenor A (maker: 8 in), on the ASSUMPTION that it is the same design scaled up

Frame of the tables: the player's view of the finger face. s runs along the body axis from the bulb end
(0) to the tail tip (1). n is across the body, + toward the player (the mouthpiece side).
Needs Pillow, numpy and scipy.
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
from ocarina_addon import ergonomics as ergo  # noqa: E402  (standard library only)

IMG = HERE / "images" / "altoC_01_top_face_product.png"
IMG_BACK = HERE / "images" / "altoC_05_video_thumb_face.png"
ALTO_C_LENGTH_MM = 170.0             # estimate (152 to 181 mm); the maker gives none
TENOR_A_LENGTH_MM = 203.2            # maker: 8 in L x 3 in W x 2.25 in thickness, "just under 1 lb"
TENOR_A_WIDTH_MM, TENOR_A_THICK_MM = 76.2, 57.15
LENGTH_MM = ALTO_C_LENGTH_MM         # the millimetres of the tables and of the JSON file
CANDIDATE_LENGTHS_MM = (152.4, 165.0, 170.0, 181.0, 203.2)
# Thumb face, photo altoC_05 (pixel x, y read off the frame; another ocarina in the background is ignored).
BACK = dict(tail=(60, 130), bulb=(1178, 465), neck_root=(790, 595), tip=(720, 880),
            feats={"R_thumb": ((573, 303), 96), "L_thumb": ((1012, 430), 94), "window_recess": ((832, 505), 190)})
# Seeds (pixel x, y) read off the photo; the code snaps each to the nearest opening.
SEEDS = {
    "R_pinky": (226, 767), "R_ring": (340, 768), "R_middle": (449, 741), "sub_R": (463, 797), "R_index": (559, 670),
    "L_index": (735, 889), "L_middle": (856, 837), "L_ring": (985, 812), "sub_L": (970, 739), "L_pinky": (1125, 805),
}
ORDER = ("sub_L", "sub_R", "R_pinky", "R_ring", "R_middle", "R_index", "L_pinky", "L_ring", "L_middle", "L_index")


def feret(points):
    """Longest chord of a point set: (p, q, length)."""
    hull = points[ConvexHull(points).vertices]
    d = np.linalg.norm(hull[:, None, :] - hull[None, :, :], axis=2)
    i, j = np.unravel_index(np.argmax(d), d.shape)
    return hull[i], hull[j], float(d[i, j])


def ellipse_axes(mask):
    """Full major and minor axis (px) of the ellipse with the same second moments as the region."""
    yy, xx = np.nonzero(mask)
    cov = np.cov(np.vstack([xx, yy]))
    ev = np.sort(np.linalg.eigvalsh(cov))[::-1]
    return 4.0 * math.sqrt(ev[0]), 4.0 * math.sqrt(ev[1])


def measure():
    im = np.asarray(Image.open(IMG).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    lum = im.mean(axis=2)
    obj = ~((r > 246) & (g > 246) & (b > 246))
    lab, n = ndi.label(obj)
    obj = lab == (1 + int(np.argmax(ndi.sum(obj, lab, range(1, n + 1)))))
    obj = ndi.binary_fill_holes(obj)
    H, W = obj.shape
    xs_all = np.nonzero(obj.any(axis=0))[0]
    top = np.array([np.nonzero(obj[:, x])[0].min() if obj[:, x].any() else -1 for x in range(W)])
    bot = np.array([np.nonzero(obj[:, x])[0].max() if obj[:, x].any() else -1 for x in range(W)])

    # the neck: where the upper edge leaves the body. Walk in from both ends until the edge jumps.
    x0, x1 = int(xs_all.min()), int(xs_all.max())
    neck_l = next(x for x in range(x0 + 60, x1) if top[x - 6] - top[x] > 14)
    neck_r = next(x for x in range(x1 - 60, x0, -1) if top[x + 6] - top[x] > 14)
    neck_l -= 6
    neck_r += 6
    # the hidden body edge under the neck: a cubic through the visible edge on both sides
    fit_x = np.r_[np.arange(neck_l - 160, neck_l - 4), np.arange(neck_r + 4, neck_r + 120)]
    coef = np.polyfit(fit_x, top[fit_x], 3)
    edge = np.polyval(coef, np.arange(W))
    body = obj.copy()
    for x in range(neck_l, neck_r + 1):
        body[: int(round(edge[x])), x] = False
    mouth = obj & ~body

    # body axis: the longest chord. Bulb end = the end near the mouthpiece.
    by, bx = np.nonzero(body ^ ndi.binary_erosion(body))
    p, q, L_px = feret(np.column_stack([bx, by]).astype(float))
    my, mx = np.nonzero(mouth)
    mc = np.array([mx.mean(), my.mean()])
    bulb, tail = (p, q) if np.linalg.norm(p - mc) < np.linalg.norm(q - mc) else (q, p)
    e = (tail - bulb) / L_px                        # along the body, bulb -> tail
    nrm = np.array([-e[1], e[0]])
    if (mc - bulb) @ nrm < 0:
        nrm = -nrm                                  # + toward the player (the mouthpiece side)
    mm = LENGTH_MM / L_px

    def sn(pt):
        d = np.asarray(pt, float) - bulb
        return float(d @ e) / L_px, float(d @ nrm) * mm

    # outline: half widths on both sides of the axis, at 101 stations
    yy, xx = np.nonzero(body)
    d = np.column_stack([xx, yy]) - bulb
    s_px, n_px = d @ e, d @ nrm
    stations = np.linspace(0.0, 1.0, 101)
    player, far = [], []
    for s in stations:
        sel = np.abs(s_px - s * L_px) <= 1.0
        player.append(float(n_px[sel].max()) * mm if sel.any() else 0.0)
        far.append(float(-n_px[sel].min()) * mm if sel.any() else 0.0)
    player, far = np.array(player), np.array(far)
    width = player + far

    # mouthpiece
    tip_row = int(my.min())
    tip = np.array([mx[my <= tip_row + 3].mean(), float(tip_row)])
    root = np.array([(neck_l + neck_r) / 2.0, edge[(neck_l + neck_r) // 2]])
    cap = mouth.copy()
    cap[tip_row + 120:, :] = False                  # the blue cap only (above the band)
    cy, cx = np.nonzero(cap)
    cap_c = np.array([cx.mean(), cy.mean()])
    axis_v = (cap_c - root) / np.linalg.norm(cap_c - root)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, float(axis_v @ e)))))   # 90 = square to the body; < 90 leans to the tail
    rows = np.arange(tip_row, int(edge[(neck_l + neck_r) // 2]))
    wrow = np.array([mouth[y].sum() for y in rows])
    blue = (b > r + 40) & (b > g + 15)
    band_rows = [y for y in rows if (mouth[y] & ~blue[y]).sum() > 0.5 * mouth[y].sum()]

    # holes: regions inside the body that are not glaze blue (unglazed rim and the dark bore)
    notblue = ndi.binary_opening(body & ~blue, iterations=1)
    hl, hn = ndi.label(notblue)
    cents = ndi.center_of_mass(notblue, hl, range(1, hn + 1))
    holes = {}
    for name, seed in SEEDS.items():
        k = 1 + int(np.argmin([math.hypot(c[1] - seed[0], c[0] - seed[1]) for c in cents]))
        m = hl == k
        c = np.array([cents[k - 1][1], cents[k - 1][0]])
        assert math.hypot(c[0] - seed[0], c[1] - seed[1]) < 12, name
        major, minor = ellipse_axes(m)
        core = m & (lum < 110)
        holes[name] = dict(px=c.tolist(), s=sn(c)[0], n_mm=sn(c)[1], d_rim_major=major * mm, d_rim_minor=minor * mm,
                           d_rim_area=2.0 * math.sqrt(m.sum() / math.pi) * mm,
                           d_core_area=2.0 * math.sqrt(core.sum() / math.pi) * mm)
    return dict(im=im, obj=obj, body=body, mouth=mouth, bulb=bulb, tail=tail, e=e, nrm=nrm, L_px=L_px, mm=mm, sn=sn,
                stations=stations, player=player, far=far, width=width, tip=tip, root=root, cap_c=cap_c, ang=ang,
                neck=(neck_l, neck_r), edge=edge, wrow=wrow, rows=rows, band_rows=band_rows, holes=holes)


def thumb_face(root_station):
    """Stations on the oblique thumb-face frame: as they appear (t) and after a one-dimensional projective
    correction that puts the neck root at the station measured on the finger face (s). Sizes are the long
    axis of each rim as a fraction of the apparent body length."""
    tail, bulb = np.array(BACK["tail"], float), np.array(BACK["bulb"], float)
    L_px = float(np.linalg.norm(tail - bulb))
    e = (tail - bulb) / L_px

    def t_of(pt):
        return float((np.asarray(pt, float) - bulb) @ e) / L_px

    t_root = t_of(BACK["neck_root"])
    k = root_station * (1.0 - t_root) / (t_root * (1.0 - root_station))
    out = {}
    for name, (pt, size_px) in BACK["feats"].items():
        tt = t_of(pt)
        out[name] = dict(px=list(pt), t=tt, s=k * tt / (1.0 + (k - 1.0) * tt), size_frac=size_px / L_px, size_px=size_px)
    return dict(L_px=L_px, t_root=t_root, k=k, feats=out)


def annotate_back(path):
    img = Image.open(IMG_BACK).convert("RGB")
    d = ImageDraw.Draw(img)
    d.line([BACK["bulb"], BACK["tail"]], fill=(255, 140, 0), width=3)
    d.line([BACK["tip"], BACK["neck_root"], BACK["feats"]["window_recess"][0]], fill=(0, 220, 0), width=3)
    x, y = BACK["neck_root"]
    d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(255, 0, 0), width=3)
    for name, (pt, size_px) in BACK["feats"].items():
        r = size_px / 2
        d.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], outline=(255, 255, 0), width=2)
        d.text((pt[0] - 30, pt[1] - r - 16), name, fill=(255, 255, 0))
    d.text((12, 10), "orange: body axis. green: mouthpiece axis to the window. red: neck root. yellow: thumb holes and the window recess.",
           fill=(255, 255, 255))
    img.save(path, optimize=True)


def player_frame(m):
    """Hole centres in the player's view: X from the bulb end toward the tail, Y toward the player (mm)."""
    L = LENGTH_MM
    return {k: (h["s"] * L, h["n_mm"]) for k, h in m["holes"].items()}


def annotate(m, path):
    img = Image.fromarray(m["im"].astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.line([tuple(m["bulb"]), tuple(m["tail"])], fill=(255, 140, 0), width=2)
    nl, nr = m["neck"]
    d.line([(x, m["edge"][x]) for x in range(nl - 40, nr + 41)], fill=(255, 0, 0), width=2)
    d.line([tuple(m["root"]), tuple(m["tip"])], fill=(0, 160, 0), width=2)
    r0 = m["root"]
    d.ellipse([r0[0] - 6, r0[1] - 6, r0[0] + 6, r0[1] + 6], outline=(255, 0, 0), width=2)
    for k, h in m["holes"].items():
        x, y = h["px"]
        d.text((x - 22, y + 30), f"{k} {h['d_rim_major']:.1f}", fill=(255, 255, 255))
    d.text((40, 990), "orange: body axis (longest chord). red: body edge under the neck (cubic fit) and neck root. "
                      "green: mouthpiece axis.", fill=(0, 0, 0))
    d.text((40, 1010), f"Alto C. Scale {m['mm']:.4f} mm/px for an estimated length of {LENGTH_MM:.0f} mm. Labels: hole, rim diameter (major axis) in mm.",
           fill=(0, 0, 0))
    img.save(path, optimize=True)


def main():
    m = measure()
    L = LENGTH_MM
    kT = TENOR_A_LENGTH_MM / L
    s_root, n_root = m["sn"](m["root"])
    s_tip, n_tip = m["sn"](m["tip"])
    i_w = int(np.argmax(m["width"]))
    P = player_frame(m)
    hm = ergo.hand_metrics(P)
    pitch = float(np.mean(hm["L"]["pitches"] + hm["R"]["pitches"]))
    hull_pts = np.column_stack(np.nonzero(m["body"])[::-1]).astype(float)
    convexity = float(m["body"].sum() / ConvexHull(hull_pts).volume)
    back = thumb_face(s_root)
    w_frac = float(m["width"].max() / L)
    mp = dict(root_station=s_root, root_across_mm=n_root, tip_station=s_tip, tip_across_mm=n_tip,
              angle_to_body_axis_deg=m["ang"], neck_width_mm=(m["neck"][1] - m["neck"][0]) * m["mm"],
              cap_width_mm=float(np.median(m["wrow"][20:100])) * m["mm"],
              band_height_mm=len(m["band_rows"]) * m["mm"], height_above_body_mm=float(n_tip - n_root))

    out = dict(
        name="Songbird OoT 12-hole Alto C (photo; length estimated 170 mm)", length_mm=L, length_is_estimate=True,
        length_bounds_mm=[152.4, 181.0], mm_per_px=m["mm"],
        stations=m["stations"].tolist(), player_half_mm=m["player"].tolist(), far_half_mm=m["far"].tolist(),
        max_width_mm=float(m["width"].max()), max_width_station=float(m["stations"][i_w]), width_over_length=w_frac,
        convexity=convexity, mouthpiece=mp,
        holes={k: dict(X=P[k][0], Y=P[k][1], **{kk: vv for kk, vv in h.items() if kk != "px"}) for k, h in m["holes"].items()},
        mean_finger_pitch_mm=pitch,
        thumb_face=dict(k=back["k"], t_root=back["t_root"],
                        feats={k: {kk: vv for kk, vv in f.items() if kk != "px"} for k, f in back["feats"].items()}),
        tenor_a=dict(name="Songbird OoT 12-hole Tenor A (maker's size; same design assumed)", length_mm=TENOR_A_LENGTH_MM,
                     width_maker_mm=TENOR_A_WIDTH_MM, thickness_maker_mm=TENOR_A_THICK_MM,
                     tw_maker=TENOR_A_THICK_MM / TENOR_A_WIDTH_MM,
                     tw_with_measured_width=TENOR_A_THICK_MM / (w_frac * TENOR_A_LENGTH_MM), scale_from_alto_c=kT),
    )
    (HERE / "measure_output.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    annotate(m, HERE / "images" / "altoC_08_annotated_top_face.png")
    annotate_back(HERE / "images" / "altoC_09_annotated_thumb_face.png")

    def row(label, mm_value):
        return f"| {label} | {mm_value / L:.3f} | {mm_value:.1f} mm | {mm_value * kT:.1f} mm |"

    overall = n_tip + float(m["far"].max())
    md = ["# Songbird OoT 12-hole, Alto C and Tenor A: measured numbers (generated by measure_songbird.py)", "",
          f"Measured on the Alto C cut-out (longest chord of the body {m['L_px']:.0f} px). The maker gives no size for the Alto C: "
          f"millimetres are for an **estimated** length of {L:.0f} mm (the evidence allows 152–181 mm). The Tenor A column takes the "
          f"maker's 203.2 mm and **assumes the same design scaled up** (× {kT:.3f}). "
          "s = station along the body axis, 0 at the bulb end, 1 at the tail tip. Across is + toward the player.", "",
          "## 1. Outline and mouthpiece", "",
          "| Item | Fraction of the body length | Alto C at 170 mm | Tenor A at 203.2 mm |", "|---|---|---|---|",
          row(f"Largest body width, at s = {m['stations'][i_w]:.2f} (maker, Tenor A: 3 in = 76 mm)", float(m["width"].max())),
          row("Mouthpiece neck root, from the bulb end", s_root * L),
          row("Neck root, distance from the body axis", n_root),
          row("Mouthpiece tip above the body edge", n_tip - n_root),
          row("Overall height, far edge to mouthpiece tip", overall),
          row("Neck width at the body (band skirt)", mp["neck_width_mm"]),
          row("Cap width", mp["cap_width_mm"]),
          row("Band height", mp["band_height_mm"]),
          "", f"Mouthpiece neck root station: **{s_root:.3f}**. Mouthpiece axis against the body axis, in this view: {m['ang']:.1f}° "
          f"(90° = square). Outline area / convex hull area: {convexity:.4f} (1 = no concave part).", "",
          "Half widths from the body axis, as fractions of the body length:", "",
          "| s | " + " | ".join(f"{s:.1f}" for s in m["stations"][::10]) + " |", "|---|" + "---|" * 11,
          "| player side | " + " | ".join(f"{v / L:.3f}" for v in m["player"][::10]) + " |",
          "| far side | " + " | ".join(f"{v / L:.3f}" for v in m["far"][::10]) + " |",
          "| width | " + " | ".join(f"{v / L:.3f}" for v in m["width"][::10]) + " |", "",
          "The player-side row between s = 0.25 and 0.45 is the cubic fit under the neck, not a visible edge.", "",
          "## 2. Finger holes", "",
          "Rim = the whole unglazed opening (white rim and dark bore), long axis of the equivalent ellipse. Core = the dark part only. "
          "The bore is between the two. Across: from the body axis toward the player.", "",
          "| Hole | Station s | Across / length | Rim Ø / length | Rim Ø, Alto C at 170 | Dark core Ø, Alto C | Rim Ø, Tenor A at 203.2 |",
          "|---|---|---|---|---|---|---|"]
    for k in ORDER:
        h = m["holes"][k]
        md.append(f"| {k} | {h['s']:.3f} | {h['n_mm'] / L:+.3f} | {h['d_rim_major'] / L:.4f} | **{h['d_rim_major']:.1f}** | "
                  f"{h['d_core_area']:.1f} | {h['d_rim_major'] * kT:.1f} |")
    md += ["", "## 3. Hand layout (ocarina_addon/ergonomics.py, plan view) at candidate body lengths", "",
           "The layout is one measurement; only the scale changes. 152.4 mm = 6 in (the first number of the retail listing the owner "
           "quoted), 165 mm = the Spencer, 170 mm = the estimate used here, 181 mm = the inside of the maker's chest, 203.2 mm = the Tenor A.", "",
           "| Body length | Pinky to pinky | L pitches P→R→M→I | R pitches P→R→M→I | L span / R span | Rows apart, across | Index holes along | sub_L from L ring | sub_R from R middle |",
           "|---|---|---|---|---|---|---|---|---|"]
    for Lc in CANDIDATE_LENGTHS_MM:
        c = Lc / L
        md.append(f"| {Lc:.1f} mm | {hm['pinky_span'] * c:.1f} | {' / '.join(f'{x * c:.1f}' for x in hm['L']['pitches'])} | "
                  f"{' / '.join(f'{x * c:.1f}' for x in hm['R']['pitches'])} | {hm['L']['span'] * c:.1f} / {hm['R']['span'] * c:.1f} | "
                  f"{hm['line_offset'] * c:.1f} | {hm['index_along'] * c:+.1f} | {hm['sub_L']['dist'] * c:.1f} | {hm['sub_R']['dist'] * c:.1f} |")
    md += ["", f"Angle between the two hand lines: {hm['hands_angle']:.1f}°. sub_L is {hm['sub_L']['off_normal_deg']:.0f}° and sub_R "
           f"{hm['sub_R']['off_normal_deg']:.0f}° off the normal of its hand line.", "",
           "## 4. Thumb face (photo altoC_05, oblique video frame: rough)", "",
           f"t = station as it appears along the body axis of the frame. s = after a one-dimensional projective correction that puts the "
           f"neck root (t = {back['t_root']:.3f}) at the station of section 1 ({s_root:.3f}); factor k = {back['k']:.2f}. The truth lies between.", "",
           "| Feature | Apparent t | Corrected s | Rim, fraction of the apparent body length | At 170 mm |", "|---|---|---|---|---|"]
    for k, f in back["feats"].items():
        md.append(f"| {k} | {f['t']:.3f} | {f['s']:.3f} | {f['size_frac']:.3f} | {f['size_frac'] * L:.0f} mm |")
    text = "\n".join(md) + "\n"
    (HERE / "measure_output.md").write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
