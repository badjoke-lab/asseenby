from pathlib import Path

path = Path("src/SpatialPage.tsx")
text = path.read_text()


def replace_between(start: str, end: str, replacement: str) -> None:
    global text
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"missing start marker: {start}")
    b = text.find(end, a)
    if b < 0:
        raise SystemExit(f"missing end marker after {start}: {end}")
    text = text[:a] + replacement.rstrip() + "\n\n" + text[b:]


replace_between(
    "function createNightStreetScene(scene: THREE.Scene) {",
    "function addStorefront(scene: THREE.Scene) {",
    r'''function createNightStreetScene(scene: THREE.Scene) {
  scene.background = new THREE.Color(0x071018);
  scene.fog = new THREE.Fog(0x071018, 20, 72);

  scene.add(new THREE.HemisphereLight(0x8299b5, 0x111315, 0.58));

  const moonLight = new THREE.DirectionalLight(0xb7cce7, 0.82);
  moonLight.position.set(-7, 11, 5);
  scene.add(moonLight);

  const fillLight = new THREE.DirectionalLight(0x5a6e88, 0.2);
  fillLight.position.set(8, 5, -8);
  scene.add(fillLight);

  const road = new THREE.Mesh(
    new THREE.PlaneGeometry(12, 54),
    new THREE.MeshStandardMaterial({ color: 0x25292d, roughness: 0.76, metalness: 0.08 }),
  );
  road.rotation.x = -Math.PI / 2;
  road.position.set(0, 0, -15);
  scene.add(road);

  const sidewalkMaterial = new THREE.MeshStandardMaterial({ color: 0x575650, roughness: 0.93 });
  addBox(scene, [-4.5, 0.09, -15], [3, 0.18, 54], sidewalkMaterial);
  addBox(scene, [4.5, 0.09, -15], [3, 0.18, 54], sidewalkMaterial);

  const curbMaterial = new THREE.MeshStandardMaterial({ color: 0x77736b, roughness: 0.9 });
  addBox(scene, [-3.02, 0.16, -15], [0.12, 0.32, 54], curbMaterial);
  addBox(scene, [3.02, 0.16, -15], [0.12, 0.32, 54], curbMaterial);

  const laneMaterial = new THREE.MeshStandardMaterial({ color: 0xc8c1a9, roughness: 0.8 });
  for (let z = 2; z > -42; z -= 6) {
    addBox(scene, [0, 0.026, z], [0.11, 0.035, 2.1], laneMaterial);
  }

  const crosswalkMaterial = new THREE.MeshStandardMaterial({ color: 0xe0ddd2, roughness: 0.82 });
  for (let x = -2.5; x <= 2.5; x += 0.72) {
    addBox(scene, [x, 0.038, -2.2], [0.42, 0.05, 2.4], crosswalkMaterial);
  }

  const buildingMaterial = new THREE.MeshStandardMaterial({ color: 0x34383d, roughness: 0.88 });
  const darkBuildingMaterial = new THREE.MeshStandardMaterial({ color: 0x202429, roughness: 0.95 });
  const brickMaterial = new THREE.MeshStandardMaterial({ color: 0x3a312e, roughness: 0.96 });
  addBox(scene, [-5.3, 3.1, -7], [4.2, 6.2, 9], brickMaterial);
  addBox(scene, [5.4, 3.6, -10], [4.5, 7.2, 12], buildingMaterial);
  addBox(scene, [-5.4, 4.8, -20], [4.6, 9.6, 12], darkBuildingMaterial);
  addBox(scene, [5.7, 5.5, -25], [5.1, 11, 14], buildingMaterial);
  addBox(scene, [-1.5, 6, -40], [7, 12, 7], darkBuildingMaterial);
  addBox(scene, [4.4, 7, -43], [6.5, 14, 8], buildingMaterial);

  addFacadeDetail(scene);
  addStorefront(scene);
  addTrafficSignal(scene);
  addStreetlight(scene, -3.25, -1.2);
  addStreetlight(scene, 3.25, -15.8);
  addVehicle(scene);
  addParkedVehicle(scene);
  addPedestrian(scene);
  addRoadSign(scene);
  addStreetSurfaceDetail(scene);
  addStreetFurniture(scene);
  addOverheadUtilities(scene);
  addDistantStreetLayer(scene);
  addDarkSideRegion(scene);
}'''
)

