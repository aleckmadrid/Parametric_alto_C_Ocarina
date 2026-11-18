"""Install test of the extension zip in a CLEAN Blender profile (plain Python; it starts Blender itself).

    python -m unittest discover -s tests/extension -v            (about 2 minutes)

What it does
    1. packs the add-on with tools/pack_extension.py into a temporary folder
    2. starts Blender 5.1 with the environment variable BLENDER_USER_RESOURCES set to a temporary folder,
       so Blender uses that folder as its whole user profile, and installs the zip there:
           blender --command extension install-file -r user_default --enable <zip>
    3. starts Blender again in that profile and builds a body with the INSTALLED extension
       (tests/extension/build_in_installed.py)
    4. checks that the owner's real Blender profile did not change

The Blender program is taken from the environment variable BLENDER, or from the default install path.
The test is skipped when Blender is not found.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools import pack_extension  # noqa: E402

BLENDER = os.environ.get("BLENDER", pack_extension.DEFAULT_BLENDER)


def real_profile() -> pathlib.Path:
    """The owner's own Blender 5.1 user folder (it must stay untouched)."""
    base = os.environ.get("APPDATA")
    if base:
        return pathlib.Path(base) / "Blender Foundation" / "Blender" / "5.1"
    return pathlib.Path.home() / ".config" / "blender" / "5.1"


def listing(folder: pathlib.Path) -> dict:
    """relative path -> (size, modification time) of every file under folder."""
    if not folder.is_dir():
        return {}
    out = {}
    for p in folder.rglob("*"):
        if p.is_file():
            st = p.stat()
            out[p.relative_to(folder).as_posix()] = (st.st_size, st.st_mtime_ns)
    return out


def run(cmd, env, timeout=900):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


@unittest.skipUnless(pathlib.Path(BLENDER).is_file(), f"Blender not found at {BLENDER} (set the environment variable BLENDER)")
class TestExtensionInstall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="oca_ext_"))
        cls.profile = cls.tmp / "blender_profile"
        cls.profile.mkdir()
        cls.before = listing(real_profile())
        cls.zip = pack_extension.pack(cls.tmp / "dist")
        env = dict(os.environ, BLENDER_USER_RESOURCES=str(cls.profile))
        for key in ("BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS", "BLENDER_USER_EXTENSIONS", "BLENDER_USER_DATAFILES"):
            env.pop(key, None)
        cls.install_code, cls.install_log = run([BLENDER, "--command", "extension", "install-file", "-r", "user_default", "--enable",
                                                 str(cls.zip)], env)
        cls.out = cls.tmp / "out"
        cls.build_code, cls.build_log = run([BLENDER, "-b", "--python", str(ROOT / "tests" / "extension" / "build_in_installed.py"),
                                             "--", str(cls.out)], env)
        result = cls.out / "result.json"
        cls.result = json.loads(result.read_text(encoding="utf-8")) if result.is_file() else {"ok": False, "error": "no result.json"}
        cls.after = listing(real_profile())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_zip_holds_the_add_on_the_kernel_and_the_parameters(self):
        with zipfile.ZipFile(self.zip) as z:
            names = set(z.namelist())
        for name in ("blender_manifest.toml", "__init__.py", "api.py", "stages.py", "ergonomics.py", "cavity_mode_solver.py",
                     "presets/cavity_presets.toml", "kernel/ocarina_kernel.py", "kernel/sizing.py", "kernel/calibration.py",
                     "params/alto_c_12hole.toml"):
            self.assertIn(name, names)
        self.assertFalse([n for n in names if "test_" in n or "__pycache__" in n or n.startswith("ocarina_addon/")], "tests or caches in the zip")

    def test_the_extension_installs_into_the_temporary_profile(self):
        self.assertEqual(self.install_code, 0, self.install_log[-2000:])
        installed = self.profile / "extensions" / "user_default" / "parametric_ocarina"
        self.assertTrue((installed / "blender_manifest.toml").is_file(), self.install_log[-2000:])
        self.assertTrue((installed / "kernel" / "sizing.py").is_file())
        self.assertTrue((installed / "params" / "alto_c_12hole.toml").is_file())

    def test_the_installed_extension_builds_a_body(self):
        r = self.result
        self.assertTrue(r["ok"], r.get("error", "") + self.build_log[-3000:])
        self.assertTrue(r["enabled"])
        self.assertEqual(r["operators"], ["build_cavity", "build_body"])
        inside = lambda p: pathlib.Path(p).resolve().is_relative_to(self.profile.resolve())
        self.assertTrue(inside(r["module_file"]), r["module_file"])           # the installed copy, not the repository
        self.assertTrue(inside(r["kernel_dir"]), r["kernel_dir"])             # the packed kernel
        self.assertTrue(inside(r["params_path"]), r["params_path"])           # the packed parameter file
        self.assertTrue(inside(r["user_resources"]), r["user_resources"])
        self.assertEqual(r["repository_on_sys_path"], [])
        self.assertEqual(r["body_id"], "P0-65")
        self.assertEqual(r["voicing_hash"], "2a71c31c2505")
        self.assertEqual(r["unexpected"], [])
        self.assertTrue(r["manifold"])
        self.assertGreater(r["triangles"], 10000)
        self.assertAlmostEqual(r["capped_air_cm3"] / 65.0, 1.0, delta=0.005)
        for name in ("P0-65.stl", "P0-65_air_capped.stl", "P0-65_checks.json"):
            self.assertIn(name, r["files"])
        self.assertEqual(r["statuses"]["hole_sizes_phase4_gate"], "pass")
        self.assertEqual(r["statuses"]["cavity_mode_computed"], "pass")       # the solver ran from the installed copy
        self.assertAlmostEqual(r["cavity_mode"], 2.24, delta=0.05)

    def test_the_owners_profile_is_untouched(self):
        self.assertEqual(self.before, self.after)
        self.assertFalse((real_profile() / "extensions" / "user_default" / "parametric_ocarina").exists())


if __name__ == "__main__":
    unittest.main()
