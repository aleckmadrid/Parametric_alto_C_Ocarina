"""Builds one full test body: cavity, wall, voicing, holes. Every number comes from the kernel.

Order of work (the "wall stack" and the Booleans)

    1  sizing            kernel: voicing record, hole diameters (first prints: the "print" set, k_hole 0.8),
                         tubes, the target volume of the cavity mesh
    2  cavity            Geometry Nodes loft, scaled about the voicing port. The scale is solved so that
                         (loft joined with the voicing pocket) has the kernel's cavity_volume_for_mesh_cm3
    3  skin              the cavity surface moved outward by the wall thickness (uniform 4 mm)
    4  envelope          skin joined with the voicing block (mouthpiece stub and flat window face)
                         [hook: a user outer mesh would be joined here, see OUTER_MESH_HOOK]
    5  shell             envelope minus (cavity joined with the pocket)
    6  tubes             each inward tube is joined (a cylinder from the wall into the cavity)
    7  holes             each hole is cut along the cavity normal, through wall and tube
    8  window, windway   the window throat with the labium ramp is cut, then the windway

After every Boolean the result must be manifold, and the volume of the solid must change by the
expected amount (meshutil.BooleanLog). The invariant at the end is that the CAPPED AIR equals the
kernel's V0: every hole capped at the outer skin, the window capped at the inner plane.
"""
from __future__ import annotations

import json
import math
import os
import types
from dataclasses import dataclass, field

import numpy as np

from . import cavity as cavity_mod
from . import cavity_math, export, holes_layout, kernel_bridge, meshutil, presets as presets_mod, voicing_geo

HOLE_SEGMENTS_DEFAULT = 64
TUBE_ROOT_MM = 2.0             # an inward tube starts this far inside the wall, so that it joins the wall cleanly
HOLE_CUT_OUTSIDE_MM = 3.0      # hole cutters reach this far outside the skin
HOLE_CUT_INSIDE_MM = 0.6       # and this far beyond the deepest point of the cavity wall under the hole
VOLUME_SOLVE_TOL = 2e-5        # relative error of the cavity-plus-pocket volume after the scale solve
CAP_EPS_MM = 0.02              # the caps of the window and the windway sit this far from the cap planes
CLEAN_MERGE_MM = 1e-3          # after the last cut, points closer than 1 micrometre are merged (Boolean slivers)

# Hook for the later feature "user outer mesh inside a sculpt envelope" (not built in this version).
# A function (envelope (V, F), body context) -> (V, F) may be set here; it runs after step 4.
OUTER_MESH_HOOK = None

# ---- the shell-edit build (prototype, branch shell-edit-prototype; see shell_edit.py). build_body(outer=...) takes
# the outer shell and the neck that the user has edited instead of making them (steps 3 and 4). The numbers marked
# PROVISIONAL are mine, for the prototype: the owner has not decided them. The least wall is the owner's (2026-11-18).
SHELL_DEPTH_TOL_MM = 0.02      # the wall measured at each hole and the wall its diameter was sized for agree to this
SHELL_DEPTH_ROUNDS = 8         # sizing rounds allowed to reach that
SHELL_RINGS, SHELL_SPOKES = 4, 16   # rays per hole: rings of equal area over the hole's disc, and one ring on its rim
# Owner decision of 2026-11-18: the least wall of an edited shell is 3 printed walls. In the standard 0.20 mm profiles
# of Bambu Studio and OrcaSlicer for a 0.4 mm nozzle that is 0.42 (outer wall) + 2 x 0.45 (inner walls) = 1.32 mm.
# PrusaSlicer's 0.20 mm profiles use 0.45 mm for every wall: 1.35 mm, the figure the notes use for the voicing block.
SHELL_MIN_WALL_MM = 1.32       # an edited shell may not leave less plastic than this over the chamber
SHELL_WALL_WARN_MM = 1.0       # PROVISIONAL: a hole whose wall is this far from the rule's wall is outside what the test prints measure
SHELL_RIM_WARN_MM = 0.5        # PROVISIONAL: relief across the rim of a hole above this may keep a finger from sealing it
SHELL_SELF_INTERSECTION_MAX_TRIANGLES = 600_000   # the self-intersection test of a user mesh is skipped above this size


@dataclass
class BodyResult:
    body_id: str
    preset_id: str
    v0_cm3: float
    rating: str
    sizing: object                       # kernel BodySizing
    voicing_hash: str
    cavity: object                       # cavity.CavityResult (the loft)
    voicing: object                      # voicing_geo.VoicingSolids
    layout: object                       # holes_layout.Layout
    solid: tuple                         # (V, F) final body
    envelope: tuple                      # (V, F) skin joined with the block, before any cut
    precut: tuple                        # (V, F) body with tubes, before the holes and the voicing cuts
    air_capped: tuple                    # (V, F) capped air (the V0 convention)
    air_fem: tuple                       # (V, F) capped air plus the window throat (for FEM)
    voicing_air: tuple                   # (V, F) the loft joined with the voicing pocket (the kernel's "cavity mesh")
    air_capped_cm3: float
    cavity_air_cm3: float                # loft joined with the pocket (the kernel's "cavity mesh")
    pocket_cm3: float
    booleans: list                       # one dict per Boolean
    measurements: dict = field(default_factory=dict)
    checks: list = field(default_factory=list)       # dicts: name, status, value, limit, message, expected
    files: dict = field(default_factory=dict)
    object_names: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    kind: str = "body"                   # "body" (12 holes) or "stub" (a Stage 1 voicing stub: no holes)
    info: dict = field(default_factory=dict)         # what the caller wants to keep with the body (stage, calibration, ...)


def default_body_id(preset_id: str, v0_cm3: float, wall_at_window_mm: float | None = None,
                    default_wall_mm: float = 4.0) -> str:
    """P0-80, or P0-95-w3 for a body built with the 3 mm window wall option."""
    base = f"{preset_id}-{v0_cm3:g}"
    if wall_at_window_mm is not None and abs(float(wall_at_window_mm) - default_wall_mm) > 1e-9:
        base += f"-w{float(wall_at_window_mm):g}"
    return base


def cut_rows(sz, hole_key: str) -> list:
    """The holes to cut: the kernel's rows of `hole_key` with d_mm replaced by the diameter to draw in CAD
    (design diameter minus the fitted hole offset; the two are equal while the offset is 0, as in round 1)."""
    rows = sz.holes.solutions[hole_key]
    cad = sz.cad_diameters_mm[hole_key]
    return [types.SimpleNamespace(name=r.name, d_mm=float(c), tube_mm=r.tube_mm, wall_mm=r.wall_mm, d_design_mm=r.d_mm)
            for r, c in zip(rows, cad)]


