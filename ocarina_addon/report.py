"""Markdown reports of a built body. No Blender imports of its own (it reads a BodyResult).

    check_blocks(checks)        the checks split into unexpected failures, expected failures and warnings
    stage_report(stage)         the report of a whole stage (stages.Stage): summary, the three blocks, sizes
                                against doc 04, and the kernel sizing of every body with both k values
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
    kind = "soft ergonomic checks" if all(c["name"].startswith("ergo_") for c in b["warnings"]) else "soft checks"
    out += f"; {len(b['warnings'])} warning{'s' if len(b['warnings']) != 1 else ''}" + (
        f" ({kind}, never failures): " + ", ".join(c["name"] for c in b["warnings"]) if b["warnings"] else "")
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
           f"- {build_text(v)}"
           + (" **Prototype settings that are not in the voicing hash:** "
              + ", ".join(f"{k} = {x:g}" for k, x in body.info["unhashed_voicing_options"].items()) + "."
              if body.info.get("unhashed_voicing_options") else ""),
           *option_lines(body),
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
        out.append(("Soft ergonomic checks" if all(c["name"].startswith("ergo_") for c in blocks["warnings"]) else
                    "Soft checks (the hand layout, and the edited shell)") + " outside their range. They are measurements to judge, not failures.")
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
            f"{vol['capped_air_built_cm3']:.4f} cm³ as the air mesh; target {vol['v0_target_cm3']:.4f} cm³ "
            f"(kernel V0 {vol.get('v0_kernel_cm3', vol['v0_target_cm3']):.4f} cm³, volume factor {vol.get('volume_factor', 1.0):g}). "
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
    if g.get("neck"):
        nk = g["neck"]
        out.append(f"| Neck: mouth end width × depth; width × depth where it meets the body | {nk['mouth_width_mm']:.1f} × {nk['mouth_depth_mm']:.1f} mm; "
                   f"{nk['base_width_mm']:.1f} × {nk['base_depth_mm']:.1f} mm (at least {nk['min_wall_mm']:g} mm of plastic around the pipe) | – |")
    if g.get("pocket_blend"):
        pb = g["pocket_blend"]
        out.append(f"| Pocket blend: reach beyond the flat part until it meets the chamber wall | {pb['reach_min_mm']:.1f} to {pb['reach_max_mm']:.1f} mm "
                   f"({pb['met_directions'] + pb['side_wall_directions']} of {pb['directions']} directions end on it) | radius {pb['radius_mm']:g} mm |")
    if "flare_steepest_deg" in g:
        out.append(f"| Plastic above the outer face, seen from the window rim (keep-out flare {v.keepout_outside_flare_deg:.0f}°) | at most "
                   f"{g['flare_steepest_deg']:.1f}° steep, {g['max_height_above_outer_face_mm']:.1f} mm high | at most {g['flare_limit_deg']:.0f}° |")
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
    se = body.info.get("shell_edit")
    if se and m["holes"]:
        out += ["", "## Edited shell (shell-edit build, prototype)", "",
                f"The outer shell ({se['shell_triangles']} triangles, {se['shell_cm3']:.2f} cm³ solid)"
                + (f" and the neck ({se['neck_triangles']} triangles) were" if se["has_neck"] else " was")
                + " edited after the add-on made them, and this body was cut out of them. The chamber, the voicing and the hole positions "
                f"are the add-on's. The wall at each hole was measured on the edited shell and each hole was sized for it, in "
                f"{se['rounds']} sizing round{'s' if se['rounds'] != 1 else ''}; the chamber was solved again so that the capped air is still V0 "
                f"(chamber {vol['cavity_mesh_cm3']:.3f} cm³; {se['chamber_base_cm3']:.3f} cm³ on the base).", "",
                f"*Wall*: the rule's wall ({se['wall_rule_mm']:g} mm) plus the mean of what the edit added over the hole. *On the axis*: the "
                "edited shell along the hole axis. *Rim relief*: how much the added plastic varies around the rim.", "",
                "| Hole | Wall | Added by the edit | On the axis | Rim relief | d on the base | d cut | Change |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in m["holes"]:
            e = se["holes"][r["name"]]
            out.append(f"| {r['name']} | {e['wall_mean_mm']:.3f} | {e['added_mm']:+.3f} | {e['wall_axis_mm']:.3f} | {e['rim_relief_mm']:.2f} | "
                       f"{e['d_base_mm']:.3f} | {r['d_kernel_mm']:.3f} | {r['d_kernel_mm'] - e['d_base_mm']:+.3f} |")
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


# ====================================================================== stage reports

def _window_text(v) -> str:
    shape = v.shape.replace("_", " ").capitalize()
    return f"{shape} {v.window_length_mm:.2f} × {v.window_width_mm:.2f} mm, {v.window_area_mm2:.1f} mm²"


def _check(body, name):
    return next((c for c in body.checks if c["name"] == name), None)


def sizing_section(item) -> list:
    """The kernel's sizing of one body as Markdown: voicing, volumes and every hole with both k values."""
    b = item.body
    sz, v, m = b.sizing, b.sizing.voicing, b.measurements
    vol = m["volume"]
    out = [f"### {item.body_id}", ""]
    if item.note:
        out += [f"*{item.note[0].upper() + item.note[1:]}.*", ""]
    out += [f"- Result: {result_line(b.checks)}.",
            f"- Voicing hash `{v.version_hash}`. Window: {_window_text(v)}, wall {v.wall_at_window_mm:.1f} mm. Windway: exit "
            f"{v.windway_exit_height_mm:.2f} × {v.windway_width_mm:.2f} mm, inlet height {v.windway_inlet_height_mm:.2f} mm, length "
            f"{v.windway_length_mm:.0f} mm; W/h {v.wh_ratio:.2f}. Labium {v.labium_ramp_angle_deg:.0f}°, edge {v.labium_edge_thickness_mm:.1f} mm, "
            f"offset {_offset_text(v.labium_offset_mm)} mm.",
            f"- {build_text(v)}",
            f"- Volume: V0 {sz.v0_cm3:.2f} cm³ (capped air). Measured on the STL: {vol['capped_air_measured_cm3']:.3f} cm³ against the model "
            f"target {vol['v0_target_cm3']:.3f} cm³ ({100 * (vol['capped_air_measured_cm3'] / vol['v0_target_cm3'] - 1):+.3f} %). Cavity mesh "
            f"{sz.cavity_volume_for_mesh_cm3:.2f} cm³ ({sz.wall_chimney_air_cm3:.2f} cm³ of air in the holes, {sz.tube_plastic_cm3:.2f} cm³ of tube wall). "
            f"Cavity spine length {b.cavity.length_mm:.1f} mm. Plastic {vol['body_plastic_cm3']:.1f} cm³."]
    if b.kind == "stub":
        forced = "" if v.shape == "teardrop" else f", forced to a {v.shape.replace('_', ' ')} of the same area (no body carries this window)"
        out.append(f"- Stub: window sized for the {sz.window_for_v0_cm3:g} cm³ body{forced}. Predicted pitch {sz.predicted_pitch_hz:.1f} Hz with the prior "
                   f"η_w {sz.eta_w:.2f} (a prediction, not a measurement).")
    info = item.extra.get("calibration_info") or {}
    if info:
        out.append(f"- Fitted constants: η_w {info['eta_w']:.4f} ({info['eta_w_source']}, match {info.get('eta_w_match', 'legacy')}), "
                   f"k_hole {info['k_hole']:.4f}, position factors of shape `{info['shape']}` (match {info.get('psi_match', 'legacy')})"
                   f"{'' if info['shape_known'] else ' (not used: every factor is 1)'}. A4 error with the kept volume: "
                   f"{sz.a4_error_cents:+.1f} cents." + ("".join(f" **Note:** {w}." for w in info.get("warnings", []))))
    solutions = sz.holes.solutions
    measured = {r["name"]: r for r in m["holes"]}
    if "print" in solutions and solutions["print"]:
        out += ["", "| Hole | Opens | Plain wall d, k 1.0 | Tube | Chimney | **Print d, k 0.8 (cut)** | Nominal d, k 1.0 | d on the STL | Chimney on the STL | Pad limit | Flags |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for p, n in zip(solutions["print"], solutions["nominal"]):
            flags = [t for t, on in (("k 1.0 above the pad limit", n.above_pad_limit), ("k 0.8 above the pad limit", p.above_pad_limit),
                                     ("below the floor", p.below_floor)) if on]
            r = measured[p.name]
            out.append(f"| {p.name} | {p.opens} | {n.d_plain_mm:.2f} | {p.tube_mm:.1f} | {p.chimney_mm:.1f} | **{p.d_mm:.2f}** | {n.d_mm:.2f} | "
                       f"{r['d_measured_mm']:.3f} | {r['chimney_measured_mm']:.3f} | {p.max_d_mm:.0f} | {', '.join(flags) or 'ok'} |")
        out += ["", "All in mm. The plain-wall column is the doc 04 number (no tube). A tube lengthens the chimney, so the tubed hole is larger."]
    elif "fitted" in solutions:
        r1 = {h.name: h for h in item.extra["round1"].holes.solutions["print"]}
        psi = {h.name: h.psi for h in solutions["fitted"]}
        cad = dict(zip([h.name for h in solutions["fitted"]], sz.cad_diameters_mm["fitted"]))
        out += ["", "| Hole | Opens | Position factor ψ | Tube | Chimney | Fitted d (needed in the print) | **CAD d (cut)** | Round 1 print d | Change | d on the STL | Pad limit | Flags |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for h in solutions["fitted"]:
            r = measured[h.name]
            flags = [t for t, on in (("above the pad limit", h.above_pad_limit), ("below the floor", h.below_floor)) if on]
            kept = "" if not item.extra.get("printed_in_round1") else (" (kept)" if abs(h.tube_mm - r1[h.name].tube_mm) < 1e-9 else " (CHANGED)")
            first = (f"{r1[h.name].d_mm:.2f} | {h.d_mm - r1[h.name].d_mm:+.2f}" if item.extra.get("printed_in_round1") else "– | –")
            out.append(f"| {h.name} | {h.opens} | {psi[h.name]:.3f} | {h.tube_mm:.1f}{kept} | {h.chimney_mm:.1f} | {h.d_mm:.2f} | **{cad[h.name]:.2f}** | "
                       f"{first} | {r['d_measured_mm']:.3f} | {h.max_d_mm:.0f} | {', '.join(flags) or 'ok'} |")
        out += ["", "All in mm. *Round 1 print d* is the k_hole 0.8 diameter of the first print at the same volume (– for a body that was never "
                "printed). *Change* is fitted minus round 1. *CAD d* is what the STL has: the fitted diameter minus the hole offset."]
    out += ["", "| Check | Result | Message |", "| --- | --- | --- |"]
    out += [f"| `{c['name']}` | {mark(c)} | {c['message']} |" for c in b.checks]
    files = ", ".join(f"{name}: `{path}`" for name, path in item.files.items() if name != "checks_json")
    out += ["", f"Files: {files}.", ""]
    return out


def _doc04_table(stage) -> list:
    """The table "Generated sizes at each step" of docs/04, regenerated from the bodies of this stage."""
    k = kernel_bridge_kernel()
    rows, seen = [], set()
    for it in stage.items:
        if it.body is None or it.kind != "body" or it.preset_id != "P0" or it.v0_cm3 in seen or "nominal" not in it.body.sizing.holes.solutions:
            continue
        seen.add(it.v0_cm3)
        rows.append((it.v0_cm3, k.sizing.table_row_doc04(it.body.sizing)))
    if not rows:
        return []
    out = ["", "## Sizes against doc 04", "",
           "The table \"Generated sizes at each step\" of [docs/04](../docs/04-testing-phase.md), regenerated by the kernel from the bodies of this "
           "stage (P0 ladder; holes at the k_hole = 1.0 nominal on a plain 4 mm wall, as in doc 04). The bodies are **printed at the k_hole = 0.8 "
           "diameters**, which the per-body tables give. Doc 04 also has a 110 cm³ row; that body belongs to Stage 3. "
           "*P0 length* is the length of the egg that holds V0, as in doc 04; the cavity mesh of a built body holds V0 minus the air in the "
           "holes, so its spine is about 1 % shorter (the per-body sections give it).", "",
           "| V0 | Window | Windway | sub2 (sub_R) | D6 thumb (L_thumb) | E6 thumb (R_thumb) | P0 length | Window area / V0^(2/3) |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for _, cells in sorted(rows):
        out.append("| " + " | ".join(cells) + " |")
    return out


def kernel_bridge_kernel():
    from . import kernel_bridge
    return kernel_bridge.kernel()


def stage_report(stage) -> str:
    """The Markdown report of a stage (stages.Stage): a summary table, three separate blocks (unexpected failures,
    expected failures, warnings), the sizes against doc 04 and one section per body."""
    built = [it for it in stage.items if it.body is not None]
    broken = [it for it in stage.items if it.body is None]
    bad = [it for it in stage.items if it.failed]
    density, masses = stage_density(), stage_masses()
    out = [f"# {stage.title}: generation report", ""]
    if stage.synthetic:
        out += ["> **SYNTHETIC CONSTANTS.** This stage was sized from a fitted-constants file that is marked synthetic: invented truth values, "
                "not measurements of printed bodies. The report shows that the Stage 3 generator works. Do not print these bodies.", ""]
    out += [f"Written by `{stage.command}` on {stage.date}. Every measured number comes from the STL file of the body, read back from disk. "
            f"Run time {stage.seconds:.0f} s for {len(stage.items)} {'body' if len(stage.items) == 1 else 'bodies'}.", "",
            f"Result: **{len(stage.items) - len(bad)} of {len(stage.items)} bodies have no unexpected failure**"
            + ("" if not bad else "; UNEXPECTED FAILURES on " + ", ".join(it.body_id for it in bad)) + ".", ""]
    out += [f"- {line}" for line in stage.header]
    out += [f"- {SUBHOLE_NAMING}",
            ("- The constants of this stage are those of the fitted-constants file named above, not the pre-calibration priors. "
             "This command measured nothing on a printed body: every measured number here comes from an STL file."
             if stage.number == 3 else
             "- Everything is pre-calibration: η_w prior 0.90, k_hole 0.8 for the first prints, 27 °C internal air. "
             "Nothing in this report was measured on a printed body."),
            "- Statuses: `pass` (the docs say ok), `FAIL`, `NEEDS FEM` (cavity-mode desk check between its limits), `WARN` (a soft ergonomic "
            "check; never a failure), `info` (a reported number)."]

    # ---- summary
    out += ["", "## Bodies", "",
            "| Body | Preset | V0 | Voicing hash | Window | Windway exit | Capped air on the STL | First cavity mode (desk check) | Plastic; solid PLA mass | doc 04 mass | Failures | Warnings |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for it in stage.items:
        if it.body is None:
            out.append(f"| {it.body_id} | {it.preset_id} | {it.v0_cm3:g} cm³ | – | – | – | – | – | – | – | **BUILD FAILED** | – |")
            continue
        b = it.body
        v, vol = b.sizing.voicing, b.measurements["volume"]
        cm = _check(b, "cavity_mode_computed")
        mode = f"{cm['value']:.2f} × F6, {mark(cm)}" if cm and cm["value"] == cm["value"] else "NOT COMPUTED"
        c2l = _check(b, "cavity_mode_c2L")
        if c2l:
            mode += f" (c/(2L): {c2l['value']:.2f})"
        blocks = check_blocks(b.checks)
        fails = ", ".join([f"**{c['name']} (unexpected)**" for c in blocks["unexpected"]] + [f"{c['name']} (expected)" for c in blocks["expected"]]) or "none"
        taped = (b.measurements.get("ergonomics") or {}).get("taped")
        warns = (f"{len(blocks['warnings'])} (taped test body)" if taped else str(len(blocks["warnings"]))) if b.layout.holes else "–"
        key = "stub" if it.kind == "stub" else f"{it.preset_id}-{it.v0_cm3:g}"
        plastic = vol["body_plastic_cm3"]
        out.append(f"| {it.body_id} | {it.preset_id} | {b.sizing.v0_cm3:.1f} cm³ | `{v.version_hash}` | {_window_text(v)} | "
                   f"{v.windway_exit_height_mm:.2f} × {v.windway_width_mm:.2f} mm | {vol['capped_air_measured_cm3']:.3f} cm³ "
                   f"({100 * (vol['capped_air_measured_cm3'] / vol['v0_target_cm3'] - 1):+.3f} %) | {mode} | {plastic:.1f} cm³; {plastic * density:.0f} g | "
                   f"{masses.get(key, '–')} g | {fails} | {warns} |")
    out += ["", "*Capped air* is compared with the target of the model: V0 for a round-1 body, the stub volume for a stub, and in Stage 3 "
            "V0 divided by the fitted volume factor, with the holes drawn at their CAD diameters. "
            "*First cavity mode* is the computed desk check with closed holes, which gives the verdict; the number in brackets is the kernel's "
            "c/(2L) estimate from the length of the chamber, the lowest estimate, shown for information (it is 30 to 44 % low for these shapes, "
            "docs/06 section 3.10). "
            f"*Solid PLA mass* is the plastic volume of the STL at {density:g} g/cm³, with no supports, brim or infill saving; the doc 04 figure "
            "includes about 12 % for supports and a brim."]
    if built:
        from . import stages as stages_mod
        total = sum(it.body.measurements["volume"]["body_plastic_cm3"] for it in built) * density
        out += ["", f"Total for the {len(built)} bodies of this stage: {total:.0f} g of solid PLA, {1.12 * total:.0f} g with 12 % for supports and a brim. "
                f"The doc 04 budget for this stage is {stages_mod.DOC04_STAGE_BUDGET[stage.number]}. The generated bodies are lighter than the budget; "
                "the doc 04 masses were estimates made before any body was built."]
    copies = [it for it in built if it.extra.get("copy_of")]
    if copies:
        out += ["", "Repeatability copies: " + "; ".join(
            f"`{it.body_id}` " + ("has the same triangles as" if it.extra.get("same_triangles_as_original") else "was built like")
            + f" `{it.extra['copy_of']}`" for it in copies) + ". A copy has its own STL file, measurement template and check report, and no pictures."]

    # ---- the three blocks
    out += ["", "## Unexpected failures", ""]
    lines = [f"- **{it.body_id}: the build failed.** {it.error}" for it in broken]
    lines += [f"- **{it.body_id}** `{c['name']}`: {c['message']}" for it in built for c in check_blocks(it.body.checks)["unexpected"]]
    out += lines or ["None."]
    if stage.number == 3 and any(c["name"] == "hole_spacing" for it in built for c in check_blocks(it.body.checks)["unexpected"]):
        out += ["", "**Why `hole_spacing` fails here.** The hole positions of a printed body are frozen at the round-1 layout (doc 04 D10), and "
                "the corrected holes are larger than the round-1 holes. A hole that was just clear of its neighbour in round 1 is then too close. "
                "The tightest pair of the hand layout is the left subhole and L_ring (the gaps are in the list above; the limit is 3.4 mm). "
                "The build is correct; the rules conflict. The owner has to choose before the layout is frozen: a longer slide in round 1, a "
                "smaller edge gap in round 2, or a subhole that may move in round 2 (see the build notes, \"Questions for the owner\")."]
    out += ["", "## Expected failures", "",
            "Failures that the plan expects (the pad-limit checks: doc 04 prints these holes on purpose, \"the real limit is unknown\"). "
            "They do not stop a stage."]
    lines = [f"- {it.body_id} `{c['name']}` ({c['status']}): {c['message']}" for it in built for c in check_blocks(it.body.checks)["expected"]]
    needs = [f"- {it.body_id} `{c['name']}` (needs a closer check, not a failure): {c['message']}" for it in built for c in check_blocks(it.body.checks)["needs_fem"]]
    out += [""] + (lines or ["None."]) + needs
    if stage.number == 3:
        over = [(it.body_id, h) for it in built for h in it.body.sizing.holes.solutions.get("fitted", []) if h.above_pad_limit]
        out += ["", "### Round-hole verdict (doc 04, Gate 2)", "",
                "The rule of Gate 2, applied to the holes of this stage: a ladder step fails this verdict if a fitted hole needs more than "
                "10 mm (finger) or 12 mm (thumb)."]
        out += [""] + ([f"- {bid}: {h.name} needs {h.d_mm:.2f} mm (limit {h.max_d_mm:.0f} mm)" for bid, h in over] or ["No fitted hole is above its pad limit."])
    out += ["", "## Warnings", "",
            "Soft ergonomic checks outside their range. They are measurements for the owner to judge. A warning is never a failure."]
    lines = []
    for it in built:
        ws = check_blocks(it.body.checks)["warnings"]
        if not ws:
            continue
        if (it.body.measurements.get("ergonomics") or {}).get("taped"):
            lines.append(f"- {it.body_id}: all {len(ws)} `ergo_*` checks warn: {ergonomics.TAPED_MESSAGE}. The measured numbers are in "
                         f"`{it.files.get('check_report', 'the check report')}`.")
        else:
            lines += [f"- {it.body_id} `{c['name']}`: {c['message']}" for c in ws]
    out += [""] + (lines or ["None."])

    out += _doc04_table(stage)
    if stage.number == 1 and built:
        out += ["", "## Sizes against doc 04", "",
                "The stub table of [docs/04](../docs/04-testing-phase.md), Stage 1, with the generated numbers.", "",
                "| Stub | Window (generated) | Windway exit | Labium offset | Voicing hash | Same hash as | Stub volume on the STL | Predicted pitch | Tests | Build |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        hashes = stub_body_hashes(stage.params)
        for it in built:
            sz, v = it.body.sizing, it.body.sizing.voicing
            out.append(f"| {it.body_id} | {_window_text(v)} | {v.windway_exit_height_mm:.2f} × {v.windway_width_mm:.2f} mm | {_offset_text(v.labium_offset_mm)} mm | "
                       f"`{v.version_hash}` | {hashes.get(v.version_hash, 'no body')} | {it.body.measurements['volume']['capped_air_measured_cm3']:.3f} cm³ | "
                       f"{sz.predicted_pitch_hz:.0f} Hz | {sz.purpose} | {'plain' if v.is_plain_build else 'of the rules'} |")
    out += ["", "## Per body", ""]
    for it in stage.items:
        if it.body is None:
            out += [f"### {it.body_id}", "", f"**The build failed:** {it.error}", ""]
        else:
            out += sizing_section(it)
    return "\n".join(out) + "\n"


def option_lines(body) -> list:
    """Header lines for the options a body was built with (none on a body of the rules)."""
    out = []
    bc = body.info.get("bowl_cut")
    if bc:
        out.append(f"- **Round bowl (an option, not the rule; window_cut `bowl`, in the hash):** measured {bc['bowl_depth_most_mm']:.2f} mm deep, "
                   f"{bc['plastic_under_bowl_least_mm']:.2f} mm of plastic under it, "
                   + (f"{bc['roof_plastic_least_mm']:.2f} mm over the windway's roof, " if bc.get("roof_plastic_least_mm") is not None else "")
                   + f"the window's walls kept exactly to {bc['z_kept_exactly_mm']:.2f} mm; the hole at the bowl's floor xw "
                   f"{bc['hole_extent_xw_mm'][0]:.2f} to {bc['hole_extent_xw_mm'][1]:.2f}, y {bc['hole_extent_y_mm'][0]:.2f} to "
                   f"{bc['hole_extent_y_mm'][1]:+.2f} mm; cutter {bc['cutter_volume_mm3']:.1f} mm³.")
        t = bc.get("throat")
        if t:
            out.append(f"- **The window's throat with the bowl** (kernel, pre-calibration, η_w prior): effective wall t_eff "
                       f"{t['t_eff_outer_face_mm']:.3f} mm to the rule's outer face, {t['t_eff_rim_mm']:.3f} mm to the bowl's rim (z "
                       f"{t['rim_z_mm']:.2f} mm); the rule's ellipse cut alone {t['rule_cut_t_eff_outer_face_mm']:.3f} mm; the kernel takes "
                       f"the wall, {t['wall_mm']:g} mm. The kernel's V0 for this window with each: {t['v0_for_t_eff_outer_face_cm3']:.2f}, "
                       f"{t['v0_for_t_eff_rim_cm3']:.2f}, {t['v0_for_rule_cut_t_eff_outer_face_cm3']:.2f} and {t['v0_for_wall_cm3']:.2f} cm³.")
    if body.info.get("window_throat_mm") is not None:
        out.append(f"- **Sized with the window's throat {body.info['window_throat_mm']:g} mm** (preset value `window_throat_mm`) instead of "
                   "the wall: the window is the rule's, V0 solved again so that A4 is on pitch with that conductance.")
    uw = body.info.get("uneven_wall")
    if uw:
        out.append(f"- **Uneven wall (an option of the shell-edit build):** {uw['wall_least_mm']:.2f} mm on the finger deck to "
                   f"{uw['wall_most_mm']:.2f} mm on the thumb face (wall_front_less_mm {uw['front_less_mm']:g}, wall_back_more_mm "
                   f"{uw['back_more_mm']:g}" + (f", refined within {', '.join(f'{r:g}' for r in uw['refine_mm'])} mm of the window" if uw["refine_mm"] else "")
                   + f"); shell {uw['shell_cm3']:.2f} cm³ solid ({uw['plain_shell_cm3']:.2f} cm³ with the rule's wall).")
    for n, (ds, dw) in (body.info.get("thumb_offsets_mm") or {}).items():
        out.append(f"- **MOVED THUMB HOLE (an ergonomic change):** {n} moved {ds:+g} mm along the hand axis (+ toward the tail) and "
                   f"{dw:+g} mm across it (preset value `thumb_offsets_mm`).")
    return out


def build_text(v) -> str:
    """The build of a voicing (the record's build fields) as one sentence."""
    if getattr(v, "is_plain_build", True):
        return "Build: plain (fan cut, level windway, box stub, no pocket blend). The build is not in this hash."
    cut = {"fan": "fan cut", "cone": f"cone cut, {v.cut_widen_mm:g} mm per side", "ellipse": f"ellipse cut, {v.cut_widen_mm:g} mm per side",
           "bowl": (f"ellipse cut, {v.cut_widen_mm:g} mm per side, opened into a round bowl {2 * v.bowl_half_width_mm:.2f} x "
                    f"{2 * v.bowl_half_length_mm:.2f} mm (xw {v.bowl_centre_xw_mm - v.bowl_half_length_mm:g} to "
                    f"{v.bowl_centre_xw_mm + v.bowl_half_length_mm:g}), set {v.bowl_depth_mm:g} mm deep")}[v.window_cut]
    if v.window_cut != "fan":
        cut += f", shelf {v.shelf_angle_deg:g}°"
    pitch = "level windway" if not v.windway_pitch_deg else f"windway {v.windway_pitch_deg:+g}° against the body"
    if v.stub_style == "neck":
        stub = f"neck standing {v.stub_pitch_deg:g}° off the body" if v.stub_pitch_deg else "neck along the body"
        if abs(v.stub_pitch_deg - v.windway_pitch_deg) > 1e-9:
            stub += f", the pipe lowered {v.stub_pitch_deg - v.windway_pitch_deg:g}° inside it"
    elif v.stub_style == "cone":
        stub = "cone neck, its outer flank " + ("along the pipe" if abs(v.stub_pitch_deg - v.windway_pitch_deg) < 1e-9 else
                                                f"{v.stub_pitch_deg:g}° off the window face, the pipe lowered "
                                                f"{v.stub_pitch_deg - v.windway_pitch_deg:g}° inside it")
    else:
        stub = "box stub" + (f" at {v.stub_pitch_deg:+g}°" if v.stub_pitch_deg else "")
    blend = f"pocket blend {v.pocket_blend_radius_mm:g} mm" if v.pocket_blend_radius_mm else "no pocket blend"
    return f"Build (in the hash): {cut}; {pitch}; {stub}; {blend}."


def _offset_text(x: float) -> str:
    """A labium offset with one decimal, or two when it needs them (the -0.35 mm coupon): -0.2, +0.0, -0.35."""
    s = f"{x:+.2f}"
    return s[:-1] if s.endswith("0") else s


def stub_body_hashes(params) -> dict:
    """voicing hash -> the body that carries the same voicing (P0 ladder), for the stub table."""
    k = kernel_bridge_kernel()
    return {k.voicing.make_voicing(v0, params=params).version_hash: f"the {v0:g} cm³ bodies" for v0 in (65.0, 80.0, 88.0, 95.0)}


def stage_density() -> float:
    from . import stages
    return stages.PLA_DENSITY_G_CM3


def stage_masses() -> dict:
    from . import stages
    return stages.DOC04_MASS_G
