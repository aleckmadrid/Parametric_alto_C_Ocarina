"""Hole-layout comparison: shared reference photos, the Miracle AO10-AC and the add-on bodies.

    python Analizes_ocarinas/Ergonomic_reference_12hole/measure_reference.py

Reads:
  images/04_top_face_yellow_orthographic.png   near-orthographic top view (mouthpiece up, bulb right)
  images/02_hand_hold_top_face.png             player view, perspective and motion blur (rough check)
  images/03_held_top_face_mouthpiece_up.png    top view held at arm's length, mild perspective (rough check)
  ../Miracle_M/Miracle_M.md section 4.2        (numbers copied below)
  ../../addon_checks/P*-80.json                the add-on's built hole centres
Writes:
  images/10_annotated_yellow.png               hole names on photo 04
  measure_output.md                            the comparison tables

Frame used for every layout: player view of the top face. x runs along the body from the bulb (left-hand)
end toward the tail; y runs toward the player. Hole names follow the standard 12-hole order. The two index
holes sit almost on one line across the body, so they are named by hand arch (each hand's four holes form
a smooth arc), not by x order.

Scale. The photos have no scale. Every photo layout is given in units of its own pinky-to-pinky span along x,
and in mm scaled to the Miracle's span (104.2 mm). Photo 04 is also given per body length.
Needs Pillow and numpy.
"""
from __future__ import annotations

import json
import math
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from ocarina_addon import cavity_math, presets  # noqa: E402  (standard library modules; no Blender needed)

LEFT = ("L_pinky", "L_ring", "L_middle", "L_index")
RIGHT = ("R_pinky", "R_ring", "R_middle", "R_index")
MIRACLE_SPAN_MM = 117.2 - 13.0

# Miracle AO10-AC, Miracle_M.md section 4.2: x from the bulb end, y from the far edge toward the player (mm).
MIRACLE = {
    "L_pinky": (13.0, 25.6), "L_ring": (30.1, 24.4), "L_middle": (47.3, 20.3), "L_index": (61.8, 11.1),
    "R_index": (67.0, 34.6), "R_middle": (82.5, 24.3), "R_ring": (100.1, 20.6), "R_pinky": (117.2, 20.3),
    "sub_L": (64.4, 26.3), "sub_R": (79.0, 17.9),
    "L_thumb": (23.2, 25.8), "R_thumb": (74.0, 21.2),
}
MIRACLE_LENGTH_MM = 150.0

# Seeds (pixel x, y) for each hole, read off the photos by eye; the code snaps to the dark opening.
SEEDS = {
    "04": {"L_pinky": (732, 489), "L_ring": (627, 481), "sub_L": (619, 422), "L_middle": (519, 489),
           "L_index": (417, 512), "R_index": (448, 355), "sub_R": (381, 444), "R_middle": (360, 402),
           "R_ring": (268, 425), "R_pinky": (176, 428)},
    "02": {"L_pinky": (148, 180), "L_ring": (222, 182), "sub_L": (219, 228), "L_middle": (310, 183),
           "L_index": (382, 155), "R_index": (400, 295), "sub_R": (472, 237), "R_middle": (480, 275),
           "R_ring": (543, 262), "R_pinky": (613, 262)},
    "03": {"L_pinky": (596, 418), "L_ring": (510, 430), "sub_L": (497, 390), "L_middle": (434, 470),
           "L_index": (373, 513), "R_index": (333, 372), "sub_R": (277, 449), "R_middle": (268, 410),
           "R_ring": (196, 438), "R_pinky": (133, 453)},
}
FILES = {"04": "04_top_face_yellow_orthographic.png", "02": "02_hand_hold_top_face.png",
         "03": "03_held_top_face_mouthpiece_up.png"}
# photo orientation -> player frame: "up" = mouthpiece at the image top (rotate 180 deg), "down" = player view
ORIENT = {"04": "up", "02": "down", "03": "up"}


