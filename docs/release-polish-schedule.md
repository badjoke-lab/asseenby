# AsSeenBy — Release / Polish Schedule

## Current state
Status: **Step R8 active / R8-2 production verified / R8-3 implementation**

Current main includes:
- accepted image comparison baseline;
- accepted spatial baseline and resolved generic animal spatial evaluation;
- image control accessibility polish;
- lazy-loaded spatial JavaScript and CSS;
- cached/debounced/blob-based image render pipeline;
- synchronized pending/render state for Strength and upload/sample source switching;
- repeatable production browser smoke coverage against the public Pages URL;
- unsupported Sex-difference Profile and Bee-like image modes removed from the public product.

Latest merged release-polish PRs:
- PR #9 — image control accessibility polish;
- PR #10 — lazy-load Three.js spatial JavaScript;
- PR #11 — lazy-load spatial CSS;
- PR #12 — optimize image render pipeline;
- PR #13 — clarify image render state;
- PR #14 — remove unsupported Bee-like image mode.

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
Status: **PASS / complete / production verified**

Purpose: review currently public image modes whose implementation confidence is weak or conservative and decide mode-by-mode whether to keep, revise, narrow, or remove them. A visually different output is not enough; each public transform must have useful explanatory value within its evidence/model boundary.

Priority order:
1. Model D public modes and placeholders;
2. Model C modes where current transform behavior may overstate the evidence;
3. animal modes whose RGB-only limitation needs stronger UI handling;
4. reference profiles that risk implying population-wide truths.

Do not strengthen a transform merely to make it look more dramatic. Prefer removal or narrower labeling when the current source data cannot support a stronger model.

### R7-1 — Sex-difference Profile
Status: **PASS / removed / production verified**

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

Validation:
- removal/build/full local browser regression workflow `34015800962` — **success**;
- production smoke `34015953222` — **success**, detected Reference = Age Profile only on attempt 1;
- matching main build `34015953216` — **success**.

### R7-2 — Bee-like image mode
Status: **PASS / removed / production verified**

Decision: **REMOVE from the public image product until UV/spectral source data exists**

Reason:
- honeybee UV/blue/green color vision is well supported, so the phenomenon Evidence remains strong;
- the former image implementation was Model D because a conventional RGB image has already discarded ultraviolet/spectral information;
- the public transform only remapped visible RGB channels and could not reconstruct UV response, nectar-guide structure, receptor catches, or bee-specific scene coding;
- strengthening the RGB color shift would have made the output more dramatic without making it more biologically defensible;
- the spatial Bee-like gate is blocked for the same missing-source-data reason, so keeping a weaker image-only pseudo-bee view would be inconsistent.

Removal scope:
- remove Bee-like from the public Animal mode list;
- remove the arbitrary RGB bee transform branch;
- remove the public Bee-specific Evidence entry;
- update README, MVP/mode documentation, and limitations to state Bee-like is unavailable until a spectral/UV data path exists;
- keep the scientific/source-data decision in this schedule and spatial documentation.

Validation:
- removal/build/local desktop + 390px + spatial regression workflow `34016158829` — **success**;
- PR #14 clean-head build `34016314919` — **success**;
- merge SHA `ce71b1f49c3fb15e6d382a3fa02fba938bd5651a`;
- matching main build `34016338118` — **success**;
- production smoke `34016338172` — **success**, confirming Animal image modes reached Dog-like / Cat-like / Bird-like with Bee-like absent.

### R7-3 — Bird-like image mode
Status: **PASS / removed / production verified**

Decision: **REMOVE the generic Bird-like image mode**

Reason:
- avian vision itself has strong evidence, but a generic “bird” observer is not a coherent single model across species;
- many birds use four single-cone classes with UVS or VS tuning and oil-droplet filtering, none of which can be reconstructed from ordinary three-channel RGB after capture;
- measured avian visual acuity varies by roughly two orders of magnitude across species, so a generic sharpen/blur rule would also overclaim;
- the former Model D transform only increased visible-range saturation and microcontrast;
- the spatial Bird-like candidate was already rejected/blocked at the evidence/source-data gate, so retaining a weaker 2D generic-bird filter is inconsistent.

