from pathlib import Path

page = Path('src/SpatialPage.tsx')
text = page.read_text()
old = '''                  onPointerDown={(event) => {
                    event.currentTarget.setPointerCapture(event.pointerId);
                    controllerRef.current?.setMovementInput(direction, true);
                  }}'''
new = '''                  onPointerDown={(event) => {
                    controllerRef.current?.setMovementInput(direction, true);
                    try {
                      event.currentTarget.setPointerCapture(event.pointerId);
                    } catch {
                      // Touch input may not expose pointer capture in every browser/runtime.
                    }
                  }}'''
if old not in text:
    raise SystemExit('mobile pointer handler not found')
page.write_text(text.replace(old, new, 1))

css = Path('src/spatial.css')
text = css.read_text()
old = '''.spatial-move-button {
  min-width: 44px;
  padding: 0;
  border-radius: 8px;
  font-size: 1.05rem;
  line-height: 1;
}'''
new = '''.spatial-move-button {
  min-width: 44px;
  padding: 0;
  border-radius: 8px;
  font-size: 1.05rem;
  line-height: 1;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}'''
if old not in text:
    raise SystemExit('mobile movement css block not found')
css.write_text(text.replace(old, new, 1))
