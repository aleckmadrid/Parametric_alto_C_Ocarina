"""Tests for measurements.py, fitter.py, calibration.py, synthetic.py (C2).

ALL data in these tests is SYNTHETIC (invented truth, see kernel/synthetic.py).
"""
import math
import pathlib
import random
import sys
import tempfile
import tomllib
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import calibration as cal_mod  # noqa: E402
import config  # noqa: E402
import fitter  # noqa: E402
import holes as hl  # noqa: E402
import measurements as meas  # noqa: E402
import noise_study  # noqa: E402
import ocarina_kernel as ok  # noqa: E402
import sizing  # noqa: E402
import synthetic as sy  # noqa: E402

MM = 1e-3
P = config.load_params()
ROOT = config.ROOT


def rel(a, b):
    return abs(a / b - 1.0)


class TmpDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


class TestMeasurementFile(TmpDirTest):
    def test_water_density(self):
        self.assertAlmostEqual(meas.water_density_kg_m3(20.0), 998.2, delta=0.05)
        self.assertAlmostEqual(meas.water_density_kg_m3(4.0), 1000.0, delta=0.05)

    def test_note_names(self):
        self.assertEqual(meas.note_midi("A4"), 69)
        self.assertEqual(meas.note_midi("F6"), 89)
        self.assertAlmostEqual(meas.note_hz("A4"), 440.0)
        self.assertAlmostEqual(meas.note_hz("C#5"), ok.midi_f(73))

    def test_blank_template_fails_with_a_list_of_what_is_missing(self):
        sz = sizing.size_body(80.0)
        t = meas.template_from_sizing(sz, "P0-80-a", "P0")
        path = self.tmp / "blank.toml"
        meas.write_measurement_file(path, t, blank=True)
        with open(path, "rb") as fh:
            data = tomllib.load(fh)                       # valid TOML
        self.assertEqual(data["schema"], meas.SCHEMA)
        self.assertEqual(len(data["hole"]), 12)
        self.assertEqual(len(data["note"]), 13)
        with self.assertRaises(meas.MeasurementIncomplete) as cm:
            meas.load_measurement(path)
        text = "\n".join(cm.exception.missing)
        for needle in ("water_net_mass_g", "room_temp_c", "sub1: d_measured_mm", "[[note]] A4", "F6"):
            self.assertIn(needle, text)
        # but it can be read with allow_incomplete (the add-on shows it)
        m = meas.load_measurement(path, allow_incomplete=True)
        self.assertEqual(m.voicing_hash, sz.voicing.version_hash)
        self.assertAlmostEqual(m.holes[1].chimney_m / MM, sz.holes.solutions["print"][1].chimney_mm)

    def test_repo_template_matches_the_generator(self):
        path = ROOT / "measurements" / "template-blank.toml"
        self.assertTrue(path.exists(), "run python kernel/synthetic.py --write-examples")
        with self.assertRaises(meas.MeasurementIncomplete):
            meas.load_measurement(path)
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("SYNTHETIC", text)
        self.assertIn("synthetic = false", text)

    def test_cents_and_hz_input_are_equivalent(self):
        b = sy.synth_body("x", "P0", 80.0, sy.make_truth(), noise_cents=2.0, rng=random.Random(3))
        a = self.tmp / "hz.toml"
        c = self.tmp / "cents.toml"
        meas.write_measurement_file(a, b, takes_hz=True)
        meas.write_measurement_file(c, b, takes_hz=False)
        ma, mc = meas.load_measurement(a), meas.load_measurement(c)
        for na, nc in zip(ma.notes, mc.notes):
            self.assertAlmostEqual(na.cents_mean, nc.cents_mean, delta=1e-9)

    def test_both_hz_and_cents_is_an_error(self):
        data = dict(schema=meas.SCHEMA, body=dict(id="x", shape="P0", voicing_hash="h", target_v0_cm3=80.0),
                    voicing=dict(window_area_mm2=60.0, wall_at_window_mm=4.0), fill=dict(water_net_mass_g=80.0),
                    conditions=dict(room_temp_c=22.0), hole=[dict(name="a", chimney_mm=4.0, d_design_mm=5.0, d_measured_mm=5.0)],
                    note=[dict(name="A4", hz=[440.0, 440.0, 440.0], cents=[0.0, 0.0, 0.0], p_pa=[150, 150, 150])])
        with self.assertRaises(ValueError):
            meas.parse_measurement(data)

    def test_water_mass_to_volume_and_corrections(self):
        b = sy.synth_body("x", "P0", 80.0, sy.make_truth(), water_temp_c=18.0)
        path = self.tmp / "w.toml"
        meas.write_measurement_file(path, b)
        m = meas.load_measurement(path)
        self.assertAlmostEqual(m.v0_m3, b.v0_m3, delta=1e-12)
        # window throat in the fill is subtracted: area x wall = 62.8 mm2 x 4 mm = 0.251 cm3
        text = path.read_text(encoding="utf-8").replace("window_throat_in_fill = false", "window_throat_in_fill = true")
        path2 = self.tmp / "w2.toml"
        path2.write_text(text, encoding="utf-8")
        m2 = meas.load_measurement(path2)
        self.assertAlmostEqual((m.v0_m3 - m2.v0_m3) / 1e-6, 62.8 * 4.0 / 1000.0, delta=0.01)

    def test_take_statistics(self):
        n = meas.NoteMeas("A4", 440.0, [-2.0, 0.0, 2.0], [150.0] * 3)
        self.assertAlmostEqual(n.cents_mean, 0.0)
        self.assertAlmostEqual(n.f_hz, 440.0)
        self.assertAlmostEqual(n.cents_sem, 2.0 / math.sqrt(3))
        self.assertIsNone(meas.NoteMeas("A4", 440.0, [1.0], [150.0]).cents_sem)

    def test_fewer_than_three_takes_is_reported(self):
        b = sy.synth_body("x", "P0", 80.0, sy.make_truth(), n_takes=2)
        path = self.tmp / "two.toml"
        meas.write_measurement_file(path, b)
        with self.assertRaises(meas.MeasurementIncomplete) as cm:
            meas.load_measurement(path)
        self.assertIn("2 take(s), 3 wanted", "\n".join(cm.exception.missing))

    def test_toml_writer_round_trip_with_awkward_strings(self):
        awkward = 'say "hi" \\ back'
        text = "\n".join([f"a = {meas.toml_value(awkward)}", f"b = {meas.toml_value([1.5, 2, 3.25])}",
                          f"c = {meas.toml_value(True)}", f"[{meas.toml_key('d1b6418b1844')}]", "x = 1",
                          f"[{meas.toml_key('has space.and dot')}]", "y = 2"])
        d = tomllib.loads(text)
        self.assertEqual(d["a"], awkward)
        self.assertEqual(d["b"], [1.5, 2, 3.25])
        self.assertEqual(d["d1b6418b1844"]["x"], 1)
        self.assertEqual(d["has space.and dot"]["y"], 2)
        with self.assertRaises(ValueError):
            meas.toml_value(float("nan"))


