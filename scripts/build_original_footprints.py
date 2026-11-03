from pathlib import Path
import json,re,csv,zipfile
R=Path(__file__).resolve().parents[1]/'hardware/reconstruction';S=Path(__file__).resolve().parents[1]/'hardware/reference/original/Project Outputs/Project Outputs for CHIP_BOY_Mk_III';D=json.loads((R/'original-through-hole-geometry.json').read_text());H={int(h['id'][1:]):h for h in D['holes']}
def flashes(ext):
 ap={};out={};x=y=0;d=None
 for l in (S/('CHIPBOY_Mk_III.'+ext)).read_text().splitlines():
  m=re.match(r'%ADD(\d+)([CRO]),([\d.X]+)\*%',l)
  if m:ap[int(m[1])]={'shape':m[2],'dimensions_mm':[round(float(v)*25.4,6) for v in m[3].split('X')]};continue
  m=re.fullmatch(r'D(\d+)\*',l)
  if m:
   n=int(m[1])
   if n==3:out[(round(x-57.658,6),round(y-50.8,6))]=ap.get(d)
   elif n>=10:d=n
   continue
  if l.startswith(('X','Y')):
   v=dict(re.findall(r'([XY])(-?\d+)',l));x=int(v['X'])*.000254 if 'X'in v else x;y=int(v['Y'])*.000254 if 'Y'in v else y
   if 'D03' in l:out[(round(x-57.658,6),round(y-50.8,6))]=ap.get(d)
 return out
layers={k:flashes(k) for k in ['GTL','GBL','GTS','GBS']}
configs=[
('M1','XIAO_original',list(range(123,130))+list(range(132,139)),[str(i) for i in range(1,15)],['D0','D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','3V3','GND','5V']),
('U1','MCP23008_original',[111,110,109,108,107,106,103,104,105,100,101,102,117,116,115,114,113,112],[str(i) for i in range(1,19)],['SCL','SDA','A2','A1','A0','RESET','NC','INT','GND','GP0','GP1','GP2','GP3','GP4','GP5','GP6','GP7','VDD']),
('U2','DFPlayer_original',list(range(60,68))+list(range(52,60)),[str(i) for i in range(1,17)],['VCC','RX','TX','DAC_R','DAC_L','SPK1','GND','SPK2','IO1','GND','IO2','ADKEY1','ADKEY2','USB+','USB-','BUSY']),
('U3','GPS_original',list(range(160,165)),[f'{i:02}' for i in range(1,6)],['VCC','GND','TX','RX','PPS']),
('U4','BNO055_original',[121,122,142,141,139,140,145,144,143,118],[str(i) for i in range(1,11)],['VIN','3VO','GND','SDA','SCL','RST','ADR','INT','PS1','PS0']),
('DS','OLED_original',[149,148,147,146],['1','2','3','4'],['GND','VCC','SCL','SDA']),
('J5','BME280_original',[174,173,172,171,170,169],['1','2','3','4','5','6'],['VCC','GND','SCL','SDA','CSB','SDO']),
('J4','TOF400C_original',[165,166,182,181,180,179],['1','2','3','4','5','6'],['SHUT','INT','SCL','SDA','GND','VCC']),
('J1','Battery_original',[175,176],['1','2'],['BAT+','GND']),
('J2','ESP_battery_original',[168,167],['1','2'],['GND','VCC']),
('J3','Laser_original',[177,178],['1','2'],['3V3','LASER_RETURN'])]
lib=R/'OriginalCarrier.pretty';lib.mkdir(exist_ok=True);records=[];checks=[];board=[]
for ref,name,ids,nums,signals in configs:
 assert len(ids)==len(nums)==len(signals) and len(set(nums))==len(nums)
 origin=H[ids[0]];body=[]
 for hid,num,sig in zip(ids,nums,signals):
  h=H[hid];key=(h['x_mm'],h['y_mm']);top=layers['GTL'][key];bottom=layers['GBL'].get(key);mt=layers['GTS'].get(key);mb=layers['GBS'].get(key)
  assert top==bottom,(ref,num,top,bottom)
  assert mt==mb and mt is not None,(ref,num,mt,mb)
  dims=top['dimensions_mm'];size=dims if len(dims)==2 else dims*2;mask=mt['dimensions_mm'];mask=mask if len(mask)==2 else mask*2
  margins=[round((mask[i]-size[i])/2,6) for i in (0,1)];assert abs(margins[0]-margins[1])<1e-6 and top['shape']==mt['shape']
  x=round(h['x_mm']-origin['x_mm'],6);y=round(origin['y_mm']-h['y_mm'],6)
  shape={'C':'circle','R':'rect','O':'oval'}[top['shape']]
  body.append(f'  (pad "{num}" thru_hole {shape} (at {x} {y}) (size {size[0]} {size[1]}) (drill {h["diameter_mm"]:.6f}) (layers "*.Cu" "*.Mask") (solder_mask_margin {margins[0]}))')
  records.append({'reference':ref,'footprint':name,'pin':num,'signal':sig,'hole_id':h['id'],'source_x_mm':h['x_mm'],'source_y_mm':h['y_mm'],'local_x_mm':x,'local_y_mm':y,'drill_mm':round(h['diameter_mm'],6),'pad_size_mm':size,'shape':shape,'mask_margin_mm':margins[0],'evidence':'Schematic pin functions plus assembly label/location; no original native netlist available','mapping_status':'Reconstructed; independent original netlist comparison unavailable'})
  checks.append({'ref':ref,'pin':num,'both_copper_layers_equal':True,'both_mask_layers_equal':True})
 fp=f'(module "{name}" (layer "F.Cu") (tedit 0)\n (descr "Original fabrication geometry; schematic/assembly reconstructed pin map; not fabrication release")\n (fp_text reference "{ref}" (at 0 -3) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))\n (fp_text value "{name}" (at 0 -5) (layer "F.Fab") (effects (font (size .7 .7) (thickness .1))))\n'+'\n'.join(body)+'\n)'
 (lib/(name+'.kicad_mod')).write_text(fp)
 board.append(fp.replace('(tedit 0)',f'(tedit 0) (at {origin["x_mm"]+20} {83.5-origin["y_mm"]})'))
