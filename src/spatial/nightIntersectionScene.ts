import * as THREE from "three";

const GROUND_Y = -1.6;

type Face = "north" | "south" | "east" | "west";

type BuildingOptions = {
  x: number;
  z: number;
  width: number;
  depth: number;
  height: number;
  floors: number;
  facade: THREE.ColorRepresentation;
  trim: THREE.ColorRepresentation;
  front: Face;
  side?: Face;
  sign: string;
  signTone: "warm" | "cool";
  balconies?: boolean;
};

export type NightIntersectionSceneMount = {
  root: THREE.Group;
  objectCount: number;
  lightCount: number;
  dispose: () => void;
};

type GroundCollisionRect = {
  x: number;
  z: number;
  halfWidth: number;
  halfDepth: number;
};

const NIGHT_INTERSECTION_COLLISIONS: GroundCollisionRect[] = [
  { x: -4.6, z: -11.5, halfWidth: 1.35, halfDepth: 2.7 },
  { x: 4.5, z: -48, halfWidth: 1.35, halfDepth: 2.7 },
  { x: 29, z: -32.5, halfWidth: 3.1, halfDepth: 1.35 },
  { x: -4.3, z: -79, halfWidth: 1.35, halfDepth: 2.7 },
  { x: 13.2, z: -61, halfWidth: 1.35, halfDepth: 2.7 },
  { x: 14.4, z: -24.5, halfWidth: 2.65, halfDepth: 1.3 },
  { x: -14.2, z: -8.3, halfWidth: 0.62, halfDepth: 1.45 },
  { x: 14.4, z: -50.5, halfWidth: 0.62, halfDepth: 1.45 },
  { x: -14.5, z: -44.5, halfWidth: 0.9, halfDepth: 0.65 },
  { x: 14.2, z: -11, halfWidth: 0.72, halfDepth: 0.72 },
  { x: -15.2, z: 17, halfWidth: 0.9, halfDepth: 0.9 },
  { x: 15.4, z: 21, halfWidth: 0.9, halfDepth: 0.9 },
  { x: -15.5, z: -69, halfWidth: 0.95, halfDepth: 0.95 },
  { x: 15.7, z: -75, halfWidth: 0.95, halfDepth: 0.95 },
  { x: -15.3, z: -49, halfWidth: 0.85, halfDepth: 0.85 },
  { x: -8.4, z: -18.2, halfWidth: 0.48, halfDepth: 0.48 },
  { x: 8.4, z: -18.2, halfWidth: 0.48, halfDepth: 0.48 },
  { x: -8.4, z: -37.8, halfWidth: 0.48, halfDepth: 0.48 },
  { x: 9.2, z: -36.2, halfWidth: 0.48, halfDepth: 0.48 },
];

const insideRect = (x: number, z: number, radius: number, minX: number, maxX: number, minZ: number, maxZ: number) => (
  x >= minX + radius && x <= maxX - radius && z >= minZ + radius && z <= maxZ - radius
);

export const NIGHT_INTERSECTION_NAVIGATION = {
  kind: 'ground' as const,
  eyeY: 0,
  radius: 0.36,
  speed: 3.0,
  fastSpeed: 5.2,
  canOccupy(x: number, z: number, radius = 0.36) {
    const inNorthSouth = insideRect(x, z, radius, -16.3, 16.3, -95, 35);
    const inEastWest = insideRect(x, z, radius, -48, 48, -41.8, -14.2);
    if (!inNorthSouth && !inEastWest) return false;
    return !NIGHT_INTERSECTION_COLLISIONS.some((obstacle) => (
      Math.abs(x - obstacle.x) < obstacle.halfWidth + radius
      && Math.abs(z - obstacle.z) < obstacle.halfDepth + radius
    ));
  },
};

