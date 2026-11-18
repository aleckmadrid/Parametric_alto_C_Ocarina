"""Photo measurement of the Spencer "Special Edition Series - Ocarina of Time" (12-hole alto C, A4-F6).

    python Analizes_ocarinas/Spencer_OoT_12h/measure_spencer.py

Reads   images/03_top_face_in_box.png         finger face from above, "split" subholes (one per hand). Primary view.
        images/06_top_face_with_songbook.png  finger face, oblique, "single hand" subholes (both on the right hand)
        images/05_top_face_album_cover.png    finger face, oblique, "single hand" subholes
        images/04_back_face_oblique.png       thumb face, strongly oblique
Writes  images/07_annotated_top_face_box.png, images/08_annotated_back_face.png
        measure_output.md, measure_output.json

None of the photos is orthographic and none has a scale bar. The scale is the maker's length, 165 mm, applied to
the longest chord of the body in each photo. Stations along the body (s, 0 at the bulb end, 1 at the tail tip)
are the reliable numbers. Distances across the body depend on how the body is rolled in the photo.
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

LENGTH_MM = 165.0                      # maker: 16.5 cm / 6.5 in
# Landmarks read off the photos by eye (pixel x, y). Holes are snapped to the nearest dark opening.
# neck = the two points where the band skirt meets the body edge; tip = the end of the mouthpiece.
PHOTOS = {
    "03": dict(file="03_top_face_in_box.png", variant="split", neck=((496, 274), (546, 310)), tip=(567, 226),
               holes={"R_pinky": (378, 254), "R_ring": (404, 271), "R_middle": (432, 281), "sub_R": (426, 294),
                      "R_index": (470, 282), "L_index": (440, 347), "L_middle": (470, 343), "sub_L": (512, 338),
                      "L_ring": (503, 354), "L_pinky": (533, 371)}),
    "06": dict(file="06_top_face_with_songbook.png", variant="single hand", neck=((551, 305), (673, 253)), tip=(541, 135),
               holes={"R_index": (590, 324), "sub_Ri": (612, 342), "R_middle": (551, 384), "sub_Rm": (571, 405),
                      "R_ring": (493, 426), "R_pinky": (417, 461), "L_pinky": (814, 318), "L_ring": (760, 342),
                      "L_middle": (710, 384), "L_index": (672, 454)}),
    "05": dict(file="05_top_face_album_cover.png", variant="single hand", neck=((273, 226), (360, 253)), tip=(370, 123),
               holes={"R_pinky": (98, 246), "R_ring": (128, 258), "R_middle": (165, 261), "sub_Rm": (158, 281),
                      "R_index": (218, 245), "sub_Ri": (208, 264), "L_index": (194, 357), "L_middle": (229, 337),
                      "L_ring": (279, 341), "L_pinky": (336, 358)}),
}
BACK = dict(file="04_back_face_oblique.png", neck=((560, 295), (625, 257)), tip=(740, 468),
            holes={"R_thumb": (378, 251), "L_thumb": (628, 121), "window": (547, 236)},
            # apparent size of each opening, px (long x short axis of the visible ellipse), read off a 2x crop
            size_px={"R_thumb": (57, 50), "L_thumb": (43, 35), "window": (37, 20)},
            scoop=((465, 155), (585, 245)), cord_holes=((541, 286), (630, 221)))
FINGERS = ("L_pinky", "L_ring", "L_middle", "L_index", "R_index", "R_middle", "R_ring", "R_pinky")


def load(name):
    im = np.asarray(Image.open(HERE / "images" / name).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    blue = (b > r + 45) & (b > g + 10) & (b > 90)
    return im, im.mean(axis=2), blue


def body_mask(blue):
    lab, n = ndi.label(ndi.binary_opening(blue, iterations=1))
    sizes = ndi.sum(blue, lab, range(1, n + 1))
    return ndi.binary_fill_holes(lab == 1 + int(np.argmax(sizes)))


def feret(mask):
    pts = np.column_stack(np.nonzero(mask)[::-1]).astype(float)
    hull = ConvexHull(pts)
    hp = pts[hull.vertices]
    d = np.linalg.norm(hp[:, None, :] - hp[None, :, :], axis=2)
    i, j = np.unravel_index(np.argmax(d), d.shape)
    return hp[i], hp[j], float(d[i, j]), float(mask.sum() / hull.volume)


def snap(lum, blue, seed, r):
    """Centre of the dark opening nearest the seed, and the long axis (px) of the non-blue region around it
    (None when that region runs into a highlight and leaves the search window)."""
    sx, sy = seed
    y0, x0 = sy - r, sx - r
    win, bw = lum[y0:sy + r + 1, x0:sx + r + 1], blue[y0:sy + r + 1, x0:sx + r + 1]
    dark = win < 70
    lab, n = ndi.label(dark)
    centre = np.array([float(sx), float(sy)])
    if n:
        c = ndi.center_of_mass(dark, lab, range(1, n + 1))
        k = int(np.argmin([math.hypot(cc[1] - r, cc[0] - r) for cc in c]))
        if math.hypot(c[k][1] - r, c[k][0] - r) <= 0.6 * r:
            centre = np.array([x0 + c[k][1], y0 + c[k][0]])
    nb = ~bw
    lab, n = ndi.label(nb)
    major = None
    if n:
        k = lab[int(round(centre[1] - y0)), int(round(centre[0] - x0))]
        if k:
            m = lab == k
            if not (m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any()) and m.sum() > 4:
                yy, xx = np.nonzero(m)
                ev = np.sort(np.linalg.eigvalsh(np.cov(np.vstack([xx, yy]))))[::-1]
                major = 4.0 * math.sqrt(ev[0])
    return centre, major


def frame(mask, mouth_pt):
    p, q, L_px, convexity = feret(mask)
    bulb, tail = (p, q) if np.linalg.norm(p - mouth_pt) < np.linalg.norm(q - mouth_pt) else (q, p)
    e = (tail - bulb) / L_px
    nrm = np.array([-e[1], e[0]])
    if (np.asarray(mouth_pt, float) - bulb) @ nrm < 0:
        nrm = -nrm
    return bulb, tail, e, nrm, L_px, convexity


def top_photo(key):
    ph = PHOTOS[key]
    im, lum, blue = load(ph["file"])
    body = body_mask(blue)
    root = (np.array(ph["neck"][0], float) + np.array(ph["neck"][1], float)) / 2.0
    bulb, tail, e, nrm, L_px, convexity = frame(body, ph["tip"])
    mm = LENGTH_MM / L_px

    def sn(pt):
        d = np.asarray(pt, float) - bulb
        return float(d @ e) / L_px, float(d @ nrm) * mm

    r = max(8, int(round(0.045 * L_px)))
    holes = {}
    for name, seed in ph["holes"].items():
        c, major = snap(lum, blue, seed, r)
        s, n_mm = sn(c)
        holes[name] = dict(px=c.tolist(), s=s, n_mm=n_mm, major_px=major)
    yy, xx = np.nonzero(body)
    d = np.column_stack([xx, yy]) - bulb
    s_px, n_px = d @ e, d @ nrm
    stations = np.linspace(0.0, 1.0, 101)
    half = max(1.0, 0.004 * L_px)
    player = np.array([n_px[np.abs(s_px - s * L_px) <= half].max() * mm for s in stations])
    far = np.array([-n_px[np.abs(s_px - s * L_px) <= half].min() * mm for s in stations])
    tip_s, tip_n = sn(ph["tip"])
    root_s, root_n = sn(root)
    v = np.array(ph["tip"], float) - root
    ang = math.degrees(math.acos(float(v @ e) / np.linalg.norm(v)))
    return dict(key=key, file=ph["file"], variant=ph["variant"], im=im, body=body, bulb=bulb, tail=tail, e=e, nrm=nrm,
                L_px=L_px, mm=mm, convexity=convexity, holes=holes, stations=stations, player=player, far=far,
                root=root, root_s=root_s, root_n=root_n, tip_s=tip_s, tip_n=tip_n, ang=ang,
                neck_width_mm=float(np.linalg.norm(np.subtract(*ph["neck"]))) * mm)


def back_photo(root_station_top):
    im, lum, blue = load(BACK["file"])
    body = body_mask(blue)
    root = (np.array(BACK["neck"][0], float) + np.array(BACK["neck"][1], float)) / 2.0
    bulb, tail, e, nrm, L_px, convexity = frame(body, BACK["tip"])

    def t_of(pt):
        return float((np.asarray(pt, float) - bulb) @ e) / L_px

    # One-dimensional projective correction along the axis: fixes 0 and 1 and maps the neck root to the
    # station measured on the top view. It is a rough correction: it also absorbs the oblique view.
    t_root = t_of(root)
    k = root_station_top * (1.0 - t_root) / (t_root * (1.0 - root_station_top))

    def s_of(t):
        return k * t / (1.0 + (k - 1.0) * t)

    feats = {}
    for name, seed in BACK["holes"].items():
        t = t_of(seed)
        feats[name] = dict(px=list(seed), t=t, s=s_of(t), size_px=BACK["size_px"][name])
    return dict(im=im, bulb=bulb, tail=tail, L_px=L_px, root=root, t_root=t_root, k=k, feats=feats)


def annotate_top(m, path):
    img = Image.fromarray(m["im"].astype(np.uint8)).crop((300, 190, 640, 440)).resize((1360, 1000), Image.LANCZOS)
    d = ImageDraw.Draw(img)

    def P(pt):
        return ((pt[0] - 300) * 4, (pt[1] - 190) * 4)

    d.line([P(m["bulb"]), P(m["tail"])], fill=(255, 140, 0), width=2)
    d.line([P(m["root"]), P(PHOTOS[m["key"]]["tip"])], fill=(0, 220, 0), width=2)
    x, y = P(m["root"])
    d.ellipse([x - 7, y - 7, x + 7, y + 7], outline=(255, 0, 0), width=2)
    for k, h in m["holes"].items():
        x, y = P(h["px"])
        d.text((x - 20, y + 24), k, fill=(255, 255, 255))
    d.text((12, 10), "orange: body axis (longest chord). red: neck root. green: mouthpiece axis. 4x crop.", fill=(255, 255, 255))
    img.save(path, optimize=True)


def annotate_back(b, path):
    img = Image.fromarray(b["im"].astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.line([tuple(b["bulb"]), tuple(b["tail"])], fill=(255, 140, 0), width=2)
    d.line([tuple(b["root"]), BACK["tip"]], fill=(0, 220, 0), width=2)
    d.line([tuple(b["root"]), BACK["holes"]["window"]], fill=(0, 220, 0), width=1)
    for k, f in b["feats"].items():
        x, y = f["px"]
        d.text((x + 22, y - 28), k, fill=(255, 255, 0))
    for x, y in BACK["cord_holes"]:
        d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(255, 255, 0), width=1)
    d.rectangle([BACK["scoop"][0], BACK["scoop"][1]], outline=(255, 255, 255), width=1)
    d.text((12, 10), "orange: body axis. green: mouthpiece axis and its line to the window. white box: labium scoop. "
                     "yellow rings: small holes beside the neck.", fill=(255, 255, 255))
    img.save(path, optimize=True)


def main():
    tops = {k: top_photo(k) for k in PHOTOS}
    m3 = tops["03"]
    back = back_photo(m3["root_s"])
    L = LENGTH_MM
    P = {k: (h["s"] * L, h["n_mm"]) for k, h in m3["holes"].items()}
    hm = ergo.hand_metrics(P)
    a = np.array(hm["a"])
    pitch = float(np.mean(hm["L"]["pitches"] + hm["R"]["pitches"]))
    root_xy = np.array([m3["root_s"] * L, m3["root_n"]])
    rel = {k: float((root_xy - np.array(P[k])) @ a) for k in ("L_pinky", "L_ring", "L_middle", "L_index", "R_index")}
    width = m3["player"] + m3["far"]
    i_w = int(np.argmax(width))

    # hole sizes: photo 06 is the largest view. Its local scale comes from the finger pitches of photo 03
    # (the eight finger holes are taken to sit in the same places on both subhole variants).
    def local_scale(m, hand):
        names = [n for n in FINGERS if n.startswith(hand)]
        px = sum(np.linalg.norm(np.subtract(m["holes"][a_]["px"], m["holes"][b_]["px"])) for a_, b_ in zip(names, names[1:]))
        ref = sum(np.linalg.norm(np.subtract(m3["holes"][a_]["px"], m3["holes"][b_]["px"])) for a_, b_ in zip(names, names[1:])) * m3["mm"]
        return ref / px

    sizes = {}
    for key in ("06", "05"):
        m = tops[key]
        sc = {"L": local_scale(m, "L"), "R": local_scale(m, "R")}
        for n, h in m["holes"].items():
            hand = "L" if n.startswith("L") else "R"
            sizes.setdefault(n, {})[key] = None if h["major_px"] is None else h["major_px"] * sc[hand]
    for n, h in m3["holes"].items():
        sizes.setdefault(n, {})["03"] = None if h["major_px"] is None else h["major_px"] * m3["mm"]

    out = dict(
        name="Spencer OoT 12-hole alto C (photos, 165 mm scale)", length_mm=L, mm_per_px=m3["mm"],
        stations=m3["stations"].tolist(), player_half_mm=m3["player"].tolist(), far_half_mm=m3["far"].tolist(),
        max_width_mm=float(width.max()), max_width_station=float(m3["stations"][i_w]), convexity=m3["convexity"],
        mouthpiece=dict(root_station=m3["root_s"], root_across_mm=m3["root_n"], tip_station=m3["tip_s"],
                        angle_to_body_axis_deg=m3["ang"], neck_width_mm=m3["neck_width_mm"],
                        root_station_by_photo={k: tops[k]["root_s"] for k in tops},
                        angle_by_photo={k: tops[k]["ang"] for k in tops}),
        holes={k: dict(X=P[k][0], Y=P[k][1], s=m3["holes"][k]["s"]) for k in P},
        hole_stations_by_photo={k: {n: h["s"] for n, h in tops[k]["holes"].items()} for k in tops},
        hole_sizes_mm=sizes, mouthpiece_from_holes_along_hand_axis_mm=rel, mean_finger_pitch_mm=pitch,
        back=dict(k=back["k"], t_root=back["t_root"], feats={k: dict(t=f["t"], s=f["s"], size_px=f["size_px"]) for k, f in back["feats"].items()}),
    )
    (HERE / "measure_output.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    annotate_top(m3, HERE / "images" / "07_annotated_top_face_box.png")
    annotate_back(back, HERE / "images" / "08_annotated_back_face.png")

    def f1(v, nd=1):
        return "–" if v is None else f"{v:.{nd}f}"

    md = ["# Spencer OoT 12-hole alto C: measured numbers (generated by measure_spencer.py)", "",
          "Scale: 165 mm on the longest chord of the body in each photo. s = station along the body axis, 0 at the bulb end, "
          "1 at the tail tip. No photo is orthographic: stations are good to about ±0.02 on photo 03 and ±0.04 on the "
          "oblique ones; distances across the body depend on the roll of the body in the photo.", "",
          "## 1. Outline and mouthpiece", "",
          "| Photo | Subholes | Longest chord px | mm/px | Outline area / hull area | Neck root station | Mouthpiece axis against the body axis (apparent) |",
          "|---|---|---|---|---|---|---|"]
    for k, m in tops.items():
        md.append(f"| {m['file']} | {m['variant']} | {m['L_px']:.0f} | {m['mm']:.3f} | {m['convexity']:.3f} | **{m['root_s']:.3f}** | {m['ang']:.0f}° |")
    md += ["", f"Photo 03: largest apparent width {width.max():.1f} mm at s = {m3['stations'][i_w]:.2f} (width / length {width.max() / L:.3f}); "
           f"neck width at the body {m3['neck_width_mm']:.1f} mm. The apparent width is the width of the rolled body, see the write-up.", "",
           "Half widths from the body axis on photo 03 (mm, apparent):", "",
           "| s | " + " | ".join(f"{s:.1f}" for s in m3["stations"][::10]) + " |", "|---|" + "---|" * 11,
           "| player side | " + " | ".join(f"{v:.1f}" for v in m3["player"][::10]) + " |",
           "| far side | " + " | ".join(f"{v:.1f}" for v in m3["far"][::10]) + " |",
           "| width | " + " | ".join(f"{v:.1f}" for v in width[::10]) + " |", "",
           "The player-side row near the neck (s 0.3–0.45) includes the band skirt.", "",
           "## 2. Finger holes: stations on the three photos", "",
           "| Hole | s, photo 03 (split) | s, photo 06 (single hand) | s, photo 05 (single hand) | X mm (03) | Y mm (03, apparent) |", "|---|---|---|---|---|---|"]
    names = ["L_pinky", "L_ring", "sub_L", "L_middle", "L_index", "R_index", "sub_Ri", "R_middle", "sub_R", "sub_Rm", "R_ring", "R_pinky"]
    for n in names:
        cells = [f1(tops[k]["holes"][n]["s"], 3) if n in tops[k]["holes"] else "–" for k in ("03", "06", "05")]
        xy = (f1(P[n][0]), f1(P[n][1])) if n in P else ("–", "–")
        md.append(f"| {n} | {cells[0]} | {cells[1]} | {cells[2]} | {xy[0]} | {xy[1]} |")
    md += ["", "sub_L and sub_R: the split variant. sub_Ri and sub_Rm: the single-hand variant (beside R index and R middle).", "",
           "## 3. Hole sizes (rough)", "",
           "Long axis of the unglazed opening (rim and bore), mm. Photo 03 uses the 165 mm scale. Photos 06 and 05 use a local "
           "scale per hand, set so that their finger pitches equal those of photo 03. A dash: the opening merges with a highlight. "
           "Treat every value as ±15 %.", "",
           "| Hole | Photo 03 | Photo 06 | Photo 05 | Mean | Mean / body length |", "|---|---|---|---|---|---|"]
    mean_sizes = {}
    for n in names:
        v = [sizes.get(n, {}).get(k) for k in ("03", "06", "05")]
        ok = [x for x in v if x is not None]
        mean_sizes[n] = float(np.mean(ok)) if ok else None
        md.append(f"| {n} | {f1(v[0])} | {f1(v[1])} | {f1(v[2])} | {('**' + f1(mean_sizes[n]) + '**') if ok else '–'} | "
                  f"{f1(mean_sizes[n] / L, 4) if ok else '–'} |")
    out["hole_sizes_mean_mm"] = mean_sizes
    (HERE / "measure_output.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    md += ["", "## 4. Hand layout from photo 03 (ocarina_addon/ergonomics.py, plan view)", "", "| Metric | Value |", "|---|---|",
           f"| Angle between the hand lines | {hm['hands_angle']:.1f}° |",
           f"| Right line nearer the player by | {hm['line_offset']:.1f} mm (apparent) |",
           f"| Pinky to pinky | {hm['pinky_span']:.1f} mm |",
           f"| L pitches P→R→M→I | {' / '.join(f'{x:.1f}' for x in hm['L']['pitches'])} |",
           f"| R pitches P→R→M→I | {' / '.join(f'{x:.1f}' for x in hm['R']['pitches'])} |",
           f"| L span / R span | {hm['L']['span']:.1f} / {hm['R']['span']:.1f} mm |",
           f"| Index holes: across / along | {hm['index_across']:.1f} / {hm['index_along']:.1f} mm |"]
    for key in ("sub_L", "sub_R"):
        s = hm.get(key)
        if s:
            md.append(f"| {key} | from {s['parent']}, {s['dist']:.1f} mm, {s['off_normal_deg']:.0f}° off the hand line's normal |")
    md += ["", "## 5. Mouthpiece against the holes (photo 03)", "",
           "Distance along the hand axis from each hole centre to the mouthpiece neck root (+ = the mouthpiece is toward the tail).", "",
           f"| From | mm | in mean finger pitches ({pitch:.1f} mm) |", "|---|---|---|"]
    md += [f"| {k} | {v:+.1f} | {v / pitch:+.2f} |" for k, v in rel.items()]
    md += ["", "## 6. Thumb face (photo 04, strongly oblique: rough)", "",
           f"Apparent station t = position along the body axis in the picture. Corrected station s = t after a one-dimensional "
           f"projective correction that puts the neck root (t = {back['t_root']:.3f}) at the station of photo 03 "
           f"({m3['root_s']:.3f}); correction factor k = {back['k']:.2f}. The true station lies between the two columns.", "",
           "| Feature | Apparent t | Corrected s | Apparent size px (long × short) |", "|---|---|---|---|"]
    for k, f in back["feats"].items():
        md.append(f"| {k} | {f['t']:.3f} | {f['s']:.3f} | {f['size_px'][0]} × {f['size_px'][1]} |")
    text = "\n".join(md) + "\n"
    (HERE / "measure_output.md").write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
