"""Check the saved final native archive, not just requested UI changes."""
from pathlib import Path
import json,zipfile,hashlib
R=Path(__file__).resolve().parents[1];O=R/'hardware/easyeda/step3-numbered'
def load(path):
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  text=z.read(next(n for n in z.namelist() if n.endswith('.epru'))).decode()
 docs={}
 for l in text.splitlines():
  if not l:continue
  h,v=map(json.loads,l.rstrip('|').split('||',1))
  if h['type']=='DOCHEAD':cur={'head':v,'rows':[]};docs[v['uuid']]=cur
  else:cur['rows'].append((h,v))
 return docs
def attrs(doc):
 out={}
 for h,v in doc['rows']:
  if h['type']=='ATTR':out.setdefault(v['parentId'],{})[v['key']]=v['value']
 return out
archive=O/'native-bound-review.epro2';docs=load(archive);previous=load(O/'native-components-review.epro2')
assert [v for h,v in docs['1d37e42034445c5d']['rows'] if h['type']=='COMPONENT']==[v for h,v in previous['1d37e42034445c5d']['rows'] if h['type']=='COMPONENT'], 'Final PCB placements changed'
page=docs['36ec364628955ba9'];components={a['Designator']:a for a in attrs(page).values() if a.get('Designator')}
cross=json.loads((O/'schematic-crosswalk.json').read_text())['components']
source={c['designator']:c for c in json.loads((R/'hardware/reconstruction/supplemental-schdoc-inventory.json').read_text())['components']}
bindings=json.loads((O/'native-footprint-bindings.json').read_text());checks=[]
for c in cross:
 ref=c['review_designator'];a=components[ref];uuid=bindings[ref]['footprint_uuid']
 assert a['Footprint']==uuid,(ref,a)
 sym=docs[a['Symbol']]
 actual={p['Pin Number']:p.get('Pin Name','') for p in attrs(sym).values() if 'Pin Number' in p}
 expected={p['Designator']:p.get('Name','') for p in source[c['source_designator']]['pins']}
 if ref=='T1':expected={'1':'G','2':'S','3':'D'}
 if ref=='LS1':expected={'1':'P','2':'M'}
 assert actual==expected,(ref,actual,expected)
 pads=[v for h,v in docs[uuid]['rows'] if h['type']=='PAD']
 originalpads=[v for h,v in previous[uuid]['rows'] if h['type']=='PAD']
 assert pads==originalpads,ref
 assert set(actual)==set(p['num'] for p in pads if p['num']),ref
 checks.append({'reference':ref,'footprint_uuid':uuid,'symbol_pins':actual,'numbered_pad_count':sum(bool(p['num']) for p in pads),'matching_pin_pad_sets':True,'geometry_unchanged_from_checked_archive':True})
assert len(checks)==40 and sum(c['numbered_pad_count'] for c in checks)==179
out={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'components':40,'symbol_pin_instances':179,'matched_footprint_bindings':40,'checks':checks,'scope':'Every final native symbol pin name/number, footprint UUID and electrical pad set checked. Does not prove retained Mk II circuit wires are suitable for Mk III or production.'}
(O/'native-binding-check.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS: final saved archive; 40 footprint bindings; 179 symbol pin/pad matches; all checked pad geometry retained.')
