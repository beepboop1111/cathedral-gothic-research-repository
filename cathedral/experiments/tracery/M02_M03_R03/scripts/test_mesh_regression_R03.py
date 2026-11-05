#!/usr/bin/env python3
"""Meaningful repair guards plus four saved, independently measured regressions."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
import trimesh
from tracery_repair_R03 import mesh_qa, collapse_precision_clusters, acceptable, repair_file

ROOT=Path(__file__).resolve().parents[1]
REFERENCE_HASHES={
    'meaux':'b32116fb36a59217d6d47c5a7d07328776010e83ad32e0851fc6be4650517ba8',
    'haina_1264':'d836628b6b4d2714da47e79018a0f737781a688a81a50fdad8ae17a697bcbca0',
    'haina_1265':'d3d768e3cba796a0cdcbdb39cfbb3b9626b8368f070930d5321e23422e126598',
    'chalons':'0ce0b2355b7d01f7cb3342cb784177d47310b6bc3c67824d73ecd29a15a740b8'}

class RepairGuards(unittest.TestCase):
    def test_vertex_pinch_is_detected_despite_closed_edges(self):
        a=trimesh.creation.box();a.apply_translation([.5,.5,.5])
        b=trimesh.creation.box();b.apply_translation([-.5,-.5,-.5])
        mesh=trimesh.util.concatenate([a,b]);mesh.merge_vertices()
        qa=mesh_qa(mesh)
        self.assertTrue(qa['watertight'])
        self.assertEqual(qa['nonmanifold_edges'],0)
        self.assertEqual(qa['nonmanifold_vertices'],1)
        self.assertFalse(acceptable(qa))

    def test_precision_sliver_removed_without_changing_a_valid_solid(self):
        base=trimesh.creation.box();v=base.vertices.copy();faces=[]
        edge=base.edges_unique[0];a,b=map(int,edge)
        q=v[a]+(v[b]-v[a])*1e-7;new=len(v);v=np.vstack([v,q])
        for tri in base.faces:
            if a in tri and b in tri:
                for k in range(3):
                    i,j=tri[k],tri[(k+1)%3];c=tri[(k+2)%3]
                    if {i,j}=={a,b}:
                        faces.extend([[i,new,c],[new,j,c]]);break
            else:faces.append(tri.tolist())
        sliver=trimesh.Trimesh(v,faces,process=False)
        fixed,audit=collapse_precision_clusters(sliver,1e-6)
        self.assertTrue(acceptable(mesh_qa(fixed)))
        np.testing.assert_array_equal(fixed.bounds,base.bounds)
        self.assertAlmostEqual(fixed.volume,base.volume,places=9)
        self.assertGreater(audit['collapsed_faces_removed'],0)

    def test_separate_solids_are_not_joined(self):
        a=trimesh.creation.box();b=a.copy();b.apply_translation([2,0,0]);m=trimesh.util.concatenate([a,b])
        fixed,audit=collapse_precision_clusters(m,1e-5)
        self.assertEqual(mesh_qa(fixed)['surface_components'],2)
        self.assertEqual(audit['merged_vertices'],0)

    def test_large_cleanup_budget_rejected(self):
        with self.assertRaises(ValueError):collapse_precision_clusters(trimesh.creation.box(),.001)

    def test_original_replacement_rejected(self):
        with self.assertRaises(ValueError):repair_file('same.stl','same.stl','report.json')

class FourWindowRegressions(unittest.TestCase):
    def test_baselines_match_original_final_stls_byte_for_byte(self):
        for name,expected in REFERENCE_HASHES.items():
            with self.subTest(window=name):
                p=ROOT/'baseline/models'/f'{name}_R02_reproduced.stl'
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),expected)

    def test_every_original_is_unchanged(self):
        for row in json.loads((ROOT/'qa/originals_frozen_R03.json').read_text()):
            with self.subTest(path=row['path']):
                self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['sha256'])

    def test_roundtripped_topology_and_dimensions(self):
        for name in REFERENCE_HASHES:
            r=json.loads((ROOT/'experimental/qa'/f'{name}_mesh_R03.json').read_text())
            with self.subTest(window=name):
                self.assertTrue(acceptable(r['after_stl_reload']))
                self.assertTrue(acceptable(r['glb_reload_in_mm']))
                self.assertEqual(r['after_stl_reload']['surface_components'],1)
                self.assertLessEqual(r['repair']['bounds_max_delta_mm'],1e-4)
                self.assertLessEqual(r['repair']['max_vertex_displacement_mm'],2e-5)
                self.assertLessEqual(r['glb_bounds_roundtrip_max_error_mm'],1e-4)

    def test_every_source_opening_and_cusp_moulding_section_retained(self):
        for name in REFERENCE_HASHES:
            r=json.loads((ROOT/'experimental/qa'/f'{name}_geometry_R03.json').read_text())
            with self.subTest(window=name):
                self.assertTrue(r['all_classified_opening_anchors_remain_void'])
                self.assertTrue(r['all_classified_opening_pixels_remain_void_after_original_cleanup'])
                self.assertEqual(r['changed_opening_anchor_classifications'],0)
                self.assertEqual(r['source_region_map_changed_pixels'],0)
                self.assertLessEqual(r['max_section_hausdorff_mm'],1e-4)
                self.assertTrue(all(s['original_loops']==s['repaired_loops'] for s in r['sections']))

    def test_exported_stl_and_glb_have_no_detected_self_intersections(self):
        rows=json.loads((ROOT/'qa/self_intersections_R03.json').read_text())
        actual={(r['name'],r['status']) for r in rows if r['status']!='original'}
        self.assertEqual(actual,{(n,s) for n in REFERENCE_HASHES for s in ['candidate_STL','candidate_GLB']})
        self.assertTrue(all(r['intersecting_face_count']==0 for r in rows if r['status']!='original'))

if __name__=='__main__':unittest.main(verbosity=2)
