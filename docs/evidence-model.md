# AsSeenBy — Evidence Model

## Why this exists
AsSeenBy now exposes mode-level evidence metadata inside the UI.
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
  - the mode has a comparatively clear justification for image-space approximation
  - examples: color-deficiency-like transforms, blur, low contrast, field masks, cataract-like viewing

- **Estimated**
  - the mode is useful, but more interpretive
  - examples: night / low light, fatigue-like, dry-eye-like, animal visible-range proxies

- **Reference**
  - the mode is presented as an averaged profile or framing device rather than a direct individual simulation

### 2. Evidence
Evidence describes how strong the basis is for the underlying visual phenomenon or viewing tendency.
It does **not** automatically mean the current image output is exact.

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
Model describes how strong the current implementation is as a screen-space approximation.
This is about the transform logic, not just the existence of sources.

- **A**
  - the implementation is a comparatively direct fit for the visual effect being shown
- **B**
  - the implementation is reasonable, but still simplified
- **C**
  - the implementation expresses a tendency, but remains notably heuristic
- **D**
  - provisional implementation or source review still pending

## Reading rule
A mode can have:
- strong evidence for the phenomenon
- but only medium confidence in the current transform

That is normal.
For example, a condition may be well established clinically while the browser-side image model remains a simplified proxy.

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
- how mature the current transform is

## Operational rule
If a mode has not yet completed source review, it should stay conservative:
- lower evidence score
- lower model score
- explicit caveat
- no exaggerated wording
