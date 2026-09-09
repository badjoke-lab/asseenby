"""Replace provisional Hansaplatz paving with one continuous PBR plaza surface.

This pass is deliberately self-contained: the canonical .blend may no longer carry
materials created by the old guessed Hansaplatz reconstruction, so the material is
rebuilt from checked-in Poly Haven CC0 maps when needed.  The surface is still a
temporary flat plaza proxy; its purpose is to avoid the raised-slab artifact while
correct Hamburg ground geometry is authored next.
"""

from __future__ import annotations

from pathlib import Path

import bpy


MATERIAL_NAME = "hansaplatz_concrete_pavement_pbr"
MATERIAL_DIR = Path("assets-src/blender/night-intersection/materials/hansaplatz")
CAPTURE_WIDTH_M = 1.8


def runtime_to_blender(point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = point
    return (x, -z, y)


def find_visual(root: bpy.types.Collection) -> bpy.types.Collection:
    visual = next((child for child in root.children if child.name == "VISUAL_LOD0"), None)
    if visual is None:
        raise RuntimeError("C0 is missing VISUAL_LOD0")
    return visual


def ensure_pavement_material() -> bpy.types.Material:
    existing = bpy.data.materials.get(MATERIAL_NAME)
    if existing is not None:
        return existing

    paths = {
        "diff": MATERIAL_DIR / "concrete_pavement_diff_1k.jpg",
        "nor": MATERIAL_DIR / "concrete_pavement_nor_gl_1k.jpg",
        "rough": MATERIAL_DIR / "concrete_pavement_rough_1k.jpg",
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing checked-in Hansaplatz pavement maps: {missing}")

    material = bpy.data.materials.new(MATERIAL_NAME)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        raise RuntimeError("Principled BSDF unavailable for pavement material")

    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.name = "hansaplatz_paving_uv"

    diffuse = nodes.new("ShaderNodeTexImage")
    diffuse.name = "concrete_pavement_diffuse"
    diffuse.image = bpy.data.images.load(str(paths["diff"].resolve()), check_existing=True)
    diffuse.image.colorspace_settings.name = "sRGB"
    diffuse.extension = "REPEAT"
    links.new(texcoord.outputs["UV"], diffuse.inputs["Vector"])
    links.new(diffuse.outputs["Color"], bsdf.inputs["Base Color"])

    rough = nodes.new("ShaderNodeTexImage")
    rough.name = "concrete_pavement_roughness"
    rough.image = bpy.data.images.load(str(paths["rough"].resolve()), check_existing=True)
    rough.image.colorspace_settings.name = "Non-Color"
    rough.extension = "REPEAT"
    links.new(texcoord.outputs["UV"], rough.inputs["Vector"])
    links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])

    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.name = "concrete_pavement_normal"
    normal_tex.image = bpy.data.images.load(str(paths["nor"].resolve()), check_existing=True)
    normal_tex.image.colorspace_settings.name = "Non-Color"
    normal_tex.extension = "REPEAT"
    links.new(texcoord.outputs["UV"], normal_tex.inputs["Vector"])
    normal = nodes.new("ShaderNodeNormalMap")
    normal.name = "concrete_pavement_normal_strength"
    normal.inputs["Strength"].default_value = 0.82
    links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])

    material["source_provider"] = "Poly Haven"
    material["source_asset_id"] = "concrete_pavement"
    material["source_license"] = "CC0-1.0"
    material["capture_width_m"] = CAPTURE_WIDTH_M
    return material


def main() -> None:
    root = bpy.data.collections.get("C0")
    if root is None:
        raise RuntimeError("Missing C0 collection")
    visual = find_visual(root)

    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith("hansaplatz_paving_slab_")]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)

    previous = bpy.data.objects.get("hansaplatz_plaza_ground_reference_plane")
    if previous is not None:
        bpy.data.objects.remove(previous, do_unlink=True)

    material = ensure_pavement_material()

    runtime_vertices = [
        (-25.0, 0.0, -53.0),
        (25.0, 0.0, -53.0),
        (25.0, 0.0, -3.0),
        (-25.0, 0.0, -3.0),
    ]
    mesh = bpy.data.meshes.new("hansaplatz_plaza_ground_reference_plane_mesh")
    mesh.from_pydata([runtime_to_blender(point) for point in runtime_vertices], [], [(0, 1, 2, 3)])
    mesh.validate(verbose=False)
    mesh.update(calc_edges=True)

    # Tile the 1.8 m physical scan at approximately real scale across the 50 m plaza.
    repeats = 50.0 / CAPTURE_WIDTH_M
    uv_layer = mesh.uv_layers.new(name="UVMap")
    uv_coords = ((0.0, 0.0), (repeats, 0.0), (repeats, repeats), (0.0, repeats))
    polygon = mesh.polygons[0]
    for loop_index, uv in zip(polygon.loop_indices, uv_coords):
        uv_layer.data[loop_index].uv = uv

    obj = bpy.data.objects.new("hansaplatz_plaza_ground_reference_plane", mesh)
    visual.objects.link(obj)
    obj.data.materials.append(material)
    obj["reference_basis"] = "Hamburg Hansaplatz temporary continuous plaza proxy"
    obj["material_source"] = "Poly Haven concrete_pavement"
    obj["material_license"] = "CC0-1.0"
    obj["material_capture_width_m"] = CAPTURE_WIDTH_M
    obj["replaces_provisional_paving_slabs"] = len(doomed)

    root["hansaplatz_paving_geometry"] = "single temporary continuous coplanar PBR surface"
    root["hansaplatz_removed_paving_slabs"] = len(doomed)
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"Hansaplatz paving field replaced: removed slabs={len(doomed)}, continuous PBR surface=1")


if __name__ == "__main__":
    main()
