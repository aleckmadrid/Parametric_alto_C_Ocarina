"""How the neck sits on the body of a built STL, as shares of the body, to compare with the rough sculpt (docs/11).

    .venv/bin/python tools/neck_view_metrics.py addon_out/<id>/<id>.stl [more.stl ...]

Needs numpy only. The body is taken as built by the add-on: long axis along X, the neck leaving toward -Y, the thumb
face toward -Z. Everything is measured on the outside; the pipe and the chamber do not enter.

    station     where the neck's axis meets the body's long axis, from the bulb end, as a share of the length
    section     the body's extent across the neck at that station (mm): the unit of the shares below
    offset      how far the neck's axis passes from the long axis, share of the section (+ = the thumb-face side)
    mouth out   the mouth end's distance from the body's long axis, in sections: the neck's height
    lean        the neck's lean along the body, degrees (+ = the mouth end toward the bulb)
    width/depth the neck's section 0.2, 0.4 and 0.6 sections from the mouth end, shares of the section

Sculpt, measured the same way on `ocarina oot rough stl.stl` (2026-11-28): station 0.24, offset +4 %, mouth out 1.35,
lean +8.6, width 0.40 / 0.52 / 0.64, depth 0.28 / 0.36 / 0.43 (the last two from its fitted cone).
"""
import struct
import sys

import numpy as np


def load(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[80:84])[0]
    assert 84 + 50 * n == len(b), f"{path}: not a binary STL"
    rec = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    return np.frombuffer(b, dtype=rec, count=n, offset=84)["v"].astype(float)


def samples(T, step=0.3):
    """Points on the triangles, about `step` mm apart."""
    edge = np.max([np.linalg.norm(T[:, a] - T[:, b], axis=1) for a, b in ((0, 1), (1, 2), (2, 0))], axis=0)
    K, out = np.minimum(np.ceil(edge / step).astype(int), 300), []
    for k in np.unique(K):
        t = T[K == k]
        out += [t[:, 0] * (1 - i / k - j / k) + t[:, 1] * (i / k) + t[:, 2] * (j / k) for i in range(k + 1) for j in range(k + 1 - i)]
    return np.concatenate(out)


def metrics(path):
    P = samples(load(path))
    M, d, x = P[P[:, 1] < P[:, 1].min() + 1.0].mean(0), np.array([0.0, -1.0, 0.0]), np.array([1.0, 0.0, 0.0])
    for _ in range(4):                                   # the neck's axis: a line through the centres of its free sections
        w = x - d * (x @ d); w /= np.linalg.norm(w); t = np.cross(w, d); C = []
        for s in np.arange(3.0, 30.0, 2.0):
            q = P[np.abs((P - (M - d * s)) @ d) < 0.2] - (M - d * s)
            q = q[np.hypot(q @ w, q @ t) < 30.0]
            C.append((M - d * s) + w * ((q @ w).max() + (q @ w).min()) / 2 + t * ((q @ t).max() + (q @ t).min()) / 2)
        C = np.array(C); c0 = C.mean(0); d = np.linalg.eigh(np.cov((C - c0).T))[1][:, 2]; d *= -np.sign(d[1]); M = c0 + d * ((M - c0) @ d)
    q = P - M; ax = q @ d
    M = M + d * ax[np.linalg.norm(q - np.outer(ax, d), axis=1) < 4.0].max()          # the mouth end itself
    B = P[(P - M) @ d < -0.5 * np.ptp(P[:, 1])]            # the body without the free neck: the far half, seen from the mouth
    c = B.mean(0); L = np.linalg.eigh(np.cov((B[::7] - c).T))[1][:, 2]; L *= np.sign(L[0])
    dn = d - L * (d @ L); dn /= np.linalg.norm(dn); e2 = np.cross(L, dn); e2 *= -np.sign(e2[2])   # e2: across the neck, toward the thumb face
    xs = (P - c) @ L; st = (M - c) @ L
    bulb_low = abs(st - xs.min()) < abs(st - xs.max())
    station = (st - xs.min()) / np.ptp(xs) if bulb_low else (xs.max() - st) / np.ptp(xs)
    m = np.abs((B - c) @ L - st) < 4.0; sec = np.ptp((B[m] - c) @ e2)
    lean = np.degrees(np.arcsin(d @ L)) * (-1 if bulb_low else 1)
    shares = []
    for f in (0.2, 0.4, 0.6):
        q = P - (M - d * f * sec); a = q @ d; q = q[(np.abs(a) < 0.25) & (np.linalg.norm(q - np.outer(a, d), axis=1) < 0.6 * sec)]
        shares.append((np.ptp(q @ np.cross(d, e2)) / sec, np.ptp(q @ e2) / sec))
    return dict(station=station, section_mm=sec, offset=(M - c) @ e2 / sec, mouth_out=(M - c) @ dn / sec, lean_deg=lean,
                width=[s[0] for s in shares], depth=[s[1] for s in shares])


if __name__ == "__main__":
    for path in sys.argv[1:]:
        r = metrics(path)
        print(f"{path}\n  station {r['station']:.2f}  section {r['section_mm']:.1f} mm  offset {100 * r['offset']:+.0f} %  "
              f"mouth out {r['mouth_out']:.2f}  lean {r['lean_deg']:+.1f} deg\n"
              f"  width {' / '.join(f'{v:.2f}' for v in r['width'])}   depth {' / '.join(f'{v:.2f}' for v in r['depth'])}")
