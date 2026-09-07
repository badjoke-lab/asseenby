# AsSeenBy — Explore 3D Execution Schedule

## Current state
Status: **E4 PASS / production verified**

Explore 3D Steps E1 through E4 are production verified. `Night Intersection` is the default real-geometry scene with bounded Human movement and the accepted Human spatial Vision set, while Hansaplatz remains the `360° Photo Reference`. The next queued implementation step is E5 Dog observer.

Current product direction is defined by `docs/explore-3d-spec.md`.

## Execution rule
Before every Explore 3D implementation step, re-read:
1. `AGENTS.md`;
2. `docs/roadmap.md`;
3. `docs/explore-3d-spec.md`;
4. this schedule;
5. `docs/methodology.md` and `docs/limitations.md`;
6. relevant evidence files;
7. the historical `docs/spatial-pilot-spec.md` / `docs/spatial-pilot-schedule.md` only as prior-decision context.

If historical pilot text conflicts with the current Explore 3D spec, follow `docs/explore-3d-spec.md` and update this schedule when implementation details are accepted or changed.

Do not rely on chat history as the sole source of product requirements.

## Step E0 — Finish active image/release work
Status: **PASS / R15 production verified**

R15 is closed. PR #40 merged as `c1673dfc7d20f890fb9f38ad2dfced1d2dc82855`; main build `34116997123` and production smoke `34116997193` both passed, including the permanent Tunnel aspect-ratio regression.

The image/release blocker is cleared. New product work may proceed to E1 without broadening or reopening R15.

## Step E1 — Architecture split: Scene / Observer / Vision
Status: **PASS / production verified**

Goal:
- refactor the current panorama-only spatial component so Scene, Observer/controller and Vision/post-processing are explicit layers;
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
Status: **PASS / production verified**

Build the first real Three.js environment, targeting roughly 150 m × 150 m × 50–60 m of useful volume.

Required minimum layers:
- geometry-based streets/buildings;
- facades/storefronts/signs;
- road/sidewalk/crossing detail;
- vehicles and pedestrians;
- street furniture;
- vegetation;
- real vertical structure such as rooftops/poles/wires/branches/ledges;
- near/mid/far targets;
- coherent night-light hierarchy.

Acceptance:
- visible depth/parallax during camera translation;
- scene no longer reads as a panorama or debug/low-effort environment;
- Normal mode is useful before adding perception effects;
- mobile performance remains acceptable.

Implemented baseline:
- `Night Intersection` is the default Explore 3D Scene; Hansaplatz remains separately available as `360° Photo Reference`;
- authored scene volume is `150x150x60`, with streets, sidewalks/crossings, multi-part buildings, procedural facade detail, storefronts/signs, vehicles, pedestrians, signals, streetlights, furniture, vegetation, wires/roof targets and near/mid/far references;
- the current optimized scene exposes 471 scene objects and 12 lights, with repeated road markings batched through instancing;
- Human / Normal is intentionally the only geometry-scene Observer/Vision combination in E2; accepted Photo Reference Vision modes remain available on the photographic scene;
- `Reference` and `Offset` authored viewpoints translate camera position from `0,0,0` to `3.2,0,-4.2` while preserving yaw, pitch and FOV, providing an explicit parallax proof before E3 free movement;
- ACES tone mapping, authored practical/emissive lighting and procedural material texture are used; expensive realtime shadow mapping is deferred rather than sacrificing the E2 interaction baseline.

Validation:
- final E2 visual/browser validation run `34132000347` passed desktop/mobile with no page or console errors; artifact `10022490421` was rendered-reviewed;
- final validation recorded 471 objects / 12 lights / `150x150x60`, preserved Reference/Offset direction and FOV, produced different rendered canvas output after translation, and retained all accepted Photo Reference Vision controls;
- CI software-render `loadMs` varied materially between runners and is not used as a release threshold; the permanent release gate checks behavior/scene metadata instead;
- PR #44 merged by squash as main commit `d67157c9f806c508f19523e7fe4c3cbe404a6cdb`;
- matching main build `34135941939` passed;
- matching production smoke `34135941956` passed against `https://asseenby.pages.dev` with `productionReleaseDetected=true`, `e2SpatialReleaseDetected=true`, desktop/mobile image=true, desktop/mobile spatial=true, the E2 Night Intersection fingerprint detected on attempt 1, and `ok=true`;
- production smoke artifact `10024024552` was uploaded.

