import * as THREE from "three";
import type { SpatialLightingMode, SpatialSceneId } from "./catalog";
import { SpatialChunkRuntime } from "./chunkRuntime";
import { mountNightIntersectionScene, NIGHT_INTERSECTION_NAVIGATION } from "./nightIntersectionScene";
import { NIGHT_INTERSECTION_CHUNKS } from "./nightIntersectionWorld";

export type SpatialGroundNavigation = {
  kind: "ground";
  eyeY: number;
  radius: number;
  speed: number;
  fastSpeed: number;
  initialPosition?: [number, number];
  initialYaw?: number;
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
  setLightingMode: (mode: SpatialLightingMode) => void;
  dispose: () => void;
};

const HANSAPLATZ_REFERENCE_URL = "/assets/panoramas/hansaplatz.jpg";
const DAY_BACKGROUND = new THREE.Color(0xb8d4e8);
const NIGHT_BACKGROUND = new THREE.Color(0x05080d);
const HANSAPLATZ_NAVIGATION: SpatialGroundNavigation = {
  ...NIGHT_INTERSECTION_NAVIGATION,
  // The official LoD2 subset is translated against the Poly Haven HDRI GPS,
  // so runtime X/Z = 0/0 is the photographic capture point. Keep the baseline
  // here; close-up quality views must be separate guided/diagnostic views.
  initialPosition: [0, 0],
  initialYaw: 0,
};

const countAuthoredAssetRoots = (scene: THREE.Scene) => {
  let count = 0;
  scene.traverse((object) => {
    if (typeof object.userData.spatialAssetId === "string") count += 1;
  });
  return count;
};

const tuneHansaplatzLights = (root: THREE.Object3D, mode: SpatialLightingMode) => {
  root.traverse((object) => {
    if (object.name === "night-sky-fill" && object instanceof THREE.HemisphereLight) {
      object.intensity = mode === "day" ? 1.65 : 0.24;
      object.color.set(mode === "day" ? 0xdcecff : 0x7990aa);
      object.groundColor.set(mode === "day" ? 0x8f866f : 0x17120f);
    } else if (object.name === "street-ambient-fill" && object instanceof THREE.AmbientLight) {
      object.intensity = mode === "day" ? 0.34 : 0.05;
      object.color.set(mode === "day" ? 0xfff8e9 : 0x8aa0b5);
    } else if (object.name === "moon-key" && object instanceof THREE.DirectionalLight) {
      object.intensity = mode === "day" ? 2.35 : 0.42;
      object.color.set(mode === "day" ? 0xffefd1 : 0xa8b7d3);
      if (mode === "day") object.position.set(-34, 72, 26);
    } else if (object.name === "intersection-fill" && object instanceof THREE.PointLight) {
      object.intensity = mode === "day" ? 0 : 7.5;
      object.distance = 42;
      object.decay = 2;
    } else if (object.name === "storefront-west-light" && object instanceof THREE.PointLight) {
      object.intensity = mode === "day" ? 0 : 32;
      object.distance = 28;
    } else if (object.name === "storefront-east-light" && object instanceof THREE.PointLight) {
      object.intensity = mode === "day" ? 0 : 28;
      object.distance = 28;
    } else if (object.name.endsWith("-light") && object instanceof THREE.SpotLight) {
      object.intensity = mode === "day" ? 0 : Math.max(object.intensity, 34);
      object.distance = Math.max(object.distance, 30);
    }
  });
};

const mountHansaplatzNightAccents = (scene: THREE.Scene, renderScene: () => void) => {
  const group = new THREE.Group();
  group.name = "hansaplatz-night-v9-accents";

  const warmFacade = new THREE.PointLight(0xffa760, 22, 30, 2);
  warmFacade.name = "hansaplatz-warm-facade-accent";
  warmFacade.position.set(-7, 4.8, -55);
  group.add(warmFacade);

  const shopGlow = new THREE.PointLight(0xffc27d, 18, 24, 2);
  shopGlow.name = "hansaplatz-shop-glow";
  shopGlow.position.set(8, 3.2, -51);
  group.add(shopGlow);

  const coolSeparation = new THREE.PointLight(0x7597b7, 8, 34, 2);
  coolSeparation.name = "hansaplatz-cool-separation";
  coolSeparation.position.set(3, 9, -76);
  group.add(coolSeparation);

  scene.add(group);
  renderScene();
  return () => {
    scene.remove(group);
    group.clear();
  };
};

