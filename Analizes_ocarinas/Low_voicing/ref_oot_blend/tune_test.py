"""Does the kernel see the owner's reference as in tune? (run after run_analysis.py and lip_scan.py)

    python Analizes_ocarinas/Low_voicing/ref_oot_blend/tune_test.py

The pipeline's own back-fit (output/ootb/report.md) fits the window so that the lowest note is exactly A4. That hides
the absolute pitch, and it uses the aperture of the dish (106 mm2) as the window. Here the window is the opening
measured by lip_scan.py (where the dish breaks through the chamber wall), the kernel's own window formula is used
(G_w = eta_w * A / (t + k * d_eq), eta_w 0.9), and nothing is fitted to a note:

  1. the pitch of every fingering at the size of the file;
  2. the scale factor at which the lowest note is A4, and what the instrument measures at that size;
  3. what is left of the 13-note scale when one common shift is taken out (the shape of the scale does not change
     with the size of the body: G grows with the length and V with its cube, so every note moves together).

The same three numbers are computed for the ECAN3 Ocarina of Time and Eclipse from their results.json, when those
files are there: two instruments their designer tuned and sells as playable. Writes tune_test.json and tune_test.md.
"""
from __future__ import annotations

import itertools
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "kernel"))
import ocarina_kernel as ok  # noqa: E402

NOTES = ["A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6", "D6", "E6", "F6"]
MIDI = [69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89]
C = ok.c_air(27.0) * 1000.0          # mm/s
ETA_W = 0.9
ASIAN = ["sub_L", "sub_R", "R_pinky", "R_ring", "R_middle", "R_index", "L_ring", "L_middle", "L_index", "L_thumb", "R_thumb", "L_pinky"]
ITALIAN = ASIAN[:10] + ["L_pinky", "R_thumb"]
OLD = ["sub_L", "sub_R", "R_pinky", "R_ring", "R_middle", "R_index", "L_pinky", "L_ring", "L_middle", "L_index", "L_thumb", "R_thumb"]


def cents(f, ref):
    return 1200.0 * math.log2(f / ref)


def scale_of(V0, Gw, holes, order, k):
    """Frequencies (Hz) of the 13 fingerings: all closed, then the holes opened one after another."""
    out, G, V = [], Gw, V0
    out.append(C / (2 * math.pi) * math.sqrt(G / V))
    for name in order:
        h = holes[name]
        G += h["A"] / (h["t"] + k * h["d_eq"])
        V -= h["A"] * h["t"]
        out.append(C / (2 * math.pi) * math.sqrt(G / V))
    return out


def shape_error(f):
    """The 13 notes against an equal-tempered A4..F6 moved as a whole: the common shift (cents) and what is left."""
    raw = [cents(x, ok.midi_f(m)) for x, m in zip(f, MIDI)]
    shift = sum(raw) / len(raw)
    left = [r - shift for r in raw]
    return shift, left, math.sqrt(sum(v * v for v in left) / len(left))


def study(title, V0, window, holes, k_values=(0.8, 0.66, 1.0)):
    res = dict(title=title, V0_cm3=V0 / 1000.0, by_k={}, free_window={})
    # any window at all: the conductance of the window that leaves the least, for each k (a test of the holes alone)
    for k in k_values:
        best = min(((shape_error(scale_of(V0, g, holes, ASIAN, k))[2], g) for g in [0.5 + 0.05 * i for i in range(600)]), key=lambda x: x[0])
        f = scale_of(V0, best[1], holes, ASIAN, k)
        shift, left, rms = shape_error(f)
        res["free_window"][f"{k:g}"] = dict(G_window_mm=best[1], left_over_rms_cents=rms, left_over_cents=dict(zip(NOTES, [round(v, 1) for v in left])),
                                            range_semitones=cents(f[-1], f[0]) / 100.0, scale_factor_for_A4=f[0] / 440.0 / 2 ** (0 / 12),
                                            lowest_note_hz=f[0], common_shift_cents=shift)
    if window is None:
        res["window"] = None
        return res
    A, t = window["A"], window["t"]
    d_eq = 2 * math.sqrt(A / math.pi)
    res["window"] = dict(area_mm2=A, t_mm=t, d_eq_mm=d_eq)
    for k in k_values:
        Gw = ETA_W * A / (t + k * d_eq)
        f = scale_of(V0, Gw, holes, ASIAN, k)
        shift, left, rms = shape_error(f)
        s_a4 = f[0] / 440.0                                       # the body scaled by this factor sounds A4 with all holes closed
        best = min(((shape_error(scale_of(V0, Gw, holes, ASIAN[:6] + list(p), k))[2], p) for p in itertools.permutations(ASIAN[6:])),
                   key=lambda x: x[0])
        res["by_k"][f"{k:g}"] = dict(
            G_window_mm=Gw, lowest_note_hz=f[0], lowest_note_cents_from_A4=cents(f[0], 440.0), top_note_hz=f[-1],
            range_semitones=cents(f[-1], f[0]) / 100.0, scale_factor_for_A4=s_a4, V0_at_that_scale_cm3=V0 * s_a4 ** 3 / 1000.0,
            common_shift_cents=shift, left_over_cents=dict(zip(NOTES, [round(v, 1) for v in left])), left_over_rms_cents=rms,
            italian_rms=shape_error(scale_of(V0, Gw, holes, ITALIAN, k))[2], old_order_rms=shape_error(scale_of(V0, Gw, holes, OLD, k))[2],
            best_of_720_rms=best[0], best_order_upper_six=list(best[1]))
    return res


