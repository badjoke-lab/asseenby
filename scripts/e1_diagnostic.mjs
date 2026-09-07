import { chromium } from "playwright";

const base = process.env.ASSEENBY_PRODUCTION_URL || "http://127.0.0.1:4173";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const pageErrors = [];
const consoleErrors = [];
page.on("pageerror", (error) => pageErrors.push(String(error)));
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
await page.goto(`${base}/?view=spatial&e1_diagnostic=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
await page.waitForTimeout(1500);
const state = await page.evaluate(() => ({
  title: document.title,
  bodyText: document.body.innerText.slice(0, 5000),
  sceneSelects: document.querySelectorAll("#spatial-scene-select").length,
  observerSelects: document.querySelectorAll("#spatial-observer-select").length,
  visionGroups: document.querySelectorAll('[role="group"][aria-label="Vision"]').length,
  canvases: document.querySelectorAll("canvas.spatial-canvas").length,
  errorText: document.querySelector(".spatial-error")?.textContent || null,
  rootHtml: document.querySelector("#root")?.innerHTML.slice(0, 8000) || null,
}));
console.log(JSON.stringify({ state, pageErrors, consoleErrors }, null, 2));
await browser.close();
