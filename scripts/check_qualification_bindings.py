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

Q=R/'hardware/easyeda/qualification'
archive=Q/'native-qualification-review.epro2'
docs=load(archive);old=load(O/'native-bound-review.epro2')
page='1d37e42034445c5d';sch='36ec364628955ba9'
placements={h['id']:v for h,v in docs[page]['rows'] if h['type']=='COMPONENT'}
previous_placements={h['id']:v for h,v in old[page]['rows'] if h['type']=='COMPONENT'}
assert set(placements)==set(previous_placements)
for key,c in placements.items():
 b=previous_placements[key]
 assert all(abs(c[k]-b[k])*.0254<.000001 for k in ['x','y']),key
 assert c['angle']==b['angle'] and c['layerId']==b['layerId'],key
 assert c['attrs']['Unique ID']==b['attrs']['Unique ID'],key

current={a['Designator']:a for a in attrs(docs[sch]).values() if a.get('Designator')}
previous={a['Designator']:a for a in attrs(old[sch]).values() if a.get('Designator')}
pcba={a['Designator']:a for a in attrs(docs[page]).values() if a.get('Designator')}
checks=[];pins=0
assert set(current)==set(previous) and len(current)==40
for ref,a in current.items():
 before=previous[ref];uuid=a['Footprint']
 assert {k:v for k,v in a.items() if k!='Footprint'}=={k:v for k,v in before.items() if k!='Footprint'},ref
 assert docs[a['Symbol']]['rows']==old[before['Symbol']]['rows'],ref
 if ref=='RE1':assert uuid=='7248999c7ca7edd8'
 else:
  assert uuid==before['Footprint'],ref
  assert [v for h,v in docs[uuid]['rows'] if h['type']=='PAD']==[v for h,v in old[uuid]['rows'] if h['type']=='PAD'],ref
 b=pcba[ref];meta=next(v for h,v in docs[b['Device']]['rows'] if h['type']=='META')
 assert meta['attributes']['Footprint']==uuid,ref
 symbol={p['Pin Number'] for p in attrs(docs[a['Symbol']]).values() if 'Pin Number' in p}
 padnums={v['num'] for h,v in docs[uuid]['rows'] if h['type']=='PAD' and v['num']}
 assert symbol==padnums,ref
 pins+=len(symbol);checks.append({'reference':ref,'footprint_uuid':uuid,'matching_pin_pad_sets':True})
assert pins==179
result={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'components':40,'symbol_pin_instances':179,'unchanged_other_footprints':39,'placements_unchanged':True,'checks':checks,'scope':'Saved native geometry, binding and placement checks only; full qualification remains open.'}
(Q/'native-qualification-check.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: corrected RE1 bound in PCB and schematic; 39 other footprints unchanged; 40 bindings, 179 pins, placements retained.')
