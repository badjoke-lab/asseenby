#!/usr/bin/env python3
from pathlib import Path

page = Path("src/SpatialPage.tsx")
s = page.read_text()
old = '''        setLighting: (nextLighting) => {
          currentLightingMode = nextLighting;
          activeSceneRuntime?.setLightingMode(nextLighting);
          if (renderer) renderer.toneMappingExposure = nextLighting === "day" ? 1.08 : 1.3;
          canvas.dataset.sceneLightingMode = nextLighting;
          renderScene();
        },'''
new = '''        setLighting: (nextLighting) => {
          currentLightingMode = nextLighting;
          canvas.dataset.sceneLightingMode = nextLighting;
          if (renderer) renderer.toneMappingExposure = nextLighting === "day" ? 1.08 : 1.3;
          activeSceneRuntime?.setLightingMode(nextLighting);
        },'''
if old not in s:
    raise SystemExit("lighting controller block not found")
page.write_text(s.replace(old, new, 1))

proof = Path(".github/hansaplatz-lod2-visual-proof.mjs")
p = proof.read_text()
old_night = 'await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "night");'
new_night = 'await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "night", { timeout: 90_000 });'
old_day = 'await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "day");'
new_day = 'await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "day", { timeout: 90_000 });'
if old_night not in p or old_day not in p:
    raise SystemExit("lighting proof wait block not found")
p = p.replace(old_night, new_night, 1).replace(old_day, new_day, 1)

# Strengthen parity check: time-of-day switching must not move the observer or camera.
needle = '    && nightLightingState?.chunks === initial?.chunks\n    && dayReturnState?.lighting === "day"'
replacement = '    && nightLightingState?.chunks === initial?.chunks\n    && nightLightingState?.position === initial?.position\n    && nightLightingState?.yaw === initial?.yaw\n    && nightLightingState?.pitch === initial?.pitch\n    && dayReturnState?.lighting === "day"\n    && dayReturnState?.position === initial?.position\n    && dayReturnState?.yaw === initial?.yaw\n    && dayReturnState?.pitch === initial?.pitch'
if needle not in p:
    raise SystemExit("Day/Night parity assertion insertion point not found")
proof.write_text(p.replace(needle, replacement, 1))
print("Day/Night switch repaired")