Removal scope:
- remove Bird-like from the public Animal image list;
- remove the saturation/microcontrast Bird transform and now-unused helpers;
- remove the public Bird-specific Evidence entry;
- update README, MVP/mode docs, limitations, and roadmap wording;
- strengthen production smoke so the accepted public Animal image set is Dog-like / Cat-like only;
- keep the scientific Bird-like rejection/source-data decision documented for future species-specific work.

Acceptance:
- Animal image category exposes Dog-like and Cat-like only;
- no `bird` image transform or Bird-like public Evidence entry remains;
- Reference remains Age Profile only;
- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;
- desktop and 390px browser checks pass without horizontal overflow or page/console errors;
- build passes;
- after merge, production smoke confirms Bird-like is absent from the public image UI.

Validation so far:
- corrected removal/build/browser workflow `34018426974` — **success**;
- typecheck + production build — **success**;
- 1440px and 390px image checks: Animal = Dog-like / Cat-like only, Reference = Age Profile only, no overflow or page/console errors — **success**;
- 1440px and 390px spatial control regression — **success**;
- earlier runs `34018291841` and `34018339466` were workflow/test-harness failures before product commit: invalid workflow formatting, then Playwright module resolution from `/tmp`; neither was a product-code failure.

### R7-4 — Cat-like image mode
Status: **PASS / removed / production verified**

Decision: **REMOVE the public Cat-like image mode**

Reason:
- domestic-cat behavioral work supports a dichromatic tendency, but it does not validate the former Cat-specific hand-tuned RGB matrix used by AsSeenBy;
- the existing image renderer differed from Dog-like through a different ad-hoc 3×3 RGB remap, extra desaturation, and the same blur family rather than a feline cone-catch or observer model;
- spatial Cat-like had already been rejected because its rendered distinction from Dog-like was not explanatory enough to justify a separate species claim;
- corrected image-output audit `34019040004` reached the same conclusion on the 2D renderer.

Output-audit result (`34019040004`):
- built-in sample, Dog vs Cat mean absolute channel delta at Strength 40 / 70 / 100: **3.10 / 4.65 / 6.16**;
- built-in sample, pixels with any channel delta >=25 between Dog and Cat: **0% at all three strengths**; maximum channel delta only **13 / 15 / 18**;
- controlled color/detail chart, Dog vs Cat mean delta: **5.14 / 6.49 / 8.84**;
- controlled chart, pixels with any channel delta >=25: **0.0028% / 0.0013% / 0.0011%**;
- each mode's change from Original was materially larger than the Dog-versus-Cat separation, so the distinct Cat control mainly communicated a small renderer-specific RGB tuning difference.

Removal scope:
- remove Cat-like from the public Animal image list;
- remove the Cat image transform and Cat-specific public Evidence entry;
- narrow the shared post-transform blur path to Dog-like only;
- update README, MVP/mode docs, limitations, and roadmap wording;
- change production smoke so the complete accepted Animal image set is Dog-like only;
- keep feline evidence and the rejection rationale documented as a future-model requirement rather than a public transform.

Acceptance:
- Animal image category exposes Dog-like only;
- no `cat` image transform or Cat-like public Evidence entry remains;
- Reference remains Age Profile only;
- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;
- desktop and 390px browser checks pass without overflow or page/console errors;
- build passes;
- after merge, production smoke confirms Cat-like is absent and Dog-like is the only public Animal image mode.

