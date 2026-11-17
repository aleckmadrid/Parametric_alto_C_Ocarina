"""Cell-size / attachment-radius sensitivity of the network result for one model.

    python Analizes_ocarinas/ECAN3_experimental/tools/convergence.py v0n3

Prints, for each (cell_mm, attach_mm), the network scale in cents relative to
the target at a fixed k (the network k fit stored in results.json), with the
window refitted to the lowest note. A robust geometry effect should not move
by more than a few cents between settings.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "kernel"))
import analyze_model as am      # noqa: E402
import cellnet as cn            # noqa: E402
import ocarina_kernel as ok     # noqa: E402
import voxcav as vc             # noqa: E402


def main(model):
    cfg = am.load_cfg(model)
    out = HERE.parent / "output" / model
    res = json.loads((out / "results.json").read_text(encoding="utf-8"))
    z = np.load(out / "stage1.npz")
    L = z["L"]
    g = vc.Grid(origin=z["origin"], h=float(z["h"]), shape=L.shape)
    cav = L == am.LBL_CAV
    from scipy import ndimage as ndi
    bores, bore_idx = am.compute_bores(cav, g, res["holes"])
    cav = cav & ~bores
    st6 = ndi.generate_binary_structure(3, 1)

    def attach_voxels(n):
        b = np.zeros_like(cav)
        b[tuple(bore_idx[n].T)] = True
        a = np.argwhere(ndi.binary_dilation(b, st6, iterations=2) & cav)
        return a if len(a) else z[f"p{res['holes'][n]['id']}"]
    c = ok.c_air(cfg["temp_c"]) * 1000.0
    k = res["k_fit"]["network"]
    order, notes = cfg["order"], cfg["notes"]
    tg = [ok.midi_f(am.midi_of(n)) for n in notes]
    holes = res["holes"]
    rows = []
    for cell in (3.0, 4.0, 5.0):
        net = cn.build_cells(cav, g.origin, g.h, cell_mm=cell)
        for att in (5.0, 7.0, 9.0):
            cn.attach_opening(net, "window", z[f"p{res['window']['id']}"], radius_mm=att)
            hk = {}
            for n, hh in holes.items():
                cn.attach_opening(net, n, attach_voxels(n), radius_mm=att)
                G = ok.conductance(hh["A"], hh["t"], k)
                hk[n] = dict(hh, G=G, G_net=cn.deembed(net, n, G))
            dvc = {n: hh["A"] * hh["t"] for n, hh in holes.items()}
            Gwk = am.fit_network_window(net, tg[0], c, dvc)
            f, veff, byp, _ = am.network_predict(net, cn.deembed(net, "window", Gwk), hk, order, c)
            cents = [ok.cents(a, b) for a, b in zip(f, tg)]
            rows.append((cell, att, net.n, cents))
            print(f"cell {cell} attach {att} n={net.n}: " + " ".join(f"{nn}:{x:+.0f}" for nn, x in zip(notes, cents)))
    arr = np.array([r[3] for r in rows])
    print("spread (max-min) per note, cents:", " ".join(f"{nn}:{s:.0f}" for nn, s in zip(notes, np.ptp(arr, axis=0))))


if __name__ == "__main__":
    main(sys.argv[1])
