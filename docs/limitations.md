# AsSeenBy — Limitations

## Scope
AsSeenBy is a visual comparison tool built around browser-side rendering.
It is designed for exploration, explanation, and side-by-side inspection.

The current public v0.1 experience uses browser-side image transforms. An experimental spatial track may add live 3D rendering for selected phenomena where space, view direction, or lighting materially affect the comparison.

## Image-source limitation
All current image outputs start from a standard RGB image.
That means the image track can only transform information already present in a conventional image file.

Because of that, the current image experience does not attempt to fully reproduce:
- ultraviolet response;
- polarization sensitivity;
- full species-specific spectral response;
- interpretation beyond image-space approximation.

## Spatial-pilot limitation
The spatial pilot is not limited to a static RGB photograph: it can use live scene geometry, view direction, depth, rendered luminance, and other renderer data.

That does **not** make it an exact reconstruction of lived perception.

The pilot does not include:
- patient-specific perimetry or optical measurements;
- measured lens-scatter parameters for a specific person;
- retinal / neural reconstruction;
- clinical validation;
- automatic diagnosis.

Therefore:
- Tunnel Vision may be dynamically and spatially modeled while remaining a generic field-loss profile;
- Cataract-like glare may respond to actual scene brightness while remaining a generic impairment model.

The term `approximation` refers to this claim boundary. It should not be interpreted as permission to substitute a decorative static filter where scene-aware modeling is required by the spatial specification.

## Human-mode limitation
Human modes are simplified visual proxies or generic simulations.
They are useful for comparative viewing, but they are not exact reconstructions of lived perception.

Examples:
- color-deficiency-like image modes are matrix-based approximations;
- image blur and contrast modes are image-space approximations;
- current image tunnel and central-loss views are simplified masks;
- spatial Tunnel Vision remains generic unless future work accepts measured individual field data;
- spatial Cataract-like remains generic unless future work accepts validated individual optical measurements.

## Animal-mode limitation
Animal modes in v0.1 are visible-range approximations only.
They should be read as comparison aids rather than complete reproductions.

Examples:
- bee mode does not reproduce ultraviolet vision;
- bird-like mode does not reproduce ultraviolet response or full avian perception;
- dog and cat modes are simplified visible-range approximations.

A future spatial scene does not create missing UV information automatically. Bee-like UV work requires additional UV-reflectance scene/material data and an explicit false-color translation for human displays.

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
The strength slider changes degree within the current approximation model.
It does not map to a validated real-world severity scale unless a future mode explicitly documents such a mapping.

## Product limitation
The v0.1 image product is intentionally limited to:
- static images only;
- browser-side processing only;
- no account system;
- no saved sessions;
- no server-side transformation.

The spatial pilot is also browser-side and does not add accounts, saved sessions, or patient data collection.

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
