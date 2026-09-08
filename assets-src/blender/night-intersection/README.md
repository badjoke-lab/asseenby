# Night Intersection — Blender source workspace

This directory is the canonical authoring workspace for the rebuilt Explore 3D Night Intersection.

Read `docs/blender-asset-pipeline.md` before adding scene content.

## Initial target

Start with the central 64 m chunk `C0`. Do not attempt to populate the full ~500 m district before C0 meets the close-range rendered quality gate.

Target source organization:

```text
core/
buildings/
streets/
interiors/
props/
vegetation/
```

A chunk scene should expose the documented role collections where applicable:

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

Use metric units with 1 Blender unit = 1 meter. Apply transforms before final export unless a documented exception exists. Production nodes must use stable names rather than Blender defaults such as `Cube.001`.

Third-party assets require provenance/license registration in `src/spatial/assetManifest.ts` before they become production dependencies.

The current procedural Night Intersection remains a temporary technical fallback. Do not extend it with new primary-visible detail instead of authoring the replacement here.
