# QR2 C0 rendered visual audit

Status: **IN PROGRESS / VISUAL FAIL / DO NOT MERGE AS QR2-COMPLETE**

Latest inspected browser run: `34247303806` on the authored-prop candidate. The run was technically green and its forward, turned, translated, opposite and mobile screenshots were manually inspected.

The current Blender-generated refinement candidate is `848a9c4f8ba6b736f7c9714f33fc40d9849952b7`. It was generated successfully by `Build Blender C0 visible core` run `34250084381`, including the new architecture/street-detail pass. This candidate remains **unaccepted until a fresh browser screenshot run on this generated GLB is inspected visually**.

## What the latest inspected authored-prop run proved

- The authored C0 GLB loaded through the real chunk runtime.
- Human look controls remained active.
- Bounded ground movement remained active; the browser proof translated the Human observer after a real W input.
- The CC0 authored street-prop replacement pass rendered without browser failures.
- Desktop and mobile browser regression remained usable.

That technical success is **not QR2 acceptance**.

## Rendered failure observed in run `34247303806`

The authored-prop candidate still failed the product-quality gate in Normal mode:

- primary buildings still read as large rectangular brick masses with insufficient macro-articulation;
- repeated window rows still read as flat/repetitive blue panels rather than varied occupied architecture;
- storefront fronts remained shallow and visually weak despite the first interior-depth pass;
- the turned/moved viewpoints exposed very large flat side facades;
- a jacaranda placement visibly intersected/pressed into a primary facade because its prior hard-coded position sat inside the building footprint;
- seating was also too close to the building footprint rather than clearly grounded in the sidewalk strip;
- street and curb surfaces remained too clean/sparse, with too few drains, covers, patches and close-range scale cues;
- lighting still lacked enough contact/occlusion depth for a convincing night street;
- overall composition still read as a staged low-detail intersection rather than a believable lived-in authored environment.

## Current refinement candidate `848a9c4f...`

The new Blender refinement pass directly targets those rendered defects rather than increasing arbitrary object count.

It now:

- moves the authored jacaranda trees and modular seating out of primary building footprints and onto the sidewalk strip;
- adds projecting facade pilasters and floor belt courses to break the single-box building read;
- adds recessed varied window backplanes with dark, warm and cool occupied/unoccupied states behind the existing framed glazing;
- adds storefront portal shadow/depth, plinths, jambs, door pulls, canopy supports and projecting blade signs;
- adds side-facade downpipes, belt articulation and compact fire-escape/platform detail on the east-side buildings so turned views are not one uninterrupted brick wall;
- adds manhole covers, asphalt repair patches, storm drains with grate slots, sidewalk service covers and stop-line detail;
- keeps all new primary-visible work in Blender/GLB and does not return visible-world responsibility to `nightIntersectionScene.ts`.

The deterministic source pass is `scripts/blender/refine_night_intersection_c0.py`; the canonical Blender workflow runs it after the authored CC0 augmentation and before GLB export.

## Remaining blockers to judge in the next render

The next screenshot audit must decide, from actual forward/turned/translated/opposite/mobile views, whether:

- facade articulation is visibly strong enough at walking distance;
- the tree/seating grounding error is genuinely gone;
- window variation stops the facade from reading as a repeated grid;
- storefronts have enough construction and depth to survive close approach;
- added street microdetail is visible at the user camera scale rather than technically present but visually irrelevant;
- side-facade detail fixes the most obvious flat-wall failure;
- the night-light hierarchy still needs a separate shadow/occlusion/runtime-light pass.

If those screenshots still read as cheap low-poly or placeholder work, QR2 remains failed and the next Blender pass will continue architecture/storefront/material/lighting work. Do not advance to QR3 or E5 based on CI alone.

QR2 passes only when representative walking-distance screenshots no longer read as debug, cheap low-poly, or placeholder work. A green build/browser test is necessary but not sufficient.
