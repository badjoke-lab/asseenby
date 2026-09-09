"""Finalize Hansaplatz C0 after official Berlin LoD2 import.

This pass removes residual guessed Hansaplatz foreground geometry left by earlier
migration passes and replaces the plaza floor with one continuous, reference-matched
CC0 scanned paving surface. It deliberately keeps Berlin LoD2 objects (lod2_*) as
the macro-geometry source of truth.
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


def remove_residual_guessed_foreground() -> int:
    prefixes = (
        "hansaplatz_",
        "c0_authored_jacaranda_tree_",
        "c0_tree_nw_",
        "c0_tree_se_",
    )
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith(prefixes)]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def scanned_paving_material(material_dir: Path) -> bpy.types.Material:
    asset_id = "rectangular_paving"
    paths = {
        kind: material_dir / f"{asset_id}_{kind}_1k.jpg"
        for kind in ("diff", "nor_gl", "rough")
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing reference paving maps: {missing}")

    material = bpy.data.materials.get("hansaplatz_reference_rectangular_paving")
    if material is None:
        material = bpy.data.materials.new("hansaplatz_reference_rectangular_paving")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])

    diffuse = nodes.new("ShaderNodeTexImage")
    diffuse.image = bpy.data.images.load(str(paths["diff"].resolve()), check_existing=True)
    diffuse.image.colorspace_settings.name = "sRGB"
    diffuse.extension = "REPEAT"
    diffuse.projection = "BOX"
    diffuse.projection_blend = 0.08
    links.new(mapping.outputs["Vector"], diffuse.inputs["Vector"])

    hue = nodes.new("ShaderNodeHueSaturation")
    hue.inputs["Saturation"].default_value = 0.72
    hue.inputs["Value"].default_value = 0.92
    links.new(diffuse.outputs["Color"], hue.inputs["Color"])
    links.new(hue.outputs["Color"], bsdf.inputs["Base Color"])

    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = bpy.data.images.load(str(paths["nor_gl"].resolve()), check_existing=True)
    normal_tex.image.colorspace_settings.name = "Non-Color"
    normal_tex.extension = "REPEAT"
    normal_tex.projection = "BOX"
    normal_tex.projection_blend = 0.08
    links.new(mapping.outputs["Vector"], normal_tex.inputs["Vector"])
    normal = nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 1.15
    links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])

    rough = nodes.new("ShaderNodeTexImage")
    rough.image = bpy.data.images.load(str(paths["rough"].resolve()), check_existing=True)
    rough.image.colorspace_settings.name = "Non-Color"
    rough.extension = "REPEAT"
    rough.projection = "BOX"
    rough.projection_blend = 0.08
    links.new(mapping.outputs["Vector"], rough.inputs["Vector"])
    links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    material["source_provider"] = "Poly Haven"
    material["source_asset_id"] = asset_id
    material["source_license"] = "CC0-1.0"
    material["reference_role"] = "Hansaplatz plaza paving"
    return material


def add_reference_ground(visual: bpy.types.Collection, material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=runtime_to_blender((0.0, -0.015, -28.0)))
    obj = bpy.context.object
    obj.name = "reference_hansaplatz_plaza_paving"
    obj.dimensions = (60.0, 60.0, 0.035)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    relink(obj, visual)
    obj.data.materials.append(material)
    obj["reference_basis"] = "Hansaplatz photographic ground plane"
    obj["source_asset"] = "Poly Haven rectangular_paving"
    obj["source_license"] = "CC0-1.0"
    return obj


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {args.collection}")
    visual = find_visual(root)

    removed = remove_residual_guessed_foreground()
    material = scanned_paving_material(Path(args.material_dir))
    add_reference_ground(visual, material)

    root["reference_foreground_policy"] = "official-LoD2-plus-reference-ground"
    root["reference_foreground_removed_guessed_objects"] = removed
    root["reference_ground_asset"] = "Poly Haven rectangular_paving / CC0-1.0"
    root["reference_ground_surface"] = "continuous 60m plaza plane"

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"Hansaplatz reference foreground finalized: removed={removed}, ground=rectangular_paving")


if __name__ == "__main__":
    main()
