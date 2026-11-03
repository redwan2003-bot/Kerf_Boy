from pathlib import Path
import re,json,csv,sys,collections,math
R=Path(__file__).resolve().parents[1]/'hardware/reconstruction';
S=Path(__file__).resolve().parents[1]/'hardware/reference/original/Project Outputs/Project Outputs for CHIP_BOY_Mk_III'
origin=(57.658,50.8)
def coord(s):return float(s) *25.4 if '.' in s else int(s.ljust(7,'0'))*.000254
holes=[];ts={};x=y=0;plated=True;tool=None
for l in (S/'CHIPBOY_Mk_III.TXT').read_text().splitlines():
 if l.startswith(';TYPE='):plated=l==';TYPE=PLATED'
 m=re.match(r'T(\d+).*C([\d.]+)',l)
 if m:ts[int(m[1])]={'diameter_mm':float(m[2])*25.4,'plated':plated};continue
 if re.fullmatch(r'T\d+',l):tool=int(l[1:]);continue
 if l.startswith(('X','Y')):
  v=dict(re.findall(r'([XY])(-?[\d.]+)',l));x=coord(v['X']) if 'X'in v else x;y=coord(v['Y']) if 'Y'in v else y
  holes.append({'id':f'H{len(holes)+1:03}','tool':tool,'x_mm':round(x-origin[0],6),'y_mm':round(y-origin[1],6),**ts[tool]})
counts=collections.Counter(h['tool'] for h in holes)
expected={1:44,2:7,3:18,4:30,5:18,6:34,7:8,8:5,9:18,10:5,12:1,13:1}
assert dict(counts)==expected,(counts,expected)
# Gerber 2:5 leading-zero suppression, independent of Excellon LZ representation.
flashes={};ap={};x=y=0;d=None;op=None
for l in (S/'CHIPBOY_Mk_III.GTL').read_text().splitlines():
 m=re.match(r'%ADD(\d+)([CRO]),([\d.X]+)\*%',l)
 if m:ap[int(m[1])]={'shape':m[2],'dimensions_mm':[round(float(v)*25.4,6) for v in m[3].split('X')]};continue
 if l=='D03*':
  flashes.setdefault((round(x-origin[0],6),round(y-origin[1],6)),[]).append({'aperture':d,**ap.get(d,{'shape':'macro/unparsed'})});continue
 if re.fullmatch(r'D\d+\*',l):d=int(l[1:-1]);continue
 if l.startswith(('X','Y')):
  v=dict(re.findall(r'([XY])(-?\d+)',l));x=int(v['X'])*.000254 if 'X'in v else x;y=int(v['Y'])*.000254 if 'Y'in v else y
  m=re.search(r'D0([123])',l)
  if m:op=int(m[1])
  if op==3:flashes.setdefault((round(x-origin[0],6),round(y-origin[1],6)),[]).append({'aperture':d,**ap.get(d,{'shape':'macro/unparsed'})})
for h in holes:
 h['top_pads']=flashes.get((h['x_mm'],h['y_mm']),[])
 h['role']='via_candidate' if h['tool']==1 else 'component_hole_candidate'
 h['pin_number']='UNVERIFIED';h['component']='UNASSIGNED'
slots=[];start=None
for l in (S/'CHIPBOY_Mk_III-RectHoles.TXT').read_text().splitlines():
 if l.startswith(('G00X','G01Y')):
  v=dict(re.findall(r'([XY])(-?[\d.]+)',l));x=coord(v['X']) if 'X'in v else x;y=coord(v['Y']) if 'Y'in v else y
  if l.startswith('G00'):start=(x-origin[0],y-origin[1])
  else:slots.append({'tool':11,'plated':True,'width_mm':.07874*25.4,'start_mm':start,'end_mm':(x-origin[0],y-origin[1]),'overall_length_mm':abs(y-origin[1]-start[1])+.07874*25.4})
assert len(slots)==2
report={'status':'Reference geometry only; component and pin mapping not released','origin_source_mm':origin,'round_hole_count':len(holes),'routed_slot_count':len(slots),'counts_match_original_DRR':True,'top_pad_matched_holes':sum(bool(h['top_pads']) for h in holes),'holes':holes,'slots':slots}
(R/'original-through-hole-geometry.json').write_text(json.dumps(report,indent=2))
with (R/'original-through-hole-geometry.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['ID','Tool','X_mm','Y_mm','Drill_mm','Plated','Top_pad_shape_dimensions','Component','Pin'])
 for h in holes:w.writerow([h['id'],h['tool'],h['x_mm'],h['y_mm'],h['diameter_mm'],h['plated'],json.dumps(h['top_pads']),h['component'],h['pin_number']])
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(14,10))
for q in json.loads((R/'outline-geometry.json').read_text()):ax.plot(*zip(*q),color='#555',lw=.8)
for h in holes:
 if h['role']=='via_candidate':ax.plot(h['x_mm'],h['y_mm'],'.',color='#aaa',ms=2)
 else:
  ax.add_patch(plt.Circle((h['x_mm'],h['y_mm']),h['diameter_mm']/2,fill=False,color='#125ca1'))
  ax.text(h['x_mm']+.35,h['y_mm']+.35,h['id'],fontsize=4.5)
for s in slots:ax.plot([s['start_mm'][0],s['end_mm'][0]],[s['start_mm'][1],s['end_mm'][1]],lw=4,color='#d67000',solid_capstyle='round')
ax.set_aspect('equal');ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)');ax.set_title('Original through-hole reference | 189 round holes + 2 routed slots\nHole IDs are references, NOT component pin numbers. Gray points: via candidates.');ax.grid(alpha=.15)
fig.savefig(R/'original-through-hole-map.png',dpi=180,bbox_inches='tight')
print(json.dumps({k:v for k,v in report.items() if k not in ('holes','slots')},indent=2));print('Slots:',slots)
