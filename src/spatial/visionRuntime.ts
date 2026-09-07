import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import type { SpatialVisionMode } from "./catalog";

const TUNNEL_SHADER = {
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
      vec4 source = texture2D(tDiffuse, vUv);
      vec2 centered = vUv - 0.5;
      centered.x *= resolution.x / max(resolution.y, 1.0);
      float radius = length(centered);
      float visibility = 1.0 - smoothstep(0.22, 0.56, radius);
      float edgeDesaturation = smoothstep(0.13, 0.48, radius);
      float luma = dot(source.rgb, vec3(0.2126, 0.7152, 0.0722));
      vec3 muted = mix(source.rgb, vec3(luma), edgeDesaturation * 0.55);
      vec3 obscured = vec3(0.012, 0.014, 0.016);
      gl_FragColor = vec4(mix(obscured, muted, visibility), source.a);
    }
  `,
};

const CENTRAL_LOSS_SHADER = {
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

const NIGHT_LOW_LIGHT_SHADER = {
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

    float lumaAt(vec2 uv) {
      vec3 color = texture2D(tDiffuse, clamp(uv, vec2(0.001), vec2(0.999))).rgb;
      return dot(color, vec3(0.2126, 0.7152, 0.0722));
    }

    void main() {
      vec2 px = 1.0 / max(resolution, vec2(1.0));
      vec3 source = texture2D(tDiffuse, vUv).rgb;
      float localLuma = dot(source, vec3(0.2126, 0.7152, 0.0722));

      float viewLuma = (
        lumaAt(vec2(0.50, 0.50)) +
        lumaAt(vec2(0.24, 0.28)) +
        lumaAt(vec2(0.76, 0.28)) +
        lumaAt(vec2(0.24, 0.72)) +
        lumaAt(vec2(0.76, 0.72))
      ) / 5.0;

      float dimView = 1.0 - smoothstep(0.16, 0.48, viewLuma);
      float localDark = 1.0 - smoothstep(0.08, 0.52, localLuma);
      float lowLightWeight = clamp(localDark * 0.72 + dimView * 0.46, 0.0, 1.0);

      float blurRadius = mix(0.7, 2.8, lowLightWeight);
      vec3 soft = source * 0.48;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * blurRadius, 0.0)).rgb * 0.13;
      soft += texture2D(tDiffuse, vUv - vec2(px.x * blurRadius, 0.0)).rgb * 0.13;
      soft += texture2D(tDiffuse, vUv + vec2(0.0, px.y * blurRadius)).rgb * 0.13;
      soft += texture2D(tDiffuse, vUv - vec2(0.0, px.y * blurRadius)).rgb * 0.13;

      float softLuma = dot(soft, vec3(0.2126, 0.7152, 0.0722));
      float desaturation = mix(0.18, 0.78, lowLightWeight);
      vec3 muted = mix(soft, vec3(softLuma), desaturation);

      float contrastScale = mix(0.94, 0.68, lowLightWeight);
      vec3 reducedContrast = vec3(0.065) + (muted - vec3(0.065)) * contrastScale;
      float shadowLoss = localDark * mix(0.08, 0.26, dimView);
      vec3 result = reducedContrast * (1.0 - shadowLoss);

      gl_FragColor = vec4(result, 1.0);
    }
  `,
};

const DOG_LIKE_SHADER = {
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
      float blurRadius = clamp(resolution.y / 420.0, 0.8, 2.8);
      vec3 source = texture2D(tDiffuse, vUv).rgb;

      vec3 soft = source * 0.44;
      soft += texture2D(tDiffuse, vUv + vec2(px.x * blurRadius, 0.0)).rgb * 0.14;
      soft += texture2D(tDiffuse, vUv - vec2(px.x * blurRadius, 0.0)).rgb * 0.14;
      soft += texture2D(tDiffuse, vUv + vec2(0.0, px.y * blurRadius)).rgb * 0.14;
      soft += texture2D(tDiffuse, vUv - vec2(0.0, px.y * blurRadius)).rgb * 0.14;

      // Human-display translation of a simplified two-channel visible-range model.
      // Standard RGB cannot reconstruct canine cone catches for arbitrary real spectra.
      float longChannel = soft.r * 0.56 + soft.g * 0.44;
      float shortChannel = soft.r * 0.04 + soft.g * 0.13 + soft.b * 0.83;
      vec3 dichromatic = vec3(
        longChannel * 0.84 + shortChannel * 0.03,
        longChannel * 0.72 + shortChannel * 0.18,
        shortChannel * 0.86 + longChannel * 0.14
      );

      float sourceLuma = dot(soft, vec3(0.2126, 0.7152, 0.0722));
      float mappedLuma = max(0.02, dot(dichromatic, vec3(0.2126, 0.7152, 0.0722)));
      dichromatic *= clamp((sourceLuma + 0.025) / mappedLuma, 0.72, 1.32);
      vec3 reducedContrast = vec3(0.055) + (dichromatic - vec3(0.055)) * 0.92;

      gl_FragColor = vec4(clamp(reducedContrast, 0.0, 1.0), 1.0);
    }
  `,
};

const CATARACT_SHADER = {
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
};

export type SpatialVisionRuntime = {
  setVision: (vision: SpatialVisionMode) => void;
  resize: (width: number, height: number) => void;
  dispose: () => void;
};

export function createSpatialVisionRuntime(
  composer: EffectComposer,
  canvas: HTMLCanvasElement,
  renderScene: () => void,
): SpatialVisionRuntime {
  const bloomPass = new UnrealBloomPass(new THREE.Vector2(1, 1), 1.3, 0.78, 0.62);
  bloomPass.enabled = false;
  composer.addPass(bloomPass);

  const cataractPass = new ShaderPass(CATARACT_SHADER);
  cataractPass.enabled = false;
  composer.addPass(cataractPass);

  const nightPass = new ShaderPass(NIGHT_LOW_LIGHT_SHADER);
  nightPass.enabled = false;
  composer.addPass(nightPass);

  const dogPass = new ShaderPass(DOG_LIKE_SHADER);
  dogPass.enabled = false;
  composer.addPass(dogPass);

  const centralLossPass = new ShaderPass(CENTRAL_LOSS_SHADER);
  centralLossPass.enabled = false;
  composer.addPass(centralLossPass);

  const tunnelPass = new ShaderPass(TUNNEL_SHADER);
  tunnelPass.enabled = false;
  composer.addPass(tunnelPass);
  composer.addPass(new OutputPass());

  const setVision = (vision: SpatialVisionMode) => {
    bloomPass.enabled = false;
    cataractPass.enabled = vision === "cataract";
    nightPass.enabled = vision === "night";
    dogPass.enabled = vision === "dog";
    centralLossPass.enabled = vision === "central_loss";
    tunnelPass.enabled = vision === "tunnel";
    canvas.dataset.visionMode = vision;
    renderScene();
  };

  const resize = (width: number, height: number) => {
    (tunnelPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
    (centralLossPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
    (nightPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
    (dogPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
    (cataractPass.uniforms.resolution.value as THREE.Vector2).set(width, height);
  };

  return {
    setVision,
    resize,
    dispose: () => {
      tunnelPass.material.dispose();
      centralLossPass.material.dispose();
      nightPass.material.dispose();
      dogPass.material.dispose();
      cataractPass.material.dispose();
      bloomPass.dispose();
    },
  };
}
