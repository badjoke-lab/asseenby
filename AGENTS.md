# AsSeenBy — Agent Instructions

These instructions are the repository-level working rules for implementation agents.

## Required reading before changing code
Read these files before implementation and use them as the source of truth for scope and product claims:

1. `README.md`
2. `docs/roadmap.md`
3. `docs/spatial-pilot-spec.md` when working on 3D / spatial features
4. `docs/spatial-pilot-schedule.md` for current execution order and status
5. `docs/methodology.md`
6. `docs/limitations.md`
7. `docs/ui-spec.md`
8. `docs/modes.md` and `docs/evidence-model.md` when changing perception modes or evidence UI

If code and documentation disagree, do not silently invent a new direction. Preserve the documented product boundary or update the relevant spec in the same change.

## Product invariants
- Keep the existing static-image comparison experience. The spatial experience is additive, not a replacement.
- The image experience remains `Compare image`; the Three.js experience remains `Explore spatial`.
- Do not turn AsSeenBy into a game, generic 3D showcase, medical tool, or claim of exact perception.
- Every perception output is a research-based approximation or reference view, subject to the evidence and limitation documents.
- Do not claim UV, polarization, full species-specific spectral perception, neural interpretation, diagnosis, or patient-level accuracy unless a future spec explicitly adds a validated data path for it.
- Keep uploads browser-side. Do not add accounts, saved sessions, server-side image storage, or an API unless separately specified.
- Preserve the editorial field-guide / research-book visual language. Avoid generic dark SaaS, glow, glass, or game HUD styling.

## Spatial expansion invariants
- The initial Normal / Tunnel Vision / Cataract-like pilot established the renderer and interaction baseline, but subsequent visual review showed that the current primitive night-street scene is not acceptable as a public-facing presentation baseline.
- Scene presentation quality is now a blocking acceptance criterion. A technically correct perception shader must not be merged if the environment still reads as placeholder geometry, a cheap low-detail demo, or a debug test scene.
- The night street must remain a controlled comparison environment, but it must also read immediately as a believable street: recognizable building facades, windows and storefront detail, credible road/sidewalk surfaces, vehicle form, pedestrian form, lighting hierarchy, street furniture, and enough near/mid/far visual information to support perception comparisons.
- Primitive geometry is allowed when it is composed into convincing forms. Bare boxes standing in for buildings, cars, or people are not sufficient for acceptance.
- Keep camera position and direction unchanged when switching perception modes so the comparison isolates the rendering model.
- Interaction remains look-around first; no walking simulation, collision system, scoring, or game mechanics are required.
- Reuse existing mode evidence and limitations wherever applicable instead of creating separate unsupported claims.
- Add post-pilot spatial modes one at a time in the order defined by `docs/spatial-pilot-schedule.md` and require a rendered acceptance check before starting the following mode.
- Central Loss, Night / Low Light, and the photographic 360° reference scene are accepted and merged. The current expansion target is `Dog-like`; do not begin Cat-like, Bird-like, or Bee-like until its rendered acceptance gate passes or it is explicitly rejected.
- Dog-like must preserve the same camera and use a conservative visible-range dichromatic + acuity proxy. Do not claim that RGB can reconstruct canine cone catches for arbitrary spectra, or that the renderer models breed-dependent field of view, motion processing, tapetal/rod low-light advantages, or literal canine qualia.
- The current panorama is tone-mapped RGB. It can support a human-display visible-range comparison, not complete species-specific spectral reconstruction.
- Central Loss remains a generic field-loss model, not an individual's measured scotoma or perimetry result.
- Bee-like UV work still requires additional UV-reflectance scene data and must not be faked with an RGB color filter.

## Engineering rules
- Prefer the smallest change that satisfies the active schedule step, except where the documented scene-quality gate explicitly requires a broader presentation pass.
- Keep the current React + TypeScript structure unless a documented requirement needs restructuring.
- Three.js remains an isolated spatial renderer/component and must not replace the 2D canvas transform engine.
- Avoid unrelated refactors while a new spatial mode is being validated.
- Keep desktop and mobile behavior usable.
- Run `npm run build` before declaring an implementation step complete. The existing GitHub workflow runs the same typecheck + Vite build on pull requests and main.

## Progress discipline
At the start of each implementation step, re-read `docs/spatial-pilot-schedule.md` and the relevant spec sections.

When a step is completed, blocked, rejected, or materially changed:
- update `docs/spatial-pilot-schedule.md` in the same branch/PR;
- update `docs/spatial-pilot-spec.md` if product behavior or acceptance criteria changed;
- update `docs/methodology.md` / `docs/limitations.md` if the scientific or claim boundary changed;
- keep renderer-specific Model notes separate from the existing 2D implementation assessment.

Do not mark later spatial modes complete merely because scaffolding exists. Status is based on the acceptance criteria in the schedule, including actual rendered review and the scene-presentation quality gate.
