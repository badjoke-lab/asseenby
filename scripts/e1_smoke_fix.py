from pathlib import Path

path = Path('.github/production-smoke.mjs')
text = path.read_text()
old = '''async function waitForExplore3DArchitecture(page, label) {
  for (let attempt = 1; attempt <= 12; attempt += 1) {
    await page.goto(`${BASE}/?view=spatial&architecture_smoke=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    try {
      const sceneValue = await page.locator("#spatial-scene-select").inputValue({ timeout: 2_000 });
      const observerValue = await page.locator("#spatial-observer-select").inputValue({ timeout: 2_000 });
      const exploreLink = await page.getByRole("link", { name: "Explore 3D", exact: true }).count();
      if (sceneValue === "photo-reference" && observerValue === "human" && exploreLink === 1) {
        result.notes.push(`${label}: Explore 3D Scene/Observer/Vision architecture detected on attempt ${attempt}`);
        return;
      }
    } catch {
      // Deployment may still be serving the pre-E1 panorama-only shell.
    }
    if (attempt < 12) await page.waitForTimeout(5_000);
  }
  throw new Error(`${label}: current Explore 3D Scene/Observer/Vision architecture was not detected`);
}
'''
new = '''async function waitForExplore3DArchitecture(page, label) {
  for (let attempt = 1; attempt <= 12; attempt += 1) {
    await page.goto(`${BASE}/?view=spatial&architecture_smoke=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    try {
      await page.waitForFunction(() => {
        const scene = document.querySelector("#spatial-scene-select");
        const observer = document.querySelector("#spatial-observer-select");
        const card = document.querySelector('.spatial-card[data-scene-id="photo-reference"][data-observer-id="human"]');
        const vision = document.querySelector('[role="group"][aria-label="Vision"]');
        const canvas = document.querySelector('canvas.spatial-canvas[data-scene-id="photo-reference"][data-observer-id="human"]');
        return scene instanceof HTMLSelectElement
          && scene.value === "photo-reference"
          && observer instanceof HTMLSelectElement
          && observer.value === "human"
          && card instanceof HTMLElement
          && vision instanceof HTMLElement
          && canvas instanceof HTMLCanvasElement
          && canvas.clientWidth > 0
          && canvas.clientHeight > 0;
      }, undefined, { timeout: 6_000 });
      await page.waitForTimeout(250);
      const stable = await page.evaluate(() => {
        const scene = document.querySelector("#spatial-scene-select");
        const observer = document.querySelector("#spatial-observer-select");
        const card = document.querySelector('.spatial-card[data-scene-id="photo-reference"][data-observer-id="human"]');
        const vision = document.querySelector('[role="group"][aria-label="Vision"]');
        const canvas = document.querySelector('canvas.spatial-canvas[data-scene-id="photo-reference"][data-observer-id="human"]');
        return scene instanceof HTMLSelectElement
          && scene.value === "photo-reference"
          && observer instanceof HTMLSelectElement
          && observer.value === "human"
          && card instanceof HTMLElement
          && vision instanceof HTMLElement
          && canvas instanceof HTMLCanvasElement
          && canvas.clientWidth > 0
          && canvas.clientHeight > 0;
      });
      if (stable) {
        result.notes.push(`${label}: stable Explore 3D Scene/Observer/Vision architecture detected on attempt ${attempt}`);
        return;
      }
    } catch (error) {
      result.notes.push(`${label}: architecture attempt ${attempt} not stable (${error instanceof Error ? error.message : String(error)})`);
    }
    if (attempt < 12) await page.waitForTimeout(5_000);
  }
  throw new Error(`${label}: current Explore 3D Scene/Observer/Vision architecture was not detected`);
}
'''
if old not in text:
    raise SystemExit('E1 architecture helper marker not found')
path.write_text(text.replace(old, new, 1))
