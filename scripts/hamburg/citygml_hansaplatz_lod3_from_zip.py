#!/usr/bin/env python3
"""Extract a local Hansaplatz subset from official Hamburg LoD3.0-HH CityGML.

The source archive is the untextured Area 1 dataset. This script preserves
semantic surface classes where present and emits a local Y-up OBJ around the
Poly Haven Hansaplatz GPS reference. The resulting shell is a macro-geometry
source; it does not claim that windows/doors/storefront depth is complete.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

from pyproj import Transformer

GML = "http://www.opengis.net/gml"
DEFAULT_LAT = 53.554451
DEFAULT_LON = 10.012056
DEFAULT_EPSG = 25832
DATASET = "3D-Gebäudemodell LoD3.0-HH Hamburg untexturiert, Area1, 2025"
LICENSE = "dl-de-by-2.0"
ATTRIBUTION = "Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV)"

SEMANTIC_KINDS = {
    "WallSurface": "wall",
    "RoofSurface": "roof",
    "GroundSurface": "ground",
    "ClosureSurface": "closure",
    "OuterCeilingSurface": "ceiling",
    "OuterFloorSurface": "floor",
    "Window": "window",
    "Door": "door",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--source-json", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--lat", type=float, default=DEFAULT_LAT)
    parser.add_argument("--lon", type=float, default=DEFAULT_LON)
    parser.add_argument("--radius-m", type=float, default=170.0)
    parser.add_argument("--source-epsg", type=int, default=DEFAULT_EPSG)
    return parser.parse_args()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return value.strip("_")[:96] or "building"


def parse_poslist(text: str | None, dimension: int = 3) -> list[tuple[float, float, float]]:
    if not text:
        return []
    values = [float(value) for value in text.split()]
    if dimension not in (2, 3) or len(values) < dimension or len(values) % dimension:
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
        values = [float(value) for value in node.text.split()]
        if len(values) >= 3:
            points.append((values[0], values[1], values[2]))
    if len(points) >= 2 and points[0] == points[-1]:
        points.pop()
    return points


def semantic_surfaces(building: ET.Element) -> list[tuple[str, list[tuple[float, float, float]]]]:
    result: list[tuple[str, list[tuple[float, float, float]]]] = []
    for element in building.iter():
        kind = SEMANTIC_KINDS.get(local_name(element.tag))
        if kind is None:
            continue
        for polygon in element.iter():
            if local_name(polygon.tag) != "Polygon":
                continue
            points = ring_points(polygon)
            if len(points) >= 3:
                result.append((kind, points))
    return result


def centroid_xy(surfaces: list[tuple[str, list[tuple[float, float, float]]]]) -> tuple[float, float] | None:
    points = [point for _, polygon in surfaces for point in polygon]
    if not points:
        return None
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


def stream_selected_buildings(
    archive: zipfile.ZipFile,
    origin_x: float,
    origin_y: float,
    radius_m: float,
) -> tuple[list[tuple[str, list[tuple[str, list[tuple[float, float, float]]]]]], list[str]]:
    selected: list[tuple[str, list[tuple[str, list[tuple[float, float, float]]]]]] = []
    members = [name for name in archive.namelist() if Path(name).suffix.lower() in {".gml", ".xml"}]
    if not members:
        raise RuntimeError("Hamburg LoD3 Area1 archive contains no CityGML/XML members")

    seen: set[str] = set()
    for member in members:
        with archive.open(member) as stream:
            for _event, element in ET.iterparse(stream, events=("end",)):
                if local_name(element.tag) != "Building":
                    continue
                building_id = element.attrib.get(f"{{{GML}}}id") or f"{Path(member).stem}-{len(seen)}"
                if building_id in seen:
                    element.clear()
                    continue
                surfaces = semantic_surfaces(element)
                center = centroid_xy(surfaces)
                if center is not None:
                    dx = center[0] - origin_x
                    dy = center[1] - origin_y
                    if dx * dx + dy * dy <= radius_m * radius_m:
                        selected.append((safe_name(building_id), surfaces))
                        seen.add(building_id)
                element.clear()
    return selected, members


def write_obj(
    out: Path,
    selected: list[tuple[str, list[tuple[str, list[tuple[float, float, float]]]]]],
    origin_x: float,
    origin_y: float,
    source_epsg: int,
    lat: float,
    lon: float,
    source_url: str,
) -> dict[str, object]:
    heights = [point[2] for _, surfaces in selected for _, polygon in surfaces for point in polygon]
    if not heights:
        raise RuntimeError("Selected Hamburg LoD3 buildings contain no height coordinates")
    base_height = min(heights)

    vertices: list[tuple[float, float, float]] = []
    objects: list[tuple[str, str, list[list[int]]]] = []
    semantic_counts: dict[str, int] = defaultdict(int)
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
                semantic_counts[kind] += 1
        for kind, faces in by_kind.items():
            objects.append((f"lod3_{building_id}_{kind}", kind, faces))

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        handle.write("# Official Hamburg LoD3.0-HH subset around Poly Haven Hansaplatz GPS\n")
        handle.write(f"# Source: {source_url}\n")
        handle.write(f"# Dataset: {DATASET}\n")
        handle.write(f"# License: {LICENSE}\n")
        handle.write(f"# Attribution: {ATTRIBUTION}\n")
        handle.write(f"# Origin WGS84: {lat}, {lon}\n")
        handle.write(f"# Origin EPSG:{source_epsg}: {origin_x:.3f}, {origin_y:.3f}\n")
        handle.write(f"# Base height: {base_height:.3f}\n")
        for x, y, z in vertices:
            handle.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for name, kind, faces in objects:
            handle.write(f"o {name}\n")
            handle.write(f"g {kind}\n")
            for face in faces:
                handle.write("f " + " ".join(str(index) for index in face) + "\n")

    return {
        "building_count": len(selected),
        "vertex_count": len(vertices),
        "semantic_object_count": len(objects),
        "semantic_face_counts": dict(sorted(semantic_counts.items())),
        "base_height": base_height,
    }


def main() -> None:
    args = parse_args()
    archive_path = Path(args.zip)
    if not archive_path.exists():
        raise RuntimeError(f"Hamburg LoD3 archive missing: {archive_path}")

    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{args.source_epsg}", always_xy=True)
    origin_x, origin_y = transformer.transform(args.lon, args.lat)
    with zipfile.ZipFile(archive_path) as archive:
        selected, members = stream_selected_buildings(archive, origin_x, origin_y, args.radius_m)

    if not selected:
        raise RuntimeError(
            f"No Hamburg LoD3 buildings selected within {args.radius_m}m of "
            f"{args.lat},{args.lon} in EPSG:{args.source_epsg}"
        )

    stats = write_obj(
        Path(args.out), selected, origin_x, origin_y, args.source_epsg, args.lat, args.lon, args.source_url
    )
    source = {
        "provider": ATTRIBUTION,
        "dataset": DATASET,
        "source_url": args.source_url,
        "metadata_url": "https://suche.transparenz.hamburg.de/dataset/3d-gebaeudemodell-lod3-0-hh-hamburg-untexturiert6",
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "reference": {
            "asset": "Poly Haven hansaplatz",
            "gps_source": "https://polyhaven.com/a/hansaplatz",
            "lat": args.lat,
            "lon": args.lon,
            "location": "Hansaplatz, Hamburg-St. Georg, Germany",
        },
        "selection": {
            "radius_m": args.radius_m,
            "source_epsg": args.source_epsg,
            "origin_easting": origin_x,
            "origin_northing": origin_y,
            "citygml_member_count": len(members),
        },
        "quality_boundary": {
            "macro_geometry": "official LoD3.0-HH shell",
            "facade_openings_complete": False,
            "final_facade_material": False,
            "panorama_role": "reference evidence and far environment; not raw final wall projection",
        },
        "output": stats,
    }
    source_path = Path(args.source_json)
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(source, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
