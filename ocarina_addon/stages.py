"""The three stages of the test plan (docs/04-testing-phase.md), each as one call.

    run_stage1(out_dir)                 the voicing stubs V-a, V-af (the plain build), V-b, V-d and the optional
                                        V-a0, V-a35
    run_stage2(out_dir)                 the round-1 bodies: P0 at 65, 80 and 95 cm3, P1, P2 and P4 at 80 cm3,
                                        and two more copies of P0-80 (P0-80-b, P0-80-c)
    run_stage3(out_dir, calibration)    the round-2 bodies, sized from a fitted-constants file, and P0 at 88 cm3

Every stage builds each body with api.build_checked_body: the STL files are written, the body STL is read
back from disk, and every check runs on that file, the cavity-mode step included. A stage builds EVERY body
even when one of them fails. It writes, per body, the STL files, a blank measurement template and a check
report, and one Markdown report for the stage (report.stage_report). The stage is "ok" when no body has an
unexpected failure; expected failures and warnings never make it fail.

The shape bodies since 2026-11-17 (docs/08-stage2-body-library.md, saved by the owner as the plan for now): P1 teardrop,
P2 tailed gourd and P4 seed. P3 is stashed: its preset still builds, but it is in no stage list.
"""
from __future__ import annotations

import datetime
import pathlib
import time
import traceback
from dataclasses import dataclass, field

from . import api, body as body_mod, checks_geo, kernel_bridge, presets as presets_mod, report, stub

PREDICTION_V0_CM3 = 88.0       # never printed in round 1: sized from the fitted model alone (doc 04, Stage 3)
# (preset, V0 cm3, body id, the body it is a copy of or None)
STAGE2_BODIES = [("P0", 65.0, "P0-65", None), ("P0", 80.0, "P0-80", None), ("P0", 95.0, "P0-95", None),
                 ("P1", 80.0, "P1-80", None), ("P2", 80.0, "P2-80", None),
                 ("P4", 80.0, "P4-80", None), ("P0", 80.0, "P0-80-b", "P0-80"), ("P0", 80.0, "P0-80-c", "P0-80")]
# (preset, V0 cm3, printed in round 1)
# Ladder since 2026-11-17: 65 / 80 / 95 cm3; P0 at 88 cm3 is the prediction body (110 and 125 cm3 were dropped).
STAGE3_BODIES = [("P0", 65.0, True), ("P0", 80.0, True), ("P0", 95.0, True),
                 ("P1", 80.0, True), ("P2", 80.0, True), ("P4", 80.0, True), ("P0", PREDICTION_V0_CM3, False)]
STAGE1_STUBS = list(stub.RECIPES)

PLA_DENSITY_G_CM3 = 1.24
# docs/04 "Filament budget": mass of each print in grams (solid 4 mm walls plus about 12 % for supports and a brim)
DOC04_MASS_G = {"P0-65": 77, "P0-80": 84, "P0-88": 88, "P0-95": 91, "P1-80": 91, "P2-80": 97, "P3-80": 91, "P4-80": 99,
                "stub": "50–54"}
# docs/04 "Filament budget": mass of each stage
DOC04_STAGE_BUDGET = {1: "200 g for the four stubs, and about 100 g more for the optional V-a0 and V-a35",
                      2: "707 g", 3: "627 g"}


@dataclass
class Item:
    body_id: str
    kind: str                      # "body" or "stub"
    preset_id: str
    v0_cm3: float
    note: str = ""
    body: object = None            # body.BodyResult when the build worked
    error: str = ""                # the exception text when it did not
    seconds: float = 0.0
    files: dict = field(default_factory=dict)       # name -> path as shown in the report
    extra: dict = field(default_factory=dict)

    @property
    def unexpected(self) -> list:
        return checks_geo.unexpected_failures(self.body) if self.body is not None else []

    @property
    def failed(self) -> bool:
        return self.body is None or bool(self.unexpected)


@dataclass
class Stage:
    number: int
    title: str
    command: str
    out_dir: pathlib.Path
    report_path: pathlib.Path
    items: list
    params: dict
    root: pathlib.Path | None = None
    header: list = field(default_factory=list)      # extra lines for the top of the report
    synthetic: bool = False
    seconds: float = 0.0
    date: str = ""

    @property
    def ok(self) -> bool:
        return not any(it.failed for it in self.items)

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1


