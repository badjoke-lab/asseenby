# QR2 C0 Visible Core Proof

Status: rendered verification in progress

QR1 is already accepted in PR #50. This document tracks the separate QR2 visual-quality gate for the Blender-authored Night Intersection central chunk.

## Current authored candidate

- branch: `feat/blender-c0-visible-core-20260908`
- generated asset commit: `a2ac808bbd6f536f4bce756b108a5d416b08b9bd`
- canonical Blender source: `assets-src/blender/night-intersection/c0/night-intersection-c0.blend`
- canonical runtime asset: `public/assets/3d/night-intersection/c0/core/night-intersection-c0.glb`
- runtime GLB SHA-256: `537bd95942c09c89a40ef65e03b3b29abd7b887a5d0960230926270fc8727822`
- Blender build/export run: `34237808435` — success
- exported scene: 914 objects / 908 meshes

The current candidate includes the C0 road/sidewalk system, crosswalks and lane markings, four facade/storefront buildings, windows/trim/signage, rooftop equipment, street furniture, vegetation, traffic signals, a delivery van, separate collision/navigation collections, spawn anchors, and light anchors. Asphalt and brick use locally retained Poly Haven CC0 1K diffuse/normal/roughness source maps with recorded hashes.

## Runtime integration

`src/spatial/nightIntersectionWorld.ts` mounts `asseenby-night-intersection-c0-v1` as C0's primary-visible authored asset. The previous Street Lamp 02 QR1 bootstrap asset is no longer the C0 primary payload.

The current scene runtime still mounts the old procedural Night Intersection technical scene alongside the authored chunk. QR2 must not be accepted until rendered review determines which procedural responsibilities remain necessary for navigation/lighting and removes duplicate primary-visible geometry.

## Blocking rendered acceptance

QR2 remains open until representative desktop and mobile browser screenshots have been inspected. Passing build/export/runtime checks is not sufficient.

Fail QR2 if any representative ground-level Normal view still reads as placeholder/debug/cheap low-poly work, if authored and procedural primary-visible geometry overlap, or if material scale/normal response is visibly broken. The Blender exporter currently reports tangent-generation warnings on some non-tri/quad geometry; these must be resolved if they materially degrade normal-mapped surfaces.

## Required evidence before acceptance

- authored C0 GLB loads through the production Three.js runtime;
- Night Intersection -> Photo Reference -> Night Intersection unload/remount remains clean;
- Human movement/reset and Vision state behavior remain intact;
- desktop Normal forward/turned/opposite screenshots inspected;
- mobile Normal/turned screenshots inspected;
- old procedural primary-visible geometry retired where it duplicates authored C0;
- any visible UV/tangent/material defects fixed;
- final build and spatial browser check green on the PR head.
