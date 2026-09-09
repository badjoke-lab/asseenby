#!/usr/bin/env python3
"""Author close-range facade depth over official Hamburg LoD2 geometry.

This pass deliberately does NOT project the Poly Haven panorama onto wall meshes.
The panorama remains a photographic reference/background only.  The structural
building envelope comes from the Hamburg LGV LoD2 subset; this script derives a
bounded set of facade modules from the real wall planes and adds actual geometry
for shopfront glazing, upper-storey windows, frames, sills, lintels, floor bands,
plinths and cornices.

It is intentionally restricted to near-field facades so distant LoD2 geometry
stays cheap and the authored layer does not become a city-wide procedural skin.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import math
from pathlib import Path
import sys

import bpy


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--obj", required=True, type=Path)
    parser.add_argument("--radius-m", type=float, default=72.0)
    parser.add_argument("--max-facades", type=int, default=28)
    return parser.parse_args(argv)


def runtime_to_blender(point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = point
    return (x, -z, y)


def find_visual(root: bpy.types.Collection) -> bpy.types.Collection:
    visual = next((child for child in root.children if child.name == "VISUAL_LOD0"), None)
    if visual is None:
        raise RuntimeError("C0 is missing VISUAL_LOD0")
    return visual


def relink(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    if target not in obj.users_collection:
        target.objects.link(obj)
    for collection in list(obj.users_collection):
        if collection != target:
            collection.objects.unlink(obj)


def material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    *,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing is not None:
        return existing
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    if bsdf.inputs.get("Metallic") is not None:
        bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        emission_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission_input is not None:
            emission_input.default_value = emission
        strength_input = bsdf.inputs.get("Emission Strength")
        if strength_input is not None:
            strength_input.default_value = emission_strength
    mat["authoring_basis"] = "Blender facade geometry derived from Hamburg LGV LoD2 wall planes"
    return mat


def load_obj(path: Path):
    vertices: list[tuple[float, float, float]] = []
    objects: dict[str, list[list[int]]] = defaultdict(list)
    current = "unknown"
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
                value = int(token.split("/", 1)[0])
                face.append(value - 1 if value > 0 else len(vertices) + value)
            objects[current].append(face)
    return vertices, objects


def unique_horizontal(points: list[tuple[float, float, float]]) -> list[tuple[float, float]]:
    seen: list[tuple[float, float]] = []
    for x, _, z in points:
        if not any(math.hypot(x - sx, z - sz) < 0.04 for sx, sz in seen):
            seen.append((x, z))
    return seen


def facade_segment(points: list[tuple[float, float, float]]):
    if len(points) < 3:
        return None
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    height = max_y - min_y
    if height < 5.5:
        return None
    horizontal = unique_horizontal(points)
    if len(horizontal) < 2:
        return None
    best = None
    best_len = 0.0
    for i, a in enumerate(horizontal):
        for b in horizontal[i + 1 :]:
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            if length > best_len:
                best = (a, b)
                best_len = length
    if best is None or best_len < 3.8:
        return None
    a, b = best
    ux = (b[0] - a[0]) / best_len
    uz = (b[1] - a[1]) / best_len
    # Pick the normal pointing roughly toward the reference observer at 0,0.
    nx, nz = -uz, ux
    midx, midz = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
    toward = (-midx, -midz)
    if nx * toward[0] + nz * toward[1] < 0:
        nx, nz = -nx, -nz
    distance = math.hypot(midx, midz)
    return {
        "a": a,
        "b": b,
        "mid": (midx, midz),
        "u": (ux, uz),
        "n": (nx, nz),
        "length": best_len,
        "min_y": min_y,
        "max_y": max_y,
        "height": height,
        "distance": distance,
    }


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def add_box_geometry(
    buckets: dict[str, tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]]],
    bucket: str,
    center: tuple[float, float, float],
    u: tuple[float, float],
    n: tuple[float, float],
    width: float,
    height: float,
    depth: float,
) -> None:
    verts, faces = buckets.setdefault(bucket, ([], []))
    cx, cy, cz = center
    ux, uz = u
    nx, nz = n
    hw, hh, hd = width * 0.5, height * 0.5, depth * 0.5
    runtime = []
    for su, sy, sn in (
        (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
    ):
        x = cx + ux * hw * su + nx * hd * sn
        z = cz + uz * hw * su + nz * hd * sn
        y = cy + hh * sy
        runtime.append(runtime_to_blender((x, y, z)))
    offset = len(verts)
    verts.extend(runtime)
    faces.extend(
        [
            (offset + 0, offset + 1, offset + 2, offset + 3),
            (offset + 4, offset + 7, offset + 6, offset + 5),
            (offset + 0, offset + 4, offset + 5, offset + 1),
            (offset + 1, offset + 5, offset + 6, offset + 2),
            (offset + 2, offset + 6, offset + 7, offset + 3),
            (offset + 4, offset + 0, offset + 3, offset + 7),
        ]
    )


def build_bucket_object(
    visual: bpy.types.Collection,
    name: str,
    data: tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]],
    mat: bpy.types.Material,
) -> bpy.types.Object | None:
    verts, faces = data
    if not verts:
        return None
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate(verbose=False)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    visual.objects.link(obj)
    obj.data.materials.append(mat)
    obj["authored_close_facade"] = True
    obj["source_geometry"] = "Hamburg LGV LoD2-DE 2026 wall planes"
    obj["photo_reference"] = "Poly Haven hansaplatz CC0; reference only, not mapped onto facade"
    return obj


def remove_previous_authored_layer() -> int:
    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith("hamburg_facade_authored_")]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    return len(doomed)


def main() -> None:
    cfg = parse_args()
    if not cfg.obj.is_file():
        raise RuntimeError(f"Hamburg LoD2 OBJ not found: {cfg.obj}")
    root = bpy.data.collections.get(cfg.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {cfg.collection}")
    visual = find_visual(root)
    removed = remove_previous_authored_layer()
    vertices, objects = load_obj(cfg.obj)

    candidates = []
    for object_name, faces in objects.items():
        if not object_name.endswith("_wall"):
            continue
        for face_index, face in enumerate(faces):
            points = [vertices[index] for index in face]
            segment = facade_segment(points)
            if segment is None or segment["distance"] > cfg.radius_m:
                continue
            # Reject tiny fragments and extreme roof/party-wall slivers.
            if segment["length"] < 4.2 or segment["height"] < 6.0:
                continue
            candidates.append((segment["distance"], object_name, face_index, segment))

    candidates.sort(key=lambda row: (row[0], -row[3]["length"]))
    selected = candidates[: cfg.max_facades]
    if not selected:
        raise RuntimeError(f"No close Hamburg LoD2 facade wall faces found within {cfg.radius_m:.1f}m")

    mats = {
        "glass_dark": material("hamburg_facade_glass_dark", (0.018, 0.026, 0.033, 1.0), 0.18, metallic=0.08),
        "glass_lit": material(
            "hamburg_facade_glass_lit", (0.22, 0.16, 0.08, 1.0), 0.28,
            emission=(1.0, 0.56, 0.20, 1.0), emission_strength=1.6,
        ),
        "frame": material("hamburg_facade_frame_dark", (0.055, 0.050, 0.045, 1.0), 0.34, metallic=0.18),
        "stone": material("hamburg_facade_stone_trim", (0.48, 0.43, 0.36, 1.0), 0.70),
        "plinth": material("hamburg_facade_plinth", (0.18, 0.17, 0.16, 1.0), 0.78),
        "shop": material(
            "hamburg_facade_shop_glass", (0.025, 0.032, 0.036, 1.0), 0.14,
            emission=(0.58, 0.32, 0.14, 1.0), emission_strength=0.42,
        ),
    }
    buckets: dict[str, tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]]] = {}
    window_count = 0
    shop_count = 0
    bay_count = 0

    for rank, (_, object_name, face_index, seg) in enumerate(selected):
        length = float(seg["length"])
        height = float(seg["height"])
        min_y = float(seg["min_y"])
        max_y = float(seg["max_y"])
        midx, midz = seg["mid"]
        ux, uz = seg["u"]
        nx, nz = seg["n"]
        seed = stable_int(f"{object_name}:{face_index}")

        # Ground-floor plinth and strong cornice make the flat LoD2 wall read as a facade.
        add_box_geometry(buckets, "plinth", (midx + nx * 0.045, min_y + 0.28, midz + nz * 0.045), (ux, uz), (nx, nz), max(1.0, length - 0.20), 0.56, 0.09)
        add_box_geometry(buckets, "stone", (midx + nx * 0.11, max_y - 0.22, midz + nz * 0.11), (ux, uz), (nx, nz), max(1.0, length - 0.12), 0.34, 0.22)

        # Storefronts: wide panes with structural mullions; no panorama image on the wall.
        ground_h = min(3.5, max(2.6, height * 0.17))
        shop_cols = max(1, min(8, int((length - 1.0) / 2.7)))
        usable = min(length - 0.8, shop_cols * 2.55)
        if usable > 1.8:
            spacing = usable / shop_cols
            start = -usable * 0.5 + spacing * 0.5
            for col in range(shop_cols):
                along = start + col * spacing
                cx = midx + ux * along + nx * 0.10
                cz = midz + uz * along + nz * 0.10
                add_box_geometry(buckets, "shop", (cx, min_y + ground_h * 0.54, cz), (ux, uz), (nx, nz), max(1.1, spacing - 0.18), ground_h * 0.78, 0.08)
                # Mullion at one side of each bay.
                mx = midx + ux * (along - spacing * 0.48) + nx * 0.18
                mz = midz + uz * (along - spacing * 0.48) + nz * 0.18
                add_box_geometry(buckets, "frame", (mx, min_y + ground_h * 0.54, mz), (ux, uz), (nx, nz), 0.07, ground_h * 0.82, 0.11)
                shop_count += 1
            # Storefront transom / canopy edge.
            add_box_geometry(buckets, "frame", (midx + nx * 0.22, min_y + ground_h + 0.10, midz + nz * 0.22), (ux, uz), (nx, nz), max(1.0, usable), 0.12, 0.24)

        upper_bottom = min_y + ground_h + 0.70
        upper_top = max_y - 0.80
        available = upper_top - upper_bottom
        if available < 2.0:
            continue
        floors = max(1, min(7, int(available / 2.75)))
        floor_step = available / floors
        window_h = min(1.75, max(1.30, floor_step * 0.60))
        cols = max(1, min(11, int((length - 0.9) / 2.15)))
        spacing = (length - 0.9) / cols
        window_w = min(1.35, max(0.88, spacing * 0.62))
        start = -((cols - 1) * spacing) * 0.5

        for floor in range(floors):
            cy = upper_bottom + (floor + 0.5) * floor_step
            # A restrained floor band gives the perimeter blocks visible horizontal relief.
            if floor > 0 and height >= 12.0:
                band_y = upper_bottom + floor * floor_step
                add_box_geometry(buckets, "stone", (midx + nx * 0.075, band_y, midz + nz * 0.075), (ux, uz), (nx, nz), max(1.0, length - 0.20), 0.11, 0.15)
            for col in range(cols):
                along = start + col * spacing
                cx = midx + ux * along
                cz = midz + uz * along
                lit = ((seed + floor * 17 + col * 29) % 7) in {0, 3}
                glass_bucket = "glass_lit" if lit else "glass_dark"
                # Dark inset panel, then 3D sill/lintel and side frames in front.
                add_box_geometry(buckets, glass_bucket, (cx + nx * 0.045, cy, cz + nz * 0.045), (ux, uz), (nx, nz), window_w, window_h, 0.06)
                frame_depth = 0.14
                frame_offset = 0.13
                for side in (-1, 1):
                    sx = cx + ux * (side * (window_w * 0.5 + 0.055)) + nx * frame_offset
                    sz = cz + uz * (side * (window_w * 0.5 + 0.055)) + nz * frame_offset
                    add_box_geometry(buckets, "frame", (sx, cy, sz), (ux, uz), (nx, nz), 0.085, window_h + 0.12, frame_depth)
                for vertical in (-1, 1):
                    fy = cy + vertical * (window_h * 0.5 + 0.055)
                    add_box_geometry(buckets, "stone" if vertical < 0 else "frame", (cx + nx * frame_offset, fy, cz + nz * frame_offset), (ux, uz), (nx, nz), window_w + 0.18, 0.10 if vertical > 0 else 0.14, frame_depth)
                # Central mullion for taller historic window proportions.
                if window_w > 1.05:
                    add_box_geometry(buckets, "frame", (cx + nx * 0.15, cy, cz + nz * 0.15), (ux, uz), (nx, nz), 0.055, window_h, 0.10)
                window_count += 1

        # Limited shallow projecting bay on a few large near facades, matching the real
        # St. Georg streetscape vocabulary without pretending LoD2 supplies window data.
        if rank < 6 and length >= 9.0 and height >= 15.0 and seed % 3 == 0:
            bay_w = min(3.2, length * 0.24)
            bay_h = max(5.0, upper_top - upper_bottom - 0.3)
            bay_y = upper_bottom + bay_h * 0.5
            add_box_geometry(buckets, "stone", (midx + nx * 0.46, bay_y, midz + nz * 0.46), (ux, uz), (nx, nz), bay_w, bay_h, 0.72)
            # Re-overlay a vertical dark glazing strip on the bay face.
            add_box_geometry(buckets, "glass_dark", (midx + nx * 0.86, bay_y, midz + nz * 0.86), (ux, uz), (nx, nz), bay_w * 0.58, bay_h * 0.82, 0.06)
            bay_count += 1

    created_objects = 0
    for bucket, data in buckets.items():
        obj = build_bucket_object(visual, f"hamburg_facade_authored_{bucket}", data, mats[bucket])
        if obj is not None:
            created_objects += 1

    root["hamburg_facade_authored_layer"] = True
    root["hamburg_facade_authored_radius_m"] = cfg.radius_m
    root["hamburg_facade_authored_face_count"] = len(selected)
    root["hamburg_facade_authored_window_count"] = window_count
    root["hamburg_facade_authored_shopfront_count"] = shop_count
    root["hamburg_facade_authored_bay_count"] = bay_count
    root["hamburg_facade_authored_source"] = "Hamburg LGV LoD2-DE 2026 + Poly Haven reference inspection"
    root["hamburg_facade_panorama_projection"] = False
    root["hamburg_facade_previous_authored_removed"] = removed

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg authored facade layer: "
        f"facades={len(selected)} windows={window_count} shopfronts={shop_count} "
        f"bays={bay_count} mesh_objects={created_objects} removed_previous={removed}"
    )


if __name__ == "__main__":
    main()
