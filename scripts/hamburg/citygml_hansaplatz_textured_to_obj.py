#!/usr/bin/env python3
"""Convert official textured Hamburg LoD3 CityGML near Hansaplatz to OBJ+MTL.

Unlike the old Poly Haven equirectangular wall projection, this converter preserves
Hamburg's own CityGML ParameterizedTexture polygon mappings. Only buildings inside
the requested radius are emitted, and only texture images referenced by those
selected polygons are copied into the output bundle.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
from pathlib import Path, PurePosixPath
import re
import shutil
import xml.etree.ElementTree as ET

from pyproj import Transformer

GML = "http://www.opengis.net/gml"
SEMANTIC_KIND = {
    "WallSurface": "wall",
    "RoofSurface": "roof",
    "GroundSurface": "ground",
    "ClosureSurface": "closure",
    "OuterCeilingSurface": "ceiling",
    "OuterFloorSurface": "floor",
    "Window": "window",
    "Door": "door",
}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--out-obj", required=True, type=Path)
    parser.add_argument("--lat", type=float, default=53.554451)
    parser.add_argument("--lon", type=float, default=10.012056)
    parser.add_argument("--radius-m", type=float, default=170.0)
    parser.add_argument("--source-epsg", type=int, default=25832)
    return parser.parse_args()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")[:112] or "item"


def normalize_en(first: float, second: float) -> tuple[float, float, str] | None:
    east = lambda value: 100_000.0 <= value <= 900_000.0
    north = lambda value: 5_000_000.0 <= value <= 7_000_000.0
    if east(first) and north(second):
        return first, second, "east-north"
    if north(first) and east(second):
        return second, first, "north-east"
    return None


def parse_numbers(text: str | None) -> list[float]:
    if not text:
        return []
    try:
        return [float(value) for value in text.replace(",", " ").split()]
    except ValueError:
        return []


def ring_geometry(polygon: ET.Element) -> tuple[list[tuple[float, float, float, str]], str | None]:
    exterior = next((node for node in polygon.iter() if local_name(node.tag) == "exterior"), None)
    scope = exterior if exterior is not None else polygon
    ring = next((node for node in scope.iter() if local_name(node.tag) == "LinearRing"), None)
    ring_id = ring.attrib.get(f"{{{GML}}}id") if ring is not None else None
    scope = ring if ring is not None else scope

    for node in scope.iter():
        if local_name(node.tag) != "posList":
            continue
        values = parse_numbers(node.text)
        try:
            dim = int(node.attrib.get("srsDimension", "3"))
        except ValueError:
            dim = 3
        if dim not in (2, 3, 4) or len(values) % dim:
            dim = 3 if len(values) >= 3 and len(values) % 3 == 0 else 2
        points: list[tuple[float, float, float, str]] = []
        for index in range(0, len(values), dim):
            if index + 1 >= len(values):
                break
            normalized = normalize_en(values[index], values[index + 1])
            if not normalized:
                continue
            east, north, order = normalized
            height = values[index + 2] if dim >= 3 and index + 2 < len(values) else 0.0
            points.append((east, north, height, order))
        if len(points) >= 2 and points[0][:3] == points[-1][:3]:
            points.pop()
        if len(points) >= 3:
            return points, ring_id

    points = []
    for node in scope.iter():
        if local_name(node.tag) != "pos":
            continue
        values = parse_numbers(node.text)
        if len(values) < 2:
            continue
        normalized = normalize_en(values[0], values[1])
        if normalized:
            east, north, order = normalized
            points.append((east, north, values[2] if len(values) >= 3 else 0.0, order))
    if len(points) >= 2 and points[0][:3] == points[-1][:3]:
        points.pop()
    return points, ring_id


def resolve_image(image_uri: str, gml_path: Path, input_dir: Path) -> Path | None:
    cleaned = image_uri.replace("\\", "/").replace("%20", " ").split("?", 1)[0].split("#", 1)[0].lstrip("./")
    direct = (gml_path.parent / cleaned).resolve()
    try:
        direct.relative_to(input_dir.resolve())
    except ValueError:
        direct = Path("/__outside__")
    if direct.is_file():
        return direct
    root_direct = (input_dir / cleaned).resolve()
    if root_direct.is_file():
        return root_direct
    basename = PurePosixPath(cleaned).name.lower()
    matches = [path for path in input_dir.rglob("*") if path.is_file() and path.name.lower() == basename]
    return matches[0] if len(matches) == 1 else None


def texture_map(root: ET.Element, gml_path: Path, input_dir: Path) -> dict[str, tuple[Path, list[float], str | None]]:
    result: dict[str, tuple[Path, list[float], str | None]] = {}
    for texture in root.iter():
        if local_name(texture.tag) != "ParameterizedTexture":
            continue
        image_uri = next((node.text.strip() for node in texture.iter() if local_name(node.tag) == "imageURI" and node.text), None)
        if not image_uri:
            continue
        image_path = resolve_image(image_uri, gml_path, input_dir)
        if image_path is None:
            continue
        for target in texture.iter():
            if local_name(target.tag) != "target":
                continue
            uri = target.attrib.get("uri") or target.attrib.get(f"{{{GML}}}href")
            if not uri:
                continue
            polygon_id = uri.lstrip("#")
            coords = next((node for node in target.iter() if local_name(node.tag) == "textureCoordinates" and node.text), None)
            if coords is None:
                continue
            values = parse_numbers(coords.text)
            if len(values) < 6 or len(values) % 2:
                continue
            ring_ref = coords.attrib.get("ring")
            result[polygon_id] = (image_path, values, ring_ref.lstrip("#") if ring_ref else None)
    return result


def iter_buildings(root: ET.Element):
    for element in root.iter():
        if local_name(element.tag) in {"Building", "BuildingPart"}:
            yield element


def building_surfaces(building: ET.Element):
    found = False
    for element in building.iter():
        semantic = SEMANTIC_KIND.get(local_name(element.tag))
        if semantic is None:
            continue
        found = True
        for polygon in element.iter():
            if local_name(polygon.tag) != "Polygon":
                continue
            points, ring_id = ring_geometry(polygon)
            if len(points) >= 3:
                yield semantic, polygon, points, ring_id
    if not found:
        for polygon in building.iter():
            if local_name(polygon.tag) == "Polygon":
                points, ring_id = ring_geometry(polygon)
                if len(points) >= 3:
                    yield "wall", polygon, points, ring_id


def centroid(surfaces) -> tuple[float, float] | None:
    points = [point for _, _, polygon, _ in surfaces for point in polygon]
    if not points:
        return None
    return sum(point[0] for point in points) / len(points), sum(point[1] for point in points) / len(points)


def texture_uv(values: list[float], point_count: int) -> list[tuple[float, float]] | None:
    pairs = [(values[i], values[i + 1]) for i in range(0, len(values), 2)]
    if len(pairs) >= 2 and pairs[0] == pairs[-1]:
        pairs.pop()
    if len(pairs) != point_count:
        return None
    return pairs


def main() -> None:
    cfg = parse_args()
    files = sorted(path for path in cfg.input_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".gml", ".xml", ".citygml"})
    if not files:
        raise RuntimeError(f"No CityGML files found under {cfg.input_dir}")

    origin_east, origin_north = Transformer.from_crs("EPSG:4326", f"EPSG:{cfg.source_epsg}", always_xy=True).transform(cfg.lon, cfg.lat)
    selected = []
    axis_orders: Counter[str] = Counter()
    heights: list[float] = []

    for path in files:
        root = ET.parse(path).getroot()
        textures = texture_map(root, path, cfg.input_dir)
        for index, building in enumerate(iter_buildings(root)):
            building_id = building.attrib.get(f"{{{GML}}}id") or f"{path.stem}-{index}"
            surfaces = list(building_surfaces(building))
            center = centroid(surfaces)
            if center is None or (center[0] - origin_east) ** 2 + (center[1] - origin_north) ** 2 > cfg.radius_m ** 2:
                continue
            selected.append((safe_name(building_id), surfaces, textures))
            for _, _, polygon, _ in surfaces:
                for _, _, height, order in polygon:
                    heights.append(height)
                    axis_orders[order] += 1

    if not selected or not heights:
        raise RuntimeError(f"No textured Hamburg LoD3 buildings within {cfg.radius_m:.1f}m")

    base_height = min(heights)
    out_dir = cfg.out_obj.parent
    textures_dir = out_dir / "textures"
    out_dir.mkdir(parents=True, exist_ok=True)
    textures_dir.mkdir(parents=True, exist_ok=True)
    mtl_path = cfg.out_obj.with_suffix(".mtl")

    image_materials: dict[Path, str] = {}
    image_destinations: dict[Path, Path] = {}
    vertices: list[tuple[float, float, float]] = []
    uvs: list[tuple[float, float]] = []
    records: list[tuple[str, str, str, list[int], list[int] | None]] = []
    textured_faces = 0
    untextured_faces = 0

    def material_for_image(path: Path) -> str:
        if path in image_materials:
            return image_materials[path]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        suffix = path.suffix.lower() if path.suffix.lower() in IMAGE_SUFFIXES else ".jpg"
        destination = textures_dir / f"{digest}{suffix}"
        if not destination.exists():
            shutil.copy2(path, destination)
        material = f"official_tex_{digest}"
        image_materials[path] = material
        image_destinations[path] = destination
        return material

    seen_buildings: set[str] = set()
    for building_id, surfaces, textures in selected:
        if building_id in seen_buildings:
            continue
        seen_buildings.add(building_id)
        for semantic, polygon_el, points, ring_id in surfaces:
            polygon_id = polygon_el.attrib.get(f"{{{GML}}}id")
            mapping = textures.get(polygon_id) if polygon_id else None
            face_vertices = []
            for east, north, height, _ in points:
                vertices.append((east - origin_east, height - base_height, -(north - origin_north)))
                face_vertices.append(len(vertices))
            face_uvs: list[int] | None = None
            material = f"fallback_{semantic}"
            if mapping:
                image_path, values, mapped_ring = mapping
                uv_pairs = texture_uv(values, len(points))
                if uv_pairs is not None and (not mapped_ring or not ring_id or mapped_ring == ring_id):
                    material = material_for_image(image_path)
                    face_uvs = []
                    for u, v in uv_pairs:
                        uvs.append((u, v))
                        face_uvs.append(len(uvs))
                    textured_faces += 1
                else:
                    untextured_faces += 1
            else:
                untextured_faces += 1
            records.append((f"lod3_{building_id}_{semantic}", semantic, material, face_vertices, face_uvs))

    with cfg.out_obj.open("w", encoding="utf-8") as handle:
        handle.write("# Official textured Hamburg LoD3 subset around Hansaplatz\n")
        handle.write(f"# Origin WGS84: {cfg.lat}, {cfg.lon}\n")
        handle.write(f"# Origin EPSG:{cfg.source_epsg}: {origin_east:.3f}, {origin_north:.3f}\n")
        handle.write(f"# Base height: {base_height:.3f}\n")
        handle.write(f"# Source axis orders normalized: {dict(axis_orders)}\n")
        handle.write(f"# Textured faces: {textured_faces}; fallback faces: {untextured_faces}\n")
        handle.write(f"mtllib {mtl_path.name}\n")
        for x, y, z in vertices:
            handle.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for u, v in uvs:
            handle.write(f"vt {u:.8f} {v:.8f}\n")
        current_obj = None
        current_material = None
        for obj_name, semantic, material, face_vertices, face_uvs in records:
            if obj_name != current_obj:
                handle.write(f"o {obj_name}\n")
                handle.write(f"g {semantic}\n")
                current_obj = obj_name
            if material != current_material:
                handle.write(f"usemtl {material}\n")
                current_material = material
            if face_uvs:
                handle.write("f " + " ".join(f"{vi}/{ti}" for vi, ti in zip(face_vertices, face_uvs)) + "\n")
            else:
                handle.write("f " + " ".join(map(str, face_vertices)) + "\n")

    with mtl_path.open("w", encoding="utf-8") as handle:
        for semantic, rgb in {
            "wall": (0.34, 0.32, 0.29),
            "roof": (0.09, 0.10, 0.11),
            "ground": (0.28, 0.28, 0.27),
            "closure": (0.31, 0.30, 0.28),
            "ceiling": (0.30, 0.30, 0.29),
            "floor": (0.28, 0.28, 0.27),
            "window": (0.05, 0.07, 0.08),
            "door": (0.14, 0.12, 0.10),
        }.items():
            handle.write(f"newmtl fallback_{semantic}\nKd {rgb[0]} {rgb[1]} {rgb[2]}\nPr 0.7\n\n")
        for source, material in sorted(image_materials.items(), key=lambda item: item[1]):
            destination = image_destinations[source]
            handle.write(f"newmtl {material}\nKd 1 1 1\nPr 0.72\nmap_Kd textures/{destination.name}\n\n")

    print(f"Selected buildings: {len(seen_buildings)}")
    print(f"Textured faces: {textured_faces}")
    print(f"Fallback faces: {untextured_faces}")
    print(f"Official texture images copied: {len(image_materials)}")
    print(f"Source axis orders normalized: {dict(axis_orders)}")
    print(f"Wrote OBJ: {cfg.out_obj}")
    print(f"Wrote MTL: {mtl_path}")


if __name__ == "__main__":
    main()
