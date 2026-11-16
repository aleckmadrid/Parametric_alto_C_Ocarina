"""Markdown reports of a built body. No Blender imports of its own (it reads a BodyResult).

    check_blocks(checks)        the checks split into unexpected failures, expected failures and warnings
    body_report(body, ...)      the full check report of one body: every check, the hand layout, the volumes,
                                the Booleans, the voicing and the per-hole table

Names. The reports use the kernel's hole names. The two subholes are `sub1` and `sub2`:
sub1 = sub_L (the left subhole, opens B4), sub2 = sub_R (the right subhole, opens C5).
"""
from __future__ import annotations

import json
import pathlib

from . import ergonomics

SUBHOLE_NAMING = ("Hole names are the kernel's. The subholes are `sub1` and `sub2`: sub1 = sub_L (left subhole, opens B4), "
                  "sub2 = sub_R (right subhole, opens C5).")
MARKS = {"pass": "pass", "needs_fem": "NEEDS FEM", "fail": "FAIL", "warn": "WARN", "info": "info"}


def mark(c) -> str:
    return MARKS.get(c["status"], c["status"]) + (" (expected)" if c.get("expected") else "")


def check_blocks(checks) -> dict:
    """unexpected: failed and not listed as expected. expected: failed or needs_fem, listed as expected.
    needs_fem: the cavity-mode desk check between its limits, not listed as expected. warnings: soft checks."""
    return dict(
        unexpected=[c for c in checks if c["status"] == "fail" and not c.get("expected")],
        expected=[c for c in checks if c["status"] in ("fail", "needs_fem") and c.get("expected")],
        needs_fem=[c for c in checks if c["status"] == "needs_fem" and not c.get("expected")],
        warnings=[c for c in checks if c["status"] == "warn"])


def result_line(checks) -> str:
    b = check_blocks(checks)
    out = "no unexpected failure" if not b["unexpected"] else "UNEXPECTED FAILURES: " + ", ".join(c["name"] for c in b["unexpected"])
    out = f"**{out}**"
    if b["expected"]:
        out += "; expected by the notes: " + ", ".join(f"{c['name']} ({c['status']})" for c in b["expected"])
    if b["needs_fem"]:
        out += "; needs a closer check: " + ", ".join(c["name"] for c in b["needs_fem"])
    out += f"; {len(b['warnings'])} warning{'s' if len(b['warnings']) != 1 else ''}" + (
        " (soft ergonomic checks, never failures): " + ", ".join(c["name"] for c in b["warnings"]) if b["warnings"] else "")
    return out


def _f(x, nd=1):
    return "–" if x is None or x != x else f"{x:.{nd}f}"


def hand_layout_section(m: dict) -> list:
    """The hand layout as tables: both measuring surfaces side by side, and the lean of every finger hole."""
    e = m.get("ergonomics") or {}
    if not e:
        return []
    a, b, rest = e["inner"], e["outer"], e["rest"]
    lay = m["layout"]
    out = ["", "## Hand layout", "",
           "Measured in the frame of the hands (`ocarina_addon/ergonomics.py`, the metrics of docs/06). The `ergo_*` checks use the "
           "hole centres **on the cavity surface**, as docs/06 did for the add-on bodies. The column *at the outer skin* gives the "
           "same number 4 mm further out along each hole axis, where the fingers are; the hole axes spread outward, so it is larger. "
           "It decides nothing."
           + (f" **This body is a {ergonomics.TAPED_MESSAGE}.**" if e.get("taped") else ""), "",
           "| Quantity | On the cavity surface (checked) | At the outer skin |", "| --- | --- | --- |"]

    def row(label, fa, fb=None):
        out.append(f"| {label} | {fa(a)} | {(fb or fa)(b)} |")

    row("Left hand, pinky → ring → middle → index, straight 3D distance", lambda m_: " / ".join(_f(x) for x in m_["pitches_3d"]["L"]) + " mm")
    row("Right hand, pinky → ring → middle → index, straight 3D distance", lambda m_: " / ".join(_f(x) for x in m_["pitches_3d"]["R"]) + " mm")
    row("Hand span pinky to index, left / right (plan view)", lambda m_: f"{_f(m_['L']['span'])} / {_f(m_['R']['span'])} mm")
    row("Pinky to pinky (plan view)", lambda m_: f"{_f(m_['pinky_span'])} mm")
    row("Arch, ring and middle: left / right", lambda m_: f"{', '.join(_f(x) for x in m_['L']['arch'])} / {', '.join(_f(x) for x in m_['R']['arch'])} mm")
    row("Angle between the hand lines", lambda m_: f"{_f(m_['hands_angle'])}°")
    row("Right-hand line nearer the player by", lambda m_: f"{_f(m_['line_offset'])} mm")
    row("R index from L index: across / along the hand axis", lambda m_: f"{_f(m_['index_across'])} / {_f(m_['index_along'])} mm")
    for sub in ergonomics.SUBHOLES:
        if sub in a:
            row(f"{sub}: nearest finger hole, distance, off the normal of that hand line",
                lambda m_, s=sub: f"{m_[s]['parent']}, {_f(m_[s].get('dist_3d', m_[s]['dist']), 2)} mm, {_f(m_[s]['off_normal_deg'], 0)}°")
    row("L thumb from L pinky / R thumb from R middle, along the hand axis",
        lambda m_: f"{_f(m_['L_thumb']['rel']['L_pinky'])} / {_f(m_['R_thumb']['rel']['R_middle'])} mm")
    d = a.get("d_mm", {})
    out.append(f"| Body end from the pinky hole centre, bulb / tail (plan view, along the hand axis) | {_f(rest['bulb'])} / {_f(rest['tail'])} mm | – |")
    out.append(f"| The same from the hole edge (the rest space) | {_f(rest['bulb'] - 0.5 * d.get('L_pinky', 0))} / "
               f"{_f(rest['tail'] - 0.5 * d.get('R_pinky', 0))} mm | – |")
    lean = a.get("lean", {})
    if lean:
        out += ["", "Lean of each finger hole (angle of the hole axis against the normal of the finger face). *Toward the end*: along the "
                "hand axis toward the nearer end of the body. *Toward the hand*: across the hand axis toward the hand that covers the hole "
                "(left hand: the far side; right hand: the player).", "",
                "| Hole | Total lean | Toward the end | Toward the hand | Mostly toward |", "| --- | --- | --- | --- | --- |"]
        for n in ergonomics.FINGERS:
            if n in lean:
                r = lean[n]
                out.append(f"| {n} | {_f(r['tilt_deg'], 0)}° | {r['toward_end_deg']:+.0f}° | {r['toward_hand_deg']:+.0f}° | {r['way']} |")
    out += ["", f"Layout record: kind `{lay['kind']}`"
            + (f"; each hand slid {lay['hand_overlap_mm']:g} mm toward the other (preset value `hand_overlap_mm`)" if lay.get("hand_overlap_mm") else "")
            + "".join(f"; {s} slides {r['slide_mm']:.2f} mm from {r['parent']} (preset {r['slide_nominal_mm']:g} mm)" for s, r in (lay.get("subholes") or {}).items())
            + "; smallest planned gaps " + ", ".join(f"{x}–{y} {gap:.2f}" for x, y, gap in lay["smallest_gaps"]) + " mm."]
    for msg in lay.get("messages", []):
        out.append(f"- {msg}")
    return out


