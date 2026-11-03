# Verification and reproduction

## Current manufacturer and native qualification checks

Run with KiCad Python: `scripts/build_qualified_encoder.py`, `scripts/check_part_qualification.py`, `scripts/check_qualified_native_geometry.py`, and `scripts/check_qualification_bindings.py`. The saved native archive is independently compared to the full corrected review board; all 181 pad checks pass within 0.0003 mm. Bindings retain 179 pin matches across 40 components, with 39 other footprints unchanged. Placement coordinates agree within 0.000001 mm (EasyEDA rounds the updated RE1 coordinates). These checks do not qualify the circuit or physical parts.

## Repository integrity (Python 3.10+, standard library only)

```sh
python scripts/verify_repository.py
```

This checks the 50 immutable source hashes, footprint counts, unique mapped pads, accounting of all round holes/slots, saved check results and local Markdown links. It does not run ERC/DRC or prove electrical connectivity.

## Independent CAD read-back

Use KiCad's Python interpreter with `pcbnew` available:

```sh
python scripts/check_footprint_roundtrip.py
```

On Windows, a typical installed interpreter is `C:/Program Files/KiCad/10.0/bin/python.exe`. The script parses the complete review board, measures pad and drill geometry against source coordinates and rejects duplicate matches. It does not rewrite the board into KiCad 10 format.

## Regenerate geometry (writes reconstruction outputs)

Create a virtual environment and install `scripts/requirements.txt`, then run from the repository root:

```sh
python scripts/recover_outline.py
python scripts/recover_through_holes.py
python scripts/build_original_footprints.py
python scripts/finish_geometry_review.py
python scripts/verify_repository.py
```

The checked-in validated DXF and historical report are reviewed artifacts; `recover_outline.py` regenerates the draft DXF and geometry JSON, not the independent validated-DXF conversion or the PDF report. Recovery scripts may create ignored review ZIPs. Review all generated diffs before committing.

Scripts use repository-relative paths. No local package cache or Python environment is bundled. The source snapshot is read-only input. Physical measurements, full net continuity, native EasyEDA conversion, ERC/DRC and bench testing are separate acceptance checks, currently pending.

## Future updates

Update the relevant files, README/status and CHANGELOG together. Run applicable checks, commit and push to `https://github.com/redwan2003-bot/Kerf_Boy.git`, then verify the remote commit. Never force-push to bypass concurrent changes.

## Source copper tracing

With the dependencies in `scripts/requirements.txt` installed:

```sh
python scripts/trace_external_copper.py
```

This source-specific parser joins GTL/GBL copper at plated holes and samples negative GP1/GP2 clearance geometry at 16 angular positions, at three offsets from the drill edge (0.02, 0.04 and 0.06 mm). It checks nine known power anchors and rejects conflicting anchored nets. The outputs include source hashes and a sensitivity list. It does not establish global internal-plane connectivity or assign manufacturer pin numbers. Missing labels and partial coverage are unresolved, not proof of no connection. See the [findings](reports/step-3-copper-verification.md).

## Supplemental SchDoc inventory

Install scripts/requirements.txt, then run `python scripts/extract_schdoc_inventory.py`. It checks record boundaries, declared counts, unique pin identifiers and 85 existing mapped identifier references. It reads explicit fields only; it does not compile a netlist or import into EasyEDA. The source hash is checked by repository verification.

## Native review update

Run `python scripts/check_easyeda_review.py` for saved native document counts and origin-name retention. `python scripts/prepare_easyeda_review_imports.py` regenerates the experimental imports (requires olefile). `python scripts/check_plane_topology.py` checks clipped internal-plane connectivity (requires Shapely). These do not prove native library geometry or electrical equivalence. See [current report](reports/easyeda-import-review.md).

After the user saved the archives, `check_native_library_geometry.py` passed under KiCad pcbnew Python for all 140 pads (see its scoped JSON report). `check_native_symbol_pins.py` passed for all 179 pin number/name instances. The archived project predates the outline correction; use the separately saved corrected PCB page.


## Current Step 3 checks

Run with the repository as working directory. `pcbnew` checks need KiCad 10's Python; the navigation check needs Shapely. No scripts certify production readiness.

```sh
python scripts/verify_repository.py
# With KiCad's Python:
python scripts/check_footprint_roundtrip.py
python scripts/check_step3_source_geometry.py
python scripts/check_step3_native_components.py
# With standard Python (Shapely needed for navigation):
python scripts/check_step3_navigation.py
python scripts/check_step3_bindings.py
```

`build_remaining_smd_footprints.py` regenerates the current 40-component input/library; `prepare_step3_schematic.py` regenerates the explicitly labelled binding-review import. They do not upload to EasyEDA. Native archives and screenshots are evidence from the actual UI, not generated substitutes. The report describes tolerances and open qualification work.
