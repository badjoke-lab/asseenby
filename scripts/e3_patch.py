from pathlib import Path
import re

# Night Intersection navigation/collision definition.
scene_path = Path('src/spatial/nightIntersectionScene.ts')
text = scene_path.read_text()
anchor = '''export type NightIntersectionSceneMount = {\n  root: THREE.Group;\n  objectCount: number;\n  lightCount: number;\n  dispose: () => void;\n};\n'''
insert = anchor + '''\ntype GroundCollisionRect = {\n  x: number;\n  z: number;\n  halfWidth: number;\n  halfDepth: number;\n};\n\nconst NIGHT_INTERSECTION_COLLISIONS: GroundCollisionRect[] = [\n  { x: -4.6, z: -11.5, halfWidth: 1.35, halfDepth: 2.7 },\n  { x: 4.5, z: -48, halfWidth: 1.35, halfDepth: 2.7 },\n  { x: 29, z: -32.5, halfWidth: 3.1, halfDepth: 1.35 },\n  { x: -4.3, z: -79, halfWidth: 1.35, halfDepth: 2.7 },\n  { x: 13.2, z: -61, halfWidth: 1.35, halfDepth: 2.7 },\n  { x: 14.4, z: -24.5, halfWidth: 2.65, halfDepth: 1.3 },\n  { x: -14.2, z: -8.3, halfWidth: 0.62, halfDepth: 1.45 },\n  { x: 14.4, z: -50.5, halfWidth: 0.62, halfDepth: 1.45 },\n  { x: -14.5, z: -44.5, halfWidth: 0.9, halfDepth: 0.65 },\n  { x: 14.2, z: -11, halfWidth: 0.72, halfDepth: 0.72 },\n  { x: -15.2, z: 17, halfWidth: 0.9, halfDepth: 0.9 },\n  { x: 15.4, z: 21, halfWidth: 0.9, halfDepth: 0.9 },\n  { x: -15.5, z: -69, halfWidth: 0.95, halfDepth: 0.95 },\n  { x: 15.7, z: -75, halfWidth: 0.95, halfDepth: 0.95 },\n  { x: -15.3, z: -49, halfWidth: 0.85, halfDepth: 0.85 },\n  { x: -8.4, z: -18.2, halfWidth: 0.48, halfDepth: 0.48 },\n  { x: 8.4, z: -18.2, halfWidth: 0.48, halfDepth: 0.48 },\n  { x: -8.4, z: -37.8, halfWidth: 0.48, halfDepth: 0.48 },\n  { x: 9.2, z: -36.2, halfWidth: 0.48, halfDepth: 0.48 },\n];\n\nconst insideRect = (x: number, z: number, radius: number, minX: number, maxX: number, minZ: number, maxZ: number) => (\n  x >= minX + radius && x <= maxX - radius && z >= minZ + radius && z <= maxZ - radius\n);\n\nexport const NIGHT_INTERSECTION_NAVIGATION = {\n  kind: 'ground' as const,\n  eyeY: 0,\n  radius: 0.36,\n  speed: 3.0,\n  fastSpeed: 5.2,\n  canOccupy(x: number, z: number, radius = 0.36) {\n    const inNorthSouth = insideRect(x, z, radius, -16.3, 16.3, -95, 35);\n    const inEastWest = insideRect(x, z, radius, -48, 48, -41.8, -14.2);\n    if (!inNorthSouth && !inEastWest) return false;\n    return !NIGHT_INTERSECTION_COLLISIONS.some((obstacle) => (\n      Math.abs(x - obstacle.x) < obstacle.halfWidth + radius\n      && Math.abs(z - obstacle.z) < obstacle.halfDepth + radius\n    ));\n  },\n};\n'''
if 'NIGHT_INTERSECTION_NAVIGATION' not in text:
    if anchor not in text:
        raise SystemExit('night scene type anchor missing')
    text = text.replace(anchor, insert, 1)
scene_path.write_text(text)

# Scene runtime now exposes navigation data for translating geometry scenes.
scene_runtime = Path('src/spatial/sceneRuntime.ts')
text = scene_runtime.read_text()
text = text.replace(
    'import { mountNightIntersectionScene } from "./nightIntersectionScene";',
    'import { mountNightIntersectionScene, NIGHT_INTERSECTION_NAVIGATION } from "./nightIntersectionScene";',
)
if 'export type SpatialGroundNavigation' not in text:
    text = text.replace(
        'export type SpatialSceneRuntime = {',
        '''export type SpatialGroundNavigation = {\n  kind: "ground";\n  eyeY: number;\n  radius: number;\n  speed: number;\n  fastSpeed: number;\n  canOccupy: (x: number, z: number, radius?: number) => boolean;\n};\n\nexport type SpatialSceneRuntime = {''',
        1,
    )
