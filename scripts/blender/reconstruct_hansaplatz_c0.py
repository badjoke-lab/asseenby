"""Rebuild the C0 macro-layout from the real Hansaplatz photographic reference.

This pass runs after the generic authored-prop/refinement passes. It deliberately
removes the invented four-brick-block intersection architecture and replaces the
primary-visible macro geometry with a Hansaplatz-inspired modernist plaza:
low white-tile retail pavilions around an atrium/plaza, continuous flat canopies
on slender steel columns, a taller theatre volume, glazed storefronts, a subway
entrance/sign, and open paved space.

Reference basis:
- Poly Haven Hansaplatz 360 HDRI by Greg Zaal, CC0-1.0 (runtime/reference plate)
- Hansaviertel architectural record: the northern Hansaplatz shopping centre is
  a mostly single-storey ensemble around an atrium, linked by continuous roofs
  on slender steel supports; small white ceramic tiles are a defining finish.

The script uses runtime XYZ values and maps them into the normalized Blender
frame with (x, y, z) -> (x, -z, y).
"""

from __future__ import annotations

import argparse
import math
import sys

import bpy


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    return parser.parse_args(argv)


def runtime_to_blender(position: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = position
    return (x, -z, y)


def find_visual(root: bpy.types.Collection) -> bpy.types.Collection:
    visual = next((child for child in root.children if child.name == "VISUAL_LOD0"), None)
    if visual is None:
        raise RuntimeError("C0 is missing VISUAL_LOD0")
    return visual


def relink(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    if target not in obj.users_collection:
        target.objects.link(obj)
    for current in list(obj.users_collection):
        if current != target:
            current.objects.unlink(obj)


def mat(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        emission_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission_input is not None:
            emission_input.default_value = emission
        strength_input = bsdf.inputs.get("Emission Strength")
        if strength_input is not None:
            strength_input.default_value = emission_strength
    return material


def add_box(
    collection: bpy.types.Collection,
    name: str,
    position: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    bevel: float = 0.0,
) -> bpy.types.Object:
    dx, dy, dz = dimensions
    bpy.ops.mesh.primitive_cube_add(size=1, location=runtime_to_blender(position))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (dx, dz, dy)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    relink(obj, collection)
    obj.data.materials.append(material)
    if bevel > 0:
        modifier = obj.modifiers.new("hansaplatz_edge_softening", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        modifier.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def add_cylinder(
    collection: bpy.types.Collection,
    name: str,
    position: tuple[float, float, float],
    radius: float,
    height: float,
    material: bpy.types.Material,
    vertices: int = 20,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=height,
        location=runtime_to_blender(position),
    )
    obj = bpy.context.object
    obj.name = name
    relink(obj, collection)
    obj.data.materials.append(material)
    return obj


def remove_invented_architecture() -> int:
    prefixes = (
        "c0_building_",
        "c0_store_nw_",
        "c0_store_ne_",
        "c0_store_sw_",
        "c0_store_se_",
        "c0_road_",
        "c0_crosswalk_",
        "c0_lane_",
        "c0_qr2_asphalt_patch_",
        "c0_qr2_stop_line_",
    )
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith(prefixes)]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def add_tile_field(
    visual: bpy.types.Collection,
    paving: bpy.types.Material,
    joint: bpy.types.Material,
) -> int:
    created = 0
    tile = 3.0
    for ix in range(-8, 9):
        for iz in range(-8, 9):
            x = ix * tile
            z = -28 + iz * tile
            # Keep the very outer ring as service/road margin.
            if abs(x) > 25.0 or z < -53.0 or z > -3.0:
                continue
            add_box(
                visual,
                f"hansaplatz_paver_{ix:+03d}_{iz:+03d}",
                (x, 0.015, z),
                (2.94, 0.05, 2.94),
                paving,
                bevel=0.025,
            )
            created += 1
    # Thin darker bands break the large ground plane and echo modular paving joints.
    for idx, x in enumerate((-12.0, 0.0, 12.0)):
        add_box(visual, f"hansaplatz_joint_ns_{idx}", (x, 0.045, -28), (0.11, 0.018, 49.0), joint)
        created += 1
    for idx, z in enumerate((-43.0, -28.0, -13.0)):
        add_box(visual, f"hansaplatz_joint_ew_{idx}", (0, 0.046, z), (49.0, 0.018, 0.11), joint)
        created += 1
    return created


def add_storefront_strip(
    visual: bpy.types.Collection,
    prefix: str,
    center: tuple[float, float, float],
    width: float,
    outward_z: float,
    glass: bpy.types.Material,
    frame: bpy.types.Material,
    warm: bpy.types.Material,
    cool: bpy.types.Material,
) -> int:
    cx, cy, cz = center
    created = 0
    bays = max(4, int(width // 3.0))
    bay_w = width / bays
    for i in range(bays):
        x = cx - width / 2 + bay_w * (i + 0.5)
        back = warm if i % 4 in (0, 3) else cool if i % 4 == 1 else frame
        add_box(visual, f"{prefix}_interior_{i:02d}", (x, 1.55, cz - outward_z * 0.34), (bay_w - 0.12, 2.7, 0.10), back, bevel=0.015)
        add_box(visual, f"{prefix}_glass_{i:02d}", (x, 1.55, cz), (bay_w - 0.13, 2.75, 0.055), glass, bevel=0.012)
        add_box(visual, f"{prefix}_mullion_{i:02d}", (cx - width / 2 + bay_w * i, 1.55, cz + outward_z * 0.035), (0.07, 2.85, 0.09), frame, bevel=0.015)
        created += 3
    add_box(visual, f"{prefix}_mullion_end", (cx + width / 2, 1.55, cz + outward_z * 0.035), (0.07, 2.85, 0.09), frame, bevel=0.015)
    return created + 1


def add_pavilion(
    visual: bpy.types.Collection,
    prefix: str,
    center: tuple[float, float],
    size: tuple[float, float],
    height: float,
    storefront_side: str,
    tile_material: bpy.types.Material,
    roof_material: bpy.types.Material,
    glass: bpy.types.Material,
    frame: bpy.types.Material,
    warm: bpy.types.Material,
    cool: bpy.types.Material,
) -> int:
    cx, cz = center
    width, depth = size
    created = 0
    add_box(visual, f"{prefix}_body", (cx, height / 2 + 0.10, cz), (width, height, depth), tile_material, bevel=0.08)
    add_box(visual, f"{prefix}_roof", (cx, height + 0.20, cz), (width + 0.42, 0.28, depth + 0.42), roof_material, bevel=0.05)
    add_box(visual, f"{prefix}_base", (cx, 0.22, cz), (width + 0.08, 0.32, depth + 0.08), frame, bevel=0.035)
    created += 3

    # Ceramic-tile seam rhythm is modeled as shallow strips so it survives real-time rendering.
    for i in range(1, int(width // 1.6)):
        x = cx - width / 2 + i * 1.6
        add_box(visual, f"{prefix}_tile_seam_v_{i:02d}", (x, height * 0.55, cz + depth / 2 + 0.011), (0.018, height * 0.72, 0.018), roof_material)
        created += 1

    if storefront_side == "south":
        face_z = cz + depth / 2 + 0.045
        created += add_storefront_strip(visual, f"{prefix}_storefront", (cx, 0, face_z), width * 0.82, 1.0, glass, frame, warm, cool)
    elif storefront_side == "north":
        face_z = cz - depth / 2 - 0.045
        created += add_storefront_strip(visual, f"{prefix}_storefront", (cx, 0, face_z), width * 0.82, -1.0, glass, frame, warm, cool)
    return created


def add_canopy(
    visual: bpy.types.Collection,
    prefix: str,
    center: tuple[float, float],
    size: tuple[float, float],
    roof: bpy.types.Material,
    metal: bpy.types.Material,
) -> int:
    cx, cz = center
    width, depth = size
    add_box(visual, f"{prefix}_roof", (cx, 3.18, cz), (width, 0.16, depth), roof, bevel=0.035)
    created = 1
    x_count = max(2, int(width // 3.2))
    z_count = max(2, int(depth // 3.2))
    # Put columns along the canopy perimeter rather than filling the walking path.
    for i in range(x_count + 1):
        x = cx - width / 2 + width * i / x_count
        for z in (cz - depth / 2 + 0.18, cz + depth / 2 - 0.18):
            add_cylinder(visual, f"{prefix}_column_x_{i}_{z:+.1f}", (x, 1.58, z), 0.055, 3.05, metal, 14)
            created += 1
    for i in range(1, z_count):
        z = cz - depth / 2 + depth * i / z_count
        for x in (cx - width / 2 + 0.18, cx + width / 2 - 0.18):
            add_cylinder(visual, f"{prefix}_column_z_{i}_{x:+.1f}", (x, 1.58, z), 0.055, 3.05, metal, 14)
            created += 1
    return created


def add_subway_entrance(
    visual: bpy.types.Collection,
    tile_material: bpy.types.Material,
    frame: bpy.types.Material,
    glass: bpy.types.Material,
    blue: bpy.types.Material,
) -> int:
    created = 0
    # Low pavilion and stair void approximation; enough depth to stop the entry reading as a sign stuck on a plane.
    add_box(visual, "hansaplatz_ubahn_entry_roof", (8.0, 3.05, -22.0), (6.8, 0.20, 5.8), tile_material, bevel=0.05)
    add_box(visual, "hansaplatz_ubahn_entry_back", (8.0, 1.55, -24.75), (6.8, 2.8, 0.16), frame, bevel=0.03)
    for i in range(3):
        x = 6.0 + i * 2.0
        add_box(visual, f"hansaplatz_ubahn_glass_{i}", (x, 1.55, -19.12), (1.7, 2.65, 0.07), glass, bevel=0.02)
        created += 1
    add_box(visual, "hansaplatz_ubahn_stair_dark", (8.0, 0.30, -21.4), (4.8, 0.15, 4.6), frame, bevel=0.03)
    # Blue U sign block; text can be replaced by a proper mesh/decal in a later fidelity pass.
    add_box(visual, "hansaplatz_ubahn_sign", (11.9, 3.65, -19.0), (0.78, 0.78, 0.22), blue, bevel=0.08)
    add_cylinder(visual, "hansaplatz_ubahn_sign_pole", (11.9, 1.75, -19.0), 0.055, 3.5, frame, 14)
    return created + 6


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {args.collection}")
    visual = find_visual(root)

    removed = remove_invented_architecture()

    ceramic = mat("hansaplatz_small_white_ceramic", (0.78, 0.79, 0.76, 1), 0.46)
    ceramic_shadow = mat("hansaplatz_ceramic_joint", (0.22, 0.23, 0.22, 1), 0.72)
    roof = mat("hansaplatz_roof_dark", (0.085, 0.09, 0.095, 1), 0.50, 0.18)
    frame = mat("hansaplatz_steel_frame", (0.045, 0.055, 0.06, 1), 0.30, 0.78)
    glass = mat("hansaplatz_glass", (0.035, 0.075, 0.085, 1), 0.12, 0.08)
    paving = mat("hansaplatz_paving", (0.34, 0.34, 0.32, 1), 0.78)
    paving_joint = mat("hansaplatz_paving_joint", (0.10, 0.11, 0.11, 1), 0.88)
    warm = mat("hansaplatz_store_warm", (0.42, 0.18, 0.055, 1), 0.32, emission=(1.0, 0.28, 0.05, 1), emission_strength=3.0)
    cool = mat("hansaplatz_store_cool", (0.045, 0.12, 0.16, 1), 0.28, emission=(0.06, 0.24, 0.42, 1), emission_strength=1.4)
    subway_blue = mat("hansaplatz_ubahn_blue", (0.02, 0.15, 0.55, 1), 0.24, emission=(0.04, 0.25, 1.0, 1), emission_strength=2.8)

    created = add_tile_field(visual, paving, paving_joint)

    # Mostly one-storey retail ensemble around the plaza/atrium, with a taller theatre volume.
    created += add_pavilion(visual, "hansaplatz_north_retail", (0.0, -47.0), (28.0, 8.0), 4.1, "south", ceramic, roof, glass, frame, warm, cool)
    created += add_pavilion(visual, "hansaplatz_east_retail", (19.0, -31.0), (10.0, 21.0), 4.0, "north", ceramic, roof, glass, frame, warm, cool)
    created += add_pavilion(visual, "hansaplatz_south_retail", (-3.0, -9.0), (24.0, 7.0), 3.8, "north", ceramic, roof, glass, frame, warm, cool)
    created += add_pavilion(visual, "hansaplatz_west_retail", (-20.0, -28.0), (9.0, 18.0), 3.9, "south", ceramic, roof, glass, frame, warm, cool)
    created += add_pavilion(visual, "hansaplatz_grips_theatre", (-18.5, -47.0), (11.0, 10.0), 8.3, "south", ceramic, roof, glass, frame, warm, cool)

    # Continuous roof links on slender steel supports are a defining Hansaplatz cue.
    created += add_canopy(visual, "hansaplatz_canopy_north", (0.0, -40.8), (30.0, 3.0), roof, frame)
    created += add_canopy(visual, "hansaplatz_canopy_east", (13.6, -28.0), (3.0, 21.0), roof, frame)
    created += add_canopy(visual, "hansaplatz_canopy_south", (-3.0, -14.0), (25.0, 3.0), roof, frame)

    # Central atrium/kiosk element and transit entrance give the plaza a real destination rather than four empty road corners.
    add_box(visual, "hansaplatz_kiosk_body", (-4.0, 1.45, -28.5), (5.0, 2.8, 4.0), ceramic, bevel=0.08)
    add_box(visual, "hansaplatz_kiosk_glass", (-4.0, 1.45, -26.42), (4.25, 2.2, 0.07), glass, bevel=0.025)
    add_box(visual, "hansaplatz_kiosk_glow", (-4.0, 1.5, -26.55), (3.9, 2.0, 0.05), warm, bevel=0.02)
    created += 3
    created += add_subway_entrance(visual, ceramic, frame, glass, subway_blue)

    # A few simple edge rails / planters keep near-ground scale readable while higher-fidelity props remain separate CC0 assets.
    for idx, (x, z, sx, sz) in enumerate(((-10.5, -24.0, 5.0, 1.2), (3.0, -34.5, 6.0, 1.2), (12.0, -12.5, 4.0, 1.1))):
        add_box(visual, f"hansaplatz_planter_{idx}", (x, 0.35, z), (sx, 0.55, sz), ceramic_shadow, bevel=0.12)
        created += 1

    root["reference_location"] = "Hansaplatz, Berlin, Germany"
    root["reference_photo_asset"] = "Poly Haven hansaplatz / Greg Zaal / CC0-1.0"
    root["reference_driven_reconstruction"] = True
    root["reference_macro_layout_pass"] = "hansaplatz-modernist-plaza-v1"
    root["reference_removed_invented_objects"] = removed
    root["reference_created_objects"] = created

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"Hansaplatz macro reconstruction: removed={removed}, created={created}")


if __name__ == "__main__":
    main()
