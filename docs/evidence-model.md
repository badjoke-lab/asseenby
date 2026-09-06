# AsSeenBy — Evidence Model

## Why this exists
AsSeenBy exposes mode-level evidence metadata inside the UI.
That means each mode can show:
- a class badge
- an evidence badge
- a model badge
- a summary
- a caveat
- basis notes
- implementation notes
- primary and supporting sources

This document defines what those labels mean.

## Three badge axes

### 1. Class
Class describes the claim type of the mode itself.
It is not a judgment about link quality.

- **Strong**
  - the mode has a comparatively clear justification for visual comparison / simulation
  - examples: color-deficiency-like transforms, blur, low contrast, field-loss models, cataract-like viewing

- **Estimated**
  - the mode is useful, but more interpretive
  - current examples: animal visible-range proxies and renderer-specific approximations such as spatial Night / Low Light

- **Reference**
  - the mode is presented as an averaged profile or framing device rather than a direct individual simulation

### 2. Evidence
Evidence describes how strong the basis is for the underlying visual phenomenon or viewing tendency.
It does **not** automatically mean the current rendered output is exact.

- **A**
  - strong primary or organization-level support
  - the phenomenon is well described in established references
- **B**
  - credible support exists, but the evidence set is narrower or less direct
- **C**
  - partial support exists, but the phenomenon-to-mode framing is still limited or mixed
- **D**
  - review still pending or evidence not yet organized for public display

### 3. Model
Model describes how strong the current implementation is for the renderer being used.
This is about the actual simulation logic, not just the existence of sources.

- **A**
  - the implementation is a comparatively direct fit for the visual effect being shown
- **B**
  - the implementation is reasonable, but still simplified
- **C**
  - the implementation expresses a tendency, but remains notably heuristic
- **D**
  - provisional implementation or source review still pending

## Renderer-specific model confidence
The same named mode can have different implementation maturity in different renderer tracks.

For example:
- the current 2D Tunnel Vision image transform is a simplified screen-space mask;
- the current spatial Tunnel Vision implementation uses a live view-relative field model;
- the underlying phenomenon evidence can remain the same while the `Model` assessment differs between the image and spatial implementations.

Likewise, a spatial Cataract-like renderer that reacts to live scene luminance should not automatically inherit the model grade of the existing static-image transform. Its implementation must be reviewed on its own behavior.

Therefore spatial metadata or implementation notes must distinguish which renderer a model assessment refers to whenever there is a meaningful difference.

Implementation note: `src/modeEvidence.ts` is a shared phenomenon-evidence base, not an image-mode registry. It may contain a key that is not selectable in image comparison when a spatial renderer reuses the same phenomenon sources. Currently `night` is intentionally retained for the spatial-only Night / Low Light evidence panel, while image visibility remains controlled by `src/modes.ts`.

## Reading rule
A mode can have:
- strong evidence for the phenomenon
- but only medium confidence in the current renderer implementation

That is normal.
For example, a condition may be well established clinically while a browser-side visual model remains a simplified proxy.

A dynamic or visually sophisticated 3D result is not automatically more scientifically exact.

## Source display rules
Each mode can expose:
- **Primary source**
  - the main anchor for the mode's evidence framing or implementation direction
- **Supporting sources**
  - additional clinical, review, or reference materials

When many links exist, only a subset should appear by default, with the remainder behind an expandable list.

Supporting sources should be shown in a stable priority order:
1. review
2. paper
3. organization
4. reference

This keeps the panel readable and makes the supporting list less dependent on raw input order.

## What the badges do not mean
The badge system does not claim:
- medical validation
- patient-level prediction
- exact perceptual reproduction
- legal or accessibility certification

The badges are there to help users distinguish:
- what kind of claim is being made
- how strong the basis is
- how mature the current renderer implementation is

## Operational rule
If a mode or renderer implementation has not yet completed source / model review, it should stay conservative:
- lower evidence score where evidence review is incomplete
- lower model score where implementation maturity is incomplete
- explicit caveat
- no exaggerated wording
