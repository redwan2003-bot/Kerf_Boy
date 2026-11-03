"""Source-specific copper tracing and plane sampling, not a general Gerber validator."""
from pathlib import Path
import re,json,math,hashlib
from shapely.geometry import Point,LineString,Polygon,box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'hardware/reconstruction';S=ROOT/'hardware/reference/original/Project Outputs/Project Outputs for CHIP_BOY_Mk_III'
def read_layer(ext):
 ap={};features=[];x=y=0.;selected=None;macro=None;macros={};operation=2
 lines=(S/f'CHIPBOY_Mk_III.{ext}').read_text().splitlines()
 assert '%FSLAX25Y25*%' in lines and '%MOIN*%' in lines
 for l in lines:
  if l.startswith('G04'):continue
  if l in ['G02*','G03*','G36*','G37*'] or l.startswith('%LP'):raise ValueError('Unsupported command '+l)
  m=re.match(r'%AM(\w+)\*',l)
  if m:macro=m[1];continue
  if macro and l.startswith('4,'):
   v=[float(s) for s in l.rstrip('*').split(',')];n=int(v[2]);macros[macro]=Polygon([(v[3+2*i]*25.4,v[4+2*i]*25.4) for i in range(n)]);continue
  if l=='%':macro=None;continue
  m=re.match(r'%ADD(\d+)([CRO]),([\d.X]+)\*%',l)
  if m:
   vals=[float(v)*25.4 for v in m[3].split('X')];w=vals[0];h=vals[1] if len(vals)>1 else w
   if m[2]=='C':g=Point(0,0).buffer(w/2,quad_segs=32)
   elif m[2]=='R':g=box(-w/2,-h/2,w/2,h/2)
   else:
    if w>=h:g=LineString([(-(w-h)/2,0),((w-h)/2,0)]).buffer(h/2,quad_segs=32)
    else:g=LineString([(0,-(h-w)/2),(0,(h-w)/2)]).buffer(w/2,quad_segs=32)
   ap[int(m[1])]=(g,w,m[2]);continue
  m=re.match(r'%ADD(\d+)(\w+)\*%',l)
  if m:ap[int(m[1])]=(macros[m[2]],None,'macro');continue
  m=re.fullmatch(r'D(\d+)\*',l)
  if m:
   n=int(m[1])
   if n>=10:selected=n;continue
   operation=n
   if n==3:
    from shapely.affinity import translate
    features.append(translate(ap[selected][0],x,y))
   continue
  if l.startswith(('X','Y')):
   v=dict(re.findall(r'([XY])(-?\d+)',l));nx=int(v['X'])*.000254-57.658 if 'X'in v else x;ny=int(v['Y'])*.000254-50.8 if 'Y'in v else y
   m=re.search(r'D0([123])',l)
   if m:operation=int(m[1])
   if operation==1:
    assert ap[selected][2]=='C'
    features.append(LineString([(x,y),(nx,ny)]).buffer(ap[selected][1]/2,quad_segs=32))
   elif operation==3:
    from shapely.affinity import translate
    features.append(translate(ap[selected][0],nx,ny))
   x,y=nx,ny
 joined=unary_union(features);return list(joined.geoms) if joined.geom_type=='MultiPolygon' else [joined]
polys={ext:read_layer(ext) for ext in ['GTL','GBL']};holes=json.loads((R/'original-through-hole-geometry.json').read_text())['holes'];parent={}
def find(a):
 parent.setdefault(a,a)
 if parent[a]!=a:parent[a]=find(parent[a])
 return parent[a]
def union(a,b):parent[find(a)]=find(b)
hit={}
for h in holes:
 point=Point(h['x_mm'],h['y_mm']);nodes=[]
 for ext,parts in polys.items():
  for i,p in enumerate(parts):
   if p.distance(point)<1e-6:nodes.append((ext,i))
 hit[h['id']]=nodes
 if h['plated']:
  for n in nodes[1:]:union(nodes[0],n)
groups={}
for h in holes:
 if hit[h['id']]:groups.setdefault(str(find(hit[h['id']][0])),[]).append(h['id'])
# Functions from established schematic references; only unambiguous direct source nets.
anchors={123:'SDA',124:'SCL',125:'D2',126:'D3',127:'D4',128:'D5',129:'D6',132:'D7',133:'D8',134:'D9_after_R4',135:'D10',136:'3V3',137:'GND',175:'BAT+',167:'VCC',168:'GND',149:'GND',148:'3V3',147:'SCL',146:'SDA',111:'SCL',110:'SDA',100:'GP0',101:'GP1',102:'GP2',117:'GP3',116:'GP4',115:'GP5',114:'GP6',113:'GP7',112:'3V3',105:'GND',106:'3V3',103:'D6',60:'VCC',62:'D10',65:'SPK1',66:'GND',67:'SPK2'}
# D9 label names the controller side; R4 prevents copper-only continuity to DFPlayer RX.
anchors[134]='D9'
rows=[]
for members in groups.values():
 labels=sorted({anchors[int(h[1:])] for h in members if int(h[1:]) in anchors});rows.append({'holes':sorted(members),'anchor_nets':labels})
conflicts=[r for r in rows if len(r['anchor_nets'])>1]
output={'scope':'Positive external GTL/GBL copper only; joins plated drill positions; excludes internal planes and component-internal connections. Absence of a link is not proof of NC.','groups':rows,'anchor_conflicts':conflicts,'polygons_per_layer':{k:len(v) for k,v in polys.items()}}
assert not conflicts,conflicts
(R/'external-copper-connectivity.json').write_text(json.dumps(output,indent=2))
print('Polygons',output['polygons_per_layer'],'groups',len(rows),'anchor conflicts',len(conflicts))
for r in rows:
 if any(68<=int(h[1:])<=99 or 119<=int(h[1:])<=120 or 130<=int(h[1:])<=131 or 150<=int(h[1:])<=159 or 183<=int(h[1:])<=187 for h in r['holes']):print(r)


