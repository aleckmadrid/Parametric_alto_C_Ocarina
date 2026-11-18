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
    def test_break_pressure_is_optional_and_round_trips(self):
        # Heuer's window check: the pressure at which the lowest note breaks. Optional, so old files still load.
        b = sy.synth_body("pb", "P0", 80.0, sy.make_truth())
        self.assertTrue(all(n.p_break_pa is None for n in b.notes))
        plain = self.tmp / "plain.toml"
        meas.write_measurement_file(plain, b)
        self.assertNotIn("p_break_pa =", plain.read_text(encoding="utf-8").replace("# p_break_pa =", ""))
        self.assertIsNone(meas.load_measurement(plain).notes[0].p_break_pa)
        b.notes[0].p_break_pa = 412.5
        path = self.tmp / "pb.toml"
        meas.write_measurement_file(path, b)
        back = meas.load_measurement(path)
        self.assertAlmostEqual(back.notes[0].p_break_pa, 412.5)
        self.assertTrue(all(n.p_break_pa is None for n in back.notes[1:]))
        fit = fitter.fit_body(back, P)
        self.assertAlmostEqual(fit.bodies[0].p_break_lowest_pa, 412.5)
        self.assertIn("Lowest note breaks at 412 Pa", fitter.format_report(fit))
        # the blank template asks for it on the lowest note
        blank = meas.write_measurement_file(self.tmp / "blank-pb.toml",
                                            meas.template_from_sizing(sizing.size_body(80.0), "X"), blank=True)
        self.assertIn("# p_break_pa =   # FILL IN: break pressure of the lowest note, Pa", blank)

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

    def test_windway_volume_is_prefilled_and_enforced(self):
        sz = sizing.size_body(80.0)
        t = meas.template_from_sizing(sz, "P0-80-a", "P0")
        v = sz.voicing
        expect = v.windway_length_mm * v.windway_width_mm * 0.5 * (v.windway_exit_height_mm + v.windway_inlet_height_mm) / 1000.0
        self.assertAlmostEqual(t.windway_cm3, expect, delta=1e-9)
        self.assertGreater(t.windway_cm3, 0.2)
        # the file carries it
        path = self.tmp / "blank.toml"
        meas.write_measurement_file(path, t, blank=True)
        self.assertAlmostEqual(meas.load_measurement(path, allow_incomplete=True).windway_cm3, round(expect, 4), delta=1e-9)
        # windway_in_fill = true with no volume is rejected, with a message
        b = sy.synth_body("x", "P0", 80.0, sy.make_truth())
        good = self.tmp / "good.toml"
        meas.write_measurement_file(good, b)
        text = good.read_text(encoding="utf-8").replace("windway_in_fill = false", "windway_in_fill = true")
        bad = self.tmp / "bad.toml"
        bad.write_text(text.replace("windway_cm3 = 0.0", "windway_cm3 = 0.0"), encoding="utf-8")
        with self.assertRaises(meas.MeasurementIncomplete) as cm:
            meas.load_measurement(bad)
        self.assertIn("windway_cm3", "\n".join(cm.exception.missing))

    def test_fit_cli_expands_wildcards_itself(self):
        import contextlib
        import io
        import fit_measurements
        buf = io.StringIO()
        pattern = str(ROOT / "measurements" / "synthetic-round1" / "*.toml")      # PowerShell passes this unexpanded
        with contextlib.redirect_stdout(buf):
            code = fit_measurements.main([pattern])
        self.assertEqual(code, 0)
        self.assertIn("Fit of 8 body(ies)", buf.getvalue())
        self.assertIn("SYNTHETIC DATA", buf.getvalue())
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(fit_measurements.main([str(ROOT / "measurements" / "template-blank.toml")]), 2)
        self.assertIn("incomplete", err.getvalue())

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

    def test_eight_bodies_with_awkward_truth(self):
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

    def test_eight_bodies_clean_truth_is_exact(self):
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
        # C2b. Before: the fitter had only the convention estimate, and k absorbed a psi scale (5 % in psi gave
        # about 8 % in k). Now: the CONVENTION estimate still shows that bias, and it is reported; the PROFILE
        # estimate compares k against the data, recovers the truth and drives the fit.
        base = sy.make_truth()
        t = sy.make_truth(psi={k: v * 1.05 for k, v in base["psi"].items()}, normalise=False)
        bodies = sy.round1_set(truth=t, noise_cents=0.0)
        fit = fitter.fit_bodies(bodies, P)
        self.assertGreater(abs(fit.k_hole_convention / t["k_hole"] - 1), 0.03)     # the convention value is biased
        self.assertLess(abs(fit.k_hole_convention / t["k_hole"] - 1), 0.15)
        self.assertEqual(fit.k_hole_source, "profile")
        self.assertLess(rel(fit.k_hole, t["k_hole"]), 1e-5)                         # the value in use is not
        self.assertLess(rel(fit.k_hole_profile.k_hole, t["k_hole"]), 1e-5)
        self.assertAlmostEqual(fit.psi_geomean_reference, 1.05, delta=1e-5)         # the psi scale is now a result
        self.assertTrue(any("convention value" in m and "outside the profile interval" in m for m in fit.messages))
        h = bodies[1].voicing_hash
        self.assertLess(rel(fit.eta_w_by_hash[h]["eta_w"], t["eta_w"]), 1e-5)  # eta_w is not affected
        for name, v in t["psi"].items():
            self.assertLess(rel(fit.psi["P0"][name], v), 1e-5, name)                # psi with its true scale
        # forcing the convention gives the old behaviour: ratios between position factors survive roughly
        old = fitter.fit_bodies(bodies, P, k_source="convention")
        self.assertEqual(old.k_hole_source, "convention")
        self.assertAlmostEqual(old.k_hole, fit.k_hole_convention, delta=1e-12)
        self.assertAlmostEqual(old.psi_geomean_reference, 1.0, delta=1e-9)
        r_fit = old.psi["P0"]["sub1"] / old.psi["P0"]["R_pinky"]
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


