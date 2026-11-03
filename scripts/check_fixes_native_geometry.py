"""Independent pcbnew/native-library comparison of the complete component import."""
from pathlib import Path
import json, zipfile, hashlib, math
import pcbnew

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/easyeda/qualification-fixes'
archive=OUT/'native-gp7-navigation-review.epro2'
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    data=z.read(next(n for n in z.namelist() if n.endswith('.epru'))).decode()
docs={}
for line in data.splitlines():
    if not line: continue
    header,payload=line.split('||',1)
    if not payload.rstrip('|'):continue # Native deletion tombstone
    h,v=json.loads(header),json.loads(payload.rstrip('|'))
    if h['type']=='DOCHEAD': current={'head':v,'rows':[]};docs[v['uuid']]=current
    else: current['rows'].append((h,v))
def attrs(doc):
    result={}
    for h,v in doc['rows']:
        if h['type']=='ATTR':result.setdefault(v['parentId'],{})[v['key']]=v['value']
    return result
page=docs['1d37e42034445c5d'];at=attrs(page)
board=pcbnew.LoadBoard(str(OUT/'complete-fixed-review.kicad_pcb'))
expected={f.GetReference():f for f in board.GetFootprints()}
checks=[];bindings={};errors=[]
mm=pcbnew.ToMM
for h,c in page['rows']:
    if h['type']!='COMPONENT':continue
    a=at[h['id']];ref=a['Designator'];fp=expected[ref]
    meta=next(v for k,v in docs[a['Device']]['rows'] if k['type']=='META')
    uuid=meta['attributes']['Footprint'];native=docs[uuid]
    bindings[ref]={'footprint_uuid':uuid,'device_uuid':a['Device']}
    assert c['angle']==0
    remaining=list(fp.Pads())
    for ph,p in native['rows']:
        if ph['type']!='PAD':continue
        # EasyEDA normalizes bottom libraries to top-side local geometry.
        sign=-1 if c['layerId']==2 else 1
        x=(c['x']+p['centerX'])*.0254
        y=-(c['y']+sign*p['centerY'])*.0254
        q=min(remaining,key=lambda q:math.hypot(mm(q.GetPosition().x)-x,mm(q.GetPosition().y)-y))
        remaining.remove(q)
        size=q.GetSize();drill=q.GetDrillSize();pos=q.GetPosition()
        differences=[abs(x-mm(pos.x)),abs(y-mm(pos.y)),abs(p['defaultPad']['width']*.0254-mm(size.x)),abs(p['defaultPad']['height']*.0254-mm(size.y))]
        differences += [abs(a-b) for a,b in zip(sorted([mm(drill.x),mm(drill.y)]),sorted([p['hole']['width']*.0254,p['hole']['height']*.0254]))]
        if not drill.x:
            differences += [abs(p['topSolderExpansion']*.0254-mm(q.GetLocalSolderMaskMargin() or 0)),abs(p['topPasteExpansion']*.0254-mm(q.GetLocalSolderPasteMargin() or 0))]
        number_ok=p['num']==q.GetNumber()
        # Rectangle angles repeat every 180 degrees. Slot long-axis is separate.
        angle_error=abs(((sign*p['padAngle']-q.GetOrientationDegrees()+90)%180)-90)
        if abs(mm(size.x)-mm(size.y))<.000001 and p['defaultPad']['padType']=='ELLIPSE':angle_error=0
        plated_ok=p['plated']==(q.GetAttribute()!=pcbnew.PAD_ATTRIB_NPTH)
        slot_angle_error=0
        if abs(mm(drill.x)-mm(drill.y))>.000001:
            native_axis=p['padAngle']+p['relativeAngle']+(90 if p['hole']['height']>p['hole']['width'] else 0)
            expected_axis=q.GetOrientationDegrees()+(90 if drill.y>drill.x else 0)
            slot_angle_error=abs(((sign*native_axis-expected_axis+90)%180)-90)
        row={'reference':ref,'pin':p['num'],'position_mm':[x,y],'max_geometry_difference_mm':max(differences),'angle_difference_deg':angle_error,'number_matches':number_ok,'plating_matches':plated_ok,'native_hole':p['hole'],'native_relative_hole_angle':p['relativeAngle']}
        checks.append(row)
        row['slot_axis_difference_deg']=slot_angle_error
        if max(differences)>.0003 or angle_error>.00001 or slot_angle_error>.00001 or not number_ok or not plated_ok:errors.append(row)
    assert not remaining,ref
assert len(bindings)==40 and len(checks)==181
result={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'footprints':40,'pads':181,'electrical_pads':sum(bool(c['pin']) for c in checks),'tolerance_mm':.0003,'max_geometry_difference_mm':max(c['max_geometry_difference_mm'] for c in checks),'errors':errors,'checks':checks,'scope':'Native library vs independently parsed input: coordinates, pad sizes, drill dimensions, pad numbers, pad angles and plating. Does not establish circuit correctness or physical fit.'}
(OUT/'native-fixes-geometry.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'native-footprint-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
print({k:v for k,v in result.items() if k not in ['checks','errors']})
print('Errors:',errors)
assert not errors
