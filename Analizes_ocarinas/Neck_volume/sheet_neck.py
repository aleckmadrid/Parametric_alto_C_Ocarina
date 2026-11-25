"""Sheets of the neck volume trials (2026-11-18). Needs Pillow and matplotlib.

    python Analizes_ocarinas/Neck_volume/sheet_neck.py

Reads neck_trials.json and images/<trial>_*.png (neck_trials.py) and sample_frame.json (sample_frame.py). Writes

    sheet_sample_against_neck.png   long sections in the frame of the window: the owner's sample, the neck of the rules, trial nk-a
    sheet_neck_volume.png           the neck of the rules and three necks whose top line follows the pipe
    sheet_pipe_angle.png            the following neck with the pipe at 0, +5, +10 and +17.65 degrees
    sheet_sample_cut.png            the owner's sample with the add-on's cut (sample_cut.py), beside two trials
"""
import json
import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE / "images"
T = json.loads((HERE / "neck_trials.json").read_text(encoding="utf-8"))
S = json.loads((HERE / "sample_frame.json").read_text(encoding="utf-8"))
SC = json.loads((HERE / "sample_cut.json").read_text(encoding="utf-8")) if (HERE / "sample_cut.json").exists() else None
INK, PAD, COL = (20, 50, 120), 14, 500


def font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


F_HEAD, F_CAP, F_ROW = font(26), font(19), font(20)


def fit(im, width):
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def trim(im, pad=10):
    """Cut the white border of a render away."""
    a = np.asarray(im.convert("RGB"))
    mask = (a < 250).any(axis=2)
    if not mask.any():
        return im
    ys, xs = np.where(mask.any(axis=1))[0], np.where(mask.any(axis=0))[0]
    return im.crop((max(xs[0] - pad, 0), max(ys[0] - pad, 0), min(xs[-1] + pad, im.width), min(ys[-1] + pad, im.height)))


def caption(name):
    if name == "sample-cut":
        n, cut = S["numbers"], {s["name"]: s["mm3"] for s in SC["steps"]}
        return [f"Plastic over the pipe: {n['plastic_over_pipe_roof_mm'][0]:.1f} to {n['plastic_over_pipe_roof_mm'][1]:.1f} mm,",
                "the same from the exit to the mouth end",
                "Above the outer face of the window: nothing",
                f"The window cut removes {cut['window throat + labium ramp']:.0f} mm³ (wall {n['wall_at_flat_face_mm']:.1f} mm)",
                f"Mouth end 15 × 8 mm; foot {n['neck_across_the_pipe'][0]['width_mm']:.1f} × {n['neck_across_the_pipe'][0]['depth_mm']:.1f} mm",
                f"Middle line of the neck {n['neck_middle_line_deg']:.0f}° off the window face",
                f"Pipe {n['pipe_against_face_deg']:.1f}° off the window face",
                "Checks: none run (a picture, not an instrument)"]
    r = T[name]
    if r.get("build_failed"):
        return ["BUILD FAILED:", r["build_failed"][:60]]
    n = r["neck"]
    return [f"Plastic over the pipe: {n['over_pipe_roof_at_exit_mm']:.1f} mm at the exit,",
            f"{n['over_pipe_roof_at_mouth_mm']:.1f} mm at the mouth end",
            f"Above the outer face of the window: {r['above_outer_face_mm']:.1f} mm, {r['flare_steepest_deg']:.0f}° steep",
            f"The window cut removes {r['window_cut_removes_mm3']:.0f} mm³",
            f"Mouth end {n['mouth_width_mm']:.1f} × {n['mouth_depth_mm']:.1f} mm; foot {n['base_width_mm']:.1f} × {n['base_depth_mm']:.1f} mm",
            f"Middle line of the neck {n['middle_line_deg_against_body']:.0f}° off the body",
            f"Plastic of the body {r['plastic_cm3']:.1f} cm³",
            ("Checks: no unexpected failure" if not r["unexpected"] else f"FAILS {len(r['unexpected'])} checks (window, exit, keep-out, floor)" if len(r["unexpected"]) == 4
             else "FAILS: " + ", ".join(r["unexpected"]))]


ROWS = (("outside", "From the mouth end"), ("window", "From beyond the window"), ("side", "Profile (along the body)"), ("mouth", "Mouth end"),
        ("section", "Section through the pipe"))


def sheet(out_name, title, lines, columns):
    """columns: list of (heading, trial name)."""
    cells = {}
    for _, name in columns:
        for key, _ in ROWS:
            p = IMG / f"{name}_{key}.png"
            if p.exists():
                im = Image.open(p).convert("RGB")
                cells[(name, key)] = fit(im if key == "section" else trim(im), COL)
    row_h = [max((cells[(n, key)].height for _, n in columns if (n, key) in cells), default=0) for key, _ in ROWS]
    cap_n = max(len(caption(n)) for _, n in columns)
    top = 54 + 28 * len(lines) + 10
    cap_h = 40 + cap_n * 25 + 10
    W = PAD + len(columns) * (COL + PAD)
    H = top + cap_h + sum(h + 30 + PAD for h in row_h) + PAD
    out = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(out)
    d.text((PAD, 12), title, fill=(0, 0, 0), font=F_HEAD)
    for i, line in enumerate(lines):
        d.text((PAD, 52 + 28 * i), line, fill=(40, 40, 40), font=F_ROW)
    for c, (head, name) in enumerate(columns):
        x = PAD + c * (COL + PAD)
        d.text((x, top), head, fill=INK, font=F_HEAD)
        for i, line in enumerate(caption(name)):
            d.text((x, top + 36 + i * 25), line, fill=(40, 40, 40), font=F_CAP)
        y = top + cap_h
        for (key, label), h in zip(ROWS, row_h):
            if c == 0:
                d.text((PAD, y), label, fill=(110, 110, 110), font=F_CAP)
            if (name, key) in cells:
                out.paste(cells[(name, key)], (x, y + 28))
            y += h + 30 + PAD
    out.save(HERE / out_name)
    print(out_name, out.size)


