import * as THREE from "three";
import type { SpatialGuidedViewpoint, SpatialObserverId, SpatialViewpointState } from "./catalog";
import type { SpatialGroundNavigation } from "./sceneRuntime";

export type SpatialMoveDirection = "forward" | "back" | "left" | "right";

export type SpatialObserverSnapshot = {
  id: SpatialObserverId;
  yaw: number;
  pitch: number;
  fov: number;
  position: [number, number, number];
  viewpoint: SpatialViewpointState;
};

export type SpatialObserverRuntime = {
  id: SpatialObserverId;
  readonly movement: "look-only" | "bounded-ground";
  getSnapshot: () => SpatialObserverSnapshot;
  setGuidedViewpoint: (viewpoint: SpatialGuidedViewpoint) => void;
  setNavigation: (navigation: SpatialGroundNavigation | null) => void;
  setMovementInput: (direction: SpatialMoveDirection, active: boolean) => void;
  reset: () => void;
  dispose: () => void;
};

type ObserverRuntimeOptions = {
  camera: THREE.PerspectiveCamera;
  canvas: HTMLCanvasElement;
  renderScene: () => void;
  navigation: SpatialGroundNavigation | null;
  onViewpointChange?: (viewpoint: SpatialViewpointState) => void;
  onPositionChange?: (position: THREE.Vector3) => void;
};

const GUIDED_VIEWPOINT_OFFSETS: Record<SpatialGuidedViewpoint, [number, number, number]> = {
  baseline: [0, 0, 0],
  offset: [3.2, 0, -4.2],
};

const MOVE_KEYS = new Set(["w", "a", "s", "d", "shift"]);

const guidedPosition = (
  guidedViewpoint: SpatialGuidedViewpoint,
  navigation: SpatialGroundNavigation | null,
): [number, number, number] => {
  const offset = GUIDED_VIEWPOINT_OFFSETS[guidedViewpoint];
  const [baseX, baseZ] = navigation?.initialPosition ?? [0, 0];
  return [baseX + offset[0], navigation?.eyeY ?? offset[1], baseZ + offset[2]];
};

