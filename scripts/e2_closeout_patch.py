from pathlib import Path
import re

smoke = Path('.github/production-smoke.mjs')
text = smoke.read_text()
text = text.replace(
    '  productionReleaseDetected: false,\n',
    '  productionReleaseDetected: false,\n  e2SpatialReleaseDetected: false,\n',
    1,
)

architecture = r'''async function waitForExplore3DArchitecture\(page, label\) \{.*?\n\}\n\nasync function desktopSpatialSmoke'''
architecture_replacement = r'''async function waitForExplore3DE2(page, label) {
  for (let attempt = 1; attempt <= 12; attempt += 1) {
    await page.goto(`${BASE}/?view=spatial&e2_release_smoke=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
    await page.waitForTimeout(1_000);
    const stable = await page.evaluate(() => {
      const scene = document.querySelector("#spatial-scene-select");
      const observer = document.querySelector("#spatial-observer-select");
      const canvas = document.querySelector('canvas.spatial-canvas[data-scene-id="night-intersection"][data-observer-id="human"]');
      const visionButtons = [...document.querySelectorAll('[role="group"][aria-label="Vision"] button')].map((button) => button.textContent?.trim());
      const sceneValues = scene instanceof HTMLSelectElement ? [...scene.options].map((option) => option.value) : [];
      return scene instanceof HTMLSelectElement
        && scene.value === "night-intersection"
        && JSON.stringify(sceneValues) === JSON.stringify(["night-intersection", "photo-reference"])
        && observer instanceof HTMLSelectElement
        && observer.value === "human"
        && canvas instanceof HTMLCanvasElement
        && canvas.dataset.sceneSupportsTranslation === "true"
        && Number(canvas.dataset.sceneObjectCount || 0) >= 220
        && Number(canvas.dataset.sceneLightCount || 0) >= 10
        && canvas.dataset.sceneVolume === "150x150x60"
        && canvas.dataset.cameraViewpoint === "baseline"
        && canvas.dataset.visionMode === "normal"
        && JSON.stringify(visionButtons) === JSON.stringify(["Normal"])
        && canvas.clientWidth > 0
        && canvas.clientHeight > 0;
    });
    if (stable) {
      try {
        const canvas = page.locator("canvas.spatial-canvas");
        const baseline = await canvas.evaluate((element) => ({
          position: element.dataset.cameraPosition,
          yaw: element.dataset.cameraYaw,
          pitch: element.dataset.cameraPitch,
          fov: element.dataset.cameraFov,
          viewpoint: element.dataset.cameraViewpoint,
        }));
        const viewpoint = page.getByRole("group", { name: "Comparison viewpoint" });
        await viewpoint.getByRole("button", { name: "Offset", exact: true }).click();
        await page.waitForTimeout(180);
        const offset = await canvas.evaluate((element) => ({
          position: element.dataset.cameraPosition,
          yaw: element.dataset.cameraYaw,
          pitch: element.dataset.cameraPitch,
          fov: element.dataset.cameraFov,
          viewpoint: element.dataset.cameraViewpoint,
        }));
        assert(offset.viewpoint === "offset", `${label}: E2 Offset viewpoint did not activate`);
        assert(offset.position !== baseline.position, `${label}: E2 Offset did not translate the camera`);
        for (const key of ["yaw", "pitch", "fov"]) {
          assert(offset[key] === baseline[key], `${label}: E2 authored translation changed ${key}`);
        }
        await viewpoint.getByRole("button", { name: "Reference", exact: true }).click();
        await page.waitForTimeout(120);
        const restored = await canvas.evaluate((element) => ({ position: element.dataset.cameraPosition, viewpoint: element.dataset.cameraViewpoint }));
        assert(restored.viewpoint === "baseline" && restored.position === baseline.position, `${label}: E2 Reference viewpoint did not restore`);
        result.e2SpatialReleaseDetected = true;
        result.notes.push(`${label}: current E2 Night Intersection fingerprint detected on attempt ${attempt}`);
        return;
      } catch (error) {
        result.notes.push(`${label}: E2 attempt ${attempt} reached geometry but failed authored-translation fingerprint: ${error instanceof Error ? error.message : String(error)}`);
      }
    } else {
      result.notes.push(`${label}: E2 attempt ${attempt} did not reach Night Intersection geometry fingerprint`);
    }
    if (attempt < 12) await page.waitForTimeout(5_000);
  }
  throw new Error(`${label}: current E2 Night Intersection release was not detected`);
}

async function desktopSpatialSmoke'''
text, count = re.subn(architecture, architecture_replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('waitForExplore3DArchitecture block not found')

desktop_pattern = r'''async function desktopSpatialSmoke\(browser\) \{.*?\n\}\n\nasync function mobileSpatialSmoke'''
desktop_replacement = r'''async function desktopSpatialSmoke(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await waitForExplore3DE2(page, "desktop spatial");
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30_000 });
  await noHorizontalOverflow(page, "desktop spatial");
  const spatialNav = page.getByRole("navigation", { name: "Spatial navigation" });
  assert((await spatialNav.getByRole("link", { name: "Compare image", exact: true }).count()) === 1, "desktop spatial: Compare image navigation is missing or duplicated");
  assert((await page.getByRole("link", { name: "Back to image", exact: true }).count()) === 0, "desktop spatial: duplicate Back to image action is still exposed");
  assert((await spatialNav.getByRole("link", { name: "Explore 3D", exact: true }).count()) === 1, "desktop spatial: Explore 3D navigation is missing or duplicated");

  const sceneSelect = page.locator("#spatial-scene-select");
  const observerSelect = page.locator("#spatial-observer-select");
  assert((await sceneSelect.inputValue()) === "night-intersection", "desktop spatial: Night Intersection is not active");
  assert((await observerSelect.inputValue()) === "human", "desktop spatial: Human observer is not active");
  assert(JSON.stringify(await sceneSelect.locator("option").allTextContents()) === JSON.stringify(["Night Intersection", "360° Photo Reference"]), "desktop spatial: unexpected Scene options");
  assert(JSON.stringify(await observerSelect.locator("option").allTextContents()) === JSON.stringify(["Human"]), "desktop spatial: unexpected Observer options");

  const modeGroup = page.getByRole("group", { name: "Vision" });
  let labels = await modeGroup.getByRole("button").allTextContents();
  assert(JSON.stringify(labels) === JSON.stringify(["Normal"]), `desktop spatial: E2 geometry must expose Normal only, got ${JSON.stringify(labels)}`);
  assert(!labels.some((label) => /Cat-like|Bird-like|Bee-like/i.test(label)), "desktop spatial: blocked/rejected animal control exposed");

  const baseline = await canvas.evaluate((element) => ({
    scene: element.dataset.sceneId,
    supportsTranslation: element.dataset.sceneSupportsTranslation,
    objectCount: Number(element.dataset.sceneObjectCount || 0),
    lightCount: Number(element.dataset.sceneLightCount || 0),
    volume: element.dataset.sceneVolume,
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    viewpoint: element.dataset.cameraViewpoint,
  }));
  assert(baseline.scene === "night-intersection" && baseline.supportsTranslation === "true", `desktop spatial: E2 geometry metadata regressed ${JSON.stringify(baseline)}`);
  assert(baseline.objectCount >= 220 && baseline.lightCount >= 10 && baseline.volume === "150x150x60", `desktop spatial: E2 density/volume regressed ${JSON.stringify(baseline)}`);

  await page.waitForTimeout(500);
  const beforeOffset = await canvas.screenshot();
  const viewpoint = page.getByRole("group", { name: "Comparison viewpoint" });
  await viewpoint.getByRole("button", { name: "Offset", exact: true }).click();
  await page.waitForTimeout(220);
  const offset = await canvas.evaluate((element) => ({
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    viewpoint: element.dataset.cameraViewpoint,
  }));
  const afterOffset = await canvas.screenshot();
  assert(offset.viewpoint === "offset" && offset.position !== baseline.position, "desktop spatial: E2 Offset did not translate camera");
  for (const key of ["yaw", "pitch", "fov"]) assert(offset[key] === baseline[key], `desktop spatial: E2 Offset changed ${key}`);
  assert(!beforeOffset.equals(afterOffset), "desktop spatial: E2 translation produced no rendered parallax difference");
  await viewpoint.getByRole("button", { name: "Reference", exact: true }).click();
  await page.waitForTimeout(180);

  const beforeLook = await canvas.screenshot();
  const box = await canvas.boundingBox();
  assert(box, "desktop spatial: canvas has no bounding box");
  await page.mouse.move(box.x + box.width * 0.60, box.y + box.height * 0.52);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.34, box.y + box.height * 0.48, { steps: 8 });
  await page.mouse.up();
  await page.waitForTimeout(180);
  const afterLook = await canvas.screenshot();
  assert(!beforeLook.equals(afterLook), "desktop spatial: drag look-around did not change E2 rendered view");
  await page.screenshot({ path: path.join(OUT, "desktop-spatial.png"), fullPage: true });

  await sceneSelect.selectOption("photo-reference");
  await page.waitForTimeout(800);
  labels = await modeGroup.getByRole("button").allTextContents();
  assert(JSON.stringify(labels) === JSON.stringify(expectedSpatialModes), `desktop spatial: Photo Reference Vision controls regressed ${JSON.stringify(labels)}`);
  const beforeVisionSwitch = await canvas.evaluate((element) => ({
    scene: element.dataset.sceneId,
    observer: element.dataset.observerId,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    position: element.dataset.cameraPosition,
  }));
  const tunnelButton = modeGroup.getByRole("button", { name: "Tunnel Vision", exact: true });
  await tunnelButton.click();
  await page.waitForTimeout(120);
  const afterVisionSwitch = await canvas.evaluate((element) => ({
    scene: element.dataset.sceneId,
    observer: element.dataset.observerId,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    position: element.dataset.cameraPosition,
    vision: element.dataset.visionMode,
  }));
  assert(afterVisionSwitch.vision === "tunnel", `desktop spatial: Photo Reference Vision runtime did not record tunnel (${JSON.stringify(afterVisionSwitch)})`);
  for (const key of ["scene", "observer", "yaw", "pitch", "fov", "position"]) {
    assert(afterVisionSwitch[key] === beforeVisionSwitch[key], `desktop spatial: Vision switch changed ${key}: ${beforeVisionSwitch[key]} -> ${afterVisionSwitch[key]}`);
  }
  for (const label of expectedSpatialModes) {
    const button = modeGroup.getByRole("button", { name: label, exact: true });
    await button.click();
    assert((await button.getAttribute("aria-pressed")) === "true", `desktop spatial: ${label} did not activate on Photo Reference`);
  }

  assertClean(errors, "desktop spatial");
  result.desktopSpatial = true;
  await context.close();
}

async function mobileSpatialSmoke'''
text, count = re.subn(desktop_pattern, desktop_replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('desktopSpatialSmoke block not found')

mobile_pattern = r'''async function mobileSpatialSmoke\(browser\) \{.*?\n\}\n\nconst browser ='''
mobile_replacement = r'''async function mobileSpatialSmoke(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const errors = collectErrors(page);
  await page.goto(`${BASE}/?view=spatial&production_smoke=e2-mobile-${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  const canvas = page.locator("canvas.spatial-canvas");
  await canvas.waitFor({ timeout: 30_000 });
  await noHorizontalOverflow(page, "mobile spatial");
  await assertTouchTargets(page.locator(".topbar a"), "mobile spatial header");
  const spatialNav = page.getByRole("navigation", { name: "Spatial navigation" });
  assert((await spatialNav.getByRole("link", { name: "Compare image", exact: true }).count()) === 1, "mobile spatial: Compare image navigation is missing or duplicated");
  assert((await page.getByRole("link", { name: "Back to image", exact: true }).count()) === 0, "mobile spatial: duplicate Back to image action is still exposed");
  assert((await spatialNav.getByRole("link", { name: "Explore 3D", exact: true }).count()) === 1, "mobile spatial: Explore 3D navigation is missing or duplicated");
  const sceneSelect = page.locator("#spatial-scene-select");
  assert((await sceneSelect.inputValue()) === "night-intersection", "mobile spatial: Night Intersection is not active");
  assert((await page.locator("#spatial-observer-select").inputValue()) === "human", "mobile spatial: Human Observer is not active");
  await assertTouchTargets(page.locator(".spatial-layer-control select"), "mobile spatial Scene/Observer controls");
  const group = page.getByRole("group", { name: "Vision" });
  assert(JSON.stringify(await group.getByRole("button").allTextContents()) === JSON.stringify(["Normal"]), "mobile spatial: E2 geometry exposes non-Normal Vision");

  const baseline = await canvas.evaluate((element) => ({
    scene: element.dataset.sceneId,
    objectCount: Number(element.dataset.sceneObjectCount || 0),
    lightCount: Number(element.dataset.sceneLightCount || 0),
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
  }));
  assert(baseline.scene === "night-intersection" && baseline.objectCount >= 220 && baseline.lightCount >= 10, `mobile spatial: E2 geometry incomplete ${JSON.stringify(baseline)}`);
  const beforeOffset = await canvas.screenshot();
  const viewpoint = page.getByRole("group", { name: "Comparison viewpoint" });
  await viewpoint.getByRole("button", { name: "Offset", exact: true }).click();
  await page.waitForTimeout(220);
  const offset = await canvas.evaluate((element) => ({
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
  }));
  const afterOffset = await canvas.screenshot();
  assert(offset.position !== baseline.position, "mobile spatial: E2 Offset did not translate camera");
  assert(offset.yaw === baseline.yaw && offset.pitch === baseline.pitch && offset.fov === baseline.fov, "mobile spatial: E2 Offset changed direction/FOV");
  assert(!beforeOffset.equals(afterOffset), "mobile spatial: E2 translation produced no rendered parallax difference");
  await page.screenshot({ path: path.join(OUT, "mobile-spatial.png"), fullPage: true });
  await viewpoint.getByRole("button", { name: "Reference", exact: true }).click();

  const beforeLook = await canvas.screenshot();
  const box = await canvas.boundingBox();
  assert(box, "mobile spatial: canvas has no bounding box");
  const cdp = await context.newCDPSession(page);
  const startX = box.x + box.width * 0.68;
  const startY = box.y + box.height * 0.52;
  const endX = box.x + box.width * 0.36;
  const endY = box.y + box.height * 0.48;
  await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: startX, y: startY }] });
  await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: endX, y: endY }] });
  await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await page.waitForTimeout(220);
  const afterLook = await canvas.screenshot();
  assert(!beforeLook.equals(afterLook), "mobile spatial: touch look-around did not change E2 rendered view");

  await sceneSelect.selectOption("photo-reference");
  await page.waitForTimeout(700);
  const photoLabels = await group.getByRole("button").allTextContents();
  assert(JSON.stringify(photoLabels) === JSON.stringify(expectedSpatialModes), `mobile spatial: Photo Reference Vision controls regressed ${JSON.stringify(photoLabels)}`);
  await group.getByRole("button", { name: "Dog-like", exact: true }).click();
  await noHorizontalOverflow(page, "mobile spatial after scene switch");
  assertClean(errors, "mobile spatial");
  result.mobileSpatial = true;
  await context.close();
}

const browser ='''
text, count = re.subn(mobile_pattern, mobile_replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('mobileSpatialSmoke block not found')

smoke.write_text(text)

schedule = Path('docs/explore-3d-schedule.md')
text = schedule.read_text()
text = text.replace('Status: **E2 ACTIVE / Night Intersection geometry baseline**', 'Status: **E2 IMPLEMENTED / release verification pending**', 1)
text = text.replace('## Step E2 — Night Intersection geometry baseline\nStatus: **ACTIVE**', '## Step E2 — Night Intersection geometry baseline\nStatus: **IMPLEMENTED / release verification pending**', 1)
acceptance = '''Acceptance:\n- visible depth/parallax during camera translation;\n- scene no longer reads as a panorama or debug/low-effort environment;\n- Normal mode is useful before adding perception effects;\n- mobile performance remains acceptable.\n'''
implemented = acceptance + '''\nImplemented baseline:\n- `Night Intersection` is the default Explore 3D Scene; Hansaplatz remains separately available as `360° Photo Reference`;\n- authored scene volume is `150x150x60`, with streets, sidewalks/crossings, multi-part buildings, procedural facade detail, storefronts/signs, vehicles, pedestrians, signals, streetlights, furniture, vegetation, wires/roof targets and near/mid/far references;\n- the current optimized scene exposes 471 scene objects and 12 lights, with repeated road markings batched through instancing;\n- Human / Normal is intentionally the only geometry-scene Observer/Vision combination in E2; accepted Photo Reference Vision modes remain available on the photographic scene;\n- `Reference` and `Offset` authored viewpoints translate camera position from `0,0,0` to `3.2,0,-4.2` while preserving yaw, pitch and FOV, providing an explicit parallax proof before E3 free movement;\n- ACES tone mapping, authored practical/emissive lighting and procedural material texture are used; expensive realtime shadow mapping is deferred rather than sacrificing the E2 interaction baseline.\n\nValidation:\n- final E2 visual/browser validation run `34132000347` passed desktop/mobile with no page or console errors; artifact `10022490421` was rendered-reviewed;\n- final validation recorded 471 objects / 12 lights / `150x150x60`, preserved Reference/Offset direction and FOV, produced different rendered canvas output after translation, and retained all accepted Photo Reference Vision controls;\n- CI software-render `loadMs` varied materially between runners and is not used as a release threshold; the permanent release gate checks behavior/scene metadata instead;\n- production verification remains pending until the E2 PR is merged and the E2-specific production fingerprint passes on the public deployment.\n'''
if acceptance not in text:
    raise SystemExit('E2 acceptance block not found')
text = text.replace(acceptance, implemented, 1)
schedule.write_text(text)

roadmap = Path('docs/roadmap.md')
text = roadmap.read_text()
text = text.replace(
    '- a production-verified Explore 3D E1 architecture split that separates Scene / Observer / Vision while retaining the 360° Photo Reference.\n',
    '- a production-verified Explore 3D E1 architecture split that separates Scene / Observer / Vision while retaining the 360° Photo Reference;\n- an implemented E2 `Night Intersection` real-geometry baseline awaiting merged-production verification.\n',
    1,
)
text = text.replace(
    '1. build the first geometry-based `Night Intersection` scene for Explore 3D Step E2;\n2. add bounded Human movement and integrate accepted Human spatial Vision modes;',
    '1. merge and production-verify the implemented `Night Intersection` geometry baseline for Explore 3D Step E2;\n2. add bounded Human movement in E3, then integrate accepted Human spatial Vision modes in E4;',
    1,
)
roadmap.write_text(text)
