# AsSeenBy — Spatial Pilot Schedule

## Current state
Branch: `feat/spatial-central-loss`
PR: `#3` — **draft / final clean-head regression before merge**

The existing public product remains the v0.1 static-image comparison tool. The spatial track is additive. The initial Normal / Tunnel Vision / Cataract-like renderer is on main, while Central Loss and the accepted photographic spatial reference remain isolated in PR #3 until the final regression passes.

## Execution rule
At the start of every spatial step, re-read `AGENTS.md`, `docs/spatial-pilot-spec.md`, this schedule, and the relevant methodology / limitation / evidence documents. A step is not complete until its rendered acceptance conditions are met.

## Steps 0–8 — Initial spatial pilot
Status: **complete / merged**

- PR #2 merged at `d3673db84864e5441951cac3be51dd01cf77602e`.
- main post-merge build `34000040892` passed.
- Three.js fixed-position look-around, Tunnel Vision and scene-dependent Cataract-like were functionally accepted.
- Later user-visible review showed that the original primitive street itself was not presentation-quality. That presentation defect was treated as blocking rather than accepted as a final visual baseline.

## Step 9 — Central Loss definition and evidence boundary
Status: **complete**

- Central Loss is the only new spatial mode in this phase.
- The disrupted center is screen/view-relative and follows straight-ahead vision while the camera turns.
- Surrounding scene information remains more available than central detail.
- The model is generic and educational, not patient perimetry or a measured individual scotoma.
- Spatial Model confidence remains conservative at C.

## Step 10 — Central Loss live renderer
Status: **complete / rendered acceptance passed**

Functional validation:
- implementation workflow `34000391905` passed;
- PR build `34000459038` passed;
- initial Chromium validation `34000441484` passed.

The implementation preserves camera direction across mode switching and keeps the disrupted region screen/view-relative rather than attached to a world-space target.

## Step 10A — Spatial reference scene presentation rebuild
Status: **PASS / accepted**

### Original through v3
Result: **FAIL**.

The first public screenshot read as a sparse prototype. v1–v3 progressively added facade detail, side-view architecture, procedural textures, better vehicle/pedestrian geometry, shadows and lighting. Browser checks passed technically, but rendered review still showed a self-built low-poly/procedural scene rather than a convincing environment.

### v4 — real CC0 building assets
Commit `61ce2e103d745fe9e1c2590dc4faa81dd633640c`; corrected build workflow `34007002239` passed.

Three Quaternius Downtown City MegaKit GLB buildings were bundled locally and integrated with `GLTFLoader`. The forward view improved, but rendered review still failed the product-quality test: primitive foreground geometry remained and side turns still read like stage-set facades rather than inhabiting a coherent real place. **v4 rejected.**

### v5 — photographic 360° reference stimulus
Core scene commit `b194bd652ee67340140e52675d6956d9b0993464`; patch/build workflow `34007320447` passed.

The active scene was changed from hand-built geometry to a locally bundled Poly Haven `Hansaplatz` tonemapped 360° panorama. The source note is stored beside the asset, the source is CC0, and the runtime does not depend on an external CDN.

Why this fits the current pilot:
- the current interaction rotates the view but never translates the camera, so scene parallax was not being used;
- the perception effects under test are screen/view-relative and operate correctly on the photographic reference;
- real architecture, lighting, material detail and 360° continuity now come from one coherent captured environment rather than hand-built approximations;
- future modes that require camera translation or geometric depth must add a separate depth/geometry requirement instead of pretending the panorama supplies it.

Rendered browser review `34007355631` passed technically and its captures were manually reviewed:
- Normal forward reads immediately as a real night-city environment;
- the turned direction contains coherent building facades, trees and illuminated storefront detail rather than a dark or flat stage edge;
- the opposite direction contains a coherent plaza, monument, lamps and surrounding architecture;
- bright shopfronts/streetlights and dark sky/street regions provide useful contrast targets;
- the original low-poly / primitive / stage-set problem is no longer present;
- the 390px mobile view remains usable and the existing browser check reported no horizontal overflow or captured page/console errors.

All seven v5 presentation questions passed. **Step 10A is accepted.**

Cleanup workflow `34007582142` subsequently passed and removed the dead primitive-scene implementation, obsolete Quaternius GLB assets, obsolete imports and remaining user-facing `3D renderer` wording. The active scene is now the panorama-backed spatial reference only.

## Step 11 — Central Loss rendered acceptance
Status: **PASS / accepted**

Rendered review on the v5 photographic reference confirmed:
- identical forward Normal vs Central Loss comparison makes direct central detail harder to inspect while surrounding scene information remains more available;
- after turning, the disrupted region remains centered in the viewer's field rather than staying on the previous world-space location;
- mobile touch look-around produces the same view-relative behavior;
- the effect remains restrained and generic rather than claiming patient-specific reconstruction;
- active scanning across a dense real scene makes the consequence of central field loss clearer than another transformed still image.

Central Loss is accepted for this spatial pilot.

## Final merge gate
Before PR #3 merges, run the existing full desktop / 390px Chromium regression once more on the cleaned branch head and require:
- image comparison desktop/mobile unchanged;
- Normal / Tunnel Vision / Cataract-like / Central Loss switching green;
- forward, turned and opposite panorama captures present;
- real mobile touch look-around green;
- no horizontal overflow;
- no captured page/console errors;
- build green.

No new perception mode may begin before this final regression and merge complete.

## Ordered next spatial candidates after Central Loss
1. Night / Low Light
2. Dog-like
3. Cat-like
4. Bird-like as a separate evaluation
5. Bee-like only with additional UV-reflectance scene data

## Current next action
Run the final clean-head browser/build regression, mark PR #3 ready, squash-merge it to main, verify main, then begin evaluation of `Night / Low Light` as the next spatial candidate.
