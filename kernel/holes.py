"""Hole sizing for a linear fingering (docs/04 D6, D8).

Each hole is round and has its own diameter, solved per note with the chimney-volume fixed point
(doc 03, section 2). Holes under 3 mm get a round inward tube. The tube length counts as chimney.

Position factors. A hole may deliver more or less conductance than the lumped model says, because of
where it sits on the body (tail, bulb). The model is

    G_i = psi_i * A_i / (t_i + k_hole * d_eq_i)

with psi_i = 1 as the default. The fitter (fitter.py) measures psi_i. Sizing with psi_i != 1 asks
for the diameter that gives the needed G_i.

All functions work in metres. The records at the end hold millimetres.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import ocarina_kernel as ok

MM = 1e-3


@dataclass(frozen=True)
class HoleSpec:
    name: str
    opens: str            # note that this hole opens, e.g. "B4"
    kind: str             # "finger" | "thumb"
    wall_m: float         # wall along the hole axis (the plain chimney), m
    max_d_m: float        # finger-pad limit, m
    min_d_m: float = 3e-3  # print floor, m


def hole_specs_from_params(params: dict, wall_mm: float | None = None) -> list:
    """Hole specs in opening order, from params [fingering] and [hole_rules].

    The chimney_mm in [fingering] is the doc 03 baseline (3 mm) and is not used. The wall of the test
    bodies comes from [hole_rules].wall_at_holes_mm (4 mm).
    """
    wall = wall_mm if wall_mm is not None else params["hole_rules"]["wall_at_holes_mm"]
    min_d = params["constraints"]["hole_min_d_mm"] * MM
    notes = params["design"]["notes"]
    out = []
    for i, h in enumerate(params["fingering"]["holes"]):
        kind = "thumb" if h["max_d_mm"] > params["constraints"]["finger_max_d_mm"] else "finger"
        out.append(HoleSpec(h["name"], notes[i + 1], kind, wall * MM, h["max_d_mm"] * MM, min_d))
    return out


# --------------------------------------------------------------------------
# Core solve
# --------------------------------------------------------------------------

def _solve_one(f: float, V0: float, V_open: float, G_open: float, X_w: float, t: float, k: float,
               K: float, psi: float, tol: float = 1e-13, max_iter: int = 200):
    """One hole of the fixed point. Returns (d, G_needed, A)."""
    A = 0.0
    for _ in range(max_iter):
        V = V0 - V_open - A * t
        G = K * f * f * V - X_w - G_open
        if G <= 0.0:
            raise ValueError("non-positive conductance: the target scale is not reachable with this window and volume")
        d = ok.hole_diameter(G / psi, t, k)
        A_new = math.pi * d * d / 4.0
        if abs(A_new - A) < tol:
            A = A_new
            break
        A = A_new
    return d, G, A


def solve_scale(f_targets, X_w: float, V0: float, chimneys, k: float, c: float, psi=None):
    """Size every hole of a linear fingering. f_targets[0] is the all-closed note.

    X_w       eta_w * G_w, m
    V0        capped air volume, m^3
    chimneys  chimney length of each hole (wall + tube), m
    k, psi    end correction and position factors of the holes
    Returns (diameters m, needed conductances m).
    """
    n = len(chimneys)
    if len(f_targets) != n + 1:
        raise ValueError("need len(f_targets) == len(chimneys) + 1")
    psi = psi if psi is not None else [1.0] * n
    K = ok.TWO_PI ** 2 / (c * c)
    V_open = G_open = 0.0
    ds, Gs = [], []
    for j in range(n):
        d, G, A = _solve_one(f_targets[j + 1], V0, V_open, G_open, X_w, chimneys[j], k, K, psi[j])
        ds.append(d)
        Gs.append(G)
        G_open += G
        V_open += A * chimneys[j]
    return ds, Gs


def predict_scale(X_w: float, V0: float, diameters, chimneys, k: float, c: float, psi=None):
    """Frequencies of the linear fingering for given holes: note j has holes 0..j-1 open."""
    n = len(diameters)
    psi = psi if psi is not None else [1.0] * n
    f = [ok.freq(X_w, V0, c)]
    G_open = V_open = 0.0
    for j in range(n):
        A = math.pi * diameters[j] ** 2 / 4.0
        G_open += psi[j] * ok.conductance(A, chimneys[j], k)
        V_open += A * chimneys[j]
        f.append(ok.freq(X_w + G_open, V0 - V_open, c))
    return f


# --------------------------------------------------------------------------
# Inward tubes
# --------------------------------------------------------------------------

def plan_tubes(f_targets, X_w: float, V0: float, specs, k_floor: float, c: float, psi=None,
               step_m: float = 0.5e-3, tube_max_m: float = 15e-3):
    """Inward tube length of each hole (m). A tube is the shortest length, in steps, that lifts the
    diameter at k_floor to the print floor. Holes that already reach the floor get 0.

    Returns (tubes, capped) where capped lists the names of holes that still miss the floor at tube_max.
    """
    n = len(specs)
    psi = psi if psi is not None else [1.0] * n
    K = ok.TWO_PI ** 2 / (c * c)
    V_open = G_open = 0.0
    tubes, capped = [], []
    for j, s in enumerate(specs):
        f = f_targets[j + 1]

        def d_at(t):
            return _solve_one(f, V0, V_open, G_open, X_w, t, k_floor, K, psi[j])

        tube = 0.0
        d, G, A = d_at(s.wall_m)
        if d < s.min_d_m:
            if d_at(s.wall_m + tube_max_m)[0] < s.min_d_m:
                tube = tube_max_m
                capped.append(s.name)
            else:
                lo, hi = 0.0, tube_max_m
                for _ in range(80):
                    mid = 0.5 * (lo + hi)
                    if d_at(s.wall_m + mid)[0] < s.min_d_m:
                        lo = mid
                    else:
                        hi = mid
                tube = min(tube_max_m, math.ceil(hi / step_m - 1e-9) * step_m)
            d, G, A = d_at(s.wall_m + tube)
        tubes.append(tube)
        G_open += G
        V_open += A * (s.wall_m + tube)
    return tubes, capped


def tube_wall_displacement_m3(bore_d: float, tube_len: float, tube_wall: float) -> float:
    """Volume of plastic in the wall of an inward tube: pi/4 * ((d + 2w)^2 - d^2) * L."""
    return math.pi * tube_wall * (bore_d + tube_wall) * tube_len


# --------------------------------------------------------------------------
# Result records (millimetres)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class HoleResult:
    name: str
    opens: str
    kind: str
    k_hole: float
    wall_mm: float
    tube_mm: float
    chimney_mm: float           # wall + tube
    d_mm: float
    area_mm2: float
    G_mm: float                 # conductance the hole must deliver (effective), mm
    psi: float
    d_plain_mm: float           # diameter in the plain wall, no tube (the number in doc 04's table)
    below_floor: bool
    above_pad_limit: bool
    max_d_mm: float
    min_d_mm: float

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class HoleSizing:
    tubes_mm: list              # inward tube length per hole (shared by every k solution)
    capped: list                # holes still under the floor at the longest tube
    solutions: dict             # key -> list[HoleResult], one list per k
    tube_wall_displacement_cm3: float
    floor_key: str

    def to_dict(self) -> dict:
        return {"tubes_mm": self.tubes_mm, "capped": self.capped,
                "tube_wall_displacement_cm3": self.tube_wall_displacement_cm3, "floor_key": self.floor_key,
                "solutions": {k: [h.to_dict() for h in v] for k, v in self.solutions.items()}}


def size_holes(f_targets, X_w: float, V0: float, specs, ks: dict, c: float, *, floor_key: str | None = None,
               psi=None, tubes_mm=None, tube_step_mm: float = 0.5, tube_max_mm: float = 15.0,
               tube_wall_mm: float = 1.2) -> HoleSizing:
    """Size the holes for each k in `ks` (a dict label -> k), with the same chimney lengths for all k.

    Tube lengths come from the floor_key solution (default: the first key), unless tubes_mm is given.
    Giving tubes_mm fixes the chimneys (Stage 3 reprints, or a body whose tubes are already modelled).
    """
    n = len(specs)
    psi_l = list(psi) if psi is not None else [1.0] * n
    floor_key = floor_key or next(iter(ks))
    if tubes_mm is None:
        tubes_m, capped = plan_tubes(f_targets, X_w, V0, specs, ks[floor_key], c, psi_l,
                                     tube_step_mm * MM, tube_max_mm * MM)
    else:
        if len(tubes_mm) != n:
            raise ValueError("tubes_mm needs one entry per hole")
        tubes_m, capped = [x * MM for x in tubes_mm], []
    chimneys = [s.wall_m + t for s, t in zip(specs, tubes_m)]
    plain_chimneys = [s.wall_m for s in specs]
    solutions = {}
    for key, k in ks.items():
        ds, Gs = solve_scale(f_targets, X_w, V0, chimneys, k, c, psi_l)
        plain, _ = solve_scale(f_targets, X_w, V0, plain_chimneys, k, c, psi_l)
        rows = []
        for s, tube, ch, d, G, dp, p in zip(specs, tubes_m, chimneys, ds, Gs, plain, psi_l):
            rows.append(HoleResult(
                name=s.name, opens=s.opens, kind=s.kind, k_hole=k, wall_mm=s.wall_m / MM, tube_mm=tube / MM,
                chimney_mm=ch / MM, d_mm=d / MM, area_mm2=math.pi * d * d / 4.0 / MM / MM, G_mm=G / MM, psi=p,
                d_plain_mm=dp / MM, below_floor=d < s.min_d_m - 1e-9, above_pad_limit=d > s.max_d_m + 1e-9,
                max_d_mm=s.max_d_m / MM, min_d_mm=s.min_d_m / MM))
        solutions[key] = rows
    disp = sum(tube_wall_displacement_m3(r.d_mm * MM, r.tube_mm * MM, tube_wall_mm * MM)
               for r in solutions[floor_key] if r.tube_mm > 0)
    return HoleSizing(tubes_mm=[t / MM for t in tubes_m], capped=capped, solutions=solutions,
                      tube_wall_displacement_cm3=disp / 1e-6, floor_key=floor_key)
