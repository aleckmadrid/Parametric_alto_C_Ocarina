"""Sheets of series 3 after the owner's reference of 2026-11-20: the stance, the blend, the ridge field, the candidates.

    python Analizes_ocarinas/Low_voicing/sheet_series3.py

Writes sheet_s3_stance_P4.png, sheet_s3_blend_P4.png, sheet_s3_ridge_P4.png, sheet_s3_ridge_P1.png,
sheet_s3_shoulder_P4.png, sheet_s3_shoulder_presets.png and sheet_s3_candidates.png next to this file. Reads series3_trials.json and walls_desk_model.json. Needs Pillow.
(sheet_series3_walls.py makes the two sheets of the slab walls.)
"""
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE / "images_s3"
REF = HERE / "ref_oot_blend" / "images"
T = json.loads((HERE / "series3_trials.json").read_text(encoding="utf-8"))
DESK = json.loads((HERE / "walls_desk_model.json").read_text(encoding="utf-8")) if (HERE / "walls_desk_model.json").exists() else {}
CW, PAD = 520, 14
OUT_ROWS = (("thumbface", "Straight at the thumb face (the player at the top)", 300), ("end", "Along the body: the player on the left, the deck up", 300),
            ("bodysection", "The same, cut through the lip (red cross); air is blue; grid 10 mm", 330),
            ("back34", "From below and beyond, the tail toward the camera", 300), ("player", "From the player", 190),
            ("section", "Close cut through the window: the jet runs left to right", 200))
IN_ROWS = (("inside", "The thumb-face half seen from the chamber (the player at the top)", 330),
           ("alongthumbs", "Cut along the body through the thumb holes: the deck is up, air is blue, grid 10 mm", 290),
           ("alongwindow", "Cut along the body through the window", 290))


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
    g, n = r["geometry"], r.get("neck") or {}
    w = r.get("inner_walls") or {}
    cm = r.get("cavity_mode") or {}
    d = DESK.get(f"{key}@1") or {}
    out = [r["what"][:96], r["what"][96:192]] if len(r["what"]) > 96 else [r["what"]]
    out.append(f"Window {100 * g['window_in_share_of_width']:.0f} % of the width inside the edge, facing {g['window_faces_from_down_deg']:.0f}° from straight down")
    out.append(f"Mouth end {g['mouth_end_beyond_player_edge_mm']:.1f} mm beyond the edge, {g['mouth_end_below_mid_plane_mm']:+.1f} mm below the middle "
               f"(pipe {g['pipe_above_level_deg']:.0f}° above level)")
    out.append(f"Voicing hash {r['voicing_hash']}; plastic {r['plastic_cm3']:.1f} cm³; thumb holes to the window "
               f"{r['thumbs']['L_thumb']['to_window_mm']:.1f} / {r['thumbs']['R_thumb']['to_window_mm']:.1f} mm")
    sh = (r.get("shoulder") or {}).get("shoulder")
    if sh:
        out.append(f"Shoulder {sh['h']:g} mm ({sh['tail']:g} mm toward the tail, {sh['bulb']:g} toward the bulb): "
                   f"{r['shoulder']['shoulder_volume_cm3']:.1f} cm³ of the air is in it; body {g['body_width_at_window_mm']:.1f} mm wide at the window")
    mv = n.get("moved")
    if mv:
        out.append(f"Neck {n['base_width_mm']:.1f} mm at the body, {mv['mouth_end_across_mm']:.1f} x {mv['mouth_end_deep_mm']:.1f} mm at the mouth end; outside tilted "
                   f"{mv['tilt_deg']:g}°, turned {mv['yaw_deg']:+g}°, moved {mv['offset_mm']:+g} mm")
        out.append(f"Mouth end's outside {mv['mouth_end_moved_to_thumb_face_mm']:.1f} mm toward the thumb face, {mv['mouth_end_moved_to_tail_mm']:+.1f} mm toward the tail; "
                   f"least plastic around the pipe {mv['least_plastic_around_pipe_mm']:.2f} mm")
    un, hs = r.get("uneven") or {}, r.get("holes") or {}
    if hs:
        deck = [v["d_mm"] for k, v in hs.items() if "thumb" not in k]
        tubes = [k for k, v in hs.items() if v["tube_mm"] > 0]
        out.append((f"Wall {un['wall_least_mm']:.1f} mm on the deck, {un['wall_most_mm']:.1f} mm on the thumb face. " if un else "Even 4 mm wall. ")
                   + f"Deck holes {min(deck):.1f} to {max(deck):.1f} mm, thumb holes {hs['L_thumb']['d_mm']:.1f} / {hs['R_thumb']['d_mm']:.1f} mm")
        out.append("Inward tubes: " + (", ".join(f"{k} {hs[k]['tube_mm']:g} mm" for k in tubes) if tubes else "none"))
    b = r.get("blend") or {}
    if b.get("radius_mm"):
        out.append(f"Blend: ball {b['radius_mm']:g} mm (bulb side {b['radius_bulb_mm']:g}), {b.get('added_mm3', 0) / 1000:.2f} cm³ added, "
                   f"up to {b.get('thickest_mm', 0):.1f} mm thick")
    rg = w.get("ridge")
    if rg:
        bt = rg["between_thumb_and_window_mm"]
        out.append(f"Ridge field {rg['height_mm']:g} mm" + (", to the tail" if rg["tail"] else "") + f": takes {rg['air_taken_cm3']:.1f} cm³; "
                   f"between thumb hole and window L {bt.get('L_thumb', 0):.1f} / R {bt.get('R_thumb', 0):.1f} mm high")
    for name, x in (w.get("walls") or {}).items():
        out.append(f"Wall {name}: {x['thickness_mm']:g} mm thick, top {x['top_above_thumb_wall_mm']:.1f} mm up ({100 * x['blocked_share']:.0f} % blocked)")
    out.append(f"First cavity mode {cm.get('ratio', float('nan')):.2f} × F6" + (f" ({d['closed_ratio']:.2f} on a 1.0 mm grid)" if d else ""))
    if "conductance_left_L" in d:
        out.append(f"Thumb holes' effect left (model): L {100 * d['conductance_left_L']:.0f} %, R {100 * d['conductance_left_R']:.0f} %, "
                   f"both {100 * d['conductance_left_LR']:.0f} %")
    bad = r.get("unexpected") or []
    out.append("Checks: no unexpected failure" if not bad else "Checks FAIL: " + ", ".join(bad))
    return out, not bad


