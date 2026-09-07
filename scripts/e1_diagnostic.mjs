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
await page.goto(`${base}/?view=spatial&architecture_smoke=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
await page.waitForTimeout(1500);
const state = await page.evaluate(() => {
  const scene = document.querySelector("#spatial-scene-select");
  const observer = document.querySelector("#spatial-observer-select");
  const card = document.querySelector('.spatial-card[data-scene-id="photo-reference"][data-observer-id="human"]');
  const vision = document.querySelector('[role="group"][aria-label="Vision"]');
  const canvas = document.querySelector('canvas.spatial-canvas[data-scene-id="photo-reference"][data-observer-id="human"]');
  const checks = {
    sceneIsSelect: scene instanceof HTMLSelectElement,
    sceneValue: scene instanceof HTMLSelectElement ? scene.value : null,
    observerIsSelect: observer instanceof HTMLSelectElement,
    observerValue: observer instanceof HTMLSelectElement ? observer.value : null,
    cardIsElement: card instanceof HTMLElement,
    visionIsElement: vision instanceof HTMLElement,
    canvasIsCanvas: canvas instanceof HTMLCanvasElement,
    canvasClientWidth: canvas instanceof HTMLCanvasElement ? canvas.clientWidth : null,
    canvasClientHeight: canvas instanceof HTMLCanvasElement ? canvas.clientHeight : null,
  };
  return {
    checks,
    exactPredicate: checks.sceneIsSelect
      && checks.sceneValue === "photo-reference"
      && checks.observerIsSelect
      && checks.observerValue === "human"
      && checks.cardIsElement
      && checks.visionIsElement
      && checks.canvasIsCanvas
      && Number(checks.canvasClientWidth) > 0
      && Number(checks.canvasClientHeight) > 0,
    sceneSelects: document.querySelectorAll("#spatial-scene-select").length,
    observerSelects: document.querySelectorAll("#spatial-observer-select").length,
    visionGroups: document.querySelectorAll('[role="group"][aria-label="Vision"]').length,
    canvases: document.querySelectorAll("canvas.spatial-canvas").length,
    errorText: document.querySelector(".spatial-error")?.textContent || null,
  };
});
console.log(JSON.stringify({ state, pageErrors, consoleErrors }, null, 2));
await browser.close();
