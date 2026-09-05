# AsSeenBy — Spatial Pilot Schedule

## Current state
Branch: `feat/spatial-pilot`
PR: `#2`

The existing public product remains the v0.1 static-image comparison tool. The spatial track is additive and has now passed its initial pilot acceptance gate.

Current implementation state:
- existing Vite + React + TypeScript image comparison remains in place;
- `src/transformEngine.ts` remains the 2D image renderer;
- Three.js powers a separate `Explore 3D` experience;
- one controlled night-street scene is implemented;
- the camera remains at one physical position and supports pointer/touch drag plus keyboard look-around;
- Normal, Tunnel Vision, and Cataract-like switch without recreating or moving the camera;
- Tunnel Vision is a live view-relative post-process;
- Cataract-like samples the live rendered frame, gates glare by actual high-luminance scene pixels, and adds local light spread, softness, lower contrast, slight desaturation, warmth, and veil;
- spatial renderer-specific evidence / Model notes are separate from the 2D model notes;
- dependency lockfile is synchronized with `three` and `@types/three`.

## Execution rule
At the start of every future spatial step, implementation work must re-read:
- `AGENTS.md`;
- `docs/spatial-pilot-spec.md`;
- this schedule;
- the relevant methodology / limitation / evidence documents for the active mode.

A step is not complete until its acceptance condition is satisfied. Update this file whenever scope, status, or claim boundaries change.

## Step 0 — Documentation baseline
Status: **complete**

Completed:
- repository-level `AGENTS.md` added;
- `docs/spatial-pilot-spec.md` added;
- this execution schedule added;
- roadmap, methodology, limitations, UI, modes, and evidence documents aligned;
- `approximation` clarified as a scientific claim boundary rather than permission for weak static filtering.

## Step 1 — Three.js integration shell
Status: **complete**

Completed:
- `three` and `@types/three` added;
- isolated spatial React renderer added;
- additive `Explore 3D` entry added;
- renderer failure UI and disposal added;
- CI build passed.

## Step 2 — Controlled night-street scene
Status: **complete**

Validated scene targets:
- red / green signal lenses;
- CROSSING sign target;
- pedestrian form;
- vehicle form and bright headlights;
- streetlights;
- crosswalk and lane markings;
- illuminated storefront / sign targets;
- mid / far building forms;
- deliberately darker side region.

The scene uses procedural / primitive geometry and browser-generated text textures; no photorealistic asset pipeline was introduced.

## Step 3 — Camera and comparison invariants
Status: **complete**

Validated:
- pointer drag look-around;
- real touch input through Pointer Events;
- keyboard arrow look-around when the canvas is focused;
- fixed camera position;
- no walking / collision / game controller;
- perception mode changes preserve camera position and direction.

## Step 4 — Tunnel Vision spatial simulation
Status: **complete**

Validated:
- live post-processing shader;
- central area remains visible;
- peripheral field progressively desaturates and is obscured;
- mask is screen / view-relative;
- same camera state is preserved across Normal <-> Tunnel Vision;
- desktop forward / turned screenshots and mobile touch screenshots show the field-loss effect following the viewer's view.

Scientific boundary:
- generic circular field-loss profile;
- not individual perimetry reconstruction.

## Step 5 — Cataract-like scene-dependent simulation
Status: **complete after correction and second rendered review**

First rendered review:
- the initial broad-bloom version was rejected because one captured view appeared excessively washed out and the validation sequence did not isolate camera direction cleanly.

Correction and stronger validation:
- broad `UnrealBloomPass` contribution is disabled for Cataract-like output;
- the post-process samples the live rendered frame and gates glare by actual high luminance;
- local and wider bright-sample offsets spread only bright rendered sources;
- modest optical softness, contrast loss, desaturation, warmth, and veil remain;
- new acceptance screenshots compare Normal and Cataract-like from the same forward camera direction and again from the same turned camera direction;
- forward view shows strong local spread around headlights, streetlights, and signal lights while scene structure remains readable;
- dark turned view shows no comparable bright-source halo, confirming view-dependent response rather than a fixed decorative glow.

Scientific boundary:
- generic scene-dependent optical-impairment model;
- not validated individual lens-scatter reconstruction.

## Step 6 — Evidence and limitations integration
Status: **complete**

Implemented:
- active spatial Tunnel Vision / Cataract-like mode shows underlying phenomenon evidence;
- `src/spatialEvidence.ts` supplies renderer-specific Model assessment / notes;
- both pilot implementations remain Model C rather than inheriting a stronger 2D rating;
- Normal shows a separate baseline note;
- UI states generic versus measured boundaries;
- Cataract-like evidence wording reflects the corrected high-luminance-gated renderer rather than the rejected broad-bloom implementation.

## Step 7 — Responsive, accessibility, dependency, and performance pass
Status: **complete**

Validated:
- responsive spatial layout;
- 44px mode controls and keyboard-focus styling;
- pointer, keyboard, and real touch interaction;
- device pixel ratio capped at 2;
- no shadows or continuous animation loop;
- ResizeObserver sizing;
- renderer / scene / material / texture / composer cleanup;
- graceful renderer failure path;
- synchronized package lock;
- no horizontal overflow in desktop or 390px mobile validation;
- no captured page or console errors;
- existing 2D image comparison is also exercised by the browser check on desktop and 390px mobile, including the Original / Approximation stage and Upload image control.

Final validation:
- Chromium spatial + image regression run: `33999864975` — **success**;
- PR build run: `33999866862` — **success**.

## Step 8 — Pilot acceptance gate
Status: **passed**

Decision: **PASS**.

Acceptance results:
1. existing `Compare image` behavior remains available and browser regression checks pass — **met**;
2. `Explore 3D` loads the controlled night-street scene — **met**;
3. all three modes switch without camera reset — **met**;
4. Tunnel Vision clearly changes spatial awareness while looking around — **met**;
5. Cataract-like glare changes with bright sources entering / leaving the rendered view — **met**;
6. evidence / limitation text is available for active spatial modes — **met**;
7. desktop and mobile interaction are usable — **met**;
8. build passes — **met**;
9. spatial rendering adds information beyond another transformed still image — **met for the accepted pilot modes**: Tunnel Vision demonstrates active scanning under peripheral loss, and Cataract-like demonstrates view-dependent glare response to scene lighting.

This pass does **not** mean the output is exact biological or patient-specific reproduction. The claim boundaries in methodology / limitations remain in force.

## Next spatial candidates
Proceed only in this order and re-apply the same evidence / rendered-review discipline:
1. Central Loss;
2. Night / Low Light;
3. Dog-like;
4. Cat-like;
5. Bird-like as a separate evaluation;
6. Bee-like only with additional UV-reflectance scene data.

## Current next action
Finalize PR #2 against the documented acceptance result, then begin the next spatial mode only after the accepted pilot is integrated cleanly.
