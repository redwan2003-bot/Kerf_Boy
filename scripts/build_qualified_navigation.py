"""Correct JS1400BFQ locator holes; preserve correct original copper dimensions.
Drawing N211128 rev D. This does not establish physical fit.
"""
from pathlib import Path
import re,zipfile,json
R=Path(__file__).resolve().parents[1];O=R/'hardware/easyeda/qualification-fixes';O.mkdir(parents=True,exist_ok=True)
lib=O/'QualifiedParts.pretty';lib.mkdir(exist_ok=True)
old=(R/'hardware/easyeda/step3-numbered/KerfOriginal.pretty/Kerf_B2_LOC_original.kicad_mod').read_text()
new=old.replace('Kerf_B2_LOC_original','Kerf_B2_JS1400BFQ').replace('REFERENCE ONLY - electrical pad numbering unresolved; not for fabrication','JS1400BFQ: corrected locator diameters; physical fit pending').replace('NAVIGATION_SOURCE_REFERENCE','JS1400BFQ')
new=new.replace('0.8001 0.8001','0.75 0.75').replace('(drill 0.800100)','(drill 0.75)').replace('1.100074 1.100074','1.05 1.05').replace('(drill 1.100074)','(drill 1.05)')
# 1.85 mm is the signal-land inner-edge gap, NOT a shield-land dimension.
# The drawing's 9.9 mm outer / 6.3 mm inner shield span gives 1.8 mm lands.
(lib/'Kerf_B2_JS1400BFQ.kicad_mod').write_text(new)
board=(R/'hardware/easyeda/qualification/complete-qualified-review.kicad_pcb').read_text()
starts=[m.start() for m in re.finditer(r'\(module\s',board)];spans=[]
for start in starts:
 depth=0;quoted=False;escape=False
 for i in range(start,len(board)):
  ch=board[i]
  if quoted:
   if escape:escape=False
   elif ch=='\\':escape=True
   elif ch=='"':quoted=False
  elif ch=='"':quoted=True
  elif ch=='(':depth+=1
  elif ch==')':
   depth-=1
   if depth==0:spans.append((start,i+1,board[start:i+1]));break
full_board=board
for start,end,mod in reversed(spans):
 if '(fp_text reference "B2_LOC"' in mod:
  pos=re.search(r'\(tedit 0\) (\(at [^)]+\))',mod)[1]
  replacement=new.replace('(tedit 0)','(tedit 0) '+pos,1)
  full_board=full_board[:start]+replacement+full_board[end:]
 else:replacement=''
 board=board[:start]+replacement+board[end:]
p=O/'qualified-navigation-review.kicad_pcb';p.write_text(board)
with zipfile.ZipFile(O/'qualified-navigation-review.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(p,p.name)
print('Prepared JS1400BFQ: 0.75/1.05 mm locators; correct existing copper retained.')

(O/'complete-fixed-review.kicad_pcb').write_text(full_board)
