import React, { useEffect, useMemo, useRef, useState } from "react";
import { ModeEvidencePanel } from "./components/ModeEvidencePanel";
import { getModeEvidence } from "./modeEvidence";
import type { ModeEvidence } from "./evidenceTypes";
import { CompareMode, ModeCategory, ModeDef, MODES, Confidence } from "./modes";
import { applyTransform as applyImageTransform } from "./transformEngine";

type ControlRailProps = {
  category: ModeCategory;
  setCategory: (category: ModeCategory) => void;
  categoryModes: ModeDef[];
  modeKey: string;
  setModeKey: (modeKey: string) => void;
  strength: number;
  setStrength: (value: number) => void;
  currentMode: ModeDef;
  onUploadClick: () => void;
  onUseSample: () => void;
  error: string;
};

const SAMPLE_IMAGE = createSampleImage();

export default function App() {
  const [category, setCategory] = useState<ModeCategory>("Human");
  const [modeKey, setModeKey] = useState<string>("protan");
  const [strength, setStrength] = useState(65);
  const [compareMode, setCompareMode] = useState<CompareMode>("slider");
  const [divider, setDivider] = useState(52);
  const [imageSrc, setImageSrc] = useState<string>(SAMPLE_IMAGE);
  const [originalUrl, setOriginalUrl] = useState<string>(SAMPLE_IMAGE);
  const [transformedUrl, setTransformedUrl] = useState<string>(SAMPLE_IMAGE);
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const categoryModes = useMemo(() => MODES.filter((mode) => mode.category === category), [category]);
  const currentMode = useMemo(() => MODES.find((mode) => mode.key === modeKey) ?? MODES[0], [modeKey]);
  const currentModeEvidence = useMemo(() => getModeEvidence(modeKey), [modeKey]);

  useEffect(() => {
    if (!categoryModes.some((mode) => mode.key === modeKey)) {
      setModeKey(categoryModes[0]?.key ?? "protan");
    }
  }, [category, categoryModes, modeKey]);

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      setIsBusy(true);
      setError("");
      try {
        const result = await prepareImages(imageSrc, modeKey, strength / 100);
        if (cancelled) return;
        setOriginalUrl(result.originalUrl);
        setTransformedUrl(result.transformedUrl);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to render image.");
      } finally {
        if (!cancelled) setIsBusy(false);
      }
    };
    run();
    return () => {
      cancelled = true;
    };
  }, [imageSrc, modeKey, strength]);

  const humanModes = MODES.filter((mode) => mode.category === "Human");
  const animalModes = MODES.filter((mode) => mode.category === "Animal");
  const referenceModes = MODES.filter((mode) => mode.category === "Reference");

  return (
    <div className="page-shell">
      <div className="page-frame">
        <Header />
        <main className="content-area">
          <Hero />

          <section id="workspace" className="workspace-grid">
            <CompareStage
              originalUrl={originalUrl}
              transformedUrl={transformedUrl}
              compareMode={compareMode}
              setCompareMode={setCompareMode}
              divider={divider}
              setDivider={setDivider}
              isBusy={isBusy}
              currentMode={currentMode}
              currentModeEvidence={currentModeEvidence}
            />
            <ControlRail
              category={category}
              setCategory={setCategory}
              categoryModes={categoryModes}
              modeKey={modeKey}
              setModeKey={setModeKey}
              strength={strength}
              setStrength={setStrength}
              currentMode={currentMode}
              onUploadClick={() => fileInputRef.current?.click()}
              onUseSample={() => setImageSrc(SAMPLE_IMAGE)}
              error={error}
              currentModeEvidence={currentModeEvidence}
            />
          </section>

          <section id="modes" className="category-grid">
            <CategoryPanel title="Human" subtitle="Visual conditions and perceptual differences." items={humanModes.map((mode) => mode.label)} icon={<EyeSketch className="mini-plate" />} onClick={() => setCategory("Human")} />
            <CategoryPanel title="Animal" subtitle="How other species may see the world." items={animalModes.map((mode) => mode.label)} icon={<BirdSketch className="mini-plate" />} onClick={() => setCategory("Animal")} />
            <CategoryPanel title="Reference" subtitle="Profiles based on research and averages." items={referenceModes.map((mode) => mode.label)} icon={<ChartSketch className="mini-plate" />} onClick={() => setCategory("Reference")} />
          </section>

          <footer className="footer-strip">
            <div className="footer-line" />
            <p>Approximations only. See the mode notes and evidence panel for methodology and limitations.</p>
            <div className="footer-line" />
          </footer>
        </main>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden-input"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (!file) return;
          const reader = new FileReader();
          reader.onload = () => {
            if (typeof reader.result === "string") setImageSrc(reader.result);
          };
          reader.readAsDataURL(file);
          event.currentTarget.value = "";
        }}
      />
    </div>
  );
}

