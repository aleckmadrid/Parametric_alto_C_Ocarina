"""Tuning evidence of one measured body as a portable HTML page (docs/10, step 4). Plain Python, no Blender.

    python -m ocarina_addon.evidence <measurement.toml> [...] [--checks <id>_checks.json] [--out <folder>]

Three things are shown and never mixed: the design targets (a prediction), the measured pitches (the takes, each one a
mark) and the geometry checks (which say that the body can be built, not how it plays). Below them, per fingering, the
paired pressure and pitch readings as they were recorded: every status, the speaking limits that were seen, the clean
runs the kernel supports, and its fit (kernel fitter.pressure_response) as a description of this specimen.

Nothing is interpolated across a gap and no pressure fit goes into sizing. A file marked synthetic says SYNTHETIC in
the title, in every figure and in the file name.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import sys
from pathlib import Path

STATUS_COLORS = dict(clean="#229485", airy="#d09214", unstable="#df3d42", absent="#7a8794")
INK, FAINT = "#243d50", "#dde5eb"


def _esc(text) -> str:
    return html.escape(str(text), quote=True)


def _svg(width, height, parts, label, synthetic) -> str:
    mark = (f'<text x="{width - 8}" y="14" text-anchor="end" font-size="11" fill="#bd832e">SYNTHETIC</text>' if synthetic else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{_esc(label)}" '
            f'style="font-family:Arial,sans-serif">{"".join(parts)}{mark}</svg>')


def _span(values, pad, least):
    """An axis range around the values (and zero), never narrower than ±least."""
    lo, hi = min([0.0, *values]), max([0.0, *values])
    return min(lo - pad, -least), max(hi + pad, least)


def _groups(k, m):
    """The fingerings of the chart in two groups: A4 and B4 speak through the subholes, C5 to F6 through the main holes."""
    first_main = k.measurements.note_midi(k.fitter.MAIN_FROM)
    sub = [n for n in m.notes if k.measurements.note_midi(n.name) < first_main]
    return [("A4, B4 (subholes)", sub), ("C5 to F6", [n for n in m.notes if n not in sub])]


def measured_svg(k, m) -> str:
    """Every take as a mark, the mean as a bar; the two groups apart. Nothing is predicted here."""
    takes = [c for n in m.notes for c in n.takes_cents]
    lo, hi = _span(takes, 5.0, 20.0)
    W, H, left, top, plot_h, step = 900, 300, 60, 40, 200, 58
    y = lambda c: top + plot_h * (hi - c) / (hi - lo)
    out = [f'<rect width="{W}" height="{H}" fill="#fff"/>',
           f'<line x1="{left}" y1="{y(0):.1f}" x2="{W - 10}" y2="{y(0):.1f}" stroke="{INK}"/>',
           f'<text x="{left - 6}" y="{y(0) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK}">0</text>']
    for c in (lo, hi):
        out.append(f'<text x="{left - 6}" y="{y(c) + 4:.1f}" text-anchor="end" font-size="11" fill="{INK}">{c:+.0f} cents</text>')
    x = left + 30
    for title, notes in _groups(k, m):
        out.append(f'<text x="{x - 20}" y="{top - 14}" font-size="12" fill="{INK}">{_esc(title)}</text>')
        for n in notes:
            for c in n.takes_cents:
                out.append(f'<circle cx="{x}" cy="{y(c):.1f}" r="3.5" fill="none" stroke="#229485" stroke-width="1.5">'
                           f'<title>{_esc(n.name)}: {c:+.1f} cents</title></circle>')
            if n.takes_cents:
                out.append(f'<line x1="{x - 12}" y1="{y(n.cents_mean):.1f}" x2="{x + 12}" y2="{y(n.cents_mean):.1f}" stroke="{INK}" stroke-width="2"/>')
                out.append(f'<text x="{x}" y="{top + plot_h + 34}" text-anchor="middle" font-size="11" fill="{INK}">{n.cents_mean:+.0f}</text>')
            out.append(f'<text x="{x}" y="{top + plot_h + 18}" text-anchor="middle" font-size="12" fill="{INK}">{_esc(n.name)}</text>')
            x += step
        x += 40                                             # the gap between the groups
    return _svg(W, H, out, "Measured pitch of each fingering", m.synthetic)


def _cents(k, m, o):
    """An observation's pitch against its target, as the kernel takes the target; None when either is missing."""
    target = o.target_hz if o.target_hz is not None else next((n.target_hz for n in m.notes if n.name == o.fingering), None)
    if target is None:
        try:
            target = k.measurements.note_hz(o.fingering)
        except (KeyError, ValueError, IndexError):
            return None
    return None if o.hz is None else 1200.0 * (math.log2(o.hz) - math.log2(target))