replace_between(
    "function addStorefront(scene: THREE.Scene) {",
    "function addTrafficSignal(scene: THREE.Scene) {",
    r'''function addStorefront(scene: THREE.Scene) {
  const frame = new THREE.MeshStandardMaterial({ color: 0x403833, roughness: 0.82 });
  addBox(scene, [-4.02, 1.65, -3.8], [0.22, 3.1, 4.8], frame);

  const windowMaterial = new THREE.MeshStandardMaterial({
    color: 0x78684f,
    emissive: 0x9f713d,
    emissiveIntensity: 1.15,
    roughness: 0.36,
    metalness: 0.08,
  });
  addBox(scene, [-3.89, 1.32, -4.35], [0.08, 1.72, 1.55], windowMaterial);
  addBox(scene, [-3.89, 1.32, -2.72], [0.08, 1.72, 1.45], windowMaterial);

  const mullion = new THREE.MeshStandardMaterial({ color: 0x1f211f, roughness: 0.75, metalness: 0.22 });
  addBox(scene, [-3.82, 1.32, -3.55], [0.08, 1.9, 0.09], mullion);
  addBox(scene, [-3.82, 1.32, -4.35], [0.08, 0.08, 1.65], mullion);
  addBox(scene, [-3.82, 1.32, -2.72], [0.08, 0.08, 1.55], mullion);

  const door = new THREE.MeshStandardMaterial({ color: 0x20272b, roughness: 0.42, metalness: 0.18 });
  addBox(scene, [-3.86, 1.18, -1.55], [0.09, 2.1, 0.82], door);
  addBox(scene, [-3.79, 1.22, -1.55], [0.035, 1.55, 0.62], new THREE.MeshStandardMaterial({ color: 0x53626b, roughness: 0.22, metalness: 0.28 }));

  const awning = new THREE.MeshStandardMaterial({ color: 0x713d34, roughness: 0.8 });
  const canopy = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.12, 4.1), awning);
  canopy.position.set(-3.68, 2.75, -3.45);
  canopy.rotation.z = -0.14;
  scene.add(canopy);

  const signTexture = createTextTexture("LATE CAFE", "#231b17", "#f1c979");
  const signMaterial = new THREE.MeshBasicMaterial({ map: signTexture, toneMapped: false });
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 0.76), signMaterial);
  sign.rotation.y = Math.PI / 2;
  sign.position.set(-3.72, 3.25, -3.55);
  scene.add(sign);

  const openTexture = createTextTexture("OPEN", "#4a1d18", "#ffc993");
  const openSign = new THREE.Mesh(new THREE.PlaneGeometry(0.72, 0.32), new THREE.MeshBasicMaterial({ map: openTexture, toneMapped: false }));
  openSign.rotation.y = Math.PI / 2;
  openSign.position.set(-3.73, 1.45, -3.15);
  scene.add(openSign);

  const storeLight = new THREE.PointLight(0xffba68, 16, 9, 2);
  storeLight.position.set(-2.8, 2.35, -3.35);
  scene.add(storeLight);
}'''
)

replace_between(
    "function addTrafficSignal(scene: THREE.Scene) {",
    "function addSignalLens(scene: THREE.Scene",
    r'''function addTrafficSignal(scene: THREE.Scene) {
  const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x3c4248, roughness: 0.58, metalness: 0.46 });
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.11, 4.5, 12), poleMaterial);
  pole.position.set(2.9, 2.25, -4.2);
  scene.add(pole);

  addBox(scene, [2.9, 4.18, -4.2], [0.68, 1.5, 0.56], new THREE.MeshStandardMaterial({ color: 0x121619, roughness: 0.72, metalness: 0.18 }));
  addBox(scene, [2.9, 4.92, -4.2], [0.84, 0.12, 0.62], poleMaterial);
  addBox(scene, [2.9, 4.53, -3.84], [0.54, 0.09, 0.32], poleMaterial);
  addBox(scene, [2.9, 4.16, -3.84], [0.54, 0.09, 0.32], poleMaterial);
  addBox(scene, [2.9, 3.79, -3.84], [0.54, 0.09, 0.32], poleMaterial);

  addSignalLens(scene, [2.9, 4.55, -3.90], 0xff2c24, 4.8);
  addSignalLens(scene, [2.9, 4.18, -3.90], 0xd8aa2f, 0.32);
  addSignalLens(scene, [2.9, 3.81, -3.90], 0x4edb70, 2.3);
}

'''
)

