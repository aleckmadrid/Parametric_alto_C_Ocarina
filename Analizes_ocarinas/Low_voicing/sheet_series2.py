"""Sheet of series 2 of the low-voicing trials (handover of 2026-11-19, section 5). Needs Pillow.

    python Analizes_ocarinas/Low_voicing/sheet_series2.py

Writes sheet_series2.png next to this file: the finer bracket around 10 deg (15, 10, 5) and the three changes of look the
owner's Spencer pictures ask for (a longer mouthpiece, a wider dish, a fat round foot of the neck), with the owner's
Spencer pictures in the left column. It uses the layout of sheet_low_voicing.py.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sheet_low_voicing as slv  # noqa: E402

PHOTOS = HERE / "reference_photos"


def head(key):
    """A column title short enough for the column: the composite (pipe 45, dish 8, foot 29 deep) is named once in the
    lines at the top of the sheet."""
    r = slv.T[key]
    o, p = r["overrides"], r.get("param_overrides", {})
    long_pipe = bool(p.get("voicing_rules.windway_length_mm"))
    if long_pipe and o.get("cone_widen_mm") and o.get("neck_base_depth_mm"):
        more = ["composite"] + (["round tip"] if o.get("neck_floor_mm") else [])
    else:
        more = (["pipe 45"] if long_pipe else []) + (["dish 8"] if o.get("cone_widen_mm") else []) \
            + (["foot 29 deep"] if o.get("neck_base_depth_mm") else [])
    body = "" if r["preset"] == "P4" else f"{r['preset']} "
    return f"{body}{r['trial']}: {o['port_angle_deg']:g}°" + (", " + ", ".join(more) if more else "")


ROWS = (("thumbface", "Straight at the thumb face (the player is at the top of the picture)"),
        ("std:voicing", "The window seen straight in (the jet runs left to right): the dish"),
        ("back34", "From below and beyond, the tail toward the camera"),
        ("end", "Along the body: the player is on the left, the deck is up"),
        ("bodysection", "The same view, cut through the lip (red cross); the air is blue; grid 10 mm"),
        ("player", "From the player"),
        ("section", "Close section through the window: the jet runs left to right, outside is up"))


def main():
    slv.head = head
    keys = (slv.have("P4", ("lv-15f", "lv-10f", "lv-5f", "lv-5fw", "lv-10fd", "lv-10fn", "lv-10fwdn", "lv-10fwdnr"))
            + slv.have("P1", ("lv-10fwdn", "lv-10fwdnr")))
    slv.sheet("sheet_series2.png", "Series 2: the low voicing against the owner's Spencer pictures (P4-80, the seed; last column P1-80)",
              ["Port angle 15, 10, 5° (window 29, 31, 35 % of the width inside the player-side edge; the Spencer reads 30 to 33 %). "
               "Foot of the neck 29 mm on P4, 34 mm on P1.",
               "pipe 45 = a 45 mm windway (rule 30 mm, a new voicing hash); dish 8 = the cut opens 8 mm beyond the window on each side, across the jet "
               "(rule 3 mm, hashed); neck 29 deep = the neck's foot 29 mm deep (rule 24.5 mm, not hashed); "
               "round tip = the mouth end 13.8 mm deep as it is wide (rule 7.6 mm, not hashed; the pipe does not move). "
               "composite = pipe 45, dish 8 and foot 29 deep together.",
               slv.RULE + " " + slv.FIT],
              keys, ROWS,
              refs={"thumbface": [(PHOTOS / "spencer_02_thumb_face.png", "reference_photos/spencer_02_thumb_face.png")],
                    "end": [(PHOTOS / "spencer_01_greenware_tray.png", "reference_photos/spencer_01_greenware_tray.png")]},
              ref_heads=("Spencer (owner's photos)",))


if __name__ == "__main__":
    main()
