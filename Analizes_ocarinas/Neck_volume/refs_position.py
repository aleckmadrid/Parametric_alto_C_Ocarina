"""Where the neck and the window sit on two reference models, measured in the frame of the BODY. Run with python -I:

    python -I Analizes_ocarinas/Neck_volume/refs_position.py "<folder>/obj_1_Ocarina_Fixed.stl" "<folder>/obj_1_OcarinaDeluxe.stl"

The two files are the owner's (2026-11-18): two playable 12-hole ocarinas of bulb shape whose tuning is not vouched
for. They are read where they lie and are not copied; nothing here uses them as acoustic references. Both stand on
their bulb end in the file, so the plane z = 40 mm is the body's cross-section through the middle of the windway.

Body frame of every picture: the PLAYER is on the left, the finger DECK is up, the origin is the lip. "Level" is
the direction straight toward the player, parallel to the plane between deck and thumb face.

The points were read by hand on enlarged sections, to about 0.2 mm (REFS below). Writes refs_position.json and, when
throwback_trials.json is there, sheet_refs_position.png with the add-on's bodies beside the references.
"""
import json
import math
import pathlib
import site
import sys

site.addsitedir(site.getusersitepackages())
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
SECTION_Z = 40.0
# In the file's x, y (the section plane): where the player is, where the deck is, and the points read on the section.
#   exit_roof, exit_floor   the two ends of the pipe's walls at the windway exit
#   mouth_roof, mouth_floor the same walls at the mouth end
#   lip                     the tip of the labium
#   lip_in                  a point on the chamber wall 8 to 9 mm beyond the lip (the direction of the inner wall)
#   flank                   two points on the neck's outer flank (the side away from the body), mouth end first
#   roof_out                the outer corner of the roof where it ends at the window
REFS = {
    "Ocarina 12": dict(arg=0, player=(0.0, -1.0), deck=(-1.0, 0.0),
                       exit_roof=(140.6, 112.2), exit_floor=(139.1, 112.5), mouth_roof=(136.0, 88.0), mouth_floor=(133.0, 88.0),
                       lip=(141.4, 119.1), lip_in=(144.85, 128.0), flank=((142.5, 92.0), (142.6, 109.0)), roof_out=(142.75, 111.7)),
    "Deluxe": dict(arg=1, player=(1.0, 0.0), deck=(0.0, -1.0),
                   exit_roof=(104.6, 106.15), exit_floor=(104.25, 104.05), mouth_roof=(134.3, 96.1), mouth_floor=(134.3, 93.3),
                   lip=(97.65, 107.4), lip_in=(89.0, 109.0), flank=((133.0, 100.2), (106.0, 107.3)), roof_out=(104.95, 107.55)),
}


def ang(v, level, deck):
    """Angle of a direction above the level (toward the deck), in degrees, for a direction that points at the player."""
    return math.degrees(math.atan2(v @ deck, v @ level))


def main(argv):
    out = {}
    for name, r in REFS.items():
        mesh = trimesh.load(argv[r["arg"]], force="mesh")
        segs = trimesh.intersections.mesh_plane(mesh, [0, 0, 1.0], [0, 0, SECTION_Z])[:, :, :2]
        P, D = np.array(r["player"]), np.array(r["deck"])
        pt = {k: np.array(r[k], float) for k in ("exit_roof", "exit_floor", "mouth_roof", "mouth_floor", "lip", "lip_in", "roof_out")}
        E, M = 0.5 * (pt["exit_roof"] + pt["exit_floor"]), 0.5 * (pt["mouth_roof"] + pt["mouth_floor"])
        up_pipe = (M - E) / np.linalg.norm(M - E)                  # upstream, toward the player
        chord = (E - pt["lip"]) / np.linalg.norm(E - pt["lip"])    # from the lip back to the exit
        wall_dir = (pt["lip"] - pt["lip_in"]) / np.linalg.norm(pt["lip"] - pt["lip_in"])    # along the chamber wall, toward the player
        f0, f1 = (np.array(q, float) for q in r["flank"])
        flank = (f0 - f1) / np.linalg.norm(f0 - f1)
        # the section's own middle: the mean of the outline points of the body ring away from the neck
        pts = segs.reshape(-1, 2)
        rel = (pts - pt["lip"])
        body = pts[(rel @ P) < 4.0]                                 # everything that is not the neck
        centre = 0.5 * (body.min(axis=0) + body.max(axis=0))
        to_lip = pt["lip"] - centre
        to_frame = lambda Q: np.stack([-(np.asarray(Q) - pt["lip"]) @ P, (np.asarray(Q) - pt["lip"]) @ D], axis=-1)   # noqa: E731  player on the left
        n = dict(
            pipe_above_level_deg=ang(up_pipe, P, D), window_chord_above_level_deg=ang(chord, P, D),
            window_faces_from_down_deg=ang(chord, P, D),          # the window's normal is square to the chord
            chamber_wall_at_lip_above_level_deg=ang(wall_dir, P, D),
            jet_enters_chamber_deg=ang(wall_dir, P, D) - ang(up_pipe, P, D),
            neck_flank_above_level_deg=ang(flank, P, D), pipe_under_flank_deg=ang(up_pipe, P, D) - ang(flank, P, D),
            window_length_mm=float(np.linalg.norm(E - pt["lip"])), exit_height_mm=float(np.linalg.norm(pt["exit_roof"] - pt["exit_floor"])),
            roof_over_exit_mm=float(np.linalg.norm(pt["roof_out"] - pt["exit_roof"])),
            pipe_length_mm=float(np.linalg.norm(M - E)),
            window_around_section_deg=math.degrees(math.atan2(to_lip @ P, -(to_lip @ D))),     # from straight down toward the player, seen from the middle
            mouth_end_behind_lip_mm=float((M - pt["lip"]) @ P), mouth_end_above_lip_mm=float((M - pt["lip"]) @ D),
            body_section_mm=[float(np.ptp(body @ P)), float(np.ptp(body @ D))])
        out[name] = dict(numbers=n, outline=np.round(to_frame(segs), 3).tolist(),
                         marks={k: to_frame(v).tolist() for k, v in dict(pt, exit=E, mouth=M).items()})
        print(name)
        for k, v in n.items():
            print(f"   {k}: {np.round(v, 2).tolist()}")
    (HERE / "refs_position.json").write_text(json.dumps(out), encoding="utf-8")
    sheet(out)


