#!/usr/bin/env python3
"""Portable output-level smoke tests; not historical geometric certification."""
import csv,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
p=Path(__file__).resolve().parent
qa=json.loads((p/'QA_REPORT.json').read_text())
assert hashlib.sha256((p/'SOURCE_MIRRORED_UNMODIFIED.png').read_bytes()).hexdigest()==qa['input_sha256']
with (p/'CIRCLE_FIT_REGISTER.csv').open() as f: circles=list(csv.DictReader(f))
with (p/'FACE_REGISTER.csv').open() as f: faces=list(csv.DictReader(f))
assert len(circles)==11
assert len(faces)==qa['faces_over_60_px']
assert all(float(c['radius_px'])>0 for c in circles)
assert all(float(c['circumference_ink_coverage'])>=0.70 for c in circles)
for name in ['01_BLACK_ONLY.svg','02_SELECTABLE_FACES.svg','03_CONSTRUCTION_ANALYSIS.svg','04_CLASSIFIED_CANDIDATE_FACES.svg']:
    ET.parse(p/name)
print('R03 smoke tests passed: source hash, 11 circle candidates, face counts, 4 parseable SVGs')
