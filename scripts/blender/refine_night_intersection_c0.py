"""Refine Night Intersection C0 after the authored-prop augmentation pass.

This pass fixes visible asset grounding/placement problems found in the rendered
QR2 review and adds authored Blender facade/storefront/street detail without
returning to Three.js primitive world authoring.

Run after normalize_c0_runtime_frame.py and augment_night_intersection_c0.py.
The file is already in the normalized Blender world, so new runtime positions use
(x, y, z) -> Blender (x, -z, y).
"""

from __future__ import annotations

import argparse
import math
import sys

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    return parser.parse_args(argv)


def runtime_to_blender(position: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = position
    return (x, -z, y)


def descendants(collection: bpy.types.Collection) -> list[bpy.types.Collection]:
    result: list[bpy.types.Collection] = []

    def walk(node: bpy.types.Collection) -> None:
        result.append(node)
        for child in node.children:
            walk(child)

    walk(collection)
    return result


def ensure_visual(root: bpy.types.Collection) -> bpy.types.Collection:
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


def material(
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
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
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
    return mat


def add_box(
    collection: bpy.types.Collection,
    name: str,
    position: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.0,
    rotation_y: float = 0.0,
) -> bpy.types.Object:
    x, y, z = position
    dx, dy, dz = dimensions
    bpy.ops.mesh.primitive_cube_add(size=1, location=runtime_to_blender(position))
    obj = bpy.context.object
    obj.name = name
    # Runtime XYZ dimensions -> normalized Blender X,-Z,Y dimensions.
    obj.dimensions = (dx, dz, dy)
    obj.rotation_euler.z = -rotation_y
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    relink(obj, collection)
    obj.data.materials.append(mat)
    if bevel > 0:
        modifier = obj.modifiers.new("qr2_edge_softening", "BEVEL")
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
    mat: bpy.types.Material,
    vertices: int = 24,
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
    obj.data.materials.append(mat)
    return obj


def move_authored_wrapper(name: str, runtime_x: float, runtime_z: float) -> None:
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Missing authored wrapper: {name}")
    # Imported Poly Haven wrappers are direct normalized-world objects. Preserve
    # the Z ground anchor computed by the augmentation pass and only change X/Y.
    obj.location.x = runtime_x
    obj.location.y = -runtime_z


def remove_residual_placeholder_trees() -> int:
    removed = 0
    for obj in list(bpy.data.objects):
        if obj.name.startswith(("c0_tree_nw_", "c0_tree_se_")):
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1
    return removed


def fix_authored_prop_placement() -> None:
    # The prior rendered pass placed trees/seating inside or directly against the
    # primary building footprints. Move them onto the sidewalk strip between the
    # building faces (~|x|=13.75) and the N/S road edge (~|x|=8.75).
    move_authored_wrapper("c0_authored_jacaranda_tree_nw", -11.55, -46.2)
    move_authored_wrapper("c0_authored_jacaranda_tree_se", 11.55, -9.8)
    move_authored_wrapper("c0_authored_modular_street_seating_sw", -11.65, -10.7)
    move_authored_wrapper("c0_authored_modular_street_seating_ne", 11.65, -45.7)


def front_face_z(cz: float, depth: float, front: str) -> float:
    if front == "south":
        return cz + depth / 2 + 0.07
    return cz - depth / 2 - 0.07


def add_front_architecture(
    visual: bpy.types.Collection,
    prefix: str,
    cx: float,
    cz: float,
    width: float,
    depth: float,
    height: float,
    floors: int,
    front: str,
    stone: bpy.types.Material,
    dark_metal: bpy.types.Material,
    window_dark: bpy.types.Material,
    window_warm: bpy.types.Material,
    window_cool: bpy.types.Material,
    sign_warm: bpy.types.Material,
) -> int:
    created = 0
    face_z = front_face_z(cz, depth, front)
    outward = 1.0 if front == "south" else -1.0

    # Projecting vertical bays and belt courses break the single-box facade read.
    for index, px in enumerate((cx - width * 0.38, cx - width * 0.13, cx + width * 0.13, cx + width * 0.38)):
        add_box(
            visual,
            f"{prefix}_qr2_pilaster_{index}",
            (px, height * 0.52, face_z + outward * 0.16),
            (0.32, height - 1.5, 0.30),
            stone,
            bevel=0.035,
        )
        created += 1

    for index, y in enumerate((4.55, 7.8, 11.0, 14.2, 17.1)):
        if y > height - 0.75:
            continue
        add_box(
            visual,
            f"{prefix}_qr2_belt_{index}",
            (cx, y, face_z + outward * 0.14),
            (width + 0.18, 0.16, 0.26),
            stone,
            bevel=0.025,
        )
        created += 1

    # Window backplanes introduce real recess contrast and occupied/unoccupied
    # variation behind the existing framed glazing instead of one repeated blue grid.
    floor_height = (height - 4.7) / max(1, floors - 1)
    window_index = 0
    inward = -outward
    for floor in range(1, floors):
        y = 4.9 + (floor - 1) * floor_height + floor_height * 0.42
        if y > height - 1.0:
            continue
        for idx in range(4):
            px = cx - width * 0.33 + idx * width * 0.22
            selector = (floor * 5 + idx * 3 + (1 if cx > 0 else 0)) % 7
            if selector in (0, 4):
                mat = window_warm
            elif selector == 2:
                mat = window_cool
            else:
                mat = window_dark
            add_box(
                visual,
                f"{prefix}_qr2_window_back_{window_index:02d}",
                (px, y, face_z + inward * 0.16),
                (1.34, 1.43, 0.05),
                mat,
                bevel=0.015,
            )
            window_index += 1
            created += 1

    # Storefront construction: recessed portal shadow, plinth, jambs, door pull,
    # canopy supports, and a projecting blade sign.
    portal_z = face_z + inward * 0.21
    add_box(visual, f"{prefix}_qr2_store_shadow", (cx, 1.75, portal_z), (width * 0.72, 3.15, 0.08), window_dark, bevel=0.02)
    add_box(visual, f"{prefix}_qr2_store_plinth", (cx, 0.24, face_z + outward * 0.12), (width * 0.80, 0.24, 0.32), stone, bevel=0.04)
    for side, px in (("l", cx - width * 0.39), ("r", cx + width * 0.39)):
        add_box(visual, f"{prefix}_qr2_store_jamb_{side}", (px, 1.9, face_z + outward * 0.13), (0.23, 3.55, 0.28), dark_metal, bevel=0.025)
    handle_x = cx + width * 0.36 + (-0.17 if cx > 0 else 0.17)
    add_box(visual, f"{prefix}_qr2_door_pull", (handle_x, 1.55, face_z + outward * 0.18), (0.045, 0.58, 0.055), dark_metal, bevel=0.012)
    for support_x in (cx - width * 0.30, cx + width * 0.30):
        add_box(visual, f"{prefix}_qr2_canopy_support_{support_x:.1f}", (support_x, 3.28, face_z + outward * 0.55), (0.055, 0.48, 0.055), dark_metal)
    blade_x = cx + (width * 0.43 if cx < 0 else -width * 0.43)
    add_box(visual, f"{prefix}_qr2_blade_arm", (blade_x, 4.55, face_z + outward * 0.48), (0.06, 0.06, 0.72), dark_metal)
    add_box(visual, f"{prefix}_qr2_blade_sign", (blade_x, 4.45, face_z + outward * 0.84), (0.72, 0.92, 0.12), sign_warm, bevel=0.07)
    created += 11
    return created


def add_side_architecture(
    visual: bpy.types.Collection,
    prefix: str,
    cx: float,
    cz: float,
    width: float,
    depth: float,
    height: float,
    stone: bpy.types.Material,
    metal: bpy.types.Material,
    dark: bpy.types.Material,
) -> int:
    created = 0
    side_x = cx + (width / 2 + 0.07) * (1 if cx < 0 else -1)
    outward = 1.0 if cx < 0 else -1.0
    # Downspouts, utility conduit and shallow side-facade bays supply scale cues
    # in the turned/moved views that previously exposed a huge flat brick wall.
    for idx, z in enumerate((cz - depth * 0.34, cz + depth * 0.34)):
        add_cylinder(visual, f"{prefix}_qr2_downpipe_{idx}", (side_x + outward * 0.13, height * 0.42, z), 0.055, height * 0.78, metal, vertices=16)
        created += 1
    for idx, y in enumerate((3.7, 7.0, 10.3)):
        if y > height - 2.0:
            continue
        add_box(visual, f"{prefix}_qr2_side_belt_{idx}", (side_x + outward * 0.12, y, cz), (0.22, 0.14, depth * 0.82), stone, bevel=0.02)
        created += 1

    # Compact fire-escape/platform detail on the two east-side buildings.
    if cx > 0:
        for level, y in enumerate((6.2, 9.8)):
            if y > height - 1.8:
                continue
            platform_x = side_x + outward * 0.62
            add_box(visual, f"{prefix}_qr2_escape_platform_{level}", (platform_x, y, cz + 1.2), (1.25, 0.10, 3.0), metal, bevel=0.025)
            for rail_z in (cz - 0.15, cz + 2.55):
                add_cylinder(visual, f"{prefix}_qr2_escape_rail_{level}_{rail_z:.1f}", (platform_x + outward * 0.45, y + 0.55, rail_z), 0.035, 1.05, metal, vertices=12)
            add_box(visual, f"{prefix}_qr2_escape_shadow_{level}", (side_x + outward * 0.09, y + 0.55, cz + 1.2), (0.06, 1.25, 2.5), dark)
            created += 4
    return created


def add_street_microdetail(
    visual: bpy.types.Collection,
    metal: bpy.types.Material,
    dark: bpy.types.Material,
    patch: bpy.types.Material,
    paint: bpy.types.Material,
) -> int:
    created = 0
    # Road covers and repair patches are low-salience authored Blender detail.
    for idx, (x, z) in enumerate(((2.4, -22.0), (-3.1, -33.5), (4.8, -46.0))):
        add_cylinder(visual, f"c0_qr2_manhole_{idx}", (x, 0.035, z), 0.48, 0.045, metal, vertices=32)
        created += 1
    for idx, (x, z, sx, sz) in enumerate(((-2.5, -8.5, 2.6, 3.8), (3.8, -42.0, 2.1, 4.4), (-18.0, -28.0, 4.0, 2.0))):
        add_box(visual, f"c0_qr2_asphalt_patch_{idx}", (x, 0.018, z), (sx, 0.022, sz), patch, bevel=0.04, rotation_y=0.06 * (idx - 1))
        created += 1

    # Storm drains and service covers sit at the curb/sidewalk edge rather than
    # floating in the carriageway.
    for idx, (x, z) in enumerate(((-8.55, -12.5), (-8.55, -45.0), (8.55, -10.8), (8.55, -43.0))):
        add_box(visual, f"c0_qr2_storm_drain_{idx}", (x, 0.06, z), (0.62, 0.055, 1.25), dark, bevel=0.025)
        for slot in range(4):
            add_box(visual, f"c0_qr2_storm_drain_{idx}_slot_{slot}", (x, 0.095, z - 0.42 + slot * 0.28), (0.48, 0.018, 0.065), metal, bevel=0.008)
        created += 5
    for idx, (x, z) in enumerate(((-12.0, -22.0), (12.0, -34.0), (-17.0, -13.0), (17.0, -42.5))):
        add_box(visual, f"c0_qr2_sidewalk_cover_{idx}", (x, 0.235, z), (0.72, 0.035, 0.72), metal, bevel=0.025)
        created += 1

    # A restrained stop-line pair adds road hierarchy without visual clutter.
    add_box(visual, "c0_qr2_stop_line_s", (0, 0.034, -15.8), (7.4, 0.025, 0.20), paint)
    add_box(visual, "c0_qr2_stop_line_n", (0, 0.034, -40.2), (7.4, 0.025, 0.20), paint)
    created += 2
    return created


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Collection not found: {args.collection}")
    if bpy.data.objects.get("c0_runtime_yup_frame") is None:
        raise RuntimeError("C0 must be normalized before QR2 refinement")
    visual = ensure_visual(root)

    removed = remove_residual_placeholder_trees()
    fix_authored_prop_placement()

    stone = material("c0_qr2_arch_stone", (0.29, 0.27, 0.23, 1), 0.62)
    metal = material("c0_qr2_arch_metal", (0.055, 0.06, 0.065, 1), 0.30, metallic=0.76)
    window_dark = material("c0_qr2_window_dark", (0.010, 0.014, 0.018, 1), 0.22)
    window_warm = material("c0_qr2_window_warm", (0.30, 0.13, 0.035, 1), 0.34, emission=(1.0, 0.34, 0.07, 1), emission_strength=1.6)
    window_cool = material("c0_qr2_window_cool", (0.025, 0.10, 0.16, 1), 0.30, emission=(0.08, 0.32, 0.65, 1), emission_strength=0.75)
    sign_warm = material("c0_qr2_blade_sign_mat", (0.23, 0.055, 0.018, 1), 0.28, emission=(1.0, 0.18, 0.035, 1), emission_strength=2.4)
    road_dark = material("c0_qr2_road_detail", (0.025, 0.028, 0.030, 1), 0.74, metallic=0.16)
    road_patch = material("c0_qr2_road_patch", (0.055, 0.058, 0.058, 1), 0.92)
    road_paint = bpy.data.materials.get("c0_mat_road_paint") or material("c0_qr2_road_paint", (0.78, 0.76, 0.68, 1), 0.56)

    buildings = [
        ("c0_building_nw", -22.0, -49.0, 16.5, 17.0, 15.5, 4, "south"),
        ("c0_building_ne", 22.0, -49.0, 16.5, 17.0, 19.0, 5, "south"),
        ("c0_building_sw", -22.0, -7.0, 16.5, 16.0, 14.0, 4, "north"),
        ("c0_building_se", 22.0, -7.0, 16.5, 16.0, 17.0, 5, "north"),
    ]

    architecture = 0
    for prefix, cx, cz, width, depth, height, floors, front in buildings:
        architecture += add_front_architecture(
            visual, prefix, cx, cz, width, depth, height, floors, front,
            stone, metal, window_dark, window_warm, window_cool, sign_warm,
        )
        architecture += add_side_architecture(
            visual, prefix, cx, cz, width, depth, height, stone, metal, window_dark,
        )

    street_detail = add_street_microdetail(visual, metal, road_dark, road_patch, road_paint)
    root["qr2_architecture_detail_pass"] = "facade articulation + storefront construction + occupied-window variation + street microdetail"
    root["qr2_architecture_detail_objects"] = architecture
    root["qr2_street_detail_objects"] = street_detail
    root["qr2_prop_grounding_fix"] = "trees and seating moved out of primary building footprints"

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        f"QR2 refinement: removed {removed} residual tree placeholders; "
        f"authored {architecture} architecture objects and {street_detail} street-detail objects"
    )


if __name__ == "__main__":
    main()
