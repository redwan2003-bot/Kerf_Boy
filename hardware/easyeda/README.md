# EasyEDA Pro review files

[Open existing project](https://pro.easyeda.com/editor#id=987575100d2f4542bfc9780160616df2)

Two review documents now exist in this project: `CHIPBOY_Mk_II_ascii_review` under `schdoc-ascii-review`, and `carrier-geometry-review`. The original Board1 scaffold is separate.

| File | Purpose |
|---|---|
| CHIPBOY_Mk_II_ascii_review.SchDoc / schdoc-ascii-review.zip | Experimental ASCII conversion of the supplied binary Mk II schematic for review import |
| carrier-geometry-review.kicad_pcb / .zip | Corrected geometry import input, with exactly one copy of the existing outline |
| imported-review-page.esch | Native schematic page read from EasyEDA File Source |
| carrier-geometry-review.epcb | Native PCB page read back after correcting the duplicate outline |
| *check.json | Scoped conversion and count evidence |

The native page files reference library UUIDs; they are **not standalone complete project archives**. The user completed both downloads. `native-review-before-outline-fix.epro2` contains the full review project and libraries before the outline correction; `schematic-review.epro2` contains the earlier schematic review export. The historical project archive must be used with the corrected native PCB page until a fresh archive is exported.

24 carrier groups and 140 pad references are present. The input has 138 round component/locator pads and two slots; embedded-library coordinates, pad sizes, drill dimensions and identifiers now match the reconstruction for all 140 pads. Slot orientation and rendered masks still require verification. The board has no connected circuit or routing. Held Hxxx/SLOT identifiers remain reference identifiers, not resolved component pin numbers.

The schematic retains all 40 designators and origin footprint names. Its native check reports 40 missing-footprint fatal findings and one shield-pin warning. Archive inspection confirms all 179 per-instance pin numbers/names survived; BME280 and TOF400C retain distinct symbols. No electrical-equivalence claim is made.

See the [full current report](../../docs/reports/easyeda-import-review.md). Do not fabricate these review files.
