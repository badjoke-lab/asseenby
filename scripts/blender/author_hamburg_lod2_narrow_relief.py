#!/usr/bin/env python3
"""Add conservative relief to narrow official Hamburg LoD2 wall faces.

Some real St. Georg building envelopes contain narrow chamfers and articulated wall
segments only ~0.5–3.8 m wide. The regular facade pass intentionally rejects these
surfaces because a normal multi-window module would be implausible. This pass keeps
each official wall plane's own direction and adds only non-photographic architectural
relief: plinth, cornice, edge trim and restrained horizontal bands. It does not merge
adjacent faces, invent window locations or project the panorama onto walls.
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
MIN_WIDTH_M = 0.45
MAX_WIDTH_M = 3.8
MIN_HEIGHT_M = 6.0
MAX_VIEW_ANGLE_DEG = 30.0


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--obj", required=True, type=Path)
    parser.add_argument("--radius-m", type=float, default=95.0)
    parser.add_argument("--max-faces", type=int, default=48)
    return parser.parse_args(argv)


def narrow_segment(points):
    if len(points) < 3:
        return None
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    height = max_y - min_y
    if height < MIN_HEIGHT_M:
        return None
    horizontal = base.unique_horizontal(points)
    if len(horizontal) < 2:
        return None
    best = None
    best_len = 0.0
    for index, a in enumerate(horizontal):
        for b in horizontal[index + 1 :]:
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            if length > best_len:
                best = (a, b)
                best_len = length
    if best is None or best_len < MIN_WIDTH_M or best_len >= MAX_WIDTH_M:
        return None
    a, b = best
    ux = (b[0] - a[0]) / best_len
    uz = (b[1] - a[1]) / best_len
    nx, nz = -uz, ux
    midx, midz = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
    if nx * (-midx) + nz * (-midz) < 0:
        nx, nz = -nx, -nz
    distance = math.hypot(midx, midz)
    if distance < 0.001:
        view_angle = 0.0
    else:
        dx, dz = midx / distance, midz / distance
        best_alignment = max(
            dx * (-math.sin(yaw)) + dz * (-math.cos(yaw))
            for yaw in VIEW_YAWS
        )
        view_angle = math.degrees(math.acos(max(-1.0, min(1.0, best_alignment))))
    return {
        "a": a,
        "b": b,
        "mid": (midx, midz),
        "u": (ux, uz),
        "n": (nx, nz),
        "length": best_len,
        "min_y": min_y,
        "max_y": max_y,
        "height": height,
        "distance": distance,
        "view_angle_deg": view_angle,
    }


def main() -> None:
    cfg = parse_args()
    if not cfg.obj.is_file():
        raise RuntimeError(f"Hamburg LoD2 OBJ not found: {cfg.obj}")
    root = bpy.data.collections.get(cfg.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {cfg.collection}")
    visual = base.find_visual(root)

    # Idempotent regeneration.
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith("hamburg_facade_narrow_")]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)

    vertices, objects = base.load_obj(cfg.obj)
    candidates = []
    for object_name, faces in objects.items():
        if not object_name.endswith("_wall"):
            continue
        for face_index, face in enumerate(faces):
            points = [vertices[index] for index in face]
            # A valid regular facade must remain owned exclusively by the main pass.
            if base.facade_segment(points) is not None:
                continue
            segment = narrow_segment(points)
            if segment is None:
                continue
            if segment["distance"] > cfg.radius_m or segment["view_angle_deg"] > MAX_VIEW_ANGLE_DEG:
                continue
            # View angle is more important than raw distance for these tiny surfaces.
            score = segment["view_angle_deg"] * 1.35 + segment["distance"] * 0.18 - segment["length"] * 0.9
            candidates.append((score, object_name, face_index, segment))

    candidates.sort(key=lambda row: (row[0], row[3]["distance"], -row[3]["length"]))
    selected = candidates[: max(1, cfg.max_faces)]
    if not selected:
        raise RuntimeError("No visible narrow Hamburg LoD2 wall faces found for relief authoring")

    trim = base.material("hamburg_facade_narrow_stone_trim", (0.39, 0.34, 0.28, 1.0), 0.72)
    shadow = base.material("hamburg_facade_narrow_shadow_joint", (0.095, 0.085, 0.075, 1.0), 0.82)
    buckets = {}
    band_count = 0
    edge_count = 0

    for _, object_name, face_index, seg in selected:
        length = float(seg["length"])
        min_y = float(seg["min_y"])
        max_y = float(seg["max_y"])
        height = float(seg["height"])
        midx, midz = seg["mid"]
        ux, uz = seg["u"]
        nx, nz = seg["n"]

        usable = max(0.24, length - 0.08)
        base.add_box_geometry(
            buckets, "trim",
            (midx + nx * 0.065, min_y + 0.27, midz + nz * 0.065),
            (ux, uz), (nx, nz), usable, 0.54, 0.13,
        )
        base.add_box_geometry(
            buckets, "trim",
            (midx + nx * 0.095, max_y - 0.19, midz + nz * 0.095),
            (ux, uz), (nx, nz), usable, 0.30, 0.19,
        )

        # Edge trims emphasize the real chamfer/corner instead of flattening it.
        edge_w = min(0.11, max(0.055, length * 0.10))
        vertical_h = max(1.0, height - 1.15)
        cy = min_y + 0.58 + vertical_h * 0.5
        for side in (-1.0, 1.0):
            along = side * max(0.0, length * 0.5 - edge_w * 0.5)
            cx = midx + ux * along + nx * 0.105
            cz = midz + uz * along + nz * 0.105
            base.add_box_geometry(
                buckets, "shadow",
                (cx, cy, cz), (ux, uz), (nx, nz), edge_w, vertical_h, 0.12,
            )
            edge_count += 1

        # Restrained horizontal relief tracks the same generalized floor rhythm already
        # used by the main structural pass, without asserting exact historic windows.
        if height >= 9.5:
            levels = max(1, min(6, int((height - 3.2) / 3.05)))
            for level in range(1, levels + 1):
                y = min_y + 3.15 + (level - 1) * ((height - 4.1) / max(levels, 1))
                if y >= max_y - 0.75:
                    continue
                base.add_box_geometry(
                    buckets, "trim",
                    (midx + nx * 0.075, y, midz + nz * 0.075),
                    (ux, uz), (nx, nz), usable, 0.095, 0.14,
                )
                band_count += 1

        print(
            "NARROW_RELIEF",
            object_name,
            "face", face_index,
            "width", round(length, 3),
            "height", round(height, 3),
            "distance", round(float(seg["distance"]), 3),
            "view_angle", round(float(seg["view_angle_deg"]), 3),
        )

    created = 0
    material_map = {"trim": trim, "shadow": shadow}
    for bucket, data in buckets.items():
        obj = base.build_bucket_object(visual, f"hamburg_facade_narrow_{bucket}", data, material_map[bucket])
        if obj is not None:
            obj["narrow_facade_relief"] = True
            obj["narrow_facade_claim"] = "architectural relief only; no exact window-position claim"
            created += 1

    root["hamburg_facade_narrow_relief"] = True
    root["hamburg_facade_narrow_relief_version"] = 1
    root["hamburg_facade_narrow_face_count"] = len(selected)
    root["hamburg_facade_narrow_band_count"] = band_count
    root["hamburg_facade_narrow_edge_count"] = edge_count
    root["hamburg_facade_narrow_basis"] = "individual official LoD2 wall planes; no face merging; plinth/cornice/edge/floor relief only"
    root["hamburg_facade_narrow_panorama_projection"] = False
    root["hamburg_facade_quality_version"] = 6
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg narrow facade relief: "
        f"faces={len(selected)} bands={band_count} edges={edge_count} mesh_objects={created} removed_previous={len(doomed)}"
    )


if __name__ == "__main__":
    main()
