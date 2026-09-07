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
  e2SpatialReleaseDetected: false,
  e3HumanMovementDetected: false,
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

async function assertTouchTargets(locator, label) {
  const count = await locator.count();
  assert(count > 0, `${label}: no touch targets found`);
  for (let index = 0; index < count; index += 1) {
    const box = await locator.nth(index).boundingBox();
    assert(box, `${label}: target ${index + 1} has no bounding box`);
    assert(
      box.width >= 44 && box.height >= 44,
      `${label}: target ${index + 1} is ${box.width.toFixed(1)}x${box.height.toFixed(1)}; expected at least 44x44`,
    );
  }
}

async function setReactRangeValue(page, selector, value) {
  const range = page.locator(selector);
  await range.evaluate((element, nextValue) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
    if (!setter) throw new Error("range value setter unavailable");
    setter.call(element, String(nextValue));
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }, value);
}

async function assertBuiltInSampleDimensions(page) {
  const original = page.locator('img[alt="Original"]').first();
  await original.waitFor({ state: "visible" });
  const originalSize = await original.evaluate((img) => ({ width: img.naturalWidth, height: img.naturalHeight }));
  if (originalSize.width !== 1440 || originalSize.height !== 900) {
    throw new Error(`Built-in sample intrinsic size mismatch: ${originalSize.width}x${originalSize.height}`);
  }

  await page.locator('#category-select').selectOption('Human');
  await page.locator('#mode-select').selectOption('blur');
  await setReactRangeValue(page, '#strength-range', 100);
  await page.waitForFunction(() => {
    const img = document.querySelector('img[alt="Approximation"]');
    return img instanceof HTMLImageElement && img.src.startsWith('blob:') && img.complete && img.naturalWidth > 0;
  });
  const approximation = page.locator('img[alt="Approximation"]').first();
  const transformedSize = await approximation.evaluate((img) => ({ width: img.naturalWidth, height: img.naturalHeight }));
  if (transformedSize.width !== 1400 || transformedSize.height !== 875) {
    throw new Error(`Built-in transformed sample size mismatch: ${transformedSize.width}x${transformedSize.height}`);
  }

  await setReactRangeValue(page, '#strength-range', 65);
  await page.locator('#mode-select').selectOption('protan');
}

