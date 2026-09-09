# Hansaplatz source correction

The Poly Haven `hansaplatz` panorama used by Explore 3D is located at Hansaplatz, Hamburg-St. Georg, Germany, not Berlin.

Canonical reference coordinates: `53.554451, 10.012056`.

## Current production geometry

The current production C0 geometry is aligned to the official Hamburg `3D-Gebäudemodell LoD2-DE Hamburg 2026` dataset from Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV), EPSG:25832, licensed `dl-de-by-2.0`.

The reproducible local subset in `assets-src/blender/night-intersection/hamburg-lod2/` contains 113 buildings and 339 semantic objects within the selected 170 m radius. The generated Blender source and runtime GLB are rebuilt from this Hamburg geometry before browser validation.

The former Berlin LoD2 + Hamburg panorama combination was a source-location mismatch and must not be reintroduced.

## Active quality target: Hamburg LoD3.0-HH

The next macro-geometry target is the official Hamburg `3D-Gebäudemodell LoD3.0-HH Hamburg untexturiert, Area1, 2025`. Area 1 covers the inner-city area containing Hansaplatz. The geometry is based on Hamburg's LoD3.0-HH model and is distributed without textures; licensing remains Datenlizenz Deutschland Namensnennung 2.0 with LGV attribution.

LoD3.0-HH improves the building shell primarily through a more detailed roof landscape, significant roof overhangs and roof superstructures. It must not be treated as proof that close-range windows, doors, shopfront recesses, signs or street-level architectural depth are modeled sufficiently for QR2.

Therefore the production quality path is intentionally hybrid:

1. official Hamburg LoD3.0-HH geometry for the real macro building/roof shell;
2. Blender-authored close-range facade geometry for windows, doors, storefronts, canopies, frames, sills, signs and other approach-distance structure;
3. the checked-in Poly Haven panorama and rectilinear reference plates as photographic evidence for facade composition/material/color placement;
4. PBR materials and facade-specific rectified textures where useful;
5. no final-quality raw equirectangular panorama projection stretched over arbitrary building walls.

The panorama remains a valid far photographic environment and reconstruction reference. It is not a substitute for modeled close-range facade depth, and transient panorama contents such as vehicles or pedestrians must not be baked onto permanent building surfaces.

Canonical source lock: `Hamburg`. Any code, workflow or document that reintroduces `Hansaplatz, Berlin` as the current reconstruction reference is inconsistent with this correction and must be fixed before quality closeout.
