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
      const canvasLocator = page.locator('canvas.spatial-canvas[data-scene-id="photo-reference"][data-observer-id="human"]');
      await canvasLocator.waitFor({ state: "visible", timeout: 4_000 });
      const sceneValue = await page.locator("#spatial-scene-select").inputValue({ timeout: 2_000 });
      const observerValue = await page.locator("#spatial-observer-select").inputValue({ timeout: 2_000 });
      const architectureCard = await page.locator('.spatial-card[data-scene-id="photo-reference"][data-observer-id="human"]').count();
      const visionGroup = await page.getByRole("group", { name: "Vision", exact: true }).count();
      const canvas = await canvasLocator.count();
      if (
        sceneValue === "photo-reference"
        && observerValue === "human"
        && architectureCard === 1
        && visionGroup === 1
        && canvas === 1
      ) {
        result.notes.push(`${label}: Explore 3D Scene/Observer/Vision architecture detected on attempt ${attempt}`);
        return;
      }
    } catch {
      // Deployment may still be serving the pre-E1 panorama-only shell or Three.js may still be mounting.
    }
    if (attempt < 12) await page.waitForTimeout(5_000);
  }
  throw new Error(`${label}: current Explore 3D Scene/Observer/Vision architecture was not detected`);
}
'''
if old not in text:
    raise SystemExit('E1 architecture helper marker not found')
path.write_text(text.replace(old, new, 1))
