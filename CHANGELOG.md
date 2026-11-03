# Change history

## 2026-11-03 - Complete digital component and binding review

- Recover separately attributed author-native Mk II PCB evidence whose companion schematic exactly matches the supplied SchDoc.
- Resolve 51 formerly held round-pad numbers; preserve original Mk III holes/slots and all original through-hole modules.
- Add eight navigation SMD pads and 16 remaining Mk III SMD footprints, reaching 40 components / 179 electrical pads plus two locator holes.
- Verify original source geometry and native EasyEDA pad geometry, angles, slot axes, plating and SMD mask/paste expansion.
- Add a separate 40-component binding-review sheet with Mk III AO3400A and speaker pin labels; verify the saved native archive and all 179 pin/pad matches.
- Record 0 fatal errors, 0 errors and 1 shield warning. Keep part qualification, body/courtyard completion and circuit redesign explicitly open.


## 2026-11-03 - Saved native archive verification

- Preserve the two user-saved native archives, labelling the full project archive as predating the outline correction.
- Compare all 140 embedded pad positions, sizes, drill dimensions and identifiers with the independently parsed input; all pass.
- Verify all 179 symbol pin number/name instances across 40 components; all pass, including separate BME280 and TOF400C symbols.
- Preserve native page byte identity across Git checkouts.

## 2026-11-03 - Native EasyEDA review imports

- Import the supplemental schematic and reconstructed carrier into the existing EasyEDA project.
- Preserve native page source and screenshots; check 40 schematic references and 24 PCB groups / 140 pad references.
- Find and remove a duplicated outline in the import copy and native PCB; read back one outer outline and four cutouts.
- Record 40 missing-footprint fatal findings, one shield-pin warning and library-name collision risks.
- Resolve H098 source-plane continuity to 3V3 using clipped copper polygons.
- Keep Step 3 incomplete; archive/library, physical numbering and electrical checks remain open.

## 2026-11-03 - Supplemental native schematic

- Preserve the explicitly supplied Mk II SchDoc separately from the original snapshot.
- Extract and check 1,236 records, 40 components, 179 pins and footprint-model names.
- Confirm all 85 existing mapped pin identifiers exist in corresponding symbols.
- Recover overlapping switch pin pairs and encoder/LED/buzzer labels.
- Record revision differences; no unverified physical pad assignments promoted.

## 2026-11-03 - Step 3 copper-trace evidence

- Add reproducible external-copper connectivity and internal-plane sampling.
- Check nine known power anchors and record no conflicting anchored nets.
- Record encoder/button functions, LED ground terminals and buzzer identity evidence.
- Flag H098 partial plane coverage; do not infer an unused or disconnected pad.
- Preserve all held footprint pin identifiers; exact numbering and native EasyEDA checks remain open.

## 2026-11-03 - Repository foundation

- Adopt Kerf_Boy as the persistent publishing destination for future project updates.
- Follow Kerf_Keeb's hardware, firmware, mechanical and documentation organization.
- Preserve the 50-file source snapshot and its fingerprints.
- Add 24 reconstructed geometry groups, 85-pad mapping records and independent checks.
- Include the complete five-page engineering report and mechanical previews.
- Separate unresolved reference footprints and superseded component research.
- Add portable recovery scripts, integrity verification and explicit production holds.
- Native EasyEDA import, full electrical mapping and production design remain unfinished.
