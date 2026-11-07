#!/usr/bin/env python3
"""run_U01.py -- build + automated QA + regression for the U01 universal tracery generator,
and composition of the single review PNG.

  python3 -I run_U01.py build   --specs specs_U01.json --out out --fixture <StLeu_R03_PLAIN_UPRIGHT.stl>
  python3 -I run_U01.py compose --out out
"""
import argparse
import copy
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import shapely  # noqa: E402
import trimesh  # noqa: E402
from shapely import wkt as swkt  # noqa: E402
from shapely.geometry import Polygon, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import tracery_universal_U01 as T  # noqa: E402

CAT = {"geometric": "geometric", "architectural": "architectural", "technical": "technical"}


def fixture_polygon(stl):
    m = trimesh.load(stl, process=False)
    tri = m.triangles
    front = np.abs(tri[:, :, 1]).max(1) < 1e-6
    ps = [Polygon(t[:, [0, 2]]) for t in tri[front]]
    return unary_union([p for p in ps if p.area > 1e-9]).buffer(0), m


def compare(a, b, dens=0.05):
    inter, uni = a.intersection(b).area, a.union(b).area
    return dict(iou=inter / uni, sym_diff_area=a.symmetric_difference(b).area,
                hausdorff=hausdorff(a.boundary, b.boundary, dens))


def hausdorff(a, b, d):
    """Symmetric Hausdorff distance between two boundaries, sampled every d along each."""
    pa = shapely.points(shapely.get_coordinates(shapely.segmentize(a, d)))
    pb = shapely.points(shapely.get_coordinates(shapely.segmentize(b, d)))
    return float(max(shapely.distance(pa, b).max(), shapely.distance(pb, a).max()))


def reordered(obj):
    if isinstance(obj, dict):
        return {k: reordered(obj[k]) for k in reversed(list(obj.keys()))}
    if isinstance(obj, list):
        return [reordered(v) for v in obj]
    return obj


def t_(cat, name, ok, detail=""):
    return dict(kind=cat, name=name, ok=bool(ok), detail=detail)


