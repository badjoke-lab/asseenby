# AsSeenBy — Roadmap

## Current state
The repository contains the initial Vite + React + TypeScript shell, the static-image comparison interface, browser-side comparison behavior, evidence metadata, and the first documentation set.

The existing image MVP remains the product baseline. A separate experimental spatial track is now being evaluated through `docs/spatial-pilot-spec.md` and `docs/spatial-pilot-schedule.md`.

## Phase 0 — Foundation
Status: in progress

Included:
- Vite project shell
- React entrypoint
- off-white editorial UI direction
- compare stage
- control rail
- image upload
- sample image
- initial mode switching
- initial transform pipeline

## Phase 1 — Stabilization
Goals:
- make local build pass cleanly
- verify TypeScript and Vite config together
- clean first-pass UI issues
- improve error messaging for invalid images

## Phase 2 — Mode quality pass
Goals:
- refine human-mode transforms
- refine animal-mode visible-range approximations
- tune strength scaling
- reduce visual artifacts in preview output

## Phase 3 — Content pages
Goals:
- wire About / Modes / Methodology / Limitations pages
- connect top navigation to real routes or sections
- expand explanatory copy where needed

## Phase 4 — Public MVP preparation
Goals:
- final visual polish
- responsive cleanup
- release checklist
- deploy target selection

## Experimental track — Spatial comparison pilot
Status: documentation baseline / pre-implementation

Purpose:
Test whether a purpose-built Three.js scene provides materially better understanding for spatially dependent visual differences than another static image transformation.

The spatial track is additive and must not replace the existing image comparison workflow.

Initial pilot scope:
- one controlled night-street / street-corner scene;
- Normal baseline;
- Tunnel Vision spatial simulation;
- Cataract-like scene-dependent glare / haze simulation;
- same camera position and direction when switching modes;
- existing evidence / limitation concepts carried into spatial mode UI;
- desktop and mobile usability;
- no game mechanics or free-roaming requirement.

The word `approximation` is a scientific/product claim boundary. It does not mean the 3D implementation should be a simple static screen filter. The spatial renderer should use live scene information such as view direction and rendered brightness whenever the mode requires it.

Acceptance and implementation order are defined in:
- `docs/spatial-pilot-spec.md`
- `docs/spatial-pilot-schedule.md`

The 3D track expands only if the pilot demonstrates clearer comparison value than the current still-image approach.

## Near-term priority order
1. finish spatial pilot documentation alignment
2. integrate an isolated Three.js renderer without regressing image comparison
3. build the controlled night-street scene
4. implement Tunnel Vision and Cataract-like pilot modes
5. run the spatial acceptance gate
6. continue existing image MVP stabilization / content / transform polish as needed
