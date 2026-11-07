#!/usr/bin/env python3
"""Experimental sub-voxel precision repair; never fills holes or smooths surfaces.

Reads an STL produced by the preserved tracery_build.py. Coordinates are model
millimeters. The tolerance is a precision budget, not an architectural parameter.
All proposed vertex clusters and deleted triangles are recorded for audit.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

VERSION = "R03-experimental"
AREA_EPS = 1e-10


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def vertex_links(mesh):
    """Count disconnected vertex fans on an otherwise closed oriented mesh.

    Opposite halfedges are paired, then next(twin(h)) walks the link of the
    start vertex. A manifold vertex has exactly one cycle. This detects bowties
    which an edge incidence test alone misses.
    """
    f = mesh.faces
    start = f.reshape(-1)
    end = f[:, [1, 2, 0]].reshape(-1)
    lo, hi = np.minimum(start, end), np.maximum(start, end)
    order = np.lexsort((hi, lo))
    if len(order) % 2:
        return None
    paired = order.reshape(-1, 2)
    if not np.all(lo[paired[:, 0]] == lo[paired[:, 1]]) or not np.all(hi[paired[:, 0]] == hi[paired[:, 1]]):
        return None
    twin = np.empty(len(start), np.int64)
    twin[paired[:, 0]] = paired[:, 1]
    twin[paired[:, 1]] = paired[:, 0]
    nxt = 3 * (twin // 3) + (twin + 1) % 3
    if not np.array_equal(start[nxt], start):
        return None
    seen = np.zeros(len(start), bool)
    cycles = np.zeros(len(mesh.vertices), np.int16)
    for first in range(len(start)):
        if seen[first]:
            continue
        cycles[start[first]] += 1
        at = first
        while not seen[at]:
            seen[at] = True
            at = nxt[at]
    return int(np.sum(cycles != 1))


def mesh_qa(mesh, *, check_links=True):
    inc = np.bincount(mesh.edges_unique_inverse)
    faces = mesh.faces
    repeats = np.any(np.diff(np.sort(faces, axis=1), axis=1) == 0, axis=1)
    uniq = np.unique(np.sort(faces, axis=1), axis=0)
    boundary = int((inc == 1).sum())
    nonmanifold = int((inc > 2).sum())
    closed = boundary == 0 and nonmanifold == 0
    adj = mesh.face_adjacency
    graph = coo_matrix((np.ones(len(adj)), (adj[:, 0], adj[:, 1])), shape=(len(faces), len(faces)))
    pieces, labels = connected_components(graph, directed=False)
    component_areas = np.bincount(labels, weights=mesh.area_faces)
    return {
        "vertices": len(mesh.vertices), "triangles": len(faces),
        "bounds_mm": mesh.bounds.tolist(), "extents_mm": mesh.extents.tolist(),
        "finite": bool(np.isfinite(mesh.vertices).all()),
        "boundary_edges": boundary, "nonmanifold_edges": nonmanifold,
        "degenerate_faces_area_under_1e-10_mm2": int((mesh.area_faces < AREA_EPS).sum()),
        "repeated_vertex_faces": int(repeats.sum()),
        "duplicate_faces": len(faces) - len(uniq),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_valid": bool(mesh.is_volume), "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area), "euler_number": int(mesh.euler_number),
        "surface_components": int(pieces), "component_surface_areas_mm2": component_areas.tolist(),
        "nonmanifold_vertices": vertex_links(mesh) if closed and check_links else None,
        "self_intersections": "evaluated separately by scripts/check_intersections_R03.py; see qa/self_intersections_R03.json",
    }


def collapse_precision_clusters(mesh, tolerance):
    if not 0 < tolerance <= 5e-5:
        raise ValueError("Experimental precision budget must be in (0, 0.00005] mm")
    verts, faces = np.asarray(mesh.vertices), np.asarray(mesh.faces)
    pairs = cKDTree(verts).query_pairs(tolerance, output_type="ndarray")
    parent = np.arange(len(verts))

    def root(i):
        while parent[i] != i:
            i = parent[i]
        return i

    for a, b in pairs:
        a, b = root(a), root(b)
        if a != b:
            parent[max(a, b)] = min(a, b)
    for i in np.unique(pairs):
        parent[i] = root(i)
    move = np.linalg.norm(verts - verts[parent], axis=1)
    if move.max(initial=0) > tolerance * 2:
        raise ValueError("Transitive cluster exceeds displacement budget")
    remapped = parent[faces]
    collapsed = np.any(np.diff(np.sort(remapped, axis=1), axis=1) == 0, axis=1)
    candidates = np.flatnonzero(~collapsed)
    _, unique_idx = np.unique(np.sort(remapped[candidates], axis=1), axis=0, return_index=True)
    kept = candidates[np.sort(unique_idx)]
    changed = np.flatnonzero(np.any(remapped != faces, axis=1))
    result = trimesh.Trimesh(verts.copy(), remapped[kept], process=False)
    result.remove_unreferenced_vertices()
    cluster_members = np.flatnonzero(parent != np.arange(len(parent)))
    audit = {
        "tolerance_mm": tolerance, "near_vertex_pairs": len(pairs),
        "merged_vertices": len(cluster_members), "collapsed_faces_removed": int(collapsed.sum()),
        "duplicate_faces_removed": len(candidates) - len(kept),
        "removed_faces": np.setdiff1d(np.arange(len(faces)), kept).tolist(),
        "changed_original_face_indices": changed.tolist(),
        "max_vertex_displacement_mm": float(move.max(initial=0)),
        "clusters": [{"old_vertex": int(i), "representative": int(parent[i]),
                      "before_mm": verts[i].tolist(), "after_mm": verts[parent[i]].tolist(),
                      "displacement_mm": float(move[i])} for i in cluster_members],
        "unchanged_vertices_fraction": float(np.mean(move == 0)),
        "bounds_max_delta_mm": float(np.max(np.abs(result.bounds - mesh.bounds))),
        "volume_delta_mm3": float(result.volume - mesh.volume),
        "surface_area_delta_mm2": float(result.area - mesh.area),
        "kept_original_face_indices_sha256": hashlib.sha256(kept.astype('<i8').tobytes()).hexdigest(),
        "method": "KD-tree proximity clusters; original-coordinate representatives; remove collapsed/duplicate triangles only",
        "hole_fill": False, "smoothing": False, "global_remesh": False,
    }
    return result, audit


def acceptable(qa):
    return (qa["finite"] and qa["watertight"] and qa["winding_consistent"] and qa["volume_valid"]
            and qa["boundary_edges"] == qa["nonmanifold_edges"] == 0
            and qa["degenerate_faces_area_under_1e-10_mm2"] == qa["duplicate_faces"] == 0
            and qa["nonmanifold_vertices"] == 0)


def repair_file(source, output, report_path, *, tolerances=(1e-6, 1e-5, 2e-5, 5e-5)):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError("Original replacement is forbidden")
    if output.exists():
        raise FileExistsError(output)
    original = trimesh.load(source, force="mesh", process=True)
    before = mesh_qa(original)
    trials = []
    for tolerance in tolerances:
        fixed, delta = collapse_precision_clusters(original, tolerance)
        qa = mesh_qa(fixed)
        trials.append({"tolerance_mm": tolerance, "qa": qa})
        if acceptable(qa):
            break
    else:
        raise RuntimeError("No precision-only repair passes topology; inspect the retained source")
    if delta["bounds_max_delta_mm"] > 1e-4:
        raise RuntimeError("Bounds exceed unchanged-dimension budget")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(fixed.export(file_type="stl"))
    # Independent reload: validate what was written, not the in-memory candidate.
    reloaded = trimesh.load(output, force="mesh", process=True)
    after = mesh_qa(reloaded)
    if not acceptable(after):
        raise RuntimeError("Exported STL fails topology")
    glb = output.with_suffix('.glb')
    glbmesh = reloaded.copy()
    glbmesh.apply_scale(0.001)  # glTF standard meters, STL model millimeters
    glbmesh.visual = trimesh.visual.ColorVisuals(glbmesh, vertex_colors=[188, 174, 148, 255])
    glbmesh.metadata.update({"status": VERSION, "source_stl_sha256": digest(source), "source_units": "mm", "glb_units": "m"})
    scene = trimesh.Scene()
    scene.add_geometry(glbmesh, node_name=output.stem, geom_name=output.stem)
    glb.write_bytes(scene.export(file_type='glb'))
    glb_read = trimesh.load(glb, force="mesh", process=True)
    glb_read.apply_scale(1000)
    glbqa = mesh_qa(glb_read)
    roundtrip_delta = float(np.max(np.abs(glb_read.bounds - reloaded.bounds)))
    if not acceptable(glbqa) or roundtrip_delta > 1e-4:
        raise RuntimeError("GLB roundtrip fails QA")
    report = {"version": VERSION, "source": str(source), "source_sha256": digest(source),
              "output": str(output), "output_sha256": digest(output), "glb_sha256": digest(glb),
              "units": {"STL": "nominal model millimeters", "GLB": "meters", "historic_calibration": None},
              "before": before, "after_stl_reload": after, "glb_reload_in_mm": glbqa,
              "glb_bounds_roundtrip_max_error_mm": roundtrip_delta, "repair": delta, "trials": trials,
              "status": "EXPERIMENTAL; topology validated; no architectural/historical/structural approval"}
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(json.dumps(report, indent=2))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source')
    ap.add_argument('-o', '--output', required=True)
    ap.add_argument('--report', required=True)
    a = ap.parse_args()
    r = repair_file(a.source, a.output, a.report)
    print(json.dumps({"source": a.source, "output": a.output, "repair": {k:v for k,v in r['repair'].items() if k not in ('clusters','changed_original_face_indices','removed_faces')}, "after":r['after_stl_reload']}, indent=2))


if __name__ == '__main__':
    main()
