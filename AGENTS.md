# AsSeenBy — Agent Instructions

These instructions are the repository-level working rules for implementation agents.

## Required reading before changing code
Read these files before implementation and use them as the source of truth for scope and product claims:

1. `README.md`
2. `docs/roadmap.md`
3. `docs/release-polish-schedule.md` for current image/release-polish execution and production-verification state
4. `docs/methodology.md`
5. `docs/limitations.md`
6. `docs/ui-spec.md`
7. `docs/modes.md` and `docs/evidence-model.md` when changing perception modes or evidence UI

For **any Explore 3D / Three.js / spatial / observer / scene / movement work**, also read before implementation:

8. `docs/explore-3d-spec.md` — **current canonical 3D product specification**
9. `docs/explore-3d-schedule.md` — **current canonical 3D execution order and status**
10. `docs/explore-3d-quality-recovery.md` — **active blocking scene/world quality recovery before E5+**
11. `docs/spatial-pilot-spec.md` — historical pilot/evidence/design record
12. `docs/spatial-pilot-schedule.md` — historical pilot execution record

If the historical spatial-pilot documents conflict with `docs/explore-3d-spec.md` on current product shape, movement, observer behavior, scene architecture, 360°-photo role, or implementation direction, **`docs/explore-3d-spec.md` controls**.

If older E2–E4 completion wording conflicts with `docs/explore-3d-quality-recovery.md` on whether the current Night Intersection presentation is accepted as final product quality, **the quality-recovery gate controls**.

If code and documentation disagree, do not silently invent a new direction. Preserve the documented product boundary or update the relevant current spec/schedule in the same change.

Do not rely on chat history alone for accepted product behavior. Durable decisions must be represented in the repository documentation.

## Product invariants
- Keep the existing static-image comparison experience. Explore 3D is additive, not a replacement.
- The image experience remains `Compare image`; the current 3D product name is `Explore 3D`.
- Do not turn AsSeenBy into a game, generic 3D showcase, medical tool, or claim of exact perception.
- Every perception output is a research-based approximation/reference view subject to the evidence and limitation documents.
- Do not claim UV, polarization, full species-specific spectral perception, neural interpretation, diagnosis, or patient-level accuracy unless a future accepted spec explicitly adds a validated data/model path.
- Keep uploads browser-side. Do not add accounts, saved sessions, server-side image storage, or an API unless separately specified.
- Preserve the editorial field-guide / research-book visual language. Avoid generic dark SaaS, glow, glass, or game-HUD styling.

## Explore 3D architecture invariants
- Explore 3D is **not** a 360° panorama viewer with filters and is **not** a primitive-geometry demo. Its current architecture is `Scene / Observer / Vision`.
- The existing Hansaplatz 360° panorama remains useful as `360° Photo Reference`, but it is only one reference Scene and must not define the capability ceiling of Explore 3D.
- Real 3D scenes must use geometry/depth/parallax and, where relevant, real scene lighting, occlusion, distance and vertical space.
- The final-quality visible scene path is asset-first: primary close-range buildings, vehicles, street furniture, vegetation and other salient objects should use authored detailed meshes/PBR materials rather than treating BoxGeometry plus generated textures as the final presentation layer.
- Primitive geometry remains valid for collision/proxy/debug helpers, simple repeated elements and distant LODs when it does not become the visible quality ceiling.
- Observer and Vision are separate. Changing only Vision must preserve Scene, Observer, camera position/direction, FOV, lighting/time and object state.
- Observer changes may alter camera height, movement model, collision envelope, reachable space, altitude bounds and reset state according to the current spec.
- Current Observer architecture must support Human, Dog, Cat and species-specific Bird presets over time.
- Human uses bounded/free authored ground movement; Dog uses a materially lower ground viewpoint; Cat uses a lower viewpoint plus authored climb/perch targets; Bird uses actual free-space flight with ascend/descend and perch/landing behavior.
- A Bird observer must not be implemented as a Human/Dog ground walker. Bird flight and Bird vision are separate requirements.
- Adding Cat/Bird observers does not automatically restore the previously rejected generic Cat-like/Bird-like RGB visual filters.
- Generic Bird-like spectral/color vision remains rejected from ordinary RGB. Any future Bird visual renderer must be species-specific and pass a separate evidence/model/data gate.
- Bee-like/UV work remains blocked until explicit UV-reflectance/spectral scene data and a documented observer/false-color model exist. Never substitute a purple/blue filter for missing UV information.
- Dog-like remains a conservative visible-range human-display proxy; do not claim exact canine cone catches, universal breed FOV, motion processing, tapetal/rod low-light reconstruction or literal qualia from ordinary RGB.
- Scene density/explanatory value matters more than empty map size, but the runtime must not hard-code the old 150 m scene as an architectural ceiling. Night Intersection is moving toward chunking/LOD/streaming capable of a district-scale envelope on the order of 500 m × 500 m when content warrants it.
- `Night Intersection` is the first full geometry-based target scene. Later candidate scenes include Daytime Park, Store/Supermarket, Home/Apartment and Station/Platform.
- Bounded/free movement is now an accepted 3D requirement where specified. The old pilot rule prohibiting walking/collision is historical and no longer controls current Explore 3D work.
- Bounded/free movement does **not** authorize game mechanics: no combat, scoring, inventory, character progression, quests or unrelated game loop.
- Scene presentation quality remains blocking. A technically correct shader, object-count metric, smoke test or production deploy must not be accepted if representative rendered views still read as placeholder/debug/cheap low-detail work.
- E5 Dog observer and later observer phases are blocked until `docs/explore-3d-quality-recovery.md` reaches QR7 product-quality closeout.

