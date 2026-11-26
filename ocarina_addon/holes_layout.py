"""Hole placement: where each of the 12 holes sits on the cavity, and along which axis it is cut.

Standard library only (it uses cavity_math and ergonomics, not Blender). Diameters, tubes and chimneys
come from the kernel; this module only decides positions.

Two layouts
    "template"   P1-P4. The eight finger holes and the two thumb holes take the Miracle AO10-AC spacing in
                 millimetres (Miracle_M.md section 4.2). The template is wrapped onto the body by ARC
                 LENGTH: along the top (or bottom) line of the body from the layout centre, then around
                 the section.
                 Subholes (docs/06 sections 3.2 and 5, owner decision of 2026-11-15): each subhole slides
                 from a named parent along the normal of its own hand's pinky -> index line, toward the
                 fingertips. sub1 (sub_L) from L_ring, 10 mm (9.5 mm until 2026-11-18), toward the player; sub2 (sub_R) from
                 R_middle, 7.5 mm, away from the player. Parent and slide are preset values. The normal is
                 taken in the plan view; the slide is the straight distance between the two hole centres.
                 Short decks (docs/06 section 3.5): the preset value `hand_overlap_mm` slides each hand
                 along its own line toward the other hand. The finger pitch is never compressed.
    "relative"   P0. The control egg is too short for the Miracle span, so it gets a compressed test
                 layout: a taped test body, not a hand layout. Positions are fractions of the spine
                 length, so the layout scales with the body and every P0 body has its holes at the same
                 relative places (the fitter shares one position factor per hole name over the P0 ladder).

Each hole axis is the outward normal of the cavity surface at the hole centre.

Edge gaps. The gap between two holes is the distance between their centres on the cavity surface minus
both radii. To keep MIN_GAP_MM a finger or thumb hole may move up to MAX_MOVE_MM along its row, and a
subhole slide may grow up to the largest slide (11 mm); a slide is never turned around. What is left
is reported, not hidden.

Sideways limit. A finger or thumb hole stays within SIDE_LIMIT of the half section from the deck line;
when that shortens a template offset, the layout says so in its messages. Subholes are not subject to
it: they are placed in the plan view and have their own limit (the deck must not lean more than
MAX_TILT_DEG where they sit), which is reported and never shortens the slide.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import cavity_math, ergonomics

MIN_GAP_MM = 3.4            # smallest edge-to-edge gap (the Miracle has 3.4 mm next to a subhole)
MAX_MOVE_MM = 2.0           # a centre may move this far along its row to keep the gap
MAX_TILT_DEG = 60.0         # a subhole must sit where the deck normal is within this angle of vertical
SIDE_LIMIT = 0.35           # finger and thumb holes: largest sideways offset, as a part of the half section
SUBHOLE_SLIDE_MAX_MM = 11.0  # a slide may grow to this to keep the edge gap (top of the ergo_subholes range)
# subhole: (parent, slide mm). Preset keys <sub>_parent and <sub>_slide_mm override them.
SUBHOLE_DEFAULTS = {"sub1": ("L_ring", 10.0), "sub2": ("R_middle", 7.5)}

# Miracle AO10-AC, section 4.2. x from the bulb end toward the tail, y from the far edge toward the player (mm).
MIRACLE = {
    "L_pinky": (13.0, 25.6), "L_ring": (30.1, 24.4), "L_middle": (47.3, 20.3), "L_index": (61.8, 11.1),
    "R_index": (67.0, 34.6), "R_middle": (82.5, 24.3), "R_ring": (100.1, 20.6), "R_pinky": (117.2, 20.3),
    "L_thumb": (23.2, 25.8), "R_thumb": (74.0, 21.2),          # back face, mirrored into the same frame
}
MIRACLE_CENTRE_X = 64.4      # between the two index holes: the layout centre
MIRACLE_REF_Y = 22.5         # the finger line that is laid on the top (and bottom) line of the body
THUMBS = ("L_thumb", "R_thumb")
SUBHOLES = ("sub1", "sub2")

# Compressed test layout of the control egg. (s, w) as fractions of the spine length: s along the top or
# bottom line from the middle of the body (negative = left-hand end), w toward the far side.
# Since 2026-11-18 the holes open in the Asian fingering order (docs/09 section 6.1), so six holes carry another
# note's diameter. This layout has no hand in it (the body is played with tape), so the PLACES were kept and the
# NAMES moved: each top-deck place holds a hole of the diameter it had before, or a smaller one. The place at
# the left-hand end, which had the A5 hole under the name L_pinky, has the A5 hole under the name L_ring; the
# B5 place is L_middle's, the C6 place L_index's, and L_pinky (now the F6 hole) has the place of the old D6
# hole. Every edge gap that was checked in C4 therefore still holds (4.0 mm or more at the print diameters on
# every P0 body from 65 to 125 cm3). The thumb places did not move: the left one has the D6 hole, the right
# one the E6 hole.
P0_RELATIVE = {
    "L_ring": (-0.395, -0.077), "L_middle": (-0.293, 0.089), "L_index": (-0.153, -0.051), "L_pinky": (-0.089, 0.153),
    "sub1": (-0.268, -0.077),
    "R_index": (0.102, -0.128), "R_middle": (0.217, 0.026), "R_ring": (0.319, -0.077), "R_pinky": (0.421, 0.038),
    "sub2": (0.128, 0.064),
    "L_thumb": (-0.280, 0.100), "R_thumb": (0.280, 0.100),
}


@dataclass
class HolePlacement:
    name: str
    deck: str                    # "top" (fingers) or "bottom" (thumbs)
    theta: float
    phi: float
    centre: tuple                # point on the cavity surface, body coordinates (mm)
    axis: tuple                  # unit outward normal there
    d_mm: float                  # diameter to cut (kernel)
    tube_mm: float               # inward tube length (kernel); 0 = none
    wall_mm: float               # wall along the axis (kernel)
    s_mm: float                  # position used: arc length along the deck line from the layout centre
    w_mm: float                  # arc length around the section, toward the far side
    s_nominal_mm: float          # position asked for by the layout, before any move
    w_nominal_mm: float
    moved_mm: float = 0.0        # distance between the nominal and the used centre
    tilt_deg: float = 0.0        # angle between the axis and the deck's vertical

    @property
    def chimney_mm(self) -> float:
        return self.wall_mm + self.tube_mm


@dataclass
class Layout:
    kind: str
    holes: list                              # HolePlacement, in the kernel's opening order
    overlap_mm: float = 0.0                  # template only: how far each hand was slid toward the other
    subholes: dict = field(default_factory=dict)      # template only: {name: dict(parent, slide_mm, slide_nominal_mm)}
    clamps: list = field(default_factory=list)        # (name, w asked, w used): sideways offsets that were limited
    gaps: list = field(default_factory=list)          # (name a, name b, gap mm), smallest first
    messages: list = field(default_factory=list)

    def by_name(self) -> dict:
        return {h.name: h for h in self.holes}

    @property
    def min_gap_mm(self) -> float:
        return self.gaps[0][2] if self.gaps else float("inf")


def _deck_of(name: str) -> str:
    return "bottom" if name in THUMBS else "top"


def _locate(cav: cavity_math.Cavity, theta_c: float, deck: str, s: float, w: float):
    """(theta, phi) of the point `s` mm along the deck line from theta_c and `w` mm toward the far side."""
    phi_ref = 0.5 * math.pi if deck == "top" else 1.5 * math.pi
    theta = cav.theta_at_meridian_arc(theta_c, s, phi_ref)
    # far side is +Y: smaller phi on the top, larger phi on the bottom
    phi = cav.phi_at_section_arc(theta, phi_ref, -w if deck == "top" else w)
    return theta, phi


def _tilt_deg(axis, deck: str) -> float:
    z = axis[2] if deck == "top" else -axis[2]
    return math.degrees(math.acos(max(-1.0, min(1.0, z))))


def _side_limit(cav, theta_c, deck, s):
    theta, _ = _locate(cav, theta_c, deck, s, 0.0)
    return SIDE_LIMIT * 0.5 * abs(cav.section_arc(theta, 0.0, math.pi))


def _place(cav, theta_c, name, s, w):
    """(theta, phi, w used) of a finger or thumb hole: the sideways offset is limited to SIDE_LIMIT."""
    deck = _deck_of(name)
    try:
        w_lim = _side_limit(cav, theta_c, deck, s)
    except ValueError as exc:
        raise ValueError(f"hole {name}: {exc}. The deck is too short for this layout: raise the preset value "
                         f"hand_overlap_mm or move layout_centre_from_port_mm") from None
    w_used = max(-w_lim, min(w_lim, w))
    theta, phi = _locate(cav, theta_c, deck, s, w_used)
    return theta, phi, w_used


def _template_nominal(overlap_mm: float = 0.0) -> dict:
    """Template positions (s, w) in mm about the layout centre, for the finger and thumb holes.

    overlap_mm slides each hand along its own pinky -> index line toward the other hand (its thumb hole
    goes with it). The distances inside one hand do not change.
    """
    out = {n: (x - MIRACLE_CENTRE_X, MIRACLE_REF_Y - y) for n, (x, y) in MIRACLE.items()}
    if overlap_mm:
        for hand in ("L", "R"):
            (s0, w0), (s1, w1) = out[f"{hand}_pinky"], out[f"{hand}_index"]
            ln = math.hypot(s1 - s0, w1 - w0)
            ds, dw = overlap_mm * (s1 - s0) / ln, overlap_mm * (w1 - w0) / ln
            for n in list(out):
                if n.startswith(hand + "_"):
                    out[n] = (out[n][0] + ds, out[n][1] + dw)
    return out


def _surface_over(cav: cavity_math.Cavity, x: float, y: float, theta: float, phi: float):
    """(theta, phi) of the point of the finger deck that lies over the plan position (x, y). Newton steps
    from the start values. Raises ValueError when the position is off the deck."""
    for _ in range(60):
        p = cav.point(theta, phi)
        ex, ey = x - p[0], y - p[1]
        if math.hypot(ex, ey) < 1e-8:
            return theta, phi
        du, dv = cav.d_theta(theta, phi), cav.d_phi(theta, phi)
        det = du[0] * dv[1] - du[1] * dv[0]
        if abs(det) < 1e-9:
            break
        dth = (ex * dv[1] - ey * dv[0]) / det
        dph = (du[0] * ey - du[1] * ex) / det
        theta = min(max(theta + max(-0.15, min(0.15, dth)), 1e-3), math.pi - 1e-3)
        phi = phi + max(-0.25, min(0.25, dph))
        if not 0.03 < phi < math.pi - 0.03:
            break
    raise ValueError(f"the plan position ({x:.1f}, {y:.1f}) mm is not on the finger deck")


def _slide_point(cav, P_plan: dict, parent, sub_hand: str, slide_mm: float):
    """Where a subhole sits: `slide_mm` (straight distance between the centres) from the parent hole, in the
    plan view along the normal of the hand line of `sub_hand`, toward that hand's fingertips.
    P_plan: finger hole centres in the player frame (x, -y). Returns (theta, phi)."""
    _, nrm = ergonomics.fingertip_normal(P_plan, sub_hand)
    px, py = P_plan[parent.name]
    t = slide_mm
    theta, phi = parent.theta, parent.phi
    for _ in range(30):
        theta, phi = _surface_over(cav, px + t * nrm[0], -(py + t * nrm[1]), parent.theta, parent.phi)
        d = cavity_math._dist(cav.point(theta, phi), parent.centre)
        if abs(d - slide_mm) < 1e-6:
            break
        t *= slide_mm / d
    return theta, phi


def with_rows(layout: "Layout", hole_rows, min_gap_mm: float = MIN_GAP_MM) -> "Layout":
    """The same hole positions with other diameters, tubes and walls (kernel rows in the same order).

    Stage 3 uses it: the corrected holes of round 2 stay where the round-1 holes were (doc 04 D10: positions
    never change after the first prints). The edge gaps are computed again for the new diameters; a gap under
    the limit is reported in the messages and nothing is moved."""
    rows = {r.name: r for r in hole_rows}
    holes = []
    for h in layout.holes:
        r = rows[h.name]
        holes.append(HolePlacement(name=h.name, deck=h.deck, theta=h.theta, phi=h.phi, centre=h.centre, axis=h.axis,
                                   d_mm=r.d_mm, tube_mm=r.tube_mm, wall_mm=r.wall_mm, s_mm=h.s_mm, w_mm=h.w_mm,
                                   s_nominal_mm=h.s_nominal_mm, w_nominal_mm=h.w_nominal_mm, moved_mm=h.moved_mm,
                                   tilt_deg=h.tilt_deg))
    gaps = sorted(((a.name, b.name, cavity_math._dist(a.centre, b.centre) - 0.5 * (a.d_mm + b.d_mm))
                   for i, a in enumerate(holes) for b in holes[i + 1:]), key=lambda t: t[2])
    messages = [m for m in layout.messages if not m.startswith("edge gap ")]
    messages.append("the hole positions are those of the round-1 layout; only the diameters changed (doc 04 D10)")
    messages += [f"edge gap {a} to {b} is {gap:.2f} mm, under {min_gap_mm:.1f} mm, with the new diameters at the round-1 positions"
                 for a, b, gap in gaps if gap < min_gap_mm - 1e-6]
    return Layout(kind=layout.kind, holes=holes, overlap_mm=layout.overlap_mm, subholes=layout.subholes,
                  clamps=layout.clamps, gaps=gaps, messages=messages)


def make_layout(cav: cavity_math.Cavity, preset: dict, hole_rows, min_gap_mm: float = MIN_GAP_MM,
                slide_max_mm: float = SUBHOLE_SLIDE_MAX_MM) -> Layout:
    """Place the holes of `hole_rows` (kernel HoleResult list, opening order) on the cavity `cav`."""
    names = [h.name for h in hole_rows]
    rows = {h.name: h for h in hole_rows}
    kind = preset.get("layout", "template")
    messages, clamps, sub_rule, slide, overlap = [], {}, {}, {}, 0.0
    if kind == "none" or not names:                      # a voicing stub: no holes
        return Layout(kind="none", holes=[])
    if kind == "relative":
        L = cav.length_mm
        theta_c = 0.5 * math.pi
        nominal = {n: (P0_RELATIVE[n][0] * L, P0_RELATIVE[n][1] * L) for n in names}
        placed_by_rule = []
    elif kind == "template":
        centre_from_port = float(preset.get("layout_centre_from_port_mm", 16.0))
        theta_c = cav.theta_at_meridian_arc(cav.port_theta, centre_from_port, 0.5 * math.pi)
        overlap = float(preset.get("hand_overlap_mm", 0.0))
        nominal = _template_nominal(overlap)
        if overlap:
            messages.append(f"each hand was slid {overlap:g} mm along its own line toward the other hand (preset value "
                            f"hand_overlap_mm); the finger pitch is unchanged")
        for n, (ds, dw) in (preset.get("thumb_offsets_mm") or {}).items():
            # an option (2026-11-26, low-voicing experiment's night_thumbs): a thumb hole moved in the template's own deck
            # coordinates, s along the hand axis (+ toward the tail), w across it. AN ERGONOMIC CHANGE, said in the report.
            if n not in ("L_thumb", "R_thumb"):
                raise ValueError(f"thumb_offsets_mm: {n!r} is not a thumb hole (L_thumb, R_thumb)")
            nominal[n] = (nominal[n][0] + float(ds), nominal[n][1] + float(dw))
            messages.append(f"MOVED THUMB HOLE (an ergonomic change): {n} moved {float(ds):+g} mm along the hand axis "
                            f"(+ toward the tail) and {float(dw):+g} mm across it (preset value thumb_offsets_mm)")
        placed_by_rule = [n for n in names if n in SUBHOLES]
        for sub in placed_by_rule:
            parent = str(preset.get(f"{sub}_parent", SUBHOLE_DEFAULTS[sub][0]))
            if parent not in ergonomics.FINGERS:
                raise ValueError(f"{sub}_parent = {parent!r} is not a finger hole")
            asked = float(preset.get(f"{sub}_slide_mm", SUBHOLE_DEFAULTS[sub][1]))
            if asked > slide_max_mm:
                raise ValueError(f"{sub}_slide_mm = {asked:g} is above the largest slide, {slide_max_mm:g} mm")
            sub_rule[sub] = dict(parent=parent, hand=parent[0], slide_nominal_mm=asked)
            slide[sub] = asked
    else:
        raise ValueError(f"unknown layout kind {kind!r}")

    pos = {n: nominal[n] for n in names if n not in placed_by_rule}

    def make(n, theta, phi, s, w, s0, w0):
        r = rows[n]
        axis = cav.normal(theta, phi)
        return HolePlacement(name=n, deck=_deck_of(n), theta=theta, phi=phi, centre=cav.point(theta, phi), axis=axis,
                             d_mm=r.d_mm, tube_mm=r.tube_mm, wall_mm=r.wall_mm, s_mm=s, w_mm=w, s_nominal_mm=s0,
                             w_nominal_mm=w0, tilt_deg=_tilt_deg(axis, _deck_of(n)))

    def sw_of(theta, phi):
        """Deck coordinates (s, w) of a point of the finger deck, for the record."""
        s = cav.meridian_arc(theta_c, theta, 0.5 * math.pi)
        return s, -cav.section_arc(theta, 0.5 * math.pi, phi)

    def build(slides):
        by = {}
        clamps.clear()
        for n in pos:
            theta, phi, w_used = _place(cav, theta_c, n, *pos[n])
            if abs(w_used - pos[n][1]) > 0.05:
                clamps[n] = (pos[n][1], w_used)
            by[n] = make(n, theta, phi, pos[n][0], w_used, *nominal[n])
        if placed_by_rule:
            P_plan = {n: ergonomics.body_to_player(by[n].centre)[:2] for n in ergonomics.FINGERS}
            for sub in placed_by_rule:
                rule = sub_rule[sub]
                theta, phi = _slide_point(cav, P_plan, by[rule["parent"]], rule["hand"], slides[sub])
                s, w = sw_of(theta, phi)
                by[sub] = make(sub, theta, phi, s, w, s, w)
        return [by[n] for n in names]

    def gaps_of(holes):
        g = []
        for i, a in enumerate(holes):
            for b in holes[i + 1:]:
                g.append((a.name, b.name, cavity_math._dist(a.centre, b.centre) - 0.5 * (a.d_mm + b.d_mm)))
        return sorted(g, key=lambda t: t[2])

    def move_along_row(n, sign, amount):
        s_new = pos[n][0] + sign * amount
        s_new = max(nominal[n][0] - MAX_MOVE_MM, min(nominal[n][0] + MAX_MOVE_MM, s_new))
        if abs(s_new - pos[n][0]) > 1e-9:
            pos[n] = (s_new, pos[n][1])
            return True
        return False

    holes = build(slide)
    nominal_centres = {h.name: h.centre for h in holes}          # before any move, for the record of moves
    for h in holes:
        if h.name in placed_by_rule:
            h.s_nominal_mm, h.w_nominal_mm = h.s_mm, h.w_mm
    sub_nominal_sw = {h.name: (h.s_mm, h.w_mm) for h in holes if h.name in placed_by_rule}
    for _ in range(40):                                   # relax: push violating pairs apart
        bad = [g for g in gaps_of(holes) if g[2] < min_gap_mm - 1e-6]
        if not bad:
            break
        by = {h.name: h for h in holes}
        moved_any = False
        for a, b, gap in bad:
            deficit = min_gap_mm - gap + 0.05
            subs = [n for n in (a, b) if n in placed_by_rule]
            if len(subs) == 1:
                sub, other = subs[0], (b if subs[0] == a else a)
                # A longer slide helps when it moves the subhole away from the other hole.
                trial = dict(slide, **{sub: min(slide[sub] + 0.5, slide_max_mm + 0.5)})
                try:
                    t = {h.name: h for h in build(trial)}
                    helps = cavity_math._dist(t[sub].centre, t[other].centre) > cavity_math._dist(by[sub].centre, by[other].centre) + 0.05
                except ValueError:
                    helps = False
                if helps and slide[sub] < slide_max_mm - 1e-9:
                    slide[sub] = min(slide[sub] + deficit, slide_max_mm)
                    moved_any = True
                    continue
                if other != sub_rule[sub]["parent"]:      # the parent carries its subhole: moving it does not help
                    moved_any |= move_along_row(other, 1.0 if by[other].s_mm >= by[sub].s_mm else -1.0, deficit)
                continue
            if subs:                                       # two subholes: lengthen both
                for sub in subs:
                    if slide[sub] < slide_max_mm - 1e-9:
                        slide[sub] = min(slide[sub] + 0.5 * deficit, slide_max_mm)
                        moved_any = True
                continue
            sign = 1.0 if pos[a][0] >= pos[b][0] else -1.0
            for n, sg in ((a, sign), (b, -sign)):
                moved_any |= move_along_row(n, sg, 0.5 * (min_gap_mm - gap) + 0.05)
        holes = build(slide)
        if not moved_any:
            break
    for h in holes:
        h.moved_mm = cavity_math._dist(h.centre, nominal_centres[h.name])
        if h.name in sub_nominal_sw:
            h.s_nominal_mm, h.w_nominal_mm = sub_nominal_sw[h.name]
    by = {h.name: h for h in holes}
    subholes = {}
    for sub in placed_by_rule:
        rule, h = sub_rule[sub], by[sub]
        used = cavity_math._dist(h.centre, by[rule["parent"]].centre)
        subholes[sub] = dict(parent=rule["parent"], slide_mm=used, slide_nominal_mm=rule["slide_nominal_mm"])
        if used > rule["slide_nominal_mm"] + 1e-6:
            messages.append(f"{sub}: the slide from {rule['parent']} was lengthened from {rule['slide_nominal_mm']:g} to "
                            f"{used:.2f} mm to keep the {min_gap_mm:g} mm edge gap (largest slide {slide_max_mm:g} mm)")
        if h.tilt_deg > MAX_TILT_DEG:
            messages.append(f"{sub}: the deck leans {h.tilt_deg:.0f}° where the subhole sits (limit {MAX_TILT_DEG:g}°); "
                            f"the slide was not shortened")
    for n, (asked, used) in clamps.items():
        messages.append(f"{n}: the sideways offset was limited from {asked:+.1f} to {used:+.1f} mm "
                        f"({100 * SIDE_LIMIT:.0f} % of the half section there)")
    gaps = gaps_of(holes)
    for a, b, gap in gaps:
        if gap < min_gap_mm - 1e-6:
            messages.append(f"edge gap {a} to {b} is {gap:.2f} mm, under {min_gap_mm:.1f} mm, after the allowed moves")
    return Layout(kind=kind, holes=holes, overlap_mm=overlap, subholes=subholes,
                  clamps=[(n, a, u) for n, (a, u) in clamps.items()], gaps=gaps, messages=messages)
