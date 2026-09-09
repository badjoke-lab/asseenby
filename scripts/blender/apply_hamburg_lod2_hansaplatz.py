"""Replace C0 macro geometry with the real Hamburg Hansaplatz LoD2 subset.

The Poly Haven Hansaplatz HDRI GPS is 53.554451, 10.012056 in Hamburg-St. Georg.
This pass consumes the local OBJ extracted from Hamburg LGV LoD2-DE 2026 and uses
that official cadastral geometry as the shape source of truth. The checked-in CC0
Poly Haven panorama is projected onto wall surfaces for photographic facade detail.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import math
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
    parser.add_argument("--panorama", required=True)
    parser.add_argument("--panorama-yaw-deg", type=float, default=0.0)
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
    )
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith(prefixes)]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def fallback_material(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def projected_panorama_material(path: Path) -> bpy.types.Material:
    if not path.exists():
        raise RuntimeError(f"Hansaplatz panorama not found: {path}")
    name = "hamburg_hansaplatz_panorama_projected_facade"
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing

    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    texture = nodes.new("ShaderNodeTexImage")
    texture.name = "hamburg_hansaplatz_cc0_panorama_projection"
    texture.label = "Poly Haven Hansaplatz CC0 panorama projection"
    texture.image = bpy.data.images.load(str(path.resolve()), check_existing=True)
    texture.image.colorspace_settings.name = "sRGB"
    texture.extension = "REPEAT"
    texture.interpolation = "Linear"
    links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])

    bsdf.inputs["Roughness"].default_value = 0.62
    metallic = bsdf.inputs.get("Metallic")
    if metallic is not None:
        metallic.default_value = 0.0
    specular = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
    if specular is not None:
        specular.default_value = 0.32
    emission_strength = bsdf.inputs.get("Emission Strength")
    if emission_strength is not None:
        emission_strength.default_value = 0.0

    material["source_provider"] = "Poly Haven"
    material["source_asset"] = "hansaplatz"
    material["source_license"] = "CC0-1.0"
    material["source_gps"] = "53.554451,10.012056"
    material["source_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
    material["projection_origin_runtime_xyz"] = "0,1.6,0"
    material["projection_type"] = "equirectangular-per-loop"
    material["projection_emissive"] = False
    return material


def load_obj(path: Path):
    vertices: list[tuple[float, float, float]] = []
    objects: dict[str, list[list[int]]] = defaultdict(list)
    current = "lod2_unknown_wall"
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] == "v" and len(parts) >= 4:
            vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
        elif parts[0] == "o" and len(parts) >= 2:
            current = parts[1]
        elif parts[0] == "f" and len(parts) >= 4:
            face: list[int] = []
            for token in parts[1:]:
                index = int(token.split("/", 1)[0])
                face.append(index - 1 if index > 0 else len(vertices) + index)
            objects[current].append(face)
    return vertices, objects


def triangulate_mesh(mesh: bpy.types.Mesh) -> None:
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        if bm.faces:
            bmesh.ops.triangulate(
                bm,
                faces=list(bm.faces),
                quad_method="BEAUTY",
                ngon_method="BEAUTY",
            )
        bm.to_mesh(mesh)
        mesh.validate(verbose=False)
        mesh.update(calc_edges=True)
    finally:
        bm.free()


def panorama_uv(
    point: tuple[float, float, float],
    yaw_radians: float,
    origin: tuple[float, float, float] = (0.0, 1.6, 0.0),
) -> tuple[float, float]:
    x = point[0] - origin[0]
    y = point[1] - origin[1]
    z = point[2] - origin[2]
    radius = math.sqrt(x * x + y * y + z * z)
    if radius < 1e-6:
        return (0.5, 0.5)
    angle = math.atan2(z, x) + yaw_radians
    u = (angle / (2.0 * math.pi) + 0.5) % 1.0
    v = 0.5 + math.asin(max(-1.0, min(1.0, y / radius))) / math.pi
    return (u, max(0.0, min(1.0, v)))


def apply_panorama_uv(
    mesh: bpy.types.Mesh,
    runtime_vertices: list[tuple[float, float, float]],
    yaw_radians: float,
) -> None:
    uv_layer = mesh.uv_layers.get("UVMap") or mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        samples: list[tuple[int, float, float]] = []
        for loop_index in polygon.loop_indices:
            vertex_index = mesh.loops[loop_index].vertex_index
            u, v = panorama_uv(runtime_vertices[vertex_index], yaw_radians)
            samples.append((loop_index, u, v))
        if not samples:
            continue
        us = [sample[1] for sample in samples]
        crosses_seam = max(us) - min(us) > 0.5
        for loop_index, u, v in samples:
            if crosses_seam and u < 0.5:
                u += 1.0
            uv_layer.data[loop_index].uv = (u, v)


def create_semantic_objects(
    path: Path,
    visual: bpy.types.Collection,
    panorama: Path,
    panorama_yaw_deg: float,
) -> int:
    vertices, objects = load_obj(path)
    if not vertices or not objects:
        raise RuntimeError(f"Hamburg LoD2 OBJ has no usable geometry: {path}")

    projected_wall = projected_panorama_material(panorama)
    roof = bpy.data.materials.get("hansaplatz_roof_dark") or fallback_material(
        "hamburg_lod2_roof_reference", (0.10, 0.11, 0.12, 1.0), 0.68
    )
    ground = bpy.data.materials.get("hansaplatz_facade_stone") or fallback_material(
        "hamburg_lod2_ground_reference", (0.30, 0.29, 0.27, 1.0), 0.82
    )
    yaw_radians = math.radians(panorama_yaw_deg)

    created = 0
    min_runtime = [float("inf"), float("inf"), float("inf")]
    max_runtime = [float("-inf"), float("-inf"), float("-inf")]
    for name, global_faces in objects.items():
        used = sorted({index for face in global_faces for index in face})
        remap = {old: new for new, old in enumerate(used)}
        runtime_vertices = [vertices[index] for index in used]
        for point in runtime_vertices:
            for axis in range(3):
                min_runtime[axis] = min(min_runtime[axis], point[axis])
                max_runtime[axis] = max(max_runtime[axis], point[axis])
        local_vertices = [runtime_to_blender(point) for point in runtime_vertices]
        local_faces = [[remap[index] for index in face] for face in global_faces]
        mesh = bpy.data.meshes.new(f"{name}_mesh")
        mesh.from_pydata(local_vertices, [], local_faces)
        mesh.validate(verbose=False)
        mesh.update(calc_edges=True)
        triangulate_mesh(mesh)
        if any(len(poly.vertices) != 3 for poly in mesh.polygons):
            raise RuntimeError(f"Hamburg LoD2 mesh remained non-triangular: {name}")

        semantic = "roof" if name.endswith("_roof") else "ground" if name.endswith("_ground") else "wall"
        if semantic == "wall":
            apply_panorama_uv(mesh, runtime_vertices, yaw_radians)

        obj = bpy.data.objects.new(name, mesh)
        visual.objects.link(obj)
        obj.data.materials.append({"wall": projected_wall, "roof": roof, "ground": ground}[semantic])
        obj["source_provider"] = "Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV)"
        obj["source_dataset"] = "3D-Gebäudemodell LoD2-DE Hamburg 2026"
        obj["source_license"] = "dl-de-by-2.0"
        obj["source_attribution"] = "Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV)"
        obj["source_semantic"] = semantic
        if semantic == "wall":
            obj["facade_reference"] = "Poly Haven hansaplatz panorama, CC0-1.0"
            obj["facade_projection_yaw_deg"] = panorama_yaw_deg
        created += 1

    width = max_runtime[0] - min_runtime[0]
    height = max_runtime[1] - min_runtime[1]
    depth = max_runtime[2] - min_runtime[2]
    if not (20.0 <= width <= 380.0 and 3.0 <= height <= 140.0 and 20.0 <= depth <= 380.0):
        raise RuntimeError(
            "Hamburg LoD2 local bounds are implausible for Hansaplatz: "
            f"width={width:.2f}m height={height:.2f}m depth={depth:.2f}m"
        )
    print(f"Hamburg LoD2 runtime bounds: width={width:.2f}m height={height:.2f}m depth={depth:.2f}m")
    return created


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {args.collection}")
    visual = find_visual(root)
    panorama = Path(args.panorama)
    removed = remove_previous_macro_geometry()
    created = create_semantic_objects(Path(args.obj), visual, panorama, args.panorama_yaw_deg)

    root["official_lod2_source"] = "https://daten-hamburg.de/opendata/3d_stadtmodell_lod2/LoD2-DE_HH_2026-04-28.zip"
    root["official_lod2_provider"] = "Freie und Hansestadt Hamburg, LGV"
    root["official_lod2_license"] = "dl-de-by-2.0"
    root["official_lod2_reference_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
    root["official_lod2_reference_gps"] = "53.554451,10.012056"
    root["official_lod2_removed_previous_objects"] = removed
    root["official_lod2_created_semantic_objects"] = created
    root["macro_geometry_basis"] = "Hamburg official cadastral LoD2-DE 2026"
    root["facade_detail_basis"] = "Poly Haven hansaplatz CC0 equirectangular projection"
    root["facade_projection_yaw_deg"] = args.panorama_yaw_deg
    root["facade_projection_emissive"] = False

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg Hansaplatz LoD2 applied: "
        f"removed previous={removed}, created semantic objects={created}, yaw={args.panorama_yaw_deg}"
    )


if __name__ == "__main__":
    main()
