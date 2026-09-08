import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { ModeEvidencePanel } from "./components/ModeEvidencePanel";
import { MODES, type ModeDef } from "./modes";
import { getSpatialModeEvidence } from "./spatialEvidence";
import {
  SPATIAL_OBSERVERS,
  SPATIAL_SCENES,
  SPATIAL_VISIONS,
  type SpatialGuidedViewpoint,
  type SpatialObserverId,
  type SpatialSceneId,
  type SpatialVisionMode,
  type SpatialViewpointState,
} from "./spatial/catalog";
import { createSpatialObserverRuntime, type SpatialMoveDirection, type SpatialObserverRuntime } from "./spatial/observerRuntime";
import { createSpatialSceneRuntime, type SpatialSceneRuntime } from "./spatial/sceneRuntime";
import { createSpatialVisionRuntime, type SpatialVisionRuntime } from "./spatial/visionRuntime";

type SpatialController = {
  setScene: (sceneId: SpatialSceneId) => void;
  setObserver: (observerId: SpatialObserverId) => void;
  setVision: (vision: SpatialVisionMode) => void;
  setViewpoint: (viewpoint: SpatialGuidedViewpoint) => void;
  setMovementInput: (direction: SpatialMoveDirection, active: boolean) => void;
  resetObserver: () => void;
  render: () => void;
};

const GEOMETRY_HUMAN_VISIONS = new Set<SpatialVisionMode>(["normal", "tunnel", "central_loss", "night", "cataract"]);