def _shown(path, root) -> str:
    p = pathlib.Path(path).resolve()
    if root is not None:
        try:
            return p.relative_to(pathlib.Path(root).resolve()).as_posix()
        except ValueError:
            pass
    return str(p)


def _run(stage: Stage, jobs, body_report_dir, render_root, renders: bool, only=None) -> Stage:
    """jobs: list of (Item, preset, build kwargs, after(item) or None). Builds every job; never raises."""
    t_stage = time.time()
    stage.out_dir = pathlib.Path(stage.out_dir).resolve()
    stage.date = datetime.date.today().isoformat()
    for item, preset, kwargs, after in jobs:
        if only and item.body_id not in only:
            continue
        stage.items.append(item)
        t0 = time.time()
        out = stage.out_dir / item.body_id
        want_renders = renders and not item.extra.get("copy_of")
        render_dir = (pathlib.Path(render_root) / item.body_id) if render_root is not None else out / "renders"
        try:
            b = api.build_checked_body(preset, item.v0_cm3, str(out), params=stage.params, renders=want_renders,
                                       render_dir=str(render_dir), root=stage.root, body_id=item.body_id, **kwargs)
            item.body = b
            item.files = {name: _shown(path, stage.root) for name, path in b.files.items() if not name.startswith("render_")}
            if want_renders:
                item.files["renders"] = _shown(render_dir, stage.root) + "/"
            if after is not None:
                after(item)
            rep_dir = pathlib.Path(body_report_dir) if body_report_dir is not None else out
            md = report.write_body_report(b, rep_dir, time.time() - t0, f"Written by `{stage.command}`.",
                                          json_default=body_mod._json_default)
            item.files["check_report"] = _shown(md, stage.root)
            bad = item.unexpected
            print(f"[stage {stage.number}] {item.body_id}: {'OK' if not bad else 'UNEXPECTED FAILURES: ' + ', '.join(c['name'] for c in bad)}; "
                  f"{len(checks_geo.warnings(b))} warnings; {time.time() - t0:.0f} s", flush=True)
        except Exception as exc:                       # noqa: BLE001 - one body must not stop the stage
            traceback.print_exc()
            item.error = f"{type(exc).__name__}: {exc}"
            print(f"[stage {stage.number}] {item.body_id}: BUILD FAILED: {item.error}", flush=True)
        item.seconds = time.time() - t0
    stage.seconds = time.time() - t_stage
    stage.report_path.parent.mkdir(parents=True, exist_ok=True)
    stage.report_path.write_text(report.stage_report(stage), encoding="utf-8")
    print(f"[stage {stage.number}] report: {stage.report_path}", flush=True)
    print(f"[stage {stage.number}] {'OK: no unexpected failure' if stage.ok else 'FAILED: ' + ', '.join(it.body_id for it in stage.items if it.failed)}"
          f" ({len(stage.items)} bodies, {stage.seconds:.0f} s)", flush=True)
    return stage


def _same_triangles(path_a, path_b) -> bool:
    """Two binary STL files hold the same triangles (the 80-byte header carries the body id and may differ)."""
    with open(path_a, "rb") as fa, open(path_b, "rb") as fb:
        return fa.read()[80:] == fb.read()[80:]


# ---------------------------------------------------------------------------------------------- stage 1