const loadHansaplatzTexture = (
  scene: THREE.Scene,
  renderScene: () => void,
  options: { useAsEnvironment: boolean; showAsBackground: boolean },
) => {
  let disposed = false;
  let activeTexture: THREE.Texture | null = null;
  const previousBackground = scene.background;
  const previousEnvironment = scene.environment;
  const previousBackgroundIntensity = scene.backgroundIntensity;
  const previousEnvironmentIntensity = scene.environmentIntensity;
  const loader = new THREE.TextureLoader();

  if (!options.showAsBackground) {
    scene.background = NIGHT_BACKGROUND;
    scene.backgroundIntensity = 1;
  }

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
      if (options.showAsBackground) {
        scene.background = texture;
        scene.backgroundIntensity = options.useAsEnvironment ? 0.86 : 1;
      }
      if (options.useAsEnvironment) {
        scene.environment = texture;
        scene.environmentIntensity = 0.14;
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
    if (options.showAsBackground && activeTexture && scene.background === activeTexture) {
      scene.background = previousBackground;
    } else if (!options.showAsBackground && scene.background === NIGHT_BACKGROUND) {
      scene.background = previousBackground;
    }
    if (activeTexture && scene.environment === activeTexture) scene.environment = previousEnvironment;
    scene.backgroundIntensity = previousBackgroundIntensity;
    scene.environmentIntensity = previousEnvironmentIntensity;
    activeTexture?.dispose();
    activeTexture = null;
  };
};

const mountHansaplatzLightingController = (
  scene: THREE.Scene,
  root: THREE.Object3D,
  renderScene: () => void,
) => {
  let disposed = false;
  let mode: SpatialLightingMode = "day";
  let nightEnvironment: THREE.Texture | null = null;
  const previousBackground = scene.background;
  const previousEnvironment = scene.environment;
  const previousBackgroundIntensity = scene.backgroundIntensity;
  const previousEnvironmentIntensity = scene.environmentIntensity;
  const nightAccents = scene.getObjectByName("hansaplatz-night-v9-accents");

  const apply = () => {
    tuneHansaplatzLights(root, mode);
    if (nightAccents) nightAccents.visible = mode === "night";
    if (mode === "day") {
      scene.background = DAY_BACKGROUND;
      scene.backgroundIntensity = 1;
      scene.environment = previousEnvironment;
      scene.environmentIntensity = 1;
    } else {
      scene.background = NIGHT_BACKGROUND;
      scene.backgroundIntensity = 1;
      scene.environment = nightEnvironment ?? previousEnvironment;
      scene.environmentIntensity = nightEnvironment ? 0.14 : previousEnvironmentIntensity;
    }
    renderScene();
  };

  new THREE.TextureLoader().load(
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
      nightEnvironment = texture;
      if (mode === "night") apply();
    },
    undefined,
    (error) => {
      if (!disposed) console.error("Hansaplatz night IBL failed to load", error);
    },
  );

  apply();
  return {
    setMode: (nextMode: SpatialLightingMode) => {
      mode = nextMode;
      apply();
    },
    dispose: () => {
      disposed = true;
      if (scene.background === DAY_BACKGROUND || scene.background === NIGHT_BACKGROUND) scene.background = previousBackground;
      if (scene.environment === nightEnvironment) scene.environment = previousEnvironment;
      scene.backgroundIntensity = previousBackgroundIntensity;
      scene.environmentIntensity = previousEnvironmentIntensity;
      nightEnvironment?.dispose();
      nightEnvironment = null;
    },
  };
};

/**
 * QR2 moves C0's primary-visible responsibility to the Blender-authored chunk.
 * The legacy Night Intersection mount is still temporarily retained for its
 * accepted navigation contract and runtime lights. Hide its close/mid visual
 * geometry so it cannot overlap or visually mask the authored world.
 *
 * The CC0 Hansaplatz panorama remains reconstruction evidence and IBL input for
 * Night Intersection, but it is intentionally not shown as the literal scene
 * background there: its photographed street horizon otherwise leaks through
 * gaps beneath/behind the authored Hamburg geometry as a bright image strip.
 * Photo Reference mode still displays the original panorama directly.
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
    const disposeNightAccents = mountHansaplatzNightAccents(scene, renderScene);
    const lightingController = mountHansaplatzLightingController(scene, mounted.root, renderScene);
    const chunkRuntime = new SpatialChunkRuntime(scene, NIGHT_INTERSECTION_CHUNKS, renderScene);
    return {
      id: sceneId,
      supportsTranslation: true,
      objectCount: mounted.objectCount,
      lightCount: mounted.lightCount + 3,
      navigation: HANSAPLATZ_NAVIGATION,
      updateObserverPosition: (position) => {
        void chunkRuntime.update(position);
      },
      getStreamingDiagnostics: () => ({
        loadedChunkIds: chunkRuntime.getLoadedChunkIds(),
        authoredAssetRootCount: countAuthoredAssetRoots(scene),
      }),
      setLightingMode: (mode) => lightingController.setMode(mode),
      dispose: () => {
        chunkRuntime.dispose();
        lightingController.dispose();
        disposeNightAccents();
        mounted.dispose();
      },
    };
  }

  if (sceneId !== "photo-reference") {
    throw new Error(`Unsupported Explore 3D scene: ${sceneId}`);
  }

  const disposeReferenceEnvironment = loadHansaplatzTexture(scene, renderScene, {
    useAsEnvironment: false,
    showAsBackground: true,
  });

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
    setLightingMode: () => {},
    dispose: disposeReferenceEnvironment,
  };
}
