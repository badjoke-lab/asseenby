type Matrix3x3 = [
  [number, number, number],
  [number, number, number],
  [number, number, number],
];

type CvdModeKey = "protan" | "deutan" | "tritan";

// Machado, Oliveira & Fernandes pre-computed CVD matrices at severity
// 0.0..1.0 in 0.1 steps. Intermediate Strength values interpolate between
// neighboring matrices before the transform is applied to linear RGB.
const MACHADO_CVD_MATRICES: Record<CvdModeKey, Matrix3x3[]> = {
  protan: [
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    [[0.856167, 0.182038, -0.038205], [0.029342, 0.955115, 0.015544], [-0.00288, -0.001563, 1.004443]],
    [[0.734766, 0.334872, -0.069637], [0.05184, 0.919198, 0.028963], [-0.004928, -0.004209, 1.009137]],
    [[0.630323, 0.465641, -0.095964], [0.069181, 0.890046, 0.040773], [-0.006308, -0.007724, 1.014032]],
    [[0.539009, 0.579343, -0.118352], [0.082546, 0.866121, 0.051332], [-0.007136, -0.011959, 1.019095]],
    [[0.458064, 0.679578, -0.137642], [0.092785, 0.846313, 0.060902], [-0.007494, -0.016807, 1.024301]],
    [[0.38545, 0.769005, -0.154455], [0.100526, 0.829802, 0.069673], [-0.007442, -0.02219, 1.029632]],
    [[0.319627, 0.849633, -0.169261], [0.106241, 0.815969, 0.07779], [-0.007025, -0.028051, 1.035076]],
    [[0.259411, 0.923008, -0.18242], [0.110296, 0.80434, 0.085364], [-0.006276, -0.034346, 1.040622]],
    [[0.203876, 0.990338, -0.194214], [0.112975, 0.794542, 0.092483], [-0.005222, -0.041043, 1.046265]],
    [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
  ],
  deutan: [
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    [[0.866435, 0.177704, -0.044139], [0.049567, 0.939063, 0.01137], [-0.003453, 0.007233, 0.99622]],
    [[0.760729, 0.319078, -0.079807], [0.090568, 0.889315, 0.020117], [-0.006027, 0.013325, 0.992702]],
    [[0.675425, 0.43385, -0.109275], [0.125303, 0.847755, 0.026942], [-0.00795, 0.018572, 0.989378]],
    [[0.605511, 0.52856, -0.134071], [0.155318, 0.812366, 0.032316], [-0.009376, 0.023176, 0.9862]],
    [[0.547494, 0.607765, -0.155259], [0.181692, 0.781742, 0.036566], [-0.01041, 0.027275, 0.983136]],
    [[0.498864, 0.674741, -0.173604], [0.205199, 0.754872, 0.039929], [-0.011131, 0.030969, 0.980162]],
    [[0.457771, 0.731899, -0.18967], [0.226409, 0.731012, 0.042579], [-0.011595, 0.034333, 0.977261]],
    [[0.422823, 0.781057, -0.203881], [0.245752, 0.709602, 0.044646], [-0.011843, 0.037423, 0.974421]],
    [[0.392952, 0.82361, -0.216562], [0.263559, 0.69021, 0.046232], [-0.01191, 0.040281, 0.97163]],
    [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.01182, 0.04294, 0.968881]],
  ],
  tritan: [
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    [[0.92667, 0.092514, -0.019184], [0.021191, 0.964503, 0.014306], [0.008437, 0.054813, 0.93675]],
    [[0.89572, 0.13333, -0.02905], [0.029997, 0.9454, 0.024603], [0.013027, 0.104707, 0.882266]],
    [[0.905871, 0.127791, -0.033662], [0.026856, 0.941251, 0.031893], [0.01341, 0.148296, 0.838294]],
    [[0.948035, 0.08949, -0.037526], [0.014364, 0.946792, 0.038844], [0.010853, 0.193991, 0.795156]],
    [[1.017277, 0.027029, -0.044306], [-0.006113, 0.958479, 0.047634], [0.006379, 0.248708, 0.744913]],
    [[1.104996, -0.046633, -0.058363], [-0.032137, 0.971635, 0.060503], [0.001336, 0.317922, 0.680742]],
    [[1.193214, -0.109812, -0.083402], [-0.058496, 0.97941, 0.079086], [-0.002346, 0.403492, 0.598854]],
    [[1.257728, -0.139648, -0.118081], [-0.078003, 0.975409, 0.102594], [-0.003316, 0.501214, 0.502102]],
    [[1.278864, -0.125333, -0.153531], [-0.084748, 0.957674, 0.127074], [-0.000989, 0.601151, 0.399838]],
    [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.3039]],
  ],
};

