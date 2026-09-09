#!/usr/bin/env python3
from __future__ import annotations

import math
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
