from pathlib import Path
import re

spatial = Path('src/SpatialPage.tsx')
text = spatial.read_text()
text = text.replace(
    'renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));',
    'renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));',
)
text = text.replace('renderer.toneMappingExposure = 1.34;', 'renderer.toneMappingExposure = 1.28;')
spatial.write_text(text)

scene = Path('src/spatial/nightIntersectionScene.ts')
text = scene.read_text()

text = text.replace(
    'color: 0x252930,\n    map: asphaltTexture,\n    roughness: 0.52,',
    'color: 0x353b43,\n    map: asphaltTexture,\n    roughness: 0.58,',
)
text = text.replace('castShadow = true,', 'castShadow = false,', 1)

facade_pattern = re.compile(r'''  const facadeTexture = \(base: string, mortar: string, repeatX: number, repeatY: number\) => makeCanvasTexture\(256, \(ctx, size\) => \{.*?\n  \}, repeatX, repeatY\);''', re.S)
facade_replacement = '''  const facadeTexture = (base: string, mortar: string, columns: number, rows: number, seed: number) => makeCanvasTexture(512, (ctx, size) => {
    ctx.fillStyle = base;
    ctx.fillRect(0, 0, size, size);

    ctx.strokeStyle = mortar;
    ctx.lineWidth = 1;
    const brickH = 16;
    for (let y = 0; y < size; y += brickH) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(size, y);
      ctx.stroke();
      const offset = (Math.floor(y / brickH) % 2) * 18;
      for (let x = -offset; x < size; x += 36) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x, Math.min(size, y + brickH));
        ctx.stroke();
      }
    }

    const marginX = 18;
    const marginTop = 20;
    const marginBottom = 52;
    const cellW = (size - marginX * 2) / Math.max(1, columns);
    const cellH = (size - marginTop - marginBottom) / Math.max(1, rows);
    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < columns; col += 1) {
        const x = marginX + col * cellW + cellW * 0.18;
        const y = marginTop + row * cellH + cellH * 0.16;
        const w = cellW * 0.64;
        const h = cellH * 0.62;
        const lit = Math.floor(seededNoise(seed + row * 19 + col * 11) * 7);
        ctx.fillStyle = 'rgba(13,17,21,0.72)';
        ctx.fillRect(x - 3, y - 3, w + 6, h + 7);
        ctx.fillStyle = lit === 0 || lit === 5 ? '#e5bd78' : lit === 2 ? '#88bed0' : '#18232b';
        ctx.fillRect(x, y, w, h);
        ctx.fillStyle = 'rgba(245,245,235,0.18)';
        ctx.fillRect(x + w * 0.48, y, 2, h);
        ctx.fillStyle = 'rgba(20,22,24,0.55)';
        ctx.fillRect(x - 4, y + h + 3, w + 8, 3);
      }
    }

    const gradient = ctx.createLinearGradient(0, 0, size, 0);
    gradient.addColorStop(0, 'rgba(255,255,255,0.09)');
    gradient.addColorStop(0.5, 'rgba(0,0,0,0.07)');
    gradient.addColorStop(1, 'rgba(255,255,255,0.025)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);
  });'''
text, count = facade_pattern.subn(facade_replacement, text, count=1)
if count != 1:
    raise SystemExit('facadeTexture block not replaced')

windows_pattern = re.compile(r'''\n  const addFacadeWindows = \(group: THREE\.Group, options: BuildingOptions, face: Face\) => \{.*?\n  \};\n\n  const addStorefront''', re.S)
text, count = windows_pattern.subn('\n\n  const addStorefront', text, count=1)
if count != 1:
    raise SystemExit('addFacadeWindows block not removed')

