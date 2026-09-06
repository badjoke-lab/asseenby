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
- goal: protanomaly-style color-discrimination approximation
- image renderer: Machado pre-computed protanomaly matrices, interpolated by Strength and applied in linear RGB
- note: not diagnostic; Strength is not an individual clinical severity measurement

### Deutan-like
- class: Strong
- goal: deuteranomaly-style color-discrimination approximation
- image renderer: Machado pre-computed deuteranomaly matrices, interpolated by Strength and applied in linear RGB
- note: not diagnostic; Strength is not an individual clinical severity measurement

### Tritan-like
- class: Strong
- goal: tritanomaly-style blue-yellow discrimination approximation
- image renderer: Machado pre-computed tritanomaly matrices, interpolated by Strength and applied in linear RGB
- note: not diagnostic; the cited tritan model is itself approximate and is not a literal patient-specific tritanopia reconstruction

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
- image status: removed in R7; the former static RGB transform was not retained as a validated low-light observer model
- spatial status: accepted post-pilot mode
- spatial renderer target: luminance-dependent loss of chromatic separation, contrast, and fine detail in darker rendered regions while brighter regions remain comparatively available
- spatial limitation: tone-mapped RGB provides relative displayed brightness only; no calibrated scotopic/mesopic luminance, dark-adaptation timing, or patient-specific night-vision reconstruction



## Animal modes
### Dog
- class: Estimated
- goal: dog-like visible-range approximation
- image status: retained after R7 audit with a narrowed human-display observer proxy
- image renderer: linear-RGB red-green-deficiency mapping plus restrained red-green compression, contrast reduction, and fine-detail softening; not a canine cone-catch reconstruction
- spatial status: accepted post-pilot mode
- spatial renderer: conservative human-display visible-range dichromatic translation plus non-calibrated fine-detail softening

