"""Hand layout of a 12-hole ocarina: metrics in the frame of the hands, and the soft ergonomic checks.

Standard library only (no Blender, no numpy), so the add-on, the analysis scripts and the tests share it.
The metrics are those of docs/06-ergonomics-challenge.md. The reference script
`Analizes_ocarinas/Ergonomic_reference_12hole/measure_cad_references.py` imports this module, so the
reference numbers and the checks come from one place.

The frame of the hands
    Every layout is given in a "player frame": X runs from the bulb (left-hand) end toward the tail,
    Y toward the player, Z out of the finger face. Only the plan view (X, Y) defines the frame:
        hand axis a   the mean direction of the two hand lines (L pinky -> L index, R index -> R pinky)
        across p      perpendicular to a, toward the player
    Nothing depends on how the body is turned in the picture or in the CAD file.

    hand_metrics(P)            plan-view metrics from hole centres {name: (X, Y)}
    layout_metrics(holes)      the same, plus the straight 3-D finger pitch and the lean of each hole
    evaluate(metrics, limits)  the ergo_* checks: each is "pass" or "warn", never "fail"

The subhole names of the kernel (sub1, sub2) and of the reference tables (sub_L, sub_R) are both read.
"""
from __future__ import annotations

import math

LEFT = ("L_pinky", "L_ring", "L_middle", "L_index")
RIGHT = ("R_pinky", "R_ring", "R_middle", "R_index")
FINGERS = LEFT + RIGHT
THUMBS = ("L_thumb", "R_thumb")
SUBHOLES = ("sub_L", "sub_R", "sub1", "sub2")
FIRST_SUBHOLE = ("sub_L", "sub1")          # the subhole that opens B4; by convention the left-hand one
TAPED_MESSAGE = "taped test body, not a hand layout"

# Default limits: the "Proposed" column of docs/06 section 5 (owner decision of 2026-11-15). The add-on reads
# them from the [ergonomics] table of params/alto_c_12hole.toml; these are used when a key is missing.
DEFAULT_LIMITS = {
    "finger_pitch_mm": (16.5, 20.5),
    "hand_span_mm": (50.0, 60.0),
    "arch_mm": (0.5, 7.0),
    "hands_parallel_max_deg": 10.0,
    "hand_offset_mm": (18.0, 28.0),
    "index_across_mm": (18.0, 28.0),
    "index_along_mm": (-22.0, 5.0),
    "subhole_distance_mm": (7.0, 11.0),
    "subhole_off_normal_max_deg": 20.0,
    "rest_space_min_mm": 10.0,
    "hole_lean_end_max_deg": 20.0,
    "hole_lean_side_max_deg": 45.0,
    "hole_lean_side_away_max_deg": 5.0,
    "r_thumb_from_r_middle_mm": (-8.0, 3.0),
    "l_thumb_from_l_pinky_mm": (4.0, 10.0),
}


# ---------------------------------------------------------------------- small 2-D helpers

def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _norm(a):
    return math.hypot(a[0], a[1])


def _unit(a):
    n = _norm(a)
    return (a[0] / n, a[1] / n)


def _dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _mid(points):
    n = len(points)
    return (sum(p[0] for p in points) / n, sum(p[1] for p in points) / n)


# ---------------------------------------------------------------------- plan-view metrics

def hand_frame(P):
    """Hand axis a (bulb -> tail), across p (toward the player) and the two line directions.
    P: name -> (X, Y) with Y toward the player. uL runs L pinky -> L index, uR runs R index -> R pinky."""
    uL = _unit(_sub(P["L_index"], P["L_pinky"]))
    uR = _unit(_sub(P["R_pinky"], P["R_index"]))
    a = _unit((uL[0] + uR[0], uL[1] + uR[1]))
    p = (-a[1], a[0])
    if p[1] < 0:
        p = (-p[0], -p[1])
    return a, p, uL, uR


