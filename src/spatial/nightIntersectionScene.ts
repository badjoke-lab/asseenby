import * as THREE from "three";

const GROUND_Y = -1.6;

export type NightIntersectionSceneMount = {
  root: THREE.Group;
  objectCount: number;
  lightCount: number;
  dispose: () => void;
};

type BuildingOptions = {
  x: number;
  z: number;
  width: number;
  depth: number;
  height: number;
  floors: number;
  facade: THREE.ColorRepresentation;
  accent: THREE.ColorRepresentation;
  front: "north" | "south" | "east" | "west";
  side?: "north" | "south" | "east" | "west";
  signColor?: THREE.ColorRepresentation;
};

export function mountNightIntersectionScene(
  scene: THREE.Scene,
  renderScene: () => void,
): NightIntersectionSceneMount {
  const root = new THREE.Group();
  root.name = "night-intersection";
  const materials = new Set<THREE.Material>();

  const material = <T extends THREE.Material>(value: T): T => {
    materials.add(value);
    return value;
  };

  const asphalt = material(new THREE.MeshStandardMaterial({ color: 0x171a1f, roughness: 0.82, metalness: 0.08 }));
  const asphaltEdge = material(new THREE.MeshStandardMaterial({ color: 0x22262b, roughness: 0.9 }));
  const concrete = material(new THREE.MeshStandardMaterial({ color: 0x66645f, roughness: 0.92 }));
  const curb = material(new THREE.MeshStandardMaterial({ color: 0x8a877f, roughness: 0.88 }));
  const roadPaint = material(new THREE.MeshStandardMaterial({ color: 0xd8d2bc, roughness: 0.72 }));
  const darkMetal = material(new THREE.MeshStandardMaterial({ color: 0x24272b, roughness: 0.48, metalness: 0.62 }));
  const paleMetal = material(new THREE.MeshStandardMaterial({ color: 0x777a7d, roughness: 0.46, metalness: 0.52 }));
  const glass = material(new THREE.MeshStandardMaterial({ color: 0x233342, roughness: 0.2, metalness: 0.18 }));
  const windowDark = material(new THREE.MeshStandardMaterial({ color: 0x11171d, emissive: 0x05090e, emissiveIntensity: 0.35, roughness: 0.28 }));
  const windowWarm = material(new THREE.MeshStandardMaterial({ color: 0xc49455, emissive: 0xffb85f, emissiveIntensity: 0.7, roughness: 0.35 }));
  const windowCool = material(new THREE.MeshStandardMaterial({ color: 0x7893a4, emissive: 0x8ec8e8, emissiveIntensity: 0.34, roughness: 0.32 }));
  const storefrontWarm = material(new THREE.MeshStandardMaterial({ color: 0x8d6949, emissive: 0xffb76d, emissiveIntensity: 0.84, roughness: 0.4 }));
  const storefrontCool = material(new THREE.MeshStandardMaterial({ color: 0x456472, emissive: 0x67b6d2, emissiveIntensity: 0.58, roughness: 0.38 }));
  const signalRed = material(new THREE.MeshStandardMaterial({ color: 0x7d1713, emissive: 0xff291d, emissiveIntensity: 1.6, roughness: 0.3 }));
  const signalAmber = material(new THREE.MeshStandardMaterial({ color: 0x7a5710, emissive: 0xffad27, emissiveIntensity: 0.42, roughness: 0.3 }));
  const signalGreen = material(new THREE.MeshStandardMaterial({ color: 0x0f5e3a, emissive: 0x2fe58e, emissiveIntensity: 0.34, roughness: 0.3 }));
  const lampMaterial = material(new THREE.MeshStandardMaterial({ color: 0xe6d1a7, emissive: 0xffd99a, emissiveIntensity: 2.0, roughness: 0.28 }));
  const redPaint = material(new THREE.MeshStandardMaterial({ color: 0x782e2a, roughness: 0.62, metalness: 0.12 }));
  const bluePaint = material(new THREE.MeshStandardMaterial({ color: 0x29465c, roughness: 0.58, metalness: 0.12 }));
  const creamPaint = material(new THREE.MeshStandardMaterial({ color: 0xb1a58d, roughness: 0.68, metalness: 0.08 }));
  const tire = material(new THREE.MeshStandardMaterial({ color: 0x0b0c0d, roughness: 0.88 }));
  const skin = material(new THREE.MeshStandardMaterial({ color: 0x9a705c, roughness: 0.82 }));
  const coat = material(new THREE.MeshStandardMaterial({ color: 0x303b48, roughness: 0.9 }));
  const coatWarm = material(new THREE.MeshStandardMaterial({ color: 0x68443a, roughness: 0.9 }));
  const trunk = material(new THREE.MeshStandardMaterial({ color: 0x3d3025, roughness: 0.98 }));
  const foliage = material(new THREE.MeshStandardMaterial({ color: 0x243b30, roughness: 0.96 }));

  const addBox = (
    name: string,
    size: [number, number, number],
    position: [number, number, number],
    meshMaterial: THREE.Material,
    parent: THREE.Object3D = root,
  ) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(size[0], size[1], size[2]), meshMaterial);
    mesh.name = name;
    mesh.position.set(position[0], position[1], position[2]);
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
    radialSegments = 12,
  ) => {
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, radialSegments), meshMaterial);
    mesh.name = name;
    mesh.position.set(position[0], position[1], position[2]);
    parent.add(mesh);
    return mesh;
  };

  scene.background = new THREE.Color(0x06090f);
  scene.fog = new THREE.FogExp2(0x080b10, 0.0062);

  const hemisphere = new THREE.HemisphereLight(0x6d7c9c, 0x17120d, 0.72);
  hemisphere.name = "night-sky-fill";
  root.add(hemisphere);

  const moon = new THREE.DirectionalLight(0x8ba4c5, 0.62);
  moon.name = "moon-key";
  moon.position.set(-45, 62, 24);
  root.add(moon);

  addBox("district-base", [150, 0.24, 150], [0, GROUND_Y - 0.16, -28], asphaltEdge);
  addBox("north-south-road", [18, 0.08, 150], [0, GROUND_Y, -28], asphalt);
  addBox("east-west-road", [150, 0.08, 18], [0, GROUND_Y + 0.01, -28], asphalt);

  const addSidewalk = (name: string, x: number, z: number, width: number, depth: number) => {
    addBox(name, [width, 0.28, depth], [x, GROUND_Y + 0.12, z], concrete);
  };

  addSidewalk("sidewalk-north-west", -12.5, -66, 7, 58);
  addSidewalk("sidewalk-north-east", 12.5, -66, 7, 58);
  addSidewalk("sidewalk-south-west", -12.5, 10, 7, 58);
  addSidewalk("sidewalk-south-east", 12.5, 10, 7, 58);
  addSidewalk("sidewalk-cross-north-west", -43, -39.5, 54, 7);
  addSidewalk("sidewalk-cross-north-east", 43, -39.5, 54, 7);
  addSidewalk("sidewalk-cross-south-west", -43, -16.5, 54, 7);
  addSidewalk("sidewalk-cross-south-east", 43, -16.5, 54, 7);

  for (const x of [-9.3, 9.3]) {
    addBox(`curb-ns-${x}`, [0.34, 0.36, 150], [x, GROUND_Y + 0.17, -28], curb);
  }
  for (const z of [-37.3, -18.7]) {
    addBox(`curb-ew-${z}`, [150, 0.36, 0.34], [0, GROUND_Y + 0.18, z], curb);
  }

  for (let i = 0; i < 8; i += 1) {
    const x = -7 + i * 2;
    addBox(`crosswalk-south-${i}`, [1.1, 0.025, 5.4], [x, GROUND_Y + 0.07, -17.1], roadPaint);
    addBox(`crosswalk-north-${i}`, [1.1, 0.025, 5.4], [x, GROUND_Y + 0.07, -38.9], roadPaint);
  }
  for (let i = 0; i < 8; i += 1) {
    const z = -35 + i * 2;
    addBox(`crosswalk-west-${i}`, [5.4, 0.025, 1.1], [-10.9, GROUND_Y + 0.075, z], roadPaint);
    addBox(`crosswalk-east-${i}`, [5.4, 0.025, 1.1], [10.9, GROUND_Y + 0.075, z], roadPaint);
  }

  for (const x of [-3.2, 3.2]) {
    for (let z = 34; z >= -92; z -= 13) {
      addBox(`lane-mark-${x}-${z}`, [0.16, 0.025, 5.6], [x, GROUND_Y + 0.07, z], roadPaint);
    }
  }
  for (const z of [-24.8, -31.2]) {
    for (let x = -66; x <= 66; x += 13) {
      addBox(`cross-lane-mark-${x}-${z}`, [5.6, 0.025, 0.16], [x, GROUND_Y + 0.075, z], roadPaint);
    }
  }

  const addFacadeWindows = (
    group: THREE.Group,
    options: BuildingOptions,
    face: "north" | "south" | "east" | "west",
  ) => {
    const verticalStart = GROUND_Y + 4.7;
    const floorStep = Math.max(2.7, (options.height - 5.2) / Math.max(1, options.floors - 1));
    const horizontalSpan = face === "north" || face === "south" ? options.width : options.depth;
    const columns = Math.max(3, Math.floor(horizontalSpan / 4.2));
    const spacing = horizontalSpan / columns;
    for (let floor = 0; floor < options.floors - 1; floor += 1) {
      const y = verticalStart + floor * floorStep;
      for (let column = 0; column < columns; column += 1) {
        const offset = -horizontalSpan / 2 + spacing * (column + 0.5);
        const litIndex = (floor * 7 + column * 3 + Math.round(options.x + options.z)) % 5;
        const mat = litIndex === 0 ? windowWarm : litIndex === 1 ? windowCool : windowDark;
        if (face === "north" || face === "south") {
          const z = face === "north" ? -options.depth / 2 - 0.035 : options.depth / 2 + 0.035;
          addBox(`window-${face}-${floor}-${column}`, [2.05, 1.45, 0.07], [offset, y - (GROUND_Y + options.height / 2), z], mat, group);
        } else {
          const x = face === "west" ? -options.width / 2 - 0.035 : options.width / 2 + 0.035;
          addBox(`window-${face}-${floor}-${column}`, [0.07, 1.45, 2.05], [x, y - (GROUND_Y + options.height / 2), offset], mat, group);
        }
      }
    }
  };

  const addStorefront = (group: THREE.Group, options: BuildingOptions, face: BuildingOptions["front"]) => {
    const panelMat = options.signColor === 0x65b8d5 ? storefrontCool : storefrontWarm;
    const signMat = material(new THREE.MeshStandardMaterial({
      color: options.signColor ?? 0xc58f4a,
      emissive: options.signColor ?? 0xffb45a,
      emissiveIntensity: 0.9,
      roughness: 0.34,
    }));
    const localY = GROUND_Y + 1.55 - (GROUND_Y + options.height / 2);
    const signY = GROUND_Y + 3.45 - (GROUND_Y + options.height / 2);
    if (face === "north" || face === "south") {
      const z = face === "north" ? -options.depth / 2 - 0.05 : options.depth / 2 + 0.05;
      addBox(`storefront-${face}`, [Math.min(options.width * 0.62, 15), 2.7, 0.1], [0, localY, z], panelMat, group);
      addBox(`storefront-sign-${face}`, [Math.min(options.width * 0.52, 12), 0.72, 0.14], [0, signY, z * 1.002], signMat, group);
      addBox(`awning-${face}`, [Math.min(options.width * 0.58, 13.5), 0.18, 1.25], [0, signY - 0.55, z + (face === "north" ? -0.56 : 0.56)], darkMetal, group);
    } else {
      const x = face === "west" ? -options.width / 2 - 0.05 : options.width / 2 + 0.05;
      addBox(`storefront-${face}`, [0.1, 2.7, Math.min(options.depth * 0.62, 15)], [x, localY, 0], panelMat, group);
      addBox(`storefront-sign-${face}`, [0.14, 0.72, Math.min(options.depth * 0.52, 12)], [x * 1.002, signY, 0], signMat, group);
      addBox(`awning-${face}`, [1.25, 0.18, Math.min(options.depth * 0.58, 13.5)], [x + (face === "west" ? -0.56 : 0.56), signY - 0.55, 0], darkMetal, group);
    }
  };

  const addBuilding = (name: string, options: BuildingOptions) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(options.x, GROUND_Y + options.height / 2, options.z);
    root.add(group);
    const facadeMaterial = material(new THREE.MeshStandardMaterial({ color: options.facade, roughness: 0.86, metalness: 0.03 }));
    const accentMaterial = material(new THREE.MeshStandardMaterial({ color: options.accent, roughness: 0.78, metalness: 0.06 }));
    addBox(`${name}-mass`, [options.width, options.height, options.depth], [0, 0, 0], facadeMaterial, group);
    addBox(`${name}-roof`, [options.width + 0.7, 0.46, options.depth + 0.7], [0, options.height / 2 + 0.23, 0], accentMaterial, group);
    addBox(`${name}-plinth`, [options.width + 0.24, 0.72, options.depth + 0.24], [0, -options.height / 2 + 0.36, 0], accentMaterial, group);
    addFacadeWindows(group, options, options.front);
    if (options.side) addFacadeWindows(group, options, options.side);
    addStorefront(group, options, options.front);
    return group;
  };

  addBuilding("north-west-block", {
    x: -34,
    z: -59,
    width: 34,
    depth: 34,
    height: 19,
    floors: 6,
    facade: 0x4a4540,
    accent: 0x27282a,
    front: "south",
    side: "east",
    signColor: 0xd28a48,
  });
  addBuilding("north-east-block", {
    x: 33,
    z: -61,
    width: 32,
    depth: 38,
    height: 27,
    floors: 8,
    facade: 0x3f454b,
    accent: 0x272c31,
    front: "south",
    side: "west",
    signColor: 0x65b8d5,
  });
  addBuilding("south-west-block", {
    x: -36,
    z: 8,
    width: 38,
    depth: 42,
    height: 15,
    floors: 5,
    facade: 0x544a42,
    accent: 0x302a27,
    front: "north",
    side: "east",
    signColor: 0xc98744,
  });
  addBuilding("south-east-block", {
    x: 36,
    z: 7,
    width: 38,
    depth: 40,
    height: 22,
    floors: 7,
    facade: 0x41484a,
    accent: 0x252b2d,
    front: "north",
    side: "west",
    signColor: 0x65b8d5,
  });

  addBuilding("far-north-left", {
    x: -31,
    z: -100,
    width: 34,
    depth: 24,
    height: 24,
    floors: 7,
    facade: 0x3d4044,
    accent: 0x24272b,
    front: "south",
  });
  addBuilding("far-north-right", {
    x: 33,
    z: -101,
    width: 34,
    depth: 24,
    height: 18,
    floors: 5,
    facade: 0x48433f,
    accent: 0x292826,
    front: "south",
  });

  const addStreetlight = (name: string, x: number, z: number, towardRoad: 1 | -1) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    root.add(group);
    addCylinder(`${name}-pole`, 0.12, 7.2, [0, 3.6, 0], darkMetal, group, 10);
    const arm = addCylinder(`${name}-arm`, 0.09, 2.2, [towardRoad * 0.95, 7.0, 0], darkMetal, group, 10);
    arm.rotation.z = Math.PI / 2;
    addBox(`${name}-lamp`, [0.78, 0.22, 0.42], [towardRoad * 1.88, 6.86, 0], lampMaterial, group);
    const point = new THREE.PointLight(0xffc77a, 8.5, 23, 2.0);
    point.name = `${name}-light`;
    point.position.set(towardRoad * 1.88, 6.62, 0);
    group.add(point);
  };

  addStreetlight("streetlight-sw", -13.5, -13.5, 1);
  addStreetlight("streetlight-se", 13.5, -13.5, -1);
  addStreetlight("streetlight-nw", -13.5, -42.5, 1);
  addStreetlight("streetlight-ne", 13.5, -42.5, -1);
  addStreetlight("streetlight-near-west", -13.5, 18, 1);
  addStreetlight("streetlight-far-east", 13.5, -72, -1);

  const addTrafficSignal = (name: string, x: number, z: number, rotationY = 0, active: "red" | "green" = "red") => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    group.rotation.y = rotationY;
    root.add(group);
    addCylinder(`${name}-pole`, 0.13, 4.4, [0, 2.2, 0], darkMetal, group, 10);
    addBox(`${name}-housing`, [0.58, 1.65, 0.5], [0, 4.15, 0], darkMetal, group);
    const signalMaterial = active === "red" ? signalRed : signalGreen;
    const darkA = active === "red" ? signalAmber : signalRed;
    const darkB = active === "red" ? signalGreen : signalAmber;
    for (const [index, mat] of [signalMaterial, darkA, darkB].entries()) {
      const lens = new THREE.Mesh(new THREE.SphereGeometry(0.15, 12, 8), mat);
      lens.name = `${name}-lens-${index}`;
      lens.position.set(0, 4.62 - index * 0.46, -0.27);
      lens.scale.z = 0.42;
      group.add(lens);
    }
  };

  addTrafficSignal("signal-south-west", -8.1, -18.2, 0, "red");
  addTrafficSignal("signal-south-east", 8.1, -18.2, 0, "green");
  addTrafficSignal("signal-north-west", -8.1, -37.8, Math.PI, "green");
  addTrafficSignal("signal-east", 9.1, -36.2, -Math.PI / 2, "red");

  const addCar = (name: string, x: number, z: number, rotationY: number, paint: THREE.Material, van = false) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    group.rotation.y = rotationY;
    root.add(group);
    const length = van ? 5.3 : 4.3;
    const height = van ? 1.55 : 0.72;
    addBox(`${name}-body`, [1.82, height, length], [0, 0.58 + height * 0.25, 0], paint, group);
    addBox(`${name}-cabin`, [1.58, van ? 1.35 : 0.82, van ? 2.4 : 2.05], [0, van ? 1.55 : 1.25, van ? 0.25 : -0.1], glass, group);
    addBox(`${name}-front-bumper`, [1.68, 0.18, 0.16], [0, 0.43, -length / 2 - 0.08], paleMetal, group);
    addBox(`${name}-rear-bumper`, [1.68, 0.18, 0.16], [0, 0.43, length / 2 + 0.08], paleMetal, group);
    for (const side of [-1, 1]) {
      for (const axle of [-1, 1]) {
        const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.36, 0.22, 14), tire);
        wheel.name = `${name}-wheel-${side}-${axle}`;
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(side * 0.94, 0.38, axle * (length * 0.31));
        group.add(wheel);
      }
    }
    for (const side of [-0.55, 0.55]) {
      addBox(`${name}-headlight-${side}`, [0.34, 0.2, 0.08], [side, 0.73, -length / 2 - 0.09], lampMaterial, group);
    }
    return group;
  };

  addCar("target-near-car", -4.3, -11.5, 0, redPaint);
  addCar("mid-blue-car", 4.4, -47, Math.PI, bluePaint);
  addCar("cross-street-van", 28, -32.5, Math.PI / 2, creamPaint, true);
  addCar("far-taxi", -4.2, -78, 0, creamPaint);

  const addPedestrian = (name: string, x: number, z: number, bodyMaterial: THREE.Material, scale = 1) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    group.scale.setScalar(scale);
    root.add(group);
    addCylinder(`${name}-torso`, 0.28, 1.05, [0, 1.18, 0], bodyMaterial, group, 10);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.23, 12, 8), skin);
    head.name = `${name}-head`;
    head.position.set(0, 1.93, 0);
    group.add(head);
    for (const side of [-1, 1]) {
      const leg = addCylinder(`${name}-leg-${side}`, 0.095, 0.9, [side * 0.13, 0.48, 0], darkMetal, group, 8);
      leg.rotation.z = side * 0.04;
      const arm = addCylinder(`${name}-arm-${side}`, 0.075, 0.82, [side * 0.36, 1.25, 0], bodyMaterial, group, 8);
      arm.rotation.z = side * 0.24;
    }
  };

  addPedestrian("target-mid-pedestrian", -10.8, -21.5, coatWarm, 1.0);
  addPedestrian("pedestrian-east", 11.8, -33.4, coat, 0.96);
  addPedestrian("pedestrian-far", -11.9, -61, coatWarm, 0.92);
  addPedestrian("pedestrian-near", 11.6, -8, coat, 1.02);

  const addBench = (name: string, x: number, z: number, rotationY: number) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    group.rotation.y = rotationY;
    root.add(group);
    addBox(`${name}-seat`, [2.3, 0.18, 0.62], [0, 0.58, 0], creamPaint, group);
    addBox(`${name}-back`, [2.3, 0.72, 0.16], [0, 0.95, 0.27], creamPaint, group);
    for (const xLeg of [-0.82, 0.82]) addBox(`${name}-leg-${xLeg}`, [0.12, 0.58, 0.46], [xLeg, 0.28, 0], darkMetal, group);
  };

  addBench("bench-west", -14.1, -8.5, Math.PI / 2);
  addBench("bench-east", 14.4, -50.5, -Math.PI / 2);
  addBox("utility-cabinet", [1.2, 1.55, 0.72], [-14.3, GROUND_Y + 0.78, -44.5], paleMetal);
  addCylinder("bin-east", 0.38, 1.05, [14.2, GROUND_Y + 0.52, -11], darkMetal, root, 12);
  for (const z of [-5, 3, 11]) addCylinder(`bollard-west-${z}`, 0.12, 0.86, [-9.8, GROUND_Y + 0.43, z], paleMetal, root, 10);

  const addTree = (name: string, x: number, z: number, height: number) => {
    const group = new THREE.Group();
    group.name = name;
    group.position.set(x, GROUND_Y, z);
    root.add(group);
    addCylinder(`${name}-trunk`, 0.28, height * 0.46, [0, height * 0.23, 0], trunk, group, 10);
    for (const [dx, dy, dz, scale] of [
      [0, height * 0.58, 0, 1.0],
      [-0.7, height * 0.68, 0.2, 0.72],
      [0.72, height * 0.65, -0.24, 0.78],
    ] as const) {
      const crown = new THREE.Mesh(new THREE.IcosahedronGeometry(1.65 * scale, 1), foliage);
      crown.name = `${name}-crown`;
      crown.position.set(dx, dy, dz);
      crown.scale.y = 1.25;
      group.add(crown);
    }
  };

  addTree("tree-south-west", -15, 17, 6.8);
  addTree("tree-south-east", 15.2, 21, 7.4);
  addTree("tree-north-west", -15.5, -69, 8.2);
  addTree("tree-north-east", 15.7, -75, 7.7);

  const addPole = (name: string, x: number, z: number, height: number) => {
    addCylinder(name, 0.16, height, [x, GROUND_Y + height / 2, z], darkMetal, root, 10);
  };
  addPole("wire-pole-west", -15.8, -54, 10.8);
  addPole("wire-pole-east", 15.8, -54, 10.8);
  addPole("wire-pole-far-west", -15.8, -88, 11.5);
  addPole("wire-pole-far-east", 15.8, -88, 11.5);

  const lineMaterial = material(new THREE.LineBasicMaterial({ color: 0x34383c }));
  const addWire = (name: string, points: THREE.Vector3[]) => {
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, lineMaterial);
    line.name = name;
    root.add(line);
  };
  addWire("wire-crossing-a", [new THREE.Vector3(-15.8, 8.5, -54), new THREE.Vector3(0, 8.1, -54), new THREE.Vector3(15.8, 8.5, -54)]);
  addWire("wire-crossing-b", [new THREE.Vector3(-15.8, 8.8, -88), new THREE.Vector3(0, 8.35, -88), new THREE.Vector3(15.8, 8.8, -88)]);
  addWire("wire-west-long", [new THREE.Vector3(-15.8, 8.5, -54), new THREE.Vector3(-15.8, 9.0, -71), new THREE.Vector3(-15.8, 9.2, -88)]);
  addWire("wire-east-long", [new THREE.Vector3(15.8, 8.5, -54), new THREE.Vector3(15.8, 9.0, -71), new THREE.Vector3(15.8, 9.2, -88)]);

  addBox("target-far-sign-post", [0.24, 4.8, 0.24], [7.1, GROUND_Y + 2.4, -90], paleMetal);
  addBox("target-far-sign", [4.8, 1.35, 0.18], [7.1, GROUND_Y + 4.4, -90], storefrontCool);
  addBox("target-rooftop-ledge", [8.0, 0.45, 1.2], [33, GROUND_Y + 27.4, -43], paleMetal);
  addCylinder("roof-antenna", 0.1, 7.0, [33, GROUND_Y + 30.8, -61], paleMetal, root, 8);

  const shopWest = new THREE.PointLight(0xff9f5a, 6.2, 18, 2.0);
  shopWest.name = "storefront-west-light";
  shopWest.position.set(-18, GROUND_Y + 3.1, -40);
  root.add(shopWest);
  const shopEast = new THREE.PointLight(0x79c9df, 5.2, 17, 2.0);
  shopEast.name = "storefront-east-light";
  shopEast.position.set(17, GROUND_Y + 3.2, -41);
  root.add(shopEast);

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
        if (object instanceof THREE.Line) object.geometry.dispose();
      });
      for (const item of materials) item.dispose();
      if (scene.fog instanceof THREE.FogExp2) scene.fog = null;
      if (scene.background instanceof THREE.Color) scene.background = null;
    },
  };
}