def lum_of(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(float).mean(axis=2)


def snap(lum, seed, r=26):
    """Centroid and area-equivalent diameter (px) of the dark opening nearest to `seed`."""
    sx, sy = seed
    H, W = lum.shape
    x0, x1, y0, y1 = max(0, sx - r), min(W, sx + r + 1), max(0, sy - r), min(H, sy + r + 1)
    win = lum[y0:y1, x0:x1]
    thr = 0.62 * np.median(win)
    mask = win < thr
    best, best_d = None, 1e9
    seen = np.zeros_like(mask)
    for yy in range(mask.shape[0]):
        for xx in range(mask.shape[1]):
            if mask[yy, xx] and not seen[yy, xx]:
                q = deque([(yy, xx)]); seen[yy, xx] = True; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True; q.append((ny, nx))
                if len(pts) < 6:
                    continue
                p = np.array(pts)
                c = p.mean(axis=0)
                d = math.hypot(c[1] + x0 - sx, c[0] + y0 - sy)
                if d < best_d:
                    best, best_d = p, d
    if best is None:
        return float(sx), float(sy), float("nan")
    c = best.mean(axis=0)
    return float(c[1] + x0), float(c[0] + y0), 2.0 * math.sqrt(len(best) / math.pi)


def photo_layout(key):
    path = HERE / "images" / FILES[key]
    lum = lum_of(path)
    pts = {n: snap(lum, s) for n, s in SEEDS[key].items()}
    # Player frame. Mouthpiece-up photo: the bulb is at the image right and the player at the image top, so
    # x from the bulb = -cx and y toward the player = -cy (a 180-degree turn, not a mirror).
    # Player-view photo: the bulb is at the image left and the player at the image bottom: x = cx, y = cy.
    up = ORIENT[key] == "up"
    out = {n: ((-cx, -cy, d) if up else (cx, cy, d)) for n, (cx, cy, d) in pts.items()}
    return pts, out


def metrics(L):
    """Ergonomic layout metrics. L: name -> (x, y toward the player, ...) in one unit."""
    P = {n: np.array(v[:2], float) for n, v in L.items()}
    m = {}
    for hand, names, ext in (("left", LEFT, +1.0), ("right", RIGHT, -1.0)):
        # ext: direction of finger extension in y (left hand comes from the far side, so its tips point
        # toward the player, +y; the right hand comes from the player side, tips point to the far side, -y)
        p = [P[n] for n in names]
        pitches = [float(np.linalg.norm(p[i + 1] - p[i])) for i in range(3)]
        chord = p[3] - p[0]
        u = chord / np.linalg.norm(chord)
        nrm = np.array([-u[1], u[0]])
        if nrm[1] * ext < 0:
            nrm = -nrm
        sag = [float((p[i] - p[0]) @ nrm) for i in (1, 2)]
        tilt = math.degrees(math.atan2(-(p[3][1] - p[0][1]), abs(p[3][0] - p[0][0])))   # + = index end toward the far side
        m[hand] = dict(pitches=pitches, span=float(np.linalg.norm(chord)), tilt_deg=tilt, sag_ring=sag[0], sag_middle=sag[1])
        sub = "sub_L" if hand == "left" else "sub_R"
        if sub in P:
            parent = min(names, key=lambda n: np.linalg.norm(P[n] - P[sub]))
            v = P[sub] - P[parent]
            m[hand].update(sub_parent=parent, sub_dist=float(np.linalg.norm(v)), sub_along_finger=float(v[1] * ext),
                           sub_along_body=float(v[0]))
    m["index_stagger_y"] = float(P["R_index"][1] - P["L_index"][1])      # + = R index nearer the player
    m["index_dx"] = float(P["R_index"][0] - P["L_index"][0])
    m["pinky_span_x"] = float(P["R_pinky"][0] - P["L_pinky"][0])
    m["centre_gap"] = float(np.linalg.norm(P["R_index"] - P["L_index"]))
    return m


def addon_layout(body):
    """Planform (x, y toward the player) of the add-on's built holes, x from the outer left end (mm)."""
    d = json.load(open(ROOT / "addon_checks" / f"{body}.json"))
    m = d["measurements"]
    pre = presets.get_preset(body.split("-")[0])
    cav = cavity_math.Cavity.from_preset(pre, scale=m["cavity"]["scale"])
    xs = [cav.point(th, ph)[0] for th in np.linspace(0, math.pi, 181) for ph in np.linspace(0, 2 * math.pi, 73)]
    wall = 4.0
    xmin, xmax = min(xs) - wall, max(xs) + wall
    names = {"sub1": "sub_L", "sub2": "sub_R"}
    out, tilt = {}, {}
    for h in m["holes"]:
        n = names.get(h["name"], h["name"])
        c = h["centre"]
        out[n] = (c[0] - xmin, -c[1], h["d_measured_mm"])
        tilt[n] = h.get("tilt_deg", float("nan"))
    return out, tilt, xmax - xmin


def fmt(v, nd=1):
    return "–" if v is None or v != v else f"{v:.{nd}f}"


def table(rows):
    """rows: list of (label, metrics, pinky insets (bulb, tail) or None, extra dict)."""
    hdr = ("| Layout | L pitches P→R→M→I | R pitches P→R→M→I | L span | R span | L chord tilt | R chord tilt "
           "| L arch (ring, middle) | R arch (ring, middle) | Index stagger y / dx | Sub L: parent, along finger, dist | "
           "Sub R: parent, along finger, dist | Pinky inset bulb / tail |")
    lines = [hdr, "|" + "---|" * (hdr.count("|") - 1)]
    for label, mt, ins in rows:
        l, r = mt["left"], mt["right"]
        lines.append(
            f"| {label} | {' / '.join(fmt(p) for p in l['pitches'])} | {' / '.join(fmt(p) for p in r['pitches'][::1])} "
            f"| {fmt(l['span'])} | {fmt(r['span'])} | {fmt(l['tilt_deg'])}° | {fmt(r['tilt_deg'])}° "
            f"| {fmt(l['sag_ring'])}, {fmt(l['sag_middle'])} | {fmt(r['sag_ring'])}, {fmt(r['sag_middle'])} "
            f"| {fmt(mt['index_stagger_y'])} / {fmt(mt['index_dx'])} "
            f"| {l.get('sub_parent', '–')}, {fmt(l.get('sub_along_finger'))}, {fmt(l.get('sub_dist'))} "
            f"| {r.get('sub_parent', '–')}, {fmt(r.get('sub_along_finger'))}, {fmt(r.get('sub_dist'))} "
            f"| {fmt(ins[0]) if ins else '–'} / {fmt(ins[1]) if ins else '–'} |")
    return "\n".join(lines)


def annotate(key, pts, out_name):
    im = Image.open(HERE / "images" / FILES[key]).convert("RGB")
    dr = ImageDraw.Draw(im)
    for n, (cx, cy, d) in pts.items():
        r = (d / 2 if d == d else 6) + 3
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(220, 0, 0), width=2)
        dr.text((cx + r + 2, cy - 6), n, fill=(255, 255, 255))
    dr.text((8, im.height - 16), "Hole names by hand arch (standard 12-hole order). Mouthpiece side = player side.",
            fill=(255, 255, 255))
    im.save(HERE / "images" / out_name)


