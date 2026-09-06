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
Status: **rejected / blocked at evidence-source gate**

Evidence review found no defensible generic Bird-like spatial renderer for the current Hansaplatz source.

Why:
- many birds use four single-cone classes plus oil-droplet spectral filtering, with ultraviolet-sensitive (UVS) and violet-sensitive (VS) systems that ordinary RGB does not encode;
- the fourth avian color dimension cannot be reconstructed from three human-camera RGB channels after spectral information has been collapsed;
- avian visual acuity varies by roughly two orders of magnitude across measured species, so a generic sharpen/blur rule would not describe “bird vision” coherently;
- temporal resolution, retinal specializations, field of view and ecology also vary substantially across species;
- the former image Bird-like behavior was only a visible-range saturation/microcontrast proxy; R7 removed it rather than preserve a generic avian claim that the RGB source cannot support.

Decision:
Do not add a Bird-like spatial control or shader from the current RGB panorama. A future avian spatial mode must be species-specific and/or use additional spectral/UV source data with a documented observer model.

## Spatial evaluation — Bee-like
Status: **blocked by missing UV-reflectance scene data**

The current panorama contains no UV-reflectance/spectral channel. Honeybee UV/blue/green photoreceptor behavior therefore cannot be reconstructed honestly from the current RGB source. No Bee-like spatial shader is started.

A future Bee-like phase requires:
- a UV-capable or measured spectral/UV scene source;
- documented mapping from bee photoreceptor catches to a human-display false-color representation;
- explicit handling of the fact that the human display cannot literally emit the bee perceptual dimensions being modeled.

## Spatial post-pilot status
The ordered animal expansion is **complete under the current RGB source-data boundary**:
- Dog-like — accepted;
- Cat-like — rejected after rendered review;
- Bird-like — rejected/blocked at evidence/source-data gate;
- Bee-like — blocked pending UV-reflectance/spectral scene data.

No additional generic animal spatial filter should be added merely to fill out the image-mode list.

## Near-term priority order
1. keep the accepted spatial set stable and regression-covered;
2. return active product work to image-transform quality, responsive/release polish, and evidence accuracy;
3. reopen species-specific spatial work only when a new source-data/model requirement is explicitly accepted.
