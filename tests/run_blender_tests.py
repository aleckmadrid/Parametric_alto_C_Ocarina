"""Runs the headless Blender tests (tests/blender/test_*.py) inside Blender 5.1.

From the repository root:

    blender -b --factory-startup --python tests/run_blender_tests.py
    blender -b --factory-startup --python tests/run_blender_tests.py -- TestBodyP1 TestStages     (only these classes)

The exit code is 0 when every test passes, 1 otherwise. The suite takes about 5 minutes. It builds each
body once, writes into a temporary folder and changes nothing in the repository.
The plain-Python tests (tests/test_*.py) do not need Blender:  python -m unittest discover -s tests
"""
import os
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(argv) -> int:
    loader = unittest.defaultTestLoader
    folder = ROOT / "tests" / "blender"
    suite = loader.discover(str(folder), pattern="test_*.py", top_level_dir=str(folder))
    if argv:
        def wanted(test):
            return any(name in test.id() for name in argv)

        def pick(s):
            out = unittest.TestSuite()
            for t in s:
                if isinstance(t, unittest.TestSuite):
                    out.addTests(pick(t))
                elif wanted(t):
                    out.addTest(t)
            return out
        suite = pick(suite)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    print(f"[blender tests] ran {result.testsRun}, failures {len(result.failures)}, errors {len(result.errors)}, "
          f"skipped {len(result.skipped)}: {'OK' if result.wasSuccessful() else 'FAILED'}", flush=True)
    return 0 if result.wasSuccessful() and result.testsRun > 0 else 1


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(args)
    sys.stdout.flush()
    os._exit(code)
