"""Plain-Python tests of ocarina_addon/holes_layout.py (no Blender).

The cavity is the analytic surface of cavity_math at the scale of the 80 cm3 body. The real build solves
the scale on the mesh, which differs by less than 0.1 %.
"""
import math
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ocarina_addon import cavity_math, ergonomics as eg, holes_layout as hl, kernel_bridge, presets  # noqa: E402

K = kernel_bridge.kernel()
P = kernel_bridge.load_params()


def cavity_of(preset: dict, v0: float):
    sz = K.sizing.size_body(v0, params=P)
    cav = cavity_math.Cavity.from_preset(preset)
    cav.scale = cav.scale_for_volume(sz.cavity_volume_for_mesh_cm3 * 1000.0)
    cav.snap_port_to_grid(129, 128)
    return cav, sz


_CACHE = {}


def layout_of(name: str, v0: float = 80.0, rows=None, **overrides):
    """(layout, cavity, kernel sizing). Layouts with the kernel's own rows are cached: a layout takes a few seconds."""
    key = (name, v0, tuple(sorted(overrides.items())))
    if rows is None and key in _CACHE:
        return _CACHE[key]
    preset = dict(presets.get_preset(name), **overrides)
    cav, sz = cavity_of(preset, v0)
    out = hl.make_layout(cav, preset, rows if rows is not None else sz.holes.solutions["print"]), cav, sz
    if rows is None:
        _CACHE[key] = out
    return out


def metrics(lay):
    return eg.layout_metrics({h.name: dict(centre=eg.body_to_player(h.centre), axis=eg.body_to_player(h.axis), d_mm=h.d_mm)
                              for h in lay.holes})


def bigger(rows, **scale):
    """Kernel rows with some diameters multiplied (to force an edge-gap conflict)."""
    return [types.SimpleNamespace(name=r.name, d_mm=r.d_mm * scale.get(r.name, 1.0), tube_mm=r.tube_mm, wall_mm=r.wall_mm) for r in rows]


class TestSubholeRule(unittest.TestCase):
    """Owner decision of 2026-11-15: sub1 9.5 mm from L_ring, sub2 7.5 mm from R_middle, along the hand-line normal."""

    def test_slide_length_and_direction(self):
        for name in ("P1", "P2", "P3", "P4"):
            lay, _, _ = layout_of(name)
            m = metrics(lay)
            self.assertEqual(m["sub1"]["parent"], "L_ring", name)
            self.assertEqual(m["sub2"]["parent"], "R_middle", name)
            self.assertAlmostEqual(m["sub1"]["dist_3d"], 9.5, delta=1e-4, msg=name)
            self.assertAlmostEqual(m["sub2"]["dist_3d"], 7.5, delta=1e-4, msg=name)
            self.assertAlmostEqual(m["sub1"]["off_normal_deg"], 0.0, delta=0.01, msg=name)
            self.assertAlmostEqual(m["sub2"]["off_normal_deg"], 0.0, delta=0.01, msg=name)
            self.assertGreater(m["sub1"]["forward"], 9.0, name)             # toward the fingertips, never behind the finger
            self.assertGreater(m["sub2"]["forward"], 7.0, name)
            self.assertEqual(lay.subholes["sub1"]["parent"], "L_ring")
            self.assertAlmostEqual(lay.subholes["sub1"]["slide_mm"], 9.5, delta=1e-4)

    def test_sub1_is_toward_the_player_and_sub2_away(self):
        for name in ("P1", "P2", "P3", "P4"):
            by = layout_of(name)[0].by_name()
            self.assertLess(by["sub1"].centre[1], by["L_ring"].centre[1], name)       # +Y is away from the player
            self.assertGreater(by["sub2"].centre[1], by["R_middle"].centre[1], name)
            for sub in ("sub1", "sub2"):
                self.assertEqual(by[sub].deck, "top")
                self.assertLess(by[sub].tilt_deg, hl.MAX_TILT_DEG)

    def test_edge_gap_holds(self):
        for name in ("P1", "P2", "P3", "P4"):
            lay, _, _ = layout_of(name)
            self.assertGreaterEqual(lay.min_gap_mm, hl.MIN_GAP_MM - 1e-6, f"{name}: {lay.gaps[0]}")
            self.assertFalse([m for m in lay.messages if m.startswith("edge gap")], name)

    def test_parent_and_slide_are_preset_values(self):
        lay, _, _ = layout_of("P1", sub1_slide_mm=10.5, sub2_parent="R_ring", sub2_slide_mm=8.0)
        m = metrics(lay)
        self.assertAlmostEqual(m["sub1"]["dist_3d"], 10.5, delta=1e-4)
        self.assertEqual(lay.subholes["sub2"]["parent"], "R_ring")
        by = lay.by_name()
        self.assertAlmostEqual(math.dist(by["sub2"].centre, by["R_ring"].centre), 8.0, delta=1e-4)
        with self.assertRaises(ValueError):
            layout_of("P1", sub1_parent="L_thumb")
        with self.assertRaises(ValueError):
            layout_of("P1", sub1_slide_mm=12.0)                # above the largest slide, 11 mm

    def test_a_slide_is_lengthened_to_keep_the_gap_and_never_turned_around(self):
        _, _, sz = layout_of("P1")
        rows = bigger(sz.holes.solutions["print"], L_ring=1.12)               # a larger L_ring hole: 9.5 mm is no longer enough
        lay, _, _ = layout_of("P1", rows=rows)
        m = metrics(lay)
        self.assertGreater(m["sub1"]["dist_3d"], 9.5 + 0.2)
        self.assertLessEqual(m["sub1"]["dist_3d"], hl.SUBHOLE_SLIDE_MAX_MM + 1e-6)
        self.assertAlmostEqual(m["sub1"]["off_normal_deg"], 0.0, delta=0.01)   # still straight forward
        self.assertGreater(m["sub1"]["forward"], 0.0)
        self.assertGreaterEqual(lay.min_gap_mm, hl.MIN_GAP_MM - 1e-6)
        self.assertTrue([msg for msg in lay.messages if msg.startswith("sub1: the slide from L_ring was lengthened")], lay.messages)

    def test_the_slide_stops_at_the_largest_slide_and_the_rest_is_reported(self):
        _, _, sz = layout_of("P1")
        lay, _, _ = layout_of("P1", rows=bigger(sz.holes.solutions["print"], L_ring=1.6))
        self.assertAlmostEqual(lay.subholes["sub1"]["slide_mm"], hl.SUBHOLE_SLIDE_MAX_MM, delta=1e-4)
        self.assertLess(lay.min_gap_mm, hl.MIN_GAP_MM)
        self.assertTrue([msg for msg in lay.messages if msg.startswith("edge gap")])

    def test_subholes_are_not_limited_sideways_without_a_message(self):
        # the subhole is placed in the plan view: its slide has the full length, whatever the 35 % limit does to finger holes
        for name in ("P1", "P2", "P3", "P4"):
            lay, _, _ = layout_of(name)
            self.assertFalse([c for c in lay.clamps if c[0].startswith("sub")])
            for sub, rule in lay.subholes.items():
                self.assertGreaterEqual(rule["slide_mm"], rule["slide_nominal_mm"] - 1e-6)