header='(kicad_pcb (version 20171130) (host pcbnew 5.1.12) (general (thickness 1.6)) (page A4) (layers (0 F.Cu signal) (31 B.Cu signal) (36 B.SilkS user) (37 F.SilkS user) (38 B.Mask user) (39 F.Mask user) (44 Edge.Cuts user) (49 F.Fab user))\n'
edges=[]
for q in json.loads((R/'outline-geometry.json').read_text()):
 for a,b in zip(q,q[1:]):edges.append(f'(gr_line (start {a[0]+20} {83.5-a[1]}) (end {b[0]+20} {83.5-b[1]}) (layer Edge.Cuts) (width .05))')
(R/'original-interface-review.kicad_pcb').write_text(header+'\n'.join(board+edges)+'\n)')
(R/'reconstructed-pin-map.json').write_text(json.dumps(records,indent=2));(R/'footprint-layer-checks.json').write_text(json.dumps({'footprints':len(configs),'pads':len(records),'checks':checks,'remaining':'Encoder, switches, LEDs, buzzer and tactile buttons not exported pending numbering/polarity verification; no EasyEDA import verification'},indent=2))
with (R/'reconstructed-pin-map.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
with zipfile.ZipFile(R/'original-interface-import.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.write(R/'original-interface-review.kicad_pcb','original-interface-review.kicad_pcb')
 for p in lib.glob('*.kicad_mod'):z.write(p,'OriginalCarrier.pretty/'+p.name)
print('Generated',len(configs),'footprints,',len(records),'pads. Copper and solder-mask matches passed on both sides.')
