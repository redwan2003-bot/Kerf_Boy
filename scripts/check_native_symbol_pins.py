"""Check per-instance symbol pin number/name retention in native archive."""
from pathlib import Path
import json,zipfile
R=Path(__file__).resolve().parents[1];E=R/'hardware/easyeda'
with zipfile.ZipFile(E/'native-review-before-outline-fix.epro2') as z:
 data=z.read(next(n for n in z.namelist() if n.endswith('.epru'))).decode()
docs={}
for line in data.splitlines():
 if not line:continue
 h,b=(json.loads(p) for p in line.rstrip('|').split('||',1))
 if h['type']=='DOCHEAD':cur={'head':b,'rows':[]};docs[b['uuid']]=cur
 else:cur['rows'].append((h,b))
def attrs(doc):
 out={}
 for h,b in doc['rows']:
  if h['type']=='ATTR':out.setdefault(b['parentId'],{})[b['key']]=b['value']
 return out
page=docs['6edbb0a5db6d0bd1'];components={a['Designator']:a for a in attrs(page).values() if 'Designator' in a}
source=json.loads((R/'hardware/reconstruction/supplemental-schdoc-inventory.json').read_text())
checks=[]
for c in source['components']:
 a=components[c['designator']];sym=docs[a['Symbol']]
 pins={p['Pin Number']:p.get('Pin Name','') for p in attrs(sym).values() if 'Pin Number' in p}
 original={p['Designator']:p.get('Name','') for p in c['pins']}
 checks.append({'designator':c['designator'],'source_pins':original,'imported_pins':pins,'match':pins==original})
result={'components':len(checks),'source_pin_instances':sum(len(c['source_pins']) for c in checks),'passed':sum(c['match'] for c in checks),'checks':checks,'scope':'Pin number/name retention only. Does not prove wire connectivity, electrical pin types or physical hole mapping.'}
(E/'native-symbol-pin-check.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:v for k,v in result.items() if k!='checks'})
print('Differences:',[c for c in checks if not c['match']])
