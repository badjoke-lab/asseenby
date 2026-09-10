#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        raise RuntimeError(f"pattern missing in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1))


# Catalog: keep the existing internal scene id for compatibility, but make the
# public scene Hansaplatz and separate time of day from Vision.
catalog = ROOT / "src/spatial/catalog.ts"
catalog.write_text('''export const SPATIAL_SCENES = [
  {
    id: "night-intersection",
    label: "Hansaplatz 3D",
    description: "Geometry-based Hansaplatz, Hamburg scene. Day and Night use the same authored geometry and camera state so lighting can be compared without changing place.",
    supportsTranslation: true,
    status: "Geometry scene",
  },
  {
    id: "photo-reference",
    label: "360° Photo Reference",
    description: "Hansaplatz photographic reference. Look-around only because the source has no translation depth.",
    supportsTranslation: false,
    status: "Photo reference",
  },
] as const;

export type SpatialSceneId = (typeof SPATIAL_SCENES)[number]["id"];

export const SPATIAL_LIGHTING_MODES = [
  {
    id: "day",
    label: "Day",
    description: "Default comparison lighting. Brighter surfaces and broader color/contrast cues make Vision differences easier to inspect.",
  },
  {
    id: "night",
    label: "Night",
    description: "Low-light environment using the same geometry and viewpoint. Use it as a stress test for glare, dark-region contrast, and visibility.",
  },
] as const;

export type SpatialLightingMode = (typeof SPATIAL_LIGHTING_MODES)[number]["id"];

export const SPATIAL_OBSERVERS = [
  {
    id: "human",
    label: "Human",
    description: "Human reference observer. Hansaplatz 3D supports bounded ground movement with collision-aware navigation; the Photo Reference remains look-only.",
  },
] as const;

export type SpatialObserverId = (typeof SPATIAL_OBSERVERS)[number]["id"];

export const SPATIAL_VISIONS = [
  { id: "normal", label: "Normal" },
  { id: "tunnel", label: "Tunnel Vision" },
  { id: "central_loss", label: "Central Loss" },
  { id: "night", label: "Night / Low Light" },
  { id: "dog", label: "Dog-like" },
  { id: "cataract", label: "Cataract-like" },
] as const;

export type SpatialVisionMode = (typeof SPATIAL_VISIONS)[number]["id"];

export type SpatialGuidedViewpoint = "baseline" | "offset";
export type SpatialViewpointState = SpatialGuidedViewpoint | "free";
''')

# Runtime: one geometry, two lighting states. Day is the default. Night retains
# the Hansaplatz panorama only as IBL; it is never projected onto walls.
runtime = ROOT / "src/spatial/sceneRuntime.ts"
text = runtime.read_text()
text = text.replace('import type { SpatialSceneId } from "./catalog";', 'import type { SpatialLightingMode, SpatialSceneId } from "./catalog";', 1)
text = text.replace('  getStreamingDiagnostics: () => SpatialStreamingDiagnostics;\n  dispose: () => void;', '  getStreamingDiagnostics: () => SpatialStreamingDiagnostics;\n  setLightingMode: (mode: SpatialLightingMode) => void;\n  dispose: () => void;', 1)
text = text.replace('const NIGHT_BACKGROUND = new THREE.Color(0x05080d);\nconst HANSAPLATZ_NIGHT_NAVIGATION', 'const DAY_BACKGROUND = new THREE.Color(0xb8d4e8);\nconst NIGHT_BACKGROUND = new THREE.Color(0x05080d);\nconst HANSAPLATZ_NAVIGATION', 1)
text = text.replace('HANSAPLATZ_NIGHT_NAVIGATION', 'HANSAPLATZ_NAVIGATION')

