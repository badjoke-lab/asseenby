from pathlib import Path
import re


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}")
    p.write_text(text.replace(old, new, 1))


# Public mode definition.
replace_once(
    "src/modes.ts",
    '  { key: "bee", label: "Bee-like", category: "Animal", confidence: "Estimated", note: "Bee-like visible-range approximation based on commonly described bee characteristics. UV not included." },\n',
    "",
)

# Arbitrary RGB-only transform branch.
p = Path("src/transformEngine.ts")
text = p.read_text()
updated, count = re.subn(
    r'  \} else if \(modeKey === "bee"\) \{\n.*?(?=  \} else if \(modeKey === "bird"\) \{)',
    "",
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f"src/transformEngine.ts: expected one bee branch, found {count}")
p.write_text(updated)

# Mode-specific evidence entry. The evidence remains represented in the R7 decision record.
p = Path("src/modeEvidence.ts")
text = p.read_text()
updated, count = re.subn(r'\n  bee: \{\n.*?\n  \},\n(?=  bird: \{)', '\n', text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f"src/modeEvidence.ts: expected one bee evidence block, found {count}")
p.write_text(updated)

# Public/product documentation.
replace_once("README.md", "- Bee-like\n", "")
replace_once("docs/mvp-spec.md", "- Bee\n", "")
# R7-1 was already removed from product code/README/modes but this older MVP scope still listed it.
replace_once("docs/mvp-spec.md", "- Sex-difference Profile\n", "")

p = Path("docs/modes.md")
text = p.read_text()
updated, count = re.subn(r'\n### Bee\n.*?(?=\n### Bird-like)', '\n', text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f"docs/modes.md: expected one Bee section, found {count}")
p.write_text(updated)

# Limitations should no longer imply a public Bee image renderer exists.
p = Path("docs/limitations.md")
text = p.read_text()
text = text.replace(
    "Examples:\n- bee mode does not reproduce ultraviolet vision;\n- bird-like mode does not reproduce ultraviolet response or full avian perception;\n- dog and cat modes are simplified visible-range approximations.\n",
    "Examples:\n- bird-like mode does not reproduce ultraviolet response or full avian perception;\n- dog and cat modes are simplified visible-range approximations.\n- Bee-like is not publicly rendered from ordinary RGB because ultraviolet/spectral scene information is absent.\n",
    1,
)
text = text.replace(
    "### Bee-like spatial source-data limitation\nA future spatial scene does not create missing UV information automatically. Bee-like UV work requires additional UV-reflectance/spectral scene/material data and an explicit false-color translation for human displays. Until those inputs exist, Bee-like spatial is blocked and no purple/blue RGB filter should be presented as bee vision.\n",
    "### Bee-like source-data limitation\nBee-like image and spatial rendering are both blocked from ordinary RGB. A conventional image has already collapsed the ultraviolet/spectral information needed to estimate honeybee UV/blue/green receptor relationships, so a visible RGB color shift is not retained as a public bee-view proxy.\n\nFuture Bee-like work requires additional UV-reflectance/spectral scene or material data and an explicit false-color translation for human displays. Until those inputs exist, no purple/blue RGB filter should be presented as bee vision.\n",
    1,
)
p.write_text(text)

# Release schedule: close R7-1 and define R7-2 removal + acceptance gate.
p = Path("docs/release-polish-schedule.md")
text = p.read_text()
text = text.replace(
    "### R7-1 — Sex-difference Profile\nDecision: **REMOVE from the product**\n",
    "### R7-1 — Sex-difference Profile\nStatus: **PASS / removed / production verified**\n\nDecision: **REMOVE from the product**\n",
    1,
)
text = text.replace(
    "Acceptance:\n- Reference category exposes Age Profile only;\n- no `sex` transform or Sex-difference Evidence entry remains;\n- existing Human / Animal image modes remain selectable;\n- accepted spatial modes remain unchanged;\n- build and browser regression pass.\n\n## Current next action\nComplete R7-1 removal and validation. Then audit the remaining public Model D animal image modes in this order: Bee-like, Bird-like.\n",
    "Acceptance:\n- Reference category exposes Age Profile only;\n- no `sex` transform or Sex-difference Evidence entry remains;\n- existing Human / Animal image modes remain selectable;\n- accepted spatial modes remain unchanged;\n- build and browser regression pass.\n\nValidation:\n- removal/build/full local browser regression workflow `34015800962` — **success**;\n- production smoke `34015953222` — **success**, detected Reference = Age Profile only on attempt 1;\n- matching main build `34015953216` — **success**.\n\n### R7-2 — Bee-like image mode\nStatus: **ACTIVE — removal implementation**\n\nDecision: **REMOVE from the public image product until UV/spectral source data exists**\n\nReason:\n- honeybee UV/blue/green color vision is well supported, so the phenomenon Evidence remains strong;\n- the current image implementation is Model D because a conventional RGB image has already discarded ultraviolet/spectral information;\n- the public transform only remaps visible RGB channels and cannot reconstruct UV response, nectar-guide structure, receptor catches, or bee-specific scene coding;\n- strengthening the RGB color shift would make the output more dramatic without making it more biologically defensible;\n- the spatial Bee-like gate is already blocked for the same missing-source-data reason, so keeping a weaker image-only pseudo-bee view is inconsistent.\n\nRemoval scope:\n- remove Bee-like from the public Animal mode list;\n- remove the arbitrary RGB bee transform branch;\n- remove the public Bee-specific Evidence entry;\n- update README, MVP/mode documentation, and limitations to state Bee-like is unavailable until a spectral/UV data path exists;\n- keep the scientific/source-data decision in this schedule and spatial documentation.\n\nAcceptance:\n- Animal image category exposes Dog-like, Cat-like, and Bird-like only;\n- no `bee` image transform or Bee-like Evidence entry remains;\n- production smoke confirms Bee-like is absent from the public image UI;\n- accepted spatial controls remain unchanged;\n- build and desktop/390px browser regression pass.\n\n## Current next action\nComplete R7-2 removal and production verification. Then audit Bird-like, the remaining public Model D animal image mode.\n",
    1,
)
p.write_text(text)

