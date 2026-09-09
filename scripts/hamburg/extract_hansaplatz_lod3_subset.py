#!/usr/bin/env python3
"""Extract the Hamburg LoD3 source subset that contains Poly Haven's Hansaplatz GPS point.

The official Hamburg archive is large, so this script does not vendor the full archive. It:
1. resolves the target point into EPSG:25832,
2. ranks CityGML/XML entries by 1 km tile tokens,
3. confirms candidates with their gml:Envelope where available,
4. extracts only matching CityGML plus referenced texture images,
5. writes a provenance/selection manifest and human-readable report.

This script is intentionally source-format tolerant: it supports namespaced or plain
lowerCorner/upperCorner elements and resolves image references by exact path, relative
path, or unique basename inside the archive.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import zipfile

from pyproj import Transformer

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
GML_SUFFIXES = {".gml", ".xml", ".citygml"}
MAX_HEADER_BYTES = 2 * 1024 * 1024
MAX_GML_SELECTION = 12

LOWER_RE = re.compile(
    rb"<(?:[A-Za-z0-9_.-]+:)?lowerCorner\b[^>]*>\s*([^<]+?)\s*</(?:[A-Za-z0-9_.-]+:)?lowerCorner>",
    re.I | re.S,
)
UPPER_RE = re.compile(
    rb"<(?:[A-Za-z0-9_.-]+:)?upperCorner\b[^>]*>\s*([^<]+?)\s*</(?:[A-Za-z0-9_.-]+:)?upperCorner>",
    re.I | re.S,
)
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
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_archive_name(name: str) -> str:
    return str(PurePosixPath(name.replace("\\", "/")))


def parse_corner(raw: bytes) -> tuple[float, ...] | None:
    try:
        values = tuple(float(part) for part in raw.decode("utf-8", "ignore").split())
    except ValueError:
        return None
    return values if len(values) >= 2 else None


def read_envelope(zf: zipfile.ZipFile, name: str) -> tuple[tuple[float, ...], tuple[float, ...]] | None:
    try:
        with zf.open(name, "r") as fh:
            prefix = fh.read(MAX_HEADER_BYTES)
    except (KeyError, OSError, zipfile.BadZipFile):
        return None
    lower_match = LOWER_RE.search(prefix)
    upper_match = UPPER_RE.search(prefix)
    if not lower_match or not upper_match:
        return None
    lower = parse_corner(lower_match.group(1))
    upper = parse_corner(upper_match.group(1))
    if not lower or not upper:
        return None
    return lower, upper


def contains_xy(envelope: tuple[tuple[float, ...], tuple[float, ...]], x: float, y: float, margin: float = 1.0) -> bool:
    lower, upper = envelope
    min_x, max_x = sorted((lower[0], upper[0]))
    min_y, max_y = sorted((lower[1], upper[1]))
    return (min_x - margin) <= x <= (max_x + margin) and (min_y - margin) <= y <= (max_y + margin)


def filename_score(name: str, tile_e: int, tile_n: int, x: float, y: float) -> int:
    lower = name.lower()
    score = 0
    e_tokens = {str(tile_e + d) for d in (-1, 0, 1)}
    n_tokens = {str(tile_n + d) for d in (-1, 0, 1)}
    exact_e = str(tile_e)
    exact_n = str(tile_n)
    if exact_e in lower:
        score += 6
    if exact_n in lower:
        score += 8
    if any(token in lower for token in e_tokens):
        score += 2
    if any(token in lower for token in n_tokens):
        score += 2
    for token in (str(int(x)), str(int(y)), str(int(x) // 100), str(int(y) // 100)):
        if token in lower:
            score += 3
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
    if len(matches) == 1:
        return matches[0]
    return None


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

    x, y = Transformer.from_crs(4326, 25832, always_xy=True).transform(args.lon, args.lat)
    tile_e = int(x) // 1000
    tile_n = int(y) // 1000

    if args.out.exists():
        shutil.rmtree(args.out)
    args.out.mkdir(parents=True, exist_ok=True)
    extracted_root = args.out / "source"
    extracted_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.archive, "r") as zf:
        infos = [info for info in zf.infolist() if not info.is_dir()]
        names = [normalize_archive_name(info.filename) for info in infos]
        archive_names = set(names)
        info_by_name = {normalize_archive_name(info.filename): info for info in infos}
        gml_names = [name for name in names if PurePosixPath(name).suffix.lower() in GML_SUFFIXES]
        image_names = [name for name in names if PurePosixPath(name).suffix.lower() in IMAGE_SUFFIXES]

        basename_index: dict[str, list[str]] = {}
        for name in image_names:
            basename_index.setdefault(PurePosixPath(name).name.lower(), []).append(name)

        ranked = sorted(
            ((filename_score(name, tile_e, tile_n, x, y), name) for name in gml_names),
            key=lambda item: (-item[0], item[1]),
        )

        selected: list[dict[str, object]] = []
        inspected = 0
        # Prefer strong filename candidates first, but do not trust the archive naming
        # convention without checking the encoded spatial envelope.
        ordered = [name for score, name in ranked if score > 0] + [name for score, name in ranked if score == 0]
        seen: set[str] = set()
        for name in ordered:
            if name in seen:
                continue
            seen.add(name)
            inspected += 1
            envelope = read_envelope(zf, name)
            if envelope and contains_xy(envelope, x, y):
                score = filename_score(name, tile_e, tile_n, x, y)
                selected.append(
                    {
                        "name": name,
                        "score": score,
                        "lower_corner": envelope[0],
                        "upper_corner": envelope[1],
                    }
                )
                if len(selected) >= MAX_GML_SELECTION:
                    break
            # Avoid decompressing an unbounded number of unrelated XML files. If
            # filenames gave no useful signal, 1500 headers is still a broad scan.
            if inspected >= 1500 and selected:
                break

        if not selected:
            # Last-resort evidence mode: retain the strongest filename candidates so
            # the workflow produces an inspectable artifact instead of silently
            # manufacturing a match.
            fallback = [(score, name) for score, name in ranked if score > 0][:12]
            if not fallback:
                raise RuntimeError(
                    f"no Hansaplatz-containing CityGML envelope found among {len(gml_names)} XML/GML entries"
                )
            for score, name in fallback:
                selected.append({"name": name, "score": score, "fallback_filename_only": True})

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

            # Some exports place textures beside the GML without explicit relative
            # paths in the snippet patterns above. Include same-directory images as
            # a conservative fallback when no image reference was resolved.
            if not resolved_images:
                parent = str(PurePosixPath(gml_name).parent)
                same_dir = [
                    name
                    for name in image_names
                    if str(PurePosixPath(name).parent) == parent
                ]
                resolved_images.update(same_dir[:500])

            for image_name in sorted(resolved_images):
                destination = extracted_root / image_name
                if not destination.exists():
                    extract_entry(zf, image_name, extracted_root)

        for path in sorted(p for p in extracted_root.rglob("*") if p.is_file()):
            relative = path.relative_to(args.out).as_posix()
            extracted_files.append(
                {
                    "path": relative,
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
                "easting": x,
                "northing": y,
                "tile_e_km": tile_e,
                "tile_n_km": tile_n,
            },
            "archive_entry_count": len(names),
            "gml_entry_count": len(gml_names),
            "image_entry_count": len(image_names),
            "inspected_gml_headers": inspected,
            "selected_gml": selected,
            "unresolved_image_references": unresolved_refs,
            "extracted_files": extracted_files,
        }

        (args.out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        report_lines = [
            "# Hansaplatz Hamburg LoD3 subset extraction",
            "",
            f"GPS: {args.lat:.6f}, {args.lon:.6f}",
            f"EPSG:25832: E={x:.3f} N={y:.3f}",
            f"1km tile index: E={tile_e} N={tile_n}",
            f"Archive entries: {len(names)}",
            f"GML/XML entries: {len(gml_names)}",
            f"Image entries: {len(image_names)}",
            f"Inspected GML headers: {inspected}",
            "",
            "Selected CityGML/XML entries:",
        ]
        for item in selected:
            report_lines.append(f"- {item['name']} | score={item.get('score', 0)} | {json.dumps(item, default=list)}")
        report_lines.extend(
            [
                "",
                f"Extracted files: {len(extracted_files)}",
                f"Extracted bytes: {sum(int(item['bytes']) for item in extracted_files)}",
                f"Unresolved image refs: {len(unresolved_refs)}",
                "",
                "This report is evidence only. A filename-only fallback is not accepted as a spatial match;",
                "the downstream Blender import must require an envelope-confirmed selection.",
            ]
        )
        (args.out / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print((args.out / "REPORT.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
