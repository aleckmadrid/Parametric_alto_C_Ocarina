"""Plain-Python tests: a variant build (P4-bowl) sized from fitted constants for the voicing that is really built.

Every constant set here is invented on top of the SYNTHETIC example file: nothing describes a printed body.
"""
import pathlib
import sys
import types
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ocarina_addon import headless, kernel_bridge, presets  # noqa: E402

K = kernel_bridge.kernel()
BOWL_HASH = "bcdd90905c01"          # P4-bowl at 80 cm3, soft (prompts/addon-v1-notes.md, addon_checks/P4-bowl-80-zb4.md)


def synthetic_cal(**voicings):
    cal = K.calibration.load_calibration(ROOT / "calibration" / "synthetic-fitted-constants.toml")
    assert cal.synthetic
    cal.voicings = {h: {"eta_w": eta} for h, eta in voicings.items()}
    return cal


class TestResolvedLookup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.P = kernel_bridge.load_params()
        cls.preset = presets.get_preset("P4-bowl")
        cls.v = presets.resolve_voicing(cls.preset, 80.0, cls.P)

    def size(self, cal, preset=None, walls=None, **kw):
        info = {}
        fn = presets.calibrated_sizing_fn(cal, preset or self.preset, 80.0, self.P, info=info, **kw)
        return fn(None, walls), info

    def test_the_resolved_record_is_the_bowl_that_is_built(self):
        self.assertEqual(self.v.version_hash, BOWL_HASH)
        self.assertEqual((self.v.window_cut, self.v.rating, self.v.windway_pitch_deg), ("bowl", "soft", 4.0))

    def test_the_handover_reproduction_selects_the_bowl_entry(self):
        # the handover's reproduction: 0.77 for the bowl's hash came back as the fallback (0.860), cut "ellipse"
        sz, info = self.size(synthetic_cal(**{BOWL_HASH: 0.77}))
        self.assertEqual((info["eta_w"], info["eta_w_source"], info["voicing_hash"]), (0.77, "measured", BOWL_HASH))
        self.assertEqual((sz.voicing.window_cut, sz.eta_w_source, sz.eta_w), ("bowl", "measured", 0.77))

    def test_another_bowl_does_not_take_that_entry(self):
        other = dict(self.preset, bowl_depth_mm=2.0)
        sz, info = self.size(synthetic_cal(**{BOWL_HASH: 0.77}), preset=other)
        self.assertNotEqual(sz.voicing.version_hash, BOWL_HASH)
        self.assertEqual(info["eta_w_source"], "fallback")

    def test_a_known_window_is_kept_whatever_eta_w(self):
        a, _ = self.size(synthetic_cal(**{BOWL_HASH: 0.77}))
        b, _ = self.size(synthetic_cal(**{BOWL_HASH: 0.95}))
        for name in ("version_hash", "window_area_mm2", "window_length_mm", "window_width_mm"):
            self.assertEqual(getattr(a.voicing, name), getattr(b.voicing, name), name)
        self.assertEqual((a.v0_cm3, b.v0_cm3), (80.0, 80.0))
        self.assertLess(a.a4_error_cents, b.a4_error_cents)          # less efficient: A4 lower at the same volume
        self.assertGreater(a.range_ratio, b.range_ratio)              # and the holes' conductance ratio higher

    def test_an_unknown_bowl_keeps_its_window_and_says_fallback(self):
        cal = synthetic_cal()
        sz, info = self.size(cal)
        self.assertEqual((info["eta_w_source"], info["voicing_hash"], sz.eta_w), ("fallback", BOWL_HASH, cal.eta_w_fallback))
        self.assertEqual(sz.voicing.window_area_mm2, self.v.window_area_mm2)
        self.assertTrue(any("never measured" in w for w in info["warnings"]))
        self.assertTrue(info["synthetic"])

    def test_explicit_rating_wins_over_the_variants(self):
        loud = presets.resolve_voicing(self.preset, 80.0, self.P, rating="medium")
        self.assertEqual(loud.rating, "medium")
        self.assertNotEqual(loud.version_hash, BOWL_HASH)
        self.assertNotEqual(loud.window_length_mm, self.v.window_length_mm)
        sz, _ = self.size(synthetic_cal(**{BOWL_HASH: 0.77}), rating="medium")
        self.assertEqual((sz.voicing.rating, sz.eta_w_source), ("medium", "fallback"))

    def test_a_voicing_and_the_arguments_that_make_one_are_refused(self):
        with self.assertRaisesRegex(ValueError, "not both"):
            K.calibration.size_body_from_calibration(synthetic_cal(), 80.0, "soft", voicing=self.v, params=self.P)

    def test_a_calibrated_record_cannot_be_rehashed_after_the_lookup(self):
        # the old build path: a record looked up for the plain voicing, the bowl put in afterwards
        plain, _ = K.calibration.size_body_from_calibration(synthetic_cal(), 80.0, "soft", shape="P4-bowl",
                                                            params=presets.params_for(self.preset, self.P))
        self.assertEqual(plain.voicing.window_cut, "ellipse")
        with self.assertRaisesRegex(ValueError, "looked up for voicing"):
            presets.resolve_sizing(self.preset, plain)
        prior = K.sizing.size_body(80.0, "soft", params=presets.params_for(self.preset, self.P))
        self.assertEqual(presets.resolve_sizing(self.preset, prior).voicing.version_hash, BOWL_HASH)   # a prior record still can


