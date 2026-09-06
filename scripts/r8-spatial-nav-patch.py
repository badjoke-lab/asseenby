from pathlib import Path

# 1) Remove the duplicate spatial back link. The existing Compare image nav item
# remains the single route back to the image experience.
spatial_path = Path("src/SpatialPage.tsx")
spatial = spatial_path.read_text()
duplicate = '          <a href="/" className="ghost-button">Back to image</a>\n'
if duplicate not in spatial:
    raise SystemExit("duplicate Back to image link not found")
spatial = spatial.replace(duplicate, "", 1)
spatial_path.write_text(spatial)

# 2) Make the no-duplicate-navigation rule part of production smoke.
smoke_path = Path(".github/production-smoke.mjs")
smoke = smoke_path.read_text()
desktop_marker = '  await noHorizontalOverflow(page, "desktop spatial");\n\n  const modeGroup = page.getByRole("group", { name: "Spatial perception mode" });'
desktop_replacement = '''  await noHorizontalOverflow(page, "desktop spatial");
  const spatialNav = page.getByRole("navigation", { name: "Spatial navigation" });
  assert((await spatialNav.getByRole("link", { name: "Compare image", exact: true }).count()) === 1, "desktop spatial: Compare image navigation is missing or duplicated");
  assert((await page.getByRole("link", { name: "Back to image", exact: true }).count()) === 0, "desktop spatial: duplicate Back to image action is still exposed");

  const modeGroup = page.getByRole("group", { name: "Spatial perception mode" });'''
if desktop_marker not in smoke:
    raise SystemExit("desktop spatial smoke marker not found")
smoke = smoke.replace(desktop_marker, desktop_replacement, 1)

mobile_marker = '  await noHorizontalOverflow(page, "mobile spatial");\n  const group = page.getByRole("group", { name: "Spatial perception mode" });'
mobile_replacement = '''  await noHorizontalOverflow(page, "mobile spatial");
  const spatialNav = page.getByRole("navigation", { name: "Spatial navigation" });
  assert((await spatialNav.getByRole("link", { name: "Compare image", exact: true }).count()) === 1, "mobile spatial: Compare image navigation is missing or duplicated");
  assert((await page.getByRole("link", { name: "Back to image", exact: true }).count()) === 0, "mobile spatial: duplicate Back to image action is still exposed");
  const group = page.getByRole("group", { name: "Spatial perception mode" });'''
if mobile_marker not in smoke:
    raise SystemExit("mobile spatial smoke marker not found")
smoke = smoke.replace(mobile_marker, mobile_replacement, 1)
smoke_path.write_text(smoke)

# 3) Record R8-1 production acceptance and start R8-2.
schedule_path = Path("docs/release-polish-schedule.md")
schedule = schedule_path.read_text()
schedule = schedule.replace(
    "Status: **Step R8 active / R7 complete / R8-1 browser validated**",
    "Status: **Step R8 active / R8-1 production verified / R8-2 implementation**",
    1,
)
schedule = schedule.replace(
    "### R8-1 — Image experience switch presentation\nStatus: **ACTIVE — browser validated**",
    "### R8-1 — Image experience switch presentation\nStatus: **PASS / production verified**",
    1,
)
schedule = schedule.replace(
    "- production smoke after merge remains required before R8-1 is marked complete.",
    "- production smoke after merge remains green — **PASS**.",
    1,
)
old_end = '''Validation before PR:
- R8-1 build + Chromium desktop/390px switch check `34041365365` — **success**;
- screenshot review confirmed the raw text defect is replaced by a compact styled control on both desktop and mobile.

## Current next action
Open the clean R8-1 PR, merge only if the normal PR build is green, then require main build and a fresh production smoke screenshot before marking R8-1 PASS.'''
new_end = '''Validation:
- R8-1 build + Chromium desktop/390px switch check `34041365365` — **success**;
- screenshot review confirmed the raw text defect is replaced by a compact styled control on both desktop and mobile;
- PR #22 build `34041588585` — **success**;
- merge SHA `fbb966a8977cd996df4fff9d9b5a22fb6448a7dd`;
- matching main build `34041626114` — **success**;
- production smoke `34041626119` — **success**;
- production artifact `9991858538` was manually reviewed: desktop/mobile image captures retain the styled experience switch with no raw-text regression, and image/spatial smoke result is fully green.

### R8-2 — Spatial header duplicate image navigation
Status: **ACTIVE — implementation**

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

## Current next action
Run the patched full browser smoke at desktop/390px, open a clean R8-2 PR only if it passes, then require main build and production smoke after merge.'''
if old_end not in schedule:
    raise SystemExit("R8-1 schedule tail not found")
schedule = schedule.replace(old_end, new_end, 1)
schedule_path.write_text(schedule)
