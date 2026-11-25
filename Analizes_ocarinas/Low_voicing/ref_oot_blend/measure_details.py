"""The detail measures of measure_ref.py: the pipe, the lip, the shell, the dish and the mouthpiece of the reference."""
from __future__ import annotations

import numpy as np
import trimesh


def segments(mesh, origin, normal, u, v):
    """The cut of a mesh with a plane, as (n, 2, 2) segments in the plane's (u, v) coordinates."""
    V = mesh.vertices
    d = (V - origin) @ normal
    d[np.abs(d) < 1e-9] = 1e-9
    F = mesh.faces
    pos = d[F] > 0
    out = []
    for f in F[pos.any(axis=1) & ~pos.all(axis=1)]:
        s = d[f]
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if (s[a] > 0) != (s[b] > 0):
                t = s[a] / (s[a] - s[b])
                p = V[f[a]] + t * (V[f[b]] - V[f[a]]) - origin
                pts.append((p @ u, p @ v))
        if len(pts) == 2:
            out.append(pts)
    return np.array(out, float)


def _cross2(S1, S2):
    """Points where two sets of 2-D segments cross."""
    out = []
    for p, q in S1:
        r = q - p
        for a, b in S2:
            t = b - a
            den = r[0] * t[1] - r[1] * t[0]
            if abs(den) < 1e-12:
                continue
            u = ((a[0] - p[0]) * t[1] - (a[1] - p[1]) * t[0]) / den
            w = ((a[0] - p[0]) * r[1] - (a[1] - p[1]) * r[0]) / den
            if 0 <= u <= 1 and 0 <= w <= 1:
                out.append(p + u * r)
    return np.array(out)


def _dir_near(S, pt, radius, toward):
    """Mean direction of the segments within `radius` of pt that lie on the side `toward` (a 2-D vector)."""
    mid = S.mean(axis=1)
    near = S[np.linalg.norm(mid - pt, axis=1) < radius]
    near = near[((near.mean(axis=1) - pt) @ toward) > 0.3]
    d = near[:, 1] - near[:, 0]
    d[(d @ toward) < 0] *= -1
    d = d.sum(axis=0)
    return d / np.linalg.norm(d)


