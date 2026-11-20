"""Sheet of the Stage 1 stubs V-a (30 mm pipe) and V-aw (45 mm pipe), from stub_long_pipe.py. Needs Pillow.

    python Analizes_ocarinas/Low_voicing/sheet_stub_long_pipe.py

Writes sheet_stub_long_pipe.png next to this file.
"""
import json
import pathlib

from PIL import Image, ImageDraw

import sheet_low_voicing as slv

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = json.loads((HERE / "stubs" / "stubs.json").read_text(encoding="utf-8"))
COLS = (("V-a", HERE / "stubs" / "renders" / "V-a"), ("V-aw", ROOT / "addon_renders" / "V-aw"))
ROWS = (("iso", "From above and aside"), ("front", "From the front"), ("end", "Along the stub"),
        ("section_windway", "Section along the windway"),
        ("voicing", "The window seen straight in. Cropped 34 mm from the window: V-aw's neck is cut 15 mm short and its pipe walls show (not plastic)"))
COL, PAD = 620, 16


def caption(sid):
    r = DATA[sid]
    n = r["neck"]
    return [f"{sid}: pipe {r['pipe_mm']:g} mm, voicing {r['voicing_hash']}",
            f"Neck {n.get('length_mm', 0):.1f} mm long; plastic {r['plastic_cm3']:.1f} cm³ ({1.24 * r['plastic_cm3']:.0f} g solid PLA)",
            f"Capped air {r['capped_air_cm3']:.3f} cm³; predicted {r['predicted_pitch_hz']:.1f} Hz (prior η_w {r['eta_w_prior']:g})",
            f"Steepest plastic seen from the window rim {r['flare_steepest_deg']:.1f}° ({r['above_outer_face_mm']:.1f} mm high)",
            "Checks: no unexpected failure" if not r["unexpected"] else "FAILS: " + ", ".join(r["unexpected"])]


def main():
    cells = {}
    for sid, folder in COLS:
        for row, _ in ROWS:
            p = folder / f"{row}.png"
            if p.exists():
                im = Image.open(p).convert("RGB")
                cells[(sid, row)] = slv.fit(im if row.startswith("section") else slv.trim(im), COL)
    heights = [max(cells[(s, r)].height for s, _ in COLS if (s, r) in cells) for r, _ in ROWS]
    top = 70
    cap_h = 5 * 22 + 40
    W = PAD + len(COLS) * (COL + PAD)
    H = top + cap_h + sum(h + 30 + PAD for h in heights)
    out = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(out)
    d.text((PAD, 10), "Stage 1 stub for the 45 mm pipe: V-a against V-aw (preset S0, 25 cm³, the 80 cm³ window)", fill=(0, 0, 0), font=slv.F_HEAD)
    d.text((PAD, 42), "Every picture is fitted to its column; the two columns of one row are at one scale only when the stubs are the same size.",
           fill=(60, 60, 60), font=slv.F_SMALL)
    for c, (sid, _) in enumerate(COLS):
        x = PAD + c * (COL + PAD)
        for i, line in enumerate(caption(sid)):
            d.text((x, top + i * 22), line, fill=slv.INK if i == 0 else (40, 40, 40), font=slv.F_CAP)
    y = top + cap_h
    for (row, label), h in zip(ROWS, heights):
        d.text((PAD, y), label, fill=(110, 110, 110), font=slv.F_CAP)
        for c, (sid, _) in enumerate(COLS):
            if (sid, row) in cells:
                out.paste(cells[(sid, row)], (PAD + c * (COL + PAD), y + 26))
        y += h + 30 + PAD
    out.save(HERE / "sheet_stub_long_pipe.png")
    print("sheet_stub_long_pipe.png", out.size)


if __name__ == "__main__":
    main()
