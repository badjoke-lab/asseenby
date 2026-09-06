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

type SpatialMode = "normal" | "tunnel" | "central_loss" | "night" | "cataract";

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

const NIGHT_LOW_LIGHT_SHADER = {
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

    float lumaAt(vec2 uv) {
      vec3 color = texture2D(tDiffuse, clamp(uv, vec2(0.001), vec2(0.999))).rgb;
      return dot(color, vec3(0.2126, 0.7152, 0.0722));
    }

    void main() {
      vec2 px = 1.0 / max(resolution, vec2(1.0));
      vec3 source = texture2D(tDiffuse, vUv).rgb;
      float localLuma = dot(source, vec3(0.2126, 0.7152, 0.0722));

      float viewLuma = (
        lumaAt(vec2(0.50, 0.50)) +
        lumaAt(vec2(0.24, 0.28)) +
        lumaAt(vec2(0.76, 0.28)) +
        lumaAt(vec2(0.24, 0.72)) +
        lumaAt(vec2(0.76, 0.72))
      ) / 5.0;

      float dimView = 1.0 - smoothstep(0.16, 0.48, viewLuma);
      float localDark = 1.0 - smoothstep(0.08, 0.52, localLuma);
      float lowLightWeight = clamp(localDark * 0.72 + dimView * 0.46, 0.0, 1.0);

      float blurRadius = mix(0.7, 2.8, lowLightWeight);
      vec3 soft = source * 0.48;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * blurRadius, 0.0)).rgb * 0.13;
      soft += texture2D(tDiffuse, vUv - vec2(px.x * blurRadius, 0.0)).rgb * 0.13;
      soft += texture2D(tDiffuse, vUv + vec2(0.0, px.y * blurRadius)).rgb * 0.13;
      soft += texture2D(tDiffuse, vUv - vec2(0.0, px.y * blurRadius)).rgb * 0.13;

      float softLuma = dot(soft, vec3(0.2126, 0.7152, 0.0722));
      float desaturation = mix(0.18, 0.78, lowLightWeight);
      vec3 muted = mix(soft, vec3(softLuma), desaturation);

      float contrastScale = mix(0.94, 0.68, lowLightWeight);
      vec3 reducedContrast = vec3(0.065) + (muted - vec3(0.065)) * contrastScale;
      float shadowLoss = localDark * mix(0.08, 0.26, dimView);
      vec3 result = reducedContrast * (1.0 - shadowLoss);

      gl_FragColor = vec4(result, 1.0);
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
            <a href="/?view=spatial" aria-current="page">Explore spatial</a>
            <a href="/support/">Support</a>
          </nav>
          <a href="/" className="ghost-button">Back to image</a>
        </header>

        <main className="content-area spatial-content">
          <section className="spatial-intro">
            <p className="spatial-kicker">Experimental spatial comparison</p>
            <h1 className="spatial-title">Explore the same scene through different ways of seeing.</h1>
            <p className="spatial-lead">
              A real 360° night-city panorama provides dense architecture, shopfronts, streetlights, dark sky, near and far detail, and high-contrast targets for the spatial comparison pilot.
            </p>
          </section>

          <SpatialRenderer mode={mode} setMode={setMode} />

          <section className="spatial-note" aria-label="Spatial pilot limitation">
            <strong>Comparison rule:</strong> switching the perception mode does not move the camera or alter the 360° photographic reference scene. Tunnel Vision and Central Loss are generic field-loss models; Night / Low Light is a luminance-dependent low-light proxy; Cataract-like is a generic scene-dependent glare and haze model. None are an individual's measured visual reconstruction, and the low-light mode does not infer physical scene luminance from the tone-mapped panorama.
          </section>

          {evidenceModeKey && evidenceMode ? (
            <section className="spatial-evidence" aria-label="Spatial mode evidence">
              <div className="spatial-evidence__intro">
                <div className="control-label">Spatial implementation evidence</div>
                <p>
                  The phenomenon evidence is shared with the corresponding AsSeenBy mode, while the Model score and implementation note below refer specifically to this experimental spatial renderer.
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
    let nightPass: ShaderPass | null = null;
    let bloomPass: UnrealBloomPass | null = null;
    let resizeObserver: ResizeObserver | null = null;

    try {
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x05070a);
      scene.fog = null;

      const camera = new THREE.PerspectiveCamera(52, 1, 0.1, 100);
      camera.position.set(0, 0, 0);
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
      renderer.toneMapping = THREE.NoToneMapping;
      renderer.toneMappingExposure = 1.0;
      renderer.shadowMap.enabled = false;
      renderer.domElement.className = "spatial-canvas";
      renderer.domElement.tabIndex = 0;
      renderer.domElement.setAttribute("role", "application");
      renderer.domElement.setAttribute("aria-label", "360 degree photographic night-city reference scene. Drag or use arrow keys to look around.");
      host.appendChild(renderer.domElement);

      composer = new EffectComposer(renderer);
      composer.addPass(new RenderPass(scene, camera));

      bloomPass = new UnrealBloomPass(new THREE.Vector2(1, 1), 1.3, 0.78, 0.62);
      bloomPass.enabled = false;
      composer.addPass(bloomPass);

      cataractPass = new ShaderPass(CATARACT_SHADER);
      cataractPass.enabled = false;
      composer.addPass(cataractPass);

      nightPass = new ShaderPass(NIGHT_LOW_LIGHT_SHADER);
      nightPass.enabled = false;
      composer.addPass(nightPass);

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

      loadPanoramaEnvironment(scene, renderScene);

      const applyMode = (nextMode: SpatialMode) => {
        if (bloomPass) bloomPass.enabled = false;
        if (cataractPass) cataractPass.enabled = nextMode === "cataract";
        if (nightPass) nightPass.enabled = nextMode === "night";
        if (centralLossPass) centralLossPass.enabled = nextMode === "central_loss";
        if (tunnelPass) tunnelPass.enabled = nextMode === "tunnel";
        renderScene();
      };

      controllerRef.current = {
        setMode: applyMode,
        render: renderScene,
      };

      const resize = () => {
        if (!renderer || !composer || !tunnelPass || !centralLossPass || !nightPass || !cataractPass) return;
        const width = Math.max(1, host.clientWidth);
        const height = Math.max(300, Math.round(width * 0.58));
        renderer.setSize(width, height, false);
        composer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        (tunnelPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
        (centralLossPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
        (nightPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
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
        nightPass?.material.dispose();
        cataractPass?.material.dispose();
        bloomPass?.dispose();
        composer?.dispose();
        disposeScene(scene, host, renderer);
      };
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The spatial renderer could not start in this browser.");
    }

    return () => {
      controllerRef.current = null;
      resizeObserver?.disconnect();
      tunnelPass?.material.dispose();
      centralLossPass?.material.dispose();
      nightPass?.material.dispose();
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
        ? "Live screen-relative central field loss. Center a shop sign, window, lamp, or other detail, then look elsewhere to see the disrupted region stay with straight-ahead vision."
        : mode === "night"
          ? "Luminance-dependent low-light proxy. Darker scene regions lose more color, contrast, and fine detail while brighter shopfronts and lamps remain more available. It does not model calibrated scotopic luminance or dark-adaptation time."
          : "Scene-aware haze, softness, lower contrast, warming, and bright-source glare. Turn toward bright shopfronts or streetlights, then toward the dark sky to compare.";

  if (error) {
    return (
      <section className="spatial-error" role="status">
        <h2>Spatial preview unavailable</h2>
        <p>{error}</p>
        <p><a href="/">Continue with Compare image</a>.</p>
      </section>
    );
  }

  return (
    <section className="spatial-card" aria-label="Explore spatial pilot">
      <div className="spatial-card__header">
        <div>
          <div className="control-label">Explore spatial</div>
          <h2>360° photographic night-city scene</h2>
        </div>
        <span className="spatial-status">Pilot</span>
      </div>

      <div className="spatial-mode-bar" role="group" aria-label="Spatial perception mode">
        <button type="button" className={mode === "normal" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "normal"} onClick={() => setMode("normal")}>Normal</button>
        <button type="button" className={mode === "tunnel" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "tunnel"} onClick={() => setMode("tunnel")}>Tunnel Vision</button>
        <button type="button" className={mode === "central_loss" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "central_loss"} onClick={() => setMode("central_loss")}>Central Loss</button>
        <button type="button" className={mode === "night" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "night"} onClick={() => setMode("night")}>Night / Low Light</button>
        <button type="button" className={mode === "cataract" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "cataract"} onClick={() => setMode("cataract")}>Cataract-like</button>
      </div>

      <p className="spatial-mode-description" aria-live="polite">{modeDescription}</p>
      <div ref={hostRef} className="spatial-render-host" />
      <div className="spatial-caption">
        Drag to look around the full 360° reference scene. Mode switching keeps the exact same viewpoint and direction. Arrow keys work when the scene has keyboard focus.
      </div>
    </section>
  );
}

function loadPanoramaEnvironment(scene: THREE.Scene, renderScene: () => void) {
  const loader = new THREE.TextureLoader();
  loader.load(
    "/assets/panoramas/hansaplatz.jpg",
    (texture) => {
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.mapping = THREE.EquirectangularReflectionMapping;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.magFilter = THREE.LinearFilter;
      scene.background = texture;
      renderScene();
    },
    undefined,
    (error) => {
      console.error("360° reference panorama failed to load", error);
    },
  );
}

function disposeScene(scene: THREE.Scene | null, host: HTMLDivElement, renderer: THREE.WebGLRenderer | null) {
  if (scene) {
    if (scene.background instanceof THREE.Texture) scene.background.dispose();
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
