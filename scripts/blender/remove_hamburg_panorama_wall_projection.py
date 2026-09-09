"""Remove the temporary equirectangular wall projection from Hamburg C0.

The checked-in Poly Haven Hansaplatz panorama is reconstruction evidence and may
remain as the far/reference environment. It must not be used as a permanent wall
material because cars, people, trees and perspective distortion are baked into a
single capture. This pass preserves official Hamburg LoD2 geometry and replaces
only the wall material with a physically-lit procedural masonry/stucco substrate
so unfenestrated side walls still read as real material while authored close-facade
geometry supplies windows, doors, storefront depth and trim where appropriate.
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

    # Rebuild this material deterministically so a previous flat/image-driven state
    # cannot survive a later regeneration.
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (640, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (390, 0)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-720, 80)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-540, 80)
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])

    # Broad low-contrast variation keeps large legitimate party walls from reading
    # as featureless CG slabs. This is procedural material variation, not facade data.
    broad = nodes.new("ShaderNodeTexNoise")
    broad.location = (-340, 170)
    broad.inputs["Scale"].default_value = 0.72
    broad.inputs["Detail"].default_value = 3.4
    broad.inputs["Roughness"].default_value = 0.64
    broad.inputs["Distortion"].default_value = 0.08
    links.new(mapping.outputs["Vector"], broad.inputs["Vector"])

    color = nodes.new("ShaderNodeValToRGB")
    color.location = (-100, 180)
    ramp = color.color_ramp
    ramp.elements.remove(ramp.elements[1])
    left = ramp.elements[0]
    left.position = 0.22
    left.color = (0.205, 0.181, 0.151, 1.0)
    mid = ramp.elements.new(0.53)
    mid.color = (0.335, 0.298, 0.247, 1.0)
    right = ramp.elements.new(0.80)
    right.color = (0.445, 0.403, 0.340, 1.0)
    links.new(broad.outputs["Fac"], color.inputs["Fac"])
    links.new(color.outputs["Color"], bsdf.inputs["Base Color"])

    # Finer stucco/stone relief affects normal and roughness, not silhouette. The low
    # strength is intentional: official LoD2 remains the envelope source of truth.
    micro = nodes.new("ShaderNodeTexNoise")
    micro.location = (-330, -120)
    micro.inputs["Scale"].default_value = 19.0
    micro.inputs["Detail"].default_value = 4.2
    micro.inputs["Roughness"].default_value = 0.72
    links.new(mapping.outputs["Vector"], micro.inputs["Vector"])

    bump = nodes.new("ShaderNodeBump")
    bump.location = (145, -125)
    bump.inputs["Strength"].default_value = 0.18
    bump.inputs["Distance"].default_value = 0.065
    links.new(micro.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    rough_map = nodes.new("ShaderNodeMapRange")
    rough_map.location = (-80, -195)
    rough_map.inputs["From Min"].default_value = 0.0
    rough_map.inputs["From Max"].default_value = 1.0
    rough_map.inputs["To Min"].default_value = 0.60
    rough_map.inputs["To Max"].default_value = 0.84
    rough_map.clamp = True
    links.new(micro.outputs["Fac"], rough_map.inputs["Value"])
    links.new(rough_map.outputs["Result"], bsdf.inputs["Roughness"])

    metallic = bsdf.inputs.get("Metallic")
    if metallic is not None:
        metallic.default_value = 0.0
    emission_strength = bsdf.inputs.get("Emission Strength")
    if emission_strength is not None:
        emission_strength.default_value = 0.0

    material["quality_role"] = "procedural-official-geometry-substrate"
    material["material_basis"] = "procedural masonry/stucco variation; no photographic facade claim"
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
    root["hamburg_wall_substrate_quality_version"] = 2
    root["hamburg_wall_substrate_basis"] = "procedural masonry/stucco color, normal and roughness variation; no panorama projection"
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

    print(f"Removed raw panorama projection from {changed} Hamburg LoD2 wall objects")
    print("Applied procedural wall substrate:", substrate.name)
    print("Former wall materials:", sorted(removed_material_names))


if __name__ == "__main__":
    main()
