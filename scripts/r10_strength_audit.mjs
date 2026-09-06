import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE = 'http://127.0.0.1:4173';
const modes = [
  ['Human','protan'],['Human','deutan'],['Human','tritan'],['Human','blur'],
  ['Human','low_contrast'],['Human','cataract'],['Human','tunnel'],['Human','central_loss'],['Animal','dog'],
];
const strengths = [0,1,40,70,100];
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><defs><linearGradient id="g"><stop stop-color="#111"/><stop offset="1" stop-color="#eee"/></linearGradient></defs><rect width="600" height="400" fill="#ddd"/><rect width="100" height="100" fill="#e32f2f"/><rect x="100" width="100" height="100" fill="#30b44a"/><rect x="200" width="100" height="100" fill="#2f59d9"/><rect x="300" width="100" height="100" fill="#e6d332"/><rect x="400" width="100" height="100" fill="#30c9cf"/><rect x="500" width="100" height="100" fill="#cf3ed0"/><rect y="100" width="600" height="80" fill="url(#g)"/><rect x="30" y="220" width="540" height="140" fill="#faf8f2" stroke="#222" stroke-width="4"/><g stroke="#222" stroke-width="2"><path d="M50 240H550M50 260H550M50 280H550M50 300H550M50 320H550M50 340H550"/><path d="M80 220V360M130 220V360M180 220V360M230 220V360M280 220V360M330 220V360M380 220V360M430 220V360M480 220V360M530 220V360"/></g><circle cx="300" cy="290" r="55" fill="#777"/><circle cx="300" cy="290" r="24" fill="#f8f8f8"/></svg>`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
await page.goto(BASE, { waitUntil: 'networkidle' });
await page.locator('input[type=file]').setInputFiles({ name: 'r10.svg', mimeType: 'image/svg+xml', buffer: Buffer.from(svg) });
await page.waitForFunction(() => document.querySelector('img[alt="Original"]')?.getAttribute('src')?.startsWith('blob:'));
const range = page.locator('#strength-range');

async function setRange(value) {
  if (await range.inputValue() === String(value)) return;
  await range.evaluate((el, v) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
    if (!setter) throw new Error('range value setter unavailable');
    setter.call(el, String(v));
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }, value);
  await page.waitForTimeout(120);
  await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10000 });
}

async function readMetrics() {
  return page.evaluate(async () => {
    const o = document.querySelector('img[alt="Original"]');
    const s = document.querySelector('img[alt="Approximation"]');
    if (!(o instanceof HTMLImageElement) || !(s instanceof HTMLImageElement)) throw new Error('images missing');
    await Promise.all([o.decode(), s.decode()]);
    const sameSource = o.src === s.src;
    if (sameSource) return { sameSource, meanAbs: 0, centerMean: 0, edgeMean: 0 };
    const w=o.naturalWidth,h=o.naturalHeight,c1=document.createElement('canvas'),c2=document.createElement('canvas');
    c1.width=c2.width=w;c1.height=c2.height=h;const x1=c1.getContext('2d'),x2=c2.getContext('2d');
    x1.drawImage(o,0,0);x2.drawImage(s,0,0);const a=x1.getImageData(0,0,w,h).data,b=x2.getImageData(0,0,w,h).data;
    let sum=0,n=0,cs=0,cn=0,es=0,en=0;const cx=w/2,cy=h/2,r=Math.min(w,h)*.25;
    for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=(y*w+x)*4,m=(Math.abs(a[i]-b[i])+Math.abs(a[i+1]-b[i+1])+Math.abs(a[i+2]-b[i+2]))/3;sum+=m;n++;if(Math.hypot(x-cx,y-cy)<=r){cs+=m;cn++;}if(x<w*.15||x>w*.85||y<h*.15||y>h*.85){es+=m;en++;}}
    return { sameSource, meanAbs: sum/n, centerMean: cs/cn, edgeMean: es/en };
  });
}

const rows=[];
for (const [category, mode] of modes) {
  await page.locator('#category-select').selectOption(category);
  await page.locator('#mode-select').selectOption(mode);
  for (const strength of strengths) {
    await setRange(strength);
    const m = await readMetrics();
    rows.push({ category, mode, strength, ...m });
    console.log('R10', mode, strength, m.meanAbs.toFixed(3), m.sameSource);
  }
}

const findings=[];
for (const [,mode] of modes) {
  const r=rows.filter(x=>x.mode===mode);
  if(!r[0].sameSource||r[0].meanAbs!==0)findings.push(`${mode}: Strength 0 is not exact Original`);
  if(r[1].meanAbs>3)findings.push(`${mode}: Strength 1 is too far from Original (${r[1].meanAbs})`);
  const means=r.map(x=>x.meanAbs);
  for(let i=1;i<means.length;i++)if(means[i]+.05<means[i-1])findings.push(`${mode}: non-monotonic ${means.join(',')}`);
  if(mode==='tunnel'&&!(r.at(-1).edgeMean>r.at(-1).centerMean*1.5))findings.push('tunnel: edge dominance lost');
  if(mode==='central_loss'&&!(r.at(-1).centerMean>r.at(-1).edgeMean*1.5))findings.push('central_loss: center dominance lost');
}

const output={rows,findings};
await fs.writeFile('r10-strength-audit.json',JSON.stringify(output,null,2));
console.log(JSON.stringify(output,null,2));
await browser.close();
if(findings.length)throw new Error(findings.join(' | '));
