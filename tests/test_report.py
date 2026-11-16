"""Plain-Python tests of the report helpers in ocarina_addon/report.py (no Blender): how a list of checks is
split into unexpected failures, expected failures and warnings, and what the result line says."""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ocarina_addon import report  # noqa: E402


def check(name, status, expected=False, message="m"):
    return dict(name=name, status=status, value=0.0, limit=0.0, message=message, expected=expected)


CHECKS = [check("range_ratio", "pass"), check("cavity_mode_c2L", "info"), check("hole_limits[print]", "fail", expected=True),
          check("hole_layout", "fail"), check("cavity_mode_computed", "needs_fem"), check("ergo_hand_span", "warn"),
          check("ergo_rest_space", "warn"), check("ergo_arch", "pass")]


class TestBlocks(unittest.TestCase):
    def test_the_three_blocks(self):
        b = report.check_blocks(CHECKS)
        self.assertEqual([c["name"] for c in b["unexpected"]], ["hole_layout"])
        self.assertEqual([c["name"] for c in b["expected"]], ["hole_limits[print]"])
        self.assertEqual([c["name"] for c in b["warnings"]], ["ergo_hand_span", "ergo_rest_space"])
        self.assertEqual([c["name"] for c in b["needs_fem"]], ["cavity_mode_computed"])

    def test_a_warning_or_an_info_is_never_a_failure(self):
        b = report.check_blocks([check("ergo_hand_span", "warn"), check("cavity_mode_c2L", "info"), check("x", "pass")])
        self.assertEqual((b["unexpected"], b["expected"], b["needs_fem"]), ([], [], []))
        self.assertEqual(len(b["warnings"]), 1)

    def test_result_line(self):
        line = report.result_line(CHECKS)
        self.assertIn("**UNEXPECTED FAILURES: hole_layout**", line)
        self.assertIn("expected by the notes: hole_limits[print] (fail)", line)
        self.assertIn("2 warnings (soft ergonomic checks, never failures): ergo_hand_span, ergo_rest_space", line)
        good = report.result_line([check("a", "pass"), check("ergo_x", "warn")])
        self.assertTrue(good.startswith("**no unexpected failure**"))
        self.assertIn("1 warning (", good)
        self.assertIn("0 warnings", report.result_line([check("a", "pass")]))

    def test_marks(self):
        self.assertEqual(report.mark(check("a", "pass")), "pass")
        self.assertEqual(report.mark(check("a", "warn")), "WARN")
        self.assertEqual(report.mark(check("a", "fail", expected=True)), "FAIL (expected)")
        self.assertEqual(report.mark(check("a", "needs_fem")), "NEEDS FEM")
        self.assertEqual(report.mark(check("a", "info")), "info")

    def test_the_subhole_naming_sentence(self):
        self.assertIn("sub1 = sub_L", report.SUBHOLE_NAMING)
        self.assertIn("sub2 = sub_R", report.SUBHOLE_NAMING)


if __name__ == "__main__":
    unittest.main()
