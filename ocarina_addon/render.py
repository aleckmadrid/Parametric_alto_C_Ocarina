"""Headless pictures for review: Workbench renders and filled section drawings.

    render_views(...)     orthographic views and isometric views of a mesh, as PNG files. Names can be
                          written beside points (the hole names in the top view).
    add_caption(...)      a line of text under a picture
    section_image(...)    a filled cross-section drawn from the plane-mesh intersection (no renderer):
                          solid is dark, air is white, with a 10 mm grid. Good for wall, labium, tubes.
    contact_sheet(...)    several PNG files side by side in one PNG

All lengths are millimetres. Pictures are evidence for the geometry checks, so they are made from the
same (V, F) arrays that the checks measure.
"""
from __future__ import annotations

import math
import os
import time

import numpy as np

import bpy
from mathutils import Matrix, Vector

from . import meshutil

VIEWS = {
    # name: (direction the camera looks along, up vector)
    "top": ((0, 0, -1), (0, 1, 0)),            # finger deck, player at the bottom of the picture
    "bottom": ((0, 0, 1), (0, -1, 0)),         # thumb face and voicing, mirrored left-right against "top"
    "front": ((0, 1, 0), (0, 0, 1)),           # seen from the player
    "back": ((0, -1, 0), (0, 0, 1)),
    "end": ((-1, 0, 0), (0, 0, 1)),            # seen from the right-hand end
    "iso": ((-1, 1, -0.8), (0, 0, 1)),         # from the player's right, above
    "iso_bottom": ((1, 1, 0.9), (0, 0, -1)),   # from the player's left, below: the voicing side
}



def _write_retry(action, tries: int = 4, wait_s: float = 0.7):
    """Run a call that writes a picture. Blender raises RuntimeError ("cannot save", "Could not write image") when the
    file is held open for a moment by something else: a viewer, an indexer, a sync client, another Blender. That
    passes, so wait and try again; the last error is raised."""
    for k in range(tries):
        try:
            return action()
        except RuntimeError:
            if k == tries - 1:
                raise
            time.sleep(wait_s * (k + 1))


def _reset_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 100          # smallest files; the pictures go into git
    scene.view_settings.view_transform = "Standard"
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "OBJECT"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_object_outline = True
    sh.show_shadows = False
    sh.background_type = "VIEWPORT"
    sh.background_color = (1.0, 1.0, 1.0)
    scene.display.render_aa = "8"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("oca_world")
    scene.world.color = (1.0, 1.0, 1.0)
    return scene


def _camera(scene):
    cam = bpy.data.objects.get("_oca_cam")
    if cam is None:
        cam = bpy.data.objects.new("_oca_cam", bpy.data.cameras.new("_oca_cam"))
        scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.clip_start, cam.data.clip_end = 0.1, 5000.0
    scene.camera = cam
    return cam


def _aim(cam, look, up, centre, half_w, half_h, distance=1000.0):
    look = Vector(look).normalized()
    up = Vector(up)
    right = look.cross(up).normalized()
    up = right.cross(look).normalized()
    rot = Matrix((right, up, -look)).transposed()          # columns: camera X, Y, Z in world
    cam.matrix_world = Matrix.Translation(Vector(centre) - look * distance) @ rot.to_4x4()
    return right, up


LABEL_SIZE_MM = 3.0            # text size of the names in a labelled view
LABEL_COLOR = (0.75, 0.05, 0.05, 1.0)
_CHAR_W = 0.56                 # mean character width of the built-in font, in text sizes
_CHAR_H = 0.72


def _text_object(name: str, text: str, location, size: float, rotation=(0.0, 0.0, 0.0), color=(0.0, 0.0, 0.0, 1.0)):
    """A flat text object (built-in font), centred on `location`, readable from +Z before the rotation."""
    cu = bpy.data.curves.new(name, type="FONT")
    cu.body = text
    cu.size = size
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.extrude = 0.02
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = tuple(float(c) for c in location)
    ob.rotation_euler = rotation
    ob.color = color
    return ob


def _remove_text(ob):
    cu = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)


