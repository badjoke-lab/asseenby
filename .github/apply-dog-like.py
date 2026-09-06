from pathlib import Path


def replace(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"anchor not found in {path}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1))


# --- Spatial renderer -------------------------------------------------------
spatial = Path("src/SpatialPage.tsx")
text = spatial.read_text()
text = text.replace(
    'type SpatialMode = "normal" | "tunnel" | "central_loss" | "night" | "cataract";',
    'type SpatialMode = "normal" | "tunnel" | "central_loss" | "night" | "dog" | "cataract";',
    1,
)

dog_shader = r'''const DOG_LIKE_SHADER = {
  uniforms: {
    tDiffuse: { value: null },
    resolution: { value: new THREE.Vector2(1, 1) },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform vec2 resolution;
    varying vec2 vUv;

    void main() {
      vec2 px = 1.0 / max(resolution, vec2(1.0));
      float blurRadius = clamp(resolution.y / 420.0, 0.8, 2.8);
      vec3 source = texture2D(tDiffuse, vUv).rgb;

      vec3 soft = source * 0.44;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * blurRadius, 0.0)).rgb * 0.14;
      soft += texture2D(tDiffuse, vUv - vec2(px.x * blurRadius, 0.0)).rgb * 0.14;
      soft += texture2D(tDiffuse, vUv + vec2(0.0, px.y * blurRadius)).rgb * 0.14;
      soft += texture2D(tDiffuse, vUv - vec2(0.0, px.y * blurRadius)).rgb * 0.14;

      // Human-display translation of a simplified two-channel visible-range model.
      // Standard RGB cannot reconstruct canine cone catches for arbitrary real spectra.
      float longChannel = soft.r * 0.56 + soft.g * 0.44;
      float shortChannel = soft.r * 0.04 + soft.g * 0.13 + soft.b * 0.83;
      vec3 dichromatic = vec3(
        longChannel * 0.84 + shortChannel * 0.03,
        longChannel * 0.72 + shortChannel * 0.18,
        shortChannel * 0.86 + longChannel * 0.14
      );

      float sourceLuma = dot(soft, vec3(0.2126, 0.7152, 0.0722));
      float mappedLuma = max(0.02, dot(dichromatic, vec3(0.2126, 0.7152, 0.0722)));
      dichromatic *= clamp((sourceLuma + 0.025) / mappedLuma, 0.72, 1.32);
      vec3 reducedContrast = vec3(0.055) + (dichromatic - vec3(0.055)) * 0.92;

      gl_FragColor = vec4(clamp(reducedContrast, 0.0, 1.0), 1.0);
    }
  `,
};

'''
anchor = "const CATARACT_SHADER = {"
if anchor not in text:
    raise SystemExit("cataract shader anchor missing")
text = text.replace(anchor, dog_shader + anchor, 1)

repls = [
    (
        '    let cataractPass: ShaderPass | null = null;\n    let nightPass: ShaderPass | null = null;\n    let bloomPass: UnrealBloomPass | null = null;',
        '    let cataractPass: ShaderPass | null = null;\n    let nightPass: ShaderPass | null = null;\n    let dogPass: ShaderPass | null = null;\n    let bloomPass: UnrealBloomPass | null = null;',
    ),
    (
        '      nightPass = new ShaderPass(NIGHT_LOW_LIGHT_SHADER);\n      nightPass.enabled = false;\n      composer.addPass(nightPass);\n\n      centralLossPass = new ShaderPass(CENTRAL_LOSS_SHADER);',
        '      nightPass = new ShaderPass(NIGHT_LOW_LIGHT_SHADER);\n      nightPass.enabled = false;\n      composer.addPass(nightPass);\n\n      dogPass = new ShaderPass(DOG_LIKE_SHADER);\n      dogPass.enabled = false;\n      composer.addPass(dogPass);\n\n      centralLossPass = new ShaderPass(CENTRAL_LOSS_SHADER);',
    ),
    (
        '        if (nightPass) nightPass.enabled = nextMode === "night";\n        if (centralLossPass) centralLossPass.enabled = nextMode === "central_loss";',
        '        if (nightPass) nightPass.enabled = nextMode === "night";\n        if (dogPass) dogPass.enabled = nextMode === "dog";\n        if (centralLossPass) centralLossPass.enabled = nextMode === "central_loss";',
    ),
    (
        '        if (!renderer || !composer || !tunnelPass || !centralLossPass || !nightPass || !cataractPass) return;',
        '        if (!renderer || !composer || !tunnelPass || !centralLossPass || !nightPass || !dogPass || !cataractPass) return;',
    ),
    (
        '        (nightPass.uniforms.resolution.value as THREE.Vector2).set(width, height);\n        (cataractPass.uniforms.resolution.value as THREE.Vector2).set(width, height);',
        '        (nightPass.uniforms.resolution.value as THREE.Vector2).set(width, height);\n        (dogPass.uniforms.resolution.value as THREE.Vector2).set(width, height);\n        (cataractPass.uniforms.resolution.value as THREE.Vector2).set(width, height);',
    ),
    (
        '        nightPass?.material.dispose();\n        cataractPass?.material.dispose();',
        '        nightPass?.material.dispose();\n        dogPass?.material.dispose();\n        cataractPass?.material.dispose();',
    ),
    (
        '      nightPass?.material.dispose();\n      cataractPass?.material.dispose();',
        '      nightPass?.material.dispose();\n      dogPass?.material.dispose();\n      cataractPass?.material.dispose();',
    ),
]
for old, new in repls:
    if old not in text:
        raise SystemExit(f"SpatialPage anchor missing: {old[:100]!r}")
    text = text.replace(old, new, 1)

old_desc = '''  const modeDescription = mode === "normal"
    ? "Baseline scene with no perception simulation."
    : mode === "tunnel"
      ? "Live screen-relative peripheral field loss. Look around to see how objects outside the center become harder to notice."
      : mode === "central_loss"
        ? "Live screen-relative central field loss. Center a shop sign, window, lamp, or other detail, then look elsewhere to see the disrupted region stay with straight-ahead vision."
        : mode === "night"
          ? "Luminance-dependent low-light proxy. Darker scene regions lose more color, contrast, and fine detail while brighter shopfronts and lamps remain more available. It does not model calibrated scotopic luminance or dark-adaptation time."
          : "Scene-aware haze, softness, lower contrast, warming, and bright-source glare. Turn toward bright shopfronts or streetlights, then toward the dark sky to compare.";'''
new_desc = '''  const modeDescription = mode === "normal"
    ? "Baseline scene with no perception simulation."
    : mode === "tunnel"
      ? "Live screen-relative peripheral field loss. Look around to see how objects outside the center become harder to notice."
      : mode === "central_loss"
        ? "Live screen-relative central field loss. Center a shop sign, window, lamp, or other detail, then look elsewhere to see the disrupted region stay with straight-ahead vision."
        : mode === "night"
          ? "Luminance-dependent low-light proxy. Darker scene regions lose more color, contrast, and fine detail while brighter shopfronts and lamps remain more available. It does not model calibrated scotopic luminance or dark-adaptation time."
          : mode === "dog"
            ? "Visible-range Dog-like proxy. It compresses red/green distinctions toward a two-channel blue/yellow-like display translation and softens fine detail. It does not reproduce canine spectral catches, breed-dependent field of view, motion processing, or low-light advantages."
            : "Scene-aware haze, softness, lower contrast, warming, and bright-source glare. Turn toward bright shopfronts or streetlights, then toward the dark sky to compare.";'''
if old_desc not in text:
    raise SystemExit("mode description anchor missing")
text = text.replace(old_desc, new_desc, 1)

button_anchor = '<button type="button" className={mode === "night" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "night"} onClick={() => setMode("night")}>Night / Low Light</button>\n        <button type="button" className={mode === "cataract"'
button_replacement = '<button type="button" className={mode === "night" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "night"} onClick={() => setMode("night")}>Night / Low Light</button>\n        <button type="button" className={mode === "dog" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "dog"} onClick={() => setMode("dog")}>Dog-like</button>\n        <button type="button" className={mode === "cataract"'
if button_anchor not in text:
    raise SystemExit("dog button anchor missing")
text = text.replace(button_anchor, button_replacement, 1)

note_old = "Tunnel Vision and Central Loss are generic field-loss models; Night / Low Light is a luminance-dependent low-light proxy; Cataract-like is a generic scene-dependent glare and haze model. None are an individual's measured visual reconstruction, and the low-light mode does not infer physical scene luminance from the tone-mapped panorama."
note_new = "Tunnel Vision and Central Loss are generic field-loss models; Night / Low Light is a luminance-dependent low-light proxy; Dog-like is a visible-range dichromatic/acuity comparison proxy; Cataract-like is a generic scene-dependent glare and haze model. None are an individual's or animal's literal visual reconstruction. The RGB panorama cannot recover full canine spectral information, and the low-light mode does not infer physical scene luminance."
if note_old not in text:
    raise SystemExit("spatial comparison note anchor missing")
text = text.replace(note_old, note_new, 1)
spatial.write_text(text)

# --- Spatial evidence -------------------------------------------------------
evidence = Path("src/spatialEvidence.ts")
text = evidence.read_text()
text = text.replace(
    'type SpatialEvidenceMode = "tunnel" | "central_loss" | "night" | "cataract";',
    'type SpatialEvidenceMode = "tunnel" | "central_loss" | "night" | "dog" | "cataract";',
    1,
)
anchor = '''  return {
    ...base,
    modelScore: "C",
    modelNote: "The spatial renderer samples the live rendered frame, gates light spread by actual high-luminance scene pixels, and combines that view-dependent glare with optical softness, lower contrast, slight desaturation, warming, and a veil component. Headlights, streetlights, and signals therefore spread more strongly when they are actually in view, while dark directions do not receive the same glare. This remains a generic browser model rather than a validated lens-scatter reconstruction.",'''
dog_branch = '''  if (modeKey === "dog") {
    return {
      ...base,
      modelScore: "C",
      modelNote: "The spatial Dog-like renderer applies a simplified two-channel visible-range color translation plus mild angularly scaled softening to the live 360° view. It is grounded in strong evidence for canine dichromacy and lower visual acuity than humans, but a standard RGB panorama cannot reconstruct canine cone catches for arbitrary spectra and the blur is not a calibrated individual-dog acuity model.",
      caveat: "Dog vision varies across individuals and breeds. This mode does not model breed-dependent field of view, retinal topography, motion sensitivity, tapetal/rod-mediated low-light advantages, spectral metamerism, or neural interpretation. It is a human-display comparison proxy, not literal canine qualia.",
      lastReviewed: SPATIAL_REVIEWED_ON,
    };
  }

'''
if anchor not in text:
    raise SystemExit("spatial evidence return anchor missing")
text = text.replace(anchor, dog_branch + anchor, 1)
evidence.write_text(text)

# --- Dog evidence review ----------------------------------------------------
mode_evidence = Path("src/modeEvidence.ts")
text = mode_evidence.read_text()
old = '''    supportingSources: [
      {
        title: "Are dogs red–green colour blind? — PMC",
        url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC5717654/",
        kind: "paper",
        note: "Behavioral evidence that dogs show a response pattern similar to red-green color-blind human observers.",
      },
    ],
    lastReviewed: REVIEWED_ON,
  },
  cat:'''
new = '''    supportingSources: [
      {
        title: "Are dogs red–green colour blind? — PMC",
        url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC5717654/",
        kind: "paper",
        note: "Behavioral evidence that dogs show a response pattern similar to red-green color-blind human observers.",
      },
      {
        title: "What do dogs (Canis familiaris) see? A review of vision in dogs",
        url: "https://pubmed.ncbi.nlm.nih.gov/29143248/",
        kind: "paper",
        note: "Review covering canine light sensitivity, visual perspective, acuity, form perception, and color vision, and emphasizing remaining uncertainty in complete canine visual processing.",
      },
      {
        title: "High visual acuity revealed in dogs",
        url: "https://pubmed.ncbi.nlm.nih.gov/29206864/",
        kind: "paper",
        note: "Behavioral measurements show substantial individual variation but consistently lower spatial acuity than human participants under comparable bright and dim conditions.",
      },
    ],
    lastReviewed: "2026-09-06",
  },
  cat:'''
if old not in text:
    raise SystemExit("dog evidence anchor missing")
text = text.replace(old, new, 1)
mode_evidence.write_text(text)

# --- Browser regression -----------------------------------------------------
check = Path(".github/spatial-browser-check.mjs")
text = check.read_text()
repls = [
    (
        'await assertMode(desktop, "Night / Low Light");\nawait desktop.screenshot({ path: `${outDir}/desktop-night-forward.png`, fullPage: true });\nawait assertMode(desktop, "Normal");',
        'await assertMode(desktop, "Night / Low Light");\nawait desktop.screenshot({ path: `${outDir}/desktop-night-forward.png`, fullPage: true });\nawait assertMode(desktop, "Dog-like");\nawait desktop.screenshot({ path: `${outDir}/desktop-dog-forward.png`, fullPage: true });\nawait assertMode(desktop, "Normal");',
    ),
    (
        'await assertMode(desktop, "Night / Low Light");\nawait desktop.screenshot({ path: `${outDir}/desktop-night-turned.png`, fullPage: true });\nawait assertMode(desktop, "Normal");',
        'await assertMode(desktop, "Night / Low Light");\nawait desktop.screenshot({ path: `${outDir}/desktop-night-turned.png`, fullPage: true });\nawait assertMode(desktop, "Dog-like");\nawait desktop.screenshot({ path: `${outDir}/desktop-dog-turned.png`, fullPage: true });\nawait assertMode(desktop, "Normal");',
    ),
    (
        'await assertMode(mobile, "Night / Low Light");\nawait mobile.screenshot({ path: `${outDir}/mobile-night-turned.png`, fullPage: true });\nawait assertMode(mobile, "Tunnel Vision");',
        'await assertMode(mobile, "Night / Low Light");\nawait mobile.screenshot({ path: `${outDir}/mobile-night-turned.png`, fullPage: true });\nawait assertMode(mobile, "Dog-like");\nawait mobile.screenshot({ path: `${outDir}/mobile-dog-turned.png`, fullPage: true });\nawait assertMode(mobile, "Tunnel Vision");',
    ),
]
for old, new in repls:
    if old not in text:
        raise SystemExit(f"browser anchor missing: {old[:100]!r}")
    text = text.replace(old, new, 1)
check.write_text(text)

# --- Documentation ----------------------------------------------------------
replace(
    "AGENTS.md",
    "- The image experience remains `Compare image`; the Three.js experience remains `Explore 3D`.",
    "- The image experience remains `Compare image`; the Three.js experience remains `Explore spatial`.",
)
replace(
    "AGENTS.md",
    "- Central Loss and the photographic 360° reference scene are accepted and merged. The current expansion target is `Night / Low Light`; do not begin Dog-like, Cat-like, Bird-like, or Bee-like until its rendered acceptance gate passes or it is explicitly rejected.\n- Night / Low Light must respond to luminance differences in the current rendered view rather than acting as a uniform dark tint. Darker regions should lose more color, contrast, and fine detail while brighter regions remain comparatively available.\n- The current panorama is tone-mapped RGB, not calibrated radiometric data. Do not claim physical scotopic/mesopic luminance, dark-adaptation timing, pupil response, or full rod/cone spectral reproduction from it.",
    "- Central Loss, Night / Low Light, and the photographic 360° reference scene are accepted and merged. The current expansion target is `Dog-like`; do not begin Cat-like, Bird-like, or Bee-like until its rendered acceptance gate passes or it is explicitly rejected.\n- Dog-like must preserve the same camera and use a conservative visible-range dichromatic + acuity proxy. Do not claim that RGB can reconstruct canine cone catches for arbitrary spectra, or that the renderer models breed-dependent field of view, motion processing, tapetal/rod low-light advantages, or literal canine qualia.\n- The current panorama is tone-mapped RGB. It can support a human-display visible-range comparison, not complete species-specific spectral reconstruction.",
)

roadmap = Path("docs/roadmap.md")
text = roadmap.read_text()
start = text.index("## Spatial expansion — Night / Low Light")
end = text.index("## Ordered next spatial candidates")
text = text[:start] + '''## Spatial expansion — Dog-like
Status: **active**

Goal:
Add a conservative visible-range canine comparison to the live 360° scene using two well-supported differences from human vision: dichromatic color discrimination and lower spatial acuity.

Required characteristics:
- compress red/green distinctions into a human-display two-channel translation while keeping blue/yellow-like distinctions more available;
- soften fine detail without claiming a calibrated acuity value for an individual dog;
- preserve exact camera position, direction, scene and field of view when switching modes;
- explicitly state that standard RGB cannot reconstruct canine cone catches for arbitrary real spectra;
- do not add breed-dependent field-of-view claims, motion sensitivity, tapetal/rod low-light advantages, or neural interpretation without source data and a separate validated model;
- renderer-specific Model assessment remains separate from the 2D transform;
- desktop/mobile rendered acceptance is required before merge.

''' + text[end:]
text = text.replace(
    "After the active Night / Low Light phase:\n1. Dog-like;\n2. Cat-like;\n3. Bird-like separate evaluation;\n4. Bee-like only with additional UV-reflectance scene data.",
    "After the active Dog-like phase:\n1. Cat-like;\n2. Bird-like separate evaluation;\n3. Bee-like only with additional UV-reflectance scene data.",
    1,
)
text = text.replace(
    "1. define the Night / Low Light scientific and source-data boundary;\n2. implement the luminance-dependent spatial pass;\n3. run build plus desktop/mobile browser regression;\n4. inspect same-camera Normal / Night comparisons across bright and dark view directions;\n5. accept, correct, or reject the spatial mode;\n6. begin Dog-like only after Night / Low Light is resolved.",
    "1. define the Dog-like spectral/acuity boundary for RGB input;\n2. implement the conservative dichromatic + soft-detail spatial pass;\n3. run build plus desktop/mobile browser regression;\n4. inspect same-camera Normal / Dog-like comparisons across multiple view directions;\n5. verify red/green compression and detail loss are visible without overclaiming canine perception;\n6. accept, correct, or reject Dog-like before Cat-like begins.",
    1,
)
roadmap.write_text(text)

spec = Path("docs/spatial-pilot-spec.md")
text = spec.read_text()
text = text.replace(
    "Current expansion target:\n4. **Night / Low Light** — the rendered comparison should respond to luminance differences in the current view, with darker regions losing more color, contrast, and fine detail than brighter regions, without claiming calibrated scotopic photometry.",
    "Accepted post-pilot examples:\n4. **Night / Low Light** — the rendered comparison responds to relative displayed luminance in the current view while remaining explicitly non-calibrated.\n\nCurrent expansion target:\n5. **Dog-like** — a visible-range human-display proxy for canine dichromacy plus lower spatial acuity, with no claim of full canine spectral, field-of-view, motion, low-light, or neural reconstruction.",
    1,
)
dog_section = '''## Post-pilot expansion — Dog-like

### Purpose
Let users scan the same 360° scene through a conservative canine-visible-range comparison grounded in two relatively well-supported differences from human vision: dichromatic color discrimination and lower spatial acuity.

### Source-data boundary
The Hansaplatz panorama is standard tone-mapped RGB. RGB values are display primaries, not spectral reflectance/radiance measurements. Different real spectra can map to the same RGB value for a human camera/display while producing different catches in another species' photoreceptors.

Therefore the current Dog-like spatial mode may provide a **human-display translation** of broad canine dichromacy, but must not claim to reconstruct exact canine cone catches or literal color qualia.

### Requirements
- compress red/green distinctions into a conservative two-channel visible-range display translation;
- keep blue-versus-yellow-like distinctions comparatively available;
- reduce fine-detail availability with mild angularly scaled softening;
- preserve exact camera position, direction and source scene on mode switching;
- preserve the same camera field of view rather than inventing one breed's anatomy as universal;
- do not add motion sensitivity because the reference scene is static;
- do not add tapetal/rod-mediated low-light enhancement because the tone-mapped RGB panorama lacks the required physiological/radiometric state;
- do not present the output as what every dog literally sees.

### Why this is spatial
The user can actively scan one coherent environment and compare how signs, foliage, shop colors, lamps, pavement and fine architectural detail remain or collapse across view directions. The spatial value is persistent same-scene exploration, not a claim that the shader models every spatial property of canine vision.

### Evidence / model rule
- canine dichromacy has strong behavioral and photopigment support;
- canine acuity is measurably lower than human acuity in comparative studies, but varies materially between dogs and methods;
- keep the spatial Model score at **C** because the RGB-to-canine translation and blur remain simplified display models;
- maintain a clear distinction between Evidence A for the broad phenomenon and Model C for this renderer.

'''
if "## Camera and interaction\n" not in text:
    raise SystemExit("spec camera anchor missing")
text = text.replace("## Camera and interaction\n", dog_section + "## Camera and interaction\n", 1)
text += '''
## Dog-like acceptance gate
Dog-like is successful only if all of the following are true:
1. Existing Compare image behavior remains unchanged.
2. Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like remain functional.
3. Dog-like can be selected without camera reset or field-of-view mutation.
4. Red/green distinctions are visibly compressed while blue/yellow-like distinctions remain comparatively available.
5. Fine-detail loss is visible but does not turn the scene into indiscriminate heavy blur.
6. Same-camera Normal / Dog-like captures show that only the perception renderer changed.
7. Forward and turned views both remain coherent and useful for comparison.
8. Evidence and limitation text explicitly state the RGB/spectral-metamer boundary and excluded canine capabilities.
9. Desktop and 390px mobile remain usable with no horizontal overflow or captured page/console errors.
10. `npm run build` passes.
11. Rendered review shows explanatory value beyond a generic deuteranopia filter or arbitrary color tint.

If criterion 4, 5, 8, or 11 fails, revise or reject the spatial mode rather than merging it because the shader merely runs.
'''
spec.write_text(text)

methodology = Path("docs/methodology.md")
text = methodology.read_text()
text = text.replace(
    "Accepted spatial modes:\n- Normal;\n- Tunnel Vision;\n- Central Loss;\n- Cataract-like.\n\nCurrent expansion target:\n- Night / Low Light.",
    "Accepted spatial modes:\n- Normal;\n- Tunnel Vision;\n- Central Loss;\n- Night / Low Light;\n- Cataract-like.\n\nCurrent expansion target:\n- Dog-like.",
    1,
)
dog_method = '''## Dog-like spatial model
The active Dog-like target combines a simplified visible-range dichromatic translation with mild loss of fine detail. The phenomenon basis is stronger than the renderer: canine dichromacy and lower acuity are supported by behavioral/physiological literature, but a standard RGB panorama does not contain the spectral information needed to calculate exact canine photoreceptor catches for arbitrary real-world materials and lights.

For that reason the renderer keeps Evidence and Model separate: the broad canine visual differences can retain strong evidence while the spatial implementation remains Model C. Field of view, motion processing, tapetal/rod low-light advantages and neural interpretation are intentionally excluded from this phase.

'''
text = text.replace("## Evidence display model\n", dog_method + "## Evidence display model\n", 1)
methodology.write_text(text)

limitations = Path("docs/limitations.md")
text = limitations.read_text()
old = '''Examples:
- bee mode does not reproduce ultraviolet vision;
- bird-like mode does not reproduce ultraviolet response or full avian perception;
- dog and cat modes are simplified visible-range approximations.

A future spatial scene does not create missing UV information automatically.'''
new = '''Examples:
- bee mode does not reproduce ultraviolet vision;
- bird-like mode does not reproduce ultraviolet response or full avian perception;
- dog and cat modes are simplified visible-range approximations.

### Dog-like specific limitation
Canine dichromacy is well supported, but a conventional RGB panorama cannot recover the original scene spectra or exact canine cone catches. The spatial Dog-like output therefore translates broad two-channel color relationships onto a human RGB display and adds mild non-calibrated detail softening.

It does not model breed-dependent field of view, retinal topography, motion sensitivity, tapetal/rod-mediated low-light advantages, spectral metamerism, or neural interpretation. It should not be read as literal canine color qualia or as one universal view shared by all dogs.

A future spatial scene does not create missing UV information automatically.'''
if old not in text:
    raise SystemExit("animal limitation anchor missing")
text = text.replace(old, new, 1)
limitations.write_text(text)

ui = Path("docs/ui-spec.md")
text = ui.read_text()
text = text.replace(
    "- Central Loss\n- Night / Low Light\n- Cataract-like\n\nNight / Low Light is the active expansion target. Its control is included only with the live luminance-dependent implementation, not as an unimplemented placeholder.",
    "- Central Loss\n- Night / Low Light\n- Dog-like\n- Cataract-like\n\nDog-like is the active expansion target. Its control is included only with the live visible-range dichromatic/acuity implementation, not as an unimplemented placeholder.",
    1,
)
dog_ui = '''## Dog-like UI behavior
When Dog-like is selected:
- keep the current camera position, direction, field of view and source scene;
- explain that the mode is a visible-range human-display proxy for canine dichromacy plus lower fine-detail resolution;
- do not describe the output as exact canine cone catches, literal canine color experience, or a breed-independent complete visual system;
- make the RGB spectral-data limitation and excluded field-of-view/motion/low-light claims available in the evidence panel.

'''
text = text.replace("## Labels\n", dog_ui + "## Labels\n", 1)
ui.write_text(text)

modes = Path("docs/modes.md")
text = modes.read_text()
text = text.replace(
    "### Dog-like\n- class: Estimated\n- goal: visible-range dog color approximation with modest softening\n- spatial status: planned after human-condition spatial modes",
    "### Dog-like\n- class: Estimated\n- goal: visible-range dog color approximation with modest softening\n- spatial status: active post-pilot expansion target\n- spatial renderer target: conservative two-channel visible-range translation plus mild angularly scaled fine-detail loss\n- spatial limitation: standard RGB cannot reconstruct exact canine cone catches; no breed-dependent field of view, motion sensitivity, tapetal/rod low-light advantage, or literal canine qualia is modeled",
    1,
)
text = text.replace(
    "### Night / Low Light\n- class: Estimated\n- goal: low-light viewing approximation\n- spatial status: active post-pilot expansion target",
    "### Night / Low Light\n- class: Estimated\n- goal: low-light viewing approximation\n- spatial status: accepted post-pilot mode",
    1,
)
modes.write_text(text)

schedule = Path("docs/spatial-pilot-schedule.md")
text = schedule.read_text()
start = text.index("## Step 12 — Night / Low Light")
text = text[:start] + '''## Step 12 — Night / Low Light
Status: **PASS / accepted / merged**

Rendered-review browser run `34009009894` passed and its Normal/Night forward, turned and 390px mobile captures were manually accepted. Final clean-head PR build `34009195003` and browser regression `34009192584` passed. PR #4 was squash-merged to main as `f7d57d3817e273e0ce2f63973f049b1a68cc0085`; post-merge main build `34009285466` passed.

The accepted model remains a relative displayed-luminance proxy with spatial Model C. It does not claim calibrated scotopic/mesopic reconstruction or dark-adaptation timing.

## Step 13 — Dog-like evidence boundary and renderer candidate
Status: **evidence boundary complete / implementation candidate awaiting rendered review**

Evidence boundary:
- behavioral and photopigment studies strongly support canine dichromatic color vision;
- comparative studies support lower canine spatial acuity than human acuity, with meaningful individual and methodological variation;
- a standard RGB panorama cannot reconstruct exact canine cone catches for arbitrary spectra;
- breed-dependent visual field, motion processing, tapetal/rod low-light advantages and neural interpretation are excluded from this phase.

Renderer candidate:
- human-display two-channel translation compresses red/green distinctions while keeping blue/yellow-like distinctions comparatively available;
- mild angularly scaled softening reduces fine detail without claiming calibrated acuity;
- camera position, direction, field of view and source panorama remain unchanged;
- spatial Model remains C pending rendered acceptance.

Rendered gate:
- compare identical-camera Normal vs Dog-like forward and turned views;
- verify red/green compression on signs, foliage and colored lights without a generic arbitrary tint;
- verify fine-detail reduction is visible but restrained;
- verify accepted spatial modes and image comparison remain unchanged;
- verify 390px mobile, no overflow, and no captured page/console errors;
- accept, revise, or reject before beginning Cat-like.

## Ordered next spatial candidates
1. Cat-like
2. Bird-like as a separate evaluation
3. Bee-like only with additional UV-reflectance scene data

## Current next action
Run build and the existing desktop / 390px Chromium capture on the Dog-like candidate. Inspect identical-camera Normal/Dog-like forward and turned views, then either correct the renderer or mark Step 13 accepted. Do not begin Cat-like yet.
'''
schedule.write_text(text)
