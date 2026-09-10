import { chromium } from "playwright";
import fs from "node:fs/promises";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "https://asseenby.pages.dev";
const OUT = "production-day-night-proof";
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

const snapshot = async () => page.evaluate(() => {
  const canvas = document.querySelector("canvas.spatial-canvas");
  const lighting = document.querySelector("#spatial-lighting-select");
  const card = document.querySelector(".spatial-card");
  if (!(canvas instanceof HTMLCanvasElement)) return null;
  return {
    lightingControlPresent: lighting instanceof HTMLSelectElement,
    lightingValue: lighting instanceof HTMLSelectElement ? lighting.value : null,
    lightingOptions: lighting instanceof HTMLSelectElement ? [...lighting.options].map((option) => option.value) : [],
    cardLighting: card instanceof HTMLElement ? card.dataset.lightingMode ?? null : null,
    canvasLighting: canvas.dataset.sceneLightingMode ?? null,
    renderState: canvas.dataset.sceneLightingRenderState ?? null,
    position: canvas.dataset.cameraPosition ?? null,
    yaw: canvas.dataset.cameraYaw ?? null,
    pitch: canvas.dataset.cameraPitch ?? null,
    loadedChunks: canvas.dataset.sceneLoadedChunks ?? null,
    roots: canvas.dataset.sceneAuthoredAssetRootCount ?? null,
    sceneId: canvas.dataset.sceneId ?? null,
    observerId: canvas.dataset.observerId ?? null,
    visionMode: canvas.dataset.visionMode ?? null,
  };
});

let initial = null;
let night = null;
let returned = null;
let lastError = null;

for (let attempt = 1; attempt <= 18; attempt += 1) {
  try {
    await page.goto(`${BASE}/?view=spatial&production_day_night=${Date.now()}`, {
      waitUntil: "domcontentloaded",
      timeout: 30_000,
    });
    await page.locator("canvas.spatial-canvas").waitFor({ state: "visible", timeout: 20_000 });
    const lighting = page.locator("#spatial-lighting-select");
    await lighting.waitFor({ state: "visible", timeout: 8_000 });
    initial = await snapshot();
    if (
      initial?.lightingControlPresent
      && initial?.lightingValue === "day"
      && initial?.lightingOptions.includes("day")
      && initial?.lightingOptions.includes("night")
      && initial?.cardLighting === "day"
      && initial?.canvasLighting === "day"
      && initial?.sceneId === "night-intersection"
      && initial?.observerId === "human"
      && initial?.visionMode === "normal"
      && initial?.roots === "1"
      && initial?.loadedChunks?.split(",").includes("c0")
    ) {
      lastError = null;
      break;
    }
    lastError = `production not current on attempt ${attempt}: ${JSON.stringify(initial)}`;
  } catch (error) {
    lastError = error instanceof Error ? error.message : String(error);
  }
  if (attempt < 18) await page.waitForTimeout(7_500);
}

if (!initial?.lightingControlPresent || initial?.lightingValue !== "day" || initial?.canvasLighting !== "day") {
  await page.screenshot({ path: `${OUT}/production-not-day-current.png`, fullPage: true }).catch(() => {});
  await fs.writeFile(`${OUT}/result.json`, JSON.stringify({ ok: false, phase: "initial", initial, lastError, errors }, null, 2));
  await browser.close();
  throw new Error(`Day-first production UI not detected: ${lastError}`);
}

await page.screenshot({ path: `${OUT}/production-day.png`, fullPage: true });
const before = { ...initial };

await page.selectOption("#spatial-lighting-select", "night");
await page.waitForFunction(() => {
  const canvas = document.querySelector("canvas.spatial-canvas");
  return canvas instanceof HTMLCanvasElement
    && canvas.dataset.sceneLightingMode === "night"
    && canvas.dataset.sceneLightingRenderState === "complete";
}, { timeout: 120_000 });
night = await snapshot();
await page.screenshot({ path: `${OUT}/production-night.png`, fullPage: true });

await page.selectOption("#spatial-lighting-select", "day");
await page.waitForFunction(() => {
  const canvas = document.querySelector("canvas.spatial-canvas");
  return canvas instanceof HTMLCanvasElement
    && canvas.dataset.sceneLightingMode === "day"
    && canvas.dataset.sceneLightingRenderState === "complete";
}, { timeout: 120_000 });
returned = await snapshot();
await page.screenshot({ path: `${OUT}/production-day-return.png`, fullPage: true });

const stable = (state) => state
  && state.position === before.position
  && state.yaw === before.yaw
  && state.pitch === before.pitch
  && state.loadedChunks === before.loadedChunks
  && state.roots === before.roots
  && state.sceneId === before.sceneId
  && state.observerId === before.observerId
  && state.visionMode === before.visionMode;

const fatalErrors = errors.filter((error) => !error.includes("Explore 3D chunk failed to load: c0 TypeError: Failed to fetch"));
const ok = Boolean(
  initial?.lightingValue === "day"
  && initial?.canvasLighting === "day"
  && night?.lightingValue === "night"
  && night?.canvasLighting === "night"
  && returned?.lightingValue === "day"
  && returned?.canvasLighting === "day"
  && stable(night)
  && stable(returned)
  && fatalErrors.length === 0
);

const result = { ok, baseUrl: BASE, initial, night, returned, fatalErrors, errors };
await fs.writeFile(`${OUT}/result.json`, JSON.stringify(result, null, 2));
await browser.close();
console.log(JSON.stringify(result, null, 2));
if (!ok) throw new Error(`Production Day/Night proof failed: ${JSON.stringify(result)}`);
