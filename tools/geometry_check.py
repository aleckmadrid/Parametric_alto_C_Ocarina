"""Geometry check script. It MEASURES the meshes; it does not restate the inputs.

Run it with Blender 5.1 in background mode, from the repository root:

    blender -b --factory-startup --python tools/geometry_check.py -- cavities [--renders]
    blender -b --factory-startup --python tools/geometry_check.py -- body P1 80 [--renders]
    blender -b --factory-startup --python tools/geometry_check.py -- body P0 95 3 [--renders]   (3 mm window wall)
    blender -b --factory-startup --python tools/geometry_check.py -- bodies [--renders]      (the printed set)
    blender -b --factory-startup --python tools/geometry_check.py -- bodies range [--renders] (plus P0-110, P0-125)

    cavities   every cavity preset (P0-P4) at 65, 80, 88, 95, 110 and 125 cm3: volume against the kernel's
               cavity_volume_for_mesh_cm3, the voicing port before and after scaling, topology,
               the mesh against the cavity formula. Report: addon_checks/C3_cavities.md
    body       one full body: every check of ocarina_addon/checks_geo.py on the exported STL.
               Report: addon_checks/<body>.md, pictures: addon_renders/<body>/

The exit code is 0 when every check passes or fails only as the notes expect, 1 otherwise.
"""
from __future__ import annotations

import json
import math
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from ocarina_addon import cavity, cavity_math, kernel_bridge, meshutil, presets as presets_mod, render  # noqa: E402

CHECK_DIR = ROOT / "addon_checks"
RENDER_DIR = ROOT / "addon_renders"
LADDER = (65.0, 80.0, 88.0, 95.0, 110.0, 125.0)   # 110 and 125: generator range check only, not printed
STAGE2 = {"P0": (65.0, 80.0, 95.0), "P1": (80.0,), "P2": (80.0,), "P4": (80.0,)}
VOLUME_TOL = 0.005
REFERENCE_VOLUME_CM3 = 40.0            # "before scaling": the same preset at another volume


def vertex_normal_at(V, F, point, radius=1e-3):
    """Area-weighted normal of the triangles that touch the vertex nearest to `point`."""
    i = int(np.argmin(np.linalg.norm(V - np.asarray(point), axis=1)))
    tris = F[(F == i).any(axis=1)]
    a, b, c = V[tris[:, 0]], V[tris[:, 1]], V[tris[:, 2]]
    n = np.cross(b - a, c - a).sum(axis=0)
    return n / np.linalg.norm(n), float(np.linalg.norm(V[i] - np.asarray(point)))


