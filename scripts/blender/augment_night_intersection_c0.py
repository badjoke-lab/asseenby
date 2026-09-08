"""Augment normalized Night Intersection C0 with production-visible authored assets.

Run this after normalize_c0_runtime_frame.py. Poly Haven glTF files are already in
Blender's native Z-up frame, so imported models are positioned directly in the
normalized Blender world using the runtime->Blender mapping (x, y, z) -> (x, -z, y).

This pass deliberately removes the most visible procedural-looking Blender
placeholders (trees, van, benches, utility box and trash bin), replaces them with
CC0 authored models, adds real KHR_lights_punctual-compatible Blender lights, and
builds shallow storefront interiors so glass no longer terminates on an empty box.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector


ASSET_PLACEMENTS = [
    # asset_id, instance, runtime_xyz, runtime_yaw, scale
    ("street_lamp_02", "sw", (-12.8, 0.0, -16.5), 0.0, 0.82),
    ("street_lamp_02", "se", (12.8, 0.0, -16.5), math.pi, 0.82),
    ("street_lamp_02", "nw", (-12.8, 0.0, -39.5), 0.0, 0.82),
    ("street_lamp_02", "ne", (12.8, 0.0, -39.5), math.pi, 0.82),
    ("modular_street_seating", "sw", (-14.2, 0.0, -11.5), math.pi / 2, 0.64),
    ("modular_street_seating", "ne", (14.5, 0.0, -44.0), -math.pi / 2, 0.64),
    ("utility_box_02", "west", (-12.2, 0.0, -47.5), math.pi / 2, 0.84),
    ("metal_trash_can", "east", (12.4, 0.0, -8.2), 0.0, 0.82),
    ("covered_car", "north", (4.7, 0.0, -50.0), math.pi, 1.0),
    ("jacaranda_tree", "nw", (-14.8, 0.0, -51.5), 0.35, 0.29),
    ("jacaranda_tree", "se", (14.8, 0.0, -4.5), -0.65, 0.27),
]

PLACEHOLDER_PREFIXES = (
    "c0_bench_sw_",
    "c0_bench_ne_",
    "c0_utility_cabinet_w_",
    "c0_trash_bin_e_",
    "c0_delivery_van",
    "c0_tree_nw_",
    "c0_tree_se_",
)


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-root", required=True)
    parser.add_argument("--collection", default="C0")
    return parser.parse_args(argv)


def runtime_to_blender(position: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = position
    return (x, -z, y)


def ensure_visual_collection(root: bpy.types.Collection) -> bpy.types.Collection:
    visual = next((child for child in root.children if child.name == "VISUAL_LOD0"), None)
    if visual is None:
        raise RuntimeError("C0 is missing VISUAL_LOD0")
    return visual


def relink_object(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    if target not in obj.users_collection:
        target.objects.link(obj)
    for collection in list(obj.users_collection):
        if collection != target:
            collection.objects.unlink(obj)


def remove_placeholders() -> int:
    doomed = [
        obj for obj in list(bpy.data.objects)
        if obj.name.startswith(PLACEHOLDER_PREFIXES)
    ]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def bundle_gltf(asset_root: Path, asset_id: str) -> tuple[Path, dict]:
    directory = asset_root / asset_id
    manifest_path = directory / "manifest.json"
    if not manifest_path.exists():
        raise RuntimeError(f"Missing fetched Poly Haven manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    gltf_path = directory / manifest["primary_gltf"]
    if not gltf_path.exists():
        raise RuntimeError(f"Missing fetched Poly Haven glTF: {gltf_path}")
    return gltf_path, manifest


def bbox_world(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    corners: list[Vector] = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not corners:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    return (
        Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners))),
        Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners))),
    )


def import_polyhaven(
    visual: bpy.types.Collection,
    asset_root: Path,
    asset_id: str,
    instance: str,
    runtime_position: tuple[float, float, float],
    runtime_yaw: float,
    scale: float,
) -> bpy.types.Object:
    gltf_path, manifest = bundle_gltf(asset_root, asset_id)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(gltf_path))
    imported = [obj for obj in bpy.data.objects if obj not in before]
    if not imported:
        raise RuntimeError(f"Poly Haven import produced no objects: {asset_id}")

    imported_set = set(imported)
    top_level = [obj for obj in imported if obj.parent not in imported_set]
    wrapper = bpy.data.objects.new(f"c0_authored_{asset_id}_{instance}", None)
    visual.objects.link(wrapper)
    wrapper["source_provider"] = "Poly Haven"
    wrapper["source_asset_id"] = asset_id
    wrapper["source_url"] = manifest["canonical_page"]
    wrapper["source_files_hash"] = manifest.get("files_hash") or ""
    wrapper["source_resolution"] = manifest["resolution"]
    wrapper["license"] = "CC0-1.0"
    wrapper["authors"] = json.dumps(manifest.get("authors", {}), ensure_ascii=False)

    # Move the full imported hierarchy inside VISUAL_LOD0 so the canonical C0
    # exporter selects it, while preserving all object parent relationships.
    for obj in imported:
        relink_object(obj, visual)
        if obj.type == "MESH":
            obj.name = f"{wrapper.name}__{obj.name}"
            for polygon in obj.data.polygons:
                polygon.use_smooth = True
    for obj in top_level:
        world = obj.matrix_world.copy()
        obj.parent = wrapper
        obj.matrix_world = world

    min_bound, max_bound = bbox_world(imported)
    wrapper.scale.set_scalar(scale)
    wrapper.rotation_euler.z = runtime_yaw
    target = runtime_to_blender(runtime_position)
    # Poly Haven model origins vary. Anchor the lowest geometry point to the
    # authored sidewalk/road elevation instead of trusting the source origin.
    wrapper.location = (target[0], target[1], target[2] - min_bound.z * scale)
    wrapper["source_bounds_m"] = [
        round(max_bound.x - min_bound.x, 4),
        round(max_bound.y - min_bound.y, 4),
        round(max_bound.z - min_bound.z, 4),
    ]
    return wrapper


def principled_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        emission_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission_input:
            emission_input.default_value = emission
        strength = bsdf.inputs.get("Emission Strength")
        if strength:
            strength.default_value = emission_strength
    return material


def add_runtime_box(
    collection: bpy.types.Collection,
    name: str,
    runtime_position: tuple[float, float, float],
    runtime_dimensions: tuple[float, float, float],
    material: bpy.types.Material,
) -> bpy.types.Object:
    x, y, z = runtime_position
    dx, dy, dz = runtime_dimensions
    bpy.ops.mesh.primitive_cube_add(size=1, location=runtime_to_blender((x, y, z)))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (dx, dz, dy)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    relink_object(obj, collection)
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("authored_edge_softening", "BEVEL")
    bevel.width = min(0.045, min(runtime_dimensions) * 0.12)
    bevel.segments = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return obj


def add_storefront_interiors(visual: bpy.types.Collection) -> int:
    wall = principled_material("c0_interior_wall", (0.19, 0.16, 0.13, 1), 0.78)
    floor = principled_material("c0_interior_floor", (0.08, 0.055, 0.035, 1), 0.52)
    wood = principled_material("c0_interior_wood", (0.24, 0.095, 0.035, 1), 0.58)
    metal = principled_material("c0_interior_metal", (0.08, 0.085, 0.09, 1), 0.32, 0.65)
    glow = principled_material(
        "c0_interior_warm_glow",
        (0.9, 0.48, 0.17, 1),
        0.25,
        emission=(1.0, 0.34, 0.08, 1),
        emission_strength=5.0,
    )

    # prefix, center x, frontage z, interior direction (+z/-z)
    stores = [
        ("nw", -22.0, -40.35, -1.0),
        ("ne", 22.0, -40.35, -1.0),
        ("sw", -22.0, -15.15, 1.0),
        ("se", 22.0, -15.15, 1.0),
    ]
    created = 0
    for prefix, x, front_z, direction in stores:
        interior_center_z = front_z + direction * 2.35
        back_z = front_z + direction * 4.35
        add_runtime_box(visual, f"c0_store_{prefix}_interior_floor", (x, 0.16, interior_center_z), (10.2, 0.16, 4.7), floor)
        add_runtime_box(visual, f"c0_store_{prefix}_interior_back", (x, 2.0, back_z), (10.2, 3.7, 0.16), wall)
        add_runtime_box(visual, f"c0_store_{prefix}_counter", (x + 1.7, 0.92, front_z + direction * 2.35), (3.4, 1.0, 0.72), wood)
        for shelf_index, shelf_x in enumerate((x - 3.25, x - 1.65)):
            add_runtime_box(visual, f"c0_store_{prefix}_shelf_{shelf_index}_body", (shelf_x, 1.35, back_z - direction * 0.35), (1.15, 2.4, 0.48), metal)
            for row in range(3):
                add_runtime_box(
                    visual,
                    f"c0_store_{prefix}_shelf_{shelf_index}_row_{row}",
                    (shelf_x, 0.52 + row * 0.72, back_z - direction * 0.62),
                    (0.92, 0.44, 0.16),
                    wood if (row + shelf_index) % 2 else glow,
                )
        for panel_index, panel_x in enumerate((x - 2.2, x + 2.2)):
            add_runtime_box(
                visual,
                f"c0_store_{prefix}_ceiling_light_{panel_index}",
                (panel_x, 3.28, interior_center_z),
                (2.15, 0.05, 0.48),
                glow,
            )
        created += 1
    return created


def add_point_light(
    collection: bpy.types.Collection,
    name: str,
    runtime_position: tuple[float, float, float],
    color: tuple[float, float, float],
    energy: float,
    radius: float,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name=name, type="POINT")
    data.color = color
    data.energy = energy
    data.shadow_soft_size = radius
    obj = bpy.data.objects.new(name, data)
    obj.location = runtime_to_blender(runtime_position)
    collection.objects.link(obj)
    obj["asseenby_light_role"] = "authored_practical"
    return obj


def add_authored_lighting(root: bpy.types.Collection) -> int:
    light_collection = next((child for child in root.children if child.name == "LIGHT_ANCHOR"), None)
    if light_collection is None:
        light_collection = bpy.data.collections.new("LIGHT_ANCHOR")
        root.children.link(light_collection)

    lights = [
        ("c0_authored_lamp_sw", (-12.4, 6.2, -16.5), (1.0, 0.63, 0.34), 155.0, 1.05),
        ("c0_authored_lamp_se", (12.4, 6.2, -16.5), (1.0, 0.63, 0.34), 155.0, 1.05),
        ("c0_authored_lamp_nw", (-12.4, 6.2, -39.5), (1.0, 0.63, 0.34), 155.0, 1.05),
        ("c0_authored_lamp_ne", (12.4, 6.2, -39.5), (1.0, 0.63, 0.34), 155.0, 1.05),
        ("c0_authored_store_nw", (-22.0, 2.5, -41.4), (1.0, 0.46, 0.22), 95.0, 0.7),
        ("c0_authored_store_ne", (22.0, 2.5, -41.4), (0.40, 0.67, 1.0), 82.0, 0.7),
        ("c0_authored_store_sw", (-22.0, 2.5, -14.1), (1.0, 0.46, 0.22), 95.0, 0.7),
        ("c0_authored_store_se", (22.0, 2.5, -14.1), (0.40, 0.67, 1.0), 82.0, 0.7),
    ]
    for args in lights:
        add_point_light(light_collection, *args)
    return len(lights)


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Collection not found: {args.collection}")
    if bpy.data.objects.get("c0_runtime_yup_frame") is None:
        raise RuntimeError("C0 must be coordinate-normalized before authored asset augmentation")
    visual = ensure_visual_collection(root)
    asset_root = Path(args.asset_root).resolve()

    removed = remove_placeholders()
    imported: list[bpy.types.Object] = []
    for placement in ASSET_PLACEMENTS:
        imported.append(import_polyhaven(visual, asset_root, *placement))

    interiors = add_storefront_interiors(visual)
    lights = add_authored_lighting(root)

    # Preserve all source image dependencies in the canonical authoring file so
    # a future export does not rely on the ephemeral Actions download cache.
    bpy.ops.file.pack_all()
    root["qr2_authored_prop_pass"] = "Poly Haven CC0 replacements + storefront depth + authored practical lights"
    root["qr2_authored_prop_instances"] = len(imported)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        f"QR2 authored augmentation: removed {removed} placeholder objects; "
        f"imported {len(imported)} authored model instances; "
        f"built {interiors} storefront interiors; added {lights} authored lights"
    )


if __name__ == "__main__":
    main()
