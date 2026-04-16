import "../evidence.css";
import type { ReactNode } from "react";
import type { EvidenceLink, ModeEvidence, SourceKind } from "../evidenceTypes";
import type { Confidence, ModeDef } from "../modes";

const SOURCE_KIND_PRIORITY: Record<SourceKind, number> = {
  review: 0,
  paper: 1,
  organization: 2,
  reference: 3,
};

export function ModeEvidencePanel({
  mode,
  evidence,
}: {
  mode: ModeDef;
  evidence: ModeEvidence;
}) {
  const sortedSupporting = [...evidence.supportingSources].sort(compareSources);
  const visibleSupporting = sortedSupporting.slice(0, 3);
  const hiddenSupporting = sortedSupporting.slice(3);
  const readerNote = buildReaderNote(mode.confidence, evidence.modelScore);

  return (
    <section className="evidence-card">
      <div className="evidence-card__header">
        <div>
          <div className="control-label">Mode profile</div>
          <h3 className="evidence-card__title">{mode.label}</h3>
        </div>
        <div className="evidence-badge-row">
          <Badge className={classConfidence(mode.confidence)}>Class {mode.confidence}</Badge>
          <Badge className={classScore(evidence.evidenceScore)}>Evidence {evidence.evidenceScore}</Badge>
          <Badge className={classScore(evidence.modelScore)}>Model {evidence.modelScore}</Badge>
        </div>
      </div>

      <p className="evidence-summary">{evidence.summary}</p>

      {readerNote ? (
        <div className="evidence-reader-note">
          <div className="evidence-reader-note__label">How to read this mode</div>
          <p className="evidence-reader-note__text">{readerNote}</p>
        </div>
      ) : null}

      {evidence.caveat ? (
        <div className="evidence-block">
          <div className="evidence-block__label">Caveat</div>
          <p className="evidence-block__text">{evidence.caveat}</p>
        </div>
      ) : null}

      <div className="evidence-block">
        <div className="evidence-block__label">Basis</div>
        <p className="evidence-block__text">{evidence.basisNote}</p>
      </div>

      <div className="evidence-block">
        <div className="evidence-block__label">Current model</div>
        <p className="evidence-block__text">{evidence.modelNote}</p>
      </div>

      <div className="evidence-block">
        <div className="evidence-block__label">Primary source</div>
        {evidence.primarySource ? (
          <SourceLink source={evidence.primarySource} />
        ) : (
          <p className="evidence-block__text">Source review pending.</p>
        )}
      </div>

      <div className="evidence-block">
        <div className="evidence-block__label">Supporting sources ({sortedSupporting.length})</div>
        {visibleSupporting.length > 0 ? (
          <div className="source-list">
            {visibleSupporting.map((source) => (
              <SourceLink key={source.url} source={source} />
            ))}
            {hiddenSupporting.length > 0 ? (
              <details className="source-details">
                <summary>More sources ({hiddenSupporting.length})</summary>
                <div className="source-list source-list--nested">
                  {hiddenSupporting.map((source) => (
                    <SourceLink key={source.url} source={source} />
                  ))}
                </div>
              </details>
            ) : null}
          </div>
        ) : (
          <p className="evidence-block__text">No supporting sources added yet.</p>
        )}
      </div>

      <div className="evidence-reviewed">Last reviewed: {evidence.lastReviewed}</div>
    </section>
  );
}

function SourceLink({ source }: { source: EvidenceLink }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noreferrer"
      className="source-link"
    >
      <span className="source-link__title">{source.title}</span>
      <span className="source-link__meta-row">
        <span className="source-link__kind">{formatKind(source.kind)}</span>
        <span className="source-link__domain">{formatHost(source.url)}</span>
      </span>
      <span className="source-link__note">{source.note}</span>
    </a>
  );
}

function Badge({ children, className }: { children: ReactNode; className: string }) {
  return <span className={className}>{children}</span>;
}

function classConfidence(confidence: Confidence) {
  if (confidence === "Strong") return "evidence-badge evidence-badge--strong";
  if (confidence === "Estimated") return "evidence-badge evidence-badge--estimated";
  return "evidence-badge evidence-badge--reference";
}

function classScore(score: ModeEvidence["evidenceScore"] | ModeEvidence["modelScore"]) {
  if (score === "A") return "evidence-badge evidence-badge--score-a";
  if (score === "B") return "evidence-badge evidence-badge--score-b";
  if (score === "C") return "evidence-badge evidence-badge--score-c";
  return "evidence-badge evidence-badge--score-d";
}

function buildReaderNote(confidence: Confidence, modelScore: ModeEvidence["modelScore"]) {
  if (confidence === "Reference" && modelScore === "D") {
    return "This is an averaged framing device with a very weak implementation claim. Read it as a cautious reference view, not as a population truth.";
  }
  if (confidence === "Reference") {
    return "This is an averaged framing device rather than an individual simulation. Use it to compare tendencies, not to infer what a specific person sees.";
  }
  if (modelScore === "D") {
    return "The underlying phenomenon may be well supported, but the current image transform is still very limited. Treat this as a rough visual proxy only.";
  }
  if (modelScore === "C") {
    return "The current transform expresses a tendency rather than a strong simulation. Use it as an explanatory aid, not as an exact reproduction.";
  }
  return "";
}

function compareSources(a: EvidenceLink, b: EvidenceLink) {
  const byKind = SOURCE_KIND_PRIORITY[a.kind] - SOURCE_KIND_PRIORITY[b.kind];
  if (byKind !== 0) return byKind;
  return a.title.localeCompare(b.title);
}

function formatKind(kind: SourceKind) {
  if (kind === "review") return "Review";
  if (kind === "paper") return "Paper";
  if (kind === "organization") return "Organization";
  return "Reference";
}

function formatHost(url: string) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "source";
  }
}
