# Hansaplatz Astra experiment

Branch: `exp/astra-hansaplatz-c0-20260911` only. No merge, PR or deployment.

Canonical place: Hansaplatz, Hamburg-St. Georg, 53.554451, 10.012056.
Official Hamburg LoD2-DE 2026 retains macro placement. Photographic references are
visual evidence only. Nearfield LoD3 coverage is unavailable; no search/substitution.

Baseline: 104499d07d69e30ad51cad01efc9fd7422bd0806. Browser run 34550829680
passed technically but screenshots show opaque polygonal tree crowns, uniformly
white exported facades, black window plates, invented sidewalk islands and floating
foundations. The attached before images are actual app screenshots from this run.

Execution: `.github/workflows/astra-hansaplatz.yml` runs Blender authoring and the
canonical exporter, measures the GLB, builds the app, executes the existing browser
regression and six-heading Day/Night photo-origin proof, then uploads evidence.
Generated assets are pushed to the experiment only after those checks pass.
No rebase or merge occurs. A concurrent remote update causes a safe push failure.

Iteration 1: exportable material values, existing CC0 paving maps at metric UV scale,
foundation-edge ground continuity, branched/leafed linden geometry at existing
landmark anchor positions. Previous draft geometry is archived outside export C0.
This is awaiting generated visual review; it is not a quality acceptance claim.
