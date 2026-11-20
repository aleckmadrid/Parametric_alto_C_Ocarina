"""One drawing of the low-voicing trials: the body's cross-section through the lip at every port angle, laid on one
body. Needs matplotlib and numpy.

    python Analizes_ocarinas/Low_voicing/sheet_sections_overlay.py

Writes sheet_sections_overlay_P4.png and sheet_sections_overlay_P1.png next to this file. The trial files give each
section in the frame of its own lip; here they are moved onto the middle of the body, so that the body is drawn once
and the window, the pipe and the mouthpiece are seen to move.
"""
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
T = {}
for f in sorted((HERE / "trials").glob("*.json")):
    row = json.loads(f.read_text(encoding="utf-8"))
    T[f"{row['preset']}:{row['trial']}"] = row
COLOURS = {30: "#444444", 20: "#1f77b4", 10: "#d95f02", 0: "#2ca02c"}
SETS = {"P4": ("lv-30", "lv-20f", "lv-10f", "lv-0f"), "P1": ("lv-30", "lv-20f", "lv-10f", "lv-0f")}
LONG = {"P4": ("lv-20fw", "lv-10fw")}
# The Spencer's window, as its report reads it from one oblique photo: 16 to 20 mm inside the player-side edge of a
# body 57 mm wide (Analizes_ocarinas/Spencer_OoT_12h/Spencer_OoT_12h.md section 5). As shares of the width:
SPENCER_SHARE = (16.0 / 57.0, 20.0 / 57.0)
SONGBIRD_MOUTHPIECE = 0.28          # the Songbird's mouthpiece beyond the body edge, as a share of the body length


def centred(r):
    """The section's segments and the points of the trial, moved to the middle of the body's own section."""
    S = np.asarray(r["outline_body"], float)                       # (n, 2, 2): u = +Y (away from the player), v = +Z (deck)
    g = r["geometry"]
    cy = S[..., 0].max() - 0.5 * g["body_width_at_window_mm"]      # the far flank and the deck are the body's own
    cz = S[..., 1].max() - 0.5 * g["body_thickness_at_window_mm"]
    shift = np.array([cy, cz])
    mouth = np.array(g["mouth_xyz"][1:]) - shift
    window = np.array(g["window_xyz"][1:]) - shift
    return S - shift, mouth, window, -shift                       # the last one is the lip (the origin of the trial)


