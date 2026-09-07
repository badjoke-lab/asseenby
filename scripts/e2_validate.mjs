import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "http://127.0.0.1:4173";
const OUT = path.resolve("e2-validation");
await fs.mkdir(OUT, { recursive: true });

const assert = (condition, message) => {
  if (!condition) throw new Error(message);
};

const collectErrors = (page) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`console: ${message.text()}`);
  });
  return errors;
};

const noOverflow = async (page, label) => {
  const sizes = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
  assert(sizes.scroll <= sizes.width + 1, `${label}: horizontal overflow ${JSON.stringify(sizes)}`);
};

const snapshot = async (canvas) => canvas.evaluate((element) => ({
  scene: element.dataset.sceneId,
  supportsTranslation: element.dataset.sceneSupportsTranslation,
  objectCount: Number(element.dataset.sceneObjectCount || 0),
  lightCount: Number(element.dataset.sceneLightCount || 0),
  volume: element.dataset.sceneVolume,
  observer: element.dataset.observerId,
  viewpoint: element.dataset.cameraViewpoint,
  yaw: element.dataset.cameraYaw,
  pitch: element.dataset.cameraPitch,
  fov: element.dataset.cameraFov,
  position: element.dataset.cameraPosition,
  vision: element.dataset.visionMode,
}));

const result = { baseUrl: BASE, desktop: null, mobile: null, ok: false };
const browser = await chromium.launch({ headless: true });

