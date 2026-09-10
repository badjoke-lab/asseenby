#!/usr/bin/env python3
"""Replace the most visible Hansaplatz v10 primitive tree proxies with authored PBR geometry.

The Hamburg LGV LoD2-DE 2026 shell remains the macro-geometry source of truth.
The documented ring of mature lindens around Hansabrunnen remains a spatial/design cue,
but exact individual tree positions and the species of the imported mesh are not claimed as
surveyed facts. Poly Haven ``tree_small_02`` is used as a CC0 broadleaf visual proxy only.

This pass deliberately removes the ico-sphere/cylinder linden proxies from VISUAL_LOD0.
It does not project panorama pixels onto walls and it does not close QR2 by itself; facade-by-
facade photo registration and further landmark/street-detail art passes remain required.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import bpy

ROOT_COLLECTION = "C0"
VISUAL_COLLECTION = "VISUAL_LOD0"
V10_TREE_PREFIX = "hamburg_hansaplatz_v10_linden_"
V12_PREFIX = "hamburg_hansaplatz_v12_"
FOUNTAIN_RUNTIME = (-7.377, 0.0, -30.192)
TREE_RING_RADIUS_M = 13.8
TREE_COUNT = 12
TARGET_TREE_HEIGHT_M = 9.0
ASSET_ID = "tree_small_02"
ASSET_PAGE = "https://polyhaven.com/a/tree_small_02"


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-dir", required=True)
    return parser.parse_args(argv)


def find_visual(root: bpy.types.Collection) -> bpy.types.Collection:
    visual = next((child for child in root.children if child.name == VISUAL_COLLECTION), None)
    if visual is None:
        raise RuntimeError(f"{ROOT_COLLECTION} is missing {VISUAL_COLLECTION}")
    return visual


def remove_named_prefix(prefix: str) -> int:
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith(prefix)]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def resolve_primary_gltf(asset_dir: Path) -> Path:
    manifest_path = asset_dir / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Missing Poly Haven manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("asset_id") != ASSET_ID:
        raise RuntimeError(f"Expected asset_id {ASSET_ID!r}, got {manifest.get('asset_id')!r}")
    if manifest.get("license") != "CC0-1.0":
        raise RuntimeError(f"Unexpected license for {ASSET_ID}: {manifest.get('license')!r}")
    primary = asset_dir / str(manifest.get("primary_gltf", ""))
    if not primary.is_file():
        raise RuntimeError(f"Primary glTF not found: {primary}")
    return primary


def import_joined_mesh(gltf_path: Path) -> bpy.types.Object:
    before = {obj.as_pointer() for obj in bpy.data.objects}
    bpy.ops.import_scene.gltf(filepath=str(gltf_path))
    imported = [obj for obj in bpy.data.objects if obj.as_pointer() not in before]
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError(f"Imported {gltf_path} but found no mesh objects")

    # Flatten imported parent transforms before joining so linked duplicates inherit one clean mesh.
    for obj in meshes:
        if obj.parent is not None:
            world = obj.matrix_world.copy()
            obj.parent = None
            obj.matrix_world = world

    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.hide_set(False)
        obj.select_set(True)
    source = meshes[0]
    bpy.context.view_layer.objects.active = source
    bpy.ops.object.join()
    source = bpy.context.view_layer.objects.active
    source.name = f"{V12_PREFIX}{ASSET_ID}_source"

    # Bake all import transforms, then normalize XY around the mesh centre and put its base at Z=0.
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    xs = [vertex.co.x for vertex in source.data.vertices]
    ys = [vertex.co.y for vertex in source.data.vertices]
    zs = [vertex.co.z for vertex in source.data.vertices]
    if not xs or not zs:
        raise RuntimeError("Imported broadleaf proxy mesh is empty")
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    zmin = min(zs)
    for vertex in source.data.vertices:
        vertex.co.x -= cx
        vertex.co.y -= cy
        vertex.co.z -= zmin

    source_height = max(vertex.co.z for vertex in source.data.vertices)
    if source_height <= 0.1:
        raise RuntimeError(f"Implausible source tree height: {source_height}")
    uniform_scale = TARGET_TREE_HEIGHT_M / source_height
    source.scale = (uniform_scale, uniform_scale, uniform_scale)
    bpy.context.view_layer.objects.active = source
    source.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    source.select_set(False)

    # Remove imported helper objects/empties. The joined mesh remains temporarily as the duplicate source.
    for obj in imported:
        if obj != source and obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    return source


def runtime_ground_to_blender(x: float, z: float) -> tuple[float, float, float]:
    # Runtime is Y-up; Blender source is Z-up. Matches the existing C0 authoring contract.
    return (x, -z, 0.0)


def place_tree_ring(source: bpy.types.Object, visual: bpy.types.Collection) -> list[bpy.types.Object]:
    cx, _, cz = FOUNTAIN_RUNTIME
    placed: list[bpy.types.Object] = []
    for index in range(TREE_COUNT):
        angle = (index / TREE_COUNT) * math.tau + 0.13
        # Retain the current bounded visual-reconstruction ring rather than inventing surveyed positions.
        radius = TREE_RING_RADIUS_M + (0.55 if index % 3 == 0 else -0.20 if index % 3 == 1 else 0.15)
        x = cx + math.sin(angle) * radius
        z = cz + math.cos(angle) * radius

        obj = bpy.data.objects.new(f"{V12_PREFIX}linden_ring_{index:02d}", source.data)
        obj.location = runtime_ground_to_blender(x, z)
        obj.rotation_euler[2] = angle + (index % 5) * 0.37
        variation = 0.94 + (index % 4) * 0.035
        obj.scale = (variation, variation, variation * (0.98 + (index % 3) * 0.02))
        visual.objects.link(obj)
        obj["quality_role"] = "primary-visible-nearfield-vegetation"
        obj["canonical_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
        obj["design_role"] = "broadleaf visual proxy for documented linden ring"
        obj["source_asset_id"] = ASSET_ID
        obj["source_asset_url"] = ASSET_PAGE
        obj["source_asset_license"] = "CC0-1.0"
        obj["species_mesh_claim"] = False
        obj["survey_position_claim"] = False
        obj["raw_panorama_projection"] = False
        placed.append(obj)
    return placed


def unlink_and_remove_source(source: bpy.types.Object) -> None:
    # Duplicates share the mesh datablock; the source object itself must not enter the C0 export.
    bpy.data.objects.remove(source, do_unlink=True)


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(ROOT_COLLECTION)
    if root is None:
        raise RuntimeError(f"Missing collection: {ROOT_COLLECTION}")
    visual = find_visual(root)

    removed_v12 = remove_named_prefix(V12_PREFIX)
    removed_v10_trees = remove_named_prefix(V10_TREE_PREFIX)
    if removed_v10_trees < TREE_COUNT:
        raise RuntimeError(
            f"Expected the v10 linden proxy layer to exist before replacement; removed only {removed_v10_trees} objects"
        )

    primary_gltf = resolve_primary_gltf(Path(args.asset_dir).resolve())
    source = import_joined_mesh(primary_gltf)
    placed = place_tree_ring(source, visual)
    unlink_and_remove_source(source)

    root["hamburg_hansaplatz_quality_version"] = 12
    root["hamburg_hansaplatz_v12_artpass"] = True
    root["hamburg_v12_tree_asset_id"] = ASSET_ID
    root["hamburg_v12_tree_asset_license"] = "CC0-1.0"
    root["hamburg_v12_tree_instance_count"] = len(placed)
    root["hamburg_v12_tree_target_height_m"] = TARGET_TREE_HEIGHT_M
    root["hamburg_v12_tree_species_claim"] = False
    root["hamburg_v12_tree_positions_surveyed"] = False
    root["hamburg_v12_facade_photo_registration_required"] = True
    root["hamburg_v12_quality_status"] = "art-pass-active; facade-by-facade photo registration remains open"
    root["raw_panorama_wall_projection"] = False

    if len(placed) != TREE_COUNT:
        raise RuntimeError(f"Expected {TREE_COUNT} tree instances, created {len(placed)}")
    if any(obj.name.startswith(V10_TREE_PREFIX) for obj in bpy.data.objects):
        raise RuntimeError("Primitive v10 linden proxy objects remain after v12 replacement")

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hansaplatz v12 vegetation art pass authored: "
        f"removed_v12={removed_v12} removed_v10_tree_objects={removed_v10_trees} "
        f"instances={len(placed)} asset={ASSET_ID} target_height={TARGET_TREE_HEIGHT_M}m"
    )


if __name__ == "__main__":
    main()
