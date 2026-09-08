"""Extract rectilinear reconstruction references from the checked-in Hansaplatz 360° panorama.

The panorama is the real CC0 photographic ground truth for Night Intersection.
This script converts the equirectangular source into repeatable perspective plates
that can be compared against browser/Blender renders from fixed relative headings.

Usage:
  python3 scripts/reference/extract_hansaplatz_reference_views.py \
    --source public/assets/panoramas/hansaplatz.jpg \
    --out assets-src/blender/night-intersection/reference/hansaplatz
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


REFERENCE_VIEWS = (
    ("yaw-000", 0.0, 0.0),
    ("yaw-060", 60.0, 0.0),
    ("yaw-120", 120.0, 0.0),
    ("yaw-180", 180.0, 0.0),
    ("yaw-240", 240.0, 0.0),
    ("yaw-300", 300.0, 0.0),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--fov", type=float, default=82.0)
    return parser.parse_args()


def normalize(values: np.ndarray) -> np.ndarray:
    lengths = np.linalg.norm(values, axis=-1, keepdims=True)
    return values / np.maximum(lengths, 1e-9)


def rotate_yaw_pitch(rays: np.ndarray, yaw_deg: float, pitch_deg: float) -> np.ndarray:
    yaw = np.deg2rad(yaw_deg)
    pitch = np.deg2rad(pitch_deg)

    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)

    # Camera looks down -Z. Apply pitch around local X, then yaw around world Y.
    x = rays[..., 0]
    y = rays[..., 1] * cp - rays[..., 2] * sp
    z = rays[..., 1] * sp + rays[..., 2] * cp

    xr = x * cy + z * sy
    yr = y
    zr = -x * sy + z * cy
    return np.stack((xr, yr, zr), axis=-1)


def perspective_to_equirectangular(
    source: np.ndarray,
    width: int,
    height: int,
    fov_deg: float,
    yaw_deg: float,
    pitch_deg: float,
) -> np.ndarray:
    source_h, source_w, _ = source.shape
    aspect = width / height
    tan_half_h = np.tan(np.deg2rad(fov_deg) / 2.0)
    tan_half_v = tan_half_h / aspect

    xs = (np.arange(width, dtype=np.float32) + 0.5) / width * 2.0 - 1.0
    ys = 1.0 - (np.arange(height, dtype=np.float32) + 0.5) / height * 2.0
    grid_x, grid_y = np.meshgrid(xs * tan_half_h, ys * tan_half_v)
    rays = normalize(np.stack((grid_x, grid_y, -np.ones_like(grid_x)), axis=-1))
    rays = rotate_yaw_pitch(rays, yaw_deg, pitch_deg)

    lon = np.arctan2(rays[..., 0], -rays[..., 2])
    lat = np.arcsin(np.clip(rays[..., 1], -1.0, 1.0))

    src_x = (lon / (2.0 * np.pi) + 0.5) * source_w
    src_y = (0.5 - lat / np.pi) * source_h

    x0 = np.floor(src_x).astype(np.int32) % source_w
    x1 = (x0 + 1) % source_w
    y0 = np.clip(np.floor(src_y).astype(np.int32), 0, source_h - 1)
    y1 = np.clip(y0 + 1, 0, source_h - 1)

    wx = (src_x - np.floor(src_x))[..., None]
    wy = (src_y - np.floor(src_y))[..., None]

    top = source[y0, x0] * (1.0 - wx) + source[y0, x1] * wx
    bottom = source[y1, x0] * (1.0 - wx) + source[y1, x1] * wx
    sampled = top * (1.0 - wy) + bottom * wy
    return np.clip(sampled, 0, 255).astype(np.uint8)


def main() -> None:
    args = parse_args()
    source_path = Path(args.source)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(source_path) as image:
        source_image = image.convert("RGB")
        source = np.asarray(source_image, dtype=np.float32)
        source_size = [source_image.width, source_image.height]

    outputs = []
    for name, yaw, pitch in REFERENCE_VIEWS:
        pixels = perspective_to_equirectangular(
            source,
            args.width,
            args.height,
            args.fov,
            yaw,
            pitch,
        )
        output_path = out_dir / f"{name}.jpg"
        Image.fromarray(pixels, mode="RGB").save(output_path, quality=92, optimize=True)
        outputs.append({
            "id": name,
            "file": output_path.name,
            "yaw_degrees_relative": yaw,
            "pitch_degrees_relative": pitch,
            "horizontal_fov_degrees": args.fov,
            "size": [args.width, args.height],
        })
        print(f"wrote {output_path}")

    manifest = {
        "reference_id": "polyhaven-hansaplatz",
        "role": "canonical photographic reconstruction reference for Night Intersection",
        "source_local": str(source_path),
        "source_canonical": "https://polyhaven.com/a/hansaplatz",
        "creator": "Greg Zaal",
        "license": "CC0-1.0",
        "source_equirectangular_size": source_size,
        "orientation_note": "Yaw values are relative to the checked-in equirectangular image seam; they are not asserted geographic bearings.",
        "views": outputs,
    }
    (out_dir / "reference-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
