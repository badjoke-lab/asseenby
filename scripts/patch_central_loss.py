from pathlib import Path

path = Path("src/SpatialPage.tsx")
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label}")
    text = text.replace(old, new, 1)


replace_once(
    'type SpatialMode = "normal" | "tunnel" | "cataract";',
    'type SpatialMode = "normal" | "tunnel" | "central_loss" | "cataract";',
    "SpatialMode union",
)

central_shader = r'''const CENTRAL_LOSS_SHADER = {
  uniforms: {
    tDiffuse: { value: null },
    resolution: { value: new THREE.Vector2(1, 1) },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform vec2 resolution;
    varying vec2 vUv;

    void main() {
      vec2 px = 1.0 / max(resolution, vec2(1.0));
      vec4 source = texture2D(tDiffuse, vUv);

      vec2 centered = vUv - 0.5;
      centered.x *= resolution.x / max(resolution.y, 1.0);
      float radius = length(centered);
      float angle = atan(centered.y, centered.x);
      float boundary = 0.165 + sin(angle * 3.0 + 0.35) * 0.012 + sin(angle * 5.0 - 0.7) * 0.008;
      float affected = 1.0 - smoothstep(boundary * 0.62, boundary * 1.28, radius);
      float core = 1.0 - smoothstep(boundary * 0.24, boundary * 0.72, radius);

      vec3 soft = source.rgb * 0.36;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 4.5, 0.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv - vec2(px.x * 4.5, 0.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(0.0, px.y * 4.5)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv - vec2(0.0, px.y * 4.5)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 7.0, px.y * 5.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x * 7.0, px.y * 5.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 7.0, -px.y * 5.0)).rgb * 0.08;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x * 7.0, -px.y * 5.0)).rgb * 0.08;

      float luma = dot(soft, vec3(0.2126, 0.7152, 0.0722));
      vec3 muted = mix(soft, vec3(luma), 0.58);
      vec3 lowContrast = mix(vec3(0.11, 0.105, 0.10), muted, 0.58);
      vec3 scotoma = mix(lowContrast, vec3(0.075, 0.073, 0.070), core * 0.76);
      vec3 result = mix(source.rgb, scotoma, affected * 0.94);

      gl_FragColor = vec4(result, source.a);
    }
  `,
};

'''
replace_once(
    "const CATARACT_SHADER = {",
    central_shader + "const CATARACT_SHADER = {",
    "insert Central Loss shader",
)

replace_once(
    '<strong>Comparison rule:</strong> switching the perception mode does not move the camera or alter the street scene. Tunnel Vision is a generic field-loss model; Cataract-like is a generic scene-dependent glare and haze model, not an individual\'s measured visual reconstruction.',
    '<strong>Comparison rule:</strong> switching the perception mode does not move the camera or alter the street scene. Tunnel Vision and Central Loss are generic field-loss models; Cataract-like is a generic scene-dependent glare and haze model. None are an individual\'s measured visual reconstruction.',
    "spatial limitation note",
)

replace_once(
    "    let tunnelPass: ShaderPass | null = null;\n    let cataractPass: ShaderPass | null = null;",
    "    let tunnelPass: ShaderPass | null = null;\n    let centralLossPass: ShaderPass | null = null;\n    let cataractPass: ShaderPass | null = null;",
    "pass declarations",
)

replace_once(
    "      cataractPass = new ShaderPass(CATARACT_SHADER);\n      cataractPass.enabled = false;\n      composer.addPass(cataractPass);\n\n      tunnelPass = new ShaderPass(TUNNEL_SHADER);",
    "      cataractPass = new ShaderPass(CATARACT_SHADER);\n      cataractPass.enabled = false;\n      composer.addPass(cataractPass);\n\n      centralLossPass = new ShaderPass(CENTRAL_LOSS_SHADER);\n      centralLossPass.enabled = false;\n      composer.addPass(centralLossPass);\n\n      tunnelPass = new ShaderPass(TUNNEL_SHADER);",
    "composer Central Loss pass",
)

replace_once(
    '        if (cataractPass) cataractPass.enabled = nextMode === "cataract";\n        if (tunnelPass) tunnelPass.enabled = nextMode === "tunnel";',
    '        if (cataractPass) cataractPass.enabled = nextMode === "cataract";\n        if (centralLossPass) centralLossPass.enabled = nextMode === "central_loss";\n        if (tunnelPass) tunnelPass.enabled = nextMode === "tunnel";',
    "mode toggles",
)

replace_once(
    "        if (!renderer || !composer || !tunnelPass || !cataractPass) return;",
    "        if (!renderer || !composer || !tunnelPass || !centralLossPass || !cataractPass) return;",
    "resize guard",
)

replace_once(
    "        (tunnelPass.uniforms.resolution.value as THREE.Vector2).set(width, height);\n        (cataractPass.uniforms.resolution.value as THREE.Vector2).set(width, height);",
    "        (tunnelPass.uniforms.resolution.value as THREE.Vector2).set(width, height);\n        (centralLossPass.uniforms.resolution.value as THREE.Vector2).set(width, height);\n        (cataractPass.uniforms.resolution.value as THREE.Vector2).set(width, height);",
    "resolution uniforms",
)

cleanup_count = text.count("tunnelPass?.material.dispose();")
if cleanup_count != 2:
    raise SystemExit(f"expected two tunnel cleanup anchors, found {cleanup_count}")
text = text.replace(
    "tunnelPass?.material.dispose();",
    "tunnelPass?.material.dispose();\n        centralLossPass?.material.dispose();",
)

replace_once(
    '  const modeDescription = mode === "normal"\n    ? "Baseline scene with no perception simulation."\n    : mode === "tunnel"\n      ? "Live screen-relative peripheral field loss. Look around to see how objects outside the center become harder to notice."\n      : "Scene-aware haze, softness, lower contrast, warming, and bright-source glare. Turn toward headlights or streetlights, then toward a dark area to compare.";',
    '  const modeDescription = mode === "normal"\n    ? "Baseline scene with no perception simulation."\n    : mode === "tunnel"\n      ? "Live screen-relative peripheral field loss. Look around to see how objects outside the center become harder to notice."\n      : mode === "central_loss"\n        ? "Live screen-relative central field loss. Center a pedestrian, sign, or light, then look elsewhere to see the disrupted region stay with straight-ahead vision."\n        : "Scene-aware haze, softness, lower contrast, warming, and bright-source glare. Turn toward headlights or streetlights, then toward a dark area to compare.";',
    "mode description",
)

replace_once(
    '        <button type="button" className={mode === "tunnel" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "tunnel"} onClick={() => setMode("tunnel")}>Tunnel Vision</button>\n        <button type="button" className={mode === "cataract" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "cataract"} onClick={() => setMode("cataract")}>Cataract-like</button>',
    '        <button type="button" className={mode === "tunnel" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "tunnel"} onClick={() => setMode("tunnel")}>Tunnel Vision</button>\n        <button type="button" className={mode === "central_loss" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "central_loss"} onClick={() => setMode("central_loss")}>Central Loss</button>\n        <button type="button" className={mode === "cataract" ? "spatial-mode-button spatial-mode-button--active" : "spatial-mode-button"} aria-pressed={mode === "cataract"} onClick={() => setMode("cataract")}>Cataract-like</button>',
    "Central Loss button",
)

path.write_text(text)
