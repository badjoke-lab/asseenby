from pathlib import Path

p = Path('.github/production-smoke.mjs')
text = p.read_text()

old = '''const expectedSpatialModes = [
  "Normal",
  "Tunnel Vision",
  "Central Loss",
  "Night / Low Light",
  "Dog-like",
  "Cataract-like",
];'''
new = old + '''
const expectedGeometryHumanVisionModes = [
  "Normal",
  "Tunnel Vision",
  "Central Loss",
  "Night / Low Light",
  "Cataract-like",
];'''
if old not in text:
    raise SystemExit('expectedSpatialModes block missing')
text = text.replace(old, new, 1)

text = text.replace('''  e3HumanMovementDetected: false,
  desktopImage: false,''', '''  e3HumanMovementDetected: false,
  e4HumanVisionDetected: false,
  desktopImage: false,''', 1)

text = text.replace('''        && JSON.stringify(visionButtons) === JSON.stringify(["Normal"])
        && canvas.clientWidth > 0''', '''        && JSON.stringify(visionButtons) === JSON.stringify(expectedGeometryHumanVisionModes)
        && canvas.clientWidth > 0''', 1)

old = '''        result.e3HumanMovementDetected = true;
        result.notes.push(`${label}: current E3 Human bounded-movement fingerprint detected on attempt ${attempt}`);
        return;'''
new = '''        result.e3HumanMovementDetected = true;

        const e4Baseline = await canvas.evaluate((element) => ({
          scene: element.dataset.sceneId,
          observer: element.dataset.observerId,
          position: element.dataset.cameraPosition,
          yaw: element.dataset.cameraYaw,
          pitch: element.dataset.cameraPitch,
          fov: element.dataset.cameraFov,
          viewpoint: element.dataset.cameraViewpoint,
        }));
        const e4Modes = [
          ["Tunnel Vision", "tunnel"],
          ["Central Loss", "central_loss"],
          ["Night / Low Light", "night"],
          ["Cataract-like", "cataract"],
          ["Normal", "normal"],
        ];
        const e4Group = page.getByRole("group", { name: "Vision" });
        for (const [modeLabel, modeId] of e4Modes) {
          await e4Group.getByRole("button", { name: modeLabel, exact: true }).click();
          await page.waitForTimeout(100);
          const state = await canvas.evaluate((element) => ({
            scene: element.dataset.sceneId,
            observer: element.dataset.observerId,
            position: element.dataset.cameraPosition,
            yaw: element.dataset.cameraYaw,
            pitch: element.dataset.cameraPitch,
            fov: element.dataset.cameraFov,
            viewpoint: element.dataset.cameraViewpoint,
            vision: element.dataset.visionMode,
          }));
          assert(state.vision === modeId, `${label}: E4 ${modeLabel} runtime did not activate (${JSON.stringify(state)})`);
          for (const key of ["scene", "observer", "position", "yaw", "pitch", "fov", "viewpoint"]) {
            assert(state[key] === e4Baseline[key], `${label}: E4 ${modeLabel} changed ${key}: ${e4Baseline[key]} -> ${state[key]}`);
          }
        }
        result.e4HumanVisionDetected = true;
        result.notes.push(`${label}: current E3 Human bounded-movement + E4 geometry Vision fingerprint detected on attempt ${attempt}`);
        return;'''
if old not in text:
    raise SystemExit('E3 return block missing')
text = text.replace(old, new, 1)

text = text.replace('''  assert(JSON.stringify(labels) === JSON.stringify(["Normal"]), `desktop spatial: E2 geometry must expose Normal only, got ${JSON.stringify(labels)}`);''', '''  assert(JSON.stringify(labels) === JSON.stringify(expectedGeometryHumanVisionModes), `desktop spatial: E4 geometry Human Vision set regressed ${JSON.stringify(labels)}`);''', 1)
text = text.replace('''  assert(JSON.stringify(await group.getByRole("button").allTextContents()) === JSON.stringify(["Normal"]), "mobile spatial: E2 geometry exposes non-Normal Vision");''', '''  assert(JSON.stringify(await group.getByRole("button").allTextContents()) === JSON.stringify(expectedGeometryHumanVisionModes), "mobile spatial: E4 geometry Human Vision set regressed");''', 1)

# Add a mobile same-state Vision switch check before free movement.
old = '''  const beforeFreeMove = await canvas.getAttribute("data-camera-position");
  const forwardButton = page.getByRole("button", { name: "Move forward", exact: true });'''
new = '''  const mobileVisionBaseline = await canvas.evaluate((element) => ({
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    viewpoint: element.dataset.cameraViewpoint,
  }));
  await group.getByRole("button", { name: "Central Loss", exact: true }).click();
  await page.waitForTimeout(100);
  const mobileVisionAfter = await canvas.evaluate((element) => ({
    position: element.dataset.cameraPosition,
    yaw: element.dataset.cameraYaw,
    pitch: element.dataset.cameraPitch,
    fov: element.dataset.cameraFov,
    viewpoint: element.dataset.cameraViewpoint,
    vision: element.dataset.visionMode,
  }));
  assert(mobileVisionAfter.vision === "central_loss", "mobile spatial: E4 Central Loss did not activate");
  for (const key of ["position", "yaw", "pitch", "fov", "viewpoint"]) assert(mobileVisionAfter[key] === mobileVisionBaseline[key], `mobile spatial: E4 Vision switch changed ${key}`);
  await group.getByRole("button", { name: "Normal", exact: true }).click();
  await page.waitForTimeout(80);

  const beforeFreeMove = await canvas.getAttribute("data-camera-position");
  const forwardButton = page.getByRole("button", { name: "Move forward", exact: true });'''
if old not in text:
    raise SystemExit('mobile free movement marker missing')
text = text.replace(old, new, 1)

p.write_text(text)
print('E4 production smoke patch applied')
