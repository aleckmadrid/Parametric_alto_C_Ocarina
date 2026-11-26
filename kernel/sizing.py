"""Top-level sizing: one call returns the voicing, the holes, the tubes and the checks for a body.

    import sizing
    body = sizing.size_body(80.0, rating="medium")          # P0 default, plain generated test body
    body.holes.solutions["print"]                            # diameters at k_hole 0.8 (what is printed)
    body.holes.solutions["nominal"]                          # diameters at k_hole 1.0

Command line (regenerates the doc 04 table):

    python kernel/sizing.py --table                          # the five steps of docs/04, plain-wall holes
    python kernel/sizing.py --v0 80 --holes                  # every hole, k 0.8 and k 1.0, with tubes
    python kernel/sizing.py --v0 65 80 --rating loud --json

Everything here is pre-calibration: eta_w = 0.90, k_hole prior 1.0.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import sys
from dataclasses import dataclass, field

import checks
import config
import holes as holes_mod
import ocarina_kernel as ok
import voicing as voicing_mod

MM = 1e-3
CM3 = 1e-6


@dataclass
class BodySizing:
    v0_cm3: float                       # capped air volume, all holes closed (the acoustic target)
    voicing: voicing_mod.Voicing
    internal_temp_c: float
    c_m_s: float
    notes: list
    f_targets_hz: list
    eta_w: float                        # eta_w used for X_w
    X_w_mm: float                       # eta_w * G_w, mm
    a4_error_cents: float               # all-closed note against A4 (0 unless V0 and window are both fixed)
    holes: holes_mod.HoleSizing
    checks: list                        # list[checks.CheckResult]
    range_ratio: float                  # sum(G_i) / (eta_w G_w)
    window_area_over_v0_23: float       # window area / V0^(2/3), dimensionless (area in mm^2, V0 in mm^3)
    p0_length_mm: float                 # internal length of the P0 control egg (2.2 : 1.5 : 1) at this V0
    volume_factor: float = 1.0
    hole_offset_mm: float = 0.0
    # Volume bookkeeping (doc 03 section 1: V0 is the capped air, every chimney included).
    #   V0 = V_cavity_mesh - tube_plastic + sum(A_i * wall_i)
    # so the cavity mesh, before the tubes are added and before the holes are cut, must hold
    #   V_cavity_mesh = (V0 + tube_plastic - sum(A_i * wall_i)) / volume_factor.
    # Areas are those of the floor-key solution (the diameters that are really built).
    cavity_volume_for_mesh_cm3: float = 0.0
    wall_chimney_air_cm3: float = 0.0         # sum(A_i * wall_i): air in the plain holes through the wall
    tube_plastic_cm3: float = 0.0             # plastic of the inward tube walls (displaces cavity air)
    L_int_mm_used: float = 0.0                # internal length behind the cavity-mode check
    L_int_source: str = ""                    # "P0 egg" (default) or "caller"
    cad_diameters_mm: dict = field(default_factory=dict)   # key -> diameter to draw in CAD = d - hole_offset

    def to_dict(self) -> dict:
        return {
            "v0_cm3": self.v0_cm3, "voicing": self.voicing.to_dict(), "internal_temp_c": self.internal_temp_c,
            "c_m_s": self.c_m_s, "notes": self.notes, "f_targets_hz": self.f_targets_hz, "eta_w": self.eta_w,
            "X_w_mm": self.X_w_mm, "a4_error_cents": self.a4_error_cents, "holes": self.holes.to_dict(),
            "checks": [c.to_dict() for c in self.checks], "range_ratio": self.range_ratio,
            "window_area_over_v0_23": self.window_area_over_v0_23, "p0_length_mm": self.p0_length_mm,
            "volume_factor": self.volume_factor, "hole_offset_mm": self.hole_offset_mm,
            "cavity_volume_for_mesh_cm3": self.cavity_volume_for_mesh_cm3,
            "wall_chimney_air_cm3": self.wall_chimney_air_cm3, "tube_plastic_cm3": self.tube_plastic_cm3,
            "L_int_mm_used": self.L_int_mm_used, "L_int_source": self.L_int_source,
            "cad_diameters_mm": self.cad_diameters_mm,
        }

    @property
    def all_ok(self) -> bool:
        return all(c.ok for c in self.checks)


def size_body(v0_cm3: float | None = None, rating: str | None = None, wall_at_window_mm: float | None = None,
              labium_offset_mm: float | None = None, *, params: dict | None = None,
              voicing: voicing_mod.Voicing | None = None, eta_w: float | None = None, shape: str | None = None,
              ks: dict | None = None, floor_key: str | None = None, psi=None, tubes_mm=None,
              volume_factor: float = 1.0, hole_offset_mm: float = 0.0, L_int_mm: float | None = None,
              internal_temp_c: float | None = None, wall_at_holes_mm=None, throat_mm: float | None = None) -> BodySizing:
    """Size one body.

    Normal use: size_body(v0_cm3, rating). The window area is solved from V0 with the eta_w prior.

    Fixed-voicing use (Stage 3): pass `voicing` (a printed voicing), `eta_w` (fitted for its hash), and
    either `v0_cm3` (keep that volume; A4 then errs by a_four_error_cents) or no v0 (retarget: V0 is
    solved so that A4 is on pitch).

    ks         dict label -> k_hole. Default {"print": 0.8, "nominal": 1.0}.
    floor_key  which k decides the inward tubes. Default: the first key ("print").
    psi        position factor per hole (default 1).
    tubes_mm   fixed inward tube lengths per hole; skips the tube rule.
    volume_factor, hole_offset_mm
               calibration. volume_factor = printed / designed cavity volume. hole_offset_mm = printed minus
               designed diameter. They change only the mesh volume and the CAD diameters reported, never the
               acoustic numbers.
    L_int_mm   internal length for the cavity-mode check. Default: the P0 egg length at this V0.
               A caller that builds P1-P3 MUST pass the real internal length; the result records
               which length was used (L_int_mm_used, L_int_source).
    wall_at_holes_mm
               the wall along each hole axis. Default: [hole_rules].wall_at_holes_mm for every hole. A number,
               a dict (hole name -> mm) or a list in opening order (holes.hole_specs_from_params). A body whose
               shell was edited passes the wall it measured at each hole; the window and V0 do not change.
    """
    P = params if params is not None else config.load_params()
    D, R, H = P["design"], P["voicing_rules"], P["hole_rules"]
    # throat_mm (an option, 2026-11-26): the window's conductance taken with this effective throat
    # (voicing.effective_wall_mm, for walls that flare into a bowl) instead of the wall. The window stays the one the
    # rule gives at v0_cm3 (or the given voicing), so V0 is solved again: A4 on pitch with that conductance.
    if ks is None:
        ks = {"print": H["print_k_hole"], "nominal": H["nominal_k_hole"]}
    T = internal_temp_c if internal_temp_c is not None else D["design_air_temp_c"]
    c = ok.c_air(T)
    notes_midi = D["notes_midi"]
    f_targets = [ok.midi_f(m, D["a4_hz"]) for m in notes_midi]
    f0 = f_targets[0]
    eta = float(eta_w if eta_w is not None else R["eta_w_prior"])

    if voicing is None:
        if v0_cm3 is None:
            raise ValueError("give v0_cm3 (or a voicing)")
        vo = voicing_mod.make_voicing(v0_cm3, rating, wall_at_window_mm, labium_offset_mm, eta_w=eta,
                                      shape=shape, params=P, internal_temp_c=T)
    else:
        vo = voicing
    X_w = eta * (vo.G_w() if throat_mm is None else ok.conductance(vo.window_area_m2, float(throat_mm) * MM, ok.K_WINDOW))
    if v0_cm3 is None or throat_mm is not None:
        V0 = ok.volume_for(X_w, f0, c)
    else:
        V0 = v0_cm3 * CM3
    a4_err = ok.cents(ok.freq(X_w, V0, c), f0)

    specs = holes_mod.hole_specs_from_params(P, wall_at_holes_mm)
    sizing = holes_mod.size_holes(
        f_targets, X_w, V0, specs, ks, c, floor_key=floor_key, psi=psi, tubes_mm=tubes_mm,
        tube_step_mm=H["tube_step_mm"], tube_max_mm=H["tube_max_mm"], tube_wall_mm=H["tube_wall_mm"])

    first = sizing.solutions[sizing.floor_key]
    sumG = sum(h.G_mm for h in first) * MM
    rr = checks.range_ratio_check(sumG, X_w, P["constraints"]["range_ratio_max"])
    L_int = (L_int_mm * MM) if L_int_mm is not None else checks.ellipsoid_length_m(V0)
    L_source = "caller" if L_int_mm is not None else "P0 egg"
    cm = checks.cavity_mode_check(L_int, f_targets[-1], c, P["constraints"]["cavity_mode_margin"],
                                  P["constraints"]["cavity_mode_fem_margin"])
    results = [rr, cm] + vo.checks()
    for key, rows in sizing.solutions.items():
        bad = [h for h in rows if h.below_floor or h.above_pad_limit]
        if bad:
            why = "; ".join(
                f"{h.name} {h.d_mm:.2f} mm " + ("below the floor" if h.below_floor else f"above the {h.max_d_mm:.0f} mm pad limit")
                for h in bad)
            results.append(checks.CheckResult(f"hole_limits[{key}]", "fail", float(len(bad)), 0.0, why))
        else:
            results.append(checks.CheckResult(f"hole_limits[{key}]", "pass", 0.0, 0.0, "all holes inside floor and pad limits"))
    if sizing.capped:
        results.append(checks.CheckResult("tube_length", "fail", sizing.tube_wall_displacement_cm3, H["tube_max_mm"],
                                          "tube capped at the maximum, hole still under the floor: " + ", ".join(sizing.capped)))

    area_over = vo.window_area_mm2 / (V0 / 1e-9) ** (2.0 / 3.0)
    wall_air = sum(h.area_mm2 * MM * MM * h.wall_mm * MM for h in first)      # m^3
    plastic = sum(holes_mod.tube_wall_displacement_m3(h.d_mm * MM, h.tube_mm * MM, H["tube_wall_mm"] * MM)
                  for h in first if h.tube_mm > 0)
    cad = {key: [h.d_mm - hole_offset_mm for h in rows] for key, rows in sizing.solutions.items()}
    return BodySizing(
        v0_cm3=V0 / CM3, voicing=vo, internal_temp_c=T, c_m_s=c, notes=D["notes"], f_targets_hz=f_targets,
        eta_w=eta, X_w_mm=X_w / MM, a4_error_cents=a4_err, holes=sizing, checks=results,
        range_ratio=rr.value, window_area_over_v0_23=area_over, p0_length_mm=checks.ellipsoid_length_m(V0) / MM,
        volume_factor=volume_factor, hole_offset_mm=hole_offset_mm,
        cavity_volume_for_mesh_cm3=(V0 + plastic - wall_air) / CM3 / volume_factor,
        wall_chimney_air_cm3=wall_air / CM3, tube_plastic_cm3=plastic / CM3,
        L_int_mm_used=L_int / MM, L_int_source=L_source, cad_diameters_mm=cad)


def cad_diameter_mm(printed_target_mm: float, hole_offset_mm: float) -> float:
    """CAD diameter that prints to the wanted diameter, given the fitted offset (printed minus designed)."""
    return printed_target_mm - hole_offset_mm


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

LABELS = {"sub1": "sub_L", "sub2": "sub_R"}     # doc 04 names for the subholes
DOC04_STEPS = (65.0, 80.0, 88.0, 95.0)      # ladder 65 / 80 / 95 and the P0-88 prediction body


def _label(name: str) -> str:
    return LABELS.get(name, name)


def _hole_by_name(rows, name):
    return next(h for h in rows if h.name == name)


def _hole_by_note(rows, note):
    """The hole that opens `note`. The doc 04 table shows the two largest holes by the note they open (D6, E6),
    so that its numbers do not depend on which finger the fingering system gives them to."""
    return next(h for h in rows if h.opens == note)


def table_row_doc04(b: BodySizing) -> list:
    """One row of the doc 04 table: plain-wall diameters at the nominal k."""
    v = b.voicing
    shape = "Teardrop" if v.shape == "teardrop" else "Rounded rectangle"
    nominal = b.holes.solutions["nominal"]
    return [
        f"{b.v0_cm3:.0f} cm³",
        f"{shape} {v.window_length_mm:.2f} × {v.window_width_mm:.1f} mm, {v.window_area_mm2:.0f} mm²",
        f"{v.windway_exit_height_mm:.1f} × {v.windway_width_mm:.1f} mm",
        f"{_hole_by_name(nominal, 'sub2').d_plain_mm:.1f} mm",
        f"{_hole_by_note(nominal, 'D6').d_plain_mm:.1f} mm",
        f"{_hole_by_note(nominal, 'E6').d_plain_mm:.1f} mm",
        f"{b.p0_length_mm:.0f} mm",
        f"{b.window_area_over_v0_23:.3f}",
    ]


def format_doc04_table(bodies) -> str:
    head = ["V0", "Window", "Windway", "sub_R", "D6 thumb (L)", "E6 thumb (R)", "P0 length", "Window area / V0^(2/3)"]
    lines = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    for b in bodies:
        lines.append("| " + " | ".join(table_row_doc04(b)) + " |")
    return "\n".join(lines)


def format_holes_table(b: BodySizing) -> str:
    pr, nom = b.holes.solutions["print"], b.holes.solutions["nominal"]
    head = ["Hole", "Opens", "Plain wall k 1.0 mm", "Tube mm", "Chimney mm", "Print d (k 0.8) mm",
            "Nominal d (k 1.0) mm", "G mm", "Pad limit mm", "Flags"]
    lines = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    for p, n in zip(pr, nom):
        flags = []
        if n.above_pad_limit:
            flags.append("k1.0 above pad limit")
        if p.above_pad_limit:
            flags.append("k0.8 above pad limit")
        if p.below_floor:
            flags.append("below floor")
        lines.append("| " + " | ".join([
            _label(p.name), p.opens, f"{n.d_plain_mm:.2f}", f"{p.tube_mm:.1f}", f"{p.chimney_mm:.1f}",
            f"{p.d_mm:.2f}", f"{n.d_mm:.2f}", f"{p.G_mm:.3f}", f"{p.max_d_mm:.0f}", ", ".join(flags) or "ok"]) + " |")
    return "\n".join(lines)


def format_body(b: BodySizing) -> str:
    v = b.voicing
    out = [f"### V0 = {b.v0_cm3:.1f} cm³, {v.rating} window (hash `{v.version_hash}`)", ""]
    out.append(f"- Window: {v.shape.replace('_', ' ')}, length {v.window_length_mm:.2f} mm, width {v.window_width_mm:.2f} mm, "
               f"area {v.window_area_mm2:.1f} mm², wall {v.wall_at_window_mm:.1f} mm. eta_w {b.eta_w:.2f}, "
               f"eta_w·G_w {b.X_w_mm:.3f} mm.")
    out.append(f"- Windway: exit {v.windway_exit_height_mm:.2f} mm, inlet {v.windway_inlet_height_mm:.2f} mm, width "
               f"{v.windway_width_mm:.2f} mm, length {v.windway_length_mm:.0f} mm; W/h {v.wh_ratio:.2f}. "
               f"Labium {v.labium_ramp_angle_deg:.0f}°, edge {v.labium_edge_thickness_mm:.1f} mm, offset {v.labium_offset_mm:+.1f} mm.")
    out.append("- Build: plain (fan cut, level windway, box stub, no pocket blend)." if v.is_plain_build else
               f"- Build (in the hash): {v.window_cut} cut, {v.cut_widen_mm:g} mm per side, shelf {v.shelf_angle_deg:g}°; windway "
               f"{v.windway_pitch_deg:+g}° against the body; {v.stub_style} stub at {v.stub_pitch_deg:+g}°; pocket blend "
               f"{v.pocket_blend_radius_mm:g} mm.")
    out.append(f"- Air at {b.internal_temp_c:.1f} °C: c = {b.c_m_s:.1f} m/s. P0 egg length {b.p0_length_mm:.0f} mm. "
               f"Cavity mesh volume {b.cavity_volume_for_mesh_cm3:.2f} cm³ (V0 minus {b.wall_chimney_air_cm3:.2f} cm³ of air in the holes, "
               f"plus {b.tube_plastic_cm3:.2f} cm³ of tube wall). Cavity-mode length {b.L_int_mm_used:.0f} mm ({b.L_int_source}).")
    out.append("")
    out.append(format_holes_table(b))
    out.append("")
    for c_ in b.checks:
        mark = {"pass": "PASS", "needs_fem": "NEEDS FEM", "fail": "FAIL"}[c_.status]
        out.append(f"- {mark} `{c_.name}`: {c_.message}")
    out.append("")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Print the sizing of generated test bodies (pre-calibration).")
    ap.add_argument("--v0", type=float, nargs="*", help="target V0 in cm³ (default: the doc 04 steps 65, 80, 88, 95)")
    ap.add_argument("--rating", default=None, choices=["soft", "medium", "loud"], help="voice rating (default medium)")
    ap.add_argument("--wall", type=float, default=None, help="wall at the window in mm: 4.0 (default) or 3.0")
    ap.add_argument("--labium-offset", type=float, default=None,
                    help="labium offset in mm: -0.2 (default), or the coupons 0 and -0.35; negative = edge below the jet centre")
    ap.add_argument("--eta-w", type=float, default=None, help="window efficiency (default: prior 0.90)")
    ap.add_argument("--temp", type=float, default=None, help="internal air temperature in °C (default 27)")
    ap.add_argument("--table", action="store_true", help="print the doc 04 table (plain-wall holes at k 1.0)")
    ap.add_argument("--holes", action="store_true", help="print the per-hole table, voicing and checks")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--params", default=None, help="path to a parameter TOML (default params/alto_c_12hole.toml)")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    P = config.load_params(args.params)
    v0s = args.v0 if args.v0 else list(DOC04_STEPS)
    bodies = [size_body(v, args.rating, args.wall, args.labium_offset, params=P, eta_w=args.eta_w,
                        internal_temp_c=args.temp) for v in v0s]
    if args.json:
        print(json.dumps([b.to_dict() for b in bodies], indent=2))
        return 0
    if args.table or not args.holes:
        print("Plain-wall holes at k_hole = 1.0 (the numbers of docs/04-testing-phase.md); pre-calibration.")
        print()
        print(format_doc04_table(bodies))
        print()
    if args.holes:
        for b in bodies:
            print(format_body(b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
