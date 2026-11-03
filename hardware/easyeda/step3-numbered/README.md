# Complete component and binding review

Current review, 2026-11-03. **Not manufacturing-ready.** See the [engineering report](../../../docs/reports/step-3-component-binding-report.md).

| Artifact | Purpose |
|---|---|
| native-bound-review.epro2 | Latest complete saved EasyEDA project, including 40 bindings and embedded libraries |
| native-components-review.epro2 | Earlier checkpoint after importing all 40 footprints, before new binding sheet |
| complete-component-review.epcb / binding-review.esch | Native page readback; libraries are in the full archive |
| complete-component-review.kicad_pcb / .zip | Complete 40-component geometry import input; KiCad is an intermediate format |
| KerfOriginal.pretty/ | Forty reconstructed original-geometry footprints |
| numbered-carrier-review.kicad_pcb / .zip | Intermediate 24-group reconstruction with navigation SMD pads |
| Kerf_Step3_Binding_Review.SchDoc / step3-binding-review.zip | Derived reference schematic for checking bindings, not approved circuit design |
| schematic-crosswalk.json | Source-to-review reference changes and explicit circuit limitations |
| pin-number-evidence.json | Rigid-transform comparison for 51 formerly held round pads |
| smd-source-check.json / source-geometry-check.json | Gerber aperture evidence and independent input readback |
| navigation-source-check.json | Navigation copper/mask/paste comparison |
| native-component-check.json / native-binding-check.json | Independent native-library geometry and final archive binding results |
| native-footprint-bindings.json | Actual footprint UUIDs from the saved native archive |
| binding-review-drc.jpg / native-drc-observation.txt | Visible native schematic check evidence |

The full archive retains earlier review pages and the original Board1 scaffold. Select `Kerf_Step3_Binding_Review` for the current binding review and `complete-component-review` for the geometry. The reference circuit has known revision discrepancies; footprint binding does not approve those wires. Body outlines, complete courtyards, physical fit, ratings, routing and manufacturing approval remain outside the verified result.
