import { chromium } from "playwright";
import fs from "node:fs/promises";

const BASE = "https://asseenby.pages.dev/";
const WIDTH = 350;
const HEIGHT = 225;

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
  </svg>`;
}

function uploadFile(width, height) {
  return {
    name: `r12-production-${width}x${height}.svg`,
    mimeType: "image/svg+xml",
    buffer: Buffer.from(makeSvg(width, height)),
  };
}

async function waitForNewApproximation(page, previous) {
  await page.waitForFunction(
    (prior) => {
      const card = document.querySelector(".compare-card");
      const src = document.querySelector('img[alt="Approximation"]')?.getAttribute("src");
      return card?.getAttribute("aria-busy") === "false" && Boolean(src?.startsWith("blob:") && src !== prior);
    },
    previous,
    { timeout: 15_000 },
  );
}

async function uploadAndWait(page, file) {
  const beforeOriginal = await page.locator('img[alt="Original"]').first().getAttribute("src");
  const beforeApprox = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
  await page.locator('input[type="file"]').setInputFiles(file);
  await page.waitForFunction(
    (prior) => {
      const src = document.querySelector('img[alt="Original"]')?.getAttribute("src");
      return Boolean(src?.startsWith("blob:") && src !== prior);
    },
    beforeOriginal,
    { timeout: 12_000 },
  );
  await waitForNewApproximation(page, beforeApprox);
}

async function setRange(page, value) {
  const range = page.locator("#strength-range");
  if (Number(await range.inputValue()) === value) return;
  const before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
  await range.evaluate((el, next) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
    if (!setter) throw new Error("range setter unavailable");
    setter.call(el, String(next));
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }, value);
  await waitForNewApproximation(page, before);
}

async function normalizedPixels(page) {
  return page.locator('img[alt="Approximation"]').first().evaluate(async (img, size) => {
    if (!(img instanceof HTMLImageElement)) throw new Error("approximation image missing");
    if (!img.complete) await img.decode();
    const canvas = document.createElement("canvas");
    canvas.width = size.width;
    canvas.height = size.height;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("canvas context unavailable");
    ctx.drawImage(img, 0, 0, size.width, size.height);
    return Array.from(ctx.getImageData(0, 0, size.width, size.height).data);
  }, { width: WIDTH, height: HEIGHT });
}

function meanRgbError(a, b) {
  let sum = 0;
  let count = 0;
  for (let i = 0; i < a.length; i += 4) {
    for (let c = 0; c < 3; c += 1) {
      sum += Math.abs(a[i + c] - b[i + c]);
      count += 1;
    }
  }
  return sum / count;
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await context.newPage();
const pageErrors = [];
page.on("pageerror", (error) => pageErrors.push(String(error)));

try {
  await page.goto(`${BASE}?r12_production=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  await page.locator("#workspace").waitFor({ timeout: 15_000 });
  await page.locator("#category-select").selectOption("Human");

  if ((await page.locator("#mode-select").inputValue()) !== "blur") {
    const before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
    await page.locator("#mode-select").selectOption("blur");
    if (before?.startsWith("blob:")) await waitForNewApproximation(page, before);
  }

  await setRange(page, 100);
  await uploadAndWait(page, uploadFile(350, 225));
  const small = await normalizedPixels(page);
  await uploadAndWait(page, uploadFile(1400, 900));
  const large = await normalizedPixels(page);

  const meanChannelError = meanRgbError(small, large);
  const result = {
    checkedAt: new Date().toISOString(),
    baseUrl: BASE,
    mode: "blur",
    strength: 100,
    sourceSizes: [[350, 225], [1400, 900]],
    meanChannelError: Number(meanChannelError.toFixed(3)),
    threshold: 3,
    pageErrors,
    ok: meanChannelError <= 3 && pageErrors.length === 0,
  };
  console.log(JSON.stringify(result, null, 2));
  await fs.writeFile("r12-production-audit.json", JSON.stringify(result, null, 2));
  if (!result.ok) process.exitCode = 1;
} finally {
  await context.close();
  await browser.close();
}
