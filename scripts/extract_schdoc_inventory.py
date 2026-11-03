"""Extract explicit symbol fields from the supplied SchDoc; no netlist inference."""
from pathlib import Path
import collections,hashlib,json,struct
import olefile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'hardware/reference/supplemental/CHIPBOY_Mk_II.SchDoc'
OUT=ROOT/'hardware/reconstruction/supplemental-schdoc-inventory.json'

def extract():
 with olefile.OleFileIO(SOURCE) as ole:
  streams=['/'.join(p) for p in ole.listdir()]
  data=ole.openstream('FileHeader').read()
 pos=0; records=[]
 while pos<len(data):
  assert pos+4<=len(data),'Truncated record header'
  length=struct.unpack_from('<I',data,pos)[0];pos+=4
  assert length and pos+length<=len(data),'Unsupported/truncated record'
  raw=data[pos:pos+length];pos+=length
  assert raw.startswith(b'|') and raw.endswith(b'\0'),'Non-text record unsupported'
  fields=dict(item.split('=',1) for item in raw.rstrip(b'\0').decode('cp1252').split('|') if '=' in item)
  records.append(fields)
 assert pos==len(data)
 assert int(records[0]['Weight'])==len(records)-1
 # OwnerIndex excludes the leading format-header record.
 children=collections.defaultdict(list)
 for index,r in enumerate(records):
  if 'OwnerIndex' in r:children[int(r['OwnerIndex'])+1].append((index,r))
 components=[]
 for index,r in enumerate(records):
  if r.get('RECORD')!='1':continue
  direct=children[index]
  designators=[v.get('Text','') for _,v in direct if v.get('RECORD')=='34']
  assert len(designators)==1,(index,designators)
  pins=[{'record_index':i,**{k:v[k] for k in ('Designator','Name','Location.X','Location.Y','PinLength','PinConglomerate') if k in v}} for i,v in direct if v.get('RECORD')=='2']
  assert len(pins)==int(r['AllPinCount']),(designators,len(pins),r['AllPinCount'])
  assert len({p['Designator'] for p in pins})==len(pins)
  models=[]
  for ci,cr in direct:
   if cr.get('RECORD')=='44':
    models.extend({k:mr.get(k,'') for k in ('ModelName','ModelType','ModelDatafileEntity0','IsCurrent')} for _,mr in children[ci] if mr.get('RECORD')=='45')
  parameters={v.get('Name',''):v.get('Text','') for _,v in direct if v.get('RECORD')=='41'}
  groups=collections.defaultdict(list)
  for pin in pins:groups[(pin.get('Location.X','0'),pin.get('Location.Y','0'))].append(pin['Designator'])
  components.append({'record_index':index,'designator':designators[0],'library_reference':r['LibReference'],'unique_id':r['UniqueID'],'comment':parameters.get('Comment',''),'pins':pins,'models':models,'coincident_pin_groups':[v for v in groups.values() if len(v)>1]})
 result={'source':str(SOURCE.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'bytes':SOURCE.stat().st_size,'streams':streams,'record_count':len(records),'component_count':len(components),'pin_count':sum(len(c['pins']) for c in components),'record_types':dict(collections.Counter(r.get('RECORD','HEADER') for r in records)),'scope':'Explicit fields only. Not a compiled netlist, PCB pad positions, proof of Mk III equivalence, or EasyEDA import verification.','components':components}
 aliases={'M1':'Xiao ESP32S3','U1':'MCP23008','U2':'DF PLAYER','U3':'ATGM336h','U4':'BNO055','DS':'128x64 OLED','J4':'TOF400C-Vl53l1x','J5':'GY-BME280','J1':'J1','J2':'J2','J3':'J3'}
 by_ref={c['designator']:c for c in components}
 mappings=json.loads((ROOT/'hardware/reconstruction/reconstructed-pin-map.json').read_text())
 checks=[]
 for m in mappings:
  comp=by_ref[aliases[m['reference']]]
  matches=[p for p in comp['pins'] if p['Designator']==str(m['pin'])]
  checks.append({'mk3_reference':m['reference'],'source_hole':m['hole_id'],'pin':str(m['pin']),'schdoc_designator':comp['designator'],'pin_present':len(matches)==1,'schdoc_pin_name':matches[0]['Name'] if matches else None})
 assert len(checks)==85 and all(c['pin_present'] for c in checks)
 result['existing_85_pad_pin_identifier_checks']=checks
 result['comparison_limit']='Pin identifiers exist in corresponding symbols; this does not validate their PCB hole assignment or electrical nets.'
 OUT.write_text(json.dumps(result,indent=2)+'\n')
 print(f"PASS: {len(records)} records, {result['component_count']} components, {result['pin_count']} pins; all declared pin counts matched.")
 for c in components:
  print(c['designator'],c['library_reference'],[m['ModelName'] for m in c['models']],c['coincident_pin_groups'])
if __name__=='__main__':extract()