def capped_target_cm3(sz, rows) -> float:
    """Capped air that the CAD model must hold: the cavity mesh target, minus the tube walls, plus the air in
    the holes as they are drawn. With volume factor 1 and hole offset 0 this is the kernel's V0. With fitted
    constants the model is drawn at V0 / volume factor, so that the PRINT holds V0."""
    hole_air = sum(math.pi * r.d_mm ** 2 / 4.0 * r.wall_mm for r in rows) / 1000.0
    return sz.cavity_volume_for_mesh_cm3 - sz.tube_plastic_cm3 + hole_air


def build_body(preset, v0_cm3: float, *, rating: str | None = None, wall_at_window_mm: float | None = None,
               params: dict | None = None,
               body_id: str | None = None, hole_key: str = "print", sizing_fn=None, layout_rows=None,
               kind: str = "body", info: dict | None = None, export_dir: str | None = None,
               renders: bool = False, render_dir: str | None = None, save_blend: bool = False,
               keep_objects: bool = False, run_checks: bool = True, cavity_mode_step: bool = True,
               verbose: bool = True, outer=None, calibration=None, shell_identity=None) -> BodyResult:
    """Build a test body. `preset` is a preset name or dict; v0_cm3 is the capped air volume (the acoustic target).

    outer        the shell-edit build (prototype): (shell, neck), each a closed mesh (V, F) in body coordinates, or
                 (shell, None) when the neck is part of the shell. They replace the skin and the voicing block, which
                 this function otherwise makes itself. The chamber, the voicing and the hole positions stay those of
                 the preset. The wall at each hole is measured on the given shell and the holes are sized for it; the
                 chamber is solved again so that the capped air stays V0. See shell_edit.py for the two steps.

    wall_at_window_mm  wall at the window: 4.0 (default) or 3.0 ([voicing_rules] window_wall_options_mm).
                 The 3 mm wall gives a narrower window at the same V0. The wall at the holes is not changed.
    hole_key     which kernel hole set is cut: "print" (k_hole 0.8, the first prints) or "nominal" (k_hole 1.0).
    sizing_fn    a function (L_int_mm or None[, walls]) -> sizing record, used instead of kernel sizing.size_body. It then
                 decides the window wall too (wall_at_window_mm is only used by the default sizing). Stage 3
                 passes one that sizes from fitted constants (hole_key is then "fitted"); a stub passes one that
                 returns a stub.StubSizing. It is called before the cavity exists, and again with the internal
                 length of the built cavity (None for the P0 egg, which keeps the kernel's own length). With an
                 uneven or edited shell it also gets `walls` (hole name -> mm, measured at each hole; None on the first
                 call) and must size the holes for them. A record sized from fitted constants must already carry the
                 variant's build fields in its voicing (presets.resolve_sizing raises otherwise).
    calibration  fitted constants (kernel calibration.Calibration): the body is sized from them for its resolved voicing
                 (presets.calibrated_sizing_fn), also on an uneven or edited shell; hole_key is then "fitted". The
                 calibration's info is kept in info["calibration_info"].
    shell_identity  with outer, what shell_edit.calibration_identity measured on the edited shell: the constants are
                 matched on it (presets.calibration_context). shell_edit.finish gives it; without it an edited shell
                 is "unverified" and matches no constants exactly.
    layout_rows  hole rows that decide the hole POSITIONS (default: the rows that are cut). Stage 3 passes the
                 round-1 rows, so that corrected holes stay where the round-1 holes were (doc 04 D10).
    kind, info   "body" or "stub"; a dict that is kept with the result.
    export_dir   write <id>.stl (the body), <id>_air_capped.stl, <id>_air_fem.stl and <id>_checks.json there.
    renders      write the review pictures to render_dir (default addon_renders/<id>/ in the repository).
    cavity_mode_step   run the cavity-mode desk check (a second Python process with scipy, see cavity_mode.py).
                 When it is off, or no such Python is found, the check `cavity_mode_computed` fails and says so.
    """
    k = kernel_bridge.kernel()
    P = params if params is not None else kernel_bridge.load_params()
    if isinstance(preset, str):
        preset = presets_mod.get_preset(preset)
    P = presets_mod.params_for(preset, P)               # a variant may set the pipe's length (presets/variants.toml)
    rating = rating or preset.get("rating")
    pid = preset.get("id", "custom")
    body_id = body_id or default_body_id(pid, v0_cm3, wall_at_window_mm,
                                         float(P["voicing_rules"]["default_wall_at_window_mm"]))
    log = (lambda *a: print(f"[{body_id}]", *a, flush=True)) if verbose else (lambda *a: None)
    if calibration is not None:
        if sizing_fn is not None:
            raise ValueError("give calibration or sizing_fn, not both")
        info = dict(info or {}, calibration_info={}, synthetic=bool(calibration.synthetic))
        sizing_fn = presets_mod.calibrated_sizing_fn(calibration, preset, v0_cm3, P, rating=rating, wall_at_window_mm=wall_at_window_mm,
                                                     edited_shell=outer is not None, identity=shell_identity,
                                                     info=info["calibration_info"])
        hole_key = "fitted"
    uneven = None
    if outer is None and (preset.get("wall_front_less_mm") or preset.get("wall_back_more_mm")):
        # the uneven wall (an option of the shell-edit build): the add-on makes the shell itself, thinner on the finger
        # deck and thicker on the thumb face, and finishes it as an edited shell (each hole sized for its own wall)
        from . import shell_edit
        outer, uneven = shell_edit.uneven_outer(preset, v0_cm3, rating=rating, wall_at_window_mm=wall_at_window_mm, params=P,
                                                hole_key=hole_key, body_id=body_id, sizing_fn=sizing_fn)
    # rounded outer rims on the holes (an option, off by default): each hole is sized for the straight chimney of the same
    # inertance, so it needs the per-hole walls of the edited-shell path
    rim_r = float(preset.get("hole_rim_round_mm") or 0.0)
    if rim_r and outer is None:
        raise ValueError("hole_rim_round_mm needs a build with a wall per hole (the uneven wall or an edited shell)")

    # ---- 1 sizing (hole sizes do not depend on the cavity length; the checks do, see below)
    if sizing_fn is None:
        def sizing_fn(L_int_mm, walls=None):
            return k.sizing.size_body(float(v0_cm3), rating, wall_at_window_mm, params=P, L_int_mm=L_int_mm,
                                      wall_at_holes_mm=walls, throat_mm=preset.get("window_throat_mm"))
    # A variant build may replace build fields of the voicing (window cut, pitch, neck ...). The replacement goes into
    # the record, so the hash that is stored, checked and written to the measurement template names what was built.
    plain_sizing_fn = sizing_fn

    def sizing_fn(L_int_mm, *more):
        return presets_mod.resolve_sizing(preset, plain_sizing_fn(L_int_mm, *more))
    sz = sizing_fn(None)
    v = sz.voicing
    target_cm3 = sz.cavity_volume_for_mesh_cm3
    wall = float(P["hole_rules"]["wall_at_holes_mm"])
    tube_wall = float(P["hole_rules"]["tube_wall_mm"])
    segments = int(P["constraints"].get("mesh_hole_segments", HOLE_SEGMENTS_DEFAULT))
    slide_max = float(P.get("ergonomics", {}).get("subhole_distance_mm", (0.0, holes_layout.SUBHOLE_SLIDE_MAX_MM))[1])
    log(f"sizing: V0 {sz.v0_cm3:.2f} cm3, cavity mesh target {target_cm3:.3f} cm3, voicing {v.version_hash} "
        f"({v.shape} {v.window_length_mm:.2f} x {v.window_width_mm:.2f} mm)")

    # ---- 2 cavity: solve the loft volume so that loft + pocket = target
    blog = meshutil.BooleanLog()
    solved = solve_cavity(preset, v, target_cm3, log)

    # ---- the shell-edit build: the user's shell and neck are the envelope. The wall at each hole is measured on it,
    #      the holes are sized for those walls, and the chamber is solved again until the two agree.
    walls = shell = user_layout = user_envelope = None
    if outer is not None:
        user_envelope = join_user_shell(outer, blog, log)
        check_chamber_inside(solved.cav, user_envelope)    # first: a shell that left the chamber is the cause of every later fault
        base_rows = cut_rows(sz, hole_key)                 # the holes of the base: they decide the hole positions
        base_target_cm3, base_sz = target_cm3, sz
        walls = {r.name: r.wall_mm for r in base_rows}
        for rnd in range(SHELL_DEPTH_ROUNDS):
            if rnd:
                sz = sizing_fn(None, walls)
                if sz.voicing.version_hash != v.version_hash:
                    raise meshutil.GeometryError("the voicing changed with the walls at the holes: it must not")
                if abs(sz.cavity_volume_for_mesh_cm3 / target_cm3 - 1.0) > 1e-9:
                    target_cm3 = sz.cavity_volume_for_mesh_cm3
                    solved = solve_cavity(preset, v, target_cm3, log, pocket_guess_mm3=solved.pocket_mm3)
            user_layout = holes_layout.with_rows(      # positions: the caller's rows (a printed layout) or the base's
                holes_layout.make_layout(solved.cav.math, preset, layout_rows if layout_rows is not None else base_rows,
                                         slide_max_mm=slide_max), cut_rows(sz, hole_key))
            over = shell_over_holes(solved.cav, user_layout.holes, user_envelope, wall)
            for h in user_layout.holes:
                over[h.name]["wall_sized_mm"] = k.voicing.rounded_rim_wall_mm(over[h.name]["wall_mean_mm"], h.d_mm, rim_r)
            worst = max((abs(over[h.name]["wall_sized_mm"] - h.wall_mm) for h in user_layout.holes), default=0.0)
            log(f"shell round {rnd}: the wall measured at the holes differs from the wall they were sized for by at most {worst:.3f} mm")
            if worst <= SHELL_DEPTH_TOL_MM:
                break
            walls = {name: o["wall_sized_mm"] for name, o in over.items()}
        else:
            raise meshutil.GeometryError(f"the walls at the holes did not settle in {SHELL_DEPTH_ROUNDS} rounds (last change {worst:.3f} mm)")
        user_layout.messages = [m for m in user_layout.messages if not m.startswith("the hole positions are those of the round-1")]
        user_layout.messages.append("the hole positions are those of the base; the diameters are sized for the wall measured at each hole "
                                    "of the edited shell")
        for r in base_rows:                                # for the report: what the hole was on the base
            over[r.name]["d_base_mm"] = float(r.d_mm)
        # A deeper hole must be wider. Holes that the edit pushed above the finger-pad limit, per hole set:
        pushed = {}
        for key, new_rows in sz.holes.solutions.items():
            was = {r.name: r for r in base_sz.holes.solutions[key]}
            names = [(r.name, float(r.d_mm), float(r.max_d_mm)) for r in new_rows if r.above_pad_limit and not was[r.name].above_pad_limit]
            if names:
                pushed[key] = names
        shell = dict(holes=over, rounds=rnd + 1, has_neck=outer[1] is not None, wall_rule_mm=wall, hole_rim_round_mm=rim_r,
                     chamber_base_cm3=float(base_target_cm3), pushed_above_pad_limit=pushed,
                     shell_cm3=float(meshutil.volume(*outer[0]) / 1000.0), calibration_identity=shell_identity,
                     shell_triangles=int(len(outer[0][1])), neck_triangles=int(len(outer[1][1])) if outer[1] is not None else 0)
    cav, vs, air, air_mm3, pocket_mm3 = solved.cav, solved.vs, solved.air, solved.air_mm3, solved.pocket_mm3
    blog.steps.append(dict(name="cavity + voicing pocket (air)", operation="UNION", solver=solved.solver,
                           volume_before_mm3=cav.volume_cm3 * 1000.0, volume_after_mm3=air_mm3, delta_mm3=pocket_mm3,
                           expected_mm3=None, bounds=(0.0, float(meshutil.volume(*vs.pocket))), ok=True, manifold=True,
                           shells=1, triangles=solved.triangles))

    # the checks need the real internal length for P1-P4; the P0 egg keeps the kernel's own length
    L_int = None if pid == "P0" else cav.length_mm
    sz = sizing_fn(L_int) if walls is None else sizing_fn(L_int, walls)
    if sz.voicing.version_hash != v.version_hash or abs(sz.cavity_volume_for_mesh_cm3 - target_cm3) > 1e-9:
        raise meshutil.GeometryError("the sizing changed between its two calls: it must not depend on the internal length")

    # ---- 3 skin, 4 envelope
    if user_envelope is None:
        skin = plain_skin(cav, wall)
        if meshutil.self_intersections(*skin) > 0:
            raise meshutil.GeometryError("the offset skin intersects itself")
        block_mm3 = meshutil.volume(*vs.block)
        envelope = blog.apply("skin + voicing block", skin, vs.block, "UNION", bounds=(0.0, block_mm3 + 1.0))
        if OUTER_MESH_HOOK is not None:
            envelope = OUTER_MESH_HOOK(envelope, dict(preset=preset, sizing=sz, cavity=cav, voicing=vs))
    else:
        envelope = user_envelope
        check_chamber_inside(cav, envelope)

    # ---- the round bowl (window_cut "bowl", an option): the window cutter is remade through the finished outside
    bowl = None
    if v.window_cut == "bowl":
        from . import bowl_cut
        bV, bF, bowl, allr = bowl_cut.cutter(vs, v, envelope, air)
        bowl["throat"] = bowl_cut.throat_record(k.voicing, v, vs, allr, bowl["rim_height_mean_mm"], P)
        vs.window = (bV, bF)
        log(f"bowl cut: depth {bowl['bowl_depth_most_mm']:.2f} mm, {bowl['plastic_under_bowl_least_mm']:.2f} mm under it, walls kept to "
            f"{bowl['z_kept_exactly_mm']:.2f} mm, cutter {bowl['cutter_volume_mm3']:.1f} mm3")

    # ---- 5 shell
    solid = blog.apply("envelope - cavity air", envelope, air, "DIFFERENCE", expected_delta_mm3=-air_mm3,
                       tol_rel=1e-4, tol_abs_mm3=0.5)

    # ---- hole placement
    rows = cut_rows(sz, hole_key)
    if user_layout is not None:
        layout = user_layout
    else:
        layout = holes_layout.make_layout(cav.math, preset, layout_rows if layout_rows is not None else rows, slide_max_mm=slide_max)
        if layout_rows is not None:
            layout = holes_layout.with_rows(layout, rows)
    for m in layout.messages:
        log("layout: " + m)

    # ---- 6 tubes. A tube starts inside the wall; where an edited shell is thin it starts half-way through the wall.
    def tube_root(h):
        return min(TUBE_ROOT_MM, 0.5 * h.wall_mm)

    for h in layout.holes:
        if h.tube_mm <= 0:
            continue
        r_out = 0.5 * h.d_mm + tube_wall
        tube = meshutil.cylinder(h.centre, h.axis, r_out, -h.tube_mm, tube_root(h), segments, area_true=False)
        poly = 0.5 * segments * r_out * r_out * math.sin(2 * math.pi / segments)
        solid = blog.apply(f"tube {h.name}", solid, tube, "UNION", expected_delta_mm3=poly * h.tube_mm,
                           tol_rel=0.08, tol_abs_mm3=2.0)
    precut = solid

    # ---- 7 holes. The air mesh is built beside the body: cavity air, minus the tubes, plus each hole up to the skin.
    air_mesh = air
    for h in layout.holes:
        if h.tube_mm > 0:
            tube = meshutil.cylinder(h.centre, h.axis, 0.5 * h.d_mm + tube_wall, -h.tube_mm, tube_root(h), segments, area_true=False)
            V, F, _ = meshutil.boolean(air_mesh, tube, "DIFFERENCE")
            air_mesh = (V, F)
    env_tree = meshutil.bvh(*envelope) if rim_r else None
    for h in layout.holes:
        inner = max(h.tube_mm, rim_depth(cav, h)) + HOLE_CUT_INSIDE_MM
        # the cutter must come out of the shell: on an edited shell, above the highest point over the hole
        top = shell["holes"][h.name]["top_mm"] if shell else h.wall_mm
        cutter = meshutil.cylinder(h.centre, h.axis, 0.5 * h.d_mm, -inner,
                                   top + HOLE_CUT_OUTSIDE_MM, segments, area_true=True)
        # with rounded rims h.wall_mm is the sized (shorter) chimney; the plastic the bore removes is the measured wall
        cut_wall = shell["holes"][h.name]["wall_mean_mm"] if shell and rim_r else h.wall_mm
        expected = -math.pi * h.d_mm ** 2 / 4.0 * (cut_wall + h.tube_mm)
        solid = blog.apply(f"hole {h.name}", solid, cutter, "DIFFERENCE", expected_delta_mm3=expected,
                           tol_rel=0.04, tol_abs_mm3=1.0)
        air_tool = cutter
        if rim_r:
            rc = rim_cutter(h, env_tree, rim_r, segments)
            a = 0.5 * h.d_mm
            est = 2.0 * math.pi * (a + 0.22 * rim_r) * (1.0 - math.pi / 4.0) * rim_r ** 2   # the quarter round's volume
            solid = blog.apply(f"rim {h.name}", solid, rc, "DIFFERENCE", bounds=(-4.0 * est - 2.0, -0.2 * est))
            V, F, _ = meshutil.boolean(cutter, rc, "UNION")             # one piece, so the air is capped at the skin once
            air_tool = (V, F)
        V, F, _ = meshutil.boolean(air_tool, envelope, "INTERSECT")     # the hole, capped at the outer skin
        V, F, _ = meshutil.boolean(air_mesh, (V, F), "UNION")
        air_mesh = (V, F)

    # ---- 8 window (throat + labium ramp), then the windway. Expected volumes come from column integration,
    #        which does not use a Boolean.
    o, fx, fy, fz = vs.frame
    L, W = v.window_length_mm, v.window_width_mm
    reach = vs.info["ramp_reach_mm"]
    bbox = (-L - 1.0 - float(vs.info.get("shelf_reach_mm") or 0.0), reach + 1.0, -(0.5 * W + reach + 1.0), 0.5 * W + reach + 1.0)
    if bowl is not None:                                # the bowl reaches beyond the box of the plain cut: integrate over all of it
        Pw = (np.asarray(vs.window[0], float) - np.asarray(o, float)) @ np.stack([fx, fy, fz], axis=1)
        bbox = (min(bbox[0], float(Pw[:, 0].min()) - 1.0), max(bbox[1], float(Pw[:, 0].max()) + 1.0),
                min(bbox[2], float(Pw[:, 1].min()) - 1.0), max(bbox[3], float(Pw[:, 1].max()) + 1.0))
    exp_window = meshutil.intersection_volume_columns(solid, vs.window, o, fx, fy, fz, bbox, step=0.25)
    solid = blog.apply("window throat + labium ramp", solid, vs.window, "DIFFERENCE", expected_delta_mm3=-exp_window,
                       tol_rel=0.03, tol_abs_mm3=3.0)
    bbox = (-L - v.windway_length_mm - 2.0, 2.0, -(0.5 * W + 0.5), 0.5 * W + 0.5)
    do, dfx, dfy, dfz = vs.windway_frame()                  # the windway's own frame (turned by the windway pitch)
    exp_windway = meshutil.intersection_volume_columns(solid, vs.windway, do, dfx, dfy, dfz, bbox, step=0.2)
    solid = blog.apply("windway", solid, vs.windway, "DIFFERENCE", expected_delta_mm3=-exp_windway,
                       tol_rel=0.04, tol_abs_mm3=3.0)

    # ---- cleanup: merge the points that the Booleans left closer than a micrometre. Nothing is remeshed or smoothed.
    solid = meshutil.cleanup(*solid, merge_mm=CLEAN_MERGE_MM, no_self_intersection=True)
    if not meshutil.manifold_report(*solid)["manifold"]:
        raise meshutil.GeometryError("the final mesh is not manifold")

    # ---- capped air (the V0 convention): the mesh built beside the body, and the air with the window throat for FEM
    capped = meshutil.cleanup(*largest_shell(*air_mesh), merge_mm=CLEAN_MERGE_MM)
    air_fem = meshutil.cleanup(*air_with_throat(capped, vs, v), merge_mm=CLEAN_MERGE_MM)
    capped_cm3 = meshutil.volume(*capped) / 1000.0
    capped_target = capped_target_cm3(sz, rows)
    log(f"capped air (built) {capped_cm3:.4f} cm3 against the target {capped_target:.4f} cm3 "
        f"({100 * (capped_cm3 / capped_target - 1):+.4f} %)")

    body = BodyResult(body_id=body_id, preset_id=pid, v0_cm3=float(v0_cm3), rating=v.rating, sizing=sz,
                      voicing_hash=v.version_hash, cavity=cav, voicing=vs, layout=layout, solid=solid, envelope=envelope,
                      precut=precut, air_capped=capped, air_fem=air_fem, voicing_air=air, air_capped_cm3=capped_cm3,
                      cavity_air_cm3=air_mm3 / 1000.0, pocket_cm3=pocket_mm3 / 1000.0, booleans=blog.steps,
                      params=dict(wall_mm=wall, wall_at_window_mm=v.wall_at_window_mm, tube_wall_mm=tube_wall, hole_segments=segments, hole_key=hole_key,
                                  capped_target_cm3=capped_target),
                      kind=kind, info=dict(info or {}, **({"unhashed_voicing_options": voicing_geo.options_from(preset)}
                                                              if voicing_geo.options_from(preset) else {})))
    if bowl is not None:
        body.info["bowl_cut"] = bowl
    if uneven is not None:
        body.info["uneven_wall"] = uneven
    if preset.get("window_throat_mm") is not None:
        body.info["window_throat_mm"] = float(preset["window_throat_mm"])
    if preset.get("thumb_offsets_mm"):
        body.info["thumb_offsets_mm"] = {n: [float(x) for x in d] for n, d in preset["thumb_offsets_mm"].items()}
    if shell is not None:
        # An edited shell: the least plastic over the chamber is a limit of its own (the plain wall is the rule's wall
        # only where the user did not touch it), and the checks read the walls that were measured at the holes.
        body.params["min_wall_mm"] = SHELL_MIN_WALL_MM
        body.info["shell_edit"] = shell
        body.user_shell = outer[0] if outer[1] is not None else None     # the shell without the neck, for hole_to_voicing
    body.info["calibration_context"] = presets_mod.calibration_context(
        preset, edited_shell=outer is not None and uneven is None, identity=shell_identity)

    # The STL files are written before the checks: the cavity-mode step reads the exported air mesh.
    if export_dir:
        export_meshes(body, export_dir)
    if run_checks:
        from . import checks_geo
        try:
            checks_geo.run_all(body, P, cavity_mode_step=cavity_mode_step)
        except meshutil.GeometryError as exc:
            if shell is None:
                raise
            # The measurements look for the voicing where the record puts it. On an edited shell a missing part
            # means that the edit removed it (a neck cut shorter than the pipe, plastic carved off the window face).
            raise meshutil.GeometryError(f"the finished body could not be measured: {exc}. The neck or the window face was "
                                         "edited too far: the mouth end of the neck and the face around the window must stay "
                                         "where the base had them") from exc
    if export_dir:
        write_checks_json(body, export_dir)
    if renders:
        from . import render_body
        render_body.render_all(body, render_dir)
    if keep_objects or save_blend:
        make_objects(body, preset)
    if save_blend and export_dir:
        import bpy
        path = os.path.join(export_dir, f"{body_id}.blend")
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(path))
        body.files["blend"] = path
    return body


