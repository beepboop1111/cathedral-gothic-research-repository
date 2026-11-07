#!/usr/bin/env python3
"""Experimental, read-only semantic registry over original tracery region maps.

No historic arc, depth, calibration, or stone/moulding approval is inferred.
IDs use normalized geometry rather than flood-fill labels. Replaying corrections
requires an anchor and geometry guards; changed topology is a conflict.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from skimage.measure import find_contours

VERSION = "M03-R03-experimental"
KINDS = {"opening", "closed_stone", "moulding", "outside", "uncertain"}
DEFAULT_PALETTE = {
    "opening": [0, 0, 255], "closed_stone": [255, 255, 255],
    "linework": [0, 0, 0], "outside": [90, 90, 90],
}
DISPLAY = {
    "opening": "#ed9b42", "closed_stone": "#8ebd90", "moulding": "#a6a4d8",
    "outside": "#dddddd", "uncertain": "#e8b9b9",
}


def digest_bytes(b):
    return hashlib.sha256(b).hexdigest()


def decode_map(rgb, palette=None):
    """Separate meaning from display colors using an explicit palette contract."""
    palette = palette or DEFAULT_PALETTE
    if len({tuple(c) for c in palette.values()}) != len(palette):
        raise ValueError("Palette colors must be unique")
    masks = {name: np.all(rgb == np.asarray(color), axis=2) for name, color in palette.items()}
    assigned = np.zeros(rgb.shape[:2], bool)
    for m in masks.values():
        assigned |= m
    if (~assigned).any():
        masks["unmapped"] = ~assigned
    return masks


def shape_signature(mask):
    """32-square normalized occupancy, stable for exact nearest-neighbor scaling."""
    h, w = mask.shape
    yy = np.minimum(((np.arange(32) + .5) * h / 32).astype(int), h - 1)
    xx = np.minimum(((np.arange(32) + .5) * w / 32).astype(int), w - 1)
    return digest_bytes(np.packbits(mask[np.ix_(yy, xx)]).tobytes())


def geometry_record(mask, sl, image_shape):
    H, W = image_shape
    y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
    ys, xs = np.nonzero(mask)
    dt = ndi.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    ay, ax = np.unravel_index(np.argmax(dt), dt.shape)
    _, complement_components = ndi.label(~np.pad(mask, 1), structure=np.ones((3, 3), int))
    hole_count = max(0, int(complement_components) - 1)
    record = {
        "bbox_uv": [x0 / W, y0 / H, x1 / W, y1 / H],
        "centroid_uv": [(x0 + float(xs.mean()) + .5) / W, (y0 + float(ys.mean()) + .5) / H],
        "area_fraction": int(mask.sum()) / (W * H),
        "shape_signature_sha256": shape_signature(mask),
        "raster_hole_count": hole_count,
    }
    # Floating data are normalized before hashing, so exactly scaled copies agree.
    canonical = {
        "bbox_uv": [round(v, 8) for v in record["bbox_uv"]],
        "centroid_uv": [round(v, 8) for v in record["centroid_uv"]],
        "area_fraction": round(record["area_fraction"], 10),
        "shape_signature_sha256": record["shape_signature_sha256"],
        "raster_hole_count": hole_count,
    }
    record.update({
        "face_id": "face-" + digest_bytes(json.dumps(canonical, sort_keys=True).encode())[:20],
        "anchor_uv": [(x0 + int(ax) + .5) / W, (y0 + int(ay) + .5) / H],
        "bbox_px": [x0, y0, x1, y1], "area_px": int(mask.sum()),
        "max_inscribed_radius_px": float(dt.max()),
        "max_inscribed_radius_fraction_width": float(dt.max()) / W,
        "touches_image_edges": [edge for edge, yes in [
            ("left", x0 == 0), ("right", x1 == W), ("top", y0 == 0), ("bottom", y1 == H)
        ] if yes],
    })
    return record


def classify(record, input_kind):
    """Keep map decisions; make linework and moulding hypotheses explicit."""
    area, rad = record["area_px"], record["max_inscribed_radius_px"]
    evidence = ["Input semantic palette: " + input_kind]
    flags = []
    if record["touches_image_edges"]:
        flags.append("crop_edge_contact")
        evidence.append("Boundary meets image edge; complete historical boundary is unverified")
    if input_kind == "opening":
        kind, confidence = "opening", .9
        evidence.append("Inherited original region-map classification, not new historical verification")
        if flags:
            confidence = .5
            flags.append("opening_may_be_crop_truncated")
    elif input_kind == "outside":
        kind, confidence = "outside", .95
        evidence.append("Inherited outside mask; crop boundary is recorded")
    elif input_kind == "closed_stone":
        compactness = area / max(rad * rad, 1)
        if record.get("support_context") == "detached_small_stone_island":
            kind, confidence = "uncertain", .15
            evidence.append("Detached small stone-mask island: possible annotation or loose fragment; preserve for review")
            flags.append("detached_annotation_or_fragment_candidate")
        elif record["area_fraction"] < 2e-6 or record["max_inscribed_radius_fraction_width"] < .0008:
            kind, confidence = "uncertain", .15
            evidence.append("Very small white component: retain as unresolved raster detail; do not infer a moulding")
            flags.append("small_component_unresolved")
        elif record["max_inscribed_radius_fraction_width"] < .015 or compactness > 10:
            kind, confidence = "moulding", .4
            evidence.append("Thin-band/compactness heuristic: provisional moulding candidate only")
            flags.append("moulding_unverified")
        else:
            kind, confidence = "closed_stone", .7
            evidence.append("White stone face in inherited map; physical depth is unknown")
        if flags and "crop_edge_contact" in flags:
            kind, confidence = "uncertain", .25
            evidence.append("Stone/band touches crop edge; classification withheld")
    else:
        kind, confidence = "uncertain", .2
        evidence.append("Drawing ink/unmapped marks may include mouldings, axes or annotations")
        flags.append("linework_not_historical_moulding_proof")
    return kind, confidence, evidence, flags


def extract_faces(masks, reverse_labels=False):
    faces = []
    image_shape = next(iter(masks.values())).shape
    stone = np.ones(image_shape, bool)
    for category in ("opening", "outside"):
        if category in masks:
            stone &= ~masks[category]
    support, support_n = ndi.label(stone, structure=np.ones((3, 3), int))
    support_areas = np.bincount(support.ravel())
    support_areas[0] = 0
    largest_support = int(support_areas.max()) if support_n else 0
    for input_kind in sorted(masks):
        mask = masks[input_kind]
        labels, n = ndi.label(mask)
        objects = ndi.find_objects(labels)
        indices = range(n, 0, -1) if reverse_labels else range(1, n + 1)
        for i in indices:
            sl = objects[i - 1]
            local = labels[sl] == i
            rec = geometry_record(local, sl, mask.shape)
            if input_kind not in ("opening", "outside"):
                ax = min(int(rec["anchor_uv"][0] * image_shape[1]), image_shape[1] - 1)
                ay = min(int(rec["anchor_uv"][1] * image_shape[0]), image_shape[0] - 1)
                area = int(support_areas[support[ay, ax]])
                rec["support_context"] = "detached_small_stone_island" if area < .02 * largest_support else "principal_stone_network"
                rec["support_area_fraction"] = area / (image_shape[0] * image_shape[1])
            kind, confidence, evidence, flags = classify(rec, input_kind)
            rec.update({"classification": kind, "input_kind": input_kind,
                        "confidence": confidence, "evidence": evidence,
                        "flags": flags, "status": "experimental",
                        "manual_correction": False})
            faces.append((rec, local))
    faces.sort(key=lambda f: f[0]["face_id"])
    ids = [r["face_id"] for r, _ in faces]
    if len(ids) != len(set(ids)):
        raise ValueError("Geometry ID collision; refuse unstable register")
    return faces


def correction_template(record):
    return {k: record[k] for k in ("face_id", "anchor_uv", "bbox_uv", "area_fraction", "shape_signature_sha256", "raster_hole_count")} | {
        "classification": record["classification"],
        "evidence": "Replace with the evidence for this manual decision",
    }


def apply_corrections(faces, corrections, source_family):
    """Apply only unique, guarded matches. Never silently transfer split/merged faces."""
    if corrections.get("source_family") != source_family:
        return [], [{"reason": "source_family_mismatch"}]
    accepted, conflicts = [], []
    used = set()
    for correction in corrections.get("overrides", []):
        if correction.get("classification") not in KINDS:
            conflicts.append({"face_id": correction.get("face_id"), "reason": "invalid_classification"})
            continue
        try:
            anchor = np.asarray(correction["anchor_uv"], float)
            old_bbox = np.asarray(correction["bbox_uv"], float)
            old_area = float(correction["area_fraction"])
            old_shape = correction["shape_signature_sha256"]
            old_holes = int(correction["raster_hole_count"])
            if anchor.shape != (2,) or old_bbox.shape != (4,) or old_area <= 0:
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            conflicts.append({"face_id": correction.get("face_id"), "reason": "missing_geometry_guard"})
            continue
        matches = []
        for rec, mask in faces:
            x0, y0, x1, y1 = rec["bbox_uv"]
            if not (x0 <= anchor[0] < x1 and y0 <= anchor[1] < y1):
                continue
            yy = min(int((anchor[1] - y0) / (y1 - y0) * mask.shape[0]), mask.shape[0] - 1)
            xx = min(int((anchor[0] - x0) / (x1 - x0) * mask.shape[1]), mask.shape[1] - 1)
            if not mask[yy, xx]:
                continue
            area_change = abs(rec["area_fraction"] / old_area - 1)
            bbox_change = float(np.max(abs(np.asarray(rec["bbox_uv"]) - old_bbox)))
            if (area_change <= .025 and bbox_change <= .003 and
                    rec["shape_signature_sha256"] == old_shape and
                    rec["raster_hole_count"] == old_holes):
                matches.append(rec)
        if len(matches) != 1 or matches[0]["face_id"] in used:
            conflicts.append({"face_id": correction.get("face_id"),
                              "reason": "split_merge_or_geometry_mismatch", "match_count": len(matches)})
            continue
        rec = matches[0]
        used.add(rec["face_id"])
        rec["classification"] = correction["classification"]
        rec["confidence"] = 1.0
        rec["evidence"].append("Manual semantic decision: " + str(correction.get("evidence", "unspecified")))
        rec["manual_correction"] = True
        rec["status"] = "experimental_manual_decision"
        accepted.append({"old_id": correction.get("face_id"), "face_id": rec["face_id"],
                         "classification": rec["classification"]})
    return accepted, conflicts


def contour_path(rec, mask):
    x0, y0, _, _ = rec["bbox_px"]
    paths = []
    for c in find_contours(np.pad(mask, 1), .5, fully_connected="low"):
        # Pixel-center coordinates; no fitted geometric arcs are claimed.
        points = np.column_stack((c[:, 1] - 1 + x0 + .5, c[:, 0] - 1 + y0 + .5))
        if len(points) > 3:
            d0, d1 = points[1:-1] - points[:-2], points[2:] - points[1:-1]
            keep = np.r_[True, (d0[:, 0] * d1[:, 1] - d0[:, 1] * d1[:, 0]) != 0, True]
            points = points[keep]
        paths.append("M" + "L".join(f"{x:g},{y:g}" for x, y in points) + "Z")
    return "".join(paths)


def write_svg(path, faces, size, family, source_hash):
    W, H = size
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             f'<title>{html.escape(family)} semantic faces — {VERSION}</title>',
             '<desc>Raster-derived selectable faces, source pixel units. Colors show provisional semantics, not physical depths. No fitted circles or exact historic arcs are claimed.</desc>',
             f'<metadata>{html.escape(json.dumps({"source_sha256": source_hash, "units": "source_pixels", "status": "experimental"}))}</metadata>',
             '<rect width="100%" height="100%" fill="white"/>']
    for rec, mask in faces:
        kind = rec["classification"]
        color = "#222222" if rec["input_kind"] == "linework" else DISPLAY[kind]
        uncertainty = ' stroke="#c12424" stroke-width="0.7" stroke-dasharray="4 3"' if rec["flags"] and rec["input_kind"] != "linework" else ''
        desc = html.escape(json.dumps({k: rec[k] for k in ("classification", "confidence", "flags", "evidence")}))
        lines.append(f'<path id="{rec["face_id"]}" data-classification="{kind}" data-confidence="{rec["confidence"]}" fill="{color}" fill-rule="evenodd"{uncertainty} d="{contour_path(rec, mask)}"><title>{rec["face_id"]}: {kind}</title><desc>{desc}</desc></path>')
    lines.append('</svg>')
    path.write_text('\n'.join(lines))


def write_preview(path, rgb, faces, family):
    image = Image.new("RGB", (rgb.shape[1], rgb.shape[0]), "white")
    a = np.asarray(image).copy()
    for rec, mask in faces:
        x0, y0, x1, y1 = rec["bbox_px"]
        color = "#222222" if rec["input_kind"] == "linework" else DISPLAY[rec["classification"]]
        color = tuple(bytes.fromhex(color[1:]))
        a[y0:y1, x0:x1][mask] = color
    preview = Image.fromarray(a)
    preview.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (preview.width, preview.height + 110), "white")
    canvas.paste(preview, (0, 100))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 20)
    except OSError:
        font = ImageFont.load_default(size=20)
    draw.text((16, 10), f"{family} — M03 R03 experimental semantic register", fill="black", font=font)
    draw.text((16, 38), "Orange openings | green stone | purple provisional moulding | gray outside", fill="black", font=font)
    draw.text((16, 66), "Black observed ink; red unresolved details. Crop contacts flagged. Source pixel units.", fill="black", font=font)
    canvas.save(path)


def build(map_path, out_dir, family, palette=None, corrections=None):
    map_path, out_dir = Path(map_path), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rgb = np.asarray(Image.open(map_path).convert("RGB"))
    masks = decode_map(rgb, palette)
    faces = extract_faces(masks)
    accepted, conflicts = ([], []) if corrections is None else apply_corrections(faces, corrections, family)
    source_hash = digest_bytes(map_path.read_bytes())
    output = {
        "schema": "gothic-semantic-faces/0.3", "version": VERSION,
        "status": "experimental_not_approved", "source_family": family,
        "source_map": str(map_path), "source_map_sha256": source_hash,
        "image_size_px": [rgb.shape[1], rgb.shape[0]], "units": "source_pixels",
        "calibration": None, "physical_depth": None,
        "palette_contract": palette or DEFAULT_PALETTE,
        "id_contract": "Normalized bounding box + centroid + area fraction + normalized occupancy signature; no flood-fill index or palette color in ID. Topology change requires guarded correction reconciliation.",
        "geometry_limit": "SVG contours sample raster boundaries at half-pixel positions; no exact historical curves or cusp construction is inferred.",
        "manual_corrections_applied": accepted, "correction_conflicts": conflicts,
        "faces": [r for r, _ in faces],
    }
    (out_dir / f"{family}_faces_R03.json").write_text(json.dumps(output, indent=2))
    template = {"schema": "gothic-semantic-corrections/0.3", "source_family": family,
                "status": "experimental", "overrides": [],
                "example_not_applied": correction_template(next(r for r, _ in faces if r["input_kind"] == "opening")),
                "instructions": "Copy example_not_applied into overrides and change classification/evidence. Source units and palette do not alter the correction; split/merged geometry is rejected."}
    (out_dir / f"{family}_corrections_TEMPLATE_R03.json").write_text(json.dumps(template, indent=2))
    write_svg(out_dir / f"{family}_semantic_faces_R03.svg", faces, (rgb.shape[1], rgb.shape[0]), family, source_hash)
    write_preview(out_dir / f"{family}_semantic_preview_R03.png", rgb, faces, family)
    qa = {"version": VERSION, "source_family": family, "source_map_sha256": source_hash,
          "face_count": len(faces), "classifications": dict(Counter(r["classification"] for r, _ in faces)),
          "input_component_counts": dict(Counter(r["input_kind"] for r, _ in faces)),
          "coverage_pixels": sum(r["area_px"] for r, _ in faces), "image_pixels": rgb.shape[0] * rgb.shape[1],
          "crop_contact_faces": sum(bool(r["touches_image_edges"]) for r, _ in faces),
          "id_collisions": 0, "manual_corrections_applied": len(accepted), "correction_conflicts": conflicts,
          "original_region_map_modified": False, "mesh_input_map_modified": False}
    (out_dir / f"{family}_semantic_QA_R03.json").write_text(json.dumps(qa, indent=2))
    return qa


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("map")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--family", required=True, help="Stable source family, independent of a display filename")
    ap.add_argument("--palette-json")
    ap.add_argument("--corrections-json")
    a = ap.parse_args()
    palette = json.loads(Path(a.palette_json).read_text()) if a.palette_json else None
    corrections = json.loads(Path(a.corrections_json).read_text()) if a.corrections_json else None
    qa = build(a.map, a.out_dir, a.family, palette, corrections)
    print(json.dumps(qa))
    if qa["correction_conflicts"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
