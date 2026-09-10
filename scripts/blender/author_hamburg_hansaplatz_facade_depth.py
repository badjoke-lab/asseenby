"""Add a bounded close-facade depth pass to the official Hamburg LoD2 shell.

This is intentionally a structural pass, not a claim that every window is a
surveyed reconstruction. It fixes the current zero-depth wall failure by adding
recess cues, glazing, mullions, sills, floor bands and cornices only to the
nearest plaza-facing facades. The Poly Haven Hansaplatz panorama is reference
evidence; no photographic pixels are mapped onto these objects.

The pass is deterministic and idempotent. Macro position/roof geometry stays the
official Hamburg LoD2-DE 2026 geometry already present in the C0 collection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import bpy

PREFIX = "hamburg_authored_facade_"
MAX_BUILDINGS = 14
MAX_DISTANCE_M = 95.0
MAX_TOTAL_BAYS = 150


def material(name: str, color, roughness: float, metallic: float = 0.0, emission=None, emission_strength: float = 0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    metallic_socket = bsdf.inputs.get("Metallic")
    if metallic_socket is not None:
        metallic_socket.default_value = metallic
    if emission is not None:
        socket = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if socket is not None:
            socket.default_value = emission
        strength = bsdf.inputs.get("Emission Strength")
        if strength is not None:
            strength.default_value = emission_strength
    return mat


@dataclass
class MeshBuilder:
    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    faces: list[tuple[int, int, int, int]] = field(default_factory=list)

    def box(self, center, dims):
        cx, cy, cz = center
        dx, dy, dz = (value / 2.0 for value in dims)
        base = len(self.vertices)
        self.vertices.extend([
            (cx-dx, cy-dy, cz-dz), (cx+dx, cy-dy, cz-dz),
            (cx+dx, cy+dy, cz-dz), (cx-dx, cy+dy, cz-dz),
            (cx-dx, cy-dy, cz+dz), (cx+dx, cy-dy, cz+dz),
            (cx+dx, cy+dy, cz+dz), (cx-dx, cy+dy, cz+dz),
        ])
        self.faces.extend([
            (base+0, base+1, base+2, base+3),
            (base+4, base+7, base+6, base+5),
            (base+0, base+4, base+5, base+1),
            (base+1, base+5, base+6, base+2),
            (base+2, base+6, base+7, base+3),
            (base+4, base+0, base+3, base+7),
        ])

    def emit(self, collection, name, mat):
        if not self.faces:
            return None
        mesh = bpy.data.meshes.new(name + "_mesh")
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.validate(verbose=False)
        mesh.update(calc_edges=True)
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        obj.data.materials.append(mat)
        obj["quality_role"] = "authored-close-facade-depth"
        obj["reference_location"] = "Hansaplatz, Hamburg-St. Georg, Germany"
        obj["raw_panorama_projection"] = False
        return obj


def remove_previous() -> int:
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith(PREFIX)]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def bbox_world(obj):
    corners = [obj.matrix_world @ __import__('mathutils').Vector(corner) for corner in obj.bound_box]
    xs = [v.x for v in corners]; ys = [v.y for v in corners]; zs = [v.z for v in corners]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def bbox_distance_xy(box) -> float:
    minx, miny, _, maxx, maxy, _ = box
    dx = 0.0 if minx <= 0.0 <= maxx else min(abs(minx), abs(maxx))
    dy = 0.0 if miny <= 0.0 <= maxy else min(abs(miny), abs(maxy))
    return math.hypot(dx, dy)


def facade_side(box):
    minx, miny, _, maxx, maxy, _ = box
    sides = [
        (abs(minx), "minx"), (abs(maxx), "maxx"),
        (abs(miny), "miny"), (abs(maxy), "maxy"),
    ]
    return min(sides)[1]


def add_oriented_box(builder: MeshBuilder, side: str, plane: float, horizontal: float, z: float, width: float, height: float, depth: float, outward_offset: float = 0.0):
    if side == "minx":
        builder.box((plane - outward_offset, horizontal, z), (depth, width, height))
    elif side == "maxx":
        builder.box((plane + outward_offset, horizontal, z), (depth, width, height))
    elif side == "miny":
        builder.box((horizontal, plane - outward_offset, z), (width, depth, height))
    else:
        builder.box((horizontal, plane + outward_offset, z), (width, depth, height))


def facade_axis_data(box, side):
    minx, miny, minz, maxx, maxy, maxz = box
    if side == "minx": return minx, miny, maxy, minz, maxz
    if side == "maxx": return maxx, miny, maxy, minz, maxz
    if side == "miny": return miny, minx, maxx, minz, maxz
    return maxy, minx, maxx, minz, maxz


def author_one(box, side, glass: MeshBuilder, trim: MeshBuilder, dark: MeshBuilder, accent: MeshBuilder, bay_budget: int):
    plane, hmin, hmax, zmin, zmax = facade_axis_data(box, side)
    width = hmax - hmin
    height = zmax - zmin
    if width < 5.5 or height < 5.8:
        return 0

    margin = max(0.65, min(1.25, width * 0.06))
    usable = width - 2.0 * margin
    if usable < 3.0:
        return 0
    bays = max(2, min(12, int(usable / 2.25)))
    bays = min(bays, bay_budget)
    if bays <= 0:
        return 0
    pitch = usable / bays
    pane_w = max(0.75, min(1.55, pitch * 0.66))

    # Ground-floor shopfront rhythm: dark glazing field plus projecting frames.
    storefront_h = min(2.65, max(2.15, height * 0.16))
    storefront_z = zmin + 0.30 + storefront_h / 2.0
    for bay in range(bays):
        h = hmin + margin + pitch * (bay + 0.5)
        add_oriented_box(dark, side, plane, h, storefront_z, pitch * 0.82, storefront_h, 0.055, 0.045)
        # vertical frame at the left edge of each bay
        edge = hmin + margin + pitch * bay
        add_oriented_box(trim, side, plane, edge, storefront_z, 0.075, storefront_h + 0.12, 0.09, 0.095)
    add_oriented_box(trim, side, plane, hmin + margin + usable, storefront_z, 0.075, storefront_h + 0.12, 0.09, 0.095)
    add_oriented_box(trim, side, plane, hmin + margin + usable/2.0, zmin + 0.27, usable + 0.15, 0.13, 0.11, 0.11)
    add_oriented_box(accent, side, plane, hmin + margin + usable/2.0, zmin + storefront_h + 0.52, usable + 0.28, 0.18, 0.16, 0.13)

    # Upper storeys. Keep the cadence bounded; this is a depth scaffold that will
    # be photo-registered facade by facade in the next pass.
    upper_bottom = zmin + storefront_h + 0.95
    upper_height = max(0.0, zmax - upper_bottom - 0.75)
    storeys = max(1, min(7, int(upper_height / 2.9))) if upper_height >= 2.2 else 0
    if storeys:
        floor_pitch = upper_height / storeys
        for floor in range(storeys):
            wz = upper_bottom + floor_pitch * (floor + 0.53)
            win_h = max(1.10, min(1.75, floor_pitch * 0.55))
            band_z = upper_bottom + floor_pitch * floor + 0.13
            add_oriented_box(accent, side, plane, hmin + margin + usable/2.0, band_z, usable + 0.22, 0.10, 0.15, 0.12)
            for bay in range(bays):
                h = hmin + margin + pitch * (bay + 0.5)
                add_oriented_box(glass, side, plane, h, wz, pane_w, win_h, 0.05, 0.055)
                # sill and head create a visible shadow break during translation.
                add_oriented_box(trim, side, plane, h, wz - win_h/2.0 - 0.07, pane_w + 0.16, 0.10, 0.11, 0.11)
                add_oriented_box(trim, side, plane, h, wz + win_h/2.0 + 0.06, pane_w + 0.11, 0.075, 0.095, 0.095)

    # Cornice / roof-edge projection is one of the strongest depth cues in the
    # supplied street-level reference.
    add_oriented_box(accent, side, plane, hmin + margin + usable/2.0, zmax - 0.22, usable + 0.45, 0.24, 0.32, 0.20)
    return bays


def main() -> None:
    root = bpy.data.collections.get("C0")
    if root is None:
        raise RuntimeError("Missing C0 collection")
    visual = next((child for child in root.children if child.name == "VISUAL_LOD0"), None)
    if visual is None:
        raise RuntimeError("C0 is missing VISUAL_LOD0")

    removed = remove_previous()
    candidates = []
    for obj in bpy.data.objects:
        if not obj.name.startswith("lod2_") or obj.type != "MESH":
            continue
        semantic = str(obj.get("source_semantic", ""))
        if semantic != "wall" and not obj.name.endswith("_wall"):
            continue
        box = bbox_world(obj)
        distance = bbox_distance_xy(box)
        if distance <= MAX_DISTANCE_M:
            candidates.append((distance, obj.name, box))
    candidates.sort(key=lambda row: (row[0], row[1]))
    candidates = candidates[:MAX_BUILDINGS]
    if not candidates:
        raise RuntimeError("No nearfield Hamburg LoD2 wall candidates found")

    glass_builder = MeshBuilder()
    trim_builder = MeshBuilder()
    dark_builder = MeshBuilder()
    accent_builder = MeshBuilder()
    remaining = MAX_TOTAL_BAYS
    authored = []
    for distance, name, box in candidates:
        side = facade_side(box)
        bays = author_one(box, side, glass_builder, trim_builder, dark_builder, accent_builder, remaining)
        if bays:
            authored.append((name, distance, side, bays))
            remaining -= bays
        if remaining <= 0:
            break
    if not authored:
        raise RuntimeError("Nearfield facade candidates produced no authored depth")

    glass_mat = material("hamburg_authored_window_glass", (0.028, 0.045, 0.055, 1.0), 0.16)
    trim_mat = material("hamburg_authored_window_trim", (0.055, 0.052, 0.047, 1.0), 0.38, metallic=0.12)
    dark_mat = material("hamburg_authored_storefront_glass", (0.035, 0.050, 0.052, 1.0), 0.20)
    accent_mat = material("hamburg_authored_stone_trim", (0.42, 0.37, 0.31, 1.0), 0.62)

    emitted = [
        glass_builder.emit(visual, PREFIX + "windows", glass_mat),
        trim_builder.emit(visual, PREFIX + "frames", trim_mat),
        dark_builder.emit(visual, PREFIX + "storefronts", dark_mat),
        accent_builder.emit(visual, PREFIX + "bands_cornices", accent_mat),
    ]
    emitted = [obj for obj in emitted if obj is not None]
    for obj in emitted:
        obj["source_geometry_basis"] = "Hamburg official LoD2-DE 2026"
        obj["reference_evidence"] = "Poly Haven hansaplatz CC0 photographic reference; no image projection"
        obj["reconstruction_status"] = "structural-depth-pass; photo registration remains required"

    root["authored_close_facade"] = True
    root["authored_close_facade_buildings"] = len(authored)
    root["authored_close_facade_bays"] = sum(row[3] for row in authored)
    root["authored_close_facade_status"] = "structural depth pass; facade-by-facade photo registration remains open"
    root["raw_panorama_wall_projection"] = False
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

    print(f"Removed previous authored facade objects: {removed}")
    print(f"Authored close facades: {len(authored)} buildings, {sum(row[3] for row in authored)} bay columns")
    for row in authored:
        print(f"FACADE {row[0]} distance={row[1]:.2f}m side={row[2]} bays={row[3]}")
    print(f"Emitted combined facade objects: {len(emitted)}")


if __name__ == "__main__":
    main()
