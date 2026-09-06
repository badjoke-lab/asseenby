# AsSeenBy — Spatial Pilot Spec

## Status
The initial Three.js pilot has passed its functional acceptance gate. This document now also governs ordered post-pilot spatial expansion and presentation quality.

The spatial experience remains additive to the existing v0.1 image comparison experience and does not replace `Compare image`.

## Important terminology
The word **approximation** is a claim boundary, not a license to use a weak visual filter.

The spatial renderer must use scene, camera, depth, luminance, view direction, and screen-relative field position where those variables matter. It must not simply apply the existing 2D output as a texture or copy a static image filter over a 3D canvas when the phenomenon being modeled is spatially dependent.

AsSeenBy does not claim that spatial output is an exact reconstruction of any particular person's lived perception. Exact patient-level reproduction would require individual measurements and validated models outside the current product.

## Product shape
The workspace exposes two experiences:
- **Compare image** — the current static-image upload / sample comparison workflow.
- **Explore 3D** — an interactive spatial comparison built with Three.js.

The 3D experience must remain visually and conceptually part of AsSeenBy: research-oriented, restrained, evidence-linked, and explicit about what is modeled versus what is not.

## Why 3D exists
3D is justified only where spatial interaction materially improves understanding.

Accepted functional examples:
1. **Tunnel Vision** — active scanning shows the consequence of losing peripheral information while the field-loss region remains tied to the viewer's field.
2. **Cataract-like** — actual bright scene sources produce stronger glare / spread when they enter the rendered view.

Current expansion target:
3. **Central Loss** — active scanning should show that disrupted straight-ahead detail remains tied to the viewer's central field. Looking directly at a target can make that target harder to inspect, while turning the view moves a different scene target into the affected center.

A mode that is only a global color matrix or static full-screen filter is not, by itself, a reason to add a 3D implementation.

## Controlled night-street scene
The same night-street environment remains the comparison scene, but the first primitive version is no longer considered presentation-quality.

The scene is still a controlled comparison environment, not a realistic city recreation and not a game level. However, controlled does **not** mean visually crude.

### Scene-quality requirements
The public-facing scene must read immediately as a believable street environment rather than placeholder geometry.

Required presentation layers:
- building masses with facade structure rather than bare black boxes;
- repeated windows, lit/unlit variation, entrances, storefront framing, signs, awnings, or similar architectural detail;
- road surface with credible material response and secondary markings/details;
- sidewalks with curbs and enough surface segmentation to read as constructed space;
- at least one vehicle with recognizable body, cabin/glass, wheels, bumpers/lights, and grounded proportions;
- pedestrian form with recognizable body segmentation rather than a capsule/box mannequin;
- traffic signal and streetlights with believable housings and support geometry;
- street furniture / utility detail such as bollards, bins, hydrants, planters, poles, utility cabinets, or equivalent elements;
- near, mid, and far layers with enough density that looking around continues to reveal useful visual information;
- a coherent night-light hierarchy: ambient sky/moon contribution, warm practical lights, headlights, shop lighting, and deliberately darker regions;
- scene composition that remains readable in Normal mode before any perception effect is applied.

Primitive Three.js geometry is allowed, but only if composed into convincing objects. A bare cuboid used as a building, car, or person is not acceptable by itself.

### Scene-quality rejection rule
If a rendered screenshot still looks like a debug environment, low-effort low-poly mockup, or sparse black-box corridor, the spatial track fails the presentation gate even if the perception shaders and browser tests pass.

## Accepted baseline spatial modes

### Normal
Baseline renderer with no perception simulation.

### Tunnel Vision
Live screen/view-relative peripheral field-loss simulation.

Boundary:
- generic field-loss profile;
- not an individual's measured perimetry result.

### Cataract-like
Live scene-dependent model combining softness, lower contrast, warming / veil, and high-luminance-gated local light spread.

Boundary:
- generic impairment model;
- not a patient-specific lens-scatter reconstruction.

## Post-pilot expansion — Central Loss

### Purpose
Demonstrate the practical consequence of degraded or missing straight-ahead detail in an interactive scene.

