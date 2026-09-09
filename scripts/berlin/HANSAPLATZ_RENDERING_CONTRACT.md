# Hansaplatz C0 rendering contract

- Macro building geometry comes from Berlin official LoD2 data.
- The Poly Haven Hansaplatz panorama is used only as projected facade albedo/detail.
- Projected facade imagery must not self-emit; runtime moon/practical lights and shadows determine illumination and contact depth.
- Non-reference foreground placeholders stay absent until a reference-matched authored asset replaces them.
- Regenerate the canonical Blender source and C0 GLB after changing this contract or its implementation.
