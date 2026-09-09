#!/usr/bin/env python3
"""Convert official Berlin LoD2 CityGML near Hansaplatz into a local OBJ.

The source CityGML uses metric ETRS89 / UTM coordinates. We select building
surfaces whose horizontal centroid lies inside a configurable radius around
Hansaplatz, shift them to a local runtime frame, and emit separate wall/roof/
ground OBJ objects. OBJ n-gons are intentionally preserved for Blender to
triangulate robustly.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from pyproj import Transformer

GML = "http://www.opengis.net/gml"
BLDG_NAMESPACES = (
    "http://www.opengis.net/citygml/building/2.0",
    "http://www.opengis.net/citygml/building/1.0",
    "http://www.opengis.net/citygml/building/3.0",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--lat", type=float, default=52.5178)
    parser.add_argument("--lon", type=float, default=13.34216)
    parser.add_argument("--radius-m", type=float, default=145.0)
    parser.add_argument("--source-epsg", type=int, default=25833)
    return parser.parse_args()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return value.strip("_")[:96] or "building"


def parse_poslist(text: str | None, dimension: int = 3) -> list[tuple[float, float, float]]:
    if not text:
        return []
    values = [float(v) for v in text.split()]
    if len(values) < dimension or len(values) % dimension != 0:
        return []
    points = []
    for i in range(0, len(values), dimension):
        if dimension == 2:
            points.append((values[i], values[i + 1], 0.0))
        else:
            points.append((values[i], values[i + 1], values[i + 2]))
    if len(points) >= 2 and points[0] == points[-1]:
        points = points[:-1]
    return points


def ring_points(polygon: ET.Element) -> list[tuple[float, float, float]]:
    exterior = None
    for child in polygon.iter():
        if local_name(child.tag) == "exterior":
            exterior = child
            break
    scope = exterior if exterior is not None else polygon
    for node in scope.iter():
        if local_name(node.tag) == "posList":
            dim = int(node.attrib.get("srsDimension", "3"))
            points = parse_poslist(node.text, dim)
            if len(points) >= 3:
                return points
    # Older GML sometimes stores repeated <gml:pos> elements.
    points = []
    for node in scope.iter():
        if local_name(node.tag) == "pos" and node.text:
            values = [float(v) for v in node.text.split()]
            if len(values) >= 3:
                points.append((values[0], values[1], values[2]))
    if len(points) >= 2 and points[0] == points[-1]:
        points = points[:-1]
    return points


def iter_buildings(root: ET.Element):
    for element in root.iter():
        if local_name(element.tag) in {"Building", "BuildingPart"}:
            yield element


def semantic_surfaces(building: ET.Element):
    for element in building.iter():
        semantic = local_name(element.tag)
        if semantic not in {"WallSurface", "RoofSurface", "GroundSurface", "ClosureSurface"}:
            continue
        kind = {
            "WallSurface": "wall",
            "RoofSurface": "roof",
            "GroundSurface": "ground",
            "ClosureSurface": "wall",
        }[semantic]
        for polygon in element.iter():
            if local_name(polygon.tag) == "Polygon":
                points = ring_points(polygon)
                if len(points) >= 3:
                    yield kind, points


def centroid_xy(surfaces: list[tuple[str, list[tuple[float, float, float]]]]) -> tuple[float, float] | None:
    pts = [point for _, poly in surfaces for point in poly]
    if not pts:
        return None
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    out = Path(args.out)
    files = sorted([*input_dir.glob("*.gml"), *input_dir.glob("*.xml")])
    if not files:
        raise RuntimeError(f"No CityGML files found in {input_dir}")

    to_metric = Transformer.from_crs("EPSG:4326", f"EPSG:{args.source_epsg}", always_xy=True)
    origin_x, origin_y = to_metric.transform(args.lon, args.lat)

    selected: list[tuple[str, list[tuple[str, list[tuple[float, float, float]]]]]] = []
    all_heights: list[float] = []
    seen_ids: set[str] = set()

    for path in files:
        root = ET.parse(path).getroot()
        for index, building in enumerate(iter_buildings(root)):
            building_id = building.attrib.get(f"{{{GML}}}id") or f"{path.stem}-{index}"
            if building_id in seen_ids:
                continue
            surfaces = list(semantic_surfaces(building))
            center = centroid_xy(surfaces)
            if center is None:
                continue
            dx = center[0] - origin_x
            dy = center[1] - origin_y
            if dx * dx + dy * dy > args.radius_m * args.radius_m:
                continue
            seen_ids.add(building_id)
            selected.append((safe_name(building_id), surfaces))
            all_heights.extend(point[2] for _, poly in surfaces for point in poly)

    if not selected:
        raise RuntimeError(f"No LoD2 building surfaces selected within {args.radius_m} m of Hansaplatz")

    # Use the lowest selected official surface as local Y=0. This keeps the
    # imported district aligned with the existing plaza ground without baking
    # Berlin's absolute vertical datum into browser coordinates.
    base_height = min(all_heights)

    vertices: list[tuple[float, float, float]] = []
    objects: list[tuple[str, str, list[list[int]]]] = []
    for building_id, surfaces in selected:
        by_kind: dict[str, list[list[int]]] = defaultdict(list)
        for kind, polygon in surfaces:
            face = []
            for east, north, height in polygon:
                # Browser runtime uses X east, Y up, -Z north.
                local = (east - origin_x, height - base_height, -(north - origin_y))
                vertices.append(local)
                face.append(len(vertices))
            if len(face) >= 3:
                by_kind[kind].append(face)
        for kind, faces in by_kind.items():
            objects.append((f"lod2_{building_id}_{kind}", kind, faces))

    with out.open("w", encoding="utf-8") as handle:
        handle.write("# Official Berlin LoD2 subset around Hansaplatz\n")
        handle.write("# Source: https://gdi.berlin.de/data/a_lod2/atom/0.atom\n")
        handle.write("# License: dl-de-zero-2.0\n")
        handle.write(f"# Origin WGS84: {args.lat}, {args.lon}\n")
        handle.write(f"# Origin EPSG:{args.source_epsg}: {origin_x:.3f}, {origin_y:.3f}\n")
        handle.write(f"# Base height: {base_height:.3f}\n")
        for x, y, z in vertices:
            handle.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for name, kind, faces in objects:
            handle.write(f"o {name}\n")
            handle.write(f"g {kind}\n")
            for face in faces:
                handle.write("f " + " ".join(str(index) for index in face) + "\n")

    print(f"Selected LoD2 buildings: {len(selected)}")
    print(f"OBJ vertices: {len(vertices)}")
    print(f"OBJ semantic objects: {len(objects)}")
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