Validation:
- corrected Cat-like image-output audit `34019040004` — **success**;
- removal/build/desktop + 390px + spatial regression `34025906254` — **success**;
- PR #16 build `34025986307` — **success**;
- merge SHA `9b12e4d855f9e4b3be388812a43ba1e5e0990f04`;
- matching main build `34026021415` — **success**;
- production smoke `34026021476` — **success**, confirming Dog-like is the only public Animal image mode while Reference remains Age Profile and the accepted six spatial controls remain unchanged.

### R7-5 — Fatigue-like image mode
Status: **PASS / removed / production verified**

Decision: **REMOVE the public Fatigue-like image mode**

Reason:
- digital eye strain / visual fatigue is a symptom cluster, not one stable visual phenotype shared by affected viewers;
- the current Evidence entry is B / Model C and explicitly describes the renderer as a communication proxy rather than a validated fatigue-specific visual model;
- the public transform is only a mild generic blur followed by contrast reduction;
- Blur and Low Contrast already expose those visual effects directly without implying that a particular combined output is what “fatigue” looks like;
- strengthening the mode would manufacture specificity that the current evidence does not support.

Removal scope:
- remove Fatigue-like from the public Human mode list;
- remove the fatigue transform branch and public fatigue Evidence entry;
- update README, MVP/mode documentation, and limitations;
- strengthen production smoke so the accepted Human image set explicitly excludes Fatigue-like and stale deployments cannot pass;
- keep Dry-eye-like as the next separate Model C audit rather than conflating the two symptom categories.

Acceptance:
- Human image modes are Protan-like, Deutan-like, Tritan-like, Blur, Low Contrast, Cataract-like, Tunnel Vision, Central Loss, Night / Low Light, and Dry-eye-like;
- no `fatigue` transform or Fatigue-like public Evidence entry remains;
- Animal remains Dog-like only and Reference remains Age Profile only;
- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;
- desktop and 390px image/spatial regression passes without overflow or page/console errors;
- build passes;
- after merge, production smoke must observe the exact Human set without Fatigue-like before R7-5 is marked PASS.

Validation:
- removal/build/desktop + 390px + spatial regression `34026264093` — **success**;
- PR #17 build `34026349097` — **success**;
- merge SHA `8a8b300546bbddc6fcdbaa98a56e308bc3d81b49`;
- matching main build `34026381562` — **success**;
- production smoke `34026381544` — **success**, confirming the exact Human set without Fatigue-like while Animal=Dog-like, Reference=Age Profile, and the accepted six spatial controls remained unchanged.

### R7-6 — Dry-eye-like image mode
Status: **PASS / removed / production verified**

Decision: **REMOVE the public Dry-eye-like image mode**

Reason:
- dry eye can produce blur and fluctuating clarity, but that does not establish one stable static appearance shared by affected viewers;
- the Evidence entry is B / Model C and already describes the renderer as heuristic;
- the current transform applies general blur and then draws six fixed radial bright spots at deterministic positions unrelated to measured tear-film breakup, corneal optics, or patient data;
- the static v0.1 image track cannot represent the time-varying clarity that is one of the mode's main stated phenomena;
- strengthening the fixed artifact pattern would make the output more visually distinctive without making it more scientifically defensible.

Removal scope:
- remove Dry-eye-like from the public Human mode list;
- remove the dry-eye transform branch, fixed artifact helper, and public dry-eye Evidence entry;
- update README, MVP/mode documentation, and limitations;
- strengthen production smoke so the exact Human set excludes both Fatigue-like and Dry-eye-like;
- leave Night / Low Light as the remaining Estimated Human mode for a separate audit.

Acceptance:
- Human image modes are Protan-like, Deutan-like, Tritan-like, Blur, Low Contrast, Cataract-like, Tunnel Vision, Central Loss, and Night / Low Light;
- no `dry_eye` transform, fixed dry-eye overlay helper, or Dry-eye-like public Evidence entry remains;
- Animal remains Dog-like only and Reference remains Age Profile only;
- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;
- desktop and 390px image/spatial regression passes without overflow or page/console errors;
- build passes;
- after merge, production smoke must observe the exact Human set without Dry-eye-like before R7-6 is marked PASS.

