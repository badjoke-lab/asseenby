from pathlib import Path
import re

path = Path('src/spatial/observerRuntime.ts')
text = path.read_text()

attempt_pattern = r'''  const attemptMove = \(dx: number, dz: number\) => \{.*?\n  \};\n\n  const hasMovementInput'''
attempt_replacement = '''  const attemptMove = (dx: number, dz: number) => {
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

  const hasMovementInput'''
text, count = re.subn(attempt_pattern, attempt_replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('attemptMove block not found')

movement_pattern = r'''  const movementTick = \(time: number\) => \{.*?\n  \};\n\n  const ensureMovementFrame'''
movement_replacement = '''  const advanceMovement = (time: number) => {
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

  const ensureMovementFrame'''
text, count = re.subn(movement_pattern, movement_replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('movementTick block not found')

text = text.replace(
'''  const ensureMovementFrame = () => {
    if (!navigation || movementFrame || !hasMovementInput()) return;
    lastMovementTime = 0;
    movementFrame = requestAnimationFrame(movementTick);
  };''',
'''  const ensureMovementFrame = () => {
    if (!navigation || movementFrame || !hasMovementInput()) return;
    if (!lastMovementTime) lastMovementTime = performance.now();
    movementFrame = requestAnimationFrame(movementTick);
  };''',
1,
)

text = text.replace(
'''  const setMovementInput = (direction: SpatialMoveDirection, active: boolean) => {
    if (!navigation) return;
    if (active) mobileMovement.add(direction);
    else mobileMovement.delete(direction);
    if (active) ensureMovementFrame();
    else if (!hasMovementInput()) lastMovementTime = 0;
  };''',
'''  const setMovementInput = (direction: SpatialMoveDirection, active: boolean) => {
    if (!navigation) return;
    if (active) {
      mobileMovement.add(direction);
      ensureMovementFrame();
      return;
    }
    if (mobileMovement.has(direction)) advanceMovement(performance.now());
    mobileMovement.delete(direction);
    if (!hasMovementInput()) lastMovementTime = 0;
  };''',
1,
)

text = text.replace(
'''  const onKeyUp = (event: KeyboardEvent) => {
    const key = event.key.toLowerCase();
    if (!MOVE_KEYS.has(key)) return;
    keyboardMovement.delete(key);
    if (!hasMovementInput()) lastMovementTime = 0;
  };''',
'''  const onKeyUp = (event: KeyboardEvent) => {
    const key = event.key.toLowerCase();
    if (!MOVE_KEYS.has(key)) return;
    if (keyboardMovement.has(key)) advanceMovement(performance.now());
    keyboardMovement.delete(key);
    if (!hasMovementInput()) lastMovementTime = 0;
  };''',
1,
)

path.write_text(text)
