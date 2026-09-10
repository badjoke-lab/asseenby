#!/usr/bin/env python3
"""Break up large visible blank Hamburg LoD2 walls with conservative structural relief.

The v9 pass is camera-aware for the Hansaplatz street-level start view. It does
not invent windows or apply photographic wall projection. Visible party/side
walls receive shallow pilasters, shadow joints, horizontal courses and a low
plinth so broad LoD2 slabs retain their official envelope while reading with
human-scale depth under night lighting.
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

CAMERA_X = 0.0
CAMERA_Z = -34.0
VIEW_YAWS = (-0.18, -1.05, 1.05)


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--obj", required=True, type=Path)
    parser.add_argument("--radius-m", type=float, default=112.0)
    parser.add_argument("--max-faces", type=int, default=32)
    return parser.parse_args(argv)


def view_score(seg):
    midx, midz = seg["mid"]
    relx = float(midx) - CAMERA_X
    relz = float(midz) - CAMERA_Z
    camera_distance = math.hypot(relx, relz)
    if camera_distance < 0.001:
        return 0.0, 0.0, 0.0, -999.0
    dx, dz = relx / camera_distance, relz / camera_distance
    aligns = [dx * (-math.sin(yaw)) + dz * (-math.cos(yaw)) for yaw in VIEW_YAWS]
    best = max(-1.0, min(1.0, max(aligns)))
    view_angle = math.degrees(math.acos(best))
    initial_yaw = VIEW_YAWS[0]
    initial_align = dx * (-math.sin(initial_yaw)) + dz * (-math.cos(initial_yaw))
    initial_angle = math.degrees(math.acos(max(-1.0, min(1.0, initial_align))))
    projected = float(seg["length"]) * float(seg["height"]) / max(camera_distance * camera_distance, 16.0)
    score = view_angle * 0.8 + camera_distance * 0.10 - min(40.0, projected * 115.0) - min(14.0, float(seg["length"]) * 0.28)
    if initial_angle <= 30.0:
        score -= 30.0
    elif initial_angle <= 42.0:
        score -= 12.0
    return view_angle, initial_angle, camera_distance, score


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
            if float(seg["distance"]) > cfg.radius_m or length < 7.5 or height < 9.0:
                continue
            view_angle, initial_angle, camera_distance, score = view_score(seg)
            if view_angle > 48.0 and initial_angle > 55.0:
                continue
            candidates.append((score, object_name, face_index, seg, view_angle, initial_angle, camera_distance))

    candidates.sort(key=lambda row: (row[0], row[4], row[6]))
    selected = candidates[: max(1, cfg.max_faces)]
    if not selected:
        raise RuntimeError("No visible large Hamburg wall faces selected for party-wall articulation")

    mats = {
        "pier": base.material("hamburg_partywall_pier", (0.27, 0.255, 0.235, 1.0), 0.84),
        "joint": base.material("hamburg_partywall_joint", (0.045, 0.044, 0.042, 1.0), 0.94),
        "course": base.material("hamburg_partywall_course", (0.34, 0.315, 0.285, 1.0), 0.80),
        "plinth": base.material("hamburg_partywall_plinth", (0.16, 0.155, 0.145, 1.0), 0.90),
    }
    buckets = {}
    pier_count = 0
    joint_count = 0
    course_count = 0
    plinth_count = 0

    for _, object_name, face_index, seg, view_angle, initial_angle, camera_distance in selected:
        length = float(seg["length"])
        height = float(seg["height"])
        min_y = float(seg["min_y"])
        midx, midz = seg["mid"]
        u = seg["u"]
        n = seg["n"]
        ux, uz = u
        nx, nz = n
        seed = base.stable_int(f"party-v9:{object_name}:{face_index}")

        target_spacing = 3.2 + (seed % 6) * 0.38
        cells = max(2, min(9, int(round(length / target_spacing))))
        spacing = length / cells
        vertical_h = max(2.0, height - 1.0)
        cy = min_y + 0.5 + vertical_h * 0.5

        for boundary in range(1, cells):
            along = -length * 0.5 + boundary * spacing
            cx = midx + ux * along + nx * 0.15
            cz = midz + uz * along + nz * 0.15
            width = 0.14 + ((seed >> (boundary % 12)) & 1) * 0.05
            base.add_box_geometry(buckets, "pier", (cx, cy, cz), u, n, width, vertical_h, 0.22)
            pier_count += 1

        joint_positions = [0.0]
        if length >= 14.0:
            joint_positions = [-0.24 * length, 0.24 * length]
        for along in joint_positions:
            cx = midx + ux * along + nx * 0.052
            cz = midz + uz * along + nz * 0.052
            base.add_box_geometry(buckets, "joint", (cx, cy, cz), u, n, 0.065, vertical_h * 0.97, 0.065)
            joint_count += 1

        # Conservative horizontal courses give blank gables/storey-scale cues
        # without asserting openings that the official LoD2 source does not contain.
        course_slots = max(2, min(6, int(round(height / 3.4)) - 1))
        for slot in range(1, course_slots + 1):
            y = min_y + (height * slot / (course_slots + 1))
            cx = midx + nx * 0.13
            cz = midz + nz * 0.13
            base.add_box_geometry(
                buckets,
                "course",
                (cx, y, cz),
                u,
                n,
                max(1.0, length - 0.24),
                0.11 if slot % 2 else 0.085,
                0.18,
            )
            course_count += 1

        # Low dark plinth anchors the wall to the pavement and removes the
        # floating-cardboard edge visible in the v8 browser proof.
        plinth_h = min(0.72, max(0.42, height * 0.035))
        base.add_box_geometry(
            buckets,
            "plinth",
            (midx + nx * 0.17, min_y + plinth_h * 0.5, midz + nz * 0.17),
            u,
            n,
            max(1.0, length - 0.16),
            plinth_h,
            0.24,
        )
        plinth_count += 1

        print(
            "PARTYWALL_V9", object_name, "face", face_index,
            "width", round(length, 3), "height", round(height, 3),
            "origin_distance", round(float(seg["distance"]), 3),
            "camera_distance", round(camera_distance, 3),
            "view_angle", round(view_angle, 3), "initial_angle", round(initial_angle, 3),
            "courses", course_slots,
        )

    created = 0
    for bucket, data in buckets.items():
        obj = base.build_bucket_object(visual, f"hamburg_facade_partywall_{bucket}", data, mats[bucket])
        if obj is not None:
            obj["partywall_articulation"] = True
            obj["partywall_claim"] = "generic structural depth relief only; no invented windows"
            created += 1

    root["hamburg_facade_partywall_articulation"] = True
    root["hamburg_facade_partywall_version"] = 2
    root["hamburg_facade_partywall_camera_origin"] = f"{CAMERA_X:.1f},{CAMERA_Z:.1f}"
    root["hamburg_facade_partywall_initial_yaw"] = VIEW_YAWS[0]
    root["hamburg_facade_partywall_face_count"] = len(selected)
    root["hamburg_facade_partywall_pier_count"] = pier_count
    root["hamburg_facade_partywall_joint_count"] = joint_count
    root["hamburg_facade_partywall_course_count"] = course_count
    root["hamburg_facade_partywall_plinth_count"] = plinth_count
    root["hamburg_facade_partywall_panorama_projection"] = False
    root["hamburg_facade_quality_version"] = 9
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg v9 party-wall articulation: "
        f"faces={len(selected)} piers={pier_count} joints={joint_count} courses={course_count} "
        f"plinths={plinth_count} objects={created} removed={len(doomed)}"
    )


if __name__ == "__main__":
    main()
