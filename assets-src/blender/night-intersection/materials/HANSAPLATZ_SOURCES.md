# Hansaplatz reference-matched material sources

These materials are build-time source inputs for the Blender-authored Hansaplatz C0 reconstruction. The production renderer does not fetch them from Poly Haven at runtime; the maps are packed into the canonical authored Blender/GLB output.

Both source assets are distributed by Poly Haven under **CC0-1.0**. `scripts/polyhaven/fetch_texture_bundle.py` also writes a machine-readable manifest from Poly Haven's current `/info/{id}` and `/files/{id}` responses, including authorship metadata, source URLs and downloaded-file hashes.

## `rounded_square_tiled_wall`

- Provider: Poly Haven
- Canonical source: https://polyhaven.com/a/rounded_square_tiled_wall
- Role: Hansaplatz pavilion / retail facade surface
- Source capture width used for texture scale: 2.0 m
- Maps used: 1K diffuse, OpenGL normal, roughness
- Runtime authoring adjustment: strongly desaturated and brightened toward the white ceramic cladding visible in the Hansaplatz reference while retaining scanned grout, surface variation and normal detail
- License: CC0-1.0

## `concrete_pavement`

- Provider: Poly Haven
- Canonical source: https://polyhaven.com/a/concrete_pavement
- Role: Hansaplatz plaza / walking-surface material
- Source capture width used for texture scale: 1.8 m
- Maps used: 1K diffuse, OpenGL normal, roughness
- Runtime authoring adjustment: restrained saturation/value correction only; scanned pavement variation supplies the near-ground texture and wear cues
- License: CC0-1.0

Generated files under `assets-src/blender/night-intersection/materials/hansaplatz/` are reproducible source cache inputs and are committed with SHA-256 hashes. The final production asset remains `public/assets/3d/night-intersection/c0/core/night-intersection-c0.glb`.
