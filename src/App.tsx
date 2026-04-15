import React, { useEffect, useMemo, useRef, useState } from "react";

type ModeCategory = "Human" | "Animal" | "Reference";
type Confidence = "Strong" | "Estimated" | "Reference";
type CompareMode = "slider" | "split" | "side-by-side";

type ModeDef = {
  key: string;
  label: string;
  category: ModeCategory;
  confidence: Confidence;
  note: string;
};

const MODES: ModeDef[] = [
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
  { key: "dog", label: "Dog", category: "Animal", confidence: "Estimated", note: "Dog-like visible-range approximation." },
  { key: "cat", label: "Cat", category: "Animal", confidence: "Estimated", note: "Cat-like visible-range approximation." },
  { key: "bee", label: "Bee", category: "Animal", confidence: "Estimated", note: "Bee-like visible-range approximation. UV not included." },
  { key: "bird", label: "Bird-like", category: "Animal", confidence: "Estimated", note: "Bird-like visible-range approximation. UV not included." },
  { key: "age", label: "Age Profile", category: "Reference", confidence: "Reference", note: "Age-related viewing profile approximation." },
  { key: "sex", label: "Sex-difference Profile", category: "Reference", confidence: "Reference", note: "Average-profile reference mode." },
];

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

          <section className="workspace-grid">
            <CompareStage
              originalUrl={originalUrl}
              transformedUrl={transformedUrl}
              compareMode={compareMode}
              setCompareMode={setCompareMode}
              divider={divider}
              setDivider={setDivider}
              isBusy={isBusy}
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
            />
          </section>

          <section className="category-grid">
            <CategoryPanel
              title="Human"
              subtitle="Visual conditions and perceptual differences."
              items={humanModes.map((mode) => mode.label)}
              icon={<EyeSketch className="mini-plate" />}
              onClick={() => setCategory("Human")}
            />
            <CategoryPanel
              title="Animal"
              subtitle="How other species may see the world."
              items={animalModes.map((mode) => mode.label)}
              icon={<BirdSketch className="mini-plate" />}
              onClick={() => setCategory("Animal")}
            />
            <CategoryPanel
              title="Reference"
              subtitle="Profiles based on research and averages."
              items={referenceModes.map((mode) => mode.label)}
              icon={<ChartSketch className="mini-plate" />}
              onClick={() => setCategory("Reference")}
            />
          </section>

          <footer className="footer-strip">
            <div className="footer-line" />
            <p>Approximations only. See Methodology and Limitations for details.</p>
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
      <div className="brand">AsSeenBy</div>
      <nav className="topnav">
        <a href="#">About</a>
        <a href="#">Modes</a>
        <a href="#">Methodology</a>
        <a href="#">Limitations</a>
      </nav>
      <button className="ghost-button">About this project</button>
    </header>
  );
}

function Hero() {
  return (
    <section className="hero-grid">
      <div>
        <h1 className="hero-title">
          See the same image through different <span>ways of seeing.</span>
        </h1>
      </div>

      <div className="hero-copy">
        <p>
          AsSeenBy is a research-based viewer that simulates how an image may appear under different visual conditions and in the eyes of other species.
          <span> Not a diagnostic tool—an instrument for understanding.</span>
        </p>
      </div>

      <div className="eye-plate-card">
        <div className="plate-title">Fig. I. The Human Eye</div>
        <div>
          <EyePlate className="plate-eye" />
        </div>
      </div>
    </section>
  );
}

