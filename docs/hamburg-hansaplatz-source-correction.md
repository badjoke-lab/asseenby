# Hansaplatz source correction

The Poly Haven `hansaplatz` panorama used by Explore 3D is located at Hansaplatz, Hamburg-St. Georg, Germany, not Berlin.

Canonical reference coordinates: `53.554451, 10.012056`.

The C0 geometry source is therefore aligned to the official Hamburg LoD2-DE 2026 dataset from Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV), EPSG:25832, licensed `dl-de-by-2.0`.

The reproducible local subset in `assets-src/blender/night-intersection/hamburg-lod2/` contains 113 buildings and 339 semantic objects within the selected 170 m radius. The generated Blender source and runtime GLB are rebuilt from this Hamburg geometry before browser validation.

The former Berlin LoD2 + Hamburg panorama combination was a source-location mismatch and must not be reintroduced.
