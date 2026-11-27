"""Headless Blender tests of the shell-edit build (PROTOTYPE, ocarina_addon/shell_edit.py).

    blender -b --factory-startup --python tests/run_blender_tests.py -- TestShellEdit       (about 6 minutes)

The add-on makes the solid shell and the solid neck (the base), they are edited, and the add-on finishes the
body. Nobody sculpts in a background run: the edits are the programs of tools/shell_edit_trial.py. The
cavity-mode step is switched off here (it has its own tests), so `cavity_mode_computed` is left out of the
lists of failures.
"""
import json
import pathlib
import sys
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import bmesh  # noqa: E402
import bpy  # noqa: E402

from ocarina_addon import api, body as body_mod, checks_geo, kernel_bridge, meshutil, report, shell_edit, voicing_geo  # noqa: E402
from tools import shell_edit_trial as trial  # noqa: E402

K = kernel_bridge.kernel()
P = kernel_bridge.load_params()
PRESET, V0 = "P4", 80.0
MM = 1e-3


def fresh_base():
    trial.reset_scene()
    base = shell_edit.build_base(PRESET, V0, params=P, verbose=False)
    return base, bpy.data.objects[base.object_names["shell"]], bpy.data.objects[base.object_names["neck"]]


def finish(shell, **kwargs):
    return shell_edit.finish(shell, params=P, cavity_mode_step=False, verbose=False, **kwargs)


def unexpected(body) -> list:
    return [c["name"] for c in checks_geo.unexpected_failures(body) if c["name"] != "cavity_mode_computed"]


def checks_of(body) -> dict:
    return {c["name"]: c for c in body.checks}


