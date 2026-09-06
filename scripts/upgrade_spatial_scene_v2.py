from pathlib import Path

path = Path("src/SpatialPage.tsx")
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label}")
    text = text.replace(old, new, 1)


replace_once(
    "  scene.background = new THREE.Color(0x071018);\n  scene.fog = new THREE.Fog(0x071018, 20, 72);\n\n  scene.add(new THREE.HemisphereLight(0x8299b5, 0x111315, 0.58));",
    "  scene.background = new THREE.Color(0x0a1420);\n  scene.fog = new THREE.Fog(0x0a1420, 22, 76);\n\n  scene.add(new THREE.HemisphereLight(0x8ba2bd, 0x171a1d, 0.7));\n  scene.add(new THREE.AmbientLight(0x2c3948, 0.18));",
    "night ambient lighting",
)

replace_once(
    "    new THREE.MeshStandardMaterial({ color: 0x25292d, roughness: 0.76, metalness: 0.08 }),",
    "    new THREE.MeshStandardMaterial({ color: 0x30343a, map: createAsphaltTexture(), roughness: 0.68, metalness: 0.12 }),",
    "asphalt material",
)

replace_once(
    "  const sidewalkMaterial = new THREE.MeshStandardMaterial({ color: 0x575650, roughness: 0.93 });",
    "  const sidewalkMaterial = new THREE.MeshStandardMaterial({ color: 0x6a6862, map: createConcreteTexture(), roughness: 0.88 });",
    "sidewalk material",
)

replace_once(
    "  const curbMaterial = new THREE.MeshStandardMaterial({ color: 0x77736b, roughness: 0.9 });",
    "  const curbMaterial = new THREE.MeshStandardMaterial({ color: 0x89847b, map: createConcreteTexture(), roughness: 0.86 });",
    "curb material",
)

replace_once(
    "  const buildingMaterial = new THREE.MeshStandardMaterial({ color: 0x34383d, roughness: 0.88 });\n  const darkBuildingMaterial = new THREE.MeshStandardMaterial({ color: 0x202429, roughness: 0.95 });\n  const brickMaterial = new THREE.MeshStandardMaterial({ color: 0x3a312e, roughness: 0.96 });",
    "  const buildingMaterial = new THREE.MeshStandardMaterial({ color: 0x4a4f54, map: createPlasterTexture(), roughness: 0.84 });\n  const darkBuildingMaterial = new THREE.MeshStandardMaterial({ color: 0x30363b, map: createPlasterTexture(), roughness: 0.92 });\n  const brickMaterial = new THREE.MeshStandardMaterial({ color: 0x55423a, map: createBrickTexture(), roughness: 0.9 });",
    "building surface materials",
)

replace_once(
    "  addBox(scene, [4.4, 7, -43], [6.5, 14, 8], buildingMaterial);\n\n  addFacadeDetail(scene);",
    "  addBox(scene, [4.4, 7, -43], [6.5, 14, 8], buildingMaterial);\n\n  addNearCornerArchitecture(scene);\n  addFacadeDetail(scene);",
    "near corner call",
)

