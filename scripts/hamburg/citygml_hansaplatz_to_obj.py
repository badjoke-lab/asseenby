#!/usr/bin/env python3
"""Convert official Hamburg LoD3 CityGML around the Hansaplatz capture point to OBJ.

Input coordinates are ETRS89 / UTM zone 32N (EPSG:25832). The output uses the
AsSeenBy runtime frame: X=east, Y=up, -Z=north, centered on Poly Haven's published
Hansaplatz capture GPS position. Building selection happens by actual geometry
centroid inside a configurable radius; sheet ids are never treated as coordinates.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from pyproj import Transformer

GML = "http://www.opengis.net/gml"
SEMANTIC_KIND = {
    "WallSurface": "wall",
    "RoofSurface": "roof",
    "GroundSurface": "ground",
    "ClosureSurface": "wall",
    "OuterCeilingSurface": "ceiling",
    "OuterFloorSurface": "ground",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--lat", type=float, default=53.554451)
    parser.add_argument("--lon", type=float, default=10.012056)
    parser.add_argument("--radius-m", type=float, default=180.0)
    parser.add_argument("--source-epsg", type=int, default=25832)
    return parser.parse_args()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def safe_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return normalized.strip("_")[:112] or "building"


def parse_poslist(text: str | None, dimension: int = 3) -> list[tuple[float, float, float]]:
    if not text:
        return []
    try:
        values = [float(value) for value in text.replace(",", " ").split()]
    except ValueError:
        return []
    if dimension not in (2, 3, 4):
        dimension = 3
    if len(values) < dimension or len(values) % dimension != 0:
        # Hamburg building geometry is 3D; tolerate files that omit srsDimension.
        if len(values) >= 3 and len(values) % 3 == 0:
            dimension = 3
        elif len(values) >= 2 and len(values) % 2 == 0:
            dimension = 2
        else:
            return []
    points: list[tuple[float, float, float]] = []
    for index in range(0, len(values), dimension):
        if dimension == 2:
            points.append((values[index], values[index + 1], 0.0))
        else:
            points.append((values[index], values[index + 1], values[index + 2]))
    if len(points) >= 2 and points[0] == points[-1]:
        points.pop()
    return points


def ring_points(polygon: ET.Element) -> list[tuple[float, float, float]]:
    exterior = next((node for node in polygon.iter() if local_name(node.tag) == "exterior"), None)
    scope = exterior if exterior is not None else polygon
    for node in scope.iter():
        if local_name(node.tag) != "posList":
            continue
        dimension = int(node.attrib.get("srsDimension", "3"))
        points = parse_poslist(node.text, dimension)
        if len(points) >= 3:
            return points
    points: list[tuple[float, float, float]] = []
    for node in scope.iter():
        if local_name(node.tag) != "pos" or not node.text:
            continue
        try:
            values = [float(value) for value in node.text.replace(",", " ").split()]
        except ValueError:
            continue
        if len(values) >= 3:
            points.append((values[0], values[1], values[2]))
        elif len(values) == 2:
            points.append((values[0], values[1], 0.0))
    if len(points) >= 2 and points[0] == points[-1]:
        points.pop()
    return points


def iter_buildings(root: ET.Element):
    for element in root.iter():
        if local_name(element.tag) in {"Building", "BuildingPart"}:
            yield element


def semantic_surfaces(building: ET.Element):
    found_semantic = False
    for element in building.iter():
        semantic = local_name(element.tag)
        kind = SEMANTIC_KIND.get(semantic)
        if kind is None:
            continue
        found_semantic = True
        for polygon in element.iter():
            if local_name(polygon.tag) != "Polygon":
                continue
            points = ring_points(polygon)
            if len(points) >= 3:
                yield kind, points
    # Some LoD3 exports wrap polygons differently. Preserve geometry rather than
    # dropping a building, but label the fallback as wall/unknown for review.
    if not found_semantic:
        for polygon in building.iter():
            if local_name(polygon.tag) == "Polygon":
                points = ring_points(polygon)
                if len(points) >= 3:
                    yield "wall", points


def centroid_xy(surfaces: list[tuple[str, list[tuple[float, float, float]]]]) -> tuple[float, float] | None:
    points = [point for _, polygon in surfaces for point in polygon]
    if not points:
        return None
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


def main() -> None:
    args = parse_args()
    files = sorted(
        path
        for path in args.input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".gml", ".xml", ".citygml"}
    )
    if not files:
        raise RuntimeError(f"No CityGML files found under {args.input_dir}")

    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{args.source_epsg}", always_xy=True)
    origin_x, origin_y = transformer.transform(args.lon, args.lat)

    selected: list[tuple[str, list[tuple[str, list[tuple[float, float, float]]]]]] = []
    heights: list[float] = []
    seen_ids: set[str] = set()
    parsed_files = 0

    for path in files:
        root = ET.parse(path).getroot()
        parsed_files += 1
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
            heights.extend(point[2] for _, polygon in surfaces for point in polygon)

    if not selected:
        raise RuntimeError(
            f"No Hamburg LoD3 building surfaces selected within {args.radius_m:.1f} m of "
            f"{args.lat},{args.lon} from {parsed_files} CityGML files"
        )

    # Align the official local district to runtime ground while preserving all
    # relative roof/facade elevations. The exact source datum is retained below.
    base_height = min(heights)
    vertices: list[tuple[float, float, float]] = []
    objects: list[tuple[str, str, list[list[int]]]] = []

    for building_id, surfaces in selected:
        by_kind: dict[str, list[list[int]]] = defaultdict(list)
        for kind, polygon in surfaces:
            face: list[int] = []
            for east, north, height in polygon:
                local = (east - origin_x, height - base_height, -(north - origin_y))
                vertices.append(local)
                face.append(len(vertices))
            if len(face) >= 3:
                by_kind[kind].append(face)
        for kind, faces in sorted(by_kind.items()):
            objects.append((f"lod3_{building_id}_{kind}", kind, faces))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        handle.write("# Official Hamburg LoD3 subset around Poly Haven Hansaplatz capture point\n")
        handle.write("# Dataset: 3D-Gebaeudemodell LoD3.0 Hamburg\n")
        handle.write("# License: Datenlizenz Deutschland – Namensnennung – Version 2.0\n")
        handle.write("# Attribution: Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung\n")
        handle.write(f"# Origin WGS84: {args.lat}, {args.lon}\n")
        handle.write(f"# Origin EPSG:{args.source_epsg}: {origin_x:.3f}, {origin_y:.3f}\n")
        handle.write(f"# Base height: {base_height:.3f}\n")
        handle.write(f"# Selection radius: {args.radius_m:.1f} m\n")
        for x, y, z in vertices:
            handle.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for name, kind, faces in objects:
            handle.write(f"o {name}\n")
            handle.write(f"g {kind}\n")
            for face in faces:
                handle.write("f " + " ".join(str(index) for index in face) + "\n")

    print(f"Parsed CityGML files: {parsed_files}")
    print(f"Selected Hamburg LoD3 buildings: {len(selected)}")
    print(f"OBJ vertices: {len(vertices)}")
    print(f"OBJ semantic objects: {len(objects)}")
    print(f"Source base height: {base_height:.3f}")
    print(f"Wrote: {args.out}")


if __name__ == "__main__":
    main()