class TestTemplateAndOverlap(unittest.TestCase):
    def test_the_template_is_the_miracle_spacing(self):
        t = hl._template_nominal()
        self.assertAlmostEqual(math.dist(t["L_pinky"], t["L_ring"]), 17.14, delta=0.01)       # Miracle_M.md section 4.2
        self.assertAlmostEqual(t["R_pinky"][0] - t["L_pinky"][0], 104.2, delta=0.01)
        self.assertNotIn("sub1", t)                                                            # subholes are placed by rule

    def test_overlap_slides_each_hand_along_its_own_line_and_keeps_every_distance_in_the_hand(self):
        a, b = hl._template_nominal(0.0), hl._template_nominal(12.0)
        for hand in ("L", "R"):
            names = [n for n in a if n.startswith(hand + "_")]
            for i, n in enumerate(names):
                for q in names[i + 1:]:
                    self.assertAlmostEqual(math.dist(a[n], a[q]), math.dist(b[n], b[q]), places=9, msg=f"{n}-{q}")
            pinky, index = a[f"{hand}_pinky"], a[f"{hand}_index"]
            u = ((index[0] - pinky[0]) / math.dist(pinky, index), (index[1] - pinky[1]) / math.dist(pinky, index))
            for n in names:                                   # the whole hand, thumb hole included, moved 12 mm along its line
                self.assertAlmostEqual(b[n][0] - a[n][0], 12.0 * u[0], places=9)
                self.assertAlmostEqual(b[n][1] - a[n][1], 12.0 * u[1], places=9)
        self.assertGreater(b["L_pinky"][0], a["L_pinky"][0])      # the left hand moves toward the tail
        self.assertLess(b["R_pinky"][0], a["R_pinky"][0])         # the right hand moves toward the bulb
        self.assertLess((b["R_pinky"][0] - b["L_pinky"][0]), (a["R_pinky"][0] - a["L_pinky"][0]) - 20.0)

    def test_p3_without_overlap_does_not_fit_and_says_what_to_change(self):
        with self.assertRaises(ValueError) as cm:
            layout_of("P3", hand_overlap_mm=0.0)
        self.assertIn("hand_overlap_mm", str(cm.exception))
        self.assertIn("too short", str(cm.exception))

    def test_p3_with_its_preset_overlap(self):
        lay, _, _ = layout_of("P3")
        self.assertEqual(lay.overlap_mm, presets.get_preset("P3")["hand_overlap_mm"])
        m = metrics(lay)
        self.assertLess(m["index_along"], -15.0)                  # the hands overlap: R index lies toward the bulb from L index
        for hand in ("L", "R"):                                   # the pinky, ring and middle distances are those of P1: nothing is compressed
            self.assertAlmostEqual(m["pitches_3d"][hand][0], 17.1, delta=0.4)
            self.assertAlmostEqual(m["pitches_3d"][hand][1], 17.7, delta=0.5)
        self.assertTrue([msg for msg in lay.messages if "slid 12 mm along its own line" in msg], lay.messages)

    def test_the_sideways_limit_is_reported(self):
        lay, cav, _ = layout_of("P2")
        self.assertEqual(sorted(c[0] for c in lay.clamps), ["L_index", "R_index"])
        for name, asked, used in lay.clamps:
            self.assertLess(abs(used), abs(asked))
            self.assertTrue([m for m in lay.messages if m.startswith(f"{name}: the sideways offset was limited")])

    def test_p1_and_p2_do_not_overlap(self):
        for name in ("P1", "P2"):
            lay, _, _ = layout_of(name)
            self.assertEqual(lay.overlap_mm, 0.0)
            self.assertLess(max(h.moved_mm for h in lay.holes), 1e-9, name)       # no hole had to move

    def test_axes_are_the_cavity_normals(self):
        lay, cav, _ = layout_of("P1")
        for h in lay.holes:
            n = cav.normal(h.theta, h.phi)
            self.assertAlmostEqual(sum(a * b for a, b in zip(n, h.axis)), 1.0, places=12)
            self.assertLess(math.dist(cav.point(h.theta, h.phi), h.centre), 1e-12)
            self.assertEqual(h.deck, "bottom" if h.name.endswith("thumb") else "top")
            self.assertEqual(h.axis[2] > 0, h.deck == "top", h.name)


