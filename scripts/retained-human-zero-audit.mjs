import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const BASE = 'http://127.0.0.1:4173';
const modes = ['protan','deutan','tritan','blur','low_contrast','cataract','tunnel','central_loss'];
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#111"/><stop offset="1" stop-color="#eee"/></linearGradient></defs>
<rect width="600" height="400" fill="#ddd"/><rect x="0" y="0" width="100" height="100" fill="#e32f2f"/><rect x="100" y="0" width="100" height="100" fill="#30b44a"/><rect x="200" y="0" width="100" height="100" fill="#2f59d9"/><rect x="300" y="0" width="100" height="100" fill="#e6d332"/><rect x="400" y="0" width="100" height="100" fill="#30c9cf"/><rect x="500" y="0" width="100" height="100" fill="#cf3ed0"/>
<rect x="0" y="100" width="600" height="80" fill="url(#g)"/><rect x="30" y="220" width="540" height="140" fill="#faf8f2" stroke="#222" stroke-width="4"/><g stroke="#222" stroke-width="2"><path d="M50 240H550M50 260H550M50 280H550M50 300H550M50 320H550M50 340H550"/><path d="M80 220V360M130 220V360M180 220V360M230 220V360M280 220V360M330 220V360M380 220V360M430 220V360M480 220V360M530 220V360"/></g><circle cx="300" cy="290" r="55" fill="#777"/><circle cx="300" cy="290" r="24" fill="#f8f8f8"/></svg>`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
await page.goto(BASE, { waitUntil: 'networkidle' });
await page.locator('input[type=file]').setInputFiles({ name:'zero.svg', mimeType:'image/svg+xml', buffer:Buffer.from(svg) });
await page.waitForFunction(() => document.querySelector('img[alt="Original"]')?.getAttribute('src')?.startsWith('blob:'));
await page.locator('#category-select').selectOption('Human');
const approx = page.locator('img[alt="Approximation"]').first();
const range = page.locator('#strength-range');

async function waitNew(previous, label) {
  await page.waitForFunction((prev) => {
    const img = document.querySelector('img[alt="Approximation"]');
    return Boolean(img?.getAttribute('src')?.startsWith('blob:') && img.getAttribute('src') !== prev && document.querySelector('.compare-card')?.getAttribute('aria-busy') === 'false');
  }, previous, { timeout: 15000 }).catch(async error => {
    const debug = await page.evaluate(() => ({mode:document.querySelector('#mode-select')?.value,strength:document.querySelector('#strength-range')?.value,busy:document.querySelector('.compare-card')?.getAttribute('aria-busy')}));
    throw new Error(`${label}: ${JSON.stringify(debug)} ${error}`);
  });
}

async function setStrength(value) {
  if (await range.inputValue() === String(value)) return;
  const before = await approx.getAttribute('src');
  await range.evaluate((el, next) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
    if (!setter) throw new Error('value setter missing');
    setter.call(el, String(next));
    el.dispatchEvent(new Event('input', {bubbles:true}));
    el.dispatchEvent(new Event('change', {bubbles:true}));
  }, value);
  await waitNew(before, `strength ${value}`);
}

const baseline = await page.evaluate(async () => {
  const orig = document.querySelector('img[alt="Original"]');
  if (!(orig instanceof HTMLImageElement)) throw new Error('original missing');
  await orig.decode();
  const c = document.createElement('canvas'); c.width=orig.naturalWidth; c.height=orig.naturalHeight;
  const ctx=c.getContext('2d'); if(!ctx) throw new Error('context missing'); ctx.drawImage(orig,0,0);
  const blob=await new Promise((resolve,reject)=>c.toBlob(b=>b?resolve(b):reject(new Error('blob failed')),'image/jpeg',0.94));
  const url=URL.createObjectURL(blob); const copy=new Image(); copy.src=url; await copy.decode();
  const c2=document.createElement('canvas'); c2.width=c.width; c2.height=c.height; const x2=c2.getContext('2d'); x2.drawImage(copy,0,0);
  const a=ctx.getImageData(0,0,c.width,c.height).data,b=x2.getImageData(0,0,c.width,c.height).data;
  let sum=0,max=0,changed1=0,changed10=0,count=0; for(let i=0;i<a.length;i+=4){let pd=0;for(let k=0;k<3;k++){const d=Math.abs(a[i+k]-b[i+k]);sum+=d;max=Math.max(max,d);pd=Math.max(pd,d);count++;}if(pd>=1)changed1++;if(pd>=10)changed10++;}
  URL.revokeObjectURL(url); return {meanAbs:sum/count,maxChannel:max,changed1Pct:changed1/(c.width*c.height)*100,changed10Pct:changed10/(c.width*c.height)*100};
});

await setStrength(0);
const rows=[];
for (const mode of modes) {
  if (await page.locator('#mode-select').inputValue() !== mode) {
    const before=await approx.getAttribute('src'); await page.locator('#mode-select').selectOption(mode); await waitNew(before,`mode ${mode}`);
  }
  const metrics=await page.evaluate(async () => {
    const orig=document.querySelector('img[alt="Original"]'),sim=document.querySelector('img[alt="Approximation"]'); if(!(orig instanceof HTMLImageElement)||!(sim instanceof HTMLImageElement))throw new Error('images missing'); await Promise.all([orig.decode(),sim.decode()]);
    const w=orig.naturalWidth,h=orig.naturalHeight,c1=document.createElement('canvas'),c2=document.createElement('canvas');c1.width=c2.width=w;c1.height=c2.height=h;const x1=c1.getContext('2d'),x2=c2.getContext('2d');x1.drawImage(orig,0,0);x2.drawImage(sim,0,0);const a=x1.getImageData(0,0,w,h).data,b=x2.getImageData(0,0,w,h).data;let sum=0,max=0,changed1=0,changed10=0,count=0;for(let i=0;i<a.length;i+=4){let pd=0;for(let k=0;k<3;k++){const d=Math.abs(a[i+k]-b[i+k]);sum+=d;max=Math.max(max,d);pd=Math.max(pd,d);count++;}if(pd>=1)changed1++;if(pd>=10)changed10++;}return {meanAbs:sum/count,maxChannel:max,changed1Pct:changed1/(w*h)*100,changed10Pct:changed10/(w*h)*100};
  });
  rows.push({mode,...metrics,meanVsJpegBaseline:metrics.meanAbs/baseline.meanAbs});
  console.log('ZERO',mode,JSON.stringify(rows.at(-1)));
}
const output={jpegBaseline:baseline,rows}; await fs.writeFile('retained-human-zero-audit.json',JSON.stringify(output,null,2)); console.log(JSON.stringify(output,null,2)); await browser.close();
