# Hardware

The target deliverable is an EasyEDA Pro carrier PCB using the original modules. This folder currently contains source evidence and an intermediate reconstruction, not a production design.

## Source versus reconstruction

- [reference/original](reference/original/): 50 supplied source files, preserved byte-for-byte. Original Gerbers describe the old design; they are not redesign manufacturing files.
- [reconstruction](reconstruction/): recovered geometry, review boards, measurements and mappings.
- [easyeda](easyeda/): status of the native EasyEDA project.

## Which library should I open?

| Path under reconstruction/ | Purpose |
|---|---|
| OriginalCarrier.pretty/ | 11 reconstructed interfaces, 85 mapped pads. Mapping is reconstructed, not native-netlist-certified. |
| UnresolvedOriginal.pretty/ | 13 reference groups with unresolved electrical identity. HOLD names and hole IDs are intentional. |
| original-interface-review.kicad_pcb | The 11 mapped groups at original locations. |
| complete-geometry-review.kicad_pcb | All 24 groups at original locations, including held groups. |
| reconstructed-pin-map.csv | Pad-by-pad source coordinates, drill sizes, shapes and function labels. |
| remaining-footprint-checks.json | Outstanding mapping issues and held features. |
| independent-footprint-verification.json | Recorded independent CAD read-back result. |

All original hole positions, pitches and drilling geometry are retained in the reconstructed groups. Footprints currently contain pad geometry and identification text; body outlines, courtyards, 3D models and symbol bindings are incomplete.

## Important distinctions

The original design has four copper layers. The review boards use two copper layers solely to carry geometry, contain no electrical nets/tracks, and must not be ordered as PCBs. The original SMD navigation switch's two locating holes are represented; its electrical SMD pads are not yet reconstructed.

[Readiness](../docs/PRODUCTION_READINESS.md) · [Verification](../docs/VERIFICATION.md) · [Report](../docs/reports/complete-reconstruction-report.pdf)
