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
    r'\n  \{ key: "night", label: "Night / Low Light", category: "Human", confidence: "Estimated", note: "Low-light viewing approximation\." \},',
    "",
)

sub_once(
    "src/transformEngine.ts",
    r'\n  if \(modeKey === "night"\) \{.*?\n    return;\n  \}\n',
    "\n",
    re.S,
)

replace_once("README.md", "- Night / Low Light\n", "")
replace_once("docs/mvp-spec.md", "\n### Estimated\n- Night / Low Light\n", "")

replace_once(
    "docs/modes.md",
    "### Night / Low Light\n- class: Estimated\n- goal: low-light viewing approximation\n- spatial status: accepted post-pilot mode\n",
    "### Night / Low Light\n- class: Estimated\n- goal: low-light viewing approximation\n- image status: removed in R7; the former static RGB transform was not retained as a validated low-light observer model\n- spatial status: accepted post-pilot mode\n",
)

replace_once(
    "docs/limitations.md",
    "### Night / Low Light specific limitation\nThe current spatial Night / Low Light mode can use relative brightness differences in the rendered panorama, but the source is a tone-mapped RGB photograph rather than calibrated luminance or spectral data.\n",
    "### Night / Low Light specific limitation\nThe former static-image Night / Low Light mode was removed in R7. A conventional uploaded RGB image has unknown exposure, tone mapping, scene luminance, and adaptation context, so applying a uniform dark/desaturated transform would imply a low-light observer state that the input does not establish.\n\nThe current spatial Night / Low Light mode remains because it can at least use relative brightness differences in the rendered panorama, but the source is still a tone-mapped RGB photograph rather than calibrated luminance or spectral data.\n",
)

smoke = Path(".github/production-smoke.mjs")
text = smoke.read_text()
text = text.replace(
    'const expectedHumanImageModes = ["protan", "deutan", "tritan", "blur", "low_contrast", "cataract", "tunnel", "central_loss", "night"];',
    'const expectedHumanImageModes = ["protan", "deutan", "tritan", "blur", "low_contrast", "cataract", "tunnel", "central_loss"];',
    1,
)
text = text.replace(
    '      result.notes.push(`current production behavior detected on attempt ${attempt}; Human set excludes Fatigue-like/Dry-eye-like, Reference=Age only, Animal=Dog-like only`);',
    '      result.notes.push(`current production behavior detected on attempt ${attempt}; image Human set excludes Fatigue-like/Dry-eye-like/Night, Reference=Age only, Animal=Dog-like only`);',
    1,
)
text = text.replace(
    '  assert(!humanBodyText.includes("Dry-eye-like"), "desktop image: removed Dry-eye-like mode is still visible");\n',
    '  assert(!humanBodyText.includes("Dry-eye-like"), "desktop image: removed Dry-eye-like mode is still visible");\n  assert(!humanBodyText.includes("Night / Low Light"), "desktop image: removed Night / Low Light image mode is still visible");\n',
    1,
)
smoke.write_text(text)

schedule = Path("docs/release-polish-schedule.md")
text = schedule.read_text()
text = text.replace(
    "### R7-6 — Dry-eye-like image mode\nStatus: **ACTIVE — removal implementation**",
    "### R7-6 — Dry-eye-like image mode\nStatus: **PASS / removed / production verified**",
    1,
)
old_next = """## Current next action
Complete and validate the R7-6 Dry-eye-like removal branch, open a clean PR, merge only if the normal PR build is green, then require production smoke to observe the exact Human set without Dry-eye-like.
"""
new_next = """Validation:
- removal/build/desktop + 390px + spatial regression `34026610348` — **success**;
- PR #18 build `34026698193` — **success**;
- merge SHA `d408ac2c054e54772753bd2f77ff545c1debfb58`;
- matching main build `34026734382` — **success**;
- production smoke `34026734384` — **success**, confirming the exact Human image set without Dry-eye-like while Animal=Dog-like, Reference=Age Profile, and all six spatial controls remained unchanged.

### R7-7 — Night / Low Light image mode
Status: **ACTIVE — removal implementation**

Decision: **REMOVE the static-image Night / Low Light mode; KEEP the accepted spatial mode**

Reason:
- the image Evidence entry is B / Model C and explicitly calls the transform heuristic rather than a validated scotopic model;
- an uploaded RGB image does not establish absolute scene luminance, camera exposure/tone mapping, pupil state, or dark-adaptation state;
- the static renderer applies a global dark/desaturated color transform, so it can manufacture a low-light appearance even when the source image does not contain the information needed to define one;
- the spatial implementation is materially different: it uses live rendered relative luminance so darker regions lose more chromatic/contrast/detail information while brighter sources remain comparatively available;
- removing the image mode does not remove the shared scientific Evidence needed by `spatialEvidence.ts`.

Removal scope:
- remove Night / Low Light from the public Human image list;
- remove only the static `night` transform branch;
- retain the `night` Evidence entry because the spatial Evidence layer extends it;
- retain the spatial Night / Low Light shader and control;
- update README, MVP/mode docs, limitations, release schedule, and production smoke.

Acceptance:
- Human image modes are Protan-like, Deutan-like, Tritan-like, Blur, Low Contrast, Cataract-like, Tunnel Vision, and Central Loss;
- image `night` is not selectable and the old static transform branch is gone;
- spatial Night / Low Light remains one of the exact six accepted spatial controls and its Evidence panel still resolves;
- Animal remains Dog-like only and Reference remains Age Profile only;
- desktop and 390px image/spatial regression passes without overflow or page/console errors;
- build passes;
- after merge, production smoke must observe the exact 8-mode Human image set while still exercising the six-mode spatial set.

## Current next action
Complete and validate R7-7, merge only after the normal PR build passes, and require production smoke to confirm image Night is absent while spatial Night remains present.
"""
if old_next not in text:
    raise SystemExit("release schedule current-next-action marker not found")
schedule.write_text(text.replace(old_next, new_next, 1))