function CompareStage({
  originalUrl,
  transformedUrl,
  compareMode,
  setCompareMode,
  divider,
  setDivider,
  isBusy,
}: {
  originalUrl: string;
  transformedUrl: string;
  compareMode: CompareMode;
  setCompareMode: (mode: CompareMode) => void;
  divider: number;
  setDivider: (value: number) => void;
  isBusy: boolean;
}) {
  const effectiveDivider = compareMode === "split" ? 50 : divider;
  const isInteractiveSlider = compareMode === "slider";
  const toolbarNote = compareMode === "slider"
    ? "Move the balance control to compare"
    : compareMode === "split"
      ? "Fixed 50 / 50 midpoint comparison"
      : "Original and transformed shown together";

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
              <img
                src={transformedUrl}
                alt="Simulated"
                className="compare-image"
                style={{ width: `${100 / (effectiveDivider / 100)}%`, maxWidth: "none" }}
              />
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

function ControlRail({ category, setCategory, categoryModes, modeKey, setModeKey, strength, setStrength, currentMode, onUploadClick, onUseSample, error }: {
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
}) {
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
  const transformedCtx = transformedCanvas.getContext("2d");
  if (!transformedCtx) throw new Error("Canvas is not available.");
  transformedCtx.drawImage(baseCanvas, 0, 0);

  applyTransform(baseCanvas, transformedCanvas, modeKey, amount);

  return {
    originalUrl: baseCanvas.toDataURL("image/jpeg", 0.94),
    transformedUrl: transformedCanvas.toDataURL("image/jpeg", 0.94),
  };
}

function applyTransform(baseCanvas: HTMLCanvasElement, outCanvas: HTMLCanvasElement, modeKey: string, amount: number) {
  const width = baseCanvas.width;
  const height = baseCanvas.height;
  const ctx = outCanvas.getContext("2d");
  if (!ctx) return;

  if (modeKey === "blur") {
    const blurCanvas = document.createElement("canvas");
    blurCanvas.width = width;
    blurCanvas.height = height;
    const blurCtx = blurCanvas.getContext("2d");
    if (!blurCtx) return;
    blurCtx.filter = `blur(${1 + amount * 8}px)`;
    blurCtx.drawImage(baseCanvas, 0, 0);
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(blurCanvas, 0, 0);
    return;
  }

  ctx.clearRect(0, 0, width, height);
  ctx.drawImage(baseCanvas, 0, 0);

  if (modeKey === "tunnel") {
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.max(width, height) * (0.6 - amount * 0.26);
    const outer = Math.max(width, height) * 0.9;
    const gradient = ctx.createRadialGradient(cx, cy, radius, cx, cy, outer);
    gradient.addColorStop(0, "rgba(0,0,0,0)");
    gradient.addColorStop(0.75, `rgba(28,22,18,${0.1 + amount * 0.2})`);
    gradient.addColorStop(1, `rgba(18,14,12,${0.55 + amount * 0.28})`);
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    return;
  }

  if (modeKey === "central_loss") {
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) * (0.08 + amount * 0.14);
    const gradient = ctx.createRadialGradient(cx, cy, radius * 0.15, cx, cy, radius);
    gradient.addColorStop(0, `rgba(38,33,30,${0.55 + amount * 0.25})`);
    gradient.addColorStop(0.6, `rgba(75,66,58,${0.32 + amount * 0.12})`);
    gradient.addColorStop(1, "rgba(75,66,58,0)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    return;
  }

  if (modeKey === "cataract") {
    const hazeCanvas = document.createElement("canvas");
    hazeCanvas.width = width;
    hazeCanvas.height = height;
    const hazeCtx = hazeCanvas.getContext("2d");
    if (!hazeCtx) return;
    hazeCtx.filter = `blur(${1 + amount * 4}px)`;
    hazeCtx.drawImage(baseCanvas, 0, 0);
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(hazeCanvas, 0, 0);
    ctx.fillStyle = `rgba(255,245,220,${0.1 + amount * 0.18})`;
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = `rgba(201,170,100,${0.04 + amount * 0.08})`;
    ctx.fillRect(0, 0, width, height);
    const imageData = ctx.getImageData(0, 0, width, height);
    applyLowContrastToData(imageData.data, 0.18 + amount * 0.22);
    ctx.putImageData(imageData, 0, 0);
    return;
  }

  if (modeKey === "night") {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    for (let i = 0; i < data.length; i += 4) {
      let r = data[i] / 255;
      let g = data[i + 1] / 255;
      let b = data[i + 2] / 255;
      const luma = 0.2126 * r + 0.7152 * g + 0.0722 * b;
      const dark = 0.42 + amount * 0.35;
      r = mix(r, luma, 0.5 + amount * 0.35) * (1 - dark * 0.4);
      g = mix(g, luma, 0.45 + amount * 0.3) * (1 - dark * 0.28);
      b = mix(b, luma, 0.38 + amount * 0.25) * (1 - dark * 0.1);
      data[i] = clamp255(r * 255);
      data[i + 1] = clamp255(g * 255);
      data[i + 2] = clamp255(b * 255);
    }
    ctx.putImageData(imageData, 0, 0);
    return;
  }

  if (modeKey === "fatigue") {
    const fatigueCanvas = document.createElement("canvas");
    fatigueCanvas.width = width;
    fatigueCanvas.height = height;
    const fatigueCtx = fatigueCanvas.getContext("2d");
    if (!fatigueCtx) return;
    fatigueCtx.filter = `blur(${0.6 + amount * 3.2}px)`;
    fatigueCtx.drawImage(baseCanvas, 0, 0);
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(fatigueCanvas, 0, 0);
    const imageData = ctx.getImageData(0, 0, width, height);
    applyLowContrastToData(imageData.data, 0.08 + amount * 0.12);
    ctx.putImageData(imageData, 0, 0);
    return;
  }

  if (modeKey === "dry_eye") {
    const dryCanvas = document.createElement("canvas");
    dryCanvas.width = width;
    dryCanvas.height = height;
    const dryCtx = dryCanvas.getContext("2d");
    if (!dryCtx) return;
    dryCtx.filter = `blur(${0.4 + amount * 2.1}px)`;
    dryCtx.drawImage(baseCanvas, 0, 0);
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(dryCanvas, 0, 0);
    addDryEyeOverlay(ctx, width, height, amount);
    return;
  }

  const imageData = ctx.getImageData(0, 0, width, height);
  const data = imageData.data;

  if (modeKey === "low_contrast") {
    applyLowContrastToData(data, amount * 0.55);
  } else if (modeKey === "protan") {
    applyColorDeficiency(data, amount, [[0.567, 0.433, 0], [0.558, 0.442, 0], [0, 0.242, 0.758]]);
  } else if (modeKey === "deutan") {
    applyColorDeficiency(data, amount, [[0.625, 0.375, 0], [0.7, 0.3, 0], [0, 0.3, 0.7]]);
  } else if (modeKey === "tritan") {
    applyColorDeficiency(data, amount, [[0.95, 0.05, 0], [0, 0.433, 0.567], [0, 0.475, 0.525]]);
  } else if (modeKey === "dog") {
    applyColorDeficiency(data, amount * 0.85, [[0.62, 0.38, 0], [0.22, 0.78, 0], [0, 0.32, 0.68]]);
    applyLowContrastToData(data, amount * 0.12);
  } else if (modeKey === "cat") {
    applyColorDeficiency(data, amount * 0.7, [[0.7, 0.3, 0], [0.25, 0.75, 0], [0.05, 0.25, 0.7]]);
    desaturateData(data, 0.14 + amount * 0.12);
  } else if (modeKey === "bee") {
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const nr = mix(r, g * 0.55, amount * 0.7);
      const ng = mix(g, clamp255(g * 1.06 + b * 0.06), amount * 0.4);
      const nb = mix(b, clamp255(b * 1.12 + g * 0.08), amount * 0.45);
      data[i] = clamp255(nr);
      data[i + 1] = clamp255(ng);
      data[i + 2] = clamp255(nb);
    }
  } else if (modeKey === "bird") {
    saturateData(data, 0.08 + amount * 0.18);
    boostMicroContrast(data, 0.02 + amount * 0.05);
  } else if (modeKey === "age") {
    applyLowContrastToData(data, 0.12 + amount * 0.16);
    warmTintData(data, 0.04 + amount * 0.08);
  } else if (modeKey === "sex") {
    saturateData(data, amount * 0.04);
    boostMicroContrast(data, amount * 0.015);
  }

  ctx.putImageData(imageData, 0, 0);

  if (modeKey === "dog" || modeKey === "cat") {
    const softCanvas = document.createElement("canvas");
    softCanvas.width = width;
    softCanvas.height = height;
    const softCtx = softCanvas.getContext("2d");
    if (!softCtx) return;
    softCtx.filter = `blur(${0.6 + amount * 2}px)`;
    softCtx.drawImage(outCanvas, 0, 0);
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(softCanvas, 0, 0);
  }
}

