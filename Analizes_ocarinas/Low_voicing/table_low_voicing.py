"""The tables of the low-voicing record, from the trial files. Standard library only.

    python Analizes_ocarinas/Low_voicing/table_low_voicing.py > Analizes_ocarinas/Low_voicing/tables.md
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
T = {}
for f in sorted((HERE / "trials").glob("*.json")):
    row = json.loads(f.read_text(encoding="utf-8"))
    T[f"{row['preset']}:{row['trial']}"] = row
ORDER = ("lv-30", "lv-20", "lv-20f", "lv-20fw", "lv-15f", "lv-10", "lv-10f", "lv-10fw", "lv-10fd", "lv-10fn", "lv-10fwdn",
         "lv-10fwdnr",
         "lv-5f", "lv-5fw", "lv-0", "lv-0f")


def built_port(asked: float, res_v: int = 128) -> float:
    """The port angle the body was built with: the port is moved to the nearest vertex of the cavity mesh, which has
    128 segments around the section (cavity.RES_V), so the angle moves by up to 1.4 degrees."""
    step = 360.0 / res_v
    return 270.0 - round((270.0 - asked) / step) * step


def free_depth(r) -> str:
    msg = r["checks"]["voicing_keepouts"]["message"]
    key = "free depth below the window "
    return msg.split(key)[1].split(" mm")[0] if key in msg else "?"


def side(value, pos, neg, fmt="{:.1f}"):
    return f"{fmt.format(abs(value))} {pos if value >= 0 else neg}"


def result(r):
    if r.get("build_failed"):
        return "build stopped: " + r["build_failed"][:80]
    return "passes" if not r["unexpected"] else "**fails `" + "`, `".join(r["unexpected"]) + "`**"


def main():
    out = []
    for pid, title in (("P4", "P4-80, the seed"), ("P1", "P1-80, the teardrop")):
        keys = [f"{pid}:{n}" for n in ORDER if f"{pid}:{n}" in T]
        if not keys:
            continue
        out += [f"### {title}: where the voicing and the mouthpiece lie", "",
                "| Trial | Port | Foot of the neck | Pipe | Window inside the player-side edge | Window faces, from straight down | Mouthpiece against the level of the body "
                "| Mouth end beyond the body's edge | Mouth end against the middle of the body | Neck below the body's lowest point | Checks |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for k in keys:
            r = T[k]
            if r.get("build_failed"):
                out.append(f"| `{r['trial']}` | {r['overrides'].get('port_angle_deg'):g}° | | | | | | | | | {result(r)} |")
                continue
            g, n = r["geometry"], r["neck"]
            out.append(f"| `{r['trial']}` | {r['overrides']['port_angle_deg']:g}° (built {built_port(r['overrides']['port_angle_deg']):.1f}°) "
                       f"| {n.get('base_width_mm', float('nan')):.0f} mm | {r['windway_length_mm']:g} mm "
                       f"| {g['window_in_from_player_edge_mm']:.1f} mm ({100 * g['window_in_share_of_width']:.0f} % of {g['body_width_at_window_mm']:.0f} mm) "
                       f"| {abs(g['window_faces_from_down_deg']):.0f}° | {side(round(g['pipe_above_level_deg']) + 0.0, 'above', 'below', '{:.0f}°')} "
                       f"| {g['mouth_end_beyond_player_edge_mm']:.1f} mm | {side(g['mouth_end_below_mid_plane_mm'], 'mm below', 'mm above')} "
                       f"| {max(g['body_hangs_below_plain_skin_mm'], 0.0):.1f} mm | {result(r)} |")
        out += ["", f"### {title}: what the checks and the theory read", "",
                "| Trial | L thumb hole edge to the window / to the neck's box | R thumb hole edge to the window / to the neck's box | Free air below the window (the check's number) "
                "| Upright wall under the exit | Chamber wall along the jet, radius | Pocket | First cavity mode ÷ F6 | Steepest plastic seen from the window rim "
                "| Thinnest plastic | Plastic | Capped air | Voicing hash |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for k in keys:
            r = T[k]
            if r.get("build_failed"):
                continue
            g, th = r["geometry"], r["thumbs"]
            wall = r["checks"]["wall_thickness"]["message"]
            thin = wall.split("away from the voicing and the tubes: ")[1].split(" mm")[0] if "away from the voicing and the tubes: " in wall else "?"
            out.append(f"| `{r['trial']}` | {th['L_thumb']['to_window_mm']:.1f} / {th['L_thumb']['to_block_mm']:.1f} mm | {th['R_thumb']['to_window_mm']:.1f} / {th['R_thumb']['to_block_mm']:.1f} mm "
                       f"| {free_depth(r)} mm | {g['drop_height_at_exit_mm']:.2f} mm | {g['chamber_radius_along_jet_mm']:.1f} mm | {r['pocket_cm3']:.3f} cm³ "
                       f"| {r['cavity_mode']['ratio']:.3f} | {r['flare_steepest_deg']:.0f}° ({r['above_outer_face_mm']:.1f} mm high) | {thin} mm | {r['plastic_cm3']:.1f} cm³ "
                       f"| {r['capped_air_cm3']:.2f} cm³ | `{r['voicing_hash']}` |")
        out.append("")
        warn = {k: T[k].get("warnings") for k in keys if not T[k].get("build_failed")}
        if len({tuple(w) for w in warn.values()}) == 1:
            out += [f"Warnings, the same on every trial of this body: {', '.join('`' + w + '`' for w in next(iter(warn.values()))) or 'none'}.", ""]
        else:
            out += ["Warnings: " + "; ".join(f"`{k.split(':')[1]}`: {', '.join(w) or 'none'}" for k, w in warn.items()) + ".", ""]
        for k in keys:
            for name, msg in (T[k].get("unexpected_messages") or {}).items():
                out.append(f"- `{T[k]['trial']}` fails `{name}`: {msg}")
        out.append("")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
