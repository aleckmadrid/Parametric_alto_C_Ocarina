"""Sheets of the low-voicing trials (low_voicing_trials.py). Needs Pillow.

    python Analizes_ocarinas/Low_voicing/sheet_low_voicing.py

Writes, next to this file:
    sheet_thumb_face.png          the two ceramic thumb-face photos beside the trials on the seed, seen the same way
    sheet_low_voicing_P4.png      the port angles on the seed: thumb face, along the body, the cut through the lip, ...
    sheet_foot_P4.png             the left thumb hole and the foot of the neck (32 mm against 29 mm)
    sheet_long_pipe_P4.png        a pipe of 45 mm against the rule's 30 mm
    sheet_low_voicing_P1.png      the port angles on the teardrop
"""
import json
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMG = HERE / "images"
T = {}
for _f in sorted((HERE / "trials").glob("*.json")):
    _row = json.loads(_f.read_text(encoding="utf-8"))
    T[f"{_row['preset']}:{_row['trial']}"] = _row
INK, PAD, COL = (20, 50, 120), 14, 430
RED, GREEN = (170, 30, 30), (20, 110, 40)
SWEEP = ("lv-30", "lv-20", "lv-10", "lv-0")
# On the seed P4 the sheets show the trials with the 29 mm foot: with the seed's own 32 mm the left thumb hole
# touches the foot of the neck at every port angle below 30 (the plain trials are in the table of the record).
SWEEP_P4 = ("lv-30", "lv-20f", "lv-10f", "lv-0f")


def font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


F_HEAD, F_CAP, F_SMALL = font(23), font(17), font(15)


def fit(im, width):
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def trim(im, pad=10):
    a = np.asarray(im.convert("RGB"))
    mask = (a < 250).any(axis=2)
    if not mask.any():
        return im
    ys, xs = np.where(mask.any(axis=1))[0], np.where(mask.any(axis=0))[0]
    return im.crop((max(xs[0] - pad, 0), max(ys[0] - pad, 0), min(xs[-1] + pad, im.width), min(ys[-1] + pad, im.height)))


def head(key):
    r = T[key]
    port = r["overrides"].get("port_angle_deg")
    name = r["trial"]
    if name == "lv-30":
        return "lv-30: port 30° (the rule)"
    more = []
    if r["overrides"].get("neck_foot_width_mm"):
        more.append(f"foot {r['overrides']['neck_foot_width_mm']:g}")
    if r.get("param_overrides", {}).get("voicing_rules.windway_length_mm"):
        more.append(f"pipe {r['param_overrides']['voicing_rules.windway_length_mm']:g} mm")
    return f"{name}: port {port:g}°" + (", " + ", ".join(more) if more else "")


def cell_path(key, row):
    if row.startswith("std:"):                      # a picture of the usual set, addon_renders/<body>/
        return ROOT / "addon_renders" / T[key]["body_id"] / f"{row[4:]}.png"
    return IMG / f"{key.replace(':', '_')}_{row}.png"


def thumb_line(r):
    out = []
    for name in ("L_thumb", "R_thumb"):
        t = (r.get("thumbs") or {}).get(name)
        if t:
            out.append(f"{name[0]} {t['to_window_mm']:.1f}")
    return "Thumb hole edge to the window: " + " / ".join(out) + " mm"


def free_depth(r) -> str:
    msg = r["checks"]["voicing_keepouts"]["message"]
    key = "free depth below the window "
    return msg.split(key)[1].split(" mm")[0] if key in msg else "?"


