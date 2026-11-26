"""Plain-Python tests of the round bowl and its options (2026-11-26; no Blender): the bowl's maths on small grids
(ocarina_addon/bowl_math.py), the thumb offset of holes_layout, and the variant P4-bowl (presets/variants.toml).
The body itself is tested in tests/blender/test_round_bowl.py.
"""
import math
import pathlib
import sys
import types
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from ocarina_addon import bowl_math as bm, holes_layout as hl, kernel_bridge, presets  # noqa: E402
from test_holes_layout import layout_of  # noqa: E402

K = kernel_bridge.kernel()
P = kernel_bridge.load_params()
BOWL = types.SimpleNamespace(**K.voicing.BOWL_BUILD)             # the record's bowl fields: s3-yH7's


class TestBowlMaths(unittest.TestCase):
    def setUp(self):
        h = BOWL.bowl_grid_mm
        self.xs = np.round(np.arange(-6.0, 30.0 + 1e-9, h), 4)
        self.ys = np.round(np.arange(-20.0, 20.0 + 1e-9, h), 4)
        X, Y = np.meshgrid(self.xs, self.ys)
        self.X, self.Y = X, Y
        self.S = 6.0 + 0.002 * (X - 10.0) ** 2 - 0.003 * Y ** 2       # a domed outside, about 6 mm over the window's plane
        self.C = 0.8 + 0.01 * Y ** 2 * (X > 0)                         # the chamber's roof, lower under the window

    def field(self, **over):
        v = types.SimpleNamespace(**dict(vars(BOWL), **over))
        return bm.bowl_field(self.S, self.C, self.xs, self.ys, v, roof_exit_z=1.67, windway_pitch_deg=4.0, windway_width_mm=9.05)

    def test_the_floors_hold(self):
        B, rho, zr, strip = self.field()
        top = bm.smooth5((bm.TOP_X0_MM - self.X) / bm.TOP_FADE_MM)
        free = top == 0.0                                              # away from the upper edge, where B follows the outside
        self.assertGreaterEqual(float((B - self.C - BOWL.bowl_under_mm)[free].min()), -1e-9)     # bowl_under_mm over the chamber
        full = strip >= 1.0
        self.assertTrue(full.any())
        self.assertGreaterEqual(float((B - zr - BOWL.bowl_roof_mm)[full].min()), -1e-9)          # bowl_roof_mm over the windway
        # a deeper setting does not go through the floor either; outside the outline the bowl is only the smoothed outside
        B2, *_ = self.field(bowl_depth_mm=6.0)
        self.assertGreaterEqual(float((B2 - self.C - BOWL.bowl_under_mm)[free].min()), -1e-9)
        far = (rho > 1.3) & free & (strip == 0.0)
        Ss = bm.gauss(self.S, BOWL.bowl_smooth_mm, BOWL.bowl_grid_mm)
        self.assertLess(float(np.abs(B - Ss)[far & (Ss > self.C + BOWL.bowl_under_mm + 1.0)].max()), 0.05)   # the smoothed outside there

    def test_the_depth_follows_the_outline(self):
        rho = np.sqrt(((self.X - BOWL.bowl_centre_xw_mm) / BOWL.bowl_half_length_mm) ** 2 + (self.Y / BOWL.bowl_half_width_mm) ** 2)
        Ss = bm.gauss(self.S, BOWL.bowl_smooth_mm, BOWL.bowl_grid_mm)
        C = np.full_like(self.C, -50.0)                                 # no chamber floor: the depth alone
        Bd, *_ = bm.bowl_field(self.S, C, self.xs, self.ys, BOWL, 1.67, 4.0, 9.05)
        d = Ss - Bd
        j, i = int(np.argmin(np.abs(self.ys))), int(np.argmin(np.abs(self.xs - BOWL.bowl_centre_xw_mm)))     # the grid node at the centre
        self.assertAlmostEqual(float(d[j, i]), BOWL.bowl_depth_mm, delta=0.01)                  # D at the centre
        self.assertLess(float(np.abs(d[(rho >= 1.0) & (self.X > 6.0)]).max()), 2e-3)            # nothing on and beyond the outline
        # (the smooth maximum with the far chamber floor lifts everything by k^2 / 4 over the gap: under 0.001 mm here)

    def test_the_quintic_rim_ends_level(self):
        g0, d0, c0, e = 1.3, -0.8, 0.4, 1e-5
        q = bm.quintic
        self.assertAlmostEqual(q(g0, d0, c0, 0.0), g0, delta=1e-12)
        self.assertAlmostEqual((q(g0, d0, c0, e) - q(g0, d0, c0, -e)) / (2 * e), d0, delta=1e-6)
        self.assertAlmostEqual((q(g0, d0, c0, e) - 2 * g0 + q(g0, d0, c0, -e)) / e ** 2, c0, delta=1e-3)
        self.assertAlmostEqual(q(g0, d0, c0, 1.0), 0.0, delta=1e-12)                              # no depth left at the end,
        self.assertAlmostEqual((q(g0, d0, c0, 1 + e) - q(g0, d0, c0, 1 - e)) / (2 * e), 0.0, delta=1e-6)   # no jump of slope,
        self.assertAlmostEqual((q(g0, d0, c0, 1 + e) - 2 * q(g0, d0, c0, 1.0) + q(g0, d0, c0, 1 - e)) / e ** 2, 0.0, delta=1e-3)   # nor of curvature

    def test_the_flow_is_capped_at_its_share_of_the_room(self):
        reach = np.concatenate([np.linspace(2.0, 30.0, 120), np.linspace(30.0, 2.0, 120)])
        out = bm.flow_out(reach, BOWL.bowl_flow_out_mm, BOWL.bowl_flow_cap)
        self.assertTrue(np.all(out <= BOWL.bowl_flow_cap * reach + 1e-12))                        # 55 % of the way to the outline at most
        self.assertTrue(np.all(out <= BOWL.bowl_flow_out_mm + 1e-12))
        self.assertAlmostEqual(float(out[np.argmax(reach)]), BOWL.bowl_flow_out_mm, delta=1e-9)  # the full flow where there is room
        self.assertAlmostEqual(BOWL.bowl_flow_cap, 0.55)

    def test_the_throat_areas_of_a_ring_stack(self):
        sq = np.array([[-2.0, -2.0], [2.0, -2.0], [2.0, 2.0], [-2.0, 2.0]])
        straight = [np.column_stack([sq, np.full(4, z)]) for z in (-1.0, 0.4, 2.0, 4.0, 6.0)]
        A = bm.throat_areas(straight, [0.0, 1.0, 3.0, 4.0])
        self.assertTrue(np.allclose(A, 16.0))
        flare = [np.column_stack([sq * (1.0 + 0.25 * max(z, 0.0)), np.full(4, z)]) for z in (-1.0, 0.0, 2.0, 4.0)]
        A = bm.throat_areas(flare, [0.0, 1.0, 2.0, 3.0, 4.0])
        self.assertTrue(np.all(np.diff(A) > 0))
        self.assertAlmostEqual(float(A[2]), 16.0 * 1.5 ** 2, delta=1e-9)                          # on a ring: its own area
        self.assertAlmostEqual(float(A[1]), 16.0 * 1.25 ** 2, delta=1.0)                         # between rings: the chords
        t = K.voicing.effective_wall_mm(np.linspace(0.0, 4.0, 81), bm.throat_areas(flare, np.linspace(0.0, 4.0, 81)), 16.0)
        self.assertLess(t, 4.0)
        self.assertAlmostEqual(K.voicing.effective_wall_mm(np.linspace(0.0, 4.0, 81), bm.throat_areas(straight, np.linspace(0.0, 4.0, 81)), 16.0),
                               4.0, delta=1e-12)


