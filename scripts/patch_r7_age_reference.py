from pathlib import Path
import re


def replace_once(path: str, old: str, new: str, label: str) -> None:
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label} in {path}")
    p.write_text(text.replace(old, new, 1))


# Product model: no public Reference category remains after removing the undefined Age Profile.
replace_once(
    "src/modes.ts",
    'export type ModeCategory = "Human" | "Animal" | "Reference";',
    'export type ModeCategory = "Human" | "Animal";',
    "ModeCategory union",
)
replace_once(
    "src/modes.ts",
    '  { key: "age", label: "Age Profile", category: "Reference", confidence: "Reference", note: "Age-related viewing profile approximation." },\n',
    '',
    "Age Profile mode",
)

replace_once(
    "src/transformEngine.ts",
    '''  } else if (modeKey === "age") {\n    applyLowContrastToData(data, 0.12 + amount * 0.16);\n    warmTintData(data, 0.04 + amount * 0.08);\n''',
    '',
    "Age image transform",
)

# Remove Age evidence entry; the underlying literature remains documented in the R7 decision, but no renderer claims it.
p = Path("src/modeEvidence.ts")
text = p.read_text()
pattern = re.compile(r'\n  age: \{\n.*?\n  \},\n\};\n\nexport function getModeEvidence', re.S)
match = pattern.search(text)
if not match:
    raise SystemExit("missing Age evidence block")
text = text[:match.start()] + '\n};\n\nexport function getModeEvidence' + text[match.end():]
p.write_text(text)

replace_once(
    "src/App.tsx",
    '  const referenceModes = MODES.filter((mode) => mode.category === "Reference");\n',
    '',
    "referenceModes variable",
)
replace_once(
    "src/App.tsx",
    '            <CategoryPanel title="Reference" subtitle="Profiles based on research and averages." items={referenceModes.map((mode) => mode.label)} icon={<ChartSketch className="mini-plate" />} onClick={() => setCategory("Reference")} />\n',
    '',
    "Reference category panel",
)
replace_once(
    "src/App.tsx",
    '        <SelectLike id="category-select" value={category} options={["Human", "Animal", "Reference"]} onChange={(value) => setCategory(value as ModeCategory)} />',
    '        <SelectLike id="category-select" value={category} options={["Human", "Animal"]} onChange={(value) => setCategory(value as ModeCategory)} />',
    "category select options",
)

# Production smoke: exact public image categories are now Human + Animal only.
p = Path(".github/production-smoke.mjs")
text = p.read_text()
text = text.replace('    let currentReferenceSet = false;\n', '')
text = text.replace(
    '''      await page.locator("#category-select").selectOption("Reference");\n      const referenceOptions = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => ({ value: node.value, text: node.textContent })));\n      currentReferenceSet = JSON.stringify(referenceOptions) === JSON.stringify([{ value: "age", text: "Age Profile" }]);\n''',
    '''      const categoryValues = await page.locator("#category-select option").evaluateAll((nodes) => nodes.map((node) => node.value));\n      if (JSON.stringify(categoryValues) !== JSON.stringify(["Human", "Animal"])) throw new Error(`unexpected image categories ${JSON.stringify(categoryValues)}`);\n''',
)
text = text.replace('      currentReferenceSet = false;\n', '')
text = text.replace('    if (src?.startsWith("blob:") && currentReferenceSet && currentAnimalSet && currentHumanSet) {', '    if (src?.startsWith("blob:") && currentAnimalSet && currentHumanSet) {')
text = text.replace('image Human set excludes Fatigue-like/Dry-eye-like/Night, Reference=Age only, Animal=Dog-like only', 'image categories are Human/Animal only, with the audited Human set and Animal=Dog-like only')
text = text.replace('production is stale for blob upload, Human set, Reference set, and/or Animal image set', 'production is stale for blob upload, Human/Animal category set, Human modes, and/or Animal modes')
text = text.replace('Production did not reach the current blob-upload + Reference-mode release behavior within the retry window.', 'Production did not reach the current blob-upload + Human/Animal-only release behavior within the retry window.')
text = text.replace(
    '''  await page.locator("#category-select").selectOption("Reference");\n  const referenceOptions = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => ({ value: node.value, text: node.textContent })));\n  assert(JSON.stringify(referenceOptions) === JSON.stringify([{ value: "age", text: "Age Profile" }]), `desktop image: unexpected Reference modes ${JSON.stringify(referenceOptions)}`);\n  assert(!(await page.locator("body").innerText()).includes("Sex-difference Profile"), "desktop image: removed Sex-difference Profile is still visible");\n''',
    '''  const categoryValues = await page.locator("#category-select option").evaluateAll((nodes) => nodes.map((node) => node.value));\n  assert(JSON.stringify(categoryValues) === JSON.stringify(["Human", "Animal"]), `desktop image: unexpected categories ${JSON.stringify(categoryValues)}`);\n  const pageText = await page.locator("body").innerText();\n  assert(!pageText.includes("Age Profile"), "desktop image: removed Age Profile is still visible");\n  assert(!pageText.includes("Sex-difference Profile"), "desktop image: removed Sex-difference Profile is still visible");\n''',
)
p.write_text(text)

# README / product docs.
replace_once("README.md", '- Human / Animal / Reference mode groups', '- Human / Animal mode groups', "README mode groups")
replace_once("README.md", '''### Reference\n\n- Age Profile\n\n''', '', "README Reference section")
replace_once("README.md", '* Human, animal, and reference outputs are research-based approximations.', '* Human and animal outputs are research-based approximations.', "README output note")

