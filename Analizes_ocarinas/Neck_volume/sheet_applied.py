"""The stage bodies as rule version 3 builds them (2026-11-19). Needs Pillow.

    python Analizes_ocarinas/Neck_volume/sheet_applied.py

Reads the standard pictures of the Stage 2 bodies (addon_renders/<id>/, written by `headless.py -- stage2`) and their
reports (addon_checks/<id>.json). Writes sheet_rule3_applied.png beside this file.
"""
import json
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BODIES = (("P0-80", "P0-80: the control egg"), ("P1-80", "P1-80: the teardrop"), ("P2-80", "P2-80: the tailed gourd"), ("P4-80", "P4-80: the seed"))
ROWS = (("end", "Seen along the body from the right-hand end: the player is on the left, the deck is up"), ("iso_bottom", "From the player's left, below"),
        ("voicing", "The window, straight in"), ("section_windway", "Section through the pipe: the jet runs left to right, outside is up"))
COL, PAD = 520, 14


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


def main():
    f_head, f_cap = font(23), font(17)
    cells, caps = {}, {}
    for bid, _ in BODIES:
        d = json.loads((ROOT / "addon_checks" / f"{bid}.json").read_text(encoding="utf-8"))
        m = d["measurements"]
        g, n = m["voicing"], m["voicing"]["neck"]
        bad = [c["name"] for c in d["checks"] if c["status"] == "fail" and not c.get("expected")]
        hv = m["hole_to_voicing"]
        near = min(hv.items(), key=lambda kv: kv[1]["to_window_mm"])
        caps[bid] = [f"Roof over the exit {n['over_pipe_roof_at_exit_mm']:.1f} mm, cut square; {n['over_pipe_roof_at_mouth_mm']:.1f} mm at the mouth end",
                     f"Neck: mouth end {n['mouth_width_mm']:.1f} × {n['mouth_depth_mm']:.1f} mm, {n['base_width_mm']:.1f} × {n['base_depth_mm']:.1f} mm at the body",
                     f"Behind the window the neck rises {g['flare_steepest_deg']:.0f}° (keep-out limit {g['flare_limit_deg']:.0f}°)",
                     f"Window {g['window_area_mm2']:.2f} mm², lip {g['labium_edge_thickness_mm']:.2f} mm, ramp {g['labium_angle_deg']:.1f}°",
                     f"Nearest hole to the window: {near[0]}, {near[1]['to_window_mm']:.1f} mm",
                     f"Neck plastic beside any hole's rim: {max(v.get('plastic_on_skin_at_rim_mm', 0.0) for v in hv.values()):.2f} mm",
                     f"Plastic {m['volume']['body_plastic_cm3']:.1f} cm³; capped air {m['volume']['capped_air_measured_cm3']:.2f} cm³",
                     "Checks: no unexpected failure" if not bad else "FAILS: " + ", ".join(bad)]
        for row, _ in ROWS:
            p = ROOT / "addon_renders" / bid / f"{row}.png"
            if p.exists():
                im = Image.open(p).convert("RGB")
                im = im if row.startswith("section") else trim(im)
                cells[(bid, row)] = im.resize((COL, round(im.height * COL / im.width)), Image.LANCZOS)
    row_h = [max((cells[(b, row)].height for b, _ in BODIES if (b, row) in cells), default=0) for row, _ in ROWS]
    top, cap_h = 84, 34 + 8 * 22 + 10
    W = PAD + len(BODIES) * (COL + PAD)
    H = top + cap_h + sum(h + 28 + PAD for h in row_h) + PAD
    out = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(out)
    d.text((PAD, 10), "Rule version 3 (2026-11-19) on the Stage 2 bodies: the cone neck, the roof cut square, the pipe at +8°, the voicing 30° around the body", fill=(0, 0, 0), font=f_head)
    d.text((PAD, 44), "All four are 80 cm³ and share one voicing. P0 carries the taped test layout, not a hand layout.", fill=(40, 40, 40), font=f_cap)
    for c, (bid, head) in enumerate(BODIES):
        x = PAD + c * (COL + PAD)
        d.text((x, top), head, fill=(20, 50, 120), font=f_head)
        for i, line in enumerate(caps[bid]):
            d.text((x, top + 32 + i * 22), line, fill=(40, 40, 40), font=f_cap)
        y = top + cap_h
        for (row, label), h in zip(ROWS, row_h):
            if c == 0:
                d.text((PAD, y), label, fill=(110, 110, 110), font=f_cap)
            if (bid, row) in cells:
                out.paste(cells[(bid, row)], (x, y + 26))
            y += h + 28 + PAD
    out.save(HERE / "sheet_rule3_applied.png")
    print("sheet_rule3_applied.png", out.size)


if __name__ == "__main__":
    main()
