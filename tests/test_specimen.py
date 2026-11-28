"""Specimen provenance and non-destructive export, without Blender."""
import json
import pathlib
import tempfile
import tomllib
import types
import unittest

from ocarina_addon import kernel_bridge, presets, specimen

K = kernel_bridge.kernel()


class TestSpecimen(unittest.TestCase):
    def test_template_preserves_edited_identity_and_fitted_holes(self):
        preset = presets.get_preset('P4')
        identity = dict(voicing='window-edit', layout='rim-edit')
        ctx = presets.calibration_context(preset, True, identity)
        cal = K.calibration.load_calibration(pathlib.Path(__file__).resolve().parents[1] / 'calibration/synthetic-fitted-constants.toml')
        sz = presets.calibrated_sizing_fn(cal, preset, 80, kernel_bridge.load_params(), edited_shell=True, identity=identity)(None)
        body = types.SimpleNamespace(body_id='test-edit', preset_id='P4', sizing=sz,
            info=dict(shell_edit=dict(calibration_identity=identity), synthetic=True, calibration_context=ctx),
            params=dict(hole_key='fitted'), v0_cm3=80., air_capped_cm3=80.,
            layout=types.SimpleNamespace(holes=[]), files={'stl': 'test-edit.stl'}, checks=[], voicing_hash=sz.voicing.version_hash)
        with tempfile.TemporaryDirectory() as tmp:
            record = specimen.write_bundle(body, preset, tmp)
            t = tomllib.loads(pathlib.Path(body.files['measurement']).read_text())
            self.assertEqual(t['context'], ctx)
            self.assertFalse(t['synthetic']) # a blank future physical record is not invented data
            self.assertTrue(record['design_uses_synthetic_calibration'])
            sheet = pathlib.Path(body.files['checklist']).read_text()
            self.assertIn('test-edit.stl', sheet)
            self.assertIn('d_measured_mm', sheet)          # the loader's own list of what is missing
            self.assertIn('synthetic = false', sheet)
            self.assertAlmostEqual(t['hole'][0]['d_design_mm'], sz.cad_diameters_mm['fitted'][0], places=5)
            self.assertEqual(json.loads(pathlib.Path(body.files['specimen']).read_text())['context'], ctx)
            path = pathlib.Path(body.files['measurement'])
            specimen.write_bundle(body, preset, tmp)   # an untouched template may be exported again
            path.write_text(path.read_text() + '\n# recorded take: preserve this\n')
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                specimen.write_bundle(body, preset, tmp)
            self.assertEqual(path.read_bytes(), before)