try {
  {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    const errors = collectErrors(page);
    const start = Date.now();
    await page.goto(`${BASE}/?view=spatial&e2_validate=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    const canvas = page.locator("canvas.spatial-canvas");
    await canvas.waitFor({ state: "visible", timeout: 30_000 });
    await page.waitForTimeout(1000);
    const loadMs = Date.now() - start;

    const sceneSelect = page.locator("#spatial-scene-select");
    const sceneOptions = await sceneSelect.locator("option").allTextContents();
    assert(JSON.stringify(sceneOptions) === JSON.stringify(["Night Intersection", "360° Photo Reference"]), `desktop: unexpected scenes ${JSON.stringify(sceneOptions)}`);
    assert((await sceneSelect.inputValue()) === "night-intersection", "desktop: Night Intersection is not the default scene");
    assert((await page.locator("#spatial-observer-select").inputValue()) === "human", "desktop: Human observer is not active");

    const visionLabels = await page.getByRole("group", { name: "Vision" }).getByRole("button").allTextContents();
    assert(JSON.stringify(visionLabels) === JSON.stringify(["Normal"]), `desktop: E2 geometry must expose Normal only, got ${JSON.stringify(visionLabels)}`);

    const baseline = await snapshot(canvas);
    assert(baseline.scene === "night-intersection", `desktop: wrong canvas scene ${JSON.stringify(baseline)}`);
    assert(baseline.supportsTranslation === "true", "desktop: Night Intersection is not marked translation-capable");
    assert(baseline.objectCount >= 220, `desktop: scene density too low (${baseline.objectCount} objects)`);
    assert(baseline.lightCount >= 10, `desktop: lighting hierarchy too small (${baseline.lightCount} lights)`);
    assert(baseline.volume === "150x150x60", `desktop: wrong scene volume ${baseline.volume}`);
    assert(baseline.viewpoint === "baseline", `desktop: baseline viewpoint missing ${JSON.stringify(baseline)}`);
    assert(baseline.vision === "normal", "desktop: geometry baseline is not Normal");

    await noOverflow(page, "desktop E2");
    await page.screenshot({ path: path.join(OUT, "desktop-night-baseline.png"), fullPage: true });
    const before = await canvas.screenshot();

    await page.getByRole("group", { name: "Comparison viewpoint" }).getByRole("button", { name: "Offset", exact: true }).click();
    await page.waitForTimeout(250);
    const offset = await snapshot(canvas);
    const after = await canvas.screenshot();
    assert(offset.viewpoint === "offset", `desktop: Offset viewpoint did not activate ${JSON.stringify(offset)}`);
    assert(offset.position !== baseline.position, `desktop: Offset did not translate camera (${baseline.position})`);
    for (const key of ["yaw", "pitch", "fov"]) assert(offset[key] === baseline[key], `desktop: viewpoint changed ${key}: ${baseline[key]} -> ${offset[key]}`);
    assert(!before.equals(after), "desktop: camera translation produced no rendered parallax difference");
    await page.screenshot({ path: path.join(OUT, "desktop-night-offset.png"), fullPage: true });

    await page.getByRole("group", { name: "Comparison viewpoint" }).getByRole("button", { name: "Reference", exact: true }).click();
    await page.waitForTimeout(200);
    const restored = await snapshot(canvas);
    assert(restored.position === baseline.position && restored.viewpoint === "baseline", `desktop: Reference did not restore canonical camera ${JSON.stringify(restored)}`);

    await sceneSelect.selectOption("photo-reference");
    await page.waitForTimeout(1200);
    const photo = await snapshot(canvas);
    assert(photo.scene === "photo-reference" && photo.supportsTranslation === "false", `desktop: Photo Reference switch failed ${JSON.stringify(photo)}`);
    const photoVisionLabels = await page.getByRole("group", { name: "Vision" }).getByRole("button").allTextContents();
    assert(JSON.stringify(photoVisionLabels) === JSON.stringify(["Normal", "Tunnel Vision", "Central Loss", "Night / Low Light", "Dog-like", "Cataract-like"]), `desktop: Photo Reference visions regressed ${JSON.stringify(photoVisionLabels)}`);
    await page.screenshot({ path: path.join(OUT, "desktop-photo-reference.png"), fullPage: true });

    assert(errors.length === 0, `desktop: browser errors ${JSON.stringify(errors)}`);
    result.desktop = { loadMs, baseline, offset, restored, photo, errors };
    await context.close();
  }

  {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const page = await context.newPage();
    const errors = collectErrors(page);
    const start = Date.now();
    await page.goto(`${BASE}/?view=spatial&e2_mobile=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    const canvas = page.locator("canvas.spatial-canvas");
    await canvas.waitFor({ state: "visible", timeout: 30_000 });
    await page.waitForTimeout(900);
    const loadMs = Date.now() - start;
    await noOverflow(page, "mobile E2");
    const baseline = await snapshot(canvas);
    assert(baseline.scene === "night-intersection" && baseline.objectCount >= 220 && baseline.lightCount >= 10, `mobile: geometry baseline incomplete ${JSON.stringify(baseline)}`);
    const before = await canvas.screenshot();
    await page.getByRole("group", { name: "Comparison viewpoint" }).getByRole("button", { name: "Offset", exact: true }).click();
    await page.waitForTimeout(250);
    const offset = await snapshot(canvas);
    const after = await canvas.screenshot();
    assert(offset.position !== baseline.position, "mobile: authored viewpoint did not translate camera");
    assert(offset.yaw === baseline.yaw && offset.pitch === baseline.pitch && offset.fov === baseline.fov, "mobile: authored viewpoint changed direction/FOV");
    assert(!before.equals(after), "mobile: translated viewpoint produced no rendered parallax difference");
    await page.screenshot({ path: path.join(OUT, "mobile-night-offset.png"), fullPage: true });
    await noOverflow(page, "mobile E2 after viewpoint");
    assert(errors.length === 0, `mobile: browser errors ${JSON.stringify(errors)}`);
    result.mobile = { loadMs, baseline, offset, errors };
    await context.close();
  }

  result.ok = true;
} finally {
  await browser.close();
  await fs.writeFile(path.join(OUT, "result.json"), `${JSON.stringify(result, null, 2)}\n`);
  console.log(JSON.stringify(result, null, 2));
}
