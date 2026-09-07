from pathlib import Path


def replace(path, old, new, count=1):
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"missing patch anchor in {path}: {old[:120]!r}")
    text = text.replace(old, new, count)
    p.write_text(text)

# Observer catalog.
replace(
    "src/spatial/catalog.ts",
    '''export const SPATIAL_OBSERVERS = [
  {
    id: "human",
    label: "Human",
    description: "Human reference observer. Night Intersection supports bounded ground movement with collision-aware navigation; the Photo Reference remains look-only.",
  },
] as const;''',
    '''export const SPATIAL_OBSERVERS = [
  {
    id: "human",
    label: "Human",
    description: "Human reference observer. Night Intersection uses a 1.60 m reference eye height with bounded collision-aware ground movement; the Photo Reference remains look-only.",
  },
  {
    id: "dog",
    label: "Dog",
    description: "Medium-dog reference observer for Night Intersection. Uses a 0.55 m reference eye height and a smaller ground collision envelope; this viewpoint/movement preset is separate from Dog-like Vision.",
  },
] as const;'''
)

# Ground navigation exposes world-ground elevation so observer eye heights are explicit.
replace("src/spatial/sceneRuntime.ts", "  eyeY: number;", "  groundY: number;")
replace("src/spatial/nightIntersectionScene.ts", "  eyeY: 0,", "  groundY: GROUND_Y,")

# Observer profiles.
replace(
    "src/spatial/observerRuntime.ts",
    '''const MOVE_KEYS = new Set(["w", "a", "s", "d", "shift"]);
''',
    '''const MOVE_KEYS = new Set(["w", "a", "s", "d", "shift"]);

const OBSERVER_PROFILES: Record<SpatialObserverId, {
  label: string;
  eyeHeight: number;
  collisionRadius: number;
}> = {
  human: {
    label: "Human reference observer",
    eyeHeight: 1.60,
    collisionRadius: 0.36,
  },
  dog: {
    label: "Medium-dog reference observer",
    eyeHeight: 0.55,
    collisionRadius: 0.28,
  },
};
'''
)
replace(
    "src/spatial/observerRuntime.ts",
    '''  if (observerId !== "human") {
    throw new Error(`Unsupported Explore 3D observer: ${observerId}`);
  }

  let navigation = initialNavigation;''',
    '''  const profile = OBSERVER_PROFILES[observerId];
  let navigation = initialNavigation;'''
)
replace(
    "src/spatial/observerRuntime.ts",
    '''  const updateAria = () => {
    canvas.setAttribute(
      "aria-label",
      navigation
        ? "Explore 3D. Human reference observer. Drag or use arrow keys to look around; use W A S D to move, Shift for faster movement, and R to reset."
        : "Explore 3D. Human reference observer. Drag or use arrow keys to look around; press R to reset the current scene view.",
    );
  };''',
    '''  const updateAria = () => {
    canvas.setAttribute(
      "aria-label",
      navigation
        ? `Explore 3D. ${profile.label}. Drag or use arrow keys to look around; use W A S D to move, Shift for faster movement, and R to reset.`
        : `Explore 3D. ${profile.label}. Drag or use arrow keys to look around; press R to reset the current scene view.`,
    );
  };'''
)
replace(
    "src/spatial/observerRuntime.ts",
    '''    canvas.dataset.observerId = observerId;
    canvas.dataset.observerMovement = movementMode();
    canvas.dataset.cameraViewpoint = viewpoint;''',
    '''    canvas.dataset.observerId = observerId;
    canvas.dataset.observerMovement = movementMode();
    canvas.dataset.observerEyeHeight = profile.eyeHeight.toFixed(2);
    canvas.dataset.observerCollisionRadius = profile.collisionRadius.toFixed(2);
    canvas.dataset.cameraViewpoint = viewpoint;'''
)
text_path = Path("src/spatial/observerRuntime.ts")
text = text_path.read_text()
text = text.replace("navigation.canOccupy(nextX, camera.position.z, navigation.radius)", "navigation.canOccupy(nextX, camera.position.z, profile.collisionRadius)")
text = text.replace("navigation.canOccupy(camera.position.x, nextZ, navigation.radius)", "navigation.canOccupy(camera.position.x, nextZ, profile.collisionRadius)")
text = text.replace("camera.position.y = navigation.eyeY;", "camera.position.y = navigation.groundY + profile.eyeHeight;")
text = text.replace("camera.position.set(target[0], navigation?.eyeY ?? target[1], target[2]);", "camera.position.set(target[0], navigation ? navigation.groundY + profile.eyeHeight : target[1], target[2]);")
text = text.replace("navigation.canOccupy(camera.position.x, camera.position.z, navigation.radius)", "navigation.canOccupy(camera.position.x, camera.position.z, profile.collisionRadius)")
if "navigation.eyeY" in text:
    raise SystemExit("observerRuntime still references navigation.eyeY")
