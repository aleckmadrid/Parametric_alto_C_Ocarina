"""The cavity surface as plain mathematics. Standard library only, no Blender imports.

The Geometry Nodes group in cavity_nodes.py builds the cavity mesh from the formula below. This
module evaluates the same formula in Python, in double precision. The add-on uses it to find the
voicing port and its frame, to convert the hole template to surface coordinates by arc length, and
to give each hole its axis. The geometry check compares the mesh against this module, so the two
copies of the formula cannot drift apart unnoticed.

The surface (unit shape, reference length LREF along the spine)
    theta in [0, pi]      along the body. t = (1 - cos theta) / 2 is the position on the spine, 0..1.
    phi   in [0, 2 pi)    around the section. 0 = far side (+Y), 90 deg = top (+Z, finger deck),
                          180 deg = player side (-Y), 270 deg = bottom (-Z, thumbs and voicing).
    half-width   a(t) = LREF / 2 * Sw(t) * sin theta
    half-height  b(t) = LREF / 2 * Sh(t) * sin theta
        Sw, Sh: uniform Catmull-Rom splines through the 7 station values (stations at t = k / 6).
        sin theta = sqrt(4 t (1 - t)) is the envelope of an ellipse. Constant station values give
        an exact ellipsoid, and the station value is then width / length. The end stations set
        how blunt the end caps are.
    section      superellipse: y' = sgn(cos phi) |cos phi|^(2/n) a,  z' = sgn(sin phi) |sin phi|^(2/n) b
    spine        a circular arc in the XY plane with total bend angle `bend_deg` (0 = straight),
                 length LREF. Positive bend moves both ends toward +Y (away from the player).
    point        C(t) + y' N(t) + z' Z,   N = left normal of the spine in the XY plane

Body coordinates (millimetres): the surface is translated so that the voicing port is the origin,
then scaled by `scale` about the origin. So the port never moves when the volume changes.
X runs along the body from the left-hand end (t = 0) to the right-hand end (t = 1), +Y points away
from the player, +Z is the finger deck.
"""
from __future__ import annotations

import math

LREF = 100.0
N_STATIONS = 7


def catmull_rom(values, t: float) -> float:
    """Uniform Catmull-Rom spline through `values` at t = k / (n - 1). The end segments use a
    phantom point by linear extrapolation (2 v0 - v1). t is clamped to [0, 1]."""
    n = len(values)
    x = min(max(t, 0.0), 1.0) * (n - 1)
    i = min(int(math.floor(x)), n - 2)
    s = x - i
    p1, p2 = values[i], values[i + 1]
    p0 = values[i - 1] if i > 0 else 2.0 * values[0] - values[1]
    p3 = values[i + 2] if i + 2 < n else 2.0 * values[n - 1] - values[n - 2]
    return 0.5 * (2.0 * p1 + (p2 - p0) * s + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * s * s
                  + (3.0 * p1 - p0 - 3.0 * p2 + p3) * s * s * s)


def _spow(c: float, e: float) -> float:
    return math.copysign(abs(c) ** e, c) if c != 0.0 else 0.0


def superellipse_area_factor(n: float) -> float:
    """Area of a superellipse with half-axes a, b and exponent n, divided by a * b (pi for n = 2)."""
    return 4.0 * math.gamma(1.0 + 1.0 / n) ** 2 / math.gamma(1.0 + 2.0 / n)


