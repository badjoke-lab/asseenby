# AsSeenBy — Spatial Pilot Schedule

## Current state
Branch: `feat/spatial-central-loss`
PR: `#3` — **draft / blocked on scene quality review**

The existing public product remains the v0.1 static-image comparison tool. The accepted Three.js renderer baseline contains Normal, Tunnel Vision, and Cataract-like on one controlled night-street scene.

Main baseline before this expansion:
- initial spatial pilot PR #2 merged at `d3673db84864e5441951cac3be51dd01cf77602e`;
- main post-merge build run `34000040892` passed;
- image comparison remains the default experience;
- Three.js remains a separate `Explore 3D` experience;
- accepted spatial interaction is fixed-position pointer/touch/keyboard look-around;
- mode changes preserve camera position and direction;
- spatial evidence / Model notes remain renderer-specific.

## Execution rule
At the start of every future spatial step, implementation work must re-read:
- `AGENTS.md`;
- `docs/spatial-pilot-spec.md`;
- this schedule;
- the relevant methodology / limitation / evidence documents for the active mode.

A step is not complete until its acceptance condition is satisfied. Update this file whenever scope, status, claim boundaries, or rendered-review quality changes.

## Steps 0–8 — Initial spatial renderer pilot
Status: **complete / merged**

What was proven:
- isolated Three.js integration;
- controlled night-street renderer;
- Normal / Tunnel Vision / Cataract-like switching;
- fixed-position look-around;
- desktop and mobile interaction;
- evidence / limitations integration;
- 2D image regression coverage;
- scene-dependent glare and view-relative field-loss behavior.

Important correction after later visual review:
- the pilot established functional viability, but the primitive scene itself is **not** now considered an acceptable public presentation baseline;
- later user-visible review exposed the environment as sparse placeholder-like geometry;
- therefore all further spatial expansion is blocked until the scene-presentation gate below passes.

## Step 9 — Central Loss definition and evidence boundary
Status: **complete**

Defined behavior:
- `Central Loss` is the only new spatial mode in this phase;
- same controlled street and same camera state are used for comparison;
- central impairment is screen/view-relative;
- surrounding scene remains more available than the center;
- direct fixation makes a target harder to inspect;
- turning the view moves a different world-space target into the affected center;
- generic scotoma-style model only, not patient perimetry reconstruction;
- spatial Model confidence starts at C.

## Step 10 — Central Loss live renderer implementation
Status: **functionally complete, not accepted**

Implemented:
- Central Loss mode union/UI;
- live view-relative post-processing pass;
- localized softness / desaturation / contrast reduction / partial obscuration;
- same-camera switching;
- renderer-specific evidence metadata;
- browser acceptance coverage.

Functional validation already passed:
- renderer patch workflow `34000391905` — success;
- PR build `34000459038` — success;
- Chromium browser validation `34000441484` — success;
- desktop and 390px mobile mode switching and view-relative behavior worked.

Why this is still blocked:
- user-visible screenshot review showed that the environment itself still reads as a crude prototype: bare dark building boxes, simplistic car geometry, mannequin-like pedestrian, sparse surface detail, and weak street composition;
- function correctness does not override presentation failure.

## Step 10A — Rebuild the night-street scene to presentation quality
Status: **implementation complete / rendered review pending / blocking**

Scene rebuild commit: `1ffd3dcfdfcf6497ae2059f42c354974350c1100`.
Patch/build workflow `34006118735` passed, including `npm ci` and `npm run build`.

Implemented rework:
- facade layers with repeated lit/unlit windows, entrances, trim, storefront framing, awning, signage, and door detail;
- road roughness/metalness changes plus patches, wet-looking areas, manhole, drainage grates, lane/crosswalk material improvement;
- curb edges and repeated sidewalk seams;
- vehicle rebuilt with body/cabin/windshield/rear glass/wheels/rims/bumper and directional headlights;
- secondary parked vehicle;
- pedestrian expanded into head/hair/shoulders/arms/legs/shoes rather than a capsule/box mannequin;
- streetlight arms and fixtures plus improved traffic-signal housings;
- bollards, utility cabinet, hydrant, planter, overhead utility wires;
- denser near/mid/far building layers and distant windows/lights;
- improved ambient/fill/night-light hierarchy while retaining bright/dark comparison zones.

Acceptance questions still require rendered review:
1. Does Normal mode immediately read as a believable night street rather than black boxes in a corridor?
2. Are vehicle, pedestrian, storefront, road, sidewalk, signal, and light sources recognizable without explanation?
3. Does looking left/right reveal additional useful visual structure rather than empty walls?
4. Do bright/dark zones remain useful for Cataract-like and field-loss comparison?
5. Does desktop remain responsive and does 390px mobile remain usable?
6. Does the existing build/browser regression remain green on the rebuilt-scene head?

All six must pass before Central Loss acceptance resumes.

## Step 11 — Central Loss rendered acceptance gate
Status: **blocked by Step 10A rendered review**

After the rebuilt scene passes its own quality gate, rerun:
- existing 2D image comparison desktop/mobile regression;
- Normal / Tunnel Vision / Cataract-like regression;
- Normal vs Central Loss same-camera forward comparison;
- turned-view Normal vs Central Loss comparison;
- real mobile touch look-around before Central Loss capture;
- no horizontal overflow;
- no page/console errors;
- build.

Rendered-review questions:
1. Does straight-ahead detail become clearly harder to inspect while the surrounding scene remains useful?
2. When the camera turns, does the disrupted region remain centered in the viewer's field rather than staying on the previous world location?
3. Does active scanning make the consequence of central field loss clearer than another transformed still image?
4. Is the effect restrained enough to remain a generic educational simulation?
5. Is the underlying scene itself now presentation-quality?

Pass requires all five answers to be yes plus the browser/build checks above.

If pass:
- mark Central Loss accepted;
- mark PR #3 ready;
- merge cleanly;
- only then begin `Night / Low Light`.

If fail:
- correct or reject the active implementation;
- do not begin Night / Low Light.

## Ordered next spatial candidates after Central Loss
1. Night / Low Light;
2. Dog-like;
3. Cat-like;
4. Bird-like as a separate evaluation;
5. Bee-like only with additional UV-reflectance scene data.

## Current next action
Run desktop and 390px Chromium capture on the rebuilt-scene head, inspect Normal / turned / perception-mode screenshots, and reject or accept Step 10A on visual quality before touching the next perception mode.
