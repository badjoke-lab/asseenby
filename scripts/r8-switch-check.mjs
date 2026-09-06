import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import { chromium } from "playwright";

const preview = spawn(process.execPath, ["node_modules/vite/bin/vite.js", "preview", "--host", "127.0.0.1"], {
  stdio: ["ignore", "pipe", "pipe"],
});

let previewLog = "";
preview.stdout.on("data", (chunk) => { previewLog += chunk.toString(); });
preview.stderr.on("data", (chunk) => { previewLog += chunk.toString(); });

async function waitForPreview() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch("http://127.0.0.1:4173/");
      if (response.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`Preview did not start.\n${previewLog}`);
}

function stopPreview() {
  return new Promise((resolve) => {
    if (preview.exitCode !== null) return resolve();
    const timer = setTimeout(() => {
      preview.kill("SIGKILL");
    }, 1500);
    preview.once("exit", () => {
      clearTimeout(timer);
      resolve();
    });
    preview.kill("SIGTERM");
  });
}

const failures = [];
await fs.mkdir("r8-switch-check", { recursive: true });

try {
  await waitForPreview();
  const browser = await chromium.launch({ headless: true });

  async function check(width, height, label) {
    const page = await browser.newPage({ viewport: { width, height } });
    page.on("pageerror", (error) => failures.push(`${label} pageerror: ${error.message}`));
    page.on("console", (message) => {
      if (message.type() === "error") failures.push(`${label} console: ${message.text()}`);
    });

    await page.goto("http://127.0.0.1:4173/", { waitUntil: "domcontentloaded" });
    const nav = page.getByRole("navigation", { name: "AsSeenBy experience" });
    await nav.waitFor({ state: "visible" });
    const image = nav.getByRole("link", { name: "Compare image", exact: true });
    const spatial = nav.getByRole("link", { name: "Explore 3D", exact: true });
    const imageBox = await image.boundingBox();
    const spatialBox = await spatial.boundingBox();

    if (!imageBox || !spatialBox) failures.push(`${label}: switch links have no bounding box`);
    if (width <= 640 && ((imageBox?.height ?? 0) < 44 || (spatialBox?.height ?? 0) < 44)) {
      failures.push(`${label}: switch tap target is below 44px`);
    }

    const active = await image.evaluate((element) => ({
      display: getComputedStyle(element).display,
      background: getComputedStyle(element).backgroundColor,
    }));
    if (!["flex", "inline-flex"].includes(active.display)) failures.push(`${label}: switch is not styled as a control`);
    if (active.background === "rgba(0, 0, 0, 0)" || active.background === "transparent") {
      failures.push(`${label}: active state has no visible background`);
    }
    if ((await image.getAttribute("aria-current")) !== "page") failures.push(`${label}: Compare image lost aria-current`);

    const metrics = await page.evaluate(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
    }));
    if (metrics.scrollWidth > metrics.clientWidth + 1) {
      failures.push(`${label}: horizontal overflow ${metrics.scrollWidth} > ${metrics.clientWidth}`);
    }

    await page.screenshot({ path: `r8-switch-check/${label}.png`, fullPage: true });
    await page.close();
  }

  await check(1440, 1000, "desktop");
  await check(390, 844, "mobile");
  await browser.close();
} finally {
  await stopPreview();
}

await fs.writeFile("r8-switch-check/result.json", JSON.stringify({ ok: failures.length === 0, failures }, null, 2));
if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
