from pathlib import Path

path = Path("scripts/e4_validate.mjs")
text = path.read_text()

helper = r'''
function cataractSpreadMetrics(normalBuffer, modeBuffer) {
  const a = decode(normalBuffer);
  const b = decode(modeBuffer);
  assert.equal(a.width, b.width);
  assert.equal(a.height, b.height);

  const pixelCount = a.width * a.height;
  const baseLumas = new Float64Array(pixelCount);
  const gains = new Float64Array(pixelCount);
  const lumas = new Array(pixelCount);
  for (let pixel = 0; pixel < pixelCount; pixel += 1) {
    const i = pixel * 4;
    const base = luma(a.data[i], a.data[i + 1], a.data[i + 2]);
    const transformed = luma(b.data[i], b.data[i + 1], b.data[i + 2]);
    baseLumas[pixel] = base;
    gains[pixel] = transformed - base;
    lumas[pixel] = base;
  }

  const brightThreshold = quantile(lumas, 0.98);
  const nearOffsets = [[3, 0], [-3, 0], [0, 3], [0, -3], [3, 3], [3, -3], [-3, 3], [-3, -3]];
  const farOffsets = [[18, 0], [-18, 0], [0, 18], [0, -18], [18, 18], [18, -18], [-18, 18], [-18, -18]];
  let nearSum = 0, nearSamples = 0, farSum = 0, farSamples = 0, brightSources = 0;

  const sampleOffsets = (x, y, offsets, bucket) => {
    for (const [dx, dy] of offsets) {
      const sx = x + dx;
      const sy = y + dy;
      if (sx < 0 || sx >= a.width || sy < 0 || sy >= a.height) continue;
      const pixel = sy * a.width + sx;
      if (baseLumas[pixel] >= brightThreshold) continue;
      if (bucket === "near") {
        nearSum += gains[pixel];
        nearSamples += 1;
      } else {
        farSum += gains[pixel];
        farSamples += 1;
      }
    }
  };

  for (let y = 0; y < a.height; y += 1) {
    for (let x = 0; x < a.width; x += 1) {
      const pixel = y * a.width + x;
      if (baseLumas[pixel] < brightThreshold) continue;
      brightSources += 1;
      sampleOffsets(x, y, nearOffsets, "near");
      sampleOffsets(x, y, farOffsets, "far");
    }
  }

  return {
    brightThreshold,
    brightSources,
    nearGain: nearSum / Math.max(1, nearSamples),
    farGain: farSum / Math.max(1, farSamples),
    nearSamples,
    farSamples,
  };
}

'''

anchor = "async function desktopValidation() {"
if "function cataractSpreadMetrics(" not in text:
    if anchor not in text:
        raise SystemExit("desktopValidation anchor missing")
    text = text.replace(anchor, helper + anchor, 1)

old = '  assert(result.metrics.cataract.brightDelta > result.metrics.cataract.midDelta * 1.03, `Cataract does not respond more strongly around high-luminance content: ${JSON.stringify(result.metrics.cataract)}`);'
new = '''  result.metrics.cataractSpread = cataractSpreadMetrics(captures["Normal"], captures["Cataract-like"]);\n  assert(result.metrics.cataractSpread.nearSamples > 1000, `Cataract bright-source spread sample is too small: ${JSON.stringify(result.metrics.cataractSpread)}`);\n  assert(result.metrics.cataractSpread.nearGain > 20 && result.metrics.cataractSpread.nearGain > result.metrics.cataractSpread.farGain + 6, `Cataract does not produce a local bright-source glare spread: ${JSON.stringify(result.metrics.cataractSpread)}`);'''
if old not in text and "result.metrics.cataractSpread = cataractSpreadMetrics" not in text:
    raise SystemExit("old Cataract assertion missing")
text = text.replace(old, new, 1)
path.write_text(text)
print("E4 Cataract validation corrected to measure bright-source halo spread")
