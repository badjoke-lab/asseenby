#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import bpy
from mathutils import Vector

root = bpy.data.collections.get("C0")
visual = next((c for c in root.children if c.name == "VISUAL_LOD0"), None) if root else None
objects = list(visual.all_objects) if visual else list(bpy.data.objects)

print("=== LEGACY HANSAPLATZ OBJECTS ===")
for obj in sorted((o for o in objects if o.name.startswith("hansaplatz_")), key=lambda o: o.name):
    print("LEGACY", obj.name, obj.type)

print("=== NEARFIELD NON-LOD2 MESHES ===")
rows = []
for obj in objects:
    if obj.type != "MESH":
        continue
    if obj.name.startswith("lod2_") or obj.name.startswith("hamburg_facade_authored_"):
        continue
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(point[i] for point in points) for i in range(3)]
    maxs = [max(point[i] for point in points) for i in range(3)]
    center_blender = [(mins[i] + maxs[i]) * 0.5 for i in range(3)]
    dims_blender = [maxs[i] - mins[i] for i in range(3)]
    # runtime XYZ = (Blender X, Blender Z, -Blender Y)
    rx, ry, rz = center_blender[0], center_blender[2], -center_blender[1]
    rdx, rdy, rdz = dims_blender[0], dims_blender[2], dims_blender[1]
    if abs(rx) > 80 or rz < -100 or rz > 25 or max(rdx, rdy, rdz) < 1.5:
        continue
    materials = [slot.material.name for slot in obj.material_slots if slot.material]
    rows.append(
        (
            rz,
            math.hypot(rx, rz),
            obj.name,
            tuple(round(v, 3) for v in (rx, ry, rz)),
            tuple(round(v, 3) for v in (rdx, rdy, rdz)),
            materials,
            {key: obj[key] for key in obj.keys()},
        )
    )

rows.sort(key=lambda row: (row[0], row[1], row[2]))
for row in rows:
    print("OBJ", row)
print("COUNT", len(rows))

print("=== FORWARD OCCLUDER CANDIDATES ===")
# Camera starts at runtime origin looking toward -Z. Flag large non-LoD2 meshes whose
# runtime bounds cross a central +/-12m horizontal corridor and lie ahead of camera.
for row in rows:
    rz, _, name, center, dims, materials, props = row
    rx, ry, _ = center
    dx, dy, dz = dims
    if rz < -3 and abs(rx) <= 12 + dx * 0.5 and dy >= 3.0 and dz >= 2.0:
        print("FORWARD", name, "center", center, "dims", dims, "materials", materials, "props", props)

print("=== FORWARD LOD2 FACADE SELECTION ===")
base_path = Path("scripts/blender/author_hamburg_lod2_facades.py").resolve()
spec = importlib.util.spec_from_file_location("hamburg_lod2_facade_diag", base_path)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load {base_path}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
obj_path = Path("assets-src/blender/night-intersection/hamburg-lod2/hansaplatz-lod2.obj")
vertices, lod2_objects = base.load_obj(obj_path)
view_yaws = (0.0, -1.05, 1.05)
candidates = []
rejected_forward = []
for object_name, faces in lod2_objects.items():
    if not object_name.endswith("_wall"):
        continue
    for face_index, face in enumerate(faces):
        points = [vertices[index] for index in face]
        seg = base.facade_segment(points)
        # Track faces whose raw centroid is in the initial forward cone even when facade_segment rejects them.
        raw_midx = sum(point[0] for point in points) / len(points)
        raw_midz = sum(point[2] for point in points) / len(points)
        raw_dist = math.hypot(raw_midx, raw_midz)
        raw_angle = 180.0
        if raw_dist > 0.001:
            raw_angle = math.degrees(math.acos(max(-1.0, min(1.0, (-raw_midz) / raw_dist))))
        if seg is None:
            if raw_dist <= 120.0 and raw_angle <= 20.0:
                ys = [p[1] for p in points]
                rejected_forward.append((raw_angle, raw_dist, object_name, face_index, max(ys)-min(ys), len(points)))
            continue
        actual_distance = float(seg["distance"])
        if actual_distance > 95.0:
            continue
        midx, midz = seg["mid"]
        direction_x = midx / max(actual_distance, 0.001)
        direction_z = midz / max(actual_distance, 0.001)
        alignments = []
        for yaw in view_yaws:
            forward_x = -math.sin(yaw)
            forward_z = -math.cos(yaw)
            alignments.append(direction_x * forward_x + direction_z * forward_z)
        best_alignment = max(-1.0, min(1.0, max(alignments)))
        view_angle_deg = math.degrees(math.acos(best_alignment))
        forward_alignment = max(-1.0, min(1.0, -direction_z))
        forward_angle_deg = math.degrees(math.acos(forward_alignment))
        projected_area = (float(seg["length"]) * float(seg["height"])) / max(actual_distance * actual_distance, 25.0)
        angle_penalty = max(0.0, view_angle_deg - 30.0) * 1.15
        area_bonus = min(28.0, projected_area * 70.0)
        outside_view_penalty = 55.0 if best_alignment < 0.10 else 0.0
        score = max(0.0, actual_distance + angle_penalty + outside_view_penalty - area_bonus)
        candidates.append((score, -float(seg["length"]), object_name, face_index, seg, forward_angle_deg, projected_area))

candidates.sort(key=lambda row: (row[0], row[1]))
selected_keys = {(row[2], row[3]) for row in candidates[:64]}
forward = [row for row in candidates if row[5] <= 22.0]
forward.sort(key=lambda row: (row[5], -row[6], row[0]))
for row in forward[:30]:
    score, _, object_name, face_index, seg, forward_angle, projected_area = row
    key = (object_name, face_index)
    print(
        "LOD2_FORWARD",
        "selected", key in selected_keys,
        "rank", candidates.index(row) + 1,
        "name", object_name,
        "face", face_index,
        "angle", round(forward_angle, 2),
        "distance", round(float(seg["distance"]), 2),
        "length", round(float(seg["length"]), 2),
        "height", round(float(seg["height"]), 2),
        "projected_area", round(projected_area, 4),
        "score", round(score, 2),
        "mid", tuple(round(v, 2) for v in seg["mid"]),
    )
print("FORWARD_VALID_COUNT", len(forward), "TOTAL_VALID_WITHIN_95", len(candidates))
for row in sorted(rejected_forward)[:30]:
    print("LOD2_FORWARD_REJECTED", row)
print("FORWARD_REJECTED_COUNT", len(rejected_forward))
