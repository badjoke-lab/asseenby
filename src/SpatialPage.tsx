import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { ModeEvidencePanel } from "./components/ModeEvidencePanel";
import { MODES } from "./modes";
import { getSpatialModeEvidence } from "./spatialEvidence";

type SpatialMode = "normal" | "tunnel" | "cataract";

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

    void main() {
      vec2 px = 1.0 / max(resolution, vec2(1.0));
      vec3 soft = texture2D(tDiffuse, vUv).rgb * 0.30;
      soft += texture2D(tDiffuse, vUv + vec2(px.x, 0.0)).rgb * 0.11;
      soft += texture2D(tDiffuse, vUv - vec2(px.x, 0.0)).rgb * 0.11;
      soft += texture2D(tDiffuse, vUv + vec2(0.0, px.y)).rgb * 0.11;
      soft += texture2D(tDiffuse, vUv - vec2(0.0, px.y)).rgb * 0.11;
      soft += texture2D(tDiffuse, vUv + vec2(px.x, px.y)).rgb * 0.065;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x, px.y)).rgb * 0.065;
      soft += texture2D(tDiffuse, vUv + vec2(px.x, -px.y)).rgb * 0.065;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x, -px.y)).rgb * 0.065;

      float luma = dot(soft, vec3(0.2126, 0.7152, 0.0722));
      vec3 desaturated = mix(vec3(luma), soft, 0.78);
      vec3 lowerContrast = mix(vec3(0.40), desaturated, 0.72);
      vec3 warmed = lowerContrast * vec3(1.07, 1.015, 0.90);
      vec3 veiled = mix(warmed, vec3(0.64, 0.58, 0.45), 0.085);
      gl_FragColor = vec4(veiled, 1.0);
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
            <strong>Comparison rule:</strong> switching the perception mode does not move the camera or alter the street scene. Tunnel Vision is a generic field-loss model; Cataract-like is a generic scene-dependent glare and haze model, not an individual's measured visual reconstruction.
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
      renderer.toneMappingExposure = 1.05;
      renderer.shadowMap.enabled = false;
      renderer.domElement.className = "spatial-canvas";
      renderer.domElement.tabIndex = 0;
      renderer.domElement.setAttribute("role", "application");
      renderer.domElement.setAttribute("aria-label", "Controlled night street scene. Drag or use arrow keys to look around.");
      host.appendChild(renderer.domElement);

      createNightStreetScene(scene);

      composer = new EffectComposer(renderer);
      composer.addPass(new RenderPass(scene, camera));

      bloomPass = new UnrealBloomPass(new THREE.Vector2(1, 1), 1.3, 0.78, 0.62);
      bloomPass.enabled = false;
      composer.addPass(bloomPass);

      cataractPass = new ShaderPass(CATARACT_SHADER);
      cataractPass.enabled = false;
      composer.addPass(cataractPass);

      tunnelPass = new ShaderPass(TUNNEL_SHADER);
      tunnelPass.enabled = false;
      composer.addPass(tunnelPass);

      composer.addPass(new OutputPass());

      const renderScene = () => {
        composer?.render();
      };

      const applyMode = (nextMode: SpatialMode) => {
        if (bloomPass) bloomPass.enabled = nextMode === "cataract";
        if (cataractPass) cataractPass.enabled = nextMode === "cataract";
        if (tunnelPass) tunnelPass.enabled = nextMode === "tunnel";
        renderScene();
      };

      controllerRef.current = {
        setMode: applyMode,
        render: renderScene,
      };

      const resize = () => {
        if (!renderer || !composer || !tunnelPass || !cataractPass) return;
        const width = Math.max(1, host.clientWidth);
        const height = Math.max(300, Math.round(width * 0.58));
        renderer.setSize(width, height, false);
        composer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        (tunnelPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
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

function createNightStreetScene(scene: THREE.Scene) {
  scene.add(new THREE.HemisphereLight(0x66778a, 0x151515, 0.46));

  const moonLight = new THREE.DirectionalLight(0x9fb5d8, 0.72);
  moonLight.position.set(-5, 9, 4);
  scene.add(moonLight);

  const road = new THREE.Mesh(
    new THREE.PlaneGeometry(12, 46),
    new THREE.MeshStandardMaterial({ color: 0x202428, roughness: 0.93, metalness: 0.03 }),
  );
  road.rotation.x = -Math.PI / 2;
  road.position.set(0, 0, -12);
  scene.add(road);

  const sidewalkMaterial = new THREE.MeshStandardMaterial({ color: 0x4d4c49, roughness: 0.98 });
  addBox(scene, [-4.5, 0.09, -12], [3, 0.18, 46], sidewalkMaterial);
  addBox(scene, [4.5, 0.09, -12], [3, 0.18, 46], sidewalkMaterial);

  const laneMaterial = new THREE.MeshBasicMaterial({ color: 0xc9c3aa });
  for (let z = 2; z > -34; z -= 6) {
    addBox(scene, [0, 0.025, z], [0.12, 0.03, 2.1], laneMaterial);
  }

  const crosswalkMaterial = new THREE.MeshBasicMaterial({ color: 0xdedbd0 });
  for (let x = -2.5; x <= 2.5; x += 0.72) {
    addBox(scene, [x, 0.035, -2.2], [0.42, 0.04, 2.4], crosswalkMaterial);
  }

  const buildingMaterial = new THREE.MeshStandardMaterial({ color: 0x292d31, roughness: 0.9 });
  const darkBuildingMaterial = new THREE.MeshStandardMaterial({ color: 0x171a1d, roughness: 0.98 });
  addBox(scene, [-5.3, 3.1, -7], [4.2, 6.2, 9], buildingMaterial);
  addBox(scene, [5.4, 3.6, -10], [4.5, 7.2, 12], buildingMaterial);
  addBox(scene, [-5.4, 4.8, -20], [4.6, 9.6, 12], darkBuildingMaterial);
  addBox(scene, [5.7, 5.5, -25], [5.1, 11, 14], buildingMaterial);
  addBox(scene, [-1.5, 6, -38], [7, 12, 6], darkBuildingMaterial);
  addBox(scene, [4.4, 7, -41], [6.5, 14, 7], buildingMaterial);

  addStorefront(scene);
  addTrafficSignal(scene);
  addStreetlight(scene, -3.25, -1.2);
  addStreetlight(scene, 3.25, -15.8);
  addVehicle(scene);
  addPedestrian(scene);
  addRoadSign(scene);
  addDarkSideRegion(scene);
}

function addStorefront(scene: THREE.Scene) {
  const frame = new THREE.MeshStandardMaterial({ color: 0x3b3430, roughness: 0.85 });
  addBox(scene, [-4.04, 1.55, -3.8], [0.18, 2.8, 4.5], frame);

  const windowMaterial = new THREE.MeshStandardMaterial({
    color: 0x7f6d50,
    emissive: 0x8e6738,
    emissiveIntensity: 1.4,
    roughness: 0.45,
  });
  addBox(scene, [-3.92, 1.35, -3.7], [0.08, 1.75, 3.15], windowMaterial);

  const signTexture = createTextTexture("OPEN", "#1d1812", "#f1c979");
  const signMaterial = new THREE.MeshBasicMaterial({ map: signTexture, toneMapped: false });
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 0.72), signMaterial);
  sign.rotation.y = Math.PI / 2;
  sign.position.set(-3.8, 2.95, -3.7);
  scene.add(sign);

  const storeLight = new THREE.PointLight(0xffc06a, 12, 8, 2);
  storeLight.position.set(-2.9, 2.2, -3.4);
  scene.add(storeLight);
}

