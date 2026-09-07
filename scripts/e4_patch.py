from pathlib import Path


def replace(path, old, new):
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"missing patch target in {path}: {old[:100]!r}")
    p.write_text(text.replace(old, new, 1))

# SpatialPage: expose the accepted Human Vision set on Night Intersection and keep Dog-like Photo Reference-only.
p = Path("src/SpatialPage.tsx")
text = p.read_text()
text = text.replace('import { MODES } from "./modes";', 'import { MODES, type ModeDef } from "./modes";')
text = text.replace('''const VISION_DESCRIPTIONS: Record<SpatialVisionMode, string> = {''', '''const GEOMETRY_HUMAN_VISIONS = new Set<SpatialVisionMode>(["normal", "tunnel", "central_loss", "night", "cataract"]);

const SPATIAL_EVIDENCE_MODE_DEFS: Partial<Record<SpatialVisionMode, ModeDef>> = {
  night: {
    key: "night",
    label: "Night / Low Light",
    category: "Human",
    confidence: "Estimated",
    note: "Luminance-dependent low-light spatial comparison proxy.",
  },
};

const VISION_DESCRIPTIONS: Record<SpatialVisionMode, string> = {''')
text = text.replace('''  const evidenceModeKey = vision === "normal" ? null : vision;
  const evidenceMode = evidenceModeKey ? MODES.find((item) => item.key === evidenceModeKey) ?? null : null;''', '''  const evidenceModeKey = vision === "normal" ? null : vision;
  const evidenceMode = evidenceModeKey
    ? MODES.find((item) => item.key === evidenceModeKey) ?? SPATIAL_EVIDENCE_MODE_DEFS[evidenceModeKey] ?? null
    : null;''')
text = text.replace('''                <strong>E3 movement boundary:</strong> the Human observer can move through the authored Night Intersection walking area with collision-aware ground navigation while keeping a 1.6 m reference eye height. This is a generic comparison viewpoint, not a claim about every person. Night Intersection intentionally exposes Normal only until Human Vision integration is reviewed in E4.''', '''                <strong>Human geometry comparison:</strong> the 1.6 m Human observer keeps the same bounded ground position, look direction, and FOV while Vision switches among Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like. The modes remain generic research simulations rather than patient-specific reconstructions.''')
text = text.replace('''              if (nextSceneId === "night-intersection") setVision("normal");''', '''              if (nextSceneId === "night-intersection" && vision === "dog") setVision("normal");''')
text = text.replace('''  const visibleVisions = isGeometryScene ? SPATIAL_VISIONS.filter((item) => item.id === "normal") : SPATIAL_VISIONS;''', '''  const visibleVisions = isGeometryScene ? SPATIAL_VISIONS.filter((item) => GEOMETRY_HUMAN_VISIONS.has(item.id)) : SPATIAL_VISIONS;''')
text = text.replace('''        {isGeometryScene ? (
          <p className="spatial-mode-availability">Geometry Vision integration remains deferred to E4. E3 validates Human movement in Normal.</p>
        ) : null}''', '''        {isGeometryScene ? (
          <p className="spatial-mode-availability">Human geometry Vision uses the same live rendered scene and preserves the current observer/camera state. Dog-like remains a separate Photo Reference Vision proxy until the Dog observer phases.</p>
        ) : null}''')
text = text.replace('''          ? "Night Intersection supports bounded Human ground movement. Walk with W/A/S/D on desktop or the compact mobile controls, use Shift for faster desktop movement, drag to look around, and use Reset observer or R to return to the canonical 1.6 m Human start."''', '''          ? "Night Intersection supports bounded Human ground movement plus same-state Human Vision switching. Walk with W/A/S/D on desktop or the compact mobile controls, use Shift for faster desktop movement, drag to look around, and use Reset observer or R to return to the canonical 1.6 m Human start without changing Vision."''')
p.write_text(text)