const DOG_BASE_DEUTAN_MATRIX: Matrix3x3 = MACHADO_CVD_MATRICES.deutan[10];

export function applyTransform(
  baseCanvas: HTMLCanvasElement,
  outCanvas: HTMLCanvasElement,
  modeKey: string,
  amount: number,
) {
  const width = baseCanvas.width;
  const height = baseCanvas.height;
  const ctx = outCanvas.getContext("2d");
  if (!ctx) return;

  drawBase(ctx, baseCanvas, width, height);

  if (modeKey === "blur") {
    renderBlurred(ctx, baseCanvas, width, height, amount * 9);
    return;
  }

  if (modeKey === "tunnel") {
    const edgeMask = createMaskCanvas(width, height, 0.44 - amount * 0.14, 0.84 - amount * 0.05, false);
    const edgeBlur = blurCanvas(baseCanvas, amount * 8.2);
    const edgeGray = grayscaleCanvas(baseCanvas);
    overlayMaskedCanvas(ctx, edgeBlur, edgeMask, amount * 0.74);
    overlayMaskedCanvas(ctx, edgeGray, edgeMask, amount * 0.18);
    addTunnelMask(ctx, width, height, amount);
    return;
  }

  if (modeKey === "central_loss") {
    const centerMask = createMaskCanvas(width, height, 0.02 + amount * 0.03, 0.1 + amount * 0.16, true);
    const centerBlur = blurCanvas(baseCanvas, amount * 9.6);
    const centerGray = grayscaleCanvas(baseCanvas);
    overlayMaskedCanvas(ctx, centerBlur, centerMask, amount * 0.82);
    overlayMaskedCanvas(ctx, centerGray, centerMask, amount * 0.2);
    addCentralLossMask(ctx, width, height, amount);
    return;
  }

  if (modeKey === "cataract") {
    renderBlurred(ctx, baseCanvas, width, height, amount * 7.2);
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    applyLowContrastToData(data, amount * 0.56);
    desaturateData(data, amount * 0.2);
    warmTintData(data, amount * 0.2);
    softenHighlights(data, 0.74, amount * 0.36);
    ctx.putImageData(imageData, 0, 0);
    drawWarmVeil(ctx, width, height, amount * 0.2);
    const edgeMask = createMaskCanvas(width, height, 0.58, 0.94, false);
    overlayMaskedCanvas(ctx, blurCanvas(baseCanvas, amount * 5.6), edgeMask, amount * 0.14);
    drawHighlightBloom(ctx, baseCanvas, 172, amount * 26, amount * 0.38, 0.38);
    return;
  }




  const imageData = ctx.getImageData(0, 0, width, height);
  const data = imageData.data;

  if (modeKey === "low_contrast") {
    applyLowContrastToData(data, amount * 0.58);
    desaturateData(data, amount * 0.11);
    softenHighlights(data, 0.82, amount * 0.14);
  } else if (isCvdMode(modeKey)) {
    applyMachadoCvd(data, modeKey, amount);
  } else if (modeKey === "dog") {
    const severity = curveAmount(amount, 1.08);
    // Human-display proxy: canine behavioral work supports a dichromatic pattern
    // broadly similar to human red-green deficiency, but this is not a canine
    // cone-catch reconstruction. Keep the chromatic and acuity changes restrained.
    applyColorMatrixLinear(data, severity * 0.82, DOG_BASE_DEUTAN_MATRIX, 0.34);
    compressRedGreenAxis(data, severity * 0.18);
    applyLowContrastToData(data, severity * 0.11);
  }

  ctx.putImageData(imageData, 0, 0);

  if (modeKey === "dog") {
    mixBlurredCopy(ctx, outCanvas, width, height, amount * 1.8, 0.52);
  }
}

