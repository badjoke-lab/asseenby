import { chromium } from "playwright";
import fs from "node:fs/promises";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "https://asseenby.pages.dev";
const OUT = "production-spatial-c0";
await fs.mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
const errors = [];
page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
page.on("console", (message) => {
  if (message.type() === "error") errors.push(`console: ${message.text()}`);
});

let live = false;
let state = null;
for (let attempt = 1; attempt <= 24; attempt += 1) {
  await page.goto(`${BASE}/?view=spatial&production_c0=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  await page.waitForTimeout(1200);
  state = await page.evaluate(() => {
    const canvas = document.querySelector("canvas.spatial-canvas");
    if (!(canvas instanceof HTMLCanvasElement)) return null;
    return {
      sceneId: canvas.dataset.sceneId ?? null,
      observerId: canvas.dataset.observerId ?? null,
      position: canvas.dataset.cameraPosition ?? null,
      movement: canvas.dataset.observerMovement ?? null,
      supportsTranslation: canvas.dataset.sceneSupportsTranslation ?? null,
      loadedChunks: canvas.dataset.sceneLoadedChunks ?? null,
      authoredAssetRootCount: canvas.dataset.sceneAuthoredAssetRootCount ?? null,
      width: canvas.clientWidth,
      height: canvas.clientHeight,
    };
  });
  if (
    state?.sceneId === "night-intersection"
    && state?.observerId === "human"
    && state?.movement === "bounded-ground"
    && state?.supportsTranslation === "true"
    && state?.authoredAssetRootCount === "1"
    && (state?.loadedChunks ?? "").split(",").includes("c0")
    && state.width > 0
    && state.height > 0
  ) {
    live = true;
    break;
  }
  if (attempt < 24) await page.waitForTimeout(10_000);
}

if (!live) {
  await page.screenshot({ path: `${OUT}/production-spatial-not-current.png`, fullPage: true });
  await fs.writeFile(`${OUT}/result.json`, JSON.stringify({ ok: false, live, state, errors }, null, 2));
  await browser.close();
  throw new Error(`Current authored C0 did not appear in production: ${JSON.stringify(state)}`);
}

await page.screenshot({ path: `${OUT}/production-c0-forward.png`, fullPage: true });
const canvas = page.locator("canvas.spatial-canvas");
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
const ok = live && moved && errors.length === 0;
await fs.writeFile(`${OUT}/result.json`, JSON.stringify({ ok, live, state, before, after, moved, errors }, null, 2));
await browser.close();
if (!ok) throw new Error(`Production C0 verification failed: ${JSON.stringify({ state, before, after, moved, errors })}`);
console.log(JSON.stringify({ ok, live, state, before, after, moved }, null, 2));