replace_between(
    "function addStreetlight(scene: THREE.Scene, x: number, z: number) {",
    "function addVehicle(scene: THREE.Scene) {",
    r'''function addStreetlight(scene: THREE.Scene, x: number, z: number) {
  const poleMaterial = new THREE.MeshStandardMaterial({ color: 0x434a50, roughness: 0.52, metalness: 0.52 });
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.095, 4.7, 12), poleMaterial);
  pole.position.set(x, 2.35, z);
  scene.add(pole);

  addBox(scene, [x + 0.28, 4.57, z], [0.62, 0.075, 0.08], poleMaterial);
  const fixture = new THREE.Mesh(
    new THREE.CylinderGeometry(0.16, 0.23, 0.34, 12),
    new THREE.MeshStandardMaterial({ color: 0x30363b, roughness: 0.45, metalness: 0.5 }),
  );
  fixture.rotation.z = Math.PI / 2;
  fixture.position.set(x + 0.57, 4.5, z);
  scene.add(fixture);

  const lamp = new THREE.Mesh(
    new THREE.SphereGeometry(0.13, 16, 12),
    new THREE.MeshStandardMaterial({
      color: 0xffe0a1,
      emissive: 0xffc66f,
      emissiveIntensity: 8,
      roughness: 0.2,
    }),
  );
  lamp.scale.set(1.4, 0.55, 1.0);
  lamp.position.set(x + 0.62, 4.42, z);
  scene.add(lamp);

  const light = new THREE.PointLight(0xffcf85, 26, 14, 2);
  light.position.copy(lamp.position);
  scene.add(light);
}

'''
)

replace_between(
    "function addVehicle(scene: THREE.Scene) {",
    "function addPedestrian(scene: THREE.Scene) {",
    r'''function addVehicle(scene: THREE.Scene) {
  const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x405467, roughness: 0.34, metalness: 0.42 });
  const trimMaterial = new THREE.MeshStandardMaterial({ color: 0x161b1f, roughness: 0.48, metalness: 0.34 });
  const glassMaterial = new THREE.MeshStandardMaterial({ color: 0x506877, roughness: 0.18, metalness: 0.28 });

  addBox(scene, [1.25, 0.52, -8.2], [2.15, 0.62, 4.15], bodyMaterial);
  addBox(scene, [1.25, 0.83, -7.2], [2.02, 0.26, 1.25], bodyMaterial);
  addBox(scene, [1.25, 1.1, -8.55], [1.72, 0.72, 1.95], bodyMaterial);
  addBox(scene, [1.25, 1.24, -7.62], [1.52, 0.43, 0.06], glassMaterial);
  addBox(scene, [1.25, 1.25, -9.52], [1.48, 0.42, 0.06], glassMaterial);
  addBox(scene, [0.37, 0.54, -8.15], [0.08, 0.28, 3.35], trimMaterial);
  addBox(scene, [2.13, 0.54, -8.15], [0.08, 0.28, 3.35], trimMaterial);
  addBox(scene, [1.25, 0.34, -6.08], [1.95, 0.16, 0.18], trimMaterial);

  const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x111315, roughness: 0.85 });
  const rimMaterial = new THREE.MeshStandardMaterial({ color: 0x7a8084, roughness: 0.38, metalness: 0.65 });
  for (const x of [0.2, 2.3]) {
    for (const z of [-7.15, -9.35]) {
      const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.16, 18), wheelMaterial);
      wheel.rotation.z = Math.PI / 2;
      wheel.position.set(x, 0.31, z);
      scene.add(wheel);
      const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.17, 18), rimMaterial);
      rim.rotation.z = Math.PI / 2;
      rim.position.set(x, 0.31, z);
      scene.add(rim);
    }
  }

  const headlightMaterial = new THREE.MeshStandardMaterial({
    color: 0xfff4d7,
    emissive: 0xffe4a7,
    emissiveIntensity: 11,
    roughness: 0.14,
  });
  for (const x of [0.65, 1.85]) {
    addBox(scene, [x, 0.62, -6.10], [0.38, 0.19, 0.08], headlightMaterial);
    const light = new THREE.SpotLight(0xffe2aa, 45, 18, Math.PI / 7, 0.45, 1.3);
    light.position.set(x, 0.68, -6.0);
    light.target.position.set(x, 0.1, 3.5);
    scene.add(light, light.target);
  }
}

function addParkedVehicle(scene: THREE.Scene) {
  const body = new THREE.MeshStandardMaterial({ color: 0x4b403d, roughness: 0.45, metalness: 0.28 });
  const glass = new THREE.MeshStandardMaterial({ color: 0x27343d, roughness: 0.2, metalness: 0.25 });
  addBox(scene, [-4.1, 0.43, -12.8], [1.65, 0.55, 3.35], body);
  addBox(scene, [-4.1, 0.88, -13.1], [1.35, 0.6, 1.65], body);
  addBox(scene, [-4.1, 1.0, -12.28], [1.15, 0.35, 0.05], glass);
  const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x111315, roughness: 0.9 });
  for (const x of [-4.88, -3.32]) {
    for (const z of [-11.9, -13.75]) {
      const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.13, 16), wheelMaterial);
      wheel.rotation.z = Math.PI / 2;
      wheel.position.set(x, 0.27, z);
      scene.add(wheel);
    }
  }
}

'''
)