text = text.replace(
    '  lightCount: number;\n  dispose: () => void;',
    '  lightCount: number;\n  navigation: SpatialGroundNavigation | null;\n  dispose: () => void;',
    1,
)
text = text.replace(
    '      lightCount: mounted.lightCount,\n      dispose: mounted.dispose,',
    '      lightCount: mounted.lightCount,\n      navigation: NIGHT_INTERSECTION_NAVIGATION,\n      dispose: mounted.dispose,',
    1,
)
text = text.replace(
    '    lightCount: 0,\n    dispose: () => {',
    '    lightCount: 0,\n    navigation: null,\n    dispose: () => {',
    1,
)
scene_runtime.write_text(text)

# Replace observer runtime with E3 bounded Human ground controller.
observer = Path('src/spatial/observerRuntime.ts')
observer.write_text('''import * as THREE from "three";\nimport type { SpatialGuidedViewpoint, SpatialObserverId, SpatialViewpointState } from "./catalog";\nimport type { SpatialGroundNavigation } from "./sceneRuntime";\n\nexport type SpatialMoveDirection = "forward" | "back" | "left" | "right";\n\nexport type SpatialObserverSnapshot = {\n  id: SpatialObserverId;\n  yaw: number;\n  pitch: number;\n  fov: number;\n  position: [number, number, number];\n  viewpoint: SpatialViewpointState;\n};\n\nexport type SpatialObserverRuntime = {\n  id: SpatialObserverId;\n  readonly movement: "look-only" | "bounded-ground";\n  getSnapshot: () => SpatialObserverSnapshot;\n  setGuidedViewpoint: (viewpoint: SpatialGuidedViewpoint) => void;\n  setNavigation: (navigation: SpatialGroundNavigation | null) => void;\n  setMovementInput: (direction: SpatialMoveDirection, active: boolean) => void;\n  reset: () => void;\n  dispose: () => void;\n};\n\ntype ObserverRuntimeOptions = {\n  camera: THREE.PerspectiveCamera;\n  canvas: HTMLCanvasElement;\n  renderScene: () => void;\n  navigation: SpatialGroundNavigation | null;\n  onViewpointChange?: (viewpoint: SpatialViewpointState) => void;\n};\n\nconst GUIDED_VIEWPOINT_POSITIONS: Record<SpatialGuidedViewpoint, [number, number, number]> = {\n  baseline: [0, 0, 0],\n  offset: [3.2, 0, -4.2],\n};\n\nconst MOVE_KEYS = new Set(["w", "a", "s", "d", "shift"]);\n\nexport function createSpatialObserverRuntime(\n  observerId: SpatialObserverId,\n  { camera, canvas, renderScene, navigation: initialNavigation, onViewpointChange }: ObserverRuntimeOptions,\n): SpatialObserverRuntime {\n  if (observerId !== "human") {\n    throw new Error(`Unsupported Explore 3D observer: ${observerId}`);\n  }\n\n  let navigation = initialNavigation;\n  let yaw = 0;\n  let pitch = -0.01;\n  let activePointer: number | null = null;\n  let lastX = 0;\n  let lastY = 0;\n  let viewpoint: SpatialViewpointState = "baseline";\n  const keyboardMovement = new Set<string>();\n  const mobileMovement = new Set<SpatialMoveDirection>();\n  let movementFrame = 0;\n  let lastMovementTime = 0;\n\n  camera.position.set(...GUIDED_VIEWPOINT_POSITIONS.baseline);\n  camera.rotation.order = "YXZ";\n\n  const movementMode = () => navigation ? "bounded-ground" as const : "look-only" as const;\n\n  const updateAria = () => {\n    canvas.setAttribute(\n      "aria-label",\n      navigation\n        ? "Explore 3D. Human reference observer. Drag or use arrow keys to look around; use W A S D to move, Shift for faster movement, and R to reset."\n        : "Explore 3D. Human reference observer. Drag or use arrow keys to look around; press R to reset the current scene view.",\n    );\n  };\n\n  const syncCamera = () => {\n    camera.rotation.y = yaw;\n    camera.rotation.x = pitch;\n    canvas.dataset.observerId = observerId;\n    canvas.dataset.observerMovement = movementMode();\n    canvas.dataset.cameraViewpoint = viewpoint;\n    canvas.dataset.cameraYaw = yaw.toFixed(6);\n    canvas.dataset.cameraPitch = pitch.toFixed(6);\n    canvas.dataset.cameraFov = camera.fov.toFixed(3);\n    canvas.dataset.cameraPosition = `${camera.position.x.toFixed(3)},${camera.position.y.toFixed(3)},${camera.position.z.toFixed(3)}`;\n  };\n\n  const markFree = () => {\n    if (viewpoint === "free") return;\n    viewpoint = "free";\n    onViewpointChange?.("free");\n  };\n\n  const clearMovement = () => {\n    keyboardMovement.clear();\n    mobileMovement.clear();\n    lastMovementTime = 0;\n    if (movementFrame) cancelAnimationFrame(movementFrame);\n    movementFrame = 0;\n  };\n\n  const attemptMove = (dx: number, dz: number) => {\n    if (!navigation) return false;\n    let moved = false;\n    const nextX = camera.position.x + dx;\n    if (navigation.canOccupy(nextX, camera.position.z, navigation.radius)) {\n      camera.position.x = nextX;\n      moved = Math.abs(dx) > 0.000001;\n    }\n    const nextZ = camera.position.z + dz;\n    if (navigation.canOccupy(camera.position.x, nextZ, navigation.radius)) {\n      camera.position.z = nextZ;\n      moved = moved || Math.abs(dz) > 0.000001;\n    }\n    camera.position.y = navigation.eyeY;\n    if (moved) {\n      markFree();\n      syncCamera();\n      renderScene();\n    }\n    return moved;\n  };\n\n  const hasMovementInput = () => (\n    keyboardMovement.has("w") || keyboardMovement.has("a") || keyboardMovement.has("s") || keyboardMovement.has("d") || mobileMovement.size > 0\n  );\n\n  const movementTick = (time: number) => {\n    movementFrame = 0;\n    if (!navigation || !hasMovementInput()) {\n      lastMovementTime = 0;\n      return;\n    }\n    if (!lastMovementTime) lastMovementTime = time;\n    const dt = Math.min(0.12, Math.max(0, (time - lastMovementTime) / 1000));\n    lastMovementTime = time;\n\n    const forward = (keyboardMovement.has("w") || mobileMovement.has("forward") ? 1 : 0)\n      - (keyboardMovement.has("s") || mobileMovement.has("back") ? 1 : 0);\n    const strafe = (keyboardMovement.has("d") || mobileMovement.has("right") ? 1 : 0)\n      - (keyboardMovement.has("a") || mobileMovement.has("left") ? 1 : 0);\n    if (forward || strafe) {\n      const magnitude = Math.hypot(forward, strafe) || 1;\n      const normalizedForward = forward / magnitude;\n      const normalizedStrafe = strafe / magnitude;\n      const speed = keyboardMovement.has("shift") ? navigation.fastSpeed : navigation.speed;\n      const distance = speed * dt;\n      const sin = Math.sin(yaw);\n      const cos = Math.cos(yaw);\n      const dx = (-sin * normalizedForward + cos * normalizedStrafe) * distance;\n      const dz = (-cos * normalizedForward - sin * normalizedStrafe) * distance;\n      attemptMove(dx, dz);\n    }\n    if (hasMovementInput()) movementFrame = requestAnimationFrame(movementTick);\n  };\n\n  const ensureMovementFrame = () => {\n    if (!navigation || movementFrame || !hasMovementInput()) return;\n    lastMovementTime = 0;\n    movementFrame = requestAnimationFrame(movementTick);\n  };\n\n  const setGuidedViewpoint = (nextViewpoint: SpatialGuidedViewpoint) => {\n    clearMovement();\n    viewpoint = nextViewpoint;\n    const target = GUIDED_VIEWPOINT_POSITIONS[nextViewpoint];\n    camera.position.set(target[0], navigation?.eyeY ?? target[1], target[2]);\n    if (navigation && !navigation.canOccupy(camera.position.x, camera.position.z, navigation.radius)) {\n      camera.position.set(...GUIDED_VIEWPOINT_POSITIONS.baseline);\n      camera.position.y = navigation.eyeY;\n      viewpoint = "baseline";\n    }\n    onViewpointChange?.(viewpoint);\n    syncCamera();\n    renderScene();\n  };\n\n  const reset = () => {\n    clearMovement();\n    yaw = 0;\n    pitch = -0.01;\n    viewpoint = "baseline";\n    camera.position.set(...GUIDED_VIEWPOINT_POSITIONS.baseline);\n    if (navigation) camera.position.y = navigation.eyeY;\n    camera.fov = 52;\n    camera.updateProjectionMatrix();\n    onViewpointChange?.("baseline");\n    syncCamera();\n    renderScene();\n  };\n\n  const setNavigation = (nextNavigation: SpatialGroundNavigation | null) => {\n    navigation = nextNavigation;\n    updateAria();\n    reset();\n  };\n\n  const setMovementInput = (direction: SpatialMoveDirection, active: boolean) => {\n    if (!navigation) return;\n    if (active) mobileMovement.add(direction);\n    else mobileMovement.delete(direction);\n    if (active) ensureMovementFrame();\n    else if (!hasMovementInput()) lastMovementTime = 0;\n  };\n\n  const onPointerDown = (event: PointerEvent) => {\n    if (activePointer !== null) return;\n    activePointer = event.pointerId;\n    lastX = event.clientX;\n    lastY = event.clientY;\n    canvas.setPointerCapture(event.pointerId);\n    canvas.focus({ preventScroll: true });\n  };\n\n  const onPointerMove = (event: PointerEvent) => {\n    if (activePointer !== event.pointerId) return;\n    const dx = event.clientX - lastX;\n    const dy = event.clientY - lastY;\n    lastX = event.clientX;\n    lastY = event.clientY;\n    yaw -= dx * 0.0042;\n    pitch = THREE.MathUtils.clamp(pitch - dy * 0.0036, -1.08, 1.08);\n    syncCamera();\n    renderScene();\n  };\n\n  const stopPointer = (event: PointerEvent) => {\n    if (activePointer !== event.pointerId) return;\n    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);\n    activePointer = null;\n  };\n\n  const onKeyDown = (event: KeyboardEvent) => {\n    const key = event.key.toLowerCase();\n    if (navigation && MOVE_KEYS.has(key)) {\n      event.preventDefault();\n      keyboardMovement.add(key);\n      ensureMovementFrame();\n      return;\n    }\n    const step = event.shiftKey ? 0.14 : 0.07;\n    if (event.key === "ArrowLeft") yaw += step;\n    else if (event.key === "ArrowRight") yaw -= step;\n    else if (event.key === "ArrowUp") pitch = THREE.MathUtils.clamp(pitch + step, -1.08, 1.08);\n    else if (event.key === "ArrowDown") pitch = THREE.MathUtils.clamp(pitch - step, -1.08, 1.08);\n    else if (key === "r") {\n      event.preventDefault();\n      reset();\n      return;\n    } else return;\n    event.preventDefault();\n    syncCamera();\n    renderScene();\n  };\n\n  const onKeyUp = (event: KeyboardEvent) => {\n    const key = event.key.toLowerCase();\n    if (!MOVE_KEYS.has(key)) return;\n    keyboardMovement.delete(key);\n    if (!hasMovementInput()) lastMovementTime = 0;\n  };\n\n  const onBlur = () => {\n    keyboardMovement.clear();\n    if (!hasMovementInput()) lastMovementTime = 0;\n  };\n\n  canvas.addEventListener("pointerdown", onPointerDown);\n  canvas.addEventListener("pointermove", onPointerMove);\n  canvas.addEventListener("pointerup", stopPointer);\n  canvas.addEventListener("pointercancel", stopPointer);\n  canvas.addEventListener("keydown", onKeyDown);\n  canvas.addEventListener("keyup", onKeyUp);\n  canvas.addEventListener("blur", onBlur);\n  updateAria();\n  syncCamera();\n\n  return {\n    id: observerId,\n    get movement() {\n      return movementMode();\n    },\n    getSnapshot: () => ({\n      id: observerId,\n      yaw,\n      pitch,\n      fov: camera.fov,\n      position: [camera.position.x, camera.position.y, camera.position.z],\n      viewpoint,\n    }),\n    setGuidedViewpoint,\n    setNavigation,\n    setMovementInput,\n    reset,\n    dispose: () => {\n      clearMovement();\n      canvas.removeEventListener("pointerdown", onPointerDown);\n      canvas.removeEventListener("pointermove", onPointerMove);\n      canvas.removeEventListener("pointerup", stopPointer);\n      canvas.removeEventListener("pointercancel", stopPointer);\n      canvas.removeEventListener("keydown", onKeyDown);\n      canvas.removeEventListener("keyup", onKeyUp);\n      canvas.removeEventListener("blur", onBlur);\n    },\n  };\n}\n''')

