#!/usr/bin/env python3
"""Semantic identity and replay regression tests; never changes original maps."""
import copy
import json
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from tracery_semantics_R03 import (DEFAULT_PALETTE, apply_corrections,
    correction_template, decode_map, extract_faces, geometry_record)


def fixture():
    a = np.zeros((64, 96, 3), np.uint8)
    a[:] = (90, 90, 90)
    a[4:60, 4:92] = (255, 255, 255)
    a[10:30, 10:30] = (0, 0, 255)
    a[20:50, 50:80] = (0, 0, 255)
    a[38:40, 10:38] = (0, 0, 0)
    return a


def id_map(faces):
    return {r["face_id"]: (r["classification"], r["input_kind"]) for r, _ in faces}


class IdentityTests(unittest.TestCase):
    def test_replay_and_floodfill_order(self):
        masks = decode_map(fixture())
        self.assertEqual(id_map(extract_faces(masks)), id_map(extract_faces(masks, reverse_labels=True)))
        self.assertEqual(id_map(extract_faces(masks)), id_map(extract_faces(masks)))

    def test_palette_independent(self):
        a = fixture()
        palette = {"opening": [17, 91, 33], "closed_stone": [33, 22, 91],
                   "linework": [101, 44, 77], "outside": [23, 12, 8]}
        b = np.zeros_like(a)
        for name, color in DEFAULT_PALETTE.items():
            b[np.all(a == color, axis=2)] = palette[name]
        self.assertEqual(id_map(extract_faces(decode_map(a))), id_map(extract_faces(decode_map(b, palette))))

    def test_scaled_identity_and_correction_replay(self):
        a = fixture()
        first = extract_faces(decode_map(a))
        b = np.repeat(np.repeat(a, 2, axis=0), 2, axis=1)
        second = extract_faces(decode_map(b))
        self.assertEqual(id_map(first), id_map(second))
        rec = next(r for r, _ in first if r["input_kind"] == "opening")
        correction = correction_template(rec)
        correction["classification"] = "closed_stone"
        accepted, conflicts = apply_corrections(second, {"source_family": "fixture", "overrides": [correction]}, "fixture")
        self.assertEqual(len(accepted), 1)
        self.assertFalse(conflicts)
        self.assertEqual(next(r for r, _ in second if r["face_id"] == rec["face_id"])["classification"], "closed_stone")

    def test_split_rejects_correction(self):
        a = fixture()
        rec = next(r for r, _ in extract_faces(decode_map(a))
                   if r["input_kind"] == "opening" and r["bbox_px"] == [10, 10, 30, 30])
        correction = correction_template(rec)
        correction["classification"] = "closed_stone"
        a[19:21, 10:30] = (255, 255, 255)
        accepted, conflicts = apply_corrections(extract_faces(decode_map(a)),
            {"source_family": "fixture", "overrides": [correction]}, "fixture")
        self.assertFalse(accepted)
        self.assertEqual(conflicts[0]["reason"], "split_merge_or_geometry_mismatch")

    def test_merge_rejects_correction(self):
        a = fixture()
        rec = next(r for r, _ in extract_faces(decode_map(a)) if r["input_kind"] == "opening")
        correction = correction_template(rec)
        a[20:25, 20:70] = (0, 0, 255)
        accepted, conflicts = apply_corrections(extract_faces(decode_map(a)),
            {"source_family": "fixture", "overrides": [correction]}, "fixture")
        self.assertFalse(accepted)
        self.assertTrue(conflicts)

    def test_cross_source_guard(self):
        rec = extract_faces(decode_map(fixture()))[0][0]
        accepted, conflicts = apply_corrections(extract_faces(decode_map(fixture())),
            {"source_family": "different", "overrides": [correction_template(rec)]}, "fixture")
        self.assertFalse(accepted)
        self.assertEqual(conflicts[0]["reason"], "source_family_mismatch")

    def test_hole_topology_guard(self):
        faces = extract_faces(decode_map(fixture()))
        rec = next(r for r, _ in faces if r["input_kind"] == "opening")
        correction = correction_template(rec)
        correction["raster_hole_count"] += 1
        accepted, conflicts = apply_corrections(faces,
            {"source_family": "fixture", "overrides": [correction]}, "fixture")
        self.assertFalse(accepted)
        self.assertEqual(conflicts[0]["reason"], "split_merge_or_geometry_mismatch")

    def test_missing_guard_and_bad_class_rejected(self):
        faces = extract_faces(decode_map(fixture()))
        for correction in ({"classification": "opening"}, {"classification": "glass"}):
            accepted, conflicts = apply_corrections(faces,
                {"source_family": "fixture", "overrides": [correction]}, "fixture")
            self.assertFalse(accepted)
            self.assertTrue(conflicts)

    def test_crop_edges_and_unknown_mark(self):
        a = fixture()
        a[0:20, 20:30] = (0, 0, 255)
        a[50:52, 80:82] = (1, 2, 3)
        faces = extract_faces(decode_map(a))
        self.assertTrue(any("opening_may_be_crop_truncated" in r["flags"] for r, _ in faces))
        self.assertTrue(any(r["input_kind"] == "unmapped" and r["classification"] == "uncertain" for r, _ in faces))
        self.assertEqual(sum(r["area_px"] for r, _ in faces), a.shape[0] * a.shape[1])


