from pathlib import Path
import pcbnew,json,math
R=Path(__file__).resolve().parents[1]/'hardware/reconstruction'
b=pcbnew.LoadBoard(str(R/'complete-geometry-review.kicad_pcb'));src=json.loads((R/'original-through-hole-geometry.json').read_text());hs={(round(h['x_mm'],6),round(h['y_mm'],6)):h for h in src['holes']};errors=[];roundn=slotn=0;maxerr=0;matches=[]
for fp in b.GetFootprints():
 for p in fp.Pads():
  xy=p.GetPosition();x=pcbnew.ToMM(xy.x)-20;y=83.5-pcbnew.ToMM(xy.y);ds=p.GetDrillSize();dx=pcbnew.ToMM(ds.x);dy=pcbnew.ToMM(ds.y)
  if abs(dx-dy)>1e-6:
   slotn+=1;s=min(src['slots'],key=lambda v:abs(x-v['start_mm'][0]));ex=s['start_mm'][0];ey=(s['start_mm'][1]+s['end_mm'][1])/2;e=max(abs(x-ex),abs(y-ey),abs(dx-s['width_mm']),abs(dy-s['overall_length_mm']))
  else:
   roundn+=1;h=min(src['holes'],key=lambda h:math.hypot(x-h['x_mm'],y-h['y_mm']));e=max(abs(x-h['x_mm']),abs(y-h['y_mm']),abs(dx-h['diameter_mm']));matches.append(h['id'])
   t=h['top_pads'][0];sz=t['dimensions_mm'];sz=sz if len(sz)==2 else sz*2;ps=p.GetSize();e=max(e,abs(pcbnew.ToMM(ps.x)-sz[0]),abs(pcbnew.ToMM(ps.y)-sz[1]))
  maxerr=max(maxerr,e)
  if e>0.000002:errors.append([fp.GetReference(),p.GetNumber(),e])
assert len(list(b.GetFootprints()))==24 and roundn==138 and slotn==2 and len(set(matches))==138 and not errors
out={'reader':'KiCad pcbnew 10 independent parser; input format is KiCad 5.1','footprints':24,'round_pads':roundn,'routed_slots':slotn,'duplicate_round_hole_matches':138-len(set(matches)),'max_geometry_difference_mm':maxerr,'tolerance_mm':0.000002,'errors':errors,'scope':'Coordinate, round pad size, round drill and routed slot geometry. Does not prove electrical mapping or EasyEDA conversion.'};(R/'independent-footprint-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
