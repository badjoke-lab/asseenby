import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "https://asseenby.pages.dev";
const OUT = path.resolve("production-smoke");
const expectedAnimalImageModes = ["dog"];
const expectedHumanImageModes = ["protan", "deutan", "tritan", "blur", "low_contrast", "cataract", "tunnel", "central_loss"];
const expectedSpatialModes = [
  "Normal",
  "Tunnel Vision",
  "Central Loss",
  "Night / Low Light",
  "Dog-like",
  "Cataract-like",
];

await fs.mkdir(OUT, { recursive: true });

const result = {
  baseUrl: BASE,
  checkedAt: new Date().toISOString(),
  productionReleaseDetected: false,
  desktopImage: false,
  mobileImage: false,
  desktopSpatial: false,
  mobileSpatial: false,
  notes: [],
};

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function collectErrors(page) {
  const pageErrors = [];
  const consoleErrors = [];
  page.on("pageerror", (error) => pageErrors.push(String(error)));
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  return { pageErrors, consoleErrors };
}

function assertClean(errors, label) {
  assert(errors.pageErrors.length === 0, `${label}: page errors: ${errors.pageErrors.join(" | ")}`);
  assert(errors.consoleErrors.length === 0, `${label}: console errors: ${errors.consoleErrors.join(" | ")}`);
}

async function noHorizontalOverflow(page, label) {
  const metrics = await page.evaluate(() => ({
    innerWidth: window.innerWidth,
    documentWidth: document.documentElement.scrollWidth,
    bodyWidth: document.body.scrollWidth,
  }));
  assert(metrics.documentWidth <= metrics.innerWidth + 1, `${label}: document horizontal overflow ${JSON.stringify(metrics)}`);
  assert(metrics.bodyWidth <= metrics.innerWidth + 1, `${label}: body horizontal overflow ${JSON.stringify(metrics)}`);
}

