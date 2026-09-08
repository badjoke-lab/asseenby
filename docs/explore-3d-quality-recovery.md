# AsSeenBy — Explore 3D Quality Recovery

## Status and authority
Status: **ACTIVE / BLOCKING E5+**

This document records the quality recovery required after the deployed E2–E4 Night Intersection implementation was reviewed against the intended Explore 3D product bar.

The E2–E4 deployments remain historical implementation/production-verification facts. They are **not** sufficient evidence that the current Night Intersection scene satisfies the product-quality acceptance boundary.

Until this recovery closes, do not advance the public product roadmap to Dog, Cat or Bird merely by adding observer controls on top of the current procedural scene.

This document is read together with `docs/explore-3d-spec.md`, `docs/explore-3d-schedule.md`, `docs/roadmap.md`, and `AGENTS.md`. Where older E2–E4 completion wording implies that the current scene presentation is accepted as final-quality, this recovery document supersedes that implication.

## Why the gate is reopened
The current Night Intersection implementation is dominated by programmatically assembled primitive geometry and generated Canvas textures. That was useful for proving Three.js depth, parallax, movement and Vision integration, but it does not meet the intended final presentation bar.

The failure is not a Three.js capability limitation. The scene architecture and asset strategy must change.

A renderer/shader/browser test can pass while the scene still fails the product. Visual/spatial acceptance therefore requires both technical behavior and rendered scene quality.

## Product target
Explore 3D must feel like a real authored environment that users can enter and move through, not a geometry demo.

The target architecture is:

```text
Scene manifest
  -> streamed/chunked world
     -> authored high-quality glTF/GLB assets
     -> PBR materials/textures
     -> environment + practical lighting
     -> visual LOD / culling
     -> separate collision/navigation representation
     -> Observer runtime
     -> Vision runtime
```

The existing Scene / Observer / Vision separation remains correct and must be preserved.

## Visible-asset rule
For final-quality Night Intersection presentation:
- primary buildings/facades must not be accepted as plain BoxGeometry shells with repeated generated windows;
- primary vehicles must use authored vehicle assets or equivalently detailed modeled meshes;
- primary street furniture, vegetation, signs, storefront elements and other close-range objects must use authored/detail-preserving assets where the user can approach them;
- materials should use physically based inputs where available, including base color, normal, roughness and metallic data as appropriate;
- emissive maps/materials may be used for signs, windows and practical light sources;
- procedural geometry remains allowed for invisible collision meshes, navigation/debug helpers, simple distant LODs, road markings, repeated low-salience elements and other cases where it does not make the final scene read as placeholder geometry.

The acceptance question is visual: if the scene still reads as cheap low-poly/debug work at normal user viewpoints, it fails regardless of object count.

## Asset pipeline
The asset runtime must support an asset-first workflow suitable for static hosting.

Required capabilities:
- glTF/GLB loading;
- PBR material preservation;
- texture compression/transcoding where practical;
- lazy loading by scene/chunk;
- shared/reused assets rather than duplicating identical geometry;
- authored LOD or generated lower-detail representations where useful;
- disposal/unload when chunks leave the active set;
- an asset/license manifest recording source, creator, license, asset version and local path for every third-party visual asset.

CC0 assets are preferred. CC-BY assets may be used only when attribution is recorded and surfaced as required by the license. Do not import assets with unclear redistribution rights.

## World scale and streaming
The old `150 m × 150 m` value is no longer a hard product ceiling.

Night Intersection should be designed as a chunked district rather than one permanently resident scene graph.

Target architecture:
- support a world envelope on the order of **500 m × 500 m** horizontally when content warrants it;
- retain useful vertical space for Bird observers, generally up to roughly **50–80 m** in the city scene;
- keep only nearby/high-value chunks at full detail;
- use lower LOD or unloaded state for distant chunks;
- do not require every chunk to be resident at once;
- avoid hard-coded navigation assumptions that only work inside the old 150 m box.

A smaller dense authored core may land before the full envelope is populated, but the runtime must no longer make 150 m the architectural limit.

## Chunk model
Night Intersection should move toward explicit chunks, for example:

```text
NW3 NW2 NW1 N0 N1 N2 N3
 W3  W2  W1 C0 E1 E2 E3
SW3 SW2 SW1 S0 S1 S2 S3
```

Exact naming/layout is implementation-defined. Each chunk should be able to own:
- visual asset references;
- light references;
- collision representation;
- navigation metadata;
- indoor portals/entries where present;
- climb/perch metadata;
- guided comparison targets;
- LOD/load priority.

## Collision and navigation
Do not use the visual mesh as the only collision contract.

Use a separate lightweight representation appropriate to the observer:
- simplified collision meshes / bounds for buildings, vehicles and major obstacles;
- acceleration structure/BVH where it materially improves collision/raycast cost;
- ground navigation for Human/Dog;
- authored climb/perch transitions for Cat;
- volumetric bounds plus building/obstacle collision for Bird.

Collision must support a larger streamed scene and must not be a fixed list of hand-entered rectangles tied to one intersection forever.

## Indoor / outdoor continuity
The architecture must permit authored interiors connected to the exterior scene.

