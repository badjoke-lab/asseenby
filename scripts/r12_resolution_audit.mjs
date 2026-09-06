import { chromium } from "playwright";
import fs from "node:fs/promises";

const BASE = process.env.ASSEENBY_AUDIT_URL || "http://127.0.0.1:4173";
const OUT = process.env.R12_AUDIT_OUT || "r12-resolution-audit.json";
const CANONICAL_WIDTH = 350;
const CANONICAL_HEIGHT = 225;
const modes = ["blur", "tunnel", "central_loss", "cataract", "dog"];
const strengths = [40, 100];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function makeSvg(width, height) {
  const stripes = Array.from({ length: 35 }, (_, index) => {
    const x = index * 40;
    const fill = index % 2 === 0 ? "#151515" : "#f2f0e8";
    return `<rect x="${x}" y="0" width="40" height="900" fill="${fill}"/>`;
  }).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 1400 900">
    <rect width="1400" height="900" fill="#d8d1c3"/>
    ${stripes}
    <rect x="0" y="560" width="1400" height="340" fill="#5b7893" opacity="0.72"/>
    <circle cx="350" cy="260" r="125" fill="#cf5d47"/>
    <circle cx="700" cy="310" r="95" fill="#4f9c68"/>
    <circle cx="1050" cy="250" r="145" fill="#d2b84f"/>
    <rect x="520" y="605" width="360" height="120" fill="#3b2d25"/>
    <path d="M120 780 L350 620 L540 805 Z" fill="#e4ddd0"/>
    <path d="M930 790 L1120 610 L1320 805 Z" fill="#211f20"/>
  </svg>`;
}

function uploadFile(width, height) {
  return {
    name: `r12-${width}x${height}.svg`,
    mimeType: "image/svg+xml",
    buffer: Buffer.from(makeSvg(width, height)),
  };
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

async function waitForNewApproximation(page, previous) {
  await page.waitForFunction(
    (prior) => {
      const card = document.querySelector(".compare-card");
      const current = document.querySelector('img[alt="Approximation"]')?.getAttribute("src");
      return card?.getAttribute("aria-busy") === "false"
        && Boolean(current && current.startsWith("blob:") && current !== prior);
    },
    previous,
    { timeout: 12_000 },
  );
}

async function selectMode(page, mode) {
  const category = mode === "dog" ? "Animal" : "Human";
  if ((await page.locator("#category-select").inputValue()) !== category) {
    await page.locator("#category-select").selectOption(category);
    await page.waitForFunction(
      (expected) => document.querySelector("#category-select")?.value === expected,
      category,
      { timeout: 5_000 },
    );
    await page.waitForTimeout(140);
    await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10_000 });
  }

  if ((await page.locator("#mode-select").inputValue()) !== mode) {
    const before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
    await page.locator("#mode-select").selectOption(mode);
    if (before?.startsWith("blob:")) {
      await waitForNewApproximation(page, before);
    } else {
      await page.waitForTimeout(140);
      await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10_000 });
    }
  }
}

async function setStrength(page, strength) {
  if (Number(await page.locator("#strength-range").inputValue()) === strength) return;
  const before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
  await setReactRangeValue(page, "#strength-range", strength);
  if (before?.startsWith("blob:")) {
    await waitForNewApproximation(page, before);
  } else {
    await page.waitForTimeout(140);
    await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10_000 });
  }
}

async function uploadAndWait(page, file) {
  const beforeOriginal = await page.locator('img[alt="Original"]').first().getAttribute("src");
  const beforeApproximation = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
  await page.locator('input[type="file"]').setInputFiles(file);
  await page.waitForFunction(
    (prior) => {
      const src = document.querySelector('img[alt="Original"]')?.getAttribute("src");
      return Boolean(src && src.startsWith("blob:") && src !== prior);
    },
    beforeOriginal,
    { timeout: 10_000 },
  );
  await waitForNewApproximation(page, beforeApproximation);
}

async function normalizedPixels(page, selector) {
  return page.locator(selector).first().evaluate(async (img, size) => {
    if (!(img instanceof HTMLImageElement)) throw new Error("expected image element");
    if (!img.complete) await img.decode();
    const canvas = document.createElement("canvas");
    canvas.width = size.width;
    canvas.height = size.height;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("canvas unavailable");
    ctx.drawImage(img, 0, 0, size.width, size.height);
    return Array.from(ctx.getImageData(0, 0, size.width, size.height).data);
  }, { width: CANONICAL_WIDTH, height: CANONICAL_HEIGHT });
}

function comparePixels(a, b) {
  assert(a.length === b.length, `pixel array length mismatch ${a.length} vs ${b.length}`);
  const diffs = [];
  let sum = 0;
  for (let i = 0; i < a.length; i += 4) {
    for (let c = 0; c < 3; c += 1) {
      const diff = Math.abs(a[i + c] - b[i + c]);
      diffs.push(diff);
      sum += diff;
    }
  }
  diffs.sort((x, y) => x - y);
  return {
    meanChannelError: Number((sum / diffs.length).toFixed(3)),
    p95ChannelError: diffs[Math.floor((diffs.length - 1) * 0.95)],
    p99ChannelError: diffs[Math.floor((diffs.length - 1) * 0.99)],
    maxChannelError: diffs[diffs.length - 1],
  };
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await context.newPage();
const pageErrors = [];
const consoleErrors = [];
page.on("pageerror", (error) => pageErrors.push(String(error)));
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});

const rows = [];
let baseline = null;

try {
  await page.goto(`${BASE}/?r12_resolution=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  await page.locator("#workspace").waitFor();

  await selectMode(page, "blur");
  await setStrength(page, 40);
  await uploadAndWait(page, uploadFile(350, 225));
  const originalSmall = await normalizedPixels(page, 'img[alt="Original"]');
  await uploadAndWait(page, uploadFile(1400, 900));
  const originalLarge = await normalizedPixels(page, 'img[alt="Original"]');
  baseline = comparePixels(originalSmall, originalLarge);
  console.log(`R12 original baseline: mean=${baseline.meanChannelError} p95=${baseline.p95ChannelError} p99=${baseline.p99ChannelError}`);

  for (const mode of modes) {
    await selectMode(page, mode);
    for (const strength of strengths) {
      await setStrength(page, strength);
      await uploadAndWait(page, uploadFile(350, 225));
      const small = await normalizedPixels(page, 'img[alt="Approximation"]');
      await uploadAndWait(page, uploadFile(1400, 900));
      const large = await normalizedPixels(page, 'img[alt="Approximation"]');

      const metrics = comparePixels(small, large);
      const row = { mode, strength, ...metrics };
      rows.push(row);
      console.log(`R12 ${mode} Strength=${strength}: mean=${metrics.meanChannelError} p95=${metrics.p95ChannelError} p99=${metrics.p99ChannelError} max=${metrics.maxChannelError}`);
    }
  }

  await fs.writeFile(
    OUT,
    JSON.stringify({
      checkedAt: new Date().toISOString(),
      baseUrl: BASE,
      canonicalSize: [CANONICAL_WIDTH, CANONICAL_HEIGHT],
      comparedSourceSizes: [[350, 225], [1400, 900]],
      baseline,
      rows,
      pageErrors,
      consoleErrors,
    }, null, 2),
  );

  assert(baseline.meanChannelError <= 0.25, `R12 original source baseline too different: ${JSON.stringify(baseline)}`);
  assert(pageErrors.length === 0, `R12 page errors: ${pageErrors.join(" | ")}`);
  assert(consoleErrors.length === 0, `R12 console errors: ${consoleErrors.join(" | ")}`);
} finally {
  await context.close();
  await browser.close();
}