function addTrafficSignal(scene: THREE.Scene) {
  const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x34383b, roughness: 0.72, metalness: 0.36 });
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 4.2, 10), poleMaterial);
  pole.position.set(2.9, 2.1, -4.2);
  scene.add(pole);

  addBox(scene, [2.9, 3.65, -4.2], [0.55, 1.3, 0.48], new THREE.MeshStandardMaterial({ color: 0x17191a, roughness: 0.8 }));

  addSignalLens(scene, [2.9, 4.02, -3.94], 0xff241d, 4.5);
  addSignalLens(scene, [2.9, 3.64, -3.94], 0xd8a729, 0.32);
  addSignalLens(scene, [2.9, 3.27, -3.94], 0x45d76c, 2.2);
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
  const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x42464a, roughness: 0.6, metalness: 0.45 });
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.09, 4.5, 10), poleMaterial);
  pole.position.set(x, 2.25, z);
  scene.add(pole);

  const lamp = new THREE.Mesh(
    new THREE.SphereGeometry(0.16, 16, 12),
    new THREE.MeshStandardMaterial({
      color: 0xffe1a3,
      emissive: 0xffc66f,
      emissiveIntensity: 8,
      roughness: 0.25,
    }),
  );
  lamp.position.set(x, 4.42, z);
  scene.add(lamp);

  const light = new THREE.PointLight(0xffcf85, 24, 13, 2);
  light.position.copy(lamp.position);
  scene.add(light);
}

function addVehicle(scene: THREE.Scene) {
  const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x39495a, roughness: 0.42, metalness: 0.3 });
  addBox(scene, [1.25, 0.55, -8.2], [2.05, 0.72, 4.1], bodyMaterial);
  addBox(scene, [1.25, 1.12, -8.45], [1.7, 0.75, 2.05], new THREE.MeshStandardMaterial({ color: 0x20282f, roughness: 0.35, metalness: 0.18 }));

  const headlightMaterial = new THREE.MeshStandardMaterial({
    color: 0xfff4d7,
    emissive: 0xffe4a7,
    emissiveIntensity: 11,
    roughness: 0.18,
  });
  for (const x of [0.65, 1.85]) {
    addBox(scene, [x, 0.62, -6.12], [0.34, 0.2, 0.09], headlightMaterial);
    const light = new THREE.PointLight(0xffe2aa, 34, 15, 2);
    light.position.set(x, 0.65, -6.0);
    scene.add(light);
  }
}

function addPedestrian(scene: THREE.Scene) {
  const clothing = new THREE.MeshStandardMaterial({ color: 0xb7493f, roughness: 0.78 });
  const skin = new THREE.MeshStandardMaterial({ color: 0xb88e73, roughness: 0.82 });

  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.25, 0.72, 6, 12), clothing);
  torso.position.set(-1.75, 1.05, -4.7);
  scene.add(torso);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 12), skin);
  head.position.set(-1.75, 1.72, -4.7);
  scene.add(head);

  const legMaterial = new THREE.MeshStandardMaterial({ color: 0x25282c, roughness: 0.9 });
  addBox(scene, [-1.88, 0.38, -4.7], [0.16, 0.75, 0.18], legMaterial);
  addBox(scene, [-1.62, 0.38, -4.7], [0.16, 0.75, 0.18], legMaterial);
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
  const wall = new THREE.MeshStandardMaterial({ color: 0x0f1214, roughness: 1 });
  addBox(scene, [4.5, 1.6, -2.2], [2.7, 3.2, 3.2], wall);
  addBox(scene, [4.2, 0.7, -0.65], [2.1, 1.4, 0.12], new THREE.MeshStandardMaterial({ color: 0x181b1d, roughness: 1 }));
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
