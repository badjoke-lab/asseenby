#!/usr/bin/env python3
"""Create a lightweight terrain-continuity underlay for Hansaplatz C0.

The official Hamburg LoD2 subset contains building ground surfaces with real local
foundation elevations, while the legacy authored plaza/road only covers the first
~60 m from the observer.  Hiding legacy geometry therefore exposed the night
background as black voids between the plaza and buildings.

This pass creates a coarse triangulated underlay.  Heights are interpolated from
LoD2 building-ground centroids and blended from the existing flat near-plaza anchor.
It is explicitly a continuity surface, not surveyed terrain and not a replacement
for future authoritative street/terrain data.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
from pathlib import Path
import sys

import bpy

BASE_PATH = Path(__file__).with_name("author_hamburg_lod2_facades.py")
spec = importlib.util.spec_from_file_location("hamburg_ground_helpers", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load Hamburg helpers: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--obj", required=True, type=Path)
    parser.add_argument("--grid-step-m", type=float, default=10.0)
    parser.add_argument("--margin-m", type=float, default=8.0)
    return parser.parse_args(argv)


def smoothstep01(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def distance_outside_rect(x: float, z: float, xmin: float, xmax: float, zmin: float, zmax: float) -> float:
    dx = max(xmin - x, 0.0, x - xmax)
    dz = max(zmin - z, 0.0, z - zmax)
    return math.hypot(dx, dz)


def idw_height(x: float, z: float, samples: list[tuple[float, float, float]]) -> float:
    nearest = sorted(samples, key=lambda item: (item[0] - x) ** 2 + (item[2] - z) ** 2)[:10]
    weighted = 0.0
    total = 0.0
    for sx, sy, sz in nearest:
        d2 = (sx - x) ** 2 + (sz - z) ** 2
        if d2 < 0.04:
            return sy
        weight = 1.0 / max(4.0, d2)
        weighted += sy * weight
        total += weight
    return weighted / total if total > 0.0 else 0.0


def main() -> None:
    cfg = parse_args()
    if not cfg.obj.is_file():
        raise RuntimeError(f"Hamburg LoD2 OBJ not found: {cfg.obj}")
    root = bpy.data.collections.get(cfg.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {cfg.collection}")
    visual = base.find_visual(root)

    doomed = [obj for obj in list(bpy.data.objects) if obj.name.startswith("hamburg_ground_continuity_")]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)

    vertices, objects = base.load_obj(cfg.obj)
    samples: list[tuple[float, float, float]] = []
    horizontal_points: list[tuple[float, float]] = []
    for object_name, faces in objects.items():
        if not object_name.endswith("_ground"):
            continue
        for face in faces:
            points = [vertices[index] for index in face]
            if not points:
                continue
            sx = sum(p[0] for p in points) / len(points)
            sy = sum(p[1] for p in points) / len(points)
            sz = sum(p[2] for p in points) / len(points)
            samples.append((sx, sy, sz))
            horizontal_points.extend((p[0], p[2]) for p in points)

    if len(samples) < 8 or not horizontal_points:
        raise RuntimeError(f"Insufficient Hamburg LoD2 ground samples: {len(samples)}")

    # Existing visible plaza/paving in the GLB covers roughly x=-30..30,
    # z=-58..2 at observer height. Keep the continuity mesh just below it and
    # blend gradually toward the LoD2 foundation elevations outside this area.
    plaza_rect = (-32.0, 32.0, -62.0, 5.0)
    anchor_samples = [
        (-30.0, 0.0, -58.0), (0.0, 0.0, -58.0), (30.0, 0.0, -58.0),
        (-30.0, 0.0, -30.0), (0.0, 0.0, -30.0), (30.0, 0.0, -30.0),
        (-30.0, 0.0, 0.0), (0.0, 0.0, 0.0), (30.0, 0.0, 0.0),
    ]
    all_samples = samples + anchor_samples

    xs_raw = [p[0] for p in horizontal_points] + [0.0]
    zs_raw = [p[1] for p in horizontal_points] + [0.0]
    step = max(6.0, min(16.0, cfg.grid_step_m))
    xmin = math.floor((min(xs_raw) - cfg.margin_m) / step) * step
    xmax = math.ceil((max(xs_raw) + cfg.margin_m) / step) * step
    zmin = math.floor((min(zs_raw) - cfg.margin_m) / step) * step
    zmax = math.ceil((max(zs_raw) + cfg.margin_m) / step) * step

    nx = int(round((xmax - xmin) / step)) + 1
    nz = int(round((zmax - zmin) / step)) + 1
    if nx * nz > 2600:
        raise RuntimeError(f"Ground continuity grid unexpectedly large: {nx}x{nz}")

    mesh_vertices: list[tuple[float, float, float]] = []
    min_height = float("inf")
    max_height = float("-inf")
    for iz in range(nz):
        runtime_z = zmin + iz * step
        for ix in range(nx):
            runtime_x = xmin + ix * step
            raw_h = idw_height(runtime_x, runtime_z, all_samples)
            outside = distance_outside_rect(runtime_x, runtime_z, *plaza_rect)
            # Spread the transition over ~55m to avoid a podium-like step between
            # observer-level paving and foundations that sit a few metres higher.
            blend = smoothstep01(outside / 55.0)
            runtime_y = raw_h * blend - 0.10
            # Continuity only: stay within the observed foundation-height envelope.
            sample_min = min(s[1] for s in samples)
            sample_max = max(s[1] for s in samples)
            runtime_y = max(-0.18, min(sample_max - 0.05, max(sample_min - 0.45, runtime_y)))
            min_height = min(min_height, runtime_y)
            max_height = max(max_height, runtime_y)
            mesh_vertices.append(base.runtime_to_blender((runtime_x, runtime_y, runtime_z)))

    faces: list[tuple[int, int, int]] = []
    for iz in range(nz - 1):
        for ix in range(nx - 1):
            a = iz * nx + ix
            b = a + 1
            c = a + nx
            d = c + 1
            faces.append((a, c, b))
            faces.append((b, c, d))

    mesh = bpy.data.meshes.new("hamburg_ground_continuity_mesh")
    mesh.from_pydata(mesh_vertices, [], faces)
    mesh.validate(verbose=False)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new("hamburg_ground_continuity_underlay", mesh)
    visual.objects.link(obj)
    mat = base.material("hamburg_ground_continuity_dark_paving", (0.105, 0.100, 0.092, 1.0), 0.90)
    obj.data.materials.append(mat)
    obj["ground_continuity"] = True
    obj["source_basis"] = "IDW interpolation from Hamburg LGV LoD2 building ground surfaces plus near-plaza observer anchors"
    obj["terrain_claim"] = "visual continuity underlay only; not authoritative surveyed terrain"

    root["hamburg_ground_continuity"] = True
    root["hamburg_ground_continuity_version"] = 1
    root["hamburg_ground_continuity_sample_count"] = len(samples)
    root["hamburg_ground_continuity_vertex_count"] = len(mesh_vertices)
    root["hamburg_ground_continuity_triangle_count"] = len(faces)
    root["hamburg_ground_continuity_grid_step_m"] = step
    root["hamburg_ground_continuity_runtime_bounds"] = f"x={xmin:.1f}..{xmax:.1f};z={zmin:.1f}..{zmax:.1f}"
    root["hamburg_ground_continuity_height_range_m"] = f"{min_height:.3f}..{max_height:.3f}"
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg ground continuity: "
        f"samples={len(samples)} grid={nx}x{nz} vertices={len(mesh_vertices)} triangles={len(faces)} "
        f"runtime_bounds=x[{xmin:.1f},{xmax:.1f}] z[{zmin:.1f},{zmax:.1f}] "
        f"height=[{min_height:.3f},{max_height:.3f}] removed={len(doomed)}"
    )


if __name__ == "__main__":
    main()
