export const SPATIAL_SCENES = [
  {
    id: "night-intersection",
    label: "Night Intersection",
    description: "First geometry-based Explore 3D scene: a dense authored night intersection with real depth, lighting, street detail, vehicles, pedestrians, vegetation, and vertical structure.",
    supportsTranslation: true,
    status: "Geometry scene",
  },
  {
    id: "photo-reference",
    label: "360° Photo Reference",
    description: "Hansaplatz photographic reference. Look-around only because the source has no translation depth.",
    supportsTranslation: false,
    status: "Photo reference",
  },
] as const;

export type SpatialSceneId = (typeof SPATIAL_SCENES)[number]["id"];

export const SPATIAL_OBSERVERS = [
  {
    id: "human",
    label: "Human",
    description: "Human reference observer. Night Intersection supports bounded ground movement with collision-aware navigation; the Photo Reference remains look-only.",
  },
] as const;

export type SpatialObserverId = (typeof SPATIAL_OBSERVERS)[number]["id"];

export const SPATIAL_VISIONS = [
  { id: "normal", label: "Normal" },
  { id: "tunnel", label: "Tunnel Vision" },
  { id: "central_loss", label: "Central Loss" },
  { id: "night", label: "Night / Low Light" },
  { id: "dog", label: "Dog-like" },
  { id: "cataract", label: "Cataract-like" },
] as const;

export type SpatialVisionMode = (typeof SPATIAL_VISIONS)[number]["id"];

export type SpatialGuidedViewpoint = "baseline" | "offset";
export type SpatialViewpointState = SpatialGuidedViewpoint | "free";
