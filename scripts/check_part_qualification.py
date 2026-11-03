"""Manufacturer-pattern checks and a complete component qualification register.

PASS here is a dimensional subcheck, never physical qualification.
Run with KiCad's Python. Manufacturer values are manually transcribed from the
linked primary drawings; the PCB dimensions are read independently by pcbnew.
"""
from pathlib import Path
import json,math,pcbnew
R=Path(__file__).resolve().parents[1];O=R/'hardware/easyeda/qualification'
old=pcbnew.LoadBoard(str(R/'hardware/easyeda/step3-numbered/complete-component-review.kicad_pcb'))
fps={f.GetReference():f for f in old.GetFootprints()}
new_board=pcbnew.LoadBoard(str(O/'qualified-encoder-review.kicad_pcb'))
new=next(iter(new_board.GetFootprints()))
def pads(f):return {p.GetNumber():p for p in f.Pads() if p.GetNumber()}
def distance(f,a,b):
 p=pads(f);v=p[a].GetPosition()-p[b].GetPosition();return math.hypot(pcbnew.ToMM(v.x),pcbnew.ToMM(v.y))
sources={
 'bourns':'https://www.bourns.com/docs/product-datasheets/pec12r.pdf',
 'alps':'https://tech.alpsalpine.com/e/products/detail/SKHHANA010/',
 'alps_drawing':'https://tech.alpsalpine.com/cms.media/product_catalog_ta_01_skhh_en_bf15276fa8.pdf',
 'nav':'https://configured-product-images.s3.amazonaws.com/2D/specs/JS1400BFQ.pdf',
 'microchip':'https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23008-and-MCP23008-Data-Sheet-DS20001919.pdf',
 'seeed':'https://wiki.seeedstudio.com/xiao_esp32s3_sense_filesystem/',
 'aos':'https://www.aosmd.com/sites/default/files/res/data_sheets/AO3400A.pdf',
 'slide':'https://www.mouser.com/datasheet/2/26/APEM_Microminiature_slide_switches_MHSS_MS-3396147.pdf'}
checks=[]
def check(ref,measure,value,nominal,tol,source):
 checks.append(dict(reference=ref,measurement=measure,measured_mm=value,nominal_mm=nominal,tolerance_mm=tol,pass_check=abs(value-nominal)<=tol,source=source))
for ref in ['B0','B1']:
 f=fps[ref];check(ref,'row width',distance(f,'1','2'),6.5,.1,'alps_drawing');check(ref,'row separation',distance(f,'1','3'),4.5,.1,'alps_drawing')
 for n,p in pads(f).items():check(ref,'finished drill '+n,pcbnew.ToMM(p.GetDrillSize().x),1,.05,'alps_drawing')
check('U1','pin pitch',distance(fps['U1'],'1','2'),2.54,.00001,'microchip')
check('U1','formed row pitch',distance(fps['U1'],'1','18'),7.62,.00001,'microchip')
check('RE1_original','mounting slot centers',distance(fps['RE1'],'SH1','SH2'),13.2,.0003,'bourns')
for a,b,nom in [('SH1','SH2',13.2),('A','B',5),('1','2',5),('A','1',14.5),('C','A',2.5)]:check('RE1_corrected',a+' to '+b,distance(new,a,b),nom,.000001,'bourns')
for n,p in pads(new).items():
 d=p.GetDrillSize()
 if n.startswith('SH'):
  check('RE1_corrected',n+' slot width',pcbnew.ToMM(d.x),2,.000001,'bourns')
  check('RE1_corrected',n+' slot length',pcbnew.ToMM(d.y),2.2,.1,'bourns')
 else:check('RE1_corrected',n+' finished drill',pcbnew.ToMM(d.x),1.1,.1,'bourns')
