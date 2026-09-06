from pathlib import Path


def replace_once(path: str, old: str, new: str):
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one anchor, found {count}: {old[:100]!r}")
    p.write_text(text.replace(old, new, 1))


replace_once(
    "src/App.tsx",
    '        const transformedCanvas = document.createElement("canvas");\n',
    '''        if (renderStrength <= 0) {
          if (transformedObjectUrlRef.current) {
            URL.revokeObjectURL(transformedObjectUrlRef.current);
            transformedObjectUrlRef.current = null;
          }
          setTransformedUrl(imageSrc);
          return;
        }

        const transformedCanvas = document.createElement("canvas");
''',
)

replace_once("src/transformEngine.ts", "    renderBlurred(ctx, baseCanvas, width, height, 1 + amount * 8);", "    renderBlurred(ctx, baseCanvas, width, height, amount * 9);")
replace_once(
    "src/transformEngine.ts",
    '''    const edgeMask = createMaskCanvas(width, height, 0.44 - amount * 0.14, 0.84 - amount * 0.05, false);
    const edgeBlur = blurCanvas(baseCanvas, 2 + amount * 6.2);
    const edgeGray = grayscaleCanvas(baseCanvas);
    overlayMaskedCanvas(ctx, edgeBlur, edgeMask, 0.58 + amount * 0.16);
    overlayMaskedCanvas(ctx, edgeGray, edgeMask, 0.08 + amount * 0.1);
''',
    '''    const edgeMask = createMaskCanvas(width, height, 0.44 - amount * 0.14, 0.84 - amount * 0.05, false);
    const edgeBlur = blurCanvas(baseCanvas, amount * 8.2);
    const edgeGray = grayscaleCanvas(baseCanvas);
    overlayMaskedCanvas(ctx, edgeBlur, edgeMask, amount * 0.74);
    overlayMaskedCanvas(ctx, edgeGray, edgeMask, amount * 0.18);
''',
)
replace_once(
    "src/transformEngine.ts",
    '''    const centerMask = createMaskCanvas(width, height, 0.02 + amount * 0.03, 0.1 + amount * 0.16, true);
    const centerBlur = blurCanvas(baseCanvas, 2.8 + amount * 6.8);
    const centerGray = grayscaleCanvas(baseCanvas);
    overlayMaskedCanvas(ctx, centerBlur, centerMask, 0.82);
    overlayMaskedCanvas(ctx, centerGray, centerMask, 0.1 + amount * 0.1);
''',
    '''    const centerMask = createMaskCanvas(width, height, 0.02 + amount * 0.03, 0.1 + amount * 0.16, true);
    const centerBlur = blurCanvas(baseCanvas, amount * 9.6);
    const centerGray = grayscaleCanvas(baseCanvas);
    overlayMaskedCanvas(ctx, centerBlur, centerMask, amount * 0.82);
    overlayMaskedCanvas(ctx, centerGray, centerMask, amount * 0.2);
''',
)
replace_once(
    "src/transformEngine.ts",
    '''    renderBlurred(ctx, baseCanvas, width, height, 1.8 + amount * 5.4);
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    applyLowContrastToData(data, 0.26 + amount * 0.3);
    desaturateData(data, 0.08 + amount * 0.12);
    warmTintData(data, 0.06 + amount * 0.14);
    softenHighlights(data, 0.74, 0.18 + amount * 0.18);
    ctx.putImageData(imageData, 0, 0);
    drawWarmVeil(ctx, width, height, 0.08 + amount * 0.12);
    const edgeMask = createMaskCanvas(width, height, 0.58, 0.94, false);
    overlayMaskedCanvas(ctx, blurCanvas(baseCanvas, 1.4 + amount * 4.2), edgeMask, 0.06 + amount * 0.08);
    drawHighlightBloom(ctx, baseCanvas, 172, 10 + amount * 16, 0.14 + amount * 0.24, 0.38);
''',
    '''    renderBlurred(ctx, baseCanvas, width, height, amount * 7.2);
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
''',
)
replace_once(
    "src/transformEngine.ts",
    '''    applyLowContrastToData(data, 0.24 + amount * 0.34);
    desaturateData(data, 0.04 + amount * 0.07);
    softenHighlights(data, 0.82, 0.06 + amount * 0.08);
''',
    '''    applyLowContrastToData(data, amount * 0.58);
    desaturateData(data, amount * 0.11);
    softenHighlights(data, 0.82, amount * 0.14);
''',
)
replace_once("src/transformEngine.ts", "    compressRedGreenAxis(data, 0.08 + severity * 0.18);", "    compressRedGreenAxis(data, severity * 0.26);")
replace_once("src/transformEngine.ts", "    compressRedGreenAxis(data, 0.06 + severity * 0.16);", "    compressRedGreenAxis(data, severity * 0.22);")
replace_once("src/transformEngine.ts", "    compressBlueYellowAxis(data, 0.07 + severity * 0.18);", "    compressBlueYellowAxis(data, severity * 0.25);")
replace_once(
    "src/transformEngine.ts",
    '''    compressRedGreenAxis(data, 0.06 + severity * 0.12);
    applyLowContrastToData(data, 0.035 + severity * 0.075);
''',
    '''    compressRedGreenAxis(data, severity * 0.18);
    applyLowContrastToData(data, severity * 0.11);
''',
)
replace_once("src/transformEngine.ts", "    mixBlurredCopy(ctx, outCanvas, width, height, 0.45 + amount * 1.35, 0.52);", "    mixBlurredCopy(ctx, outCanvas, width, height, amount * 1.8, 0.52);")
replace_once(
    "src/transformEngine.ts",
    '''  gradient.addColorStop(0.7, `rgba(18,14,12,${0.08 + amount * 0.12})`);
  gradient.addColorStop(1, `rgba(18,14,12,${0.58 + amount * 0.24})`);
''',
    '''  gradient.addColorStop(0.7, `rgba(18,14,12,${amount * 0.2})`);
  gradient.addColorStop(1, `rgba(18,14,12,${amount * 0.82})`);
''',
)
replace_once(
    "src/transformEngine.ts",
    '''  gradient.addColorStop(0, `rgba(42, 36, 32, ${0.62 + amount * 0.18})`);
  gradient.addColorStop(0.45, `rgba(64, 56, 50, ${0.34 + amount * 0.14})`);
''',
    '''  gradient.addColorStop(0, `rgba(42, 36, 32, ${amount * 0.8})`);
  gradient.addColorStop(0.45, `rgba(64, 56, 50, ${amount * 0.48})`);
''',
)

