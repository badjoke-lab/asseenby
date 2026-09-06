# AsSeenBy — Agent Instructions

These instructions are the repository-level working rules for implementation agents.

## Required reading before changing code
Read these files before implementation and use them as the source of truth for scope and product claims:

1. `README.md`
2. `docs/roadmap.md`
3. `docs/spatial-pilot-spec.md` when working on 3D / spatial features
4. `docs/spatial-pilot-schedule.md` for spatial execution order and status
5. `docs/release-polish-schedule.md` for image/release-polish execution order and production verification status
6. `docs/methodology.md`
7. `docs/limitations.md`
8. `docs/ui-spec.md`
9. `docs/modes.md` and `docs/evidence-model.md` when changing perception modes or evidence UI

If code and documentation disagree, do not silently invent a new direction. Preserve the documented product boundary or update the relevant spec/schedule in the same change.

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
- Central Loss, Night / Low Light, Dog-like, and the photographic 360° reference scene are accepted and merged. Cat-like spatial was rejected after rendered review. Generic Bird-like spatial was then rejected/blocked at the evidence/source-data gate: ordinary RGB cannot reproduce avian tetrachromatic/UV relationships, while acuity and spectral tuning vary too widely across bird species to justify one generic live renderer.
- Bee-like spatial remains blocked until an explicit UV-reflectance/spectral scene-data path exists. Do not begin a Bee-like shader from ordinary RGB, and do not substitute a purple/blue false tint for missing UV information.
- The ordered animal spatial evaluation is therefore resolved under the current Hansaplatz RGB source. Any future species-specific spatial work must introduce a new documented data/model requirement rather than reopening generic animal filters.
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
- For production-verification steps, preview/local success is not enough: test the public production URL and record stale/deployment-state failures separately from code failures.

## Progress discipline
At the start of each spatial implementation step, re-read `docs/spatial-pilot-schedule.md` and the relevant spec sections.

At the start of each image/release-polish step, re-read `docs/release-polish-schedule.md` and `docs/roadmap.md`; if the step touches spatial behavior, also re-read the spatial spec/schedule.

When a step is completed, blocked, rejected, or materially changed:
- update the active schedule (`docs/spatial-pilot-schedule.md` or `docs/release-polish-schedule.md`) in the same branch/PR;
- update `docs/spatial-pilot-spec.md` if spatial product behavior or acceptance criteria changed;
- update `docs/methodology.md` / `docs/limitations.md` if the scientific or claim boundary changed;
- keep renderer-specific Model notes separate from the existing 2D implementation assessment.

Do not mark a step complete merely because scaffolding exists. Status is based on the acceptance criteria in the active schedule, including actual rendered review where required and production verification where explicitly required.
