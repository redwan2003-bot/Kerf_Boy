# Component qualification review — 2026-11-03

**Correction and superseding work:** [GP7/navigation checkpoint](gp7-navigation-checkpoint.md). GP7 is now disconnected from the button and locator holes are corrected. The earlier grounding-pad deviation claim was wrong: 1.85 mm is a signal-land gap, and original 2.0 x 1.8 mm grounding lands are correct. This report otherwise records the earlier review.

## Saved native verification

The [current project archive](../../hardware/easyeda/qualification/native-qualification-review.epro2) contains the corrected RE1 footprint in the PCB and schematic. Independent read-back passed all 181 pad checks (maximum difference 0.000000728 mm), all 40 bindings and 179 electrical pin matches. The other 39 footprint pad geometries are unchanged. Component placements agree within 0.000001 mm. Native binding DRC completed with 0 fatal, 0 errors, 1 warning and 4 information items; unresolved grounding and circuit issues remain. The full intermediate board and machine-readable checks are in the same qualification folder.

**Full qualification is not complete.** The user confirmed that the physical parts are not available. This review also found real design and part-identity issues that prevent approval independently of physical testing. Original-file conversion fidelity is not proof that the original footprint fits its labelled component.

## Corrected encoder

The [Bourns PEC12R drawing](https://www.bourns.com/docs/product-datasheets/pec12r.pdf), revision 07/21, page 4, specifies mounting slots 13.20 mm apart for PEC12R-4217F-S0024. The original recovered pattern measures 11.199876 mm. This is a 2.000124 mm discrepancy, not rounding.

The user explicitly selected the named Bourns part and authorized correcting the footprint. The new `Kerf_RE1_PEC12R4217F_S0024` footprint uses:

- Slot centers 13.20 mm apart, centered on the signal/switch pattern.
- Signal and switch spans of 5.00 mm and row separation of 14.50 mm.
- Finished round-hole target 1.10 mm, within the drawing's 1.00–1.20 mm range.
- Finished slot target 2.00 × 2.20 mm; the specified long-axis range is 2.10–2.30 mm.

The PCB fabricator must guarantee finished-hole tolerances inside those ranges. These are finished dimensions, not a prescription for the fabrication drill tool. Physical insertion, knob/shaft access and enclosure clearance remain untested. The original footprint is preserved as historical evidence; it is not approved for purchasing this Bourns part.

## Electrical qualification failure

Microchip's current [MCP23008 datasheet DS20001919I](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23008-and-MCP23008-Data-Sheet-DS20001919.pdf), pages 1 and 4, specifies GP7 as output-only for MCP23008. The original copper connectivity joins U1 pin 17 / H113 to encoder push pin 1 / H187 on GP7. The reference assignment therefore fails the current input-capability check. Move the encoder input to an input-capable pin during the GPIO redesign; do not simply change the symbol type or hide the warning.

The same manufacturer's PDIP pin pitch/formed-row nominal dimensions agree with the reconstructed 2.54/7.62 mm pattern. That dimensional result does not resolve the GP7 fault or freeze the ordering suffix.

## Other drawing checks

| Components | Evidence and result | Remaining requirement |
|---|---|---|
| B0, B1 | [Alps SKHHANA010](https://tech.alpsalpine.com/e/products/detail/SKHHANA010/) and [drawing 4](https://tech.alpsalpine.com/cms.media/product_catalog_ta_01_skhh_en_bf15276fa8.pdf): existing 6.5024 × 4.5212 mm hole grid and 1.016 mm holes lie within the specified 6.5 ±0.1, 4.5 ±0.1 and 1.0 ±0.05 mm ranges. Body/actuator envelope is 6 × 6 × 9.5 mm. | Confirm purchased part, fabrication tolerance and enclosure actuator clearance. |
| B2_LOC | [E-Switch JS1400BFQ drawing N211128 rev D](https://configured-product-images.s3.amazonaws.com/2D/specs/JS1400BFQ.pdf) identifies a 7.7 × 7.4 mm body, 5 mm height, common pin 5, center pin 2 and two grounding terminals. | Original locator holes are 0.8001/1.100074 mm versus recommended 0.75/1.05; the 2.0 x 1.8 mm grounding lands are correct (the earlier 1.85 mm interpretation was wrong). Preserve as recorded deviations until fit/process review; do not claim exact recommended-land-pattern compliance. |
| S1–S5 | All five upstream native footprint names are `SW_MHSS1104`. The [APEM-authored MHSS sheet](https://www.mouser.com/datasheet/2/26/APEM_Microminiature_slide_switches_MHSS_MS-3396147.pdf) gives 300 mA at 6 VDC for that family. | A library name is identification evidence, not proof of the installed part. Confirm exact switch geometry/contact pairs and load/inrush. Do not approve battery/audio load switching without a current budget. |
| M1 | [Seeed's Sense SD documentation](https://wiki.seeedstudio.com/xiao_esp32s3_sense_filesystem/) reserves D8/D9/D10 for SCK/MISO/MOSI. The reference carrier also uses these signals for other functions. | Freeze base/expansion revision and resolve the concurrent pin allocation. The SD chip-select must be checked against that exact revision. |
| T1 | [AO3400A manufacturer data](https://www.aosmd.com/sites/default/files/res/data_sheets/AO3400A.pdf) and the Mk III schematic support G1/S2/D3. | Exact laser load, gate drive, power dissipation and board temperature still need qualification. |

The [40-component qualification register](../../hardware/easyeda/qualification/part-qualification.json) records each reference, its evidence, status and required closure. No part is labelled physically tested. There are 28 passing dimensional subchecks and one confirmed failure of the historical encoder pattern; the corrected encoder is checked separately.

## Requirements that cannot be closed from the supplied files

Exact revisions/order codes remain necessary for the OLED, BNO055/BME280/TOF/GPS breakouts, DFPlayer, headers, LEDs, buzzer, speaker and SMD passive parts. Their source footprints do not establish every body dimension, electrical rating or purchasing identity. The battery also needs a model, chemistry, capacity, protection and charging limits. Full courtyards, access/antenna keepouts and the enclosure stack depend on these choices.

The reference schematic still needs J2/buzzer polarity reconciliation, shield grounding and a complete power/GPIO redesign. Consequently the native binding DRC result is not an electrical approval. No manufacturing release or physical-test success is claimed.

## Physical acceptance procedure — not executed

1. Record manufacturer, exact model/revision and supplier for every purchased part. Check them against the qualification register before soldering.
2. Check lead pitch, maximum lead dimensions, body/actuator height, connectors and polarity against the selected drawing. Compare a calibrated 1:1 print or an unpopulated prototype; do not force leads into mismatched holes.
3. Verify switch contact pairs with power disconnected, including every slide position, tactile contact group, encoder push and navigation direction. Verify encoder A/B phase and the selected shield-to-case connection.
4. Verify bare-board continuity and absence of shorts against the final approved netlist. This requires the completed circuit and manufactured board, neither of which this geometry review supplies.
5. After the power architecture and ratings are approved, bring up with a current-limited bench supply. Measure rails, load steps and temperature. Validate battery charge/protection with the actual specified battery and charger limits.
6. Exercise Wi-Fi/camera/microSD, GPS, display, sensors, controls and audio concurrently. Record results and resolve failures before production release.

Each test needs an actual measured result, instrument/setup, date and pass/fail decision. A blank test sheet or a simulation is not a physical test result.
