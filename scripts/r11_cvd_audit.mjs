import { chromium } from "playwright";
import fs from "node:fs/promises";

const BASE = process.env.ASSEENBY_AUDIT_URL || "http://127.0.0.1:4173";
const modes = ["protan", "deutan", "tritan"];
const strengths = [10, 15, 40, 70, 100];
const colors = [
  [220, 30, 30], [30, 200, 60], [30, 70, 220], [230, 210, 30],
  [30, 200, 210], [210, 30, 210], [240, 130, 30], [120, 70, 180],
  [70, 150, 120], [180, 120, 90], [128, 128, 128], [235, 235, 235],
];

const matrices = {
  protan: [
    [[1,0,0],[0,1,0],[0,0,1]],
    [[0.856167,0.182038,-0.038205],[0.029342,0.955115,0.015544],[-0.00288,-0.001563,1.004443]],
    [[0.734766,0.334872,-0.069637],[0.05184,0.919198,0.028963],[-0.004928,-0.004209,1.009137]],
    [[0.630323,0.465641,-0.095964],[0.069181,0.890046,0.040773],[-0.006308,-0.007724,1.014032]],
    [[0.539009,0.579343,-0.118352],[0.082546,0.866121,0.051332],[-0.007136,-0.011959,1.019095]],
    [[0.458064,0.679578,-0.137642],[0.092785,0.846313,0.060902],[-0.007494,-0.016807,1.024301]],
    [[0.38545,0.769005,-0.154455],[0.100526,0.829802,0.069673],[-0.007442,-0.02219,1.029632]],
    [[0.319627,0.849633,-0.169261],[0.106241,0.815969,0.07779],[-0.007025,-0.028051,1.035076]],
    [[0.259411,0.923008,-0.18242],[0.110296,0.80434,0.085364],[-0.006276,-0.034346,1.040622]],
    [[0.203876,0.990338,-0.194214],[0.112975,0.794542,0.092483],[-0.005222,-0.041043,1.046265]],
    [[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
  ],
  deutan: [
    [[1,0,0],[0,1,0],[0,0,1]],
    [[0.866435,0.177704,-0.044139],[0.049567,0.939063,0.01137],[-0.003453,0.007233,0.99622]],
    [[0.760729,0.319078,-0.079807],[0.090568,0.889315,0.020117],[-0.006027,0.013325,0.992702]],
    [[0.675425,0.43385,-0.109275],[0.125303,0.847755,0.026942],[-0.00795,0.018572,0.989378]],
    [[0.605511,0.52856,-0.134071],[0.155318,0.812366,0.032316],[-0.009376,0.023176,0.9862]],
    [[0.547494,0.607765,-0.155259],[0.181692,0.781742,0.036566],[-0.01041,0.027275,0.983136]],
    [[0.498864,0.674741,-0.173604],[0.205199,0.754872,0.039929],[-0.011131,0.030969,0.980162]],
    [[0.457771,0.731899,-0.18967],[0.226409,0.731012,0.042579],[-0.011595,0.034333,0.977261]],
    [[0.422823,0.781057,-0.203881],[0.245752,0.709602,0.044646],[-0.011843,0.037423,0.974421]],
    [[0.392952,0.82361,-0.216562],[0.263559,0.69021,0.046232],[-0.01191,0.040281,0.97163]],
    [[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.01182,0.04294,0.968881]],
  ],
  tritan: [
    [[1,0,0],[0,1,0],[0,0,1]],
    [[0.92667,0.092514,-0.019184],[0.021191,0.964503,0.014306],[0.008437,0.054813,0.93675]],
    [[0.89572,0.13333,-0.02905],[0.029997,0.9454,0.024603],[0.013027,0.104707,0.882266]],
    [[0.905871,0.127791,-0.033662],[0.026856,0.941251,0.031893],[0.01341,0.148296,0.838294]],
    [[0.948035,0.08949,-0.037526],[0.014364,0.946792,0.038844],[0.010853,0.193991,0.795156]],
    [[1.017277,0.027029,-0.044306],[-0.006113,0.958479,0.047634],[0.006379,0.248708,0.744913]],
    [[1.104996,-0.046633,-0.058363],[-0.032137,0.971635,0.060503],[0.001336,0.317922,0.680742]],
    [[1.193214,-0.109812,-0.083402],[-0.058496,0.97941,0.079086],[-0.002346,0.403492,0.598854]],
    [[1.257728,-0.139648,-0.118081],[-0.078003,0.975409,0.102594],[-0.003316,0.501214,0.502102]],
    [[1.278864,-0.125333,-0.153531],[-0.084748,0.957674,0.127074],[-0.000989,0.601151,0.399838]],
    [[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.3039]],
  ],
};

function mix(a, b, t) { return a + (b - a) * t; }
function clamp01(v) { return Math.max(0, Math.min(1, v)); }
function srgbToLinearByte(v) {
  const n = v / 255;
  return n <= 0.04045 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
}
function linearToSrgbByte(v) {
  const n = clamp01(v);
  const e = n <= 0.0031308 ? n * 12.92 : 1.055 * n ** (1 / 2.4) - 0.055;
  return Math.max(0, Math.min(255, Math.round(e * 255)));
}
function matrixFor(mode, strength) {
  const scaled = clamp01(strength / 100) * 10;
  const lo = Math.floor(scaled);
  const hi = Math.min(10, lo + 1);
  const t = scaled - lo;
  return matrices[mode][lo].map((row, r) => row.map((v, c) => mix(v, matrices[mode][hi][r][c], t)));
}
function expectedColor(rgb, mode, strength) {
  const m = matrixFor(mode, strength);
  const [r,g,b] = rgb.map(srgbToLinearByte);
  return [
    linearToSrgbByte(r*m[0][0] + g*m[0][1] + b*m[0][2]),
    linearToSrgbByte(r*m[1][0] + g*m[1][1] + b*m[1][2]),
    linearToSrgbByte(r*m[2][0] + g*m[2][1] + b*m[2][2]),
  ];
}

function makeSvg() {
  const w = 640, h = 480, cell = 160;
  const rects = colors.map((rgb, i) => {
    const x = (i % 4) * cell;
    const y = Math.floor(i / 4) * cell;
    return `<rect x="${x}" y="${y}" width="${cell}" height="${cell}" fill="rgb(${rgb.join(",")})"/>`;
  }).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${rects}</svg>`;
}

async function setReactRangeValue(page, selector, value) {
  await page.locator(selector).evaluate((element, nextValue) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
    setter.call(element, String(nextValue));
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }, value);
}

async function waitForNewApproximation(page, previous) {
  await page.waitForFunction((prev) => {
    const image = document.querySelector('img[alt="Approximation"]');
    const card = document.querySelector('.compare-card');
    const current = image?.getAttribute("src");
    return Boolean(current?.startsWith("blob:") && current !== prev && card?.getAttribute("aria-busy") === "false");
  }, previous, { timeout: 10_000 });
}

async function samplePatchCenters(page) {
  return page.evaluate(async () => {
    const image = document.querySelector('img[alt="Approximation"]');
    if (!image) throw new Error("Approximation image missing");
    await image.decode();
    const canvas = document.createElement("canvas");
    canvas.width = image.naturalWidth;
    canvas.height = image.naturalHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Canvas unavailable");
    ctx.drawImage(image, 0, 0);
    const centers = [];
    for (let i = 0; i < 12; i += 1) {
      const x = (i % 4) * 160 + 80;
      const y = Math.floor(i / 4) * 160 + 80;
      centers.push(Array.from(ctx.getImageData(x, y, 1, 1).data.slice(0, 3)));
    }
    return centers;
  });
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const results = [];
let worst = { error: -1 };

try {
  await page.goto(`${BASE}/?r11_cvd=${Date.now()}`, { waitUntil: "networkidle" });
  await page.locator('input[type="file"]').setInputFiles({
    name: "r11-cvd-chart.svg",
    mimeType: "image/svg+xml",
    buffer: Buffer.from(makeSvg()),
  });
  await page.waitForFunction(() => document.querySelector('img[alt="Original"]')?.getAttribute("src")?.startsWith("blob:"));
  await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10_000 });
  await page.locator("#category-select").selectOption("Human");

  for (const mode of modes) {
    let before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
    await page.locator("#mode-select").selectOption(mode);
    await waitForNewApproximation(page, before);

    for (const strength of strengths) {
      before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
      await setReactRangeValue(page, "#strength-range", strength);
      await waitForNewApproximation(page, before);
      const actual = await samplePatchCenters(page);
      const expected = colors.map((rgb) => expectedColor(rgb, mode, strength));

      let maxError = 0;
      let sumError = 0;
      let sampleCount = 0;
      actual.forEach((rgb, index) => {
        rgb.forEach((channel, c) => {
          const error = Math.abs(channel - expected[index][c]);
          maxError = Math.max(maxError, error);
          sumError += error;
          sampleCount += 1;
          if (error > worst.error) {
            worst = { error, mode, strength, colorIndex: index, channel: c, actual: channel, expected: expected[index][c] };
          }
        });
      });

      const row = { mode, strength, meanChannelError: Number((sumError / sampleCount).toFixed(3)), maxChannelError: maxError };
      results.push(row);
      console.log(`R11 ${mode} Strength=${strength}: mean=${row.meanChannelError} max=${maxError}`);
      if (maxError > 6) throw new Error(`R11 ${mode} Strength=${strength} exceeded JPEG tolerance: max channel error ${maxError}`);
    }
  }

  // Permanent R10 semantic remains part of the actual product path.
  for (const mode of modes) {
    await page.locator("#mode-select").selectOption(mode);
    await setReactRangeValue(page, "#strength-range", 0);
    await page.waitForTimeout(180);
    await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10_000 });
    const original = await page.locator('img[alt="Original"]').first().getAttribute("src");
    const approximation = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
    if (!original || original !== approximation) throw new Error(`${mode} Strength 0 lost exact identity`);
  }

  const output = { baseUrl: BASE, results, worst, tolerance: 6, colors };
  await fs.writeFile("r11-cvd-audit.json", JSON.stringify(output, null, 2));
  console.log(JSON.stringify({ worst, rows: results.length }, null, 2));
} finally {
  await browser.close();
}
