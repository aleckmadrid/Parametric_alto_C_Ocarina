"""Trials of the shell-edit build (PROTOTYPE): does an instrument come out right after the shell was edited?

Run it with Blender 5.1 in background mode, from the repository root:

    blender -b --factory-startup --python tools/shell_edit_trial.py -- [--preset P4] [--v0 80] [--renders] [--blend]
                                                                     [--only plain tail ...]

Nobody sculpts in a background run, so each trial edits the base the way a user could, with a short program
(the EDITS below), and then finishes the body with ocarina_addon.shell_edit.finish. Every trial starts from a
fresh base. A finished body is checked like every other body: the STL is read back from disk and measured.

    plain     nothing is edited. The body must be the one the one-step build makes
    tail      the tail is 25 mm longer (solid plastic: the chamber does not grow)
    sculpt    the longer tail, a 1.5 mm boss over the R ring hole, a groove across the L middle hole, a relief
              pattern up to 0.6 mm over the whole body, and a neck that is 20 % thicker
    remesh    the shell and the neck as a sculpting session leaves them: voxel-remeshed (another mesh altogether)
              and pushed outward by a cloud texture, both as modifiers that are still on the objects
    thick     2.5 mm more plastic over the whole finger deck: far outside what the test prints measure

It writes
    addon_checks/<id>.md, .json        the check report of each finished body (<id> = <preset>-<V0>-edit-<trial>)
    addon_checks/shell-edit-trials.md  one table for all trials
    addon_out/<id>/                    the STL files, and with --blend the scene with the base and the result
    addon_renders/<id>/                with --renders: the review pictures, and base.png (the shell and the neck
                                       as the user left them, before anything was cut)

For each trial the table gives what the edit would have done to the scale if the holes had kept the sizes of
the base (the kernel's model, with the walls measured on the edited shell), and what the finished body has.
"""
from __future__ import annotations

import math
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import bpy  # noqa: E402
import numpy as np  # noqa: E402

from ocarina_addon import body as body_mod, checks_geo, export, kernel_bridge, meshutil, render, report, shell_edit, voicing_geo  # noqa: E402

CHECK_DIR = ROOT / "addon_checks"
OUT_DIR = ROOT / "addon_out"
RENDER_DIR = ROOT / "addon_renders"
SHELL_COLOR = (0.78, 0.74, 0.62, 1.0)
NECK_COLOR = (0.55, 0.66, 0.80, 1.0)


# ------------------------------------------------------------------ edits (what a user could do, as programs)

def vertices(ob) -> np.ndarray:
    n = len(ob.data.vertices)
    V = np.empty(n * 3, dtype=np.float64)
    ob.data.vertices.foreach_get("co", V)
    return V.reshape(n, 3)


def set_vertices(ob, V) -> None:
    ob.data.vertices.foreach_set("co", np.asarray(V, dtype=np.float32).ravel())
    ob.data.update()


def normals_of(ob) -> np.ndarray:
    V, F = meshutil.arrays_from_mesh(ob.data)
    return meshutil.vertex_normals(V, F)


def hole(base, name):
    return base.layout.by_name()[name]


def outer_point(h) -> np.ndarray:
    """The middle of a hole at the plain skin."""
    return np.asarray(h.centre, float) + h.wall_mm * np.asarray(h.axis, float)


def lengthen_tail(base, shell, neck, extra_mm: float = 25.0) -> str:
    """Stretch the tail: everything past the R pinky hole moves along the body, the tip by extra_mm."""
    V = vertices(shell)
    h = hole(base, "R_pinky")
    tip = float(V[:, 0].max())
    past = float(outer_point(h)[0] + 0.5 * h.d_mm + 6.0)
    x0 = min(past, tip - 10.0)                             # a short body ends less than 6 mm past the hole: stretch its last 10 mm
    t = np.clip((V[:, 0] - x0) / (tip - x0), 0.0, 1.0)
    V[:, 0] += extra_mm * t * t * (3.0 - 2.0 * t)
    set_vertices(shell, V)
    return f"tail {extra_mm:g} mm longer (" + ("from 6 mm past the R pinky hole)" if x0 == past else "the last 10 mm of the body stretched)")


def boss(base, shell, neck, name: str = "R_ring", height_mm: float = 1.5, radius_mm: float = 8.0) -> str:
    """A round boss (or, with a negative height, a dimple) centred on a hole."""
    V, N = vertices(shell), normals_of(shell)
    d = np.linalg.norm(V - outer_point(hole(base, name)), axis=1)
    set_vertices(shell, V + (height_mm * np.exp(-(d / radius_mm) ** 2))[:, None] * N)
    return f"boss {height_mm:+g} mm high, {radius_mm:g} mm radius, over {name}"