replace_between(
    "function addPedestrian(scene: THREE.Scene) {",
    "function addRoadSign(scene: THREE.Scene) {",
    r'''function addPedestrian(scene: THREE.Scene) {
  const coat = new THREE.MeshStandardMaterial({ color: 0xa9473f, roughness: 0.74 });
  const skin = new THREE.MeshStandardMaterial({ color: 0xb99179, roughness: 0.8 });
  const trouser = new THREE.MeshStandardMaterial({ color: 0x24292d, roughness: 0.88 });
  const shoe = new THREE.MeshStandardMaterial({ color: 0x111417, roughness: 0.92 });

  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.25, 0.68, 8, 14), coat);
  torso.position.set(-1.75, 1.08, -4.7);
  scene.add(torso);

  const shoulder = new THREE.Mesh(new THREE.BoxGeometry(0.68, 0.22, 0.3), coat);
  shoulder.position.set(-1.75, 1.38, -4.7);
  scene.add(shoulder);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.19, 18, 14), skin);
  head.position.set(-1.75, 1.78, -4.7);
  scene.add(head);

  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.195, 18, 10, 0, Math.PI * 2, 0, Math.PI * 0.5), new THREE.MeshStandardMaterial({ color: 0x2a211f, roughness: 0.9 }));
  hair.position.set(-1.75, 1.84, -4.7);
  scene.add(hair);

  addBox(scene, [-2.07, 1.03, -4.7], [0.13, 0.72, 0.16], coat);
  addBox(scene, [-1.43, 1.03, -4.7], [0.13, 0.72, 0.16], coat);
  addBox(scene, [-1.9, 0.42, -4.7], [0.18, 0.82, 0.2], trouser);
  addBox(scene, [-1.6, 0.42, -4.7], [0.18, 0.82, 0.2], trouser);
  addBox(scene, [-1.92, 0.08, -4.55], [0.26, 0.12, 0.42], shoe);
  addBox(scene, [-1.58, 0.08, -4.55], [0.26, 0.12, 0.42], shoe);
}

'''
)