near_corner = r'''function addNearCornerArchitecture(scene: THREE.Scene) {
  const leftWall = new THREE.MeshStandardMaterial({ color: 0x5a4a43, map: createBrickTexture(), roughness: 0.88 });
  const rightWall = new THREE.MeshStandardMaterial({ color: 0x4b5157, map: createPlasterTexture(), roughness: 0.84 });
  addBox(scene, [-5.4, 3.6, 4.0], [4.4, 7.2, 6.8], leftWall);
  addBox(scene, [5.4, 3.2, 4.0], [4.4, 6.4, 6.8], rightWall);

  const frame = new THREE.MeshStandardMaterial({ color: 0x272c30, roughness: 0.55, metalness: 0.28 });
  const glassDark = new THREE.MeshStandardMaterial({ color: 0x31404a, roughness: 0.16, metalness: 0.25 });
  const glassWarm = new THREE.MeshStandardMaterial({ color: 0x755c42, emissive: 0xa66d34, emissiveIntensity: 0.74, roughness: 0.24, metalness: 0.1 });
  const glassCool = new THREE.MeshStandardMaterial({ color: 0x3d5263, emissive: 0x496f8e, emissiveIntensity: 0.32, roughness: 0.24 });

  const addInnerWindow = (x: number, y: number, z: number, side: "left" | "right", variant: number) => {
    const material = variant === 0 ? glassDark : variant === 1 ? glassWarm : glassCool;
    addBox(scene, [x, y, z], [0.06, 0.92, 1.05], material);
    const trimX = side === "left" ? x + 0.04 : x - 0.04;
    addBox(scene, [trimX, y, z], [0.08, 0.07, 1.16], frame);
    addBox(scene, [trimX, y, z], [0.08, 1.03, 0.07], frame);
  };

  for (const z of [1.35, 3.2, 5.15, 6.45]) {
    addInnerWindow(-3.16, 2.25, z, "left", Math.abs(Math.round(z * 10)) % 3);
    addInnerWindow(-3.16, 4.05, z, "left", Math.abs(Math.round(z * 7 + 2)) % 3);
  }

  for (const z of [1.2, 3.1, 5.2, 6.5]) {
    addInnerWindow(3.16, 3.85, z, "right", Math.abs(Math.round(z * 8 + 1)) % 3);
    addInnerWindow(3.16, 5.05, z, "right", Math.abs(Math.round(z * 6 + 2)) % 3);
  }

  // Right-side corner shop, visible immediately when the viewer turns right.
  addBox(scene, [3.13, 1.35, 4.8], [0.08, 2.45, 3.25], new THREE.MeshStandardMaterial({ color: 0x6b563e, emissive: 0x8a5e31, emissiveIntensity: 0.78, roughness: 0.28 }));
  for (const z of [3.75, 4.8, 5.85]) {
    addBox(scene, [3.08, 1.34, z], [0.08, 2.25, 0.08], frame);
  }
  addBox(scene, [3.04, 2.48, 4.8], [0.12, 0.1, 3.35], frame);
  addBox(scene, [2.84, 2.82, 4.8], [0.52, 0.12, 3.7], new THREE.MeshStandardMaterial({ color: 0x6d3e35, roughness: 0.76 }));

  const shopTexture = createTextTexture("NIGHT MARKET", "#241b17", "#f1ca81");
  const shopSign = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 0.62), new THREE.MeshBasicMaterial({ map: shopTexture, toneMapped: false }));
  shopSign.rotation.y = -Math.PI / 2;
  shopSign.position.set(3.02, 3.1, 4.8);
  scene.add(shopSign);

  const rightDoor = new THREE.Mesh(new THREE.BoxGeometry(0.07, 2.1, 0.9), glassDark);
  rightDoor.position.set(3.05, 1.2, 2.1);
  scene.add(rightDoor);
  addBox(scene, [3.0, 1.2, 2.1], [0.08, 2.18, 0.08], frame);

  const shopLight = new THREE.PointLight(0xffba69, 18, 8, 2);
  shopLight.position.set(2.55, 2.25, 4.8);
  scene.add(shopLight);

  // Left-side apartment entrance and canopy.
  addBox(scene, [-3.13, 1.28, 5.2], [0.08, 2.35, 1.35], glassDark);
  addBox(scene, [-2.9, 2.6, 5.2], [0.55, 0.12, 1.65], frame);
  const entryTexture = createTextTexture("12", "#232629", "#d8cda8");
  const entrySign = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.44), new THREE.MeshBasicMaterial({ map: entryTexture, toneMapped: false }));
  entrySign.rotation.y = Math.PI / 2;
  entrySign.position.set(-3.03, 2.15, 4.25);
  scene.add(entrySign);

  // Bench and compact scooter shape provide close-range depth cues.
  const wood = new THREE.MeshStandardMaterial({ color: 0x604a37, roughness: 0.82 });
  addBox(scene, [-3.8, 0.52, 2.55], [1.35, 0.12, 0.42], wood);
  addBox(scene, [-3.8, 0.9, 2.78], [1.35, 0.62, 0.1], wood);
  addBox(scene, [-4.3, 0.28, 2.55], [0.1, 0.52, 0.1], frame);
  addBox(scene, [-3.3, 0.28, 2.55], [0.1, 0.52, 0.1], frame);

  const scooterBody = new THREE.MeshStandardMaterial({ color: 0x526776, roughness: 0.38, metalness: 0.32 });
  addBox(scene, [3.8, 0.44, 1.45], [0.38, 0.32, 1.05], scooterBody);
  const wheelMat = new THREE.MeshStandardMaterial({ color: 0x111315, roughness: 0.88 });
  for (const z of [1.05, 1.85]) {
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.1, 16), wheelMat);
    wheel.rotation.z = Math.PI / 2;
    wheel.position.set(3.8, 0.22, z);
    scene.add(wheel);
  }
  const handle = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.95, 8), frame);
  handle.position.set(3.8, 0.9, 1.15);
  handle.rotation.x = -0.25;
  scene.add(handle);
}

'''
replace_once(
    "function addFacadeDetail(scene: THREE.Scene) {",
    near_corner + "function addFacadeDetail(scene: THREE.Scene) {",
    "insert near corner architecture",
)

