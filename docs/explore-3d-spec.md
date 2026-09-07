# AsSeenBy — Explore 3D Specification

## Status and authority
This is the current product specification for post-pilot Three.js work.

`docs/spatial-pilot-spec.md` remains the historical pilot/evidence record. When that older pilot document conflicts with this file on current product shape, camera movement, scene architecture, observer behavior, or execution direction, **this specification controls**.

`Compare image` remains a separate browser-side 2D experience. `Explore 3D` is additive and must not replace it.

## Product definition
Explore 3D is not a 360° panorama viewer with filters. Its purpose is to let a user enter the same modeled environment as different observers and compare how **viewpoint, body scale, movement, reachable space, distance, depth, occlusion, lighting, and the selected visual model** change what information is available.

Three.js is justified only when the experience uses spatial variables that a flat image cannot provide. A panorama may remain as a photographic reference scene, but it is not the main Explore 3D architecture.

## Core architecture: Scene / Observer / Vision
The public 3D experience has three independent layers.

### Scene
The environment being explored. It owns geometry, materials, lights, collision surfaces, navigation bounds, observer spawn points, climb/perch targets, and guided comparison targets.

### Observer
The body/viewpoint and movement model. It owns camera height, movement style, movement speed, reachable space, collision envelope, altitude limits, and other physical-view constraints.

### Vision
The perception renderer. It changes visual processing while preserving the current Scene and Observer state unless a mode explicitly requires a documented observer-specific parameter.

Observer and Vision must remain separable. For example, a user must be able to use a Dog-height observer with Normal RGB before enabling the Dog-like visual proxy. This allows the user to distinguish viewpoint/body effects from visual-model effects.

## Comparison invariants
When only Vision changes:
- preserve scene;
- preserve observer;
- preserve camera position;
- preserve camera direction;
- preserve FOV;
- preserve lighting/time/object state;
- change only the perception renderer.

When Observer changes, observer-specific camera height, movement model, reachable space, collision envelope, spawn/reset state, and approved FOV rules may change.

## Observer set
Initial architecture must support at least:
- Human;
- Dog;
- Cat;
- Bird, implemented through species-specific observer presets rather than one biologically generic Bird vision model.

Observer availability does **not** imply that a species-specific visual model is scientifically accepted.

## Human observer
### Viewpoint
Use a generic standing-adult baseline around 1.6 m for the first implementation. This is a product reference viewpoint, not a claim about every human.

Future observer-height presets may include child or seated/wheelchair viewpoints if separately specified.

### Movement
Use bounded ground movement inside the active scene.

Desktop baseline:
- pointer/mouse drag: look;
- W/S: forward/back;
- A/D: strafe;
- Shift: moderately faster movement;
- restrained wheel/FOV control if validated;
- R / Reset: return to canonical observer start.

Mobile baseline:
- touch look;
- compact movement control/virtual stick;
- restrained pinch/FOV if validated;
- Reset control.

No combat, scoring, inventory, jumping game loop, quests, or unrelated game mechanics.

## Dog observer
### Viewpoint
Use a low ground viewpoint. The initial generic medium-dog reference should be around 0.5–0.6 m, with future Small / Medium / Large presets allowed because breed/body-size variation is material.

### Movement
Ground movement with a lower collision/view envelope than Human. The low viewpoint must materially change occlusion by cars, benches, curbs, plants, street furniture, people, and indoor furniture.

### Vision
Dog-like remains a conservative human-display proxy, not literal canine perception. Current defensible components include:
- visible-range dichromatic comparison;
- compressed red/green discrimination;
- comparatively available blue/yellow-like distinctions;
- reduced fine-detail availability.

In true 3D scenes, detail loss should increasingly use distance/angular size rather than a uniform full-screen blur alone.

Do not claim exact canine cone catches, breed-universal FOV, motion processing, tapetal/rod low-light reconstruction, or literal canine qualia from ordinary RGB.

## Cat observer
### Viewpoint
Use a lower ground viewpoint, initially around 0.3 m.

### Movement
Cat movement is not limited to flat ground. The scene may expose explicit climbable/perchable targets such as benches, low walls, steps, shelves, ledges, or similar surfaces.

The first implementation may use authored `climbable`/`perchable` transitions rather than full procedural climbing physics.

### Vision boundary
The previously rejected Cat-like RGB visual filter is **not automatically restored** by adding a Cat observer. Camera height/movement and Cat-specific vision are separate concerns.

A future Cat visual model requires a documented feline observer model and evidence gate. Until then, Cat may use Normal vision and any cross-species-safe vision modes that are explicitly approved.