text_path.write_text(text)

# Spatial UI: observer/vision compatibility and copy.
replace(
    "src/SpatialPage.tsx",
    '''const GEOMETRY_HUMAN_VISIONS = new Set<SpatialVisionMode>(["normal", "tunnel", "central_loss", "night", "cataract"]);
''',
    '''const GEOMETRY_HUMAN_VISIONS = new Set<SpatialVisionMode>(["normal", "tunnel", "central_loss", "night", "cataract"]);
const GEOMETRY_DOG_VISIONS = new Set<SpatialVisionMode>(["normal", "dog"]);
'''
)
replace(
    "src/SpatialPage.tsx",
    '''  dog: "Visible-range Dog-like visual proxy on the current Human reference observer. It compresses red/green distinctions and softens fine detail; it does not change observer height or reproduce full canine spectral, motion, field-of-view, or low-light behavior.",''',
    '''  dog: "Visible-range Dog-like visual proxy. It compresses red/green distinctions and softens fine detail; the Vision switch itself does not change observer height, movement, field of view, or reproduce full canine spectral, motion, or low-light behavior.",'''
)
replace(
    "src/SpatialPage.tsx",
    '''          <section className="spatial-note" aria-label="Explore 3D comparison limitation">
            {isGeometryScene ? (
              <>
                <strong>Human geometry comparison:</strong> the 1.6 m Human observer keeps the same bounded ground position, look direction, and FOV while Vision switches among Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like. The modes remain generic research simulations rather than patient-specific reconstructions.
              </>
            ) : (
              <>
                <strong>Comparison rule:</strong> changing only Vision keeps the active Scene, Observer, camera position, look direction, and FOV unchanged. The Photo Reference has no translation depth, so its Human observer remains look-only. Dog-like here is a Vision proxy only; it does not claim a Dog-height observer.
              </>
            )}
          </section>''',
    '''          <section className="spatial-note" aria-label="Explore 3D comparison limitation">
            {isGeometryScene ? observerId === "dog" ? (
              <>
                <strong>Dog observer geometry:</strong> the initial medium-dog reference uses a 0.55 m eye height and smaller collision envelope so cars, curbs, furniture, planting, and people can occlude the scene differently from Human height. Normal separates that physical viewpoint from Dog-like Vision; neither is a claim about every dog or breed.
              </>
            ) : (
              <>
                <strong>Human geometry comparison:</strong> the 1.60 m Human observer keeps the same bounded ground position, look direction, and FOV while Vision switches among Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like. The modes remain generic research simulations rather than patient-specific reconstructions.
              </>
            ) : (
              <>
                <strong>Comparison rule:</strong> changing only Vision keeps the active Scene, Observer, camera position, look direction, and FOV unchanged. The Photo Reference has no translation depth, so its Human observer remains look-only. Dog-like here is a Vision proxy only; it does not claim a Dog-height observer.
              </>
            )}
          </section>'''
)
replace(
    "src/SpatialPage.tsx",
    '''  const observerDefinition = SPATIAL_OBSERVERS.find((item) => item.id === observerId) ?? SPATIAL_OBSERVERS[0];
  const isGeometryScene = sceneId === "night-intersection";
  const visibleVisions = isGeometryScene ? SPATIAL_VISIONS.filter((item) => GEOMETRY_HUMAN_VISIONS.has(item.id)) : SPATIAL_VISIONS;''',
    '''  const observerDefinition = SPATIAL_OBSERVERS.find((item) => item.id === observerId) ?? SPATIAL_OBSERVERS[0];
  const isGeometryScene = sceneId === "night-intersection";
  const visibleObservers = isGeometryScene ? SPATIAL_OBSERVERS : SPATIAL_OBSERVERS.filter((item) => item.id === "human");
  const geometryVisions = observerId === "dog" ? GEOMETRY_DOG_VISIONS : GEOMETRY_HUMAN_VISIONS;
  const visibleVisions = isGeometryScene ? SPATIAL_VISIONS.filter((item) => geometryVisions.has(item.id)) : SPATIAL_VISIONS;'''
)
replace(
    "src/SpatialPage.tsx",
    '''              setViewpoint("baseline");
              if (nextSceneId === "night-intersection" && vision === "dog") setVision("normal");
              setSceneId(nextSceneId);''',
    '''              setViewpoint("baseline");
              if (nextSceneId === "photo-reference" && observerId === "dog") setObserverId("human");
              if (nextSceneId === "night-intersection") {
                const allowed = observerId === "dog" ? GEOMETRY_DOG_VISIONS : GEOMETRY_HUMAN_VISIONS;
                if (!allowed.has(vision)) setVision("normal");
              }
              setSceneId(nextSceneId);'''
)
replace(
    "src/SpatialPage.tsx",
    '''            onChange={(event) => setObserverId(event.target.value as SpatialObserverId)}
          >
            {SPATIAL_OBSERVERS.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}''',
    '''            onChange={(event) => {
              const nextObserverId = event.target.value as SpatialObserverId;
              setViewpoint("baseline");
              if (isGeometryScene) {
                const allowed = nextObserverId === "dog" ? GEOMETRY_DOG_VISIONS : GEOMETRY_HUMAN_VISIONS;
                if (!allowed.has(vision)) setVision("normal");
              }
              setObserverId(nextObserverId);
            }}
          >
            {visibleObservers.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}'''
)
replace(
    "src/SpatialPage.tsx",
    '''        {isGeometryScene ? (
          <p className="spatial-mode-availability">Human geometry Vision uses the same live rendered scene and preserves the current observer/camera state. Dog-like remains a separate Photo Reference Vision proxy until the Dog observer phases.</p>
        ) : null}''',
    '''        {isGeometryScene ? (
          <p className="spatial-mode-availability">
            {observerId === "dog"
              ? "Dog observer keeps its 0.55 m geometry viewpoint while Vision switches between Normal and Dog-like. E6 will refine Dog-like distance/detail behavior separately."
              : "Human geometry Vision uses the same live rendered scene and preserves the current observer/camera state. Select Dog as Observer to separate low viewpoint/movement from Dog-like Vision."}
          </p>
        ) : null}'''
)
replace(
    "src/SpatialPage.tsx",
    '''        <div className="spatial-movement-section" aria-label="Human movement controls">''',
    '''        <div className="spatial-movement-section" aria-label={`${observerDefinition.label} movement controls`}>'''
)
replace(
    "src/SpatialPage.tsx",
    '''        {isGeometryScene
          ? "Night Intersection supports bounded Human ground movement plus same-state Human Vision switching. Walk with W/A/S/D on desktop or the compact mobile controls, use Shift for faster desktop movement, drag to look around, and use Reset observer or R to return to the canonical 1.6 m Human start without changing Vision."
          : "This Photo Reference supports look-around only. Drag or use arrow keys to look around; press R to reset. Changing Vision keeps the exact same Scene, Human observer, viewpoint, direction, and FOV."}''',
    '''        {isGeometryScene
          ? observerId === "dog"
            ? "Night Intersection Dog uses a 0.55 m medium-dog reference eye height with bounded ground movement and a smaller collision envelope. Use Normal to inspect viewpoint/occlusion alone, then Dog-like to add the separate visible-range Vision proxy without moving the observer."
            : "Night Intersection Human uses a 1.60 m reference eye height with bounded ground movement and same-state Human Vision switching. Select Dog as Observer to compare the lower physical viewpoint independently of Dog-like Vision."
          : "This Photo Reference supports look-around only with the Human observer. Drag or use arrow keys to look around; press R to reset. Dog-like here remains a Vision proxy and does not change camera height."}'''
)

