"""Plain-Python tests of ocarina_addon/ergonomics.py (no Blender).

The second half reproduces the Miracle and ECAN3 rows of
Analizes_ocarinas/Ergonomic_reference_12hole/measure_cad_output.md from the reference hole data. The data
are the tables in measure_reference.py (Miracle) and measure_cad_references.py (ECAN3); those two scripts
need numpy and Pillow to import, so that half is skipped when they are missing.
"""
import math
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
REF_DIR = ROOT / "Analizes_ocarinas" / "Ergonomic_reference_12hole"
sys.path.insert(0, str(ROOT))
from ocarina_addon import ergonomics as eg  # noqa: E402

try:
    sys.path.insert(0, str(REF_DIR))
    import measure_cad_references as mc  # noqa: E402
except Exception as exc:                    # noqa: BLE001 - numpy, Pillow or the photos may be missing
    mc = None
    IMPORT_ERROR = str(exc)


def simple_layout(pitch=18.0, offset=22.0, sub_slide=9.0):
    """Two parallel straight hand lines along X, the right one `offset` nearer the player. Y = toward the player."""
    P = {}
    for i, n in enumerate(eg.LEFT):
        P[n] = (i * pitch, 0.0)
    for i, n in enumerate(eg.RIGHT):                      # R_pinky ... R_index; the index is next to the left hand
        P[n] = (3 * pitch + 4.0 + (3 - i) * pitch, offset)
    P["sub1"] = (P["L_ring"][0], P["L_ring"][1] + sub_slide)          # left fingertips point toward the player
    P["sub2"] = (P["R_middle"][0], P["R_middle"][1] - 7.5)            # right fingertips point away
    P["L_thumb"] = (P["L_pinky"][0] + 7.0, 5.0)
    P["R_thumb"] = (P["R_middle"][0] - 4.0, 12.0)
    return P


class TestHandMetrics(unittest.TestCase):
    def test_parallel_lines(self):
        m = eg.hand_metrics(simple_layout())
        self.assertAlmostEqual(m["hands_angle"], 0.0, places=9)
        self.assertAlmostEqual(m["line_offset"], 22.0, places=9)
        self.assertAlmostEqual(m["a"][0], 1.0, places=9)
        self.assertAlmostEqual(m["p"][1], 1.0, places=9)
        self.assertEqual(m["L"]["pitches"], [18.0, 18.0, 18.0])
        self.assertAlmostEqual(m["L"]["span"], 54.0)
        self.assertAlmostEqual(m["index_across"], 22.0)
        self.assertAlmostEqual(m["index_along"], 4.0)

    def test_the_frame_does_not_depend_on_how_the_layout_is_turned(self):
        P = simple_layout()
        P["L_ring"] = (P["L_ring"][0], 3.0)                # an arch on the left hand
        P["R_middle"] = (P["R_middle"][0], 22.0 - 4.0)     # and on the right hand
        m0 = eg.hand_metrics(P)
        ang = math.radians(31.0)
        turn = lambda v: (v[0] * math.cos(ang) - v[1] * math.sin(ang) + 7.0, v[0] * math.sin(ang) + v[1] * math.cos(ang) - 3.0)
        m1 = eg.hand_metrics({n: turn(v) for n, v in P.items()})
        for key in ("hands_angle", "line_offset", "pinky_span", "index_across", "index_along"):
            self.assertAlmostEqual(m0[key], m1[key], places=9, msg=key)
        self.assertAlmostEqual(m0["L"]["arch"][0], 3.0, places=9)           # toward the player = toward the left fingertips
        self.assertAlmostEqual(m0["R"]["arch"][1], 4.0, places=9)           # away from the player = toward the right fingertips
        self.assertAlmostEqual(m1["L"]["arch"][0], 3.0, places=9)
        self.assertAlmostEqual(m1["sub1"]["forward"], m0["sub1"]["forward"], places=9)

    def test_subhole_forward_of_its_parent(self):
        m = eg.hand_metrics(simple_layout(sub_slide=9.0))
        self.assertEqual(m["sub1"]["parent"], "L_ring")
        self.assertAlmostEqual(m["sub1"]["dist"], 9.0)
        self.assertAlmostEqual(m["sub1"]["forward"], 9.0)
        self.assertAlmostEqual(m["sub1"]["off_normal_deg"], 0.0)
        self.assertEqual(m["sub2"]["parent"], "R_middle")
        self.assertAlmostEqual(m["sub2"]["forward"], 7.5)

    def test_subhole_behind_the_finger_or_sideways(self):
        P = simple_layout()
        P["sub1"] = (P["L_ring"][0], P["L_ring"][1] - 9.0)          # on the far side: the left finger must curl back
        m = eg.hand_metrics(P)
        self.assertLess(m["sub1"]["forward"], 0.0)
        self.assertAlmostEqual(abs(m["sub1"]["off_normal_deg"]), 180.0)
        P["sub1"] = (P["L_ring"][0] + 9.0, P["L_ring"][1])          # on the line toward the index: sideways
        self.assertAlmostEqual(eg.hand_metrics(P)["sub1"]["off_normal_deg"], 90.0)

    def test_the_parent_search_looks_at_both_hands(self):
        P = simple_layout()
        P["sub1"] = (P["R_index"][0], P["R_index"][1] - 8.7)        # the Miracle's first subhole: forward of R index
        m = eg.hand_metrics(P)
        self.assertEqual(m["sub1"]["parent"], "R_index")
        self.assertAlmostEqual(m["sub1"]["forward"], 8.7)
        self.assertEqual(m["sub1"]["nearest_same_hand"][0], "L")    # what a search in the assumed hand would report

    def test_thumbs_along_the_hand_axis(self):
        m = eg.hand_metrics(simple_layout())
        self.assertAlmostEqual(m["L_thumb"]["rel"]["L_pinky"], 7.0)
        self.assertAlmostEqual(m["R_thumb"]["rel"]["R_middle"], -4.0)


