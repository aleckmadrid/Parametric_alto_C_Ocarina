"""Measurement input format (C2). One TOML file per printed body, filled in by hand.

The generator writes a template with the design numbers already filled in (hash, window area,
chimney lengths, design diameters, target pitches). You type only what you measure:

    [fill]    water_net_mass_g, water_temp_c  (and two yes/no lines about the window and windway)
    [conditions] room_temp_c
    [[hole]]  d_measured_mm for each hole
    [[note]]  hz (or cents) and p_pa, three takes for each of the 13 fingerings; optional p_break_pa
              (the pressure at which the note breaks: the top of its speaking range). Wanted at least
              for the lowest note: it is Heuer's window check ("blow that low note away", Videos #2, #4, #8).

Optional, the observations extension (observations_version = 1): paired readings, for a pressure response per
fingering (fitter.pressure_response). They do not replace [[note]], which the fit reads.
    [session]            instrument, specimen, method, warm_up, and internal_temp_c only if it was measured
    [[observation]]      fingering, p_pa and hz read at the same moment, status (clean, airy, unstable, absent:
                         an absent note has no hz), take, order, sweep (up, down), open_holes for a cross-fingering
    [[speaking_range]]   fingering, onset_pa, break_pa (leave out what was not seen)

Volume convention. The kernel's V0 is the capped air: every hole chimney is inside, the window throat
and the windway are not. Tape every hole at its outer rim before the water fill. If water also fills the
window throat or the windway, say so in [fill] and the loader subtracts their volume (given in the file).

Synthetic files carry `synthetic = true` and a banner comment. Never put invented data in a file
without that flag.

Stage 1 voicing stubs have a file format of their own (schema ocarina-stub-measurement-v1): the stub id,
the voicing hash, the water fill, the room temperature, three takes of the stub's one pitch and the
optional break pressure.
See stub_template(), write_stub_file() and load_stub() at the end of this module.
"""
from __future__ import annotations

import math
import pathlib
import tomllib
from dataclasses import dataclass, field

import ocarina_kernel as ok

SCHEMA = "ocarina-measurement-v1"
MM = 1e-3
CM3 = 1e-6

NOTE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


class MeasurementIncomplete(ValueError):
    """The file is valid TOML but not filled in. `.missing` lists what is empty."""

    def __init__(self, missing):
        self.missing = list(missing)
        super().__init__("measurement file is incomplete:\n  - " + "\n  - ".join(self.missing))


def note_midi(name: str) -> int:
    """'A4' -> 69, 'F6' -> 89. Sharps: 'C#5'."""
    letter, rest = name[0].upper(), name[1:]
    semis = NOTE_OFFSETS[letter]
    if rest.startswith("#"):
        semis += 1
        rest = rest[1:]
    elif rest.startswith("b"):
        semis -= 1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + semis


def note_hz(name: str, a4: float = 440.0) -> float:
    return ok.midi_f(note_midi(name), a4)


def water_density_kg_m3(T_c: float) -> float:
    """Density of air-free water (Tanaka et al. 1999). Good to 0.01 % between 0 and 40 degC."""
    return 999.974950 * (1.0 - (T_c - 3.983035) ** 2 * (T_c + 301.797) / (522528.9 * (T_c + 69.34881)))


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------

@dataclass
class HoleMeas:
    name: str
    opens: str
    chimney_m: float             # wall + inward tube, from the design (measure it if you can)
    d_design_m: float            # diameter drawn in CAD
    d_measured_m: float | None   # measured with drill-bit shanks or calipers


@dataclass
class NoteMeas:
    name: str
    target_hz: float
    takes_cents: list            # each take as cents against target_hz
    pressures_pa: list
    p_break_pa: float | None = None   # pressure at which the note breaks (top of the speaking range), optional

    @property
    def n_takes(self) -> int:
        return len(self.takes_cents)

    @property
    def cents_mean(self) -> float:
        return sum(self.takes_cents) / len(self.takes_cents)

    @property
    def f_hz(self) -> float:
        """Mean pitch of the takes (mean in cents = geometric mean in Hz)."""
        return self.target_hz * 2.0 ** (self.cents_mean / 1200.0)

    @property
    def cents_sem(self) -> float | None:
        """Standard error of the mean in cents, or None for a single take."""
        n = len(self.takes_cents)
        if n < 2:
            return None
        m = self.cents_mean
        sd = math.sqrt(sum((x - m) ** 2 for x in self.takes_cents) / (n - 1))
        return sd / math.sqrt(n)


