# AsSeenBy — Roadmap

## Current state
The repository contains the Vite + React + TypeScript static-image comparison product, browser-side image transforms, evidence metadata, and an accepted additive Three.js spatial baseline.

The existing image MVP remains the product baseline. The initial spatial pilot has passed and is merged on main; post-pilot spatial modes are now evaluated one at a time under `docs/spatial-pilot-spec.md` and `docs/spatial-pilot-schedule.md`.

## Image track
Current priorities remain:
- build reliability
- content wiring
- transform quality
- responsive / release polish

The image track remains browser-side, static-image based, and independent of the spatial renderer.

## Spatial track — accepted baseline
Status: **initial pilot accepted and merged**

Accepted:
- one controlled night-street / street-corner scene;
- Normal baseline;
- Tunnel Vision live view-relative simulation;
- Cataract-like scene-dependent glare / haze simulation;
- same camera position and direction when switching modes;
- evidence / limitation integration;
- desktop and mobile interaction;
- existing image regression coverage.

The word `approximation` remains a scientific/product claim boundary. It does not mean the 3D implementation should be a simple static screen filter.

## Spatial expansion — Central Loss
Status: **active**

Goal:
Add a live view-relative Central Loss mode to the accepted scene and verify that active scanning explains central field disruption more clearly than another transformed still image.

Required characteristics:
- straight-ahead detail is more degraded than surrounding scene information;
- the affected region stays in the viewer's central field while the camera turns;
- mode switching preserves camera and scene state;
- generic educational model only, not patient-specific scotoma reconstruction;
- renderer-specific Model assessment remains separate from the 2D transform;
- desktop/mobile rendered acceptance is required before merge.

## Ordered next spatial candidates
Only after Central Loss acceptance:
1. Night / Low Light;
2. Dog-like;
3. Cat-like;
4. Bird-like separate evaluation;
5. Bee-like only with additional UV-reflectance scene data.

## Near-term priority order
1. complete Central Loss documentation boundary;
2. implement Central Loss as a live view-relative spatial pass;
3. run build plus desktop/mobile browser regression;
4. inspect same-camera rendered comparisons;
5. accept/correct/reject Central Loss;
6. begin Night / Low Light only after Central Loss integration.
