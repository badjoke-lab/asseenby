"""Remove equirectangular wall projection and restore varied physical substrates.

The checked-in Poly Haven Hansaplatz panorama is reconstruction evidence and IBL
reference only. It must never be mapped to Hamburg building walls. Official LGV
LoD2 remains the macro envelope. This pass assigns deterministic per-building
procedural masonry/stucco materials so legitimate blank/party walls do not collapse
into one uniform CG slab while authored geometry supplies close facade depth.
"""

from __future__ import annotations

import hashlib

import bpy

PALETTE = (
    ((0.20, 0.175, 0.145, 1.0), (0.34, 0.30, 0.245, 1.0), (0.46, 0.415, 0.345, 1.0)),
    ((0.26, 0.245, 0.215, 1.0), (0.43, 0.405, 0.355, 1.0), (0.58, 0.545, 0.465, 1.0)),
    ((0.18, 0.185, 0.19, 1.0), (0.315, 0.32, 0.325, 1.0), (0.44, 0.44, 0.425, 1.0)),
    ((0.245, 0.185, 0.135, 1.0), (0.405, 0.31, 0.225, 1.0), (0.52, 0.415, 0.31, 1.0)),
    ((0.205, 0.155, 0.13, 1.0), (0.34, 0.255, 0.205, 1.0), (0.445, 0.355, 0.29, 1.0)),
    ((0.29, 0.275, 0.245, 1.0), (0.46, 0.435, 0.385, 1.0), (0.61, 0.575, 0.505, 1.0)),
)


def stable_index(name: str) -> int:
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % len(PALETTE)


def procedural_facade_material(index: int) -> bpy.types.Material:
    name = f"hamburg_lod2_facade_substrate_v3_{index}"
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (650, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (400, 0)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-760, 90)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-580, 90)
    mapping.inputs["Scale"].default_value = (1.0 + index * 0.035,) * 3
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])

    broad = nodes.new("ShaderNodeTexNoise")
    broad.location = (-370, 180)
    broad.inputs["Scale"].default_value = 0.62 + index * 0.07
    broad.inputs["Detail"].default_value = 3.0 + (index % 3) * 0.45
    broad.inputs["Roughness"].default_value = 0.60 + (index % 2) * 0.08
    broad.inputs["Distortion"].default_value = 0.05 + (index % 3) * 0.025
    links.new(mapping.outputs["Vector"], broad.inputs["Vector"])

    ramp_node = nodes.new("ShaderNodeValToRGB")
    ramp_node.location = (-100, 180)
    ramp = ramp_node.color_ramp
    ramp.elements.remove(ramp.elements[1])
    dark, middle, light = PALETTE[index]
    left = ramp.elements[0]
    left.position = 0.20
    left.color = dark
    mid = ramp.elements.new(0.52)
    mid.color = middle
    right = ramp.elements.new(0.82)
    right.color = light
    links.new(broad.outputs["Fac"], ramp_node.inputs["Fac"])
    links.new(ramp_node.outputs["Color"], bsdf.inputs["Base Color"])

    micro = nodes.new("ShaderNodeTexNoise")
    micro.location = (-360, -120)
    micro.inputs["Scale"].default_value = 15.0 + index * 1.6
    micro.inputs["Detail"].default_value = 3.6 + (index % 3) * 0.35
    micro.inputs["Roughness"].default_value = 0.68
    links.new(mapping.outputs["Vector"], micro.inputs["Vector"])

    bump = nodes.new("ShaderNodeBump")
    bump.location = (145, -125)
    bump.inputs["Strength"].default_value = 0.12 + (index % 3) * 0.025
    bump.inputs["Distance"].default_value = 0.045 + (index % 2) * 0.015
    links.new(micro.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    rough_map = nodes.new("ShaderNodeMapRange")
    rough_map.location = (-80, -205)
    rough_map.inputs["From Min"].default_value = 0.0
    rough_map.inputs["From Max"].default_value = 1.0
    rough_map.inputs["To Min"].default_value = 0.58 + (index % 2) * 0.03
    rough_map.inputs["To Max"].default_value = 0.82 + (index % 3) * 0.02
    rough_map.clamp = True
    links.new(micro.outputs["Fac"], rough_map.inputs["Value"])
    links.new(rough_map.outputs["Result"], bsdf.inputs["Roughness"])

    metallic = bsdf.inputs.get("Metallic")
    if metallic is not None:
        metallic.default_value = 0.0
    emission_strength = bsdf.inputs.get("Emission Strength")
    if emission_strength is not None:
        emission_strength.default_value = 0.0

    material["quality_role"] = "varied-procedural-official-geometry-substrate"
    material["material_basis"] = "deterministic building-level masonry/stucco variation; no photographic facade claim"
    material["palette_index"] = index
    material["raw_panorama_projection"] = False
    material["reference_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
    return material


def main() -> None:
    root = bpy.data.collections.get("C0")
    if root is None:
        raise RuntimeError("Missing C0 collection")

    substrates = [procedural_facade_material(i) for i in range(len(PALETTE))]
    changed = 0
    distribution = [0 for _ in PALETTE]
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
        index = stable_index(obj.name)
        obj.data.materials.clear()
        obj.data.materials.append(substrates[index])
        while obj.data.uv_layers:
            obj.data.uv_layers.remove(obj.data.uv_layers[0])
        obj["facade_reference"] = "Poly Haven hansaplatz used as reference evidence only"
        obj["raw_panorama_wall_projection"] = False
        obj["quality_role"] = "official-hamburg-lod2-macro-shell"
        obj["procedural_substrate_palette_index"] = index
        distribution[index] += 1
        changed += 1

    if changed == 0:
        raise RuntimeError("No Hamburg LoD2 wall objects were found to clean")
    if sum(1 for count in distribution if count > 0) < 4:
        raise RuntimeError(f"Hamburg substrate palette collapsed unexpectedly: {distribution}")

    root["raw_panorama_wall_projection"] = False
    root["facade_detail_basis"] = "Blender-authored close facade overlay; panorama is reference evidence/IBL only"
    root["official_nearfield_geometry"] = "Hamburg LoD2-DE 2026"
    root["official_lod3_nearfield_status"] = "coverage gap verified in Area1 2024 and 2025"
    root["hamburg_wall_substrate_quality_version"] = 3
    root["hamburg_wall_substrate_palette_size"] = len(PALETTE)
    root["hamburg_wall_substrate_distribution"] = ",".join(str(v) for v in distribution)
    root["hamburg_wall_substrate_basis"] = "deterministic per-building procedural masonry/stucco color, normal and roughness variation; no panorama projection"
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

    print(f"Removed raw panorama projection from {changed} Hamburg LoD2 wall objects")
    print("Applied procedural wall substrate palette:", [m.name for m in substrates])
    print("Substrate distribution:", distribution)
    print("Former wall materials:", sorted(removed_material_names))


if __name__ == "__main__":
    main()