# Catalog: free state and E3 copy.
catalog = Path('src/spatial/catalog.ts')
text = catalog.read_text()
text = text.replace(
    'description: "Human reference observer. Night Intersection currently offers authored comparison viewpoints; bounded free ground movement arrives in E3.",',
    'description: "Human reference observer. Night Intersection supports bounded ground movement with collision-aware navigation; the Photo Reference remains look-only.",',
)
if 'SpatialViewpointState' not in text:
    text = text.replace(
        'export type SpatialGuidedViewpoint = "baseline" | "offset";',
        'export type SpatialGuidedViewpoint = "baseline" | "offset";\nexport type SpatialViewpointState = SpatialGuidedViewpoint | "free";',
    )
catalog.write_text(text)

# SpatialPage controller and E3 UI.
page = Path('src/SpatialPage.tsx')
text = page.read_text()
text = text.replace(
    '  type SpatialVisionMode,\n} from "./spatial/catalog";',
    '  type SpatialVisionMode,\n  type SpatialViewpointState,\n} from "./spatial/catalog";',
)
text = text.replace(
    'import { createSpatialObserverRuntime, type SpatialObserverRuntime } from "./spatial/observerRuntime";',
    'import { createSpatialObserverRuntime, type SpatialMoveDirection, type SpatialObserverRuntime } from "./spatial/observerRuntime";',
)
text = text.replace(
    '  setViewpoint: (viewpoint: SpatialGuidedViewpoint) => void;\n  render: () => void;',
    '  setViewpoint: (viewpoint: SpatialGuidedViewpoint) => void;\n  setMovementInput: (direction: SpatialMoveDirection, active: boolean) => void;\n  resetObserver: () => void;\n  render: () => void;',
)
text = text.replace(
    '  const [viewpoint, setViewpoint] = useState<SpatialGuidedViewpoint>("baseline");',
    '  const [viewpoint, setViewpoint] = useState<SpatialViewpointState>("baseline");',
)
text = text.replace(
    '''  useEffect(() => {\n    controllerRef.current?.setViewpoint(viewpoint);\n  }, [viewpoint]);''',
    '''  useEffect(() => {\n    if (viewpoint !== "free") controllerRef.current?.setViewpoint(viewpoint);\n  }, [viewpoint]);''',
)
text = text.replace(
    '''        activeSceneRuntime = createSpatialSceneRuntime(nextSceneId, scene, renderScene);\n        canvas.dataset.sceneId = nextSceneId;''',
    '''        activeSceneRuntime = createSpatialSceneRuntime(nextSceneId, scene, renderScene);\n        activeObserverRuntime?.setNavigation(activeSceneRuntime.navigation);\n        canvas.dataset.sceneId = nextSceneId;''',
)
text = text.replace(
    '''        activeObserverRuntime?.dispose();\n        activeObserverRuntime = createSpatialObserverRuntime(nextObserverId, { camera, canvas, renderScene });\n        activeObserverRuntime.setGuidedViewpoint(viewpoint);''',
    '''        activeObserverRuntime?.dispose();\n        activeObserverRuntime = createSpatialObserverRuntime(nextObserverId, {\n          camera,\n          canvas,\n          renderScene,\n          navigation: activeSceneRuntime?.navigation ?? null,\n          onViewpointChange: setViewpoint,\n        });\n        activeObserverRuntime.setGuidedViewpoint(viewpoint === "free" ? "baseline" : viewpoint);''',
)
text = text.replace(
    '''        setVision: (nextVision) => visionRuntime?.setVision(nextVision),\n        setViewpoint: (nextViewpoint) => activeObserverRuntime?.setGuidedViewpoint(nextViewpoint),\n        render: renderScene,''',
    '''        setVision: (nextVision) => visionRuntime?.setVision(nextVision),\n        setViewpoint: (nextViewpoint) => activeObserverRuntime?.setGuidedViewpoint(nextViewpoint),\n        setMovementInput: (direction, active) => activeObserverRuntime?.setMovementInput(direction, active),\n        resetObserver: () => activeObserverRuntime?.reset(),\n        render: renderScene,''',
)
text = text.replace(
    '''                <strong>E2 geometry boundary:</strong> the two authored viewpoints change only camera position, making real parallax visible while direction and FOV stay unchanged. Bounded Human free movement and collision arrive in E3. Night Intersection intentionally exposes Normal only until the accepted Human Vision modes are integrated and reviewed for geometry in E4.''',
    '''                <strong>E3 movement boundary:</strong> the Human observer can move through the authored Night Intersection walking area with collision-aware ground navigation while keeping a 1.6 m reference eye height. This is a generic comparison viewpoint, not a claim about every person. Night Intersection intentionally exposes Normal only until Human Vision integration is reviewed in E4.''',
)
text = text.replace(
    '<p className="spatial-mode-availability">Geometry Vision integration is intentionally deferred to E4. E2 is judged in Normal.</p>',
    '<p className="spatial-mode-availability">Geometry Vision integration remains deferred to E4. E3 validates Human movement in Normal.</p>',
)
text = text.replace(
    '      <div ref={hostRef} className="spatial-render-host" />\n\n      {isGeometryScene ? (',
    '''      <div ref={hostRef} className="spatial-render-host" />\n\n      {isGeometryScene ? (\n        <div className="spatial-movement-section" aria-label="Human movement controls">\n          <div className="spatial-movement-copy">\n            <span className="control-label">Move</span>\n            <small>Desktop: W/A/S/D to walk, Shift for faster movement, drag or arrow keys to look, R to reset. Movement stays inside the authored walking area and avoids major obstacles.</small>\n          </div>\n          <div className="spatial-movement-actions">\n            <div className="spatial-move-pad" role="group" aria-label="Mobile movement">\n              {([\n                ["forward", "↑", "Move forward"],\n                ["left", "←", "Move left"],\n                ["back", "↓", "Move back"],\n                ["right", "→", "Move right"],\n              ] as Array<[SpatialMoveDirection, string, string]>).map(([direction, symbol, label]) => (\n                <button\n                  key={direction}\n                  type="button"\n                  className={`spatial-move-button spatial-move-button--${direction}`}\n                  aria-label={label}\n                  onPointerDown={(event) => {\n                    event.currentTarget.setPointerCapture(event.pointerId);\n                    controllerRef.current?.setMovementInput(direction, true);\n                  }}\n                  onPointerUp={() => controllerRef.current?.setMovementInput(direction, false)}\n                  onPointerCancel={() => controllerRef.current?.setMovementInput(direction, false)}\n                  onLostPointerCapture={() => controllerRef.current?.setMovementInput(direction, false)}\n                >\n                  {symbol}\n                </button>\n              ))}\n            </div>\n            <button\n              type="button"\n              className="spatial-reset-button"\n              onClick={() => controllerRef.current?.resetObserver()}\n            >\n              Reset observer\n            </button>\n          </div>\n        </div>\n      ) : null}\n\n      {isGeometryScene ? (''',
    1,
)
text = text.replace(
    '<small>Position changes; look direction and FOV stay fixed so nearby and distant geometry reveal parallax.</small>',
    '<small>These guided positions remain available alongside free movement. Selecting one changes position while preserving the current look direction and FOV.</small>',
)
text = text.replace(
    '''          ? "Night Intersection is a real geometry baseline. Switch Reference / Offset to compare parallax, drag or use arrow keys to look around, and press R to return to the canonical view. Bounded free ground movement is scheduled for E3."''',
    '''          ? "Night Intersection supports bounded Human ground movement. Walk with W/A/S/D on desktop or the compact mobile controls, use Shift for faster desktop movement, drag to look around, and use Reset observer or R to return to the canonical 1.6 m Human start."''',
)
page.write_text(text)

