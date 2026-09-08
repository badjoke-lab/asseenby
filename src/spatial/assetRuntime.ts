import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { getSpatialAssetDefinition } from "./assetManifest";

export type SpatialAssetHandle = {
  assetId: string;
  root: THREE.Object3D;
  dispose: () => void;
};

const collectMaterialTextures = (material: THREE.Material, textures: Set<THREE.Texture>) => {
  const values = Object.values(material) as unknown[];
  for (const value of values) {
    if (value instanceof THREE.Texture) textures.add(value);
  }
};

const disposeObjectTree = (root: THREE.Object3D) => {
  const geometries = new Set<THREE.BufferGeometry>();
  const materials = new Set<THREE.Material>();
  const textures = new Set<THREE.Texture>();

  root.traverse((object) => {
    const mesh = object as THREE.Mesh;
    if (mesh.geometry instanceof THREE.BufferGeometry) geometries.add(mesh.geometry);

    const material = mesh.material;
    if (Array.isArray(material)) {
      material.forEach((entry) => {
        if (entry instanceof THREE.Material) materials.add(entry);
      });
    } else if (material instanceof THREE.Material) {
      materials.add(material);
    }
  });

  materials.forEach((material) => collectMaterialTextures(material, textures));
  textures.forEach((texture) => texture.dispose());
  materials.forEach((material) => material.dispose());
  geometries.forEach((geometry) => geometry.dispose());
};

const configureVisibleMeshes = (root: THREE.Object3D, qualityRole: string) => {
  const casts = qualityRole === "primary-visible" || qualityRole === "secondary-visible";
  root.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return;
    object.castShadow = casts;
    object.receiveShadow = casts;
  });
};

export class SpatialAssetRuntime {
  private readonly loader = new GLTFLoader();

  async mount(assetId: string, parent: THREE.Object3D): Promise<SpatialAssetHandle> {
    const definition = getSpatialAssetDefinition(assetId);
    if (!definition.localUrl) {
      throw new Error(`Explore 3D asset is not locally available: ${assetId}`);
    }

    const gltf = await this.loader.loadAsync(definition.localUrl);
    const root = gltf.scene;
    root.name = `asset:${assetId}`;
    root.userData.spatialAssetId = assetId;
    root.userData.spatialAssetQualityRole = definition.qualityRole;
    configureVisibleMeshes(root, definition.qualityRole);
    parent.add(root);

    let disposed = false;
    return {
      assetId,
      root,
      dispose: () => {
        if (disposed) return;
        disposed = true;
        root.removeFromParent();
        disposeObjectTree(root);
      },
    };
  }
}
