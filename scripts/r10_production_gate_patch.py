from pathlib import Path

p = Path('.github/production-smoke.mjs')
text = p.read_text()

old = '''    let currentAnimalSet = false;
    let currentHumanSet = false;
    try {
      const categoryValues = await page.locator("#category-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      if (JSON.stringify(categoryValues) !== JSON.stringify(["Human", "Animal"])) throw new Error(`unexpected image categories ${JSON.stringify(categoryValues)}`);
      await page.locator("#category-select").selectOption("Animal");
      const animalValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      currentAnimalSet = JSON.stringify(animalValues) === JSON.stringify(expectedAnimalImageModes);
      await page.locator("#category-select").selectOption("Human");
      const humanValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      currentHumanSet = JSON.stringify(humanValues) === JSON.stringify(expectedHumanImageModes);
    } catch {
      currentAnimalSet = false;
      currentHumanSet = false;
    }

    if (src?.startsWith("blob:") && currentAnimalSet && currentHumanSet) {
      result.productionReleaseDetected = true;
      result.notes.push(`current production behavior detected on attempt ${attempt}; image categories are Human/Animal only, with the audited Human set and Animal=Dog-like only`);
      return;
    }

    result.notes.push(`attempt ${attempt}: production is stale for blob upload, Human/Animal category set, Human modes, and/or Animal modes`);
'''

new = '''    let currentAnimalSet = false;
    let currentHumanSet = false;
    let currentStrengthZeroIdentity = false;
    try {
      const categoryValues = await page.locator("#category-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      if (JSON.stringify(categoryValues) !== JSON.stringify(["Human", "Animal"])) throw new Error(`unexpected image categories ${JSON.stringify(categoryValues)}`);
      await page.locator("#category-select").selectOption("Animal");
      const animalValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      currentAnimalSet = JSON.stringify(animalValues) === JSON.stringify(expectedAnimalImageModes);
      await page.locator("#category-select").selectOption("Human");
      const humanValues = await page.locator("#mode-select option").evaluateAll((nodes) => nodes.map((node) => node.value));
      currentHumanSet = JSON.stringify(humanValues) === JSON.stringify(expectedHumanImageModes);
      await page.locator("#mode-select").selectOption("protan");
      await setReactRangeValue(page, "#strength-range", 0);
      await page.waitForTimeout(180);
      await page.locator('.compare-card[aria-busy="false"]').waitFor({ timeout: 2_000 });
      const zeroOriginal = await page.locator('img[alt="Original"]').first().getAttribute("src");
      const zeroApproximation = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
      currentStrengthZeroIdentity = Boolean(zeroOriginal && zeroOriginal === zeroApproximation);
    } catch {
      currentAnimalSet = false;
      currentHumanSet = false;
      currentStrengthZeroIdentity = false;
    }

    if (src?.startsWith("blob:") && currentAnimalSet && currentHumanSet && currentStrengthZeroIdentity) {
      result.productionReleaseDetected = true;
      result.notes.push(`current production behavior detected on attempt ${attempt}; image categories/modes match and Strength 0 is exact Original`);
      return;
    }

    result.notes.push(`attempt ${attempt}: production is stale for blob upload, current image mode set, and/or Strength-0 identity`);
'''

if text.count(old) != 1:
    raise SystemExit(f'expected one release-gate anchor, found {text.count(old)}')
text = text.replace(old, new, 1)

old_error = '  throw new Error("Production did not reach the current blob-upload + Human/Animal-only release behavior within the retry window.");'
new_error = '  throw new Error("Production did not reach the current blob-upload + image-mode-set + Strength-0-identity release behavior within the retry window.");'
if text.count(old_error) != 1:
    raise SystemExit('release-gate error anchor mismatch')

p.write_text(text.replace(old_error, new_error, 1))
