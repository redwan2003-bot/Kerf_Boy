"""Check final import input against original drilled holes and SMD aperture evidence."""
from pathlib import Path
import json,math
import pcbnew
R=Path(__file__).resolve().parents[1];O=R/'hardware/easyeda/step3-numbered'
b=pcbnew.LoadBoard(str(O/'complete-component-review.kicad_pcb'))
source=json.loads((R/'hardware/reconstruction/original-through-hole-geometry.json').read_text())
sm=json.loads((O/'smd-source-check.json').read_text())['records']
smd={(r['reference'],r['pin']):r for r in sm}
holes=[];slots=[];smdchecks=[]
mm=pcbnew.ToMM
for f in b.GetFootprints():
 for p in f.Pads():
  pos=p.GetPosition();x=mm(pos.x)-20;y=83.5-mm(pos.y);d=p.GetDrillSize();sz=p.GetSize()
  if d.x and d.x==d.y:
   h=min(source['holes'],key=lambda h:math.hypot(x-h['x_mm'],y-h['y_mm']))
   error=max(abs(x-h['x_mm']),abs(y-h['y_mm']),abs(mm(d.x)-h['diameter_mm']))
   assert error<.000002,(f.GetReference(),p.GetNumber(),error)
   holes.append({'reference':f.GetReference(),'pin':p.GetNumber(),'source_hole':h['id'],'error_mm':error})
  elif d.x:
   s=min(source['slots'],key=lambda s:abs(x-s['start_mm'][0]))
   error=max(abs(x-s['start_mm'][0]),abs(y-(s['start_mm'][1]+s['end_mm'][1])/2),abs(mm(d.x)-s['width_mm']),abs(mm(d.y)-s['overall_length_mm']))
   assert error<.000002
   slots.append({'reference':f.GetReference(),'pin':p.GetNumber(),'error_mm':error})
  elif (f.GetReference(),p.GetNumber()) in smd:
   r=smd[f.GetReference(),p.GetNumber()]
   differences=[abs(x-r['source_center_mm'][0]),abs(y-r['source_center_mm'][1]),abs(mm(sz.x)-r['pad_mm'][0]),abs(mm(sz.y)-r['pad_mm'][1])]
   assert max(differences)<.000002
   assert f.GetLayer()==(pcbnew.F_Cu if r['side']=='F' else pcbnew.B_Cu)
   mask=mm(p.GetLocalSolderMaskMargin() or 0);paste=mm(p.GetLocalSolderPasteMargin() or 0)
   maskerr=max(abs(mm(sz.x)+2*mask-r['mask_mm'][0]),abs(mm(sz.y)+2*mask-r['mask_mm'][1]))
   pasteerr=max(abs(mm(sz.x)+2*paste-r['paste_mm'][0]),abs(mm(sz.y)+2*paste-r['paste_mm'][1]))
   assert maskerr<=.0006 and pasteerr<=.0006
   smdchecks.append({'reference':f.GetReference(),'pin':p.GetNumber(),'copper_error_mm':max(differences),'mask_error_mm':maskerr,'paste_error_mm':pasteerr})
assert len(holes)==138 and len(set(r['source_hole'] for r in holes))==138 and len(slots)==2 and len(smdchecks)==33
out={'round_holes':138,'slots':2,'remaining_smd_pads':33,'holes':holes,'slot_checks':slots,'smd_checks':smdchecks,'scope':'Original drilled geometry and 33 SMD copper/mask/paste apertures. Uniform mask expansion approximates independently rounded aperture axes within 0.0006 mm. Navigation SMD pads checked separately.'}
(O/'source-geometry-check.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS: 138 original round holes, 2 routed slots, 33 SMD pads; no duplicate hole assignments.')
print('Maximum SMD mask deviation mm:',max(c['mask_error_mm'] for c in smdchecks))
