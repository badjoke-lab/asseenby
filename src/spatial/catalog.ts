export const SPATIAL_SCENES = [
  {
    id: "photo-reference",
    label: "360° Photo Reference",
    description: "Hansaplatz photographic reference. Look-around only because the source has no translation depth.",
    supportsTranslation: false,
  },
] as const;

export type SpatialSceneId = (typeof SPATIAL_SCENES)[number]["id"];

export const SPATIAL_OBSERVERS = [
  {
    id: "human",
    label: "Human",
    description: "Human reference observer at the source panorama viewpoint. Ground translation begins with geometry scenes, not this photograph.",
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
