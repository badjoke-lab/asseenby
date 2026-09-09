#!/usr/bin/env python3
"""Prioritize Hamburg LoD2 facade authoring for the camera views users actually see.

The underlying authoring implementation remains scripts/blender/author_hamburg_lod2_facades.py.
This wrapper changes candidate ranking and raises the nearfield facade budget. It keeps
real Hamburg LoD2 wall planes, never substitutes geometry, and never maps the Hansaplatz
panorama onto walls.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import bpy

BASE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "blender" / "author_hamburg_lod2_facades.py"
spec = importlib.util.spec_from_file_location("hamburg_lod2_facade_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load facade authoring base: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

original_facade_segment = base.facade_segment
original_parse_args = base.parse_args

# Cover the initial forward view and the two large turn directions exercised by the
# browser proof. The runtime's yaw=0 forward vector is (0, -1) in X/Z.
VIEW_YAWS = (0.0, -1.05, 1.05)
INITIAL_FORWARD_GUARANTEE_DEG = 22.0


def expanded_parse_args():
    cfg = original_parse_args()
    # The authored layer is bucketed into six mesh/material groups, so increasing the
    # selected wall-face budget does not linearly increase draw calls. Keep enough real
    # nearfield walls to prevent a turn from revealing giant blank LoD2 slabs.
    cfg.max_facades = max(int(cfg.max_facades), 64)
    return cfg


def camera_priority_segment(points):
    seg = original_facade_segment(points)
    if seg is None:
        return None

    actual_distance = float(seg["distance"])
    midx, midz = seg["mid"]
    if actual_distance < 0.001:
        seg["actual_distance"] = actual_distance
        seg["view_angle_deg"] = 0.0
        seg["initial_forward_angle_deg"] = 0.0
        seg["priority_score"] = 0.0
        return seg

    direction_x = float(midx) / actual_distance
    direction_z = float(midz) / actual_distance

    # Runtime movement establishes forward(yaw) = (-sin(yaw), -cos(yaw)). Rank each
    # wall by its best alignment to forward, left-turn or right-turn inspection views.
    alignments = []
    for yaw in VIEW_YAWS:
        forward_x = -math.sin(yaw)
        forward_z = -math.cos(yaw)
        alignments.append(direction_x * forward_x + direction_z * forward_z)
    best_alignment = max(-1.0, min(1.0, max(alignments)))
    view_angle_deg = math.degrees(math.acos(best_alignment))

    initial_forward_alignment = max(-1.0, min(1.0, -direction_z))
    initial_forward_angle_deg = math.degrees(math.acos(initial_forward_alignment))

    projected_area = (float(seg["length"]) * float(seg["height"])) / max(actual_distance * actual_distance, 25.0)

    # Prefer walls visible in any of the three main views, especially large close planes.
    # Walls outside all three view cones remain valid fallbacks rather than being deleted.
    angle_penalty = max(0.0, view_angle_deg - 30.0) * 1.15
    area_bonus = min(28.0, projected_area * 70.0)
    outside_view_penalty = 55.0 if best_alignment < 0.10 else 0.0
    raw_priority = max(0.0, actual_distance + angle_penalty + outside_view_penalty - area_bonus)

    # The browser proof showed that distance-first ranking could still drop a very large
    # wall almost exactly on the initial optical axis (e.g. a 15.8m x 21.2m wall at
    # ~90.5m ranked 84th). Any valid facade in the initial +/-22 degree cone is therefore
    # guaranteed a strong ranking bonus. This does not fabricate geometry; it only makes
    # existing official Hamburg wall planes receive the authored depth layer.
    initial_forward_guaranteed = initial_forward_angle_deg <= INITIAL_FORWARD_GUARANTEE_DEG
    if initial_forward_guaranteed:
        raw_priority = max(0.0, raw_priority - 70.0)

    seg["actual_distance"] = actual_distance
    seg["view_angle_deg"] = view_angle_deg
    seg["initial_forward_angle_deg"] = initial_forward_angle_deg
    seg["initial_forward_guaranteed"] = initial_forward_guaranteed
    seg["projected_area_proxy"] = projected_area
    seg["priority_score"] = raw_priority

    # The base pass reuses `distance` for both radius admission and sorting. Preserve the
    # entire real 95 m candidate domain by compressing only the ranking value below 95 m.
    seg["distance"] = min(94.90, raw_priority)
    return seg


base.parse_args = expanded_parse_args
base.facade_segment = camera_priority_segment
base.main()

root = bpy.data.collections.get("C0")
if root is not None:
    root["hamburg_facade_selection_basis"] = "multi-view wall priority: yaw 0,+/-1.05 rad; initial +/-22deg valid walls guaranteed; 95m candidate domain retained; facade budget >=64"
    root["hamburg_facade_selection_priority_version"] = 4
    root["hamburg_facade_selection_view_yaws"] = "0,-1.05,1.05"
    root["hamburg_facade_selection_initial_forward_guarantee_deg"] = INITIAL_FORWARD_GUARANTEE_DEG
    root["hamburg_facade_selection_min_budget"] = 64
    root["hamburg_facade_selection_panorama_projection"] = False
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