def place_labels(circles, size: float = LABEL_SIZE_MM) -> list:
    """Where to write a name beside each circle so that names and circles do not overlap.

    circles: list of (name, x, y, radius) in the picture plane (x to the right, y up). Returns a list of
    (name, x, y) label centres. Each label takes the free place (above, below, left, right of its circle) that
    is farthest from the other circles and from the labels placed before it.
    """
    def rect_of(name, cx, cy):
        return (cx - 0.5 * _CHAR_W * size * len(name), cx + 0.5 * _CHAR_W * size * len(name),
                cy - 0.5 * _CHAR_H * size, cy + 0.5 * _CHAR_H * size)

    def rect_circle(r, c):
        dx = max(r[0] - c[1], 0.0, c[1] - r[1])
        dy = max(r[2] - c[2], 0.0, c[2] - r[3])
        return math.hypot(dx, dy) - c[3]

    def rect_rect(a, b):
        return math.hypot(max(a[0] - b[1], 0.0, b[0] - a[1]), max(a[2] - b[3], 0.0, b[2] - a[3]))

    placed, out = [], []
    for name, x, y, rad in sorted(circles, key=lambda c: c[3]):         # small holes first: they have the least room
        half_w, half_h, gap = 0.5 * _CHAR_W * size * len(name), 0.5 * _CHAR_H * size, 0.9
        best = None
        for k, (cx, cy) in enumerate(((x, y + rad + gap + half_h), (x, y - rad - gap - half_h),
                                      (x + rad + gap + half_w, y), (x - rad - gap - half_w, y))):
            r = rect_of(name, cx, cy)
            clear = min([rect_circle(r, c) for c in circles if c[0] != name] + [rect_rect(r, q) for q in placed] + [6.0])
            score = clear - 0.01 * k
            if best is None or score > best[0]:
                best = (score, cx, cy, r)
        placed.append(best[3])
        out.append((name, best[1], best[2]))
    return out


def render_views(meshes, out_dir: str, prefix: str = "", views=("top", "bottom", "front", "end", "iso", "iso_bottom"),
                 size_px: int = 1000, margin: float = 1.08, markers=None, labels=None) -> list:
    """Render the meshes (a list of (V, F, rgba)) from the named views. Returns the list of files written.

    markers: optional list of (point, direction, length, rgba) drawn as thin arrows (for the port frame).
    labels:  optional {view name: [(text, x, y), ...]} for the views "top" and "bottom": names written in the
             picture plane at body coordinates (x, y), floating between the body and the camera.
    """
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    scene = _reset_scene()
    cam = _camera(scene)
    # Only the meshes given here may appear in the picture. Everything else in the scene is hidden for the
    # render and restored afterwards (the factory scene has a 2 mm cube at the origin, where the port is).
    hidden = [(o, o.hide_render) for o in scene.objects if o is not cam]
    for o, _ in hidden:
        o.hide_render = True
    objs = []
    allV = []
    for k, (V, F, color) in enumerate(meshes):
        ob = meshutil.object_from_arrays(f"_oca_render_{k}", V, F)
        ob.data.shade_flat()                  # show the mesh as it is: flat faces stay flat in the picture
        ob.color = color
        objs.append(ob)
        allV.append(np.asarray(V))
    for k, (p, d, length, color) in enumerate(markers or []):
        d = np.asarray(d, float) / np.linalg.norm(d)
        V, F = meshutil.cylinder(p, d, 0.35, 0.0, length, segments=12, area_true=False)
        ob = meshutil.object_from_arrays(f"_oca_marker_{k}", V, F)
        ob.color = color
        objs.append(ob)
    P = np.concatenate(allV)
    written = []
    try:
        for name in views:
            look, up = VIEWS[name]
            look_v = Vector(look).normalized()
            right = look_v.cross(Vector(up)).normalized()
            up_v = right.cross(look_v).normalized()
            xs = P @ np.array(right)
            ys = P @ np.array(up_v)
            texts = []
            if labels and labels.get(name) and name in ("top", "bottom"):
                top = name == "top"
                z = float(P[:, 2].max() + 2.0) if top else float(P[:, 2].min() - 2.0)
                ex, ey = [], []
                for k, (text, lx, ly) in enumerate(labels[name]):
                    texts.append(_text_object(f"_oca_label_{k}", text, (lx, ly, z), LABEL_SIZE_MM,
                                              rotation=(0.0, 0.0, 0.0) if top else (math.pi, 0.0, 0.0), color=LABEL_COLOR))
                    hw, hh = 0.5 * _CHAR_W * LABEL_SIZE_MM * len(text) + 1.0, 0.5 * _CHAR_H * LABEL_SIZE_MM + 1.0
                    for sx in (-hw, hw):
                        for sy in (-hh, hh):
                            q = np.array([lx + sx, ly + sy, z])
                            ex.append(float(q @ np.array(right)))
                            ey.append(float(q @ np.array(up_v)))
                xs, ys = np.concatenate([xs, ex]), np.concatenate([ys, ey])
            cx, cy = 0.5 * (xs.min() + xs.max()), 0.5 * (ys.min() + ys.max())
            w, h = (xs.max() - xs.min()) * margin, (ys.max() - ys.min()) * margin
            centre = np.array(right) * cx + np.array(up_v) * cy + np.array(look_v) * float((P @ np.array(look_v)).mean())
            aspect = max(w, 1e-6) / max(h, 1e-6)
            if aspect >= 1.0:
                scene.render.resolution_x, scene.render.resolution_y = size_px, max(200, int(size_px / aspect))
                cam.data.ortho_scale = w
            else:
                scene.render.resolution_x, scene.render.resolution_y = max(200, int(size_px * aspect)), size_px
                cam.data.ortho_scale = h
            _aim(cam, look, up, centre, w / 2, h / 2)
            path = os.path.join(out_dir, f"{prefix}{name}.png")
            scene.render.filepath = path
            try:
                _write_retry(lambda: bpy.ops.render.render(write_still=True))
            finally:
                for t in texts:
                    _remove_text(t)
            _posterise(path)
            written.append(path)
    finally:
        for ob in objs:
            m = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            bpy.data.meshes.remove(m)
        for o, state in hidden:
            try:
                o.hide_render = state
            except ReferenceError:
                pass
    return written


