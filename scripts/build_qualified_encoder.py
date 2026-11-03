"""User-approved correction for the explicitly selected Bourns PEC12R-4217F-S0024.

Original reconstruction is retained. Manufacturer PEC12R datasheet rev 07/21,
page 4: 13.2 mm locating-slot spacing; 5 mm signal/switch spacing, 14.5 mm rows.
"""
from pathlib import Path
import re,zipfile,json
R=Path(__file__).resolve().parents[1];O=R/'hardware/easyeda/qualification';O.mkdir(exist_ok=True)
lib=O/'QualifiedParts.pretty';lib.mkdir(exist_ok=True)
old=(R/'hardware/easyeda/step3-numbered/KerfOriginal.pretty/Kerf_RE1_original.kicad_mod').read_text()
new=old.replace('Kerf_RE1_original','Kerf_RE1_PEC12R4217F_S0024').replace('REFERENCE ONLY - electrical pad numbering unresolved; not for fabrication','Bourns PEC12R-4217F-S0024: manufacturer land-pattern correction; physical fit and fabrication tolerances pending').replace('NUMBERED_ORIGINAL','PEC12R-4217F-S0024')
# Preserve the original pad-1 datum; normalize the specified nominal pitch.
new=new.replace('2.500122','2.5').replace('4.99999','5.0').replace('-14.500098','-14.5')
new=new.replace('-3.099816 -7.500112','-4.1 -7.5').replace('8.100060 -7.500112','9.1 -7.5')
# Midpoints of the manufacturer's permitted finished-hole dimensions.
new=new.replace('(drill 1.199896)','(drill 1.1)').replace('(drill oval 1.999996 2.299716)','(drill oval 2.0 2.2)')
(lib/'Kerf_RE1_PEC12R4217F_S0024.kicad_mod').write_text(new)
board=(R/'hardware/easyeda/step3-numbered/complete-component-review.kicad_pcb').read_text()
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
 if '(fp_text reference "RE1"' in mod:
  pos=re.search(r'\(tedit 0\) (\(at [^)]+\))',mod)[1]
  replacement=new.replace('(tedit 0)','(tedit 0) '+pos,1)
  full_board=full_board[:start]+replacement+full_board[end:]
 else:replacement=''
 board=board[:start]+replacement+board[end:]
p=O/'qualified-encoder-review.kicad_pcb';p.write_text(board)
with zipfile.ZipFile(O/'qualified-encoder-review.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(p,p.name)
print('Prepared corrected encoder: 13.2 mm slots, 1.1 mm finished round holes, 2.0 x 2.2 mm slots.')

(O/'complete-qualified-review.kicad_pcb').write_text(full_board)
