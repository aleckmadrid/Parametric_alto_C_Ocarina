"""SYNTHETIC measurement data for tests and examples (C2).

Everything this module writes is invented. The truth values below are made up for testing and are
not predictions. Every file it writes carries `synthetic = true` and a banner. Nothing here may be
used as calibration.

    python kernel/synthetic.py --write-examples        # rewrites measurements/ and calibration/ examples

A synthetic body is built from the design (sizing.size_body, first-print k 0.8 diameters), then given a
hidden truth: eta_w, k_hole, position factors, hole offset, volume factor. Its 13 pitches follow from the
physical model with that truth, plus noise in cents per take.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import random
import sys

import config
import holes as holes_mod
import measurements as meas
import ocarina_kernel as ok
import sizing

MM = 1e-3
CM3 = 1e-6

# Invented truth (not a prediction): eta_w a little under the prior, k_hole near the ECAN3 fit,
# holes printed 0.12 mm small, cavity 1.5 % small.
DEFAULT_TRUTH = dict(
    eta_w=0.86, k_hole=1.07, hole_offset_mm=-0.12, volume_factor=0.985,
    # Position factors by hole name. Bulb-end holes a little strong, tail holes weaker. Geometric mean 1 (normalised below).
    psi={"sub1": 1.04, "sub2": 0.97, "R_pinky": 0.82, "R_ring": 0.88, "R_middle": 0.93, "R_index": 1.02,
         "L_pinky": 1.12, "L_ring": 1.05, "L_middle": 1.00, "L_index": 1.08, "L_thumb": 0.96, "R_thumb": 1.06},
    breath_p0_pa=150.0, breath_alpha=1.2,
)

# Different shapes get a different (invented) pattern, so the shape test has something to find.
SHAPE_PSI_SCALE = {"P0": 1.0, "P1": 1.0, "P2": 0.95, "P3": 1.0}


def normalise_psi(psi: dict) -> dict:
    """Scale so that the geometric mean is 1 (the convention of the fitter)."""
    g = math.exp(sum(math.log(v) for v in psi.values()) / len(psi))
    return {k: v / g for k, v in psi.items()}


def make_truth(**overrides) -> dict:
    t = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULT_TRUTH.items()}
    t.update(overrides)
    t["psi"] = normalise_psi(t["psi"]) if t.pop("normalise", True) else t["psi"]
    return t


def synth_body(body_id: str, shape: str, v0_target_cm3: float, truth: dict, *, rating: str | None = None,
               room_temp_c: float = 22.0, noise_cents: float = 0.0, noise: str = "gauss", n_takes: int = 3,
               rng: random.Random | None = None, hole_scatter_mm: float = 0.0, volume_scatter_rel: float = 0.0,
               window_scatter_rel: float = 0.0, d_measure_step_mm: float | None = None,
               hz_decimals: int | None = None, mass_decimals: int | None = None, water_temp_c: float = 20.0,
               shape_psi_scale: float = 1.0, params: dict | None = None, hole_noise_mm: float = 0.0) -> meas.BodyMeasurement:
    """One synthetic body. noise is "gauss" (sigma = noise_cents) or "uniform" (+-noise_cents)."""
    rng = rng or random.Random(0)
    P = params if params is not None else config.load_params()
    sz = sizing.size_body(v0_target_cm3, rating, params=P)
    rows = sz.holes.solutions["print"]
    cad = sz.cad_diameters_mm["print"]
    T_room = room_temp_c
    Tt = P["temperature"]
    c = ok.c_air(ok.internal_air_temp_c(T_room, Tt["design_internal_c"], Tt["reference_room_c"], Tt["room_coupling"]))
    # physical truth
    d_print = [(d + truth["hole_offset_mm"] + rng.gauss(0.0, hole_scatter_mm)) * MM for d in cad]
    chim = [r.chimney_mm * MM for r in rows]
    psi = []
    for r in rows:
        v = truth["psi"][r.name]
        psi.append(v * shape_psi_scale)
    V0 = v0_target_cm3 * CM3 * truth["volume_factor"] * (1.0 + rng.gauss(0.0, volume_scatter_rel))
    X = truth["eta_w"] * sz.voicing.G_w() * (1.0 + rng.gauss(0.0, window_scatter_rel))
    f_true = holes_mod.predict_scale(X, V0, d_print, chim, truth["k_hole"], c, psi)
    # what the person would measure
    notes = []
    m0 = meas.note_midi(sz.notes[0])
    for name, ft, tgt in zip(sz.notes, f_true, sz.f_targets_hz):
        takes, press = [], []
        for _ in range(n_takes):
            if noise == "uniform":
                e = rng.uniform(-noise_cents, noise_cents)
            else:
                e = rng.gauss(0.0, noise_cents)
            f = ft * 2.0 ** (e / 1200.0)
            if hz_decimals is not None:
                f = round(f, hz_decimals)
            takes.append(ok.cents(f, tgt))
            n_semi = meas.note_midi(name) - m0
            press.append(round(truth["breath_p0_pa"] * 2.0 ** (truth["breath_alpha"] * n_semi / 12.0) * (1 + rng.gauss(0, 0.03)), 1))
        notes.append(meas.NoteMeas(name, tgt, takes, press))
    d_meas = []
    for d in d_print:
        dm = d / MM + rng.gauss(0.0, hole_noise_mm)
        if d_measure_step_mm:
            dm = round(dm / d_measure_step_mm) * d_measure_step_mm
        d_meas.append(dm * MM)
    holes = [meas.HoleMeas(r.name, r.opens, r.chimney_mm * MM, cd * MM, dm) for r, cd, dm in zip(rows, cad, d_meas)]
    mass_g = V0 * meas.water_density_kg_m3(water_temp_c) * 1e3
    if mass_decimals is not None:
        mass_g = round(mass_g, mass_decimals)
    v = sz.voicing
    return meas.BodyMeasurement(
        id=body_id, shape=shape, voicing_hash=v.version_hash, target_v0_cm3=sz.v0_cm3, synthetic=True,
        window_area_mm2=v.window_area_mm2, wall_at_window_mm=v.wall_at_window_mm,
        v0_m3=mass_g * 1e-3 / meas.water_density_kg_m3(water_temp_c), room_temp_c=room_temp_c, holes=holes, notes=notes, date="SYNTHETIC",
        comment="SYNTHETIC: invented truth values, not a measurement", water_net_mass_g=mass_g, water_temp_c=water_temp_c)


def round1_set(seed: int = 7, noise_cents: float = 2.0, truth: dict | None = None, **kw) -> list:
    """Synthetic version of the Stage 2 set: P0 at 65/80/95/125, two more P0-80, and P1-P3 at 80 cm3."""
    rng = random.Random(seed)
    truth = truth or make_truth()
    plan = [("P0-65", "P0", 65.0), ("P0-80-a", "P0", 80.0), ("P0-80-b", "P0", 80.0), ("P0-80-c", "P0", 80.0),
            ("P0-95", "P0", 95.0), ("P0-125", "P0", 125.0), ("P1-80", "P1", 80.0), ("P2-80", "P2", 80.0),
            ("P3-80", "P3", 80.0)]
    temps = [21.0, 22.5, 23.0, 22.0, 24.0, 20.5, 22.0, 23.5, 21.5]
    out = []
    for (bid, shape, v0), T in zip(plan, temps):
        out.append(synth_body(bid, shape, v0, truth, room_temp_c=T, noise_cents=noise_cents, rng=rng,
                              shape_psi_scale=SHAPE_PSI_SCALE.get(shape, 1.0), **kw))
    return out


def roundtrip_through_file(body: meas.BodyMeasurement, path) -> meas.BodyMeasurement:
    """Write the synthetic body as a measurement file and load it back (tests the file path)."""
    meas.write_measurement_file(path, body)
    return meas.load_measurement(path)


# --------------------------------------------------------------------------
# Example files
# --------------------------------------------------------------------------

def write_examples(root=None) -> list:
    """Write the blank template, one synthetic example, the synthetic round-1 set and the synthetic constants file."""
    import calibration
    import fitter
    root = pathlib.Path(root) if root else config.ROOT
    P = config.load_params()
    written = []

    # blank template for P0 at 80 cm3
    sz = sizing.size_body(80.0, params=P)
    tmpl = meas.template_from_sizing(sz, "P0-80-a", "P0")
    p = root / "measurements" / "template-blank.toml"
    meas.write_measurement_file(p, tmpl, blank=True)
    written.append(p)

    # synthetic round-1 set, rounded the way a person would read the instruments
    bodies = round1_set(noise_cents=2.0, d_measure_step_mm=0.05, hz_decimals=1, mass_decimals=1)
    sdir = root / "measurements" / "synthetic-round1"
    loaded = []
    for b in bodies:
        path = sdir / f"{b.id}.synthetic.toml"
        meas.write_measurement_file(path, b)
        loaded.append(meas.load_measurement(path))
        written.append(path)
    ex = root / "measurements" / "example-synthetic-P0-80.toml"
    meas.write_measurement_file(ex, bodies[1])           # P0-80-a
    written.append(ex)

    fit = fitter.fit_bodies(loaded, P)
    cal = calibration.calibration_from_fit(fit, loaded, params=P)
    cp = root / "calibration" / "synthetic-fitted-constants.toml"
    calibration.write_calibration(cp, cal)
    written.append(cp)
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write SYNTHETIC example files (invented data, labelled as such).")
    ap.add_argument("--write-examples", action="store_true")
    ap.add_argument("--root", default=None)
    args = ap.parse_args(argv)
    if not args.write_examples:
        ap.print_help()
        return 0
    for p in write_examples(args.root):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
