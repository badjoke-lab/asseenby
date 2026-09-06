import type { ModeEvidence } from "./evidenceTypes";
import { getModeEvidence } from "./modeEvidence";

const SPATIAL_REVIEWED_ON = "2026-09-06";

type SpatialEvidenceMode = "tunnel" | "central_loss" | "night" | "dog" | "cataract";

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

  if (modeKey === "night") {
    return {
      ...base,
      modelScore: "C",
      modelNote: "The spatial Night / Low Light renderer uses displayed scene luminance from the current rendered view to increase desaturation, contrast loss, and fine-detail loss in darker regions while leaving brighter sources more available. Because the 360° panorama is a tone-mapped RGB photograph rather than calibrated radiometric scene data, this is a luminance-dependent communication model, not a physical scotopic or mesopic reconstruction.",
      caveat: "Real low-light vision changes with absolute luminance, rod/cone contribution, adaptation state, pupil size, glare, ocular health, and individual differences. The current spatial mode does not model dark-adaptation timing, calibrated cd/m², or full rod/cone spectral sensitivity.",
      lastReviewed: SPATIAL_REVIEWED_ON,
    };
  }

  if (modeKey === "dog") {
    return {
      ...base,
      modelScore: "C",
      modelNote: "The spatial Dog-like renderer applies a simplified two-channel visible-range color translation plus mild angularly scaled softening to the live 360° view. It is grounded in strong evidence for canine dichromacy and lower visual acuity than humans, but a standard RGB panorama cannot reconstruct canine cone catches for arbitrary spectra and the blur is not a calibrated individual-dog acuity model.",
      caveat: "Dog vision varies across individuals and breeds. This mode does not model breed-dependent field of view, retinal topography, motion sensitivity, tapetal/rod-mediated low-light advantages, spectral metamerism, or neural interpretation. It is a human-display comparison proxy, not literal canine qualia.",
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
