from pathlib import Path

path = Path("src/SpatialPage.tsx")
text = path.read_text()
needle = "      applyObserver(observerId);\n      activeObserverRuntime?.setGuidedViewpoint(viewpoint);\n      visionRuntime.setVision(vision);"
replacement = "      applyObserver(observerId);\n      visionRuntime.setVision(vision);"
if needle in text:
    path.write_text(text.replace(needle, replacement, 1))
elif replacement not in text:
    raise SystemExit("E2 viewpoint initialization marker not found")