function drawBase(ctx: CanvasRenderingContext2D, source: HTMLCanvasElement, width: number, height: number) {
  ctx.clearRect(0, 0, width, height);
  ctx.globalCompositeOperation = "source-over";
  ctx.globalAlpha = 1;
  ctx.drawImage(source, 0, 0, width, height);
}

function renderBlurred(ctx: CanvasRenderingContext2D, source: HTMLCanvasElement, width: number, height: number, blurPx: number) {
  const blurred = blurCanvas(source, blurPx);
  ctx.clearRect(0, 0, width, height);
  ctx.drawImage(blurred, 0, 0);
}

function mixBlurredCopy(ctx: CanvasRenderingContext2D, source: HTMLCanvasElement, width: number, height: number, blurPx: number, alpha: number) {
  const blurred = blurCanvas(source, blurPx);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.drawImage(blurred, 0, 0, width, height);
  ctx.restore();
}

function overlayMaskedCanvas(
  ctx: CanvasRenderingContext2D,
  source: HTMLCanvasElement,
  mask: HTMLCanvasElement,
  alpha: number,
) {
  const masked = createCanvas(source.width, source.height);
  const maskedCtx = masked.getContext("2d");
  if (!maskedCtx) return;
  maskedCtx.drawImage(source, 0, 0);
  maskedCtx.globalCompositeOperation = "destination-in";
  maskedCtx.drawImage(mask, 0, 0);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.drawImage(masked, 0, 0);
  ctx.restore();
}

function createMaskCanvas(
  width: number,
  height: number,
  innerRatio: number,
  outerRatio: number,
  invert: boolean,
) {
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext("2d");
  if (!ctx) return canvas;
  const cx = width / 2;
  const cy = height / 2;
  const base = Math.min(width, height) * 0.5;
  const inner = Math.max(0, base * innerRatio);
  const outer = Math.max(inner + 1, base * outerRatio);
  const gradient = ctx.createRadialGradient(cx, cy, inner, cx, cy, outer);
  if (invert) {
    gradient.addColorStop(0, "rgba(0,0,0,1)");
    gradient.addColorStop(0.65, "rgba(0,0,0,1)");
    gradient.addColorStop(1, "rgba(0,0,0,0)");
  } else {
    gradient.addColorStop(0, "rgba(0,0,0,0)");
    gradient.addColorStop(0.65, "rgba(0,0,0,0)");
    gradient.addColorStop(1, "rgba(0,0,0,1)");
  }
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);
  return canvas;
}

function blurCanvas(source: HTMLCanvasElement, blurPx: number) {
  const canvas = createCanvas(source.width, source.height);
  const ctx = canvas.getContext("2d");
  if (!ctx) return canvas;
  ctx.filter = `blur(${blurPx}px)`;
  ctx.drawImage(source, 0, 0);
  ctx.filter = "none";
  return canvas;
}

