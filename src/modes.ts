export type ModeCategory = "Human" | "Animal" | "Reference";
export type Confidence = "Strong" | "Estimated" | "Reference";
export type CompareMode = "slider" | "split" | "side-by-side";

export type ModeDef = {
  key: string;
  label: string;
  category: ModeCategory;
  confidence: Confidence;
  note: string;
};

export const MODES: ModeDef[] = [
  { key: "protan", label: "Protan-like", category: "Human", confidence: "Strong", note: "Reduced red-channel discrimination approximation." },
  { key: "deutan", label: "Deutan-like", category: "Human", confidence: "Strong", note: "Reduced green-channel discrimination approximation." },
  { key: "tritan", label: "Tritan-like", category: "Human", confidence: "Strong", note: "Blue-yellow discrimination shift approximation." },
  { key: "blur", label: "Blur", category: "Human", confidence: "Strong", note: "Lower visual sharpness approximation." },
  { key: "low_contrast", label: "Low Contrast", category: "Human", confidence: "Strong", note: "Reduced contrast sensitivity approximation." },
  { key: "cataract", label: "Cataract-like", category: "Human", confidence: "Strong", note: "Hazy, lower-contrast, yellowed viewing approximation." },
  { key: "tunnel", label: "Tunnel Vision", category: "Human", confidence: "Strong", note: "Peripheral field loss approximation." },
  { key: "central_loss", label: "Central Loss", category: "Human", confidence: "Strong", note: "Central field loss approximation." },
  { key: "night", label: "Night / Low Light", category: "Human", confidence: "Estimated", note: "Low-light viewing approximation." },
  { key: "fatigue", label: "Fatigue-like", category: "Human", confidence: "Estimated", note: "Fatigue-related viewing softness approximation." },
  { key: "dry_eye", label: "Dry-eye-like", category: "Human", confidence: "Estimated", note: "Uneven blur and glare approximation." },
  { key: "dog", label: "Dog-like", category: "Animal", confidence: "Estimated", note: "Dog-like visible-range approximation based on commonly described canine characteristics." },
  { key: "cat", label: "Cat-like", category: "Animal", confidence: "Estimated", note: "Cat-like visible-range approximation based on commonly described feline characteristics." },
  { key: "bee", label: "Bee-like", category: "Animal", confidence: "Estimated", note: "Bee-like visible-range approximation based on commonly described bee characteristics. UV not included." },
  { key: "bird", label: "Bird-like", category: "Animal", confidence: "Estimated", note: "Bird-like visible-range approximation based on commonly described avian characteristics. UV not included." },
  { key: "age", label: "Age Profile", category: "Reference", confidence: "Reference", note: "Age-related viewing profile approximation." },
  { key: "sex", label: "Sex-difference Profile", category: "Reference", confidence: "Reference", note: "Average-profile reference mode." },
];
