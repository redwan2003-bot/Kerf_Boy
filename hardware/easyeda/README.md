# EasyEDA Pro

[Existing draft project](https://pro.easyeda.com/editor#id=987575100d2f4542bfc9780160616df2)

The project was created with schematic/PCB scaffolding and a draft note. No completed circuit, routed PCB or verified native footprint import is present in the recorded work. Browser attachment timed out during the last attempt. No native `.epro` or `.elibz` export is included.

## Planned conversion and acceptance

EasyEDA Pro documents [KiCad import](https://prodocs.easyeda.com/en/import-export/import-kicad/) for versions below 10. The intermediate files here use KiCad 5.1 syntax and were read by KiCad 10 without rewriting their source format.

1. Import the review/library files using EasyEDA's supported import workflow into a review area.
2. Compare pad count, IDs, shape, pitch, drill diameter, routed slots, masks and board dimensions with the CSV/JSON evidence.
3. Resolve held electrical identities before symbol binding. Do not treat Hxxx or SLOT identifiers as finalized pin numbers.
4. Bind the correct symbol/footprint combinations, save and reopen the native project.
5. Commit native exports and fresh conversion verification evidence here when completed.

Successful intermediate CAD parsing is not proof of a successful EasyEDA conversion.