SPEAKING = ("clean", "airy", "unstable", "absent")
OBSERVATIONS_VERSION = 1


@dataclass
class Observation:
    """One paired reading of the observations extension: the pitch of one fingering and the blowing pressure read at the
    same moment. A reading without a pitch (the note did not speak, or was not read) keeps hz None: nothing is invented."""
    fingering: str                    # the chart's note name ("C5"), or a name of your own for a cross-fingering
    p_pa: float | None = None
    hz: float | None = None
    status: str = "clean"             # SPEAKING: clean, airy, unstable or absent (no note at all)
    take: str = ""                    # which repeat
    order: int = 0                    # position in the session: warm-up drift, the run of a sweep
    sweep: str = ""                   # "up", "down" or "" (a single reading)
    open_holes: list = field(default_factory=list)   # the open holes when not the chart's fingering (a cross-fingering)
    target_hz: float | None = None    # default: the [[note]] of that name, else equal temperament at A4 = 440 Hz
    audio: str = ""                   # a recording or spectrum kept with the file, if any


@dataclass
class BodyMeasurement:
    id: str
    shape: str
    voicing_hash: str
    target_v0_cm3: float
    synthetic: bool
    window_area_mm2: float
    wall_at_window_mm: float
    v0_m3: float                 # measured capped air volume, after the window/windway corrections
    room_temp_c: float
    holes: list
    notes: list
    date: str = ""
    comment: str = ""
    water_net_mass_g: float = 0.0
    water_temp_c: float = 20.0
    source: str = ""
    windway_cm3: float = 0.0           # windway volume from the voicing numbers (subtracted if water filled it)
    # What a fitted constant of this body applies to beyond its voicing hash (the add-on's presets.calibration_context):
    # voicing_context, layout (signatures) and window_throat (the model's convention). {} in files written without it.
    context: dict = field(default_factory=dict)
    # The observations extension (optional; empty in older files): [session], [[observation]] in file order,
    # [[speaking_range]] as fingering -> (onset_pa, break_pa) with None for what was not seen.
    session: dict = field(default_factory=dict)
    observations: list = field(default_factory=list)
    speaking_range: dict = field(default_factory=dict)

    @property
    def v0_cm3(self) -> float:
        return self.v0_m3 / CM3

    def internal_temp_c(self, params: dict | None = None) -> float:
        t = (params or {}).get("temperature", {})
        return ok.internal_air_temp_c(self.room_temp_c, t.get("design_internal_c", 27.0),
                                      t.get("reference_room_c", 22.0), t.get("room_coupling", 0.31))

    def c_m_s(self, params: dict | None = None) -> float:
        return ok.c_air(self.internal_temp_c(params))

    def window_G_w(self) -> float:
        """Window conductance in metres under k_window."""
        return ok.conductance(self.window_area_mm2 * MM * MM, self.wall_at_window_mm * MM, ok.K_WINDOW)


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _observation(o: dict, i: int) -> Observation:
    where = f"[[observation]] {i + 1} ({o.get('fingering', '?')})"
    status, sweep = str(o.get("status", "clean")), str(o.get("sweep", ""))
    if not o.get("fingering"):
        raise ValueError(f"{where}: fingering is missing")
    if status not in SPEAKING:
        raise ValueError(f"{where}: status {status!r} is not one of {', '.join(SPEAKING)}")
    if sweep not in ("", "up", "down"):
        raise ValueError(f"{where}: sweep is up, down or left out")
    hz = float(o["hz"]) if _num(o.get("hz")) else None
    if status == "absent" and hz is not None:
        raise ValueError(f"{where}: a fingering that did not speak has no frequency")
    return Observation(fingering=str(o["fingering"]), p_pa=float(o["p_pa"]) if _num(o.get("p_pa")) else None, hz=hz,
                       status=status, take=str(o.get("take", "")), order=int(o.get("order", i)), sweep=sweep,
                       open_holes=[str(x) for x in o.get("open_holes", [])],
                       target_hz=float(o["target_hz"]) if _num(o.get("target_hz")) else None, audio=str(o.get("audio", "")))


