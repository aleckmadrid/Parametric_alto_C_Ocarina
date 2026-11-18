"""Review pictures of a full body. They are evidence for the geometry checks: look at every one.

Written to addon_renders/<body id>/ (or the folder given):

    top.png, bottom.png, front.png, end.png     orthographic views (bottom = thumb face and voicing). The top
                                                 view has the hole names beside the holes; the bottom view
                                                 names the thumb holes.
    iso.png, iso_bottom.png                      isometric views from above and from the voicing side
    voicing.png                                  the window seen from outside, straight along its normal
    section_windway.png                          section along the windway centre line (jet runs left to right,
                                                 outside is up). The capped air is drawn in blue.
    section_window_across.png                    section across the window at its widest point
    section_window_plan.png                      section parallel to the wall, half-way through the window throat
    section_row_left.png, section_row_right.png  sections through the left-hand and right-hand finger rows
    section_thumbs.png                           section through the two thumb holes
    section_hole_<name>.png                      section along the axis of each hole with an inward tube
    sheet_views.png, sheet_sections.png          the pictures above, side by side

A body with the taped test layout (the P0 control egg) carries the caption "taped test body, not a hand
layout" under every picture.
"""
from __future__ import annotations

import os
import pathlib

import numpy as np

from . import ergonomics, render

ROOT = pathlib.Path(__file__).resolve().parent.parent
BODY_COLOR = (0.78, 0.74, 0.62, 1.0)
AIR_RGB = (0.35, 0.62, 1.0)


def _fit_plane(points):
    """Plane through points: centroid, unit normal (smallest principal direction)."""
    P = np.asarray(points, float)
    c = P.mean(axis=0)
    _, _, vt = np.linalg.svd(P - c)
    return c, vt[-1]


def render_all(body, out_dir: str | None = None, size_px: int = 760) -> dict:
    out = (pathlib.Path(out_dir) if out_dir else ROOT / "addon_renders" / body.body_id).resolve()   # Blender needs absolute paths
    out.mkdir(parents=True, exist_ok=True)
    V, F = body.solid
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    L, W, wall = v.window_length_mm, v.window_width_mm, v.wall_at_window_mm
    files = {}

    # hole names: beside each hole mouth at the outer skin, in the plan view
    circles = {"top": [], "bottom": []}
    for h in body.layout.holes:
        c = np.asarray(h.centre, float) + h.wall_mm * np.asarray(h.axis, float)
        circles[h.deck].append((h.name, float(c[0]), float(c[1]), 0.5 * h.d_mm))
    labels = {deck: render.place_labels(cs) for deck, cs in circles.items() if cs}
    views = render.render_views([(V, F, BODY_COLOR)], str(out), views=("top", "bottom", "front", "end", "iso", "iso_bottom"),
                                size_px=size_px, labels=labels)
    for p in views:
        files[pathlib.Path(p).stem] = p

    # the window seen from outside along its normal: jet direction to the right
    render.VIEWS["_voicing"] = (tuple(-fz), tuple(fy))
    r = 0.5 * W + vs.info["ramp_reach_mm"] + 6.0
    sel = np.linalg.norm(V - (o - fx * 0.5 * L), axis=1) < r + 14.0
    used = np.unique(F[sel[F].all(axis=1)])
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    Fs = remap[F[sel[F].all(axis=1)]]
    p = render.render_views([(V[used], Fs, BODY_COLOR)], str(out), prefix="", views=("_voicing",), size_px=size_px)[0]
    target = str(out / "voicing.png")
    os.replace(p, target)
    files["voicing"] = target

    air = [(body.air_capped[0], body.air_capped[1], AIR_RGB)]
    lab = [((0.0, 0.0), (1.0, 0.1, 0.1))]
    # along the windway centre line: plane spanned by the jet (u) and the outward normal (v)
    files["section_windway"] = render.section_image(
        V, F, o, fy, fx, fz, str(out / "section_windway.png"), mm_per_px=0.04,
        extent=(-L - v.windway_length_mm - 3.0, 16.0, -9.0, wall + 3.0), extra=air, marks=lab)[0]
    xb = vs.info["widest_xw_mm"]
    files["section_window_across"] = render.section_image(
        V, F, o + fx * (xb - L), fx, fy, fz, str(out / "section_window_across.png"), mm_per_px=0.04,
        extent=(-(0.5 * W + 14.0), 0.5 * W + 14.0, -9.0, wall + 3.0), extra=air)[0]
    files["section_window_plan"] = render.section_image(
        V, F, o + fz * (0.6 * wall), fz, fx, fy, str(out / "section_window_plan.png"), mm_per_px=0.04,
        extent=(-L - 8.0, vs.info["ramp_reach_mm"] + 3.0, -(0.5 * W + 14.0), 0.5 * W + 14.0))[0]

    # sections through the hole rows: a plane fitted through the hole axes of the row
    by = body.layout.by_name()
    rows = {"row_left": ["L_pinky", "L_ring", "L_middle", "L_index"], "row_right": ["R_index", "R_middle", "R_ring", "R_pinky"],
            "thumbs": ["L_thumb", "R_thumb"]}
    for key, names in rows.items():
        hs = [by[n] for n in names if n in by]
        if len(hs) < 2:
            continue
        pts = [np.asarray(h.centre) for h in hs] + [np.asarray(h.centre) + 6.0 * np.asarray(h.axis) for h in hs]
        c, n = _fit_plane(pts)
        u = np.array([1.0, 0.0, 0.0]) - n[0] * n
        u /= np.linalg.norm(u)
        w = np.cross(n, u)
        if w[2] < 0:
            w = -w
        files[f"section_{key}"] = render.section_image(V, F, c, n, u, w, str(out / f"section_{key}.png"), mm_per_px=0.08, extra=air,
                                                       marks=[(((np.asarray(h.centre) - c) @ u, (np.asarray(h.centre) - c) @ w), (1.0, 0.1, 0.1)) for h in hs])[0]
    for h in body.layout.holes:
        if h.tube_mm <= 0:
            continue
        n_ax = np.asarray(h.axis)
        u = np.array([1.0, 0.0, 0.0]) - n_ax[0] * n_ax
        u /= np.linalg.norm(u)
        files[f"section_hole_{h.name}"] = render.section_image(
            V, F, np.asarray(h.centre), np.cross(u, n_ax), u, n_ax, str(out / f"section_hole_{h.name}.png"), mm_per_px=0.03,
            extent=(-9.0, 9.0, -(h.tube_mm + 4.0), h.wall_mm + 3.0), extra=air)[0]

    if body.layout.holes and body.layout.kind == "relative":
        for pth in files.values():
            render.add_caption(str(pth), f"{body.body_id}: {ergonomics.TAPED_MESSAGE}")
    view_keys = ["top", "bottom", "front", "end", "iso", "iso_bottom", "voicing"]
    files["sheet_views"] = render.contact_sheet([files[k] for k in view_keys], str(out / "sheet_views.png"), cols=4, cell_px=440)
    sec_keys = [k for k in files if k.startswith("section_")]
    files["sheet_sections"] = render.contact_sheet([files[k] for k in sec_keys], str(out / "sheet_sections.png"), cols=3, cell_px=520)
    body.files.update({f"render_{k}": str(pth) for k, pth in files.items()})
    return files
