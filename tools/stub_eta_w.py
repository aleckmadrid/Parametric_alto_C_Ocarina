"""Window efficiency eta_w from the filled measurement files of Stage 1 voicing stubs (plain Python).

    python tools/stub_eta_w.py addon_out/stage1/V-a/V-a_measurement.toml [more files ...]

A stub has a voicing and no holes, so its pitch at a known volume gives eta_w * G_w directly
(kernel fitter.eta_w_from_stub). The file format is the kernel's stub template (measurements.load_stub):
fill in the water mass, the room temperature and three takes of the pitch. Stage 1 writes a blank file for
every stub next to its STL. A file that is not complete is reported with the list of what is missing.
"""
from __future__ import annotations

import glob
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ocarina_addon import kernel_bridge  # noqa: E402  (standard library only)


def main(argv) -> int:
    if not argv:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    k = kernel_bridge.kernel()
    P = kernel_bridge.load_params()
    paths = [p for a in argv for p in (sorted(glob.glob(a)) or [a])]
    code = 0
    print("| Stub | Voicing hash | Volume, cm³ (target) | Pitch, Hz (predicted) | Spread, cents | η_w·G_w, mm | η_w | Gate 1: speaks / overblows |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for path in paths:
        try:
            m = k.measurements.load_stub(path)
        except k.measurements.MeasurementIncomplete as exc:
            print(f"| {pathlib.Path(path).name} | not complete: {'; '.join(exc.missing)} | | | | | | |")
            code = 1
            continue
        r = k.fitter.eta_w_from_stub(m.f_hz, m.v0_cm3, m.window_area_mm2, m.wall_at_window_mm, m.room_temp_c, P)
        yes_no = lambda x: "–" if x is None else ("yes" if x else "no")
        print(f"| {m.id}{' (SYNTHETIC)' if m.synthetic else ''} | `{m.voicing_hash}` | {m.v0_cm3:.2f} ({m.target_volume_cm3:g}) | "
              f"{m.f_hz:.1f} ({m.predicted_hz:.1f}) | {m.spread_cents:.1f} | {r['X_w_mm']:.3f} | {r['eta_w']:.3f} | "
              f"{yes_no(m.speaks_cleanly)} / {yes_no(m.overblows_a_semitone_cleanly)} |")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
