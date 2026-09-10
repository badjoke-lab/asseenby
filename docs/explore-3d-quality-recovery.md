# AsSeenBy — Explore 3D Quality Recovery

## Status and authority
Status: **ACTIVE / REFERENCE-DRIVEN / CONTINUOUSLY DEPLOYED / BLOCKING ONLY QUALITY CLOSEOUT AND E5+ SEQUENCING**

This document records the quality recovery required after the deployed E2–E4 Night Intersection implementation was reviewed against the intended Explore 3D product bar.

The E2–E4 deployments remain historical implementation/production-verification facts. They are **not** sufficient evidence that the current Night Intersection scene satisfies the product-quality acceptance boundary.

### Deployment rule
Quality recovery status no longer blocks work-in-progress deployment. A coherent Explore 3D implementation increment should be merged to `main` and made inspectable on the public site even when the current render is visibly unfinished.

The quality gate controls two things only:
1. whether QR2/QR7 may be called visually complete;
2. whether the roadmap may advance to E5 Dog / later observer phases as the active sequence.

Do not use “QR2 fail” or “QR7 not yet closed” as a reason to keep current implementation work off production.

This document is read together with `docs/explore-3d-spec.md`, `docs/explore-3d-schedule.md`, `docs/blender-asset-pipeline.md`, `docs/roadmap.md`, and `AGENTS.md`.

## Reference-driven correction
The earlier rebuild still allowed too much invented generic-city styling. That process is replaced with a concrete photographic/reference-data loop.

`Night Intersection` uses **Hansaplatz, Hamburg-St. Georg, Germany** as the canonical current reconstruction location. The previous Berlin/Hansaviertel interpretation was a source-identification error and must not be reintroduced.

Primary evidence and geometry boundary:
- `public/assets/panoramas/hansaplatz.jpg` — Poly Haven `hansaplatz` 360 HDRI tonemapped JPG, Greg Zaal, CC0-1.0; photographic reference/environment only;
- fixed perspective reference plates generated under `assets-src/blender/night-intersection/reference/hansaplatz/`;
- Hamburg LGV **3D-Gebäudemodell LoD2-DE Hamburg 2026** — canonical macro building geometry for the Hansaplatz nearfield;
- `.github/HANSAPLATZ_SOURCE_TRUTH` — fail-closed city, coordinate, geometry, LoD3-gap and panorama-use contract.

The official Hamburg LoD3 Area1 archives have a verified Hansaplatz nearfield coverage gap. Distant LoD3 geometry must not be substituted into the gap. Close-range quality therefore comes from **Blender-authored detail aligned to the official Hamburg LoD2 macro shell**, not from fabricated LoD3 or raw panorama wall projection.

Current visible cues that must be represented rather than invented away include:
- the real Hamburg perimeter building massing and roof forms from official LoD2;
- Hansabrunnen and the plaza around it;
- the documented ring of mature lindens around the fountain, while keeping non-surveyed individual placement clearly labeled as reconstruction;
- real facade depth: windows, doors, storefront recesses, frames, sills, cornices, roof edges, signs and canopies where supported by photographic/reference evidence;
- credible pavement, street furniture and vegetation at walking distance;
- a coherent Day baseline plus a same-geometry Night environment for low-light/glare comparison.

The production loop is:

```text
real Hamburg reference + official macro geometry
  -> reference plates / source notes
  -> authored assets + Blender assembly
  -> GLB
  -> Three.js production runtime
  -> browser screenshot / real-site inspection
  -> compare against reference
  -> fix the visible mismatch
  -> publish next increment
```

The target is not merely “more objects”. The render must converge toward the Hamburg reference composition, architectural language, material response, lighting and density.

## Why the gate was reopened
The original Night Intersection implementation was dominated by programmatically assembled primitive geometry and generated Canvas textures. That was useful for proving Three.js depth, parallax, movement and Vision integration, but it did not meet the intended presentation bar.

The failure is not a Three.js capability limitation. The scene architecture and authoring strategy changed accordingly.

A renderer/shader/browser test can pass while the scene still looks poor. Visual/spatial acceptance therefore requires both technical behavior and rendered scene review.

## Product target
Explore 3D must feel like a real authored environment that users can enter and move through, not a geometry demo.

The target architecture is:

```text
Reference photography / official geometry evidence
  -> Blender authoring / assembly
     -> glTF/GLB export
        -> Scene manifest
           -> streamed/chunked world
              -> authored high-quality assets
              -> PBR materials/textures
              -> environment + practical lighting
              -> visual LOD / culling
              -> separate collision/navigation representation
              -> Observer runtime
              -> Vision runtime
```

