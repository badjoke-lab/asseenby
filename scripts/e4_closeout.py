from pathlib import Path

schedule = Path("docs/explore-3d-schedule.md")
text = schedule.read_text()
text = text.replace(
    "Status: **E4 IMPLEMENTED / release verification pending**\n\nExplore 3D Steps E1, E2, and E3 are production verified. `Night Intersection` is the default real-geometry scene with bounded Human movement while Hansaplatz remains the `360° Photo Reference`. E4 integrates the accepted Human spatial Vision set on the geometry scene.",
    "Status: **E4 PASS / production verified**\n\nExplore 3D Steps E1 through E4 are production verified. `Night Intersection` is the default real-geometry scene with bounded Human movement and the accepted Human spatial Vision set, while Hansaplatz remains the `360° Photo Reference`. The next queued implementation step is E5 Dog observer.",
    1,
)
text = text.replace(
    "## Step E4 — Human spatial Vision integration\nStatus: **IMPLEMENTED / release verification pending**",
    "## Step E4 — Human spatial Vision integration\nStatus: **PASS / production verified**",
    1,
)
anchor = "- permanent production smoke with an E4-specific stale-release fingerprint.\n\n## Step E5 — Dog observer"
closeout = """- permanent production smoke with an E4-specific stale-release fingerprint.\n\nProduction closeout:\n- final E4 validation run `34148557108` passed build, desktop/mobile geometry Vision behavior, same-state Vision switching, Compare image regression, and the full local production smoke; validation artifact `10028600514` was uploaded;\n- rendered validation confirmed Tunnel edge-dominance (`centerDelta=0.00001`, `edgeDelta=21.158`), Central center-dominance (`centerDelta=53.588`, `edgeDelta=0.00001`), stronger Night response in dark regions (`darkRelativeDelta=1.190` vs `brightRelativeDelta=0.199`), and local Cataract bright-source glare spread (`nearGain=38.976` vs `farGain=29.290`);\n- PR #47 was squash-merged as main commit `58fbd132c24f5d182b90e8c55a096d500419b580`;\n- matching main build `34148945521` passed;\n- matching production smoke `34148945534` passed against `https://asseenby.pages.dev` with `productionReleaseDetected=true`, `e2SpatialReleaseDetected=true`, `e3HumanMovementDetected=true`, `e4HumanVisionDetected=true`, desktop/mobile image=true, desktop/mobile spatial=true, and `ok=true`;\n- the production E4 fingerprint was detected on attempt 1 and production smoke artifact `10028717598` was uploaded.\n\n## Step E5 — Dog observer"""
if anchor not in text:
    raise SystemExit("E4 closeout anchor missing")
text = text.replace(anchor, closeout, 1)
schedule.write_text(text)

roadmap = Path("docs/roadmap.md")
text = roadmap.read_text()
text = text.replace(
    "- a production-verified E3 Human observer with bounded collision-aware ground movement on Night Intersection.",
    "- a production-verified E3 Human observer with bounded collision-aware ground movement on Night Intersection;\n- a production-verified E4 Human spatial Vision integration on Night Intersection with Normal, Tunnel Vision, Central Loss, Night / Low Light, and Cataract-like.",
    1,
)
text = text.replace(
    "## Immediate priority order\n1. integrate the accepted Human spatial Vision modes into Night Intersection in E4 while preserving the E3 observer state;\n2. add Dog observer, then refine Dog-like 3D detail behavior;\n3. add Cat observer movement/viewpoint without automatically restoring Cat-like Vision;\n4. select a concrete first Bird species and implement real flight/perch behavior;\n5. evaluate that Bird species' visual model separately from its movement/viewpoint;\n6. expand to additional dense scenes after the first architecture is stable.",
    "## Immediate priority order\n1. add Dog observer in E5, then refine Dog-like 3D detail behavior in E6;\n2. add Cat observer movement/viewpoint without automatically restoring Cat-like Vision;\n3. select a concrete first Bird species and implement real flight/perch behavior;\n4. evaluate that Bird species' visual model separately from its movement/viewpoint;\n5. expand to additional dense scenes after the first architecture is stable.",
    1,
)
roadmap.write_text(text)
print("E4 production closeout docs patched")