def parse_measurement(data: dict, source: str = "", allow_incomplete: bool = False) -> BodyMeasurement:
    """Build a BodyMeasurement from a parsed TOML dict. Raises MeasurementIncomplete if values are empty."""
    missing = []
    if data.get("schema") != SCHEMA:
        raise ValueError(f"unknown schema {data.get('schema')!r}; expected {SCHEMA!r}")
    body = data.get("body", {})
    vo = data.get("voicing", {})
    fill = data.get("fill", {})
    cond = data.get("conditions", {})

    for key in ("id", "shape", "voicing_hash"):
        if not body.get(key):
            missing.append(f"[body] {key}")
    if not _num(body.get("target_v0_cm3")):
        missing.append("[body] target_v0_cm3")
    for key in ("window_area_mm2", "wall_at_window_mm"):
        if not _num(vo.get(key)):
            missing.append(f"[voicing] {key}")

    # water fill
    v0_m3 = None
    mass, tw = fill.get("water_net_mass_g"), fill.get("water_temp_c", 20.0)
    if not _num(mass) or mass <= 0:
        missing.append("[fill] water_net_mass_g")
    else:
        v = mass * 1e-3 / water_density_kg_m3(tw if _num(tw) else 20.0)
        if fill.get("window_throat_in_fill", False):
            v -= float(fill.get("window_throat_cm3", 0.0)) * CM3
        if fill.get("windway_in_fill", False):
            ww = fill.get("windway_cm3")
            if not _num(ww) or ww <= 0:
                missing.append("[fill] windway_cm3 (windway_in_fill is true, so the windway volume must be given)")
            else:
                v -= float(ww) * CM3
        v0_m3 = v
    if not _num(cond.get("room_temp_c")):
        missing.append("[conditions] room_temp_c")

    holes = []
    for i, h in enumerate(data.get("hole", [])):
        d_meas = h.get("d_measured_mm")
        if not _num(d_meas) or d_meas <= 0:
            missing.append(f"[[hole]] {h.get('name', i)}: d_measured_mm")
            d_meas_m = None
        else:
            d_meas_m = d_meas * MM
        holes.append(HoleMeas(h["name"], h.get("opens", ""), float(h["chimney_mm"]) * MM,
                              float(h["d_design_mm"]) * MM, d_meas_m))
    if not holes:
        missing.append("[[hole]] entries")

    notes = []
    for i, n in enumerate(data.get("note", [])):
        name = n["name"]
        target = float(n["target_hz"]) if _num(n.get("target_hz")) else note_hz(name)
        hz, cents = list(n.get("hz", [])), list(n.get("cents", []))
        if hz and cents:
            raise ValueError(f"note {name}: fill either hz or cents, not both")
        if hz:
            takes = [ok.cents(float(x), target) for x in hz]
        else:
            takes = [float(x) for x in cents]
        if not takes:
            missing.append(f"[[note]] {name}: hz (or cents), 3 takes")
        elif len(takes) < 3:
            missing.append(f"[[note]] {name}: {len(takes)} take(s), 3 wanted")
        p = [float(x) for x in n.get("p_pa", [])]
        if not p:
            missing.append(f"[[note]] {name}: p_pa")
        pb = n.get("p_break_pa")                      # optional: never in the missing list
        notes.append(NoteMeas(name, target, takes, p, float(pb) if _num(pb) else None))
    if not notes:
        missing.append("[[note]] entries")

    if data.get("observation") and data.get("observations_version") != OBSERVATIONS_VERSION:
        raise ValueError(f"[[observation]] needs observations_version = {OBSERVATIONS_VERSION} at the top of the file")
    observations = [_observation(o, i) for i, o in enumerate(data.get("observation", []))]
    session = dict(data.get("session", {}))
    if "internal_temp_c" in session and not _num(session["internal_temp_c"]):
        raise ValueError("[session] internal_temp_c is a measured temperature: a number, or leave it out")
    speaking = {str(r["fingering"]): (float(r["onset_pa"]) if _num(r.get("onset_pa")) else None,
                                      float(r["break_pa"]) if _num(r.get("break_pa")) else None)
                for r in data.get("speaking_range", [])}

    if missing and not allow_incomplete:
        raise MeasurementIncomplete(missing)
    return BodyMeasurement(
        id=body.get("id", ""), shape=body.get("shape", ""), voicing_hash=body.get("voicing_hash", ""),
        target_v0_cm3=float(body.get("target_v0_cm3", 0.0)), synthetic=bool(data.get("synthetic", False)),
        window_area_mm2=float(vo.get("window_area_mm2", 0.0)), wall_at_window_mm=float(vo.get("wall_at_window_mm", 0.0)),
        v0_m3=v0_m3 if v0_m3 is not None else 0.0, room_temp_c=float(cond.get("room_temp_c", 0.0)), holes=holes,
        notes=notes, date=str(body.get("date", "")), comment=str(body.get("comment", "")),
        water_net_mass_g=float(mass) if _num(mass) else 0.0, water_temp_c=float(tw) if _num(tw) else 20.0,
        source=source, windway_cm3=float(fill.get("windway_cm3", 0.0)) if _num(fill.get("windway_cm3", 0.0)) else 0.0,
        context={str(k): str(v) for k, v in data.get("context", {}).items()},
        session=session, observations=observations, speaking_range=speaking)


