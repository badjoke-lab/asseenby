"""Replace provisional raised Hansaplatz paving boxes with one continuous plaza surface.

The earlier reference reconstruction tiled the plaza with dozens of shallow beveled
boxes. At Human eye level their bevels and individual top faces read as large white
platforms and occlude the photographic/LoD2 facade, especially after turning. The
real plaza is effectively continuous at this scale, so retain the checked-in CC0
scanned pavement material but put it on one coplanar authored mesh instead.
"""

from __future__ import annotations

import bpy


def runtime_to_blender(point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = point
    return (x, -z, y)


def find_visual(root: bpy.types.Collection) -> bpy.types.Collection:
    visual = next((child for child in root.children if child.name == "VISUAL_LOD0"), None)
    if visual is None:
        raise RuntimeError("C0 is missing VISUAL_LOD0")
    return visual


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

    material = bpy.data.materials.get("hansaplatz_concrete_pavement_pbr")
    if material is None:
        raise RuntimeError("Missing Hansaplatz scanned pavement material")

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

    obj = bpy.data.objects.new("hansaplatz_plaza_ground_reference_plane", mesh)
    visual.objects.link(obj)
    obj.data.materials.append(material)
    obj["reference_basis"] = "Hansaplatz open plaza; continuous surface at browser scale"
    obj["material_source"] = "Poly Haven concrete_pavement"
    obj["material_license"] = "CC0-1.0"
    obj["replaces_provisional_paving_slabs"] = len(doomed)

    root["hansaplatz_paving_geometry"] = "single continuous coplanar reference surface"
    root["hansaplatz_removed_paving_slabs"] = len(doomed)
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"Hansaplatz paving field replaced: removed slabs={len(doomed)}, continuous surface=1")


if __name__ == "__main__":
    main()
