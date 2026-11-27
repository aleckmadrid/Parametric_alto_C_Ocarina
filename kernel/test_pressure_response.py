"""The observations extension of the measurement file and the pressure response of one instrument.

Every instrument here is SYNTHETIC: invented sensitivities, invented readings, flagged synthetic.
"""
import dataclasses
import math
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import config  # noqa: E402
import fitter  # noqa: E402
import measurements as meas  # noqa: E402
import sizing  # noqa: E402
import synthetic as sy  # noqa: E402

P = config.load_params()
TEMPLATE = meas.template_from_sizing(sizing.size_body(80.0, params=P), "X-80")


def instrument(name, sensitivity, in_tune_pa, pressures=(250.0, 350.0, 500.0, 700.0)):
    """A synthetic instrument whose fingering f reads cents = sensitivity[f] * log2(p / in_tune_pa[f]) at every pressure."""
    obs, order = [], 0
    for f, cpd in sensitivity.items():
        target = next(n.target_hz for n in TEMPLATE.notes if n.name == f)
        for sweep, ps in (("up", pressures), ("down", tuple(reversed(pressures)))):
            for p in ps:
                order += 1
                obs.append(meas.Observation(f, p, target * 2.0 ** (cpd * math.log2(p / in_tune_pa[f]) / 1200.0),
                                            take=sweep, order=order, sweep=sweep))
    return dataclasses.replace(TEMPLATE, id=name, synthetic=True, room_temp_c=21.0, observations=obs,
                               session=dict(instrument=name, specimen=f"{name}-a", method="synthetic sweep"))


class TestObservationFiles(unittest.TestCase):
    def test_old_files_load_as_before(self):
        old = meas.load_measurement(config.ROOT / "measurements" / "example-synthetic-P0-80.toml")
        self.assertEqual((old.observations, old.session, old.speaking_range), ([], {}, {}))
        self.assertEqual(len(old.notes), 13)

    def test_paired_readings_round_trip_in_their_order(self):
        obs = [meas.Observation("C5", 400.0, 523.0, take="1", order=3, sweep="up"),
               meas.Observation("C5", None, 524.5, status="airy", take="2", order=1),                  # pressure not read
               meas.Observation("F6", 900.0, None, status="absent", order=2, sweep="down"),           # no note: no hz
               meas.Observation("B5x", 610.0, 1001.0, order=4, open_holes=["L_index", "R_ring"], target_hz=1000.0, audio="b5x.wav")]
        m = dataclasses.replace(TEMPLATE, observations=obs, session=dict(instrument="P4-bowl-80", specimen="a", internal_temp_c=29.5),
                                speaking_range={"A4": (180.0, 640.0), "C5": (None, 900.0)})
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "m.toml"
            meas.write_measurement_file(path, m, blank=True)
            back = meas.load_measurement(path, allow_incomplete=True)
        self.assertEqual(back.observations, obs)
        self.assertEqual(back.session, m.session)
        self.assertEqual(back.speaking_range, m.speaking_range)

    def test_a_note_that_did_not_speak_has_no_frequency(self):
        data = dict(schema=meas.SCHEMA, observations_version=1, observation=[dict(fingering="F6", p_pa=900.0, hz=1400.0, status="absent")])
        with self.assertRaisesRegex(ValueError, "did not speak has no frequency"):
            meas.parse_measurement(data, allow_incomplete=True)
        with self.assertRaisesRegex(ValueError, "observations_version"):
            meas.parse_measurement(dict(schema=meas.SCHEMA, observation=[dict(fingering="C5")]), allow_incomplete=True)
        with self.assertRaisesRegex(ValueError, "measured temperature"):
            meas.parse_measurement(dict(schema=meas.SCHEMA, session=dict(internal_temp_c="warm")), allow_incomplete=True)


