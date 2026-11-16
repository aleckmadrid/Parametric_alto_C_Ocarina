"""Pack the add-on as a Blender extension zip (plain Python; Blender is needed only for --validate).

    python tools/pack_extension.py                      # writes dist/parametric_ocarina-<version>.zip
    python tools/pack_extension.py --out some/folder
    python tools/pack_extension.py --validate           # also runs Blender's own check of the zip

What goes into the zip (at its root, as Blender wants it):
    blender_manifest.toml, *.py                the add-on (ocarina_addon/)
    presets/cavity_presets.toml                the cavity presets
    kernel/*.py                                the acoustic kernel, without its tests and command-line studies
    params/alto_c_12hole.toml                  the parameter file

ocarina_addon/kernel_bridge.py looks for `kernel/` and `params/` inside the add-on folder first, so the
installed extension uses its packed copies and needs nothing from the repository.

The cavity-mode check needs a Python with numpy and scipy outside Blender (see ocarina_addon/cavity_mode.py).
An installed extension finds it on PATH or through the environment variable OCARINA_PYTHON.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import tomllib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
ADDON = ROOT / "ocarina_addon"
DEFAULT_BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
sys.path.insert(0, str(ROOT))
from ocarina_addon import kernel_bridge  # noqa: E402  (standard library only)


def files_to_pack() -> list:
    """(source path, name in the zip), sorted by the name in the zip."""
    out = [(ADDON / "blender_manifest.toml", "blender_manifest.toml")]
    out += [(p, p.name) for p in ADDON.glob("*.py")]
    out += [(p, f"presets/{p.name}") for p in (ADDON / "presets").glob("*.toml")]
    out += [(ROOT / "kernel" / f"{name}.py", f"kernel/{name}.py") for name in kernel_bridge.KERNEL_MODULES]
    out += [(ROOT / "params" / kernel_bridge.PARAMS_FILE, f"params/{kernel_bridge.PARAMS_FILE}")]
    missing = [str(src) for src, _ in out if not src.is_file()]
    if missing:
        raise FileNotFoundError("missing: " + ", ".join(missing))
    return sorted(out, key=lambda t: t[1])


def pack(out_dir=None) -> pathlib.Path:
    """Write the extension zip and return its path."""
    with open(ADDON / "blender_manifest.toml", "rb") as fh:
        manifest = tomllib.load(fh)
    out_dir = pathlib.Path(out_dir) if out_dir else ROOT / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{manifest['id']}-{manifest['version']}.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for src, name in files_to_pack():
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))        # fixed dates: the same sources give the same zip
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, src.read_bytes())
    return path


def validate(zip_path, blender=DEFAULT_BLENDER) -> int:
    """Blender's own check of an extension package. Returns 0 when Blender reports no error."""
    r = subprocess.run([blender, "--command", "extension", "validate", str(zip_path)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    text = ((r.stdout or "") + (r.stderr or "")).strip()
    print(text.encode("ascii", "replace").decode("ascii"))                # the Windows console may not have the characters
    return 1 if (r.returncode != 0 or "ERROR" in text) else 0             # Blender prints FATAL_ERROR and still exits with 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pack the Parametric Ocarina add-on as a Blender extension zip.")
    ap.add_argument("--out", help="folder for the zip (default: dist/ in the repository)")
    ap.add_argument("--validate", action="store_true", help="run `blender --command extension validate` on the zip")
    ap.add_argument("--blender", default=DEFAULT_BLENDER, help="path of the Blender 5.1 program")
    args = ap.parse_args(argv)
    path = pack(args.out)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
    print(f"packed {len(names)} files into {path} ({path.stat().st_size / 1024:.0f} kB)")
    return validate(path, args.blender) if args.validate else 0


if __name__ == "__main__":
    sys.exit(main())
