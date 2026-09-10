#!/usr/bin/env python3
"""Add conservative depth to large visible Hamburg LoD2 walls left unfenestrated.

The detailed facade pass has a bounded 64-face budget. Large party/side walls that
remain outside that budget are legitimate official geometry, but a bare planar wall
reads as a giant CG box at human scale. This pass reproduces the v6 camera-priority
selection to identify walls that are *not* owned by the detailed facade layer, then
adds only non-photographic architectural relief: plinth, parapet/cornice, end returns
and restrained horizontal string courses. It never invents windows or merges faces.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
from pathlib import Path
import sys

import bpy

BASE_PATH = Path(__file__).with_name("author_hamburg_lod2_facades.py")
spec = importlib.util.spec_from_file_location("hamburg_facade_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load facade helpers: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

VIEW_YAWS = (0.0, -1.05, 1.05)
INITIAL_FORWARD_GUARANTEE_DEG = 22.0
DETAILED_FACE_BUDGET = 64
MIN_WIDTH_M = 8.0
MIN_HEIGHT_M = 8.0
MAX_VIEW_ANGLE_DEG = 38.0


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--obj", required=True, type=Path)
    parser.add_argument("--radius-m", type=float, default=95.0)
    parser.add_argument("--max-faces", type=int, default=28)
    return parser.parse_args(argv)


def view_metrics(seg):
    distance = float(seg["distance"])
    midx, midz = seg["mid"]
    if distance < 0.001:
        return 0.0, 0.0, 0.0
    dx, dz = float(midx) / distance, float(midz) / distance
    alignments = [
        dx * (-math.sin(yaw)) + dz * (-math.cos(yaw))
        for yaw in VIEW_YAWS
    ]
    best_alignment = max(-1.0, min(1.0, max(alignments)))
    view_angle = math.degrees(math.acos(best_alignment))
    initial_alignment = max(-1.0, min(1.0, -dz))
    initial_angle = math.degrees(math.acos(initial_alignment))
    projected_area = (float(seg["length"]) * float(seg["height"])) / max(distance * distance, 25.0)
    return view_angle, initial_angle, projected_area


def priority_score(seg):
    distance = float(seg["distance"])
    view_angle, initial_angle, projected_area = view_metrics(seg)
    angle_penalty = max(0.0, view_angle - 30.0) * 1.15
    area_bonus = min(28.0, projected_area * 70.0)
    midx, midz = seg["mid"]
    if distance < 0.001:
        best_alignment = 1.0
    else:
        dx, dz = float(midx) / distance, float(midz) / distance
        best_alignment = max(
            dx * (-math.sin(yaw)) + dz * (-math.cos(yaw))
            for yaw in VIEW_YAWS
        )
    outside_penalty = 55.0 if best_alignment < 0.10 else 0.0
    score = max(0.0, distance + angle_penalty + outside_penalty - area_bonus)
    if initial_angle <= INITIAL_FORWARD_GUARANTEE_DEG:
        score = max(0.0, score - 70.0)
    return score, view_angle, initial_angle, projected_area


def main() -> None:
    cfg = parse_args()
    if not cfg.obj.is_file():
        raise RuntimeError(f"Hamburg LoD2 OBJ not found: {cfg.obj}")
    root = bpy.data.collections.get(cfg.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {cfg.collection}")
    visual = base.find_visual(root)

    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith("hamburg_facade_largewall_")]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)

    vertices, objects = base.load_obj(cfg.obj)
    regular = []
    for object_name, faces in objects.items():
        if not object_name.endswith("_wall"):
            continue
        for face_index, face in enumerate(faces):
            points = [vertices[index] for index in face]
            seg = base.facade_segment(points)
            if seg is None:
                continue
            if float(seg["distance"]) > cfg.radius_m or float(seg["length"]) < 4.2 or float(seg["height"]) < 6.0:
                continue
            score, view_angle, initial_angle, projected_area = priority_score(seg)
            regular.append((score, object_name, face_index, seg, view_angle, initial_angle, projected_area))

    regular.sort(key=lambda row: (row[0], -float(row[3]["length"])))
    detailed_ids = {(row[1], row[2]) for row in regular[:DETAILED_FACE_BUDGET]}

    candidates = []
    for row in regular:
        score, object_name, face_index, seg, view_angle, initial_angle, projected_area = row
        if (object_name, face_index) in detailed_ids:
            continue
        length = float(seg["length"])
        height = float(seg["height"])
        if length < MIN_WIDTH_M or height < MIN_HEIGHT_M:
            continue
        if view_angle > MAX_VIEW_ANGLE_DEG and initial_angle > 52.0:
            continue
        # Large projected walls in the user's actual forward/turned views come first.
        relief_score = view_angle * 1.05 + float(seg["distance"]) * 0.17 - min(35.0, projected_area * 92.0) - min(12.0, length * 0.25)
        candidates.append((relief_score, object_name, face_index, seg, view_angle, initial_angle, projected_area))

    candidates.sort(key=lambda row: (row[0], row[4], row[3]["distance"]))
    selected = candidates[: max(1, cfg.max_faces)]
    if not selected:
        raise RuntimeError("No large visible undetailed Hamburg wall faces found for relief authoring")

    trim = base.material("hamburg_facade_largewall_trim", (0.34, 0.31, 0.275, 1.0), 0.74)
    joint = base.material("hamburg_facade_largewall_shadow_joint", (0.07, 0.068, 0.064, 1.0), 0.86)
    buckets = {}
    band_count = 0
    edge_count = 0

    for _, object_name, face_index, seg, view_angle, initial_angle, projected_area in selected:
        length = float(seg["length"])
        min_y = float(seg["min_y"])
        max_y = float(seg["max_y"])
        height = float(seg["height"])
        midx, midz = seg["mid"]
        ux, uz = seg["u"]
        nx, nz = seg["n"]
        usable = max(1.0, length - 0.28)

        # Base and cap are shallow enough to preserve the official envelope reading.
        base.add_box_geometry(
            buckets, "trim",
            (midx + nx * 0.075, min_y + 0.31, midz + nz * 0.075),
            (ux, uz), (nx, nz), usable, 0.62, 0.15,
        )
        base.add_box_geometry(
            buckets, "trim",
            (midx + nx * 0.115, max_y - 0.24, midz + nz * 0.115),
            (ux, uz), (nx, nz), usable, 0.38, 0.23,
        )

        # End returns reveal wall thickness/corners without asserting openings.
        edge_w = min(0.22, max(0.11, length * 0.012))
        vertical_h = max(1.5, height - 1.35)
        cy = min_y + 0.68 + vertical_h * 0.5
        for side in (-1.0, 1.0):
            along = side * max(0.0, length * 0.5 - edge_w * 0.55)
            cx = midx + ux * along + nx * 0.13
            cz = midz + uz * along + nz * 0.13
            base.add_box_geometry(
                buckets, "joint",
                (cx, cy, cz), (ux, uz), (nx, nz), edge_w, vertical_h, 0.16,
            )
            edge_count += 1

        # String courses provide scale on blank party walls. They are intentionally
        # generic structural cues, not claims about exact historic floor decoration.
        if height >= 10.0:
            floor_step = 3.0 if height < 18.0 else 3.15
            y = min_y + 3.15
            while y < max_y - 0.85:
                depth = 0.13 if band_count % 2 == 0 else 0.10
                base.add_box_geometry(
                    buckets, "trim",
                    (midx + nx * 0.085, y, midz + nz * 0.085),
                    (ux, uz), (nx, nz), usable, 0.10, depth,
                )
                band_count += 1
                y += floor_step

        print(
            "LARGE_WALL_RELIEF", object_name, "face", face_index,
            "width", round(length, 3), "height", round(height, 3),
            "distance", round(float(seg["distance"]), 3),
            "view_angle", round(view_angle, 3),
            "initial_angle", round(initial_angle, 3),
            "projected", round(projected_area, 4),
        )

    created = 0
    for bucket, data in buckets.items():
        mat = trim if bucket == "trim" else joint
        obj = base.build_bucket_object(visual, f"hamburg_facade_largewall_{bucket}", data, mat)
        if obj is not None:
            obj["large_wall_relief"] = True
            obj["large_wall_claim"] = "non-photographic scale/depth relief only; no invented windows"
            created += 1

    root["hamburg_facade_largewall_relief"] = True
    root["hamburg_facade_largewall_relief_version"] = 1
    root["hamburg_facade_largewall_face_count"] = len(selected)
    root["hamburg_facade_largewall_band_count"] = band_count
    root["hamburg_facade_largewall_edge_count"] = edge_count
    root["hamburg_facade_largewall_basis"] = "official LoD2 planes outside 64-face detailed budget; plinth/cap/end/string-course relief only"
    root["hamburg_facade_largewall_panorama_projection"] = False
    root["hamburg_facade_quality_version"] = 7
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg large-wall relief: "
        f"faces={len(selected)} bands={band_count} edges={edge_count} mesh_objects={created} removed_previous={len(doomed)}"
    )


if __name__ == "__main__":
    main()
