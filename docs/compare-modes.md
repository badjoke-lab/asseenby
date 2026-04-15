# AsSeenBy — Compare Modes

## Goal
The compare stage should make it easy to inspect the difference between the source image and the transformed image.

## Modes

### Slider
- source image stays behind
- transformed image is revealed by a movable divider
- the user adjusts a balance control
- best for gradual inspection across one image plane

### Split
- source and transformed image are shown in a fixed 50 / 50 split
- no draggable balance is required
- useful when the user wants a stable midpoint comparison

### Side by side
- source and transformed image are shown in separate panels
- best for broader composition-level comparison
- useful on large displays and for reference viewing

## UI rule
The three compare modes should not feel like cosmetic variants.
Each mode should have a visibly distinct interaction model.

## Current implementation note
If slider and split share the same interaction pattern, split should be adjusted so that it becomes a fixed comparison state rather than a second slider variant.