# Permanent production regression/fingerprint.
smoke = Path(".github/production-smoke.mjs")
text = smoke.read_text()
text = text.replace(
    '''const expectedGeometryHumanVisionModes = [
  "Normal",
  "Tunnel Vision",
  "Central Loss",
  "Night / Low Light",
  "Cataract-like",
];''',
    '''const expectedGeometryHumanVisionModes = [
  "Normal",
  "Tunnel Vision",
  "Central Loss",
  "Night / Low Light",
  "Cataract-like",
];
const expectedGeometryDogVisionModes = ["Normal", "Dog-like"];''',
    1,
)
text = text.replace("  e4HumanVisionDetected: false,\n  desktopImage", "  e4HumanVisionDetected: false,\n  e5DogObserverDetected: false,\n  desktopImage", 1)
text = text.replace(
    '''      const visionButtons = [...document.querySelectorAll('[role="group"][aria-label="Vision"] button')].map((button) => button.textContent?.trim());
      const sceneValues = scene instanceof HTMLSelectElement ? [...scene.options].map((option) => option.value) : [];
      return scene instanceof HTMLSelectElement''',
    '''      const visionButtons = [...document.querySelectorAll('[role="group"][aria-label="Vision"] button')].map((button) => button.textContent?.trim());
      const sceneValues = scene instanceof HTMLSelectElement ? [...scene.options].map((option) => option.value) : [];
      const observerValues = observer instanceof HTMLSelectElement ? [...observer.options].map((option) => option.value) : [];
      return scene instanceof HTMLSelectElement''',
    1,
)
text = text.replace(
    '''        && observer instanceof HTMLSelectElement
        && observer.value === "human"
        && canvas instanceof HTMLCanvasElement''',
    '''        && observer instanceof HTMLSelectElement
        && observer.value === "human"
        && JSON.stringify(observerValues) === JSON.stringify(["human", "dog"])
        && canvas instanceof HTMLCanvasElement''',
    1,
)
text = text.replace(
    '''        && canvas.dataset.observerMovement === "bounded-ground"
        && document.querySelector('.spatial-reset-button') instanceof HTMLButtonElement''',
    '''        && canvas.dataset.observerMovement === "bounded-ground"
        && canvas.dataset.observerEyeHeight === "1.60"
        && canvas.dataset.observerCollisionRadius === "0.36"
        && document.querySelector('.spatial-reset-button') instanceof HTMLButtonElement''',
    1,
)
old = '''        result.e4HumanVisionDetected = true;
        result.notes.push(`${label}: current E3 Human bounded-movement + E4 geometry Vision fingerprint detected on attempt ${attempt}`);
        return;'''