def fingertip_normal(P, hand: str, p=None):
    """Unit normal of one hand's pinky -> index line, on the side its fingertips point to.
    The left fingers come over from the far side, so their tips point toward the player; the right
    fingers come from the player's side, so their tips point away. Returns (u, normal)."""
    names = LEFT if hand == "L" else RIGHT
    if p is None:
        p = hand_frame(P)[1]
    u = _unit(_sub(P[names[3]], P[names[0]]))
    nrm = (-u[1], u[0])
    ext = 1.0 if hand == "L" else -1.0
    if _dot(nrm, p) * ext < 0:
        nrm = (-nrm[0], -nrm[1])
    return u, nrm


def hand_metrics(P) -> dict:
    """Frame-free layout metrics in the plan view. P: name -> (X, Y[, ...]); X from the bulb side, Y toward
    the player. Lengths come back in the unit of P."""
    P = {n: (float(v[0]), float(v[1])) for n, v in P.items()}
    a, p, uL, uR = hand_frame(P)
    m = {"a": a, "p": p}
    # angle between the two hand lines: + = the lines open toward the tail (a fan), 0 = parallel
    m["hands_angle"] = math.degrees(math.atan2(uL[0] * uR[1] - uL[1] * uR[0], _dot(uL, uR)))
    m["line_tilt"] = math.degrees(math.acos(max(-1.0, min(1.0, _dot(uL, a)))))      # each line against the hand axis
    # + = the right-hand line is nearer the player
    m["line_offset"] = _dot(_sub(_mid([P["R_pinky"], P["R_index"]]), _mid([P["L_pinky"], P["L_index"]])), p)
    m["pinky_span"] = _norm(_sub(P["R_pinky"], P["L_pinky"]))
    v = _sub(P["R_index"], P["L_index"])
    m["index_across"], m["index_along"], m["index_dist"] = _dot(v, p), _dot(v, a), _norm(v)
    # each line against the frame's own X axis (the body axis, where the frame has one). Reported, never checked.
    m["line_vs_x_deg"] = {"L": math.degrees(math.atan2(uL[1], uL[0])), "R": math.degrees(math.atan2(uR[1], uR[0]))}
    for hand, names in (("L", LEFT), ("R", RIGHT)):
        q = [P[n] for n in names]
        u, nrm = fingertip_normal(P, hand, p)
        m[hand] = dict(pitches=[_norm(_sub(q[i + 1], q[i])) for i in range(3)], span=_norm(_sub(q[3], q[0])),
                       arch=[_dot(_sub(q[i], q[0]), nrm) for i in (1, 2)], u=u, nrm=nrm)
    # subholes: the nearest finger hole of EITHER hand is the parent; the slide is given in the parent's hand frame
    for sub in SUBHOLES:
        if sub not in P:
            continue
        parent = min(FINGERS, key=lambda n: _norm(_sub(P[n], P[sub])))
        hand = parent[0]
        v = _sub(P[sub], P[parent])
        fwd, along = _dot(v, m[hand]["nrm"]), _dot(v, m[hand]["u"])
        same = min((LEFT if sub in FIRST_SUBHOLE else RIGHT), key=lambda n: _norm(_sub(P[n], P[sub])))
        m[sub] = dict(parent=parent, dist=_norm(v), forward=fwd, toward_index=along,
                      off_normal_deg=math.degrees(math.atan2(along, fwd)),
                      nearest_same_hand=same, dist_same_hand=_norm(_sub(P[same], P[sub])))
    # thumbs: position along the hand axis against the finger holes of that hand
    for th, names in (("L_thumb", LEFT), ("R_thumb", RIGHT)):
        if th not in P:
            continue
        s = _dot(P[th], a)
        rel = {n: s - _dot(P[n], a) for n in names}            # + = the thumb is toward the tail of that finger hole
        m[th] = dict(rel=rel, nearest=min(names, key=lambda n: abs(rel[n])),
                     across={n: _dot(_sub(P[th], P[n]), p) for n in names})
    return m