def draw_segments(ax, segs, color, lw=1.0):
    for (x0, z0), (x1, z1) in segs:
        ax.plot([x0, x1], [z0, z1], "-", color=color, lw=lw, solid_capstyle="round")


def line_at(ax, x0, z0, deg, length, color, label):
    """A dashed line from (x0, z0) going upstream (toward -x), rising by deg."""
    t = math.radians(deg)
    ax.plot([x0, x0 - length * math.cos(t)], [z0, z0 + length * math.sin(t)], "--", color=color, lw=1.1)
    ax.text(x0 - length * math.cos(t), z0 + length * math.sin(t) + 0.8, label, color=color, fontsize=10, ha="left", va="bottom")


def compare():
    fig, axs = plt.subplots(1, 3, figsize=(24, 9.2))
    n = S["numbers"]
    ax = axs[0]
    draw_segments(ax, S["sections"]["body"], "#222222")
    draw_segments(ax, S["sections"]["neck"], "#2e86ab", 1.4)
    draw_segments(ax, S["sections"]["wind"], "#d1495b", 1.2)
    ax.set_title(f"The owner's sample (body black, neck blue, wind cut red)\npipe {n['pipe_against_face_deg']:.1f}° off the window face; top line of the neck {n['neck_top_line_deg']:.1f}°; "
                 f"middle line {n['neck_middle_line_deg']:.0f}°\nplastic over the pipe {n['plastic_over_pipe_roof_mm'][0]:.1f} to {n['plastic_over_pipe_roof_mm'][1]:.1f} mm\n"
                 f"the top line runs into the body's outer face", fontsize=12)
    for ax, name, head in ((axs[1], "now", "The rules today"), (axs[2], "nk-a", "Trial nk-a: the top line follows the pipe")):
        r = T[name]
        draw_segments(ax, r["outline"], "#222222", 1.2)
        nk = r["neck"]
        over = f"{nk['over_pipe_roof_at_exit_mm']:.1f} mm at the exit, {nk['over_pipe_roof_at_mouth_mm']:.1f} mm at the mouth end"
        ax.set_title(f"{head} (P4-80, plastic outlined)\npipe +5° off the window face; middle line of the neck {nk['middle_line_deg_against_body']:.0f}°\n"
                     f"plastic over the pipe {over}\n{r['above_outer_face_mm']:.1f} mm of plastic stands above the outer face of the window", fontsize=12)
    for ax in axs:
        ax.plot([0], [0], "+", color="#d1495b", ms=14, mew=2)
        ax.axhline(0.0, color="#7da0d8", lw=0.6)
        ax.set_xlim(-48, 16)
        ax.set_ylim(-24, 20)
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3)
        ax.set_xlabel("along the jet, mm (0 = the lip; the mouth end is on the left)")
        ax.set_ylabel("out of the window face, mm")
    fig.suptitle("Long section through the pipe, in the frame of the window. Outside is up, the chamber is below the blue line.", fontsize=14)
    fig.tight_layout()
    fig.savefig(HERE / "sheet_sample_against_neck.png", dpi=80)
    print("sheet_sample_against_neck.png")


def main():
    compare()
    sheet("sheet_neck_volume.png", "The neck volume on P4-80: the rules today, and a neck whose top line follows the pipe",
          ["Same body, chamber, window cut (ellipse P3) and pipe (+5° against the body) in all four. Only the neck changes.",
           "The rules today: the top line of the neck stands 15° and the pipe 5°, so a wedge of plastic lies over the pipe and over the window."],
          [("The rules today", "now"), ("nk-a: top follows the pipe", "nk-a"), ("nk-slim: slimmer bell", "nk-slim"), ("nk-full: the sample's bell", "nk-full")])
    sheet("sheet_pipe_angle.png", "The following neck with the pipe at four angles (P4-80)",
          ["The top line of the neck is 2.2 mm over the pipe in all four, so the neck stands as the pipe stands.",
           "The angle is the pipe against the window face: 0° = along the labium's inner face; + = the jet enters the chamber. The rules have +5°."],
          [("nk-p0: pipe level", "nk-p0"), ("nk-a: pipe +5° (the rules)", "nk-a"), ("nk-p10: pipe +10°", "nk-p10"), ("nk-p17: +17.65° (the sample)", "nk-p17")])
    if SC:
        sheet("sheet_sample_cut.png", "The owner's sample with the add-on's windway and window cut, beside two trials",
              ["Left: the sample's own body and neck; the add-on's pipe, window and dish cut into them at the sample's own angle and wall.",
               "Middle and right: the add-on's body P4-80 with the following neck, at the rules' +5° and at +10°."],
              [("The sample, cut by the add-on", "sample-cut"), ("nk-a: pipe +5° (the rules)", "nk-a"), ("nk-p10: pipe +10°", "nk-p10")])


if __name__ == "__main__":
    main()
