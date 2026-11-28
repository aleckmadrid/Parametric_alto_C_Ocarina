"""Measurement provenance for exported bodies; no Blender dependency.

The template is blank even when the design used synthetic constants. The accompanying
record labels that design provenance separately. A measurement file that was touched is never replaced.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import kernel_bridge


def require_new_export(folder, body_id):
    """A specimen may be exported again only while its measurement template is as it was written (its hash is in the
    specimen record). Anything else, a comment included, is somebody's record and is never replaced."""
    template, record = (Path(folder) / f"{body_id}{suffix}" for suffix in ("_measurement.toml", "_specimen.json"))
    if not template.exists() and not record.exists():
        return
    try:
        blank = json.loads(record.read_text(encoding="utf-8"))["blank_template_sha256"]
        untouched = blank == hashlib.sha256(template.read_bytes()).hexdigest()
    except (OSError, ValueError, KeyError, TypeError):
        untouched = False
    if not untouched:
        raise FileExistsError("This folder holds a measurement record of this specimen. Choose a new export folder or body ID to keep it.")


def write_bundle(body, preset, folder):
    """Write the template and resolved design record beside the already exported mesh."""
    folder = Path(folder).resolve()
    require_new_export(folder, body.body_id)
    folder.mkdir(parents=True, exist_ok=True)
    k = kernel_bridge.kernel()
    context = body.info["calibration_context"]              # the one build_body matched the constants on
    template = k.measurements.template_from_sizing(
        body.sizing, body.body_id, shape=body.preset_id,
        key=body.params["hole_key"], context=context)
    template.comment = "Blank physical measurement template. Design calibration provenance is in the companion specimen JSON."
    if body.info.get("synthetic", False):
        template.comment += " The design used SYNTHETIC calibration constants; no observations are supplied."
    path = folder / f"{body.body_id}_measurement.toml"
    k.measurements.write_measurement_file(path, template, blank=True)
    body.files["measurement"] = str(path)
    blank_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    record = dict(schema="ocarina-specimen-v1", body_id=body.body_id, preset=preset,
                  voicing=body.sizing.voicing.to_dict(), context=context,
                  blank_template_sha256=blank_hash,
                  calibration_identity=body.info.get("shell_edit", {}).get("calibration_identity"),
                  calibration=body.info.get("calibration_info", {}),
                  design_uses_synthetic_calibration=bool(body.info.get("synthetic", False)),
                  params=body.params, target_v0_cm3=body.v0_cm3,
                  built_air_cm3=body.air_capped_cm3,
                  holes=[dict(name=h.name, diameter_mm=h.d_mm, wall_mm=h.wall_mm,
                              tube_mm=h.tube_mm, centre=list(h.centre), axis=list(h.axis))
                         for h in body.layout.holes], files=dict(body.files))
    path = folder / f"{body.body_id}_specimen.json"
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    body.files["specimen"] = str(path)
    body.files["checklist"] = str(write_checklist(body, folder))
    return record


def write_checklist(body, folder):
    """PRINT-AND-MEASURE.md beside an exported specimen: what to print, what to measure (docs/04, "What to measure"),
    what to fill in and the commands that follow. The list of what the loader still wants is the loader's own."""
    k = kernel_bridge.kernel()
    name = lambda key: Path(body.files[key]).name
    try:
        k.measurements.load_measurement(body.files["measurement"])
        missing = []
    except k.measurements.MeasurementIncomplete as exc:
        missing = exc.missing
    kinds = sorted({m.split(":")[-1].strip() if m.startswith("[[") else m for m in missing})
    expected = [c["name"] for c in body.checks if c.get("expected")]
    unexpected = [c["name"] for c in body.checks if c["status"] == "fail" and not c.get("expected")]
    lines = [
        f"# Print and measure {body.body_id}", "",
        "Geometry checks say this body can be built. They say nothing about its tuning: that is what this sheet measures.", "",
        "## Before printing", "",
        f"- Print `{name('stl')}`. The two air files are for the checks, not for the printer.",
        f"- Voicing `{body.voicing_hash}`, target air volume {body.v0_cm3:g} cm³, built {body.air_capped_cm3:.2f} cm³.",
        "- Geometry checks: " + ("no unexpected failure" if not unexpected else "UNEXPECTED FAILURES: " + ", ".join(unexpected))
        + ("; expected failures: " + ", ".join(expected) if expected else "") + f". Details in `{name('report')}`."
        if body.files.get("report") else "- Geometry checks: no report was written.",
        "- Material: PLA, solid walls (docs/04 budgets solid 4 mm walls with about 12 % for supports and a brim).",
        "- Orientation, layer height and nozzle: not specified in docs/04. Write down what was used, in `comment` of the measurement file.",
        "- The first print of a layout freezes the hole positions for the later rounds (docs/04 D10).", "",
        "## What you need", "",
        "- A tuner app or a recording, a water manometer (clear tubing, a ruler, a tee into a mouthpiece tube), a scale reading to 0.1 g, "
        "drill-bit shanks as hole gauges, a thermometer, tape.", "",
        "## Measure", "",
        "1. Hole diameters: the largest drill shank that enters each hole (`d_measured_mm`).",
        "2. Air volume: tape every hole at its outer rim, fill with water, weigh within a minute, dry (`water_net_mass_g`, `water_temp_c`). "
        "Set `window_throat_in_fill` or `windway_in_fill` if water stood there too.",
        "3. Room temperature (`room_temp_c`). Play for one minute before recording.",
        "4. The 13 notes, A4 (all closed) to F6 (all open): three takes each (`hz` or `cents`) with the manometer pressure of each (`p_pa`). "
        "Start from the breath curve p = 150 Pa · 2^(1.2·n/12), n semitones above A4.",
        "5. Optional, and wanted at least for A4: the break pressure (`p_break_pa`), the pressure just before the note jumps or screeches.",
        "6. Optional: `[[observation]]` rows (fingering, pressure and pitch read at the same moment, with a status: clean, airy, unstable, absent) "
        "and `[[speaking_range]]` rows (onset and break pressure). Leave out what was not seen; do not estimate it.", "",
        "## Fill in", "",
        f"`{name('measurement')}`: every line marked FILL IN. Leave `synthetic = false`: this is a physical record. "
        "Once the file is changed, a later export into this folder is refused, so the record cannot be overwritten.", "",
        "The loader does not accept the file until these are filled: " + ("; ".join(kinds) if kinds else "nothing is missing") + ".", "",
        "## Then", "",
        "```",
        f"python kernel/fit_measurements.py {name('measurement')} --write-constants {body.body_id}_constants.toml",
        "```", "",
        "Build the same body again with that constants file (Blender: **Calibration file** in the build dialog; "
        f"headless: `--calibration {body.body_id}_constants.toml`). The report must say that voicing and layout match exactly.", ""]
    path = Path(folder) / "PRINT-AND-MEASURE.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
