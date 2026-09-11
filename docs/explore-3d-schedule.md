# AsSeenBy — Explore 3D Execution Schedule

## Current state
Status: **REFERENCE-DRIVEN QUALITY RECOVERY ACTIVE / CONTINUOUS PRODUCTION**

Explore 3D Steps E1 through E4 were deployed and production-verified as technical implementation milestones. Those historical deployments remain valid facts, but the current `Night Intersection` presentation has been re-reviewed against the product-quality gate and is **not accepted as the final scene baseline**.

The current procedural scene proved Three.js depth/parallax, Human movement and Human Vision integration. The active rebuild replaces that invented presentation with an authored, reference-driven environment.

### Current reference decision
`Night Intersection` now uses **Hansaplatz, Berlin** as its canonical photographic/architectural reference rather than an invented generic intersection.

Primary reconstruction evidence:
- checked-in Poly Haven `Hansaplatz` 360 HDRI / tonemapped JPG by Greg Zaal, CC0-1.0;
- repeatable rectilinear reference plates generated from that panorama under `assets-src/blender/night-intersection/reference/hansaplatz/`;
- authoritative Hansaviertel architectural records for macro-layout cues such as the mostly single-storey shopping-centre ensemble, atrium arrangement, continuous flat roofs on slender steel supports and small white ceramic-tile finish.

The working sequence is now:
1. continue QR1–QR7 in `docs/explore-3d-quality-recovery.md`;
2. build C0 by matching real reference composition/material/architecture rather than inventing detail from scratch;
3. publish each coherent implementation increment to `main` immediately so the real site remains inspectable during development;
4. use rendered comparison to determine the next correction;
5. resume E5 Dog observer after the scene/world recovery closes.

**Important production rule:** QR quality status controls whether a milestone may be called visually complete. It does **not** block deployment of work-in-progress Explore 3D improvements. Completed implementation increments are expected to land on `main` and be visible in production while recovery continues.

Current product direction is defined by `docs/explore-3d-spec.md`, with the active recovery gate in `docs/explore-3d-quality-recovery.md`. Final-quality world authoring/export is governed by `docs/blender-asset-pipeline.md`.

## Execution rule
Before every Explore 3D implementation step, re-read:
1. `AGENTS.md`;
2. `docs/roadmap.md`;
3. `docs/explore-3d-spec.md`;
4. this schedule;
5. `docs/explore-3d-quality-recovery.md` while recovery remains active;
6. `docs/blender-asset-pipeline.md` for any asset/world/export work;
7. `docs/methodology.md` and `docs/limitations.md`;
8. relevant evidence files;
9. the historical `docs/spatial-pilot-spec.md` / `docs/spatial-pilot-schedule.md` only as prior-decision context.

If historical pilot text conflicts with the current Explore 3D spec, follow `docs/explore-3d-spec.md`.

If older E2–E4 completion wording conflicts with the active scene/world quality gate, follow `docs/explore-3d-quality-recovery.md`.

Do not rely on chat history as the sole source of product requirements.

## Step E0 — Finish active image/release work
Status: **PASS / R15 production verified**

R15 is closed. PR #40 merged as `c1673dfc7d20f890fb9f38ad2dfced1d2dc82855`; main build `34116997123` and production smoke `34116997193` both passed, including the permanent Tunnel aspect-ratio regression.

The image/release blocker is cleared.

## Step E1 — Architecture split: Scene / Observer / Vision
Status: **PASS / production verified**

Goal:
- refactor the panorama-only spatial component so Scene, Observer/controller and Vision/post-processing are explicit layers;
- retain the Hansaplatz panorama as `360° Photo Reference`;
- add public control structure for Scene / Observer / Vision without claiming unimplemented observers or vision models as complete.

Acceptance:
- `Compare image` unchanged;
- panorama still works as a reference scene;
- Vision changes preserve Scene/Observer/camera state;
- architecture can host geometry-based scenes and translating observers;
- desktop/mobile regression green;
- build and production verification green.

Implemented:
- current available Scene is explicitly `360° Photo Reference` and is owned by a Scene runtime rather than `SpatialPage` directly;
- current available Observer is explicitly `Human`; its fixed-photo look controls are owned by an Observer runtime and do not claim ground translation;
- existing Normal / Tunnel Vision / Central Loss / Night / Dog-like / Cataract-like post-processing is owned by a Vision runtime;
- public UI exposes Scene / Observer / Vision as separate controls without exposing unfinished Dog/Cat/Bird observers;
- permanent browser regression asserts the E1 control structure and verifies that switching Vision preserves scene, observer, yaw, pitch, FOV and camera position;
- production smoke waits for the E1 spatial architecture before accepting a freshly deployed release.

