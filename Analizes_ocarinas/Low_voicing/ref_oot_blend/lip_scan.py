"""The lip of the reference across the window: where the dish (outer skin) leaves the chamber, and the angles there.

    python Analizes_ocarinas/Low_voicing/ref_oot_blend/lip_scan.py
"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import measure_details as md  # noqa: E402
import measure_ref as mr  # noqa: E402

M = mr.load()
X, Y, Z = np.eye(3)
ang = lambda d: float(np.degrees(np.arctan2(d[0], -d[1])))      # noqa: E731
rows = []
for x in np.arange(26.0, 40.1, 1.0):
    o = np.array([x, 0, 0.0])
    So, Sc, Sb = (md.segments(M[k], o, X, Y, Z) for k in ("outer", "cavity", "body"))
    box = lambda S: S[(S[..., 0].min(axis=1) > 8) & (S[..., 1].min(axis=1) > 0) & (S[..., 1].max(axis=1) < 30)]      # noqa: E731
    cr = md._cross2(box(So), box(Sc))
    if len(cr) < 2:
        rows.append(dict(x=float(x), open=False))
        continue
    cr = cr[np.argsort(cr[:, 1])]
    lip, top = cr[0], cr[-1]
    down = np.array([0.0, -1.0])
    w, r = md._dir_near(Sc, lip, 1.8, down), md._dir_near(Sb[Sb[..., 0].min(axis=1) > lip[0] - 0.05], lip, 2.5, down)      # the finished body: the dish outside the chamber
    up = np.array([0.0, 1.0])
    wu = md._dir_near(Sc, lip, 1.8, up)                          # the chamber wall on the player's side of the lip (cut away by the dish)
    rows.append(dict(x=float(x), open=True, lip_yz=lip.round(2).tolist(), upper_yz=top.round(2).tolist(),
                     opening_mm=round(float(np.linalg.norm(top - lip)), 2), chamber_wall_deg=round(ang(w), 1), dish_deg=round(ang(r), 1),
                     wedge_deg=round(ang(r) - ang(w), 1), chamber_wall_before_lip_deg=round(ang(-wu), 1)))
(HERE / "lip_scan.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
for r in rows:
    print(r)
