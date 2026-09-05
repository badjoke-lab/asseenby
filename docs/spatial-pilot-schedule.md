# AsSeenBy — Spatial Pilot Schedule

## Current state
Branch: `feat/spatial-pilot`
PR: `#2`

The existing public product remains the v0.1 static-image comparison tool. The spatial track is experimental and additive.

Current implementation state:
- Vite + React + TypeScript image app remains in place;
- static image upload and sample image flow remain in place;
- slider / split / side-by-side image comparison remains in place;
- `src/transformEngine.ts` remains the 2D image transform engine;
- Three.js and TypeScript definitions are declared for the spatial track;
- `Explore 3D` opens through the existing main entry;
- one controlled night-street scene exists;
- the camera stays at one physical position and supports pointer/touch drag plus keyboard look-around;
- Normal, Tunnel Vision, and Cataract-like are switchable without recreating or moving the camera;
- Tunnel Vision is a live view-relative post-process;
- Cataract-like now uses a rendered-image high-luminance gate plus local light spread, softness, contrast loss, warmth, and veil processing; the earlier broad bloom version was rejected after screenshot review because it washed out the scene;
- spatial renderer-specific evidence notes are separate from the existing 2D model notes;
- dependency lockfile is synchronized with `three` and `@types/three`.

## Execution rule
At the start of every step below, implementation work must re-read:
- `AGENTS.md`;
- `docs/spatial-pilot-spec.md`;
- this schedule;
- any referenced methodology / limitation document for the active mode.

A step is not complete until its acceptance condition is satisfied. Update this file when status changes.

## Step 0 — Documentation baseline
Status: **complete**

Completed:
- repository-level `AGENTS.md` added;
- `docs/spatial-pilot-spec.md` added;
- this execution schedule added;
- roadmap, methodology, limitations, UI, modes, and evidence documents aligned;
- `approximation` clarified as a claim boundary rather than permission for weak static filtering.

## Step 1 — Three.js integration shell
Status: **complete**

Completed:
- `three` and `@types/three` declared;
- isolated spatial React renderer added;
- additive `Explore 3D` entry added;
- renderer failure UI and disposal added;
- CI build passed.

## Step 2 — Controlled night-street scene
Status: **implementation complete; runtime visual validation in Step 7**

Implemented scene targets:
- red / green signal lenses;
- text-like CROSSING sign;
- pedestrian form;
- vehicle form;
- bright vehicle headlights;
- streetlights;
- crosswalk and lane markings;
- illuminated storefront and OPEN sign;
- mid / far building forms;
- deliberately darker side region.

The scene uses procedural / primitive geometry and browser-generated text textures; no photorealistic asset pipeline was added.

## Step 3 — Camera and comparison invariants
Status: **implementation complete; browser interaction validation passed once and will be repeated after the cataract correction**

Implemented:
- pointer drag look-around;
- Pointer Events also cover touch input;
- keyboard arrow look-around when the canvas is focused;
- fixed camera position;
- no walking / collision / game controller;
- perception mode changes toggle renderer passes without recreating the camera.

## Step 4 — Tunnel Vision spatial simulation
Status: **implementation complete; first rendered review passed**

Implemented:
- live post-processing shader;
- central area remains visible;
- peripheral field progressively desaturates and is obscured;
- mask is screen/view-relative;
- same camera state is preserved across Normal <-> Tunnel Vision.

Rendered review finding:
- desktop Normal / Tunnel screenshots and look-around screenshot showed a clear view-relative peripheral-loss effect while retaining the center;
- mobile touch validation also passed in the first browser run.

Scientific boundary:
- generic circular field-loss profile;
- not individual perimetry reconstruction.

## Step 5 — Cataract-like scene-dependent simulation
Status: **corrected implementation; second rendered review required**

First rendered review finding:
- the initial broad bloom implementation was rejected because the scene became excessively washed out / gray and lost useful spatial information;
- it was not accepted merely because the code built or the effect was technically scene-dependent.

Correction applied:
- broad `UnrealBloomPass` contribution is disabled for Cataract-like output;
- the post-process now samples the live rendered frame and gates glare contribution by actual high luminance;
- nearby and wider bright-sample offsets spread only bright rendered sources;
- dark regions retain substantially more scene information;
- modest optical softness, contrast loss, desaturation, warmth, and veil remain;
- the same camera state is preserved across Normal <-> Cataract-like.

Required next check:
- regenerate desktop/mobile screenshots from the corrected implementation;
- confirm headlights / streetlights create local glare while darker regions remain legible;
- confirm turning the camera changes the glare response because the bright sources entering the rendered view change.

Scientific boundary:
- generic scene-dependent optical-impairment model;
- not validated individual lens-scatter reconstruction.

## Step 6 — Evidence and limitations integration
Status: **complete at implementation level**

Implemented:
- active spatial Tunnel Vision / Cataract-like mode shows the existing underlying phenomenon evidence;
- `src/spatialEvidence.ts` overrides the Model assessment / model note specifically for the 3D renderer;
- both pilot spatial implementations remain Model C pending stronger validation;
- Normal shows a separate baseline note;
- UI text states generic versus measured boundaries.

## Step 7 — Responsive, accessibility, dependency, and performance pass
Status: **in progress**

Already implemented / verified:
- responsive spatial layout;
- 44px mode controls;
- keyboard-focus styling;
- keyboard scene controls;
- pointer/touch input through Pointer Events;
- device pixel ratio capped at 2;
- no shadows or continuous animation loop;
- ResizeObserver-based sizing;
- scene/material/texture cleanup;
- composer/pass cleanup;
- graceful renderer failure path;
- package lock synchronized;
- first Chromium run passed desktop interaction, 390px mobile touch interaction, mode switching, horizontal-overflow checks, and console/page-error checks;
- first screenshots established that Tunnel Vision was visually coherent but the first Cataract-like rendering was not, leading to the correction above.

Still to verify before calling Step 7 complete:
- repeat Chromium desktop/mobile validation on the corrected Cataract-like implementation;
- inspect the new screenshots visually;
- confirm corrected glare remains scene-dependent and does not wash out the whole scene.

## Step 8 — Pilot acceptance gate
Status: **not started**

Decision question:
Does the spatial version explain Tunnel Vision and Cataract-like materially better than another static transformed image?

Pass requires:
1. existing `Compare image` behavior still works;
2. `Explore 3D` loads the controlled night-street scene;
3. all three modes switch without camera reset;
4. Tunnel Vision clearly changes spatial awareness while looking around;
5. Cataract-like glare clearly changes when bright sources enter / leave the view;
6. evidence / limitation text is available for active spatial modes;
7. desktop and mobile interaction are usable;
8. build passes;
9. the spatial result is materially more informative than another transformed still image.

Do not mark this gate passed from code review or CI alone. It requires an actual rendered experience review.

If pass, next candidates are:
1. Central Loss;
2. Night / Low Light;
3. Dog-like;
4. Cat-like;
5. Bird-like separate evaluation;
6. Bee-like only with additional UV-reflectance scene data.

If fail:
Keep the image tool and remove or leave the spatial work experimental. Do not expand 3D because it merely looks impressive.

## Current next action
Run the second Chromium desktop/mobile validation on the corrected Cataract-like implementation, inspect the screenshots, then decide Step 7 completion and begin Step 8 only if the rendered result passes.