new = '''        result.e4HumanVisionDetected = true;

        const observerSelect = page.locator("#spatial-observer-select");
        await observerSelect.selectOption("dog");
        await page.waitForTimeout(160);
        const dogLabels = await e4Group.getByRole("button").allTextContents();
        assert(JSON.stringify(dogLabels) === JSON.stringify(expectedGeometryDogVisionModes), `${label}: E5 Dog Vision set mismatch ${JSON.stringify(dogLabels)}`);
        const dogBaseline = await canvas.evaluate((element) => ({
          observer: element.dataset.observerId,
          movement: element.dataset.observerMovement,
          eyeHeight: element.dataset.observerEyeHeight,
          collisionRadius: element.dataset.observerCollisionRadius,
          position: element.dataset.cameraPosition,
          yaw: element.dataset.cameraYaw,
          pitch: element.dataset.cameraPitch,
          fov: element.dataset.cameraFov,
          viewpoint: element.dataset.cameraViewpoint,
          vision: element.dataset.visionMode,
        }));
        assert(dogBaseline.observer === "dog" && dogBaseline.movement === "bounded-ground", `${label}: E5 Dog observer runtime unavailable ${JSON.stringify(dogBaseline)}`);
        assert(dogBaseline.eyeHeight === "0.55" && dogBaseline.collisionRadius === "0.28", `${label}: E5 Dog geometry profile mismatch ${JSON.stringify(dogBaseline)}`);
        assert(dogBaseline.position === "0.000,-1.050,0.000" && dogBaseline.viewpoint === "baseline" && dogBaseline.vision === "normal", `${label}: E5 Dog canonical start mismatch ${JSON.stringify(dogBaseline)}`);

        await canvas.focus();
        await page.keyboard.down("w");
        await page.waitForTimeout(320);
        await page.keyboard.up("w");
        await page.waitForTimeout(120);
        const dogMoved = await canvas.evaluate((element) => ({ position: element.dataset.cameraPosition, viewpoint: element.dataset.cameraViewpoint }));
        assert(dogMoved.position && dogMoved.position !== dogBaseline.position && dogMoved.position.split(",")[1] === "-1.050", `${label}: E5 Dog movement did not preserve low eye height ${JSON.stringify(dogMoved)}`);
        assert(dogMoved.viewpoint === "free", `${label}: E5 Dog movement did not mark free viewpoint`);

        const beforeDogVision = await canvas.evaluate((element) => ({
          position: element.dataset.cameraPosition,
          yaw: element.dataset.cameraYaw,
          pitch: element.dataset.cameraPitch,
          fov: element.dataset.cameraFov,
          viewpoint: element.dataset.cameraViewpoint,
        }));
        await e4Group.getByRole("button", { name: "Dog-like", exact: true }).click();
        await page.waitForTimeout(100);
        const afterDogVision = await canvas.evaluate((element) => ({
          position: element.dataset.cameraPosition,
          yaw: element.dataset.cameraYaw,
          pitch: element.dataset.cameraPitch,
          fov: element.dataset.cameraFov,
          viewpoint: element.dataset.cameraViewpoint,
          vision: element.dataset.visionMode,
        }));
        assert(afterDogVision.vision === "dog", `${label}: E5 Dog-like Vision did not activate`);
        for (const key of ["position", "yaw", "pitch", "fov", "viewpoint"]) {
          assert(afterDogVision[key] === beforeDogVision[key], `${label}: E5 Dog-like Vision changed ${key}`);
        }
        await page.getByRole("button", { name: "Reset observer", exact: true }).click();
        await page.waitForTimeout(100);
        assert((await canvas.getAttribute("data-camera-position")) === "0.000,-1.050,0.000", `${label}: E5 Dog Reset did not restore 0.55 m reference start`);

        await observerSelect.selectOption("human");
        await page.waitForTimeout(140);
        assert((await canvas.getAttribute("data-observer-id")) === "human" && (await canvas.getAttribute("data-camera-position")) === "0.000,0.000,0.000", `${label}: E5 Human observer did not restore Human canonical start`);
        assert(JSON.stringify(await e4Group.getByRole("button").allTextContents()) === JSON.stringify(expectedGeometryHumanVisionModes), `${label}: Human Vision set did not return after Dog observer`);
        result.e5DogObserverDetected = true;
        result.notes.push(`${label}: current E3/E4 + E5 Dog observer fingerprint detected on attempt ${attempt}`);
        return;'''
