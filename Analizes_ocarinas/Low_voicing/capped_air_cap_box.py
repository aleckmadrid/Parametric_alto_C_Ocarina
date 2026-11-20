"""Why the capped air measured on the finished mesh reads low when the voicing sits near the thumb holes. numpy only.

    python Analizes_ocarinas/Low_voicing/capped_air_cap_box.py

The check volume_capped_air has two numbers: the air mesh built beside the body, and the air measured on the finished
mesh by columns (body.measure_capped_air_cm3). The second one leaves out everything inside two "cap boxes" on the
voicing side (body.cap_boxes). Box k1 lies above the window's inner plane and reaches 26.6 mm along the body on each
side of the window. A thumb hole that lies beside the window at about the level of that plane has part of its own air
inside the box, and that air is then not counted. This script estimates that part for each trial (random points in
each hole's chimney) and sets it against the difference of the two numbers in the trial's report.
"""
import json, math, sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from ocarina_addon import cavity_math as cm, presets
rng = np.random.default_rng(1)
for pid, trial, port in (("P4", "lv-30", 30), ("P4", "lv-20f", 20), ("P4", "lv-10f", 10), ("P4", "lv-0f", 0), ("P1", "lv-30", 30), ("P1", "lv-10f", 10), ("P1", "lv-0f", 0)):
    cav = cm.Cavity.from_preset(dict(presets.get_preset(pid), port_angle_deg=port))
    cav.snap_port_to_grid(129, 128)
    fx, fy, fz = (np.array(a) for a in cav.port_frame())
    o = 0.05 * fz
    d = json.load(open(__import__("pathlib").Path(__file__).resolve().parents[2] / f"addon_checks/{pid}-80-{trial}.json", encoding="utf-8"))
    L, W, wall, Lw = 9.65, 8.81, 4.0, 30.0
    reach = None
    v = d["measurements"]["voicing"]
    # the cap box k1 of body.cap_boxes: z_top = wall + 1 + (wall + L) sin(stub pitch) + 0.5, reach = (z_top - e) / tan(ramp)
    z_top = wall + 1.0 + (wall + L) * math.sin(math.radians(8.0)) + 0.5
    reach = (z_top - 0.4) / math.tan(math.radians(20.0))
    lo = np.array([-L - Lw - 3.0, -(0.5 * W + reach + 3.0), 0.02])
    hi = np.array([reach + 3.0, 0.5 * W + reach + 3.0, 99.0])
    total = 0.0
    parts = []
    for h in d["measurements"]["holes"]:
        c, a = np.array(h["centre"], float), np.array(h["axis"], float)
        r = 0.5 * h["d_measured_mm"]
        # points in the chimney: the cylinder from the cavity surface to the outer skin
        u = np.cross(a, [1.0, 0.0, 0.0]); u /= np.linalg.norm(u); w = np.cross(a, u)
        n = 40000
        rr, th, t = r * np.sqrt(rng.random(n)), 2 * math.pi * rng.random(n), wall * rng.random(n)
        P = c + np.outer(rr * np.cos(th), u) + np.outer(rr * np.sin(th), w) + np.outer(t, a)
        Q = (P - o) @ np.stack([fx, fy, fz], axis=1)
        inside = ((Q > lo) & (Q < hi)).all(axis=1).mean()
        vol = math.pi * r * r * wall * inside / 1000.0
        if vol > 1e-4:
            parts.append(f"{h['name']} {vol:.3f} cm3 ({100 * inside:.0f} % of its chimney)")
        total += vol
    m = d["measurements"]["volume"]
    print(f"{pid} {trial}: port built {cav.port_angle_deg:.2f} deg; hole air inside the cap box {total:.3f} cm3 [{'; '.join(parts)}]; "
          f"built {m['capped_air_built_cm3']:.3f}, measured {m['capped_air_measured_cm3']:.3f}, difference {m['capped_air_built_cm3'] - m['capped_air_measured_cm3']:.3f} cm3; half-width of the box along the body {0.5 * W + reach + 3.0:.1f} mm")