def run_stage1(out_dir, *, report_path=None, body_report_dir=None, render_root=None, renders: bool = True, params=None,
               root=None, only=None, command: str = "ocarina_addon/headless.py -- stage1") -> Stage:
    """Stage 1: the voicing stubs. A stub has the voicing, the wall and no holes."""
    k = kernel_bridge.kernel()
    P = params if params is not None else kernel_bridge.load_params()
    out_dir = pathlib.Path(out_dir)
    preset = presets_mod.get_preset(stub.STUB_PRESET)
    volume = float(preset["stub_volume_cm3"])
    stage = Stage(1, "Stage 1 · Voicing stubs", command, out_dir, pathlib.Path(report_path) if report_path else out_dir / "stage1.md",
                  [], P, root)
    stage.header = [f"A stub is a small egg ({volume:g} cm³ of capped air, preset `{stub.STUB_PRESET}`) with a generated voicing, the "
                    f"{P['hole_rules']['wall_at_holes_mm']:g} mm wall and no holes. Its pitch at a known volume gives η_w·G_w for that voicing. "
                    "A stub with the window of a body has the voicing hash of that body.",
                    "The predicted pitch uses the prior η_w. It is a prediction, not a measurement.",
                    "Every stub has the build of the bodies (the ellipse cut, the neck that stands off the body, the pipe lowered inside it, "
                    "the pocket blend; owner decisions of 2026-11-18), except V-af and V-b. V-af is the same window as V-a with the plain build "
                    "(fan cut, level windway, box stub). The build is part of the hash, so V-af has a hash that no body carries. "
                    "V-a against V-af says what the build is worth and whether it speaks. V-b, the rounded rectangle, has the plain build "
                    "too (the ellipse cut is made for the teardrop), so the shape pair is V-b against V-af."]
    jobs = []
    for sid in STAGE1_STUBS:
        purpose, optional = stub.RECIPES[sid][3], stub.RECIPES[sid][4]
        item = Item(sid, "stub", stub.STUB_PRESET, volume, note=purpose + (" (optional stub of doc 04)" if optional else ""))

        def after(it):
            sz = it.body.sizing
            t = k.measurements.stub_template(sz.voicing, it.body_id, sz.v0_cm3, predicted_hz=sz.predicted_pitch_hz)
            path = out_dir / it.body_id / f"{it.body_id}_measurement.toml"
            k.measurements.write_stub_file(path, t, blank=True)
            it.files["measurement_template"] = _shown(path, root)

        jobs.append((item, preset, dict(kind="stub", sizing_fn=lambda L, sid=sid: stub.stub_sizing(sid, P, volume),
                                        info=dict(stage=1)), after))
    return _run(stage, jobs, body_report_dir, render_root, renders, only)


# ---------------------------------------------------------------------------------------------- stage 2

def run_stage2(out_dir, *, report_path=None, body_report_dir=None, render_root=None, renders: bool = True, params=None,
               root=None, only=None, command: str = "ocarina_addon/headless.py -- stage2") -> Stage:
    """Stage 2: the round-1 bodies, holes cut at the k_hole 0.8 ("print") diameters."""
    k = kernel_bridge.kernel()
    P = params if params is not None else kernel_bridge.load_params()
    out_dir = pathlib.Path(out_dir)
    stage = Stage(2, "Stage 2 · Round 1 bodies", command, out_dir, pathlib.Path(report_path) if report_path else out_dir / "stage2.md",
                  [], P, root)
    stage.header = ["Every body has the full 12 round holes, sized for its own volume and cut at the k_hole = 0.8 (`print`) diameters. "
                    "P0 bodies carry the taped test layout; P1, P2 and P4 carry the hand layout.",
                    "**Read the warnings before printing.** The hole layout of every shape is frozen once Stage 2 is printed "
                    "(doc 04 D10), because the fitted position factors belong to one layout.",
                    "The shape bodies are P1, P2 and P4, the seed (docs/08). P3 is stashed: its preset still builds, but it is not in this list."]
    jobs = []
    for pid, v0, bid, copy_of in STAGE2_BODIES:
        item = Item(bid, "body", pid, v0, note=(f"repeatability copy of {copy_of}: the same geometry (doc 02 A7)" if copy_of else ""),
                    extra=dict(copy_of=copy_of))

        def after(it, pid=pid, copy_of=copy_of):
            t = k.measurements.template_from_sizing(it.body.sizing, it.body_id, shape=pid)
            path = out_dir / it.body_id / f"{it.body_id}_measurement.toml"
            k.measurements.write_measurement_file(path, t, blank=True)
            it.files["measurement_template"] = _shown(path, root)
            if copy_of:
                first = out_dir / copy_of / f"{copy_of}.stl"
                it.extra["same_triangles_as_original"] = first.is_file() and _same_triangles(first, it.body.files["stl"])

        jobs.append((item, pid, dict(info=dict(stage=2)), after))
    return _run(stage, jobs, body_report_dir, render_root, renders, only)


# ---------------------------------------------------------------------------------------------- stage 3

