"""Build numbered carrier footprints using matching Mk II pad geometry as evidence.
Original Mk III fabrication geometry is retained. Buzzer P/N is a redesign polarity
assignment, not a claim that the original board connected P correctly.
"""
from pathlib import Path
import json,re,math,zipfile
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'hardware/reconstruction';OUT=ROOT/'hardware/easyeda/step3-numbered'
OUT.mkdir(exist_ok=True);lib=OUT/'KerfOriginal.pretty';lib.mkdir(exist_ok=True)
source={c['reference']:c for c in json.loads((R/'upstream-mk-ii-pad-inventory.json').read_text())}
held=json.loads((R/'remaining-footprint-checks.json').read_text())['held_pad_records']
byref={}
for p in held:byref.setdefault(p['reference'],[]).append(p)
configs={
 'RE1':('ENCODER',180,{'H183':'A','H184':'C','H185':'B','H187':'1','H186':'2','SLOT1':'SH1','SLOT2':'SH2'}),
 'S4':('POWER SW',0,dict(zip(['H070','H075','H071','H074','H072','H073'],map(str,range(1,7))))),
 'S5':('TONE SW',0,dict(zip(['H076','H081','H077','H080','H078','H079'],map(str,range(1,7))))),
 'S1':('FLASH SW',0,dict(zip(['H082','H087','H083','H086','H084','H085'],map(str,range(1,7))))),
 'S3':('LASER SW',0,dict(zip(['H088','H093','H089','H092','H090','H091'],map(str,range(1,7))))),
 'S2':('CAM FLASH',0,dict(zip(['H096','H097','H095','H098','H094','H099'],map(str,range(1,7))))),
 'B0':('B0',0,{'H156':'1','H159':'2','H157':'3','H158':'4'}),
 'B1':('B1',0,{'H153':'1','H154':'2','H152':'3','H155':'4'}),
 'LED1':('D1',0,{'H151':'C','H150':'A'}),
 'LED2':('D1',0,{'H119':'C','H120':'A'}),
 'LED3':('D1',-90,{'H131':'C','H130':'A'}),
 'AUDIO':('TONE',180,{'H068':'P','H069':'N'}),
}
checks=[];modules=[]
board=(R/'complete-geometry-review.kicad_pcb').read_text()
# Original module records are balanced S expressions; split with a small scanner.
def expressions(text,token):
 starts=[m.start() for m in re.finditer(r'\('+token+r'\s',text)]
 for start in starts:
  depth=0;quoted=False;escape=False
  for i in range(start,len(text)):
   ch=text[i]
   if quoted:
    if escape:escape=False
    elif ch=='\\':escape=True
    elif ch=='"':quoted=False
   elif ch=='"':quoted=True
   elif ch=='(':depth+=1
   elif ch==')':
    depth-=1
    if depth==0:yield start,i+1,text[start:i+1];break
for start,end,mod in expressions(board,'module'):
 ref=re.search(r'\(fp_text reference "([^"]+)"',mod)[1]
 name='Kerf_'+ref+'_original'
 mod=re.sub(r'\(module "[^"]+"','(module "'+name+'"',mod,count=1)
 if ref in configs:
  upstream,angle,mapping=configs[ref];sp={p['number']:p for p in source[upstream]['pads']}
  pts=[p for p in byref[ref] if p.get('source_x_mm') is not None]
  rad=math.radians(angle)
  def rotated(p):return (p['x_mm']*math.cos(rad)-p['y_mm']*math.sin(rad),p['x_mm']*math.sin(rad)+p['y_mm']*math.cos(rad))
  anchor=pts[0];a=rotated(sp[mapping[anchor['source_hole']]])
  shift=(anchor['source_x_mm']+20-a[0],83.5-anchor['source_y_mm']-a[1])
  for p in pts:
   n=mapping[p['source_hole']];x,y=rotated(sp[n]);err=max(abs(x+shift[0]-p['source_x_mm']-20),abs(y+shift[1]-(83.5-p['source_y_mm'])))
   assert err<.0004,(ref,n,err)
   checks.append({'reference':ref,'hole':p['source_hole'],'pin':n,'upstream_reference':upstream,'rotation_deg':angle,'max_position_difference_mm':err,'evidence':'Rigid footprint-coordinate match; Mk III copper/assembly orientation considered. Buzzer polarity deliberately corrected.' if ref=='AUDIO' else 'Rigid footprint-coordinate match to supplied-schematic-matching upstream PCB; not full net equivalence.'})
  for old,new in mapping.items():mod=mod.replace('(pad "'+old+'"','(pad "'+new+'"')
  mod=mod.replace('HOLD_PIN_MAP','NUMBERED_ORIGINAL')
 elif ref=='B2_LOC':
  # Unequal locator diameters determine orientation and translation uniquely.
  loc=byref[ref][0];up=source['NAV']['pads'][0]
  dx=loc['source_x_mm']+20-up['x_mm'];dy=83.5-loc['source_y_mm']-up['y_mm']
  origin=(loc['source_x_mm']+20,83.5-loc['source_y_mm'])
  pads=[]
  for p in source['NAV']['pads']:
   if not p['number']:continue
   x=p['x_mm']+dx-origin[0];y=p['y_mm']+dy-origin[1]
   pads.append(f'(pad "{p["number"]}" smd rect (at {x:.6f} {y:.6f} 45) (size {p["size_mm"][0]} {p["size_mm"][1]}) (layers F.Cu F.Paste F.Mask) (solder_mask_margin 0.1016))')
  mod=mod[:-1]+'\n'+'\n'.join(pads)+'\n)'
  mod=mod.replace('HOLD_PIN_MAP','NAVIGATION_SOURCE_REFERENCE')
  # Source-derived SMD pads remain labelled for Gerber comparison, not accepted yet.
 modules.append(mod)
 standalone=re.sub(r'\(tedit 0\) \(at [^)]+\)','(tedit 0)',mod,count=1)
 (lib/(name+'.kicad_mod')).write_text(standalone)
# Preserve board header and drawing records, replacing only module records.
new=board
for start,end,old in reversed(list(expressions(board,'module'))):new=new[:start]+modules.pop()+new[end:]
(OUT/'numbered-carrier-review.kicad_pcb').write_text(new)
with zipfile.ZipFile(OUT/'numbered-carrier-review.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(OUT/'numbered-carrier-review.kicad_pcb','numbered-carrier-review.kicad_pcb')
(OUT/'pin-number-evidence.json').write_text(json.dumps({'checks':checks,'scope':'51 formerly held round pads numbered with rigid-transform evidence. Encoder shield and navigation SMD details need separate review; no electrical release.'},indent=2)+'\n')
print('Numbered round pads:',len(checks),'max coordinate difference:',max(c['max_position_difference_mm'] for c in checks))
