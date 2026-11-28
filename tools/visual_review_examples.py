"""The examples of the annotated inspection (docs/10, steps 1 and 2): the selected P4-bowl and the body it replaced.

    blender -b --factory-startup --python tools/visual_review_examples.py -- [<output folder>]

prior     P4-bowl without pocket_back_margin_mm: the thin floor under the windway's exit corners
current   P4-bowl as selected, compared with prior
Default output: addon_out/visual-review-step12/. Geometry only; nothing here is tuning evidence.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ocarina_addon import api, checks_geo, presets  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = pathlib.Path(argv[0]) if argv else ROOT / "addon_out" / "visual-review-step12"
selected = presets.get_preset("P4-bowl")
before = {k: x for k, x in selected.items() if k != "pocket_back_margin_mm"}
prior = api.export_specimen(before, 80.0, out / "prior", body_id="P4-bowl-prior-floor-defect", verbose=False)
current = api.export_specimen(selected, 80.0, out / "current", body_id="P4-bowl-80-review", verbose=False,
                              previous_inspection=prior.files["inspection_snapshot"])
for body in (prior, current):
    wide = sum(r["wide_thin_plate_probes"] for r in body.measurements["bowl_local"]["regions"].values())
    print(f"{body.body_id}: unexpected {[c['name'] for c in checks_geo.unexpected_failures(body)]}, "
          f"expected {[c['name'] for c in body.checks if c.get('expected')]}, wide thin-plate probes {wide}")
