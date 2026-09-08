"""Fetch one Poly Haven model as a self-contained local 1K glTF bundle.

Poly Haven's /files/{id} endpoint is the canonical machine-readable source for
file URLs. Model glTF records contain a primary file and an `include` mapping.
This script downloads both, verifies hashes when available, flattens the bundle
into one directory, and rewrites glTF external URIs to the local filenames.

The downloaded cache is build-time only. Blender imports the model and packs its
images into the canonical .blend source; production never depends on Poly Haven.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import urllib.parse
import urllib.request


API_BASE = "https://api.polyhaven.com"
USER_AGENT = "AsSeenBy-Explore3D/1.0 (+https://github.com/badjoke-lab/asseenby)"


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


def download(url: str, target: Path, md5: str | None = None) -> dict[str, object]:
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
    if md5 and actual_md5.lower() != md5.lower():
        target.unlink(missing_ok=True)
        raise RuntimeError(
            f"MD5 mismatch for {url}: expected {md5}, got {actual_md5}"
        )
    return {
        "source_url": url,
        "filename": target.name,
        "size": size,
        "md5": actual_md5,
        "sha256": sha256.hexdigest(),
    }


def pick_gltf(files: dict, resolution: str) -> dict:
    gltf_tree = files.get("gltf")
    if not isinstance(gltf_tree, dict) or not gltf_tree:
        raise RuntimeError("Poly Haven file tree has no gltf variants")
    preferred = [resolution, "1k", "2k", "4k"]
    selected_resolution = next((key for key in preferred if key in gltf_tree), None)
    if selected_resolution is None:
        selected_resolution = sorted(gltf_tree.keys())[0]
    block = gltf_tree.get(selected_resolution)
    if not isinstance(block, dict):
        raise RuntimeError(f"Malformed gltf resolution block: {selected_resolution}")
    record = block.get("gltf")
    if not isinstance(record, dict) or not record.get("url"):
        raise RuntimeError(f"No gltf file record at resolution {selected_resolution}")
    result = dict(record)
    result["_resolution"] = selected_resolution
    return result


def safe_filename(url: str, fallback: str) -> str:
    name = Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).name
    return name or fallback


def rewrite_external_uris(gltf_path: Path, downloaded_names: set[str]) -> None:
    document = json.loads(gltf_path.read_text(encoding="utf-8"))
    changed = False
    for section in ("buffers", "images"):
        for item in document.get(section, []):
            uri = item.get("uri")
            if not isinstance(uri, str) or uri.startswith("data:"):
                continue
            basename = Path(urllib.parse.unquote(uri)).name
            if basename not in downloaded_names:
                raise RuntimeError(
                    f"glTF dependency {uri!r} was not provided by Poly Haven includes"
                )
            if uri != basename:
                item["uri"] = basename
                changed = True
    if changed:
        gltf_path.write_text(
            json.dumps(document, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )


def main() -> None:
    args = parse_args()
    asset_id = args.asset
    out_dir = Path(args.out).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    files_url = f"{API_BASE}/files/{urllib.parse.quote(asset_id)}"
    info_url = f"{API_BASE}/info/{urllib.parse.quote(asset_id)}"
    files = get_json(files_url)
    info = get_json(info_url)
    record = pick_gltf(files, args.resolution)

    manifest_files: list[dict[str, object]] = []
    primary_url = str(record["url"])
    primary_name = safe_filename(primary_url, f"{asset_id}.gltf")
    if not primary_name.lower().endswith(".gltf"):
        primary_name = f"{asset_id}_{record['_resolution']}.gltf"
    primary_path = out_dir / primary_name
    manifest_files.append(download(primary_url, primary_path, record.get("md5")))

    includes = record.get("include") or {}
    if not isinstance(includes, dict):
        raise RuntimeError("Poly Haven glTF include field is not an object")
    downloaded_names = {primary_name}
    for include_key, include_record in sorted(includes.items()):
        if not isinstance(include_record, dict) or not include_record.get("url"):
            continue
        url = str(include_record["url"])
        name = safe_filename(url, Path(include_key).name)
        if name in downloaded_names:
            continue
        manifest_files.append(download(url, out_dir / name, include_record.get("md5")))
        downloaded_names.add(name)

    rewrite_external_uris(primary_path, downloaded_names)
    rewritten_sha = hashlib.sha256(primary_path.read_bytes()).hexdigest()

    provenance = {
        "asset_id": asset_id,
        "name": info.get("name", asset_id),
        "authors": info.get("authors", {}),
        "canonical_page": f"https://polyhaven.com/a/{asset_id}",
        "api_files_url": files_url,
        "api_info_url": info_url,
        "files_hash": info.get("files_hash"),
        "license": "CC0-1.0",
        "resolution": record["_resolution"],
        "primary_gltf": primary_name,
        "rewritten_gltf_sha256": rewritten_sha,
        "source_files": manifest_files,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Fetched Poly Haven {asset_id}: {record['_resolution']} glTF + "
        f"{len(manifest_files) - 1} dependencies -> {out_dir}"
    )
    print(primary_path)


if __name__ == "__main__":
    main()
