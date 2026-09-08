"""Fetch a compact Poly Haven PBR texture bundle for Blender authoring.

The Poly Haven files API is treated as the source of truth. The script walks the
returned file tree, selects 1K JPG diffuse / OpenGL normal / roughness records,
verifies MD5 when provided, and stores deterministic local filenames plus a
machine-readable provenance manifest.

Usage:
  python3 scripts/polyhaven/fetch_texture_bundle.py \
    --asset concrete_pavement \
    --out assets-src/blender/night-intersection/materials/hansaplatz
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request


API_BASE = "https://api.polyhaven.com"
USER_AGENT = "AsSeenBy-Explore3D/1.0 (+https://github.com/badjoke-lab/asseenby)"
TOKENS = {
    "diff": ("_diff_", "_diffuse_"),
    "nor_gl": ("_nor_gl_", "normal_gl", "nor_gl"),
    "rough": ("_rough_", "roughness"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--resolution", default="1k")
    return parser.parse_args()


def get_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response)


def walk_records(node: object, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], dict]]:
    found: list[tuple[tuple[str, ...], dict]] = []
    if isinstance(node, dict):
        if isinstance(node.get("url"), str):
            found.append((path, node))
        for key, value in node.items():
            if key in {"url", "md5", "size"}:
                continue
            found.extend(walk_records(value, path + (str(key),)))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(walk_records(value, path + (str(index),)))
    return found


def score_record(path: tuple[str, ...], record: dict, asset: str, resolution: str, kind: str) -> int:
    url = str(record.get("url", ""))
    decoded = urllib.parse.unquote(url).lower()
    filename = Path(urllib.parse.urlparse(decoded).path).name
    haystack = " ".join(part.lower() for part in path) + " " + filename
    if not filename.endswith((".jpg", ".jpeg")):
        return -10_000
    if asset.lower() not in decoded:
        return -5_000
    if not any(token in haystack for token in TOKENS[kind]):
        return -4_000

    score = 100
    if resolution.lower() in haystack:
        score += 50
    if f"/{resolution.lower()}/" in decoded:
        score += 35
    if filename.endswith(".jpg"):
        score += 10
    # Avoid DirectX normal variants when OpenGL was requested.
    if kind == "nor_gl" and ("nor_dx" in haystack or "normal_dx" in haystack):
        score -= 500
    return score


def select_record(records: list[tuple[tuple[str, ...], dict]], asset: str, resolution: str, kind: str) -> tuple[tuple[str, ...], dict]:
    ranked = sorted(
        ((score_record(path, record, asset, resolution, kind), path, record) for path, record in records),
        key=lambda item: item[0],
        reverse=True,
    )
    if not ranked or ranked[0][0] < 0:
        candidates = [str(record.get("url")) for _, record in records[:20]]
        raise RuntimeError(f"Could not resolve {kind} map for {asset}. Sample records: {candidates}")
    _, path, record = ranked[0]
    return path, record


def download(record: dict, target: Path) -> dict[str, object]:
    url = str(record["url"])
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    target.parent.mkdir(parents=True, exist_ok=True)
    sha256 = hashlib.sha256()
    md5_hash = hashlib.md5()
    size = 0
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as fh:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)
            sha256.update(chunk)
            md5_hash.update(chunk)
            size += len(chunk)

    actual_md5 = md5_hash.hexdigest()
    expected_md5 = record.get("md5")
    if isinstance(expected_md5, str) and expected_md5 and actual_md5.lower() != expected_md5.lower():
        target.unlink(missing_ok=True)
        raise RuntimeError(f"MD5 mismatch for {url}: expected {expected_md5}, got {actual_md5}")
    return {
        "source_url": url,
        "filename": target.name,
        "size": size,
        "md5": actual_md5,
        "sha256": sha256.hexdigest(),
    }


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    files_url = f"{API_BASE}/files/{urllib.parse.quote(args.asset)}"
    info_url = f"{API_BASE}/info/{urllib.parse.quote(args.asset)}"
    files = get_json(files_url)
    info = get_json(info_url)
    records = walk_records(files)

    selected: dict[str, object] = {}
    for kind in ("diff", "nor_gl", "rough"):
        path, record = select_record(records, args.asset, args.resolution, kind)
        target = out_dir / f"{args.asset}_{kind}_{args.resolution}.jpg"
        downloaded = download(record, target)
        downloaded["api_tree_path"] = list(path)
        selected[kind] = downloaded
        print(f"{args.asset} {kind}: {record['url']} -> {target}")

    manifest = {
        "asset_id": args.asset,
        "name": info.get("name", args.asset),
        "authors": info.get("authors", {}),
        "canonical_page": f"https://polyhaven.com/a/{args.asset}",
        "api_files_url": files_url,
        "api_info_url": info_url,
        "files_hash": info.get("files_hash"),
        "license": "CC0-1.0",
        "requested_resolution": args.resolution,
        "maps": selected,
    }
    (out_dir / f"{args.asset}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
