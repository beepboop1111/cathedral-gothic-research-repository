#!/usr/bin/env python3
"""Read-only source-cleanup, opening, cusp and moulding section comparisons.

Closed section loops are raster-derived geometry, not fitted historical arcs.
The preserved builder is traced without changing it to recover its actual
post-cleanup mask. No duplicated cleanup implementation is used for validation.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely import STRtree, linestrings, points
import trimesh


def load_builder(path):
    spec = importlib.util.spec_from_file_location('preserved_tracery_build', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def actual_cleanup_mask(builder_path, map_path):
    mod = load_builder(builder_path)
    lines = Path(builder_path).read_text().splitlines()
    stop = next(i + 1 for i, line in enumerate(lines) if line.strip() == 'T = a.thickness')
    captured = {}

    class Done(Exception):
        pass

    def trace(frame, event, arg):
        if event == 'line' and frame.f_code.co_filename == str(Path(builder_path)) and frame.f_lineno == stop:
            captured['stone'] = frame.f_locals['stone'].copy()
            raise Done()
        return trace

    argv = sys.argv
    try:
        sys.argv = [str(builder_path), str(map_path), '--res', '0.25']
        sys.settrace(trace)
        try:
            mod.main()
        except Done:
            pass
    finally:
        sys.settrace(None)
        sys.argv = argv
    if 'stone' not in captured:
        raise RuntimeError('Failed to capture actual preserved builder cleanup')
    return captured['stone']


def contours(mesh, origin, normal):
    section = mesh.section(plane_origin=origin, plane_normal=normal)
    return [] if section is None else section.discrete


def same_contours(a, b):
    av,bv=np.concatenate(a),np.concatenate(b)
    if av.shape!=bv.shape:return False
    return np.array_equal(av[np.lexsort(av.T[::-1])],bv[np.lexsort(bv.T[::-1])])


def discrete_hausdorff(a,b,axes):
    def directed(source,target):
        vertices=np.concatenate([p[:,axes] for p in source])
        segments=np.concatenate([np.stack([p[:-1,axes],p[1:,axes]],axis=1) for p in target])
        tree=STRtree(linestrings(segments))
        _,dist=tree.query_nearest(points(vertices),return_distance=True,all_matches=False)
        return float(dist.max(initial=0))
    return max(directed(a,b),directed(b,a))


def nearest_sample_deviation(a, b):
    # Deterministic contour-vertex comparison. Exact match is checked first.
    av, bv = np.concatenate(a), np.concatenate(b)
    d1 = cKDTree(av).query(bv)[0]
    d2 = cKDTree(bv).query(av)[0]
    return float(max(d1.max(initial=0), d2.max(initial=0)))


def audit(name, root):
    root = Path(root)
    map_path = root/'baseline/maps'/f'{name}_map.png'
    before = trimesh.load(root/'baseline/models'/f'{name}_R02_reproduced.stl', force='mesh')
    after = trimesh.load(root/'experimental/models'/f'{name}_M02_R03.stl', force='mesh')
    a = np.asarray(Image.open(map_path).convert('RGB'))
    h, w = a.shape[:2]
    px = 150 / w
    blue = (a[:,:,2] > 150) & (a[:,:,0] < 100) & (a[:,:,1] < 100)
    labels, count = ndi.label(blue)
    slices = ndi.find_objects(labels)
    cleaned = actual_cleanup_mask(root/'originals/kit/tracery_build.py', map_path)
    void_labels, _ = ndi.label(~cleaned)
    exterior = np.unique(np.concatenate([void_labels[0],void_labels[-1],void_labels[:,0],void_labels[:,-1]]))
    ny, nx = int(round(h*px/.25)), int(round(w*px/.25))
    mid_before = contours(before, [0,0,3], [0,0,1])
    mid_after = contours(after, [0,0,3], [0,0,1])
    rings_before = [Polygon(p[:,:2]) for p in mid_before]
    rings_after = [Polygon(p[:,:2]) for p in mid_after]
    records=[]
    for i, sl in enumerate(slices,1):
        mask = labels[sl] == i
        distances = ndi.distance_transform_edt(np.pad(mask,1))[1:-1,1:-1]
        yy,xx = np.unravel_index(np.argmax(distances),mask.shape)
        y,x = yy+sl[0].start, xx+sl[1].start
        xy = [x/(w-1)*(nx-1)*.25, ny*.25-y/(h-1)*(ny-1)*.25]
        p = Point(xy)
        nesting_before=sum(poly.covers(p) for poly in rings_before)
        nesting_after=sum(poly.covers(p) for poly in rings_after)
        label=int(void_labels[y,x])
        records.append({
            'legacy_opening_component':i, 'anchor_source_px':[int(x),int(y)],
            'anchor_model_xy_mm':xy, 'source_opening_area_mm2':float(mask.sum()*px*px),
            'source_blue_pixels':int(mask.sum()),
            'crop_contacts':{'top':sl[0].start==0,'bottom':sl[0].stop==h,'left':sl[1].start==0,'right':sl[1].stop==w},
            'original_mesh_anchor_is_void':bool(nesting_before%2==0),
            'repaired_mesh_anchor_is_void':bool(nesting_after%2==0),
            'source_pixels_remaining_void_after_original_cleanup_fraction':float(np.mean(~cleaned[sl][mask])),
            'original_cleanup_anchor_void':bool(not cleaned[y,x]),
            'original_cleanup_void_connected_to_exterior':bool(label in exterior),
            'original_cleanup_void_label':label,
            'original_midplane_loop_nesting':nesting_before,
            'repaired_midplane_loop_nesting':nesting_after,
            'original_mesh_anchor_in_opening':bool(nesting_before>0 and nesting_before%2==0),
            'repaired_mesh_anchor_in_opening':bool(nesting_after>0 and nesting_after%2==0),
        })
    sections=[]
    for z in [.25,.75,1.5,3.,4.5,5.5,5.8]:
        b=contours(before,[0,0,z],[0,0,1]); c=contours(after,[0,0,z],[0,0,1])
        bl=MultiLineString([p[:,:2] for p in b]); cl=MultiLineString([p[:,:2] for p in c])
        haus=0.0 if same_contours(b,c) else discrete_hausdorff(b,c,[0,1])
        sections.append({'axis':'Z','position_mm':z,'original_loops':len(b),'repaired_loops':len(c),
                         'hausdorff_mm':haus,'nearest_contour_vertex_max_mm':nearest_sample_deviation(b,c),
                         'original_length_mm':float(bl.length),'repaired_length_mm':float(cl.length)})
    # Longitudinal sections test chamfer and groove depth, including central and side cusps.
    for f in [.2,.35,.5,.65,.8]:
        x=float(before.bounds[0,0]+f*before.extents[0]); b=contours(before,[x,0,0],[1,0,0]);c=contours(after,[x,0,0],[1,0,0])
        if not b or not c:
            continue
        bl=MultiLineString([p[:,1:] for p in b]);cl=MultiLineString([p[:,1:] for p in c])
        sections.append({'axis':'X','position_mm':x,'original_loops':len(b),'repaired_loops':len(c),
                         'hausdorff_mm':0.0 if same_contours(b,c) else discrete_hausdorff(b,c,[1,2]),
                         'nearest_contour_vertex_max_mm':nearest_sample_deviation(b,c),
                         'original_length_mm':float(bl.length),'repaired_length_mm':float(cl.length)})
    opening_changes=[r for r in records if r['original_mesh_anchor_in_opening']!=r['repaired_mesh_anchor_in_opening']]
    mesh_holes=len(mid_after)-1
    cleanup_closed=np.setdiff1d(np.unique(void_labels),np.r_[0,exterior])
    source_anchor_holes=len(set(r['original_cleanup_void_label'] for r in records if not r['original_cleanup_void_connected_to_exterior'] and r['original_cleanup_anchor_void']))
    report={
        'name':name,'status':'EXPERIMENTAL geometry comparison, no historical/architectural approval',
        'source_classified_openings':count,
        'source_openings_with_original_enclosed_void_anchor':sum(r['original_mesh_anchor_in_opening'] for r in records),
        'source_openings_with_repaired_enclosed_void_anchor':sum(r['repaired_mesh_anchor_in_opening'] for r in records),
        'all_classified_opening_anchors_remain_void':all(r['original_mesh_anchor_is_void'] and r['repaired_mesh_anchor_is_void'] for r in records),
        'all_classified_opening_pixels_remain_void_after_original_cleanup':all(r['source_pixels_remaining_void_after_original_cleanup_fraction']==1.0 for r in records),
        'source_openings_connected_to_crop_exterior':sum(r['original_cleanup_void_connected_to_exterior'] for r in records),
        'distinct_source_anchor_void_components_after_original_cleanup':source_anchor_holes,
        'original_cleanup_closed_void_components':len(cleanup_closed),
        'midplane_before_loops':len(mid_before),'midplane_after_loops':len(mid_after),
        'midplane_through_holes':mesh_holes,
        'changed_opening_anchor_classifications':len(opening_changes),
        'source_region_map_changed_pixels':0,
        'opening_records':records,'sections':sections,
        'section_metric':'Symmetric discrete Hausdorff: all section vertices to nearest continuous section segment (STRtree); not a continuous global surface bound',
        'max_section_hausdorff_mm':max(s['hausdorff_mm'] for s in sections),
        'interpretation':'Source classification count and distinct mesh through-hole count are different. Classified openings connected to a crop boundary are open-edge cutouts, not enclosed topological holes; both are checked separately. No opening is silently filled or closed. Section comparisons include raster cusps and moulding transitions; exact historical arc/tangency validation is deferred to M04.',
    }
    out=root/'experimental/qa'/f'{name}_geometry_R03.json';out.write_text(json.dumps(report,indent=2))
    # Matched, full-outline overlay. No artistic redraw; numerical section coordinates.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,9));
    for j,p in enumerate(mid_before):ax.plot(p[:,0],p[:,1],color='black',lw=.65,label='Original section Z=3 mm' if j==0 else None)
    for j,p in enumerate(mid_after):ax.plot(p[:,0],p[:,1],color='#0794a4',lw=.5,ls='--',label='R03 section (matched)' if j==0 else None)
    for r in records:
        if r['original_cleanup_void_connected_to_exterior']:
            ax.plot(*r['anchor_model_xy_mm'],'rx',ms=4)
    ax.set_aspect('equal');ax.set_xlabel('Model X, mm');ax.set_ylabel('Model Y, mm');ax.legend(loc='upper right',fontsize=8)
    ax.set_title(f"{name} | exact mesh section overlay\n{count} classified openings; {mesh_holes} distinct through-holes; {len(opening_changes)} repair changes")
    fig.tight_layout();fig.savefig(root/'comparisons'/f'{name}_section_overlay_R03.png',dpi=150);plt.close(fig)
    print(json.dumps({k:v for k,v in report.items() if k not in ('opening_records','sections')},indent=2),flush=True)
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('name');ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();audit(a.name,a.root)
