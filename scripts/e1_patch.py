from pathlib import Path

ROOT = Path('.')
spatial_page_path = ROOT / 'src/SpatialPage.tsx'
original_page = spatial_page_path.read_text()

shader_start = original_page.index('const TUNNEL_SHADER =')
shader_end = original_page.index('\n\nexport default function SpatialPage()')
shader_block = original_page[shader_start:shader_end]

catalog = '''export const SPATIAL_SCENES = [
  {
    id: "photo-reference",
    label: "360° Photo Reference",
    description: "Hansaplatz photographic reference. Look-around only because the source has no translation depth.",
    supportsTranslation: false,
  },
] as const;

export type SpatialSceneId = (typeof SPATIAL_SCENES)[number]["id"];

export const SPATIAL_OBSERVERS = [
  {
    id: "human",
    label: "Human",
    description: "Human reference observer at the source panorama viewpoint. Ground translation begins with geometry scenes, not this photograph.",
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
'''
(ROOT / 'src/spatial').mkdir(parents=True, exist_ok=True)
(ROOT / 'src/spatial/catalog.ts').write_text(catalog)

scene_runtime = '''import * as THREE from "three";
import type { SpatialSceneId } from "./catalog";

export type SpatialSceneRuntime = {
  id: SpatialSceneId;
  supportsTranslation: boolean;
  dispose: () => void;
};

export function createSpatialSceneRuntime(
  sceneId: SpatialSceneId,
  scene: THREE.Scene,
  renderScene: () => void,
): SpatialSceneRuntime {
  if (sceneId !== "photo-reference") {
    throw new Error(`Unsupported Explore 3D scene: ${sceneId}`);
  }

  let disposed = false;
  let activeTexture: THREE.Texture | null = null;
  const loader = new THREE.TextureLoader();
  loader.load(
    "/assets/panoramas/hansaplatz.jpg",
    (texture) => {
      if (disposed) {
        texture.dispose();
        return;
      }
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.mapping = THREE.EquirectangularReflectionMapping;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.magFilter = THREE.LinearFilter;
      activeTexture = texture;
      scene.background = texture;
      renderScene();
    },
    undefined,
    (error) => {
      if (!disposed) console.error("360° Photo Reference failed to load", error);
    },
  );

  return {
    id: sceneId,
    supportsTranslation: false,
    dispose: () => {
      disposed = true;
      if (activeTexture && scene.background === activeTexture) scene.background = null;
      activeTexture?.dispose();
      activeTexture = null;
    },
  };
}
'''
(ROOT / 'src/spatial/sceneRuntime.ts').write_text(scene_runtime)

