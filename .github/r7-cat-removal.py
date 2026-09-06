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
    r'\n  \{ key: "cat", label: "Cat-like", category: "Animal", confidence: "Estimated", note: "Cat-like visible-range approximation based on commonly described feline characteristics\." \},',
    "",
)

sub_once(
    "src/transformEngine.ts",
    r'  \} else if \(modeKey === "cat"\) \{\n    applyColorDeficiency\(data, amount \* 0\.7, \[\[0\.7, 0\.3, 0\], \[0\.25, 0\.75, 0\], \[0\.05, 0\.25, 0\.7\]\]\);\n    desaturateData\(data, 0\.14 \+ amount \* 0\.12\);\n  \} else if \(modeKey === "age"\) \{',
    '  } else if (modeKey === "age") {',
)
replace_once(
    "src/transformEngine.ts",
    '  if (modeKey === "dog" || modeKey === "cat") {\n',
    '  if (modeKey === "dog") {\n',
)

sub_once(
    "src/modeEvidence.ts",
    r'\n  cat: \{.*?\n  \},\n  age: \{',
    "\n  age: {",
    re.S,
)

replace_once("README.md", "- Cat-like\n", "")
replace_once("docs/mvp-spec.md", "- Cat\n", "")
sub_once(
    "docs/modes.md",
    r'\n### Cat\n.*?(?=\n## Reference modes)',
    "\n",
    re.S,
)

replace_once(
    "docs/limitations.md",
    "Examples:\n- dog and cat modes are simplified visible-range approximations.\n- Bird-like is not publicly rendered from ordinary RGB because a generic avian observer cannot be reconstructed from three camera channels.\n- Bee-like is not publicly rendered from ordinary RGB because ultraviolet/spectral scene information is absent.\n",
    "Examples:\n- Dog-like remains a simplified visible-range approximation.\n- Cat-like is no longer publicly rendered because the former RGB proxy was not independently justified strongly enough from Dog-like.\n- Bird-like is not publicly rendered from ordinary RGB because a generic avian observer cannot be reconstructed from three camera channels.\n- Bee-like is not publicly rendered from ordinary RGB because ultraviolet/spectral scene information is absent.\n",
)
replace_once(
    "docs/limitations.md",
    "### Cat-like spatial evaluation limitation\nThe separate spatial Cat-like candidate was rejected after same-camera review because its visible distinction from Dog-like was mainly a small increase in chromatic compression/desaturation and fine-detail softening. The current RGB source does not justify manufacturing a stronger feline-specific distinction.\n\nThe image-track Cat-like mode remains an explicitly cautious visible-range approximation. There is no accepted public Cat-like spatial renderer at this stage.\n",
    "### Cat-like image and spatial evaluation limitation\nThe separate spatial Cat-like candidate was rejected after same-camera review because its visible distinction from Dog-like was mainly small chromatic and softening changes. R7 later audited the image renderer against Dog-like on the built-in sample and a controlled color/detail chart and reached the same product conclusion: the former Cat-specific RGB matrix was a heuristic, not a transform derived from measured feline cone catches or a validated feline observer model.\n\nDomestic-cat dichromatic color behavior has research support, but that evidence does not validate the former hand-tuned Dog-versus-Cat RGB difference. The public Cat-like image mode was therefore removed rather than strengthened. A future Cat-like renderer requires a documented feline observer mapping and source-data assumptions strong enough to justify a separate species-specific output.\n",
)

replace_once(
    "docs/roadmap.md",
    "The image-track Cat-like mode remains available as an explicitly cautious visible-range approximation. The rejected spatial candidate is not added to the public spatial controls.\n",
    "R7 subsequently audited the image-track Cat-like output against Dog-like on both the built-in sample and a controlled color/detail chart. The remaining distinction was dominated by modest hand-tuned RGB/softening differences rather than a validated feline observer mapping, so the public Cat-like image mode was also removed. Future Cat-like work must justify a separate feline renderer with an explicit observer model rather than manufacture a larger visual gap.\n",
)

