# Night Intersection C0 authored third-party model sources

All models in this pass are fetched from Poly Haven through its public `/files/{id}` API during the Blender authoring build. The build uses the 1K glTF variant, verifies Poly Haven-provided MD5 hashes when present, imports the models into Blender, packs their dependencies into the canonical `.blend`, and exports one repository-hosted C0 GLB. Production does not request these sources from Poly Haven.

Every model below is released under **CC0-1.0** by Poly Haven.

| Asset ID | Role in C0 | Creator(s) | Canonical source |
| --- | --- | --- | --- |
| `street_lamp_02` | four street-light fixtures | Josh Dean | https://polyhaven.com/a/street_lamp_02 |
| `modular_street_seating` | two urban seating groups | Stuart Attenborrow | https://polyhaven.com/a/modular_street_seating |
| `utility_box_02` | west-side utility cabinet | James Ray Cock | https://polyhaven.com/a/utility_box_02 |
| `metal_trash_can` | east-side street bin | GurJas Studios | https://polyhaven.com/a/metal_trash_can |
| `covered_car` | parked north-side vehicle | MP | https://polyhaven.com/a/covered_car |
| `jacaranda_tree` | two street trees | Rico Cilliers; Rob Tuytel | https://polyhaven.com/a/jacaranda_tree |

The generated build cache retains a machine-readable `manifest.json` per asset containing Poly Haven's current authorship metadata, `files_hash`, selected resolution, source URLs, MD5 values, downloaded-file SHA-256 values, and rewritten local glTF SHA-256. The cache is intentionally not committed because the canonical packed Blender source and runtime GLB are the repository artifacts.

CC0 does not require attribution. These records are retained for provenance, reproducibility, and future replacement audits.