class TestLeanAnd3D(unittest.TestCase):
    def test_hole_lean_directions(self):
        a, p = (1.0, 0.0), (0.0, 1.0)
        s, c = math.sin(math.radians(30.0)), math.cos(math.radians(30.0))
        left_bulb = eg.hole_lean((-s, 0.0, c), a, p, "L")            # a left-hand hole leaning toward the bulb end
        self.assertAlmostEqual(left_bulb["toward_end_deg"], 30.0)
        self.assertAlmostEqual(left_bulb["toward_hand_deg"], 0.0)
        self.assertEqual(left_bulb["way"], "bulb")
        left_far = eg.hole_lean((0.0, -s, c), a, p, "L")             # toward the far side, where the left hand comes from
        self.assertAlmostEqual(left_far["toward_hand_deg"], 30.0)
        self.assertEqual(left_far["way"], "far")
        right_far = eg.hole_lean((0.0, -s, c), a, p, "R")            # the same lean is AWAY from the right hand
        self.assertAlmostEqual(right_far["toward_hand_deg"], -30.0)
        right_tail = eg.hole_lean((s, 0.0, c), a, p, "R")
        self.assertAlmostEqual(right_tail["toward_end_deg"], 30.0)
        self.assertAlmostEqual(right_tail["tilt_deg"], 30.0)

    def test_3d_pitch_is_longer_on_a_curved_deck(self):
        P = simple_layout()
        holes = {n: dict(centre=(v[0], v[1], 0.0), axis=(0.0, 0.0, 1.0), d_mm=6.0) for n, v in P.items()}
        holes["L_pinky"]["centre"] = (P["L_pinky"][0], P["L_pinky"][1], -6.0)       # the pinky hole sits lower, on the end
        m = eg.layout_metrics(holes)
        self.assertAlmostEqual(m["L"]["pitches"][0], 18.0)                           # plan view
        self.assertAlmostEqual(m["pitches_3d"]["L"][0], math.hypot(18.0, 6.0))       # straight 3-D distance
        self.assertAlmostEqual(m["sub1"]["dist_3d"], 9.0)
        self.assertEqual(sorted(m["lean"]), sorted(eg.FINGERS))

    def test_body_to_player(self):
        self.assertEqual(eg.body_to_player((1.0, 2.0, 3.0)), (1.0, -2.0, 3.0))


