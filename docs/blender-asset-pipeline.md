# AsSeenBy — Blender Asset / World Authoring Pipeline

## Status and authority
Status: **ACTIVE / REQUIRED FOR EXPLORE 3D QUALITY RECOVERY**

This document defines the canonical authoring pipeline for final-quality Explore 3D world content.

For primary visible world content, the durable production path is:

```text
Blender authoring / assembly
  -> glTF/GLB export
  -> repository asset/provenance manifest
  -> Night Intersection chunk manifest
  -> Three.js asset + chunk runtime
  -> Scene
  -> Observer
  -> Vision
```

Three.js remains the browser runtime. It is responsible for loading, streaming, LOD selection, culling, runtime lighting, movement/collision integration, Observer behavior, Vision rendering and UI state. It is **not** the final-quality world-authoring tool for close-range buildings, vehicles, storefronts, vegetation or street furniture.

The current procedural `nightIntersectionScene.ts` remains a temporary technical fallback/reference while the authored path is populated. Do not extend that procedural implementation with new primary-visible BoxGeometry/CanvasTexture content as a substitute for authored assets.

## Canonical authoring tool
Blender is the canonical DCC authoring/assembly tool for new primary-visible Explore 3D scene content.

This means:
- original Night Intersection world modules are modeled/assembled in Blender;
- third-party meshes are imported into Blender when they need scale correction, material cleanup, LOD preparation, scene placement, collision proxies or integration with the authored world;
- Blender-authored/assembled content is exported to glTF/GLB for the browser runtime;
- Three.js code should describe runtime behavior and placement contracts, not rebuild detailed close-range world art from primitives.

A third-party GLB that already meets the runtime contract may be consumed directly when no Blender edit is needed, but it still requires provenance/license registration and must fit the same chunk/LOD/collision rules.

## Repository layout
Use this layout as the target organization:

```text
assets-src/
  blender/
    night-intersection/
      README.md
      core/
      buildings/
      streets/
      interiors/
      props/
      vegetation/

public/
  assets/
    3d/
      night-intersection/
        c0/
        n0/
        s0/
        e0/
        w0/

scripts/
  blender/
    export_night_intersection.py
```

Binary `.blend` source files may be committed when reasonably sized and legally redistributable. Do not commit embedded third-party source material whose license does not permit redistribution. When source files are too large for normal Git history, preserve a reproducible source/provenance record and keep the optimized runtime GLB plus the exact authoring/export recipe; do not silently drop provenance.

## Units and coordinate contract
- Blender scene unit system: Metric.
- 1 Blender unit = 1 meter.
- Apply object scale before final export unless a documented exception exists.
- Keep a consistent world origin for each chunk.
- glTF/Three.js runtime coordinates use Y-up after export.
- Chunk placement in Three.js is authoritative for district-scale streaming; individual assets should not contain arbitrary world-scale offsets unless they are a chunk-level export.

## Night Intersection chunk contract
The current runtime world envelope is approximately `500 m × 500 m` with `64 m` chunks and up to roughly `80 m` useful vertical space.

The first authored target is the central chunk `C0`. Do not attempt to fill the entire 500 m district before C0 meets the close-range quality bar.

A Blender chunk scene should use collections or equivalent exported grouping for these roles when applicable:

```text
C0
├── VISUAL_LOD0
├── VISUAL_LOD1
├── VISUAL_LOD2
├── COLLISION
├── NAV
├── PERCH
├── CLIMB
├── PORTAL
├── SPAWN
└── LIGHT_ANCHOR
```

Not every chunk needs every role on day one, but the structure must not prevent later Dog/Cat/Bird/interior work.

### Role meanings
- `VISUAL_LOD0` — close-range primary visible geometry.
- `VISUAL_LOD1` — medium-distance reduced detail.
- `VISUAL_LOD2` — far-distance silhouette/low-detail representation where useful.
- `COLLISION` — simplified non-visible collision proxies.
- `NAV` — authored ground navigation surfaces/regions and related metadata.
- `PERCH` — Bird landing/perch targets and shared elevated targets where appropriate.
- `CLIMB` — authored Cat climb/perch transitions.
- `PORTAL` — exterior/interior continuity anchors and zone transitions.
- `SPAWN` — canonical observer/reset anchors.
- `LIGHT_ANCHOR` — authored placement anchors for runtime lights or exported practical-light metadata.

Collision/navigation metadata may ultimately be exported as dedicated GLB nodes, sidecar data or scene-manifest data. The visible mesh must not become the only collision contract.

## Naming
Use stable, machine-readable names. Prefer names such as:

```text
c0_building_corner_01_lod0
c0_storefront_01_lod0
c0_vehicle_sedan_01_lod0
c0_streetlamp_01_lod0
c0_collision_building_corner_01
c0_perch_wire_01
c0_portal_store_01
```

Do not rely on Blender default names such as `Cube.001` for production assets.

## Visible-quality target
Primary close-range content must survive normal walking distance and low Observer viewpoints.

C0 should ultimately contain a believable authored mix of:
- road, curb, sidewalk and crosswalk detail;
- detailed building/facade modules;
- modeled doors/windows/storefronts/signage;
- vehicles;
- traffic signals and streetlights;
- benches/bins/poles/utility objects or equivalent street furniture;
- vegetation;
- dark alley/occluded areas and bright practical-light areas;
- rooftop/ledge/wire/branch structure required for later vertical observers.

