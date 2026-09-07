from pathlib import Path

spatial = Path('src/SpatialPage.tsx')
text = spatial.read_text()
old_renderer = '''      renderer.outputColorSpace = THREE.SRGBColorSpace;\n      renderer.toneMapping = THREE.NoToneMapping;\n      renderer.toneMappingExposure = 1.0;\n      renderer.shadowMap.enabled = false;'''
polished_renderer = '''      renderer.outputColorSpace = THREE.SRGBColorSpace;\n      renderer.toneMapping = THREE.ACESFilmicToneMapping;\n      renderer.toneMappingExposure = 1.34;\n      renderer.shadowMap.enabled = true;\n      renderer.shadowMap.type = THREE.PCFSoftShadowMap;'''
intermediate_renderer = '''      renderer.outputColorSpace = THREE.SRGBColorSpace;\n      renderer.toneMapping = THREE.ACESFilmicToneMapping;\n      renderer.toneMappingExposure = 1.08;\n      renderer.shadowMap.enabled = true;\n      renderer.shadowMap.type = THREE.PCFSoftShadowMap;'''
if old_renderer in text:
    text = text.replace(old_renderer, polished_renderer, 1)
elif intermediate_renderer in text:
    text = text.replace(intermediate_renderer, polished_renderer, 1)
elif polished_renderer not in text:
    raise SystemExit('renderer settings block not found')
spatial.write_text(text)

scene = Path('src/spatial/nightIntersectionScene.ts')
text = scene.read_text()
replacements = {
    'scene.fog = new THREE.FogExp2(0x111722, 0.0042);': 'scene.fog = new THREE.FogExp2(0x111722, 0.0030);',
    'const hemisphere = new THREE.HemisphereLight(0x91a9c7, 0x2a2018, 1.3);': 'const hemisphere = new THREE.HemisphereLight(0xa8bad0, 0x3d3024, 2.15);',
    'const moon = new THREE.DirectionalLight(0xa7bdd7, 1.28);': 'const moon = new THREE.DirectionalLight(0xb4c8de, 1.85);',
    'const shopWest = new THREE.PointLight(0xff9b55, 10.5, 20, 2.0);': 'const shopWest = new THREE.PointLight(0xff9b55, 18.0, 23, 2.0);',
    'const shopEast = new THREE.PointLight(0x72c5de, 9.4, 19, 2.0);': 'const shopEast = new THREE.PointLight(0x72c5de, 16.5, 22, 2.0);',
    'facade: 0x6a5b50': 'facade: 0x8a7868',
    'facade: 0x59636b': 'facade: 0x72818a',
    'facade: 0x715d4f': 'facade: 0x8d7563',
    'facade: 0x566469': 'facade: 0x71848a',
    'facade: 0x50565e': 'facade: 0x68737e',
    'facade: 0x625850': 'facade: 0x796b60',
}
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)

ambient_marker = '''  hemisphere.name = "night-sky-fill";\n  root.add(hemisphere);'''
ambient_block = '''  hemisphere.name = "night-sky-fill";\n  root.add(hemisphere);\n\n  const ambient = new THREE.AmbientLight(0x8f9baa, 0.72);\n  ambient.name = "street-ambient-fill";\n  root.add(ambient);'''
if ambient_marker in text and 'street-ambient-fill' not in text:
    text = text.replace(ambient_marker, ambient_block, 1)

moon_marker = '''  moon.shadow.bias = -0.0007;\n  root.add(moon);'''
moon_block = '''  moon.shadow.bias = -0.0007;\n  root.add(moon);\n\n  const intersectionFill = new THREE.PointLight(0xffddb0, 9.5, 36, 1.7);\n  intersectionFill.name = "intersection-fill";\n  intersectionFill.position.set(-2, 7.5, -25);\n  root.add(intersectionFill);'''
if moon_marker in text and 'intersection-fill' not in text:
    text = text.replace(moon_marker, moon_block, 1)

sign_marker = '''  addBuilding("far-north-right", { x: 33, z: -101, width: 34, depth: 24, height: 19, floors: 5, facade: 0x796b60, trim: 0x302e2b, front: "south", sign: "DINER", signTone: "warm" });'''
sign_block = sign_marker + '''\n\n  const addStreetSign = (name: string, label: string, tone: "warm" | "cool", x: number, y: number, z: number, width: number, height: number) => {\n    const texture = makeSignTexture(label, tone);\n    const signMaterial = trackMaterial(new THREE.MeshStandardMaterial({\n      map: texture,\n      emissiveMap: texture,\n      emissive: 0xffffff,\n      emissiveIntensity: 1.45,\n      roughness: 0.28,\n      side: THREE.DoubleSide,\n    }));\n    const sign = new THREE.Mesh(new THREE.PlaneGeometry(width, height), signMaterial);\n    sign.name = name;\n    sign.position.set(x, GROUND_Y + y, z);\n    sign.castShadow = false;\n    root.add(sign);\n    addBox(`${name}-frame`, [width + 0.18, height + 0.18, 0.08], [x, GROUND_Y + y, z + 0.04], darkMetal, root);\n  };\n\n  addStreetSign("corner-market-sign", "MARKET", "warm", -12.8, 4.2, -41.75, 5.6, 1.25);\n  addStreetSign("corner-books-sign", "BOOKS", "cool", 12.8, 4.2, -41.75, 5.2, 1.25);\n  addStreetSign("bus-stop-sign", "BUS", "cool", -10.8, 2.8, -22.2, 1.1, 1.75);'''
if sign_marker in text and 'corner-market-sign' not in text:
    text = text.replace(sign_marker, sign_block, 1)

bench_marker = '''  addBench("bench-west", -14.2, -8.3, Math.PI / 2);\n  addBench("bench-east", 14.4, -50.5, -Math.PI / 2);'''
bench_block = bench_marker + '''\n\n  const shelter = new THREE.Group();\n  shelter.name = "bus-shelter-east";\n  shelter.position.set(14.4, GROUND_Y, -24.5);\n  root.add(shelter);\n  addBox("bus-shelter-roof", [4.6, 0.16, 1.8], [0, 2.65, 0], darkMetal, shelter);\n  addBox("bus-shelter-back", [4.5, 2.25, 0.08], [0, 1.35, 0.78], glass, shelter, false);\n  addBox("bus-shelter-side", [0.08, 2.25, 1.55], [-2.15, 1.35, 0], glass, shelter, false);\n  for (const px of [-2.15, 2.15]) addCylinder(`bus-shelter-post-${px}`, 0.07, 2.65, [px, 1.33, 0.72], darkMetal, shelter, 10);\n  addBox("bus-shelter-seat", [2.7, 0.16, 0.48], [0.4, 0.58, 0.42], paleMetal, shelter);'''
if bench_marker in text and 'bus-shelter-east' not in text:
    text = text.replace(bench_marker, bench_block, 1)

scene.write_text(text)
