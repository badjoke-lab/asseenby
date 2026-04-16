import type { ModeEvidence } from "./evidenceTypes";

const REVIEWED_ON = "2026-04-16";

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
    modelNote: "The current output uses a linear-RGB deficiency transform with additional red-green axis compression. It is stronger than a naive RGB mix, but still remains a screen-space approximation rather than a patient-specific perceptual model.",
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
    modelNote: "The transform now combines a linear-RGB deficiency mapping with additional red-green axis compression. This improves the visible comparison behavior, but it is still constrained by source-image gamut and display conditions.",
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
    modelNote: "The current transform uses a linear-RGB deficiency mapping plus blue-yellow axis compression. It is a stronger comparison aid than a simple tint shift, but still not a full spectral or observer-specific simulation.",
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
    modelNote: "The transform now combines contrast reduction, slight desaturation, and mild highlight softening. That makes it a better first-pass comparison aid, but it still does not model the full spatial-frequency behavior of human contrast sensitivity.",
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
    modelNote: "The current transform combines blur, contrast loss, desaturation, warm veil, softened highlights, and bloom. This is a stronger screen-space communication model than blur alone, but it is still not a physical lens-scatter simulation.",
    caveat: "Cataract symptoms vary with type and severity. This mode is a visual proxy for comparison rather than a patient-specific simulation.",
    primarySource: {
      title: "National Eye Institute — Cataracts",
      url: "https://www.nei.nih.gov/index.php/learn-about-eye-health/eye-conditions-and-diseases/cataracts",
      kind: "organization",
      note: "Public clinical overview of cataract symptoms including blurry vision, faded colors, light sensitivity, and night-vision difficulty.",
    },
    supportingSources: [
      {
        title: "MedlinePlus — Cataract",
        url: "https://medlineplus.gov/cataract.html",
        kind: "organization",
        note: "Additional public clinical summary describing cloudy vision and glare-related complaints.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  tunnel: {
    summary: "Approximation of peripheral field loss, keeping the center more visible while darkening and de-emphasizing the outside field.",
    evidenceScore: "A",
    modelScore: "B",
    basisNote: "Peripheral vision loss is a standard clinical description in glaucoma and related visual-field conditions.",
    modelNote: "The current output now combines radial masking with peripheral blur and desaturation tendencies. It communicates peripheral field restriction more convincingly than a black vignette alone, but it still cannot represent a measured patient field exactly.",
    caveat: "Real visual-field loss is often irregular rather than perfectly circular. This mode is a simplified communication tool.",
    primarySource: {
      title: "National Eye Institute — Glaucoma",
      url: "https://www.nei.nih.gov/index.php/eye-health-information/eye-conditions-and-diseases/glaucoma",
      kind: "organization",
      note: "Clinical reference describing loss of side or peripheral vision as a later symptom.",
    },
    supportingSources: [
      {
        title: "Merck Manual Consumer Version — Glaucoma",
        url: "https://www.merckmanuals.com/home/eye-disorders/glaucoma/glaucoma",
        kind: "organization",
        note: "General clinical description of peripheral field loss progression and tunnel-vision-like outcomes.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  central_loss: {
    summary: "Approximation of central field disruption, based on conditions in which straight-ahead detail vision is lost or degraded.",
    evidenceScore: "A",
    modelScore: "B",
    basisNote: "Central vision loss is a standard clinical description in macular disease, including age-related macular degeneration.",
    modelNote: "The current output now combines central masking with localized blur and partial desaturation. It better conveys degraded central detail, but it still simplifies the irregular forms and progressions of real central scotomas.",
    caveat: "This mode simplifies a broad group of central-vision problems into one visual comparison proxy.",
    primarySource: {
      title: "National Eye Institute — Age-Related Macular Degeneration (AMD)",
      url: "https://www.nei.nih.gov/index.php/eye-health-information/eye-conditions-and-diseases/age-related-macular-degeneration",
      kind: "organization",
      note: "Clinical overview describing blurry or blank areas in the center of vision and loss of sharp straight-ahead detail.",
    },
    supportingSources: [
      {
        title: "MedlinePlus — Macular Degeneration",
        url: "https://medlineplus.gov/maculardegeneration.html",
        kind: "organization",
        note: "Public clinical summary describing central-vision difficulty in everyday tasks.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  night: {
    summary: "Approximation of low-light viewing, with reduced color separation, lower contrast, and increased difficulty seeing detail.",
    evidenceScore: "B",
    modelScore: "C",
    basisNote: "Difficulty seeing in low light or at night is a recognized clinical complaint, but this mode deliberately compresses multiple possible causes into one simplified viewing proxy.",
    modelNote: "The current transform darkens, desaturates, and softens detail to express low-light difficulty. It is useful as a communication aid, but it remains heuristic rather than a validated scotopic vision model.",
    caveat: "Night viewing changes with adaptation state, glare, ocular health, and scene luminance. This mode is intentionally conservative in its claim strength.",
    primarySource: {
      title: "National Eye Institute — Low Vision",
      url: "https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/low-vision",
      kind: "organization",
      note: "Lists night blindness and low-light difficulty as a recognized low-vision type.",
    },
    supportingSources: [
      {
        title: "National Eye Institute — Cataracts",
        url: "https://www.nei.nih.gov/index.php/learn-about-eye-health/eye-conditions-and-diseases/cataracts",
        kind: "organization",
        note: "Includes trouble seeing at night among common cataract-related complaints.",
      },
      {
        title: "National Eye Institute — Age-Related Macular Degeneration (AMD)",
        url: "https://www.nei.nih.gov/index.php/eye-health-information/eye-conditions-and-diseases/age-related-macular-degeneration",
        kind: "organization",
        note: "Lists trouble seeing in low lighting as a symptom in intermediate or late AMD.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  fatigue: {
    summary: "Approximation of visual softness and reduced comfort associated with sustained visual effort or digital eye strain.",
    evidenceScore: "B",
    modelScore: "C",
    basisNote: "Digital eye strain and sustained near-work discomfort are widely described as causing eyestrain, blur, headaches, and reduced comfort during prolonged screen use.",
    modelNote: "The current transform uses mild blur and contrast reduction to express the general tendency toward tired, less crisp viewing. It is a communication proxy rather than a validated fatigue-specific visual model.",
    caveat: "Visual fatigue is influenced by screen distance, glare, refractive error, dryness, posture, and task duration. This mode compresses those contributors into one simplified output.",
    primarySource: {
      title: "American Optometric Association — Computer Vision Syndrome",
      url: "https://www.aoa.org/healthy-eyes/eye-and-vision-conditions/computer-vision-syndrome?sso=y",
      kind: "organization",
      note: "Public clinical overview of digital eye strain symptoms including eyestrain, blurred vision, dry eyes, and headaches.",
    },
    supportingSources: [
      {
        title: "National Eye Institute — Refractive Errors",
        url: "https://www.nei.nih.gov/index.php/eye-health-information/eye-conditions-and-diseases/refractive-errors",
        kind: "organization",
        note: "Lists eye strain and trouble focusing while reading or using a computer among common vision complaints.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
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
    supportingSources: [
      {
        title: "National Eye Institute — Causes of Dry Eye",
        url: "https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/dry-eye/causes-dry-eye",
        kind: "organization",
        note: "Adds context on how dry eye can lead to discomfort and vision problems, and why symptoms fluctuate.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  dog: {
    summary: "Visible-range approximation inspired by well-studied canine dichromatic vision, presented as a comparison proxy rather than a full dog-view simulation.",
    evidenceScore: "A",
    modelScore: "C",
    basisNote: "Canine color vision is comparatively well described in behavioral and photopigment studies, with evidence consistent with dichromatic vision.",
    modelNote: "The current dog mode uses a simplified visible-range color remapping plus softening. It communicates the broad red-green limitation better than an unmodified image, but it does not model canine acuity, rod dominance, motion sensitivity, or low-light strengths.",
    caveat: "This mode is a browser-side visible-range proxy. It should not be read as a complete simulation of what a dog sees.",
    primarySource: {
      title: "Color vision in the dog",
      url: "https://pubmed.ncbi.nlm.nih.gov/2487095/",
      kind: "paper",
      note: "Behavioral and sensitivity data supporting dichromatic color vision in dogs.",
    },
    supportingSources: [
      {
        title: "Are dogs red–green colour blind? — PMC",
        url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC5717654/",
        kind: "paper",
        note: "Behavioral evidence that dogs show a response pattern similar to red-green color-blind human observers.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  cat: {
    summary: "Visible-range approximation inspired by limited feline color discrimination, kept conservative because feline color-vision framing is less straightforward than the canine case.",
    evidenceScore: "C",
    modelScore: "C",
    basisNote: "Historical studies support the presence of more than one cone process and some color discrimination in cats, but the literature is older and less straightforward to summarize into a single simple public model.",
    modelNote: "The current cat mode is a conservative visible-range proxy with remapped color relationships and reduced saturation. It is intentionally presented as heuristic rather than as a settled feline spectral model.",
    caveat: "This mode should be read as a cautious educational proxy. It does not capture feline low-light advantages or resolve all uncertainty in the older cat color-vision literature.",
    primarySource: {
      title: "Cat colour vision: evidence for more than one cone process — PMC",
      url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC1395586/",
      kind: "paper",
      note: "Evidence that cats can discriminate some colors beyond a single-cone account.",
    },
    supportingSources: [
      {
        title: "Trichromatic vision in the cat",
        url: "https://pubmed.ncbi.nlm.nih.gov/910161/",
        kind: "paper",
        note: "Older evidence that complicates a simple one-line public framing of feline color vision and supports a conservative score here.",
      },
      {
        title: "Cone Pathways through the Retina — NCBI Bookshelf",
        url: "https://www.ncbi.nlm.nih.gov/books/NBK11529/",
        kind: "reference",
        note: "Background reference noting that most mammals are dichromatic, useful as context but not a cat-specific conclusion on its own.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  bee: {
    summary: "Visible-range approximation inspired by honeybee color vision, with strong evidence for ultraviolet-, blue-, and green-sensitive channels but a deliberately weak implementation claim.",
    evidenceScore: "A",
    modelScore: "D",
    basisNote: "Honeybee color vision is well studied and includes ultraviolet, blue, and green sensitivity, making it much richer than a standard human-visible RGB transform.",
    modelNote: "The current bee mode only shifts visible-range relationships inside a standard image. It does not reproduce ultraviolet information, nectar-guide structure, or bee-specific scene coding, so the implementation score remains deliberately low.",
    caveat: "This mode is not a bee-vision simulation in the full biological sense. It is only a visible-range comparison proxy.",
    primarySource: {
      title: "Mechanisms, functions and ecology of colour vision in the honeybee",
      url: "https://pubmed.ncbi.nlm.nih.gov/24828676/",
      kind: "paper",
      note: "Comprehensive review of honeybee color vision and its ecological significance.",
    },
    supportingSources: [
      {
        title: "Honeybee blue- and ultraviolet-sensitive opsins",
        url: "https://pubmed.ncbi.nlm.nih.gov/9502802/",
        kind: "paper",
        note: "Photoreceptor evidence for ultraviolet and blue sensitivity in honeybee vision.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  bird: {
    summary: "Visible-range approximation inspired by avian color vision, with strong biological evidence for ultraviolet-sensitive and tetrachromatic systems but a deliberately weak implementation claim.",
    evidenceScore: "A",
    modelScore: "D",
    basisNote: "Many birds have four cone classes and bird vision commonly extends into ultraviolet or violet-sensitive ranges, which are outside the information content of a standard RGB image.",
    modelNote: "The current bird-like mode only boosts visible-range contrast and color vividness. It does not reproduce tetrachromacy, ultraviolet sensitivity, oil-droplet filtering, or species-specific avian spectral tuning, so the model score stays low.",
    caveat: "This mode should be read as a very limited visual proxy. It does not simulate the full color space available to many birds.",
    primarySource: {
      title: "Ultraviolet vision in birds: the importance of transparent eye media",
      url: "https://pubmed.ncbi.nlm.nih.gov/24258716/",
      kind: "paper",
      note: "Evidence that ultraviolet-sensitive pigments and UV transmission are important features of avian vision.",
    },
    supportingSources: [
      {
        title: "Biological aspects of bird colouration and avian colour vision including ultraviolet range",
        url: "https://pubmed.ncbi.nlm.nih.gov/8023462/",
        kind: "paper",
        note: "Classic reference describing widespread four-cone avian color vision including ultraviolet range.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  age: pendingModeEvidence("Reference profile based on broad age-related viewing tendencies rather than individual prediction."),
  sex: pendingModeEvidence("Reference profile based on averaged population framing rather than personal prediction."),
};

export function getModeEvidence(modeKey: string): ModeEvidence {
  return MODE_EVIDENCE[modeKey] ?? pendingModeEvidence("Evidence metadata for this mode has not been reviewed yet.");
}
