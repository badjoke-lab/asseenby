"""Build the Night Intersection C0 authored visible core in Blender.

This is a deterministic authoring script, not a Three.js scene generator. It creates
Blender geometry/materials/collections, saves the canonical .blend source, and then
the existing export_night_intersection.py script exports the C0 collection to GLB.

Usage:
  blender --background --factory-startup \
    --python scripts/blender/build_night_intersection_c0.py -- \
    --material-dir assets-src/blender/night-intersection/materials \
    --blend-out assets-src/blender/night-intersection/c0/night-intersection-c0.blend
"""

from __future__ import annotations

import argparse
from pathlib import Path
import math
import sys

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--material-dir", required=True)
    parser.add_argument("--blend-out", required=True)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def make_collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    if parent is None:
        bpy.context.scene.collection.children.link(collection)
    else:
        parent.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def principled_material(
    name: str,
    base_color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        emission_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission_input:
            emission_input.default_value = emission
        strength_input = bsdf.inputs.get("Emission Strength")
        if strength_input:
            strength_input.default_value = emission_strength
    return mat


def image_pbr_material(
    name: str,
    material_dir: Path,
    slug: str,
    roughness_fallback: float,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = roughness_fallback

    diff_path = material_dir / f"{slug}_diff_1k.jpg"
    normal_path = material_dir / f"{slug}_nor_gl_1k.jpg"
    rough_path = material_dir / f"{slug}_rough_1k.jpg"

    if not diff_path.exists():
        raise RuntimeError(f"Missing PBR diffuse texture: {diff_path}")
    if not normal_path.exists():
        raise RuntimeError(f"Missing PBR normal texture: {normal_path}")
    if not rough_path.exists():
        raise RuntimeError(f"Missing PBR roughness texture: {rough_path}")

    diff = nodes.new("ShaderNodeTexImage")
    diff.name = f"{slug}_diff"
    diff.image = bpy.data.images.load(str(diff_path.resolve()), check_existing=True)
    diff.image.colorspace_settings.name = "sRGB"
    links.new(diff.outputs["Color"], bsdf.inputs["Base Color"])

    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.name = f"{slug}_normal"
    normal_tex.image = bpy.data.images.load(str(normal_path.resolve()), check_existing=True)
    normal_tex.image.colorspace_settings.name = "Non-Color"
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = 0.72
    links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

    rough = nodes.new("ShaderNodeTexImage")
    rough.name = f"{slug}_roughness"
    rough.image = bpy.data.images.load(str(rough_path.resolve()), check_existing=True)
    rough.image.colorspace_settings.name = "Non-Color"
    links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
    return mat


def add_box(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    bevel: float = 0.0,
    bevel_segments: int = 2,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, collection)
    if material is not None:
        obj.data.materials.append(material)
    if bevel > 0:
        modifier = obj.modifiers.new(name="edge_softening", type="BEVEL")
        modifier.width = bevel
        modifier.segments = bevel_segments
        modifier.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def add_cylinder(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: bpy.types.Material,
    vertices: int = 24,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, collection)
    obj.data.materials.append(material)
    return obj


def add_uv_sphere(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, collection)
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def add_empty(collection: bpy.types.Collection, name: str, location: tuple[float, float, float]) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.location = location
    collection.objects.link(obj)
    return obj


def add_road_tiles(visual: bpy.types.Collection, asphalt: bpy.types.Material) -> None:
    # 64 m central chunk centered at z=-28. Tiles keep the 1K asphalt texture
    # from stretching over an entire district-scale plane.
    for index, z in enumerate([0, -8, -16, -24, -32, -40, -48, -56]):
        add_box(
            visual,
            f"c0_road_ns_tile_{index:02d}_lod0",
            (0, -0.10, z),
            (17.5, 0.18, 8.02),
            asphalt,
            bevel=0.03,
        )
    for index, x in enumerate([-28, -20, -12, -4, 4, 12, 20, 28]):
        add_box(
            visual,
            f"c0_road_ew_tile_{index:02d}_lod0",
            (x, -0.085, -28),
            (8.02, 0.19, 17.5),
            asphalt,
            bevel=0.03,
        )


def add_sidewalk_corner(
    visual: bpy.types.Collection,
    prefix: str,
    center: tuple[float, float],
    concrete: bpy.types.Material,
    curb: bpy.types.Material,
) -> None:
    cx, cz = center
    # 4x4 slab field gives joints and close-range relief instead of a single box.
    slab = 5.6
    for ix in range(4):
        for iz in range(4):
            x = cx + (ix - 1.5) * slab
            z = cz + (iz - 1.5) * slab
            add_box(
                visual,
                f"{prefix}_sidewalk_slab_{ix}_{iz}_lod0",
                (x, 0.105, z),
                (slab - 0.055, 0.21, slab - 0.055),
                concrete,
                bevel=0.035,
            )
    toward_x = 1 if cx < 0 else -1
    toward_z = 1 if cz < -28 else -1
    edge_x = cx + toward_x * 11.25
    edge_z = cz + toward_z * 11.25
    add_box(visual, f"{prefix}_curb_ns_lod0", (edge_x, 0.22, cz), (0.34, 0.34, 22.5), curb, bevel=0.045)
    add_box(visual, f"{prefix}_curb_ew_lod0", (cx, 0.22, edge_z), (22.5, 0.34, 0.34), curb, bevel=0.045)


def add_crosswalks(visual: bpy.types.Collection, paint: bpy.types.Material) -> None:
    for side_name, z in (("south", -18.55), ("north", -37.45)):
        for i in range(8):
            x = -7.1 + i * 2.03
            add_box(visual, f"c0_crosswalk_{side_name}_{i:02d}_lod0", (x, 0.025, z), (1.05, 0.025, 4.7), paint, bevel=0.01)
    for side_name, x in (("west", -9.9), ("east", 9.9)):
        for i in range(8):
            z = -35.1 + i * 2.03
            add_box(visual, f"c0_crosswalk_{side_name}_{i:02d}_lod0", (x, 0.03, z), (4.7, 0.025, 1.05), paint, bevel=0.01)
    for x in (-3.25, 3.25):
        for i, z in enumerate([-52, -42, -12, -2]):
            add_box(visual, f"c0_lane_ns_{int(x*10)}_{i}_lod0", (x, 0.026, z), (0.16, 0.022, 4.2), paint)
    for z in (-24.75, -31.25):
        for i, x in enumerate([-24, -14, 14, 24]):
            add_box(visual, f"c0_lane_ew_{int(abs(z)*10)}_{i}_lod0", (x, 0.03, z), (4.2, 0.022, 0.16), paint)


def add_window(
    visual: bpy.types.Collection,
    prefix: str,
    center: tuple[float, float, float],
    size: tuple[float, float],
    axis: str,
    glass: bpy.types.Material,
    frame: bpy.types.Material,
) -> None:
    x, y, z = center
    width, height = size
    frame_t = 0.08
    depth = 0.10
    if axis == "z":
        add_box(visual, f"{prefix}_glass", (x, y, z), (width, height, depth), glass, bevel=0.015)
        add_box(visual, f"{prefix}_frame_top", (x, y + height / 2 + 0.055, z - 0.018), (width + 0.22, 0.11, 0.14), frame, bevel=0.02)
        add_box(visual, f"{prefix}_frame_bottom", (x, y - height / 2 - 0.055, z - 0.018), (width + 0.22, 0.11, 0.14), frame, bevel=0.02)
        add_box(visual, f"{prefix}_frame_left", (x - width / 2 - 0.055, y, z - 0.018), (0.11, height, 0.14), frame, bevel=0.02)
        add_box(visual, f"{prefix}_frame_right", (x + width / 2 + 0.055, y, z - 0.018), (0.11, height, 0.14), frame, bevel=0.02)
        add_box(visual, f"{prefix}_mullion", (x, y, z - 0.025), (frame_t, height, 0.15), frame, bevel=0.015)
        add_box(visual, f"{prefix}_sill", (x, y - height / 2 - 0.13, z - 0.10), (width + 0.34, 0.12, 0.30), frame, bevel=0.03)
    else:
        add_box(visual, f"{prefix}_glass", (x, y, z), (depth, height, width), glass, bevel=0.015)
        add_box(visual, f"{prefix}_frame_top", (x - 0.018, y + height / 2 + 0.055, z), (0.14, 0.11, width + 0.22), frame, bevel=0.02)
        add_box(visual, f"{prefix}_frame_bottom", (x - 0.018, y - height / 2 - 0.055, z), (0.14, 0.11, width + 0.22), frame, bevel=0.02)
        add_box(visual, f"{prefix}_frame_left", (x - 0.018, y, z - width / 2 - 0.055), (0.14, height, 0.11), frame, bevel=0.02)
        add_box(visual, f"{prefix}_frame_right", (x - 0.018, y, z + width / 2 + 0.055), (0.14, height, 0.11), frame, bevel=0.02)
        add_box(visual, f"{prefix}_mullion", (x - 0.025, y, z), (0.15, height, frame_t), frame, bevel=0.015)
        add_box(visual, f"{prefix}_sill", (x - 0.10, y - height / 2 - 0.13, z), (0.30, 0.12, width + 0.34), frame, bevel=0.03)


def add_storefront(
    visual: bpy.types.Collection,
    prefix: str,
    center: tuple[float, float, float],
    width: float,
    axis: str,
    outward_sign: float,
    glass: bpy.types.Material,
    metal: bpy.types.Material,
    sign: bpy.types.Material,
) -> None:
    x, _, z = center
    y = 1.75
    if axis == "z":
        for i in range(3):
            px = x - width * 0.31 + i * width * 0.31
            add_box(visual, f"{prefix}_glass_{i}", (px, y, z), (width * 0.27, 2.7, 0.11), glass, bevel=0.025)
        for i in range(4):
            px = x - width * 0.46 + i * width * 0.31
            add_box(visual, f"{prefix}_mullion_{i}", (px, y, z - outward_sign * 0.025), (0.10, 2.85, 0.16), metal, bevel=0.02)
        add_box(visual, f"{prefix}_door", (x + width * 0.36, 1.55, z - outward_sign * 0.035), (1.45, 2.45, 0.14), glass, bevel=0.025)
        add_box(visual, f"{prefix}_awning", (x, 3.45, z - outward_sign * 0.62), (width * 0.82, 0.18, 1.15), metal, bevel=0.08)
        add_box(visual, f"{prefix}_sign", (x, 4.12, z - outward_sign * 0.13), (width * 0.72, 0.76, 0.17), sign, bevel=0.08)
    else:
        for i in range(3):
            pz = z - width * 0.31 + i * width * 0.31
            add_box(visual, f"{prefix}_glass_{i}", (x, y, pz), (0.11, 2.7, width * 0.27), glass, bevel=0.025)
        for i in range(4):
            pz = z - width * 0.46 + i * width * 0.31
            add_box(visual, f"{prefix}_mullion_{i}", (x - outward_sign * 0.025, y, pz), (0.16, 2.85, 0.10), metal, bevel=0.02)
        add_box(visual, f"{prefix}_door", (x - outward_sign * 0.035, 1.55, z + width * 0.36), (0.14, 2.45, 1.45), glass, bevel=0.025)
        add_box(visual, f"{prefix}_awning", (x - outward_sign * 0.62, 3.45, z), (1.15, 0.18, width * 0.82), metal, bevel=0.08)
        add_box(visual, f"{prefix}_sign", (x - outward_sign * 0.13, 4.12, z), (0.17, 0.76, width * 0.72), sign, bevel=0.08)


def add_building(
    visual: bpy.types.Collection,
    prefix: str,
    center: tuple[float, float],
    size: tuple[float, float],
    height: float,
    floors: int,
    front: str,
    brick: bpy.types.Material,
    trim: bpy.types.Material,
    glass: bpy.types.Material,
    metal: bpy.types.Material,
    roof: bpy.types.Material,
    sign: bpy.types.Material,
) -> None:
    cx, cz = center
    width, depth = size
    add_box(visual, f"{prefix}_shell_lod0", (cx, height / 2 + 0.30, cz), (width, height, depth), brick, bevel=0.16, bevel_segments=3)
    add_box(visual, f"{prefix}_base_course_lod0", (cx, 0.72, cz), (width + 0.12, 0.75, depth + 0.12), trim, bevel=0.08)
    add_box(visual, f"{prefix}_cornice_lod0", (cx, height - 0.22, cz), (width + 0.45, 0.38, depth + 0.45), trim, bevel=0.08)
    add_box(visual, f"{prefix}_parapet_lod0", (cx, height + 0.25, cz), (width + 0.10, 0.65, depth + 0.10), brick, bevel=0.06)

    # Ground-floor storefront faces the intersection.
    if front == "south":
        face_z = cz + depth / 2 + 0.07
        add_storefront(visual, f"{prefix}_storefront", (cx, 0, face_z), width * 0.76, "z", -1, glass, metal, sign)
    elif front == "north":
        face_z = cz - depth / 2 - 0.07
        add_storefront(visual, f"{prefix}_storefront", (cx, 0, face_z), width * 0.76, "z", 1, glass, metal, sign)
    elif front == "east":
        face_x = cx + width / 2 + 0.07
        add_storefront(visual, f"{prefix}_storefront", (face_x, 0, cz), depth * 0.76, "x", -1, glass, metal, sign)
    else:
        face_x = cx - width / 2 - 0.07
        add_storefront(visual, f"{prefix}_storefront", (face_x, 0, cz), depth * 0.76, "x", 1, glass, metal, sign)

    floor_height = (height - 4.7) / max(1, floors - 1)
    for floor in range(1, floors):
        y = 4.9 + (floor - 1) * floor_height + floor_height * 0.42
        if y > height - 1.0:
            continue
        count = 4
        if front in ("south", "north"):
            face_z = cz + (depth / 2 + 0.065) * (1 if front == "south" else -1)
            for idx in range(count):
                px = cx - width * 0.33 + idx * width * 0.22
                add_window(visual, f"{prefix}_front_f{floor}_w{idx}", (px, y, face_z), (1.55, 1.65), "z", glass, trim)
        else:
            face_x = cx + (width / 2 + 0.065) * (1 if front == "east" else -1)
            for idx in range(count):
                pz = cz - depth * 0.33 + idx * depth * 0.22
                add_window(visual, f"{prefix}_front_f{floor}_w{idx}", (face_x, y, pz), (1.55, 1.65), "x", glass, trim)

    # Intersection-facing side facade receives a second window rhythm.
    side_axis = "x" if cx < 0 else "x"
    side_x = cx + (width / 2 + 0.065) * (1 if cx < 0 else -1)
    for floor in range(1, min(floors, 4)):
        y = 4.9 + (floor - 1) * floor_height + floor_height * 0.42
        for idx in range(3):
            pz = cz - depth * 0.25 + idx * depth * 0.25
            add_window(visual, f"{prefix}_side_f{floor}_w{idx}", (side_x, y, pz), (1.25, 1.45), side_axis, glass, trim)

    # Roof equipment adds skyline detail for later Cat/Bird observers.
    add_box(visual, f"{prefix}_roof_hvac_a_lod0", (cx - 2.3, height + 0.95, cz + 1.6), (2.6, 1.25, 1.8), metal, bevel=0.10)
    add_box(visual, f"{prefix}_roof_hvac_b_lod0", (cx + 2.6, height + 0.72, cz - 1.8), (1.7, 0.85, 1.5), metal, bevel=0.08)
    add_cylinder(visual, f"{prefix}_roof_vent_lod0", (cx + 0.7, height + 1.15, cz + 2.5), 0.28, 1.6, metal, vertices=20)
    add_box(visual, f"{prefix}_roof_access_lod0", (cx, height + 1.0, cz - 3.0), (2.4, 1.65, 2.3), roof, bevel=0.10)


def add_bench(visual: bpy.types.Collection, prefix: str, x: float, z: float, rotation_y: float, wood: bpy.types.Material, metal: bpy.types.Material) -> None:
    root = []
    seat = add_box(visual, f"{prefix}_seat_lod0", (x, 0.58, z), (2.2, 0.16, 0.52), wood, bevel=0.06)
    back = add_box(visual, f"{prefix}_back_lod0", (x, 1.05, z + 0.22), (2.2, 0.68, 0.14), wood, bevel=0.05)
    for obj in (seat, back):
        obj.rotation_euler[1] = rotation_y
    for sx in (-0.78, 0.78):
        leg = add_box(visual, f"{prefix}_leg_{sx}_lod0", (x + sx, 0.30, z), (0.12, 0.55, 0.48), metal, bevel=0.035)
        leg.rotation_euler[1] = rotation_y


def add_tree(visual: bpy.types.Collection, prefix: str, x: float, z: float, trunk: bpy.types.Material, foliage: bpy.types.Material, planter: bpy.types.Material) -> None:
    add_box(visual, f"{prefix}_planter_lod0", (x, 0.38, z), (2.0, 0.68, 2.0), planter, bevel=0.12)
    add_cylinder(visual, f"{prefix}_trunk_lod0", (x, 2.5, z), 0.26, 4.5, trunk, vertices=24)
    for idx, (ox, oy, oz, sx, sy, sz) in enumerate([
        (-0.45, 4.7, 0.10, 1.65, 1.25, 1.45),
        (0.55, 5.0, -0.25, 1.55, 1.35, 1.35),
        (0.0, 5.55, 0.45, 1.45, 1.25, 1.45),
        (0.25, 4.45, 0.75, 1.35, 1.10, 1.25),
    ]):
        add_uv_sphere(visual, f"{prefix}_crown_{idx}_lod0", (x + ox, oy, z + oz), (sx, sy, sz), foliage)


def add_traffic_signal(visual: bpy.types.Collection, prefix: str, x: float, z: float, red: bpy.types.Material, green: bpy.types.Material, amber: bpy.types.Material, metal: bpy.types.Material) -> None:
    add_cylinder(visual, f"{prefix}_pole_lod0", (x, 2.55, z), 0.14, 5.1, metal, vertices=24)
    add_box(visual, f"{prefix}_housing_lod0", (x, 4.75, z), (0.72, 2.0, 0.65), metal, bevel=0.09)
    for idx, (y, mat) in enumerate(((5.25, red), (4.75, amber), (4.25, green))):
        add_cylinder(visual, f"{prefix}_lens_{idx}_lod0", (x, y, z - 0.36), 0.18, 0.10, mat, vertices=24, rotation=(math.pi / 2, 0, 0))


def add_delivery_van(visual: bpy.types.Collection, prefix: str, x: float, z: float, rotation_y: float, paint: bpy.types.Material, glass: bpy.types.Material, tire: bpy.types.Material, metal: bpy.types.Material) -> None:
    body = add_box(visual, f"{prefix}_body_lod0", (x, 1.15, z), (2.05, 1.8, 4.7), paint, bevel=0.28, bevel_segments=4)
    cabin = add_box(visual, f"{prefix}_cabin_lod0", (x, 1.45, z - 1.55), (1.98, 1.55, 1.7), paint, bevel=0.26, bevel_segments=4)
    windshield = add_box(visual, f"{prefix}_windshield_lod0", (x, 1.65, z - 2.43), (1.58, 0.70, 0.08), glass, bevel=0.06)
    for obj in (body, cabin, windshield):
        obj.rotation_euler[1] = rotation_y
    for side in (-1, 1):
        for axle in (-1.45, 1.42):
            wheel = add_cylinder(visual, f"{prefix}_wheel_{side}_{axle}_lod0", (x + side * 1.03, 0.48, z + axle), 0.43, 0.24, tire, vertices=28, rotation=(0, math.pi / 2, 0))
            hub = add_cylinder(visual, f"{prefix}_hub_{side}_{axle}_lod0", (x + side * 1.055, 0.48, z + axle), 0.20, 0.255, metal, vertices=24, rotation=(0, math.pi / 2, 0))
            wheel.rotation_euler[1] += rotation_y
            hub.rotation_euler[1] += rotation_y


def main() -> None:
    args = parse_args()
    material_dir = Path(args.material_dir)
    blend_out = Path(args.blend_out)

    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "EEVEE_NEXT") else scene.render.engine

    c0 = make_collection("C0")
    visual = make_collection("VISUAL_LOD0", c0)
    make_collection("VISUAL_LOD1", c0)
    make_collection("VISUAL_LOD2", c0)
    collision = make_collection("COLLISION", c0)
    nav = make_collection("NAV", c0)
    make_collection("PERCH", c0)
    make_collection("CLIMB", c0)
    make_collection("PORTAL", c0)
    spawn = make_collection("SPAWN", c0)
    lights = make_collection("LIGHT_ANCHOR", c0)

    asphalt = image_pbr_material("c0_mat_asphalt_polyhaven", material_dir, "asphalt_01", 0.88)
    brick = image_pbr_material("c0_mat_brick_polyhaven", material_dir, "brick_wall_001", 0.84)
    concrete = principled_material("c0_mat_concrete", (0.42, 0.43, 0.42, 1), 0.82)
    curb = principled_material("c0_mat_curb", (0.52, 0.53, 0.50, 1), 0.74)
    trim = principled_material("c0_mat_stone_trim", (0.25, 0.27, 0.27, 1), 0.58)
    metal = principled_material("c0_mat_dark_metal", (0.055, 0.065, 0.075, 1), 0.32, metallic=0.72)
    pale_metal = principled_material("c0_mat_pale_metal", (0.45, 0.49, 0.52, 1), 0.36, metallic=0.62)
    road_paint = principled_material("c0_mat_road_paint", (0.80, 0.78, 0.68, 1), 0.55)
    wood = principled_material("c0_mat_bench_wood", (0.22, 0.10, 0.045, 1), 0.66)
    planter = principled_material("c0_mat_planter", (0.18, 0.19, 0.18, 1), 0.72)
    trunk = principled_material("c0_mat_tree_trunk", (0.12, 0.065, 0.035, 1), 0.90)
    foliage = principled_material("c0_mat_foliage", (0.045, 0.14, 0.065, 1), 0.82)
    tire = principled_material("c0_mat_tire", (0.018, 0.018, 0.020, 1), 0.92)
    van_paint = principled_material("c0_mat_van_paint", (0.12, 0.22, 0.30, 1), 0.34, metallic=0.24)
    roof = principled_material("c0_mat_roof", (0.09, 0.10, 0.11, 1), 0.72)
    glass = principled_material("c0_mat_glass", (0.055, 0.12, 0.16, 1), 0.13, metallic=0.05)
    glass.diffuse_color[3] = 0.72
    glass.surface_render_method = "DITHERED" if hasattr(glass, "surface_render_method") else glass.surface_render_method
    sign_warm = principled_material("c0_mat_sign_warm", (0.35, 0.12, 0.03, 1), 0.28, emission=(1.0, 0.22, 0.04, 1), emission_strength=3.0)
    sign_cool = principled_material("c0_mat_sign_cool", (0.03, 0.22, 0.30, 1), 0.28, emission=(0.04, 0.45, 1.0, 1), emission_strength=2.6)
    red = principled_material("c0_mat_signal_red", (0.18, 0.01, 0.008, 1), 0.20, emission=(1.0, 0.015, 0.01, 1), emission_strength=5.0)
    amber = principled_material("c0_mat_signal_amber", (0.20, 0.10, 0.005, 1), 0.20, emission=(1.0, 0.34, 0.01, 1), emission_strength=2.0)
    green = principled_material("c0_mat_signal_green", (0.005, 0.16, 0.06, 1), 0.20, emission=(0.02, 1.0, 0.20, 1), emission_strength=4.0)

    add_road_tiles(visual, asphalt)
    for prefix, center in (
        ("c0_nw", (-20.5, -48.5)),
        ("c0_ne", (20.5, -48.5)),
        ("c0_sw", (-20.5, -7.5)),
        ("c0_se", (20.5, -7.5)),
    ):
        add_sidewalk_corner(visual, prefix, center, concrete, curb)
    add_crosswalks(visual, road_paint)

    add_building(visual, "c0_building_nw", (-22.0, -49.0), (16.5, 17.0), 15.5, 4, "south", brick, trim, glass, metal, roof, sign_warm)
    add_building(visual, "c0_building_ne", (22.0, -49.0), (16.5, 17.0), 19.0, 5, "south", brick, trim, glass, metal, roof, sign_cool)
    add_building(visual, "c0_building_sw", (-22.0, -7.0), (16.5, 16.0), 14.0, 4, "north", brick, trim, glass, metal, roof, sign_warm)
    add_building(visual, "c0_building_se", (22.0, -7.0), (16.5, 16.0), 17.0, 5, "north", brick, trim, glass, metal, roof, sign_cool)

    add_bench(visual, "c0_bench_sw", -14.2, -11.5, 0.0, wood, metal)
    add_bench(visual, "c0_bench_ne", 14.5, -44.0, math.pi, wood, metal)
    add_tree(visual, "c0_tree_nw", -14.8, -51.5, trunk, foliage, planter)
    add_tree(visual, "c0_tree_se", 14.8, -4.5, trunk, foliage, planter)

    for i, (x, z) in enumerate([(-10.7, -14.5), (-10.7, -11.5), (10.7, -41.5), (10.7, -44.5)]):
        add_cylinder(visual, f"c0_bollard_{i:02d}_lod0", (x, 0.62, z), 0.12, 1.18, metal, vertices=20)
    add_box(visual, "c0_utility_cabinet_w_lod0", (-12.2, 0.85, -47.5), (1.15, 1.5, 0.72), pale_metal, bevel=0.08)
    add_box(visual, "c0_trash_bin_e_lod0", (12.4, 0.72, -8.2), (0.78, 1.25, 0.78), metal, bevel=0.10)

    # Bike rack: three U-like frames assembled from cylinders.
    for rack in range(3):
        bx = -15.5 + rack * 0.75
        for side in (-0.32, 0.32):
            add_cylinder(visual, f"c0_bike_rack_{rack}_leg_{side}_lod0", (bx + side, 0.62, -15.3), 0.045, 1.20, pale_metal, vertices=16)
        top = add_cylinder(visual, f"c0_bike_rack_{rack}_top_lod0", (bx, 1.20, -15.3), 0.045, 0.64, pale_metal, vertices=16, rotation=(0, math.pi / 2, 0))
        top.rotation_euler[2] = math.pi / 2

    add_traffic_signal(visual, "c0_signal_sw", -8.9, -18.7, red, green, amber, metal)
    add_traffic_signal(visual, "c0_signal_ne", 8.9, -37.3, red, green, amber, metal)
    add_delivery_van(visual, "c0_delivery_van", 4.7, -50.0, math.pi, van_paint, glass, tire, pale_metal)

    # Simplified collision proxies and NAV are authored separately and hidden from render.
    for name, center, size in (
        ("c0_collision_nw", (-22.0, 7.5, -49.0), (17.2, 15.0, 17.7)),
        ("c0_collision_ne", (22.0, 9.5, -49.0), (17.2, 19.0, 17.7)),
        ("c0_collision_sw", (-22.0, 7.0, -7.0), (17.2, 14.0, 16.7)),
        ("c0_collision_se", (22.0, 8.5, -7.0), (17.2, 17.0, 16.7)),
    ):
        proxy = add_box(collision, name, center, size, trim)
        proxy.hide_render = True
    nav_surface = add_box(nav, "c0_nav_ground", (0, 0.01, -28), (63.5, 0.02, 63.5), concrete)
    nav_surface.hide_render = True

    add_empty(spawn, "c0_spawn_human_reference", (0.0, 1.6, 0.0))
    add_empty(spawn, "c0_spawn_human_offset", (3.2, 1.6, -4.2))
    for idx, location in enumerate([(-12.8, 6.8, -16.5), (12.8, 6.8, -39.5), (-12.8, 6.8, -39.5), (12.8, 6.8, -16.5)]):
        anchor = add_empty(lights, f"c0_light_anchor_street_{idx:02d}", location)
        anchor["light_role"] = "street_practical"
        anchor["temperature_k"] = 3200
        anchor["intensity_hint"] = 24.0

    # Metadata used to prove provenance and authoring intent after export.
    c0["asseenby_chunk"] = "c0"
    c0["authoring_tool"] = "Blender"
    c0["unit_contract"] = "1 Blender unit = 1 meter"
    c0["quality_gate"] = "QR2 visible core candidate; rendered acceptance required"

    blend_out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_out.resolve()))
    print(f"Saved authored C0 Blender source: {blend_out}")


if __name__ == "__main__":
    main()
