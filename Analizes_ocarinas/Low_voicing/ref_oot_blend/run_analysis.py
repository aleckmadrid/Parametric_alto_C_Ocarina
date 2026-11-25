"""Run the ECAN3 reference pipeline (Analizes_ocarinas/ECAN3_experimental/tools/analyze_model.py) on the owner's
low-voicing reference, with this folder as its root (config/, models/, output/, images/).

    python Analizes_ocarinas/Low_voicing/ref_oot_blend/run_analysis.py [--redo-stage1]

The model files are third-party and are not in git (see .gitignore): put the STL at models/oot_blend_body.stl.

One repair between the two stages: the small subhole beside the left ring hole (8.6 mm from it) is found as an
opening, but the bore search slides into the larger neighbour and returns that hole a second time. Its record is
replaced by what find_holes.py measures through the face (3.7 mm across), with the chimney of the holes around it.
"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "ECAN3_experimental" / "tools"
sys.path.insert(0, str(TOOLS))
import analyze_model as am  # noqa: E402

am.ROOT = HERE
MODEL = "ootb"
SUB_L = dict(at=[26.84, -26.5, -1.76], d=3.69)


def repair(outdir):
    p = outdir / "stage1.json"
    meta = json.loads(p.read_text(encoding="utf-8"))
    ts = [r["t"] for r in meta["openings"] if r.get("measured") and not r["is_window"] and r["patch_centroid"][1] < 0 and r.get("t", 9) < 3]
    for r in meta["openings"]:
        c = np.array(r["patch_centroid"])
        if np.linalg.norm(c[[0, 2]] - np.array(SUB_L["at"])[[0, 2]]) < 3.0 and r["patch_centroid"][1] < 0:
            t = float(np.median(ts))
            area = float(np.pi * SUB_L["d"] ** 2 / 4)
            r.update(measured=True, ok=True, centre=r["patch_centroid"], axis=r["patch_normal"], d_eq=SUB_L["d"], A_min=area,
                     A_mean_closed=area, t=t, t_closed=t, t_min=t, t_max=t, z_in=-t, z_out=0.0, n_rays=0,
                     method="through the face (find_holes.py); the bore search returned the neighbouring hole")
            print(f"[{MODEL}] repaired opening {r['id']}: sub_L, d {SUB_L['d']} mm, t {t:.2f} mm")
    p.write_text(json.dumps(meta, indent=1), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    outdir = HERE / "output" / MODEL
    outdir.mkdir(parents=True, exist_ok=True)
    (HERE / "images").mkdir(exist_ok=True)
    cfg = am.load_cfg(MODEL)
    if "--redo-stage1" in sys.argv or not (outdir / "stage1.npz").exists():
        am.stage1(MODEL, cfg, outdir)
    repair(outdir)
    am.stage2(MODEL, cfg, outdir, HERE / "images")
