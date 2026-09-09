import fs from "node:fs/promises";
import { chromium } from "playwright";

const outDir = "browser-check";
await fs.rm(outDir, { recursive: true, force: true });
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const failures = [];

function attachDiagnostics(page, label) {
  page.on("pageerror", (error) => failures.push(`${label} pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") failures.push(`${label} console: ${message.text()}`);
  });
  page.on("crash", () => failures.push(`${label}: page crashed`));
}

async function captureFailureState(page, label, error) {
  failures.push(`${label}: ${error instanceof Error ? error.message : String(error)}`);
  const state = await page.evaluate(() => {
    const canvas = document.querySelector("canvas.spatial-canvas");
    return {
      url: location.href,
      title: document.title,
      bodyText: document.body?.innerText?.slice(0, 8000) ?? "",
      sceneSelectCount: document.querySelectorAll("#spatial-scene-select").length,
      observerSelectCount: document.querySelectorAll("#spatial-observer-select").length,
      canvasCount: document.querySelectorAll("canvas.spatial-canvas").length,
      canvasDataset: canvas instanceof HTMLCanvasElement ? { ...canvas.dataset } : null,
    };
  }).catch(() => ({ unavailable: true }));
  await fs.writeFile(`${outDir}/${label}-failure.json`, JSON.stringify(state, null, 2));
  await page.screenshot({ path: `${outDir}/${label}-failure.png`, fullPage: true }).catch(() => {});
}

async function runPageGroup(label, page, fn) {
  attachDiagnostics(page, label);
  try {
    await fn();
  } catch (error) {
    await captureFailureState(page, label, error);
  }
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
  await button.waitFor({ state: "visible", timeout: 15000 });
  await button.click();
  const pressed = await button.getAttribute("aria-pressed");
  if (pressed !== "true") failures.push(`${name}: aria-pressed did not become true`);
  await page.waitForTimeout(180);
}

async function dragCanvas(page, canvas, dx, dy) {
  await canvas.scrollIntoViewIfNeeded();
  const box = await canvas.boundingBox();
  if (!box) return false;
  const startX = box.x + box.width * 0.52;
  const startY = box.y + box.height * 0.52;
  await page.mouse.move(startX, startY);
  await page.mouse.down();
  await page.mouse.move(startX + dx, startY + dy, { steps: 8 });
  await page.mouse.up();
  await page.waitForTimeout(180);
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
    { timeout: 20000 },
  );
}

async function openSpatial(page) {
  await page.goto(`http://127.0.0.1:4173/?view=spatial&audit=${Date.now()}`, {
    waitUntil: "domcontentloaded",
    timeout: 30000,
  });
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ state: "visible", timeout: 20000 });
  await waitForAuthoredChunk(page, 1, "c0");
  await page.locator("#spatial-scene-select").waitFor({ state: "attached", timeout: 10000 });
  return canvas;
}

async function selectScene(page, sceneId, expectedCount, expectedChunkId = null) {
  const select = page.locator("#spatial-scene-select");
  await select.waitFor({ state: "attached", timeout: 10000 });
  await select.selectOption(sceneId);
  await page.locator(`section.spatial-card[data-scene-id="${sceneId}"]`).waitFor({ state: "visible", timeout: 15000 });
  await waitForAuthoredChunk(page, expectedCount, expectedChunkId);
}

