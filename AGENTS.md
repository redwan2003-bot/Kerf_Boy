# Kerf_Boy project instructions

## Repository and publishing

The user explicitly designated https://github.com/redwan2003-bot/Kerf_Boy.git as the destination for every future update to this project. After each completed project update, update relevant documentation and checks, commit the related files, push to this remote, and verify the remote commit. Do not claim a push succeeded without verification. If authentication or branch rules block the push, preserve the commit and report the blocker. Never force-push or overwrite unrelated work.

Use Kerf_Keeb as the structural reference: hardware/, firmware/, mechanical/, docs/, clear READMEs and production-readiness documentation. Its design claims do not transfer to this project.

## Design constraints

- Preserve the exact original through-hole components and plug-in modules. No substitute vendor breakout or SMD replacement without an explicit scope change.
- hardware/reference/original/ is read-only source evidence; preserve its bytes and attribution.
- Do not turn unresolved hole identifiers into guessed electrical pin numbers.
- A geometry check is not electrical, physical-fit, ERC/DRC or manufacturing approval.
- The target editor is EasyEDA Pro. KiCad files here are intermediate review/import artifacts, not a change of target CAD tool.
- Keep mapped reconstruction and held reference-only footprints visibly separate.
- Update docs/PRODUCTION_READINESS.md and CHANGELOG.md when status changes.
- Do not include credentials, local dependency environments, caches or unrelated work.

## Checks

Run `python scripts/verify_repository.py`. For CAD geometry validation also run `scripts/check_footprint_roundtrip.py` with a Python interpreter providing KiCad's pcbnew module. Record which checks actually ran. Do not label firmware, native EasyEDA project or manufacturing files complete when absent.
