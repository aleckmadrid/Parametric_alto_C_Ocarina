"""Split the owner's sample STL into its bodies and describe each. Run with python -I."""
import site
import sys

site.addsitedir(site.getusersitepackages())
import numpy as np  # noqa: E402
import trimesh  # noqa: E402

m = trimesh.load(sys.argv[1], force="mesh")
print("tris", len(m.faces), "bounds", np.round(m.bounds, 2).tolist())
parts = sorted(m.split(only_watertight=False), key=lambda p: -len(p.faces))
print("bodies", len(parts))
for k, p in enumerate(parts[:8]):
    c = p.vertices.mean(axis=0)
    w, v = np.linalg.eigh(np.cov((p.vertices - c).T))
    ext = [(float(((p.vertices - c) @ v[:, i]).min()), float(((p.vertices - c) @ v[:, i]).max())) for i in (2, 1, 0)]
    print(k, "tris", len(p.faces), "watertight", p.is_watertight, "vol cm3", round(abs(p.volume) / 1000, 2),
          "bounds", np.round(p.bounds, 1).tolist())
    print("   principal axes (long first):", np.round(v[:, ::-1].T, 3).tolist(), "extents", [round(b - a, 1) for a, b in ext])
    p.export(f"{sys.argv[2]}/sample_part{k}.stl")