# Spatial evidence: describe the renderer across both live geometry and the photographic reference.
p = Path("src/spatialEvidence.ts")
text = p.read_text().replace('const SPATIAL_REVIEWED_ON = "2026-09-06";', 'const SPATIAL_REVIEWED_ON = "2026-09-08";')
text = text.replace('''      modelNote: "The spatial Night / Low Light renderer uses displayed scene luminance from the current rendered view to increase desaturation, contrast loss, and fine-detail loss in darker regions while leaving brighter sources more available. Because the 360° panorama is a tone-mapped RGB photograph rather than calibrated radiometric scene data, this is a luminance-dependent communication model, not a physical scotopic or mesopic reconstruction.",''', '''      modelNote: "The spatial Night / Low Light renderer samples displayed luminance from the current live rendered frame, increasing desaturation, contrast loss, and fine-detail loss in darker regions while leaving brighter sources more available. On Night Intersection that frame reflects authored geometry, materials, lights, visibility, and occlusion; on the 360° Photo Reference it reflects the tone-mapped RGB photograph. Neither source is calibrated radiometric scene data, so this remains a luminance-dependent communication model rather than a physical scotopic or mesopic reconstruction.",''')
text = text.replace('''    modelNote: "The spatial renderer samples the live rendered frame, gates light spread by actual high-luminance scene pixels, and combines that view-dependent glare with optical softness, lower contrast, slight desaturation, warming, and a veil component. Headlights, streetlights, and signals therefore spread more strongly when they are actually in view, while dark directions do not receive the same glare. This remains a generic browser model rather than a validated lens-scatter reconstruction.",''', '''    modelNote: "The spatial renderer samples the live rendered frame, gates light spread by actual high-luminance pixels, and combines that view-dependent glare with optical softness, lower contrast, slight desaturation, warming, and a veil component. On Night Intersection, visible practical/emissive sources and geometry occlusion therefore affect the pixels that can drive glare; the Photo Reference uses its photographed highlights. This remains a generic browser model without calibrated point-spread, lens-scatter, or patient-specific optical measurements.",''')
p.write_text(text)

# UI spec: make scene-specific Vision availability explicit.
p = Path("docs/ui-spec.md")
text = p.read_text()
text = text.replace('''Current 3D mode controls:
- Normal
- Tunnel Vision
- Central Loss
- Night / Low Light
- Dog-like
- Cataract-like

Dog-like is accepted and public.''', '''Current Night Intersection × Human Vision controls:
- Normal
- Tunnel Vision
- Central Loss
- Night / Low Light
- Cataract-like

The 360° Photo Reference also exposes Dog-like as a Human-height Vision proxy. Dog-like is accepted and public on that reference scene, but it is not part of the E4 Human geometry Vision set and does not imply a Dog observer.''')
p.write_text(text)

# Methodology: synchronize the current E4 geometry state.
p = Path("docs/methodology.md")
text = p.read_text()
old = '''## Explore 3D implementation approach
- Three.js runs browser-side and remains separate from the Canvas 2D image transform engine;
- the runtime is organized into explicit **Scene / Observer / Vision** layers;
- the current public Scene is the Hansaplatz `360° Photo Reference`, retained as a fixed-position photographic reference rather than the capability ceiling of Explore 3D;
- the current Photo Reference Observer is Human and look-only because the panorama contains no geometry for translation/parallax; this does not claim that bounded Human movement is already implemented;
- Vision is independent from Observer state: changing Vision preserves Scene, Observer, camera position, direction and FOV;
- geometry scenes may introduce translation, depth, collision, authored lighting, observer height and reachable-space differences in their scheduled phases;'''
new = '''## Explore 3D implementation approach
- Three.js runs browser-side and remains separate from the Canvas 2D image transform engine;
- the runtime is organized into explicit **Scene / Observer / Vision** layers;
- the current default public Scene is the geometry-based `Night Intersection`; Hansaplatz remains separately available as the fixed-position `360° Photo Reference`;
- the Night Intersection Human observer uses a 1.6 m reference eye height with bounded collision-aware ground movement, while the Photo Reference Human observer remains look-only because the panorama contains no translation/parallax depth;
- Vision is independent from Observer state: changing Vision preserves Scene, Observer, camera position, direction and FOV;
- Night Intersection Human Vision currently includes Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like; Dog-like remains a separate Photo Reference Vision proxy until Dog observer work;
- Tunnel/Central use live view-relative field position, Night uses luminance from the current rendered frame, and Cataract-like gates glare from visible high-luminance rendered pixels, so the geometry scene's lighting/visibility/occlusion can influence those live inputs without turning them into calibrated biological reconstructions;'''
if old not in text:
    raise SystemExit("methodology current Explore 3D block not found")
