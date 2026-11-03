"""Compare native archive footprints against independently parsed KiCad input."""
from pathlib import Path
import pcbnew,json,zipfile,math,hashlib
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'hardware/easyeda'
def rows(text):
 return [tuple(json.loads(p) for p in l.rstrip('|').split('||',1)) for l in text.splitlines() if l]
archive=E/'native-review-before-outline-fix.epro2'
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 data=z.read(next(n for n in z.namelist() if n.endswith('.epru'))).decode()
docs={}
for h,b in rows(data):
 if h['type']=='DOCHEAD':current={'head':b,'rows':[]};docs[b['uuid']]=current
 else:current['rows'].append((h,b))
device_ids={v['parentId']:v['value'] for k,v in docs['d9e9d23f0604e918']['rows'] if k['type']=='ATTR' and v['key']=='Device'}
b=pcbnew.LoadBoard(str(E/'carrier-geometry-review.kicad_pcb'))
expected=[p for fp in b.GetFootprints() for p in fp.Pads()]
seen=set();checks=[];errors=[]
for h,c in rows((E/'carrier-geometry-review.epcb').read_text()):
 if h['type']!='COMPONENT':continue
 assert c['angle']==0
 device=docs.get(device_ids[h['id']])
 if device is None:
  # Page FootprintName references library device identity, retained in META source mapping.
  raise KeyError(c['attrs']['FootprintName'])
 fp=device
 if device['head']['docType']=='DEVICE':
  meta=next(v for k,v in device['rows'] if k['type']=='META')
  fp=docs[meta['attributes']['Footprint']]
 assert fp['head']['docType']=='FOOTPRINT'
 for ph,p in fp['rows']:
  if ph['type']!='PAD':continue
  x=(c['x']+p['centerX'])*.0254;y=-(c['y']+p['centerY'])*.0254
  i=min(range(len(expected)),key=lambda i: math.hypot(x-pcbnew.ToMM(expected[i].GetPosition().x),y-pcbnew.ToMM(expected[i].GetPosition().y)))
  q=expected[i];assert i not in seen;seen.add(i)
  pos=q.GetPosition();drill=q.GetDrillSize();size=q.GetSize()
  ed=sorted([pcbnew.ToMM(drill.x),pcbnew.ToMM(drill.y)])
  nd=sorted([p['hole']['width']*.0254,p['hole']['height']*.0254])
  diffs=[abs(x-pcbnew.ToMM(pos.x)),abs(y-pcbnew.ToMM(pos.y))]+[abs(a-b) for a,b in zip(ed,nd)]+[abs(p['defaultPad']['width']*.0254-pcbnew.ToMM(size.x)),abs(p['defaultPad']['height']*.0254-pcbnew.ToMM(size.y))]
  numbered=p['num']==q.GetNumber()
  checks.append({'pad':p['num'],'position_mm':[x,y],'max_dimension_difference_mm':max(diffs),'number_matches':numbered,'hole_type':p['hole']['holeType'],'plated':p['plated'],'relative_hole_angle':p['relativeAngle'],'mask_expansion_mm':[p['topSolderExpansion']*.0254,p['bottomSolderExpansion']*.0254]})
  if max(diffs)>.0003 or not numbered:errors.append(checks[-1])
assert len(checks)==140 and len(seen)==140
out={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'pads_checked':140,'tolerance_mm':.0003,'max_dimension_difference_mm':max(c['max_dimension_difference_mm'] for c in checks),'errors':errors,'checks':checks,'scope':'Native embedded pad coordinates, pad sizes, unordered drill dimensions and identifiers compared with pcbnew input. Slot orientation, solder-mask rendering, full symbol/net mapping and electrical fitness require further checks. Archive predates outline correction; corrected native page is separate.'}
(E/'native-library-geometry-check.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:v for k,v in out.items() if k!='checks'})
assert not errors
