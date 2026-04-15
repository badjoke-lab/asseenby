import type { ModeEvidence } from "./evidenceTypes";

const REVIEWED_ON = "2026-04-15";

function pendingModeEvidence(summary: string): ModeEvidence {
  return {
    summary,
    evidenceScore: "D",
    modelScore: "D",
    basisNote: "A source review for this mode is still pending.",
    modelNote: "The current transform remains provisional until the evidence pass is completed.",
    caveat: "Treat this mode as exploratory until the evidence set is filled in.",
    supportingSources: [],
    lastReviewed: REVIEWED_ON,
  };
}

export const MODE_EVIDENCE: Record<string, ModeEvidence> = {
  protan: {
    summary: "Research-based approximation of a red-weak color-vision difference. The current image transform is intended for side-by-side comparison, not diagnosis.",
    evidenceScore: "A",
    modelScore: "B",
    basisNote: "Red-green color-vision differences are well described in vision science and public clinical resources.",
    modelNote: "The current output uses an RGB image-space simulation informed by established color-deficiency simulation work, but it is still a screen-space approximation rather than a patient-specific model.",
    caveat: "This mode represents a viewing proxy for comparison. It does not reproduce an individual person's exact perception.",
    primarySource: {
      title: "Machado, Oliveira, Fernandes (2009) — A physiologically-based model for simulation of color vision deficiency",
      url: "https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html",
      kind: "paper",
      note: "Core simulation reference used as the main implementation anchor for color-deficiency-style transforms.",
    },
    supportingSources: [
      {
        title: "National Eye Institute — Types of Color Vision Deficiency",
        url: "https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness/types-color-vision-deficiency",
        kind: "organization",
        note: "Public-facing description of protan, deutan, and tritan categories and their typical effects.",
      },
      {
        title: "National Eye Institute — Color Blindness",
        url: "https://www.nei.nih.gov/index.php/learn-about-eye-health/eye-conditions-and-diseases/color-blindness",
        kind: "organization",
        note: "General clinical framing and limitations for color-vision-deficiency descriptions.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  deutan: {
    summary: "Research-based approximation of a green-weak color-vision difference, shown as a browser-side comparison mode.",
    evidenceScore: "A",
    modelScore: "B",
    basisNote: "Deutan-type differences are among the best-described color-vision-deficiency categories.",
    modelNote: "The transform is guided by established simulation literature, but the present implementation is still constrained by RGB source images and display conditions.",
    caveat: "Use this output to compare tendencies, not to infer exact lived perception.",
    primarySource: {
      title: "Machado, Oliveira, Fernandes (2009) — A physiologically-based model for simulation of color vision deficiency",
      url: "https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html",
      kind: "paper",
      note: "Primary simulation reference for red-green and blue-yellow deficiency approximations.",
    },
    supportingSources: [
      {
        title: "National Eye Institute — Types of Color Vision Deficiency",
        url: "https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness/types-color-vision-deficiency",
        kind: "organization",
        note: "Defines deuteranomaly and related red-green differences in public clinical language.",
      },
      {
        title: "National Eye Institute — Color Blindness",
        url: "https://www.nei.nih.gov/index.php/learn-about-eye-health/eye-conditions-and-diseases/color-blindness",
        kind: "organization",
        note: "General clinical framing and limitations for color-vision-deficiency descriptions.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  tritan: {
    summary: "Research-based approximation of a blue-yellow discrimination shift, presented as a visual comparison aid.",
    evidenceScore: "A",
    modelScore: "B",
    basisNote: "Blue-yellow color-vision differences are clinically recognized and described in reference material alongside red-green differences.",
    modelNote: "The current transform uses a simplified screen-space mapping that aims to express the direction of change rather than exact perceptual reconstruction.",
    caveat: "This is an image transform for comparison. It does not model all spectral or individual differences.",
    primarySource: {
      title: "Machado, Oliveira, Fernandes (2009) — A physiologically-based model for simulation of color vision deficiency",
      url: "https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html",
      kind: "paper",
      note: "Primary simulation reference for color-vision-deficiency matrices and severity interpolation.",
    },
    supportingSources: [
      {
        title: "National Eye Institute — Types of Color Vision Deficiency",
        url: "https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness/types-color-vision-deficiency",
        kind: "organization",
        note: "Describes tritanomaly and tritanopia in public clinical language.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  blur: {
    summary: "Optical softening proxy for reduced image sharpness or out-of-focus viewing.",
    evidenceScore: "B",
    modelScore: "A",
    basisNote: "Blurred vision is a common consequence of refractive and optical focusing problems.",
    modelNote: "A blur kernel is a direct image-space method for expressing reduced sharpness, so the transform itself is comparatively straightforward even though causes of blur vary.",
    caveat: "This mode does not identify why the blur occurs. It only expresses the visual effect of reduced sharpness.",
    primarySource: {
      title: "National Eye Institute — Refractive Errors",
      url: "https://www.nei.nih.gov/index.php/eye-health-information/eye-conditions-and-diseases/refractive-errors",
      kind: "organization",
      note: "Clinical explanation that refractive problems commonly produce blurred or hazy vision.",
    },
    supportingSources: [
      {
        title: "National Eye Institute — Types of Refractive Errors",
        url: "https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/refractive-errors/types-refractive-errors",
        kind: "organization",
        note: "Examples of common refractive causes that make distant or near objects look blurry.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  low_contrast: {
    summary: "Approximation of reduced contrast sensitivity, where edges and differences in luminance become harder to perceive.",
    evidenceScore: "B",
    modelScore: "B",
    basisNote: "Contrast sensitivity is a recognized component of visual function and differs from high-contrast acuity alone.",
    modelNote: "Lowering image contrast is a reasonable first-pass way to show the direction of reduced contrast sensitivity, but it does not model the full spatial-frequency behavior of human vision.",
    caveat: "This is a broad proxy. Real contrast-sensitivity loss can vary with spatial frequency, light level, and ocular condition.",
    primarySource: {
      title: "PubMed / StatPearls — Contrast Sensitivity",
      url: "https://pubmed.ncbi.nlm.nih.gov/35593849/",
      kind: "review",
      note: "Clinical overview of contrast sensitivity, what it measures, and why it differs from standard acuity.",
    },
    supportingSources: [
      {
        title: "NCBI Bookshelf — Visual Acuity (Contrast Sensitivity section)",
        url: "https://www.ncbi.nlm.nih.gov/books/NBK11509/",
        kind: "reference",
        note: "Background explanation of how contrast sensitivity relates to real-world perception and low-light viewing.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  cataract: {
    summary: "Approximation of hazy, lower-contrast, glare-prone viewing inspired by common cataract-related complaints.",
    evidenceScore: "A",
    modelScore: "B",
    basisNote: "Cataracts are well described clinically as causing blurry or hazy vision, faded colors, light sensitivity, and trouble seeing at night.",
    modelNote: "The current transform combines blur, lowered contrast, and a warm veil to express the common direction of cataract-related changes, but it is not a full optical lens model.",
    caveat: "Cataract symptoms vary with type and severity. This mode is a visual proxy for comparison rather than a patient-specific simulation.",
    primarySource: {
      title: "National Eye Institute — Cataracts",
      url: "https://www.nei.nih.gov/index.php/learn-about-eye-health/eye-conditions-and-diseases/cataracts",
      kind: "organization",
      note: "Public clinical overview of cataract symptoms including blurry vision, faded colors, light sensitivity, and night-vision difficulty.",
    },
    supportingSources: [],
    lastReviewed: REVIEWED_ON,
  },
  tunnel: {
    summary: "Approximation of peripheral field loss, keeping the center more visible while darkening and de-emphasizing the outside field.",
    evidenceScore: "A",
    modelScore: "B",
    basisNote: "Peripheral vision loss is a standard clinical description in glaucoma and related visual-field conditions.",
    modelNote: "A radial field mask is a reasonable way to communicate the direction of peripheral field restriction, but it cannot represent a real patient's measured field exactly.",
    caveat: "Real visual-field loss is often irregular rather than perfectly circular. This mode is a simplified communication tool.",
    primarySource: {
      title: "National Eye Institute — Glaucoma",
      url: "https://www.nei.nih.gov/index.php/eye-health-information/eye-conditions-and-diseases/glaucoma",
      kind: "organization",
      note: "Clinical reference describing loss of side or peripheral vision as a later symptom.",
    },
    supportingSources: [],
    lastReviewed: REVIEWED_ON,
  },
  central_loss: {
    summary: "Approximation of central field disruption, based on conditions in which straight-ahead detail vision is lost or degraded.",
    evidenceScore: "A",
    modelScore: "B",
    basisNote: "Central vision loss is a standard clinical description in macular disease, including age-related macular degeneration.",
    modelNote: "A central obscuration mask expresses the main viewing consequence, but it does not reproduce the many shapes and progressions that real central scotomas can take.",
    caveat: "This mode simplifies a broad group of central-vision problems into one visual comparison proxy.",
    primarySource: {
      title: "National Eye Institute — Age-Related Macular Degeneration (AMD)",
      url: "https://www.nei.nih.gov/index.php/eye-health-information/eye-conditions-and-diseases/age-related-macular-degeneration",
      kind: "organization",
      note: "Clinical overview describing blurry or blank areas in the center of vision and loss of sharp straight-ahead detail.",
    },
    supportingSources: [],
    lastReviewed: REVIEWED_ON,
  },
  night: {
    summary: "Approximation of low-light viewing, with reduced color separation, lower contrast, and increased difficulty seeing detail.",
    evidenceScore: "C",
    modelScore: "C",
    basisNote: "Low-light complaints are clinically real, but the present mode blends multiple tendencies into one simplified viewing proxy.",
    modelNote: "The current transform is heuristic and should be treated as a first-pass communication aid rather than a validated low-light vision model.",
    caveat: "Night viewing changes with adaptation state, glare, ocular health, and scene luminance. This mode is intentionally conservative in its claim strength.",
    primarySource: {
      title: "National Eye Institute — Cataracts",
      url: "https://www.nei.nih.gov/index.php/learn-about-eye-health/eye-conditions-and-diseases/cataracts",
      kind: "organization",
      note: "Includes night-vision difficulty among common cataract-related viewing complaints.",
    },
    supportingSources: [
      {
        title: "National Eye Institute — Age-Related Macular Degeneration (AMD)",
        url: "https://www.nei.nih.gov/index.php/eye-health-information/eye-conditions-and-diseases/age-related-macular-degeneration",
        kind: "organization",
        note: "Lists trouble seeing in low lighting as a symptom in intermediate or late AMD.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  fatigue: pendingModeEvidence("Exploratory proxy for visual softness and reduced clarity associated with visual fatigue or prolonged strain."),
  dry_eye: {
    summary: "Approximation of irregular blur and visual discomfort tendencies associated with dry eye symptoms.",
    evidenceScore: "B",
    modelScore: "C",
    basisNote: "Dry eye is commonly described as causing discomfort together with blurry vision and fluctuating clarity.",
    modelNote: "The current transform uses a soft blur plus localized artifacts to express the tendency toward unstable clarity, but it remains heuristic.",
    caveat: "Dry eye symptoms can fluctuate over time and with environment. This is not a patient-specific tear-film model.",
    primarySource: {
      title: "National Eye Institute — Dry Eye",
      url: "https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/dry-eye",
      kind: "organization",
      note: "Clinical reference describing blurry vision among common dry-eye symptoms.",
    },
    supportingSources: [],
    lastReviewed: REVIEWED_ON,
  },
  dog: pendingModeEvidence("Visible-range approximation inspired by common descriptions of canine dichromatic vision."),
  cat: pendingModeEvidence("Visible-range approximation inspired by common descriptions of feline dichromatic vision."),
  bee: pendingModeEvidence("Visible-range approximation only. Ultraviolet response is not reproduced in this version."),
  bird: pendingModeEvidence("Visible-range approximation only. Full avian and ultraviolet perception are outside the current model scope."),
  age: pendingModeEvidence("Reference profile based on broad age-related viewing tendencies rather than individual prediction."),
  sex: pendingModeEvidence("Reference profile based on averaged population framing rather than personal prediction."),
};

export function getModeEvidence(modeKey: string): ModeEvidence {
  return MODE_EVIDENCE[modeKey] ?? pendingModeEvidence("Evidence metadata for this mode has not been reviewed yet.");
}
