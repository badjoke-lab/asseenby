import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });

  await page.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });
  await page.locator("#category-select").selectOption("Reference");
  const options = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => ({ value: node.value, text: node.textContent })));
  if (JSON.stringify(options) !== JSON.stringify([{ value: "age", text: "Age Profile" }])) {
    throw new Error(`Reference category still exposes unexpected modes: ${JSON.stringify(options)}`);
  }
  if ((await page.locator("body").innerText()).includes("Sex-difference Profile")) {
    throw new Error("Removed Sex-difference Profile is still visible in the image UI");
  }

  await page.goto("http://127.0.0.1:4173/?view=spatial", { waitUntil: "networkidle" });
  await page.locator("canvas.spatial-canvas").waitFor();
  const spatial = await page.getByRole("group", { name: "Spatial perception mode" }).getByRole("button").allTextContents();
  const expected = ["Normal", "Tunnel Vision", "Central Loss", "Night / Low Light", "Dog-like", "Cataract-like"];
  if (JSON.stringify(spatial) !== JSON.stringify(expected)) {
    throw new Error(`Spatial controls changed unexpectedly: ${JSON.stringify(spatial)}`);
  }
  if (errors.length) throw new Error(`Browser errors: ${errors.join(" | ")}`);
  console.log(JSON.stringify({ referenceModes: options, spatialModes: spatial, ok: true }, null, 2));
} finally {
  await browser.close();
}
