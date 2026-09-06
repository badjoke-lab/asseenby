from pathlib import Path

path = Path("src/SpatialPage.tsx")
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label}")
    text = text.replace(old, new, 1)


def replace_between(start: str, end: str, replacement: str) -> None:
    global text
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"missing start marker: {start}")
    b = text.find(end, a)
    if b < 0:
        raise SystemExit(f"missing end marker: {end}")
    text = text[:a] + replacement.rstrip() + "\n\n" + text[b:]


replace_once(
    'import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";\nimport { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";',
    'import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";\nimport { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";\nimport { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";',
    "RoundedBoxGeometry import",
)

replace_once(
    '      renderer.toneMappingExposure = 1.05;\n      renderer.shadowMap.enabled = false;',
    '      renderer.toneMappingExposure = 1.08;\n      renderer.shadowMap.enabled = true;\n      renderer.shadowMap.type = THREE.PCFSoftShadowMap;',
    "renderer shadows",
)

replace_once(
    '      createNightStreetScene(scene);\n\n      composer = new EffectComposer(renderer);',
    '''      createNightStreetScene(scene);\n      scene.traverse((object) => {\n        if (!(object instanceof THREE.Mesh)) return;\n        const material = object.material as THREE.Material | THREE.Material[];\n        const materials = Array.isArray(material) ? material : [material];\n        const isUnlitPlane = materials.some((item) => item instanceof THREE.MeshBasicMaterial);\n        object.castShadow = !isUnlitPlane;\n        object.receiveShadow = !isUnlitPlane;\n      });\n\n      composer = new EffectComposer(renderer);''',
    "scene shadow flags",
)

replace_once(
    '  const moonLight = new THREE.DirectionalLight(0xb7cce7, 0.82);\n  moonLight.position.set(-7, 11, 5);\n  scene.add(moonLight);',
    '''  const moonLight = new THREE.DirectionalLight(0xb7cce7, 0.92);\n  moonLight.position.set(-7, 11, 5);\n  moonLight.castShadow = true;\n  moonLight.shadow.mapSize.set(1024, 1024);\n  moonLight.shadow.camera.near = 0.5;\n  moonLight.shadow.camera.far = 60;\n  moonLight.shadow.camera.left = -13;\n  moonLight.shadow.camera.right = 13;\n  moonLight.shadow.camera.top = 13;\n  moonLight.shadow.camera.bottom = -13;\n  moonLight.shadow.bias = -0.00035;\n  scene.add(moonLight);''',
    "moon shadow setup",
)

replace_once(
    '  addDarkSideRegion(scene);\n}',
    '  addDarkSideRegion(scene);\n  addNightSky(scene);\n}',
    "night sky call",
)

sky_fn = r'''function addNightSky(scene: THREE.Scene) {
  const geometry = new THREE.SphereGeometry(72, 32, 18);
  const material = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      topColor: { value: new THREE.Color(0x07111e) },
      horizonColor: { value: new THREE.Color(0x26394c) },
      glowColor: { value: new THREE.Color(0x6f5c4c) },
    },
    vertexShader: `
      varying vec3 vWorldPosition;
      void main() {
        vec4 worldPosition = modelMatrix * vec4(position, 1.0);
        vWorldPosition = worldPosition.xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 topColor;
      uniform vec3 horizonColor;
      uniform vec3 glowColor;
      varying vec3 vWorldPosition;
      void main() {
        float h = normalize(vWorldPosition).y;
        float horizon = 1.0 - smoothstep(-0.08, 0.46, h);
        vec3 color = mix(topColor, horizonColor, horizon * 0.72);
        color = mix(color, glowColor, pow(max(0.0, horizon), 3.0) * 0.08);
        gl_FragColor = vec4(color, 1.0);
      }
    `,
  });
  const sky = new THREE.Mesh(geometry, material);
  sky.position.set(0, 0, -12);
  sky.renderOrder = -10;
  scene.add(sky);
}

'''
replace_once(
    "function addStorefront(scene: THREE.Scene) {",
    sky_fn + "function addStorefront(scene: THREE.Scene) {",
    "insert night sky function",
)