def benchmark_tests(root):
    results = []
    counts = {"meaux": 48, "haina_1264": 21, "haina_1265": 30, "chalons": 19}
    for name, expected in counts.items():
        path = root / "baseline" / "maps" / (name + "_map.png")
        rgb = np.asarray(Image.open(path).convert("RGB"))
        masks = decode_map(rgb)
        faces = extract_faces(masks)
        reversed_faces = extract_faces(masks, reverse_labels=True)
        assert id_map(faces) == id_map(reversed_faces), name + " changed IDs under label reordering"
        assert len([r for r, _ in faces if r["input_kind"] == "opening"]) == expected, name + " opening mismatch"
        assert sum(r["area_px"] for r, _ in faces) == rgb.shape[0] * rgb.shape[1]
        scaled_openings = 0
        for rec, mask in faces:
            if rec["input_kind"] != "opening":
                continue
            x0, y0, x1, y1 = rec["bbox_px"]
            scaled_mask = np.repeat(np.repeat(mask, 2, axis=0), 2, axis=1)
            scaled = geometry_record(scaled_mask, (slice(2*y0,2*y1), slice(2*x0,2*x1)),
                (2*rgb.shape[0], 2*rgb.shape[1]))
            assert scaled["face_id"] == rec["face_id"], name + " scaled opening ID mismatch"
            scaled_openings += 1
        # Exercise one manual decision, retaining all original source bytes.
        opening = next(r for r, _ in faces if r["input_kind"] == "opening")
        correction = correction_template(opening)
        correction["classification"] = "uncertain"
        applied, conflicts = apply_corrections(reversed_faces,
            {"source_family": name, "overrides": [correction]}, name)
        assert len(applied) == 1 and not conflicts
        results.append({"window": name, "face_count": len(faces), "map_openings": expected,
            "repeat_and_reordered_labels": "PASS", "full_image_coverage": "PASS",
            "manual_decision_replay": "PASS", "opening_faces_exact_2x_identity": scaled_openings,
            "original_map_changed": False})
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == "--benchmarks":
        root = Path(__file__).resolve().parent.parent
        results = benchmark_tests(root)
        out = Path(__file__).parent / "semantic_benchmark_tests_R03.json"
        out.write_text(json.dumps(results, indent=2))
        print(json.dumps(results))
    else:
        import hashlib
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(IdentityTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        directory = Path(__file__).resolve().parent
        evidence = {"tests_run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "success": result.wasSuccessful(),
            "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "implementation_sha256": hashlib.sha256((directory/"tracery_semantics_R03.py").read_bytes()).hexdigest()}
        (directory/"unit_test_evidence_R03.json").write_text(json.dumps(evidence,indent=2))
        sys.exit(0 if result.wasSuccessful() else 1)
