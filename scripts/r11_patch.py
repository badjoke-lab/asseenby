from pathlib import Path


def replace_once(path: str, old: str, new: str):
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one anchor, found {count}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1))


# --- src/transformEngine.ts -------------------------------------------------
transform = Path("src/transformEngine.ts")
text = transform.read_text()

old_constants = '''const PROTAN_MATRIX: Matrix3x3 = [
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
'''

new_constants = '''type CvdModeKey = "protan" | "deutan" | "tritan";

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
'''

if text.count(old_constants) != 1:
    raise SystemExit("transformEngine constants anchor mismatch")
text = text.replace(old_constants, new_constants, 1)

old_branches = '''  } else if (modeKey === "protan") {
    const severity = curveAmount(amount, 1.2);
    applyColorMatrixLinear(data, severity, PROTAN_MATRIX, 0.44);
    compressRedGreenAxis(data, severity * 0.26);
  } else if (modeKey === "deutan") {
    const severity = curveAmount(amount, 1.16);
    applyColorMatrixLinear(data, severity, DEUTAN_MATRIX, 0.44);
    compressRedGreenAxis(data, severity * 0.22);
  } else if (modeKey === "tritan") {
    const severity = curveAmount(amount, 1.12);
    applyColorMatrixLinear(data, severity, TRITAN_MATRIX, 0.38);
    compressBlueYellowAxis(data, severity * 0.25);
  } else if (modeKey === "dog") {
    const severity = curveAmount(amount, 1.08);
    // Human-display proxy: canine behavioral work supports a dichromatic pattern
    // broadly similar to human red-green deficiency, but this is not a canine
    // cone-catch reconstruction. Keep the chromatic and acuity changes restrained.
    applyColorMatrixLinear(data, severity * 0.82, DEUTAN_MATRIX, 0.34);
'''
new_branches = '''  } else if (isCvdMode(modeKey)) {
    applyMachadoCvd(data, modeKey, amount);
  } else if (modeKey === "dog") {
    const severity = curveAmount(amount, 1.08);
    // Human-display proxy: canine behavioral work supports a dichromatic pattern
    // broadly similar to human red-green deficiency, but this is not a canine
    // cone-catch reconstruction. Keep the chromatic and acuity changes restrained.
    applyColorMatrixLinear(data, severity * 0.82, DOG_BASE_DEUTAN_MATRIX, 0.34);
'''
if text.count(old_branches) != 1:
    raise SystemExit("transformEngine CVD branch anchor mismatch")
text = text.replace(old_branches, new_branches, 1)

old_helper_anchor = '''function applyColorMatrixLinear(
  data: Uint8ClampedArray,
  amount: number,
  matrix: Matrix3x3,
  luminancePreserve: number,
) {
'''
new_helper_block = '''function isCvdMode(modeKey: string): modeKey is CvdModeKey {
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
'''
if text.count(old_helper_anchor) != 1:
    raise SystemExit("transformEngine helper anchor mismatch")
text = text.replace(old_helper_anchor, new_helper_block, 1)

old_blue = '''function compressBlueYellowAxis(data: Uint8ClampedArray, amount: number) {
  for (let i = 0; i < data.length; i += 4) {
    const yellow = (data[i] + data[i + 1]) * 0.5;
    const blue = data[i + 2];
    data[i + 2] = clamp255(mix(blue, yellow, amount));
    data[i] = clamp255(mix(data[i], yellow * 0.9 + blue * 0.1, amount * 0.14));
    data[i + 1] = clamp255(mix(data[i + 1], yellow * 0.94 + blue * 0.06, amount * 0.1));
  }
}

'''
if text.count(old_blue) != 1:
    raise SystemExit("transformEngine blue-yellow helper anchor mismatch")
text = text.replace(old_blue, "", 1)
transform.write_text(text)