Production closeout:
- local full validation run `34121147909` passed desktop/mobile Compare image and Explore 3D regression; artifact `10018270114` was rendered-reviewed;
- PR #42 merged by squash as main commit `9a081da1639ba3228ee89e91766bc5c9101b1a18`;
- matching main build `34123678525` passed;
- matching production smoke `34123678534` passed against `https://asseenby.pages.dev` with `productionReleaseDetected=true`, desktop/mobile image=true, desktop/mobile spatial=true, stable E1 architecture detected on attempt 1, and `ok=true`;
- production smoke artifact `10019243348` was uploaded.

## Step E2 — Night Intersection geometry baseline
Status: **HISTORICAL TECHNICAL PASS / PRODUCT-QUALITY ACCEPTANCE REOPENED**

Original goal:
- build the first real Three.js environment;
- prove geometry-based depth/parallax and a non-panorama Scene path.

The original implementation used a roughly `150x150x60` authored volume, procedural facade/material generation, repeated primitive geometry, 471 scene objects and 12 lights. It proved camera translation/parallax and the Scene runtime, and was production-verified as commit `d67157c9f806c508f19523e7fe4c3cbe404a6cdb`.

That technical proof remains useful, but the scene is no longer accepted as the final presentation baseline. In particular, the earlier acceptance sentence that the scene should not read as debug/low-effort was not satisfied strongly enough by the primitive/procedural implementation.

The old 150 m extent is also no longer an architectural ceiling. The recovery work moves Night Intersection toward asset-first rendering plus chunking/LOD/streaming capable of district-scale expansion.

Historical production verification:
- final E2 visual/browser validation run `34132000347` passed the then-current technical checks;
- PR #44 merged by squash as main commit `d67157c9f806c508f19523e7fe4c3cbe404a6cdb`;
- matching main build `34135941939` passed;
- matching production smoke `34135941956` passed.

These runs prove the old implementation was deployed and behaved as tested. They do **not** close the newly reopened visual-product gate.

## Step E3 — Human observer and bounded movement
Status: **HISTORICAL TECHNICAL PASS / REUSED DURING RECOVERY**

The current Human movement contract remains useful:
- approximately 1.6 m standing viewpoint;
- yaw-relative W/A/S/D movement;
- Shift speed increase;
- desktop/mobile movement controls;
- Reset;
- Vision state preservation.

Historical implementation used a fixed authored cross-shaped navigation area and hand-entered obstacle rectangles. That collision representation is now considered prototype-specific and must be replaced by the scalable collision/navigation work in QR4.

Historical production closeout:
- validation run `34143680918` passed the then-current movement/collision/browser checks;
- PR #46 squash-merged as `47d7c0f9a15b62520b1a4a8994043668c14553cd`;
- matching main build `34144520176` passed;
- matching production smoke `34144520172` passed.

## Step E4 — Human spatial Vision integration
Status: **HISTORICAL TECHNICAL PASS / VISION WORK REMAINS REUSABLE**

Accepted Human geometry Vision modes remain:
- Normal;
- Tunnel Vision;
- Central Loss;
- Night / Low Light;
- Cataract-like.

The existing Vision state-preservation and evidence/limitations work remains valid unless separately changed. The recovery is not a reason to discard correct Vision behavior.

Historical production closeout:
- final E4 validation run `34148557108` passed build, desktop/mobile geometry Vision behavior, same-state Vision switching, Compare image regression and local production smoke;
- rendered validation recorded the then-current Tunnel/Central/Night/Cataract metrics;
- PR #47 squash-merged as `58fbd132c24f5d182b90e8c55a096d500419b580`;
- matching main build `34148945521` passed;
- matching production smoke `34148945534` passed.

Those checks validate the Vision implementation over the current rendered frame. They do not validate the underlying scene as final-quality.

# Recovery sequence before E5

## QR1 — Runtime and asset contract
Status: **PASS / merged / production path established**

Accepted foundation:
- glTF/GLB loading;
- asset/texture lifecycle and disposal path;
- scene/chunk manifest types;
- chunk load state;
- third-party asset/license provenance manifest type;
- compatibility with current Scene / Observer / Vision state contracts;
- streamed Night Intersection world envelope/chunk scaffold;
- real authored PBR asset through the production runtime;
- browser-verified load -> unload -> remount lifecycle without duplicate authored roots.

