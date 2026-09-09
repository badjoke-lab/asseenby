"""Remove the temporary equirectangular wall projection from Hamburg C0.

The checked-in Poly Haven Hansaplatz panorama is reconstruction evidence and may
remain as the far/reference environment. It must not be used as a permanent wall
material because cars, people, trees and perspective distortion are baked into a
single capture. This pass preserves official Hamburg LoD2 geometry and replaces
only the wall material with a physically-lit neutral facade substrate so an
authored close-facade layer can supply windows, doors, storefront depth and trim.
"""

from __future__ import annotations

import bpy


def neutral_facade_material() -> bpy.types.Material:
    name = "hamburg_lod2_facade_substrate"
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)
        material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        raise RuntimeError("Principled BSDF missing from Hamburg facade substrate")

    # Disconnect any inherited image-driven base colour/emission inputs.
    for socket_name in ("Base Color", "Emission Color", "Emission"):
        socket = bsdf.inputs.get(socket_name)
        if socket is not None:
            for link in list(socket.links):
                links.remove(link)

    bsdf.inputs["Base Color"].default_value = (0.32, 0.29, 0.25, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.72
    metallic = bsdf.inputs.get("Metallic")
    if metallic is not None:
        metallic.default_value = 0.0
    emission_strength = bsdf.inputs.get("Emission Strength")
    if emission_strength is not None:
        emission_strength.default_value = 0.0

    material["quality_role"] = "neutral-official-geometry-substrate"
    material["raw_panorama_projection"] = False
    material["reference_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
    return material


def main() -> None:
    root = bpy.data.collections.get("C0")
    if root is None:
        raise RuntimeError("Missing C0 collection")

    substrate = neutral_facade_material()
    changed = 0
    removed_material_names: set[str] = set()

    for obj in bpy.data.objects:
        if not obj.name.startswith("lod2_") or obj.type != "MESH":
            continue
        semantic = str(obj.get("source_semantic", ""))
        if semantic != "wall" and not obj.name.endswith("_wall"):
            continue
        for slot in obj.material_slots:
            if slot.material is not None:
                removed_material_names.add(slot.material.name)
        obj.data.materials.clear()
        obj.data.materials.append(substrate)
        # Projection UVs are not needed for authored facade geometry. Removing them
        # also prevents a later material substitution from silently reviving it.
        while obj.data.uv_layers:
            obj.data.uv_layers.remove(obj.data.uv_layers[0])
        obj["facade_reference"] = "Poly Haven hansaplatz used as reference evidence only"
        obj["raw_panorama_wall_projection"] = False
        obj["quality_role"] = "official-hamburg-lod2-macro-shell"
        changed += 1

    if changed == 0:
        raise RuntimeError("No Hamburg LoD2 wall objects were found to clean")

    root["raw_panorama_wall_projection"] = False
    root["facade_detail_basis"] = "Blender-authored close facade overlay; panorama is reference evidence only"
    root["official_nearfield_geometry"] = "Hamburg LoD2-DE 2026"
    root["official_lod3_nearfield_status"] = "coverage gap verified in Area1 2024 and 2025"
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

    print(f"Removed raw panorama projection from {changed} Hamburg LoD2 wall objects")
    print("Former wall materials:", sorted(removed_material_names))


if __name__ == "__main__":
    main()
