"""Does an annotated inspection agree with the check report beside it? Plain Python, no Blender.

    python tools/check_inspection.py <folder> [<folder> ...]

For every <id>_inspection.json in the folders, with <id>_checks.json beside it: the values drawn as measured are the
check report's, each is within the checks' tolerance of the design value, and the labium edge sits where the design
puts it against the projected jet axis (ocarina_addon.inspection.verify). Exit code 1 on a difference.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from ocarina_addon import inspection  # noqa: E402


def main(folders) -> int:
    seen = bad = 0
    for path in sorted(p for f in folders for p in pathlib.Path(f).glob("[!.]*_inspection.json")):
        checks = path.with_name(path.name.replace("_inspection.json", "_checks.json"))
        if not checks.is_file():
            print(f"{path}: no check report beside it (not compared)")
            continue
        seen += 1
        found = inspection.verify(inspection.load_snapshot(path), json.loads(checks.read_text(encoding="utf-8")))
        bad += bool(found)
        print(f"{path}: " + ("agrees with the check report" if not found else "; ".join(found)))
    if not seen:
        print("no inspection with a check report was found")
    return 1 if bad or not seen else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