The acceptance test is rendered appearance, not polygon count. If representative close-range views still read as placeholder/debug/cheap low-poly work, the chunk fails.

## Materials and textures
Use Blender Principled BSDF/glTF-compatible material paths where practical.

Preferred physically based inputs:
- Base Color;
- Normal;
- Roughness;
- Metallic;
- Emissive;
- AO/occlusion where supported by the export/runtime path.

Use texture resolution according to approach distance and mobile cost. Do not keep 8K source textures in production merely because the source asset provides them. Create optimized runtime variants, normally 1K/2K for small/medium props unless close-range inspection materially justifies more.

Do not use post-processing as a substitute for missing material/geometry quality.

## Lighting
Blender may define authored light placement/reference and baked data, but the browser runtime remains responsible for the final runtime lighting strategy.

Night Intersection should preserve a coherent hierarchy of:
- environment/sky contribution;
- street/practical lights;
- storefront/window/sign emissive sources;
- vehicle lights where used;
- deliberately dark regions;
- shadows/occlusion/reflection response where performance allows.

When a light is not exported as a live glTF light, preserve an explicit `LIGHT_ANCHOR` or scene-manifest reference instead of hand-entering unrelated coordinates in multiple runtime files.

## Third-party assets and provenance
Every third-party visual asset must be registered in `src/spatial/assetManifest.ts` before it becomes a production dependency.

Required provenance includes:
- creator/author;
- canonical source URL;
- source asset ID/version when available;
- license/SPDX-style identifier;
- whether attribution is required;
- whether redistribution is allowed;
- local runtime path;
- notes describing Blender edits, scale/material changes or derived LODs when material.

Prefer CC0. CC-BY is allowed only when attribution obligations are tracked and satisfied. Do not ship unclear-license assets.

Poly Haven is an acceptable candidate source because its asset pages identify creator and CC0 status; any imported asset must still be recorded individually and optimized for browser use before production acceptance.

## Source and runtime asset roles
Use the existing `qualityRole` field consistently:
- `primary-visible` — final close-range asset that may count toward QR2 quality;
- `secondary-visible` — useful visible support asset;
- `distant-lod` — far representation only;
- `collision-only` — invisible collision/navigation geometry;
- `development-bootstrap` — loader/pipeline proof only; never closes the visible-quality gate.

Do not label a bootstrap asset `primary-visible` merely to satisfy a gate.

## Export contract
The canonical runtime format is `.glb` unless a specific `.gltf` + external-texture layout is intentionally required.

Before export:
1. verify metric scale and transforms;
2. verify normals/tangents and material assignment;
3. remove hidden authoring-only geometry from the export set;
4. verify collection/node names;
5. verify LOD/collision role separation;
6. verify texture paths and runtime texture resolution;
7. verify third-party redistribution rights and manifest entry.

Export should preserve:
- mesh hierarchy needed by runtime;
- PBR materials/textures;
- node names used for metadata/anchors;
- required animations when a future asset needs them.

Use `scripts/blender/export_night_intersection.py` as the initial automation entry point. The script validates the basic scene contract and exports selected Night Intersection collections to GLB. Expand it rather than creating unrelated one-off export scripts for each chunk.

## First implementation target: C0
The immediate authored-world target is `Night Intersection / C0`.

Order:
1. establish the Blender source scene and collection contract;
2. import/model a first real PBR primary-visible object and record provenance;
3. export it through the canonical script/path;
4. register the GLB in `src/spatial/assetManifest.ts`;
5. attach it to C0 in `src/spatial/nightIntersectionWorld.ts`;
6. prove mount/unmount through the existing `SpatialAssetRuntime` / chunk lifecycle;
7. preserve Human Scene/Observer/Vision state and Compare image behavior;
8. only then expand C0 into the full authored intersection core.

QR1 is **not** complete until a real authored PBR asset passes that runtime path and load/unload regression. The existence of this document, directories or export script is only pipeline establishment.

## Procedural-scene retirement rule
The current procedural Night Intersection may remain temporarily for technical comparison and fallback while C0 is rebuilt.

Do not add new primary-visible world detail to it.

As authored C0 reaches acceptance:
- move visible building/vehicle/street-furniture/vegetation responsibility to GLB assets;
- retain procedural geometry only where it is appropriate for debug, collision/proxy, road markings, distant LOD or other explicitly low-salience roles;
- remove duplicate visible procedural objects once their authored replacements are active;
- do not keep two independent versions of the same visible world merely to avoid deleting obsolete code.

## QR1 / QR2 gate
Pipeline establishment and product-quality acceptance are separate.

### QR1 pipeline/runtime proof
Must show:
- a real authored PBR asset;
- explicit provenance/license metadata;
- local repository/static-hosted runtime path;
- successful GLB load;
- successful unload/disposal without duplicate leaked objects;
- build/Compare image regression green.

### QR2 visible-core acceptance
Must additionally show:
- C0 no longer reads as primitive/debug/cheap low-poly at representative desktop/mobile viewpoints;
- close-range building/storefront/vehicle/street-furniture/vegetation detail is credible;
- Normal view is credible before Vision effects;
- Human movement remains usable.

Do not collapse these gates into an object-count, file-presence or CI-only check.
