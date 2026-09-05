# AsSeenBy — Spatial Pilot Schedule

## Current state
Branch: `feat/spatial-pilot`

The existing public product is still the v0.1 static-image comparison tool. The spatial track is experimental and additive.

Current implementation state before spatial coding:
- Vite + React + TypeScript app exists;
- static image upload and sample image flow exist;
- slider / split / side-by-side comparison exists;
- `src/transformEngine.ts` contains the current 2D image transforms;
- mode evidence and limitations are already represented in the repository;
- Three.js is not yet installed;
- no spatial renderer exists yet.

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

What this produces:
A documented source of truth before code changes begin, preventing the 3D work from drifting into a game, decorative demo, or unsupported scientific claim.

Acceptance:
- required documents exist — **met**;
- existing v0.1 image MVP remains explicitly preserved — **met**;
- spatial modes are limited to Normal, Tunnel Vision, and Cataract-like for the first gate — **met**.

## Step 1 — Three.js integration shell
Status: **in progress**

Work:
- add `three` and required TypeScript typings/dependencies;
- add an isolated spatial renderer/component;
- add an `Explore 3D` entry without removing the current image workflow;
- add graceful initialization failure handling.

What this produces:
The existing site can open an empty or minimal Three.js scene while the current `Compare image` experience continues to work unchanged.

Acceptance:
- app builds;
- image comparison still works;
- 3D renderer initializes and disposes cleanly;
- mobile layout does not break.

## Step 2 — Controlled night-street scene
Status: **not started**

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
Begin Step 1: install/integrate Three.js as an isolated spatial renderer and add the `Explore 3D` entry without changing existing image comparison behavior.
