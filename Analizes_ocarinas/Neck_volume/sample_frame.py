"""The owner's sample (body, neck, wind cut) measured in the frame of its own window. Run with python -I:

    python -I Analizes_ocarinas/Neck_volume/sample_frame.py "<path>/ocarina-body+neck+wind cut.stl"

The sample is read where it lies (the owner's Desktop); it is not copied into the repository. Writes
sample_frame.json beside this file: the frame, the long section of the three shapes, and the numbers. It also
writes the body and the neck as two STL files to addon_out/sample_owner/ (not committed), for sample_cut.py.

Frame of the window (the same as the add-on's voicing frame)
    z       out of the flat face that the body has inside, where the labium will be
    y       across the wind cut (its 10 mm width)
    x       along the jet, in the plane of that face
    origin  where the centre line of the wind cut meets the plane of the flat face
"""
import json
import math
import pathlib
import site
import sys

site.addsitedir(site.getusersitepackages())
import numpy as np  # noqa: E402
import trimesh  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
m = trimesh.load(sys.argv[1], force="mesh")
parts = sorted(m.split(only_watertight=False), key=lambda p: -abs(p.volume))
body, neck, wind = parts[0], parts[1], parts[2:]
windV = np.vstack([p.vertices for p in wind])
print("shapes: body", round(abs(body.volume) / 1000, 2), "cm3 of plastic; neck", round(abs(neck.volume) / 1000, 2), "cm3; wind cut",
      round(sum(abs(p.volume) for p in wind) / 1000, 2), "cm3 in", len(wind), "pieces")

# ---- the wind cut: long axis, width axis, height axis, and its two ends (the exit is the thin end)
w0 = wind[0]
c = w0.vertices.mean(axis=0)
_, evec = np.linalg.eigh(np.cov((w0.vertices - c).T))
long_ax, wide_ax, high_ax = evec[:, 2], evec[:, 1], evec[:, 0]
t = (w0.vertices - c) @ long_ax
ends = []
for sel in (t < t.min() + 0.5, t > t.max() - 0.5):
    P = w0.vertices[sel]
    ends.append(dict(centre=P.mean(axis=0), height=float(np.ptp((P - c) @ high_ax)), width=float(np.ptp((P - c) @ wide_ax))))
exit_end, tip_end = sorted(ends, key=lambda e: e["height"])
jet = exit_end["centre"] - tip_end["centre"]
length = float(np.linalg.norm(jet))
jet /= length
print(f"wind cut: {length:.1f} mm long, {tip_end['width']:.1f} mm wide, {tip_end['height']:.2f} mm high at the mouth end, {exit_end['height']:.2f} mm at the exit")

# ---- the flat face inside the body near the exit: the largest group of inner faces in one plane
fn, fa, fc = body.face_normals, body.area_faces, body.triangles_center
near = np.linalg.norm(fc - exit_end["centre"], axis=1) < 22.0
inner = ((body.centroid - fc) * fn).sum(axis=1) > 0
idx = np.where(near & inner)[0]
best = None
for i in idx[np.argsort(-fa[idx])][:400]:
    same = idx[(fn[idx] @ fn[i]) > math.cos(math.radians(1.0))]
    same = same[np.abs((fc[same] - fc[i]) @ fn[i]) < 0.05]
    if best is None or fa[same].sum() > best[0]:
        best = (fa[same].sum(), i, same)
area, i0, same = best
p0 = fc[same].mean(axis=0)
print(f"flat face inside the body: {area:.1f} mm2")

z = -fn[i0]
y = wide_ax - (wide_ax @ z) * z
y /= np.linalg.norm(y)
x = np.cross(y, z)
if x @ jet < 0:
    x, y = -x, -y
s = ((p0 - exit_end["centre"]) @ z) / (jet @ z)
origin = exit_end["centre"] + s * jet
pitch = math.degrees(math.asin(-(jet @ z)))


def to_frame(P):
    Q = np.asarray(P, float) - origin
    return np.column_stack([Q @ x, Q @ y, Q @ z])


def section(mesh):
    segs = trimesh.intersections.mesh_plane(mesh, y, origin)
    return to_frame(segs.reshape(-1, 3)).reshape(-1, 2, 3)[:, :, [0, 2]] if len(segs) else np.zeros((0, 2, 2))


sec = {"body": section(body), "neck": section(neck), "wind": np.concatenate([section(p) for p in wind])}


