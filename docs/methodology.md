# AsSeenBy — Methodology

## Positioning
AsSeenBy is a research-based comparison and simulation tool.
It compares a baseline view with a transformed or simulated view that translates documented visual characteristics into a plausible viewing model.

It does not claim exact perceptual reproduction.
It is not a diagnostic or medical product.

## Two renderer tracks
AsSeenBy has two distinct implementation tracks.

### Image comparison
The v0.1 experience starts from a standard RGB image and performs browser-side image transforms.

### Spatial comparison
The spatial track starts from a live rendered 3D scene. Where a visual phenomenon depends on space or lighting, the renderer should use scene-aware variables such as:
- view direction;
- camera state;
- depth;
- rendered luminance / bright-source information;
- screen-relative field position.

The spatial track must not be reduced to applying a pre-rendered 2D filter over a 3D canvas when the phenomenon being modeled is spatially dependent.

## What `approximation` means
`Approximation` describes the scientific claim boundary, not the implementation quality target.

A spatial mode can use a detailed dynamic renderer and still be an approximation because AsSeenBy is not supplied with patient-specific measurements, full biological sensing data, or a validated reconstruction of neural perception.

Examples:
- Tunnel Vision can model live screen-relative peripheral field loss while remaining a generic field-loss profile rather than an individual's measured perimetry result;
- Cataract-like can make glare respond to actual bright scene sources while remaining a generic optical impairment model rather than a reconstruction of a particular person's lens scattering;
- Central Loss can keep a disrupted region tied to straight-ahead vision while the user scans the scene, while still remaining a generic central-field-loss profile rather than an individual's measured scotoma.

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
Spatial comparison uses the same rendered scene from the same camera state while only the perception renderer changes.

Accepted baseline spatial modes:
- Normal;
- Tunnel Vision;
- Cataract-like.

Current expansion target:
- Central Loss.

Mode switching must preserve camera position and view direction so the comparison isolates the modeled visual difference.

For field-loss modes, the affected field is view-relative rather than attached to a world-space object. This is central to the spatial comparison value: looking around changes which scene content falls inside the affected part of vision.

## Central Loss spatial model
The current design target is a generic central-field-loss simulation.

It should:
- degrade or obscure straight-ahead detail more strongly than surrounding scene information;
- remain centered in the viewer's field as camera direction changes;
- operate on the live rendered scene;
- demonstrate that centering a target can make that target harder to inspect;
- avoid implying that the chosen central-loss shape, size, opacity, or severity maps to an individual patient.

The implementation may combine localized softness, desaturation, and partial obscuration to communicate loss of central detail. The exact visual form remains a renderer model and must be rated separately from the evidence for central vision loss itself.

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

## Spatial implementation approach
- Three.js runs browser-side;
- the accepted controlled night-street scene is reused while the current field-loss expansion is evaluated;
- scene-aware / view-relative post-processing is used where required by the mode;
- no accounts or server-side user data requirement;
- no game mechanics required;
- the current 2D transform engine remains in place;
- new spatial modes are added one at a time and require their own rendered acceptance gate.

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
