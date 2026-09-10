import fs from "node:fs/promises";
import { chromium } from "playwright";

const BASE = process.env.ASSEENBY_PREVIEW_URL || "http://127.0.0.1:4173";
const OUT = "lod2-visual-proof";
await fs.rm(OUT, { recursive: true, force: true });
await fs.mkdir(OUT, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  args: ["--use-gl=swiftshader", "--disable-gpu-sandbox"],
});
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
      lighting: canvas.dataset.sceneLightingMode ?? null,
      chunks: canvas.dataset.sceneLoadedChunks ?? null,
      roots: canvas.dataset.sceneAuthoredAssetRootCount ?? null,
      movement: canvas.dataset.observerMovement ?? null,
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    };
  });
}

async function waitForC0(page, timeout = 120_000) {
  await page.waitForFunction(
    () => {
      const canvas = document.querySelector("canvas.spatial-canvas");
      return canvas instanceof HTMLCanvasElement
        && canvas.dataset.sceneAuthoredAssetRootCount === "1"
        && (canvas.dataset.sceneLoadedChunks || "").split(",").includes("c0");
    },
    { timeout, polling: 250 },
  );
  await page.waitForTimeout(1200);
  return readCanvas(page);
}

async function frameCanvas(page) {
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.scrollIntoViewIfNeeded();
  await page.waitForTimeout(180);
  const box = await canvas.boundingBox();
  if (!box) throw new Error("canvas has no bounding box after scrollIntoViewIfNeeded");
  return { canvas, box };
}

async function captureViewport(page, path) {
  const session = await page.context().newCDPSession(page);
  try {
    const { data } = await session.send("Page.captureScreenshot", {
      format: "png",
      fromSurface: true,
      captureBeyondViewport: false,
    });
    await fs.writeFile(path, Buffer.from(data, "base64"));
  } finally {
    await session.detach();
  }
}

const desktop = await browser.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
collectErrors(desktop, "desktop");
await desktop.goto(`${BASE}/?view=spatial&hamburg_visual=${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
await waitForC0(desktop);
let { canvas: desktopCanvas, box: desktopBox } = await frameCanvas(desktop);
let initial = await readCanvas(desktop);
await captureViewport(desktop, `${OUT}/desktop-forward.png`);

await desktop.selectOption("#spatial-lighting-select", "night");
await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "night");
await desktop.waitForFunction(
  () => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingRenderState === "complete",
  null,
  { timeout: 120_000 },
);
await desktop.waitForTimeout(250);
const nightLightingState = await readCanvas(desktop);
await captureViewport(desktop, `${OUT}/desktop-night-forward.png`);
await desktop.selectOption("#spatial-lighting-select", "day");
await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "day");
await desktop.waitForFunction(
  () => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingRenderState === "complete",
  null,
  { timeout: 120_000 },
);
await desktop.waitForTimeout(250);
const dayReturnState = await readCanvas(desktop);

let turned = null;
let moved = null;
if (desktopBox.width > 0 && desktopBox.height > 0) {
  const sx = desktopBox.x + desktopBox.width * 0.50;
  const sy = desktopBox.y + Math.min(desktopBox.height * 0.50, 320);
  await desktop.mouse.move(sx, sy);
  await desktop.mouse.down();
  await desktop.mouse.move(sx + Math.min(240, desktopBox.width * 0.24), sy - 30, { steps: 10 });
  await desktop.mouse.up();
  await desktop.waitForTimeout(500);
  turned = await readCanvas(desktop);
  await captureViewport(desktop, `${OUT}/desktop-turned.png`);

  await desktopCanvas.focus();
  await desktop.keyboard.down("w");
  await desktop.waitForTimeout(650);
  await desktop.keyboard.up("w");
  await desktop.waitForTimeout(500);
  moved = await readCanvas(desktop);
  await captureViewport(desktop, `${OUT}/desktop-moved.png`);
}

// Diagnostic ring from the exact HDRI/LoD2 registration origin. Each 15-key
// increment is 1.05 rad (~60.16 degrees), close enough to pair silhouettes with
// the checked-in 60-degree photographic reference plates. This is diagnostic
// evidence only; the relative panorama seam is not claimed as geographic north.
const registration = await browser.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
collectErrors(registration, "registration");
await registration.goto(`${BASE}/?view=spatial&hamburg_registration=${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
await waitForC0(registration);
const { canvas: registrationCanvas } = await frameCanvas(registration);
await registrationCanvas.focus();
const registrationStates = [];
for (let index = 0; index < 6; index += 1) {
  if (index > 0) {
    for (let step = 0; step < 15; step += 1) await registration.keyboard.press("ArrowLeft");
    await registration.waitForTimeout(250);
  }
  const state = await readCanvas(registration);
  registrationStates.push(state);
  const degrees = String(index * 60).padStart(3, "0");
  await captureViewport(registration, `${OUT}/registration-yaw-${degrees}.png`);
}

const mobileContext = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 1,
  isMobile: true,
  hasTouch: true,
});
const mobile = await mobileContext.newPage();
collectErrors(mobile, "mobile");
await mobile.goto(`${BASE}/?view=spatial&hamburg_mobile=${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
await waitForC0(mobile);
await frameCanvas(mobile);
const mobileState = await readCanvas(mobile);
await captureViewport(mobile, `${OUT}/mobile-forward.png`);

const yawDelta = initial?.yaw != null && turned?.yaw != null
  ? Math.abs(Number(turned.yaw) - Number(initial.yaw))
  : 0;
const registrationOriginOk = registrationStates.every((state) => state?.position === "0.000,0.000,0.000");
const result = {
  ok: errors.length === 0
    && initial?.roots === "1"
    && initial?.chunks?.split(",").includes("c0")
    && initial?.movement === "bounded-ground"
    && initial?.lighting === "day"
    && nightLightingState?.lighting === "night"
    && nightLightingState?.roots === initial?.roots
    && nightLightingState?.chunks === initial?.chunks
    && nightLightingState?.position === initial?.position
    && nightLightingState?.yaw === initial?.yaw
    && nightLightingState?.pitch === initial?.pitch
    && dayReturnState?.lighting === "day"
    && dayReturnState?.position === initial?.position
    && dayReturnState?.yaw === initial?.yaw
    && dayReturnState?.pitch === initial?.pitch
    && initial?.position === "0.000,0.000,0.000"
    && Number.isFinite(yawDelta)
    && yawDelta >= 0.25
    && moved?.position !== turned?.position
    && mobileState?.roots === "1"
    && registrationOriginOk,
  errors,
  yawDelta,
  initial,
  nightLightingState,
  dayReturnState,
  turned,
  moved,
  mobile: mobileState,
  registrationOriginOk,
  registrationStates,
};
await fs.writeFile(`${OUT}/result.json`, JSON.stringify(result, null, 2));

await mobileContext.close();
await registration.close();
await desktop.close();
await browser.close();

console.log(JSON.stringify(result, null, 2));
if (!result.ok) process.exitCode = 1;
