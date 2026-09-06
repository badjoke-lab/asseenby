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
- spatial status: accepted post-pilot mode
- spatial renderer: live view-relative central-field-loss simulation; straight-ahead detail is degraded while surrounding scene information remains more available, and the affected region stays centered in the viewer's field during look-around
- spatial limitation: generic central-loss / scotoma-style profile, not an individual's measured scotoma or perimetry result

### Night / Low Light
- class: Estimated
- goal: low-light viewing approximation
- spatial status: accepted post-pilot mode
- spatial renderer target: luminance-dependent loss of chromatic separation, contrast, and fine detail in darker rendered regions while brighter regions remain comparatively available
- spatial limitation: tone-mapped RGB provides relative displayed brightness only; no calibrated scotopic/mesopic luminance, dark-adaptation timing, or patient-specific night-vision reconstruction

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
- spatial status: accepted post-pilot mode
- spatial renderer: conservative human-display visible-range dichromatic translation plus non-calibrated fine-detail softening


## Reference modes
### Age Profile
- class: Reference
- goal: age-related viewing profile approximation
