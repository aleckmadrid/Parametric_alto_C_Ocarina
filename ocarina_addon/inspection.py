"""Portable annotated geometry review, using actual sections and existing check probes.

The HTML/SVG report needs no server or third-party packages. JSON snapshots permit
aligned before/after views without retaining Blender objects or changing the scene.
"""
from __future__ import annotations

import html
import json
import math
import tempfile
from pathlib import Path

import numpy as np

SCHEMA = "ocarina-inspection-v1"
COLORS = dict(within_limit="#229485", thin_edge="#8a53bc", thin_plate="#d09214", wide_thin_plate="#df3d42")


def _plain(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def _json_safe(value):
    """Unavailable check values (NaN when a solver did not run) remain missing."""
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    return None if isinstance(value, float) and not math.isfinite(value) else value


def snapshot(body):
    from . import export, render, voicing_geo
    v, vs = body.sizing.voicing, body.voicing
    o, fx, fy, fz = (np.asarray(a, float) for a in vs.frame)
    L, W = v.window_length_mm, v.window_width_mm
    # Exported reviews show the geometry that was actually written to disk.
    solid = export.read_stl(body.files["stl"]) if body.files.get("stl") else body.solid
    extent = [-L - 8, max(16, vs.info["ramp_reach_mm"] + 3), -10, v.wall_at_window_mm + 5]
    if v.window_cut == "bowl":
        extent[0] = min(extent[0], v.bowl_centre_xw_mm - v.bowl_half_length_mm - L - 3)
        extent[1] = max(extent[1], v.bowl_centre_xw_mm + v.bowl_half_length_mm - L + 3)
    across = max(W / 2 + 6, v.bowl_half_width_mm + 3 if v.window_cut == "bowl" else 0)
    sections = {}
    for name, origin, normal, u, w, bounds in (
        ("windway", o, fy, fx, fz, extent),
        ("across", o + fx * (vs.info["widest_xw_mm"] - L), fx, fy, fz, [-across, across, -10, v.wall_at_window_mm + 5]),
        ("plan", o + fz * (0.6 * v.wall_at_window_mm), fz, fx, fy, [extent[0], extent[1], -across, across]),
    ):
        # micrometres are enough for a drawing, and a third of the file
        sections[name] = dict(solid=np.round(render.section_2d(*solid, origin, normal, u, w), 3).tolist(),
                              air=np.round(render.section_2d(*body.air_capped, origin, normal, u, w), 3).tolist(), extent=bounds)
    do, dx, dy, dz = (np.asarray(a, float) for a in vs.windway_frame())
    zc = voicing_geo.windway_centre_z(v)
    def local(p):
        return [float((p - o) @ fx), float((p - o) @ fz)]
    jet = [local(do - L * dx + zc * dz), local(do + 2 * dx + zc * dz)]
    # The labium edge against the projected axis: how far along it, and how far off it (+ above). Geometry, not airflow.
    a, b = np.asarray(jet[0]), np.asarray(jet[1])
    d, e = (b - a) / np.linalg.norm(b - a), np.array([0.0, 0.5 * v.labium_edge_thickness_mm]) - a
    jet_to_edge = dict(along_mm=float(e @ d), off_axis_mm=float(d[0] * e[1] - d[1] * e[0]))
    exit_line = [local(do - L * dx + (zc + s * v.windway_exit_height_mm / 2) * dz) for s in (-1, 1)]
    aperture = np.asarray(vs.outline)[:, :2].copy()
    aperture[:, 0] -= L
    bowl = None
    if v.window_cut == "bowl":
        bowl = dict(cx=v.bowl_centre_xw_mm - L, a=v.bowl_half_length_mm, b=v.bowl_half_width_mm)
    holes = []
    for h in body.layout.holes:
        if h.deck != "bottom":
            continue
        axis = np.asarray(h.axis, float)
        u = np.cross(axis, [1., 0., 0.])
        if np.linalg.norm(u) < 1e-6:
            u = np.cross(axis, [0., 1., 0.])
        u /= np.linalg.norm(u)
        w = np.cross(axis, u)
        centre = np.asarray(h.centre) + h.wall_mm * axis
        seal = body.measurements.get("seal", {}).get(h.name, {}).get("seal_mm")
        rings = []
        for radius in (h.d_mm / 2, h.d_mm / 2 + seal if seal is not None else h.d_mm / 2):
            rings.append([(centre + radius * (math.cos(t) * u + math.sin(t) * w))[:2].tolist()
                          for t in np.linspace(0, 2 * math.pi, 65)])
        measured = next((r for r in body.measurements.get("holes", []) if r["name"] == h.name), {})
        holes.append(dict(name=h.name, centre=centre[:2].tolist(), rings=rings, diameter=h.d_mm, seal=seal,
                          nearest_gap=measured.get("nearest_gap_mm"), nearest_hole=measured.get("nearest_hole")))
    V, F = solid
    # Horizontal section provides body context; thumb rings are projections of their
    # actual tilted axes, rather than circles that imply a flat sealing surface.
    mid = 0.5 * (float(V[:, 2].min()) + float(V[:, 2].max()))
    sections["thumbs"] = dict(solid=np.round(render.section_2d(V, F, [0, 0, mid], [0, 0, 1], [1, 0, 0], [0, 1, 0]), 3).tolist(), air=[],
                               extent=[float(V[:, 0].min()) - 3, float(V[:, 0].max()) + 3,
                                       float(V[:, 1].min()) - 3, float(V[:, 1].max()) + 3])
    aperture_world = o + aperture[:, :1] * fx + aperture[:, 1:] * fy
    calibration = body.info.get("calibration_info", {})
    return dict(schema=SCHEMA, body_id=body.body_id, voicing_hash=body.voicing_hash,
                source="exported STL" if body.files.get("stl") else "mesh in memory", sections=sections,
                voicing=v.to_dict(), jet=jet, exit_line=exit_line, jet_to_edge=jet_to_edge,
                measured=body.measurements.get("voicing", {}),          # empty when the checks did not run
                aperture=aperture.tolist(), bowl=bowl,
                aperture_world=aperture_world[:, :2].tolist(), holes=holes,
                local=body.measurements.get("bowl_local", {}), calibration=calibration,
                synthetic=bool(body.info.get("synthetic")), checks=body.checks,
                built_air_cm3=body.air_capped_cm3, target_air_cm3=body.v0_cm3,
                context=body.info.get("calibration_context"),
                build_options=body.info.get("unhashed_voicing_options", {}),
                identity=body.info.get("shell_edit", {}).get("calibration_identity"))


def load_snapshot(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError("Choose an ocarina inspection JSON snapshot for the comparison.")
    for key in ("windway", "across", "plan", "thumbs"):
        sec = data["sections"][key]
        for name in ("solid", "air"):
            a = np.asarray(sec[name], float)
            if a.size and (a.ndim != 3 or a.shape[1:] != (2, 2) or not np.isfinite(a).all()):
                raise ValueError("Invalid section coordinates in inspection snapshot")
        if len(sec["extent"]) != 4 or not all(math.isfinite(x) for x in sec["extent"]):
            raise ValueError("Invalid section extent in inspection snapshot")
    return data


def verify(data, checks, tol_mm=0.05):
    """What a snapshot shows against the check report it was drawn from (<id>_checks.json): a list of differences,
    empty when they agree. tol_mm is checks_geo.TOL_MM, the tolerance of the checks themselves."""
    bad = []
    if data["voicing_hash"] != checks["voicing_hash"]:
        bad.append(f"voicing hash {data['voicing_hash']} against {checks['voicing_hash']} in the check report")
    reported = _json_safe(checks["measurements"].get("voicing", {}))
    design = data["voicing"]
    for name, shown in data.get("measured", {}).items():
        if shown != reported.get(name) and not (isinstance(shown, float) and math.isclose(shown, reported.get(name) or math.inf, abs_tol=1e-9)):
            bad.append(f"{name}: drawn {shown}, check report {reported.get(name)}")
        if name.endswith("_mm") and isinstance(shown, float) and isinstance(design.get(name), float) and abs(shown - design[name]) > tol_mm:
            bad.append(f"{name}: measured {shown:.3f} mm, design {design[name]:.3f} mm")
    off = design["labium_offset_mm"] * math.cos(math.radians(design["windway_pitch_deg"]))
    if abs(data["jet_to_edge"]["off_axis_mm"] - off) > 1e-6:
        bad.append(f"labium edge {data['jet_to_edge']['off_axis_mm']:.4f} mm off the projected axis, the design gives {off:.4f} mm")
    return bad


def _esc(text):
    return html.escape(str(text), quote=True)


def _num(value, unit=" mm"):
    return "not measured" if value is None else f"{value:.2f}{unit}"


def _both(data, name, unit=" mm"):
    """The check's measurement beside the design value; a snapshot without checks says so."""
    return f"{_num(data.get('measured', {}).get(name), unit)} (design {data['voicing'][name]:.2f}{unit})"


def status(data):
    c = data.get("calibration", {})
    return ("SYNTHETIC design calibration; " if data.get("synthetic") else "") + (
        f"Voicing: {c.get('eta_w_match', 'uncalibrated')} · Layout: {c.get('psi_match', 'unfitted')}. Physical tuning not established by this drawing.")


def svg_view(data, key, previous=None, *, only_current=False):
    """Current/previous sections share one orthographic coordinate transform."""
    source_key = "plan" if key == "thickness" else key
    bounds = list(data["sections"][source_key]["extent"])
    if previous:
        b = previous["sections"][source_key]["extent"]
        bounds = [min(bounds[0], b[0]), max(bounds[1], b[1]), min(bounds[2], b[2]), max(bounds[3], b[3])]
    x0, x1, y0, y1 = bounds
    scale = min(820 / max(x1-x0, 1), 270 / max(y1-y0, 1))
    left, top = 40 + (820 - scale * (x1-x0)) / 2, 68 + (270 - scale * (y1-y0)) / 2
    def xy(p):
        return left + (p[0]-x0)*scale, top + (y1-p[1])*scale
    def path(segments, color, width=1, dash=""):
        d = " ".join(f"M{xy(a)[0]:.2f},{xy(a)[1]:.2f}L{xy(b)[0]:.2f},{xy(b)[1]:.2f}" for a,b in segments)
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>'
    def poly(points, color, dash=""):
        return path(list(zip(points, points[1:] + points[:1])), color, 1.7, dash)
    def text(p, s, color="#354151"):
        x,y=xy(p)
        return f'<text x="{x:.2f}" y="{y:.2f}" fill="{color}" font-size="12">{_esc(s)}</text>'
    title = {"windway":"Along the windway", "across":"Across the window", "plan":"Window plan", "thickness":"Local plastic thickness", "thumbs":"Thumb face projection"}[key]
    if key == "thickness":
        title += " — " + data["body_id"]
    clip_id = "clip_" + key
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 410" role="img" aria-label="{_esc(title)}" style="font-family:Arial,sans-serif">',
           '<rect width="900" height="410" fill="#fff"/>', f'<text x="24" y="25" font-size="18" fill="#182e40">{_esc(title)}</text>',
           f'<defs><clipPath id="{clip_id}"><rect x="{left}" y="{top}" width="{scale*(x1-x0)}" height="{scale*(y1-y0)}"/></clipPath></defs>',
           f'<g clip-path="url(#{clip_id})">']
    grid = 5 if x1-x0 < 80 else 10
    for x in np.arange(math.ceil(x0/grid)*grid,x1,grid):
        out.append(path([([x,y0],[x,y1])], "#e5ebef"))
    for y in np.arange(math.ceil(y0/grid)*grid,y1,grid):
        out.append(path([([x0,y],[x1,y])], "#e5ebef"))
    for d, css, color in ((previous,"previous","#bc7b29"),(data,"current","#243d50")):
        if not d or (only_current and css == "previous"):
            continue
        layer_class = "thickness-map" if only_current else css
        out.append(f'<g class="{layer_class}">')
        s=d["sections"][source_key]
        out.append(path(s["air"], "#7db8f4", .8))
        out.append(path(s["solid"],color,1.4,"5 3" if css=="previous" else ""))
        if key in ("plan","thickness"):
            # in a comparison the previous aperture is amber, as its section is
            out.append(poly(d["aperture"], "#bc7b29" if css=="previous" and not only_current else "#275eda", "5 3" if css=="previous" and not only_current else ""))
            if d["bowl"]:
                b=d["bowl"]
                pts=[[b["cx"]+b["a"]*math.cos(t), b["b"]*math.sin(t)] for t in np.linspace(0,2*math.pi,100)]
                out.append(poly(pts,"#8a53bc","5 3"))
        if key=="windway":
            out.append(path([d["jet"]],"#db6340",1.8,"6 4"))
            out.append(path([d["exit_line"]],"#208d85",2.7))
            p=xy([0,d["voicing"]["labium_edge_thickness_mm"]/2])
            out.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="4" fill="#8a53bc"/>')
        if key=="thumbs":
            out.append(poly(d["aperture_world"],"#275eda"))
            for h in d["holes"]:
                if h["seal"] is not None:
                    out.append(poly(h["rings"][1],"#229485","3 2"))
                out.append(poly(h["rings"][0],color))
                out.append(text([h["centre"][0]+2,h["centre"][1]+8],h["name"]))
        if key=="thickness":
            # Draw all reduced probe classes; failing plates remain on top.
            samples=sorted(d["local"].get("map_samples",[]),key=lambda s:list(COLORS).index(s["category"]))
            for s in samples:
                p=s["xw_y_z"]
                x,y=xy([p[0]-d["voicing"]["window_length_mm"],p[1]])
                normal = s["category"] == "within_limit"
                radius, opacity = (1.0, 0.18) if normal else (2.2, 1.0)
                out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" opacity="{opacity}" fill="{COLORS[s["category"]]}"><title>{_esc(s["region"])}: {s["thickness_mm"]:.3f} mm, {_esc(s["category"])}</title></circle>')
            for name, r in d["local"].get("regions", {}).items():
                if r.get("at_xw_y_z"):
                    x,y=xy([r["at_xw_y_z"][0]-d["voicing"]["window_length_mm"],r["at_xw_y_z"][1]])
                    out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="none" stroke="#182e40"><title>{_esc(name)}: least {r["least_mm"]:.3f} mm</title></circle>')
        out.append('</g>')
    out.append('</g>')
    v = data["voicing"]
    if key == "windway":
        j = data.get("jet_to_edge")
        notes = (f"Exit {_both(data, 'windway_exit_height_mm')}  |  Labium offset {_both(data, 'labium_offset_mm')}  |  Duct {v['windway_pitch_deg']:+.1f}° (design)",
                 f"Jet to edge {j['along_mm']:.2f} mm along the projected axis, edge {j['off_axis_mm']:+.2f} mm off it" if j else "Jet to edge unavailable")
        for y, note in zip((46, 62), notes):                  # two lines: one runs off the drawing
            out.append(f'<text x="24" y="{y}" font-size="12" fill="#354151">{_esc(note)}</text>')
    if key == "plan":
        note = f"Designed aperture {v['window_length_mm']:.2f} × {v['window_width_mm']:.2f} mm  |  {v['window_area_mm2']:.2f} mm²  |  {v['shape']}"
        out.append(f'<text x="24" y="52" font-size="13" fill="#354151">{_esc(note)}</text>')
    legend = ("single build · aperture: blue · nominal bowl boundary: purple dashed" if only_current else
              "current solid: blue-grey · previous: dashed amber · cavity section: light blue")
    out.append(f'<text x="24" y="375" font-size="12" fill="#526071">{grid} mm grid · {legend}</text>')
    captions={"windway":"Orange: projected jet axis (geometric guide, not CFD) · green: exit height · purple: labium centre",
              "across":"Section at the current window’s widest point; previous uses its own widest point.",
              "plan":"Blue: designed aperture (previous: amber dashed) · purple dashed: nominal bowl boundary · dark: actual throat section",
              "thickness":"Green: within limit · purple: thin edge · amber: narrow thin plate · red: failing wide plate · ring: least of a region",
              "thumbs":"Projected hole rims and measured sealing bands; body context is a horizontal section, not a silhouette."}
    out.append(f'<text x="24" y="395" font-size="11" fill="#526071">{_esc(captions[key])}</text></svg>')
    return ''.join(out)


def render_html(data, previous=None):
    v=data["voicing"]
    def table(headers, rows):
        return '<table><thead><tr>'+''.join('<th>'+_esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+_esc(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'
    out=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>Ocarina geometry inspection</title><style>body{font:15px/1.5 system-ui,sans-serif;color:#243d50;background:#edf2f5;margin:0}main{max-width:1200px;margin:auto;padding:28px}h1{margin-bottom:6px}h2{font-size:19px}section{background:white;padding:20px;margin:18px 0;border-radius:10px}svg{width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:13px}td,th{text-align:left;border-bottom:1px solid #dde5eb;padding:8px}th{background:#f4f7f9}.status{border-left:5px solid #bd832e;padding:12px;background:#fff4df}label{margin-right:22px}.grid{display:grid;grid-template-columns:1fr;gap:16px}.grid section{min-width:0;margin:0}@media(max-width:850px){.grid{grid-template-columns:1fr}}small{color:#526071}</style><main>',
         f'<h1>{_esc(data["body_id"])} — geometry inspection</h1><p>Source: {_esc(data["source"])} · voicing {_esc(data["voicing_hash"])} · dimensions in millimetres</p>',
         f'<p class="status">{_esc(status(data))}</p>']
    if previous:
        out += [f'<p>Previous: {_esc(previous["body_id"])} · {_esc(status(previous))}</p>',
                '<p><label><input type="checkbox" checked onchange="document.querySelectorAll(\'.current\').forEach(e=>e.style.display=this.checked?\'\':\'none\')">Current overlay</label><label><input type="checkbox" checked onchange="document.querySelectorAll(\'.previous\').forEach(e=>e.style.display=this.checked?\'\':\'none\')">Previous overlay</label> Both use the same framing in each view. Thickness maps are shown separately.</p>']
    out += ['<section><h2>Design dimensions and built air</h2>', table(['Quantity','Current','Previous'],[
        (label,_num(v[name],unit),_num(previous['voicing'][name],unit) if previous else '—')
        for label,name,unit in [('Window length along jet','window_length_mm',' mm'),('Window width','window_width_mm',' mm'),('Aperture area','window_area_mm2',' mm²'),('Windway exit height','windway_exit_height_mm',' mm'),('Labium offset relative to jet','labium_offset_mm',' mm'),('Windway pitch','windway_pitch_deg','°'),('Wall throat convention','wall_at_window_mm',' mm')]] +
        [('Built capped air',_num(data['built_air_cm3'],' cm³'),_num(previous['built_air_cm3'],' cm³') if previous else '—')]),
        '<h2>Measured by the checks</h2>', table(['Quantity','Measured (design)'],[(label,_both(data,name,unit)) for label,name,unit in [
            ('Windway exit height','windway_exit_height_mm',' mm'),('Labium offset relative to jet','labium_offset_mm',' mm'),
            ('Labium edge thickness','labium_edge_thickness_mm',' mm')]]),
        '<p><small>Dimensions above are resolved design values. Sections show the built mesh. Window length is the design exit-to-labium span along the untilted frame; the projected jet follows the tilted duct.</small></p></section>',
        '<div class="grid">']
    for key in ('windway','across','plan'):
        out.append('<section>'+svg_view(data,key,previous)+'</section>')
    out.append('<section>'+svg_view(data,'thickness',previous,only_current=True)+'</section>')
    if previous:
        out.append('<section><p>Previous build thickness, shown separately at the same scale.</p>'+svg_view(previous,'thickness',data,only_current=True)+'</section>')
    out.append('</div><section><h2>Local plastic measurements</h2>')
    regions=data['local'].get('regions',{})
    if regions:
        out.append(table(['Region','Least sampled','Least parallel plate','Plate limit','Wide thin plate probes'],[(name,_num(r.get('least_mm')),_num(r.get('least_plate_mm')),_num(r['limit_mm']),r['wide_thin_plate_probes']) for name,r in regions.items()]))
        out.append('<p><small>The map retains the thinnest probe of each class per 0.5 mm plan cell, including hidden surfaces. Checks use every probe. A thin edge is descriptive; a wide thin plate fails its regional limit. Hover over a point for thickness.</small></p>')
    else:
        out.append('<p>Local bowl measurements are unavailable for this build. No pass is inferred.</p>')
    out += ['</section><section>',svg_view(data,'thumbs',previous),table(['Hole','Design diameter','Measured sealing band','Measured nearest edge gap'],[(h['name'],_num(h['diameter']),_num(h['seal']),_num(h['nearest_gap']) + (' to '+h['nearest_hole'] if h.get('nearest_hole') else '')) for h in data['holes']]),'</section>']
    if previous:
        changes=[(name,str(previous['voicing'].get(name,'—')),str(value)) for name,value in v.items() if previous['voicing'].get(name)!=value]
        options, old_options = data.get('build_options', {}), previous.get('build_options', {})
        changes += [(name, str(old_options.get(name, 'default')), str(options.get(name, 'default')))
                    for name in sorted(set(options) | set(old_options)) if old_options.get(name) != options.get(name)]
        out += ['<section><h2>Changed voicing settings</h2>',table(['Setting','Previous','Current'],changes) if changes else '<p>No resolved voicing settings changed.</p>',
                '<p>Calibration context comparison: '+_esc('unavailable' if not data.get('context') or not previous.get('context') else 'same' if data['context']==previous['context'] else 'different')+'. This describes reuse compatibility, not measured tuning.</p></section>']
    out += ['<section><h2>Geometry check status</h2>',table(['Check','Status','Detail'],[(c['name'],c['status']+(' (expected)' if c.get('expected') else ''),c['message']) for c in data['checks']]),'</section></main></html>']
    return ''.join(out)


def write_inspection(body, out_dir=None, *, previous_path=None):
    previous=load_snapshot(previous_path) if previous_path else None
    data=_json_safe(snapshot(body))
    out=Path(out_dir) if out_dir else Path(tempfile.mkdtemp(prefix='ocarina-review-'))
    out=out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    stem=out / f'{body.body_id}_inspection'
    json_path=stem.with_suffix('.json')
    json_path.write_text(json.dumps(data,default=_plain,allow_nan=False)+ '\n',encoding='utf-8')
    page=stem.with_suffix('.html')
    page.write_text(render_html(data,previous),encoding='utf-8')
    body.files.update(inspection=str(page),inspection_snapshot=str(json_path))
    for key in ('windway','across','plan','thickness','thumbs'):
        path=out / f'{body.body_id}_{key}.svg'
        path.write_text(svg_view(data,key,previous,only_current=key == 'thickness'),encoding='utf-8')
    return str(page)
