"""Sheet for section 12 of Window_cutout.md: the validated ellipse-loft bodies, outside and in section.

    python Analizes_ocarinas/Window_cutout/sheet_ellipse.py

Reads images/outside_<body>_front.png, images/outside_<body>_oblique.png (render_windows.py) and
images/sections_<body>.png (measure_windows.py); writes images/sheet_ellipse_chosen.png and
images/sheet_ellipse_wide_window.png. Needs Pillow.
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE / "images"
ROWS = [("P4-80-ellipse-p3", "P3: opening +3 mm per side (0.34 x window width), shelf 40°"),
        ("P4-80-ellipse-p1", "P1: opening +4 mm per side (0.45 x window width), shelf 50°"),
        ("P4-80-el-p1-m25", "P1 with the windway lowered 2.5° inside the neck")]
T = 520


def font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def fit(im, h=T):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def main():
    rows = []
    for name, label in ROWS:
        front = fit(Image.open(IMG / f"outside_{name}_front.png").convert("RGB"))
        oblique = fit(Image.open(IMG / f"outside_{name}_oblique.png").convert("RGB"))
        sec = Image.open(IMG / f"sections_{name}.png").convert("RGB")
        sec = fit(sec.crop((0, 0, sec.width // 3, sec.height)))                # the long section is the first of three panels
        rows.append((label, [front, oblique, sec]))
    width = max(sum(i.width for i in ims) + 10 * (len(ims) + 1) for _, ims in rows)
    sheet = Image.new("RGB", (width, len(rows) * (T + 46) + 10), "white")
    d = ImageDraw.Draw(sheet)
    y = 6
    for label, ims in rows:
        d.text((10, y + 6), label, fill=(20, 60, 140), font=font(24))
        y += 40
        x = 10
        for im in ims:
            sheet.paste(im, (x, y))
            x += im.width + 10
        y += T + 6
    sheet.save(IMG / "sheet_ellipse_chosen.png")
    print("written", sheet.size)

    # the widest window of the ladder, with the opening in millimetres and as a share of the window width
    wide = [("P0-125-el-mm4", "125 cm³ (window 18.6 x 9.65 mm): opening +4 mm per side, as P1 in mm"),
            ("P0-125-el-p1", "125 cm³: opening 0.45 x window width = +8.4 mm per side")]
    sheet = Image.new("RGB", (2 * T + 30, len(wide) * (T + 46) + 10), "white")
    d = ImageDraw.Draw(sheet)
    y = 6
    for name, label in wide:
        d.text((10, y + 6), label, fill=(20, 60, 140), font=font(24))
        y += 40
        for k, view in enumerate(("front", "oblique")):
            sheet.paste(Image.open(IMG / f"outside_{name}_{view}.png").convert("RGB").resize((T, T), Image.LANCZOS), (10 + k * (T + 10), y))
        y += T + 6
    sheet.save(IMG / "sheet_ellipse_wide_window.png")
    print("written", sheet.size)


if __name__ == "__main__":
    main()
