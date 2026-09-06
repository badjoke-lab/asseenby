# AsSeenBy — Spatial Pilot Schedule

## Current state
PR #4 — **draft / rendered acceptance passed / final clean-head regression before merge**
Branch: `feat/spatial-night-low-light`

The public main branch currently uses the accepted fixed-viewpoint 360° photographic night-city reference with Normal, Tunnel Vision, Central Loss, and Cataract-like comparison modes. PR #4 adds the accepted Night / Low Light candidate while preserving the separate image comparison experience.

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

## Step 12 — Night / Low Light evidence boundary and renderer
Status: **PASS / accepted / pending merge**

Implementation candidate commit: `0aa83861be18d6ac77457ebe7032637aa6525944`.
Patch/build workflow `34008903572` passed, including `npm ci` and `npm run build`.
PR build `34009020573` passed on the rendered-review head.
Chromium rendered review `34009009894` passed technically with `result.json` reporting no failures.

Evidence/source-data boundary:
- low-light vision involves a shift toward rod contribution, reduced color information, and lower spatial resolution at sufficiently low luminance;
- dark adaptation is time-dependent rather than an instant filter;
- the current Hansaplatz source is a tone-mapped RGB panorama, not calibrated scene photometry;
- this phase therefore uses relative displayed luminance only and does not claim physical scotopic/mesopic reconstruction.

Renderer behavior accepted in manual review:
- darker rendered regions lose substantially more chromatic separation, contrast and fine detail than the Normal view;
- bright shopfronts, windows and lamps remain comparatively available instead of being uniformly blacked down;
- the forward comparison clearly differs from Normal without collapsing into a uniform dark or blue tint;
- the turned view contains a different bright/dark composition and the renderer follows that composition while preserving the exact camera direction;
- the effect reads as loss of low-light information rather than simply lowering the whole image brightness;
- 390px mobile keeps the five spatial controls usable, preserves the same-view comparison, and the automated check reports no horizontal overflow or captured page/console errors;
- accepted Normal, Tunnel Vision, Central Loss and Cataract-like regressions plus the separate image workflow remain green.

Spatial Model remains **C** because the renderer uses relative displayed luminance from tone-mapped RGB rather than calibrated scene photometry or a validated physiological observer model.

## Ordered next spatial candidates
1. Dog-like
2. Cat-like
3. Bird-like as a separate evaluation
4. Bee-like only with additional UV-reflectance scene data

## Final merge gate
Run the existing full build and desktop / 390px Chromium regression once more on this accepted documentation head. If both are green, mark PR #4 ready and squash-merge it. Do not begin Dog-like before that merge completes.
