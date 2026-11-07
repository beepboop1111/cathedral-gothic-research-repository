import fitz,re,unicodedata,subprocess,collections,csv,json,pathlib,statistics
ROOT=pathlib.Path('/mnt/data')
P=ROOT/'global thematic and analytical index to navigate cross-references across all 9 text books raisonnedelarchi10viol.pdf'
DOC=fitz.open(P)
layout=subprocess.check_output(['pdftotext','-layout',str(P),'-'],text=True).split('\f')
assert len(DOC)==448
LETTERS='ABCDEFGHIJKLMNOPQRSTUVWXY'
RANGES={'A':(15,43),'B':(45,75),'C':(77,129),'D':(131,137),'E':(139,145),'F':(147,155),'G':(157,163),'H':(165,167),'I':(169,171),'J':(173,175),'K':(177,177),'L':(179,201),'M':(203,239),'N':(241,253),'O':(255,259),'P':(261,297),'Q':(299,299),'R':(301,319),'S':(321,387),'T':(389,407),'U':(409,409),'V':(411,433),'W':(435,437),'X':(439,439),'Y':(441,441)}
THEMES={
  'Vaults, ribs, bosses':r'\bvo[uû]t|\b(ogiv|clef de vo[uû]te|arc.doubleau|arc formeret|formeret|lierne|tierceron|nervur)',
  'Arches, arcades':r'\barc[- ](?!boutant)|\barcature|\barchivolte|\barcade|\barc[hs]?(?:\s|$)',
  'Flying buttresses':r'\barc[- ]boutant',
  'Buttresses, foundations, loads':r'\bcontre[- ]for[ti]|\bfondation|\bcha[iî]nage|\bconstruction|\bappareil|\bpouss[ée]|\bmassif',
  'Piers, shafts, supports':r'\bpilier|\bpiles?\b|\bcolon(n|e)|\bchapiteau|\bbase\b|\bcul[- ]de[- ]lampe|\bcorbeau|\babaque|\bastragale|\btailloir',
  'Chevet, choir, chapels':r'\babsid|\bch[œoe]ur|\bchapell|\bd[ée]ambul|\bchevet|\bsanctuaire',
  'Galleries, triforia':r'\btrifor|\bgaleri|\btribun|\bclaire[- ]voie|\bclerestor',
  'Windows, openings, tracery':r'\bfen[eê]tre|\bmeneau|\brose\b|\bverri[eè]re|\bvitrail|\bporte\b|\bportail|\btraceri|\bremplage',
  'Mouldings, profiles, ornament':r'\bprofil|\bmoulur|\bcorniche|\bcrochet|\bfleuron|\bsculpture|\bstatuaire|\bfrise|\bcong[ée]|\bboudin',
  'Masonry, works, roofs':r'\bcharpente|\bcouv[er]|\bsolive|\bplomberie|\btoiture|\btuile|\bar[dc]oise|\bdallage|\bappareil|\bbrique|\b[ée]chaf',
  'Plans, bays, proportional studies':r'\bplan\b|\btrav[ée]e|\bproportion|\bnef\b|\btranssep|\bcrois[ée]',
  'Stairs and circulation':r'\bescalier|\bpassage|\bporche|\bgaleri|\btribun|\bclo[iî]tre',
}
COMPILED={k:re.compile(v,re.I) for k,v in THEMES.items()}


def is_heading(t):
 t=t.strip()
 if len(t)<3 or len(t)>65: return False
 if t in ('—','NOTES A LA MAIN','FIN DE LA TABLE','NOTES À LA MAIN'):return False
 if t.startswith('[') or t.startswith('T. X'):return False
 # retain only uppercase monumental geographical names; OCR slightly corrupt
 # Geographic headings normally have lower-case departmental qualifiers,
 # so evaluate uppercase only in the place-name portion before parentheses.
 place=t.split('(')[0].strip()
 letters=[ch for ch in place if ch.isalpha()]
 if len(letters)<3:return False
 ratio=sum(1 for ch in letters if ch.isupper())/len(letters)
 if ratio<.82:return False
 if re.match(r'^(CATH[EÉ]DRALE|[ÉE]GLISE|ABBAYE|CH[AÂ]TEAU|MONUMENT|MAISON|VILLE|CHAPELLE|PORTE|REMPART|MOULIN|HOTEL|ÉDIFICE|ÉGLI|ARC|FENÊTRE|TRIFORIUM|ABB[EÉ]|FIGURES|SI[EÈ]CLES|TOMES|PAGES|BASE|PLAN|VO[UÛ]TE)\b',t):return False
 if any(ch.isdigit() for ch in t):return False
 return True

