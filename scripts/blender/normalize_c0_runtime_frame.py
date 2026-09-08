"""Normalize C0's runtime-style authoring coordinates into Blender's Z-up frame.

The deterministic C0 author script expresses placement as the runtime contract:
X = east/west, Y = vertical, Z = forward/depth. Blender itself is Z-up and the
glTF exporter converts Blender coordinates to glTF Y-up. Without this frame
normalization, C0 height/depth are exchanged and the authored world appears
rotated/flattened in Three.js.

This script wraps all top-level C0 objects in one +90 degree Blender-X frame:

    authored (x, y, z)
      -> Blender world (x, -z, y)
      -> glTF / Three.js (x, y, z)

Usage:
  blender --background path/to/night-intersection-c0.blend \
    --python scripts/blender/normalize_c0_runtime_frame.py -- \
    --collection C0
"""

from __future__ import annotations

import argparse
import math
import sys

import bpy


FRAME_NAME = "c0_runtime_yup_frame"


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

    frame = bpy.data.objects.new(FRAME_NAME, None)
    frame.empty_display_type = "PLAIN_AXES"
    frame.rotation_euler.x = math.pi / 2
    frame["asseenby_axis_contract"] = "runtime XYZ -> Blender X,-Z,Y -> glTF XYZ"
    root.objects.link(frame)

    objects = [obj for obj in collection_objects(root) if obj != frame]
    top_level = [obj for obj in objects if obj.parent is None]
    for obj in top_level:
        # Keep the object's existing transform as local runtime-style coordinates.
        # The rotated parent performs the single coordinate-basis conversion.
        obj.parent = frame

    if not top_level:
        raise RuntimeError("C0 has no top-level authored objects to normalize")

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        f"Normalized {len(top_level)} top-level C0 objects through {FRAME_NAME} "
        f"and saved {bpy.data.filepath}"
    )


if __name__ == "__main__":
    main()
