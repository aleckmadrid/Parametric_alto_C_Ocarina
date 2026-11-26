"""The add-on's windway and window cut, made in the owner's sample (its body and its neck). A picture experiment.

Run sample_frame.py first (it finds the frame of the sample's window and writes the body and the neck to
addon_out/sample_owner/). Then, with Blender 5.1 in background mode, from the repository root:

    blender -b --factory-startup --python Analizes_ocarinas/Neck_volume/sample_cut.py

What it does: the body and the neck of the sample are joined. The add-on's windway cutter and window cutter (the
voicing record of an 80 cm3 body: teardrop window 9.65 x 8.81 mm, ellipse cut "P3", lip 0.4 mm, ramp 20 deg) are
placed in the sample's own window frame, with the lip where the centre line of the sample's wind cut meets the
flat face inside its body, and the pipe at the sample's own angle. The two are cut out, and with them the pocket:
the flat ceiling under the window (plain, without the blend, which needs the add-on's own chamber). Nothing else
is done: the sample keeps its own chamber and its own holes, and NO CHECK RUNS. The result is not an instrument;
it shows how the add-on's cut looks on a neck shaped as the owner shaped it.

Three things differ from the rules, all because the sample differs: the pipe stands 17.65 deg off the window face
(the rule is +5 deg), the windway is made 40 mm long so that it comes out of the sample's longer neck (the rule is
30 mm), and the wall at the window is the sample's 5.3 mm (the rule is 4 mm), so the ramp and the dish are longer.

Writes images/sample-cut_*.png, sample_cut.json and addon_out/sample_owner/sample_cut.stl (not committed).
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ocarina_addon import export, kernel_bridge, meshutil, render, voicing_geo  # noqa: E402

IMG = HERE / "images"
PARTS = ROOT / "addon_out" / "sample_owner"
WINDWAY_LENGTH_MM = 40.0
BODY_COLOR = (0.78, 0.74, 0.62, 1.0)


def main():
    S = json.loads((HERE / "sample_frame.json").read_text(encoding="utf-8"))
    o, fx, fy, fz = (np.asarray(S[k], float) for k in ("origin", "x", "y", "z"))
    pitch = float(S["numbers"]["pipe_against_face_deg"])
    K, P = kernel_bridge.kernel(), kernel_bridge.load_params()
    v = K.voicing.make_voicing(80.0, params=P)
    # a picture experiment: the record is not used for anything else, so its hash and its sizes no longer belong together
    v = dataclasses.replace(v, windway_length_mm=WINDWAY_LENGTH_MM, wall_at_window_mm=float(S["numbers"]["wall_at_flat_face_mm"]))
    vs = voicing_geo.build(v, (fx, fy, fz), windway_pitch_deg=pitch, stub_pitch_deg=pitch, stub_style="box", pocket_blend_radius_mm=0.0)
    shift = o - voicing_geo.POCKET_CLEARANCE_MM * fz                          # the inner plane of the voicing on the sample's flat face

    body = meshutil.cleanup(*export.read_stl(str(PARTS / "body.stl")))
    neck = meshutil.cleanup(*export.read_stl(str(PARTS / "neck.stl")))
    print("sample: body", round(meshutil.volume(*body) / 1000, 2), "cm3, neck", round(meshutil.volume(*neck) / 1000, 2), "cm3", flush=True)
    V, F, _ = meshutil.boolean(body, neck, "UNION")
    steps = [("body + neck", meshutil.volume(V, F))]
    for name, (cV, cF) in (("pocket", vs.pocket), ("windway", vs.windway), ("window throat + labium ramp", vs.window)):
        before = meshutil.volume(V, F)
        V, F, _ = meshutil.boolean((V, F), (np.asarray(cV) + shift, cF), "DIFFERENCE")
        steps.append((name, before - meshutil.volume(V, F)))
        print(f"{name}: removes {steps[-1][1]:.0f} mm3", flush=True)
    rep = meshutil.manifold_report(V, F)
    export.write_stl(str(PARTS / "sample_cut.stl"), V, F)

    IMG.mkdir(parents=True, exist_ok=True)
    L, Lw, wall = v.window_length_mm, v.windway_length_mm, v.wall_at_window_mm
    mid = o - fx * (L + 0.45 * 30.0) + fz * 4.0
    sel = np.linalg.norm(V - mid, axis=1) < 50.0
    keep = sel[F].all(axis=1)
    used = np.unique(F[keep])
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    part = (V[used], remap[F[keep]], BODY_COLOR)
    views = {"_outside": (tuple(-0.75 * fz + 0.50 * fx + 0.42 * fy), tuple(fz), True),
             "_window": (tuple(-0.62 * fz - 0.70 * fx + 0.28 * fy), tuple(fz), True),
             "_side": (tuple(fy), tuple(fz), False),
             "_mouth": (tuple(fx - 0.25 * fz), tuple(fz), False)}
    for key, (look, up, cropped) in views.items():
        render.VIEWS[key] = (look, up)
        p = render.render_views([part if cropped else (V, F, BODY_COLOR)], str(IMG), prefix="sample-cut", views=(key,), size_px=820)[0]
        os.replace(p, str(IMG / f"sample-cut{key}.png"))
    extent = (-L - 30.0 - 4.0 - 10.0, 18.0, -24.0, wall + 16.0)
    render.section_image(V, F, o, fy, fx, fz, str(IMG / "sample-cut_section.png"), mm_per_px=0.05, extent=extent, marks=[((0.0, 0.0), (1.0, 0.1, 0.1))])
    out = dict(pitch_deg=pitch, windway_length_mm=WINDWAY_LENGTH_MM, wall_at_window_of_the_sample_mm=S["numbers"]["wall_at_flat_face_mm"],
               steps=[dict(name=n, mm3=float(x)) for n, x in steps], manifold=bool(rep["manifold"]), triangles=int(rep["triangles"]),
               cut=vs.info["cone"], roof_at_exit_plane_z_mm=vs.info["windway_roof_at_exit_plane_z_mm"])
    (HERE / "sample_cut.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("ok", out["steps"], "manifold", out["manifold"], flush=True)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
