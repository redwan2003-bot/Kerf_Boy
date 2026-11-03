"""Check eight navigation SMD pads against the Mk III Gerber polygons."""
from pathlib import Path
import json
from shapely.geometry import box
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'hardware/easyeda/step3-numbered'
parser=R/'scripts/trace_external_copper.py';ns={'__file__':str(parser)}
exec(parser.read_text().split('polys={ext:read_layer')[0],ns)
layers={e:unary_union(ns['read_layer'](e)) for e in ['GTL','GTS','GTP']}
checked=json.loads((O/'native-component-check.json').read_text())['checks']
checks=[]
for p in checked:
 if p['reference']!='B2_LOC' or not p['pin']:continue
 x,y=p['position_mm'];x-=20;y=83.5-y
 w,h=(2,1.8) if p['pin'].startswith('SH') else (2,1)
 row={'pin':p['pin'],'center_mm':[x,y],'layer_checks':{}}
 for ext in layers:
  margin=.1016 if ext=='GTS' else 0
  shape=translate(rotate(box(-w/2-margin,-h/2-margin,w/2+margin,h/2+margin),45),x,y)
  outside=shape.difference(layers[ext].buffer(.001)).area
  row['layer_checks'][ext]={'outside_area_mm2_at_1um_tolerance':outside}
  assert outside<1e-9,(p['pin'],ext,outside)
 checks.append(row)
assert len(checks)==8
(O/'navigation-source-check.json').write_text(json.dumps({'pads':8,'tolerance_mm':.001,'checks':checks,'scope':'Eight rotated rectangular copper/paste and expanded mask shapes contained in original Gerbers within 1 micrometre. This is source conversion evidence, not a fabrication tolerance or mechanical fit approval.'},indent=2)+'\n')
print('PASS: eight navigation pads on copper, solder mask and paste.')