observer_runtime = '''import * as THREE from "three";
import type { SpatialObserverId } from "./catalog";

export type SpatialObserverSnapshot = {
  id: SpatialObserverId;
  yaw: number;
  pitch: number;
  fov: number;
  position: [number, number, number];
};

export type SpatialObserverRuntime = {
  id: SpatialObserverId;
  movement: "look-only";
  getSnapshot: () => SpatialObserverSnapshot;
  reset: () => void;
  dispose: () => void;
};

type ObserverRuntimeOptions = {
  camera: THREE.PerspectiveCamera;
  canvas: HTMLCanvasElement;
  renderScene: () => void;
};

export function createSpatialObserverRuntime(
  observerId: SpatialObserverId,
  { camera, canvas, renderScene }: ObserverRuntimeOptions,
): SpatialObserverRuntime {
  if (observerId !== "human") {
    throw new Error(`Unsupported observer in the current Photo Reference scene: ${observerId}`);
  }

  let yaw = 0;
  let pitch = -0.01;
  let activePointer: number | null = null;
  let lastX = 0;
  let lastY = 0;

  camera.position.set(0, 0, 0);
  camera.rotation.order = "YXZ";

  const syncCamera = () => {
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;
    canvas.dataset.observerId = observerId;
    canvas.dataset.observerMovement = "look-only";
    canvas.dataset.cameraYaw = yaw.toFixed(6);
    canvas.dataset.cameraPitch = pitch.toFixed(6);
    canvas.dataset.cameraFov = camera.fov.toFixed(3);
    canvas.dataset.cameraPosition = `${camera.position.x.toFixed(3)},${camera.position.y.toFixed(3)},${camera.position.z.toFixed(3)}`;
  };

  const reset = () => {
    yaw = 0;
    pitch = -0.01;
    camera.position.set(0, 0, 0);
    camera.fov = 52;
    camera.updateProjectionMatrix();
    syncCamera();
    renderScene();
  };

  const onPointerDown = (event: PointerEvent) => {
    if (activePointer !== null) return;
    activePointer = event.pointerId;
    lastX = event.clientX;
    lastY = event.clientY;
    canvas.setPointerCapture(event.pointerId);
    canvas.focus({ preventScroll: true });
  };

  const onPointerMove = (event: PointerEvent) => {
    if (activePointer !== event.pointerId) return;
    const dx = event.clientX - lastX;
    const dy = event.clientY - lastY;
    lastX = event.clientX;
    lastY = event.clientY;
    yaw -= dx * 0.0042;
    pitch = THREE.MathUtils.clamp(pitch - dy * 0.0036, -1.08, 1.08);
    syncCamera();
    renderScene();
  };

  const stopPointer = (event: PointerEvent) => {
    if (activePointer !== event.pointerId) return;
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    activePointer = null;
  };

  const onKeyDown = (event: KeyboardEvent) => {
    const step = event.shiftKey ? 0.14 : 0.07;
    if (event.key === "ArrowLeft") yaw += step;
    else if (event.key === "ArrowRight") yaw -= step;
    else if (event.key === "ArrowUp") pitch = THREE.MathUtils.clamp(pitch + step, -1.08, 1.08);
    else if (event.key === "ArrowDown") pitch = THREE.MathUtils.clamp(pitch - step, -1.08, 1.08);
    else if (event.key.toLowerCase() === "r") {
      event.preventDefault();
      reset();
      return;
    } else return;
    event.preventDefault();
    syncCamera();
    renderScene();
  };

  canvas.setAttribute("aria-label", "360 degree Photo Reference. Human reference observer. Drag, use arrow keys, or press R to reset the look direction.");
  canvas.addEventListener("pointerdown", onPointerDown);
  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("pointerup", stopPointer);
  canvas.addEventListener("pointercancel", stopPointer);
  canvas.addEventListener("keydown", onKeyDown);
  syncCamera();

  return {
    id: observerId,
    movement: "look-only",
    getSnapshot: () => ({
      id: observerId,
      yaw,
      pitch,
      fov: camera.fov,
      position: [camera.position.x, camera.position.y, camera.position.z],
    }),
    reset,
    dispose: () => {
      canvas.removeEventListener("pointerdown", onPointerDown);
      canvas.removeEventListener("pointermove", onPointerMove);
      canvas.removeEventListener("pointerup", stopPointer);
      canvas.removeEventListener("pointercancel", stopPointer);
      canvas.removeEventListener("keydown", onKeyDown);
    },
  };
}
'''
(ROOT / 'src/spatial/observerRuntime.ts').write_text(observer_runtime)

vision_runtime = '''import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import type { SpatialVisionMode } from "./catalog";

''' + shader_block + '''

export type SpatialVisionRuntime = {
  setVision: (vision: SpatialVisionMode) => void;
  resize: (width: number, height: number) => void;
  dispose: () => void;
};

export function createSpatialVisionRuntime(
  composer: EffectComposer,
  canvas: HTMLCanvasElement,
  renderScene: () => void,
): SpatialVisionRuntime {
  const bloomPass = new UnrealBloomPass(new THREE.Vector2(1, 1), 1.3, 0.78, 0.62);
  bloomPass.enabled = false;
  composer.addPass(bloomPass);

  const cataractPass = new ShaderPass(CATARACT_SHADER);
  cataractPass.enabled = false;
  composer.addPass(cataractPass);

  const nightPass = new ShaderPass(NIGHT_LOW_LIGHT_SHADER);
  nightPass.enabled = false;
  composer.addPass(nightPass);

  const dogPass = new ShaderPass(DOG_LIKE_SHADER);
  dogPass.enabled = false;
  composer.addPass(dogPass);

  const centralLossPass = new ShaderPass(CENTRAL_LOSS_SHADER);
  centralLossPass.enabled = false;
  composer.addPass(centralLossPass);

  const tunnelPass = new ShaderPass(TUNNEL_SHADER);
  tunnelPass.enabled = false;
  composer.addPass(tunnelPass);
  composer.addPass(new OutputPass());

  const setVision = (vision: SpatialVisionMode) => {
    bloomPass.enabled = false;
    cataractPass.enabled = vision === "cataract";
    nightPass.enabled = vision === "night";
    dogPass.enabled = vision === "dog";
    centralLossPass.enabled = vision === "central_loss";
    tunnelPass.enabled = vision === "tunnel";
    canvas.dataset.visionMode = vision;
    renderScene();
  };

  const resize = (width: number, height: number) => {
    (tunnelPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
    (centralLossPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
    (nightPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
    (dogPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
    (cataractPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
  };

  return {
    setVision,
    resize,
    dispose: () => {
      tunnelPass.material.dispose();
      centralLossPass.material.dispose();
      nightPass.material.dispose();
      dogPass.material.dispose();
      cataractPass.material.dispose();
      bloomPass.dispose();
    },
  };
}
'''
(ROOT / 'src/spatial/visionRuntime.ts').write_text(vision_runtime)

