"""Reproduce review imports. These are not electrically validated design files."""
from pathlib import Path
import hashlib, json, struct, zipfile
import olefile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/easyeda'
SOURCE = ROOT / 'hardware/reference/supplemental/CHIPBOY_Mk_II.SchDoc'
with olefile.OleFileIO(SOURCE) as ole:
    data = ole.openstream('FileHeader').read()
records = []
offset = 0
while offset < len(data):
    length = struct.unpack_from('<I', data, offset)[0]
    offset += 4
    record = data[offset:offset + length]
    assert len(record) == length and record.endswith(b'\0')
    records.append(record[:-1])
    offset += length
assert offset == len(data) and len(records) == 1236
assert b'Binary File' in records[0]
records[0] = records[0].replace(b'Binary File', b'Ascii File')
ascii_path = OUT / 'CHIPBOY_Mk_II_ascii_review.SchDoc'
ascii_path.write_bytes(b'\r\n'.join(records) + b'\r\n')
board = (ROOT / 'hardware/reconstruction/complete-geometry-review.kicad_pcb').read_text()
pcb_path = OUT / 'carrier-geometry-review.kicad_pcb'
pcb_path.write_text(board)
for path, archive in [(ascii_path, 'schdoc-ascii-review.zip'), (pcb_path, 'carrier-geometry-review.zip')]:
    with zipfile.ZipFile(OUT / archive, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(path, path.name)
print(f'Prepared {len(records)} schematic records and the existing board outline (without duplicating it). Review only.')