def load_measurement(path, allow_incomplete: bool = False) -> BodyMeasurement:
    path = pathlib.Path(path)
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    return parse_measurement(data, str(path), allow_incomplete)


# --------------------------------------------------------------------------
# Writing (the standard library reads TOML but cannot write it)
# --------------------------------------------------------------------------

def toml_value(x) -> str:
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        if not math.isfinite(x):
            raise ValueError("cannot write a non-finite number to TOML")
        return repr(x)
    if isinstance(x, str):
        esc = x.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")
        return f'"{esc}"'
    if isinstance(x, (list, tuple)):
        return "[" + ", ".join(toml_value(v) for v in x) + "]"
    raise TypeError(f"cannot write {type(x).__name__} to TOML")


def toml_key(k: str) -> str:
    """Bare key when possible, quoted otherwise (hash-keyed tables, names with dots or spaces)."""
    ok_chars = all(ch.isalnum() or ch in "-_" for ch in k) and k != ""
    return k if ok_chars else toml_value(k)


def _comment(text: str) -> list:
    return ["# " + line if line else "#" for line in text.splitlines()]


SYNTHETIC_BANNER = ("SYNTHETIC DATA. Generated by kernel/synthetic.py from invented truth values.\n"
                    "Nothing in this file was measured on a printed body. Do not use it as calibration.")


