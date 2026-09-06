from pathlib import Path
import re


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"missing expected text in {path}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1))


def sub_once(path: str, pattern: str, repl: str, flags: int = 0) -> None:
    p = Path(path)
    text = p.read_text()
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"expected one regex match in {path}, got {n}: {pattern}")
    p.write_text(new)


sub_once(
    "src/modes.ts",
    r'\n  \{ key: "fatigue", label: "Fatigue-like", category: "Human", confidence: "Estimated", note: "Fatigue-related viewing softness approximation\." \},',
    "",
)

sub_once(
    "src/transformEngine.ts",
    r'\n  if \(modeKey === "fatigue"\) \{\n    renderBlurred\(ctx, baseCanvas, width, height, 0\.6 \+ amount \* 3\.2\);\n    const imageData = ctx\.getImageData\(0, 0, width, height\);\n    applyLowContrastToData\(imageData\.data, 0\.08 \+ amount \* 0\.12\);\n    ctx\.putImageData\(imageData, 0, 0\);\n    return;\n  \}\n',
    "\n",
)

sub_once(
    "src/modeEvidence.ts",
    r'\n  fatigue: \{.*?\n  \},\n  dry_eye: \{',
    "\n  dry_eye: {",
    re.S,
)

replace_once("README.md", "- Fatigue-like\n", "")
replace_once("docs/mvp-spec.md", "- Fatigue-like\n", "")
sub_once(
    "docs/modes.md",
    r'\n### Fatigue-like\n- class: Estimated\n- goal: fatigue-related viewing softness approximation\n',
    "\n",
)

replace_once(
    "docs/limitations.md",
    "Examples:\n- color-deficiency-like image modes are matrix-based approximations;\n- image blur and contrast modes are image-space approximations;\n- current image tunnel and central-loss views are simplified transforms;\n",
    "Examples:\n- color-deficiency-like image modes are matrix-based approximations;\n- image blur and contrast modes are image-space approximations;\n- Fatigue-like is no longer public because digital eye strain is a symptom cluster rather than one validated visual phenotype, and the former renderer only combined generic blur with contrast reduction;\n- current image tunnel and central-loss views are simplified transforms;\n",
)

smoke = Path(".github/production-smoke.mjs")
text = smoke.read_text()
text = text.replace(
    'const expectedAnimalImageModes = ["dog"];\n',
    'const expectedAnimalImageModes = ["dog"];\nconst expectedHumanImageModes = ["protan", "deutan", "tritan", "blur", "low_contrast", "cataract", "tunnel", "central_loss", "night", "dry_eye"];\n',
    1,
)
text = text.replace(
    '    let currentReferenceSet = false;\n    let currentAnimalSet = false;\n',
    '    let currentReferenceSet = false;\n    let currentAnimalSet = false;\n    let currentHumanSet = false;\n',
    1,
)
text = text.replace(
    '      currentAnimalSet = JSON.stringify(animalValues) === JSON.stringify(expectedAnimalImageModes);\n',
    '      currentAnimalSet = JSON.stringify(animalValues) === JSON.stringify(expectedAnimalImageModes);\n      await page.locator("#category-select").selectOption("Human");\n      const humanValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));\n      currentHumanSet = JSON.stringify(humanValues) === JSON.stringify(expectedHumanImageModes);\n',
    1,
)
text = text.replace(
    '      currentAnimalSet = false;\n',
    '      currentAnimalSet = false;\n      currentHumanSet = false;\n',
    1,
)
text = text.replace(
    '    if (src?.startsWith("blob:") && currentReferenceSet && currentAnimalSet) {\n',
    '    if (src?.startsWith("blob:") && currentReferenceSet && currentAnimalSet && currentHumanSet) {\n',
    1,
)
text = text.replace(
    '      result.notes.push(`current production behavior detected on attempt ${attempt}; Reference=Age only and Animal image set=Dog-like only`);\n',
    '      result.notes.push(`current production behavior detected on attempt ${attempt}; Human set excludes Fatigue-like, Reference=Age only, Animal=Dog-like only`);\n',
    1,
)
text = text.replace(
    '    result.notes.push(`attempt ${attempt}: production is stale for blob upload, Reference set, and/or Animal image set`);\n',
    '    result.notes.push(`attempt ${attempt}: production is stale for blob upload, Human set, Reference set, and/or Animal image set`);\n',
    1,
)
text = text.replace(
    '  await page.locator("#category-select").selectOption("Human");\n\n  const split = page.getByRole("button", { name: "Split" });\n',
    '  await page.locator("#category-select").selectOption("Human");\n  const humanValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));\n  assert(JSON.stringify(humanValues) === JSON.stringify(expectedHumanImageModes), `desktop image: unexpected Human image modes ${JSON.stringify(humanValues)}`);\n  assert(!(await page.locator("body").innerText()).includes("Fatigue-like"), "desktop image: removed Fatigue-like mode is still visible");\n\n  const split = page.getByRole("button", { name: "Split" });\n',
    1,
)
smoke.write_text(text)

