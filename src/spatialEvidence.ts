import type { ModeEvidence } from "./evidenceTypes";
import { getModeEvidence } from "./modeEvidence";

const SPATIAL_REVIEWED_ON = "2026-09-06";

export function getSpatialModeEvidence(modeKey: "tunnel" | "cataract"): ModeEvidence {
  const base = getModeEvidence(modeKey);

  if (modeKey === "tunnel") {
    return {
      ...base,
      modelScore: "C",
      modelNote: "The spatial pilot applies a live screen-relative peripheral field-loss shader to the rendered scene while preserving camera position and direction. This is more spatially interactive than the current still-image mask, but it remains a generic circular field-loss model and has not been validated against individual perimetry data.",
      caveat: "Real visual-field loss is often irregular and patient-specific. The spatial mode demonstrates the consequence of losing peripheral scene information; it does not reproduce a measured individual field.",
      lastReviewed: SPATIAL_REVIEWED_ON,
    };
  }

  return {
    ...base,
    modelScore: "C",
    modelNote: "The spatial pilot combines live bright-pass bloom from rendered scene luminance with optical softness, lower contrast, warming, and a veil pass. Headlights and streetlights therefore create stronger glare when they enter the view instead of receiving a fixed decorative glow. This is still a generic browser model rather than a validated lens-scatter reconstruction.",
    caveat: "Cataract type, density, scatter, glare, contrast loss, and color shift vary substantially between individuals. This spatial output is an educational scene-dependent simulation, not a patient-specific optical measurement.",
    lastReviewed: SPATIAL_REVIEWED_ON,
  };
}
