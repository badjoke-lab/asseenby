import fs from "node:fs/promises";
import { chromium } from "playwright";

const outDir = "browser-check";
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
const failures = [];

page.on("pageerror", (error) => failures.push(`pageerror: ${error.message}`));
page.on("console", (message) => {
  if (message.type() === "error") failures.push(`console: ${message.text()}`);
});

await page.goto("http://127.0.0.1:4173/?view=spatial", { waitUntil: "networkidle" });
const canvas = page.locator("canvas.spatial-canvas");
await canvas.waitFor({ state: "visible" });
await page.waitForFunction(() => {
  const element = document.querySelector("canvas.spatial-canvas");
  return element instanceof HTMLCanvasElement
    && element.dataset.sceneLoadedChunks?.split(",").includes("c0")
    && Number(element.dataset.sceneAuthoredAssetRootCount ?? 0) >= 1;
}, null, { timeout: 20000 });

await canvas.scrollIntoViewIfNeeded();
await page.waitForTimeout(120);

const readState = () => page.evaluate(() => {
  const element = document.querySelector("canvas.spatial-canvas");
  if (!(element instanceof HTMLCanvasElement)) return null;
  return {
    yaw: Number(element.dataset.cameraYaw ?? "NaN"),
    pitch: Number(element.dataset.cameraPitch ?? "NaN"),
    position: (element.dataset.cameraPosition ?? "").split(",").map(Number),
  };
});

async function drag(dx, dy) {
  await canvas.scrollIntoViewIfNeeded();
  const box = await canvas.boundingBox();
  if (!box) throw new Error("canvas has no bounding box");
  const x = box.x + box.width * 0.5;
  const y = box.y + box.height * 0.5;
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x + dx, y + dy, { steps: 10 });
  await page.mouse.up();
  await page.waitForTimeout(180);
}

const baseline = await readState();
await page.screenshot({ path: `${outDir}/desktop-c0-verified-forward.png`, fullPage: true });

await drag(230, -35);
const turned = await readState();
if (!baseline || !turned || !Number.isFinite(baseline.yaw) || !Number.isFinite(turned.yaw)) {
  failures.push("camera yaw diagnostics unavailable");
} else if (Math.abs(turned.yaw - baseline.yaw) < 0.25) {
  failures.push(`mouse drag did not materially change yaw: ${baseline.yaw} -> ${turned.yaw}`);
}
await page.screenshot({ path: `${outDir}/desktop-c0-verified-turned.png`, fullPage: true });

await canvas.focus();
const beforeMove = await readState();
await page.keyboard.down("w");
await page.waitForTimeout(700);
await page.keyboard.up("w");
await page.waitForTimeout(180);
const afterMove = await readState();
if (!beforeMove || !afterMove || beforeMove.position.length !== 3 || afterMove.position.length !== 3) {
  failures.push("camera position diagnostics unavailable");
} else {
  const distance = Math.hypot(
    afterMove.position[0] - beforeMove.position[0],
    afterMove.position[2] - beforeMove.position[2],
  );
  if (distance < 0.4) failures.push(`W movement did not materially translate observer: ${distance.toFixed(3)}m`);
}
await page.screenshot({ path: `${outDir}/desktop-c0-verified-moved.png`, fullPage: true });

await drag(-520, 25);
const opposite = await readState();
if (turned && opposite && Number.isFinite(turned.yaw) && Number.isFinite(opposite.yaw)
    && Math.abs(opposite.yaw - turned.yaw) < 0.5) {
  failures.push(`opposite sweep did not materially change yaw: ${turned.yaw} -> ${opposite.yaw}`);
}
await page.screenshot({ path: `${outDir}/desktop-c0-verified-opposite.png`, fullPage: true });

await fs.writeFile(
  `${outDir}/turn-result.json`,
  JSON.stringify({ ok: failures.length === 0, failures, baseline, turned, beforeMove, afterMove, opposite }, null, 2),
);
await browser.close();

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