building_pattern = re.compile(r'''  const addBuilding = \(name: string, options: BuildingOptions\) => \{.*?\n    return group;\n  \};''', re.S)
building_replacement = '''  const addBuilding = (name: string, options: BuildingOptions) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(options.x, GROUND_Y + options.height / 2, options.z);
    root.add(group);

    const facadeColumns = Math.max(4, Math.round(options.width / 5));
    const facadeRows = Math.max(3, options.floors - 1);
    const tex = facadeTexture(
      typeof options.facade === "number" && (options.facade as number) < 0x505050 ? "#42484f" : "#65594f",
      "rgba(220,216,207,0.12)",
      facadeColumns,
      facadeRows,
      Math.abs(Math.round(options.x * 17 + options.z * 11)),
    );
    const facadeMaterial = trackMaterial(new THREE.MeshStandardMaterial({
      color: options.facade,
      map: tex,
      roughness: 0.76,
      metalness: 0.03,
      emissive: 0x17130f,
      emissiveIntensity: 0.08,
    }));
    const trimMaterial = trackMaterial(new THREE.MeshStandardMaterial({ color: options.trim, roughness: 0.62, metalness: 0.1 }));

    const podiumHeight = Math.min(5.6, options.height * 0.29);
    const upperHeight = options.height - podiumHeight;
    const upperWidth = Math.max(12, options.width - 2.6);
    const upperDepth = Math.max(12, options.depth - 2.2);
    const upperShiftX = options.x < 0 ? 0.65 : -0.65;
    const upperShiftZ = options.front === "south" ? -0.45 : 0.45;
    const podiumY = -options.height / 2 + podiumHeight / 2;
    const upperY = -options.height / 2 + podiumHeight + upperHeight / 2;

    addBox(`${name}-podium`, [options.width, podiumHeight, options.depth], [0, podiumY, 0], facadeMaterial, group, true);
    addBox(`${name}-upper`, [upperWidth, upperHeight, upperDepth], [upperShiftX, upperY, upperShiftZ], facadeMaterial, group, true);
    addBox(`${name}-podium-cornice`, [options.width + 0.45, 0.32, options.depth + 0.45], [0, -options.height / 2 + podiumHeight + 0.16, 0], trimMaterial, group);
    addBox(`${name}-roof-cap`, [upperWidth + 0.75, 0.48, upperDepth + 0.75], [upperShiftX, options.height / 2 + 0.24, upperShiftZ], trimMaterial, group);
    addBox(`${name}-ground-belt`, [options.width + 0.28, 0.7, options.depth + 0.28], [0, -options.height / 2 + 0.35, 0], trimMaterial, group);

    const pierY = upperY;
    const pierX = upperWidth / 2 - 0.22;
    const pierZ = upperDepth / 2 - 0.22;
    for (const sx of [-1, 1]) {
      for (const sz of [-1, 1]) {
        addBox(`${name}-corner-pier-${sx}-${sz}`, [0.42, upperHeight - 0.4, 0.42], [upperShiftX + sx * pierX, pierY, upperShiftZ + sz * pierZ], trimMaterial, group);
      }
    }

    addStorefront(group, options);
    if (options.balconies) {
      for (let floor = 1; floor < Math.min(options.floors - 1, 5); floor += 2) {
        const y = -options.height / 2 + podiumHeight + Math.min(upperHeight - 1.6, 1.6 + floor * 2.55);
        if (options.front === "south" || options.front === "north") {
          const z = options.front === "south" ? options.depth / 2 + 0.64 : -options.depth / 2 - 0.64;
          addBox(`${name}-balcony-${floor}`, [7.7, 0.16, 1.18], [upperShiftX, y, z], darkMetal, group);
          addBox(`${name}-balcony-rail-${floor}`, [7.7, 0.72, 0.08], [upperShiftX, y + 0.34, z + (options.front === "south" ? 0.53 : -0.53)], paleMetal, group);
        }
      }
    }

    addBox(`${name}-roof-service`, [3.8, 1.65, 2.8], [upperShiftX + options.width * 0.12, options.height / 2 + 1.05, upperShiftZ - options.depth * 0.08], trimMaterial, group);
    addBox(`${name}-roof-service-cap`, [4.2, 0.18, 3.2], [upperShiftX + options.width * 0.12, options.height / 2 + 1.92, upperShiftZ - options.depth * 0.08], paleMetal, group);
    return group;
  };'''
text, count = building_pattern.subn(building_replacement, text, count=1)
if count != 1:
    raise SystemExit('addBuilding block not replaced')

car_anchor = '''  const paints = [0x7e3432, 0x31566f, 0xc0ad83, 0x45484d].map((color) => trackMaterial(new THREE.MeshPhysicalMaterial({ color, roughness: 0.4, metalness: 0.28, clearcoat: 0.5, clearcoatRoughness: 0.28 })));
  const addCar ='''
car_helper = '''  const paints = [0x7e3432, 0x31566f, 0xc0ad83, 0x45484d].map((color) => trackMaterial(new THREE.MeshPhysicalMaterial({ color, roughness: 0.4, metalness: 0.28, clearcoat: 0.5, clearcoatRoughness: 0.28 })));

  const addTaperedBox = (
    name: string,
    size: [number, number, number],
    position: [number, number, number],
    meshMaterial: THREE.Material,
    parent: THREE.Object3D,
    topWidth = 0.82,
    topLength = 0.72,
  ) => {
    const geometry = new THREE.BoxGeometry(...size);
    const attribute = geometry.getAttribute("position") as THREE.BufferAttribute;
    for (let index = 0; index < attribute.count; index += 1) {
      const x = attribute.getX(index);
      const y = attribute.getY(index);
      const z = attribute.getZ(index);
      if (y > 0) attribute.setXYZ(index, x * topWidth, y, z * topLength);
    }
    geometry.computeVertexNormals();
    const mesh = new THREE.Mesh(geometry, meshMaterial);
    mesh.name = name;
    mesh.position.set(...position);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
  };

  const addCar ='''
if car_anchor not in text:
    raise SystemExit('car anchor not found')
text = text.replace(car_anchor, car_helper, 1)

text = text.replace(
    'addBox(`${name}-lower`, [1.92, 0.58, length], [0, 0.64, 0], paint, group);',
    'addBox(`${name}-lower`, [1.92, 0.58, length], [0, 0.64, 0], paint, group, true);',
)
text = text.replace(
    'addBox(`${name}-hood`, [1.78, 0.34, van ? 1.25 : 1.2], [0, 1.0, -length * 0.31], paint, group);',
    'addTaperedBox(`${name}-hood`, [1.78, 0.34, van ? 1.25 : 1.2], [0, 1.0, -length * 0.31], paint, group, 0.96, 0.86);',
)
text = text.replace(
    'addBox(`${name}-trunk`, [1.76, 0.32, van ? 0.62 : 1.0], [0, 0.96, length * 0.35], paint, group);',
    'addTaperedBox(`${name}-trunk`, [1.76, 0.32, van ? 0.62 : 1.0], [0, 0.96, length * 0.35], paint, group, 0.97, 0.9);',
)
text = text.replace(
    'addBox(`${name}-cabin`, [1.62, van ? 1.45 : 1.02, van ? 2.9 : 2.15], [0, van ? 1.5 : 1.36, van ? 0.15 : 0.02], paint, group);',
    'addTaperedBox(`${name}-cabin`, [1.62, van ? 1.45 : 1.02, van ? 2.9 : 2.15], [0, van ? 1.5 : 1.36, van ? 0.15 : 0.02], paint, group, van ? 0.92 : 0.78, van ? 0.9 : 0.68);',
)

scene.write_text(text)
