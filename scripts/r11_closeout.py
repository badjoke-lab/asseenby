from pathlib import Path

path = Path("docs/release-polish-schedule.md")
text = path.read_text()

replacements = {
    "Status: **Step R11 ACTIVE / CVD model fidelity / R10 Strength semantics production verified**":
        "Status: **Step R11 PASS / CVD model fidelity production verified / R10 Strength semantics production verified**",
    "## Step R11 — CVD model fidelity\nStatus: **ACTIVE — implementation / validation**":
        "## Step R11 — CVD model fidelity\nStatus: **PASS / production verified**",
    "- controlled browser color patches for Protan / Deutan / Tritan at Strength 10/40/70/100 agree with an independent Machado pre-computed-matrix calculation within the small tolerance required by the JPEG output path;":
        "- controlled browser color patches for Protan / Deutan / Tritan at Strength 10/40/70/100 agree with an independent Machado pre-computed-matrix calculation within the small tolerance required by the JPEG output path — **PASS**;",
    "- Strength 0 remains exact Original through the R10 invariant;":
        "- Strength 0 remains exact Original through the R10 invariant — **PASS**;",
    "- no custom red-green/blue-yellow post-compression is applied to the three Human CVD modes;":
        "- no custom red-green/blue-yellow post-compression is applied to the three Human CVD modes — **PASS**;",
    "- Dog-like renderer behavior remains on its existing separate proxy path;":
        "- Dog-like renderer behavior remains on its existing separate proxy path — **PASS**;",
    "- build and full desktop/390px image + spatial browser regression remain green;":
        "- build and full desktop/390px image + spatial browser regression remain green — **PASS**;",
    "- matching main build and production smoke pass after merge before R11 is marked production verified.\n\n## Current next action\nValidate the R11 Protan/Deutan/Tritan browser outputs against an independent Machado matrix calculation at Strength 10/40/70/100, then run the full image/spatial browser regression. Open a clean PR only if both gates pass.":
        "- matching main build and production smoke pass after merge before R11 is marked production verified — **PASS**.\n\nValidation:\n- corrected R11 CVD fidelity validation v2 `34052635954` — **success**; browser output matched an independent Machado calculation for Protan / Deutan / Tritan at Strength 10 / 15 / 40 / 70 / 100, including interpolation between adjacent 0.1 matrices at 15%;\n- the same run completed the full desktop/390px image + spatial browser regression — **success**;\n- PR #31 build `34066924253` — **success**;\n- PR #31 squash-merged as `cb41cca5ebd2641602b7f3bb6867ad2086b43063`;\n- matching main build `34066953225` — **success**;\n- production smoke `34066953211` — **success**.\n\n## Current next action\nR11 is closed. Re-read the roadmap and audit the remaining retained image transforms one by one for a concrete evidence/implementation mismatch. Do not create a new numbered release step unless an actual defect or unsupported model behavior is found."
}

for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one anchor, found {count}: {old[:100]!r}")
    text = text.replace(old, new, 1)

path.write_text(text)
