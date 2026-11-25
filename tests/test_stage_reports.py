"""Plain-Python tests of the committed stage reports (addon_checks/stage1.md, stage2.md, stage3-*.md).

They check that the reports the stage commands wrote agree with docs/04-testing-phase.md and with the
kernel. They read files only; run a stage command again to refresh the reports
(ocarina_addon/headless.py -- stage1 | stage2 | stage3). A missing report skips its tests.
"""
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ocarina_addon import kernel_bridge, report  # noqa: E402

CHECKS = ROOT / "addon_checks"
K = kernel_bridge.kernel()
P = kernel_bridge.load_params()


def numbers(text: str) -> list:
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", text)]


def table_after(text: str, heading: str) -> list:
    """Rows (lists of cells) of the first Markdown table after a heading."""
    part = text.split(heading, 1)[1] if heading else text
    rows, started = [], False
    for line in part.splitlines():
        if line.startswith("|"):
            started = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not set(cells[0]) <= set("-: "):
                rows.append(cells)
        elif started:
            break
    return rows[1:]                                   # without the header row


def thinnest_plastic(text: str) -> list:
    """The thinnest plastic of every body of a stage report (the wall check prints it), in mm."""
    return [float(x) for x in re.findall(r"tubes: ([0-9.]+) mm \(it must be at least 0\.4 mm", text)]


def read(name: str) -> str:
    path = CHECKS / name
    if not path.is_file():
        raise unittest.SkipTest(f"{path} is missing: run the stage command")
    return path.read_text(encoding="utf-8")