The existing Scene / Observer / Vision separation remains correct and must be preserved.

For new primary-visible world content, Blender is the canonical DCC authoring/assembly layer. Three.js remains the browser runtime. A third-party GLB that already meets the runtime contract may be consumed directly when no Blender edit is required, but it still needs the same provenance, chunk, LOD and collision discipline.

## Visible-asset rule
For final-quality Night Intersection presentation:
- primary buildings/facades must not be accepted as plain BoxGeometry shells with repeated generated windows;
- primary vehicles must use authored vehicle assets or equivalently detailed modeled meshes;
- primary street furniture, vegetation, signs, storefront elements and other close-range objects must use authored/detail-preserving assets where the user can approach them;
- materials should use physically based inputs where available, including base color, normal, roughness and metallic data as appropriate;
- emissive maps/materials may be used for signs, windows and practical light sources;
- procedural geometry remains allowed for invisible collision meshes, navigation/debug helpers, simple distant LODs, road markings, repeated low-salience elements and other cases where it does not become the visible quality ceiling.

The acceptance question is visual: if the scene still reads as cheap low-poly/debug work at normal user viewpoints, it fails the quality label regardless of object count. It may nevertheless remain deployed while the next correction is being built.

Do not add new primary-visible world detail to the old procedural `nightIntersectionScene.ts` merely to improve screenshots. That implementation is a temporary technical fallback/reference while the Blender-authored path replaces its visible responsibilities.

## Asset pipeline
The canonical authoring/export contract is `docs/blender-asset-pipeline.md`.

Required capabilities:
- Blender-authored/assembled source path for new primary-visible world content;
- glTF/GLB loading;
- PBR material preservation;
- texture compression/transcoding where practical;
- lazy loading by scene/chunk;
- shared/reused assets rather than duplicating identical geometry;
- authored LOD or generated lower-detail representations where useful;
- disposal/unload when chunks leave the active set;
- an asset/license manifest recording source, creator, license, asset version and local path for every third-party visual asset.

CC0 assets are preferred. CC-BY assets may be used only when attribution is recorded and surfaced as required by the license. Do not import assets with unclear redistribution rights.

Source/runtime layout:

```text
assets-src/blender/night-intersection/
assets-src/blender/night-intersection/reference/hansaplatz/
public/assets/3d/night-intersection/
scripts/reference/extract_hansaplatz_reference_views.py
scripts/blender/export_night_intersection.py
```

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

A smaller dense authored core may land before the full envelope is populated. The first authored rebuild target remains central `C0`.

## Collision and navigation
Do not use the visual mesh as the only collision contract.

Use a separate lightweight representation appropriate to the observer:
- simplified collision meshes / bounds for buildings, vehicles and major obstacles;
- acceleration structure/BVH where it materially improves collision/raycast cost;
- ground navigation for Human/Dog;
- authored climb/perch transitions for Cat;
- volumetric bounds plus building/obstacle collision for Bird.

Collision must support a larger streamed scene and must not remain a fixed list of hand-entered rectangles tied to one prototype layout.

## Indoor / outdoor continuity
The architecture must permit authored interiors connected to the exterior scene.

Initial Night Intersection does not need every building to be enterable. At least one useful interior transition should eventually prove:
- exterior -> entrance -> interior -> exterior;
- consistent observer/camera state;
- collision/navigation changes by zone;
- Vision independence from the transition.

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
- Cat observer does not imply Cat-specific Vision.

### Bird
- concrete species preset;
- free-space flight;
- ascend/descend;
- variable altitude;
- building/major-obstacle collision;
- authored landing/perch targets;
- Bird Vision remains a separate evidence gate.

## Lighting and rendering target
The rebuilt scene uses **Day as the standard geometry/material comparison baseline** and preserves **Night as a same-geometry low-light environment**. Time of day remains independent from Vision.

Day should expose weak geometry, flat materials, bad scale and missing facade detail instead of hiding them in darkness. Night should add a coherent physically plausible hierarchy of:
- environment/sky contribution;
- streetlights;
- storefront/practical lights;
- vehicle lights where present;
- emissive signs/windows;
- deliberately dark regions;
- shadows or baked/approximate occlusion where performance permits;
- reflections/environment response where they materially improve surfaces.

Post-processing and darkness must not be used to hide weak geometry/material work.

## Performance strategy
Use as appropriate:
- frustum culling;
- InstancedMesh or mesh-data reuse for repeated objects;
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
Status: **PASS / merged / production path proven**