def main():
    rows, notes = [], []
    # Miracle (mm)
    mir = {n: (x, -(-y)) for n, (x, y) in MIRACLE.items()}         # y already grows toward the player
    rows.append(("Miracle AO10-AC (mm, measured)", metrics(mir), (MIRACLE["L_pinky"][0], MIRACLE_LENGTH_MM - MIRACLE["R_pinky"][0])))

    # photos, scaled to the Miracle pinky span
    photo_px = {}
    for key, label in (("04", "Photo 04, yellow (orthographic)"), ("03", "Photo 03, blue (mild perspective)"),
                       ("02", "Photo 02, blue (perspective, blurred)")):
        pts, lay = photo_layout(key)
        photo_px[key] = (pts, lay)
        span = lay["R_pinky"][0] - lay["L_pinky"][0]
        f = MIRACLE_SPAN_MM / span
        lay_mm = {n: (x * f, y * f) for n, (x, y, d) in lay.items()}
        ins = None
        if key == "04":
            lum = lum_of(HERE / "images" / FILES[key])
            body = lum > 80
            ys, xs = np.nonzero(body)
            x_bulb, x_tail = xs.max(), xs.min()                          # image x of the bulb end and the tail tip
            L_px = x_bulb - x_tail
            ins = ((x_bulb - pts["L_pinky"][0]) * f, (pts["R_pinky"][0] - x_tail) * f)
            notes.append(f"Photo 04: body length {L_px} px, pinky-to-pinky span {span:.0f} px = {span / L_px:.3f} of the body "
                         f"length (Miracle {MIRACLE_SPAN_MM / MIRACLE_LENGTH_MM:.3f}). Scaled to the Miracle span the body would be "
                         f"{L_px * f:.0f} mm long.")
            # local body width and hole band at each hole (orthographic photo only)
            for n in ("L_pinky", "L_index", "R_index", "R_pinky"):
                cx, cy, _ = pts[n]
                col = np.nonzero(body[:, int(round(cx))])[0]
                notes.append(f"  {n}: far edge to centre {(col.max() - cy) * f:.1f} mm, local body width "
                             f"{(col.max() - col.min()) * f:.1f} mm (scaled)")
        rows.append((label + ", scaled to the Miracle span", metrics(lay_mm), ins))
    annotate("04", photo_px["04"][0], "10_annotated_yellow.png")

    # add-on bodies (mm, built)
    tilt_lines = []
    for body in ("P1-80", "P2-80", "P3-80", "P0-80"):
        lay, tilt, Lout = addon_layout(body)
        ins = (lay["L_pinky"][0], Lout - lay["R_pinky"][0])
        rows.append((f"Add-on {body} (mm, built)", metrics(lay), ins))
        tilt_lines.append(f"| {body} | {Lout:.0f} mm | " + " | ".join(fmt(tilt[n], 0) + "°" for n in LEFT + RIGHT) + " |")

    md = ["# Hole-layout comparison (generated by measure_reference.py)", "",
          "Frame: player view of the top face. x from the bulb (left-hand) end toward the tail, y toward the player. "
          "All lengths in mm. Photo layouts are scaled so that their pinky-to-pinky span along x equals the Miracle's "
          f"{MIRACLE_SPAN_MM:.1f} mm; their absolute size is unknown.", "",
          "- **Pitches**: centre-to-centre distance between neighbouring finger holes of one hand, pinky → ring → middle → index.",
          "- **Chord tilt**: angle of the line pinky → index against the body axis; + means the index end is farther from the player.",
          "- **Arch**: how far the ring and middle holes stand off that line, + in the direction the fingertips point "
          "(left hand: toward the player; right hand: toward the far side). + means the holes follow the fingertip arch.",
          "- **Index stagger**: y(R index) − y(L index) (+ = R index nearer the player) and x(R index) − x(L index).",
          "- **Sub**: the finger hole nearest each subhole, the subhole's offset along that hand's fingertip direction "
          "(+ = the finger reaches it by straightening), and the centre distance.",
          "- **Pinky inset**: from the outer end of the body to the pinky hole centre, along x.", "",
          table(rows), "", "Notes:", ""] + [f"- {n}" if not n.startswith("  ") else f"  - {n.strip()}" for n in notes]
    md += ["", "Hole tilt of the add-on bodies (angle between the hole axis and the vertical of its deck):", "",
           "| Body | Outer length | " + " | ".join(LEFT + RIGHT) + " |", "|" + "---|" * 10] + tilt_lines
    text = "\n".join(md) + "\n"
    (HERE / "measure_output.md").write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)
    for key, (pts, _) in photo_px.items():
        print(key, {n: (round(cx), round(cy), round(d, 1) if d == d else None) for n, (cx, cy, d) in pts.items()})


if __name__ == "__main__":
    main()