class TestRelativeAndOthers(unittest.TestCase):
    def test_p0_layout_scales_with_the_body(self):
        small, cav_s, _ = layout_of("P0", 65.0)
        large, cav_l, _ = layout_of("P0", 125.0)
        self.assertEqual(small.kind, "relative")
        self.assertEqual(small.subholes, {})                     # the taped test layout has no subhole rule
        ratio = cav_l.length_mm / cav_s.length_mm
        for a, b in zip(small.holes, large.holes):
            self.assertEqual(a.name, b.name)
            self.assertAlmostEqual(b.s_nominal_mm / a.s_nominal_mm, ratio, places=9, msg=a.name)
            self.assertAlmostEqual(b.w_nominal_mm / a.w_nominal_mm, ratio, places=9, msg=a.name)
        for lay in (small, large):
            self.assertGreaterEqual(lay.min_gap_mm, 4.0)         # notes, C4: at least 4.0 mm on every P0 body

    def test_twelve_holes_in_the_kernel_order(self):
        lay, _, sz = layout_of("P2")
        self.assertEqual([h.name for h in lay.holes], [r.name for r in sz.holes.solutions["print"]])
        self.assertEqual(len(lay.holes), 12)
        for h, r in zip(lay.holes, sz.holes.solutions["print"]):
            self.assertEqual((h.d_mm, h.tube_mm, h.wall_mm), (r.d_mm, r.tube_mm, r.wall_mm))

    def test_no_holes(self):
        preset = presets.get_preset("S0")
        cav, _ = cavity_of(preset, 80.0)
        lay = hl.make_layout(cav, preset, [])
        self.assertEqual((lay.kind, lay.holes, lay.gaps), ("none", [], []))
        self.assertEqual(lay.min_gap_mm, float("inf"))

    def test_unknown_kind(self):
        with self.assertRaises(ValueError):
            layout_of("P1", layout="spiral")

    def test_with_rows_keeps_the_positions_and_reports_the_gaps(self):
        """Stage 3: corrected diameters at the round-1 positions (doc 04 D10)."""
        lay, _, sz = layout_of("P1")
        nominal = sz.holes.solutions["nominal"]                  # the k_hole 1.0 diameters: larger holes
        again = hl.with_rows(lay, nominal)
        for a, b, r in zip(lay.holes, again.holes, nominal):
            self.assertEqual((a.name, a.centre, a.axis, a.theta, a.phi), (b.name, b.centre, b.axis, b.theta, b.phi))
            self.assertEqual(b.d_mm, r.d_mm)
        self.assertLess(again.min_gap_mm, lay.min_gap_mm)
        self.assertIn("the hole positions are those of the round-1 layout", " ".join(again.messages))
        # the open question recorded in the notes: at the k 1.0 diameters the 9.5 mm slide leaves less than 3.4 mm
        self.assertAlmostEqual(again.gaps[0][2], 9.5 - 0.5 * (nominal[7].d_mm + nominal[0].d_mm), delta=1e-3)
        self.assertEqual({again.gaps[0][0], again.gaps[0][1]}, {"sub1", "L_ring"})
        self.assertEqual(again.gaps[0][2] < hl.MIN_GAP_MM, bool([m for m in again.messages if m.startswith("edge gap")]))


if __name__ == "__main__":
    unittest.main()
