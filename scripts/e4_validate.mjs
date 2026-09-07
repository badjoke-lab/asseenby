import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";
import { PNG } from "pngjs";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "http://127.0.0.1:4173";
const OUT = path.resolve("e4-validation");
const GEOMETRY_LABELS = ["Normal", "Tunnel Vision", "Central Loss", "Night / Low Light", "Cataract-like"];
const PHOTO_LABELS = ["Normal", "Tunnel Vision", "Central Loss", "Night / Low Light", "Dog-like", "Cataract-like"];
const MODE_IDS = {
  "Normal": "normal",
  "Tunnel Vision": "tunnel",
  "Central Loss": "central_loss",
  "Night / Low Light": "night",
  "Cataract-like": "cataract",
};

await fs.mkdir(OUT, { recursive: true });
const result = { desktop: {}, mobile: {}, metrics: {}, errors: [], ok: false };
const browser = await chromium.launch({ headless: true });

function collectErrors(page, label) {
  page.on("pageerror", (error) => result.errors.push(`${label}:page:${error.message}`));
  page.on("console", (msg) => { if (msg.type() === "error") result.errors.push(`${label}:console:${msg.text()}`); });
}

function cameraStateObject(element) {
  return {
    scene: element.dataset.sceneId,
    observer: element.dataset.observerId,
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    viewpoint: element.dataset.cameraViewpoint,
  };
}

function assertSameCamera(before, after, label) {
  for (const key of ["scene", "observer", "position", "yaw", "pitch", "fov", "viewpoint"]) {
    assert.equal(after[key], before[key], `${label}: Vision changed ${key}: ${before[key]} -> ${after[key]}`);
  }
}

function decode(buffer) {
  return PNG.sync.read(buffer);
}

function luma(r, g, b) {
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function quantile(values, q) {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.max(0, Math.min(sorted.length - 1, Math.floor((sorted.length - 1) * q)))];
}

function comparePng(normalBuffer, modeBuffer) {
  const a = decode(normalBuffer);
  const b = decode(modeBuffer);
  assert.equal(a.width, b.width);
  assert.equal(a.height, b.height);
  const aspect = a.width / a.height;
  let centerSum = 0, centerN = 0, edgeSum = 0, edgeN = 0;
  const pixels = [];
  for (let y = 0; y < a.height; y += 1) {
    for (let x = 0; x < a.width; x += 1) {
      const i = (y * a.width + x) * 4;
      const ar = a.data[i], ag = a.data[i + 1], ab = a.data[i + 2];
      const br = b.data[i], bg = b.data[i + 1], bb = b.data[i + 2];
      const delta = (Math.abs(ar - br) + Math.abs(ag - bg) + Math.abs(ab - bb)) / 3;
      const nx = ((x + 0.5) / a.width - 0.5) * aspect;
      const ny = (y + 0.5) / a.height - 0.5;
      const radius = Math.hypot(nx, ny);
      if (radius < 0.12) { centerSum += delta; centerN += 1; }
      if (radius > 0.42) { edgeSum += delta; edgeN += 1; }
      const baseLuma = luma(ar, ag, ab);
      pixels.push({ baseLuma, delta, relDelta: delta / (baseLuma + 18) });
    }
  }
  const lumas = pixels.map((p) => p.baseLuma);
  const q30 = quantile(lumas, 0.30);
  const q45 = quantile(lumas, 0.45);
  const q70 = quantile(lumas, 0.70);
  const q82 = quantile(lumas, 0.82);
  const mean = (arr, key) => arr.reduce((sum, item) => sum + item[key], 0) / Math.max(1, arr.length);
  const dark = pixels.filter((p) => p.baseLuma <= q30);
  const bright = pixels.filter((p) => p.baseLuma >= q82);
  const mid = pixels.filter((p) => p.baseLuma >= q45 && p.baseLuma <= q70);
  return {
    width: a.width,
    height: a.height,
    centerDelta: centerSum / Math.max(1, centerN),
    edgeDelta: edgeSum / Math.max(1, edgeN),
    darkRelativeDelta: mean(dark, "relDelta"),
    brightRelativeDelta: mean(bright, "relDelta"),
    brightDelta: mean(bright, "delta"),
    midDelta: mean(mid, "delta"),
    lumaQuantiles: { q30, q45, q70, q82 },
  };
}

