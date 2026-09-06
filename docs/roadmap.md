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

## Spatial expansion — Dog-like
Status: **active**

Goal:
Add a conservative visible-range canine comparison to the live 360° scene using two well-supported differences from human vision: dichromatic color discrimination and lower spatial acuity.

Required characteristics:
- compress red/green distinctions into a human-display two-channel translation while keeping blue/yellow-like distinctions more available;
- soften fine detail without claiming a calibrated acuity value for an individual dog;
- preserve exact camera position, direction, scene and field of view when switching modes;
- explicitly state that standard RGB cannot reconstruct canine cone catches for arbitrary real spectra;
- do not add breed-dependent field-of-view claims, motion sensitivity, tapetal/rod low-light advantages, or neural interpretation without source data and a separate validated model;
- renderer-specific Model assessment remains separate from the 2D transform;
- desktop/mobile rendered acceptance is required before merge.

## Ordered next spatial candidates
After the active Dog-like phase:
1. Cat-like;
2. Bird-like separate evaluation;
3. Bee-like only with additional UV-reflectance scene data.

## Near-term priority order
1. define the Dog-like spectral/acuity boundary for RGB input;
2. implement the conservative dichromatic + soft-detail spatial pass;
3. run build plus desktop/mobile browser regression;
4. inspect same-camera Normal / Dog-like comparisons across multiple view directions;
5. verify red/green compression and detail loss are visible without overclaiming canine perception;
6. accept, correct, or reject Dog-like before Cat-like begins.