def run_build(a):
    specs = json.loads(Path(a.specs).read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report, geoms, models = {"version": T.VERSION, "models": {}}, {}, {}
    for spec in specs:
        m = T.build(spec)
        models[m.id] = m
        tests = [dict(kind=c["kind"], name=c["name"], ok=c["ok"], detail=f"value={c['value']:.3g} limit={c['limit']:.3g}")
                 for c in m.checks]
        parts = {}
        for nm, mesh, _, _ in m.parts:
            q = T.mesh_qa(mesh)
            parts[nm] = q
            if nm == "glass":
                continue
            holes = len(m.voids) if nm == "stone" else 1
            tests += [t_("geometric", f"{nm}: watertight, consistent winding, outward volume",
                         q["watertight"] and q["winding_consistent"] and q["volume"] > 0),
                      t_("geometric", f"{nm}: 0 nonmanifold edges / degenerate faces / loose vertices",
                         q["nonmanifold_edges"] == 0 and q["degenerate_faces"] == 0 and q["unreferenced_vertices"] == 0,
                         f"{q['nonmanifold_edges']}/{q['degenerate_faces']}/{q['unreferenced_vertices']}"),
                      t_("geometric", f"{nm}: one body, genus = openings ({holes})",
                         q["bodies"] == 1 and q["euler"] == 2 - 2 * holes, f"bodies={q['bodies']} euler={q['euler']}")]
        A, D, c = m.stone.area, m.D, m.c
        V = parts["stone"]["volume"]
        if all(v.get("chamfer", 0) == 0 for v in m.voids):
            tests.append(t_("geometric", "stone volume == face area x depth", abs(V - A * D) <= 1e-9 * A * D, f"{V:.6g}"))
        else:
            rem = sum((B.area - v["poly"].area) * v["chamfer"] for v, B in zip(m.voids, m.Bs))
            tests.append(t_("geometric", "chamfered volume within 5% of analytic removal",
                            abs((A * D - V) - rem) <= 0.05 * rem, f"removed={A * D - V:.6g} est={rem:.6g}"))
        # GLB export / reload
        data = m.export_glb(out / f"{m.id}.glb")
        sc = trimesh.load(io.BytesIO(data), file_type="glb", process=False, force="scene")
        ok_rt, det = True, []
        for nm, mesh, _, _ in m.parts:
            g = sc.geometry.get(f"{m.id}__{nm}")
            same = g is not None and len(g.vertices) == len(mesh.vertices) and len(g.faces) == len(mesh.faces) \
                and np.allclose(g.bounds, mesh.bounds, atol=1e-6 * m.size)
            ok_rt &= same
            det.append(f"{nm}:{'ok' if same else 'MISMATCH'}")
        tests.append(t_("technical", "GLB export -> reload: counts and bounds unchanged", ok_rt, " ".join(det)))
        # determinism, reordered spec, exact 2x
        h = T.mesh_hash(m.stone_mesh)
        m2 = T.build(copy.deepcopy(spec))
        tests.append(t_("technical", "rebuild is bit-identical", T.mesh_hash(m2.stone_mesh) == h))
        m3 = T.build(reordered(spec))
        tests.append(t_("technical", "reordered spec keys: same opening IDs + mesh",
                        [v["id"] for v in m3.voids] == [v["id"] for v in m.voids] and T.mesh_hash(m3.stone_mesh) == h))
        m4 = T.build(spec, 2.0)
        same_n = len(m4.stone_mesh.vertices) == len(m.stone_mesh.vertices)
        exact2 = same_n and np.allclose(m4.stone_mesh.vertices, 2 * m.stone_mesh.vertices, atol=1e-9 * m4.size)
        tests.append(t_("geometric", "exact 2x: IDs kept, area x4, vertices x2",
                        [v["id"] for v in m4.voids] == [v["id"] for v in m.voids]
                        and abs(m4.stone.area - 4 * A) <= 1e-9 * 4 * A and exact2))
        rec = m.record()
        rec["parts"] = {k: dict(v, bounds_blender=[[v["bounds"][0][0], -v["bounds"][1][2], v["bounds"][0][1]],
                                                    [v["bounds"][1][0], -v["bounds"][0][2], v["bounds"][1][1]]])
                        for k, v in parts.items()}
        rec["checks"], rec["title"], rec["stone_hash"] = tests, spec.get("title", ""), h
        report["models"][m.id] = rec
        (out / f"{m.id}_construction.json").write_text(json.dumps(rec, indent=1))
        geoms[m.id] = dict(stone=m.stone.wkt, outline=m.outline.wkt,
                           voids=[dict(id=v["id"], role=v["role"], wkt=v["poly"].wkt) for v in m.voids],
                           members=[dict(name=x["name"], kind=x["kind"], wkt=x["poly"].wkt) for x in m.members],
                           con=m.con)
    # ---- regression: St-Leu rebuild vs archived early R03 fixture
    fx, fm = fixture_polygon(a.fixture)
    rb = models["stleu_fig80_rebuild"]
    clip = unary_union(T.polys(rb.stone.intersection(box(-1e4, 0, 1e4, 1e4))))
    cm = compare(fx, clip)
    fixture_vol = float(fm.volume)
    reg = dict(fixture=str(Path(a.fixture).name), fixture_face_area=fx.area, rebuild_face_area=clip.area,
               fixture_volume=fixture_vol, rebuild_plain_volume_equiv=clip.area * 12.0, **cm)
    reg_tests = [t_("geometric", f"St-Leu rebuild vs R03 fixture: IoU {cm['iou']:.6f} >= 0.999", cm["iou"] >= 0.999),
                 t_("geometric", f"St-Leu rebuild vs R03 fixture: Hausdorff {cm['hausdorff']:.3f} px <= 1 px "
                    "(max sits at the outer-arch apex, where R03 merged a 1.68 px crown seam)", cm["hausdorff"] <= 1.0),
                 t_("geometric", "St-Leu plain volume equivalent within 0.1% of fixture",
                    abs(clip.area * 12 - fixture_vol) <= 1e-3 * fixture_vol,
                    f"{clip.area * 12:.1f} vs {fixture_vol:.1f}")]
    # ---- construction hypothesis: ideal symmetric/regular vs rebuild
    idl = models["stleu_fig80_ideal"]
    per = {}
    for v in rb.voids:
        w = next(x for x in idl.voids if x["id"] == v["id"])
        per[v["id"]] = compare(v["poly"], w["poly"])["hausdorff"]
    per["outline"] = compare(rb.outline, idl.outline)["hausdorff"]
    hyp = dict(per_element_hausdorff_px=per, **compare(rb.stone, idl.stone))
    report["regression"] = dict(stleu_vs_fixture=reg, tests=reg_tests, stleu_ideal_vs_rebuild=hyp)
    geoms["fixture"] = dict(stone=fx.wkt)
    # ---- baseline
    base_p = out / "baseline_U01.json"
    snap = {k: dict(stone_hash=v["stone_hash"], roles=v["roles"], openings=[o["id"] for o in v["openings"]])
            for k, v in report["models"].items()}
    if base_p.exists():
        base = json.loads(base_p.read_text())
        report["baseline"] = {k: (base.get(k) == s) for k, s in snap.items()}
    else:
        base_p.write_text(json.dumps(snap, indent=1))
        report["baseline"] = "created"
    (out / "QA_U01.json").write_text(json.dumps(report, indent=1, default=float))
    (out / "geom_U01.json").write_text(json.dumps(geoms))
    # ---- console summary
    for k, v in report["models"].items():
        bad = [c for c in v["checks"] if not c["ok"]]
        print(f"{k}: {len(v['checks']) - len(bad)}/{len(v['checks'])} pass | roles {v['roles']} | web {v['web']} | "
              f"chamfer {v['section']['chamfer_used']} | stone V/F {v['parts']['stone']['vertices']}/{v['parts']['stone']['faces']}"
              f" | corrections {[c['type'] for c in v['corrections']]}")
        for c in bad:
            print("   FAIL", c["kind"], c["name"], c["detail"])
    print("REGRESSION", {k: (round(x, 6) if isinstance(x, float) else x) for k, x in reg.items()})
    for c in reg_tests:
        print("  ", "PASS" if c["ok"] else "FAIL", c["name"], c["detail"])
    print("HYPOTHESIS", {k: round(x, 3) for k, x in per.items()}, "IoU", round(hyp["iou"], 5))


# ----------------------------------------------------------------- compose
def run_compose(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath

    out = Path(a.out)
    qa = json.loads((out / "QA_U01.json").read_text())
    bq = json.loads((out / "blender_QA_U01.json").read_text())
    G = json.loads((out / "geom_U01.json").read_text())

    def patch(g, **kw):
        g = swkt.loads(g) if isinstance(g, str) else g
        verts, codes = [], []
        for p in T.polys(g):
            for r in [p.exterior, *p.interiors]:
                c = np.asarray(r.coords)
                verts += c.tolist()
                codes += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY]
        return PathPatch(MPath(verts, codes), **kw)

    def lines(ax, g, **kw):
        g = swkt.loads(g) if isinstance(g, str) else g
        for p in T.polys(g):
            for r in [p.exterior, *p.interiors]:
                c = np.asarray(r.coords)
                ax.plot(c[:, 0], c[:, 1], **kw)

    fig = plt.figure(figsize=(24, 16), dpi=100, facecolor="white")
    fig.text(0.01, 0.985, "U01 universal tracery generator (EXPERIMENTAL) - spec -> analytic construction -> members/junctions "
             "-> stone/void topology -> GLB -> Blender re-import", fontsize=17, weight="bold", va="top")
    ax0 = fig.add_axes([0.005, 0.40, 0.99, 0.56])
    img = plt.imread(out / "render_U01.png")
    ax0.imshow(img)
    ax0.axis("off")
    H, Wd = img.shape[:2]
    for lab in bq["labels"]:
        rec = qa["models"][lab["id"]]
        ax0.text(lab["u"] * Wd, (1 - 0.035) * H, f"{lab['id']}\n{rec['units'].split(';')[0].split('(')[0].strip()}",
                 ha="center", va="bottom", fontsize=11, weight="bold",
                 bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
    ax0.text(0.006 * Wd, 0.012 * H, f"Blender {bq['blender']} - GLBs re-imported, Cycles render; each window scaled to equal "
             "display height (St-Leu in uncalibrated source px; others parametric mm)", fontsize=10, va="top",
             bbox=dict(fc="white", ec="none", alpha=0.85))

    # (a) St-Leu regression
    ax1 = fig.add_axes([0.02, 0.04, 0.20, 0.33])
    ax1.add_patch(patch(G["fixture"]["stone"], fc="#d9d4c8", ec="black", lw=0.7))
    lines(ax1, swkt.loads(G["stleu_fig80_rebuild"]["stone"]).intersection(box(-1e4, 0, 1e4, 1e4)),
          color="#c0392b", lw=0.8, ls=(0, (3, 2)))
    ax1.set_aspect("equal")
    ax1.set_xlim(40, 500)
    ax1.set_ylim(-5, 730)
    r = qa["regression"]["stleu_vs_fixture"]
    ax1.set_title("(a) St-Leu Fig.80: generator rebuild (red dash)\nvs archived early R03 fixture (grey)", fontsize=11, loc="left")
    ax1.text(0.02, 0.02, f"IoU {r['iou']:.6f}\nHausdorff {r['hausdorff']:.3f} px\nface area {r['rebuild_face_area']:.1f} vs "
             f"{r['fixture_face_area']:.1f} px²\nplain vol. {r['rebuild_plain_volume_equiv']:.0f} vs {r['fixture_volume']:.0f}",
             transform=ax1.transAxes, fontsize=9, family="monospace", va="bottom",
             bbox=dict(fc="white", ec="#999", alpha=0.9))
    ax1.tick_params(labelsize=8)

    # (b) construction hypothesis
    ax2 = fig.add_axes([0.245, 0.04, 0.20, 0.33])
    rb, idl = swkt.loads(G["stleu_fig80_rebuild"]["stone"]), swkt.loads(G["stleu_fig80_ideal"]["stone"])
    ax2.add_patch(patch(rb.symmetric_difference(idl), fc="#e67e22", ec="none", alpha=0.9))
    lines(ax2, rb, color="black", lw=0.8)
    lines(ax2, idl, color="#2471a3", lw=0.8, ls=(0, (3, 2)))
    ax2.set_aspect("equal")
    ax2.set_xlim(150, 390)
    ax2.set_ylim(440, 650)
    hyp = qa["regression"]["stleu_ideal_vs_rebuild"]
    ph = hyp["per_element_hausdorff_px"]
    ax2.set_title("(b) Hypothesis test: symmetric arches + regular\nsixfold foil (blue dash) vs measured (black); "
                  "orange = difference", fontsize=11, loc="left")
    ax2.text(0.02, 0.02, "max boundary deviation, px\n" + "\n".join(f"{k:8s} {v:6.2f}" for k, v in ph.items()),
             transform=ax2.transAxes, fontsize=9, family="monospace", va="bottom",
             bbox=dict(fc="white", ec="#999", alpha=0.9))
    ax2.tick_params(labelsize=8)

    # (c) construction / members of the recursive window
    ax3 = fig.add_axes([0.47, 0.04, 0.24, 0.33])
    g4 = G["bar_4light_recursive"]
    col = {"frame": "#b9ae97", "sub_arch_band": "#d6c9a8", "oculus_ring": "#c8a96e", "foil_cusps": "#a3804a",
           "mullion": "#d6c9a8", "intersecting_arc": "#c8a96e"}
    for mb in g4["members"]:
        ax3.add_patch(patch(mb["wkt"], fc=col.get(mb["kind"], "#ccc"), ec="#5b4a2f", lw=0.3, alpha=0.95))
    for v in g4["voids"]:
        p = swkt.loads(v["wkt"])
        ax3.add_patch(patch(p, fc="#2c3e50" if v["role"] != "spandrel" else "#5d6d7e", ec="none", alpha=0.25))
        c = p.representative_point()
        ax3.text(c.x, c.y, v["id"].replace("W.", ""), fontsize=6.5, ha="center", va="center", color="#1b2631")
    for k, cc in g4["con"]["circles"].items():
        x, z = cc["centre"]
        ax3.plot([x], [z], "+", color="#c0392b", ms=6)
        ax3.add_patch(plt.Circle((x, z), cc["r_outer"], fill=False, ls=":", ec="#c0392b", lw=0.6))
    for k, ar in g4["con"]["arches"].items():
        for cc in (ar["CL"], ar["CR"]):
            ax3.plot([cc[0]], [cc[1]], ".", color="#1f618d", ms=3)
    ax3.set_aspect("equal")
    ax3.set_xlim(-2700, 2700)
    ax3.set_ylim(-300, 9300)
    rec4 = qa["models"]["bar_4light_recursive"]
    jt = {}
    for j in rec4["junctions"]:
        jt[j["type"]] = jt.get(j["type"], 0) + 1
    ax3.set_title(f"(c) bar_4light_recursive: {len(rec4['members'])} members, {len(rec4['junctions'])} junctions\n"
                  f"({jt.get('shared_edge', 0)} shared edge, {jt.get('overlap', 0)} overlap); + oculus centres, . arc centres",
                  fontsize=11, loc="left")
    ax3.tick_params(labelsize=8)

    # (d) QA table
    ax4 = fig.add_axes([0.73, 0.04, 0.265, 0.33])
    ax4.axis("off")
    rows = ["model                   geom   arch   tech   Blender"]
    for k, v in qa["models"].items():
        cs = v["checks"]
        f = lambda kind: f"{sum(c['ok'] for c in cs if c['kind'] == kind)}/{sum(c['kind'] == kind for c in cs)}"
        b = bq["models"][k]
        bok = "ok" if b["ok"] else "FAIL"
        rows.append(f"{k[:22]:22s}  {f('geometric'):6s} {f('architectural'):6s} {f('technical'):6s} {bok}")
    rt = qa["regression"]["tests"]
    rows.append(f"St-Leu fixture regression: {sum(c['ok'] for c in rt)}/{len(rt)}")
    rows += ["", "Blender: 0 nonmanifold edges, 0 degenerate faces,", "0 self-intersecting face pairs, bounds match"
             if bq["all_ok"] else "Blender: SEE blender_QA_U01.json", "",
             "Technical  : GLB export/reload, bit-identical rebuilds",
             "Geometric  : analytic tangency/apex residuals, watertight,",
             "             genus = openings, exact 2x, fixture rebuild",
             "Architect. : connected member graph, min web vs chamfer,",
             "             expected openings; profiles are trial chamfers",
             "Historical : St-Leu = existing fits in source px (uncalibrated);",
             "             mm windows are parametric, not surveys",
             "Structural : not assessed"]
    ax4.text(0.0, 1.0, "\n".join(rows), fontsize=9.6, family="monospace", va="top")
    ax4.set_title("(d) Automated QA (U01)", fontsize=11, loc="left")
    fig.savefig(out / "U01_comparison.png", dpi=100, facecolor="white")
    print("wrote", out / "U01_comparison.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["build", "compose"])
    ap.add_argument("--specs", default="specs_U01.json")
    ap.add_argument("--out", default="out")
    ap.add_argument("--fixture")
    a = ap.parse_args()
    run_build(a) if a.stage == "build" else run_compose(a)