def solve_cavity(preset, v, target_cm3: float, log=lambda *a: None, pocket_guess_mm3: float = 0.0):
    """Step 2: the cavity loft and the voicing solids, with the loft scaled so that (loft joined with the voicing
    pocket) holds target_cm3. pocket_guess_mm3 is a first guess of the pocket's own volume (a second solve of the
    same body starts from the pocket of the first)."""
    loft_target = target_cm3 - pocket_guess_mm3 / 1000.0
    for it in range(5):
        cav = cavity_mod.build_cavity(preset, loft_target, keep_object=False)
        vs = voicing_geo.build(v, cav.math.port_frame(), cavity_height=cavity_height_fn(cav, v), **voicing_geo.options_from(preset))
        aV, aF, solver = meshutil.boolean((cav.V, cav.F), vs.pocket, "UNION")
        air_mm3 = meshutil.volume(aV, aF)
        pocket_mm3 = air_mm3 - cav.volume_cm3 * 1000.0
        err = air_mm3 / (target_cm3 * 1000.0) - 1.0
        log(f"volume solve {it}: loft {cav.volume_cm3:.4f} cm3 + pocket {pocket_mm3 / 1000:.4f} cm3 = {air_mm3 / 1000:.4f} cm3 "
            f"({100 * err:+.5f} %)")
        if abs(err) < VOLUME_SOLVE_TOL:
            break
        loft_target = target_cm3 - pocket_mm3 / 1000.0
    else:
        raise meshutil.GeometryError("the cavity volume solve did not converge")
    rep = meshutil.manifold_report(aV, aF)
    if not rep["manifold"] or rep["shells"] != 1:
        raise meshutil.GeometryError("cavity joined with the pocket is not one closed shell")
    if pocket_mm3 <= 0:
        raise meshutil.GeometryError("the voicing pocket added no air: the inner plane is inside the cavity")
    return types.SimpleNamespace(cav=cav, vs=vs, air=(aV, aF), air_mm3=air_mm3, pocket_mm3=pocket_mm3, solver=solver,
                                 triangles=rep["triangles"])