replace_once("docs/mvp-spec.md", '- human / animal / reference grouping', '- human / animal grouping', "MVP grouping")
replace_once("docs/mvp-spec.md", '''## Reference modes\n- Age Profile\n\n''', '', "MVP Reference modes")
replace_once("docs/mvp-spec.md", '- stronger animal/reference explanation', '- stronger animal explanation', "MVP explanation")

replace_once("docs/overview.md", 'different human visual conditions, animal approximations, and reference profiles.', 'different human visual conditions and animal approximations.', "overview premise")
replace_once("docs/overview.md", '''### Reference\nAverage-profile reference views that should not be treated as individual prediction.\n\n''', '', "overview Reference group")
replace_once("docs/overview.md", '\nReference modes represent averaged profiles only and should not be treated as individual-level predictions.\n', '\n', "overview Reference notice")

replace_once("docs/ui-spec.md", '- Human / Animal / Reference panels below', '- Human / Animal panels below', "UI panels")
replace_once("docs/ui-spec.md", '''## Labels\nEach existing mode should display one of:\n- Strong\n- Estimated\n- Reference\n''', '''## Labels\nEach current public mode should display one of:\n- Strong\n- Estimated\n\nThe evidence model may retain a Reference class for future explicitly defined reference datasets, but no public Reference mode is included in the current release.\n''', "UI labels")

replace_once("docs/modes.md", '''\n\n## Reference modes\n### Age Profile\n- class: Reference\n- goal: age-related viewing profile approximation''', '', "modes Reference section")

replace_once("docs/limitations.md", '''## Reference-mode limitation\nReference modes are averaged profiles, not individual predictions.\nThey are intended as framing tools for comparison.\n\n''', '', "Reference limitation")

p = Path("docs/methodology.md")
text = p.read_text()
text = text.replace(
    '''## Reference modes\nReference modes are deliberately weaker claims.\nThey represent averaged profiles rather than individual prediction.\n\nIncluded:\n- age profile;\n- sex-difference profile.\n\nThese should not be interpreted as personal diagnosis or exact individual simulation.\n\n''',
    '''## Reference-mode status\nThe current public release has no Reference modes. Earlier Age Profile and sex-difference presets were removed during R7 because their broad population labels did not define a sufficiently specific observer for the renderer. The evidence model retains a Reference class only for future datasets with an explicit population, variable, and mapping.\n\n''',
)
# Align the stale public animal list with the completed R7 audit.
text = text.replace(
    '''Included animal modes:\n- dog-like;\n- cat-like;\n- bee-like;\n- bird-like.\n\nImportant note:\n- bee and bird modes in v0.1 do not reproduce ultraviolet response;\n- none of the animal modes reproduce the full perceptual world of the species.\n''',
    '''Current public animal image mode:\n- dog-like.\n\nCat-like, Bird-like, and Bee-like image modes were removed during R7 because the former generic RGB transforms did not justify distinct species-specific observer claims. Dog-like remains a conservative visible-range proxy and does not reproduce the full canine perceptual world.\n''',
)
p.write_text(text)

# Release schedule: finish Dog production verification, then record the Age/Reference removal decision.
p = Path("docs/release-polish-schedule.md")
text = p.read_text()
old = '''- manual capture review retained the mode as a restrained visible-range comparison proxy; image Model remains **C**.\n\n## Current next action\nOpen the clean R7-8 PR, merge only if the normal PR build is green, then require main build and production smoke to remain green with Animal=Dog-like only and the accepted six spatial controls unchanged.'''
new = '''- manual capture review retained the mode as a restrained visible-range comparison proxy; image Model remains **C**;\n- PR #20 build `34035301890` — **success**;\n- merge SHA `31dbf2b50fd44fd5265639c16fa123b3c043cef7`;\n- matching main build `34035329766` — **success**;\n- production smoke `34035329745` — **success**, confirming Animal=Dog-like only and the accepted six spatial controls unchanged.\n\n### R7-9 — Age Profile / Reference category\nStatus: **ACTIVE — removal implementation**\n\nDecision: **REMOVE Age Profile and remove the now-empty public Reference category**\n\nReason:\n- age-related contrast sensitivity, glare, optical density and focusing changes are real, but they are not one stable visual phenotype;\n- chromatic adaptation can compensate substantially for progressive lens yellowing, so a fixed warm tint should not be presented as a generic older-person view;\n- the current Age Profile does not specify an age, age range, ocular status, lens density, pupil state, adaptation state, or measurement source for an individual/population observer;\n- the image renderer is only a broad low-contrast + warm-tint preset, so the label implies more specificity than the transform supports;\n- Sex-difference Profile was already removed, so Age Profile is the only remaining Reference item and removing it eliminates an otherwise empty category.\n\nRemoval scope:\n- remove `age` from public mode metadata, transform engine, and evidence registry;\n- remove Reference from the public image category selector and category cards;\n- update production smoke to require exactly Human + Animal image categories;\n- update README/MVP/overview/UI/methodology/modes/limitations documentation;\n- retain the generic `Reference` evidence-class concept for future explicitly defined datasets, but expose no current public Reference mode.\n\nAcceptance:\n- image category selector exposes exactly Human and Animal;\n- Age Profile and Sex-difference Profile are absent from public UI;\n- Human remains the exact audited 8-mode set;\n- Animal remains Dog-like only;\n- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;\n- desktop and 390px image/spatial regression passes without overflow or page/console errors;\n- build passes;\n- after merge, production smoke observes the Human/Animal-only image release.\n\n## Current next action\nApply R7-9 removal, run the patched production smoke against a local build at desktop/390px plus the accepted spatial controls, then open a PR only if the two-category release is clean.'''
if old not in text:
    raise SystemExit("missing R7-8 schedule anchor")
p.write_text(text.replace(old, new, 1))
