"""Photo measurement and Helmholtz back-fit for the Miracle AO10-AC (12-hole alto C).

Reads the product photos in ./images, measures the dark openings (finger holes,
thumb holes, window) in pixels, converts them to mm with the catalogue size
(150 mm long, 95 mm tall including the mouthpiece), then fits chamber volume
and effective window conductance with the repo kernel.

    python Analizes_ocarinas/Miracle_M/measure_miracle_m.py

Needs Pillow and numpy (the kernel itself is standard library).
"""
from __future__ import annotations

import math
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "kernel"))
import ocarina_kernel as ok  # noqa: E402

IMG_TOP = HERE / "images" / "04_top_face_front_view.jpg"
IMG_BACK = HERE / "images" / "06_back_face_front_view.jpg"
LENGTH_MM, HEIGHT_MM = 150.0, 95.0          # catalogue, "approx."
BODY_THR = 235                              # grey level: below = instrument
HOLE_THR = (90, 125)                        # dark core / half-max edge


def load(p):
    return np.asarray(Image.open(p).convert("L")).astype(int)


def components(mask, min_px=30):
    H, W = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not seen[y, x]:
                q = deque([(y, x)]); seen[y, x] = True; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True; q.append((ny, nx))
                if len(pts) >= min_px:
                    out.append(np.array(pts))
    return out


def body_bbox(im):
    ys, xs = np.nonzero(im < BODY_THR)
    return xs.min(), xs.max(), ys.min(), ys.max()


def holes(im, thr):
    res = []
    for p in components(im < thr):
        y0, x0 = p.min(0); y1, x1 = p.max(0)
        res.append(dict(cx=p[:, 1].mean(), cy=p[:, 0].mean(), w=x1 - x0 + 1, h=y1 - y0 + 1,
                        area=len(p), pts=p))
    return sorted(res, key=lambda r: r["cx"])


def match(a, b, tol=6):
    """Pair components found at the two thresholds by centroid."""
    for r in a:
        r["edge"] = min(b, key=lambda s: math.hypot(s["cx"] - r["cx"], s["cy"] - r["cy"]))
        assert math.hypot(r["edge"]["cx"] - r["cx"], r["edge"]["cy"] - r["cy"]) < tol
    return a


def main():
    top, back = load(IMG_TOP), load(IMG_BACK)
    bt, bb = body_bbox(top), body_bbox(back)
    Lpx = ((bt[1] - bt[0]) + (bb[1] - bb[0])) / 2
    Hpx = ((bt[3] - bt[2]) + (bb[3] - bb[2])) / 2
    s_len, s_h = LENGTH_MM / Lpx, HEIGHT_MM / Hpx
    s = (s_len + s_h) / 2
    print(f"top bbox {bt}, back bbox {bb}")
    print(f"scale from length {s_len:.4f} mm/px, from height {s_h:.4f} mm/px -> using {s:.4f} "
          f"(spread {100*(s_len-s_h)/s:.1f} %)")

    # ---- holes, top face (player's view: mouthpiece toward the player) ----
    print("\n## Top face (x from bulb end, y from top edge, mm)")
    T = match(holes(top, HOLE_THR[0]), holes(top, HOLE_THR[1]))
    x0, y0 = bt[0], bt[2]
    rows = []
    for i, r in enumerate(T):
        e = r["edge"]
        d_core = 2 * math.sqrt(r["area"] / math.pi) * s
        d_edge = 2 * math.sqrt(e["area"] / math.pi) * s
        d_maxwh = max(e["w"], e["h"]) * s
        rows.append((i, (r["cx"] - x0) * s, (r["cy"] - y0) * s, d_core, d_edge, d_maxwh, e["w"], e["h"]))
        print(f"T{i}: x {rows[-1][1]:6.1f}  y {rows[-1][2]:5.1f}  d_core {d_core:4.2f}  "
              f"d_edge {d_edge:4.2f}  max(w,h) {d_maxwh:4.2f}  px {e['w']}x{e['h']}")

    # ---- back face, mirrored into the top-view frame ----
    print("\n## Back face mirrored into top-view frame (mm)")
    B = match(holes(back, HOLE_THR[0]), holes(back, HOLE_THR[1]))
    bx1, by0 = bb[1], bb[2]
    for i, r in enumerate(B):
        e = r["edge"]
        d_edge = 2 * math.sqrt(e["area"] / math.pi) * s
        print(f"B{i}: x {(bx1 - r['cx'])*s:6.1f}  y {(r['cy']-by0)*s:5.1f}  "
              f"d_core {2*math.sqrt(r['area']/math.pi)*s:4.2f}  d_edge {d_edge:4.2f}  "
              f"w {e['w']*s:4.2f} h {e['h']*s:4.2f}  area_edge {e['area']*s*s:5.1f} mm2")

    # window = the non-round component (aspect > 1.3)
    win = max(B, key=lambda r: r["edge"]["h"] / r["edge"]["w"])["edge"]
    p = win["pts"]
    ys = np.arange(p[:, 0].min(), p[:, 0].max() + 1)
    widths = np.array([np.count_nonzero(p[:, 0] == y) for y in ys]) * s
    n = len(ys)
    print(f"\nwindow length {n*s:.2f} mm, max width {widths.max():.2f} mm at "
          f"{100*np.argmax(widths)/n:.0f} % from the top, width at 15 % {widths[int(.15*n)]:.2f}, "
          f"at 85 % {widths[int(.85*n)]:.2f}, area {win['area']*s*s:.1f} mm2")
    print(f"window top (narrow end) {(p[:,0].min()-by0)*s:.1f} mm below top edge; "
          f"bottom (wide end) {(p[:,0].max()-by0)*s:.1f} mm; mouthpiece end at {(bb[3]-by0)*s:.1f} mm")
    print(f"=> mouthpiece end to wide end of window {(bb[3]-p[:,0].max())*s:.1f} mm (windway length upper bound)")

    # silhouette area of the body above the mouthpiece
    sil = top < BODY_THR
    print(f"\nsilhouette area (top view, whole) {sil.sum()*s*s/100:.1f} cm2")

    round_back = sorted([r for r in B if r["edge"] is not win], key=lambda r: bx1 - r["cx"])
    thumb_bulb, thumb_center = (max(r["edge"]["w"], r["edge"]["h"]) * s for r in round_back)
    win_area = win["area"] * s * s
    fit(rows, thumb_center, thumb_bulb)
    ideal(rows, thumb_center, thumb_bulb, win_area)


