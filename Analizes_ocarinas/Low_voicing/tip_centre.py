"""(python Analizes_ocarinas/Low_voicing/tip_centre.py, after the trials are built; it reads addon_out/.)

Where the outside of the mouthpiece tip lies against the middle of the body, read from the finished STL.

The trial table gives the pipe's mouth end. The eye reads the middle of the neck's outside at the tip instead. Body frame:
X along the body, +Y away from the player, +Z the finger deck; the mouth end is the body's extreme toward -Y."""
import json
import pathlib
import struct
import sys

import numpy as np

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[2]


def read_stl(path):
    data = path.read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    if 84 + 50 * n == len(data):
        rec = np.frombuffer(data, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n, offset=84)
        return rec["v"].reshape(-1, 3).astype(float)
    pts = [list(map(float, line.split()[1:4])) for line in data.decode().splitlines() if line.strip().startswith("vertex")]
    return np.array(pts)


for pid in ("P4", "P1"):
    for trial in ("lv-30", "lv-10f", "lv-10fwdn", "lv-10fwdnr"):
        bid = f"{pid}-80-{trial}"
        stl = ROOT / "addon_out" / bid / f"{bid}.stl"
        tj = ROOT / "Analizes_ocarinas" / "Low_voicing" / "trials" / f"{pid}_{trial}.json"
        if not stl.exists() or not tj.exists():
            print(bid, "missing")
            continue
        g = json.loads(tj.read_text(encoding="utf-8"))["geometry"]
        mid = g["mouth_xyz"][2] + g["mouth_end_below_mid_plane_mm"]
        V = read_stl(stl)
        y0 = V[:, 1].min()
        tip = V[V[:, 1] < y0 + 1.5]
        zc = 0.5 * (tip[:, 2].min() + tip[:, 2].max())
        # 10 mm back from the tip, the same
        ring = V[np.abs(V[:, 1] - (y0 + 10.0)) < 0.4]
        ring = ring[np.abs(ring[:, 0] - tip[:, 0].mean()) < 20.0]
        z10 = 0.5 * (ring[:, 2].min() + ring[:, 2].max()) if len(ring) else float("nan")
        print(f"{bid:18s} tip outside {tip[:, 2].max() - tip[:, 2].min():5.1f} mm high, its middle {mid - zc:5.1f} mm below the body's middle "
              f"(pipe {g['mouth_end_below_mid_plane_mm']:.1f}); 10 mm back: {mid - z10:5.1f} mm below")