class TestRecoveryNoiseFree(TmpDirTest):
    """The fitter recovers invented truth within 1 %. Data goes through a measurement file."""

    def _fit_through_files(self, bodies):
        loaded = [sy.roundtrip_through_file(b, self.tmp / f"{b.id}.toml") for b in bodies]
        return fitter.fit_bodies(loaded, P), loaded

    def test_single_body_recovers_everything(self):
        truth = sy.make_truth()
        b = sy.synth_body("one", "P0", 80.0, truth, room_temp_c=24.0)
        fit, loaded = self._fit_through_files([b])
        h = b.voicing_hash
        self.assertLess(rel(fit.eta_w_by_hash[h]["eta_w"], truth["eta_w"]), 1e-3)
        self.assertLess(rel(fit.k_hole, truth["k_hole"]), 1e-3)
        for name, v in truth["psi"].items():
            self.assertLess(rel(fit.psi["P0"][name], v), 1e-3, name)
        # eta_w·G_w
        X_true = truth["eta_w"] * sizing.size_body(80.0).voicing.G_w() / MM
        self.assertLess(rel(fit.bodies[0].X_w_mm, X_true), 1e-3)

    def test_nine_bodies_with_awkward_truth(self):
        # per-hole psi, tubes (65 cm3 needs them), measured diameters and V0 that differ from the design,
        # a different room temperature per body, three shapes
        truth = sy.make_truth()
        bodies = sy.round1_set(truth=truth, noise_cents=0.0, hole_scatter_mm=0.04, volume_scatter_rel=0.004,
                               window_scatter_rel=0.006)
        self.assertTrue(any(h.chimney_m / MM > 4.5 for h in bodies[0].holes))          # a tube is in play
        self.assertGreater(len({round(b.room_temp_c, 1) for b in bodies}), 4)
        fit, loaded = self._fit_through_files(bodies)
        self.assertLess(rel(fit.k_hole, truth["k_hole"]), 0.01)
        eta_h = bodies[1].voicing_hash
        # the window scatter makes eta_w differ by body; the mean over three copies stays inside 1 %
        self.assertLess(rel(fit.eta_w_by_hash[eta_h]["eta_w"], truth["eta_w"]), 0.01)
        for name, v in truth["psi"].items():
            # the per-hole scatter of 0.04 mm in diameter feeds psi, so psi is checked at 3 %, P0 only
            self.assertLess(rel(fit.psi["P0"][name], v), 0.03, name)
        self.assertAlmostEqual(fit.hole_offset_mm, truth["hole_offset_mm"], delta=0.02)
        self.assertAlmostEqual(fit.volume_factor, truth["volume_factor"], delta=0.005)
        self.assertAlmostEqual(fit.breath["alpha"], truth["breath_alpha"], delta=0.1)
        self.assertAlmostEqual(fit.breath["p0_pa"], truth["breath_p0_pa"], delta=15.0)

    def test_nine_bodies_clean_truth_is_exact(self):
        truth = sy.make_truth()
        bodies = sy.round1_set(truth=truth, noise_cents=0.0)
        fit, _ = self._fit_through_files(bodies)
        self.assertLess(rel(fit.k_hole, truth["k_hole"]), 1e-5)
        h = bodies[1].voicing_hash
        self.assertLess(rel(fit.eta_w_by_hash[h]["eta_w"], truth["eta_w"]), 1e-5)
        for name, v in truth["psi"].items():
            self.assertLess(rel(fit.psi["P0"][name], v), 1e-5, name)
        # bodies of the shape P2 have psi scaled by 0.95: the fit sees it as a shape effect
        for name, v in truth["psi"].items():
            self.assertLess(rel(fit.psi["P2"][name], v * sy.SHAPE_PSI_SCALE["P2"]), 1e-5, name)

    def test_k_absorbs_a_psi_scale_that_breaks_the_convention(self):
        base = sy.make_truth()
        t = sy.make_truth(psi={k: v * 1.05 for k, v in base["psi"].items()}, normalise=False)
        bodies = sy.round1_set(truth=t, noise_cents=0.0)
        fit = fitter.fit_bodies(bodies, P)
        self.assertGreater(abs(fit.k_hole / t["k_hole"] - 1), 0.03)         # k is biased: 5 % in psi -> about 8 % in k
        self.assertLess(abs(fit.k_hole / t["k_hole"] - 1), 0.15)
        h = bodies[1].voicing_hash
        self.assertLess(rel(fit.eta_w_by_hash[h]["eta_w"], t["eta_w"]), 1e-5)  # eta_w is not affected
        # ratios between position factors survive
        r_fit = fit.psi["P0"]["sub1"] / fit.psi["P0"]["R_pinky"]
        r_true = t["psi"]["sub1"] / t["psi"]["R_pinky"]
        self.assertAlmostEqual(r_fit / r_true, 1.0, delta=0.12)

    def test_corrected_diameters_put_every_note_on_pitch(self):
        truth = sy.make_truth()
        b = sy.synth_body("one", "P0", 80.0, truth, room_temp_c=23.0)
        fit = fitter.fit_body(b, P)
        bf = fit.bodies[0]
        c = b.c_m_s(P)
        chim = [h.chimney_m for h in b.holes]
        d_need = [h.d_needed_mm * MM for h in bf.holes]
        psi_true = [truth["psi"][h.name] for h in b.holes]
        # with the TRUE physics, the needed diameters hit every note above A4
        pred = hl.predict_scale(bf.X_w_mm * MM, b.v0_m3, d_need, chim, truth["k_hole"], c, psi_true)
        for p, n in zip(pred[1:], b.notes[1:]):
            self.assertLess(abs(ok.cents(p, n.target_hz)), 0.02)
        # printed holes are 0.12 mm under their design: ream_mm and the CAD diameter reflect that
        for hf in bf.holes:
            self.assertAlmostEqual(hf.d_cad_needed_mm, hf.d_needed_mm - fit.hole_offset_mm, delta=1e-12)
        self.assertAlmostEqual(bf.a4_error_cents, ok.cents(b.notes[0].f_hz, b.notes[0].target_hz), delta=1e-9)

    def test_holes_that_are_too_big_are_flagged(self):
        truth = sy.make_truth(hole_offset_mm=+0.6)         # holes printed far too large
        b = sy.synth_body("big", "P0", 80.0, truth)
        fit = fitter.fit_body(b, P)
        flags = [f for h in fit.bodies[0].holes for f in h.flags]
        self.assertIn("too_big_cannot_ream", flags)
        small = sy.synth_body("small", "P0", 80.0, sy.make_truth(hole_offset_mm=-0.3))
        f2 = fitter.fit_body(small, P)
        self.assertTrue(all(h.ream_mm > 0 for h in f2.bodies[0].holes[3:]))

    def test_pad_limit_flag_uses_the_params(self):
        b = sy.synth_body("v", "P0", 125.0, sy.make_truth())
        fit = fitter.fit_body(b, P)
        self.assertTrue(any("above_pad_limit" in h.flags for h in fit.bodies[0].holes))

    def test_share_none_fits_k_only(self):
        truth = sy.make_truth(psi={k: 1.0 for k in sy.DEFAULT_TRUTH["psi"]})
        bodies = [b for b in sy.round1_set(truth=truth, noise_cents=0.0) if b.shape == "P0"]
        fit = fitter.fit_bodies(bodies, P, share="none")
        self.assertLess(rel(fit.k_hole, truth["k_hole"]), 1e-5)
        self.assertTrue(all(v == 1.0 for tbl in fit.psi.values() for v in tbl.values()))
        # with psi = 1 true, the shapes are all alike: pooled psi=1 residual is ~0
        self.assertLess(fit.pooled_psi1.rms_cents, 0.5)

    def test_region_sharing(self):
        regions = {n: ("bulb" if n.startswith("L_") else "tail" if n.startswith("R_") else "centre")
                   for n in sy.DEFAULT_TRUTH["psi"]}
        truth = sy.make_truth(psi={n: {"bulb": 1.1, "tail": 0.9, "centre": 1.0}[regions[n]] for n in regions})
        bodies = sy.round1_set(truth=truth, noise_cents=0.0)
        fit = fitter.fit_bodies(bodies, P, share="region", regions=regions)
        self.assertLess(rel(fit.k_hole, truth["k_hole"]), 1e-4)
        self.assertAlmostEqual(fit.psi["P0"]["L_ring"], fit.psi["P0"]["L_index"], delta=1e-12)
        with self.assertRaises(ValueError):
            fitter.fit_bodies(bodies, P, share="region")

    def test_room_temperature_enters_the_fit(self):
        truth = sy.make_truth()
        b = sy.synth_body("one", "P0", 80.0, truth, room_temp_c=22.0)
        b_wrong = sy.synth_body("one", "P0", 80.0, truth, room_temp_c=22.0)
        b_wrong.room_temp_c = 32.0                          # the file says 32 degC, the body was played at 22
        e0 = fitter.fit_body(b, P).bodies[0].eta_w
        e1 = fitter.fit_body(b_wrong, P).bodies[0].eta_w
        self.assertLess(e1, e0 * 0.99)                      # a warmer room means a bigger c, so G and eta_w come out smaller (1.1 %)
        self.assertAlmostEqual(e1 / e0, (ok.c_air(27.0) / ok.c_air(ok.internal_air_temp_c(32.0))) ** 2, delta=1e-9)


