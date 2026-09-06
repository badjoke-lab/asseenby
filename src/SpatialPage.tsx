import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { ModeEvidencePanel } from "./components/ModeEvidencePanel";
import { MODES } from "./modes";
import { getSpatialModeEvidence } from "./spatialEvidence";

type SpatialMode = "normal" | "tunnel" | "central_loss" | "cataract";

type SpatialController = {
  setMode: (mode: SpatialMode) => void;
  render: () => void;
};

const TUNNEL_SHADER = {
  uniforms: {
    tDiffuse: { value: null },
    resolution: { value: new THREE.Vector2(1, 1) },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform vec2 resolution;
    varying vec2 vUv;

    void main() {
      vec4 source = texture2D(tDiffuse, vUv);
      vec2 centered = vUv - 0.5;
      centered.x *= resolution.x / max(resolution.y, 1.0);
      float radius = length(centered);
      float visibility = 1.0 - smoothstep(0.22, 0.56, radius);
      float edgeDesaturation = smoothstep(0.13, 0.48, radius);
      float luma = dot(source.rgb, vec3(0.2126, 0.7152, 0.0722));
      vec3 muted = mix(source.rgb, vec3(luma), edgeDesaturation * 0.55);
      vec3 obscured = vec3(0.012, 0.014, 0.016);
      gl_FragColor = vec4(mix(obscured, muted, visibility), source.a);
    }
  `,
};

const CENTRAL_LOSS_SHADER = {
  uniforms: {
    tDiffuse: { value: null },
    resolution: { value: new THREE.Vector2(1, 1) },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform vec2 resolution;
    varying vec2 vUv;

    void main() {
      vec2 px = 1.0 / max(resolution, vec2(1.0));
      vec4 source = texture2D(tDiffuse, vUv);

      vec2 centered = vUv - 0.5;
      centered.x *= resolution.x / max(resolution.y, 1.0);
      float radius = length(centered);
      float angle = atan(centered.y, centered.x);
      float boundary = 0.165 + sin(angle * 3.0 + 0.35) * 0.012 + sin(angle * 5.0 - 0.7) * 0.008;
      float affected = 1.0 - smoothstep(boundary * 0.62, boundary * 1.28, radius);
      float core = 1.0 - smoothstep(boundary * 0.24, boundary * 0.72, radius);

      vec3 soft = source.rgb * 0.36;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 4.5, 0.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv - vec2(px.x * 4.5, 0.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(0.0, px.y * 4.5)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv - vec2(0.0, px.y * 4.5)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 7.0, px.y * 5.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x * 7.0, px.y * 5.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 7.0, -px.y * 5.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x * 7.0, -px.y * 5.0)).rgb * 0.08;

      float luma = dot(soft, vec3(0.2126, 0.7152, 0.0722));
      vec3 muted = mix(soft, vec3(luma), 0.58);
      vec3 lowContrast = mix(vec3(0.11, 0.105, 0.10), muted, 0.58);
      vec3 scotoma = mix(lowContrast, vec3(0.075, 0.073, 0.070), core * 0.76);
      vec3 result = mix(source.rgb, scotoma, affected * 0.94);

      gl_FragColor = vec4(result, source.a);
    }
  `,
};

const CATARACT_SHADER = {
  uniforms: {
    tDiffuse: { value: null },
    resolution: { value: new THREE.Vector2(1, 1) },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform vec2 resolution;
    varying vec2 vUv;

    vec3 brightSample(vec2 uv) {
      vec3 sampleColor = texture2D(tDiffuse, clamp(uv, vec2(0.001), vec2(0.999))).rgb;
      float luminance = dot(sampleColor, vec3(0.2126, 0.7152, 0.0722));
      float brightGate = smoothstep(0.58, 1.05, luminance);
      return sampleColor * brightGate;
    }

    void main() {
      vec2 px = 1.0 / max(resolution, vec2(1.0));
      vec3 source = texture2D(tDiffuse, vUv).rgb;

      vec3 soft = source * 0.56;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 1.5, 0.0)).rgb * 0.07;
      soft += texture2D(tDiffuse, vUv - vec2(px.x * 1.5, 0.0)).rgb * 0.07;
      soft += texture2D(tDiffuse, vUv + vec2(0.0, px.y * 1.5)).rgb * 0.07;
      soft += texture2D(tDiffuse, vUv - vec2(0.0, px.y * 1.5)).rgb * 0.07;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 1.5, px.y * 1.5)).rgb * 0.04;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x * 1.5, px.y * 1.5)).rgb * 0.04;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 1.5, -px.y * 1.5)).rgb * 0.04;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x * 1.5, -px.y * 1.5)).rgb * 0.04;

      vec3 glare = vec3(0.0);
      glare += brightSample(vUv + vec2(px.x * 4.0, 0.0));
      glare += brightSample(vUv - vec2(px.x * 4.0, 0.0));
      glare += brightSample(vUv + vec2(0.0, px.y * 4.0));
      glare += brightSample(vUv - vec2(0.0, px.y * 4.0));
      glare += brightSample(vUv + vec2(px.x * 8.0, px.y * 5.0));
      glare += brightSample(vUv + vec2(-px.x * 8.0, px.y * 5.0));
      glare += brightSample(vUv + vec2(px.x * 8.0, -px.y * 5.0));
      glare += brightSample(vUv + vec2(-px.x * 8.0, -px.y * 5.0));
      glare += brightSample(vUv + vec2(px.x * 15.0, 0.0)) * 0.7;
      glare += brightSample(vUv - vec2(px.x * 15.0, 0.0)) * 0.7;
      glare += brightSample(vUv + vec2(0.0, px.y * 15.0)) * 0.7;
      glare += brightSample(vUv - vec2(0.0, px.y * 15.0)) * 0.7;
      glare *= 0.085;

      float luma = dot(soft, vec3(0.2126, 0.7152, 0.0722));
      vec3 desaturated = mix(vec3(luma), soft, 0.82);
      vec3 lowerContrast = mix(vec3(0.075, 0.072, 0.065), desaturated, 0.84);
      vec3 warmed = lowerContrast * vec3(1.055, 1.015, 0.92);
      vec3 veiled = mix(warmed, vec3(0.34, 0.29, 0.20), 0.035);
      vec3 result = min(veiled + glare * vec3(1.08, 1.02, 0.88), vec3(1.35));
      gl_FragColor = vec4(result, 1.0);
    }
  `,
};

export default function SpatialPage() {
  const [mode, setMode] = useState<SpatialMode>("normal");
  const evidenceModeKey = mode === "normal" ? null : mode;
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
          <a href="/" className="ghost-button">Back to image</a>
        </header>

        <main className="content-area spatial-content">
          <section className="spatial-intro">
            <p className="spatial-kicker">Experimental spatial comparison</p>
            <h1 className="spatial-title">Explore the same scene through different ways of seeing.</h1>
            <p className="spatial-lead">
              A controlled night-street scene provides bright lights, dark regions, near and far targets, signage, people, vehicles, and road markings for the spatial comparison pilot.
            </p>
          </section>

          <SpatialRenderer mode={mode} setMode={setMode} />

          <section className="spatial-note" aria-label="Spatial pilot limitation">
            <strong>Comparison rule:</strong> switching the perception mode does not move the camera or alter the street scene. Tunnel Vision and Central Loss are generic field-loss models; Cataract-like is a generic scene-dependent glare and haze model. None are an individual's measured visual reconstruction.
          </section>

          {evidenceModeKey && evidenceMode ? (
            <section className="spatial-evidence" aria-label="Spatial mode evidence">
              <div className="spatial-evidence__intro">
                <div className="control-label">Spatial implementation evidence</div>
                <p>
                  The phenomenon evidence is shared with the corresponding AsSeenBy mode, while the Model score and implementation note below refer specifically to this experimental 3D renderer.
                </p>
              </div>
              <ModeEvidencePanel mode={evidenceMode} evidence={getSpatialModeEvidence(evidenceModeKey)} />
            </section>
          ) : (
            <section className="spatial-baseline-note" aria-label="Normal mode information">
              <div className="control-label">Normal baseline</div>
              <p>No perception simulation is applied. Use this view as the reference before switching to a spatial mode.</p>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}

function SpatialRenderer({ mode, setMode }: { mode: SpatialMode; setMode: (mode: SpatialMode) => void }) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const controllerRef = useRef<SpatialController | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    controllerRef.current?.setMode(mode);
  }, [mode]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    let renderer: THREE.WebGLRenderer | null = null;
    let composer: EffectComposer | null = null;
    let tunnelPass: ShaderPass | null = null;
    let centralLossPass: ShaderPass | null = null;
    let cataractPass: ShaderPass | null = null;
    let bloomPass: UnrealBloomPass | null = null;
    let resizeObserver: ResizeObserver | null = null;

    try {
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0b0f14);
      scene.fog = new THREE.Fog(0x0b0f14, 22, 58);

      const camera = new THREE.PerspectiveCamera(52, 1, 0.1, 100);
      camera.position.set(0, 1.65, 7.4);
      camera.rotation.order = "YXZ";

      let yaw = 0;
      let pitch = -0.01;
      let activePointer: number | null = null;
      let lastX = 0;
      let lastY = 0;

      const applyCameraRotation = () => {
        camera.rotation.y = yaw;
        camera.rotation.x = pitch;
      };
      applyCameraRotation();

      renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.08;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.domElement.className = "spatial-canvas";
      renderer.domElement.tabIndex = 0;
      renderer.domElement.setAttribute("role", "application");
      renderer.domElement.setAttribute("aria-label", "Controlled night street scene. Drag or use arrow keys to look around.");
      host.appendChild(renderer.domElement);

      createNightStreetScene(scene);
      scene.traverse((object) => {
        if (!(object instanceof THREE.Mesh)) return;
        const material = object.material as THREE.Material | THREE.Material[];
        const materials = Array.isArray(material) ? material : [material];
        const isUnlitPlane = materials.some((item) => item instanceof THREE.MeshBasicMaterial);
        object.castShadow = !isUnlitPlane;
        object.receiveShadow = !isUnlitPlane;
      });

      composer = new EffectComposer(renderer);
      composer.addPass(new RenderPass(scene, camera));

      bloomPass = new UnrealBloomPass(new THREE.Vector2(1, 1), 1.3, 0.78, 0.62);
      bloomPass.enabled = false;
      composer.addPass(bloomPass);

      cataractPass = new ShaderPass(CATARACT_SHADER);
      cataractPass.enabled = false;
      composer.addPass(cataractPass);

      centralLossPass = new ShaderPass(CENTRAL_LOSS_SHADER);
      centralLossPass.enabled = false;
      composer.addPass(centralLossPass);

      tunnelPass = new ShaderPass(TUNNEL_SHADER);
      tunnelPass.enabled = false;
      composer.addPass(tunnelPass);

      composer.addPass(new OutputPass());

      const renderScene = () => {
        composer?.render();
      };

      loadPresentationBuildings(scene, renderScene);

      const applyMode = (nextMode: SpatialMode) => {
        if (bloomPass) bloomPass.enabled = false;
        if (cataractPass) cataractPass.enabled = nextMode === "cataract";
        if (centralLossPass) centralLossPass.enabled = nextMode === "central_loss";
        if (tunnelPass) tunnelPass.enabled = nextMode === "tunnel";
        renderScene();
      };

      controllerRef.current = {
        setMode: applyMode,
        render: renderScene,
      };

      const resize = () => {
        if (!renderer || !composer || !tunnelPass || !centralLossPass || !cataractPass) return;
        const width = Math.max(1, host.clientWidth);
        const height = Math.max(300, Math.round(width * 0.58));
        renderer.setSize(width, height, false);
        composer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        (tunnelPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
        (centralLossPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
        (cataractPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
        renderScene();
      };

      const canvas = renderer.domElement;
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
        applyCameraRotation();
        renderScene();
      };

      const stopPointer = (event: PointerEvent) => {
        if (activePointer !== event.pointerId) return;
        if (canvas.hasPointerCapture(event.pointerId)) {
          canvas.releasePointerCapture(event.pointerId);
        }
        activePointer = null;
      };

      const onKeyDown = (event: KeyboardEvent) => {
        const step = event.shiftKey ? 0.14 : 0.07;
        if (event.key === "ArrowLeft") yaw += step;
        else if (event.key === "ArrowRight") yaw -= step;
        else if (event.key === "ArrowUp") pitch = THREE.MathUtils.clamp(pitch + step, -1.08, 1.08);
        else if (event.key === "ArrowDown") pitch = THREE.MathUtils.clamp(pitch - step, -1.08, 1.08);
        else return;
        event.preventDefault();
        applyCameraRotation();
        renderScene();
      };

      canvas.addEventListener("pointerdown", onPointerDown);
      canvas.addEventListener("pointermove", onPointerMove);
      canvas.addEventListener("pointerup", stopPointer);
      canvas.addEventListener("pointercancel", stopPointer);
      canvas.addEventListener("keydown", onKeyDown);

      resizeObserver = new ResizeObserver(resize);
      resizeObserver.observe(host);
      resize();
      applyMode(mode);

      return () => {
        controllerRef.current = null;
        canvas.removeEventListener("pointerdown", onPointerDown);
        canvas.removeEventListener("pointermove", onPointerMove);
        canvas.removeEventListener("pointerup", stopPointer);
        canvas.removeEventListener("pointercancel", stopPointer);
        canvas.removeEventListener("keydown", onKeyDown);
        resizeObserver?.disconnect();
        tunnelPass?.material.dispose();
        centralLossPass?.material.dispose();
        cataractPass?.material.dispose();
        bloomPass?.dispose();
        composer?.dispose();
        disposeScene(scene, host, renderer);
      };
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The 3D renderer could not start in this browser.");
    }

    return () => {
      controllerRef.current = null;
      resizeObserver?.disconnect();
      tunnelPass?.material.dispose();
        centralLossPass?.material.dispose();
      cataractPass?.material.dispose();
      bloomPass?.dispose();
      composer?.dispose();
      if (renderer) disposeScene(null, host, renderer);
    };
  }, []);

  const modeDescription = mode === "normal"
    ? "Baseline scene with no perception simulation."
    : mode === "tunnel"
      ? "Live screen-relative peripheral field loss. Look around to see how objects outside the center become harder to notice."
      : mode === "central_loss"
        ? "Live screen-relative central field loss. Center a pedestrian, sign, or light, then look elsewhere to see the disrupted region stay with straight-ahead vision."
        : "Scene-aware haze, softness, lower contrast, warming, and bright-source glare. Turn toward headlights or streetlights, then toward a dark area to compare.";

  if (error) {
    return (
      <section className="spatial-error" role="status">
        <h2>3D preview unavailable</h2>
        <p>{error}</p>
        <p><a href="/">Continue with Compare image</a>.</p>
      </section>
    );
  }

  return (
    <section className="spatial-card" aria-label="Explore 3D pilot">
      <div className="spatial-card__header">
        <div>
          <div className="control-label">Explore 3D</div>
          <h2>Controlled night-street scene</h2>
        </div>
        <span className="spatial-status">Pilot</span>
      </div>

      <div className="spatial-mode-bar" role="group" aria-label="Spatial perception mode">
        <button type="button" className={mode === "normal" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "normal"} onClick={() => setMode("normal")}>Normal</button>
        <button type="button" className={mode === "tunnel" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "tunnel"} onClick={() => setMode("tunnel")}>Tunnel Vision</button>
        <button type="button" className={mode === "central_loss" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "central_loss"} onClick={() => setMode("central_loss")}>Central Loss</button>
        <button type="button" className={mode === "cataract" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "cataract"} onClick={() => setMode("cataract")}>Cataract-like</button>
      </div>

      <p className="spatial-mode-description" aria-live="polite">{modeDescription}</p>
      <div ref={hostRef} className="spatial-render-host" />
      <div className="spatial-caption">
        Drag on the scene to look around. Mode switching keeps the same camera position and direction. Arrow keys work when the scene has keyboard focus.
      </div>
    </section>
  );
}

function loadPresentationBuildings(scene: THREE.Scene, renderScene: () => void) {
  const loader = new GLTFLoader();

  const placements = [
    { url: "/assets/models/downtown-small.glb", position: [-5.35, 0, -14.5] as [number, number, number], height: 8.6, rotationY: Math.PI / 2 },
    { url: "/assets/models/downtown-medium.glb", position: [5.3, 0, -21.5] as [number, number, number], height: 11.8, rotationY: -Math.PI / 2 },
    { url: "/assets/models/downtown-large.glb", position: [-4.8, 0, -36.0] as [number, number, number], height: 15.2, rotationY: Math.PI / 2 },
  ];

  for (const placement of placements) {
    loader.load(
      placement.url,
      (gltf) => {
        const model = gltf.scene;
        const sourceBox = new THREE.Box3().setFromObject(model);
        const sourceSize = sourceBox.getSize(new THREE.Vector3());
        if (!Number.isFinite(sourceSize.y) || sourceSize.y <= 0) return;

        const scale = placement.height / sourceSize.y;
        const center = sourceBox.getCenter(new THREE.Vector3());
        model.scale.setScalar(scale);
        model.position.set(-center.x * scale, -sourceBox.min.y * scale, -center.z * scale);

        model.traverse((object) => {
          if (!(object instanceof THREE.Mesh)) return;
          object.castShadow = true;
          object.receiveShadow = true;
          const materials = Array.isArray(object.material) ? object.material : [object.material];
          for (const material of materials) {
            if (material instanceof THREE.MeshStandardMaterial) {
              material.roughness = Math.max(0.3, Math.min(0.9, material.roughness));
              material.needsUpdate = true;
            }
          }
        });

        const wrapper = new THREE.Group();
        wrapper.position.set(...placement.position);
        wrapper.rotation.y = placement.rotationY;
        wrapper.add(model);
        scene.add(wrapper);
        renderScene();
      },
      undefined,
      (error) => {
        console.warn(`Optional presentation asset failed to load: ${placement.url}`, error);
      },
    );
  }
}

function createNightStreetScene(scene: THREE.Scene) {
  scene.background = new THREE.Color(0x0a1420);
  scene.fog = new THREE.Fog(0x0a1420, 22, 76);

  scene.add(new THREE.HemisphereLight(0x8ba2bd, 0x171a1d, 0.7));
  scene.add(new THREE.AmbientLight(0x2c3948, 0.18));

  const moonLight = new THREE.DirectionalLight(0xb7cce7, 0.92);
  moonLight.position.set(-7, 11, 5);
  moonLight.castShadow = true;
  moonLight.shadow.mapSize.set(1024, 1024);
  moonLight.shadow.camera.near = 0.5;
  moonLight.shadow.camera.far = 60;
  moonLight.shadow.camera.left = -13;
  moonLight.shadow.camera.right = 13;
  moonLight.shadow.camera.top = 13;
  moonLight.shadow.camera.bottom = -13;
  moonLight.shadow.bias = -0.00035;
  scene.add(moonLight);

  const fillLight = new THREE.DirectionalLight(0x5a6e88, 0.2);
  fillLight.position.set(8, 5, -8);
  scene.add(fillLight);

  const road = new THREE.Mesh(
    new THREE.PlaneGeometry(12, 54),
    new THREE.MeshStandardMaterial({ color: 0x30343a, map: createAsphaltTexture(), roughness: 0.68, metalness: 0.12 }),
  );
  road.rotation.x = -Math.PI / 2;
  road.position.set(0, 0, -15);
  scene.add(road);

  const sidewalkMaterial = new THREE.MeshStandardMaterial({ color: 0x6a6862, map: createConcreteTexture(), roughness: 0.88 });
  addBox(scene, [-4.5, 0.09, -15], [3, 0.18, 54], sidewalkMaterial);
  addBox(scene, [4.5, 0.09, -15], [3, 0.18, 54], sidewalkMaterial);

  const curbMaterial = new THREE.MeshStandardMaterial({ color: 0x89847b, map: createConcreteTexture(), roughness: 0.86 });
  addBox(scene, [-3.02, 0.16, -15], [0.12, 0.32, 54], curbMaterial);
  addBox(scene, [3.02, 0.16, -15], [0.12, 0.32, 54], curbMaterial);

  const laneMaterial = new THREE.MeshStandardMaterial({ color: 0xc8c1a9, roughness: 0.8 });
  for (let z = 2; z > -42; z -= 6) {
    addBox(scene, [0, 0.026, z], [0.11, 0.035, 2.1], laneMaterial);
  }

  const crosswalkMaterial = new THREE.MeshStandardMaterial({ color: 0xe0ddd2, roughness: 0.82 });
  for (let x = -2.5; x <= 2.5; x += 0.72) {
    addBox(scene, [x, 0.038, -2.2], [0.42, 0.05, 2.4], crosswalkMaterial);
  }

  const buildingMaterial = new THREE.MeshStandardMaterial({ color: 0x4a4f54, map: createPlasterTexture(), roughness: 0.84 });
  const darkBuildingMaterial = new THREE.MeshStandardMaterial({ color: 0x30363b, map: createPlasterTexture(), roughness: 0.92 });
  const brickMaterial = new THREE.MeshStandardMaterial({ color: 0x55423a, map: createBrickTexture(), roughness: 0.9 });
  addBox(scene, [-5.3, 3.1, -7], [4.2, 6.2, 9], brickMaterial);
  addBox(scene, [5.4, 3.6, -10], [4.5, 7.2, 12], buildingMaterial);
  addBox(scene, [-5.4, 4.8, -20], [4.6, 9.6, 12], darkBuildingMaterial);
  addBox(scene, [5.7, 5.5, -25], [5.1, 11, 14], buildingMaterial);
  addBox(scene, [-1.5, 6, -40], [7, 12, 7], darkBuildingMaterial);
  addBox(scene, [4.4, 7, -43], [6.5, 14, 8], buildingMaterial);

  addNearCornerArchitecture(scene);
  addFacadeDetail(scene);
  addStorefront(scene);
  addTrafficSignal(scene);
  addStreetlight(scene, -3.25, -1.2);
  addStreetlight(scene, 3.25, -15.8);
  addVehicle(scene);
  addParkedVehicle(scene);
  addPedestrian(scene);
  addRoadSign(scene);
  addStreetSurfaceDetail(scene);
  addStreetFurniture(scene);
  addOverheadUtilities(scene);
  addDistantStreetLayer(scene);
  addDarkSideRegion(scene);
  addNightSky(scene);
}

function addNightSky(scene: THREE.Scene) {
  const geometry = new THREE.SphereGeometry(72, 32, 18);
  const material = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      topColor: { value: new THREE.Color(0x07111e) },
      horizonColor: { value: new THREE.Color(0x26394c) },
      glowColor: { value: new THREE.Color(0x6f5c4c) },
    },
    vertexShader: `
      varying vec3 vWorldPosition;
      void main() {
        vec4 worldPosition = modelMatrix * vec4(position, 1.0);
        vWorldPosition = worldPosition.xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 topColor;
      uniform vec3 horizonColor;
      uniform vec3 glowColor;
      varying vec3 vWorldPosition;
      void main() {
        float h = normalize(vWorldPosition).y;
        float horizon = 1.0 - smoothstep(-0.08, 0.46, h);
        vec3 color = mix(topColor, horizonColor, horizon * 0.72);
        color = mix(color, glowColor, pow(max(0.0, horizon), 3.0) * 0.08);
        gl_FragColor = vec4(color, 1.0);
      }
    `,
  });
  const sky = new THREE.Mesh(geometry, material);
  sky.position.set(0, 0, -12);
  sky.renderOrder = -10;
  scene.add(sky);
}

function addStorefront(scene: THREE.Scene) {
  const frame = new THREE.MeshStandardMaterial({ color: 0x403833, roughness: 0.82 });
  addBox(scene, [-4.02, 1.65, -3.8], [0.22, 3.1, 4.8], frame);

  const windowMaterial = new THREE.MeshStandardMaterial({
    color: 0x78684f,
    emissive: 0x9f713d,
    emissiveIntensity: 1.15,
    roughness: 0.36,
    metalness: 0.08,
  });
  addBox(scene, [-3.89, 1.32, -4.35], [0.08, 1.72, 1.55], windowMaterial);
  addBox(scene, [-3.89, 1.32, -2.72], [0.08, 1.72, 1.45], windowMaterial);

  const mullion = new THREE.MeshStandardMaterial({ color: 0x1f211f, roughness: 0.75, metalness: 0.22 });
  addBox(scene, [-3.82, 1.32, -3.55], [0.08, 1.9, 0.09], mullion);
  addBox(scene, [-3.82, 1.32, -4.35], [0.08, 0.08, 1.65], mullion);
  addBox(scene, [-3.82, 1.32, -2.72], [0.08, 0.08, 1.55], mullion);

  const door = new THREE.MeshStandardMaterial({ color: 0x20272b, roughness: 0.42, metalness: 0.18 });
  addBox(scene, [-3.86, 1.18, -1.55], [0.09, 2.1, 0.82], door);
  addBox(scene, [-3.79, 1.22, -1.55], [0.035, 1.55, 0.62], new THREE.MeshStandardMaterial({ color: 0x53626b, roughness: 0.22, metalness: 0.28 }));

  const awning = new THREE.MeshStandardMaterial({ color: 0x713d34, roughness: 0.8 });
  const canopy = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.12, 4.1), awning);
  canopy.position.set(-3.68, 2.75, -3.45);
  canopy.rotation.z = -0.14;
  scene.add(canopy);

  const signTexture = createTextTexture("LATE CAFE", "#231b17", "#f1c979");
  const signMaterial = new THREE.MeshBasicMaterial({ map: signTexture, toneMapped: false });
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 0.76), signMaterial);
  sign.rotation.y = Math.PI / 2;
  sign.position.set(-3.72, 3.25, -3.55);
  scene.add(sign);

  const openTexture = createTextTexture("OPEN", "#4a1d18", "#ffc993");
  const openSign = new THREE.Mesh(new THREE.PlaneGeometry(0.72, 0.32), new THREE.MeshBasicMaterial({ map: openTexture, toneMapped: false }));
  openSign.rotation.y = Math.PI / 2;
  openSign.position.set(-3.73, 1.45, -3.15);
  scene.add(openSign);

  const storeLight = new THREE.PointLight(0xffba68, 16, 9, 2);
  storeLight.position.set(-2.8, 2.35, -3.35);
  scene.add(storeLight);
}

function addTrafficSignal(scene: THREE.Scene) {
  const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x3c4248, roughness: 0.58, metalness: 0.46 });
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.11, 4.5, 12), poleMaterial);
  pole.position.set(2.9, 2.25, -4.2);
  scene.add(pole);

  addBox(scene, [2.9, 4.18, -4.2], [0.68, 1.5, 0.56], new THREE.MeshStandardMaterial({ color: 0x121619, roughness: 0.72, metalness: 0.18 }));
  addBox(scene, [2.9, 4.92, -4.2], [0.84, 0.12, 0.62], poleMaterial);
  addBox(scene, [2.9, 4.53, -3.84], [0.54, 0.09, 0.32], poleMaterial);
  addBox(scene, [2.9, 4.16, -3.84], [0.54, 0.09, 0.32], poleMaterial);
  addBox(scene, [2.9, 3.79, -3.84], [0.54, 0.09, 0.32], poleMaterial);

  addSignalLens(scene, [2.9, 4.55, -3.90], 0xff2c24, 4.8);
  addSignalLens(scene, [2.9, 4.18, -3.90], 0xd8aa2f, 0.32);
  addSignalLens(scene, [2.9, 3.81, -3.90], 0x4edb70, 2.3);
}

function addSignalLens(scene: THREE.Scene, position: [number, number, number], color: number, emissiveIntensity: number) {
  const lens = new THREE.Mesh(
    new THREE.SphereGeometry(0.13, 18, 12),
    new THREE.MeshStandardMaterial({
      color,
      emissive: color,
      emissiveIntensity,
      roughness: 0.38,
    }),
  );
  lens.position.set(...position);
  scene.add(lens);
}

function addStreetlight(scene: THREE.Scene, x: number, z: number) {
  const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x434a50, roughness: 0.52, metalness: 0.52 });
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.095, 4.7, 12), poleMaterial);
  pole.position.set(x, 2.35, z);
  scene.add(pole);

  addBox(scene, [x + 0.28, 4.57, z], [0.62, 0.075, 0.08], poleMaterial);
  const fixture = new THREE.Mesh(
    new THREE.CylinderGeometry(0.16, 0.23, 0.34, 12),
    new THREE.MeshStandardMaterial({ color: 0x30363b, roughness: 0.45, metalness: 0.5 }),
  );
  fixture.rotation.z = Math.PI / 2;
  fixture.position.set(x + 0.57, 4.5, z);
  scene.add(fixture);

  const lamp = new THREE.Mesh(
    new THREE.SphereGeometry(0.13, 16, 12),
    new THREE.MeshStandardMaterial({
      color: 0xffe0a1,
      emissive: 0xffc66f,
      emissiveIntensity: 8,
      roughness: 0.2,
    }),
  );
  lamp.scale.set(1.4, 0.55, 1.0);
  lamp.position.set(x + 0.62, 4.42, z);
  scene.add(lamp);

  const light = new THREE.PointLight(0xffcf85, 26, 14, 2);
  light.position.copy(lamp.position);
  scene.add(light);
}

function addVehicle(scene: THREE.Scene) {
  const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x405467, roughness: 0.28, metalness: 0.5 });
  const trimMaterial = new THREE.MeshStandardMaterial({ color: 0x161b1f, roughness: 0.42, metalness: 0.4 });
  const glassMaterial = new THREE.MeshStandardMaterial({ color: 0x526b7a, roughness: 0.1, metalness: 0.38 });
  const chrome = new THREE.MeshStandardMaterial({ color: 0x9aa1a5, roughness: 0.24, metalness: 0.75 });

  addRoundedBox(scene, [1.25, 0.54, -8.2], [2.18, 0.66, 4.16], 0.12, bodyMaterial);
  const hood = addRoundedBox(scene, [1.25, 0.83, -7.12], [2.02, 0.28, 1.18], 0.1, bodyMaterial);
  hood.rotation.x = -0.035;
  const cabin = addRoundedBox(scene, [1.25, 1.12, -8.58], [1.72, 0.78, 1.98], 0.16, bodyMaterial);
  cabin.scale.x = 0.96;
  addBox(scene, [1.25, 1.29, -7.61], [1.48, 0.43, 0.055], glassMaterial);
  addBox(scene, [1.25, 1.3, -9.55], [1.46, 0.42, 0.055], glassMaterial);
  addBox(scene, [0.36, 0.55, -8.15], [0.07, 0.28, 3.2], trimMaterial);
  addBox(scene, [2.14, 0.55, -8.15], [0.07, 0.28, 3.2], trimMaterial);
  addRoundedBox(scene, [1.25, 0.35, -6.07], [1.98, 0.17, 0.2], 0.05, trimMaterial);
  addBox(scene, [1.25, 0.56, -6.035], [0.75, 0.06, 0.045], chrome);

  const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x0f1113, roughness: 0.82 });
  const rimMaterial = new THREE.MeshStandardMaterial({ color: 0x8a9195, roughness: 0.3, metalness: 0.72 });
  for (const x of [0.18, 2.32]) {
    for (const z of [-7.16, -9.32]) {
      const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.31, 0.31, 0.17, 24), wheelMaterial);
      wheel.rotation.z = Math.PI / 2;
      wheel.position.set(x, 0.31, z);
      scene.add(wheel);
      const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.18, 20), rimMaterial);
      rim.rotation.z = Math.PI / 2;
      rim.position.set(x, 0.31, z);
      scene.add(rim);
    }
  }

  const headlightMaterial = new THREE.MeshStandardMaterial({
    color: 0xfff4d7,
    emissive: 0xffe4a7,
    emissiveIntensity: 11,
    roughness: 0.1,
  });
  for (const x of [0.65, 1.85]) {
    addRoundedBox(scene, [x, 0.62, -6.105], [0.38, 0.19, 0.08], 0.035, headlightMaterial);
    const light = new THREE.SpotLight(0xffe2aa, 45, 18, Math.PI / 7, 0.45, 1.3);
    light.position.set(x, 0.68, -6.0);
    light.target.position.set(x, 0.1, 3.5);
    scene.add(light, light.target);
  }

  const tailMaterial = new THREE.MeshStandardMaterial({ color: 0x601c1a, emissive: 0xc52d27, emissiveIntensity: 0.55, roughness: 0.22 });
  for (const x of [0.55, 1.95]) {
    addRoundedBox(scene, [x, 0.59, -10.29], [0.38, 0.15, 0.07], 0.03, tailMaterial);
  }
}

function addParkedVehicle(scene: THREE.Scene) {
  const body = new THREE.MeshStandardMaterial({ color: 0x4b403d, roughness: 0.45, metalness: 0.28 });
  const glass = new THREE.MeshStandardMaterial({ color: 0x27343d, roughness: 0.2, metalness: 0.25 });
  addBox(scene, [-4.1, 0.43, -12.8], [1.65, 0.55, 3.35], body);
  addBox(scene, [-4.1, 0.88, -13.1], [1.35, 0.6, 1.65], body);
  addBox(scene, [-4.1, 1.0, -12.28], [1.15, 0.35, 0.05], glass);
  const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x111315, roughness: 0.9 });
  for (const x of [-4.88, -3.32]) {
    for (const z of [-11.9, -13.75]) {
      const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.13, 16), wheelMaterial);
      wheel.rotation.z = Math.PI / 2;
      wheel.position.set(x, 0.27, z);
      scene.add(wheel);
    }
  }
}

function addPedestrian(scene: THREE.Scene) {
  const coat = new THREE.MeshStandardMaterial({ color: 0xa9473f, roughness: 0.64 });
  const skin = new THREE.MeshStandardMaterial({ color: 0xb99179, roughness: 0.72 });
  const trouser = new THREE.MeshStandardMaterial({ color: 0x24292d, roughness: 0.82 });
  const shoe = new THREE.MeshStandardMaterial({ color: 0x111417, roughness: 0.88 });

  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.25, 0.68, 10, 18), coat);
  torso.position.set(-1.75, 1.08, -4.7);
  scene.add(torso);

  const shoulder = new THREE.Mesh(new THREE.CapsuleGeometry(0.13, 0.42, 8, 14), coat);
  shoulder.rotation.z = Math.PI / 2;
  shoulder.position.set(-1.75, 1.4, -4.7);
  scene.add(shoulder);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.19, 22, 16), skin);
  head.position.set(-1.75, 1.78, -4.7);
  scene.add(head);

  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.197, 20, 12, 0, Math.PI * 2, 0, Math.PI * 0.52), new THREE.MeshStandardMaterial({ color: 0x2a211f, roughness: 0.84 }));
  hair.position.set(-1.75, 1.84, -4.7);
  scene.add(hair);

  const addLimb = (x: number, y: number, material: THREE.Material, length: number, radius: number, tilt: number) => {
    const limb = new THREE.Mesh(new THREE.CapsuleGeometry(radius, length, 8, 14), material);
    limb.position.set(x, y, -4.7);
    limb.rotation.z = tilt;
    scene.add(limb);
  };

  addLimb(-2.03, 1.04, coat, 0.43, 0.075, 0.08);
  addLimb(-1.47, 1.04, coat, 0.43, 0.075, -0.08);
  addLimb(-1.9, 0.43, trouser, 0.52, 0.09, 0.035);
  addLimb(-1.6, 0.43, trouser, 0.52, 0.09, -0.035);
  addRoundedBox(scene, [-1.93, 0.08, -4.55], [0.27, 0.12, 0.43], 0.04, shoe);
  addRoundedBox(scene, [-1.57, 0.08, -4.55], [0.27, 0.12, 0.43], 0.04, shoe);
}

function addRoadSign(scene: THREE.Scene) {
  const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x60656a, roughness: 0.6, metalness: 0.35 });
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.055, 2.6, 10), poleMaterial);
  pole.position.set(-2.95, 1.3, -8.5);
  scene.add(pole);

  const texture = createTextTexture("CROSSING", "#d7d6c8", "#242b31");
  const sign = new THREE.Mesh(
    new THREE.PlaneGeometry(1.5, 0.62),
    new THREE.MeshBasicMaterial({ map: texture, toneMapped: false }),
  );
  sign.position.set(-2.95, 2.42, -8.43);
  scene.add(sign);
}

function addDarkSideRegion(scene: THREE.Scene) {
  const wall = new THREE.MeshStandardMaterial({ color: 0x14191d, roughness: 0.98 });
  addBox(scene, [4.55, 1.6, -2.2], [2.7, 3.2, 3.2], wall);
  addBox(scene, [4.2, 0.7, -0.65], [2.1, 1.4, 0.12], new THREE.MeshStandardMaterial({ color: 0x20262a, roughness: 1 }));
  addBox(scene, [4.1, 1.62, -0.58], [1.3, 1.5, 0.05], new THREE.MeshStandardMaterial({ color: 0x27333a, roughness: 0.34, metalness: 0.2 }));
}

function addNearCornerArchitecture(scene: THREE.Scene) {
  const leftWall = new THREE.MeshStandardMaterial({ color: 0x5a4a43, map: createBrickTexture(), roughness: 0.88 });
  const rightWall = new THREE.MeshStandardMaterial({ color: 0x4b5157, map: createPlasterTexture(), roughness: 0.84 });
  addBox(scene, [-5.4, 3.6, 4.0], [4.4, 7.2, 6.8], leftWall);
  addBox(scene, [5.4, 3.2, 4.0], [4.4, 6.4, 6.8], rightWall);

  const frame = new THREE.MeshStandardMaterial({ color: 0x272c30, roughness: 0.55, metalness: 0.28 });
  const glassDark = new THREE.MeshStandardMaterial({ color: 0x31404a, roughness: 0.16, metalness: 0.25 });
  const glassWarm = new THREE.MeshStandardMaterial({ color: 0x755c42, emissive: 0xa66d34, emissiveIntensity: 0.74, roughness: 0.24, metalness: 0.1 });
  const glassCool = new THREE.MeshStandardMaterial({ color: 0x3d5263, emissive: 0x496f8e, emissiveIntensity: 0.32, roughness: 0.24 });

  const addInnerWindow = (x: number, y: number, z: number, side: "left" | "right", variant: number) => {
    const material = variant === 0 ? glassDark : variant === 1 ? glassWarm : glassCool;
    addBox(scene, [x, y, z], [0.06, 0.92, 1.05], material);
    const trimX = side === "left" ? x + 0.04 : x - 0.04;
    addBox(scene, [trimX, y, z], [0.08, 0.07, 1.16], frame);
    addBox(scene, [trimX, y, z], [0.08, 1.03, 0.07], frame);
  };

  for (const z of [1.35, 3.2, 5.15, 6.45]) {
    addInnerWindow(-3.16, 2.25, z, "left", Math.abs(Math.round(z * 10)) % 3);
    addInnerWindow(-3.16, 4.05, z, "left", Math.abs(Math.round(z * 7 + 2)) % 3);
  }

  for (const z of [1.2, 3.1, 5.2, 6.5]) {
    addInnerWindow(3.16, 3.85, z, "right", Math.abs(Math.round(z * 8 + 1)) % 3);
    addInnerWindow(3.16, 5.05, z, "right", Math.abs(Math.round(z * 6 + 2)) % 3);
  }

  // Right-side corner shop, visible immediately when the viewer turns right.
  addBox(scene, [3.13, 1.35, 4.8], [0.08, 2.45, 3.25], new THREE.MeshStandardMaterial({ color: 0x6b563e, emissive: 0x8a5e31, emissiveIntensity: 0.78, roughness: 0.28 }));
  for (const z of [3.75, 4.8, 5.85]) {
    addBox(scene, [3.08, 1.34, z], [0.08, 2.25, 0.08], frame);
  }
  addBox(scene, [3.04, 2.48, 4.8], [0.12, 0.1, 3.35], frame);
  addBox(scene, [2.84, 2.82, 4.8], [0.52, 0.12, 3.7], new THREE.MeshStandardMaterial({ color: 0x6d3e35, roughness: 0.76 }));

  const shopTexture = createTextTexture("NIGHT MARKET", "#241b17", "#f1ca81");
  const shopSign = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 0.62), new THREE.MeshBasicMaterial({ map: shopTexture, toneMapped: false }));
  shopSign.rotation.y = -Math.PI / 2;
  shopSign.position.set(3.02, 3.1, 4.8);
  scene.add(shopSign);

  const rightDoor = new THREE.Mesh(new THREE.BoxGeometry(0.07, 2.1, 0.9), glassDark);
  rightDoor.position.set(3.05, 1.2, 2.1);
  scene.add(rightDoor);
  addBox(scene, [3.0, 1.2, 2.1], [0.08, 2.18, 0.08], frame);

  const shopLight = new THREE.PointLight(0xffba69, 18, 8, 2);
  shopLight.position.set(2.55, 2.25, 4.8);
  scene.add(shopLight);

  // Left-side apartment entrance and canopy.
  addBox(scene, [-3.13, 1.28, 5.2], [0.08, 2.35, 1.35], glassDark);
  addBox(scene, [-2.9, 2.6, 5.2], [0.55, 0.12, 1.65], frame);
  const entryTexture = createTextTexture("12", "#232629", "#d8cda8");
  const entrySign = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.44), new THREE.MeshBasicMaterial({ map: entryTexture, toneMapped: false }));
  entrySign.rotation.y = Math.PI / 2;
  entrySign.position.set(-3.03, 2.15, 4.25);
  scene.add(entrySign);

  // Bench and compact scooter shape provide close-range depth cues.
  const wood = new THREE.MeshStandardMaterial({ color: 0x604a37, roughness: 0.82 });
  addBox(scene, [-3.8, 0.52, 2.55], [1.35, 0.12, 0.42], wood);
  addBox(scene, [-3.8, 0.9, 2.78], [1.35, 0.62, 0.1], wood);
  addBox(scene, [-4.3, 0.28, 2.55], [0.1, 0.52, 0.1], frame);
  addBox(scene, [-3.3, 0.28, 2.55], [0.1, 0.52, 0.1], frame);

  const scooterBody = new THREE.MeshStandardMaterial({ color: 0x526776, roughness: 0.38, metalness: 0.32 });
  addBox(scene, [3.8, 0.44, 1.45], [0.38, 0.32, 1.05], scooterBody);
  const wheelMat = new THREE.MeshStandardMaterial({ color: 0x111315, roughness: 0.88 });
  for (const z of [1.05, 1.85]) {
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.1, 16), wheelMat);
    wheel.rotation.z = Math.PI / 2;
    wheel.position.set(3.8, 0.22, z);
    scene.add(wheel);
  }
  const handle = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.95, 8), frame);
  handle.position.set(3.8, 0.9, 1.15);
  handle.rotation.x = -0.25;
  scene.add(handle);
}

function addFacadeDetail(scene: THREE.Scene) {
  const darkWindow = new THREE.MeshStandardMaterial({ color: 0x18222a, roughness: 0.3, metalness: 0.14 });
  const warmWindow = new THREE.MeshStandardMaterial({ color: 0x775a3b, emissive: 0xa96f37, emissiveIntensity: 0.72, roughness: 0.38 });
  const coolWindow = new THREE.MeshStandardMaterial({ color: 0x344452, emissive: 0x425f7b, emissiveIntensity: 0.28, roughness: 0.35 });
  const sill = new THREE.MeshStandardMaterial({ color: 0x4c4d4d, roughness: 0.82 });

  const addFacadeWindow = (x: number, y: number, z: number, side: "left" | "right", lit: number) => {
    const material = lit === 1 ? warmWindow : lit === 2 ? coolWindow : darkWindow;
    if (side === "left") {
      addBox(scene, [x, y, z], [0.055, 0.74, 0.82], material);
      addBox(scene, [x + 0.035, y - 0.42, z], [0.08, 0.08, 0.92], sill);
    } else {
      addBox(scene, [x, y, z], [0.055, 0.74, 0.82], material);
      addBox(scene, [x - 0.035, y - 0.42, z], [0.08, 0.08, 0.92], sill);
    }
  };

  const leftX = -3.18;
  for (let y = 2.3; y <= 5.0; y += 1.3) {
    for (const z of [-7.9, -10.0, -15.8, -18.0, -21.0]) {
      addFacadeWindow(leftX, y, z, "left", (Math.round(y * 10 + z) % 3 + 3) % 3);
    }
  }

  const rightX = 3.18;
  for (let y = 2.4; y <= 6.2; y += 1.35) {
    for (const z of [-8.2, -10.4, -13.5, -18.8, -22.0, -26.2]) {
      addFacadeWindow(rightX, y, z, "right", (Math.round(y * 8 - z) % 3 + 3) % 3);
    }
  }

  const entryMaterial = new THREE.MeshStandardMaterial({ color: 0x1d252a, roughness: 0.42, metalness: 0.25 });
  addBox(scene, [3.16, 1.15, -10.7], [0.08, 2.15, 1.2], entryMaterial);
  addBox(scene, [3.12, 2.4, -10.7], [0.09, 0.22, 1.42], sill);
  addBox(scene, [-3.16, 1.1, -17.0], [0.08, 2.05, 1.15], entryMaterial);

  const verticalTrim = new THREE.MeshStandardMaterial({ color: 0x454849, roughness: 0.86 });
  for (const z of [-7.2, -12.0, -17.0, -22.0]) {
    addBox(scene, [-3.13, 3.2, z], [0.09, 5.7, 0.12], verticalTrim);
  }
  for (const z of [-9.0, -15.0, -21.5, -27.0]) {
    addBox(scene, [3.13, 3.4, z], [0.09, 6.0, 0.12], verticalTrim);
  }
}

function addStreetSurfaceDetail(scene: THREE.Scene) {
  const patchMaterial = new THREE.MeshStandardMaterial({ color: 0x30353a, roughness: 0.62, metalness: 0.12 });
  const wetMaterial = new THREE.MeshStandardMaterial({ color: 0x1e2429, roughness: 0.32, metalness: 0.22 });
  const grateMaterial = new THREE.MeshStandardMaterial({ color: 0x26292b, roughness: 0.55, metalness: 0.58 });

  addBox(scene, [-1.3, 0.02, -5.1], [1.2, 0.015, 2.7], patchMaterial);
  addBox(scene, [1.75, 0.018, -12.6], [1.65, 0.012, 3.4], wetMaterial);
  addBox(scene, [-0.65, 0.018, -20.5], [2.05, 0.012, 4.2], wetMaterial);

  const manhole = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.025, 28), grateMaterial);
  manhole.position.set(-1.45, 0.02, -10.6);
  scene.add(manhole);

  for (const z of [-4.8, -14.6, -24.2]) {
    addBox(scene, [-2.72, 0.065, z], [0.42, 0.05, 0.78], grateMaterial);
  }

  const seam = new THREE.MeshStandardMaterial({ color: 0x45433f, roughness: 0.92 });
  for (let z = 4; z > -38; z -= 2.4) {
    addBox(scene, [-4.48, 0.19, z], [2.75, 0.012, 0.028], seam);
    addBox(scene, [4.48, 0.19, z], [2.75, 0.012, 0.028], seam);
  }
}

function addStreetFurniture(scene: THREE.Scene) {
  const metal = new THREE.MeshStandardMaterial({ color: 0x3c4348, roughness: 0.58, metalness: 0.52 });
  const darkMetal = new THREE.MeshStandardMaterial({ color: 0x252c31, roughness: 0.72, metalness: 0.34 });
  const red = new THREE.MeshStandardMaterial({ color: 0x7a342f, roughness: 0.7 });

  for (const [x, z] of [[-3.38, 1.2], [-3.38, -0.2], [3.36, -5.5], [3.36, -7.0]] as Array<[number, number]>) {
    const bollard = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.11, 0.72, 12), metal);
    bollard.position.set(x, 0.45, z);
    scene.add(bollard);
  }

  addBox(scene, [4.1, 0.55, -7.2], [0.62, 1.05, 0.62], darkMetal);
  addBox(scene, [4.1, 1.12, -7.2], [0.7, 0.12, 0.68], metal);

  const hydrantBody = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.22, 0.62, 14), red);
  hydrantBody.position.set(-3.72, 0.42, -6.2);
  scene.add(hydrantBody);
  const hydrantCap = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.2, 0.18, 14), red);
  hydrantCap.position.set(-3.72, 0.82, -6.2);
  scene.add(hydrantCap);

  const planter = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.5, 0.5, 16), new THREE.MeshStandardMaterial({ color: 0x4a4740, roughness: 0.96 }));
  planter.position.set(3.95, 0.34, -12.2);
  scene.add(planter);
  const leaves = new THREE.Mesh(new THREE.SphereGeometry(0.52, 14, 10), new THREE.MeshStandardMaterial({ color: 0x334637, roughness: 0.9 }));
  leaves.scale.set(0.78, 1.15, 0.78);
  leaves.position.set(3.95, 1.0, -12.2);
  scene.add(leaves);
}

function addOverheadUtilities(scene: THREE.Scene) {
  const wireMaterial = new THREE.LineBasicMaterial({ color: 0x20262b });
  const makeWire = (points: Array<[number, number, number]>) => {
    const geometry = new THREE.BufferGeometry().setFromPoints(points.map(([x, y, z]) => new THREE.Vector3(x, y, z)));
    scene.add(new THREE.Line(geometry, wireMaterial));
  };

  makeWire([[-3.5, 5.0, -3], [0, 4.7, -8], [3.5, 5.2, -13]]);
  makeWire([[-3.4, 5.45, -10], [0.2, 5.15, -17], [3.6, 5.6, -23]]);
  makeWire([[-3.6, 6.0, -20], [-0.4, 5.72, -27], [3.7, 6.1, -34]]);
}

function addDistantStreetLayer(scene: THREE.Scene) {
  const distant = new THREE.MeshStandardMaterial({ color: 0x252b30, roughness: 0.94 });
  addBox(scene, [-5.8, 5.5, -50], [5.2, 11, 10], distant);
  addBox(scene, [0.2, 7.2, -53], [6.2, 14.4, 8], new THREE.MeshStandardMaterial({ color: 0x20262b, roughness: 0.96 }));
  addBox(scene, [5.5, 6.1, -49], [4.8, 12.2, 10], distant);

  const windowMat = new THREE.MeshStandardMaterial({ color: 0x6a563d, emissive: 0x8a6236, emissiveIntensity: 0.4, roughness: 0.4 });
  for (const x of [-2.4, -0.8, 0.8, 2.4]) {
    for (const y of [2.8, 4.4, 6.0, 7.6]) {
      addBox(scene, [x, y, -48.8], [0.7, 0.58, 0.05], ((Math.round(x * 10 + y * 10) % 3) === 0) ? windowMat : new THREE.MeshStandardMaterial({ color: 0x172027, roughness: 0.4 }));
    }
  }

  const distantLamp = new THREE.PointLight(0xffc477, 9, 12, 2);
  distantLamp.position.set(0.5, 4.3, -34);
  scene.add(distantLamp);
  addBox(scene, [0.5, 4.2, -34], [0.24, 0.15, 0.16], new THREE.MeshStandardMaterial({ color: 0xffd28a, emissive: 0xffbd63, emissiveIntensity: 5 }));
}

function createAsphaltTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  if (!context) return null;
  context.fillStyle = "#34383c";
  context.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 650; i += 1) {
    const seed = Math.sin(i * 91.73) * 43758.5453;
    const seed2 = Math.sin(i * 43.17 + 2.1) * 24634.6345;
    const x = Math.abs(seed % 1) * 256;
    const y = Math.abs(seed2 % 1) * 256;
    const tone = 42 + (i % 5) * 4;
    context.fillStyle = `rgb(${tone}, ${tone + 2}, ${tone + 4})`;
    context.fillRect(x, y, 1 + (i % 2), 1 + ((i + 1) % 2));
  }
  context.strokeStyle = "rgba(18, 21, 24, 0.5)";
  context.lineWidth = 1;
  context.beginPath();
  context.moveTo(12, 190);
  context.bezierCurveTo(72, 155, 110, 205, 166, 171);
  context.bezierCurveTo(203, 150, 224, 166, 252, 138);
  context.stroke();
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(3.5, 14);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createConcreteTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  if (!context) return null;
  context.fillStyle = "#8c8982";
  context.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 300; i += 1) {
    const x = Math.abs(Math.sin(i * 18.2) * 9973) % 256;
    const y = Math.abs(Math.sin(i * 37.7 + 1.4) * 7919) % 256;
    context.fillStyle = i % 3 === 0 ? "rgba(70,68,65,0.18)" : "rgba(210,207,198,0.12)";
    context.fillRect(x, y, 1.2, 1.2);
  }
  context.strokeStyle = "rgba(66,64,61,0.28)";
  context.lineWidth = 2;
  context.strokeRect(2, 2, 252, 252);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1.6, 10);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createBrickTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  if (!context) return null;
  context.fillStyle = "#695148";
  context.fillRect(0, 0, 256, 256);
  context.strokeStyle = "rgba(211,190,174,0.24)";
  context.lineWidth = 2;
  const rowHeight = 28;
  for (let y = 0; y <= 256; y += rowHeight) {
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(256, y);
    context.stroke();
    const offset = (Math.floor(y / rowHeight) % 2) * 32;
    for (let x = -64 + offset; x < 320; x += 64) {
      context.beginPath();
      context.moveTo(x, y);
      context.lineTo(x, y + rowHeight);
      context.stroke();
    }
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1.4, 2.8);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createPlasterTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  if (!context) return null;
  context.fillStyle = "#72787c";
  context.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 420; i += 1) {
    const x = Math.abs(Math.sin(i * 13.11) * 3271) % 256;
    const y = Math.abs(Math.sin(i * 29.31 + 0.8) * 6143) % 256;
    context.fillStyle = i % 2 ? "rgba(32,37,41,0.08)" : "rgba(220,224,226,0.055)";
    context.fillRect(x, y, 2, 2);
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1.8, 2.6);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createTextTexture(text: string, background: string, foreground: string) {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 192;
  const context = canvas.getContext("2d");
  if (!context) return new THREE.CanvasTexture(canvas);

  context.fillStyle = background;
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = foreground;
  context.font = "700 76px Arial, sans-serif";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(text, canvas.width / 2, canvas.height / 2);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  return texture;
}

function addRoundedBox(
  scene: THREE.Scene,
  position: [number, number, number],
  size: [number, number, number],
  radius: number,
  material: THREE.Material,
) {
  const [width, height, depth] = size;
  const safeRadius = Math.min(radius, width * 0.24, height * 0.24, depth * 0.24);
  const mesh = new THREE.Mesh(new RoundedBoxGeometry(width, height, depth, 4, safeRadius), material);
  mesh.position.set(...position);
  scene.add(mesh);
  return mesh;
}

function addBox(
  scene: THREE.Scene,
  position: [number, number, number],
  size: [number, number, number],
  material: THREE.Material,
) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), material);
  mesh.position.set(...position);
  scene.add(mesh);
  return mesh;
}

function disposeScene(scene: THREE.Scene | null, host: HTMLDivElement, renderer: THREE.WebGLRenderer | null) {
  if (scene) {
    scene.traverse((object) => {
      const mesh = object as THREE.Mesh;
      mesh.geometry?.dispose?.();
      const material = mesh.material as THREE.Material | THREE.Material[] | undefined;
      if (Array.isArray(material)) {
        material.forEach((item) => disposeMaterial(item));
      } else if (material) {
        disposeMaterial(material);
      }
    });
  }

  if (!renderer) return;
  renderer.domElement.remove();
  renderer.dispose();
  renderer.forceContextLoss();

  while (host.firstChild) {
    host.removeChild(host.firstChild);
  }
}

function disposeMaterial(material: THREE.Material) {
  const withMap = material as THREE.Material & { map?: THREE.Texture };
  withMap.map?.dispose();
  material.dispose();
}