def groove(base, shell, neck, name: str = "L_middle", depth_mm: float = 0.9, width_mm: float = 2.0) -> str:
    """A groove along the body, across the rim of a hole (half a radius beside its middle)."""
    V, N = vertices(shell), normals_of(shell)
    h = hole(base, name)
    p = outer_point(h)
    across = np.cross(np.asarray(h.axis, float), np.array([1.0, 0.0, 0.0]))
    across /= np.linalg.norm(across)
    rel = V - (p + 0.25 * h.d_mm * across)
    off = rel @ across                                     # distance from the groove line, across it
    near = np.exp(-(np.linalg.norm(rel - np.outer(off, across), axis=1) / 14.0) ** 4)     # the groove is about 28 mm long
    set_vertices(shell, V - (depth_mm * np.exp(-(off / width_mm) ** 2) * near)[:, None] * N)
    return f"groove {depth_mm:g} mm deep, {2 * width_mm:g} mm wide, across the rim of {name}"


def relief(base, shell, neck, height_mm: float = 0.6, wave_mm: float = 7.0, keep_clear_mm: float = 16.0) -> str:
    """A pattern raised out of the surface (never cut into it), fading out toward the window."""
    V, N = vertices(shell), normals_of(shell)
    o = np.asarray(base.voicing.frame[0], float)
    fade = np.clip((np.linalg.norm(V - o, axis=1) - keep_clear_mm) / 8.0, 0.0, 1.0)
    k = 2.0 * math.pi / wave_mm
    pattern = 0.5 + 0.5 * np.sin(k * V[:, 0]) * np.sin(k * (V[:, 1] + 0.6 * V[:, 2]))
    set_vertices(shell, V + (height_mm * pattern * fade)[:, None] * N)
    return f"relief up to {height_mm:g} mm, {wave_mm:g} mm pattern, none within {keep_clear_mm:g} mm of the window"


def deck_pad(base, shell, neck, height_mm: float = 2.5) -> str:
    """More plastic over the whole finger deck (the upper half of the body)."""
    V, N = vertices(shell), normals_of(shell)
    up = np.clip(N[:, 2] / 0.4, 0.0, 1.0)
    set_vertices(shell, V + (height_mm * up * up * (3.0 - 2.0 * up))[:, None] * N)
    return f"{height_mm:g} mm more plastic over the finger deck"


def thicken_neck(base, shell, neck, factor: float = 1.2) -> str:
    """A thicker neck: wider, and deeper on the side away from the window. The roof line, the mouth end plane and
    the part next to the window do not move."""
    v, vs = base.sizing.voicing, base.voicing
    zc = voicing_geo.windway_centre_z(v)
    o, fx, fy, fz = voicing_geo.pitched_frame(vs.frame, zc, float(vs.info["stub_pitch_deg"])) if vs.info["stub_pitch_deg"] else vs.frame
    R = np.stack([fx, fy, fz], axis=1)
    V = vertices(neck)
    Q = (V - o) @ R                                        # along the neck (0 at the labium), across, outward
    L, Lw, wall = v.window_length_mm, v.windway_length_mm, v.wall_at_window_mm
    xw = Q[:, 0] + L
    t = np.clip((xw + Lw) / Lw, 0.0, 1.0)                  # 0 at the mouth end, 1 at the windway exit
    s = 1.0 + (factor - 1.0) * (1.0 - t * t * (3.0 - 2.0 * t))
    Q[:, 1] *= s
    Q[:, 2] = wall - (wall - Q[:, 2]) * s
    set_vertices(neck, Q @ R.T + o)
    return f"neck {100 * (factor - 1):.0f} % thicker toward the mouth end (roof line and mouth end plane kept)"


def sculpt_modifiers(base, shell, neck, voxel_mm: float = 0.6, strength_mm: float = 0.5) -> str:
    """Modifiers that stay on the objects: a voxel remesh (the topology of a sculpting session) and, on the shell, a
    cloud texture that pushes the surface outward."""
    for ob in (shell, neck):
        m = ob.modifiers.new("Remesh", "REMESH")
        m.mode = "VOXEL"
        m.voxel_size = voxel_mm
        m.adaptivity = 0.0
    tex = bpy.data.textures.new("oca_trial_clouds", "CLOUDS")
    tex.noise_scale = 9.0
    d = shell.modifiers.new("Displace", "DISPLACE")
    d.texture = tex
    d.texture_coords = "GLOBAL"
    d.mid_level = 0.0
    d.strength = strength_mm
    return f"voxel remesh at {voxel_mm:g} mm on the shell and the neck, cloud displacement up to {strength_mm:g} mm on the shell (modifiers)"


