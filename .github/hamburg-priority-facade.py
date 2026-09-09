#!/usr/bin/env python3
"""Prioritize and recover Hamburg LoD2 facade authoring for the views users see.

The underlying authoring implementation remains scripts/blender/author_hamburg_lod2_facades.py.
This wrapper keeps official Hamburg LoD2 as the macro source of truth, ranks real wall
planes for the three browser-proof views, and conservatively joins only contiguous,
nearly-collinear narrow LoD2 wall fragments into an authoring guide. It never substitutes
building geometry and never maps the Hansaplatz panorama onto walls.
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
original_load_obj = base.load_obj

# Cover the initial forward view and the two large turn directions exercised by the
# browser proof. Runtime forward(yaw) = (-sin(yaw), -cos(yaw)) in X/Z.
VIEW_YAWS = (0.0, -1.05, 1.05)
INITIAL_FORWARD_GUARANTEE_DEG = 22.0
FRAGMENT_VIEW_DEG = 28.0
FRAGMENT_MAX_WIDTH_M = 4.2
FRAGMENT_MIN_WIDTH_M = 0.35
FRAGMENT_MAX_ORIENTATION_DELTA_DEG = 2.5
FRAGMENT_MAX_ENDPOINT_GAP_M = 0.65
FRAGMENT_MAX_PLANE_SPREAD_M = 0.28
FRAGMENT_MAX_COMBINED_WIDTH_M = 20.0
RECOVERED_FRAGMENT_GROUPS = 0
RECOVERED_FRAGMENT_FACES = 0


def expanded_parse_args():
    cfg = original_parse_args()
    cfg.max_facades = max(int(cfg.max_facades), 64)
    return cfg


def _best_horizontal_segment(points):
    horizontal = base.unique_horizontal(points)
    if len(horizontal) < 2:
        return None
    best = None
    best_len = 0.0
    for index, a in enumerate(horizontal):
        for b in horizontal[index + 1 :]:
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            if length > best_len:
                best = (a, b)
                best_len = length
    if best is None:
        return None
    a, b = best
    ux = (b[0] - a[0]) / best_len
    uz = (b[1] - a[1]) / best_len
    return a, b, best_len, ux, uz


def _angle_delta_mod_pi(a, b):
    delta = abs(a - b) % math.pi
    return min(delta, math.pi - delta)


def _best_view_angle_deg(midx, midz):
    distance = math.hypot(midx, midz)
    if distance < 0.001:
        return 0.0
    dx, dz = midx / distance, midz / distance
    best = -1.0
    for yaw in VIEW_YAWS:
        fx, fz = -math.sin(yaw), -math.cos(yaw)
        best = max(best, dx * fx + dz * fz)
    return math.degrees(math.acos(max(-1.0, min(1.0, best))))


def _fragment_descriptor(points, face_index):
    if len(points) < 3:
        return None
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    height = max_y - min_y
    if height < 6.0:
        return None
    segment = _best_horizontal_segment(points)
    if segment is None:
        return None
    a, b, length, ux, uz = segment
    # Only recover fragments that the normal facade pass rejects for being narrow.
    if length < FRAGMENT_MIN_WIDTH_M or length >= FRAGMENT_MAX_WIDTH_M:
        return None
    midx, midz = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
    distance = math.hypot(midx, midz)
    if distance > 95.0 or _best_view_angle_deg(midx, midz) > FRAGMENT_VIEW_DEG:
        return None
    orientation = math.atan2(uz, ux) % math.pi
    return {
        "face_index": face_index,
        "a": a,
        "b": b,
        "u": (ux, uz),
        "orientation": orientation,
        "length": length,
        "min_y": min_y,
        "max_y": max_y,
        "height": height,
        "mid": (midx, midz),
        "distance": distance,
    }


def _endpoint_gap(left, right):
    return min(
        math.hypot(a[0] - b[0], a[1] - b[1])
        for a in (left["a"], left["b"])
        for b in (right["a"], right["b"])
    )


def recover_fragmented_wall_spans(path):
    """Append synthetic *authoring guides* for strict coplanar chains of narrow faces.

    The returned geometry still contains every original official OBJ face unchanged.
    A recovered guide is only a four-point span used by the facade-detail pass. Its end
    points come from actual Hamburg LoD2 fragment endpoints, and chains are accepted only
    when height, orientation, endpoint continuity and coplanarity all agree tightly.
    """
    global RECOVERED_FRAGMENT_GROUPS, RECOVERED_FRAGMENT_FACES
    vertices, objects = original_load_obj(path)
    recovered_groups = 0
    recovered_faces = 0

    for object_name, faces in objects.items():
        if not object_name.endswith("_wall"):
            continue
        fragments = []
        for face_index, face in enumerate(list(faces)):
            points = [vertices[index] for index in face]
            # Do not duplicate an already-valid facade candidate.
            if original_facade_segment(points) is not None:
                continue
            descriptor = _fragment_descriptor(points, face_index)
            if descriptor is not None:
                fragments.append(descriptor)
        if len(fragments) < 2:
            continue

        parent = list(range(len(fragments)))

        def find(index):
            while parent[index] != index:
                parent[index] = parent[parent[index]]
                index = parent[index]
            return index

        def union(left, right):
            root_left, root_right = find(left), find(right)
            if root_left != root_right:
                parent[root_right] = root_left

        orientation_limit = math.radians(FRAGMENT_MAX_ORIENTATION_DELTA_DEG)
        for i, left in enumerate(fragments):
            for j in range(i + 1, len(fragments)):
                right = fragments[j]
                if abs(left["min_y"] - right["min_y"]) > 0.25:
                    continue
                if abs(left["max_y"] - right["max_y"]) > 0.25:
                    continue
                if _angle_delta_mod_pi(left["orientation"], right["orientation"]) > orientation_limit:
                    continue
                if _endpoint_gap(left, right) > FRAGMENT_MAX_ENDPOINT_GAP_M:
                    continue
                union(i, j)

        components = {}
        for index, fragment in enumerate(fragments):
            components.setdefault(find(index), []).append(fragment)

        for component in components.values():
            if len(component) < 2:
                continue
            ref_ux, ref_uz = component[0]["u"]
            aligned = []
            total_weight = 0.0
            for fragment in component:
                ux, uz = fragment["u"]
                if ux * ref_ux + uz * ref_uz < 0:
                    ux, uz = -ux, -uz
                weight = fragment["length"]
                aligned.append((ux, uz, weight))
                total_weight += weight
            ux = sum(item[0] * item[2] for item in aligned) / max(total_weight, 0.001)
            uz = sum(item[1] * item[2] for item in aligned) / max(total_weight, 0.001)
            norm = math.hypot(ux, uz)
            if norm < 0.001:
                continue
            ux, uz = ux / norm, uz / norm
            nx, nz = -uz, ux

            endpoints = [point for fragment in component for point in (fragment["a"], fragment["b"])]
            normal_values = [point[0] * nx + point[1] * nz for point in endpoints]
            if max(normal_values) - min(normal_values) > FRAGMENT_MAX_PLANE_SPREAD_M:
                continue
            projections = [(point[0] * ux + point[1] * uz, point) for point in endpoints]
            projections.sort(key=lambda item: item[0])
            a = projections[0][1]
            b = projections[-1][1]
            combined_length = math.hypot(b[0] - a[0], b[1] - a[1])
            if combined_length < 4.2 or combined_length > FRAGMENT_MAX_COMBINED_WIDTH_M:
                continue
            midx, midz = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
            if math.hypot(midx, midz) > 95.0 or _best_view_angle_deg(midx, midz) > FRAGMENT_VIEW_DEG:
                continue

            min_y = sum(fragment["min_y"] for fragment in component) / len(component)
            max_y = sum(fragment["max_y"] for fragment in component) / len(component)
            start = len(vertices)
            vertices.extend(
                [
                    (a[0], min_y, a[1]),
                    (a[0], max_y, a[1]),
                    (b[0], max_y, b[1]),
                    (b[0], min_y, b[1]),
                ]
            )
            faces.append([start, start + 1, start + 2, start + 3])
            recovered_groups += 1
            recovered_faces += len(component)
            print(
                "RECOVERED_FRAGMENTED_FACADE",
                object_name,
                "source_faces", [fragment["face_index"] for fragment in component],
                "combined_width", round(combined_length, 3),
                "height", round(max_y - min_y, 3),
                "distance", round(math.hypot(midx, midz), 3),
                "best_view_angle", round(_best_view_angle_deg(midx, midz), 3),
            )

    RECOVERED_FRAGMENT_GROUPS = recovered_groups
    RECOVERED_FRAGMENT_FACES = recovered_faces
    print("RECOVERED_FRAGMENT_GROUP_COUNT", recovered_groups)
    print("RECOVERED_FRAGMENT_SOURCE_FACE_COUNT", recovered_faces)
    return vertices, objects


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

    angle_penalty = max(0.0, view_angle_deg - 30.0) * 1.15
    area_bonus = min(28.0, projected_area * 70.0)
    outside_view_penalty = 55.0 if best_alignment < 0.10 else 0.0
    raw_priority = max(0.0, actual_distance + angle_penalty + outside_view_penalty - area_bonus)

    initial_forward_guaranteed = initial_forward_angle_deg <= INITIAL_FORWARD_GUARANTEE_DEG
    if initial_forward_guaranteed:
        raw_priority = max(0.0, raw_priority - 70.0)

    seg["actual_distance"] = actual_distance
    seg["view_angle_deg"] = view_angle_deg
    seg["initial_forward_angle_deg"] = initial_forward_angle_deg
    seg["initial_forward_guaranteed"] = initial_forward_guaranteed
    seg["projected_area_proxy"] = projected_area
    seg["priority_score"] = raw_priority
    # Preserve the real 95 m candidate domain while using distance as the base sort key.
    seg["distance"] = min(94.90, raw_priority)
    return seg


base.parse_args = expanded_parse_args
base.load_obj = recover_fragmented_wall_spans
base.facade_segment = camera_priority_segment
base.main()

root = bpy.data.collections.get("C0")
if root is not None:
    root["hamburg_facade_selection_basis"] = "multi-view wall priority; initial +/-22deg valid walls guaranteed; strict contiguous coplanar narrow-fragment recovery; 95m candidate domain; facade budget >=64"
    root["hamburg_facade_selection_priority_version"] = 5
    root["hamburg_facade_selection_view_yaws"] = "0,-1.05,1.05"
    root["hamburg_facade_selection_initial_forward_guarantee_deg"] = INITIAL_FORWARD_GUARANTEE_DEG
    root["hamburg_facade_selection_fragment_recovery"] = True
    root["hamburg_facade_selection_fragment_group_count"] = RECOVERED_FRAGMENT_GROUPS
    root["hamburg_facade_selection_fragment_source_face_count"] = RECOVERED_FRAGMENT_FACES
    root["hamburg_facade_selection_fragment_orientation_delta_deg"] = FRAGMENT_MAX_ORIENTATION_DELTA_DEG
    root["hamburg_facade_selection_fragment_endpoint_gap_m"] = FRAGMENT_MAX_ENDPOINT_GAP_M
    root["hamburg_facade_selection_fragment_plane_spread_m"] = FRAGMENT_MAX_PLANE_SPREAD_M
    root["hamburg_facade_selection_min_budget"] = 64
    root["hamburg_facade_selection_panorama_projection"] = False
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
