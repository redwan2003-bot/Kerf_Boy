# GP7 and navigation correction checkpoint — 2026-11-03

The GP7 input conflict is removed in the saved EasyEDA schematic and partial PCB net assignments. Navigation locator holes now match the manufacturer drawing. **This is not a manufacturing release or full qualification.** Module/battery selection remains underway and no physical tests have run.

## Completed corrections

- RE1 pin 1 now connects to XIAO M1 pin 7 (D6 / GPIO43); RE1 pin 2 remains grounded. The MCP23008 INT connection was removed to free D6. INT and GP7 have explicit no-connect markers. Reset remains on 3.3 V in the schematic; the partial PCB reset net is now 3V3, correcting its source-board D6 assignment.
- The PCB assigns D6 to RE1.1 and M1.7. U1 pins 8 and 17 have no assigned PCB net. This geometry review still lacks complete circuit net transfer and routing.
- B2_LOC has 0.75 and 1.05 mm locator drills. All other 39 native footprint pad geometries, including the corrected Bourns encoder, are unchanged.

Firmware must configure GPIO43 as an input with pull-up, debounce the active-low button, disable UART TX use of that pin, and poll GP0–GP6 instead of using INT. These changes have not been integrated into or tested with application firmware. D8/D9/D10 microSD conflicts and the revision-specific D2/CS issue still require broader GPIO redesign.

## Correction to the previous report

Closer inspection of [E-Switch drawing N211128 rev D](https://configured-product-images.s3.amazonaws.com/2D/specs/JS1400BFQ.pdf) shows **1.85 mm is the inner-edge gap between signal lands 1 and 3**, not the grounding-pad short dimension. The drawing's grounding-land outer/inner spans imply (9.90 − 6.30) / 2 = 1.80 mm. The existing 2.00 × 1.80 mm grounding lands were correct and remain unchanged. The earlier grounding-pad deviation claim was wrong. Hole correction does not prove physical insertion or enclosure clearance.

## Verification performed

| Check | Result |
|---|---|
| Saved archive | ZIP integrity and SHA-256 recorded |
| Independent pcbnew/native geometry | 40 footprints, 181 pads; no errors; maximum discrepancy 0.000000766 mm against 0.0003 mm tolerance |
| Schematic/PCB library bindings | 40 bindings, 179 electrical pin/pad matches |
| Other footprints | All 39 other native pad geometries retained |
| Saved schematic connectivity | RE1.1 and M1.7 resolve to D6; U1.6 to 3V3; GP7/INT disconnected and explicitly marked no-connect |
| Native PCB assignments | D6 on RE1.1/M1.7; U1.6 at 3V3; U1.8/U1.17 unassigned |
| Navigation dimensions | 0.75/1.05 mm locators; 2.0 × 1.8 mm grounding lands retained |
| Repository checks | All 50 immutable original source hashes, independent footprint round-trip, Python syntax, local documentation links and whitespace checks passed |
| Native schematic DRC | Completed 13:40:34: 0 fatal, 0 errors, 1 warning, 4 information items |

The warning concerns four unconnected encoder/navigation shield terminals. Information concerns three unconventional designators and unnumbered locator holes. These findings were not suppressed. The digital connectivity check reads saved symbol pin positions, wire endpoints and labels; it is not physical continuity testing or complete circuit approval.

## Deliverables

- [Saved EasyEDA project](../../hardware/easyeda/qualification-fixes/native-gp7-navigation-review.epro2)
- [Native geometry verification](../../hardware/easyeda/qualification-fixes/native-fixes-geometry.json)
- [Connectivity and binding verification](../../hardware/easyeda/qualification-fixes/native-fixes-check.json)
- [Intermediate geometry board](../../hardware/easyeda/qualification-fixes/complete-fixed-review.kicad_pcb)
- [Native schematic check screenshot](../../hardware/easyeda/qualification-fixes/schematic-check.jpg)

## Remaining work

The user authorized exact compatible purchasable parts where original identity is missing, retaining through-hole connections and allowing necessary carrier footprint changes. Research began, but no replacement module/battery set is frozen or claimed to fit. The archive still contains original module footprints. Selections need power, interface, pin-order, body/keepout, availability and enclosure checks before implementation.

The user has no parts. Physical fit, contact-pair checks, bare-board continuity, power/temperature measurements and simultaneous-function tests remain **NOT RUN**. The physical acceptance procedure in the [qualification report](part-qualification-review.md) applies after circuit completion and prototype assembly.
