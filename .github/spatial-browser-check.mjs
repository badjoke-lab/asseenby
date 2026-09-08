import fs from "node:fs/promises";
import { chromium } from "playwright";

const outDir = "browser-check";
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const failures = [];

async function attachDiagnostics(page, label) {
  page.on("pageerror", (error) => failures.push(`${label} pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") failures.push(`${label} console: ${message.text()}`);
  });
}

async function assertNoHorizontalOverflow(page, label) {
  const size = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  if (size.scrollWidth > size.clientWidth + 1) {
    failures.push(`${label}: horizontal overflow ${size.scrollWidth} > ${size.clientWidth}`);
  }
}

async function assertMode(page, name) {
  const button = page.getByRole("button", { name, exact: true });
  await button.click();
  const pressed = await button.getAttribute("aria-pressed");
  if (pressed !== "true") failures.push(`${name}: aria-pressed did not become true`);
  await page.waitForTimeout(140);
}

async function dragCanvas(page, canvas, dx, dy) {
  const box = await canvas.boundingBox();
  if (!box) return false;
  const startX = box.x + box.width * 0.52;
  const startY = box.y + box.height * 0.52;
  await page.mouse.move(startX, startY);
  await page.mouse.down();
  await page.mouse.move(startX + dx, startY + dy, { steps: 8 });
  await page.mouse.up();
  await page.waitForTimeout(140);
  return true;
}

async function waitForAuthoredChunk(page, expectedCount, expectedChunkId = null) {
  await page.waitForFunction(
    ({ expectedCount, expectedChunkId }) => {
      const canvas = document.querySelector("canvas.spatial-canvas");
      if (!(canvas instanceof HTMLCanvasElement)) return false;
      if (canvas.dataset.sceneAuthoredAssetRootCount !== String(expectedCount)) return false;
      const loaded = (canvas.dataset.sceneLoadedChunks ?? "").split(",").filter(Boolean);
      return expectedChunkId ? loaded.includes(expectedChunkId) : loaded.length === 0;
    },
    { expectedCount, expectedChunkId },
    { timeout: 15000 },
  );
}

async function checkImageExperience(page, label) {
  await attachDiagnostics(page, label);
  await page.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: /See the same image through different ways of seeing/i }).waitFor({ state: "visible" });
  await page.getByRole("button", { name: "Upload image", exact: true }).waitFor({ state: "visible" });
  await page.getByText("Original", { exact: true }).first().waitFor({ state: "visible" });
  await page.getByText("Approximation", { exact: true }).first().waitFor({ state: "visible" });
  await assertNoHorizontalOverflow(page, label);
}

const imageDesktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
await checkImageExperience(imageDesktop, "image-desktop");
await imageDesktop.screenshot({ path: `${outDir}/desktop-image-baseline.png`, fullPage: true });
await imageDesktop.close();

const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
await attachDiagnostics(desktop, "spatial-desktop");
await desktop.goto("http://127.0.0.1:4173/?view=spatial", { waitUntil: "networkidle" });
const desktopCanvas = desktop.locator("canvas.spatial-canvas");
await desktopCanvas.waitFor({ state: "visible" });
await assertNoHorizontalOverflow(desktop, "spatial-desktop");

// QR1 authored-world proof: C0 must mount the locally hosted PBR asset,
// unload cleanly when leaving Night Intersection, and remount on return.
await waitForAuthoredChunk(desktop, 1, "c0");
const sceneSelect = desktop.locator("#spatial-scene-select");
await sceneSelect.selectOption("photo-reference");
await waitForAuthoredChunk(desktop, 0, null);
// Dog-like remains a Photo Reference Vision proxy until the Dog observer phase.
await assertMode(desktop, "Dog-like");
await desktop.screenshot({ path: `${outDir}/desktop-photo-dog-like.png`, fullPage: true });
await sceneSelect.selectOption("night-intersection");
await waitForAuthoredChunk(desktop, 1, "c0");
await assertMode(desktop, "Normal");

// Forward view: hold camera fixed and compare each Human geometry Vision against Normal.
await desktop.screenshot({ path: `${outDir}/desktop-normal-forward.png`, fullPage: true });
await assertMode(desktop, "Night / Low Light");
await desktop.screenshot({ path: `${outDir}/desktop-night-forward.png`, fullPage: true });
await assertMode(desktop, "Normal");
await assertMode(desktop, "Central Loss");
await desktop.screenshot({ path: `${outDir}/desktop-central-forward.png`, fullPage: true });
await assertMode(desktop, "Normal");
await assertMode(desktop, "Cataract-like");
await desktop.screenshot({ path: `${outDir}/desktop-cataract-forward.png`, fullPage: true });
await assertMode(desktop, "Normal");

// Tunnel Vision remains live and view-relative while the camera direction changes.
await assertMode(desktop, "Tunnel Vision");
await desktop.screenshot({ path: `${outDir}/desktop-tunnel-forward.png`, fullPage: true });
if (!(await dragCanvas(desktop, desktopCanvas, 250, -45))) {
  failures.push("spatial-desktop: canvas has no bounding box");
} else {
  await desktop.screenshot({ path: `${outDir}/desktop-tunnel-turned.png`, fullPage: true });
}

// Turned view: preserve the exact new camera direction across Normal, Central Loss and Cataract-like.
await assertMode(desktop, "Normal");
await desktop.screenshot({ path: `${outDir}/desktop-normal-turned.png`, fullPage: true });
await assertMode(desktop, "Night / Low Light");
await desktop.screenshot({ path: `${outDir}/desktop-night-turned.png`, fullPage: true });
await assertMode(desktop, "Normal");
await assertMode(desktop, "Central Loss");
await desktop.screenshot({ path: `${outDir}/desktop-central-turned.png`, fullPage: true });
await assertMode(desktop, "Normal");
await assertMode(desktop, "Cataract-like");
await desktop.screenshot({ path: `${outDir}/desktop-cataract-turned.png`, fullPage: true });

// Scene-quality check: sweep through the original direction to the opposite side.
// Both horizontal directions must contain meaningful street/facade information rather than an empty dark void.
await assertMode(desktop, "Normal");
if (!(await dragCanvas(desktop, desktopCanvas, -500, 45))) {
  failures.push("spatial-desktop-opposite: canvas has no bounding box");
} else {
  await desktop.screenshot({ path: `${outDir}/desktop-normal-opposite.png`, fullPage: true });
}

const mobileContext = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 1,
  isMobile: true,
  hasTouch: true,
});

const imageMobile = await mobileContext.newPage();
await checkImageExperience(imageMobile, "image-mobile");
await imageMobile.screenshot({ path: `${outDir}/mobile-image-baseline.png`, fullPage: true });
await imageMobile.close();

const mobile = await mobileContext.newPage();
await attachDiagnostics(mobile, "spatial-mobile");
await mobile.goto("http://127.0.0.1:4173/?view=spatial", { waitUntil: "networkidle" });
const mobileCanvas = mobile.locator("canvas.spatial-canvas");
await mobileCanvas.waitFor({ state: "visible" });
await assertNoHorizontalOverflow(mobile, "spatial-mobile");
await waitForAuthoredChunk(mobile, 1, "c0");

await mobile.screenshot({ path: `${outDir}/mobile-normal-forward.png`, fullPage: true });
await assertMode(mobile, "Central Loss");
await mobile.screenshot({ path: `${outDir}/mobile-central-forward.png`, fullPage: true });

// Exercise real touch input while Central Loss is active, then verify the affected region on the turned view.
const mobileBox = await mobileCanvas.boundingBox();
if (!mobileBox) {
  failures.push("spatial-mobile: canvas has no bounding box");
} else {
  const session = await mobileContext.newCDPSession(mobile);
  const startX = mobileBox.x + mobileBox.width * 0.52;
  const startY = mobileBox.y + mobileBox.height * 0.52;
  await session.send("Input.dispatchTouchEvent", {
    type: "touchStart",
    touchPoints: [{ x: startX, y: startY, radiusX: 2, radiusY: 2, force: 1, id: 1 }],
  });
  await session.send("Input.dispatchTouchEvent", {
    type: "touchMove",
    touchPoints: [{ x: startX + 72, y: startY - 20, radiusX: 2, radiusY: 2, force: 1, id: 1 }],
  });
  await session.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await mobile.waitForTimeout(150);
}
await mobile.screenshot({ path: `${outDir}/mobile-central-turned.png`, fullPage: true });

await assertMode(mobile, "Normal");
await mobile.screenshot({ path: `${outDir}/mobile-normal-turned.png`, fullPage: true });
await assertMode(mobile, "Night / Low Light");
await mobile.screenshot({ path: `${outDir}/mobile-night-turned.png`, fullPage: true });
await assertMode(mobile, "Tunnel Vision");
await mobile.screenshot({ path: `${outDir}/mobile-tunnel-turned.png`, fullPage: true });
await assertMode(mobile, "Cataract-like");
await mobile.screenshot({ path: `${outDir}/mobile-cataract-turned.png`, fullPage: true });

await mobileContext.close();
await desktop.close();
await browser.close();

await fs.writeFile(`${outDir}/result.json`, JSON.stringify({ ok: failures.length === 0, failures }, null, 2));
if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
