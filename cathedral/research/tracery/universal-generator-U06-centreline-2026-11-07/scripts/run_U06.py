#!/usr/bin/env python3
"""run_U06.py -- run the U06 centreline specs through the UNCHANGED U01, U02 and U03 runners.

The runners are imported from ../../universal-generator-U01-U05-2026-11-07/scripts and only told how to build a
"type": "centreline" spec (T.build, U.Sectioned and run_U03.make are wrapped; nothing is edited on disk).
Regression models go through the same run: all five U01 specs (with the St-Leu fixture regression) and
bar_2light_sexfoil through U02/U03, compared with the archived U01-U05 results.

usage:  python3 -I run_U06.py --out <out dir> --fixture <StLeu_R03_PLAIN_UPRIGHT.stl>
"""
import argparse
import json
import sys
from argparse import Namespace
from pathlib import Path

HERE = Path(__file__).resolve().parent
U15 = HERE.parent.parent / "universal-generator-U01-U05-2026-11-07" / "scripts"
sys.path.insert(0, str(U15))
sys.path.insert(0, str(HERE))

import run_U01  # noqa: E402
import run_U02  # noqa: E402
import run_U03  # noqa: E402
import tracery_centreline_U06 as C  # noqa: E402
import tracery_section_U02 as U  # noqa: E402
import tracery_universal_U01 as T  # noqa: E402

REG = "bar_2light_sexfoil"

_build = T.build


def build(spec, scale=1.0):
    return C.build(spec, scale) if spec.get("type") == "centreline" else _build(spec, scale)


class Sectioned(U.Sectioned):
    def __init__(self, spec, section, scale=1.0, model_cls=None):
        if model_cls is None and spec.get("type") == "centreline":
            model_cls = C.CentrelineModel
        super().__init__(spec, section, scale, model_cls=model_cls)


_make = run_U03.make


def make(spec, sec, js):
    return C.CentrelineJointed(spec, sec, js) if spec.get("type") == "centreline" else _make(spec, sec, js)


T.build, U.Sectioned, run_U03.make = build, Sectioned, make


def same(a, b, path=""):
    """Recursive comparison of archived vs new QA records (floats to 1e-9 relative)."""
    if isinstance(a, dict) and isinstance(b, dict):
        diffs = []
        for k in set(a) | set(b):
            if k in ("version", "title", "note", "notes"):
                continue
            if k not in a or k not in b:
                diffs.append(f"{path}/{k} missing")
            else:
                diffs += same(a[k], b[k], f"{path}/{k}")
        return diffs
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path} length {len(a)} != {len(b)}"]
        return [d for x, y in zip(a, b) for d in same(x, y, path)]
    if isinstance(a, float) or isinstance(b, float):
        return [] if abs(float(a) - float(b)) <= 1e-9 * max(1.0, abs(float(a))) else [f"{path} {a} != {b}"]
    return [] if a == b else [f"{path} {a} != {b}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE.parent / "out"))
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--specs", default=str(HERE / "specs_U06.json"))
    ap.add_argument("--sections", default=str(HERE / "sections_U06.json"))
    ap.add_argument("--joints", default=str(HERE / "joints_U06.json"))
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    specs = json.loads((U15 / "specs_U01.json").read_text()) + json.loads(Path(a.specs).read_text())
    secs = {REG: json.loads((U15 / "sections_U02.json").read_text())[REG], **json.loads(Path(a.sections).read_text())}
    jts = {REG: json.loads((U15 / "joints_U03.json").read_text())[REG], **json.loads(Path(a.joints).read_text())}
    (out / "specs_run.json").write_text(json.dumps(specs, indent=1))
    (out / "sections_run.json").write_text(json.dumps(secs, indent=1))
    (out / "joints_run.json").write_text(json.dumps(jts, indent=1))
    S = str(out / "specs_run.json")
    print("== U01 stage (all U01 specs + U06)")
    run_U01.run_build(Namespace(specs=S, out=str(out / "U01"), fixture=a.fixture))
    print("== U02 stage (orders + mouldings)")
    run_U02.run_build(Namespace(specs=S, sections=str(out / "sections_run.json"), u01=str(out / "U01"), out=str(out / "U02")))
    print("== U03 stage (jointing)")
    run_U03.run_build(Namespace(specs=S, sections=str(out / "sections_run.json"), joints=str(out / "joints_run.json"),
                                out=str(out / "U03")))
    # regression against the archived U01-U05 results
    res = U15.parent / "results"
    reg = {}
    for st in ("U02", "U03"):
        old = json.loads((res / st / f"QA_{st}.json").read_text())["models"][REG]
        new = json.loads((out / st / f"QA_{st}.json").read_text())["models"][REG]
        reg[st] = same(old, new)
        print(f"regression {st} {REG}: {'IDENTICAL' if not reg[st] else 'DIFFERS ' + str(reg[st][:5])}")
    (out / "regression_U06.json").write_text(json.dumps(reg, indent=1))


if __name__ == "__main__":
    main()