# E3 movement styling; mobile pad remains restrained and hidden on desktop.
css = Path('src/spatial.css')
text = css.read_text()
text = text.replace(
    '.spatial-mode-button,\n.spatial-viewpoint-button {',
    '.spatial-mode-button,\n.spatial-viewpoint-button,\n.spatial-reset-button,\n.spatial-move-button {',
)
text = text.replace(
    '.spatial-mode-button:focus-visible,\n.spatial-viewpoint-button:focus-visible {',
    '.spatial-mode-button:focus-visible,\n.spatial-viewpoint-button:focus-visible,\n.spatial-reset-button:focus-visible,\n.spatial-move-button:focus-visible {',
)
if '.spatial-movement-section {' not in text:
    marker = '\n@media (max-width: 760px) {'
    movement_css = '''\n.spatial-movement-section {\n  display: grid;\n  grid-template-columns: minmax(0, 1fr) auto;\n  align-items: center;\n  gap: 18px;\n  padding: 13px 16px;\n  border-top: 1px solid #d8d1c5;\n  background: #f4efe5;\n}\n\n.spatial-movement-copy {\n  display: grid;\n  gap: 4px;\n}\n\n.spatial-movement-copy small {\n  color: #6a645a;\n  line-height: 1.45;\n}\n\n.spatial-movement-actions {\n  display: flex;\n  align-items: center;\n  gap: 10px;\n}\n\n.spatial-reset-button {\n  white-space: nowrap;\n}\n\n.spatial-move-pad {\n  display: none;\n}\n\n.spatial-move-button {\n  min-width: 44px;\n  padding: 0;\n  border-radius: 8px;\n  font-size: 1.05rem;\n  line-height: 1;\n}\n'''
    if marker not in text:
        raise SystemExit('css media marker missing')
    text = text.replace(marker, movement_css + marker, 1)
