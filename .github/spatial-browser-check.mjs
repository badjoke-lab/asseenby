import fs from "node:fs/promises";
import { chromium } from "playwright";

const BASE = process.env.ASSEENBY_PREVIEW_URL || "http://127.0.0.1:4173";
const OUT = "browser-check";
await fs.rm(OUT, { recursive: true, force: true });
await fs.mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const failures = [];

function attachDiagnostics(page, label) {
  page.on("pageerror", (error) => failures.push(`${label} pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") failures.push(`${label} console: ${message.text()}`);
  });
  page.on("crash", () => failures.push(`${label}: page crashed`));
}

async function readCanvas(page) {
  return page.evaluate(() => {
    const canvas = document.querySelector("canvas.spatial-canvas");
    if (!(canvas instanceof HTMLCanvasElement)) return null;
    const rect = canvas.getBoundingClientRect();
    return {
      scene: canvas.dataset.sceneId ?? null,
      observer: canvas.dataset.observerId ?? null,
      roots: canvas.dataset.sceneAuthoredAssetRootCount ?? null,
      chunks: canvas.dataset.sceneLoadedChunks ?? null,
      movement: canvas.dataset.observerMovement ?? null,
      yaw: canvas.dataset.cameraYaw ?? null,
      pitch: canvas.dataset.cameraPitch ?? null,
      position: canvas.dataset.cameraPosition ?? null,
      width: rect.width,
      height: rect.height,
      x: rect.x,
      y: rect.y,
    };
  });
}

async function waitForState(page, predicateSource, timeout = 30000) {
  await page.waitForFunction(
    ({ predicateSource }) => {
      const canvas = document.querySelector("canvas.spatial-canvas");
      if (!(canvas instanceof HTMLCanvasElement)) return false;
      const state = {
        scene: canvas.dataset.sceneId ?? "",
        observer: canvas.dataset.observerId ?? "",
        roots: canvas.dataset.sceneAuthoredAssetRootCount ?? "",
        chunks: canvas.dataset.sceneLoadedChunks ?? "",
        movement: canvas.dataset.observerMovement ?? "",
        yaw: canvas.dataset.cameraYaw ?? "",
        position: canvas.dataset.cameraPosition ?? "",
        width: canvas.clientWidth,
        height: canvas.clientHeight,
      };
      return Function("state", `return (${predicateSource})(state)`)(state);
    },
    { predicateSource },
    { timeout },
  );
  await page.waitForTimeout(500);
  return readCanvas(page);
}

async function openGeometry(page) {
  await page.goto(`${BASE}/?view=spatial&audit=${Date.now()}`, {
    waitUntil: "domcontentloaded",
    timeout: 60000,
  });
  return waitForState(
    page,
    `(s) => s.scene === "night-intersection" && s.observer === "human" && s.roots === "1" && s.chunks.split(",").includes("c0") && s.movement === "bounded-ground" && s.width > 0 && s.height > 0`,
  );
}

async function setVision(page, name) {
  const button = page.getByRole("button", { name, exact: true });
  await button.waitFor({ state: "visible", timeout: 15000 });
  await button.click();
  await page.waitForFunction(
    (label) => {
      const button = [...document.querySelectorAll("button")].find((node) => node.textContent?.trim() === label);
      return button?.getAttribute("aria-pressed") === "true";
    },
    name,
    { timeout: 10000 },
  );
  await page.waitForTimeout(180);
}

async function setScene(page, sceneId) {
  await page.waitForFunction(() => document.querySelector("#spatial-scene-select") instanceof HTMLSelectElement, undefined, { timeout: 15000 });
  await page.evaluate((nextSceneId) => {
    const select = document.querySelector("#spatial-scene-select");
    if (!(select instanceof HTMLSelectElement)) throw new Error("Scene select missing");
    select.value = nextSceneId;
    select.dispatchEvent(new Event("change", { bubbles: true }));
  }, sceneId);
  if (sceneId === "night-intersection") {
    return waitForState(page, `(s) => s.scene === "night-intersection" && s.roots === "1" && s.chunks.split(",").includes("c0")`, 30000);
  }
  return waitForState(page, `(s) => s.scene === "photo-reference" && s.roots === "0"`, 20000);
}

async function dragDesktop(page, dx, dy) {
  const state = await readCanvas(page);
  if (!state || state.width <= 0 || state.height <= 0) throw new Error("desktop canvas has no usable box");
  const sx = state.x + state.width * 0.52;
  const sy = state.y + state.height * 0.52;
  await page.mouse.move(sx, sy);
  await page.mouse.down();
  await page.mouse.move(sx + dx, sy + dy, { steps: 14 });
  await page.mouse.up();
  await page.waitForTimeout(250);
  return readCanvas(page);
}

async function touchTurn(page) {
  const state = await readCanvas(page);
  if (!state || state.width <= 0 || state.height <= 0) throw new Error("mobile canvas has no usable box");
  const session = await page.context().newCDPSession(page);
  const sx = state.x + state.width * 0.52;
  const sy = state.y + state.height * 0.52;
  await session.send("Input.dispatchTouchEvent", {
    type: "touchStart",
    touchPoints: [{ x: sx, y: sy, radiusX: 2, radiusY: 2, force: 1, id: 1 }],
  });
  for (let step = 1; step <= 8; step += 1) {
    await session.send("Input.dispatchTouchEvent", {
      type: "touchMove",
      touchPoints: [{ x: sx + step * 12, y: sy - step * 3, radiusX: 2, radiusY: 2, force: 1, id: 1 }],
    });
  }
  await session.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await page.waitForTimeout(250);
  return readCanvas(page);
}

async function verifyNoHorizontalOverflow(page, label) {
  const dims = await page.evaluate(() => ({
    client: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  if (dims.scroll > dims.client + 1) failures.push(`${label}: horizontal overflow ${dims.scroll} > ${dims.client}`);
}

async function run(label, page, fn) {
  attachDiagnostics(page, label);
  try {
    await fn();
  } catch (error) {
    failures.push(`${label}: ${error instanceof Error ? error.message : String(error)}`);
    await page.screenshot({ path: `${OUT}/${label}-failure.png`, fullPage: true }).catch(() => {});
    const state = await readCanvas(page).catch(() => null);
    await fs.writeFile(`${OUT}/${label}-failure.json`, JSON.stringify(state, null, 2)).catch(() => {});
  }
}

const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
await run("desktop", desktop, async () => {
  const initial = await openGeometry(desktop);
  if (!initial) throw new Error("initial geometry state unavailable");
  await verifyNoHorizontalOverflow(desktop, "desktop");

  await setVision(desktop, "Normal");
  await desktop.screenshot({ path: `${OUT}/desktop-normal-forward.png`, fullPage: true });
  await setVision(desktop, "Night / Low Light");
  await desktop.screenshot({ path: `${OUT}/desktop-night-forward.png`, fullPage: true });
  await setVision(desktop, "Central Loss");
  await desktop.screenshot({ path: `${OUT}/desktop-central-forward.png`, fullPage: true });
  await setVision(desktop, "Cataract-like");
  await desktop.screenshot({ path: `${OUT}/desktop-cataract-forward.png`, fullPage: true });
  await setVision(desktop, "Normal");

  const turned = await dragDesktop(desktop, 290, -35);
  if (!turned || turned.yaw === initial.yaw) failures.push("desktop: drag did not change camera yaw");
  await desktop.screenshot({ path: `${OUT}/desktop-normal-turned.png`, fullPage: true });

  const opposite = await dragDesktop(desktop, -560, 30);
  if (!opposite || opposite.yaw === turned?.yaw) failures.push("desktop: second drag did not change camera yaw");
  await desktop.screenshot({ path: `${OUT}/desktop-normal-opposite.png`, fullPage: true });

  const beforeMove = opposite?.position;
  await desktop.evaluate(() => document.querySelector("canvas.spatial-canvas")?.focus());
  await desktop.keyboard.down("w");
  await desktop.waitForTimeout(700);
  await desktop.keyboard.up("w");
  await desktop.waitForTimeout(250);
  const moved = await readCanvas(desktop);
  if (!moved || !beforeMove || moved.position === beforeMove) failures.push("desktop: W movement did not change camera position");
  await desktop.screenshot({ path: `${OUT}/desktop-normal-moved.png`, fullPage: true });

  await setScene(desktop, "photo-reference");
  await desktop.screenshot({ path: `${OUT}/desktop-photo-reference.png`, fullPage: true });
  const restored = await setScene(desktop, "night-intersection");
  if (!restored || restored.roots !== "1") failures.push("desktop: geometry did not remount after scene lifecycle switch");
  await desktop.screenshot({ path: `${OUT}/desktop-lifecycle-restored.png`, fullPage: true });
});
await desktop.close();

const mobileContext = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 1,
  isMobile: true,
  hasTouch: true,
});
const mobile = await mobileContext.newPage();
await run("mobile", mobile, async () => {
  const initial = await openGeometry(mobile);
  if (!initial) throw new Error("initial mobile geometry state unavailable");
  await verifyNoHorizontalOverflow(mobile, "mobile");
  await setVision(mobile, "Normal");
  await mobile.screenshot({ path: `${OUT}/mobile-normal-forward.png`, fullPage: true });
  const turned = await touchTurn(mobile);
  if (!turned || turned.yaw === initial.yaw) failures.push("mobile: touch did not change camera yaw");
  await mobile.screenshot({ path: `${OUT}/mobile-normal-turned.png`, fullPage: true });
});
await mobile.close();
await mobileContext.close();

await browser.close();
await fs.writeFile(`${OUT}/result.json`, JSON.stringify({ ok: failures.length === 0, failures }, null, 2));
if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
console.log("spatial browser check passed");
