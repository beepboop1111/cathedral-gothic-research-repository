from pathlib import Path
import json,base64,html,sys,platform,importlib.metadata
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'derived'
g=json.loads((D/'geometry.json').read_text());m=json.loads((D/'model_comparison.json').read_text());s=json.loads((D/'threshold_sensitivity.json').read_text());v=json.loads((D/'validation.json').read_text())
maxshift=max(x['center_shift_from_155_px'] for a in s.values() for x in a)
maxrshift=max(abs(x['radius_shift_from_155_px']) for a in s.values() for x in a)
table='| Arc | Center X | Center Y | Radius | Fit RMS | Samples retained | Block holdout RMS |\n|---|---:|---:|---:|---:|---:|---:|\n'
for n,r in g['arcs'].items():table+=f"| {n} | {r['center'][0]:.3f} | {r['center'][1]:.3f} | {r['radius']:.3f} | {r['inlier_rmse_px']:.3f} | {r['retained_count']}/{r['sample_count']} | {r['angular_block_holdout_raw_rmse_px']:.3f} |\n"
ctable='| Upper junction | X | Y | Acute tangent crossing |\n|---|---:|---:|---:|\n'
for n,r in g['upper_cusps'].items():ctable+=f"| {n} | {r['point'][0]:.3f} | {r['point'][1]:.3f} | {r['acute_tangent_crossing_angle_deg']:.3f}° |\n"
text=f'''# F5ZP Phase 3A — CXVIII / 1205b inner-arc research

Research checkpoint, 3 November 2026. **EXPERIMENTAL reconstruction of engraved ink; no architectural calibration or approval.**

The recovered drawing supports six circular arc pieces rather than one complete circle for each lobe. The top lobe and upper halves of the side lobes have radii approximately 43 pixels; the bottom lobe and lower side halves have radii approximately 36 pixels. Two upper cusp intersections are recoverable. The lower pairs are separated even when their supporting circles are completed. The SVG preserves those open ends.

![Matched source, overlay and analytic reconstruction](derived/comparison.png)

## Source and inherited authority

Ungewitter–Mohrmann, Volume II (1892), original PDF page 281, Plate CXVIII, figure 1205b. Original source book SHA-256: `{g['source']['source_pdf_sha256']}`. The supplied 144-DPI page/crop and all 24 handoff-manifest files remain byte-identical. The book itself was read without editing; it is not duplicated in this package.

The inherited outer circle is held fixed: center **(109.21742236738913, 111.23955699522183)**, radius **93.51694870364518 px**. Its prior conditional fit RMS remains **0.6915841262264908 px**, 339/360 inliers. This experiment does not refit or promote that reference.

A 432-DPI derivative was rendered directly from the matching PDF, not by enlarging the supplied PNG. Re-rendering at 144 DPI reproduced the supplied crop pixel for pixel. The PDF page contains a 2259 × 3271 detail image; rendering at 432 DPI is still resampling, not a claim of new scan resolution. No additional historical facts are inferred from extra render pixels.

## Coordinates and measurement

All table values use the original **144-DPI crop pixel coordinates**. Origin is the center of the crop's top-left pixel, X right, Y down. Positive angles run clockwise from +X. Page coordinates add (114,239). A high-resolution pixel index maps to reference coordinates as **(index − 1)/3**; this accounts for pixel-center alignment. The SVG has viewBox `0 0 225 226` and uses those same units. Its display size does not define physical units. Full-precision numeric parameters are in `derived/geometry.json`.

{table}
Radii and centers were fitted independently. No rotational symmetry, common radius, outer-circle tangency or closed topology was imposed. The values are engraving centerline measurements, not stone or opening boundaries.

## Intersections and cusp geometry

{ctable}
Each upper pair has a second supporting-circle intersection inside the figure. It is recorded in JSON but is outside the chosen engraved arc spans and is not used as a cusp. Acute tangent crossing is the smaller angle between the two tangent lines, not an assigned masonry cusp angle.

The completed south/west-lower circles have a **{g['adjacent_circle_relations']['S__W_lower']['external_gap_px']:.3f} px** minimum separation; the south/east-lower circles have a **{g['adjacent_circle_relations']['S__E_lower']['external_gap_px']:.3f} px** separation. There is no real intersection to use for either lower cusp. Extending or closing them would invent geometry. Lower free endpoints are read approximately from the stroke and projected onto their fitted circles; their location is uncertain by about 1 reference pixel.

The independently measured upper/lower side arcs leave endpoint discrepancies of **{g['side_junction_discrepancies']['W_side_endpoint_gap_px']:.3f} px west** and **{g['side_junction_discrepancies']['E_side_endpoint_gap_px']:.3f} px east**. They remain separate paths. Their apparent common side contact is consistent at ink scale, but an exact analytic join has not been established. Inner-circle internal-tangency errors relative to the inherited outer circle range from {min(r['outer_internal_tangency_error_px'] for r in g['arcs'].values()):.3f} to {max(r['outer_internal_tangency_error_px'] for r in g['arcs'].values()):.3f} px. Exact outer tangency is therefore not claimed.

All 21 supporting-circle pairs, including the outer reference, have relation/intersection records in JSON. Supporting-circle intersections are not automatically part of the visible geometry.

## Sampling, alternatives and numerical validation

The unchanged supplied grayscale and threshold scripts produced fixed-155, fixed-180 and adaptive alternatives. The supplied hatch script was run in no-fill mode as a diagnostic; it was excluded from fitting because closing can bridge construction marks or alter cusps. There is no masonry mask.

The new wrapper uses V08 plate inspection, ink extraction, `circle_fit` and `sample_arc`. A human-interpreted seed circle and angular window isolate each stroke. At 2° steps, a ±4 px radial search identifies contiguous dark runs; a darkness-weighted radial centroid supplies each sample. Runs wider than 2.5 px and rays within 6° of the guide axes are rejected. A robust preliminary circle rejects residuals over 1 px, then V08 fits the retained points. Of 378 sampled positions, {sum(r['retained_count'] for r in g['arcs'].values())} are retained. The CSV records every candidate sample, width, residual and retention flag. These are **conditional local fits**, not independent arc detection or statistical proof of a historical construction.

On the identical raw sample set, the four-circle model has **{m['four_circles']['raw_rmse_px']:.3f} px RMS** and the six-arc model has **{m['six_arcs']['raw_rmse_px']:.3f} px RMS**. These models have 12 and 18 free circle parameters respectively. The different side-arc radii improve the descriptive fit substantially; the comparison does not establish an author's intended construction.

Five angular-block holdouts are fitted on the other four blocks before residual rejection; the table reports prediction RMS on held-out samples. Holdouts test local arc extrapolation within the selected strokes. They are not a new engraving or independently annotated ground truth.

Thresholds 110,135,155,180 change centers by at most **{maxshift:.3f} px** and radii by at most **{maxrshift:.3f} px** relative to threshold 155. Six-block bootstrap percentile bounds (250 deterministic resamples) are supplied as sensitivity ranges, not metrological confidence intervals: scan distortion, seed selection, ink thickness and shared pixel errors remain unmodeled.

![Sample selection](derived/selected_samples.png)

The source/overlay views, segmentation sheet and per-arc residual plots were visually inspected. All 11 supplied V08 tests pass. SVG re-parsing verifies all six circular `A` commands and endpoint circle equations within 1e-7 px; upper intersection equation errors are below 3e-14 px. Those tiny errors validate analytic export consistency, not the accuracy of the drawing. The SVG is not a faceted polyline and contains no forced closing segment.

## Historical interpretation and limits

Primary-source observation: the upper strokes meet at visible pointed cusps, the lower strokes stop with gaps, and several fine guide curves coexist in the lower-left quadrant. The figure may be contrasting construction choices or radius regimes, rather than depicting a single completed symmetric opening. That is an experimental interpretation; accompanying explanatory text has not been checked. The fine guide curves, a/b/c lettering and diagonal lines are retained in the source, excluded from the lobe fit and not assigned verified construction-center identities.

The two upper cusp candidates and six local circular pieces are measurable research results. This is not a fully closed quatrefoil, a verified stone section, or an approved design. No STL is made. No cathedral geometry, locked dimensions or existing generator has been changed.

## Contents and reproduction

- `derived/1205b_measured.svg`: six editable circular paths, centers and unchanged outer reference.
- `derived/1205b_overlay.svg`: self-contained SVG with original crop embedded for comparison.
- `derived/geometry.json`: full-precision centers, radii, spans, endpoints, lengths, intersections and coordinate conventions.
- `derived/stroke_samples.csv`, `threshold_sensitivity.json`, `model_comparison.json`, `validation.json`: numeric evidence and provenance.
- `derived/comparison.png`, `selected_samples.png`, `radial_residuals.png`, `segmentation_alternatives.png`: visual evidence.
- `source_handoff/`: complete supplied handoff and unchanged tools.
- `CHECKPOINT.md`: bounded continuation instructions.
- `research_report.html`: self-contained offline visual report.

Run `python scripts/reconstruct.py` to regenerate measurements and visuals from the bundled derivative, then `python scripts/make_report.py` to rebuild this report. Optional source reproduction: `python scripts/render_source.py /path/to/lehrbuchdergotis02unge.pdf` before reconstruction. Dependencies and recorded versions are in `requirements-recorded.txt`. No network or cathedral generator is required for regeneration.

Next bounded research task: locate the explanatory text for 1205b and verify the a/b/c construction alternatives; then test explicitly labeled constrained construction variants alongside these measurements. Preserve this measured candidate and inherited outer reference. Do not silently fill the lower gaps or substitute an idealized symmetric design.
'''
# Count is derived, not a hard-coded claim.
total=sum(r['sample_count'] for r in g['arcs'].values());text=text.replace('Of 378 sampled positions',f'Of {total} sampled positions')
(ROOT/'REPORT.md').write_text(text)
(ROOT/'README.md').write_text('# F5ZP Phase 3A / 1205b research package\n\nOpen `research_report.html` for the self-contained illustrated report, or `REPORT.md` for text. Measurable vector files and numeric evidence are in `derived/`. Resume with `CHECKPOINT.md`.\n\nSix measured arc pieces; two upper cusp candidates; lower gaps preserved. Image-pixel units only. This is an experimental research candidate and does not alter cathedral geometry.\n')
versions=[]
for n in ['numpy','scipy','Pillow','matplotlib','scikit-image','trimesh','PyMuPDF']:
    versions.append(f'{n}=={importlib.metadata.version(n)}')
