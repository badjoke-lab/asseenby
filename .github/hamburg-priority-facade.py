#!/usr/bin/env python3
"""Prioritize Hamburg LoD2 facade authoring for the actual initial camera view.

The underlying authoring implementation remains scripts/blender/author_hamburg_lod2_facades.py.
This wrapper only changes candidate ranking. It keeps real Hamburg LoD2 wall planes,
never substitutes geometry, and never maps the Hansaplatz panorama onto walls.
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


def camera_priority_segment(points):
    seg = original_facade_segment(points)
    if seg is None:
        return None

    actual_distance = float(seg["distance"])
    midx, midz = seg["mid"]
    if actual_distance < 0.001:
        seg["actual_distance"] = actual_distance
        seg["view_angle_deg"] = 0.0
        seg["priority_score"] = 0.0
        return seg

    # Runtime initial human observer looks down -Z at yaw=0. Give walls that
    # actually occupy that forward view precedence over merely-nearest side/rear walls.
    forward_alignment = max(-1.0, min(1.0, -float(midz) / actual_distance))
    view_angle_deg = math.degrees(math.acos(forward_alignment))
    projected_area = (float(seg["length"]) * float(seg["height"])) / max(actual_distance * actual_distance, 25.0)

    angle_penalty = max(0.0, view_angle_deg - 22.0) * 1.55
    area_bonus = min(24.0, projected_area * 62.0)
    rear_penalty = 140.0 if float(midz) >= 0.0 else 0.0
    raw_priority = max(0.0, actual_distance + angle_penalty + rear_penalty - area_bonus)

    seg["actual_distance"] = actual_distance
    seg["view_angle_deg"] = view_angle_deg
    seg["projected_area_proxy"] = projected_area
    seg["priority_score"] = raw_priority

    # The base pass unfortunately uses `distance` for both radius admission and sorting.
    # Preserve all walls whose *real* distance already passed the intended 95 m domain by
    # compressing ranking into that domain instead of allowing ranking penalties to exceed
    # the radius. Front/on-screen walls still sort first; side/rear walls remain fallbacks
    # that can fill the 40-face budget rather than disappearing from the candidate set.
    seg["distance"] = min(94.90, raw_priority)
    return seg


base.facade_segment = camera_priority_segment
base.main()

root = bpy.data.collections.get("C0")
if root is not None:
    root["hamburg_facade_selection_basis"] = "initial-camera-visible wall priority: yaw 0 / forward -Z; 95m candidate domain retained"
    root["hamburg_facade_selection_priority_version"] = 3
    root["hamburg_facade_selection_panorama_projection"] = False
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
