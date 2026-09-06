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
- Three.js `Explore 3D`, fixed-position look-around, Tunnel Vision and scene-dependent Cataract-like were functionally accepted.
- Later user-visible review showed that the original primitive street itself was not presentation-quality. That presentation defect now blocks further spatial expansion.

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

Central Loss is still blocked because the surrounding 3D scene must pass the presentation gate first.

## Step 10A — Night-street presentation rebuild
Status: **v4 implemented / rendered review now running / blocking**

### Original scene review
Result: **FAIL**.
The first public screenshot read as a sparse prototype: bare dark building boxes, crude car, mannequin pedestrian, flat surfaces, weak lighting hierarchy and little useful side-view information.

### v1
Commit `1ffd3dcfdfcf6497ae2059f42c354974350c1100`; build workflow `34006118735` passed.

Added facade/window/storefront details, road/sidewalk detail, improved vehicle and pedestrian, street furniture, distant layers and stronger lighting.

Rendered result: **FAIL** because turning away from the forward view exposed mostly empty darkness.

### v2
Commit `2ec9a883aae7c24a80d78e369643e294a3fc19e7`; build workflow `34006314644` passed.

Added near-camera architecture, NIGHT MARKET storefront, apartment entrance, bench, scooter, side-facing windows and procedural asphalt/concrete/brick/plaster textures.

Rendered result: improved side views, but still visibly procedural / primitive-heavy and not accepted as public quality.

### v3
Commit `54daffe36aa49e9882e90387834cbd701e6b6295`; build workflow `34006591840` passed. Browser review `34006654513` passed technically.

Added:
- soft PCF shadows;
- gradient night sky;
- rounded vehicle body / lamps / tail lights;
- more organic pedestrian limbs;
- explicit screenshots for both horizontal look-around directions.

Rendered result: both directions now contain useful street structure, but the scene still reads too strongly as self-built primitive geometry. **Not accepted.**

### v4 — real CC0 building assets
Commit `61ce2e103d745fe9e1c2590dc4faa81dd633640c`.

The first v4 attempt failed only because an unnecessary Meshopt decoder import did not match the installed Three.js typings. The three building downloads themselves succeeded. The source asset's own implementation uses ordinary `GLTFLoader`, so the decoder dependency was removed.

Corrected v4 workflow `34007002239` passed:
- downloaded and locally bundled three optimized Quaternius Downtown City MegaKit GLB buildings;
- bundled the Quaternius license file;
- integrated the models with local `/assets/models/...` URLs using `GLTFLoader`;
- retained local procedural street, vehicle, pedestrian and perception-test targets;
- enabled shadows on loaded meshes;
- `npm ci` and `npm run build` passed.

Asset-backed head before this schedule trigger: `61ce2e103d745fe9e1c2590dc4faa81dd633640c`.

### v4 rendered acceptance questions
1. Does Normal immediately read as an intentional night street rather than a primitive test corridor?
2. Do the real building assets materially improve architectural depth and silhouette quality?
3. Do forward, right-turn and opposite-turn views all contain useful environment information?
4. Are the vehicle, pedestrian, storefront, road, sidewalk, signal and light sources still clearly readable as controlled perception targets?
5. Do Tunnel Vision, Cataract-like and Central Loss still work without camera reset or scene mutation?
6. Does 390px mobile remain usable, with no horizontal overflow or captured page/console errors?
7. Is the result good enough to show publicly without explaining that it is merely a technical prototype?

All seven must pass. Build success alone is insufficient.

## Step 11 — Central Loss rendered acceptance
Status: **blocked by Step 10A rendered review**

After the asset-backed scene passes:
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
Run the full desktop / 390px Chromium capture on the v4 asset-backed head, inspect forward and both horizontal directions plus Central Loss / Cataract-like output, and either reject again or mark Step 10A passed. Do not begin Night / Low Light yet.