## Step E3 — Human observer and bounded movement
Status: **PASS / production verified**

Add a generic standing Human observer around 1.6 m with bounded ground movement.

Desktop baseline:
- pointer look;
- WASD movement;
- Shift speed modifier;
- Reset;
- restrained FOV control only if validated.

Mobile baseline:
- touch look;
- compact movement control;
- Reset.

Acceptance:
- collision/navigation bounds prevent leaving the useful scene or walking through major geometry;
- camera translation produces correct parallax;
- Vision switching never moves the observer;
- no game-loop mechanics are introduced.

Implemented E3:
- Night Intersection Human uses a 1.6 m reference eye height with yaw-relative W/A/S/D ground movement;
- Shift provides a moderate desktop speed increase; R and the visible Reset observer control restore position, direction, FOV and movement state;
- mobile exposes a compact four-direction movement pad plus the same Reset observer control;
- navigation is constrained to an authored cross-shaped road/sidewalk area and rejects entry into listed major vehicle/street obstacles; axis-separated collision resolution allows sliding instead of requiring a physics engine;
- free movement marks the camera viewpoint as `free`, so the guided Reference/Offset controls do not falsely remain selected;
- `360° Photo Reference` remains look-only and receives no ground-movement controls;
- Night Intersection still exposes Normal only; Human Vision integration remains E4.

Validation requirement before merge:
- build;
- desktop keyboard movement / faster Shift movement / Reset / navigation bound checks;
- mobile movement-pad touch targets / movement / Reset;
- Photo Reference look-only regression;
- full Compare image + Explore 3D production-smoke regression with an E3-specific stale-release fingerprint.

Production closeout:
- full E3 validation run `34143680918` passed movement speed, collision, authored bounds, Reset, Photo Reference look-only behavior, real mobile touch movement, and the full local production-smoke regression; validation artifact `10026994364` was uploaded;
- PR #46 was squash-merged as main commit `47d7c0f9a15b62520b1a4a8994043668c14553cd`;
- matching main build `34144520176` passed;
- matching production smoke `34144520172` passed against `https://asseenby.pages.dev` with `productionReleaseDetected=true`, `e2SpatialReleaseDetected=true`, `e3HumanMovementDetected=true`, desktop/mobile image=true, desktop/mobile spatial=true, and `ok=true`;
- production smoke artifact `10027185737` was uploaded.

## Step E4 — Human spatial Vision integration
Status: **PASS / production verified**

Port/adjust the accepted Human spatial modes to the geometry scene:
- Normal;
- Tunnel Vision;
- Central Loss;
- Night / Low Light;
- Cataract-like.

Use true scene information where it improves the model:
- real lights/occlusion for Cataract-like glare where feasible;
- scene lighting/current-view information for Night / Low Light;
- view-relative field effects for Tunnel/Central.

Acceptance requires same-position/same-direction comparisons and evidence/limitation review.

Implemented E4:
- Night Intersection × Human exposes exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like; Dog-like remains Photo Reference-only until the Dog observer phase;
- the existing live Vision runtime is applied to the geometry renderer rather than duplicating the image transform engine;
- Tunnel/Central remain view-relative post-processing effects over the live geometry frame;
- Night / Low Light uses the current rendered frame's relative luminance, so authored geometry/material/light visibility changes its input while remaining explicitly non-calibrated;
- Cataract-like gates local glare from visible high-luminance rendered pixels, so geometry occlusion and visible practical/emissive sources affect the glare input without claiming calibrated lens scatter;
- Vision switching preserves Scene, Human observer, camera position, direction, FOV, lighting/object state and free/guided viewpoint state;
- Night / Low Light now has a spatial Evidence panel even though it is intentionally absent from the public image-mode registry.

