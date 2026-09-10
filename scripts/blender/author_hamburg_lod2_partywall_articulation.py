#!/usr/bin/env python3
"""Break up large visible blank Hamburg LoD2 walls with conservative vertical relief.

This supplements the existing large-wall base/cap/string-course pass.  It does not
invent windows.  Visible party/side walls receive shallow pilasters and narrow
shadow joints so they no longer read as a single giant CG slab at human scale.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
from pathlib import Path
import sys

import bpy

BASE_PATH = Path(__file__).with_name("author_hamburg_lod2_facades.py")
spec = importlib.util.spec_from_file_location("hamburg_partywall_helpers", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load facade helpers: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

VIEW_YAWS = (0.0, -1.05, 1.05)


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--obj", required=True, type=Path)
    parser.add_argument("--radius-m", type=float, default=105.0)
    parser.add_argument("--max-faces", type=int, default=20)
    return parser.parse_args(argv)


def view_score(seg):
    distance = float(seg["distance"])
    midx, midz = seg["mid"]
    if distance < 0.001:
        return 0.0, 0.0, 999.0
    dx, dz = float(midx) / distance, float(midz) / distance
    aligns = [dx * (-math.sin(yaw)) + dz * (-math.cos(yaw)) for yaw in VIEW_YAWS]
    best = max(-1.0, min(1.0, max(aligns)))
    view_angle = math.degrees(math.acos(best))
    initial_angle = math.degrees(math.acos(max(-1.0, min(1.0, -dz))))
    projected = float(seg["length"]) * float(seg["height"]) / max(distance * distance, 25.0)
    score = view_angle * 0.9 + distance * 0.12 - min(32.0, projected * 95.0) - min(12.0, float(seg["length"]) * 0.24)
    if initial_angle <= 28.0:
        score -= 20.0
    return view_angle, initial_angle, score


def main() -> None:
    cfg = parse_args()
    if not cfg.obj.is_file():
        raise RuntimeError(f"Hamburg LoD2 OBJ not found: {cfg.obj}")
    root = bpy.data.collections.get(cfg.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {cfg.collection}")
    visual = base.find_visual(root)

    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith("hamburg_facade_partywall_")]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)

    vertices, objects = base.load_obj(cfg.obj)
    candidates = []
    for object_name, faces in objects.items():
        if not object_name.endswith("_wall"):
            continue
        for face_index, face in enumerate(faces):
            seg = base.facade_segment([vertices[index] for index in face])
            if seg is None:
                continue
            length = float(seg["length"])
            height = float(seg["height"])
            if float(seg["distance"]) > cfg.radius_m or length < 8.0 or height < 10.0:
                continue
            view_angle, initial_angle, score = view_score(seg)
            if view_angle > 42.0 and initial_angle > 48.0:
                continue
            candidates.append((score, object_name, face_index, seg, view_angle, initial_angle))

    candidates.sort(key=lambda row: (row[0], row[4], row[3]["distance"]))
    selected = candidates[: max(1, cfg.max_faces)]
    if not selected:
        raise RuntimeError("No visible large Hamburg wall faces selected for party-wall articulation")

    mats = {
        "pier": base.material("hamburg_partywall_pier", (0.31, 0.29, 0.265, 1.0), 0.80),
        "joint": base.material("hamburg_partywall_joint", (0.055, 0.052, 0.048, 1.0), 0.90),
    }
    buckets = {}
    pier_count = 0
    joint_count = 0

    for _, object_name, face_index, seg, view_angle, initial_angle in selected:
        length = float(seg["length"])
        height = float(seg["height"])
        min_y = float(seg["min_y"])
        max_y = float(seg["max_y"])
        midx, midz = seg["mid"]
        u = seg["u"]
        n = seg["n"]
        ux, uz = u
        nx, nz = n
        seed = base.stable_int(f"party:{object_name}:{face_index}")

        target_spacing = 3.6 + (seed % 5) * 0.42
        cells = max(2, min(7, int(round(length / target_spacing))))
        spacing = length / cells
        vertical_h = max(2.0, height - 1.25)
        cy = min_y + 0.62 + vertical_h * 0.5

        # Internal pilasters are structural scale cues only.  They do not imply
        # openings and are intentionally shallow relative to the official wall.
        for boundary in range(1, cells):
            along = -length * 0.5 + boundary * spacing
            cx = midx + ux * along + nx * 0.12
            cz = midz + uz * along + nz * 0.12
            width = 0.13 + ((seed >> (boundary % 12)) & 1) * 0.04
            base.add_box_geometry(buckets, "pier", (cx, cy, cz), u, n, width, vertical_h, 0.18)
            pier_count += 1

        # One or two narrow darker joints prevent a broad side wall from reading
        # as a perfectly uniform slab without fabricating fenestration.
        joint_positions = [0.0]
        if length >= 15.0:
            joint_positions = [-0.22 * length, 0.22 * length]
        for along in joint_positions:
            cx = midx + ux * along + nx * 0.045
            cz = midz + uz * along + nz * 0.045
            base.add_box_geometry(buckets, "joint", (cx, cy, cz), u, n, 0.055, vertical_h * 0.96, 0.055)
            joint_count += 1

        print(
            "PARTYWALL", object_name, "face", face_index,
            "width", round(length, 3), "height", round(height, 3),
            "distance", round(float(seg["distance"]), 3),
            "view_angle", round(view_angle, 3), "initial_angle", round(initial_angle, 3),
        )

    created = 0
    for bucket, data in buckets.items():
        obj = base.build_bucket_object(visual, f"hamburg_facade_partywall_{bucket}", data, mats[bucket])
        if obj is not None:
            obj["partywall_articulation"] = True
            obj["partywall_claim"] = "generic vertical depth relief only; no invented windows"
            created += 1

    root["hamburg_facade_partywall_articulation"] = True
    root["hamburg_facade_partywall_version"] = 1
    root["hamburg_facade_partywall_face_count"] = len(selected)
    root["hamburg_facade_partywall_pier_count"] = pier_count
    root["hamburg_facade_partywall_joint_count"] = joint_count
    root["hamburg_facade_partywall_panorama_projection"] = False
    root["hamburg_facade_quality_version"] = 8
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg party-wall articulation: "
        f"faces={len(selected)} piers={pier_count} joints={joint_count} objects={created} removed={len(doomed)}"
    )


if __name__ == "__main__":
    main()