def run_stage3(out_dir, calibration_path, *, report_path=None, body_report_dir=None, render_root=None, renders: bool = False,
               params=None, root=None, only=None, retarget_volume: bool = False,
               command: str = "ocarina_addon/headless.py -- stage3") -> Stage:
    """Stage 3: the round-2 bodies, sized from a fitted-constants file (kernel calibration.py).

    Printed in round 1 (P0 at 65, 80, 95; P1, P2, P4 at 80): the printed window and the printed volume
    are kept (retarget_volume=False is the default; the A4 error that the measured eta_w implies is in the
    report), the round-1 inward tubes are kept, and the holes stay at their round-1 positions (doc 04 D10).
    Only the diameters change. P0 at 88 cm3 was never printed: it is sized from the fitted model alone.
    The holes are drawn at the CAD diameter (design minus the fitted hole offset) and the model is scaled
    by the fitted volume factor.
    """
    k = kernel_bridge.kernel()
    P = params if params is not None else kernel_bridge.load_params()
    out_dir = pathlib.Path(out_dir)
    cal = k.calibration.load_calibration(calibration_path)
    stage = Stage(3, "Stage 3 · Round 2 corrected bodies", command, out_dir,
                  pathlib.Path(report_path) if report_path else out_dir / "stage3.md", [], P, root, synthetic=bool(cal.synthetic))
    stage.header = [
        f"Sized from the fitted-constants file `{_shown(calibration_path, root)}`: k_hole {cal.k_hole:.4f} ({cal.k_hole_source} estimate), "
        f"hole offset {cal.hole_offset_mm:+.3f} mm (printed minus designed), volume factor {cal.volume_factor:.4f} (printed / designed), "
        f"η_w fallback {cal.eta_w_fallback:.4f}; η_w measured for the voicing hashes "
        + ", ".join(f"`{h}` {v['eta_w']:.4f}" for h, v in cal.voicings.items()) + ".",
        "Bodies that were printed in round 1 keep their window, their volume, their inward tubes and their hole positions "
        "(doc 04 D10). Only the hole diameters change. "
        + ("The volume is retargeted so that A4 is on pitch (option `--retarget-volume`)." if retarget_volume else
           "The printed volume is kept (the default), so A4 errs by the amount the measured η_w says; the table gives it."),
        "Each hole is drawn at its CAD diameter (design diameter minus the hole offset), and the model holds V0 divided by the "
        "volume factor, so that the print holds V0.",
        f"P0 at {PREDICTION_V0_CM3:g} cm³ was never printed: its window, tubes and holes come from the fitted model alone (the prediction test of Gate 3).",
        "The per-body check reports of this stage are written beside the STL files (not in git), and no pictures are made unless "
        "`--renders` is given: the result depends on the constants file."]
    names = [h["name"] for h in P["fingering"]["holes"]]
    jobs = []
    for pid, v0, printed in STAGE3_BODIES:
        bid = f"{pid}-{v0:g}-r2"
        round1 = k.sizing.size_body(v0, params=P)
        tubes = list(round1.holes.tubes_mm) if printed else None
        infos = {}

        def sizing_fn(L, pid=pid, v0=v0, tubes=tubes, infos=infos):
            kw = dict(tubes_mm=tubes) if tubes is not None else {}
            sz, info = k.calibration.size_body_from_calibration(cal, v0, shape=pid, retarget_volume=retarget_volume, L_int_mm=L,
                                                                params=P, **kw)
            infos.update(info)
            return sz

        item = Item(bid, "body", pid, v0, note="round 2 of a printed body" if printed else "never printed: sized from the fitted model only",
                    extra=dict(printed_in_round1=printed, round1=round1, calibration_info=infos, names=names))

        def after(it, pid=pid):
            t = k.measurements.template_from_sizing(it.body.sizing, it.body_id, shape=pid, key="fitted")
            path = out_dir / it.body_id / f"{it.body_id}_measurement.toml"
            k.measurements.write_measurement_file(path, t, blank=True)
            it.files["measurement_template"] = _shown(path, root)

        kwargs = dict(hole_key="fitted", sizing_fn=sizing_fn, info=dict(stage=3, synthetic=bool(cal.synthetic)))
        if printed:
            kwargs["layout_rows"] = body_mod.cut_rows(round1, "print")
        jobs.append((item, pid, kwargs, after))
    return _run(stage, jobs, body_report_dir, render_root, renders, only)
