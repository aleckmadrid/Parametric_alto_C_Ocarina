"""The kernel against three made instruments, and four desk estimates for the voicing decisions of 2026-11-17.

    python Analizes_ocarinas/Kernel_challenge/kernel_vs_references.py

Part 0  The order in which the holes open: the params file as it was until 2026-11-18 against the Asian system
        (the params file since then) and the Italian system.
Part 1  Hole by hole. The measured holes of the Miracle, the Spencer and the Songbird Alto C are put into the
        kernel's own scale model (kernel/holes.py). For each instrument the capped air volume is fitted so that the
        13 notes are as close to pitch as they can be with A4 exact; the table shows what is left over per note and
        how each measured hole compares with the hole the kernel would cut at that volume.
Part 2  The same holes at the volumes the other evidence gives (Spencer 70 cm3, Songbird 100 cm3).
Part 3  The window throat. How much A4 moves when the effective depth of the throat changes, and a duct estimate
        of that depth for the plain prism, the fan cut and the two ellipse cuts from the volumes the cuts remove.
Part 4  The lowered windway: where the exit and the mouth end go, for the angles that were tried.
Part 5  The windway as a slot: viscous pressure loss against the jet's dynamic pressure, for the kernel's slot
        and for the slots of the references.

Every reference diameter is a photo measurement (+-0.3 mm on the Miracle, +-15 % on the ceramic rims). Read the
patterns, not the single numbers. Writes kernel_vs_references.md. Standard library only.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "kernel"))
import holes as kh            # noqa: E402
import ocarina_kernel as ok   # noqa: E402

MM = 1e-3
MIDI = [69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89]
NOTES = ["A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6", "D6", "E6", "F6"]
F = [ok.midi_f(m) for m in MIDI]
C = ok.c_air(27.0)
KK = ok.TWO_PI ** 2 / (C * C)
LOW = ["sub_L", "sub_R", "R_pinky", "R_ring", "R_middle", "R_index"]            # B4 .. G5: the same in every chart
# The order in which the six upper holes open (A5 .. F6).
ORDER_REPO = LOW + ["L_pinky", "L_ring", "L_middle", "L_index", "L_thumb", "R_thumb"]      # params [fingering] until 2026-11-18
ORDER_ASIAN = LOW + ["L_ring", "L_middle", "L_index", "L_thumb", "R_thumb", "L_pinky"]     # Pure Ocarinas, Asian system; params since 2026-11-18
ORDER_ITALIAN = LOW + ["L_ring", "L_middle", "L_index", "L_thumb", "L_pinky", "R_thumb"]   # Italian: E on the pinky
ORDER = ORDER_ASIAN
KERNEL_NAME = {"sub_L": "sub1", "sub_R": "sub2"}


def references():
    sp = json.load(open(ROOT / "Analizes_ocarinas" / "Spencer_OoT_12h" / "measure_output.json"))["hole_sizes_mean_mm"]
    sb = json.load(open(ROOT / "Analizes_ocarinas" / "Songbird_OoT_12h" / "measure_output.json"))
    L0 = sb["length_mm"]
    FING = [n for n in ORDER if "thumb" not in n]
    sbh = {n: sb["holes"][n]["d_rim_major"] for n in FING}
    th = sb["thumb_face"]["feats"]
    sbh["L_thumb"] = th["L_thumb"]["size_frac"] * L0
    sbh["R_thumb"] = th["R_thumb"]["size_frac"] * L0
    sph = {n: sp[n] for n in FING}
    sph["L_thumb"] = sph["R_thumb"] = 12.0
    # Miracle_M.md section 4.2. Its subholes are both on the right hand; the order of opening is what matters
    # here. Dark-opening diameters, so no rim allowance. The thumb hole at the bulb end (9.7 mm) is the left
    # thumb's, the one at the centre (10.6 mm) the right thumb's.
    mir = {"sub_L": 3.5, "sub_R": 2.6, "R_pinky": 5.8, "R_ring": 6.1, "R_middle": 5.2, "R_index": 6.4,
           "L_pinky": 4.5, "L_ring": 6.8, "L_middle": 6.1, "L_index": 7.1, "L_thumb": 9.7, "R_thumb": 10.6}
    return [
        ("Miracle AO10-AC (photo, dark openings)", mir, 0.0, 4.0, "65–75 cm³ (Miracle_M.md §6.4)"),
        ("Spencer OoT alto C (photo rims − 1 mm, thumbs 12 mm)", sph, -1.0, 5.0, "about 70 cm³ (65–80)"),
        ("Songbird OoT Alto C at 170 mm (photo rims − 1 mm)", sbh, -1.0, 5.0, "92–116 cm³ at 170 mm; 77 cm³ or more at any allowed length"),
    ]


def scale_cents(v0_cm3, d_mm, t_mm, k):
    v0 = v0_cm3 * 1e-6
    xw = KK * F[0] ** 2 * v0                      # A4 exact
    f = kh.predict_scale(xw, v0, [d * MM for d in d_mm], [t_mm * MM] * 12, k, C)
    return [ok.cents(a, b) for a, b in zip(f, F)]


def fit_v0(d_mm, t_mm, k, step=0.25):
    best = None
    v = 30.0
    while v <= 260.0:
        try:
            e = scale_cents(v, d_mm, t_mm, k)
        except (ValueError, ZeroDivisionError):
            v += step
            continue
        s = sum(x * x for x in e)
        if best is None or s < best[0]:
            best = (s, v, e)
        v += step
    return best[1], best[2]


def rms12(e):
    return math.sqrt(sum(x * x for x in e[1:]) / 12)


def part0(md):
    import itertools
    md += ["## 0. Which hole opens for which note", "",
           "The kernel sizes each hole for the note it opens, so the order of opening decides which finger gets which "
           "diameter. Until 2026-11-18 `params/alto_c_12hole.toml` opened the left hand pinky first (A5) and the thumbs last "
           "(E6, F6); the owner then chose the Asian system, and the parameter file follows it. "
           "The Asian fingering system, the common one on 12-hole instruments, opens L ring, L middle, L index, then the left "
           "thumb (D6), the right thumb (E6) and the left pinky last (F6); the Italian system swaps the last two "
           "(Pure Ocarinas, *The ocarina's fingering system* and *Learning the ocarina's fingerings*). "
           "The low six holes open in the same order in all three.", "",
           "Each instrument's measured holes were put into the kernel's scale model under each order (A4 exact, volume fitted, "
           "k_hole 1.0). *Rank* is the place of that order among all 720 ways of opening the six upper holes.", "",
           "| Instrument | Order of the params file until 2026-11-18: rms cents, rank | Asian (the params file now): rms cents, rank | Italian: rms cents, rank | Best of the 720, rms cents |",
           "| --- | --- | --- | --- | --- |"]
    upper = ORDER_REPO[6:]
    for name, holes, off, wall, _ in references():
        res = []
        for p in itertools.permutations(upper):
            d = [holes[n] + off for n in LOW + list(p)]
            _, e = fit_v0(d, wall, 1.0, step=1.0)
            res.append((rms12(e), p))
        res.sort()
        cells = []
        for o in (ORDER_REPO, ORDER_ASIAN, ORDER_ITALIAN):
            r = next(i for i, x in enumerate(res) if list(x[1]) == o[6:])
            cells.append(f"{res[r][0]:.0f}, {r + 1}")
        md.append(f"| {name.split(' (')[0]} | " + " | ".join(cells) + f" | {res[0][0]:.0f} |")
    md += ["", "What the kernel cuts under each order (4 mm wall, η_w 0.90; print = k_hole 0.8, nominal = k_hole 1.0), and the "
           "edge gap between the left subhole and L ring at the 9.5 mm slide (limit 3.4 mm, notes open problem 19):", "",
           "| V0 cm³ | Order | L pinky | L ring | L middle | L index | L thumb | R thumb | Over the pad limit (10 mm fingers, 12 mm thumbs) | Edge gap sub L – L ring, print / nominal |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    import copy
    import config
    import sizing
    P = config.load_params()
    notes = P["design"]["notes"][1:]
    by = {h["name"]: h for h in P["fingering"]["holes"]}
    for v0 in (65.0, 80.0, 95.0):
        for lab, order in (("until 2026-11-18", ORDER_REPO), ("Asian (now)", ORDER_ASIAN)):
            Q = copy.deepcopy(P)
            Q["fingering"]["holes"] = [dict(by[KERNEL_NAME.get(n, n)], opens=notes[i]) for i, n in enumerate(order)]
            b = sizing.size_body(v0, params=Q)
            pr = {h.name: h.d_mm for h in b.holes.solutions["print"]}
            no = {h.name: h.d_mm for h in b.holes.solutions["nominal"]}
            over = [n for n, x in no.items() if x > (12.0 if "thumb" in n else 10.0)]
            gap = [9.5 - (dd["L_ring"] + dd["sub1"]) / 2.0 for dd in (pr, no)]
            md.append(f"| {v0:.0f} | {lab} | " + " | ".join(f"{pr[n]:.1f} / {no[n]:.1f}" for n in upper) +
                      f" | {', '.join(over) if over else 'none'} (nominal) | {gap[0]:.2f} / {gap[1]:.2f} mm |")
    md.append("")


def kernel_holes(v0_cm3, t_mm, k):
    v0 = v0_cm3 * 1e-6
    xw = KK * F[0] ** 2 * v0
    ds, _ = kh.solve_scale(F, xw, v0, [t_mm * MM] * 12, k, C)
    return [d / MM for d in ds]


def part1(md):
    md += ["## 1. Hole by hole: three made instruments in the kernel's scale model", "",
           "For each instrument: the capped air volume that brings its 13 notes closest to pitch (A4 exact, least squares "
           "over the other twelve), the error that is left on each note, and each measured hole against the hole the kernel "
           "would cut at that volume and wall, **in the Asian order of section 0**. k_hole = 1.0 (the kernel's prior). "
           "A ratio under 1 means the maker's hole is smaller than the kernel's.", ""]
    summary = []
    for name, holes, off, wall, other in references():
        d = [holes[n] + off for n in ORDER]
        v, e = fit_v0(d, wall, 1.0)
        dk = kernel_holes(v, wall, 1.0)
        md += [f"### {name}", "",
               f"Wall at the holes taken as {wall:.0f} mm. Best-fit volume **{v:.0f} cm³**; the other evidence gives {other}. "
               f"Left over: rms {math.sqrt(sum(x * x for x in e[1:]) / 12):.0f} cents, from {min(e):+.0f} to {max(e):+.0f}.", "",
               "| Opens | Hole | Measured Ø mm | Kernel Ø mm | Measured / kernel | Note error with the measured holes, cents |",
               "| --- | --- | --- | --- | --- | --- |"]
        ratios = []
        for i, n in enumerate(ORDER):
            r = d[i] / dk[i]
            ratios.append(r)
            md.append(f"| {NOTES[i + 1]} | {n} | {d[i]:.1f} | {dk[i]:.1f} | {r:.2f} | {e[i + 1]:+.0f} |")
        low = sum(ratios[2:6]) / 4.0          # right hand, D5..G5
        top = sum(ratios[6:9]) / 3.0          # L ring, L middle, L index: A5..C6
        thumbs = sum(ratios[9:11]) / 2.0      # D6, E6
        fing = [i for i, n in enumerate(ORDER) if "thumb" not in n]
        thum = [i for i, n in enumerate(ORDER) if "thumb" in n]
        summary.append((name.split(" (")[0], v, sum(ratios[:2]) / 2.0, low, top, thumbs, ratios[11],
                        max(d[i] for i in fing), max(d[i] for i in thum), max(dk[i] for i in fing), max(dk[i] for i in thum)))
        md.append("")
    md += ["### The pattern across the three", "",
           "| Instrument | Fitted V0 cm³ | Subholes, measured / kernel | Right hand (D5–G5) | Left ring, middle, index (A5–C6) | Thumbs (D6, E6) | L pinky (F6) | Largest finger hole, measured / kernel mm | Largest thumb hole, measured / kernel mm |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in summary:
        md.append(f"| {s[0]} | {s[1]:.0f} | {s[2]:.2f} | {s[3]:.2f} | {s[4]:.2f} | {s[5]:.2f} | {s[6]:.2f} | {s[7]:.1f} / {s[9]:.1f} | {s[8]:.1f} / {s[10]:.1f} |")
    md.append("")
    return summary


def part2(md):
    md += ["## 2. The same holes at the volume the other evidence gives", "",
           "Here the volume is not fitted. A4 is exact; the table shows where each later note lands with the measured holes "
           "in the passive model. A note that reads flat here is a note the maker reaches with less hole than the model "
           "asks for: by blowing harder up the scale, by an undercut, or by where the hole sits.", "",
           "| Instrument | V0 cm³ | Wall mm | k_hole | D5 | G5 | A5 | D6 | E6 | F6 |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    cases = [(0, 70.0), (1, 70.0), (2, 100.0), (2, 85.0)]
    refs = references()
    for idx, v in cases:
        name, holes, off, wall, _ = refs[idx]
        d = [holes[n] + off for n in ORDER]
        for k in (0.8, 1.0):
            e = scale_cents(v, d, wall, k)
            md.append(f"| {name.split(' (')[0]} | {v:.0f} | {wall:.0f} | {k:.1f} | " + " | ".join(f"{e[NOTES.index(n)]:+.0f}" for n in ("D5", "G5", "A5", "D6", "E6", "F6")) + " |")
    md.append("")


def part3(md):
    A = 62.84e-6                                    # the 80 cm3 window of the kernel, 4 mm wall
    deq = ok.d_eq(A)
    k = 0.80
    g0 = A / (4.0 * MM + k * deq)
    md += ["## 3. The window throat: what a cut is worth", "",
           f"The kernel takes the window as a prism through the wall: G_w = A / (t + k·d_eq), with t the wall at the window. "
           f"For the 80 cm³ window (A = 62.84 mm², d_eq = {deq / MM:.2f} mm, k = 0.80) the wall of 4 mm is {4.0 / (4.0 + k * deq / MM) * 100:.0f} % of the effective length.", "",
           "| Effective throat depth t, mm | G_w, mm | Against t = 4 mm | A4 moves by, cents (same window, same volume) | Volume the same window tunes to A4, cm³ |",
           "| --- | --- | --- | --- | --- |"]
    for t in (2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0):
        g = A / (t * MM + k * deq)
        md.append(f"| {t:.1f} | {g / MM:.2f} | {(g / g0 - 1) * 100:+.1f} % | {1200 * math.log2(math.sqrt(g / g0)):+.0f} | {80.0 * g / g0:.0f} |")
    md += ["", "A cut that opens the throat acts like a shorter throat. A duct estimate, from the volume each cut removes "
           "(notes, open problem 24; all on the 80 cm³ window through a 4 mm wall): take the area as growing evenly from the "
           "window outline to the outer face, so that the mean area is volume / 4 mm, and integrate the resistance of that duct. "
           "It treats the whole removed volume as duct, which the ramp side is not, so it overstates the effect; the "
           "differences between the cuts are the point.", "",
           "| Cut | Volume removed, mm³ | Mean area / window area | Duct-equivalent depth t, mm | G_w against the plain prism | A4 against the fan cut, cents |",
           "| --- | --- | --- | --- | --- | --- |"]
    rows = []
    for label, vol in (("Plain prism (the kernel's model)", 251.0), ("Fan (default; the Stage 1 stubs)", 548.0),
                       ("Ellipse P1 (+4 mm, shelf 50°)", 474.0), ("Ellipse P3 (+3 mm, shelf 40°)", 458.0)):
        a0 = 62.84
        mean = vol / 4.0
        a1 = 2.0 * mean - a0
        teq = 4.0 if a1 <= a0 * 1.0001 else 4.0 * a0 * math.log(a1 / a0) / (a1 - a0)
        g = A / (teq * MM + k * deq)
        rows.append((label, vol, mean / a0, teq, g))
    gfan = rows[1][4]
    for label, vol, m, teq, g in rows:
        md.append(f"| {label} | {vol:.0f} | {m:.2f} | {teq:.2f} | {(g / g0 - 1) * 100:+.0f} % | {1200 * math.log2(math.sqrt(g / gfan)):+.0f} |")
    md.append("")


def part4(md):
    W, Lw = 9.65, 30.0
    md += ["## 4. The lowered windway", "",
           "The windway turns about the lip edge. With the window 9.65 mm long and the windway 30 mm long:", "",
           "| Lowered by | Exit moves toward the chamber, mm | Mouth end moves, mm | Jet meets the flat under the lip at |",
           "| --- | --- | --- | --- |"]
    for a in (1.0, 2.5, 2.7, 4.0, 10.6):
        t = math.tan(math.radians(a))
        md.append(f"| {a:.1f}° | {W * t:.2f} | {(W + Lw) * t:.2f} | {a:.1f}° from below |")
    md += ["", "10.6° is the angle of the owner's sample (Window_cutout.md §10.1), which has a 5.5 mm wall and a flat face inside.", ""]


def part5(md):
    mu, rho = 1.85e-5, 1.18
    md += ["## 5. The windway as a slot", "",
           "Laminar loss in a slot whose height tapers evenly: Δp = 6 μ L q (h₁ + h₂) / (h₁² h₂²), with q the flow per unit width "
           "(jet speed × exit height). Entrance losses are left out, so the real loss is higher. The mouth pressure a "
           "manometer reads is the jet's dynamic pressure plus this loss.", "",
           "| Slot | Length mm | Height, mouth → exit, mm | Loss at a 15 m/s jet (135 Pa) | Loss at a 25 m/s jet (370 Pa) |", "| --- | --- | --- | --- | --- |"]
    for label, L, h1, h2 in (("Kernel rule (taper 1.3)", 30.0, 1.56, 1.20), ("Owner's sample wind cut (tapered part)", 23.0, 3.0, 1.3),
                             ("Miracle (entrance 2.5–3 mm; exit assumed 1.2)", 31.0, 2.75, 1.2),
                             ("Kernel exit with a 3 mm mouth end", 30.0, 3.0, 1.2), ("Kernel rule at 45 mm", 45.0, 1.56, 1.20)):
        cells = []
        for u in (15.0, 25.0):
            q = u * h2 * MM
            dp = 6.0 * mu * (L * MM) * q * (h1 + h2) * MM / ((h1 * MM) ** 2 * (h2 * MM) ** 2)
            dyn = 0.5 * rho * u * u
            cells.append(f"{dp:.0f} Pa ({dp / dyn * 100:.0f} % of the jet's)")
        md.append(f"| {label} | {L:.0f} | {h1:.2f} → {h2:.2f} | {cells[0]} | {cells[1]} |")
    md.append("")


def main():
    md = ["# The kernel against made instruments, and estimates for the voicing decisions (generated by kernel_vs_references.py)", "",
          "Desk numbers. Nothing here was printed or played. The reference holes are photo measurements; the estimates of "
          "sections 3 and 5 are textbook duct formulas, not models of a jet.", ""]
    part0(md)
    part1(md)
    part2(md)
    part3(md)
    part4(md)
    part5(md)
    out = HERE / "kernel_vs_references.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