def write_measurement_file(path, m: BodyMeasurement, *, blank: bool = False, takes_hz: bool = True,
                           notes_in_file: str = "") -> str:
    """Write a measurement file. blank=True writes the template: design numbers filled in, measured
    values empty. Returns the text."""
    out = []
    if m.synthetic:
        out += _comment(SYNTHETIC_BANNER) + [""]
    if blank:
        out += _comment("Measurement file for one printed body (docs/04, Stage 2). Fill in the values marked FILL IN.\n"
                        "Everything else was written by the generator from the design. One file per body.\n"
                        "Tape every hole at its outer rim before the water fill. Play 1 minute before recording.") + [""]
    out += [f"schema = {toml_value(SCHEMA)}", f"synthetic = {toml_value(m.synthetic)}"]
    out += [f"observations_version = {OBSERVATIONS_VERSION}", ""] if m.observations else [""]
    out += ["[body]", f"id = {toml_value(m.id)}", f"shape = {toml_value(m.shape)}  # bodies of one shape share position factors",
            f"voicing_hash = {toml_value(m.voicing_hash)}", f"target_v0_cm3 = {toml_value(m.target_v0_cm3)}",
            f"date = {toml_value(m.date)}", f"comment = {toml_value(m.comment)}", ""]
    out += ["[voicing]  # from the sizing report; do not change",
            f"window_area_mm2 = {toml_value(m.window_area_mm2)}", f"wall_at_window_mm = {toml_value(m.wall_at_window_mm)}", ""]
    if m.context:
        out += ["[context]  # what the fitted constants of this body apply to beyond the voicing hash; do not change"]
        out += [f"{toml_key(k)} = {toml_value(v)}" for k, v in sorted(m.context.items())] + [""]
    throat = m.window_area_mm2 * m.wall_at_window_mm * 1e-3     # cm3: area mm2 * wall mm = mm3 -> cm3
    out += ["[fill]  # water fill with every hole taped at its outer rim"]
    if blank:
        out += ["# water_net_mass_g =    # FILL IN: wet mass minus dry mass of the body, in grams",
                "# water_temp_c = 20.0  # FILL IN: water temperature, degC"]
    else:
        out += [f"water_net_mass_g = {toml_value(m.water_net_mass_g)}", f"water_temp_c = {toml_value(m.water_temp_c)}"]
    out += ["window_throat_in_fill = false  # set true if water also filled the window throat",
            f"window_throat_cm3 = {toml_value(round(throat, 4))}  # area x wall, subtracted only if the line above is true",
            "windway_in_fill = false         # set true if water also filled the windway",
            f"windway_cm3 = {toml_value(round(m.windway_cm3, 4))}  # windway volume from the voicing, subtracted only if the line above is true", ""]
    out += ["[conditions]"]
    out += ["# room_temp_c =   # FILL IN"] if blank else [f"room_temp_c = {toml_value(m.room_temp_c)}"]
    out += [""]
    for h in m.holes:
        out += ["[[hole]]", f"name = {toml_value(h.name)}", f"opens = {toml_value(h.opens)}",
                f"chimney_mm = {toml_value(round(h.chimney_m / MM, 6))}  # wall + inward tube",
                f"d_design_mm = {toml_value(round(h.d_design_m / MM, 6))}  # drawn in CAD"]
        if blank or h.d_measured_m is None:
            out += ["# d_measured_mm =   # FILL IN: measured diameter in mm"]
        else:
            out += [f"d_measured_mm = {toml_value(h.d_measured_m / MM)}"]
        out += [""]
    out += ["# Notes in fingering order, A4 (all closed) to F6 (all open). Three takes each.",
            "# Fill hz = [..] with the tuner frequency of each take, or cents = [..] with the tuner's cents offset from target_hz.",
            "# p_pa = [..] is the manometer pressure of each take in Pa. Fill hz OR cents, not both.",
            "# p_break_pa = .. (optional) is the pressure at which the note breaks: blow harder until it jumps or",
            "# screeches, read the manometer just before. Wanted at least for the lowest note (Heuer's window check).", ""]
    for i, n in enumerate(m.notes):
        out += ["[[note]]", f"name = {toml_value(n.name)}", f"target_hz = {toml_value(n.target_hz)}"]
        if blank or not n.takes_cents:
            out += ["hz = []  # FILL IN", "p_pa = []  # FILL IN"]
        else:
            if takes_hz:
                out += [f"hz = {toml_value([n.target_hz * 2.0 ** (c / 1200.0) for c in n.takes_cents])}"]
            else:
                out += [f"cents = {toml_value(n.takes_cents)}"]
            out += [f"p_pa = {toml_value(n.pressures_pa)}"]
        if n.p_break_pa is not None:
            out += [f"p_break_pa = {toml_value(n.p_break_pa)}"]
        elif blank:
            out += ["# p_break_pa =   # FILL IN: break pressure of the lowest note, Pa" if i == 0 else "# p_break_pa =   # optional"]
        out += [""]
    out += _observations_toml(m, blank)
    text = "\n".join(out)
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(text, encoding="utf-8")
    return text


def _observations_toml(m: BodyMeasurement, blank: bool) -> list:
    """The observations extension, in the order of the record (the order of the readings is data)."""
    tv, out = toml_value, []
    if blank and not m.observations:
        out += _comment("Optional, paired readings for a pressure response per fingering (they do not replace [[note]]).\n"
                        "Put observations_version = 1 under `synthetic` at the top, then one [[observation]] per reading:\n"
                        "fingering, p_pa and hz read at the same moment; status clean, airy, unstable or absent (absent: no hz);\n"
                        "take, order (1, 2, 3 ... through the session) and sweep (up or down) when you sweep the pressure.\n"
                        "[session] instrument, specimen, method, warm_up; internal_temp_c only if you measured it.\n"
                        "[[speaking_range]] fingering, onset_pa, break_pa: leave out what you did not see.") + [""]
    if m.session:
        out += ["[session]  # instrument, specimen, method, warm_up; internal_temp_c only if it was measured"]
        out += [f"{toml_key(k)} = {tv(v)}" for k, v in m.session.items()] + [""]
    for o in m.observations:
        out += ["[[observation]]", f"fingering = {tv(o.fingering)}"]
        out += [f"{k} = {tv(getattr(o, k))}" for k in ("p_pa", "hz", "target_hz") if getattr(o, k) is not None]
        out += [f"status = {tv(o.status)}", f"take = {tv(o.take)}", f"order = {tv(o.order)}", f"sweep = {tv(o.sweep)}"]
        out += ([f"open_holes = {tv(o.open_holes)}"] if o.open_holes else []) + ([f"audio = {tv(o.audio)}"] if o.audio else []) + [""]
    for name, (onset, brk) in m.speaking_range.items():
        out += ["[[speaking_range]]", f"fingering = {tv(name)}"]
        out += ([f"onset_pa = {tv(onset)}"] if onset is not None else []) + ([f"break_pa = {tv(brk)}"] if brk is not None else []) + [""]
    return out


