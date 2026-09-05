import { useEffect, useRef, useState } from "react";
import * as THREE from "three";

export default function SpatialPage() {
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

          <SpatialRenderer />

          <section className="spatial-note" aria-label="Spatial pilot limitation">
            <strong>Current step:</strong> controlled scene baseline. Perception modes will be added only after the scene and camera comparison rules are stable.
          </section>
        </main>
      </div>
    </div>
  );
}

function SpatialRenderer() {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    let renderer: THREE.WebGLRenderer | null = null;
    let resizeObserver: ResizeObserver | null = null;

    try {
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0b0f14);
      scene.fog = new THREE.Fog(0x0b0f14, 22, 58);

      const camera = new THREE.PerspectiveCamera(52, 1, 0.1, 100);
      camera.position.set(0, 1.65, 7.4);
      camera.lookAt(0, 1.5, -8);

      renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.05;
      renderer.shadowMap.enabled = false;
      renderer.domElement.className = "spatial-canvas";
      renderer.domElement.setAttribute("aria-label", "Controlled three-dimensional night street scene");
      host.appendChild(renderer.domElement);

      createNightStreetScene(scene);

      const render = () => {
        if (!renderer) return;
        const width = Math.max(1, host.clientWidth);
        const height = Math.max(300, Math.round(width * 0.58));
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.render(scene, camera);
      };

      resizeObserver = new ResizeObserver(render);
      resizeObserver.observe(host);
      render();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The 3D renderer could not start in this browser.");
    }

    return () => {
      resizeObserver?.disconnect();
      disposeScene(host, renderer);
    };
  }, []);

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
        <span className="spatial-status">Step 2</span>
      </div>
      <div ref={hostRef} className="spatial-render-host" />
      <div className="spatial-caption">
        Scene targets include traffic signals, readable signage, a pedestrian, vehicle headlights, street lighting, crosswalk markings, storefront light, near/mid/far buildings, and a deliberately darker side region.
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

function disposeScene(host: HTMLDivElement, renderer: THREE.WebGLRenderer | null) {
  if (!renderer) return;

  renderer.domElement.remove();
  renderer.dispose();
  renderer.forceContextLoss();

  while (host.firstChild) {
    host.removeChild(host.firstChild);
  }
}
