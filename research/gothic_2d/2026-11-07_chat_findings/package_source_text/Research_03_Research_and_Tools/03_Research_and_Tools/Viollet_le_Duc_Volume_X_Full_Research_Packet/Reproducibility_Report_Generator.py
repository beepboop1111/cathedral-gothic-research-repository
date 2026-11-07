from pathlib import Path
import csv,json,collections,zipfile,re
ROOT=Path('/mnt/data')
OUT=ROOT/'Viollet_le_Duc_Volume_X_Complete_Research_Packet'
leaf_rows=list(csv.DictReader((OUT/'All_214_Leaf_Inventory.csv').open()))
THEMES={
'Vaults and vault supports': ['Voûte','Voûtes','Arc-doubleau','Arc formeret','Arc ogive','Clef de voûte','Travée'],
'Chevets, choirs, chapels':['Abside','Chapelles absidales','Chœur','Plan','Sanctuaire'],
'Piers, columns, profiles':['Pilier','Piliers','Colonne','Chapiteau','Profil','Profils'],
'Exterior stability':['Arc-boutant','Contre-fort','Construction','Fondations','Chaînage'],
'Elevation, lighting, galleries':['Triforium','Galerie','Tribune','Fenêtre','Meneau','Vitrail']}
# Carefully checked against original image on pages 53, 373, 423, 425, 435 and extracted image-layer witnesses on the other pages.
CURATED=[
# subject, site, pdf, vol, printed pg, fig, project area, level
('Amiens Cathedral','Arc-boutant',23,'I','64, 72, 78, 82','62, 72','flying buttress','print/OCR comparison needed'),
('Amiens Cathedral','Chapelles absidales',23,'I; II','I 201; II 474','II 38–40','chevet / chapel','print/OCR comparison needed'),
('Amiens Cathedral','Piliers',25,'IV; VII','IV 167; VII 169','IV 94–98','supports and springings','print/OCR comparison needed'),
('Amiens Cathedral','Profils',25,'VII','510','18, 27','mouldings','print/OCR comparison needed'),
('Amiens Cathedral','Triforium',25,'I; II','I 201, 203; II 325, 330','I 35','gallery and elevation','print/OCR comparison needed'),
('Amiens Cathedral','Triforium',27,'IX','290','11, 12','gallery and elevation','print/OCR comparison needed'),
('Amiens Cathedral','Voûtes',27,'IV; VI; IX','IV 167; VI 437; IX 517','IV 94–98; IX 30','vaults and rib/pier links','print/OCR comparison needed'),
('Beauvais Cathedral','Arc-doubleau / arc formeret',53,'I','58; 57','—','transverse and formeret arches','image-checked'),
('Beauvais Cathedral','Arc-boutant',53,'I','69, 71, 74','61','flying buttresses','image-checked'),
('Beauvais Cathedral','Chapelles absidales',53,'II','477','—','chevet / chapel','image-checked'),
('Beauvais Cathedral','Piliers',53,'IV','177','101, 101 bis, 101 ter','supports and springings','image-checked'),
('Beauvais Cathedral','Triforium',53,'I','201','—','gallery and elevation','image-checked'),
('Chartres Cathedral','Arc-boutant',99,'I; II','I 65; II 315','I 54','flying buttresses','print/OCR comparison needed'),
('Chartres Cathedral','Chapelles absidales',101,'I; II','I 201, 207; II 466','—','chevet / chapel','print/OCR comparison needed'),
('Chartres Cathedral','Contre-fort',101,'IV','299','—','buttressing','print/OCR comparison needed'),
('Chartres Cathedral','Profils',101,'VII','489','6 A','mouldings','print/OCR comparison needed'),
('Langres Cathedral','Voûte',183,'IV','70','37–39','vault comparisons','OCR leads only'),
('Laon Cathedral','Clef de voûte',185,'III','260','4, 5','bosses / vault intersections','OCR leads only'),
('Laon Cathedral','Pilier',185,'VII','162','11, 12','responds / supports','OCR leads only'),
('Laon Cathedral','Voûte',185,'I','191','—','vault comparisons','OCR leads only'),
('Noyon Cathedral','Arc ogive',251,'III','263','—','rib definition','OCR leads only'),
('Noyon Cathedral','Chapelles absidales',251,'II','457, 461','28','chevet / chapel','OCR leads only'),
('Noyon Cathedral','Construction',251,'II','298','—','construction chronology','OCR leads only'),
('Noyon Cathedral','Profil',253,'VII','497','11','mouldings','OCR leads only'),
('Noyon Cathedral','Voûte',253,'I; II; IV; IX','I 191, 195; II 304; IV 49; IX 248','I 30','vault comparisons','OCR leads only'),
('Paris, Notre-Dame','Arc-boutant',263,'I','68, 69, 82','59, 69, 71','flying buttresses','image-checked'),
('Paris, Notre-Dame','Arc-doubleau',263,'I','55','40','transverse arches','image-checked'),
('Paris, Notre-Dame','Construction',265,'IV','158','91, 91 bis','structural construction','OCR leads only'),
('Paris, Notre-Dame','Profils',267,'VII','506','16','mouldings','image-checked'),
('Paris, Notre-Dame','Voûte',267,'I; VI; IX','I 188, 192, 195; VI 432; IX 512','I 27–29; VI 6, 8; IX 26, 27','vault comparisons','image-checked'),
('Reims Cathedral','Chapelles absidales',303,'I; II','I 111, 201; II 469','II 36, 37','chevet / chapel','OCR leads only'),
('Reims Cathedral','Chapelles du chœur',303,'II','321','—','choir perimeter','OCR leads only'),
('Saint-Denis abbey church','Chapelles',329,'II','457, 461','—','chevet / chapel','image-checked'),
('Saint-Denis abbey church','Arc-boutant',329,'I','59, 66, 74, 82','55, 73','flying buttresses','image-checked'),
('Saint-Denis abbey church','Profils',331,'VII','504','15, 19','mouldings','image-checked'),
('Saint-Denis abbey church','Triforium',331,'I; IX','I 205; IX 292','I 36; IX 13, 14','gallery and elevation','image-checked'),
('Saint-Denis abbey church','Voûte',331,'VI; IX','VI 446; IX 501','IX 22','vaults','image-checked'),
('Senlis Cathedral','Arc ogive',373,'III','263','9','rib geometry','image-checked'),
('Senlis Cathedral','Chapelles absidales',373,'II','457, 465','29–31','chevet / chapel','image-checked'),
('Senlis Cathedral','Voûte',373,'IX','515','29','vaults','image-checked'),
('Sens Cathedral','Triforium',375,'I; IX','I 201; IX 286','IX 9','gallery and elevation','image-checked'),
('Sens Cathedral','Voûte',375,'IV; IX','IV 49; IX 506','IX 23–25','vaults','image-checked'),
('Soissons Cathedral','Arc-boutant',379,'I','63','52','flying buttress','OCR leads only'),
('Soissons Cathedral','Voûte',381,'I','191, 196, 198','—','vaults','OCR leads only'),
('Troyes, Saint-Urbain','Arc-boutant',403,'I','76, 80','66, 70','buttress framing','image-checked'),
('Troyes, Saint-Urbain','Construction',403,'IV','183, 190','102–106','construction / spans','image-checked'),
('Troyes, Saint-Urbain','Profil',405,'VII','519','22','mouldings','OCR leads only'),
('Vézelay abbey church','Arc-doubleau',421,'I','55','38','transverse arches','OCR leads only'),
('Vézelay abbey church','Chapelles absidales',423,'II','457, 465','—','chevet / chapel','image-checked'),
('Vézelay abbey church','Clef de voûte',423,'III','257, 262','2, 7','bosses','image-checked'),
('Vézelay abbey church','Profil',423,'VII','495, 505','9 C, D; 17','mouldings','image-checked'),
('Vézelay abbey church','Voûte',423,'I','182, 185, 190','21, 22','vaults','image-checked'),
('Vézelay abbey church','Voûte (continuation)',425,'IV; VI; IX','IV 31, 103; VI 427; IX 486, 510','VI 3, 5','vaults','image-checked'),
('Westminster Abbey','Voûte',435,'IX','523','34','English comparative vault','image-checked'),
('Windsor, St George’s Chapel','Voûte',435,'IX','537','40','English comparative vault','image-checked'),
]
with (OUT/'Curated_Cathedral_Reference_Leads.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['monument','index_heading','vol_x_pdf_page','target_tome','target_printed_pages','target_figures','study_track','index_transcription_status','target_source_status'])
 for row in CURATED:w.writerow([*row,'NOT UPLOADED / NOT EXAMINED'])

RANGES={'A':(15,43),'B':(45,75),'C':(77,129),'D':(131,137),'E':(139,145),'F':(147,155),'G':(157,163),'H':(165,167),'I':(169,171),'J':(173,175),'K':(177,177),'L':(179,201),'M':(203,239),'N':(241,253),'O':(255,259),'P':(261,297),'Q':(299,299),'R':(301,319),'S':(321,387),'T':(389,407),'U':(409,409),'V':(411,433),'W':(435,437),'X':(439,439),'Y':(441,441)}
# Curated sample to anchor alphabetical reading, not the only named sites in each section
EXAMPLES={'A':'Abbeville; Amiens; Angers','B':'Beauvais; Beaune; Bourges','C':'Carcassonne; Chartres; Châlons; Clairvaux','D':'Die; Dijon; Durham','E':'Elne; Ely; Évreux','F':'Falaise; Fréjus; Francfort','G':'Gaillon; Gérone; Gorze','H':'Harcourt; Honfleur','I':'Ibos; Île Barbe; Issoire','J':'Jérusalem; Josselin; Jumièges','K':'Kingston-sur-Hall; Rœnigsheim (as printed/OCR check)','L':'Langres; Laon; La Réole','M':'Mende; Metz; Meaux; Mont-Saint-Michel','N':'Nevers; Noyon','O':'Orcival; Orléans; Ourscamps','P':'Paris; Pontigny; Poitiers','Q':'Querqueville; Quilleboeuf; Quimper; Quimperlé','R':'Reims; Rouen','S':'Saint-Denis; Senlis; Sens; Soissons; Strasbourg','T':'Toulouse; Tournus; Troyes','U':'Unac; Ussé; Ussel; Uzerche; Uzeste','V':'Vézelay; Vienne; Vignory; Vincennes','W':'Walbourg; Westminster; Winchester; Windsor; Worms','X':'Xaintrailles','Y':'Yainville; Ydes; Yèvre-le-Châtel'}
# Don't present unverified examples as fact for all sections. Only anchored samples via scan/text layer.
# Exception some EXAMPLES may be OCR-inferred; not an exhaustive site listing.
lines=[]
def put(t=''):lines.append(t)
put('# Viollet-le-Duc, Tome X — Complete-Volume Analytical Research Report')
put('**Research date:** October 2026  •  **Source:** the user-uploaded 448-page scan of *Dictionnaire raisonné de l’architecture française du XIe au XVIe siècle*, Tome dixième, Paris: A. Morel, 1868.  •  **Geometry:** no modification to F5ZE, V13 v0.10, or A4–A6.')
put()
put('> **Status language.** “Whole-volume coverage” means every printed index leaf has been ingested and filed in scan order. It does **not** mean that the ~500,000-character OCR transcription has been independently proofread character-by-character. Selected key pages and citations have been checked against rendered images. Every target-volume reference is a finding aid until the user supplies the corresponding Volume I–IX.')
put()
put('## Executive conclusions')
put('1. **Tome X is a monument-first analytical index** to the preceding nine volumes, not a tenth volume of treatise articles. Its value is to reunite references to a building that may be dispersed across many architectural articles.')
put('2. **The physical design embodies research annotation.** Printed index leaves on PDF pages 15–441 odd (214 leaves) face intentionally blank *Notes à la main* leaves on PDF pages 14–440 even. The *Avis* (PDF 9–11) explains that users should append commentary and cross-references.')
put('3. **Reference fields are decade/century, tome, printed page, and figure.** The page/figure fields refer to the other volumes, not to Tome X. The index supplies **no substitute for reading those passages and looking at those illustrations**.')
put('4. **The chevet/vault problem is distributed across volumes.** Example index clusters link ambulatory-adjacent subjects such as *chapelles absidales* to Tome II, *piliers* and *construction* to Tome IV, *profils* to Tome VII, *triforium* to Tomes I and IX, and *voûte* to IX (as well as other volumes).')
put('5. **Careful monument identification is essential.** In PDF p. 373, *Senlis* vault → IX p. 515, fig. 29, while on PDF p. 375, *Sens* vault → IX p. 506, figs. 23–25. They are separate buildings; abbreviating both to “Sen…” would corrupt the catalogue.')
put('6. **Comparative geography is broader than France.** It includes sites such as Westminster, Windsor, Worms, Jerusalem, and others. The W index leaf (PDF p. 435) points to Westminster *voûte* IX p. 523, fig. 34 and Windsor *voûte* IX p. 537, fig. 40. Those may be valuable comparisons, but English examples must not silently be treated as French precedents.')
put('7. **The source does not prove a vault-generation algorithm.** There is presently no source basis for changing radial web bulge, spring lines, doubleau paths, or moulded profile sizes in V13.')
put()
put('## Part I — The book, pagination, and how to cite it')
put('The PDF has **448 scanned pages**, title page at PDF 7, the author’s *Avis* at PDF 9–11, analytical-title page at PDF 13, printed index at odd PDF pages 15–441, and facing notes at even PDF pages 14–440. The index closes at **Y** and reads *Fin de la table* at PDF 441; it has **no Z section**. Closing scanned matter follows.')
put('Use references in the form **“Tome X, uploaded PDF p. 373; Senlis — Voûte → Tome IX, printed p. 515, fig. 29.”** Do not mistake printer’s signatures or a scanned-page number for the printed page in the other volume.')
put('The title-page engraving is illustrative. Sampled index leaves are typographic cross-references; the technical architectural figures listed there reside in the indexed Volumes I–IX rather than being reproduced in Volume X.')
put()
put('### The *Avis*, page-by-page interpretive reading')
put('- **PDF 9:** The dictionary format makes entries easy to look up, but one monumental case study can be divided among twenty to thirty separate articles. Our treatment: create a monument dossier in addition to a subject dossier.')
put('- **PDF 10:** The index tracks building components, historical dates, and related figures, but cannot fulfill every research purpose. Facing blank leaves enable custom notes and cross-references. Our treatment: distinguish source data, interpretation, and modern computational hypotheses.')
put('- **PDF 11:** The introduction concludes with a rhetorical comparison between consultable books and absorbing conversation. This is an expression of the author’s hopes for the *Dictionnaire*, not an architectural proposition.')
put('The complete French transcription and English translation are in the already prepared **Session 02: Avis and First Index Leaf** document; this research packet does not replace or revise that transcription.')
put()
put('## Part II — Every alphabetical section, without skipped index leaves')
put('The table covers *every* printed index page, regardless of whether a famous cathedral appears. “Named examples” are orientation cues, **not an exhaustive site list**; use the 214-leaf companion for all page content.')
put()
put('| Letter | PDF scan pages, odd only | Leaves | Orienting entries present / to consult |')
put('|:--:|:--|--:|:--|')
for let,(first,last) in RANGES.items():
 rr=[r for r in leaf_rows if r['section']==let]
 put(f"| {let} | {first}–{last} | {len(rr)} | {EXAMPLES[let]} |")
put(f"| **Total** | **15–441 (odd)** | **{len(leaf_rows)}** | |")
put()
put('### What the page sequence shows')
put('- A, B, C, L, M, P, S, T, and V contain many densely referenced building dossiers. **S (34 index leaves)** is the longest section and deserves careful monument disambiguation.')
put('- Short letters K, Q, U, X, and Y are still valuable and are covered in the same leaf register. K includes Kingston-sur-Hall and a second château entry; Q includes four identified place entries, not only two.')
put('- The entries are often **nested** as locality → monument → architectural element → century/volume/page/figure. A continued cathedral entry can occupy several pages and can be interrupted by the next monument; never assume page boundaries coincide with monument boundaries.')
put()
put('## Part III — Source-derived thematic architecture map')
put('This is a **map of where evidence may be found**, not a claim that the listed medieval construction principles have already been established. Short French titles remain in the original architectural vocabulary.')
put()
put('### A. Vaults, arch families, and bosses — highest priority')
put('**French index vocabulary:** *voûte; voûtes; arc-doubleau; arc formeret; arc ogive; clef de voûte; travée*.')
put('The most direct vault comparisons indexed in Tome IX include **Saint-Denis IX p. 501 fig. 22, Sens IX p. 506 figs. 23–25, Senlis IX p. 515 fig. 29, Amiens IX p. 517 fig. 30**. Additional leads include **Paris IX p. 512 figs. 26–27**, **Vézelay IX pp. 486, 510** and English comparative examples **Westminster IX p. 523 fig. 34**, **Windsor IX p. 537 fig. 40**. Earlier discussions for the same monuments are indexed in Tomes I, III, IV, and VI.')
put('**Architectural questions to test when source volumes arrive:** Is web curvature described explicitly? Is the profile of a *doubleau* structural, ornamental, or both? How are arches carried to supports? Are irregular/tapering chevet bays actually illustrated? Does a figure show geometry or merely a completed appearance?')
put()
put('### B. Chevets, ambulatories, and radiating chapels')
put('**Vocabulary:** *abside; chapelles absidales; chœur; chevet; sanctuaire*. Volume X frequently uses **chapelles absidales** rather than the exact project term “ambulatory vault.” It identifies many Tome II page leads in the **457–477** region, including Noyon II pp. 457, 461; Saint-Denis II pp. 457, 461; Senlis II pp. 457, 465; Chartres II p. 466; Amiens II p. 474; Beauvais II p. 477. The index does not establish the geometry of the intermediate vaulted passage.')
put('**F5ZE consequence:** these are strong candidates for analyzing plan relationships among radiating chapels, shared piers, aisle bands, and perimeter supports. Wait for original plans and descriptions before converting any proportions to the generator.')
put()
put('### C. Structural reasoning, construction, piers, responds')
put('**Vocabulary:** *construction; pilier; piliers; pile; colonne; chapiteau; chaînage; contre-fort; arc-boutant; clef de voûte*. An index cluster includes Paris **IV p. 158 figs. 91, 91 bis**, Amiens **IV p. 167 figs. 94–98**, Beauvais **IV p. 177 figs. 101/101 bis/101 ter**, and Saint-Urbain (Troyes) **IV pp. 183, 190 figs. 102–106**. These may form a particularly useful figure-comparison run about structural arrangements. The content and argument of each figure are **not yet verified**.')
put('**F5ZE consequence:** potential material for fixing how ribs and transverse arches terminate into responds without unnatural radial flaring, but no source-backed change is claimed.')
put()
put('### D. Flying buttresses, roof support, and outer elevation')
put('**Vocabulary:** *arc-boutant; contre-fort; chaînage; bahut; pinacle; corniche*. Leads include Beauvais I pp. 69, 71, 74 fig. 61; Chartres I p. 65 fig. 54; Paris I pp. 68, 69, 82 figs. 59, 69, 71; Saint-Denis I pp. 59, 66, 74, 82 figs. 55, 73; Saint-Urbain I pp. 76, 80 figs. 66, 70.')
put('**F5ZE consequence:** important for the exterior profile and narrow clerestory/gallery arrangement, but the indexed lines themselves do not state thrust calculations or allowable spans.')
put()
put('### E. Triforia, galleries, circulation and upper levels')
put('**Vocabulary:** *triforium; galerie; tribune; porche; escalier*. Tome IX references include **Noyon p. 280**, **Soissons p. 280**, **Sens p. 286 fig. 9**, **Amiens p. 290 figs. 11–12**, and **Saint-Denis p. 292 figs. 13–14**, plus Tome I examples around pp. 201–205. They form a research trail, not proof of a single historical gallery system.')
put('**F5ZE consequence:** revisit upper-gallery and choir-overlook concepts only after studying elevation diagrams and physical passage conditions.')
put()
put('### F. Moulding profiles and profile provenance')
put('**Vocabulary:** *profil; profils; moulure; boudin; congé; astragale; abaque*. Named monument profile leads include Chartres **VII p. 489 fig. 6 A**, Noyon **VII p. 497 fig. 11**, Vézelay **VII pp. 495, 505 figs. 9 C/D and 17**, Saint-Denis **VII p. 504 figs. 15, 19**, Paris **VII p. 506 fig. 16**, Amiens **VII p. 510 figs. 18, 27**, and Saint-Urbain **VII p. 519 fig. 22**.')
put('**F5ZE consequence:** these pointers may eventually help identify the monuments and functions behind the user’s own hand-traced profiles. Original tracings remain unaltered; no profile is automatically assigned to a doubleau merely because it looks appropriate.')
put()
put('### G. Windows, tracery, openings and ornament')
put('**Vocabulary:** *fenêtre; meneau; archivolte; rose; verrière; vitrail; fleurons; crochets; statuaire*. These appear at many sites and can be organized into opening geometry, wall/arch interfaces, and decorative sculpture. The index links them to a wide range of Tomes; exact architectural conclusions require inspecting target images.')
put()
put('### H. Construction material, masonry and chronology')
put('**Vocabulary:** *appareil; charpente; chaînage; maçonnerie; brique; fondations; dallage; couverture*. The index frequently attributes distinct centuries to particular parts of a building; catalogue dates **per indexed component**, not as a construction date for the entire church.')
put()
put('## Part IV — Curated monument research register')
put('The following table is an editorial **selection of high-value pointers** (not all of the book’s entries). The complete corresponding machine-readable register contains **'+str(len(CURATED))+' rows**. Each pointer is explicitly marked **target source NOT EXAMINED**.')
put()
put('| Monument | X scan p. | Indexed subject | Destination in Tomes I–IX | Application / question |')
put('|:--|--:|:--|:--|:--|')
for x in CURATED:
 mon,sub,pdf,vol,pages,fig,track,status=x
 put(f'| {mon} | {pdf} | *{sub}* | {vol}, p. {pages}'+(f', fig. {fig}' if fig!='—' else '')+f' | {track} |')
put()
put('## Part V — What the complete-document extraction does and does not prove')
put('The reference packet contains **214 separate leaf text files** and one 540 KB combined text-layer extraction. That makes all pages searchable and provides a stable page inventory. The automated classifier also found lines containing relevant architectural terms across many leaves. This is an **OCR keyword index**, not a replacement for photographic collation: column position is crucial, figures often look like letters, and a term may be hyphenated across lines.')
put('The downloadable **Thematic_Hits_Searchable.csv** identifies candidate lines with their X page number so that we can jump directly to the uploaded scan. Counts of keyword matches should not be interpreted as numbers of monuments or numbers of separate architectural facts.')
put('**Examples of witnessed reading hazards:** `Zi57` is likely printed `457`; `9^,95,90,97,98` can represent `94–98`; `VII` may become `VIL` in OCR; **Senlis** and **Sens** are adjacent but distinct. Consequently, sensitive citations are checked against the page image, and uncertain rows are not silently “fixed” by general knowledge.')
put()
put('## Part VI — Questions to carry into the next nine volumes')
for q in [
'**Curved ambulatory web:** What evidence does *Voûte* provide for ribs and webs over nonrectangular or wedge-shaped plans? Are there explicit plan, section, and perspective figures of a single bay?',
'**Rib alignment and springing:** Where do *ogives*, *doubleaux*, and *formerets* share a spring, and how do their different curvatures meet at the pier?',
'**Upper-gallery support:** What is actually shown for *triforium*, *galerie*, and *tribune* in relation to the chevet’s inner and outer structural lines?',
'**Buttress/chapel relation:** Which photographed/indexed monuments show flying buttresses landing at chapels or passing above circulation?',
'**Profiles:** Can the user’s existing traced curves be located to an exact *profil* figure and a specifically identified structural member?',
'**Construction vs reconstruction:** Which geometric procedures are described by Viollet-le-Duc himself, and which would be new mathematical conjectures in our V13 generator?',
]:put('- '+q)
put()
put('## Part VII — Research sequence, preserving source authority')
put('1. **Begin with Volume IX, *Voûte*,** reading the original French and checking figs. 22–30 and relevant later English comparisons against their printed pages. Use the four-monument list as a start, not a substitute for full entry reading.')
put('2. **Study Volume IV construction/support arguments**, including the indexed Paris IV 158, Amiens IV 167, Beauvais IV 177, and Saint-Urbain IV 183/190 group, and every adjoining figure or passage needed for context.')
put('3. **Consult Volume II *chapelles absidales* and related church plans**, using the printed p. 457–477 cluster to reconstruct how actual chapel perimeters and connecting aisle bands were organized.')
put('4. **Investigate Volume VII *profils***, cross-checking actual figure shapes against the user’s hand-traced moulding files; never overwrite, rename, or transform the originals without explicit authorization.')
put('5. **Complete volume-by-volume article coverage** of linked terms in Tomes I, III, V, VI, VIII and the remainder of II/IV/VII/IX as each user-uploaded file arrives.')
put('6. **Synthesize only afterward** into hypothetical algorithms and compare with the unchanged F5ZE/V13 model. Label source-derived geometry, inferred reconstruction, and modern design decisions separately.')
put()
put('## Provenance and limitations')
put('- **Only the user-uploaded Volume X was used.** No other editions were downloaded or consulted.')
put('- **Original French:** *Avis* fully transcribed in Session 02. For the 214 index leaves, a full OCR-layer transcription is retained, with verified representative pages and selected citation rows. It is not claimed to be a diplomatic transcription of every index entry.')
put('- **Illustrations:** The named figures are located in source Volumes I–IX; none has yet been examined. The uploaded Tome X index does not establish construction geometry.')
put('- **Exhaustive reading status:** all 214 leaves are included in an ordered inventory and searchable appendix; selected high-value entries are manually visually checked. Comprehensive line-by-line verification of every reference remains an editorial proofing task, especially for ambiguous digits and names.')
put('- **No design intervention:** geometry, source code, files, scale, F5ZE topology, V13 v0.10, and experimental bays A4–A6 unchanged.')
put()
put('## Packet contents')
for item in [
'`All_214_Leaf_Inventory.csv` — page-by-page X location, facing-note folio, OCR-detected headings (may miss/garble names), verification labels.',
'`Thematic_Hits_Searchable.csv` — OCR candidates for architectural terms on every index leaf, with exact Volume X PDF locator.',
'`Curated_Cathedral_Reference_Leads.csv` — monument → component → tome/printed page/figure cross-reference leads.',
'`Full_Volume_X_Extracted_Index_Text_UNVERIFIED_OCR.md` — complete, ordered OCR layer of all 214 leaves (not proofread).',
'`index_leaves/` — 214 leaf-sized companion files in original sequence.',
'`visual_audit_sheets/` and `preview_*.png` — selected page-image audits; renderings are not alternate editions.',
'`Volume_X_Leaf_Data_OCR.json` — structured preliminary search index, not authoritative for the printed digits.',
]:put('- '+item)
put()
put('**Closing research judgment:** Volume X has successfully established a navigational architecture for the larger ten-volume investigation. The chief value of the completed pass is a traceable set of primary-source questions and page/figure targets, **not a premature solution** to the cathedral’s parametric geometry.')
report='\n'.join(lines)+'\n'
(OUT/'Volume_X_Comprehensive_Research_Findings.md').write_text(report)
( ROOT/'Viollet_le_Duc_Volume_X_Comprehensive_Research_Findings.md').write_text(report)
print('Report words:',len(report.split()),'Curated refs:',len(CURATED),'Raw leaves',len(leaf_rows))
