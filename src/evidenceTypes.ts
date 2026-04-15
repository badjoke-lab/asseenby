export type EvidenceScore = "A" | "B" | "C" | "D";
export type SourceKind = "paper" | "organization" | "review" | "reference";

export type EvidenceLink = {
  title: string;
  url: string;
  kind: SourceKind;
  note: string;
};

export type ModeEvidence = {
  summary: string;
  evidenceScore: EvidenceScore;
  modelScore: EvidenceScore;
  basisNote: string;
  modelNote: string;
  caveat?: string;
  primarySource?: EvidenceLink;
  supportingSources: EvidenceLink[];
  lastReviewed: string;
};
