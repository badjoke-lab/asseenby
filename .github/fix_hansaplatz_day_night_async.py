#!/usr/bin/env python3
from pathlib import Path

page = Path("src/SpatialPage.tsx")
s = page.read_text()
old = '''        setLighting: (nextLighting) => {
          currentLightingMode = nextLighting;
          canvas.dataset.sceneLightingMode = nextLighting;
          if (renderer) renderer.toneMappingExposure = nextLighting === "day" ? 1.08 : 1.3;
          activeSceneRuntime?.setLightingMode(nextLighting);
        },'''
new = '''        setLighting: (nextLighting) => {
          currentLightingMode = nextLighting;
          canvas.dataset.sceneLightingMode = nextLighting;
          canvas.dataset.sceneLightingRenderState = "pending";
          if (renderer) renderer.toneMappingExposure = nextLighting === "day" ? 1.08 : 1.3;
          const runtimeAtRequest = activeSceneRuntime;
          window.setTimeout(() => {
            if (currentLightingMode !== nextLighting || activeSceneRuntime !== runtimeAtRequest) return;
            runtimeAtRequest?.setLightingMode(nextLighting);
            canvas.dataset.sceneLightingRenderState = "complete";
          }, 100);
        },'''
if old not in s:
    raise SystemExit("current lighting controller block not found")
page.write_text(s.replace(old, new, 1))

proof = Path(".github/hansaplatz-lod2-visual-proof.mjs")
p = proof.read_text()
old_night = '''await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "night", { timeout: 90_000 });
await desktop.waitForTimeout(350);'''
new_night = '''await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "night");
await desktop.waitForFunction(
  () => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingRenderState === "complete",
  null,
  { timeout: 120_000 },
);
await desktop.waitForTimeout(250);'''
old_day = '''await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "day", { timeout: 90_000 });
await desktop.waitForTimeout(250);'''
new_day = '''await desktop.waitForFunction(() => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingMode === "day");
await desktop.waitForFunction(
  () => document.querySelector("canvas.spatial-canvas")?.dataset.sceneLightingRenderState === "complete",
  null,
  { timeout: 120_000 },
);
await desktop.waitForTimeout(250);'''
if old_night not in p or old_day not in p:
    raise SystemExit("current Day/Night proof waits not found")
p = p.replace(old_night, new_night, 1).replace(old_day, new_day, 1)
proof.write_text(p)
print("async Day/Night render repair applied")