if old not in text:
    raise SystemExit("E4 smoke return anchor missing")
text = text.replace(old, new, 1)
text = text.replace(
    '''  assert(JSON.stringify(await observerSelect.locator("option").allTextContents()) === JSON.stringify(["Human"]), "desktop spatial: unexpected Observer options");''',
    '''  assert(JSON.stringify(await observerSelect.locator("option").allTextContents()) === JSON.stringify(["Human", "Dog"]), "desktop spatial: unexpected geometry Observer options");''',
    1,
)
# Insert desktop Dog regression before Photo Reference switch.
old = '''  await page.screenshot({ path: path.join(OUT, "desktop-spatial.png"), fullPage: true });

  await sceneSelect.selectOption("photo-reference");'''
new = '''  await page.screenshot({ path: path.join(OUT, "desktop-spatial.png"), fullPage: true });

  await observerSelect.selectOption("dog");
  await page.waitForTimeout(160);
  labels = await modeGroup.getByRole("button").allTextContents();
  assert(JSON.stringify(labels) === JSON.stringify(expectedGeometryDogVisionModes), `desktop spatial: E5 Dog Vision set regressed ${JSON.stringify(labels)}`);
  assert((await canvas.getAttribute("data-camera-position")) === "0.000,-1.050,0.000", "desktop spatial: E5 Dog reference height regressed");
  const dogStateBeforeVision = await canvas.evaluate((element) => ({ position: element.dataset.cameraPosition, yaw: element.dataset.cameraYaw, pitch: element.dataset.cameraPitch, fov: element.dataset.cameraFov, viewpoint: element.dataset.cameraViewpoint }));
  await modeGroup.getByRole("button", { name: "Dog-like", exact: true }).click();
  await page.waitForTimeout(120);
  const dogStateAfterVision = await canvas.evaluate((element) => ({ position: element.dataset.cameraPosition, yaw: element.dataset.cameraYaw, pitch: element.dataset.cameraPitch, fov: element.dataset.cameraFov, viewpoint: element.dataset.cameraViewpoint, vision: element.dataset.visionMode }));
  assert(dogStateAfterVision.vision === "dog", "desktop spatial: E5 Dog-like Vision did not activate at Dog height");
  for (const key of ["position", "yaw", "pitch", "fov", "viewpoint"]) assert(dogStateAfterVision[key] === dogStateBeforeVision[key], `desktop spatial: Dog-like Vision changed Dog ${key}`);
  await page.screenshot({ path: path.join(OUT, "desktop-spatial-dog.png"), fullPage: true });
  await observerSelect.selectOption("human");
  await page.waitForTimeout(120);

  await sceneSelect.selectOption("photo-reference");'''
if old not in text:
    raise SystemExit("desktop photo switch anchor missing")
text = text.replace(old, new, 1)
# Photo Reference exposes Human observer only.
text = text.replace(
    '''  labels = await modeGroup.getByRole("button").allTextContents();
  assert(JSON.stringify(labels) === JSON.stringify(expectedSpatialModes), `desktop spatial: Photo Reference Vision controls regressed ${JSON.stringify(labels)}`);''',
    '''  labels = await modeGroup.getByRole("button").allTextContents();
  assert(JSON.stringify(await observerSelect.locator("option").allTextContents()) === JSON.stringify(["Human"]), "desktop spatial: Photo Reference exposed a non-Human Observer");
  assert(JSON.stringify(labels) === JSON.stringify(expectedSpatialModes), `desktop spatial: Photo Reference Vision controls regressed ${JSON.stringify(labels)}`);''',
    1,
)
# Mobile geometry should expose Human and Dog; add Dog touch regression before photo switch.
text = text.replace(
    '''  assert((await page.locator("#spatial-observer-select").inputValue()) === "human", "mobile spatial: Human Observer is not active");''',
    '''  const mobileObserverSelect = page.locator("#spatial-observer-select");
  assert((await mobileObserverSelect.inputValue()) === "human", "mobile spatial: Human Observer is not active");
  assert(JSON.stringify(await mobileObserverSelect.locator("option").allTextContents()) === JSON.stringify(["Human", "Dog"]), "mobile spatial: E5 geometry Observer options regressed");''',
    1,
)
old = '''  await sceneSelect.selectOption("photo-reference");
  await page.waitForTimeout(700);'''