class TestGate2Numbers(TmpDirTest):
    def test_pooled_psi1_uses_one_eta_per_hash(self):
        # Three copies of the same voicing with scatter in the window: with one eta_w per hash, A4 does NOT fit
        # perfectly in every body. (A per-body eta_w would hide this.)
        truth = sy.make_truth(psi={k: 1.0 for k in sy.DEFAULT_TRUTH["psi"]})
        rng = random.Random(5)
        bodies = [sy.synth_body(f"c{i}", "P0", 80.0, truth, rng=rng, window_scatter_rel=0.02) for i in range(3)]
        fit = fitter.fit_bodies(bodies, P)
        self.assertEqual(len(fit.pooled_psi1.eta_w_by_hash), 1)
        a4 = [abs(b.residual_pooled_psi1_cents[0]) for b in fit.bodies]
        self.assertGreater(max(a4), 3.0)
        # 2 % scatter in eta_w is about 17 cents at A4
        self.assertLess(max(a4), 40.0)

    def test_pooled_psi1_residual_exposes_position_effects(self):
        truth = sy.make_truth()                              # psi 0.83 .. 1.13
        fit = fitter.fit_bodies(sy.round1_set(truth=truth, noise_cents=0.0), P)
        self.assertGreater(fit.pooled_psi1.rms_cents, 5.0)
        self.assertLess(fit.pooled_psi1.rms_cents, 60.0)
        # the shared-psi residual is ~0 on noise-free data
        for b in fit.bodies:
            self.assertLess(b.rms_shared_psi_cents, 0.01)

    def test_copies_agree(self):
        fit = fitter.fit_bodies(sy.round1_set(noise_cents=0.0), P)
        d = fit.eta_w_by_hash[fit.bodies[1].voicing_hash]
        self.assertEqual(d["n"], 6)                      # P0-80 x3 and P1, P2, P3 at 80 cm3 share one voicing hash
        self.assertLess(d["sigma"], 1e-6)


