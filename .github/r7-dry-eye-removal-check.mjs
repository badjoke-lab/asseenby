import { chromium } from "playwright";

const BASE = "http://127.0.0.1:4173";
const expectedHuman = [
  "protan",
  "deutan",
  "tritan",
  "blur",
  "low_contrast",
  "cataract",
  "tunnel",
  "central_loss",
  "night",
];
const expectedSpatial = [
  "Normal",
  "Tunnel Vision",
  "Central Loss",
  "Night / Low Light",
  "Dog-like",
  "Cataract-like",
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function noOverflow(page, label) {
  const metrics = await page.evaluate(() => ({
    inner: innerWidth,
    doc: document.documentElement.scrollWidth,
    body: document.body.scrollWidth,
  }));
  assert(
    metrics.doc <= metrics.inner + 1 && metrics.body <= metrics.inner + 1,
    `${label}: overflow ${JSON.stringify(metrics)}`,
  );
}

function watch(page) {
  const errors = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  return errors;
}

const browser = await chromium.launch({ headless: true });
try {
  for (const viewport of [
    { width: 1440, height: 1000 },
    { width: 390, height: 844 },
  ]) {
    const context = await browser.newContext({
      viewport,
      isMobile: viewport.width === 390,
      hasTouch: viewport.width === 390,
    });
    const page = await context.newPage();
    const errors = watch(page);
    await page.goto(BASE, { waitUntil: "networkidle" });
    await noOverflow(page, `image-${viewport.width}`);

    await page.locator("#category-select").selectOption("Human");
    const human = await page
      .locator("#mode-select option")
      .evaluateAll((nodes) => nodes.map((node) => node.value));
    assert(JSON.stringify(human) === JSON.stringify(expectedHuman), `Human set ${JSON.stringify(human)}`);
    const body = await page.locator("body").innerText();
    assert(!body.includes("Fatigue-like"), "Fatigue-like is still visible");
    assert(!body.includes("Dry-eye-like"), "Dry-eye-like is still visible");
    await page.waitForFunction(() =>
      document.querySelector('img[alt="Approximation"]')?.getAttribute("src")?.startsWith("blob:"),
    );

    await page.locator("#category-select").selectOption("Animal");
    const animal = await page
      .locator("#mode-select option")
      .evaluateAll((nodes) => nodes.map((node) => node.value));
    assert(JSON.stringify(animal) === JSON.stringify(["dog"]), `Animal set ${JSON.stringify(animal)}`);

    await page.locator("#category-select").selectOption("Reference");
    const references = await page
      .locator("#mode-select option")
      .evaluateAll((nodes) => nodes.map((node) => node.value));
    assert(JSON.stringify(references) === JSON.stringify(["age"]), `Reference set ${JSON.stringify(references)}`);

    await noOverflow(page, `image-${viewport.width}-after-controls`);
    assert(errors.length === 0, `image-${viewport.width}: ${errors.join(" | ")}`);
    await context.close();
  }

  for (const viewport of [
    { width: 1440, height: 1000 },
    { width: 390, height: 844 },
  ]) {
    const context = await browser.newContext({
      viewport,
      isMobile: viewport.width === 390,
      hasTouch: viewport.width === 390,
    });
    const page = await context.newPage();
    const errors = watch(page);
    await page.goto(`${BASE}/?view=spatial`, { waitUntil: "networkidle" });
    await page.locator("canvas.spatial-canvas").waitFor({ timeout: 30000 });
    await noOverflow(page, `spatial-${viewport.width}`);
    const labels = await page
      .getByRole("group", { name: "Spatial perception mode" })
      .getByRole("button")
      .allTextContents();
    assert(JSON.stringify(labels) === JSON.stringify(expectedSpatial), `Spatial set ${JSON.stringify(labels)}`);
    assert(errors.length === 0, `spatial-${viewport.width}: ${errors.join(" | ")}`);
    await context.close();
  }
} finally {
  await browser.close();
}