function applyColorDeficiency(data: Uint8ClampedArray, amount: number, matrix: number[][]) {
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const tr = clamp255(r * matrix[0][0] + g * matrix[0][1] + b * matrix[0][2]);
    const tg = clamp255(r * matrix[1][0] + g * matrix[1][1] + b * matrix[1][2]);
    const tb = clamp255(r * matrix[2][0] + g * matrix[2][1] + b * matrix[2][2]);
    data[i] = clamp255(mix(r, tr, amount));
    data[i + 1] = clamp255(mix(g, tg, amount));
    data[i + 2] = clamp255(mix(b, tb, amount));
  }
}

function applyLowContrastToData(data: Uint8ClampedArray, amount: number) {
  const midpoint = 127.5;
  const factor = 1 - amount;
  for (let i = 0; i < data.length; i += 4) {
    data[i] = clamp255(midpoint + (data[i] - midpoint) * factor);
    data[i + 1] = clamp255(midpoint + (data[i + 1] - midpoint) * factor);
    data[i + 2] = clamp255(midpoint + (data[i + 2] - midpoint) * factor);
  }
}

function desaturateData(data: Uint8ClampedArray, amount: number) {
  for (let i = 0; i < data.length; i += 4) {
    const luma = 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
    data[i] = clamp255(mix(data[i], luma, amount));
    data[i + 1] = clamp255(mix(data[i + 1], luma, amount));
    data[i + 2] = clamp255(mix(data[i + 2], luma, amount));
  }
}