class TestKHoleProfile(TmpDirTest):
    """C2b, owner decision 2: k_hole estimated from the data (profile), next to the convention value."""

    LADDER = ("P0-65", "P0-80-a", "P0-95")

    def _truth(self, scale):
        base = sy.make_truth()
        return sy.make_truth(psi={k: v * scale for k, v in base["psi"].items()}, normalise=False)

    def _p0_88_worst_cents(self, truth, bodies, fit):
        """Size P0-88 (the prediction body, never printed in round 1) from the fitted constants, then play it with the true physics."""
        cal = cal_mod.calibration_from_fit(fit, bodies, P)
        body, _ = cal_mod.size_body_from_calibration(cal, 88.0, shape="P0", params=P)
        rows = body.holes.solutions["fitted"]
        chim = [r.chimney_mm * MM for r in rows]
        d_printed = [(cad + truth["hole_offset_mm"]) * MM for cad in body.cad_diameters_mm["fitted"]]
        pred = hl.predict_scale(truth["eta_w"] * body.voicing.G_w(), body.v0_cm3 * 1e-6, d_printed, chim,
                                truth["k_hole"], body.c_m_s, [truth["psi"][r.name] for r in rows])
        return max(abs(ok.cents(p, t)) for p, t in zip(pred, body.f_targets_hz))

    def test_noise_free_recovery_when_the_convention_is_broken(self):
        # psi scaled by 1.2 and by 0.8: the convention estimate is off by 28 % and 43 %, the profile is exact
        for scale, conv_expected in ((1.2, 0.769), (0.8, 1.526)):
            t = self._truth(scale)
            bodies = sy.round1_set(truth=t, noise_cents=0.0)
            loaded = [sy.roundtrip_through_file(b, self.tmp / f"{b.id}-{scale}.toml") for b in bodies]
            fit = fitter.fit_bodies(loaded, P)
            pr = fit.k_hole_profile
            self.assertTrue(pr.informative)
            self.assertEqual(fit.k_hole_source, "profile")
            self.assertLess(rel(fit.k_hole, t["k_hole"]), 1e-4, scale)
            self.assertLess(pr.lo, t["k_hole"])
            self.assertGreater(pr.hi, t["k_hole"])
            # 5.1 % (psi x 1.2) and 6.2 % (psi x 0.8) with the 65 / 80 / 95 ladder; it was under 5 % while the
            # ladder reached 125 cm3. Still well inside the 15 % rule that lets the profile drive.
            self.assertLess(pr.rel_halfwidth, 0.08)
            self.assertLess(pr.chi2_min, 1e-6)
            self.assertAlmostEqual(fit.k_hole_convention, conv_expected, delta=0.003)
            self.assertFalse(pr.lo <= fit.k_hole_convention <= pr.hi)
            self.assertTrue(any("outside the profile interval" in m for m in fit.messages))
            self.assertAlmostEqual(fit.psi_geomean_reference, scale, delta=1e-4)
            for name, v in t["psi"].items():
                self.assertLess(rel(fit.psi["P0"][name], v), 1e-4, name)
                self.assertLess(rel(fit.psi["P2"][name], v * sy.SHAPE_PSI_SCALE["P2"]), 1e-4, name)
            # Stage 3 / Gate 3: P0-88 sized from the fitted constants plays on pitch in the true physics.
            # With the convention estimate the same body is 5 cents (psi x 1.2) and 22 cents (psi x 0.8) off.
            # (P0-110 was 10 and 27 cents: 88 cm3 lies inside the ladder, so a k error costs less there.)
            self.assertLess(self._p0_88_worst_cents(t, loaded, fit), 0.1)
            conv = fitter.fit_bodies(loaded, P, k_source="convention")
            self.assertGreater(self._p0_88_worst_cents(t, loaded, conv), 4.0)

    def test_the_three_ladder_bodies_are_enough(self):
        t = self._truth(1.2)
        bodies = [b for b in sy.round1_set(truth=t, noise_cents=0.0) if b.id in self.LADDER]
        fit = fitter.fit_bodies(bodies, P)
        self.assertEqual(fit.k_hole_source, "profile")
        self.assertLess(rel(fit.k_hole, t["k_hole"]), 1e-4)

    def test_single_body_keeps_the_convention(self):
        # One body has a flat profile: any k fits with its own psi. Behaviour is the same as before C2b.
        for scale in (1.0, 1.2):
            t = self._truth(scale) if scale != 1.0 else sy.make_truth()
            b = sy.synth_body("one", "P0", 80.0, t, room_temp_c=24.0)
            fit = fitter.fit_body(b, P)
            self.assertEqual(fit.k_hole_source, "convention")
            self.assertFalse(fit.k_hole_profile.informative)
            self.assertEqual(fit.k_hole, fit.k_hole_convention)
            self.assertAlmostEqual(fit.psi_geomean_reference, 1.0, delta=1e-9)
            g = math.exp(sum(math.log(v) for v in fit.psi["P0"].values()) / 12)
            self.assertAlmostEqual(g, 1.0, delta=1e-9)
            self.assertFalse(any("outside the profile interval" in m for m in fit.messages))
            with self.assertRaises(ValueError):
                fitter.fit_body(b, P, k_source="profile")
        self.assertLess(rel(fitter.fit_body(sy.synth_body("one", "P0", 80.0, sy.make_truth()), P).k_hole, 1.07), 1e-3)

    def test_identical_copies_do_not_constrain_k(self):
        # three copies of P0-80 have the same holes: the profile is flat, the convention drives
        t = self._truth(1.2)
        bodies = [b for b in sy.round1_set(truth=t, noise_cents=0.0) if b.id.startswith("P0-80")]
        fit = fitter.fit_bodies(bodies, P)
        self.assertEqual(len(bodies), 3)
        self.assertEqual(fit.k_hole_source, "convention")
        self.assertFalse(fit.k_hole_profile.informative)

    def test_with_noise_the_profile_stays_near_the_truth(self):
        # +-5 cents uniform per take, 3 takes, eight bodies, psi scaled by 1.2, six seeds.
        # Tolerance: the one-sigma interval of the profile estimate is about 5 % here (4.8 % median, 5.4 %
        # worst over 12 seeds). The test allows 3 sigma = 15 %, which is also the limit of the rule that lets
        # the profile drive. The convention estimate is off by 28 % in the same runs, whatever the noise.
        t = self._truth(1.2)
        worst = 0.0
        for seed in range(6):
            bodies = sy.round1_set(seed=900 + seed, noise_cents=5.0, noise="uniform", truth=t)
            fit = fitter.fit_bodies(bodies, P)
            pr = fit.k_hole_profile
            self.assertEqual(fit.k_hole_source, "profile", seed)
            self.assertLess(rel(fit.k_hole, t["k_hole"]), 0.15, seed)
            self.assertGreater(rel(fit.k_hole_convention, t["k_hole"]), 0.20, seed)
            self.assertLess(pr.rel_halfwidth, 0.10, seed)
            self.assertGreater(pr.rel_halfwidth, 0.02, seed)                       # the noise is seen by the interval
            self.assertLess(self._p0_88_worst_cents(t, bodies, fit), 6.0, seed)   # Gate 3 allows 20 cents for P0-88
            worst = max(worst, rel(fit.k_hole, t["k_hole"]))
        self.assertGreater(worst, 1e-4)                                            # noise really reached the estimate

    def test_wide_interval_falls_back_to_the_convention(self):
        # A limit of 0.1 % can never be met with noise: the rule then keeps the convention estimate and says why.
        bodies = sy.round1_set(seed=3, noise_cents=5.0, noise="uniform")
        fit = fitter.fit_bodies(bodies, P, k_profile_max_rel_halfwidth=0.001)
        self.assertEqual(fit.k_hole_source, "convention")
        self.assertTrue(fit.k_hole_profile.informative)
        self.assertIn("wider than the limit", fit.k_hole_rule)
        self.assertEqual(fit.k_hole, fit.k_hole_convention)
        with self.assertRaises(ValueError):
            fitter.fit_bodies(bodies, P, k_source="median")

    def test_report_and_constants_file_carry_both_estimates(self):
        t = self._truth(1.2)
        bodies = sy.round1_set(truth=t, noise_cents=0.0)
        fit = fitter.fit_bodies(bodies, P)
        text = fitter.format_report(fit)
        for needle in ("profile estimate", "convention estimate", "1.0700", "0.77", "geometric mean of psi"):
            self.assertIn(needle, text)
        cal = cal_mod.calibration_from_fit(fit, bodies, P)
        path = self.tmp / "c.toml"
        cal_mod.write_calibration(path, cal)
        back = cal_mod.load_calibration(path)
        self.assertEqual(back.k_hole_source, "profile")
        self.assertAlmostEqual(back.k_hole, fit.k_hole, delta=1e-12)
        self.assertAlmostEqual(back.k_hole_profile, fit.k_hole_profile.k_hole, delta=1e-12)
        self.assertAlmostEqual(back.k_hole_convention, fit.k_hole_convention, delta=1e-12)
        self.assertAlmostEqual(back.k_hole_profile_lo, fit.k_hole_profile.lo, delta=1e-12)
        self.assertAlmostEqual(back.psi_geomean_reference, 1.2, delta=1e-4)
        # a single body: the report says that the profile estimate is not available
        one = fitter.fit_body(bodies[1], P)
        self.assertIn("not available", fitter.format_report(one))
        cal1 = cal_mod.calibration_from_fit(one, [bodies[1]], P)
        self.assertIsNone(cal1.k_hole_profile)
        self.assertEqual(cal1.k_hole_source, "convention")

    def test_share_none_has_no_profile(self):
        truth = sy.make_truth(psi={k: 1.0 for k in sy.DEFAULT_TRUTH["psi"]})
        bodies = [b for b in sy.round1_set(truth=truth, noise_cents=0.0) if b.shape == "P0"]
        fit = fitter.fit_bodies(bodies, P, share="none")
        self.assertIsNone(fit.k_hole_profile)
        self.assertEqual(fit.k_hole_source, "convention")

    def test_noise_study_has_the_psi_offset_rows(self):
        r = noise_study.run_case(0.0, "gauss", 3, 1, seed=3, single=False, params=P, psi_scale=1.2)
        self.assertLess(r["k_med"], 1e-3)                   # the k in use (profile) is exact, percent
        self.assertGreater(r["kc_med"], 20.0)               # the convention estimate is 28 % off
        self.assertEqual(r["profile_runs"], 1)
        self.assertLess(r["psi_med"], 1e-3)
        self.assertIn("psi scale", noise_study.table([r]))


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