# Production smoke should wait for the Bee removal deployment, not merely an older blob-capable release.
p = Path(".github/production-smoke.mjs")
text = p.read_text()
text = text.replace(
    'const expectedSpatialModes = [\n',
    'const expectedAnimalImageModes = ["dog", "cat", "bird"];\nconst expectedSpatialModes = [\n',
    1,
)
old = '''    let currentReferenceSet = false;\n    try {\n      await page.locator("#category-select").selectOption("Reference");\n      const referenceOptions = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => ({ value: node.value, text: node.textContent })));\n      currentReferenceSet = JSON.stringify(referenceOptions) === JSON.stringify([{ value: "age", text: "Age Profile" }]);\n    } catch {\n      currentReferenceSet = false;\n    }\n\n    if (src?.startsWith("blob:") && currentReferenceSet) {\n      result.productionReleaseDetected = true;\n      result.notes.push(`current production behavior detected on attempt ${attempt}; Reference exposes Age Profile only`);\n      return;\n    }\n\n    result.notes.push(`attempt ${attempt}: production is stale for blob upload and/or Reference mode set`);\n'''
new = '''    let currentReferenceSet = false;\n    let currentAnimalSet = false;\n    try {\n      await page.locator("#category-select").selectOption("Reference");\n      const referenceOptions = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => ({ value: node.value, text: node.textContent })));\n      currentReferenceSet = JSON.stringify(referenceOptions) === JSON.stringify([{ value: "age", text: "Age Profile" }]);\n      await page.locator("#category-select").selectOption("Animal");\n      const animalValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));\n      currentAnimalSet = JSON.stringify(animalValues) === JSON.stringify(expectedAnimalImageModes);\n    } catch {\n      currentReferenceSet = false;\n      currentAnimalSet = false;\n    }\n\n    if (src?.startsWith("blob:") && currentReferenceSet && currentAnimalSet) {\n      result.productionReleaseDetected = true;\n      result.notes.push(`current production behavior detected on attempt ${attempt}; Reference=Age only and Bee-like image mode absent`);\n      return;\n    }\n\n    result.notes.push(`attempt ${attempt}: production is stale for blob upload, Reference set, and/or Animal image set`);\n'''
if old not in text:
    raise SystemExit("production-smoke.mjs: release gate anchor not found")
text = text.replace(old, new, 1)
old = '''  await page.locator("#category-select").selectOption("Human");\n\n  const split = page.getByRole("button", { name: "Split" });\n'''
new = '''  await page.locator("#category-select").selectOption("Animal");\n  const animalValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));\n  assert(JSON.stringify(animalValues) === JSON.stringify(expectedAnimalImageModes), `desktop image: unexpected Animal image modes ${JSON.stringify(animalValues)}`);\n  assert(!(await page.locator("body").innerText()).includes("Bee-like"), "desktop image: removed Bee-like image mode is still visible");\n  await page.locator("#category-select").selectOption("Human");\n\n  const split = page.getByRole("button", { name: "Split" });\n'''
if old not in text:
    raise SystemExit("production-smoke.mjs: desktop animal gate anchor not found")
text = text.replace(old, new, 1)
p.write_text(text)

# Sanity checks.
checks = {
    "src/modes.ts": ["Bee-like", 'key: "bee"'],
    "src/transformEngine.ts": ['modeKey === "bee"'],
    "src/modeEvidence.ts": ['\n  bee: {'],
    "README.md": ["- Bee-like"],
    "docs/mvp-spec.md": ["- Bee\n", "- Sex-difference Profile"],
    "docs/modes.md": ["### Bee\n"],
}
for path, needles in checks.items():
    contents = Path(path).read_text()
    for needle in needles:
        if needle in contents:
            raise SystemExit(f"{path}: removed content still present: {needle!r}")