## Bird observers
### Species rule
Do not implement one generic biological `Bird-like` vision shader. Avian spectral systems, acuity, retinal specialization, FOV, ecology, and behavior vary too much, and ordinary RGB cannot reconstruct UV/tetrachromatic information.

Bird movement/viewpoint can still be implemented as an Observer layer because flight, altitude, distance, and occlusion are geometric properties independent of unsupported spectral claims.

Initial bird work must select a concrete species preset. A city-compatible species such as Pigeon is a practical first candidate, but species selection itself is an implementation/evidence decision and must be recorded before release.

### Movement
Bird observers use the vertical dimension of the scene.

Desktop baseline:
- pointer/mouse: look;
- W: forward flight;
- S: slow/backward assist as appropriate;
- A/D: turn or lateral control;
- Space: ascend;
- Ctrl/C: descend;
- Shift: faster flight;
- R: reset to canonical flight start;
- Land/Perch: use an authored valid landing/perch target.

Mobile baseline:
- horizontal movement/flight control;
- touch look;
- ascend/descend controls;
- Perch control.

Bird movement must support actual free-space flight inside scene altitude/navigation bounds. A Bird observer must not be forced to walk on the ground like Human/Dog.

### Vertical scene requirements
A street scene intended for Bird observers must include meaningful vertical structure, for example:
- ground level;
- streetlights;
- wires/poles;
- trees/branches;
- signs/ledges;
- balconies;
- rooftops;
- open air volume.

Initial city scenes should normally provide roughly 30–50 m of useful flight altitude, with up to around 50–80 m where scene composition supports it.

### Bird vision boundary
Observer flight does not validate avian color vision. A species-specific Bird visual model requires a separate evidence/model gate and, for spectral/UV claims, additional source data such as spectral or UV-reflectance channels.

## Bee and other spectral observers
Bee-like remains blocked from ordinary RGB for visual-model purposes. Do not fake UV with a purple/blue filter.

A future UV/spectral observer requires:
- appropriate scene/material spectral or UV data;
- documented receptor/model inputs;
- a documented human-display false-color translation;
- explicit limitations.

## Scene portfolio
Explore 3D should use multiple dense scenes rather than one huge sparse world.

### Scene 1 — Night Intersection
First full 3D production scene.

Target useful volume: approximately 150 m × 150 m × 50–60 m, expandable toward 200 m × 200 m and 80 m height if performance remains acceptable.

Required content should include a believable mix of:
- buildings and facades;
- windows, entrances, storefronts and signs;
- road, curb, sidewalk and crossing details;
- several vehicles where useful;
- pedestrians;
- traffic signals and streetlights;
- benches, bins, vending/utility objects, poles, planters or equivalent street furniture;
- vegetation;
- dark alleys and bright storefront areas;
- rooftops, wires, branches, ledges or other Bird perch/height structure;
- near, mid and far targets.

This scene should support Human, Dog, Cat and Bird observer behavior.

### Later scenes
Planned scene families:
- Daytime Park — approximately 200 m × 200 m with useful vertical tree/flight structure;
- Store / Supermarket — approximately 40 m × 60 m, dense signage/shelf/detail comparisons;
- Home / Apartment — approximately 15 m × 25 m, strong Human/Dog/Cat viewpoint comparison;
- Station / Platform — approximately 100 m × 300 m, signage, crowds and long-distance targets;
- 360° Photo Reference — photographic reference mode retained as a separate scene, not the Explore 3D core.

## 360° photographic reference
The existing Hansaplatz panorama remains valuable for:
- real photographic density;
- same-view post-processing comparison;
- regression/reference work;
- comparison with synthetic/geometry-based scenes.

But it is explicitly a **reference scene**. It must not define the capability ceiling of Explore 3D.

Features requiring translation, parallax, object distance, geometry occlusion, physical lights, altitude, collision, climbing or flight must use a real 3D scene.

## Bounded movement, not a game
The old pilot restriction against walking is superseded.

Current target: **bounded free movement** within each authored scene, plus guided viewpoints/targets.

This means:
- movement is allowed where it improves the perception comparison;
- collision/navigation bounds prevent leaving the useful scene;
- preset comparison viewpoints may coexist with free movement;
- no need for a game loop, combat, scoring, inventory, character progression, or unrestricted open-world simulation.

## Guided comparison targets
Each scene should expose useful comparison targets so users do not need to discover every demonstration manually.

Examples for Night Intersection:
- crosswalk;
- traffic signal;
- pedestrian;
- bus stop/sign;
- bright storefront;
- dark alley;
- distant sign;
- rooftop/perch.

A guided target may move/reset the observer to an authored comparison viewpoint when the user requests it, but must not silently change Vision.

