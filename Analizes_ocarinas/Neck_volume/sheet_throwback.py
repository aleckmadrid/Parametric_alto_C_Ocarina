"""Sheets of the second round of neck trials (throwback_trials.py). Needs Pillow.

    python Analizes_ocarinas/Neck_volume/sheet_throwback.py

Writes sheet_throwback_P1.png and sheet_throwback_P4.png (five voicings each), and sheet_top_cut.png (the top of the
window cut, close: the rules, the square roof, and the two thrown-back necks, on P1).
"""
import json
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE / "images"
T = json.loads((HERE / "throwback_trials.json").read_text(encoding="utf-8"))
INK, PAD, COL = (20, 50, 120), 14, 430
HEADS = {"now": "The rules today", "nk-a": "nk-a: neck follows the pipe", "sq": "sq: nk-a, roof cut square",
         "tb-f": "tb-f: thrown back, neck follows", "tb-l": "tb-l: thrown back, neck level"}


def font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


F_HEAD, F_CAP = font(23), font(17)


def fit(im, width):
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def trim(im, pad=10):
    a = np.asarray(im.convert("RGB"))
    mask = (a < 250).any(axis=2)
    if not mask.any():
        return im
    ys, xs = np.where(mask.any(axis=1))[0], np.where(mask.any(axis=0))[0]
    return im.crop((max(xs[0] - pad, 0), max(ys[0] - pad, 0), min(xs[-1] + pad, im.width), min(ys[-1] + pad, im.height)))


def caption(key):
    r = T[key]
    if r.get("build_failed"):
        return ["BUILD FAILED:", r["build_failed"][:48]]
    n = r["neck"]
    over_exit = n.get("over_pipe_roof_at_exit_mm")
    return [f"Port {r['overrides'].get('port_angle_deg', 45):g}° around the body; pipe {r['window_faces_from_down_deg'] - r['pipe_above_level_deg']:+.0f}° into the chamber",
            f"Window faces {r['pipe_above_level_deg']:.0f}° from straight down",
            f"Pipe {r['pipe_above_level_deg']:.0f}° above level; neck flank {abs(round(r['neck_top_above_level_deg'])):.0f}°",
            f"Roof over the exit {over_exit:.1f} mm, " + ("cut square" if not r["shelf_angle_deg"] else f"shelf {r['shelf_angle_deg']:.0f}°"),
            f"Above the window's outer face: {r['above_outer_face_mm']:.1f} mm" + (f", {r['flare_steepest_deg']:.0f}° steep" if r["flare_steepest_deg"] < 89 else ", none at the rim"),
            f"The window cut removes {r['window_cut_removes_mm3']:.0f} mm³",
            f"Mouth end {n['mouth_width_mm']:.1f} × {n['mouth_depth_mm']:.1f} mm",
            f"Nearest hole to the window: {r['hole_to_voicing'].split(',')[1].strip().split(' (')[0]}",
            ("Checks: no unexpected failure" if not r["unexpected"] else "FAILS: " + ", ".join(r["unexpected"]))]


def sheet(out_name, title, lines, keys, rows):
    cells = {}
    for key in keys:
        tag = key.replace(":", "_")
        for row, _ in rows:
            p = IMG / f"{tag}_{row}.png"
            if p.exists():
                im = Image.open(p).convert("RGB")
                cells[(key, row)] = fit(im if row.endswith("section") else trim(im), COL)
    row_h = [max((cells[(k, row)].height for k in keys if (k, row) in cells), default=0) for row, _ in rows]
    top = 50 + 26 * len(lines) + 10
    cap_h = 36 + max(len(caption(k)) for k in keys) * 22 + 10
    W = PAD + len(keys) * (COL + PAD)
    H = top + cap_h + sum(h + 28 + PAD for h in row_h) + PAD
    out = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(out)
    d.text((PAD, 10), title, fill=(0, 0, 0), font=F_HEAD)
    for i, line in enumerate(lines):
        d.text((PAD, 46 + 26 * i), line, fill=(40, 40, 40), font=F_CAP)
    for c, key in enumerate(keys):
        x = PAD + c * (COL + PAD)
        d.text((x, top), HEADS[key.split(":")[1]], fill=INK, font=F_HEAD)
        for i, line in enumerate(caption(key)):
            d.text((x, top + 32 + i * 22), line, fill=(40, 40, 40), font=F_CAP)
        y = top + cap_h
        for (row, label), h in zip(rows, row_h):
            if c == 0:
                d.text((PAD, y), label, fill=(110, 110, 110), font=F_CAP)
            if (key, row) in cells:
                out.paste(cells[(key, row)], (x, y + 26))
            y += h + 28 + PAD
    out.save(HERE / out_name)
    print(out_name, out.size)


ROWS = (("end", "Along the body: the player is on the left, the deck is up"), ("bodysection", "The same view, cut through the lip (red cross)"),
        ("under", "From below and behind"), ("window", "The window, from beyond the labium"), ("outside", "From the mouth end"),
        ("section", "Close section through the window: the jet runs left to right, outside is up"))


def main():
    for pid, shape in (("P1", "the teardrop, the preset nearest to the two bulb references"), ("P4", "the seed")):
        sheet(f"sheet_throwback_{pid}.png", f"Neck and window cut on {pid}-80 ({shape})",
              ["Left to right: the rules; the first round's neck; the same with the roof over the exit cut square; then the voicing turned toward the",
               "bottom of the body (port 30° instead of 45°) with the pipe at +8°, first with a neck that follows the pipe, then with a neck that lies level."],
              [f"{pid}:{n}" for n in ("now", "nk-a", "sq", "tb-f", "tb-l")], ROWS)
    sheet("sheet_top_cut.png", "The top of the window cut, close (P1-80)",
          ["The wall over the windway exit: the rules lean it back 40° through thick plastic; the three trials cut a thin roof square, as both new models do."],
          [f"P1:{n}" for n in ("now", "sq", "tb-f", "tb-l")], (("window", "From beyond the labium"), ("section", "Section through the window")))


if __name__ == "__main__":
    main()