class Cavity:
    """One cavity preset at one scale. All results are in body coordinates (mm) unless a name says raw."""

    def __init__(self, width, height, exponent: float = 2.0, bend_deg: float = 0.0,
                 port_u: float = 0.5, port_angle_deg: float = 45.0, scale: float = 1.0, name: str = ""):
        if len(width) != N_STATIONS or len(height) != N_STATIONS:
            raise ValueError(f"a cavity needs {N_STATIONS} width and {N_STATIONS} height stations")
        self.width = [float(v) for v in width]
        self.height = [float(v) for v in height]
        self.exponent = float(exponent)
        self.bend_deg = float(bend_deg)
        self.name = name
        self.scale = float(scale)
        self.port_theta = self.port_phi = 0.0
        self._port_raw = (0.0, 0.0, 0.0)
        self.set_port(port_u, port_angle_deg)

    # ------------------------------------------------------------------ construction helpers
    @classmethod
    def from_preset(cls, preset: dict, scale: float = 1.0, name: str = "") -> "Cavity":
        return cls(preset["width"], preset["height"], preset.get("exponent", 2.0), preset.get("bend_deg", 0.0),
                   preset.get("port_u", 0.5), preset.get("port_angle_deg", 45.0), scale, name or preset.get("name", ""))

    def set_port(self, port_u: float, port_angle_deg: float) -> None:
        """Voicing port: position on the spine (0..1) and angle around the section, measured from the
        bottom (-Z) toward the player (-Y). 45 deg is the lower player-side quadrant."""
        self.port_u = float(port_u)
        self.port_angle_deg = float(port_angle_deg)
        self.port_theta = math.acos(1.0 - 2.0 * self.port_u)
        self.port_phi = math.radians(270.0 - self.port_angle_deg)
        self._port_raw = self.raw_point(self.port_theta, self.port_phi)

    def snap_port_to_grid(self, n_u: int, n_v: int) -> None:
        """Move the port to the nearest vertex of a grid with n_u rings (theta = pi i / (n_u - 1)) and
        n_v segments (phi = 2 pi j / n_v), so that the port is a vertex of the mesh."""
        i = min(max(round(self.port_theta / math.pi * (n_u - 1)), 1), n_u - 2)
        j = round(self.port_phi / (2.0 * math.pi) * n_v) % n_v
        theta = math.pi * i / (n_u - 1)
        phi = 2.0 * math.pi * j / n_v
        self.set_port((1.0 - math.cos(theta)) / 2.0, 270.0 - math.degrees(phi))
        self.port_theta, self.port_phi = theta, phi
        self._port_raw = self.raw_point(theta, phi)

    # ------------------------------------------------------------------ the formula
    def half_axes_raw(self, theta: float):
        t = (1.0 - math.cos(theta)) / 2.0
        env = math.sin(theta)
        return (0.5 * LREF * catmull_rom(self.width, t) * env, 0.5 * LREF * catmull_rom(self.height, t) * env)

    def spine_raw(self, t: float):
        """Spine point, tangent and left normal at t (unit shape)."""
        beta = math.radians(self.bend_deg)
        if abs(beta) < 1e-9:
            return (LREF * (t - 0.5), 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
        rho = LREF / beta
        psi = beta * (t - 0.5)
        return ((rho * math.sin(psi), rho * (1.0 - math.cos(psi)), 0.0),
                (math.cos(psi), math.sin(psi), 0.0), (-math.sin(psi), math.cos(psi), 0.0))

    def raw_point(self, theta: float, phi: float):
        t = (1.0 - math.cos(theta)) / 2.0
        a, b = self.half_axes_raw(theta)
        e = 2.0 / self.exponent
        yy = _spow(math.cos(phi), e) * a
        zz = _spow(math.sin(phi), e) * b
        c, _, n = self.spine_raw(t)
        return (c[0] + yy * n[0], c[1] + yy * n[1], c[2] + zz)

    def point(self, theta: float, phi: float):
        p = self.raw_point(theta, phi)
        s, o = self.scale, self._port_raw
        return ((p[0] - o[0]) * s, (p[1] - o[1]) * s, (p[2] - o[2]) * s)

    def to_body(self, raw):
        s, o = self.scale, self._port_raw
        return ((raw[0] - o[0]) * s, (raw[1] - o[1]) * s, (raw[2] - o[2]) * s)

    # ------------------------------------------------------------------ derivatives, normal, frames
    def d_theta(self, theta: float, phi: float, h: float = 1e-5):
        h = min(h, 0.5 * theta, 0.5 * (math.pi - theta)) if 0.0 < theta < math.pi else h
        p0, p1 = self.point(theta - h, phi), self.point(theta + h, phi)
        return tuple((b - a) / (2.0 * h) for a, b in zip(p0, p1))

    def d_phi(self, theta: float, phi: float, h: float = 1e-5):
        p0, p1 = self.point(theta, phi - h), self.point(theta, phi + h)
        return tuple((b - a) / (2.0 * h) for a, b in zip(p0, p1))

    def normal(self, theta: float, phi: float):
        """Unit outward normal. The section runs counter-clockwise seen from +X, so the outward normal
        is d_phi x d_theta ... with the sign fixed by pointing away from the spine."""
        du, dv = self.d_theta(theta, phi), self.d_phi(theta, phi)
        n = _cross(dv, du)
        ln = _norm(n)
        if ln < 1e-12:
            raise ValueError("no normal at a pole")
        n = tuple(c / ln for c in n)
        t = (1.0 - math.cos(theta)) / 2.0
        c = self.to_body(self.spine_raw(t)[0])
        p = self.point(theta, phi)
        if _dot(n, tuple(pi - ci for pi, ci in zip(p, c))) < 0.0:
            n = tuple(-x for x in n)
        return n

    def port_frame(self):
        """Voicing frame at the port (the origin): (x, y, z) unit vectors in body coordinates.
        z = outward normal. x = jet direction: tangent to the section, pointing from the player side
        toward the bottom of the body (increasing phi). y = z cross x."""
        z = self.normal(self.port_theta, self.port_phi)
        dv = self.d_phi(self.port_theta, self.port_phi)
        x = tuple(d - _dot(dv, z) * zc for d, zc in zip(dv, z))
        lx = _norm(x)
        x = tuple(c / lx for c in x)
        return x, _cross(z, x), z

    def curvature_radius_along(self, theta: float, phi: float, direction, step_mm: float = 0.5) -> float:
        """Radius of curvature of the surface along a tangent direction, by a 3-point fit on the
        section/meridian chart. Used for information only (sag under the voicing)."""
        du, dv = self.d_theta(theta, phi), self.d_phi(theta, phi)
        # solve direction = alpha du + beta dv (least squares in the tangent plane)
        a11, a12, a22 = _dot(du, du), _dot(du, dv), _dot(dv, dv)
        b1, b2 = _dot(direction, du), _dot(direction, dv)
        det = a11 * a22 - a12 * a12
        al, be = (b1 * a22 - b2 * a12) / det, (a11 * b2 - a12 * b1) / det
        p0 = self.point(theta, phi)
        n = self.normal(theta, phi)
        pp = self.point(theta + al * step_mm, phi + be * step_mm)
        pm = self.point(theta - al * step_mm, phi - be * step_mm)
        sag = -0.5 * (_dot(tuple(a - b for a, b in zip(pp, p0)), n) + _dot(tuple(a - b for a, b in zip(pm, p0)), n))
        return float("inf") if sag <= 1e-12 else step_mm * step_mm / (2.0 * sag)

    # ------------------------------------------------------------------ size
    @property
    def length_mm(self) -> float:
        """Internal length along the spine."""
        return LREF * self.scale

    def volume_mm3(self, n: int = 2000) -> float:
        """Volume of the analytic surface: integral of the section area along the spine. The mesh has
        a slightly smaller volume at the same scale (it is inscribed)."""
        k = superellipse_area_factor(self.exponent)
        total = 0.0
        for i in range(n):
            th = math.pi * (i + 0.5) / n
            a, b = self.half_axes_raw(th)
            total += k * a * b * 0.5 * LREF * math.sin(th) * (math.pi / n)      # dt = sin(theta) / 2 dtheta
        return total * self.scale ** 3

    def scale_for_volume(self, volume_mm3: float) -> float:
        unit = Cavity(self.width, self.height, self.exponent, self.bend_deg, self.port_u, self.port_angle_deg, 1.0)
        return (volume_mm3 / unit.volume_mm3()) ** (1.0 / 3.0)

    def max_width_height_mm(self, n: int = 400):
        w = h = 0.0
        for i in range(1, n):
            a, b = self.half_axes_raw(math.pi * i / n)
            w, h = max(w, 2 * a), max(h, 2 * b)
        return w * self.scale, h * self.scale

    # ------------------------------------------------------------------ arc lengths (for the hole template)
    def meridian_arc(self, theta0: float, theta1: float, phi: float, n: int = 400) -> float:
        """Signed arc length along the surface at fixed phi, from theta0 to theta1."""
        sgn = 1.0 if theta1 >= theta0 else -1.0
        lo, hi = min(theta0, theta1), max(theta0, theta1)
        steps = max(8, int(n * (hi - lo) / math.pi))
        total, prev = 0.0, self.point(lo, phi)
        for i in range(1, steps + 1):
            p = self.point(lo + (hi - lo) * i / steps, phi)
            total += _dist(p, prev)
            prev = p
        return sgn * total

    def section_arc(self, theta: float, phi0: float, phi1: float, n: int = 720) -> float:
        """Signed arc length around the section at fixed theta, from phi0 to phi1."""
        sgn = 1.0 if phi1 >= phi0 else -1.0
        lo, hi = min(phi0, phi1), max(phi0, phi1)
        steps = max(8, int(n * (hi - lo) / (2.0 * math.pi)))
        total, prev = 0.0, self.point(theta, lo)
        for i in range(1, steps + 1):
            p = self.point(theta, lo + (hi - lo) * i / steps)
            total += _dist(p, prev)
            prev = p
        return sgn * total

    def theta_at_meridian_arc(self, theta_c: float, s_mm: float, phi: float) -> float:
        """theta where the arc length from theta_c along the meridian `phi` equals s_mm (toward larger
        theta for positive s). Raises ValueError when the body is too short."""
        lo, hi = (theta_c, math.pi - 1e-3) if s_mm >= 0 else (1e-3, theta_c)
        end = hi if s_mm >= 0 else lo
        if abs(self.meridian_arc(theta_c, end, phi)) < abs(s_mm):
            raise ValueError(f"the body is too short for a hole {s_mm:.1f} mm from the layout centre")
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if self.meridian_arc(theta_c, mid, phi) < s_mm:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    def phi_at_section_arc(self, theta: float, phi_ref: float, w_mm: float) -> float:
        """phi where the arc length around the section from phi_ref equals w_mm (toward larger phi for
        positive w). Limited to a quarter turn each way."""
        lo, hi = (phi_ref, phi_ref + 0.5 * math.pi) if w_mm >= 0 else (phi_ref - 0.5 * math.pi, phi_ref)
        end = hi if w_mm >= 0 else lo
        if abs(self.section_arc(theta, phi_ref, end)) < abs(w_mm):
            raise ValueError(f"the section is too small for a hole {w_mm:.1f} mm off the reference line")
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if self.section_arc(theta, phi_ref, mid) < w_mm:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)


# ---------------------------------------------------------------------- small vector helpers

def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    return math.sqrt(_dot(a, a))


def _dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
