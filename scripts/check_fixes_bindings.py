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
  header,payload=l.split('||',1)
  if not payload.rstrip('|'):continue # Native deletion tombstone
  h,v=json.loads(header),json.loads(payload.rstrip('|'))
  if h['type']=='DOCHEAD':cur={'head':v,'rows':[]};docs[v['uuid']]=cur
  else:cur['rows'].append((h,v))
 return docs
def attrs(doc):
 out={}
 for h,v in doc['rows']:
  if h['type']=='ATTR':out.setdefault(v['parentId'],{})[v['key']]=v['value']
 return out

Q=R/'hardware/easyeda/qualification-fixes'
archive=Q/'native-gp7-navigation-review.epro2'
docs=load(archive);old=load(R/'hardware/easyeda/qualification/native-qualification-review.epro2')
page='1d37e42034445c5d';sch='36ec364628955ba9'
a={v['Designator']:v for v in attrs(docs[sch]).values() if v.get('Designator')}
b={v['Designator']:v for v in attrs(old[sch]).values() if v.get('Designator')}
pcba={v['Designator']:v for v in attrs(docs[page]).values() if v.get('Designator')}
assert set(a)==set(b) and len(a)==40
count=0
for ref,v in a.items():
 uuid=v['Footprint']
 assert docs[v['Symbol']]['rows']==old[b[ref]['Symbol']]['rows'],ref
 if ref=='B2_LOC':assert uuid=='78b8685372ea381c'
 else:
  assert uuid==b[ref]['Footprint'],ref
  assert [v for h,v in docs[uuid]['rows'] if h['type']=='PAD']==[v for h,v in old[uuid]['rows'] if h['type']=='PAD'],ref
 meta=next(v for h,v in docs[pcba[ref]['Device']]['rows'] if h['type']=='META')
 assert meta['attributes']['Footprint']==uuid,ref
 pins={p['Pin Number'] for p in attrs(docs[v['Symbol']]).values() if 'Pin Number' in p}
 padnums={p['num'] for h,p in docs[uuid]['rows'] if h['type']=='PAD' and p['num']}
 assert pins==padnums,ref
 count+=len(pins)
assert count==179
# Independent graph of saved native schematic wire endpoints and labels.
rows=docs[sch]['rows'];at=attrs(docs[sch]);comps={h['id']:v for h,v in rows if h['type']=='COMPONENT'}
lines=[v for h,v in rows if h['type']=='LINE'];graph={};labels={}
def point(x,y):return(round(x,5),round(y,5))
def addlabel(p,s):labels.setdefault(p,set()).add(s)
for line in lines:
 p=point(line['startX'],line['startY']);q=point(line['endX'],line['endY'])
 graph.setdefault(p,set()).add(q);graph.setdefault(q,set()).add(p)
 net=at.get(line.get('lineGroup'),{}).get('NET')
 if net:addlabel(p,net)
for id,c in comps.items():
 v=at.get(id,{})
 if not v.get('Designator') and v.get('Name'):addlabel(point(c['x'],c['y']),v['Name'])
def network(start):
 seen=set();todo=[start]
 while todo:
  p=todo.pop()
  if p in seen:continue
  seen.add(p);todo.extend(graph.get(p,set())-seen)
 return seen,set().union(*(labels.get(p,set()) for p in seen))
def terminal(ref,num):
 id,v=next((id,v) for id,v in at.items() if v.get('Designator')==ref);c=comps[id]
 assert c['rotation']==0 and not c['isMirror']
 sym=docs[v['Symbol']];pa=attrs(sym)
 pin=next(p for h,p in sym['rows'] if h['type']=='PIN' and pa[h['id']]['Pin Number']==num)
 return point(c['x']+pin['x'],c['y']+pin['y'])
assert network(terminal('RE1','1'))[1]=={'D6'}
assert network(terminal('M1','7'))[1]=={'D6'}
assert network(terminal('U1','6'))[1]=={'3V3'}
assert not network(terminal('U1','17'))[1] and not network(terminal('U1','8'))[1]
assert {v['parentId'] for h,v in rows if h['type']=='ATTR' and v.get('key')=='NO_CONNECT' and v.get('value')=='yes'} >= {'ie235-ie29','ie235-ie41'}
assert not any(v.get('value')=='GP7' for h,v in rows if h['type']=='ATTR' and v.get('key') in ['NET','Name'])
# PCB partial net assignments: no routing/full schematic transfer claimed.
padnets={tuple(json.loads(h['id'])[1:3]):v['padNet'] for h,v in docs[page]['rows'] if h['type']=='PAD_NET'}
assert padnets[('ie55','1')]==padnets[('ie0','7')]=='D6'
assert padnets[('ie5','6')]=='3V3'
assert padnets[('ie5','8')]==padnets[('ie5','17')]==''
pads=[v for h,v in docs[a['B2_LOC']['Footprint']]['rows'] if h['type']=='PAD']
assert sorted(round(v['hole']['width']*.0254,5) for v in pads if not v['num'])==[.75,1.05]
shield=[v for v in pads if v['num'].startswith('SH')]
assert all(sorted(round(v['defaultPad'][k]*.0254,5) for k in ['width','height'])==[1.8,2.0] for v in shield)
result={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'components':40,'symbol_pin_instances':179,'unchanged_other_footprints':39,'gp7_button_conflict_removed':True,'encoder_button':'M1 pin 7 / D6 / GPIO43; configure input pull-up, disable UART TX on this pin','expander':'RESET to 3V3; INT and GP7 deliberately unconnected; poll GP0-GP6','navigation_locator_drills_mm':[.75,1.05],'grounding_land_size_mm':[2,1.8],'scope':'Native saved-file checks; partial PCB nets only. Full routing/circuit/firmware and hardware qualification remain unfinished.'}
(Q/'native-fixes-check.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 40 bindings/179 pins; 181 pads checked separately; GP7 isolated; RE1.1 and M1.7 on D6; reset 3V3; 0.75/1.05 mm navigation locators.')

