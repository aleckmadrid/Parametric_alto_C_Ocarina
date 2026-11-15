"""Hole placement: where each of the 12 holes sits on the cavity, and along which axis it is cut.

Standard library only (it uses cavity_math, not Blender). Diameters, tubes and chimneys come from the
kernel; this module only decides positions.

Two layouts
    "template"   P1-P3. Miracle AO10-AC finger spacing in millimetres (Miracle_M.md section 4.2), with one
                 subhole per hand in the ECAN3 position (doc 04, D5): sub_L (kernel name sub1) between
                 L_ring and L_middle, sub_R (kernel name sub2) between R_index and R_middle, both off the
                 finger line, on the far side. The template is wrapped onto the body by ARC LENGTH: along
                 the top (or bottom) line of the body from the layout centre, then around the section.
    "relative"   P0. The control egg is too short for the Miracle span, so it gets a compressed test
                 layout. Positions are fractions of the spine length, so the layout scales with the body
                 and every P0 body has its holes at the same relative places (the fitter shares one
                 position factor per hole name over the P0 ladder).

Each hole axis is the outward normal of the cavity surface at the hole centre.

Edge gaps. The gap between two holes is the distance between their centres on the cavity surface
minus both radii. A hole may move up to MAX_MOVE_MM along its row to keep MIN_GAP_MM; a subhole may
also move further off the finger line. What is left is reported, not hidden.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import cavity_math

MIN_GAP_MM = 3.4            # smallest edge-to-edge gap (the Miracle has 3.4 mm next to a subhole)
MAX_MOVE_MM = 2.0           # a centre may move this far along its row to keep the gap
MAX_TILT_DEG = 60.0         # template only: holes stay where the deck normal is within this angle of vertical
SUBHOLE_OFFSET_MM = (6.0, 12.0)   # subhole distance from the finger line: start value and largest value

# Miracle AO10-AC, section 4.2. x from the bulb end toward the tail, y from the far edge toward the player (mm).
MIRACLE = {
    "L_pinky": (13.0, 25.6), "L_ring": (30.1, 24.4), "L_middle": (47.3, 20.3), "L_index": (61.8, 11.1),
    "R_index": (67.0, 34.6), "R_middle": (82.5, 24.3), "R_ring": (100.1, 20.6), "R_pinky": (117.2, 20.3),
    "L_thumb": (23.2, 25.8), "R_thumb": (74.0, 21.2),          # back face, mirrored into the same frame
}
MIRACLE_CENTRE_X = 64.4      # between the two index holes: the layout centre
MIRACLE_REF_Y = 22.5         # the finger line that is laid on the top (and bottom) line of the body
THUMBS = ("L_thumb", "R_thumb")
SUBHOLES = {"sub1": ("L_ring", "L_middle"), "sub2": ("R_index", "R_middle")}

# Compressed test layout of the control egg. (s, w) as fractions of the spine length: s along the top or
# bottom line from the middle of the body (negative = left-hand end), w toward the far side.
P0_RELATIVE = {
    "L_index": (-0.089, 0.153), "L_middle": (-0.153, -0.051), "L_ring": (-0.293, 0.089), "L_pinky": (-0.395, -0.077),
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
    compression: dict = field(default_factory=dict)   # template only: {"left": f, "right": f}; 1 = not compressed
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


def _usable_arc(cav: cavity_math.Cavity, theta_c: float, deck: str, direction: int) -> float:
    """Arc length along the deck line from theta_c to where the deck normal tilts MAX_TILT_DEG from vertical."""
    phi_ref = 0.5 * math.pi if deck == "top" else 1.5 * math.pi
    lo, hi = theta_c, (math.pi - 2e-3 if direction > 0 else 2e-3)
    if _tilt_deg(cav.normal(hi, phi_ref), deck) <= MAX_TILT_DEG:
        return abs(cav.meridian_arc(theta_c, hi, phi_ref))
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if _tilt_deg(cav.normal(mid, phi_ref), deck) <= MAX_TILT_DEG:
            lo = mid
        else:
            hi = mid
    return abs(cav.meridian_arc(theta_c, lo, phi_ref))


def _template_nominal(diam: dict) -> dict:
    """Template positions (s, w) in mm about the layout centre, with the subholes placed by rule."""
    out = {n: (x - MIRACLE_CENTRE_X, MIRACLE_REF_Y - y) for n, (x, y) in MIRACLE.items()}
    for sub, (a, b) in SUBHOLES.items():
        (sa, wa), (sb, wb) = out[a], out[b]
        out[sub] = (0.5 * (sa + sb), 0.5 * (wa + wb) + SUBHOLE_OFFSET_MM[0])      # off the finger line, far side
    return out


def make_layout(cav: cavity_math.Cavity, preset: dict, hole_rows, min_gap_mm: float = MIN_GAP_MM) -> Layout:
    """Place the holes of `hole_rows` (kernel HoleResult list, opening order) on the cavity `cav`."""
    names = [h.name for h in hole_rows]
    diam = {h.name: h.d_mm for h in hole_rows}
    kind = preset.get("layout", "template")
    messages, compression = [], {}
    if kind == "relative":
        L = cav.length_mm
        theta_c = 0.5 * math.pi
        nominal = {n: (P0_RELATIVE[n][0] * L, P0_RELATIVE[n][1] * L) for n in names}
    elif kind == "template":
        centre_from_port = float(preset.get("layout_centre_from_port_mm", 16.0))
        theta_c = cav.theta_at_meridian_arc(cav.port_theta, centre_from_port, 0.5 * math.pi)
        nominal = _template_nominal(diam)
        # Fit the template to the usable deck: compress each side about the layout centre if it is too long.
        for side, direction in (("left", -1), ("right", 1)):
            members = [n for n in names if direction * nominal[n][0] > 0]
            need = max(abs(nominal[n][0]) + 0.5 * diam[n] + 1.0 for n in members)
            have = min(_usable_arc(cav, theta_c, "top", direction), _usable_arc(cav, theta_c, "bottom", direction))
            f = min(1.0, have / need)
            compression[side] = f
            if f < 1.0:
                for n in members:
                    nominal[n] = (nominal[n][0] * f, nominal[n][1])
                messages.append(f"the {side}-hand template was compressed to {100 * f:.0f} % along the body: the usable deck is "
                                f"{have:.1f} mm long from the layout centre and the template needs {need:.1f} mm")
    else:
        raise ValueError(f"unknown layout kind {kind!r}")

    pos = dict(nominal)
    rows = {h.name: h for h in hole_rows}

    def place(n):
        s, w = pos[n]
        deck = _deck_of(n)
        # keep the hole on the deck: limit the sideways offset to 35 % of the half section there
        theta, _ = _locate(cav, theta_c, deck, s, 0.0)
        half = 0.5 * abs(cav.section_arc(theta, 0.0, math.pi))
        w_lim = 0.35 * half
        w_used = max(-w_lim, min(w_lim, w))
        theta, phi = _locate(cav, theta_c, deck, s, w_used)
        return theta, phi, w_used

    def build():
        out = []
        for n in names:
            theta, phi, w_used = place(n)
            p, axis = cav.point(theta, phi), cav.normal(theta, phi)
            s0, w0 = nominal[n]
            r = rows[n]
            h = HolePlacement(name=n, deck=_deck_of(n), theta=theta, phi=phi, centre=p, axis=axis, d_mm=r.d_mm,
                              tube_mm=r.tube_mm, wall_mm=r.wall_mm, s_mm=pos[n][0], w_mm=w_used, s_nominal_mm=s0,
                              w_nominal_mm=w0, tilt_deg=_tilt_deg(axis, _deck_of(n)))
            out.append(h)
        return out

    def gaps_of(holes):
        g = []
        for i, a in enumerate(holes):
            for b in holes[i + 1:]:
                g.append((a.name, b.name, cavity_math._dist(a.centre, b.centre) - 0.5 * (a.d_mm + b.d_mm)))
        return sorted(g, key=lambda t: t[2])

    holes = build()
    for _ in range(40):                                   # relax: push violating pairs apart along the row
        bad = [g for g in gaps_of(holes) if g[2] < min_gap_mm - 1e-6]
        if not bad:
            break
        moved_any = False
        for a, b, gap in bad:
            need = 0.5 * (min_gap_mm - gap) + 0.05
            sa, sb = pos[a][0], pos[b][0]
            sign = 1.0 if sa >= sb else -1.0
            for n, sg in ((a, sign), (b, -sign)):
                if n in SUBHOLES and kind == "template":
                    w_new = min(pos[n][1] + need, nominal[n][1] - SUBHOLE_OFFSET_MM[0] + SUBHOLE_OFFSET_MM[1])
                    if w_new > pos[n][1] + 1e-9:
                        pos[n] = (pos[n][0], w_new)
                        moved_any = True
                        continue
                s_new = pos[n][0] + sg * need
                s_new = max(nominal[n][0] - MAX_MOVE_MM, min(nominal[n][0] + MAX_MOVE_MM, s_new))
                if abs(s_new - pos[n][0]) > 1e-9:
                    pos[n] = (s_new, pos[n][1])
                    moved_any = True
        holes = build()
        if not moved_any:
            break
    by = {}
    for h in holes:                                       # distance moved from the nominal template position
        theta0, phi0, _ = _nominal_point(cav, theta_c, h, nominal[h.name])
        h.moved_mm = cavity_math._dist(h.centre, cav.point(theta0, phi0))
        by[h.name] = h
    gaps = gaps_of(holes)
    for a, b, gap in gaps:
        if gap < min_gap_mm - 1e-6:
            messages.append(f"edge gap {a} to {b} is {gap:.2f} mm, under {min_gap_mm:.1f} mm, after the allowed moves")
    return Layout(kind=kind, holes=holes, compression=compression, gaps=gaps, messages=messages)


def _nominal_point(cav, theta_c, h: HolePlacement, sw):
    s, w = sw
    theta, _ = _locate(cav, theta_c, h.deck, s, 0.0)
    half = 0.5 * abs(cav.section_arc(theta, 0.0, math.pi))
    w = max(-0.35 * half, min(0.35 * half, w))
    theta, phi = _locate(cav, theta_c, h.deck, s, w)
    return theta, phi, w
