"""One comparison sheet per open decision of 2026-11-18 (notes, "Fingering order switched"; docs/09 section 8).

    python Analizes_ocarinas/Decisions_2026-11-18/sheet_decisions.py            the six option sheets (before the decisions)
    python Analizes_ocarinas/Decisions_2026-11-18/sheet_decisions.py applied    the sheets of what was applied (after them)

The option bodies were built BEFORE the decisions became the rule: their commands in decisions.md name every setting,
and since 2026-11-18 a setting that is not named comes from [voicing_rules], so they no longer rebuild the same body.

All bodies are the seed body P4 at 80 cm3, in the Asian fingering order, labium offset -0.2 mm, built with
tools/geometry_check_variant.py (the commands are in decisions.md). Reads addon_renders/<id>/ (the standard
pictures of a build) and Analizes_ocarinas/Window_cutout/images/outside_<id>_*.png (render_windows.py).
Writes the sheets beside this file. Needs Pillow.
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REN = ROOT / "addon_renders"
WIN = ROOT / "Analizes_ocarinas" / "Window_cutout" / "images"
INK = (20, 50, 120)
PAD = 14


def font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


F_HEAD, F_CAP = font(26), font(20)


def ren(body, view):
    return Image.open(REN / body / f"{view}.png").convert("RGB")


def fit(im, width):
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def sheet(name, title, columns):
    """columns: list of (heading, [caption lines], [images]); images of a column are stacked."""
    widths = [max(im.width for im in ims) for _, _, ims in columns]
    heights = [sum(im.height + PAD for im in ims) for _, _, ims in columns]
    cap_h = max(len(c) for _, c, _ in columns) * 26 + 40
    W = PAD + sum(w + PAD for w in widths)
    H = 54 + cap_h + max(heights) + PAD
    out = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(out)
    d.text((PAD, 12), title, fill=(0, 0, 0), font=F_HEAD)
    x = PAD
    for (head, caps, ims), w in zip(columns, widths):
        d.text((x, 54), head, fill=INK, font=F_HEAD)
        for i, line in enumerate(caps):
            d.text((x, 54 + 34 + i * 26), line, fill=(40, 40, 40), font=F_CAP)
        y = 54 + cap_h
        for im in ims:
            out.paste(im, (x, y))
            y += im.height + PAD
        x += w + PAD
    out.save(HERE / name)
    print(name, out.size)


def main():
    # 1. the left subhole slide
    box = (60, 40, 440, 290)                       # the left hand on top.png (760 x 397)
    cols = []
    for head, body, caps in (
            ("Slide 9.5 mm (now)", "P4-80-el-d-p3-m25",
             ["Edge gap, left subhole to L ring:", "4.26 mm at the print diameters", "3.78 mm at k_hole 1.0",
              "3.02 mm with the synthetic constants (limit 3.4)"]),
            ("Slide 10.0 mm", "P4-80-el-d-p3-m25-s10",
             ["Edge gap, left subhole to L ring:", "4.76 mm at the print diameters", "4.28 mm at k_hole 1.0",
              "3.52 mm with the synthetic constants (limit 3.4)"])):
        cols.append((head, caps, [fit(ren(body, "top").crop(box), 760), fit(ren(body, "top"), 760)]))
    sheet("decision1_subhole_slide.png", "Decision 1: the left subhole slide (seed body, 80 cm³, finger face)", cols)

    # 2. the cut
    cols = []
    for head, body, caps in (
            ("Fan cut, box stub (today's default)", "P4-80-el-d-fan", ["Opens on the labium side only", "Cut removes 557 mm³ of plastic"]),
            ("Ellipse P3, neck", "P4-80-el-d-p3", ["+3 mm per side, shelf 40°. Dish 14.8 × 21.6 mm", "Cut removes 446 mm³ of plastic"]),
            ("Ellipse P1, neck", "P4-80-el-d-p1", ["+4 mm per side, shelf 50°. Dish 16.8 × 22.4 mm", "Cut removes 478 mm³ of plastic"])):
        ims = [fit(Image.open(WIN / f"outside_{body}_{v}.png").convert("RGB"), 560) for v in ("front", "oblique")]
        cols.append((head, caps, ims))
    sheet("decision2_window_cut.png", "Decision 2: the window cut (seed body, 80 cm³, seen from outside)", cols)

    # 3. the tilt
    cols = [("", ["Top: windway level. Plastic under the windway at the exit 3.21 mm.",
                  "Bottom: lowered 2.5° about the lip edge, hidden in the neck. Plastic under the windway at the exit 1.48 mm (the same at 65 and 95 cm³).",
                  "Chamber in blue, outside up, mouth end at the left, lip edge at the red cross. The outside of the neck is the same in both."],
             [fit(ren("P4-80-el-d-p3", "section_windway"), 1467), fit(ren("P4-80-el-d-p3-m25", "section_windway"), 1467)])]
    sheet("decision3_tilt.png", "Decision 3: the tilt of the windway (seed body, 80 cm³, section through the windway)", cols)

    # 4. the mouth end of the windway
    cols = [("", ["Top: the kernel's slot today, 1.56 mm high at the mouth end, 1.20 mm at the exit.",
                  "Bottom: 3.0 mm at the mouth end, 1.20 mm at the exit. Both lowered 2.5°. The window, the lip and the exit are the same.",
                  "The neck's mouth end is made deeper to keep 1.2 mm of plastic around the taller slot."],
             [fit(ren("P4-80-el-d-p3-m25", "section_windway"), 1467), fit(ren("P4-80-el-d-p3-m25-h3", "section_windway"), 1467)])]
    sheet("decision4_mouth_end.png", "Decision 4: the height of the windway at the mouth end (section through the windway)", cols)
    cols = [("1.56 mm at the mouth end (today)", [], [fit(ren("P4-80-el-d-p3-m25", "iso_bottom"), 700)]),
            ("3.0 mm at the mouth end", [], [fit(ren("P4-80-el-d-p3-m25-h3", "iso_bottom"), 700)])]
    sheet("decision4_mouth_end_outside.png", "Decision 4, outside: the neck and its mouth slot", cols)

    # 6. the stance of the neck
    cols = [("", ["Top: as built. The neck lies along the windway; the pipe is lowered 2.5° inside it; the jet leaves the labium's inner face by 2.5°.",
                  "Bottom: a neck that stands 15° off the body, the pipe lowered 10° inside it; the jet enters the chamber at 5°.",
                  "The bottom one fails the outside keep-out check (plastic above the 45° flare beside the window). A picture body only."],
             [fit(ren("P4-80-el-d-p3-m25", "section_windway"), 1467), fit(ren("P4-80-el-d-p3-stand", "section_windway"), 1467)])]
    sheet("decision6_neck_stance.png", "Decision 6: the stance of the neck (section through the windway)", cols)
    cols = [("Neck along the windway (as built)", [], [fit(ren("P4-80-el-d-p3-m25", "iso_bottom"), 700), fit(ren("P4-80-el-d-p3-m25", "front"), 700)]),
            ("Neck standing 15° off the body", [], [fit(ren("P4-80-el-d-p3-stand", "iso_bottom"), 700), fit(ren("P4-80-el-d-p3-stand", "front"), 700)])]
    sheet("decision6_neck_stance_outside.png", "Decision 6, outside", cols)


def applied():
    """The decisions as applied on 2026-11-18 (the owner took recommendations 1 to 5 and the standing neck for 6):
    the Stage 2 seed body and the two Stage 1 stubs that test the build. Reads the stage pictures in addon_renders/
    and, for "before", the same pictures as committed (git show HEAD:...)."""
    import io
    import subprocess

    def before(body, view):
        raw = subprocess.run(["git", "show", f"HEAD:addon_renders/{body}/{view}.png"], cwd=ROOT, capture_output=True, check=True).stdout
        return Image.open(io.BytesIO(raw)).convert("RGB")

    cols = [("Before (2026-11-17)", ["Fan cut, box stub, level windway, 1.56 mm at the mouth end.", "Voicing hash 617b869f0b10."],
             [fit(before("P4-80", "iso_bottom"), 700), fit(before("P4-80", "front"), 700)]),
            ("Now (2026-11-18)", ["Ellipse cut, neck standing 15°, pipe 10° lower inside it, 3 mm at the mouth end.", "Voicing hash b4620fbf3d67."],
             [fit(ren("P4-80", "iso_bottom"), 700), fit(ren("P4-80", "front"), 700)])]
    sheet("applied_seed_body_outside.png", "Applied: the seed body P4 at 80 cm³, outside", cols)
    cols = [("", ["Top: before. Level windway 1.56 → 1.20 mm in a box stub; plastic under the windway at the exit 3.21 mm.",
                  "Bottom: now. The neck stands 15° off the body; the pipe lies 10° lower inside it and reaches the lip heading 5° into the chamber;",
                  "3.00 → 1.20 mm; plastic under the windway at the exit 4.44 mm. Chamber in blue, lip edge at the red cross."],
             [fit(before("P4-80", "section_windway"), 1467), fit(ren("P4-80", "section_windway"), 1467)])]
    sheet("applied_seed_body_section.png", "Applied: the seed body P4 at 80 cm³, section through the windway", cols)
    cols = [("V-a: the build of the bodies", ["The 80 cm³ window, ellipse cut, standing neck, lowered pipe"],
             [fit(ren("V-a", "iso_bottom"), 700), fit(ren("V-a", "section_windway"), 700)]),
            ("V-af: the plain build", ["The same window, fan cut, level windway, box stub"],
             [fit(ren("V-af", "iso_bottom"), 700), fit(ren("V-af", "section_windway"), 700)])]
    sheet("applied_stubs.png", "Applied: the two Stage 1 stubs that test the build (decision 5)", cols)

    # The open point: the angle of the pipe inside the neck that stands 15 degrees (decisions 3 and 6 together).
    options = (("P4-80", "Built (the rule): pipe 10° under the neck, +5° against the body",
                ["Jet enters the chamber at 5°. Under the exit 4.44 mm.", "Mouth end of the neck 13.8 × 15.0 mm.",
                 "Thinnest plastic 3.52 mm."]),
               ("P4-80-st15-lvl", "Pipe 15° under the neck, level with the body",
                ["Jet along the labium's inner face. Under the exit 3.20 mm.", "Mouth end of the neck 13.8 × 19.2 mm.",
                 "Thinnest plastic 0.95 mm (under the 1.2 mm minimum)."]),
               ("P4-80-st15-m25", "Pipe 17.5° under the neck, −2.5° against the body",
                ["Jet leaves the inner face by 2.5°. Under the exit 1.47 mm.", "Mouth end of the neck 13.8 × 21.3 mm.",
                 "Thinnest plastic 0.92 mm (under the 1.2 mm minimum)."]))
    cols = [(head, caps, [fit(ren(body, "section_windway"), 900), fit(ren(body, "iso_bottom"), 900)]) for body, head, caps in options]
    sheet("question_pipe_angle.png", "Open point: the angle of the pipe inside the neck that stands 15° (seed body, 80 cm³)", cols)


if __name__ == "__main__":
    import sys
    applied() if "applied" in sys.argv[1:] else main()
