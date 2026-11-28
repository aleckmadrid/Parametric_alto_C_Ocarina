"""The tuning evidence page (ocarina_addon/evidence.py), on SYNTHETIC records only. No Blender."""
import dataclasses
import pathlib
import tempfile
import unittest

from ocarina_addon import evidence, kernel_bridge

K = kernel_bridge.kernel()
M = K.measurements
ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "measurements" / "example-synthetic-P0-80.toml"


def body(**changes):
    """The repository's synthetic example with a few invented paired readings."""
    m = M.load_measurement(EXAMPLE)
    hz = {n.name: n.target_hz for n in m.notes}
    obs = [M.Observation("A4", 150.0, hz["A4"] * 0.99, order=1), M.Observation("A4", 300.0, hz["A4"] * 1.01, order=2),
           M.Observation("A4", 500.0, hz["A4"] * 1.03, status="unstable", order=3),
           M.Observation("C5", 200.0, hz["C5"], order=4), M.Observation("C5", 900.0, None, status="absent", order=5)]
    return dataclasses.replace(m, observations=obs, speaking_range={"A4": (120.0, None)}, **changes)


class TestTuningEvidence(unittest.TestCase):
    def test_prediction_measurement_and_geometry_are_separate_sections(self):
        page = evidence.render_html(K, body())
        order = [page.index(h) for h in ("Predicted: the design targets", "Measured: the takes", "Pressure and pitch, per fingering",
                                         "Geometry checks")]
        self.assertEqual(order, sorted(order))
        self.assertIn("No check report was given", page)                 # nothing is assumed about the geometry
        self.assertIn("not used to size holes", page)

    def test_synthetic_is_said_everywhere(self):
        m = body()
        page = evidence.render_html(K, m)
        self.assertIn("<title>SYNTHETIC ", page)
        self.assertEqual(page.count(">SYNTHETIC</text>"), page.count("<svg"))   # every figure
        self.assertNotIn("SYNTHETIC", evidence.render_html(K, dataclasses.replace(m, synthetic=False)))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(evidence.write_evidence(EXAMPLE, tmp).name.startswith("SYNTHETIC-"))

    def test_an_unstable_reading_is_drawn_and_not_fitted_and_a_missing_one_is_a_cross(self):
        m = body()
        s = K.fitter.pressure_response(m)["A4"]
        self.assertEqual(len(s["clean"]), 2)                             # the unstable reading is not in the fit
        a4 = evidence.pressure_svg(K, m, "A4", s, (120.0, 900.0))
        self.assertEqual(a4.count(evidence.STATUS_COLORS["unstable"]), 1)
        self.assertIn("unstable: 500 Pa", a4)
        self.assertIn("onset 120", a4)
        self.assertIn("break not seen", a4)                              # a limit that was not seen is not invented
        c5 = evidence.pressure_svg(K, m, "C5", K.fitter.pressure_response(m)["C5"], (120.0, 900.0))
        self.assertIn("absent: 900 Pa, no pitch", c5)
        self.assertIn("no fit", c5)

    def test_the_subhole_notes_are_grouped_apart(self):
        groups = evidence._groups(K, body())
        self.assertEqual([n.name for n in groups[0][1]], ["A4", "B4"])
        self.assertEqual(groups[1][1][0].name, "C5")
        page = evidence.render_html(K, body())
        self.assertLess(page.index("<h3>A4, B4 (subholes)</h3>"), page.index("<h3>C5 to F6</h3>"))

    def test_a_file_without_paired_readings_says_so(self):
        self.assertIn("no paired pressure and pitch readings", evidence.render_html(K, M.load_measurement(EXAMPLE)))

    def test_a_number_that_is_not_finite_fails_with_the_fingering(self):
        m = body()
        m.observations[0].p_pa = float("nan")
        with self.assertRaisesRegex(ValueError, "A4"):
            evidence.render_html(K, m)

    def test_the_check_report_is_shown_as_geometry_only(self):
        checks = dict(voicing_hash="other", checks=[dict(name="wall", status="pass", message=""),
                                                    dict(name="hole_limits", status="fail", expected=True, message="pad limit")])
        page = evidence.render_html(K, body(), checks)
        self.assertIn("1 checks passed", page)
        self.assertIn("fail (expected)", page)
        self.assertIn("another voicing than the measurement file", page)


if __name__ == "__main__":
    unittest.main()
