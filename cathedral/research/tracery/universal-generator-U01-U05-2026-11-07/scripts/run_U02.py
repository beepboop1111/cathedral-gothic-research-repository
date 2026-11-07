#!/usr/bin/env python3
"""run_U02.py -- build U02 (orders + mouldings) on top of unchanged U01 topology, run QA, compose PNG.

  python3 -I run_U02.py build   --specs specs_U01.json --sections sections_U02.json --u01 out --out out_U02
  python3 -I run_U02.py compose --out out_U02
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
from shapely.ops import unary_union  # noqa: E402

import tracery_section_U02 as U  # noqa: E402
import tracery_universal_U01 as T  # noqa: E402


def t_(kind, name, ok, detail=""):
    return dict(kind=kind, name=name, ok=bool(ok), detail=detail)


def run_build(a):
    specs = {s["id"]: s for s in json.loads(Path(a.specs).read_text())}
    secs = json.loads(Path(a.sections).read_text())
    q01 = json.loads((Path(a.u01) / "QA_U01.json").read_text())["models"]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report, geoms = {"version": U.VERSION, "models": {}}, {}
    for mid, sec in secs.items():
        spec = specs[mid]
        u = U.Sectioned(spec, sec)
        tests = list(u.checks)
        c01 = u.m.checks
        tests.append(t_("geometric", f"U01 topology/analytic checks still pass ({sum(c['ok'] for c in c01)}/{len(c01)})",
                        all(c["ok"] for c in c01)))
        ids = [v["id"] for v in u.m.voids]
        tests.append(t_("technical", "U01 opening IDs and stone area unchanged",
                        ids == [o["id"] for o in q01[mid]["openings"]]
                        and abs(u.m.stone.area - q01[mid]["stone_face_area"]) <= 1e-6 * u.m.stone.area))
        parts, stone_ok = {}, []
        for nm, mesh, _, _ in u.parts:
            qa = T.mesh_qa(mesh)
            parts[nm] = qa
            if nm == "glass":
                continue
            ok = qa["watertight"] and qa["winding_consistent"] and qa["volume"] > 0 and qa["nonmanifold_edges"] == 0 \
                and qa["degenerate_faces"] == 0 and qa["unreferenced_vertices"] == 0
            if nm.startswith("stone_o"):
                pm = u.piece_meta[nm]
                o = u.order_of(pm["order"])
                vmax, vmin = 2 * o["H"] * pm["area"], 2 * (o["H"] - float(o["prof"][:, 1].max())) * pm["area"]
                ok = ok and qa["bodies"] == 1 and qa["euler"] == 2 - 2 * pm["holes"] and pm["min_half"] > 0 \
                    and vmin * (1 - 1e-9) <= qa["volume"] <= vmax * (1 + 1e-9)
                stone_ok.append(ok)
                if not ok:
                    tests.append(t_("geometric", f"{nm}: closed piece FAILED", False, json.dumps({x: qa[x] for x in (
                        "watertight", "winding_consistent", "nonmanifold_edges", "degenerate_faces", "bodies", "euler")})))
            else:
                tests.append(t_("geometric", f"{nm}: watertight, consistent winding, 0 nonmanifold/degenerate, one body",
                                ok and qa["bodies"] == 1 and qa["euler"] == 0))
        tests.append(t_("geometric", f"all {len(stone_ok)} stone pieces: watertight, consistent winding, one body, "
                        "genus = holes, 0 nonmanifold/degenerate, height field above glazing plane, volume within "
                        "section bounds", all(stone_ok)))
        data = u.export_glb(out / f"{mid}.glb")
        sc = trimesh.load(io.BytesIO(data), file_type="glb", process=False, force="scene")
        ok_rt = all((g := sc.geometry.get(f"{mid}__{nm}")) is not None and len(g.vertices) == len(mesh.vertices)
                    and len(g.faces) == len(mesh.faces) and np.allclose(g.bounds, mesh.bounds, atol=1e-6 * u.m.size)
                    for nm, mesh, _, _ in u.parts)
        tests.append(t_("technical", "GLB export -> reload: counts and bounds unchanged", ok_rt))
        h = [T.mesh_hash(mesh) for nm, mesh, _, _ in u.parts if nm.startswith("stone")]
        u2 = U.Sectioned(copy.deepcopy(spec), copy.deepcopy(sec))
        tests.append(t_("technical", "rebuild is bit-identical",
                        h == [T.mesh_hash(mesh) for nm, mesh, _, _ in u2.parts if nm.startswith("stone")]))
        u4 = U.Sectioned(spec, sec, 2.0)
        ok2 = len(u.parts) == len(u4.parts) and all(abs(b_[1].volume - 8 * a_[1].volume) <= 1e-6 * 8 * a_[1].volume
                  and np.allclose(b_[1].bounds, 2 * a_[1].bounds, atol=1e-6 * u4.m.size)
                  for a_, b_ in zip(u.parts, u4.parts) if a_[0].startswith("stone"))
        tests.append(t_("geometric", "2x (spec + sections): IDs kept, each order volume x8 and bounds x2",
                        ok2 and [v["id"] for v in u4.m.voids] == ids))
        rec = dict(id=mid, title=spec.get("title", ""), units=spec.get("units"), note=sec.get("note", ""),
                   orders=[dict(depth=2 * o["H"], profile=o["raw"], face_width=float(o["prof"][-1, 0]),
                                max_drop=float(o["prof"][:, 1].max())) for o in u.orders],
                   pieces=u.piece_info, flat_face_fraction=u.flat, checks=tests,
                   parts={k: dict(v, bounds_blender=[[v["bounds"][0][0], -v["bounds"][1][2], v["bounds"][0][1]],
                                                     [v["bounds"][1][0], -v["bounds"][0][2], v["bounds"][1][1]]])
                          for k, v in parts.items()})
        report["models"][mid] = rec
        geoms[mid] = dict(regions={str(k): [p.wkt for p in ps] for k, ps in u.regions.items()},
                          voids=[v["poly"].wkt for v in u.m.voids],
                          profiles={str(i): o["prof"].tolist() for i, o in enumerate(u.orders)},
                          H=[o["H"] for o in u.orders])
        bad = [c for c in tests if not c["ok"]]
        print(f"{mid}: {len(tests) - len(bad)}/{len(tests)} pass | pieces {u.piece_info} | flat {u.flat}")
        for c in bad:
            print("   FAIL", c["kind"], c["name"], c["detail"])
    (out / "QA_U02.json").write_text(json.dumps(report, indent=1, default=float))
    (out / "QA_U01.json").write_text(json.dumps(report, indent=1, default=float))  # name read by the Blender checker
    (out / "geom_U02.json").write_text(json.dumps(geoms))


def run_compose(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath

    out = Path(a.out)
    qa = json.loads((out / "QA_U02.json").read_text())
    bq = json.loads((out / "blender_QA_U01.json").read_text())
    G = json.loads((out / "geom_U02.json").read_text())

    def patch(g, **kw):
        g = swkt.loads(g) if isinstance(g, str) else g
        verts, codes = [], []
        for p in T.polys(g):
            for r in [p.exterior, *p.interiors]:
                c = np.asarray(r.coords)
                verts += c.tolist()
                codes += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY]
        return PathPatch(MPath(verts, codes), **kw)

    fig = plt.figure(figsize=(24, 17), dpi=100, facecolor="white")
    fig.text(0.01, 0.988, "U02 depth + small details (EXPERIMENTAL): member orders step back, mouldings run from every "
             "opening edge and mitre at junctions - built on unchanged U01 topology", fontsize=16.5, weight="bold", va="top")
    ax0 = fig.add_axes([0.005, 0.585, 0.99, 0.385])
    img = plt.imread(out / "render_U02.png")
    ax0.imshow(img)
    ax0.axis("off")
    H, W = img.shape[:2]
    for lab in bq["labels"]:
        ax0.text(lab["u"] * W, 0.975 * H, lab["id"], ha="center", va="bottom", fontsize=11, weight="bold",
                 bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
    ax0.text(0.006 * W, 0.012 * H, f"Blender {bq['blender']}: GLBs re-imported, smooth-by-angle 32°, Cycles. Equal display "
             "height; St-Leu in uncalibrated source px, others parametric mm", fontsize=10, va="top",
             bbox=dict(fc="white", ec="none", alpha=0.85))
    ax1 = fig.add_axes([0.005, 0.215, 0.44, 0.355])
    ax1.imshow(plt.imread(out / "closeup_U02.png"))
    ax1.axis("off")
    ax1.set_title("(a) bar_4light_recursive head, raking light: stepped orders, hollow/roll mouldings, quirk groove, "
                  "mitred cusps", fontsize=10.5, loc="left")

    # (b) sections of the four orders (half-sections, glazing plane at 0)
    ax2 = fig.add_axes([0.48, 0.255, 0.22, 0.30])
    g4 = G["bar_4light_recursive"]
    for i, (k, prof) in enumerate(g4["profiles"].items()):
        P, Hk = np.asarray(prof), g4["H"][i]
        x = np.r_[0, P[:, 0], P[-1, 0] + 25, P[-1, 0] + 25]
        y = np.r_[0, Hk - P[:, 1], Hk, 0]
        ax2.fill(x, y, fc=U.DEPTH_PALETTE[i], ec="black", lw=0.8, alpha=0.55, label=f"order {k}: depth {2 * Hk:.0f}")
    ax2.axhline(0, color="#2c3e50", lw=1.2, ls="--")
    ax2.text(2, 4, "glazing plane", fontsize=8, color="#2c3e50")
    ax2.set_xlabel("distance from the opening arris (mm)", fontsize=9)
    ax2.set_ylabel("face height above glazing plane (mm)", fontsize=9)
    ax2.set_title("(b) bar_4light half-sections per order (trial)\nmirrored on the back face", fontsize=10.5, loc="left")
    ax2.legend(fontsize=8, loc="lower right")
    ax2.set_aspect("equal")
    ax2.tick_params(labelsize=8)

    # (c) order map in the accepted 2D depth-study palette
    ax3 = fig.add_axes([0.72, 0.215, 0.13, 0.355])
    for k, ps in g4["regions"].items():
        for p in ps:
            ax3.add_patch(patch(p, fc=U.DEPTH_PALETTE[int(k)], ec="black", lw=0.25))
    ax3.set_aspect("equal")
    ax3.set_xlim(-2700, 2700)
    ax3.set_ylim(-300, 9300)
    ax3.axis("off")
    ax3.set_title("(c) order map, 2D depth-study\npalette (now physical, trial)", fontsize=10.5, loc="left")
    ax3s = fig.add_axes([0.86, 0.215, 0.13, 0.355])
    gs = G["bar_2light_sexfoil"]
    for k, ps in gs["regions"].items():
        for p in ps:
            ax3s.add_patch(patch(p, fc=U.DEPTH_PALETTE[int(k)], ec="black", lw=0.25))
    ax3s.set_aspect("equal")
    ax3s.set_xlim(-1500, 1500)
    ax3s.set_ylim(-250, 6000)
    ax3s.axis("off")
    ax3s.set_title("bar_2light_sexfoil", fontsize=10.5, loc="left")

    # (d) QA
    ax4 = fig.add_axes([0.01, 0.005, 0.98, 0.20])
    ax4.axis("off")
    rows = [f"{'model':22s} {'geometric':>10s} {'architect.':>10s} {'technical':>10s}  Blender  orders  pieces/order"
            "                      flat face left after profile (fraction of order area)"]
    for k, v in qa["models"].items():
        cs = v["checks"]
        f = lambda kind: f"{sum(c['ok'] for c in cs if c['kind'] == kind)}/{sum(c['kind'] == kind for c in cs)}"
        b = "ok" if bq["models"][k]["ok"] else "FAIL"
        pcs = " ".join(f"o{o}:{p['pieces']}" for o, p in v["pieces"].items())
        ff = " ".join(f"o{o}:{x:.2f}" for o, x in v["flat_face_fraction"].items())
        rows.append(f"{k[:22]:22s} {f('geometric'):>10s} {f('architectural'):>10s} {f('technical'):>10s}  {b:7s}  "
                    f"{len(v['orders']):^6d}  {pcs:33s} {ff}")
    rows += ["",
             "Technical: GLB export/reload, bit-identical rebuilds, U01 opening IDs + stone area unchanged.   "
             "Geometric: order regions tile the U01 stone, height fields never cross the glazing plane, watertight,",
             "  bodies/Euler match pieces, 2x scaling (volume x8, bounds x2); Blender: 0 nonmanifold, 0 degenerate, 0 self-intersecting pairs, bounds match.   "
             "Architectural: depths step back by order, mouldings shallower than half-depth.",
             "Historical: St-Leu chamfer follows Moore 139a in KIND only (size trial, source px); bar-window orders and profiles "
             "are trial values, not measured sections.   Structural: not assessed."]
    ax4.text(0.0, 1.0, "\n".join(rows), fontsize=9.6, family="monospace", va="top")
    fig.savefig(out / "U02_depth_details.png", dpi=100, facecolor="white")
    print("wrote", out / "U02_depth_details.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["build", "compose"])
    ap.add_argument("--specs", default="specs_U01.json")
    ap.add_argument("--sections", default="sections_U02.json")
    ap.add_argument("--u01", default="out")
    ap.add_argument("--out", default="out_U02")
    a = ap.parse_args()
    run_build(a) if a.stage == "build" else run_compose(a)
