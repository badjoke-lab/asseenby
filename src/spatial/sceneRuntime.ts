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

const HANSAPLATZ_REFERENCE_URL = "/assets/panoramas/hansaplatz.jpg";

const countAuthoredAssetRoots = (scene: THREE.Scene) => {
  let count = 0;
  scene.traverse((object) => {
    if (typeof object.userData.spatialAssetId === "string") count += 1;
  });
  return count;
};

const loadHansaplatzTexture = (
  scene: THREE.Scene,
  renderScene: () => void,
  options: { useAsEnvironment: boolean },
) => {
  let disposed = false;
  let activeTexture: THREE.Texture | null = null;
  const previousBackground = scene.background;
  const previousEnvironment = scene.environment;
  const previousBackgroundIntensity = scene.backgroundIntensity;
  const previousEnvironmentIntensity = scene.environmentIntensity;
  const loader = new THREE.TextureLoader();

  loader.load(
    HANSAPLATZ_REFERENCE_URL,
    (texture) => {
      if (disposed) {
        texture.dispose();
        return;
      }
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.mapping = THREE.EquirectangularReflectionMapping;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.magFilter = THREE.LinearFilter;
      texture.anisotropy = 4;
      activeTexture = texture;
      scene.background = texture;
      scene.backgroundIntensity = options.useAsEnvironment ? 0.86 : 1;
      if (options.useAsEnvironment) {
        scene.environment = texture;
        scene.environmentIntensity = 0.42;
      }
      renderScene();
    },
    undefined,
    (error) => {
      if (!disposed) console.error("Hansaplatz reference environment failed to load", error);
    },
  );

  return () => {
    disposed = true;
    if (activeTexture && scene.background === activeTexture) scene.background = previousBackground;
    if (activeTexture && scene.environment === activeTexture) scene.environment = previousEnvironment;
    scene.backgroundIntensity = previousBackgroundIntensity;
    scene.environmentIntensity = previousEnvironmentIntensity;
    activeTexture?.dispose();
    activeTexture = null;
  };
};

/**
 * QR2 moves C0's primary-visible responsibility to the Blender-authored chunk.
 * The legacy Night Intersection mount is still temporarily retained for its
 * accepted navigation contract and runtime lights. Hide its close/mid visual
 * geometry so it cannot overlap or visually mask the authored world. The
 * distant visual context now comes from the real CC0 Hansaplatz panorama used
 * as the reconstruction reference/environment instead of invented far boxes.
 *
 * This is deliberately a migration boundary, not a final architecture. QR3/QR4
 * move lighting/navigation into authored chunk contracts and remove the legacy
 * scene mount entirely.
 */
const retireLegacyPrimaryVisibleGeometry = (root: THREE.Object3D) => {
  root.traverse((object) => {
    if (object instanceof THREE.Points) {
      object.visible = false;
      return;
    }
    if (object instanceof THREE.Line) {
      object.visible = false;
      return;
    }
    if (object instanceof THREE.Mesh) {
      object.visible = false;
    }
  });
};

export function createSpatialSceneRuntime(
  sceneId: SpatialSceneId,
  scene: THREE.Scene,
  renderScene: () => void,
): SpatialSceneRuntime {
  if (sceneId === "night-intersection") {
    const mounted = mountNightIntersectionScene(scene, renderScene);
    retireLegacyPrimaryVisibleGeometry(mounted.root);
    const disposeReferenceEnvironment = loadHansaplatzTexture(scene, renderScene, { useAsEnvironment: true });
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
        disposeReferenceEnvironment();
        mounted.dispose();
      },
    };
  }

  if (sceneId !== "photo-reference") {
    throw new Error(`Unsupported Explore 3D scene: ${sceneId}`);
  }

  const disposeReferenceEnvironment = loadHansaplatzTexture(scene, renderScene, { useAsEnvironment: false });

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
    dispose: disposeReferenceEnvironment,
  };
}
