# AsSeenBy — Methodology

## Positioning
AsSeenBy is a research-based approximation tool.
It compares an original image with a transformed version that represents a plausible viewing profile.

It does not claim exact perceptual reproduction.
It is not a diagnostic or medical product.

## Core limitation
All transformations in v0.1 start from a standard RGB image.
That means the system is limited by what a conventional image already contains.

Because of that, the following are outside v0.1 scope:
- ultraviolet perception
- polarization sensitivity
- full species-specific spectral response
- neural interpretation beyond image-space approximation
- patient-level medical prediction

## Comparison model
Each simulation is shown against the original image.
The user can compare them through:
- slider
- split
- side-by-side

The strength control changes the degree of transformation applied.

## Evidence display model
Each mode can expose a mode-level evidence panel in the UI.
That panel is intended to show what kind of claim is being made and how mature the current approximation is.

The panel uses three axes:
- **Class** — Strong / Estimated / Reference
- **Evidence** — A / B / C / D for the underlying phenomenon or viewing basis
- **Model** — A / B / C / D for the current implementation maturity

This means a mode can have strong evidence for the underlying phenomenon while still having only moderate confidence in the current browser-side transform.

## Human modes
Human modes are divided into two groups.

### Strong
These are first-pass public approximations that have the clearest justification for image-space simulation.
Examples:
- protan-like
- deutan-like
- tritan-like
- blur
- low contrast
- tunnel vision
- central loss
- cataract-like

### Estimated
These are useful but more interpretive viewing profiles.
Examples:
- night / low light
- fatigue-like
- dry-eye-like

## Animal modes
Animal modes in v0.1 are visible-range approximations only.
They are included for comparison and education, not as claims of full species reproduction.

Included animal modes:
- dog
- cat
- bee
- bird-like

Important note:
- bee and bird modes in v0.1 do not reproduce ultraviolet response
- none of the animal modes reproduce the full perceptual world of the species

## Reference modes
Reference modes are deliberately weaker claims.
They represent averaged profiles rather than individual prediction.

Included:
- age profile
- sex-difference profile

These should not be interpreted as personal diagnosis or exact individual simulation.

## Implementation approach in v0.1
- browser-side image processing only
- no server-side image transformation
- no stored uploads
- static-image only
- per-mode evidence metadata attached in the UI layer

This keeps the product lightweight and privacy-friendly for the initial release.

## Practical reading rule
Users should treat each output as:
- a comparison aid
- an educational or exploratory approximation
- a research-oriented visual proxy

Users should not treat each output as:
- medical advice
- diagnosis
- exact biological truth
- legal or accessibility certification