# --- src/modeEvidence.ts ----------------------------------------------------
replace_once(
    "src/modeEvidence.ts",
    'modelNote: "The current output uses a linear-RGB deficiency transform with additional red-green axis compression. It is stronger than a naive RGB mix, but still remains a screen-space approximation rather than a patient-specific perceptual model.",',
    'modelNote: "The current image renderer applies the Machado pre-computed protanomaly matrices to linear RGB and interpolates between adjacent 0.1 severity steps. The public Strength control selects the renderer parameter; it is not a patient-specific or measured clinical severity.",',
)
replace_once(
    "src/modeEvidence.ts",
    'note: "Core simulation reference used as the main implementation anchor for color-deficiency-style transforms.",',
    'note: "Core implementation reference for the linear-RGB protanomaly matrix family and its severity interpolation.",',
)
replace_once(
    "src/modeEvidence.ts",
    'modelNote: "The transform now combines a linear-RGB deficiency mapping with additional red-green axis compression. This improves the visible comparison behavior, but it is still constrained by source-image gamut and display conditions.",',
    'modelNote: "The current image renderer applies the Machado pre-computed deuteranomaly matrices to linear RGB and interpolates between adjacent 0.1 severity steps. Display gamut, source encoding, and the lack of an individual measurement still limit the result.",',
)
replace_once(
    "src/modeEvidence.ts",
    'note: "Primary simulation reference for red-green and blue-yellow deficiency approximations.",',
    'note: "Primary implementation reference for the deuteranomaly matrix family; the same work also provides the project\'s tritanomaly reference matrices.",',
)
replace_once(
    "src/modeEvidence.ts",
    'modelNote: "The current transform uses a linear-RGB deficiency mapping plus blue-yellow axis compression. It is a stronger comparison aid than a simple tint shift, but still not a full spectral or observer-specific simulation.",',
    'modelNote: "The current image renderer applies the Machado pre-computed tritanomaly matrices to linear RGB and interpolates between adjacent 0.1 severity steps. The reference itself treats tritanomaly with an approximate shift model, so the output remains a comparison proxy rather than a literal tritanopic observer reconstruction.",',
)
replace_once(
    "src/modeEvidence.ts",
    'caveat: "This is an image transform for comparison. It does not model all spectral or individual differences.",',
    'caveat: "This is an image transform for comparison. The Machado tritanomaly model is itself approximate and the output does not reproduce all spectral or individual differences.",',
)
replace_once(
    "src/modeEvidence.ts",
    'note: "Primary simulation reference for color-vision-deficiency matrices and severity interpolation.",',
    'note: "Primary implementation reference for the pre-computed tritanomaly matrices and adjacent-matrix severity interpolation; the source model also documents its tritan limitation.",',
)


# --- docs/methodology.md ----------------------------------------------------
methodology_anchor = '''## Central Loss spatial model
'''
methodology_insert = '''## Color-vision-deficiency image model
The Protan-like, Deutan-like, and Tritan-like image modes use the pre-computed Machado color-vision-deficiency matrix families. The uploaded sRGB image is decoded to linear RGB, the matrix for the selected renderer Strength is obtained by interpolating between the neighboring 0.1 reference steps, and the result is encoded back to sRGB for display.

This deliberately avoids adding separate hand-tuned red/green or blue/yellow compression after the published matrix. It also avoids mixing a full-severity result in gamma-encoded display space, which is not equivalent to the reference model's matrix interpolation.

The public Strength percentage is still an interaction control, not an inferred clinical measurement. The renderer uses the reference model's 0–1 parameter internally, but AsSeenBy does not know an individual viewer's measured deficiency, display calibration, adaptation state, or complete spectral environment. Tritan-like remains especially cautious because the underlying Machado tritanomaly construction is itself an approximation and is not presented here as a literal patient-specific tritanopic reconstruction.

## Central Loss spatial model
'''
replace_once("docs/methodology.md", methodology_anchor, methodology_insert)


# --- docs/limitations.md ----------------------------------------------------
replace_once(
    "docs/limitations.md",
    '- color-deficiency-like image modes are matrix-based approximations;',
    '- Protan-like / Deutan-like / Tritan-like image modes use the Machado pre-computed matrix families in linear RGB, but remain display- and source-dependent approximations rather than patient-specific reconstructions;',
)
strength_anchor = '''## Strength control limitation
'''
strength_insert = '''### Color-vision-deficiency specific limitation
For Protan-like, Deutan-like, and Tritan-like, Strength selects the 0–1 parameter used to interpolate the Machado pre-computed matrices. That improves fidelity to the cited implementation reference, but the percentage must not be read as a diagnosis or a measured severity for the person viewing the result.

The source image is ordinary sRGB, output is clipped to the displayable RGB range, display primaries are not measured per user, and individual cone fundamentals / adaptation are not supplied. The Machado tritanomaly model also has its own documented approximation boundary. These modes therefore remain comparison simulations even when the matrix implementation follows the cited reference closely.

## Strength control limitation
'''
replace_once("docs/limitations.md", strength_anchor, strength_insert)


# --- docs/modes.md ----------------------------------------------------------
replace_once(
    "docs/modes.md",
    '''### Protan-like
- class: Strong
- goal: reduced red-channel discrimination approximation
- note: not diagnostic; intended for visual comparison only

### Deutan-like
- class: Strong
- goal: reduced green-channel discrimination approximation
- note: not diagnostic; intended for visual comparison only

### Tritan-like
- class: Strong
- goal: blue-yellow discrimination shift approximation
- note: not diagnostic; intended for visual comparison only
''',
    '''### Protan-like
- class: Strong
- goal: protanomaly-style color-discrimination approximation
- image renderer: Machado pre-computed protanomaly matrices, interpolated by Strength and applied in linear RGB
- note: not diagnostic; Strength is not an individual clinical severity measurement

### Deutan-like
- class: Strong
- goal: deuteranomaly-style color-discrimination approximation
- image renderer: Machado pre-computed deuteranomaly matrices, interpolated by Strength and applied in linear RGB
- note: not diagnostic; Strength is not an individual clinical severity measurement

### Tritan-like
- class: Strong
- goal: tritanomaly-style blue-yellow discrimination approximation
- image renderer: Machado pre-computed tritanomaly matrices, interpolated by Strength and applied in linear RGB
- note: not diagnostic; the cited tritan model is itself approximate and is not a literal patient-specific tritanopia reconstruction
''',
)


