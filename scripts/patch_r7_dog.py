from pathlib import Path


def replace_once(path: str, old: str, new: str, label: str) -> None:
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label} in {path}")
    p.write_text(text.replace(old, new, 1))


replace_once(
    "src/transformEngine.ts",
    '''  } else if (modeKey === "dog") {\n    applyColorDeficiency(data, amount * 0.85, [[0.62, 0.38, 0], [0.22, 0.78, 0], [0, 0.32, 0.68]]);\n    applyLowContrastToData(data, amount * 0.12);\n''',
    '''  } else if (modeKey === "dog") {\n    const severity = curveAmount(amount, 1.08);\n    // Human-display proxy: canine behavioral work supports a dichromatic pattern\n    // broadly similar to human red-green deficiency, but this is not a canine\n    // cone-catch reconstruction. Keep the chromatic and acuity changes restrained.\n    applyColorMatrixLinear(data, severity * 0.82, DEUTAN_MATRIX, 0.34);\n    compressRedGreenAxis(data, 0.06 + severity * 0.12);\n    applyLowContrastToData(data, 0.035 + severity * 0.075);\n''',
    "dog color transform",
)

replace_once(
    "src/transformEngine.ts",
    '''  if (modeKey === "dog") {\n    mixBlurredCopy(ctx, outCanvas, width, height, 0.6 + amount * 2, 0.75);\n  }\n''',
    '''  if (modeKey === "dog") {\n    mixBlurredCopy(ctx, outCanvas, width, height, 0.45 + amount * 1.35, 0.52);\n  }\n''',
    "dog acuity softening",
)

replace_once(
    "src/transformEngine.ts",
    '''function applyColorDeficiency(data: Uint8ClampedArray, amount: number, matrix: number[][]) {\n  for (let i = 0; i < data.length; i += 4) {\n    const r = data[i];\n    const g = data[i + 1];\n    const b = data[i + 2];\n    const tr = clamp255(r * matrix[0][0] + g * matrix[0][1] + b * matrix[0][2]);\n    const tg = clamp255(r * matrix[1][0] + g * matrix[1][1] + b * matrix[1][2]);\n    const tb = clamp255(r * matrix[2][0] + g * matrix[2][1] + b * matrix[2][2]);\n    data[i] = clamp255(mix(r, tr, amount));\n    data[i + 1] = clamp255(mix(g, tg, amount));\n    data[i + 2] = clamp255(mix(b, tb, amount));\n  }\n}\n\n''',
    "",
    "remove obsolete dog RGB helper",
)

replace_once(
    "src/modeEvidence.ts",
    '    modelNote: "The current dog mode uses a simplified visible-range color remapping plus softening. It communicates the broad red-green limitation better than an unmodified image, but it does not model canine acuity, rod dominance, motion sensitivity, or low-light strengths.",\n    caveat: "This mode is a browser-side visible-range proxy. It should not be read as a complete simulation of what a dog sees.",',
    '    modelNote: "The audited image renderer now uses a linear-RGB red-green-deficiency mapping as a human-display proxy for canine dichromacy, then applies restrained red-green axis compression, mild contrast reduction, and mild detail softening. The mapping is evidence-aligned at the tendency level but is not derived from canine cone catches or a calibrated canine observer model, so Model remains C.",\n    caveat: "This is a visible-range human-display proxy. It does not reconstruct canine cone excitations, breed-dependent field of view, rod/tapetal low-light behavior, motion processing, neural interpretation, or literal canine color experience.",',
    "dog evidence model wording",
)

replace_once(
    "docs/modes.md",
    '''### Dog\n- class: Estimated\n- goal: dog-like visible-range approximation\n- spatial status: accepted post-pilot mode\n- spatial renderer: conservative human-display visible-range dichromatic translation plus non-calibrated fine-detail softening\n''',
    '''### Dog\n- class: Estimated\n- goal: dog-like visible-range approximation\n- image status: retained after R7 audit with a narrowed human-display observer proxy\n- image renderer: linear-RGB red-green-deficiency mapping plus restrained red-green compression, contrast reduction, and fine-detail softening; not a canine cone-catch reconstruction\n- spatial status: accepted post-pilot mode\n- spatial renderer: conservative human-display visible-range dichromatic translation plus non-calibrated fine-detail softening\n''',
    "dog modes documentation",
)

