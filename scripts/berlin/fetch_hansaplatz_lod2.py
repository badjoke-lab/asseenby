#!/usr/bin/env python3
"""Fetch official Berlin LoD2 tiles covering Hansaplatz.

Source: Senatsverwaltung für Stadtentwicklung, Bauen und Wohnen Berlin
ATOM feed: https://gdi.berlin.de/data/a_lod2/atom/0.atom
License: Datenlizenz Deutschland – Zero – Version 2.0 (dl-de-zero-2.0)

Berlin's current ATOM feed exposes one entry containing hundreds of ZIP links.
Each ZIP is a 1 km EPSG:25833 tile named ``LoD2_<easting-km>_<northing-km>.zip``.
This script transforms Hansaplatz from WGS84 into EPSG:25833 and downloads only
the one-kilometre tiles intersecting the requested local radius.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import shutil
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

from pyproj import Transformer

DEFAULT_FEED = "https://gdi.berlin.de/data/a_lod2/atom/0.atom"
TILE_PATTERN = re.compile(r"LoD2_(\d+)_(\d+)\.zip$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feed", default=DEFAULT_FEED)
    parser.add_argument("--lat", type=float, default=52.5178)
    parser.add_argument("--lon", type=float, default=13.34216)
    parser.add_argument("--radius-m", type=float, default=200.0)
    parser.add_argument("--source-epsg", type=int, default=25833)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-downloads", type=int, default=6)
    return parser.parse_args()


def fetch(url: str, target: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "AsSeenBy-Hansaplatz-LoD2/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response, target.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def zip_links(root: ET.Element) -> list[str]:
    links: list[str] = []
    for element in root.iter():
        if local_name(element.tag) != "link":
            continue
        href = element.attrib.get("href", "")
        if urllib.parse.urlparse(href).path.lower().endswith(".zip"):
            links.append(href)
    return links


def tile_id_from_url(url: str) -> tuple[int, int] | None:
    name = Path(urllib.parse.urlparse(url).path).name
    match = TILE_PATTERN.fullmatch(name)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def required_tiles(easting: float, northing: float, radius_m: float) -> set[tuple[int, int]]:
    min_e = math.floor((easting - radius_m) / 1000.0)
    max_e = math.floor((easting + radius_m) / 1000.0)
    min_n = math.floor((northing - radius_m) / 1000.0)
    max_n = math.floor((northing + radius_m) / 1000.0)
    return {(e, n) for e in range(min_e, max_e + 1) for n in range(min_n, max_n + 1)}


def main() -> None:
    args = parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    atom_path = out / "berlin-lod2.atom"
    fetch(args.feed, atom_path)

    root = ET.parse(atom_path).getroot()
    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{args.source_epsg}", always_xy=True)
    easting, northing = transformer.transform(args.lon, args.lat)
    wanted_tiles = required_tiles(easting, northing, args.radius_m)

    available: dict[tuple[int, int], str] = {}
    unparsed_links: list[str] = []
    for url in zip_links(root):
        tile_id = tile_id_from_url(url)
        if tile_id is None:
            unparsed_links.append(url)
            continue
        available[tile_id] = url

    missing = sorted(tile for tile in wanted_tiles if tile not in available)
    if missing:
        raise RuntimeError(
            "Berlin LoD2 ATOM does not expose required Hansaplatz tile(s): "
            f"{missing}; center EPSG:{args.source_epsg}=({easting:.3f}, {northing:.3f})"
        )

    selected = [(tile, available[tile]) for tile in sorted(wanted_tiles)]
    if len(selected) > args.max_downloads:
        raise RuntimeError(f"Hansaplatz query selected {len(selected)} ZIPs; expected <= {args.max_downloads}")

    extracted: list[str] = []
    downloads: list[dict[str, object]] = []
    for index, (tile, url) in enumerate(selected):
        zip_path = out / f"lod2-{tile[0]}-{tile[1]}.zip"
        fetch(url, zip_path)
        downloads.append({"tile": [tile[0], tile[1]], "url": url, "archive": zip_path.name})
        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                suffix = Path(member.filename).suffix.lower()
                if suffix not in {".xml", ".gml"}:
                    continue
                safe_name = f"tile-{tile[0]}-{tile[1]}-{Path(member.filename).name}"
                target = out / safe_name
                with archive.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                extracted.append(target.name)

    if not extracted:
        raise RuntimeError("Selected Berlin LoD2 archives contained no CityGML/XML files")

    manifest = {
        "source": args.feed,
        "provider": "Senatsverwaltung für Stadtentwicklung, Bauen und Wohnen Berlin",
        "dataset": "3D-Gebäudemodelle im Level of Detail 2 (LoD 2)",
        "license": "dl-de-zero-2.0",
        "reference_location": "Hansaplatz, Berlin, Germany",
        "selection_mode": "epsg25833-kilometre-tile-filename",
        "query": {
            "lat": args.lat,
            "lon": args.lon,
            "radius_m": args.radius_m,
            "source_epsg": args.source_epsg,
            "easting": easting,
            "northing": northing,
            "required_tiles": [list(tile) for tile in sorted(wanted_tiles)],
        },
        "downloads": downloads,
        "extracted": extracted,
        "unparsed_zip_link_count": len(unparsed_links),
    }
    (out / "SOURCE.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
