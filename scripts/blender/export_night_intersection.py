"""Export an authored Night Intersection Blender collection to GLB.

Usage:
  blender --background path/to/night-intersection.blend \
    --python scripts/blender/export_night_intersection.py -- \
    --collection C0 \
    --out public/assets/3d/night-intersection/c0/c0.glb

The script intentionally validates only the durable minimum contract. Product quality
is still decided by the rendered QR1/QR2 acceptance gates, not by successful export.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import bpy


ROLE_COLLECTIONS = {
    "VISUAL_LOD0",
    "VISUAL_LOD1",
    "VISUAL_LOD2",
    "COLLISION",
    "NAV",
    "PERCH",
    "CLIMB",
    "PORTAL",
    "SPAWN",
    "LIGHT_ANCHOR",
}

REQUIRED_INITIAL_ROLES = {"VISUAL_LOD0"}


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--allow-empty-role",
        action="store_true",
        help="Allow required role collections to exist without mesh objects.",
    )
    return parser.parse_args(argv)


def descendants(collection: bpy.types.Collection) -> list[bpy.types.Collection]:
    result: list[bpy.types.Collection] = []

    def walk(node: bpy.types.Collection) -> None:
        result.append(node)
        for child in node.children:
            walk(child)

    walk(collection)
    return result


def all_objects(collection: bpy.types.Collection) -> list[bpy.types.Object]:
    seen: set[str] = set()
    objects: list[bpy.types.Object] = []
    for node in descendants(collection):
        for obj in node.objects:
            if obj.name in seen:
                continue
            seen.add(obj.name)
            objects.append(obj)
    return objects


def validate_scene(root: bpy.types.Collection, allow_empty_role: bool) -> None:
    scene = bpy.context.scene
    if scene.unit_settings.system != "METRIC":
        raise RuntimeError("Night Intersection Blender source must use Metric units")
    if abs(scene.unit_settings.scale_length - 1.0) > 1e-6:
        raise RuntimeError("Night Intersection requires 1 Blender unit = 1 meter")

    child_names = {child.name for child in root.children}
    missing = sorted(REQUIRED_INITIAL_ROLES - child_names)
    if missing:
        raise RuntimeError(
            f"{root.name} is missing required role collection(s): {', '.join(missing)}"
        )

    unknown_role_like = sorted(
        name
        for name in child_names
        if name.isupper() and name not in ROLE_COLLECTIONS
    )
    if unknown_role_like:
        print(
            "WARNING: unrecognized uppercase role collection(s): "
            + ", ".join(unknown_role_like)
        )

    lod0 = next(child for child in root.children if child.name == "VISUAL_LOD0")
    lod0_meshes = [obj for obj in all_objects(lod0) if obj.type == "MESH"]
    if not lod0_meshes and not allow_empty_role:
        raise RuntimeError("VISUAL_LOD0 must contain at least one mesh for runtime export")

    bad_names = [
        obj.name
        for obj in all_objects(root)
        if obj.name.startswith(("Cube.", "Cylinder.", "Plane.", "Sphere."))
    ]
    if bad_names:
        raise RuntimeError(
            "Production objects must use stable names instead of Blender defaults: "
            + ", ".join(sorted(bad_names)[:12])
        )


def select_collection_objects(root: bpy.types.Collection) -> list[bpy.types.Object]:
    bpy.ops.object.select_all(action="DESELECT")
    objects = all_objects(root)
    selectable = [obj for obj in objects if not obj.hide_render]
    for obj in selectable:
        obj.hide_set(False)
        obj.select_set(True)
    if selectable:
        bpy.context.view_layer.objects.active = selectable[0]
    return selectable


def export_glb(root: bpy.types.Collection, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    selected = select_collection_objects(root)
    if not selected:
        raise RuntimeError(f"No exportable objects found in collection {root.name}")

    bpy.ops.export_scene.gltf(
        filepath=str(out_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_texcoords=True,
        export_normals=True,
        export_tangents=True,
        export_cameras=False,
        export_lights=True,
        export_extras=True,
    )

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"GLB export did not produce a file: {out_path}")

    mesh_count = sum(1 for obj in selected if obj.type == "MESH")
    print(
        f"Exported {root.name}: {len(selected)} objects / {mesh_count} meshes -> {out_path}"
    )


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Collection not found: {args.collection}")

    validate_scene(root, args.allow_empty_role)
    export_glb(root, Path(args.out).resolve())


if __name__ == "__main__":
    main()
