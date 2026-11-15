"""STL export and import as plain binary files (numpy only). Units: millimetres.

The writer does not go through a Blender operator, so the file holds exactly the triangles that the
checks measured. The reader welds the vertices again, so a check can run on the file that was written.
"""
from __future__ import annotations

import os
import struct

import numpy as np

_DTYPE = np.dtype([("normal", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")])


def write_stl(path: str, V, F, header: str = "parametric ocarina, units mm") -> str:
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int64)
    tri = V[F].astype(np.float32)                                  # (m, 3, 3)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    data = np.zeros(len(F), dtype=_DTYPE)
    data["normal"] = n / ln[:, None]
    data["v"] = tri
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(header.encode("ascii", "replace")[:80].ljust(80, b" "))
        fh.write(struct.pack("<I", len(F)))
        fh.write(data.tobytes())
    return path


def read_stl(path: str, weld_decimals: int = 5):
    """Read a binary STL. Returns (V, F) with coincident vertices welded (rounded to 1e-5 mm)."""
    with open(path, "rb") as fh:
        fh.read(80)
        (count,) = struct.unpack("<I", fh.read(4))
        data = np.frombuffer(fh.read(count * _DTYPE.itemsize), dtype=_DTYPE, count=count)
    pts = data["v"].reshape(-1, 3).astype(np.float64)
    key = np.round(pts, weld_decimals)
    uniq, inverse = np.unique(key, axis=0, return_inverse=True)
    F = inverse.reshape(-1, 3).astype(np.int64)
    keep = (F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])
    return uniq, F[keep]
