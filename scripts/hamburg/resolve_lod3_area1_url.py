#!/usr/bin/env python3
"""Resolve the current official Hamburg LoD3.0-HH untextured Area 1 CityGML ZIP.

The resolver intentionally starts from public metadata pages instead of pinning an
opaque download URL. It fails closed unless it can identify exactly one plausible
Area 1 archive URL after canonicalizing escaped metadata representations.
"""

from __future__ import annotations

import argparse
from html import unescape
import json
import re
import sys
from urllib.parse import urljoin
from urllib.request import Request, urlopen

METADATA_URLS = (
    "https://suche.transparenz.hamburg.de/dataset/3d-gebaeudemodell-lod3-0-hh-hamburg-untexturiert6",
    "https://www.govdata.de/suche/daten/3d-gebaudemodell-lod3-0-hh-hamburg-untexturiert",
    "https://data.europa.eu/data/datasets/de792ab5-b70c-4f92-b5e2-e8ad8704c30e?locale=en",
)

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
HREF_RE = re.compile(r"(?:href|content)=[\"']([^\"']+)[\"']", re.I)


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "AsSeenBy-source-resolver/1.0"})
    with urlopen(req, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def canonicalize_url(value: str) -> str:
    value = unescape(value)
    value = value.replace("\\/", "/")
    # Some metadata pages expose the same JSON-escaped URL both as a raw text
    # match and as an href/content value. Strip serialization punctuation so
    # those representations collapse to one canonical download URL.
    value = value.rstrip("\\),.;\"'")
    return value


def normalized_candidates(base_url: str, text: str) -> set[str]:
    raw: set[str] = set(URL_RE.findall(text))
    raw.update(urljoin(base_url, unescape(value)) for value in HREF_RE.findall(text))
    candidates: set[str] = set()
    for raw_value in raw:
        value = canonicalize_url(raw_value)
        lower = value.lower()
        if "lod3" not in lower:
            continue
        if "area1" not in lower and "area_1" not in lower and "area%201" not in lower:
            continue
        if not any(token in lower for token in (".zip", "citygml", ".gml")):
            continue
        candidates.add(value)
    return candidates


def score(url: str) -> tuple[int, int, int, int]:
    lower = url.lower()
    return (
        1 if lower.endswith(".zip") else 0,
        1 if "2025" in lower else 0,
        1 if "area1" in lower or "area_1" in lower else 0,
        1 if "daten-hamburg.de/opendata/3d_stadtmodell_lod3/" in lower else 0,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    all_candidates: set[str] = set()
    failures: dict[str, str] = {}
    for metadata_url in METADATA_URLS:
        try:
            html = fetch(metadata_url)
        except Exception as exc:  # network diagnostics belong in output
            failures[metadata_url] = f"{type(exc).__name__}: {exc}"
            continue
        all_candidates.update(normalized_candidates(metadata_url, html))

    if not all_candidates:
        payload = {"ok": False, "candidates": [], "failures": failures}
        print(json.dumps(payload, indent=2), file=sys.stderr)
        raise SystemExit("No LoD3 Area 1 archive URL found in official metadata pages")

    ranked = sorted(all_candidates, key=lambda item: (score(item), item), reverse=True)
    best_score = score(ranked[0])
    best = [url for url in ranked if score(url) == best_score]
    if len(best) != 1:
        payload = {"ok": False, "candidates": ranked, "failures": failures}
        print(json.dumps(payload, indent=2), file=sys.stderr)
        raise SystemExit(f"Ambiguous LoD3 Area 1 archive candidates: {len(best)} share best score")

    payload = {
        "ok": True,
        "url": best[0],
        "candidates": ranked,
        "metadata_urls": list(METADATA_URLS),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(best[0])


if __name__ == "__main__":
    main()