replace_between(
    "function addDarkSideRegion(scene: THREE.Scene) {",
    "function createTextTexture(text: string",
    r'''function addDarkSideRegion(scene: THREE.Scene) {
  const wall = new THREE.MeshStandardMaterial({ color: 0x14191d, roughness: 0.98 });
  addBox(scene, [4.55, 1.6, -2.2], [2.7, 3.2, 3.2], wall);
  addBox(scene, [4.2, 0.7, -0.65], [2.1, 1.4, 0.12], new THREE.MeshStandardMaterial({ color: 0x20262a, roughness: 1 }));
  addBox(scene, [4.1, 1.62, -0.58], [1.3, 1.5, 0.05], new THREE.MeshStandardMaterial({ color: 0x27333a, roughness: 0.34, metalness: 0.2 }));
}

function addFacadeDetail(scene: THREE.Scene) {
  const darkWindow = new THREE.MeshStandardMaterial({ color: 0x18222a, roughness: 0.3, metalness: 0.14 });
  const warmWindow = new THREE.MeshStandardMaterial({ color: 0x775a3b, emissive: 0xa96f37, emissiveIntensity: 0.72, roughness: 0.38 });
  const coolWindow = new THREE.MeshStandardMaterial({ color: 0x344452, emissive: 0x425f7b, emissiveIntensity: 0.28, roughness: 0.35 });
  const sill = new THREE.MeshStandardMaterial({ color: 0x4c4d4d, roughness: 0.82 });

  const addFacadeWindow = (x: number, y: number, z: number, side: "left" | "right", lit: number) => {
    const material = lit === 1 ? warmWindow : lit === 2 ? coolWindow : darkWindow;
    if (side === "left") {
      addBox(scene, [x, y, z], [0.055, 0.74, 0.82], material);
      addBox(scene, [x + 0.035, y - 0.42, z], [0.08, 0.08, 0.92], sill);
    } else {
      addBox(scene, [x, y, z], [0.055, 0.74, 0.82], material);
      addBox(scene, [x - 0.035, y - 0.42, z], [0.08, 0.08, 0.92], sill);
    }
  };

  const leftX = -3.18;
  for (let y = 2.3; y <= 5.0; y += 1.3) {
    for (const z of [-7.9, -10.0, -15.8, -18.0, -21.0]) {
      addFacadeWindow(leftX, y, z, "left", (Math.round(y * 10 + z) % 3 + 3) % 3);
    }
  }

  const rightX = 3.18;
  for (let y = 2.4; y <= 6.2; y += 1.35) {
    for (const z of [-8.2, -10.4, -13.5, -18.8, -22.0, -26.2]) {
      addFacadeWindow(rightX, y, z, "right", (Math.round(y * 8 - z) % 3 + 3) % 3);
    }
  }

  const entryMaterial = new THREE.MeshStandardMaterial({ color: 0x1d252a, roughness: 0.42, metalness: 0.25 });
  addBox(scene, [3.16, 1.15, -10.7], [0.08, 2.15, 1.2], entryMaterial);
  addBox(scene, [3.12, 2.4, -10.7], [0.09, 0.22, 1.42], sill);
  addBox(scene, [-3.16, 1.1, -17.0], [0.08, 2.05, 1.15], entryMaterial);

  const verticalTrim = new THREE.MeshStandardMaterial({ color: 0x454849, roughness: 0.86 });
  for (const z of [-7.2, -12.0, -17.0, -22.0]) {
    addBox(scene, [-3.13, 3.2, z], [0.09, 5.7, 0.12], verticalTrim);
  }
  for (const z of [-9.0, -15.0, -21.5, -27.0]) {
    addBox(scene, [3.13, 3.4, z], [0.09, 6.0, 0.12], verticalTrim);
  }
}

function addStreetSurfaceDetail(scene: THREE.Scene) {
  const patchMaterial = new THREE.MeshStandardMaterial({ color: 0x30353a, roughness: 0.62, metalness: 0.12 });
  const wetMaterial = new THREE.MeshStandardMaterial({ color: 0x1e2429, roughness: 0.32, metalness: 0.22 });
  const grateMaterial = new THREE.MeshStandardMaterial({ color: 0x26292b, roughness: 0.55, metalness: 0.58 });

  addBox(scene, [-1.3, 0.02, -5.1], [1.2, 0.015, 2.7], patchMaterial);
  addBox(scene, [1.75, 0.018, -12.6], [1.65, 0.012, 3.4], wetMaterial);
  addBox(scene, [-0.65, 0.018, -20.5], [2.05, 0.012, 4.2], wetMaterial);

  const manhole = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.025, 28), grateMaterial);
  manhole.position.set(-1.45, 0.02, -10.6);
  scene.add(manhole);

  for (const z of [-4.8, -14.6, -24.2]) {
    addBox(scene, [-2.72, 0.065, z], [0.42, 0.05, 0.78], grateMaterial);
  }

  const seam = new THREE.MeshStandardMaterial({ color: 0x45433f, roughness: 0.92 });
  for (let z = 4; z > -38; z -= 2.4) {
    addBox(scene, [-4.48, 0.19, z], [2.75, 0.012, 0.028], seam);
    addBox(scene, [4.48, 0.19, z], [2.75, 0.012, 0.028], seam);
  }
}

function addStreetFurniture(scene: THREE.Scene) {
  const metal = new THREE.MeshStandardMaterial({ color: 0x3c4348, roughness: 0.58, metalness: 0.52 });
  const darkMetal = new THREE.MeshStandardMaterial({ color: 0x252c31, roughness: 0.72, metalness: 0.34 });
  const red = new THREE.MeshStandardMaterial({ color: 0x7a342f, roughness: 0.7 });

  for (const [x, z] of [[-3.38, 1.2], [-3.38, -0.2], [3.36, -5.5], [3.36, -7.0]] as Array<[number, number]>) {
    const bollard = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.11, 0.72, 12), metal);
    bollard.position.set(x, 0.45, z);
    scene.add(bollard);
  }

  addBox(scene, [4.1, 0.55, -7.2], [0.62, 1.05, 0.62], darkMetal);
  addBox(scene, [4.1, 1.12, -7.2], [0.7, 0.12, 0.68], metal);

  const hydrantBody = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.22, 0.62, 14), red);
  hydrantBody.position.set(-3.72, 0.42, -6.2);
  scene.add(hydrantBody);
  const hydrantCap = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.2, 0.18, 14), red);
  hydrantCap.position.set(-3.72, 0.82, -6.2);
  scene.add(hydrantCap);

  const planter = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.5, 0.5, 16), new THREE.MeshStandardMaterial({ color: 0x4a4740, roughness: 0.96 }));
  planter.position.set(3.95, 0.34, -12.2);
  scene.add(planter);
  const leaves = new THREE.Mesh(new THREE.SphereGeometry(0.52, 14, 10), new THREE.MeshStandardMaterial({ color: 0x334637, roughness: 0.9 }));
  leaves.scale.set(0.78, 1.15, 0.78);
  leaves.position.set(3.95, 1.0, -12.2);
  scene.add(leaves);
}

function addOverheadUtilities(scene: THREE.Scene) {
  const wireMaterial = new THREE.LineBasicMaterial({ color: 0x20262b });
  const makeWire = (points: Array<[number, number, number]>) => {
    const geometry = new THREE.BufferGeometry().setFromPoints(points.map(([x, y, z]) => new THREE.Vector3(x, y, z)));
    scene.add(new THREE.Line(geometry, wireMaterial));
  };

  makeWire([[-3.5, 5.0, -3], [0, 4.7, -8], [3.5, 5.2, -13]]);
  makeWire([[-3.4, 5.45, -10], [0.2, 5.15, -17], [3.6, 5.6, -23]]);
  makeWire([[-3.6, 6.0, -20], [-0.4, 5.72, -27], [3.7, 6.1, -34]]);
}

function addDistantStreetLayer(scene: THREE.Scene) {
  const distant = new THREE.MeshStandardMaterial({ color: 0x252b30, roughness: 0.94 });
  addBox(scene, [-5.8, 5.5, -50], [5.2, 11, 10], distant);
  addBox(scene, [0.2, 7.2, -53], [6.2, 14.4, 8], new THREE.MeshStandardMaterial({ color: 0x20262b, roughness: 0.96 }));
  addBox(scene, [5.5, 6.1, -49], [4.8, 12.2, 10], distant);

  const windowMat = new THREE.MeshStandardMaterial({ color: 0x6a563d, emissive: 0x8a6236, emissiveIntensity: 0.4, roughness: 0.4 });
  for (const x of [-2.4, -0.8, 0.8, 2.4]) {
    for (const y of [2.8, 4.4, 6.0, 7.6]) {
      addBox(scene, [x, y, -48.8], [0.7, 0.58, 0.05], ((Math.round(x * 10 + y * 10) % 3) === 0) ? windowMat : new THREE.MeshStandardMaterial({ color: 0x172027, roughness: 0.4 }));
    }
  }

  const distantLamp = new THREE.PointLight(0xffc477, 9, 12, 2);
  distantLamp.position.set(0.5, 4.3, -34);
  scene.add(distantLamp);
  addBox(scene, [0.5, 4.2, -34], [0.24, 0.15, 0.16], new THREE.MeshStandardMaterial({ color: 0xffd28a, emissive: 0xffbd63, emissiveIntensity: 5 }));
}

'''
)

path.write_text(text)