class TestShellEditBase(unittest.TestCase):
    """Step 1, and step 3 on a base that nobody edited: the body must be the one the one-step build makes."""

    @classmethod
    def setUpClass(cls):
        cls.one = api.build_body(PRESET, V0, params=P, cavity_mode_step=False, verbose=False)
        cls.base, cls.shell, cls.neck = fresh_base()
        cls.objects = {k: bpy.data.objects[n] for k, n in cls.base.object_names.items()}
        cls.state_before = cls.shell[shell_edit.BASE_PROPERTY]
        cls.body = finish(cls.shell)

    def test_the_base_is_two_solids_and_two_reference_objects(self):
        self.assertEqual(sorted(self.objects), ["chamber", "cuts", "neck", "shell"])
        for key in ("shell", "neck"):
            V, F = meshutil.arrays_from_mesh(self.objects[key].data)
            rep = meshutil.manifold_report(V, F)
            self.assertTrue(rep["manifold"] and rep["shells"] == 1, key)
            self.assertEqual(len(V) - len(F) // 2, 2, key)                       # a closed surface with no hole through it
            self.assertFalse(self.objects[key].hide_select, key)
        for key in ("chamber", "cuts"):
            self.assertTrue(self.objects[key].hide_select, key)
            self.assertEqual(self.objects[key].display_type, "WIRE", key)
        wall = P["hole_rules"]["wall_at_holes_mm"]
        self.assertAlmostEqual(meshutil.volume(*self.base.shell) / 1000.0,
                               meshutil.volume(*body_mod.plain_skin(self.base.cavity, wall)) / 1000.0, places=6)
        self.assertGreater(meshutil.volume(*self.base.shell), meshutil.volume(*self.base.air) + 40000.0)   # solid: not hollowed
        body_mod.check_chamber_inside(self.base.cavity, self.base.shell)        # does not raise

    def test_the_state_is_stored_on_the_shell(self):
        state = json.loads(self.state_before)
        self.assertEqual((state["body_id"], state["v0_cm3"], state["rating"], state["hole_key"]), ("P4-80", 80.0, "medium", "print"))
        self.assertEqual(state["preset"]["id"], "P4")
        self.assertEqual(state["voicing_hash"], K.sizing.size_body(V0, params=P).voicing.version_hash)
        self.assertEqual((state["neck"], state["chamber"], state["cuts"]), ("OCA_P4-80_neck", "OCA_P4-80_chamber", "OCA_P4-80_cuts"))
        self.assertIs(shell_edit.find_shell(self.neck), self.shell)
        self.assertIs(shell_edit.find_shell(self.shell), self.shell)
        self.assertIsNone(shell_edit.find_shell(self.objects["cuts"]))
        with self.assertRaises(ValueError):
            shell_edit.base_state(self.objects["cuts"])
        with self.assertRaises(ValueError):                                     # a stub has no shell to edit
            shell_edit.base_parts("S0", 25.0, params=P, verbose=False)

    def test_an_unedited_base_gives_the_one_step_body(self):
        a, b = self.body, self.one
        se = a.info["shell_edit"]
        self.assertEqual(se["rounds"], 1)
        self.assertTrue(se["has_neck"])
        self.assertEqual(a.voicing_hash, b.voicing_hash)
        self.assertEqual(a.body_id, "P4-80-edit")
        for ha, hb in zip(a.layout.holes, b.layout.holes):
            self.assertEqual(ha.name, hb.name)
            self.assertAlmostEqual(ha.d_mm, hb.d_mm, places=9, msg=ha.name)
            self.assertAlmostEqual(ha.wall_mm, hb.wall_mm, places=9, msg=ha.name)
            self.assertLess(float(np.linalg.norm(np.array(ha.centre) - np.array(hb.centre))), 1e-9, ha.name)
            self.assertLess(abs(se["holes"][ha.name]["added_mm"]), 1e-5, ha.name)
            self.assertLess(se["holes"][ha.name]["rim_relief_mm"], 1e-4, ha.name)
        self.assertAlmostEqual(meshutil.volume(*a.solid) / 1000.0, meshutil.volume(*b.solid) / 1000.0, places=4)
        self.assertAlmostEqual(a.air_capped_cm3, b.air_capped_cm3, places=5)
        self.assertEqual(unexpected(a), [])
        ca, cb = checks_of(a), checks_of(b)
        self.assertEqual(set(ca) - set(cb), {"shell_hole_walls", "shell_hole_rims", "windway_mouth_end"})
        for name in cb:
            self.assertEqual(ca[name]["status"], cb[name]["status"], name)
        for name in ("shell_hole_walls", "shell_hole_rims", "windway_mouth_end"):
            self.assertEqual(ca[name]["status"], "pass", name)
        self.assertIsNone(a.measurements["voicing"]["windway_mouth_blocked_after_mm"])
        self.assertIsNone(b.measurements["voicing"]["windway_mouth_blocked_after_mm"])
        self.assertNotIn("windway_mouth_end", cb)                                # a one-step body with an open pipe has no such line
        self.assertEqual(ca["wall_thickness"]["limit"], body_mod.SHELL_MIN_WALL_MM)
        self.assertEqual(cb["wall_thickness"]["limit"], 4.0)

    def test_the_wall_is_measured_on_every_preset(self):
        """On a base that nobody edited, every ray over every hole of every preset finds the shell, and finds it where
        the plain skin is. (A hole on the top line of the body sits on a line of the chamber's grid, and a ray that
        runs exactly through an edge of a mesh can slip between its triangles: such a ray is sent again from beside.)"""
        for pid in ("P1", "P2", "P3", "P4"):
            base = shell_edit.base_parts(pid, V0, params=P, verbose=False)
            envelope = meshutil.boolean(base.shell, base.neck, "UNION")[:2]
            over = body_mod.shell_over_holes(base.cavity, base.layout.holes, envelope, 4.0)
            self.assertEqual(len(over), 12, pid)
            for name, o in over.items():
                self.assertLess(abs(o["added_mm"]), 1e-4, f"{pid} {name}")
                self.assertAlmostEqual(o["wall_axis_mm"], 4.0, delta=0.02, msg=f"{pid} {name}")

    def test_the_base_is_hidden_and_kept(self):
        for key in ("shell", "neck", "chamber", "cuts"):
            self.assertTrue(self.objects[key].hide_viewport, key)
        self.assertEqual(self.shell[shell_edit.BASE_PROPERTY], self.state_before)
        result = bpy.data.objects["OCA_P4-80-edit"]
        self.assertEqual(result["oca_voicing_hash"], self.body.voicing_hash)
        self.assertIn("OCA_P4-80-edit_air", bpy.data.objects)


class TestShellEditSculpt(unittest.TestCase):
    """A base that was edited all over: a longer tail, a boss over one hole, a groove across another, relief,
    a thicker neck."""

    @classmethod
    def setUpClass(cls):
        cls.base, cls.shell, cls.neck = fresh_base()
        cls.edits = [edit(cls.base, cls.shell, cls.neck) for edit in trial.EDITS["sculpt"]]
        cls.outer = shell_edit.user_meshes(cls.shell)
        cls.body = finish(cls.shell)
        cls.se = cls.body.info["shell_edit"]
        cls.m = cls.body.measurements
        cls.checks = checks_of(cls.body)

    def test_it_finishes_with_no_unexpected_failure(self):
        self.assertEqual(unexpected(self.body), [])
        for name in ("topology", "booleans", "voicing_hash", "voicing_dimensions", "voicing_orientation", "voicing_keepouts",
                     "wall_thickness", "volume_capped_air", "volume_cavity_mesh", "hole_sizes_phase4_gate", "hole_axes",
                     "hole_spacing", "hole_to_voicing", "windway_floor_lip", "windway_mouth_end", "pocket_blend"):
            self.assertEqual(self.checks[name]["status"], "pass", name)
        self.assertEqual(self.body.voicing_hash, self.base.sizing.voicing.version_hash)        # the voicing is the base's
        self.assertLessEqual(self.se["rounds"], 4)

    def test_the_walls_were_measured_and_the_holes_sized_for_them(self):
        walls = {n: o["wall_mean_mm"] for n, o in self.se["holes"].items()}
        self.assertGreater(walls["R_ring"], 5.5)                                 # the 1.5 mm boss, plus relief
        self.assertTrue(all(3.5 < w < 6.5 for w in walls.values()), walls)
        old = {r.name: r.d_mm for r in body_mod.cut_rows(self.base.sizing, "print")}
        new = {h.name: h for h in self.body.layout.holes}
        self.assertGreater(new["R_ring"].d_mm, old["R_ring"] + 0.4)             # a deeper hole must be wider
        for n, h in new.items():
            self.assertAlmostEqual(h.wall_mm, walls[n], delta=body_mod.SHELL_DEPTH_TOL_MM, msg=n)
            self.assertAlmostEqual(self.se["holes"][n]["d_base_mm"], old[n], places=9)
        # measured again, on the chamber and the layout of the finished body
        again = body_mod.shell_over_holes(self.body.cavity, self.body.layout.holes, self.body.envelope, 4.0)
        for n, h in new.items():
            self.assertAlmostEqual(again[n]["wall_mean_mm"], h.wall_mm, delta=body_mod.SHELL_DEPTH_TOL_MM, msg=n)
        # the holes on the mesh are the kernel's, and the wall on each axis is the one that was measured before the cuts
        for r in self.m["holes"]:
            self.assertLess(abs(r["d_error_mm"]), 0.05, r["name"])
            self.assertLess(abs(r["chimney_error_mm"]), 0.05, r["name"])
            self.assertAlmostEqual(r["chimney_reference_mm"], self.se["holes"][r["name"]]["wall_axis_mm"] + r["tube_kernel_mm"], places=9)

    def test_the_scale_is_on_pitch_only_because_the_holes_changed(self):
        """The kernel's model with the diameters MEASURED on the finished body and the walls measured on the shell."""
        sz = self.body.sizing
        rows = sz.holes.solutions["print"]
        by = {r["name"]: r for r in self.m["holes"]}
        walls = body_mod.shell_over_holes(self.body.cavity, self.body.layout.holes, self.body.envelope, 4.0)
        d = [by[r.name]["d_measured_mm"] * MM for r in rows]
        ch = [(walls[r.name]["wall_mean_mm"] + r.tube_mm) * MM for r in rows]
        v0 = self.m["volume"]["capped_air_built_cm3"] * 1e-6
        f = K.holes.predict_scale(sz.X_w_mm * MM, v0, d, ch, rows[0].k_hole, sz.c_m_s)
        cents = [K.ocarina_kernel.cents(a, b) for a, b in zip(f, sz.f_targets_hz)]
        self.assertLess(max(abs(c) for c in cents), 2.0, cents)
        before = trial.scale_without_resizing(self.base, self.body)
        self.assertLess(min(before), -40.0, before)                             # with the base's holes: about 50 cents flat
        self.assertLess(abs(before[0]), 5.0)                                    # A4 (all closed) hardly moves

    def test_the_chamber_gave_way_to_the_deeper_holes(self):
        vol = self.m["volume"]
        self.assertLess(abs(vol["capped_air_measured_cm3"] / V0 - 1.0), 0.005)
        self.assertLess(abs(vol["capped_air_built_cm3"] / V0 - 1.0), 0.005)
        self.assertLess(vol["cavity_mesh_cm3"], self.se["chamber_base_cm3"] - 0.1)
        self.assertAlmostEqual(self.se["chamber_base_cm3"], self.base.sizing.cavity_volume_for_mesh_cm3, places=9)
        self.assertLess(self.body.cavity.length_mm, self.base.cavity.length_mm)

    def test_the_outside_is_the_users(self):
        one_len = float(np.ptp(self.base.shell[0][:, 0]))
        self.assertGreater(float(np.ptp(self.body.solid[0][:, 0])), one_len + 20.0)             # the tail is 25 mm longer
        self.assertGreater(self.se["shell_cm3"], meshutil.volume(*self.base.shell) / 1000.0 + 5.0)
        self.assertGreater(meshutil.volume(*self.outer[1]), meshutil.volume(*self.base.neck) * 1.05)   # the thicker neck
        self.assertGreater(self.m["wall"]["shell_min_mm"], 3.0)

    def test_the_soft_checks_warn_and_never_fail(self):
        self.assertEqual(self.checks["shell_hole_walls"]["status"], "warn")
        self.assertIn("R_ring", self.checks["shell_hole_walls"]["message"])
        self.assertEqual(self.checks["shell_hole_rims"]["status"], "warn")
        self.assertIn("L_middle", self.checks["shell_hole_rims"]["message"])
        self.assertGreater(self.se["holes"]["L_middle"]["rim_relief_mm"], 0.8)                   # the groove crosses its rim
        self.assertEqual(self.se["pushed_above_pad_limit"], {})                                  # no hole grew past its pad limit
        self.assertNotIn("pushed above the finger-pad limit", self.checks["shell_hole_walls"]["message"])
        self.assertNotIn("shell_hole_walls", [c["name"] for c in checks_geo.unexpected_failures(self.body)])
        self.assertIn("shell_hole_walls", [c["name"] for c in checks_geo.warnings(self.body)])

    def test_the_report_has_the_edited_shell(self):
        text = report.body_report(self.body, 1.0, "Written by a test.")
        self.assertIn("## Edited shell (shell-edit build, prototype)", text)
        self.assertIn("| R_ring | 5.", text)
        self.assertIn("sizing rounds", text)

    def test_finishing_again_after_another_edit(self):
        """The base is kept: the user edits on and finishes again."""
        self.assertTrue(self.shell.hide_viewport)
        trial.boss(self.base, self.shell, self.neck, name="R_index", height_mm=1.0)
        again = finish(self.shell, run_checks=False)
        self.assertTrue(self.shell.hide_viewport)                                # hidden again after the second finish
        self.assertGreater(again.info["shell_edit"]["holes"]["R_index"]["wall_mean_mm"],
                           self.se["holes"]["R_index"]["wall_mean_mm"] + 0.5)
        self.assertEqual(len([o for o in bpy.data.objects if o.name.startswith("OCA_P4-80-edit")]), 3)   # body, air, cavity: once


class TestShellEditRemesh(unittest.TestCase):
    """The shell and the neck as a sculpting session leaves them: another mesh altogether (voxel remesh) and a
    displacement, both as modifiers that are still on the objects when the body is finished."""

    @classmethod
    def setUpClass(cls):
        cls.base, cls.shell, cls.neck = fresh_base()
        trial.sculpt_modifiers(cls.base, cls.shell, cls.neck)
        cls.body = finish(cls.shell)

    def test_it_finishes_from_another_mesh(self):
        se = self.body.info["shell_edit"]
        self.assertGreater(se["shell_triangles"], 3 * len(self.base.shell[1]))   # the modifiers were applied
        self.assertEqual(len(self.shell.modifiers), 2)                            # and are still on the object
        self.assertEqual(unexpected(self.body), [])
        vol = self.body.measurements["volume"]
        self.assertLess(abs(vol["capped_air_measured_cm3"] / V0 - 1.0), 0.005)
        self.assertLessEqual(se["rounds"], 5)
        walls = [o["wall_mean_mm"] for o in se["holes"].values()]
        self.assertTrue(all(3.7 < w < 5.0 for w in walls), walls)
        for r in self.body.measurements["holes"]:
            self.assertLess(abs(r["d_error_mm"]), 0.05, r["name"])


class TestShellEditTooFar(unittest.TestCase):
    """Edits that went too far are refused with the reason, or fail a named check."""

    def test_a_shell_that_is_not_a_closed_solid(self):
        base, shell, neck = fresh_base()
        bm = bmesh.new()
        bm.from_mesh(shell.data)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.faces[100]], context="FACES")
        bm.to_mesh(shell.data)
        bm.free()
        with self.assertRaisesRegex(meshutil.GeometryError, "the shell is not a closed surface: 3 open edges"):
            finish(shell)

    def test_the_chamber_must_stay_inside(self):
        base, shell, neck = fresh_base()
        shell.location = (0.0, 6.0, 0.0)                                         # the object is moved, not its vertices
        with self.assertRaisesRegex(meshutil.GeometryError, "the chamber comes through the shell near"):
            finish(shell)

    def test_the_neck_must_touch_the_shell(self):
        base, shell, neck = fresh_base()
        neck.location = (0.0, -80.0, 0.0)
        with self.assertRaisesRegex(meshutil.GeometryError, "the neck does not touch the shell"):
            finish(shell)

    def test_an_object_that_is_not_a_base(self):
        trial.reset_scene()
        ob = bpy.data.objects.new("x", bpy.data.meshes.new("x"))
        with self.assertRaisesRegex(ValueError, "not the shell of a base"):
            shell_edit.finish(ob)

    def test_a_calibrated_finish_keeps_the_bases_voicing(self):
        # fitted constants (SYNTHETIC, with an invented eta_w for this base's hash) size the edited shell's holes for the
        # wall measured at each one; loading them does not make the base stale, because the voicing stays the base's
        base, shell, neck = fresh_base()
        h = base.state["voicing_hash"]
        cal = K.calibration.load_calibration(ROOT / "calibration" / "synthetic-fitted-constants.toml")
        cal.voicings = {h: {"eta_w": 0.8}}
        body = finish(shell, calibration=cal)
        self.assertEqual(body.voicing_hash, h)
        self.assertEqual(body.params["hole_key"], "fitted")
        self.assertEqual((body.info["calibration_info"]["eta_w"], body.info["calibration_info"]["eta_w_source"]), (0.8, "measured"))
        self.assertTrue(body.info["synthetic"])
        self.assertEqual(unexpected(body), [])
        over = body.info["shell_edit"]["holes"]
        for r in body.sizing.holes.solutions["fitted"]:
            self.assertAlmostEqual(r.wall_mm, over[r.name]["wall_sized_mm"], delta=body_mod.SHELL_DEPTH_TOL_MM, msg=r.name)

    def test_a_carved_shell_fails_the_wall_check(self):
        base, shell, neck = fresh_base()
        V, N = trial.vertices(shell), trial.normals_of(shell)
        pts = [trial.outer_point(h) for h in base.layout.holes] + [np.asarray(base.voicing.frame[0], float)]
        far = np.min([np.linalg.norm(V - p, axis=1) for p in pts], axis=0)
        i = int(np.argmax(far))                                                  # the place furthest from every hole and the window
        self.assertGreater(far[i], 20.0)
        d = np.linalg.norm(V - V[i], axis=1)
        trial.set_vertices(shell, V - (3.1 * np.exp(-(d / 5.0) ** 2))[:, None] * N)        # 0.9 mm is left: under three printed walls
        body = finish(shell)
        self.assertEqual(unexpected(body), ["wall_thickness"])
        c = checks_of(body)["wall_thickness"]
        self.assertLess(c["value"], body_mod.SHELL_MIN_WALL_MM)
        self.assertIn("edited shell: at least 1.32 mm, three printed walls", c["message"])
        self.assertEqual(body.info["shell_edit"]["rounds"], 1)                   # no hole is near: nothing was sized again

    def test_a_neck_longer_than_the_pipe_fails_a_named_check(self):
        base, shell, neck = fresh_base()
        v, vs = base.sizing.voicing, base.voicing
        zc = voicing_geo.windway_centre_z(v)
        o, fx, fy, fz = voicing_geo.pitched_frame(vs.frame, zc, float(vs.info["stub_pitch_deg"]))
        R = np.stack([fx, fy, fz], axis=1)
        Q = (trial.vertices(neck) - o) @ R
        xw = Q[:, 0] + v.window_length_mm
        Q[:, 0] -= 6.0 * np.clip(-(xw + 0.5 * v.windway_length_mm) / (0.5 * v.windway_length_mm), 0.0, 1.0)
        trial.set_vertices(neck, Q @ R.T + o)
        body = finish(shell)
        self.assertEqual(sorted(unexpected(body)), ["topology", "windway_mouth_end"])
        c = checks_of(body)["windway_mouth_end"]
        self.assertIn("the pipe is CLOSED at the mouth end", c["message"])
        # the value is where the plastic begins: the pipe cutter reaches about 1 mm past the end of the pipe, no further
        self.assertGreater(c["value"], 0.5)
        self.assertLess(c["value"], 2.5)
