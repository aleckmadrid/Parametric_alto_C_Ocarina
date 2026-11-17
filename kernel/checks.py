"""Pass/fail checks from docs/02-unified-plan.md (pre-export checks) and doc 03 sections 2 and 8.

Every check returns a CheckResult. `status` is one of:
    "pass"      inside the rule
    "needs_fem" outside the comfortable rule, inside the hard limit (cavity-mode check only)
    "fail"      outside the hard limit
A caller that prints a body on purpose past a limit must say so itself; the check does not
know about waivers and reports the maths.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import ocarina_kernel as ok


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str            # "pass" | "needs_fem" | "fail"
    value: float           # the number that was checked
    limit: float           # the limit it was checked against
    message: str

    @property
    def ok(self) -> bool:
        return self.status == "pass"

    @property
    def blocking(self) -> bool:
        return self.status == "fail"

    def to_dict(self) -> dict:
        return {"name": self.name, "status": self.status, "value": self.value,
                "limit": self.limit, "message": self.message}


def range_ratio_identity(f_top: float, f_low: float) -> float:
    """sum(G_i) / (eta_w G_w) without chimney volume: (f_top / f_low)^2 - 1. A4..F6 gives 9.08."""
    return (f_top / f_low) ** 2 - 1.0


def range_ratio_check(sum_G: float, G_w_eff: float, limit: float = 10.0) -> CheckResult:
    """Range-ratio check (doc 02, doc 03 identity 1). Inputs in metres; any common unit works."""
    ratio = sum_G / G_w_eff
    status = "pass" if ratio <= limit else "fail"
    msg = (f"sum(G_i) / (eta_w G_w) = {ratio:.2f}; single-chamber ceiling {limit:.1f}"
           + ("" if status == "pass" else " exceeded: the holes cannot supply this range for this window"))
    return CheckResult("range_ratio", status, ratio, limit, msg)


def cavity_mode_ratio(L_int_m: float, f_top: float, c: float) -> float:
    """First closed-closed cavity mode c / (2 L), divided by the top note. Conservative (lowest) estimate."""
    return c / (2.0 * L_int_m) / f_top


def cavity_mode_check(L_int_m: float, f_top: float, c: float,
                      margin: float = 1.0, fem_margin: float = 1.3) -> CheckResult:
    """Cavity-mode check: first internal resonance c/(2 L_int) against the top note (F6).

    ratio >= fem_margin  pass        (doc 03 section 8: the lumped model is safe)
    margin <= ratio < fem_margin  needs_fem (the plan allows it only with a FEM check on the top fingerings)
    ratio < margin       fail        (the first mode lies below the top note)
    """
    ratio = cavity_mode_ratio(L_int_m, f_top, c)
    if ratio >= fem_margin:
        status, msg = "pass", f"c/(2L) = {ratio:.2f} x F6 (rule: at least {fem_margin:.1f})"
    elif ratio >= margin:
        status, msg = "needs_fem", f"c/(2L) = {ratio:.2f} x F6: below {fem_margin:.1f}, so a FEM check of the top fingerings is required"
    else:
        status, msg = "fail", f"c/(2L) = {ratio:.2f} x F6: the first cavity mode lies below the top note"
    return CheckResult("cavity_mode", status, ratio, fem_margin, msg)


def ellipsoid_length_m(v_m3: float, r_length: float = 2.2, r_width: float = 1.5) -> float:
    """Length of an ellipsoid of volume v with axis ratios length : width : height = r_length : r_width : 1.

    The P0 control egg (2.2 : 1.5 : 1) uses this. V = pi/6 * L * W * H.
    """
    H = (6.0 * v_m3 / (math.pi * r_length * r_width)) ** (1.0 / 3.0)
    return r_length * H


def hole_limit_check(name: str, d_m: float, min_d_m: float, max_d_m: float) -> CheckResult:
    """Hole floor (print and voicing) and finger-pad limit."""
    if d_m < min_d_m - 1e-9:
        return CheckResult(f"hole_floor:{name}", "fail", d_m, min_d_m,
                           f"{name}: {d_m * 1e3:.2f} mm is below the {min_d_m * 1e3:.1f} mm floor")
    if d_m > max_d_m + 1e-9:
        return CheckResult(f"hole_pad:{name}", "fail", d_m, max_d_m,
                           f"{name}: {d_m * 1e3:.2f} mm is above the {max_d_m * 1e3:.1f} mm finger-pad limit")
    return CheckResult(f"hole_limits:{name}", "pass", d_m, max_d_m, f"{name}: {d_m * 1e3:.2f} mm inside the limits")


def wh_ratio_check(window_length_m: float, exit_height_m: float, band=(7.0, 10.0)) -> CheckResult:
    """Windway check: W/h (window length over exit height) inside the band."""
    r = window_length_m / exit_height_m
    lo, hi = band
    status = "pass" if lo <= r <= hi else "fail"
    return CheckResult("wh_ratio", status, r, hi, f"W/h = {r:.2f} (band {lo:.0f}..{hi:.0f})")