export function mountNightIntersectionScene(
  scene: THREE.Scene,
  renderScene: () => void,
): NightIntersectionSceneMount {
  const root = new THREE.Group();
  root.name = "night-intersection";
  const materials = new Set<THREE.Material>();
  const textures = new Set<THREE.Texture>();

  const trackMaterial = <T extends THREE.Material>(value: T): T => {
    materials.add(value);
    return value;
  };

  const trackTexture = <T extends THREE.Texture>(value: T): T => {
    textures.add(value);
    return value;
  };

  const makeCanvasTexture = (
    size: number,
    draw: (ctx: CanvasRenderingContext2D, size: number) => void,
    repeatX = 1,
    repeatY = 1,
  ) => {
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Canvas 2D unavailable while building Night Intersection textures");
    draw(ctx, size);
    const texture = trackTexture(new THREE.CanvasTexture(canvas));
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(repeatX, repeatY);
    texture.anisotropy = 4;
    return texture;
  };

  const seededNoise = (index: number) => {
    const value = Math.sin(index * 12.9898 + 78.233) * 43758.5453;
    return value - Math.floor(value);
  };

  const asphaltTexture = makeCanvasTexture(512, (ctx, size) => {
    ctx.fillStyle = "#181b20";
    ctx.fillRect(0, 0, size, size);
    for (let i = 0; i < 4200; i += 1) {
      const x = Math.floor(seededNoise(i) * size);
      const y = Math.floor(seededNoise(i + 5000) * size);
      const shade = 24 + Math.floor(seededNoise(i + 9000) * 26);
      const alpha = 0.10 + seededNoise(i + 12000) * 0.18;
      ctx.fillStyle = `rgba(${shade},${shade + 2},${shade + 5},${alpha})`;
      ctx.fillRect(x, y, seededNoise(i + 15000) > 0.86 ? 3 : 1, 1);
    }
    ctx.strokeStyle = "rgba(118,126,135,0.12)";
    ctx.lineWidth = 1;
    for (let i = 0; i < 12; i += 1) {
      const y = 18 + i * 42;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.bezierCurveTo(size * 0.28, y + 8, size * 0.66, y - 6, size, y + 3);
      ctx.stroke();
    }
  }, 9, 9);

  const concreteTexture = makeCanvasTexture(384, (ctx, size) => {
    ctx.fillStyle = "#77736d";
    ctx.fillRect(0, 0, size, size);
    ctx.strokeStyle = "rgba(35,34,32,0.30)";
    ctx.lineWidth = 3;
    const tile = size / 4;
    for (let i = 0; i <= 4; i += 1) {
      ctx.beginPath();
      ctx.moveTo(i * tile, 0);
      ctx.lineTo(i * tile, size);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * tile);
      ctx.lineTo(size, i * tile);
      ctx.stroke();
    }
    for (let i = 0; i < 400; i += 1) {
      const g = 85 + Math.floor(seededNoise(i + 22000) * 70);
      ctx.fillStyle = `rgba(${g},${g - 2},${g - 5},0.16)`;
      ctx.fillRect(seededNoise(i) * size, seededNoise(i + 800) * size, 2, 2);
    }
  }, 7, 7);

  const facadeTexture = (base: string, mortar: string, columns: number, rows: number, seed: number) => makeCanvasTexture(512, (ctx, size) => {
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
  });

  const makeSignTexture = (label: string, tone: "warm" | "cool") => makeCanvasTexture(512, (ctx, size) => {
    ctx.fillStyle = tone === "warm" ? "#3e2416" : "#12313b";
    ctx.fillRect(0, 0, size, size);
    const gradient = ctx.createLinearGradient(0, 0, size, 0);
    gradient.addColorStop(0, tone === "warm" ? "#c96d2f" : "#2c8dad");
    gradient.addColorStop(0.5, tone === "warm" ? "#f2b66f" : "#8dd6e9");
    gradient.addColorStop(1, tone === "warm" ? "#a8572d" : "#276b82");
    ctx.fillStyle = gradient;
    ctx.fillRect(18, 18, size - 36, size - 36);
    ctx.strokeStyle = "rgba(255,255,255,0.45)";
    ctx.lineWidth = 6;
    ctx.strokeRect(25, 25, size - 50, size - 50);
    ctx.fillStyle = "#fff7df";
    ctx.font = "600 64px Georgia, serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(label, size / 2, size / 2 + 2);
  });

  const asphalt = trackMaterial(new THREE.MeshPhysicalMaterial({
    color: 0x353b43,
    map: asphaltTexture,
    roughness: 0.58,
    metalness: 0.18,
    clearcoat: 0.36,
    clearcoatRoughness: 0.34,
  }));
  const asphaltEdge = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x202329, map: asphaltTexture, roughness: 0.82 }));
  const concrete = trackMaterial(new THREE.MeshStandardMaterial({ color: 0xaaa49a, map: concreteTexture, roughness: 0.86 }));
  const curb = trackMaterial(new THREE.MeshStandardMaterial({ color: 0xa5a098, roughness: 0.78 }));
  const roadPaint = trackMaterial(new THREE.MeshStandardMaterial({ color: 0xd9d4c5, roughness: 0.62 }));
  const darkMetal = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x252a2f, roughness: 0.34, metalness: 0.74 }));
  const paleMetal = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x8e969b, roughness: 0.36, metalness: 0.62 }));
  const glass = trackMaterial(new THREE.MeshPhysicalMaterial({ color: 0x263d4e, roughness: 0.08, metalness: 0.2, transmission: 0.12, transparent: true, opacity: 0.84 }));
  const windowDark = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x10171d, emissive: 0x081018, emissiveIntensity: 0.28, roughness: 0.22 }));
  const windowWarm = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x9b663a, emissive: 0xffa649, emissiveIntensity: 1.35, roughness: 0.24 }));
  const windowCool = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x466a7a, emissive: 0x69b7d6, emissiveIntensity: 0.75, roughness: 0.2 }));
  const lampMaterial = trackMaterial(new THREE.MeshStandardMaterial({ color: 0xf3d6a2, emissive: 0xffcf82, emissiveIntensity: 3.1, roughness: 0.2 }));
  const redLight = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x7f1814, emissive: 0xff2f21, emissiveIntensity: 2.4 }));
  const amberLight = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x725213, emissive: 0xffa928, emissiveIntensity: 0.7 }));
  const greenLight = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x115d3b, emissive: 0x24e787, emissiveIntensity: 1.7 }));
  const tire = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x08090a, roughness: 0.94 }));
  const rim = trackMaterial(new THREE.MeshStandardMaterial({ color: 0xa7adb0, roughness: 0.3, metalness: 0.8 }));
  const trunkMaterial = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x3f3327, roughness: 0.98 }));
  const foliage = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x2d4a37, roughness: 0.94 }));
  const skin = trackMaterial(new THREE.MeshStandardMaterial({ color: 0xa57a62, roughness: 0.82 }));
  const coatA = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x344554, roughness: 0.88 }));
  const coatB = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x775042, roughness: 0.88 }));
  const wetPuddle = trackMaterial(new THREE.MeshPhysicalMaterial({ color: 0x161d24, roughness: 0.14, metalness: 0.42, clearcoat: 1, clearcoatRoughness: 0.1, transparent: true, opacity: 0.58 }));

  const addBox = (
    name: string,
    size: [number, number, number],
    position: [number, number, number],
    meshMaterial: THREE.Material,
    parent: THREE.Object3D = root,
    castShadow = false,
  ) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), meshMaterial);
    mesh.name = name;
    mesh.position.set(...position);
    mesh.castShadow = castShadow;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
  };

  const addInstancedBoxes = (
    name: string,
    size: [number, number, number],
    positions: Array<[number, number, number]>,
    meshMaterial: THREE.Material,
  ) => {
    const geometry = new THREE.BoxGeometry(...size);
    const mesh = new THREE.InstancedMesh(geometry, meshMaterial, positions.length);
    mesh.name = name;
    const matrix = new THREE.Matrix4();
    positions.forEach((position, index) => {
      matrix.makeTranslation(position[0], position[1], position[2]);
      mesh.setMatrixAt(index, matrix);
    });
    mesh.instanceMatrix.needsUpdate = true;
    root.add(mesh);
    return mesh;
  };

  const addCylinder = (
    name: string,
    radius: number,
    height: number,
    position: [number, number, number],
    meshMaterial: THREE.Material,
    parent: THREE.Object3D = root,
    segments = 16,
  ) => {
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, segments), meshMaterial);
    mesh.name = name;
    mesh.position.set(...position);
    mesh.castShadow = false;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
  };

  scene.background = new THREE.Color(0x111927);
  scene.fog = new THREE.FogExp2(0x111722, 0.0030);

  const hemisphere = new THREE.HemisphereLight(0xa8bad0, 0x3d3024, 0.95);
  hemisphere.name = "night-sky-fill";
  root.add(hemisphere);

  const ambient = new THREE.AmbientLight(0x8f9baa, 0.22);
  ambient.name = "street-ambient-fill";
  root.add(ambient);

  const moon = new THREE.DirectionalLight(0xb4c8de, 1.35);
  moon.name = "moon-key";
  moon.position.set(-38, 58, 30);
  moon.castShadow = true;
  moon.shadow.mapSize.set(1024, 1024);
  moon.shadow.camera.left = -70;
  moon.shadow.camera.right = 70;
  moon.shadow.camera.top = 70;
  moon.shadow.camera.bottom = -70;
  moon.shadow.bias = -0.00035;
  moon.shadow.normalBias = 0.025;
  root.add(moon);

  const intersectionFill = new THREE.PointLight(0xffddb0, 4.2, 36, 1.7);
  intersectionFill.name = "intersection-fill";
  intersectionFill.position.set(-2, 7.5, -25);
  root.add(intersectionFill);

  addBox("district-base", [150, 0.28, 150], [0, GROUND_Y - 0.18, -28], asphaltEdge, root, false);
  addBox("north-south-road", [19, 0.09, 150], [0, GROUND_Y, -28], asphalt, root, false);
  addBox("east-west-road", [150, 0.09, 19], [0, GROUND_Y + 0.01, -28], asphalt, root, false);

  const addSidewalk = (name: string, x: number, z: number, width: number, depth: number) => {
    addBox(name, [width, 0.3, depth], [x, GROUND_Y + 0.13, z], concrete, root, false);
  };
  addSidewalk("sidewalk-nw-long", -13.1, -66, 7.2, 58);
  addSidewalk("sidewalk-ne-long", 13.1, -66, 7.2, 58);
  addSidewalk("sidewalk-sw-long", -13.1, 10, 7.2, 58);
  addSidewalk("sidewalk-se-long", 13.1, 10, 7.2, 58);
  addSidewalk("sidewalk-nw-cross", -43, -40.1, 54, 7.2);
  addSidewalk("sidewalk-ne-cross", 43, -40.1, 54, 7.2);
  addSidewalk("sidewalk-sw-cross", -43, -15.9, 54, 7.2);
  addSidewalk("sidewalk-se-cross", 43, -15.9, 54, 7.2);

  for (const x of [-9.55, 9.55]) addBox(`curb-ns-${x}`, [0.34, 0.37, 150], [x, GROUND_Y + 0.17, -28], curb, root, false);
  for (const z of [-37.55, -18.45]) addBox(`curb-ew-${z}`, [150, 0.37, 0.34], [0, GROUND_Y + 0.18, z], curb, root, false);

  const crosswalkNs: Array<[number, number, number]> = [];
  const crosswalkEw: Array<[number, number, number]> = [];
  for (let i = 0; i < 9; i += 1) {
    const x = -7.6 + i * 1.9;
    crosswalkNs.push([x, GROUND_Y + 0.07, -17.9], [x, GROUND_Y + 0.07, -38.1]);
    const z = -35.6 + i * 1.9;
    crosswalkEw.push([-10.9, GROUND_Y + 0.075, z], [10.9, GROUND_Y + 0.075, z]);
  }
  addInstancedBoxes("crosswalk-ns-instances", [1.0, 0.026, 5.6], crosswalkNs, roadPaint);
  addInstancedBoxes("crosswalk-ew-instances", [5.6, 0.026, 1.0], crosswalkEw, roadPaint);

  const laneNs: Array<[number, number, number]> = [];
  for (const x of [-3.2, 3.2]) {
    for (let z = 34; z >= -96; z -= 13) laneNs.push([x, GROUND_Y + 0.07, z]);
  }
  addInstancedBoxes("lane-ns-instances", [0.16, 0.026, 5.4], laneNs, roadPaint);

  const laneEw: Array<[number, number, number]> = [];
  for (const z of [-24.8, -31.2]) {
    for (let x = -66; x <= 66; x += 13) laneEw.push([x, GROUND_Y + 0.075, z]);
  }
  addInstancedBoxes("lane-ew-instances", [5.4, 0.026, 0.16], laneEw, roadPaint);

  for (const [x, z, sx, sz, rotation] of [
    [-5.8, -7.2, 4.8, 1.5, -0.1],
    [5.2, -44.5, 3.4, 1.2, 0.14],
    [-28, -30.7, 6.5, 1.4, 0.02],
    [30, -25.4, 5.1, 1.2, -0.08],
  ] as const) {
    const puddle = addBox(`puddle-${x}-${z}`, [sx, 0.012, sz], [x, GROUND_Y + 0.085, z], wetPuddle, root, false);
    puddle.rotation.y = rotation;
  }


  const addStorefront = (group: THREE.Group, options: BuildingOptions) => {
    const signTexture = makeSignTexture(options.sign, options.signTone);
    const signMaterial = trackMaterial(new THREE.MeshStandardMaterial({
      map: signTexture,
      emissiveMap: signTexture,
      emissive: 0xffffff,
      emissiveIntensity: 1.2,
      roughness: 0.32,
    }));
    const storeGlass = trackMaterial(new THREE.MeshPhysicalMaterial({
      color: options.signTone === "warm" ? 0x5b3829 : 0x1f4652,
      emissive: options.signTone === "warm" ? 0xff9f55 : 0x5bc1dc,
      emissiveIntensity: options.signTone === "warm" ? 0.72 : 0.48,
      roughness: 0.12,
      metalness: 0.1,
      transparent: true,
      opacity: 0.9,
    }));
    const face = options.front;
    const y = -options.height / 2 + 1.55;
    const signY = -options.height / 2 + 3.55;
    const entranceY = -options.height / 2 + 1.34;
    if (face === "north" || face === "south") {
      const z = face === "north" ? -options.depth / 2 - 0.11 : options.depth / 2 + 0.11;
      const signZ = z + (face === "north" ? -0.05 : 0.05);
      const width = Math.min(15.5, options.width * 0.62);
      addBox(`store-glass-${face}`, [width, 2.82, 0.16], [0, y, z], storeGlass, group, false);
      for (const x of [-width / 3, 0, width / 3]) addBox(`store-mullion-${face}-${x}`, [0.1, 2.9, 0.22], [x, y, z], darkMetal, group);
      addBox(`store-door-${face}`, [1.65, 2.55, 0.24], [width * 0.29, entranceY, z + (face === "north" ? -0.02 : 0.02)], glass, group);
      addBox(`store-sign-${face}`, [Math.min(12.5, options.width * 0.52), 1.05, 0.18], [0, signY, signZ], signMaterial, group, false);
      addBox(`store-awning-${face}`, [Math.min(13.5, options.width * 0.56), 0.18, 1.35], [0, signY - 0.72, z + (face === "north" ? -0.68 : 0.68)], darkMetal, group);
    } else {
      const x = face === "west" ? -options.width / 2 - 0.11 : options.width / 2 + 0.11;
      const signX = x + (face === "west" ? -0.05 : 0.05);
      const width = Math.min(15.5, options.depth * 0.62);
      addBox(`store-glass-${face}`, [0.16, 2.82, width], [x, y, 0], storeGlass, group, false);
      for (const z of [-width / 3, 0, width / 3]) addBox(`store-mullion-${face}-${z}`, [0.22, 2.9, 0.1], [x, y, z], darkMetal, group);
      addBox(`store-door-${face}`, [0.24, 2.55, 1.65], [x + (face === "west" ? -0.02 : 0.02), entranceY, width * 0.29], glass, group);
      addBox(`store-sign-${face}`, [0.18, 1.05, Math.min(12.5, options.depth * 0.52)], [signX, signY, 0], signMaterial, group, false);
      addBox(`store-awning-${face}`, [1.35, 0.18, Math.min(13.5, options.depth * 0.56)], [x + (face === "west" ? -0.68 : 0.68), signY - 0.72, 0], darkMetal, group);
    }
  };

  const addBuilding = (name: string, options: BuildingOptions) => {
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
    const upperWidth = Math.max(12, options.width - 4.6);
    const upperDepth = Math.max(12, options.depth - 4.0);
    const upperShiftX = options.x < 0 ? 1.35 : -1.35;
    const upperShiftZ = options.front === "south" ? -0.9 : 0.9;
    const podiumY = -options.height / 2 + podiumHeight / 2;
    const upperY = -options.height / 2 + podiumHeight + upperHeight / 2;

    addBox(`${name}-podium`, [options.width, podiumHeight, options.depth], [0, podiumY, 0], facadeMaterial, group, true);
    addBox(`${name}-upper`, [upperWidth, upperHeight, upperDepth], [upperShiftX, upperY, upperShiftZ], facadeMaterial, group, true);
    const bayWidth = Math.max(5.2, upperWidth * 0.34);
    const bayHeight = Math.max(6.2, upperHeight * 0.72);
    const bayX = upperShiftX + (options.x < 0 ? upperWidth * 0.31 : -upperWidth * 0.31);
    const bayZ = upperShiftZ + (options.front === "south" ? upperDepth * 0.12 : -upperDepth * 0.12);
    const bayY = -options.height / 2 + podiumHeight + bayHeight / 2 + 0.18;
    addBox(`${name}-corner-bay`, [bayWidth, bayHeight, upperDepth + 0.9], [bayX, bayY, bayZ], facadeMaterial, group, true);
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
  };

  addBuilding("north-west-block", { x: -34, z: -59, width: 34, depth: 34, height: 20, floors: 6, facade: 0x8a7868, trim: 0x303136, front: "south", side: "east", sign: "NIGHT MARKET", signTone: "warm", balconies: true });
  addBuilding("north-east-block", { x: 33, z: -61, width: 32, depth: 38, height: 28, floors: 8, facade: 0x72818a, trim: 0x30363b, front: "south", side: "west", sign: "BLUE HOUR", signTone: "cool" });
  addBuilding("south-west-block", { x: -36, z: 8, width: 38, depth: 42, height: 16, floors: 5, facade: 0x8d7563, trim: 0x362f2a, front: "north", side: "east", sign: "CAFE 24", signTone: "warm" });
  addBuilding("south-east-block", { x: 36, z: 7, width: 38, depth: 40, height: 23, floors: 7, facade: 0x71848a, trim: 0x2c3437, front: "north", side: "west", sign: "CITY BOOKS", signTone: "cool", balconies: true });
  addBuilding("far-north-left", { x: -31, z: -101, width: 34, depth: 24, height: 25, floors: 7, facade: 0x68737e, trim: 0x292e33, front: "south", sign: "HOTEL", signTone: "warm" });
  addBuilding("far-north-right", { x: 33, z: -101, width: 34, depth: 24, height: 19, floors: 5, facade: 0x796b60, trim: 0x302e2b, front: "south", sign: "DINER", signTone: "warm" });

  const addStreetSign = (name: string, label: string, tone: "warm" | "cool", x: number, y: number, z: number, width: number, height: number) => {
    const texture = makeSignTexture(label, tone);
    const signMaterial = trackMaterial(new THREE.MeshStandardMaterial({
      map: texture,
      emissiveMap: texture,
      emissive: 0xffffff,
      emissiveIntensity: 1.45,
      roughness: 0.28,
      side: THREE.DoubleSide,
    }));
    const sign = new THREE.Mesh(new THREE.PlaneGeometry(width, height), signMaterial);
    sign.name = name;
    sign.position.set(x, GROUND_Y + y, z);
    sign.castShadow = false;
    root.add(sign);
    addBox(`${name}-frame`, [width + 0.18, height + 0.18, 0.08], [x, GROUND_Y + y, z + 0.04], darkMetal, root);
  };

  addStreetSign("corner-market-sign", "MARKET", "warm", -12.8, 4.2, -41.75, 5.6, 1.25);
  addStreetSign("corner-books-sign", "BOOKS", "cool", 12.8, 4.2, -41.75, 5.2, 1.25);
  addStreetSign("bus-stop-sign", "BUS", "cool", -10.8, 2.8, -22.2, 1.1, 1.75);

  const backgroundBuildings: Array<[number, number, number, number, number]> = [
    [-62, -74, 22, 28, 30], [-62, -25, 24, 30, 18], [62, -74, 24, 30, 24], [62, -22, 24, 30, 34],
    [-48, 29, 30, 28, 21], [48, 28, 30, 28, 27], [-62, -112, 24, 24, 20], [62, -112, 24, 24, 26],
  ];
  for (const [x, z, width, depth, height] of backgroundBuildings) {
    const mat = trackMaterial(new THREE.MeshStandardMaterial({ color: x < 0 ? 0x40454b : 0x464b50, roughness: 0.84 }));
    addBox(`background-building-${x}-${z}`, [width, height, depth], [x, GROUND_Y + height / 2, z], mat);
    const roof = trackMaterial(new THREE.MeshStandardMaterial({ color: 0x252a30, roughness: 0.72 }));
    addBox(`background-roof-${x}-${z}`, [width + 0.5, 0.4, depth + 0.5], [x, GROUND_Y + height + 0.2, z], roof);
  }

  const addStreetlight = (name: string, x: number, z: number, towardRoad: 1 | -1) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    root.add(group);
    addCylinder(`${name}-pole`, 0.13, 7.6, [0, 3.8, 0], darkMetal, group, 14);
    const arm = addCylinder(`${name}-arm`, 0.095, 2.4, [towardRoad * 1.02, 7.34, 0], darkMetal, group, 14);
    arm.rotation.z = Math.PI / 2;
    addBox(`${name}-housing`, [0.92, 0.2, 0.5], [towardRoad * 2.0, 7.18, 0], darkMetal, group);
    addBox(`${name}-lamp`, [0.72, 0.08, 0.34], [towardRoad * 2.0, 7.04, 0], lampMaterial, group, false);
    const light = new THREE.SpotLight(0xffc47b, 26, 27, Math.PI / 4.2, 0.72, 1.25);
    light.name = `${name}-light`;
    light.position.set(towardRoad * 2.0, 6.92, 0);
    light.target.position.set(towardRoad * 3.2, 0, 0);
    group.add(light, light.target);
  };
  addStreetlight("streetlight-sw", -13.8, -12.5, 1);
  addStreetlight("streetlight-se", 13.8, -12.5, -1);
  addStreetlight("streetlight-nw", -13.8, -43.5, 1);
  addStreetlight("streetlight-ne", 13.8, -43.5, -1);
  addStreetlight("streetlight-near-west", -13.8, 18, 1);
  addStreetlight("streetlight-far-east", 13.8, -73, -1);

  const addTrafficSignal = (name: string, x: number, z: number, rotationY: number, active: "red" | "green") => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    group.rotation.y = rotationY;
    root.add(group);
    addCylinder(`${name}-pole`, 0.14, 4.8, [0, 2.4, 0], darkMetal, group, 14);
    addBox(`${name}-housing`, [0.68, 1.95, 0.58], [0, 4.6, 0], darkMetal, group);
    const mats = active === "red" ? [redLight, amberLight, windowDark] : [windowDark, amberLight, greenLight];
    mats.forEach((mat, index) => {
      const lens = new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 10), mat);
      lens.name = `${name}-lens-${index}`;
      lens.position.set(0, 5.14 - index * 0.53, -0.31);
      lens.scale.z = 0.42;
      group.add(lens);
    });
    addBox(`${name}-visor`, [0.62, 0.12, 0.45], [0, active === "red" ? 5.4 : 4.32, -0.48], darkMetal, group);
  };
  addTrafficSignal("signal-sw", -8.4, -18.2, 0, "red");
  addTrafficSignal("signal-se", 8.4, -18.2, 0, "green");
  addTrafficSignal("signal-nw", -8.4, -37.8, Math.PI, "green");
  addTrafficSignal("signal-east", 9.2, -36.2, -Math.PI / 2, "red");

  const paints = [0x7e3432, 0x31566f, 0xc0ad83, 0x45484d].map((color) => trackMaterial(new THREE.MeshPhysicalMaterial({ color, roughness: 0.4, metalness: 0.28, clearcoat: 0.5, clearcoatRoughness: 0.28 })));

  const addCarShell = (
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

  const addPedestrian = (name: string, x: number, z: number, coat: THREE.Material, scale = 1, heading = 0) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    group.rotation.y = heading;
    group.scale.setScalar(scale);
    root.add(group);
    addCylinder(`${name}-torso`, 0.29, 1.02, [0, 1.2, 0], coat, group, 14);
    const shoulders = addBox(`${name}-shoulders`, [0.72, 0.18, 0.34], [0, 1.58, 0], coat, group);
    shoulders.rotation.z = 0.02;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.235, 16, 12), skin);
    head.name = `${name}-head`;
    head.position.set(0, 1.94, 0);
    head.castShadow = true;
    group.add(head);
    for (const side of [-1, 1]) {
      const leg = addCylinder(`${name}-leg-${side}`, 0.095, 0.92, [side * 0.13, 0.5, 0], darkMetal, group, 10);
      leg.rotation.z = side * 0.055;
      const arm = addCylinder(`${name}-arm-${side}`, 0.075, 0.84, [side * 0.38, 1.25, 0], coat, group, 10);
      arm.rotation.z = side * 0.22;
    }
  };
  addPedestrian("target-mid-pedestrian", -10.9, -21.5, coatB, 1, 0.2);
  addPedestrian("pedestrian-east", 11.8, -33.4, coatA, 0.96, -0.4);
  addPedestrian("pedestrian-far", -11.9, -61, coatB, 0.92, 0.1);
  addPedestrian("pedestrian-near", 11.6, -8, coatA, 1.02, -0.25);
  addPedestrian("pedestrian-crossing", 4.8, -23.2, coatB, 0.98, Math.PI / 2);

  const addBench = (name: string, x: number, z: number, rotationY: number) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    group.rotation.y = rotationY;
    root.add(group);
    for (let i = -4; i <= 4; i += 1) addBox(`${name}-slat-${i}`, [2.35, 0.08, 0.07], [0, 0.58 + Math.max(0, i) * 0.08, i * 0.07], i > 0 ? darkMetal : paleMetal, group);
    addBox(`${name}-seat`, [2.35, 0.14, 0.68], [0, 0.58, 0], paleMetal, group);
    for (const xLeg of [-0.82, 0.82]) addBox(`${name}-leg-${xLeg}`, [0.12, 0.6, 0.48], [xLeg, 0.3, 0], darkMetal, group);
  };
  addBench("bench-west", -14.2, -8.3, Math.PI / 2);
  addBench("bench-east", 14.4, -50.5, -Math.PI / 2);

  const shelter = new THREE.Group();
  shelter.name = "bus-shelter-east";
  shelter.position.set(14.4, GROUND_Y, -24.5);
  root.add(shelter);
  addBox("bus-shelter-roof", [4.6, 0.16, 1.8], [0, 2.65, 0], darkMetal, shelter);
  addBox("bus-shelter-back", [4.5, 2.25, 0.08], [0, 1.35, 0.78], glass, shelter, false);
  addBox("bus-shelter-side", [0.08, 2.25, 1.55], [-2.15, 1.35, 0], glass, shelter, false);
  for (const px of [-2.15, 2.15]) addCylinder(`bus-shelter-post-${px}`, 0.07, 2.65, [px, 1.33, 0.72], darkMetal, shelter, 10);
  addBox("bus-shelter-seat", [2.7, 0.16, 0.48], [0.4, 0.58, 0.42], paleMetal, shelter);
  addBox("utility-cabinet", [1.25, 1.62, 0.76], [-14.5, GROUND_Y + 0.82, -44.5], paleMetal);
  addCylinder("bin-east", 0.4, 1.08, [14.2, GROUND_Y + 0.54, -11], darkMetal, root, 16);
  for (const z of [-5, 3, 11]) addCylinder(`bollard-west-${z}`, 0.13, 0.88, [-9.9, GROUND_Y + 0.44, z], paleMetal, root, 12);

  const addTree = (name: string, x: number, z: number, height: number) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    root.add(group);
    addCylinder(`${name}-trunk`, 0.3, height * 0.46, [0, height * 0.23, 0], trunkMaterial, group, 14);
    const branches: Array<[number, number, number, number]> = [[0, 0.6, 0, 1], [-0.7, 0.68, 0.25, 0.75], [0.72, 0.66, -0.28, 0.8], [0.15, 0.79, 0.35, 0.6]];
    branches.forEach(([dx, dy, dz, scale], index) => {
      const crown = new THREE.Mesh(new THREE.DodecahedronGeometry(1.7 * scale, 1), foliage);
      crown.name = `${name}-crown-${index}`;
      crown.position.set(dx, height * dy, dz);
      crown.scale.y = 1.25;
      crown.castShadow = false;
      group.add(crown);
    });
  };
  addTree("tree-sw", -15.2, 17, 7.0);
  addTree("tree-se", 15.4, 21, 7.5);
  addTree("tree-nw", -15.5, -69, 8.2);
  addTree("tree-ne", 15.7, -75, 7.8);
  addTree("tree-west-mid", -15.3, -49, 6.6);

  const addPole = (name: string, x: number, z: number, height: number) => addCylinder(name, 0.17, height, [x, GROUND_Y + height / 2, z], darkMetal, root, 14);
  addPole("wire-pole-west", -15.9, -54, 11.2);
  addPole("wire-pole-east", 15.9, -54, 11.2);
  addPole("wire-pole-far-west", -15.9, -89, 12.1);
  addPole("wire-pole-far-east", 15.9, -89, 12.1);
  const lineMaterial = trackMaterial(new THREE.LineBasicMaterial({ color: 0x59606a, transparent: true, opacity: 0.76 }));
  const addWire = (name: string, points: THREE.Vector3[]) => {
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), lineMaterial);
    line.name = name;
    root.add(line);
  };
  addWire("wire-cross-a", [new THREE.Vector3(-15.9, 8.9, -54), new THREE.Vector3(0, 8.4, -54), new THREE.Vector3(15.9, 8.9, -54)]);
  addWire("wire-cross-b", [new THREE.Vector3(-15.9, 9.5, -89), new THREE.Vector3(0, 8.9, -89), new THREE.Vector3(15.9, 9.5, -89)]);
  addWire("wire-west", [new THREE.Vector3(-15.9, 8.9, -54), new THREE.Vector3(-15.9, 9.4, -71), new THREE.Vector3(-15.9, 9.5, -89)]);
  addWire("wire-east", [new THREE.Vector3(15.9, 8.9, -54), new THREE.Vector3(15.9, 9.4, -71), new THREE.Vector3(15.9, 9.5, -89)]);

  const farSignTexture = makeSignTexture("CENTRAL", "cool");
  const farSignMaterial = trackMaterial(new THREE.MeshStandardMaterial({ map: farSignTexture, emissiveMap: farSignTexture, emissive: 0xffffff, emissiveIntensity: 0.95, roughness: 0.3 }));
  addBox("target-far-sign-post", [0.24, 4.8, 0.24], [7.1, GROUND_Y + 2.4, -91], paleMetal);
  addBox("target-far-sign", [5.2, 1.45, 0.18], [7.1, GROUND_Y + 4.55, -91], farSignMaterial, root, false);
  addBox("target-rooftop-ledge", [8.4, 0.48, 1.3], [33, GROUND_Y + 28.4, -43], paleMetal);
  addCylinder("roof-antenna", 0.1, 7.2, [33, GROUND_Y + 31.4, -61], paleMetal, root, 10);

  const shopWest = new THREE.PointLight(0xff9b55, 18.0, 23, 2.0);
  shopWest.name = "storefront-west-light";
  shopWest.position.set(-18, GROUND_Y + 3.1, -40);
  root.add(shopWest);
  const shopEast = new THREE.PointLight(0x72c5de, 16.5, 22, 2.0);
  shopEast.name = "storefront-east-light";
  shopEast.position.set(17, GROUND_Y + 3.2, -41);
  root.add(shopEast);

  const starsGeometry = new THREE.BufferGeometry();
  const starPositions: number[] = [];
  for (let i = 0; i < 180; i += 1) {
    const angle = seededNoise(i + 40000) * Math.PI * 2;
    const radius = 85 + seededNoise(i + 41000) * 45;
    const y = 36 + seededNoise(i + 42000) * 36;
    starPositions.push(Math.cos(angle) * radius, y, -28 + Math.sin(angle) * radius);
  }
  starsGeometry.setAttribute("position", new THREE.Float32BufferAttribute(starPositions, 3));
  const starMaterial = trackMaterial(new THREE.PointsMaterial({ color: 0xb8c6d8, size: 0.28, transparent: true, opacity: 0.72, sizeAttenuation: true }));
  const stars = new THREE.Points(starsGeometry, starMaterial);
  stars.name = "night-sky-stars";
  root.add(stars);

  scene.add(root);
  renderScene();

  let objectCount = 0;
  let lightCount = 0;
  root.traverse((object) => {
    objectCount += 1;
    if (object instanceof THREE.Light) lightCount += 1;
  });

  return {
    root,
    objectCount,
    lightCount,
    dispose: () => {
      scene.remove(root);
      root.traverse((object) => {
        const mesh = object as THREE.Mesh;
        mesh.geometry?.dispose?.();
        if (object instanceof THREE.Line || object instanceof THREE.Points) object.geometry.dispose();
      });
      for (const item of materials) item.dispose();
      for (const item of textures) item.dispose();
      if (scene.fog instanceof THREE.FogExp2) scene.fog = null;
      if (scene.background instanceof THREE.Color) scene.background = null;
    },
  };
}