Proven:
- scene asset manifest;
- glTF/GLB loader path;
- asset lifecycle/disposal path;
- chunk interfaces/load states;
- license/provenance manifest;
- streamed Night Intersection world envelope/chunk runtime scaffold;
- canonical Blender authoring/export path;
- a real authored PBR asset in C0;
- browser-verified load -> unload -> reload without duplicate authored roots.

### QR2 — Rebuild the visible Night Intersection core
Status: **ACTIVE / HAMBURG REFERENCE-DRIVEN / PRODUCTION ITERATION**

Current work:
- canonical reconstruction location is Hansaplatz, Hamburg-St. Georg, not Berlin;
- official Hamburg LGV LoD2-DE 2026 remains the macro nearfield geometry source;
- the checked-in Poly Haven panorama is reference/environment evidence and is not projected raw onto permanent facade geometry;
- repeatable 82° perspective plates at six relative yaw headings are retained for visual comparison;
- close-facade structural depth currently adds windows/storefront/frame/sill/cornice cues, but it is explicitly a scaffold and **facade-by-facade photo registration remains open**;
- v10 Hansabrunnen/plaza work restored the central landmark composition but still contains proxy-level landmark geometry;
- v12 nearfield art-pass branch `feat/hansaplatz-v12-nearfield-artpass-20260911` replaces the primitive cylinder/ico-sphere linden-ring vegetation with linked CC0 PBR broadleaf mesh instances while explicitly making no species or surveyed-position claim;
- the v12 vegetation change does **not** close QR2; facade registration, landmark refinement, street-detail/material work and rendered desktop/mobile acceptance remain required.

Immediate QR2 art-pass order after the v12 vegetation replacement:
1. photo-register the closest plaza-facing facades one facade at a time instead of generating generic bays from bounding boxes;
2. replace remaining close-range landmark/street primitives that visibly read as proxies;
3. improve pavement/material variation and contact/shadow response under the Day baseline;
4. run rendered desktop/mobile comparison against the six fixed reference plates and keep QR2 open until the result no longer reads as placeholder work.

Acceptance for **quality closeout**:
- representative ground-level screenshots no longer read as placeholder/debug/cheap low-poly work;
- architecture and composition materially resemble the real Hamburg reference;
- near-field storefront/vehicle/street-furniture/vegetation detail survives normal walking distance;
- Normal mode is visually credible before any Vision effect;
- Human movement still works.

A failed rendered review keeps QR2 open, but the current implementation remains eligible for production deployment.

### QR3 — Chunking / LOD / larger district envelope
Status: **queued**

Acceptance:
- multiple chunks load/unload based on observer position;
- runtime can address toward 500 m × 500 m without all high-detail assets resident;
- parallax/lighting/collision remain coherent across boundaries.

### QR4 — Collision/navigation rebuild
Status: **queued**

Acceptance:
- Human cannot cross primary buildings/vehicles/major obstacles;
- collision stays stable across chunk boundaries;
- collision representation is separate from final visual geometry.

### QR5 — Vertical and perch contract
Status: **queued**

Acceptance:
- useful rooftops/ledges/wires/branches/poles exist as real spatial targets;
- metadata can support Cat climb/perch and Bird landing without rewriting the scene.

### QR6 — Interior continuity proof
Status: **queued**

Acceptance:
- exterior/interior transition is reachable through normal movement;
- collision/navigation zone changes correctly;
- scene/observer/vision state remains coherent.

### QR7 — Product-quality closeout
Status: **queued**

Run rendered desktop/mobile review plus browser regression and production verification.

Only after QR7 passes may E5+ resume as the active roadmap sequence. Intermediate QR work remains continuously deployable.

## Quality closeout gate
Do **not** mark QR7 complete based on:
- object count;
- shader metrics alone;
- production smoke alone;
- source-code inspection alone;
- the presence of glTF files alone.

QR7 requires actual rendered review at representative user viewpoints and comparison against the real reference.

Fail the quality label if representative close-range views still look like a primitive prototype/debug environment. Continue publishing corrections while fixing it.

## What remains valid from E1–E4
Keep and reuse where technically sound:
- Scene / Observer / Vision separation;
- 360° Photo Reference role;
- Human movement/reset semantics;
- Vision state-preservation invariants;
- accepted Human Vision evidence/limitation boundaries;
- production smoke and browser-regression infrastructure.

The recovery is a scene/world quality and scalability correction, not a reason to discard correct evidence work or the 2D Compare image product.