## Visual models in 3D
### Tunnel Vision
Viewer-relative peripheral field loss. World targets move into/out of the affected region as the user looks or moves.

### Central Loss
Viewer-relative central disruption. Centering a target can make that target harder to inspect; looking away moves a different world target into the affected center.

### Cataract-like
Move toward scene-aware behavior using actual 3D lighting and bright sources. Glare/haze should respond to the current view and, where implemented, geometry occlusion, source intensity and distance rather than merely detecting bright pixels in a panorama.

### Night / Low Light
Use scene lighting, shadow, material response, current-view brightness and distance where available. Continue to avoid claims of calibrated scotopic/mesopic reconstruction unless the scene carries the required physical data.

### Species acuity/detail
Where supported, use camera geometry, projected/angular object size and distance to model fine-detail availability rather than only applying resolution-independent screen blur.

## Lighting
True 3D night scenes must use an authored lighting hierarchy, such as:
- ambient/sky contribution;
- streetlights;
- storefront/practical lights;
- vehicle lights;
- signs/emissive sources;
- deliberately dark regions;
- occlusion/shadow where performance allows.

Perception modes may use this scene information but must clearly separate physical scene lighting from physiological claims.

## Collision and navigation
Use the simplest collision/navigation model that preserves the comparison.

Human/Dog/Cat:
- do not pass through buildings, vehicles or major obstacles;
- stay inside authored navigation bounds.

Cat:
- explicit climb/perch targets are allowed.

Bird:
- enforce building collision, altitude bounds and valid perch/landing targets;
- ground collision is secondary to volumetric navigation.

Full rigid-body physics is not required unless a future interaction specifically needs it.

## Scene scale and performance
Three.js can support much larger spaces, but AsSeenBy should optimize for comparison density rather than map size.

Preferred initial public scene size: roughly 100–200 m per horizontal dimension, with enough vertical space for Bird observers.

A 500 m × 500 m scene may be possible with LOD, instancing and chunking. A 1 km-class world is technically possible but is not a current product goal.

Use as needed:
- InstancedMesh;
- texture atlases/compressed textures;
- LOD;
- frustum culling;
- repeated asset reuse;
- baked lighting where appropriate;
- controlled dynamic-light count;
- lazy scene loading;
- scene chunking.

The renderer remains browser-side and should preserve the free/static-hosting operating model.

## UI structure
Explore 3D should expose the architecture directly.

Baseline control order:
1. Scene selector;
2. Observer selector;
3. species/body-size preset where applicable;
4. Vision selector;
5. scene viewport;
6. concise movement help / reset;
7. Evidence / Model / limitation information.

Example:

```text
Explore 3D
Scene    [Night Intersection]
Observer [Human] [Dog] [Cat] [Bird]
Vision   [Normal] [Tunnel] [Central] [Night] [Cataract]

[ Three.js scene ]

Move · Look · Reset
```

Controls must remain usable on desktop and mobile without becoming a game HUD. Preserve AsSeenBy's restrained editorial/research visual language.

## Reset semantics
Each Scene × Observer combination owns a canonical start state.

Reset restores:
- observer position;
- camera direction;
- FOV;
- movement velocity/state;
- altitude where relevant.

Preferred behavior: preserve the selected Vision so the user can reset position without losing the comparison mode.

## Evidence and claim boundary
For every observer and visual model distinguish:
- physical/geometric observer assumptions;
- evidence for the visual phenomenon;
- confidence in the current renderer/model;
- source-data limitations.

A more sophisticated 3D scene does not make an unsupported species visual claim acceptable.

In particular:
- Dog Observer height/movement is distinct from Dog-like Vision;
- Cat Observer does not imply accepted Cat Vision;
- Bird flight does not imply accepted Bird color Vision;
- UV/tetrachromatic claims remain blocked without appropriate data/model support.

## Engineering architecture
Keep `Compare image` and Explore 3D renderers separate.

```text
shared metadata / evidence
        |
        +-- Compare image -> Canvas 2D transform engine
        |
        +-- Explore 3D
              +-- Scene layer
              +-- Observer/controller layer
              +-- Vision/post-processing layer
```

The current panorama renderer should be refactored into one Scene implementation rather than remaining the entire spatial architecture.

## Acceptance boundary
Explore 3D architecture is not considered implemented merely because Scene/Observer/Vision selectors exist.

Acceptance requires actual rendered behavior showing:
- a geometry-based scene with depth/parallax;
- bounded camera translation for ground observers;
- observer-specific viewpoint height;
- at least one observer-specific reachable-space difference;
- Bird flight in three dimensions once the Bird phase begins;
- Vision switching without unintended scene/camera reset;
- desktop and mobile usability;
- evidence/limitations matching the actual implementation;
- public production verification.
