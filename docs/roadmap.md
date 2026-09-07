# AsSeenBy — Roadmap

## Current state
The repository contains:
- the Vite + React + TypeScript static-image comparison product;
- browser-side image transforms and evidence metadata;
- a production-verified Three.js 360° spatial reference implementation;
- accepted Human spatial perception modes on that reference scene;
- a production-verified image/release-polish track through R15;
- a production-verified Explore 3D E1 architecture split that separates Scene / Observer / Vision while retaining the 360° Photo Reference;
- a production-verified E2 `Night Intersection` real-geometry baseline with authored camera translation/parallax and a permanent production fingerprint;
- a production-verified E3 Human observer with bounded collision-aware ground movement on Night Intersection;
- a production-verified E4 Human spatial Vision integration on Night Intersection with Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like.

The historical 360° pilot is no longer the target architecture for the 3D product.

Current Explore 3D direction is defined by:
- `docs/explore-3d-spec.md`;
- `docs/explore-3d-schedule.md`.

The old `docs/spatial-pilot-spec.md` and `docs/spatial-pilot-schedule.md` remain historical records of the pilot and prior evidence decisions.

## Product shape
AsSeenBy keeps two complementary experiences.

### Compare image
Browser-side static-image comparison. This remains independent of the Three.js renderer.

### Explore 3D
A spatial comparison experience built around **Scene / Observer / Vision**.

Explore 3D is not defined as a 360° panorama viewer. Its purpose is to let users compare how the same environment changes when viewpoint height, movement, reachable space, distance, depth, occlusion, lighting and the selected visual model change.

## Immediate priority order
1. add Dog observer in E5, then refine Dog-like 3D detail behavior in E6;
2. add Cat observer movement/viewpoint without automatically restoring Cat-like Vision;
3. select a concrete first Bird species and implement real flight/perch behavior;
4. evaluate that Bird species' visual model separately from its movement/viewpoint;
5. expand to additional dense scenes after the first architecture is stable.

## Explore 3D architecture
### Scene
Owns geometry, materials, lights, navigation bounds, collision surfaces, spawn states, climb/perch targets and guided comparison targets.

### Observer
Owns viewpoint/body scale and movement.

Planned observer families:
- Human;
- Dog;
- Cat;
- species-specific Bird presets.

### Vision
Owns perception rendering and must remain independent from Observer wherever possible.

Changing Vision must preserve the exact Scene/Observer/camera state. Changing Observer may alter camera height, movement model, collision envelope, reachable space and altitude according to the current spec.

## Observer roadmap
### Human
Target baseline:
- generic standing-adult viewpoint around 1.6 m;
- bounded ground movement;
- pointer/touch look;
- desktop WASD-style movement;
- mobile movement control;
- Reset;
- no game mechanics.

### Dog
Target baseline:
- materially lower viewpoint, initially around 0.5–0.6 m for a medium-dog reference;
- ground movement and lower occlusion envelope;
- Normal view available independently of Dog-like Vision;
- Dog-like remains a conservative visible-range proxy.

Longer-term Dog-like 3D work should use distance/projected angular size for fine-detail loss where possible rather than only a uniform screen blur.

### Cat
Target baseline:
- lower viewpoint, initially around 0.3 m;
- ground movement;
- authored climb/perch transitions for selected low/high surfaces.

Cat Observer does **not** imply an accepted Cat-specific visual renderer. The old generic Cat-like RGB filter remains rejected unless a new documented feline observer model passes a separate evidence gate.

### Bird
Bird movement is a first-class 3D requirement, not ground walking.

Target behavior:
- concrete species preset rather than one generic biological Bird model;
- free-space flight inside scene bounds;
- ascend/descend;
- real altitude change;
- landing/perch targets;
- major-geometry collision;
- useful city flight volume roughly 30–50 m initially.

Bird flight/viewpoint can be implemented before Bird-specific Vision. Generic Bird-like spectral/color vision remains rejected from ordinary RGB. Species-specific Vision requires its own evidence/data/model review and may require UV/spectral scene data.

## Scene roadmap
### Night Intersection — first full 3D scene
Target useful volume: approximately 150 m × 150 m × 50–60 m.

The scene should contain enough real geometry and visual density to support Human, Dog, Cat and Bird observers:
- street/sidewalk/crosswalk;
- buildings/facades/storefronts/signs;
- vehicles and pedestrians;
- traffic signals/streetlights;
- street furniture;
- vegetation;
- dark and bright areas;
- rooftops/poles/wires/branches/ledges;
- near/mid/far targets.

The goal is explanatory density, not an open-world map.

### Later candidate scenes
- Daytime Park;
- Store / Supermarket;
- Home / Apartment;
- Station / Platform;
- 360° Photo Reference as a retained photographic comparison scene.

A strong 100–200 m scene is preferred over a sparse kilometre-scale environment.

## 360° photographic reference
The Hansaplatz panorama remains accepted and useful, but its role changes.

It remains:
- a real photographic density reference;
- a post-processing comparison scene;
- a regression/reference surface.

It does **not** satisfy features that require:
- camera translation;
- parallax;
- object distance;
- geometric occlusion;
- collision;
- climbing;
- flight;
- real 3D lights/altitude relationships.

Those require geometry-based scenes.

## Human spatial Vision roadmap
Accepted broad modes remain:
- Normal;
- Tunnel Vision;
- Central Loss;
- Night / Low Light;
- Cataract-like.

In geometry scenes, these should use real spatial information where that materially improves the model:
- viewer-relative field position for Tunnel/Central;
- real scene lighting/current-view context for Night / Low Light;
- real bright-source/occlusion/distance information for Cataract-like where feasible.

## Animal/species evidence boundary
### Dog-like
Accepted as a conservative human-display visible-range proxy. It does not claim exact canine cone catches, universal breed FOV, motion processing, tapetal/rod low-light reconstruction or literal canine qualia.

### Cat-like
The old generic visual filter remains rejected. Cat Observer movement/viewpoint is a separate product feature and may proceed without Cat-specific Vision.

### Bird-like
The old generic Bird-like visual concept remains rejected/blocked. Bird Observer flight may proceed because geometry/movement does not require unsupported spectral claims. Any Bird Vision work must target a concrete species and pass a separate model/data gate.

### Bee-like
Still blocked without UV-reflectance/spectral scene data and a documented observer/false-color model.

## Image track
The image track remains browser-side and separate.

Continue to maintain:
- build reliability;
- evidence accuracy;
- transform quality;
- responsive/release polish;
- production browser regression.

Do not let ongoing image polish delay the active Explore 3D observer/movement work, unless a production regression requires immediate repair.

## Engineering / operating constraints
- browser-side rendering;
- static/free-hosting-compatible operation;
- no account/storage requirement unless separately specified;
- lazy-load heavy 3D assets/scenes;
- use instancing, LOD, culling, compressed/reused assets and controlled lighting as needed;
- desktop and mobile must remain usable;
- preserve `Compare image` if WebGL/Three.js fails.

## Source of truth
For future implementation agents:
- repository docs, not chat memory, are authoritative;
- `AGENTS.md` defines the required reading discipline;
- `docs/explore-3d-spec.md` defines current 3D behavior;
- `docs/explore-3d-schedule.md` defines current 3D execution order;
- when a product decision changes, update those documents in the same implementation change before marking the work complete.