Initial Night Intersection does not need every building to be enterable. At least one useful interior transition should eventually prove the contract:
- exterior street -> entrance -> interior space -> exit back to exterior;
- consistent observer/camera state;
- collision/navigation changes by zone;
- Vision remains independent from the transition.

Interior work must not be faked as a scene-reset if the public UI presents it as a continuous reachable space.

## Observer movement contract after recovery
### Human
- standing eye height around 1.6 m;
- mouse/pointer look;
- WASD ground movement;
- Shift faster movement;
- collision, stairs/ramps where authored;
- Reset.

### Dog
- size preset controls viewpoint/collision envelope;
- ground movement;
- materially different occlusion and reachable space from Human;
- Normal available independently from Dog-like Vision.

### Cat
- lower viewpoint;
- ground movement plus authored climb/perch targets;
- ledges/benches/low walls/interior furniture may be reachable where authored;
- Cat observer does not imply Cat-specific Vision.

### Bird
- concrete species preset;
- free-space flight;
- forward/lateral/turn controls as selected by implementation;
- ascend/descend;
- variable altitude;
- building/major-obstacle collision;
- authored landing/perch targets;
- Bird Vision remains a separate evidence gate.

## Lighting and rendering target
The rebuilt scene should use a coherent physically plausible night-light hierarchy:
- environment/sky contribution;
- streetlights;
- storefront/practical lights;
- vehicle lights where present;
- emissive signs/windows;
- deliberately dark regions;
- shadows or baked/approximate occlusion where performance permits;
- reflections/environment response where they materially improve surfaces.

Post-processing must not be used to hide weak geometry/material work.

## Performance strategy
The quality recovery is not permission to make the page unusable on mobile.

Use as appropriate:
- frustum culling;
- InstancedMesh for repeated objects;
- chunk streaming;
- LOD;
- compressed textures;
- shared materials/textures;
- controlled dynamic-light counts;
- baked lighting/lightmaps where suitable;
- quality tiers based on device/runtime capability;
- simplified collision meshes;
- deferred loading of non-visible interiors and distant chunks.

A lower mobile quality tier may reduce texture resolution, shadow quality, LOD distance or active lights. It must not revert the scene to the old placeholder visual language.

## Recovery execution order
### QR1 — Runtime and asset contract
Status: **next**

Implement:
- scene asset manifest;
- glTF/GLB loader path;
- asset lifecycle/disposal;
- chunk interfaces/load states;
- license/provenance manifest;
- preserve current Scene / Observer / Vision state contracts.

Acceptance:
- at least one real authored PBR asset loads through the production runtime;
- load/unload does not leak the scene into duplicate objects after switching scenes;
- build and existing Compare image regressions remain green.

### QR2 — Rebuild the visible Night Intersection core
Status: **queued**

Replace the close-range primitive/demo look with authored assets and higher-fidelity materials.

Acceptance:
- representative ground-level screenshots no longer read as placeholder/debug/cheap low-poly work;
- near-field building/storefront/vehicle/street-furniture detail survives normal walking distance;
- Normal mode is visually credible before any Vision effect;
- current Human movement still works.

### QR3 — Chunking / LOD / larger district envelope
Status: **queued**

Move the scene away from one fixed 150 m graph and prove streamed world expansion.

Acceptance:
- multiple chunks load/unload based on observer position;
- the runtime can address a district-scale envelope toward 500 m × 500 m without keeping all high-detail assets resident;
- parallax/lighting/collision remain coherent across chunk boundaries.

### QR4 — Collision/navigation rebuild
Status: **queued**

Replace the fixed obstacle-rectangle model with collision/navigation data that scales with authored assets and chunks.

Acceptance:
- Human cannot cross primary buildings/vehicles/major obstacles;
- collision stays stable across chunk boundaries;
- collision representation is separate from final visual geometry.

### QR5 — Vertical and perch contract
Status: **queued**

Add vertical structures and authored perch/climb metadata needed by Cat/Bird.

Acceptance:
- useful rooftops/ledges/wires/branches/poles exist as real reachable spatial targets;
- metadata can support Cat climb/perch and Bird landing without rewriting the scene.

### QR6 — Interior continuity proof
Status: **queued**

Add at least one authored enterable interior path.

Acceptance:
- exterior/interior transition is reachable through normal movement;
- collision/navigation zone changes correctly;
- scene/observer/vision state remains coherent.

### QR7 — Product-quality closeout
Status: **queued**

Run rendered desktop/mobile review plus browser regression and production verification.

Only after QR7 passes may E5+ resume as the active roadmap sequence.

## Blocking acceptance gate
Do **not** mark QR7 complete based on:
- object count;
- shader metrics alone;
- production smoke alone;
- source-code inspection alone;
- the presence of glTF files alone.

QR7 requires actual rendered review at representative user viewpoints.

Fail if any representative close-range view still looks like a primitive prototype/debug environment.

## What remains valid from E1–E4
Keep and reuse where technically sound:
- Scene / Observer / Vision separation;
- 360° Photo Reference role;
- Human movement/reset semantics;
- Vision state-preservation invariants;
- accepted Human Vision evidence/limitation boundaries;
- production smoke and browser-regression infrastructure.

The recovery is a scene/world quality and scalability correction, not a reason to discard correct evidence work or the 2D Compare image product.