Validation requirement before merge:
- build;
- same-position/same-direction/FOV checks for all five geometry Human Vision modes after both guided and free movement;
- rendered Tunnel edge-dominance and Central center-dominance checks;
- rendered Night dark-versus-bright response and Cataract bright-source response checks;
- Night spatial Evidence panel availability;
- desktop and 390px mobile geometry Vision usability with no horizontal overflow/errors;
- Photo Reference accepted Vision set unchanged;
- full Compare image regression;
- permanent production smoke with an E4-specific stale-release fingerprint.

Production closeout:
- final E4 validation run `34148557108` passed build, desktop/mobile geometry Vision behavior, same-state Vision switching, Compare image regression, and the full local production smoke; validation artifact `10028600514` was uploaded;
- rendered validation confirmed Tunnel edge-dominance (`centerDelta=0.00001`, `edgeDelta=21.158`), Central center-dominance (`centerDelta=53.588`, `edgeDelta=0.00001`), stronger Night response in dark regions (`darkRelativeDelta=1.190` vs `brightRelativeDelta=0.199`), and local Cataract bright-source glare spread (`nearGain=38.976` vs `farGain=29.290`);
- PR #47 was squash-merged as main commit `58fbd132c24f5d182b90e8c55a096d500419b580`;
- matching main build `34148945521` passed;
- matching production smoke `34148945534` passed against `https://asseenby.pages.dev` with `productionReleaseDetected=true`, `e2SpatialReleaseDetected=true`, `e3HumanMovementDetected=true`, `e4HumanVisionDetected=true`, desktop/mobile image=true, desktop/mobile spatial=true, and `ok=true`;
- the production E4 fingerprint was detected on attempt 1 and production smoke artifact `10028717598` was uploaded.

## Step E5 — Dog observer
Status: **queued**

Add a low ground observer, initially around 0.5–0.6 m.

Acceptance:
- lower viewpoint creates materially different occlusion from Human;
- ground collision/navigation remains stable;
- `Normal` can be used at Dog height independently of Dog-like Vision;
- Dog-like Vision can be toggled without camera reset.

## Step E6 — Dog-like 3D Vision refinement
Status: **queued**

Move Dog-like detail loss toward distance/projected-angular-size behavior rather than relying only on full-screen softening.

Keep the existing scientific boundary: visible-range human-display proxy, not literal canine perception.

## Step E7 — Cat observer
Status: **queued**

Add a lower observer around 0.3 m and authored climb/perch interactions.

Initial accepted behavior may use explicit climbable/perchable targets instead of general climbing physics.

Important: this step does **not** restore Cat-like Vision.

Acceptance:
- low viewpoint materially changes scene visibility;
- at least one authored elevated Cat-reachable target works;
- Cat can use Normal vision;
- unsupported Cat-specific Vision remains absent.

## Step E8 — First Bird species selection and observer
Status: **queued / species decision required before implementation**

Select one concrete bird species suitable for the first scene. A city species such as Pigeon is a practical candidate, but the choice must be documented before release.

Implement observer flight independent of species-specific color Vision.

Acceptance:
- free-space 3D flight inside navigation/altitude bounds;
- ascend/descend controls;
- real camera-height change and parallax;
- collision with major geometry;
- authored landing/perch targets;
- useful flight altitude roughly 30–50 m for Night Intersection;
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

Add dense scenes one at a time after Night Intersection architecture is stable.

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
- Scene density and explanatory value matter more than map size.
- Prefer a strong 100–200 m scene over a sparse 1 km world.
- Observer and Vision remain independent concepts.
- Bird movement uses the air/vertical space; species vision is a separate evidence problem.
- Cat observer movement does not resurrect the rejected Cat-like visual filter.
- UV/spectral perception is never fabricated from ordinary RGB.
- Every completed step requires build, browser regression, rendered review where visual behavior matters, and production verification when merged.
- If the user changes an accepted product behavior, update `docs/explore-3d-spec.md` and this schedule in the same implementation branch/PR before declaring the step complete.
