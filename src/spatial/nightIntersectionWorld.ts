import type { SpatialChunkDefinition } from "./chunkRuntime";

export const NIGHT_INTERSECTION_WORLD = {
  id: "night-intersection-district",
  horizontalEnvelopeMeters: [500, 500] as const,
  verticalEnvelopeMeters: 80,
  chunkSizeMeters: 64,
};

/**
 * QR1 establishes the streamed-world contract before QR2 begins replacing
 * the visible procedural scene. Chunks are intentionally empty until an
 * approved, locally hosted asset with recorded redistribution rights is
 * committed to the canonical asset manifest.
 *
 * Do not treat this empty list as a finished world or QR1 acceptance.
 */
export const NIGHT_INTERSECTION_CHUNKS: readonly SpatialChunkDefinition[] = [];
