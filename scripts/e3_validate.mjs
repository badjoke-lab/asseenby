import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "http://127.0.0.1:4173";
const OUT = "e3-validation";
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
  await page.waitForTimeout(100);
};

try {
  {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(`page:${error.message}`));
    page.on("console", (msg) => { if (msg.type() === "error") errors.push(`console:${msg.text()}`); });
    await page.goto(`${BASE}/?view=spatial&e3_validation=${Date.now()}`, { waitUntil: "networkidle", timeout: 60000 });
    const canvas = page.locator("canvas.spatial-canvas");
    await canvas.waitFor({ timeout: 30000 });
    await canvas.focus();
    assert.equal(await canvas.getAttribute("data-observer-movement"), "bounded-ground");
    assert.equal(await canvas.getAttribute("data-camera-position"), "0.000,0.000,0.000");

    // Normal vs Shift speed from the same canonical start.
    await holdKey(page, "w", 650);
    const normal = await position(canvas);
    const normalDistance = Math.hypot(normal[0], normal[2]);
    await page.getByRole("button", { name: "Reset observer", exact: true }).click();
    await page.waitForTimeout(120);
    await canvas.focus();
    await holdKey(page, "w", 650, ["Shift"]);
    const fast = await position(canvas);
    const fastDistance = Math.hypot(fast[0], fast[2]);
    assert(normalDistance > 0.8, `normal movement too small: ${normalDistance}`);
    assert(fastDistance > normalDistance * 1.35, `Shift speed not materially faster: normal=${normalDistance} fast=${fastDistance}`);

    // Collision: align with the near car at x≈-4.6, then walk toward it.
    await page.getByRole("button", { name: "Reset observer", exact: true }).click();
    await page.waitForTimeout(120);
    await canvas.focus();
    await holdKey(page, "a", 1650);
    const aligned = await position(canvas);
    assert(aligned[0] < -3.8 && aligned[0] > -5.4, `failed to align with near car: ${aligned}`);
    await holdKey(page, "w", 4800);
    const carStop = await position(canvas);
    assert(carStop[2] > -9.2, `observer passed through near-car collision: ${carStop}`);
    assert(carStop[2] < -6.0, `observer did not approach near car: ${carStop}`);

    // Navigation bound: strafe from reset until the east edge; x must remain inside ~15.94.
    await page.getByRole("button", { name: "Reset observer", exact: true }).click();
    await page.waitForTimeout(120);
    await canvas.focus();
    await holdKey(page, "d", 4200, ["Shift"]);
    const boundStop = await position(canvas);
    assert(boundStop[0] <= 16.0 && boundStop[0] >= 15.0, `east navigation bound failed: ${boundStop}`);

    // R reset semantics.
    await canvas.focus();
    await page.keyboard.press("r");
    await page.waitForTimeout(120);
    assert.equal(await canvas.getAttribute("data-camera-position"), "0.000,0.000,0.000");
    assert.equal(await canvas.getAttribute("data-camera-viewpoint"), "baseline");
    assert.equal(await canvas.getAttribute("data-camera-yaw"), "0.000000");
    assert.equal(await canvas.getAttribute("data-camera-pitch"), "-0.010000");
    assert.equal(await canvas.getAttribute("data-camera-fov"), "52.000");

    // Photo Reference remains look-only and does not translate on W.
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
    results.desktop = { normalDistance, fastDistance, aligned, carStop, boundStop, photoBefore, photoAfter, errors };
    await context.close();
  }

  {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(`page:${error.message}`));
    page.on("console", (msg) => { if (msg.type() === "error") errors.push(`console:${msg.text()}`); });
    await page.goto(`${BASE}/?view=spatial&e3_mobile_validation=${Date.now()}`, { waitUntil: "networkidle", timeout: 60000 });
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