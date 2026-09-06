# AsSeenBy — Spatial Pilot Schedule

## Current state
Branch: `feat/spatial-dog-like`
Status: **Dog-like implementation candidate awaiting rendered review**

The public main branch now includes the accepted fixed-viewpoint 360° photographic night-city reference with Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like comparison modes. The Dog-like branch is additive and preserves the separate image comparison experience.

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

## Step 12 — Night / Low Light
Status: **PASS / accepted / merged**

Rendered-review browser run `34009009894` passed and its Normal/Night forward, turned and 390px mobile captures were manually accepted. Final clean-head PR build `34009195003` and browser regression `34009192584` passed. PR #4 was squash-merged to main as `f7d57d3817e273e0ce2f63973f049b1a68cc0085`; post-merge main build `34009285466` passed.

The accepted model remains a relative displayed-luminance proxy with spatial Model C. It does not claim calibrated scotopic/mesopic reconstruction or dark-adaptation timing.

## Step 13 — Dog-like evidence boundary and renderer candidate
Status: **evidence boundary complete / implementation candidate awaiting rendered review**

Implementation candidate commit: `0c72120a5ba7fed80581c2337d06073211fa9103`.
Patch/build workflow `34009455739` passed, including `npm ci` and `npm run build`.

Evidence boundary:
- behavioral and photopigment studies strongly support canine dichromatic color vision;
- comparative studies support lower canine spatial acuity than human acuity, with meaningful individual and methodological variation;
- a standard RGB panorama cannot reconstruct exact canine cone catches for arbitrary spectra;
- breed-dependent visual field, motion processing, tapetal/rod low-light advantages and neural interpretation are excluded from this phase.

Renderer candidate:
- human-display two-channel translation compresses red/green distinctions while keeping blue/yellow-like distinctions comparatively available;
- mild angularly scaled softening reduces fine detail without claiming calibrated acuity;
- camera position, direction, field of view and source panorama remain unchanged;
- spatial Model remains C pending rendered acceptance.

Rendered gate:
- compare identical-camera Normal vs Dog-like forward and turned views;
- verify red/green compression on signs, foliage and colored lights without a generic arbitrary tint;
- verify fine-detail reduction is visible but restrained;
- verify accepted spatial modes and image comparison remain unchanged;
- verify 390px mobile, no overflow, and no captured page/console errors;
- accept, revise, or reject before beginning Cat-like.

## Ordered next spatial candidates
1. Cat-like
2. Bird-like as a separate evaluation
3. Bee-like only with additional UV-reflectance scene data

## Current next action
Run build and the existing desktop / 390px Chromium capture on the Dog-like candidate. Inspect identical-camera Normal/Dog-like forward and turned views, then either correct the renderer or mark Step 13 accepted. Do not begin Cat-like yet.
