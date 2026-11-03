# Manufacturer qualification review

[Download current EasyEDA project](native-qualification-review.epro2). This saved archive contains the corrected RE1 in both the full PCB and binding schematic. `complete-qualified-review.kicad_pcb` is the full intermediate review board. `native-qualification-geometry.json` verifies all 181 pads; `native-qualification-check.json` verifies 40 bindings, 179 pin matches and preservation of the other 39 footprints. Placement coordinates are retained within 0.000001 mm. Native schematic DRC completed with 0 fatal, 0 errors, 1 warning and 4 information items; this is not circuit approval.

See the [qualification report](../../../docs/reports/part-qualification-review.md). Full qualification remains open: the user has no physical parts, identities/ratings remain unresolved, and an MCP23008 GP7 input assignment fails the current manufacturer specification.

`QualifiedParts.pretty/Kerf_RE1_PEC12R4217F_S0024.kicad_mod` is the user-authorized correction for that exact Bourns encoder. The folder name identifies manufacturer-based work, not complete product certification. `qualified-encoder-review.kicad_pcb` / `.zip` provide a reproducible EasyEDA import and `qualified-encoder-review.epcb` is its native page. The historical original geometry is unchanged in `../step3-numbered/`.

`part-qualification.json` covers all 40 components and external battery/load holds. Generate it with KiCad's Python using `scripts/check_part_qualification.py`. `scripts/build_qualified_encoder.py` regenerates the corrected encoder input without modifying source evidence.
