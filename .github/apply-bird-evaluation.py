from pathlib import Path
import re


def require_replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


# AGENTS -------------------------------------------------------------------
p = Path("AGENTS.md")
text = p.read_text()
text = require_replace(
    text,
    '- Central Loss, Night / Low Light, Dog-like, and the photographic 360° reference scene are accepted and merged. Cat-like spatial was evaluated and rejected because rendered review did not show enough distinct explanatory value beyond Dog-like without unsupported assumptions. The current expansion target is `Bird-like`; do not begin Bee-like until Bird-like is resolved.\n- Bird-like must begin with an evidence/source-data boundary before implementation. Ordinary tone-mapped RGB cannot reproduce avian ultraviolet response, tetrachromatic cone catches, oil-droplet filtering, polarization sensitivity, or literal avian qualia. Do not ship a generic saturation/contrast filter as avian vision merely to create a visible difference.',
    '- Central Loss, Night / Low Light, Dog-like, and the photographic 360° reference scene are accepted and merged. Cat-like spatial was rejected after rendered review. Generic Bird-like spatial was then rejected/blocked at the evidence/source-data gate: ordinary RGB cannot reproduce avian tetrachromatic/UV relationships, while acuity and spectral tuning vary too widely across bird species to justify one generic live renderer.\n- Bee-like spatial remains blocked until an explicit UV-reflectance/spectral scene-data path exists. Do not begin a Bee-like shader from ordinary RGB, and do not substitute a purple/blue false tint for missing UV information.\n- The ordered animal spatial evaluation is therefore resolved under the current Hansaplatz RGB source. Any future species-specific spatial work must introduce a new documented data/model requirement rather than reopening generic animal filters.',
    "AGENTS resolved animal spatial status",
)
p.write_text(text)


# ROADMAP ------------------------------------------------------------------
p = Path("docs/roadmap.md")
text = p.read_text()
pattern = r"## Spatial evaluation — Bird-like\nStatus: \*\*active next evaluation\*\*.*\Z"
replacement = '''## Spatial evaluation — Bird-like
Status: **rejected / blocked at evidence-source gate**

Evidence review found no defensible generic Bird-like spatial renderer for the current Hansaplatz source.

Why:
- many birds use four single-cone classes plus oil-droplet spectral filtering, with ultraviolet-sensitive (UVS) and violet-sensitive (VS) systems that ordinary RGB does not encode;
- the fourth avian color dimension cannot be reconstructed from three human-camera RGB channels after spectral information has been collapsed;
- avian visual acuity varies by roughly two orders of magnitude across measured species, so a generic sharpen/blur rule would not describe “bird vision” coherently;
- temporal resolution, retinal specializations, field of view and ecology also vary substantially across species;
- the only current image Bird-like behavior is a visible-range saturation/microcontrast proxy, which is not enough to justify a separate spatial mode.

Decision:
Do not add a Bird-like spatial control or shader from the current RGB panorama. A future avian spatial mode must be species-specific and/or use additional spectral/UV source data with a documented observer model.

## Spatial evaluation — Bee-like
Status: **blocked by missing UV-reflectance scene data**

The current panorama contains no UV-reflectance/spectral channel. Honeybee UV/blue/green photoreceptor behavior therefore cannot be reconstructed honestly from the current RGB source. No Bee-like spatial shader is started.

A future Bee-like phase requires:
- a UV-capable or measured spectral/UV scene source;
- documented mapping from bee photoreceptor catches to a human-display false-color representation;
- explicit handling of the fact that the human display cannot literally emit the bee perceptual dimensions being modeled.

## Spatial post-pilot status
The ordered animal expansion is **complete under the current RGB source-data boundary**:
- Dog-like — accepted;
- Cat-like — rejected after rendered review;
- Bird-like — rejected/blocked at evidence/source-data gate;
- Bee-like — blocked pending UV-reflectance/spectral scene data.

No additional generic animal spatial filter should be added merely to fill out the image-mode list.

## Near-term priority order
1. keep the accepted spatial set stable and regression-covered;
2. return active product work to image-transform quality, responsive/release polish, and evidence accuracy;
3. reopen species-specific spatial work only when a new source-data/model requirement is explicitly accepted.
'''
text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit("roadmap Bird tail replacement failed")
p.write_text(text)


