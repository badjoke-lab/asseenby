import * as THREE from "three";
import type { SpatialSceneId } from "./catalog";
import { mountNightIntersectionScene } from "./nightIntersectionScene";

export type SpatialSceneRuntime = {
  id: SpatialSceneId;
  supportsTranslation: boolean;
  objectCount: number;
  lightCount: number;
  dispose: () => void;
};

export function createSpatialSceneRuntime(
  sceneId: SpatialSceneId,
  scene: THREE.Scene,
  renderScene: () => void,
): SpatialSceneRuntime {
  if (sceneId === "night-intersection") {
    const mounted = mountNightIntersectionScene(scene, renderScene);
    return {
      id: sceneId,
      supportsTranslation: true,
      objectCount: mounted.objectCount,
      lightCount: mounted.lightCount,
      dispose: mounted.dispose,
    };
  }

  if (sceneId !== "photo-reference") {
    throw new Error(`Unsupported Explore 3D scene: ${sceneId}`);
  }

  let disposed = false;
  let activeTexture: THREE.Texture | null = null;
  scene.fog = null;
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
    objectCount: 0,
    lightCount: 0,
    dispose: () => {
      disposed = true;
      if (activeTexture && scene.background === activeTexture) scene.background = null;
      activeTexture?.dispose();
      activeTexture = null;
    },
  };
}