pattern = re.compile(r'const tuneHansaplatzNightLights = \(root: THREE\.Object3D\) => \{.*?\n\};\n\nconst mountHansaplatzNightAccents', re.S)
replacement = '''const tuneHansaplatzLights = (root: THREE.Object3D, mode: SpatialLightingMode) => {
  root.traverse((object) => {
    if (object.name === "night-sky-fill" && object instanceof THREE.HemisphereLight) {
      object.intensity = mode === "day" ? 1.65 : 0.24;
      object.color.set(mode === "day" ? 0xdcecff : 0x7990aa);
      object.groundColor.set(mode === "day" ? 0x8f866f : 0x17120f);
    } else if (object.name === "street-ambient-fill" && object instanceof THREE.AmbientLight) {
      object.intensity = mode === "day" ? 0.34 : 0.05;
      object.color.set(mode === "day" ? 0xfff8e9 : 0x8aa0b5);
    } else if (object.name === "moon-key" && object instanceof THREE.DirectionalLight) {
      object.intensity = mode === "day" ? 2.35 : 0.42;
      object.color.set(mode === "day" ? 0xffefd1 : 0xa8b7d3);
      if (mode === "day") object.position.set(-34, 72, 26);
    } else if (object.name === "intersection-fill" && object instanceof THREE.PointLight) {
      object.intensity = mode === "day" ? 0 : 7.5;
      object.distance = 42;
      object.decay = 2;
    } else if (object.name === "storefront-west-light" && object instanceof THREE.PointLight) {
      object.intensity = mode === "day" ? 0 : 32;
      object.distance = 28;
    } else if (object.name === "storefront-east-light" && object instanceof THREE.PointLight) {
      object.intensity = mode === "day" ? 0 : 28;
      object.distance = 28;
    } else if (object.name.endsWith("-light") && object instanceof THREE.SpotLight) {
      object.intensity = mode === "day" ? 0 : Math.max(object.intensity, 34);
      object.distance = Math.max(object.distance, 30);
    }
  });
};

const mountHansaplatzNightAccents'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise RuntimeError("night light tuning block not found")

marker = '''/**
 * QR2 moves C0's primary-visible responsibility to the Blender-authored chunk.'''
if marker not in text:
    raise RuntimeError("runtime insertion marker missing")
controller = '''const mountHansaplatzLightingController = (
  scene: THREE.Scene,
  root: THREE.Object3D,
  renderScene: () => void,
) => {
  let disposed = false;
  let mode: SpatialLightingMode = "day";
  let nightEnvironment: THREE.Texture | null = null;
  const previousBackground = scene.background;
  const previousEnvironment = scene.environment;
  const previousBackgroundIntensity = scene.backgroundIntensity;
  const previousEnvironmentIntensity = scene.environmentIntensity;
  const nightAccents = scene.getObjectByName("hansaplatz-night-v9-accents");

  const apply = () => {
    tuneHansaplatzLights(root, mode);
    if (nightAccents) nightAccents.visible = mode === "night";
    if (mode === "day") {
      scene.background = DAY_BACKGROUND;
      scene.backgroundIntensity = 1;
      scene.environment = previousEnvironment;
      scene.environmentIntensity = 1;
    } else {
      scene.background = NIGHT_BACKGROUND;
      scene.backgroundIntensity = 1;
      scene.environment = nightEnvironment ?? previousEnvironment;
      scene.environmentIntensity = nightEnvironment ? 0.14 : previousEnvironmentIntensity;
    }
    renderScene();
  };

  new THREE.TextureLoader().load(
    HANSAPLATZ_REFERENCE_URL,
    (texture) => {
      if (disposed) {
        texture.dispose();
        return;
      }
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.mapping = THREE.EquirectangularReflectionMapping;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.magFilter = THREE.LinearFilter;
      texture.anisotropy = 4;
      nightEnvironment = texture;
      if (mode === "night") apply();
    },
    undefined,
    (error) => {
      if (!disposed) console.error("Hansaplatz night IBL failed to load", error);
    },
  );

  apply();
  return {
    setMode: (nextMode: SpatialLightingMode) => {
      mode = nextMode;
      apply();
    },
    dispose: () => {
      disposed = true;
      if (scene.background === DAY_BACKGROUND || scene.background === NIGHT_BACKGROUND) scene.background = previousBackground;
      if (scene.environment === nightEnvironment) scene.environment = previousEnvironment;
      scene.backgroundIntensity = previousBackgroundIntensity;
      scene.environmentIntensity = previousEnvironmentIntensity;
      nightEnvironment?.dispose();
      nightEnvironment = null;
    },
  };
};

'''
text = text.replace(marker, controller + marker, 1)
old_geometry = '''    tuneHansaplatzNightLights(mounted.root);
    const disposeNightAccents = mountHansaplatzNightAccents(scene, renderScene);
    const disposeReferenceEnvironment = loadHansaplatzTexture(scene, renderScene, {
      useAsEnvironment: true,
      showAsBackground: false,
    });
    const chunkRuntime = new SpatialChunkRuntime(scene, NIGHT_INTERSECTION_CHUNKS, renderScene);'''
new_geometry = '''    const disposeNightAccents = mountHansaplatzNightAccents(scene, renderScene);
    const lightingController = mountHansaplatzLightingController(scene, mounted.root, renderScene);
    const chunkRuntime = new SpatialChunkRuntime(scene, NIGHT_INTERSECTION_CHUNKS, renderScene);'''
if old_geometry not in text:
    raise RuntimeError("geometry lighting mount block missing")
text = text.replace(old_geometry, new_geometry, 1)
text = text.replace('      getStreamingDiagnostics: () => ({\n        loadedChunkIds: chunkRuntime.getLoadedChunkIds(),\n        authoredAssetRootCount: countAuthoredAssetRoots(scene),\n      }),\n      dispose: () => {\n        chunkRuntime.dispose();\n        disposeReferenceEnvironment();\n        disposeNightAccents();', '      getStreamingDiagnostics: () => ({\n        loadedChunkIds: chunkRuntime.getLoadedChunkIds(),\n        authoredAssetRootCount: countAuthoredAssetRoots(scene),\n      }),\n      setLightingMode: (mode) => lightingController.setMode(mode),\n      dispose: () => {\n        chunkRuntime.dispose();\n        lightingController.dispose();\n        disposeNightAccents();', 1)
text = text.replace('    getStreamingDiagnostics: () => ({\n      loadedChunkIds: [],\n      authoredAssetRootCount: countAuthoredAssetRoots(scene),\n    }),\n    dispose: disposeReferenceEnvironment,', '    getStreamingDiagnostics: () => ({\n      loadedChunkIds: [],\n      authoredAssetRootCount: countAuthoredAssetRoots(scene),\n    }),\n    setLightingMode: () => {},\n    dispose: disposeReferenceEnvironment,', 1)
runtime.write_text(text)

# React UI: Day is the explicit default and Time of day sits between Scene and Vision.
page = ROOT / "src/SpatialPage.tsx"
text = page.read_text()
text = text.replace('  SPATIAL_OBSERVERS,\n  SPATIAL_SCENES,\n  SPATIAL_VISIONS,', '  SPATIAL_LIGHTING_MODES,\n  SPATIAL_OBSERVERS,\n  SPATIAL_SCENES,\n  SPATIAL_VISIONS,', 1)
text = text.replace('  type SpatialGuidedViewpoint,\n  type SpatialObserverId,', '  type SpatialGuidedViewpoint,\n  type SpatialLightingMode,\n  type SpatialObserverId,', 1)
text = text.replace('  setObserver: (observerId: SpatialObserverId) => void;\n  setVision:', '  setObserver: (observerId: SpatialObserverId) => void;\n  setLighting: (lighting: SpatialLightingMode) => void;\n  setVision:', 1)
text = text.replace('  const [observerId, setObserverId] = useState<SpatialObserverId>("human");\n  const [vision, setVision]', '  const [observerId, setObserverId] = useState<SpatialObserverId>("human");\n  const [lighting, setLighting] = useState<SpatialLightingMode>("day");\n  const [vision, setVision]', 1)
text = text.replace('Night Intersection is the first geometry-based Explore 3D scene, built to make depth, occlusion, authored lighting, and camera translation visible. Hansaplatz remains available as the 360° Photo Reference for photographic same-view Vision comparisons.', 'Hansaplatz 3D now uses one authored geometry for both Day and Night. Day is the default comparison baseline so color, contrast, depth, and detail differences remain easier to inspect; Night is a separate low-light stress test. The 360° Photo Reference remains available for photographic same-view Vision comparisons.', 1)
text = text.replace('            observerId={observerId}\n            vision={vision}', '            observerId={observerId}\n            lighting={lighting}\n            vision={vision}', 1)
text = text.replace('            setObserverId={setObserverId}\n            setVision={setVision}', '            setObserverId={setObserverId}\n            setLighting={setLighting}\n            setVision={setVision}', 1)
text = text.replace('<strong>Human geometry comparison:</strong> the 1.6 m Human observer keeps the same bounded ground position, look direction, and FOV while Vision switches among Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like. The modes remain generic research simulations rather than patient-specific reconstructions.', '<strong>Human geometry comparison:</strong> Day / Night changes only the environment lighting while preserving the same Hansaplatz geometry, observer position, look direction, and FOV. Vision is a separate layer, so Normal + Day is the standard baseline and Night / Low Light remains a perception simulation rather than a time-of-day switch.', 1)
text = text.replace('  observerId,\n  vision,\n  setSceneId,\n  setObserverId,\n  setVision,', '  observerId,\n  lighting,\n  vision,\n  setSceneId,\n  setObserverId,\n  setLighting,\n  setVision,', 1)
text = text.replace('  observerId: SpatialObserverId;\n  vision: SpatialVisionMode;', '  observerId: SpatialObserverId;\n  lighting: SpatialLightingMode;\n  vision: SpatialVisionMode;', 1)
text = text.replace('  setObserverId: (observerId: SpatialObserverId) => void;\n  setVision:', '  setObserverId: (observerId: SpatialObserverId) => void;\n  setLighting: (lighting: SpatialLightingMode) => void;\n  setVision:', 1)
text = text.replace('  useEffect(() => {\n    controllerRef.current?.setObserver(observerId);\n  }, [observerId]);\n\n  useEffect(() => {\n    controllerRef.current?.setVision(vision);', '  useEffect(() => {\n    controllerRef.current?.setObserver(observerId);\n  }, [observerId]);\n\n  useEffect(() => {\n    controllerRef.current?.setLighting(lighting);\n  }, [lighting]);\n\n  useEffect(() => {\n    controllerRef.current?.setVision(vision);', 1)
text = text.replace('    let visionRuntime: SpatialVisionRuntime | null = null;\n    let scene: THREE.Scene | null = null;', '    let visionRuntime: SpatialVisionRuntime | null = null;\n    let scene: THREE.Scene | null = null;\n    let currentLightingMode: SpatialLightingMode = lighting;', 1)
text = text.replace('        activeSceneRuntime = createSpatialSceneRuntime(nextSceneId, scene, renderScene);\n        activeObserverRuntime?.setNavigation(activeSceneRuntime.navigation);', '        activeSceneRuntime = createSpatialSceneRuntime(nextSceneId, scene, renderScene);\n        activeSceneRuntime.setLightingMode(currentLightingMode);\n        activeObserverRuntime?.setNavigation(activeSceneRuntime.navigation);', 1)
text = text.replace('        canvas.dataset.sceneLightCount = String(activeSceneRuntime.lightCount);\n        canvas.dataset.sceneVolume', '        canvas.dataset.sceneLightCount = String(activeSceneRuntime.lightCount);\n        canvas.dataset.sceneLightingMode = currentLightingMode;\n        canvas.dataset.sceneVolume', 1)
text = text.replace('        setScene: applyScene,\n        setObserver: applyObserver,\n        setVision:', '        setScene: applyScene,\n        setObserver: applyObserver,\n        setLighting: (nextLighting) => {\n          currentLightingMode = nextLighting;\n          activeSceneRuntime?.setLightingMode(nextLighting);\n          if (renderer) renderer.toneMappingExposure = nextLighting === "day" ? 1.08 : 1.3;\n          canvas.dataset.sceneLightingMode = nextLighting;\n          renderScene();\n        },\n        setVision:', 1)
text = text.replace('      applyScene(sceneId);\n      applyObserver(observerId);\n      visionRuntime.setVision(vision);', '      applyScene(sceneId);\n      applyObserver(observerId);\n      activeSceneRuntime?.setLightingMode(currentLightingMode);\n      if (renderer) renderer.toneMappingExposure = currentLightingMode === "day" ? 1.08 : 1.3;\n      canvas.dataset.sceneLightingMode = currentLightingMode;\n      visionRuntime.setVision(vision);', 1)
text = text.replace('    <section className="spatial-card" aria-label="Explore 3D" data-scene-id={sceneId} data-observer-id={observerId} data-vision-mode={vision}>', '    <section className="spatial-card" aria-label="Explore 3D" data-scene-id={sceneId} data-observer-id={observerId} data-lighting-mode={lighting} data-vision-mode={vision}>', 1)
observer_marker = '''        <label className="spatial-layer-control" htmlFor="spatial-observer-select">'''
lighting_control = '''        {isGeometryScene ? (
          <label className="spatial-layer-control" htmlFor="spatial-lighting-select">
            <span className="control-label">Time of day</span>
            <select
              id="spatial-lighting-select"
              value={lighting}
              onChange={(event) => setLighting(event.target.value as SpatialLightingMode)}
            >
              {SPATIAL_LIGHTING_MODES.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
            </select>
            <small>{SPATIAL_LIGHTING_MODES.find((item) => item.id === lighting)?.description}</small>
          </label>
        ) : null}

'''
if observer_marker not in text:
    raise RuntimeError("observer control marker missing")
text = text.replace(observer_marker, lighting_control + observer_marker, 1)
text = text.replace('Human geometry Vision uses the same live rendered scene and preserves the current observer/camera state. Dog-like remains a separate Photo Reference Vision proxy until the Dog observer phases.', 'Vision uses the same live rendered geometry and preserves observer/camera state. Time of day is independent: switch Day / Night without changing Vision. Dog-like remains a separate Photo Reference Vision proxy until the Dog observer phases.', 1)
text = text.replace('"Night Intersection supports bounded Human ground movement plus same-state Human Vision switching. Walk with W/A/S/D on desktop or the compact mobile controls, use Shift for faster desktop movement, drag to look around, and use Reset observer or R to return to the canonical 1.6 m Human start without changing Vision."', '"Hansaplatz 3D supports bounded Human ground movement, Day / Night lighting on identical geometry, and same-state Human Vision switching. Day is the default baseline. Walk with W/A/S/D on desktop or the compact mobile controls, drag to look around, and reset without changing Time of day or Vision."', 1)
page.write_text(text)

# Three desktop controls; mobile already collapses to one column.
css = ROOT / "src/spatial.css"
replace_once(css, '  grid-template-columns: repeat(2, minmax(0, 1fr));', '  grid-template-columns: repeat(3, minmax(0, 1fr));')

# Visual proof now checks that Day is default and that Night can be switched on
# without changing geometry/chunk identity.
proof = ROOT / ".github/hansaplatz-lod2-visual-proof.mjs"
text = proof.read_text()
text = text.replace('      observer: canvas.dataset.observerId ?? null,\n      chunks:', '      observer: canvas.dataset.observerId ?? null,\n      lighting: canvas.dataset.sceneLightingMode ?? null,\n      chunks:', 1)
text = text.replace('await captureViewport(desktop, `${OUT}/desktop-forward.png`);\n\nlet turned', '''await captureViewport(desktop, `${OUT}/desktop-forward.png`);

await desktop.selectOption("#spatial-lighting-select", "night");
await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "night");
await desktop.waitForTimeout(350);
const nightLightingState = await readCanvas(desktop);
await captureViewport(desktop, `${OUT}/desktop-night-forward.png`);
await desktop.selectOption("#spatial-lighting-select", "day");
await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "day");
await desktop.waitForTimeout(250);
const dayReturnState = await readCanvas(desktop);

let turned''', 1)
text = text.replace('    && initial?.movement === "bounded-ground"\n    && initial?.position', '    && initial?.movement === "bounded-ground"\n    && initial?.lighting === "day"\n    && nightLightingState?.lighting === "night"\n    && nightLightingState?.roots === initial?.roots\n    && nightLightingState?.chunks === initial?.chunks\n    && dayReturnState?.lighting === "day"\n    && initial?.position', 1)
text = text.replace('  initial,\n  turned,', '  initial,\n  nightLightingState,\n  dayReturnState,\n  turned,', 1)
proof.write_text(text)

# Let the existing Hansaplatz visual workflow cover this and future feature branches.
workflow = ROOT / ".github/workflows/verify-hansaplatz-lod2-visual.yml"
text = workflow.read_text()
text = text.replace('      - feat/c0-hamburg-lod3-quality-20260909\n      - feat/hansaplatz-v10-landmark-plaza-20260911', '      - feat/c0-hamburg-lod3-quality-20260909\n      - "feat/hansaplatz-*"', 1)
workflow.write_text(text)

# Record the architecture change in the spec and roadmap.
for rel, heading, body in [
    ("docs/explore-3d-spec.md", "## Hansaplatz Day / Night baseline policy (2026-09-11)", "- Hansaplatz 3D uses one shared geometry/chunk set for both Day and Night.\n- Day is the default reference environment for Vision comparisons.\n- Night is an environment stress test and is independent from the `Night / Low Light` Vision simulation.\n- Switching Time of day must preserve Scene geometry, observer position, look direction, FOV, and Vision.\n- The Poly Haven Hansaplatz panorama may be used as Night IBL/reference evidence, but raw equirectangular wall projection remains forbidden.\n"),
    ("docs/roadmap.md", "## Explore 3D Day-first comparison update (2026-09-11)", "- Make Hansaplatz Day the standard Explore 3D baseline.\n- Preserve Night as a same-geometry low-light environment for glare/contrast stress testing.\n- Keep Time of day separate from Vision so environmental darkness is not conflated with the Night / Low Light perception model.\n- Continue geometry/material/facade quality work once the Day/Night switch is production-proven.\n"),
]:
    path = ROOT / rel
    existing = path.read_text()
    if heading not in existing:
        path.write_text(existing.rstrip() + "\n\n" + heading + "\n\n" + body)

print("Hansaplatz Day/Night migration applied")
