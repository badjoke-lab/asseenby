import * as THREE from "three";
import type { SpatialGuidedViewpoint, SpatialObserverId } from "./catalog";

export type SpatialObserverSnapshot = {
  id: SpatialObserverId;
  yaw: number;
  pitch: number;
  fov: number;
  position: [number, number, number];
  viewpoint: SpatialGuidedViewpoint;
};

export type SpatialObserverRuntime = {
  id: SpatialObserverId;
  movement: "look-only";
  getSnapshot: () => SpatialObserverSnapshot;
  setGuidedViewpoint: (viewpoint: SpatialGuidedViewpoint) => void;
  reset: () => void;
  dispose: () => void;
};

type ObserverRuntimeOptions = {
  camera: THREE.PerspectiveCamera;
  canvas: HTMLCanvasElement;
  renderScene: () => void;
};

const GUIDED_VIEWPOINT_POSITIONS: Record<SpatialGuidedViewpoint, [number, number, number]> = {
  baseline: [0, 0, 0],
  offset: [3.2, 0, -4.2],
};

export function createSpatialObserverRuntime(
  observerId: SpatialObserverId,
  { camera, canvas, renderScene }: ObserverRuntimeOptions,
): SpatialObserverRuntime {
  if (observerId !== "human") {
    throw new Error(`Unsupported Explore 3D observer: ${observerId}`);
  }

  let yaw = 0;
  let pitch = -0.01;
  let activePointer: number | null = null;
  let lastX = 0;
  let lastY = 0;
  let viewpoint: SpatialGuidedViewpoint = "baseline";

  camera.position.set(...GUIDED_VIEWPOINT_POSITIONS.baseline);
  camera.rotation.order = "YXZ";

  const syncCamera = () => {
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;
    canvas.dataset.observerId = observerId;
    canvas.dataset.observerMovement = "look-only";
    canvas.dataset.cameraViewpoint = viewpoint;
    canvas.dataset.cameraYaw = yaw.toFixed(6);
    canvas.dataset.cameraPitch = pitch.toFixed(6);
    canvas.dataset.cameraFov = camera.fov.toFixed(3);
    canvas.dataset.cameraPosition = `${camera.position.x.toFixed(3)},${camera.position.y.toFixed(3)},${camera.position.z.toFixed(3)}`;
  };

  const setGuidedViewpoint = (nextViewpoint: SpatialGuidedViewpoint) => {
    viewpoint = nextViewpoint;
    camera.position.set(...GUIDED_VIEWPOINT_POSITIONS[nextViewpoint]);
    syncCamera();
    renderScene();
  };

  const reset = () => {
    yaw = 0;
    pitch = -0.01;
    viewpoint = "baseline";
    camera.position.set(...GUIDED_VIEWPOINT_POSITIONS.baseline);
    camera.fov = 52;
    camera.updateProjectionMatrix();
    syncCamera();
    renderScene();
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
    const step = event.shiftKey ? 0.14 : 0.07;
    if (event.key === "ArrowLeft") yaw += step;
    else if (event.key === "ArrowRight") yaw -= step;
    else if (event.key === "ArrowUp") pitch = THREE.MathUtils.clamp(pitch + step, -1.08, 1.08);
    else if (event.key === "ArrowDown") pitch = THREE.MathUtils.clamp(pitch - step, -1.08, 1.08);
    else if (event.key.toLowerCase() === "r") {
      event.preventDefault();
      reset();
      return;
    } else return;
    event.preventDefault();
    syncCamera();
    renderScene();
  };

  canvas.setAttribute("aria-label", "Explore 3D. Human reference observer. Drag or use arrow keys to look around; press R to reset the current scene view.");
  canvas.addEventListener("pointerdown", onPointerDown);
  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("pointerup", stopPointer);
  canvas.addEventListener("pointercancel", stopPointer);
  canvas.addEventListener("keydown", onKeyDown);
  syncCamera();

  return {
    id: observerId,
    movement: "look-only",
    getSnapshot: () => ({
      id: observerId,
      yaw,
      pitch,
      fov: camera.fov,
      position: [camera.position.x, camera.position.y, camera.position.z],
      viewpoint,
    }),
    setGuidedViewpoint,
    reset,
    dispose: () => {
      canvas.removeEventListener("pointerdown", onPointerDown);
      canvas.removeEventListener("pointermove", onPointerMove);
      canvas.removeEventListener("pointerup", stopPointer);
      canvas.removeEventListener("pointercancel", stopPointer);
      canvas.removeEventListener("keydown", onKeyDown);
    },
  };
}
