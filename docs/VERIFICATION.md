# Verification and reproduction

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