class TestStubFile(TmpDirTest):
    """The measurement file of a Stage 1 voicing stub (measurements.stub_template, write_stub_file, load_stub)."""

    def _voicing(self):
        import voicing as vo
        return vo, vo.make_voicing(80.0)

    def test_blank_stub_template_is_valid_toml_and_incomplete(self):
        vo, v = self._voicing()
        t = meas.stub_template(v, "V-a", 25.0, predicted_hz=vo.stub_pitch_hz(v, 25.0))
        path = self.tmp / "V-a.toml"
        text = meas.write_stub_file(path, t, blank=True)
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
        self.assertEqual(data["schema"], meas.STUB_SCHEMA)
        self.assertEqual(data["stub"]["voicing_hash"], v.version_hash)
        self.assertEqual(data["stub"]["target_volume_cm3"], 25.0)
        self.assertAlmostEqual(data["voicing"]["window_area_mm2"], v.window_area_mm2)
        self.assertEqual(data["pitch"]["hz"], [])
        self.assertIn("FILL IN", text)
        self.assertNotIn("SYNTHETIC", text)
        with self.assertRaises(meas.MeasurementIncomplete) as cm:
            meas.load_stub(path)
        missing = "\n".join(cm.exception.missing)
        for needle in ("water_net_mass_g", "room_temp_c", "[pitch] hz"):
            self.assertIn(needle, missing)
        m = meas.load_stub(path, allow_incomplete=True)
        self.assertEqual(m.id, "V-a")
        self.assertEqual(m.takes_hz, [])
        self.assertIsNone(m.speaks_cleanly)

    def test_filled_stub_file_round_trip_gives_eta_w(self):
        # SYNTHETIC: an invented eta_w and an invented volume, written to a file, read back and fitted.
        vo, v = self._voicing()
        eta_true, v_true_cm3, room = 0.86, 24.6, 22.0
        f = vo.stub_pitch_hz(v, v_true_cm3, eta_w=eta_true, internal_temp_c=27.0)
        m = meas.stub_template(v, "V-a", 25.0, predicted_hz=vo.stub_pitch_hz(v, 25.0))
        m.synthetic = True
        m.water_temp_c = 21.0
        m.water_net_mass_g = v_true_cm3 * 1e-6 * meas.water_density_kg_m3(21.0) * 1e3
        m.room_temp_c = room
        m.takes_hz = [f * 2 ** (c / 1200.0) for c in (-1.5, 0.0, 1.5)]
        m.pressures_pa = [300.0, 310.0, 305.0]
        m.speaks_cleanly, m.overblows_a_semitone_cleanly = True, False
        path = self.tmp / "V-a-filled.toml"
        text = meas.write_stub_file(path, m)
        self.assertIn("SYNTHETIC DATA", text)
        back = meas.load_stub(path)
        self.assertTrue(back.synthetic)
        self.assertAlmostEqual(back.v0_cm3, v_true_cm3, places=9)
        self.assertAlmostEqual(back.f_hz, f, delta=1e-9 * f)
        self.assertAlmostEqual(back.spread_cents, 3.0, places=6)
        self.assertIs(back.speaks_cleanly, True)
        self.assertIs(back.overblows_a_semitone_cleanly, False)
        out = fitter.eta_w_from_stub(back.f_hz, back.v0_cm3, back.window_area_mm2, back.wall_at_window_mm, back.room_temp_c, P)
        self.assertAlmostEqual(out["eta_w"], eta_true, delta=1e-9)

    def test_stub_fill_corrections_and_errors(self):
        vo, v = self._voicing()
        m = meas.stub_template(v, "V-a", 25.0)
        m.water_net_mass_g, m.water_temp_c, m.room_temp_c, m.takes_hz, m.pressures_pa = 26.0, 20.0, 22.0, [780.0, 781.0, 782.0], []
        path = self.tmp / "s.toml"
        text = meas.write_stub_file(path, m)
        plain = meas.load_stub(path).v0_cm3
        path.write_text(text.replace("window_throat_in_fill = false", "window_throat_in_fill = true")
                        .replace("windway_in_fill = false", "windway_in_fill = true"), encoding="utf-8")
        both = meas.load_stub(path).v0_cm3
        throat = v.window_area_mm2 * v.wall_at_window_mm / 1000.0
        self.assertAlmostEqual(plain - both, round(throat, 4) + round(m.windway_cm3, 4), places=6)
        path.write_text(text.replace("hz = [780.0, 781.0, 782.0]", "hz = [780.0]"), encoding="utf-8")
        with self.assertRaises(meas.MeasurementIncomplete):
            meas.load_stub(path)
        path.write_text(text.replace(meas.STUB_SCHEMA, meas.SCHEMA), encoding="utf-8")
        with self.assertRaises(ValueError):
            meas.load_stub(path)
        path.write_text(text, encoding="utf-8")
        with self.assertRaises(ValueError):                      # a stub file is not a body file
            meas.load_measurement(path)


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

    def test_pooled_sigma_is_the_default_and_helps_with_many_bodies(self):
        # same noise, same seeds: the pooled per-body sigma is not worse than per-note standard errors
        # (seeded; over seeds 4, 11, 23, 37 with 40 runs each, pooled k error p95 is 0.22-0.37 % against 0.50-0.57 %)
        a = noise_study.run_case(5.0, "uniform", 3, 20, seed=11, single=False, params=P, sigma_mode="sem")
        b = noise_study.run_case(5.0, "uniform", 3, 20, seed=11, single=False, params=P, sigma_mode="pooled")
        self.assertLess(b["kc_p95"], a["kc_p95"])          # the convention estimate (the one these weights were tuned on)
        body = sy.synth_body("x", "P0", 80.0, sy.make_truth(), noise_cents=5.0, noise="uniform", rng=random.Random(1))
        s = fitter.note_sigmas_cents(body)
        self.assertEqual(len(set(s)), 1)                          # one value per body
        self.assertGreater(len(set(fitter.note_sigmas_cents(body, mode="sem"))), 1)


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

    def test_silent_defaults_are_reported(self):
        body, info = cal_mod.size_body_from_calibration(self.cal, 80.0, shape="P0", params=P)
        self.assertEqual(info["warnings"], [])
        self.assertTrue(info["shape_known"])
        body, info = cal_mod.size_body_from_calibration(self.cal, 88.0, shape="P9", params=P)
        self.assertFalse(info["shape_known"])
        self.assertTrue(any("P9" in w for w in info["warnings"]))
        self.assertTrue(any("never measured" in w for w in info["warnings"]))
        self.assertTrue(all(v == 1.0 for v in (r.psi for r in body.holes.solutions["fitted"])))

    def test_unresolved_psi_is_recorded_in_the_constants_file(self):
        b = sy.synth_body("x", "P0", 80.0, sy.make_truth())
        b.notes[4].takes_cents = [c - 400.0 for c in b.notes[4].takes_cents]       # hole 3 (R_ring) unresolved
        fit = fitter.fit_body(b, P)
        cal = cal_mod.calibration_from_fit(fit, [b], P)
        self.assertIn("P0/R_ring", cal.fit["psi_unresolved"])
        path = self.tmp / "c.toml"
        cal_mod.write_calibration(path, cal)
        body, info = cal_mod.size_body_from_calibration(cal_mod.load_calibration(path), 80.0, shape="P0", params=P)
        self.assertTrue(any("R_ring" in w for w in info["warnings"]))

    def test_fixed_tubes_can_be_passed_to_stage3(self):
        round1 = sizing.size_body(65.0)
        body, info = cal_mod.size_body_from_calibration(self.cal, 65.0, shape="P0", params=P, tubes_mm=round1.holes.tubes_mm)
        self.assertEqual(body.holes.tubes_mm, round1.holes.tubes_mm)

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
        body, info = cal_mod.size_body_from_calibration(self.cal, 88.0, shape="P0", params=P)    # never printed
        self.assertEqual(info["eta_w_source"], "fallback")
        self.assertAlmostEqual(body.eta_w, self.cal.eta_w_fallback)
        self.assertAlmostEqual(body.voicing.labium_offset_mm, -0.2)          # the params default reaches Stage 3
        self.assertAlmostEqual(body.a4_error_cents, 0.0, delta=1e-9)
        # the window was re-solved for the fallback eta_w: it is larger than the prior's window
        prior = sizing.size_body(88.0)
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