spatial_page = '''import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { ModeEvidencePanel } from "./components/ModeEvidencePanel";
import { MODES } from "./modes";
import { getSpatialModeEvidence } from "./spatialEvidence";
import {
  SPATIAL_OBSERVERS,
  SPATIAL_SCENES,
  SPATIAL_VISIONS,
  type SpatialObserverId,
  type SpatialSceneId,
  type SpatialVisionMode,
} from "./spatial/catalog";
import { createSpatialObserverRuntime, type SpatialObserverRuntime } from "./spatial/observerRuntime";
import { createSpatialSceneRuntime, type SpatialSceneRuntime } from "./spatial/sceneRuntime";
import { createSpatialVisionRuntime, type SpatialVisionRuntime } from "./spatial/visionRuntime";

type SpatialController = {
  setScene: (sceneId: SpatialSceneId) => void;
  setObserver: (observerId: SpatialObserverId) => void;
  setVision: (vision: SpatialVisionMode) => void;
  render: () => void;
};

const VISION_DESCRIPTIONS: Record<SpatialVisionMode, string> = {
  normal: "Baseline scene with no perception simulation.",
  tunnel: "Live screen-relative peripheral field loss. Look around to see how objects outside the center become harder to notice.",
  central_loss: "Live screen-relative central field loss. Center a shop sign, window, lamp, or other detail, then look elsewhere to see the disrupted region stay with straight-ahead vision.",
  night: "Luminance-dependent low-light proxy. Darker scene regions lose more color, contrast, and fine detail while brighter shopfronts and lamps remain more available. It does not model calibrated scotopic luminance or dark-adaptation time.",
  dog: "Visible-range Dog-like visual proxy on the current Human reference observer. It compresses red/green distinctions and softens fine detail; it does not change observer height or reproduce full canine spectral, motion, field-of-view, or low-light behavior.",
  cataract: "Scene-aware haze, softness, lower contrast, warming, and bright-source glare. Turn toward bright shopfronts or streetlights, then toward the dark sky to compare.",
};

export default function SpatialPage() {
  const [sceneId, setSceneId] = useState<SpatialSceneId>("photo-reference");
  const [observerId, setObserverId] = useState<SpatialObserverId>("human");
  const [vision, setVision] = useState<SpatialVisionMode>("normal");
  const evidenceModeKey = vision === "normal" ? null : vision;
  const evidenceMode = evidenceModeKey ? MODES.find((item) => item.key === evidenceModeKey) ?? null : null;

  return (
    <div className="page-shell">
      <div className="page-frame spatial-frame">
        <header className="topbar">
          <a href="/" className="brand">AsSeenBy</a>
          <nav className="topnav" aria-label="Spatial navigation">
            <a href="/">Compare image</a>
            <a href="/?view=spatial" aria-current="page">Explore 3D</a>
            <a href="/support/">Support</a>
          </nav>
        </header>

        <main className="content-area spatial-content">
          <section className="spatial-intro">
            <p className="spatial-kicker">Explore 3D</p>
            <h1 className="spatial-title">Separate the scene, the observer, and the way of seeing.</h1>
            <p className="spatial-lead">
              Explore 3D is organized as Scene / Observer / Vision. The current available Scene is the Hansaplatz 360° Photo Reference, so it supports look-around from the source camera point. Geometry scenes will add translation, depth, occlusion, and observer-specific movement without turning the experience into a game.
            </p>
          </section>

          <SpatialRenderer
            sceneId={sceneId}
            observerId={observerId}
            vision={vision}
            setSceneId={setSceneId}
            setObserverId={setObserverId}
            setVision={setVision}
          />

          <section className="spatial-note" aria-label="Explore 3D comparison limitation">
            <strong>Comparison rule:</strong> changing only Vision keeps the active Scene, Observer, camera position, look direction, and FOV unchanged. The current photographic reference has no translation depth, so its Human observer is deliberately look-only. Dog-like here is a visual proxy only; it does not claim that the camera has become a Dog observer. Species-specific observers and geometry movement are separate implementation steps with their own evidence and model boundaries.
          </section>

          {evidenceModeKey && evidenceMode ? (
            <section className="spatial-evidence" aria-label="Spatial mode evidence">
              <div className="spatial-evidence__intro">
                <div className="control-label">Spatial implementation evidence</div>
                <p>
                  The phenomenon evidence is shared with the corresponding AsSeenBy mode, while the Model score and implementation note below refer specifically to this live Vision renderer.
                </p>
              </div>
              <ModeEvidencePanel mode={evidenceMode} evidence={getSpatialModeEvidence(evidenceModeKey)} />
            </section>
          ) : (
            <section className="spatial-baseline-note" aria-label="Normal mode information">
              <div className="control-label">Normal baseline</div>
              <p>No Vision simulation is applied. Use this view as the reference before switching the Vision layer.</p>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}

function SpatialRenderer({
  sceneId,
  observerId,
  vision,
  setSceneId,
  setObserverId,
  setVision,
}: {
  sceneId: SpatialSceneId;
  observerId: SpatialObserverId;
  vision: SpatialVisionMode;
  setSceneId: (sceneId: SpatialSceneId) => void;
  setObserverId: (observerId: SpatialObserverId) => void;
  setVision: (vision: SpatialVisionMode) => void;
}) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const controllerRef = useRef<SpatialController | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    controllerRef.current?.setScene(sceneId);
  }, [sceneId]);

  useEffect(() => {
    controllerRef.current?.setObserver(observerId);
  }, [observerId]);

  useEffect(() => {
    controllerRef.current?.setVision(vision);
  }, [vision]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    let renderer: THREE.WebGLRenderer | null = null;
    let composer: EffectComposer | null = null;
    let resizeObserver: ResizeObserver | null = null;
    let activeSceneRuntime: SpatialSceneRuntime | null = null;
    let activeObserverRuntime: SpatialObserverRuntime | null = null;
    let visionRuntime: SpatialVisionRuntime | null = null;
    let scene: THREE.Scene | null = null;

    const cleanup = () => {
      controllerRef.current = null;
      resizeObserver?.disconnect();
      activeObserverRuntime?.dispose();
      activeObserverRuntime = null;
      activeSceneRuntime?.dispose();
      activeSceneRuntime = null;
      visionRuntime?.dispose();
      visionRuntime = null;
      composer?.dispose();
      if (renderer) disposeScene(scene, host, renderer);
      renderer = null;
      composer = null;
      scene = null;
    };

    try {
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x05070a);
      scene.fog = null;

      const camera = new THREE.PerspectiveCamera(52, 1, 0.1, 100);
      renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.NoToneMapping;
      renderer.toneMappingExposure = 1.0;
      renderer.shadowMap.enabled = false;
      renderer.domElement.className = "spatial-canvas";
      renderer.domElement.tabIndex = 0;
      renderer.domElement.setAttribute("role", "application");
      host.appendChild(renderer.domElement);

      composer = new EffectComposer(renderer);
      composer.addPass(new RenderPass(scene, camera));
      const renderScene = () => composer?.render();
      const canvas = renderer.domElement;
      visionRuntime = createSpatialVisionRuntime(composer, canvas, renderScene);

      const applyScene = (nextSceneId: SpatialSceneId) => {
        if (!scene || activeSceneRuntime?.id === nextSceneId) return;
        activeSceneRuntime?.dispose();
        activeSceneRuntime = createSpatialSceneRuntime(nextSceneId, scene, renderScene);
        canvas.dataset.sceneId = nextSceneId;
        canvas.dataset.sceneSupportsTranslation = String(activeSceneRuntime.supportsTranslation);
        renderScene();
      };

      const applyObserver = (nextObserverId: SpatialObserverId) => {
        if (activeObserverRuntime?.id === nextObserverId) return;
        activeObserverRuntime?.dispose();
        activeObserverRuntime = createSpatialObserverRuntime(nextObserverId, { camera, canvas, renderScene });
        renderScene();
      };

      controllerRef.current = {
        setScene: applyScene,
        setObserver: applyObserver,
        setVision: (nextVision) => visionRuntime?.setVision(nextVision),
        render: renderScene,
      };

      const resize = () => {
        if (!renderer || !composer || !visionRuntime) return;
        const width = Math.max(1, host.clientWidth);
        const height = Math.max(300, Math.round(width * 0.58));
        renderer.setSize(width, height, false);
        composer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        visionRuntime.resize(width, height);
        renderScene();
      };

      resizeObserver = new ResizeObserver(resize);
      resizeObserver.observe(host);
      resize();
      applyScene(sceneId);
      applyObserver(observerId);
      visionRuntime.setVision(vision);
      return cleanup;
    } catch (cause) {
      cleanup();
      setError(cause instanceof Error ? cause.message : "Explore 3D could not start in this browser.");
    }

    return cleanup;
  }, []);

  const sceneDefinition = SPATIAL_SCENES.find((item) => item.id === sceneId) ?? SPATIAL_SCENES[0];
  const observerDefinition = SPATIAL_OBSERVERS.find((item) => item.id === observerId) ?? SPATIAL_OBSERVERS[0];

  if (error) {
    return (
      <section className="spatial-error" role="status">
        <h2>Explore 3D unavailable</h2>
        <p>{error}</p>
        <p><a href="/">Continue with Compare image</a>.</p>
      </section>
    );
  }

  return (
    <section className="spatial-card" aria-label="Explore 3D" data-scene-id={sceneId} data-observer-id={observerId} data-vision-mode={vision}>
      <div className="spatial-card__header">
        <div>
          <div className="control-label">Current Scene</div>
          <h2>{sceneDefinition.label}</h2>
        </div>
        <span className="spatial-status">Reference scene</span>
      </div>

      <div className="spatial-layer-grid" aria-label="Explore 3D configuration">
        <label className="spatial-layer-control" htmlFor="spatial-scene-select">
          <span className="control-label">Scene</span>
          <select
            id="spatial-scene-select"
            value={sceneId}
            onChange={(event) => setSceneId(event.target.value as SpatialSceneId)}
          >
            {SPATIAL_SCENES.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
          </select>
          <small>{sceneDefinition.description}</small>
        </label>

        <label className="spatial-layer-control" htmlFor="spatial-observer-select">
          <span className="control-label">Observer</span>
          <select
            id="spatial-observer-select"
            value={observerId}
            onChange={(event) => setObserverId(event.target.value as SpatialObserverId)}
          >
            {SPATIAL_OBSERVERS.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
          </select>
          <small>{observerDefinition.description}</small>
        </label>
      </div>

      <div className="spatial-vision-section">
        <div className="control-label spatial-vision-label">Vision</div>
        <div className="spatial-mode-bar" role="group" aria-label="Vision">
          {SPATIAL_VISIONS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={vision === item.id ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"}
              aria-pressed={vision === item.id}
              onClick={() => setVision(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <p className="spatial-mode-description" aria-live="polite">{VISION_DESCRIPTIONS[vision]}</p>
      <div ref={hostRef} className="spatial-render-host" />
      <div className="spatial-caption">
        This Photo Reference supports look-around only. Drag or use arrow keys to look around; press R to reset. Changing Vision keeps the exact same Scene, Human observer, viewpoint, direction, and FOV.
      </div>
    </section>
  );
}

function disposeScene(scene: THREE.Scene | null, host: HTMLDivElement, renderer: THREE.WebGLRenderer | null) {
  if (scene) {
    if (scene.background instanceof THREE.Texture) scene.background.dispose();
    scene.traverse((object) => {
      const mesh = object as THREE.Mesh;
      mesh.geometry?.dispose?.();
      const material = mesh.material as THREE.Material | THREE.Material[] | undefined;
      if (Array.isArray(material)) material.forEach((item) => disposeMaterial(item));
      else if (material) disposeMaterial(material);
    });
  }

  if (!renderer) return;
  renderer.domElement.remove();
  renderer.dispose();
  renderer.forceContextLoss();

  while (host.firstChild) host.removeChild(host.firstChild);
}

function disposeMaterial(material: THREE.Material) {
  const withMap = material as THREE.Material & { map?: THREE.Texture };
  withMap.map?.dispose();
  material.dispose();
}
'''
spatial_page_path.write_text(spatial_page)

