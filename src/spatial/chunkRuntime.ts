import * as THREE from "three";
import { SpatialAssetRuntime, type SpatialAssetHandle } from "./assetRuntime";

export type SpatialChunkId = string;

export type SpatialAssetPlacement = {
  assetId: string;
  position: [number, number, number];
  rotation?: [number, number, number];
  scale?: number | [number, number, number];
};

export type SpatialChunkDefinition = {
  id: SpatialChunkId;
  center: [number, number, number];
  halfExtent: [number, number, number];
  loadRadius: number;
  unloadRadius: number;
  assets: readonly SpatialAssetPlacement[];
};

export type SpatialChunkState = "unloaded" | "loading" | "loaded" | "error";

type MountedChunk = {
  definition: SpatialChunkDefinition;
  root: THREE.Group;
  assets: SpatialAssetHandle[];
};

const horizontalDistance = (position: THREE.Vector3, center: [number, number, number]) => {
  const dx = position.x - center[0];
  const dz = position.z - center[2];
  return Math.hypot(dx, dz);
};

const applyPlacement = (root: THREE.Object3D, placement: SpatialAssetPlacement) => {
  root.position.set(...placement.position);
  if (placement.rotation) root.rotation.set(...placement.rotation);
  if (typeof placement.scale === "number") {
    root.scale.setScalar(placement.scale);
  } else if (placement.scale) {
    root.scale.set(...placement.scale);
  }
};

export class SpatialChunkRuntime {
  private readonly assetRuntime = new SpatialAssetRuntime();
  private readonly states = new Map<SpatialChunkId, SpatialChunkState>();
  private readonly mounted = new Map<SpatialChunkId, MountedChunk>();
  private readonly inFlight = new Map<SpatialChunkId, Promise<void>>();
  private disposed = false;

  constructor(
    private readonly worldRoot: THREE.Object3D,
    private readonly chunks: readonly SpatialChunkDefinition[],
    private readonly onChanged: () => void,
  ) {
    chunks.forEach((chunk) => this.states.set(chunk.id, "unloaded"));
  }

  getState(chunkId: SpatialChunkId): SpatialChunkState {
    return this.states.get(chunkId) ?? "unloaded";
  }

  getLoadedChunkIds(): SpatialChunkId[] {
    return [...this.mounted.keys()];
  }

  async update(observerPosition: THREE.Vector3): Promise<void> {
    if (this.disposed) return;

    const operations: Promise<void>[] = [];
    for (const chunk of this.chunks) {
      const distance = horizontalDistance(observerPosition, chunk.center);
      const state = this.getState(chunk.id);

      if ((state === "unloaded" || state === "error") && distance <= chunk.loadRadius) {
        operations.push(this.load(chunk));
      } else if (state === "loaded" && distance > chunk.unloadRadius) {
        this.unload(chunk.id);
      }
    }

    if (operations.length) await Promise.all(operations);
  }

  private load(chunk: SpatialChunkDefinition): Promise<void> {
    const existing = this.inFlight.get(chunk.id);
    if (existing) return existing;

    this.states.set(chunk.id, "loading");
    const task = this.mountChunk(chunk)
      .then(() => {
        if (!this.disposed) this.states.set(chunk.id, "loaded");
      })
      .catch((error) => {
        if (!this.disposed) this.states.set(chunk.id, "error");
        console.error(`Explore 3D chunk failed to load: ${chunk.id}`, error);
      })
      .finally(() => {
        this.inFlight.delete(chunk.id);
        this.onChanged();
      });

    this.inFlight.set(chunk.id, task);
    return task;
  }

  private async mountChunk(definition: SpatialChunkDefinition): Promise<void> {
    const root = new THREE.Group();
    root.name = `chunk:${definition.id}`;
    this.worldRoot.add(root);

    const assets: SpatialAssetHandle[] = [];
    try {
      for (const placement of definition.assets) {
        if (this.disposed) break;
        const handle = await this.assetRuntime.mount(placement.assetId, root);
        applyPlacement(handle.root, placement);
        assets.push(handle);
      }

      if (this.disposed) {
        assets.forEach((asset) => asset.dispose());
        root.removeFromParent();
        return;
      }

      this.mounted.set(definition.id, { definition, root, assets });
    } catch (error) {
      assets.forEach((asset) => asset.dispose());
      root.removeFromParent();
      throw error;
    }
  }

  unload(chunkId: SpatialChunkId): void {
    const chunk = this.mounted.get(chunkId);
    if (!chunk) return;

    chunk.assets.forEach((asset) => asset.dispose());
    chunk.root.removeFromParent();
    this.mounted.delete(chunkId);
    this.states.set(chunkId, "unloaded");
    this.onChanged();
  }

  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    [...this.mounted.keys()].forEach((chunkId) => this.unload(chunkId));
    this.inFlight.clear();
    this.states.clear();
  }
}
