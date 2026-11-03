from pathlib import Path
import json,re,zipfile
R=Path(__file__).resolve().parents[1]/'hardware/reconstruction'
# Reuse parsed, independently compared source-layer data; no UI state accessed.
exec(Path(__file__).with_name('build_original_footprints.py').read_text(encoding='utf-8-sig'))
lib2=R/'UnresolvedOriginal.pretty';lib2.mkdir(exist_ok=True)
extra=[('RE1','Encoder',[183,184,185,187,186]),('S4','Power_switch',list(range(70,76))),('S5','Tone_switch',list(range(76,82))),('S1','Flash_switch',list(range(82,88))),('S3','Laser_switch',list(range(88,94))),('S2','Flash_LED3_switch',list(range(94,100))),('LED1','LED1',[151,150]),('LED2','LED2',[119,120]),('LED3','LED3',[131,130]),('AUDIO','Audio_two_pin',[68,69]),('B0','Button_B0',[156,157,158,159]),('B1','Button_B1',[152,153,154,155]),('B2_LOC','Navigation_locators',[188,189])]
known={r['hole_id'] for r in records};new=[];fplist=[]
for ref,name,ids in extra:
 o=H[ids[0]];body=[]
 for hid in ids:
  h=H[hid];assert h['id'] not in known;known.add(h['id']);k=(h['x_mm'],h['y_mm']);t=layers['GTL'].get(k);bt=layers['GBL'].get(k);mt=layers['GTS'].get(k);mb=layers['GBS'].get(k)
  assert t==bt,(ref,hid,'copper');assert mt==mb,(ref,hid,'mask')
  sz=t['dimensions_mm'];sz=sz if len(sz)==2 else sz*2
  margin=0
  if mt:
   ms=mt['dimensions_mm'];ms=ms if len(ms)==2 else ms*2
   assert abs((ms[0]-sz[0])-(ms[1]-sz[1]))<1e-6
   margin=round((ms[0]-sz[0])/2,6)
  x=round(h['x_mm']-o['x_mm'],6);y=round(o['y_mm']-h['y_mm'],6)
  # Hole IDs deliberately retain unknown pin identity instead of guessing polarity/contact numbering.
  num=h['id'] if h['plated'] else '';typ='thru_hole' if h['plated'] else 'np_thru_hole';shape={'C':'circle','R':'rect','O':'oval'}[t['shape']]
  body.append(f'(pad "{num}" {typ} {shape} (at {x} {y}) (size {sz[0]} {sz[1]}) (drill {h["diameter_mm"]:.6f}) (layers "*.Cu" "*.Mask") (solder_mask_margin {margin}))')
  new.append({'reference':ref,'source_hole':h['id'],'electrical_pin':'UNRESOLVED' if h['plated'] else 'MECHANICAL','local_x_mm':x,'local_y_mm':y,'source_x_mm':h['x_mm'],'source_y_mm':h['y_mm'],'both_copper_layers_match':True,'both_mask_layers_match':True,'plated':h['plated']})
 if ref=='RE1':
  for i,s in enumerate(D['slots']):
   x=(s['start_mm'][0]+s['end_mm'][0])/2-o['x_mm'];y=o['y_mm']-(s['start_mm'][1]+s['end_mm'][1])/2
   # Slot copper uses an oval aperture; establish it at the routed-slot midpoint.
   k=(round(x+o['x_mm'],6),round(o['y_mm']-y,6));t=layers['GTL'].get(k);bt=layers['GBL'].get(k);mt=layers['GTS'].get(k);mb=layers['GBS'].get(k)
   assert t and t==bt and mt==mb,(k,t,bt,mt,mb)
   sz=t['dimensions_mm'];ms=mt['dimensions_mm'];margin=round((ms[0]-sz[0])/2,6);assert abs((ms[1]-sz[1])/2-margin)<1e-6
   body.append(f'(pad "SLOT{i+1}" thru_hole oval (at {x:.6f} {y:.6f}) (size {sz[0]} {sz[1]}) (drill oval {s["width_mm"]:.6f} {s["overall_length_mm"]:.6f}) (layers "*.Cu" "*.Mask") (solder_mask_margin {margin}))')
   new.append({'reference':ref,'source_hole':f'SLOT{i+1}','electrical_pin':'SHIELD_NUMBER_UNRESOLVED','both_copper_layers_match':True,'both_mask_layers_match':True})
 name='HOLD_'+name;fp=f'(module "{name}" (layer "F.Cu") (tedit 0)\n(descr "REFERENCE ONLY - electrical pad numbering unresolved; not for fabrication")\n(fp_text reference "{ref}" (at 0 -3) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))\n(fp_text value "HOLD_PIN_MAP" (at 0 -5) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))\n'+'\n'.join(body)+'\n)'
 (lib2/(name+'.kicad_mod')).write_text(fp);fplist.append(fp.replace('(tedit 0)',f'(tedit 0) (at {o["x_mm"]+20} {83.5-o["y_mm"]})'))
original=(R/'original-interface-review.kicad_pcb').read_text();(R/'complete-geometry-review.kicad_pcb').write_text(original.rstrip()[:-1]+'\n'+'\n'.join(fplist)+'\n)')
remaining=[h for h in D['holes'] if h['id'] not in known]
assert len(remaining)==51 and all(h['tool'] in (1,2) for h in remaining)
report={'geometry_groups_total':24,'mapped_component_groups':11,'reconstructed_signal_pads':85,'held_groups':13,'additional_round_holes':53,'routed_slots':2,'all_component_round_holes_accounted':138,'small_unassigned_via_candidates':len(remaining),'unassigned_tool_counts':{'T01':44,'T02':7},'full_pin_map_complete':False,'easyeda_import_verified':False,'held_pad_records':new,'hold_reasons':['Six-lead switches use three-terminal schematic symbols; native numbering and H098 partial plane coverage remain unresolved.', 'Copper tracing supports BZ1 identity; exact component numbering and symbol binding remain unverified.', 'LED ground terminals have trace evidence; native numbering and physical polarity remain unverified.', 'B0/B1 contact grouping has copper evidence; native numbering remains unverified.', 'Encoder contact functions have copper evidence; native numbering and shield assignment remain unverified.', 'Navigation switch SMD contacts are not reconstructed by the two locating holes.']}
(R/'remaining-footprint-checks.json').write_text(json.dumps(report,indent=2))
with zipfile.ZipFile(R/'through-hole-review-package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['complete-geometry-review.kicad_pcb','reconstructed-pin-map.csv','reconstructed-pin-map.json','remaining-footprint-checks.json','footprint-layer-checks.json','original-through-hole-geometry.csv']:
  z.write(R/name,name)
 for lib in (R/'OriginalCarrier.pretty',lib2):
  for p in lib.glob('*.kicad_mod'):z.write(p,lib.name+'/'+p.name)
print('GEOMETRY ACCOUNTED: 138 round component/locator holes + 2 slots; 51 small via candidates remain outside footprints. 24 groups exported.')