def pressure_svg(k, m, name, s, p_range) -> str:
    """One fingering: what was read at which pressure. A reading without a pitch is a mark on the axis, not a point."""
    obs = [o for o in m.observations if o.fingering == name]
    note = next((n for n in m.notes if n.name == name), None)
    points = [(o, _cents(k, m, o)) for o in obs]
    takes = list(zip(note.pressures_pa, note.takes_cents)) if note else []
    lo, hi = _span([c for _, c in points if c is not None] + [c for _, c in takes], 5.0, 20.0)
    W, H, left, top, pw, ph = 300, 230, 44, 30, 240, 140
    p0, p1 = (math.log(p) for p in p_range)
    x = lambda p: left + pw * (math.log(p) - p0) / ((p1 - p0) or 1.0)
    y = lambda c: top + ph * (hi - c) / (hi - lo)
    out = [f'<rect width="{W}" height="{H}" fill="#fff"/>', f'<text x="8" y="16" font-size="13" fill="{INK}">{_esc(name)}</text>']
    for a, b in s["clean_intervals_pa"]:                    # the runs the kernel supports as clean
        out.append(f'<rect x="{x(a):.1f}" y="{top}" width="{max(x(b) - x(a), 1.5):.1f}" height="{ph}" fill="#229485" opacity="0.10"/>')
    out.append(f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="none" stroke="{FAINT}"/>')
    out.append(f'<line x1="{left}" y1="{y(0):.1f}" x2="{left + pw}" y2="{y(0):.1f}" stroke="{INK}" stroke-width="0.8"/>')
    for c in (lo, hi):
        out.append(f'<text x="{left - 4}" y="{y(c) + 4:.1f}" text-anchor="end" font-size="10" fill="{INK}">{c:+.0f}</text>')
    for p in p_range:
        out.append(f'<text x="{x(p):.1f}" y="{top + ph + 13}" text-anchor="middle" font-size="10" fill="{INK}">{p:.0f} Pa</text>')
    for label, p in (("onset", s["onset_pa"]), ("break", s["break_pa"])):
        if p is not None:
            out.append(f'<line x1="{x(p):.1f}" y1="{top}" x2="{x(p):.1f}" y2="{top + ph}" stroke="{INK}" stroke-dasharray="4 3"/>'
                       f'<text x="{x(p) + 2:.1f}" y="{top + 10}" font-size="10" fill="{INK}">{label} {p:.0f}</text>')
    b = s["slope_cents_per_doubling"]
    if b is not None and s["clean"]:                        # the fit, over the clean readings' own range only
        xs, ys = [math.log(p) for p, _ in s["clean"]], [c for _, c in s["clean"]]
        slope = b / math.log(2.0)
        at = lambda lp: sum(ys) / len(ys) + slope * (lp - sum(xs) / len(xs))
        a, z = min(xs), max(xs)
        out.append(f'<line x1="{x(math.exp(a)):.1f}" y1="{y(at(a)):.1f}" x2="{x(math.exp(z)):.1f}" y2="{y(at(z)):.1f}" '
                   f'stroke="#275eda" stroke-dasharray="6 3"><title>descriptive fit: {b:+.1f} cents per doubling of pressure</title></line>')
    for p, c in takes:
        out.append(f'<rect x="{x(p) - 3:.1f}" y="{y(c) - 3:.1f}" width="6" height="6" fill="none" stroke="{INK}"><title>take: {p:.0f} Pa, {c:+.1f} cents</title></rect>')
    for o, c in points:
        colour = STATUS_COLORS.get(o.status, INK)
        if o.p_pa is None:
            continue                                        # counted in the caption: there is no place to draw it
        tip = f"<title>{_esc(o.status)}: {o.p_pa:.0f} Pa" + (f", {c:+.1f} cents" if c is not None else ", no pitch") + "</title>"
        if c is None:                                       # the note did not speak, or no pitch was read
            out.append(f'<path d="M{x(o.p_pa) - 4:.1f},{top + ph - 4}l8,8m0,-8l-8,8" stroke="{colour}" stroke-width="1.6">{tip}</path>')
        else:
            out.append(f'<circle cx="{x(o.p_pa):.1f}" cy="{y(c):.1f}" r="3.5" fill="{colour}">{tip}</circle>')
    seen = ", ".join(f"{v} {key}" for key, v in s["by_status"].items())
    limits = "; ".join(f"{label} not seen" for label, p in (("onset", s["onset_pa"]), ("break", s["break_pa"])) if p is None)
    no_p = sum(o.p_pa is None for o in obs)
    for i, line in enumerate(filter(None, (seen, limits, f"{no_p} reading(s) without a pressure, not drawn" if no_p else "",
                                           f"fit {b:+.1f} cents per doubling; in tune: {s['in_tune']}" if b is not None else "no fit"))):
        out.append(f'<text x="8" y="{top + ph + 28 + 12 * i}" font-size="10" fill="#526071">{_esc(line)}</text>')
    return _svg(W, H, out, f"Pressure and pitch readings of {name}", m.synthetic)


def render_html(k, m, checks: dict | None = None) -> str:
    """The page of one measured body. checks: the content of its <id>_checks.json, when there is one."""
    response = k.fitter.pressure_response(m)                # raises ValueError naming the fingering on a bad number
    tag = "SYNTHETIC " if m.synthetic else ""
    table = lambda head, rows: ("<table><thead><tr>" + "".join(f"<th>{_esc(h)}</th>" for h in head) + "</tr></thead><tbody>"
                                + "".join("<tr>" + "".join(f"<td>{_esc(c)}</td>" for c in row) + "</tr>" for row in rows) + "</tbody></table>")
    out = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
           f"<title>{_esc(tag)}Tuning evidence {_esc(m.id)}</title>",
           "<style>body{font:15px/1.5 system-ui,sans-serif;color:#243d50;background:#edf2f5;margin:0}main{max-width:1200px;margin:auto;padding:28px}"
           "section{background:#fff;padding:20px;margin:18px 0;border-radius:10px}h2{font-size:19px}svg{max-width:100%;height:auto}"
           "table{border-collapse:collapse;width:100%;font-size:13px}td,th{text-align:left;border-bottom:1px solid #dde5eb;padding:6px}"
           ".status{border-left:5px solid #bd832e;padding:12px;background:#fff4df}.grid{display:flex;flex-wrap:wrap;gap:10px}"
           ".grid svg{width:300px}small{color:#526071}</style><main>",
           f"<h1>{_esc(tag)}Tuning evidence: {_esc(m.id)}</h1>",
           f"<p>Shape {_esc(m.shape)} · voicing {_esc(m.voicing_hash)} · room {m.room_temp_c:.1f} °C · measured air {m.v0_cm3:.2f} cm³ "
           f"(target {m.target_v0_cm3:g} cm³)</p>"]
    if m.synthetic:
        out.append('<p class="status">SYNTHETIC DATA. Nothing on this page was measured on a printed body.</p>')
    out += ["<section><h2>Predicted: the design targets</h2>",
            "<p><small>What the sizing aimed at. A prediction of the model, not an observation.</small></p>",
            table(["Fingering", "Target Hz"], [(n.name, f"{n.target_hz:.2f}") for n in m.notes]), "</section>",
            "<section><h2>Measured: the takes</h2>",
            "<p><small>Cents against the target. Each circle is one take, the bar is their mean. A4 and B4 are kept apart from C5 to F6.</small></p>",
            measured_svg(k, m), "</section>", "<section><h2>Pressure and pitch, per fingering</h2>"]
    if response:
        out.append("<p><small>Filled circle: a paired reading, coloured by its status (green clean, amber airy, red unstable). Cross on the axis: "
                   "no pitch at that pressure. Square: a take of the chart. Green band: a clean run the readings support. Dashed blue: a fit of "
                   "this specimen's clean readings, drawn over their own range only. It describes this body at these conditions; it is not used "
                   "to size holes. Nothing is drawn where nothing was read.</small></p>")
        ps = [o.p_pa for o in m.observations if o.p_pa] + [p for n in m.notes for p in n.pressures_pa] \
            + [p for pair in m.speaking_range.values() for p in pair if p]
        p_range = (min(ps), max(ps))
        for group, title in (("subhole", "A4, B4 (subholes)"), ("main", "C5 to F6"), ("other", "Other fingerings")):
            names = [n for n, s in response.items() if s["group"] == group]
            if names:
                out.append(f"<h3>{_esc(title)}</h3><div class=\"grid\">" + "".join(pressure_svg(k, m, n, response[n], p_range) for n in names) + "</div>")
    else:
        out.append("<p>This file has no paired pressure and pitch readings ([[observation]]). Nothing is inferred from the takes alone.</p>")
    out.append("</section><section><h2>Geometry checks</h2>")
    if checks:
        rows = [(c["name"], c["status"] + (" (expected)" if c.get("expected") else ""), c["message"]) for c in checks["checks"] if c["status"] != "pass"]
        passed = sum(c["status"] == "pass" for c in checks["checks"])
        out.append(f"<p>{passed} checks passed" + (f" · check report of voicing {_esc(checks['voicing_hash'])}" if checks["voicing_hash"] != m.voicing_hash else "")
                   + ". They establish that the body can be built, not how it is tuned.</p>" + (table(["Check", "Status", "Detail"], rows) if rows else ""))
        if checks["voicing_hash"] != m.voicing_hash:
            out.append('<p class="status">The check report is of another voicing than the measurement file.</p>')
    else:
        out.append("<p>No check report was given. Nothing is assumed about the geometry.</p>")
    out.append("</section></main></html>")
    return "".join(out)


