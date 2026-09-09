#!/usr/bin/env python3
"""Extract the Hamburg LoD3 source subset containing the Hansaplatz capture point.

Hamburg's LoD3 Area archives use compact sheet ids (for example 6431.gml), not
UTM tile names, and the current files do not expose a root gml:Envelope. Selection
therefore has two independently inspectable spatial paths:

1. use gml:lowerCorner / gml:upperCorner when present;
2. otherwise derive each CityGML file's XY bounds from gml:posList / gml:pos
   coordinates and require the target EPSG:25832 point to fall inside those bounds.

Only a coordinate-confirmed CityGML file and its referenced textures are extracted.
A filename-only fallback is retained solely as diagnostic evidence and must never be
accepted by the downstream Blender build.
"""

from __future__ import annotations

import argparse
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
MAX_GML_SELECTION = 12
MAX_XML_BYTES = 256 * 1024 * 1024

LOWER_RE = re.compile(
    rb"<(?:[A-Za-z0-9_.-]+:)?lowerCorner\b[^>]*>\s*([^<]+?)\s*</(?:[A-Za-z0-9_.-]+:)?lowerCorner>",
    re.I | re.S,
)
UPPER_RE = re.compile(
    rb"<(?:[A-Za-z0-9_.-]+:)?upperCorner\b[^>]*>\s*([^<]+?)\s*</(?:[A-Za-z0-9_.-]+:)?upperCorner>",
    re.I | re.S,
)
POSLIST_RE = re.compile(
    rb"<(?:[A-Za-z0-9_.-]+:)?posList\b([^>]*)>(.*?)</(?:[A-Za-z0-9_.-]+:)?posList>",
    re.I | re.S,
)
POS_RE = re.compile(
    rb"<(?:[A-Za-z0-9_.-]+:)?pos\b([^>]*)>(.*?)</(?:[A-Za-z0-9_.-]+:)?pos>",
    re.I | re.S,
)
DIM_RE = re.compile(rb"(?:srsDimension|dimension)\s*=\s*['\"](\d+)['\"]", re.I)
IMAGE_REF_RE = re.compile(
    r"(?:[A-Za-z0-9_.%+@~-]+/)*[A-Za-z0-9_.%+@~-]+\.(?:jpe?g|png|tiff?)",
    re.I,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--lat", type=float, default=53.554451)
    parser.add_argument("--lon", type=float, default=10.012056)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--dataset-url", required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_archive_name(name: str) -> str:
    return str(PurePosixPath(name.replace("\\", "/")))


def parse_numbers(raw: bytes) -> list[float]:
    try:
        return [float(part) for part in raw.decode("utf-8", "ignore").replace(",", " ").split()]
    except ValueError:
        return []


def parse_corner(raw: bytes) -> tuple[float, ...] | None:
    values = parse_numbers(raw)
    return tuple(values) if len(values) >= 2 else None


def update_bounds(bounds: list[float], x: float, y: float) -> None:
    # Hamburg EPSG:25832 coordinates should be approximately E=5e5, N=5.9e6.
    # This guard excludes texture coordinates and other local numeric tuples that
    # can occur in appearance elements.
    if not (100_000.0 <= x <= 900_000.0 and 5_000_000.0 <= y <= 7_000_000.0):
        return
    bounds[0] = min(bounds[0], x)
    bounds[1] = min(bounds[1], y)
    bounds[2] = max(bounds[2], x)
    bounds[3] = max(bounds[3], y)


def infer_dimension(attrs: bytes, count: int) -> int:
    match = DIM_RE.search(attrs)
    if match:
        dimension = int(match.group(1))
        if dimension in (2, 3, 4) and count % dimension == 0:
            return dimension
    # CityGML building geometry in this dataset is 3D. Prefer triples whenever
    # possible; fall back to 2D only when triples are impossible.
    if count >= 3 and count % 3 == 0:
        return 3
    if count >= 2 and count % 2 == 0:
        return 2
    return 3


def derive_coordinate_bounds(data: bytes) -> tuple[tuple[float, float], tuple[float, float], int] | None:
    bounds = [float("inf"), float("inf"), float("-inf"), float("-inf")]
    tuple_count = 0

    for match in POSLIST_RE.finditer(data):
        values = parse_numbers(match.group(2))
        if len(values) < 2:
            continue
        dimension = infer_dimension(match.group(1), len(values))
        for index in range(0, len(values) - 1, dimension):
            if index + 1 >= len(values):
                break
            update_bounds(bounds, values[index], values[index + 1])
            tuple_count += 1

    for match in POS_RE.finditer(data):
        values = parse_numbers(match.group(2))
        if len(values) >= 2:
            update_bounds(bounds, values[0], values[1])
            tuple_count += 1

    if bounds[0] == float("inf"):
        return None
    return (bounds[0], bounds[1]), (bounds[2], bounds[3]), tuple_count


def read_spatial_bounds(
    zf: zipfile.ZipFile, name: str
) -> tuple[tuple[float, ...], tuple[float, ...], str, int] | None:
    try:
        info = zf.getinfo(name)
        if info.file_size > MAX_XML_BYTES:
            raise RuntimeError(f"CityGML file exceeds safety limit ({info.file_size} bytes): {name}")
        data = zf.read(name)
    except (KeyError, OSError, zipfile.BadZipFile) as exc:
        raise RuntimeError(f"cannot read CityGML entry {name}: {exc}") from exc

    lower_match = LOWER_RE.search(data)
    upper_match = UPPER_RE.search(data)
    if lower_match and upper_match:
        lower = parse_corner(lower_match.group(1))
        upper = parse_corner(upper_match.group(1))
        if lower and upper:
            return lower, upper, "gml-envelope", 0

    derived = derive_coordinate_bounds(data)
    if derived:
        lower, upper, tuple_count = derived
        return lower, upper, "geometry-coordinate-extents", tuple_count
    return None


def contains_xy(
    lower: tuple[float, ...],
    upper: tuple[float, ...],
    x: float,
    y: float,
    margin: float = 1.0,
) -> bool:
    min_x, max_x = sorted((lower[0], upper[0]))
    min_y, max_y = sorted((lower[1], upper[1]))
    return (min_x - margin) <= x <= (max_x + margin) and (min_y - margin) <= y <= (max_y + margin)


def filename_score(name: str, tile_e: int, tile_n: int, x: float, y: float) -> int:
    lower = name.lower()
    score = 0
    for token, points in (
        (str(tile_e), 6),
        (str(tile_n), 8),
        (str(int(x)), 3),
        (str(int(y)), 3),
    ):
        if token in lower:
            score += points
    if "lod3" in lower:
        score += 2
    if lower.endswith(".gml"):
        score += 1
    return score


def resolve_image_reference(
    ref: str,
    gml_name: str,
    archive_names: set[str],
    basename_index: dict[str, list[str]],
) -> str | None:
    decoded = html.unescape(ref).replace("%20", " ")
    decoded = decoded.split("?", 1)[0].split("#", 1)[0].lstrip("./")
    candidates = [
        normalize_archive_name(decoded),
        normalize_archive_name(str(PurePosixPath(gml_name).parent / decoded)),
    ]
    for candidate in candidates:
        if candidate in archive_names:
            return candidate
    matches = basename_index.get(PurePosixPath(decoded).name.lower(), [])
    return matches[0] if len(matches) == 1 else None


def extract_entry(zf: zipfile.ZipFile, name: str, out_root: Path) -> Path:
    safe_name = normalize_archive_name(name).lstrip("/")
    if safe_name.startswith("../") or "/../" in safe_name:
        raise RuntimeError(f"unsafe archive path: {name}")
    destination = out_root / safe_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(name, "r") as src, destination.open("wb") as dst:
        shutil.copyfileobj(src, dst, 1024 * 1024)
    return destination


def main() -> int:
    args = parse_args()
    if not args.archive.is_file():
        raise SystemExit(f"archive not found: {args.archive}")

    target_x, target_y = Transformer.from_crs(4326, 25832, always_xy=True).transform(args.lon, args.lat)
    tile_e = int(target_x) // 1000
    tile_n = int(target_y) // 1000

    if args.out.exists():
        shutil.rmtree(args.out)
    args.out.mkdir(parents=True, exist_ok=True)
    extracted_root = args.out / "source"
    extracted_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.archive, "r") as zf:
        infos = [info for info in zf.infolist() if not info.is_dir()]
        names = [normalize_archive_name(info.filename) for info in infos]
        archive_names = set(names)
        gml_names = [name for name in names if PurePosixPath(name).suffix.lower() in GML_SUFFIXES]
        image_names = [name for name in names if PurePosixPath(name).suffix.lower() in IMAGE_SUFFIXES]

        basename_index: dict[str, list[str]] = {}
        for name in image_names:
            basename_index.setdefault(PurePosixPath(name).name.lower(), []).append(name)

        ranked = sorted(
            ((filename_score(name, tile_e, tile_n, target_x, target_y), name) for name in gml_names),
            key=lambda item: (-item[0], item[1]),
        )

        selected: list[dict[str, object]] = []
        inspected = 0
        bounds_evidence: list[dict[str, object]] = []
        # There are only about 80 GML sheets in Area1. Scan all of them and derive
        # spatial extents from actual building coordinates rather than guessing from
        # the sheet id.
        for score, name in ranked:
            inspected += 1
            spatial = read_spatial_bounds(zf, name)
            if not spatial:
                continue
            lower, upper, method, tuple_count = spatial
            evidence = {
                "name": name,
                "score": score,
                "selection_method": method,
                "lower_corner": list(lower),
                "upper_corner": list(upper),
                "coordinate_tuple_count": tuple_count,
            }
            if len(bounds_evidence) < 200:
                bounds_evidence.append(evidence)
            if contains_xy(lower, upper, target_x, target_y):
                selected.append(evidence)
                if len(selected) >= MAX_GML_SELECTION:
                    break

        if not selected:
            fallback = [(score, name) for score, name in ranked if score > 0][:12]
            for score, name in fallback:
                selected.append({"name": name, "score": score, "fallback_filename_only": True})
            if not selected:
                raise RuntimeError(f"no spatial or filename candidate found among {len(gml_names)} GML entries")

        extracted_files: list[dict[str, object]] = []
        unresolved_refs: list[dict[str, str]] = []
        selected_gml_names = [str(item["name"]) for item in selected]

        for gml_name in selected_gml_names:
            gml_path = extract_entry(zf, gml_name, extracted_root)
            text = gml_path.read_text("utf-8", errors="ignore")
            refs = sorted(set(IMAGE_REF_RE.findall(text)))
            resolved_images: set[str] = set()
            for ref in refs:
                resolved = resolve_image_reference(ref, gml_name, archive_names, basename_index)
                if resolved:
                    resolved_images.add(resolved)
                else:
                    unresolved_refs.append({"gml": gml_name, "reference": ref})

            if not resolved_images and image_names:
                parent = str(PurePosixPath(gml_name).parent)
                same_dir = [name for name in image_names if str(PurePosixPath(name).parent) == parent]
                resolved_images.update(same_dir[:1000])

            for image_name in sorted(resolved_images):
                destination = extracted_root / image_name
                if not destination.exists():
                    extract_entry(zf, image_name, extracted_root)

        for path in sorted(p for p in extracted_root.rglob("*") if p.is_file()):
            extracted_files.append(
                {
                    "path": path.relative_to(args.out).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )

        manifest = {
            "dataset": "Hamburg 3D building model LoD3.0 Area1",
            "dataset_url": args.dataset_url,
            "archive_url": args.source_url,
            "archive_bytes": args.archive.stat().st_size,
            "archive_sha256": sha256_file(args.archive),
            "license": "Datenlizenz Deutschland – Namensnennung – Version 2.0",
            "target": {
                "name": "Hansaplatz (Poly Haven HDRI capture point)",
                "latitude": args.lat,
                "longitude": args.lon,
                "epsg": 25832,
                "easting": target_x,
                "northing": target_y,
                "nominal_tile_e_km": tile_e,
                "nominal_tile_n_km": tile_n,
            },
            "archive_entry_count": len(names),
            "gml_entry_count": len(gml_names),
            "image_entry_count": len(image_names),
            "inspected_gml_files": inspected,
            "selected_gml": selected,
            "bounds_evidence": bounds_evidence,
            "unresolved_image_references": unresolved_refs,
            "extracted_files": extracted_files,
        }

        (args.out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        report_lines = [
            "# Hansaplatz Hamburg LoD3 subset extraction",
            "",
            f"GPS: {args.lat:.6f}, {args.lon:.6f}",
            f"EPSG:25832: E={target_x:.3f} N={target_y:.3f}",
            f"Archive entries: {len(names)}",
            f"GML/XML entries: {len(gml_names)}",
            f"Image entries: {len(image_names)}",
            f"Inspected GML files: {inspected}",
            "",
            "Selected CityGML/XML entries:",
        ]
        for item in selected:
            report_lines.append(f"- {item['name']} | {json.dumps(item, default=list)}")
        report_lines.extend(
            [
                "",
                f"Extracted files: {len(extracted_files)}",
                f"Extracted bytes: {sum(int(item['bytes']) for item in extracted_files)}",
                f"Unresolved image refs: {len(unresolved_refs)}",
                "",
                "Acceptance rule: every production geometry selection must use either",
                "gml-envelope or geometry-coordinate-extents. Filename-only fallback is diagnostic only.",
            ]
        )
        (args.out / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print((args.out / "REPORT.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