function grayscaleCanvas(source: HTMLCanvasElement) {
  const canvas = createCanvas(source.width, source.height);
  const ctx = canvas.getContext("2d");
  if (!ctx) return canvas;
  ctx.drawImage(source, 0, 0);
  const imageData = ctx.getImageData(0, 0, source.width, source.height);
  const data = imageData.data;
  for (let i = 0; i < data.length; i += 4) {
    const luma = 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
    data[i] = luma;
    data[i + 1] = luma;
    data[i + 2] = luma;
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}

function drawHighlightBloom(
  ctx: CanvasRenderingContext2D,
  source: HTMLCanvasElement,
  threshold: number,
  blurPx: number,
  alpha: number,
  warmth: number,
) {
  const width = source.width;
  const height = source.height;
  const sourceCtx = source.getContext("2d");
  if (!sourceCtx) return;
  const bloomBase = createCanvas(width, height);
  const bloomCtx = bloomBase.getContext("2d");
  if (!bloomCtx) return;
  const imageData = sourceCtx.getImageData(0, 0, width, height);
  const data = imageData.data;
  for (let i = 0; i < data.length; i += 4) {
    const luma = 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
    const strength = clamp01((luma - threshold) / Math.max(1, 255 - threshold));
    if (strength <= 0) {
      data[i + 3] = 0;
      continue;
    }
    data[i] = clamp255(data[i] + 255 * warmth * 0.2 * strength);
    data[i + 1] = clamp255(data[i + 1] + 255 * warmth * 0.12 * strength);
    data[i + 2] = clamp255(data[i + 2] + 255 * warmth * 0.03 * strength);
    data[i + 3] = clamp255(255 * strength);
  }
  bloomCtx.putImageData(imageData, 0, 0);
  const blurred = blurCanvas(bloomBase, blurPx);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.globalCompositeOperation = "screen";
  ctx.drawImage(blurred, 0, 0);
  ctx.restore();
}

function drawWarmVeil(ctx: CanvasRenderingContext2D, width: number, height: number, alpha: number) {
  ctx.save();
  ctx.fillStyle = `rgba(255, 244, 224, ${alpha})`;
  ctx.fillRect(0, 0, width, height);
  ctx.restore();
}

function addTunnelMask(ctx: CanvasRenderingContext2D, width: number, height: number, amount: number) {
  const cx = width / 2;
  const cy = height / 2;
  const inner = Math.max(width, height) * (0.42 - amount * 0.16);
  const outer = Math.max(width, height) * 0.98;
  const gradient = ctx.createRadialGradient(cx, cy, inner, cx, cy, outer);
  gradient.addColorStop(0, "rgba(0,0,0,0)");
  gradient.addColorStop(0.7, `rgba(18,14,12,${amount * 0.2})`);
  gradient.addColorStop(1, `rgba(18,14,12,${amount * 0.82})`);
  ctx.save();
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);
  ctx.restore();
}

function addCentralLossMask(ctx: CanvasRenderingContext2D, width: number, height: number, amount: number) {
  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(width, height) * (0.08 + amount * 0.16);
  const gradient = ctx.createRadialGradient(cx, cy, radius * 0.18, cx, cy, radius);
  gradient.addColorStop(0, `rgba(42, 36, 32, ${amount * 0.8})`);
  gradient.addColorStop(0.45, `rgba(64, 56, 50, ${amount * 0.48})`);
  gradient.addColorStop(1, "rgba(64, 56, 50, 0)");
  ctx.save();
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);
  ctx.restore();
}

function isCvdMode(modeKey: string): modeKey is CvdModeKey {
  return modeKey === "protan" || modeKey === "deutan" || modeKey === "tritan";
}

function interpolateMachadoMatrix(modeKey: CvdModeKey, severity: number): Matrix3x3 {
  const scaled = clamp01(severity) * 10;
  const lowerIndex = Math.floor(scaled);
  const upperIndex = Math.min(10, lowerIndex + 1);
  const mixAmount = scaled - lowerIndex;
  const lower = MACHADO_CVD_MATRICES[modeKey][lowerIndex];
  const upper = MACHADO_CVD_MATRICES[modeKey][upperIndex];

  return lower.map((row, rowIndex) =>
    row.map((value, columnIndex) => mix(value, upper[rowIndex][columnIndex], mixAmount)),
  ) as Matrix3x3;
}

