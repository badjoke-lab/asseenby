import type { ModeEvidence } from "./evidenceTypes";
import { getModeEvidence } from "./modeEvidence";

const SPATIAL_REVIEWED_ON = "2026-09-06";

type SpatialEvidenceMode = "tunnel" | "central_loss" | "cataract";

export function getSpatialModeEvidence(modeKey: SpatialEvidenceMode): ModeEvidence {
  const base = getModeEvidence(modeKey);

  if (modeKey === "tunnel") {
    return {
      ...base,
      modelScore: "C",
      modelNote: "The spatial renderer applies a live screen-relative peripheral field-loss shader to the rendered scene while preserving camera position and direction. This is more spatially interactive than the current still-image mask, but it remains a generic circular field-loss model and has not been validated against individual perimetry data.",
      caveat: "Real visual-field loss is often irregular and patient-specific. The spatial mode demonstrates the consequence of losing peripheral scene information; it does not reproduce a measured individual field.",
      lastReviewed: SPATIAL_REVIEWED_ON,
    };
  }

  if (modeKey === "central_loss") {
    return {
      ...base,
      modelScore: "C",
      modelNote: "The spatial Central Loss implementation uses a live screen-relative central-field shader so straight-ahead scene detail is degraded while surrounding information remains more available. The affected region stays tied to the viewer's visual center while the camera turns, allowing active scanning to change which world-space target falls inside the disrupted center. The current shape and strength are generic renderer choices, not measured patient data.",
      caveat: "Real central vision loss and scotomas vary in shape, completeness, distortion, progression, and individual experience. This spatial mode is an educational central-field-loss model, not an individual's measured scotoma or perimetry reconstruction.",
      lastReviewed: SPATIAL_REVIEWED_ON,
    };
  }

  return {
    ...base,
    modelScore: "C",
    modelNote: "The spatial renderer samples the live rendered frame, gates light spread by actual high-luminance scene pixels, and combines that view-dependent glare with optical softness, lower contrast, slight desaturation, warming, and a veil component. Headlights, streetlights, and signals therefore spread more strongly when they are actually in view, while dark directions do not receive the same glare. This remains a generic browser model rather than a validated lens-scatter reconstruction.",
    caveat: "Cataract type, density, scatter, glare, contrast loss, and color shift vary substantially between individuals. This spatial output is an educational scene-dependent simulation, not a patient-specific optical measurement.",
    lastReviewed: SPATIAL_REVIEWED_ON,
  };
}