async function checkImageExperience(page, label) {
  await page.goto("http://127.0.0.1:4173/", { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.getByRole("heading", { name: /See the same image through different ways of seeing/i }).waitFor({ state: "visible" });
  await page.getByRole("button", { name: "Upload image", exact: true }).waitFor({ state: "visible" });
  await page.getByText("Original", { exact: true }).first().waitFor({ state: "visible" });
  await page.getByText("Approximation", { exact: true }).first().waitFor({ state: "visible" });
  await assertNoHorizontalOverflow(page, label);
}

const imageDesktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
await runPageGroup("image-desktop", imageDesktop, async () => {
  await checkImageExperience(imageDesktop, "image-desktop");
  await imageDesktop.screenshot({ path: `${outDir}/desktop-image-baseline.png`, fullPage: true });
});
await imageDesktop.close();

const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
await runPageGroup("spatial-desktop", desktop, async () => {
  const desktopCanvas = await openSpatial(desktop);
  await assertNoHorizontalOverflow(desktop, "spatial-desktop");
  await assertMode(desktop, "Normal");

  // Capture the current generated C0 before any scene switch. This makes the visual
  // artifact useful even if a later lifecycle check finds a real runtime failure.
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

  await assertMode(desktop, "Tunnel Vision");
  await desktop.screenshot({ path: `${outDir}/desktop-tunnel-forward.png`, fullPage: true });
  if (!(await dragCanvas(desktop, desktopCanvas, 250, -45))) {
    failures.push("spatial-desktop: canvas has no bounding box");
  } else {
    await desktop.screenshot({ path: `${outDir}/desktop-tunnel-turned.png`, fullPage: true });
  }

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

  await assertMode(desktop, "Normal");
  if (!(await dragCanvas(desktop, desktopCanvas, -500, 45))) {
    failures.push("spatial-desktop-opposite: canvas has no bounding box");
  } else {
    await desktop.screenshot({ path: `${outDir}/desktop-normal-opposite.png`, fullPage: true });
  }

  const beforeMove = await desktopCanvas.evaluate((element) => element.dataset.cameraPosition);
  await desktopCanvas.focus();
  await desktop.keyboard.down("w");
  await desktop.waitForTimeout(360);
  await desktop.keyboard.up("w");
  await desktop.waitForTimeout(180);
  const afterMove = await desktopCanvas.evaluate((element) => element.dataset.cameraPosition);
  if (!beforeMove || !afterMove || beforeMove === afterMove) failures.push("spatial-desktop: W movement did not change camera position");
  await desktop.screenshot({ path: `${outDir}/desktop-normal-moved.png`, fullPage: true });
});
await desktop.close();

const mobileContext = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 1,
  isMobile: true,
  hasTouch: true,
});

const imageMobile = await mobileContext.newPage();
await runPageGroup("image-mobile", imageMobile, async () => {
  await checkImageExperience(imageMobile, "image-mobile");
  await imageMobile.screenshot({ path: `${outDir}/mobile-image-baseline.png`, fullPage: true });
});
await imageMobile.close();

const mobile = await mobileContext.newPage();
await runPageGroup("spatial-mobile", mobile, async () => {
  const mobileCanvas = await openSpatial(mobile);
  await assertNoHorizontalOverflow(mobile, "spatial-mobile");
  await mobile.screenshot({ path: `${outDir}/mobile-normal-forward.png`, fullPage: true });
  await assertMode(mobile, "Central Loss");
  await mobile.screenshot({ path: `${outDir}/mobile-central-forward.png`, fullPage: true });

  await mobileCanvas.scrollIntoViewIfNeeded();
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
    await mobile.waitForTimeout(180);
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
});
await mobile.close();
await mobileContext.close();

// Keep scene mount/unmount/remount as an independent proof so it cannot prevent
// collection of the primary visual/movement audit above.
const lifecycle = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
await runPageGroup("spatial-lifecycle", lifecycle, async () => {
  await openSpatial(lifecycle);
  await selectScene(lifecycle, "photo-reference", 0, null);
  await lifecycle.screenshot({ path: `${outDir}/desktop-photo-reference.png`, fullPage: true });
  await assertMode(lifecycle, "Dog-like");
  await lifecycle.screenshot({ path: `${outDir}/desktop-photo-dog-like.png`, fullPage: true });
  await selectScene(lifecycle, "night-intersection", 1, "c0");
  await assertMode(lifecycle, "Normal");
  await lifecycle.screenshot({ path: `${outDir}/desktop-lifecycle-restored.png`, fullPage: true });
});
await lifecycle.close();

await browser.close();
await fs.writeFile(`${outDir}/result.json`, JSON.stringify({ ok: failures.length === 0, failures }, null, 2));
if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