function Header() {
  return (
    <header className="topbar">
      <a href="#about" className="brand">AsSeenBy</a>
      <nav className="topnav">
        <a href="#about">About</a>
        <a href="#workspace">Compare</a>
        <a href="#modes">Modes</a>
      </nav>
      <a href="#workspace" className="ghost-button">Open viewer</a>
    </header>
  );
}

function Hero() {
  return (
    <section id="about" className="hero-grid">
      <div>
        <h1 className="hero-title">See the same image through different <span>ways of seeing.</span></h1>
      </div>
      <div className="hero-copy">
        <p>
          AsSeenBy is a research-based viewer that simulates how an image may appear under different visual conditions and in the eyes of other species.
          <span> Not a diagnostic tool—an instrument for understanding.</span>
        </p>
      </div>
      <div className="eye-plate-card">
        <div className="plate-title">Fig. I. The Human Eye</div>
        <div><EyePlate className="plate-eye" /></div>
      </div>
    </section>
  );
}

function CompareStage({ originalUrl, transformedUrl, compareMode, setCompareMode, divider, setDivider, isBusy, currentMode, currentModeEvidence }: {
  originalUrl: string;
  transformedUrl: string;
  compareMode: CompareMode;
  setCompareMode: (mode: CompareMode) => void;
  divider: number;
  setDivider: (value: number) => void;
  isBusy: boolean;
  currentMode: ModeDef;
  currentModeEvidence: ModeEvidence;
}) {
  const effectiveDivider = compareMode === "split" ? 50 : divider;
  const isInteractiveSlider = compareMode === "slider";
  const toolbarNote = compareMode === "slider"
    ? "Move the balance control to compare"
    : compareMode === "split"
      ? "Fixed 50 / 50 midpoint comparison"
      : "Original and transformed shown together";
  const compareGuidance = buildCompareGuidance(currentMode, currentModeEvidence);

  return (
    <section className="compare-card">
      <div className={compareMode === "side-by-side" ? "compare-stage compare-stage--side" : "compare-stage"}>
        {compareMode === "side-by-side" ? (
          <>
            <ImagePanel src={originalUrl} label="Original" />
            <ImagePanel src={transformedUrl} label="Simulated" borderLeft />
          </>
        ) : (
          <div className="compare-overlay">
            <img src={originalUrl} alt="Original" className="compare-image" />
            <div className="compare-overlay-layer" style={{ width: `${effectiveDivider}%` }}>
              <img src={transformedUrl} alt="Simulated" className="compare-image" style={{ width: `${100 / (effectiveDivider / 100)}%`, maxWidth: "none" }} />
            </div>
            <LabelPill className="image-label image-label--left">Original</LabelPill>
            <LabelPill className="image-label image-label--right">Simulated</LabelPill>
            <div className="divider-line" style={{ left: `${effectiveDivider}%` }} />
            {isInteractiveSlider ? <div className="divider-handle" style={{ left: `${effectiveDivider}%` }}>↔</div> : null}
            {isBusy ? <div className="loading-badge" /> : null}
          </div>
        )}
      </div>
      <div className="compare-toolbar">
        <div className="compare-toolbar-top">
          <div className="pill-row">
            <span className="toolbar-label">Compare</span>
            <ComparePill active={compareMode === "slider"} onClick={() => setCompareMode("slider")}>Slider</ComparePill>
            <ComparePill active={compareMode === "split"} onClick={() => setCompareMode("split")}>Split</ComparePill>
            <ComparePill active={compareMode === "side-by-side"} onClick={() => setCompareMode("side-by-side")}>Side by side</ComparePill>
          </div>
          <div className="toolbar-note">{toolbarNote}</div>
        </div>
        {isInteractiveSlider ? (
          <div className="balance-row">
            <span className="toolbar-label">Balance</span>
            <input type="range" min={20} max={80} value={divider} onChange={(event) => setDivider(Number(event.target.value))} />
            <span className="balance-value">{divider}%</span>
          </div>
        ) : null}
        {compareGuidance ? (
          <div className="compare-guidance">
            <div className="compare-guidance__label">Current mode notice</div>
            <p className="compare-guidance__text">{compareGuidance}</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function ImagePanel({ src, label, borderLeft = false }: { src: string; label: string; borderLeft?: boolean }) {
  return (
    <div className={["image-panel", borderLeft ? "image-panel--bordered" : ""].join(" ")}>
      <img src={src} alt={label} className="compare-image" />
      <LabelPill className={borderLeft ? "image-label image-label--right" : "image-label image-label--left"}>{label}</LabelPill>
    </div>
  );
}

function ControlRail({ category, setCategory, categoryModes, modeKey, setModeKey, strength, setStrength, currentMode, onUploadClick, onUseSample, error, currentModeEvidence }: ControlRailProps & { currentModeEvidence: ReturnType<typeof getModeEvidence> }) {
  return (
    <aside className="control-rail">
      <div className="control-block">
        <label className="control-label">Category</label>
        <SelectLike value={category} options={["Human", "Animal", "Reference"]} onChange={(value) => setCategory(value as ModeCategory)} />
      </div>
      <div className="control-block">
        <label className="control-label">Mode</label>
        <SelectLike value={modeKey} options={categoryModes.map((mode) => mode.key)} onChange={setModeKey} labels={Object.fromEntries(categoryModes.map((m) => [m.key, m.label]))} />
        <p className="control-note">{currentMode.note}</p>
      </div>
      <div className="control-block">
        <label className="control-label">Strength</label>
        <div className="strength-row">
          <input type="range" min={0} max={100} value={strength} onChange={(event) => setStrength(Number(event.target.value))} />
          <span>{strength}%</span>
        </div>
      </div>
      <div className="button-stack">
        <button className="primary-button" onClick={onUploadClick}>Upload image</button>
        <button className="secondary-button" onClick={onUseSample}>Use sample image</button>
      </div>
      <div className="class-box">
        <div className="class-row">
          <span className="control-label">Class</span>
          <span className={confidenceClassName(currentMode.confidence)}>{currentMode.confidence}</span>
        </div>
        <p className="control-note">Research-based approximation. Not a diagnostic tool.</p>
        {error ? <p className="error-text">{error}</p> : null}
      </div>
      <ModeEvidencePanel mode={currentMode} evidence={currentModeEvidence} />
    </aside>
  );
}

function CategoryPanel({ title, subtitle, items, icon, onClick }: { title: string; subtitle: string; items: string[]; icon: React.ReactNode; onClick: () => void; }) {
  return (
    <button onClick={onClick} className="category-card">
      <div className="category-top">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <div className="category-icon">{icon}</div>
      </div>
      <div className="category-rule" />
      <div className="category-items">
        {items.map((item) => <div key={item}>{item}</div>)}
      </div>
    </button>
  );
}

function SelectLike({ value, options, onChange, labels }: { value: string; options: string[]; onChange: (value: string) => void; labels?: Record<string, string>; }) {
  return (
    <select className="control-select" value={value} onChange={(event) => onChange(event.target.value)}>
      {options.map((option) => <option key={option} value={option}>{labels?.[option] ?? option}</option>)}
    </select>
  );
}

function ComparePill({ children, active, onClick }: { children: React.ReactNode; active?: boolean; onClick?: () => void; }) {
  return <button onClick={onClick} className={active ? "pill pill--active" : "pill"}>{children}</button>;
}

function LabelPill({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={className}>{children}</div>;
}

function confidenceClassName(confidence: Confidence) {
  if (confidence === "Strong") return "confidence confidence--strong";
  if (confidence === "Estimated") return "confidence confidence--estimated";
  return "confidence confidence--reference";
}

function buildCompareGuidance(mode: ModeDef, evidence: ModeEvidence) {
  if (mode.confidence === "Reference" && evidence.modelScore === "D") {
    return `${mode.label} is a weak reference profile. Read it as an averaged framing view, not as a truth about a whole population.`;
  }
  if (mode.confidence === "Reference") {
    return `${mode.label} is an averaged reference profile, not an individual simulation.`;
  }
  if (evidence.modelScore === "D") {
    return `${mode.label} is shown as a rough visual proxy only. The phenomenon may be supported, but the current transform is still very limited.`;
  }
  if (evidence.modelScore === "C") {
    return `${mode.label} expresses a tendency rather than a strong simulation. Use it as an explanatory comparison aid, not as an exact reproduction.`;
  }
  return "";
}

async function prepareImages(source: string, modeKey: string, amount: number) {
  const image = await loadImage(source);
  const { width, height } = fitWithin(image.width, image.height, 1400, 960);

  const baseCanvas = document.createElement("canvas");
  baseCanvas.width = width;
  baseCanvas.height = height;
  const baseCtx = baseCanvas.getContext("2d");
  if (!baseCtx) throw new Error("Canvas is not available.");
  baseCtx.drawImage(image, 0, 0, width, height);

  const transformedCanvas = document.createElement("canvas");
  transformedCanvas.width = width;
  transformedCanvas.height = height;
  applyImageTransform(baseCanvas, transformedCanvas, modeKey, amount);

  return {
    originalUrl: baseCanvas.toDataURL("image/jpeg", 0.94),
    transformedUrl: transformedCanvas.toDataURL("image/jpeg", 0.94),
  };
}

function fitWithin(width: number, height: number, maxWidth: number, maxHeight: number) {
  const ratio = Math.min(maxWidth / width, maxHeight / height, 1);
  return { width: Math.round(width * ratio), height: Math.round(height * ratio) };
}

function loadImage(src: string) {
  return new Promise<HTMLImageElement>((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error("Image could not be loaded."));
    img.src = src;
  });
}

function createSampleImage() {
  const svg = `
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900">
    <defs>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#d7d0c1" />
        <stop offset="38%" stop-color="#e0c993" />
        <stop offset="100%" stop-color="#6c8190" />
      </linearGradient>
      <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#6c8190" />
        <stop offset="100%" stop-color="#334754" />
      </linearGradient>
      <filter id="cloudBlur"><feGaussianBlur stdDeviation="22" /></filter>
      <filter id="soft"><feGaussianBlur stdDeviation="1.2" /></filter>
    </defs>
    <rect width="1440" height="900" fill="url(#sky)" />
    <g filter="url(#cloudBlur)" opacity="0.55">
      <ellipse cx="350" cy="170" rx="170" ry="70" fill="#f6edd8" />
      <ellipse cx="760" cy="140" rx="210" ry="80" fill="#f0e4c8" />
      <ellipse cx="1060" cy="210" rx="180" ry="70" fill="#f6eddc" />
    </g>
    <g opacity="0.18">
      <rect x="0" y="420" width="1440" height="120" fill="#b89756" />
    </g>
    <g fill="#8e7443" opacity="0.95">
      <rect x="270" y="270" width="24" height="310" />
      <polygon points="282,195 250,270 314,270" />
      <rect x="478" y="315" width="148" height="220" />
      <ellipse cx="552" cy="315" rx="72" ry="72" />
      <rect x="636" y="350" width="160" height="185" />
      <rect x="820" y="332" width="118" height="203" />
      <rect x="968" y="310" width="150" height="225" />
      <rect x="1135" y="345" width="92" height="190" />
      <rect x="1168" y="260" width="20" height="275" />
      <polygon points="1178,212 1148,260 1208,260" />
    </g>
    <g opacity="0.72">
      <ellipse cx="340" cy="355" rx="26" ry="170" fill="#c9ad67" />
      <ellipse cx="1175" cy="365" rx="24" ry="190" fill="#be9d5c" />
    </g>
    <g fill="#70593a" opacity="0.72" filter="url(#soft)">
      <rect x="240" y="520" width="950" height="24" />
      <rect x="405" y="450" width="32" height="160" />
      <rect x="420" y="450" width="7" height="150" />
      <rect x="1010" y="460" width="28" height="150" />
      <line x1="438" y1="458" x2="1020" y2="458" stroke="#775f3a" stroke-width="6" />
    </g>
    <rect y="590" width="1440" height="310" fill="url(#water)" />
    <g opacity="0.18">
      <path d="M0 660 C160 635, 310 690, 520 662 S980 622, 1440 670 L1440 900 L0 900 Z" fill="#f0d7a0" />
      <path d="M0 710 C140 682, 330 730, 610 695 S1090 675, 1440 722" fill="none" stroke="#f2dfb3" stroke-width="2" />
    </g>
    <g fill="#3d2f20">
      <ellipse cx="240" cy="710" rx="92" ry="26" />
      <path d="M158 704 C184 652, 274 652, 314 704" fill="#3d2f20" />
      <path d="M168 702 C208 676, 258 674, 300 702" fill="#53422d" />
      <ellipse cx="610" cy="750" rx="44" ry="14" />
      <path d="M575 745 C590 712, 623 712, 646 745" fill="#4c3b29" />
      <ellipse cx="1280" cy="700" rx="34" ry="12" />
      <path d="M1252 697 C1265 672, 1290 672, 1310 697" fill="#4c3b29" />
    </g>
    <g opacity="0.12">
      <rect x="0" y="0" width="1440" height="900" fill="#fff3d7" />
    </g>
  </svg>`;

  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function EyePlate({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 320 220" fill="none" className={className}>
      <path d="M24 114c34-42 80-66 136-66 55 0 102 24 136 66-34 42-81 66-136 66-56 0-102-24-136-66Z" stroke="currentColor" strokeWidth="2" />
      <ellipse cx="160" cy="114" rx="46" ry="48" stroke="currentColor" strokeWidth="2" />
      <circle cx="160" cy="114" r="19" fill="currentColor" fillOpacity="0.55" />
      <circle cx="167" cy="106" r="6" fill="#f7f3eb" fillOpacity="0.8" />
      <path d="M52 96c30-24 63-36 108-36 47 0 81 14 109 36" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" opacity="0.8" />
      <path d="M52 132c30 24 63 36 108 36 47 0 81-14 109-36" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" opacity="0.8" />
      <path d="M211 76h34" stroke="currentColor" strokeWidth="1.5" />
      <path d="M205 96h58" stroke="currentColor" strokeWidth="1.5" />
      <path d="M210 120h48" stroke="currentColor" strokeWidth="1.5" />
      <path d="M203 146h61" stroke="currentColor" strokeWidth="1.5" />
      <text x="250" y="79" fontSize="12" fill="currentColor">cor.</text>
      <text x="268" y="100" fontSize="12" fill="currentColor">pup.</text>
      <text x="263" y="124" fontSize="12" fill="currentColor">iris</text>
      <text x="270" y="149" fontSize="12" fill="currentColor">l.</text>
    </svg>
  );
}

function EyeSketch({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" fill="none" className={className}>
      <path d="M6 32c7-9 16-14 26-14s19 5 26 14c-7 9-16 14-26 14S13 41 6 32Z" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="32" cy="32" r="8" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="32" cy="32" r="3.5" fill="currentColor" />
    </svg>
  );
}

function BirdSketch({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" fill="none" className={className}>
      <path d="M13 42c6-13 13-19 23-20 11-1 18 5 18 14 0 8-6 14-14 15-10 2-19-2-27-9Z" stroke="currentColor" strokeWidth="1.6" />
      <path d="M36 24c3 3 5 7 5 12" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M23 47c3 3 5 7 6 11" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="42" cy="28" r="1.8" fill="currentColor" />
    </svg>
  );
}

function ChartSketch({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" fill="none" className={className}>
      <path d="M10 52h44" stroke="currentColor" strokeWidth="1.6" />
      <rect x="14" y="33" width="6" height="19" stroke="currentColor" strokeWidth="1.4" />
      <rect x="26" y="24" width="6" height="28" stroke="currentColor" strokeWidth="1.4" />
      <rect x="38" y="18" width="6" height="34" stroke="currentColor" strokeWidth="1.4" />
      <rect x="50" y="29" width="6" height="23" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}
