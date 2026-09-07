import fs from "node:fs";
import { chromium } from "playwright";

const baseUrl = process.env.ASSEENBY_PRODUCTION_URL || "http://127.0.0.1:4173";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const cases = [
  { name: "wide", width: 1600, height: 900 },
  { name: "square", width: 900, height: 900 },
  { name: "tall", width: 900, height: 1600 },
];
const results = [];

for (const item of cases) {
  await page.goto(`${baseUrl}/?r15=${item.name}-${Date.now()}`, { waitUntil: "networkidle" });
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${item.width}" height="${item.height}" viewBox="0 0 ${item.width} ${item.height}"><rect width="100%" height="100%" fill="rgb(220,220,220)"/></svg>`;
  await page.locator('input[type="file"]').setInputFiles({ name: `${item.name}.svg`, mimeType: "image/svg+xml", buffer: Buffer.from(svg) });
  await page.locator("#category-select").selectOption("Human");
  await page.locator("#mode-select").selectOption("tunnel");
  const before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
  await page.locator("#strength-range").evaluate((element) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
    if (!setter) throw new Error("range value setter unavailable");
    setter.call(element, "100");
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await page.waitForFunction((previous) => {
    const img = document.querySelector('img[alt="Approximation"]');
    return img instanceof HTMLImageElement
      && img.src.startsWith("blob:")
      && img.src !== previous
      && img.complete
      && img.naturalWidth > 0
      && document.querySelector(".compare-card")?.getAttribute("aria-busy") === "false";
  }, before, { timeout: 10_000 });

  const measured = await page.evaluate(async () => {
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
      return Number((luma(a) - luma(b)).toFixed(3));
    };
    return {
      width: output.canvas.width,
      height: output.canvas.height,
      centerDelta: sample(0.5, 0.5),
      topDelta: sample(0.5, 0.05),
      bottomDelta: sample(0.5, 0.95),
      leftDelta: sample(0.05, 0.5),
      rightDelta: sample(0.95, 0.5),
      cornerDelta: sample(0.05, 0.05),
    };
  });
  results.push({ name: item.name, ...measured });
}

await browser.close();
const failures = [];
for (const result of results) {
  if (Math.abs(result.centerDelta) > 2) failures.push(`${result.name}: center delta ${result.centerDelta}`);
  if (result.topDelta < 5 || result.leftDelta < 5) failures.push(`${result.name}: weak edge ${result.topDelta}/${result.leftDelta}`);
  if (Math.abs(result.topDelta - result.leftDelta) > 2) failures.push(`${result.name}: axis gap ${Math.abs(result.topDelta - result.leftDelta)}`);
  if (Math.abs(result.bottomDelta - result.topDelta) > 2) failures.push(`${result.name}: vertical asymmetry`);
  if (Math.abs(result.rightDelta - result.leftDelta) > 2) failures.push(`${result.name}: horizontal asymmetry`);
}
const square = results.find((result) => result.name === "square");
if (!square) failures.push("square case missing");
else {
  if (Math.abs(square.topDelta - 8) > 2 || Math.abs(square.leftDelta - 8) > 2) failures.push(`square endpoint drift ${square.topDelta}/${square.leftDelta}`);
  if (Math.abs(square.cornerDelta - 19) > 3) failures.push(`square corner endpoint drift ${square.cornerDelta}`);
}

const output = { checkedAt: new Date().toISOString(), baseUrl, results, failures, ok: failures.length === 0 };
fs.writeFileSync("r15-tunnel-audit.json", JSON.stringify(output, null, 2));
console.log(JSON.stringify(output, null, 2));
if (failures.length) throw new Error(failures.join(" | "));
