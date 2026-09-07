import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "http://127.0.0.1:4173";
const OUT = "e3-validation-v2";
await fs.mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const results = { baseUrl: BASE, desktop: {}, mobile: {}, ok: false };
const parsePosition = (value) => value.split(",").map(Number);
const position = async (canvas) => parsePosition(await canvas.getAttribute("data-camera-position"));

const holdKey = async (page, key, ms, extra = []) => {
  for (const modifier of extra) await page.keyboard.down(modifier);
  await page.keyboard.down(key);
  await page.waitForTimeout(ms);
  await page.keyboard.up(key);
  for (const modifier of [...extra].reverse()) await page.keyboard.up(modifier);
  await page.waitForTimeout(80);
};

try {
  {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(`page:${error.message}`));
    page.on("console", (msg) => { if (msg.type() === "error") errors.push(`console:${msg.text()}`); });
    await page.goto(`${BASE}/?view=spatial&e3_validation_v2=${Date.now()}`, { waitUntil: "networkidle", timeout: 60000 });
    const canvas = page.locator("canvas.spatial-canvas");
    await canvas.waitFor({ timeout: 30000 });
    await canvas.focus();
    assert.equal(await canvas.getAttribute("data-observer-movement"), "bounded-ground");
    assert.equal(await canvas.getAttribute("data-camera-position"), "0.000,0.000,0.000");

    // Speed comparison from identical canonical start.
    await holdKey(page, "w", 650);
    const normal = await position(canvas);
    const normalDistance = Math.hypot(normal[0], normal[2]);
    await page.getByRole("button", { name: "Reset observer", exact: true }).click();
    await page.waitForTimeout(120);
    await canvas.focus();
    await holdKey(page, "w", 650, ["Shift"]);
    const fast = await position(canvas);
    const fastDistance = Math.hypot(fast[0], fast[2]);
    assert(normalDistance > 0.45, `normal movement too small: ${normalDistance}`);
    assert(fastDistance > normalDistance * 1.35, `Shift speed not materially faster: normal=${normalDistance} fast=${fastDistance}`);

    // Collision: six controlled left taps align near x=-4.5; repeated forward taps must stop at the near car.
    await page.getByRole("button", { name: "Reset observer", exact: true }).click();
    await page.waitForTimeout(120);
    await canvas.focus();
    for (let i = 0; i < 6; i += 1) await holdKey(page, "a", 250);
    const aligned = await position(canvas);
    assert(aligned[0] < -3.4 && aligned[0] > -5.6, `failed to align with near car: ${aligned}`);
    let previousZ = aligned[2];
    let stableCount = 0;
    for (let i = 0; i < 18; i += 1) {
      await holdKey(page, "w", 250);
      const current = await position(canvas);
      if (Math.abs(current[2] - previousZ) < 0.03) stableCount += 1;
      else stableCount = 0;
      previousZ = current[2];
      if (stableCount >= 2) break;
    }
    const carStop = await position(canvas);
    assert(carStop[2] > -9.2, `observer passed through near-car collision: ${carStop}`);
    assert(carStop[2] < -6.0, `observer did not approach near car: ${carStop}`);
    assert(stableCount >= 2, `near-car collision did not produce a stable stop: ${carStop}`);

    // Outer navigation bound: repeated fast right taps from reset must stop around x=15.94.
    await page.getByRole("button", { name: "Reset observer", exact: true }).click();
    await page.waitForTimeout(120);
    await canvas.focus();
    let boundStable = 0;
    let previousX = 0;
    for (let i = 0; i < 20; i += 1) {
      await holdKey(page, "d", 250, ["Shift"]);
      const current = await position(canvas);
      if (Math.abs(current[0] - previousX) < 0.03) boundStable += 1;
      else boundStable = 0;
      previousX = current[0];
      if (boundStable >= 2) break;
    }
    const boundStop = await position(canvas);
    assert(boundStop[0] <= 16.0 && boundStop[0] >= 15.0, `east navigation bound failed: ${boundStop}`);
    assert(boundStable >= 2, `east navigation bound did not produce a stable stop: ${boundStop}`);

    // R reset semantics.
    await canvas.focus();
    await page.keyboard.press("r");
    await page.waitForTimeout(120);
    assert.equal(await canvas.getAttribute("data-camera-position"), "0.000,0.000,0.000");
    assert.equal(await canvas.getAttribute("data-camera-viewpoint"), "baseline");
    assert.equal(await canvas.getAttribute("data-camera-yaw"), "0.000000");
    assert.equal(await canvas.getAttribute("data-camera-pitch"), "-0.010000");
    assert.equal(await canvas.getAttribute("data-camera-fov"), "52.000");

    // Photo Reference stays look-only and ignores W translation.
    await page.locator("#spatial-scene-select").selectOption("photo-reference");
    await page.waitForTimeout(900);
    assert.equal(await canvas.getAttribute("data-observer-movement"), "look-only");
    assert.equal(await page.getByRole("group", { name: "Mobile movement" }).count(), 0);
    const photoBefore = await canvas.getAttribute("data-camera-position");
    await canvas.focus();
    await holdKey(page, "w", 650);
    const photoAfter = await canvas.getAttribute("data-camera-position");
    assert.equal(photoAfter, photoBefore, `Photo Reference translated on W: ${photoBefore} -> ${photoAfter}`);

    await page.screenshot({ path: path.join(OUT, "desktop-e3.png"), fullPage: true });
    assert.deepEqual(errors, [], `desktop browser errors: ${errors.join(" | ")}`);
    results.desktop = { normalDistance, fastDistance, aligned, carStop, stableCount, boundStop, boundStable, photoBefore, photoAfter, errors };
    await context.close();
  }

  {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(`page:${error.message}`));
    page.on("console", (msg) => { if (msg.type() === "error") errors.push(`console:${msg.text()}`); });
    await page.goto(`${BASE}/?view=spatial&e3_mobile_validation_v2=${Date.now()}`, { waitUntil: "networkidle", timeout: 60000 });
    const canvas = page.locator("canvas.spatial-canvas");
    await canvas.waitFor({ timeout: 30000 });
    const group = page.getByRole("group", { name: "Mobile movement" });
    assert.equal(await group.count(), 1);
    const buttons = group.getByRole("button");
    assert.equal(await buttons.count(), 4);
    for (let i = 0; i < 4; i += 1) {
      const box = await buttons.nth(i).boundingBox();
      assert(box && box.width >= 44 && box.height >= 44, `mobile move target too small: ${JSON.stringify(box)}`);
    }
    const before = await canvas.getAttribute("data-camera-position");
    const forward = page.getByRole("button", { name: "Move forward", exact: true });
    await forward.dispatchEvent("pointerdown", { pointerId: 91, pointerType: "touch", isPrimary: true });
    await page.waitForTimeout(650);
    await forward.dispatchEvent("pointerup", { pointerId: 91, pointerType: "touch", isPrimary: true });
    await page.waitForTimeout(120);
    const after = await canvas.getAttribute("data-camera-position");
    assert.notEqual(after, before, "mobile forward control did not move observer");
    assert.equal(await canvas.getAttribute("data-camera-viewpoint"), "free");
    await page.getByRole("button", { name: "Reset observer", exact: true }).click();
    await page.waitForTimeout(120);
    assert.equal(await canvas.getAttribute("data-camera-position"), "0.000,0.000,0.000");
    const bodyWidth = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }));
    assert(bodyWidth.scrollWidth <= bodyWidth.clientWidth + 1, `mobile horizontal overflow: ${JSON.stringify(bodyWidth)}`);
    await page.screenshot({ path: path.join(OUT, "mobile-e3.png"), fullPage: true });
    assert.deepEqual(errors, [], `mobile browser errors: ${errors.join(" | ")}`);
    results.mobile = { before, after, bodyWidth, errors };
    await context.close();
  }

  results.ok = true;
} finally {
  await browser.close();
  await fs.writeFile(path.join(OUT, "e3-validation.json"), JSON.stringify(results, null, 2));
}

console.log(JSON.stringify(results, null, 2));