def caption(key):
    r = T[key]
    if r.get("build_failed"):
        text = r["build_failed"]
        return [("BUILD STOPPED:", RED)] + [(text[i:i + 50], RED) for i in range(0, min(len(text), 200), 50)]
    g = r["geometry"]
    lines = [(f"Window {g['window_in_from_player_edge_mm']:.1f} mm inside the player-side edge", None),
             (f"   ({100 * g['window_in_share_of_width']:.0f} % of the width), facing {abs(g['window_faces_from_down_deg']):.0f}° from straight down", None),
             (f"Mouthpiece {abs(g['pipe_above_level_deg']):.0f}° {'above' if g['pipe_above_level_deg'] >= 0 else 'below'} the level of the body", None),
             (f"Mouth end {g['mouth_end_beyond_player_edge_mm']:.1f} mm beyond the body's edge,", None),
             (f"   {abs(g['mouth_end_below_mid_plane_mm']):.1f} mm {'below' if g['mouth_end_below_mid_plane_mm'] >= 0 else 'above'} the middle of the body", None),
             (thumb_line(r), None),
             (f"Pipe {r['windway_length_mm']:g} mm; free air below the window {free_depth(r)} mm", None)]
    if r["unexpected"]:
        lines.append(("FAILS: " + ", ".join(r["unexpected"]), RED))
    else:
        lines.append(("Checks: no unexpected failure", GREEN))
    return lines


def sheet(out_name, title, lines, keys, rows, refs=None, ref_heads=()):
    """refs: optional {row: [(image path, label), ...]} put in extra columns on the left."""
    keys = [k for k in keys if k in T]
    cells = {}
    for key in keys:
        for row, _ in rows:
            p = cell_path(key, row)
            if p.exists():
                im = Image.open(p).convert("RGB")
                cells[(key, row)] = fit(im if row.endswith("section") else trim(im), COL)
    ref_cols = max((len(v) for v in (refs or {}).values()), default=0)
    ref_cells = {}
    for row, items in (refs or {}).items():
        for i, (path, label) in enumerate(items):
            ref_cells[(i, row)] = (fit(Image.open(path).convert("RGB"), COL), label)
    row_h = [max([cells[(k, row)].height for k in keys if (k, row) in cells]
                 + [ref_cells[(i, row)][0].height + 20 for i in range(ref_cols) if (i, row) in ref_cells], default=0) for row, _ in rows]
    top = 50 + 26 * len(lines) + 10
    cap_h = 36 + max(len(caption(k)) for k in keys) * 22 + 10
    W = PAD + (ref_cols + len(keys)) * (COL + PAD)
    H = top + cap_h + sum(h + 28 + PAD for h in row_h) + PAD
    out = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(out)
    d.text((PAD, 10), title, fill=(0, 0, 0), font=F_HEAD)
    for i, line in enumerate(lines):
        d.text((PAD, 46 + 26 * i), line, fill=(40, 40, 40), font=F_CAP)
    y = top + cap_h
    for (row, label), h in zip(rows, row_h):
        d.text((PAD, y), label, fill=(110, 110, 110), font=F_CAP)
        for i in range(ref_cols):
            if (i, row) in ref_cells:
                im, lab = ref_cells[(i, row)]
                out.paste(im, (PAD + i * (COL + PAD), y + 26))
                d.text((PAD + i * (COL + PAD) + 4, y + 26 + im.height + 2), lab, fill=(110, 110, 110), font=F_SMALL)
        y += h + 28 + PAD
    for i in range(ref_cols):
        d.text((PAD + i * (COL + PAD), top), ref_heads[i] if i < len(ref_heads) else "", fill=INK, font=F_HEAD)
    for c, key in enumerate(keys):
        x = PAD + (ref_cols + c) * (COL + PAD)
        d.text((x, top), head(key), fill=INK, font=F_HEAD)
        for i, (line, colour) in enumerate(caption(key)):
            d.text((x, top + 32 + i * 22), line, fill=colour or (40, 40, 40), font=F_CAP)
        y = top + cap_h
        for (row, _), h in zip(rows, row_h):
            if (key, row) in cells:
                out.paste(cells[(key, row)], (x, y + 26))
            y += h + 28 + PAD
    out.save(HERE / out_name)
    print(out_name, out.size)


ROWS = (("thumbface", "Straight at the thumb face (the player is at the top of the picture)"),
        ("back34", "The thumb face as the two ceramic photos show it: from below, the tail toward the camera"),
        ("end", "Along the body: the player is on the left, the deck is up"),
        ("bodysection", "The same view, cut through the lip (red cross); the air is blue; grid 10 mm"),
        ("std:top", "The finger deck from above (the player is at the bottom of the picture)"),
        ("under", "From below, from the player's side"),
        ("player", "From the player"),
        ("std:voicing", "The window seen straight in (the jet runs left to right)"),
        ("section", "Close section through the window: the jet runs left to right, outside is up"))