class TestCalibratedWalls(unittest.TestCase):
    """The holes of a calibrated variant follow the walls of each call and the fitted hole constants."""

    @classmethod
    def setUpClass(cls):
        cls.P = kernel_bridge.load_params()
        cls.preset = presets.get_preset("P4-bowl")
        cls.names = [h["name"] for h in cls.P["fingering"]["holes"]]

    def rows(self, cal, walls=None):
        sz = presets.calibrated_sizing_fn(cal, self.preset, 80.0, self.P)(None, walls)
        return sz, {r.name: r for r in sz.holes.solutions["fitted"]}

    def test_a_thicker_thumb_wall_gives_a_wider_thumb_hole(self):
        cal = synthetic_cal(**{BOWL_HASH: 0.77})
        walls = {n: (6.0 if n.endswith("thumb") else 3.0) for n in self.names}
        _, nominal = self.rows(cal)
        _, uneven = self.rows(cal, walls)
        for n in self.names:
            self.assertAlmostEqual(uneven[n].wall_mm, walls[n], delta=1e-12, msg=n)     # the measured wall, not 4 mm
        self.assertGreater(uneven["R_thumb"].d_mm, nominal["R_thumb"].d_mm)
        self.assertLess(uneven["L_index"].d_mm, nominal["L_index"].d_mm)

    def test_the_fitted_hole_constants_move_the_holes_and_the_template(self):
        base = synthetic_cal(**{BOWL_HASH: 0.77})
        more_k = synthetic_cal(**{BOWL_HASH: 0.77})
        more_k.k_hole = base.k_hole * 1.15
        offset = synthetic_cal(**{BOWL_HASH: 0.77})
        offset.hole_offset_mm = base.hole_offset_mm + 0.2
        sz0, r0 = self.rows(base)
        _, r1 = self.rows(more_k)
        sz2, _ = self.rows(offset)
        for n in self.names:
            if r0[n].tube_mm == 0.0 and r1[n].tube_mm == 0.0:
                self.assertGreater(r1[n].d_mm, r0[n].d_mm, n)          # a longer end correction needs a wider hole
        t0 = K.measurements.template_from_sizing(sz0, "x", shape="P4-bowl", key="fitted")
        t2 = K.measurements.template_from_sizing(sz2, "x", shape="P4-bowl", key="fitted")
        self.assertEqual(t0.voicing_hash, BOWL_HASH)
        for h0, h2 in zip(t0.holes, t2.holes):
            self.assertAlmostEqual(h0.d_design_m - h2.d_design_m, 0.2e-3, delta=1e-12)   # drawn 0.2 mm smaller