def negative_plane_clearance(ext):
 ap={};features=[];x=y=0.;selected=None;region=False;pts=[];operation=2
 lines=(S/f'CHIPBOY_Mk_III.{ext}').read_text().splitlines()
 assert '%FSLAX25Y25*%' in lines and '%MOIN*%' in lines
 assert any('TF.FilePolarity,Negative' in l for l in lines)
 for l in lines:
  if l.startswith('G04'):continue
  if l in ('G02*','G03*') or l.startswith('%LP'):raise ValueError('Unsupported plane geometry '+l)
  m=re.match(r'%ADD(\d+)([CR]),([\d.X]+)\*%',l)
  if m:
   v=[float(s)*25.4 for s in m[3].split('X')];ap[int(m[1])]=Point(0,0).buffer(v[0]/2,quad_segs=64) if m[2]=='C' else box(-v[0]/2,-v[1]/2,v[0]/2,v[1]/2);continue
  if l=='G36*':region=True;pts=[];continue
  if l=='G37*':
   if len(pts)>2:features.append(Polygon(pts))
   region=False;pts=[];continue
  m=re.fullmatch(r'D(\d+)\*',l)
  if m:
   n=int(m[1])
   if n>=10:selected=n
   elif n==3:
    from shapely.affinity import translate
    features.append(translate(ap[selected],x,y))
   continue
  if l.startswith(('X','Y')):
   v=dict(re.findall(r'([XY])(-?\d+)',l));nx=int(v['X'])*.000254-57.658 if 'X'in v else x;ny=int(v['Y'])*.000254-50.8 if 'Y'in v else y
   m=re.search(r'D0([123])',l)
   if m:operation=int(m[1])
   if region:
    if operation==2 and pts:
     if len(pts)>2:features.append(Polygon(pts))
     pts=[]
    pts.append((nx,ny))
   elif operation==1:
    width=ap[selected].bounds[2]-ap[selected].bounds[0]
    assert abs(width-(ap[selected].bounds[3]-ap[selected].bounds[1]))<1e-6
    features.append(LineString([(x,y),(nx,ny)]).buffer(width/2,quad_segs=64))
   x,y=nx,ny
 assert all(g.is_valid for g in features)
 return unary_union(features)
clearances={ext:negative_plane_clearance(ext) for ext in ['GP1','GP2']}
plane_rows=[]
for h in holes:
 if not h['plated']:continue
 counts={}; sensitivity={}
 for ext,g in clearances.items():
  samples=[]
  for offset in (0.02,0.04,0.06):
   radius=h['diameter_mm']/2+offset
   samples.append(sum(not g.covers(Point(h['x_mm']+radius*math.cos(i*math.pi/8),h['y_mm']+radius*math.sin(i*math.pi/8))) for i in range(16)))
  counts[ext]=samples[1];sensitivity[ext]=samples
 plane_rows.append({'hole':h['id'],'copper_samples_of_16':counts,'samples_at_offsets_002_004_006_mm':sensitivity})
plane_by_hole={r['hole']:r for r in plane_rows}
checks=[]
for num,net in anchors.items():
 if net in ('GND','3V3'):
  good='GP1' if net=='GND' else 'GP2';bad='GP2' if good=='GP1' else 'GP1';v=plane_by_hole[f'H{num:03}']['copper_samples_of_16'];checks.append({'hole':f'H{num:03}','expected':net,'pass':v[good]==16 and v[bad]==0,'samples':v})
assert all(r['pass'] for r in checks),checks
full=[]
for group in rows:
 nets=set(group['anchor_nets'])
 for hid in group['holes']:
  v=plane_by_hole.get(hid,{}).get('copper_samples_of_16',{})
  if v.get('GP1')==16:nets.add('GND')
  if v.get('GP2')==16:nets.add('3V3')
 full.append({'holes':group['holes'],'nets':sorted(nets)})
assert all(len(g['nets'])<=1 for g in full),[g for g in full if len(g['nets'])>1]
result={'scope':'Original external copper plus negative internal plane clearance-ring sampling; 16 samples 0.04 mm outside each plated drill. Not component internal continuity or manufacturer numbering verification.','known_power_anchor_checks':checks,'plane_samples':plane_rows,'groups':full,'conflicts':[]}
(R/'four-layer-connectivity-check.json').write_text(json.dumps(result,indent=2))
sensitive=[r for r in plane_rows if any(len(set(v))>1 for v in r['samples_at_offsets_002_004_006_mm'].values())]
result['sampling_sensitivity_holes']=sensitive
result['source_sha256']={ext:hashlib.sha256((S/f'CHIPBOY_Mk_III.{ext}').read_bytes()).hexdigest() for ext in ('GTL','GBL','GP1','GP2')}
result['limitations']=['No net label means unresolved, not isolated or NC.','Partial ring coverage requires thermal/clearance inspection; H098 is unresolved.','Only local plane copper is sampled; global plane continuity is not established.','Exact component numbering and component-internal connections are not reconstructed.']
(R/'four-layer-connectivity-check.json').write_text(json.dumps(result,indent=2))
print('Internal-plane anchor checks passed:',len(checks),'sampling-sensitive holes:',len(sensitive))
for g in full:
 if any(68<=int(h[1:])<=99 or 119<=int(h[1:])<=120 or 130<=int(h[1:])<=131 or 150<=int(h[1:])<=159 or 183<=int(h[1:])<=187 for h in g['holes']):print(g)
