"""Check plane connectivity using clipped copper polygons and drilled holes."""
from pathlib import Path
import contextlib,io,json
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
# Reuse the source-specific parser; suppress its verbose diagnostic output.
with contextlib.redirect_stdout(io.StringIO()):
 import trace_external_copper as trace
R=trace.R
loops=json.loads((R/'outline-geometry.json').read_text())
board=Polygon(loops[0],loops[1:]);assert board.is_valid
drills=[Point(h['x_mm'],h['y_mm']).buffer(h['diameter_mm']/2,quad_segs=64) for h in trace.holes]
for slot in json.loads((R/'original-through-hole-geometry.json').read_text())['slots']:
 drills.append(LineString([slot['start_mm'],slot['end_mm']]).buffer(slot['width_mm']/2,quad_segs=64))
removed=unary_union(drills)
planes={};results=[]
for ext,anchor in [('GP1','H137'),('GP2','H136')]:
 copper=board.difference(trace.clearances[ext]).difference(removed)
 parts=list(copper.geoms) if copper.geom_type=='MultiPolygon' else [copper]
 planes[ext]=parts
 def touched(hid):
  h=next(h for h in trace.holes if h['id']==hid)
  center=Point(h['x_mm'],h['y_mm']);ring=center.buffer(h['diameter_mm']/2+0.02,quad_segs=64).difference(center.buffer(h['diameter_mm']/2,quad_segs=64))
  return [i for i,p in enumerate(parts) if p.intersection(ring).area>1e-8]
 anchor_parts=touched(anchor);assert len(anchor_parts)==1
 for hid in ['H095','H098','H083','H086','H089','H092']:
  ids=touched(hid);results.append({'layer':ext,'hole':hid,'anchor':anchor,'same_copper_island':bool(set(ids)&set(anchor_parts)),'touched_islands':ids,'anchor_islands':anchor_parts})
result={'scope':'Source plane topology: reconstructed board clipped by negative Gerber clearance geometry and all round drills/routed slots. Polygon approximation, not physical continuity testing.','source_sha256':json.loads((R/'four-layer-connectivity-check.json').read_text())['source_sha256'],'copper_islands':{k:len(v) for k,v in planes.items()},'checks':results}
assert all(c['same_copper_island']==(c['layer']=='GP2') for c in results)
(R/'plane-topology-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
