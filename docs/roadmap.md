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
Status: **accepted / merged**

Dog-like passed same-camera desktop/mobile rendered review and is now part of the accepted spatial set. It remains a conservative human-display visible-range dichromatic/acuity proxy, not a complete canine visual reconstruction.

## Spatial evaluation — Cat-like
Status: **rejected after rendered review**

A conservative Cat-like candidate was implemented and compared against Normal and Dog-like on the same 360° camera states. Browser regression passed, but the visible difference from Dog-like was dominated by slightly lower chroma and slightly stronger softening. Keeping a separate spatial Cat-like control would therefore imply a species-specific distinction that the current RGB source and evidence boundary do not justify strongly enough.

The image-track Cat-like mode remains available as an explicitly cautious visible-range approximation. The rejected spatial candidate is not added to the public spatial controls.

## Spatial evaluation — Bird-like
Status: **active next evaluation**

Goal:
Determine whether an honest Bird-like spatial comparison is possible from the current tone-mapped RGB panorama, and reject it rather than inventing ultraviolet/tetrachromatic information if the source data is insufficient.

Required evaluation:
- review avian cone classes, ultraviolet/violet sensitivity, oil-droplet filtering and species variation;
- separate what can be communicated from ordinary RGB from what requires spectral/UV scene data;
- do not treat saturation or contrast boost as a sufficient Bird-like simulation;
- preserve the exact camera/source scene for any candidate that survives the evidence boundary;
- require rendered explanatory value beyond a decorative filter before adding a public control.

## Ordered next spatial candidates
1. Bird-like evidence/source-data evaluation;
2. Bee-like only with additional UV-reflectance scene data.

## Near-term priority order
1. define the Bird-like spectral/source-data boundary;
2. decide whether the current RGB panorama supports any non-misleading spatial Bird-like renderer;
3. if yes, implement one restrained candidate and run same-camera desktop/mobile review;
4. if no, record Bird-like as rejected/blocked rather than faking missing UV/tetrachromatic information;
5. do not begin Bee-like until Bird-like is resolved.
