#!/usr/bin/env python3
"""Convert official Hamburg LoD3 CityGML around Hansaplatz to local OBJ.

The source CRS is EPSG:25832. CityGML may serialize that CRS as east/north or
north/east, so every geometry coordinate is normalized by metric range before
selection and conversion. Output uses AsSeenBy runtime XYZ: X=east, Y=up, -Z=north.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
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
    "Window": "window",
    "Door": "door",
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
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")[:112] or "building"


def normalize_en(first: float, second: float) -> tuple[float, float, str] | None:
    east = lambda value: 100_000.0 <= value <= 900_000.0
    north = lambda value: 5_000_000.0 <= value <= 7_000_000.0
    if east(first) and north(second):
        return first, second, "east-north"
    if north(first) and east(second):
        return second, first, "north-east"
    return None


def parse_poslist(text: str | None, dim: int = 3) -> list[tuple[float, float, float, str]]:
    if not text:
        return []
    try:
        values = [float(value) for value in text.replace(",", " ").split()]
    except ValueError:
        return []
    if dim not in (2, 3, 4) or len(values) % dim != 0:
        dim = 3 if len(values) >= 3 and len(values) % 3 == 0 else 2
    points: list[tuple[float, float, float, str]] = []
    for index in range(0, len(values), dim):
        if index + 1 >= len(values):
            break
        normalized = normalize_en(values[index], values[index + 1])
        if normalized is None:
            continue
        east, north, order = normalized
        height = values[index + 2] if dim >= 3 and index + 2 < len(values) else 0.0
        points.append((east, north, height, order))
    if len(points) >= 2 and points[0][:3] == points[-1][:3]:
        points.pop()
    return points


def ring_points(polygon: ET.Element) -> list[tuple[float, float, float, str]]:
    exterior = next((node for node in polygon.iter() if local_name(node.tag) == "exterior"), None)
    scope = exterior if exterior is not None else polygon
    for node in scope.iter():
        if local_name(node.tag) == "posList":
            try:
                dim = int(node.attrib.get("srsDimension", "3"))
            except ValueError:
                dim = 3
            points = parse_poslist(node.text, dim)
            if len(points) >= 3:
                return points
    points: list[tuple[float, float, float, str]] = []
    for node in scope.iter():
        if local_name(node.tag) != "pos" or not node.text:
            continue
        try:
            values = [float(value) for value in node.text.replace(",", " ").split()]
        except ValueError:
            continue
        if len(values) < 2:
            continue
        normalized = normalize_en(values[0], values[1])
        if normalized:
            east, north, order = normalized
            points.append((east, north, values[2] if len(values) >= 3 else 0.0, order))
    if len(points) >= 2 and points[0][:3] == points[-1][:3]:
        points.pop()
    return points


def iter_buildings(root: ET.Element):
    for element in root.iter():
        if local_name(element.tag) in {"Building", "BuildingPart"}:
            yield element


def semantic_surfaces(building: ET.Element):
    found_semantic = False
    for element in building.iter():
        kind = SEMANTIC_KIND.get(local_name(element.tag))
        if kind is None:
            continue
        found_semantic = True
        for polygon in element.iter():
            if local_name(polygon.tag) == "Polygon":
                points = ring_points(polygon)
                if len(points) >= 3:
                    yield kind, points
    if not found_semantic:
        for polygon in building.iter():
            if local_name(polygon.tag) == "Polygon":
                points = ring_points(polygon)
                if len(points) >= 3:
                    yield "wall", points


def centroid(surfaces) -> tuple[float, float] | None:
    points = [point for _, polygon in surfaces for point in polygon]
    if not points:
        return None
    return sum(point[0] for point in points) / len(points), sum(point[1] for point in points) / len(points)


def main() -> None:
    cfg = parse_args()
    files = sorted(path for path in cfg.input_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".gml", ".xml", ".citygml"})
    if not files:
        raise RuntimeError(f"No CityGML files found under {cfg.input_dir}")

    origin_east, origin_north = Transformer.from_crs("EPSG:4326", f"EPSG:{cfg.source_epsg}", always_xy=True).transform(cfg.lon, cfg.lat)
    selected = []
    heights: list[float] = []
    seen: set[str] = set()
    axis_orders: Counter[str] = Counter()

    for path in files:
        root = ET.parse(path).getroot()
        for index, building in enumerate(iter_buildings(root)):
            building_id = building.attrib.get(f"{{{GML}}}id") or f"{path.stem}-{index}"
            if building_id in seen:
                continue
            surfaces = list(semantic_surfaces(building))
            center = centroid(surfaces)
            if center is None:
                continue
            if (center[0] - origin_east) ** 2 + (center[1] - origin_north) ** 2 > cfg.radius_m ** 2:
                continue
            seen.add(building_id)
            selected.append((safe_name(building_id), surfaces))
            for _, polygon in surfaces:
                for _, _, height, order in polygon:
                    heights.append(height)
                    axis_orders[order] += 1

    if not selected:
        raise RuntimeError(f"No Hamburg LoD3 buildings within {cfg.radius_m:.1f}m of {cfg.lat},{cfg.lon}")

    base_height = min(heights)
    vertices: list[tuple[float, float, float]] = []
    objects: list[tuple[str, str, list[list[int]]]] = []
    for building_id, surfaces in selected:
        by_kind: dict[str, list[list[int]]] = defaultdict(list)
        for kind, polygon in surfaces:
            face = []
            for east, north, height, _ in polygon:
                vertices.append((east - origin_east, height - base_height, -(north - origin_north)))
                face.append(len(vertices))
            if len(face) >= 3:
                by_kind[kind].append(face)
        for kind, faces in sorted(by_kind.items()):
            objects.append((f"lod3_{building_id}_{kind}", kind, faces))

    cfg.out.parent.mkdir(parents=True, exist_ok=True)
    with cfg.out.open("w", encoding="utf-8") as handle:
        handle.write("# Official Hamburg LoD3 subset around Poly Haven Hansaplatz capture point\n")
        handle.write("# License: Datenlizenz Deutschland – Namensnennung – Version 2.0\n")
        handle.write("# Attribution: Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung\n")
        handle.write(f"# Origin WGS84: {cfg.lat}, {cfg.lon}\n")
        handle.write(f"# Origin EPSG:{cfg.source_epsg}: {origin_east:.3f}, {origin_north:.3f}\n")
        handle.write(f"# Base height: {base_height:.3f}\n")
        handle.write(f"# Source axis orders normalized: {dict(axis_orders)}\n")
        for x, y, z in vertices:
            handle.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for name, kind, faces in objects:
            handle.write(f"o {name}\n")
            handle.write(f"g {kind}\n")
            for face in faces:
                handle.write("f " + " ".join(map(str, face)) + "\n")

    print(f"Parsed CityGML files: {len(files)}")
    print(f"Selected Hamburg LoD3 buildings: {len(selected)}")
    print(f"OBJ vertices: {len(vertices)}")
    print(f"OBJ semantic objects: {len(objects)}")
    print(f"Source axis orders normalized: {dict(axis_orders)}")
    print(f"Source base height: {base_height:.3f}")
    print(f"Wrote: {cfg.out}")


if __name__ == "__main__":
    main()
