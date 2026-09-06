from pathlib import Path

path = Path("docs/release-polish-schedule.md")
text = path.read_text()

replacements = [
    (
        "Status: **Step R7 active / R7-2 production verified / R7-3 branch validated**",
        "Status: **Step R8 active / R7 complete / R8-1 browser validated**",
    ),
    (
        "## Step R7 — Image transform / evidence quality audit\nStatus: **ACTIVE**",
        "## Step R7 — Image transform / evidence quality audit\nStatus: **PASS / complete / production verified**",
    ),
    (
        "### R7-9 — Age Profile / Reference category\nStatus: **ACTIVE — removal implementation**",
        "### R7-9 — Age Profile / Reference category\nStatus: **PASS / removed / production verified**",
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f"missing schedule marker: {old}")
    text = text.replace(old, new, 1)

old_tail = """## Current next action
Apply R7-9 removal, run the patched production smoke against a local build at desktop/390px plus the accepted spatial controls, then open a PR only if the two-category release is clean."""

new_tail = """Validation:
- local Age/Reference removal + build + desktop/390px image and accepted-spatial smoke workflow `34035694131` — **success**;
- PR #21 build `34040582076` — **success**;
- merge SHA `4da5328f9e48b5b630d13a8951926241ca5e22f7`;
- matching main build `34040615102` — **success**;
- production smoke `34040615208` — **success**, confirming the image experience exposes exactly Human + Animal while the accepted six spatial controls remain unchanged.

## Step R8 — Public surface / responsive polish
Status: **ACTIVE**

Purpose: inspect accepted production captures as a user-facing surface and fix concrete presentation or responsive defects without changing the scientific model or spatial source-data boundary.

### R8-1 — Image experience switch presentation
Status: **ACTIVE — browser validated**

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
- production smoke after merge remains required before R8-1 is marked complete.

Validation before PR:
- R8-1 build + Chromium desktop/390px switch check `34041365365` — **success**;
- screenshot review confirmed the raw text defect is replaced by a compact styled control on both desktop and mobile.

## Current next action
Open the clean R8-1 PR, merge only if the normal PR build is green, then require main build and a fresh production smoke screenshot before marking R8-1 PASS."""

if old_tail not in text:
    raise SystemExit("missing old current-next-action block")
text = text.replace(old_tail, new_tail, 1)
path.write_text(text)