async function assertTunnelAspectSymmetry(page) {
  const cases = [
    { name: "wide", width: 1600, height: 900 },
    { name: "square", width: 900, height: 900 },
    { name: "tall", width: 900, height: 1600 },
  ];

  for (const item of cases) {
    await page.goto(`${BASE}/?tunnel_aspect=${item.name}-${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${item.width}" height="${item.height}" viewBox="0 0 ${item.width} ${item.height}"><rect width="100%" height="100%" fill="rgb(220,220,220)"/></svg>`;
    await page.locator('input[type="file"]').setInputFiles({
      name: `tunnel-${item.name}.svg`,
      mimeType: "image/svg+xml",
      buffer: Buffer.from(svg),
    });
    await page.locator("#category-select").selectOption("Human");
    await page.locator("#mode-select").selectOption("tunnel");
    const before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
    await setReactRangeValue(page, "#strength-range", 100);
    await page.waitForFunction(
      (previous) => {
        const img = document.querySelector('img[alt="Approximation"]');
        return img instanceof HTMLImageElement
          && img.src.startsWith("blob:")
          && img.src !== previous
          && img.complete
          && img.naturalWidth > 0
          && document.querySelector(".compare-card")?.getAttribute("aria-busy") === "false";
      },
      before,
      { timeout: 10_000 },
    );

    const deltas = await page.evaluate(async () => {
      const original = document.querySelector('img[alt="Original"]');
      const approximation = document.querySelector('img[alt="Approximation"]');
      if (!(original instanceof HTMLImageElement) || !(approximation instanceof HTMLImageElement)) throw new Error("comparison images unavailable");
      const load = async (src) => {
        const img = new Image();
        img.src = src;
        await img.decode();
        const canvas = document.createElement("canvas");
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        const ctx = canvas.getContext("2d", { willReadFrequently: true });
        if (!ctx) throw new Error("canvas context unavailable");
        ctx.drawImage(img, 0, 0);
        return { canvas, ctx };
      };
      const source = await load(original.src);
      const output = await load(approximation.src);
      const sample = (xRatio, yRatio) => {
        const ox = Math.min(output.canvas.width - 1, Math.max(0, Math.round((output.canvas.width - 1) * xRatio)));
        const oy = Math.min(output.canvas.height - 1, Math.max(0, Math.round((output.canvas.height - 1) * yRatio)));
        const sx = Math.min(source.canvas.width - 1, Math.max(0, Math.round((source.canvas.width - 1) * xRatio)));
        const sy = Math.min(source.canvas.height - 1, Math.max(0, Math.round((source.canvas.height - 1) * yRatio)));
        const a = source.ctx.getImageData(sx, sy, 1, 1).data;
        const b = output.ctx.getImageData(ox, oy, 1, 1).data;
        const luma = (pixel) => 0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2];
        return luma(a) - luma(b);
      };
      return {
        center: sample(0.5, 0.5),
        top: sample(0.5, 0.05),
        left: sample(0.05, 0.5),
      };
    });

    assert(Math.abs(deltas.center) <= 2, `desktop image: Tunnel ${item.name} center changed unexpectedly (${deltas.center})`);
    assert(deltas.top >= 5 && deltas.left >= 5, `desktop image: Tunnel ${item.name} edge effect is too weak (${JSON.stringify(deltas)})`);
    assert(Math.abs(deltas.top - deltas.left) <= 2, `desktop image: Tunnel ${item.name} aspect-axis bias returned (${JSON.stringify(deltas)})`);
  }

  await page.goto(`${BASE}/?tunnel_aspect_reset=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  await page.locator("#category-select").selectOption("Human");
  await page.locator("#mode-select").selectOption("protan");
  await setReactRangeValue(page, "#strength-range", 65);
}

async function assertImageStrengthZeroIdentity(page) {
  await setReactRangeValue(page, "#strength-range", 0);
  await page.waitForFunction(() => {
    const original = document.querySelector('img[alt="Original"]')?.getAttribute("src");
    const approximation = document.querySelector('img[alt="Approximation"]')?.getAttribute("src");
    return document.querySelector("#strength-range")?.value === "0"
      && document.querySelector(".compare-card")?.getAttribute("aria-busy") === "false"
      && Boolean(original && approximation && original === approximation);
  }, undefined, { timeout: 10_000 });

  for (const [category, modes] of [["Human", expectedHumanImageModes], ["Animal", expectedAnimalImageModes]]) {
    await page.locator("#category-select").selectOption(category);
    for (const mode of modes) {
      await page.locator("#mode-select").selectOption(mode);
      await page.waitForTimeout(140);
      await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10_000 });
      const original = await page.locator('img[alt="Original"]').first().getAttribute("src");
      const approximation = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
      assert(original === approximation, `desktop image: Strength 0 is not Original for ${category}/${mode}`);
    }
  }
  await page.locator("#category-select").selectOption("Human");
  await page.locator("#mode-select").selectOption("protan");
  await setReactRangeValue(page, "#strength-range", 65);
  await page.waitForFunction(() => document.querySelector("#strength-range")?.value === "65" && document.querySelector(".compare-card")?.getAttribute("aria-busy") === "false", undefined, { timeout: 10_000 });
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
    let currentStrengthZeroIdentity = false;
    try {
      const categoryValues = await page.locator("#category-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      if (JSON.stringify(categoryValues) !== JSON.stringify(["Human", "Animal"])) throw new Error(`unexpected image categories ${JSON.stringify(categoryValues)}`);
      await page.locator("#category-select").selectOption("Animal");
      const animalValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      currentAnimalSet = JSON.stringify(animalValues) === JSON.stringify(expectedAnimalImageModes);
      await page.locator("#category-select").selectOption("Human");
      const humanValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      currentHumanSet = JSON.stringify(humanValues) === JSON.stringify(expectedHumanImageModes);
      await page.locator("#mode-select").selectOption("protan");
      await setReactRangeValue(page, "#strength-range", 0);
      await page.waitForTimeout(180);
      await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 2_000 });
      const zeroOriginal = await page.locator('img[alt="Original"]').first().getAttribute("src");
      const zeroApproximation = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
      currentStrengthZeroIdentity = Boolean(zeroOriginal && zeroOriginal === zeroApproximation);
    } catch {
      currentAnimalSet = false;
      currentHumanSet = false;
      currentStrengthZeroIdentity = false;
    }

    if (src?.startsWith("blob:") && currentAnimalSet && currentHumanSet && currentStrengthZeroIdentity) {
      result.productionReleaseDetected = true;
      result.notes.push(`current production behavior detected on attempt ${attempt}; image categories/modes match and Strength 0 is exact Original`);
      return;
    }

    result.notes.push(`attempt ${attempt}: production is stale for blob upload, current image mode set, and/or Strength-0 identity`);
    if (attempt < 12) await page.waitForTimeout(15_000);
  }
  throw new Error("Production did not reach the current blob-upload + image-mode-set + Strength-0-identity release behavior within the retry window.");
}

async function desktopImageSmoke(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const errors = collectErrors(page);

  await waitForCurrentProduction(page);
  await page.goto(`${BASE}/?production_smoke=image-${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  await page.getByRole("heading", { name: /See the same image through different ways of seeing/i }).waitFor();
  await noHorizontalOverflow(page, "desktop image");
  const compareBox = await page.locator(".compare-card").boundingBox();
  const categoryGridBox = await page.locator("#modes").boundingBox();
  assert(compareBox && categoryGridBox, "desktop image: workspace geometry is unavailable");
  const workspaceGap = categoryGridBox.y - (compareBox.y + compareBox.height);
  assert(workspaceGap >= 0 && workspaceGap <= 48, `desktop image: category cards are pushed too far below compare stage (${workspaceGap}px)`);
  const categoryCards = page.locator("#modes .category-card");
  assert((await categoryCards.count()) === 2, "desktop image: expected exactly Human and Animal category cards");
  const lastCategoryBox = await categoryCards.nth(1).boundingBox();
  assert(lastCategoryBox, "desktop image: Animal category card has no bounding box");
  assert(Math.abs((lastCategoryBox.x + lastCategoryBox.width) - (categoryGridBox.x + categoryGridBox.width)) <= 3, "desktop image: two-category grid leaves an unused desktop column");

  const initialResources = await page.evaluate(() => performance.getEntriesByType("resource").map((entry) => entry.name));
  assert(!initialResources.some((name) => /SpatialEntry/i.test(name)), "desktop image: spatial bundle loaded before Explore 3D was opened");

  const categoryValues = await page.locator("#category-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
  assert(JSON.stringify(categoryValues) === JSON.stringify(["Human", "Animal"]), `desktop image: unexpected categories ${JSON.stringify(categoryValues)}`);
  const pageText = await page.locator("body").innerText();
  const heroText = await page.locator(".hero-copy").innerText();
  assert(heroText.includes("human visual conditions") && heroText.includes("animal-inspired modes"), "desktop image: hero does not describe the current Human/Animal product scope");
  assert(!heroText.includes("reference profiles"), "desktop image: removed Reference scope is still advertised in the hero");
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

  await assertBuiltInSampleDimensions(page);
  await assertTunnelAspectSymmetry(page);
  await assertImageStrengthZeroIdentity(page);

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
  await assertTouchTargets(page.locator(".topbar a"), "mobile image header");
  const mobileCompareBox = await page.locator(".compare-card").boundingBox();
  const mobileControlBox = await page.locator(".control-rail").boundingBox();
  const mobileCategoryBox = await page.locator("#modes").boundingBox();
  assert(mobileCompareBox && mobileControlBox && mobileCategoryBox, "mobile image: workspace geometry is unavailable");
  assert(mobileCompareBox.y < mobileControlBox.y && mobileControlBox.y < mobileCategoryBox.y, "mobile image: expected compare -> controls -> categories order");
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

async function waitForExplore3DE3(page, label) {
  for (let attempt = 1; attempt <= 12; attempt += 1) {
    await page.goto(`${BASE}/?view=spatial&e3_release_smoke=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    await page.waitForTimeout(1_000);
    const stable = await page.evaluate(() => {
      const scene = document.querySelector("#spatial-scene-select");
      const observer = document.querySelector("#spatial-observer-select");
      const canvas = document.querySelector('canvas.spatial-canvas[data-scene-id="night-intersection"][data-observer-id="human"]');
      const visionButtons = [...document.querySelectorAll('[role="group"][aria-label="Vision"] button')].map((button) => button.textContent?.trim());
      const sceneValues = scene instanceof HTMLSelectElement ? [...scene.options].map((option) => option.value) : [];
      return scene instanceof HTMLSelectElement
        && scene.value === "night-intersection"
        && JSON.stringify(sceneValues) === JSON.stringify(["night-intersection", "photo-reference"])
        && observer instanceof HTMLSelectElement
        && observer.value === "human"
        && canvas instanceof HTMLCanvasElement
        && canvas.dataset.sceneSupportsTranslation === "true"
        && canvas.dataset.observerMovement === "bounded-ground"
        && document.querySelector('.spatial-reset-button') instanceof HTMLButtonElement
        && Number(canvas.dataset.sceneObjectCount || 0) >= 220
        && Number(canvas.dataset.sceneLightCount || 0) >= 10
        && canvas.dataset.sceneVolume === "150x150x60"
        && canvas.dataset.cameraViewpoint === "baseline"
        && canvas.dataset.visionMode === "normal"
        && JSON.stringify(visionButtons) === JSON.stringify(["Normal"])
        && canvas.clientWidth > 0
        && canvas.clientHeight > 0;
    });
    if (stable) {
      try {
        const canvas = page.locator("canvas.spatial-canvas");
        const baseline = await canvas.evaluate((element) => ({
          position: element.dataset.cameraPosition,
          yaw: element.dataset.cameraYaw,
          pitch: element.dataset.cameraPitch,
          fov: element.dataset.cameraFov,
          viewpoint: element.dataset.cameraViewpoint,
        }));
        const viewpoint = page.getByRole("group", { name: "Comparison viewpoint" });
        await viewpoint.getByRole("button", { name: "Offset", exact: true }).click();
        await page.waitForTimeout(180);
        const offset = await canvas.evaluate((element) => ({
          position: element.dataset.cameraPosition,
          yaw: element.dataset.cameraYaw,
          pitch: element.dataset.cameraPitch,
          fov: element.dataset.cameraFov,
          viewpoint: element.dataset.cameraViewpoint,
        }));
        assert(offset.viewpoint === "offset", `${label}: E2 Offset viewpoint did not activate`);
        assert(offset.position !== baseline.position, `${label}: E2 Offset did not translate the camera`);
        for (const key of ["yaw", "pitch", "fov"]) {
          assert(offset[key] === baseline[key], `${label}: E2 authored translation changed ${key}`);
        }
        await viewpoint.getByRole("button", { name: "Reference", exact: true }).click();
        await page.waitForTimeout(120);
        const restored = await canvas.evaluate((element) => ({ position: element.dataset.cameraPosition, viewpoint: element.dataset.cameraViewpoint }));
        assert(restored.viewpoint === "baseline" && restored.position === baseline.position, `${label}: E2 Reference viewpoint did not restore`);
        result.e2SpatialReleaseDetected = true;
        const beforeMove = await canvas.evaluate((element) => element.dataset.cameraPosition);
        await canvas.focus();
        await page.keyboard.down("w");
        await page.waitForTimeout(320);
        await page.keyboard.up("w");
        await page.waitForTimeout(120);
        const moved = await canvas.evaluate((element) => ({
          position: element.dataset.cameraPosition,
          viewpoint: element.dataset.cameraViewpoint,
          movement: element.dataset.observerMovement,
        }));
        assert(moved.position && moved.position !== beforeMove, `${label}: E3 W movement did not translate the Human observer`);
        assert(moved.viewpoint === "free" && moved.movement === "bounded-ground", `${label}: E3 movement state is not free/bounded-ground`);
        await page.getByRole("button", { name: "Reset observer", exact: true }).click();
        await page.waitForTimeout(120);
        const reset = await canvas.evaluate((element) => ({
          position: element.dataset.cameraPosition,
          yaw: element.dataset.cameraYaw,
          pitch: element.dataset.cameraPitch,
          fov: element.dataset.cameraFov,
          viewpoint: element.dataset.cameraViewpoint,
        }));
        assert(reset.position === "0.000,0.000,0.000" && reset.viewpoint === "baseline", `${label}: E3 Reset did not restore canonical position`);
        assert(reset.yaw === "0.000000" && reset.pitch === "-0.010000" && reset.fov === "52.000", `${label}: E3 Reset did not restore direction/FOV`);
        result.e3HumanMovementDetected = true;
        result.notes.push(`${label}: current E3 Human bounded-movement fingerprint detected on attempt ${attempt}`);
        return;
      } catch (error) {
        result.notes.push(`${label}: E2 attempt ${attempt} reached geometry but failed E3 movement/translation fingerprint: ${error instanceof Error ? error.message : String(error)}`);
      }
    } else {
      result.notes.push(`${label}: E2 attempt ${attempt} did not reach E3 Night Intersection movement fingerprint`);
    }
    if (attempt < 12) await page.waitForTimeout(5_000);
  }
  throw new Error(`${label}: current E3 Human bounded-movement release was not detected`);
}

async function desktopSpatialSmoke(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await waitForExplore3DE3(page, "desktop spatial");
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30_000 });
  await noHorizontalOverflow(page, "desktop spatial");
  const spatialNav = page.getByRole("navigation", { name: "Spatial navigation" });
  assert((await spatialNav.getByRole("link", { name: "Compare image", exact: true }).count()) === 1, "desktop spatial: Compare image navigation is missing or duplicated");
  assert((await page.getByRole("link", { name: "Back to image", exact: true }).count()) === 0, "desktop spatial: duplicate Back to image action is still exposed");
  assert((await spatialNav.getByRole("link", { name: "Explore 3D", exact: true }).count()) === 1, "desktop spatial: Explore 3D navigation is missing or duplicated");

  const sceneSelect = page.locator("#spatial-scene-select");
  const observerSelect = page.locator("#spatial-observer-select");
  assert((await sceneSelect.inputValue()) === "night-intersection", "desktop spatial: Night Intersection is not active");
  assert((await observerSelect.inputValue()) === "human", "desktop spatial: Human observer is not active");
  assert(JSON.stringify(await sceneSelect.locator("option").allTextContents()) === JSON.stringify(["Night Intersection", "360° Photo Reference"]), "desktop spatial: unexpected Scene options");
  assert(JSON.stringify(await observerSelect.locator("option").allTextContents()) === JSON.stringify(["Human"]), "desktop spatial: unexpected Observer options");

  const modeGroup = page.getByRole("group", { name: "Vision" });
  let labels = await modeGroup.getByRole("button").allTextContents();
  assert(JSON.stringify(labels) === JSON.stringify(["Normal"]), `desktop spatial: E2 geometry must expose Normal only, got ${JSON.stringify(labels)}`);
  assert(!labels.some((label) => /Cat-like|Bird-like|Bee-like/i.test(label)), "desktop spatial: blocked/rejected animal control exposed");

  const baseline = await canvas.evaluate((element) => ({
    scene: element.dataset.sceneId,
    supportsTranslation: element.dataset.sceneSupportsTranslation,
    objectCount: Number(element.dataset.sceneObjectCount || 0),
    lightCount: Number(element.dataset.sceneLightCount || 0),
    volume: element.dataset.sceneVolume,
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    viewpoint: element.dataset.cameraViewpoint,
  }));
  assert(baseline.scene === "night-intersection" && baseline.supportsTranslation === "true", `desktop spatial: E2 geometry metadata regressed ${JSON.stringify(baseline)}`);
  assert(baseline.objectCount >= 220 && baseline.lightCount >= 10 && baseline.volume === "150x150x60", `desktop spatial: E2 density/volume regressed ${JSON.stringify(baseline)}`);
  assert((await canvas.getAttribute("data-observer-movement")) === "bounded-ground", "desktop spatial: bounded Human movement is unavailable");
  assert((await page.getByRole("button", { name: "Reset observer", exact: true }).count()) === 1, "desktop spatial: Reset observer control is missing");

  await page.waitForTimeout(500);
  const beforeOffset = await canvas.screenshot();
  const viewpoint = page.getByRole("group", { name: "Comparison viewpoint" });
  await viewpoint.getByRole("button", { name: "Offset", exact: true }).click();
  await page.waitForTimeout(220);
  const offset = await canvas.evaluate((element) => ({
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    viewpoint: element.dataset.cameraViewpoint,
  }));
  const afterOffset = await canvas.screenshot();
  assert(offset.viewpoint === "offset" && offset.position !== baseline.position, "desktop spatial: E2 Offset did not translate camera");
  for (const key of ["yaw", "pitch", "fov"]) assert(offset[key] === baseline[key], `desktop spatial: E2 Offset changed ${key}`);
  assert(!beforeOffset.equals(afterOffset), "desktop spatial: E2 translation produced no rendered parallax difference");
  await viewpoint.getByRole("button", { name: "Reference", exact: true }).click();
  await page.waitForTimeout(180);

  const beforeLook = await canvas.screenshot();
  const box = await canvas.boundingBox();
  assert(box, "desktop spatial: canvas has no bounding box");
  await page.mouse.move(box.x + box.width * 0.60, box.y + box.height * 0.52);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.34, box.y + box.height * 0.48, { steps: 8 });
  await page.mouse.up();
  await page.waitForTimeout(180);
  const afterLook = await canvas.screenshot();
  assert(!beforeLook.equals(afterLook), "desktop spatial: drag look-around did not change E2 rendered view");
  await page.screenshot({ path: path.join(OUT, "desktop-spatial.png"), fullPage: true });

  await sceneSelect.selectOption("photo-reference");
  await page.waitForTimeout(800);
  labels = await modeGroup.getByRole("button").allTextContents();
  assert(JSON.stringify(labels) === JSON.stringify(expectedSpatialModes), `desktop spatial: Photo Reference Vision controls regressed ${JSON.stringify(labels)}`);
  const beforeVisionSwitch = await canvas.evaluate((element) => ({
    scene: element.dataset.sceneId,
    observer: element.dataset.observerId,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    position: element.dataset.cameraPosition,
  }));
  const tunnelButton = modeGroup.getByRole("button", { name: "Tunnel Vision", exact: true });
  await tunnelButton.click();
  await page.waitForTimeout(120);
  const afterVisionSwitch = await canvas.evaluate((element) => ({
    scene: element.dataset.sceneId,
    observer: element.dataset.observerId,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    position: element.dataset.cameraPosition,
    vision: element.dataset.visionMode,
  }));
  assert(afterVisionSwitch.vision === "tunnel", `desktop spatial: Photo Reference Vision runtime did not record tunnel (${JSON.stringify(afterVisionSwitch)})`);
  for (const key of ["scene", "observer", "yaw", "pitch", "fov", "position"]) {
    assert(afterVisionSwitch[key] === beforeVisionSwitch[key], `desktop spatial: Vision switch changed ${key}: ${beforeVisionSwitch[key]} -> ${afterVisionSwitch[key]}`);
  }
  for (const label of expectedSpatialModes) {
    const button = modeGroup.getByRole("button", { name: label, exact: true });
    await button.click();
    assert((await button.getAttribute("aria-pressed")) === "true", `desktop spatial: ${label} did not activate on Photo Reference`);
  }

  assertClean(errors, "desktop spatial");
  result.desktopSpatial = true;
  await context.close();
}

async function mobileSpatialSmoke(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await page.goto(`${BASE}/?view=spatial&production_smoke=e2-mobile-${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30_000 });
  await noHorizontalOverflow(page, "mobile spatial");
  await assertTouchTargets(page.locator(".topbar a"), "mobile spatial header");
  const spatialNav = page.getByRole("navigation", { name: "Spatial navigation" });
  assert((await spatialNav.getByRole("link", { name: "Compare image", exact: true }).count()) === 1, "mobile spatial: Compare image navigation is missing or duplicated");
  assert((await page.getByRole("link", { name: "Back to image", exact: true }).count()) === 0, "mobile spatial: duplicate Back to image action is still exposed");
  assert((await spatialNav.getByRole("link", { name: "Explore 3D", exact: true }).count()) === 1, "mobile spatial: Explore 3D navigation is missing or duplicated");
  const sceneSelect = page.locator("#spatial-scene-select");
  assert((await sceneSelect.inputValue()) === "night-intersection", "mobile spatial: Night Intersection is not active");
  assert((await page.locator("#spatial-observer-select").inputValue()) === "human", "mobile spatial: Human Observer is not active");
  await assertTouchTargets(page.locator(".spatial-layer-control select"), "mobile spatial Scene/Observer controls");
  const group = page.getByRole("group", { name: "Vision" });
  assert(JSON.stringify(await group.getByRole("button").allTextContents()) === JSON.stringify(["Normal"]), "mobile spatial: E2 geometry exposes non-Normal Vision");

  const baseline = await canvas.evaluate((element) => ({
    scene: element.dataset.sceneId,
    objectCount: Number(element.dataset.sceneObjectCount || 0),
    lightCount: Number(element.dataset.sceneLightCount || 0),
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
  }));
  assert(baseline.scene === "night-intersection" && baseline.objectCount >= 220 && baseline.lightCount >= 10, `mobile spatial: E2 geometry incomplete ${JSON.stringify(baseline)}`);
  assert((await canvas.getAttribute("data-observer-movement")) === "bounded-ground", "mobile spatial: bounded Human movement is unavailable");
  const mobileMoveButtons = page.getByRole("group", { name: "Mobile movement" }).getByRole("button");
  await assertTouchTargets(mobileMoveButtons, "mobile spatial movement pad");
  const beforeFreeMove = await canvas.getAttribute("data-camera-position");
  const forwardButton = page.getByRole("button", { name: "Move forward", exact: true });
  await forwardButton.scrollIntoViewIfNeeded();
  const forwardBox = await forwardButton.boundingBox();
  assert(forwardBox, "mobile spatial: Move forward has no bounding box");
  const movementCdp = await context.newCDPSession(page);
  const moveX = forwardBox.x + forwardBox.width / 2;
  const moveY = forwardBox.y + forwardBox.height / 2;
  await movementCdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: moveX, y: moveY, id: 71, radiusX: 4, radiusY: 4, force: 1 }] });
  await page.waitForTimeout(320);
  await movementCdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await page.waitForTimeout(120);
  const afterFreeMove = await canvas.getAttribute("data-camera-position");
  assert(afterFreeMove && afterFreeMove !== beforeFreeMove, "mobile spatial: movement control did not translate observer");
  assert((await canvas.getAttribute("data-camera-viewpoint")) === "free", "mobile spatial: movement did not mark viewpoint free");
  await page.getByRole("button", { name: "Reset observer", exact: true }).click();
  await page.waitForTimeout(120);
  assert((await canvas.getAttribute("data-camera-position")) === "0.000,0.000,0.000", "mobile spatial: Reset observer did not restore canonical position");
  const beforeOffset = await canvas.screenshot();
  const viewpoint = page.getByRole("group", { name: "Comparison viewpoint" });
  await viewpoint.getByRole("button", { name: "Offset", exact: true }).click();
  await page.waitForTimeout(220);
  const offset = await canvas.evaluate((element) => ({
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
  }));
  const afterOffset = await canvas.screenshot();
  assert(offset.position !== baseline.position, "mobile spatial: E2 Offset did not translate camera");
  assert(offset.yaw === baseline.yaw && offset.pitch === baseline.pitch && offset.fov === baseline.fov, "mobile spatial: E2 Offset changed direction/FOV");
  assert(!beforeOffset.equals(afterOffset), "mobile spatial: E2 translation produced no rendered parallax difference");
  await page.screenshot({ path: path.join(OUT, "mobile-spatial.png"), fullPage: true });
  await viewpoint.getByRole("button", { name: "Reference", exact: true }).click();

  const beforeLook = await canvas.screenshot();
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
  await page.waitForTimeout(220);
  const afterLook = await canvas.screenshot();
  assert(!beforeLook.equals(afterLook), "mobile spatial: touch look-around did not change E2 rendered view");

  await sceneSelect.selectOption("photo-reference");
  await page.waitForTimeout(700);
  const photoLabels = await group.getByRole("button").allTextContents();
  assert(JSON.stringify(photoLabels) === JSON.stringify(expectedSpatialModes), `mobile spatial: Photo Reference Vision controls regressed ${JSON.stringify(photoLabels)}`);
  await group.getByRole("button", { name: "Dog-like", exact: true }).click();
  await noHorizontalOverflow(page, "mobile spatial after scene switch");
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
