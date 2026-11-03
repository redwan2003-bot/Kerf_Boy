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
 supplemental=read('supplemental-schdoc-inventory.json')
 source=ROOT/supplemental['source']
 check(source.stat().st_size==supplemental['bytes'] and hashlib.sha256(source.read_bytes()).hexdigest()==supplemental['sha256'],'Supplemental SchDoc source changed')
 check(supplemental['component_count']==40 and supplemental['pin_count']==179,'Supplemental SchDoc counts changed')
 checks=supplemental['existing_85_pad_pin_identifier_checks']
 check(len(checks)==85 and all(c['pin_present'] for c in checks),'Supplemental pin identifier checks failed')
 original=read('original-through-hole-geometry.json');check(len(original['holes'])==189 and len(original['slots'])==2,'Source drill count mismatch')
 mapping=read('reconstructed-pin-map.json');check(len(mapping)==85,'Mapped pad count mismatch');check(len({x['hole_id'] for x in mapping})==85,'Repeated mapped source hole');check(len({(x['reference'],x['pin']) for x in mapping})==85,'Duplicate component pin')
 held=read('remaining-footprint-checks.json');check(held['all_component_round_holes_accounted']==138 and held['small_unassigned_via_candidates']==51,'Hole accounting mismatch')
 roundtrip=read('independent-footprint-verification.json');check(roundtrip['footprints']==24 and roundtrip['round_pads']==138 and roundtrip['routed_slots']==2 and not roundtrip['errors'],'Recorded independent CAD check failed')
 for folder,n in [('OriginalCarrier.pretty',11),('UnresolvedOriginal.pretty',13)]:check(len(list((DATA/folder).glob('*.kicad_mod')))==n,f'Wrong footprint count: {folder}')
 copper=read('four-layer-connectivity-check.json')
 check(not copper['conflicts'] and len(copper['known_power_anchor_checks'])==9 and all(r['pass'] for r in copper['known_power_anchor_checks']),'Copper anchor checks failed')
 source=ROOT/'hardware/reference/original/Project Outputs/Project Outputs for CHIP_BOY_Mk_III'
 for ext,digest in copper['source_sha256'].items():check(hashlib.sha256((source/f'CHIPBOY_Mk_III.{ext}').read_bytes()).hexdigest()==digest,f'Copper trace source mismatch: {ext}')
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
