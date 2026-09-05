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
              This pilot adds a live 3D renderer without replacing the existing image comparison tool. The first controlled night-street scene and perception modes are being added in the next steps.
            </p>
          </section>

          <SpatialRendererShell />

          <section className="spatial-note" aria-label="Spatial pilot limitation">
            <strong>Current step:</strong> renderer integration shell only. Spatial effects must use live scene information where the model depends on view direction, field position, depth, or brightness; they are not intended to be decorative static filters.
          </section>
        </main>
      </div>
    </div>
  );
}

function SpatialRendererShell() {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    let renderer: THREE.WebGLRenderer | null = null;
    let resizeObserver: ResizeObserver | null = null;

    try {
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x171817);

      const camera = new THREE.PerspectiveCamera(52, 1, 0.1, 100);
      camera.position.set(0, 1.6, 6.2);
      camera.lookAt(0, 1, 0);

      renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.shadowMap.enabled = false;
      renderer.domElement.className = "spatial-canvas";
      renderer.domElement.setAttribute("aria-label", "Three-dimensional spatial pilot preview");
      host.appendChild(renderer.domElement);

      const hemisphere = new THREE.HemisphereLight(0xe5e1d6, 0x252522, 1.4);
      scene.add(hemisphere);

      const keyLight = new THREE.DirectionalLight(0xfff2d8, 2.2);
      keyLight.position.set(3, 6, 4);
      scene.add(keyLight);

      const floor = new THREE.Mesh(
        new THREE.PlaneGeometry(16, 16),
        new THREE.MeshStandardMaterial({ color: 0x3a3a37, roughness: 0.95 }),
      );
      floor.rotation.x = -Math.PI / 2;
      scene.add(floor);

      const nearMarker = new THREE.Mesh(
        new THREE.BoxGeometry(1.1, 1.1, 1.1),
        new THREE.MeshStandardMaterial({ color: 0xb6a47a, roughness: 0.72 }),
      );
      nearMarker.position.set(-1.35, 0.55, 0.25);
      scene.add(nearMarker);

      const farMarker = new THREE.Mesh(
        new THREE.BoxGeometry(1.4, 2.2, 1.2),
        new THREE.MeshStandardMaterial({ color: 0x777c80, roughness: 0.82 }),
      );
      farMarker.position.set(1.7, 1.1, -2.1);
      scene.add(farMarker);

      const render = () => {
        if (!renderer) return;
        const width = Math.max(1, host.clientWidth);
        const height = Math.max(280, Math.round(width * 0.58));
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
      if (renderer) {
        renderer.dispose();
        renderer.forceContextLoss();
        renderer.domElement.remove();
      }
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
          <h2>Renderer integration test</h2>
        </div>
        <span className="spatial-status">Step 1</span>
      </div>
      <div ref={hostRef} className="spatial-render-host" />
      <div className="spatial-caption">
        Minimal geometry is intentional here. The controlled night-street scene is the next scheduled step.
      </div>
    </section>
  );
}
