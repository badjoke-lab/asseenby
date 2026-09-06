# AsSeenBy — Spatial Pilot Schedule

## Current state
PR #6 — **Cat-like spatial rejection recorded / final clean-head regression before merge**
Branch: `feat/spatial-cat-like`

Dog-like is merged on main as `5bdd0d39f963b498fcf2f7f379f07b50adf79e25`; post-merge main build `34009808490` passed. Cat-like candidate browser run `34010239767` passed technically, but manual same-camera review rejected the spatial mode as insufficiently distinct from Dog-like without unsupported assumptions. Rejection/cleanup commit `2497db8d6143c13155be4b477e3ec017216549d4` contains no Cat-like spatial renderer/control changes; patch/build workflow `34010475440` passed.

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

## Step 13 — Dog-like
Status: **PASS / accepted / merged**

Rendered review `34009491932` passed and was manually accepted. Final clean-head build `34009690754` and browser regression `34009688930` passed. PR #5 was squash-merged to main as `5bdd0d39f963b498fcf2f7f379f07b50adf79e25`; post-merge main build `34009808490` passed.

Dog-like remains a human-display visible-range dichromatic/acuity proxy with spatial Model C. It does not claim exact canine cone catches, breed-dependent field of view, motion processing, tapetal/rod low-light reconstruction, or literal canine qualia.

## Step 14 — Cat-like spatial evaluation
Status: **REJECTED after rendered review**

Candidate implementation `dd6df2295f2e3efe480913035a6db3da116ae3ee` built successfully in patch workflow `34010195587`. PR build `34010245847` passed. Chromium browser run `34010239767` also passed with `result.json` reporting no browser failures, overflow, page errors, or console errors.

Manual same-camera review compared Normal / Dog-like / Cat-like in forward and turned desktop views plus the 390px mobile Cat-like view. The Cat-like candidate remained coherent and technically usable, but its visible separation from Dog-like was primarily a modest further desaturation/chromatic compression and slightly stronger fine-detail softening.

Decision: **reject the spatial Cat-like control**. The current RGB panorama and evidence boundary do not justify inventing a stronger feline-specific visual distinction merely to make the modes look different. The existing image-track Cat-like approximation remains separately available and conservatively labeled.

The rejected candidate was removed before the merge head. Comparison against main contains documentation/evidence updates only; no Cat-like shader, spatial evidence branch, control, or browser capture addition remains. Cleanup build `34010475440` passed.

## Step 15 — Bird-like evidence/source-data boundary
Status: **next / not yet implemented**

Before any Bird-like renderer is added, determine which avian characteristics can be represented from the current tone-mapped RGB panorama and which require additional spectral/UV scene data. Many avian visual systems involve four cone classes, ultraviolet/violet sensitivity, species-specific oil-droplet filtering and other properties that ordinary RGB cannot reconstruct.

Acceptance rule for beginning implementation:
- a candidate must have a documented visible-range component that is both supported and meaningfully different from simply increasing saturation/contrast;
- missing UV/tetrachromatic information must not be fabricated from RGB;
- if the current source cannot support a useful non-misleading Bird-like spatial comparison, record the mode as rejected/blocked instead of implementing a decorative filter.

## Ordered next spatial candidates
1. Bird-like evidence/source-data evaluation
2. Bee-like only with additional UV-reflectance scene data

## Final merge gate
Run the existing PR build and full desktop / 390px Chromium regression on this clean rejection/documentation head. If both are green, mark PR #6 ready and squash-merge it. Then begin Bird-like evidence/source-data evaluation from the new main.
