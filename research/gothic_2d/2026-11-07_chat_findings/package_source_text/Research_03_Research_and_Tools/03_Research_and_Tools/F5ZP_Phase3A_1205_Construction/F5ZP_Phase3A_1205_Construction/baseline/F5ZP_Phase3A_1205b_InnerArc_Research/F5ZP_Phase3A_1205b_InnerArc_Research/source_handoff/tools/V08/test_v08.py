import sys
from pathlib import Path
import unittest
import tempfile
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import gothic_plate_reader as pr
import gothic_geometry as geo
import gothic_patterns as pat
import gothic_stonework as st

class V08Tests(unittest.TestCase):
    def test_plate_inspection_and_crop(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'plate.png'
            Image.new('RGB',(80,100),'white').save(p)
            r=pr.inspect_plate(p,(10,20,75,98))
            self.assertEqual(r['crop_px'],[10,20,75,98])
            self.assertIsNone(r['calibration'])
    def test_calibration(self):
        c=pr.Calibration((10,20),(30,20),100,'mm')
        self.assertAlmostEqual(c.units_per_pixel,5)
        self.assertEqual(c.transform((14,17)),(20,15))
    def test_color_separation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'red.png'
            a=np.full((32,32,3),255,np.uint8);a[5:12,4:18]=(230,0,0)
            Image.fromarray(a).save(p)
            mask,_=pr.extract_ink(p,color='red')
            self.assertEqual(int(mask.sum()),98)
    def test_circle_fit(self):
        q=geo.sample_arc((12,-9),30,20,220,150)
        r=geo.circle_fit(q)
        self.assertAlmostEqual(r.radius,30,places=5)
        self.assertLess(r.rmse,1e-7)
    def test_reject_collinear(self):
        with self.assertRaises(ValueError):geo.circle_fit([[0,0],[1,0],[2,0]])
    def test_join(self):
        p=[[[0,0],[5,0]],[[5.8,0],[10,0]]]
        self.assertEqual(len(geo.joining_candidates(p,max_gap=1.)),1)
    def test_reject_branch(self):
        p=[[[0,0],[5,0]],[[5.8,.2],[11,.2]],[[5.8,-.2],[11,-.2]]]
        self.assertEqual(len(geo.joining_candidates(p,max_gap=1.)),0)
    def test_radial_and_partial(self):
        t=pat.radial_instances((0,0),8,master_index=5,selected=[5,6])
        self.assertEqual([a['index'] for a in t],[5,6])
        p=pat.instantiate_points([[10,0]],t)
        np.testing.assert_allclose(p[1]['points'],[[10/np.sqrt(2),10/np.sqrt(2)]],atol=1e-7)
    def test_unique_head_slots(self):
        p=pat.preserve_unique_decorations([[1,2],[2,3]])
        self.assertEqual(len(p),2)
        self.assertTrue(all(x['geometry'] is None for x in p))
    def test_2rail_sweep(self):
        x=np.linspace(0,30,41)
        a=np.column_stack((x, np.zeros(len(x))))
        b=np.column_stack((x, np.full(len(x),5.)))
        profile=[[0,0],[1,0],[1,1],[0,1]]
        mesh,qa=st.sweep_between_rails(a,b,profile,3)
        self.assertTrue(mesh.is_watertight)
        self.assertEqual(mesh.euler_number,2)
        self.assertLess(qa['outer_rail_max_residual'],1e-9)
        self.assertLess(qa['inner_rail_max_residual'],1e-9)
    def test_repeated_scene(self):
        mesh,_=st.sweep_between_rails(np.array([[0,0],[5,0],[10,0]]),np.array([[0,2],[5,2],[10,2]]),[[0,0],[1,0],[1,1],[0,1]],1)
        scene=st.repeat_mesh_radially(mesh,8,master_index=5)
        self.assertEqual(len(scene.graph.nodes_geometry),8)
        self.assertEqual(len(scene.geometry),1)

if __name__=='__main__':unittest.main(verbosity=2)
