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

const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
await attachDiagnostics(desktop, "desktop");
await desktop.goto("http://127.0.0.1:4173/?view=spatial", { waitUntil: "networkidle" });
const desktopCanvas = desktop.locator("canvas.spatial-canvas");
await desktopCanvas.waitFor({ state: "visible" });
await assertNoHorizontalOverflow(desktop, "desktop");

// Forward-view comparison: same camera, only the perception renderer changes.
await desktop.screenshot({ path: `${outDir}/desktop-normal-forward.png`, fullPage: true });
await assertMode(desktop, "Cataract-like");
await desktop.screenshot({ path: `${outDir}/desktop-cataract-forward.png`, fullPage: true });
await assertMode(desktop, "Normal");

// Tunnel Vision remains live and view-relative while the camera direction changes.
await assertMode(desktop, "Tunnel Vision");
await desktop.screenshot({ path: `${outDir}/desktop-tunnel-forward.png`, fullPage: true });
if (!(await dragCanvas(desktop, desktopCanvas, 250, -45))) {
  failures.push("desktop: canvas has no bounding box");
} else {
  await desktop.screenshot({ path: `${outDir}/desktop-tunnel-turned.png`, fullPage: true });
}

// Turned-view comparison: preserve that exact camera direction across modes.
await assertMode(desktop, "Normal");
await desktop.screenshot({ path: `${outDir}/desktop-normal-turned.png`, fullPage: true });
await assertMode(desktop, "Cataract-like");
await desktop.screenshot({ path: `${outDir}/desktop-cataract-turned.png`, fullPage: true });

const mobileContext = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 1,
  isMobile: true,
  hasTouch: true,
});
const mobile = await mobileContext.newPage();
await attachDiagnostics(mobile, "mobile");
await mobile.goto("http://127.0.0.1:4173/?view=spatial", { waitUntil: "networkidle" });
const mobileCanvas = mobile.locator("canvas.spatial-canvas");
await mobileCanvas.waitFor({ state: "visible" });
await assertNoHorizontalOverflow(mobile, "mobile");

await mobile.screenshot({ path: `${outDir}/mobile-normal-forward.png`, fullPage: true });
await assertMode(mobile, "Cataract-like");
await mobile.screenshot({ path: `${outDir}/mobile-cataract-forward.png`, fullPage: true });
await assertMode(mobile, "Tunnel Vision");

const mobileBox = await mobileCanvas.boundingBox();
if (!mobileBox) {
  failures.push("mobile: canvas has no bounding box");
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
await mobile.screenshot({ path: `${outDir}/mobile-tunnel-turned.png`, fullPage: true });
await assertMode(mobile, "Normal");
await mobile.screenshot({ path: `${outDir}/mobile-normal-turned.png`, fullPage: true });
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