text = text.replace(old, new, 1)
p.write_text(text)

# Limitations: broaden the low-light source statement beyond the old panorama-only wording.
p = Path("docs/limitations.md")
text = p.read_text()
text = text.replace('''The current spatial Night / Low Light mode remains because it can at least use relative brightness differences in the rendered panorama, but the source is still a tone-mapped RGB photograph rather than calibrated luminance or spectral data.

It therefore does not reproduce a validated scotopic/mesopic observer, dark-adaptation timing, pupil dynamics, complete rod/cone spectral response, or a specific person's night-vision impairment. It is a luminance-dependent comparison proxy: dark regions are made less informative relative to bright regions so users can inspect the consequence across one fixed scene.''', '''The current spatial Night / Low Light mode remains because it uses relative brightness differences in the current live rendered frame. On Night Intersection those pixels come from authored geometry, materials and lights after the renderer's tone mapping; on the 360° Photo Reference they come from the tone-mapped RGB photograph. Neither path supplies calibrated luminance or spectral radiance.

It therefore does not reproduce a validated scotopic/mesopic observer, dark-adaptation timing, pupil dynamics, complete rod/cone spectral response, or a specific person's night-vision impairment. It is a luminance-dependent comparison proxy: darker rendered regions are made less informative relative to bright regions while the observer scans the same scene.''')
text = text.replace('''- spatial Cataract-like remains generic unless future work accepts validated individual optical measurements.''', '''- spatial Cataract-like remains generic even when Night Intersection's visible lights and geometry occlusion determine which rendered bright pixels drive the glare proxy; no calibrated lens scatter or individual optical measurements are supplied.''')
p.write_text(text)

# Modes: record geometry integration rather than pilot-only status.
p = Path("docs/modes.md")
text = p.read_text()
text = text.replace('- spatial status: accepted initial pilot mode\n- spatial renderer: scene-dependent simulation using live rendered high-luminance information so bright sources can produce stronger glare / spread as the camera turns', '- spatial status: accepted and integrated for the Human geometry scene\n- spatial renderer: scene-dependent simulation using live rendered high-luminance information so visible bright sources can produce stronger glare / spread as the camera turns; Night Intersection geometry/occlusion affects which highlights reach the rendered frame')
text = text.replace('- spatial status: accepted initial pilot mode\n- spatial renderer: live view-relative peripheral field-loss simulation on the rendered scene', '- spatial status: accepted and integrated for the Human geometry scene\n- spatial renderer: live view-relative peripheral field-loss simulation on the rendered scene')
text = text.replace('- spatial status: accepted post-pilot mode\n- spatial renderer: live view-relative central-field-loss simulation;', '- spatial status: accepted and integrated for the Human geometry scene\n- spatial renderer: live view-relative central-field-loss simulation;')
text = text.replace('- spatial status: accepted post-pilot mode\n- spatial renderer target: luminance-dependent loss of chromatic separation, contrast, and fine detail in darker rendered regions while brighter regions remain comparatively available', '- spatial status: accepted and integrated for the Human geometry scene\n- spatial renderer: luminance-dependent loss of chromatic separation, contrast, and fine detail in darker current-frame regions while brighter regions remain comparatively available')
p.write_text(text)

# Roadmap: E3 is closed; E4 is now the active geometry-Vision step.
p = Path("docs/roadmap.md")
text = p.read_text()
text = text.replace('- a production-verified E2 `Night Intersection` real-geometry baseline with authored camera translation/parallax and a permanent production fingerprint.', '- a production-verified E2 `Night Intersection` real-geometry baseline with authored camera translation/parallax and a permanent production fingerprint;\n- a production-verified E3 Human observer with bounded collision-aware ground movement on Night Intersection.')
text = text.replace('''## Immediate priority order
1. add bounded Human movement in E3, then integrate accepted Human spatial Vision modes in E4;
2. add Dog observer, then refine Dog-like 3D detail behavior;''', '''## Immediate priority order
1. integrate the accepted Human spatial Vision modes into Night Intersection in E4 while preserving the E3 observer state;
2. add Dog observer, then refine Dog-like 3D detail behavior;''')
p.write_text(text)

