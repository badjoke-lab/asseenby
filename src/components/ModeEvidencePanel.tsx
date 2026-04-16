import type { ReactNode } from "react";
import type { EvidenceLink, ModeEvidence } from "../evidenceTypes";
import type { Confidence, ModeDef } from "../modes";

export function ModeEvidencePanel({
  mode,
  evidence,
}: {
  mode: ModeDef;
  evidence: ModeEvidence;
}) {
  const visibleSupporting = evidence.supportingSources.slice(0, 3);
  const hiddenSupporting = evidence.supportingSources.slice(3);

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
        <div className="evidence-block__label">Supporting sources</div>
        {visibleSupporting.length > 0 ? (
          <div className="source-list">
            {visibleSupporting.map((source) => (
              <SourceLink key={source.url} source={source} />
            ))}
            {hiddenSupporting.length > 0 ? (
              <details className="source-details">
                <summary>All sources ({evidence.supportingSources.length})</summary>
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
      <span className="source-link__meta">{formatKind(source.kind)}</span>
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

function classScore(score: ModeEvidence["evidenceScore"]) {
  if (score === "A") return "evidence-badge evidence-badge--score-a";
  if (score === "B") return "evidence-badge evidence-badge--score-b";
  if (score === "C") return "evidence-badge evidence-badge--score-c";
  return "evidence-badge evidence-badge--score-d";
}

function formatKind(kind: string) {
  if (kind === "paper") return "Paper";
  if (kind === "organization") return "Organization";
  if (kind === "review") return "Review";
  return "Reference";
}