# ---------------------------------------------------------------------- 3-D metrics

def hole_lean(axis, a, p, hand: str) -> dict:
    """Lean of a finger hole. axis: unit vector out of the hole in the player frame (Z out of the finger face).

    tilt_deg        angle between the axis and the normal of the finger face
    toward_end_deg  lean along the hand axis toward the nearer end of the body (left hand: the bulb,
                    right hand: the tail). Negative = toward the middle.
    toward_hand_deg lean across the hand axis toward the hand that covers the hole (left hand: the far
                    side, right hand: the player). Negative = away from that hand.
    way             the larger of the two, as a word: "far" / "player" / "bulb" / "tail"
    """
    ax, ay, az = (float(c) for c in axis)
    along, across = ax * a[0] + ay * a[1], ax * p[0] + ay * p[1]
    tilt = math.degrees(math.acos(max(-1.0, min(1.0, az))))
    toward_tail = math.degrees(math.atan2(along, az))
    toward_player = math.degrees(math.atan2(across, az))
    way = ("player" if across > 0 else "far") if abs(across) >= abs(along) else ("tail" if along > 0 else "bulb")
    sign = -1.0 if hand == "L" else 1.0
    return dict(tilt_deg=tilt, toward_tail_deg=toward_tail, toward_player_deg=toward_player,
                toward_end_deg=sign * toward_tail, toward_hand_deg=sign * toward_player, way=way)


def layout_metrics(holes: dict) -> dict:
    """Metrics of a layout given in 3-D. holes: name -> dict(centre=(X, Y, Z), axis=(aX, aY, aZ), d_mm=...),
    in the player frame. `axis` and `d_mm` are optional. Adds to hand_metrics():

        pitches_3d   {"L": [...], "R": [...]}  straight distance between neighbouring centres
        lean         {finger hole: hole_lean(...)}     (holes that have an axis)
        d_mm         {name: diameter}                  (holes that have one)
    The subhole and thumb entries get "dist_3d" where it applies.
    """
    C = {n: tuple(float(c) for c in h["centre"]) for n, h in holes.items()}
    m = hand_metrics({n: c[:2] for n, c in C.items()})
    m["pitches_3d"] = {hand: [_dist(C[names[i + 1]], C[names[i]]) for i in range(3)]
                       for hand, names in (("L", LEFT), ("R", RIGHT))}
    for sub in SUBHOLES:
        if sub in m:
            m[sub]["dist_3d"] = _dist(C[sub], C[m[sub]["parent"]])
    m["lean"] = {n: hole_lean(holes[n]["axis"], m["a"], m["p"], n[0]) for n in FINGERS
                 if holes[n].get("axis") is not None}
    m["d_mm"] = {n: float(h["d_mm"]) for n, h in holes.items() if h.get("d_mm") is not None}
    return m


def body_to_player(v):
    """A point or a direction in the add-on's body coordinates (X along the body from the left-hand end,
    +Y away from the player, +Z the finger deck) in the player frame of this module."""
    return (float(v[0]), -float(v[1]), float(v[2]))


# ---------------------------------------------------------------------- the soft checks

def _result(name, problems, value, limit, message, taped):
    status = "warn" if (problems or taped) else "pass"
    if taped:
        message = f"{TAPED_MESSAGE}. Measured: {message}"
    elif problems:
        message = "; ".join(problems) + ". Measured: " + message
    return dict(name=name, status=status, value=float(value), limit=limit, message=message)


def _outside(x, lo, hi):
    """How far x lies outside [lo, hi] (0 inside)."""
    return max(lo - x, x - hi, 0.0)


def _fmt_range(r, unit=" mm"):
    return f"{r[0]:g} to {r[1]:g}{unit}"