The authored production path is fixed:
- Blender is the canonical DCC authoring/assembly tool for new primary-visible world content;
- `docs/blender-asset-pipeline.md` defines units, collection roles, PBR/material, provenance and export rules;
- `assets-src/blender/night-intersection/` is the source workspace;
- `public/assets/3d/night-intersection/` is the optimized runtime asset path;
- `scripts/blender/export_night_intersection.py` is the canonical export automation entry point;
- the first authored target is central 64 m chunk `C0`.

Do **not** add new primary-visible detail to the procedural `nightIntersectionScene.ts` to bypass this path.

## QR2 — Visible Night Intersection rebuild
Status: **ACTIVE / REFERENCE-DRIVEN / CONTINUOUSLY DEPLOYED**

C0 is now rebuilt and iterated as an authored Blender/GLB environment against the real Hansaplatz reference rather than as an invented generic street.

Current implementation direction:
- the checked-in Hansaplatz equirectangular photo is the canonical visual reference and runtime far environment;
- six fixed perspective reference plates are generated reproducibly for comparison;
- invented brick-block macro geometry is being replaced with Hansaplatz-specific modernist low-rise pavilions, glazed storefronts, continuous canopies on slender steel supports, a plaza/atrium, transit entry and white ceramic-tile architectural language;
- authored CC0 props/materials remain reusable when they match the reference;
- each coherent improvement is committed to `main` and allowed to appear on the public site before the final QR2 quality bar is reached.

Acceptance for declaring QR2 visually complete remains:
- representative desktop and mobile screenshots no longer read as placeholder/debug/cheap low-poly work;
- primary architecture/storefronts, vehicles, street furniture and vegetation survive close walking distance;
- rendered composition materially matches the Hansaplatz photographic reference rather than merely being internally detailed;
- Normal mode is credible before any Vision effect;
- Human movement remains usable.

Failure to meet those acceptance points means “continue iterating”, **not** “withhold the current implementation from production”.

## QR3 — Chunking, LOD and district-scale envelope
Status: **queued**

Remove the old 150 m architectural cap and prove a streamed/chunked district runtime.

Acceptance:
- multiple chunks can load/unload based on observer position;
- nearby chunks can remain high detail while distant chunks are lower LOD or unloaded;
- runtime architecture can address a world envelope on the order of 500 m × 500 m without requiring all high-detail content resident at once;
- scene state remains coherent across chunk boundaries.

## QR4 — Collision/navigation rebuild
Status: **queued**

Replace the fixed hand-entered rectangle collision list with scene/chunk collision/navigation data.

Acceptance:
- Human cannot walk through primary buildings/vehicles/major obstacles;
- collision remains stable across chunk boundaries;
- collision representation is independent from final visual geometry;
- architecture can later support Dog/Cat envelopes and Bird volumetric collision.

## QR5 — Vertical/climb/perch contract
Status: **queued**

Add real vertical structure and metadata needed by Cat/Bird.

Acceptance:
- rooftops/ledges/wires/branches/poles or equivalent reachable spatial targets exist;
- scene metadata can expose Cat climb/perch and Bird landing targets without rewriting the Scene architecture.

## QR6 — Interior continuity proof
Status: **queued**

Add at least one authored exterior-to-interior-to-exterior path.

Acceptance:
- transition is reachable through normal movement rather than a fake scene reset;
- collision/navigation zone changes correctly;
- Observer and Vision state remain coherent.

## QR7 — Product-quality closeout
Status: **queued**

Run:
- build/typecheck;
- desktop rendered review;
- mobile rendered review;
- movement/collision regression;
- Vision state-preservation regression;
- Compare image regression;
- production deployment/smoke verification.

Closeout rule:
- object count is not enough;
- source inspection is not enough;
- shader metrics are not enough;
- production smoke is not enough;
- the presence of glTF files is not enough.

QR7 passes only when representative rendered views satisfy the scene-quality bar in `docs/explore-3d-quality-recovery.md`. The rule determines the quality-closeout label, not whether intermediate implementation is allowed on `main`.

## Step E5 — Dog observer
Status: **BLOCKED BY QR1–QR7 CLOSEOUT / CURRENT WORK MAY STILL DEPLOY**

After the recovery gate passes, add a low ground observer, initially around 0.5–0.6 m.

Acceptance:
- lower viewpoint creates materially different occlusion from Human;
- ground collision/navigation remains stable;
- `Normal` can be used at Dog height independently of Dog-like Vision;
- Dog-like Vision can be toggled without camera reset.