EDITS = {
    "plain": [],
    "tail": [lengthen_tail],
    "sculpt": [lengthen_tail, boss, groove, relief, thicken_neck],
    "remesh": [sculpt_modifiers],
    "thick": [deck_pad],
}


# ------------------------------------------------------------------ one trial

def reset_scene() -> None:
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def scale_without_resizing(base, body) -> list:
    """Cents per note if the holes had kept the diameters of the base on the edited shell (the kernel's model):
    the walls are those measured on the edited shell, and the capped air holds the extra air of the deeper holes."""
    k = kernel_bridge.kernel()
    MM = 1e-3
    sz = base.sizing
    key = body.params["hole_key"]
    rows = sz.holes.solutions[key]
    walls = body.info["shell_edit"]["holes"]
    d = [r.d_mm * MM for r in rows]
    ch = [(walls[r.name]["wall_mean_mm"] + r.tube_mm) * MM for r in rows]
    extra = sum(math.pi * x * x / 4.0 * (walls[r.name]["wall_mean_mm"] - r.wall_mm) * MM for x, r in zip(d, rows))
    f = k.holes.predict_scale(sz.X_w_mm * MM, sz.v0_cm3 * 1e-6 + extra, d, ch, rows[0].k_hole, sz.c_m_s)
    return [k.ocarina_kernel.cents(a, b) for a, b in zip(f, sz.f_targets_hz)]


def run_trial(name: str, preset: str, v0: float, renders: bool, blend: bool) -> dict:
    reset_scene()
    t0 = time.time()
    P = kernel_bridge.load_params()
    base = shell_edit.build_base(preset, v0, params=P)
    shell, neck = bpy.data.objects[base.object_names["shell"]], bpy.data.objects[base.object_names["neck"]]
    done = [edit(base, shell, neck) for edit in EDITS[name]]
    bid = f"{base.body_id}{shell_edit.EDIT_SUFFIX}-{name}"
    out = OUT_DIR / bid
    row = dict(trial=name, body_id=bid, edits=done, error="")
    outer = shell_edit.user_meshes(shell)
    row["shell_triangles"], row["neck_triangles"] = len(outer[0][1]), len(outer[1][1])
    row["shell_cm3"], row["base_shell_cm3"] = meshutil.volume(*outer[0]) / 1000.0, meshutil.volume(*base.shell) / 1000.0
    if renders:
        rdir = RENDER_DIR / bid
        files = render.render_views([(outer[0][0], outer[0][1], SHELL_COLOR), (outer[1][0], outer[1][1], NECK_COLOR)], str(rdir),
                                    prefix="base_", views=("top", "front", "iso", "iso_bottom"), size_px=700)
        render.contact_sheet(files, str(rdir / "base.png"), cols=4, cell_px=440)
        for f in files:
            os.remove(f)
    try:
        body = shell_edit.finish(shell, export_dir=str(out), body_id=bid, run_checks=False, params=P, save_blend=blend)
    except Exception as exc:                     # noqa: BLE001 - a trial that cannot be finished is a result
        import traceback
        traceback.print_exc()
        row["error"] = f"{type(exc).__name__}: {exc}"
        row["seconds"] = time.time() - t0
        print(f"[{bid}] NOT FINISHED: {row['error']}", flush=True)
        return row
    V, F = export.read_stl(body.files["stl"])                # the checks run on the file that was written
    checks_geo.run_all(body, P, V, F)
    body_mod.write_checks_json(body, str(out))
    if renders:
        from ocarina_addon import render_body
        render_body.render_all(body, str(RENDER_DIR / bid))
    row["seconds"] = time.time() - t0
    report.write_body_report(body, CHECK_DIR, row["seconds"],
                             f"Written by `tools/shell_edit_trial.py` (trial `{name}`): the shell-edit build, a PROTOTYPE. "
                             f"Edits made to the base {base.body_id} before it was finished: " + ("; ".join(done) if done else "none") + ".",
                             json_default=body_mod._json_default)
    se, m = body.info["shell_edit"], body.measurements
    walls = [o["wall_mean_mm"] for o in se["holes"].values()]
    before = scale_without_resizing(base, body)
    old = {r.name: r.d_mm for r in body_mod.cut_rows(base.sizing, body.params["hole_key"])}
    change = max(((h.d_mm - old[h.name], h.name) for h in body.layout.holes), key=lambda t: abs(t[0]))
    row.update(body=body, rounds=se["rounds"], wall_min=min(walls), wall_max=max(walls),
               cents_unsized_worst=max(before, key=abs), cents_unsized_a4=before[0], d_change=change,
               v0_measured=m["volume"]["capped_air_measured_cm3"], v0_target=m["volume"]["v0_target_cm3"],
               plastic_cm3=m["volume"]["body_plastic_cm3"], chamber_cm3=m["volume"]["cavity_mesh_cm3"],
               chamber_base_cm3=base.sizing.cavity_volume_for_mesh_cm3, length_mm=float(np.ptp(V[:, 0])),
               unexpected=[c["name"] for c in checks_geo.unexpected_failures(body)],
               warnings=[c["name"] for c in checks_geo.warnings(body) if c["name"].startswith("shell_")],
               hole_error=max(abs(r["d_error_mm"]) for r in m["holes"]), chimney_error=max(abs(r["chimney_error_mm"]) for r in m["holes"]),
               triangles=m["topology"]["triangles"])
    for c in body.checks:
        if c["status"] in ("fail", "warn") and not c["name"].startswith("ergo_"):
            print(f"[{bid}] {body_mod.STATUS_MARKS.get(c['status'], c['status'])}{' (expected)' if c['expected'] else ''} {c['name']}: {c['message']}", flush=True)
    print(f"[{bid}] {'OK' if not row['unexpected'] else 'UNEXPECTED FAILURES: ' + ', '.join(row['unexpected'])}; {row['seconds']:.0f} s", flush=True)
    return row