def angle_deg(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    c = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def mesh_vs_formula(res, step=8):
    """Largest distance between sampled points of the cavity formula and the nearest mesh vertex."""
    cav = res.math
    worst = 0.0
    for i in range(1, cavity.RES_U - 1, step):
        for j in range(0, cavity.RES_V, step):
            p = np.array(cav.point(math.pi * i / (cavity.RES_U - 1), 2 * math.pi * j / cavity.RES_V))
            worst = max(worst, float(np.linalg.norm(res.V - p, axis=1).min()))
    return worst


def check_cavities(renders: bool) -> int:
    rows, failures, seconds = measure_cavities(renders)
    write_cavity_report(rows, failures, seconds)
    return 1 if failures else 0


def measure_cavities(renders: bool = False):
    """Build and measure every body cavity preset at every ladder volume. Returns (rows, failures, seconds).
    Nothing is written except the pictures (with renders=True). The test suite calls this."""
    k = kernel_bridge.kernel()
    P = kernel_bridge.load_params()
    f_top = k.ocarina_kernel.midi_f(P["design"]["notes_midi"][-1], P["design"]["a4_hz"])
    rows, failures = [], []
    t_start = time.time()
    for pid, preset in presets_mod.load_presets().items():
        if preset.get("layout") == "none":            # the voicing stub preset is not a body cavity
            continue
        ref = cavity.build_cavity(preset, REFERENCE_VOLUME_CM3, keep_object=False)
        n_ref, d_ref = vertex_normal_at(ref.V, ref.F, (0, 0, 0))
        for v0 in LADDER:
            sz = k.sizing.size_body(v0, params=P)
            target = sz.cavity_volume_for_mesh_cm3
            res = cavity.build_cavity(preset, target, keep_object=False)
            rep = meshutil.manifold_report(res.V, res.F)
            n_mesh, d_port = vertex_normal_at(res.V, res.F, (0, 0, 0))
            x_dir, y_dir, z_dir = res.math.port_frame()
            vol_err = res.volume_cm3 / target - 1.0
            si = meshutil.self_intersections(res.V, res.F)
            w_max, h_max = res.math.max_width_height_mm()
            row = dict(
                preset=pid, v0_cm3=v0, stage2=v0 in STAGE2.get(pid, ()), target_cm3=target, measured_cm3=res.volume_cm3,
                volume_error_pct=100.0 * vol_err, scale=res.scale, length_mm=res.length_mm, width_mm=w_max, height_mm=h_max,
                bbox_mm=[float(x) for x in (res.V.max(axis=0) - res.V.min(axis=0))],
                port_distance_before_mm=d_ref, port_distance_after_mm=d_port,
                port_normal_change_deg=angle_deg(n_ref, n_mesh), port_normal_vs_formula_deg=angle_deg(n_mesh, z_dir),
                mesh_vs_formula_mm=mesh_vs_formula(res), manifold=rep["manifold"], shells=rep["shells"],
                boundary_edges=rep["boundary_edges"], nonmanifold_edges=rep["nonmanifold_edges"],
                zero_length_edges=rep["zero_length_edges"], degenerate_faces=rep["degenerate_faces"],
                self_intersections=si, triangles=rep["triangles"],
                cavity_mode_ratio=k.checks.cavity_mode_ratio(res.length_mm * 1e-3, f_top, sz.c_m_s))
            ok = (abs(vol_err) <= VOLUME_TOL and d_port < 1e-3 and d_ref < 1e-3 and row["port_normal_change_deg"] < 0.05
                  and row["port_normal_vs_formula_deg"] < 2.0 and row["mesh_vs_formula_mm"] < 1e-3 and rep["manifold"]
                  and rep["shells"] == 1 and rep["zero_length_edges"] == 0 and rep["degenerate_faces"] == 0 and si == 0)
            row["ok"] = bool(ok)
            if not ok:
                failures.append(f"{pid} at {v0:g} cm3")
            rows.append(row)
            print(f"[cavity] {pid} V0 {v0:g}: target {target:.3f} measured {res.volume_cm3:.4f} cm3 ({100 * vol_err:+.5f} %), "
                  f"L {res.length_mm:.2f} mm, port {d_port:.1e} mm, normal change {row['port_normal_change_deg']:.4f} deg, "
                  f"manifold {rep['manifold']}, self-intersections {si}, {'OK' if ok else 'FAIL'}", flush=True)
            if renders and v0 == 80.0:
                out = RENDER_DIR / "C3_cavities" / pid
                jet = [((0, 0, 0), x_dir, 12.0, (0.1, 0.3, 1.0, 1.0)), ((0, 0, 0), z_dir, 8.0, (1.0, 0.2, 0.1, 1.0))]
                files = render.render_views([(res.V, res.F, (0.78, 0.74, 0.62, 1.0))], str(out), prefix="",
                                            views=("top", "bottom", "front", "end", "iso", "iso_bottom"), markers=jet, size_px=700)
                # section across the body through the port, seen from the right-hand end (u = +Y, v = +Z)
                sec, _ = render.section_image(res.V, res.F, (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), str(out / "section_port.png"),
                                              mm_per_px=0.1, marks=[((0.0, 0.0), (1.0, 0.1, 0.1))])
                # section along the body through the spine height at the port station (u = +X, v = +Y), seen from above
                c = res.math.to_body(res.math.spine_raw(res.math.port_u)[0])
                sec2, _ = render.section_image(res.V, res.F, (0, 0, c[2]), (0, 0, 1), (1, 0, 0), (0, 1, 0), str(out / "section_plan.png"),
                                               mm_per_px=0.15)
                sec3, _ = render.section_image(res.V, res.F, (0, c[1], 0), (0, 1, 0), (1, 0, 0), (0, 0, 1), str(out / "section_long.png"),
                                               mm_per_px=0.15)
                render.contact_sheet(files + [sec, sec2, sec3], str(out / "sheet.png"), cols=3)
    return rows, failures, time.time() - t_start


def write_cavity_report(rows, failures, seconds):
    CHECK_DIR.mkdir(exist_ok=True)
    (CHECK_DIR / "C3_cavities.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    out = ["# C3 geometry check: cavity presets", "",
           "Written by `tools/geometry_check.py -- cavities`. Every number is measured on the evaluated mesh.", "",
           f"Result: **{'all cavities pass' if not failures else 'FAILED: ' + ', '.join(failures)}** "
           f"({len(rows)} cavities, {seconds:.0f} s).", "",
           "- Target: `BodySizing.cavity_volume_for_mesh_cm3` of the kernel for the P0 hole set at that V0 (plain cavity, "
           "before the voicing pocket of C4).",
           "- Port before / after: distance from the origin to the nearest mesh vertex, for the preset at "
           f"{REFERENCE_VOLUME_CM3:g} cm³ (before) and at the target (after). The port is the origin by construction, "
           "so both must be zero.",
           "- Normal change: angle between the mesh normals at the port before and after scaling.",
           "- Mesh vs formula: largest distance between the cavity formula (`cavity_math.py`) and the mesh, on a grid of samples.",
           "- Stage 2 marks the volumes that the test plan prints for that shape.", "",
           "| Preset | V0 cm³ | Stage 2 | Target cm³ | Measured cm³ | Error % | Length mm | Width × height mm | Port before mm | Port after mm | "
           "Normal change ° | Mesh vs formula mm | Manifold | Shells | Zero edges | Self-intersections | c/(2L) ÷ F6 | Result |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        out.append(f"| {r['preset']} | {r['v0_cm3']:g} | {'yes' if r['stage2'] else ''} | {r['target_cm3']:.3f} | {r['measured_cm3']:.4f} | "
                   f"{r['volume_error_pct']:+.5f} | {r['length_mm']:.2f} | {r['width_mm']:.1f} × {r['height_mm']:.1f} | "
                   f"{r['port_distance_before_mm']:.1e} | {r['port_distance_after_mm']:.1e} | {r['port_normal_change_deg']:.4f} | "
                   f"{r['mesh_vs_formula_mm']:.1e} | {'yes' if r['manifold'] else 'NO'} | {r['shells']} | {r['zero_length_edges']} | "
                   f"{r['self_intersections']} | {r['cavity_mode_ratio']:.3f} | {'pass' if r['ok'] else 'FAIL'} |")
    (CHECK_DIR / "C3_cavities.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[cavity] report: {CHECK_DIR / 'C3_cavities.md'}")


def main(argv) -> int:
    args = [a for a in argv if not a.startswith("--")]
    renders = "--renders" in argv
    if not args or args[0] == "cavities":
        return check_cavities(renders)
    if args[0] in ("body", "bodies"):
        from tools import geometry_check_body           # C4 part, kept in its own file
        return geometry_check_body.main(args, renders)
    print(__doc__)
    return 2


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    sys.stdout.flush()
    os._exit(code) if code else None
