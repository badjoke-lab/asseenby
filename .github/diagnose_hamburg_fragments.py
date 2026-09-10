#!/usr/bin/env python3
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path

OBJ = Path('assets-src/blender/night-intersection/hamburg-lod2/hansaplatz-lod2.obj')
TARGET = 'lod2_DEHHALKAJ0000zPg_wall'
VIEW_YAWS = (0.0, -1.05, 1.05)


def load_obj(path: Path):
    vertices = []
    objects = defaultdict(list)
    current = 'unknown'
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if parts[0] == 'v' and len(parts) >= 4:
            vertices.append(tuple(map(float, parts[1:4])))
        elif parts[0] == 'o' and len(parts) >= 2:
            current = parts[1]
        elif parts[0] == 'f' and len(parts) >= 4:
            face = []
            for token in parts[1:]:
                value = int(token.split('/', 1)[0])
                face.append(value - 1 if value > 0 else len(vertices) + value)
            objects[current].append(face)
    return vertices, objects


def unique_horizontal(points):
    seen = []
    for x, _, z in points:
        if not any(math.hypot(x-sx, z-sz) < 0.04 for sx, sz in seen):
            seen.append((x, z))
    return seen


def desc(points, index):
    horiz = unique_horizontal(points)
    best = None
    best_len = 0.0
    for i, a in enumerate(horiz):
        for b in horiz[i+1:]:
            length = math.hypot(b[0]-a[0], b[1]-a[1])
            if length > best_len:
                best = (a, b)
                best_len = length
    if not best:
        return None
    a, b = best
    ux, uz = (b[0]-a[0])/best_len, (b[1]-a[1])/best_len
    orientation = math.degrees(math.atan2(uz, ux) % math.pi)
    midx, midz = (a[0]+b[0])/2, (a[1]+b[1])/2
    dist = math.hypot(midx, midz)
    dx, dz = midx/max(dist,1e-9), midz/max(dist,1e-9)
    best_align = max(dx*(-math.sin(y)) + dz*(-math.cos(y)) for y in VIEW_YAWS)
    view_angle = math.degrees(math.acos(max(-1,min(1,best_align))))
    forward_angle = math.degrees(math.acos(max(-1,min(1,-dz))))
    return {
        'index': index,
        'a': a,
        'b': b,
        'length': best_len,
        'orientation': orientation,
        'min_y': min(p[1] for p in points),
        'max_y': max(p[1] for p in points),
        'distance': dist,
        'view_angle': view_angle,
        'forward_angle': forward_angle,
        'vertex_count': len(points),
    }


def angle_delta(a, b):
    delta = abs(a-b) % 180.0
    return min(delta, 180.0-delta)


def endpoint_gap(a, b):
    return min(math.hypot(x[0]-y[0], x[1]-y[1]) for x in (a['a'],a['b']) for y in (b['a'],b['b']))


vertices, objects = load_obj(OBJ)
faces = objects[TARGET]
print('TARGET', TARGET, 'FACE_COUNT', len(faces))
descriptors = []
for index, face in enumerate(faces):
    d = desc([vertices[i] for i in face], index)
    if d is None:
        continue
    descriptors.append(d)
    if index <= 24:
        print('FACE', index,
              'len', round(d['length'],4),
              'orient_deg', round(d['orientation'],4),
              'height', round(d['max_y']-d['min_y'],4),
              'dist', round(d['distance'],4),
              'view_deg', round(d['view_angle'],4),
              'forward_deg', round(d['forward_angle'],4),
              'a', tuple(round(v,4) for v in d['a']),
              'b', tuple(round(v,4) for v in d['b']),
              'verts', d['vertex_count'])

print('=== PAIRS 8-16 ===')
subset = [d for d in descriptors if 8 <= d['index'] <= 16]
for i, left in enumerate(subset):
    for right in subset[i+1:]:
        print('PAIR', left['index'], right['index'],
              'orient_delta', round(angle_delta(left['orientation'],right['orientation']),4),
              'endpoint_gap', round(endpoint_gap(left,right),4),
              'miny_delta', round(abs(left['min_y']-right['min_y']),4),
              'maxy_delta', round(abs(left['max_y']-right['max_y']),4))
