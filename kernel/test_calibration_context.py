"""Calibration compatibility beyond the voicing hash: the voicing context, the hole layout and the model's convention.

All bodies and constants here are SYNTHETIC (kernel/synthetic.py); the contexts are invented labels.
"""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import calibration as cal_mod  # noqa: E402
import config  # noqa: E402
import fitter  # noqa: E402
import measurements as meas  # noqa: E402
import sizing  # noqa: E402
import synthetic as sy  # noqa: E402

P = config.load_params()
CTX = dict(voicing_context="aaaaaaaaaaaa", layout="bbbbbbbbbbbb", window_throat="wall")


class TestContexts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bodies = sy.round1_set(noise_cents=1.0, seed=2)
        for b in cls.bodies:
            b.context = dict(CTX, layout=f"layout-{b.shape}")
        cls.fit = fitter.fit_bodies(cls.bodies, P)
        cls.cal = cal_mod.calibration_from_fit(cls.fit, cls.bodies, P)
        cls.h = cls.bodies[0].voicing_hash

    def test_the_fit_keeps_the_contexts_its_bodies_share(self):
        self.assertEqual(self.cal.voicings[self.h]["voicing_context"], CTX["voicing_context"])
        self.assertEqual(self.cal.layouts, {s: f"layout-{s}" for s in self.cal.psi})
        self.assertEqual(self.cal.model, {"window_throat": "wall"})

    def test_bodies_of_different_contexts_are_not_pooled(self):
        bodies = sy.round1_set(noise_cents=1.0, seed=2)
        hashes = [b.voicing_hash for b in bodies]
        first = next(i for i, h in enumerate(hashes) if hashes.count(h) > 1)     # one of the copies of one voicing
        for i, b in enumerate(bodies):
            b.context = dict(CTX, voicing_context="x" if i == first else "y")
        with self.assertRaisesRegex(ValueError, "different contexts"):
            cal_mod.calibration_from_fit(fitter.fit_bodies(bodies, P), bodies, P)
        legacy = sy.round1_set(noise_cents=1.0, seed=2)           # copies of one voicing, only one with a context: legacy
        legacy[first].context = dict(CTX)
        cal = cal_mod.calibration_from_fit(fitter.fit_bodies(legacy, P), legacy, P)
        self.assertNotIn("voicing_context", cal.voicings[legacy[first].voicing_hash])

    def test_the_match_statuses(self):
        eta = self.cal.voicings[self.h]["eta_w"]
        m = self.cal.eta_w_match
        self.assertEqual(m(self.h, CTX["voicing_context"]), (eta, "exact"))
        self.assertEqual(m(self.h, None), (eta, "legacy"))
        self.assertEqual(m(self.h, "zzzzzzzzzzzz"), (self.cal.eta_w_fallback, "fallback"))
        self.assertEqual(m(self.h, "zzzzzzzzzzzz", allow_transfer=True), (eta, "transfer"))
        self.assertEqual(m("000000000000", CTX["voicing_context"]), (self.cal.eta_w_fallback, "fallback"))
        self.assertEqual(self.cal.eta_w_for(self.h, "zzzzzzzzzzzz"), (self.cal.eta_w_fallback, "fallback"))
        self.assertEqual(self.cal.psi_match("P0", "layout-P0"), "exact")
        self.assertEqual(self.cal.psi_match("P0", None), "legacy")
        self.assertEqual(self.cal.psi_match("P0", "layout-moved"), "other layout")
        self.assertEqual(self.cal.psi_match("P9", "layout-P0"), "unfitted")

    def test_another_context_sizes_with_the_fallback_and_psi_1(self):
        v0 = self.bodies[0].target_v0_cm3
        exact, i1 = cal_mod.size_body_from_calibration(self.cal, v0, shape="P0", params=P, context=dict(CTX, layout="layout-P0"))
        other, i2 = cal_mod.size_body_from_calibration(self.cal, v0, shape="P0", params=P,
                                                       context=dict(CTX, voicing_context="pocket-moved", layout="thumb-moved"))
        self.assertEqual((i1["eta_w_match"], i1["psi_match"], i1["eta_w_source"]), ("exact", "exact", "measured"))
        self.assertEqual((i2["eta_w_match"], i2["psi_match"], i2["eta_w_source"]), ("fallback", "other layout", "fallback"))
        self.assertIn("voicing measured in another voicing context: eta_w_fallback used", i2["warnings"])
        self.assertFalse(i2["shape_known"])
        n = len(P["fingering"]["holes"])
        psi_1 = sizing.size_body(v0, voicing=other.voicing, eta_w=self.cal.eta_w_fallback, params=P, ks={"fitted": self.cal.k_hole},
                                 psi=[1.0] * n, volume_factor=self.cal.volume_factor, hole_offset_mm=self.cal.hole_offset_mm)
        self.assertEqual([r.d_mm for r in other.holes.solutions["fitted"]], [r.d_mm for r in psi_1.holes.solutions["fitted"]])
        self.assertNotEqual([r.d_mm for r in exact.holes.solutions["fitted"]][:4], [r.d_mm for r in psi_1.holes.solutions["fitted"]][:4])

    def test_an_effective_throat_needs_constants_fitted_for_it(self):
        v0 = self.bodies[0].target_v0_cm3
        with self.assertRaisesRegex(ValueError, "wall as its throat"):
            cal_mod.size_body_from_calibration(self.cal, v0, shape="P0", params=P, throat_mm=2.4)
        legacy = cal_mod.load_calibration(config.ROOT / "calibration" / "synthetic-fitted-constants.toml")
        self.assertEqual(legacy.model, {})                                  # no [model]: the wall, assumed
        with self.assertRaisesRegex(ValueError, "wall as its throat"):
            cal_mod.size_body_from_calibration(legacy, v0, shape="P0", params=P, throat_mm=2.4)

    def test_files_keep_the_contexts_and_old_files_stay_legacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "c.toml"
            cal_mod.write_calibration(path, self.cal)
            back = cal_mod.load_calibration(path)
            self.assertEqual(back.voicings[self.h]["voicing_context"], CTX["voicing_context"])
            self.assertEqual((back.layouts, back.model), (self.cal.layouts, self.cal.model))
            t = meas.template_from_sizing(sizing.size_body(80.0, params=P), "x", context=CTX)
            mp = pathlib.Path(tmp) / "m.toml"
            meas.write_measurement_file(mp, t, blank=True)
            self.assertEqual(meas.load_measurement(mp, allow_incomplete=True).context, CTX)
        legacy = cal_mod.load_calibration(config.ROOT / "calibration" / "synthetic-fitted-constants.toml")
        self.assertEqual(legacy.layouts, {})
        h = next(iter(legacy.voicings))
        self.assertEqual(legacy.eta_w_match(h, CTX["voicing_context"])[1], "legacy")
        old = meas.load_measurement(config.ROOT / "measurements" / "example-synthetic-P0-80.toml")
        self.assertEqual(old.context, {})


if __name__ == "__main__":
    unittest.main()
