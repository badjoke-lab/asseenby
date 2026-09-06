# AsSeenBy — Release / Polish Schedule

## Current state
Status: **Step R6 production smoke PASS / current public release verified**

Current main includes:
- accepted image comparison baseline;
- accepted spatial baseline and resolved generic animal spatial evaluation;
- image control accessibility polish;
- lazy-loaded spatial JavaScript and CSS;
- cached/debounced/blob-based image render pipeline;
- synchronized pending/render state for Strength and upload/sample source switching;
- repeatable production browser smoke coverage against the public Pages URL.

Latest merged release-polish PRs:
- PR #9 — image control accessibility polish;
- PR #10 — lazy-load Three.js spatial JavaScript;
- PR #11 — lazy-load spatial CSS;
- PR #12 — optimize image render pipeline;
- PR #13 — clarify image render state.

## Execution rule
At the start of every release/polish step, re-read `AGENTS.md`, `docs/roadmap.md`, this schedule, and any feature-specific spec affected by the change. If a step touches spatial behavior, also re-read `docs/spatial-pilot-spec.md` and `docs/spatial-pilot-schedule.md`.

Do not call a release step complete from local/preview build success alone when the step is explicitly a production verification step.

## Step R1 — Image control accessibility
Status: **PASS / merged**

- form controls have explicit label associations;
- compare mode buttons expose pressed state;
- keyboard focus behavior was validated with real Tab navigation;
- existing spatial behavior remained regression-covered.

## Step R2 — Spatial JavaScript lazy loading
Status: **PASS / merged**

- Three.js/spatial code moved behind the spatial route boundary;
- initial image-page JavaScript dropped from roughly 756 kB to roughly 206 kB minified;
- spatial JavaScript remains a separate roughly 551 kB lazy chunk;
- desktop and 390px spatial regression passed.

## Step R3 — Spatial CSS lazy loading
Status: **PASS / merged**

- spatial-only CSS moved behind the same lazy route boundary;
- initial shared CSS dropped from 15.49 kB to 12.00 kB minified;
- 3.49 kB spatial-only CSS loads only with the spatial experience;
- desktop and 390px spatial regression passed.

## Step R4 — Image render pipeline
Status: **PASS / merged**

- decoded/resized base image is cached across mode/Strength changes;
- rapid Strength changes are coalesced with a short debounce;
- transformed output uses async `toBlob()` plus object URLs instead of synchronous data URLs;
- uploaded originals use object URLs instead of FileReader/base64;
- generated/upload object URLs are revoked when replaced or unmounted;
- image and full spatial browser regression passed.

## Step R5 — Image render-state synchronization
Status: **PASS / merged**

- Original renders directly from the active source rather than duplicate state;
- upload/sample switching updates Original immediately;
- debounce time is represented as pending render state rather than falsely showing completion;
- image and full spatial browser regression passed.

## Step R6 — Production smoke
Status: **PASS / production verified**

Target:
- `https://asseenby.pages.dev/`
- `https://asseenby.pages.dev/?view=spatial`

Acceptance requirements and result:
1. Production root renders the current image experience — **PASS**.
2. `Explore 3D` renders the accepted photographic panorama rather than the discarded primitive scene — **PASS**.
3. Desktop image compare mode, Strength, sample, and upload paths — **PASS**.
4. 390px image layout without horizontal overflow — **PASS**.
5. Desktop spatial controls for Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like — **PASS**.
6. Spatial desktop look-around with no page/console errors — **PASS**.
7. 390px spatial route and actual touch look-around — **PASS**.
8. Cat-like, Bird-like, and Bee-like spatial controls remain absent — **PASS**.
9. No uncaught page error or meaningful console error during the smoke path — **PASS**.
10. Matching main build green — **PASS**.

Production smoke run `34015593874` passed. The matching main build run `34015593899` also passed. The smoke detected current blob-upload behavior on the first production attempt, so this was not a pass against a stale pre-PR-12 deployment.

The first smoke run `34015498797` was a test-harness failure, not a product failure: it tried to observe a transient 90 ms `aria-busy=true` window. The harness was corrected to verify the user-visible outcome (a newly rendered blob output that settles back to idle), then R6 passed.

## Step R7 — Image transform / evidence quality audit
Status: **ACTIVE**

Purpose: review currently public image modes whose implementation confidence is weak or conservative and decide mode-by-mode whether to keep, revise, narrow, or remove them. A visually different output is not enough; each public transform must have useful explanatory value within its evidence/model boundary.

Priority order:
1. Model D public modes and placeholders;
2. Model C modes where current transform behavior may overstate the evidence;
3. animal modes whose RGB-only limitation needs stronger UI handling;
4. reference profiles that risk implying population-wide truths.

Do not strengthen a transform merely to make it look more dramatic. Prefer removal or narrower labeling when the current source data cannot support a stronger model.

### R7-1 — Sex-difference Profile
Decision: **REMOVE from the product**

Reason:
- Evidence score was C and Model score was D;
- the evidence set explicitly described reported differences as small, task-specific, heterogeneous, and insufficient for one broad perceptual profile;
- the implementation was only a tiny saturation/microcontrast adjustment and was explicitly described as a placeholder framing tool;
- making the transform stronger would create unsupported sex-wide visual claims rather than improve explanatory accuracy.

Removal scope:
- remove the public mode definition;
- remove the image transform branch;
- remove the mode-specific Evidence metadata;
- remove the mode from README and mode documentation;
- keep the product-level statement that reference profiles are averaged and non-individual for the remaining Age Profile.

Acceptance:
- Reference category exposes Age Profile only;
- no `sex` transform or Sex-difference Evidence entry remains;
- existing Human / Animal image modes remain selectable;
- accepted spatial modes remain unchanged;
- build and browser regression pass.

## Current next action
Complete R7-1 removal and validation. Then audit the remaining public Model D animal image modes in this order: Bee-like, Bird-like.
