#!/usr/bin/env python3
"""Extract the coordinate-confirmed Hamburg LoD3 sheet for Hansaplatz.

Hamburg Area1 uses compact sheet ids rather than UTM filenames. CityGML can also
serialize EPSG:25832 in either east/north or CRS axis order north/east. This tool
normalizes both forms to (easting, northing), derives each sheet's geometry bounds,
and extracts only sheets containing the published Poly Haven Hansaplatz GPS point.
Filename-only candidates are diagnostic and are rejected by downstream builds.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import zipfile

from pyproj import Transformer

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
GML_SUFFIXES = {".gml", ".xml", ".citygml"}
MAX_XML_BYTES = 256 * 1024 * 1024
MAX_SELECTION = 12

LOWER_RE = re.compile(rb"<(?:[\w.-]+:)?lowerCorner\b[^>]*>\s*([^<]+?)\s*</(?:[\w.-]+:)?lowerCorner>", re.I | re.S)
UPPER_RE = re.compile(rb"<(?:[\w.-]+:)?upperCorner\b[^>]*>\s*([^<]+?)\s*</(?:[\w.-]+:)?upperCorner>", re.I | re.S)
POSLIST_RE = re.compile(rb"<(?:[\w.-]+:)?posList\b([^>]*)>(.*?)</(?:[\w.-]+:)?posList>", re.I | re.S)
POS_RE = re.compile(rb"<(?:[\w.-]+:)?pos\b([^>]*)>(.*?)</(?:[\w.-]+:)?pos>", re.I | re.S)
DIM_RE = re.compile(rb"(?:srsDimension|dimension)\s*=\s*['\"](\d+)['\"]", re.I)
IMAGE_REF_RE = re.compile(r"(?:[A-Za-z0-9_.%+@~-]+/)*[A-Za-z0-9_.%+@~-]+\.(?:jpe?g|png|tiff?)", re.I)


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--lat", type=float, default=53.554451)
    parser.add_argument("--lon", type=float, default=10.012056)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--dataset-url", required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def norm_name(name: str) -> str:
    return str(PurePosixPath(name.replace("\\", "/")))


def numbers(raw: bytes) -> list[float]:
    try:
        return [float(value) for value in raw.decode("utf-8", "ignore").replace(",", " ").split()]
    except ValueError:
        return []


def normalize_en(first: float, second: float) -> tuple[float, float, str] | None:
    east = lambda value: 100_000.0 <= value <= 900_000.0
    north = lambda value: 5_000_000.0 <= value <= 7_000_000.0
    if east(first) and north(second):
        return first, second, "east-north"
    if north(first) and east(second):
        return second, first, "north-east"
    return None


def dimension(attrs: bytes, count: int) -> int:
    match = DIM_RE.search(attrs)
    if match:
        value = int(match.group(1))
        if value in (2, 3, 4) and count % value == 0:
            return value
    if count >= 3 and count % 3 == 0:
        return 3
    if count >= 2 and count % 2 == 0:
        return 2
    return 3


def derive_bounds(data: bytes) -> tuple[list[float], list[float], int, dict[str, int]] | None:
    bounds = [float("inf"), float("inf"), float("-inf"), float("-inf")]
    accepted = 0
    orders: Counter[str] = Counter()

    def consume(first: float, second: float) -> None:
        nonlocal accepted
        normalized = normalize_en(first, second)
        if normalized is None:
            return
        east, north, order = normalized
        bounds[0] = min(bounds[0], east)
        bounds[1] = min(bounds[1], north)
        bounds[2] = max(bounds[2], east)
        bounds[3] = max(bounds[3], north)
        accepted += 1
        orders[order] += 1

    for match in POSLIST_RE.finditer(data):
        values = numbers(match.group(2))
        dim = dimension(match.group(1), len(values))
        for index in range(0, len(values) - 1, dim):
            consume(values[index], values[index + 1])

    for match in POS_RE.finditer(data):
        values = numbers(match.group(2))
        if len(values) >= 2:
            consume(values[0], values[1])

    if accepted == 0:
        return None
    return [bounds[0], bounds[1]], [bounds[2], bounds[3]], accepted, dict(orders)


def envelope_bounds(data: bytes) -> tuple[list[float], list[float], str] | None:
    lower_match = LOWER_RE.search(data)
    upper_match = UPPER_RE.search(data)
    if not lower_match or not upper_match:
        return None
    lower_values = numbers(lower_match.group(1))
    upper_values = numbers(upper_match.group(1))
    if len(lower_values) < 2 or len(upper_values) < 2:
        return None
    lower = normalize_en(lower_values[0], lower_values[1])
    upper = normalize_en(upper_values[0], upper_values[1])
    if not lower or not upper:
        return None
    order = lower[2] if lower[2] == upper[2] else f"{lower[2]}/{upper[2]}"
    return [lower[0], lower[1]], [upper[0], upper[1]], order


def spatial_bounds(zf: zipfile.ZipFile, name: str) -> dict[str, object] | None:
    info = zf.getinfo(name)
    if info.file_size > MAX_XML_BYTES:
        raise RuntimeError(f"CityGML exceeds safety limit: {name} ({info.file_size} bytes)")
    data = zf.read(name)
    envelope = envelope_bounds(data)
    if envelope:
        lower, upper, order = envelope
        return {
            "selection_method": "gml-envelope",
            "lower_corner": lower,
            "upper_corner": upper,
            "axis_order": order,
            "coordinate_tuple_count": 0,
        }
    derived = derive_bounds(data)
    if derived:
        lower, upper, count, orders = derived
        return {
            "selection_method": "geometry-coordinate-extents",
            "lower_corner": lower,
            "upper_corner": upper,
            "axis_orders": orders,
            "coordinate_tuple_count": count,
        }
    return None


def contains(record: dict[str, object], east: float, north: float, margin: float = 1.0) -> bool:
    lower = record["lower_corner"]
    upper = record["upper_corner"]
    assert isinstance(lower, list) and isinstance(upper, list)
    return (
        min(lower[0], upper[0]) - margin <= east <= max(lower[0], upper[0]) + margin
        and min(lower[1], upper[1]) - margin <= north <= max(lower[1], upper[1]) + margin
    )


def score_name(name: str, east: float, north: float) -> int:
    lower = name.lower()
    score = 1 if lower.endswith(".gml") else 0
    for token, points in ((str(int(east)), 5), (str(int(north)), 5), (str(int(east) // 1000), 2), (str(int(north) // 1000), 2)):
        if token in lower:
            score += points
    return score


def resolve_image(ref: str, gml_name: str, names: set[str], basenames: dict[str, list[str]]) -> str | None:
    decoded = html.unescape(ref).replace("%20", " ").split("?", 1)[0].split("#", 1)[0].lstrip("./")
    for candidate in (
        norm_name(decoded),
        norm_name(str(PurePosixPath(gml_name).parent / decoded)),
    ):
        if candidate in names:
            return candidate
    matches = basenames.get(PurePosixPath(decoded).name.lower(), [])
    return matches[0] if len(matches) == 1 else None


def extract(zf: zipfile.ZipFile, name: str, root: Path) -> Path:
    safe = norm_name(name).lstrip("/")
    if safe.startswith("../") or "/../" in safe:
        raise RuntimeError(f"unsafe archive path: {name}")
    destination = root / safe
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(name) as source, destination.open("wb") as target:
        shutil.copyfileobj(source, target, 1024 * 1024)
    return destination


def main() -> int:
    cfg = args()
    if not cfg.archive.is_file():
        raise SystemExit(f"archive not found: {cfg.archive}")
    east, north = Transformer.from_crs(4326, 25832, always_xy=True).transform(cfg.lon, cfg.lat)

    if cfg.out.exists():
        shutil.rmtree(cfg.out)
    source_root = cfg.out / "source"
    source_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(cfg.archive) as zf:
        archive_names = [norm_name(info.filename) for info in zf.infolist() if not info.is_dir()]
        names = set(archive_names)
        gml_names = [name for name in archive_names if PurePosixPath(name).suffix.lower() in GML_SUFFIXES]
        image_names = [name for name in archive_names if PurePosixPath(name).suffix.lower() in IMAGE_SUFFIXES]
        basenames: dict[str, list[str]] = {}
        for image in image_names:
            basenames.setdefault(PurePosixPath(image).name.lower(), []).append(image)

        selected: list[dict[str, object]] = []
        evidence: list[dict[str, object]] = []
        for name in sorted(gml_names):
            spatial = spatial_bounds(zf, name)
            if spatial is None:
                continue
            record = {"name": name, "filename_score": score_name(name, east, north), **spatial}
            evidence.append(record)
            if contains(record, east, north):
                selected.append(record)
                if len(selected) >= MAX_SELECTION:
                    break

        if not selected:
            diagnostics = sorted(gml_names, key=lambda name: (-score_name(name, east, north), name))[:12]
            selected = [
                {"name": name, "filename_score": score_name(name, east, north), "fallback_filename_only": True}
                for name in diagnostics
            ]

        unresolved: list[dict[str, str]] = []
        for record in selected:
            gml_name = str(record["name"])
            gml_path = extract(zf, gml_name, source_root)
            text = gml_path.read_text("utf-8", errors="ignore")
            resolved: set[str] = set()
            for ref in sorted(set(IMAGE_REF_RE.findall(text))):
                image = resolve_image(ref, gml_name, names, basenames)
                if image:
                    resolved.add(image)
                else:
                    unresolved.append({"gml": gml_name, "reference": ref})
            if not resolved and image_names:
                parent = str(PurePosixPath(gml_name).parent)
                resolved.update(name for name in image_names if str(PurePosixPath(name).parent) == parent)
            for image in sorted(resolved):
                if not (source_root / image).exists():
                    extract(zf, image, source_root)

        files = []
        for path in sorted(item for item in source_root.rglob("*") if item.is_file()):
            files.append({"path": path.relative_to(cfg.out).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})

        manifest = {
            "dataset": "Hamburg 3D building model LoD3.0 Area1",
            "dataset_url": cfg.dataset_url,
            "archive_url": cfg.source_url,
            "archive_bytes": cfg.archive.stat().st_size,
            "archive_sha256": sha256(cfg.archive),
            "license": "Datenlizenz Deutschland – Namensnennung – Version 2.0",
            "attribution": "Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung",
            "target": {"name": "Poly Haven Hansaplatz capture point", "latitude": cfg.lat, "longitude": cfg.lon, "epsg": 25832, "easting": east, "northing": north},
            "archive_entry_count": len(archive_names),
            "gml_entry_count": len(gml_names),
            "image_entry_count": len(image_names),
            "selected_gml": selected,
            "bounds_evidence": evidence,
            "unresolved_image_references": unresolved,
            "extracted_files": files,
        }
        (cfg.out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        report = [
            "# Hansaplatz Hamburg LoD3 subset extraction",
            "",
            f"Target WGS84: {cfg.lat:.6f}, {cfg.lon:.6f}",
            f"Target EPSG:25832: E={east:.3f} N={north:.3f}",
            f"GML/XML entries inspected: {len(evidence)}/{len(gml_names)}",
            f"Image entries: {len(image_names)}",
            "",
            "Selected CityGML:",
            *[f"- {json.dumps(record)}" for record in selected],
            "",
            f"Extracted files: {len(files)}",
            f"Extracted bytes: {sum(int(item['bytes']) for item in files)}",
            f"Unresolved image refs: {len(unresolved)}",
            "",
            "Production acceptance requires selection_method=gml-envelope or geometry-coordinate-extents.",
            "Filename-only fallback is diagnostic only.",
        ]
        (cfg.out / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print((cfg.out / "REPORT.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
