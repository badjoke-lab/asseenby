import { chromium } from "playwright";
import fs from "node:fs/promises";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "https://asseenby.pages.dev";
const OUT = "production-spatial-c0";
const SHA_PATH = "public/assets/3d/night-intersection/c0/core/SHA256SUMS.txt";
const EXPECTED_SHA = (await fs.readFile(SHA_PATH, "utf8")).trim();
await fs.rm(OUT, { recursive: true, force: true });
await fs.mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
const errors = [];
page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
page.on("console", (message) => {
  if (message.type() === "error") errors.push(`console: ${message.text()}`);
});
page.on("crash", () => errors.push("page crash"));

let live = false;
let state = null;
let deployedSha = null;
let lastNavigationError = null;

for (let attempt = 1; attempt <= 18; attempt += 1) {
  const cacheBust = Date.now();
  try {
    await page.goto(`${BASE}/?view=spatial&production_c0=${cacheBust}`, {
      waitUntil: "domcontentloaded",
      timeout: 30_000,
    });
    await page.locator("canvas.spatial-canvas").waitFor({ state: "visible", timeout: 20_000 });
    await page.waitForTimeout(900);
    lastNavigationError = null;
  } catch (error) {
    lastNavigationError = error instanceof Error ? error.message : String(error);
    if (attempt < 18) {
      await page.waitForTimeout(7_500);
      continue;
    }
    break;
  }

  try {
    const response = await fetch(`${BASE}/assets/3d/night-intersection/c0/core/SHA256SUMS.txt?production_c0_sha=${cacheBust}`, {
      cache: "no-store",
    });
    deployedSha = response.ok ? (await response.text()).trim() : `HTTP ${response.status}`;
  } catch (error) {
    deployedSha = `fetch failed: ${error instanceof Error ? error.message : String(error)}`;
  }

  state = await page.evaluate(() => {
    const canvas = document.querySelector("canvas.spatial-canvas");
    const sceneSelect = document.querySelector("#spatial-scene-select");
    const lightingSelect = document.querySelector("#spatial-lighting-select");
    if (!(canvas instanceof HTMLCanvasElement)) return null;
    return {
      sceneId: canvas.dataset.sceneId ?? null,
      lightingControlPresent: lightingSelect instanceof HTMLSelectElement,
      lightingValue: lightingSelect instanceof HTMLSelectElement ? lightingSelect.value : null,
      lightingOptions: lightingSelect instanceof HTMLSelectElement ? [...lightingSelect.options].map((option) => option.value) : [],
      canvasLighting: canvas.dataset.sceneLightingMode ?? null,
      observerId: canvas.dataset.observerId ?? null,
      position: canvas.dataset.cameraPosition ?? null,
      movement: canvas.dataset.observerMovement ?? null,
      supportsTranslation: canvas.dataset.sceneSupportsTranslation ?? null,
      loadedChunks: canvas.dataset.sceneLoadedChunks ?? null,
      authoredAssetRootCount: canvas.dataset.sceneAuthoredAssetRootCount ?? null,
      sceneVolume: canvas.dataset.sceneVolume ?? null,
      visionMode: canvas.dataset.visionMode ?? null,
      sceneSelectPresent: sceneSelect instanceof HTMLSelectElement,
      width: canvas.clientWidth,
      height: canvas.clientHeight,
    };
  });

  if (
    deployedSha === EXPECTED_SHA
    && state?.sceneId === "night-intersection"
    && state?.lightingControlPresent === true
    && state?.lightingValue === "day"
    && JSON.stringify(state?.lightingOptions) === JSON.stringify(["day", "night"])
    && state?.canvasLighting === "day"
    && state?.observerId === "human"
    && state?.movement === "bounded-ground"
    && state?.supportsTranslation === "true"
    && state?.authoredAssetRootCount === "1"
    && (state?.loadedChunks ?? "").split(",").includes("c0")
    && state?.sceneVolume === "500x500x80-streamed-envelope"
    && state?.visionMode === "normal"
    && state?.sceneSelectPresent === true
    && state.width > 0
    && state.height > 0
  ) {
    live = true;
    break;
  }

  if (attempt < 18) await page.waitForTimeout(7_500);
}

if (!live) {
  await page.screenshot({ path: `${OUT}/production-spatial-not-current.png`, fullPage: true }).catch(() => {});
  await fs.writeFile(
    `${OUT}/result.json`,
    JSON.stringify({ ok: false, live, state, expectedSha: EXPECTED_SHA, deployedSha, lastNavigationError, errors }, null, 2),
  );
  await browser.close();
  throw new Error(
    `Current authored C0 did not appear in production: ${JSON.stringify({ state, expectedSha: EXPECTED_SHA, deployedSha, lastNavigationError })}`,
  );
}

await page.screenshot({ path: `${OUT}/production-c0-forward.png`, fullPage: true });
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
const before = await canvas.evaluate((element) => element.dataset.cameraPosition);
await canvas.focus();
await page.keyboard.down("w");
await page.waitForTimeout(420);
await page.keyboard.up("w");
await page.waitForTimeout(180);
const after = await canvas.evaluate((element) => ({
  position: element.dataset.cameraPosition,
  viewpoint: element.dataset.cameraViewpoint,
  movement: element.dataset.observerMovement,
  loadedChunks: element.dataset.sceneLoadedChunks,
  authoredAssetRootCount: element.dataset.sceneAuthoredAssetRootCount,
}));
await page.screenshot({ path: `${OUT}/production-c0-moved.png`, fullPage: true });

const moved = Boolean(before && after.position && before !== after.position && after.viewpoint === "free");
// Pages can briefly serve the new HTML before the large GLB is available at the edge.
// If the verifier subsequently proves the exact expected SHA, mounts C0, and moves
// through it successfully, that earlier one-off chunk fetch is a deployment race,
// not a current production failure. Keep it in the proof as a transient warning.
const transientChunkFetchErrors = errors.filter((error) =>
  error.includes("Explore 3D chunk failed to load: c0 TypeError: Failed to fetch"),
);
const fatalErrors = errors.filter((error) => !transientChunkFetchErrors.includes(error));
const ok = live && lightingParity && moved && fatalErrors.length === 0;
await fs.writeFile(
  `${OUT}/result.json`,
  JSON.stringify(
    { ok, live, state, expectedSha: EXPECTED_SHA, deployedSha, lightingBaseline, nightLighting, returnedDayLighting, lightingParity, before, after, moved, fatalErrors, transientChunkFetchErrors },
    null,
    2,
  ),
);
await browser.close();
if (!ok) throw new Error(`Production C0 verification failed: ${JSON.stringify({ state, before, after, moved, fatalErrors })}`);
console.log(
  JSON.stringify(
    { ok, live, state, expectedSha: EXPECTED_SHA, deployedSha, lightingBaseline, nightLighting, returnedDayLighting, lightingParity, before, after, moved, transientChunkFetchErrors },
    null,
    2,
  ),
);
