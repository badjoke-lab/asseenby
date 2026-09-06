from pathlib import Path

path = Path("src/SpatialPage.tsx")
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label}")
    text = text.replace(old, new, 1)


replace_once(
    '<a href="/?view=spatial" aria-current="page">Explore 3D</a>',
    '<a href="/?view=spatial" aria-current="page">Explore spatial</a>',
    "top navigation label",
)

replace_once(
    'A controlled night-street scene provides bright lights, dark regions, near and far targets, signage, people, vehicles, and road markings for the spatial comparison pilot.',
    'A real 360° night-city panorama provides dense architecture, shopfronts, streetlights, dark sky, near and far detail, and high-contrast targets for the spatial comparison pilot.',
    "intro copy",
)

replace_once(
    '<strong>Comparison rule:</strong> switching the perception mode does not move the camera or alter the street scene. Tunnel Vision and Central Loss are generic field-loss models; Cataract-like is a generic scene-dependent glare and haze model. None are an individual\'s measured visual reconstruction.',
    '<strong>Comparison rule:</strong> switching the perception mode does not move the camera or alter the 360° photographic reference scene. Tunnel Vision and Central Loss are generic field-loss models; Cataract-like is a generic scene-dependent glare and haze model. None are an individual\'s measured visual reconstruction.',
    "comparison rule",
)

replace_once(
    '      scene.background = new THREE.Color(0x0b0f14);\n      scene.fog = new THREE.Fog(0x0b0f14, 22, 58);',
    '      scene.background = new THREE.Color(0x05070a);\n      scene.fog = null;',
    "scene baseline",
)

replace_once(
    '      camera.position.set(0, 1.65, 7.4);',
    '      camera.position.set(0, 0, 0);',
    "camera position",
)

replace_once(
    '      renderer.toneMapping = THREE.ACESFilmicToneMapping;\n      renderer.toneMappingExposure = 1.08;\n      renderer.shadowMap.enabled = true;\n      renderer.shadowMap.type = THREE.PCFSoftShadowMap;',
    '      renderer.toneMapping = THREE.NoToneMapping;\n      renderer.toneMappingExposure = 1.0;\n      renderer.shadowMap.enabled = false;',
    "renderer photo baseline",
)

replace_once(
    '      renderer.domElement.setAttribute("aria-label", "Controlled night street scene. Drag or use arrow keys to look around.");',
    '      renderer.domElement.setAttribute("aria-label", "360 degree photographic night-city reference scene. Drag or use arrow keys to look around.");',
    "canvas aria label",
)

replace_once(
    '''      createNightStreetScene(scene);\n      scene.traverse((object) => {\n        if (!(object instanceof THREE.Mesh)) return;\n        const material = object.material as THREE.Material | THREE.Material[];\n        const materials = Array.isArray(material) ? material : [material];\n        const isUnlitPlane = materials.some((item) => item instanceof THREE.MeshBasicMaterial);\n        object.castShadow = !isUnlitPlane;\n        object.receiveShadow = !isUnlitPlane;\n      });\n\n''',
    '',
    "remove primitive scene instantiation",
)

replace_once(
    '      loadPresentationBuildings(scene, renderScene);',
    '      loadPanoramaEnvironment(scene, renderScene);',
    "panorama loader call",
)

replace_once(
    '? "Live screen-relative central field loss. Center a pedestrian, sign, or light, then look elsewhere to see the disrupted region stay with straight-ahead vision."',
    '? "Live screen-relative central field loss. Center a shop sign, window, lamp, or other detail, then look elsewhere to see the disrupted region stay with straight-ahead vision."',
    "central loss mode copy",
)

replace_once(
    ': "Scene-aware haze, softness, lower contrast, warming, and bright-source glare. Turn toward headlights or streetlights, then toward a dark area to compare.";',
    ': "Scene-aware haze, softness, lower contrast, warming, and bright-source glare. Turn toward bright shopfronts or streetlights, then toward the dark sky to compare.";',
    "cataract mode copy",
)

replace_once(
    '<h2>3D preview unavailable</h2>',
    '<h2>Spatial preview unavailable</h2>',
    "error heading",
)

replace_once(
    '<section className="spatial-card" aria-label="Explore 3D pilot">',
    '<section className="spatial-card" aria-label="Explore spatial pilot">',
    "card aria label",
)

replace_once(
    '<div className="control-label">Explore 3D</div>\n          <h2>Controlled night-street scene</h2>',
    '<div className="control-label">Explore spatial</div>\n          <h2>360° photographic night-city scene</h2>',
    "card heading",
)

replace_once(
    '        Drag on the scene to look around. Mode switching keeps the same camera position and direction. Arrow keys work when the scene has keyboard focus.',
    '        Drag to look around the full 360° reference scene. Mode switching keeps the exact same viewpoint and direction. Arrow keys work when the scene has keyboard focus.',
    "caption copy",
)

panorama_fn = r'''function loadPanoramaEnvironment(scene: THREE.Scene, renderScene: () => void) {
  const loader = new THREE.TextureLoader();
  loader.load(
    "/assets/panoramas/hansaplatz.jpg",
    (texture) => {
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.mapping = THREE.EquirectangularReflectionMapping;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.magFilter = THREE.LinearFilter;
      scene.background = texture;
      renderScene();
    },
    undefined,
    (error) => {
      console.error("360° reference panorama failed to load", error);
    },
  );
}

'''
replace_once(
    'function loadPresentationBuildings(scene: THREE.Scene, renderScene: () => void) {',
    panorama_fn + 'function loadPresentationBuildings(scene: THREE.Scene, renderScene: () => void) {',
    "panorama function insertion",
)

replace_once(
    '''function disposeScene(scene: THREE.Scene | null, host: HTMLDivElement, renderer: THREE.WebGLRenderer | null) {\n  if (scene) {\n    scene.traverse((object) => {''',
    '''function disposeScene(scene: THREE.Scene | null, host: HTMLDivElement, renderer: THREE.WebGLRenderer | null) {\n  if (scene) {\n    if (scene.background instanceof THREE.Texture) scene.background.dispose();\n    scene.traverse((object) => {''',
    "panorama disposal",
)

path.write_text(text)