text = text.replace(
    '''  .spatial-viewpoint-section {\n    grid-template-columns: 1fr;''',
    '''  .spatial-movement-section,\n  .spatial-viewpoint-section {\n    grid-template-columns: 1fr;''',
)
if '  .spatial-move-pad {' not in text:
    mobile_marker = '''  .spatial-viewpoint-buttons {\n    justify-content: stretch;\n  }\n'''
    mobile_css = '''  .spatial-movement-actions {\n    justify-content: space-between;\n    align-items: end;\n  }\n\n  .spatial-move-pad {\n    display: grid;\n    grid-template-columns: repeat(3, 44px);\n    grid-template-rows: repeat(2, 44px);\n    gap: 6px;\n  }\n\n  .spatial-move-button--forward { grid-column: 2; grid-row: 1; }\n  .spatial-move-button--left { grid-column: 1; grid-row: 2; }\n  .spatial-move-button--back { grid-column: 2; grid-row: 2; }\n  .spatial-move-button--right { grid-column: 3; grid-row: 2; }\n\n'''
    if mobile_marker not in text:
        raise SystemExit('mobile css marker missing')
    text = text.replace(mobile_marker, mobile_css + mobile_marker, 1)
css.write_text(text)

# Permanent production smoke: stale E2 cannot satisfy E3 movement fingerprint.
smoke = Path('.github/production-smoke.mjs')
text = smoke.read_text()
if 'e3HumanMovementDetected' not in text:
    text = text.replace(
        '  e2SpatialReleaseDetected: false,',
        '  e2SpatialReleaseDetected: false,\n  e3HumanMovementDetected: false,',
        1,
    )