new = '''  await mobileObserverSelect.selectOption("dog");
  await page.waitForTimeout(140);
  assert(JSON.stringify(await group.getByRole("button").allTextContents()) === JSON.stringify(expectedGeometryDogVisionModes), "mobile spatial: E5 Dog Vision controls regressed");
  assert((await canvas.getAttribute("data-camera-position")) === "0.000,-1.050,0.000", "mobile spatial: E5 Dog reference start regressed");
  const dogForwardButton = page.getByRole("button", { name: "Move forward", exact: true });
  await dogForwardButton.scrollIntoViewIfNeeded();
  const dogForwardBox = await dogForwardButton.boundingBox();
  assert(dogForwardBox, "mobile spatial: Dog Move forward has no bounding box");
  const dogTouch = await context.newCDPSession(page);
  const dogX = dogForwardBox.x + dogForwardBox.width / 2;
  const dogY = dogForwardBox.y + dogForwardBox.height / 2;
  await dogTouch.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: dogX, y: dogY, id: 91, radiusX: 4, radiusY: 4, force: 1 }] });
  await page.waitForTimeout(300);
  await dogTouch.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await page.waitForTimeout(100);
  const mobileDogMoved = await canvas.getAttribute("data-camera-position");
  assert(mobileDogMoved && mobileDogMoved !== "0.000,-1.050,0.000" && mobileDogMoved.split(",")[1] === "-1.050", `mobile spatial: Dog touch movement failed ${mobileDogMoved}`);
  const mobileDogBeforeVision = await canvas.getAttribute("data-camera-position");
  await group.getByRole("button", { name: "Dog-like", exact: true }).click();
  await page.waitForTimeout(100);
  assert((await canvas.getAttribute("data-camera-position")) === mobileDogBeforeVision, "mobile spatial: Dog-like Vision moved Dog observer");
  await page.getByRole("button", { name: "Reset observer", exact: true }).click();
  await page.waitForTimeout(100);
  assert((await canvas.getAttribute("data-camera-position")) === "0.000,-1.050,0.000", "mobile spatial: Dog Reset failed");
  await mobileObserverSelect.selectOption("human");
  await page.waitForTimeout(100);

  await sceneSelect.selectOption("photo-reference");
  await page.waitForTimeout(700);'''
if old not in text:
    raise SystemExit("mobile photo switch anchor missing")
text = text.replace(old, new, 1)
smoke.write_text(text)

# Evidence/model wording now covers geometry Dog observer as well as Photo Reference.
replace(
    "src/spatialEvidence.ts",
    '''      modelNote: "The spatial Dog-like renderer applies a simplified two-channel visible-range color translation plus mild angularly scaled softening to the live 360° view. It is grounded in strong evidence for canine dichromacy and lower visual acuity than humans, but a standard RGB panorama cannot reconstruct canine cone catches for arbitrary spectra and the blur is not a calibrated individual-dog acuity model.",''',
    '''      modelNote: "The spatial Dog-like renderer applies a simplified two-channel visible-range color translation plus mild screen-space softening to the current live rendered frame. It can now be toggled independently at the 0.55 m Dog observer viewpoint on Night Intersection or used as a Human-height proxy on the Photo Reference. Ordinary RGB/display values cannot reconstruct canine cone catches for arbitrary spectra, and the current softening is not yet distance/angular-size calibrated; E6 addresses that renderer refinement separately.",'''
)