replace_once(
    ".github/production-smoke.mjs",
    'const expectedAnimalImageModes = ["dog", "cat"];',
    'const expectedAnimalImageModes = ["dog"];',
)
replace_once(
    ".github/production-smoke.mjs",
    'result.notes.push(`current production behavior detected on attempt ${attempt}; Reference=Age only and Bee-like/Bird-like image modes absent`);',
    'result.notes.push(`current production behavior detected on attempt ${attempt}; Reference=Age only and Animal image set=Dog-like only`);',
)
replace_once(
    ".github/production-smoke.mjs",
    '  assert(!animalBodyText.includes("Bird-like"), "desktop image: removed Bird-like image mode is still visible");\n',
    '  assert(!animalBodyText.includes("Bird-like"), "desktop image: removed Bird-like image mode is still visible");\n  assert(!animalBodyText.includes("Cat-like"), "desktop image: removed Cat-like image mode is still visible");\n',
)

schedule = Path("docs/release-polish-schedule.md")
text = schedule.read_text()
text = text.replace(
    "### R7-3 — Bird-like image mode\nStatus: **ACTIVE — branch implementation validated**",
    "### R7-3 — Bird-like image mode\nStatus: **PASS / removed / production verified**",
    1,
)
old_next = """## Current next action
Open the clean R7-3 PR, require the normal PR build, merge only if green, then require public production smoke to observe Dog-like / Cat-like as the complete Animal image set before marking R7-3 PASS.
"""
new_next = """### R7-4 — Cat-like image mode
Status: **ACTIVE — removal implementation**

Decision: **REMOVE the public Cat-like image mode**

Reason:
- domestic-cat behavioral work supports a dichromatic tendency, but it does not validate the former Cat-specific hand-tuned RGB matrix used by AsSeenBy;
- the existing image renderer differed from Dog-like through a different ad-hoc 3×3 RGB remap, extra desaturation, and the same blur family rather than a feline cone-catch or observer model;
- spatial Cat-like had already been rejected because its rendered distinction from Dog-like was not explanatory enough to justify a separate species claim;
- corrected image-output audit `34019040004` reached the same conclusion on the 2D renderer.

Output-audit result (`34019040004`):
- built-in sample, Dog vs Cat mean absolute channel delta at Strength 40 / 70 / 100: **3.10 / 4.65 / 6.16**;
- built-in sample, pixels with any channel delta >=25 between Dog and Cat: **0% at all three strengths**; maximum channel delta only **13 / 15 / 18**;
- controlled color/detail chart, Dog vs Cat mean delta: **5.14 / 6.49 / 8.84**;
- controlled chart, pixels with any channel delta >=25: **0.0028% / 0.0013% / 0.0011%**;
- each mode's change from Original was materially larger than the Dog-versus-Cat separation, so the distinct Cat control mainly communicated a small renderer-specific RGB tuning difference.

Removal scope:
- remove Cat-like from the public Animal image list;
- remove the Cat image transform and Cat-specific public Evidence entry;
- narrow the shared post-transform blur path to Dog-like only;
- update README, MVP/mode docs, limitations, and roadmap wording;
- change production smoke so the complete accepted Animal image set is Dog-like only;
- keep feline evidence and the rejection rationale documented as a future-model requirement rather than a public transform.

Acceptance:
- Animal image category exposes Dog-like only;
- no `cat` image transform or Cat-like public Evidence entry remains;
- Reference remains Age Profile only;
- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;
- desktop and 390px browser checks pass without overflow or page/console errors;
- build passes;
- after merge, production smoke confirms Cat-like is absent and Dog-like is the only public Animal image mode.

## Current next action
Complete and validate the R7-4 removal branch, open a clean PR, merge only after the normal PR build passes, then require the public production smoke to observe Dog-like as the complete Animal image set before marking R7-4 PASS.
"""
if old_next not in text:
    raise SystemExit("release schedule current-next-action marker not found")
schedule.write_text(text.replace(old_next, new_next, 1))
