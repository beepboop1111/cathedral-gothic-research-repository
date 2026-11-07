from pathlib import Path
import csv, json
from PIL import Image
p=Path(__file__).resolve().parent
with (p/'CIRCULAR_ARC_FITS.csv').open() as f: a=list(csv.DictReader(f))
with (p/'MASTER_TRANSFER_QA.csv').open() as f: b=list(csv.DictReader(f))
q=json.loads((p/'QA_REPORT.json').read_text())
assert len(a)==42 and len(b)==7 and len({r['name'] for r in a})==7
assert all(float(r['rms_px'])<0.5 and float(r['n_points'])>=30 for r in a)
assert q['number_complete_cusps_validated']==0
assert Image.open(p/'SOURCE_MIRRORED_UNMODIFIED.png').size==(1563,1996)
assert all((p/n).stat().st_size>500 for n in ['02_MEASURED_LOBE_ARCS.svg','06_MASTER_CLOSEUP_CONSTRUCTION.svg','03_MASTER_FIT_OVERLAY.png'])
print('R04 tests: PASS (42 circular-section fits / 7 roundels; cusps unverified)')