def body_report(body, seconds: float | None = None, written_by: str = "") -> str:
    """The check report of one body as Markdown. Every measured number was measured on the STL read back
    from disk when the body was built by api.build_checked_body()."""
    m, sz, v = body.measurements, body.sizing, body.sizing.voicing
    stl = m.get("stl_file")
    source = (f"Every measured number comes from the STL file `{stl['path']}`, read back from disk ({stl['triangles']} triangles)."
              if stl else "The numbers were measured on the mesh in memory.")
    out = [f"# Geometry check: {body.body_id}", "",
           (written_by + " " if written_by else "") + source, "",
           "Result: " + result_line(body.checks) + (f". Build and check time {seconds:.0f} s." if seconds is not None else "."), "",
           f"- Preset {body.preset_id}, V0 {sz.v0_cm3:.2f} cm³, voice rating {v.rating}"
           + (f", holes cut at the `{body.params['hole_key']}` diameters." if body.layout.holes else ", no holes (a voicing stub)."),
           f"- Voicing hash `{v.version_hash}`: {v.shape} window {v.window_length_mm:.2f} × {v.window_width_mm:.2f} mm, {v.window_area_mm2:.2f} mm², "
           f"windway exit {v.windway_exit_height_mm:.2f} × {v.windway_width_mm:.2f} mm, W/h {v.wh_ratio:.2f}.",
           f"- Cavity spine length {body.cavity.length_mm:.2f} mm"
           + (f" (length behind the kernel's c/(2L) estimate: {sz.L_int_mm_used:.2f} mm, {sz.L_int_source})." if hasattr(sz, "L_int_mm_used") else "."),
           f"- {SUBHOLE_NAMING}", "",
           "## Checks", "",
           "`pass` is what the docs call ok. `WARN` marks a soft ergonomic check outside its range: a warning is never a failure. "
           "`info` is a reported number that decides nothing.", "",
           "| Check | Result | Message |", "| --- | --- | --- |"]
    for c in body.checks:
        out.append(f"| `{c['name']}` | {mark(c)} | {c['message']} |")
    blocks = check_blocks(body.checks)
    out += ["", "## Warnings", ""]
    if blocks["warnings"]:
        out.append("Soft ergonomic checks outside their range. They are measurements to judge, not failures.")
        out.append("")
        out += [f"- `{c['name']}`: {c['message']}" for c in blocks["warnings"]]
    else:
        out.append("None.")
    out += hand_layout_section(m)
    vol = m["volume"]
    out += ["", "## Volumes", "",
            f"- Cavity mesh: loft {vol['loft_cm3']:.4f} cm³ + voicing pocket {vol['pocket_cm3']:.4f} cm³ = {vol['cavity_mesh_cm3']:.4f} cm³; "
            f"kernel target {vol['cavity_mesh_target_cm3']:.4f} cm³.",
            f"- Capped air: {vol['capped_air_measured_cm3']:.4f} cm³ measured on the STL by column integration ({vol['capped_air_measure_step_mm']} mm grid), "
            f"{vol['capped_air_built_cm3']:.4f} cm³ as the air mesh; kernel V0 {vol['v0_target_cm3']:.4f} cm³. "
            f"Kernel bookkeeping: {sz.wall_chimney_air_cm3:.3f} cm³ of air in the holes, {sz.tube_plastic_cm3:.3f} cm³ of tube wall.",
            f"- Plastic volume of the body {vol['body_plastic_cm3']:.2f} cm³. Air with the window throat (FEM export) {vol['air_fem_cm3']:.4f} cm³."]
    if "air_capped_stl" in m:
        out.append(f"- Exported air files: capped {m['air_capped_stl']['volume_cm3']:.4f} cm³ (manifold {m['air_capped_stl']['manifold']}, "
                   f"shells {m['air_capped_stl']['shells']}); with throat {m['air_fem_stl']['volume_cm3']:.4f} cm³ (manifold {m['air_fem_stl']['manifold']}).")
    cm = m.get("cavity_mode") or {}
    if cm.get("computed"):
        out.append(f"- Cavity-mode desk check: first mode {cm['f1_hz']:.0f} Hz, second {cm['f2_hz']:.0f} Hz, top note {cm['f_top_hz']:.1f} Hz, "
                   f"speed of sound {cm['c_m_s']:.1f} m/s; voxel volume {cm['voxel_cm3']:.2f} cm³ on the {cm['grid_mm']:g} mm grid; {cm['solver']}.")
    out += ["", "## Booleans", "", "| Step | Solver | Volume change mm³ | Expected mm³ | Manifold |", "| --- | --- | --- | --- | --- |"]
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
            f"| Widest point, from the windway exit | {g['widest_point_xw_mm']:.3f} mm | {m.get('voicing_record_widest_xw_mm', 0.5 * v.broad_end_length_mm):.3f} mm |",
            f"| Windway exit height × width | {g['windway_exit_height_mm']:.3f} × {g['windway_exit_width_mm']:.3f} mm | {v.windway_exit_height_mm:.3f} × {v.windway_width_mm:.3f} mm |",
            f"| Windway inlet height × width | {g['windway_inlet_height_mm']:.3f} × {g['windway_inlet_width_mm']:.3f} mm | {v.windway_inlet_height_mm:.3f} × {v.windway_width_mm:.3f} mm |",
            f"| Labium ramp angle | {g['labium_angle_deg']:.2f}° | {v.labium_ramp_angle_deg:.2f}° |",
            f"| Labium edge thickness | {g['labium_edge_thickness_mm']:.3f} mm | {v.labium_edge_thickness_mm:.3f} mm |",
            f"| Labium edge against the windway centre line | {g['labium_offset_mm']:+.3f} mm | {v.labium_offset_mm:+.3f} mm |",
            f"| Windway roof thickness / floor lip at the exit | {g['windway_roof_thickness_mm']:.2f} / {g['windway_floor_lip_mm']:.2f} mm | – |",
            f"| Free depth below the window (keep-out {v.keepout_inside_mm:.0f} mm) | {g['depth_below_window_mm']:.1f} mm | – |"]
    if m["holes"]:
        out += ["", "## Holes, measured on the mesh", "",
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
        out += ["", "All lengths in millimetres."]
    w, t = m["wall"], m["topology"]
    out += ["", "## Wall and topology", "",
            f"- Plain wall (cavity to outside along the normal, {w['shell_samples']} rays): minimum {w['shell_min_mm']:.3f} mm, median {w['shell_median_mm']:.3f} mm.",
            f"- Thinnest plastic of the finished body away from the voicing and the tubes ({w['final_samples']} rays): {w['final_min_thickness_mm']:.2f} mm "
            f"at {tuple(round(x, 1) for x in (w['final_min_thickness_at'] or []))}.",
            f"- Topology of the STL: {t['triangles']} triangles, manifold {t['manifold']}, shells {t['shells']}, boundary edges {t['boundary_edges']}, "
            f"non-manifold edges {t['nonmanifold_edges']}, zero-length edges {t['zero_length_edges']}, degenerate triangles {t['degenerate_faces']}, "
            f"self-intersections {t['self_intersections']}, genus {t['genus']}.", ""]
    return "\n".join(out) + "\n"


def write_body_report(body, check_dir, seconds: float | None = None, written_by: str = "", json_default=None) -> pathlib.Path:
    """Write <check_dir>/<id>.md and <id>.json. Returns the Markdown path."""
    check_dir = pathlib.Path(check_dir)
    check_dir.mkdir(parents=True, exist_ok=True)
    md = check_dir / f"{body.body_id}.md"
    md.write_text(body_report(body, seconds, written_by), encoding="utf-8")
    with open(check_dir / f"{body.body_id}.json", "w", encoding="utf-8") as fh:
        json.dump(dict(body_id=body.body_id, checks=body.checks, measurements=body.measurements, booleans=body.booleans), fh,
                  indent=1, default=json_default)
    return md
