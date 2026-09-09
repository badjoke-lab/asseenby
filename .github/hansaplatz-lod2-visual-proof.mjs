import fs from "node:fs/promises";
import { chromium } from "playwright";

const BASE = process.env.ASSEENBY_PREVIEW_URL || "http://127.0.0.1:4173";
const OUT = "lod2-visual-proof";
await fs.rm(OUT, { recursive: true, force: true });
await fs.mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const errors = [];

function collectErrors(page, label) {
  page.on("pageerror", (error) => errors.push(`${label} pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`${label} console: ${message.text()}`);
  });
}

async function readCanvas(page) {
  return page.evaluate(() => {
    const canvas = document.querySelector("canvas.spatial-canvas");
    if (!(canvas instanceof HTMLCanvasElement)) return null;
    const rect = canvas.getBoundingClientRect();
    return {
      position: canvas.dataset.cameraPosition ?? null,
      yaw: canvas.dataset.cameraYaw ?? null,
      pitch: canvas.dataset.cameraPitch ?? null,
      scene: canvas.dataset.sceneId ?? null,
      observer: canvas.dataset.observerId ?? null,
      chunks: canvas.dataset.sceneLoadedChunks ?? null,
      roots: canvas.dataset.sceneAuthoredAssetRootCount ?? null,
      movement: canvas.dataset.observerMovement ?? null,
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    };
  });
}

async function settle(page, millis = 9000) {
  await page.waitForTimeout(millis);
  return readCanvas(page);
}

const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
collectErrors(desktop, "desktop");
await desktop.goto(`${BASE}/?view=spatial&lod2_visual=${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
let initial = await settle(desktop);
await desktop.screenshot({ path: `${OUT}/desktop-forward.png`, fullPage: true });

let turned = null;
let moved = null;
if (initial?.rect?.width > 0 && initial?.rect?.height > 0) {
  const box = initial.rect;
  const sx = box.x + box.width * 0.50;
  const sy = box.y + box.height * 0.50;
  await desktop.mouse.move(sx, sy);
  await desktop.mouse.down();
  await desktop.mouse.move(sx + Math.min(280, box.width * 0.28), sy - 35, { steps: 12 });
  await desktop.mouse.up();
  await desktop.waitForTimeout(350);
  turned = await readCanvas(desktop);
  await desktop.screenshot({ path: `${OUT}/desktop-turned.png`, fullPage: true });

  await desktop.evaluate(() => document.querySelector("canvas.spatial-canvas")?.focus());
  await desktop.keyboard.down("w");
  await desktop.waitForTimeout(650);
  await desktop.keyboard.up("w");
  await desktop.waitForTimeout(350);
  moved = await readCanvas(desktop);
  await desktop.screenshot({ path: `${OUT}/desktop-moved.png`, fullPage: true });
}

const mobileContext = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
const mobile = await mobileContext.newPage();
collectErrors(mobile, "mobile");
await mobile.goto(`${BASE}/?view=spatial&lod2_mobile=${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
const mobileState = await settle(mobile, 9000);
await mobile.screenshot({ path: `${OUT}/mobile-forward.png`, fullPage: true });

const result = {
  ok: errors.length === 0
    && initial?.roots === "1"
    && initial?.chunks?.split(",").includes("c0")
    && initial?.movement === "bounded-ground"
    && turned?.yaw !== initial?.yaw
    && moved?.position !== turned?.position
    && mobileState?.roots === "1",
  errors,
  initial,
  turned,
  moved,
  mobile: mobileState,
};
await fs.writeFile(`${OUT}/result.json`, JSON.stringify(result, null, 2));

await mobileContext.close();
await desktop.close();
await browser.close();

console.log(JSON.stringify(result, null, 2));
if (!result.ok) process.exitCode = 1;
