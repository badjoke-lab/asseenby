"""Replace guessed Hansaplatz building masses with official Berlin LoD2 geometry.

Runs after reconstruct_hansaplatz_c0.py. The plaza paving, canopies, subway entry
and authored street props remain, while all hand-guessed building/pavilion masses
are deleted and replaced with the local OBJ generated from Berlin's official LoD2.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import sys

import bpy


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--obj", required=True)
    return parser.parse_args(argv)


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


def remove_guessed_buildings() -> int:
    prefixes = (
        "hansaplatz_north_retail",
        "hansaplatz_east_retail",
        "hansaplatz_south_retail",
        "hansaplatz_west_retail",
        "hansaplatz_grips_theatre",
        "hansaplatz_north_perimeter",
        "hansaplatz_northwest_perimeter",
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
            face = []
            for token in parts[1:]:
                index = int(token.split("/", 1)[0])
                face.append(index - 1 if index > 0 else len(vertices) + index)
            objects[current].append(face)
    return vertices, objects


def create_semantic_objects(path: Path, visual: bpy.types.Collection) -> int:
    vertices, objects = load_obj(path)
    if not vertices or not objects:
        raise RuntimeError(f"LoD2 OBJ has no usable geometry: {path}")

    wall = bpy.data.materials.get("hansaplatz_small_white_ceramic_pbr") or fallback_material(
        "berlin_lod2_wall_reference", (0.56, 0.54, 0.50, 1.0), 0.76
    )
    roof = bpy.data.materials.get("hansaplatz_roof_dark") or fallback_material(
        "berlin_lod2_roof_reference", (0.10, 0.11, 0.12, 1.0), 0.68
    )
    ground = bpy.data.materials.get("hansaplatz_facade_stone") or fallback_material(
        "berlin_lod2_ground_reference", (0.30, 0.29, 0.27, 1.0), 0.82
    )

    created = 0
    for name, global_faces in objects.items():
        used = sorted({index for face in global_faces for index in face})
        remap = {old: new for new, old in enumerate(used)}
        local_vertices = [vertices[index] for index in used]
        local_faces = [[remap[index] for index in face] for face in global_faces]
        mesh = bpy.data.meshes.new(f"{name}_mesh")
        mesh.from_pydata(local_vertices, [], local_faces)
        mesh.validate(verbose=False)
        mesh.update(calc_edges=True)
        obj = bpy.data.objects.new(name, mesh)
        visual.objects.link(obj)
        semantic = "roof" if name.endswith("_roof") else "ground" if name.endswith("_ground") else "wall"
        obj.data.materials.append({"wall": wall, "roof": roof, "ground": ground}[semantic])
        obj["source_provider"] = "Senatsverwaltung für Stadtentwicklung, Bauen und Wohnen Berlin"
        obj["source_dataset"] = "3D-Gebäudemodelle im Level of Detail 2 (LoD 2)"
        obj["source_license"] = "dl-de-zero-2.0"
        obj["source_semantic"] = semantic
        created += 1
    return created


def main() -> None:
    args = parse_args()
    root = bpy.data.collections.get(args.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {args.collection}")
    visual = find_visual(root)
    removed = remove_guessed_buildings()
    created = create_semantic_objects(Path(args.obj), visual)

    root["official_lod2_source"] = "https://gdi.berlin.de/data/a_lod2/atom/0.atom"
    root["official_lod2_license"] = "dl-de-zero-2.0"
    root["official_lod2_reference_location"] = "Hansaplatz, Berlin, Germany"
    root["official_lod2_removed_guessed_objects"] = removed
    root["official_lod2_created_semantic_objects"] = created
    root["macro_geometry_basis"] = "Berlin official cadastral LoD2"

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"Berlin LoD2 Hansaplatz applied: removed guessed={removed}, created semantic objects={created}")


if __name__ == "__main__":
    main()