async function waitForCurrentProduction(page) {
  const file = {
    name: "production-smoke.svg",
    mimeType: "image/svg+xml",
    buffer: Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="60"><rect width="80" height="60" fill="#c46b45"/><circle cx="52" cy="25" r="14" fill="#4b7794"/></svg>'),
  };

  for (let attempt = 1; attempt <= 12; attempt += 1) {
    await page.goto(`${BASE}/?production_smoke=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    const input = page.locator('input[type="file"]');
    await input.setInputFiles(file);
    await page.waitForTimeout(250);
    const src = await page.locator('img[alt="Original"]').first().getAttribute("src");

    let currentAnimalSet = false;
    let currentHumanSet = false;
    try {
      const categoryValues = await page.locator("#category-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      if (JSON.stringify(categoryValues) !== JSON.stringify(["Human", "Animal"])) throw new Error(`unexpected image categories ${JSON.stringify(categoryValues)}`);
      await page.locator("#category-select").selectOption("Animal");
      const animalValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      currentAnimalSet = JSON.stringify(animalValues) === JSON.stringify(expectedAnimalImageModes);
      await page.locator("#category-select").selectOption("Human");
      const humanValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      currentHumanSet = JSON.stringify(humanValues) === JSON.stringify(expectedHumanImageModes);
    } catch {
      currentAnimalSet = false;
      currentHumanSet = false;
    }

    if (src?.startsWith("blob:") && currentAnimalSet && currentHumanSet) {
      result.productionReleaseDetected = true;
      result.notes.push(`current production behavior detected on attempt ${attempt}; image categories are Human/Animal only, with the audited Human set and Animal=Dog-like only`);
      return;
    }

    result.notes.push(`attempt ${attempt}: production is stale for blob upload, Human/Animal category set, Human modes, and/or Animal modes`);
    if (attempt < 12) await page.waitForTimeout(15_000);
  }
  throw new Error("Production did not reach the current blob-upload + Human/Animal-only release behavior within the retry window.");
}

async function desktopImageSmoke(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const errors = collectErrors(page);

  await waitForCurrentProduction(page);
  await page.goto(`${BASE}/?production_smoke=image-${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  await page.getByRole("heading", { name: /See the same image through different ways of seeing/i }).waitFor();
  await noHorizontalOverflow(page, "desktop image");

  const initialResources = await page.evaluate(() => performance.getEntriesByType("resource").map((entry) => entry.name));
  assert(!initialResources.some((name) => /SpatialEntry/i.test(name)), "desktop image: spatial bundle loaded before Explore 3D was opened");

  const categoryValues = await page.locator("#category-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
  assert(JSON.stringify(categoryValues) === JSON.stringify(["Human", "Animal"]), `desktop image: unexpected categories ${JSON.stringify(categoryValues)}`);
  const pageText = await page.locator("body").innerText();
  assert(!pageText.includes("Age Profile"), "desktop image: removed Age Profile is still visible");
  assert(!pageText.includes("Sex-difference Profile"), "desktop image: removed Sex-difference Profile is still visible");
  await page.locator("#category-select").selectOption("Animal");
  const animalValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
  assert(JSON.stringify(animalValues) === JSON.stringify(expectedAnimalImageModes), `desktop image: unexpected Animal image modes ${JSON.stringify(animalValues)}`);
  const animalBodyText = await page.locator("body").innerText();
  assert(!animalBodyText.includes("Bee-like"), "desktop image: removed Bee-like image mode is still visible");
  assert(!animalBodyText.includes("Bird-like"), "desktop image: removed Bird-like image mode is still visible");
  assert(!animalBodyText.includes("Cat-like"), "desktop image: removed Cat-like image mode is still visible");
  await page.locator("#category-select").selectOption("Human");
  const humanValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
  assert(JSON.stringify(humanValues) === JSON.stringify(expectedHumanImageModes), `desktop image: unexpected Human image modes ${JSON.stringify(humanValues)}`);
  const humanBodyText = await page.locator("body").innerText();
  assert(!humanBodyText.includes("Fatigue-like"), "desktop image: removed Fatigue-like mode is still visible");
  assert(!humanBodyText.includes("Dry-eye-like"), "desktop image: removed Dry-eye-like mode is still visible");
  assert(!humanBodyText.includes("Night / Low Light"), "desktop image: removed Night / Low Light image mode is still visible");

  const split = page.getByRole("button", { name: "Split" });
  await split.click();
  assert((await split.getAttribute("aria-pressed")) === "true", "desktop image: Split did not become active");
  const side = page.getByRole("button", { name: "Side by side" });
  await side.click();
  assert((await side.getAttribute("aria-pressed")) === "true", "desktop image: Side by side did not become active");
  await page.getByRole("button", { name: "Slider" }).click();

  const approximation = page.locator('img[alt="Approximation"]').first();
  await page.waitForFunction(() => document.querySelector('img[alt="Approximation"]')?.getAttribute("src")?.startsWith("blob:"));
  const beforeStrengthSrc = await approximation.getAttribute("src");
  const strength = page.locator("#strength-range");
  await strength.focus();
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowRight");
  await page.waitForFunction(
    (previous) => {
      const current = document.querySelector('img[alt="Approximation"]')?.getAttribute("src");
      return Boolean(current && current.startsWith("blob:") && current !== previous);
    },
    beforeStrengthSrc,
    { timeout: 10_000 },
  );
  assert((await page.locator(".compare-card").getAttribute("aria-busy")) === "false", "desktop image: comparison did not settle back to idle after Strength change");

  const upload = {
    name: "smoke-upload.svg",
    mimeType: "image/svg+xml",
    buffer: Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="120" height="90"><rect width="120" height="90" fill="#8b674a"/><rect x="48" y="18" width="50" height="50" fill="#708d66"/></svg>'),
  };
  await page.locator('input[type="file"]').setInputFiles(upload);
  await page.waitForFunction(() => document.querySelector('img[alt="Original"]')?.getAttribute("src")?.startsWith("blob:"));
  await page.locator(".compare-card[aria-busy=\"false\"]").waitFor({ timeout: 10_000 });
  assert((await page.locator('img[alt="Original"]').first().getAttribute("src"))?.startsWith("blob:"), "desktop image: uploaded Original is not a blob URL");

  await page.getByRole("button", { name: "Use sample image" }).click();
  await page.waitForFunction(() => document.querySelector('img[alt="Original"]')?.getAttribute("src")?.startsWith("data:image/svg+xml"));
  await page.screenshot({ path: path.join(OUT, "desktop-image.png"), fullPage: true });
  assertClean(errors, "desktop image");
  result.desktopImage = true;
  await context.close();
}

async function mobileImageSmoke(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await page.goto(`${BASE}/?production_smoke=mobile-image-${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  await page.locator("#workspace").waitFor();
  await noHorizontalOverflow(page, "mobile image");
  await page.getByRole("button", { name: "Side by side" }).click();
  await page.getByRole("button", { name: "Slider" }).click();
  const approximation = page.locator('img[alt="Approximation"]').first();
  await page.waitForFunction(() => document.querySelector('img[alt="Approximation"]')?.getAttribute("src")?.startsWith("blob:"));
  const before = await approximation.getAttribute("src");
  await page.locator("#strength-range").focus();
  await page.keyboard.press("ArrowRight");
  await page.waitForFunction(
    (previous) => {
      const current = document.querySelector('img[alt="Approximation"]')?.getAttribute("src");
      return Boolean(current && current.startsWith("blob:") && current !== previous);
    },
    before,
    { timeout: 10_000 },
  );
  await page.screenshot({ path: path.join(OUT, "mobile-image.png"), fullPage: true });
  await noHorizontalOverflow(page, "mobile image after controls");
  assertClean(errors, "mobile image");
  result.mobileImage = true;
  await context.close();
}

async function desktopSpatialSmoke(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await page.goto(`${BASE}/?view=spatial&production_smoke=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  await page.getByRole("heading", { name: "360° photographic night-city scene" }).waitFor({ timeout: 30_000 });
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30_000 });
  await noHorizontalOverflow(page, "desktop spatial");

  const modeGroup = page.getByRole("group", { name: "Spatial perception mode" });
  const labels = await modeGroup.getByRole("button").allTextContents();
  assert(JSON.stringify(labels) === JSON.stringify(expectedSpatialModes), `desktop spatial: unexpected controls ${JSON.stringify(labels)}`);
  assert(!labels.some((label) => /Cat-like|Bird-like|Bee-like/i.test(label)), "desktop spatial: blocked/rejected animal control exposed");

  for (const label of expectedSpatialModes) {
    const button = modeGroup.getByRole("button", { name: label, exact: true });
    await button.click();
    assert((await button.getAttribute("aria-pressed")) === "true", `desktop spatial: ${label} did not activate`);
  }
  await modeGroup.getByRole("button", { name: "Normal", exact: true }).click();
  await page.waitForTimeout(700);
  const before = await canvas.screenshot();
  const box = await canvas.boundingBox();
  assert(box, "desktop spatial: canvas has no bounding box");
  await page.mouse.move(box.x + box.width * 0.55, box.y + box.height * 0.52);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.30, box.y + box.height * 0.48, { steps: 8 });
  await page.mouse.up();
  await page.waitForTimeout(200);
  const after = await canvas.screenshot();
  assert(!before.equals(after), "desktop spatial: drag did not change rendered view");

  await page.screenshot({ path: path.join(OUT, "desktop-spatial.png"), fullPage: true });
  assertClean(errors, "desktop spatial");
  result.desktopSpatial = true;
  await context.close();
}

async function mobileSpatialSmoke(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await page.goto(`${BASE}/?view=spatial&production_smoke=mobile-${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30_000 });
  await noHorizontalOverflow(page, "mobile spatial");
  const group = page.getByRole("group", { name: "Spatial perception mode" });
  await group.getByRole("button", { name: "Central Loss", exact: true }).click();
  await page.waitForTimeout(400);
  const before = await canvas.screenshot();
  const box = await canvas.boundingBox();
  assert(box, "mobile spatial: canvas has no bounding box");
  const cdp = await context.newCDPSession(page);
  const startX = box.x + box.width * 0.68;
  const startY = box.y + box.height * 0.52;
  const endX = box.x + box.width * 0.36;
  const endY = box.y + box.height * 0.48;
  await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: startX, y: startY }] });
  await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: endX, y: endY }] });
  await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await page.waitForTimeout(250);
  const after = await canvas.screenshot();
  assert(!before.equals(after), "mobile spatial: touch look-around did not change rendered view");
  await group.getByRole("button", { name: "Dog-like", exact: true }).click();
  await page.screenshot({ path: path.join(OUT, "mobile-spatial.png"), fullPage: true });
  await noHorizontalOverflow(page, "mobile spatial after touch");
  assertClean(errors, "mobile spatial");
  result.mobileSpatial = true;
  await context.close();
}

const browser = await chromium.launch({ headless: true });
try {
  await desktopImageSmoke(browser);
  await mobileImageSmoke(browser);
  await desktopSpatialSmoke(browser);
  await mobileSpatialSmoke(browser);
  result.ok = true;
} catch (error) {
  result.ok = false;
  result.failure = error instanceof Error ? error.stack || error.message : String(error);
  throw error;
} finally {
  await browser.close();
  await fs.writeFile(path.join(OUT, "result.json"), `${JSON.stringify(result, null, 2)}\n`);
  console.log(JSON.stringify(result, null, 2));
}
