"""Make a separately labelled component-binding review; circuit redesign remains pending."""
from pathlib import Path
import json,zipfile
R=Path(__file__).resolve().parents[1];O=R/'hardware/easyeda/step3-numbered'
lines=(R/'hardware/easyeda/CHIPBOY_Mk_II_ascii_review.SchDoc').read_text().splitlines()
records=[dict(x.split('=',1) for x in l.split('|') if '=' in x) for l in lines]
inventory=json.loads((R/'hardware/reconstruction/supplemental-schdoc-inventory.json').read_text())['components']
cross={'Xiao ESP32S3':'M1','128x64 OLED':'DS','MCP23008':'U1','BNO055':'U4','GY-BME280':'J5','DF PLAYER':'U2','TOF400C-Vl53l1x':'J4','ATGM336h':'U3','Buzzer':'AUDIO','Navigation Switch':'B2_LOC','PEC12R-4217F-S0024':'RE1','SPK1':'LS1','SW5':'S5','SW1':'S4','SW4':'S3','SW3':'S1','SW2':'S2','R1':'R2','R2':'R3','R3':'R1'}
changes=[]
for c in inventory:
 old=c['designator'];new=cross.get(old,old);idx=c['record_index'];component=records[idx]
 component['LibReference']='Kerf_'+new+'_review_symbol';component['DesignItemId']=component['LibReference']
 for r in records:
  if r.get('OwnerIndex')==str(idx-1):
   if r.get('RECORD')=='34':r['Text']=new
   if r.get('RECORD')=='41' and r.get('Name')=='Comment':
    if new=='T1':r['Text']='AO3400A'
    elif new in ['C3','C4']:r['Text']='100 uF'
   if r.get('RECORD')=='2':
    if new=='T1':r['Designator']={'G':'1','S':'2','D':'3'}[r['Name']]
    if new=='LS1':r['Designator']={'P':'1','M':'2'}[r['Designator']]
  if r.get('RECORD')=='45':
   parent=records[int(r['OwnerIndex'])+1]
   if parent.get('OwnerIndex')==str(idx-1):
    r['ModelName']='Kerf_'+new+'_original';r['ModelDatafileEntity0']=r['ModelName']
 changes.append({'source_designator':old,'review_designator':new,'symbol_reference':component['LibReference'],'footprint_name':'Kerf_'+new+'_original'})
assert len({c['review_designator'] for c in changes})==40
path=O/'Kerf_Step3_Binding_Review.SchDoc'
path.write_bytes(('\r\n'.join('|'+ '|'.join(k+'='+v for k,v in r.items()) for r in records)+'\r\n').encode())
with zipfile.ZipFile(O/'step3-binding-review.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(path,path.name)
(O/'schematic-crosswalk.json').write_text(json.dumps({'components':changes,'scope':'Component-binding review derived from Mk II. T1 G1/S2/D3 and speaker 1/2 adapted to Mk III. R1-R3 references follow Mk III LED positions. Wires are retained for reference and NOT approved; power/header/buzzer polarity and full circuit reconciliation remain Stage 4/5 work.'},indent=2)+'\n')
print('Prepared 40 uniquely named symbols and footprint model references; circuit review only.')