# ------------------------------------------------------------------------
# Helmholtz back-fit
# ------------------------------------------------------------------------
NOTES = ["A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6", "D6", "E6", "F6"]
MIDI = [69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89]


def fit_design(d_mm, t_mm, k=0.80, T_c=27.0):
    """Linear LSQ for V0 and G_w_eff given the opening order d_mm (12 holes)."""
    c = ok.c_air(T_c)
    A = [math.pi * (d * 1e-3) ** 2 / 4 for d in d_mm]
    G = [ok.conductance(a, t_mm * 1e-3, k) for a in A]
    rows, rhs, w = [], [], []
    for j, m in enumerate(MIDI):
        f = ok.midi_f(m)
        a = (ok.TWO_PI * f / c) ** 2
        chim = sum(A[i] * t_mm * 1e-3 for i in range(j))
        rows.append((a, -1.0)); rhs.append(sum(G[:j]) + a * chim)
        w.append(1.0)
    X = np.array(rows); y = np.array(rhs)
    for _ in range(5):                                  # reweight -> relative (cents-like) error
        W = np.diag(w)
        V0, Gw = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
        w = [1.0 / (r[0] * V0) ** 2 for r in rows]
    des = ok.Design(c=c, G_w_eff=Gw, V0=V0, k=k,
                    holes=[ok.Hole(name=f"h{i}", t=t_mm * 1e-3, d=d * 1e-3) for i, d in enumerate(d_mm)])
    res = [ok.cents(des.predict(range(j)), ok.midi_f(m)) for j, m in enumerate(MIDI)]
    return V0, Gw, res, G


def top_diams(rows):
    """Best estimate = major axis: a tilted circle images as an ellipse whose long axis is the
    true diameter (the area-equivalent value under-reads by sqrt(cos tilt))."""
    return {r[0]: r[5] for r in rows}


# opening order A4 -> F6 for the "bulb = left hand" reading (T = top-face index, see printout)
ORDER_LEFT_BULB = ["T4", "T6", "T9", "T8", "T7", "T5", "T0", "T1", "T2", "T3", "Bc", "Bb"]
FINGER = ["sub 1", "sub 2", "R pinky", "R ring", "R middle", "R index",
          "L pinky", "L ring", "L middle", "L index", "thumb (centre)", "thumb (bulb)"]


