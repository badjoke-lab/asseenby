from pathlib import Path
import re

spatial = Path('src/SpatialPage.tsx')
text = spatial.read_text()
text = text.replace(
    'renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));',
    'renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.25));',
)
text = text.replace('renderer.toneMappingExposure = 1.28;', 'renderer.toneMappingExposure = 1.3;')
spatial.write_text(text)

scene = Path('src/spatial/nightIntersectionScene.ts')
text = scene.read_text()

text = text.replace('moon.shadow.mapSize.set(1024, 1024);', 'moon.shadow.mapSize.set(512, 512);')
text = text.replace('    mesh.castShadow = true;\n    mesh.receiveShadow = true;\n    parent.add(mesh);\n    return mesh;\n  };\n\n  scene.background', '    mesh.castShadow = false;\n    mesh.receiveShadow = true;\n    parent.add(mesh);\n    return mesh;\n  };\n\n  scene.background', 1)
text = text.replace('      crown.castShadow = true;', '      crown.castShadow = false;')
text = text.replace('        wheel.castShadow = true;', '        wheel.castShadow = false;')

text = text.replace('const upperWidth = Math.max(12, options.width - 2.6);', 'const upperWidth = Math.max(12, options.width - 4.6);')
text = text.replace('const upperDepth = Math.max(12, options.depth - 2.2);', 'const upperDepth = Math.max(12, options.depth - 4.0);')
text = text.replace('const upperShiftX = options.x < 0 ? 0.65 : -0.65;', 'const upperShiftX = options.x < 0 ? 1.35 : -1.35;')
text = text.replace('const upperShiftZ = options.front === "south" ? -0.45 : 0.45;', 'const upperShiftZ = options.front === "south" ? -0.9 : 0.9;')

upper_anchor = '''    addBox(`${name}-upper`, [upperWidth, upperHeight, upperDepth], [upperShiftX, upperY, upperShiftZ], facadeMaterial, group, true);\n'''
if '`${name}-corner-bay`' not in text:
    upper_extra = upper_anchor + '''    const bayWidth = Math.max(5.2, upperWidth * 0.34);\n    const bayHeight = Math.max(6.2, upperHeight * 0.72);\n    const bayX = upperShiftX + (options.x < 0 ? upperWidth * 0.31 : -upperWidth * 0.31);\n    const bayZ = upperShiftZ + (options.front === "south" ? upperDepth * 0.12 : -upperDepth * 0.12);\n    const bayY = -options.height / 2 + podiumHeight + bayHeight / 2 + 0.18;\n    addBox(`${name}-corner-bay`, [bayWidth, bayHeight, upperDepth + 0.9], [bayX, bayY, bayZ], facadeMaterial, group, true);\n'''
    if upper_anchor not in text:
        raise SystemExit('upper building anchor not found')
    text = text.replace(upper_anchor, upper_extra, 1)

if 'const addCarShell =' not in text:
    car_pattern = re.compile(r'''  const addTaperedBox = \(.*?\n  addCar\("parked-east", 13\.2, -61, Math\.PI, paints\[3\]\);\n''', re.S)
    car_replacement = r'''  const addCarShell = (
    name: string,
    length: number,
    width: number,
    van: boolean,
    paint: THREE.Material,
    parent: THREE.Object3D,
  ) => {
    const shape = new THREE.Shape();
    const points = van
      ? [
          [-length / 2, 0.46],
          [-length * 0.44, 1.05],
          [-length * 0.31, 1.82],
          [-length * 0.18, 2.02],
          [length * 0.34, 2.02],
          [length * 0.45, 1.72],
          [length / 2, 0.5],
        ]
      : [
          [-length / 2, 0.46],
          [-length * 0.44, 0.84],
          [-length * 0.28, 1.02],
          [-length * 0.13, 1.58],
          [length * 0.04, 1.76],
          [length * 0.22, 1.68],
          [length * 0.37, 1.08],
          [length * 0.46, 0.92],
          [length / 2, 0.5],
        ];
    shape.moveTo(points[0][0], points[0][1]);
    for (const [px, py] of points.slice(1)) shape.lineTo(px, py);
    shape.lineTo(points[0][0], points[0][1]);
    const geometry = new THREE.ExtrudeGeometry(shape, {
      depth: width,
      bevelEnabled: true,
      bevelSegments: 1,
      steps: 1,
      bevelSize: 0.055,
      bevelThickness: 0.055,
    });
    geometry.translate(0, 0, -width / 2);
    geometry.rotateY(Math.PI / 2);
    geometry.computeVertexNormals();
    const shell = new THREE.Mesh(geometry, paint);
    shell.name = `${name}-shell`;
    shell.castShadow = true;
    shell.receiveShadow = true;
    parent.add(shell);
    return shell;
  };

  const addCar = (name: string, x: number, z: number, rotationY: number, paint: THREE.Material, van = false) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    group.rotation.y = rotationY;
    root.add(group);
    const length = van ? 5.5 : 4.5;
    const width = van ? 1.95 : 1.9;
    addCarShell(name, length, width, van, paint, group);

    const windshieldZ = -length * (van ? 0.29 : 0.18);
    const rearGlassZ = length * (van ? 0.34 : 0.23);
    addBox(`${name}-windshield`, [width * 0.79, van ? 0.78 : 0.62, 0.055], [0, van ? 1.63 : 1.48, windshieldZ], glass, group, false);
    addBox(`${name}-rear-glass`, [width * 0.76, van ? 0.7 : 0.55, 0.055], [0, van ? 1.61 : 1.43, rearGlassZ], glass, group, false);
    for (const side of [-1, 1]) {
      addBox(`${name}-side-glass-${side}`, [0.045, van ? 0.78 : 0.56, van ? 2.2 : 1.35], [side * (width / 2 + 0.02), van ? 1.64 : 1.5, van ? 0.12 : 0.03], glass, group, false);
      addBox(`${name}-mirror-${side}`, [0.18, 0.11, 0.28], [side * (width / 2 + 0.12), 1.34, -length * 0.18], darkMetal, group, false);
      for (const axle of [-1, 1]) {
        const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.39, 0.39, 0.22, 14), tire);
        wheel.name = `${name}-wheel-${side}-${axle}`;
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(side * (width / 2 + 0.03), 0.42, axle * length * 0.31);
        wheel.receiveShadow = true;
        group.add(wheel);
        const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.232, 12), rim);
        hub.name = `${name}-hub-${side}-${axle}`;
        hub.rotation.z = Math.PI / 2;
        hub.position.copy(wheel.position);
        group.add(hub);
      }
    }
    for (const side of [-0.55, 0.55]) {
      addBox(`${name}-headlight-${side}`, [0.32, 0.16, 0.07], [side, 0.83, -length / 2 - 0.05], lampMaterial, group, false);
      addBox(`${name}-taillight-${side}`, [0.28, 0.15, 0.07], [side, 0.8, length / 2 + 0.05], redLight, group, false);
    }
  };
  addCar("target-near-car", -4.6, -11.5, 0.02, paints[0]);
  addCar("mid-blue-car", 4.5, -48, Math.PI, paints[1]);
  addCar("cross-street-van", 29, -32.5, Math.PI / 2, paints[2], true);
  addCar("far-taxi", -4.3, -79, 0, paints[2]);
  addCar("parked-east", 13.2, -61, Math.PI, paints[3]);
'''
    text, count = car_pattern.subn(car_replacement, text, count=1)
    if count != 1:
        raise SystemExit('car block not replaced')

scene.write_text(text)