# ------------------------------------------------------------------ captions

_caption_cache: dict = {}


def caption_strip(text: str, height_px: int = 30):
    """The text as a picture: (height_px, w, 3) float array, dark text on white, row 0 at the bottom."""
    if text in _caption_cache:
        return _caption_cache[text]
    import tempfile
    scene = _reset_scene()
    cam = _camera(scene)
    hidden = [(o, o.hide_render) for o in scene.objects if o is not cam]
    for o, _ in hidden:
        o.hide_render = True
    size = 10.0
    ob = _text_object("_oca_caption", text, (0.0, 0.0, 5000.0), size, color=(0.05, 0.05, 0.05, 1.0))
    w_mm = _CHAR_W * size * len(text) * 1.15 + size
    h_mm = 1.5 * size
    tmp = os.path.join(tempfile.gettempdir(), f"_oca_caption_{os.getpid()}.png")
    try:
        scene.render.resolution_y = height_px
        scene.render.resolution_x = int(height_px * w_mm / h_mm)
        cam.data.ortho_scale = w_mm
        _aim(cam, (0, 0, -1), (0, 1, 0), (0.0, 0.0, 5000.0), 0, 0, distance=100.0)
        scene.render.filepath = tmp
        outline = scene.display.shading.show_object_outline
        scene.display.shading.show_object_outline = False
        _write_retry(lambda: bpy.ops.render.render(write_still=True))
        scene.display.shading.show_object_outline = outline
        strip = load_png(tmp)
    finally:
        _remove_text(ob)
        for o, state in hidden:
            try:
                o.hide_render = state
            except ReferenceError:
                pass
        if os.path.exists(tmp):
            os.remove(tmp)
    _caption_cache[text] = strip
    return strip


