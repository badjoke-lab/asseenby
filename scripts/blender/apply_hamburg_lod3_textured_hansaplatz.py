"""Apply official textured Hamburg LoD3 OBJ/MTL geometry to the C0 Blender source.

The input bundle must preserve CityGML ParameterizedTexture UVs. This importer is
purpose-built so the official Hamburg polygon texture mapping survives into GLB;
it does not use the Poly Haven panorama as a building-wall texture.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import sys

import bmesh
import bpy


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--obj", required=True)
    parser.add_argument("--source-url", required=True)
    return parser.parse_args(argv)


def runtime_to_blender(point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = point
    return (x, -z, y)


def find_visual(root: bpy.types.Collection) -> bpy.types.Collection:
    visual = next((child for child in root.children if child.name == "VISUAL_LOD0"), None)
    if visual is None:
        raise RuntimeError("C0 is missing VISUAL_LOD0")
    return visual


def remove_previous_macro_geometry() -> int:
    prefixes = (
        "hansaplatz_north_retail",
        "hansaplatz_east_retail",
        "hansaplatz_south_retail",
        "hansaplatz_west_retail",
        "hansaplatz_grips_theatre",
        "hansaplatz_north_perimeter",
        "hansaplatz_northwest_perimeter",
        "lod2_",
        "lod3_",
    )
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith(prefixes)]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def parse_mtl(path: Path) -> dict[str, dict[str, str]]:
    materials: dict[str, dict[str, str]] = {}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        key = parts[0]
        value = parts[1] if len(parts) > 1 else ""
        if key == "newmtl":
            current = value
            materials[current] = {}
        elif current is not None:
            materials[current][key] = value
    return materials


def fallback_material(name: str, kd: str | None = None) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    rgb = (0.32, 0.31, 0.29)
    if kd:
        try:
            values = [float(value) for value in kd.split()[:3]]
            if len(values) == 3:
                rgb = tuple(values)
        except ValueError:
            pass
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.72
    return material


def official_texture_material(name: str, image_path: Path) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    if not image_path.is_file():
        raise RuntimeError(f"Official Hamburg texture image missing: {image_path}")
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    texture = nodes.new("ShaderNodeTexImage")
    texture.name = f"{name}_official_image"
    texture.label = "Hamburg LGV LoD3 official oblique-aerial texture"
    texture.image = bpy.data.images.load(str(image_path.resolve()), check_existing=True)
    texture.image.colorspace_settings.name = "sRGB"
    texture.interpolation = "Linear"
    links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.72
    material["source_provider"] = "Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV)"
    material["source_dataset"] = "3D-Gebäudemodell LoD3.0-HH Hamburg, Area1"
    material["source_license"] = "dl-de-by-2.0"
    material["texture_basis"] = "official privacy-compliant 20cm oblique-aerial texture"
    return material


def load_obj(path: Path):
    vertices: list[tuple[float, float, float]] = []
    uvs: list[tuple[float, float]] = []
    objects: dict[str, list[tuple[list[int], list[int] | None, str]]] = defaultdict(list)
    current_object = "lod3_unknown_wall"
    current_material = "fallback_wall"
    mtllib: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] == "mtllib" and len(parts) >= 2:
            mtllib = " ".join(parts[1:])
        elif parts[0] == "v" and len(parts) >= 4:
            vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
        elif parts[0] == "vt" and len(parts) >= 3:
            uvs.append((float(parts[1]), float(parts[2])))
        elif parts[0] == "o" and len(parts) >= 2:
            current_object = parts[1]
        elif parts[0] == "usemtl" and len(parts) >= 2:
            current_material = " ".join(parts[1:])
        elif parts[0] == "f" and len(parts) >= 4:
            vis: list[int] = []
            tis: list[int] = []
            has_uv = True
            for token in parts[1:]:
                fields = token.split("/")
                vi = int(fields[0])
                vis.append(vi - 1 if vi > 0 else len(vertices) + vi)
                if len(fields) >= 2 and fields[1]:
                    ti = int(fields[1])
                    tis.append(ti - 1 if ti > 0 else len(uvs) + ti)
                else:
                    has_uv = False
            objects[current_object].append((vis, tis if has_uv and len(tis) == len(vis) else None, current_material))
    if not mtllib:
        raise RuntimeError(f"Textured Hamburg OBJ is missing mtllib: {path}")
    return vertices, uvs, objects, path.parent / mtllib


def triangulate_with_uv(mesh: bpy.types.Mesh) -> None:
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        if bm.faces:
            bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(mesh)
        mesh.validate(verbose=False)
        mesh.update(calc_edges=True)
    finally:
        bm.free()


def build_materials(mtl_path: Path) -> dict[str, bpy.types.Material]:
    definitions = parse_mtl(mtl_path)
    result: dict[str, bpy.types.Material] = {}
    for name, values in definitions.items():
        image = values.get("map_Kd")
        if image:
            result[name] = official_texture_material(name, mtl_path.parent / image)
        else:
            result[name] = fallback_material(name, values.get("Kd"))
    return result


def create_objects(obj_path: Path, visual: bpy.types.Collection) -> tuple[int, int, int]:
    global_vertices, global_uvs, objects, mtl_path = load_obj(obj_path)
    materials = build_materials(mtl_path)
    if not global_vertices or not objects:
        raise RuntimeError(f"Textured Hamburg LoD3 OBJ has no usable geometry: {obj_path}")

    created = 0
    textured_polygons = 0
    fallback_polygons = 0
    for name, records in objects.items():
        used_vertices = sorted({index for face, _, _ in records for index in face})
        remap = {old: new for new, old in enumerate(used_vertices)}
        runtime_vertices = [global_vertices[index] for index in used_vertices]
        local_vertices = [runtime_to_blender(point) for point in runtime_vertices]
        local_faces = [[remap[index] for index in face] for face, _, _ in records]
        mesh = bpy.data.meshes.new(f"{name}_mesh")
        mesh.from_pydata(local_vertices, [], local_faces)
        mesh.validate(verbose=False)
        mesh.update(calc_edges=True)

        object_materials: list[str] = []
        for _, _, material_name in records:
            if material_name not in object_materials:
                object_materials.append(material_name)
        for material_name in object_materials:
            material = materials.get(material_name)
            if material is None:
                material = fallback_material(material_name)
                materials[material_name] = material
            mesh.materials.append(material)

        uv_layer = mesh.uv_layers.new(name="UVMap") if any(record[1] for record in records) else None
        for polygon_index, polygon in enumerate(mesh.polygons):
            _, uv_indices, material_name = records[polygon_index]
            polygon.material_index = object_materials.index(material_name)
            if material_name.startswith("official_tex_"):
                textured_polygons += 1
            else:
                fallback_polygons += 1
            if uv_layer is not None and uv_indices is not None:
                if len(polygon.loop_indices) != len(uv_indices):
                    raise RuntimeError(f"UV loop mismatch before triangulation: {name} polygon {polygon_index}")
                for loop_index, uv_index in zip(polygon.loop_indices, uv_indices):
                    uv_layer.data[loop_index].uv = global_uvs[uv_index]

        triangulate_with_uv(mesh)
        obj = bpy.data.objects.new(name, mesh)
        visual.objects.link(obj)
        obj["source_provider"] = "Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV)"
        obj["source_dataset"] = "3D-Gebäudemodell LoD3.0-HH Hamburg textured, Area1"
        obj["source_license"] = "dl-de-by-2.0"
        obj["quality_role"] = "official-textured-macro-shell"
        created += 1

    return created, textured_polygons, fallback_polygons


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {args.collection}")
    visual = find_visual(root)
    removed = remove_previous_macro_geometry()
    created, textured_polygons, fallback_polygons = create_objects(Path(args.obj), visual)
    if textured_polygons <= 0:
        raise RuntimeError("Official Hamburg textured LoD3 import produced zero textured polygons")

    root["official_geometry_level"] = "LoD3.0-HH"
    root["official_lod3_textured_source"] = args.source_url
    root["official_lod3_provider"] = "Freie und Hansestadt Hamburg, LGV"
    root["official_lod3_license"] = "dl-de-by-2.0"
    root["official_lod3_reference_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
    root["official_lod3_reference_gps"] = "53.554451,10.012056"
    root["official_lod3_created_objects"] = created
    root["official_lod3_textured_polygons"] = textured_polygons
    root["official_lod3_fallback_polygons"] = fallback_polygons
    root["macro_geometry_basis"] = "Hamburg official LoD3.0-HH"
    root["facade_texture_basis"] = "Hamburg official 20cm privacy-compliant oblique-aerial textures"
    root["close_facade_detail_basis"] = "Blender-authored overlay required for approach-distance windows/doors/storefront depth"
    root["raw_panorama_wall_projection"] = False

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg textured LoD3 applied: "
        f"removed={removed}, objects={created}, textured polygons={textured_polygons}, fallback polygons={fallback_polygons}"
    )


if __name__ == "__main__":
    main()