export function createSpatialObserverRuntime(
  observerId: SpatialObserverId,
  { camera, canvas, renderScene, navigation: initialNavigation, onViewpointChange, onPositionChange }: ObserverRuntimeOptions,
): SpatialObserverRuntime {
  if (observerId !== "human") {
    throw new Error(`Unsupported Explore 3D observer: ${observerId}`);
  }

  let navigation = initialNavigation;
  let yaw = navigation?.initialYaw ?? 0;
  let pitch = -0.01;
  let activePointer: number | null = null;
  let lastX = 0;
  let lastY = 0;
  let viewpoint: SpatialViewpointState = "baseline";
  const keyboardMovement = new Set<string>();
  const mobileMovement = new Set<SpatialMoveDirection>();
  let movementFrame = 0;
  let lastMovementTime = 0;

  camera.position.set(...guidedPosition("baseline", navigation));
  camera.rotation.order = "YXZ";

  const movementMode = () => navigation ? "bounded-ground" as const : "look-only" as const;

  const updateAria = () => {
    canvas.setAttribute(
      "aria-label",
      navigation
        ? "Explore 3D. Human reference observer. Drag or use arrow keys to look around; use W A S D to move, Shift for faster movement, and R to reset."
        : "Explore 3D. Human reference observer. Drag or use arrow keys to look around; press R to reset the current scene view.",
    );
  };

  const syncCamera = () => {
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;
    canvas.dataset.observerId = observerId;
    canvas.dataset.observerMovement = movementMode();
    canvas.dataset.cameraViewpoint = viewpoint;
    canvas.dataset.cameraYaw = yaw.toFixed(6);
    canvas.dataset.cameraPitch = pitch.toFixed(6);
    canvas.dataset.cameraFov = camera.fov.toFixed(3);
    canvas.dataset.cameraPosition = `${camera.position.x.toFixed(3)},${camera.position.y.toFixed(3)},${camera.position.z.toFixed(3)}`;
    onPositionChange?.(camera.position);
  };

  const markFree = () => {
    if (viewpoint === "free") return;
    viewpoint = "free";
    onViewpointChange?.("free");
  };

  const clearMovement = () => {
    keyboardMovement.clear();
    mobileMovement.clear();
    lastMovementTime = 0;
    if (movementFrame) cancelAnimationFrame(movementFrame);
    movementFrame = 0;
  };

  const attemptMove = (dx: number, dz: number) => {
    if (!navigation) return false;
    const maxComponent = Math.max(Math.abs(dx), Math.abs(dz));
    const steps = Math.max(1, Math.ceil(maxComponent / 0.22));
    const stepX = dx / steps;
    const stepZ = dz / steps;
    let moved = false;
    for (let index = 0; index < steps; index += 1) {
      const nextX = camera.position.x + stepX;
      if (navigation.canOccupy(nextX, camera.position.z, navigation.radius)) {
        camera.position.x = nextX;
        moved = moved || Math.abs(stepX) > 0.000001;
      }
      const nextZ = camera.position.z + stepZ;
      if (navigation.canOccupy(camera.position.x, nextZ, navigation.radius)) {
        camera.position.z = nextZ;
        moved = moved || Math.abs(stepZ) > 0.000001;
      }
    }
    camera.position.y = navigation.eyeY;
    if (moved) {
      markFree();
      syncCamera();
      renderScene();
    }
    return moved;
  };

  const hasMovementInput = () => (
    keyboardMovement.has("w") || keyboardMovement.has("a") || keyboardMovement.has("s") || keyboardMovement.has("d") || mobileMovement.size > 0
  );

  const advanceMovement = (time: number) => {
    if (!navigation || !hasMovementInput()) return;
    if (!lastMovementTime) lastMovementTime = time;
    const dt = Math.min(0.25, Math.max(0, (time - lastMovementTime) / 1000));
    lastMovementTime = time;

    const forward = (keyboardMovement.has("w") || mobileMovement.has("forward") ? 1 : 0)
      - (keyboardMovement.has("s") || mobileMovement.has("back") ? 1 : 0);
    const strafe = (keyboardMovement.has("d") || mobileMovement.has("right") ? 1 : 0)
      - (keyboardMovement.has("a") || mobileMovement.has("left") ? 1 : 0);
    if (!forward && !strafe) return;
    const magnitude = Math.hypot(forward, strafe) || 1;
    const normalizedForward = forward / magnitude;
    const normalizedStrafe = strafe / magnitude;
    const speed = keyboardMovement.has("shift") ? navigation.fastSpeed : navigation.speed;
    const distance = speed * dt;
    const sin = Math.sin(yaw);
    const cos = Math.cos(yaw);
    const dx = (-sin * normalizedForward + cos * normalizedStrafe) * distance;
    const dz = (-cos * normalizedForward - sin * normalizedStrafe) * distance;
    attemptMove(dx, dz);
  };

  const movementTick = (time: number) => {
    movementFrame = 0;
    if (!navigation || !hasMovementInput()) {
      lastMovementTime = 0;
      return;
    }
    advanceMovement(time);
    if (hasMovementInput()) movementFrame = requestAnimationFrame(movementTick);
  };

  const ensureMovementFrame = () => {
    if (!navigation || movementFrame || !hasMovementInput()) return;
    if (!lastMovementTime) lastMovementTime = performance.now();
    movementFrame = requestAnimationFrame(movementTick);
  };

  const setGuidedViewpoint = (nextViewpoint: SpatialGuidedViewpoint) => {
    clearMovement();
    viewpoint = nextViewpoint;
    const target = guidedPosition(nextViewpoint, navigation);
    camera.position.set(...target);
    if (navigation && !navigation.canOccupy(camera.position.x, camera.position.z, navigation.radius)) {
      camera.position.set(...guidedPosition("baseline", navigation));
      viewpoint = "baseline";
    }
    onViewpointChange?.(viewpoint);
    syncCamera();
    renderScene();
  };

  const reset = () => {
    clearMovement();
    yaw = navigation?.initialYaw ?? 0;
    pitch = -0.01;
    viewpoint = "baseline";
    camera.position.set(...guidedPosition("baseline", navigation));
    camera.fov = 52;
    camera.updateProjectionMatrix();
    onViewpointChange?.("baseline");
    syncCamera();
    renderScene();
  };

  const setNavigation = (nextNavigation: SpatialGroundNavigation | null) => {
    navigation = nextNavigation;
    updateAria();
    reset();
  };

  const setMovementInput = (direction: SpatialMoveDirection, active: boolean) => {
    if (!navigation) return;
    if (active) {
      mobileMovement.add(direction);
      ensureMovementFrame();
      return;
    }
    if (mobileMovement.has(direction)) advanceMovement(performance.now());
    mobileMovement.delete(direction);
    if (!hasMovementInput()) lastMovementTime = 0;
  };

  const onPointerDown = (event: PointerEvent) => {
    if (activePointer !== null) return;
    activePointer = event.pointerId;
    lastX = event.clientX;
    lastY = event.clientY;
    canvas.setPointerCapture(event.pointerId);
    canvas.focus({ preventScroll: true });
  };

  const onPointerMove = (event: PointerEvent) => {
    if (activePointer !== event.pointerId) return;
    const dx = event.clientX - lastX;
    const dy = event.clientY - lastY;
    lastX = event.clientX;
    lastY = event.clientY;
    yaw -= dx * 0.0042;
    pitch = THREE.MathUtils.clamp(pitch - dy * 0.0036, -1.08, 1.08);
    syncCamera();
    renderScene();
  };

  const stopPointer = (event: PointerEvent) => {
    if (activePointer !== event.pointerId) return;
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    activePointer = null;
  };

  const onKeyDown = (event: KeyboardEvent) => {
    const key = event.key.toLowerCase();
    if (navigation && MOVE_KEYS.has(key)) {
      event.preventDefault();
      keyboardMovement.add(key);
      ensureMovementFrame();
      return;
    }
    const step = event.shiftKey ? 0.14 : 0.07;
    if (event.key === "ArrowLeft") yaw += step;
    else if (event.key === "ArrowRight") yaw -= step;
    else if (event.key === "ArrowUp") pitch = THREE.MathUtils.clamp(pitch + step, -1.08, 1.08);
    else if (event.key === "ArrowDown") pitch = THREE.MathUtils.clamp(pitch - step, -1.08, 1.08);
    else if (key === "r") {
      event.preventDefault();
      reset();
      return;
    } else return;
    event.preventDefault();
    syncCamera();
    renderScene();
  };

  const onKeyUp = (event: KeyboardEvent) => {
    const key = event.key.toLowerCase();
    if (!MOVE_KEYS.has(key)) return;
    if (keyboardMovement.has(key)) advanceMovement(performance.now());
    keyboardMovement.delete(key);
    if (!hasMovementInput()) lastMovementTime = 0;
  };

  const onBlur = () => {
    keyboardMovement.clear();
    if (!hasMovementInput()) lastMovementTime = 0;
  };

  canvas.addEventListener("pointerdown", onPointerDown);
  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("pointerup", stopPointer);
  canvas.addEventListener("pointercancel", stopPointer);
  canvas.addEventListener("keydown", onKeyDown);
  canvas.addEventListener("keyup", onKeyUp);
  canvas.addEventListener("blur", onBlur);
  updateAria();
  syncCamera();

  return {
    id: observerId,
    get movement() {
      return movementMode();
    },
    getSnapshot: () => ({
      id: observerId,
      yaw,
      pitch,
      fov: camera.fov,
      position: [camera.position.x, camera.position.y, camera.position.z],
      viewpoint,
    }),
    setGuidedViewpoint,
    setNavigation,
    setMovementInput,
    reset,
    dispose: () => {
      clearMovement();
      canvas.removeEventListener("pointerdown", onPointerDown);
      canvas.removeEventListener("pointermove", onPointerMove);
      canvas.removeEventListener("pointerup", stopPointer);
      canvas.removeEventListener("pointercancel", stopPointer);
      canvas.removeEventListener("keydown", onKeyDown);
      canvas.removeEventListener("keyup", onKeyUp);
      canvas.removeEventListener("blur", onBlur);
    },
  };
}