def template_from_sizing(body_sizing, body_id: str, shape: str = "P0", key: str = "print", date: str = "",
                         context: dict | None = None):
    """Build a blank BodyMeasurement from a sizing.BodySizing. Design numbers filled in, measurements empty.
    context: the calibration context of the build (the add-on's presets.calibration_context), kept in the file."""
    rows = body_sizing.holes.solutions[key]
    holes = [HoleMeas(r.name, r.opens, r.chimney_mm * MM, body_sizing.cad_diameters_mm[key][i] * MM, None)
             for i, r in enumerate(rows)]
    notes = [NoteMeas(n, f, [], []) for n, f in zip(body_sizing.notes, body_sizing.f_targets_hz)]
    v = body_sizing.voicing
    windway_cm3 = (v.windway_length_mm * v.windway_width_mm * 0.5 * (v.windway_exit_height_mm + v.windway_inlet_height_mm)) / 1000.0
    return BodyMeasurement(id=body_id, shape=shape, voicing_hash=v.version_hash, windway_cm3=windway_cm3,
                           target_v0_cm3=body_sizing.v0_cm3, synthetic=False, window_area_mm2=v.window_area_mm2,
                           wall_at_window_mm=v.wall_at_window_mm, v0_m3=0.0, room_temp_c=0.0, holes=holes,
                           notes=notes, date=date, context=dict(context or {}))


# --------------------------------------------------------------------------
# Stage 1 voicing stubs: a small chamber with a voicing and no holes (docs/04, Stage 1)
# --------------------------------------------------------------------------

STUB_SCHEMA = "ocarina-stub-measurement-v1"


@dataclass
class StubMeasurement:
    """One printed voicing stub. Its pitch at a known volume gives eta_w * G_w for the voicing
    (fitter.eta_w_from_stub). The volume convention is that of a body: capped air, the window throat and
    the windway are not part of it."""
    id: str
    voicing_hash: str
    target_volume_cm3: float
    synthetic: bool
    window_area_mm2: float
    wall_at_window_mm: float
    v0_m3: float                         # measured capped volume, after the window/windway corrections
    room_temp_c: float
    takes_hz: list                       # measured pitch of each take
    pressures_pa: list = field(default_factory=list)
    p_break_pa: float | None = None      # break pressure: the manometer reading just before the note jumps or screeches (optional)
    predicted_hz: float = 0.0            # design prediction with the prior eta_w; not a measurement
    windway_cm3: float = 0.0
    water_net_mass_g: float = 0.0
    water_temp_c: float = 20.0
    speaks_cleanly: bool | None = None           # Gate 1 of docs/04, typed in by hand
    overblows_a_semitone_cleanly: bool | None = None
    date: str = ""
    comment: str = ""
    source: str = ""

    @property
    def v0_cm3(self) -> float:
        return self.v0_m3 / CM3

    @property
    def f_hz(self) -> float:
        """Mean pitch of the takes (geometric mean, as for the notes of a body)."""
        if not self.takes_hz:
            raise ValueError(f"stub {self.id}: no pitch takes")
        return math.exp(sum(math.log(x) for x in self.takes_hz) / len(self.takes_hz))

    @property
    def spread_cents(self) -> float:
        """Largest minus smallest take, in cents."""
        return ok.cents(max(self.takes_hz), min(self.takes_hz)) if len(self.takes_hz) > 1 else 0.0


def stub_template(voicing, stub_id: str, target_volume_cm3: float, predicted_hz: float = 0.0, date: str = "") -> StubMeasurement:
    """A blank StubMeasurement for a generated stub: design numbers filled in, measurements empty.
    `voicing` is a voicing.Voicing record."""
    v = voicing
    windway_cm3 = (v.windway_length_mm * v.windway_width_mm * 0.5 * (v.windway_exit_height_mm + v.windway_inlet_height_mm)) / 1000.0
    return StubMeasurement(id=stub_id, voicing_hash=v.version_hash, target_volume_cm3=float(target_volume_cm3), synthetic=False,
                           window_area_mm2=v.window_area_mm2, wall_at_window_mm=v.wall_at_window_mm, v0_m3=0.0, room_temp_c=0.0,
                           takes_hz=[], predicted_hz=float(predicted_hz), windway_cm3=windway_cm3, date=date)


