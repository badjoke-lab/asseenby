#!/usr/bin/env python3
"""Author v8 nearfield facades with deterministic per-building grammar.

The Hamburg LGV LoD2 wall planes remain the geometric source of truth.  This pass
adds only authored depth cues on those planes; it never maps the Poly Haven
panorama onto a facade and it does not claim exact window registration.

v8 addresses the browser-proof failure mode where every building inherited nearly
identical floor, bay, window and shopfront proportions.  A deterministic grammar is
chosen per *building* rather than per wall face, so adjacent faces keep a coherent
architectural rhythm while different buildings visibly differ.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
from pathlib import Path
import sys

import bpy

BASE_PATH = Path(__file__).with_name("author_hamburg_lod2_facades.py")
spec = importlib.util.spec_from_file_location("hamburg_facade_base_v8", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load facade helpers: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

VIEW_YAWS = (0.0, -1.05, 1.05)
INITIAL_FORWARD_GUARANTEE_DEG = 24.0
MAX_PER_BUILDING = 4


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="C0")
    parser.add_argument("--obj", required=True, type=Path)
    parser.add_argument("--radius-m", type=float, default=98.0)
    parser.add_argument("--max-facades", type=int, default=64)
    return parser.parse_args(argv)


def building_key(object_name: str) -> str:
    return object_name[:-5] if object_name.endswith("_wall") else object_name


def metrics(seg):
    distance = float(seg["distance"])
    midx, midz = seg["mid"]
    if distance < 0.001:
        return 0.0, 0.0, 1.0, 999.0
    dx, dz = float(midx) / distance, float(midz) / distance
    aligns = [dx * (-math.sin(yaw)) + dz * (-math.cos(yaw)) for yaw in VIEW_YAWS]
    best = max(-1.0, min(1.0, max(aligns)))
    view_angle = math.degrees(math.acos(best))
    initial = max(-1.0, min(1.0, -dz))
    initial_angle = math.degrees(math.acos(initial))
    projected = (float(seg["length"]) * float(seg["height"])) / max(distance * distance, 25.0)
    score = distance + max(0.0, view_angle - 27.0) * 1.25 - min(34.0, projected * 82.0)
    if best < 0.10:
        score += 58.0
    if initial_angle <= INITIAL_FORWARD_GUARANTEE_DEG:
        score -= 78.0
    return view_angle, initial_angle, projected, max(0.0, score)


def select_facades(vertices, objects, radius_m: float, max_facades: int):
    candidates = []
    for object_name, faces in objects.items():
        if not object_name.endswith("_wall"):
            continue
        for face_index, face in enumerate(faces):
            points = [vertices[index] for index in face]
            seg = base.facade_segment(points)
            if seg is None:
                continue
            if float(seg["distance"]) > radius_m or float(seg["length"]) < 4.2 or float(seg["height"]) < 6.0:
                continue
            view_angle, initial_angle, projected, score = metrics(seg)
            candidates.append((score, object_name, face_index, seg, view_angle, initial_angle, projected))

    candidates.sort(key=lambda row: (row[0], -row[6], row[4]))
    selected = []
    selected_ids = set()
    per_building: dict[str, int] = {}

    # First guarantee the initial user's forward cone, then fill the turned views.
    for forward_only in (True, False):
        for row in candidates:
            _, object_name, face_index, _, _, initial_angle, _ = row
            if forward_only and initial_angle > INITIAL_FORWARD_GUARANTEE_DEG:
                continue
            key = (object_name, face_index)
            if key in selected_ids:
                continue
            bkey = building_key(object_name)
            limit = MAX_PER_BUILDING + (1 if forward_only else 0)
            if per_building.get(bkey, 0) >= limit:
                continue
            selected.append(row)
            selected_ids.add(key)
            per_building[bkey] = per_building.get(bkey, 0) + 1
            if len(selected) >= max_facades:
                return selected
    return selected


def add_frame(buckets, trim_bucket, frame_bucket, cx, cy, cz, u, n, w, h, depth_scale=1.0):
    ux, uz = u
    nx, nz = n
    side_w = max(0.07, min(0.12, w * 0.075))
    front = 0.15 * depth_scale
    depth = 0.13 * depth_scale
    for side in (-1.0, 1.0):
        sx = cx + ux * side * (w * 0.5 + side_w * 0.45) + nx * front
        sz = cz + uz * side * (w * 0.5 + side_w * 0.45) + nz * front
        base.add_box_geometry(buckets, frame_bucket, (sx, cy, sz), u, n, side_w, h + 0.14, depth)
    base.add_box_geometry(buckets, frame_bucket, (cx + nx * front, cy + h * 0.5 + 0.055, cz + nz * front), u, n, w + 0.18, 0.10, depth)
    base.add_box_geometry(buckets, trim_bucket, (cx + nx * (front + 0.02), cy - h * 0.5 - 0.075, cz + nz * (front + 0.02)), u, n, w + 0.24, 0.14, depth + 0.04)


def main() -> None:
    cfg = parse_args()
    if not cfg.obj.is_file():
        raise RuntimeError(f"Hamburg LoD2 OBJ not found: {cfg.obj}")
    root = bpy.data.collections.get(cfg.collection)
    if root is None:
        raise RuntimeError(f"Missing collection: {cfg.collection}")
    visual = base.find_visual(root)
    removed = base.remove_previous_authored_layer()
    vertices, objects = base.load_obj(cfg.obj)
    selected = select_facades(vertices, objects, cfg.radius_m, cfg.max_facades)
    if not selected:
        raise RuntimeError("No Hamburg nearfield facade faces selected for v8 authoring")

    mats = {
        "glass_dark": base.material("hamburg_v8_glass_dark", (0.016, 0.023, 0.030, 1.0), 0.20, metallic=0.06),
        "glass_cool": base.material("hamburg_v8_glass_cool", (0.055, 0.078, 0.092, 1.0), 0.24, metallic=0.04),
        "glass_lit": base.material("hamburg_v8_glass_lit", (0.22, 0.15, 0.075, 1.0), 0.30, emission=(1.0, 0.54, 0.18, 1.0), emission_strength=1.45),
        "frame": base.material("hamburg_v8_frame_dark", (0.045, 0.043, 0.040, 1.0), 0.38, metallic=0.12),
        "shadow": base.material("hamburg_v8_recess_shadow", (0.018, 0.017, 0.016, 1.0), 0.88),
        "plinth": base.material("hamburg_v8_plinth", (0.16, 0.15, 0.14, 1.0), 0.82),
        "shop_dark": base.material("hamburg_v8_shop_dark", (0.025, 0.033, 0.038, 1.0), 0.18, metallic=0.04),
        "shop_lit": base.material("hamburg_v8_shop_lit", (0.12, 0.075, 0.035, 1.0), 0.26, emission=(0.72, 0.36, 0.12, 1.0), emission_strength=0.72),
        "trim_0": base.material("hamburg_v8_trim_sandstone", (0.42, 0.37, 0.31, 1.0), 0.76),
        "trim_1": base.material("hamburg_v8_trim_limestone", (0.54, 0.51, 0.45, 1.0), 0.72),
        "trim_2": base.material("hamburg_v8_trim_greige", (0.35, 0.34, 0.32, 1.0), 0.78),
        "trim_3": base.material("hamburg_v8_trim_ochre", (0.43, 0.32, 0.23, 1.0), 0.80),
    }
    buckets = {}
    window_count = 0
    shop_count = 0
    portal_count = 0
    pilaster_count = 0
    bay_count = 0
    grammar_seen = set()

    floor_targets = (2.72, 3.05, 3.28, 2.90, 3.38)
    bay_targets = (2.05, 2.55, 2.90, 2.25, 3.05)
    width_ratios = (0.56, 0.70, 0.62, 0.50, 0.77)
    height_ratios = (0.68, 0.54, 0.72, 0.62, 0.50)
    group_sizes = (2, 3, 2, 4, 3)

    for rank, (_, object_name, face_index, seg, _, initial_angle, _) in enumerate(selected):
        length = float(seg["length"])
        height = float(seg["height"])
        min_y = float(seg["min_y"])
        max_y = float(seg["max_y"])
        midx, midz = seg["mid"]
        u = seg["u"]
        n = seg["n"]
        ux, uz = u
        nx, nz = n
        bkey = building_key(object_name)
        bseed = base.stable_int(bkey)
        fseed = base.stable_int(f"{object_name}:{face_index}")
        grammar = bseed % 5
        grammar_seen.add(grammar)
        trim_bucket = f"trim_{bseed % 4}"

        # Per-building base/cornice proportions, with corner piers that visually
        # terminate each wall instead of leaving an unbounded rectangular sheet.
        ground_h = min(3.75, 2.75 + ((bseed >> 3) % 6) * 0.16)
        base.add_box_geometry(buckets, "plinth", (midx + nx * 0.055, min_y + 0.30, midz + nz * 0.055), u, n, max(1.0, length - 0.18), 0.60, 0.11)
        cornice_depth = 0.20 + (grammar % 3) * 0.045
        base.add_box_geometry(buckets, trim_bucket, (midx + nx * 0.12, max_y - 0.24, midz + nz * 0.12), u, n, max(1.0, length - 0.10), 0.38, cornice_depth)
        corner_w = 0.15 + (grammar % 2) * 0.05
        corner_h = max(1.5, height - 1.15)
        for side in (-1.0, 1.0):
            along = side * max(0.0, length * 0.5 - corner_w * 0.6)
            cx = midx + ux * along + nx * 0.13
            cz = midz + uz * along + nz * 0.13
            base.add_box_geometry(buckets, trim_bucket, (cx, min_y + 0.58 + corner_h * 0.5, cz), u, n, corner_w, corner_h, 0.18)
            pilaster_count += 1

        # Ground-floor grammar: mixed commercial, residential portals, or a hybrid.
        ground_mode = bseed % 4
        margin = min(1.25, max(0.55, length * (0.055 + grammar * 0.004)))
        usable_ground = max(1.0, length - 2.0 * margin)
        target_ground_bay = 2.25 + ((bseed >> 6) % 5) * 0.22
        ground_cols = max(1, min(9, int(round(usable_ground / target_ground_bay))))
        ground_spacing = usable_ground / ground_cols
        ground_start = -usable_ground * 0.5 + ground_spacing * 0.5
        door_col = (bseed >> 10) % ground_cols

        for col in range(ground_cols):
            along = ground_start + col * ground_spacing
            cx = midx + ux * along
            cz = midz + uz * along
            is_door = col == door_col
            if is_door:
                door_w = min(1.30, max(0.92, ground_spacing * 0.50))
                door_h = min(2.75, ground_h * 0.78)
                # A dark plane close to the wall plus a proud surround reads as a
                # recessed entrance without moving the official LoD2 wall itself.
                base.add_box_geometry(buckets, "shadow", (cx + nx * 0.025, min_y + door_h * 0.52, cz + nz * 0.025), u, n, door_w, door_h, 0.04)
                add_frame(buckets, trim_bucket, "frame", cx, min_y + door_h * 0.52, cz, u, n, door_w, door_h, 1.12)
                base.add_box_geometry(buckets, trim_bucket, (cx + nx * 0.28, min_y + door_h + 0.18, cz + nz * 0.28), u, n, door_w + 0.42, 0.18, 0.42)
                portal_count += 1
                continue

            commercial = ground_mode in (0, 1) or (ground_mode == 2 and col % 2 == 0)
            if commercial:
                pane_w = max(0.95, ground_spacing - 0.26)
                pane_h = ground_h * (0.70 if grammar != 4 else 0.62)
                bucket = "shop_lit" if ((fseed + col * 19) % 5 == 0) else "shop_dark"
                base.add_box_geometry(buckets, bucket, (cx + nx * 0.055, min_y + pane_h * 0.55, cz + nz * 0.055), u, n, pane_w, pane_h, 0.07)
                add_frame(buckets, trim_bucket, "frame", cx, min_y + pane_h * 0.55, cz, u, n, pane_w, pane_h, 0.88)
                shop_count += 1
            else:
                pane_w = max(0.78, min(1.28, ground_spacing * 0.54))
                pane_h = min(2.05, ground_h * 0.58)
                bucket = "glass_cool" if col % 2 else "glass_dark"
                base.add_box_geometry(buckets, bucket, (cx + nx * 0.04, min_y + pane_h * 0.62 + 0.38, cz + nz * 0.04), u, n, pane_w, pane_h, 0.055)
                add_frame(buckets, trim_bucket, "frame", cx, min_y + pane_h * 0.62 + 0.38, cz, u, n, pane_w, pane_h, 0.92)
                window_count += 1

        # Ground-floor head course is not continuous on every building.
        if ground_mode != 3:
            base.add_box_geometry(buckets, trim_bucket, (midx + nx * 0.16, min_y + ground_h + 0.10, midz + nz * 0.16), u, n, max(1.0, usable_ground), 0.13, 0.26)

        upper_bottom = min_y + ground_h + 0.72
        upper_top = max_y - 0.82
        available = upper_top - upper_bottom
        if available < 2.0:
            continue
        floors = max(1, min(7, int(round(available / floor_targets[grammar]))))
        floor_step = available / floors
        upper_margin = min(1.35, max(0.58, 0.62 + ((bseed >> 12) % 5) * 0.12))
        usable = max(1.2, length - upper_margin * 2.0)
        cols = max(1, min(11, int(round(usable / bay_targets[grammar]))))
        spacing = usable / cols
        window_w = min(1.72, max(0.78, spacing * width_ratios[grammar]))
        window_h = min(2.12, max(1.18, floor_step * height_ratios[grammar]))
        start = -usable * 0.5 + spacing * 0.5
        group_size = group_sizes[grammar]

        # Building-level pilasters split the repetitive window field into bays.
        if cols >= 4:
            for boundary in range(group_size, cols, group_size):
                along = -usable * 0.5 + boundary * spacing
                cx = midx + ux * along + nx * 0.15
                cz = midz + uz * along + nz * 0.15
                ph = max(1.0, upper_top - upper_bottom + 0.42)
                base.add_box_geometry(buckets, trim_bucket, (cx, upper_bottom - 0.14 + ph * 0.5, cz), u, n, 0.11 + grammar * 0.012, ph, 0.20)
                pilaster_count += 1

        for floor in range(floors):
            cy = upper_bottom + (floor + 0.5) * floor_step
            # Different buildings use different horizontal band cadence.
            if floor > 0 and ((floor + grammar) % (2 if grammar in (0, 3) else 3) == 0):
                band_y = upper_bottom + floor * floor_step
                base.add_box_geometry(buckets, trim_bucket, (midx + nx * 0.085, band_y, midz + nz * 0.085), u, n, max(1.0, length - 0.22), 0.10, 0.15)

            for col in range(cols):
                # One grammar intentionally leaves a few blank bays; this prevents
                # the synthetic perfect-grid look without claiming exact fenestration.
                if grammar == 4 and ((fseed + floor * 13 + col * 7) % 17 == 0):
                    continue
                along = start + col * spacing
                # Paired-window grammars tighten alternating columns toward a pair.
                if grammar in (1, 4) and cols > 2:
                    pair_shift = spacing * 0.075 * (-1.0 if col % 2 == 0 else 1.0)
                    along += pair_shift
                cx = midx + ux * along
                cz = midz + uz * along
                jitter = (((bseed >> ((col + floor) % 16)) & 3) - 1.5) * 0.025
                ww = window_w * (1.0 + jitter)
                wh = window_h * (1.0 - jitter * 0.6)
                state = (fseed + floor * 17 + col * 29) % 9
                bucket = "glass_lit" if state in (0, 4) else "glass_cool" if state in (2, 6) else "glass_dark"
                base.add_box_geometry(buckets, bucket, (cx + nx * 0.035, cy, cz + nz * 0.035), u, n, ww, wh, 0.055)
                add_frame(buckets, trim_bucket, "frame", cx, cy, cz, u, n, ww, wh, 0.90 + grammar * 0.04)
                if ww > 1.18 and grammar in (0, 1, 4):
                    base.add_box_geometry(buckets, "frame", (cx + nx * 0.15, cy, cz + nz * 0.15), u, n, 0.055, wh, 0.11)
                window_count += 1

        # A small number of projecting bays add silhouette depth to the closest
        # prominent facades.  They remain generic authored vocabulary, not survey data.
        if rank < 10 and initial_angle <= 36.0 and length >= 10.0 and height >= 15.0 and bseed % 4 == 0:
            bay_w = min(3.15, length * 0.22)
            bay_h = max(5.0, upper_top - upper_bottom - 0.35)
            bay_y = upper_bottom + bay_h * 0.5
            offset = (0.14 if ((bseed >> 5) & 1) else -0.14) * length
            bx = midx + ux * offset
            bz = midz + uz * offset
            base.add_box_geometry(buckets, trim_bucket, (bx + nx * 0.44, bay_y, bz + nz * 0.44), u, n, bay_w, bay_h, 0.72)
            base.add_box_geometry(buckets, "glass_dark", (bx + nx * 0.84, bay_y, bz + nz * 0.84), u, n, bay_w * 0.56, bay_h * 0.80, 0.06)
            bay_count += 1

    created = 0
    for bucket, data in buckets.items():
        obj = base.build_bucket_object(visual, f"hamburg_facade_authored_{bucket}", data, mats[bucket])
        if obj is not None:
            obj["hamburg_facade_grammar_version"] = 1
            created += 1

    root["hamburg_facade_authored_layer"] = True
    root["hamburg_facade_authored_radius_m"] = cfg.radius_m
    root["hamburg_facade_authored_face_count"] = len(selected)
    root["hamburg_facade_authored_window_count"] = window_count
    root["hamburg_facade_authored_shopfront_count"] = shop_count
    root["hamburg_facade_authored_portal_count"] = portal_count
    root["hamburg_facade_authored_pilaster_count"] = pilaster_count
    root["hamburg_facade_authored_bay_count"] = bay_count
    root["hamburg_facade_grammar_version"] = 1
    root["hamburg_facade_grammar_count"] = len(grammar_seen)
    root["hamburg_facade_selection_basis"] = "v8 balanced multi-view official-wall priority; initial forward cone first; per-building face cap"
    root["hamburg_facade_selection_priority_version"] = 8
    root["hamburg_facade_selection_view_yaws"] = "0,-1.05,1.05"
    root["hamburg_facade_selection_initial_forward_guarantee_deg"] = INITIAL_FORWARD_GUARANTEE_DEG
    root["hamburg_facade_selection_fragment_merging"] = False
    root["hamburg_facade_selection_min_budget"] = cfg.max_facades
    root["hamburg_facade_panorama_projection"] = False
    root["hamburg_facade_quality_version"] = 8
    root["hamburg_facade_authored_source"] = "Hamburg LGV LoD2-DE 2026; deterministic per-building authored grammar; no facade photo projection"
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(
        "Hamburg v8 facade grammar: "
        f"facades={len(selected)} windows={window_count} shops={shop_count} portals={portal_count} "
        f"pilasters={pilaster_count} bays={bay_count} grammars={len(grammar_seen)} objects={created} removed={removed}"
    )


if __name__ == "__main__":
    main()
