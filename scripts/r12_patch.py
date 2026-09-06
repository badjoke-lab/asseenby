from pathlib import Path


def replace_once(path: str, old: str, new: str):
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one anchor, found {count}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1))


# --- src/transformEngine.ts -------------------------------------------------
path = Path("src/transformEngine.ts")
text = path.read_text()

replace_pairs = [
    (
        '  const ctx = outCanvas.getContext("2d");\n  if (!ctx) return;\n\n  drawBase(ctx, baseCanvas, width, height);',
        '  const ctx = outCanvas.getContext("2d");\n  if (!ctx) return;\n  const blurScale = relativeBlurScale(width, height);\n\n  drawBase(ctx, baseCanvas, width, height);',
    ),
    ('renderBlurred(ctx, baseCanvas, width, height, amount * 9);', 'renderBlurred(ctx, baseCanvas, width, height, amount * 9 * blurScale);'),
    ('const edgeBlur = blurCanvas(baseCanvas, amount * 8.2);', 'const edgeBlur = blurCanvas(baseCanvas, amount * 8.2 * blurScale);'),
    ('const centerBlur = blurCanvas(baseCanvas, amount * 9.6);', 'const centerBlur = blurCanvas(baseCanvas, amount * 9.6 * blurScale);'),
    ('renderBlurred(ctx, baseCanvas, width, height, amount * 7.2);', 'renderBlurred(ctx, baseCanvas, width, height, amount * 7.2 * blurScale);'),
    ('overlayMaskedCanvas(ctx, blurCanvas(baseCanvas, amount * 5.6), edgeMask, amount * 0.14);', 'overlayMaskedCanvas(ctx, blurCanvas(baseCanvas, amount * 5.6 * blurScale), edgeMask, amount * 0.14);'),
    ('drawHighlightBloom(ctx, baseCanvas, 172, amount * 26, amount * 0.38, 0.38);', 'drawHighlightBloom(ctx, baseCanvas, 172, amount * 26 * blurScale, amount * 0.38, 0.38);'),
    ('mixBlurredCopy(ctx, outCanvas, width, height, amount * 1.8, 0.52);', 'mixBlurredCopy(ctx, outCanvas, width, height, amount * 1.8 * blurScale, 0.52);'),
]
for old, new in replace_pairs:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"src/transformEngine.ts: expected one anchor, found {count}: {old!r}")
    text = text.replace(old, new, 1)

helper_anchor = '''function blurCanvas(source: HTMLCanvasElement, blurPx: number) {
'''
helper_block = '''const IMAGE_BLUR_REFERENCE_SHORT_EDGE = 900;

function relativeBlurScale(width: number, height: number) {
  return Math.min(width, height) / IMAGE_BLUR_REFERENCE_SHORT_EDGE;
}

function blurCanvas(source: HTMLCanvasElement, blurPx: number) {
'''
if text.count(helper_anchor) != 1:
    raise SystemExit("src/transformEngine.ts: blur helper anchor mismatch")
text = text.replace(helper_anchor, helper_block, 1)
path.write_text(text)


# --- methodology / limitations ---------------------------------------------
replace_once(
    "docs/methodology.md",
    "The strength control changes the degree of transformation applied. At 0%, Approximation is the Original source with no perception transform; 100% applies the full configured transform for that mode. Intermediate values interpolate within the renderer model and are not a validated clinical severity scale.",
    "The strength control changes the degree of transformation applied. At 0%, Approximation is the Original source with no perception transform; 100% applies the full configured transform for that mode. Intermediate values interpolate within the renderer model and are not a validated clinical severity scale. Image-space blur radii are normalized to the processed image short edge against the 900 px built-in-sample reference, so the same image content at different source pixel resolutions receives a comparable relative blur effect.",
)
replace_once(
    "docs/limitations.md",
    "Intermediate percentages are renderer intensity controls, not validated real-world severity values. They do not map to a clinical scale unless a future mode explicitly documents such a mapping.\n\nThe current spatial field-loss modes do not expose a patient-severity control. Their generic profile should not be interpreted as a severity measurement.",
    "Intermediate percentages are renderer intensity controls, not validated real-world severity values. They do not map to a clinical scale unless a future mode explicitly documents such a mapping. Pixel-radius blur components are normalized to image size for cross-resolution consistency, but that normalization is not an optical prescription, diopter value, acuity measurement, point-spread function, or patient-specific calibration.\n\nThe current spatial field-loss modes do not expose a patient-severity control. Their generic profile should not be interpreted as a severity measurement.",
)


# --- release schedule --------------------------------------------------------
replace_once(
    "docs/release-polish-schedule.md",
    "Status: **Step R11 PASS / CVD model fidelity production verified / R10 Strength semantics production verified**",
    "Status: **Step R12 ACTIVE / resolution-normalized image blur components / R11 CVD model fidelity production verified**",
)
replace_once(
    "docs/release-polish-schedule.md",
    "## Current next action\nR11 is closed. Re-read the roadmap and audit the remaining retained image transforms one by one for a concrete evidence/implementation mismatch. Do not create a new numbered release step unless an actual defect or unsupported model behavior is found.",
    "## Step R12 — Resolution-normalized image blur components\nStatus: **ACTIVE — implementation / validation**\n\nFinding:\n- `prepareBaseCanvas()` downsizes only images larger than 1400×960; smaller uploads retain their original pixel dimensions;\n- Blur, Tunnel Vision, Central Loss, Cataract-like, and Dog-like use fixed pixel blur radii in `transformEngine.ts`;\n- therefore identical image content at different source resolutions receives a different blur radius relative to the image: a 9 px Blur endpoint occupies 4% of a 225 px short edge but 1% of a 900 px short edge;\n- the compare UI then scales either source to the same display frame, so this source-resolution dependence is user-visible and conflicts with the R10 definition of Strength as degree within one renderer model.\n\nImplementation target:\n- preserve the current 1440×900 built-in sample exactly by using its 900 px short edge as the reference scale;\n- multiply every image-track pixel blur radius by `min(width, height) / 900`;\n- apply the normalization to Blur, Tunnel Vision peripheral blur, Central Loss central blur, Cataract-like blur/bloom spread, and Dog-like fine-detail softening;\n- do not change masks, color transforms, contrast transforms, mode evidence grades, or any spatial renderer.\n\nAcceptance:\n- same-content 350×225 and 1400×900 uploads produce comparable normalized outputs for every blur-bearing public image mode at Strength 40 and 100;\n- the built-in 1440×900 sample retains scale 1.0 and therefore preserves all pre-R12 configured blur endpoints;\n- Strength 0 identity and R11 CVD fidelity remain unchanged;\n- full desktop/390px image + spatial browser regression remains green;\n- matching main build and production smoke pass after merge before R12 is marked production verified.\n\n## Current next action\nRun a controlled same-content resolution audit for Blur / Tunnel / Central Loss / Cataract-like / Dog-like at 350×225 versus 1400×900, then run the full image/spatial browser regression. Open a clean PR only if both gates pass.",
)