class TestThumbOffsets(unittest.TestCase):
    def test_none_by_default(self):
        plain, _, _ = layout_of("P4")
        self.assertFalse(any("MOVED THUMB HOLE" in m for m in plain.messages))
        same, _, _ = layout_of("P4", thumb_offsets_mm=())
        self.assertEqual([(h.name, h.s_mm, h.w_mm) for h in same.holes], [(h.name, h.s_mm, h.w_mm) for h in plain.holes])

    def test_a_thumb_hole_moves_and_is_marked(self):
        plain, cav, sz = layout_of("P4")
        moved = hl.make_layout(cav, dict(presets.get_preset("P4"), thumb_offsets_mm={"L_thumb": (-4.0, 0.0)}), sz.holes.solutions["print"])
        a, b = plain.by_name(), moved.by_name()
        self.assertAlmostEqual(b["L_thumb"].s_nominal_mm, a["L_thumb"].s_nominal_mm - 4.0, delta=1e-9)
        self.assertAlmostEqual(b["L_thumb"].w_nominal_mm, a["L_thumb"].w_nominal_mm, delta=1e-9)
        self.assertGreater(math.dist(a["L_thumb"].centre, b["L_thumb"].centre), 3.5)
        for n in a:
            if n != "L_thumb":
                self.assertLess(math.dist(a[n].centre, b[n].centre), 1e-9, n)          # nothing else moves
        self.assertTrue(any(m.startswith("MOVED THUMB HOLE (an ergonomic change): L_thumb moved -4 mm") for m in moved.messages))

    def test_only_thumb_holes(self):
        _, cav, sz = layout_of("P4")
        with self.assertRaises(ValueError):
            hl.make_layout(cav, dict(presets.get_preset("P4"), thumb_offsets_mm={"L_index": (1.0, 0.0)}), sz.holes.solutions["print"])