class TestCalibrationContext(unittest.TestCase):
    """What else a fitted constant of P4-bowl is matched on (presets.calibration_context)."""

    @classmethod
    def setUpClass(cls):
        cls.P = kernel_bridge.load_params()
        cls.preset = presets.get_preset("P4-bowl")
        cls.ctx = presets.calibration_context(cls.preset)

    def cal_measured_here(self):
        cal = synthetic_cal(**{BOWL_HASH: 0.88})
        cal.voicings[BOWL_HASH]["voicing_context"] = self.ctx["voicing_context"]
        cal.psi["P4-bowl"] = {h["name"]: 1.02 for h in self.P["fingering"]["holes"]}
        cal.layouts["P4-bowl"] = self.ctx["layout"]
        return cal

    def size(self, preset, cal=None, **kw):
        info = {}
        presets.calibrated_sizing_fn(cal or self.cal_measured_here(), preset, 80.0, self.P, info=info, **kw)(None)
        return info

    def test_the_same_build_matches_exactly(self):
        info = self.size(self.preset)
        self.assertEqual((info["eta_w_match"], info["psi_match"], info["eta_w"]), ("exact", "exact", 0.88))
        self.assertEqual(self.ctx["window_throat"], "wall")

    def test_another_pocket_margin_is_not_the_measured_voicing(self):
        moved = dict(self.preset, pocket_back_margin_mm=0.3)          # not in the voicing hash
        self.assertEqual(presets.resolve_voicing(moved, 80.0, self.P).version_hash, BOWL_HASH)
        self.assertEqual(presets.calibration_context(moved)["layout"], self.ctx["layout"])
        info = self.size(moved)
        self.assertEqual((info["eta_w_match"], info["eta_w_source"], info["psi_match"]), ("fallback", "fallback", "exact"))
        self.assertEqual(self.size(moved, allow_transfer=True)["eta_w_match"], "transfer")

    def test_a_moved_thumb_hole_drops_the_position_factors_only(self):
        moved = dict(self.preset, thumb_offsets_mm={"L_thumb": [-6.0, 0.0]})
        ctx = presets.calibration_context(moved)
        self.assertEqual(ctx["voicing_context"], self.ctx["voicing_context"])
        info = self.size(moved)
        self.assertEqual((info["eta_w_match"], info["psi_match"]), ("exact", "other layout"))
        self.assertEqual(len(info["psi_defaulted_to_1"]), len(self.P["fingering"]["holes"]))

    def test_names_do_not_count_and_an_edited_shell_does(self):
        self.assertEqual(presets.calibration_context(dict(self.preset, name="x", note="y")), self.ctx)
        edited = presets.calibration_context(self.preset, edited_shell=True)
        self.assertNotEqual(edited["voicing_context"], self.ctx["voicing_context"])
        self.assertNotEqual(edited["layout"], self.ctx["layout"])
        self.assertEqual(self.size(self.preset, edited_shell=True)["eta_w_match"], "fallback")

    def test_an_effective_throat_is_refused_with_wall_constants(self):
        with self.assertRaisesRegex(ValueError, "wall as its throat"):
            self.size(dict(self.preset, window_throat_mm=2.403))
        self.assertEqual(presets.calibration_context(dict(self.preset, window_throat_mm=2.403))["window_throat"], "effective")


class TestHeadlessRating(unittest.TestCase):
    def test_body_without_rating_leaves_the_presets(self):
        seen = {}

        def fake(preset, v0, **kw):
            seen.update(kw)
            raise RuntimeError("stop")
        api = types.SimpleNamespace(build_body=fake)          # the real api imports Blender
        with mock.patch.dict(sys.modules, {"ocarina_addon.api": api}), self.assertRaisesRegex(RuntimeError, "stop"):
            headless.main(["body", "--preset", "P4-bowl", "--out", "unused"])
        self.assertIsNone(seen["rating"])
        self.assertIsNone(seen["calibration"])


if __name__ == "__main__":
    unittest.main()
