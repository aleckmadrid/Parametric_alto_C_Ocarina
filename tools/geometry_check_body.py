"""Body part of the geometry check (see tools/geometry_check.py for how to run it).

For each body it builds the body, writes the STL files, READS THE BODY STL BACK from disk and runs every
measurement of ocarina_addon/checks_geo.py on the file that was written. It then writes

    addon_checks/<body>.md      every check, the per-hole table, the Boolean log, the voicing numbers
    addon_checks/<body>.json    the same as data
    addon_renders/<body>/       the review pictures (with --renders)
    addon_out/<body>/           the STL files (not committed)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

import numpy as np  # noqa: E402

from ocarina_addon import body as body_mod, checks_geo, export, kernel_bridge, meshutil  # noqa: E402

CHECK_DIR = ROOT / "addon_checks"
OUT_DIR = ROOT / "addon_out"
C4_SET = [("P1", 80.0), ("P0", 80.0), ("P0", 65.0), ("P0", 125.0), ("P2", 80.0), ("P3", 80.0), ("P0", 95.0), ("P0", 110.0)]


def check_body(preset: str, v0: float, renders: bool) -> int:
    t0 = time.time()
    P = kernel_bridge.load_params()
    bid = body_mod.default_body_id(preset, v0)
    out = OUT_DIR / bid
    body = body_mod.build_body(preset, v0, params=P, export_dir=str(out), run_checks=False)
    # measure the file that was written, not the arrays in memory
    V, F = export.read_stl(body.files["stl"])
    file_report = meshutil.manifold_report(V, F)
    checks_geo.run_all(body, P, V, F)
    body.measurements["stl_file"] = dict(path=str(pathlib.Path(body.files["stl"]).relative_to(ROOT)), triangles=file_report["triangles"],
                                         manifold=file_report["manifold"], volume_cm3=meshutil.volume(V, F) / 1000.0,
                                         volume_in_memory_cm3=meshutil.volume(*body.solid) / 1000.0)
    for key in ("air_capped_stl", "air_fem_stl"):
        aV, aF = export.read_stl(body.files[key])
        rep = meshutil.manifold_report(aV, aF)
        body.measurements[key] = dict(triangles=rep["triangles"], manifold=rep["manifold"], shells=rep["shells"],
                                      volume_cm3=meshutil.volume(aV, aF) / 1000.0)
    body_mod.export_body(body, str(out))          # write the checks JSON again, now with the results
    if renders:
        from ocarina_addon import render_body
        render_body.render_all(body)
    write_report(body, time.time() - t0)
    bad = checks_geo.unexpected_failures(body)
    for c in body.checks:
        mark = {"pass": "PASS", "needs_fem": "NEEDS FEM", "fail": "FAIL"}.get(c["status"], c["status"])
        print(f"[{bid}] {mark}{' (expected)' if c['expected'] else ''} {c['name']}: {c['message']}", flush=True)
    print(f"[{bid}] {'OK' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(c['name'] for c in bad)} in {time.time() - t0:.0f} s", flush=True)
    return 1 if bad else 0


def write_report(body, seconds: float) -> None:
    CHECK_DIR.mkdir(exist_ok=True)
    m, sz, v = body.measurements, body.sizing, body.sizing.voicing
    bad = checks_geo.unexpected_failures(body)
    expected = [c for c in body.checks if c["expected"]]
    out = [f"# Geometry check: {body.body_id}", "",
           f"Written by `tools/geometry_check.py -- body {body.preset_id} {body.v0_cm3:g}`. Every measured number comes from the STL "
           f"file `{m['stl_file']['path']}`, read back from disk ({m['stl_file']['triangles']} triangles).", "",
           f"Result: **{'no unexpected failure' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(c['name'] for c in bad)}**"
           + (f"; expected by the notes: {', '.join(c['name'] + ' (' + c['status'] + ')' for c in expected)}" if expected else "")
           + f". Build and check time {seconds:.0f} s.", "",
           f"- Preset {body.preset_id}, V0 {sz.v0_cm3:.2f} cm³, voice rating {v.rating}, holes cut at the `{body.params['hole_key']}` diameters.",
           f"- Voicing hash `{v.version_hash}`: {v.shape} window {v.window_length_mm:.2f} × {v.window_width_mm:.2f} mm, {v.window_area_mm2:.2f} mm², "
           f"windway exit {v.windway_exit_height_mm:.2f} × {v.windway_width_mm:.2f} mm, W/h {v.wh_ratio:.2f}.",
           f"- Cavity spine length {body.cavity.length_mm:.2f} mm (length behind the cavity-mode check: {sz.L_int_mm_used:.2f} mm, {sz.L_int_source}).", "",
           "## Checks", "", "| Check | Result | Message |", "| --- | --- | --- |"]
    for c in body.checks:
        mark = {"pass": "pass", "needs_fem": "NEEDS FEM", "fail": "FAIL"}.get(c["status"], c["status"])
        out.append(f"| `{c['name']}` | {mark}{' (expected)' if c['expected'] else ''} | {c['message']} |")
    vol = m["volume"]
    out += ["", "## Volumes", "",
            f"- Cavity mesh: loft {vol['loft_cm3']:.4f} cm³ + voicing pocket {vol['pocket_cm3']:.4f} cm³ = {vol['cavity_mesh_cm3']:.4f} cm³; "
            f"kernel target {vol['cavity_mesh_target_cm3']:.4f} cm³.",
            f"- Capped air: {vol['capped_air_measured_cm3']:.4f} cm³ measured on the STL by column integration ({vol['capped_air_measure_step_mm']} mm grid), "
            f"{vol['capped_air_built_cm3']:.4f} cm³ as the air mesh; kernel V0 {vol['v0_target_cm3']:.4f} cm³. "
            f"Kernel bookkeeping: {sz.wall_chimney_air_cm3:.3f} cm³ of air in the holes, {sz.tube_plastic_cm3:.3f} cm³ of tube wall.",
            f"- Plastic volume of the body {vol['body_plastic_cm3']:.2f} cm³. Air with the window throat (FEM export) {vol['air_fem_cm3']:.4f} cm³.",
            f"- Exported air files: capped {m['air_capped_stl']['volume_cm3']:.4f} cm³ (manifold {m['air_capped_stl']['manifold']}, "
            f"shells {m['air_capped_stl']['shells']}); with throat {m['air_fem_stl']['volume_cm3']:.4f} cm³ (manifold {m['air_fem_stl']['manifold']}).", "",
            "## Booleans", "", "| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |", "| --- | --- | --- | --- | --- |"]
    for s in body.booleans:
        exp = "–" if s.get("expected_mm3") is None else f"{s['expected_mm3']:+.2f}"
        if s.get("expected_mm3") is None and s.get("bounds"):
            exp = f"between {s['bounds'][0]:+.0f} and {s['bounds'][1]:+.0f}"
        out.append(f"| {s['name']} | {s['solver']} | {s['delta_mm3']:+.2f} | {exp} | {'yes' if s['manifold'] else 'NO'} |")
    g = m["voicing"]
    out += ["", "## Voicing, measured on the mesh", "",
            "| Quantity | Measured | Voicing record |", "| --- | --- | --- |",
            f"| Window length (windway exit to labium) | {g['window_length_mm']:.3f} mm | {v.window_length_mm:.3f} mm |",
            f"| Window width (broad end) | {g['window_width_mm']:.3f} mm | {v.window_width_mm:.3f} mm |",
            f"| Window area | {g['window_area_mm2']:.2f} mm² | {v.window_area_mm2:.2f} mm² |",
            f"| Widest point, from the windway exit | {g['widest_point_xw_mm']:.3f} mm | {0.5 * v.broad_end_length_mm:.3f} mm |",
            f"| Windway exit height × width | {g['windway_exit_height_mm']:.3f} × {g['windway_exit_width_mm']:.3f} mm | {v.windway_exit_height_mm:.3f} × {v.windway_width_mm:.3f} mm |",
            f"| Windway inlet height × width | {g['windway_inlet_height_mm']:.3f} × {g['windway_inlet_width_mm']:.3f} mm | {v.windway_inlet_height_mm:.3f} × {v.windway_width_mm:.3f} mm |",
            f"| Labium ramp angle | {g['labium_angle_deg']:.2f}° | {v.labium_ramp_angle_deg:.2f}° |",
            f"| Labium edge thickness | {g['labium_edge_thickness_mm']:.3f} mm | {v.labium_edge_thickness_mm:.3f} mm |",
            f"| Labium edge against the windway centre line | {g['labium_offset_mm']:+.3f} mm | {v.labium_offset_mm:+.3f} mm |",
            f"| Windway roof thickness / floor lip at the exit | {g['windway_roof_thickness_mm']:.2f} / {g['windway_floor_lip_mm']:.2f} mm | – |",
            f"| Free depth below the window (keep-out {v.keepout_inside_mm:.0f} mm) | {g['depth_below_window_mm']:.1f} mm | – |",
            "", "## Holes, measured on the mesh", "",
            "Diameter: from the area of the bore in a slice at mid wall. Chimney: a ray along the hole axis through the wall before the hole is cut "
            "(doc 02, Phase 4 step 5). Bore wall: mean length of the cut bore wall in the final mesh (it is a little longer than the axis "
            "chimney on a curved wall). Axis: angle between the bore axis and the normal of the cavity mesh.", "",
            "| Hole | Deck | d kernel | d measured | Error | Chimney kernel | Chimney measured | Error | Bore wall | Tube | Axis ° | Moved | Nearest gap | To window | To ramp |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    hv = m["hole_to_voicing"]
    for r in m["holes"]:
        tube = "–" if r["tube_kernel_mm"] <= 0 else (f"{r.get('tube_length_measured_mm', float('nan')):.2f} mm, wall "
                                                      f"{r.get('tube_wall_measured_mm', float('nan')):.2f}")
        out.append(f"| {r['name']} | {r['deck']} | {r['d_kernel_mm']:.3f} | {r['d_measured_mm']:.3f} | {r['d_error_mm']:+.4f} | {r['chimney_kernel_mm']:.2f} | "
                   f"{r['chimney_measured_mm']:.3f} | {r['chimney_error_mm']:+.4f} | {r['bore_wall_mean_length_mm']:.2f} | {tube} | "
                   f"{r['axis_vs_cavity_normal_deg']:.2f} | {r['moved_mm']:.2f} | {r['nearest_gap_mm']:.2f} ({r['nearest_hole']}) | "
                   f"{hv[r['name']]['to_window_mm']:.1f} | {hv[r['name']]['to_ramp_mm']:.1f} |")
    w, t = m["wall"], m["topology"]
    out += ["", "All lengths in millimetres.", "", "## Wall and topology", "",
            f"- Plain wall (cavity to outside along the normal, {w['shell_samples']} rays): minimum {w['shell_min_mm']:.3f} mm, median {w['shell_median_mm']:.3f} mm.",
            f"- Thinnest plastic of the finished body away from the voicing and the tubes ({w['final_samples']} rays): {w['final_min_thickness_mm']:.2f} mm "
            f"at {tuple(round(x, 1) for x in (w['final_min_thickness_at'] or []))}.",
            f"- Topology of the STL: {t['triangles']} triangles, manifold {t['manifold']}, shells {t['shells']}, boundary edges {t['boundary_edges']}, "
            f"non-manifold edges {t['nonmanifold_edges']}, zero-length edges {t['zero_length_edges']}, degenerate triangles {t['degenerate_faces']}, "
            f"self-intersections {t['self_intersections']}, genus {t['genus']}.",
            f"- Layout: {m['layout']['kind']}; compression {m['layout']['compression'] or 'none'}; smallest planned gaps "
            + ", ".join(f"{a}–{b} {gap:.2f}" for a, b, gap in m['layout']['smallest_gaps']) + ".", ""]
    (CHECK_DIR / f"{body.body_id}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    with open(CHECK_DIR / f"{body.body_id}.json", "w", encoding="utf-8") as fh:
        json.dump(dict(body_id=body.body_id, checks=body.checks, measurements=m, booleans=body.booleans), fh, indent=1,
                  default=body_mod._json_default)


def main(args, renders: bool) -> int:
    if args[0] == "body":
        return check_body(args[1], float(args[2]), renders)
    code = 0
    for preset, v0 in C4_SET:
        try:
            code |= check_body(preset, v0, renders)
        except Exception as exc:                 # noqa: BLE001 - one body must not hide the others
            import traceback
            traceback.print_exc()
            print(f"[{preset}-{v0:g}] BUILD FAILED: {exc}", flush=True)
            code |= 1
    return code
