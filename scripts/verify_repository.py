from pathlib import Path
import ast,hashlib,json,re
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'hardware/reconstruction'
def read(name):return json.loads((DATA/name).read_text(encoding='utf-8-sig'))
def main():
 errors=[]
 def check(ok,message):
  if not ok:errors.append(message)
 manifest=read('source-manifest.json');check(len(manifest)==50,'Expected 50 source files')
 for item in manifest:
  p=ROOT/'hardware/reference/original'/Path(item['path'].replace('\\','/'))
  check(p.is_file(),f'Missing source: {item["path"]}')
  if p.is_file():check(p.stat().st_size==item['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Changed source: {item["path"]}')
 original=read('original-through-hole-geometry.json');check(len(original['holes'])==189 and len(original['slots'])==2,'Source drill count mismatch')
 mapping=read('reconstructed-pin-map.json');check(len(mapping)==85,'Mapped pad count mismatch');check(len({x['hole_id'] for x in mapping})==85,'Repeated mapped source hole');check(len({(x['reference'],x['pin']) for x in mapping})==85,'Duplicate component pin')
 held=read('remaining-footprint-checks.json');check(held['all_component_round_holes_accounted']==138 and held['small_unassigned_via_candidates']==51,'Hole accounting mismatch')
 roundtrip=read('independent-footprint-verification.json');check(roundtrip['footprints']==24 and roundtrip['round_pads']==138 and roundtrip['routed_slots']==2 and not roundtrip['errors'],'Recorded independent CAD check failed')
 for folder,n in [('OriginalCarrier.pretty',11),('UnresolvedOriginal.pretty',13)]:check(len(list((DATA/folder).glob('*.kicad_mod')))==n,f'Wrong footprint count: {folder}')
 for p in (ROOT/'scripts').glob('*.py'):
  try:ast.parse(p.read_text(encoding='utf-8-sig'))
  except SyntaxError as e:errors.append(f'{p.name}: {e}')
 for p in ROOT.rglob('*.md'):
  if 'reference' in p.parts:continue # Preserve third-party README, including missing upstream image links.
  for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
   if re.match(r'^(?:https?://|mailto:|#)',link):continue
   target=unquote(link.split('#')[0]);check((p.parent/target).exists(),f'Broken local link {p.relative_to(ROOT)} -> {link}')
 if errors:raise SystemExit('\n'.join(errors))
 print('PASS: 50 source hashes; 189 round holes + 2 slots; 24 footprint groups; 85 unique mapped pads; saved independent checks; Python syntax; local documentation links.')
 print('Scope: repository integrity and recorded geometry evidence, not electrical/production certification.')
if __name__=='__main__':main()