(ROOT/'requirements-recorded.txt').write_text('\n'.join(versions)+'\n')
# Minimal Markdown-to-HTML conversion with no remote resources.
lines=text.splitlines();parts=[];tablelines=[];inlist=False
def inline(t):
    import re
    t=html.escape(t);t=re.sub(r'`([^`]+)`',r'<code>\1</code>',t);t=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',t);return t
for line in lines+['']:
    if line.startswith('|'):tablelines.append(line);continue
    if tablelines:
        parts.append('<table>')
        for k,row in enumerate(tablelines):
            if k==1:continue
            tag='th' if k==0 else 'td';parts.append('<tr>'+''.join(f'<{tag}>{inline(c.strip())}</{tag}>' for c in row.strip('|').split('|'))+'</tr>')
        parts.append('</table>');tablelines=[]
    if not line.startswith('- ') and inlist:parts.append('</ul>');inlist=False
    if line.startswith('!['):
        alt,path=line[2:].split('](');p=ROOT/path[:-1];data=base64.b64encode(p.read_bytes()).decode();parts.append(f'<figure><img alt="{html.escape(alt)}" src="data:image/png;base64,{data}"><figcaption>{html.escape(alt)}</figcaption></figure>')
    elif line.startswith('# '):parts.append('<h1>'+inline(line[2:])+'</h1>')
    elif line.startswith('## '):parts.append('<h2>'+inline(line[3:])+'</h2>')
    elif line.startswith('- '):
        if not inlist:parts.append('<ul>');inlist=True
        parts.append('<li>'+inline(line[2:])+'</li>')
    elif line.strip():parts.append('<p>'+inline(line)+'</p>')
style='body{font:16px/1.55 system-ui,sans-serif;color:#18212b;background:#f4f1e9;margin:0}main{max-width:1120px;margin:auto;padding:42px;background:white}h1{font-size:30px}h2{margin-top:34px}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:14px}td,th{border-bottom:1px solid #ccd1d5;padding:8px;text-align:right}td:first-child,th:first-child{text-align:left}th{background:#edf2f5}img{max-width:100%;height:auto}figure{margin:22px 0}figcaption{font-size:13px;color:#56616a}code{font-size:13px;overflow-wrap:anywhere}p{max-width:100ch}'
(ROOT/'research_report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>F5ZP Phase 3A — 1205b research</title><style>'+style+'</style><main>'+''.join(parts)+'</main></html>')
print('Research report generated.')
