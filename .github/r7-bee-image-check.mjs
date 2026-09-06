import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
try {
  const desktop = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  desktop.on("pageerror", (error) => errors.push(String(error)));
  desktop.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  await desktop.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });
  await desktop.locator("#category-select").selectOption("Animal");
  const animal = await desktop.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => ({ value: node.value, text: node.textContent })));
  const expectedAnimal = [
    { value: "dog", text: "Dog-like" },
    { value: "cat", text: "Cat-like" },
    { value: "bird", text: "Bird-like" },
  ];
  if (JSON.stringify(animal) !== JSON.stringify(expectedAnimal)) {
    throw new Error(`Unexpected Animal image modes: ${JSON.stringify(animal)}`);
  }
  if ((await desktop.locator("body").innerText()).includes("Bee-like")) {
    throw new Error("Bee-like is still visible in the image product");
  }
  for (const value of ["dog", "cat", "bird"]) {
    await desktop.locator("#mode-select").selectOption(value);
    await desktop.waitForFunction(() => document.querySelector('img[alt="Approximation"]')?.getAttribute("src")?.startsWith("blob:"));
  }

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  mobile.on("pageerror", (error) => errors.push(String(error)));
  mobile.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  await mobile.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });
  await mobile.locator("#category-select").selectOption("Animal");
  const mobileValues = await mobile.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
  if (JSON.stringify(mobileValues) !== JSON.stringify(["dog", "cat", "bird"])) {
    throw new Error(`Unexpected mobile Animal modes: ${JSON.stringify(mobileValues)}`);
  }
  const overflow = await mobile.evaluate(() => ({ inner: innerWidth, doc: document.documentElement.scrollWidth, body: document.body.scrollWidth }));
  if (overflow.doc > overflow.inner + 1 || overflow.body > overflow.inner + 1) {
    throw new Error(`Mobile horizontal overflow: ${JSON.stringify(overflow)}`);
  }
  if (errors.length) throw new Error(`Browser errors: ${errors.join(" | ")}`);
  console.log(JSON.stringify({ animal, mobileValues, ok: true }, null, 2));
} finally {
  await browser.close();
}