schedule = Path("docs/release-polish-schedule.md")
text = schedule.read_text()
text = text.replace(
    "### R7-4 — Cat-like image mode\nStatus: **ACTIVE — removal implementation**",
    "### R7-4 — Cat-like image mode\nStatus: **PASS / removed / production verified**",
    1,
)
old_next = """## Current next action
Complete and validate the R7-4 removal branch, open a clean PR, merge only after the normal PR build passes, then require the public production smoke to observe Dog-like as the complete Animal image set before marking R7-4 PASS.
"""
new_next = """Validation:
- corrected Cat-like image-output audit `34019040004` — **success**;
- removal/build/desktop + 390px + spatial regression `34025906254` — **success**;
- PR #16 build `34025986307` — **success**;
- merge SHA `9b12e4d855f9e4b3be388812a43ba1e5e0990f04`;
- matching main build `34026021415` — **success**;
- production smoke `34026021476` — **success**, confirming Dog-like is the only public Animal image mode while Reference remains Age Profile and the accepted six spatial controls remain unchanged.

### R7-5 — Fatigue-like image mode
Status: **ACTIVE — removal implementation**

Decision: **REMOVE the public Fatigue-like image mode**

Reason:
- digital eye strain / visual fatigue is a symptom cluster, not one stable visual phenotype shared by affected viewers;
- the current Evidence entry is B / Model C and explicitly describes the renderer as a communication proxy rather than a validated fatigue-specific visual model;
- the public transform is only a mild generic blur followed by contrast reduction;
- Blur and Low Contrast already expose those visual effects directly without implying that a particular combined output is what “fatigue” looks like;
- strengthening the mode would manufacture specificity that the current evidence does not support.

Removal scope:
- remove Fatigue-like from the public Human mode list;
- remove the fatigue transform branch and public fatigue Evidence entry;
- update README, MVP/mode documentation, and limitations;
- strengthen production smoke so the accepted Human image set explicitly excludes Fatigue-like and stale deployments cannot pass;
- keep Dry-eye-like as the next separate Model C audit rather than conflating the two symptom categories.

Acceptance:
- Human image modes are Protan-like, Deutan-like, Tritan-like, Blur, Low Contrast, Cataract-like, Tunnel Vision, Central Loss, Night / Low Light, and Dry-eye-like;
- no `fatigue` transform or Fatigue-like public Evidence entry remains;
- Animal remains Dog-like only and Reference remains Age Profile only;
- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;
- desktop and 390px image/spatial regression passes without overflow or page/console errors;
- build passes;
- after merge, production smoke must observe the exact Human set without Fatigue-like before R7-5 is marked PASS.

## Current next action
Complete and validate the R7-5 Fatigue-like removal branch, open a clean PR, merge only if the normal PR build is green, then require production smoke to observe the exact Human set with Fatigue-like absent.
"""
if old_next not in text:
    raise SystemExit("release schedule current-next-action marker not found")
schedule.write_text(text.replace(old_next, new_next, 1))