def add_caption(path: str, text: str) -> str:
    """Write `text` on a white band under the picture at `path` (the picture grows by the band)."""
    img = load_png(path)
    H, W, _ = img.shape
    strip = caption_strip(text)
    h, w, _ = strip.shape
    if w > W:                                          # a narrow picture: scale the text down
        f = W / w
        yi = (np.arange(max(1, int(h * f))) / f).astype(int).clip(0, h - 1)
        xi = (np.arange(W) / f).astype(int).clip(0, w - 1)
        strip = strip[yi][:, xi]
        h, w, _ = strip.shape
    band = np.ones((h + 4, W, 3), dtype=np.float32)
    x0 = (W - w) // 2
    band[2:2 + h, x0:x0 + w, :] = strip
    save_png(np.concatenate([band, img], axis=0), path)
    return path


# ------------------------------------------------------------------ section drawings

def plane_segments(V, F, origin, normal):
    """Segments where the plane cuts the triangles. Returns an (n, 2, 3) array of end points."""
    n = np.asarray(normal, float)
    n = n / np.linalg.norm(n)
    d = (V - np.asarray(origin, float)) @ n
    d = np.where(np.abs(d) < 1e-9, 1e-9, d)             # push vertices off the plane: no degenerate cases
    dF = d[F]
    side = dF > 0
    cut = side.any(axis=1) & ~side.all(axis=1)
    segs = []
    for tri, dd in zip(F[cut], dF[cut]):
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if (dd[a] > 0) != (dd[b] > 0):
                t = dd[a] / (dd[a] - dd[b])
                pts.append(V[tri[a]] + (V[tri[b]] - V[tri[a]]) * t)
        if len(pts) == 2:
            segs.append(pts)
    return np.array(segs, dtype=np.float64).reshape(-1, 2, 3)


def section_2d(V, F, origin, normal, u_axis, v_axis):
    """Section segments in plane coordinates: (n, 2, 2) array with u, v in mm from `origin`."""
    segs = plane_segments(V, F, origin, normal)
    o = np.asarray(origin, float)
    u = np.asarray(u_axis, float)
    v = np.asarray(v_axis, float)
    return np.stack([(segs - o) @ u, (segs - o) @ v], axis=-1)


def section_image(V, F, origin, normal, u_axis, v_axis, out_path: str, mm_per_px: float = 0.1, extent=None,
                  grid_mm: float = 10.0, extra=None, marks=None):
    """Draw a filled section. extent = (u0, u1, v0, v1) in mm (default: the whole cut, with a margin).

    extra: list of (V, F, rgb) drawn the same way on top in another colour (for example the air domain).
    marks: list of ((u, v), rgb) small crosses. Returns (path, extent).
    """
    S = section_2d(V, F, origin, normal, u_axis, v_axis)
    if len(S) == 0:
        raise meshutil.GeometryError("the section plane does not cut the mesh")
    if extent is None:
        u0, v0 = S[..., 0].min() - 3.0, S[..., 1].min() - 3.0
        u1, v1 = S[..., 0].max() + 3.0, S[..., 1].max() + 3.0
    else:
        u0, u1, v0, v1 = extent
    W = int(math.ceil((u1 - u0) / mm_per_px))
    H = int(math.ceil((v1 - v0) / mm_per_px))
    img = np.ones((H, W, 3), dtype=np.float32)
    # grid
    if grid_mm:
        for g in np.arange(math.ceil(u0 / grid_mm) * grid_mm, u1, grid_mm):
            x = int((g - u0) / mm_per_px)
            if 0 <= x < W:
                img[:, x, :] = (0.82, 0.86, 0.92) if abs(g) > 1e-9 else (0.55, 0.65, 0.85)
        for g in np.arange(math.ceil(v0 / grid_mm) * grid_mm, v1, grid_mm):
            y = int((g - v0) / mm_per_px)
            if 0 <= y < H:
                img[y, :, :] = (0.82, 0.86, 0.92) if abs(g) > 1e-9 else (0.55, 0.65, 0.85)
    _fill(img, S, u0, v0, mm_per_px, (0.25, 0.27, 0.30))
    for (EV, EF, rgb) in (extra or []):
        ES = section_2d(EV, EF, origin, normal, u_axis, v_axis)
        if len(ES):
            _fill(img, ES, u0, v0, mm_per_px, rgb, alpha=0.55)
    for (pt, rgb) in (marks or []):
        x, y = int((pt[0] - u0) / mm_per_px), int((pt[1] - v0) / mm_per_px)
        r = max(3, int(0.6 / mm_per_px))
        if 0 <= x < W and 0 <= y < H:
            img[max(0, y - r):y + r + 1, max(0, x - 1):x + 2, :] = rgb
            img[max(0, y - 1):y + 2, max(0, x - r):x + r + 1, :] = rgb
    save_png(img, out_path)
    return out_path, (u0, u1, v0, v1)