text = text.replace('async function waitForExplore3DE2(page, label) {', 'async function waitForExplore3DE3(page, label) {')
text = text.replace('e2_release_smoke=', 'e3_release_smoke=')
text = text.replace(
    '        && canvas.dataset.sceneSupportsTranslation === "true"\n        && Number(canvas.dataset.sceneObjectCount || 0) >= 220',
    '        && canvas.dataset.sceneSupportsTranslation === "true"\n        && canvas.dataset.observerMovement === "bounded-ground"\n        && document.querySelector(\'.spatial-reset-button\') instanceof HTMLButtonElement\n        && Number(canvas.dataset.sceneObjectCount || 0) >= 220',
    1,
)
old_success = '''        result.e2SpatialReleaseDetected = true;\n        result.notes.push(`${label}: current E2 Night Intersection fingerprint detected on attempt ${attempt}`);\n        return;'''
new_success = '''        result.e2SpatialReleaseDetected = true;\n        const beforeMove = await canvas.evaluate((element) => element.dataset.cameraPosition);\n        await canvas.focus();\n        await page.keyboard.down("w");\n        await page.waitForTimeout(320);\n        await page.keyboard.up("w");\n        await page.waitForTimeout(120);\n        const moved = await canvas.evaluate((element) => ({\n          position: element.dataset.cameraPosition,\n          viewpoint: element.dataset.cameraViewpoint,\n          movement: element.dataset.observerMovement,\n        }));\n        assert(moved.position && moved.position !== beforeMove, `${label}: E3 W movement did not translate the Human observer`);\n        assert(moved.viewpoint === "free" && moved.movement === "bounded-ground", `${label}: E3 movement state is not free/bounded-ground`);\n        await page.getByRole("button", { name: "Reset observer", exact: true }).click();\n        await page.waitForTimeout(120);\n        const reset = await canvas.evaluate((element) => ({\n          position: element.dataset.cameraPosition,\n          yaw: element.dataset.cameraYaw,\n          pitch: element.dataset.cameraPitch,\n          fov: element.dataset.cameraFov,\n          viewpoint: element.dataset.cameraViewpoint,\n        }));\n        assert(reset.position === "0.000,0.000,0.000" && reset.viewpoint === "baseline", `${label}: E3 Reset did not restore canonical position`);\n        assert(reset.yaw === "0.000000" && reset.pitch === "-0.010000" && reset.fov === "52.000", `${label}: E3 Reset did not restore direction/FOV`);\n        result.e3HumanMovementDetected = true;\n        result.notes.push(`${label}: current E3 Human bounded-movement fingerprint detected on attempt ${attempt}`);\n        return;'''
if old_success in text:
    text = text.replace(old_success, new_success, 1)