def crossings(S, xv):
    return sorted(z0 + (z1 - z0) * (xv - x0) / (x1 - x0) for (x0, z0), (x1, z1) in S if (x0 - xv) * (x1 - xv) <= 0 and abs(x1 - x0) > 1e-9)


WV = to_frame(w0.vertices)
x_exit, x_tip = float(WV[:, 0].max()), float(WV[:, 0].min())
xs = np.arange(math.ceil(x_tip) + 4.0, x_exit, 2.0)
rows = []
for xv in xs:
    n, w, b = crossings(sec["neck"], xv), crossings(sec["wind"], xv), crossings(sec["body"], xv)
    if n and w:
        rows.append(dict(x=float(xv), neck_top=n[-1], pipe_roof=w[-1], pipe_floor=w[0], neck_bottom=n[0], body_top=b[-1] if b else None))
A = np.array([[r["x"], r["neck_top"], r["pipe_roof"], r["pipe_floor"], r["neck_bottom"]] for r in rows])


def slope(col):
    return math.degrees(math.atan(-np.polyfit(A[1:-1, 0], A[1:-1, col], 1)[0]))


over = A[1:-1, 1] - A[1:-1, 2]
# the neck across the pipe: its outline at stations along the pipe, and the middle of each
cents = []
for a in np.arange(4.0, 32.0, 3.0):
    segs = trimesh.intersections.mesh_plane(neck, -jet, exit_end["centre"] - a * jet)
    P = to_frame(segs.reshape(-1, 3))
    cents.append((a, P[:, 0].mean(), P[:, 2].mean(), np.ptp(P[:, 1]), np.ptp((P - P.mean(axis=0)) @ np.array([math.sin(math.radians(pitch)), 0, math.cos(math.radians(pitch))]))))
C = np.array(cents)
axis = math.degrees(math.atan(-np.polyfit(C[:, 1], C[:, 2], 1)[0]))
b0 = crossings(sec["body"], 0.0)
# where the top line of the neck runs into the outer face of the body (the first x at which it is within 0.3 mm of it)
meet = float("nan")
for xv in np.arange(x_exit - 6.0, 6.0, 0.25):
    n, b = crossings(sec["neck"], xv), crossings(sec["body"], xv)
    if not n or (b and n[-1] - b[-1] < 0.3):
        meet = float(xv)
        break
numbers = dict(
    pipe_against_face_deg=pitch, neck_top_line_deg=slope(1), pipe_roof_deg=slope(2), pipe_floor_deg=slope(3), neck_middle_line_deg=axis,
    plastic_over_pipe_roof_mm=[float(over.min()), float(over.max())],
    plastic_under_pipe_floor_mm=[float((A[1:-1, 3] - A[1:-1, 4]).min()), float((A[1:-1, 3] - A[1:-1, 4]).max())],
    wall_at_flat_face_mm=float(b0[-1] - b0[-2]), pipe_exit_x_mm=x_exit, pipe_centre_line_to_face_mm=float(s),
    neck_top_meets_body_top_at_x_mm=meet, plastic_over_the_pipe_exit_mm=float(crossings(sec["neck"], x_exit - 0.2)[-1] - crossings(sec["wind"], x_exit - 0.2)[-1]),
    neck_across_the_pipe=[dict(before_exit_mm=float(a), width_mm=float(w), depth_mm=float(d)) for a, _, _, w, d in cents],
    wind_cut=dict(length_mm=length, width_mm=tip_end["width"], mouth_height_mm=tip_end["height"], exit_height_mm=exit_end["height"]))
for k, v in numbers.items():
    if k != "neck_across_the_pipe":
        print(f"  {k}: {np.round(v, 2).tolist() if not isinstance(v, dict) else {a: round(b, 2) for a, b in v.items()}}")
for r in numbers["neck_across_the_pipe"]:
    print("  neck across the pipe:", {a: round(b, 1) for a, b in r.items()})
json.dump(dict(origin=origin.tolist(), x=x.tolist(), y=y.tolist(), z=z.tolist(), numbers=numbers, rows=rows,
               sections={k: np.round(v, 3).tolist() for k, v in sec.items()}), open(HERE / "sample_frame.json", "w"), indent=None)
# the body and the neck as files of their own, for sample_cut.py (addon_out is not committed)
parts_dir = HERE.parents[1] / "addon_out" / "sample_owner"
parts_dir.mkdir(parents=True, exist_ok=True)
body.export(parts_dir / "body.stl")
neck.export(parts_dir / "neck.stl")
print("ok; parts in", parts_dir)