Validation:
- removal/build/desktop + 390px + spatial regression `34026610348` — **success**;
- PR #18 build `34026698193` — **success**;
- merge SHA `d408ac2c054e54772753bd2f77ff545c1debfb58`;
- matching main build `34026734382` — **success**;
- production smoke `34026734384` — **success**, confirming the exact Human image set without Dry-eye-like while Animal=Dog-like, Reference=Age Profile, and all six spatial controls remained unchanged.

### R7-7 — Night / Low Light image mode
Status: **PASS / removed / production verified**

Decision: **REMOVE the static-image Night / Low Light mode; KEEP the accepted spatial mode**

Reason:
- the image Evidence entry is B / Model C and explicitly calls the transform heuristic rather than a validated scotopic model;
- an uploaded RGB image does not establish absolute scene luminance, camera exposure/tone mapping, pupil state, or dark-adaptation state;
- the static renderer applies a global dark/desaturated color transform, so it can manufacture a low-light appearance even when the source image does not contain the information needed to define one;
- the spatial implementation is materially different: it uses live rendered relative luminance so darker regions lose more chromatic/contrast/detail information while brighter sources remain comparatively available;
- removing the image mode does not remove the shared scientific Evidence needed by `spatialEvidence.ts`.

Removal scope:
- remove Night / Low Light from the public Human image list;
- remove only the static `night` transform branch;
- retain the `night` Evidence entry because the spatial Evidence layer extends it;
- retain the spatial Night / Low Light shader and control;
- update README, MVP/mode docs, limitations, release schedule, and production smoke.

Acceptance:
- Human image modes are Protan-like, Deutan-like, Tritan-like, Blur, Low Contrast, Cataract-like, Tunnel Vision, and Central Loss;
- image `night` is not selectable and the old static transform branch is gone;
- spatial Night / Low Light remains one of the exact six accepted spatial controls and its Evidence panel still resolves;
- Animal remains Dog-like only and Reference remains Age Profile only;
- desktop and 390px image/spatial regression passes without overflow or page/console errors;
- build passes;
- after merge, production smoke must observe the exact 8-mode Human image set while still exercising the six-mode spatial set.

Validation:
- removal/build/desktop + 390px + spatial regression workflow `34026970730` — **success**;
- PR #19 build `34034654963` — **success**;
- merge SHA `b1f565feaf46251da3ad8149856ff73d69ee5569`;
- matching main build `34034680040` — **success**;
- production smoke `34034680087` — **success**, confirming image Night is absent while spatial Night remains one of the accepted six controls.

### R7-8 — Dog-like image mode
Status: **PASS / revised / browser validated**

Decision: **KEEP the public Dog-like image mode, but REVISE the renderer and narrow its model claim**

Reason:
- canine dichromatic color vision has strong behavioral and photopigment support;
- behavioral work also supports a broad similarity to human red-green color-deficiency discrimination, while canine acuity and brightness discrimination differ from typical human vision;
- the former AsSeenBy image renderer used an ad-hoc RGB matrix, which was not derived from canine cone catches or a validated observer model;
- unlike the removed Cat/Bird/Bee modes, Dog-like still has a defensible visible-range explanatory target from ordinary RGB if the implementation is kept conservative.

Revision scope:
- replace the bespoke dog RGB matrix with the existing linear-RGB red-green-deficiency mapping as a human-display proxy;
- add only restrained red-green compression, contrast reduction, and detail softening;
- remove the now-unused arbitrary RGB-deficiency helper;
- keep Evidence A but keep image Model C;
- explicitly state that the renderer is not canine cone-catch reconstruction, literal canine qualia, rod/tapetal night vision, motion processing, or breed-specific field of view.