def from_results(path, window=None):
    r = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    holes = {n: dict(A=h["A"], t=h["t"], d_eq=h["d_eq"]) for n, h in r["holes"].items()}
    w = r["window"]
    win = window or dict(A=w.get("A_outer_mm2"), t=w.get("t"))
    return r["volumes"]["V0_air_capped_at_outer_rims_mm3"], win, holes, r


def main():
    out = {}
    V0, _, holes, r = from_results(HERE / "output" / "ootb" / "results.json")
    scan = [s for s in json.loads((HERE / "lip_scan.json").read_text(encoding="utf-8")) if s["open"]]
    width = len(scan) * 1.0                                         # the cuts are 1 mm apart
    length = max(s["opening_mm"] for s in scan)
    area = sum(s["opening_mm"] for s in scan) * 1.0                 # the opening, cut by cut
    win = dict(A=area, t=r["window"]["t"], width_mm=width, length_mm=length)
    out["reference_window_as_measured"] = study("Owner's reference, window = the opening in the chamber wall", V0, win, holes)
    out["reference_window_as_measured"]["window"].update(width_mm=width, length_mm=length)
    out["reference_dish_aperture"] = study("Owner's reference, window = the aperture of the dish (the pipeline's reading)", V0,
                                           dict(A=r["window"]["A_outer_mm2"], t=r["window"]["t"]), holes)
    for name in ("oot", "eclipse"):
        p = ROOT / "Analizes_ocarinas" / "ECAN3_experimental" / "output" / name / "results.json"
        if not p.exists():
            continue
        V, w, h, rr = from_results(p)
        out[f"ecan3_{name}"] = study(f"ECAN3 {name} (tuned by its designer)", V, w if w.get("A") and w.get("t") else None, h)
    (HERE / "tune_test.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    md = ["# The kernel on the owner's low-voicing reference (generated by tune_test.py)", "",
          "Nothing is fitted to a note. Window conductance by the kernel's formula (eta_w 0.9). *Common shift*: how far the "
          "whole scale lies from A4..F6 at the size of the file. *Left over*: the 13 notes after that one shift is taken out; "
          "this does not change when the body is scaled. Order of opening: the Asian system.", "",
          "| Instrument | k | Air cm³ | Window mm² | Lowest note at file size | Range, semitones (a 13-note scale: 20) | Scale factor for A4 | Air at that size cm³ | "
          "Left over, rms cents | Worst notes | Best of the 720 orders, rms |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for key, s in out.items():
        for k, b in s["by_k"].items():
            lo = b["left_over_cents"]
            worst = sorted(lo.items(), key=lambda kv: -abs(kv[1]))[:3]
            md.append(f"| {s['title']} | {k} | {s['V0_cm3']:.1f} | {s['window']['area_mm2']:.0f} | {b['lowest_note_hz']:.0f} Hz "
                      f"({b['lowest_note_cents_from_A4']:+.0f} cents from A4) | {b['range_semitones']:.1f} | {b['scale_factor_for_A4']:.2f} | "
                      f"{b['V0_at_that_scale_cm3']:.0f} | {b['left_over_rms_cents']:.0f} | "
                      + ", ".join(f"{n} {v:+.0f}" for n, v in worst) + f" | {b['best_of_720_rms']:.0f} |")
    md += ["", "## With any window at all", "",
           "The window's conductance is set free and chosen to leave the least. What is left is then a property of the holes "
           "alone: their sizes against each other and against the chamber.", "",
           "| Instrument | k | Best window conductance mm | Range, semitones | Left over, rms cents | Worst notes |", "| --- | --- | --- | --- | --- | --- |"]
    for key, s in out.items():
        if key == "reference_dish_aperture":
            continue
        for k, b in s["free_window"].items():
            worst = sorted(b["left_over_cents"].items(), key=lambda kv: -abs(kv[1]))[:3]
            md.append(f"| {s['title']} | {k} | {b['G_window_mm']:.2f} | {b['range_semitones']:.1f} | {b['left_over_rms_cents']:.0f} | "
                      + ", ".join(f"{n} {v:+.0f}" for n, v in worst) + " |")
    (HERE / "tune_test.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