def sheet(name, title, sub, keys, rows, ref=None):
    keys = [k for k in keys if k in T and "build_failed" not in T[k]]
    if not keys:
        return
    f_h, f_t, f_s = font(20, True), font(15, True), font(13)
    head_h = 190
    n_ref = 1 if ref else 0
    W = PAD + (len(keys) + n_ref) * (CW + PAD)
    H = 70 + head_h + sum(h + 26 for _, _, h in rows) + PAD
    im = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(im)
    dr.text((PAD, 10), title, font=f_h, fill="black")
    dr.text((PAD, 38), sub, font=f_s, fill=(70, 70, 70))
    if ref:
        dr.text((PAD, 70), ref[0], font=f_t, fill=(20, 40, 110))
        for i, s in enumerate(ref[1]):
            dr.text((PAD, 92 + i * 15), s, font=f_s, fill="black")
    for c, key in enumerate(keys):
        x = PAD + (c + n_ref) * (CW + PAD)
        dr.text((x, 70), key.replace(":", " "), font=f_t, fill=(20, 40, 110))
        ls, ok = lines(key)
        for i, s in enumerate(ls):
            last = i == len(ls) - 1
            dr.text((x, 92 + i * 15), s[:98], font=f_s, fill=((0, 110, 40) if ok else (190, 0, 0)) if last else "black")
    y = 70 + head_h
    for rname, rtitle, h in rows:
        dr.text((PAD + n_ref * (CW + PAD), y), rtitle, font=f_s, fill=(90, 90, 90))
        if ref and rname in ref[2]:
            p = ref[2][rname]
            if p.exists():
                im.paste(fit(p, CW, h), (PAD, y + 20))
        for c, key in enumerate(keys):
            p = IMG / f"{key.replace(':', '_')}_{rname}.png"
            if p.exists():
                im.paste(fit(p, CW, h), (PAD + (c + n_ref) * (CW + PAD), y + 20))
        y += h + 26
    out = HERE / name
    im.save(out)
    print(out.name, im.size)


