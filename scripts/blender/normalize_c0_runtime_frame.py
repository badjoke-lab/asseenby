"""Normalize C0 authoring coordinates, metric PBR UVs, and export topology.

The deterministic C0 author script expresses placement as the runtime contract:
X = east/west, Y = vertical, Z = forward/depth. Blender itself is Z-up and the
glTF exporter converts Blender coordinates to glTF Y-up. Without this frame
normalization, C0 height/depth are exchanged and the authored world appears
rotated/flattened in Three.js.

This script wraps all top-level C0 objects in one +90 degree Blender-X frame:

    authored (x, y, z)
      -> Blender world (x, -z, y)
      -> glTF / Three.js (x, y, z)

It also reprojects the scanned Poly Haven asphalt and brick materials at their
physical capture scale. The original primitive cube UVs mapped one complete
texture across an entire building face, visibly stretching individual bricks
across several metres. Metric cube projection makes the 3 m brick scan and 2.1 m
asphalt scan repeat at approximately real-world scale before export.

Finally, exported mesh faces are triangulated before glTF export to keep tangent
generation deterministic for normal-mapped beveled/ngon geometry.

Usage:
  blender --background path/to/night-intersection-c0.blend \
    --python scripts/blender/normalize_c0_runtime_frame.py -- \
    --collection C0
"""

from __future__ import annotations

import argparse
import math
import sys

import bmesh
import bpy


FRAME_NAME = "c0_runtime_yup_frame"
PBR_METRIC_UV_METERS = {
    "c0_mat_brick_polyhaven": 3.0,
    "c0_mat_asphalt_polyhaven": 2.1,
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    return parser.parse_args(argv)


def descendants(collection: bpy.types.Collection) -> list[bpy.types.Collection]:
    result: list[bpy.types.Collection] = []

    def walk(node: bpy.types.Collection) -> None:
        result.append(node)
        for child in node.children:
            walk(child)

    walk(collection)
    return result


def collection_objects(root: bpy.types.Collection) -> list[bpy.types.Object]:
    seen: set[str] = set()
    objects: list[bpy.types.Object] = []
    for collection in descendants(root):
        for obj in collection.objects:
            if obj.name in seen:
                continue
            seen.add(obj.name)
            objects.append(obj)
    return objects


def metric_uv_scale_for(obj: bpy.types.Object) -> float | None:
    if obj.type != "MESH":
        return None
    for slot in obj.material_slots:
        material = slot.material
        if material is not None and material.name in PBR_METRIC_UV_METERS:
            return PBR_METRIC_UV_METERS[material.name]
    return None


def apply_metric_cube_uv(obj: bpy.types.Object, cube_size: float) -> None:
    if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    obj.hide_set(False)
    obj.hide_viewport = False
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(
        cube_size=cube_size,
        correct_aspect=True,
        clip_to_bounds=False,
        scale_to_bounds=False,
    )
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)


def apply_metric_uvs(objects: list[bpy.types.Object]) -> int:
    count = 0
    for obj in objects:
        cube_size = metric_uv_scale_for(obj)
        if cube_size is None:
            continue
        apply_metric_cube_uv(obj, cube_size)
        count += 1
    return count


def triangulate_meshes(objects: list[bpy.types.Object]) -> int:
    count = 0
    processed_meshes: set[str] = set()
    for obj in objects:
        if obj.type != "MESH" or obj.data.name in processed_meshes:
            continue
        processed_meshes.add(obj.data.name)
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        if bm.faces:
            bmesh.ops.triangulate(bm, faces=list(bm.faces))
            bm.to_mesh(mesh)
            mesh.update()
        bm.free()
        count += 1
    return count


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Collection not found: {args.collection}")

    existing = bpy.data.objects.get(FRAME_NAME)
    if existing is not None:
        raise RuntimeError(
            f"{FRAME_NAME} already exists; refusing to apply the runtime frame twice"
        )

    objects = collection_objects(root)
    metric_uv_objects = apply_metric_uvs(objects)
    triangulated = triangulate_meshes(objects)

    frame = bpy.data.objects.new(FRAME_NAME, None)
    frame.empty_display_type = "PLAIN_AXES"
    frame.rotation_euler.x = math.pi / 2
    frame["asseenby_axis_contract"] = "runtime XYZ -> Blender X,-Z,Y -> glTF XYZ"
    frame["asseenby_metric_uv_objects"] = metric_uv_objects
    frame["asseenby_export_triangulated"] = True
    root.objects.link(frame)

    top_level = [obj for obj in objects if obj.parent is None]
    for obj in top_level:
        obj.parent = frame

    if not top_level:
        raise RuntimeError("C0 has no top-level authored objects to normalize")

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        f"Normalized {len(top_level)} top-level C0 objects through {FRAME_NAME}; "
        f"metric PBR UVs applied to {metric_uv_objects} meshes; "
        f"triangulated {triangulated} unique meshes; saved {bpy.data.filepath}"
    )


if __name__ == "__main__":
    main()
