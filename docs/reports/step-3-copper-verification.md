# Step 3 copper-verification addendum

Date: 2026-11-03. Status: **Step 3 incomplete; evidence improved, no fabrication release.**

## Step acceptance

1. Source audit: complete with recorded discrepancies; all 50 source fingerprints rechecked.
2. Digital mechanical reference: verified against supplied geometry. Physical fit and native EasyEDA import remain unverified. Calling all of Step 2 totally complete would overstate the evidence.
3. Footprints and pin mapping: 24 geometry groups cover 138 round component/locator holes plus two slots. The existing 85-pad mapping is unchanged. Held pad identifiers remain hole IDs because functional tracing alone does not establish manufacturer numbering.

## New findings

These are source-copper observations and schematic-based interpretations, not hardware continuity measurements.

| Region | Evidence | Interpretation / remaining limit |
|---|---|---|
| Encoder | H183 reaches D8; H185 reaches D7; H187 reaches MCP GP7. H184/H186 sample as ground. | Supports A, B, push contact and common functions; exact native numbering and shield identities still pending. |
| B0 | H156/H159 reach GP0; H157/H158 sample as ground. | Contact grouping established in source PCB; native part pad numbers pending. |
| B1 | H153/H154 reach GP1; H152/H155 sample as ground. | Contact grouping established in source PCB; native part pad numbers pending. |
| LEDs | H151 (LED1), H119 (LED2), H131 (LED3) sample as ground. | Consistent with schematic cathodes; exact original part numbering and physical polarity still require confirmation. |
| Two-pin audio region | H068 shares copper with S5 H076/H081; H069 samples as ground. S5 H077/H080 share copper with XIAO D2. | Supports identifying this region as BZ1, the switched buzzer, rather than the DFPlayer speaker. Component and symbol binding remain pending. |
| Power switch | H070/H075 reach switched VCC; H071/H074 reach battery positive. | Confirms source external contact groups; six physical leads versus three schematic terminals remains unresolved. |
| S2 H098 | GP2 copper samples are 13/16, 13/16 and 11/16 at offsets 0.02/0.04/0.06 mm. | Partial coverage; neither disconnected nor connected is certified by this sampling rule. Inspect the plane/thermal geometry before assignment. |

## Verification performed

- External layers produced 159 top and 146 bottom copper polygons, with 109 groups containing drill positions.
- Nine known power anchors matched the expected plane and excluded the opposite plane at the nominal sample radius.
- No conflicting anchored net labels were found in the reconstructed groups.
- Three-radius sampling flagged H098 for further inspection. Missing labels are **unresolved**, never proof of NC.
- Independent KiCad read-back and repository integrity checks were rerun for the existing geometry package.
- Source files remain unchanged. No alternate components or guessed electrical pin numbers were introduced.

## Limits and remaining work

The parser is specific to the supplied Gerber dialect. Local copper-ring sampling does not prove global plane continuity, component-internal connections, physical part identity or schematic equivalence. The original schematic and PCB-output dates differ. This evidence cannot replace a full native netlist comparison.

Remaining Step 3 work: resolve six-lead switch numbering and H098; establish exact encoder/shield and other held native pin identities; reconstruct and bind the navigation switch's six SMD contacts; confirm exact original part drawings; import into EasyEDA Pro and verify every symbol-to-footprint assignment. Physical fit remains a separate acceptance check.

The existing EasyEDA tab was found, but access failed with a timeout on `Emulation.setFocusEmulationEnabled`. No native import, ERC or DRC was verified during this update. The latest verified state remains a draft project, not a completed schematic or PCB.

## Reproduction and artifacts

Run `python scripts/trace_external_copper.py` with the repository requirements installed. See [verification instructions](../VERIFICATION.md).

- [External copper groups](../../hardware/reconstruction/external-copper-connectivity.json)
- [Plane samples, anchor checks and source hashes](../../hardware/reconstruction/four-layer-connectivity-check.json)
- [Production readiness](../PRODUCTION_READINESS.md)

This addendum supersedes the historical PDF only for the findings above. It does not mark the native EasyEDA design complete.
