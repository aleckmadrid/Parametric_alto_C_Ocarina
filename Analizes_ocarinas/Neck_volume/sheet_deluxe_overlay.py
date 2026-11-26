"""The trials of the third round laid over the section of the "Deluxe" model. Needs matplotlib and Pillow.

    python Analizes_ocarinas/Neck_volume/sheet_deluxe_overlay.py

Reads refs_position.json (the Deluxe's section, from refs_position.py) and throwback_trials.json. Every panel is the
body's cross-section through the windway in the frame of the body: the player on the left, the deck up, the lip at
the cross. The trial is drawn in black and the Deluxe in red, both placed on their lips, at the same scale. Writes
sheet_deluxe_overlay.png (sections) and sheet_deluxe_views.png (the pictures of the same trials).
"""
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE / "images"
R = json.loads((HERE / "refs_position.json").read_text(encoding="utf-8"))
T = json.loads((HERE / "throwback_trials.json").read_text(encoding="utf-8"))
PANELS = (("P1:tb-f", "tb-f (second round): the neck is a bell"), ("P1:tb-d1", "tb-d1: straight flank on the deck side"),
          ("P1:tb-d2", "tb-d2: the Deluxe's proportions"))


def draw(ax, segs, color, lw):
    for (x0, z0), (x1, z1) in segs:
        ax.plot([x0, x1], [z0, z1], "-", color=color, lw=lw, solid_capstyle="round")


def overlay():
    keys = [(k, h) for k, h in PANELS if k in T and not T[k].get("build_failed")]
    fig, axs = plt.subplots(1, len(keys), figsize=(8.6 * len(keys), 8.0))
    for ax, (key, head) in zip(np.atleast_1d(axs), keys):
        r = T[key]
        n = r["neck"]
        draw(ax, R["Deluxe"]["outline"], "#d1495b", 0.9)
        draw(ax, r["outline_body"], "#111111", 1.3)
        ax.plot([0], [0], "+", color="#2e86ab", ms=14, mew=2)
        ax.set_xlim(-48, 30)
        ax.set_ylim(-14, 46)
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3)
        ax.set_title(f"{head}\nP1-80 in black, the Deluxe in red\nmouth end {n['mouth_width_mm']:.1f} × {n['mouth_depth_mm']:.1f} mm; "
                     f"{n['base_depth_mm']:.1f} mm deep at the body\n"
                     + ("no unexpected failure" if not r["unexpected"] else "FAILS: " + ", ".join(r["unexpected"])), fontsize=12, loc="left")
    fig.suptitle("The body's cross-section through the windway: the player is on the left, the finger deck is up, the cross is the lip. Millimetres.", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(HERE / "sheet_deluxe_overlay.png", dpi=80)
    print("sheet_deluxe_overlay.png")


def font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def trim(im, pad=10):
    a = np.asarray(im.convert("RGB"))
    mask = (a < 250).any(axis=2)
    ys, xs = np.where(mask.any(axis=1))[0], np.where(mask.any(axis=0))[0]
    return im.crop((max(xs[0] - pad, 0), max(ys[0] - pad, 0), min(xs[-1] + pad, im.width), min(ys[-1] + pad, im.height)))


def views(out_name, title, keys, rows=(("end", "Along the body: the player is on the left, the deck is up"), ("under", "From below and behind"),
                                       ("window", "The window, from beyond the labium"), ("outside", "From the mouth end"),
                                       ("section", "Close section through the window"))):
    col, pad = 470, 14
    f_head, f_cap = font(22), font(17)
    cells = {}
    for key, _ in keys:
        for row, _ in rows:
            p = IMG / f"{key.replace(':', '_')}_{row}.png"
            if p.exists():
                im = Image.open(p).convert("RGB")
                im = im if row == "section" else trim(im)
                cells[(key, row)] = im.resize((col, round(im.height * col / im.width)), Image.LANCZOS)
    row_h = [max((cells[(k, row)].height for k, _ in keys if (k, row) in cells), default=0) for row, _ in rows]
    caps = {}
    for key, _ in keys:
        r = T[key]
        n = r["neck"]
        caps[key] = [f"Mouth end {n['mouth_width_mm']:.1f} × {n['mouth_depth_mm']:.1f} mm; {n['base_width_mm']:.1f} × {n['base_depth_mm']:.1f} mm at the body",
                     f"Roof over the exit {n['over_pipe_roof_at_exit_mm']:.1f} mm, cut square",
                     f"Plastic of the body {r['plastic_cm3']:.1f} cm³; thinnest {r['wall_thinnest'].split('tubes: ')[1].split(' mm')[0]} mm",
                     f"Nearest hole to the window: {r['hole_to_voicing'].split(',')[1].strip().split(' (')[0]}",
                     ("Checks: no unexpected failure" if not r["unexpected"] else "FAILS: " + ", ".join(r["unexpected"]))]
    top = 52
    cap_h = 34 + 5 * 22 + 10
    W = pad + len(keys) * (col + pad)
    H = top + cap_h + sum(h + 28 + pad for h in row_h) + pad
    out = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(out)
    d.text((pad, 12), title, fill=(0, 0, 0), font=f_head)
    for c, (key, head) in enumerate(keys):
        x = pad + c * (col + pad)
        d.text((x, top), head, fill=(20, 50, 120), font=f_head)
        for i, line in enumerate(caps[key]):
            d.text((x, top + 32 + i * 22), line, fill=(40, 40, 40), font=f_cap)
        y = top + cap_h
        for (row, label), h in zip(rows, row_h):
            if c == 0:
                d.text((pad, y), label, fill=(110, 110, 110), font=f_cap)
            if (key, row) in cells:
                out.paste(cells[(key, row)], (x, y + 26))
            y += h + 28 + pad
    out.save(HERE / out_name)
    print(out_name, out.size)


if __name__ == "__main__":
    overlay()
    views("sheet_deluxe_views.png", "tb-f with the neck adjusted toward the Deluxe (P1-80, the teardrop): pipe, window and square roof are the same in all three",
          [(k, h.split(":")[0] if ":" in h else h) for k, h in PANELS if k in T and not T[k].get("build_failed")])
    p4 = [(k, h) for k, h in (("P4:tb-f", "tb-f"), ("P4:tb-d1", "tb-d1"), ("P4:tb-d2", "tb-d2")) if k in T and not T[k].get("build_failed")]
    if p4:
        views("sheet_deluxe_views_P4.png", "The same three necks on the seed P4-80", p4,
              rows=(("end", "Along the body"), ("under", "From below and behind"), ("window", "The window, from beyond the labium")))
