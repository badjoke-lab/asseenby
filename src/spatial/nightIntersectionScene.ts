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

  const facadeTexture = (base: string, mortar: string, repeatX: number, repeatY: number) => makeCanvasTexture(256, (ctx, size) => {
    ctx.fillStyle = base;
    ctx.fillRect(0, 0, size, size);
    ctx.strokeStyle = mortar;
    ctx.lineWidth = 1;
    const row = 20;
    for (let y = 0; y < size; y += row) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(size, y);
      ctx.stroke();
      const offset = (Math.floor(y / row) % 2) * 20;
      for (let x = -offset; x < size; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x, Math.min(size, y + row));
        ctx.stroke();
      }
    }
    const gradient = ctx.createLinearGradient(0, 0, size, 0);
    gradient.addColorStop(0, "rgba(255,255,255,0.08)");
    gradient.addColorStop(0.52, "rgba(0,0,0,0.06)");
    gradient.addColorStop(1, "rgba(255,255,255,0.03)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);
  }, repeatX, repeatY);

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
    color: 0x252930,
    map: asphaltTexture,
    roughness: 0.52,
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
    castShadow = true,
  ) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), meshMaterial);
    mesh.name = name;
    mesh.position.set(...position);
    mesh.castShadow = castShadow;
    mesh.receiveShadow = true;
    parent.add(mesh);
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
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
  };

  scene.background = new THREE.Color(0x111927);
  scene.fog = new THREE.FogExp2(0x111722, 0.0042);

  const hemisphere = new THREE.HemisphereLight(0x91a9c7, 0x2a2018, 1.3);
  hemisphere.name = "night-sky-fill";
  root.add(hemisphere);

  const moon = new THREE.DirectionalLight(0xa7bdd7, 1.28);
  moon.name = "moon-key";
  moon.position.set(-38, 58, 30);
  moon.castShadow = true;
  moon.shadow.mapSize.set(1024, 1024);
  moon.shadow.camera.left = -70;
  moon.shadow.camera.right = 70;
  moon.shadow.camera.top = 70;
  moon.shadow.camera.bottom = -70;
  moon.shadow.bias = -0.0007;
  root.add(moon);

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

  for (let i = 0; i < 9; i += 1) {
    const x = -7.6 + i * 1.9;
    addBox(`crosswalk-s-${i}`, [1.0, 0.026, 5.6], [x, GROUND_Y + 0.07, -17.9], roadPaint, root, false);
    addBox(`crosswalk-n-${i}`, [1.0, 0.026, 5.6], [x, GROUND_Y + 0.07, -38.1], roadPaint, root, false);
    const z = -35.6 + i * 1.9;
    addBox(`crosswalk-w-${i}`, [5.6, 0.026, 1.0], [-10.9, GROUND_Y + 0.075, z], roadPaint, root, false);
    addBox(`crosswalk-e-${i}`, [5.6, 0.026, 1.0], [10.9, GROUND_Y + 0.075, z], roadPaint, root, false);
  }
  for (const x of [-3.2, 3.2]) {
    for (let z = 34; z >= -96; z -= 13) addBox(`lane-${x}-${z}`, [0.16, 0.026, 5.4], [x, GROUND_Y + 0.07, z], roadPaint, root, false);
  }
  for (const z of [-24.8, -31.2]) {
    for (let x = -66; x <= 66; x += 13) addBox(`lane-cross-${x}-${z}`, [5.4, 0.026, 0.16], [x, GROUND_Y + 0.075, z], roadPaint, root, false);
  }

  for (const [x, z, sx, sz, rotation] of [
    [-5.8, -7.2, 4.8, 1.5, -0.1],
    [5.2, -44.5, 3.4, 1.2, 0.14],
    [-28, -30.7, 6.5, 1.4, 0.02],
    [30, -25.4, 5.1, 1.2, -0.08],
  ] as const) {
    const puddle = addBox(`puddle-${x}-${z}`, [sx, 0.012, sz], [x, GROUND_Y + 0.085, z], wetPuddle, root, false);
    puddle.rotation.y = rotation;
  }

  const addFacadeWindows = (group: THREE.Group, options: BuildingOptions, face: Face) => {
    const horizontalSpan = face === "north" || face === "south" ? options.width : options.depth;
    const columns = Math.max(4, Math.floor(horizontalSpan / 4.1));
    const spacing = horizontalSpan / columns;
    const baseY = -options.height / 2 + 4.6;
    const floorStep = (options.height - 5.4) / Math.max(1, options.floors - 1);
    for (let floor = 0; floor < options.floors - 1; floor += 1) {
      for (let col = 0; col < columns; col += 1) {
        const offset = -horizontalSpan / 2 + spacing * (col + 0.5);
        const pattern = Math.abs((floor * 13 + col * 7 + Math.round(options.x - options.z)) % 7);
        const pane = pattern === 0 || pattern === 5 ? windowWarm : pattern === 2 ? windowCool : windowDark;
        const y = baseY + floor * floorStep;
        if (face === "north" || face === "south") {
          const z = face === "north" ? -options.depth / 2 - 0.075 : options.depth / 2 + 0.075;
          addBox(`window-frame-${face}-${floor}-${col}`, [2.3, 1.72, 0.12], [offset, y, z], darkMetal, group);
          addBox(`window-pane-${face}-${floor}-${col}`, [1.92, 1.36, 0.14], [offset, y, z + (face === "north" ? -0.02 : 0.02)], pane, group, false);
          addBox(`window-sill-${face}-${floor}-${col}`, [2.42, 0.12, 0.3], [offset, y - 0.94, z + (face === "north" ? -0.08 : 0.08)], options.front === face ? paleMetal : darkMetal, group);
        } else {
          const x = face === "west" ? -options.width / 2 - 0.075 : options.width / 2 + 0.075;
          addBox(`window-frame-${face}-${floor}-${col}`, [0.12, 1.72, 2.3], [x, y, offset], darkMetal, group);
          addBox(`window-pane-${face}-${floor}-${col}`, [0.14, 1.36, 1.92], [x + (face === "west" ? -0.02 : 0.02), y, offset], pane, group, false);
          addBox(`window-sill-${face}-${floor}-${col}`, [0.3, 0.12, 2.42], [x + (face === "west" ? -0.08 : 0.08), y - 0.94, offset], options.front === face ? paleMetal : darkMetal, group);
        }
      }
    }
  };

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
    const tex = facadeTexture(
      typeof options.facade === "number" && (options.facade as number) < 0x505050 ? "#34373b" : "#5b5047",
      "rgba(210,205,195,0.12)",
      Math.max(2, options.width / 12),
      Math.max(2, options.height / 8),
    );
    const facadeMaterial = trackMaterial(new THREE.MeshStandardMaterial({ color: options.facade, map: tex, roughness: 0.78, metalness: 0.03 }));
    const trimMaterial = trackMaterial(new THREE.MeshStandardMaterial({ color: options.trim, roughness: 0.66, metalness: 0.08 }));
    addBox(`${name}-mass`, [options.width, options.height, options.depth], [0, 0, 0], facadeMaterial, group);
    addBox(`${name}-roof-cap`, [options.width + 0.8, 0.45, options.depth + 0.8], [0, options.height / 2 + 0.22, 0], trimMaterial, group);
    addBox(`${name}-ground-belt`, [options.width + 0.28, 0.75, options.depth + 0.28], [0, -options.height / 2 + 0.38, 0], trimMaterial, group);
    for (const x of [-options.width * 0.28, options.width * 0.28]) addBox(`${name}-vertical-band-${x}`, [0.24, options.height - 1, options.depth + 0.16], [x, 0.15, 0], trimMaterial, group);
    addFacadeWindows(group, options, options.front);
    if (options.side) addFacadeWindows(group, options, options.side);
    addStorefront(group, options);
    if (options.balconies) {
      for (let floor = 1; floor < Math.min(options.floors - 1, 5); floor += 2) {
        const y = -options.height / 2 + 4.8 + floor * 2.8;
        if (options.front === "south" || options.front === "north") {
          const z = options.front === "south" ? options.depth / 2 + 0.62 : -options.depth / 2 - 0.62;
          addBox(`${name}-balcony-${floor}`, [7.5, 0.16, 1.15], [0, y - 0.7, z], darkMetal, group);
          addBox(`${name}-balcony-rail-${floor}`, [7.5, 0.72, 0.08], [0, y - 0.35, z + (options.front === "south" ? 0.52 : -0.52)], paleMetal, group);
        }
      }
    }
    addBox(`${name}-roof-service`, [3.8, 1.6, 2.8], [options.width * 0.18, options.height / 2 + 1.0, -options.depth * 0.12], trimMaterial, group);
    return group;
  };

  addBuilding("north-west-block", { x: -34, z: -59, width: 34, depth: 34, height: 20, floors: 6, facade: 0x6a5b50, trim: 0x303136, front: "south", side: "east", sign: "NIGHT MARKET", signTone: "warm", balconies: true });
  addBuilding("north-east-block", { x: 33, z: -61, width: 32, depth: 38, height: 28, floors: 8, facade: 0x59636b, trim: 0x30363b, front: "south", side: "west", sign: "BLUE HOUR", signTone: "cool" });
  addBuilding("south-west-block", { x: -36, z: 8, width: 38, depth: 42, height: 16, floors: 5, facade: 0x715d4f, trim: 0x362f2a, front: "north", side: "east", sign: "CAFE 24", signTone: "warm" });
  addBuilding("south-east-block", { x: 36, z: 7, width: 38, depth: 40, height: 23, floors: 7, facade: 0x566469, trim: 0x2c3437, front: "north", side: "west", sign: "CITY BOOKS", signTone: "cool", balconies: true });
  addBuilding("far-north-left", { x: -31, z: -101, width: 34, depth: 24, height: 25, floors: 7, facade: 0x50565e, trim: 0x292e33, front: "south", sign: "HOTEL", signTone: "warm" });
  addBuilding("far-north-right", { x: 33, z: -101, width: 34, depth: 24, height: 19, floors: 5, facade: 0x625850, trim: 0x302e2b, front: "south", sign: "DINER", signTone: "warm" });

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
  const addCar = (name: string, x: number, z: number, rotationY: number, paint: THREE.Material, van = false) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    group.rotation.y = rotationY;
    root.add(group);
    const length = van ? 5.5 : 4.5;
    addBox(`${name}-lower`, [1.92, 0.58, length], [0, 0.64, 0], paint, group);
    addBox(`${name}-hood`, [1.78, 0.34, van ? 1.25 : 1.2], [0, 1.0, -length * 0.31], paint, group);
    addBox(`${name}-trunk`, [1.76, 0.32, van ? 0.62 : 1.0], [0, 0.96, length * 0.35], paint, group);
    addBox(`${name}-cabin`, [1.62, van ? 1.45 : 1.02, van ? 2.9 : 2.15], [0, van ? 1.5 : 1.36, van ? 0.15 : 0.02], paint, group);
    addBox(`${name}-windshield`, [1.46, van ? 0.82 : 0.72, 0.08], [0, van ? 1.72 : 1.57, -length * 0.2], glass, group, false);
    addBox(`${name}-rear-glass`, [1.46, van ? 0.78 : 0.68, 0.08], [0, van ? 1.65 : 1.52, length * 0.22], glass, group, false);
    for (const side of [-1, 1]) {
      addBox(`${name}-side-glass-${side}`, [0.08, van ? 0.86 : 0.67, van ? 1.95 : 1.35], [side * 0.83, van ? 1.65 : 1.53, 0.03], glass, group, false);
      addBox(`${name}-mirror-${side}`, [0.22, 0.12, 0.34], [side * 1.05, 1.44, -length * 0.18], darkMetal, group);
      for (const axle of [-1, 1]) {
        const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.39, 0.39, 0.24, 18), tire);
        wheel.name = `${name}-wheel-${side}-${axle}`;
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(side * 0.99, 0.4, axle * length * 0.31);
        wheel.castShadow = true;
        group.add(wheel);
        const wheelRim = new THREE.Mesh(new THREE.CylinderGeometry(0.19, 0.19, 0.252, 18), rim);
        wheelRim.rotation.z = Math.PI / 2;
        wheelRim.position.copy(wheel.position);
        group.add(wheelRim);
      }
    }
    for (const side of [-0.55, 0.55]) {
      addBox(`${name}-headlight-${side}`, [0.34, 0.18, 0.08], [side, 0.86, -length / 2 - 0.08], lampMaterial, group, false);
      addBox(`${name}-taillight-${side}`, [0.3, 0.16, 0.08], [side, 0.82, length / 2 + 0.08], redLight, group, false);
    }
    addBox(`${name}-front-bumper`, [1.68, 0.16, 0.16], [0, 0.47, -length / 2 - 0.1], paleMetal, group);
    addBox(`${name}-rear-bumper`, [1.68, 0.16, 0.16], [0, 0.47, length / 2 + 0.1], paleMetal, group);
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
      crown.castShadow = true;
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

  const shopWest = new THREE.PointLight(0xff9b55, 10.5, 20, 2.0);
  shopWest.name = "storefront-west-light";
  shopWest.position.set(-18, GROUND_Y + 3.1, -40);
  root.add(shopWest);
  const shopEast = new THREE.PointLight(0x72c5de, 9.4, 19, 2.0);
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
