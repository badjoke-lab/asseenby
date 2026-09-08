# QR1 Authored World Proof

Status: in verification

This document records the acceptance evidence required before QR1 can be closed.

## Required runtime proof

- Night Intersection starts with the central `c0` authored chunk inside load radius.
- `c0` mounts at least one repository-hosted glTF/PBR asset through `SpatialAssetRuntime`.
- The renderer exposes `data-scene-loaded-chunks` and `data-scene-authored-asset-root-count` diagnostics for automated verification.
- Switching from Night Intersection to the 360° Photo Reference removes authored chunk roots.
- Returning to Night Intersection remounts `c0` and its authored asset.
- Observer position changes are forwarded into `SpatialSceneRuntime.updateObserverPosition`, so load/unload decisions follow the actual observer position rather than remaining disconnected.
- Desktop and mobile browser checks must complete without page errors or console errors.

## Current bootstrap asset

The first runtime proof asset is Poly Haven `Street Lamp 02`, exported by Blender's Khronos glTF I/O, redistributed under CC0-1.0, and hosted locally under `public/assets/3d/night-intersection/c0/`.

This asset is a QR1 pipeline/runtime proof only. It does **not** close QR2 close-range scene quality. QR2 requires a Blender-authored C0 environment whose primary visible geometry no longer reads as procedural/debug/cheap low-poly at inspection distance.

## QR1 close condition

QR1 is closed only after the branch build and spatial browser run both succeed with the authored chunk lifecycle assertions enabled. Until then, status remains `in verification`.
