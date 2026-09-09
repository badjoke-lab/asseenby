"""Replace C0 macro geometry with the real Hamburg Hansaplatz LoD2 subset.

The Poly Haven Hansaplatz HDRI GPS is 53.554451, 10.012056 in Hamburg-St. Georg.
This pass consumes the local OBJ extracted from Hamburg LGV LoD2-DE 2026 and uses
that official cadastral geometry as the building-envelope source of truth.

Important quality rule: the equirectangular Poly Haven panorama is NOT projected
onto building walls.  It remains a photographic/environment reference only.
Close-range facade depth is authored separately in Blender by
``author_hamburg_lod2_facades.py``.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
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
    # Kept as a backwards-compatible build argument.  The image is reference-only.
    parser.add_argument("--panorama", default="")
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
        "hamburg_facade_authored_",
    )
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith(prefixes)]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def flat_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    if bsdf.inputs.get("Metallic") is not None:
        bsdf.inputs["Metallic"].default_value = metallic
    return material


def masonry_material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.74
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"{name}_micro_surface"
    noise.inputs["Scale"].default_value = 18.0
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.62
    bump = nodes.new("ShaderNodeBump")
    bump.name = f"{name}_micro_bump"
    bump.inputs["Strength"].default_value = 0.10
    bump.inputs["Distance"].default_value = 0.035
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    material["texture_basis"] = "procedural micro-relief; no panorama projection"
    return material


def facade_palette() -> list[bpy.types.Material]:
    return [
        masonry_material("hamburg_facade_masonry_warm_stone", (0.43, 0.36, 0.28, 1.0)),
        masonry_material("hamburg_facade_masonry_cream", (0.55, 0.50, 0.42, 1.0)),
        masonry_material("hamburg_facade_masonry_muted_ochre", (0.46, 0.34, 0.22, 1.0)),
        masonry_material("hamburg_facade_masonry_grey_stone", (0.34, 0.33, 0.31, 1.0)),
        masonry_material("hamburg_facade_masonry_brown", (0.31, 0.24, 0.19, 1.0)),
    ]


def stable_material_index(name: str, count: int) -> int:
    value = int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:8], 16)
    return value % count


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


def create_semantic_objects(path: Path, visual: bpy.types.Collection) -> int:
    vertices, objects = load_obj(path)
    if not vertices or not objects:
        raise RuntimeError(f"Hamburg LoD2 OBJ has no usable geometry: {path}")

    walls = facade_palette()
    roof = flat_material("hamburg_lod2_roof_reference", (0.085, 0.090, 0.095, 1.0), 0.72)
    ground = flat_material("hamburg_lod2_ground_reference", (0.25, 0.24, 0.225, 1.0), 0.84)

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
        obj = bpy.data.objects.new(name, mesh)
        visual.objects.link(obj)
        if semantic == "wall":
            wall_material = walls[stable_material_index(name, len(walls))]
            obj.data.materials.append(wall_material)
        else:
            obj.data.materials.append({"roof": roof, "ground": ground}[semantic])
        obj["source_provider"] = "Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV)"
        obj["source_dataset"] = "3D-Gebäudemodell LoD2-DE Hamburg 2026"
        obj["source_license"] = "dl-de-by-2.0"
        obj["source_attribution"] = "Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV)"
        obj["source_semantic"] = semantic
        if semantic == "wall":
            obj["facade_photo_reference"] = "Poly Haven hansaplatz panorama, CC0-1.0; reference only"
            obj["facade_panorama_projection"] = False
            obj["facade_depth_layer"] = "scripts/blender/author_hamburg_lod2_facades.py"
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
    removed = remove_previous_macro_geometry()
    created = create_semantic_objects(Path(args.obj), visual)

    root["official_lod2_source"] = "https://daten-hamburg.de/opendata/3d_stadtmodell_lod2/LoD2-DE_HH_2026-04-28.zip"
    root["official_lod2_provider"] = "Freie und Hansestadt Hamburg, LGV"
    root["official_lod2_license"] = "dl-de-by-2.0"
    root["official_lod2_reference_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
    root["official_lod2_reference_gps"] = "53.554451,10.012056"
    root["official_lod2_removed_previous_objects"] = removed
    root["official_lod2_created_semantic_objects"] = created
    root["macro_geometry_basis"] = "Hamburg official cadastral LoD2-DE 2026"
    root["facade_detail_basis"] = "Blender-authored geometry; Poly Haven panorama is reference/background only"
    root["facade_panorama_projection"] = False
    root["facade_projection_emissive"] = False
    if args.panorama:
        root["facade_photo_reference_path"] = args.panorama
        root["facade_photo_reference_yaw_deg"] = args.panorama_yaw_deg

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg Hansaplatz LoD2 applied without facade panorama projection: "
        f"removed previous={removed}, created semantic objects={created}"
    )


if __name__ == "__main__":
    main()
