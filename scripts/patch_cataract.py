from pathlib import Path
import re

path = Path("src/SpatialPage.tsx")
text = path.read_text()

replacement = r'''const CATARACT_SHADER = {
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

    vec3 brightSample(vec2 uv) {
      vec3 sampleColor = texture2D(tDiffuse, clamp(uv, vec2(0.001), vec2(0.999))).rgb;
      float luminance = dot(sampleColor, vec3(0.2126, 0.7152, 0.0722));
      float brightGate = smoothstep(0.58, 1.05, luminance);
      return sampleColor * brightGate;
    }

    void main() {
      vec2 px = 1.0 / max(resolution, vec2(1.0));
      vec3 source = texture2D(tDiffuse, vUv).rgb;

      vec3 soft = source * 0.56;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 1.5, 0.0)).rgb * 0.07;
      soft += texture2D(tDiffuse, vUv - vec2(px.x * 1.5, 0.0)).rgb * 0.07;
      soft += texture2D(tDiffuse, vUv + vec2(0.0, px.y * 1.5)).rgb * 0.07;
      soft += texture2D(tDiffuse, vUv - vec2(0.0, px.y * 1.5)).rgb * 0.07;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 1.5, px.y * 1.5)).rgb * 0.04;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x * 1.5, px.y * 1.5)).rgb * 0.04;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * 1.5, -px.y * 1.5)).rgb * 0.04;
      soft += texture2D(tDiffuse, vUv + vec2(-px.x * 1.5, -px.y * 1.5)).rgb * 0.04;

      vec3 glare = vec3(0.0);
      glare += brightSample(vUv + vec2(px.x * 4.0, 0.0));
      glare += brightSample(vUv - vec2(px.x * 4.0, 0.0));
      glare += brightSample(vUv + vec2(0.0, px.y * 4.0));
      glare += brightSample(vUv - vec2(0.0, px.y * 4.0));
      glare += brightSample(vUv + vec2(px.x * 8.0, px.y * 5.0));
      glare += brightSample(vUv + vec2(-px.x * 8.0, px.y * 5.0));
      glare += brightSample(vUv + vec2(px.x * 8.0, -px.y * 5.0));
      glare += brightSample(vUv + vec2(-px.x * 8.0, -px.y * 5.0));
      glare += brightSample(vUv + vec2(px.x * 15.0, 0.0)) * 0.7;
      glare += brightSample(vUv - vec2(px.x * 15.0, 0.0)) * 0.7;
      glare += brightSample(vUv + vec2(0.0, px.y * 15.0)) * 0.7;
      glare += brightSample(vUv - vec2(0.0, px.y * 15.0)) * 0.7;
      glare *= 0.085;

      float luma = dot(soft, vec3(0.2126, 0.7152, 0.0722));
      vec3 desaturated = mix(vec3(luma), soft, 0.82);
      vec3 lowerContrast = mix(vec3(0.075, 0.072, 0.065), desaturated, 0.84);
      vec3 warmed = lowerContrast * vec3(1.055, 1.015, 0.92);
      vec3 veiled = mix(warmed, vec3(0.34, 0.29, 0.20), 0.035);
      vec3 result = min(veiled + glare * vec3(1.08, 1.02, 0.88), vec3(1.35));
      gl_FragColor = vec4(result, 1.0);
    }
  `,
};'''

text, count = re.subn(
    r"const CATARACT_SHADER = \{.*?\n\};\n\nexport default function SpatialPage",
    replacement + "\n\nexport default function SpatialPage",
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f"expected one cataract shader block, replaced {count}")

old = 'if (bloomPass) bloomPass.enabled = nextMode === "cataract";'
new = 'if (bloomPass) bloomPass.enabled = false;'
if old not in text:
    raise SystemExit("bloom mode line not found")
text = text.replace(old, new, 1)

path.write_text(text)
