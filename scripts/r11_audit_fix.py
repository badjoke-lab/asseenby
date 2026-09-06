from pathlib import Path

p = Path("scripts/r11_cvd_audit.mjs")
text = p.read_text()
old = '''  for (const mode of modes) {
    let before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
    await page.locator("#mode-select").selectOption(mode);
    await waitForNewApproximation(page, before);

    for (const strength of strengths) {
'''
new = '''  for (const mode of modes) {
    let before;
    const currentMode = await page.locator("#mode-select").inputValue();
    if (currentMode !== mode) {
      before = await page.locator('img[alt="Approximation"]').first().getAttribute("src");
      await page.locator("#mode-select").selectOption(mode);
      await waitForNewApproximation(page, before);
    }

    for (const strength of strengths) {
'''
if text.count(old) != 1:
    raise SystemExit(f"expected one initial-mode anchor, found {text.count(old)}")
p.write_text(text.replace(old, new, 1))