def _fill(img, S, u0, v0, mm_per_px, rgb, alpha: float = 1.0):
    """Even-odd scanline fill of closed loops given as unordered segments."""
    H, W, _ = img.shape
    x0 = (S[:, 0, 0] - u0) / mm_per_px
    y0 = (S[:, 0, 1] - v0) / mm_per_px
    x1 = (S[:, 1, 0] - u0) / mm_per_px
    y1 = (S[:, 1, 1] - v0) / mm_per_px
    rgb = np.asarray(rgb, dtype=np.float32)
    for row in range(H):
        yc = row + 0.5
        hit = ((y0 <= yc) & (y1 > yc)) | ((y1 <= yc) & (y0 > yc))
        if not hit.any():
            continue
        xs = np.sort(x0[hit] + (yc - y0[hit]) * (x1[hit] - x0[hit]) / (y1[hit] - y0[hit]))
        for a, b in zip(xs[0::2], xs[1::2]):
            ia, ib = max(0, int(round(a))), min(W, int(round(b)))
            if ib > ia:
                img[row, ia:ib, :] = img[row, ia:ib, :] * (1.0 - alpha) + rgb * alpha


def _posterise(path: str, levels: int = 40):
    """Reduce the number of grey levels of a rendered picture, so that the PNG is several times smaller.
    The pictures are review evidence in git; smooth shading is not needed for that."""
    img = load_png(path)
    save_png(np.round(img * (levels - 1)) / (levels - 1), path)


def save_png(img, path: str):
    """img: (H, W, 3) float array in 0..1, row 0 at the bottom (v grows upward)."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    H, W, _ = img.shape
    rgba = np.concatenate([img, np.ones((H, W, 1), dtype=np.float32)], axis=2)
    im = bpy.data.images.new("_oca_png", width=W, height=H, alpha=False)
    try:
        im.pixels.foreach_set(rgba.ravel())
        scene = bpy.context.scene
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGB"
        scene.render.image_settings.compression = 100
        _write_retry(lambda: im.save_render(os.path.abspath(path), scene=scene))
    finally:
        bpy.data.images.remove(im)


def load_png(path: str):
    im = bpy.data.images.load(os.path.abspath(path), check_existing=False)
    try:
        W, H = im.size
        px = np.empty(W * H * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        return px.reshape(H, W, 4)[:, :, :3].copy()
    finally:
        bpy.data.images.remove(im)


def contact_sheet(paths, out_path: str, cols: int = 3, cell_px: int = 460, pad: int = 6):
    """Put several pictures into one (nearest-neighbour scaling, white background)."""
    cells = []
    for p in paths:
        a = load_png(p)
        H, W, _ = a.shape
        s = min(cell_px / W, cell_px / H)
        nw, nh = max(1, int(W * s)), max(1, int(H * s))
        yi = (np.arange(nh) / s).astype(int).clip(0, H - 1)
        xi = (np.arange(nw) / s).astype(int).clip(0, W - 1)
        b = np.ones((cell_px, cell_px, 3), dtype=np.float32)
        oy, ox = (cell_px - nh) // 2, (cell_px - nw) // 2
        b[oy:oy + nh, ox:ox + nw, :] = a[yi][:, xi]
        cells.append(b)
    rows = int(math.ceil(len(cells) / cols))
    sheet = np.ones((rows * (cell_px + pad) + pad, cols * (cell_px + pad) + pad, 3), dtype=np.float32) * 0.9
    for k, c in enumerate(cells):
        r, q = divmod(k, cols)
        y = sheet.shape[0] - (r + 1) * (cell_px + pad)          # row 0 at the top of the sheet
        x = pad + q * (cell_px + pad)
        sheet[y:y + cell_px, x:x + cell_px, :] = c
    save_png(sheet, out_path)
    return out_path