css_path = ROOT / 'src/spatial.css'
css = css_path.read_text()
if '.spatial-layer-grid {' not in css:
    insert = '''

.spatial-layer-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid #d8d1c5;
  background: #f3eee4;
}

.spatial-layer-control {
  display: grid;
  gap: 7px;
  min-width: 0;
}

.spatial-layer-control select {
  width: 100%;
  min-height: 44px;
  border: 1px solid #aaa294;
  border-radius: 8px;
  background: #fbf8f1;
  color: #35332f;
  padding: 0 38px 0 12px;
  font: inherit;
}

.spatial-layer-control select:focus-visible {
  outline: 3px solid #7f786b;
  outline-offset: 2px;
}

.spatial-layer-control small {
  color: #6a645a;
  line-height: 1.45;
}

.spatial-vision-section {
  background: #eee8dc;
  border-bottom: 1px solid #d8d1c5;
}

.spatial-vision-label {
  display: block;
  padding: 12px 16px 0;
}

.spatial-vision-section .spatial-mode-bar {
  border-bottom: 0;
  padding-top: 9px;
}
'''
    css += insert
    css = css.replace(
        '  .spatial-mode-bar {\n    padding: 10px 12px;\n  }',
        '  .spatial-layer-grid {\n    grid-template-columns: 1fr;\n    padding: 12px;\n  }\n\n  .spatial-mode-bar {\n    padding: 10px 12px;\n  }',
        1,
    )
