#!/usr/bin/env python3
"""run_U03.py -- build U03 masonry jointing on U02 sections, run QA, compose PNG.

  python3 -I run_U03.py build   --out out_U03
  python3 -I run_U03.py compose --out out_U03
"""
import argparse
import copy
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from shapely import wkt as swkt  # noqa: E402

import tracery_joints_U03 as J  # noqa: E402
import tracery_universal_U01 as T  # noqa: E402


def t_(kind, name, ok, detail=""):
    return dict(kind=kind, name=name, ok=bool(ok), detail=detail)


def make(spec, sec, js):
    if spec.get("type") == "rose":
        import tracery_rose_U04 as R
        return R.RoseJointed(spec, sec, js)
    return J.Jointed(spec, sec, js)


def run_build(a):
    specs = {s["id"]: s for s in json.loads(Path(a.specs).read_text())}
    secs = json.loads(Path(a.sections).read_text())
    jts = json.loads(Path(a.joints).read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report, geoms = {"version": J.VERSION, "models": {}}, {}
    for mid, js in jts.items():
        j = make(specs[mid], secs[mid], js)
        mc = j.m.checks
        tests = [t_("geometric", f"construction/topology checks ({sum(c['ok'] for c in mc)}/{len(mc)})",
                    all(c["ok"] for c in mc), "; ".join(c["name"] for c in mc if not c["ok"])[:300])] + list(j.checks) + [dict(c, name="U02: " + c["name"]) for c in j.u.checks if "interpenetrate" not in c["name"]]
        parts, ok_blocks, bad = {}, [], []
        for nm, mesh, _, _ in j.parts:
            qa = T.mesh_qa(mesh)
            parts[nm] = qa
            if nm == "glass":
                continue
            ok = qa["watertight"] and qa["winding_consistent"] and qa["volume"] > 0 and qa["nonmanifold_edges"] == 0 \
                and qa["degenerate_faces"] == 0 and qa["unreferenced_vertices"] == 0 and qa["bodies"] == 1
            if nm.startswith("stone_"):
                md = j.meta[nm]
                vmax = sum(2 * j.u.order_of(k)["H"] * A for k, A in md["label_areas"].items())
                vmin = sum(2 * (j.u.order_of(k)["H"] - float(j.u.order_of(k)["prof"][:, 1].max())) * A
                           for k, A in md["label_areas"].items())
                ok = ok and qa["euler"] == 2 - 2 * md["holes"] and vmin * (1 - 1e-9) <= qa["volume"] <= vmax * (1 + 1e-9)
                ok_blocks.append(ok)
                if not ok:
                    bad.append((nm, {x: qa[x] for x in ("watertight", "winding_consistent", "nonmanifold_edges",
                                                        "degenerate_faces", "bodies", "euler")}, md["holes"]))
            else:
                tests.append(t_("geometric", f"{nm}: closed, one body", ok))
        tests.append(t_("geometric", f"all {len(ok_blocks)} stones: watertight, consistent winding, one body, genus = holes, "
                        "0 nonmanifold/degenerate, volume within section bounds", all(ok_blocks), json.dumps(bad[:3])))
        data = j.export_glb(out / f"{mid}.glb")
        sc = trimesh.load(io.BytesIO(data), file_type="glb", process=False, force="scene")
        ok_rt = all((g := sc.geometry.get(f"{mid}__{nm}")) is not None and len(g.vertices) == len(mesh.vertices)
                    and len(g.faces) == len(mesh.faces) and np.allclose(g.bounds, mesh.bounds, atol=1e-6 * j.m.size)
                    for nm, mesh, _, _ in j.parts)
        tests.append(t_("technical", "GLB export -> reload: counts and bounds unchanged", ok_rt))
        j2 = make(copy.deepcopy(specs[mid]), copy.deepcopy(secs[mid]), copy.deepcopy(js))
        tests.append(t_("technical", "rebuild is bit-identical",
                        [T.mesh_hash(x[1]) for x in j.parts] == [T.mesh_hash(x[1]) for x in j2.parts]))
        nb = sum(1 for x in j.parts if x[0].startswith("stone_"))
        kinds = {}
        for jj in j.joints:
            kinds[jj["kind"]] = kinds.get(jj["kind"], 0) + 1
        rec = dict(id=mid, units=specs[mid].get("units"), joints=js, joint_kinds=kinds, notes=j.notes, blocks=nb,
                   frame_blocks=sum(1 for b in j.blocks if b["region"] == "frame"),
                   largest=max(b["long"] for b in j.blocks), smallest_short=min(b["short"] for b in j.blocks),
                   checks=tests,
                   parts={k: dict(v, bounds_blender=[[v["bounds"][0][0], -v["bounds"][1][2], v["bounds"][0][1]],
                                                     [v["bounds"][1][0], -v["bounds"][0][2], v["bounds"][1][1]]])
                          for k, v in parts.items()})
        report["models"][mid] = rec
        geoms[mid] = dict(blocks=[dict(name=b["name"], region=b["region"], wkt=b["poly"].wkt) for b in j.blocks],
                          joints=[dict(kind=x["kind"], wkt=x["seg"].intersection(j.m.stone.buffer(j.e)).wkt) for x in j.joints],
                          zones=[z.wkt for z in j.zones], voids=[v["poly"].wkt for v in j.m.voids])
        badt = [c for c in tests if not c["ok"]]
        print(f"{mid}: {len(tests) - len(badt)}/{len(tests)} pass | {nb} stones ({rec['frame_blocks']} frame) | joints {kinds}"
              f" | largest {rec['largest']:.0f} | notes {len(j.notes)}")
        for c in badt:
            print("   FAIL", c["kind"], c["name"][:150], c["detail"][:300])
    (out / "QA_U03.json").write_text(json.dumps(report, indent=1, default=float))
    (out / "QA_U01.json").write_text(json.dumps(report, indent=1, default=float))  # name read by the Blender checker
    (out / "geom_U03.json").write_text(json.dumps(geoms))


def run_compose(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath

    out = Path(a.out)
    qa = json.loads((out / "QA_U03.json").read_text())
    bq = json.loads((out / "blender_QA_U01.json").read_text())
    G = json.loads((out / "geom_U03.json").read_text())

    def patch(g, **kw):
        g = swkt.loads(g) if isinstance(g, str) else g
        verts, codes = [], []
        for p in T.polys(g):
            for r in [p.exterior, *p.interiors]:
                c = np.asarray(r.coords)
                verts += c.tolist()
                codes += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY]
        return PathPatch(MPath(verts, codes), **kw)

    fig = plt.figure(figsize=(24, 16.5), dpi=100, facecolor="white")
    fig.text(0.01, 0.99, "U03 masonry jointing (EXPERIMENTAL): coursed jambs and mullions, voussoirs radial to each arc, "
             "rings cut at lobe centres, junctions kept inside single stones", fontsize=16, weight="bold", va="top")
    ax0 = fig.add_axes([0.0, 0.60, 1.0, 0.37])
    img = plt.imread(out / "render_U02.png")
    ax0.imshow(img)
    ax0.axis("off")
    H, W = img.shape[:2]
    for lab in bq["labels"]:
        r = qa["models"][lab["id"]]
        ax0.text(lab["u"] * W, 0.975 * H, f"{lab['id']}  ({r['blocks']} stones)", ha="center", va="bottom", fontsize=11,
                 weight="bold", bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
    ax1 = fig.add_axes([0.005, 0.20, 0.36, 0.385])
    ax1.imshow(plt.imread(out / "closeup_U02.png"))
    ax1.axis("off")
    ax1.set_title("(a) bar_4light head, raking light: 6 mm open joints; cusps carved with their ring stones; orders step "
                  "inside each stone", fontsize=10, loc="left")
    pal = ["#d9c9a3", "#c9b48a", "#e4d8bb", "#bfa77a", "#d2bf95"]
    for ax_pos, mid, xl, yl, ttl in (([0.39, 0.20, 0.20, 0.385], "bar_4light_recursive", (-2700, 2700), (-300, 9300),
                                      "(b) bar_4light joint layout"),
                                     ([0.60, 0.20, 0.13, 0.385], "bar_2light_sexfoil", (-1500, 1500), (-250, 6000),
                                      "(c) bar_2light"),
                                     ([0.74, 0.20, 0.12, 0.385], "intersecting_3light", (-1600, 1600), (-250, 6100),
                                      "(d) intersecting"),
                                     ([0.87, 0.20, 0.125, 0.385], "stleu_fig80_rebuild", (40, 500), (-40, 730),
                                      "(e) St-Leu plate (px)")):
        ax = fig.add_axes(ax_pos)
        g = G[mid]
        for i, b in enumerate(g["blocks"]):
            ax.add_patch(patch(b["wkt"], fc=("#b7a98f" if b["region"] == "frame" else pal[i % len(pal)]), ec="#5b4a2f",
                               lw=0.35))
        for z in g["zones"]:
            ax.add_patch(patch(z, fc="none", ec="#c0392b", lw=0.5, ls=(0, (2, 2))))
        ax.set_aspect("equal")
        ax.set_xlim(*xl)
        ax.set_ylim(*yl)
        ax.axis("off")
        ax.set_title(ttl + "\n(red dashed = junction keep-out)", fontsize=10, loc="left")
    ax4 = fig.add_axes([0.01, 0.005, 0.98, 0.18])
    ax4.axis("off")
    rows = [f"{'model':22s} {'geometric':>10s} {'architect.':>10s} {'technical':>10s}  Blender  stones (frame)  joints by kind"
            "                                    largest stone"]
    for k, v in qa["models"].items():
        cs = v["checks"]
        f = lambda kind: f"{sum(c['ok'] for c in cs if c['kind'] == kind)}/{sum(c['kind'] == kind for c in cs)}"
        b = "ok" if bq["models"][k]["ok"] else "FAIL"
        rows.append(f"{k[:22]:22s} {f('geometric'):>10s} {f('architectural'):>10s} {f('technical'):>10s}  {b:7s}  "
                    f"{v['blocks']:>4d} ({v['frame_blocks']:>3d})    {json.dumps(v['joint_kinds']):48s} {v['largest']:.0f}")
    rows += ["",
             "Geometric: stones + open joints account for the stone area; radial joints pass through their centres; every stone "
             "watertight, one body, genus = holes; Blender 0 nonmanifold / degenerate / self-intersecting.",
             "Architectural: no voussoir or ring joint inside a junction keep-out; largest stone within the trial maximum; "
             "course, voussoir, keep-out and joint sizes are TRIAL values.",
             "Historical: jointing follows the documented principle (coursed mullions; arcs and oculus jointed onto mullion "
             "and jambs), not a survey of any building.   Structural: not assessed."]
    ax4.text(0.0, 1.0, "\n".join(rows), fontsize=9.4, family="monospace", va="top")
    fig.savefig(out / "U03_joints.png", dpi=100, facecolor="white")
    print("wrote", out / "U03_joints.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["build", "compose"])
    ap.add_argument("--specs", default="specs_U01.json")
    ap.add_argument("--sections", default="sections_U02.json")
    ap.add_argument("--joints", default="joints_U03.json")
    ap.add_argument("--out", default="out_U03")
    a = ap.parse_args()
    run_build(a) if a.stage == "build" else run_compose(a)
