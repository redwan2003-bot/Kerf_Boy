"""Recover the remaining 16 Mk III SMD footprints directly from Gerber flashes."""
from pathlib import Path
import json,zipfile
import build_numbered_carrier as base
R=base.R;OUT=base.OUT;lib=OUT/'KerfOriginal.pretty'
parser=Path(__file__).with_name('build_original_footprints.py');ns={'__file__':str(parser)};code=parser.read_text();exec(code[:code.index('layers={')],ns)
layers={ext:ns['flashes'](ext) for ext in ['GTL','GBL','GTS','GBS','GTP','GBP']}
# Nonpolar pin numbering is explicit redesign numbering. Polar pads use copper-anchor evidence.
configs=[
 ('R1','B',[(7.6581,49.022),(9.6139,49.022)],['1','2']),
 ('R2','B',[(85.0011,44.577),(86.9569,44.577)],['1','2']),
 ('R3','B',[(83.3501,17.526),(85.3059,17.526)],['1','2']),
 ('R4','B',[(15.0241,28.321),(16.9799,28.321)],['1','2']),
 ('R5','B',[(25.5651,33.528),(27.5209,33.528)],['1','2']),
 ('R6','B',[(27.5971,36.449),(29.5529,36.449)],['1','2']),
 ('R7','B',[(59.2201,50.419),(61.1759,50.419)],['1','2']),
 ('R8','B',[(55.245,51.740054),(55.245,49.784)],['1','2']),
 ('C1','B',[(24.003,22.07006),(24.003,20.32)],['1','2']),
 ('C2','B',[(79.89697,44.831),(81.64703,44.831)],['1','2']),
 ('C5','B',[(60.84697,54.102),(62.59703,54.102)],['1','2']),
 ('C9','B',[(47.61103,57.404),(45.86097,57.404)],['1','2']),
 ('C3','F',[(35.266122,28.448),(30.266132,28.448)],['1','2']),
 ('C4','F',[(25.741122,28.448),(20.741132,28.448)],['1','2']),
 ('T1','B',[(57.97296,54.144926),(56.07304,54.144926),(57.023,56.345074)],['1','2','3']),
 ('LS1','F',[(34.186114,55.572914),(34.186114,45.773086)],['1','2'])]
records=[];mods=[]
for ref,side,centers,nums in configs:
 cu,mask,paste=('GTL','GTS','GTP') if side=='F' else ('GBL','GBS','GBP')
 ox,oy=centers[0];pads=[]
 for xy,n in zip(centers,nums):
  c=layers[cu][xy];m=layers[mask][xy];p=layers[paste].get(xy)
  assert c['shape']==m['shape']=='R' and p is not None,(ref,n)
  w,h=c['dimensions_mm'];mw,mh=m['dimensions_mm'];pw,ph=p['dimensions_mm'];margin=(mw-w)/2;pm=(pw-w)/2
  assert abs((mh-h)/2-margin)<0.0003 and abs((ph-h)/2-pm)<0.0003,(ref,n,(mw,mh),(pw,ph),(w,h))
  pads.append(f'(pad "{n}" smd rect (at {xy[0]-ox:.6f} {oy-xy[1]:.6f}) (size {w} {h}) (layers {side}.Cu {side}.Paste {side}.Mask) (solder_mask_margin {margin:.6f}) (solder_paste_margin {pm:.6f}))')
  records.append({'reference':ref,'pin':n,'side':side,'source_center_mm':xy,'pad_mm':[w,h],'mask_mm':[mw,mh],'paste_mm':[pw,ph]})
 name='Kerf_'+ref+'_original';head=f'(module "{name}" (layer "{side}.Cu") (tedit 0)'
 body=f'\n(fp_text reference "{ref}" (at 0 -3) (layer "{side}.SilkS") (effects (font (size 1 1) (thickness .15))))\n(fp_text value "{name}" (at 0 -4) (layer "{side}.Fab") (effects (font (size .7 .7) (thickness .1))))\n'+'\n'.join(pads)+'\n)'
 (lib/(name+'.kicad_mod')).write_text(head+body)
 mods.append(head+f' (at {ox+20:.6f} {83.5-oy:.6f})'+body)
board=(OUT/'numbered-carrier-review.kicad_pcb').read_text().rstrip();board=board[:-1]+'\n'+'\n'.join(mods)+'\n)\n'
# Add layers used by the reconstructed SMD footprints to the legacy import header.
board=board.replace('(36 B.SilkS user)', '(34 B.Paste user) (35 F.Paste user) (36 B.SilkS user)').replace('(49 F.Fab user)', '(48 B.Fab user) (49 F.Fab user)')
(OUT/'complete-component-review.kicad_pcb').write_text(board)
with zipfile.ZipFile(OUT/'complete-component-review.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(OUT/'complete-component-review.kicad_pcb','complete-component-review.kicad_pcb')
(OUT/'smd-source-check.json').write_text(json.dumps({'footprints':16,'pads':len(records),'records':records,'scope':'Positive copper aperture geometry; mask/paste use uniform expansion approximating separately rounded axes. See source-geometry-check.json for measured deviation. Nonpolar pin numbers are explicit redesign conventions; T1 uses AO3400A G1/S2/D3. Full circuit and manufacturer fit are separate.'},indent=2)+'\n')
print('Added',len(configs),'SMD footprints;',len(records),'pad copper/mask/paste checks')