const SPATIAL_EVIDENCE_MODE_DEFS: Partial<Record<SpatialVisionMode, ModeDef>> = {
  night: {
    key: "night",
    label: "Night / Low Light",
    category: "Human",
    confidence: "Estimated",
    note: "Luminance-dependent low-light spatial comparison proxy.",
  },
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
  const evidenceMode = evidenceModeKey
    ? MODES.find((item) => item.key === evidenceModeKey) ?? SPATIAL_EVIDENCE_MODE_DEFS[evidenceModeKey] ?? null
    : null;
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
                <strong>Human geometry comparison:</strong> the 1.6 m Human observer keeps the same bounded ground position, look direction, and FOV while Vision switches among Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like. The modes remain generic research simulations rather than patient-specific reconstructions.
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
  const [viewpoint, setViewpoint] = useState<SpatialViewpointState>("baseline");

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
    if (viewpoint !== "free") controllerRef.current?.setViewpoint(viewpoint);
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
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.25));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.3;
      renderer.shadowMap.enabled = false;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.domElement.className = "spatial-canvas";
      renderer.domElement.tabIndex = 0;
      renderer.domElement.setAttribute("role", "application");
      host.appendChild(renderer.domElement);

      composer = new EffectComposer(renderer);
      composer.addPass(new RenderPass(scene, camera));
      const canvas = renderer.domElement;
      const syncStreamingDiagnostics = () => {
        const diagnostics = activeSceneRuntime?.getStreamingDiagnostics();
        canvas.dataset.sceneLoadedChunks = diagnostics?.loadedChunkIds.join(",") ?? "";
        canvas.dataset.sceneAuthoredAssetRootCount = String(diagnostics?.authoredAssetRootCount ?? 0);
      };
      const renderScene = () => {
        composer?.render();
        syncStreamingDiagnostics();
      };
      visionRuntime = createSpatialVisionRuntime(composer, canvas, renderScene);

      const applyScene = (nextSceneId: SpatialSceneId) => {
        if (!scene || activeSceneRuntime?.id === nextSceneId) return;
        activeSceneRuntime?.dispose();
        activeSceneRuntime = createSpatialSceneRuntime(nextSceneId, scene, renderScene);
        activeObserverRuntime?.setNavigation(activeSceneRuntime.navigation);
        canvas.dataset.sceneId = nextSceneId;
        canvas.dataset.sceneSupportsTranslation = String(activeSceneRuntime.supportsTranslation);
        canvas.dataset.sceneObjectCount = String(activeSceneRuntime.objectCount);
        canvas.dataset.sceneLightCount = String(activeSceneRuntime.lightCount);
        canvas.dataset.sceneVolume = nextSceneId === "night-intersection" ? "500x500x80-streamed-envelope" : "photographic-reference";
        renderScene();
      };

      const applyObserver = (nextObserverId: SpatialObserverId) => {
        if (activeObserverRuntime?.id === nextObserverId) return;
        activeObserverRuntime?.dispose();
        activeObserverRuntime = createSpatialObserverRuntime(nextObserverId, {
          camera,
          canvas,
          renderScene,
          navigation: activeSceneRuntime?.navigation ?? null,
          onViewpointChange: setViewpoint,
          onPositionChange: (position) => activeSceneRuntime?.updateObserverPosition(position),
        });
        activeObserverRuntime.setGuidedViewpoint(viewpoint === "free" ? "baseline" : viewpoint);
        renderScene();
      };

      controllerRef.current = {
        setScene: applyScene,
        setObserver: applyObserver,
        setVision: (nextVision) => visionRuntime?.setVision(nextVision),
        setViewpoint: (nextViewpoint) => activeObserverRuntime?.setGuidedViewpoint(nextViewpoint),
        setMovementInput: (direction, active) => activeObserverRuntime?.setMovementInput(direction, active),
        resetObserver: () => activeObserverRuntime?.reset(),
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
  const isGeometryScene = sceneId === "night-intersection";
  const visibleVisions = isGeometryScene ? SPATIAL_VISIONS.filter((item) => GEOMETRY_HUMAN_VISIONS.has(item.id)) : SPATIAL_VISIONS;

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
              if (nextSceneId === "night-intersection" && vision === "dog") setVision("normal");
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
          <p className="spatial-mode-availability">Human geometry Vision uses the same live rendered scene and preserves the current observer/camera state. Dog-like remains a separate Photo Reference Vision proxy until the Dog observer phases.</p>
        ) : null}
      </div>

      <p className="spatial-mode-description" aria-live="polite">{VISION_DESCRIPTIONS[vision]}</p>
      <div ref={hostRef} className="spatial-render-host" />

      {isGeometryScene ? (
        <div className="spatial-movement-section" aria-label="Human movement controls">
          <div className="spatial-movement-copy">
            <span className="control-label">Move</span>
            <small>Desktop: W/A/S/D to walk, Shift for faster movement, drag or arrow keys to look, R to reset. Movement stays inside the authored walking area and avoids major obstacles.</small>
          </div>
          <div className="spatial-movement-actions">
            <div className="spatial-move-pad" role="group" aria-label="Mobile movement">
              {([
                ["forward", "↑", "Move forward"],
                ["left", "←", "Move left"],
                ["back", "↓", "Move back"],
                ["right", "→", "Move right"],
              ] as Array<[SpatialMoveDirection, string, string]>).map(([direction, symbol, label]) => (
                <button
                  key={direction}
                  type="button"
                  className={`spatial-move-button spatial-move-button--${direction}`}
                  aria-label={label}
                  onPointerDown={(event) => {
                    event.currentTarget.setPointerCapture(event.pointerId);
                    controllerRef.current?.setMovementInput(direction, true);
                  }}
                  onPointerUp={() => controllerRef.current?.setMovementInput(direction, false)}
                  onPointerCancel={() => controllerRef.current?.setMovementInput(direction, false)}
                  onLostPointerCapture={() => controllerRef.current?.setMovementInput(direction, false)}
                >
                  {symbol}
                </button>
              ))}
            </div>
            <button
              type="button"
              className="spatial-reset-button"
              onClick={() => controllerRef.current?.resetObserver()}
            >
              Reset observer
            </button>
          </div>
        </div>
      ) : null}

      {isGeometryScene ? (
        <div className="spatial-viewpoint-section" aria-label="Authored comparison viewpoints">
          <div>
            <span className="control-label">Comparison viewpoint</span>
            <small>These guided positions remain available alongside free movement. Selecting one changes position while preserving the current look direction and FOV.</small>
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
          ? "Night Intersection supports bounded Human ground movement plus same-state Human Vision switching. Walk with W/A/S/D on desktop or the compact mobile controls, use Shift for faster desktop movement, drag to look around, and use Reset observer or R to return to the canonical 1.6 m Human start without changing Vision."
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
