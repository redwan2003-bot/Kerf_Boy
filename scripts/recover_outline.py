from pathlib import Path
import math, re, json

ROOT=Path(__file__).resolve().parents[1]/'hardware/reconstruction'
SOURCE=Path(__file__).resolve().parents[1]/'hardware/reference/original/Project Outputs/Project Outputs for CHIP_BOY_Mk_III/CHIPBOY_Mk_III.GM1'
scale=25.4/100000
pos=(0.,0.)
mode=1
paths=[]
for line in SOURCE.read_text().splitlines():
    if line in ('G01*','G02*','G03*'):
        mode=int(line[1:3]);continue
    if not re.match('[XY]',line):continue
    v={k:float(n)*scale for k,n in re.findall(r'([XYIJ])(-?\d+)',line)}
    end=(v.get('X',pos[0]),v.get('Y',pos[1]))
    draw='D01' in line
    if draw:
        if mode==1: paths.append([pos,end])
        else:
            center=(pos[0]+v.get('I',0),pos[1]+v.get('J',0))
            r=math.dist(pos,center)
            a=math.atan2(pos[1]-center[1],pos[0]-center[0])
            b=math.atan2(end[1]-center[1],end[0]-center[0])
            delta=(b-a)%(2*math.pi)
            if math.dist(pos,end)<1e-8:delta=2*math.pi
            if mode==2:delta=delta-2*math.pi
            n=max(2,math.ceil(abs(delta)/(2*math.acos(max(-1,1-0.003/r)))))
            pts=[(center[0]+r*math.cos(a+delta*i/n),center[1]+r*math.sin(a+delta*i/n)) for i in range(n+1)]
            pts[0]=pos;pts[-1]=end
            paths.append(pts)
    pos=end

loops=[];gaps=[]
while paths:
    loop=paths.pop(0)
    while math.dist(loop[-1],loop[0])>0.06:
        candidates=[(math.dist(loop[-1],p[j]),i,j) for i,p in enumerate(paths) for j in (0,-1)]
        if not candidates:raise ValueError('Unclosed outline')
        d,i,j=min(candidates)
        if d>0.06:raise ValueError(f'Outline gap {d} mm')
        p=paths.pop(i)
        if j==-1:p.reverse()
        gaps.append(d)
        # Merge small drafting discrepancies at their midpoint, avoiding slivers.
        loop[-1]=((loop[-1][0]+p[0][0])/2,(loop[-1][1]+p[0][1])/2)
        loop.extend(p[1:])
    gaps.append(math.dist(loop[-1],loop[0]))
    join=((loop[-1][0]+loop[0][0])/2,(loop[-1][1]+loop[0][1])/2)
    loop[-1]=join;loop[0]=join
    loops.append(loop)

def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]))/2)
loops.sort(key=area,reverse=True)
x0=min(p[0] for q in loops for p in q);y0=min(p[1] for q in loops for p in q)
loops=[[(round(x-x0,6),round(y-y0,6)) for x,y in q] for q in loops]
width=max(x for q in loops for x,y in q);height=max(y for q in loops for x,y in q)
assert len(loops)==5,(len(loops),'Expected outer perimeter, three mounting holes, one slot')
# Reject proper self-crossings in each polygon.
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
for q in loops:
    seg=list(zip(q,q[1:]))
    for i,(a,b) in enumerate(seg):
        for j,(c,d) in enumerate(seg[i+2:],i+2):
            if i==0 and j==len(seg)-1:continue
            assert not (cross(a,b,c)*cross(a,b,d)<-1e-12 and cross(c,d,a)*cross(c,d,b)<-1e-12),f'Self crossing: {i} {j} {a} {b} {c} {d}'
lines=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1009','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
for q in loops:
    lines+=['0','POLYLINE','8','BOARD_OUTLINE','66','1','70','1','10','0','20','0','30','0']
    for x,y in q[:-1]:lines+=['0','VERTEX','8','BOARD_OUTLINE','10',str(x),'20',str(y),'30','0']
    lines+=['0','SEQEND']
lines+=['0','ENDSEC','0','EOF']
(ROOT/'carrier-outline-draft.dxf').write_text('\n'.join(lines)+'\n')
(ROOT/'outline-geometry.json').write_text(json.dumps(loops))
report={'source':str(SOURCE),'status':'Recovered reference outline, not fabrication release','width_mm':width,'height_mm':height,'closed_contours':len(loops),'self_crossings':0,'max_source_endpoint_gap_mm':max(gaps),'arc_chord_error_target_mm':0.003,'note':'Tiny source drafting gaps joined; arcs approximated by line segments. Validate fabrication tolerances before release.'}
(ROOT/'outline-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
