import type { SpatialChunkDefinition } from "./chunkRuntime";

export const NIGHT_INTERSECTION_WORLD = {
  id: "night-intersection-district",
  horizontalEnvelopeMeters: [500, 500] as const,
  verticalEnvelopeMeters: 80,
  chunkSizeMeters: 64,
};

/**
 * Central 64 m Night Intersection chunk.
 *
 * QR1 proved the authored asset/chunk runtime with a single secondary lamp.
 * QR2 moves C0's primary-visible responsibility to the Blender-authored core.
 * The Blender source is normalized into the runtime Y-up coordinate frame before
 * glTF export. Its authored ground is therefore Y=0 in Three.js. The existing
 * Explore 3D Human observer contract keeps eye Y=0 over the legacy -1.6 m ground,
 * so the chunk placement applies one -1.6 m Y offset during the recovery migration.
 */
export const NIGHT_INTERSECTION_CHUNKS: readonly SpatialChunkDefinition[] = [
  {
    id: "c0",
    center: [0, 0, -28],
    halfExtent: [32, 40, 32],
    loadRadius: 80,
    unloadRadius: 104,
    assets: [
      {
        assetId: "asseenby-night-intersection-c0-v1",
        position: [0, -1.6, 0],
        rotation: [0, 0, 0],
        scale: 1,
      },
    ],
  },
];