class TestRobustness(TmpDirTest):
    def test_unresolved_hole_does_not_crash(self):
        b = sy.synth_body("x", "P0", 80.0, sy.make_truth())
        # make note 4 flatter than note 3: the conductance of hole 3 comes out negative
        b.notes[4].takes_cents = [c - 400.0 for c in b.notes[4].takes_cents]
        fit = fitter.fit_body(b, P)
        h = fit.bodies[0].holes
        self.assertFalse(h[3].resolved)
        self.assertIn("unresolved", h[3].flags)
        self.assertIsNone(h[3].G_eff_mm)
        self.assertTrue(any("unresolved" in m for m in fit.messages))
        self.assertTrue(math.isfinite(fit.k_hole))

    def test_single_take_uses_the_default_sigma(self):
        b = sy.synth_body("x", "P0", 80.0, sy.make_truth(), n_takes=1)
        X, G, sig, _ = fitter.effective_conductances(b, b.c_m_s(P))
        self.assertTrue(all(s is not None and s > 0 for s in sig))

    def test_note_count_must_match_hole_count(self):
        b = sy.synth_body("x", "P0", 80.0, sy.make_truth())
        b.notes = b.notes[:-1]
        with self.assertRaises(ValueError):
            fitter.fit_body(b, P)

    def test_incomplete_body_is_rejected(self):
        b = sy.synth_body("x", "P0", 80.0, sy.make_truth())
        b.holes[2].d_measured_m = None
        with self.assertRaises(meas.MeasurementIncomplete):
            fitter.fit_body(b, P)

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            fitter.fit_bodies([], P)

    def test_report_is_labelled_synthetic(self):
        fit = fitter.fit_bodies(sy.round1_set(noise_cents=0.0)[:3], P)
        text = fitter.format_report(fit)
        self.assertIn("SYNTHETIC DATA", text)
        self.assertIn("Gate 2 number", text)