def write_stub_file(path, m: StubMeasurement, *, blank: bool = False) -> str:
    """Write a stub measurement file. blank=True writes the template: design numbers filled in, measured
    values empty. Returns the text."""
    out = []
    if m.synthetic:
        out += _comment(SYNTHETIC_BANNER) + [""]
    if blank:
        out += _comment("Measurement file for one printed voicing stub (docs/04, Stage 1). Fill in the values marked FILL IN.\n"
                        "Everything else was written by the generator from the design. One file per stub.\n"
                        "A stub has no holes. Close the window with tape at its inner edge, or fill only up to the window,\n"
                        "before the water fill. Play 1 minute before recording.") + [""]
    out += [f"schema = {toml_value(STUB_SCHEMA)}", f"synthetic = {toml_value(m.synthetic)}", ""]
    out += ["[stub]", f"id = {toml_value(m.id)}", f"voicing_hash = {toml_value(m.voicing_hash)}",
            f"target_volume_cm3 = {toml_value(m.target_volume_cm3)}",
            f"predicted_hz = {toml_value(round(m.predicted_hz, 3))}  # design prediction with the prior eta_w; not a measurement",
            f"date = {toml_value(m.date)}", f"comment = {toml_value(m.comment)}", ""]
    out += ["[voicing]  # from the sizing report; do not change",
            f"window_area_mm2 = {toml_value(m.window_area_mm2)}", f"wall_at_window_mm = {toml_value(m.wall_at_window_mm)}", ""]
    throat = m.window_area_mm2 * m.wall_at_window_mm * 1e-3
    out += ["[fill]  # water fill of the chamber"]
    if blank:
        out += ["# water_net_mass_g =    # FILL IN: wet mass minus dry mass of the stub, in grams",
                "# water_temp_c = 20.0  # FILL IN: water temperature, degC"]
    else:
        out += [f"water_net_mass_g = {toml_value(m.water_net_mass_g)}", f"water_temp_c = {toml_value(m.water_temp_c)}"]
    out += ["window_throat_in_fill = false  # set true if water also filled the window throat",
            f"window_throat_cm3 = {toml_value(round(throat, 4))}  # area x wall, subtracted only if the line above is true",
            "windway_in_fill = false         # set true if water also filled the windway",
            f"windway_cm3 = {toml_value(round(m.windway_cm3, 4))}  # windway volume from the voicing, subtracted only if the line above is true", ""]
    out += ["[conditions]"]
    out += ["# room_temp_c =   # FILL IN"] if blank else [f"room_temp_c = {toml_value(m.room_temp_c)}"]
    out += ["", "[pitch]  # the one note of the stub, three takes",
            "# hz = [..] is the tuner frequency of each take. p_pa = [..] is the manometer pressure of each take in Pa."]
    if blank or not m.takes_hz:
        out += ["hz = []  # FILL IN", "p_pa = []  # FILL IN"]
    else:
        out += [f"hz = {toml_value([float(x) for x in m.takes_hz])}", f"p_pa = {toml_value([float(x) for x in m.pressures_pa])}"]
    out += ["# p_break_pa is the break pressure (docs/04, Stage 1): blow harder until the note jumps or screeches and read the",
            "# manometer just before. Optional, but wanted on every stub: it compares the voicings on one number."]
    out += ["# p_break_pa =   # FILL IN: break pressure, Pa"] if (blank or m.p_break_pa is None) else [f"p_break_pa = {toml_value(m.p_break_pa)}"]
    out += ["", "[gate1]  # docs/04, Gate 1. Type true or false."]
    for key, value in (("speaks_cleanly", m.speaks_cleanly), ("overblows_a_semitone_cleanly", m.overblows_a_semitone_cleanly)):
        out += [f"# {key} =   # FILL IN: true or false"] if (blank or value is None) else [f"{key} = {toml_value(bool(value))}"]
    out += [""]
    text = "\n".join(out)
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(text, encoding="utf-8")
    return text


