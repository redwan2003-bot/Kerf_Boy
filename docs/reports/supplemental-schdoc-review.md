# Supplemental SchDoc inspection

Inspected 2026-11-03. **Symbol evidence recovered; Mk III equivalence and EasyEDA import remain unverified.**

## Verification

The user supplied `CHIPBOY_Mk_II.SchDoc` after the original audit. It is preserved separately from the immutable 50-file snapshot. Its title/revision fields are placeholders, so its metadata does not certify a Mk III revision.

- 225,792-byte source preserved with SHA-256 recorded in the linked inventory.
- 1,236 FileHeader records parsed to the exact stream boundary; declared count matched.
- 40 components and 179 pins extracted; every declared component pin count matched, with unique pin identifiers within each component.
- All 85 existing mapped pin identifiers exist in corresponding native symbols using an explicit reference crosswalk. This checks identifier presence, not nets or physical hole assignment.

## Findings

| Item | Native evidence | Remaining check |
|---|---|---|
| Five slide switches | Model SW_MHSS1104; pins 1/2 overlap at terminal named 1, pins 3/4 at terminal named 2, pins 5/6 at terminal named 3. | Per-hole numbering and linked footprint geometry. |
| Encoder | PEC12R-4217F-S0024; model XDCR_PEC12R-4217F-S0024; A/B/C, 1/2, SH1/SH2. | Physical slot/shield numbering and dimensional comparison. |
| LEDs | Pins A/C; model LED_WP7113ID. | Installed part and Mk III geometry reconciliation. |
| Buzzer | Pins P/N; model CUI_CMI-1295IC-0385T. | Installed part and footprint comparison. |
| B0/B1 | SKHHANA010; model SW_SKHHANA010; pins 1–4. | Exact physical pad numbering. |
| Navigation | JS1400BFQ; model SW_JS1400BFQ; pins 1–6 and SH1/SH2. | Complete SMD footprint and symbol binding. |

The overlapping switch pins explain why the PDF can appear to show three terminals. They do not establish two independent poles. Previous wording about a second pole was not a verified component characteristic.

## Revision differences

Module designators are descriptive strings rather than Mk III M1/U1/U4-style references. Switches use SW1–SW5. The provisional function/placement crosswalk is SW1 → S4 (power), SW5 → S5 (buzzer), SW4 → S3 (laser), SW3 → S1 (main flashlight), SW2 → S2 (camera flashlight). This is not a compiled netlist comparison.

The supplied schematic places R1 beside LED1; the prior Mk III reading assigns R1 to LED3. Several passive symbols link axial/radial through-hole models. These references must be reconciled before transferring footprints or reference names.

Linked model names establish library intent, not the actual installed component. No substitute part has been adopted. This extraction recovers symbol/model fields, not PCB pad geometry. H098 partial plane coverage also remains unresolved.

The [Bourns PEC12R datasheet](https://www.bourns.com/docs/product-datasheets/pec12r.pdf) supports the encoder family/order-code identification. A complete dimensional overlay and physical fit check have not been performed.

## Artifacts and status

- [Structured inventory and identifier checks](../../hardware/reconstruction/supplemental-schdoc-inventory.json)
- [Preserved supplemental schematic](../../hardware/reference/supplemental/CHIPBOY_Mk_II.SchDoc)
- [Verification instructions](../VERIFICATION.md)

This file resolves missing symbol labels and provides specific footprint-model references. Step 3 remains open for revision/net reconciliation, physical pad-number mapping, navigation SMD geometry and verified EasyEDA import. Held footprints retain their hole identifiers until those checks pass.
