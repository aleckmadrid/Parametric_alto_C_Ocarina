"""Sheets of the inner-wall trials of series 3 (stage W, first pass). Needs Pillow.

    python Analizes_ocarinas/Low_voicing/sheet_series3_walls.py

Writes sheet_s3_walls_P4.png and sheet_s3_walls_P1.png next to this file: one column per trial, the owner's Spencer
half-shell picture in the first column. Reads series3_trials.json and walls_desk_model.json.
"""
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE / "images_s3"
T = json.loads((HERE / "series3_trials.json").read_text(encoding="utf-8"))
DESK = json.loads((HERE / "walls_desk_model.json").read_text(encoding="utf-8")) if (HERE / "walls_desk_model.json").exists() else {}
CW, PAD = 520, 14
ROWS = (("inside", "The thumb-face half seen from the chamber (the body opened at its middle; the player at the top)", 330),
        ("alongthumbs", "Cut along the body through the thumb holes: the deck is up, air is blue, grid 10 mm", 290),
        ("alongwindow", "Cut along the body through the window", 290),
        ("thumbface", "Outside, straight at the thumb face", 250))
ORDER = ("s3-fwr", "s3-w25", "s3-w38", "s3-w50", "s3-wL", "s3-wR", "s3-wf", "s3-wt16", "s3-wt40", "s3-fwr30", "s3-w30")


def font(size, bold=False):
    for name in (("arialbd.ttf",) if bold else ()) + ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def fit(path, w, h):
    im = Image.open(path).convert("RGB")
    k = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def lines(key):
    r = T[key]
    w = r.get("inner_walls") or {}
    cm = r.get("cavity_mode") or {}
    d = DESK.get(f"{key}@1") or {}
    out = [r["what"]]
    for name, x in (w.get("walls") or {}).items():
        hole = min(h["rim_to_wall_mm"] for h in x["thumb_holes"].values())
        out.append(f"{name}: x {x['x_mm']:+.1f} mm, {x['thickness_mm']:g} mm thick, top {x['top_above_thumb_wall_mm']:.1f} mm up "
                   f"({100 * x['blocked_share']:.0f} % blocked)")
        out.append(f"   to its thumb hole {hole:.1f} mm, to the window {x['window_to_wall_mm']:.1f} mm, takes {x['air_taken_cm3']:.2f} cm³")
    if w:
        out.append(f"Chamber grown by {w['chamber_grown_cm3']:.2f} cm³; plastic {r['plastic_cm3']:.1f} cm³")
    else:
        out.append(f"No wall; plastic {r['plastic_cm3']:.1f} cm³")
    out.append(f"First cavity mode {cm.get('ratio', float('nan')):.2f} × F6 on the add-on's 1.5 mm grid"
               + (f", {d['closed_ratio']:.2f} on 1.0 mm" if d else ""))
    if "conductance_left_L" in d:
        out.append(f"Thumb holes' effect left (model): L {100 * d['conductance_left_L']:.0f} %, R {100 * d['conductance_left_R']:.0f} %, "
                   f"both {100 * d['conductance_left_LR']:.0f} %")
    bad = r.get("unexpected") or []
    out.append("Checks: no unexpected failure" if not bad else "Checks FAIL: " + ", ".join(bad))
    return out, not bad


def sheet(pid):
    keys = [f"{pid}:{t}" for t in ORDER if f"{pid}:{t}" in T and "build_failed" not in T[f"{pid}:{t}"]]
    if not keys:
        return
    f_h, f_t, f_s = font(20, True), font(15, True), font(13)
    head_h = 178
    W = PAD + (len(keys) + 1) * (CW + PAD)
    H = 70 + head_h + sum(h + 26 for _, _, h in ROWS) + PAD
    im = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(im)
    dr.text((PAD, 10), f"Series 3, stage W: inner walls between the window and the thumb holes ({pid}-80, port 10°, pipe 45 mm, round tip)", font=f_h, fill="black")
    dr.text((PAD, 38), "A wall is cut out of the air before the air is cut out of the shell; the chamber is grown until the walled air is 80 cm³ again. "
            "The voicing hash is 40688a48d1c7 in every column (port 30° in the last one). Nothing was printed.", font=f_s, fill=(70, 70, 70))
    x0 = PAD
    dr.text((x0, 70), "Spencer (owner's photo): the thumb-face half", font=f_t, fill=(20, 40, 110))
    ref = fit(HERE / "reference_photos" / "spencer_04_half_shell_inside.png", CW, ROWS[0][2] + ROWS[1][2] + 20)
    im.paste(ref, (x0, 70 + head_h))
    for c, key in enumerate(keys):
        x = PAD + (c + 1) * (CW + PAD)
        dr.text((x, 70), key.split(":")[1], font=f_t, fill=(20, 40, 110))
        ls, ok = lines(key)
        for i, s in enumerate(ls):
            dr.text((x, 92 + i * 15), s[:92], font=f_s, fill=(0, 110, 40) if (i == len(ls) - 1 and ok) else ((190, 0, 0) if i == len(ls) - 1 else "black"))
    y = 70 + head_h
    for name, title, h in ROWS:
        dr.text((PAD + CW + PAD, y), title, font=f_s, fill=(90, 90, 90))
        for c, key in enumerate(keys):
            p = IMG / f"{key.replace(':', '_')}_{name}.png"
            if p.exists():
                pic = fit(p, CW, h)
                im.paste(pic, (PAD + (c + 1) * (CW + PAD), y + 20))
        y += h + 26
    out = HERE / f"sheet_s3_walls_{pid}.png"
    im.save(out)
    print(out.name, im.size)


if __name__ == "__main__":
    for pid in ("P4", "P1"):
        sheet(pid)