def parse_stub(data: dict, source: str = "", allow_incomplete: bool = False) -> StubMeasurement:
    """Build a StubMeasurement from a parsed TOML dict. Raises MeasurementIncomplete if values are empty.
    The two Gate 1 answers are optional."""
    if data.get("schema") != STUB_SCHEMA:
        raise ValueError(f"unknown schema {data.get('schema')!r}; expected {STUB_SCHEMA!r}")
    missing = []
    stub, vo, fill = data.get("stub", {}), data.get("voicing", {}), data.get("fill", {})
    cond, pitch, gate = data.get("conditions", {}), data.get("pitch", {}), data.get("gate1", {})
    for key in ("id", "voicing_hash"):
        if not stub.get(key):
            missing.append(f"[stub] {key}")
    if not _num(stub.get("target_volume_cm3")):
        missing.append("[stub] target_volume_cm3")
    for key in ("window_area_mm2", "wall_at_window_mm"):
        if not _num(vo.get(key)):
            missing.append(f"[voicing] {key}")
    v0_m3 = None
    mass, tw = fill.get("water_net_mass_g"), fill.get("water_temp_c", 20.0)
    if not _num(mass) or mass <= 0:
        missing.append("[fill] water_net_mass_g")
    else:
        v = mass * 1e-3 / water_density_kg_m3(tw if _num(tw) else 20.0)
        if fill.get("window_throat_in_fill", False):
            v -= float(fill.get("window_throat_cm3", 0.0)) * CM3
        if fill.get("windway_in_fill", False):
            ww = fill.get("windway_cm3")
            if not _num(ww) or ww <= 0:
                missing.append("[fill] windway_cm3 (windway_in_fill is true, so the windway volume must be given)")
            else:
                v -= float(ww) * CM3
        v0_m3 = v
    if not _num(cond.get("room_temp_c")):
        missing.append("[conditions] room_temp_c")
    hz = [float(x) for x in pitch.get("hz", [])]
    if not hz:
        missing.append("[pitch] hz, 3 takes")
    elif len(hz) < 3:
        missing.append(f"[pitch] hz: {len(hz)} take(s), 3 wanted")
    if any(x <= 0 for x in hz):
        raise ValueError("[pitch] hz: a frequency must be above zero")
    pb = pitch.get("p_break_pa")                     # optional: never in the missing list
    if pb is not None and (not _num(pb) or pb <= 0):
        raise ValueError("[pitch] p_break_pa: the break pressure must be a number above zero")
    if missing and not allow_incomplete:
        raise MeasurementIncomplete(missing)
    yes_no = lambda x: bool(x) if isinstance(x, bool) else None
    return StubMeasurement(
        id=str(stub.get("id", "")), voicing_hash=str(stub.get("voicing_hash", "")),
        target_volume_cm3=float(stub.get("target_volume_cm3", 0.0)) if _num(stub.get("target_volume_cm3")) else 0.0,
        synthetic=bool(data.get("synthetic", False)), window_area_mm2=float(vo.get("window_area_mm2", 0.0)),
        wall_at_window_mm=float(vo.get("wall_at_window_mm", 0.0)), v0_m3=v0_m3 if v0_m3 is not None else 0.0,
        room_temp_c=float(cond.get("room_temp_c", 0.0)) if _num(cond.get("room_temp_c")) else 0.0, takes_hz=hz,
        pressures_pa=[float(x) for x in pitch.get("p_pa", [])], p_break_pa=float(pb) if pb is not None else None,
        predicted_hz=float(stub.get("predicted_hz", 0.0)) if _num(stub.get("predicted_hz")) else 0.0,
        windway_cm3=float(fill.get("windway_cm3", 0.0)) if _num(fill.get("windway_cm3", 0.0)) else 0.0,
        water_net_mass_g=float(mass) if _num(mass) else 0.0, water_temp_c=float(tw) if _num(tw) else 20.0,
        speaks_cleanly=yes_no(gate.get("speaks_cleanly")), overblows_a_semitone_cleanly=yes_no(gate.get("overblows_a_semitone_cleanly")),
        date=str(stub.get("date", "")), comment=str(stub.get("comment", "")), source=source)


def load_stub(path, allow_incomplete: bool = False) -> StubMeasurement:
    path = pathlib.Path(path)
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    return parse_stub(data, str(path), allow_incomplete)
