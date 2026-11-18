"""Stage 1 voicing stubs (docs/04-testing-phase.md): a small chamber with a generated voicing and no holes.

No Blender imports. A stub is built by body.build_body with a sizing record from this module instead of
the kernel's BodySizing. The voicing record comes from the kernel (voicing.make_voicing), so a stub that
carries the 80 cm3 window has the same voicing hash as the 80 cm3 body. That is the point of Stage 1.

    RECIPES              the stubs of doc 04: V-a, V-af (plain build), V-b, V-d and the optional V-a0, V-a35 (labium coupons)
                         and V-a3 (3 mm wall)
    stub_sizing(...)     the sizing record of one stub

The stub's pitch at a known volume gives eta_w * G_w for its voicing (kernel fitter.eta_w_from_stub).
The pitch printed in the reports is a PREDICTION with the prior eta_w; nothing here is measured.
"""
from __future__ import annotations

import types
from dataclasses import dataclass, field

from . import kernel_bridge

# id: (window of this body volume in cm3, forced shape or None, labium offset in mm or None for the default of
#      [voicing_rules] (-0.2 mm since 2026-11-17), what it tests, optional, wall at the window in mm or None for the default,
#      build: None for the build of [voicing_rules] or "plain" for the plain build)
# Stub V-c (the 125 cm3 window) was dropped with the 125 cm3 step. The labium offset is never positive.
# Every stub carries the build of the rules (ellipse cut, standing neck, lowered pipe, pocket blend; owner decisions of
# 2026-11-18) except V-af, which has the plain build: fan cut, level windway, box stub. The pair V-a / V-af says what
# the owner's build is worth, and whether it speaks, before the eight bodies are printed with it (decision 5).
# V-b, the forced rounded rectangle, has the plain build too: the ellipse cut is made for the teardrop (the add-on refuses
# it on another shape), so the shape pair is V-b against V-af, at one build.
RECIPES = {
    "V-a": (80.0, None, None, "Baseline: the 80 cm³ window with the build of the bodies", False, None, None),
    "V-af": (80.0, None, None, "V-a with the plain build (fan cut, level windway, box stub): what the ellipse cut, the tilt and the neck are worth", False, None, "plain"),
    "V-b": (80.0, "rounded_rectangle", None, "Window shape at equal area; pairs with V-af (both have the plain build)", False, None, "plain"),
    "V-d": (65.0, None, None, "Proven-band reference: the 65 cm³ window", False, None, None),
    "V-a0": (80.0, None, 0.0, "V-a with the labium offset 0 mm (labium height: brackets the −0.2 mm default)", True, None, None),
    "V-a35": (80.0, None, -0.35, "V-a with the labium offset −0.35 mm (labium height: brackets the −0.2 mm default)", True, None, None),
    "V-a3": (80.0, None, None, "The 80 cm³ window at the 3 mm window wall: η_w at 3 mm, against V-a at 4 mm", True, 3.0, None),
}
STUB_PRESET = "S0"


@dataclass
class StubSizing:
    """What body.build_body and the checks read from a sizing record, for a body without holes."""
    stub_id: str
    v0_cm3: float                        # the stub volume: capped air, window capped at its inner plane
    voicing: object                      # kernel voicing.Voicing
    window_for_v0_cm3: float             # the body volume this window was sized for
    purpose: str
    optional: bool
    internal_temp_c: float
    c_m_s: float
    notes: list
    f_targets_hz: list                   # the scale of the full instrument (the top note is used by the cavity-mode check)
    eta_w: float
    predicted_pitch_hz: float            # kernel voicing.stub_pitch_hz with the prior eta_w: a prediction
    checks: list
    holes: object = field(default_factory=lambda: types.SimpleNamespace(solutions={"print": []}, tubes_mm=[]))
    cad_diameters_mm: dict = field(default_factory=lambda: {"print": []})
    volume_factor: float = 1.0
    hole_offset_mm: float = 0.0
    cavity_volume_for_mesh_cm3: float = 0.0
    wall_chimney_air_cm3: float = 0.0
    tube_plastic_cm3: float = 0.0


def stub_sizing(stub_id: str, params: dict, stub_volume_cm3: float) -> StubSizing:
    """Sizing record of the stub `stub_id` (a key of RECIPES) at the given capped volume."""
    if stub_id not in RECIPES:
        raise ValueError(f"unknown stub {stub_id!r}; known: {', '.join(RECIPES)}")
    k = kernel_bridge.kernel()
    v0_window, shape, offset, purpose, optional, wall, build = RECIPES[stub_id]
    kwargs = dict(params=params)
    if shape:
        kwargs["shape"] = shape
    if wall is not None:
        kwargs["wall_at_window_mm"] = wall
    if build is not None:
        kwargs["build"] = build
    v = k.voicing.make_voicing(v0_window, labium_offset_mm=offset, **kwargs)
    ref = k.sizing.size_body(v0_window, params=params)          # for the scale, the air temperature and the speed of sound
    pitch = k.voicing.stub_pitch_hz(v, stub_volume_cm3, internal_temp_c=ref.internal_temp_c)
    return StubSizing(stub_id=stub_id, v0_cm3=float(stub_volume_cm3), voicing=v, window_for_v0_cm3=v0_window, purpose=purpose,
                      optional=optional, internal_temp_c=ref.internal_temp_c, c_m_s=ref.c_m_s, notes=ref.notes,
                      f_targets_hz=ref.f_targets_hz, eta_w=v.eta_w_assumed or ref.eta_w, predicted_pitch_hz=pitch,
                      checks=v.checks(), cavity_volume_for_mesh_cm3=float(stub_volume_cm3))
