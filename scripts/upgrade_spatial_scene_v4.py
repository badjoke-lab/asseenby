from pathlib import Path

path = Path("src/SpatialPage.tsx")
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label}")
    text = text.replace(old, new, 1)


replace_once(
    'import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";',
    'import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";\nimport { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";\nimport { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";',
    "GLTF loader imports",
)

replace_once(
    '''      const renderScene = () => {\n        composer?.render();\n      };\n\n      const applyMode = (nextMode: SpatialMode) => {''',
    '''      const renderScene = () => {\n        composer?.render();\n      };\n\n      loadPresentationBuildings(scene, renderScene);\n\n      const applyMode = (nextMode: SpatialMode) => {''',
    "load presentation buildings",
)

loader_fn = r'''function loadPresentationBuildings(scene: THREE.Scene, renderScene: () => void) {
  const loader = new GLTFLoader();
  loader.setMeshoptDecoder(MeshoptDecoder);

  const placements = [
    { url: "/assets/models/downtown-small.glb", position: [-5.35, 0, -14.5] as [number, number, number], height: 8.6, rotationY: Math.PI / 2 },
    { url: "/assets/models/downtown-medium.glb", position: [5.3, 0, -21.5] as [number, number, number], height: 11.8, rotationY: -Math.PI / 2 },
    { url: "/assets/models/downtown-large.glb", position: [-4.8, 0, -36.0] as [number, number, number], height: 15.2, rotationY: Math.PI / 2 },
  ];

  for (const placement of placements) {
    loader.load(
      placement.url,
      (gltf) => {
        const model = gltf.scene;
        const sourceBox = new THREE.Box3().setFromObject(model);
        const sourceSize = sourceBox.getSize(new THREE.Vector3());
        if (!Number.isFinite(sourceSize.y) || sourceSize.y <= 0) return;

        const scale = placement.height / sourceSize.y;
        const center = sourceBox.getCenter(new THREE.Vector3());
        model.scale.setScalar(scale);
        model.position.set(-center.x * scale, -sourceBox.min.y * scale, -center.z * scale);

        model.traverse((object) => {
          if (!(object instanceof THREE.Mesh)) return;
          object.castShadow = true;
          object.receiveShadow = true;
          const materials = Array.isArray(object.material) ? object.material : [object.material];
          for (const material of materials) {
            if (material instanceof THREE.MeshStandardMaterial) {
              material.roughness = Math.max(0.3, Math.min(0.9, material.roughness));
              material.needsUpdate = true;
            }
          }
        });

        const wrapper = new THREE.Group();
        wrapper.position.set(...placement.position);
        wrapper.rotation.y = placement.rotationY;
        wrapper.add(model);
        scene.add(wrapper);
        renderScene();
      },
      undefined,
      (error) => {
        console.warn(`Optional presentation asset failed to load: ${placement.url}`, error);
      },
    );
  }
}

'''
replace_once(
    "function createNightStreetScene(scene: THREE.Scene) {",
    loader_fn + "function createNightStreetScene(scene: THREE.Scene) {",
    "presentation loader function",
)

path.write_text(text)