class TestEvaluate(unittest.TestCase):
    def good(self):
        P = simple_layout()
        P["L_ring"], P["L_middle"] = (P["L_ring"][0], 2.5), (P["L_middle"][0], 3.0)
        P["R_ring"], P["R_middle"] = (P["R_ring"][0], 22.0 - 2.5), (P["R_middle"][0], 22.0 - 3.0)
        P["sub1"] = (P["L_ring"][0], P["L_ring"][1] + 9.0)
        P["sub2"] = (P["R_middle"][0], P["R_middle"][1] - 7.5)
        return {n: dict(centre=(v[0], v[1], 0.0), axis=(0.0, 0.0, 1.0), d_mm=6.0) for n, v in P.items()}

    def test_a_good_layout_passes_every_check(self):
        res = eg.evaluate(eg.layout_metrics(self.good()), rest={"bulb": 16.0, "tail": 14.0})
        self.assertEqual([c["name"] for c in res],
                         ["ergo_finger_pitch", "ergo_hand_span", "ergo_arch", "ergo_hands_parallel", "ergo_hand_offset", "ergo_index_meet",
                          "ergo_subholes", "ergo_rest_space", "ergo_hole_lean_end", "ergo_hole_lean_side", "ergo_thumbs"])
        self.assertEqual({c["status"] for c in res}, {"pass"}, [c for c in res if c["status"] != "pass"])

    def test_a_status_is_pass_or_warn_and_never_fail(self):
        bad = self.good()
        bad["sub1"]["centre"] = (bad["L_ring"]["centre"][0] + 20.0, -9.0, 0.0)
        bad["L_pinky"]["axis"] = (-0.7, 0.0, 0.714)
        for n in eg.RIGHT:
            c = bad[n]["centre"]
            bad[n]["centre"] = (c[0] + 30.0, c[1] + 20.0, 0.0)
        res = eg.evaluate(eg.layout_metrics(bad), rest={"bulb": 3.0, "tail": 30.0})
        self.assertTrue(all(c["status"] in ("pass", "warn") for c in res))
        warned = {c["name"] for c in res if c["status"] == "warn"}
        self.assertTrue({"ergo_subholes", "ergo_rest_space", "ergo_hole_lean_end", "ergo_hand_offset", "ergo_index_meet"} <= warned, warned)

    def test_rest_space_is_measured_from_the_hole_edge_and_gives_the_missing_length(self):
        res = {c["name"]: c for c in eg.evaluate(eg.layout_metrics(self.good()), rest={"bulb": 9.0, "tail": 14.0})}
        c = res["ergo_rest_space"]
        self.assertEqual(c["status"], "warn")                       # 9.0 - 3.0 (radius) = 6.0 mm of land: 4.0 mm short of 10
        self.assertAlmostEqual(c["value"], 6.0)
        self.assertIn("4.0 mm too short", c["message"])
        self.assertNotIn("tail end is", c["message"].split("Measured")[0])

    def test_without_rest_or_axes_those_checks_are_left_out(self):
        m = eg.hand_metrics({n: h["centre"][:2] for n, h in self.good().items()})
        names = [c["name"] for c in eg.evaluate(m)]
        self.assertNotIn("ergo_rest_space", names)
        self.assertNotIn("ergo_hole_lean_end", names)
        self.assertIn("ergo_finger_pitch", names)

    def test_taped_body_warns_everywhere_with_the_message(self):
        res = eg.evaluate(eg.layout_metrics(self.good()), rest={"bulb": 16.0, "tail": 14.0}, taped=True)
        self.assertEqual(len(res), 11)
        for c in res:
            self.assertEqual(c["status"], "warn")
            self.assertTrue(c["message"].startswith("taped test body, not a hand layout"), c["message"])

    def test_limits_can_be_changed(self):
        m = eg.layout_metrics(self.good())
        strict = {c["name"]: c["status"] for c in eg.evaluate(m, {"finger_pitch_mm": (19.0, 20.5)})}
        self.assertEqual(strict["ergo_finger_pitch"], "warn")
        self.assertEqual(strict["ergo_hand_span"], "pass")

    def test_the_outer_skin_numbers_are_quoted_and_decide_nothing(self):
        inner = self.good()
        outer = {n: dict(h, centre=(h["centre"][0] * 0.8, h["centre"][1] * 0.8, 0.0)) for n, h in inner.items()}   # a squeezed copy
        res = {c["name"]: c for c in eg.evaluate(eg.layout_metrics(inner), outer=eg.layout_metrics(outer))}
        self.assertEqual(res["ergo_finger_pitch"]["status"], "pass")
        self.assertIn("at the outer skin", res["ergo_finger_pitch"]["message"])
        self.assertIn("at the outer skin", res["ergo_hand_span"]["message"])


