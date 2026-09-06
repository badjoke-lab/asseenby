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

The strength control changes the degree of transformation applied. At 0%, Approximation is the Original source with no perception transform; 100% applies the full configured transform for that mode. Intermediate values interpolate within the renderer model and are not a validated clinical severity scale.

### Spatial comparison
Spatial comparison uses the same rendered scene from the same camera state while only the perception renderer changes.

Accepted spatial modes:
- Normal;
- Tunnel Vision;
- Central Loss;
- Night / Low Light;
- Dog-like;
- Cataract-like.

Evaluated and rejected spatial candidate:
- Cat-like — technically valid renderer candidate, but not distinct enough from Dog-like to justify a separate spatial claim from the current RGB source.

Evaluated and rejected/blocked spatial candidate:
- Bird-like — the current RGB source cannot support a generic avian observer without fabricating missing tetrachromatic/UV information, and species-level acuity/spectral variation is too large for one generic renderer.

Blocked spatial candidate:
- Bee-like — requires UV-reflectance/spectral scene data before implementation.

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

## Night / Low Light spatial model
The current spatial target is a luminance-dependent low-light communication model. It uses relative displayed luminance in the rendered 360° view so darker regions can lose more color, contrast, and fine detail than brighter regions.

The source panorama is tone-mapped RGB rather than calibrated radiometric data. The spatial mode therefore does not model physical cd/m², full rod/cone spectral sensitivity, pupil response, or the time course of dark adaptation. Those limitations are part of the model definition, not hidden implementation details.

## Dog-like spatial model
The accepted Dog-like renderer combines a simplified visible-range dichromatic translation with mild loss of fine detail. The phenomenon basis is stronger than the renderer: canine dichromacy and lower acuity are supported by behavioral/physiological literature, but a standard RGB panorama does not contain the spectral information needed to calculate exact canine photoreceptor catches for arbitrary real-world materials and lights.

For that reason the renderer keeps Evidence and Model separate: the broad canine visual differences can retain strong evidence while the spatial implementation remains Model C. Field of view, motion processing, tapetal/rod low-light advantages and neural interpretation are intentionally excluded from this phase.

## Cat-like spatial evaluation
A Cat-like spatial candidate was implemented with conservative chromatic compression and slightly stronger fine-detail softening. Automated browser validation passed, but same-camera rendered review found that its explanatory difference from the accepted Dog-like mode was mostly a small degree change in chroma and blur.

Because the feline literature contains historical uncertainty and the RGB panorama cannot recover exact feline spectral catches, the project rejected the spatial Cat-like control rather than exaggerating unsupported differences. R7 later removed the separate image-track Cat-like mode after its own rendered-output audit reached the same product conclusion: the available RGB proxy did not justify a distinct feline observer claim. Cat-like is therefore absent from both current public tracks.

## Bird-like spatial evaluation result
Bird-like was evaluated as a source-data/evidence question before shader work and was rejected/blocked for the current generic RGB setup. Ordinary RGB cannot reconstruct ultraviolet/violet-sensitive cone catches, tetrachromatic color relationships, species-specific oil-droplet filtering, or polarization sensitivity. In addition, comparative data show very large species variation in avian acuity, making a generic spatial sharpness rule misleading.

R7 later removed the former image Bird-like mode as well. Its visible-range saturation/microcontrast transform had Model D and could not represent avian tetrachromacy, UVS/VS variation, oil-droplet filtering, species-specific acuity, or a defensible generic avian observer. Bird-like is therefore absent from both current public tracks under the ordinary-RGB source boundary.

## Bee-like spatial source-data result
Bee-like remains blocked until UV-reflectance/spectral scene data are available. A future implementation must model a documented bee observer and then translate that result to a human display with explicit false-color caveats; ordinary RGB cannot supply the missing UV channel after capture.

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
Human modes use Strong / Estimated classes where applicable.

### Strong
The current public image Human set contains the first-pass approximations with the clearest justification for static comparison:
- protan-like;
- deutan-like;
- tritan-like;
- blur;
- low contrast;
- tunnel vision;
- central loss;
- cataract-like.

### Estimated
There are currently no Estimated Human modes in public image comparison. Night / Low Light remains an Estimated spatial-only mode because its live renderer can at least respond to relative displayed luminance in the accepted panorama. Fatigue-like and Dry-eye-like image modes were removed during R7 rather than retain symptom-cluster proxies that the static renderer could not justify as distinct observer models.

## Animal modes
Animal modes in v0.1 are visible-range approximations only.
They are included for comparison and education, not as claims of full species reproduction.

Current public animal image mode:
- dog-like.

Cat-like, Bird-like, and Bee-like image modes were removed during R7 because the former generic RGB transforms did not justify distinct species-specific observer claims. Dog-like remains a conservative visible-range proxy and does not reproduce the full canine perceptual world.

A future Bee-like spatial mode must not invent UV information from RGB scene color. It requires additional scene/material data such as documented UV-reflectance information plus a false-color display mapping.

## Reference-mode status
The current public release has no Reference modes. Earlier Age Profile and sex-difference presets were removed during R7 because their broad population labels did not define a sufficiently specific observer for the renderer. The evidence model retains a Reference class only for future datasets with an explicit population, variable, and mapping.

## Implementation approach in v0.1 image comparison
- browser-side image processing only;
- no server-side image transformation;
- no stored uploads;
- static-image only;
- per-mode evidence metadata attached in the UI layer.

## Spatial implementation approach
- Three.js runs browser-side;
- the accepted fixed-viewpoint 360° photographic night-city reference is reused while post-pilot modes are evaluated;
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
