# QR2 C0 rendered visual audit

Status: **IN PROGRESS / VISUAL FAIL / DO NOT MERGE AS QR2-COMPLETE**

Latest verified browser run: `34242568808` on head `dfea5b36f963301ae316a6d6e4a81905061fc594`.

The run is technically green. It proves that the rebuilt Blender-authored C0 loads, the Human camera turns, and bounded ground translation works. The dedicated movement proof changed yaw from `0` to `-0.966`, translated the observer from `[0,0,0]` to `[0.658,0,-0.455]`, and then swept to yaw `1.218`.

That technical success is **not QR2 acceptance**. Rendered inspection still fails the product-quality gate.

## Improvements confirmed in this pass

- Blender/Three.js axis mismatch is fixed; authored buildings now stand upright in the runtime frame.
- Poly Haven brick and asphalt scans are projected at approximately physical capture scale instead of stretching one texture over an entire facade/road face.
- The old procedural primary-visible C0 geometry is retired from the rendered foreground/midground so the Blender-authored core can be judged directly.
- The browser audit now has real turned and translated viewpoints rather than duplicate screenshots caused by attempting pointer input while the canvas was outside the viewport.

## Current visual failures

- Building macro-geometry still reads as simple blocks rather than authored architecture.
- Window openings remain shallow/repetitive and read as flat blue panels at walking distance.
- Storefronts lack believable interiors, glazing depth, merchandise/fixtures, door hardware, signage construction, and local practical-light detail.
- Vegetation is still placeholder geometry and is visibly unacceptable in the turned/moved viewpoints.
- The delivery vehicle and several street props remain low-detail authored primitives rather than production-quality assets.
- Lighting is too flat for a night scene; contact/shadow depth and material response are not yet strong enough.
- Sidewalk/street edges are clean and sparse; there are too few drains, covers, curb wear, decals, litter, utility details, parked objects, and other close-range scale cues.
- The scene does not yet have enough occlusion/variation to feel like a lived-in district rather than a staged intersection blockout.

## Next corrective pass

Do not spend the next pass increasing object count with more simple primitives. Replace high-salience close-range elements with genuinely authored assets and improve architectural depth.

Priority order:

1. replace placeholder vegetation with a game-suitable authored tree/plant asset and LOD;
2. replace bench/bin/utility/street furniture with detailed CC0 authored assets;
3. replace the blockout vehicle with an authored vehicle asset;
4. deepen storefront/window assemblies and add interior/parallax detail;
5. add coherent night environment/reflection lighting and controlled shadow/contact depth;
6. add close-range street/curb microdetail and decals;
7. rerun verified forward/turned/moved/opposite desktop views plus mobile views.

QR2 passes only when representative walking-distance screenshots no longer read as debug, cheap low-poly, or placeholder work. A green build/browser test is necessary but not sufficient.