def panel(ax, segs, title, lines):
    for (x0, z0), (x1, z1) in segs:
        ax.plot([x0, x1], [z0, z1], "-", color="#222222", lw=1.0, solid_capstyle="round")
    ax.plot([0], [0], "+", color="#d1495b", ms=14, mew=2)
    ax.axhline(0.0, color="#7da0d8", lw=0.6)
    ax.set_xlim(-58, 38)
    ax.set_ylim(-30, 46)
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3)
    ax.set_title(title + "\n" + "\n".join(lines), fontsize=11, loc="left")


def sheet(refs):
    path = HERE / "throwback_trials.json"
    ours = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    cols = [(n, r["outline"], [f"window faces {r['numbers']['window_faces_from_down_deg']:.0f}° from straight down toward the player",
                               f"pipe {r['numbers']['pipe_above_level_deg']:.0f}° above level; outer flank of the neck {r['numbers']['neck_flank_above_level_deg']:.0f}°",
                               f"roof over the exit {r['numbers']['roof_over_exit_mm']:.1f} mm, cut square; window {r['numbers']['window_length_mm']:.1f} mm long"])
            for n, r in refs.items()]
    for key, head in (("P1:now", "Add-on P1-80, the rules"), ("P1:sq", "Add-on P1-80, trial sq"), ("P1:tb-f", "Add-on P1-80, trial tb-f"),
                      ("P1:tb-l", "Add-on P1-80, trial tb-l")):
        r = ours.get(key)
        if not r or r.get("build_failed"):
            continue
        nk = r["neck"]
        cols.append((head, r["outline_body"],
                     [f"window faces {r['window_faces_from_down_deg'] - (r['window_faces_from_down_deg'] - r['pipe_above_level_deg']):.0f}° from straight down toward the player",
                      f"pipe {r['pipe_above_level_deg']:.0f}° above level; outer flank of the neck {abs(round(r['neck_top_above_level_deg'])):.0f}°",
                      f"roof over the exit {nk['over_pipe_roof_at_exit_mm']:.1f} mm, " + ("cut square" if not r["shelf_angle_deg"] else f"shelf {r['shelf_angle_deg']:.0f}°")
                      + "; window 9.65 mm long"]))
    rows = 2
    per = math.ceil(len(cols) / rows)
    fig, axs = plt.subplots(rows, per, figsize=(8.2 * per, 7.4 * rows))
    axs = np.atleast_2d(axs)
    for ax in axs.ravel():
        ax.axis("off")
    for ax, (title, segs, lines) in zip(axs.ravel(), cols):
        ax.axis("on")
        panel(ax, segs, title, lines)
    fig.suptitle("The body's cross-section through the windway. The player is on the left, the finger deck is up, the cross is the lip. Millimetres.", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(HERE / "sheet_refs_position.png", dpi=80)
    print("sheet_refs_position.png")


if __name__ == "__main__":
    main(sys.argv[1:])
