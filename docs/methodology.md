# AsSeenBy — Methodology

## Positioning
AsSeenBy is a research-based comparison and simulation tool.
It compares a baseline view with a transformed or simulated view that translates documented visual characteristics into a plausible viewing model.

It does not claim exact perceptual reproduction.
It is not a diagnostic or medical product.

## Two renderer tracks
AsSeenBy has two distinct implementation tracks.

### Image comparison
The current v0.1 experience starts from a standard RGB image and performs browser-side image transforms.

### Spatial comparison pilot
The experimental spatial track starts from a live rendered 3D scene. Where a visual phenomenon depends on space or lighting, the renderer should use scene-aware variables such as:
- view direction;
- camera state;
- depth;
- rendered luminance / bright-source information;
- screen-relative field position.

The spatial track must not be reduced to applying a pre-rendered 2D filter over a 3D canvas when the phenomenon being modeled is spatially dependent.

## What `approximation` means
`Approximation` describes the scientific claim boundary, not the implementation quality target.

A spatial mode can use a detailed dynamic renderer and still be an approximation because AsSeenBy is not supplied with patient-specific measurements, full biological sensing data, or a validated reconstruction of neural perception.

For example:
- Tunnel Vision can model live screen-relative peripheral field loss while remaining a generic field-loss profile rather than an individual's measured perimetry result;
- Cataract-like can make glare respond to actual bright scene sources while remaining a generic optical impairment model rather than a reconstruction of a particular person's lens scattering.

## Core limitation of the image track
All transformations in v0.1 image comparison start from a standard RGB image.
That means the image track is limited by what a conventional image already contains.

Because of that, the following are outside the current image scope:
- ultraviolet perception;
- polarization sensitivity;
- full species-specific spectral response;
- neural interpretation beyond image-space approximation;
- patient-level medical prediction.

## Comparison model
### Image comparison
Each simulation is shown against the original image.
The user can compare them through:
- slider;
- split;
- side-by-side.

The strength control changes the degree of transformation applied.

### Spatial comparison
The pilot compares the same rendered scene from the same camera state while only the perception renderer changes.

The initial spatial modes are:
- Normal;
- Tunnel Vision;
- Cataract-like.

Mode switching must preserve camera position and view direction so the comparison isolates the modeled visual difference.

## Evidence display model
Each mode can expose a mode-level evidence panel in the UI.
That panel is intended to show what kind of claim is being made and how mature the current approximation or simulation is.

The panel uses three axes:
- **Class** — Strong / Estimated / Reference;
- **Evidence** — A / B / C / D for the underlying phenomenon or viewing basis;
- **Model** — A / B / C / D for the current implementation maturity.

This means a mode can have strong evidence for the underlying phenomenon while still having only moderate confidence in the current browser-side implementation.

For spatial modes, model maturity must reflect the spatial implementation itself rather than automatically inheriting confidence from the 2D renderer.

## Human modes
Human modes are divided into two groups.

### Strong
These are first-pass public approximations that have the clearest justification for comparison.
Examples:
- protan-like;
- deutan-like;
- tritan-like;
- blur;
- low contrast;
- tunnel vision;
- central loss;
- cataract-like.

### Estimated
These are useful but more interpretive viewing profiles.
Examples:
- night / low light;
- fatigue-like;
- dry-eye-like.

## Animal modes
Animal modes in v0.1 are visible-range approximations only.
They are included for comparison and education, not as claims of full species reproduction.

Included animal modes:
- dog-like;
- cat-like;
- bee-like;
- bird-like.

Important note:
- bee and bird modes in v0.1 do not reproduce ultraviolet response;
- none of the animal modes reproduce the full perceptual world of the species.

A future Bee-like spatial mode must not invent UV information from RGB scene color. It requires additional scene/material data such as documented UV-reflectance information plus a false-color display mapping.

## Reference modes
Reference modes are deliberately weaker claims.
They represent averaged profiles rather than individual prediction.

Included:
- age profile;
- sex-difference profile.

These should not be interpreted as personal diagnosis or exact individual simulation.

## Implementation approach in v0.1 image comparison
- browser-side image processing only;
- no server-side image transformation;
- no stored uploads;
- static-image only;
- per-mode evidence metadata attached in the UI layer.

This keeps the product lightweight and privacy-friendly for the initial release.

## Spatial pilot implementation approach
- Three.js runs browser-side;
- one controlled night-street scene first;
- scene-aware post-processing where required by the mode;
- no accounts or server-side user data requirement;
- no game mechanics required;
- the current 2D transform engine remains in place;
- spatial expansion is conditional on the acceptance gate in `docs/spatial-pilot-spec.md`.

## Practical reading rule
Users should treat each output as:
- a comparison aid;
- an educational or exploratory simulation;
- a research-oriented visual proxy.

Users should not treat each output as:
- medical advice;
- diagnosis;
- exact biological truth;
- a patient-specific reconstruction unless a future validated individual-data workflow explicitly says otherwise;
- legal or accessibility certification.