class TestStubs(unittest.TestCase):
    def test_stub_pitch_and_eta_w_round_trip(self):
        import voicing as vo
        v = vo.make_voicing(80.0)
        f = vo.stub_pitch_hz(v, 25.0, eta_w=0.86, internal_temp_c=27.0)
        self.assertGreater(f, 700.0)                 # a 25 cm3 stub with the 80 cm3 window plays well above A4
        self.assertLess(f, 1100.0)
        out = fitter.eta_w_from_stub(f, 25.0, v.window_area_mm2, v.wall_at_window_mm, room_temp_c=22.0, params=P)
        self.assertAlmostEqual(out["eta_w"], 0.86, delta=1e-9)       # 22 degC room = 27 degC internal air
        # a stub is a body without holes: the pitch of the 80 cm3 body's A4 gives the prior eta_w exactly
        f_a4 = vo.stub_pitch_hz(v, 80.0)
        self.assertAlmostEqual(f_a4, 440.0, delta=1e-6)


class TestNoise(unittest.TestCase):
    """Seeded and loose, so the suite is not flaky. The full table is in the notes."""

    def test_error_grows_with_noise_and_stays_small(self):
        truth = sy.make_truth()
        r0 = noise_study.run_case(0.0, "uniform", 3, 1, seed=3, single=True, truth=truth, params=P)
        r2 = noise_study.run_case(2.0, "uniform", 3, 6, seed=3, single=True, truth=truth, params=P)
        r5 = noise_study.run_case(5.0, "uniform", 3, 6, seed=3, single=True, truth=truth, params=P)
        self.assertLess(r0["k_med"], 1e-6)
        self.assertLess(r2["psi_med"], r5["psi_med"])
        self.assertLess(r2["k_med"], r5["k_med"])
        # +-5 cents uniform, 3 takes, one body: eta_w·G_w under 1 %, k under 3 %, psi a few percent
        self.assertLess(r5["eta_p95"], 1.0)
        self.assertLess(r5["k_p95"], 3.0)
        self.assertLess(r5["psi_med"], 5.0)
        self.assertGreater(r5["psi_med"], 0.2)           # noise is really applied
        self.assertEqual(r5["unresolved"], 0)


