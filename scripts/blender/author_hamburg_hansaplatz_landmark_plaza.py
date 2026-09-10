#!/usr/bin/env python3
"""Author a source-grounded Hansaplatz landmark/plaza layer over the Hamburg LoD2 C0.

The Hamburg LGV LoD2 building envelope remains the macro-geometry source of truth.
This pass adds the central public-space cues that are absent from LoD2 buildings:
- a reconstruction proxy for the 17 m Hansabrunnen at the photo-registered square centre;
- a central granite-small-paver field;
- a ring of mature linden-tree visual proxies around the fountain.

Authoritative facts used here:
- Hamburg describes the restored Hansabrunnen as the 17 m landmark in the middle of Hansaplatz.
- Hamburg's Hansaplatz design guide specifies Granitkleinpflaster in the traffic-free centre and
  says the historic fountain is enclosed by a circle of large-crowned lindens.

The exact sculptural meshes, paving-zone dimensions, and individual tree survey positions are
not claimed as authoritative. They are explicitly tagged as reconstruction proxies. The Poly
Haven panorama remains photographic reference/environment evidence only and is never projected
onto permanent wall geometry by this script.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

import bpy

ROOT_COLLECTION = "C0"
PREFIX = "hamburg_hansaplatz_v10_"
FOUNTAIN_RUNTIME = (-7.377, 0.0, -30.192)
FOUNTAIN_HEIGHT_M = 17.0
TREE_RING_RADIUS_M = 13.8
TREE_COUNT = 12

HAMBURG_PLACE_SOURCE = "https://www.hamburg.de/tourismus/sehenswuerdigkeiten/hansaplatz-hamburg-360882"
HAMBURG_DESIGN_SOURCE = "https://www.hamburg.de/contentblob/4498572/c9f8de8272cf87cba874c4af9de5f84b"
PHOTO_REFERENCE = "https://polyhaven.com/a/hansaplatz"


def runtime_to_blender(point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = point
    return (x, -z, y)


def find_visual(root: bpy.types.Collection) -> bpy.types.Collection:
    visual = next((child for child in root.children if child.name == "VISUAL_LOD0"), None)
    if visual is None:
        raise RuntimeError("C0 is missing VISUAL_LOD0")
    return visual


def relink(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    if collection not in obj.users_collection:
        collection.objects.link(obj)
    for current in list(obj.users_collection):
        if current != collection:
            current.objects.unlink(obj)


def material(name: str, color: tuple[float, float, float, float], roughness: float, metallic: float = 0.0) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    if bsdf.inputs.get("Metallic") is not None:
        bsdf.inputs["Metallic"].default_value = metallic
    mat["reconstruction_role"] = "Hansaplatz v10 source-grounded visual proxy"
    return mat


def granite_material() -> bpy.types.Material:
    name = "hamburg_hansaplatz_v10_granite_small_paver"
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.18, 0.175, 0.165, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.88
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = "granite_aggregate"
    noise.inputs["Scale"].default_value = 34.0
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.name = "granite_joint_microrelief"
    bump.inputs["Strength"].default_value = 0.24
    bump.inputs["Distance"].default_value = 0.025
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat["source_fact"] = "central Hansaplatz uses Granitkleinpflaster"
    mat["source_url"] = HAMBURG_DESIGN_SOURCE
    mat["exact_pattern_claim"] = False
    return mat


def add_box(collection: bpy.types.Collection, name: str, runtime_position: tuple[float, float, float], dimensions: tuple[float, float, float], mat: bpy.types.Material, bevel: float = 0.0) -> bpy.types.Object:
    dx, dy, dz = dimensions
    bpy.ops.mesh.primitive_cube_add(size=1, location=runtime_to_blender(runtime_position))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (dx, dz, dy)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    relink(obj, collection)
    obj.data.materials.append(mat)
    if bevel > 0.0:
        mod = obj.modifiers.new("edge_softening", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        obj.select_set(False)
    return obj


def add_cylinder(collection: bpy.types.Collection, name: str, runtime_position: tuple[float, float, float], radius: float, height: float, mat: bpy.types.Material, vertices: int = 16) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=height, location=runtime_to_blender(runtime_position))
    obj = bpy.context.object
    obj.name = name
    relink(obj, collection)
    obj.data.materials.append(mat)
    return obj


def add_cone(collection: bpy.types.Collection, name: str, runtime_position: tuple[float, float, float], radius1: float, radius2: float, height: float, mat: bpy.types.Material, vertices: int = 16) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=height, location=runtime_to_blender(runtime_position))
    obj = bpy.context.object
    obj.name = name
    relink(obj, collection)
    obj.data.materials.append(mat)
    return obj


def add_ico(collection: bpy.types.Collection, name: str, runtime_position: tuple[float, float, float], radius: float, scale: tuple[float, float, float], mat: bpy.types.Material, subdivisions: int = 2) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=radius, location=runtime_to_blender(runtime_position))
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    relink(obj, collection)
    obj.data.materials.append(mat)
    return obj


def tag(obj: bpy.types.Object, role: str, exact_geometry: bool = False) -> None:
    obj["hansaplatz_v10"] = True
    obj["role"] = role
    obj["canonical_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
    obj["photo_origin_wgs84"] = "53.554451,10.012056"
    obj["photo_reference"] = PHOTO_REFERENCE
    obj["exact_geometry_claim"] = exact_geometry


def remove_previous() -> int:
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith(PREFIX)]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def author_paving(visual: bpy.types.Collection, granite: bpy.types.Material) -> int:
    # Dimensions are a bounded visual reconstruction, not a surveyed Zone-1 polygon.
    # The tile grid supplies readable small-paver scale without pretending to reproduce each stone.
    cx, _, cz = FOUNTAIN_RUNTIME
    created = 0
    tile = 2.0
    half = 10
    for ix in range(-half, half + 1):
        for iz in range(-half, half + 1):
            x = cx + ix * tile
            z = cz + iz * tile
            if math.hypot(x - cx, z - cz) > 20.0:
                continue
            obj = add_box(
                visual,
                f"{PREFIX}granite_{ix:+03d}_{iz:+03d}",
                (x, -0.035, z),
                (1.94, 0.055, 1.94),
                granite,
                bevel=0.018,
            )
            tag(obj, "central_granite_small_paver_proxy")
            created += 1
    return created


def author_fountain(visual: bpy.types.Collection) -> int:
    stone = material("hamburg_hansaplatz_v10_fountain_dark_stone", (0.115, 0.105, 0.095, 1.0), 0.72)
    stone_mid = material("hamburg_hansaplatz_v10_fountain_mid_stone", (0.17, 0.155, 0.135, 1.0), 0.76)
    bronze = material("hamburg_hansaplatz_v10_fountain_bronze", (0.12, 0.105, 0.075, 1.0), 0.52, metallic=0.56)
    water = material("hamburg_hansaplatz_v10_fountain_water", (0.035, 0.07, 0.075, 1.0), 0.22, metallic=0.08)
    cx, _, cz = FOUNTAIN_RUNTIME
    created = 0

    def cyl(suffix: str, y: float, radius: float, height: float, mat: bpy.types.Material, vertices: int = 8, role: str = "hansabrunnen_reconstruction_proxy"):
        nonlocal created
        obj = add_cylinder(visual, f"{PREFIX}fountain_{suffix}", (cx, y, cz), radius, height, mat, vertices)
        tag(obj, role)
        created += 1
        return obj

    cyl("lower_step", 0.12, 4.15, 0.24, stone_mid, 12)
    cyl("basin_wall", 0.40, 3.65, 0.42, stone, 12)
    cyl("water_surface", 0.58, 3.26, 0.07, water, 32, "hansabrunnen_water_proxy")
    cyl("inner_plinth", 0.82, 2.55, 0.46, stone_mid, 8)
    cyl("figure_stage", 1.38, 1.90, 0.66, stone, 8)
    cyl("lower_pedestal", 2.35, 1.28, 1.30, stone_mid, 8)

    # Four cardinal figure silhouettes: preserve the monument's four-sided human-scale articulation
    # without claiming scanned sculpture meshes.
    for index, angle in enumerate((0.0, math.pi / 2, math.pi, 3 * math.pi / 2)):
        sx = cx + math.sin(angle) * 1.48
        sz = cz + math.cos(angle) * 1.48
        body = add_cylinder(visual, f"{PREFIX}fountain_figure_{index}_body", (sx, 3.25, sz), 0.26, 1.45, bronze, 10)
        tag(body, "hansabrunnen_historical_figure_silhouette_proxy")
        head = add_ico(visual, f"{PREFIX}fountain_figure_{index}_head", (sx, 4.15, sz), 0.29, (0.92, 0.92, 1.08), bronze, 1)
        tag(head, "hansabrunnen_historical_figure_silhouette_proxy")
        created += 2

    cyl("mid_column", 5.25, 0.86, 3.30, stone_mid, 8)
    cyl("heraldic_band", 7.05, 1.08, 0.36, stone, 8)
    cyl("upper_column", 9.30, 0.63, 4.20, stone_mid, 8)
    add_cone(visual, f"{PREFIX}fountain_crown_transition", (cx, 11.85, cz), 0.92, 0.46, 0.90, stone, 8)
    tag(bpy.context.object, "hansabrunnen_upper_reconstruction_proxy")
    created += 1
    cyl("upper_cap", 12.48, 0.72, 0.36, stone, 8)

    # Top allegorical statue proxy; total top is constrained to ~17 m.
    statue_body = add_cylinder(visual, f"{PREFIX}fountain_top_figure_body", (cx, 14.05, cz), 0.28, 2.55, bronze, 10)
    tag(statue_body, "hansabrunnen_top_allegory_silhouette_proxy")
    statue_head = add_ico(visual, f"{PREFIX}fountain_top_figure_head", (cx, 15.55, cz), 0.34, (0.95, 0.95, 1.1), bronze, 2)
    tag(statue_head, "hansabrunnen_top_allegory_silhouette_proxy")
    spear = add_cylinder(visual, f"{PREFIX}fountain_top_vertical_accent", (cx + 0.36, 15.35, cz), 0.055, 3.30, bronze, 8)
    tag(spear, "hansabrunnen_top_vertical_accent_proxy")
    created += 3

    return created


def author_linden_ring(visual: bpy.types.Collection) -> int:
    bark = material("hamburg_hansaplatz_v10_linden_bark", (0.115, 0.082, 0.052, 1.0), 0.93)
    leaf_a = material("hamburg_hansaplatz_v10_linden_leaf_a", (0.075, 0.13, 0.055, 1.0), 0.92)
    leaf_b = material("hamburg_hansaplatz_v10_linden_leaf_b", (0.095, 0.155, 0.065, 1.0), 0.90)
    cx, _, cz = FOUNTAIN_RUNTIME
    created = 0
    for i in range(TREE_COUNT):
        angle = (i / TREE_COUNT) * math.tau + 0.13
        radius = TREE_RING_RADIUS_M + (0.55 if i % 3 == 0 else -0.20 if i % 3 == 1 else 0.15)
        x = cx + math.sin(angle) * radius
        z = cz + math.cos(angle) * radius
        trunk_h = 4.4 + (i % 4) * 0.18
        trunk = add_cylinder(visual, f"{PREFIX}linden_{i:02d}_trunk", (x, trunk_h / 2, z), 0.27 + (i % 3) * 0.025, trunk_h, bark, 10)
        tag(trunk, "mature_linden_visual_proxy")
        trunk["species_reference"] = "Tilia sp. (Linden)"
        trunk["survey_position_claim"] = False
        created += 1
        canopy_y = trunk_h + 2.15
        for lobe in range(3):
            a = angle + lobe * 2.1
            lx = x + math.sin(a) * (0.85 if lobe else 0.0)
            lz = z + math.cos(a) * (0.85 if lobe else 0.0)
            ly = canopy_y + (0.25 if lobe == 0 else -0.15)
            leaf = add_ico(
                visual,
                f"{PREFIX}linden_{i:02d}_canopy_{lobe}",
                (lx, ly, lz),
                2.75,
                (1.12, 1.04, 0.82),
                leaf_a if (i + lobe) % 2 == 0 else leaf_b,
                2,
            )
            tag(leaf, "large_crowned_linden_canopy_visual_proxy")
            leaf["species_reference"] = "Tilia sp. (Linden)"
            leaf["survey_position_claim"] = False
            created += 1
    return created


def main() -> None:
    root = bpy.data.collections.get(ROOT_COLLECTION)
    if root is None:
        raise RuntimeError(f"Missing collection: {ROOT_COLLECTION}")
    visual = find_visual(root)
    removed = remove_previous()

    granite = granite_material()
    paving_count = author_paving(visual, granite)
    fountain_count = author_fountain(visual)
    tree_object_count = author_linden_ring(visual)

    root["hamburg_hansaplatz_quality_version"] = 10
    root["hamburg_hansaplatz_landmark_plaza"] = True
    root["hamburg_hansaplatz_photo_origin_runtime"] = "0,0"
    root["hamburg_hansaplatz_photo_origin_wgs84"] = "53.554451,10.012056"
    root["hamburg_hansabrunnen_runtime_position"] = f"{FOUNTAIN_RUNTIME[0]:.3f},0,{FOUNTAIN_RUNTIME[2]:.3f}"
    root["hamburg_hansabrunnen_height_m"] = FOUNTAIN_HEIGHT_M
    root["hamburg_hansabrunnen_geometry_role"] = "source-grounded reconstruction proxy; not scanned sculpture geometry"
    root["hamburg_hansabrunnen_source"] = HAMBURG_PLACE_SOURCE
    root["hamburg_central_paving_source"] = HAMBURG_DESIGN_SOURCE
    root["hamburg_central_paving_material"] = "Granitkleinpflaster visual proxy"
    root["hamburg_linden_ring_source"] = HAMBURG_DESIGN_SOURCE
    root["hamburg_linden_ring_tree_count"] = TREE_COUNT
    root["hamburg_linden_ring_position_role"] = "visual reconstruction around documented circular linden enclosure; not surveyed tree coordinates"
    root["hamburg_v10_paving_object_count"] = paving_count
    root["hamburg_v10_fountain_object_count"] = fountain_count
    root["hamburg_v10_tree_object_count"] = tree_object_count
    root["raw_panorama_wall_projection"] = False

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hansaplatz v10 landmark plaza authored: "
        f"removed={removed} paving={paving_count} fountain={fountain_count} "
        f"tree_objects={tree_object_count} tree_count={TREE_COUNT} "
        f"fountain_runtime={FOUNTAIN_RUNTIME} height={FOUNTAIN_HEIGHT_M}m"
    )


if __name__ == "__main__":
    main()
