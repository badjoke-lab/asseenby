# AsSeenBy — Spatial Pilot Schedule

## Current state
Branch: `feat/spatial-central-loss`

The existing public product remains the v0.1 static-image comparison tool. The accepted Three.js spatial baseline contains Normal, Tunnel Vision, and Cataract-like on one controlled night-street scene.

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

A step is not complete until its acceptance condition is satisfied. Update this file whenever scope, status, or claim boundaries change.

## Steps 0–8 — Initial spatial pilot
Status: **complete / accepted / merged**

Accepted baseline:
- controlled night-street scene;
- Normal;
- Tunnel Vision;
- Cataract-like;
- fixed-position look-around;
- desktop and mobile interaction;
- evidence / limitations integration;
- 2D image regression coverage;
- rendered acceptance review.

The initial acceptance gate passed. This permits the ordered post-pilot expansion below; it does not make later modes automatically accepted.

## Step 9 — Central Loss definition and evidence boundary
Status: **in progress**

Goal:
Define exactly what the spatial Central Loss mode demonstrates before changing renderer code.

Product behavior:
- add `Central Loss` as the only new spatial mode in this phase;
- reuse the existing controlled night-street scene;
- keep the exact same camera position and direction when switching Normal <-> Central Loss;
- keep the central impairment screen/view-relative while the user looks around;
- preserve usable peripheral information while degrading or obscuring straight-ahead detail;
- use a soft, generic central scotoma-style profile rather than implying a measured patient field;
- make direct-fixation consequences visible: a pedestrian, sign, signal, or headlight placed in the center should become harder to inspect, while moving the view changes which scene target falls inside the central-loss region.

What this produces:
A documented reason for using the interactive spatial renderer: the user can actively scan the same scene and experience that the disrupted region stays tied to straight-ahead vision rather than to one object or one pre-rendered image position.

Acceptance:
- product behavior is documented in spec / methodology / limitations / modes;
- underlying phenomenon evidence remains inherited from the existing Central Loss evidence set;
- spatial implementation confidence starts conservatively at Model C;
- no claim of patient-specific scotoma shape, size, severity, or perimetry reconstruction.

## Step 10 — Central Loss live renderer implementation
Status: **not started**

Work:
- extend the spatial mode union and UI with `Central Loss`;
- add a dedicated live post-processing pass;
- keep the central-loss region view-relative;
- degrade central detail through a combination of local softness / desaturation / obscuration while retaining surrounding scene information;
- preserve camera state when toggling among all accepted modes;
- connect Central Loss to renderer-specific evidence metadata;
- update browser validation to exercise the new mode.

What this produces:
The same street scene can be viewed as Normal, Tunnel Vision, Central Loss, or Cataract-like without camera reset.

Acceptance:
- center is materially less useful for detailed inspection;
- periphery remains substantially more usable than the center;
- the central-loss region remains in the visual center while the camera direction changes;
- no world-space object is used as the mask anchor;
- mode switching does not move or recreate the camera;
- active mode evidence / limitations are visible;
- `npm run build` passes.

## Step 11 — Central Loss rendered acceptance gate
Status: **not started**

Required browser validation:
- existing 2D image comparison still passes desktop and 390px mobile checks;
- existing Normal / Tunnel Vision / Cataract-like spatial regression still passes;
- Central Loss mode can be selected on desktop and mobile;
- same-camera Normal vs Central Loss forward screenshots are captured;
- the user then changes camera direction and same-camera Normal vs Central Loss turned screenshots are captured;
- real mobile touch look-around is exercised before a Central Loss capture;
- no horizontal overflow;
- no captured page / console errors;
- build succeeds.

Rendered-review questions:
1. Does straight-ahead detail become clearly harder to inspect while the surrounding scene remains useful?
2. When the camera turns, does the disrupted region remain centered in the viewer's field rather than staying on the previous world location?
3. Does active scanning make the consequence of central field loss clearer than another transformed still image?
4. Is the result restrained enough to remain a generic educational simulation rather than a dramatic decorative effect?

Pass requires all four rendered-review answers to be yes plus the browser/build checks above.

If pass:
- mark Central Loss accepted;
- merge the mode cleanly;
- only then begin `Night / Low Light`.

If fail:
- correct or reject the Central Loss spatial implementation;
- do not begin Night / Low Light.

## Ordered next spatial candidates after Central Loss
1. Night / Low Light;
2. Dog-like;
3. Cat-like;
4. Bird-like as a separate evaluation;
5. Bee-like only with additional UV-reflectance scene data.

## Current next action
Finish Step 9 documentation alignment, then implement Step 10 Central Loss as a live view-relative spatial pass on the existing accepted scene.
