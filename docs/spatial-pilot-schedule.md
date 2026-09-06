# AsSeenBy — Spatial Pilot Schedule

## Current state
Branch: `feat/spatial-central-loss`
PR: `#3` — **draft / blocked on scene quality review**

The existing public product remains the v0.1 static-image comparison tool. The spatial track is additive. The initial Normal / Tunnel Vision / Cataract-like renderer is on main, while Central Loss and the scene-presentation rebuild remain isolated in PR #3.

## Execution rule
At the start of every spatial step, re-read `AGENTS.md`, `docs/spatial-pilot-spec.md`, this schedule, and the relevant methodology / limitation / evidence documents. A step is not complete until its rendered acceptance conditions are met.

## Steps 0–8 — Initial spatial pilot
Status: **complete / merged**

- PR #2 merged at `d3673db84864e5441951cac3be51dd01cf77602e`.
- main post-merge build `34000040892` passed.
- Three.js fixed-position look-around, Tunnel Vision and scene-dependent Cataract-like were functionally accepted.
- Later user-visible review showed that the original primitive street itself was not presentation-quality. That presentation defect blocks further spatial expansion.

## Step 9 — Central Loss definition and evidence boundary
Status: **complete**

- Central Loss is the only new spatial mode in this phase.
- The disrupted center is screen/view-relative and follows straight-ahead vision while the camera turns.
- Surrounding scene information remains more available than central detail.
- The model is generic and educational, not patient perimetry or a measured individual scotoma.
- Spatial Model confidence remains conservative at C until final rendered review.

## Step 10 — Central Loss live renderer
Status: **functionally complete / not accepted**

Already passed functional checks:
- implementation workflow `34000391905`;
- PR build `34000459038`;
- Chromium browser validation `34000441484`.

Central Loss is still blocked because the surrounding spatial reference scene must pass the presentation gate first.

## Step 10A — Spatial reference scene presentation rebuild
Status: **v5 implemented / rendered review running / blocking**

### Original through v3
Result: **FAIL**.

The first public screenshot read as a sparse prototype. v1–v3 progressively added facade detail, side-view architecture, procedural textures, better vehicle/pedestrian geometry, shadows and lighting. Browser checks passed technically, but rendered review still showed a self-built low-poly/procedural scene rather than a convincing environment.

### v4 — real CC0 building assets
Commit `61ce2e103d745fe9e1c2590dc4faa81dd633640c`; corrected build workflow `34007002239` passed.

Three Quaternius Downtown City MegaKit GLB buildings were bundled locally and integrated with `GLTFLoader`. The forward view improved, but rendered review still failed the product-quality test: the scene retained primitive foreground geometry and side turns still read like looking at stage-set facades rather than inhabiting a real place. **v4 rejected.**

### v5 — photographic 360° reference stimulus
Commit `b194bd652ee67340140e52675d6956d9b0993464`; patch/build workflow `34007320447` passed.

Decision: stop spending effort trying to make a fixed-position perception pilot look realistic through hand-built geometry. Because this pilot allows rotation but no camera translation, a real equirectangular 360° photographic stimulus is a better technical and perceptual fit than fake geometry.

Implemented:
- locally bundled Poly Haven `Hansaplatz` tonemapped 360° panorama;
- source author/license note bundled beside the asset;
- source is CC0 and does not require a runtime CDN;
- Three.js now uses the panorama as an equirectangular scene background;
- the camera remains fixed and only direction changes;
- existing screen-relative Tunnel Vision / Central Loss / Cataract-like passes remain unchanged;
- primitive procedural street geometry is no longer instantiated for the active reference scene;
- UI copy no longer claims the active reference stimulus is a literal 3D street; it is described as a spatial / 360° photographic reference scene.

Why this is not a shortcut:
- the current interaction never translates the camera, so parallax from scene geometry was not being used;
- the perception effects under test are screen/view-relative and operate correctly on the photographic stimulus;
- real architecture, lighting, material detail, depth cues, signage and 360° coverage now come from one coherent captured environment instead of hand-built approximations;
- future modes that genuinely require geometric depth or camera translation must introduce a separate depth/geometry requirement rather than pretending the panorama supplies it.

### v5 rendered acceptance questions
1. Does Normal immediately read as a real night-city environment rather than a prototype scene?
2. Do forward, right-turn and opposite-turn views all remain visually rich and coherent?
3. Do bright shopfronts/streetlights and dark sky/streets provide useful high-contrast targets for Cataract-like and field-loss comparison?
4. Do Tunnel Vision, Cataract-like and Central Loss still work without camera reset or source-scene mutation?
5. Does 390px mobile remain usable with touch look-around and no horizontal overflow or page/console errors?
6. Does the photographic source remove the low-poly / stage-set problem that caused the original rejection?
7. Is the result good enough to show publicly without apologizing for the environment quality?

All seven must pass. Build success alone is insufficient.

## Step 11 — Central Loss rendered acceptance
Status: **blocked by Step 10A rendered review**

After the v5 scene passes:
- compare Normal vs Central Loss at the identical forward view;
- compare the identical turned view;
- verify the disrupted center follows the viewer rather than a world-space object;
- repeat with real mobile touch input;
- confirm existing image workflow and accepted spatial modes still pass;
- confirm active scanning explains central loss more clearly than another transformed still.

Only after this gate passes may PR #3 become ready and merge.

## Ordered next spatial candidates after Central Loss
1. Night / Low Light
2. Dog-like
3. Cat-like
4. Bird-like as a separate evaluation
5. Bee-like only with additional UV-reflectance scene data

## Current next action
Run the full desktop / 390px Chromium capture on the v5 panorama-backed head, inspect forward and both horizontal directions plus Central Loss / Cataract-like output, then either reject again or mark Step 10A passed. Do not begin Night / Low Light yet.
