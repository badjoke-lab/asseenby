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
- Fatigue-like is no longer public because digital eye strain is a symptom cluster rather than one validated visual phenotype, and the former renderer only combined generic blur with contrast reduction;
- Dry-eye-like is no longer public because blur/fluctuating clarity are real symptoms but the former static renderer added fixed localized artifacts that were not derived from tear-film measurements or a validated dry-eye observer model;
- current image tunnel and central-loss views are simplified transforms;
- spatial Tunnel Vision remains generic unless future work accepts measured individual field data;
- spatial Central Loss must not be interpreted as a patient's actual scotoma shape, size, opacity, severity, or perimetry result;
- spatial Cataract-like remains generic unless future work accepts validated individual optical measurements.

### Central Loss specific limitation
Real central vision loss can be irregular, incomplete, blurred, distorted, or experienced differently depending on condition and individual.

The spatial Central Loss mode therefore uses a deliberately generic central disruption for education and comparison. Its purpose is to demonstrate the consequence of reduced straight-ahead detail during active scene scanning, not to claim that people with macular disease see a fixed circular patch identical to the renderer output.

### Night / Low Light specific limitation
The former static-image Night / Low Light mode was removed in R7. A conventional uploaded RGB image has unknown exposure, tone mapping, scene luminance, and adaptation context, so applying a uniform dark/desaturated transform would imply a low-light observer state that the input does not establish.

The current spatial Night / Low Light mode remains because it can at least use relative brightness differences in the rendered panorama, but the source is still a tone-mapped RGB photograph rather than calibrated luminance or spectral data.

It therefore does not reproduce a validated scotopic/mesopic observer, dark-adaptation timing, pupil dynamics, complete rod/cone spectral response, or a specific person's night-vision impairment. It is a luminance-dependent comparison proxy: dark regions are made less informative relative to bright regions so users can inspect the consequence across one fixed scene.

## Animal-mode limitation
Animal modes in v0.1 are visible-range approximations only.
They should be read as comparison aids rather than complete reproductions.

Examples:
- Dog-like remains a simplified visible-range approximation.
- Cat-like is no longer publicly rendered because the former RGB proxy was not independently justified strongly enough from Dog-like.
- Bird-like is not publicly rendered from ordinary RGB because a generic avian observer cannot be reconstructed from three camera channels.
- Bee-like is not publicly rendered from ordinary RGB because ultraviolet/spectral scene information is absent.

### Dog-like specific limitation
Canine dichromacy is well supported, including behavioral results that resemble human red-green color deficiency, but ordinary RGB cannot recover original scene spectra or exact canine cone catches. The audited image renderer therefore uses a linear-RGB red-green-deficiency mapping only as a human-display proxy, with restrained contrast and detail changes rather than a bespoke species-specific RGB matrix. The spatial Dog-like renderer remains a separate visible-range proxy on the accepted panorama.

Neither renderer models breed-dependent field of view, retinal topography, motion sensitivity, tapetal/rod-mediated low-light advantages, spectral metamerism, exact canine acuity, or neural interpretation. They should not be read as literal canine color qualia or as one universal view shared by all dogs.

### Cat-like image and spatial evaluation limitation
The separate spatial Cat-like candidate was rejected after same-camera review because its visible distinction from Dog-like was mainly small chromatic and softening changes. R7 later audited the image renderer against Dog-like on the built-in sample and a controlled color/detail chart and reached the same product conclusion: the former Cat-specific RGB matrix was a heuristic, not a transform derived from measured feline cone catches or a validated feline observer model.

Domestic-cat dichromatic color behavior has research support, but that evidence does not validate the former hand-tuned Dog-versus-Cat RGB difference. The public Cat-like image mode was therefore removed rather than strengthened. A future Cat-like renderer requires a documented feline observer mapping and source-data assumptions strong enough to justify a separate species-specific output.

### Bird-like spatial evaluation limitation
Generic Bird-like spatial has been rejected/blocked for the current RGB panorama. Avian color systems include UVS/VS and tetrachromatic mechanisms with oil-droplet filtering that ordinary RGB cannot reconstruct, while measured acuity varies by roughly two orders of magnitude across bird species. A generic saturation/contrast boost or generic sharpen/blur effect would therefore imply a coherent “bird view” that the source data and taxonomic category do not support.

The former Bird-like image mode was also removed during R7 because its saturation/microcontrast adjustment could not represent tetrachromacy, UVS/VS variation, oil-droplet filtering, species-specific acuity, or a defensible generic avian observer.

A future avian image or spatial mode must be species-specific and/or use additional spectral/UV scene data with a documented observer model.

### Bee-like source-data limitation
Bee-like image and spatial rendering are both blocked from ordinary RGB. A conventional image has already collapsed the ultraviolet/spectral information needed to estimate honeybee UV/blue/green receptor relationships, so a visible RGB color shift is not retained as a public bee-view proxy.

Future Bee-like work requires additional UV-reflectance/spectral scene or material data and an explicit false-color translation for human displays. Until those inputs exist, no purple/blue RGB filter should be presented as bee vision.

## Evidence-badge limitation
The evidence panel helps communicate claim strength and implementation maturity.
It does not convert the product into a validated medical or perceptual instrument.

Important reading rule:
- a higher evidence score does not mean the visual output is exact;
- a higher model score does not mean patient-level accuracy;
- lower scores may reflect unfinished review rather than a false phenomenon;
- spatial model maturity must be assessed separately from the existing 2D transform quality.

## Strength control limitation
The strength slider changes degree within the current image approximation model. At 0%, the image comparison uses the Original source without a perception transform; 100% applies the mode's full configured transform.
Intermediate percentages are renderer intensity controls, not validated real-world severity values. They do not map to a clinical scale unless a future mode explicitly documents such a mapping.

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