assert all(c['pass_check'] for c in checks if c['reference']!='RE1_original')
assert not next(c for c in checks if c['reference']=='RE1_original')['pass_check']
cross=json.loads((R/'hardware/easyeda/step3-numbered/schematic-crosswalk.json').read_text())['components']
source_inventory={c['designator']:c for c in json.loads((R/'hardware/reconstruction/supplemental-schdoc-inventory.json').read_text())['components']}
rows=[]
for c in cross:
 ref=c['review_designator'];s=source_inventory[c['source_designator']]
 row={'reference':ref,'source_label':c['source_designator'],'source_comment':s['comment'],'physical_test':'NOT_RUN_NO_PARTS','qualification':'HOLD_IDENTITY_OR_RATINGS','required_evidence':'Exact part/order code, matching drawing, ratings, body/height/clearance, and physical fit.'}
 if ref in ['B0','B1']:row.update(qualification='DRAWING_PATTERN_PASS_PHYSICAL_PENDING',selected_part='Alps SKHHANA010',body_mm=[6,6,9.5],rating='50 mA at 12 VDC maximum; low-level minimum 10 uA at 1 VDC',source='alps',required_evidence='Confirm purchased SKHHANA010; fit 9.5 mm actuator to enclosure and record finished-hole tolerance.')
 elif ref=='RE1':row.update(qualification='CORRECTED_PATTERN_PHYSICAL_PENDING',selected_part='Bourns PEC12R-4217F-S0024',source='bourns',rating='Encoder and push contacts: 10 mA at 5 VDC',required_evidence='Use corrected 13.2 mm slot pattern; fit actual part and knob, check actuator/enclosure clearance and finished-hole tolerances.')
 elif ref=='B2_LOC':row.update(qualification='LAND_PATTERN_DEVIATIONS_REVIEW',selected_part='E-Switch JS1400BFQ (source comment)',body_mm=[7.7,7.4,5],source='nav',rating='50 mA at 12 VDC',required_evidence='Original locating holes 0.8001/1.100074 mm vs drawing 0.75/1.05; grounding lands 2.0 x 1.8 mm are correct; 1.85 mm is a signal-land gap. Resolve deviations and define grounded chassis tabs, actuator cap and courtyard.')
 elif ref=='U1':row.update(qualification='ELECTRICAL_FAIL_GP7_INPUT',selected_part='MCP23008, 18-pin PDIP; ordering suffix not frozen',source='microchip',required_evidence='Move encoder push input off GP7; GP7 is output-only in current datasheet. Confirm purchased PDIP suffix and body/lead envelope.')
 elif ref=='M1':row.update(qualification='HOLD_EXACT_SENSE_REVISION_AND_PIN_BUDGET',source='seeed',required_evidence='Freeze XIAO base/Sense expansion revisions; reserve SD D8/D9/D10 and revision-specific CS, camera/microphone pins, antenna and USB/SD access.')
 elif ref in ['S1','S2','S3','S4','S5']:row.update(qualification='HOLD_MHSS1104_IDENTITY_AND_LOAD',candidate='APEM MHSS1104 from all five upstream PCB footprint names',source='slide',rating='Conditional on MHSS1104 identity: 300 mA at 6 VDC',required_evidence='Match actual switch and drawing; verify contact pairs and actuator height; prove load/inrush below rating or use switch as control input.')
 elif ref=='T1':row.update(qualification='PINOUT_VERIFIED_LOAD_THERMAL_PENDING',selected_part='AO3400A',source='aos',required_evidence='Verify G1/S2/D3, source-ground and laser-return net; qualify exact load/current, gate drive, loss and temperature.')
 elif ref.startswith('R') and ref!='RE1':row['required_evidence']='Select exact original-compatible SMD package with resistance, tolerance, power and voltage rating; pad shape alone does not identify rated part.'
 elif ref.startswith('C'):row['required_evidence']='Select exact original-compatible SMD package, voltage rating, dielectric/polarity, tolerance and ESR; C3/C4 are 100 uF in Mk III.'
 rows.append(row)
assert len(rows)==40 and len({r['reference'] for r in rows})==40
out={'date':'2026-11-03','user_has_parts':False,'full_qualification':False,'sources':sources,'dimension_checks':checks,'components':rows,'external_holds':['Battery exact chemistry/model/capacity/protection/charge limits and connector polarity','Laser module model/current/driver/interface','Speaker impedance/power and buzzer active/passive identity','Enclosure clearance and actual assembled stack height'],'physical_tests':'Not performed; user reports no parts available.'}
(O/'part-qualification.json').write_text(json.dumps(out,indent=2)+'\n')
print('Register: 40 components. Manufacturer subchecks passed:',sum(c['pass_check'] for c in checks),'Original encoder mismatch confirmed:',sum(not c['pass_check'] for c in checks))
print('Full qualification remains blocked by identified electrical/identity issues and absent hardware.')
