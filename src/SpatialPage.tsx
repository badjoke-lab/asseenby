import { useEffect, useRef, useState } from "react";
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
  type SpatialGuidedViewpoint,
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
  setViewpoint: (viewpoint: SpatialGuidedViewpoint) => void;
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
  const [sceneId, setSceneId] = useState<SpatialSceneId>("night-intersection");
  const [observerId, setObserverId] = useState<SpatialObserverId>("human");
  const [vision, setVision] = useState<SpatialVisionMode>("normal");
  const evidenceModeKey = vision === "normal" ? null : vision;
  const evidenceMode = evidenceModeKey ? MODES.find((item) => item.key === evidenceModeKey) ?? null : null;
  const isGeometryScene = sceneId === "night-intersection";

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
              Night Intersection is the first geometry-based Explore 3D scene, built to make depth, occlusion, authored lighting, and camera translation visible. Hansaplatz remains available as the 360° Photo Reference for photographic same-view Vision comparisons.
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
            {isGeometryScene ? (
              <>
                <strong>E2 geometry boundary:</strong> the two authored viewpoints change only camera position, making real parallax visible while direction and FOV stay unchanged. Bounded Human free movement and collision arrive in E3. Night Intersection intentionally exposes Normal only until the accepted Human Vision modes are integrated and reviewed for geometry in E4.
              </>
            ) : (
              <>
                <strong>Comparison rule:</strong> changing only Vision keeps the active Scene, Observer, camera position, look direction, and FOV unchanged. The Photo Reference has no translation depth, so its Human observer remains look-only. Dog-like here is a Vision proxy only; it does not claim a Dog-height observer.
              </>
            )}
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
              <p>
                {isGeometryScene
                  ? "No Vision simulation is applied. Use Normal to inspect the geometry, lighting hierarchy, depth, occlusion, near/mid/far targets, and viewpoint parallax before perception effects are introduced on this scene."
                  : "No Vision simulation is applied. Use this view as the reference before switching the Vision layer."}
              </p>
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
  const [viewpoint, setViewpoint] = useState<SpatialGuidedViewpoint>("baseline");

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
    controllerRef.current?.setViewpoint(viewpoint);
  }, [viewpoint]);

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

      const camera = new THREE.PerspectiveCamera(52, 1, 0.1, 280);
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
        canvas.dataset.sceneObjectCount = String(activeSceneRuntime.objectCount);
        canvas.dataset.sceneLightCount = String(activeSceneRuntime.lightCount);
        canvas.dataset.sceneVolume = nextSceneId === "night-intersection" ? "150x150x60" : "photographic-reference";
        renderScene();
      };

      const applyObserver = (nextObserverId: SpatialObserverId) => {
        if (activeObserverRuntime?.id === nextObserverId) return;
        activeObserverRuntime?.dispose();
        activeObserverRuntime = createSpatialObserverRuntime(nextObserverId, { camera, canvas, renderScene });
        activeObserverRuntime.setGuidedViewpoint(viewpoint);
        renderScene();
      };

      controllerRef.current = {
        setScene: applyScene,
        setObserver: applyObserver,
        setVision: (nextVision) => visionRuntime?.setVision(nextVision),
        setViewpoint: (nextViewpoint) => activeObserverRuntime?.setGuidedViewpoint(nextViewpoint),
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
      activeObserverRuntime?.setGuidedViewpoint(viewpoint);
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
  const isGeometryScene = sceneId === "night-intersection";
  const visibleVisions = isGeometryScene ? SPATIAL_VISIONS.filter((item) => item.id === "normal") : SPATIAL_VISIONS;

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
        <span className="spatial-status">{sceneDefinition.status}</span>
      </div>

      <div className="spatial-layer-grid" aria-label="Explore 3D configuration">
        <label className="spatial-layer-control" htmlFor="spatial-scene-select">
          <span className="control-label">Scene</span>
          <select
            id="spatial-scene-select"
            value={sceneId}
            onChange={(event) => {
              const nextSceneId = event.target.value as SpatialSceneId;
              setViewpoint("baseline");
              if (nextSceneId === "night-intersection") setVision("normal");
              setSceneId(nextSceneId);
            }}
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
          {visibleVisions.map((item) => (
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
        {isGeometryScene ? (
          <p className="spatial-mode-availability">Geometry Vision integration is intentionally deferred to E4. E2 is judged in Normal.</p>
        ) : null}
      </div>

      <p className="spatial-mode-description" aria-live="polite">{VISION_DESCRIPTIONS[vision]}</p>
      <div ref={hostRef} className="spatial-render-host" />

      {isGeometryScene ? (
        <div className="spatial-viewpoint-section" aria-label="Authored comparison viewpoints">
          <div>
            <span className="control-label">Comparison viewpoint</span>
            <small>Position changes; look direction and FOV stay fixed so nearby and distant geometry reveal parallax.</small>
          </div>
          <div className="spatial-viewpoint-buttons" role="group" aria-label="Comparison viewpoint">
            <button
              type="button"
              className={viewpoint === "baseline" ? "spatial-viewpoint-button spatial-viewpoint-button--active" : "spatial-viewpoint-button"}
              aria-pressed={viewpoint === "baseline"}
              onClick={() => setViewpoint("baseline")}
            >
              Reference
            </button>
            <button
              type="button"
              className={viewpoint === "offset" ? "spatial-viewpoint-button spatial-viewpoint-button--active" : "spatial-viewpoint-button"}
              aria-pressed={viewpoint === "offset"}
              onClick={() => setViewpoint("offset")}
            >
              Offset
            </button>
          </div>
        </div>
      ) : null}

      <div className="spatial-caption">
        {isGeometryScene
          ? "Night Intersection is a real geometry baseline. Switch Reference / Offset to compare parallax, drag or use arrow keys to look around, and press R to return to the canonical view. Bounded free ground movement is scheduled for E3."
          : "This Photo Reference supports look-around only. Drag or use arrow keys to look around; press R to reset. Changing Vision keeps the exact same Scene, Human observer, viewpoint, direction, and FOV."}
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
