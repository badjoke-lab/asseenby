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
- Keep the existing static-image comparison experience. The spatial pilot is additive, not a replacement.
- The image experience remains `Compare image`; the experimental Three.js experience is `Explore 3D`.
- Do not turn AsSeenBy into a game, generic 3D showcase, medical tool, or claim of exact perception.
- Every perception output is a research-based approximation or reference view, subject to the evidence and limitation documents.
- Do not claim UV, polarization, full species-specific spectral perception, neural interpretation, diagnosis, or patient-level accuracy unless a future spec explicitly adds a validated data path for it.
- Keep uploads browser-side. Do not add accounts, saved sessions, server-side image storage, or an API unless separately specified.
- Preserve the editorial field-guide / research-book visual language. Avoid generic dark SaaS, glow, glass, or game HUD styling.

## Spatial pilot invariants
- Initial scene: one purpose-built night street / street-corner test environment.
- Initial spatial modes: `Normal`, `Tunnel Vision`, and `Cataract-like` only.
- Keep camera position and direction unchanged when switching perception modes so the comparison isolates the rendering model.
- Initial interaction is look-around plus restrained zoom; no walking simulation is required for the first pilot.
- Reuse existing mode evidence and limitations wherever applicable instead of creating separate unsupported claims.
- The pilot must demonstrate a benefit that static-image comparison cannot show as clearly: field-of-view loss and lighting/glare response in an interactive spatial scene.
- Dog-like, Cat-like, Central Loss, Night / Low Light, and other modes come only after the first pilot acceptance gate.
- Bee-like UV work requires additional UV-reflectance scene data and must not be faked with an RGB color filter.

## Engineering rules
- Prefer the smallest change that satisfies the active schedule step.
- Keep the current React + TypeScript structure unless a documented requirement needs restructuring.
- Three.js should be integrated as an isolated spatial renderer/component rather than replacing the 2D canvas transform engine.
- Avoid unrelated refactors while the pilot is being validated.
- Keep desktop and mobile behavior usable.
- Run `npm run build` before declaring an implementation step complete. The existing GitHub workflow runs the same typecheck + Vite build on pull requests and main.

## Progress discipline
At the start of each implementation step, re-read `docs/spatial-pilot-schedule.md` and the relevant spec sections.

When a step is completed, blocked, rejected, or materially changed:
- update `docs/spatial-pilot-schedule.md` in the same branch/PR;
- update `docs/spatial-pilot-spec.md` if the product behavior or acceptance criteria changed;
- update `docs/methodology.md` / `docs/limitations.md` if the scientific or claim boundary changed.

Do not mark later steps complete merely because scaffolding exists. Status is based on the acceptance criteria in the schedule.
