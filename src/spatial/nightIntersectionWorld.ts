import type { SpatialChunkDefinition } from "./chunkRuntime";

export const NIGHT_INTERSECTION_WORLD = {
  id: "night-intersection-district",
  horizontalEnvelopeMeters: [500, 500] as const,
  verticalEnvelopeMeters: 80,
  chunkSizeMeters: 64,
};

/**
 * The first authored-world target is the central 64 m intersection chunk C0.
 * During QR1/QR2 the procedural Night Intersection remains mounted as a
 * technical fallback/reference while authored assets begin replacing its
 * primary-visible responsibilities.
 *
 * Chunk centers are used for load/unload distance. Asset placement is in the
 * scene's existing world coordinates so authored assets can coexist with the
 * temporary procedural baseline during recovery.
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
        assetId: "polyhaven-street-lamp-02-1k",
        // Mount the authored wall lamp on the north-facing facade of the
        // temporary south-east block. It is a QR1 runtime/PBR proof, not the
        // final C0 facade composition; QR2 will replace the procedural block.
        position: [20, -1.205, -13.0],
        rotation: [0, Math.PI, 0],
        scale: 1,
      },
    ],
  },
];
