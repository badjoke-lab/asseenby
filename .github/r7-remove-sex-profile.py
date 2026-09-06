from pathlib import Path
import re


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected one match, found {text.count(old)}")
    p.write_text(text.replace(old, new, 1))


replace_once(
    "src/modes.ts",
    '  { key: "sex", label: "Sex-difference Profile", category: "Reference", confidence: "Reference", note: "Average-profile reference mode." },\n',
    "",
)

replace_once(
    "src/transformEngine.ts",
    '  } else if (modeKey === "sex") {\n    saturateData(data, amount * 0.04);\n    boostMicroContrast(data, amount * 0.015);\n',
    "",
)

p = Path("src/modeEvidence.ts")
text = p.read_text()
updated, count = re.subn(r'\n  sex: \{\n.*?\n  \},\n(?=\};)', '\n', text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f"src/modeEvidence.ts: expected one sex evidence block, found {count}")
p.write_text(updated)

replace_once(
    "README.md",
    '- Sex-difference Profile\n',
    "",
)

replace_once(
    "docs/modes.md",
    '\n### Sex-difference Profile\n- class: Reference\n- goal: averaged sex-difference reference mode\n- note: should not be treated as an individual-level prediction\n',
    "",
)

schedule = Path("docs/release-polish-schedule.md")
text = schedule.read_text()
old = '''## Step R7 — Image transform / evidence quality audit
Status: **ACTIVE**

Purpose: review currently public image modes whose implementation confidence is weak or conservative and decide mode-by-mode whether to keep, revise, narrow, or remove them. A visually different output is not enough; each public transform must have useful explanatory value within its evidence/model boundary.

Priority order:
1. Model D public modes and placeholders;
2. Model C modes where current transform behavior may overstate the evidence;
3. animal modes whose RGB-only limitation needs stronger UI handling;
4. reference profiles that risk implying population-wide truths.

Do not strengthen a transform merely to make it look more dramatic. Prefer removal or narrower labeling when the current source data cannot support a stronger model.

## Current next action
Start R7 by inventorying the public mode list against `modeEvidence.ts` and `transformEngine.ts`, then take the highest-risk weak mode through a keep/revise/remove decision before changing the next one.
'''
new = '''## Step R7 — Image transform / evidence quality audit
Status: **ACTIVE**

Purpose: review currently public image modes whose implementation confidence is weak or conservative and decide mode-by-mode whether to keep, revise, narrow, or remove them. A visually different output is not enough; each public transform must have useful explanatory value within its evidence/model boundary.

Priority order:
1. Model D public modes and placeholders;
2. Model C modes where current transform behavior may overstate the evidence;
3. animal modes whose RGB-only limitation needs stronger UI handling;
4. reference profiles that risk implying population-wide truths.

Do not strengthen a transform merely to make it look more dramatic. Prefer removal or narrower labeling when the current source data cannot support a stronger model.

### R7-1 — Sex-difference Profile
Decision: **REMOVE from the product**

Reason:
- Evidence score was C and Model score was D;
- the evidence set explicitly described reported differences as small, task-specific, heterogeneous, and insufficient for one broad perceptual profile;
- the implementation was only a tiny saturation/microcontrast adjustment and was explicitly described as a placeholder framing tool;
- making the transform stronger would create unsupported sex-wide visual claims rather than improve explanatory accuracy.

Removal scope:
- remove the public mode definition;
- remove the image transform branch;
- remove the mode-specific Evidence metadata;
- remove the mode from README and mode documentation;
- keep the product-level statement that reference profiles are averaged and non-individual for the remaining Age Profile.

Acceptance:
- Reference category exposes Age Profile only;
- no `sex` transform or Sex-difference Evidence entry remains;
- existing Human / Animal image modes remain selectable;
- accepted spatial modes remain unchanged;
- build and browser regression pass.

## Current next action
Complete R7-1 removal and validation. Then audit the remaining public Model D animal image modes in this order: Bee-like, Bird-like.
'''
if old not in text:
    raise SystemExit("docs/release-polish-schedule.md: R7 block anchor not found")
schedule.write_text(text.replace(old, new, 1))

# Public/product files should no longer contain the removed mode after this patch.
for path in ["src/modes.ts", "src/transformEngine.ts", "src/modeEvidence.ts", "README.md", "docs/modes.md"]:
    text = Path(path).read_text()
    if "Sex-difference Profile" in text or 'modeKey === "sex"' in text or '\n  sex: {' in text:
        raise SystemExit(f"{path}: removed sex profile still present")
