from pathlib import Path

path = Path('src/SpatialPage.tsx')
text = path.read_text()
old = '''      renderer.outputColorSpace = THREE.SRGBColorSpace;\n      renderer.toneMapping = THREE.NoToneMapping;\n      renderer.toneMappingExposure = 1.0;\n      renderer.shadowMap.enabled = false;'''
new = '''      renderer.outputColorSpace = THREE.SRGBColorSpace;\n      renderer.toneMapping = THREE.ACESFilmicToneMapping;\n      renderer.toneMappingExposure = 1.08;\n      renderer.shadowMap.enabled = true;\n      renderer.shadowMap.type = THREE.PCFSoftShadowMap;'''
if old not in text:
    raise SystemExit('renderer settings block not found')
path.write_text(text.replace(old, new, 1))
