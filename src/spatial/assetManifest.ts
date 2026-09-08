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
export const SPATIAL_ASSET_MANIFEST: readonly SpatialAssetDefinition[] = [];

const assetById = new Map(SPATIAL_ASSET_MANIFEST.map((asset) => [asset.id, asset]));

export function getSpatialAssetDefinition(assetId: string): SpatialAssetDefinition {
  const asset = assetById.get(assetId);
  if (!asset) throw new Error(`Unknown Explore 3D asset: ${assetId}`);
  return asset;
}