css_path.write_text(css)

smoke_path = ROOT / '.github/production-smoke.mjs'
smoke = smoke_path.read_text()
helper_marker = 'async function desktopSpatialSmoke(browser) {'
if 'async function waitForExplore3DArchitecture' not in smoke:
    helper = '''async function waitForExplore3DArchitecture(page, label) {
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
    smoke = smoke.replace(helper_marker, helper + helper_marker, 1)

old_desktop_start = '''  await page.goto(`${BASE}/?view=spatial&production_smoke=${Date.now()}`, { waitUntil: "networkidle", timeout: 60_000 });
  await page.getByRole("heading", { name: "360° photographic night-city scene" }).waitFor({ timeout: 30_000 });'''
new_desktop_start = '''  await waitForExplore3DArchitecture(page, "desktop spatial");
  await page.getByRole("heading", { name: "360° Photo Reference" }).waitFor({ timeout: 30_000 });'''
if old_desktop_start not in smoke:
    raise SystemExit('desktop spatial start marker not found')
smoke = smoke.replace(old_desktop_start, new_desktop_start, 1)

old_group = '  const modeGroup = page.getByRole("group", { name: "Spatial perception mode" });'
new_group = '''  assert((await spatialNav.getByRole("link", { name: "Explore 3D", exact: true }).count()) === 1, "desktop spatial: Explore 3D navigation is missing or duplicated");
  const sceneSelect = page.locator("#spatial-scene-select");
  const observerSelect = page.locator("#spatial-observer-select");
  assert((await sceneSelect.inputValue()) === "photo-reference", "desktop spatial: Photo Reference scene is not active");
  assert((await observerSelect.inputValue()) === "human", "desktop spatial: Human observer is not active");
  assert(JSON.stringify(await sceneSelect.locator("option").allTextContents()) === JSON.stringify(["360° Photo Reference"]), "desktop spatial: unexpected Scene options");
  assert(JSON.stringify(await observerSelect.locator("option").allTextContents()) === JSON.stringify(["Human"]), "desktop spatial: unexpected Observer options");

  const modeGroup = page.getByRole("group", { name: "Vision" });'''
if old_group not in smoke:
    raise SystemExit('desktop mode group marker not found')
smoke = smoke.replace(old_group, new_group, 1)

camera_marker = '''  assert(!labels.some((label) => /Cat-like|Bird-like|Bee-like/i.test(label)), "desktop spatial: blocked/rejected animal control exposed");

  for (const label of expectedSpatialModes) {'''
camera_insert = '''  assert(!labels.some((label) => /Cat-like|Bird-like|Bee-like/i.test(label)), "desktop spatial: blocked/rejected animal control exposed");

  await canvas.focus();
  await page.keyboard.press("ArrowRight");
  await page.waitForTimeout(120);
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
  assert(afterVisionSwitch.vision === "tunnel", `desktop spatial: Vision runtime did not record tunnel (${JSON.stringify(afterVisionSwitch)})`);
  for (const key of ["scene", "observer", "yaw", "pitch", "fov", "position"]) {
    assert(afterVisionSwitch[key] === beforeVisionSwitch[key], `desktop spatial: Vision switch changed ${key}: ${beforeVisionSwitch[key]} -> ${afterVisionSwitch[key]}`);
  }

  for (const label of expectedSpatialModes) {'''
if camera_marker not in smoke:
    raise SystemExit('camera invariant insertion marker not found')
smoke = smoke.replace(camera_marker, camera_insert, 1)

old_mobile_group = '  const group = page.getByRole("group", { name: "Spatial perception mode" });'
new_mobile_group = '''  assert((await spatialNav.getByRole("link", { name: "Explore 3D", exact: true }).count()) === 1, "mobile spatial: Explore 3D navigation is missing or duplicated");
  assert((await page.locator("#spatial-scene-select").inputValue()) === "photo-reference", "mobile spatial: Photo Reference Scene is not active");
  assert((await page.locator("#spatial-observer-select").inputValue()) === "human", "mobile spatial: Human Observer is not active");
  await assertTouchTargets(page.locator(".spatial-layer-control select"), "mobile spatial Scene/Observer controls");
  const group = page.getByRole("group", { name: "Vision" });'''
if old_mobile_group not in smoke:
    raise SystemExit('mobile group marker not found')
smoke = smoke.replace(old_mobile_group, new_mobile_group, 1)
smoke_path.write_text(smoke)

methodology_path = ROOT / 'docs/methodology.md'
methodology = methodology_path.read_text()
old_method = '''## Spatial implementation approach
- Three.js runs browser-side;
- the accepted fixed-viewpoint 360° photographic night-city reference is reused while post-pilot modes are evaluated;
- scene-aware / view-relative post-processing is used where required by the mode;
- no accounts or server-side user data requirement;
- no game mechanics required;
- the current 2D transform engine remains in place;
- new spatial modes are added one at a time and require their own rendered acceptance gate.'''
new_method = '''## Explore 3D implementation approach
- Three.js runs browser-side and remains separate from the Canvas 2D image transform engine;
- the runtime is organized into explicit **Scene / Observer / Vision** layers;
- the current public Scene is the Hansaplatz `360° Photo Reference`, retained as a fixed-position photographic reference rather than the capability ceiling of Explore 3D;
- the current Photo Reference Observer is Human and look-only because the panorama contains no geometry for translation/parallax; this does not claim that bounded Human movement is already implemented;
- Vision is independent from Observer state: changing Vision preserves Scene, Observer, camera position, direction and FOV;
- geometry scenes may introduce translation, depth, collision, authored lighting, observer height and reachable-space differences in their scheduled phases;
- Dog/Cat/Bird observer behavior is separate from species-specific Vision claims, and unsupported Cat/Bird spectral filters are not restored by the architecture split;
- no accounts or server-side user data are required;
- bounded movement may be added where specified, but combat, scoring, inventory, quests and unrelated game-loop mechanics remain outside scope;
- every material spatial behavior change requires build/browser regression and the scheduled rendered/production acceptance gate.'''
if old_method not in methodology:
    raise SystemExit('methodology spatial implementation marker not found')
methodology_path.write_text(methodology.replace(old_method, new_method, 1))

limitations_path = ROOT / 'docs/limitations.md'
limitations = limitations_path.read_text()
limit_marker = '''The term `approximation` refers to this claim boundary. It should not be interpreted as permission to substitute a decorative static filter where live spatial modeling is required by the specification.'''
limit_insert = '''The term `approximation` refers to this claim boundary. It should not be interpreted as permission to substitute a decorative static filter where live spatial modeling is required by the specification.

### Current Explore 3D architecture boundary
The Scene / Observer / Vision split does not by itself create geometry, depth, parallax, collision, observer-height differences, climbing, or flight. The current public `360° Photo Reference` remains a fixed-position photographic source, so its Human observer supports look-around only. Features that require translation or physical observer differences remain unavailable until the scheduled geometry/observer phases are implemented and production-verified.

Dog-like remains available on the Photo Reference as a **Vision proxy** while the current Observer remains Human. That visual switch must not be read as a Dog-height camera or canine movement model. Cat and Bird observers are likewise not claimed until their movement/viewpoint phases exist; Bird flight and Bird spectral/color Vision remain separate requirements.'''
if limit_marker not in limitations:
    raise SystemExit('limitations architecture marker not found')
limitations_path.write_text(limitations.replace(limit_marker, limit_insert, 1))

roadmap_path = ROOT / 'docs/roadmap.md'
roadmap = roadmap_path.read_text()
roadmap = roadmap.replace(
    '- a production-verified image/release-polish track through R14, with R15 Tunnel image aspect-ratio correction validated and awaiting its own closeout.',
    '- a production-verified image/release-polish track through R15;\n- an active Explore 3D E1 architecture split that separates Scene / Observer / Vision while retaining the 360° Photo Reference.',
    1,
)
old_priority = '''## Immediate priority order
1. close the already-validated R15 Tunnel image aspect-ratio fix without broadening its scope;
2. begin Explore 3D Step E1: split the current spatial architecture into Scene / Observer / Vision;
3. retain Hansaplatz as `360° Photo Reference`, not as the whole 3D product;
4. build the first geometry-based `Night Intersection` scene;
5. add bounded Human movement and integrate accepted Human spatial Vision modes;
6. add Dog observer, then refine Dog-like 3D detail behavior;
7. add Cat observer movement/viewpoint without automatically restoring Cat-like Vision;
8. select a concrete first Bird species and implement real flight/perch behavior;
9. evaluate that Bird species' visual model separately from its movement/viewpoint;
10. expand to additional dense scenes after the first architecture is stable.'''
new_priority = '''## Immediate priority order
1. complete and production-verify Explore 3D Step E1: explicit Scene / Observer / Vision architecture while retaining Hansaplatz as `360° Photo Reference`;
2. build the first geometry-based `Night Intersection` scene;
3. add bounded Human movement and integrate accepted Human spatial Vision modes;
4. add Dog observer, then refine Dog-like 3D detail behavior;
5. add Cat observer movement/viewpoint without automatically restoring Cat-like Vision;
6. select a concrete first Bird species and implement real flight/perch behavior;
7. evaluate that Bird species' visual model separately from its movement/viewpoint;
8. expand to additional dense scenes after the first architecture is stable.'''
if old_priority not in roadmap:
    raise SystemExit('roadmap priority marker not found')
roadmap_path.write_text(roadmap.replace(old_priority, new_priority, 1))

schedule_path = ROOT / 'docs/explore-3d-schedule.md'
schedule = schedule_path.read_text()
schedule = schedule.replace(
    '## Step E1 — Architecture split: Scene / Observer / Vision\nStatus: **ACTIVE**',
    '## Step E1 — Architecture split: Scene / Observer / Vision\nStatus: **VALIDATED locally / awaiting PR and production verification**',
    1,
)
e1_acceptance = '''Acceptance:
- `Compare image` unchanged;
- panorama still works as a reference scene;
- Vision changes preserve Scene/Observer/camera state;
- architecture can host geometry-based scenes and translating observers;
- desktop/mobile regression green;
- build and production verification green.'''
e1_record = '''Acceptance:
- `Compare image` unchanged;
- panorama still works as a reference scene;
- Vision changes preserve Scene/Observer/camera state;
- architecture can host geometry-based scenes and translating observers;
- desktop/mobile regression green;
- build and production verification green.

Implementation under validation:
- current available Scene is explicitly `360° Photo Reference` and is owned by a Scene runtime rather than `SpatialPage` directly;
- current available Observer is explicitly `Human`; its fixed-photo look controls are owned by an Observer runtime and do not claim ground translation;
- existing Normal / Tunnel Vision / Central Loss / Night / Dog-like / Cataract-like post-processing is owned by a Vision runtime;
- public UI exposes Scene / Observer / Vision as separate controls without exposing unfinished Dog/Cat/Bird observers;
- permanent browser regression asserts the E1 control structure and verifies that switching Vision preserves scene, observer, yaw, pitch, FOV and camera position;
- production smoke waits for the E1 spatial architecture before accepting a freshly deployed release.'''
if e1_acceptance not in schedule:
    raise SystemExit('E1 acceptance marker not found')
schedule_path.write_text(schedule.replace(e1_acceptance, e1_record, 1))