def write_evidence(measurement_path, out_dir=None, checks_path=None) -> Path:
    """Write <id>_evidence.html (SYNTHETIC-<id>_evidence.html for a synthetic file) and return its path. The check report
    beside the measurement file (<id>_checks.json) is used when none is given."""
    from . import kernel_bridge
    k = kernel_bridge.kernel()
    measurement_path = Path(measurement_path)
    m = k.measurements.load_measurement(measurement_path)
    checks_path = Path(checks_path) if checks_path else measurement_path.with_name(f"{m.id}_checks.json")
    checks = json.loads(checks_path.read_text(encoding="utf-8")) if checks_path.is_file() else None
    out = Path(out_dir) if out_dir else measurement_path.parent
    out.mkdir(parents=True, exist_ok=True)
    page = out / f"{'SYNTHETIC-' if m.synthetic else ''}{m.id}_evidence.html"
    page.write_text(render_html(k, m, checks), encoding="utf-8")
    return page


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m ocarina_addon.evidence", description="Tuning evidence of measured bodies (docs/10, step 4).")
    ap.add_argument("files", nargs="+", help="filled measurement TOML files, one per body")
    ap.add_argument("--checks", help="the <id>_checks.json of the body (default: beside the measurement file)")
    ap.add_argument("--out", help="folder for the pages (default: beside each measurement file)")
    args = ap.parse_args(argv)
    for f in args.files:
        print(write_evidence(f, args.out, args.checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
