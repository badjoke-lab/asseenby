import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { chromium } from "playwright";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "http://127.0.0.1:4173";
const browser = await chromium.launch({ headless: true });
const result = { before: null, after: null, events: [], movement: null, viewpoint: null, errors: [] };
try {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  page.on("pageerror", (error) => result.errors.push(`page:${error.message}`));
  page.on("console", (msg) => { if (msg.type() === "error") result.errors.push(`console:${msg.text()}`); });
  await page.goto(`${BASE}/?view=spatial&e3_mobile_probe=${Date.now()}`, { waitUntil: "networkidle", timeout: 60000 });
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30000 });
  const button = page.getByRole("button", { name: "Move forward", exact: true });
  await button.waitFor();
  await button.evaluate((element) => {
    window.__e3MobileProbe = [];
    for (const type of ["touchstart", "touchend", "pointerdown", "pointerup", "pointercancel", "lostpointercapture"]) {
      element.addEventListener(type, (event) => window.__e3MobileProbe.push({ type, pointerId: event.pointerId ?? null }));
    }
  });
  const box = await button.boundingBox();
  assert(box, "Move forward has no bounding box");
  result.before = await canvas.getAttribute("data-camera-position");
  const cdp = await context.newCDPSession(page);
  const x = box.x + box.width / 2;
  const y = box.y + box.height / 2;
  await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y, id: 41, radiusX: 4, radiusY: 4, force: 1 }] });
  await page.waitForTimeout(700);
  await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await page.waitForTimeout(150);
  result.after = await canvas.getAttribute("data-camera-position");
  result.movement = await canvas.getAttribute("data-observer-movement");
  result.viewpoint = await canvas.getAttribute("data-camera-viewpoint");
  result.events = await page.evaluate(() => window.__e3MobileProbe || []);
  assert.notEqual(result.after, result.before, `mobile did not move: ${JSON.stringify(result)}`);
  assert.equal(result.movement, "bounded-ground");
  assert.equal(result.viewpoint, "free");
  assert.deepEqual(result.errors, []);
  await context.close();
} finally {
  await browser.close();
  await fs.mkdir("e3-mobile-probe", { recursive: true });
  await fs.writeFile("e3-mobile-probe/result.json", JSON.stringify(result, null, 2));
}
console.log(JSON.stringify(result, null, 2));