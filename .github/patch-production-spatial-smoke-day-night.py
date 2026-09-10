#!/usr/bin/env python3
from pathlib import Path

smoke_path = Path('.github/production-smoke.mjs')
c0_path = Path('.github/production-spatial-c0-check.mjs')
smoke = smoke_path.read_text()
c0 = c0_path.read_text()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

helper_anchor = 'async function waitForExplore3DE3(page, label) {'
helper = '''async function waitForSpatialC0(page) {
  await page.locator("canvas.spatial-canvas").waitFor({ state: "visible", timeout: 20_000 });
  await page.locator("#spatial-lighting-select").waitFor({ state: "visible", timeout: 10_000 });
  await page.waitForFunction(() => {
    const canvas = document.querySelector("canvas.spatial-canvas");
    return canvas instanceof HTMLCanvasElement
      && canvas.dataset.sceneAuthoredAssetRootCount === "1"
      && (canvas.dataset.sceneLoadedChunks ?? "").split(",").includes("c0");
  }, undefined, { timeout: 60_000 });
}

async function waitForExplore3DE3(page, label) {'''
smoke = replace_once(smoke, helper_anchor, helper, 'insert spatial C0 wait helper')

old_nav = '''    await page.goto(`${BASE}/?view=spatial&e3_release_smoke=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    await page.waitForTimeout(1_000);'''
new_nav = '''    await page.goto(`${BASE}/?view=spatial&e3_release_smoke=${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
    await waitForSpatialC0(page);
    await page.waitForTimeout(250);'''
smoke = replace_once(smoke, old_nav, new_nav, 'desktop spatial navigation')

old_eval_defs = '''      const scene = document.querySelector("#spatial-scene-select");
      const observer = document.querySelector("#spatial-observer-select");
      const canvas = document.querySelector('canvas.spatial-canvas[data-scene-id="night-intersection"][data-observer-id="human"]');
      const visionButtons = [...document.querySelectorAll('[role="group"][aria-label="Vision"] button')].map((button) => button.textContent?.trim());
      const sceneValues = scene instanceof HTMLSelectElement ? [...scene.options].map((option) => option.value) : [];
      return scene instanceof HTMLSelectElement'''
new_eval_defs = '''      const scene = document.querySelector("#spatial-scene-select");
      const lighting = document.querySelector("#spatial-lighting-select");
      const observer = document.querySelector("#spatial-observer-select");
      const canvas = document.querySelector('canvas.spatial-canvas[data-scene-id="night-intersection"][data-observer-id="human"]');
      const visionButtons = [...document.querySelectorAll('[role="group"][aria-label="Vision"] button')].map((button) => button.textContent?.trim());
      const sceneValues = scene instanceof HTMLSelectElement ? [...scene.options].map((option) => option.value) : [];
      const lightingValues = lighting instanceof HTMLSelectElement ? [...lighting.options].map((option) => option.value) : [];
      return scene instanceof HTMLSelectElement'''
smoke = replace_once(smoke, old_eval_defs, new_eval_defs, 'spatial stable definitions')

old_stable = '''        && observer instanceof HTMLSelectElement
        && observer.value === "human"
        && canvas instanceof HTMLCanvasElement
        && canvas.dataset.sceneSupportsTranslation === "true"'''
new_stable = '''        && lighting instanceof HTMLSelectElement
        && lighting.value === "day"
        && JSON.stringify(lightingValues) === JSON.stringify(["day", "night"])
        && observer instanceof HTMLSelectElement
        && observer.value === "human"
        && canvas instanceof HTMLCanvasElement
        && canvas.dataset.sceneLightingMode === "day"
        && canvas.dataset.sceneAuthoredAssetRootCount === "1"
        && (canvas.dataset.sceneLoadedChunks ?? "").split(",").includes("c0")
        && canvas.dataset.sceneSupportsTranslation === "true"'''
smoke = replace_once(smoke, old_stable, new_stable, 'spatial stable Day contract')

if smoke.count('150x150x60') != 2:
    raise SystemExit(f'expected two legacy scene volume literals, found {smoke.count("150x150x60")}')
smoke = smoke.replace('150x150x60', '500x500x80-streamed-envelope')

smoke = replace_once(
    smoke,
    'JSON.stringify(["Night Intersection", "360° Photo Reference"])',
    'JSON.stringify(["Hansaplatz 3D", "360° Photo Reference"])',
    'desktop scene labels',
)

old_desktop_controls = '''  const sceneSelect = page.locator("#spatial-scene-select");
  const observerSelect = page.locator("#spatial-observer-select");
  assert((await sceneSelect.inputValue()) === "night-intersection", "desktop spatial: Night Intersection is not active");
  assert((await observerSelect.inputValue()) === "human", "desktop spatial: Human observer is not active");'''
