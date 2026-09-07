import { chromium } from "playwright";
import fs from "node:fs/promises";

const BASE = process.env.ASSEENBY_PRODUCTION_URL || "https://asseenby.pages.dev";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const result = {
  checkedAt: new Date().toISOString(),
  baseUrl: BASE,
  attempts: [],
  ok: false,
};

try {
  for (let attempt = 1; attempt <= 8; attempt += 1) {
    await page.goto(`${BASE}/?r13_copy_audit=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    await page.locator("#category-select").selectOption("Human");

    await page.locator("#mode-select").selectOption("protan");
    await page.waitForTimeout(100);
    const protanText = await page.locator("body").innerText();
    const protanCurrent = protanText.includes("Protanomaly-style red-green color-discrimination approximation.")
      && !protanText.includes("Reduced red-channel discrimination approximation.");

    await page.locator("#mode-select").selectOption("deutan");
    await page.waitForTimeout(100);
    const deutanText = await page.locator("body").innerText();
    const deutanCurrent = deutanText.includes("Deuteranomaly-style red-green color-discrimination approximation.")
      && !deutanText.includes("Reduced green-channel discrimination approximation.");

    result.attempts.push({ attempt, protanCurrent, deutanCurrent });
    if (protanCurrent && deutanCurrent) {
      result.ok = true;
      result.passedAttempt = attempt;
      break;
    }
    if (attempt < 8) await page.waitForTimeout(15_000);
  }
} finally {
  await browser.close();
}

await fs.writeFile("r13-production-copy-audit.json", `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result, null, 2));
if (!result.ok) throw new Error("R13 corrected CVD copy was not observed in production within the retry window");