class TestStage2Report(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("stage2.md")
        cls.doc04 = (ROOT / "docs" / "04-testing-phase.md").read_text(encoding="utf-8")

    def test_the_bodies_of_doc_04(self):
        ids = [r[0] for r in table_after(self.text, "## Bodies")]
        self.assertEqual(ids, ["P0-65", "P0-80", "P0-95", "P1-80", "P2-80", "P4-80", "P0-80-b", "P0-80-c"])
        self.assertNotIn("P0-125", self.text)               # dropped with the ladder change of 2026-11-17
        self.assertNotIn("| P3", self.text)                 # stashed since 2026-11-17 (docs/08)

    def test_sizes_agree_with_doc_04(self):
        """The regenerated table against "Generated sizes at each step" of doc 04, cell by cell."""
        doc = {numbers(r[0])[0]: r for r in table_after(self.doc04, "## Generated sizes at each step")}
        rep = {numbers(r[0])[0]: r for r in table_after(self.text, "## Sizes against doc 04")}
        self.assertEqual(sorted(rep), [65.0, 80.0, 95.0])
        for v0, row in rep.items():
            want = doc[v0]
            self.assertEqual(row[1].split()[0], want[1].split()[0], f"{v0}: window shape")
            (l1, w1, a1), (l2, w2, a2) = numbers(row[1]), numbers(want[1])
            self.assertAlmostEqual(l1, l2, delta=0.005, msg=f"{v0}: window length")
            self.assertAlmostEqual(w1, w2, delta=0.05, msg=f"{v0}: window width")
            self.assertAlmostEqual(a1, a2, delta=1.0, msg=f"{v0}: window area (doc 04 rounds 46.5 to 47)")
            for col, name, tol in ((2, "windway", 0.05), (3, "sub2", 0.05), (4, "D6 thumb", 0.05), (5, "E6 thumb", 0.05),
                                   (6, "P0 length", 0.5), (7, "area ratio", 0.0005)):
                for got, exp in zip(numbers(row[col]), numbers(want[col])):
                    self.assertAlmostEqual(got, exp, delta=tol, msg=f"{v0} cm3: {name}")

    def test_three_separate_blocks_and_no_unexpected_failure(self):
        for heading in ("## Unexpected failures", "## Expected failures", "## Warnings"):
            self.assertEqual(self.text.count(heading + "\n"), 1, heading)
        block = self.text.split("## Unexpected failures")[1].split("## Expected failures")[0]
        self.assertEqual(block.strip(), "None.")
        self.assertIn("8 of 8 bodies have no unexpected failure", self.text)
        expected = self.text.split("## Expected failures")[1].split("## Warnings")[0]
        self.assertIn("hole_limits[print]", expected)
        self.assertNotIn("ergo_", expected)
        warnings = self.text.split("## Warnings")[1].split("## Sizes against doc 04")[0]
        self.assertIn("P1-80 `ergo_hand_span`", warnings)
        self.assertIn("taped test body, not a hand layout", warnings)
        self.assertNotIn("hole_limits", warnings)

    def test_subhole_naming_is_stated_and_used(self):
        self.assertIn(report.SUBHOLE_NAMING, self.text)
        tables = "\n".join(line for line in self.text.split("## Per body")[1].splitlines() if line.startswith("| sub"))
        self.assertIn("| sub1 |", tables)
        self.assertNotIn("| sub_L", tables)
        self.assertNotIn("| sub_R", tables)

    def test_hole_tables_are_the_kernel_numbers(self):
        """Every hole of every Stage 2 body: print d (k 0.8), nominal d (k 1.0), tube and chimney as the kernel sizes them."""
        for body, v0 in (("P0-65", 65.0), ("P1-80", 80.0), ("P0-95", 95.0)):
            section = self.text.split(f"### {body}\n")[1].split("\n### ")[0]
            rows = {r[0]: r for r in table_after(section, "") if r[0] in [h["name"] for h in P["fingering"]["holes"]]}
            sz = K.sizing.size_body(v0, params=P)
            self.assertEqual(len(rows), 12, body)
            for p, n in zip(sz.holes.solutions["print"], sz.holes.solutions["nominal"]):
                r = rows[p.name]
                self.assertAlmostEqual(numbers(r[2])[0], n.d_plain_mm, delta=0.006, msg=f"{body} {p.name}: plain wall d")
                self.assertAlmostEqual(numbers(r[3])[0], p.tube_mm, delta=0.051, msg=f"{body} {p.name}: tube")
                self.assertAlmostEqual(numbers(r[4])[0], p.chimney_mm, delta=0.051, msg=f"{body} {p.name}: chimney")
                self.assertAlmostEqual(numbers(r[5])[0], p.d_mm, delta=0.006, msg=f"{body} {p.name}: print d")
                self.assertAlmostEqual(numbers(r[6])[0], n.d_mm, delta=0.006, msg=f"{body} {p.name}: nominal d")
                self.assertAlmostEqual(numbers(r[7])[0], p.d_mm, delta=0.05, msg=f"{body} {p.name}: d on the STL (Phase 4 gate)")
            self.assertIn(f"Voicing hash `{sz.voicing.version_hash}`", section)

    def test_the_build_of_the_rules_on_every_body(self):
        """Rule version 3 (owner's choice of 2026-11-19): every Stage 2 body has the ellipse cut with the roof cut
        square, the pipe at +8 degrees, the cone neck, the 3 mm mouth end and the pocket blend."""
        self.assertEqual(self.text.count("Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm."), 8)
        self.assertEqual(self.text.count("inlet height 3.00 mm"), 8)
        self.assertNotIn("Build: plain", self.text)
        # the neck stands behind the window: it must stay outside the 45 degree flare from the window rim
        self.assertEqual(self.text.count("0 points of the surface inside the 45° flare from the window rim"), 8)
        self.assertNotIn("nothing stands above the outer face", self.text)

    def test_the_pocket_blend_ends_on_the_chamber_wall_and_leaves_no_sliver(self):
        """The first build with the blend on every body left 0.06 mm of plastic on P2-80: the skirt had a fixed reach
        and did not meet the wall of a curved chamber. It now ends where it meets the wall."""
        self.assertEqual(self.text.count("| `pocket_blend` | pass |"), 8)
        thin = thinnest_plastic(self.text)
        self.assertEqual(len(thin), 8)
        self.assertGreaterEqual(min(thin), 1.15)            # the roof of the cone neck over the pipe: 1.2 mm by rule (owner, 2026-11-17)

    def test_the_left_subhole_slide_is_10_mm(self):
        """Owner decision 1 of 2026-11-18. The smallest edge gap of the hand bodies is then the right subhole's."""
        for body in ("P1-80", "P2-80", "P4-80"):
            section = self.text.split(f"### {body}\n")[1].split("\n### ")[0]
            self.assertIn("sub1 slides 10.00 mm from L_ring", section, body)

    def test_the_copies(self):
        self.assertIn("`P0-80-b` has the same triangles as `P0-80`", self.text)
        self.assertIn("`P0-80-c` has the same triangles as `P0-80`", self.text)


class TestStage1Report(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("stage1.md")

    def test_the_stubs_of_doc_04(self):
        rows = {r[0]: r for r in table_after(self.text, "## Sizes against doc 04")}
        self.assertEqual(list(rows), ["V-a", "V-af", "V-b", "V-d", "V-a0", "V-a35", "V-a3"])
        # doc 04, Stage 1: teardrop 63 mm2; rounded rectangle 63 mm2; teardrop 47 mm2; V-a3 is the teardrop of the 3 mm wall, 54 mm2
        for stub, shape, area, tol in (("V-a", "Teardrop", 63.0, 0.5), ("V-af", "Teardrop", 63.0, 0.5), ("V-b", "Rounded rectangle", 63.0, 0.5),
                                       ("V-d", "Teardrop", 47.0, 0.6), ("V-a3", "Teardrop", 54.0, 0.5)):
            self.assertTrue(rows[stub][1].startswith(shape), stub)
            self.assertAlmostEqual(numbers(rows[stub][1])[2], area, delta=tol, msg=stub)
        # the labium offset: -0.2 mm by default, the coupons 0 and -0.35 mm; never positive
        for stub, offset in (("V-a", -0.2), ("V-af", -0.2), ("V-b", -0.2), ("V-d", -0.2), ("V-a3", -0.2), ("V-a0", 0.0), ("V-a35", -0.35)):
            self.assertAlmostEqual(numbers(rows[stub][3])[0], offset, msg=stub)
        for stub in rows:                                    # the capped air of every stub is the stub volume
            self.assertAlmostEqual(numbers(rows[stub][6])[0], 25.0, delta=0.125)
        # the build (owner decisions of 2026-11-18): every stub has the build of the rules except V-af and V-b (plain)
        self.assertEqual({stub: rows[stub][9] for stub in rows},
                         {"V-a": "of the rules", "V-af": "plain", "V-b": "plain", "V-d": "of the rules", "V-a0": "of the rules",
                          "V-a35": "of the rules", "V-a3": "of the rules"})
        for stub, mouth_end in (("V-a", 3.0), ("V-af", 3.0)):                    # 3 mm at the mouth end on both builds (decision 4)
            section = self.text.split(f"### {stub}\n")[1].split("\n### ")[0]
            self.assertIn(f"inlet height {mouth_end:.2f} mm", section)
        self.assertIn("Build (in the hash): ellipse cut, 3 mm per side, shelf 0°; windway +8° against the body; cone neck, its outer flank along the pipe; pocket blend 12 mm.", self.text.split("### V-a\n")[1].split("\n### ")[0])
        self.assertIn("Build: plain (fan cut, level windway, box stub, no pocket blend).", self.text.split("### V-af\n")[1].split("\n### ")[0])

    def test_stub_hashes_are_those_of_the_bodies(self):
        rows = {r[0]: r for r in table_after(self.text, "## Sizes against doc 04")}
        for stub, v0 in (("V-a", 80.0), ("V-d", 65.0)):
            self.assertEqual(rows[stub][4].strip("`"), K.sizing.size_body(v0, params=P).voicing.version_hash, stub)
            self.assertIn(f"{v0:g} cm³ bodies", rows[stub][5])
        self.assertEqual(len({rows[s][4] for s in rows}), 7)             # seven voicings, seven hashes
        self.assertEqual(rows["V-b"][5], "no body")
        # V-af: the window of V-a with the plain build. The build is in the hash, so no body carries this one.
        self.assertEqual(rows["V-af"][5], "no body")
        self.assertEqual(rows["V-af"][1], rows["V-a"][1])
        self.assertEqual(rows["V-af"][4].strip("`"), K.voicing.make_voicing(80.0, params=P, build="plain").version_hash)

    def test_blocks_and_result(self):
        for heading in ("## Unexpected failures", "## Expected failures", "## Warnings"):
            self.assertEqual(self.text.count(heading + "\n"), 1, heading)
        # The four stubs of the plan and the two labium coupons have no unexpected failure. The optional V-a3 (3 mm
        # window wall) fails its outside keep-out: on a 3 mm window wall the standing neck is 47 degrees steep seen from
        # the window rim, against the 45 degree flare (open problem 22 of the notes). When that is solved this must
        # become "7 of 7".
        self.assertIn("6 of 7 bodies have no unexpected failure", self.text)
        self.assertIn("UNEXPECTED FAILURES on V-a3.", self.text)
        block = self.text.split("## Unexpected failures")[1].split("## Expected failures")[0]
        self.assertEqual([ln.split("**")[1] for ln in block.splitlines() if ln.startswith("- **")], ["V-a3"])
        self.assertIn("`voicing_keepouts`", block)
        self.assertEqual(self.text.count("| `stub_volume` | pass |"), 7)
        # the pocket blend: on the five stubs with the build of the rules, and with no sliver on the small egg
        self.assertEqual(self.text.count("| `pocket_blend` | pass |"), 5)
        thin = thinnest_plastic(self.text)
        self.assertEqual(len(thin), 7)
        self.assertGreaterEqual(min(thin), 1.15)            # the roof of the cone neck over the pipe: 1.2 mm by rule (owner, 2026-11-17)
        self.assertIn("inside the 45° flare from the window rim", block)
        self.assertIn(report.SUBHOLE_NAMING, self.text)
        self.assertIn("a prediction, not a measurement", self.text)


class TestStage3Report(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("stage3-synthetic-fitted-constants.md")

    def test_marked_synthetic(self):
        self.assertIn("**SYNTHETIC CONSTANTS.**", self.text.split("\n")[2])
        self.assertIn("Do not print these bodies", self.text)

    def test_bodies_and_kept_tubes(self):
        ids = [r[0] for r in table_after(self.text, "## Bodies")]
        self.assertEqual(ids, ["P0-65-r2", "P0-80-r2", "P0-95-r2", "P1-80-r2", "P2-80-r2", "P4-80-r2", "P0-88-r2"])
        self.assertEqual(self.text.count("(kept)"), 6 * 12)              # every hole of the six printed bodies
        self.assertNotIn("(CHANGED)", self.text)
        section = self.text.split("### P0-65-r2\n")[1].split("\n### ")[0]
        rows = {r[0]: r for r in table_after(section, "")}
        round1 = K.sizing.size_body(65.0, params=P)
        for h, tube in zip(round1.holes.solutions["print"], round1.holes.tubes_mm):
            self.assertAlmostEqual(numbers(rows[h.name][3])[0], tube, delta=0.051, msg=h.name)
            self.assertAlmostEqual(numbers(rows[h.name][7])[0], h.d_mm, delta=0.006, msg=f"{h.name}: round 1 print d")
        self.assertEqual([t for t in round1.holes.tubes_mm if t > 0], [0.5, 5.0])

    def test_blocks_and_verdict(self):
        for heading in ("## Unexpected failures", "## Expected failures", "## Warnings", "### Round-hole verdict (doc 04, Gate 2)"):
            self.assertEqual(self.text.count(heading + "\n"), 1, heading)
        # Open problem 19 closed (2026-11-18): with the 10 mm slide no round-2 body fails the edge gap, even with the
        # synthetic constants (k_hole 1.18, invented).
        self.assertIn("7 of 7 bodies have no unexpected failure", self.text)
        self.assertNotIn("Why `hole_spacing` fails here", self.text)
        self.assertEqual(self.text.count("| `pocket_blend` | pass |"), 7)
        self.assertIn("The printed volume is kept (the default)", self.text)
        self.assertIn("never printed", self.text)


if __name__ == "__main__":
    unittest.main()