new_desktop_controls = '''  const sceneSelect = page.locator("#spatial-scene-select");
  const lightingSelect = page.locator("#spatial-lighting-select");
  const observerSelect = page.locator("#spatial-observer-select");
  assert((await sceneSelect.inputValue()) === "night-intersection", "desktop spatial: Hansaplatz 3D is not active");
  assert((await lightingSelect.inputValue()) === "day", "desktop spatial: Day is not the default Time of day");
  assert(JSON.stringify(await lightingSelect.locator("option").allTextContents()) === JSON.stringify(["Day", "Night"]), "desktop spatial: unexpected Time of day options");
  assert((await canvas.getAttribute("data-scene-lighting-mode")) === "day", "desktop spatial: canvas is not on Day lighting");
  assert((await observerSelect.inputValue()) === "human", "desktop spatial: Human observer is not active");'''
smoke = replace_once(smoke, old_desktop_controls, new_desktop_controls, 'desktop lighting assertions')

old_mobile_nav = '''  await page.goto(`${BASE}/?view=spatial&production_smoke=e2-mobile-${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30_000 });'''
new_mobile_nav = '''  await page.goto(`${BASE}/?view=spatial&production_smoke=e2-mobile-${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
  await waitForSpatialC0(page);
  const canvas = page.locator("canvas.spatial-canvas");'''
smoke = replace_once(smoke, old_mobile_nav, new_mobile_nav, 'mobile spatial navigation')

old_mobile_controls = '''  const sceneSelect = page.locator("#spatial-scene-select");
  assert((await sceneSelect.inputValue()) === "night-intersection", "mobile spatial: Night Intersection is not active");
  assert((await page.locator("#spatial-observer-select").inputValue()) === "human", "mobile spatial: Human Observer is not active");'''
new_mobile_controls = '''  const sceneSelect = page.locator("#spatial-scene-select");
  const lightingSelect = page.locator("#spatial-lighting-select");
  assert((await sceneSelect.inputValue()) === "night-intersection", "mobile spatial: Hansaplatz 3D is not active");
  assert((await lightingSelect.inputValue()) === "day", "mobile spatial: Day is not the default Time of day");
  assert((await canvas.getAttribute("data-scene-lighting-mode")) === "day", "mobile spatial: canvas is not on Day lighting");
  assert((await page.locator("#spatial-observer-select").inputValue()) === "human", "mobile spatial: Human Observer is not active");'''
smoke = replace_once(smoke, old_mobile_controls, new_mobile_controls, 'mobile lighting assertions')

# Harden production C0 verification so it cannot pass against an old UI that happens
# to serve the same GLB hash.
old_state_defs = '''    const canvas = document.querySelector("canvas.spatial-canvas");
    const sceneSelect = document.querySelector("#spatial-scene-select");
    if (!(canvas instanceof HTMLCanvasElement)) return null;
    return {
      sceneId: canvas.dataset.sceneId ?? null,'''
new_state_defs = '''    const canvas = document.querySelector("canvas.spatial-canvas");
    const sceneSelect = document.querySelector("#spatial-scene-select");
    const lightingSelect = document.querySelector("#spatial-lighting-select");
    if (!(canvas instanceof HTMLCanvasElement)) return null;
    return {
      sceneId: canvas.dataset.sceneId ?? null,
      lightingControlPresent: lightingSelect instanceof HTMLSelectElement,
      lightingValue: lightingSelect instanceof HTMLSelectElement ? lightingSelect.value : null,
      lightingOptions: lightingSelect instanceof HTMLSelectElement ? [...lightingSelect.options].map((option) => option.value) : [],
      canvasLighting: canvas.dataset.sceneLightingMode ?? null,'''
c0 = replace_once(c0, old_state_defs, new_state_defs, 'C0 state lighting fields')

old_live = '''    && state?.sceneId === "night-intersection"
    && state?.observerId === "human"'''
new_live = '''    && state?.sceneId === "night-intersection"
    && state?.lightingControlPresent === true
    && state?.lightingValue === "day"
    && JSON.stringify(state?.lightingOptions) === JSON.stringify(["day", "night"])
    && state?.canvasLighting === "day"
    && state?.observerId === "human"'''
c0 = replace_once(c0, old_live, new_live, 'C0 live Day contract')