def details(M):
    X, Y, Z = np.eye(3)
    out = {}
    # ---- the pipe (windway cutter): seven rings of 10 points along z, from the mouth end to the exit
    P = M["pipe"].vertices
    order = np.argsort(-P[:, 2])
    rings = [P[order[i:i + 10]] for i in range(0, 70, 10)]
    cen = np.array([r.mean(axis=0) for r in rings])
    rows, length = [], 0.0
    for k, r in enumerate(rings):
        t = cen[min(k + 1, 6)] - cen[max(k - 1, 0)]
        t /= np.linalg.norm(t)                                          # from the mouth end toward the exit (-z)
        q = r - cen[k]
        q = q - np.outer(q @ t, t)
        _, v = np.linalg.eigh(q.T @ q)
        major, minor = q @ v[:, 2], q @ v[:, 1]
        if k:
            length += float(np.linalg.norm(cen[k] - cen[k - 1]))
        rows.append(dict(centre=cen[k].round(2).tolist(), along_mm=round(length, 2), width_mm=round(float(np.ptp(major)), 2),
                         height_mm=round(float(np.ptp(minor)), 2),
                         toward_thumb_face_deg=round(float(np.degrees(np.arctan2(t[1], -t[2]))), 1),
                         along_body_deg=round(float(np.degrees(np.arctan2(t[0], -t[2]))), 1)))
    out["pipe_rings_mouth_to_exit"] = rows
    out["pipe_length_mm"] = round(length, 2)
    # ---- the voicing in the cut across the body through the middle of the exit
    xe = float(cen[-1][0])
    o = np.array([xe, 0, 0.0])
    So, Sc = (segments(M[k], o, X, Y, Z) for k in ("outer", "cavity"))
    box = lambda S: S[(S[..., 0].min(axis=1) > 8) & (S[..., 1].min(axis=1) > 0) & (S[..., 1].max(axis=1) < 30)]      # noqa: E731
    cr = _cross2(box(So), box(Sc))
    cr = cr[np.argsort(cr[:, 1])]
    lip, top = cr[0], cr[-1]
    down = np.array([0.0, -1.0])                                        # away from the player
    wall_dir = _dir_near(Sc, lip, 4.0, down)                            # the chamber wall beyond the lip
    ramp_dir = _dir_near(So, lip, 4.0, down)                            # the dish surface beyond the lip
    ang = lambda d: float(np.degrees(np.arctan2(d[0], -d[1])))          # noqa: E731  from "away from the player", toward the thumb face
    jet = cen[-1] - cen[-2]
    jet2 = np.array([jet[1], jet[2]]) / np.hypot(jet[1], jet[2])
    exit_c = np.array([cen[-1][1], cen[-1][2]])
    n_jet = np.array([-jet2[1], jet2[0]])
    if n_jet[0] < 0:
        n_jet = -n_jet                                                  # toward the thumb face (outside)
    out["voicing_section"] = dict(
        x_of_cut=round(xe, 2), lip_yz=lip.round(2).tolist(), upper_meeting_yz=top.round(2).tolist(),
        all_meetings_yz=cr.round(2).tolist(),
        chamber_wall_beyond_lip_deg=round(ang(wall_dir), 1), dish_beyond_lip_deg=round(ang(ramp_dir), 1),
        lip_wedge_deg=round(ang(ramp_dir) - ang(wall_dir), 1), jet_deg=round(ang(jet2), 1),
        jet_against_chamber_wall_deg=round(ang(jet2) - ang(wall_dir), 1),
        exit_centre_yz=exit_c.round(2).tolist(), exit_to_lip_along_jet_mm=round(float((lip - exit_c) @ jet2), 2),
        lip_offset_from_jet_axis_mm_outside_positive=round(float((lip - exit_c) @ n_jet), 2))
    # ---- shell thickness: from the outer skin to the cavity mesh
    skin = M["outer"].vertices
    _, dist, _ = trimesh.proximity.closest_point(M["cavity"], skin)
    body_part = skin[:, 2] < 22.0                                       # leave the mouthpiece and its root out
    q = lambda m: [round(float(v), 2) for v in np.percentile(dist[m], [5, 25, 50, 75, 95])]      # noqa: E731
    lip3 = np.array([xe, lip[0], lip[1]])
    out["shell_thickness_mm_percentiles_5_25_50_75_95"] = dict(
        body_without_mouthpiece=q(body_part), thumb_face=q(body_part & (skin[:, 1] > 10)), finger_deck=q(body_part & (skin[:, 1] < -10)),
        far_edge=q(skin[:, 2] < -20), bulb_end=q(body_part & (skin[:, 0] > 60)), tail_end=q(body_part & (skin[:, 0] < -60)),
        around_the_window_within_14mm=q(np.linalg.norm(skin - lip3, axis=1) < 14.0))
    # ---- the dish: how far the skin lies under its own convex hull, on the thumb face
    hull = M["outer"].convex_hull
    _, dh, _ = trimesh.proximity.closest_point(hull, skin)
    dish = (dh > 0.6) & (skin[:, 1] > 8) & (skin[:, 2] < 24) & (np.abs(skin[:, 0] - xe) < 35)
    D = skin[dish]
    out["dish"] = dict(deepest_under_hull_mm=round(float(dh[dish].max()), 2),
                       along_body_x_mm=[round(float(D[:, 0].min()), 1), round(float(D[:, 0].max()), 1)],
                       toward_player_z_mm=[round(float(D[:, 2].min()), 1), round(float(D[:, 2].max()), 1)],
                       size_mm=[round(float(np.ptp(D[:, 0])), 1), round(float(np.ptp(D[:, 2])), 1)])
    # ---- the mouthpiece: its section at heights above the body
    neck = []
    for z in (30, 35, 40, 50, 60, 70, 76):
        S = segments(M["outer"], np.array([0, 0, float(z)]), Z, X, Y)
        pts = S.reshape(-1, 2)
        neck.append(dict(z=z, along_body_mm=round(float(np.ptp(pts[:, 0])), 1), across_thickness_mm=round(float(np.ptp(pts[:, 1])), 1),
                         centre_x=round(float(0.5 * (pts[:, 0].min() + pts[:, 0].max())), 1),
                         centre_y=round(float(0.5 * (pts[:, 1].min() + pts[:, 1].max())), 1)))
    out["mouthpiece_sections"] = neck
    b = M["outer"].bounds
    mid = segments(M["outer"], np.array([0.0, 0, 0]), Z, X, Y).reshape(-1, 2)
    acr = segments(M["outer"], np.array([xe, 0, 0.0]), X, Y, Z).reshape(-1, 2)
    out["body"] = dict(length_mm=round(float(b[1][0] - b[0][0]), 1), thickness_at_z0_mm=round(float(np.ptp(mid[:, 1])), 1),
                       mid_thickness_y=round(float(0.5 * (mid[:, 1].min() + mid[:, 1].max())), 2),
                       far_edge_z=round(float(b[0][2]), 1), tip_z=round(float(b[1][2]), 1),
                       thickness_at_the_window_cut_mm=round(float(np.ptp(acr[acr[:, 1] < 20][:, 0])), 1))
    return out
