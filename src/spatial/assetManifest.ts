export type SpatialAssetLicense = {
  spdx: string;
  name: string;
  attributionRequired: boolean;
  redistributionAllowed: boolean;
};

export type SpatialAssetProvenance = {
  creator: string;
  sourceUrl: string;
  sourceAssetId?: string;
  sourceVersion?: string;
  license: SpatialAssetLicense;
  notes?: string;
};

export type SpatialAssetQualityRole =
  | "primary-visible"
  | "secondary-visible"
  | "distant-lod"
  | "collision-only"
  | "development-bootstrap";

export type SpatialAssetDefinition = {
  id: string;
  label: string;
  format: "glb" | "gltf";
  localUrl: string | null;
  qualityRole: SpatialAssetQualityRole;
  provenance: SpatialAssetProvenance;
};

/**
 * Canonical runtime manifest for third-party/authored Explore 3D assets.
 *
 * Rules:
 * - Do not add an asset until redistribution rights have been checked.
 * - `localUrl` must point to a repository-hosted/static-hosted file; the
 *   production renderer must not depend on third-party runtime hosting.
 * - A `development-bootstrap` or `distant-lod` asset can prove the loader
 *   contract but cannot close the QR2 visible-quality gate.
 * - Final QR2 close-range assets must use `primary-visible` where appropriate
 *   and pass rendered review; the role itself is not an automatic approval.
 */
export const SPATIAL_ASSET_MANIFEST: readonly SpatialAssetDefinition[] = [
  {
    id: "asseenby-night-intersection-c0-v1",
    label: "Night Intersection C0 authored visible core v1",
    format: "glb",
    localUrl: "/assets/3d/night-intersection/c0/core/night-intersection-c0.glb",
    qualityRole: "primary-visible",
    provenance: {
      creator: "badjoke-lab / AsSeenBy",
      sourceUrl: "https://github.com/badjoke-lab/asseenby/tree/main/assets-src/blender/night-intersection/c0",
      sourceAssetId: "night-intersection-c0",
      sourceVersion: "QR2 C0 v1",
      license: {
        spdx: "MIT",
        name: "MIT License",
        attributionRequired: true,
        redistributionAllowed: true,
      },
      notes:
        "Original C0 geometry is authored in Blender and exported through scripts/blender/export_night_intersection.py. The GLB embeds CC0 Poly Haven Asphalt 01 and Brick Wall 001 1K PBR maps; exact material provenance and source hashes are retained under assets-src/blender/night-intersection/materials. primary-visible marks the intended QR2 role only: rendered desktop/mobile review is still required before QR2 can close.",
    },
  },
  {
    id: "polyhaven-street-lamp-02-1k",
    label: "Street Lamp 02 (Poly Haven 1K)",
    format: "gltf",
    localUrl: "/assets/3d/night-intersection/c0/street-lamp-02/street_lamp_02_1k.gltf",
    qualityRole: "secondary-visible",
    provenance: {
      creator: "Josh Dean / Poly Haven",
      sourceUrl: "https://polyhaven.com/a/street_lamp_02",
      sourceAssetId: "street_lamp_02",
      sourceVersion: "1K glTF runtime variant",
      license: {
        spdx: "CC0-1.0",
        name: "CC0 1.0 Universal",
        attributionRequired: false,
        redistributionAllowed: true,
      },
      notes:
        "Authored PBR glTF exported by Khronos glTF Blender I/O. The checked-in runtime bundle includes base color, normal and ARM textures. Fetched glTF SHA-256: 3a8a42486c5dc4538a8b44aeeef502c64a1c9d0d42fa5610e37886c355337ff8. SOURCE.txt records the exact CDN URLs. This first asset proves the authored asset/runtime path; by itself it does not close the QR2 scene-quality gate.",
    },
  },
];

const assetById = new Map(SPATIAL_ASSET_MANIFEST.map((asset) => [asset.id, asset]));

export function getSpatialAssetDefinition(assetId: string): SpatialAssetDefinition {
  const asset = assetById.get(assetId);
  if (!asset) throw new Error(`Unknown Explore 3D asset: ${assetId}`);
  return asset;
}