smoke = Path(".github/production-smoke.mjs")
text = smoke.read_text()
helper_anchor = "async function waitForCurrentProduction(page) {"
helper = '''async function setReactRangeValue(page, selector, value) {
  const range = page.locator(selector);
  await range.evaluate((element, nextValue) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
    if (!setter) throw new Error("range value setter unavailable");
    setter.call(element, String(nextValue));
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }, value);
}

async function assertImageStrengthZeroIdentity(page) {
  await setReactRangeValue(page, "#strength-range", 0);
  await page.waitForFunction(() => {
    const original = document.querySelector('img[alt="Original"]')?.getAttribute("src");
    const approximation = document.querySelector('img[alt="Approximation"]')?.getAttribute("src");
    return document.querySelector("#strength-range")?.value === "0"
      && document.querySelector(".compare-card")?.getAttribute("aria-busy") === "false"
      && Boolean(original && approximation && original === approximation);
  }, undefined, { timeout: 10_000 });

  for (const [category, modes] of [["Human", expectedHumanImageModes], ["Animal", expectedAnimalImageModes]]) {
    await page.locator("#category-select").selectOption(category);
    for (const mode of modes) {
      await page.locator("#mode-select").selectOption(mode);
      await page.waitForTimeout(140);
      await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 10_000 });
      const original = await page.locator('img[alt="Original"]').first().getAttribute("src");
      const approximation = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
      assert(original === approximation, `desktop image: Strength 0 is not Original for ${category}/${mode}`);
    }
  }
  await page.locator("#category-select").selectOption("Human");
  await page.locator("#mode-select").selectOption("protan");
  await setReactRangeValue(page, "#strength-range", 65);
  await page.waitForFunction(() => document.querySelector("#strength-range")?.value === "65" && document.querySelector(".compare-card")?.getAttribute("aria-busy") === "false", undefined, { timeout: 10_000 });
}

async function waitForCurrentProduction(page) {'''
if text.count(helper_anchor) != 1:
    raise SystemExit("production smoke helper anchor mismatch")