# --- docs/release-polish-schedule.md ---------------------------------------
schedule = Path("docs/release-polish-schedule.md")
text = schedule.read_text()
text = text.replace(
    'Status: **Step R10 ACTIVE / Strength semantics correction / R9 evidence accuracy validated**',
    'Status: **Step R11 ACTIVE / CVD model fidelity / R10 Strength semantics production verified**',
    1,
)
start = text.index("## Step R10 — Strength semantics")
end = text.index("## Current next action", start)
r10_r11 = '''## Step R10 — Strength semantics
Status: **PASS / production verified**

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

Validation:
- R10 corrected output/build/full browser validation `34051388047` — **success**; all 9 public image modes passed Strength 0/1/40/70/100 checks, monotonic output change, Tunnel edge dominance, Central Loss center dominance, and desktop/390px image + spatial regression;
- PR #29 build `34051549838` — **success**;
- PR #29 squash-merged as `15def04f65dc91586d6bece14b466a462daf2578`;
- matching main build `34051584742` — **success**;
- first production-smoke attempt `34051584808` ran before renderer deployment propagation and exposed that the old release detector could misclassify the previous deployment as current;
- rerun of the same production smoke after propagation — **success**, confirming the R10 product behavior itself;
- PR #30 hardened release detection so a deployment is considered current only after the accepted image-mode set **and** Strength-0 identity are present;
- PR #30 build `34051905958` — **success**;
- PR #30 squash-merged as `439bf14a5a26f3d8f2fff912cfe8254e653bfe8f`;
- matching main build `34051950964` — **success**;
- R10-aware production smoke `34051951021` — **success on first attempt**.

## Step R11 — CVD model fidelity
Status: **ACTIVE — implementation / validation**

Finding:
- Protan-like / Deutan-like / Tritan-like cite Machado, Oliveira & Fernandes as the implementation anchor, and the evidence text explicitly refers to color-deficiency matrices and severity interpolation;
- the current renderer contains the published full-severity matrices, but it does not use the reference severity-matrix path at intermediate Strength values: it applies only the 1.0 matrix, adds a custom luminance rebalance, mixes the encoded result back toward Original, then adds custom red-green or blue-yellow compression;
- on a 17×17×17 controlled RGB grid, current output versus the published Machado matrix at the same Strength has mean absolute channel deltas of 9.36 / 9.61 / 9.23 for Protan / Deutan / Tritan at Strength 40, with 25–34% of grid colors differing by at least 25 in one channel;
- even at 100%, custom post-processing keeps the output from the published endpoint, with Tritan reaching a maximum channel delta of about 32.6 on the controlled grid;
- the extra post-processing has no separate source/model justification in the repository, so implementation and cited model should be brought back into alignment rather than preserving an undocumented visual exaggeration.

Implementation target:
- retain the published Machado pre-computed 0.0–1.0 matrix families for Protan-like, Deutan-like, and Tritan-like;
- interpolate between adjacent 0.1 matrices for intermediate Strength values;
- decode sRGB to linear RGB, apply the interpolated matrix, and encode back to sRGB;
- remove CVD-only custom luminance rebalance / axis-compression behavior from the three Human CVD modes;
- keep Dog-like separate: it intentionally reuses a deutan-style matrix as one component of a broader conservative canine human-display proxy and is not being redefined as a Machado human CVD mode;
- keep Model B and the non-diagnostic / non-patient-specific claim boundary; document the tritan-model limitation explicitly.

Acceptance:
- controlled browser color patches for Protan / Deutan / Tritan at Strength 10/40/70/100 agree with an independent Machado pre-computed-matrix calculation within the small tolerance required by the JPEG output path;
- Strength 0 remains exact Original through the R10 invariant;
- no custom red-green/blue-yellow post-compression is applied to the three Human CVD modes;
- Dog-like renderer behavior remains on its existing separate proxy path;
- build and full desktop/390px image + spatial browser regression remain green;
- matching main build and production smoke pass after merge before R11 is marked production verified.

'''
text = text[:start] + r10_r11 + text[end:]
text = text.replace(
    '## Current next action\nValidate the corrected 0/1/40/70/100 output curves for all 9 public image modes, then run the full image/spatial browser regression. Open a clean PR only if both gates pass.',
    '## Current next action\nValidate the R11 Protan/Deutan/Tritan browser outputs against an independent Machado matrix calculation at Strength 10/40/70/100, then run the full image/spatial browser regression. Open a clean PR only if both gates pass.',
    1,
)
schedule.write_text(text)