SHORT_ROWS = (("end", "Along the body: the player is on the left, the deck is up"),
              ("bodysection", "The same view, cut through the lip (red cross); the air is blue; grid 10 mm"),
              ("std:top", "The finger deck from above (the player is at the bottom of the picture)"),
              ("thumbface", "Straight at the thumb face (the player is at the top of the picture)"),
              ("player", "From the player"))
RULE = "Everything else is the rule of version 3: cone neck, pipe +8° into the chamber, roof cut square, pipe 30 mm long."
FIT = "Every picture is fitted to its column: the pictures of one row are not at one scale."


def have(pid, names):
    return [f"{pid}:{n}" for n in names if f"{pid}:{n}" in T]


def main():
    spencer = ROOT / "Analizes_ocarinas" / "Spencer_OoT_12h" / "images" / "04_back_face_oblique.png"
    songbird = ROOT / "Analizes_ocarinas" / "Songbird_OoT_12h" / "images" / "altoC_05_video_thumb_face.png"
    keys = have("P4", SWEEP_P4)
    if keys:
        sheet("sheet_thumb_face.png", "The thumb face: the two ceramic instruments and the trials on the seed P4-80",
              ["The Spencer and the Songbird Alto C carry the window on the thumb face, inside the outline, and the mouthpiece leaves the edge of the body.",
               "The trials are seen the same way. The photos are oblique and not to scale with the renders."],
              keys, (("back34", "From below, the tail toward the camera"), ("thumbface", "Straight at the thumb face (the player is at the top)")),
              refs={"back34": [(spencer, "Spencer_OoT_12h/images/04_back_face_oblique.png"), (songbird, "Songbird_OoT_12h/images/altoC_05_video_thumb_face.png")]},
              ref_heads=("Spencer (photo)", "Songbird Alto C (photo)"))
        sheet("sheet_low_voicing_P4.png", "The voicing lower on the thumb face: P4-80 (the seed, which has the outline of the Songbird)",
              ["Left to right: the port angle, from the rule (30° around the body from the bottom toward the player) down to 0° (the bottom line of the thumb face).",
               RULE + " Below 30° the foot of the neck is 29 mm wide (32 mm on the rule body).", FIT], keys, ROWS)
    keys = have("P4", ("lv-20", "lv-20f", "lv-10", "lv-10f", "lv-0", "lv-0f"))
    if keys:
        sheet("sheet_foot_P4.png", "The left thumb hole and the foot of the neck: P4-80",
              ["With the seed's own foot (32 mm) the left thumb hole touches the foot of the neck at every port angle below 30°.",
               "With 29 mm, the proportion of the two ceramic necks (0.21 of the body length), it is clear."],
              keys, (("thumbface", "Straight at the thumb face (the player is at the top of the picture)"), ("under", "From below, from the player's side")))
    keys = have("P4", ("lv-20f", "lv-20fw", "lv-10f", "lv-10fw"))
    if keys:
        sheet("sheet_long_pipe_P4.png", "A longer pipe on the low voicing: P4-80, 30 mm against 45 mm",
              ["A window that lies further inside the outline leaves less mouthpiece outside it. The Songbird's mouthpiece stands 0.28 of the body length beyond the edge (39 mm at this size).",
               "A pipe of another length is another voicing (its own hash and its own stub). The owner parked the longer pipe for later; it is shown because this approach leans on it.", FIT],
              keys, SHORT_ROWS)
    keys = have("P1", SWEEP_P4)
    if keys:
        sheet("sheet_low_voicing_P1.png", "The voicing lower on the thumb face: P1-80 (the teardrop)",
              ["Left to right: the port angle, from the rule (30°) down to 0°. " + RULE,
               "Below 30° the foot of the neck is 34 mm wide (42 mm on the rule body). " + FIT], keys, ROWS)


if __name__ == "__main__":
    main()
