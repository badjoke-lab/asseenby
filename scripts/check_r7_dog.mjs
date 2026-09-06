import fs from "node:fs/promises";
import { chromium } from "playwright";

const OUT = "dog-audit";
await fs.mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const failures = [];

function collectErrors(page, label) {
  page.on("pageerror", (error) => failures.push(`${label} pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") failures.push(`${label} console: ${message.text()}`);
  });
}

async function noOverflow(page, label) {
  const metrics = await page.evaluate(() => ({ width: innerWidth, doc: document.documentElement.scrollWidth, body: document.body.scrollWidth }));
  if (metrics.doc > metrics.width + 1 || metrics.body > metrics.width + 1) failures.push(`${label} horizontal overflow: ${JSON.stringify(metrics)}`);
}

async function waitForNewApproximation(page, previous = null) {
  await page.waitForFunction((prior) => {
    const src = document.querySelector('img[alt="Approximation"]')?.getAttribute("src");
    return Boolean(src && src.startsWith("blob:") && src !== prior);
  }, previous, { timeout: 10000 });
  return page.locator('img[alt="Approximation"]').first().getAttribute("src");
}

async function setStrength(page, value) {
  const range = page.locator("#strength-range");
  const previous = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
  await range.fill(String(value));
  const next = await waitForNewApproximation(page, previous);
  await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10000 });
  return next;
}

async function imageDelta(page) {
  return page.evaluate(async () => {
    const original = document.querySelector('img[alt="Original"]');
    const approx = document.querySelector('img[alt="Approximation"]');
    if (!(original instanceof HTMLImageElement) || !(approx instanceof HTMLImageElement)) throw new Error("comparison images missing");
    await Promise.all([original.decode(), approx.decode()]);
    const width = 240;
    const height = 160;
    const a = document.createElement("canvas");
    const b = document.createElement("canvas");
    a.width = b.width = width;
    a.height = b.height = height;
    const ac = a.getContext("2d", { willReadFrequently: true });
    const bc = b.getContext("2d", { willReadFrequently: true });
    if (!ac || !bc) throw new Error("canvas unavailable");
    ac.drawImage(original, 0, 0, width, height);
    bc.drawImage(approx, 0, 0, width, height);
    const ad = ac.getImageData(0, 0, width, height).data;
    const bd = bc.getImageData(0, 0, width, height).data;
    let sum = 0;
    let max = 0;
    for (let i = 0; i < ad.length; i += 4) {
      for (let c = 0; c < 3; c += 1) {
        const d = Math.abs(ad[i + c] - bd[i + c]);
        sum += d;
        if (d > max) max = d;
      }
    }
    return { meanAbsChannelDelta: sum / (width * height * 3), maxChannelDelta: max };
  });
}

async function configureDog(page, label) {
  collectErrors(page, label);
  await page.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });
  await page.locator("#category-select").selectOption("Animal");
  const values = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
  if (JSON.stringify(values) !== JSON.stringify(["dog"])) failures.push(`${label}: unexpected Animal modes ${JSON.stringify(values)}`);
  await page.locator("#mode-select").selectOption("dog");
  await waitForNewApproximation(page);
  await noOverflow(page, label);
}

const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
await configureDog(desktop, "desktop-dog");

const testSvg = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="720" height="480">
  <rect width="720" height="480" fill="#d9d4c8"/>
  <rect x="20" y="20" width="200" height="160" fill="#d52f32"/>
  <rect x="260" y="20" width="200" height="160" fill="#36a34d"/>
  <rect x="500" y="20" width="200" height="160" fill="#2e62ce"/>
  <rect x="20" y="220" width="320" height="80" fill="#f0c63e"/>
  <rect x="380" y="220" width="320" height="80" fill="#6d4da8"/>
  <g fill="#111" font-family="sans-serif" font-size="16">
    ${Array.from({ length: 18 }, (_, i) => `<text x="${22 + (i % 6) * 115}" y="${350 + Math.floor(i / 6) * 38}">DETAIL ${i + 1}</text>`).join("")}
  </g>
</svg>`);
await desktop.locator('input[type="file"]').setInputFiles({ name: "dog-audit.svg", mimeType: "image/svg+xml", buffer: testSvg });
await waitForNewApproximation(desktop);

await setStrength(desktop, 40);
const low = await imageDelta(desktop);
await desktop.screenshot({ path: `${OUT}/dog-strength-40.png`, fullPage: true });

await setStrength(desktop, 100);
const high = await imageDelta(desktop);
await desktop.screenshot({ path: `${OUT}/dog-strength-100.png`, fullPage: true });

if (low.meanAbsChannelDelta <= 1) failures.push(`dog strength 40 appears near no-op: ${JSON.stringify(low)}`);
if (high.meanAbsChannelDelta <= low.meanAbsChannelDelta + 0.5) failures.push(`dog strength scaling not increasing enough: low=${JSON.stringify(low)} high=${JSON.stringify(high)}`);
if (high.maxChannelDelta < 10) failures.push(`dog high-strength output too close to source: ${JSON.stringify(high)}`);

const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
await configureDog(mobile, "mobile-dog");
await mobile.screenshot({ path: `${OUT}/dog-mobile.png`, fullPage: true });

await fs.writeFile(`${OUT}/result.json`, JSON.stringify({ ok: failures.length === 0, low, high, failures }, null, 2));
await desktop.close();
await mobile.close();
await browser.close();

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
