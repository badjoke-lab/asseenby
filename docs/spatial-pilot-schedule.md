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
- `Explore 3D` opens through the existing main index using `?view=spatial`;
- one controlled night-street scene exists;
- the camera stays at one physical position and supports pointer/touch drag plus keyboard look-around;
- Normal, Tunnel Vision, and Cataract-like are switchable without recreating or moving the camera;
- Tunnel Vision is a live view-relative post-process;
- Cataract-like uses live scene bright-pass bloom plus softness / contrast / warmth / veil processing;
- spatial renderer-specific evidence notes are separate from the existing 2D model notes;
- latest checked PR head build (run 61) passed dependency install, TypeScript checking, and Vite build.

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
Status: **implementation complete; runtime visual validation pending Step 7**

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
Status: **implementation complete; runtime interaction validation pending Step 7**

Implemented:
- pointer drag look-around;
- Pointer Events also cover touch input;
- keyboard arrow look-around when the canvas is focused;
- fixed camera position;
- no walking / collision / game controller;
- perception mode changes toggle renderer passes without recreating the camera.

## Step 4 — Tunnel Vision spatial simulation
Status: **implementation complete; visual validation pending Step 7 / 8**

Implemented:
- live post-processing shader;
- central area remains visible;
- peripheral field progressively desaturates and is obscured;
- mask is screen/view-relative;
- same camera state is preserved across Normal <-> Tunnel Vision.

Scientific boundary:
- generic circular field-loss profile;
- not individual perimetry reconstruction.

## Step 5 — Cataract-like scene-dependent simulation
Status: **implementation complete; visual validation pending Step 7 / 8**

Implemented:
- `UnrealBloomPass` bright-pass response to rendered scene luminance;
- high-emissive headlights / streetlights / signals provide actual bright scene sources;
- post-process softness;
- reduced contrast;
- desaturation / warming;
- veil / haze component;
- same camera state is preserved across Normal <-> Cataract-like.

The glare component is not a fixed overlay: it depends on which bright rendered sources are currently in view.

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

Already implemented:
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
- latest build passes.

Still to verify / resolve before calling Step 7 complete:
- dependency lockfile consistency after adding Three.js packages;
- actual desktop browser rendering / interaction;
- actual mobile/touch browser rendering / interaction;
- subjective scene readability and performance on real hardware.

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
Finish Step 7 dependency consistency and obtain an actual rendered desktop/mobile review before deciding Step 8 or merging the pilot into `main`.
