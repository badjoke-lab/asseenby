# AsSeenBy — Release / Polish Schedule

## Current state
Status: **production smoke pending on current main**

Current main includes:
- accepted image comparison baseline;
- accepted spatial baseline and resolved generic animal spatial evaluation;
- image control accessibility polish;
- lazy-loaded spatial JavaScript and CSS;
- cached/debounced/blob-based image render pipeline;
- synchronized pending/render state for Strength and upload/sample source switching.

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
Status: **ACTIVE**

Target:
- `https://asseenby.pages.dev/`
- `https://asseenby.pages.dev/?view=spatial`

Acceptance requirements:
1. Production root returns and renders the current image experience.
2. `Explore 3D` production route renders the accepted panorama rather than the discarded primitive scene.
3. Desktop image controls work: compare mode, Strength, sample, and upload.
4. 390px image layout has no horizontal overflow and remains operable.
5. Desktop spatial controls work for Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like.
6. Spatial look-around works without page/console errors.
7. 390px spatial route remains usable and touch interaction changes view direction.
8. Production does not expose Cat-like, Bird-like, or Bee-like spatial controls.
9. No uncaught page error or meaningful console error occurs during the smoke path.
10. Current main build is green.

If production is stale relative to main, record that as a deployment-state failure rather than treating preview success as production success.

## Current next action
Run Step R6 against the public production URL, record the exact result, then either:
- mark R6 PASS and close the current release-polish cycle; or
- open the smallest corrective PR for the observed production failure and repeat R6 after deployment.