text = text.replace('failed authored-translation fingerprint', 'failed E3 movement/translation fingerprint')
text = text.replace('did not reach Night Intersection geometry fingerprint', 'did not reach E3 Night Intersection movement fingerprint')
text = text.replace('current E2 Night Intersection release was not detected', 'current E3 Human bounded-movement release was not detected')
text = text.replace('await waitForExplore3DE2(page, "desktop spatial");', 'await waitForExplore3DE3(page, "desktop spatial");')
# Add explicit movement assertions in desktop smoke after E2 metadata check.
desktop_anchor = '''  assert(baseline.objectCount >= 220 && baseline.lightCount >= 10 && baseline.volume === "150x150x60", `desktop spatial: E2 density/volume regressed ${JSON.stringify(baseline)}`);\n'''
if 'desktop spatial: bounded Human movement is unavailable' not in text and desktop_anchor in text:
    text = text.replace(desktop_anchor, desktop_anchor + '''  assert((await canvas.getAttribute("data-observer-movement")) === "bounded-ground", "desktop spatial: bounded Human movement is unavailable");\n  assert((await page.getByRole("button", { name: "Reset observer", exact: true }).count()) === 1, "desktop spatial: Reset observer control is missing");\n''', 1)
# Mobile smoke: assert pad touch targets, move, reset before screenshot.
mobile_anchor = '''  assert(baseline.scene === "night-intersection" && baseline.objectCount >= 220 && baseline.lightCount >= 10, `mobile spatial: E2 geometry incomplete ${JSON.stringify(baseline)}`);\n'''
if 'mobile spatial movement pad' not in text and mobile_anchor in text:
    text = text.replace(mobile_anchor, mobile_anchor + '''  assert((await canvas.getAttribute("data-observer-movement")) === "bounded-ground", "mobile spatial: bounded Human movement is unavailable");\n  const mobileMoveButtons = page.getByRole("group", { name: "Mobile movement" }).getByRole("button");\n  await assertTouchTargets(mobileMoveButtons, "mobile spatial movement pad");\n  const beforeFreeMove = await canvas.getAttribute("data-camera-position");\n  const forwardButton = page.getByRole("button", { name: "Move forward", exact: true });\n  await forwardButton.dispatchEvent("pointerdown", { pointerId: 71, pointerType: "touch", isPrimary: true });\n  await page.waitForTimeout(320);\n  await forwardButton.dispatchEvent("pointerup", { pointerId: 71, pointerType: "touch", isPrimary: true });\n  await page.waitForTimeout(120);\n  const afterFreeMove = await canvas.getAttribute("data-camera-position");\n  assert(afterFreeMove && afterFreeMove !== beforeFreeMove, "mobile spatial: movement control did not translate observer");\n  assert((await canvas.getAttribute("data-camera-viewpoint")) === "free", "mobile spatial: movement did not mark viewpoint free");\n  await page.getByRole("button", { name: "Reset observer", exact: true }).click();\n  await page.waitForTimeout(120);\n  assert((await canvas.getAttribute("data-camera-position")) === "0.000,0.000,0.000", "mobile spatial: Reset observer did not restore canonical position");\n''', 1)