def summary(rows, preset: str, v0: float) -> str:
    out = ["# Shell-edit build: trials", "",
           f"Written by `tools/shell_edit_trial.py` for the base {preset}-{v0:g}. The shell-edit build is a PROTOTYPE "
           "(`ocarina_addon/shell_edit.py`): the add-on makes the solid shell and the solid neck, they are edited, and the add-on "
           "then cuts the chamber, the holes and the voicing. In these trials a program made the edits a user could make.", "",
           "*Scale with the base's holes* is what the edit would have done if the holes had kept the sizes of the base: the kernel's "
           "model with the walls measured on the edited shell. It is a prediction, not a measurement. *Finished body* is what the "
           "add-on built after it sized every hole for its own wall; its numbers are measured on the STL file.", "",
           "| Trial | Edits | Shell triangles | Wall at the holes | Scale with the base's holes: A4, worst note | Largest hole change | "
           "Sizing rounds | Chamber | Capped air (target) | Length | Plastic | Largest hole / chimney error | Result | Time |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        if r["error"]:
            out.append(f"| `{r['trial']}` | {'; '.join(r['edits']) or 'none'} | {r['shell_triangles']} | – | – | – | – | – | – | – | – | – | "
                       f"**not finished:** {r['error']} | {r['seconds']:.0f} s |")
            continue
        res = "no unexpected failure" if not r["unexpected"] else "**UNEXPECTED FAILURES:** " + ", ".join(r["unexpected"])
        if r["warnings"]:
            res += "; warnings: " + ", ".join(r["warnings"])
        out.append(f"| `{r['trial']}` | {'; '.join(r['edits']) or 'none'} | {r['shell_triangles']} | {r['wall_min']:.2f} to {r['wall_max']:.2f} mm | "
                   f"{r['cents_unsized_a4']:+.0f}, {r['cents_unsized_worst']:+.0f} cents | {r['d_change'][0]:+.2f} mm ({r['d_change'][1]}) | "
                   f"{r['rounds']} | {r['chamber_cm3']:.2f} cm³ (base {r['chamber_base_cm3']:.2f}) | {r['v0_measured']:.2f} cm³ ({r['v0_target']:.2f}) | "
                   f"{r['length_mm']:.0f} mm | {r['plastic_cm3']:.1f} cm³ | {r['hole_error']:.3f} / {r['chimney_error']:.3f} mm | {res} | {r['seconds']:.0f} s |")
    out += ["", "The check report of each finished body is `addon_checks/<id>.md`, with <id> = "
            f"`{preset}-{v0:g}{shell_edit.EDIT_SUFFIX}-<trial>`.", ""]
    return "\n".join(out)


def main(argv) -> int:
    def opt(flag, default):
        return argv[argv.index(flag) + 1] if flag in argv else default

    preset, v0 = opt("--preset", "P4"), float(opt("--v0", "80"))
    names = list(EDITS)
    if "--only" in argv:
        names = [a for a in argv[argv.index("--only") + 1:] if not a.startswith("--")]
    rows = [run_trial(n, preset, v0, "--renders" in argv, "--blend" in argv) for n in names]
    text = summary(rows, preset, v0)
    if "--only" not in argv:
        (CHECK_DIR / "shell-edit-trials.md").write_text(text, encoding="utf-8")
    print(text.encode("ascii", "replace").decode("ascii"), flush=True)
    return 1 if any(r["error"] or r["unexpected"] for r in rows) else 0


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(args)
    sys.stdout.flush()
    os._exit(code)