Acceptance:
- Dog-like remains the only public Animal image mode;
- Dog-like produces a non-trivial but restrained output change that increases with Strength;
- the implementation no longer contains the bespoke dog RGB matrix/helper;
- desktop and 390px image checks pass without overflow or page/console errors;
- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;
- build passes;
- after merge, production smoke remains green with Animal=Dog-like only.

Validation before PR:
- renderer patch + typecheck/build + 1440px/390px Dog output + full spatial regression workflow `34035027559` — **success**;
- controlled color/detail chart at Strength 40: mean absolute channel delta **12.75**, maximum channel delta **79**;
- controlled color/detail chart at Strength 100: mean absolute channel delta **17.16**, maximum channel delta **89**;
- the output therefore remains non-trivial and scales with Strength without requiring a bespoke canine RGB matrix;
- manual capture review retained the mode as a restrained visible-range comparison proxy; image Model remains **C**;
- PR #20 build `34035301890` — **success**;
- merge SHA `31dbf2b50fd44fd5265639c16fa123b3c043cef7`;
- matching main build `34035329766` — **success**;
- production smoke `34035329745` — **success**, confirming Animal=Dog-like only and the accepted six spatial controls unchanged.

### R7-9 — Age Profile / Reference category
Status: **PASS / removed / production verified**

Decision: **REMOVE Age Profile and remove the now-empty public Reference category**

Reason:
- age-related contrast sensitivity, glare, optical density and focusing changes are real, but they are not one stable visual phenotype;
- chromatic adaptation can compensate substantially for progressive lens yellowing, so a fixed warm tint should not be presented as a generic older-person view;
- the current Age Profile does not specify an age, age range, ocular status, lens density, pupil state, adaptation state, or measurement source for an individual/population observer;
- the image renderer is only a broad low-contrast + warm-tint preset, so the label implies more specificity than the transform supports;
- Sex-difference Profile was already removed, so Age Profile is the only remaining Reference item and removing it eliminates an otherwise empty category.

Removal scope:
- remove `age` from public mode metadata, transform engine, and evidence registry;
- remove Reference from the public image category selector and category cards;
- update production smoke to require exactly Human + Animal image categories;
- update README/MVP/overview/UI/methodology/modes/limitations documentation;
- retain the generic `Reference` evidence-class concept for future explicitly defined datasets, but expose no current public Reference mode.

Acceptance:
- image category selector exposes exactly Human and Animal;
- Age Profile and Sex-difference Profile are absent from public UI;
- Human remains the exact audited 8-mode set;
- Animal remains Dog-like only;
- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;
- desktop and 390px image/spatial regression passes without overflow or page/console errors;
- build passes;
- after merge, production smoke observes the Human/Animal-only image release.

Validation:
- local Age/Reference removal + build + desktop/390px image and accepted-spatial smoke workflow `34035694131` — **success**;
- PR #21 build `34040582076` — **success**;
- merge SHA `4da5328f9e48b5b630d13a8951926241ca5e22f7`;
- matching main build `34040615102` — **success**;
- production smoke `34040615208` — **success**, confirming the image experience exposes exactly Human + Animal while the accepted six spatial controls remain unchanged.

## Step R8 — Public surface / responsive polish
Status: **ACTIVE**

Purpose: inspect accepted production captures as a user-facing surface and fix concrete presentation or responsive defects without changing the scientific model or spatial source-data boundary.

### R8-1 — Image experience switch presentation
Status: **PASS / production verified**

Finding:
- production smoke `34040615208` exposed `ExperienceCompare imageExplore 3D` as unstyled run-together text above the image page frame on desktop and 390px mobile;
- `ExperienceRoot.tsx` rendered the experience switch, but the image surface had no `experience-switch*` styles.

Implementation:
- add a small dedicated `experience-switch.css` imported by `ExperienceRoot.tsx`;
- present Compare image / Explore 3D as a compact editorial segmented control without altering the spatial lazy-CSS boundary;
- make the mobile links at least 44px tall.

