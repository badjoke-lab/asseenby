# AsSeenBy — Limitations

## Scope
AsSeenBy is a visual comparison tool built around browser-side rendering.
It is designed for exploration, explanation, and side-by-side inspection.

The public v0.1 experience uses browser-side image transforms. The spatial track adds live 3D rendering only for selected phenomena where space, view direction, or lighting materially affect the comparison.

## Image-source limitation
All current image outputs start from a standard RGB image.
That means the image track can only transform information already present in a conventional image file.

Because of that, the current image experience does not attempt to fully reproduce:
- ultraviolet response;
- polarization sensitivity;
- full species-specific spectral response;
- interpretation beyond image-space approximation.

## Spatial limitation
The spatial renderer is not limited to a static RGB photograph: it can use live scene geometry, view direction, depth, rendered luminance, screen-relative field position, and other renderer data.

That does **not** make it an exact reconstruction of lived perception.

The spatial experience does not include:
- patient-specific perimetry or scotoma measurements;
- measured lens-scatter parameters for a specific person;
- retinal / neural reconstruction;
- clinical validation;
- automatic diagnosis.

Therefore:
- Tunnel Vision may be dynamically and spatially modeled while remaining a generic peripheral field-loss profile;
- Central Loss may remain tied to the viewer's central field while remaining a generic central-loss profile rather than an individual's measured scotoma;
- Cataract-like glare may respond to actual scene brightness while remaining a generic impairment model.

The term `approximation` refers to this claim boundary. It should not be interpreted as permission to substitute a decorative static filter where live spatial modeling is required by the specification.

## Human-mode limitation
Human modes are simplified visual proxies or generic simulations.
They are useful for comparative viewing, but they are not exact reconstructions of lived perception.

Examples:
- color-deficiency-like image modes are matrix-based approximations;
- image blur and contrast modes are image-space approximations;
- current image tunnel and central-loss views are simplified transforms;
- spatial Tunnel Vision remains generic unless future work accepts measured individual field data;
- spatial Central Loss must not be interpreted as a patient's actual scotoma shape, size, opacity, severity, or perimetry result;
- spatial Cataract-like remains generic unless future work accepts validated individual optical measurements.

### Central Loss specific limitation
Real central vision loss can be irregular, incomplete, blurred, distorted, or experienced differently depending on condition and individual.

The spatial Central Loss mode therefore uses a deliberately generic central disruption for education and comparison. Its purpose is to demonstrate the consequence of reduced straight-ahead detail during active scene scanning, not to claim that people with macular disease see a fixed circular patch identical to the renderer output.

### Night / Low Light specific limitation
The current spatial Night / Low Light mode can use relative brightness differences in the rendered panorama, but the source is a tone-mapped RGB photograph rather than calibrated luminance or spectral data.

It therefore does not reproduce a validated scotopic/mesopic observer, dark-adaptation timing, pupil dynamics, complete rod/cone spectral response, or a specific person's night-vision impairment. It is a luminance-dependent comparison proxy: dark regions are made less informative relative to bright regions so users can inspect the consequence across one fixed scene.

## Animal-mode limitation
Animal modes in v0.1 are visible-range approximations only.
They should be read as comparison aids rather than complete reproductions.

Examples:
- bee mode does not reproduce ultraviolet vision;
- bird-like mode does not reproduce ultraviolet response or full avian perception;
- dog and cat modes are simplified visible-range approximations.

### Dog-like specific limitation
Canine dichromacy is well supported, but a conventional RGB panorama cannot recover the original scene spectra or exact canine cone catches. The spatial Dog-like output therefore translates broad two-channel color relationships onto a human RGB display and adds mild non-calibrated detail softening.

It does not model breed-dependent field of view, retinal topography, motion sensitivity, tapetal/rod-mediated low-light advantages, spectral metamerism, or neural interpretation. It should not be read as literal canine color qualia or as one universal view shared by all dogs.

### Cat-like spatial evaluation limitation
The separate spatial Cat-like candidate was rejected after same-camera review because its visible distinction from Dog-like was mainly a small increase in chromatic compression/desaturation and fine-detail softening. The current RGB source does not justify manufacturing a stronger feline-specific distinction.

The image-track Cat-like mode remains an explicitly cautious visible-range approximation. There is no accepted public Cat-like spatial renderer at this stage.

### Bird-like spatial evaluation limitation
Generic Bird-like spatial has been rejected/blocked for the current RGB panorama. Avian color systems include UVS/VS and tetrachromatic mechanisms with oil-droplet filtering that ordinary RGB cannot reconstruct, while measured acuity varies by roughly two orders of magnitude across bird species. A generic saturation/contrast boost or generic sharpen/blur effect would therefore imply a coherent “bird view” that the source data and taxonomic category do not support.

A future avian spatial mode must be species-specific and/or use additional spectral/UV scene data with a documented observer model.

### Bee-like spatial source-data limitation
A future spatial scene does not create missing UV information automatically. Bee-like UV work requires additional UV-reflectance/spectral scene/material data and an explicit false-color translation for human displays. Until those inputs exist, Bee-like spatial is blocked and no purple/blue RGB filter should be presented as bee vision.

## Reference-mode limitation
Reference modes are averaged profiles, not individual predictions.
They are intended as framing tools for comparison.

## Evidence-badge limitation
The evidence panel helps communicate claim strength and implementation maturity.
It does not convert the product into a validated medical or perceptual instrument.

Important reading rule:
- a higher evidence score does not mean the visual output is exact;
- a higher model score does not mean patient-level accuracy;
- lower scores may reflect unfinished review rather than a false phenomenon;
- spatial model maturity must be assessed separately from the existing 2D transform quality.

## Strength control limitation
The strength slider changes degree within the current image approximation model.
It does not map to a validated real-world severity scale unless a future mode explicitly documents such a mapping.

The current spatial field-loss modes do not expose a patient-severity control. Their generic profile should not be interpreted as a severity measurement.

## Product limitation
The v0.1 image product is intentionally limited to:
- static images only;
- browser-side processing only;
- no account system;
- no saved sessions;
- no server-side transformation.

The spatial experience is also browser-side and does not add accounts, saved sessions, or patient data collection.

## Reading rule
Treat each output as:
- a comparison aid;
- an educational simulation or approximation;
- a research-oriented visual proxy.

Do not treat each output as:
- exact biological truth;
- personal evaluation;
- diagnosis;
- a patient-specific reconstruction unless a future validated individual-data workflow explicitly says otherwise;
- certification.
