import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE = 'http://127.0.0.1:4173';
const modes = ['protan','deutan','tritan','blur','low_contrast','cataract','tunnel','central_loss'];
const strengths = [40,70,100];
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#111"/><stop offset="1" stop-color="#eee"/></linearGradient></defs>
  <rect width="600" height="400" fill="#ddd"/>
  <rect x="0" y="0" width="100" height="100" fill="#e32f2f"/><rect x="100" y="0" width="100" height="100" fill="#30b44a"/><rect x="200" y="0" width="100" height="100" fill="#2f59d9"/>
  <rect x="300" y="0" width="100" height="100" fill="#e6d332"/><rect x="400" y="0" width="100" height="100" fill="#30c9cf"/><rect x="500" y="0" width="100" height="100" fill="#cf3ed0"/>
  <rect x="0" y="100" width="600" height="80" fill="url(#g)"/>
  <rect x="30" y="220" width="540" height="140" fill="#faf8f2" stroke="#222" stroke-width="4"/>
  <g stroke="#222" stroke-width="2"><path d="M50 240H550M50 260H550M50 280H550M50 300H550M50 320H550M50 340H550"/><path d="M80 220V360M130 220V360M180 220V360M230 220V360M280 220V360M330 220V360M380 220V360M430 220V360M480 220V360M530 220V360"/></g>
  <circle cx="300" cy="290" r="55" fill="#777"/><circle cx="300" cy="290" r="24" fill="#f8f8f8"/>
  <text x="300" y="390" text-anchor="middle" font-family="Arial" font-size="22" fill="#222">COLOR · CONTRAST · DETAIL</text>
</svg>`;

const round = (n) => Math.round(n * 1000) / 1000;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
await page.goto(BASE, { waitUntil: 'networkidle' });
await page.locator('input[type=file]').setInputFiles({ name:'audit.svg', mimeType:'image/svg+xml', buffer:Buffer.from(svg) });
await page.waitForFunction(() => document.querySelector('img[alt="Original"]')?.getAttribute('src')?.startsWith('blob:'));
await page.locator('#category-select').selectOption('Human');
await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10000 });

const approx = page.locator('img[alt="Approximation"]').first();
const range = page.locator('#strength-range');
const rows = [];

async function waitForNewApproximation(previous, label) {
  await page.waitForFunction((prev) => {
    const img = document.querySelector('img[alt="Approximation"]');
    return Boolean(img?.getAttribute('src')?.startsWith('blob:') && img.getAttribute('src') !== prev && document.querySelector('.compare-card')?.getAttribute('aria-busy') === 'false');
  }, previous, { timeout: 15000 }).catch(async (error) => {
    const debug = await page.evaluate(() => ({
      mode: document.querySelector('#mode-select')?.value,
      strength: document.querySelector('#strength-range')?.value,
      busy: document.querySelector('.compare-card')?.getAttribute('aria-busy'),
      approx: document.querySelector('img[alt="Approximation"]')?.getAttribute('src'),
    }));
    throw new Error(`${label}: render did not produce a new settled blob: ${JSON.stringify(debug)}\n${error}`);
  });
}

async function setStrength(value) {
  const desired = String(value);
  const current = await range.inputValue();
  if (current === desired) {
    await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10000 });
    return;
  }
  const before = await approx.getAttribute('src');
  await range.evaluate((el, next) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
    if (!setter) throw new Error('HTMLInputElement value setter unavailable');
    setter.call(el, String(next));
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }, value);
  await waitForNewApproximation(before, `strength ${value}`);
}

async function readMetrics() {
  return page.evaluate(async () => {
    const orig = document.querySelector('img[alt="Original"]');
    const simulated = document.querySelector('img[alt="Approximation"]');
    if (!(orig instanceof HTMLImageElement) || !(simulated instanceof HTMLImageElement)) throw new Error('missing comparison images');
    await Promise.all([orig.decode(), simulated.decode()]);
    const w = orig.naturalWidth, h = orig.naturalHeight;
    const c1 = document.createElement('canvas'), c2 = document.createElement('canvas');
    c1.width = c2.width = w; c1.height = c2.height = h;
    const x1 = c1.getContext('2d'), x2 = c2.getContext('2d');
    if (!x1 || !x2) throw new Error('2d context unavailable');
    x1.drawImage(orig,0,0,w,h); x2.drawImage(simulated,0,0,w,h);
    const a = x1.getImageData(0,0,w,h).data, b = x2.getImageData(0,0,w,h).data;
    let sum=0,max=0,changed10=0,count=0,centerSum=0,centerCount=0,edgeSum=0,edgeCount=0;
    const cx=w/2, cy=h/2, r=Math.min(w,h)*0.25;
    for(let y=0;y<h;y++) for(let x=0;x<w;x++) {
      const i=(y*w+x)*4; let pd=0;
      for(let c=0;c<3;c++) { const d=Math.abs(a[i+c]-b[i+c]); sum+=d; pd=Math.max(pd,d); max=Math.max(max,d); count++; }
      if(pd>=10) changed10++;
      const dist=Math.hypot(x-cx,y-cy);
      const mean=(Math.abs(a[i]-b[i])+Math.abs(a[i+1]-b[i+1])+Math.abs(a[i+2]-b[i+2]))/3;
      if(dist<=r){ centerSum+=mean; centerCount++; }
      if(x<w*.15 || x>w*.85 || y<h*.15 || y>h*.85){ edgeSum+=mean; edgeCount++; }
    }
    return { width:w,height:h,meanAbs:sum/count,maxChannel:max,changed10Pct:changed10/(w*h)*100,centerMean:centerSum/centerCount,edgeMean:edgeSum/edgeCount };
  });
}

for (const mode of modes) {
  const currentMode = await page.locator('#mode-select').inputValue();
  if (currentMode !== mode) {
    const before = await approx.getAttribute('src');
    await page.locator('#mode-select').selectOption(mode);
    await waitForNewApproximation(before, `mode ${mode}`);
  }
  for (const strength of strengths) {
    console.log(`AUDIT ${mode} strength=${strength}`);
    await setStrength(strength);
    const metrics = await readMetrics();
    rows.push({ mode, strength, ...Object.fromEntries(Object.entries(metrics).map(([k,v]) => [k, typeof v==='number' ? round(v) : v])) });
    await fs.writeFile('retained-human-output-audit.json', JSON.stringify({ rows, findings: [] }, null, 2));
  }
}

const byMode = Object.fromEntries(modes.map(mode => [mode, rows.filter(r => r.mode === mode)]));
const findings = [];
for (const mode of modes) {
  const r = byMode[mode];
  const means = r.map(x => x.meanAbs);
  if (!(means[0] <= means[1] + .05 && means[1] <= means[2] + .05)) findings.push(`${mode}: mean output delta is not monotonic across Strength 40/70/100 (${means.join(', ')})`);
  if (means[2] < 1) findings.push(`${mode}: Strength 100 produces negligible mean delta (${means[2]})`);
  if (mode==='tunnel' && !(r[2].edgeMean > r[2].centerMean*1.5)) findings.push(`tunnel: edge effect is not clearly stronger than center at Strength 100 (${r[2].edgeMean} vs ${r[2].centerMean})`);
  if (mode==='central_loss' && !(r[2].centerMean > r[2].edgeMean*1.5)) findings.push(`central_loss: center effect is not clearly stronger than edge at Strength 100 (${r[2].centerMean} vs ${r[2].edgeMean})`);
}

const output = { rows, findings };
await fs.writeFile('retained-human-output-audit.json', JSON.stringify(output,null,2));
console.log(JSON.stringify(output,null,2));
await browser.close();
