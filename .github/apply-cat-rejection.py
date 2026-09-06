from pathlib import Path
import re


def require_replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


# AGENTS: Dog is merged, Cat spatial was evaluated and rejected, Bird is next.
p = Path("AGENTS.md")
text = p.read_text()
text = require_replace(
    text,
    '- Central Loss, Night / Low Light, and the photographic 360° reference scene are accepted and merged. The current expansion target is `Dog-like`; do not begin Cat-like, Bird-like, or Bee-like until its rendered acceptance gate passes or it is explicitly rejected.\n- Dog-like must preserve the same camera and use a conservative visible-range dichromatic + acuity proxy. Do not claim that RGB can reconstruct canine cone catches for arbitrary spectra, or that the renderer models breed-dependent field of view, motion processing, tapetal/rod low-light advantages, or literal canine qualia.',
    '- Central Loss, Night / Low Light, Dog-like, and the photographic 360° reference scene are accepted and merged. Cat-like spatial was evaluated and rejected because rendered review did not show enough distinct explanatory value beyond Dog-like without unsupported assumptions. The current expansion target is `Bird-like`; do not begin Bee-like until Bird-like is resolved.\n- Bird-like must begin with an evidence/source-data boundary before implementation. Ordinary tone-mapped RGB cannot reproduce avian ultraviolet response, tetrachromatic cone catches, oil-droplet filtering, polarization sensitivity, or literal avian qualia. Do not ship a generic saturation/contrast filter as avian vision merely to create a visible difference.',
    "AGENTS spatial target",
)
p.write_text(text)


# Roadmap: record Cat rejection and make Bird evaluation active.
p = Path("docs/roadmap.md")
text = p.read_text()
pattern = r"## Spatial expansion — Dog-like\nStatus: \*\*active\*\*.*\Z"
replacement = '''## Spatial expansion — Dog-like
Status: **accepted / merged**

Dog-like passed same-camera desktop/mobile rendered review and is now part of the accepted spatial set. It remains a conservative human-display visible-range dichromatic/acuity proxy, not a complete canine visual reconstruction.

## Spatial evaluation — Cat-like
Status: **rejected after rendered review**

A conservative Cat-like candidate was implemented and compared against Normal and Dog-like on the same 360° camera states. Browser regression passed, but the visible difference from Dog-like was dominated by slightly lower chroma and slightly stronger softening. Keeping a separate spatial Cat-like control would therefore imply a species-specific distinction that the current RGB source and evidence boundary do not justify strongly enough.

The image-track Cat-like mode remains available as an explicitly cautious visible-range approximation. The rejected spatial candidate is not added to the public spatial controls.

## Spatial evaluation — Bird-like
Status: **active next evaluation**

Goal:
Determine whether an honest Bird-like spatial comparison is possible from the current tone-mapped RGB panorama, and reject it rather than inventing ultraviolet/tetrachromatic information if the source data is insufficient.

Required evaluation:
- review avian cone classes, ultraviolet/violet sensitivity, oil-droplet filtering and species variation;
- separate what can be communicated from ordinary RGB from what requires spectral/UV scene data;
- do not treat saturation or contrast boost as a sufficient Bird-like simulation;
- preserve the exact camera/source scene for any candidate that survives the evidence boundary;
- require rendered explanatory value beyond a decorative filter before adding a public control.

## Ordered next spatial candidates
1. Bird-like evidence/source-data evaluation;
2. Bee-like only with additional UV-reflectance scene data.

## Near-term priority order
1. define the Bird-like spectral/source-data boundary;
2. decide whether the current RGB panorama supports any non-misleading spatial Bird-like renderer;
3. if yes, implement one restrained candidate and run same-camera desktop/mobile review;
4. if no, record Bird-like as rejected/blocked rather than faking missing UV/tetrachromatic information;
5. do not begin Bee-like until Bird-like is resolved.
'''
text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit("roadmap tail replacement failed")
p.write_text(text)


