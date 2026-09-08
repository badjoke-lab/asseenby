# QR2 C0 rendered visual audit

Status: **IN PROGRESS / VISUAL FAIL UNTIL RENDERED RECHECK / DO NOT MERGE AS QR2-COMPLETE**

Latest accepted technical browser run: `34242568808` on head `dfea5b36f963301ae316a6d6e4a81905061fc594`.

A newer Blender-generated C0 candidate now exists at `31ca779f52146373c30f3ea4cc96377992b342ae`. It replaces several high-salience placeholders with authored CC0 models, packs them into the canonical Blender source, adds shallow storefront interiors, and adds authored practical lights. This candidate is **not accepted by this document until its generated GLB is re-run through the browser screenshot audit and inspected visually**.

The earlier run was technically green. It proved that the rebuilt Blender-authored C0 loads, the Human camera turns, and bounded ground translation works. The dedicated movement proof changed yaw from `0` to `-0.966`, translated the observer from `[0,0,0]` to `[0.658,0,-0.455]`, and then swept to yaw `1.218`.

That technical success is **not QR2 acceptance**. Rendered inspection of the earlier candidate failed the product-quality gate.

## Improvements already confirmed before the authored-prop pass

- Blender/Three.js axis mismatch is fixed; authored buildings now stand upright in the runtime frame.
- Poly Haven brick and asphalt scans are projected at approximately physical capture scale instead of stretching one texture over an entire facade/road face.
- The old procedural primary-visible C0 geometry is retired from the rendered foreground/midground so the Blender-authored core can be judged directly.
- The browser audit has real turned and translated viewpoints rather than duplicate screenshots caused by attempting pointer input while the canvas was outside the viewport.

## New candidate awaiting rendered inspection

The generated C0 at `31ca779f52146373c30f3ea4cc96377992b342ae` adds the following Blender-authored replacements and depth work:

- Poly Haven `street_lamp_02` instances for intersection street lighting;
- Poly Haven `modular_street_seating` in place of bench blockouts;
- Poly Haven `utility_box_02` and `metal_trash_can` in place of street-prop blockouts;
- Poly Haven `covered_car` in place of the blockout delivery vehicle;
- Poly Haven `jacaranda_tree` instances in place of the obvious tree placeholders;
- shallow modeled interiors behind all four primary storefront glazing systems, including floor, rear wall, counter, shelving and emissive ceiling panels;
- authored Blender point lights for four street-practical and four storefront-practical positions.

All listed third-party model sources are CC0 and are recorded under `assets-src/blender/night-intersection/third-party/SOURCES.md`.

## Earlier visual failures that must be re-evaluated now

- Building macro-geometry still read as simple blocks rather than authored architecture.
- Window openings were shallow/repetitive and read as flat blue panels at walking distance.
- Storefronts lacked believable interiors, glazing depth, merchandise/fixtures, door hardware, signage construction, and local practical-light detail.
- Vegetation was placeholder geometry and visibly unacceptable in the turned/moved viewpoints.
- The delivery vehicle and several street props were low-detail authored primitives rather than production-quality assets.
- Lighting was too flat for a night scene; contact/shadow depth and material response were not strong enough.
- Sidewalk/street edges were clean and sparse; there were too few drains, covers, curb wear, decals, litter, utility details, parked objects, and other close-range scale cues.
- The scene did not have enough occlusion/variation to feel like a lived-in district rather than a staged intersection blockout.

## Immediate rendered gate

Run the generated authored-prop C0 through the verified browser audit and inspect forward, turned, translated, opposite and mobile captures. Reject and iterate immediately if imported model scale/orientation/grounding, storefront visibility, lighting, architecture or close-range density is visibly wrong.

If the authored-prop pass fixes the vegetation/vehicle/street-furniture blockers, the next Blender pass must focus on the remaining architecture, glazing/storefront construction, lighting depth and street microdetail rather than returning to primitive-object-count growth.

QR2 passes only when representative walking-distance screenshots no longer read as debug, cheap low-poly, or placeholder work. A green build/browser test is necessary but not sufficient.