def numbers(cell: str) -> list:
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", cell)]


@unittest.skipIf(mc is None, "the reference scripts could not be imported (numpy or Pillow missing)")
class TestReferenceRows(unittest.TestCase):
    """ergonomics.py reproduces the Miracle and ECAN3 rows of measure_cad_output.md."""

    @classmethod
    def setUpClass(cls):
        text = (REF_DIR / "measure_cad_output.md").read_text(encoding="utf-8")
        cls.sections = {}
        for part in text.split("\n## ")[1:]:
            title, body = part.split("\n", 1)
            cls.sections[title.split(".")[0]] = [ln for ln in body.splitlines() if ln.startswith("| ")]
        cls.layouts = {"Miracle AO10-AC": {n: dict(centre=(float(v[0]), float(v[1]), 0.0)) for n, v in mc.mr.MIRACLE.items()}}
        for model, title in (("oot", "ECAN3 Ocarina of Time v3 (CAD)"), ("eclipse", "ECAN3 Eclipse (CAD)")):
            fr = mc.ECAN3_FRAME[model]
            holes = {}
            for n, (c, ax, d, t) in mc.ECAN3[model].items():
                face = fr["top"] if not n.endswith("thumb") else -fr["top"]
                holes[n] = dict(centre=(fr["sx"] * c[0], -c[2], fr["top"] * c[1]), axis=(fr["sx"] * ax[0], -ax[2], face * ax[1]), d_mm=d)
            cls.layouts[title] = holes

    def row(self, section, label):
        rows = [ln for ln in self.sections[section] if ln.startswith(f"| {label}")]
        self.assertEqual(len(rows), 1, f"section {section}: row {label!r}")
        return [c.strip() for c in rows[0].strip("|").split("|")]

    def close(self, got, want, tol, what):
        self.assertEqual(len(got), len(want), what)
        for g, w in zip(got, want):
            self.assertAlmostEqual(g, w, delta=tol, msg=what)

    def test_three_reference_layouts(self):
        self.assertEqual(len(self.layouts), 3)

    def test_section_1_the_two_hand_lines(self):
        for label, holes in self.layouts.items():
            m = eg.hand_metrics({n: h["centre"][:2] for n, h in holes.items()})
            cells = self.row("1", label)
            self.close(numbers(cells[1]), [m["hands_angle"]], 0.051, f"{label}: angle between the hand lines")
            self.close(numbers(cells[2]), [m["line_tilt"]], 0.051, f"{label}: line against the hand axis")
            self.close(numbers(cells[3]), [m["line_offset"]], 0.051, f"{label}: right line nearer the player")
            self.close(numbers(cells[4]), [m["pinky_span"]], 0.051, f"{label}: pinky to pinky")
            self.close(numbers(cells[5]), m["L"]["pitches"], 0.051, f"{label}: left pitches")
            self.close(numbers(cells[6]), m["R"]["pitches"], 0.051, f"{label}: right pitches")
            self.close(numbers(cells[7]), [m["L"]["span"]], 0.051, f"{label}: left span")
            self.close(numbers(cells[8]), [m["R"]["span"]], 0.051, f"{label}: right span")
            self.close(numbers(cells[9]), m["L"]["arch"], 0.051, f"{label}: left arch")
            self.close(numbers(cells[10]), m["R"]["arch"], 0.051, f"{label}: right arch")
            self.close(numbers(cells[11]), [m["index_across"], m["index_along"], m["index_dist"]], 0.051, f"{label}: index holes")

    def test_section_2_subholes(self):
        for label, holes in self.layouts.items():
            m = eg.hand_metrics({n: h["centre"][:2] for n, h in holes.items()})
            cells = self.row("2", label)
            for cell, sub in ((cells[1], "sub_L"), (cells[2], "sub_R")):
                s = m[sub]
                self.assertTrue(cell.startswith(s["parent"] + ","), f"{label} {sub}: parent {s['parent']} against {cell!r}")
                got = numbers(cell.split(",", 1)[1])
                self.close(got[:3], [s["dist"], s["forward"], s["toward_index"]], 0.051, f"{label} {sub}")
                self.assertAlmostEqual(got[3], s["off_normal_deg"], delta=0.51, msg=f"{label} {sub}: off the normal")
            self.assertTrue(cells[3].startswith(m["sub_L"]["nearest_same_hand"]), label)
            self.close(numbers(cells[3].split("/")[1]), [m["sub_L"]["dist_same_hand"]], 0.051, f"{label}: assumed-hand distance")
        # the finding of docs/06 section 3.1: the Miracle's first subhole belongs to the RIGHT index finger
        m = eg.hand_metrics({n: h["centre"][:2] for n, h in self.layouts["Miracle AO10-AC"].items()})
        self.assertEqual(m["sub_L"]["parent"], "R_index")
        self.assertAlmostEqual(m["sub_L"]["dist"], 8.7, delta=0.05)

    def test_section_3_thumb_holes(self):
        for label, holes in self.layouts.items():
            m = eg.hand_metrics({n: h["centre"][:2] for n, h in holes.items()})
            cells = self.row("3", label)
            lt, rt = m["L_thumb"], m["R_thumb"]
            self.close(numbers(cells[1]), [lt["rel"]["L_pinky"], lt["rel"]["L_ring"]], 0.051, f"{label}: L thumb")
            self.close(numbers(cells[2]), [rt["rel"]["R_index"], rt["rel"]["R_middle"], rt["rel"]["R_ring"]], 0.051, f"{label}: R thumb")
            self.close(numbers(cells[3]), [rt["across"]["R_index"]], 0.051, f"{label}: R thumb across")

    def test_section_5_hole_lean(self):
        for label, holes in self.layouts.items():
            if label.startswith("Miracle"):
                continue                                   # a photo has no hole axes
            m = eg.layout_metrics(holes)
            cells = self.row("5", label)
            for cell, name in zip(cells[1:], eg.FINGERS):
                r = m["lean"][name]
                self.assertAlmostEqual(numbers(cell)[0], r["tilt_deg"], delta=0.51, msg=f"{label} {name}")
                self.assertTrue(cell.endswith(r["way"]), f"{label} {name}: {cell!r} against {r['way']}")

    def test_the_references_pass_every_check_with_the_limits_of_doc_06(self):
        """The limits are the range of these three layouts, widened a little: none of them may warn."""
        for label, holes in self.layouts.items():
            m = eg.layout_metrics(holes) if "axis" in holes["L_pinky"] else eg.hand_metrics({n: h["centre"][:2] for n, h in holes.items()})
            res = eg.evaluate(m)
            self.assertEqual([c["name"] for c in res if c["status"] != "pass"], [], label)
            self.assertGreaterEqual(len(res), 8)


if __name__ == "__main__":
    unittest.main()