textures = r'''function createAsphaltTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  if (!context) return null;
  context.fillStyle = "#34383c";
  context.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 650; i += 1) {
    const seed = Math.sin(i * 91.73) * 43758.5453;
    const seed2 = Math.sin(i * 43.17 + 2.1) * 24634.6345;
    const x = Math.abs(seed % 1) * 256;
    const y = Math.abs(seed2 % 1) * 256;
    const tone = 42 + (i % 5) * 4;
    context.fillStyle = `rgb(${tone}, ${tone + 2}, ${tone + 4})`;
    context.fillRect(x, y, 1 + (i % 2), 1 + ((i + 1) % 2));
  }
  context.strokeStyle = "rgba(18, 21, 24, 0.5)";
  context.lineWidth = 1;
  context.beginPath();
  context.moveTo(12, 190);
  context.bezierCurveTo(72, 155, 110, 205, 166, 171);
  context.bezierCurveTo(203, 150, 224, 166, 252, 138);
  context.stroke();
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(3.5, 14);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createConcreteTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  if (!context) return null;
  context.fillStyle = "#8c8982";
  context.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 300; i += 1) {
    const x = Math.abs(Math.sin(i * 18.2) * 9973) % 256;
    const y = Math.abs(Math.sin(i * 37.7 + 1.4) * 7919) % 256;
    context.fillStyle = i % 3 === 0 ? "rgba(70,68,65,0.18)" : "rgba(210,207,198,0.12)";
    context.fillRect(x, y, 1.2, 1.2);
  }
  context.strokeStyle = "rgba(66,64,61,0.28)";
  context.lineWidth = 2;
  context.strokeRect(2, 2, 252, 252);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1.6, 10);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createBrickTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  if (!context) return null;
  context.fillStyle = "#695148";
  context.fillRect(0, 0, 256, 256);
  context.strokeStyle = "rgba(211,190,174,0.24)";
  context.lineWidth = 2;
  const rowHeight = 28;
  for (let y = 0; y <= 256; y += rowHeight) {
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(256, y);
    context.stroke();
    const offset = (Math.floor(y / rowHeight) % 2) * 32;
    for (let x = -64 + offset; x < 320; x += 64) {
      context.beginPath();
      context.moveTo(x, y);
      context.lineTo(x, y + rowHeight);
      context.stroke();
    }
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1.4, 2.8);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createPlasterTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const context = canvas.getContext("2d");
  if (!context) return null;
  context.fillStyle = "#72787c";
  context.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 420; i += 1) {
    const x = Math.abs(Math.sin(i * 13.11) * 3271) % 256;
    const y = Math.abs(Math.sin(i * 29.31 + 0.8) * 6143) % 256;
    context.fillStyle = i % 2 ? "rgba(32,37,41,0.08)" : "rgba(220,224,226,0.055)";
    context.fillRect(x, y, 2, 2);
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1.8, 2.6);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

'''
replace_once(
    "function createTextTexture(text: string",
    textures + "function createTextTexture(text: string",
    "insert generated surface textures",
)

path.write_text(text)