def draw(pid, title, body_length_mm):
    keys = [f"{pid}:{n}" for n in SETS[pid] if f"{pid}:{n}" in T and not T[f"{pid}:{n}"].get("build_failed")]
    if not keys:
        return
    fig, ax = plt.subplots(figsize=(13.5, 8.2), dpi=120)
    g0 = T[keys[0]]["geometry"]
    W, Th = g0["body_width_at_window_mm"], g0["body_thickness_at_window_mm"]
    for key in keys:
        r = T[key]
        port = int(round(r["overrides"]["port_angle_deg"]))
        col = COLOURS[port]
        S, mouth, window, lip = centred(r)
        ax.add_collection(LineCollection(S, colors=col, linewidths=1.5 if port == 30 else 1.2, alpha=0.9))
        ax.plot(*lip, marker="+", color=col, markersize=13, markeredgewidth=2.2)
        ax.plot(*mouth, marker="o", color=col, markersize=6)
        g = r["geometry"]
        ax.plot([], [], color=col, linewidth=2.5,
                label=(f"port {port}°" + (" (the rule)" if port == 30 else "") + f": window {g['window_in_from_player_edge_mm']:.0f} mm inside the edge "
                       f"({100 * g['window_in_share_of_width']:.0f} %), mouthpiece {abs(g['pipe_above_level_deg']):.0f}° "
                       f"{'above' if g['pipe_above_level_deg'] >= 0 else 'below'} level, mouth end {g['mouth_end_beyond_player_edge_mm']:.0f} mm out, "
                       f"{abs(g['mouth_end_below_mid_plane_mm']):.0f} mm {'below' if g['mouth_end_below_mid_plane_mm'] >= 0 else 'above'} the middle"))
    for name in LONG.get(pid, ()):
        key = f"{pid}:{name}"
        if key in T and not T[key].get("build_failed"):
            r = T[key]
            port = int(round(r["overrides"]["port_angle_deg"]))
            _, mouth, _, lip = centred(r)
            ax.plot(*mouth, marker="o", markerfacecolor="white", color=COLOURS[port], markersize=8, markeredgewidth=2)
            ax.annotate(f"45 mm pipe", mouth, textcoords="offset points", xytext=(-6, -16), ha="right", fontsize=9, color=COLOURS[port])
    # under the body, on one scale: the middle of each trial's window (ticks) and the Spencer's window (band)
    edge = -0.5 * W
    y0 = -0.5 * Th - 11.0
    for key in keys:
        r = T[key]
        _, _, window, _ = centred(r)
        col = COLOURS[int(round(r["overrides"]["port_angle_deg"]))]
        ax.plot([window[0], window[0]], [y0 + 1.2, y0 + 4.6], color=col, linewidth=3)
        ax.plot([window[0], window[0]], [y0 + 4.6, window[1]], color=col, linewidth=0.6, linestyle=":")
    ax.plot([edge + SPENCER_SHARE[0] * W, edge + SPENCER_SHARE[1] * W], [y0, y0], color="#b22222", linewidth=6, solid_capstyle="butt")
    ax.annotate("middle of the window: the trials (ticks) and the Spencer\n"
                "(red band: 28 to 35 % of the width inside the edge; one oblique photo, rough)",
                (edge + SPENCER_SHARE[1] * W + 2.5, y0 + 1.6), va="center", fontsize=9.5, color="#b22222")
    xm = edge - SONGBIRD_MOUTHPIECE * body_length_mm
    ax.plot([xm, xm], [-0.5 * Th - 4, 0.5 * Th - 14], color="#b22222", linewidth=1.2, linestyle="--")
    ax.annotate("Songbird: the mouthpiece tip,\n0.28 of the body length beyond\n"
                f"the edge ({SONGBIRD_MOUTHPIECE * body_length_mm:.0f} mm at this size)",
                (xm + 1.0, 0.5 * Th - 13), ha="left", va="bottom", fontsize=9.5, color="#b22222")
    ax.axhline(0.0, color="#999999", linewidth=0.6, linestyle=":")
    ax.axvline(edge, color="#999999", linewidth=0.6, linestyle=":")
    ax.annotate("middle of the body", (0.5 * W - 1, 0.8), fontsize=8.5, color="#777777", ha="right")
    ax.annotate("player-side edge of the body", (edge - 0.8, 0.5 * Th + 1.0), fontsize=8.5, color="#777777", ha="right")
    ax.set_aspect("equal")
    ax.set_xlim(edge - 52, 0.5 * W + 30)
    ax.set_ylim(-0.5 * Th - 15, 0.5 * Th + 6)
    ax.set_xlabel("across the body, mm (the player is on the left)")
    ax.set_ylabel("mm (the finger deck is up)")
    ax.grid(True, color="#dddddd", linewidth=0.5)
    ax.set_title(f"{title}: the cross-section through the lip at four port angles, laid on one body\n"
                 "cross = the lip, dot = the middle of the mouth end of the pipe (30 mm pipe); open dot = the same with a 45 mm pipe",
                 fontsize=11.5, loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), fontsize=10, frameon=False, ncol=1)
    fig.tight_layout()
    out = HERE / f"sheet_sections_overlay_{pid}.png"
    fig.savefig(out)
    plt.close(fig)
    print(out.name)


if __name__ == "__main__":
    draw("P4", "P4-80, the seed", 140.0)
    draw("P1", "P1-80, the teardrop", 118.0)
