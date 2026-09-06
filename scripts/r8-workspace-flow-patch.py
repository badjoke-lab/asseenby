from pathlib import Path

# Reflow the image workspace so the primary content is independent of the taller
# sticky evidence rail on desktop, while preserving the existing mobile order.
app_path = Path('src/App.tsx')
app = app_path.read_text()
start_marker = '          <section id="workspace" className="workspace-grid">'
end_marker = '        </main>'
start = app.index(start_marker)
end = app.index(end_marker, start)
replacement = '''          <section id="workspace" className="workspace-grid">
            <div className="workspace-primary">
              <CompareStage
                originalUrl={imageSrc}
                transformedUrl={transformedUrl}
                compareMode={compareMode}
                setCompareMode={setCompareMode}
                divider={divider}
                setDivider={setDivider}
                isBusy={renderPending}
                currentMode={currentMode}
                currentModeEvidence={currentModeEvidence}
              />

              <section id="modes" className="category-grid">
                <CategoryPanel title="Human" subtitle="Visual conditions and perceptual differences." items={humanModes.map((mode) => mode.label)} icon={<EyeSketch className="mini-plate" />} onClick={() => setCategory("Human")} />
                <CategoryPanel title="Animal" subtitle="Animal-inspired comparison profiles." items={animalModes.map((mode) => mode.label)} icon={<BirdSketch className="mini-plate" />} onClick={() => setCategory("Animal")} />
              </section>

              <footer className="footer-strip">
                <div className="footer-line" />
                <p>Approximations only. See the mode notes and evidence panel for methodology and limitations.</p>
                <div className="footer-line" />
              </footer>
            </div>

            <ControlRail
              category={category}
              setCategory={setCategory}
              categoryModes={categoryModes}
              modeKey={modeKey}
              setModeKey={setModeKey}
              strength={strength}
              setStrength={setStrength}
              currentMode={currentMode}
              onUploadClick={() => fileInputRef.current?.click()}
              onUseSample={() => {
                if (uploadedObjectUrlRef.current) {
                  URL.revokeObjectURL(uploadedObjectUrlRef.current);
                  uploadedObjectUrlRef.current = null;
                }
                baseCanvasRef.current = null;
                setImageSrc(SAMPLE_IMAGE);
              }}
              error={error}
              currentModeEvidence={currentModeEvidence}
            />
          </section>

'''
app = app[:start] + replacement + app[end:]
app_path.write_text(app)

styles_path = Path('src/styles.css')
styles = styles_path.read_text()
workspace_anchor = '''.workspace-grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 16px;
  align-items: start;
}
'''
workspace_replacement = workspace_anchor + '''
.workspace-primary {
  min-width: 0;
}
'''
if workspace_anchor not in styles:
    raise SystemExit('workspace CSS anchor not found')
styles = styles.replace(workspace_anchor, workspace_replacement, 1)
styles = styles.replace('grid-template-columns: repeat(3, minmax(0, 1fr));', 'grid-template-columns: repeat(2, minmax(0, 1fr));', 1)
mobile_anchor = '''  .hero-grid,
  .workspace-grid,
  .category-grid,
  .support-grid {
    grid-template-columns: 1fr;
  }
'''
mobile_replacement = mobile_anchor + '''

  .workspace-primary {
    display: contents;
  }

  .workspace-grid .compare-card {
    order: 1;
  }

  .workspace-grid > .control-rail {
    order: 2;
  }

  .workspace-grid .category-grid {
    order: 3;
  }

  .workspace-grid .footer-strip {
    order: 4;
  }
'''
if mobile_anchor not in styles:
    raise SystemExit('mobile CSS anchor not found')
styles = styles.replace(mobile_anchor, mobile_replacement, 1)
styles_path.write_text(styles)

# Add regression checks for the desktop dead-space defect and the mobile order.
smoke_path = Path('.github/production-smoke.mjs')
smoke = smoke_path.read_text()
desktop_anchor = '  await noHorizontalOverflow(page, "desktop image");\n\n  const initialResources = await page.evaluate(() => performance.getEntriesByType("resource").map((entry) => entry.name));'
desktop_replacement = '''  await noHorizontalOverflow(page, "desktop image");
  const compareBox = await page.locator(".compare-card").boundingBox();
  const categoryGridBox = await page.locator("#modes").boundingBox();
  assert(compareBox && categoryGridBox, "desktop image: workspace geometry is unavailable");
  const workspaceGap = categoryGridBox.y - (compareBox.y + compareBox.height);
  assert(workspaceGap >= 0 && workspaceGap <= 48, `desktop image: category cards are pushed too far below compare stage (${workspaceGap}px)`);
  const categoryCards = page.locator("#modes .category-card");
  assert((await categoryCards.count()) === 2, "desktop image: expected exactly Human and Animal category cards");
  const lastCategoryBox = await categoryCards.nth(1).boundingBox();
  assert(lastCategoryBox, "desktop image: Animal category card has no bounding box");
  assert(Math.abs((lastCategoryBox.x + lastCategoryBox.width) - (categoryGridBox.x + categoryGridBox.width)) <= 3, "desktop image: two-category grid leaves an unused desktop column");

  const initialResources = await page.evaluate(() => performance.getEntriesByType("resource").map((entry) => entry.name));'''
if desktop_anchor not in smoke:
    raise SystemExit('desktop smoke anchor not found')
smoke = smoke.replace(desktop_anchor, desktop_replacement, 1)
mobile_anchor = '  await noHorizontalOverflow(page, "mobile image");\n  await page.getByRole("button", { name: "Side by side" }).click();'
mobile_replacement = '''  await noHorizontalOverflow(page, "mobile image");
  const mobileCompareBox = await page.locator(".compare-card").boundingBox();
  const mobileControlBox = await page.locator(".control-rail").boundingBox();
  const mobileCategoryBox = await page.locator("#modes").boundingBox();
  assert(mobileCompareBox && mobileControlBox && mobileCategoryBox, "mobile image: workspace geometry is unavailable");
  assert(mobileCompareBox.y < mobileControlBox.y && mobileControlBox.y < mobileCategoryBox.y, "mobile image: expected compare -> controls -> categories order");
  await page.getByRole("button", { name: "Side by side" }).click();'''
if mobile_anchor not in smoke:
    raise SystemExit('mobile smoke anchor not found')
smoke = smoke.replace(mobile_anchor, mobile_replacement, 1)
smoke_path.write_text(smoke)

# Close R8-2 and start R8-3 in the release schedule.
schedule_path = Path('docs/release-polish-schedule.md')
schedule = schedule_path.read_text()
schedule = schedule.replace(
    'Status: **Step R8 active / R8-1 production verified / R8-2 implementation**',
    'Status: **Step R8 active / R8-2 production verified / R8-3 implementation**',
    1,
)
schedule = schedule.replace(
    '### R8-2 — Spatial header duplicate image navigation\nStatus: **ACTIVE — implementation**',
    '### R8-2 — Spatial header duplicate image navigation\nStatus: **PASS / production verified**',
    1,
)
old_tail = '''## Current next action
Run the patched full browser smoke at desktop/390px, open a clean R8-2 PR only if it passes, then require main build and production smoke after merge.'''
new_tail = '''Validation:
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
Run build + full desktop/390px image/spatial browser smoke, inspect captures, then open a clean R8-3 PR only if the workspace flow is improved without mobile regression.'''
if old_tail not in schedule:
    raise SystemExit('R8-2 schedule tail not found')
schedule = schedule.replace(old_tail, new_tail, 1)
schedule_path.write_text(schedule)
