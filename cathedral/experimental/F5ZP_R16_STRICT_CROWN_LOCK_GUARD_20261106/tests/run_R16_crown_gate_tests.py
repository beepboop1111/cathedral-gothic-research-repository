#!/usr/bin/env python3
"""Regression suite: actual R06 four-sector, actual R07 six-sector,
synthetic future three/five/eight-arch types, all hard-stop/locks cases.
"""
from pathlib import Path
import json,math,sys,unittest,numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from strict_crown_guard import (
 CrownBelowArchApex,LockedGeometryChange,UnverifiedBoundaryGeometry,
 CrownRule,enforce,preferred_crown,measure_arches)
from guarded_vault_adapter import (preflight_existing_rectangular,
 polygon_R07_arches,source_lock_snapshot)

def arch(i,apex=4200.,spring=3000.,samples=257):
    pts=[]
    for u in np.linspace(0,1,samples):
        pts.append([float(u),float(i),float(spring+(apex-spring)*math.sin(math.pi*u))])
    return {'id':'arch'+str(i),'points_xyz':pts}

class StrictCrownTests(unittest.TestCase):
    def valid(self,arches=None,crown=4425,**kw):
        arcs=arches or [arch(i) for i in range(5)]
        ref={'floorplan':'hash_locked_f5zkc','ribs':list(range(len(arcs)))}
        params=dict(vault_id='TEST',crown_Z=crown,boundary_arches=arcs,
            spring_Z=3000.,cap_Z=4800.,crown_locked=False,
            locks_before=ref,locks_after=ref,intended_export='open_intrados')
        params.update(kw)
        return enforce(**params)
    def test_01_new_3_sector_higher(self):
        r=self.valid([arch(i) for i in range(3)])
        self.assertEqual(r['crown_relation'],'RAISED')
        self.assertEqual(r['arch_count'],3)
    def test_02_new_5_sector_higher(self):
        r=self.valid([arch(i) for i in range(5)])
        self.assertEqual(r['crown_relation'],'RAISED')
    def test_03_new_8_sector_higher(self):
        r=self.valid([arch(i) for i in range(8)])
        self.assertEqual(r['arch_count'],8)
    def test_04_crown_level_generates_warnings(self):
        r=self.valid(crown=4200.)
        self.assertEqual(r['crown_relation'],'LEVEL_WARNING')
        self.assertIn('LEVEL_CROWN_REDUCES_DOME_EFFECT',r['warning_codes'])
        self.assertIn('PREFER_HIGHER_CROWN',r['warning_codes'])
    def test_05_crown_below_rejected_hard(self):
        with self.assertRaises(CrownBelowArchApex):
            self.valid(crown=4199.999999)
    def test_06_detects_highest_apex_of_all_arcs(self):
        a=[arch(0,apex=4100),arch(1,apex=4220),arch(2,apex=4200)]
        with self.assertRaises(CrownBelowArchApex):
            self.valid(a,crown=4210.)
        q=self.valid(a,crown=4220.)
        self.assertEqual(q['highest_apex_Z'],4220.)
        self.assertEqual(q['crown_relation'],'LEVEL_WARNING')
    def test_07_locked_crown_valid_but_no_raise(self):
        r=self.valid(crown=4200.,crown_locked=True)
        self.assertIn('CROWN_LOCKED_DO_NOT_RAISE',r['warning_codes'])
        self.assertTrue(r['no_automatic_crown_changes'])
        self.assertEqual(r['crown_Z'],4200.)
    def test_08_immutable_lock_mismatch_rejected(self):
        with self.assertRaises(LockedGeometryChange):
            self.valid(locks_after={'floorplan':'shifted_invalid'})
    def test_09_unnamed_empty_arches_rejected(self):
        with self.assertRaises(UnverifiedBoundaryGeometry):
            self.valid(boundary_arches=[])
    def test_10_missing_arch_sample_warned(self):
        r=self.valid([arch(0,samples=11)])
        self.assertIn('LOW_ARCH_SAMPLING',r['warning_codes'])
    def test_11_caps_not_approved_for_closed_export(self):
        with self.assertRaises(ValueError):
            self.valid(cap_Z=4300.,web_peak_Z=4370.,
                       intended_export='closed_masonry')
    def test_12_cap_conflict_only_warns_open_study(self):
        r=self.valid(crown=4300.,cap_Z=4341.,web_peak_Z=4370.34,
                     intended_export='open_intrados')
        self.assertIn('CAP_INTERSECTION_OR_INSUFFICIENT_COVER',r['warning_codes'])
        self.assertIn('WEB_ABOVE_CROWN_REVIEW_CAP',r['warning_codes'])
    def test_13_report_always_discloses_locks(self):
        r=self.valid()
        self.assertIn('LOCKED_GEOMETRY_WARNING_ALWAYS',r['warning_codes'])
        self.assertTrue(r['locked_snapshot_hash_verified'])
        self.assertGreaterEqual(len(r['warnings'][0]['protected']),5)
    def test_14_avoids_inventing_baseline(self):
        r=self.valid(locks_after=None)
        self.assertFalse(r['locked_snapshot_hash_verified'])
        self.assertIn('LOCK_REFERENCE_NOT_FULLY_VERIFIED',r['warning_codes'])
    def test_15_unlocked_preference_always_higher(self):
        p=preferred_crown(boundary_arches=[arch(i) for i in range(6)],
                          spring_Z=3000)
        self.assertGreater(p,4200)
        self.assertAlmostEqual(p,4296)
    def test_16_historical_real_4_sector_V4_inputs(self):
        raw=json.loads((ROOT/'reference/CHAPEL_TWO_BAYS_4296_POINTED_SKELETON_ZERO_BULGE.json').read_text())
        for record in raw['bays']:
            q=preflight_existing_rectangular(record)
            self.assertEqual(q['arch_count'],4)
            self.assertEqual(q['crown_relation'],'LEVEL_WARNING')
            self.assertIn('CROWN_LOCKED_DO_NOT_RAISE',q['warning_codes'])
            self.assertTrue(q['locked_snapshot_hash_verified'])
    def test_17_historical_real_6_sector_R07(self):
        arcs=polygon_R07_arches()
        p=ROOT.parent/'CHAPEL_APSE_R14_BOTH_USER_RED_TYPES_EXPERIMENTAL'
        refs=source_lock_snapshot([
            p/'configs/R14_TWO_TYPES_REDLINE.json',
            p/'scripts/build_R14_two_user_drawn_web_types.py'])
        q=enforce(vault_id='R14_SIX_SECTOR_ORIGINAL_UNMODIFIED',
             boundary_arches=arcs,crown_Z=4296,spring_Z=1800,
             cap_Z=4341,web_peak_Z=4370.341,crown_locked=True,
             locks_before=refs,locks_after=refs)
        self.assertEqual(q['arch_count'],6)
        self.assertEqual(q['crown_relation'],'LEVEL_WARNING')
        self.assertIn('CAP_INTERSECTION_OR_INSUFFICIENT_COVER',q['warning_codes'])
        self.assertTrue(q['locked_snapshot_hash_verified'])
    def test_18_close_no_cap_hard_stop(self):
        with self.assertRaises(ValueError):
            self.valid(cap_Z=None,intended_export='closed_masonry')
    def test_19_nonfinite_apex_hard_stop(self):
        bad=arch(0);bad['points_xyz'][18][2]=float('nan')
        with self.assertRaises(UnverifiedBoundaryGeometry):
            self.valid(boundary_arches=[bad])
    def test_20_new_unlocked_preference_does_not_mutate(self):
        arcs=[arch(i) for i in range(3)]
        before=json.dumps(arcs,sort_keys=True)
        q=self.valid(arcs,crown=4215)
        self.assertEqual(q['crown_Z'],4215)
        self.assertEqual(json.dumps(arcs,sort_keys=True),before)
        self.assertIn('PREFER_HIGHER_CROWN',q['warning_codes'])

    def test_21_closed_masonry_explicit_cover_required(self):
        with self.assertRaises(ValueError):
            self.valid(crown=4425,cap_Z=4750,
                       intended_export='closed_masonry')
    def test_22_closed_masonry_explicit_cover_policy_preflight(self):
        r=self.valid(crown=4425,cap_Z=4750,
                     intended_export='closed_masonry',
                     rule=CrownRule(minimum_cover_for_closed_masonry_native=50))
        self.assertEqual(r['cap_clearance_native'],325)
        self.assertIn('LOCKED_GEOMETRY_WARNING_ALWAYS',r['warning_codes'])
    def test_23_below_apex_error_includes_locked_warning(self):
        with self.assertRaises(CrownBelowArchApex) as ctx:
            self.valid(crown=4199.99)
        self.assertIn('LOCKED_GEOMETRY_WARNING',str(ctx.exception))

    def test_24_builder_inplace_mutation_hard_stop(self):
        from guarded_vault_adapter import guarded_build
        import trimesh
        arcs=[arch(i) for i in range(3)]
        dest=ROOT/'outputs'/'INTENTIONAL_BAD_MUTATION_MUST_NOT_EXPORT'
        self.assertFalse(dest.exists())
        def bad_builder():
            arcs[0]['points_xyz'][0][2]+=1.0
            m=trimesh.Trimesh(vertices=[[0,0,0],[1,0,0],[0,1,0]],faces=[[0,1,2]])
            return {'mesh':m,'boundary_arches':arcs,'crown_Z':4400,
                    'web_peak_Z':4400,'locks':{'original':'baseline'}}
        with self.assertRaises(LockedGeometryChange):
            guarded_build(name='R16_DENY_INPLACE_MUTATION',boundary_arches=arcs,
                crown_Z=4400,spring_Z=3000,cap_Z=4750,
                source_paths=[ROOT/'reference/vault_generator.py'],
                build_in_memory_fn=bad_builder,
                locked_baseline_fn=lambda:{'original':'baseline'},
                output_dir=dest)
        self.assertFalse(dest.exists())
    def test_25_builder_postbuild_changed_boundary_hard_stop(self):
        from guarded_vault_adapter import guarded_build
        import trimesh
        arcs=[arch(i) for i in range(3)]
        dest=ROOT/'outputs'/'INTENTIONAL_BAD_POSTBUILD_MUST_NOT_EXPORT'
        self.assertFalse(dest.exists())
        def bad_builder():
            other=json.loads(json.dumps(arcs));other[0]['points_xyz'][0][2]+=2
            m=trimesh.Trimesh(vertices=[[0,0,0],[1,0,0],[0,1,0]],faces=[[0,1,2]])
            return {'mesh':m,'boundary_arches':other,'crown_Z':4400,
                    'web_peak_Z':4400,'locks':{'original':'baseline'}}
        with self.assertRaises(LockedGeometryChange):
            guarded_build(name='R16_DENY_CHANGED_POSTBUILD_BOUNDARY',
                boundary_arches=arcs,crown_Z=4400,spring_Z=3000,cap_Z=4750,
                source_paths=[ROOT/'reference/vault_generator.py'],
                build_in_memory_fn=bad_builder,
                locked_baseline_fn=lambda:{'original':'baseline'},
                output_dir=dest)
        self.assertFalse(dest.exists())

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(StrictCrownTests)
    report=unittest.TestResult()
    suite.run(report)
    checks={'tests_run':report.testsRun,'failures':[(str(x),str(y)) for x,y in report.failures],
            'errors':[(str(x),str(y)) for x,y in report.errors],
            'all_passed':report.wasSuccessful(),
            'source':'Real 4-sector V4 and 6-sector R07 plus synthetic 3/5/8 families',
            'architectural_status':'Strict generator policy tests only; no approved cathedral geometry changed'}
    from strict_crown_guard import save_report
    save_report(ROOT/'qa/R16_STRICT_CROWN_GUARD_REGRESSION_QA.json',checks)
    print('R16_REGRESSIONS',report.testsRun,'tests','PASS' if report.wasSuccessful() else 'FAIL')
    if not report.wasSuccessful():
        print('FAILURES',checks['failures'],'ERRORS',checks['errors'])
        sys.exit(1)