replace_between(
    "function addVehicle(scene: THREE.Scene) {",
    "function addParkedVehicle(scene: THREE.Scene) {",
    r'''function addVehicle(scene: THREE.Scene) {
  const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x405467, roughness: 0.28, metalness: 0.5 });
  const trimMaterial = new THREE.MeshStandardMaterial({ color: 0x161b1f, roughness: 0.42, metalness: 0.4 });
  const glassMaterial = new THREE.MeshStandardMaterial({ color: 0x526b7a, roughness: 0.1, metalness: 0.38 });
  const chrome = new THREE.MeshStandardMaterial({ color: 0x9aa1a5, roughness: 0.24, metalness: 0.75 });

  addRoundedBox(scene, [1.25, 0.54, -8.2], [2.18, 0.66, 4.16], 0.12, bodyMaterial);
  const hood = addRoundedBox(scene, [1.25, 0.83, -7.12], [2.02, 0.28, 1.18], 0.1, bodyMaterial);
  hood.rotation.x = -0.035;
  const cabin = addRoundedBox(scene, [1.25, 1.12, -8.58], [1.72, 0.78, 1.98], 0.16, bodyMaterial);
  cabin.scale.x = 0.96;
  addBox(scene, [1.25, 1.29, -7.61], [1.48, 0.43, 0.055], glassMaterial);
  addBox(scene, [1.25, 1.3, -9.55], [1.46, 0.42, 0.055], glassMaterial);
  addBox(scene, [0.36, 0.55, -8.15], [0.07, 0.28, 3.2], trimMaterial);
  addBox(scene, [2.14, 0.55, -8.15], [0.07, 0.28, 3.2], trimMaterial);
  addRoundedBox(scene, [1.25, 0.35, -6.07], [1.98, 0.17, 0.2], 0.05, trimMaterial);
  addBox(scene, [1.25, 0.56, -6.035], [0.75, 0.06, 0.045], chrome);

  const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x0f1113, roughness: 0.82 });
  const rimMaterial = new THREE.MeshStandardMaterial({ color: 0x8a9195, roughness: 0.3, metalness: 0.72 });
  for (const x of [0.18, 2.32]) {
    for (const z of [-7.16, -9.32]) {
      const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.31, 0.31, 0.17, 24), wheelMaterial);
      wheel.rotation.z = Math.PI / 2;
      wheel.position.set(x, 0.31, z);
      scene.add(wheel);
      const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.18, 20), rimMaterial);
      rim.rotation.z = Math.PI / 2;
      rim.position.set(x, 0.31, z);
      scene.add(rim);
    }
  }

  const headlightMaterial = new THREE.MeshStandardMaterial({
    color: 0xfff4d7,
    emissive: 0xffe4a7,
    emissiveIntensity: 11,
    roughness: 0.1,
  });
  for (const x of [0.65, 1.85]) {
    addRoundedBox(scene, [x, 0.62, -6.105], [0.38, 0.19, 0.08], 0.035, headlightMaterial);
    const light = new THREE.SpotLight(0xffe2aa, 45, 18, Math.PI / 7, 0.45, 1.3);
    light.position.set(x, 0.68, -6.0);
    light.target.position.set(x, 0.1, 3.5);
    scene.add(light, light.target);
  }

  const tailMaterial = new THREE.MeshStandardMaterial({ color: 0x601c1a, emissive: 0xc52d27, emissiveIntensity: 0.55, roughness: 0.22 });
  for (const x of [0.55, 1.95]) {
    addRoundedBox(scene, [x, 0.59, -10.29], [0.38, 0.15, 0.07], 0.03, tailMaterial);
  }
}

'''
)

replace_between(
    "function addPedestrian(scene: THREE.Scene) {",
    "function addRoadSign(scene: THREE.Scene) {",
    r'''function addPedestrian(scene: THREE.Scene) {
  const coat = new THREE.MeshStandardMaterial({ color: 0xa9473f, roughness: 0.64 });
  const skin = new THREE.MeshStandardMaterial({ color: 0xb99179, roughness: 0.72 });
  const trouser = new THREE.MeshStandardMaterial({ color: 0x24292d, roughness: 0.82 });
  const shoe = new THREE.MeshStandardMaterial({ color: 0x111417, roughness: 0.88 });

  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.25, 0.68, 10, 18), coat);
  torso.position.set(-1.75, 1.08, -4.7);
  scene.add(torso);

  const shoulder = new THREE.Mesh(new THREE.CapsuleGeometry(0.13, 0.42, 8, 14), coat);
  shoulder.rotation.z = Math.PI / 2;
  shoulder.position.set(-1.75, 1.4, -4.7);
  scene.add(shoulder);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.19, 22, 16), skin);
  head.position.set(-1.75, 1.78, -4.7);
  scene.add(head);

  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.197, 20, 12, 0, Math.PI * 2, 0, Math.PI * 0.52), new THREE.MeshStandardMaterial({ color: 0x2a211f, roughness: 0.84 }));
  hair.position.set(-1.75, 1.84, -4.7);
  scene.add(hair);

  const addLimb = (x: number, y: number, material: THREE.Material, length: number, radius: number, tilt: number) => {
    const limb = new THREE.Mesh(new THREE.CapsuleGeometry(radius, length, 8, 14), material);
    limb.position.set(x, y, -4.7);
    limb.rotation.z = tilt;
    scene.add(limb);
  };

  addLimb(-2.03, 1.04, coat, 0.43, 0.075, 0.08);
  addLimb(-1.47, 1.04, coat, 0.43, 0.075, -0.08);
  addLimb(-1.9, 0.43, trouser, 0.52, 0.09, 0.035);
  addLimb(-1.6, 0.43, trouser, 0.52, 0.09, -0.035);
  addRoundedBox(scene, [-1.93, 0.08, -4.55], [0.27, 0.12, 0.43], 0.04, shoe);
  addRoundedBox(scene, [-1.57, 0.08, -4.55], [0.27, 0.12, 0.43], 0.04, shoe);
}

'''
)

rounded_helper = r'''function addRoundedBox(
  scene: THREE.Scene,
  position: [number, number, number],
  size: [number, number, number],
  radius: number,
  material: THREE.Material,
) {
  const [width, height, depth] = size;
  const safeRadius = Math.min(radius, width * 0.24, height * 0.24, depth * 0.24);
  const mesh = new THREE.Mesh(new RoundedBoxGeometry(width, height, depth, 4, safeRadius), material);
  mesh.position.set(...position);
  scene.add(mesh);
  return mesh;
}

'''
replace_once(
    "function addBox(\n",
    rounded_helper + "function addBox(\n",
    "rounded box helper",
)

path.write_text(text)
