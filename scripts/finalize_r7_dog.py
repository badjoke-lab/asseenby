from pathlib import Path

path = Path("docs/release-polish-schedule.md")
text = path.read_text()
text = text.replace(
    '### R7-8 — Dog-like image mode\nStatus: **ACTIVE — renderer revision and output audit**',
    '### R7-8 — Dog-like image mode\nStatus: **PASS / revised / browser validated**',
    1,
)
old = '''- after merge, production smoke remains green with Animal=Dog-like only.\n\n## Current next action\nApply and browser-test the R7-8 Dog-like renderer revision, inspect its output against Original at multiple Strength levels, then open a PR only if the revised output remains useful and restrained.'''
new = '''- after merge, production smoke remains green with Animal=Dog-like only.\n\nValidation before PR:\n- renderer patch + typecheck/build + 1440px/390px Dog output + full spatial regression workflow `34035027559` — **success**;\n- controlled color/detail chart at Strength 40: mean absolute channel delta **12.75**, maximum channel delta **79**;\n- controlled color/detail chart at Strength 100: mean absolute channel delta **17.16**, maximum channel delta **89**;\n- the output therefore remains non-trivial and scales with Strength without requiring a bespoke canine RGB matrix;\n- manual capture review retained the mode as a restrained visible-range comparison proxy; image Model remains **C**.\n\n## Current next action\nOpen the clean R7-8 PR, merge only if the normal PR build is green, then require main build and production smoke to remain green with Animal=Dog-like only and the accepted six spatial controls unchanged.'''
if old not in text:
    raise SystemExit("missing R7-8 finalization anchor")
path.write_text(text.replace(old, new, 1))