### Requirements
- central region is materially more degraded or obscured than surrounding vision;
- surrounding / peripheral scene information remains substantially available;
- the affected region remains centered in the viewer's field while the camera turns;
- the effect operates on the live rendered scene;
- switching Normal <-> Central Loss does not change camera position, direction, object placement, lighting, time, or scene state;
- direct-fixation targets such as a pedestrian, sign, signal, or headlight become harder to inspect when they fall in the central-loss region;
- turning the camera changes which world-space target falls under the central disruption because the disruption is view-relative;
- use a soft generic central scotoma-style profile, optionally combining localized blur / desaturation / partial obscuration;
- do not present the shape, size, opacity, or strength as an individual's measured field loss.

### Why this is spatial rather than another image filter
The value is not the existence of a central mask by itself. The value is the interaction between fixation and scene inspection:
- the user attempts to center a target;
- central detail becomes less available;
- the user scans elsewhere;
- the affected region remains in straight-ahead vision and a different target moves into it.

This behavior must be visible in rendered validation before the mode is accepted.

### Evidence / model rule
- reuse the existing Central Loss evidence set for the underlying phenomenon;
- assess the spatial renderer implementation separately from the image renderer;
- initial spatial Model assessment must remain conservative at **C** until rendered review is completed;
- state explicitly that the model is generic and not a measured scotoma / perimetry reconstruction.

## Camera and interaction
Spatial interaction remains:
- drag / pointer movement to look around;
- touch drag on mobile;
- keyboard look-around when the scene has focus;
- restrained zoom only if separately justified;
- no free walking, collision system, scoring, character controller, or game mechanics.

Mode comparison rule:
- keep camera position and view direction unchanged when switching modes;
- do not change object placement, lighting, time, or scene state between modes;
- only the perception renderer changes.

## Relationship to the existing 2D engine
The existing `src/transformEngine.ts` remains the image renderer for `Compare image`.

The spatial renderer remains separate. It may share mode metadata and evidence, but it must not replace the 2D canvas engine.

```text
mode / evidence metadata
        |
        +-- image renderer -> current Canvas 2D transform engine
        |
        +-- spatial renderer -> Three.js scene + live post-processing
```

## Evidence and claims
For every spatial mode, documentation and UI must distinguish:
- evidence for the underlying visual phenomenon;
- confidence in the current spatial implementation;
- whether the model is generic or based on individual measurements.

A visually sophisticated 3D result is not automatically more scientifically exact.

## Ordered expansion rule
After the accepted initial pilot, spatial modes are evaluated one at a time in this order:
1. Central Loss;
2. Night / Low Light;
3. Dog-like;
4. Cat-like;
5. Bird-like as a separate evaluation;
6. Bee-like only with additional UV-reflectance scene data.

Do not start the next mode until the active mode has passed both its rendered-effect acceptance gate and the scene-presentation quality gate, or has been explicitly rejected.

### Bee-like special rule
Bee-like UV work cannot be represented honestly from ordinary RGB scene color alone. A future UV-aware scene requires additional scene/material data such as UV-reflectance information and a documented false-color mapping. Do not fake UV perception with a purple / blue filter.

## Performance and fallback
The spatial experience must remain usable on desktop and mobile browsers supported by the current site.

Requirements:
- no server-side rendering dependency for the 3D scene;
- no account or storage requirement;
- keep scene and post-processing lightweight enough for the current deployment target;
- preserve the existing image comparison experience if WebGL / Three.js initialization fails;
- show a concise failure notice instead of breaking the page.

## Central Loss acceptance gate
Central Loss is successful only if all of the following are true:
1. Existing `Compare image` behavior still works.
2. Existing accepted spatial modes still work.
3. Central Loss can be selected without camera reset.
4. Straight-ahead detail is clearly less usable while surrounding scene information remains available.
5. The disrupted region remains view-relative during look-around.
6. Same-camera Normal / Central Loss comparisons demonstrate that only the perception renderer changed.
7. Evidence / limitation text is available for Central Loss.
8. Desktop and mobile interaction remain usable.
9. `npm run build` passes.
10. Rendered review shows that active scanning explains central field loss more clearly than another transformed still image.
11. Normal-mode rendered review passes the scene-quality requirements above and no longer reads as placeholder geometry or a cheap demo environment.

If criterion 10 or 11 is not met, do not merge the spatial Central Loss phase merely because the shader works.
