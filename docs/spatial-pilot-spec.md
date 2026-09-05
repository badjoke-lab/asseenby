# AsSeenBy — Spatial Pilot Spec

## Status
Experimental track. Additive to the existing v0.1 image comparison experience.

## Purpose
Test whether an interactive 3D environment can explain selected visual differences more clearly than a transformed still image.

The pilot is not a redesign of AsSeenBy and does not replace `Compare image`.

## Important terminology
The word **approximation** is a claim boundary, not a license to use a weak visual filter.

The spatial renderer must use scene, camera, depth, luminance, and view direction where those variables matter. It must not simply apply the existing 2D output as a texture or copy a static image filter over a 3D canvas.

AsSeenBy still does not claim that the output is an exact reconstruction of any particular person's lived perception. Exact patient-level reproduction would require individual measurements and validated models that are outside this pilot.

## Product shape
The workspace exposes two experiences:

- **Compare image** — the current static-image upload / sample comparison workflow.
- **Explore 3D** — an experimental interactive spatial comparison built with Three.js.

The 3D experience must remain visually and conceptually part of AsSeenBy: research-oriented, restrained, evidence-linked, and explicit about what is modeled versus what is not.

## Why 3D exists
3D is justified only where spatial interaction materially improves understanding.

The first pilot focuses on:

1. **Peripheral field loss / Tunnel Vision** — the user can look around the same environment and experience how losing peripheral information changes awareness of objects outside the center.
2. **Cataract-like glare / haze** — bright scene lights affect the result dynamically so glare, light spread, haze, blur, and contrast loss change as the user turns toward or away from them.

A mode that is only a global color matrix or a static full-screen filter is not, by itself, a reason to add a 3D implementation.

## Initial scene
Build exactly one purpose-designed night street / street-corner scene.

Required visual targets:
- traffic signal or strong red/green signal targets;
- road sign or text-like sign target;
- pedestrian silhouette;
- vehicle or vehicle-like geometry;
- streetlight;
- bright headlight-like sources;
- crosswalk / high-contrast ground markings;
- storefront or illuminated sign;
- mid-distance and far-distance building forms;
- at least one darker region with lower contrast.

The scene is a controlled comparison environment, not a realistic city recreation and not a game level.

## Initial spatial modes

### Normal
Baseline renderer with no perception simulation.

### Tunnel Vision
A spatial simulation of peripheral field loss.

Requirements:
- central region remains most visible;
- peripheral scene information is progressively obscured or degraded;
- the field-loss mask stays view-relative while the user looks around;
- switching to/from Normal does not move the camera;
- the implementation must work on the live rendered scene, not on a pre-rendered still.

The generic mode is not a patient-specific visual-field reconstruction unless future work adds measured field data.

### Cataract-like
A physically informed scene-dependent simulation combining the product's current cataract framing: haze, lower contrast, yellowing/warming, blur, and light spread.

Requirements:
- global contrast is reduced;
- moderate optical softness / blur is present;
- bright scene sources produce stronger glare / spread than dark regions;
- the effect changes when the camera turns toward or away from bright sources;
- the response must use rendered luminance or bright-pass information rather than a fixed decorative glow;
- switching to/from Normal does not move the camera.

The generic mode is not a patient-specific cataract optical model.

## Camera and interaction
Initial pilot interaction:
- drag / pointer movement to look around;
- touch drag on mobile;
- restrained zoom or field-of-view adjustment where practical;
- no free walking, collision system, scoring, character controller, or game mechanics.

Mode comparison rule:
- keep camera position and view direction unchanged when switching modes;
- do not change object placement, lighting, time, or scene state between Normal and simulated modes;
- only the perception renderer changes.

This isolates the effect being compared.

## Relationship to the existing 2D engine
The existing `src/transformEngine.ts` remains the image renderer for `Compare image`.

The spatial pilot must be implemented as a separate renderer/component. It may share mode metadata and evidence, but it should not replace the 2D canvas engine.

Target architecture:

```text
mode / evidence metadata
        |
        +-- image renderer -> current Canvas 2D transform engine
        |
        +-- spatial renderer -> Three.js scene + scene-aware post-processing
```

## Evidence and claims
Existing evidence and limitation concepts remain in force.

For spatial modes, documentation and UI must distinguish:
- evidence for the underlying visual phenomenon;
- confidence in the current spatial implementation;
- whether the model is generic or based on individual measurements.

A visually impressive implementation must not be presented as more scientifically exact than its evidence supports.

## Deferred spatial modes
Do not add these before the pilot acceptance gate:
- Central Loss;
- Night / Low Light;
- Dog-like;
- Cat-like;
- other human modes;
- Bird-like;
- Bee-like.

### Bee-like special rule
Bee-like UV work cannot be represented honestly from ordinary RGB scene color alone.

A future UV-aware scene would need additional scene/material data such as UV-reflectance information and a documented false-color mapping. Do not fake UV perception with a purple/blue filter.

## Performance and fallback
The pilot must remain usable on desktop and mobile browsers supported by the current site.

Requirements:
- no server-side rendering dependency for the 3D scene;
- no account or storage requirement;
- keep the initial scene lightweight;
- if WebGL / Three.js initialization fails, preserve access to the existing image comparison experience and show a concise failure notice rather than breaking the page.

## Acceptance gate
The pilot is successful only if all of the following are true:

1. Existing `Compare image` behavior still works.
2. `Explore 3D` loads one night-street test scene.
3. Normal, Tunnel Vision, and Cataract-like can be switched without camera reset.
4. Tunnel Vision is view-relative and clearly changes spatial awareness.
5. Cataract-like glare responds to actual scene brightness / viewing direction instead of behaving as a static overlay.
6. Evidence / limitation text is available for the active spatial mode.
7. Desktop and mobile interaction are usable.
8. `npm run build` passes.
9. The result is clearly more informative for these two modes than showing another transformed still image.

If criterion 9 is not met, do not expand the 3D track merely because the renderer works.
