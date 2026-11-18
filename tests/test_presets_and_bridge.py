"""Plain-Python tests of ocarina_addon/presets.py and ocarina_addon/kernel_bridge.py (no Blender)."""
import pathlib
import sys
import tempfile
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ocarina_addon import ergonomics, holes_layout, kernel_bridge, presets  # noqa: E402


class TestPresets(unittest.TestCase):
    def test_the_presets_of_the_test_plan_exist(self):
        all_ = presets.load_presets()
        self.assertEqual(sorted(all_), ["P0", "P1", "P2", "P3", "P4", "S0"])
        for name, p in all_.items():
            self.assertEqual(p["id"], name)
            self.assertEqual(len(p["width"]), 7)
            self.assertEqual(len(p["height"]), 7)
            for key in presets.REQUIRED:
                self.assertIn(key, p, f"{name} lacks {key}")

    def test_layout_kinds(self):
        self.assertEqual(presets.get_preset("P0")["layout"], "relative")       # the taped test layout (doc 02 Q12)
        for name in ("P1", "P2", "P3", "P4"):
            self.assertEqual(presets.get_preset(name)["layout"], "template")
        s0 = presets.get_preset("S0")
        self.assertEqual(s0["layout"], "none")
        self.assertEqual(s0["stub_volume_cm3"], 25.0)

    def test_subhole_rule_of_the_owner_decision(self):
        # 2026-11-15: sub1 from L_ring, sub2 from R_middle, 7.5 mm (doc 02 Q8, doc 04 D5); sub1 slides 10 mm since 2026-11-18 (9.5 before)
        for name in ("P1", "P2", "P3", "P4"):
            p = presets.get_preset(name)
            self.assertEqual((p["sub1_parent"], p["sub1_slide_mm"]), ("L_ring", 10.0), name)
            self.assertEqual((p["sub2_parent"], p["sub2_slide_mm"]), ("R_middle", 7.5), name)
        self.assertEqual(holes_layout.SUBHOLE_DEFAULTS, {"sub1": ("L_ring", 10.0), "sub2": ("R_middle", 7.5)})

    def test_layout_values(self):
        self.assertEqual(presets.get_preset("P2")["layout_centre_from_port_mm"], 23.0)       # the accepted slide (doc 06 3.11)
        self.assertEqual(presets.get_preset("P1")["layout_centre_from_port_mm"], 16.0)
        self.assertEqual(presets.get_preset("P1")["hand_overlap_mm"], 0.0)
        self.assertEqual(presets.get_preset("P2")["hand_overlap_mm"], 0.0)
        self.assertGreater(presets.get_preset("P3")["hand_overlap_mm"], 0.0)                 # the short deck overlaps the hands
        p4 = presets.get_preset("P4")                                                        # the seed (docs/08, 2026-11-17)
        self.assertEqual((p4["port_u"], p4["layout_centre_from_port_mm"], p4["hand_overlap_mm"]), (0.35, 20.0, 0.0))
        self.assertEqual((p4["exponent"], p4["bend_deg"]), (2.0, 0.0))

    def test_unknown_preset(self):
        with self.assertRaises(ValueError) as cm:
            presets.get_preset("P9")
        self.assertIn("P1", str(cm.exception))

    def test_bad_files_are_rejected(self):
        good = presets.DEFAULT_PATH.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "presets.toml"
            p.write_text(good.replace('schema = "ocarina-cavity-presets-v1"', 'schema = "something-else"'), encoding="utf-8")
            with self.assertRaises(ValueError):
                presets.load_presets(p)
            p.write_text(good.replace("exponent = 2.2\n", ""), encoding="utf-8")
            with self.assertRaises(ValueError) as cm:
                presets.load_presets(p)
            self.assertIn("exponent", str(cm.exception))
            p.write_text(good.replace("width  = [0.4584, 0.4859, 0.4676, 0.4034, 0.3301, 0.2659, 0.2200]",
                                      "width  = [0.4584, 0.4859, 0.4676]"), encoding="utf-8")
            with self.assertRaises(ValueError):
                presets.load_presets(p)
            p.write_text(good, encoding="utf-8")
            self.assertEqual(sorted(presets.load_presets(p)), sorted(presets.load_presets()))


class TestKernelBridge(unittest.TestCase):
    def test_the_kernel_comes_from_the_kernel_folder(self):
        k = kernel_bridge.kernel()
        self.assertEqual(k.dir, ROOT / "kernel")
        for name in kernel_bridge.KERNEL_MODULES:
            mod = getattr(k, name)
            self.assertEqual(pathlib.Path(mod.__file__).resolve().parent, ROOT / "kernel", name)
        self.assertIs(kernel_bridge.kernel(), k)                 # cached

    def test_a_foreign_module_with_a_kernel_name_is_not_reused(self):
        saved = kernel_bridge._cache
        fake = types.ModuleType("config")
        fake.__file__ = str(ROOT / "somewhere_else" / "config.py")
        real = sys.modules.get("config")
        try:
            kernel_bridge._cache = None
            sys.modules["config"] = fake
            k = kernel_bridge.kernel()
            self.assertIsNot(k.config, fake)
            self.assertEqual(pathlib.Path(k.config.__file__).resolve().parent, ROOT / "kernel")
        finally:
            kernel_bridge._cache = saved
            if real is not None:
                sys.modules["config"] = real

    def test_the_parameter_file(self):
        self.assertEqual(kernel_bridge.params_path(), ROOT / "params" / kernel_bridge.PARAMS_FILE)
        P = kernel_bridge.load_params()
        self.assertEqual(P["design"]["notes"][0], "A4")
        self.assertEqual(P["design"]["notes"][-1], "F6")
        self.assertEqual(len(P["fingering"]["holes"]), 12)
        self.assertEqual(P["hole_rules"]["wall_at_holes_mm"], 4.0)

    def test_every_ergonomic_limit_is_in_the_parameter_file(self):
        """The limits live in [ergonomics] of the TOML; the defaults in the module must be the same numbers."""
        E = kernel_bridge.load_params()["ergonomics"]
        self.assertEqual(sorted(E), sorted(ergonomics.DEFAULT_LIMITS))
        for key, default in ergonomics.DEFAULT_LIMITS.items():
            got = tuple(E[key]) if isinstance(E[key], list) else E[key]
            self.assertEqual(got, default, key)
        # the "Proposed" column of docs/06 section 5
        self.assertEqual(E["finger_pitch_mm"], [16.5, 20.5])
        self.assertEqual(E["hand_span_mm"], [50.0, 60.0])
        self.assertEqual(E["subhole_distance_mm"], [7.0, 11.0])
        self.assertEqual(E["subhole_off_normal_max_deg"], 20.0)
        self.assertEqual(E["rest_space_min_mm"], 10.0)
        self.assertEqual(E["index_along_mm"], [-22.0, 5.0])

    def test_the_kernel_sizes_a_body_through_the_bridge(self):
        k = kernel_bridge.kernel()
        sz = k.sizing.size_body(80.0, params=kernel_bridge.load_params())
        self.assertEqual(sz.voicing.version_hash, "b4620fbf3d67")           # rules of version 2 (2026-11-18)
        self.assertEqual([h.name for h in sz.holes.solutions["print"]][:2], ["sub1", "sub2"])
        self.assertAlmostEqual(sz.cavity_volume_for_mesh_cm3, 78.11, delta=0.01)


if __name__ == "__main__":
    unittest.main()
