#!/usr/bin/env python3
from pathlib import Path

path = Path('.github/production-spatial-c0-check.mjs')
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, found {count}')
    text = text.replace(old, new, 1)

old_baseline = '''const canvas = page.locator("canvas.spatial-canvas");
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
await lightingSelect.selectOption("night");'''
new_baseline = '''const readLightingState = async () => page.evaluate(() => {
  const element = document.querySelector("canvas.spatial-canvas");
  if (!(element instanceof HTMLCanvasElement)) return null;
  return {
    lighting: element.dataset.sceneLightingMode ?? null,
    renderState: element.dataset.sceneLightingRenderState ?? null,
    position: element.dataset.cameraPosition ?? null,
    yaw: element.dataset.cameraYaw ?? null,
    pitch: element.dataset.cameraPitch ?? null,
    fov: element.dataset.cameraFov ?? null,
    loadedChunks: element.dataset.sceneLoadedChunks ?? null,
    roots: element.dataset.sceneAuthoredAssetRootCount ?? null,
    vision: element.dataset.visionMode ?? null,
  };
});
const lightingBaseline = await readLightingState();
await page.selectOption("#spatial-lighting-select", "night");'''
replace_once(old_baseline, new_baseline, 'baseline lighting snapshot')

old_night = '''const nightLighting = await canvas.evaluate((element) => ({
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
await lightingSelect.selectOption("day");'''
new_night = '''const nightLighting = await readLightingState();
await page.screenshot({ path: `${OUT}/production-c0-night.png`, fullPage: true });
await page.selectOption("#spatial-lighting-select", "day");'''
replace_once(old_night, new_night, 'night lighting snapshot')

old_day = '''const returnedDayLighting = await canvas.evaluate((element) => ({
  lighting: element.dataset.sceneLightingMode,
  position: element.dataset.cameraPosition,
  yaw: element.dataset.cameraYaw,
  pitch: element.dataset.cameraPitch,
  fov: element.dataset.cameraFov,
  loadedChunks: element.dataset.sceneLoadedChunks,
  roots: element.dataset.sceneAuthoredAssetRootCount,
  vision: element.dataset.visionMode,
}));'''
new_day = '''const returnedDayLighting = await readLightingState();'''
replace_once(old_day, new_day, 'returned Day lighting snapshot')

old_before = '''const before = await canvas.evaluate((element) => element.dataset.cameraPosition);
await canvas.focus();
await page.keyboard.down("w");'''
new_before = '''const movementCanvas = page.locator("canvas.spatial-canvas");
await movementCanvas.waitFor({ state: "visible", timeout: 30_000 });
const before = await movementCanvas.evaluate((element) => element.dataset.cameraPosition);
await movementCanvas.focus();
await page.keyboard.down("w");'''
replace_once(old_before, new_before, 'movement canvas reacquire')

old_after = '''const after = await canvas.evaluate((element) => ({
  position: element.dataset.cameraPosition,
  viewpoint: element.dataset.cameraViewpoint,
  movement: element.dataset.observerMovement,
  loadedChunks: element.dataset.sceneLoadedChunks,
  authoredAssetRootCount: element.dataset.sceneAuthoredAssetRootCount,
}));'''
new_after = '''const after = await movementCanvas.evaluate((element) => ({
  position: element.dataset.cameraPosition,
  viewpoint: element.dataset.cameraViewpoint,
  movement: element.dataset.observerMovement,
  loadedChunks: element.dataset.sceneLoadedChunks,
  authoredAssetRootCount: element.dataset.sceneAuthoredAssetRootCount,
}));'''
replace_once(old_after, new_after, 'movement state read')

old_throw = '''if (!ok) throw new Error(`Production C0 verification failed: ${JSON.stringify({ state, before, after, moved, fatalErrors })}`);'''
new_throw = '''if (!ok) throw new Error(`Production C0 verification failed: ${JSON.stringify({ state, lightingBaseline, nightLighting, returnedDayLighting, lightingParity, before, after, moved, fatalErrors })}`);'''
replace_once(old_throw, new_throw, 'diagnostic error payload')

path.write_text(text)
print('production C0 lighting snapshots now re-query the live DOM')