async function desktopValidation() {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  collectErrors(page, "desktop");
  await page.goto(`${BASE}/?view=spatial&e4_validate=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30_000 });
  await page.waitForTimeout(450);
  const group = page.getByRole("group", { name: "Vision" });
  assert.deepEqual(await group.getByRole("button").allTextContents(), GEOMETRY_LABELS);
  assert.equal((await group.getByRole("button", { name: "Dog-like", exact: true }).count()), 0, "Dog-like leaked into Human geometry Vision");
  const baselineState = await canvas.evaluate(cameraStateObject);
  assert.equal(baselineState.scene, "night-intersection");
  assert.equal(baselineState.observer, "human");
  assert.equal(await canvas.getAttribute("data-observer-movement"), "bounded-ground");

  const captures = {};
  for (const label of GEOMETRY_LABELS) {
    const button = group.getByRole("button", { name: label, exact: true });
    await button.click();
    await page.waitForTimeout(140);
    assert.equal(await canvas.getAttribute("data-vision-mode"), MODE_IDS[label]);
    const state = await canvas.evaluate(cameraStateObject);
    assertSameCamera(baselineState, state, `desktop baseline ${label}`);
    captures[label] = await canvas.screenshot({ path: path.join(OUT, `desktop-${MODE_IDS[label]}.png`) });
  }
  assert(!captures["Normal"].equals(captures["Tunnel Vision"]), "Tunnel rendered output equals Normal");
  assert(!captures["Normal"].equals(captures["Central Loss"]), "Central rendered output equals Normal");
  assert(!captures["Normal"].equals(captures["Night / Low Light"]), "Night rendered output equals Normal");
  assert(!captures["Normal"].equals(captures["Cataract-like"]), "Cataract rendered output equals Normal");

  result.metrics.tunnel = comparePng(captures["Normal"], captures["Tunnel Vision"]);
  result.metrics.central = comparePng(captures["Normal"], captures["Central Loss"]);
  result.metrics.night = comparePng(captures["Normal"], captures["Night / Low Light"]);
  result.metrics.cataract = comparePng(captures["Normal"], captures["Cataract-like"]);

  assert(result.metrics.tunnel.edgeDelta > result.metrics.tunnel.centerDelta + 8, `Tunnel is not edge-dominant: ${JSON.stringify(result.metrics.tunnel)}`);
  assert(result.metrics.central.centerDelta > result.metrics.central.edgeDelta + 5, `Central Loss is not center-dominant: ${JSON.stringify(result.metrics.central)}`);
  assert(result.metrics.night.darkRelativeDelta > result.metrics.night.brightRelativeDelta * 1.03, `Night does not respond more strongly in darker regions: ${JSON.stringify(result.metrics.night)}`);
  assert(result.metrics.cataract.brightDelta > result.metrics.cataract.midDelta * 1.03, `Cataract does not respond more strongly around high-luminance content: ${JSON.stringify(result.metrics.cataract)}`);

  await group.getByRole("button", { name: "Night / Low Light", exact: true }).click();
  await page.locator(".evidence-card__title").filter({ hasText: "Night / Low Light" }).waitFor({ timeout: 5_000 });
  assert((await page.locator(".evidence-card__title").filter({ hasText: "Night / Low Light" }).count()) === 1, "Night spatial Evidence panel missing");

  // Free movement, then switch every Human geometry Vision without moving/resetting the observer.
  await group.getByRole("button", { name: "Normal", exact: true }).click();
  await canvas.focus();
  const beforeMove = await canvas.getAttribute("data-camera-position");
  await page.keyboard.down("w");
  await page.waitForTimeout(360);
  await page.keyboard.up("w");
  await page.waitForTimeout(120);
  const freeState = await canvas.evaluate(cameraStateObject);
  assert.notEqual(freeState.position, beforeMove, "desktop free movement did not translate camera");
  assert.equal(freeState.viewpoint, "free");
  for (const label of GEOMETRY_LABELS.slice(1)) {
    await group.getByRole("button", { name: label, exact: true }).click();
    await page.waitForTimeout(100);
    const state = await canvas.evaluate(cameraStateObject);
    assertSameCamera(freeState, state, `desktop free ${label}`);
  }
  assert.equal(await canvas.getAttribute("data-vision-mode"), "cataract");
  await page.getByRole("button", { name: "Reset observer", exact: true }).click();
  await page.waitForTimeout(120);
  assert.equal(await canvas.getAttribute("data-camera-position"), "0.000,0.000,0.000");
  assert.equal(await canvas.getAttribute("data-vision-mode"), "cataract", "Reset changed selected Vision");

  // Photo Reference keeps its accepted six-mode set including Dog-like.
  await page.locator("#spatial-scene-select").selectOption("photo-reference");
  await page.waitForTimeout(700);
  assert.deepEqual(await group.getByRole("button").allTextContents(), PHOTO_LABELS);
  assert.equal(await canvas.getAttribute("data-scene-supports-translation"), "false");
  const photoBefore = await canvas.getAttribute("data-camera-position");
  await canvas.focus();
  await page.keyboard.down("w");
  await page.waitForTimeout(260);
  await page.keyboard.up("w");
  await page.waitForTimeout(100);
  assert.equal(await canvas.getAttribute("data-camera-position"), photoBefore, "Photo Reference translated under W input");

  result.desktop = { geometryLabels: GEOMETRY_LABELS, photoLabels: PHOTO_LABELS, freeState, nightEvidence: true };
  await context.close();
}

async function mobileValidation() {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  collectErrors(page, "mobile");
  await page.goto(`${BASE}/?view=spatial&e4_mobile=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30_000 });
  const group = page.getByRole("group", { name: "Vision" });
  assert.deepEqual(await group.getByRole("button").allTextContents(), GEOMETRY_LABELS);
  const overflow = await page.evaluate(() => ({ inner: innerWidth, doc: document.documentElement.scrollWidth, body: document.body.scrollWidth }));
  assert(overflow.doc <= overflow.inner + 1 && overflow.body <= overflow.inner + 1, `mobile overflow ${JSON.stringify(overflow)}`);
  for (const label of GEOMETRY_LABELS) {
    const box = await group.getByRole("button", { name: label, exact: true }).boundingBox();
    assert(box && box.height >= 44, `mobile Vision target too short for ${label}: ${JSON.stringify(box)}`);
  }
  const before = await canvas.evaluate(cameraStateObject);
  await group.getByRole("button", { name: "Central Loss", exact: true }).click();
  await page.waitForTimeout(100);
  assertSameCamera(before, await canvas.evaluate(cameraStateObject), "mobile Central Loss");

  const forward = page.getByRole("button", { name: "Move forward", exact: true });
  await forward.scrollIntoViewIfNeeded();
  const box = await forward.boundingBox();
  assert(box);
  const cdp = await context.newCDPSession(page);
  const x = box.x + box.width / 2, y = box.y + box.height / 2;
  await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y, id: 31, radiusX: 4, radiusY: 4, force: 1 }] });
  await page.waitForTimeout(420);
  await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await page.waitForTimeout(120);
  const moved = await canvas.evaluate(cameraStateObject);
  assert.notEqual(moved.position, before.position, "mobile movement did not translate Human observer");
  assert.equal(moved.viewpoint, "free");
  await group.getByRole("button", { name: "Night / Low Light", exact: true }).click();
  await page.waitForTimeout(100);
  assertSameCamera(moved, await canvas.evaluate(cameraStateObject), "mobile free Night");
  await canvas.screenshot({ path: path.join(OUT, "mobile-night.png") });
  result.mobile = { labels: GEOMETRY_LABELS, overflow, moved };
  await context.close();
}

try {
  await desktopValidation();
  await mobileValidation();
  assert.deepEqual(result.errors, []);
  result.ok = true;
} catch (error) {
  result.failure = error instanceof Error ? error.stack || error.message : String(error);
  throw error;
} finally {
  await fs.writeFile(path.join(OUT, "result.json"), JSON.stringify(result, null, 2));
  await browser.close();
}

console.log(JSON.stringify(result, null, 2));
