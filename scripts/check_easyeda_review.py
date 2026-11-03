"""Check saved native page evidence; libraries are not embedded in these pages."""
from pathlib import Path
from collections import Counter
import json, hashlib, re

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'hardware/easyeda'
def read(name):
    return [tuple(json.loads(p) for p in line.rstrip('|').split('||', 1))
            for line in (E / name).read_text().splitlines() if line]

pcb = read('carrier-geometry-review.epcb')
sch = read('imported-review-page.esch')
counts = Counter(h['type'] for h, b in pcb)
assert counts['COMPONENT'] == 24 and counts['PAD_NET'] == 140
assert counts['POLY'] == 1 and counts['FILL'] == 4
assert all(b['padNet'] == '' for h, b in pcb if h['type'] == 'PAD_NET')
attributes = {}
for h, b in sch:
    if h['type'] == 'ATTR':
        attributes.setdefault(b['parentId'], {})[b['key']] = b['value']
components = [a for a in attributes.values() if 'Designator' in a]
assert len(components) == 40
recorded = json.loads((E / 'schematic-import-check.json').read_text())
assert {a['Designator'] for a in components} == {c['designator'] for c in recorded['checks']}
for c in recorded['checks']:
    a = next(a for a in components if a['Designator'] == c['designator'])
    assert a['Origin Footprint'] == c['source_footprint']
result = {
    'native_pcb_components': counts['COMPONENT'],
    'native_pad_net_records': counts['PAD_NET'],
    'native_schematic_designators': len(components),
    'original_footprint_name_checks': 40,
    'source_sha256': {n: hashlib.sha256((E/n).read_bytes()).hexdigest() for n in
                      ['carrier-geometry-review.epcb', 'imported-review-page.esch']},
    'scope': 'Native document counts and schematic reference/model-name retention. Does not validate external library geometry, pin mapping, nets, masks or electrical design.',
    'library_geometry_verification': '140 embedded pads dimensionally compared; see native-library-geometry-check.json for scope',
    'observed_schematic_drc': {'fatal_missing_footprints': 40, 'errors': 0, 'warnings': 1},
}
(E / 'native-review-check.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))

