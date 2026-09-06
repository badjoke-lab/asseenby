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

## Spatial expansion — Night / Low Light
Status: **active**

Goal:
Add a scene-luminance-dependent low-light comparison that becomes more restrictive in darker rendered regions while preserving the same camera and photographic reference scene.

Required characteristics:
- darker regions lose more color separation, contrast, and fine detail than bright regions;
- the effect uses the currently rendered view rather than a uniform global tint;
- mode switching preserves camera and source-scene state;
- the model is explicitly a display-luminance proxy, not calibrated scotopic/mesopic photometry;
- no dark-adaptation timing or patient-specific night-vision claim;
- renderer-specific Model assessment remains separate from the 2D transform;
- desktop/mobile rendered acceptance is required before merge.

## Ordered next spatial candidates
After the active Night / Low Light phase:
1. Dog-like;
2. Cat-like;
3. Bird-like separate evaluation;
4. Bee-like only with additional UV-reflectance scene data.

## Near-term priority order
1. define the Night / Low Light scientific and source-data boundary;
2. implement the luminance-dependent spatial pass;
3. run build plus desktop/mobile browser regression;
4. inspect same-camera Normal / Night comparisons across bright and dark view directions;
5. accept, correct, or reject the spatial mode;
6. begin Dog-like only after Night / Low Light is resolved.