def fit(rows, thumb_center, thumb_bulb):
    d = top_diams(rows)
    maps = {
        "bulb = left hand": [d[4], d[6], d[9], d[8], d[7], d[5], d[0], d[1], d[2], d[3], thumb_center, thumb_bulb],
        "bulb = left hand, thumbs swapped": [d[4], d[6], d[9], d[8], d[7], d[5], d[0], d[1], d[2], d[3], thumb_bulb, thumb_center],
        "bulb = right hand": [d[4], d[6], d[0], d[1], d[2], d[5], d[9], d[8], d[7], d[3], thumb_bulb, thumb_center],
    }
    print("\n## Helmholtz back-fit (k = 0.80, 27 C)")
    for name, dm in maps.items():
        for t in (2.5, 3.0, 3.5):
            V0, Gw, res, G = fit_design(dm, t)
            rms = math.sqrt(sum(r * r for r in res) / len(res))
            print(f"{name:34s} t {t} mm: V0 {V0*1e6:5.1f} cm3  Gw_eff {Gw*1e3:5.2f} mm  "
                  f"rms {rms:5.1f} c  max {max(res, key=abs):+6.1f} c")
    best = maps["bulb = left hand"]
    V0, Gw, res, G = fit_design(best, 3.0)
    print("\nper note, bulb = left hand, t = 3.0 mm:")
    for j, n in enumerate(NOTES):
        hole = "-" if j == 0 else f"d {best[j-1]:4.2f} G {G[j-1]*1e3:5.3f}"
        print(f"  {n:3s} {res[j]:+6.1f} c   opened hole: {hole}")
    # cents per +0.1 mm on each hole at the note where it opens
    print("\ncents per +0.1 mm diameter at the note where each hole opens:")
    c = ok.c_air(27.0)
    base = ok.Design(c=c, G_w_eff=Gw, V0=V0, k=0.8,
                     holes=[ok.Hole(name=str(i), t=3e-3, d=x * 1e-3) for i, x in enumerate(best)])
    for j in range(12):
        f0 = base.predict(range(j + 1))
        base.holes[j].d += 1e-4
        f1 = base.predict(range(j + 1))
        base.holes[j].d -= 1e-4
        print(f"  hole {j+1:2d} ({NOTES[j+1]}): {ok.cents(f1, f0):+5.1f} c")


def ideal(rows, thumb_center, thumb_bulb, win_area_mm2, t_w=3.0, t=3.0, k=0.80):
    """Kernel-sized diameters for this window, against the measured ones."""
    d = top_diams(rows)
    xpos = {f"T{r[0]}": r[1] for r in rows}
    xpos.update(Bc=74.0, Bb=23.2)
    meas = {f"T{i}": v for i, v in d.items()}
    meas.update(Bc=thumb_center, Bb=thumb_bulb)
    c = ok.c_air(27.0)
    Gw = ok.conductance(win_area_mm2 * 1e-6, t_w * 1e-3, k)
    print(f"\n## Kernel-ideal holes for the measured window ({win_area_mm2:.1f} mm2, wall {t_w} mm): "
          f"G_w = {Gw*1e3:.2f} mm")
    # Identity 1 (doc 03): sum(G_i) / (eta_w G_w) is fixed by the scale -> implied eta_w
    holes = [ok.Hole(name=n, t=t * 1e-3) for n in ORDER_LEFT_BULB]
    ref = ok.solve_linear_fingering([ok.midi_f(m) for m in MIDI], Gw, holes, k=k, c=c)
    ratio_needed = sum(ref.G(i) for i in range(12)) / Gw
    for tt in (2.5, 3.0, 3.5):
        Gw_t = ok.conductance(win_area_mm2 * 1e-6, tt * 1e-3, k)
        sG = sum(ok.conductance(math.pi * (meas[n] * 1e-3) ** 2 / 4, tt * 1e-3, k) for n in ORDER_LEFT_BULB)
        print(f"range identity, walls {tt} mm: sum G_meas {sG*1e3:.1f} mm, G_w {Gw_t*1e3:.2f} mm, "
              f"needed ratio {ratio_needed:.2f} -> implied eta_w {sG / Gw_t / ratio_needed:.2f}")
    for eta in (0.8, 0.9, 1.0):
        holes = [ok.Hole(name=n, t=t * 1e-3) for n in ORDER_LEFT_BULB]
        des = ok.solve_linear_fingering([ok.midi_f(m) for m in MIDI], eta * Gw, holes, k=k, c=c)
        print(f"\neta_w {eta}: V0 {des.V0*1e6:.1f} cm3")
        print("| # | opens | finger | photo hole | x mm | measured d | ideal d | G_meas / G_ideal |")
        for j, h in enumerate(holes):
            gm = ok.conductance(math.pi * (meas[h.name] * 1e-3) ** 2 / 4, t * 1e-3, k)
            gi = ok.conductance(h.area, h.t, k)
            print(f"| {j+1} | {NOTES[j+1]} | {FINGER[j]} | {h.name} | {xpos[h.name]:.0f} | "
                  f"{meas[h.name]:.2f} | {h.d*1e3:.2f} | {gm/gi:.2f} |")


if __name__ == "__main__":
    main()