def evaluate(m: dict, limits: dict | None = None, rest: dict | None = None, taped: bool = False,
             outer: dict | None = None) -> list:
    """The ergo_* checks of docs/06 section 5. Each result is a dict: name, status, value, limit, message.
    The status is "pass" or "warn"; a warning is never a failure.

    m       layout_metrics() of the layout (or hand_metrics(): checks that need 3-D data are then left out)
    limits  the [ergonomics] table; missing keys fall back to DEFAULT_LIMITS
    rest    {"bulb": mm, "tail": mm}: from the pinky hole CENTRE to the end of the body, along the hand axis
            in the plan view. Without it ergo_rest_space is left out.
    taped   a taped test body (the P0 control egg): every check reports "warn" with TAPED_MESSAGE
    outer   the same metrics for the hole centres at the outer skin. They do not decide any status; where
            they are given, the span, pitch and subhole messages quote them.
    """
    lim = dict(DEFAULT_LIMITS)
    lim.update(limits or {})
    out = []
    side = {"L": "left", "R": "right"}

    # --- finger pitch: straight 3-D distance where the layout has one
    lo, hi = lim["finger_pitch_mm"]
    pitches = m.get("pitches_3d") or {h: m[h]["pitches"] for h in ("L", "R")}
    kind = "straight 3D distance" if "pitches_3d" in m else "plan view"
    pairs = [(f"{names[i]} to {names[i + 1]}", pitches[hand][i]) for hand, names in (("L", LEFT), ("R", RIGHT)) for i in range(3)]
    bad = [f"{n} {v:.1f} mm" for n, v in pairs if _outside(v, lo, hi) > 0]
    worst = max(pairs, key=lambda t: _outside(t[1], lo, hi))[1] if bad else min(v for _, v in pairs)
    msg = (f"left {' / '.join(f'{v:.1f}' for v in pitches['L'])} mm, right {' / '.join(f'{v:.1f}' for v in pitches['R'])} mm "
           f"(pinky, ring, middle, index; {kind}); ok {_fmt_range((lo, hi))}")
    if outer and "pitches_3d" in outer:
        po = outer["pitches_3d"]
        msg += f"; at the outer skin: left {' / '.join(f'{v:.1f}' for v in po['L'])}, right {' / '.join(f'{v:.1f}' for v in po['R'])} mm"
    out.append(_result("ergo_finger_pitch", ["finger pitch out of range: " + ", ".join(bad)] if bad else [], worst,
                       [lo, hi], msg, taped))

    # --- hand span, pinky to index
    lo, hi = lim["hand_span_mm"]
    spans = [("left", m["L"]["span"]), ("right", m["R"]["span"])]
    bad = [f"{n} hand {v:.1f} mm" for n, v in spans if _outside(v, lo, hi) > 0]
    msg = f"left {spans[0][1]:.1f} mm, right {spans[1][1]:.1f} mm (pinky to index, plan view); ok {_fmt_range((lo, hi))}"
    if outer:
        msg += f"; at the outer skin: left {outer['L']['span']:.1f}, right {outer['R']['span']:.1f} mm"
    out.append(_result("ergo_hand_span", ["hand span out of range: " + ", ".join(bad)] if bad else [],
                       max(spans, key=lambda t: _outside(t[1], lo, hi))[1] if bad else min(v for _, v in spans), [lo, hi], msg, taped))

    # --- arch: ring and middle off the pinky -> index line, toward the fingertips
    lo, hi = lim["arch_mm"]
    arch = [(f"{side[h]} {f}", v) for h in ("L", "R") for f, v in zip(("ring", "middle"), m[h]["arch"])]
    bad = [f"{n} {v:+.1f} mm" + (" (against the fingers)" if v < 0 else "") for n, v in arch if _outside(v, lo, hi) > 0]
    msg = (f"left ring {m['L']['arch'][0]:+.1f}, left middle {m['L']['arch'][1]:+.1f}, right ring {m['R']['arch'][0]:+.1f}, "
           f"right middle {m['R']['arch'][1]:+.1f} mm off the pinky to index line, + toward the fingertips; ok {lo:+g} to {hi:+g} mm")
    out.append(_result("ergo_arch", ["arch out of range: " + ", ".join(bad)] if bad else [],
                       max(arch, key=lambda t: _outside(t[1], lo, hi))[1] if bad else min(v for _, v in arch), [lo, hi], msg, taped))

    # --- the two hand lines: parallel, and a set distance apart across the hands
    lim_par = lim["hands_parallel_max_deg"]
    ang = m["hands_angle"]
    out.append(_result("ergo_hands_parallel", [f"the hand lines are {ang:+.1f}° apart"] if abs(ang) > lim_par else [], ang, lim_par,
                       f"angle between the two hand lines {ang:+.1f}° (+ = they open toward the tail); ok within ±{lim_par:g}°", taped))
    lo, hi = lim["hand_offset_mm"]
    off = m["line_offset"]
    tilt = m.get("line_vs_x_deg", {})
    msg = f"the right-hand line is {off:.1f} mm nearer the player than the left-hand line; ok {_fmt_range((lo, hi))}"
    if tilt:
        msg += (f". Tilt against the body axis, reported only: left line {-tilt['L']:+.1f}°, right line {-tilt['R']:+.1f}° "
                f"(+ = the tail end of the line is farther from the player)")
    out.append(_result("ergo_hand_offset", [f"hand lines {off:.1f} mm apart across"] if _outside(off, lo, hi) > 0 else [], off,
                       [lo, hi], msg, taped))

    # --- where the two index holes meet
    (alo, ahi), (blo, bhi) = lim["index_across_mm"], lim["index_along_mm"]
    ac, al = m["index_across"], m["index_along"]
    bad = ([f"index holes {ac:.1f} mm apart across"] if _outside(ac, alo, ahi) > 0 else []) + \
          ([f"R index {al:+.1f} mm along the hand axis from L index"] if _outside(al, blo, bhi) > 0 else [])
    out.append(_result("ergo_index_meet", bad, ac if _outside(ac, alo, ahi) > 0 or not bad else al, [alo, ahi, blo, bhi],
                       f"R index from L index: {ac:.1f} mm across (toward the player), {al:+.1f} mm along the hand axis "
                       f"(− = toward the bulb: the hands overlap); ok {_fmt_range((alo, ahi))} across, {blo:+g} to {bhi:+g} mm along", taped))

    # --- subholes: a short slide straight forward of the parent
    lo, hi = lim["subhole_distance_mm"]
    lim_n = lim["subhole_off_normal_max_deg"]
    subs = [s for s in SUBHOLES if s in m]
    if subs:
        bad, parts, worst = [], [], 0.0
        for s in subs:
            r = m[s]
            dist = r.get("dist_3d", r["dist"])
            part = (f"{s} from {r['parent']}: {dist:.1f} mm, {r['off_normal_deg']:+.0f}° off the normal of the "
                    f"{side[r['parent'][0]]}-hand line ({r['forward']:+.1f} mm forward, {r['toward_index']:+.1f} mm toward the index)")
            if outer and s in outer:
                part += f"; at the outer skin {outer[s].get('dist_3d', outer[s]['dist']):.1f} mm"
            parts.append(part)
            if _outside(dist, lo, hi) > 0:
                bad.append(f"{s} is {dist:.1f} mm from {r['parent']}")
            if abs(r["off_normal_deg"]) > lim_n:
                bad.append(f"{s} lies {r['off_normal_deg']:+.0f}° off the normal" + (" (behind the finger)" if r["forward"] < 0 else ""))
            worst = max(worst, _outside(dist, lo, hi), abs(r["off_normal_deg"]) - lim_n)
        out.append(_result("ergo_subholes", bad, m[subs[0]].get("dist_3d", m[subs[0]]["dist"]), [lo, hi, lim_n],
                           "; ".join(parts) + f"; ok {_fmt_range((lo, hi))} from the nearest finger hole, within {lim_n:g}° of the normal", taped))

    # --- rest space past the pinky holes, from the hole edge
    if rest is not None:
        need = lim["rest_space_min_mm"]
        d = m.get("d_mm", {})
        land = {"bulb": rest["bulb"] - 0.5 * d.get("L_pinky", 0.0), "tail": rest["tail"] - 0.5 * d.get("R_pinky", 0.0)}
        bad = [f"the {end} end is {need - v:.1f} mm too short: {v:.1f} mm past the {pinky} hole edge"
               for end, pinky, v in (("bulb", "L pinky", land["bulb"]), ("tail", "R pinky", land["tail"])) if v < need]
        out.append(_result("ergo_rest_space", bad, min(land.values()), need,
                           f"land past the pinky holes, from the hole edge along the hand axis: bulb {land['bulb']:.1f} mm "
                           f"(centre {rest['bulb']:.1f}), tail {land['tail']:.1f} mm (centre {rest['tail']:.1f}); ok at least {need:g} mm", taped))

    # --- lean of the finger holes
    lean = m.get("lean") or {}
    if lean:
        lim_e = lim["hole_lean_end_max_deg"]
        bad = [f"{n} leans {r['toward_end_deg']:.0f}° toward the {'bulb' if n[0] == 'L' else 'tail'} end"
               for n, r in lean.items() if r["toward_end_deg"] > lim_e]
        worst_n = max(lean, key=lambda n: lean[n]["toward_end_deg"])
        out.append(_result("ergo_hole_lean_end", bad, lean[worst_n]["toward_end_deg"], lim_e,
                           "lean along the hand axis toward the nearer end (− = toward the middle): "
                           + ", ".join(f"{n} {lean[n]['toward_end_deg']:+.0f}°" for n in FINGERS if n in lean)
                           + f"; ok up to {lim_e:g}°", taped))
        lim_s, lim_a = lim["hole_lean_side_max_deg"], lim["hole_lean_side_away_max_deg"]
        bad = []
        for n, r in lean.items():
            hand_side = "far side" if n[0] == "L" else "player"
            if r["toward_hand_deg"] > lim_s:
                bad.append(f"{n} leans {r['toward_hand_deg']:.0f}° toward the {hand_side}")
            elif r["toward_hand_deg"] < -lim_a:
                bad.append(f"{n} leans {-r['toward_hand_deg']:.0f}° away from the hand that covers it")
        worst_n = max(lean, key=lambda n: max(lean[n]["toward_hand_deg"] - lim_s, -lim_a - lean[n]["toward_hand_deg"]))
        out.append(_result("ergo_hole_lean_side", bad, lean[worst_n]["toward_hand_deg"], [-lim_a, lim_s],
                           "lean across the hand axis toward the covering hand (left hand: the far side; right hand: the player; "
                           "− = away from it): " + ", ".join(f"{n} {lean[n]['toward_hand_deg']:+.0f}°" for n in FINGERS if n in lean)
                           + f"; ok up to {lim_s:g}° toward it and up to {lim_a:g}° away", taped))

    # --- thumbs
    if "L_thumb" in m and "R_thumb" in m:
        (rlo, rhi), (llo, lhi) = lim["r_thumb_from_r_middle_mm"], lim["l_thumb_from_l_pinky_mm"]
        rt, lt = m["R_thumb"]["rel"]["R_middle"], m["L_thumb"]["rel"]["L_pinky"]
        bad = ([f"R thumb {rt:+.1f} mm from R middle"] if _outside(rt, rlo, rhi) > 0 else []) + \
              ([f"L thumb {lt:+.1f} mm from L pinky"] if _outside(lt, llo, lhi) > 0 else [])
        out.append(_result("ergo_thumbs", bad, rt if _outside(rt, rlo, rhi) > 0 or not bad else lt, [rlo, rhi, llo, lhi],
                           f"along the hand axis, + toward the tail: R thumb {rt:+.1f} mm from R middle (ok {rlo:+g} to {rhi:+g}), "
                           f"L thumb {lt:+.1f} mm from L pinky (ok {llo:+g} to {lhi:+g})", taped))
    return out