# Canonical product documentation.
replace(
    "docs/explore-3d-schedule.md",
    '''Status: **E4 PASS / production verified**

Explore 3D Steps E1 through E4 are production verified. `Night Intersection` is the default real-geometry scene with bounded Human movement and the accepted Human spatial Vision set, while Hansaplatz remains the `360° Photo Reference`. The next queued implementation step is E5 Dog observer.''',
    '''Status: **E5 IMPLEMENTED / release verification pending**

Explore 3D Steps E1 through E4 are production verified. `Night Intersection` now has the E5 medium-dog observer implementation alongside Human, while Hansaplatz remains the Human-only `360° Photo Reference`. E5 requires merge/build/production verification before it is closed.'''
)
replace(
    "docs/explore-3d-schedule.md",
    '''## Step E5 — Dog observer
Status: **queued**

Add a low ground observer, initially around 0.5–0.6 m.

Acceptance:
- lower viewpoint creates materially different occlusion from Human;
- ground collision/navigation remains stable;
- `Normal` can be used at Dog height independently of Dog-like Vision;
- Dog-like Vision can be toggled without camera reset.''',
    '''## Step E5 — Dog observer
Status: **IMPLEMENTED / release verification pending**

Add a low ground observer, initially around 0.5–0.6 m.

Acceptance:
- lower viewpoint creates materially different occlusion from Human;
- ground collision/navigation remains stable;
- `Normal` can be used at Dog height independently of Dog-like Vision;
- Dog-like Vision can be toggled without camera reset.

Implemented E5:
- Night Intersection exposes Human and Dog as separate Observer choices; the 360° Photo Reference remains Human-only because the panorama cannot supply a real Dog-height translation;
- the initial medium-dog reference eye height is 0.55 m above the authored ground, versus the 1.60 m Human reference;
- Dog uses a 0.28 m ground collision radius versus Human 0.36 m, while sharing the same authored navigation/collision map and non-game movement controls;
- Dog geometry Vision exposes exactly Normal and Dog-like, so Normal isolates viewpoint/occlusion while Dog-like adds the separate visible-range proxy;
- switching Normal <-> Dog-like preserves Dog position, direction, FOV and free/guided viewpoint state;
- switching Observer resets to that Scene × Observer canonical start; switching back to Human restores the 1.60 m Human reference start;
- E6 remains responsible for moving Dog-like fine-detail loss toward distance/projected-angular-size behavior.

Validation requirement before merge:
- build;
- rendered Human-vs-Dog same-scene review showing materially different low-viewpoint occlusion/composition;
- Dog keyboard movement, authored bounds, collision, guided viewpoints and Reset at 0.55 m;
- same-state Normal <-> Dog-like switching at Dog height;
- Photo Reference remains Human-only and retains its accepted Vision set;
- real 390px mobile Dog selection, movement, Reset and Dog-like toggle with no overflow/errors;
- full Compare image + E1-E4 Explore 3D regression;
- permanent E5 production stale-release fingerprint.'''
)
replace(
    "docs/explore-3d-spec.md",
    '''Use a low ground viewpoint. The initial generic medium-dog reference should be around 0.5–0.6 m, with future Small / Medium / Large presets allowed because breed/body-size variation is material.''',
    '''Use a low ground viewpoint. The initial implemented generic medium-dog reference is 0.55 m above the authored ground. Future Small / Medium / Large presets remain allowed because breed/body-size variation is material. The 0.55 m value is a product reference, not a universal anatomical claim.'''
)
replace(
    "docs/explore-3d-spec.md",
    '''Ground movement with a lower collision/view envelope than Human. The low viewpoint must materially change occlusion by cars, benches, curbs, plants, street furniture, people, and indoor furniture.''',
    '''Ground movement with a lower collision/view envelope than Human. The initial Night Intersection implementation uses a 0.28 m ground collision radius for Dog versus 0.36 m for Human while sharing the authored navigation map. These are comparison/navigation envelopes rather than measured body-width claims. The low viewpoint must materially change occlusion by cars, benches, curbs, plants, street furniture, people, and indoor furniture.'''
)
replace(
    "docs/methodology.md",
    '''- the Night Intersection Human observer uses a 1.6 m reference eye height with bounded collision-aware ground movement, while the Photo Reference Human observer remains look-only because the panorama contains no translation/parallax depth;
- Vision is independent from Observer state:''',
    '''- Night Intersection now provides a 1.60 m Human reference observer and an initial 0.55 m medium-dog reference observer, both using bounded collision-aware ground movement; the Dog collision envelope is smaller so the low viewpoint/body proxy can occupy a slightly different ground envelope without claiming breed-specific anatomy;
- the Photo Reference remains Human-only and look-only because the panorama contains no translation/parallax depth from which to construct a Dog-height observer;
- Vision is independent from Observer state:'''
)
replace(
    "docs/methodology.md",
    '''- Night Intersection Human Vision currently includes Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like; Dog-like remains a separate Photo Reference Vision proxy until Dog observer work;''',
    '''- Night Intersection Human Vision includes Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like; the Dog observer exposes Normal and Dog-like so the physical low viewpoint can be inspected independently before adding the Dog-like visible-range proxy;'''
)
replace(
    "docs/limitations.md",
    '''`Night Intersection` is a geometry-based scene with real depth/parallax. Its Human observer uses a generic 1.6 m reference eye height and bounded collision-aware ground movement inside an authored walking area. That movement model is a geometric comparison tool, not a measurement of a particular person's body, gait, reach, mobility, or preferred walking speed. Full rigid-body physics is not implied.

`360° Photo Reference` remains a fixed-position photographic source, so its Human observer supports look-around only and cannot provide real camera translation, collision, or parallax. Dog-like remains available there as a **Vision proxy** while the Observer remains Human; that visual switch must not be read as a Dog-height camera or canine movement model. Cat and Bird observers are likewise not claimed until their movement/viewpoint phases exist; Bird flight and Bird spectral/color Vision remain separate requirements.''',
    '''`Night Intersection` is a geometry-based scene with real depth/parallax. Its Human observer uses a generic 1.60 m reference eye height and its initial medium-dog observer uses a 0.55 m reference eye height. Both use bounded collision-aware ground movement inside an authored walking area; Dog uses a smaller 0.28 m navigation radius versus Human 0.36 m. These values are product comparison envelopes, not measurements of a particular person, dog, breed, body width, gait, reach, mobility, or preferred walking speed. Full rigid-body physics is not implied.

`360° Photo Reference` remains a fixed-position photographic source, so it supports the Human look-around observer only and cannot provide real camera-height translation, collision, or parallax. Dog-like remains available there as a **Vision proxy** while the Observer remains Human. On Night Intersection, Dog Observer and Dog-like Vision are separate controls: Normal at Dog height isolates geometry/viewpoint, while Dog-like adds the visual proxy without moving the observer. Cat and Bird observers are likewise not claimed until their movement/viewpoint phases exist; Bird flight and Bird spectral/color Vision remain separate requirements.'''
)
replace(
    "docs/limitations.md",
    '''Canine dichromacy is well supported, including behavioral results that resemble human red-green color deficiency, but ordinary RGB cannot recover original scene spectra or exact canine cone catches. The audited image renderer therefore uses a linear-RGB red-green-deficiency mapping only as a human-display proxy, with restrained contrast and detail changes rather than a bespoke species-specific RGB matrix. The spatial Dog-like renderer remains a separate visible-range proxy on the accepted panorama.''',
    '''Canine dichromacy is well supported, including behavioral results that resemble human red-green color deficiency, but ordinary RGB/display color cannot recover original scene spectra or exact canine cone catches. The audited image renderer therefore uses a linear-RGB red-green-deficiency mapping only as a human-display proxy, with restrained contrast and detail changes rather than a bespoke species-specific RGB matrix. The spatial Dog-like renderer remains a separate visible-range proxy: it can now be toggled at the geometry Dog observer height, but its current fine-detail softening is still screen-space and is not a distance/angular-size canine acuity model until E6 refinement.'''
)
replace(
    "docs/ui-spec.md",
    '''Current Night Intersection × Human Vision controls:
- Normal
- Tunnel Vision
- Central Loss
- Night / Low Light
- Cataract-like

The 360° Photo Reference also exposes Dog-like as a Human-height Vision proxy. Dog-like is accepted and public on that reference scene, but it is not part of the E4 Human geometry Vision set and does not imply a Dog observer.''',
    '''Current Night Intersection Observer choices:
- Human — 1.60 m reference eye height;
- Dog — initial medium-dog 0.55 m reference eye height.

Night Intersection × Human Vision controls:
- Normal
- Tunnel Vision
- Central Loss
- Night / Low Light
- Cataract-like

Night Intersection × Dog Vision controls:
- Normal
- Dog-like

Normal at Dog height is intentionally available so viewpoint/occlusion can be compared independently of Dog-like Vision. The 360° Photo Reference remains Human-only because a fixed panorama cannot provide real Dog-height translation; it still exposes Dog-like as a Human-height Vision proxy.'''
)
replace(
    "docs/modes.md",
    '''- spatial status: accepted post-pilot mode
- spatial renderer: conservative human-display visible-range dichromatic translation plus non-calibrated fine-detail softening''',
    '''- spatial status: accepted; E5 can toggle it independently at the Night Intersection Dog observer height or on the Human-height Photo Reference
- spatial renderer: conservative human-display visible-range dichromatic translation plus non-calibrated screen-space fine-detail softening; E6 separately targets distance/projected-angular-size refinement'''
)
replace(
    "docs/roadmap.md",
    '''- a production-verified E4 Human spatial Vision integration on Night Intersection with Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like.''',
    '''- a production-verified E4 Human spatial Vision integration on Night Intersection with Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like;
- an implemented E5 medium-dog observer on Night Intersection pending release verification, with 0.55 m reference eye height, smaller collision envelope, and Normal/Dog-like Vision separation.'''
)
replace(
    "docs/roadmap.md",
    '''1. add Dog observer in E5, then refine Dog-like 3D detail behavior in E6;''',
    '''1. complete E5 Dog observer release verification, then refine Dog-like 3D detail behavior in E6;'''
)
replace(
    "README.md",
    '''Planned observer families include Human, Dog, Cat and species-specific Bird presets.''',
    '''Night Intersection currently exposes Human and an initial medium-dog Observer; Cat and species-specific Bird observers remain planned.'''
)
replace(
    "README.md",
    '''- Dog/Cat/Bird observer movement and camera height are separate from species-specific visual claims;''',
    '''- Dog Observer movement/camera height is implemented on Night Intersection and remains separate from Dog-like Vision; Cat/Bird observer movement and camera height remain separate from species-specific visual claims;'''
)

print("E5 product/docs patch applied")