# Schedule: close Dog merge, record Cat technical pass + manual rejection, advance to Bird.
p = Path("docs/spatial-pilot-schedule.md")
text = p.read_text()
text, count = re.subn(
    r"## Current state\n.*?\n\n## Execution rule",
    "## Current state\nBranch: `feat/spatial-cat-like`\nStatus: **Cat-like spatial rejected after rendered review / Bird-like next**\n\nDog-like is merged on main as `5bdd0d39f963b498fcf2f7f379f07b50adf79e25`; post-merge main build `34009808490` passed. Cat-like candidate browser run `34010239767` passed technically, but manual same-camera review rejected the spatial mode as insufficiently distinct from Dog-like without unsupported assumptions.\n\n## Execution rule",
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit("schedule current state replacement failed")
text, count = re.subn(
    r"## Step 13 — Dog-like evidence boundary and renderer\n.*\Z",
    '''## Step 13 — Dog-like
Status: **PASS / accepted / merged**

Rendered review `34009491932` passed and was manually accepted. Final clean-head build `34009690754` and browser regression `34009688930` passed. PR #5 was squash-merged to main as `5bdd0d39f963b498fcf2f7f379f07b50adf79e25`; post-merge main build `34009808490` passed.

Dog-like remains a human-display visible-range dichromatic/acuity proxy with spatial Model C. It does not claim exact canine cone catches, breed-dependent field of view, motion processing, tapetal/rod low-light reconstruction, or literal canine qualia.

## Step 14 — Cat-like spatial evaluation
Status: **REJECTED after rendered review**

Candidate implementation `dd6df2295f2e3efe480913035a6db3da116ae3ee` built successfully in patch workflow `34010195587`. PR build `34010245847` passed. Chromium browser run `34010239767` also passed with `result.json` reporting no browser failures, overflow, page errors, or console errors.

Manual same-camera review compared Normal / Dog-like / Cat-like in forward and turned desktop views plus the 390px mobile Cat-like view. The Cat-like candidate remained coherent and technically usable, but its visible separation from Dog-like was primarily a modest further desaturation/chromatic compression and slightly stronger fine-detail softening.

Decision: **reject the spatial Cat-like control**. The current RGB panorama and evidence boundary do not justify inventing a stronger feline-specific visual distinction merely to make the modes look different. The existing image-track Cat-like approximation remains separately available and conservatively labeled.

No Cat-like shader, spatial evidence branch, control, or browser capture additions are merged to main from the rejected candidate.

## Step 15 — Bird-like evidence/source-data boundary
Status: **next / not yet implemented**

Before any Bird-like renderer is added, determine which avian characteristics can be represented from the current tone-mapped RGB panorama and which require additional spectral/UV scene data. Many avian visual systems involve four cone classes, ultraviolet/violet sensitivity, species-specific oil-droplet filtering and other properties that ordinary RGB cannot reconstruct.

Acceptance rule for beginning implementation:
- a candidate must have a documented visible-range component that is both supported and meaningfully different from simply increasing saturation/contrast;
- missing UV/tetrachromatic information must not be fabricated from RGB;
- if the current source cannot support a useful non-misleading Bird-like spatial comparison, record the mode as rejected/blocked instead of implementing a decorative filter.

## Ordered next spatial candidates
1. Bird-like evidence/source-data evaluation
2. Bee-like only with additional UV-reflectance scene data

## Current next action
Review Bird-like evidence and source-data requirements against the current Hansaplatz RGB panorama. Decide whether a spatial renderer candidate is justified before writing any Bird-like shader. Do not begin Bee-like yet.
''',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit("schedule Dog tail replacement failed")
p.write_text(text)


# Methodology: Dog accepted, Cat spatial rejected, Bird next evaluation.
p = Path("docs/methodology.md")
text = p.read_text()
text = require_replace(
    text,
    "Accepted spatial modes:\n- Normal;\n- Tunnel Vision;\n- Central Loss;\n- Night / Low Light;\n- Cataract-like.\n\nCurrent expansion target:\n- Dog-like.",
    "Accepted spatial modes:\n- Normal;\n- Tunnel Vision;\n- Central Loss;\n- Night / Low Light;\n- Dog-like;\n- Cataract-like.\n\nEvaluated and rejected spatial candidate:\n- Cat-like — technically valid renderer candidate, but not distinct enough from Dog-like to justify a separate spatial claim from the current RGB source.\n\nCurrent expansion target:\n- Bird-like evidence/source-data evaluation.",
    "methodology mode list",
)
dog_anchor = '''## Dog-like spatial model
The active Dog-like target combines a simplified visible-range dichromatic translation with mild loss of fine detail. The phenomenon basis is stronger than the renderer: canine dichromacy and lower acuity are supported by behavioral/physiological literature, but a standard RGB panorama does not contain the spectral information needed to calculate exact canine photoreceptor catches for arbitrary real-world materials and lights.

For that reason the renderer keeps Evidence and Model separate: the broad canine visual differences can retain strong evidence while the spatial implementation remains Model C. Field of view, motion processing, tapetal/rod low-light advantages and neural interpretation are intentionally excluded from this phase.
'''
replacement = '''## Dog-like spatial model
The accepted Dog-like renderer combines a simplified visible-range dichromatic translation with mild loss of fine detail. The phenomenon basis is stronger than the renderer: canine dichromacy and lower acuity are supported by behavioral/physiological literature, but a standard RGB panorama does not contain the spectral information needed to calculate exact canine photoreceptor catches for arbitrary real-world materials and lights.

For that reason the renderer keeps Evidence and Model separate: the broad canine visual differences can retain strong evidence while the spatial implementation remains Model C. Field of view, motion processing, tapetal/rod low-light advantages and neural interpretation are intentionally excluded from this phase.

## Cat-like spatial evaluation
A Cat-like spatial candidate was implemented with conservative chromatic compression and slightly stronger fine-detail softening. Automated browser validation passed, but same-camera rendered review found that its explanatory difference from the accepted Dog-like mode was mostly a small degree change in chroma and blur.

Because the feline literature contains historical uncertainty and the RGB panorama cannot recover exact feline spectral catches, the project rejected the spatial Cat-like control rather than exaggerating unsupported differences. This rejection does not remove the separate image-track Cat-like approximation; it only means the current spatial source/model does not justify a distinct live Cat-like mode.

## Bird-like spatial evaluation boundary
Bird-like begins as a source-data/evidence question, not a shader task. Ordinary RGB cannot reconstruct ultraviolet/violet-sensitive cone catches, tetrachromatic color relationships, species-specific oil-droplet filtering, or polarization sensitivity. Any spatial Bird-like candidate must identify a supported visible-range property with explanatory value beyond a generic saturation/contrast effect, or be rejected/blocked.
'''
text = require_replace(text, dog_anchor, replacement, "methodology Dog/Cat/Bird section")
p.write_text(text)


# Limitations: explicitly record Cat spatial rejection and Bird data boundary.
p = Path("docs/limitations.md")
text = p.read_text()
anchor = '''### Dog-like specific limitation
Canine dichromacy is well supported, but a conventional RGB panorama cannot recover the original scene spectra or exact canine cone catches. The spatial Dog-like output therefore translates broad two-channel color relationships onto a human RGB display and adds mild non-calibrated detail softening.

It does not model breed-dependent field of view, retinal topography, motion sensitivity, tapetal/rod-mediated low-light advantages, spectral metamerism, or neural interpretation. It should not be read as literal canine color qualia or as one universal view shared by all dogs.

'''
addition = anchor + '''### Cat-like spatial evaluation limitation
The separate spatial Cat-like candidate was rejected after same-camera review because its visible distinction from Dog-like was mainly a small increase in chromatic compression/desaturation and fine-detail softening. The current RGB source does not justify manufacturing a stronger feline-specific distinction.

The image-track Cat-like mode remains an explicitly cautious visible-range approximation. There is no accepted public Cat-like spatial renderer at this stage.

### Bird-like spatial source-data limitation
Many avian visual systems include ultraviolet/violet-sensitive and tetrachromatic mechanisms plus species-specific filtering that ordinary RGB scene data cannot reconstruct. A future Bird-like spatial mode must not substitute a saturation or contrast boost for missing spectral information. If no supported RGB-visible component adds genuine explanatory value, Bird-like should remain rejected/blocked until additional data is available.

'''
text = require_replace(text, anchor, addition, "limitations animal spatial sections")
p.write_text(text)


# UI spec: Dog is accepted; Cat spatial is deliberately absent; Bird has no control yet.
p = Path("docs/ui-spec.md")
text = p.read_text()
text = require_replace(
    text,
    "- Dog-like\n- Cataract-like\n\nDog-like is the active expansion target. Its control is included only with the live visible-range dichromatic/acuity implementation, not as an unimplemented placeholder.",
    "- Dog-like\n- Cataract-like\n\nDog-like is accepted and public. Cat-like spatial was evaluated and rejected, so there is intentionally no Cat-like control in Explore spatial. Bird-like is the next evidence/source-data evaluation and must not receive a control until a renderer candidate passes its scientific and rendered acceptance gates.",
    "UI spatial controls",
)
p.write_text(text)


# Modes: Dog accepted, Cat image remains but spatial candidate rejected, Bird is next evaluation.
p = Path("docs/modes.md")
text = p.read_text()
text = require_replace(
    text,
    "### Dog\n- class: Estimated\n- goal: dog-like visible-range approximation\n- spatial status: deferred until the ordered human spatial expansion reaches it\n\n### Cat\n- class: Estimated\n- goal: cat-like visible-range approximation\n- spatial status: deferred until the ordered human spatial expansion reaches it",
    "### Dog\n- class: Estimated\n- goal: dog-like visible-range approximation\n- spatial status: accepted post-pilot mode\n- spatial renderer: conservative human-display visible-range dichromatic translation plus non-calibrated fine-detail softening\n\n### Cat\n- class: Estimated\n- goal: cat-like visible-range approximation\n- image status: current cautious visible-range image proxy remains available\n- spatial status: rejected after rendered evaluation; candidate was not distinct enough from Dog-like to justify a separate live spatial claim from the current RGB source",
    "modes Dog/Cat status",
)
text = require_replace(
    text,
    "### Bird-like\n- class: Estimated\n- goal: bird-like visible-range approximation\n- limitation: UV is not reproduced\n- spatial status: deferred for separate evaluation after earlier spatial candidates",
    "### Bird-like\n- class: Estimated\n- goal: bird-like visible-range approximation\n- limitation: UV and full tetrachromatic response are not reproduced by ordinary RGB\n- spatial status: next evidence/source-data evaluation; no spatial control until a non-misleading renderer candidate is justified",
    "modes Bird status",
)
p.write_text(text)


# Spatial spec: Dog accepted, Cat rejected, Bird is the current evaluation target.
p = Path("docs/spatial-pilot-spec.md")
text = p.read_text()
text = require_replace(
    text,
    "Current expansion target:\n5. **Dog-like** — a visible-range human-display proxy for canine dichromacy plus lower spatial acuity, with no claim of full canine spectral, field-of-view, motion, low-light, or neural reconstruction.",
    "Accepted post-pilot example:\n5. **Dog-like** — a visible-range human-display proxy for canine dichromacy plus lower spatial acuity, with no claim of full canine spectral, field-of-view, motion, low-light, or neural reconstruction.\n\nEvaluated and rejected spatial candidate:\n6. **Cat-like** — technically valid color/acuity candidate, but same-camera review did not show enough distinct explanatory value beyond Dog-like to justify a separate spatial claim from the current RGB source.\n\nCurrent expansion target:\n7. **Bird-like** — evidence/source-data evaluation first. Do not create a Bird-like shader until a supported visible-range component is identified that adds value beyond a generic saturation/contrast filter without fabricating UV/tetrachromatic information.",
    "spec current target",
)
cat_record = '''## Post-pilot evaluation — Cat-like (rejected)

A conservative Cat-like candidate was implemented and passed automated desktop/mobile browser checks. Same-camera rendered review compared it directly with Normal and Dog-like. The remaining visible distinction was mainly slightly lower chroma/chromatic separation plus slightly stronger fine-detail softening.

The project rejected the spatial Cat-like control because keeping it would encourage unsupported species-specific differentiation from a tone-mapped RGB source. Historical feline cone literature is also less straightforward than the canine case. The image-track Cat-like approximation remains separately available and conservatively labeled.

Rejection rule established by this step: a species mode is not accepted merely because a shader can be made visually different. It must add documented explanatory value that the available source data can support.

## Bird-like evaluation boundary

Bird-like starts with evidence and source-data review. Many birds use four cone classes and ultraviolet- or violet-sensitive vision, often with species-specific oil-droplet filtering. The current panorama contains human-camera RGB values, not spectral radiance/reflectance or UV data.

Therefore:
- do not infer UV or tetrachromatic cone catches from RGB;
- do not use a generic saturation/contrast boost as a stand-in for avian vision;
- identify any supported RGB-visible component before implementation;
- if no such component justifies a distinct spatial comparison, reject/block Bird-like until additional data is available.

'''
text = require_replace(text, "## Camera and interaction\n", cat_record + "## Camera and interaction\n", "spec Cat rejection/Bird boundary")
p.write_text(text)


# Improve Cat image evidence with the modern behavioral source while retaining historical disagreement.
p = Path("src/modeEvidence.ts")
text = p.read_text()
cat_block = '''  cat: {
    summary: "Visible-range approximation inspired by domestic-cat color discrimination and lower spatial acuity, kept conservative because feline spectral literature contains historical disagreement.",
    evidenceScore: "B",
    modelScore: "C",
    basisNote: "Modern behavioral neutral-point testing supports dichromatic feline color vision, while older physiological studies reported competing two- and three-cone interpretations. Behavioral acuity work also supports substantially lower spatial resolution than human vision.",
    modelNote: "The current image cat mode remains a simplified visible-range proxy with remapped color relationships, reduced saturation, and softening. It does not claim exact feline cone catches from ordinary RGB input. A separate spatial Cat-like candidate was evaluated and rejected because it did not add enough distinct explanatory value beyond Dog-like.",
    caveat: "Cat vision depends on luminance, adaptation, individual physiology, and task. This image mode does not reproduce tapetal/rod low-light advantages, exact spectral catches, field of view, motion processing, or literal feline color experience.",
    primarySource: {
      title: "Neutral point testing of color vision in the domestic cat",
      url: "https://pubmed.ncbi.nlm.nih.gov/27720709/",
      kind: "paper",
      note: "2016 behavioral study reporting strong evidence for dichromatic color vision in domestic cats and a neutral point near the human deuteranope.",
    },
    supportingSources: [
      {
        title: "Cat colour vision: evidence for more than one cone process",
        url: "https://pubmed.ncbi.nlm.nih.gov/5500987/",
        kind: "paper",
        note: "Classic behavioral and physiological evidence for more than one feline cone process.",
      },
      {
        title: "The effects of time, luminance, and high contrast targets: revisiting grating acuity in the domestic cat",
        url: "https://pubmed.ncbi.nlm.nih.gov/23978601/",
        kind: "paper",
        note: "Reviews behavioral feline grating-acuity estimates and demonstrates that measured acuity depends strongly on test conditions.",
      },
      {
        title: "Trichromatic vision in the cat",
        url: "https://pubmed.ncbi.nlm.nih.gov/910161/",
        kind: "paper",
        note: "Historical physiological evidence for a third cone mechanism, retained as a counterweight to overconfident dichromatic framing.",
      },
    ],
    lastReviewed: "2026-09-06",
  },
'''
text, count = re.subn(r"  cat: \{.*?\n  bee: \{", cat_block + "  bee: {", text, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Cat evidence replacement failed")
p.write_text(text)

print("Cat-like spatial rejection recorded; Bird-like advanced")