replace_once(
    "docs/limitations.md",
    '''### Dog-like specific limitation\nCanine dichromacy is well supported, but a conventional RGB panorama cannot recover the original scene spectra or exact canine cone catches. The spatial Dog-like output therefore translates broad two-channel color relationships onto a human RGB display and adds mild non-calibrated detail softening.\n\nIt does not model breed-dependent field of view, retinal topography, motion sensitivity, tapetal/rod-mediated low-light advantages, spectral metamerism, or neural interpretation. It should not be read as literal canine color qualia or as one universal view shared by all dogs.\n''',
    '''### Dog-like specific limitation\nCanine dichromacy is well supported, including behavioral results that resemble human red-green color deficiency, but ordinary RGB cannot recover original scene spectra or exact canine cone catches. The audited image renderer therefore uses a linear-RGB red-green-deficiency mapping only as a human-display proxy, with restrained contrast and detail changes rather than a bespoke species-specific RGB matrix. The spatial Dog-like renderer remains a separate visible-range proxy on the accepted panorama.\n\nNeither renderer models breed-dependent field of view, retinal topography, motion sensitivity, tapetal/rod-mediated low-light advantages, spectral metamerism, exact canine acuity, or neural interpretation. They should not be read as literal canine color qualia or as one universal view shared by all dogs.\n''',
    "dog limitation wording",
)

schedule = Path("docs/release-polish-schedule.md")
text = schedule.read_text()
text = text.replace(
    '### R7-7 — Night / Low Light image mode\nStatus: **ACTIVE — removal implementation**',
    '### R7-7 — Night / Low Light image mode\nStatus: **PASS / removed / production verified**',
    1,
)
acceptance_tail = '''- after merge, production smoke must observe the exact 8-mode Human image set while still exercising the six-mode spatial set.\n\n## Current next action\nComplete and validate R7-7, merge only after the normal PR build passes, and require production smoke to confirm image Night is absent while spatial Night remains present.'''
replacement_tail = '''- after merge, production smoke must observe the exact 8-mode Human image set while still exercising the six-mode spatial set.\n\nValidation:\n- removal/build/desktop + 390px + spatial regression workflow `34026970730` — **success**;\n- PR #19 build `34034654963` — **success**;\n- merge SHA `b1f565feaf46251da3ad8149856ff73d69ee5569`;\n- matching main build `34034680040` — **success**;\n- production smoke `34034680087` — **success**, confirming image Night is absent while spatial Night remains one of the accepted six controls.\n\n### R7-8 — Dog-like image mode\nStatus: **ACTIVE — renderer revision and output audit**\n\nDecision: **KEEP the public Dog-like image mode, but REVISE the renderer and narrow its model claim**\n\nReason:\n- canine dichromatic color vision has strong behavioral and photopigment support;\n- behavioral work also supports a broad similarity to human red-green color-deficiency discrimination, while canine acuity and brightness discrimination differ from typical human vision;\n- the former AsSeenBy image renderer used an ad-hoc RGB matrix, which was not derived from canine cone catches or a validated observer model;\n- unlike the removed Cat/Bird/Bee modes, Dog-like still has a defensible visible-range explanatory target from ordinary RGB if the implementation is kept conservative.\n\nRevision scope:\n- replace the bespoke dog RGB matrix with the existing linear-RGB red-green-deficiency mapping as a human-display proxy;\n- add only restrained red-green compression, contrast reduction, and detail softening;\n- remove the now-unused arbitrary RGB-deficiency helper;\n- keep Evidence A but keep image Model C;\n- explicitly state that the renderer is not canine cone-catch reconstruction, literal canine qualia, rod/tapetal night vision, motion processing, or breed-specific field of view.\n\nAcceptance:\n- Dog-like remains the only public Animal image mode;\n- Dog-like produces a non-trivial but restrained output change that increases with Strength;\n- the implementation no longer contains the bespoke dog RGB matrix/helper;\n- desktop and 390px image checks pass without overflow or page/console errors;\n- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;\n- build passes;\n- after merge, production smoke remains green with Animal=Dog-like only.\n\n## Current next action\nApply and browser-test the R7-8 Dog-like renderer revision, inspect its output against Original at multiple Strength levels, then open a PR only if the revised output remains useful and restrained.'''
if acceptance_tail not in text:
    raise SystemExit("missing schedule tail anchor")
text = text.replace(acceptance_tail, replacement_tail, 1)
schedule.write_text(text)
