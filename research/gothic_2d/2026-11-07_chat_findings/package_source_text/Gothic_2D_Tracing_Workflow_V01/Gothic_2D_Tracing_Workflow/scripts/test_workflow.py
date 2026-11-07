import unittest,sys,json,hashlib,math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from fit_arcs import fit_circle
from four_circle_analysis import C, R, circle_intersections

class WorkflowTests(unittest.TestCase):
    def test_inputs_unchanged(self):
        sources=json.loads((ROOT/'docs/SOURCE_MANIFEST.json').read_text())
        for entry in sources:
            p=ROOT/'inputs'/entry['file']
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),entry['sha256'])

    def test_1193_to_1198_exist(self):
        for i in range(1193,1199):
            self.assertTrue((ROOT/'outputs'/f'{i}_VECTOR_TRACE.svg').is_file())

    def test_svg_layers(self):
        for id in ['1193','1194','1195','FOUR_CIRCLE']:
            txt=(ROOT/'outputs'/f'{id}_VECTOR_TRACE.svg').read_text()
            for group in ['dividing_axes','source_black_outlines','uncertain_alternative_red']:
                self.assertIn(f'id="{group}"',txt)

    def test_four_circle_tangencies(self):
        for x,y in [('K','I'),('I','J'),('J','H'),('H','K')]:
            self.assertEqual(len(circle_intersections(C[x],R,C[y],R)),1)

    def test_square_edges(self):
        q=json.loads((ROOT/'outputs/FOUR_CIRCLE_GEOMETRY.json').read_text())
        self.assertEqual(q['center_square_side_lengths_px'],[310.,310.,310.,310.])
        self.assertEqual(len(q['intersections_between_adjacent_lobes']),4)
        self.assertIn('provisional',q['geometry_status'])

    def test_circle_fit(self):
        t=np.linspace(0.1,2.8,80)
        points=np.column_stack((13+24*np.cos(t),-8+24*np.sin(t)))
        fit=fit_circle(points)
        np.testing.assert_allclose(fit['center'],[13,-8],rtol=0,atol=1e-8)
        self.assertAlmostEqual(fit['radius'],24,places=7)

    def test_duplicate_reference_identified(self):
        d=json.loads((ROOT/'docs/SOURCE_MANIFEST.json').read_text())
        self.assertEqual(d[1]['sha256'],d[2]['sha256'])

if __name__=='__main__':unittest.main(verbosity=2)
