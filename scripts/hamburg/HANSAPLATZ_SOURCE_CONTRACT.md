# Hansaplatz source contract

The checked-in photographic reference is Poly Haven asset `hansaplatz`, authored by Greg Zaal and licensed CC0-1.0.

Its published GPS target is **53.554451, 10.012056**, which is Hansaplatz in **Hamburg, Germany**. Berlin geometry is therefore not an acceptable geometry source for this scene and must not remain in the active C0 build once the Hamburg replacement is available.

Authoritative geometry target:

- Provider: Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV)
- Dataset: 3D-Gebäudemodell LoD3.0-HH Hamburg, Area1
- Capture basis: 2020 nadir and oblique aerial imagery
- Geometry: detailed roofscape beyond ordinary LoD2, including significant roof overhangs and rooftop structures
- Facades: official oblique-aerial textures at 20 cm privacy-compliant resolution
- CRS: ETRS89 / UTM zone 32N (EPSG:25832)
- License: Datenlizenz Deutschland Namensnennung 2.0
- Attribution: Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung
- Area1 archive: https://archiv.transparenz.hamburg.de/hmbtgarchive/HMDK/lod3-hh_area1_2023_12_14_180710_snap_1.zip

Build rules:

1. The Poly Haven panorama is the photographic camera/reference environment at its real Hamburg location; do not project it onto unrelated Berlin geometry.
2. Preserve Hamburg LoD3 geometry and its official facade texture references/materials when deriving the C0 subset.
3. Do not vendor the full Area1 archive. Extract and commit only the small source subset and textures needed around the reference camera, with hashes and provenance.
4. Primary-visible near-range additions must be reference-matched Blender-authored geometry or clearly licensed authored assets. Do not reintroduce guessed blockout objects.
5. Three.js remains runtime only: loading, streaming, movement, collision, Observer/Vision and rendering.
