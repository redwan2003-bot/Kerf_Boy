# GP7 and navigation correction checkpoint

See the [verification report](../../../docs/reports/gp7-navigation-checkpoint.md). The [saved EasyEDA project](native-gp7-navigation-review.epro2) contains corrected navigation binding and encoder-button reassignment. It remains an unrouted engineering review with partial PCB nets.

`QualifiedParts.pretty/` contains the corrected navigation footprint. `complete-fixed-review.kicad_pcb` is geometry-only intermediate input; native partial net changes are checked separately. The single-footprint board, ZIP and native page preserve the import trail. JSON checks inspect the saved native export. Historical source reconstruction remains unchanged.

Use KiCad Python to run `scripts/build_qualified_navigation.py`, `scripts/check_fixes_native_geometry.py` and `scripts/check_fixes_bindings.py`. Replacement-module selection and physical tests remain unfinished.
