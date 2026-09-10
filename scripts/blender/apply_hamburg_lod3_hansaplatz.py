"""Replace C0 macro shell with official Hamburg Hansaplatz LoD3.0-HH geometry.

This pass deliberately does NOT project the equirectangular panorama onto building
walls. The panorama remains reconstruction evidence and a far environment. Close
facades must be authored separately in Blender so transient photo content is not
baked into permanent walls.
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


def fallback_material(
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


def glass_material() -> bpy.types.Material:
    name = "hamburg_lod3_opening_glass_reference"
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.035, 0.055, 0.065, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.16
    metallic = bsdf.inputs.get("Metallic")
    if metallic is not None:
        metallic.default_value = 0.0
    transmission = bsdf.inputs.get("Transmission Weight") or bsdf.inputs.get("Transmission")
    if transmission is not None:
        transmission.default_value = 0.35
    return material


def load_obj(path: Path):
    vertices: list[tuple[float, float, float]] = []
    objects: dict[str, list[list[int]]] = defaultdict(list)
    current = "lod3_unknown_wall"
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


def semantic_from_name(name: str) -> str:
    for semantic in ("window", "door", "roof", "ground", "ceiling", "floor", "closure", "wall"):
        if name.endswith(f"_{semantic}"):
            return semantic
    return "wall"


def create_semantic_objects(path: Path, visual: bpy.types.Collection) -> tuple[int, dict[str, int]]:
    vertices, objects = load_obj(path)
    if not vertices or not objects:
        raise RuntimeError(f"Hamburg LoD3 OBJ has no usable geometry: {path}")

    materials = {
        "wall": bpy.data.materials.get("hansaplatz_facade_stone")
        or fallback_material("hamburg_lod3_wall_shell", (0.32, 0.30, 0.27, 1.0), 0.72),
        "roof": bpy.data.materials.get("hansaplatz_roof_dark")
        or fallback_material("hamburg_lod3_roof_shell", (0.08, 0.09, 0.10, 1.0), 0.70),
        "ground": fallback_material("hamburg_lod3_ground_shell", (0.27, 0.27, 0.25, 1.0), 0.86),
        "floor": fallback_material("hamburg_lod3_floor_shell", (0.24, 0.24, 0.23, 1.0), 0.82),
        "ceiling": fallback_material("hamburg_lod3_ceiling_shell", (0.28, 0.28, 0.27, 1.0), 0.80),
        "closure": fallback_material("hamburg_lod3_closure_shell", (0.30, 0.29, 0.27, 1.0), 0.76),
        "window": glass_material(),
        "door": fallback_material("hamburg_lod3_door_reference", (0.12, 0.10, 0.09, 1.0), 0.42),
    }

    created = 0
    counts: dict[str, int] = defaultdict(int)
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
            raise RuntimeError(f"Hamburg LoD3 mesh remained non-triangular: {name}")

        semantic = semantic_from_name(name)
        obj = bpy.data.objects.new(name, mesh)
        visual.objects.link(obj)
        obj.data.materials.append(materials[semantic])
        obj["source_provider"] = "Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV)"
        obj["source_dataset"] = "3D-Gebäudemodell LoD3.0-HH Hamburg untexturiert, Area1, 2025"
        obj["source_license"] = "dl-de-by-2.0"
        obj["source_semantic"] = semantic
        obj["quality_role"] = "macro-shell"
        counts[semantic] += 1
        created += 1

    width = max_runtime[0] - min_runtime[0]
    height = max_runtime[1] - min_runtime[1]
    depth = max_runtime[2] - min_runtime[2]
    if not (20.0 <= width <= 400.0 and 3.0 <= height <= 160.0 and 20.0 <= depth <= 400.0):
        raise RuntimeError(
            "Hamburg LoD3 local bounds are implausible for Hansaplatz: "
            f"width={width:.2f}m height={height:.2f}m depth={depth:.2f}m"
        )
    print(f"Hamburg LoD3 runtime bounds: width={width:.2f}m height={height:.2f}m depth={depth:.2f}m")
    print(f"Hamburg LoD3 semantic objects: {dict(sorted(counts.items()))}")
    return created, dict(counts)


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {args.collection}")
    visual = find_visual(root)
    removed = remove_previous_macro_geometry()
    created, counts = create_semantic_objects(Path(args.obj), visual)

    root["official_geometry_level"] = "LoD3.0-HH"
    root["official_lod3_source"] = args.source_url
    root["official_lod3_provider"] = "Freie und Hansestadt Hamburg, LGV"
    root["official_lod3_license"] = "dl-de-by-2.0"
    root["official_lod3_reference_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
    root["official_lod3_reference_gps"] = "53.554451,10.012056"
    root["official_lod3_removed_previous_objects"] = removed
    root["official_lod3_created_semantic_objects"] = created
    root["official_lod3_semantic_counts"] = str(dict(sorted(counts.items())))
    root["macro_geometry_basis"] = "Hamburg official LoD3.0-HH untextured Area1 2025"
    root["facade_detail_basis"] = "Blender-authored facade overlay required; Poly Haven panorama is reference only"
    root["raw_panorama_wall_projection"] = False

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg Hansaplatz LoD3 applied: "
        f"removed previous={removed}, created semantic objects={created}"
    )


if __name__ == "__main__":
    main()
