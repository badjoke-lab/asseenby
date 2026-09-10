export const SPATIAL_SCENES = [
  {
    id: "night-intersection",
    label: "Hansaplatz 3D",
    description: "Geometry-based Hansaplatz, Hamburg scene. Day and Night use the same authored geometry and camera state so lighting can be compared without changing place.",
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

export const SPATIAL_LIGHTING_MODES = [
  {
    id: "day",
    label: "Day",
    description: "Default comparison lighting. Brighter surfaces and broader color/contrast cues make Vision differences easier to inspect.",
  },
  {
    id: "night",
    label: "Night",
    description: "Low-light environment using the same geometry and viewpoint. Use it as a stress test for glare, dark-region contrast, and visibility.",
  },
] as const;

export type SpatialLightingMode = (typeof SPATIAL_LIGHTING_MODES)[number]["id"];

export const SPATIAL_OBSERVERS = [
  {
    id: "human",
    label: "Human",
    description: "Human reference observer. Hansaplatz 3D supports bounded ground movement with collision-aware navigation; the Photo Reference remains look-only.",
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