class TestPressureResponse(unittest.TestCase):
    def response(self, rows, **changes):
        """Rows: pressure, cents (or None), status; all readings are synthetic."""
        target = meas.note_hz("C5")
        obs = [meas.Observation("C5", p, None if c is None else target * 2 ** (c / 1200), status=status, order=i)
               for i, (p, c, status) in enumerate(rows)]
        m = dataclasses.replace(TEMPLATE, observations=obs, **changes)
        return m, fitter.pressure_response(m)["C5"]

    def test_nearly_flat_fit_does_not_overflow_before_checking_bounds(self):
        m, r = self.response([(100, 10, "clean"), (200, 9.999, "clean")])
        self.assertIsNone(r["in_tune_pa"])
        self.assertIn("not extrapolated", r["in_tune"])
        self.assertIn("outside", fitter.format_pressure_response(m, P))

    def test_flat_response_has_no_unique_tuning_pressure(self):
        for cents in (0, 10, -10):
            with self.subTest(cents=cents):
                _, r = self.response([(100, cents, "clean"), (200, cents, "clean")])
                self.assertIsNone(r["in_tune_pa"])
                self.assertIn("flat response", r["in_tune"])

    def test_unstable_or_absent_reading_is_not_bridged(self):
        for status, cents in (("unstable", 0), ("absent", None), ("airy", 0)):
            with self.subTest(status=status):
                m, r = self.response([(100, -20, "clean"), (200, cents, status), (400, 20, "clean")])
                self.assertIsNone(r["in_tune_pa"])
                self.assertIsNone(r["clean_interval_pa"])
                self.assertEqual(r["clean_intervals_pa"], [(100, 100), (400, 400)])
                self.assertIn("100–100, 400–400", fitter.format_pressure_response(m, P))

    def test_separate_takes_and_sweeps_do_not_create_a_clean_bridge(self):
        for field in ("take", "sweep"):
            with self.subTest(field=field):
                m, _ = self.response([(100, -20, "clean"), (400, 20, "clean")])
                setattr(m.observations[0], field, "up")
                setattr(m.observations[1], field, "down")
                self.assertIsNone(fitter.pressure_response(m)["C5"]["in_tune_pa"])

    def test_contradictory_repeat_blocks_an_otherwise_clean_run(self):
        m, _ = self.response([(100, -20, "clean"), (400, 20, "clean"), (200, None, "absent")])
        m.observations[-1].take = "another take"
        r = fitter.pressure_response(m)["C5"]
        self.assertIsNone(r["in_tune_pa"])
        self.assertEqual(r["clean_intervals_pa"], [(100, 100), (400, 400)])

    def test_order_and_missing_readings_interrupt_clean_runs(self):
        m, _ = self.response([(100, -20, "clean"), (400, 20, "clean"), (None, None, "clean")])
        # The interruption was stored last but occurred between the two valid readings.
        m.observations[1].order, m.observations[2].order = 2, 1
        self.assertIsNone(fitter.pressure_response(m)["C5"]["in_tune_pa"])

    def test_clean_region_after_a_break_remains_usable(self):
        _, r = self.response([(50, None, "absent"), (100, -20, "clean"), (400, 20, "clean")])
        self.assertAlmostEqual(r["in_tune_pa"], 200)
        self.assertEqual(r["clean_interval_pa"], (100, 400))

    def test_speaking_limits_restrict_supported_tuning(self):
        for limits in ((250, None), (None, 150), (None, 200), (250, 300)):
            with self.subTest(limits=limits):
                _, r = self.response([(100, -20, "clean"), (400, 20, "clean")], speaking_range={"C5": limits})
                self.assertIsNone(r["in_tune_pa"])
        _, r = self.response([(100, -20, "clean"), (400, 20, "clean")], speaking_range={"C5": (150, 250)})
        self.assertAlmostEqual(r["in_tune_pa"], 200)
        self.assertEqual(r["clean_interval_pa"], (150, 250))

    def test_invalid_speaking_limits_are_rejected(self):
        for limits in ((-1, None), (None, math.inf), (math.nan, None), (300, 200), (200, 200)):
            with self.subTest(limits=limits), self.assertRaisesRegex(ValueError, "speaking limits|onset pressure"):
                self.response([(100, -20, "clean"), (400, 20, "clean")], speaking_range={"C5": limits})

    def test_indistinguishable_log_pressures_do_not_divide_by_zero(self):
        _, r = self.response([(100, -20, "clean"), (math.nextafter(100, math.inf), 20, "clean")])
        self.assertIsNone(r["in_tune_pa"])

    def test_invalid_pressure_and_frequency_values_are_rejected(self):
        for field in ("p_pa", "hz", "target_hz"):
            for value in (0, -1, math.inf, math.nan):
                with self.subTest(field=field, value=value):
                    m, _ = self.response([(100, -20, "clean"), (400, 20, "clean")])
                    setattr(m.observations[0], field, value)
                    with self.assertRaisesRegex(ValueError, "finite and positive"):
                        fitter.pressure_response(m)

    def test_different_sensitivities_are_recovered_and_kept_apart(self):
        a = fitter.pressure_response(instrument("A", {"C5": 30.0, "G5": 45.0}, {"C5": 400.0, "G5": 450.0}))
        b = fitter.pressure_response(instrument("B", {"C5": 60.0, "G5": 45.0}, {"C5": 300.0, "G5": 450.0}))
        self.assertAlmostEqual(a["C5"]["slope_cents_per_doubling"], 30.0, delta=1e-9)
        self.assertAlmostEqual(b["C5"]["slope_cents_per_doubling"], 60.0, delta=1e-9)
        self.assertAlmostEqual(a["C5"]["in_tune_pa"], 400.0, delta=1e-6)
        self.assertAlmostEqual(b["C5"]["in_tune_pa"], 300.0, delta=1e-6)
        self.assertAlmostEqual(a["G5"]["slope_cents_per_doubling"], b["G5"]["slope_cents_per_doubling"], delta=1e-9)
        self.assertEqual(a["C5"]["clean_interval_pa"], (250.0, 700.0))

    def test_no_extrapolation_and_no_invented_readings(self):
        m = instrument("C", {"D5": 40.0}, {"D5": 1500.0})                      # in tune far above the readings
        m.observations += [meas.Observation("D5", None, 600.0, order=99), meas.Observation("D5", 800.0, None, status="absent", order=100)]
        r = fitter.pressure_response(m)["D5"]
        self.assertIsNone(r["in_tune_pa"])
        self.assertTrue(r["in_tune"].startswith("outside"))
        self.assertEqual((r["readings"], len(r["clean"]), r["by_status"]), (10, 8, {"clean": 9, "absent": 1}))

    def test_subholes_are_kept_apart_from_the_main_curve(self):
        r = fitter.pressure_response(instrument("D", {"A4": 20.0, "B4": 20.0, "C5": 30.0}, {"A4": 300.0, "B4": 300.0, "C5": 400.0}))
        self.assertEqual([r[n]["group"] for n in ("A4", "B4", "C5")], ["subhole", "subhole", "main"])

    def test_the_report_states_its_conditions(self):
        m = instrument("E", {"C5": 30.0}, {"C5": 400.0})
        text = fitter.format_pressure_response(m, P)
        self.assertIn("SYNTHETIC DATA", text)
        self.assertIn("room 21.0 °C", text)
        self.assertIn("estimate (design", text)                                 # the internal air is not presented as measured
        self.assertIn("blowing 250 to 700 Pa", text)
        m.session["internal_temp_c"] = 29.5
        self.assertIn("internal air 29.5 °C, measured", fitter.format_pressure_response(m, P))

    def test_the_fit_report_states_conditions_and_that_its_breath_curve_is_pooled(self):
        bodies = sy.round1_set(noise_cents=1.0, seed=2)
        fit = fitter.fit_bodies(bodies, P)
        self.assertEqual(fit.breath["bodies"], sorted(b.id for b in bodies))
        self.assertGreater(len(fit.breath["voicing_hashes"]), 1)
        text = fitter.format_report(fit)
        self.assertIn(f"pooled over {len(bodies)} bodies and {len(fit.breath['voicing_hashes'])} voicing(s)", text)
        self.assertIn("Conditions of this verdict: room", text)
        self.assertIn("Pa.", text)


if __name__ == "__main__":
    unittest.main()
