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
    r'\n  \{ key: "dry_eye", label: "Dry-eye-like", category: "Human", confidence: "Estimated", note: "Uneven blur and glare approximation\." \},',
    "",
)

sub_once(
    "src/transformEngine.ts",
    r'\n  if \(modeKey === "dry_eye"\) \{\n    renderBlurred\(ctx, baseCanvas, width, height, 0\.4 \+ amount \* 2\.1\);\n    addDryEyeOverlay\(ctx, width, height, amount\);\n    return;\n  \}\n',
    "\n",
)
sub_once(
    "src/transformEngine.ts",
    r'\nfunction addDryEyeOverlay\(ctx: CanvasRenderingContext2D, width: number, height: number, amount: number\) \{.*?\n\}\n',
    "\n",
    re.S,
)

sub_once(
    "src/modeEvidence.ts",
    r'\n  dry_eye: \{.*?\n  \},\n  dog: \{',
    "\n  dog: {",
    re.S,
)

replace_once("README.md", "- Dry-eye-like\n", "")
replace_once("docs/mvp-spec.md", "- Dry-eye-like\n", "")
sub_once(
    "docs/modes.md",
    r'\n### Dry-eye-like\n- class: Estimated\n- goal: uneven blur and glare approximation\n',
    "\n",
)

replace_once(
    "docs/limitations.md",
    "- Fatigue-like is no longer public because digital eye strain is a symptom cluster rather than one validated visual phenotype, and the former renderer only combined generic blur with contrast reduction;\n- current image tunnel and central-loss views are simplified transforms;\n",
    "- Fatigue-like is no longer public because digital eye strain is a symptom cluster rather than one validated visual phenotype, and the former renderer only combined generic blur with contrast reduction;\n- Dry-eye-like is no longer public because blur/fluctuating clarity are real symptoms but the former static renderer added fixed localized artifacts that were not derived from tear-film measurements or a validated dry-eye observer model;\n- current image tunnel and central-loss views are simplified transforms;\n",
)

smoke = Path(".github/production-smoke.mjs")
text = smoke.read_text()
text = text.replace(
    'const expectedHumanImageModes = ["protan", "deutan", "tritan", "blur", "low_contrast", "cataract", "tunnel", "central_loss", "night", "dry_eye"];',
    'const expectedHumanImageModes = ["protan", "deutan", "tritan", "blur", "low_contrast", "cataract", "tunnel", "central_loss", "night"];',
    1,
)
text = text.replace(
    '      result.notes.push(`current production behavior detected on attempt ${attempt}; Human set excludes Fatigue-like, Reference=Age only, Animal=Dog-like only`);',
    '      result.notes.push(`current production behavior detected on attempt ${attempt}; Human set excludes Fatigue-like/Dry-eye-like, Reference=Age only, Animal=Dog-like only`);',
    1,
)
text = text.replace(
    '  assert(!(await page.locator("body").innerText()).includes("Fatigue-like"), "desktop image: removed Fatigue-like mode is still visible");\n',
    '  const humanBodyText = await page.locator("body").innerText();\n  assert(!humanBodyText.includes("Fatigue-like"), "desktop image: removed Fatigue-like mode is still visible");\n  assert(!humanBodyText.includes("Dry-eye-like"), "desktop image: removed Dry-eye-like mode is still visible");\n',
    1,
)
smoke.write_text(text)

schedule = Path("docs/release-polish-schedule.md")
text = schedule.read_text()
text = text.replace(
    "### R7-5 — Fatigue-like image mode\nStatus: **ACTIVE — removal implementation**",
    "### R7-5 — Fatigue-like image mode\nStatus: **PASS / removed / production verified**",
    1,
)
old_next = """## Current next action
Complete and validate the R7-5 Fatigue-like removal branch, open a clean PR, merge only if the normal PR build is green, then require production smoke to observe the exact Human set with Fatigue-like absent.
"""
new_next = """Validation:
- removal/build/desktop + 390px + spatial regression `34026264093` — **success**;
- PR #17 build `34026349097` — **success**;
- merge SHA `8a8b300546bbddc6fcdbaa98a56e308bc3d81b49`;
- matching main build `34026381562` — **success**;
- production smoke `34026381544` — **success**, confirming the exact Human set without Fatigue-like while Animal=Dog-like, Reference=Age Profile, and the accepted six spatial controls remained unchanged.

### R7-6 — Dry-eye-like image mode
Status: **ACTIVE — removal implementation**

Decision: **REMOVE the public Dry-eye-like image mode**

Reason:
- dry eye can produce blur and fluctuating clarity, but that does not establish one stable static appearance shared by affected viewers;
- the Evidence entry is B / Model C and already describes the renderer as heuristic;
- the current transform applies general blur and then draws six fixed radial bright spots at deterministic positions unrelated to measured tear-film breakup, corneal optics, or patient data;
- the static v0.1 image track cannot represent the time-varying clarity that is one of the mode's main stated phenomena;
- strengthening the fixed artifact pattern would make the output more visually distinctive without making it more scientifically defensible.

Removal scope:
- remove Dry-eye-like from the public Human mode list;
- remove the dry-eye transform branch, fixed artifact helper, and public dry-eye Evidence entry;
- update README, MVP/mode documentation, and limitations;
- strengthen production smoke so the exact Human set excludes both Fatigue-like and Dry-eye-like;
- leave Night / Low Light as the remaining Estimated Human mode for a separate audit.

Acceptance:
- Human image modes are Protan-like, Deutan-like, Tritan-like, Blur, Low Contrast, Cataract-like, Tunnel Vision, Central Loss, and Night / Low Light;
- no `dry_eye` transform, fixed dry-eye overlay helper, or Dry-eye-like public Evidence entry remains;
- Animal remains Dog-like only and Reference remains Age Profile only;
- accepted spatial controls remain exactly Normal, Tunnel Vision, Central Loss, Night / Low Light, Dog-like, and Cataract-like;
- desktop and 390px image/spatial regression passes without overflow or page/console errors;
- build passes;
- after merge, production smoke must observe the exact Human set without Dry-eye-like before R7-6 is marked PASS.

## Current next action
Complete and validate the R7-6 Dry-eye-like removal branch, open a clean PR, merge only if the normal PR build is green, then require production smoke to observe the exact Human set without Dry-eye-like.
"""
if old_next not in text:
    raise SystemExit("release schedule current-next-action marker not found")
schedule.write_text(text.replace(old_next, new_next, 1))