# Schedule: synchronize E3 production closeout and mark E4 implemented pending release verification.
p = Path("docs/explore-3d-schedule.md")
text = p.read_text()
text = text.replace('Status: **E3 IMPLEMENTED / release verification pending**', 'Status: **E4 IMPLEMENTED / release verification pending**', 1)
text = text.replace('Explore 3D Steps E1 and E2 are production verified. `Night Intersection` is now the default real-geometry scene while Hansaplatz remains the `360° Photo Reference`.', 'Explore 3D Steps E1, E2, and E3 are production verified. `Night Intersection` is the default real-geometry scene with bounded Human movement while Hansaplatz remains the `360° Photo Reference`. E4 integrates the accepted Human spatial Vision set on the geometry scene.')
text = text.replace('''## Step E3 — Human observer and bounded movement
Status: **IMPLEMENTED / release verification pending**''', '''## Step E3 — Human observer and bounded movement
Status: **PASS / production verified**''')
insert_after = '''Validation requirement before merge:
- build;
- desktop keyboard movement / faster Shift movement / Reset / navigation bound checks;
- mobile movement-pad touch targets / movement / Reset;
- Photo Reference look-only regression;
- full Compare image + Explore 3D production-smoke regression with an E3-specific stale-release fingerprint.
'''
replacement = insert_after + '''
Production closeout:
- full E3 validation run `34143680918` passed movement speed, collision, authored bounds, Reset, Photo Reference look-only behavior, real mobile touch movement, and the full local production-smoke regression; validation artifact `10026994364` was uploaded;
- PR #46 was squash-merged as main commit `47d7c0f9a15b62520b1a4a8994043668c14553cd`;
- matching main build `34144520176` passed;
- matching production smoke `34144520172` passed against `https://asseenby.pages.dev` with `productionReleaseDetected=true`, `e2SpatialReleaseDetected=true`, `e3HumanMovementDetected=true`, desktop/mobile image=true, desktop/mobile spatial=true, and `ok=true`;
- production smoke artifact `10027185737` was uploaded.
'''
if insert_after not in text:
    raise SystemExit("E3 validation block not found")
text = text.replace(insert_after, replacement, 1)
text = text.replace('''## Step E4 — Human spatial Vision integration
Status: **queued**''', '''## Step E4 — Human spatial Vision integration
Status: **IMPLEMENTED / release verification pending**''')
e4_accept = '''Acceptance requires same-position/same-direction comparisons and evidence/limitation review.
'''
e4_new = e4_accept + '''
Implemented E4:
- Night Intersection × Human exposes exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like; Dog-like remains Photo Reference-only until the Dog observer phase;
- the existing live Vision runtime is applied to the geometry renderer rather than duplicating the image transform engine;
- Tunnel/Central remain view-relative post-processing effects over the live geometry frame;
- Night / Low Light uses the current rendered frame's relative luminance, so authored geometry/material/light visibility changes its input while remaining explicitly non-calibrated;
- Cataract-like gates local glare from visible high-luminance rendered pixels, so geometry occlusion and visible practical/emissive sources affect the glare input without claiming calibrated lens scatter;
- Vision switching preserves Scene, Human observer, camera position, direction, FOV, lighting/object state and free/guided viewpoint state;
- Night / Low Light now has a spatial Evidence panel even though it is intentionally absent from the public image-mode registry.

Validation requirement before merge:
- build;
- same-position/same-direction/FOV checks for all five geometry Human Vision modes after both guided and free movement;
- rendered Tunnel edge-dominance and Central center-dominance checks;
- rendered Night dark-versus-bright response and Cataract bright-source response checks;
- Night spatial Evidence panel availability;
- desktop and 390px mobile geometry Vision usability with no horizontal overflow/errors;
- Photo Reference accepted Vision set unchanged;
- full Compare image regression;
- permanent production smoke with an E4-specific stale-release fingerprint.
'''
if e4_accept not in text:
    raise SystemExit("E4 acceptance line not found")
text = text.replace(e4_accept, e4_new, 1)
p.write_text(text)

print("E4 product/docs patch applied")
