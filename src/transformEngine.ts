type Matrix3x3 = [
  [number, number, number],
  [number, number, number],
  [number, number, number],
];

const PROTAN_MATRIX: Matrix3x3 = [
  [0.152286, 1.052583, -0.204868],
  [0.114503, 0.786281, 0.099216],
  [-0.003882, -0.048116, 1.051998],
];

const DEUTAN_MATRIX: Matrix3x3 = [
  [0.367322, 0.860646, -0.227968],
  [0.280085, 0.672501, 0.047413],
  [-0.01182, 0.04294, 0.968881],
];

const TRITAN_MATRIX: Matrix3x3 = [
  [1.255528, -0.076749, -0.178779],
  [-0.078411, 0.930809, 0.147602],
  [0.004733, 0.691367, 0.3039],
];

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
    renderBlurred(ctx, baseCanvas, width, height, 1 + amount * 8);
    return;
  }

  if (modeKey === "tunnel") {
    mixBlurredCopy(ctx, baseCanvas, width, height, 1.2 + amount * 2.2, 0.06 + amount * 0.1);
    addTunnelMask(ctx, width, height, amount);
    return;
  }

  if (modeKey === "central_loss") {
    mixBlurredCopy(ctx, baseCanvas, width, height, 0.8 + amount * 1.6, 0.05 + amount * 0.08);
    addCentralLossMask(ctx, width, height, amount);
    return;
  }

  if (modeKey === "cataract") {
    renderBlurred(ctx, baseCanvas, width, height, 1.4 + amount * 4.8);
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    applyLowContrastToData(data, 0.22 + amount * 0.32);
    desaturateData(data, 0.06 + amount * 0.1);
    warmTintData(data, 0.06 + amount * 0.12);
    ctx.putImageData(imageData, 0, 0);
    drawWarmVeil(ctx, width, height, 0.08 + amount * 0.1);
    drawHighlightBloom(ctx, baseCanvas, 176, 10 + amount * 14, 0.14 + amount * 0.2, 0.35);
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
    renderBlurred(ctx, baseCanvas, width, height, 0.6 + amount * 3.2);
    const imageData = ctx.getImageData(0, 0, width, height);
    applyLowContrastToData(imageData.data, 0.08 + amount * 0.12);
    ctx.putImageData(imageData, 0, 0);
    return;
  }

  if (modeKey === "dry_eye") {
    renderBlurred(ctx, baseCanvas, width, height, 0.4 + amount * 2.1);
    addDryEyeOverlay(ctx, width, height, amount);
    return;
  }

  const imageData = ctx.getImageData(0, 0, width, height);
  const data = imageData.data;

  if (modeKey === "low_contrast") {
    applyLowContrastToData(data, 0.22 + amount * 0.38);
    desaturateData(data, 0.03 + amount * 0.05);
  } else if (modeKey === "protan") {
    applyColorMatrixLinear(data, amount, PROTAN_MATRIX, 0.42);
  } else if (modeKey === "deutan") {
    applyColorMatrixLinear(data, amount, DEUTAN_MATRIX, 0.42);
  } else if (modeKey === "tritan") {
    applyColorMatrixLinear(data, amount, TRITAN_MATRIX, 0.36);
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
    mixBlurredCopy(ctx, outCanvas, width, height, 0.6 + amount * 2, 0.75);
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

function blurCanvas(source: HTMLCanvasElement, blurPx: number) {
  const canvas = document.createElement("canvas");
  canvas.width = source.width;
  canvas.height = source.height;
  const ctx = canvas.getContext("2d");
  if (!ctx) return canvas;
  ctx.filter = `blur(${blurPx}px)`;
  ctx.drawImage(source, 0, 0);
  ctx.filter = "none";
  return canvas;
}

function drawHighlightBloom(ctx: CanvasRenderingContext2D, source: HTMLCanvasElement, threshold: number, blurPx: number, alpha: number, warmth: number) {
  const width = source.width;
  const height = source.height;
  const sourceCtx = source.getContext("2d");
  if (!sourceCtx) return;
  const bloomBase = document.createElement("canvas");
  bloomBase.width = width;
  bloomBase.height = height;
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
  gradient.addColorStop(0.7, `rgba(18,14,12,${0.08 + amount * 0.12})`);
  gradient.addColorStop(1, `rgba(18,14,12,${0.58 + amount * 0.24})`);
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
  gradient.addColorStop(0, `rgba(42, 36, 32, ${0.62 + amount * 0.18})`);
  gradient.addColorStop(0.45, `rgba(64, 56, 50, ${0.34 + amount * 0.14})`);
  gradient.addColorStop(1, "rgba(64, 56, 50, 0)");
  ctx.save();
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);
  ctx.restore();
}

function applyColorMatrixLinear(data: Uint8ClampedArray, amount: number, matrix: Matrix3x3, luminancePreserve: number) {
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
    data[i] = clamp255(data[i] + 255 * amount * 0.42);
    data[i + 1] = clamp255(data[i + 1] + 255 * amount * 0.16);
    data[i + 2] = clamp255(data[i + 2] - 255 * amount * 0.1);
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

function clamp01(value: number) {
  return Math.max(0, Math.min(1, value));
}

function mix(a: number, b: number, amount: number) {
  return a + (b - a) * amount;
}

function clamp255(value: number) {
  return Math.max(0, Math.min(255, value));
}
