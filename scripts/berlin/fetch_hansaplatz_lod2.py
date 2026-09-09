#!/usr/bin/env python3
"""Fetch the official Berlin LoD2 tile(s) covering Hansaplatz.

Source: Senatsverwaltung für Stadtentwicklung, Bauen und Wohnen Berlin
ATOM feed: https://gdi.berlin.de/data/a_lod2/atom/0.atom
License: Datenlizenz Deutschland – Zero – Version 2.0 (dl-de-zero-2.0)

The script selects only entries whose advertised spatial footprint intersects a
small Hansaplatz bounding box. Berlin's ATOM has changed serialization over time,
so both GeoRSS Simple and GeoRSS-GML are accepted. If a future feed exposes no
spatial metadata, a very small feed (<= --max-downloads) may be consumed in full;
a larger unlocated feed fails closed and prints its ZIP URLs for diagnosis.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ATOM_NS = "http://www.w3.org/2005/Atom"
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


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def floats(text: str | None) -> list[float]:
    if not text:
        return []
    return [float(value) for value in text.replace(",", " ").split()]


def find_descendants(element: ET.Element, name: str):
    for child in element.iter():
        if local_name(child.tag) == name:
            yield child


def normalize_pairs(values: list[float]) -> list[tuple[float, float]]:
    """Return WGS84 (lat, lon) pairs from a 2D GeoRSS/GML coordinate list."""
    if len(values) < 2 or len(values) % 2:
        return []
    raw = list(zip(values[0::2], values[1::2]))
    # Standard GeoRSS/GML WGS84 axis order is latitude, longitude. Some services
    # nevertheless emit x/y. Detect only when the latitude interpretation is
    # impossible, otherwise retain standards-compliant order.
    if all(abs(first) <= 90 and abs(second) <= 180 for first, second in raw):
        return [(first, second) for first, second in raw]
    if all(abs(second) <= 90 and abs(first) <= 180 for first, second in raw):
        return [(second, first) for first, second in raw]
    return []


def bbox_from_pairs(pairs: list[tuple[float, float]]) -> tuple[float, float, float, float] | None:
    if not pairs:
        return None
    lats = [pair[0] for pair in pairs]
    lons = [pair[1] for pair in pairs]
    return min(lats), min(lons), max(lats), max(lons)


def entry_bbox(entry: ET.Element) -> tuple[float, float, float, float] | None:
    # GeoRSS Simple: <box>lat lon lat lon</box>
    for box in find_descendants(entry, "box"):
        values = floats(box.text)
        result = bbox_from_pairs(normalize_pairs(values[:4]))
        if result is not None:
            return result

    # GeoRSS Simple polygon or GeoRSS-GML Polygon/LinearRing posList.
    for polygon in find_descendants(entry, "polygon"):
        values = floats(polygon.text)
        result = bbox_from_pairs(normalize_pairs(values))
        if result is not None:
            return result
    for poslist in find_descendants(entry, "posList"):
        values = floats(poslist.text)
        dimension = int(poslist.attrib.get("srsDimension", "2"))
        if dimension == 2:
            result = bbox_from_pairs(normalize_pairs(values))
            if result is not None:
                return result

    # GML Envelope commonly appears below <georss:where>.
    for envelope in find_descendants(entry, "Envelope"):
        lower = next(find_descendants(envelope, "lowerCorner"), None)
        upper = next(find_descendants(envelope, "upperCorner"), None)
        if lower is not None and upper is not None:
            pairs = normalize_pairs(floats(lower.text)[:2] + floats(upper.text)[:2])
            result = bbox_from_pairs(pairs)
            if result is not None:
                return result

    # Point metadata is enough for tile selection when no polygon/envelope exists.
    for point in find_descendants(entry, "Point"):
        pos = next(find_descendants(point, "pos"), None)
        if pos is not None:
            pairs = normalize_pairs(floats(pos.text)[:2])
            result = bbox_from_pairs(pairs)
            if result is not None:
                return result
    return None


def intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    amin_lat, amin_lon, amax_lat, amax_lon = a
    bmin_lat, bmin_lon, bmax_lat, bmax_lon = b
    return not (amax_lat < bmin_lat or amin_lat > bmax_lat or amax_lon < bmin_lon or amin_lon > bmax_lon)


def zip_links(entry: ET.Element) -> list[str]:
    links = []
    for element in entry.iter():
        if local_name(element.tag) != "link":
            continue
        href = element.attrib.get("href", "")
        if urllib.parse.urlparse(href).path.lower().endswith(".zip"):
            links.append(href)
    return links


def entry_title(entry: ET.Element) -> str:
    for child in entry:
        if local_name(child.tag) == "title" and child.text:
            return child.text.strip()
    return "untitled"


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

    entries = [element for element in root.iter() if local_name(element.tag) == "entry"]
    matches: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    all_downloads: list[dict[str, object]] = []
    located_entries = 0
    for entry in entries:
        title = entry_title(entry)
        bbox = entry_bbox(entry)
        links = zip_links(entry)
        if bbox is not None:
            located_entries += 1
        if links:
            diagnostics.append({"title": title, "bbox": bbox, "zip_links": links})
        for href in links:
            record = {"title": title, "bbox": bbox, "url": href}
            all_downloads.append(record)
            if bbox is not None and intersects(bbox, query):
                matches.append(record)

    selection_mode = "spatial-footprint"
    if not matches and located_entries == 0 and 0 < len(all_downloads) <= args.max_downloads:
        # Safe bounded fallback for a feed that contains only a few complete-area
        # archives and no per-entry spatial metadata.
        matches = all_downloads
        selection_mode = "bounded-complete-feed-fallback"

    if not matches:
        diagnostic = {
            "query_bbox": query,
            "entry_count": len(entries),
            "entries_with_spatial_bbox": located_entries,
            "zip_link_count": len(all_downloads),
            "sample_entries": diagnostics[:30],
        }
        print(json.dumps(diagnostic, indent=2))
        raise RuntimeError(
            "No safely selectable Berlin LoD2 download intersects Hansaplatz; "
            "see ATOM diagnostics above"
        )
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
        "selection_mode": selection_mode,
        "query": {"lat": args.lat, "lon": args.lon, "radius_deg": args.radius_deg, "bbox": query},
        "downloads": matches,
        "extracted": extracted,
    }
    (out / "SOURCE.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