def plain_skin(cav, wall: float) -> tuple:
    """Step 3: the cavity surface moved outward by the wall along its vertex normals. It is the shell of a body
    that nobody edited, and the surface an edited shell is measured against."""
    return cav.V + wall * meshutil.vertex_normals(cav.V, cav.F), cav.F.copy()


# ------------------------------------------------------------------ the shell-edit build (prototype)

def checked_user_mesh(what: str, V, F) -> tuple:
    """A mesh that the user edited, as a closed solid the Booleans can use. Raises GeometryError with the reason
    when it is not one closed surface with outward normals."""
    V, F = np.asarray(V, dtype=np.float64), np.asarray(F, dtype=np.int64)
    if len(F) == 0:
        raise meshutil.GeometryError(f"the {what} has no faces")
    V, F = meshutil._weld(V, F)                         # a Blender mesh holds single precision: merge what coincides
    rep = meshutil.manifold_report(V, F)
    if not rep["manifold"]:
        raise meshutil.GeometryError(f"the {what} is not a closed surface: {rep['boundary_edges']} open edges, "
                                     f"{rep['nonmanifold_edges']} edges with more than two faces, {rep['inconsistent_edges']} "
                                     f"edges with flipped faces. Close the holes or remesh it")
    if rep["shells"] != 1:
        raise meshutil.GeometryError(f"the {what} is {rep['shells']} separate pieces: join them into one solid (remesh) or delete the loose ones")
    if meshutil.volume(V, F) <= 0.0:
        raise meshutil.GeometryError(f"the faces of the {what} point inward: recalculate the normals")
    if len(F) <= SHELL_SELF_INTERSECTION_MAX_TRIANGLES:
        # Faces that only touch are not a fault: a mesh that came out of a Boolean or a remesh has slivers that lie
        # in each other to within the single precision of a Blender mesh. A crossing deeper than 0.1 micrometre counts.
        n = meshutil.self_intersections(V, F, eps=1e-4)
        if n:
            raise meshutil.GeometryError(f"the {what} passes through itself in {n} places: remesh it")
    return V, F


