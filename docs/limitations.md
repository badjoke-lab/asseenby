# AsSeenBy — Limitations

## Scope
AsSeenBy is a visual comparison tool built around browser-side image transforms.
It is designed for exploration, explanation, and side-by-side inspection.

## Image-source limitation
All current outputs start from a standard RGB image.
That means the system can only transform information already present in a conventional image file.

Because of that, v0.1 does not attempt to fully reproduce:
- ultraviolet response
- polarization sensitivity
- full species-specific spectral response
- interpretation beyond image-space approximation

## Human-mode limitation
Human modes are simplified visual proxies.
They are useful for comparative viewing, but they are not exact reconstructions of lived perception.

Examples:
- color-deficiency-like modes are matrix-based approximations
- blur and contrast modes are image-space approximations
- tunnel and central-loss views are simplified masks

## Animal-mode limitation
Animal modes in v0.1 are visible-range approximations only.
They should be read as comparison aids rather than complete reproductions.

Examples:
- bee mode does not reproduce ultraviolet vision
- bird-like mode does not reproduce ultraviolet response or full avian perception
- dog and cat modes are simplified visible-range approximations

## Reference-mode limitation
Reference modes are averaged profiles, not individual predictions.
They are intended as framing tools for comparison.

## Strength control limitation
The strength slider changes degree within the current approximation model.
It does not map to a validated real-world scale.

## Product limitation
v0.1 is intentionally limited to:
- static images only
- browser-side processing only
- no account system
- no saved sessions
- no server-side transformation

## Reading rule
Treat each output as:
- a comparison aid
- an educational approximation
- a research-oriented visual proxy

Do not treat each output as:
- exact biological truth
- personal evaluation
- certification
