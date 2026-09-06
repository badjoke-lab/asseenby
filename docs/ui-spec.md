# AsSeenBy — UI Spec

## Visual direction
- off-white background
- serif-led typography
- restrained editorial layout
- quiet, research-book tone
- no dark SaaS styling
- no glow / glass / startup-style effects

## Core layout
### Desktop
- header at top
- hero intro block
- main compare stage on left
- control rail on right
- Human / Animal panels below

### Mobile
- stacked layout
- compare stage first
- controls below
- category panels stacked

## Primary experience switch
The existing image workflow remains primary and intact.

Experiences:
- **Compare image**
- **Explore 3D**

The switch must not make the 3D experience look like a separate game or product.

### Compare image
Uses the existing slider / split / side-by-side image comparison flow.

### Explore 3D
Shows the controlled spatial test scene and a restrained mode switch for accepted / active spatial modes.

Current 3D mode controls:
- Normal
- Tunnel Vision
- Central Loss
- Night / Low Light
- Dog-like
- Cataract-like

Dog-like is accepted and public. Cat-like spatial was rejected after rendered review. Generic Bird-like spatial was rejected/blocked at the evidence/source-data gate, and Bee-like is blocked pending UV-reflectance/spectral scene data. There are intentionally no Cat-like, Bird-like, or Bee-like controls in Explore spatial under the current source-data boundary.

Mode switching must keep the current camera state. The UI should make it obvious that the user is comparing the same scene/view under different rendering models.

## Compare modes
Image comparison:
- slider
- split
- side-by-side

Spatial comparison:
- direct mode switching;
- do not add a second simultaneous dual-render layout unless separately justified and performance-tested.

## Control rail
Image comparison:
- category select
- mode select
- strength slider
- upload image
- use sample image
- confidence badge
- short note and warning

Spatial experience:
- active spatial mode
- concise interaction hint
- evidence / limitation access
- reset-view control only if needed

Do not expose game-like movement, speed, graphics-quality, inventory, score, or decorative HUD controls.

## Spatial interaction
Desktop:
- pointer drag to look around
- keyboard look-around when the scene has focus
- restrained zoom only if separately justified

Mobile:
- touch drag to look around
- controls remain reachable without covering most of the scene

The scene does not require free walking.

## Central Loss UI behavior
When Central Loss is selected:
- keep the current camera position and direction;
- keep the disrupted region centered in the rendered visual field;
- do not draw a world-space marker suggesting the loss belongs to one scene object;
- explanatory copy should state that straight-ahead detail is degraded while surrounding information remains more available;
- evidence / limitation copy should state that the profile is generic, not an individual's measured scotoma.

## Night / Low Light UI behavior
When Night / Low Light is selected:
- keep the current camera position and direction;
- explain that darker rendered regions lose more color, contrast, and fine detail while brighter regions remain more available;
- do not describe the output as calibrated scotopic vision or a patient's measured night-vision deficit;
- make the tone-mapped RGB / non-calibrated-luminance boundary available in the evidence panel.

## Dog-like UI behavior
When Dog-like is selected:
- keep the current camera position, direction, field of view and source scene;
- explain that the mode is a visible-range human-display proxy for canine dichromacy plus lower fine-detail resolution;
- do not describe the output as exact canine cone catches, literal canine color experience, or a breed-independent complete visual system;
- make the RGB spectral-data limitation and excluded field-of-view/motion/low-light claims available in the evidence panel.

## Labels
Each current public mode should display one of:
- Strong
- Estimated

The evidence model may retain a Reference class for future explicitly defined reference datasets, but no public Reference mode is included in the current release.

Spatial mode UI must also communicate that the current output is a generic research simulation unless future work explicitly provides validated individual measurement support.

## Editorial notes
The app should feel closer to a modern field guide, visual reference plate, or interactive research exhibit than a startup dashboard or video game.

Three.js rendering must inherit that presentation: clean labels, subdued chrome, evidence visibility, and no gratuitous visual effects unrelated to the perception model.