function saturateData(data: Uint8ClampedArray, amount: number) {
  for (let i = 0; i < data.length; i += 4) {
    const luma = 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
    data[i] = clamp255(mix(luma, data[i], 1 + amount));
    data[i + 1] = clamp255(mix(luma, data[i + 1], 1 + amount));
    data[i + 2] = clamp255(mix(luma, data[i + 2], 1 + amount));
  }
}

function warmTintData(data: Uint8ClampedArray, amount: number) {
  for (let i = 0; i < data.length; i += 4) {
    data[i] = clamp255(data[i] + 255 * amount * 0.45);
    data[i + 1] = clamp255(data[i + 1] + 255 * amount * 0.18);
    data[i + 2] = clamp255(data[i + 2] - 255 * amount * 0.12);
  }
}

function boostMicroContrast(data: Uint8ClampedArray, amount: number) {
  if (amount <= 0) return;
  for (let i = 0; i < data.length; i += 4) {
    data[i] = clamp255(data[i] + (data[i] - 127.5) * amount);
    data[i + 1] = clamp255(data[i + 1] + (data[i + 1] - 127.5) * amount);
    data[i + 2] = clamp255(data[i + 2] + (data[i + 2] - 127.5) * amount);
  }
}

function addDryEyeOverlay(ctx: CanvasRenderingContext2D, width: number, height: number, amount: number) {
  const spots = 6;
  for (let i = 0; i < spots; i += 1) {
    const x = width * ((i * 0.17 + 0.12) % 1);
    const y = height * ((i * 0.21 + 0.18) % 1);
    const radius = Math.min(width, height) * (0.06 + 0.03 * i * amount);
    const gradient = ctx.createRadialGradient(x, y, radius * 0.2, x, y, radius);
    gradient.addColorStop(0, `rgba(255,250,235,${0.08 + amount * 0.12})`);
    gradient.addColorStop(1, "rgba(255,250,235,0)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
  }
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

function mix(a: number, b: number, amount: number) {
  return a + (b - a) * amount;
}

function clamp255(value: number) {
  return Math.max(0, Math.min(255, value));
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