def join_user_shell(outer, blog, log=lambda *a: None) -> tuple:
    """The envelope of the shell-edit build: the user's shell joined with the user's neck."""
    shell, neck = outer
    shell = checked_user_mesh("shell", *shell)
    if neck is None:
        log(f"edited shell: {len(shell[1])} triangles, {meshutil.volume(*shell) / 1000.0:.2f} cm3; no separate neck")
        return shell
    neck = checked_user_mesh("neck", *neck)
    log(f"edited shell: {len(shell[1])} triangles, {meshutil.volume(*shell) / 1000.0:.2f} cm3; neck: {len(neck[1])} triangles, "
        f"{meshutil.volume(*neck) / 1000.0:.2f} cm3")
    envelope = blog.apply("shell + neck", shell, neck, "UNION", bounds=(-0.5, meshutil.volume(*neck) + 1.0))
    if meshutil.manifold_report(*envelope)["shells"] != 1:
        raise meshutil.GeometryError("the neck does not touch the shell: the two must overlap where they meet")
    return envelope


def check_chamber_inside(cav, envelope, step: int = 5) -> None:
    """The chamber must lie inside the edited shell with printable plastic over it. This is the test that says where
    it does not; the wall check of the finished body measures the same rays and applies the limit."""
    tree = meshutil.bvh(*envelope)
    N = meshutil.vertex_normals(cav.V, cav.F)
    worst, where = float("inf"), None
    # A ray along the normal of a chamber vertex runs exactly through the matching vertex of a shell that nobody
    # edited, and can slip between its triangles. So a ray that finds an even number of surfaces is sent again, a
    # little off the normal; a point is outside only when all three rays say so.
    tilts = ((0.0, 0.0), (0.013, 0.007), (-0.009, 0.011))
    for i in np.unique(cav.F)[::step]:
        if np.linalg.norm(N[i]) < 0.5:
            continue
        helper = np.array([1.0, 0.0, 0.0]) if abs(N[i][0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        a = np.cross(N[i], helper)
        a /= np.linalg.norm(a)
        b = np.cross(N[i], a)
        t = 0.0
        for ta, tb in tilts:
            hits = meshutil.ray_hits(tree, cav.V[i] + N[i] * 1e-3, N[i] + ta * a + tb * b, 400.0)
            if len(hits) % 2 == 1:
                t = hits[0][0] + 1e-3
                break
        if t < worst:
            worst, where = t, cav.V[i]
    if worst < 0.4:
        raise meshutil.GeometryError(
            f"the chamber comes through the shell near ({where[0]:.0f}, {where[1]:.0f}, {where[2]:.0f}) mm ({worst:.2f} mm of plastic "
            f"there): the shell was carved or moved too far inward. Add material there")


def shell_over_holes(cav, holes, envelope, wall: float) -> dict:
    """Per hole: how much plastic an edited shell has along the hole axis.

    Rays run outward along the hole axis, from the plane through the hole centre, over the hole's disc. Each one
    meets the edited shell and the plain skin (the cavity moved outward by `wall`); the difference is what the edit
    added there (negative: what it took away). Per hole:

        wall_mean_mm   wall + the mean of that difference over the disc. This is the wall the kernel sizes the hole
                       for. On a shell that nobody edited the difference is zero and this is the rule's wall, so the
                       body is the one the one-step build makes
        added_mm       the mean difference alone
        wall_axis_mm   the edited shell on the hole axis (what a ray along the axis measures on the finished body)
        rim_relief_mm  how much the difference varies around the rim of the hole: relief that a finger pad must seal
        top_mm         the highest point of the shell over the disc; the hole cutter starts above it
    """
    if not holes:
        return {}
    env_tree, skin_tree = meshutil.bvh(*envelope), meshutil.bvh(*plain_skin(cav, wall))
    out = {}
    for h in holes:
        p, n = np.asarray(h.centre, float), np.asarray(h.axis, float)
        helper = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        u = np.cross(n, helper)
        u /= np.linalg.norm(u)
        w = np.cross(n, u)
        R = 0.5 * h.d_mm

        def first(tree, q):
            # A ray that runs exactly through an edge or a vertex of the mesh can slip between the triangles (a hole
            # on the top line of the body sits on a line of the chamber's grid). Such a ray is sent again from a
            # start point 2 micrometres to the side.
            for du, dw in ((0.0, 0.0), (2e-3, 1e-3), (-1e-3, 2e-3), (-2e-3, -1e-3), (1e-3, -2e-3)):
                hit = meshutil.ray_hits(tree, q + du * u + dw * w, n, 200.0, limit=1)
                if hit:
                    return hit[0][0]
            raise meshutil.GeometryError(f"hole {h.name}: the shell does not cover the hole (rays along its axis find no surface)")

        def both(q):
            return first(env_tree, q), first(skin_tree, q)

        axis_e, _ = both(p)
        disc, rim = [], []
        ang = np.arange(SHELL_SPOKES) * (2.0 * math.pi / SHELL_SPOKES)
        for k_ring in range(SHELL_RINGS):
            r = R * math.sqrt((k_ring + 0.5) / SHELL_RINGS)                  # rings of equal area
            for a in ang + (0.5 * (k_ring % 2)) * (2.0 * math.pi / SHELL_SPOKES):
                disc.append(both(p + r * (math.cos(a) * u + math.sin(a) * w)))
        for a in ang:
            rim.append(both(p + R * (math.cos(a) * u + math.sin(a) * w)))
        disc, rim = np.array(disc), np.array(rim)
        added = float((disc[:, 0] - disc[:, 1]).mean())
        rim_added = rim[:, 0] - rim[:, 1]
        out[h.name] = dict(wall_mean_mm=wall + added, added_mm=added, wall_axis_mm=float(axis_e),
                           rim_relief_mm=float(rim_added.max() - rim_added.min()),
                           top_mm=float(max(axis_e, disc[:, 0].max(), rim[:, 0].max())), rays=int(len(disc) + len(rim) + 1))
    return out


RIM_STEPS = 12                 # facets of a hole's rounded rim, along its quarter round


def rim_cutter(h, env_tree, r: float, segments: int):
    """A closed solid that rounds a hole's outer rim by r: in each half-plane through the hole axis a quarter ellipse,
    tangent to the bore r below where the bore meets the outside and ending on the outside r out from the bore.
    shortcut: tangent to the outside only where the outside is square to the axis; on a sloped or curved outside
    the round meets it at an angle of up to that slope. A rim shaped along the outside's normals would fix it."""
    p, n = np.asarray(h.centre, float), np.asarray(h.axis, float)
    n = n / np.linalg.norm(n)
    helper = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(n, helper)
    u /= np.linalg.norm(u)
    w = np.cross(n, u)
    ang = np.arange(segments) * (2.0 * math.pi / segments)          # the bore's own angles (meshutil.cylinder)
    dirs = np.cos(ang)[:, None] * u + np.sin(ang)[:, None] * w
    a = 0.5 * h.d_mm

    def heights(rad):
        out = []
        for d_ in dirs:
            for j in ((0.0, 0.0), (2e-3, 1e-3), (-1e-3, -2e-3)):    # a ray along an edge can slip through: send it again beside
                hit = meshutil.ray_hits(env_tree, p + rad * d_ + j[0] * u + j[1] * w, n, 200.0, limit=1)
                if hit:
                    out.append(hit[0][0])
                    break
            else:
                raise meshutil.GeometryError(f"hole {h.name}: no outside found around the rim for its round")
        return np.array(out)

    h_in, h_out = heights(a), heights(a + r)
    rise = np.maximum(h_out - h_in + r + 0.02, 0.3)       # ends 0.02 mm above the outside: a touch exactly on it is not manifold
    rings = [p + (a - 0.3) * dirs + (h_in.min() - r - 0.5) * n]
    for phi in np.linspace(0.0, 0.5 * math.pi, RIM_STEPS + 1):
        # starts 0.05 mm inside the bore (its polygon lies only microns outside a small hole's circle) and ends r out
        rings.append(p + (a - 0.05 + (r + 0.05) * (1.0 - math.cos(phi))) * dirs + ((h_in - r) + rise * math.sin(phi))[:, None] * n)
    rings.append(p + (a + r) * dirs + (max(h_in.max(), h_out.max()) + HOLE_CUT_OUTSIDE_MM) * n)
    return meshutil.prism_from_rings(rings)


def rim_depth(cav, h) -> float:
    """How far the cavity wall under a hole lies below the hole centre, measured along the hole axis.

    On a curved wall the cavity surface at the rim of a hole is deeper than at its centre (by about
    radius^2 / (2 * curvature radius): more than 1 mm for a 13 mm hole near the end of a body). The hole
    cutter must reach below that, or a thin lip of plastic stays across the inner rim of the hole.
    """
    p, n = np.asarray(h.centre, float), np.asarray(h.axis, float)
    rel = cav.V - p
    ax = rel @ n
    rho = np.linalg.norm(rel - np.outer(ax, n), axis=1)
    near = (rho <= 0.5 * h.d_mm + 1.0) & (np.abs(ax) < 0.5 * h.d_mm + 4.0)
    return float(max(0.0, -ax[near].min())) if near.any() else 0.0


def cavity_height_fn(cav, v):
    """(xw, y) -> z of the chamber wall in the voicing frame, along the frame's normal; None where that line misses the
    chamber. The pocket blend of the voicing ends where it meets this surface (voicing_geo.build)."""
    tree = meshutil.bvh(cav.V, cav.F)
    o, fx, fy, fz = voicing_geo.voicing_frame(cav.math.port_frame())
    L, top = v.window_length_mm, 25.0

    def height(xw, y):
        hits = meshutil.ray_hits(tree, o + fx * (xw - L) + fy * y + fz * top, -fz, 80.0, limit=1)
        return top - hits[0][0] if hits else None
    return height


def cap_boxes(vs, v):
    """The two boxes that close the voicing side under the V0 convention, in body coordinates.

    k1  everything above the inner plane around the window: the throat, the ramp scoop, the windway roof side
    k2  the windway behind the exit plane, below the inner plane
    Both stop CAP_EPS_MM short of the cap planes, so they never share a face with the body.
    """
    L, W, wall = v.window_length_mm, v.window_width_mm, v.wall_at_window_mm
    reach = vs.info["ramp_reach_mm"]
    e = CAP_EPS_MM
    pitch = float(vs.info.get("windway_pitch_deg") or 0.0)
    rise = (v.windway_length_mm + L) * abs(math.sin(math.radians(pitch)))      # a turned windway leaves the level of the window
    k1 = meshutil.box_local(-L - v.windway_length_mm - 3.0, reach + 3.0, -(0.5 * W + reach + 3.0), 0.5 * W + reach + 3.0,
                            e, max(wall + 4.0, vs.info["z_top_mm"] + 3.0) + rise)
    zc = voicing_geo.windway_centre_z(v)
    k2 = meshutil.box_local(-L - v.windway_length_mm - 3.0, -L - voicing_geo.POCKET_BACK_OVERLAP_MM - e,
                            -(0.5 * W + 0.6), 0.5 * W + 0.6, zc - 0.5 * v.windway_inlet_height_mm - 0.2,
                            2 * e if not pitch else zc + 0.5 * v.windway_inlet_height_mm + 0.2)
    return [(meshutil.frame_points(k1[0], *vs.frame), k1[1]), (meshutil.frame_points(k2[0], *vs.windway_frame()), k2[1])]


def measure_capped_air_cm3(envelope, solid, vs, v, step: float = 0.25) -> float:
    """Capped air measured from the FINAL body mesh, without a Boolean.

    A point is capped air when it is inside the envelope (the skin joined with the voicing block, which
    closes every hole at the outer skin), outside the body's plastic, and not on the voicing side of the
    caps (cap_boxes). The volume of that set is integrated along columns parallel to the body's Z axis.
    """
    V = envelope[0]
    lo, hi = V.min(axis=0) - 1.0, V.max(axis=0) + 1.0
    I = np.eye(3)
    vol = meshutil.column_volume([envelope], [solid] + cap_boxes(vs, v), (0.0, 0.0, 0.0), I[0], I[1], I[2],
                                 (lo[0], hi[0], lo[1], hi[1]), step)
    return vol / 1000.0


def air_with_throat(capped, vs, v):
    """FEM air domain: the capped air joined with the window throat (the neck of the window), up to the outer face."""
    out = vs.outline
    L, wall = v.window_length_mm, v.wall_at_window_mm
    r0 = np.column_stack([out[:, 0], out[:, 1], np.full(len(out), -0.5)])
    r1 = np.column_stack([out[:, 0], out[:, 1], np.full(len(out), wall)])
    tV, tF = meshutil.prism_from_rings([r0, r1])
    tV[:, 0] -= L
    throat = (meshutil.frame_points(tV, *vs.frame), tF)
    fV, fF, _ = meshutil.boolean(capped, throat, "UNION")
    return fV, fF


def largest_shell(V, F):
    """Keep the connected surface with the largest volume; raise if another shell holds real volume."""
    parent = np.arange(V.shape[0])

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for tri in F:
        r0 = find(int(tri[0]))
        for j in (1, 2):
            r = find(int(tri[j]))
            if r != r0:
                parent[r] = r0
    roots = np.array([find(int(t[0])) for t in F])
    best, best_vol, others = None, -1.0, 0.0
    for r in np.unique(roots):
        vol = abs(meshutil.volume(V, F[roots == r]))
        if vol > best_vol:
            others += max(best_vol, 0.0)
            best, best_vol = r, vol
        else:
            others += vol
    if others > 5.0:
        raise meshutil.GeometryError(f"the capped air has loose pieces with {others:.1f} mm3 in total")
    Fk = F[roots == best]
    used = np.unique(Fk)
    remap = -np.ones(V.shape[0], dtype=np.int64)
    remap[used] = np.arange(len(used))
    return V[used], remap[Fk]


# ------------------------------------------------------------------ export, objects, summary

def export_body(body: BodyResult, export_dir: str) -> dict:
    """Write the STL files and the check results. A body whose voicing hash is not intact is never exported."""
    export_meshes(body, export_dir)
    write_checks_json(body, export_dir)
    return body.files


def export_meshes(body: BodyResult, export_dir: str) -> dict:
    """Write <id>.stl, <id>_air_capped.stl and <id>_air_fem.stl."""
    k = kernel_bridge.kernel()
    v = body.sizing.voicing
    if not (k.voicing.voicing_hash_of(v) == v.version_hash == body.voicing_hash):
        raise meshutil.GeometryError(f"{body.body_id}: the voicing hash is not intact; the body is not exported")
    os.makedirs(export_dir, exist_ok=True)
    bid = body.body_id
    files = {
        "stl": export.write_stl(os.path.join(export_dir, f"{bid}.stl"), *body.solid, header=f"ocarina {bid} body, mm"),
        "air_capped_stl": export.write_stl(os.path.join(export_dir, f"{bid}_air_capped.stl"), *body.air_capped,
                                           header=f"ocarina {bid} capped air (V0), mm"),
        "air_fem_stl": export.write_stl(os.path.join(export_dir, f"{bid}_air_fem.stl"), *body.air_fem,
                                        header=f"ocarina {bid} air with window throat, mm"),
    }
    body.files.update(files)
    return files


def write_checks_json(body: BodyResult, export_dir: str) -> str:
    """Write <id>_checks.json: the checks, the measurements and the Boolean log."""
    os.makedirs(export_dir, exist_ok=True)
    bid = body.body_id
    path = os.path.join(export_dir, f"{bid}_checks.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(dict(body_id=bid, preset=body.preset_id, v0_cm3=body.v0_cm3, voicing_hash=body.voicing_hash,
                       checks=body.checks, measurements=body.measurements, booleans=body.booleans), fh, indent=1,
                  default=_json_default)
    body.files["checks_json"] = path
    return path


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, tuple):
        return list(o)
    return str(o)


