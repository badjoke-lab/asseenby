#!/usr/bin/env python3
"""Fetch the official Berlin LoD2 tile(s) covering Hansaplatz.

Source: Senatsverwaltung für Stadtentwicklung, Bauen und Wohnen Berlin
ATOM feed: https://gdi.berlin.de/data/a_lod2/atom/0.atom
License: Datenlizenz Deutschland – Zero – Version 2.0 (dl-de-zero-2.0)

The script deliberately downloads only ATOM entries whose GeoRSS footprint
intersects a small Hansaplatz bounding box. It never downloads Berlin-wide data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ATOM_NS = "http://www.w3.org/2005/Atom"
GEORSS_NS = "http://www.georss.org/georss"
DEFAULT_FEED = "https://gdi.berlin.de/data/a_lod2/atom/0.atom"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feed", default=DEFAULT_FEED)
    parser.add_argument("--lat", type=float, default=52.5178)
    parser.add_argument("--lon", type=float, default=13.34216)
    parser.add_argument("--radius-deg", type=float, default=0.0030)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-downloads", type=int, default=6)
    return parser.parse_args()


def fetch(url: str, target: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "AsSeenBy-Hansaplatz-LoD2/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response, target.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def floats(text: str | None) -> list[float]:
    if not text:
        return []
    return [float(value) for value in text.split()]


def entry_bbox(entry: ET.Element) -> tuple[float, float, float, float] | None:
    # GeoRSS simple box: lat1 lon1 lat2 lon2
    box = entry.find(f"{{{GEORSS_NS}}}box")
    values = floats(box.text if box is not None else None)
    if len(values) >= 4:
        lats = values[0::2]
        lons = values[1::2]
        return min(lats), min(lons), max(lats), max(lons)

    # GeoRSS polygon: alternating latitude longitude pairs.
    polygon = entry.find(f"{{{GEORSS_NS}}}polygon")
    values = floats(polygon.text if polygon is not None else None)
    if len(values) >= 6 and len(values) % 2 == 0:
        lats = values[0::2]
        lons = values[1::2]
        return min(lats), min(lons), max(lats), max(lons)
    return None


def intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    amin_lat, amin_lon, amax_lat, amax_lon = a
    bmin_lat, bmin_lon, bmax_lat, bmax_lon = b
    return not (amax_lat < bmin_lat or amin_lat > bmax_lat or amax_lon < bmin_lon or amin_lon > bmax_lon)


def main() -> None:
    args = parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    atom_path = out / "berlin-lod2.atom"
    fetch(args.feed, atom_path)

    root = ET.parse(atom_path).getroot()
    query = (
        args.lat - args.radius_deg,
        args.lon - args.radius_deg,
        args.lat + args.radius_deg,
        args.lon + args.radius_deg,
    )

    matches: list[dict[str, object]] = []
    for entry in root.findall(f"{{{ATOM_NS}}}entry"):
        bbox = entry_bbox(entry)
        if bbox is None or not intersects(bbox, query):
            continue
        title = entry.findtext(f"{{{ATOM_NS}}}title") or "untitled"
        links = [
            link.attrib.get("href", "")
            for link in entry.findall(f"{{{ATOM_NS}}}link")
            if link.attrib.get("href", "").lower().endswith(".zip")
        ]
        for href in links:
            matches.append({"title": title, "bbox": bbox, "url": href})

    # Some Berlin feeds place downloadable ZIP links in entries without GeoRSS.
    # Do not silently fall back to a Berlin-wide download: failing closed protects
    # CI bandwidth and makes source-layout changes visible.
    if not matches:
        raise RuntimeError(f"No Berlin LoD2 ATOM entry intersects Hansaplatz query bbox {query}")
    if len(matches) > args.max_downloads:
        raise RuntimeError(f"Hansaplatz query selected {len(matches)} ZIPs; expected <= {args.max_downloads}")

    extracted: list[str] = []
    for index, match in enumerate(matches):
        url = str(match["url"])
        zip_path = out / f"lod2-{index:02d}.zip"
        fetch(url, zip_path)
        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                suffix = Path(member.filename).suffix.lower()
                if suffix not in {".xml", ".gml"}:
                    continue
                safe_name = f"tile-{index:02d}-{Path(member.filename).name}"
                target = out / safe_name
                with archive.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                extracted.append(target.name)

    if not extracted:
        raise RuntimeError("Selected Berlin LoD2 archives contained no CityGML/XML files")

    manifest = {
        "source": args.feed,
        "license": "dl-de-zero-2.0",
        "reference_location": "Hansaplatz, Berlin, Germany",
        "query": {"lat": args.lat, "lon": args.lon, "radius_deg": args.radius_deg, "bbox": query},
        "downloads": matches,
        "extracted": extracted,
    }
    (out / "SOURCE.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
