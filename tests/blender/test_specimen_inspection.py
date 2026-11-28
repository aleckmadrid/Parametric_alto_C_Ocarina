"""Export -> synthetic measurements -> fit -> exact edited-shell reuse, plus visual evidence.

All generated measurements in these tests are SYNTHETIC, never physical tuning evidence.
"""
import json
import pathlib
import tempfile
import time
import tomllib
import unittest

import bpy
import numpy as np

from ocarina_addon import api, body as body_mod, inspection, kernel_bridge, operators, presets, shell_edit, specimen
from tools import shell_edit_trial as trial

ROOT=pathlib.Path(__file__).resolve().parents[2]
K=kernel_bridge.kernel()
P=kernel_bridge.load_params()


class TestSpecimenInspection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='oca-specimen-')
        cls.out=pathlib.Path(cls.tmp.name)
        trial.reset_scene()
        cls.base=shell_edit.build_base('P4',80,params=P,verbose=False)
        cls.shell=bpy.data.objects[cls.base.object_names['shell']]
        neck=bpy.data.objects[cls.base.object_names['neck']]
        trial.boss(cls.base,cls.shell,neck,name='R_ring',height_mm=0.5)
        cls.first=shell_edit.finish(cls.shell,export_dir=str(cls.out / 'first'),inspection=True,
                                    params=P,cavity_mode_step=False,verbose=False)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_export_has_identity_and_actual_chimneys_before_calibration(self):
        b=self.first
        record=json.loads(pathlib.Path(b.files['specimen']).read_text())
        data=tomllib.loads(pathlib.Path(b.files['measurement']).read_text())
        self.assertTrue(data['context']['layout'].startswith('edited:'))
        self.assertEqual(data['context'],record['context'])
        self.assertEqual(inspection.load_snapshot(b.files['inspection_snapshot'])['context'], record['context'])
        self.assertEqual(record['calibration_identity'],b.info['shell_edit']['calibration_identity'])
        self.assertIn('stl_file',b.measurements)
        self.assertTrue((self.out/'first'/f'{b.body_id}.md').exists())
        for h,row in zip(data['hole'],b.sizing.holes.solutions['print']):
            self.assertAlmostEqual(h['chimney_mm'],row.chimney_mm, places=6)
        # the exported ID names the edit; the same edit again has the same ID, the untouched base has zeros
        tag=shell_edit.identity_tag(b.info['shell_edit']['calibration_identity'])
        self.assertEqual(b.body_id,'P4-80-edit-'+tag)
        self.assertNotEqual(tag,'0'*8)
        self.assertEqual(shell_edit.identity_tag(dict(voicing=None,layout=None)),'0'*8)
        self.assertNotEqual(shell_edit.identity_tag(dict(voicing='a',layout=None)),shell_edit.identity_tag(dict(voicing=None,layout='a')))
        self.assertIn('air_capped_stl',b.measurements)   # the same read-back as every exported body
        specimen.require_new_export(self.out/'first',b.body_id)   # untouched template: export again is allowed
        path=pathlib.Path(b.files['measurement'])
        blank=path.read_bytes()
        path.write_bytes(blank+b'\n# a recorded note\n')
        try:
            with self.assertRaises(FileExistsError):
                shell_edit.finish(self.shell,export_dir=str(self.out/'first'),verbose=False)
        finally:
            path.write_bytes(blank)

    def test_synthetic_measure_fit_and_finish_reuses_the_same_edit(self):
        b=self.first
        ctx=tomllib.loads(pathlib.Path(b.files['measurement']).read_text())['context']
        m=K.measurements.template_from_sizing(b.sizing,b.body_id,shape=b.preset_id,key='print',context=ctx)
        # the template filled in below is the exported file, not a look-alike
        exported=pathlib.Path(b.files['measurement']).read_text()
        m.comment=tomllib.loads(exported)['body']['comment']
        self.assertEqual(K.measurements.write_measurement_file(self.out/'same-blank.toml',m,blank=True),exported)
        m.synthetic=True
        m.comment='SYNTHETIC test measurements; nothing printed.'
        m.room_temp_c=22.
        m.v0_m3=80e-6
        m.water_temp_c=20.
        m.water_net_mass_g=m.v0_m3*K.measurements.water_density_kg_m3(20)*1e3
        for h in m.holes:
            h.d_measured_m=h.d_design_m
        frequencies=K.holes.predict_scale(.87*b.sizing.voicing.G_w(),m.v0_m3,
            [h.d_measured_m for h in m.holes],[h.chimney_m for h in m.holes],.8,m.c_m_s(P),[1.]*len(m.holes))
        for n,f in zip(m.notes,frequencies):
            n.takes_cents=[K.ocarina_kernel.cents(f,n.target_hz)]*3
            n.pressures_pa=[150.]*3
        measured=self.out/'synthetic-measured.toml'
        K.measurements.write_measurement_file(measured,m)
        loaded=K.measurements.load_measurement(measured)
        fitted=K.fitter.fit_bodies([loaded],P)
        cal=K.calibration.calibration_from_fit(fitted,[loaded],P)
        constants=self.out/'synthetic-constants.toml'
        K.calibration.write_calibration(constants,cal)
        cal=K.calibration.load_calibration(constants)
        again=shell_edit.finish(self.shell,calibration=cal,params=P,cavity_mode_step=False,verbose=False,
                                export_dir=str(self.out/'second'),inspection=True,previous_inspection=b.files['inspection_snapshot'])
        self.assertEqual(again.info['calibration_info']['eta_w_match'],'exact')
        self.assertEqual(again.info['calibration_info']['psi_match'],'exact')
        self.assertTrue(again.info['synthetic'])
        self.assertEqual(again.voicing_hash,b.voicing_hash)
        self.assertEqual(again.body_id,b.body_id)   # the same edit
        self.assertEqual(sum(o.name.startswith('OCA_P4-80-edit') and o.type=='MESH' and not o.name.endswith(('_air','_cavity')) for o in bpy.data.objects),1)
        for field in ('window_area_mm2','window_length_mm','window_width_mm'):
            self.assertEqual(getattr(again.sizing.voicing,field),getattr(b.sizing.voicing,field))
        text=pathlib.Path(again.files['inspection']).read_text()
        self.assertIn('SYNTHETIC',text)
        self.assertIn('class="previous"',text)
        # A new rim edit must not borrow the position factors just fitted.
        changed=dict(ctx,layout='edited:different-outside')
        _,info=K.calibration.size_body_from_calibration(cal,80,voicing=b.sizing.voicing,shape='P4',params=P,context=changed)
        self.assertNotEqual(info['psi_match'],'exact')
        changed=dict(ctx,voicing_context='edited:different-window')
        _,info=K.calibration.size_body_from_calibration(cal,80,voicing=b.sizing.voicing,shape='P4',params=P,context=changed)
        self.assertEqual(info['eta_w_match'],'fallback')

    def test_review_has_actual_sections_and_projected_jet_without_mutating_geometry(self):
        b=self.first
        before=b.solid[0].copy()
        mesh=bpy.data.objects[b.object_names['body']].data
        def scene():
            co=np.empty(3*len(mesh.vertices))
            mesh.vertices.foreach_get('co',co)
            return len(bpy.data.objects),co
        scene_before=scene()
        data=inspection._json_safe(inspection.snapshot(b))
        inspection.render_html(data)
        self.assertEqual(scene()[0],scene_before[0])
        self.assertTrue(np.array_equal(scene()[1],scene_before[1]))
        v=b.sizing.voicing
        # measured by the checks, not copied from the design
        self.assertAlmostEqual(data['measured']['windway_exit_height_mm'],b.measurements['voicing']['windway_exit_height_mm'])
        self.assertAlmostEqual(data['measured']['windway_exit_height_mm'],v.windway_exit_height_mm,places=2)
        j=data['jet_to_edge']
        self.assertAlmostEqual(j['off_axis_mm'],v.labium_offset_mm*np.cos(np.radians(v.windway_pitch_deg)),places=6)
        self.assertTrue(v.window_length_mm<=j['along_mm']<v.window_length_mm+0.5)
        # the drawing agrees with the check report written beside it
        from ocarina_addon import checks_geo
        report=json.loads(pathlib.Path(b.files['checks_json']).read_text())
        self.assertEqual(inspection.verify(inspection.load_snapshot(b.files['inspection_snapshot']),report,checks_geo.TOL_MM),[])
        wrong=dict(data,measured=dict(data['measured'],windway_exit_height_mm=1.5))
        self.assertEqual(len(inspection.verify(wrong,report)),2)   # not the report's value, and off the design
        unchecked=dict(data,measured={})
        self.assertIn('Exit not measured (design',inspection.svg_view(unchecked,'windway'))
        self.assertEqual(data['source'],'exported STL')
        self.assertTrue(data['sections']['windway']['solid'])
        jet=np.asarray(data['jet'])
        slope=(jet[1,1]-jet[0,1])/(jet[1,0]-jet[0,0])
        self.assertAlmostEqual(slope,-np.tan(np.radians(b.sizing.voicing.windway_pitch_deg)),places=8)
        self.assertAlmostEqual(np.linalg.norm(np.diff(data['exit_line'],axis=0)),b.sizing.voicing.windway_exit_height_mm)
        self.assertTrue(np.array_equal(before,b.solid[0]))
        text=pathlib.Path(b.files['inspection']).read_text()
        self.assertIn('not CFD',text)
        self.assertIn('Jet to edge',text)
        self.assertEqual(inspection.load_snapshot(b.files['inspection_snapshot'])['voicing_hash'],b.voicing_hash)

    def test_blender_properties_register_and_preserve_bowl_defaults(self):
        # __init__ was imported, but not registered by this test runner.
        operators.register()
        try:
            rna=bpy.ops.oca.build_body.get_rna_type()
            self.assertIn('calibration_path',rna.properties)
            self.assertEqual(rna.properties['rating'].default,'preset')
            self.assertIn('P4-bowl',rna.properties['preset'].enum_items.keys())
            self.assertIn('previous_inspection',bpy.ops.oca.finish_body.get_rna_type().properties)
            # the panel's settings: changing one builds nothing and returns at once
            s=bpy.context.scene.oca
            self.assertEqual((s.preset,s.rating),('P4-bowl','preset'))
            self.assertEqual(operators._preset_rating('P4-bowl'),'soft')
            meshes=len(bpy.data.meshes)
            started=time.perf_counter()
            s.preset,s.v0_cm3,s.rating,s.window_wall,s.export_dir,s.calibration_path='P0',65.0,'medium','4.0','//out','//c.toml'
            s.calibration_path=''
            self.assertLess(time.perf_counter()-started,0.05)
            self.assertEqual(len(bpy.data.meshes),meshes)
            # the neck's base: 0 keeps the preset; a value builds the preset with that key under an id that names it
            self.assertEqual(operators.panel_preset(s),('P0',None))
            before=operators.settings_signature(s)
            s.preset,s.neck_base_width_mm,s.neck_flare='P4-bowl',38.0,1.5
            preset,bid=operators.panel_preset(s)
            self.assertEqual((preset['neck_base_width_mm'],preset['neck_width_exponent'],preset['neck_depth_exponent'],preset['neck_base_depth_mm']),(38.0,1.5,1.5,25.4))
            self.assertEqual(bid,'P4-bowl-65-neck38x0f1.5')
            self.assertNotEqual(operators.settings_signature(s),before)
            s.neck_base_width_mm=s.neck_flare=0.0
            # preview, validate, then a changed setting
            self.assertEqual(operators.validation_state(bpy.context.scene),'not built')
        finally:
            operators.unregister()

    def test_preview_validate_and_changed_since_validation(self):
        operators.register()
        try:
            scene=bpy.context.scene
            s=scene.oca
            s.preset,s.v0_cm3,s.rating,s.export_dir,s.inspection='P0',65.0,'preset','',False
            with self.assertRaisesRegex(RuntimeError,'export folder'):          # background mode raises an operator's error
                bpy.ops.oca.run(action='EXPORT')
            self.assertEqual(bpy.ops.oca.run(action='PREVIEW'),{'FINISHED'})
            self.assertEqual(operators.validation_state(scene),'not validated')
            self.assertEqual(bpy.ops.oca.run(action='VALIDATE'),{'FINISHED'})
            self.assertEqual(operators.validation_state(scene),'validated')
            s.v0_cm3=66.0
            self.assertEqual(operators.validation_state(scene),'changed since validation')
            s.v0_cm3=65.0
            s.export_dir=str(self.out/'panel-export')                               # not a body setting
            self.assertEqual(operators.validation_state(scene),'validated')
            self.assertEqual(bpy.ops.oca.run(action='EXPORT'),{'FINISHED'})
            self.assertTrue((self.out/'panel-export'/'PRINT-AND-MEASURE.md').is_file())
            self.assertTrue((self.out/'panel-export'/'P0-65_measurement.toml').is_file())
        finally:
            operators.unregister()
