import * as THREE from "three";
import type { SpatialSceneId } from "./catalog";
import { SpatialChunkRuntime } from "./chunkRuntime";
import { mountNightIntersectionScene, NIGHT_INTERSECTION_NAVIGATION } from "./nightIntersectionScene";
import { NIGHT_INTERSECTION_CHUNKS } from "./nightIntersectionWorld";

export type SpatialGroundNavigation = {
  kind: "ground";
  eyeY: number;
  radius: number;
  speed: number;
  fastSpeed: number;
  canOccupy: (x: number, z: number, radius?: number) => boolean;
};

export type SpatialStreamingDiagnostics = {
  loadedChunkIds: string[];
  authoredAssetRootCount: number;
};

export type SpatialSceneRuntime = {
  id: SpatialSceneId;
  supportsTranslation: boolean;
  objectCount: number;
  lightCount: number;
  navigation: SpatialGroundNavigation | null;
  updateObserverPosition: (position: THREE.Vector3) => void;
  getStreamingDiagnostics: () => SpatialStreamingDiagnostics;
  dispose: () => void;
};

const countAuthoredAssetRoots = (scene: THREE.Scene) => {
  let count = 0;
  scene.traverse((object) => {
    if (typeof object.userData.spatialAssetId === "string") count += 1;
  });
  return count;
};

export function createSpatialSceneRuntime(
  sceneId: SpatialSceneId,
  scene: THREE.Scene,
  renderScene: () => void,
): SpatialSceneRuntime {
  if (sceneId === "night-intersection") {
    const mounted = mountNightIntersectionScene(scene, renderScene);
    const chunkRuntime = new SpatialChunkRuntime(scene, NIGHT_INTERSECTION_CHUNKS, renderScene);
    return {
      id: sceneId,
      supportsTranslation: true,
      objectCount: mounted.objectCount,
      lightCount: mounted.lightCount,
      navigation: NIGHT_INTERSECTION_NAVIGATION,
      updateObserverPosition: (position) => {
        void chunkRuntime.update(position);
      },
      getStreamingDiagnostics: () => ({
        loadedChunkIds: chunkRuntime.getLoadedChunkIds(),
        authoredAssetRootCount: countAuthoredAssetRoots(scene),
      }),
      dispose: () => {
        chunkRuntime.dispose();
        mounted.dispose();
      },
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
    navigation: null,
    updateObserverPosition: () => {},
    getStreamingDiagnostics: () => ({
      loadedChunkIds: [],
      authoredAssetRootCount: countAuthoredAssetRoots(scene),
    }),
    dispose: () => {
      disposed = true;
      if (activeTexture && scene.background === activeTexture) scene.background = null;
      activeTexture?.dispose();
      activeTexture = null;
    },
  };
}
