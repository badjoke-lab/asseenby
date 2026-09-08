# QR1 Authored World Proof

Status: accepted

QR1 was accepted and merged in PR #50. Merge SHA: `f5e66e8ecaf7533039f466edbafe575a07b6b90b`.

Acceptance evidence on the final PR head `f340d01e704babd5f6c3446a17d48f2aab5ae1f2`:

- build run `34234208798`: success
- spatial browser check run `34234208806`: success

## Accepted runtime proof

- Night Intersection starts with the central `c0` authored chunk inside load radius.
- `c0` mounts a repository-hosted glTF/PBR asset through `SpatialAssetRuntime`.
- The renderer exposes `data-scene-loaded-chunks` and `data-scene-authored-asset-root-count` diagnostics for automated verification.
- The browser test asserts the authored lifecycle: Night Intersection mounts `c0` -> switching to the 360° Photo Reference removes authored chunk roots -> returning to Night Intersection remounts `c0`.
- Observer position changes are forwarded into `SpatialSceneRuntime.updateObserverPosition`, so load/unload decisions follow the actual observer position rather than remaining disconnected.
- Desktop and mobile browser validation completed without page or console failures on the accepted run.

## Current bootstrap asset

The first runtime proof asset is Poly Haven `Street Lamp 02`, exported by Blender's Khronos glTF I/O, redistributed under CC0-1.0, and hosted locally under `public/assets/3d/night-intersection/c0/`.

This asset closes the QR1 pipeline/runtime proof only. It does **not** close QR2 close-range scene quality. QR2 requires a Blender-authored C0 environment whose primary visible geometry no longer reads as procedural/debug/cheap low-poly at inspection distance.

## Next gate

QR2 replaces the temporary procedural primary-visible C0 world with a dense Blender-authored environment, then proves close-range visual quality on desktop and mobile before Dog, Cat, or Bird observer work resumes.
