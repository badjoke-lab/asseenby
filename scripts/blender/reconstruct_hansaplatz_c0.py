"""Rebuild C0 around the real Hansaplatz photographic reference.

This pass runs after the older generic authored-prop/refinement passes. It removes
the invented four-brick-block intersection architecture and replaces the
primary-visible macro geometry with a Hansaplatz-driven modernist plaza:
low tiled retail pavilions around open public space, continuous flat canopies on
slender steel columns, a taller theatre volume, glazed storefronts, a U-Bahn
entrance/sign and scanned PBR paving/facade materials.

Reference basis:
- Poly Haven Hansaplatz 360 HDRI by Greg Zaal, CC0-1.0;
- reproducible rectilinear plates generated from that panorama;
- Hansaviertel architectural records describing the low shopping-centre ensemble,
  continuous roofs/slender supports and small ceramic-tile finish.

The file is already in the normalized Blender frame. Runtime XYZ maps to Blender
(x, -z, y).
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import bpy


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--material-dir", required=True)
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


def flat_material(
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


def scanned_box_material(
    name: str,
    material_dir: Path,
    asset_id: str,
    capture_width_m: float,
    *,
    saturation: float = 1.0,
    value: float = 1.0,
    normal_strength: float = 0.8,
) -> bpy.types.Material:
    """Create a real-scale triplanar PBR material from checked-in Poly Haven maps."""
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing

    paths = {
        kind: material_dir / f"{asset_id}_{kind}_1k.jpg"
        for kind in ("diff", "nor_gl", "rough")
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing Hansaplatz PBR maps: {missing}")

    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.name = f"{asset_id}_object_coordinates"
    mapping = nodes.new("ShaderNodeMapping")
    mapping.name = f"{asset_id}_meter_scale"
    repeat = 1.0 / max(capture_width_m, 0.01)
    mapping.inputs["Scale"].default_value = (repeat, repeat, repeat)
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])

    diffuse = nodes.new("ShaderNodeTexImage")
    diffuse.name = f"{asset_id}_diffuse"
    diffuse.image = bpy.data.images.load(str(paths["diff"].resolve()), check_existing=True)
    diffuse.image.colorspace_settings.name = "sRGB"
    diffuse.extension = "REPEAT"
    diffuse.projection = "BOX"
    diffuse.projection_blend = 0.12
    links.new(mapping.outputs["Vector"], diffuse.inputs["Vector"])

    hue = nodes.new("ShaderNodeHueSaturation")
    hue.name = f"{asset_id}_reference_color_adjustment"
    hue.inputs["Saturation"].default_value = saturation
    hue.inputs["Value"].default_value = value
    links.new(diffuse.outputs["Color"], hue.inputs["Color"])
    links.new(hue.outputs["Color"], bsdf.inputs["Base Color"])

    normal_texture = nodes.new("ShaderNodeTexImage")
    normal_texture.name = f"{asset_id}_normal"
    normal_texture.image = bpy.data.images.load(str(paths["nor_gl"].resolve()), check_existing=True)
    normal_texture.image.colorspace_settings.name = "Non-Color"
    normal_texture.extension = "REPEAT"
    normal_texture.projection = "BOX"
    normal_texture.projection_blend = 0.12
    links.new(mapping.outputs["Vector"], normal_texture.inputs["Vector"])
    normal = nodes.new("ShaderNodeNormalMap")
    normal.name = f"{asset_id}_normal_strength"
    normal.inputs["Strength"].default_value = normal_strength
    links.new(normal_texture.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])

    roughness = nodes.new("ShaderNodeTexImage")
    roughness.name = f"{asset_id}_roughness"
    roughness.image = bpy.data.images.load(str(paths["rough"].resolve()), check_existing=True)
    roughness.image.colorspace_settings.name = "Non-Color"
    roughness.extension = "REPEAT"
    roughness.projection = "BOX"
    roughness.projection_blend = 0.12
    links.new(mapping.outputs["Vector"], roughness.inputs["Vector"])
    links.new(roughness.outputs["Color"], bsdf.inputs["Roughness"])

    material["source_provider"] = "Poly Haven"
    material["source_asset_id"] = asset_id
    material["license"] = "CC0-1.0"
    material["capture_width_m"] = capture_width_m
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
        "hansaplatz_",
    )
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith(prefixes)]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def add_paving_field(visual: bpy.types.Collection, paving: bpy.types.Material) -> int:
    # Larger slabs reduce draw/object overhead; the scanned PBR surface supplies
    # the small-scale joints, wear and aggregate that the earlier flat blocks lacked.
    created = 0
    slab = 8.0
    for ix in range(-3, 4):
        for iz in range(-3, 4):
            x = ix * slab
            z = -28 + iz * slab
            if abs(x) > 25.0 or z < -53.0 or z > -3.0:
                continue
            add_box(
                visual,
                f"hansaplatz_paving_slab_{ix:+02d}_{iz:+02d}",
                (x, 0.012, z),
                (7.96, 0.045, 7.96),
                paving,
                bevel=0.018,
            )
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
    cx, _, cz = center
    created = 0
    bays = max(4, int(width // 2.6))
    bay_w = width / bays
    for i in range(bays):
        x = cx - width / 2 + bay_w * (i + 0.5)
        back = warm if i % 5 in (0, 4) else cool if i % 5 == 2 else frame
        add_box(visual, f"{prefix}_interior_{i:02d}", (x, 1.48, cz - outward_z * 0.48), (bay_w - 0.12, 2.55, 0.10), back, bevel=0.015)
        add_box(visual, f"{prefix}_glass_{i:02d}", (x, 1.52, cz), (bay_w - 0.11, 2.72, 0.05), glass, bevel=0.012)
        add_box(visual, f"{prefix}_mullion_{i:02d}", (cx - width / 2 + bay_w * i, 1.52, cz + outward_z * 0.035), (0.065, 2.84, 0.09), frame, bevel=0.012)
        created += 3
    add_box(visual, f"{prefix}_mullion_end", (cx + width / 2, 1.52, cz + outward_z * 0.035), (0.065, 2.84, 0.09), frame, bevel=0.012)
    # Continuous transom and plinth are visible cues in the photographic shopfront rhythm.
    add_box(visual, f"{prefix}_transom", (cx, 2.93, cz + outward_z * 0.04), (width + 0.08, 0.07, 0.09), frame, bevel=0.012)
    add_box(visual, f"{prefix}_plinth", (cx, 0.14, cz + outward_z * 0.05), (width + 0.08, 0.18, 0.11), frame, bevel=0.018)
    return created + 3


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
    add_box(visual, f"{prefix}_body", (cx, height / 2 + 0.10, cz), (width, height, depth), tile_material, bevel=0.055)
    add_box(visual, f"{prefix}_roof", (cx, height + 0.20, cz), (width + 0.42, 0.24, depth + 0.42), roof_material, bevel=0.045)
    add_box(visual, f"{prefix}_base", (cx, 0.19, cz), (width + 0.08, 0.28, depth + 0.08), frame, bevel=0.028)
    created += 3

    if storefront_side == "south":
        face_z = cz + depth / 2 + 0.045
        created += add_storefront_strip(visual, f"{prefix}_storefront", (cx, 0, face_z), width * 0.84, 1.0, glass, frame, warm, cool)
    elif storefront_side == "north":
        face_z = cz - depth / 2 - 0.045
        created += add_storefront_strip(visual, f"{prefix}_storefront", (cx, 0, face_z), width * 0.84, -1.0, glass, frame, warm, cool)
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
    add_box(visual, f"{prefix}_roof", (cx, 3.16, cz), (width, 0.13, depth), roof, bevel=0.025)
    created = 1
    x_count = max(2, int(width // 3.4))
    z_count = max(2, int(depth // 3.4))
    for i in range(x_count + 1):
        x = cx - width / 2 + width * i / x_count
        for z in (cz - depth / 2 + 0.16, cz + depth / 2 - 0.16):
            add_cylinder(visual, f"{prefix}_column_x_{i}_{z:+.1f}", (x, 1.56, z), 0.045, 3.03, metal, 16)
            created += 1
    for i in range(1, z_count):
        z = cz - depth / 2 + depth * i / z_count
        for x in (cx - width / 2 + 0.16, cx + width / 2 - 0.16):
            add_cylinder(visual, f"{prefix}_column_z_{i}_{x:+.1f}", (x, 1.56, z), 0.045, 3.03, metal, 16)
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
    add_box(visual, "hansaplatz_ubahn_entry_roof", (8.0, 3.02, -22.0), (6.8, 0.16, 5.8), tile_material, bevel=0.045)
    add_box(visual, "hansaplatz_ubahn_entry_back", (8.0, 1.50, -24.76), (6.8, 2.72, 0.14), frame, bevel=0.025)
    for i in range(3):
        x = 6.0 + i * 2.0
        add_box(visual, f"hansaplatz_ubahn_glass_{i}", (x, 1.50, -19.10), (1.72, 2.58, 0.055), glass, bevel=0.018)
        created += 1
    # Descending stair treads create actual parallax/depth instead of one dark slab.
    for step in range(8):
        add_box(
            visual,
            f"hansaplatz_ubahn_step_{step:02d}",
            (8.0, 0.08 - step * 0.12, -20.05 - step * 0.48),
            (4.7, 0.12, 0.48),
            frame,
            bevel=0.01,
        )
        created += 1
    add_box(visual, "hansaplatz_ubahn_sign", (11.9, 3.62, -19.0), (0.74, 0.74, 0.18), blue, bevel=0.07)
    add_cylinder(visual, "hansaplatz_ubahn_sign_pole", (11.9, 1.74, -19.0), 0.045, 3.45, frame, 16)
    return created + 5


def main() -> None:
    args = parse_args()
    material_dir = Path(args.material_dir)
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {args.collection}")
    visual = find_visual(root)

    removed = remove_invented_architecture()

    # Rounded Square Tiled Wall is a close geometric match for the small ceramic
    # facade module. Desaturate/brighten its photographed beige surface toward
    # Hansaplatz's white cladding while preserving scanned grout/wear/normal data.
    ceramic = scanned_box_material(
        "hansaplatz_small_white_ceramic_pbr",
        material_dir,
        "rounded_square_tiled_wall",
        2.0,
        saturation=0.22,
        value=1.34,
        normal_strength=0.72,
    )
    paving = scanned_box_material(
        "hansaplatz_concrete_pavement_pbr",
        material_dir,
        "concrete_pavement",
        1.8,
        saturation=0.72,
        value=0.82,
        normal_strength=0.82,
    )
    ceramic_shadow = flat_material("hansaplatz_ceramic_joint", (0.18, 0.19, 0.18, 1), 0.72)
    roof = flat_material("hansaplatz_roof_dark", (0.065, 0.072, 0.078, 1), 0.48, 0.28)
    frame = flat_material("hansaplatz_steel_frame", (0.032, 0.042, 0.048, 1), 0.26, 0.82)
    glass = flat_material("hansaplatz_glass", (0.025, 0.060, 0.072, 1), 0.10, 0.08)
    warm = flat_material("hansaplatz_store_warm", (0.40, 0.15, 0.038, 1), 0.30, emission=(1.0, 0.24, 0.035, 1), emission_strength=3.5)
    cool = flat_material("hansaplatz_store_cool", (0.035, 0.095, 0.13, 1), 0.26, emission=(0.05, 0.20, 0.36, 1), emission_strength=1.6)
    subway_blue = flat_material("hansaplatz_ubahn_blue", (0.018, 0.11, 0.52, 1), 0.22, emission=(0.035, 0.20, 1.0, 1), emission_strength=3.0)

    created = add_paving_field(visual, paving)

    # Hansaplatz is not a four-corner brick canyon. The authored foreground is
    # rebuilt as a low pavilion/plaza ensemble with the taller theatre volume.
    created += add_pavilion(visual, "hansaplatz_north_retail", (0.0, -47.0), (28.0, 8.0), 4.1, "south", ceramic, roof, glass, frame, warm, cool)
    created += add_pavilion(visual, "hansaplatz_east_retail", (19.0, -31.0), (10.0, 21.0), 4.0, "north", ceramic, roof, glass, frame, warm, cool)
    created += add_pavilion(visual, "hansaplatz_south_retail", (-3.0, -9.0), (24.0, 7.0), 3.8, "north", ceramic, roof, glass, frame, warm, cool)
    created += add_pavilion(visual, "hansaplatz_west_retail", (-20.0, -28.0), (9.0, 18.0), 3.9, "south", ceramic, roof, glass, frame, warm, cool)
    created += add_pavilion(visual, "hansaplatz_grips_theatre", (-18.5, -47.0), (11.0, 10.0), 8.3, "south", ceramic, roof, glass, frame, warm, cool)

    created += add_canopy(visual, "hansaplatz_canopy_north", (0.0, -40.8), (30.0, 3.0), roof, frame)
    created += add_canopy(visual, "hansaplatz_canopy_east", (13.6, -28.0), (3.0, 21.0), roof, frame)
    created += add_canopy(visual, "hansaplatz_canopy_south", (-3.0, -14.0), (25.0, 3.0), roof, frame)

    add_box(visual, "hansaplatz_kiosk_body", (-4.0, 1.42, -28.5), (5.0, 2.75, 4.0), ceramic, bevel=0.055)
    add_box(visual, "hansaplatz_kiosk_glass", (-4.0, 1.43, -26.46), (4.30, 2.20, 0.055), glass, bevel=0.018)
    add_box(visual, "hansaplatz_kiosk_glow", (-4.0, 1.45, -26.56), (3.92, 2.00, 0.04), warm, bevel=0.015)
    created += 3
    created += add_subway_entrance(visual, ceramic, frame, glass, subway_blue)

    for idx, (x, z, sx, sz) in enumerate(((-10.5, -24.0, 5.0, 1.2), (3.0, -34.5, 6.0, 1.2), (12.0, -12.5, 4.0, 1.1))):
        add_box(visual, f"hansaplatz_planter_{idx}", (x, 0.35, z), (sx, 0.55, sz), ceramic_shadow, bevel=0.10)
        created += 1

    root["reference_location"] = "Hansaplatz, Berlin, Germany"
    root["reference_photo_asset"] = "Poly Haven hansaplatz / Greg Zaal / CC0-1.0"
    root["reference_driven_reconstruction"] = True
    root["reference_macro_layout_pass"] = "hansaplatz-modernist-plaza-pbr-v2"
    root["reference_removed_invented_objects"] = removed
    root["reference_created_objects"] = created
    root["reference_pbr_facade"] = "Poly Haven rounded_square_tiled_wall / CC0-1.0"
    root["reference_pbr_paving"] = "Poly Haven concrete_pavement / CC0-1.0"

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"Hansaplatz PBR reconstruction: removed={removed}, created={created}")


if __name__ == "__main__":
    main()
