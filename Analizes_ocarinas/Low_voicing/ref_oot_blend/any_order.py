"""The reference's twelve holes in ANY order of opening: is there a fingering under which the kernel sees a 13-note scale?

    python Analizes_ocarinas/Low_voicing/ref_oot_blend/any_order.py

tune_test.py names the holes by hand and opens them in the Asian order. If a name is wrong, its verdict is wrong.
Here no hole has a name: every order of the twelve is allowed (dynamic programming over the 4096 sets of open
holes, since the pitch depends only on which holes are open), the lowest note is taken as exact, and the window's
conductance is free. What is left is the least any fingering chart could leave. The same is done for the two ECAN3
instruments. Writes any_order.json.
"""
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MIDI = [69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89]
RATIO = [2 ** ((m - 69) / 12) for m in MIDI]


def best(V0, holes, k):
    names = list(holes)
    n = len(names)
    g = [holes[x]["A"] / (holes[x]["t"] + k * holes[x]["d_eq"]) for x in names]
    dv = [holes[x]["A"] * holes[x]["t"] for x in names]
    G = [0.0] * (1 << n)
    DV = [0.0] * (1 << n)
    cnt = [0] * (1 << n)
    for S in range(1, 1 << n):
        j = (S & -S).bit_length() - 1
        G[S], DV[S], cnt[S] = G[S ^ (1 << j)] + g[j], DV[S ^ (1 << j)] + dv[j], cnt[S ^ (1 << j)] + 1
    out = None
    for i in range(400):
        gw = 1.0 + 0.05 * i
        f0 = math.sqrt(gw / V0)
        cost = [0.0] * (1 << n)
        for S in range(1, 1 << n):
            c = 1200.0 * math.log2(math.sqrt((gw + G[S]) / (V0 - DV[S])) / f0 / RATIO[cnt[S]])
            cost[S] = c
        dp = [math.inf] * (1 << n)
        prev = [-1] * (1 << n)
        dp[0] = 0.0
        for S in range(1, 1 << n):
            m = S
            bestv, bj = math.inf, -1
            while m:
                j = (m & -m).bit_length() - 1
                m &= m - 1
                v = dp[S ^ (1 << j)]
                if v < bestv:
                    bestv, bj = v, j
            dp[S] = bestv + cost[S] ** 2
            prev[S] = bj
        full = (1 << n) - 1
        rms = math.sqrt(dp[full] / n)
        if out is None or rms < out["rms_cents"]:
            order, S = [], full
            errs = []
            while S:
                j = prev[S]
                order.append(names[j])
                errs.append(round(cost[S], 1))
                S ^= 1 << j
            out = dict(rms_cents=rms, G_window_mm=gw, order=order[::-1], cents_per_note_after_A4=errs[::-1])
    return out


def main():
    res = {}
    for title, p in (("owner's reference", HERE / "output" / "ootb" / "results.json"),
                     ("ECAN3 oot", ROOT / "Analizes_ocarinas" / "ECAN3_experimental" / "output" / "oot" / "results.json"),
                     ("ECAN3 eclipse", ROOT / "Analizes_ocarinas" / "ECAN3_experimental" / "output" / "eclipse" / "results.json")):
        if not p.exists():
            continue
        r = json.loads(p.read_text(encoding="utf-8"))
        holes = {n: dict(A=h["A"], t=h["t"], d_eq=h["d_eq"]) for n, h in r["holes"].items()}
        res[title] = {f"{k:g}": best(r["volumes"]["V0_air_capped_at_outer_rims_mm3"], holes, k) for k in (0.8, 0.66)}
        for k, b in res[title].items():
            print(f"{title}, k {k}: least rms {b['rms_cents']:.0f} cents at G_w {b['G_window_mm']:.2f} mm; order {b['order']}; cents {b['cents_per_note_after_A4']}", flush=True)
    (HERE / "any_order.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