def make_objects(body: BodyResult, preset: dict) -> dict:
    """Put the result into the scene: the body mesh (with the voicing hash as a custom property), the air
    domain, and the procedural cavity object with its Geometry Nodes modifier."""
    import bpy
    names = {}
    ob = meshutil.object_from_arrays(f"OCA_{body.body_id}", *body.solid)
    ob["oca_body_id"] = body.body_id
    ob["oca_voicing_hash"] = body.voicing_hash          # voicing.version_hash, stored on the object
    ob["oca_voicing"] = json.dumps(body.sizing.voicing.to_dict())
    ob["oca_v0_cm3"] = body.v0_cm3
    ob["oca_preset"] = body.preset_id
    names["body"] = ob.name
    air = meshutil.object_from_arrays(f"OCA_{body.body_id}_air", *body.air_capped)
    air.display_type = "WIRE"
    names["air"] = air.name
    cav = cavity_mod.build_cavity(preset, body.cavity.target_volume_cm3, name=f"OCA_{body.body_id}_cavity", keep_object=True)
    bpy.data.objects[cav.object_name].display_type = "WIRE"
    names["cavity"] = cav.object_name
    body.object_names.update(names)
    return names


STATUS_MARKS = {"pass": "PASS", "needs_fem": "NEEDS FEM", "fail": "FAIL", "info": "INFO", "warn": "WARN"}


def format_summary(body: BodyResult) -> str:
    sz, v = body.sizing, body.sizing.voicing
    out = [f"{body.body_id}: {body.preset_id}, V0 {sz.v0_cm3:.2f} cm3, voicing {v.version_hash}",
           f"  window {v.shape} {v.window_length_mm:.2f} x {v.window_width_mm:.2f} mm, {v.window_area_mm2:.1f} mm2; "
           f"windway exit {v.windway_exit_height_mm:.2f} x {v.windway_width_mm:.2f} mm",
           f"  cavity length {body.cavity.length_mm:.2f} mm; cavity air (loft + pocket) {body.cavity_air_cm3:.4f} cm3 "
           f"(target {sz.cavity_volume_for_mesh_cm3:.4f}); capped air {body.air_capped_cm3:.4f} cm3 (V0 {sz.v0_cm3:.4f})"]
    for c in body.checks:
        mark = STATUS_MARKS.get(c["status"], c["status"])
        exp = " (expected)" if c.get("expected") else ""
        out.append(f"  {mark}{exp} {c['name']}: {c['message']}")
    for name, path in body.files.items():
        out.append(f"  file {name}: {path}")
    return "\n".join(out)