## Step E6 — Dog-like 3D Vision refinement
Status: **BLOCKED BY QR1–QR7 CLOSEOUT / then queued after E5**

Move Dog-like detail loss toward distance/projected-angular-size behavior rather than relying only on full-screen softening.

Keep the existing scientific boundary: visible-range human-display proxy, not literal canine perception.

## Step E7 — Cat observer
Status: **BLOCKED BY QR1–QR7 CLOSEOUT**

Add a lower observer around 0.3 m and authored climb/perch interactions.

Initial accepted behavior may use explicit climbable/perchable targets instead of general climbing physics.

Important: this step does **not** restore Cat-like Vision.

Acceptance:
- low viewpoint materially changes scene visibility;
- at least one authored elevated Cat-reachable target works;
- Cat can use Normal vision;
- unsupported Cat-specific Vision remains absent.

## Step E8 — First Bird species selection and observer
Status: **BLOCKED BY QR1–QR7 CLOSEOUT / species decision required before implementation**

Select one concrete bird species suitable for the first scene. A city species such as Pigeon is a practical candidate, but the choice must be documented before release.

Implement observer flight independent of species-specific color Vision.

Acceptance:
- free-space 3D flight inside navigation/altitude bounds;
- ascend/descend controls;
- real camera-height change and parallax;
- collision with major geometry;
- authored landing/perch targets;
- useful flight altitude roughly 30–50 m initially, expandable toward 50–80 m where scene composition supports it;
- Bird is not forced into Human/Dog ground-walking controls.

## Step E9 — Bird species Vision evidence gate
Status: **blocked until species/model/data review**

Do not create a generic `Bird-like` shader.

Before any species-specific visual renderer:
- document species visual evidence;
- decide what ordinary RGB can support;
- identify any UV/spectral source-data requirement;
- define human-display translation and caveats;
- define rendered acceptance criteria.

Observer flight may ship before this visual-model step.

## Step E10 — Additional scenes
Status: **future**

Add dense scenes one at a time after the rebuilt Night Intersection architecture is stable.

Candidate order:
1. Daytime Park;
2. Store / Supermarket;
3. Home / Apartment;
4. Station / Platform.

Each scene must justify which Observer/Vision comparisons it improves.

## Step E11 — 360° Photo Reference integration polish
Status: **future**

Keep Hansaplatz as a clearly labeled photographic reference scene.

Do not present it as the full Explore 3D experience.

## Permanent rules
- The active QR2 source candidate adds the missing Hansaplatz tall perimeter facade
  layer in Blender; regeneration and fresh rendered comparison are still required,
  so this source increment is not a QR2 quality-closeout claim.
- **Work-in-progress visual quality does not block deployment.** Completed Explore 3D implementation increments go to `main` so the public site can be inspected continuously.
- Quality labels still matter: do not call a weak render QR2/QR7 complete merely because it was deployed.
- Hansaplatz is the canonical current Night Intersection reconstruction reference; new macro architecture must be justified against the real reference instead of invented generic city-block styling.
- Reference -> authored assets -> Blender assembly -> browser render -> rendered critique -> correction is the normal art-production loop.
- Blender is the canonical authoring/assembly layer for new primary-visible Explore 3D world content; Three.js remains the runtime.
- Do not treat a primitive/procedural scene as accepted merely because Three.js, movement, shaders and smoke checks work.
- Do not extend the old procedural scene with new primary-visible art to evade the authored asset path.
- The old 150 m scene size is not an architectural ceiling; larger district-scale space must use chunking/LOD/streaming rather than all-resident geometry.
- Observer and Vision remain independent concepts.
- Bird movement uses the air/vertical space; species vision is a separate evidence problem.
- Cat observer movement does not resurrect the rejected Cat-like visual filter.
- UV/spectral perception is never fabricated from ordinary RGB.
- Third-party assets require explicit provenance/license tracking.
- Every completed visual/spatial recovery step requires rendered review where visual behavior matters.
- If the user changes an accepted product behavior, update `docs/explore-3d-spec.md`, this schedule, and the active quality-recovery document in the same implementation change before declaring the step complete.

## Isolated Astra experiment — 2026-09-11

`exp/astra-hansaplatz-c0-20260911` uses GitHub-hosted Blender and application browser
checks. This experiment does not merge, deploy, or modify the other quality branch.
Hamburg source lock / LoD2 / shared Day-Night geometry govern this experiment and
supersede the historical Berlin/pavilion wording above. Status and visual evidence:
`docs/experiments/hansaplatz-astra/README.md`. QR2 remains open pending visual review.