class TestCalibrationFile(TmpDirTest):
    def setUp(self):
        super().setUp()
        self.bodies = sy.round1_set(noise_cents=1.0, seed=2)
        self.fit = fitter.fit_bodies(self.bodies, P)
        self.cal = cal_mod.calibration_from_fit(self.fit, self.bodies, P)

    def test_synthetic_label_is_carried_to_the_file(self):
        path = self.tmp / "c.toml"
        text = cal_mod.write_calibration(path, self.cal)
        self.assertIn("SYNTHETIC CONSTANTS", text)
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
        self.assertTrue(data["synthetic"])
        self.assertTrue(cal_mod.load_calibration(path).synthetic)

    def test_round_trip(self):
        path = self.tmp / "c.toml"
        cal_mod.write_calibration(path, self.cal)
        back = cal_mod.load_calibration(path)
        self.assertAlmostEqual(back.k_hole, self.cal.k_hole, delta=1e-12)
        self.assertAlmostEqual(back.eta_w_fallback, self.cal.eta_w_fallback, delta=1e-12)
        self.assertAlmostEqual(back.volume_factor, self.cal.volume_factor, delta=1e-12)
        self.assertEqual(set(back.voicings), set(self.cal.voicings))
        h = self.bodies[1].voicing_hash
        self.assertAlmostEqual(back.voicings[h]["eta_w"], self.cal.voicings[h]["eta_w"], delta=1e-12)
        for shape in ("P0", "P1", "P2", "P3"):
            for n, v in self.cal.psi[shape].items():
                self.assertAlmostEqual(back.psi[shape][n], v, delta=1e-12)
        self.assertEqual(back.internal_air["room_coupling"], 0.31)

    def test_repo_synthetic_files_are_labelled_and_load(self):
        cp = ROOT / "calibration" / "synthetic-fitted-constants.toml"
        self.assertTrue(cp.exists(), "run python kernel/synthetic.py --write-examples")
        self.assertTrue(cal_mod.load_calibration(cp).synthetic)
        self.assertIn("SYNTHETIC", cp.read_text(encoding="utf-8")[:200])
        for f in [ROOT / "measurements" / "example-synthetic-P0-80.toml"] + sorted((ROOT / "measurements" / "synthetic-round1").glob("*.toml")):
            m = meas.load_measurement(f)
            self.assertTrue(m.synthetic, f.name)
            self.assertIn("SYNTHETIC", f.read_text(encoding="utf-8")[:200], f.name)

    def test_wrong_schema_is_rejected(self):
        path = self.tmp / "bad.toml"
        path.write_text('schema = "something-else"\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            cal_mod.load_calibration(path)
        with self.assertRaises(ValueError):
            meas.parse_measurement({"schema": "x"})

    def test_stage3_sizing_known_hash_keeps_the_window(self):
        v0 = 80.0
        body, info = cal_mod.size_body_from_calibration(self.cal, v0, shape="P0", params=P)
        self.assertEqual(info["eta_w_source"], "measured")
        self.assertTrue(info["synthetic"])
        self.assertEqual(body.voicing.version_hash, self.bodies[1].voicing_hash)
        self.assertLess(abs(body.a4_error_cents), 60.0)                 # eta_w is 0.86 against the 0.90 prior: flat or sharp
        self.assertNotEqual(round(body.a4_error_cents, 3), 0.0)
        self.assertEqual(list(body.holes.solutions), ["fitted"])
        # retarget: A4 on pitch, smaller volume (eta 0.86 < 0.90)
        r, _ = cal_mod.size_body_from_calibration(self.cal, v0, shape="P0", retarget_volume=True, params=P)
        self.assertAlmostEqual(r.a4_error_cents, 0.0, delta=1e-9)
        self.assertLess(r.v0_cm3, v0)
        self.assertAlmostEqual(r.volume_factor, self.cal.volume_factor)

    def test_stage3_sizing_unknown_hash_uses_the_fallback(self):
        body, info = cal_mod.size_body_from_calibration(self.cal, 110.0, shape="P0", params=P)   # never printed
        self.assertEqual(info["eta_w_source"], "fallback")
        self.assertAlmostEqual(body.eta_w, self.cal.eta_w_fallback)
        self.assertAlmostEqual(body.a4_error_cents, 0.0, delta=1e-9)
        # the window was re-solved for the fallback eta_w: it is larger than the prior's window
        prior = sizing.size_body(110.0)
        self.assertGreater(body.voicing.window_area_mm2, prior.voicing.window_area_mm2 * 0.99)

    def test_stage3_corrected_body_hits_the_scale_in_the_synthetic_world(self):
        # Close the loop: with the synthetic truth known, holes sized from fitted constants play on pitch.
        truth = sy.make_truth()
        bodies = sy.round1_set(truth=truth, noise_cents=0.0)
        cal = cal_mod.calibration_from_fit(fitter.fit_bodies(bodies, P), bodies, P)
        body, _ = cal_mod.size_body_from_calibration(cal, 80.0, shape="P0", retarget_volume=True, params=P)
        rows = body.holes.solutions["fitted"]
        chim = [r.chimney_mm * MM for r in rows]
        # printed = CAD + true offset
        d_printed = [(cad + truth["hole_offset_mm"]) * MM for cad in body.cad_diameters_mm["fitted"]]
        X = truth["eta_w"] * body.voicing.G_w()
        V0 = body.v0_cm3 * 1e-6                                   # retargeted capped volume (volume factor aside)
        psi_true = [truth["psi"][r.name] for r in rows]
        pred = hl.predict_scale(X, V0, d_printed, chim, truth["k_hole"], body.c_m_s, psi_true)
        for p, t in zip(pred[1:], body.f_targets_hz[1:]):
            self.assertLess(abs(ok.cents(p, t)), 0.1)


if __name__ == "__main__":
    unittest.main()
