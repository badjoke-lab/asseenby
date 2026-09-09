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

async function waitForC0(page) {
  await page.waitForFunction(() => {
    const canvas = document.querySelector("canvas.spatial-canvas");
    if (!(canvas instanceof HTMLCanvasElement)) return false;
    const chunks = (canvas.dataset.sceneLoadedChunks ?? "").split(",").filter(Boolean);
    return canvas.dataset.sceneId === "night-intersection"
      && canvas.dataset.observerId === "human"
      && canvas.dataset.sceneAuthoredAssetRootCount === "1"
      && chunks.includes("c0")
      && canvas.clientWidth > 0
      && canvas.clientHeight > 0;
  }, undefined, { timeout: 30_000 });
  await page.waitForTimeout(1200);
}

async function canvasState(page) {
  return page.locator("canvas.spatial-canvas").evaluate((canvas) => ({
    position: canvas.dataset.cameraPosition,
    yaw: canvas.dataset.cameraYaw,
    pitch: canvas.dataset.cameraPitch,
    scene: canvas.dataset.sceneId,
    observer: canvas.dataset.observerId,
    chunks: canvas.dataset.sceneLoadedChunks,
    roots: canvas.dataset.sceneAuthoredAssetRootCount,
    movement: canvas.dataset.observerMovement,
  }));
}

const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
collectErrors(desktop, "desktop");
await desktop.goto(`${BASE}/?view=spatial&lod2_visual=${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
await waitForC0(desktop);
const desktopCanvas = desktop.locator("canvas.spatial-canvas");
await desktopCanvas.scrollIntoViewIfNeeded();
await desktop.screenshot({ path: `${OUT}/desktop-forward.png`, fullPage: true });
const initial = await canvasState(desktop);

const box = await desktopCanvas.boundingBox();
if (!box) throw new Error("desktop canvas has no bounding box");
const sx = box.x + box.width * 0.50;
const sy = box.y + box.height * 0.50;
await desktop.mouse.move(sx, sy);
await desktop.mouse.down();
await desktop.mouse.move(sx + Math.min(280, box.width * 0.28), sy - 35, { steps: 12 });
await desktop.mouse.up();
await desktop.waitForTimeout(250);
await desktop.screenshot({ path: `${OUT}/desktop-turned.png`, fullPage: true });
const turned = await canvasState(desktop);

await desktopCanvas.focus();
await desktop.keyboard.down("w");
await desktop.waitForTimeout(650);
await desktop.keyboard.up("w");
await desktop.waitForTimeout(250);
await desktop.screenshot({ path: `${OUT}/desktop-moved.png`, fullPage: true });
const moved = await canvasState(desktop);

const mobileContext = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
const mobile = await mobileContext.newPage();
collectErrors(mobile, "mobile");
await mobile.goto(`${BASE}/?view=spatial&lod2_mobile=${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
await waitForC0(mobile);
await mobile.locator("canvas.spatial-canvas").scrollIntoViewIfNeeded();
await mobile.screenshot({ path: `${OUT}/mobile-forward.png`, fullPage: true });
const mobileState = await canvasState(mobile);

const result = {
  ok: errors.length === 0
    && initial.roots === "1"
    && initial.chunks?.split(",").includes("c0")
    && initial.movement === "bounded-ground"
    && turned.yaw !== initial.yaw
    && moved.position !== turned.position,
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

if (!result.ok) {
  throw new Error(`LoD2 visual proof failed: ${JSON.stringify(result)}`);
}
console.log(JSON.stringify(result, null, 2));