text = text.replace(helper_anchor, helper, 1)
call_anchor = '  assert(!humanBodyText.includes("Night / Low Light"), "desktop image: removed Night / Low Light image mode is still visible");\n\n'
if text.count(call_anchor) != 1:
    raise SystemExit("production smoke zero call anchor mismatch")
text = text.replace(call_anchor, call_anchor + "  await assertImageStrengthZeroIdentity(page);\n\n", 1)
smoke.write_text(text)

replace_once(
    "docs/methodology.md",
    "The strength control changes the degree of transformation applied.",
    "The strength control changes the degree of transformation applied. At 0%, Approximation is the Original source with no perception transform; 100% applies the full configured transform for that mode. Intermediate values interpolate within the renderer model and are not a validated clinical severity scale.",
)
replace_once(
    "docs/limitations.md",
    '''## Strength control limitation
The strength slider changes degree within the current image approximation model.
It does not map to a validated real-world severity scale unless a future mode explicitly documents such a mapping.
''',
    '''## Strength control limitation
The strength slider changes degree within the current image approximation model. At 0%, the image comparison uses the Original source without a perception transform; 100% applies the mode's full configured transform.
Intermediate percentages are renderer intensity controls, not validated real-world severity values. They do not map to a clinical scale unless a future mode explicitly documents such a mapping.
''',
)

schedule = Path("docs/release-polish-schedule.md")
text = schedule.read_text()
old_state = "Status: **Step R9 PASS / evidence accuracy validated / R8 production-polished**"
if text.count(old_state) != 1:
    raise SystemExit("R10 top status anchor mismatch")
text = text.replace(old_state, "Status: **Step R10 ACTIVE / Strength semantics correction / R9 evidence accuracy validated**", 1)
old_next = """## Current next action
Continue the roadmap's retained-mode transform/evidence-quality audit without reopening removed modes. Prioritize the remaining public image renderers by implementation maturity and evidence/model fit, while keeping the accepted spatial set stable."""
if text.count(old_next) != 1:
    raise SystemExit("R10 current next action anchor mismatch")
r10 = """## Step R10 — Strength semantics
Status: **ACTIVE — implementation / validation**

Finding:
- the public image Strength control exposes 0–100%, and methodology defines it as the degree of transformation;
- retained-Human output audit `34046781290` passed 24 controlled outputs at Strength 40/70/100 with no monotonicity or field-direction finding;
- a dedicated Strength-0 audit `34046907994` then showed that 0% still applied substantial fixed effects: JPEG-roundtrip baseline mean delta was 0.731, while Blur was 8.63, Low Contrast 21.08, Cataract-like 30.38, and Tunnel Vision 6.66;
- source inspection confirmed fixed nonzero terms at `amount=0` across multiple transforms, so the 0% label did not match renderer behavior.

Implementation:
- at Strength 0, use the Original source directly as Approximation rather than transform/JPEG-reencode it;
- scale each transform's effect components continuously from identity to its existing 100% endpoint;
- apply the same semantics to Dog-like because the Strength control is shared across all public image modes;
- add permanent production-smoke coverage that checks exact Original/Approximation source identity at 0% for all 8 Human modes plus Dog-like;
- document 0%=Original, 100%=full configured transform, with intermediate values explicitly non-clinical.

Acceptance:
- every public image mode is exact Original at Strength 0;
- Strength 1 produces only a small departure from Original rather than the former fixed minimum effect;
- controlled output delta increases monotonically through 1/40/70/100 for every public image mode;
- Tunnel Vision remains edge-dominant and Central Loss remains center-dominant;
- each mode's 100% configured endpoint is preserved;
- full desktop/390px image + spatial regression remains green;
- after merge, matching main build and production smoke must pass before R10 is marked production verified.

## Current next action
Validate the corrected 0/1/40/70/100 output curves for all 9 public image modes, then run the full image/spatial browser regression. Open a clean PR only if both gates pass."""
schedule.write_text(text.replace(old_next, r10, 1))