## Asset / world rules
- Record third-party 3D asset provenance and redistribution rights in an asset/license manifest.
- Prefer CC0; use CC-BY only with tracked attribution; do not ship assets with unclear rights.
- Use glTF/GLB and PBR materials for authored primary visible assets where practical.
- Use chunk streaming, LOD, culling, reuse/instancing and compressed textures so larger scenes remain static-hosting/browser compatible.
- Keep collision/navigation representation separable from final visual geometry.
- Do not permanently model world collision as a fixed hand-entered rectangle list tied to one prototype intersection.
- The architecture must support authored exterior/interior continuity and Cat/Bird climb/perch/landing metadata without replacing the scene runtime again.

## Image / perception invariants
- The existing `src/transformEngine.ts` remains the image renderer for `Compare image`.
- Image Strength semantics, evidence/model claims and production-smoke gates remain governed by the current release-polish/methodology/limitations documents.
- Reuse existing mode evidence and limitations wherever applicable instead of creating unsupported duplicate claims.
- Keep renderer-specific Model notes separate from underlying phenomenon Evidence.

## Engineering rules
- Prefer the smallest change that satisfies the active schedule step, except where the accepted scene-quality/architecture gate explicitly requires a broader coherent change.
- During QR1–QR7, do not preserve the old scene implementation merely to minimize diff size when doing so conflicts with the accepted asset/world architecture.
- Keep the current React + TypeScript structure unless a documented requirement needs restructuring.
- Three.js remains isolated from the 2D Canvas transform engine, but Explore 3D may be refactored internally into Scene, Observer/controller and Vision layers as required by the canonical spec.
- Avoid unrelated refactors while a scheduled step is being validated.
- Keep desktop and mobile behavior usable.
- Run `npm run build` before declaring an implementation step complete. The existing GitHub workflow runs the same typecheck + Vite build on pull requests and main.
- For production-verification steps, preview/local success is not enough: test the public production URL and record stale/deployment-state failures separately from code failures.
- Where visual/spatial behavior materially changes, include a rendered/browser acceptance check, not only source inspection or typecheck.

## Progress discipline
At the start of **every** implementation step, re-read `AGENTS.md`, `docs/roadmap.md`, and the active schedule for that workstream.

At the start of every Explore 3D step, re-read at minimum:
- `docs/explore-3d-spec.md`;
- `docs/explore-3d-schedule.md`;
- `docs/explore-3d-quality-recovery.md` while the recovery remains active;
- relevant methodology/limitations/evidence sections.

Read the old spatial-pilot spec/schedule when prior decisions matter, but do not let historical pilot restrictions override the current Explore 3D spec.

At the start of each image/release-polish step, re-read `docs/release-polish-schedule.md` and `docs/roadmap.md`; if the step touches Explore 3D behavior, also re-read the current Explore 3D spec/schedule/quality-recovery document.

When a step is completed, blocked, rejected, or materially changed:
- update the active schedule in the same branch/PR;
- update `docs/explore-3d-spec.md` if current 3D product behavior, observer behavior, scene architecture, movement, source-data boundary or acceptance criteria changed;
- update `docs/explore-3d-quality-recovery.md` for QR1–QR7 state/acceptance changes while that gate is active;
- update `docs/methodology.md` / `docs/limitations.md` if the scientific or claim boundary changed;
- update `docs/roadmap.md` if product priority/order changed materially.

When the user makes a new product decision that changes accepted behavior, **do not leave that decision only in conversation history**. Before declaring related implementation complete, reflect it in the canonical spec/schedule/recovery documents and then continue using those repository documents as the source of truth.

Do not mark a step complete merely because scaffolding exists. Status is based on the acceptance criteria in the active schedule/recovery gate, including actual rendered review where required and production verification where explicitly required.
