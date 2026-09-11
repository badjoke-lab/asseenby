# Hansaplatz Astra experiment

Branch: `exp/astra-hansaplatz-c0-20260911` only. No merge or PR. On 2026-09-11 the user selected this branch as disposable Cloudflare Production; branch pushes are authorized to update the public site. Do not change Cloudflare branch configuration.

Canonical place: Hansaplatz, Hamburg-St. Georg, 53.554451, 10.012056.
Official Hamburg LoD2-DE 2026 retains macro placement. Photographic references are
visual evidence only. Nearfield LoD3 coverage is unavailable; no search/substitution.

Baseline: 104499d07d69e30ad51cad01efc9fd7422bd0806. Browser run 34550829680
passed technically but screenshots show opaque polygonal tree crowns, uniformly
white exported facades, black window plates, invented sidewalk islands and floating
foundations. Before screenshots are retained in the workflow artifact for this run.

Execution: `.github/workflows/astra-hansaplatz.yml` runs Blender authoring and the
canonical exporter, measures the GLB, builds the app, executes the existing browser
regression and six-heading Day/Night photo-origin proof, then uploads evidence.
Generated assets are pushed to the experiment only after those checks pass.
No rebase or merge occurs. A concurrent remote update causes a safe push failure.

Iteration 1: exportable material values, existing CC0 paving maps at metric UV scale,
foundation-edge ground continuity, branched/leafed linden geometry at existing
landmark anchor positions. Previous draft geometry is archived outside export C0.
Generated HEAD a55cb0d4c16e4834f8708fc13d4917d3a4398352, run 34551409891. Build and both browser scripts passed. The screenshots confirm improved trees/ground but facades still read as repeated applied dark panels. GLB: 20,881,012 bytes; 264,410 triangles; 584,565 vertices; 386 meshes; 37 materials. This is not a quality acceptance claim.

Iteration 2 is in visual review: exact source wall polygons are subdivided into masonry with apertures, replacing the old applied facade buckets. Deep reveals, sash and shop joinery, sills, floor hierarchy and profiled eaves use building-specific profiles. Window positions and ornament remain reference-informed approximations, not cadastral measurements. Roof and wall boundary registration remain LoD2. Current first pass prioritizes origin-visible faces within 108 m. QR2 stays open until actual browser results support acceptance.

First facade result: commit 9da437719e523a9a588b2933b7f1eaddd1c05209,
generated commit 1d92358c8e713f8e4c8e9147652ede5e1c852c98, run 34569778332.
Both browser scripts and build passed. 33 source wall faces / actual apertures;
22,345,656 bytes, 297,348 triangles, 639,423 vertices, 379 meshes/primitives,
25 materials and three 1024 px paving maps. Forward and turned screenshots show
narrower sash proportions and shop hierarchy, but surfaces remain flat and Night
lost too many illuminated interiors. A second visual correction adds material-scale
brick/plaster maps, dressed bases, quoins, selected lintels, blinds and restrained
interior emission. Day reflection/shadow correction is limited to this scene.
The direct public browser failed to create WebGL; the existing GitHub-hosted
Chromium path additionally tests the public deployment and verifies the actual
loaded GLB response hash against the generated asset. No local Blender rebuild.