old_before = '''await page.screenshot({ path: `${OUT}/production-c0-forward.png`, fullPage: true });
const canvas = page.locator("canvas.spatial-canvas");
const before = await canvas.evaluate((element) => element.dataset.cameraPosition);'''
new_before = '''await page.screenshot({ path: `${OUT}/production-c0-forward.png`, fullPage: true });
const canvas = page.locator("canvas.spatial-canvas");
const lightingSelect = page.locator("#spatial-lighting-select");
const lightingBaseline = await canvas.evaluate((element) => ({
  position: element.dataset.cameraPosition,
  yaw: element.dataset.cameraYaw,
  pitch: element.dataset.cameraPitch,
  fov: element.dataset.cameraFov,
  loadedChunks: element.dataset.sceneLoadedChunks,
  roots: element.dataset.sceneAuthoredAssetRootCount,
  vision: element.dataset.visionMode,
}));
await lightingSelect.selectOption("night");
await page.waitForFunction(() => {
  const element = document.querySelector("canvas.spatial-canvas");
  return element instanceof HTMLCanvasElement
    && element.dataset.sceneLightingMode === "night"
    && element.dataset.sceneLightingRenderState === "complete";
}, undefined, { timeout: 120_000 });
const nightLighting = await canvas.evaluate((element) => ({
  lighting: element.dataset.sceneLightingMode,
  position: element.dataset.cameraPosition,
  yaw: element.dataset.cameraYaw,
  pitch: element.dataset.cameraPitch,
  fov: element.dataset.cameraFov,
  loadedChunks: element.dataset.sceneLoadedChunks,
  roots: element.dataset.sceneAuthoredAssetRootCount,
  vision: element.dataset.visionMode,
}));
await page.screenshot({ path: `${OUT}/production-c0-night.png`, fullPage: true });
await lightingSelect.selectOption("day");
await page.waitForFunction(() => {
  const element = document.querySelector("canvas.spatial-canvas");
  return element instanceof HTMLCanvasElement
    && element.dataset.sceneLightingMode === "day"
    && element.dataset.sceneLightingRenderState === "complete";
}, undefined, { timeout: 120_000 });
const returnedDayLighting = await canvas.evaluate((element) => ({
  lighting: element.dataset.sceneLightingMode,
  position: element.dataset.cameraPosition,
  yaw: element.dataset.cameraYaw,
  pitch: element.dataset.cameraPitch,
  fov: element.dataset.cameraFov,
  loadedChunks: element.dataset.sceneLoadedChunks,
  roots: element.dataset.sceneAuthoredAssetRootCount,
  vision: element.dataset.visionMode,
}));
const sameLightingState = (state) => state
  && state.position === lightingBaseline.position
  && state.yaw === lightingBaseline.yaw
  && state.pitch === lightingBaseline.pitch
  && state.fov === lightingBaseline.fov
  && state.loadedChunks === lightingBaseline.loadedChunks
  && state.roots === lightingBaseline.roots
  && state.vision === lightingBaseline.vision;
const lightingParity = nightLighting?.lighting === "night"
  && returnedDayLighting?.lighting === "day"
  && sameLightingState(nightLighting)
  && sameLightingState(returnedDayLighting);
const before = await canvas.evaluate((element) => element.dataset.cameraPosition);'''
c0 = replace_once(c0, old_before, new_before, 'C0 Day Night parity block')

old_ok = 'const ok = live && moved && fatalErrors.length === 0;'
new_ok = 'const ok = live && lightingParity && moved && fatalErrors.length === 0;'
c0 = replace_once(c0, old_ok, new_ok, 'C0 ok includes lighting parity')

old_result = '''    { ok, live, state, expectedSha: EXPECTED_SHA, deployedSha, before, after, moved, fatalErrors, transientChunkFetchErrors },'''
new_result = '''    { ok, live, state, expectedSha: EXPECTED_SHA, deployedSha, lightingBaseline, nightLighting, returnedDayLighting, lightingParity, before, after, moved, fatalErrors, transientChunkFetchErrors },'''
if c0.count(old_result) != 1:
    raise SystemExit(f'C0 result object expected once, found {c0.count(old_result)}')
c0 = c0.replace(old_result, new_result, 1)

old_console = '''    { ok, live, state, expectedSha: EXPECTED_SHA, deployedSha, before, after, moved, transientChunkFetchErrors },'''
new_console = '''    { ok, live, state, expectedSha: EXPECTED_SHA, deployedSha, lightingBaseline, nightLighting, returnedDayLighting, lightingParity, before, after, moved, transientChunkFetchErrors },'''
c0 = replace_once(c0, old_console, new_console, 'C0 console result object')

smoke_path.write_text(smoke)
c0_path.write_text(c0)
print('production spatial smoke and C0 Day/Night contract updated')
