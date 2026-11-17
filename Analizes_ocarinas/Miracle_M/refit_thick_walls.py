"""Miracle AO10-AC: volume re-assessment with thicker hole walls (stdlib + repo kernel only).

The first back-fit (measure_miracle_m.py) assumed uniform 3 mm walls. Angled photos 03 and 05
show deeper bores: the thumb holes look like 4-6 mm chimneys, and the top-face holes at least
3 mm. This script repeats the volume estimate over a grid of wall thicknesses.

Two estimates per case:
  * range identity (window independent): V0 = sum(G_meas) / R * c^2 / (2 pi f_A4)^2, where R is
    the scale's fixed ratio sum(G) / (eta_w G_w), recomputed with the same chimney heights;
  * free weighted least squares of V0 and eta_w*G_w over all 13 notes (as in measure_miracle_m.py).
Then the eta_w that the measured window (56.3 mm2) implies for several window wall thicknesses.

    python Analizes_ocarinas/Miracle_M/refit_thick_walls.py            # k = 0.80 and 1.00
    python Analizes_ocarinas/Miracle_M/refit_thick_walls.py 0.9        # one k value
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "kernel"))
import ocarina_kernel as ok  # noqa: E402

MM = 1e-3
MIDI = [69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89]
F = [ok.midi_f(m) for m in MIDI]
C = ok.c_air(27.0)
# Measured diameters in opening order (Miracle_M.md section 4.2); the last two are the thumbs.
D = [3.54, 2.57, 5.79, 6.11, 5.15, 6.43, 4.50, 6.75, 6.11, 7.08, 10.61, 9.65]
WIN_A = 56.3e-6
TOP_WALLS = (3.0, 4.0, 5.0, 6.0)
THUMB_WALLS = (3.0, 4.0, 5.0, 6.0, 7.0)
WINDOW_WALLS = (3.0, 4.0, 5.0, 6.0)


def walls(t_top, t_thumb):
    return [t_top] * 10 + [t_thumb] * 2


def ratio_needed(t, k):
    holes = [ok.Hole(f"h{i}", ti * MM) for i, ti in enumerate(t)]
    des = ok.solve_linear_fingering(F, 1e-3, holes, k=k, c=C)
    return sum(des.G(i) for i in range(12)) / 1e-3


def lsq(t, k):
    A = [math.pi * (d * MM) ** 2 / 4 for d in D]
    G = [ok.conductance(a, ti * MM, k) for a, ti in zip(A, t)]
    xs, ys = [], []
    for j, f in enumerate(F):
        a = (ok.TWO_PI * f / C) ** 2
        chim = sum(A[i] * t[i] * MM for i in range(j))
        xs.append(a)
        ys.append(sum(G[:j]) + a * chim)
    w = [1.0] * len(xs)
    for _ in range(6):                       # reweight toward relative (cents-like) error
        s11 = sum(wi * a * a for wi, a in zip(w, xs))
        s12 = -sum(wi * a for wi, a in zip(w, xs))
        s22 = sum(w)
        b1 = sum(wi * a * y for wi, a, y in zip(w, xs, ys))
        b2 = -sum(wi * y for wi, y in zip(w, ys))
        det = s11 * s22 - s12 * s12
        V0 = (b1 * s22 - s12 * b2) / det
        Gw = (s11 * b2 - s12 * b1) / det
        w = [1.0 / (a * V0) ** 2 for a in xs]
    des = ok.Design(c=C, G_w_eff=Gw, V0=V0, k=k,
                    holes=[ok.Hole(f"h{i}", ti * MM, d=d * MM) for i, (d, ti) in enumerate(zip(D, t))])
    res = [ok.cents(des.predict(range(j)), f) for j, f in enumerate(F)]
    return V0, math.sqrt(sum(r * r for r in res) / len(res))


def table(k):
    print(f"\n## k = {k:.2f}  (c = {C:.1f} m/s, window 56.3 mm2, d_eq {ok.d_eq(WIN_A)/MM:.2f} mm)\n")
    print("| top mm | thumb mm | sum G mm | R | V0 identity cm3 | closed chimneys cm3 | V0 LSQ cm3 | LSQ rms c | "
          + " | ".join(f"eta_w, window wall {tw:.0f}" for tw in WINDOW_WALLS) + " |")
    print("| " + " | ".join(["---"] * (8 + len(WINDOW_WALLS))) + " |")
    for t_top in TOP_WALLS:
        for t_thumb in THUMB_WALLS:
            t = walls(t_top, t_thumb)
            R = ratio_needed(t, k)
            sG = sum(ok.conductance(math.pi * (d * MM) ** 2 / 4, ti * MM, k) for d, ti in zip(D, t))
            V0 = ok.volume_for(sG / R, F[0], C)
            chim = sum(math.pi * (d * MM) ** 2 / 4 * ti * MM for d, ti in zip(D, t))
            V0l, rms = lsq(t, k)
            etas = [sG / R / ok.conductance(WIN_A, tw * MM, k) for tw in WINDOW_WALLS]
            print(f"| {t_top:.0f} | {t_thumb:.0f} | {sG/MM:.1f} | {R:.2f} | {V0*1e6:.1f} | {chim*1e6:.2f} | "
                  f"{V0l*1e6:.1f} | {rms:.0f} | " + " | ".join(f"{e:.2f}" for e in etas) + " |")


if __name__ == "__main__":
    ks = [float(sys.argv[1])] if len(sys.argv) > 1 else [0.80, 1.00]
    for k in ks:
        table(k)
