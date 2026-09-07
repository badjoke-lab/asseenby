# AsSeenBy

AsSeenBy is a research-based visual comparison tool for translating commonly described visual differences into image-based and spatial comparison views across human visual conditions and carefully bounded animal/species approximations.

It is designed for comparison, illustration, and discussion rather than exact perceptual reproduction, diagnosis, or medical judgment.

**Site:** [https://asseenby.pages.dev/](https://asseenby.pages.dev/)  
**Support:** [Support AsSeenBy](https://buy.stripe.com/6oUcMY4cD3Zm6FdcNdcIE02?utm_source=github&utm_medium=repo&utm_campaign=support)

Support is optional and helps cover maintenance, hosting, and future improvements.

## Project direction

The product direction is editorial rather than SaaS-like: off-white background, serif-led typography, and a quiet encyclopedia / atlas / research-book tone.

AsSeenBy now has two complementary product tracks:
- **Compare image** — browser-side static-image comparison;
- **Explore 3D** — Three.js spatial comparison built around `Scene / Observer / Vision`.

Explore 3D is not intended to remain a 360° panorama viewer. The current Hansaplatz panorama is retained as a photographic reference scene while the post-pilot architecture moves toward geometry-based environments, observer-specific viewpoint/movement, depth/parallax, lighting, occlusion, distance and vertical space.

Current 3D product behavior is defined by `docs/explore-3d-spec.md` and current implementation order by `docs/explore-3d-schedule.md`.

## Status

The original v0.1 image MVP remains the stable comparison baseline. Explore 3D is an additive post-MVP track and must not replace or break Compare image.

## Current stack

- Vite
- React
- TypeScript
- Browser-side Canvas 2D image processing
- Three.js / WebGL for Explore 3D
- Static/client-side deployment; no server-side image processing required

## Compare image scope

### Included

- static image upload
- sample image loading
- compare stage with slider / split / side-by-side modes
- Human / Animal mode groups
- strength control
- browser-side transformation only
- mode-level evidence panel with badges and sources
- no server-side image storage

### Not included

- video processing
- live camera mode
- user accounts
- saved sessions
- API
- diagnostic output

## Current image mode groups

### Human

- Protan-like
- Deutan-like
- Tritan-like
- Blur
- Low Contrast
- Cataract-like
- Tunnel Vision
- Central Loss

### Animal

- Dog-like

## Explore 3D direction

The current architecture target separates:

- **Scene** — geometry, materials, lights, navigation/collision bounds, spawn/perch/guided targets;
- **Observer** — viewpoint height, movement, reachable space and body/navigation constraints;
- **Vision** — perception renderer.

Planned observer families include Human, Dog, Cat and species-specific Bird presets.

Important boundaries:
- Dog/Cat/Bird observer movement and camera height are separate from species-specific visual claims;
- Cat observer support does not automatically restore the previously rejected Cat-like RGB visual filter;
- Bird observers must use actual vertical flight/altitude/perch behavior rather than Human/Dog ground walking;
- generic Bird-like spectral/color vision is not accepted from ordinary RGB;
- UV/tetrachromatic/bee-like visual work remains blocked without appropriate spectral/UV source data and a documented observer model;
- the existing 360° panorama remains `360° Photo Reference`, not the capability ceiling of Explore 3D.

The first full geometry-based target scene is `Night Intersection`, followed by additional dense scenes only after the architecture is stable.

## Project structure

- `src/App.tsx` — Compare image UI and workflow
- `src/transformEngine.ts` — image transform logic
- `src/SpatialPage.tsx` — current Three.js spatial implementation; to be refactored under the Scene / Observer / Vision architecture
- `src/modes.ts` — mode definitions and confidence classes
- `src/modeEvidence.ts` — per-mode evidence metadata
- `src/spatialEvidence.ts` — spatial renderer evidence/Model notes
- `src/evidenceTypes.ts` — evidence and source types
- `src/components/ModeEvidencePanel.tsx` — evidence panel UI
- `docs/roadmap.md` — current product priority
- `docs/explore-3d-spec.md` — canonical current Explore 3D product specification
- `docs/explore-3d-schedule.md` — canonical current Explore 3D execution order
- `docs/spatial-pilot-spec.md` — historical spatial pilot specification/evidence record
- `docs/spatial-pilot-schedule.md` — historical spatial pilot execution record
- `docs/release-polish-schedule.md` — current image/release-polish execution and production verification
- `docs/ui-spec.md` — visual and layout direction
- `docs/modes.md` — mode groups and confidence classes
- `docs/methodology.md` — methodology and framing
- `docs/limitations.md` — current scope boundaries and reading rules
- `docs/evidence-model.md` — evidence badge model and source-display rules

## Agent / contributor reading rule

Implementation agents must follow `AGENTS.md`.

For Explore 3D work, `docs/explore-3d-spec.md` and `docs/explore-3d-schedule.md` are mandatory current sources of truth. The older spatial-pilot documents remain historical context; where they conflict with current Explore 3D product behavior, the current Explore 3D spec controls.

## Local development

```bash
npm install
npm run dev
```

## Production build

```bash
npm run build
npm run preview
```

## Notes and limitations

- AsSeenBy is not a medical tool.
- Human and animal outputs are research-based approximations.
- Observer geometry/movement does not by itself validate a species-specific visual model.
- Ordinary RGB cannot recover UV, polarization, complete spectral relationships, exact animal cone catches or neural interpretation.
- The current public release has no Reference image modes; any future reference dataset must define its population and mapping explicitly.
- Evidence and Model badges communicate claim strength and implementation maturity, not certainty.

## Product positioning

AsSeenBy should feel closer to a field guide or visual reference plate than a dark startup dashboard or game HUD. The app is meant to support comparison, understanding and discussion rather than exact biological or medical claims.