# SCHEDULE -----------------------------------------------------------------
p = Path("docs/spatial-pilot-schedule.md")
text = p.read_text()
text, count = re.subn(
    r"## Current state\n.*?\n\n## Execution rule",
    "## Current state\nBranch: `feat/spatial-bird-evaluation`\nStatus: **Bird-like rejected/blocked at evidence gate / Bee-like blocked by source data**\n\nCat-like rejection was merged to main as `b28262f65ca8358aecbb4b76175e786423cf93fe`; post-merge main build `34010635740` passed. Bird-like was then reviewed as a source-data/evidence question before any shader work. The current RGB panorama cannot support a defensible generic Bird-like spatial observer, and Bee-like remains blocked without UV-reflectance/spectral scene data.\n\n## Execution rule",
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit("schedule current state replacement failed")
text, count = re.subn(
    r"## Step 15 — Bird-like evidence/source-data boundary\n.*\Z",
    '''## Step 15 — Bird-like evidence/source-data evaluation
Status: **REJECTED / BLOCKED before implementation**

Evidence review established:
- avian color vision commonly uses four spectrally distinct single-cone classes, with oil-droplet filtering and UVS/VS short-wavelength systems;
- UVS/VS tuning differs across avian lineages and cannot be recovered from the current three-channel tone-mapped RGB panorama;
- measured visual acuity varies by roughly two orders of magnitude across bird species, so one generic “bird sharpness” transform would be biologically incoherent;
- temporal resolution and other visual specializations also vary substantially across species;
- the current image Bird-like transform only boosts visible-range saturation/microcontrast and has Model D, which does not provide a scientifically sufficient spatial mechanism.

Evidence anchors reviewed for this decision include:
- `Avian visual pigments: characteristics, spectral tuning, and evolution` (PMID 19426092);
- `Ultraviolet vision in birds: the importance of transparent eye media` (PMID 24258716);
- `The phylogenetic distribution of ultraviolet sensitivity in birds` (PMID 23394614);
- `Ecological and morphological correlates of visual acuity in birds` (PMID 38126722), which compiled acuity data for 94 species in 38 families and reported variation across roughly two orders of magnitude.

Decision:
**Do not implement a generic Bird-like spatial shader/control from the current RGB panorama.** A saturation/contrast boost would be decorative, not an avian observer model. A future avian spatial mode must either target a specific species with a documented visual model or add spectral/UV scene data sufficient for the intended observer transform.

## Step 16 — Bee-like source-data gate
Status: **BLOCKED / not implemented**

Bee-like already has an explicit special rule: ordinary RGB cannot provide the UV information required for a defensible bee observer model. The current Hansaplatz panorama has no UV-reflectance or spectral channel, so no Bee-like spatial implementation is started.

Unblock requirements:
- UV-reflectance or spectral scene/material data;
- documented bee photoreceptor sensitivity/model inputs;
- explicit human-display false-color mapping and caveats;
- a rendered acceptance gate proving explanatory value beyond an arbitrary purple/blue filter.

## Ordered animal spatial evaluation — resolved
- Dog-like — **accepted / merged**;
- Cat-like — **rejected after rendered review**;
- Bird-like — **rejected/blocked at evidence/source-data gate**;
- Bee-like — **blocked pending UV-reflectance/spectral scene data**.

## Current next action
Close the current ordered animal spatial expansion under the RGB source-data boundary. Keep the accepted spatial modes regression-covered and return active product work to the existing image track / release-polish priorities unless a new spatial data/model requirement is explicitly introduced.
''',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit("schedule Bird tail replacement failed")
p.write_text(text)


# SPEC ---------------------------------------------------------------------
p = Path("docs/spatial-pilot-spec.md")
text = p.read_text()
text = require_replace(
    text,
    "Current expansion target:\n7. **Bird-like** — evidence/source-data evaluation first. Do not create a Bird-like shader until a supported visible-range component is identified that adds value beyond a generic saturation/contrast filter without fabricating UV/tetrachromatic information.",
    "Evaluated and rejected/blocked spatial candidate:\n7. **Bird-like** — no generic RGB-only renderer is accepted. Avian tetrachromatic/UV systems cannot be reconstructed from the current RGB panorama, while visual acuity and other visual traits vary too widely across bird species for one generic live observer.\n\nBlocked by source-data requirement:\n8. **Bee-like** — no spatial implementation until UV-reflectance/spectral scene data and a documented bee observer/false-color model exist.",
    "spec Bird target status",
)
old_boundary = '''## Bird-like evaluation boundary

Bird-like starts with evidence and source-data review. Many birds use four cone classes and ultraviolet- or violet-sensitive vision, often with species-specific oil-droplet filtering. The current panorama contains human-camera RGB values, not spectral radiance/reflectance or UV data.

Therefore:
- do not infer UV or tetrachromatic cone catches from RGB;
- do not use a generic saturation/contrast boost as a stand-in for avian vision;
- identify any supported RGB-visible component before implementation;
- if no such component justifies a distinct spatial comparison, reject/block Bird-like until additional data is available.

'''
new_boundary = '''## Bird-like evaluation result — rejected / blocked

Bird-like was evaluated before implementation and failed the source-data/generic-model gate.

Evidence boundary:
- many birds use four spectrally distinct single-cone classes rather than the human three-channel system;
- UVS and VS short-wavelength tuning varies among avian lineages;
- colored oil droplets further alter cone spectral sensitivities;
- ordinary RGB has already collapsed the scene spectrum into three human-camera channels and cannot reconstruct a fourth independent avian color dimension or UV reflectance;
- avian visual acuity varies by roughly two orders of magnitude across species, so a generic sharpen/blur rule is not defensible as “Bird-like” vision.

Result:
- no Bird-like spatial control is added;
- no saturation/contrast shader is accepted as avian vision;
- a future avian spatial mode must be species-specific and/or use additional spectral/UV source data plus a documented observer model.

## Bee-like source-data result — blocked

The Bee-like special rule remains binding. The current scene has no UV-reflectance/spectral data, so there is no honest spatial Bee-like implementation path from the existing panorama alone.

Unblocking Bee-like requires a separate data/model phase with UV-capable scene information and a documented false-color translation for human displays. Until then, no Bee-like spatial control or shader should exist.

'''
text = require_replace(text, old_boundary, new_boundary, "spec Bird/Bee evaluation")
p.write_text(text)


# METHODOLOGY --------------------------------------------------------------
p = Path("docs/methodology.md")
text = p.read_text()
text = require_replace(
    text,
    "Current expansion target:\n- Bird-like evidence/source-data evaluation.",
    "Evaluated and rejected/blocked spatial candidate:\n- Bird-like — the current RGB source cannot support a generic avian observer without fabricating missing tetrachromatic/UV information, and species-level acuity/spectral variation is too large for one generic renderer.\n\nBlocked spatial candidate:\n- Bee-like — requires UV-reflectance/spectral scene data before implementation.",
    "methodology current Bird target",
)
old = '''## Bird-like spatial evaluation boundary
Bird-like begins as a source-data/evidence question, not a shader task. Ordinary RGB cannot reconstruct ultraviolet/violet-sensitive cone catches, tetrachromatic color relationships, species-specific oil-droplet filtering, or polarization sensitivity. Any spatial Bird-like candidate must identify a supported visible-range property with explanatory value beyond a generic saturation/contrast effect, or be rejected/blocked.
'''
new = '''## Bird-like spatial evaluation result
Bird-like was evaluated as a source-data/evidence question before shader work and was rejected/blocked for the current generic RGB setup. Ordinary RGB cannot reconstruct ultraviolet/violet-sensitive cone catches, tetrachromatic color relationships, species-specific oil-droplet filtering, or polarization sensitivity. In addition, comparative data show very large species variation in avian acuity, making a generic spatial sharpness rule misleading.

The current image Bird-like mode remains a deliberately weak visible-range proxy with Model D. That image transform is not promoted into a spatial mode merely because Three.js can reproduce the same saturation/microcontrast changes interactively.

## Bee-like spatial source-data result
Bee-like remains blocked until UV-reflectance/spectral scene data are available. A future implementation must model a documented bee observer and then translate that result to a human display with explicit false-color caveats; ordinary RGB cannot supply the missing UV channel after capture.
'''
text = require_replace(text, old, new, "methodology Bird/Bee result")
p.write_text(text)


# LIMITATIONS --------------------------------------------------------------
p = Path("docs/limitations.md")
text = p.read_text()
old = '''### Bird-like spatial source-data limitation
Many avian visual systems include ultraviolet/violet-sensitive and tetrachromatic mechanisms plus species-specific filtering that ordinary RGB scene data cannot reconstruct. A future Bird-like spatial mode must not substitute a saturation or contrast boost for missing spectral information. If no supported RGB-visible component adds genuine explanatory value, Bird-like should remain rejected/blocked until additional data is available.

A future spatial scene does not create missing UV information automatically. Bee-like UV work requires additional UV-reflectance scene/material data and an explicit false-color translation for human displays.
'''
new = '''### Bird-like spatial evaluation limitation
Generic Bird-like spatial has been rejected/blocked for the current RGB panorama. Avian color systems include UVS/VS and tetrachromatic mechanisms with oil-droplet filtering that ordinary RGB cannot reconstruct, while measured acuity varies by roughly two orders of magnitude across bird species. A generic saturation/contrast boost or generic sharpen/blur effect would therefore imply a coherent “bird view” that the source data and taxonomic category do not support.

A future avian spatial mode must be species-specific and/or use additional spectral/UV scene data with a documented observer model.

### Bee-like spatial source-data limitation
A future spatial scene does not create missing UV information automatically. Bee-like UV work requires additional UV-reflectance/spectral scene/material data and an explicit false-color translation for human displays. Until those inputs exist, Bee-like spatial is blocked and no purple/blue RGB filter should be presented as bee vision.
'''
text = require_replace(text, old, new, "limitations Bird/Bee")
p.write_text(text)


# MODES --------------------------------------------------------------------
p = Path("docs/modes.md")
text = p.read_text()
text = require_replace(
    text,
    "### Bee\n- class: Estimated\n- goal: bee-like visible-range approximation\n- limitation: UV is not reproduced by the current image mode\n- spatial rule: a future UV-aware implementation requires additional UV-reflectance scene/material data and must not invent UV from ordinary RGB color\n\n### Bird-like\n- class: Estimated\n- goal: bird-like visible-range approximation\n- limitation: UV and full tetrachromatic response are not reproduced by ordinary RGB\n- spatial status: next evidence/source-data evaluation; no spatial control until a non-misleading renderer candidate is justified",
    "### Bee\n- class: Estimated\n- goal: bee-like visible-range approximation\n- limitation: UV is not reproduced by the current image mode\n- spatial status: blocked; requires additional UV-reflectance/spectral scene/material data and a documented false-color observer mapping before implementation\n\n### Bird-like\n- class: Estimated\n- goal: bird-like visible-range approximation\n- image status: current saturation/microcontrast proxy remains available with Model D\n- limitation: UV/tetrachromacy and broad species variation are not reproduced by ordinary RGB\n- spatial status: rejected/blocked at evidence/source-data gate; no generic Bird-like spatial control is accepted from the current RGB panorama",
    "modes Bee/Bird status",
)
p.write_text(text)


# UI SPEC ------------------------------------------------------------------
p = Path("docs/ui-spec.md")
text = p.read_text()
text = require_replace(
    text,
    "Dog-like is accepted and public. Cat-like spatial was evaluated and rejected, so there is intentionally no Cat-like control in Explore spatial. Bird-like is the next evidence/source-data evaluation and must not receive a control until a renderer candidate passes its scientific and rendered acceptance gates.",
    "Dog-like is accepted and public. Cat-like spatial was rejected after rendered review. Generic Bird-like spatial was rejected/blocked at the evidence/source-data gate, and Bee-like is blocked pending UV-reflectance/spectral scene data. There are intentionally no Cat-like, Bird-like, or Bee-like controls in Explore spatial under the current source-data boundary.",
    "UI resolved animal controls",
)
p.write_text(text)


# MODE EVIDENCE ------------------------------------------------------------
p = Path("src/modeEvidence.ts")
text = p.read_text()
bird_block = '''  bird: {
    summary: "Visible-range avian-inspired image proxy with strong evidence that many birds use visual systems outside human RGB, but deliberately weak implementation confidence because a generic bird observer cannot be reconstructed from a standard image.",
    evidenceScore: "A",
    modelScore: "D",
    basisNote: "Birds commonly have four spectrally distinct single-cone classes with UVS or VS short-wavelength tuning and cone oil-droplet filtering. Comparative work also shows that visual acuity varies by roughly two orders of magnitude across bird species, so there is no single generic avian sharpness profile.",
    modelNote: "The current image Bird-like mode only boosts visible-range saturation and microcontrast. It does not reconstruct tetrachromatic cone catches, ultraviolet information, oil-droplet filtering, species-specific acuity, temporal resolution, retinal specializations, or neural interpretation. A separate generic spatial Bird-like candidate was rejected/blocked at the evidence/source-data gate rather than promoting this weak image proxy into Three.js.",
    caveat: "Treat this as a limited visual comparison aid, not a simulation of what birds generally see. Avian vision differs materially among species, and ordinary RGB has already discarded the spectral/UV information needed for a four-channel observer model.",
    primarySource: {
      title: "Avian visual pigments: characteristics, spectral tuning, and evolution",
      url: "https://pubmed.ncbi.nlm.nih.gov/19426092/",
      kind: "review",
      note: "Review of the four avian single-cone pigment classes, their spectral tuning, and evolutionary variation including UV/violet-sensitive systems.",
    },
    supportingSources: [
      {
        title: "Ultraviolet vision in birds: the importance of transparent eye media",
        url: "https://pubmed.ncbi.nlm.nih.gov/24258716/",
        kind: "paper",
        note: "Shows UVS versus VS spectral sensitivity and ocular-media differences across 38 bird species.",
      },
      {
        title: "The phylogenetic distribution of ultraviolet sensitivity in birds",
        url: "https://pubmed.ncbi.nlm.nih.gov/23394614/",
        kind: "paper",
        note: "Documents repeated shifts between UVS and VS avian color-vision classes across the bird phylogeny.",
      },
      {
        title: "Ecological and morphological correlates of visual acuity in birds",
        url: "https://pubmed.ncbi.nlm.nih.gov/38126722/",
        kind: "paper",
        note: "Comparative review of 94 species from 38 families reporting visual-acuity variation across roughly two orders of magnitude.",
      },
      {
        title: "Tetrachromacy, oil droplets and bird plumage colours",
        url: "https://pubmed.ncbi.nlm.nih.gov/9839454/",
        kind: "paper",
        note: "Explains how tetrachromacy and colored oil droplets alter avian spectral discrimination beyond a human RGB model.",
      },
    ],
    lastReviewed: "2026-09-06",
  },
'''
text, count = re.subn(r"  bird: \{.*?\n  age: \{", bird_block + "  age: {", text, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Bird evidence replacement failed")
p.write_text(text)

print("Bird-like rejected/blocked; Bee-like source-data block recorded")
