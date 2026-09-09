# C0 generated-asset rendering contract

Audit basis for this generated C0 revision:

- Berlin official LoD2 remains the macro-geometry source of truth.
- Hansaplatz panorama projection is albedo/detail only and is non-emissive.
- Runtime directional/practical lighting and authored mesh shadows determine depth.
- Non-reference foreground placeholders are excluded from the generated C0 asset.
- The audit branch is rebased onto the current main shadow/contact-depth runtime before browser acceptance.
- Browser acceptance must cover forward, turned, moved, opposite and mobile viewpoints of this regenerated asset.