def main():
    ref_out = ("The owner's reference (Blender file), at the size of the file",
               ["175 mm long, 191 cm³ of air; at 0.74 to 0.83 of this size the", "kernel puts its lowest note at A4 (77 to 110 cm³).",
                "Window faces about 23° from straight down; the pipe is 73 mm long,", "curved, and enters 4° into the chamber against the chamber wall.",
                "The mouth end stands at mid thickness. Wall 5.3 mm, 1.3 to 2.3 mm", "at the holes (hollowed from inside)."],
               {"thumbface": REF / "ref_thumb.png", "end": REF / "ref_bulb.png", "bodysection": REF / "ref_section_across_pipe.png",
                "back34": REF / "ref_thumbwin.png", "player": REF / "ref_player.png", "section": REF / "ref_section_across_pipe_close.png"})
    p4 = lambda *names: [f"P4:{n}" for n in names]      # noqa: E731
    sheet("sheet_s3_stance_P4.png", "Series 3: the stance of the owner's reference, with settings the add-on has (P4-80)",
          "Port angle, the pipe's angle into the chamber (+8° is the rule) and its length; 'raised' = the neck's outside 8° over the pipe. "
          "A new pipe angle or length is a new voicing hash. Nothing was printed.",
          p4("s3-fwr", "s3-r20", "s3-r20p", "s3-r20pn", "s3-r15pn", "s3-r10pn", "s3-r25pn"), OUT_ROWS, ref_out)
    sheet("sheet_s3_blend_P4.png", "Series 3: the blend between the neck and the body, a rolling-ball fillet on the outside (P4-80, stance of s3-r20p)",
          "The ball fills the crease where the neck meets the body. It adds nothing on a hole's rim, nothing inside the keep-out of the window, "
          "and it does not change the voicing hash.",
          p4("s3-r20p", "s3-b8", "s3-b16", "s3-b24", "s3-ba", "s3-bw", "s3-fwr-b8"), OUT_ROWS[:5], ref_out)
    ref_in = ("Spencer (owner's photos): the thumb-face half and the press moulds", [], {"inside": HERE / "reference_photos" / "spencer_04_half_shell_inside.png",
                                                                                      "alongthumbs": HERE / "reference_photos" / "spencer_05_press_moulds.png"})
    for pid in ("P4", "P1"):
        sheet(f"sheet_s3_ridge_{pid}.png", f"Series 3: the ridge field, a thick thumb-face wall with pockets left in it ({pid}-80, port 10°, control s3-fwr)",
              "A smooth height field of plastic on the thumb-face wall; a funnel is left around each thumb hole and the voicing's pocket is kept free. "
              "The chamber is grown until the air is 80 cm³ again.",
              [f"{pid}:{n}" for n in ("s3-fwr", "s3-w25", "s3-k1", "s3-k2", "s3-k3", "s3-k4", "s3-k5", "s3-k6", "s3-k7")], IN_ROWS, ref_in)
    sheet("sheet_s3_shoulder_P4.png", "Series 3: the voicing shoulder, extra volume of the body around the voicing (P4-80)",
          "Around the port's station the player-side half of the chamber is made wider; the wall and the outside follow. The air is still 80 cm³, "
          "so the rest of the body is a little smaller. Lopsided blend as in s3-ba. s3-ba is the same body without a shoulder.",
          p4("s3-ba", "s3-h6", "s3-h9", "s3-h9p25", "s3-h9p30", "s3-h12p25", "s3-h9e", "s3-h9s"), OUT_ROWS[:5] + IN_ROWS[:1], ref_out)
    sheet("sheet_s3_shoulder_presets.png", "Series 3: the same shoulder on the other bodies (9 mm, port 25°; P1: 7 mm), each beside its body without one",
          "s3-ba: port 20°, no shoulder. P3 without a shoulder fails two checks at the low voicing; with it, it passes.",
          ["P0:s3-ba", "P0:s3-h9p25", "P1:s3-c0", "P1:s3-h7p25", "P2:s3-ba", "P2:s3-h9p25", "P3:s3-ba", "P3:s3-h9p25"],
          (OUT_ROWS[0], OUT_ROWS[2], OUT_ROWS[3]) + IN_ROWS[:1], None)
    draft = HERE / "sculpt" / "images"
    ref_draft = ("The owner's draft of 2026-11-24 (cone and flat tube on base A)",
                 ["A straight cone, 25.4 mm across at the body and 15.2 mm at the", "mouth end (57 mm out), level; the pipe (red in the last picture)",
                  "runs diagonally inside it, about 10° off its axis.", "A flat tube 18.7 x 11.3 mm around the voicing, to 8.5 mm past the lip."],
                 {"thumbface": draft / "draft_thumb.png", "end": draft / "draft_tail.png", "back34": draft / "draft_low34.png", "bodysection": draft / "draftneck_tail.png"})
    rows_t = (OUT_ROWS[0], OUT_ROWS[1], OUT_ROWS[2], OUT_ROWS[3], OUT_ROWS[4])
    sheet("sheet_s3_tandem_P4.png", "Series 3: the owner's cone neck on the plain body; the outside tilted against the pipe (P4-80, port 20°)",
          "The pipe, the window and the voicing hash are those of s3-r20p in every column: only the outside of the neck changes. "
          "s3-ba is the neck before the draft (42 mm foot, lopsided blend).",
          p4("s3-ba", "s3-t0", "s3-t4", "s3-t6", "s3-t10", "s3-t6b", "s3-t6l"), rows_t, ref_draft)
    sheet("sheet_s3_tandem_turn_P4.png", "Series 3: the cone neck turned sideways and moved, the pipe where it was (P4-80, port 20°, tilted 6°)",
          "Turned 3° toward the tail or the bulb, moved 2.5 mm, run on past the lip, and with a small shoulder of the chamber.",
          p4("s3-t6", "s3-t6yt", "s3-t6yb", "s3-t6o", "s3-t6h", "s3-t6s"), rows_t, ref_draft)
    sheet("sheet_s3_tandem_presets.png", "Series 3: the cone neck tilted 6° on the five bodies (port 20°)", "Same pipe and voicing as s3-r20p.",
          [f"{b}:s3-t6" for b in ("P4", "P1", "P0", "P2", "P3")], (OUT_ROWS[0], OUT_ROWS[2], OUT_ROWS[3]), None)
    rows_u = (OUT_ROWS[0], OUT_ROWS[2], OUT_ROWS[3], OUT_ROWS[4]) + IN_ROWS[:2]
    sheet("sheet_s3_uneven_P4.png", "Series 3: an uneven wall, thin on the deck and thick on the thumb face (P4-80, port 20°, cone neck tilted 6°)",
          "The chamber is the same in every column; the outside is drawn further from it on the thumb face and nearer on the deck. "
          "Each hole is sized again for the wall it has. Around the window the thick wall falls away as a dish.",
          p4("s3-u0", "s3-u1", "s3-u6", "s3-u7", "s3-u2", "s3-u3", "s3-u2n"), rows_u, None)
    sheet("sheet_s3_approaches_P4.png", "Series 3: the approaches side by side at this voicing height (P4-80, cone neck tilted 6°)",
          "Even wall; thick back only; thin deck only; 3 / 6 mm; that with a chamber shoulder; that with the low inner walls; the inner walls on the even wall.",
          p4("s3-u0", "s3-u4", "s3-u5", "s3-u6", "s3-u6s", "s3-u6w", "s3-t6w"), rows_u, None)
    sheet("sheet_s3_ramp_P4.png", "Series 3: the window in the 3 / 5 mm wall, no dish; the ramp run on as an oval scoop (P4-80, port 20°, cone neck tilted 6°)",
          "s3-u0: even wall. s3-v0: no hollow at all, the add-on's own window cut through the thicker wall. s3-v1 to v3: the extra wall rises from nothing "
          "to all of it inside an oval that begins on the line of the window's upper edge. s3-u1: the dish that was dropped.",
          p4("s3-u0", "s3-v0", "s3-v1", "s3-v3", "s3-v2", "s3-u1"), (OUT_ROWS[0], OUT_ROWS[2], OUT_ROWS[3], OUT_ROWS[4]), None)
    sheet("sheet_s3_candidates.png", "Series 3: the candidates (stance of the reference, lopsided blend, and the inside either way)",
          "A: the two low slab walls the owner chose. B: the ridge field to the tail. Left: P4, right: P1.",
          ["P4:s3-ba", "P4:s3-cA", "P4:s3-cB", "P1:s3-c0", "P1:s3-cA", "P1:s3-cB"], OUT_ROWS[:4] + IN_ROWS[:2], None)


if __name__ == "__main__":
    main()