function applyMachadoCvd(data: Uint8ClampedArray, modeKey: CvdModeKey, severity: number) {
  const matrix = interpolateMachadoMatrix(modeKey, severity);
  for (let i = 0; i < data.length; i += 4) {
    const sr = srgbToLinear(data[i]);
    const sg = srgbToLinear(data[i + 1]);
    const sb = srgbToLinear(data[i + 2]);

    const tr = sr * matrix[0][0] + sg * matrix[0][1] + sb * matrix[0][2];
    const tg = sr * matrix[1][0] + sg * matrix[1][1] + sb * matrix[1][2];
    const tb = sr * matrix[2][0] + sg * matrix[2][1] + sb * matrix[2][2];

    data[i] = clamp255(linearToSrgb255(tr));
    data[i + 1] = clamp255(linearToSrgb255(tg));
    data[i + 2] = clamp255(linearToSrgb255(tb));
  }
}

function applyColorMatrixLinear(
  data: Uint8ClampedArray,
  amount: number,
  matrix: Matrix3x3,
  luminancePreserve: number,
) {
  for (let i = 0; i < data.length; i += 4) {
    const sr = srgbToLinear(data[i]);
    const sg = srgbToLinear(data[i + 1]);
    const sb = srgbToLinear(data[i + 2]);

    let tr = sr * matrix[0][0] + sg * matrix[0][1] + sb * matrix[0][2];
    let tg = sr * matrix[1][0] + sg * matrix[1][1] + sb * matrix[1][2];
    let tb = sr * matrix[2][0] + sg * matrix[2][1] + sb * matrix[2][2];

    const srcLuma = 0.2126 * sr + 0.7152 * sg + 0.0722 * sb;
    const dstLuma = 0.2126 * tr + 0.7152 * tg + 0.0722 * tb;
    const rebalance = dstLuma > 0.0001 ? srcLuma / dstLuma : 1;
    const preserve = 1 + (rebalance - 1) * luminancePreserve;

    tr *= preserve;
    tg *= preserve;
    tb *= preserve;

    data[i] = clamp255(mix(data[i], linearToSrgb255(tr), amount));
    data[i + 1] = clamp255(mix(data[i + 1], linearToSrgb255(tg), amount));
    data[i + 2] = clamp255(mix(data[i + 2], linearToSrgb255(tb), amount));
  }
}

function compressRedGreenAxis(data: Uint8ClampedArray, amount: number) {
  for (let i = 0; i < data.length; i += 4) {
    const mean = (data[i] + data[i + 1]) * 0.5;
    data[i] = clamp255(mix(data[i], mean, amount));
    data[i + 1] = clamp255(mix(data[i + 1], mean, amount));
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


function warmTintData(data: Uint8ClampedArray, amount: number) {
  for (let i = 0; i < data.length; i += 4) {
    data[i] = clamp255(data[i] + 255 * amount * 0.42);
    data[i + 1] = clamp255(data[i + 1] + 255 * amount * 0.16);
    data[i + 2] = clamp255(data[i + 2] - 255 * amount * 0.1);
  }
}

function softenHighlights(data: Uint8ClampedArray, threshold: number, amount: number) {
  const cutoff = threshold * 255;
  for (let i = 0; i < data.length; i += 4) {
    for (let c = 0; c < 3; c += 1) {
      const value = data[i + c];
      if (value <= cutoff) continue;
      const extra = value - cutoff;
      data[i + c] = clamp255(cutoff + extra * (1 - amount));
    }
  }
}



function srgbToLinear(value: number) {
  const normalized = value / 255;
  if (normalized <= 0.04045) return normalized / 12.92;
  return ((normalized + 0.055) / 1.055) ** 2.4;
}

function linearToSrgb255(value: number) {
  const clamped = clamp01(value);
  const encoded = clamped <= 0.0031308 ? clamped * 12.92 : 1.055 * clamped ** (1 / 2.4) - 0.055;
  return encoded * 255;
}

function curveAmount(value: number, power: number) {
  return clamp01(value) ** power;
}

function clamp01(value: number) {
  return Math.max(0, Math.min(1, value));
}

function mix(a: number, b: number, amount: number) {
  return a + (b - a) * amount;
}

function clamp255(value: number) {
  return Math.max(0, Math.min(255, value));
}

function createCanvas(width: number, height: number) {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  return canvas;
}
