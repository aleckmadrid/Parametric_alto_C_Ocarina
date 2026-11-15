"""Lumped Helmholtz acoustic kernel for vessel flutes (ocarinas).

Seed of the Phase 0 kernel described in docs/02-unified-plan.md.
Pure Python standard library, no Blender imports. SI units throughout
(m, m^2, m^3, Hz, Pa, deg C) unless a name ends in _mm or _cm3.

Model (docs/03-parametric-findings.md, section 2):
    f_j   = c / (2 pi) * sqrt(G_tot_j / V_j)
    G_tot = eta_w * G_w + sum(G_i, i open)
    G_i   = A_i / (t_i + k * d_eq_i),   d_eq = 2 sqrt(A / pi)
    V_j   = V_0 - sum(A_i * t_i, i open)        (open chimneys are neck, not cavity)
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

TWO_PI = 2.0 * math.pi
R_GAS = 8.314462618          # J/(mol K)
CENTS_PER_LN = 1200.0 / math.log(2.0)   # 1731.234...

# --------------------------------------------------------------------------
# Air properties
# --------------------------------------------------------------------------

def c_air(T_c: float = 27.0) -> float:
    """Speed of sound in dry air (the build plan's formula). m/s."""
    return 331.3 * math.sqrt(1.0 + T_c / 273.15)


# molar mass (kg/mol), molar Cp (J/(mol K)) near 300 K
_SPECIES = {
    "N2": (0.0280134, 29.12),
    "O2": (0.0319988, 29.38),
    "Ar": (0.0399480, 20.79),
    "CO2": (0.0440095, 37.22),
    "H2O": (0.0180153, 33.58),
}
DRY_AIR = {"N2": 0.78084, "O2": 0.20946, "Ar": 0.00934, "CO2": 0.00042}
# Exhaled breath, dry basis (typical textbook values; O2 down, CO2 up).
EXHALED_DRY = {"N2": 0.7846, "O2": 0.1640, "Ar": 0.0094, "CO2": 0.0420}


def p_sat_kpa(T_c: float) -> float:
    """Saturation vapour pressure of water (Buck 1981), kPa."""
    return 0.61121 * math.exp((18.678 - T_c / 234.5) * (T_c / (257.14 + T_c)))


def humidify(dry: dict, T_c: float, rh: float, p_kpa: float = 101.325) -> dict:
    x_w = rh * p_sat_kpa(T_c) / p_kpa
    mix = {s: x * (1.0 - x_w) for s, x in dry.items()}
    mix["H2O"] = mix.get("H2O", 0.0) + x_w
    return mix


def c_mixture(T_c: float, composition: dict) -> float:
    """Ideal-gas speed of sound sqrt(gamma R T / M) for a molar composition."""
    tot = sum(composition.values())
    M = sum(x * _SPECIES[s][0] for s, x in composition.items()) / tot
    cp = sum(x * _SPECIES[s][1] for s, x in composition.items()) / tot
    gamma = cp / (cp - R_GAS)
    return math.sqrt(gamma * R_GAS * (T_c + 273.15) / M)


def rho_air(T_c: float = 27.0, p_pa: float = 101325.0, M: float = 0.028965) -> float:
    return p_pa * M / (R_GAS * (T_c + 273.15))


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------

def teardrop_area(length: float, width: float, tip_radius: float) -> float:
    """Area of a teardrop = convex hull of two circles (R = width/2, r = tip).

    length is tip-to-tail along the axis (for the window: windway exit to
    labium edge). Reduces to a stadium when tip_radius == width/2.
    """
    R, r = width / 2.0, tip_radius
    D = length - R - r
    if D <= 0 or r > R:
        raise ValueError("teardrop needs length > width/2 + tip_radius and tip <= width/2")
    phi = math.asin((R - r) / D)
    return R * R * (math.pi / 2 + phi) + r * r * (math.pi / 2 - phi) + (R + r) * D * math.cos(phi)


def polygon_circumradius_for_area(radius: float, n_sides: int) -> float:
    """Circumradius of a regular n-gon whose area equals pi*radius^2."""
    return radius * math.sqrt(TWO_PI / (n_sides * math.sin(TWO_PI / n_sides)))


# --------------------------------------------------------------------------
# Core acoustics
# --------------------------------------------------------------------------

def d_eq(area: float) -> float:
    return 2.0 * math.sqrt(area / math.pi)


def conductance(area: float, t: float, k: float = 0.80) -> float:
    """Rayleigh conductivity of an opening with chimney height t. Units: m."""
    return area / (t + k * d_eq(area))


def hole_diameter(G: float, t: float, k: float = 0.80) -> float:
    """Invert G = (pi d^2 / 4) / (t + k d) for d."""
    if G <= 0:
        raise ValueError(f"non-positive conductance {G}")
    return (2.0 / math.pi) * (G * k + math.sqrt(G * G * k * k + math.pi * G * t))


def freq(G_total: float, V: float, c: float) -> float:
    return c / TWO_PI * math.sqrt(G_total / V)


def volume_for(G_total: float, f: float, c: float) -> float:
    return G_total * c * c / (TWO_PI * TWO_PI * f * f)


def midi_f(m: int, a4: float = 440.0) -> float:
    return a4 * 2.0 ** ((m - 69) / 12.0)


def cents(f: float, f_ref: float) -> float:
    return CENTS_PER_LN * math.log(f / f_ref)


# --------------------------------------------------------------------------
# Design solve and prediction
# --------------------------------------------------------------------------

@dataclass
class Hole:
    name: str
    t: float                 # chimney height (core wall + shell along axis), m
    d: float = 0.0           # solved diameter, m
    max_d: float = 10e-3     # finger pad limit, m
    min_d: float = 3e-3      # voicing / viscous-loss floor, m

    @property
    def area(self) -> float:
        return math.pi * self.d * self.d / 4.0


@dataclass
class Design:
    c: float
    G_w_eff: float           # eta_w * G_w, m
    V0: float                # capped cavity volume, all holes closed, m^3
    k: float
    holes: list = field(default_factory=list)

    def G(self, i: int) -> float:
        h = self.holes[i]
        return conductance(h.area, h.t, self.k)

    def predict(self, open_set) -> float:
        open_set = list(open_set)
        G_tot = self.G_w_eff + sum(self.G(i) for i in open_set)
        V = self.V0 - sum(self.holes[i].area * self.holes[i].t for i in open_set)
        return freq(G_tot, V, self.c)


def solve_linear_fingering(f_targets, G_w_eff, holes, k=0.80, c=None,
                           chimney_volume=True, tol=1e-13, max_iter=200) -> Design:
    """Size holes for a linear fingering: f_targets[0] all closed, opening
    hole j (0-based) moves note j -> j+1. Returns a Design with diameters.
    """
    c = c if c is not None else c_air()
    if len(f_targets) != len(holes) + 1:
        raise ValueError("need len(f_targets) == len(holes) + 1")
    V0 = volume_for(G_w_eff, f_targets[0], c)
    des = Design(c=c, G_w_eff=G_w_eff, V0=V0, k=k, holes=holes)
    K = TWO_PI * TWO_PI / (c * c)
    G_open, V_open = 0.0, 0.0
    for j, h in enumerate(holes):
        f = f_targets[j + 1]
        A_j = 0.0
        for _ in range(max_iter):
            V = V0 - V_open - (A_j * h.t if chimney_volume else 0.0)
            G_j = K * f * f * V - G_w_eff - G_open
            d = hole_diameter(G_j, h.t, k)
            A_new = math.pi * d * d / 4.0
            if abs(A_new - A_j) < tol:
                A_j = A_new
                break
            A_j = A_new
        h.d = d
        G_open += conductance(h.area, h.t, k)
        if chimney_volume:
            V_open += h.area * h.t
    return des


# --------------------------------------------------------------------------
# Jet / voicing diagnostics
# --------------------------------------------------------------------------

def jet_speed(p_pa: float, rho: float) -> float:
    return math.sqrt(2.0 * p_pa / rho)


def strouhal(f: float, W: float, U: float) -> float:
    return f * W / U


def pressure_for_strouhal(f: float, W: float, St: float, rho: float) -> float:
    U = f * W / St
    return 0.5 * rho * U * U


def breath_curve(p0: float, semitones: float, alpha: float) -> float:
    """p = p0 * (f/f0)^alpha with f/f0 = 2^(n/12): exponential in semitones."""
    return p0 * 2.0 ** (alpha * semitones / 12.0)


# --------------------------------------------------------------------------
# Tolerance analysis
# --------------------------------------------------------------------------

def monte_carlo(des: Design, fingerings, targets, n=4000, sigma_V_rel=0.005,
                sigma_d=0.05e-3, sigma_Gw_rel=0.0, seed=1):
    """Return per-fingering (rms_cents, p95_abs_cents) under random print errors."""
    rng = random.Random(seed)
    base_d = [h.d for h in des.holes]
    base_V0, base_Gw = des.V0, des.G_w_eff
    errs = [[] for _ in fingerings]
    try:
        for _ in range(n):
            des.V0 = base_V0 * (1.0 + rng.gauss(0.0, sigma_V_rel))
            des.G_w_eff = base_Gw * (1.0 + rng.gauss(0.0, sigma_Gw_rel))
            for h, d0 in zip(des.holes, base_d):
                h.d = d0 + rng.gauss(0.0, sigma_d)
            for j, (fs, ft) in enumerate(zip(fingerings, targets)):
                errs[j].append(cents(des.predict(fs), ft))
    finally:
        des.V0, des.G_w_eff = base_V0, base_Gw
        for h, d0 in zip(des.holes, base_d):
            h.d = d0
    out = []
    for e in errs:
        rms = math.sqrt(sum(x * x for x in e) / len(e))
        s = sorted(abs(x) for x in e)
        out.append((rms, s[int(0.95 * len(s)) - 1]))
    return out
