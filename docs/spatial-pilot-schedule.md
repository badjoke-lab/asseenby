# AsSeenBy — Spatial Pilot Schedule

## Current state
PR #3 — **merged / complete**
Merge commit: `48dbda797ac287170dc02444771e8ee0ce1e38d0`

The public spatial track now uses the accepted fixed-viewpoint 360° photographic night-city reference with Normal, Tunnel Vision, Central Loss, and Cataract-like comparison modes. Image comparison remains available separately.

## Execution rule
At the start of every spatial step, re-read `AGENTS.md`, `docs/spatial-pilot-spec.md`, this schedule, and the relevant methodology / limitation / evidence documents. A step is not complete until its rendered acceptance conditions are met.

## Steps 0–8 — Initial spatial pilot
Status: **complete / merged**

- PR #2 merged at `d3673db84864e5441951cac3be51dd01cf77602e`.
- Three.js fixed-position look-around, Tunnel Vision and scene-dependent Cataract-like were functionally established.
- Later rendered review rejected the primitive street itself as a presentation baseline, so subsequent expansion was blocked until the scene was replaced.

## Step 9 — Central Loss definition and evidence boundary
Status: **complete**

- Central Loss is screen/view-relative and follows straight-ahead vision while the view rotates.
- Surrounding scene information remains more available than central detail.
- It is a generic educational model, not patient perimetry or a measured individual scotoma.
- Spatial Model confidence remains conservative at C.

## Step 10 — Central Loss live renderer
Status: **complete / accepted**

Functional validation passed and mode switching preserves the exact viewing direction. The affected region is viewer-relative rather than attached to a world-space target.

## Step 10A — Spatial reference scene presentation rebuild
Status: **PASS / accepted**

### Rejected approaches
- Original through v3: hand-built procedural scene remained visibly low-poly / prototype-like.
- v4: real CC0 building GLBs improved the forward view but still read as a stage-set environment because primitive foreground geometry remained.

### Accepted v5 approach
The active scene was replaced with a locally bundled Poly Haven `Hansaplatz` tonemapped 360° panorama. The source/license note is stored beside the asset and runtime has no external CDN dependency.

This fits the current pilot because the camera rotates but does not translate. No geometric parallax is required by the accepted interaction. Future features that require camera translation or depth-dependent effects must add an explicit depth/geometry requirement.

Rendered review confirmed:
- forward, turned and opposite directions all read as one coherent real night-city environment;
- architecture, storefronts, streetlights, dark sky and near/far detail remain useful across view directions;
- the original primitive / low-poly / stage-set presentation failure is gone;
- desktop and 390px mobile remain usable;
- bright and dark regions remain useful for field-loss and Cataract-like comparisons.

Cleanup workflow `34007582142` passed and removed the dead primitive scene implementation, obsolete GLB assets/imports and obsolete user-facing `3D renderer` wording.

## Step 11 — Central Loss rendered acceptance
Status: **PASS / accepted / merged**

Final clean-head Chromium regression `34007622720` passed. Review confirmed that Central Loss remains centered in the viewer's field after rotation and mobile touch look-around, while surrounding information remains more available. The model remains generic and restrained.

PR build `34007624784` passed. PR #3 was then squash-merged to main as `48dbda797ac287170dc02444771e8ee0ce1e38d0`. Main build `34007765671` passed.

## Ordered next spatial candidates
1. Night / Low Light
2. Dog-like
3. Cat-like
4. Bird-like as a separate evaluation
5. Bee-like only with additional UV-reflectance scene data

## Current next action
Begin `Night / Low Light` as a separate evaluated mode. First define its evidence boundary and what the current photographic reference can and cannot support before implementing a shader. Do not alter the accepted reference scene merely to force the new mode to work.