records=[]
for i,n in enumerate(range(15,442,2),1):
 pg=DOC[n-1]
 letter=next(k for k,(a,b) in RANGES.items() if a<=n<=b)
 # Place-name headings are extracted from the PDF text layer; these are candidates, not confirmed names.
 body=layout[n-1]
 headings=[]
 for raw in body.splitlines():
  t=re.sub(r'\s+',' ',raw.strip())
  if not t or len(t)>95: continue
  if not re.match(r'^[A-ZÀÂÉÈÊËÎÏÔÙÛÜÇÆŒ]',t):continue
  if not is_heading(t):continue
  if re.search(r'\s+(?:XI|XII|XIII|XIV|XV|XVI|I|II|III|IV|V|VI|VII|VIII|IX)\b',t):continue
  if re.match(r'^(?:FIGURES|PAGES|SIÈCLES|TOMES|T\. X|NOTES)',t):continue
  if '(' in t and ')' in t: headings.append(t)
  elif len(t)<44 and re.search(r'^\s{10,}',raw):headings.append(t)
 headings=list(dict.fromkeys(headings))
 body=layout[n-1]
 raw_lines=body.splitlines()
 hits={}
 for cat,patt in COMPILED.items():
  matches=[]
  for j,line in enumerate(raw_lines):
   if patt.search(line):
    loc=re.sub(r'\s+',' ',line.strip())
    if len(loc)>160:loc=loc[:160]
    if loc and not re.match(r'^\[\s*[A-Z]{3}',loc):matches.append({'line':j+1,'text':loc})
  hits[cat]=matches
 records.append(dict(pdf_page=n,note_page=n-1,leaf_number=i,letter=letter,site_headings_ocr=headings,source_text=body.rstrip(),topics=hits))

OUT=ROOT/'Viollet_le_Duc_Volume_X_Complete_Research_Packet'
OUT.mkdir(exist_ok=True)
(OUT/'index_leaves').mkdir(exist_ok=True)
for r in records:
 text=f"# Volume X — Leaf {r['leaf_number']:03d} / PDF page {r['pdf_page']} / Letter {r['letter']}\n\n**Status:** PDF text-layer transcription (UNVERIFIED OCR); the scan image is authoritative. Facing notes page: PDF {r['note_page']}.\n\n## OCR-detected place headings (verify where uncertain)\n" + '\n'.join('- '+h for h in r['site_headings_ocr']) + '\n\n## Full extracted original page (layout-preserving; possible OCR errors)\n\n```text\n'+r['source_text']+'\n```\n'
 (OUT/'index_leaves'/f"leaf_{r['leaf_number']:03d}_pdf_{r['pdf_page']:03d}.md").write_text(text)
# comprehensive source PDF text export single file
with (OUT/'Full_Volume_X_Extracted_Index_Text_UNVERIFIED_OCR.md').open('w') as f:
 f.write('# Volume X: Full extracted analytical index text\n\n**All 214 printed index leaves, in scan order.** OCR-derived text layer: every name, date, page number and figure must be checked against the scanned image before quotation or definitive citation. Blank facing notes pages are not repeated here.\n\n')
 for r in records:
  f.write(f"\n## Leaf {r['leaf_number']:03d} — PDF page {r['pdf_page']} — Letter {r['letter']}\n\n```text\n{r['source_text']}\n```\n")
# page inventory compact
with (OUT/'All_214_Leaf_Inventory.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['leaf_number','section','volume_x_pdf_page','facing_notes_pdf_page','ocr_detected_headings','total_thematic_line_matches','index_scan_status','numeric_and_name_reading_status'])
 for r in records:
  w.writerow([r['leaf_number'],r['letter'],r['pdf_page'],r['note_page'],'; '.join(r['site_headings_ocr']),sum(map(len,r['topics'].values())),'page text inventoried','OCR unverified'])
# thematic hit inventory with index pages per term
with (OUT/'Thematic_Hits_Searchable.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['theme','letter','volume_x_pdf_page','leaf','line_number_in_extracted_page','ocr_line','status'])
 for r in records:
  for cat,hits in r['topics'].items():
   for h in hits: w.writerow([cat,r['letter'],r['pdf_page'],r['leaf_number'],h['line'],h['text'],'candidate OCR index entry, verify scan'])

# compact JSON structured references
with (OUT/'Volume_X_Leaf_Data_OCR.json').open('w') as f:json.dump([{k:v for k,v in r.items() if k!='source_text'} for r in records],f,indent=2,ensure_ascii=False)
print('LEAVES',len(records),'total text chars',sum(len(r['source_text']) for r in records),'nonempty:',sum(bool(r['source_text'].strip()) for r in records))
print('Detected site headings',sum(len(r['site_headings_ocr']) for r in records),'coverage',sum(bool(r['site_headings_ocr']) for r in records),'page leaves')
for k in THEMES:
 pages=set(r['pdf_page'] for r in records if r['topics'][k]);print(k,len(pages),'leaves',sum(len(r['topics'][k]) for r in records),'lines')
for letter,(a,b) in RANGES.items():
 rr=[r for r in records if r['letter']==letter]
 names=[h for r in rr for h in r['site_headings_ocr']]
 print(letter,len(rr),'leaves',len(names),'headings','; '.join(names[:12]))
