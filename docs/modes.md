# AsSeenBy — Modes

## Confidence classes
Each mode belongs to one of three confidence classes.

### Strong
Research-backed approximations that are suitable for first-pass public comparison.

### Estimated
Approximate profiles that are useful for comparison, but should be read more cautiously.

### Reference
Average-profile reference modes. These are not individual-level predictions.

## Renderer note
A named mode can have more than one renderer implementation.

The v0.1 modes use the image renderer. The spatial experience adds separate live 3D implementations only where space, view direction, depth, or lighting materially improves the comparison.

The existence of a spatial implementation does not change the mode's evidence class automatically, and spatial model maturity is reviewed separately from the existing image transform.

## Human modes
### Protan-like
- class: Strong
- goal: reduced red-channel discrimination approximation
- note: not diagnostic; intended for visual comparison only

### Deutan-like
- class: Strong
- goal: reduced green-channel discrimination approximation
- note: not diagnostic; intended for visual comparison only

### Tritan-like
- class: Strong
- goal: blue-yellow discrimination shift approximation
- note: not diagnostic; intended for visual comparison only

### Blur
- class: Strong
- goal: lower visual sharpness approximation

### Low Contrast
- class: Strong
- goal: reduced contrast sensitivity approximation

### Cataract-like
- class: Strong
- goal: hazy, lower-contrast, yellowed viewing approximation
- image renderer: current static-image transform
- spatial status: accepted initial pilot mode
- spatial renderer: scene-dependent simulation using live rendered high-luminance information so bright sources can produce stronger glare / spread as the camera turns toward them
- spatial limitation: generic model, not a reconstruction of an individual's lens scattering

### Tunnel Vision
- class: Strong
- goal: peripheral field loss approximation
- image renderer: current simplified screen-space mask
- spatial status: accepted initial pilot mode
- spatial renderer: live view-relative peripheral field-loss simulation on the rendered scene
- spatial limitation: generic field-loss profile, not an individual's measured perimetry result

### Central Loss
- class: Strong
- goal: central field loss approximation
- image renderer: current localized central-loss transform
- spatial status: active post-pilot expansion target
- spatial renderer target: live view-relative central-field-loss simulation; straight-ahead detail is degraded while surrounding scene information remains more available, and the affected region stays centered in the viewer's field during look-around
- spatial limitation: generic central-loss / scotoma-style profile, not an individual's measured scotoma or perimetry result

### Night / Low Light
- class: Estimated
- goal: low-light viewing approximation
- spatial status: next candidate only after Central Loss acceptance

### Fatigue-like
- class: Estimated
- goal: fatigue-related viewing softness approximation

### Dry-eye-like
- class: Estimated
- goal: uneven blur and glare approximation

## Animal modes
### Dog
- class: Estimated
- goal: dog-like visible-range approximation
- spatial status: deferred until the ordered human spatial expansion reaches it

### Cat
- class: Estimated
- goal: cat-like visible-range approximation
- spatial status: deferred until the ordered human spatial expansion reaches it

### Bee
- class: Estimated
- goal: bee-like visible-range approximation
- limitation: UV is not reproduced by the current image mode
- spatial rule: a future UV-aware implementation requires additional UV-reflectance scene/material data and must not invent UV from ordinary RGB color

### Bird-like
- class: Estimated
- goal: bird-like visible-range approximation
- limitation: UV is not reproduced
- spatial status: deferred for separate evaluation after earlier spatial candidates

## Reference modes
### Age Profile
- class: Reference
- goal: age-related viewing profile approximation

### Sex-difference Profile
- class: Reference
- goal: averaged sex-difference reference mode
- note: should not be treated as an individual-level prediction
