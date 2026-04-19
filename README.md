# AsSeenBy

AsSeenBy is a research-based visual comparison tool for translating commonly described visual differences into image-based comparison views across human visual conditions, animal-inspired approximations, and reference profiles.

It is designed for comparison, illustration, and discussion rather than exact perceptual reproduction, diagnosis, or medical judgment.

**Site:** [https://asseenby.pages.dev/](https://asseenby.pages.dev/)  
**Support:** [Support AsSeenBy](https://buy.stripe.com/6oUcMY4cD3Zm6FdcNdcIE02?utm_source=github&utm_medium=repo&utm_campaign=support)

Support is optional and helps cover maintenance, hosting, and future improvements.

## Project direction

The product direction is editorial rather than SaaS-like: off-white background, serif-led typography, and a quiet encyclopedia / atlas / research-book tone.

## Status

v0.1 is intentionally narrow and focused on a browser-based MVP.

## Current stack

- Vite
- React
- TypeScript
- Browser-side canvas image processing only

## MVP scope

### Included in v0.1

- static image upload
- sample image loading
- compare stage with slider / split / side-by-side modes
- Human / Animal / Reference mode groups
- strength control
- browser-side transformation only
- mode-level evidence panel with badges and sources
- no server-side image storage

### Not included in v0.1

- video processing
- live camera mode
- user accounts
- saved sessions
- API
- share links
- diagnostic output

## Current mode groups

### Human

- Protan-like
- Deutan-like
- Tritan-like
- Blur
- Low Contrast
- Cataract-like
- Tunnel Vision
- Central Loss
- Night / Low Light
- Fatigue-like
- Dry-eye-like

### Animal

- Dog-like
- Cat-like
- Bee-like
- Bird-like

### Reference

- Age Profile
- Sex-difference Profile

## Project structure

- `src/App.tsx` — main comparison UI and workflow
- `src/transformEngine.ts` — image transform logic
- `src/modes.ts` — mode definitions and confidence classes
- `src/modeEvidence.ts` — per-mode evidence metadata
- `src/evidenceTypes.ts` — evidence and source types
- `src/components/ModeEvidencePanel.tsx` — evidence panel UI
- `src/styles.css` — editorial UI styling
- `src/evidence.css` — evidence panel styling
- `src/main.tsx` — app entry
- `docs/overview.md` — product overview and positioning
- `docs/mvp-spec.md` — MVP scope and included features
- `docs/ui-spec.md` — visual and layout direction
- `docs/modes.md` — mode groups and confidence classes
- `docs/methodology.md` — methodology and framing
- `docs/limitations.md` — current scope boundaries and reading rules
- `docs/evidence-model.md` — evidence badge model and source-display rules
- `docs/compare-modes.md` — compare behavior notes for slider, split, and side-by-side

## Local development

```bash
npm install
npm run dev
````

## Production build

```bash
npm run build
npm run preview
```

## Notes and limitations

* AsSeenBy is not a medical tool.
* Human, animal, and reference outputs are research-based approximations.
* Animal modes are visible-range approximations only.
* UV, polarization, and full species-specific perception are not reproduced in v0.1.
* Reference modes are averaged profiles only and should not be treated as individual-level predictions.
* Evidence and model badges help communicate claim strength and implementation maturity, not certainty.

## Product positioning

AsSeenBy should feel closer to a field guide or visual reference plate than a dark startup dashboard. The app is meant to support comparison, understanding, and discussion rather than exact biological or medical claims.
