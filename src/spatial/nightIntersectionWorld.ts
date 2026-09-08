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
 * The authored Blender file uses a conventional ground plane at Y=0, while
 * the existing Explore 3D camera contract places the Human eye at runtime Y=0
 * over a legacy ground level of -1.6 m. The chunk placement therefore applies
 * a single -1.6 m Y offset so authored ground and the existing observer contract
 * remain aligned during the recovery migration.
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
