import sys
from pathlib import Path
import tempfile
import unittest
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import gothic_geometry as geo
import gothic_stonework as st
import gothic_adapters as ad


class AdapterTests(unittest.TestCase):
    def test_closed_ring_sweep(self):
        outer = geo.sample_arc((0, 0), 10, 0, 359, 120)
        inner = geo.sample_arc((0, 0), 8, 0, 359, 120)
        mesh, qa = st.sweep_between_rails(outer, inner, [[0, 0], [1, 0], [.5, 1]], 2, closed=True)
        self.assertTrue(mesh.is_watertight)
        self.assertEqual(mesh.euler_number, 0)          # a torus: one hole through it
        self.assertGreater(mesh.volume, 0)

    def test_open_sweep_unchanged(self):
        x = np.linspace(0, 30, 41)
        mesh, _ = st.sweep_between_rails(np.column_stack((x, 0 * x)), np.column_stack((x, 0 * x + 5)),
                                         [[0, 0], [1, 0], [1, 1], [0, 1]], 3)
        self.assertEqual(mesh.euler_number, 2)
        self.assertAlmostEqual(abs(mesh.volume), 30 * 5 * 3, places=6)

    def test_profile_from_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'sec.png'
            a = np.full((60, 40), 255, np.uint8)
            a[10:50, 5:35] = 0                       # 30 wide x 40 tall block
            a[2:4, 2:4] = 0                          # a speck that must be ignored
            Image.fromarray(a).save(p)
            prof = ad.profile_from_png(p)
            self.assertGreater(st.polygon_area(prof), 0)            # CCW
            span = np.ptp(prof, axis=0)
            self.assertAlmostEqual(span[0], 30, delta=1.5)
            self.assertAlmostEqual(span[1], 40, delta=1.5)

    def test_sweep_centerline_with_corner(self):
        line = [[0, 0], [20, 0], [20, 15]]
        mesh = ad.sweep_centerline(line, 2.0, 1.5, z0=4)
        self.assertTrue(mesh.is_watertight)
        self.assertAlmostEqual(mesh.bounds[0][2], 4, places=6)
        self.assertAlmostEqual(mesh.bounds[1][2], 5.5, places=6)

    def test_prism_concave_outline(self):
        cross = [[0, 1], [1, 1], [1, 0], [2, 0], [2, 1], [3, 1], [3, 2], [2, 2],
                 [2, 3], [1, 3], [1, 2], [0, 2]][::-1]          # clockwise on purpose
        mesh = ad.prism_from_polygon(cross, 0, 2)
        self.assertTrue(mesh.is_watertight)
        self.assertAlmostEqual(mesh.volume, 5 * 2, places=6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
