# AsSeenBy — Spatial Pilot Schedule

## Current state
Branch: `feat/spatial-pilot`

The existing public product is still the v0.1 static-image comparison tool. The spatial track is experimental and additive.

Current implementation state:
- Vite + React + TypeScript image app remains in place;
- static image upload and sample image flow remain in place;
- slider / split / side-by-side image comparison remains in place;
- `src/transformEngine.ts` remains the 2D image transform engine;
- Three.js and TypeScript definitions are now declared for the spatial track;
- `Explore 3D` now opens an isolated browser-side Three.js renderer through the existing main entry;
- the renderer shell has initialization failure handling and explicit disposal;
- PR #2 build run 51 passed `npm install`, TypeScript checking, and Vite build.

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
- `docs/roadmap.md`, `docs/methodology.md`, `docs/limitations.md`, `docs/ui-spec.md`, `docs/modes.md`, and `docs/evidence-model.md` aligned with the additive spatial track;
- spatial terminology clarified: `approximation` is a claim boundary, while spatially dependent effects must use live scene-aware rendering rather than a static decorative filter.

Acceptance:
- required documents exist — **met**;
- existing v0.1 image MVP remains explicitly preserved — **met**;
- spatial modes are limited to Normal, Tunnel Vision, and Cataract-like for the first gate — **met**.

## Step 1 — Three.js integration shell
Status: **complete**

Completed:
- `three` and `@types/three` declared;
- isolated spatial React renderer added;
- `Explore 3D` entry added without replacing the image workflow;
- renderer has graceful failure UI and cleanup/disposal;
- build workflow run 51 completed successfully.

What this produces:
The existing site can open a minimal Three.js scene while `Compare image` continues to exist as the product baseline.

Acceptance:
- app builds — **met**;
- image experience remains routed as the default — **met**;
- 3D renderer initializes/disposes in an isolated component — **met by implementation and build**;
- mobile layout has a dedicated responsive shell — **met at code level; broader interaction validation continues in Step 7**.

## Step 2 — Controlled night-street scene
Status: **in progress**

Work:
Create one lightweight test environment containing the visual targets required by `docs/spatial-pilot-spec.md`.

What this produces:
A single repeatable spatial test environment with bright lights, dark areas, near/mid/far targets, pedestrians/signage/road markings, and enough structure to expose field-loss and glare behavior.

Acceptance:
- required targets are visible;
- scene is understandable without game controls;
- no unnecessary photorealistic asset pipeline is introduced;
- performance remains acceptable on desktop and mobile test sizes.

## Step 3 — Camera and comparison invariants
Status: **not started**

Work:
- implement look-around interaction;
- implement touch look-around;
- add restrained zoom only if it does not confuse the comparison;
- preserve camera position and direction when switching perception mode.

What this produces:
A user can inspect the scene, then toggle modes while comparing exactly the same viewpoint.

Acceptance:
- mode switches never reset or teleport the camera;
- no walking/game controller is required;
- interaction remains usable by mouse and touch.

## Step 4 — Tunnel Vision spatial simulation
Status: **not started**

Work:
Implement live view-relative peripheral field loss on the rendered scene.

What this produces:
The user can actively scan the scene and experience the practical consequence of losing peripheral information, rather than viewing a single masked photograph.

Acceptance:
- central region stays most visible;
- peripheral information is progressively lost/degraded;
- the field-loss region follows the viewer's screen/view, not world coordinates;
- Normal <-> Tunnel Vision switch preserves the same scene/camera state;
- effect is applied to the live scene.

## Step 5 — Cataract-like scene-dependent simulation
Status: **not started**

Work:
Implement a scene-aware cataract-like model using rendered brightness information plus contrast loss, softness, haze/warming, and bright-source light spread.

What this produces:
Looking toward headlights/streetlights produces a stronger impairment than looking into a dark region, demonstrating why the spatial renderer is useful.

Acceptance:
- bright-source response depends on actual rendered luminance/bright-pass data;
- turning toward and away from bright sources visibly changes glare/spread;
- effect is not a constant decorative bloom overlay;
- Normal <-> Cataract-like switch preserves scene/camera state.

## Step 6 — Evidence and limitations integration
Status: **not started**

Work:
- connect existing evidence concepts to the spatial mode UI;
- state what the spatial model represents;
- state what is generic versus measured;
- keep the non-diagnostic / non-exact-reproduction boundary visible.

What this produces:
The 3D output remains an AsSeenBy research comparison tool rather than an unexplained visual effect demo.

Acceptance:
- active mode has evidence/limitations available;
- UI does not imply patient-specific accuracy;
- claims match `docs/methodology.md` and `docs/limitations.md`.

## Step 7 — Responsive, accessibility, and performance pass
Status: **not started**

Work:
- desktop interaction check;
- mobile interaction check;
- keyboard/focus behavior for mode controls;
- renderer resize/disposal verification;
- conservative scene complexity/performance tuning;
- reduced-motion behavior where relevant.

What this produces:
A pilot that can actually be tried on the same public-facing site instead of a desktop-only technical demo.

Acceptance:
- no horizontal layout breakage at narrow widths;
- controls remain usable by keyboard and touch;
- renderer does not continue leaking animation loops/resources after leaving the view;
- build passes.

## Step 8 — Pilot acceptance gate
Status: **not started**

Decision question:
Does the spatial version explain Tunnel Vision and Cataract-like materially better than another static transformed image?

Pass means:
- all acceptance criteria in `docs/spatial-pilot-spec.md` are met;
- comparison value is clear;
- no regression to the image MVP.

If pass:
Proceed to the next spatial candidates in this order:
1. Central Loss;
2. Night / Low Light;
3. Dog-like;
4. Cat-like;
5. evaluate Bird-like separately;
6. Bee-like only with additional UV-reflectance scene data.

If fail:
Keep the current image tool and remove or leave the spatial work experimental. Do not expand 3D simply because it looks impressive.

## Current next action
Build the controlled night-street test environment for Step 2, then verify it before starting camera interaction.
