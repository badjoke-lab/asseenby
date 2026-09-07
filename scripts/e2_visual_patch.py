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
text = text.replace('      crown.castShadow = true;', '      crown.castShadow = false;')
text = text.replace('        wheel.castShadow = true;', '        wheel.castShadow = false;')

shell_pattern = re.compile(r'''  const addCarShell = \(.*?\n  const addCar =''', re.S)
if 'new THREE.ExtrudeGeometry' in text:
    shell_replacement = r'''  const addCarShell = (
    name: string,
    length: number,
    width: number,
    van: boolean,
    paint: THREE.Material,
    parent: THREE.Object3D,
  ) => {
    const profile: Array<[number, number]> = van
      ? [
          [-length / 2, 0.48],
          [-length / 2, 0.9],
          [-length * 0.4, 1.12],
          [-length * 0.29, 1.9],
          [-length * 0.18, 2.04],
          [length * 0.38, 2.04],
          [length * 0.46, 1.76],
          [length / 2, 1.08],
          [length / 2, 0.5],
        ]
      : [
          [-length / 2, 0.48],
          [-length / 2, 0.78],
          [-length * 0.42, 0.96],
          [-length * 0.26, 1.02],
          [-length * 0.11, 1.55],
          [length * 0.02, 1.7],
          [length * 0.18, 1.65],
          [length * 0.31, 1.1],
          [length * 0.43, 0.98],
          [length / 2, 0.78],
          [length / 2, 0.48],
        ];

    const halfWidth = width / 2;
    const positions: number[] = [];
    for (const side of [-halfWidth, halfWidth]) {
      for (const [pz, py] of profile) positions.push(side, py, pz);
    }
    const count = profile.length;
    const indices: number[] = [];

    for (let i = 1; i < count - 1; i += 1) {
      indices.push(0, i + 1, i);
      indices.push(count, count + i, count + i + 1);
    }
    for (let i = 0; i < count; i += 1) {
      const next = (i + 1) % count;
      const leftA = i;
      const leftB = next;
      const rightA = count + i;
      const rightB = count + next;
      indices.push(leftA, rightA, rightB, leftA, rightB, leftB);
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    const shell = new THREE.Mesh(geometry, paint);
    shell.name = `${name}-shell`;
    shell.castShadow = true;
    shell.receiveShadow = true;
    parent.add(shell);
    return shell;
  };

  const addCar ='''
    text, count = shell_pattern.subn(shell_replacement, text, count=1)
    if count != 1:
        raise SystemExit('current addCarShell block not replaced')

scene.write_text(text)
