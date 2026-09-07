from pathlib import Path
import re

spatial = Path('src/SpatialPage.tsx')
text = spatial.read_text()
text = text.replace('renderer.shadowMap.enabled = true;', 'renderer.shadowMap.enabled = false;')
spatial.write_text(text)

scene = Path('src/spatial/nightIntersectionScene.ts')
text = scene.read_text()
text = text.replace('moon.castShadow = true;', 'moon.castShadow = false;')

if 'const addInstancedBoxes =' not in text:
    anchor = '''  const addCylinder = (\n'''
    helper = '''  const addInstancedBoxes = (\n    name: string,\n    size: [number, number, number],\n    positions: Array<[number, number, number]>,\n    meshMaterial: THREE.Material,\n  ) => {\n    const geometry = new THREE.BoxGeometry(...size);\n    const mesh = new THREE.InstancedMesh(geometry, meshMaterial, positions.length);\n    mesh.name = name;\n    const matrix = new THREE.Matrix4();\n    positions.forEach((position, index) => {\n      matrix.makeTranslation(position[0], position[1], position[2]);\n      mesh.setMatrixAt(index, matrix);\n    });\n    mesh.instanceMatrix.needsUpdate = true;\n    root.add(mesh);\n    return mesh;\n  };\n\n'''
    if anchor not in text:
        raise SystemExit('addCylinder anchor missing')
    text = text.replace(anchor, helper + anchor, 1)

road_pattern = re.compile(r'''  for \(let i = 0; i < 9; i \+= 1\) \{.*?\n  for \(const z of \[-24\.8, -31\.2\]\) \{\n    for \(let x = -66; x <= 66; x \+= 13\) addBox\(`lane-cross-\$\{x\}-\$\{z\}`, \[5\.4, 0\.026, 0\.16\], \[x, GROUND_Y \+ 0\.075, z\], roadPaint, root, false\);\n  \}\n''', re.S)
if 'crosswalk-ns-instances' not in text:
    road_replacement = '''  const crosswalkNs: Array<[number, number, number]> = [];\n  const crosswalkEw: Array<[number, number, number]> = [];\n  for (let i = 0; i < 9; i += 1) {\n    const x = -7.6 + i * 1.9;\n    crosswalkNs.push([x, GROUND_Y + 0.07, -17.9], [x, GROUND_Y + 0.07, -38.1]);\n    const z = -35.6 + i * 1.9;\n    crosswalkEw.push([-10.9, GROUND_Y + 0.075, z], [10.9, GROUND_Y + 0.075, z]);\n  }\n  addInstancedBoxes("crosswalk-ns-instances", [1.0, 0.026, 5.6], crosswalkNs, roadPaint);\n  addInstancedBoxes("crosswalk-ew-instances", [5.6, 0.026, 1.0], crosswalkEw, roadPaint);\n\n  const laneNs: Array<[number, number, number]> = [];\n  for (const x of [-3.2, 3.2]) {\n    for (let z = 34; z >= -96; z -= 13) laneNs.push([x, GROUND_Y + 0.07, z]);\n  }\n  addInstancedBoxes("lane-ns-instances", [0.16, 0.026, 5.4], laneNs, roadPaint);\n\n  const laneEw: Array<[number, number, number]> = [];\n  for (const z of [-24.8, -31.2]) {\n    for (let x = -66; x <= 66; x += 13) laneEw.push([x, GROUND_Y + 0.075, z]);\n  }\n  addInstancedBoxes("lane-ew-instances", [5.4, 0.026, 0.16], laneEw, roadPaint);\n'''
    text, count = road_pattern.subn(road_replacement, text, count=1)
    if count != 1:
        raise SystemExit('road marking loops not replaced')

scene.write_text(text)