Acceptance:
- the image/spatial switch reads as one compact editorial control rather than raw text — **PASS in branch browser review**;
- Compare image remains visibly active on the image route — **PASS**;
- both experience links are at least 44px high at 390px — **PASS**;
- no horizontal overflow at 1440px or 390px — **PASS**;
- build passes — **PASS**;
- production smoke after merge remains green — **PASS**.

Validation:
- R8-1 build + Chromium desktop/390px switch check `34041365365` — **success**;
- screenshot review confirmed the raw text defect is replaced by a compact styled control on both desktop and mobile;
- PR #22 build `34041588585` — **success**;
- merge SHA `fbb966a8977cd996df4fff9d9b5a22fb6448a7dd`;
- matching main build `34041626114` — **success**;
- production smoke `34041626119` — **success**;
- production artifact `9991858538` was manually reviewed: desktop/mobile image captures retain the styled experience switch with no raw-text regression, and image/spatial smoke result is fully green.

### R8-2 — Spatial header duplicate image navigation
Status: **PASS / production verified**

Finding:
- accepted production spatial captures expose both `Compare image` in the primary navigation and a separate `Back to image` button;
- both actions resolve to `/`, so the second control is redundant;
- on 390px mobile the redundant button consumes a full header row before the primary navigation.

Implementation:
- remove only the redundant `Back to image` ghost-button from `SpatialPage.tsx`;
- retain `Compare image`, `Explore spatial`, and `Support` in the semantic `Spatial navigation` nav;
- add production-smoke assertions that exactly one `Compare image` nav action is present and no `Back to image` action is exposed on desktop or mobile.

Acceptance:
- one clear route from spatial back to image comparison;
- no `Back to image` duplicate on desktop or 390px mobile;
- Spatial navigation remains usable and no horizontal overflow is introduced;
- all six accepted spatial modes and image workflows remain regression-green;
- build passes;
- after merge, production smoke and screenshot review confirm the cleaner header before R8-2 is marked PASS.

Validation:
- full local image + spatial browser smoke `34042685234` — **success**;
- PR #23 build `34042922365` — **success**;
- merge SHA `4d244f6f5779e326e37f0e5c74ad84678298e1e3`;
- matching main build `34042960952` — **success**;
- first production smoke attempt `34042960947` correctly failed while Pages still exposed stale `Back to image`;
- rerun of the same production smoke after deployment — **success**;
- production artifact `9992273386` was manually reviewed: desktop/mobile spatial headers expose only Compare image / Explore spatial / Support, with no duplicate Back to image action.

### R8-3 — Desktop image workspace flow after Reference removal
Status: **ACTIVE — implementation**

Finding:
- the desktop production image capture leaves a large empty area below the compare card because the taller sticky ControlRail determines the `workspace-grid` row height while the Human/Animal cards live outside that grid;
- after Reference removal, `.category-grid` still reserves three desktop columns even though only Human and Animal remain, leaving an unused third column.

Implementation:
- group CompareStage + Human/Animal cards + footer into a primary desktop column independent of the sticky ControlRail height;
- use exactly two desktop category columns;
- at <=960px use `display: contents` plus explicit ordering so the existing mobile sequence remains Compare -> controls/evidence -> Human/Animal -> footer;
- add browser-smoke geometry assertions for the desktop compare-to-category gap, two-column fill, and mobile content order.

Acceptance:
- Human/Animal cards begin within 48px of the compare card bottom on desktop;
- the two cards fill the available primary-column width with no obsolete empty third column;
- 390px order remains Compare -> controls/evidence -> category cards;
- no horizontal overflow or console/page errors;
- all existing image and six spatial mode regression paths remain green;
- production screenshot review is required after merge before R8-3 is marked PASS.

## Current next action
Run build + full desktop/390px image/spatial browser smoke, inspect captures, then open a clean R8-3 PR only if the workspace flow is improved without mobile regression.
