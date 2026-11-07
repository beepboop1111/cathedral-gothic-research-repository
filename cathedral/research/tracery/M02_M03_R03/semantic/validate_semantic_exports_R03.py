#!/usr/bin/env python3
"""Validate selectable SVG identities and produce matching source/semantic views."""
import json
import hashlib
import shutil
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont


def main():
    directory = Path(__file__).resolve().parent
    root = directory.parent
    names = ["meaux", "haina_1264", "haina_1265", "chalons"]
    qa = []
    W, cellH = 1800, 900
    canvas = Image.new("RGB", (W, cellH * len(names) + 90), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 24)
    except OSError:
        font = ImageFont.load_default(size=24)
    draw.text((24, 14), "M03 R03 — unchanged source map / proposed semantic interpretation", font=font, fill="black")
    draw.text((24, 49), "Source pixels; all classifications experimental. Orange openings, purple provisional moulding, red uncertainty.", font=font, fill="black")
    for i, name in enumerate(names):
        p = directory / name / (name + "_semantic_faces_R03.svg")
        paths = ET.parse(p).findall("{http://www.w3.org/2000/svg}path")
        data = json.loads((p.parent / (name + "_faces_R03.json")).read_text())
        ids = [x.attrib["id"] for x in paths]
        expected = {x["face_id"] for x in data["faces"]}
        assert len(paths) == len(expected) == len(set(ids))
        assert set(ids) == expected
        qa.append({"name": name, "SVG_xml_parses": True, "selectable_paths": len(paths),
                   "unique_ids": True, "matches_json_faces": True})
        raw = Image.open(root / "baseline" / "maps" / (name + "_map.png")).convert("RGB")
        sem = Image.open(p.parent / (name + "_semantic_preview_R03.png")).convert("RGB")
        sem = sem.crop((0, 100, sem.width, sem.height))
        top = 90 + i * cellH
        for column, image in enumerate((raw, sem)):
            image.thumbnail((870, cellH - 70), Image.Resampling.LANCZOS)
            canvas.paste(image, (column * 900 + (900 - image.width) // 2, top + 60))
            draw.text((column * 900 + 24, top + 15), name + (" — original map" if column == 0 else " — semantic view"), font=font, fill="black")
    (directory / "svg_validation_R03.json").write_text(json.dumps(qa, indent=2))
    canvas.save(directory / "semantic_source_comparison_R03.png")
    renders = []
    if shutil.which("inkscape"):
        for name in names:
            source = directory / name / (name + "_semantic_faces_R03.svg")
            output = directory / name / (name + "_SVG_render_R03.png")
            result = subprocess.run(["inkscape", str(source), "--export-type=png", "--export-width=1000",
                "--export-filename=" + str(output)], capture_output=True, text=True)
            renders.append({"window": name, "renderer": "Inkscape", "exit_code": result.returncode,
                "png_exists": output.is_file(), "warnings": result.stderr.strip()})
            assert result.returncode == 0 and output.is_file()
    else:
        renders.append({"renderer": "Inkscape", "status": "unavailable; PIL semantic previews retained"})
    (directory / "svg_render_validation_R03.json").write_text(json.dumps(renders, indent=2))
    evidence=json.loads((directory/"unit_test_evidence_R03.json").read_text())
    if not evidence["success"] or evidence["test_sha256"]!=hashlib.sha256((directory/"test_semantics_R03.py").read_bytes()).hexdigest() or evidence["implementation_sha256"]!=hashlib.sha256((directory/"tracery_semantics_R03.py").read_bytes()).hexdigest():
        raise RuntimeError("Current successful semantic unit-test evidence is required")
    summary = {"version": "M03-R03-experimental", "unit_tests_passed": evidence["tests_run"], "unit_test_evidence": evidence,
        "benchmark_windows": json.loads((directory / "semantic_benchmark_tests_R03.json").read_text()),
        "svg_exports": qa, "original_maps_modified": False, "historical_validation": False,
        "architectural_approval": False,
        "limitations": ["Raster face count includes tiny scan islands, not architectural panels.",
            "Moulding labels are low-confidence hypotheses without physical depth.",
            "Exact2x scaling tested; arbitrary edited/resampled correspondence is not guaranteed.",
            "Source-map opening counts do not establish mesh through-hole counts."]}
    (directory / "semantic_QA_SUMMARY_R03.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(qa))


if __name__ == "__main__":
    main()