smoke.write_text(text)

# UI spec: canonical movement behavior supersedes the stale no-walking sentence.
ui = Path('docs/ui-spec.md')
text = ui.read_text()
text = text.replace(
    '''## Spatial interaction\nDesktop:\n- pointer drag to look around\n- keyboard look-around when the scene has focus\n- restrained zoom only if separately justified\n\nMobile:\n- touch drag to look around\n- controls remain reachable without covering most of the scene\n\nThe scene does not require free walking.''',
    '''## Spatial interaction\nGeometry scenes with an active ground observer:\n- desktop pointer drag / arrow keys: look around;\n- desktop W/A/S/D: bounded ground movement;\n- desktop Shift: moderately faster movement;\n- R / Reset observer: return to the canonical Scene × Observer start;\n- mobile touch drag: look around;\n- mobile uses a compact movement control that does not cover most of the viewport;\n- movement controls remain restrained and informational rather than becoming a game HUD.\n\n`360° Photo Reference` remains look-only because the photographic source has no translation depth. Collision/navigation bounds belong to geometry scenes and must prevent ground observers from leaving the useful authored area or passing through major obstacles.''',
)
ui.write_text(text)

# Limitations: distinguish E3 geometry movement from fixed Photo Reference.
limitations = Path('docs/limitations.md')
text = limitations.read_text()
old = '''### Current Explore 3D architecture boundary\nThe Scene / Observer / Vision split does not by itself create geometry, depth, parallax, collision, observer-height differences, climbing, or flight. The current public `360° Photo Reference` remains a fixed-position photographic source, so its Human observer supports look-around only. Features that require translation or physical observer differences remain unavailable until the scheduled geometry/observer phases are implemented and production-verified.\n\nDog-like remains available on the Photo Reference as a **Vision proxy** while the current Observer remains Human. That visual switch must not be read as a Dog-height camera or canine movement model. Cat and Bird observers are likewise not claimed until their movement/viewpoint phases exist; Bird flight and Bird spectral/color Vision remain separate requirements.'''
new = '''### Current Explore 3D architecture boundary\n`Night Intersection` is a geometry-based scene with real depth/parallax. Its Human observer uses a generic 1.6 m reference eye height and bounded collision-aware ground movement inside an authored walking area. That movement model is a geometric comparison tool, not a measurement of a particular person's body, gait, reach, mobility, or preferred walking speed. Full rigid-body physics is not implied.\n\n`360° Photo Reference` remains a fixed-position photographic source, so its Human observer supports look-around only and cannot provide real camera translation, collision, or parallax. Dog-like remains available there as a **Vision proxy** while the Observer remains Human; that visual switch must not be read as a Dog-height camera or canine movement model. Cat and Bird observers are likewise not claimed until their movement/viewpoint phases exist; Bird flight and Bird spectral/color Vision remain separate requirements.'''
if old in text:
    text = text.replace(old, new, 1)
limitations.write_text(text)

# Active schedule records implementation pending merged-production verification.
schedule = Path('docs/explore-3d-schedule.md')
text = schedule.read_text()
text = text.replace('Status: **E3 ACTIVE / Human observer and bounded movement**', 'Status: **E3 IMPLEMENTED / release verification pending**', 1)
text = text.replace('## Step E3 — Human observer and bounded movement\nStatus: **ACTIVE**', '## Step E3 — Human observer and bounded movement\nStatus: **IMPLEMENTED / release verification pending**', 1)
acceptance = '''Acceptance:\n- collision/navigation bounds prevent leaving the useful scene or walking through major geometry;\n- camera translation produces correct parallax;\n- Vision switching never moves the observer;\n- no game-loop mechanics are introduced.\n'''
if 'Implemented E3:' not in text and acceptance in text:
    text = text.replace(acceptance, acceptance + '''\nImplemented E3:\n- Night Intersection Human uses a 1.6 m reference eye height with yaw-relative W/A/S/D ground movement;\n- Shift provides a moderate desktop speed increase; R and the visible Reset observer control restore position, direction, FOV and movement state;\n- mobile exposes a compact four-direction movement pad plus the same Reset observer control;\n- navigation is constrained to an authored cross-shaped road/sidewalk area and rejects entry into listed major vehicle/street obstacles; axis-separated collision resolution allows sliding instead of requiring a physics engine;\n- free movement marks the camera viewpoint as `free`, so the guided Reference/Offset controls do not falsely remain selected;\n- `360° Photo Reference` remains look-only and receives no ground-movement controls;\n- Night Intersection still exposes Normal only; Human Vision integration remains E4.\n\nValidation requirement before merge:\n- build;\n- desktop keyboard movement / faster Shift movement / Reset / navigation bound checks;\n- mobile movement-pad touch targets / movement / Reset;\n- Photo Reference look-only regression;\n- full Compare image + Explore 3D production-smoke regression with an E3-specific stale-release fingerprint.\n''', 1)
schedule.write_text(text)