class TestVariant(unittest.TestCase):
    def test_the_presets_stay_and_the_variant_is_found(self):
        self.assertEqual(sorted(presets.load_presets()), ["P0", "P1", "P2", "P3", "P4", "S0"])
        v = presets.get_preset("P4-bowl")
        p4 = presets.get_preset("P4")
        self.assertEqual((v["id"], v["base"]), ("P4-bowl", "P4"))
        self.assertEqual(v["width"], p4["width"])
        self.assertEqual({k: v[k] for k in ("rating", "windway_length_mm", "port_angle_deg", "windway_pitch_deg", "stub_pitch_deg",
                                             "neck_tilt_deg", "wall_front_less_mm", "wall_back_more_mm", "wall_refine_mm", "window_cut")},
                         dict(rating="soft", windway_length_mm=57.0, port_angle_deg=20.0, windway_pitch_deg=4.0, stub_pitch_deg=4.0,
                              neck_tilt_deg=6.0, wall_front_less_mm=1.0, wall_back_more_mm=2.0, wall_refine_mm=[30.0, 24.0], window_cut="bowl"))
        self.assertNotIn("thumb_offsets_mm", v)                                          # the move is the owner's to set
        with self.assertRaises(ValueError):
            presets.get_preset("P9")

    def test_rule_values_of_a_variant(self):
        self.assertIs(presets.params_for(presets.get_preset("P4"), P), P)               # a preset changes no rule value
        Q = presets.params_for(presets.get_preset("P4-bowl"), P)
        self.assertEqual(Q["voicing_rules"]["windway_length_mm"], 57.0)
        self.assertEqual(P["voicing_rules"]["windway_length_mm"], 30.0)                 # the rule table itself is untouched
        v = K.voicing.make_voicing(80.0, "soft", params=Q, build={"window_cut": "bowl"})
        self.assertEqual(v.window_cut, "bowl")
        self.assertAlmostEqual(v.window_length_mm, 8.89, delta=1e-9)
        self.assertAlmostEqual(v.window_area_mm2, 62.84, delta=0.01)

    def test_a_variant_needs_a_base(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = pathlib.Path(d) / "v.toml"
            path.write_text('schema = "ocarina-preset-variants-v1"\n[X]\nbase = "P7"\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                presets.load_variants(path)


if __name__ == "__main__":
    unittest.main()
